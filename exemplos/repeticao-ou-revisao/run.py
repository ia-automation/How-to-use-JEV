"""Roda o repetição-ou-revisão num conjunto rotulado de grupos de mensagens e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 grupos fáceis; não é métrica) → resultados-rascunho.md
  python run.py variantes    no ajuste: state com × sem minutos e grupo de 3 inteiro × em pares → resultados-variantes.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py,
                             relacao.py, run.py, dados/teste.json e o critério de continuar; hash de _comum/ só
                             como registro); o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA
                             execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por grupo que o código não resolve por igualdade exata. Falha operacional (chamada, cache faltando,
resposta fora do contrato, grupo inválido) NÃO aborta o lote NEM o relatório: aquele grupo sai `revisar` por
`relacao.julgar_seguro` (nos baselines também, por `baselines_seguro`) e é contado à parte — conjunto com falha
não é medição do Jev. O cache em `cache/` faz rodar de novo custar zero. Bateria do código: `testa_falhas.py`.
"""
from __future__ import annotations

import contextlib
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
import relacao as R  # noqa: E402
from jevcache import Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
# Manifesto com hash do código executado (inclusive este arquivo), dos dados de teste e do critério de aceite.
# `_comum/` entra só como registro: mudar a infra comum não recusa o teste, mas fica anotado.
CONGELADOS = ["perguntas.py", "relacao.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py", "../_comum/metricas.py"]
B_IGUAL, B_JACC, B_ULT = "baseline: igualdade normalizada", "baseline: Jaccard de palavras", "baseline: a última sempre vale"
SEMPRE, SO_CHOICE, JEV = "sempre revisa", "só Choice", "Jev (política)"
BASES = {B_IGUAL: "igualdade", B_JACC: "jaccard", B_ULT: "ultima"}
VARIANTES = [B_IGUAL, B_JACC, B_ULT, SEMPRE, SO_CHOICE, JEV]
RELACOES = P.OPCOES
ABREV = {"same_intent": "same", "revision": "rev", "additional_request": "add", "unclear": "unclear"}
PERDIDA, DUPLICADO = "CORREÇÃO PERDIDA", "EFEITO DUPLICADO"
# Grades das curvas (zero chamada nova): a MESMA faixa em todos os Nouls; depois o piso de confiança da Choice.
GRADE_FAIXA = [(0.5, 0.5), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9), (0.05, 0.95)]
GRADE_CONF = [0.0, 0.3, 0.5, 0.7, 0.9]
GRADE_JACCARD = [(m, r) for m in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0) for r in (0.05, 0.1, 0.2, 0.3)]
COLUNAS = ["variante", "n", "acerto_relacao", f"{PERDIDA} (revision → colapsar)", f"{DUPLICADO} (same_intent → somar)",
           "acao_vigente certa", "unclear → revisar", "revisou sem necessidade"]
CUSTO_ZERO = {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
              "input_tokens": 0, "custo_us": 0.0, "modelos": []}


def familia(c: dict) -> str:
    """Família pela `nota` do rotulador ("difícil: <família> — detalhe"). As fáceis não têm família na nota:
    agrupam pela relação do gabarito."""
    nota = c.get("nota") or ""
    if not nota.startswith("difícil:"):
        return f"fácil: {c['relacao']}"
    corpo = nota[len("difícil:"):].strip()
    return re.sub(r"\s*\(.*?\)", "", re.split(r"\s+[—–]\s+|:\s+", corpo, maxsplit=1)[0]).strip()


def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    """Um grupo por vez pelo mesmo invólucro que o consumidor usa (`julgar_seguro`): o código resolve a igualdade
    exata sem chamada; falha operacional vira `revisar` SÓ naquele grupo. Tudo contado à parte."""
    jev = Jev(AQUI / "cache")  # uma instância por conjunto: latência e tokens separados
    with ThreadPoolExecutor(8) as ex:  # mesmo paralelismo de `Jev.perguntar_varios`
        saidas = list(ex.map(lambda c: R.julgar_seguro(jev, c["mensagens"]), casos))
    custo = jev.resumo() or dict(CUSTO_ZERO)
    for origem in ("codigo", "longo", "falha"):
        custo[origem] = sum(s["origem"] == origem for s in saidas)
    return saidas, custo


def relacao_variante(s: dict, c: dict, variante: str) -> str:
    """Relação prevista por cada variante sobre o MESMO grupo. `só Choice` = a opção vencedora, sem Nouls nem piso
    (o que o código resolveu sem chamada, ou a falha, vale igual nas duas variantes do Jev)."""
    if variante in BASES:
        return R.baselines_seguro(c["mensagens"])[BASES[variante]]
    if variante == SEMPRE:
        return "unclear"
    return s["choice"] if variante == SO_CHOICE and s["origem"] == "jev" else s["relacao"]


def erro_caro(previsto: str, c: dict) -> str:
    """Os dois erros caros, contados à parte: revisão colapsada (a correção some) e repetição somada (efeito em dobro)."""
    if c["relacao"] == "revision" and previsto == "same_intent":
        return PERDIDA
    if c["relacao"] == "same_intent" and previsto == "additional_request":
        return DUPLICADO
    return ""


def metricas_relacao(itens: list[tuple[str, dict]]) -> dict:
    """itens = [(relação prevista pela variante, caso)]."""
    caros = Counter(erro_caro(p, c) for p, c in itens)
    n = Counter(c["relacao"] for _, c in itens)
    b = {"acerto": M.acerto([(p, c["relacao"]) for p, c in itens]), "perdida": caros[PERDIDA], "rev": n["revision"],
         "duplicado": caros[DUPLICADO], "same": n["same_intent"],
         "vigente": sum(R.vigente(p, c["mensagens"]) == c["acao_vigente"] for p, c in itens),
         "unclear_revisar": sum(p == "unclear" and c["relacao"] == "unclear" for p, c in itens), "unclear": n["unclear"],
         "revisou_sem": sum(p == "unclear" and c["relacao"] != "unclear" for p, c in itens),
         "decidiveis": len(itens) - n["unclear"], "n": len(itens)}
    return {"n": len(itens), "acerto_relacao": b["acerto"],
            f"{PERDIDA} (revision → colapsar)": f"{b['perdida']}/{b['rev']}",
            f"{DUPLICADO} (same_intent → somar)": f"{b['duplicado']}/{b['same']}",
            "acao_vigente certa": f"{b['vigente']}/{b['n']}", "unclear → revisar": f"{b['unclear_revisar']}/{b['unclear']}",
            "revisou sem necessidade": f"{b['revisou_sem']}/{b['decidiveis']}", "_bruto": b}


def veredito(variantes: dict) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    if not P.CRITERIO_CONTINUAR:
        return "_(critério ainda não fixado em `perguntas.py`)_"
    lim, j = P.CRITERIO_CONTINUAR["limites"], variantes[JEV]["_bruto"]
    melhor = max(BASES, key=lambda v: variantes[v]["_bruto"]["acerto"])
    base = variantes[melhor]["_bruto"]["acerto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    div = lambda a, n: a / n if n else 0.0  # noqa: E731
    linhas = [
        {"critério": "1 correção perdida", "medido": f"{j['perdida']}/{j['rev']}", "limite": f"≤ {lim['correcao_perdida_max']}",
         "passa": ok(j["perdida"] <= lim["correcao_perdida_max"])},
        {"critério": "2 efeito duplicado", "medido": f"{j['duplicado']}/{j['same']}", "limite": f"≤ {lim['efeito_duplicado_max']}",
         "passa": ok(j["duplicado"] <= lim["efeito_duplicado_max"])},
        {"critério": "3 acerto da relação", "medido": f"{j['acerto']:.3f} (melhor baseline: {melhor.split(': ')[1]} {base:.3f})",
         "limite": f"≥ {base + lim['margem_relacao']:.3f}", "passa": ok(j["acerto"] >= base + lim["margem_relacao"])},
        {"critério": "secundário: unclear → revisar", "medido": f"{j['unclear_revisar']}/{j['unclear']} ({div(j['unclear_revisar'], j['unclear']):.3f})",
         "limite": f"≥ {lim['unclear_revisar_min_fracao']}", "passa": ok(div(j["unclear_revisar"], j["unclear"]) >= lim["unclear_revisar_min_fracao"])},
        {"critério": "secundário: revisou sem necessidade", "medido": f"{j['revisou_sem']}/{j['decidiveis']} ({div(j['revisou_sem'], j['decidiveis']):.3f})",
         "limite": f"≤ {lim['revisou_sem_necessidade_max']}", "passa": ok(div(j["revisou_sem"], j["decidiveis"]) <= lim["revisou_sem_necessidade_max"])},
        {"critério": "secundário: acao_vigente certa", "medido": f"{j['vigente']}/{j['n']} ({div(j['vigente'], j['n']):.3f})",
         "limite": f"≥ {lim['vigente_min_fracao']}", "passa": ok(div(j["vigente"], j["n"]) >= lim["vigente_min_fracao"])},
    ]
    return M.tabela(linhas)


def matriz(pares: list[tuple[str, str]]) -> str:
    cont = Counter((g, p) for p, g in pares)
    return M.tabela([{"gabarito ↓ / previsto →": g, **{a: cont[(g, a)] for a in RELACOES}} for g in RELACOES])


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


def _linha_curva(rotulo: dict, saidas: list[dict], casos: list[dict]) -> dict:
    """Re-decide com as constantes ATUAIS de `perguntas` a partir dos números guardados (sem cache nem API)."""
    previstos = [R.politica(s)[0] if s["origem"] == "jev" else s["relacao"] for s in saidas]
    auto = [(p, c) for p, c in zip(previstos, casos) if p != "unclear"]
    caros = Counter(erro_caro(p, c) for p, c in auto)
    return {**rotulo, "cobertura_auto": len(auto) / len(casos),
            "erro_automatico": (sum(p != c["relacao"] for p, c in auto) / len(auto)) if auto else float("nan"),
            "correções perdidas": caros[PERDIDA], "efeitos duplicados": caros[DUPLICADO],
            "unclear automatizado": sum(c["relacao"] == "unclear" for _, c in auto), "n_auto": len(auto)}


def curvas(saidas: list[dict], casos: list[dict]) -> tuple[list[dict], list[dict]]:
    """Cobertura automática (não foi a `revisar`) × erro entre automáticos, mexendo num parâmetro por vez."""
    faixas = [_linha_curva({"faixa (todos os Nouls)": "atual (perguntas.py)"}, saidas, casos)]
    for faixa in GRADE_FAIXA:
        with _com(FAIXA={q: faixa for q in P.NOULS}):
            faixas.append(_linha_curva({"faixa (todos os Nouls)": f"{faixa[0]}–{faixa[1]}"}, saidas, casos))
    pisos = [_linha_curva({"piso de confiança da Choice": "atual (perguntas.py)"}, saidas, casos)]
    for piso in GRADE_CONF:
        with _com(CONF_MIN=piso):
            pisos.append(_linha_curva({"piso de confiança da Choice": piso}, saidas, casos))
    return faixas, pisos


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custo = rodar(casos)
    itens = {v: [(relacao_variante(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    cont = Counter(c["relacao"] for c in casos)
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    de3 = sum(isinstance(c["mensagens"], list) and len(c["mensagens"]) == 3 for c in casos)
    resumo = {"n": len(casos), "dificeis": dificeis, "custo": custo, "variantes": {v: metricas_relacao(itens[v]) for v in VARIANTES}}
    f2 = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731 — grupo resolvido pelo código ou com falha não tem números

    out = [f"## Conjunto `{nome}` — {len(casos)} grupos (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           + ", ".join(f"{cont[r]} `{r}`" for r in RELACOES) + f"; {dificeis} difíceis; {de3} grupos de 3\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if custo["falha"]:
        out.append(f"> **{custo['falha']} falha(s) operacional(is)** neste conjunto ({', '.join(c['id'] for s, c in zip(saidas, casos) if s['origem'] == 'falha')}): "
                   "esses grupos saíram `revisar` sem resposta do Jev (ou com entrada inválida). **As métricas abaixo não são medição do Jev** — rode de novo.\n")

    # --- relação
    out.append("### Relação (4 classes) — métrica principal, baselines × sempre revisa × Jev nos mesmos grupos\n")
    out.append("Sinal de reconciliação: `same_intent` → colapsar · `revision` → substituir · `additional_request` → somar · "
               "`unclear` → revisar. **CORREÇÃO PERDIDA** = gabarito `revision` que saiu `same_intent` (colapsar apaga a correção). "
               "**EFEITO DUPLICADO** = gabarito `same_intent` que saiu `additional_request` (somar executa duas vezes). "
               "`igualdade normalizada` = textos iguais ⇒ repetição, senão executa tudo; `Jaccard de palavras` = "
               f"≥ {P.JACCARD_MESMO} ⇒ repetição, ≥ {P.JACCARD_REVISAO} ⇒ revisão, abaixo ⇒ pedido novo (limiares da grade do ajuste); "
               "`a última sempre vale` = sempre revisão; `sempre revisa` = zero erro caro, 100% dos grupos a humano; "
               "`só Choice` = a opção vencedora, sem Nouls nem piso; `Jev (política)` = Choice confirmada pelos Nouls, dúvida → revisar. "
               "`acao_vigente` é derivada da relação prevista. As duas variantes do Jev leem a MESMA resposta.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES], COLUNAS) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(resumo["variantes"]) + "\n")
    for v in (JEV, SO_CHOICE, B_IGUAL, B_JACC, B_ULT):
        out.append(f"**Matriz de confusão — {v}** (linhas = gabarito, colunas = previsto)\n")
        out.append(matriz([(p, c["relacao"]) for p, c in itens[v]]) + "\n")
    caros = [{"id": c["id"], "variante": v, "erro": erro_caro(p, c), "família": familia(c)}
             for v in (JEV, SO_CHOICE, B_IGUAL, B_JACC, B_ULT) for p, c in itens[v] if erro_caro(p, c)]
    out.append("**Erros caros, grupo a grupo** (todas as variantes)\n")
    out.append((M.tabela(caros) if caros else "_(nenhum)_") + "\n")

    # --- o que o código resolveu
    sem_chamada = [(s, c) for s, c in zip(saidas, casos) if s["origem"] == "codigo"]
    reduzidos = [(s, c) for s, c in zip(saidas, casos) if s["origem"] == "jev" and s["colapsadas_pelo_codigo"]]
    resumo["codigo_certo"] = f"{sum(c['relacao'] == 'same_intent' for _, c in sem_chamada)}/{len(sem_chamada)}"
    out.append("### O que o código resolveu sem o Jev\n")
    out.append(f"Texto idêntico após normalização em todas as mensagens ⇒ `same_intent` sem chamada: {len(sem_chamada)} grupos, "
               f"{resumo['codigo_certo']} com gabarito `same_intent`"
               + (f" ({', '.join(c['id'] for _, c in sem_chamada)})" if sem_chamada else "") + ". "
               f"Grupos em que o código tirou uma cópia adjacente e mandou ao Jev só as mensagens distintas: {len(reduzidos)}"
               + (f" ({', '.join(c['id'] for _, c in reduzidos)})" if reduzidos else "") + ".\n")

    com_jev = [(s, c) for s, c in zip(saidas, casos) if s["origem"] == "jev"]  # só estes têm números do Jev

    # --- Nouls contra o gabarito
    out.append(f"### Nouls contra a relação do gabarito — {len(com_jev)} grupos que foram ao Jev\n")
    out.append("Cada Noul é o sim/não de UMA relação (`replaces_previous` ↔ `revision`; `soma` = o maior entre `adds_new_request` e "
               "`completes_previous` ↔ `additional_request`; `same_request_again` ↔ `same_intent`); grupos `unclear` ficam fora (o "
               "gabarito não diz sim nem não). Acerto com corte 0,5; `cobertura` = fração decidida fora da faixa de dúvida; "
               "`revisao` = casos dentro dela.\n")
    linhas = []
    # `soma` = o maior dos dois Nouls de soma (pedido novo OU complemento): é o que a política consome.
    valor = lambda s, q: max(s["nouls"][x] for x in P.NOULS_SOMA) if q == "soma" else s["nouls"][q]  # noqa: E731
    for q, rel in (("replaces_previous", "revision"), ("soma", "additional_request"), ("same_request_again", "same_intent")):
        it = [(valor(s, q), None if c["relacao"] == "unclear" else c["relacao"] == rel) for s, c in com_jev]
        nao, sim = P.FAIXA["adds_new_request" if q == "soma" else q]
        linhas.append({"noul": q, "positivos": sum(g is True for _, g in it), "acerto": M.acerto([(v >= 0.5, g) for v, g in it]),
                       "faixa": f"{nao}–{sim}", **M.faixa_noul(it, nao, sim), "brier": M.brier(it)})
    resumo["nouls"] = {l["noul"]: l["acerto"] for l in linhas}
    out.append(M.tabela(linhas) + "\n")
    faixa_txt = lambda xs: "—" if not xs else f"{min(xs):.2f}–{max(xs):.2f}"  # noqa: E731
    out.append("**Nouls de dúvida** (o lado absoluto da opção `unclear`; qualquer um ≥ `sim` → revisar): mín–máx dentro e fora "
               "dos grupos `unclear`, e quantos passam do `sim`.\n")
    eh = lambda c: c["relacao"] == "unclear"  # noqa: E731
    out.append(M.tabela([{"noul": q, "unclear: mín–máx": faixa_txt([s["nouls"][q] for s, c in com_jev if eh(c)]),
                          "unclear ≥ sim": f"{sum(s['nouls'][q] >= P.FAIXA[q][1] for s, c in com_jev if eh(c))}/{sum(eh(c) for _, c in com_jev)}",
                          "demais: mín–máx": faixa_txt([s["nouls"][q] for s, c in com_jev if not eh(c)]),
                          "demais ≥ sim": f"{sum(s['nouls'][q] >= P.FAIXA[q][1] for s, c in com_jev if not eh(c))}/{sum(not eh(c) for _, c in com_jev)}",
                          "faixa": f"{P.FAIXA[q][0]}–{P.FAIXA[q][1]}"} for q in P.NOULS_DUVIDA]) + "\n")
    out.append("Os Nouls de relação nos grupos `unclear`: "
               + "; ".join(f"`{q}` {faixa_txt([s['nouls'][q] for s, c in com_jev if eh(c)])}" for q in P.NOULS if q not in P.NOULS_DUVIDA) + ".\n")

    # --- Choice
    out.append("### Choice `relation` sozinha — cobertura × erro por confiança\n")
    out.append(M.tabela(M.cobertura_erro([(s["conf"], s["choice"] == c["relacao"]) for s, c in com_jev], GRADE_CONF)) + "\n")
    muda = [(s, c) for s, c in com_jev if s["choice"] != s["relacao"]]
    resumo["nouls_mudam"] = len(muda)
    out.append(f"**Os Nouls acrescentam algo à Choice?** A política só pode mandar a `revisar` o que a Choice propôs. Mudou "
               f"{len(muda)} grupo(s): {sum(s['choice'] != c['relacao'] and c['relacao'] == 'unclear' for s, c in muda)} `unclear` recuperado(s), "
               f"{sum(bool(erro_caro(s['choice'], c)) for s, c in muda)} erro(s) caro(s) evitado(s), "
               f"{sum(s['choice'] != c['relacao'] and c['relacao'] != 'unclear' and not erro_caro(s['choice'], c) for s, c in muda)} outro(s) erro(s) trocado(s) por revisão, "
               f"{sum(s['choice'] == c['relacao'] for s, c in muda)} acerto(s) da Choice mandado(s) a `revisar` sem necessidade"
               + (f" ({', '.join(c['id'] for _, c in muda)})" if muda else "") + ".\n")

    # --- famílias
    out.append("### Por família (pela `nota` do rotulador; fáceis agrupadas pela relação)\n")
    linhas = []
    for fam in sorted(dict.fromkeys(familia(c) for c in casos), key=lambda x: (x.startswith("fácil"), x)):
        idx = [i for i, c in enumerate(casos) if familia(c) == fam]
        ac = lambda v: M.acerto([(itens[v][i][0], casos[i]["relacao"]) for i in idx])  # noqa: E731
        linhas.append({"família": fam, "gabarito": "/".join(sorted({ABREV[casos[i]["relacao"]] for i in idx})), "n": len(idx),
                       "Jev": ac(JEV), "só Choice": ac(SO_CHOICE), "igualdade": ac(B_IGUAL), "Jaccard": ac(B_JACC), "última vale": ac(B_ULT),
                       "Jev → revisar": sum(saidas[i]["relacao"] == "unclear" for i in idx),
                       "sem chamada (código)": sum(saidas[i]["origem"] == "codigo" for i in idx),
                       "erro caro Jev": sum(bool(erro_caro(saidas[i]["relacao"], casos[i])) for i in idx)})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curvas
    faixas, pisos = curvas(saidas, casos)
    out.append("### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)\n")
    out.append("`cobertura_auto` = grupo que não foi a `revisar` (inclui os resolvidos pelo código sem chamada). "
               "**Faixa dos Nouls** (a mesma em todos):\n")
    out.append(M.tabela(faixas) + "\n")
    out.append("**Piso de confiança da Choice** (o resto como em `perguntas.py`):\n")
    out.append(M.tabela(pisos) + "\n")
    out.append("**Baseline Jaccard — grade de limiares neste conjunto** (os de `perguntas.py` foram escolhidos no ajuste):\n")
    grade = []
    for mesmo, rev in GRADE_JACCARD:
        with _com(JACCARD_MESMO=mesmo, JACCARD_REVISAO=rev):
            m = metricas_relacao([(R.baselines_seguro(c["mensagens"])["jaccard"], c) for c in casos])["_bruto"]
        grade.append({"≥ mesmo": mesmo, "≥ revisão": rev, "acerto_relacao": m["acerto"], "correções perdidas": m["perdida"], "efeitos duplicados": m["duplicado"]})
    out.append(M.tabela(sorted(grade, key=lambda l: -l["acerto_relacao"])[:6]) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"grupos": len(casos), "requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "sem chamada (código resolve)": custo["codigo"], "fora da faixa (sem chamada)": custo["longo"],
                          "falhas operacionais (→ revisar)": custo["falha"], "perguntas": custo["perguntas"],
                          "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_requisicao": round(custo["input_tokens"] / req),
                          "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_1000_grupos": f"{1000 * custo['custo_us'] / len(casos):.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("`choice` = opção vencedora da Choice (confiança); `troca`/`soma`/`compl`/`mesma` = Nouls `replaces_previous`, "
               "`adds_new_request`, `completes_previous`, `same_request_again`; `s/elo`/`s/alvo`/`ordem` = Nouls de dúvida `no_link_word`, "
               "`target_not_said`, `arrived_out_of_order`; `Jev` = relação da política (`unclear` = revisar); `ok` compara com o "
               "gabarito; `caro` marca o erro caro; `vig` = `acao_vigente` derivada bate com o gabarito; `=`/`J`/`últ` = baselines "
               "igualdade, Jaccard e última vale; `—` = grupo resolvido pelo código sem chamada, ou falha.\n")
    linhas = []
    for s, c in zip(saidas, casos):
        b = R.baselines_seguro(c["mensagens"])
        linhas.append({"id": c["id"], "fam": familia(c), "gab": ABREV[c["relacao"]], "msgs": len(c["mensagens"]) if isinstance(c["mensagens"], list) else "—",
                       "choice": "—" if s["choice"] is None else f"{ABREV[s['choice']]} ({s['conf']:.2f})",
                       "troca": f2(s["nouls"]["replaces_previous"]), "soma": f2(s["nouls"]["adds_new_request"]),
                       "compl": f2(s["nouls"]["completes_previous"]), "mesma": f2(s["nouls"]["same_request_again"]),
                       "s/elo": f2(s["nouls"]["no_link_word"]), "s/alvo": f2(s["nouls"]["target_not_said"]), "ordem": f2(s["nouls"]["arrived_out_of_order"]),
                       "Jev": ABREV[s["relacao"]], "sinal": s["sinal"], "ok": "✓" if s["relacao"] == c["relacao"] else "✗",
                       "caro": erro_caro(s["relacao"], c), "vig": "✓" if s["acao_vigente"] == c["acao_vigente"] else "✗",
                       "=": ABREV[b["igualdade"]], "J": ABREV[b["jaccard"]], "últ": ABREV[b["ultima"]], "motivo": s["motivo"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Relação por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES],
                        ["conjunto", *COLUNAS]) + "\n")
    out.append("### Nouls, código, custo\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"],
                          **{f"{q} ≥0,5": a for q, a in r["nouls"].items()},
                          "código sem chamada (certos)": r["codigo_certo"], "Nouls mudaram a Choice": r["nouls_mudam"],
                          "requisições": r["custo"]["requisicoes"],
                          "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_requisicao": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000_grupos": f"{1000 * r['custo']['custo_us'] / r['n']:.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def variantes_md() -> str:
    """No AJUSTE: as duas decisões de desenho medidas — minutos no state e grupo de 3 inteiro × em pares. Cada
    configuração refaz as chamadas que mudam (state diferente = outra chave de cache)."""
    casos = json.loads((AQUI / "dados" / "ajuste.json").read_text(encoding="utf-8"))["casos"]
    configs = [("sem minutos · grupo de 3 inteiro", {"MINUTOS_NO_STATE": False, "GRUPO_DE_3": "inteiro"}),
               ("COM minutos · grupo de 3 inteiro", {"MINUTOS_NO_STATE": True, "GRUPO_DE_3": "inteiro"}),
               ("sem minutos · grupo de 3 em PARES", {"MINUTOS_NO_STATE": False, "GRUPO_DE_3": "pares"})]
    atual = {"MINUTOS_NO_STATE": P.MINUTOS_NO_STATE, "GRUPO_DE_3": P.GRUPO_DE_3}
    linhas, por_config = [], {}
    for nome, cfg in configs:
        with _com(**cfg):
            saidas, custo = rodar(casos)
        por_config[nome] = saidas
        m = {v: metricas_relacao([(relacao_variante(s, c, v), c) for s, c in zip(saidas, casos)])["_bruto"] for v in (JEV, SO_CHOICE)}
        tres = [(s, c) for s, c in zip(saidas, casos) if len(c["mensagens"]) - len(s["colapsadas_pelo_codigo"]) == 3]
        linhas.append({"configuração": nome + (" (a de `perguntas.py`)" if cfg == atual else ""), "requisições": custo["requisicoes"],
                       "falhas": custo["falha"], "Jev (política)": m[JEV]["acerto"], "só Choice": m[SO_CHOICE]["acerto"],
                       "correções perdidas": m[JEV]["perdida"], "efeitos duplicados": m[JEV]["duplicado"],
                       "unclear → revisar": f"{m[JEV]['unclear_revisar']}/{m[JEV]['unclear']}",
                       "revisou sem necessidade": f"{m[JEV]['revisou_sem']}/{m[JEV]['decidiveis']}",
                       "grupos de 3 distintas certos": f"{sum(s['relacao'] == c['relacao'] for s, c in tres)}/{len(tres)}",
                       "tokens_por_requisicao": round(custo["input_tokens"] / max(custo["requisicoes"], 1))})
    base = por_config[configs[0][0]]
    out = ["# Variantes de desenho — repeticao-ou-revisao (só no ajuste)\n",
           f"Gerado por `run.py variantes` em {datetime.date.today().isoformat()}; {len(casos)} grupos do `ajuste`; mesmas perguntas e "
           "política, muda só o state (minutos) ou o número de requisições por grupo de 3 (inteiro × pares).\n", M.tabela(linhas) + "\n",
           "## O que muda, grupo a grupo, contra a primeira configuração\n"]
    for nome, _ in configs[1:]:
        dif = [{"id": c["id"], "gabarito": c["relacao"], "antes": f"{a['relacao']} (choice {a['choice']})",
                "nesta": f"{b['relacao']} (choice {b['choice']})", "motivo": b["motivo"]}
               for a, b, c in zip(base, por_config[nome], casos) if (a["relacao"], a["choice"]) != (b["relacao"], b["choice"])]
        out.append(f"**{nome}**\n")
        out.append((M.tabela(dif) if dif else "_(nenhuma decisão muda)_") + "\n")
        desvio = [abs(a["nouls"][q] - b["nouls"][q]) for a, b in zip(base, por_config[nome]) for q in P.NOULS
                  if a["origem"] == b["origem"] == "jev"]
        if desvio:
            out.append(f"Diferença absoluta nos Nouls contra a primeira configuração: média {sum(desvio) / len(desvio):.3f}, máxima {max(desvio):.2f}.\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; cega ou não, conforme a rodada declarada no README): {h}"


def _congelar() -> dict:
    """Grava o manifesto pela infra comum e anota, só como registro, o hash da infra comum que rodou."""
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
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — repeticao-ou-revisao (encanamento)\n\n{texto}", encoding="utf-8",
                                                     newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — repeticao-ou-revisao\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas e política: "
                 f"`perguntas.py`; validação, deduplicação exata, composição e baselines: `relacao.py`. Preço: US$ 0,042 por milhão de "
                 f"tokens de entrada. State: minutos {'dentro' if P.MINUTOS_NO_STATE else 'fora'}; grupo de 3: {P.GRUPO_DE_3}. Faixa validada: "
                 f"até {P.MAX_MENSAGENS} mensagens distintas e {P.TETO_CARACTERES} caracteres (acima → revisar, sem chamada). O sinal é "
                 f"proposta de reconciliação: nada é executado nem descartado.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: r["custo"]["falha"] for n, r in resumos.items() if r["custo"]["falha"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — esses grupos saíram `revisar` sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists() and not falhas:
        # A primeira execução COMPLETA com o teste É a rodada cega: fica preservada e nunca é reescrita por este
        # script. Execução com falha operacional não é medição (os grupos que falharam não têm resposta do Jev):
        # não vira rodada 1; rodar de novo só refaz as chamadas que faltaram (o resto vem do cache).
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
