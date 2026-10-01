"""Roda o roteador sobre conjuntos rotulados, mede e escreve resultados.md (nunca escrito à mão).

Uso:  python run.py [conjunto ...]      padrão: CONJUNTOS_PADRAO  ·  conjuntos: rascunho | ajuste | teste
      JEV_MODO=gravado  só do cache (sem chave)  ·  JEV_MODO=ao_vivo  refaz as chamadas

Os LLMs são SIMULADOS: nada é chamado; o custo deles é estimado com os preços e tokens abaixo.
O custo do Jev é o medido (tokens reais × tarifa do jevcache).
"""
from __future__ import annotations

import datetime
import json
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import metricas as M  # noqa: E402  (depois do sys.path: _comum é pasta irmã, não pacote)
import perguntas as P  # noqa: E402
from jevcache import MODELO, Jev  # noqa: E402
from roteador import rotear  # noqa: E402

# ---------------------------------------------------------------- preços de referência (US$ por 1M tokens)
# Tabela oficial de preços da OpenAI (contexto curto), recebida do dono em 2026-09-30
# antes de usar como número de negócio. Trocar de modelo = trocar estas linhas.
LLM_BARATO = {"nome": "gpt-6-luna", "entrada": 0.10, "saida": 0.50}
LLM_RACIOCINIO = {"nome": "gpt-6-astra", "entrada": 10.00, "saida": 50.00}

# ---------------------------------------------------------------- tokens por pedido (estimativa explícita)
TOKENS_POR_CARACTERE = 1 / 4       # aproximação grosseira para pt-BR; o pedido em si pesa pouco
BARATO_PROMPT, BARATO_SAIDA = 600, 150              # instruções + tom da loja; resposta curta
RACIOCINIO_PROMPT = 2500                            # instruções + políticas (troca, reembolso, frete)
RACIOCINIO_SAIDA = 400 + 1500                       # resposta + raciocínio (cobrado como saída)

CONJUNTOS_PADRAO = ["ajuste", "teste"]  # teste rodado UMA vez, com perguntas e limiares congelados
FAQ_DO_CONJUNTO = {"rascunho": "faq_rascunho.json"}  # os demais usam faq.json
DESTINOS = ["faq", "status_pedido", "llm_barato", "llm_raciocinio", "humano"]
LIMIARES_CURVA = [0.0, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def _itens(arquivo: Path) -> list[dict]:
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    return dados["casos"] if isinstance(dados, dict) else dados


def custo_llm(destino: str, texto: str) -> float:
    """Custo estimado (US$) de UM pedido no destino; código e humano não gastam LLM."""
    if destino == "llm_barato":
        m, prompt, saida = LLM_BARATO, BARATO_PROMPT, BARATO_SAIDA
    elif destino == "llm_raciocinio":
        m, prompt, saida = LLM_RACIOCINIO, RACIOCINIO_PROMPT, RACIOCINIO_SAIDA
    else:
        return 0.0
    return ((prompt + len(texto) * TOKENS_POR_CARACTERE) * m["entrada"] + saida * m["saida"]) / 1e6


def binaria(nome: str, pares: list[tuple[bool, bool]]) -> dict:
    """pares = [(previsto, gabarito)] → precisão/recall de um sinal contra o destino do gabarito."""
    vp = sum(p and g for p, g in pares)
    prev, pos = sum(p for p, _ in pares), sum(g for _, g in pares)
    return {"sinal": nome, "n": len(pares), "previstos": prev, "reais": pos, "acertos_pos": vp,
            "precisao": vp / prev if prev else float("nan"), "recall": vp / pos if pos else float("nan"),
            "acerto": sum(p == g for p, g in pares) / len(pares) if pares else float("nan")}


def us(v: float) -> str:
    return f"{v:.4f}" if v >= 0.01 else f"{v:.6f}"


def secao(nome: str) -> tuple[str, dict]:
    """Roda um conjunto. Devolve o detalhe (Markdown) e o resumo que vai para a tabela lado a lado."""
    casos = _itens(AQUI / "dados" / f"{nome}.json")
    faq = _itens(AQUI / "dados" / FAQ_DO_CONJUNTO.get(nome, "faq.json"))
    jev = Jev(AQUI / "cache")
    rotas, respostas = rotear(jev, [c["pedido"] for c in casos], faq)
    r = jev.resumo()
    gab = [c.get("destino") for c in casos]
    pred = [x.destino for x in rotas]
    par = list(zip(pred, gab))
    validos = [(p, g) for p, g in par if g is not None]
    n = len(validos)
    res = {"n": f"{len(casos)} ({n} com gabarito)",
           "acerto do destino": f"{M.acerto(par):.3f} ({sum(p == g for p, g in validos)}/{n})"}

    # Por destino: recall / precisão
    for d in DESTINOS:
        b = binaria(d, [(p == d, g == d) for p, g in validos])
        res[f"{d}: recall / precisão"] = f"{b['recall']:.2f} / {b['precisao']:.2f} ({b['reais']} reais)"
    res["_matriz"] = M.matriz_confusao(par)

    # Erros pelo custo
    caros = {
        "risco vazado (gabarito humano, foi a outro lugar)": sum(g == "humano" and p != "humano" for p, g in par),
        "… dos quais ao LLM barato (o pior)": sum(g == "humano" and p == "llm_barato" for p, g in par),
        "FAQ servida sem ser FAQ (resposta oficial errada)": sum(p == "faq" and g not in ("faq", None) for p, g in par),
        "desperdício (simples/código foi ao raciocínio)": sum(p == "llm_raciocinio" and g in ("faq", "status_pedido", "llm_barato") for p, g in par),
        "automação perdida (FAQ/status foi a LLM)": sum(g in ("faq", "status_pedido") and p.startswith("llm") for p, g in par),
        "humano sem precisar": sum(p == "humano" and g not in ("humano", None) for p, g in par),
    }
    if any(c.get("faq_id") for c in casos):
        caros["FAQ certa como destino, mas item errado"] = sum(
            1 for c, x in zip(casos, rotas) if x.destino == "faq" and c.get("faq_id") and str(c["faq_id"]) != x.faq_id)
    res.update({f"erro: {k}": v for k, v in caros.items()})

    # Custo (LLMs estimados; Jev medido) por 1000 pedidos
    textos = [c["pedido"] for c in casos]
    tudo_rac = sum(custo_llm("llm_raciocinio", t) for t in textos)
    roteado = sum(custo_llm(p, t) for p, t in zip(pred, textos)) + r["custo_us"]
    oraculo = sum(custo_llm(g or "llm_raciocinio", t) for g, t in zip(gab, textos))
    # Justo: humano não gasta LLM no roteado, mas gasta no "tudo no raciocínio" → mostrar também sem eles.
    base_sem_h = sum(custo_llm("llm_raciocinio", t) for p, t in zip(pred, textos) if p != "humano")
    k = 1000 / len(casos)
    res.update({
        "US$/1000 pedidos: tudo no LLM de raciocínio": us(tudo_rac * k),
        "US$/1000 pedidos: roteado com Jev (LLM + Jev)": us(roteado * k),
        "US$/1000 pedidos: … só a parte Jev (medida)": us(r["custo_us"] * k),
        "US$/1000 pedidos: roteamento perfeito (gabarito)": us(oraculo * k),
        "economia contra tudo no raciocínio": f"{1 - roteado / tudo_rac:.1%}" if tudo_rac else "—",
        "economia só nos que não foram a humano": f"{1 - roteado / base_sem_h:.1%}" if base_sem_h else "—",
        "pedidos a humano (previsto / gabarito)": f"{pred.count('humano')} / {gab.count('humano')}",
        "Jev: requisições (do cache)": f"{r['requisicoes']} ({r['do_cache']})",
        "Jev: perguntas por pedido": r["perguntas"] // max(1, r["requisicoes"]),
        "Jev: latência p50 / p95 (ms, chamada real)": f"{r['latencia_p50_ms']} / {r['latencia_p95_ms']}",
        "Jev: tokens de entrada (por pedido)": f"{r['input_tokens']} ({r['input_tokens'] // max(1, r['requisicoes'])})",
        "Jev: custo medido (US$)": us(r["custo_us"]),
        "Jev: modelo que respondeu": ", ".join(r["modelos"]),
    })

    out = [f"## Detalhe — `{nome}` ({len(casos)} pedidos, FAQ com {len(faq)} itens)\n"]
    if nome == "rascunho":
        out.append("> RASCUNHO do construtor para testar o encanamento — NÃO é métrica do exemplo.\n")

    # Por pergunta (sinal do Jev contra o destino do gabarito, no limiar em vigor)
    a = [x["answers"] for x in respostas]
    idx = [i for i, g in enumerate(gab) if g is not None]
    sinais = [binaria(f"{k} ≥ {P.LIM_RISCO}", [(a[i][k]["noul"] >= P.LIM_RISCO, gab[i] == "humano") for i in idx])
              for k in P.RISCO]
    sinais.append(binaria(f"irritacao P(nível≥{P.NIVEL_IRRITADO}) ≥ {P.LIM_IRRITACAO}", [
        (sum(p for nv, p in a[i]["irritacao"]["probabilities"].items() if int(nv) >= P.NIVEL_IRRITADO)
         >= P.LIM_IRRITACAO, gab[i] == "humano") for i in idx]))
    sinais.append(binaria(f"status_pedido ≥ {P.LIM_STATUS}",
                          [(a[i]["status_pedido"]["noul"] >= P.LIM_STATUS, gab[i] == "status_pedido") for i in idx]))
    sinais.append(binaria("faq ≠ none (Choice)", [(a[i]["faq"]["choice"] != P.NENHUMA, gab[i] == "faq") for i in idx]))
    llm = [i for i in idx if gab[i] != "humano"]  # raciocínio vem logo depois do risco na precedência
    for k in P.RACIOCINIO:
        sinais.append(binaria(f"{k} ≥ {P.LIM_RACIOCINIO} (gabarito ≠ humano)",
                              [(a[i][k]["noul"] >= P.LIM_RACIOCINIO, gab[i] == "llm_raciocinio") for i in llm]))
    out.append("### Por pergunta (cada sinal sozinho contra o gabarito)\n\n"
               "Cada Noul de risco é UM motivo: recall baixo sozinho é esperado; a composição (max) é a linha "
               "`humano` da tabela por destino. `status_pedido` aqui é o Noul cru, sem a regra do número.\n")
    out.append(M.tabela(sinais, ["sinal", "n", "previstos", "reais", "acertos_pos", "precisao", "recall", "acerto"]) + "\n")

    # Cobertura × erro das rotas baratas (faq, status, llm_barato) pela confiança da rota
    baratas = [(x.confianca, x.destino_bruto == g) for x, g in zip(rotas, gab)
               if g is not None and x.destino_bruto in ("faq", "status_pedido", "llm_barato")]
    out.append(f"### Cobertura × erro das rotas baratas por piso de confiança ({len(baratas)} pedidos)\n\n"
               f"Abaixo do piso, a rota cai para o LLM de raciocínio. Piso em vigor: {P.PISO_ROTA}.\n")
    out.append(M.tabela(M.cobertura_erro(baratas, LIMIARES_CURVA), ["limiar", "cobertura", "erro_automatico", "n_auto"]) + "\n")

    # Distribuição e erros um a um
    out.append(f"### Rotas previstas\n\n{dict(Counter(pred))}\n")
    erros = [{"id": c["id"], "gabarito": c.get("destino"), "previsto": x.destino, "motivo": x.motivo,
              "conf": x.confianca, "mais_fraco": x.mais_fraco, "pedido": c["pedido"][:90].replace("|", "/").replace("\n", " ")}
             for c, x in zip(casos, rotas) if c.get("destino") is not None and x.destino != c["destino"]]
    out.append("### Erros um a um\n\n" + M.tabela(erros) + "\n")
    return "\n".join(out), res


def lado_a_lado(conjuntos: list[str], resumos: list[dict]) -> str:
    """Tabela métrica × conjunto e matriz de confusão com as células 'ajuste / teste'."""
    cab = "| métrica | " + " | ".join(f"`{c}`" for c in conjuntos) + " |\n|" + "---|" * (len(conjuntos) + 1)
    chaves = [k for k in resumos[0] if not k.startswith("_")]
    linhas = "\n".join(f"| {k} | " + " | ".join(str(r.get(k, "—")) for r in resumos) + " |" for k in chaves)
    mc_cab = "| gabarito \\ previsto | " + " | ".join(DESTINOS) + " |\n|" + "---|" * (len(DESTINOS) + 1)
    mc = "\n".join(f"| {g} | " + " | ".join(" / ".join(str(r["_matriz"].get((g, p), 0)) for r in resumos)
                                            for p in DESTINOS) + " |" for g in DESTINOS)
    return (f"## Lado a lado\n\n{cab}\n{linhas}\n\n### Matriz de confusão (células: {' / '.join(conjuntos)})\n\n"
            f"{mc_cab}\n{mc}\n")


def main() -> None:
    conjuntos = sys.argv[1:] or CONJUNTOS_PADRAO
    faltando = [c for c in conjuntos if not (AQUI / "dados" / f"{c}.json").exists()]
    if faltando:
        sys.exit(f"conjunto sem arquivo em dados/: {', '.join(faltando)}")
    detalhes, resumos = [], []
    for c in conjuntos:
        texto, res = secao(c)
        detalhes.append(texto)
        resumos.append(res)
    cab = (f"# Resultados — roteador Jev × LLM × código\n\nGerado por `run.py` em {datetime.date.today()} · "
           f"modelo fixado `{MODELO}` · conjuntos: {', '.join(conjuntos)}\n\n"
           f"Limiares em vigor (perguntas.py): risco {P.LIM_RISCO} · irritação {P.LIM_IRRITACAO} (nível ≥ "
           f"{P.NIVEL_IRRITADO}) · status {P.LIM_STATUS} · FAQ conf {P.LIM_FAQ_CONF} + cobre {P.LIM_FAQ_COBRE} · "
           f"raciocínio {P.LIM_RACIOCINIO} · piso {P.PISO_ROTA}\n\n"
           f"Custo: Jev MEDIDO (tokens reais × US$ 0,042/M); LLMs SIMULADOS — barato = `{LLM_BARATO['nome']}` "
           f"US$ {LLM_BARATO['entrada']}/{LLM_BARATO['saida']}, raciocínio = `{LLM_RACIOCINIO['nome']}` "
           f"US$ {LLM_RACIOCINIO['entrada']}/{LLM_RACIOCINIO['saida']} por 1M entrada/saída (tabela OpenAI "
           f"de 2026-09-30); tokens por pedido: barato {BARATO_PROMPT}+texto → {BARATO_SAIDA}, raciocínio "
           f"{RACIOCINIO_PROMPT}+texto → {RACIOCINIO_SAIDA}, texto = caracteres × {TOKENS_POR_CARACTERE}. "
           f"Humano não entra no custo de LLM; é contado à parte.\n")
    (AQUI / "resultados.md").write_text(cab + "\n" + lado_a_lado(conjuntos, resumos) + "\n" + "\n".join(detalhes),
                                        encoding="utf-8")
    print(f"resultados.md escrito ({', '.join(conjuntos)})")


if __name__ == "__main__":
    main()
