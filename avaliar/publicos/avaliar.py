"""Avalia o Jev em R5 (HateBR) e R4 (B2W) pelo PROTOCOLO.md congelado.

Modos:
  ajuste    roda as variantes de `perguntas.py` SÓ no ajuste e imprime métricas; os erros COM TEXTO vão
            para `.local/publicos/ajuste-relatorio.md` (texto licenciado não entra no repositório).
  congelar  grava `congelamento.json` com o sha256 de `perguntas.py` e `baselines.py` (antes do teste).
  teste     confere o congelamento, roda o teste UMA vez (depois disso, só do cache), roda os baselines e
            gera `resultados.md` (só agregados, IDs e hashes). Divergências com texto → `.local/publicos/`.
            Rodar de novo regenera o relatório do cache (ex.: depois de gravar `auditoria.json`).

Cache das respostas: `.local/publicos/cache/{ajuste,teste}/` (a chave do cache é o hash do texto).
Rodar: PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe avaliar/publicos/avaliar.py <modo>
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
LOCAL = RAIZ / ".local" / "publicos"
sys.path.insert(0, str(RAIZ / "exemplos" / "_comum"))
sys.path.insert(0, str(AQUI))
from jevcache import MODELO, PRECO_US_POR_MILHAO_ENTRADA, Jev  # noqa: E402
import perguntas as P  # noqa: E402
import baselines as B  # noqa: E402

BOOT = 2000
SEMENTE = 20260930
TENTATIVAS = 3  # erro operacional: repete a MESMA requisição até 3 vezes; o que sobrar é contado à parte
CONGELAMENTO = AQUI / "congelamento.json"


# ------------------------------------------------------------------------------------------ dados
def carregar(corpus: str, parte: str) -> list[dict]:
    itens = [json.loads(l) for l in (LOCAL / "divisoes" / f"{corpus}-{parte}.jsonl").open(encoding="utf-8")]
    prep = json.loads((AQUI / "preparacao.json").read_text(encoding="utf-8"))["corpora"][corpus][parte]
    h = hashlib.sha256(json.dumps(sorted(it["id"] for it in itens)).encode()).hexdigest()
    if h != prep["ids_sha256"]:
        raise SystemExit(f"{corpus}-{parte}: lista de IDs difere da publicada em preparacao.json")
    return itens


def state(corpus: str, it: dict) -> dict:
    """SÓ o texto que existiria no uso real (protocolo): nunca estrelas, produto, marca ou avaliador."""
    if corpus == "hatebr":
        return {"comment": it["texto"]}
    return {"review_title": it["titulo"], "review_text": it["corpo"]}


def sha_arquivo(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ------------------------------------------------------------------------------------------ Jev
def consultar(jev: Jev, corpus: str, itens: list[dict], questions: dict) -> list[dict]:
    """Uma requisição por item. Separa resposta válida, inválida e erro operacional."""
    def um(it):
        erro = None
        for t in range(TENTATIVAS):
            try:
                r = jev.perguntar(state(corpus, it), questions)
                break
            except Exception as e:  # noqa: BLE001 — qualquer falha da chamada é "erro operacional"
                if "não gravada" in str(e):
                    raise
                erro = f"{type(e).__name__}: {str(e)[:120]}"
                time.sleep(1 + 2 * t)
        else:
            return {"status": "erro_operacional", "erro": erro}
        ans = r.get("answers") or {}
        if any(q not in ans for q in questions):
            return {"status": "invalida", "erro": "pergunta sem resposta"}
        out = {"status": "ok", "modelo": r.get("model")}
        for q, a in ans.items():
            v = a.get("noul") if a.get("type") == "noul" else a.get("score")
            if v is None or not (0 <= v <= (1 if a.get("type") == "noul" else 4)):
                return {"status": "invalida", "erro": f"{q} fora da faixa"}
            out[q] = v
        return out
    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(um, itens))


def custo_cache(pasta: Path) -> dict:
    """Custo REAL gasto: cada arquivo do cache = uma chamada que de fato foi à API (inclui versões descartadas)."""
    regs = [json.loads(p.read_text(encoding="utf-8"))["medicao"] for p in pasta.rglob("*.json")]
    tok = sum(r["input_tokens"] for r in regs)
    return {"requisicoes": len(regs), "input_tokens": tok, "custo_us": round(tok / 1e6 * PRECO_US_POR_MILHAO_ENTRADA, 5)}


# ------------------------------------------------------------------------------------------ métricas
def binario(g, pred, escore=None, prob=None) -> dict:
    g, pred = np.asarray(g), np.asarray(pred)
    m = {"n": len(g), "acerto": float((g == pred).mean())}
    f1s = []
    for c in (1, 0):
        tp = int(((pred == c) & (g == c)).sum()); fp = int(((pred == c) & (g != c)).sum()); fn = int(((pred != c) & (g == c)).sum())
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f = 2 * p * r / (p + r) if p + r else 0.0
        m[f"P{c}"], m[f"R{c}"], m[f"F1_{c}"] = p, r, f
        f1s.append(f)
    m["macroF1"] = float(np.mean(f1s))
    m["matriz"] = {"tp": int(((pred == 1) & (g == 1)).sum()), "fp": int(((pred == 1) & (g == 0)).sum()),
                   "fn": int(((pred == 0) & (g == 1)).sum()), "tn": int(((pred == 0) & (g == 0)).sum())}
    if escore is not None and 0 < g.sum() < len(g):
        e = np.asarray(escore, dtype=float)
        m["PRAUC_1"] = float(average_precision_score(g, e))
        m["PRAUC_0"] = float(average_precision_score(1 - g, -e))
    m["prev_1"] = float(g.mean())
    if prob is not None:
        m["brier"] = float(np.mean((np.asarray(prob, dtype=float) - g) ** 2))
    return m


def ordinal(g, pred) -> dict:
    g, pred = np.asarray(g), np.asarray(pred)
    d = np.abs(g - pred)
    mat = [[int(((g == i) & (pred == j)).sum()) for j in range(1, 6)] for i in range(1, 6)]
    return {"n": len(g), "MAE": float(d.mean()), "exato": float((d == 0).mean()), "pm1": float((d <= 1).mean()), "matriz": mat}


def faixa(g, noul, nao, sim) -> dict:
    g, v = np.asarray(g), np.asarray(noul)
    dec = (v <= nao) | (v >= sim)
    ok = ((v >= sim) == (g == 1))[dec]
    return {"cobertura": float(dec.mean()), "acerto_decididos": float(ok.mean()) if ok.size else float("nan"),
            "revisao": int((~dec).sum()), "erros_decididos": int((~ok).sum())}


def escolher_limiar(g, noul) -> float:
    """Custo simétrico declarado em perguntas.py (FP = FN = 1); empate → mais perto de 0,5."""
    g, v = np.asarray(g), np.asarray(noul)
    return min(P.GRADE_LIMIAR, key=lambda t: (int(((v >= t) != (g == 1)).sum()), abs(t - 0.5)))


def bootstrap(grupos: list[str], estat, B_=BOOT) -> tuple[float, float]:
    """IC 95% percentil reamostrando GRUPOS (post / produto) com reposição."""
    idx_por = {}
    for i, gr in enumerate(grupos):
        idx_por.setdefault(gr, []).append(i)
    blocos = list(idx_por.values())
    rng = np.random.default_rng(SEMENTE)
    vals = []
    for _ in range(B_):
        esc = rng.integers(0, len(blocos), len(blocos))
        idx = np.concatenate([blocos[k] for k in esc])
        vals.append(estat(idx))
    vals = np.asarray(vals, dtype=float)
    return float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))


def _mf1(g, p, idx):
    return binario(np.asarray(g)[idx], np.asarray(p)[idx])["macroF1"]


def _ap(g, e, idx, classe=1):
    g, e = np.asarray(g)[idx], np.asarray(e, dtype=float)[idx]
    if not 0 < g.sum() < len(g):
        return float("nan")
    return float(average_precision_score(g, e) if classe == 1 else average_precision_score(1 - g, -e))


# ------------------------------------------------------------------------------------------ ajuste
def modo_ajuste() -> None:
    jev = Jev(LOCAL / "cache" / "ajuste")
    linhas_local = ["# Relatório do AJUSTE (LOCAL — contém texto licenciado; não versionar)", ""]
    for corpus in ("hatebr", "b2w"):
        itens = carregar(corpus, "ajuste")
        res = consultar(jev, corpus, itens, P.PERGUNTAS[corpus])
        print(f"\n## {corpus} ajuste n={len(itens)} status={dict((s, sum(r['status'] == s for r in res)) for s in {r['status'] for r in res})}")
        ok = [(it, r) for it, r in zip(itens, res) if r["status"] == "ok"]
        g = [it["gold"] for it, _ in ok]
        for q, spec in P.PERGUNTAS[corpus].items():
            v = [r[q] for _, r in ok]
            if spec["type"] == "noul":
                t = escolher_limiar(g, v)
                m = binario(g, [int(x >= t) for x in v], v, v)
                m5 = binario(g, [int(x >= 0.5) for x in v])
                fx = faixa(g, v, 0.2, 0.8)
                print(f"  {q}: limiar_escolhido={t} acerto={m['acerto']:.3f} macroF1={m['macroF1']:.3f} "
                      f"(0,5: {m5['acerto']:.3f}/{m5['macroF1']:.3f}) PRAUC1={m.get('PRAUC_1', 0):.3f} "
                      f"PRAUC0={m.get('PRAUC_0', 0):.3f} brier={m['brier']:.3f} faixa0,2-0,8={fx}")
                print("     acerto por limiar:", {x: round(float(np.mean([(vv >= x) == gg for vv, gg in zip(v, g)])), 3) for x in P.GRADE_LIMIAR})
                if corpus == "hatebr":
                    for est in ("unanime", "disputado"):
                        sel = [(gg, vv) for (it, _), gg, vv in zip(ok, g, v) if it["estrato"] == est]
                        print(f"     {est}: n={len(sel)} acerto@{t}={np.mean([(vv >= t) == gg for gg, vv in sel]):.3f}")
                erros = sorted([(it, x) for (it, _), x in zip(ok, v) if (x >= t) != it["gold"]], key=lambda z: -abs(z[1] - 0.5))
                linhas_local += [f"## {corpus} · {q} · limiar {t} · {len(erros)} erros", ""]
                for it, x in erros:
                    extra = f" votos={it['votos']}" if corpus == "hatebr" else f" nota={it['nota']}"
                    linhas_local.append(f"- id {it['id']} gold={it['gold']}{extra} noul={x:.2f} :: {it['texto'][:300]!r}")
                linhas_local.append("")
            else:
                notas = [it["nota"] for it, _ in ok]
                pred = [P.nota_de_score(x) for x in v]
                o = ordinal(notas, pred)
                print(f"  {q}: MAE={o['MAE']:.3f} exato={o['exato']:.3f} ±1={o['pm1']:.3f}")
                print("     score médio por nota-gabarito:", {k: round(float(np.mean([x for x, n in zip(v, notas) if n == k])), 2) for k in range(1, 6) if k in notas})
                print("     matriz (linhas=gabarito 1..5, colunas=previsto 1..5):", o["matriz"])
                linhas_local += [f"## {corpus} · {q} · erros de ≥2 níveis", ""]
                for (it, _), x, p in zip(ok, v, pred):
                    if abs(p - it["nota"]) >= 2:
                        linhas_local.append(f"- id {it['id']} nota={it['nota']} prev={p} score={x:.2f} rec={it['gold']} :: {it['texto'][:300]!r}")
                linhas_local.append("")
    (LOCAL / "ajuste-relatorio.md").write_text("\n".join(linhas_local), encoding="utf-8")
    print("\ncusto desta execução:", jev.resumo())
    print("custo acumulado do ajuste (cache):", custo_cache(LOCAL / "cache" / "ajuste"))


# ------------------------------------------------------------------------------------------ congelar
def modo_congelar() -> None:
    if CONGELAMENTO.exists() and json.loads(CONGELAMENTO.read_text(encoding="utf-8")).get("teste_executado_em"):
        raise SystemExit("o teste já rodou com este congelamento; mudança = nova versão do protocolo")
    c = {"congelado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "modelo": MODELO,
         "perguntas_py_sha256": sha_arquivo(AQUI / "perguntas.py"),
         "baselines_py_sha256": sha_arquivo(AQUI / "baselines.py"),
         "preparacao_json_sha256": sha_arquivo(AQUI / "preparacao.json"),
         "usar": P.USAR, "limiar": P.LIMIAR, "faixa": P.FAIXA}
    CONGELAMENTO.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(c, ensure_ascii=False, indent=1))


# ------------------------------------------------------------------------------------------ teste
def modo_teste() -> None:
    c = json.loads(CONGELAMENTO.read_text(encoding="utf-8"))
    for arq, chave in (("perguntas.py", "perguntas_py_sha256"), ("baselines.py", "baselines_py_sha256"),
                       ("preparacao.json", "preparacao_json_sha256")):
        if sha_arquivo(AQUI / arq) != c[chave]:
            raise SystemExit(f"{arq} mudou depois do congelamento — o teste não roda")
    primeira = not c.get("teste_executado_em")
    jev = Jev(LOCAL / "cache" / "teste", modo=None if primeira else "gravado")
    R = {"congelamento": c}
    locais = ["# Divergências do TESTE (LOCAL — texto licenciado; não versionar)", ""]

    # ---- R5
    te, aj, amplo = carregar("hatebr", "teste"), carregar("hatebr", "ajuste"), carregar("hatebr", "treino_amplo")
    qid = P.USAR["R5"][1]
    res = consultar(jev, "hatebr", te, {qid: P.PERGUNTAS["hatebr"][qid]})
    R["R5"] = avaliar_binario("R5", te, aj, amplo, res, qid, locais)
    # ---- R4
    te, aj, amplo = carregar("b2w", "teste"), carregar("b2w", "ajuste"), carregar("b2w", "treino_amplo")
    qa, qb = P.USAR["R4a"][1], P.USAR["R4b"][1]
    res = consultar(jev, "b2w", te, {qa: P.PERGUNTAS["b2w"][qa], qb: P.PERGUNTAS["b2w"][qb]})
    R["R4a"] = avaliar_binario("R4a", te, aj, amplo, res, qa, locais)
    R["R4b"] = avaliar_nota(te, aj, amplo, res, qb, locais)

    R["custo_teste"] = jev.resumo()
    R["custo_ajuste_total"] = custo_cache(LOCAL / "cache" / "ajuste")
    R["custo_teste_cache"] = custo_cache(LOCAL / "cache" / "teste")
    R["ajuste"] = resumo_ajuste()
    if primeira:
        c["teste_executado_em"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        CONGELAMENTO.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
    (LOCAL / "divergencias-teste.md").write_text("\n".join(locais), encoding="utf-8")
    (AQUI / "resultados.md").write_text(relatorio(R), encoding="utf-8")
    print(relatorio(R))


def resumo_ajuste() -> dict:
    """Métricas do AJUSTE das perguntas congeladas (do cache; nenhuma chamada nova)."""
    jev = Jev(LOCAL / "cache" / "ajuste", modo="gravado")
    out = {}
    for tarefa, (corpus, q) in P.USAR.items():
        itens = carregar(corpus, "ajuste")
        res = consultar(jev, corpus, itens, P.PERGUNTAS[corpus])
        v = [r[q] for r in res]
        if tarefa == "R4b":
            out[tarefa] = ordinal([it["nota"] for it in itens], [P.nota_de_score(x) for x in v])
        else:
            g = [it["gold"] for it in itens]
            out[tarefa] = binario(g, [int(x >= P.LIMIAR[tarefa]) for x in v], v, v)
            out[tarefa]["limiar_pela_regra"] = escolher_limiar(g, v)
    return out


def avaliar_binario(tarefa, te, aj, amplo, res, q, locais) -> dict:
    status = {s: sum(r["status"] == s for r in res) for s in ("ok", "invalida", "erro_operacional")}
    ok = [i for i, r in enumerate(res) if r["status"] == "ok"]
    itens = [te[i] for i in ok]
    g = [it["gold"] for it in itens]
    grupos = [it["grupo"] for it in itens]
    v = [res[i][q] for i in ok]
    t = P.LIMIAR[tarefa]
    pj = [int(x >= t) for x in v]
    out = {"status": status, "limiar": t, "modelos": sorted({res[i]["modelo"] for i in ok})}
    out["jev"] = binario(g, pj, v, v)
    out["jev"]["IC_macroF1"] = bootstrap(grupos, lambda idx: _mf1(g, pj, idx))
    out["jev"]["IC_acerto"] = bootstrap(grupos, lambda idx: float((np.asarray(g)[idx] == np.asarray(pj)[idx]).mean()))
    out["jev"]["IC_PRAUC_1"] = bootstrap(grupos, lambda idx: _ap(g, v, idx, 1))
    out["jev"]["IC_PRAUC_0"] = bootstrap(grupos, lambda idx: _ap(g, v, idx, 0))
    out["jev"]["IC_brier"] = bootstrap(grupos, lambda idx: float(np.mean((np.asarray(v)[idx] - np.asarray(g)[idx]) ** 2)))
    nao, sim = P.FAIXA[tarefa]
    out["faixa"] = {"nao": nao, "sim": sim, **faixa(g, v, nao, sim)}
    # Baselines (nos MESMOS itens válidos do Jev, para a comparação ser pareada)
    out["baselines"] = {}
    for nome, (prev, regime) in B.rodar_todos(aj, amplo, itens).items():
        pb = [p["pred"] for p in prev]
        m = binario(g, pb, [p["escore"] for p in prev], [p["prob"] for p in prev] if prev[0]["prob"] is not None else None)
        m["regime"] = regime
        m["IC_macroF1"] = bootstrap(grupos, lambda idx: _mf1(g, pb, idx))
        m["delta_macroF1_jev_menos_base"] = out["jev"]["macroF1"] - m["macroF1"]
        m["IC_delta_macroF1"] = bootstrap(grupos, lambda idx: _mf1(g, pj, idx) - _mf1(g, pb, idx))
        m["jev_certo_base_errado"] = sum((a == gg) and (b != gg) for a, b, gg in zip(pj, pb, g))
        m["jev_errado_base_certo"] = sum((a != gg) and (b == gg) for a, b, gg in zip(pj, pb, g))
        m["_pred"] = pb
        out["baselines"][nome] = m
    if tarefa == "R5":  # estratos unânime × disputado (votos individuais)
        out["estratos"] = {}
        for est in ("unanime", "disputado"):
            sel = [k for k, it in enumerate(itens) if it["estrato"] == est]
            gs = [g[k] for k in sel]
            linha = {"n": len(sel), "positivos": sum(gs),
                     "jev": binario(gs, [pj[k] for k in sel], [v[k] for k in sel], [v[k] for k in sel]),
                     "jev_na_faixa_de_duvida": float(np.mean([nao < v[k] < sim for k in sel])),
                     "jev_distancia_media_de_0_5": float(np.mean([abs(v[k] - 0.5) for k in sel]))}
            for nome, m in out["baselines"].items():
                linha[nome] = binario(gs, [m["_pred"][k] for k in sel])
            linha["IC_acerto_jev"] = bootstrap([grupos[k] for k in sel],
                                               lambda idx, s=sel: float(np.mean([(pj[s[j]] == g[s[j]]) for j in idx])))
            out["estratos"][est] = linha
    for m in out["baselines"].values():
        m.pop("_pred")
    # Divergências (local, com texto) — amostra fixa por semente para auditoria
    erros = [(it, x) for it, x in zip(itens, v) if int(x >= t) != it["gold"]]
    amostra = random.Random(SEMENTE).sample(erros, min(20, len(erros)))
    locais += [f"## {tarefa} · {len(erros)} erros do Jev no teste · amostra de {len(amostra)} para auditoria", ""]
    for it, x in sorted(amostra, key=lambda z: z[0]["id"]):
        extra = f" votos={it['votos']} estrato={it['estrato']}" if tarefa == "R5" else f" nota={it['nota']}"
        locais.append(f"- id {it['id']} gold={it['gold']}{extra} noul={x:.2f} :: {it['texto'][:400]!r}")
    locais.append("")
    out["erros_ids"] = sorted(it["id"] for it, _ in erros)
    out["amostra_auditoria_ids"] = sorted(it["id"] for it, _ in amostra)
    return out


def avaliar_nota(te, aj, amplo, res, q, locais) -> dict:
    status = {s: sum(r["status"] == s for r in res) for s in ("ok", "invalida", "erro_operacional")}
    ok = [i for i, r in enumerate(res) if r["status"] == "ok"]
    itens = [te[i] for i in ok]
    n = [it["nota"] for it in itens]
    grupos = [it["grupo"] for it in itens]
    pj = [P.nota_de_score(res[i][q]) for i in ok]
    out = {"status": status, "jev": ordinal(n, pj)}
    na = np.asarray(n)
    mae = lambda p: (lambda idx: float(np.abs(na[idx] - np.asarray(p)[idx]).mean()))  # noqa: E731
    exa = lambda p: (lambda idx: float((na[idx] == np.asarray(p)[idx]).mean()))  # noqa: E731
    out["jev"]["IC_MAE"] = bootstrap(grupos, mae(pj))
    out["jev"]["IC_exato"] = bootstrap(grupos, exa(pj))
    out["baselines"] = {}
    for nome, (prev, regime) in B.rodar_todos(aj, amplo, itens).items():
        pb = [p["nota"] for p in prev]
        m = ordinal(n, pb)
        m["regime"] = regime
        m["IC_MAE"] = bootstrap(grupos, mae(pb))
        m["IC_delta_MAE_jev_menos_base"] = bootstrap(grupos, lambda idx: mae(pj)(idx) - mae(pb)(idx))
        out["baselines"][nome] = m
    longe = [(it, p) for it, p in zip(itens, pj) if abs(p - it["nota"]) >= 2]
    amostra = random.Random(SEMENTE).sample(longe, min(15, len(longe)))
    locais += [f"## R4b · {len(longe)} erros de ≥2 níveis · amostra de {len(amostra)}", ""]
    for it, p in sorted(amostra, key=lambda z: z[0]["id"]):
        locais.append(f"- id {it['id']} nota={it['nota']} prev={p} rec={it['gold']} :: {it['texto'][:400]!r}")
    return out


# ------------------------------------------------------------------------------------------ relatório
def f(x, d=3):
    return "n/a" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def ic(par):
    return f"[{f(par[0])}; {f(par[1])}]"


def relatorio(R: dict) -> str:
    c = R["congelamento"]
    prep = json.loads((AQUI / "preparacao.json").read_text(encoding="utf-8"))
    aud = json.loads((AQUI / "auditoria.json").read_text(encoding="utf-8")) if (AQUI / "auditoria.json").exists() else None
    L = ["# R4/R5 — Jev em texto real em português com gabarito humano (resultados)", "",
         "**Fontes (crédito e licença):** HateBR — Vargas, Carvalho, Rodrigues de Góes, Pardo e Benevenuto, LREC 2022 "
         "(https://github.com/franciellevargas/HateBR), CC BY-NC 4.0. B2W-Reviews01 — **B2W Digital** "
         "(https://github.com/americanas-tech/b2w-reviews01), CC BY-NC-SA 4.0. Este arquivo tem só agregados, IDs e "
         "hashes; nenhum texto dos conjuntos. Gerado por `avaliar.py teste`.", "",
         f"Protocolo `PROTOCOLO.md` (sha256 `{prep['protocolo_sha256'][:16]}…`). Modelo pedido `{c['modelo']}`; "
         f"respondido {R['R5']['modelos']} / {R['R4a']['modelos']}. Semente {prep['semente']}; bootstrap {BOOT}× por grupo "
         "(post no HateBR, produto no B2W), IC 95% percentil.", "",
         "## Congelamento (antes do teste)", "",
         f"- Congelado em {c['congelado_em']}; teste executado em {c.get('teste_executado_em', 'agora')} (uma vez; relatórios seguintes saem do cache).",
         f"- `perguntas.py` sha256 `{c['perguntas_py_sha256']}` · `baselines.py` `{c['baselines_py_sha256']}` · "
         f"`preparacao.json` `{c['preparacao_json_sha256']}`.",
         f"- Perguntas usadas: {c['usar']}; limiar único {c['limiar']} (custo simétrico FP = FN = 1); faixa de dúvida {c['faixa']}; "
         "nota = arredondar(score) + 1.",
         "- Entradas ao Jev: HateBR `{comment}`; B2W `{review_title, review_text}`. Nada de estrelas, recomendação, produto, "
         "marca, categoria ou avaliador. Perguntas em inglês (texto integral em `perguntas.py`).", "",
         "## Amostras", "", "| corpus | parte | n | grupos | prevalência (classe positiva) | extra | sha256 IDs |", "|---|---|---|---|---|---|---|"]
    for corpus, cc in prep["corpora"].items():
        for parte in ("ajuste", "teste"):
            a = cc[parte]
            L.append(f"| {corpus} (arquivo `{cc['arquivo_sha256'][:12]}…`) | {parte} | {a['n']} | {a['grupos']} | {a['prevalencia_positiva']} "
                     f"({cc['classe_positiva']}) | {a.get('estratos') or a.get('notas')} | `{a['ids_sha256'][:16]}…` |")
    L += ["", "Elegíveis, exclusões e duplicatas: `preparacao.md` (publicado antes da primeira chamada). A prevalência "
          "50/50 do HateBR é a do CONJUNTO (balanceado pelos autores), não a do Instagram.", ""]

    for tarefa, titulo in (("R5", "R5 · HateBR — o comentário é ofensivo? (positivo = ofensivo)"),
                           ("R4a", "R4a · B2W — recomendaria a um amigo? (positivo = Yes)")):
        r = R[tarefa]
        j = r["jev"]
        L += [f"## {titulo}", "",
              f"Status das respostas: {r['status']} (inválida e erro operacional ficam fora e são contados aqui). "
              f"Prevalência positiva no teste {f(j['prev_1'])}.", "",
              "| sistema | regime | acerto | macro-F1 [IC] | P1 | R1 | F1₁ | P0 | R0 | F1₀ | PR-AUC₁ | PR-AUC₀ | Brier | matriz tp/fp/fn/tn |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        linhas = [("**Jev**", "zero-shot, limiar do ajuste", j)] + [(n, m["regime"], m) for n, m in r["baselines"].items()]
        for nome, reg, m in linhas:
            mm = m["matriz"]
            icm = ic(m["IC_macroF1"]) if "IC_macroF1" in m else ""
            L.append(f"| {nome} | {reg} | {f(m['acerto'])} | {f(m['macroF1'])} {icm} | {f(m['P1'])} | {f(m['R1'])} | {f(m['F1_1'])} | "
                     f"{f(m['P0'])} | {f(m['R0'])} | {f(m['F1_0'])} | {f(m.get('PRAUC_1'))} | {f(m.get('PRAUC_0'))} | "
                     f"{f(m.get('brier'))} | {mm['tp']}/{mm['fp']}/{mm['fn']}/{mm['tn']} |")
        L += ["", f"Jev: IC do acerto {ic(j['IC_acerto'])}; PR-AUC₁ {ic(j['IC_PRAUC_1'])}; PR-AUC₀ {ic(j['IC_PRAUC_0'])}; "
              f"Brier {ic(j['IC_brier'])}. PR-AUC de referência (aleatório) = prevalência da classe.", "",
              "**Comparação pareada** (mesmos itens; Δ = Jev − baseline; IC por bootstrap pareado por grupo):", "",
              "| baseline | regime | Δ macro-F1 [IC] | Jev certo / base errado | Jev errado / base certo |", "|---|---|---|---|---|"]
        for nome, m in r["baselines"].items():
            L.append(f"| {nome} | {m['regime']} | {f(m['delta_macroF1_jev_menos_base'])} {ic(m['IC_delta_macroF1'])} | "
                     f"{m['jev_certo_base_errado']} | {m['jev_errado_base_certo']} |")
        fx = r["faixa"]
        L += ["", f"**Faixa de dúvida** (não ≤ {fx['nao']}, sim ≥ {fx['sim']}, meio → humano): cobertura {f(fx['cobertura'])}, "
              f"acerto nos decididos {f(fx['acerto_decididos'])} ({fx['erros_decididos']} erros), {fx['revisao']} à revisão; "
              f"no conjunto todo (limiar único) acerto {f(j['acerto'])}.", ""]
        if tarefa == "R5":
            L += ["**Estratos** (votos individuais; concordância entre anotadores = referência de ambiguidade, não teto):", "",
                  "| estrato | n | ofensivos | Jev acerto [IC] | Jev macro-F1 | Jev Brier | Jev na faixa de dúvida | |noul − 0,5| médio | "
                  + " | ".join(f"{n} acerto" for n in r["baselines"]) + " |",
                  "|---|---|---|---|---|---|---|---|" + "---|" * len(r["baselines"])]
            for est, e in r["estratos"].items():
                L.append(f"| {est} | {e['n']} | {e['positivos']} | {f(e['jev']['acerto'])} {ic(e['IC_acerto_jev'])} | {f(e['jev']['macroF1'])} | "
                         f"{f(e['jev'].get('brier'))} | {f(e['jev_na_faixa_de_duvida'])} | {f(e['jev_distancia_media_de_0_5'])} | "
                         + " | ".join(f(e[n]['acerto']) for n in r["baselines"]) + " |")
            L.append("")
        L += [f"Erros do Jev no teste (IDs): {r['erros_ids']}", ""]
        if aud and tarefa in aud:
            L += [f"**Auditoria das divergências** (amostra de {len(r['amostra_auditoria_ids'])} por semente; texto lido só localmente):", ""]
            cont = {}
            for cat in aud[tarefa].values():
                cont[cat] = cont.get(cat, 0) + 1
            for cat, k in sorted(cont.items(), key=lambda z: -z[1]):
                ids = [i for i, cc in aud[tarefa].items() if cc == cat]
                L.append(f"- {cat}: {k} (IDs {', '.join(ids)})")
            L.append("")

    r = R["R4b"]
    j = r["jev"]
    L += ["## R4b · B2W — nota geral 1–5 (Score de 5 situações → arredondar + 1)", "",
          f"Status: {r['status']}.", "", "| sistema | regime | MAE [IC] | exato | ±1 | Δ MAE Jev − base [IC] |", "|---|---|---|---|---|---|",
          f"| **Jev** | zero-shot | {f(j['MAE'])} {ic(j['IC_MAE'])} | {f(j['exato'])} {ic(j['IC_exato'])} | {f(j['pm1'])} | |"]
    for nome, m in r["baselines"].items():
        L.append(f"| {nome} | {m['regime']} | {f(m['MAE'])} {ic(m['IC_MAE'])} | {f(m['exato'])} | {f(m['pm1'])} | {ic(m['IC_delta_MAE_jev_menos_base'])} |")
    L += ["", "Matriz 5×5 do Jev (linha = nota real 1..5, coluna = prevista 1..5):", "", "| real \\ prevista | 1 | 2 | 3 | 4 | 5 |", "|---|---|---|---|---|---|"]
    for i, row in enumerate(j["matriz"], 1):
        L.append(f"| {i} | " + " | ".join(str(x) for x in row) + " |")
    L.append("")
    if aud and "R4b" in aud:
        cont = {}
        for cat in aud["R4b"].values():
            cont[cat] = cont.get(cat, 0) + 1
        L += ["**Auditoria (erros de ≥ 2 níveis, amostra):** " + "; ".join(f"{k}: {v}" for k, v in sorted(cont.items(), key=lambda z: -z[1])), ""]

    A = R["ajuste"]
    L += ["## Ajuste (100 por corpus) das perguntas congeladas — referência, não resultado", "",
          f"- R5: acerto {f(A['R5']['acerto'])}, macro-F1 {f(A['R5']['macroF1'])}, Brier {f(A['R5']['brier'])}, limiar pela regra {A['R5']['limiar_pela_regra']}.",
          f"- R4a: acerto {f(A['R4a']['acerto'])}, macro-F1 {f(A['R4a']['macroF1'])}, Brier {f(A['R4a']['brier'])}, limiar pela regra {A['R4a']['limiar_pela_regra']}.",
          f"- R4b: MAE {f(A['R4b']['MAE'])}, exato {f(A['R4b']['exato'])}, ±1 {f(A['R4b']['pm1'])}.", ""]
    ct, ca, cte = R["custo_teste"], R["custo_ajuste_total"], R["custo_teste_cache"]
    L += ["## Custo, latência, tokens", "",
          f"- Teste: {cte['requisicoes']} requisições, {cte['input_tokens']} tokens de entrada, US$ {cte['custo_us']}; "
          f"latência p50 {ct.get('latencia_p50_ms')} ms, p95 {ct.get('latencia_p95_ms')} ms (medida na chamada real, 8 em paralelo); modelos {ct.get('modelos')}.",
          f"- Ajuste (todas as versões e variantes, inclusive as descartadas): {ca['requisicoes']} requisições, {ca['input_tokens']} tokens, US$ {ca['custo_us']}.",
          f"- Total gasto: US$ {round(ca['custo_us'] + cte['custo_us'], 5)} (teto publicado antes: US$ {prep['custo_max_total_us']}). Preço US$ {PRECO_US_POR_MILHAO_ENTRADA}/M de entrada.", ""]
    L += ["## O que isto NÃO mostra", "",
          "- n = 300 por tarefa: exploratório; não prova taxa de erro rara. HateBR com 34 posts no teste: o IC por post é largo de propósito.",
          "- HateBR 50/50 é prevalência do conjunto (balanceado), não do Instagram; precisão em tráfego real (ofensa rara) seria menor.",
          "- Uma versão do modelo (`jev-1.13.0`), uma rodada; ruído entre chamadas idênticas medido em ~0,01 (máx. 0,15) — itens perto do limiar podem trocar de lado.",
          "- Baseline LLM real não entrou (sem autorização para outro provedor). `tfidf_lr_amplo` é OUTRO regime (milhares de rótulos), não comparável ao zero-shot.",
          "- Nunca misturar R4 com R5 numa média."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else ""
    {"ajuste": modo_ajuste, "congelar": modo_congelar, "teste": modo_teste}.get(
        modo, lambda: sys.exit("uso: avaliar.py ajuste|congelar|teste"))()
