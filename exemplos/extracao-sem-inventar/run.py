"""Roda a extração num conjunto rotulado, mede e gera `resultados.md` sozinho.

Uso:
  python run.py                  conjuntos de CONJUNTOS_PADRAO que existirem
  python run.py rascunho         só o encanamento (dados/rascunho.json — não é métrica)
  JEV_MODO=gravado python run.py reproduz tudo do cache, sem chave
Uma requisição por mensagem com TODAS as perguntas; mensagem sem candidato nem pista de data não chama.

O que se mede, por campo:
  cobertura_cand   o valor do gabarito estava entre os candidatos? (data: havia pista de data?) — o Jev não
                   escolhe o que a regex não achou; esta coluna separa falha do código de falha da escolha.
  acerto_escolha   entre os cobertos, o valor final bate?
  exatidao         todos os casos (null certo conta como acerto)
  preencheu_null   devolveu valor onde o gabarito é null · omitiu: null onde o gabarito tem valor
  auto / erro_auto fração decidida sem revisão e erro entre essas
  inventou         valor devolvido que NÃO se rastreia a um trecho da mensagem — tem de ser 0
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import candidatos as C  # noqa: E402
import extrator as X  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import Jev  # noqa: E402

# O helper importa o SDK dentro do trecho cronometrado da 1ª chamada; importar antes tira ~300 ms dela.
try:
    import typesafe_sdk  # noqa: E402,F401
except ImportError:  # modo gravado sem o SDK continua funcionando
    pass

# Fase 2: ["ajuste", "teste"] — o teste roda UMA vez, no fim, com perguntas e limiares congelados.
CONJUNTOS_PADRAO = ["ajuste", "teste"]
GABARITO = {"email": "email", "telefone": "telefone", "cpf": "cpf", "valor": "valor_reais", "data_visita": "data_visita"}
LIMIARES_CONF = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9]

# Congelamento: hash dos arquivos que decidem, registrado ANTES de abrir o teste. O relatório compara com o
# hash atual — se mudou depois do registro, o número do teste não vale.
CONGELADOS = ["perguntas.py", "extrator.py", "candidatos.py"]
CONGELAMENTO = {"em": "2026-09-30 19:40:48", "sha256": {
    "perguntas.py": "4f8529765f0d2164c0b968d6043a05e90e5d5358289fdf9a767f91404c6ae064",
    "extrator.py": "3a7f76b7b63cdabc39171d9deda1ff49bd46d5092279cfe28d1d67de2dffff91",
    "candidatos.py": "3e1234fc4a84cf0adc14cdd187e67ad3ae1ecb1d660be99b5a769d3b273f218b",
}}


def hashes() -> dict:
    return {f: hashlib.sha256((AQUI / f).read_bytes()).hexdigest() for f in CONGELADOS}


def igual(campo: str, previsto, gabarito) -> bool:
    if previsto is None or gabarito is None:
        return previsto is None and gabarito is None
    if campo == "valor":
        return Decimal(str(previsto)) == Decimal(str(gabarito))
    if campo == "email":
        return previsto.lower() == gabarito.lower()
    return previsto == gabarito


def coberto(campo: str, gabarito, ctx: dict) -> bool:
    """O valor certo era alcançável pelo desenho? (candidato presente; valor cru com alguma escala; pista de data)."""
    if campo == "data_visita":
        return ctx["data_perguntada"]
    if campo == "valor":
        return any(igual("valor", c["base"] * f, gabarito) for c in ctx["valor"]
                   for f in (P.ESCALA_FATOR.values() if c["nu"] else [1]))
    return any(c["valor"] is not None and igual(campo, c["valor"], gabarito) for c in ctx[campo])


_DIAS_PT = ["segunda", "ter[çc]a", "quarta", "quinta", "sexta", "s[áa]bado", "domingo"]


def rastreavel(campo: str, valor, texto: str) -> bool:
    """Prova independente de 'não inventou': o valor devolvido se reconstrói a partir do texto."""
    if valor is None:
        return True
    t = texto.lower()
    if campo == "email":
        local, dominio = valor.split("@")
        return local in t and all(rotulo in t for rotulo in dominio.split("."))
    if campo in ("telefone", "cpf"):
        juntos = re.sub(r"(?<=\d)[\s.\-()/]+(?=\d)", "", texto)  # tira separadores ENTRE dígitos
        alvo = re.sub(r"\D", "", valor)
        if campo == "cpf":
            return alvo in juntos
        nacional = alvo[2:]
        return nacional in juntos or (nacional[2:] in juntos and re.search(rf"\b{nacional[:2]}\b", texto) is not None)
    if campo == "valor":
        return any(Decimal(valor) == c["base"] * f for c in C.valores(texto)
                   for f in (P.ESCALA_FATOR.values() if c["nu"] else [1]))
    d = datetime.date.fromisoformat(valor)
    return bool(re.search(rf"(?<!\d)0?{d.day}(?!\d)", t) or re.search(r"hoje|amanh", t)
                or re.search(_DIAS_PT[d.weekday()], t))


def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    jev = Jev(AQUI / "cache")
    montados = [X.montar(c["mensagem"]) for c in casos]
    com_pergunta = [i for i, (_, q, _) in enumerate(montados) if q]
    respostas = dict(zip(com_pergunta, jev.perguntar_varios([montados[i][:2] for i in com_pergunta])))
    saidas = []
    for i, c in enumerate(casos):
        state, q, ctx = montados[i]
        r = respostas.get(i, {"answers": {}})
        saidas.append({"ctx": ctx, "n_perguntas": len(q), "resposta": r,
                       "campos": X.extrair(r, ctx, c["data_referencia"])})
    return saidas, jev.resumo()


def secao(nome: str, dados: dict) -> str:
    casos = dados["casos"]
    saidas, custo = rodar(casos)
    out = [f"## Conjunto `{nome}` — {len(casos)} mensagens (arquivo versão {dados.get('versao')}, "
           f"autor {dados.get('autor')})\n"]
    if nome == "rascunho":
        out.append("> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**\n")

    linhas, inventados = [], []
    for campo in X.CAMPOS:
        g = GABARITO[campo]
        pares = [(s["campos"][campo], c[g], s["ctx"], c) for s, c in zip(saidas, casos)]
        com_valor = [(p, gab, ctx) for p, gab, ctx, _ in pares if gab is not None]
        cob = [(p, gab) for p, gab, ctx in com_valor if coberto(campo, gab, ctx)]
        auto = [(p, gab) for p, gab, _, _ in pares if not p["revisar"]]
        inv = [c["id"] for p, _, _, c in pares if not rastreavel(campo, p["valor"], c["mensagem"])]
        inventados += [f"{i}:{campo}" for i in inv]
        linhas.append({
            "campo": campo, "n": len(pares), "n_com_valor": len(com_valor),
            "cobertura_cand": f"{len(cob)}/{len(com_valor)}",
            "acerto_escolha": M.acerto([(igual(campo, p["valor"], gab), True) for p, gab in cob]),
            "exatidao": M.acerto([(igual(campo, p["valor"], gab), True) for p, gab, _, _ in pares]),
            "preencheu_null": sum(p["valor"] is not None and gab is None for p, gab, _, _ in pares),
            "omitiu": sum(p["valor"] is None and gab is not None for p, gab, _, _ in pares),
            "auto": f"{len(auto)}/{len(pares)}",
            "erro_auto": (1 - sum(igual(campo, p["valor"], gab) for p, gab in auto) / len(auto)) if auto else float("nan"),
            "inventou": len(inv),
        })
    out.append("### Exatidão por campo\n")
    out.append("`cobertura_cand` = gabarito entre os candidatos da regex (data: havia pista de data); "
               "`acerto_escolha` = acerto só entre os cobertos (mede o Jev + normalização); `exatidao` = todos "
               "os casos, null certo conta; `auto` = decididos sem revisão; `inventou` = valor que não se "
               "reconstrói do texto (tem de ser 0).\n")
    out.append(M.tabela(linhas) + "\n")
    resumo_campos = linhas
    out.append(f"**Inventou (total): {len(inventados)}** {inventados if inventados else ''}\n")

    out.append("### Cobertura automática × erro por limiar de confiança\n")
    out.append("Só casos em que houve pergunta (há confiança). Limiar atual por campo em `perguntas.CONF_MIN`.\n")
    for campo in X.CAMPOS:
        g = GABARITO[campo]
        itens = [(s["campos"][campo]["conf"], igual(campo, s["campos"][campo]["valor"], c[g]))
                 for s, c in zip(saidas, casos) if s["campos"][campo]["conf"] is not None]
        out.append(f"**{campo}** (CONF_MIN={P.CONF_MIN[campo]}, n={len(itens)})\n")
        out.append(M.tabela(M.cobertura_erro(itens, LIMIARES_CONF)) + "\n")

    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    chamadas = sum(bool(s["n_perguntas"]) for s in saidas)
    if custo:
        out.append(M.tabela([{
            "mensagens": len(casos), "requisicoes": custo["requisicoes"], "sem_chamada": len(casos) - chamadas,
            "perguntas_por_req": round(custo["perguntas"] / custo["requisicoes"], 1),
            "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
            "tokens_por_req": round(custo["input_tokens"] / custo["requisicoes"]),
            "US$_total": f"{custo['custo_us']:.6f}",
            "US$_por_1000_msgs": f"{1000 * custo['custo_us'] / len(casos):.4f}",
            "modelo": ", ".join(custo["modelos"])}]) + "\n")

    out.append("### Caso a caso (só campos errados ou em revisão)\n")
    linhas = []
    for s, c in zip(saidas, casos):
        for campo in X.CAMPOS:
            p, gab = s["campos"][campo], c[GABARITO[campo]]
            if igual(campo, p["valor"], gab) and not p["revisar"]:
                continue
            extra = X.partes_data(s["resposta"]) if campo == "data_visita" else p["escolha"]
            linhas.append({"id": c["id"], "campo": campo, "gabarito": gab, "previsto": p["valor"],
                           "ok": igual(campo, p["valor"], gab), "revisar": p["revisar"], "motivo": p["motivo"],
                           "conf": p["conf"] if p["conf"] is not None else "", "escolha/partes": extra,
                           "candidatos": len(s["ctx"].get(campo, [])) if campo != "data_visita" else "",
                           "nota": c.get("nota") or ""})
    out.append(M.tabela(linhas) + "\n" if linhas else "_(nenhum)_\n")
    return "\n".join(out), resumo_campos, custo, len(casos)


def secao_congelamento() -> str:
    atual = hashes()
    linhas = [{"arquivo": f, "sha256 registrado": (CONGELAMENTO["sha256"].get(f) or "—")[:16],
               "sha256 atual": atual[f][:16], "igual": CONGELAMENTO["sha256"].get(f) == atual[f]} for f in CONGELADOS]
    ok = all(l["igual"] for l in linhas)
    cab = (f"## Congelamento\n\nRegistrado em {CONGELAMENTO['em']}, depois de afinar no ajuste e ANTES de abrir "
           f"`teste.json`. " + ("**Arquivos atuais iguais ao registro: o teste vale.**" if ok
                                else "**ATENÇÃO: arquivo mudou depois do registro — o teste não vale.**"))
    return cab + "\n\n" + M.tabela(linhas) + "\n"


def resumo_lado_a_lado(res: dict) -> str:
    """Uma linha por campo, colunas por conjunto — o que se compara entre ajuste e teste."""
    nomes = list(res)
    linhas = []
    for i, campo in enumerate(X.CAMPOS):
        l = {"campo": campo}
        for n in nomes:
            r = res[n][0][i]
            l[f"{n}: exatidão"] = r["exatidao"]
            l[f"{n}: cobertura_cand"] = r["cobertura_cand"]
            l[f"{n}: acerto_escolha"] = r["acerto_escolha"]
            l[f"{n}: auto"] = r["auto"]
            l[f"{n}: erro_auto"] = r["erro_auto"]
            l[f"{n}: inventou"] = r["inventou"]
        linhas.append(l)
    custo = []
    for n in nomes:
        c, n_msgs = res[n][1] or {}, res[n][2]
        custo.append({"conjunto": n, "n_msgs": n_msgs, "requisicoes": c.get("requisicoes", 0),
                      "perguntas_por_req": round(c["perguntas"] / c["requisicoes"], 1) if c else 0,
                      "p50_ms": c.get("latencia_p50_ms"), "p95_ms": c.get("latencia_p95_ms"),
                      "tokens_entrada": c.get("input_tokens"), "US$_total": f"{c.get('custo_us', 0):.6f}",
                      "US$_por_1000_msgs": f"{1000 * c.get('custo_us', 0) / n_msgs:.4f}",
                      "modelo": ", ".join(c.get("modelos", []))})
    return (f"## Resumo — {' × '.join(nomes)}\n\n" + M.tabela(linhas) + "\n\n" + M.tabela(custo) + "\n")


def main(nomes: list[str]) -> None:
    partes = ["# Resultados — extração sem inventar\n",
              f"Gerado por `run.py` em {datetime.date.today().isoformat()}. Modelo pedido: `jev-1.13.0` "
              f"(o respondido aparece na tabela de custo). Preço: US$ 0,042 por milhão de tokens de entrada.\n",
              secao_congelamento()]
    secoes, res = [], {}
    for nome in nomes:
        arq = AQUI / "dados" / f"{nome}.json"
        if not arq.exists():
            secoes.append(f"## Conjunto `{nome}` — arquivo ausente, não rodou\n")
            continue
        md, campos, custo, n = secao(nome, json.loads(arq.read_text(encoding="utf-8")))
        secoes.append(md)
        res[nome] = (campos, custo, n)
    if res:
        partes.append(resumo_lado_a_lado(res))
    (AQUI / "resultados.md").write_text("\n".join(partes + secoes), encoding="utf-8")
    print((AQUI / "resultados.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main(sys.argv[1:] or CONJUNTOS_PADRAO)
