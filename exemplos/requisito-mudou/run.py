"""Roda o `requisito-mudou` num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, requisitos.py,
                             run.py, dados/teste.json e o critério, com a variante principal; hash de _comum/ só como
                             registro); o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA
                             execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por história (todas as perguntas de todos os requisitos). Falha operacional (chamada, cache faltando,
resposta fora do contrato) NÃO aborta o lote: aquela história sai toda `incerto` por `requisitos.julgar_seguro`,
`origem: "falha"`, e é contada à parte — conjunto com falha não é medição do Jev.
O cache em `cache/` faz rodar de novo custar zero. Bateria do código (sem chave nem rede): `testa_falhas.py`.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
import requisitos as R  # noqa: E402
from jevcache import Jev  # noqa: E402

ROTULOS = R.ROTULOS
MUDADOS = ("substituido", "negado", "incerto")
RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
# Manifesto com hash do código executado (inclusive este arquivo), dos dados de teste e do critério (que carrega a
# variante principal). `_comum/` entra só como registro: mudar a infra comum não recusa o teste, mas fica anotado.
CONGELADOS = ["perguntas.py", "requisitos.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py", "../_comum/numeros_br.py"]
JEV_PRINCIPAL = f"Jev {P.VARIANTE_PRINCIPAL}"
JEV_OUTRA = "Jev nouls" if P.VARIANTE_PRINCIPAL == "choice" else "Jev choice"
VARIANTES = ["baseline (palavras-chave)", "sempre mantido", JEV_PRINCIPAL, JEV_OUTRA]
GRADE_PISO = [0.0, 0.4, 0.5, 0.6, 0.7, 0.8]  # curva da Choice: piso do vencedor (zero chamada nova)
COLUNAS = ["variante", "requisitos", "acerto_total", "acerto_mudados", "MUDANÇA PERDIDA (subst/negado → mantido)",
           "TROCA INDEVIDA (incerto/mantido → subst/negado)", "hipótese/terceiro → substituido", "novo_valor certo",
           "reavaliar exato (histórias)", "detectou mudança", "alarme falso (história sem mudança)"]


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador (LEIA-ME: "difícil: <família> — detalhe")."""
    nota = c.get("nota") or ""
    if nota.startswith("difícil:"):
        return re.split(r"\s+[—–-]\s+", nota[len("difícil:"):].strip(), maxsplit=1)[0].strip()
    return "fácil / outros"


def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    """Uma requisição por história, pelo mesmo invólucro que o consumidor usa (`julgar_seguro`): falha operacional
    vira tudo `incerto` SÓ naquela história, sem abortar o lote; contada à parte."""
    jev = Jev(AQUI / "cache")  # uma instância por conjunto: latência e tokens separados
    with ThreadPoolExecutor(8) as ex:  # mesmo paralelismo de `Jev.perguntar_varios`
        saidas = list(ex.map(lambda c: R.julgar_seguro(jev, c["requisitos_anteriores"], c["conversa"], c["shortlist"]), casos))
    custo = jev.resumo() or {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
                             "input_tokens": 0, "custo_us": 0.0, "modelos": []}
    custo["historias_longas"] = sum(s["origem"] == "longa" for s in saidas)
    custo["falhas_operacionais"] = sum(s["origem"] == "falha" for s in saidas)
    return saidas, custo


def saida_variante(s: dict, c: dict, variante: str) -> dict:
    """{atualizacoes, novo_valor, reavaliar} de cada variante sobre a MESMA história (e a mesma resposta do Jev)."""
    reqs, sl = c["requisitos_anteriores"], c["shortlist"]
    if variante.startswith("baseline"):
        return R.baseline(reqs, c["conversa"], sl)
    if variante == "sempre mantido":
        at = {r["id"]: "mantido" for r in reqs}
        return {"atualizacoes": at, "novo_valor": {r["id"]: None for r in reqs}, "reavaliar": []}
    return R.redecidir(s, reqs, sl, variante.split(" ")[1])


def metricas(itens: list[tuple[dict, dict]]) -> dict:
    """itens = [(saída da variante, caso)]. Erros caros contados à parte: mudança perdida (a dor) e troca indevida."""
    pares, perdida, perdida_n, indevida, indevida_n, hip_subst, hip_n, nv_ok, nv_n = [], 0, 0, 0, 0, 0, 0, 0, 0
    reav_ok, detectou, detectou_n, alarme, alarme_n = 0, 0, 0, 0, 0
    por_classe = {g: [0, 0] for g in ROTULOS}
    for v, c in itens:
        gab = c["atualizacoes"]
        for q, g in gab.items():
            p = v["atualizacoes"][q]
            pares.append((p, g))
            por_classe[g][1] += 1
            por_classe[g][0] += p == g
            if g in ("substituido", "negado"):
                perdida_n += 1
                perdida += p == "mantido"
            if g in ("incerto", "mantido"):
                indevida_n += 1
                indevida += p in ("substituido", "negado")
            if g == "incerto":
                hip_n += 1
                hip_subst += p == "substituido"
            if g == "substituido" and p == "substituido":
                nv_n += 1
                nv_ok += v["novo_valor"][q] == c["novo_valor"][q]
        reav_ok += v["reavaliar"] == c["reavaliar"]
        mudou_gab = any(g != "mantido" for g in gab.values())
        mudou_v = any(p != "mantido" for p in v["atualizacoes"].values())
        if mudou_gab:
            detectou_n += 1
            detectou += mudou_v
        else:
            alarme_n += 1
            alarme += mudou_v
    mudados = [(p, g) for p, g in pares if g in MUDADOS]
    b = {"acerto": M.acerto(pares), "acerto_mudados": M.acerto(mudados), "n": len(pares), "n_mudados": len(mudados),
         "perdida": perdida, "perdida_n": perdida_n, "indevida": indevida, "indevida_n": indevida_n,
         "hip_subst": hip_subst, "hip_n": hip_n, "nv_ok": nv_ok, "nv_n": nv_n, "reav_ok": reav_ok, "historias": len(itens),
         "detectou": detectou, "detectou_n": detectou_n, "alarme": alarme, "alarme_n": alarme_n,
         "por_classe": {g: (a, n) for g, (a, n) in por_classe.items()}, "pares": pares}
    return {"requisitos": len(pares), "acerto_total": b["acerto"], "acerto_mudados": b["acerto_mudados"],
            "MUDANÇA PERDIDA (subst/negado → mantido)": f"{perdida}/{perdida_n}",
            "TROCA INDEVIDA (incerto/mantido → subst/negado)": f"{indevida}/{indevida_n}",
            "hipótese/terceiro → substituido": f"{hip_subst}/{hip_n}", "novo_valor certo": f"{nv_ok}/{nv_n}",
            "reavaliar exato (histórias)": f"{reav_ok}/{len(itens)}", "detectou mudança": f"{detectou}/{detectou_n}",
            "alarme falso (história sem mudança)": f"{alarme}/{alarme_n}", "_bruto": b}


def veredito(variantes: dict) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    lim, j = P.CRITERIO_CONTINUAR["limites"], variantes[JEV_PRINCIPAL]["_bruto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    div = lambda a, n: a / n if n else float("nan")  # noqa: E731
    linhas = [
        {"critério": "1 mudança perdida", "medido": f"{j['perdida']}/{j['perdida_n']}", "limite": f"≤ {lim['mudanca_perdida_max']}",
         "passa": ok(j["perdida"] <= lim["mudanca_perdida_max"])},
        {"critério": "2 troca indevida", "medido": f"{j['indevida']}/{j['indevida_n']}", "limite": f"≤ {lim['troca_indevida_max']}",
         "passa": ok(j["indevida"] <= lim["troca_indevida_max"])},
        {"critério": "3 acerto nos mudados", "medido": f"{j['acerto_mudados']:.3f} ({j['n_mudados']})", "limite": f"≥ {lim['acerto_mudados_min']}",
         "passa": ok(j["acerto_mudados"] >= lim["acerto_mudados_min"])},
        {"critério": "4 reavaliar exato", "medido": f"{j['reav_ok']}/{j['historias']} ({div(j['reav_ok'], j['historias']):.3f})",
         "limite": f"≥ {lim['reavaliar_min']}", "passa": ok(div(j["reav_ok"], j["historias"]) >= lim["reavaliar_min"])},
        {"critério": "5 acerto total", "medido": f"{j['acerto']:.3f} ({j['n']})", "limite": f"≥ {lim['acerto_total_min']}",
         "passa": ok(j["acerto"] >= lim["acerto_total_min"])},
        {"critério": "secundário: novo_valor certo", "medido": f"{j['nv_ok']}/{j['nv_n']} ({div(j['nv_ok'], j['nv_n']):.3f})",
         "limite": f"≥ {lim['novo_valor_min']}", "passa": ok(div(j["nv_ok"], j["nv_n"]) >= lim["novo_valor_min"])},
        {"critério": "secundário: detectou mudança", "medido": f"{j['detectou']}/{j['detectou_n']} ({div(j['detectou'], j['detectou_n']):.3f})",
         "limite": f"≥ {lim['detectou_min']}", "passa": ok(div(j["detectou"], j["detectou_n"]) >= lim["detectou_min"])},
    ]
    return M.tabela(linhas)


def matriz(pares: list[tuple[str, str]]) -> str:
    cont = Counter((g, p) for p, g in pares)
    return M.tabela([{"gabarito ↓ / previsto →": g, **{a: cont[(g, a)] for a in ROTULOS}} for g in ROTULOS])


def curva(saidas: list[dict], casos: list[dict]) -> list[dict]:
    """Choice principal com outro piso do vencedor (mesmas respostas): cobertura automática (requisitos que não
    saíram `incerto`) × erro entre eles × erros caros. Troca a constante no laço e restaura."""
    antes = P.P_MIN_VENCEDOR
    linhas = []
    try:
        for piso in GRADE_PISO:
            P.P_MIN_VENCEDOR = piso
            itens = [(R.redecidir(s, c["requisitos_anteriores"], c["shortlist"], "choice"), c) for s, c in zip(saidas, casos)]
            b = metricas(itens)["_bruto"]
            auto = [(p, g) for p, g in b["pares"] if p != "incerto"]
            linhas.append({"piso do vencedor": piso, "cobertura (não incerto)": len(auto) / len(b["pares"]),
                           "erro entre decididos": (1 - M.acerto(auto)) if auto else float("nan"),
                           "mudança perdida": b["perdida"], "troca indevida": b["indevida"], "acerto total": b["acerto"],
                           "reavaliar exato": b["reav_ok"]})
    finally:
        P.P_MIN_VENCEDOR = antes
    return linhas


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custo = rodar(casos)
    itens = {v: [(saida_variante(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    n_req = sum(len(c["atualizacoes"]) for c in casos)
    resumo = {"n": len(casos), "dificeis": dificeis, "requisitos": n_req, "custo": custo,
              "variantes": {v: metricas(itens[v]) for v in VARIANTES}}

    out = [f"## Conjunto `{nome}` — {len(casos)} histórias, {n_req} requisitos (arquivo versão {dados.get('versao')}, autor "
           f"{dados.get('autor')}); {dificeis} difíceis\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if custo["falhas_operacionais"]:
        out.append(f"> **{custo['falhas_operacionais']} falha(s) operacional(is)** neste conjunto: essas histórias saíram todas `incerto` "
                   "sem resposta do Jev. **As métricas abaixo não são medição do Jev** — rode de novo.\n")

    out.append("### Por requisito e por história — baseline × sempre mantido × Jev (principal e informativa) nos mesmos casos\n")
    out.append("`acerto_total` = rótulo exato nos requisitos; `acerto_mudados` = só nos que o gabarito marca `substituido`/`negado`/"
               "`incerto`. **MUDANÇA PERDIDA** = requisito substituído ou negado que saiu `mantido` (a shortlist velha continua valendo: "
               "a dor do exemplo). **TROCA INDEVIDA** = requisito mantido ou incerto (hipótese, terceiro) que saiu `substituido` ou "
               "`negado` (cadastro trocado por fala que não decide). `novo_valor certo` = entre os `substituido` acertados. "
               "`reavaliar exato` = conjunto e ordem iguais ao gabarito (conta do código). `detectou mudança` = história com algum "
               "requisito mudado em que a variante marcou algum. `sempre mantido` = o baseline trivial do LEIA-ME.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES], COLUNAS) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(resumo["variantes"]) + "\n")
    for v in (JEV_PRINCIPAL, JEV_OUTRA, VARIANTES[0]):
        b = resumo["variantes"][v]["_bruto"]
        out.append(f"**Matriz de confusão — {v}** (linhas = gabarito, colunas = previsto) · por classe: " +
                   " · ".join(f"`{g}` {a}/{n}" for g, (a, n) in b["por_classe"].items()) + "\n")
        out.append(matriz(b["pares"]) + "\n")

    com_jev = [(s, c) for s, c in zip(saidas, casos) if s["origem"] == "jev"]

    # --- probabilidades da Choice por classe do gabarito
    out.append("### Choice de status — probabilidade do vencedor e da classe certa, por classe do gabarito\n")
    linhas = []
    for g in ROTULOS:
        op = next(k for k, v in P.ROTULO_DA_OPCAO.items() if v == g)
        pv, pc = [], []
        for s, c in com_jev:
            for q, gab in c["atualizacoes"].items():
                if gab == g:
                    st = s["detalhe"][q]["status"]
                    pv.append(st["probabilities"][st["choice"]])
                    pc.append(st["probabilities"][op])
        if pv:
            pv.sort(), pc.sort()
            linhas.append({"gabarito": g, "n": len(pv), "P(vencedor) mín–mediana–máx": f"{pv[0]:.2f}–{pv[len(pv)//2]:.2f}–{pv[-1]:.2f}",
                           "P(classe certa) mín–mediana–máx": f"{pc[0]:.2f}–{pc[len(pc)//2]:.2f}–{pc[-1]:.2f}",
                           "P(classe certa) < 0,5": sum(x < 0.5 for x in pc)})
    out.append(M.tabela(linhas) + "\n")

    # --- Nouls informativos
    out.append("### Nouls informativos — valores por classe do gabarito (mín–máx) e acerto a 0,5\n")
    linhas = []
    for k in ("changed", "dropped", "open"):
        linha = {"noul": k, "faixa": f"{P.FAIXA[k][0]}–{P.FAIXA[k][1]}"}
        for g in ROTULOS:
            xs = sorted(s["detalhe"][q]["nouls"][k] for s, c in com_jev for q, gab in c["atualizacoes"].items() if gab == g)
            linha[g] = "—" if not xs else f"{xs[0]:.2f}–{xs[-1]:.2f} ({len(xs)})"
        linhas.append(linha)
    out.append(M.tabela(linhas) + "\n")

    # --- valor novo
    out.append("### Valor novo — candidatos do código e escolha do Jev nos `substituido` do gabarito\n")
    linhas = []
    for s, c in com_jev:
        for q, gab in c["atualizacoes"].items():
            if gab != "substituido":
                continue
            d = s["detalhe"][q]
            atr = next(r["atributo"] for r in c["requisitos_anteriores"] if r["id"] == q)
            esc = "—" if d["valor"] is None else f"{d['valor']['choice']} ({d['valor']['probabilities'][d['valor']['choice']]:.2f})"
            linhas.append({"id": c["id"], "q": q, "atributo": atr, "gabarito": c["novo_valor"][q], "n_cand": len(d["candidatos"]),
                           "gabarito entre os candidatos": "sim" if (c["novo_valor"][q] in d["candidatos"] or P.ATRIBUTOS[atr]["tipo"] == "sim_ou_nada") else "NÃO",
                           "escolha (P)": esc, "saiu": s["novo_valor"][q] or "—", "ok": "✓" if s["novo_valor"][q] == c["novo_valor"][q] else "✗"})
    out.append(M.tabela(linhas) + "\n")

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador) — requisitos mudados e erros caros\n")
    linhas = []
    fams = list(dict.fromkeys(familia(c) for c in casos if familia(c) != "fácil / outros")) + ["fácil / outros"]
    for fam in fams:
        grupo = [(v, c) for v, c in itens[JEV_PRINCIPAL] if familia(c) == fam]
        if not grupo:
            continue
        bj, bb = metricas(grupo)["_bruto"], metricas([(v, c) for v, c in itens[VARIANTES[0]] if familia(c) == fam])["_bruto"]
        linhas.append({"família": fam, "histórias": len(grupo), "requisitos": bj["n"], "mudados": bj["n_mudados"],
                       "acerto mudados Jev": bj["acerto_mudados"], "acerto mudados baseline": bb["acerto_mudados"],
                       "mudança perdida Jev": bj["perdida"], "troca indevida Jev": bj["indevida"],
                       "reavaliar exato Jev": f"{bj['reav_ok']}/{len(grupo)}", "mudança perdida baseline": bb["perdida"],
                       "troca indevida baseline": bb["indevida"]})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curva
    out.append("### Curva da Choice principal — piso do vencedor (mesmas respostas; informativo no teste)\n")
    out.append(M.tabela(curva(saidas, casos)) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "histórias longas (sem chamada)": custo["historias_longas"],
                          "falhas operacionais (→ incerto)": custo["falhas_operacionais"], "perguntas": custo["perguntas"],
                          "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_historia": round(custo["input_tokens"] / req), "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_1000_historias": f"{1000 * custo['custo_us'] / req:.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")

    # --- caso a caso
    out.append("### Caso a caso (um requisito por linha)\n")
    out.append("`P` = probabilidade do vencedor da Choice; `chg/drop/open` = Nouls informativos; `ok` compara o rótulo da variante "
               "principal com o gabarito; `caro` = mudança perdida ou troca indevida; `base` = baseline. A linha `reavaliar` fecha cada história.\n")
    f2 = lambda v: f"{v:.2f}"  # noqa: E731
    linhas = []
    for s, c in zip(saidas, casos):
        b = saida_variante(s, c, VARIANTES[0])
        o = saida_variante(s, c, JEV_OUTRA)
        for r in c["requisitos_anteriores"]:
            q, gab = r["id"], c["atualizacoes"][r["id"]]
            p = s["atualizacoes"][q]
            d = s["detalhe"].get(q)
            caro = ""
            if gab in ("substituido", "negado") and p == "mantido":
                caro = "mudança perdida"
            elif gab in ("incerto", "mantido") and p in ("substituido", "negado"):
                caro = "troca indevida"
            linhas.append({"id": c["id"], "fam": familia(c), "q": q, "atributo": r["atributo"], "valor": r["valor"],
                           "gab": gab + (f" → {c['novo_valor'][q]}" if c["novo_valor"][q] else ""),
                           "Jev": p + (f" → {s['novo_valor'][q]}" if s["novo_valor"][q] else ""),
                           "P": f2(d["status"]["probabilities"][d["status"]["choice"]]) if d else "—",
                           "chg/drop/open": "/".join(f2(d["nouls"][k]) for k in ("changed", "dropped", "open")) if d else "—",
                           "nouls→": o["atualizacoes"][q], "ok": "✓" if p == gab else "✗", "caro": caro,
                           "base": b["atualizacoes"][q] + (f" → {b['novo_valor'][q]}" if b["novo_valor"][q] else ""),
                           "motivo": s["motivo"][q]})
        linhas.append({"id": c["id"], "fam": "", "q": "reavaliar", "atributo": "", "valor": "", "gab": ", ".join(c["reavaliar"]) or "[]",
                       "Jev": ", ".join(s["reavaliar"]) or "[]", "P": "", "chg/drop/open": "", "nouls→": ", ".join(o["reavaliar"]) or "[]",
                       "ok": "✓" if s["reavaliar"] == c["reavaliar"] else "✗", "caro": "", "base": ", ".join(b["reavaliar"]) or "[]",
                       "motivo": s["origem"] if s["origem"] != "jev" else ""})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES],
                        ["conjunto", *COLUNAS]) + "\n")
    out.append("### Custo\n")
    out.append(M.tabela([{"conjunto": n, "histórias": r["n"], "difíceis": r["dificeis"], "requisitos": r["requisitos"],
                          "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_historia": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000": f"{1000 * r['custo']['custo_us'] / max(r['custo']['requisicoes'], 1):.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return (f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; variante principal "
            f"`{m['criterio_de_aceite'].get('variante_principal')}`; cega ou não, conforme a rodada declarada no README): {h}")


def _congelar() -> dict:
    """Grava o manifesto pela infra comum e anota, só como registro, o hash da infra comum que rodou."""
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    return "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_CONTINUAR.items() if k != "limites")


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if "teste" in conjuntos:
        # O teste só roda com perguntas, política, dados E critério congelados: o manifesto gravado ANTES tem de bater.
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
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — requisito-mudou (encanamento)\n\n{texto}", encoding="utf-8",
                                                     newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — requisito-mudou\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, política e critério: "
                 f"`perguntas.py`; state, candidatos, validação, `reavaliar` e baseline: `requisitos.py`. Preço: US$ 0,042 por "
                 f"milhão de tokens de entrada. Variante principal: `{P.VARIANTE_PRINCIPAL}`; piso do vencedor {P.P_MIN_VENCEDOR}; "
                 f"teto {P.TETO_CARACTERES} caracteres / {P.TETO_REQUISITOS} requisitos (acima → tudo `incerto`, sem chamada).\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: r["custo"]["falhas_operacionais"] for n, r in resumos.items() if r["custo"]["falhas_operacionais"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — essas histórias saíram `incerto` sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists():
        # A primeira execução com o teste É a rodada cega: fica preservada e nunca é reescrita por este script.
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
