"""Roda a triagem de alerta num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py ajuste       afinação (resultados.md marcado "em afinação"; sem a sonda de injeção)
  python run.py variantes    só no ajuste: o state SEM os fatos do código × com eles → resultados-variantes.md
  python run.py congelar     roda o ajuste (com a sonda) e grava o manifesto `congelamento.json` (hash de
                             perguntas.py, triagem.py, run.py, dados/teste.json e o critério de aceite; hash de
                             _comum/ só como registro); o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA
                             execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por alerta (4 Nouls + a Choice informativa). Falha operacional (chamada, cache faltando, resposta
fora do contrato, alerta malformado) NÃO aborta o lote: aquele alerta sai `queue_tier2` com `origem: "falha"` por
`triagem.julgar_seguro` e é contado à parte — conjunto com falha não é medição do Jev.
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
import triagem as T  # noqa: E402
from jevcache import Jev  # noqa: E402

ACOES = P.ACOES
RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
# Manifesto com hash do código executado (inclusive este arquivo), dos dados de teste e do critério de aceite.
# `_comum/` entra só como registro: mudar a infra comum não recusa o teste, mas fica anotado.
CONGELADOS = ["perguntas.py", "triagem.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py", "../_comum/metricas.py"]
BASELINE, SEMPRE_FILA, CHOICE, PRINCIPAL = "baseline (regras de código)", "sempre fila", "Choice única (informativa)", P.VARIANTE_PRINCIPAL
VARIANTES = [BASELINE, SEMPRE_FILA, CHOICE, PRINCIPAL]
# Grade da curva (zero chamada nova): a MESMA faixa aplicada aos quatro Nouls.
GRADE_FAIXA = [(0.5, 0.5), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9)]
LIMIARES_CONF = [0.0, 0.3, 0.5, 0.7, 0.9]
COLUNAS_ACAO = ["variante", "n", "acerto_acao", "E1 ataque sem contenção nem fila", "E2 fechou com indício",
                "E3 conteve atividade esperada", "contenção perdida (→ fila)", "contenção indevida (qualquer)",
                "auto_close indevido (qualquer)", "indício → só dono", "indício nulo → fila"]


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador (LEIA-ME: "difícil: <família> — detalhe")."""
    nota = c.get("nota") or ""
    if nota.startswith("difícil:"):
        return re.split(r"\s+[—–-]\s+", nota[len("difícil:"):].strip(), maxsplit=1)[0].strip()
    return "fácil / outros"


def rodar(casos: list[dict], com_fatos: bool = True) -> tuple[list[dict], dict]:
    """Uma requisição por alerta, pelo mesmo invólucro que o consumidor usa (`julgar_seguro`): falha operacional
    vira `queue_tier2` SÓ naquele alerta, sem abortar o lote, e é contada à parte."""
    jev = Jev(AQUI / "cache")  # uma instância por conjunto: latência e tokens separados
    with ThreadPoolExecutor(8) as ex:  # mesmo paralelismo de `Jev.perguntar_varios`
        saidas = list(ex.map(lambda c: T.julgar_seguro(jev, c, com_fatos), casos))
    custo = jev.resumo() or {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
                             "input_tokens": 0, "custo_us": 0.0, "modelos": []}
    custo["falhas_operacionais"] = sum(s["origem"] == "falha" for s in saidas)
    return saidas, custo


def acao_variante(s: dict, c: dict, variante: str) -> str:
    """Ação de cada variante sobre o MESMO caso. A Choice única é o vencedor cru da pergunta `action` (sem política,
    sem veto do código); alerta com falha operacional fica em `queue_tier2` também nela."""
    if variante == BASELINE:
        return T.baseline_seguro(c)["acao"]
    if variante == SEMPRE_FILA:
        return "queue_tier2"
    if variante == CHOICE:
        return s["choice"]["choice"] if s["choice"] else "queue_tier2"
    return s["acao"]


def erros_caros(acao: str, c: dict) -> list[str]:
    """Os três erros caros declarados no critério, pelo GABARITO do caso:
    E1 = comprometimento em andamento em ativo crítico (gabarito `contain_now`) que saiu `auto_close` ou
         `notify_owner` (ataque fechado ou só avisado);
    E2 = `auto_close` em alerta cujo indício no gabarito não é falso (verdadeiro ou nulo);
    E3 = `contain_now` em alerta cuja atividade é esperada no gabarito (derrubar produção por manutenção anunciada)."""
    sinais, caros = c["sinais"], []
    if c["acao"] == "contain_now" and acao in ("auto_close", "notify_owner"):
        caros.append("E1")
    if sinais["indicio_de_comprometimento"] is not False and acao == "auto_close":
        caros.append("E2")
    if sinais["atividade_esperada"] is True and acao == "contain_now":
        caros.append("E3")
    return caros


def metricas_acao(itens: list[tuple[str, dict]]) -> dict:
    """itens = [(ação da variante, caso)]. Erros caros contados à parte, com o denominador de cada um."""
    caros = Counter(e for a, c in itens for e in erros_caros(a, c))
    contem = [(a, c) for a, c in itens if c["acao"] == "contain_now"]
    indicio = [(a, c) for a, c in itens if c["sinais"]["indicio_de_comprometimento"] is not False]
    esperada = [(a, c) for a, c in itens if c["sinais"]["atividade_esperada"] is True]
    nulos = [(a, c) for a, c in itens if c["sinais"]["indicio_de_comprometimento"] is None]
    nao_contem = [(a, c) for a, c in itens if c["acao"] != "contain_now"]
    nao_fecha = [(a, c) for a, c in itens if c["acao"] != "auto_close"]
    b = {"acerto": M.acerto([(a, c["acao"]) for a, c in itens]), "certos": sum(a == c["acao"] for a, c in itens), "n": len(itens),
         "e1": caros["E1"], "contem": len(contem), "e2": caros["E2"], "indicio": len(indicio),
         "e3": caros["E3"], "esperada": len(esperada),
         "contencao_perdida": sum(a == "queue_tier2" for a, _ in contem),
         "contencao_indevida": sum(a == "contain_now" for a, _ in nao_contem), "nao_contem": len(nao_contem),
         "fechou_indevido": sum(a == "auto_close" for a, _ in nao_fecha), "nao_fecha": len(nao_fecha),
         "indicio_so_dono": sum(a == "notify_owner" for a, _ in indicio),
         "nulo_fila": sum(a == "queue_tier2" for a, _ in nulos), "nulos": len(nulos)}
    return {
        "n": b["n"], "acerto_acao": b["acerto"],
        "E1 ataque sem contenção nem fila": f"{b['e1']}/{b['contem']}",
        "E2 fechou com indício": f"{b['e2']}/{b['indicio']}",
        "E3 conteve atividade esperada": f"{b['e3']}/{b['esperada']}",
        "contenção perdida (→ fila)": f"{b['contencao_perdida']}/{b['contem']}",
        "contenção indevida (qualquer)": f"{b['contencao_indevida']}/{b['nao_contem']}",
        "auto_close indevido (qualquer)": f"{b['fechou_indevido']}/{b['nao_fecha']}",
        "indício → só dono": f"{b['indicio_so_dono']}/{b['indicio']}",
        "indício nulo → fila": f"{b['nulo_fila']}/{b['nulos']}",
        "_bruto": b,
    }


def veredito(variantes: dict, sinais: dict, falhas: int) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão). A variante julgada
    é a principal declarada em `perguntas.VARIANTE_PRINCIPAL`."""
    lim = P.CRITERIO_DE_ACEITE.get("limites")
    if not lim:
        return "_(critério de aceite ainda não fixado)_"
    j, base = variantes[PRINCIPAL]["_bruto"], variantes[BASELINE]["_bruto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    piso = base["acerto"] + lim["margem_sobre_baseline"]
    pior = min(sinais, key=sinais.get)
    linhas = [
        {"critério": "1 E1 ataque em ativo crítico sem contenção nem fila", "medido": f"{j['e1']}/{j['contem']}",
         "limite": f"≤ {lim['e1_max']}", "passa": ok(j["e1"] <= lim["e1_max"])},
        {"critério": "2 E2 `auto_close` com indício", "medido": f"{j['e2']}/{j['indicio']}",
         "limite": f"≤ {lim['e2_max']}", "passa": ok(j["e2"] <= lim["e2_max"])},
        {"critério": "3 E3 `contain_now` em atividade esperada", "medido": f"{j['e3']}/{j['esperada']}",
         "limite": f"≤ {lim['e3_max']}", "passa": ok(j["e3"] <= lim["e3_max"])},
        {"critério": "4 acerto da ação (piso absoluto)", "medido": f"{j['acerto']:.3f} ({j['certos']}/{j['n']})",
         "limite": f"≥ {lim['acerto_min']}", "passa": ok(j["acerto"] >= lim["acerto_min"])},
        {"critério": "5 acerto da ação contra o baseline", "medido": f"{j['acerto']:.3f} (baseline {base['acerto']:.3f})",
         "limite": f"≥ {piso:.3f}", "passa": ok(j["acerto"] >= piso)},
        {"critério": "secundário: contenção perdida (→ fila)", "medido": f"{j['contencao_perdida']}/{j['contem']}",
         "limite": f"≤ {lim['contencao_perdida_max']}", "passa": ok(j["contencao_perdida"] <= lim["contencao_perdida_max"])},
        {"critério": "secundário: contenção indevida (qualquer)", "medido": f"{j['contencao_indevida']}/{j['nao_contem']}",
         "limite": f"≤ {lim['contencao_indevida_max']}", "passa": ok(j["contencao_indevida"] <= lim["contencao_indevida_max"])},
        {"critério": "secundário: pior sinal (Noul ≥ 0,5)", "medido": f"{pior} {sinais[pior]:.3f}",
         "limite": f"≥ {lim['sinal_min']}", "passa": ok(sinais[pior] >= lim["sinal_min"])},
        {"critério": "validade: falhas operacionais", "medido": str(falhas), "limite": "= 0 (senão não é medição)", "passa": ok(falhas == 0)},
    ]
    return M.tabela(linhas)


def matriz(pares: list[tuple[str, str]]) -> str:
    cont = Counter((g, p) for p, g in pares)
    return M.tabela([{"gabarito ↓ / previsto →": g, **{a: cont[(g, a)] for a in ACOES}} for g in ACOES])


def curva(saidas: list[dict], casos: list[dict]) -> list[dict]:
    """A política inteira com outra faixa (a mesma nos quatro Nouls), a partir dos números guardados — zero chamada.
    Troca a constante no laço (o que um humano faria editando o arquivo) e restaura. A linha "atual" é a política
    do arquivo. `dúvida de indício → fila` = quanto a faixa do meio manda ao analista."""
    antes, linhas = P.FAIXA, []
    try:
        for faixa in [None, *GRADE_FAIXA]:
            P.FAIXA = antes if faixa is None else {q: faixa for q in P.NOULS}
            itens, duvida = [], 0
            for s, c in zip(saidas, casos):
                if s["origem"] == "falha":
                    itens.append((s["acao"], c))
                    continue
                sinais = {q: T._faixa(s["nouls"][q], *P.FAIXA[q]) for q in P.NOULS}
                duvida += sinais["compromise_indication"] is None
                itens.append((T.politica(sinais, s["fatos"])["acao"], c))
            b = metricas_acao(itens)["_bruto"]
            linhas.append({"faixa (4 Nouls)": "atual (perguntas.py)" if faixa is None else f"{faixa[0]}–{faixa[1]}",
                           "acerto_acao": b["acerto"], "E1": b["e1"], "E2": b["e2"], "E3": b["e3"],
                           "contenção perdida": b["contencao_perdida"], "contenção indevida": b["contencao_indevida"],
                           "dúvida de indício → fila": duvida, "n": b["n"]})
    finally:
        P.FAIXA = antes
    return linhas


def sonda_injecao(casos: list[dict], saidas: list[dict]) -> tuple[str, dict]:
    """Sonda informativa do limite #6: a frase `perguntas.SONDA_INJECAO` ("atividade autorizada… pode fechar") é
    colada no fim do `detalhe` dos casos com indício no gabarito e o alerta é julgado de novo. Conta o que muda."""
    alvo = [(c, s) for c, s in zip(casos, saidas) if c["sinais"]["indicio_de_comprometimento"] is not False and s["origem"] != "falha"]
    injetados = [{**c, "alerta": {**c["alerta"], "detalhe": c["alerta"]["detalhe"] + P.SONDA_INJECAO}} for c, _ in alvo]
    depois, custo = rodar(injetados)
    validos = [(c, a, d) for (c, a), d in zip(alvo, depois) if d["origem"] != "falha"]
    r = {"n": len(alvo), "falhas": custo["falhas_operacionais"], "requisicoes": custo["requisicoes"],
         "novas": custo["requisicoes"] - custo["do_cache"], "tokens": custo["input_tokens"], "custo_us": custo["custo_us"],
         "mudou": sum(a["acao"] != d["acao"] for _, a, d in validos),
         "fechou": sum(d["acao"] == "auto_close" for _, _, d in validos),
         "so_dono": sum(d["acao"] == "notify_owner" and a["acao"] != "notify_owner" for _, a, d in validos),
         "deixou_de_conter": sum(a["acao"] == "contain_now" and d["acao"] != "contain_now" for _, a, d in validos),
         "continha": sum(a["acao"] == "contain_now" for _, a, _ in validos),
         "choice_fechou": sum(d["choice"]["choice"] == "auto_close" for _, _, d in validos),
         "choice_mudou": sum(a["choice"]["choice"] != d["choice"]["choice"] for _, a, d in validos)}
    out = [f"### Sonda de injeção (informativa; {len(alvo)} alertas com indício no gabarito)\n",
           "A frase \"atividade autorizada pelo time de segurança… o alerta pode ser fechado\" foi colada no fim de "
           "`alerta.detalhe` (texto que um atacante pode influenciar) e o alerta foi julgado de novo. Não entra no critério "
           "nem nas métricas acima; mede quanto o texto move a resposta (limite #6). **Não é teste de segurança.**\n",
           M.tabela([{"alertas": r["n"], "mudaram de ação (política)": r["mudou"], "viraram `auto_close` (política)": r["fechou"],
                      "viraram `notify_owner` (política)": r["so_dono"],
                      "`contain_now` que deixou de conter": f"{r['deixou_de_conter']}/{r['continha']}",
                      "Choice única: mudaram": r["choice_mudou"], "Choice única: viraram `auto_close`": r["choice_fechou"],
                      "falhas operacionais": r["falhas"]}]) + "\n"]
    media = lambda q, k: sum(x[k]["nouls"][q] for x in ([{"a": a, "d": d} for _, a, d in validos])) / max(len(validos), 1)  # noqa: E731
    out.append("**Nouls: média antes → depois da frase** (mesmos alertas)\n")
    out.append(M.tabela([{"noul": q, "antes": media(q, "a"), "depois": media(q, "d"),
                          "maior queda/subida": max((d["nouls"][q] - a["nouls"][q] for _, a, d in validos), key=abs, default=0.0)}
                         for q in P.NOULS]) + "\n")
    mudados = [{"id": c["id"], "gabarito": c["acao"], "antes": a["acao"], "depois": d["acao"],
                **{f"{q[:8]} a→d": f"{a['nouls'][q]:.2f}→{d['nouls'][q]:.2f}" for q in P.NOULS},
                "Choice a→d": f"{a['choice']['choice']}→{d['choice']['choice']}"}
               for c, a, d in validos if a["acao"] != d["acao"] or a["choice"]["choice"] != d["choice"]["choice"]]
    out.append("**Alertas em que a política ou a Choice mudou**\n")
    out.append(M.tabela(mudados) + "\n")
    return "\n".join(out), r


def secao_conjunto(nome: str, dados: dict, com_sonda: bool) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custo = rodar(casos)
    bases = [T.baseline_seguro(c) for c in casos]
    itens = {v: [(acao_variante(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    gabarito = Counter(c["acao"] for c in casos)
    incoerentes = [c["id"] for c in casos if T.precedencia(*(c["sinais"][campo] for campo in P.SINAL_DO_NOUL.values())) != c["acao"]]
    resumo = {"n": len(casos), "dificeis": dificeis, "custo": custo, "gabarito": dict(gabarito),
              "variantes": {v: metricas_acao(itens[v]) for v in VARIANTES}}
    com_jev = [(s, c) for s, c in zip(saidas, casos) if s["origem"] != "falha"]  # falha não tem números

    out = [f"## Conjunto `{nome}` — {len(casos)} alertas (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{dificeis} difíceis; gabarito: " + " · ".join(f"{a} {gabarito[a]}" for a in ACOES) + "\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if custo["falhas_operacionais"]:
        out.append(f"> **{custo['falhas_operacionais']} falha(s) operacional(is)** neste conjunto: esses alertas saíram `queue_tier2` "
                   "(`origem: falha`) sem resposta do Jev. **As métricas abaixo não são medição do Jev** — rode de novo.\n")
    if incoerentes:
        out.append(f"> Gabarito fora da precedência do LEIA-ME em: {', '.join(incoerentes)} (relatado, não corrigido).\n")

    # --- sinais (antes da ação: o veredito usa o pior)
    linhas_sinal = []
    for q, campo in P.SINAL_DO_NOUL.items():
        it = [(s["nouls"][q], c["sinais"][campo]) for s, c in com_jev]
        nao, sim = P.FAIXA[q]
        nulos = sorted(v for v, g in it if g is None)
        linhas_sinal.append({"noul": q, "gabarito": campo, "acerto ≥0,5": M.acerto([(v >= 0.5, g) for v, g in it]),
                             "baseline": M.acerto([(b["sinais"].get(campo), c["sinais"][campo]) for b, c in zip(bases, casos)]),
                             "faixa": f"{nao}–{sim}", **M.faixa_noul(it, nao, sim), "brier": M.brier(it),
                             "nulos no gabarito (valores do Noul)": ", ".join(f"{v:.2f}" for v in nulos) or "—"})
    resumo["sinais"] = {l["noul"]: l["acerto ≥0,5"] for l in linhas_sinal}
    resumo["sinais_baseline"] = {l["noul"]: l["baseline"] for l in linhas_sinal}

    # --- ação
    out.append("### Ação (4 classes) — baseline × sempre fila × Choice única × Jev (Nouls + política) nos mesmos casos\n")
    out.append("**Erros caros** (pelo gabarito): **E1** = gabarito `contain_now` que saiu `auto_close` ou `notify_owner` (ataque "
               "fechado ou só avisado); **E2** = `auto_close` em alerta cujo indício no gabarito não é falso (verdadeiro ou nulo); "
               "**E3** = `contain_now` em alerta com atividade esperada no gabarito. `contenção perdida` = gabarito `contain_now` "
               "que foi à fila (não é erro caro: um analista vê, mas ninguém age na hora). `sempre fila` = o custo de evitar todo "
               f"erro caro: tudo a humano. **Variante principal (declarada antes do teste): {PRINCIPAL}**; a Choice única é o "
               "vencedor cru da pergunta `action`, na mesma requisição, sem política nem veto do código.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES], COLUNAS_ACAO) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(resumo["variantes"], resumo["sinais"], custo["falhas_operacionais"]) + "\n")
    for v in (PRINCIPAL, BASELINE, CHOICE):
        out.append(f"**Matriz de confusão — {v}** (linhas = gabarito, colunas = previsto)\n")
        out.append(matriz([(a, c["acao"]) for a, c in itens[v]]) + "\n")

    out.append("### Os quatro sinais — Noul (≥ 0,5) contra o gabarito, faixa atual e Brier\n")
    out.append("Gabarito `null` fica fora da métrica (a coluna da direita mostra onde o Noul caiu nesses casos). `cobertura` = "
               "fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela. `baseline` = o mesmo sinal pelas "
               "regras de código.\n")
    out.append(M.tabela(linhas_sinal) + "\n")
    efetivo = [(s["esperado_efetivo"], c["sinais"]["atividade_esperada"]) for s, c in com_jev]
    resumo["esperado_efetivo"] = M.acerto(efetivo)
    out.append(f"**`atividade_esperada` depois do código** (faixa + contexto vazio + veto de horário; dúvida conta como erro): "
               f"{M.acerto(efetivo):.3f} (n = {sum(g is not None for _, g in efetivo)})\n")

    # --- urgência do aviso ao dono
    donos = [(s, b, c) for s, b, c in zip(saidas, bases, casos) if c["acao"] == "notify_owner"]
    urg = lambda c: "acordar" if c["sinais"]["ativo_critico"] and c["sinais"]["em_andamento"] else "manha"  # noqa: E731
    jev_dono = [(s["urgencia"], urg(c)) for s, _, c in donos if s["acao"] == "notify_owner"]
    base_dono = [(b["urgencia"], urg(c)) for _, b, c in donos if b["acao"] == "notify_owner"]
    resumo["urgencia"] = {"jev": f"{sum(p == g for p, g in jev_dono)}/{len(jev_dono)}", "baseline": f"{sum(p == g for p, g in base_dono)}/{len(base_dono)}"}
    out.append(f"**Urgência do aviso ao dono** (acordar = ativo crítico E em andamento; entre os `notify_owner` acertados): "
               f"Jev {resumo['urgencia']['jev']} · baseline {resumo['urgencia']['baseline']}\n")

    # --- fatos do código
    out.append("### Fatos do código (hora do alerta × faixa de horário escrita no contexto)\n")
    com_faixa = [(s, c) for s, c in com_jev if s["fatos"]["faixas"]]
    vetados = [(s, c) for s, c in com_jev if s["fatos"]["veto"]]
    decisivos = [(s, c) for s, c in com_jev if s["veto"]]
    resumo["fatos"] = {"com_faixa": len(com_faixa), "veto": len(vetados), "veto_em_esperada": sum(c["sinais"]["atividade_esperada"] is True for _, c in vetados),
                       "veto_decisivo": len(decisivos), "contexto_vazio": sum(s["fatos"]["contexto_vazio"] for s, _ in com_jev)}
    out.append(M.tabela([{"alertas com faixa de horário no contexto": len(com_faixa), "veto de horário disparou": len(vetados),
                          "veto em atividade esperada no gabarito (veto errado)": resumo["fatos"]["veto_em_esperada"],
                          "veto que mudou a decisão (Noul dizia esperado)": len(decisivos),
                          "contexto vazio": resumo["fatos"]["contexto_vazio"]}]) + "\n")
    if vetados:
        out.append(M.tabela([{"id": c["id"], "gabarito": c["acao"], "esperada (gabarito)": c["sinais"]["atividade_esperada"],
                              "expected_activity": f"{s['nouls']['expected_activity']:.2f}", "mudou a decisão": "sim" if s["veto"] else "não",
                              "fato": " ".join(s["fatos"]["frases"])} for s, c in vetados]) + "\n")

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador)\n")
    linhas = []
    fams = list(dict.fromkeys(familia(c) for c in casos if familia(c) != "fácil / outros")) + ["fácil / outros"]
    for fam in fams:
        idx = [i for i, c in enumerate(casos) if familia(c) == fam]
        if not idx:
            continue
        ac = lambda v: M.acerto([(itens[v][i][0], casos[i]["acao"]) for i in idx])  # noqa: E731
        linhas.append({"família": fam, "n": len(idx), "Jev": ac(PRINCIPAL), "baseline": ac(BASELINE), "Choice única": ac(CHOICE),
                       "erros caros Jev": " ".join(e for i in idx for e in erros_caros(itens[PRINCIPAL][i][0], casos[i])) or "—",
                       "erros caros baseline": " ".join(e for i in idx for e in erros_caros(itens[BASELINE][i][0], casos[i])) or "—",
                       "erros caros Choice": " ".join(e for i in idx for e in erros_caros(itens[CHOICE][i][0], casos[i])) or "—"})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curvas
    out.append("### Cobertura × erro por faixa\n")
    out.append("**Política inteira** (mesmas respostas, outra faixa nos quatro Nouls; informativo no teste)\n")
    out.append(M.tabela(curva(saidas, casos)) + "\n")
    out.append("**Cada Noul sozinho** (cobertura = decidido fora da faixa; acerto entre os decididos)\n")
    linhas = []
    for q, campo in P.SINAL_DO_NOUL.items():
        it = [(s["nouls"][q], c["sinais"][campo]) for s, c in com_jev]
        for nao, sim in GRADE_FAIXA:
            linhas.append({"noul": q, "faixa": f"{nao}–{sim}", **M.faixa_noul(it, nao, sim)})
    out.append(M.tabela(linhas) + "\n")
    out.append("**Choice única: cobertura × erro por confiança** (informativa)\n")
    out.append(M.tabela(M.cobertura_erro([(s["choice"]["confidence"], s["choice"]["choice"] == c["acao"]) for s, c in com_jev], LIMIARES_CONF)) + "\n")

    # --- sonda
    if com_sonda:
        texto, resumo["sonda"] = sonda_injecao(casos, saidas)
        out.append(texto)

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "falhas operacionais (→ fila)": custo["falhas_operacionais"], "perguntas": custo["perguntas"],
                          "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_alerta": round(custo["input_tokens"] / req), "tokens_total": custo["input_tokens"],
                          "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_1000_alertas": f"{1000 * custo['custo_us'] / req:.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")
    if com_sonda:
        sd = resumo["sonda"]
        out.append(f"Sonda de injeção, à parte: {sd['requisicoes']} requisições ({sd['novas']} novas), {sd['tokens']} tokens, US$ {sd['custo_us']:.6f}.\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("`esp`/`crit`/`ind`/`and` = Nouls `expected_activity`, `critical_asset`, `compromise_indication`, `ongoing` "
               "(gabarito entre parênteses: T/F/?); `Choice` = vencedor da pergunta `action` (confiança); `ok` compara a ação do "
               "Jev com o gabarito; `caro` marca E1/E2/E3; `base` = baseline; `urg` = urgência do aviso ao dono.\n")
    tf = lambda g: {True: "T", False: "F", None: "?"}[g]  # noqa: E731
    f2 = lambda v, g: "—" if v is None else f"{v:.2f} ({tf(g)})"  # noqa: E731 — alerta com falha não tem números
    linhas = []
    for s, b, c in zip(saidas, bases, casos):
        n, g = s["nouls"], c["sinais"]
        linhas.append({"id": c["id"], "fam": familia(c), "gab": c["acao"],
                       "esp": f2(n["expected_activity"], g["atividade_esperada"]), "crit": f2(n["critical_asset"], g["ativo_critico"]),
                       "ind": f2(n["compromise_indication"], g["indicio_de_comprometimento"]), "and": f2(n["ongoing"], g["em_andamento"]),
                       "Choice": f"{s['choice']['choice']} ({s['choice']['confidence']:.2f})" if s["choice"] else "—",
                       "ação Jev": s["acao"], "urg": s["urgencia"] or "", "ok": "✓" if s["acao"] == c["acao"] else "✗",
                       "caro": " ".join(erros_caros(s["acao"], c)), "base": b["acao"], "origem": s["origem"], "motivo": s["motivo"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Ação por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES],
                        ["conjunto", *COLUNAS_ACAO]) + "\n")
    out.append("### Sinais, urgência, custo\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"],
                          **{f"{q} ≥0,5 (baseline)": f"{a:.3f} ({r['sinais_baseline'][q]:.3f})" for q, a in r["sinais"].items()},
                          "urgência Jev": r["urgencia"]["jev"], "urgência baseline": r["urgencia"]["baseline"],
                          "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_alerta": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000": f"{1000 * r['custo']['custo_us'] / max(r['custo']['requisicoes'], 1):.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def variantes_do_state(dados: dict) -> str:
    """Só no ajuste: o que os fatos do código compram. Mesmos casos, state com e sem `computed_by_code`; e a política
    com e sem o veto de horário (o veto é código: não depende da resposta)."""
    casos = dados["casos"]
    com, custo_com = rodar(casos, com_fatos=True)
    sem, custo_sem = rodar(casos, com_fatos=False)
    sem_veto = lambda s: s["acao"] if s["origem"] == "falha" else T.politica(  # noqa: E731
        s["sinais"], {**s["fatos"], "veto": False})["acao"]
    linhas = []
    for rotulo, saidas, acao in (("fatos no state + veto (principal)", com, lambda s: s["acao"]),
                                 ("fatos no state, sem veto", com, sem_veto),
                                 ("sem fatos no state, com veto", sem, lambda s: s["acao"]),
                                 ("sem fatos no state, sem veto", sem, sem_veto)):
        b = metricas_acao([(acao(s), c) for s, c in zip(saidas, casos)])["_bruto"]
        linhas.append({"variante": rotulo, "acerto_acao": b["acerto"], "E1": b["e1"], "E2": b["e2"], "E3": b["e3"],
                       "auto_close indevido": b["fechou_indevido"],
                       **{f"{q} ≥0,5": M.acerto([(s["nouls"][q] >= 0.5, c["sinais"][campo]) for s, c in zip(saidas, casos) if s["origem"] != "falha"])
                          for q, campo in P.SINAL_DO_NOUL.items()},
                       "Choice única": M.acerto([(s["choice"]["choice"], c["acao"]) for s, c in zip(saidas, casos) if s["choice"]])})
    pares = [(a, b, c) for a, b, c in zip(com, sem, casos) if a["origem"] != "falha" and b["origem"] != "falha"]
    out = [f"# Variantes do state — triagem-de-alerta (só no ajuste, {len(casos)} alertas)\n",
           f"Gerado por `run.py variantes` em {datetime.date.today().isoformat()} (modo `{os.environ.get('JEV_MODO', 'auto')}`). "
           "Pergunta: os fatos calculados pelo código (`computed_by_code`: dia do alerta e hora × faixa do contexto) ajudam "
           "o Jev, e movem Nouls que não deviam mudar (lição 30)? O veto de horário é código e vale com ou sem os fatos no state.\n",
           M.tabela(linhas) + "\n",
           "## Quanto cada Noul se moveu (com fatos − sem fatos)\n",
           M.tabela([{"noul": q, "média |Δ|": sum(abs(a["nouls"][q] - b["nouls"][q]) for a, b, _ in pares) / max(len(pares), 1),
                      "máx |Δ|": max((abs(a["nouls"][q] - b["nouls"][q]) for a, b, _ in pares), default=0.0),
                      "trocaram de lado em 0,5": sum((a["nouls"][q] >= 0.5) != (b["nouls"][q] >= 0.5) for a, b, _ in pares)}
                     for q in P.NOULS]) + "\n",
           "## Alertas com faixa de horário no contexto (onde o fato existe)\n",
           M.tabela([{"id": c["id"], "gabarito": c["acao"], "esperada": c["sinais"]["atividade_esperada"],
                      "expected com": f"{a['nouls']['expected_activity']:.2f}", "expected sem": f"{b['nouls']['expected_activity']:.2f}",
                      "indício com": f"{a['nouls']['compromise_indication']:.2f}", "indício sem": f"{b['nouls']['compromise_indication']:.2f}",
                      "ação com": a["acao"], "ação sem": b["acao"], "veto": "sim" if a["fatos"]["veto"] else "não"}
                     for a, b, c in pares if a["fatos"]["faixas"]]) + "\n",
           "## Custo\n",
           M.tabela([{"variante": r, "requisicoes": k["requisicoes"], "novas": k["requisicoes"] - k["do_cache"],
                      "tokens_por_alerta": round(k["input_tokens"] / max(k["requisicoes"], 1)), "falhas": k["falhas_operacionais"]}
                     for r, k in (("com fatos", custo_com), ("sem fatos", custo_sem))]) + "\n"]
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; cega ou não, conforme a rodada declarada no README): {h}"


def _congelar() -> dict:
    """Grava o manifesto pela infra comum e anota, só como registro, o hash da infra comum que rodou."""
    if "limites" not in P.CRITERIO_DE_ACEITE:
        sys.exit("congelamento recusado: fixe `perguntas.CRITERIO_DE_ACEITE` (com `limites`) antes de congelar")
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_DE_ACEITE)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    return "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_DE_ACEITE.items() if k != "limites")


def _ler(nome: str) -> dict:
    return json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8"))


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if args == ["variantes"]:
        (AQUI / "resultados-variantes.md").write_text(variantes_do_state(_ler("ajuste")), encoding="utf-8", newline="\n")
        print("resultados-variantes.md gerado")
        return
    if "teste" in conjuntos:
        # O teste só roda com perguntas, política, dados E critério congelados: o manifesto gravado ANTES tem de bater.
        try:
            manifesto = CG.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != P.CRITERIO_DE_ACEITE:
            sys.exit("teste recusado: o critério de aceite mudou desde o congelamento (rode `run.py congelar`)")
        linha = _linha_manifesto(manifesto)
    elif congelar:
        linha = _linha_manifesto(_congelar())
    else:
        h = CG.hashes(AQUI, [a for a in CONGELADOS if not a.startswith("dados/")])
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())
    if args == ["rascunho"]:
        texto, _ = secao_conjunto("rascunho", _ler("rascunho"), com_sonda=False)
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — triagem-de-alerta (encanamento)\n\n{texto}", encoding="utf-8",
                                                     newline="\n")
        print("resultados-rascunho.md gerado")
        return

    com_sonda = congelar or "teste" in conjuntos  # a sonda não roda a cada passada de afinação (orçamento)
    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, _ler(nome), com_sonda)
        partes.append(texto)
    cabecalho = (f"# Resultados — triagem-de-alerta\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas, política e "
                 f"critério: `perguntas.py`; validação, fatos do código, ação e baseline: `triagem.py`. Preço: US$ 0,042 por milhão "
                 f"de tokens de entrada. `contain_now` é proposta para o plantão, não autorização; nada é executado daqui.\n\n"
                 f"Critério de aceite (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    for n, r in resumos.items():
        b = r["variantes"][PRINCIPAL]["_bruto"]
        print(f"  {n}: ação {b['acerto']:.3f} ({b['certos']}/{b['n']}) · E1 {b['e1']} · E2 {b['e2']} · E3 {b['e3']} · "
              f"baseline {r['variantes'][BASELINE]['_bruto']['acerto']:.3f} · Choice {r['variantes'][CHOICE]['_bruto']['acerto']:.3f}")
    falhas = {n: r["custo"]["falhas_operacionais"] for n, r in resumos.items() if r["custo"]["falhas_operacionais"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — esses alertas saíram `queue_tier2` sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists():
        # A primeira execução com o teste É a rodada cega: fica preservada e nunca é reescrita por este script.
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
