"""Roda o imóvel duplicado num conjunto rotulado de pares e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 pares fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py,
                             duplicado.py, run.py, dados/teste.json e o critério de continuar; hash de _comum/ só
                             como registro); o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA
                             execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por par que o código não decide sozinho (cidade, quartos ou vagas diferentes = separados, sem
chamada). Falha operacional (chamada, cache faltando, resposta fora do contrato, anúncio inválido) NÃO aborta
o lote NEM o relatório: aquele par sai `revisar` por `duplicado.julgar_seguro` (no baseline também, por
`baseline_seguro`), fica fora da conferência dos sinais do código e é contado à parte — conjunto com falha não é
medição do Jev. O cache em `cache/` faz rodar de novo custar zero. Bateria do código: `testa_falhas.py`.
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
import duplicado as D  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import Jev  # noqa: E402

ACOES = D.ACOES
RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
# Manifesto com hash do código executado (inclusive este arquivo), dos dados de teste e do critério de aceite.
# `_comum/` entra só como registro: mudar a infra comum não recusa o teste, mas fica anotado.
CONGELADOS = ["perguntas.py", "duplicado.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py", "../_comum/numeros_br.py"]
BASE, SEMPRE, SO_SCORE, SO_NOULS, JEV = "baseline (4 sinais)", "sempre revisa", "só Score", "só Nouls", "Jev (política)"
VARIANTES = [BASE, SEMPRE, SO_SCORE, SO_NOULS, JEV]
GABARITO = {True: "unir", False: "manter_separados", None: "revisar"}
# Grades das curvas (zero chamada nova): a MESMA faixa nos três vetos; depois o sinal forte e o Score.
GRADE_VETOS = [(0.5, 0.5), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9), (0.05, 0.95)]
GRADE_FORTE = [0.5, 0.7, 0.8, 0.9]
GRADE_SCORE = [None, 1.0, 1.5, 1.7, 1.8, 1.9]
LIMIARES_CONF = [0.0, 0.3, 0.5, 0.7, 0.9]
COLUNAS_ACAO = ["variante", "n", "acerto_acao", "DIFERENTE UNIDO (apagaria um imóvel)", "indecidível unido",
                "DUPLICATA SEPARADA", "duplicata unida", "null → revisar", "revisou sem necessidade"]


def familia(c: dict) -> str:
    """Família pela `nota` do rotulador ("difícil: <família> — detalhe"; nas fáceis, o começo da nota).
    O parêntese sai: "unidade diferente (mesmo prédio)" e "(mesma rua)" são a mesma família."""
    nota = c.get("nota") or ""
    dificil = nota.startswith("difícil:")
    corpo = nota[len("difícil:"):].strip() if dificil else nota
    nome = re.sub(r"\s*\(.*?\)", "", re.split(r"\s+[—–]\s+|:\s+", corpo, maxsplit=1)[0]).strip()
    return nome if dificil else f"fácil: {nome}"


def acao_esperada(c: dict) -> str:
    """Gabarito da ação: mesmo imóvel → unir; outro → manter_separados; indecidível (`null`) → revisar."""
    return GABARITO[c["mesmo_imovel"]]


def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    """Um par por vez pelo mesmo invólucro que o consumidor usa (`julgar_seguro`): o código decide o que é dele
    sem chamada; falha operacional vira `revisar` SÓ naquele par. Tudo contado à parte."""
    jev = Jev(AQUI / "cache")  # uma instância por conjunto: latência e tokens separados
    with ThreadPoolExecutor(8) as ex:  # mesmo paralelismo de `Jev.perguntar_varios`
        saidas = list(ex.map(lambda c: D.julgar_seguro(jev, c["a"], c["b"]), casos))
    custo = jev.resumo() or {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
                             "input_tokens": 0, "custo_us": 0.0, "modelos": []}
    for origem in ("codigo", "longo", "falha"):
        custo[origem] = sum(s["origem"] == origem for s in saidas)
    return saidas, custo


def acao_variante(s: dict, c: dict, variante: str) -> str:
    """Ação de cada variante sobre o MESMO par. `só Score` e `só Nouls` reusam os números da mesma resposta; o que
    o código decidiu sem chamada (ou falhou) vale igual nas três variantes do Jev. Par com anúncio inválido conta
    como `revisar` também no baseline (nenhuma variante faz conta com campo inválido)."""
    if variante == BASE:
        return D.baseline_seguro(c["a"], c["b"])["acao"]
    if variante == SEMPRE:
        return "revisar"
    if s["origem"] != "jev" or variante == JEV:
        return s["acao"]
    return D.acao_score(s)[0] if variante == SO_SCORE else D.acao_nouls(s, s["fatos"])[0]


def erro_caro(acao: str, c: dict) -> str:
    """Os erros caros, contados à parte: união sem prova (apagaria um imóvel) e duplicata real dada como outro imóvel."""
    if acao == "unir" and c["mesmo_imovel"] is False:
        return "DIFERENTE UNIDO"
    if acao == "unir" and c["mesmo_imovel"] is None:
        return "indecidível unido"
    if acao == "manter_separados" and c["mesmo_imovel"] is True:
        return "DUPLICATA SEPARADA"
    return ""


def metricas_acao(itens: list[tuple[str, dict]]) -> dict:
    """itens = [(ação da variante, caso)]."""
    caros = Counter(erro_caro(a, c) for a, c in itens)
    n = Counter(c["mesmo_imovel"] for _, c in itens)
    b = {"acerto": M.acerto([(a, acao_esperada(c)) for a, c in itens]),
         "dif_unido": caros["DIFERENTE UNIDO"], "dif": n[False], "nulo_unido": caros["indecidível unido"], "nulos": n[None],
         "dup_separada": caros["DUPLICATA SEPARADA"], "dup": n[True],
         "dup_unida": sum(a == "unir" and c["mesmo_imovel"] is True for a, c in itens),
         "nulo_revisar": sum(a == "revisar" and c["mesmo_imovel"] is None for a, c in itens),
         "revisou_sem": sum(a == "revisar" and c["mesmo_imovel"] is not None for a, c in itens), "decidiveis": n[True] + n[False]}
    return {"n": len(itens), "acerto_acao": b["acerto"],
            "DIFERENTE UNIDO (apagaria um imóvel)": f"{b['dif_unido']}/{b['dif']}",
            "indecidível unido": f"{b['nulo_unido']}/{b['nulos']}",
            "DUPLICATA SEPARADA": f"{b['dup_separada']}/{b['dup']}", "duplicata unida": f"{b['dup_unida']}/{b['dup']}",
            "null → revisar": f"{b['nulo_revisar']}/{b['nulos']}",
            "revisou sem necessidade": f"{b['revisou_sem']}/{b['decidiveis']}", "_bruto": b}


def veredito(variantes: dict, sinais_codigo_ok: bool) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    if not P.CRITERIO_CONTINUAR:
        return "_(critério ainda não fixado em `perguntas.py`)_"
    lim, j, base = P.CRITERIO_CONTINUAR["limites"], variantes[JEV]["_bruto"], variantes[BASE]["_bruto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    div = lambda a, n: a / n if n else 0.0  # noqa: E731
    linhas = [
        {"critério": "1 diferente unido", "medido": f"{j['dif_unido']}/{j['dif']}", "limite": f"≤ {lim['diferente_unido_max']}",
         "passa": ok(j["dif_unido"] <= lim["diferente_unido_max"])},
        {"critério": "2 indecidível unido", "medido": f"{j['nulo_unido']}/{j['nulos']}", "limite": f"≤ {lim['indecidivel_unido_max']}",
         "passa": ok(j["nulo_unido"] <= lim["indecidivel_unido_max"])},
        {"critério": "3 duplicata separada", "medido": f"{j['dup_separada']}/{j['dup']} ({div(j['dup_separada'], j['dup']):.3f})",
         "limite": f"≤ {lim['duplicata_separada_max_fracao']}", "passa": ok(div(j["dup_separada"], j["dup"]) <= lim["duplicata_separada_max_fracao"])},
        {"critério": "4 acerto da ação", "medido": f"{j['acerto']:.3f} (baseline {base['acerto']:.3f})",
         "limite": f"≥ {base['acerto'] + lim['margem_acao']:.3f}", "passa": ok(j["acerto"] >= base["acerto"] + lim["margem_acao"])},
        {"critério": "secundário: nulo → revisar", "medido": f"{j['nulo_revisar']}/{j['nulos']}", "limite": "todos",
         "passa": ok(j["nulo_revisar"] == j["nulos"])},
        {"critério": "secundário: revisou sem necessidade", "medido": f"{j['revisou_sem']}/{j['decidiveis']} ({div(j['revisou_sem'], j['decidiveis']):.3f})",
         "limite": f"≤ {lim['revisou_sem_necessidade_max']}", "passa": ok(div(j["revisou_sem"], j["decidiveis"]) <= lim["revisou_sem_necessidade_max"])},
        {"critério": "secundário: sinais numéricos do código", "medido": "100%" if sinais_codigo_ok else "DIVERGE", "limite": "100% (senão é bug)",
         "passa": ok(sinais_codigo_ok)},
    ]
    return M.tabela(linhas)


def matriz(pares: list[tuple[str, str]]) -> str:
    cont = Counter((g, p) for p, g in pares)
    return M.tabela([{"gabarito ↓ / previsto →": g, **{a: cont[(g, a)] for a in ACOES}} for g in ACOES])


def endereco_previsto(s: dict) -> bool | None:
    """`mesmo_endereco` de três valores a partir dos dois Nouls (corte 0,5): conflito → False; mesmo → True;
    nenhum dos dois → None (um dos anúncios não cita nada comparável)."""
    mesmo, conflito = s["nouls"]["same_building_or_street"], s["nouls"]["address_conflict"]
    if conflito >= 0.5 and conflito >= mesmo:
        return False
    return True if mesmo >= 0.5 else None


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
    acoes = [D.compor(s, s["fatos"])["acao"] if s["origem"] == "jev" else s["acao"] for s in saidas]
    auto = [(a, c) for a, c in zip(acoes, casos) if a != "revisar"]
    caros = Counter(erro_caro(a, c) for a, c in auto)
    return {**rotulo, "cobertura_auto": len(auto) / len(casos),
            "erro_automatico": (sum(a != acao_esperada(c) for a, c in auto) / len(auto)) if auto else float("nan"),
            "diferentes unidos": caros["DIFERENTE UNIDO"], "indecidíveis unidos": caros["indecidível unido"],
            "duplicatas separadas": caros["DUPLICATA SEPARADA"],
            "duplicatas unidas": sum(a == "unir" and c["mesmo_imovel"] is True for a, c in auto), "n_auto": len(auto)}


def curvas(saidas: list[dict], casos: list[dict]) -> tuple[list[dict], list[dict]]:
    """Cobertura automática (não foi a `revisar`) × erro entre automáticos, mexendo num parâmetro por vez."""
    vetos = [_linha_curva({"faixa (3 vetos)": "atual (perguntas.py)"}, saidas, casos)]
    for faixa in GRADE_VETOS:
        with _com(FAIXA={**P.FAIXA, **{q: faixa for q in P.VETOS}}):
            vetos.append(_linha_curva({"faixa (3 vetos)": f"{faixa[0]}–{faixa[1]}"}, saidas, casos))
    uniao = [_linha_curva({"parâmetro": "atual (perguntas.py)", "valor": "—"}, saidas, casos)]
    for sim in GRADE_FORTE:
        with _com(FAIXA={**P.FAIXA, "shared_distinctive_details": (P.FAIXA["shared_distinctive_details"][0], sim)}):
            uniao.append(_linha_curva({"parâmetro": "`sim` do sinal forte", "valor": sim}, saidas, casos))
    for corte in GRADE_SCORE:
        with _com(USAR_SCORE=corte is not None, SCORE_UNIR_MIN=corte if corte is not None else P.SCORE_UNIR_MIN):
            uniao.append(_linha_curva({"parâmetro": "Score mínimo para unir", "valor": "sem Score" if corte is None else corte}, saidas, casos))
    return vetos, uniao


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custo = rodar(casos)
    itens = {v: [(acao_variante(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    cont = Counter(c["mesmo_imovel"] for c in casos)
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    resumo = {"n": len(casos), "dificeis": dificeis, "nulos": cont[None], "custo": custo,
              "variantes": {v: metricas_acao(itens[v]) for v in VARIANTES}}
    f2 = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731 — par decidido pelo código ou com falha não tem números
    faixa_txt = lambda xs: "—" if not xs else f"{min(xs):.2f}–{max(xs):.2f}"  # noqa: E731

    out = [f"## Conjunto `{nome}` — {len(casos)} pares (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{cont[True]} duplicatas, {cont[False]} diferentes, {cont[None]} indecidíveis; {dificeis} difíceis\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if custo["falha"]:
        out.append(f"> **{custo['falha']} falha(s) operacional(is)** neste conjunto: esses pares saíram `revisar` sem resposta do "
                   "Jev. **As métricas abaixo não são medição do Jev** — rode de novo.\n")

    # --- sinais do código (têm de bater 100% com o gabarito: são conta). Os fatos são os que `julgar_seguro` já
    # calculou: par com anúncio inválido não tem fatos (None), não é recalculado e fica fora desta conferência.
    calc = [(s["fatos"], c) for s, c in zip(saidas, casos)]
    validos = [(f, c) for f, c in calc if f is not None]
    resumo["entrada_invalida"] = len(casos) - len(validos)
    if resumo["entrada_invalida"]:
        out.append(f"> **{resumo['entrada_invalida']} par(es) com entrada inválida** (anúncio sem campo ou com número inválido; "
                   f"{', '.join(c['id'] for f, c in calc if f is None)}): contam como `revisar` no Jev E no baseline, já estão "
                   "entre as falhas operacionais e ficam fora da conferência dos sinais do código.\n")
    area = sum(f["area_within_3_percent"] == c["sinais"]["mesma_area"] for f, c in validos)
    preco = sum(f["price_within_5_percent"] == c["sinais"]["mesmo_preco"] for f, c in validos)
    outra = [(f, c) for f, c in validos if not (f["same_bedrooms"] and f["same_parking_spaces"])]
    planta_cod = sum(c["sinais"]["mesma_planta"] is False for _, c in outra)
    sem_chamada = [(s, c) for s, c in zip(saidas, casos) if s["origem"] == "codigo"]
    cod_certo = sum(c["mesmo_imovel"] is False for _, c in sem_chamada)
    codigo_ok = area == preco == len(validos) and planta_cod == len(outra)
    resumo["codigo_ok"] = codigo_ok

    # --- ação
    out.append("### Ação (3 classes) — métrica principal, baseline × sempre revisa × Jev nos mesmos pares\n")
    out.append("Gabarito da ação: `mesmo_imovel` true → `unir`; false → `manter_separados`; null → `revisar`. "
               "**DIFERENTE UNIDO** = par de imóveis diferentes que saiu `unir` (a união apagaria um imóvel do catálogo). "
               "`indecidível unido` = gabarito `null` que saiu `unir` (união sem prova). **DUPLICATA SEPARADA** = mesmo imóvel que "
               "saiu `manter_separados` (a duplicata fica e ninguém revisa). `baseline` = mesmos bairro/cidade + quartos + vagas + "
               "área ±3% + preço ±5% ⇒ unir, senão separados. `sempre revisa` = zero erro caro, 100% dos pares a humano. "
               "`só Score` = arredondamento do Score (cortes 0,5 e 1,5), como na receita; `só Nouls` = política sem o Score; "
               "`Jev (política)` = Nouls + Score como segunda leitura da união. As três leem a MESMA resposta.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES], COLUNAS_ACAO) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(resumo["variantes"], codigo_ok) + "\n")
    for v in (JEV, SO_NOULS, SO_SCORE, BASE):
        out.append(f"**Matriz de confusão — {v}** (linhas = gabarito, colunas = previsto)\n")
        out.append(matriz([(a, acao_esperada(c)) for a, c in itens[v]]) + "\n")
    caros = [{"id": c["id"], "variante": v, "erro": erro_caro(a, c), "família": familia(c)}
             for v in (JEV, SO_NOULS, SO_SCORE, BASE) for a, c in itens[v] if erro_caro(a, c)]
    out.append("**Erros caros, par a par** (todas as variantes)\n")
    out.append((M.tabela(caros) if caros else "_(nenhum)_") + "\n")

    out.append("### Sinais numéricos do código — têm de bater 100% com o gabarito (senão é bug)\n")
    out.append(M.tabela([
        {"sinal": "`mesma_area` (±3%)", "certos": f"{area}/{len(validos)}", "ok": "✓" if area == len(validos) else "**BUG**"},
        {"sinal": "`mesmo_preco` (±5%)", "certos": f"{preco}/{len(validos)}", "ok": "✓" if preco == len(validos) else "**BUG**"},
        {"sinal": "quartos ou vagas diferentes ⇒ `mesma_planta` false", "certos": f"{planta_cod}/{len(outra)}",
         "ok": "✓" if planta_cod == len(outra) else "**BUG**"},
        {"sinal": "decidido pelo código sem chamada (cidade, quartos ou vagas) ⇒ gabarito false",
         "certos": f"{cod_certo}/{len(sem_chamada)}", "ok": "✓" if cod_certo == len(sem_chamada) else "✗ (erro da REGRA, não da conta)"},
    ]) + "\n")
    explic = [(f, c) for f, c in validos if not f["area_within_3_percent"] and f["local"] != "distinto"
              and f["same_bedrooms"] and f["same_parking_spaces"]]
    out.append(f"Área fora da tolerância entre os pares que foram ao Jev: {len(explic)}; conciliada pelo código pela relação total × "
               f"privativa rotulada no texto: {sum(f['area_gap_explained_by_second_figure'] for f, _ in explic)} "
               f"(destes, duplicatas reais: {sum(f['area_gap_explained_by_second_figure'] and c['mesmo_imovel'] is True for f, c in explic)}); "
               f"indefinida (uma metragem do texto bate, mas sem rótulo de área da unidade → não concilia): "
               f"{sum(f['area'] == 'indefinida' for f, _ in explic)}.\n")
    indef = [(s, c) for s, c in zip(saidas, casos) if s["fatos"] is not None and s["fatos"]["local"] == "indefinido"]
    out.append(f"Bairro que difere no texto dentro da mesma cidade (não prova outro imóvel: o código não separa sozinho, o par vai ao "
               f"Jev e não pode sair `unir`): {len(indef)}"
               + (" — " + "; ".join(f"{c['id']} → `{s['acao']}` (gabarito `{acao_esperada(c)}`)" for s, c in indef) if indef else "") + ".\n")

    com_jev = [(s, c) for s, c in zip(saidas, casos) if s["origem"] == "jev"]  # só estes têm números do Jev

    # --- sinais de texto contra o gabarito
    out.append(f"### Sinais de texto (Nouls) contra os `sinais` do gabarito — {len(com_jev)} pares que foram ao Jev\n")
    out.append("`mesmo_endereco` tem três valores (true / false / `null` = um dos anúncios não cita prédio nem rua): "
               "`same_building_or_street` mede o true, `address_conflict` mede o false. `mesma_planta` false, entre os pares "
               "que chegam ao Jev (quartos e vagas iguais), é `layout_contradiction`. Acerto com corte 0,5; `cobertura` = fração "
               "decidida fora da faixa de dúvida; `revisao` = casos dentro dela.\n")
    sub = {"same_building_or_street": [(s["nouls"]["same_building_or_street"], c["sinais"]["mesmo_endereco"] is True) for s, c in com_jev],
           "address_conflict": [(s["nouls"]["address_conflict"], c["sinais"]["mesmo_endereco"] is False) for s, c in com_jev],
           "layout_contradiction": [(s["nouls"]["layout_contradiction"], c["sinais"]["mesma_planta"] is False) for s, c in com_jev]}
    linhas = []
    for q, it in sub.items():
        nao, sim = P.FAIXA[q]
        linhas.append({"noul": q, "positivos": sum(g for _, g in it), "acerto": M.acerto([(v >= 0.5, g) for v, g in it]),
                       "faixa": f"{nao}–{sim}", **M.faixa_noul(it, nao, sim), "brier": M.brier(it)})
    resumo["nouls"] = {l["noul"]: l["acerto"] for l in linhas}
    out.append(M.tabela(linhas) + "\n")
    end = Counter((c["sinais"]["mesmo_endereco"], endereco_previsto(s)) for s, c in com_jev)
    end_certo = sum(n for (g, p), n in end.items() if g == p)
    resumo["endereco"] = end_certo / len(com_jev) if com_jev else float("nan")
    out.append(f"**`mesmo_endereco` em três valores** (os dois Nouls juntos, corte 0,5): {end_certo}/{len(com_jev)} certos\n")
    out.append(M.tabela([{"gabarito ↓ / previsto →": str(g), **{str(p): end[(g, p)] for p in (True, False, None)}} for g in (True, False, None)]) + "\n")
    planta = [((f["same_bedrooms"] and f["same_parking_spaces"]) and (s["nouls"]["layout_contradiction"] is None or s["nouls"]["layout_contradiction"] < 0.5),
               c["sinais"]["mesma_planta"]) for (f, c), s in zip(calc, saidas) if s["origem"] != "falha"]
    resumo["planta"] = M.acerto(planta)
    out.append(f"**`mesma_planta` composta** (quartos e vagas iguais pelo CÓDIGO e nenhum cômodo estrutural contradito pelo Noul; par "
               f"decidido pelo código sem chamada entra só com a parte do código): {M.acerto(planta):.3f} (n = {len(planta)})\n")

    # --- Nouls sem campo próprio no gabarito
    out.append("### Nouls sem campo próprio no gabarito — valores por grupo\n")
    grupos = [("fixed_contradiction", "família detalhe fixo contradiz", lambda c: familia(c) == "detalhe fixo contradiz"),
              ("state_contradiction", "família mobiliado × vazio", lambda c: familia(c) == "mobiliado × vazio"),
              ("shared_distinctive_details", "duplicatas reais (true)", lambda c: c["mesmo_imovel"] is True),
              ("shared_distinctive_details", "família sem detalhe distintivo", lambda c: familia(c) == "sem detalhe distintivo")]
    linhas = []
    for q, rotulo, dentro in grupos:
        a = [s["nouls"][q] for s, c in com_jev if dentro(c)]
        b = [s["nouls"][q] for s, c in com_jev if not dentro(c)]
        nao, sim = P.FAIXA[q]
        linhas.append({"noul": q, "grupo": rotulo, "n_grupo": len(a), "mín–máx no grupo": faixa_txt(a), "grupo ≥ sim": sum(x >= sim for x in a),
                       "grupo ≤ nao": sum(x <= nao for x in a), "mín–máx fora": faixa_txt(b), "fora ≥ sim": sum(x >= sim for x in b),
                       "fora ≤ nao": sum(x <= nao for x in b), "faixa": f"{nao}–{sim}"})
    out.append(M.tabela(linhas) + "\n")

    # --- Score
    out.append("### Score `same_listing` (0 = diferentes · 1 = não dá para saber · 2 = a mesma unidade)\n")
    linhas = []
    for g in (True, None, False):
        xs = [s["score"] for s, c in com_jev if c["mesmo_imovel"] is g]
        linhas.append({"gabarito `mesmo_imovel`": str(g), "esperado": {True: 2, None: 1, False: 0}[g], "n": len(xs),
                       "média": sum(xs) / len(xs) if xs else float("nan"), "mín–máx": faixa_txt(xs),
                       "→ 0 (≤ 0,5)": sum(x <= P.SCORE_ARREDONDA[0] for x in xs),
                       "→ 1": sum(P.SCORE_ARREDONDA[0] < x < P.SCORE_ARREDONDA[1] for x in xs),
                       "→ 2 (≥ 1,5)": sum(x >= P.SCORE_ARREDONDA[1] for x in xs),
                       f"≥ {P.SCORE_UNIR_MIN} (mínimo da política)": sum(x >= P.SCORE_UNIR_MIN for x in xs)})
    out.append(M.tabela(linhas) + "\n")
    out.append("**Cobertura × erro por confiança do Score** (acerto = arredondamento igual ao gabarito)\n")
    out.append(M.tabela(M.cobertura_erro([(s["score_conf"], D.acao_score(s)[0] == acao_esperada(c)) for s, c in com_jev], LIMIARES_CONF)) + "\n")
    muda = [(s, c) for s, c in com_jev if D.acao_nouls(s, s["fatos"])[0] != s["acao"]]
    so_n, so_s = resumo["variantes"][SO_NOULS]["_bruto"], resumo["variantes"][SO_SCORE]["_bruto"]
    resumo["score_muda"] = len(muda)
    out.append(f"**O Score acrescenta algo aos Nouls?** Na política ele só pode tirar uma união. Mudou a decisão dos Nouls em "
               f"{len(muda)} par(es): {sum(c['mesmo_imovel'] is not True for _, c in muda)} união(ões) sem prova evitada(s), "
               f"{sum(c['mesmo_imovel'] is True for _, c in muda)} união(ões) certa(s) mandada(s) a `revisar`"
               + (f" ({', '.join(c['id'] for _, c in muda)})" if muda else "") + ". Sozinho (arredondamento): "
               f"{so_s['dif_unido']} diferente(s) e {so_s['nulo_unido']} indecidível(is) unidos, {so_s['dup_separada']} duplicata(s) separada(s), "
               f"acerto {so_s['acerto']:.3f}; só Nouls: {so_n['dif_unido']}, {so_n['nulo_unido']}, {so_n['dup_separada']}, acerto {so_n['acerto']:.3f}.\n")

    # --- famílias
    out.append("### Por família (pela `nota` do rotulador)\n")
    linhas = []
    for fam in sorted(dict.fromkeys(familia(c) for c in casos), key=lambda x: (x.startswith("fácil"), x)):
        grupo = [(s, c) for s, c in zip(saidas, casos) if familia(c) == fam]
        base = [D.baseline_seguro(c["a"], c["b"])["acao"] for _, c in grupo]
        linhas.append({"família": fam, "gabarito": "/".join(sorted({str(c["mesmo_imovel"]) for _, c in grupo})), "n": len(grupo),
                       "ação Jev": M.acerto([(s["acao"], acao_esperada(c)) for s, c in grupo]),
                       "ação baseline": M.acerto([(b, acao_esperada(c)) for b, (_, c) in zip(base, grupo)]),
                       "Jev → revisar": sum(s["acao"] == "revisar" for s, _ in grupo),
                       "sem chamada (código)": sum(s["origem"] == "codigo" for s, _ in grupo),
                       "erro caro Jev": sum(bool(erro_caro(s["acao"], c)) for s, c in grupo),
                       "erro caro baseline": sum(bool(erro_caro(b, c)) for b, (_, c) in zip(base, grupo))})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curvas
    vetos, uniao = curvas(saidas, casos)
    out.append("### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)\n")
    out.append("`cobertura_auto` = par que não foi a `revisar` (inclui os decididos pelo código sem chamada). "
               "**Vetos** (a mesma faixa em `address_conflict`, `layout_contradiction` e `fixed_contradiction`):\n")
    out.append(M.tabela(vetos) + "\n")
    out.append("**O que autoriza a união** (um parâmetro por vez, o resto como em `perguntas.py`):\n")
    out.append(M.tabela(uniao) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"pares": len(casos), "requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "sem chamada (código decide)": custo["codigo"], "longos (sem chamada)": custo["longo"],
                          "falhas operacionais (→ revisar)": custo["falha"], "perguntas": custo["perguntas"],
                          "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_requisicao": round(custo["input_tokens"] / req),
                          "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_par": f"{custo['custo_us'] / len(casos):.7f}",
                          "US$_por_1000_pares": f"{1000 * custo['custo_us'] / len(casos):.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("`end`/`conf` = Nouls `same_building_or_street` e `address_conflict`; `planta` = `layout_contradiction`; `fixo` = "
               "`fixed_contradiction`; `estado` = `state_contradiction`; `comum` = `shared_distinctive_details`; `score` = "
               "`same_listing` (confiança); `área`/`preço` = fatos do código (`expl.` = fora de ±3% mas conciliada pela relação total × "
               "privativa rotulada no texto; `indef.` = uma metragem do texto bate, sem rótulo: não concilia); `ok` compara a ação do Jev "
               "com o gabarito; `caro` marca o erro caro; `base` = baseline; `—` = par decidido pelo código sem chamada, ou sem fatos "
               "(entrada inválida).\n")
    linhas = []
    for (s, c), (f, _) in zip(zip(saidas, casos), calc):
        gab, n = acao_esperada(c), s["nouls"]
        linhas.append({"id": c["id"], "fam": familia(c), "gab": gab, "end": f2(n["same_building_or_street"]), "conf": f2(n["address_conflict"]),
                       "planta": f2(n["layout_contradiction"]), "fixo": f2(n["fixed_contradiction"]), "estado": f2(n["state_contradiction"]),
                       "comum": f2(n["shared_distinctive_details"]),
                       "score": "—" if s["score"] is None else f"{s['score']:.2f} ({s['score_conf']:.2f})",
                       "área": "—" if f is None else {"dentro": "ok", "conciliada": "expl.", "indefinida": "indef."}.get(f["area"], "✗"),
                       "preço": "—" if f is None else "ok" if f["price_within_5_percent"] else "✗",
                       "ação Jev": s["acao"], "ok": "✓" if s["acao"] == gab else "✗", "caro": erro_caro(s["acao"], c),
                       "base": D.baseline_seguro(c["a"], c["b"])["acao"], "motivo": s["motivo"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Ação por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES],
                        ["conjunto", *COLUNAS_ACAO]) + "\n")
    out.append("### Sinais, custo\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"], "nulos": r["nulos"],
                          **{f"{q} ≥0,5": a for q, a in r["nouls"].items()},
                          "mesmo_endereco (3 valores)": r["endereco"], "mesma_planta composta": r["planta"],
                          "sinais do código 100%": "✓" if r["codigo_ok"] else "**BUG**",
                          "Score mudou a decisão": r["score_muda"],
                          "requisições": r["custo"]["requisicoes"], "sem chamada": r["custo"]["codigo"],
                          "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_requisicao": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000_pares": f"{1000 * r['custo']['custo_us'] / r['n']:.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
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
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — imovel-duplicado (encanamento)\n\n{texto}", encoding="utf-8",
                                                     newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — imovel-duplicado\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas e política: "
                 f"`perguntas.py`; fatos do código, validação, ação e baseline: `duplicado.py`. Preço: US$ 0,042 por milhão de tokens "
                 f"de entrada. Teto do par: {P.TETO_CARACTERES} caracteres (acima → revisar, sem chamada). `unir` é proposta: nada é apagado.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: r["custo"]["falha"] for n, r in resumos.items() if r["custo"]["falha"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — esses pares saíram `revisar` sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists() and not falhas:
        # A primeira execução COMPLETA com o teste É a rodada cega: fica preservada e nunca é reescrita por este
        # script. Execução com falha operacional não é medição (os pares que falharam não têm resposta do Jev):
        # não vira rodada 1; rodar de novo só refaz as chamadas que faltaram (o resto vem do cache).
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
