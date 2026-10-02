"""Roda o `compromisso-real` num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, compromisso.py,
                             run.py, dados/teste.json e o critério, com a variante principal; hash de _comum/ só como
                             registro); o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA
                             execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por conversa (todas as perguntas de todos os candidatos). Falha operacional (chamada, cache faltando,
resposta fora do contrato) NÃO aborta o lote: aquela conversa sai toda `revisar` por `compromisso.julgar_seguro`,
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
import compromisso as C  # noqa: E402
from jevcache import Jev  # noqa: E402

ROTULOS = C.ROTULOS
SAIDAS = [*ROTULOS, C.REVISAR]
RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
CONGELADOS = ["perguntas.py", "compromisso.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py", "../_comum/numeros_br.py"]
VARIANTES_JEV = ["choice", "nouls", "choice+nouls"]
JEV_PRINCIPAL = f"Jev {P.VARIANTE_PRINCIPAL}"
VARIANTES = ["baseline (regex)", "sempre compromisso", *[f"Jev {v}" for v in VARIANTES_JEV]]
GRADE_PISO = [0.0, 0.4, 0.5, 0.6, 0.7, 0.8]
COLUNAS = ["variante", "candidatos", "acerto_total", "acerto_nao_compromisso", "TAREFA FANTASMA (não compromisso → compromisso)",
           "COMPROMISSO PERDIDO (compromisso → cancelado/citação)", "compromisso → proposta/pedido", "revisar",
           "prazo certo nos compromissos acertados", "prazo certo nos vivos acertados"]


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador (LEIA-ME: "difícil: <família> — detalhe")."""
    nota = c.get("nota") or ""
    if nota.startswith("difícil:"):
        return re.split(r"\s+[—–-]\s+", nota[len("difícil:"):].strip(), maxsplit=1)[0].strip()
    return "fácil / outros"


def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    """Uma requisição por conversa, pelo mesmo invólucro que o consumidor usa (`julgar_seguro`)."""
    jev = Jev(AQUI / "cache")
    with ThreadPoolExecutor(8) as ex:
        saidas = list(ex.map(lambda c: C.julgar_seguro(jev, c), casos))
    custo = jev.resumo() or {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
                             "input_tokens": 0, "custo_us": 0.0, "modelos": []}
    custo["conversas_longas"] = sum(s["origem"] == "longa" for s in saidas)
    custo["falhas_operacionais"] = sum(s["origem"] == "falha" for s in saidas)
    return saidas, custo


def saida_variante(s: dict, c: dict, variante: str) -> dict:
    """{vereditos, prazo} de cada variante sobre a MESMA conversa (e a mesma resposta do Jev)."""
    if variante.startswith("baseline"):
        return C.baseline(c)
    if variante == "sempre compromisso":
        exprs = C.candidatos_prazo(c)
        return {"vereditos": {k["id"]: "compromisso" for k in c["candidatos"]},
                "prazo": {k["id"]: next((e["data"] for e in exprs if e["data"]), None) for k in c["candidatos"]}}
    return C.redecidir(s, variante.split(" ", 1)[1])


def metricas(itens: list[tuple[dict, dict]]) -> dict:
    """itens = [(saída da variante, caso)]. Erros caros contados à parte: tarefa fantasma, compromisso perdido e prazo
    errado em compromisso acertado."""
    pares, fantasma, fantasma_n, perdido, perdido_n, enfraq, revisar = [], 0, 0, 0, 0, 0, 0
    pc_ok, pc_n, pv_ok, pv_n = 0, 0, 0, 0
    por_classe = {g: [0, 0] for g in ROTULOS}
    fantasma_por = Counter()
    for v, c in itens:
        for k, g in c["vereditos"].items():
            p = v["vereditos"][k]
            pares.append((p, g))
            por_classe[g][1] += 1
            por_classe[g][0] += p == g
            revisar += p == C.REVISAR
            if g != "compromisso":
                fantasma_n += 1
                if p == "compromisso":
                    fantasma += 1
                    fantasma_por[g] += 1
            else:
                perdido_n += 1
                perdido += p in ("cancelado", "citacao_antiga")
                enfraq += p in ("proposta", "pedido_sem_aceite")
            if p == g and g == "compromisso":
                pc_n += 1
                pc_ok += v["prazo"][k] == c["prazo"][k]
            if p == g and g in C.VIVOS:
                pv_n += 1
                pv_ok += v["prazo"][k] == c["prazo"][k]
    nao_comp = [(p, g) for p, g in pares if g != "compromisso"]
    b = {"acerto": M.acerto(pares), "acerto_nao_comp": M.acerto(nao_comp), "n": len(pares), "n_nao_comp": len(nao_comp),
         "fantasma": fantasma, "fantasma_n": fantasma_n, "fantasma_por": dict(fantasma_por), "perdido": perdido, "perdido_n": perdido_n,
         "enfraq": enfraq, "revisar": revisar, "pc_ok": pc_ok, "pc_n": pc_n, "pv_ok": pv_ok, "pv_n": pv_n,
         "por_classe": {g: (a, n) for g, (a, n) in por_classe.items()}, "pares": pares}
    return {"candidatos": len(pares), "acerto_total": b["acerto"], "acerto_nao_compromisso": b["acerto_nao_comp"],
            "TAREFA FANTASMA (não compromisso → compromisso)": f"{fantasma}/{fantasma_n}",
            "COMPROMISSO PERDIDO (compromisso → cancelado/citação)": f"{perdido}/{perdido_n}",
            "compromisso → proposta/pedido": f"{enfraq}/{perdido_n}", "revisar": f"{revisar}/{len(pares)}",
            "prazo certo nos compromissos acertados": f"{pc_ok}/{pc_n}", "prazo certo nos vivos acertados": f"{pv_ok}/{pv_n}", "_bruto": b}


def veredito(variantes: dict) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    lim, j = P.CRITERIO_CONTINUAR["limites"], variantes[JEV_PRINCIPAL]["_bruto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    div = lambda a, n: a / n if n else float("nan")  # noqa: E731
    linhas = [
        {"critério": "1 tarefa fantasma", "medido": f"{j['fantasma']}/{j['fantasma_n']}", "limite": f"≤ {lim['fantasma_max']}",
         "passa": ok(j["fantasma"] <= lim["fantasma_max"])},
        {"critério": "2 compromisso perdido", "medido": f"{j['perdido']}/{j['perdido_n']}", "limite": f"≤ {lim['perdido_max']}",
         "passa": ok(j["perdido"] <= lim["perdido_max"])},
        {"critério": "3 prazo nos compromissos acertados", "medido": f"{j['pc_ok']}/{j['pc_n']} ({div(j['pc_ok'], j['pc_n']):.3f})",
         "limite": f"≥ {lim['prazo_compromisso_min']}", "passa": ok(div(j["pc_ok"], j["pc_n"]) >= lim["prazo_compromisso_min"])},
        {"critério": "4 acerto total", "medido": f"{j['acerto']:.3f} ({j['n']})", "limite": f"≥ {lim['acerto_total_min']}",
         "passa": ok(j["acerto"] >= lim["acerto_total_min"])},
        {"critério": "5 acerto nos não-compromisso", "medido": f"{j['acerto_nao_comp']:.3f} ({j['n_nao_comp']})",
         "limite": f"≥ {lim['acerto_nao_compromisso_min']}", "passa": ok(j["acerto_nao_comp"] >= lim["acerto_nao_compromisso_min"])},
        {"critério": "secundário: revisar", "medido": f"{j['revisar']}/{j['n']} ({div(j['revisar'], j['n']):.3f})",
         "limite": f"≤ {lim['revisar_max']}", "passa": ok(div(j["revisar"], j["n"]) <= lim["revisar_max"])},
        {"critério": "secundário: prazo nos vivos acertados", "medido": f"{j['pv_ok']}/{j['pv_n']} ({div(j['pv_ok'], j['pv_n']):.3f})",
         "limite": f"≥ {lim['prazo_vivos_min']}", "passa": ok(div(j["pv_ok"], j["pv_n"]) >= lim["prazo_vivos_min"])},
    ]
    return M.tabela(linhas)


def matriz(pares: list[tuple[str, str]]) -> str:
    cont = Counter((g, p) for p, g in pares)
    return M.tabela([{"gabarito ↓ / previsto →": g, **{a: cont[(g, a)] for a in SAIDAS}} for g in ROTULOS])


def curva(saidas: list[dict], casos: list[dict]) -> list[dict]:
    """Choice principal com outro piso do vencedor (mesmas respostas): cobertura × erro × erros caros."""
    antes = P.P_MIN_VENCEDOR
    linhas = []
    try:
        for piso in GRADE_PISO:
            P.P_MIN_VENCEDOR = piso
            b = metricas([(C.redecidir(s, "choice"), c) for s, c in zip(saidas, casos)])["_bruto"]
            auto = [(p, g) for p, g in b["pares"] if p != C.REVISAR]
            linhas.append({"piso do vencedor": piso, "cobertura (não revisar)": len(auto) / len(b["pares"]),
                           "erro entre decididos": (1 - M.acerto(auto)) if auto else float("nan"),
                           "tarefa fantasma": b["fantasma"], "compromisso perdido": b["perdido"], "acerto total": b["acerto"]})
    finally:
        P.P_MIN_VENCEDOR = antes
    return linhas


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custo = rodar(casos)
    itens = {v: [(saida_variante(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    n_cand = sum(len(c["candidatos"]) for c in casos)
    resumo = {"n": len(casos), "dificeis": dificeis, "candidatos": n_cand, "custo": custo,
              "variantes": {v: metricas(itens[v]) for v in VARIANTES}}

    out = [f"## Conjunto `{nome}` — {len(casos)} conversas, {n_cand} candidatos (arquivo versão {dados.get('versao')}, autor "
           f"{dados.get('autor')}); {dificeis} difíceis\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if custo["falhas_operacionais"]:
        out.append(f"> **{custo['falhas_operacionais']} falha(s) operacional(is)** neste conjunto: essas conversas saíram todas `revisar` "
                   "sem resposta do Jev. **As métricas abaixo não são medição do Jev** — rode de novo.\n")

    out.append("### Por candidato — baseline × sempre compromisso × Jev (principal e informativas) nos mesmos casos\n")
    out.append("`acerto_total` = veredito exato (`revisar` conta como erro); `acerto_nao_compromisso` = só nos candidatos cujo gabarito "
               "não é `compromisso`. **TAREFA FANTASMA** = gabarito `proposta`/`cancelado`/`citacao_antiga`/`pedido_sem_aceite` que "
               "saiu `compromisso` (a dor: tarefa criada do nada). **COMPROMISSO PERDIDO** = gabarito `compromisso` que saiu "
               "`cancelado` ou `citacao_antiga` (tarefa real fechada). `compromisso → proposta/pedido` = compromisso enfraquecido "
               "(não cria tarefa; menos caro). `prazo certo` = data (ou nulo) igual ao gabarito entre os acertados. `sempre "
               "compromisso` = baseline trivial do LEIA-ME (prazo = primeira expressão com dia da conversa).\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES], COLUNAS) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(resumo["variantes"]) + "\n")
    for v in (JEV_PRINCIPAL, *[f"Jev {x}" for x in VARIANTES_JEV if f"Jev {x}" != JEV_PRINCIPAL], VARIANTES[0]):
        b = resumo["variantes"][v]["_bruto"]
        out.append(f"**Matriz de confusão — {v}** (linhas = gabarito, colunas = previsto) · por classe: " +
                   " · ".join(f"`{g}` {a}/{n}" for g, (a, n) in b["por_classe"].items()) +
                   (f" · fantasma por classe {b['fantasma_por']}" if b["fantasma_por"] else "") + "\n")
        out.append(matriz(b["pares"]) + "\n")

    com_jev = [(s, c) for s, c in zip(saidas, casos) if s["origem"] == "jev"]

    out.append("### Choice de veredito — probabilidade do vencedor e da classe certa, por classe do gabarito\n")
    linhas = []
    for g in ROTULOS:
        op = next(k for k, v in P.ROTULO_DA_OPCAO.items() if v == g)
        pv, pc = [], []
        for s, c in com_jev:
            for k, gab in c["vereditos"].items():
                if gab == g:
                    ch = s["detalhe"][k]["verdict"]
                    pv.append(ch["probabilities"][ch["choice"]])
                    pc.append(ch["probabilities"][op])
        if pv:
            pv.sort(), pc.sort()
            linhas.append({"gabarito": g, "n": len(pv), "P(vencedor) mín–mediana–máx": f"{pv[0]:.2f}–{pv[len(pv)//2]:.2f}–{pv[-1]:.2f}",
                           "P(classe certa) mín–mediana–máx": f"{pc[0]:.2f}–{pc[len(pc)//2]:.2f}–{pc[-1]:.2f}",
                           "P(classe certa) < 0,5": sum(x < 0.5 for x in pc)})
    out.append(M.tabela(linhas) + "\n")

    out.append("### Nouls informativos — valores por classe do gabarito (mín–máx, n) e faixa\n")
    linhas = []
    for k in P.NOULS:
        linha = {"noul": k, "faixa": f"{P.FAIXA[k][0]}–{P.FAIXA[k][1]}"}
        for g in ROTULOS:
            xs = sorted(s["detalhe"][q]["nouls"][k] for s, c in com_jev for q, gab in c["vereditos"].items() if gab == g)
            linha[g] = "—" if not xs else f"{xs[0]:.2f}–{xs[-1]:.2f} ({len(xs)})"
        linhas.append(linha)
    out.append(M.tabela(linhas) + "\n")

    out.append("### Prazo — expressões lidas pelo código e escolha do Jev nos candidatos vivos do gabarito\n")
    out.append("`gabarito entre as expressões` = alguma expressão extraída resolve para a data do gabarito (cobertura do extrator, "
               "código); `escolha` = opção vencedora da Choice do prazo e sua probabilidade.\n")
    linhas, cobre, cobre_n = [], 0, 0
    for s, c in com_jev:
        exprs = s["expressoes"]
        for k, gab in c["vereditos"].items():
            if gab not in C.VIVOS:
                continue
            d = s["detalhe"][k]
            gp = c["prazo"][k]
            entre = (gp is None) or any(e["data"] == gp for e in exprs.values())
            cobre_n += 1
            cobre += entre
            esc = "—" if d["deadline"] is None else f"{d['deadline']['choice']} ({d['deadline']['probabilities'][d['deadline']['choice']]:.2f})"
            linhas.append({"id": c["id"], "k": k, "gabarito": gab, "prazo gab.": gp or "null", "n_expr": len(exprs),
                           "gabarito entre as expressões": "sim" if entre else "NÃO", "escolha (P)": esc,
                           "saiu": s["prazo"][k] or "null", "ok": "✓" if s["prazo"][k] == gp else "✗"})
    resumo["cobertura_prazo"] = (cobre, cobre_n)
    out.append(f"Cobertura do extrator: {cobre}/{cobre_n} candidatos vivos com o gabarito entre as expressões (ou gabarito nulo).\n")
    out.append(M.tabela(linhas) + "\n")

    out.append("### Por família difícil (pela `nota` do rotulador) — acerto e erros caros, Jev principal × baseline\n")
    linhas = []
    fams = list(dict.fromkeys(familia(c) for c in casos if familia(c) != "fácil / outros")) + ["fácil / outros"]
    for fam in fams:
        grupo = [(v, c) for v, c in itens[JEV_PRINCIPAL] if familia(c) == fam]
        if not grupo:
            continue
        bj = metricas(grupo)["_bruto"]
        bb = metricas([(v, c) for v, c in itens[VARIANTES[0]] if familia(c) == fam])["_bruto"]
        linhas.append({"família": fam, "conversas": len(grupo), "candidatos": bj["n"], "acerto Jev": bj["acerto"], "acerto baseline": bb["acerto"],
                       "fantasma Jev": bj["fantasma"], "perdido Jev": bj["perdido"], "revisar Jev": bj["revisar"],
                       "prazo ok Jev": f"{bj['pv_ok']}/{bj['pv_n']}", "fantasma baseline": bb["fantasma"], "perdido baseline": bb["perdido"]})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    out.append("### Curva da Choice principal — piso do vencedor (mesmas respostas; informativo no teste)\n")
    out.append(M.tabela(curva(saidas, casos)) + "\n")

    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "conversas longas (sem chamada)": custo["conversas_longas"],
                          "falhas operacionais (→ revisar)": custo["falhas_operacionais"], "perguntas": custo["perguntas"],
                          "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_conversa": round(custo["input_tokens"] / req), "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_1000_conversas": f"{1000 * custo['custo_us'] / req:.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")

    out.append("### Caso a caso (um candidato por linha)\n")
    out.append("`P` = probabilidade do vencedor da Choice de veredito; `acc/und/quo/opn` = Nouls `accepted`/`undone`/`quoted`/`open_request`; "
               "`ok` compara o veredito da variante principal com o gabarito; `caro` = tarefa fantasma, compromisso perdido ou prazo "
               "errado em compromisso acertado; `base` = baseline.\n")
    f2 = lambda v: f"{v:.2f}"  # noqa: E731
    linhas = []
    for s, c in zip(saidas, casos):
        b = saida_variante(s, c, VARIANTES[0])
        o = saida_variante(s, c, "Jev nouls")
        for k in c["candidatos"]:
            q, gab = k["id"], c["vereditos"][k["id"]]
            p = s["vereditos"][q]
            d = s["detalhe"].get(q)
            caro = ""
            if gab != "compromisso" and p == "compromisso":
                caro = "tarefa fantasma"
            elif gab == "compromisso" and p in ("cancelado", "citacao_antiga"):
                caro = "compromisso perdido"
            elif gab == "compromisso" and p == gab and s["prazo"][q] != c["prazo"][q]:
                caro = "prazo errado"
            linhas.append({"id": c["id"], "fam": familia(c), "k": q, "responsável": k["responsavel_candidato"], "trecho": k["trecho"][:50],
                           "gab": gab + (f" → {c['prazo'][q]}" if c["prazo"][q] else ""),
                           "Jev": p + (f" → {s['prazo'][q]}" if s["prazo"][q] else ""),
                           "P": f2(d["verdict"]["probabilities"][d["verdict"]["choice"]]) if d else "—",
                           "acc/und/quo/opn": "/".join(f2(d["nouls"][x]) for x in P.NOULS) if d else "—",
                           "nouls→": o["vereditos"][q], "ok": "✓" if p == gab else "✗", "caro": caro,
                           "base": b["vereditos"][q] + (f" → {b['prazo'][q]}" if b["prazo"][q] else ""),
                           "motivo": s["motivo"][q] if s["origem"] == "jev" else s["origem"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES],
                        ["conjunto", *COLUNAS]) + "\n")
    out.append("### Custo\n")
    out.append(M.tabela([{"conjunto": n, "conversas": r["n"], "difíceis": r["dificeis"], "candidatos": r["candidatos"],
                          "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_conversa": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000": f"{1000 * r['custo']['custo_us'] / max(r['custo']['requisicoes'], 1):.4f}",
                          "cobertura do extrator de datas": f"{r['cobertura_prazo'][0]}/{r['cobertura_prazo'][1]}",
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
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — compromisso-real (encanamento)\n\n{texto}", encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — compromisso-real\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, política e critério: "
                 f"`perguntas.py`; state, expressões de tempo, validação, guarda de citação e baseline: `compromisso.py`. Preço: US$ 0,042 "
                 f"por milhão de tokens de entrada. Variante principal: `{P.VARIANTE_PRINCIPAL}`; piso do vencedor {P.P_MIN_VENCEDOR}; piso "
                 f"do prazo {P.P_MIN_PRAZO}; guarda de citação {'ligada' if P.GUARDA_CITACAO else 'desligada'}; teto {P.TETO_CARACTERES} "
                 f"caracteres / {P.TETO_CANDIDATOS} candidatos (acima → tudo `revisar`, sem chamada).\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: r["custo"]["falhas_operacionais"] for n, r in resumos.items() if r["custo"]["falhas_operacionais"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — essas conversas saíram `revisar` sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists():
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
