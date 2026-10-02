"""Roda o "auditor de evidência" num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, auditor.py,
                             run.py, dados/teste.json e o critério de continuar; hash de _comum/ só como registro)
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por afirmação (2 Nouls por registro + 1 global). O cache em `cache/` faz rodar de novo custar zero.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import auditor as A  # noqa: E402
import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import Jev  # noqa: E402

RELACOES = P.RELACOES
COLUNAS = RELACOES + [P.REVISA]
RESULTADOS = AQUI / "resultados.md"
CONGELADOS = ["perguntas.py", "auditor.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
# Grade para a curva cobertura × erro (zero chamada nova): faixa de `contradicts` × faixa de `established`.
GRADE_FAIXA = [(0.5, 0.5), (0.3, 0.7), (0.2, 0.8)]
VARIANTES = ["baseline (palavra-chave)", "sempre pede prova", "Jev"]
# Família difícil pela `nota` do rotulador (LEIA-ME, 14 famílias; heurística por palavra, primeira que casa).
FAMILIAS = [
    (r"mais recente|velho|ficou", "8 verde velho × vermelho novo"),
    (r"/saude|saúde|404", "13 404 / saúde no lugar da rota"),
    (r"\b200\b|corpo", "2 HTTP 200 sem conteúdo / com erro"),
    (r"localhost|homolog", "9 homolog/localhost como produção"),
    (r"dubl|mock|nock", "4 teste com mock"),
    (r"manual", "6 registro manual"),
    (r"lint|warning", "12a lint sem erros × limpo"),
    (r"numérica|versão|\d\.\d\.\d|mostram|latência|réplica|cobertura", "12b numéricas"),
    (r"e-mail|backup|\bdown\b|sonda|\b202\b|entreg|aceit", "14 aceito ≠ entregue / backup / down"),
    (r"outra revisão|revisão [0-9a-f]+|anterior ao|posterior", "1 teste de outra revisão"),
    (r"push|commit|gh pr|pull request", "11 commit ≠ push / push recusado / gh"),
    (r"pulad|skipped|rodou|rodaram|cancel|repeti|instáv|subconjunto|filtro|worker|timeout|nenhum falhou", "10 subconjunto / pulados / cancelada"),
    (r"\bdev\b|\bprod\b|bancos|cofre|migration", "5 dev generalizado / prod com erro / cofre"),
    (r"publicad|deploy|rollback", "7 testado estendido a publicado"),
    (r"build", "3 build sem teste"),
]


def familia(caso: dict) -> str:
    nota = caso.get("nota") or ""
    if not nota.startswith("difícil"):
        return "fácil / outros"
    return next((nome for chave, nome in FAMILIAS if re.search(chave, nota, re.I)), "difícil: outra")


def rodar(casos: list[dict]) -> tuple[list[dict], list[dict], dict]:
    """Uma requisição por afirmação, em lote; 2ª passada (state sem o registro superado) só para os casos em que
    `auditor.precisa_segunda_passada` diz sim. Devolve (números validados, states, custo) da passada que decide;
    cada state carrega `passada`, `fora` (o que a triagem do código tirou antes da chamada) e, na 2ª, `superados` da
    1ª (para o relatório). Registros inválidos = erro antes da chamada. State que a triagem deixou sem registro não
    vai ao Jev: o valor fica None e `auditor.compor` decide `insufficient_evidence` sozinho."""
    jev = Jev(AQUI / "cache")
    pedidos = [A.pedido(c) for c in casos]
    com = [i for i, (st, _) in enumerate(pedidos) if st["records"]]
    respostas = dict(zip(com, _perguntar_varios_seguro(jev, [pedidos[i] for i in com])))
    valores = [_validar_seguro(jev, pedidos[i], respostas[i], len(st["records"])) if i in respostas else None
               for i, (st, _) in enumerate(pedidos)]
    states = [dict(st, passada=1, fora=A.fora_do_state(c)) for (st, _), c in zip(pedidos, casos)]
    segunda = [i for i, (v, st) in enumerate(zip(valores, states)) if A.precisa_segunda_passada(A.compor(v, st))]
    if segunda:
        pedidos2 = [A.pedido(casos[i], set(A.compor(valores[i], states[i])["superados"])) for i in segunda]
        respostas2 = _perguntar_varios_seguro(jev, pedidos2)
        for i, (st2, q2), r2 in zip(segunda, pedidos2, respostas2):
            superados = A.compor(valores[i], states[i])["superados"]
            valores[i] = _validar_seguro(jev, (st2, q2), r2, len(st2["records"]))
            states[i] = dict(st2, passada=2, superados_na_1a=superados, fora=states[i]["fora"])
    custo = jev.resumo()
    custo["segundas_passadas"] = len(segunda)
    custo["falhas_operacionais"] = sum(1 for v in valores if v and v.get("falha"))
    return valores, states, custo


def _perguntar_varios_seguro(jev, pedidos: list[tuple]) -> list:
    """Como `jev.perguntar_varios`, mas uma falha de rede/cache vira o próprio erro no lugar da resposta: a afirmação
    fecha em `revisa` (abaixo) e o lote segue (revisão do Codex no comparador, 2026-10-01, família)."""
    def um(p):
        try:
            return jev.perguntar(*p)
        except Exception as e:  # noqa: BLE001 — a falha vira dado da afirmação, não aborto do lote
            return e
    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(um, pedidos))


def _validar_seguro(jev, pedido: tuple, resposta, n: int) -> dict:
    """`A.validar` com falha isolada: chamada que falhou ou resposta fora do contrato → valor marcado `falha` (que
    `auditor.compor` fecha em `revisa`, nunca `supported`); resposta JSON válida rejeitada sai do cache
    (`invalidar`), senão `auto` a reproduziria em toda rodada."""
    if isinstance(resposta, Exception):
        return A.valor_falha(n, f"falha operacional: chamada ({type(resposta).__name__})")
    try:
        return A.validar(resposta, n)
    except Exception as e:  # noqa: BLE001 — resposta fora do contrato
        if hasattr(jev, "invalidar"):
            jev.invalidar(*pedido)
        return A.valor_falha(n, f"falha operacional: resposta inválida ({type(e).__name__})")


def saida_variante(v: dict, st: dict, caso: dict, variante: str) -> dict:
    """{relacao, apoio} de cada variante sobre o MESMO caso. O baseline lê TODOS os registros (`state_bruto(caso)`),
    nunca o state do auditor: na rodada 1 do teste ele recebia o state já sem o registro superado pelo Jev (vazamento
    de 1 caso, corrigido depois do teste — ver README); desde a rodada 2 o state do auditor também sai sem os
    registros que a triagem tira, e o baseline não herda esse trabalho."""
    if variante.startswith("baseline"):
        return A.baseline(A.state_bruto(caso))
    if variante == "sempre pede prova":
        return {"relacao": "insufficient_evidence", "apoio": []}
    return A.compor(v, st)


def pares_apoio(relacao: str, ids: list[str]) -> set[tuple[str, str]]:
    """Apoio como pares (registro, papel): em `contradicted` os registros citados CONTRADIZEM; nas outras relações
    SUSTENTAM parte. Revisão do Codex 2026-10-01, achado 5: contando só o ID, o baseline de AE-T044 ganhava crédito
    por citar como sustentação o registro que contradiz.
    @example pares_apoio("supported", ["e1"]) → {("e1", "sustenta")}
    @example pares_apoio("contradicted", ["e1"]) → {("e1", "contradiz")}
    """
    papel = "contradiz" if relacao == "contradicted" else "sustenta"
    return {(i, papel) for i in ids}


def gabarito_sustenta(caso: dict, registro_id: str) -> bool | None:
    """Rótulo de "este registro sustenta parte da afirmação" SÓ onde o gabarito é inequívoco para o registro: em
    `supported`/`insufficient_evidence`, apoio = sustenta e fora do apoio = não sustenta; em `contradicted`, o apoio
    lista quem contradiz (não sustenta) e os registros de FORA não têm rótulo de sustentação — o deploy completo de
    AE-T042 sustenta parte e o gabarito não diz. None = fora da métrica (contado e dito no relatório)."""
    if caso["relacao"] == "contradicted":
        return False if registro_id in caso["registros_de_apoio"] else None
    return registro_id in caso["registros_de_apoio"]


def metricas_relacao(itens: list[tuple[dict, dict]]) -> dict:
    """itens = [(saída da variante, caso)]. Acerto com `revisa` contado como erro; cobertura = não revisa;
    FALSA APROVAÇÃO = gabarito não sustentado (insuficiente ou contradito) que saiu `supported` — o erro caro;
    falso alarme = gabarito `supported` que saiu `contradicted`; precisão/recall micro dos registros de apoio POR PAR
    (registro, sustenta|contradiz) — `pares_apoio`."""
    pares = [(s["relacao"], c["relacao"]) for s, c in itens]
    decididos = [(p, g) for p, g in pares if p != P.REVISA]
    nao_sust = [s for s, c in itens if c["relacao"] != "supported"]
    sust = [s for s, c in itens if c["relacao"] == "supported"]
    apoios = [(pares_apoio(s["relacao"], s["apoio"]), pares_apoio(c["relacao"], c["registros_de_apoio"])) for s, c in itens]
    tp = sum(len(prev & gab) for prev, gab in apoios)
    n_prev = sum(len(prev) for prev, _ in apoios)
    n_gab = sum(len(gab) for _, gab in apoios)
    return {
        "n": len(itens),
        "acerto (revisa=erro)": M.acerto(pares),
        "cobertura": len(decididos) / len(itens) if itens else float("nan"),
        "acerto_decididos": M.acerto(decididos),
        "revisa": sum(p == P.REVISA for p, _ in pares),
        "FALSA APROVAÇÃO": f"{sum(s['relacao'] == 'supported' for s in nao_sust)}/{len(nao_sust)}",
        "falso alarme": f"{sum(s['relacao'] == 'contradicted' for s in sust)}/{len(sust)}",
        "apoio precisão": tp / n_prev if n_prev else float("nan"),
        "apoio recall": tp / n_gab if n_gab else float("nan"),
        "apoio exato": f"{sum(prev == gab for prev, gab in apoios)}/{len(itens)}",
    }


def matriz(pares: list[tuple[str, str]]) -> str:
    cont = Counter((g, p) for p, g in pares)
    return M.tabela([{"gabarito ↓ / previsto →": g, **{a: cont[(g, a)] for a in COLUNAS}} for g in RELACOES])


def curva(valores: list[dict], states: list[dict], casos: list[dict]) -> list[dict]:
    """Cobertura (não revisa) × erro entre decididos × falsas aprovações, por faixa de `contradicts` × faixa de
    `established`. Troca as constantes no laço (o que um humano faria editando o arquivo) e restaura."""
    antes = dict(P.FAIXA)
    linhas = []
    try:
        for fc in GRADE_FAIXA:
            for fe in GRADE_FAIXA:
                P.FAIXA.update({"contradicts": fc, "established": fe, "parts": fe})
                ss = [A.compor(v, st) for v, st in zip(valores, states)]
                dec = [(s, c) for s, c in zip(ss, casos) if s["relacao"] != P.REVISA]
                linhas.append({"faixa_contradicts": f"{fc[0]}–{fc[1]}", "faixa_established": f"{fe[0]}–{fe[1]}",
                               "atual": "←" if (fc, fe) == (antes["contradicts"], antes["established"]) else "",
                               "cobertura": len(dec) / len(casos),
                               "erro_decididos": (sum(s["relacao"] != c["relacao"] for s, c in dec) / len(dec)) if dec else float("nan"),
                               "falsas_aprovacoes": sum(s["relacao"] == "supported" and c["relacao"] != "supported" for s, c in dec),
                               "acerto (revisa=erro)": M.acerto([(s["relacao"], c["relacao"]) for s, c in zip(ss, casos)])})
    finally:
        P.FAIXA.update(antes)
    return linhas


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    valores, states, custo = rodar(casos)
    itens = {v: [(saida_variante(val, st, c, v), c) for val, st, c in zip(valores, states, casos)] for v in VARIANTES}
    sem_global = [(A.compor_sem_global(val, st), c) for val, st, c in zip(valores, states, casos)]
    composicoes = {k: [(A.compor(val, st, k), c) for val, st, c in zip(valores, states, casos)] for k in ("established", "parts", "both")}
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    gab = Counter(c["relacao"] for c in casos)
    resumo = {"n": len(casos), "dificeis": dificeis, "gabarito": dict(gab),
              "variantes": {v: metricas_relacao(itens[v]) for v in VARIANTES},
              "sem_global": metricas_relacao(sem_global), "composicoes": {k: metricas_relacao(x) for k, x in composicoes.items()},
              "custo": custo}

    out = [f"## Conjunto `{nome}` — {len(casos)} afirmações (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{dificeis} difíceis; gabarito: " + ", ".join(f"{k} {gab[k]}" for k in RELACOES) + "\n"]
    if nome == "rascunho":
        out.append("> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**\n")

    out.append("### Relação — métrica principal, baseline × sempre pede prova × Jev nos mesmos casos\n")
    out.append("`acerto (revisa=erro)` compara o veredito com o gabarito contando `revisa` como erro; `cobertura` = fração "
               "decidida sem humano. **FALSA APROVAÇÃO** = gabarito `insufficient_evidence` ou `contradicted` que saiu "
               "`supported` (o relatório passaria no portão sem prova): critério 1. `falso alarme` = gabarito `supported` que "
               "saiu `contradicted`. `sempre pede prova` = o custo de evitar toda falsa aprovação: nada aprovado. Apoio: "
               "precisão/recall micro dos `registros_de_apoio` previstos contra o gabarito, por PAR (registro, papel) — "
               "papel = `contradiz` quando a relação é `contradicted`, `sustenta` nas demais; citar como sustentação o "
               "registro que contradiz não pontua; `exato` = conjunto de pares igual.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES]) + "\n")
    out.append(f"**Leituras de \"provada\" nas mesmas respostas** (`COMPOSICAO` atual: `{P.COMPOSICAO}`): só o Noul global "
               "`established`; só os 4 Nouls por parte; ambos; e sem leitura global (algum registro sustenta parte → supported).\n")
    out.append(M.tabela([{"composição": k, **resumo["composicoes"][k]} for k in ("established", "parts", "both")]
                        + [{"composição": "nenhuma (só supports_i)", **resumo["sem_global"]}]) + "\n")
    out.append("**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto; `revisa` = foi para humano)\n")
    out.append(matriz([(s["relacao"], c["relacao"]) for s, c in itens["Jev"]]) + "\n")
    out.append("**Matriz de confusão — baseline**\n")
    out.append(matriz([(s["relacao"], c["relacao"]) for s, c in itens["baseline (palavra-chave)"]]) + "\n")

    # --- Nouls crus
    out.append("### Nouls — acerto (≥ 0,5) e Brier no que cada um decide\n")
    # Só os casos que foram ao Jev (state sem registro não tem Noul). `supports_i`: rótulo por registro só onde o
    # gabarito é inequívoco (`gabarito_sustenta`); None fica fora de acerto, faixa e Brier (as métricas ignoram None).
    resp = [(v, st, c) for v, st, c in zip(valores, states, casos) if v is not None]
    sup_it = [(v["supports"][i], gabarito_sustenta(c, st["records"][i]["id"])) for v, st, c in resp for i in range(len(st["records"]))]
    con_it = [(v["contradicts"][i], st["records"][i]["id"] in c["registros_de_apoio"] and c["relacao"] == "contradicted")
              for v, st, c in resp for i in range(len(st["records"]))]
    est_it = [(v["established"], c["relacao"] == "supported") for v, _, c in resp]
    # Partes: o gabarito só existe no agregado (supported = todas as partes provadas); um Noul de parte pode dizer "sim"
    # num caso insufficient (a parte dele está provada, outra não). A tabela mede cada parte contra "supported" só como
    # leitura; o que decide é a composição.
    linhas = []
    for q, it, faixa, gabarito in (("supports_i", sup_it, (P.APOIO_MIN, P.APOIO_MIN), "registro sustenta parte (rótulo inequívoco)"),
                                   ("contradicts_i", con_it, P.FAIXA["contradicts"], "registro está no apoio de contradicted"),
                                   ("established", est_it, P.FAIXA["established"], "relação = supported"),
                                   *((q, [(v["parts"][q], c["relacao"] == "supported") for v, _, c in resp], P.FAIXA["parts"],
                                      "relação = supported (leitura)") for q in P.PARTES_NOULS)):
        linhas.append({"noul": q, "gabarito": gabarito, "n": sum(g is not None for _, g in it), "acerto": M.acerto([(x >= 0.5, g) for x, g in it]),
                       "faixa": f"{faixa[0]}–{faixa[1]}", **M.faixa_noul(it, *faixa), "brier": M.brier(it)})
    out.append(M.tabela(linhas) + "\n")
    n_fora_sup = sum(g is None for _, g in sup_it)
    out.append(f"`supports_i` é medido só onde o gabarito rotula o registro sem ambiguidade: em `supported` e "
               f"`insufficient_evidence`, apoio = sustenta e o resto = não sustenta; em `contradicted`, o apoio contradiz (não "
               f"sustenta) e os registros FORA do apoio não têm rótulo de sustentação — **{n_fora_sup} registros ficaram fora** "
               f"da métrica de `supports_i` neste conjunto. `contradicts_i` não perde nenhum (fora do apoio de `contradicted`, e "
               f"qualquer registro das outras relações, não contradiz).\n")
    n_checks = sum(len(st["checks"]) for st in states)
    n_falham = sum(not ck["holds"] for st in states for ck in st["checks"])
    n_sup = sum(len(A.compor(v, st)["superados"]) for v, st in zip(valores, states))
    n_ord = sum([r["id"] for r in A.ordenar(c["registros"])] != [r["id"] for r in c["registros"]] for c in casos)
    n_sup += sum(len(st.get("superados_na_1a", {})) for st in states)
    n_fora = {k: sum(len(st["fora"][k]) for st in states) for k in ("neutros", "vencidos", "nao_pertinentes")}
    resumo["codigo"] = {"checks": n_checks, "checks_falham": n_falham, "neutros_fora": n_fora["neutros"],
                        "vencidos_fora": n_fora["vencidos"], "sem_check (não pertinente)": n_fora["nao_pertinentes"],
                        "superados": n_sup, "reordenados": n_ord, "segundas_passadas": custo["segundas_passadas"],
                        "sem_chamada": len(valores) - len(resp)}
    out.append(f"**Trabalho do código**: antes da chamada, {n_fora['neutros']} registros de outra revisão/migration e "
               f"{n_fora['vencidos']} de número refeito por outro mais recente saíram do state ({len(valores) - len(resp)} afirmações "
               f"ficaram sem registro e não foram ao Jev), e {n_fora['nao_pertinentes']} registros de outro ambiente/componente "
               f"ficaram sem check numérico; {n_checks} checks no state ({n_falham} falham); depois da chamada, {n_sup} registros "
               f"superados por outro mais recente do mesmo assunto ({custo['segundas_passadas']} afirmações com 2ª passada sem o "
               f"superado); {n_ord} afirmações com registros reordenados por carimbo.\n")

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador; heurística por palavra)\n")
    linhas = []
    for fam in dict.fromkeys([n for _, n in FAMILIAS] + ["difícil: outra", "fácil / outros"]):
        grupo = [(s, b, c) for (s, c), (b, _) in zip(itens["Jev"], itens["baseline (palavra-chave)"]) if familia(c) == fam]
        if not grupo:
            continue
        linhas.append({"família": fam, "n": len(grupo),
                       "Jev": M.acerto([(s["relacao"], c["relacao"]) for s, _, c in grupo]),
                       "revisa": sum(s["relacao"] == P.REVISA for s, _, _ in grupo),
                       "falsas aprov. Jev": sum(s["relacao"] == "supported" and c["relacao"] != "supported" for s, _, c in grupo),
                       "baseline": M.acerto([(b["relacao"], c["relacao"]) for _, b, c in grupo]),
                       "falsas aprov. base": sum(b["relacao"] == "supported" and c["relacao"] != "supported" for _, b, c in grupo)})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curva
    out.append("### Cobertura × erro por faixa de `contradicts` × faixa de `established`/partes (mesmas respostas; informativo no teste)\n")
    out.append(M.tabela(curva(valores, states, casos)) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    out.append(M.tabela([{"requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "2as_passadas": custo["segundas_passadas"],
                          "perguntas": custo["perguntas"], "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_afirmacao": round(custo["input_tokens"] / max(len(casos), 1)),
                          "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_1000_afirmacoes": f"{1000 * custo['custo_us'] / max(len(casos), 1):.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("`sup/con` = Nouls `supports_i` / `contradicts_i` por registro (ordem cronológica); `est` = `established`; `partes` = "
               "`object_shown` / `state_shown` / `place_shown` / `scope_shown`; "
               "`ok` compara o veredito do Jev com o gabarito; `base` = baseline. `código` = trabalho do código: checks no "
               "state, registros fora do state antes da chamada (outra revisão/migration; número refeito), registros sem check "
               "(outro ambiente/componente) e superados depois da chamada. Registro fora do state não tem Noul.\n")
    linhas = []
    for (s, c), (b, _), v, st in zip(itens["Jev"], itens["baseline (palavra-chave)"], valores, states):
        nouls = " ".join(f"{r['id']} {v['supports'][i]:.2f}/{v['contradicts'][i]:.2f}" for i, r in enumerate(st["records"]))
        codigo = "; ".join([f"{ck['record']} {ck['check']} {'ok' if ck['holds'] else 'FALHA'}" for ck in st["checks"]]
                           + [f"{k} fora do state ({m})" for k, m in {**st["fora"]["neutros"], **st["fora"]["vencidos"]}.items()]
                           + [f"{k} sem check ({m})" for k, m in st["fora"]["nao_pertinentes"].items()]
                           + [f"{k} {m}" for k, m in {**st.get("superados_na_1a", {}), **s["superados"]}.items()]
                           + (["2ª passada sem o superado"] if st.get("passada") == 2 else []))
        partes = " ".join(f"{q.split('_')[0][:3]} {x:.2f}" for q, x in v["parts"].items()) if v else "—"
        linhas.append({"id": c["id"], "fam": familia(c).split(" ")[0], "gab": c["relacao"], "Jev": s["relacao"],
                       "ok": "✓" if s["relacao"] == c["relacao"] else "✗", "apoio gab": ",".join(c["registros_de_apoio"]) or "—",
                       "apoio Jev": ",".join(s["apoio"]) or "—", "est": f"{v['established']:.2f}" if v else "—", "partes": partes,
                       "sup/con": nouls or "—", "código": codigo or "—", "base": b["relacao"], "motivo": s["motivo"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Relação por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES]) + "\n")
    out.append("### Custo e trabalho do código\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"], **r["codigo"],
                          "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_afirmacao": round(r["custo"]["input_tokens"] / r["n"]),
                          "US$_por_1000": f"{1000 * r['custo']['custo_us'] / r['n']:.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    # "antes de abrir o teste" só vale para a rodada cega; o manifesto é regravado a cada correção pós-revisão
    # (revisão do Codex 2026-10-01, achado de família): quem diz se a rodada é cega é o README.
    return (f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; cega ou não, conforme a rodada "
            f"declarada no README): {h}")


def _congelar() -> dict:
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
        (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    c = P.CRITERIO_CONTINUAR
    return f"{c['onde']}: (1) {c['1_falsa_aprovacao']}; (2) {c['2_acerto']}. Secundário: {c['secundario_nao_decide']}."


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
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — auditor-de-evidencia (encanamento)\n\n{texto}",
                                                     encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — auditor-de-evidencia\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas e política: "
                 f"`perguntas.py`; checks, recência, composição e validação: `auditor.py`. Preço: US$ 0,042 por milhão de tokens "
                 f"de entrada. Faixas: contradicts {P.FAIXA['contradicts']}, established {P.FAIXA['established']}, partes {P.FAIXA['parts']}, "
                 f"apoio ≥ {P.APOIO_MIN}; leitura de provada: `{P.COMPOSICAO}`.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    RESULTADOS.write_text(cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes), encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")


if __name__ == "__main__":
    main()
