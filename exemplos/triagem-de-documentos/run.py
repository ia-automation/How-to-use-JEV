"""Roda a triagem de documentos num conjunto de condições rotuladas, nos DOIS desenhos, e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 condições fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, triagem.py, run.py,
                             dados/documentos.json, dados/condicoes_teste.json e o critério; hash de _comum/ só como registro)
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo e dentro do orçamento.
                             A PRIMEIRA execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Desenho A (mapa): uma requisição por seção; desenho B (inteiro): uma por documento; condição numérica: zero chamada.
Falha operacional NÃO aborta o lote: aquele documento sai `indecidivel` pelas `*_seguro` e é contado à parte —
conjunto com falha não é medição do Jev. Bateria do código (sem chave nem rede): `testa_falhas.py`.
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
import triagem as T  # noqa: E402
from jevcache import Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
ARQUIVOS = {"ajuste": "condicoes_ajuste.json", "teste": "condicoes_teste.json", "rascunho": "rascunho.json"}
CONGELADOS = ["perguntas.py", "triagem.py", "run.py", "dados/documentos.json", "dados/condicoes_teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
DESENHOS = {"mapa": "A: mapa por seção", "inteiro": "B: documento inteiro"}
GRADE_FAIXA = [(0.5, 0.5), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9)]
# "documento sem a cláusula" é a família "sem a cláusula" (rodada 2: a expressão da rodada 1 contava T09 como "fácil").
FAMILIAS = r"difícil:\s*(negada|revogada|duas seções|termo só no título|seção parecida|(?:documento )?sem a cláusula)"
COLUNAS_TOTAL = ["desenho", "decidíveis", "decididas", "P", "R", "F1", "humano (decidíveis)", "V a humano", "PERDIDAS (V → falso)",
                 "FP", "FP NEGADA/REVOGADA", "prova certa (V semânticos)", "indecidíveis → humano", "falhas"]


def familia(c: dict) -> str:
    m = re.match(FAMILIAS, c.get("nota") or "")
    return m.group(1).replace("documento ", "") if m else "fácil"


def separar(c: dict) -> dict:
    """`separar_seguro` com o `tipo` do rotulador (achado 1: `tipo` ausente ou em desacordo com a forma = condição inválida)."""
    return T.separar_seguro(c.get("condicao"), c.get("tipo"))


def gabarito(c: dict) -> dict:
    """{id do documento: verdadeiro | indecidivel}; documento fora das duas listas vale falso (LEIA-ME)."""
    g = {i: "verdadeiro" for i in c["documentos_verdadeiros"]}
    g.update({i: "indecidivel" for i in c["documentos_indecidiveis"]})
    return g


def requisicoes_previstas(casos: list[dict], docs: list[dict]) -> int:
    """Condição semântica válida: uma requisição por seção (A) + uma por documento (B); numérica ou inválida: zero."""
    n = 0
    for c in casos:
        sep = separar(c)
        if not sep.get("erro") and not sep["numerica"]:
            n += sum(len(d.get("secoes") or []) for d in docs) + len(docs)
    return n


def _custo_vazio() -> dict:
    return {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0, "input_tokens": 0,
            "custo_us": 0.0, "modelos": []}


def rodar(casos: list[dict], docs: list[dict]) -> tuple[dict, dict]:
    """{desenho: {id da condição: [saída por documento]}} e {desenho: custo}. Um `Jev` por (condição, documento) para medir
    tokens e latência POR DOCUMENTO (no mapa, a soma das seções); o cache em disco é o mesmo. Falha operacional vira
    `indecidivel` só naquele documento, contada à parte."""
    seps = {c["id"]: separar(c) for c in casos}
    pares = [(c["id"], d) for c in casos for d in docs]
    saidas, custos = {}, {}

    def um(desenho, par):
        cid, d = par
        jev = Jev(AQUI / "cache")
        s = T.AVALIAR[desenho](jev, seps[cid], d)
        ms = [c["ms"] for c in jev.chamadas]
        s["doc_medicao"] = {"requisicoes": len(ms), "ms_serial": sum(ms), "ms_paralelo": max(ms, default=0),  # ESTIMATIVA idealizada: as seções foram chamadas em sequência (achado 4)
                            "tokens": sum(c["input_tokens"] for c in jev.chamadas)}
        return s, jev

    for desenho in DESENHOS:
        with ThreadPoolExecutor(8) as ex:
            lista = list(ex.map(lambda p: um(desenho, p), pares))
        total = Jev(AQUI / "cache")
        for _, jev in lista:
            total.chamadas.extend(jev.chamadas)
        custo = total.resumo() or _custo_vazio()
        custo["documentos_avaliados"] = len(pares)
        custo["sem_chamada"] = sum(s["por"] == "codigo" for s, _ in lista)
        custo["textos_longos"] = sum(bool(s.get("longo")) for s, _ in lista)
        custo["falhas_operacionais"] = sum(bool(s.get("falha")) for s, _ in lista)
        com = [s["doc_medicao"] for s, _ in lista if s["doc_medicao"]["requisicoes"]]
        q = lambda xs, f: sorted(xs)[min(len(xs) - 1, int(f * len(xs)))] if xs else 0  # noqa: E731
        custo["por_documento"] = {"n": len(com), "tokens_p50": q([m["tokens"] for m in com], 0.5),
                                  "ms_serial_p50": q([m["ms_serial"] for m in com], 0.5), "ms_serial_p95": q([m["ms_serial"] for m in com], 0.95),
                                  "ms_paralelo_p50": q([m["ms_paralelo"] for m in com], 0.5), "ms_paralelo_p95": q([m["ms_paralelo"] for m in com], 0.95)}
        saidas[desenho] = {c["id"]: [] for c in casos}
        for (cid, _), (s, _) in zip(pares, lista):
            saidas[desenho][cid].append(s)
        custos[desenho] = custo
    return saidas, custos


def redecidir(s: dict, desenho: str, faixa: dict, adiado: float) -> str:
    """Re-decide com outra faixa a partir dos números guardados (sem cache nem API); saída sem números fica."""
    if s["por"] != "jev":
        return s["saida"]
    if desenho == "mapa":
        return T.reduzir(s["secoes"], faixa, adiado)[0]
    return T.decidir_inteiro(s["valores"], faixa, adiado)[0]


def metricas(itens: list[tuple]) -> dict:
    """itens = [(saída, gabarito, família, prova_ok)]. Micro sobre os documentos DECIDÍVEIS (gabarito ≠ indecidível);
    decidível mandado a humano fica fora de P/R/F1 e é contado à parte. PERDIDA = verdadeiro do gabarito que saiu `falso`;
    FP NEGADA/REVOGADA = falso marcado `verdadeiro` em condição das famílias negada/revogada (o erro da busca por palavra);
    prova_ok = None quando não se mede (numérica, documento falso) — `prova` é a fração entre os verdadeiros semânticos."""
    decid = [i for i in itens if i[1] != "indecidivel"]
    tp = sum(s == "verdadeiro" and g == "verdadeiro" for s, g, _, _ in decid)
    fp = sum(s == "verdadeiro" and g == "falso" for s, g, _, _ in decid)
    fn = sum(s == "falso" and g == "verdadeiro" for s, g, _, _ in decid)
    humano = sum(s == "indecidivel" for s, _, _, _ in decid)
    v_humano = sum(s == "indecidivel" and g == "verdadeiro" for s, g, _, _ in decid)
    verdadeiras = sum(g == "verdadeiro" for _, g, _, _ in decid)
    ind = [i for i in itens if i[1] == "indecidivel"]
    provas = [ok for s, g, _, ok in decid if g == "verdadeiro" and ok is not None]
    div = lambda a, b: a / b if b else float("nan")  # noqa: E731
    zero = lambda a, b: a / b if b else 0.0  # noqa: E731 — sem positivo previsto: P = 0, não indefinido
    p, r = zero(tp, tp + fp), zero(tp, tp + fn)
    return {"decidiveis": len(decid), "decididas": len(decid) - humano, "tp": tp, "fp": fp, "fn": fn, "verdadeiras": verdadeiras,
            "P": p, "R": r, "F1": zero(2 * p * r, p + r), "humano": humano, "humano_frac": div(humano, len(decid)),
            "v_humano": v_humano, "perdidas": fn, "perdidas_frac": div(fn, verdadeiras),
            "fp_negada_revogada": sum(s == "verdadeiro" and g == "falso" and f in ("negada", "revogada") for s, g, f, _ in decid),
            "prova_ok": sum(provas), "prova_n": len(provas), "prova_frac": div(sum(provas), len(provas)),
            "ind_total": len(ind), "ind_humano": sum(s == "indecidivel" for s, _, _, _ in ind),
            "ind_verdadeiro": sum(s == "verdadeiro" for s, _, _, _ in ind)}


def linha_total(nome: str, m: dict, falhas: int = 0) -> dict:
    return {"desenho": nome, "decidíveis": m["decidiveis"], "decididas": m["decididas"], "P": m["P"], "R": m["R"], "F1": m["F1"],
            "humano (decidíveis)": f"{m['humano']} ({m['humano_frac']:.3f})", "V a humano": m["v_humano"],
            "PERDIDAS (V → falso)": f"{m['perdidas']}/{m['verdadeiras']}", "FP": m["fp"], "FP NEGADA/REVOGADA": m["fp_negada_revogada"],
            "prova certa (V semânticos)": f"{m['prova_ok']}/{m['prova_n']} ({m['prova_frac']:.3f})",
            "indecidíveis → humano": f"{m['ind_humano']}/{m['ind_total']} (V: {m['ind_verdadeiro']})", "falhas": falhas}


def veredito(jev: dict, base: dict, falhas: int) -> str:
    """Confere o critério congelado contra os números do desenho padrão (gerado, não escrito à mão)."""
    lim = P.CRITERIO_CONTINUAR["limites"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    linhas = [
        {"critério": "1 F1 (decididas)", "medido": f"{jev['F1']:.3f} (baseline {base['F1']:.3f})",
         "limite": f"≥ {lim['f1_min']} e ≥ {base['F1'] + lim['margem_baseline']:.3f}",
         "passa": ok(jev["F1"] >= lim["f1_min"] and jev["F1"] >= base["F1"] + lim["margem_baseline"])},
        {"critério": "2 perdidas (V → falso)", "medido": f"{jev['perdidas']}/{jev['verdadeiras']} ({jev['perdidas_frac']:.3f})",
         "limite": f"≤ {lim['perdidas_max']}", "passa": ok(jev["perdidas_frac"] <= lim["perdidas_max"])},
        {"critério": "3 FP negada/revogada", "medido": jev["fp_negada_revogada"], "limite": f"≤ {lim['fp_negada_revogada_max']}",
         "passa": ok(jev["fp_negada_revogada"] <= lim["fp_negada_revogada_max"])},
        {"critério": "4 humano (decidíveis)", "medido": f"{jev['humano']}/{jev['decidiveis']} ({jev['humano_frac']:.3f})",
         "limite": f"≤ {lim['humano_max']}", "passa": ok(jev["humano_frac"] <= lim["humano_max"])},
        {"critério": "secundário: seção que prova", "medido": f"{jev['prova_ok']}/{jev['prova_n']} ({jev['prova_frac']:.3f})",
         "limite": f"≥ {lim['prova_min']}", "passa": ok(jev["prova_n"] == 0 or jev["prova_frac"] >= lim["prova_min"])},
        {"critério": "secundário: indecidíveis → humano", "medido": f"{jev['ind_humano']}/{jev['ind_total']}",
         "limite": f"≥ {lim['indecidiveis_a_humano_min']}",
         "passa": ok(jev["ind_total"] == 0 or jev["ind_humano"] / jev["ind_total"] >= lim["indecidiveis_a_humano_min"])},
        {"critério": "secundário: falhas operacionais", "medido": falhas, "limite": "0", "passa": ok(falhas == 0)},
    ]
    return M.tabela(linhas)


def _q(xs: list, f: float):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(f * len(xs)))] if xs else float("nan")


def secao_conjunto(nome: str, dados: dict, docs: list[dict]) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custos = rodar(casos, docs)
    seps = {c["id"]: separar(c) for c in casos}
    bases = {c["id"]: [T.baseline_seguro(seps[c["id"]], d) for d in docs] for c in casos}
    falhas_base = sum(bool(b.get("falha")) for bs in bases.values() for b in bs)
    gabs, fams = {c["id"]: gabarito(c) for c in casos}, {c["id"]: familia(c) for c in casos}
    semantica = {c["id"]: not seps[c["id"]].get("erro") and not seps[c["id"]]["numerica"] for c in casos}

    def item(c, d, s):
        g = gabs[c["id"]].get(d["id"], "falso")
        ok = (s.get("prova") == c["secao_que_prova"].get(d["id"])) if (semantica[c["id"]] and g == "verdadeiro") else None
        return g, fams[c["id"]], ok

    def itens(desenho: str, faixa=None, adiado=None, so=None, so_semantica=False):
        out = []
        for c in casos:
            if (so and c["id"] != so) or (so_semantica and not semantica[c["id"]]):
                continue
            for d, s in zip(docs, saidas[desenho][c["id"]]):
                saida = s["saida"] if faixa is None else redecidir(s, desenho, faixa, adiado)
                out.append((saida, *item(c, d, s)))
        return out

    def itens_base(so=None):
        return [(b["saida"], *item(c, d, b)) for c in casos if not so or c["id"] == so for d, b in zip(docs, bases[c["id"]])]

    ms = {k: metricas(itens(k)) for k in DESENHOS}
    base = metricas(itens_base())
    dificeis = sum(fams[c["id"]] != "fácil" for c in casos)
    resumo = {"n_condicoes": len(casos), "dificeis": dificeis, "n_docs": len(docs), "semanticas": sum(semantica.values()),
              "custo": custos, "desenhos": ms, "baseline": base}
    falhas = {k: custos[k]["falhas_operacionais"] for k in DESENHOS}

    out = [f"## Conjunto `{nome}` — {len(casos)} condições ({sum(semantica.values())} semânticas) × {len(docs)} documentos (arquivo versão "
           f"{dados.get('versao')}, autor {dados.get('autor')}); {dificeis} difíceis; "
           f"{sum(len(c['documentos_verdadeiros']) for c in casos)} verdadeiros e {sum(len(c['documentos_indecidiveis']) for c in casos)} "
           "indecidíveis no gabarito\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if any(falhas.values()) or falhas_base:
        out.append(f"> **Falhas operacionais**: {falhas} (Jev) e {falhas_base} (baseline): esses documentos saíram `indecidivel` sem "
                   "julgamento. **As métricas abaixo não são medição** — corrija a entrada ou rode de novo.\n")

    # --- total
    out.append("### Total (micro, sobre os documentos decidíveis de todas as condições) — desenho A × desenho B × baseline\n")
    out.append("P/R/F1 sobre os decidíveis que o sistema DECIDIU; `humano` = decidíveis mandados a `indecidivel` (fora de P/R/F1). "
               "**PERDIDAS** = verdadeiro do gabarito que saiu `falso`. **FP NEGADA/REVOGADA** = falso marcado `verdadeiro` em condição "
               "das famílias negada/revogada (cláusula negada ou revogada lida como presente — o erro caro). `prova certa` = entre os "
               "verdadeiros das condições semânticas, a seção apontada (A: maior `establishes`; B: Choice) é a do gabarito. "
               f"Desenho padrão: `{P.DESENHO_PADRAO}`; faixas {P.FAIXA}; `deferred` ≥ {P.ADIADO_SIM}.\n")
    tab = [linha_total(DESENHOS[k] + (" (padrão)" if k == P.DESENHO_PADRAO else ""), ms[k], falhas[k]) for k in DESENHOS]
    tab.append(linha_total("baseline palavras-chave", base, falhas_base))
    out.append(M.tabela(tab, COLUNAS_TOTAL) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(ms[P.DESENHO_PADRAO], base, falhas[P.DESENHO_PADRAO]) + "\n")

    # --- A × B
    out.append("### Desenho A × desenho B (só condições semânticas; mesmos documentos, pareado)\n")
    a, b = itens("mapa", so_semantica=True), itens("inteiro", so_semantica=True)
    pares = [(x[0], y[0], x[1]) for x, y in zip(a, b) if x[1] != "indecidivel"]
    ma, mb = metricas(a), metricas(b)
    tab = [{"n (decidíveis)": len(pares), "F1 A": ma["F1"], "F1 B": mb["F1"], "F1 A − B": ma["F1"] - mb["F1"],
            "A certo, B errado": sum(x == g and y != g for x, y, g in pares), "B certo, A errado": sum(y == g and x != g for x, y, g in pares),
            "os dois errados": sum(x != g and y != g for x, y, g in pares), "humano A / B": f"{ma['humano']} / {mb['humano']}",
            "perdidas A / B": f"{ma['perdidas']} / {mb['perdidas']}", "FP A / B": f"{ma['fp']} / {mb['fp']}",
            "prova certa A / B": f"{ma['prova_ok']}/{ma['prova_n']} / {mb['prova_ok']}/{mb['prova_n']}"}]
    resumo["a_x_b"] = tab[0]
    out.append(M.tabela(tab) + "\n")

    # --- por condição
    out.append("### Por condição\n")
    out.append("`tipo` = semântica (Jev) ou numérica (código, igual nos dois desenhos); `V/I` = verdadeiros / indecidíveis do gabarito; "
               "`hum` = a humano; `perd` = perdidas; `prova` = seção que prova certa; `base` = palavras-chave (radicais entre colchetes).\n")
    tab = []
    for c in casos:
        sep = seps[c["id"]]
        linha = {"id": c["id"], "família": fams[c["id"]],
                 "tipo": sep["erro"].upper() if sep.get("erro") else ("numérica " + " ".join(map(str, sep["numerica"])) if sep["numerica"] else "semântica"),
                 "V/I": f"{len(c['documentos_verdadeiros'])}/{len(c['documentos_indecidiveis'])}"}
        for k, rot in (("mapa", "A"), ("inteiro", "B")):
            m = metricas(itens(k, so=c["id"]))
            linha.update({f"{rot} P": m["P"], f"{rot} R": m["R"], f"{rot} F1": m["F1"], f"{rot} hum": m["humano"], f"{rot} perd": m["perdidas"],
                          f"{rot} FP": m["fp"], f"{rot} prova": f"{m['prova_ok']}/{m['prova_n']}", f"{rot} I→hum": f"{m['ind_humano']}/{m['ind_total']}"})
        bm = metricas(itens_base(c["id"]))
        linha.update({"base F1": bm["F1"], "base FP": bm["fp"], "base perd": bm["perdidas"],
                      "radicais": "[" + ", ".join(T.radicais(sep["texto"])) + "]" if semantica[c["id"]] else "—"})
        tab.append(linha)
    resumo["condicoes"] = tab
    out.append(M.tabela(tab) + "\n")

    # --- por família
    out.append("### Por família difícil (pela `nota` do rotulador)\n")
    tab = []
    for fam in list(dict.fromkeys(fams.values())):
        fa, fb = metricas([i for i in itens("mapa") if i[2] == fam]), metricas([i for i in itens("inteiro") if i[2] == fam])
        fbase = metricas([i for i in itens_base() if i[2] == fam])
        tab.append({"família": fam, "condições": sum(f == fam for f in fams.values()), "F1 A": fa["F1"], "F1 B": fb["F1"], "F1 base": fbase["F1"],
                    "perdidas A/B/base": f"{fa['perdidas']}/{fb['perdidas']}/{fbase['perdidas']}", "FP A/B/base": f"{fa['fp']}/{fb['fp']}/{fbase['fp']}",
                    "humano A/B": f"{fa['humano']}/{fb['humano']}", "prova A/B": f"{fa['prova_ok']}/{fa['prova_n']} · {fb['prova_ok']}/{fb['prova_n']}"})
    resumo["familias"] = tab
    out.append(M.tabela(tab) + "\n")

    # --- onde os Nouls caem
    out.append("### Onde os Nouls caem, por gabarito (só documentos que foram ao Jev)\n")
    out.append("A: `establishes` da seção que prova (verdadeiros) ou o MÁXIMO entre as seções (falsos/indecidíveis); `revokes` = máximo no "
               "documento; B: `holds`. `deferred` = máximo no documento (A) ou o do documento (B).\n")
    tab = []
    for g in ("verdadeiro", "falso", "indecidivel"):
        for k in DESENHOS:
            vals, revs, defs = [], [], []
            for c in casos:
                for d, s in zip(docs, saidas[k][c["id"]]):
                    if s["por"] != "jev" or gabs[c["id"]].get(d["id"], "falso") != g:
                        continue
                    if k == "mapa":
                        prova = c["secao_que_prova"].get(d["id"])
                        por_id = {x["id"]: x for x in s["secoes"]}
                        vals.append(por_id[prova]["establishes"] if g == "verdadeiro" and prova in por_id else max(x["establishes"] for x in s["secoes"]))
                        revs.append(max(x["revokes"] for x in s["secoes"]))
                        defs.append(max(x["deferred"] for x in s["secoes"]))
                    else:
                        vals.append(s["valores"]["holds"])
                        defs.append(s["valores"]["deferred"])
            tab.append({"gabarito": g, "desenho": k, "n": len(vals), "mín": _q(vals, 0), "p10": _q(vals, 0.1), "p50": _q(vals, 0.5), "p90": _q(vals, 0.9),
                        "máx": _q(vals, 1), "≤ 0,2": sum(v <= 0.2 for v in vals), "0,2–0,8": sum(0.2 < v < 0.8 for v in vals), "≥ 0,8": sum(v >= 0.8 for v in vals),
                        "revokes p50 / ≥ 0,8": f"{_q(revs, 0.5):.2f} / {sum(v >= 0.8 for v in revs)}" if revs else "—",
                        "deferred p50 / ≥ 0,7": f"{_q(defs, 0.5):.2f} / {sum(v >= P.ADIADO_SIM for v in defs)}" if defs else "—"})
    out.append(M.tabela(tab) + "\n")

    # --- curva
    out.append("### Cobertura × erro por faixa (mesmas respostas, outra faixa; `deferred` fixo)\n")
    tab = []
    for k in DESENHOS:
        for faixa in [None, *GRADE_FAIXA]:
            fx = P.FAIXA if faixa is None else {q: faixa for q in P.FAIXA}
            m = metricas(itens(k, fx, P.ADIADO_SIM))
            tab.append({"desenho": k, "faixa": "atual (perguntas.py)" if faixa is None else f"{faixa[0]}–{faixa[1]}",
                        "cobertura (decididas/decidíveis)": m["decididas"] / m["decidiveis"] if m["decidiveis"] else float("nan"),
                        "erro entre decididas": (m["fp"] + m["fn"]) / m["decididas"] if m["decididas"] else float("nan"),
                        "F1": m["F1"], "humano": m["humano"], "perdidas": m["perdidas"], "FP": m["fp"], "FP neg/rev": m["fp_negada_revogada"],
                        "I → humano": f"{m['ind_humano']}/{m['ind_total']}"})
    resumo["curva"] = tab
    out.append(M.tabela(tab) + "\n")

    # --- custo
    out.append("### Custo e latência por desenho (medidos na chamada real; do cache também)\n")
    tab = []
    for k in DESENHOS:
        cu = custos[k]
        req, pd = max(cu["requisicoes"], 1), cu["por_documento"]
        tab.append({"desenho": k, "documentos avaliados (cond × doc)": cu["documentos_avaliados"], "sem chamada (numérica)": cu["sem_chamada"],
                    "requisições": cu["requisicoes"], "novas (não cache)": cu["requisicoes"] - cu["do_cache"], "falhas": cu["falhas_operacionais"],
                    "p50_ms / p95_ms por requisição": f"{cu['latencia_p50_ms']} / {cu['latencia_p95_ms']}", "tokens por requisição": round(cu["input_tokens"] / req),
                    "tokens por documento (p50)": pd["tokens_p50"], "ms por documento serial p50 / p95": f"{pd['ms_serial_p50']} / {pd['ms_serial_p95']}",
                    "ms por documento, estimativa idealizada = máx das seções (chamadas em sequência) p50 / p95": f"{pd['ms_paralelo_p50']} / {pd['ms_paralelo_p95']}", "US$ total": f"{cu['custo_us']:.6f}",
                    "US$ por mil documentos avaliados (semânticos)": f"{1000 * cu['custo_us'] / max(pd['n'], 1):.4f}", "modelo": ", ".join(cu["modelos"])})
    out.append(M.tabela(tab) + "\n")

    # --- caso a caso
    out.append("### Caso a caso — erros, documentos mandados a humano e indecidíveis do gabarito (em qualquer desenho)\n")
    out.append("`A` = mapa (motivo = passos da redução; `prova` = seção de maior `establishes`); `B` = inteiro (`holds`; prova = Choice); `gab prova` = `secao_que_prova`.\n")
    tab = []
    for c in casos:
        for i, d in enumerate(docs):
            g = gabs[c["id"]].get(d["id"], "falso")
            sa, sb = saidas["mapa"][c["id"]][i], saidas["inteiro"][c["id"]][i]
            if sa["saida"] == g and sb["saida"] == g and g != "indecidivel":
                continue
            tab.append({"cond": c["id"], "doc": d["id"], "gab": g, "gab prova": c["secao_que_prova"].get(d["id"], "—"),
                        "A": sa["saida"], "A ok": "✓" if sa["saida"] == g else "✗", "A prova": sa.get("prova") or "—", "A motivo": sa["motivo"].replace("|", "/"),
                        "B": sb["saida"], "B ok": "✓" if sb["saida"] == g else "✗", "B prova": sb.get("prova") or "—", "B motivo": sb["motivo"].replace("|", "/"),
                        "base": bases[c["id"]][i]["saida"]})
    out.append(M.tabela(tab) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n"]
    tab = []
    for n, r in resumos.items():
        for k in DESENHOS:
            tab.append({"conjunto": n, **linha_total(DESENHOS[k], r["desenhos"][k], r["custo"][k]["falhas_operacionais"])})
        tab.append({"conjunto": n, **linha_total("baseline palavras-chave", r["baseline"])})
    out.append(M.tabela(tab, ["conjunto", *COLUNAS_TOTAL]) + "\n")
    tab = []
    for n, r in resumos.items():
        for k in DESENHOS:
            cu = r["custo"][k]
            tab.append({"conjunto": n, "desenho": k, "condições": r["n_condicoes"], "semânticas": r["semanticas"], "difíceis": r["dificeis"],
                        "documentos": r["n_docs"], "requisições": cu["requisicoes"], "p50_ms": cu["latencia_p50_ms"], "p95_ms": cu["latencia_p95_ms"],
                        "tokens por requisição": round(cu["input_tokens"] / max(cu["requisicoes"], 1)),
                        "US$ por mil documentos": f"{1000 * cu['custo_us'] / max(cu['por_documento']['n'], 1):.4f}", "modelo": ", ".join(cu["modelos"])})
    out.append(M.tabela(tab) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}): {h}"


def _congelar() -> dict:
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _dados(nome: str) -> dict:
    return json.loads((AQUI / "dados" / ARQUIVOS[nome]).read_text(encoding="utf-8"))


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    docs = json.loads((AQUI / "dados" / "documentos.json").read_text(encoding="utf-8"))["documentos"]
    if "teste" in conjuntos:
        try:
            manifesto = CG.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != P.CRITERIO_CONTINUAR:
            sys.exit("teste recusado: o critério de continuar mudou desde o congelamento (rode `run.py congelar`)")
        previstas = requisicoes_previstas(_dados("teste")["casos"], docs)
        if previstas > P.ORCAMENTO["teste"]:
            sys.exit(f"teste recusado: {previstas} requisições previstas > orçamento {P.ORCAMENTO['teste']} (perguntas.ORCAMENTO)")
        linha = _linha_manifesto(manifesto)
    elif congelar:
        linha = _linha_manifesto(_congelar())
    else:
        h = CG.hashes(AQUI, CONGELADOS)
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())
    if args == ["rascunho"]:
        texto, _ = secao_conjunto("rascunho", _dados("rascunho"), docs)
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — triagem-de-documentos (encanamento)\n\n{texto}", encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, _dados(nome), docs)
        partes.append(texto)
    criterio = "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_CONTINUAR.items() if k != "limites")
    cabecalho = (f"# Resultados — triagem-de-documentos\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas e política: "
                 f"`perguntas.py`; parte numérica, states, redução, decisão e baseline: `triagem.py`. Preço: US$ 0,042 por milhão de "
                 f"tokens de entrada. Tetos: {P.TETO_CARACTERES} caracteres (acima → indecidivel, sem chamada). "
                 f"Orçamento: {P.ORCAMENTO['teste']} requisições no teste.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {criterio}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: {k: r["custo"][k]["falhas_operacionais"] for k in DESENHOS} for n, r in resumos.items() if any(r["custo"][k]["falhas_operacionais"] for k in DESENHOS)}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — esses documentos saíram `indecidivel` sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists():
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
