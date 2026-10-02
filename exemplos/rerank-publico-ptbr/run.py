"""Roda o rerank nas consultas sorteadas do Quati e gera `resultados.md` sozinho.

Uso (precisa do subconjunto em .local/, gerado por `preparar.py`; o texto do corpus nunca entra no Git):
  python run.py ajuste       afinação (10 consultas; variantes em inglês, português e lote)
  python run.py rascunho     só o encanamento: 1 consulta do ajuste, por trecho → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, rerank.py,
                             bm25.py, run.py, dados/teste.json e o critério); o anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste; o teste só roda com o manifesto batendo. A PRIMEIRA execução com teste
                             grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache (.local/publicos/rerank/cache-jev/), sem chave
Métricas: NDCG@10 graduado (ganho 2^nota − 1, ideal pelo gabarito INTEIRO da consulta) e MRR@10 com relevante = nota ≥ 2
("responde"); intervalo de 95% por bootstrap sobre as consultas (1.000 reamostras, semente fixa), pareado para o Δ.
Falha operacional numa consulta → ordem do BM25 (`rerank.reordenar_seguro`), contada à parte; conjunto com falha
não é medição do Jev.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import random
import shutil
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI.parent / "_comum"))
sys.path.insert(0, str(AQUI))

import bm25 as B  # noqa: E402
import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
import rerank as R  # noqa: E402
from jevcache import Jev  # noqa: E402

LOCAL = RAIZ / ".local" / "publicos"
CACHE = LOCAL / "rerank" / "cache-jev"          # contém os trechos: fora do Git
SUBCONJUNTO = LOCAL / "quati" / "quati_1M.subconjunto.jsonl"
CONSULTAS = LOCAL / "rerank" / "consultas.json"
RESULTADOS, RODADA1 = AQUI / "resultados.md", AQUI / "resultados-rodada1.md"
CONGELADOS = ["perguntas.py", "rerank.py", "bm25.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py", "../_comum/metricas.py", "preparacao.json"]
K, REL_MIN = 10, 2                 # NDCG@10, MRR@10; relevante binário = nota ≥ 2 (responde)
SEMENTE_BOOT, N_BOOT = 20261001, 1000
PARALELO = 8
VARIANTES = {"ajuste": ["bm25", "sobreposicao", "jev", "jev_pt", "jev_lote", "teto"],
             "teste": ["bm25", "sobreposicao", "jev", "jev_lote", "teto"],
             "rascunho": ["bm25", "sobreposicao", "jev", "teto"]}
COM_JEV = {"jev", "jev_pt", "jev_lote"}
PRECO = 0.042  # US$ por milhão de tokens de entrada


# ------------------------------------------------------------------------------------------ dados
def textos() -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    if not SUBCONJUNTO.exists() or not CONSULTAS.exists():
        sys.exit("falta o subconjunto em .local/publicos/ — rode `preparar.py` (download do Quati) antes")
    passagens = {}
    with SUBCONJUNTO.open(encoding="utf-8") as f:
        for linha in f:
            p = json.loads(linha)
            passagens[p["id"]] = p["texto"]
    return passagens, json.loads(CONSULTAS.read_text(encoding="utf-8"))


def carregar(parte: str) -> list[dict]:
    """Consultas de `dados/<parte>.json` (IDs, notas, BM25) com os textos de .local/ anexados."""
    passagens, consultas = textos()
    arquivo = "ajuste" if parte == "rascunho" else parte
    dados = json.loads((AQUI / "dados" / f"{arquivo}.json").read_text(encoding="utf-8"))
    saida = []
    for c in dados["consultas"]:
        q = str(c["query_id"])
        saida.append({**c, "texto": consultas[arquivo][q], "trechos": [passagens[t["id"]] for t in c["top"]],
                      "bm25": [t["bm25"] for t in c["top"]], "notas": [t["nota"] for t in c["top"]]})
    return saida[:1] if parte == "rascunho" else saida


def hash_textos(consultas: list[dict]) -> str:
    """sha256 dos textos EFETIVAMENTE consumidos (consulta + trechos do top-20, na ordem, por ID). Entra no manifesto:
    consulta ou passagem trocada em .local/ com o mesmo ID já não passa como a rodada congelada (revisão do Codex,
    2026-10-01). Só o hash vai ao Git; o conteúdo fica fora."""
    corpo = [{"q": c["query_id"], "consulta": c["texto"], "trechos": [[t["id"], x] for t, x in zip(c["top"], c["trechos"])]} for c in consultas]
    return hashlib.sha256(json.dumps(corpo, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


# ------------------------------------------------------------------------------------------ métricas
def ndcg(ordem: list[int], c: dict) -> float:
    notas = [float(c["notas"][i] or 0) for i in ordem]           # não julgada = 0 (lacuna do gabarito, declarada)
    return M.ndcg(notas, K, [float(n) for n in c["gabarito"].values()])


def mrr(ordem: list[int], c: dict) -> float:
    for pos, i in enumerate(ordem[:K], start=1):
        if (c["notas"][i] or 0) >= REL_MIN:
            return 1.0 / pos
    return 0.0


def primeiro_relevante(ordem: list[int], c: dict) -> int | None:
    for pos, i in enumerate(ordem, start=1):
        if (c["notas"][i] or 0) >= REL_MIN:
            return pos
    return None


def bootstrap(por_consulta: dict[str, list[float]], ref: str = "bm25") -> dict:
    """Média e intervalo de 95% por variante, e Δ pareado (variante − ref), sobre as consultas."""
    n = len(next(iter(por_consulta.values())))
    rng = random.Random(SEMENTE_BOOT)
    amostras = {v: [] for v in por_consulta}
    deltas = {v: [] for v in por_consulta}
    for _ in range(N_BOOT):
        idx = [rng.randrange(n) for _ in range(n)]
        for v, vals in por_consulta.items():
            m = sum(vals[i] for i in idx) / n
            amostras[v].append(m)
            deltas[v].append(m - sum(por_consulta[ref][i] for i in idx) / n)

    def ic(xs):
        s = sorted(xs)
        return s[int(0.025 * len(s))], s[min(len(s) - 1, int(0.975 * len(s)))]

    return {v: {"media": sum(vals) / n, "ic": ic(amostras[v]),
                "delta": sum(vals) / n - sum(por_consulta[ref]) / n, "delta_ic": ic(deltas[v])} for v, vals in por_consulta.items()}


def latencia_consulta(ms: list[int], vagas: int = PARALELO) -> int:
    """Fila de `vagas` com os ms medidos de cada requisição (como o busca-imoveis)."""
    fila = [0] * vagas
    for m in ms:
        i = fila.index(min(fila))
        fila[i] += m
    return max(fila) if ms else 0


# ------------------------------------------------------------------------------------------ execução
def rodar_variante(variante: str, consultas: list[dict]) -> tuple[list[dict], dict]:
    """Uma saída por consulta: {ordem, probs, falha, ms}; custo do Jev da variante (instância própria)."""
    if variante == "bm25":
        return [{"ordem": list(range(len(c["top"]))), "probs": None, "falha": None, "ms": 0} for c in consultas], {}
    if variante == "teto":
        return [{"ordem": sorted(range(len(c["top"])), key=lambda i, c=c: (-(c["notas"][i] or 0), i)), "probs": None,
                 "falha": None, "ms": 0} for c in consultas], {}
    if variante == "sobreposicao":
        saidas = []
        for c in consultas:
            s = [B.sobreposicao(c["texto"], t) for t in c["trechos"]]
            saidas.append({"ordem": R.ordenar(s, c["bm25"]), "probs": s, "falha": None, "ms": 0})
        return saidas, {}
    jev = Jev(CACHE)
    if variante == "jev_lote":
        def um(c):
            return R.reordenar_seguro(jev, c["texto"], c["trechos"], c["bm25"], modo="lote")
        with ThreadPoolExecutor(PARALELO) as ex:
            saidas = list(ex.map(um, consultas))
        # uma requisição por consulta: a latência da consulta é a da requisição (ordem de conclusão ≠ de consulta,
        # por isso só o p50/p95 por requisição é relatado para o lote)
        for s in saidas:
            s["ms"] = None
    else:
        pergunta = P.PERGUNTA_PT if variante == "jev_pt" else P.PERGUNTA_EN
        saidas = []
        for c in consultas:
            antes = len(jev.chamadas)
            s = R.reordenar_seguro(jev, c["texto"], c["trechos"], c["bm25"], modo="trecho", pergunta=pergunta)
            s["ms"] = latencia_consulta([ch["ms"] for ch in jev.chamadas[antes:]])
            saidas.append(s)
    custo = jev.resumo() or {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
                             "input_tokens": 0, "custo_us": 0.0, "modelos": []}
    custo["falhas"] = sum(s["falha"] is not None for s in saidas)
    return saidas, custo


def veredito(res: dict, custos: dict, n: int) -> str:
    lim = P.CRITERIO_CONTINUAR["limites"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    j = res["ndcg"]["jev"]
    c = custos["jev"]
    por_mil = 1000 * c["custo_us"] / n if n else float("nan")
    linhas = [
        {"critério": "1 ganho NDCG@10 (Jev − BM25)", "medido": f"Δ {j['delta']:+.3f} [{j['delta_ic'][0]:+.3f}; {j['delta_ic'][1]:+.3f}]",
         "limite": f"Δ ≥ {lim['ganho_ndcg_min']} e IC > 0", "passa": ok(j["delta"] >= lim["ganho_ndcg_min"] and j["delta_ic"][0] > 0)},
        {"critério": "2 custo por mil consultas", "medido": f"US$ {por_mil:.3f}", "limite": f"≤ US$ {lim['custo_por_mil_max_us']}",
         "passa": ok(por_mil <= lim["custo_por_mil_max_us"])},
        {"critério": "3 p95 por requisição", "medido": f"{c['latencia_p95_ms']} ms", "limite": f"≤ {lim['p95_ms_max']} ms",
         "passa": ok(c["latencia_p95_ms"] <= lim["p95_ms_max"])},
        {"critério": "secundário: Δ MRR@10 com IC > 0", "medido": f"Δ {res['mrr']['jev']['delta']:+.3f} [{res['mrr']['jev']['delta_ic'][0]:+.3f}; {res['mrr']['jev']['delta_ic'][1]:+.3f}]",
         "limite": "IC > 0", "passa": ok(res["mrr"]["jev"]["delta_ic"][0] > 0)},
        {"critério": "secundário: Jev ≥ sobreposição (NDCG@10)", "medido": f"{j['media']:.3f} × {res['ndcg']['sobreposicao']['media']:.3f}",
         "limite": "≥", "passa": ok(j["media"] >= res["ndcg"]["sobreposicao"]["media"])},
    ]
    if custos["jev"]["falhas"]:
        linhas.append({"critério": "falhas operacionais", "medido": str(custos["jev"]["falhas"]), "limite": "0 (senão não é medição)", "passa": "✗"})
    return M.tabela(linhas)


def secao_conjunto(parte: str) -> tuple[str, dict]:
    consultas = carregar(parte)
    variantes = VARIANTES[parte]
    saidas, custos = {}, {}
    for v in variantes:
        saidas[v], custos[v] = rodar_variante(v, consultas)
    n = len(consultas)
    por = {"ndcg": {v: [ndcg(s["ordem"], c) for s, c in zip(saidas[v], consultas)] for v in variantes},
           "mrr": {v: [mrr(s["ordem"], c) for s, c in zip(saidas[v], consultas)] for v in variantes}}
    res = {m: bootstrap(por[m]) for m in por}
    sem_rel = [c["query_id"] for c in consultas if not any((x or 0) >= REL_MIN for x in c["notas"])]
    nao_julg = sum(1 for c in consultas for x in c["notas"] if x is None)
    ausentes = sum(len(c.get("ausentes_da_colecao", [])) for c in consultas)
    resumo = {"n": n, "res": res, "custos": custos, "sem_relevante_top20": sem_rel, "nao_julgadas": nao_julg, "ausentes": ausentes}

    out = [f"## Conjunto `{parte}` — {n} consultas × {len(consultas[0]['top'])} trechos do BM25 (Quati 1M, semente da preparação "
           f"{json.loads((AQUI / 'preparacao.json').read_text(encoding='utf-8'))['semente']})\n"]
    if parte == "rascunho":
        out.append("> Rascunho: 1 consulta do ajuste, só o encanamento. **Não é métrica.**\n")
    falhas = {v: c["falhas"] for v, c in custos.items() if c and c["falhas"]}
    if falhas:
        out.append(f"> **Falhas operacionais** {falhas}: essas consultas saíram na ordem do BM25 sem resposta do Jev. "
                   "**As métricas da variante não são medição do Jev** — rode de novo.\n")
    out.append(f"Teto do rerank: **{len(sem_rel)}** consulta(s) sem nenhum trecho com nota ≥ {REL_MIN} no top-20 "
               f"({sem_rel or '—'}) — nelas nenhuma reordenação muda o MRR; `teto` = top-20 na ordem do gabarito. "
               f"Trechos não julgados no top-20: {nao_julg}/{n * len(consultas[0]['top'])} (contam como nota 0). Julgamentos cuja "
               f"passagem não está na coleção: {ausentes} (ficam no ideal do NDCG).\n")

    # --- lado a lado
    out.append("### Qualidade do ranking — média sobre as consultas, intervalo de 95% por bootstrap "
               f"({N_BOOT} reamostras, semente {SEMENTE_BOOT}); Δ pareado contra `bm25`\n")
    linhas = []
    for v in variantes:
        a, b = res["ndcg"][v], res["mrr"][v]
        linhas.append({"variante": v, "NDCG@10": f"{a['media']:.3f} [{a['ic'][0]:.3f}; {a['ic'][1]:.3f}]",
                       "Δ NDCG@10 vs bm25": "—" if v == "bm25" else f"{a['delta']:+.3f} [{a['delta_ic'][0]:+.3f}; {a['delta_ic'][1]:+.3f}]",
                       f"MRR@10 (nota ≥ {REL_MIN})": f"{b['media']:.3f} [{b['ic'][0]:.3f}; {b['ic'][1]:.3f}]",
                       "Δ MRR@10 vs bm25": "—" if v == "bm25" else f"{b['delta']:+.3f} [{b['delta_ic'][0]:+.3f}; {b['delta_ic'][1]:+.3f}]",
                       "1º relevante no top-10": sum(1 for s, c in zip(saidas[v], consultas) if (primeiro_relevante(s["ordem"], c) or 99) <= K),
                       "ganhou · empatou · perdeu (NDCG vs bm25)": "—" if v == "bm25" else " · ".join(str(sum(
                           1 for x, y in zip(por["ndcg"][v], por["ndcg"]["bm25"]) if f(x, y))) for f in
                           (lambda x, y: x > y + 1e-9, lambda x, y: abs(x - y) <= 1e-9, lambda x, y: x < y - 1e-9))})
    out.append(M.tabela(linhas) + "\n")
    if parte != "rascunho":
        out.append("**Critério congelado conferido no teste** (é este que decide)\n" if parte == "teste"
                   else f"**Critério conferido no `{parte}`** (informativo: só o `teste` decide)\n")
        out.append(veredito(res, custos, n) + "\n")

    # --- Jev × gabarito
    out.append("### Noul × nota do gabarito (todos os trechos julgados pelo Jev)\n")
    out.append(f"Média de P(responde) por nota; `acerto ≥ 0,5` compara P ≥ 0,5 com nota ≥ {REL_MIN} (só trechos julgados); "
               "Brier contra o mesmo binário. Nota `—` = não julgado pelo gabarito.\n")
    linhas = []
    for v in [x for x in variantes if x in COM_JEV]:
        pares = [(p, nota) for s, c in zip(saidas[v], consultas) if s["probs"] for p, nota in zip(s["probs"], c["notas"])]
        por_nota = {}
        for nota in (None, 0, 1, 2, 3):
            xs = [p for p, nt in pares if nt == nota]
            por_nota[nota] = f"{statistics.mean(xs):.2f} (n={len(xs)})" if xs else "—"
        julg = [(p, nt >= REL_MIN) for p, nt in pares if nt is not None]
        linhas.append({"variante": v, "nota —": por_nota[None], "nota 0": por_nota[0], "nota 1": por_nota[1], "nota 2": por_nota[2],
                       "nota 3": por_nota[3], "acerto ≥ 0,5": M.acerto([(p >= 0.5, g) for p, g in julg]), "brier": M.brier(julg),
                       "n julgados": len(julg)})
    resumo["noul"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    linhas = []
    for v in [x for x in variantes if x in COM_JEV]:
        c = custos[v]
        req = max(c["requisicoes"], 1)
        ms = [s["ms"] for s in saidas[v] if s["ms"] is not None]
        linhas.append({"variante": v, "requisições (do cache)": f"{c['requisicoes']} ({c['do_cache']})", "falhas (→ ordem do BM25)": c["falhas"],
                       "req/consulta": round(c["requisicoes"] / n, 1), "tokens/consulta": round(c["input_tokens"] / n),
                       "US$/1000 consultas": f"{1000 * c['custo_us'] / n:.4f}",
                       "p50/p95 por requisição (ms)": f"{c['latencia_p50_ms']} / {c['latencia_p95_ms']}",
                       f"p50/p95 por consulta (ms, {PARALELO} vagas)": f"{round(statistics.median(ms))} / {sorted(ms)[min(len(ms) - 1, int(0.95 * len(ms)))]}" if ms else "= por requisição",
                       "modelo": ", ".join(c["modelos"])})
    out.append(M.tabela(linhas) + "\n")

    # --- por consulta
    out.append("### Por consulta\n")
    out.append(f"`rel` = trechos com nota ≥ {REL_MIN} (gabarito inteiro / no top-20); `n/j` = não julgados no top-20; "
               "`1º rel` = posição do primeiro relevante (bm25 → jev); `P máx` = maior P(responde) da consulta.\n")
    linhas = []
    for i, c in enumerate(consultas):
        rel_g = sum(1 for x in c["gabarito"].values() if x >= REL_MIN)
        rel_t = sum(1 for x in c["notas"] if (x or 0) >= REL_MIN)
        pj = saidas["jev"][i]["probs"]
        linha = {"consulta": c["query_id"], "rel": f"{rel_g} / {rel_t}", "n/j": sum(1 for x in c["notas"] if x is None)}
        for v in variantes:
            linha[f"NDCG {v}"] = por["ndcg"][v][i]
        linha["MRR bm25 → jev"] = f"{por['mrr']['bm25'][i]:.2f} → {por['mrr']['jev'][i]:.2f}"
        linha["1º rel"] = f"{primeiro_relevante(saidas['bm25'][i]['ordem'], c) or '—'} → {primeiro_relevante(saidas['jev'][i]['ordem'], c) or '—'}"
        linha["P máx"] = f"{max(pj):.2f}" if pj else "—"
        linha["ms"] = saidas["jev"][i]["ms"]
        linha["falha"] = saidas["jev"][i]["falha"] or ""
        linhas.append(linha)
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n"]
    linhas = []
    for parte, r in resumos.items():
        for v, a in r["res"]["ndcg"].items():
            b = r["res"]["mrr"][v]
            c = r["custos"].get(v) or {}
            linhas.append({"conjunto": parte, "variante": v, "n": r["n"],
                           "NDCG@10 [IC]": f"{a['media']:.3f} [{a['ic'][0]:.3f}; {a['ic'][1]:.3f}]",
                           "Δ NDCG vs bm25 [IC]": "—" if v == "bm25" else f"{a['delta']:+.3f} [{a['delta_ic'][0]:+.3f}; {a['delta_ic'][1]:+.3f}]",
                           "MRR@10 [IC]": f"{b['media']:.3f} [{b['ic'][0]:.3f}; {b['ic'][1]:.3f}]",
                           "Δ MRR vs bm25 [IC]": "—" if v == "bm25" else f"{b['delta']:+.3f} [{b['delta_ic'][0]:+.3f}; {b['delta_ic'][1]:+.3f}]",
                           "req": c.get("requisicoes", ""), "US$/1000": f"{1000 * c['custo_us'] / r['n']:.4f}" if c else "",
                           "p50/p95 req (ms)": f"{c['latencia_p50_ms']} / {c['latencia_p95_ms']}" if c else "",
                           "falhas": c.get("falhas", "") if c else ""})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}): {h}"


def _congelar() -> dict:
    """Manifesto da infra comum + hash dos textos consumidos no teste. Textos diferentes dos congelados = manifesto novo
    (o antigo vai para congelamentos-anteriores/), mesmo que nenhum arquivo do Git tenha mudado."""
    textos = {"teste": hash_textos(carregar("teste"))}
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if m.get("textos_consumidos") != textos:
        if "textos_consumidos" in m:
            guarda = AQUI / "congelamentos-anteriores"
            guarda.mkdir(exist_ok=True)
            shutil.move(str(AQUI / CG.MANIFESTO), str(guarda / f"{m['congelado_em'].replace(':', '-')}.json"))
            m["congelado_em"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        m["textos_consumidos"] = textos
    m["informativo"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if "teste" in conjuntos:
        try:
            manifesto = CG.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != P.CRITERIO_CONTINUAR:
            sys.exit("teste recusado: o critério mudou desde o congelamento (rode `run.py congelar`)")
        atual = hash_textos(carregar("teste"))
        if manifesto.get("textos_consumidos", {}).get("teste") != atual:
            sys.exit("teste recusado: os textos consumidos (consultas e trechos do top-20 em .local/) não são os congelados (rode `run.py congelar`)")
        linha = _linha_manifesto(manifesto) + f" · textos consumidos no teste sha256 {atual[:16]}…"
        if RODADA1.exists():
            linha += ("\n\n> **Rodada 2 ou posterior (pós-revisão, NÃO cega).** A rodada cega está preservada em "
                      "`resultados-rodada1.md`; este arquivo é regerado do cache.")
    elif congelar:
        linha = _linha_manifesto(_congelar())
    else:
        h = CG.hashes(AQUI, CONGELADOS)
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())
    prep = json.loads((AQUI / "preparacao.json").read_text(encoding="utf-8"))
    cabecalho = (f"# Resultados — rerank-publico-ptbr\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`). Corpus: Quati 1M (unicamp-dl/quati, CC BY 4.0; Bueno et al., 2024), "
                 f"subconjunto de {prep['colecao']['passagens']} passagens ({prep['colecao']['julgadas']} julgadas + "
                 f"{prep['colecao']['distratores']} distratores), BM25 próprio k1 = {B.K1}, b = {B.B}. Gabarito: notas 0–3 do Quati "
                 f"(GPT-4; kappa 0,31 com humanos [artigo]); relevante binário = nota ≥ {REL_MIN}. Perguntas e critério: `perguntas.py`; "
                 f"ordenação e política segura: `rerank.py`. Preço: US$ {PRECO} por milhão de tokens de entrada.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): "
                 + "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_CONTINUAR.items() if k != "limites") + f"\n\n{linha}\n")
    if args == ["rascunho"]:
        texto, _ = secao_conjunto("rascunho")
        (AQUI / "resultados-rascunho.md").write_text(cabecalho + "\n" + texto, encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return
    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome)
        partes.append(texto)
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: {v: c["falhas"] for v, c in r["custos"].items() if c and c["falhas"]} for n, r in resumos.items()}
    falhas = {n: f for n, f in falhas.items() if f}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — consultas na ordem do BM25 sem resposta do Jev; não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists():
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
