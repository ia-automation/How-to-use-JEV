"""Roda o compactação-de-contexto num conjunto rotulado de sessões e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 sessões fáceis; não é métrica) → resultados-rascunho.md
  python run.py variantes    no ajuste: state `dict` × `list` → resultados-variantes.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py,
                             compactacao.py, run.py, dados/teste.json e o critério; hash de _comum/ só como registro)
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA
                             execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por sessão. Falha operacional (chamada, cache faltando, resposta fora do contrato, sessão inválida)
NÃO aborta o lote NEM o relatório: aquela sessão sai com TUDO mantido por `compactacao.julgar_seguro` e é contada
à parte — conjunto com falha não é medição do Jev. O cache em `cache/` faz rodar de novo custar zero.
Bateria do código: `testa_falhas.py`.
"""
from __future__ import annotations

import contextlib
import datetime
import json
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import compactacao as C  # noqa: E402
import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
CONGELADOS = ["perguntas.py", "compactacao.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py", "../_comum/metricas.py"]
B_USU, B_ULT, B_PAL = "baseline: papel = usuario", "baseline: últimas N", "baseline: palavras da tarefa"
TUDO, SO_NEEDED, JEV = "manter tudo", "só needed (≥ 0,5)", "Jev (política)"
BASES = {B_USU: "usuario", B_ULT: "ultimas", B_PAL: "palavras"}
VARIANTES = [B_USU, B_ULT, B_PAL, TUDO, SO_NEEDED, JEV]
PAPEIS = ["usuario", "assistente", "ferramenta"]
CARO = "NECESSÁRIA DESCARTADA"
GRADE_FAIXA = [(0.5, 0.5), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9)]
GRADE_SIM = [0.5, 0.6, 0.7, 0.8, 0.9, 1.01]      # 1.01 = guarda/veto desligados
GRADE_N = [2, 4, 6, 8, 10, 12]
GRADE_K = [1, 2, 3]
TAMANHOS = [(12, 13), (14, 16), (17, 25)]
COLUNAS = ["variante", "mensagens", "acerto", "precisão manter", "cobertura manter", f"{CARO} (gab. manter → descartar)",
           "manter demais (gab. descartar → manter)", "necessária descartada: usuario"]
CUSTO_ZERO = {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
              "input_tokens": 0, "custo_us": 0.0, "modelos": []}


def familia(c: dict) -> str:
    """Família pela `nota` do rotulador ("difícil: <família> — detalhe"); sem família = "fácil"."""
    nota = c.get("nota") or ""
    if not nota.startswith("difícil:"):
        return "fácil"
    corpo = nota[len("difícil:"):].strip()
    for sep in (" — ", " – ", ": "):
        if sep in corpo:
            corpo = corpo.split(sep, 1)[0]
    return corpo.strip()


def gabarito(c: dict) -> dict[str, str | None]:
    """{id: manter | descartar | None (discutível, fora da métrica)}."""
    k, d = set(c.get("manter") or []), set(c.get("descartar") or [])
    return {m["id"]: "manter" if m["id"] in k else "descartar" if m["id"] in d else None for m in c["mensagens"]}


def sessao_invalida(c) -> str | None:
    """Motivo se a sessão NÃO pode entrar na métrica: o que `compactacao.preparar` recusa (sem `id`, papel fora do
    vocabulário, `mensagens` não lista, texto vazio…) ou gabarito que não é lista / cita ID inexistente. Antes, uma
    mensagem sem `id` passava pelo julgamento (falha fechada) mas derrubava `gabarito()` e o relatório inteiro
    (revisão do Codex, 2026-10-01): agora essas sessões são separadas ANTES das métricas e contadas como falha."""
    try:
        C.preparar(c)
    except ValueError as e:
        return str(e)
    ids = {m["id"] for m in c["mensagens"]}
    for campo in ("manter", "descartar"):
        lista = c.get(campo) or []
        if not isinstance(lista, list) or not all(isinstance(i, str) and i in ids for i in lista):
            return f"`{campo}` não é lista ou cita ID inexistente"
    return None


def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    """Uma sessão por vez pelo mesmo invólucro que o consumidor usa (`julgar_seguro`): falha operacional mantém
    tudo SÓ naquela sessão. Tudo contado à parte."""
    jev = Jev(AQUI / "cache")
    with ThreadPoolExecutor(8) as ex:
        saidas = list(ex.map(lambda c: C.julgar_seguro(jev, c), casos))
    custo = jev.resumo() or dict(CUSTO_ZERO)
    for origem in ("longo", "falha"):
        custo[origem] = sum(s["origem"] == origem for s in saidas)
    return saidas, custo


def decisoes_variante(s: dict, c: dict, variante: str) -> dict[str, str]:
    """{id: decisão} de cada variante sobre a MESMA sessão. `só needed` = `needed` ≥ 0,5, sem guarda nem dúvida
    (o que saiu por falha ou faixa vale igual nas duas variantes do Jev: tudo mantido)."""
    if variante in BASES:
        return C.baselines_seguro(c)[BASES[variante]]
    ids = [m["id"] for m in c["mensagens"]]
    if variante == TUDO:
        return {i: "manter" for i in ids}
    if variante == SO_NEEDED and s["origem"] == "jev":
        return {i: "manter" if s["por_mensagem"][i]["needed"] >= 0.5 else "descartar" for i in ids}
    return {i: ("manter" if i in s["manter"] else "descartar") for i in ids}


def itens_de(saidas, casos, variante) -> list[tuple]:
    """[(previsto, gabarito, mensagem, caso)] de uma variante, todas as mensagens (gabarito None = discutível)."""
    out = []
    for s, c in zip(saidas, casos):
        d, g = decisoes_variante(s, c, variante), gabarito(c)
        out += [(d[m["id"]], g[m["id"]], m, c) for m in c["mensagens"]]
    return out


def metricas(itens: list[tuple]) -> dict:
    """Acerto por mensagem, precisão/cobertura de `manter`, erro caro (necessária descartada) e manter demais."""
    val = [(p, g, m) for p, g, m, _ in itens if g is not None]
    tp = sum(p == "manter" and g == "manter" for p, g, _ in val)
    fp = sum(p == "manter" and g == "descartar" for p, g, _ in val)
    fn = sum(p == "descartar" and g == "manter" for p, g, _ in val)
    fn_usu = sum(p == "descartar" and g == "manter" and m["papel"] == "usuario" for p, g, m in val)
    nk = sum(g == "manter" for _, g, _ in val)
    nd = sum(g == "descartar" for _, g, _ in val)
    b = {"acerto": M.acerto([(p, g) for p, g, _ in val]), "precisao": tp / (tp + fp) if tp + fp else float("nan"),
         "cobertura": tp / nk if nk else float("nan"), "fn": fn, "fp": fp, "nk": nk, "nd": nd, "fn_usu": fn_usu,
         "nk_usu": sum(g == "manter" and m["papel"] == "usuario" for _, g, m in val), "n": len(val)}
    return {"mensagens": len(val), "acerto": b["acerto"], "precisão manter": b["precisao"], "cobertura manter": b["cobertura"],
            f"{CARO} (gab. manter → descartar)": f"{fn}/{nk}", "manter demais (gab. descartar → manter)": f"{fp}/{nd}",
            "necessária descartada: usuario": f"{fn_usu}/{b['nk_usu']}", "_bruto": b}


def veredito(variantes: dict) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    if not P.CRITERIO_CONTINUAR:
        return "_(critério ainda não fixado em `perguntas.py`)_"
    lim, j = P.CRITERIO_CONTINUAR["limites"], variantes[JEV]["_bruto"]
    melhor = max(BASES, key=lambda v: variantes[v]["_bruto"]["acerto"])
    base = variantes[melhor]["_bruto"]["acerto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    fn_frac = j["fn"] / j["nk"] if j["nk"] else 0.0
    fp_frac = j["fp"] / j["nd"] if j["nd"] else 0.0
    linhas = [
        {"critério": "1 necessária descartada (absoluto)", "medido": f"{j['fn']}/{j['nk']} ({fn_frac:.3f})",
         "limite": f"≤ {lim['necessaria_descartada_max_fracao']}", "passa": ok(fn_frac <= lim["necessaria_descartada_max_fracao"])},
        {"critério": "2 acerto por mensagem (piso)", "medido": f"{j['acerto']:.3f}", "limite": f"≥ {lim['acerto_min']}",
         "passa": ok(j["acerto"] >= lim["acerto_min"])},
        {"critério": "3 acerto ≥ melhor baseline + margem", "medido": f"{j['acerto']:.3f} ({melhor.split(': ')[1]} {base:.3f})",
         "limite": f"≥ {base + lim['margem_sobre_baseline']:.3f}", "passa": ok(j["acerto"] >= base + lim["margem_sobre_baseline"])},
        {"critério": "secundário: manter demais", "medido": f"{j['fp']}/{j['nd']} ({fp_frac:.3f})",
         "limite": f"≤ {lim['manter_demais_max_fracao']}", "passa": ok(fp_frac <= lim["manter_demais_max_fracao"])},
        {"critério": "secundário: precisão de manter", "medido": f"{j['precisao']:.3f}", "limite": f"≥ {lim['precisao_min']}",
         "passa": ok(j["precisao"] >= lim["precisao_min"])},
    ]
    return M.tabela(linhas)


@contextlib.contextmanager
def _com(**troca):
    """Troca constantes de `perguntas` dentro do bloco (o que um humano faria editando o arquivo) e restaura."""
    antes = {k: getattr(P, k) for k in troca}
    try:
        for k, v in troca.items():
            setattr(P, k, v)
        yield
    finally:
        for k, v in antes.items():
            setattr(P, k, v)


def _redecidir(saidas: list[dict], casos: list[dict]) -> list[tuple]:
    """Re-decide com as constantes ATUAIS de `perguntas` a partir dos números guardados (sem cache nem API)."""
    out = []
    for s, c in zip(saidas, casos):
        g = gabarito(c)
        for m in c["mensagens"]:
            pm = s["por_mensagem"][m["id"]]
            p = C.politica(pm)[0] if s["origem"] == "jev" else "manter"
            out.append((p, g[m["id"]], m, c))
    return out


def _linha_curva(rotulo: dict, itens: list[tuple]) -> dict:
    b = metricas(itens)["_bruto"]
    return {**rotulo, "acerto": b["acerto"], "precisão": b["precisao"], "cobertura": b["cobertura"],
            "necessária descartada": f"{b['fn']}/{b['nk']}", "manter demais": f"{b['fp']}/{b['nd']}"}


def curvas(saidas, casos) -> list[tuple[str, list[dict]]]:
    """Cobertura × erro mexendo num parâmetro por vez (mesmas respostas, zero chamada nova)."""
    out = []
    linhas = [_linha_curva({"faixa de needed": "atual (perguntas.py)"}, _redecidir(saidas, casos))]
    for faixa in GRADE_FAIXA:
        with _com(FAIXA_NEEDED=faixa):
            linhas.append(_linha_curva({"faixa de needed": f"{faixa[0]}–{faixa[1]}"}, _redecidir(saidas, casos)))
    out.append(("Faixa de `needed` (≤ nao → não; ≥ sim → sim; meio = dúvida → manter); o resto como em `perguntas.py`", linhas))
    linhas = [_linha_curva({"guarda ≥": "atual (perguntas.py)"}, _redecidir(saidas, casos))]
    for sim in GRADE_SIM:
        with _com(GUARDA_SIM=sim):
            linhas.append(_linha_curva({"guarda ≥": "desligada" if sim > 1 else sim}, _redecidir(saidas, casos)))
    out.append(("Corte da guarda por papel (`rule`/`status`/`literal`)", linhas))
    linhas = [_linha_curva({"superseded ≥": "atual (perguntas.py)"}, _redecidir(saidas, casos))]
    for sim in GRADE_SIM:
        with _com(SUPERSEDED_SIM=sim):
            linhas.append(_linha_curva({"superseded ≥": "desligado" if sim > 1 else sim}, _redecidir(saidas, casos)))
    out.append(("Corte do veto `superseded` (anula a guarda)", linhas))
    linhas = []
    for n in GRADE_N:
        with _com(ULTIMAS_N=n):
            linhas.append(_linha_curva({"últimas N": n}, itens_de(saidas, casos, B_ULT)))
    for k in GRADE_K:
        with _com(PALAVRAS_K=k):
            linhas.append(_linha_curva({"últimas N": f"palavras K={k}"}, itens_de(saidas, casos, B_PAL)))
    out.append(("Baselines — grade de parâmetros neste conjunto (os de `perguntas.py` foram escolhidos no ajuste)", linhas))
    return out


def tamanho(c: dict) -> str:
    n = len(c["mensagens"])
    for a, b in TAMANHOS:
        if a <= n <= b:
            return f"{a}–{b} msgs"
    return f"> {TAMANHOS[-1][1]} msgs"


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    # Sessão estruturalmente inválida (ou com gabarito quebrado) é separada ANTES de qualquer chamada e das métricas:
    # não vai ao Jev, não entra nas tabelas; é listada aqui e contada como falha (no consumidor sairia com tudo mantido).
    todos = dados["casos"]
    motivos = [sessao_invalida(c) for c in todos]
    invalidas = [(str((c.get("id") if isinstance(c, dict) else None) or f"#{i + 1}"), m) for i, (c, m) in enumerate(zip(todos, motivos)) if m]
    casos = [c for c, m in zip(todos, motivos) if not m]
    saidas, custo = rodar(casos)
    custo["invalidas"] = len(invalidas)
    custo["falha"] += len(invalidas)
    itens = {v: itens_de(saidas, casos, v) for v in VARIANTES}
    res = {v: metricas(itens[v]) for v in VARIANTES}
    total = sum(len(c["mensagens"]) for c in casos)
    nk = sum(len(c.get("manter") or []) for c in casos)
    nd = sum(len(c.get("descartar") or []) for c in casos)
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    resumo = {"n": len(casos), "mensagens": total, "dificeis": dificeis, "custo": custo, "variantes": res}
    f2 = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731

    out = [f"## Conjunto `{nome}` — {len(casos)} sessões, {total} mensagens (arquivo versão {dados.get('versao')}, autor "
           f"{dados.get('autor')}); {nk} `manter`, {nd} `descartar`, {total - nk - nd} discutíveis (fora da métrica); {dificeis} difíceis\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if invalidas:
        out.append(f"> **{len(invalidas)} sessão(ões) inválida(s)**, fora da métrica e contada(s) como falha (saem com TUDO mantido pelo "
                   "consumidor, sem chamada): " + "; ".join(f"{i} ({m})" for i, m in invalidas) + ".\n")
    if custo["falha"] > len(invalidas):
        out.append(f"> **{custo['falha']} falha(s) operacional(is)** neste conjunto ({', '.join(c['id'] for s, c in zip(saidas, casos) if s['origem'] == 'falha')}): "
                   "essas sessões saíram com TUDO mantido, sem resposta do Jev (ou com entrada inválida). **As métricas abaixo não são medição do Jev** — rode de novo.\n")

    out.append("### Por mensagem — métrica principal, baselines × manter tudo × Jev nas mesmas mensagens\n")
    out.append(f"**{CARO}** = gabarito `manter` que saiu `descartar` (erro caro: restrição válida, decisão vigente, valor em uso ou erro "
               "aberto somem). **manter demais** = gabarito `descartar` que saiu `manter` (custa tokens). "
               f"`papel = usuario` = toda mensagem do usuário fica; `últimas N` = as últimas {P.ULTIMAS_N} ficam; `palavras da tarefa` = "
               f"≥ {P.PALAVRAS_K} palavra(s) de conteúdo em comum com `tarefa_atual`; `manter tudo` = zero erro caro, zero compactação; "
               "`só needed` = `needed` ≥ 0,5 sem guarda nem faixa de dúvida; `Jev (política)` = `needed` em sim ou dúvida → manter, guarda por "
               "papel em sim sem `superseded` em sim → manter, senão descartar. As duas variantes do Jev leem a MESMA resposta.\n")
    out.append(M.tabela([{"variante": v, **res[v]} for v in VARIANTES], COLUNAS) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(res) + "\n")

    # --- por papel
    out.append("### Por papel\n")
    linhas = []
    for papel in PAPEIS:
        linha = {"papel": papel, "mensagens": sum(m["papel"] == papel and g is not None for _, g, m, _ in itens[JEV]),
                 "gab. manter": sum(m["papel"] == papel and g == "manter" for _, g, m, _ in itens[JEV])}
        for v in (JEV, SO_NEEDED, B_USU, B_ULT, B_PAL):
            b = metricas([it for it in itens[v] if it[2]["papel"] == papel])["_bruto"]
            linha[f"{v}: acerto"] = b["acerto"]
            linha[f"{v}: nec. descartada"] = f"{b['fn']}/{b['nk']}"
        linhas.append(linha)
    out.append(M.tabela(linhas) + "\n")

    # --- Nouls contra o gabarito
    com_jev = [(s, c) for s, c in zip(saidas, casos) if s["origem"] == "jev"]
    out.append(f"### Nouls contra o gabarito — {len(com_jev)} sessões que foram ao Jev\n")
    out.append("`needed` ↔ gabarito `manter` (corte 0,5; faixa = fração fora da dúvida e acerto entre as decididas). A guarda de cada "
               "papel contra o gabarito do papel. `superseded` só é lido como veto: aqui, quanto deu nas mantidas e nas descartadas.\n")
    linhas = []
    it = [(s["por_mensagem"][m["id"]]["needed"], g) for s, c in com_jev for m, g in ((m, gabarito(c)[m["id"]]) for m in c["mensagens"])]
    linhas.append({"noul": "needed (todos)", "positivos": sum(g == "manter" for _, g in it if g), "acerto ≥0,5": M.acerto([(v >= 0.5, g == "manter") for v, g in it if g]),
                   "faixa": f"{P.FAIXA_NEEDED[0]}–{P.FAIXA_NEEDED[1]}", **M.faixa_noul([(v, None if g is None else g == "manter") for v, g in it], *P.FAIXA_NEEDED),
                   "brier": M.brier([(v, g == "manter") for v, g in it if g])})
    for papel in PAPEIS:
        it = [(s["por_mensagem"][m["id"]]["guarda"], gabarito(c)[m["id"]]) for s, c in com_jev for m in c["mensagens"] if m["papel"] == papel]
        if it:
            linhas.append({"noul": f"{P.GUARDA_POR_PAPEL[papel]} ({papel})", "positivos": sum(g == "manter" for _, g in it if g),
                           "acerto ≥0,5": M.acerto([(v >= 0.5, g == "manter") for v, g in it if g]), "faixa": f"≥ {P.GUARDA_SIM}",
                           **M.faixa_noul([(v, None if g is None else g == "manter") for v, g in it], P.GUARDA_SIM, P.GUARDA_SIM),
                           "brier": M.brier([(v, g == "manter") for v, g in it if g])})
    resumo["nouls"] = {l["noul"]: l["acerto ≥0,5"] for l in linhas}
    out.append(M.tabela(linhas) + "\n")
    sup = [(s["por_mensagem"][m["id"]]["superseded"], gabarito(c)[m["id"]]) for s, c in com_jev for m in c["mensagens"]]
    faixa_txt = lambda xs: "—" if not xs else f"{min(xs):.2f}–{max(xs):.2f} (média {sum(xs) / len(xs):.2f})"  # noqa: E731
    out.append(f"`superseded` nas mantidas: {faixa_txt([v for v, g in sup if g == 'manter'])}; ≥ {P.SUPERSEDED_SIM} em "
               f"{sum(v >= P.SUPERSEDED_SIM for v, g in sup if g == 'manter')}/{sum(g == 'manter' for _, g in sup)}. Nas descartadas: "
               f"{faixa_txt([v for v, g in sup if g == 'descartar'])}; ≥ {P.SUPERSEDED_SIM} em "
               f"{sum(v >= P.SUPERSEDED_SIM for v, g in sup if g == 'descartar')}/{sum(g == 'descartar' for _, g in sup)}.\n")
    muda = [(s, c, m) for s, c in com_jev for m in c["mensagens"]
            if (s["por_mensagem"][m["id"]]["decisao"] == "manter") != (s["por_mensagem"][m["id"]]["needed"] >= 0.5)]
    resumo["guardas_mudam"] = len(muda)
    out.append(f"**A guarda e a faixa acrescentam algo a `needed` ≥ 0,5?** Mudaram {len(muda)} decisão(ões): "
               f"{sum(gabarito(c)[m['id']] == s['por_mensagem'][m['id']]['decisao'] for s, c, m in muda)} acerto(s) ganho(s), "
               f"{sum(gabarito(c)[m['id']] not in (None, s['por_mensagem'][m['id']]['decisao']) for s, c, m in muda)} erro(s) novo(s), "
               f"{sum(gabarito(c)[m['id']] is None for s, c, m in muda)} discutível(is).\n")

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador; a sessão inteira conta na família)\n")
    linhas = []
    fams = sorted(dict.fromkeys(familia(c) for c in casos), key=lambda x: (x == "fácil", x))
    for fam in fams:
        sel = lambda v: [it for it in itens[v] if familia(it[3]) == fam]  # noqa: E731
        b = metricas(sel(JEV))["_bruto"]
        linhas.append({"família": fam, "sessões": sum(familia(c) == fam for c in casos), "mensagens": b["n"], "Jev": b["acerto"],
                       "Jev nec. descartada": f"{b['fn']}/{b['nk']}", "Jev manter demais": f"{b['fp']}/{b['nd']}",
                       "só needed": metricas(sel(SO_NEEDED))["_bruto"]["acerto"], "usuario": metricas(sel(B_USU))["_bruto"]["acerto"],
                       "últimas N": metricas(sel(B_ULT))["_bruto"]["acerto"], "palavras": metricas(sel(B_PAL))["_bruto"]["acerto"]})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- tamanho
    out.append("### Por tamanho de sessão (o state inteiro vai numa requisição; acerto cai com sessões maiores?)\n")
    linhas = []
    for t in dict.fromkeys(tamanho(c) for c in casos):
        sel = lambda v: [it for it in itens[v] if tamanho(it[3]) == t]  # noqa: E731
        b = metricas(sel(JEV))["_bruto"]
        linhas.append({"tamanho": t, "sessões": sum(tamanho(c) == t for c in casos), "mensagens": b["n"], "Jev": b["acerto"],
                       "Jev nec. descartada": f"{b['fn']}/{b['nk']}", "Jev manter demais": f"{b['fp']}/{b['nd']}",
                       "só needed": metricas(sel(SO_NEEDED))["_bruto"]["acerto"], "usuario": metricas(sel(B_USU))["_bruto"]["acerto"]})
    resumo["tamanhos"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curvas
    out.append("### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)\n")
    for titulo, linhas in curvas(saidas, casos):
        out.append(f"**{titulo}**\n")
        out.append(M.tabela(linhas) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"sessões": len(casos), "requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "fora da faixa (sem chamada)": custo["longo"], "falhas operacionais (→ manter tudo)": custo["falha"],
                          "perguntas": custo["perguntas"], "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_sessao": round(custo["input_tokens"] / req), "tokens_por_mensagem": round(custo["input_tokens"] / max(total, 1)),
                          "US$_total": f"{custo['custo_us']:.6f}", "US$_por_1000_sessoes": f"{1000 * custo['custo_us'] / max(len(casos), 1):.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")

    # --- caso a caso
    out.append("### Sessão a sessão\n")
    out.append("`gab.` = quantas o gabarito manda manter / descartar; `Jev` = quantas a política manteve; `nec. descartada` e `manter demais` "
               "listam os IDs; `usuario` = acerto do baseline na sessão.\n")
    linhas = []
    for s, c in zip(saidas, casos):
        g = gabarito(c)
        fn = [i for i in c["mensagens"] if g[i["id"]] == "manter" and i["id"] in s["descartar"]]
        fp = [i for i in c["mensagens"] if g[i["id"]] == "descartar" and i["id"] in s["manter"]]
        b = metricas([it for it in itens[JEV] if it[3]["id"] == c["id"]])["_bruto"]
        bu = metricas([it for it in itens[B_USU] if it[3]["id"] == c["id"]])["_bruto"]
        linhas.append({"id": c["id"], "família": familia(c), "msgs": len(c["mensagens"]), "gab.": f"{len(c.get('manter') or [])}/{len(c.get('descartar') or [])}",
                       "Jev manteve": len(s["manter"]), "acerto": b["acerto"], "nec. descartada": ", ".join(i["id"] for i in fn) or "—",
                       "manter demais": ", ".join(i["id"] for i in fp) or "—", "usuario": bu["acerto"], "origem": s["origem"]})
    out.append(M.tabela(linhas) + "\n")
    out.append("### Erros da política, mensagem a mensagem\n")
    out.append("`needed`/`sup`/`guarda` = os três Nouls da mensagem; `motivo` = o da política. Discutíveis ficam fora.\n")
    linhas = []
    for s, c in zip(saidas, casos):
        g = gabarito(c)
        for m in c["mensagens"]:
            pm = s["por_mensagem"][m["id"]]
            if g[m["id"]] is not None and pm["decisao"] != g[m["id"]]:
                linhas.append({"sessão": c["id"], "msg": m["id"], "papel": m["papel"], "gabarito": g[m["id"]], "erro": CARO if g[m["id"]] == "manter" else "manter demais",
                               "needed": f2(pm["needed"]), "sup": f2(pm["superseded"]), "guarda": f2(pm["guarda"]), "motivo": pm["motivo"],
                               "texto": (m["texto"][:90].replace("\n", " ") + ("…" if len(m["texto"]) > 90 else "")).replace("|", "\\|")})
    out.append((M.tabela(linhas) if linhas else "_(nenhum)_") + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Por mensagem, variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES],
                        ["conjunto", *COLUNAS]) + "\n")
    out.append("### Nouls, custo\n")
    out.append(M.tabela([{"conjunto": n, "sessões": r["n"], "mensagens": r["mensagens"], "difíceis": r["dificeis"],
                          **{f"{q} ≥0,5": a for q, a in r["nouls"].items()}, "guarda/faixa mudaram": r["guardas_mudam"],
                          "requisições": r["custo"]["requisicoes"], "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_sessao": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000_sessoes": f"{1000 * r['custo']['custo_us'] / max(r['n'], 1):.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def variantes_md() -> str:
    """No AJUSTE: state `dict` (mensagem apontada por `messages.m07`) × `list` (entrada cujo `id` é m07). Cada
    configuração refaz as chamadas (state diferente = outra chave de cache)."""
    casos = json.loads((AQUI / "dados" / "ajuste.json").read_text(encoding="utf-8"))["casos"]
    configs = [("state `dict` — `messages.m07`", {"STATE_FORMATO": "dict"}), ("state `list` — entrada cujo `id` é m07", {"STATE_FORMATO": "list"})]
    linhas, por_config = [], {}
    for nome, cfg in configs:
        with _com(**cfg):
            saidas, custo = rodar(casos)
            m = {v: metricas(itens_de(saidas, casos, v))["_bruto"] for v in (JEV, SO_NEEDED)}
        por_config[nome] = saidas
        linhas.append({"configuração": nome + (" (a de `perguntas.py`)" if cfg["STATE_FORMATO"] == P.STATE_FORMATO else ""),
                       "requisições": custo["requisicoes"], "falhas": custo["falha"], "Jev (política)": m[JEV]["acerto"],
                       "só needed": m[SO_NEEDED]["acerto"], "nec. descartada": f"{m[JEV]['fn']}/{m[JEV]['nk']}",
                       "manter demais": f"{m[JEV]['fp']}/{m[JEV]['nd']}", "tokens_por_sessao": round(custo["input_tokens"] / max(custo["requisicoes"], 1))})
    base = por_config[configs[0][0]]
    out = ["# Variantes de desenho — compactacao-de-contexto (só no ajuste)\n",
           f"Gerado por `run.py variantes` em {datetime.date.today().isoformat()}; {len(casos)} sessões do `ajuste`; mesmas perguntas e "
           "política, muda só como o state apresenta as mensagens (objeto por ID × lista de objetos).\n", M.tabela(linhas) + "\n",
           "## O que muda, mensagem a mensagem, contra a primeira configuração\n"]
    for nome, _ in configs[1:]:
        dif = []
        for a, b, c in zip(base, por_config[nome], casos):
            g = gabarito(c)
            for m in c["mensagens"]:
                pa, pb = a["por_mensagem"][m["id"]], b["por_mensagem"][m["id"]]
                if pa["decisao"] != pb["decisao"]:
                    dif.append({"sessão": c["id"], "msg": m["id"], "gabarito": g[m["id"]] or "discutível", "antes": f"{pa['decisao']} (needed {pa['needed']:.2f})",
                                "nesta": f"{pb['decisao']} (needed {pb['needed']:.2f})"})
        out.append(f"**{nome}**\n")
        out.append((M.tabela(dif) if dif else "_(nenhuma decisão muda)_") + "\n")
        desvio = [abs(a["por_mensagem"][i][q] - b["por_mensagem"][i][q]) for a, b in zip(base, por_config[nome])
                  if a["origem"] == b["origem"] == "jev" for i in a["por_mensagem"] for q in ("needed", "superseded", "guarda")]
        if desvio:
            out.append(f"Diferença absoluta nos Nouls contra a primeira configuração: média {sum(desvio) / len(desvio):.3f}, máxima {max(desvio):.2f}.\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; cega ou não, conforme a rodada declarada no README): {h}"


def _congelar() -> dict:
    if not P.CRITERIO_CONTINUAR:
        sys.exit("congelar recusado: `perguntas.CRITERIO_CONTINUAR` está vazio (o critério vem ANTES do teste)")
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    return "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_CONTINUAR.items() if k != "limites") or "(ainda não fixado)"


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if args == ["variantes"]:
        (AQUI / "resultados-variantes.md").write_text(variantes_md(), encoding="utf-8", newline="\n")
        print("resultados-variantes.md gerado")
        return
    if "teste" in conjuntos:
        try:
            manifesto = CG.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != P.CRITERIO_CONTINUAR:
            sys.exit("teste recusado: o critério de continuar mudou desde o congelamento (rode `run.py congelar`)")
        linha = _linha_manifesto(manifesto)
    elif congelar:
        linha = _linha_manifesto(_congelar())
    else:
        h = CG.hashes(AQUI, CONGELADOS)
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())
    if args == ["rascunho"]:
        texto, _ = secao_conjunto("rascunho", json.loads((AQUI / "dados" / "rascunho.json").read_text(encoding="utf-8")))
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — compactacao-de-contexto (encanamento)\n\n{texto}", encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — compactacao-de-contexto\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas e política: "
                 f"`perguntas.py`; validação, state, composição e baselines: `compactacao.py`. Preço: US$ 0,042 por milhão de tokens de "
                 f"entrada. State: `{P.STATE_FORMATO}`; faixa de `needed` {P.FAIXA_NEEDED[0]}–{P.FAIXA_NEEDED[1]}; guarda ≥ {P.GUARDA_SIM}; "
                 f"veto `superseded` ≥ {P.SUPERSEDED_SIM}. Faixa validada: até {P.MAX_MENSAGENS} mensagens e {P.TETO_CARACTERES} caracteres "
                 f"por sessão (acima → manter tudo, sem chamada). A saída é a lista para o compactador: nada é apagado daqui.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: r["custo"]["falha"] for n, r in resumos.items() if r["custo"]["falha"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — essas sessões saíram com tudo mantido, sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists() and not falhas:
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
