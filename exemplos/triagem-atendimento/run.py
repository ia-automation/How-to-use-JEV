"""Roda a triagem num conjunto rotulado, nas duas línguas do ticket, e gera `resultados.md` sozinho.

Uso:
  python run.py                  conjuntos de CONJUNTOS_PADRAO
  python run.py rascunho         só o encanamento (dados/rascunho.json — não é métrica)
  JEV_MODO=gravado python run.py reproduz tudo do cache, sem chave
Cada ticket vira uma requisição por variante (todas as perguntas juntas). O cache em `cache/`
faz a segunda rodada custar zero.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
import triagem as T  # noqa: E402
from jevcache import Jev  # noqa: E402

# O teste roda UMA vez, com perguntas, limiares e pesos congelados (hash no cabeçalho de resultados.md).
CONJUNTOS_PADRAO = ["ajuste", "teste"]

# variante → (campo do ticket, língua das perguntas). As duas primeiras usam as MESMAS perguntas (inglês):
# a diferença entre elas é só a língua do ticket.
VARIANTES = {
    "en": ("mensagem_en", "en"),
    "pt": ("mensagem_pt", "en"),
    "pt+perg_pt": ("mensagem_pt", "pt"),  # língua da pergunta: afinada só no ajuste, medida igual nos dois
}
LIMIARES_CONF = [0.0, 0.3, 0.5, 0.7, 0.9]
PERGUNTAS_MEDIDAS = ["setor", *P.NOULS, "frustracao"]


def rodar(casos: list[dict], variante: str) -> tuple[list[dict], dict, list[dict]]:
    campo, lingua = VARIANTES[variante]
    jev = Jev(AQUI / "cache")  # uma instância por variante: latência e tokens separados por língua
    respostas = jev.perguntar_varios([T.pedido(c[campo], lingua) for c in casos])
    return [T.decidir(r, lingua) for r in respostas], jev.resumo(), respostas


def previsto(s: dict, pergunta: str):
    """Resposta dura por pergunta (sem faixa de dúvida): é o que se compara entre línguas."""
    if pergunta == "setor":
        return s["setor"]
    if pergunta == "frustracao":
        return s["frustracao_nivel"]
    return s["nouls"][pergunta] >= 0.5


def sinal(s: dict, pergunta: str) -> float:
    """Número contínuo por pergunta, para medir o quanto pt e en discordam."""
    if pergunta == "frustracao":
        return s["frustracao_score"]
    if pergunta == "setor":
        return 0.0  # setor: desacordo = escolhas diferentes (tratado à parte)
    return s["nouls"][pergunta]


def acao_certa(s: dict, c: dict) -> bool:
    """Ticket que seguiu sozinho está certo se as decisões que MUDAM A AÇÃO batem: setor e os três sim/não.

    Gabarito nulo decidido sozinho conta como erro (DADOS.md: nulo = indecidível, deveria ir a humano).
    Frustração fica fora: não roteia, só pesa na prioridade, medida à parte.
    """
    if s["setor"] != c["setor"]:
        return False
    return all(s["flags"][f] is None or s["flags"][f] == c[f] for f in P.NOULS)


def nulo_como_duvida(s: dict, pergunta: str) -> bool:
    """Para gabarito nulo: o sistema sinalizou dúvida em vez de decidir sozinho? (cópia não conta)"""
    if pergunta == "setor":
        return s["setor_duvida"]
    return s["flags"][pergunta] is None


# Grade de políticas para a curva do roteamento: mesma resposta bruta, outros limiares, zero chamada nova.
GRADE_SETOR = [0.0, 0.5, 0.7, 0.9]
GRADE_FAIXA = [(0.5, 0.5), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9)]


def curva_roteamento(respostas: list[dict], casos: list[dict], lingua: str) -> list[dict]:
    """Cobertura automática × erro entre os automáticos para cada par (piso do setor, faixa dos sim/não).

    Troca as constantes de `perguntas` durante o laço porque `triagem.decidir` as lê na hora — é
    exatamente o que um humano faria editando o arquivo; restaura no fim.
    """
    antes = P.SETOR_CONF_MIN, P.FAIXA_NOUL
    linhas = []
    try:
        for piso in GRADE_SETOR:
            for faixa in GRADE_FAIXA:
                P.SETOR_CONF_MIN, P.FAIXA_NOUL = piso, {f: faixa for f in P.NOULS}
                ss = [T.decidir(r, lingua) for r in respostas]
                auto = [acao_certa(s, c) for s, c in zip(ss, casos) if s["destino"] != "humano"]
                linhas.append({"piso_setor": piso, "faixa_sim_nao": f"{faixa[0]}–{faixa[1]}",
                               "cobertura": len(auto) / len(casos),
                               "erro_automatico": (1 - sum(auto) / len(auto)) if auto else float("nan"),
                               "n_auto": len(auto)})
    finally:
        P.SETOR_CONF_MIN, P.FAIXA_NOUL = antes
    return linhas


def secao_conjunto(nome: str, dados: dict, variantes: list[str]) -> tuple[str, dict]:
    """Seção detalhada de um conjunto + resumo numérico para a comparação lado a lado."""
    casos = dados["casos"]
    resumo = {"n": len(casos), "acerto": {}, "desacordo": {}, "prior": {}, "rota": {}, "custo": {}}
    saidas, custos, brutas = {}, {}, {}
    for v in variantes:
        saidas[v], custos[v], brutas[v] = rodar(casos, v)

    out = [f"## Conjunto `{nome}` — {len(casos)} casos (arquivo versão {dados.get('versao')}, autor {dados.get('autor')})\n"]
    if nome == "rascunho":
        out.append("> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**\n")

    # --- acerto por pergunta e por língua
    linhas = []
    for q in PERGUNTAS_MEDIDAS:
        l = {"pergunta": q, "n": sum(c[q] is not None for c in casos)}
        for v in variantes:
            l[f"acerto_{v}"] = M.acerto([(previsto(s, q), c[q]) for s, c in zip(saidas[v], casos)])
        if "pt" in variantes and "en" in variantes:
            l["Δ pt−en"] = l["acerto_pt"] - l["acerto_en"]
            if q == "setor":
                l["desacordo pt×en"] = sum(a["setor"] != b["setor"] for a, b in zip(saidas["pt"], saidas["en"])) / len(casos)
            else:
                l["desacordo pt×en"] = sum(abs(sinal(a, q) - sinal(b, q)) for a, b in zip(saidas["pt"], saidas["en"])) / len(casos)
            resumo["desacordo"][q] = l["desacordo pt×en"]
        resumo["acerto"][q] = {v: l[f"acerto_{v}"] for v in variantes}
        linhas.append(l)
    out.append("### Acerto por pergunta e por língua\n")
    out.append("Resposta dura, sem faixa de dúvida: setor = opção vencedora; sim/não = noul ≥ 0,5; frustração = "
               "nível mais próximo do score. `en` e `pt` usam as MESMAS perguntas em inglês; `pt+perg_pt` troca "
               "também a pergunta. `desacordo pt×en`: setor = fração de escolhas diferentes; sim/não = média de "
               "|noul_pt − noul_en|; frustração = média de |score_pt − score_en| (escala 0–2). Referência de ruído "
               "(mesma requisição repetida, 30 pares, rascunho 2026-09-30): noul média 0,011 (p95 0,05); "
               "score média 0,008 — desacordo nessa ordem de grandeza não pode ser atribuído à língua (a média do ruído não identifica a causa de cada diferença).\n")
    out.append(M.tabela(linhas) + "\n")

    # --- setor: cobertura × erro e cópia para 2º setor
    out.append("### Setor — cobertura automática × erro por limiar de confiança\n")
    for v in variantes:
        itens = [(s["setor_conf"], s["setor"] == c["setor"]) for s, c in zip(saidas[v], casos) if c["setor"] is not None]
        com_copia = [c["setor"] in (s["setor"], *s["setor_copias"]) for s, c in zip(saidas[v], casos) if c["setor"] is not None]
        n_copia = sum(bool(s["setor_copias"]) for s in saidas[v])
        out.append(f"**{v}** — atual SETOR_CONF_MIN={P.SETOR_CONF_MIN}, SETOR_COPIA_SIM={P.SETOR_COPIA_SIM}; "
                   f"tickets com cópia: {n_copia}; gabarito no vencedor ou numa cópia: {sum(com_copia)}/{len(com_copia)}\n")
        out.append(M.tabela(M.cobertura_erro(itens, LIMIARES_CONF)) + "\n")

    # --- Nouls: faixa de dúvida e Brier
    out.append("### Sim/não — faixa de dúvida (limiares de `perguntas.py`) e Brier\n")
    linhas = []
    for f in P.NOULS:
        nao, sim = P.FAIXA_NOUL[f]
        for v in variantes:
            itens = [(s["nouls"][f], c[f]) for s, c in zip(saidas[v], casos)]
            linhas.append({"pergunta": f, "variante": v, "faixa": f"{nao}–{sim}", **M.faixa_noul(itens, nao, sim),
                           "brier": M.brier(itens)})
    out.append(M.tabela(linhas) + "\n")

    # --- frustração: cobertura × erro
    out.append("### Frustração — cobertura × erro por confiança do Score\n")
    out.append("Informativo: frustração não manda para humano (só alimenta a prioridade, pelo score contínuo).\n")
    for v in variantes:
        itens = [(s["frustracao_conf"], s["frustracao_nivel"] == c["frustracao"])
                 for s, c in zip(saidas[v], casos) if c["frustracao"] is not None]
        out.append(f"**{v}**\n")
        out.append(M.tabela(M.cobertura_erro(itens, LIMIARES_CONF)) + "\n")

    # --- prioridade composta: faixa prevista × faixa composta a partir do gabarito
    out.append("### Prioridade composta — faixa prevista × faixa do gabarito (mesma fórmula sobre os rótulos)\n")
    linhas = []
    for v in variantes:
        pares = []
        for s, c in zip(saidas[v], casos):
            if all(c[k] is not None for k in P.PESOS_PRIORIDADE):
                gab = {k: (c[k] / 2 if k == "frustracao" else float(c[k])) for k in P.PESOS_PRIORIDADE}
                pares.append((s["prioridade_faixa"], T.compor_prioridade(gab)[1]))
        linhas.append({"variante": v, "n": len(pares), "acerto_faixa": M.acerto(pares),
                       "confusao (gab→prev)": dict(sorted(M.matriz_confusao(pares).items()))})
        resumo["prior"][v] = M.acerto(pares)
    out.append(M.tabela(linhas) + "\n")

    # --- roteamento
    out.append("### Roteamento — o incerto vai para humano\n")
    linhas = []
    for v in variantes:
        pares = list(zip(saidas[v], casos))
        auto = [(s, c) for s, c in pares if s["destino"] != "humano"]
        nulos = [(s, q) for s, c in pares for q in ["setor", *P.NOULS] if c[q] is None]
        # humano sem necessidade: nada nulo no gabarito, cliente não pediu humano e a resposta dura acertava tudo
        sem_nec = [s for s, c in pares if s["destino"] == "humano" and not c["quer_humano"]
                   and all(c[q] is not None and previsto(s, q) == c[q] for q in ["setor", *P.NOULS])]
        linhas.append({
            "variante": v,
            "humano": sum(s["destino"] == "humano" for s, _ in pares),
            "automatico": len(auto),
            "erro_entre_automaticos": (1 - sum(acao_certa(s, c) for s, c in auto) / len(auto)) if auto else float("nan"),
            "humano_sem_necessidade": len(sem_nec),
            "nulo_tratado_como_duvida": f"{sum(nulo_como_duvida(s, q) for s, q in nulos)}/{len(nulos)}",
            "setor_nulo_com_copia": sum(bool(s["setor_copias"]) for s, c in pares if c["setor"] is None),
        })
        resumo["rota"][v] = linhas[-1]
    out.append("Erro entre automáticos = setor ou algum sim/não decidido errado; gabarito nulo decidido sozinho "
               "conta como erro. Frustração fica fora (não roteia). `nulo_tratado_como_duvida`: setor sem "
               "informação, abaixo do piso ou com cópia sem principal claro; sim/não na faixa do meio.\n")
    out.append(M.tabela(linhas) + "\n")
    out.append("**Curva do roteamento** — mesmas respostas, outros limiares (piso de confiança do setor × faixa "
               f"de dúvida dos sim/não, a mesma nos três; piso com cópia fixo em {P.SETOR_CONF_MIN_COM_COPIA}). "
               "Linha atual: piso "
               f"{P.SETOR_CONF_MIN}, faixas {sorted(set(P.FAIXA_NOUL.values()))}.\n")
    for v in variantes:
        out.append(f"**{v}**\n")
        out.append(M.tabela(curva_roteamento(brutas[v], casos, VARIANTES[v][1])) + "\n")

    # --- custo e latência
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    linhas = []
    for v in variantes:
        c = custos[v]
        linhas.append({"variante": v, "requisicoes": c["requisicoes"], "perguntas": c["perguntas"],
                       "p50_ms": c["latencia_p50_ms"], "p95_ms": c["latencia_p95_ms"],
                       "tokens_por_ticket": round(c["input_tokens"] / c["requisicoes"]),
                       "US$_total": f"{c['custo_us']:.6f}",  # string: a tabela arredonda float a 3 casas
                       "US$_por_1000_tickets": f"{1000 * c['custo_us'] / c['requisicoes']:.4f}",
                       "modelo": ", ".join(c["modelos"])})
        resumo["custo"][v] = linhas[-1]
    out.append(M.tabela(linhas) + "\n")

    # --- casos, para afinar (no teste é só leitura)
    out.append("### Caso a caso\n")
    linhas = []
    for i, c in enumerate(casos):
        for v in variantes:
            s = saidas[v][i]
            erros = [q for q in PERGUNTAS_MEDIDAS if c[q] is not None and previsto(s, q) != c[q]]
            linhas.append({
                "id": c["id"], "var": v,
                "setor": f"{s['setor']} ({s['setor_conf']:.2f})" + "".join(f" +{x}" for x in s["setor_copias"]),
                "reemb": round(s["nouls"]["pede_reembolso"], 2), "humano": round(s["nouls"]["quer_humano"], 2),
                "cancelar": round(s["nouls"]["ameaca_cancelar"], 2),
                "frustr": f"{s['frustracao_score']:.2f} ({s['frustracao_conf']:.2f})",
                "prior": f"{s['prioridade']:.2f} {s['prioridade_faixa']}", "destino": s["destino"],
                "erros": ", ".join(erros) or "—",
            })
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    """Conjuntos lado a lado: uma coluna (ou linha) por conjunto × variante."""
    colunas = [(c, v) for c, r in resumos.items() for v in r["rota"]]
    out = ["## Lado a lado\n", "### Acerto por pergunta (resposta dura) e desacordo pt × en\n"]
    linhas = []
    for q in PERGUNTAS_MEDIDAS:
        l = {"pergunta": q}
        for c, v in colunas:
            l[f"{c} {v}"] = resumos[c]["acerto"][q][v]
        for c, r in resumos.items():
            l[f"desacordo {c}"] = r["desacordo"].get(q, float("nan"))
        linhas.append(l)
    out.append(M.tabela(linhas) + "\n")
    out.append("### Roteamento, prioridade, latência e custo\n")
    linhas = []
    for c, v in colunas:
        r, k, n = resumos[c]["rota"][v], resumos[c]["custo"][v], resumos[c]["n"]
        linhas.append({"conjunto": c, "variante": v, "n": n, "humano": r["humano"],
                       "cobertura_auto": r["automatico"] / n, "erro_entre_automaticos": r["erro_entre_automaticos"],
                       "humano_sem_necessidade": r["humano_sem_necessidade"],
                       "nulo_tratado_como_duvida": r["nulo_tratado_como_duvida"],
                       "prioridade_acerto_faixa": resumos[c]["prior"][v],
                       "p50_ms": k["p50_ms"], "p95_ms": k["p95_ms"], "tokens_por_ticket": k["tokens_por_ticket"],
                       "US$_por_1000_tickets": k["US$_por_1000_tickets"], "modelo": k["modelo"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out)


def _hash(nome: str) -> str:
    return hashlib.sha256((AQUI / nome).read_bytes()).hexdigest()[:16]


def main() -> None:
    conjuntos = sys.argv[1:] or CONJUNTOS_PADRAO
    partes, resumos = [], {}
    for nome in conjuntos:
        arquivo = AQUI / "dados" / f"{nome}.json"
        if not arquivo.exists():
            print(f"pulando {nome}: {arquivo.name} não existe")
            continue
        texto, resumos[nome] = secao_conjunto(nome, json.loads(arquivo.read_text(encoding="utf-8")), list(VARIANTES))
        partes.append(texto)
    if not partes:
        sys.exit("nenhum conjunto encontrado")
    cabecalho = (f"# Resultados — triagem-atendimento\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, limiares "
                 f"e pesos: `perguntas.py`. Preço: US$ 0,042 por milhão de tokens de entrada.\n\n"
                 f"Versão congelada: `perguntas.py` sha256 {_hash('perguntas.py')}… · `triagem.py` sha256 "
                 f"{_hash('triagem.py')}…\n")
    (AQUI / "resultados.md").write_text(cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes),
                                        encoding="utf-8")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")


if __name__ == "__main__":
    main()
