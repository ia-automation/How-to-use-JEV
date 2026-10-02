"""Roda o SQL semântico num conjunto de condições rotuladas e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 condições fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, sql.py, run.py,
                             dados/linhas.json, dados/condicoes_teste.json e o critério; hash de _comum/ só como registro);
                             o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo e dentro do orçamento.
                             A PRIMEIRA execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por (condição, linha que passou no filtro de campos); linha que falha o filtro não custa chamada.
Falha operacional (chamada, cache faltando, resposta fora do contrato) NÃO aborta o lote: aquela linha sai `indecidivel`
por `sql.avaliar_seguro` e é contada à parte — conjunto com falha não é medição do Jev.
O cache em `cache/` faz rodar de novo custar zero. Bateria do código (sem chave nem rede): `testa_falhas.py`.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
import sql as S  # noqa: E402
from jevcache import Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
ARQUIVOS = {"ajuste": "condicoes_ajuste.json", "teste": "condicoes_teste.json", "rascunho": "rascunho.json"}
# Manifesto com hash do código executado (inclusive este arquivo), da tabela, das condições de teste e do critério.
CONGELADOS = ["perguntas.py", "sql.py", "run.py", "dados/linhas.json", "dados/condicoes_teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
# Variantes calculadas das MESMAS respostas (zero chamada nova); a oficial é `perguntas.VARIANTE`.
VARIANTES = {"inteira": {"composta": "inteira", "pista": False}, "inteira+pista": {"composta": "inteira", "pista": True},
             "cláusulas": {"composta": "clausulas", "pista": False}, "cláusulas+pista": {"composta": "clausulas", "pista": True}}
GRADE_FAIXA = [(0.5, 0.5), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9)]
COLUNAS_TOTAL = ["variante", "decidíveis", "decididas", "P", "R", "F1", "F1 com V a humano = perdidas", "humano (decidíveis)",
                 "V a humano", "F a humano", "PERDIDAS (V → falso)", "FP EM NEGAÇÃO", "indecidíveis → humano", "falhas"]


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador ("difícil: <família> — detalhe"; senão "fácil")."""
    m = re.match(r"difícil:\s*(negação|composta|inferência fraca)", c.get("nota") or "")
    return m.group(1) if m else "fácil"


def gabarito(c: dict) -> dict:
    """{id da linha: verdadeiro | indecidivel}; linha fora das duas listas vale falso (LEIA-ME)."""
    g = {i: "verdadeiro" for i in c["linhas_verdadeiras"]}
    g.update({i: "indecidivel" for i in c["linhas_indecidiveis"]})
    return g


def requisicoes_previstas(casos: list[dict], linhas: list[dict]) -> int:
    """Quantas linhas passariam no filtro de campos e iriam ao Jev (uma requisição cada), sem chamar nada."""
    n = 0
    for c in casos:
        sep = S.separar_seguro(c["condicao"])  # condição inválida: nenhuma chamada (toda linha sai `indecidivel`)
        if sep["semantica"]:
            for l in linhas:
                try:
                    n += S.passa_filtro(l["campos"], sep["filtros"])
                except Exception:  # noqa: BLE001 — linha com campo inválido não vai ao Jev (achado 4)
                    pass
    return n


def rodar(casos: list[dict], linhas: list[dict]) -> tuple[dict, dict]:
    """{id da condição: [saída por linha]} pelo mesmo invólucro que o consumidor usa (`avaliar_seguro`): falha
    operacional vira `indecidivel` SÓ naquela linha, sem abortar o lote, contada à parte."""
    jev = Jev(AQUI / "cache")
    seps = {c["id"]: S.separar_seguro(c["condicao"]) for c in casos}
    pares = [(c["id"], l) for c in casos for l in linhas]
    with ThreadPoolExecutor(8) as ex:  # mesmo paralelismo de `Jev.perguntar_varios`
        lista = list(ex.map(lambda p: S.avaliar_seguro(jev, seps[p[0]], p[1]), pares))
    saidas = {c["id"]: [] for c in casos}
    for (cid, _), s in zip(pares, lista):
        saidas[cid].append(s)
    custo = jev.resumo() or {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
                             "input_tokens": 0, "custo_us": 0.0, "modelos": []}
    custo["linhas_avaliadas"] = len(pares)
    custo["sem_chamada"] = sum(s["por"] == "filtro" for s in lista)
    custo["textos_longos"] = sum(bool(s.get("longo")) for s in lista)
    custo["falhas_operacionais"] = sum(bool(s.get("falha")) for s in lista)
    return saidas, custo


def redecidir(s: dict, conector: str | None, variante: dict) -> str:
    """Re-decide com outra variante/faixa a partir dos números guardados (sem cache nem API); saída sem números fica."""
    if s["por"] != "jev":
        return s["saida"]
    return S.decidir(s["valores"], conector, variante)[0]


def metricas(itens: list[tuple[str, str, str]]) -> dict:
    """itens = [(saída, gabarito, família da condição)]. Micro sobre as linhas DECIDÍVEIS (gabarito ≠ indecidível);
    linha decidível mandada a humano fica fora de P/R/F1 e é contada à parte (`humano`, separada em V e F a humano);
    `F1_v_humano_perdidas` é o F1 contando as VERDADEIRAS mandadas a humano como perdidas (as falsas a humano não entram:
    renomeado na revisão do Codex, 2026-10-02, achado 5).
    Erros caros: PERDIDA = verdadeira do gabarito que saiu `falso`; FP EM NEGAÇÃO = falsa marcada `verdadeiro` em
    condição da família negação (as linhas em que a palavra-chave aparece negada)."""
    decid = [(s, g, f) for s, g, f in itens if g != "indecidivel"]
    tp = sum(s == "verdadeiro" and g == "verdadeiro" for s, g, _ in decid)
    fp = sum(s == "verdadeiro" and g == "falso" for s, g, _ in decid)
    fn = sum(s == "falso" and g == "verdadeiro" for s, g, _ in decid)
    humano = sum(s == "indecidivel" for s, _, _ in decid)
    v_humano = sum(s == "indecidivel" and g == "verdadeiro" for s, g, _ in decid)
    verdadeiras = sum(g == "verdadeiro" for _, g, _ in decid)
    ind = [(s, g, f) for s, g, f in itens if g == "indecidivel"]
    div = lambda a, b: a / b if b else float("nan")  # noqa: E731
    zero = lambda a, b: a / b if b else 0.0  # noqa: E731 — sem positivo previsto (LIKE que nada acha): P = 0, não indefinido
    p, r = zero(tp, tp + fp), zero(tp, tp + fn)
    r_estrito = zero(tp, tp + fn + v_humano)
    return {"decidiveis": len(decid), "decididas": len(decid) - humano, "tp": tp, "fp": fp, "fn": fn, "verdadeiras": verdadeiras,
            "P": p, "R": r, "F1": zero(2 * p * r, p + r), "F1_v_humano_perdidas": zero(2 * p * r_estrito, p + r_estrito),
            "humano": humano, "humano_frac": div(humano, len(decid)), "v_humano": v_humano, "f_humano": humano - v_humano,
            "perdidas": fn, "perdidas_frac": div(fn, verdadeiras),
            "fp_negacao": sum(s == "verdadeiro" and g == "falso" and f == "negação" for s, g, f in decid),
            "ind_total": len(ind), "ind_humano": sum(s == "indecidivel" for s, _, _ in ind),
            "ind_verdadeiro": sum(s == "verdadeiro" for s, _, _ in ind)}


def linha_total(nome: str, m: dict, falhas: int = 0) -> dict:
    return {"variante": nome, "decidíveis": m["decidiveis"], "decididas": m["decididas"], "P": m["P"], "R": m["R"], "F1": m["F1"],
            "F1 com V a humano = perdidas": m["F1_v_humano_perdidas"], "humano (decidíveis)": f"{m['humano']} ({m['humano_frac']:.3f})",
            "V a humano": m["v_humano"], "F a humano": m["f_humano"],
            "PERDIDAS (V → falso)": f"{m['perdidas']}/{m['verdadeiras']}", "FP EM NEGAÇÃO": m["fp_negacao"],
            "indecidíveis → humano": f"{m['ind_humano']}/{m['ind_total']} (V: {m['ind_verdadeiro']})", "falhas": falhas}


def veredito(jev: dict, base: dict, falhas: int) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    lim = P.CRITERIO_CONTINUAR["limites"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    linhas = [
        {"critério": "1 F1 (decididas)", "medido": f"{jev['F1']:.3f} (baseline {base['F1']:.3f})",
         "limite": f"≥ {lim['f1_min']} e ≥ {base['F1'] + lim['margem_baseline']:.3f}",
         "passa": ok(jev["F1"] >= lim["f1_min"] and jev["F1"] >= base["F1"] + lim["margem_baseline"])},
        {"critério": "2 perdidas (V → falso)", "medido": f"{jev['perdidas']}/{jev['verdadeiras']} ({jev['perdidas_frac']:.3f})",
         "limite": f"≤ {lim['perdidas_max']}", "passa": ok(jev["perdidas_frac"] <= lim["perdidas_max"])},
        {"critério": "3 FP em negação", "medido": jev["fp_negacao"], "limite": f"≤ {lim['fp_negacao_max']}",
         "passa": ok(jev["fp_negacao"] <= lim["fp_negacao_max"])},
        {"critério": "4 humano (decidíveis)", "medido": f"{jev['humano']}/{jev['decidiveis']} ({jev['humano_frac']:.3f})",
         "limite": f"≤ {lim['humano_max']}", "passa": ok(jev["humano_frac"] <= lim["humano_max"])},
        {"critério": "secundário: indecidíveis → humano", "medido": f"{jev['ind_humano']}/{jev['ind_total']}",
         "limite": f"≥ {lim['indecidiveis_a_humano_min']}",
         "passa": ok(jev["ind_total"] == 0 or jev["ind_humano"] / jev["ind_total"] >= lim["indecidiveis_a_humano_min"])},
        {"critério": "secundário: falhas operacionais", "medido": falhas, "limite": "0", "passa": ok(falhas == 0)},
    ]
    return M.tabela(linhas)


def secao_conjunto(nome: str, dados: dict, linhas: list[dict]) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custo = rodar(casos, linhas)
    seps = {c["id"]: S.separar_seguro(c["condicao"]) for c in casos}
    bases = {c["id"]: [S.baseline_seguro(seps[c["id"]], l) for l in linhas] for c in casos}
    custo["falhas_baseline"] = sum(b["falha"] for bs in bases.values() for b in bs)
    gabs = {c["id"]: gabarito(c) for c in casos}
    fams = {c["id"]: familia(c) for c in casos}

    def itens(variante: dict | None, so: str | None = None):
        out = []
        for c in casos:
            if so and c["id"] != so:
                continue
            for l, s in zip(linhas, saidas[c["id"]]):
                saida = s["saida"] if variante is None else redecidir(s, seps[c["id"]]["conector"], variante)
                out.append((saida, gabs[c["id"]].get(l["id"], "falso"), fams[c["id"]]))
        return out

    def itens_base(so: str | None = None):
        return [(b["saida"], gabs[c["id"]].get(l["id"], "falso"), fams[c["id"]])
                for c in casos if not so or c["id"] == so for l, b in zip(linhas, bases[c["id"]])]

    oficial, base = metricas(itens(None)), metricas(itens_base())
    dificeis = sum(fams[c["id"]] != "fácil" for c in casos)
    resumo = {"n_condicoes": len(casos), "dificeis": dificeis, "n_linhas": len(linhas), "custo": custo, "jev": oficial, "baseline": base,
              "variantes": {v: metricas(itens(var)) for v, var in VARIANTES.items()}}

    out = [f"## Conjunto `{nome}` — {len(casos)} condições × {len(linhas)} linhas (arquivo versão {dados.get('versao')}, autor "
           f"{dados.get('autor')}); {dificeis} difíceis; {sum(len(c['linhas_verdadeiras']) for c in casos)} verdadeiras e "
           f"{sum(len(c['linhas_indecidiveis']) for c in casos)} indecidíveis no gabarito\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if custo["falhas_operacionais"] or custo["falhas_baseline"]:
        out.append(f"> **{custo['falhas_operacionais']} falha(s) operacional(is)** (Jev) e **{custo['falhas_baseline']}** (baseline) neste "
                   "conjunto: essas linhas saíram `indecidivel` sem julgamento (condição inválida, campo com tipo errado ou "
                   "chamada que falhou). **As métricas abaixo não são medição** — corrija a entrada ou rode de novo.\n")

    # --- total
    out.append("### Total (micro, sobre as linhas decidíveis de todas as condições) — Jev × variantes × baseline LIKE\n")
    out.append("P/R/F1 sobre as decidíveis que o sistema DECIDIU; `humano` = decidíveis mandadas a `indecidivel` (fora de P/R/F1), "
               "separadas em `V a humano` e `F a humano`; `F1 com V a humano = perdidas` conta só as verdadeiras mandadas a humano "
               "como perdidas (as falsas a humano não o alteram). **PERDIDAS** = verdadeira do gabarito que saiu `falso` (o filtro perdeu a linha). "
               "**FP EM NEGAÇÃO** = falsa marcada `verdadeiro` numa condição da família negação (o erro do LIKE). "
               "`indecidíveis → humano` = linhas de pista fraca do gabarito que o sistema mandou revisar (e quantas virou `verdadeiro`). "
               f"Variante oficial: `{P.VARIANTE['composta']}`" + (" + pista" if P.VARIANTE["pista"] else "") +
               f"; faixa de `stated` {P.FAIXA['stated'][0]}–{P.FAIXA['stated'][1]}; `hinted` ≥ {P.PISTA_SIM}.\n")
    tab = [linha_total("Jev (oficial)", oficial, custo["falhas_operacionais"])]
    tab += [linha_total(f"Jev: {v}", m) for v, m in resumo["variantes"].items()]
    tab.append(linha_total("baseline LIKE", base, custo["falhas_baseline"]))
    out.append(M.tabela(tab, COLUNAS_TOTAL) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(oficial, base, custo["falhas_operacionais"]) + "\n")

    # --- por condição
    out.append("### Por condição\n")
    out.append("`filtro` = parte de campo resolvida pelo código; `chamadas` = linhas que passaram no filtro e foram ao Jev; "
               "`V/I` = verdadeiras / indecidíveis do gabarito; `base` = baseline LIKE (radicais entre colchetes).\n")
    tab = []
    for c in casos:
        m, b = metricas(itens(None, c["id"])), metricas(itens_base(c["id"]))
        sep = seps[c["id"]]
        tab.append({"id": c["id"], "família": fams[c["id"]],
                    "filtro": sep["erro"].upper() if sep.get("erro") else " ".join(f"{a} {o} {v}" for a, o, v in sep["filtros"]) or "—",
                    "composta": sep["conector"] or "—", "chamadas": sum(s["por"] != "filtro" for s in saidas[c["id"]]),
                    "V/I": f"{len(c['linhas_verdadeiras'])}/{len(c['linhas_indecidiveis'])}",
                    "P": m["P"], "R": m["R"], "F1": m["F1"], "humano": m["humano"], "perdidas": m["perdidas"], "FP": m["fp"],
                    "I → humano": f"{m['ind_humano']}/{m['ind_total']}", "base F1": b["F1"], "base FP": b["fp"], "base perdidas": b["perdidas"],
                    "LIKE": "[" + ", ".join(S.palavras_like(sep["semantica"])) + "]"})
    resumo["condicoes"] = tab
    out.append(M.tabela(tab) + "\n")

    # --- por família
    out.append("### Por família difícil (pela `nota` do rotulador)\n")
    tab = []
    for fam in list(dict.fromkeys(fams.values())):
        m = metricas([i for i in itens(None) if i[2] == fam])
        b = metricas([i for i in itens_base() if i[2] == fam])
        tab.append({"família": fam, "condições": sum(f == fam for f in fams.values()), "F1 Jev": m["F1"], "F1 baseline": b["F1"],
                    "humano Jev": m["humano"], "perdidas Jev": m["perdidas"], "FP Jev": m["fp"], "perdidas base": b["perdidas"], "FP base": b["fp"],
                    "I → humano": f"{m['ind_humano']}/{m['ind_total']}"})
    resumo["familias"] = tab
    out.append(M.tabela(tab) + "\n")

    # --- distribuição de `stated` por gabarito (onde os limiares cortam)
    out.append("### Onde `stated` cai, por gabarito (só linhas que foram ao Jev)\n")
    tab = []
    for g in ("verdadeiro", "falso", "indecidivel"):
        vals = sorted(s["valores"]["stated"] for c in casos for l, s in zip(linhas, saidas[c["id"]])
                      if s["por"] == "jev" and gabs[c["id"]].get(l["id"], "falso") == g)
        hint = sorted(s["valores"]["hinted"] for c in casos for l, s in zip(linhas, saidas[c["id"]])
                      if s["por"] == "jev" and gabs[c["id"]].get(l["id"], "falso") == g)
        q = lambda xs, f: xs[min(len(xs) - 1, int(f * len(xs)))] if xs else float("nan")  # noqa: E731
        tab.append({"gabarito": g, "n": len(vals), "stated mín": q(vals, 0), "p10": q(vals, 0.1), "p50": q(vals, 0.5), "p90": q(vals, 0.9),
                    "máx": q(vals, 1), "≤ 0,2": sum(v <= 0.2 for v in vals), "0,2–0,8": sum(0.2 < v < 0.8 for v in vals),
                    "≥ 0,8": sum(v >= 0.8 for v in vals), "hinted p50": q(hint, 0.5), "hinted ≥ 0,8": sum(v >= 0.8 for v in hint)})
    out.append(M.tabela(tab) + "\n")

    # --- curva
    out.append("### Cobertura × erro por faixa de `stated` (variante oficial; mesmas respostas, outra faixa)\n")
    antes = P.FAIXA
    tab = []
    try:
        for faixa in [None, *GRADE_FAIXA]:
            P.FAIXA = antes if faixa is None else {**antes, "stated": faixa}
            m = metricas(itens(P.VARIANTE))
            tab.append({"faixa": "atual (perguntas.py)" if faixa is None else f"{faixa[0]}–{faixa[1]}",
                        "cobertura (decididas/decidíveis)": m["decididas"] / m["decidiveis"] if m["decidiveis"] else float("nan"),
                        "erro entre decididas": (m["fp"] + m["fn"]) / m["decididas"] if m["decididas"] else float("nan"),
                        "F1": m["F1"], "humano": m["humano"], "perdidas": m["perdidas"], "FP em negação": m["fp_negacao"],
                        "I → humano": f"{m['ind_humano']}/{m['ind_total']}"})
    finally:
        P.FAIXA = antes
    resumo["curva"] = tab
    out.append(M.tabela(tab) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"linhas avaliadas (cond × linha)": custo["linhas_avaliadas"], "sem chamada (filtro)": custo["sem_chamada"],
                          "requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "textos longos (sem chamada)": custo["textos_longos"], "falhas operacionais (→ indecidivel)": custo["falhas_operacionais"],
                          "perguntas": custo["perguntas"], "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_requisicao": round(custo["input_tokens"] / req), "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_1000_linhas_avaliadas": f"{1000 * custo['custo_us'] / max(custo['linhas_avaliadas'], 1):.4f}",
                          "US$_por_1000_requisicoes": f"{1000 * custo['custo_us'] / req:.4f}", "modelo": ", ".join(custo["modelos"])}]) + "\n")

    # --- caso a caso (só o que interessa: erros, humano e indecidíveis do gabarito)
    out.append("### Caso a caso — erros, linhas mandadas a humano e indecidíveis do gabarito\n")
    out.append("`st`/`hi` = Nouls `stated` e `hinted`; `partes` = Nouls por cláusula (compostas); `saída` = variante oficial; `base` = LIKE.\n")
    f2 = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731
    tab = []
    for c in casos:
        for l, s in zip(linhas, saidas[c["id"]]):
            g = gabs[c["id"]].get(l["id"], "falso")
            if s["saida"] == g and g != "indecidivel":
                continue
            v = s["valores"] or {}
            partes = ", ".join(f2(v[k]) for k in sorted(k for k in v if k.startswith("stated_part_")))
            tab.append({"cond": c["id"], "linha": l["id"], "gab": g, "st": f2(v.get("stated")), "hi": f2(v.get("hinted")), "partes": partes or "—",
                        "saída": s["saida"], "ok": "✓" if s["saida"] == g else "✗", "base": bases[c["id"]][linhas.index(l)]["saida"],
                        "por": s["por"], "texto": l["texto"][:110].replace("|", "/") + ("…" if len(l["texto"]) > 110 else "")})
    out.append(M.tabela(tab) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n"]
    tab = []
    for n, r in resumos.items():
        tab.append({"conjunto": n, **linha_total("Jev (oficial)", r["jev"], r["custo"]["falhas_operacionais"])})
        tab.append({"conjunto": n, **linha_total("baseline LIKE", r["baseline"])})
    out.append(M.tabela(tab, ["conjunto", *COLUNAS_TOTAL]) + "\n")
    out.append(M.tabela([{"conjunto": n, "condições": r["n_condicoes"], "difíceis": r["dificeis"], "linhas": r["n_linhas"],
                          "requisições": r["custo"]["requisicoes"], "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_requisicao": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000_linhas": f"{1000 * r['custo']['custo_us'] / max(r['custo']['linhas_avaliadas'], 1):.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; cega ou não, conforme a rodada declarada no README): {h}"


def _congelar() -> dict:
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    return "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_CONTINUAR.items() if k != "limites")


def _dados(nome: str) -> dict:
    return json.loads((AQUI / "dados" / ARQUIVOS[nome]).read_text(encoding="utf-8"))


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    linhas = json.loads((AQUI / "dados" / "linhas.json").read_text(encoding="utf-8"))["linhas"]
    if "teste" in conjuntos:
        # O teste só roda com perguntas, política, tabela, condições E critério congelados, e dentro do orçamento declarado.
        try:
            manifesto = CG.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != P.CRITERIO_CONTINUAR:
            sys.exit("teste recusado: o critério de continuar mudou desde o congelamento (rode `run.py congelar`)")
        previstas = requisicoes_previstas(_dados("teste")["casos"], linhas)
        if previstas > P.ORCAMENTO["teste"]:
            sys.exit(f"teste recusado: {previstas} requisições previstas > orçamento {P.ORCAMENTO['teste']} (perguntas.ORCAMENTO)")
        linha = _linha_manifesto(manifesto)
    elif congelar:
        linha = _linha_manifesto(_congelar())
    else:
        h = CG.hashes(AQUI, CONGELADOS)
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())
    if args == ["rascunho"]:
        texto, _ = secao_conjunto("rascunho", _dados("rascunho"), linhas)
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — sql-semantico (encanamento)\n\n{texto}", encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, _dados(nome), linhas)
        partes.append(texto)
    cabecalho = (f"# Resultados — sql-semantico\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas e política: "
                 f"`perguntas.py`; separação da condição, filtro, validação, decisão e baseline: `sql.py`. Preço: US$ 0,042 por milhão de "
                 f"tokens de entrada. Teto do texto: {P.TETO_CARACTERES} caracteres (acima → indecidivel, sem chamada). "
                 f"Orçamento: {P.ORCAMENTO['teste']} requisições no teste.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: r["custo"]["falhas_operacionais"] for n, r in resumos.items() if r["custo"]["falhas_operacionais"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — essas linhas saíram `indecidivel` sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists():
        # A primeira execução com o teste É a rodada cega: fica preservada e nunca é reescrita por este script.
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
