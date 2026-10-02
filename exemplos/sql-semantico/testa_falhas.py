"""Bateria do código do SQL semântico — roda sem chave e sem rede (`python testa_falhas.py`).

O que se testa aqui é código nosso, não o modelo (dublê no lugar do Jev); nenhum número desta bateria é medição.
  A. falha operacional — resposta falsa (bool no lugar de número, string, NaN, fora de [0,1], ID faltando, `type`
     trocado, `answers` ausente, resposta que não é objeto), exceção de rede simulada ou entrada inválida:
     `avaliar_seguro` devolve `indecidivel` com motivo "falha operacional" para AQUELA linha, nunca `verdadeiro`
     nem `falso`; `avaliar` (baixo nível) levanta; o lote (`run.rodar`) não aborta; resposta inválida é tirada do
     cache (`jev.invalidar`) e falha de chamada não é;
  B. condição sem parte semântica — resolvida só pelo filtro, ZERO chamada (o dublê levanta se for chamado);
  C. filtro com campo nulo, ausente ou de tipo errado — nulo/ausente é `falso` sem chamada (LEIA-ME, regra 4);
     tipo errado é falha operacional (`indecidivel`), nunca `verdadeiro`;
  D. separação da condição — parênteses com crase, cláusula solta, dois filtros, `data em`, E/OU, sujeito herdado;
  E. política — grade de `decidir`: faixas de `stated`, válvula do `hinted`, combinação E/OU (regra 5 do LEIA-ME)
     sobre todos os estados; texto acima do teto não vai ao Jev;
  F. revisão do Codex (2026-10-02, achados 1–4) — cláusula estruturada inválida (operador `<`, campo desconhecido,
     valor fora do domínio, crase sem par) = condição inválida → `indecidivel` em TODAS as linhas, com o erro, nunca
     `verdadeiro`, zero chamada; resíduo só de pontuação = semântica vazia; válvula da pista por cláusula antes de
     combinar (SQ-T14/OB-062) com a negação do E preservada; baseline e previsão de orçamento protegidos (campo com
     tipo errado e condição inválida não abortam o relatório).
"""
from __future__ import annotations

import copy
import itertools
import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import perguntas as P  # noqa: E402
import run as R  # noqa: E402
import sql as S  # noqa: E402

NAO, SIM = P.FAIXA["stated"]
BAIXO, DUVIDA, ALTO = NAO / 2, (NAO + SIM) / 2, (SIM + 1) / 2
LINHA = {"id": "X1", "texto": "Cliente tem dois cachorros e procura casa com quintal.",
         "campos": {"data": "2026-08-01", "canal": "whatsapp", "finalidade": "compra", "orcamento": 400000, "visitas": 1, "etapa": "visita"}}
SEP = S.separar("Clientes com animal de estimação.")
SEP_COMPOSTA = S.separar("Clientes com urgência E com animal de estimação.")


def resposta(perguntas: dict | None = None, **valores: float) -> dict:
    """Resposta VÁLIDA no formato da API. Sem argumentos: tudo baixo → `falso` (se a validação deixar passar uma
    resposta corrompida, a bateria vê `falso` ou `verdadeiro` em vez de `indecidivel`)."""
    qs = perguntas or P.perguntas_de(SEP["partes"])
    return {"model": "duble", "answers": {q: {"type": "noul", "noul": valores.get(q, BAIXO)} for q in qs}}


class Duble:
    """Jev de mentira: devolve a resposta dada ou levanta a exceção dada; por texto, se `por_texto`. Conta chamadas e
    invalidações."""

    def __init__(self, padrao=None, por_texto: dict | None = None, invalidar_quebra: bool = False):
        self.padrao = padrao if padrao is not None else resposta()
        self.por_texto, self.invalidar_quebra = por_texto or {}, invalidar_quebra
        self.chamadas, self.invalidados = 0, 0

    def perguntar(self, state, questions):
        self.chamadas += 1
        saida = self.por_texto.get(state["note"], self.padrao)
        if isinstance(saida, Exception):
            raise saida
        return saida

    def invalidar(self, state, questions) -> bool:
        if self.invalidar_quebra:
            raise OSError("disco")
        self.invalidados += 1
        return True

    def resumo(self) -> dict:
        return {}


class ErroHTTP(Exception):
    """Faz o papel do erro de status do SDK (503, 429…) sem depender da classe dele."""


def _mexe(caminho: list, valor=None, apaga: bool = False):
    def aplica(r: dict) -> dict:
        alvo = r
        for chave in caminho[:-1]:
            alvo = alvo[chave]
        if apaga:
            del alvo[caminho[-1]]
        else:
            alvo[caminho[-1]] = valor
        return r
    return aplica


RESPOSTAS_FALSAS = [
    ("Noul bool False no lugar de número (viraria 0.0 → falso)", _mexe(["answers", "stated", "noul"], False)),
    ("Noul bool True (viraria 1.0 → verdadeiro)", _mexe(["answers", "stated", "noul"], True)),
    ("Noul string", _mexe(["answers", "stated", "noul"], "0.95")),
    ("Noul None", _mexe(["answers", "hinted", "noul"], None)),
    ("Noul NaN", _mexe(["answers", "stated", "noul"], math.nan)),
    ("Noul infinito", _mexe(["answers", "stated", "noul"], math.inf)),
    ("Noul fora de [0, 1] (1.5)", _mexe(["answers", "stated", "noul"], 1.5)),
    ("Noul negativo", _mexe(["answers", "hinted", "noul"], -0.1)),
    ("Noul sem o campo `noul`", _mexe(["answers", "stated", "noul"], apaga=True)),
    ("ID `stated` faltando", _mexe(["answers", "stated"], apaga=True)),
    ("ID `hinted` faltando", _mexe(["answers", "hinted"], apaga=True)),
    ("discriminador `type` trocado (Noul que volta como choice)", _mexe(["answers", "stated", "type"], "choice")),
    ("resposta de um ID que não é objeto", _mexe(["answers", "stated"], 0.9)),
    ("`answers` vazio", _mexe(["answers"], {})),
    ("`answers` None", _mexe(["answers"], None)),
    ("sem `answers`", _mexe(["answers"], apaga=True)),
]
RESPOSTAS_INTEIRAS = [("resposta None", None), ("resposta lista", []), ("resposta string", "ok"), ("resposta {}", {})]
EXCECOES = [
    ("timeout", TimeoutError("tempo esgotado")),
    ("conexão recusada", ConnectionError("sem rede")),
    ("erro HTTP 503", ErroHTTP("503 Service Unavailable")),
    ("erro HTTP 429", ErroHTTP("429 Too Many Requests")),
    ("cache faltando no modo gravado", RuntimeError("resposta não gravada no cache")),
    ("erro não previsto dentro do cliente", KeyError("usage")),
]
ENTRADAS = [("texto vazio", ""), ("texto só com espaço", "   "), ("texto None", None), ("texto não textual", 123)]


def _linha(texto="…", **campos) -> dict:
    return {"id": "X", "texto": texto, "campos": {**LINHA["campos"], **campos}}


def _confere_falha(nome: str, jev, linha: dict, etapa: str, falhas: list, sep: dict = SEP, invalida: bool | None = None) -> None:
    """Uma falha: o invólucro devolve `indecidivel` marcado; o baixo nível levanta; o cache é (ou não) invalidado."""
    d = S.avaliar_seguro(jev, sep, linha)
    if d["saida"] != "indecidivel" or not d.get("falha") or d["por"] != "falha" \
            or not d["motivo"].startswith(f"falha operacional: {etapa} ("):
        falhas.append(f"A {nome}: avaliar_seguro devolveu {d['saida']!r} / {d['motivo']!r}")
    if invalida is not None and bool(jev.invalidados) != invalida:
        falhas.append(f"A {nome}: invalidações {jev.invalidados} (esperado {'1' if invalida else '0'})")
    try:
        S.avaliar(jev, sep, linha)
        falhas.append(f"A {nome}: avaliar (baixo nível) não levantou erro")
    except Exception:  # noqa: BLE001 — qualquer exceção serve: o ponto é não devolver decisão
        pass


def bateria_falhas(falhas: list) -> int:
    n = 0
    base = S.avaliar_seguro(Duble(), SEP, LINHA)
    assert base["saida"] == "falso" and base["por"] == "jev", f"o dublê válido tem de dar `falso` pelo Jev: {base}"
    for nome, corrompe in RESPOSTAS_FALSAS:
        _confere_falha(nome, Duble(corrompe(copy.deepcopy(resposta()))), LINHA, "resposta inválida", falhas, invalida=True)
        n += 1
    for nome, inteira in RESPOSTAS_INTEIRAS:
        jev = Duble()
        jev.padrao = inteira  # direto: o construtor trocaria None pela resposta válida
        _confere_falha(nome, jev, LINHA, "resposta inválida", falhas, invalida=True)
        n += 1
    for nome, erro in EXCECOES:
        _confere_falha(nome, Duble(erro), LINHA, "chamada", falhas, invalida=False)  # nada foi gravado: nada a invalidar
        n += 1
    for nome, texto in ENTRADAS:
        _confere_falha(nome, Duble(), _linha(texto), "entrada inválida", falhas)
        n += 1
    # invalidar que quebra não muda o desfecho
    _confere_falha("invalidar que quebra", Duble(_mexe(["answers", "stated", "noul"], True)(resposta()), invalidar_quebra=True),
                   LINHA, "resposta inválida", falhas)
    n += 1
    # o lote não aborta: `run.rodar` com o dublê; só as linhas com falha saem `indecidivel`
    linhas = [_linha(f"t{i}") for i in range(6)]
    duble = Duble(por_texto={"t1": TimeoutError(), "t3": _mexe(["answers", "stated", "noul"], False)(resposta()),
                             "t4": resposta(stated=ALTO)})
    jev_real, R.Jev = R.Jev, lambda pasta: duble
    try:
        saidas, custo = R.rodar([{"id": "C1", "condicao": "Clientes com animal de estimação."}], linhas)
    finally:
        R.Jev = jev_real
    acoes = [s["saida"] for s in saidas["C1"]]
    if acoes != ["falso", "indecidivel", "falso", "indecidivel", "verdadeiro", "falso"] or custo["falhas_operacionais"] != 2:
        falhas.append(f"A lote: saídas {acoes}, falhas contadas {custo['falhas_operacionais']}")
    return n + 1


class NuncaChama(Duble):
    def perguntar(self, state, questions):
        raise AssertionError("o Jev foi chamado para condição só de campos")


def bateria_sem_semantica(falhas: list) -> int:
    sep = S.separar("(`canal` = whatsapp)")
    if sep["semantica"] or sep["partes"] or sep["filtros"] != [("canal", "=", "whatsapp")]:
        falhas.append(f"B separar sem semântica: {sep}")
    for linha, esperado in ((_linha(canal="whatsapp"), "verdadeiro"), (_linha(canal="email"), "falso")):
        for f in (S.avaliar, S.avaliar_seguro):
            d = f(NuncaChama(), sep, linha)
            if d["saida"] != esperado or d["por"] != "filtro":
                falhas.append(f"B {f.__name__} canal {linha['campos']['canal']}: {d}")
    return 4


def bateria_filtro(falhas: list) -> int:
    sep = S.separar("Clientes com pet (`orcamento` <= 500000).")
    n = 0
    for nome, campos, esperado in (("orcamento nulo", {"orcamento": None}, "falso"), ("orcamento acima", {"orcamento": 600000}, "falso"),
                                   ("orcamento igual", {"orcamento": 500000}, "jev"), ("orcamento abaixo", {"orcamento": 1}, "jev")):
        d = S.avaliar_seguro(Duble(resposta(stated=ALTO)), sep, _linha(**campos))
        got = d["por"] if d["por"] == "jev" else d["saida"]
        if got != esperado:
            falhas.append(f"C {nome}: {d}")
        n += 1
    linha = _linha()
    del linha["campos"]["orcamento"]
    d = S.avaliar_seguro(NuncaChama(), sep, linha)
    if d["saida"] != "falso" or d["por"] != "filtro":
        falhas.append(f"C campo ausente: {d}")
    d = S.avaliar_seguro(NuncaChama(), sep, {"id": "X", "texto": "…", "campos": None})
    if d["saida"] != "falso" or d["por"] != "filtro":
        falhas.append(f"C campos None: {d}")
    for nome, campos, cond in (("orcamento string", {"orcamento": "500000"}, None), ("orcamento bool", {"orcamento": True}, None),
                               ("data número", {"data": 20260801}, "Clientes com pet (`data` em 2026-08)."),
                               ("canal número", {"canal": 1}, "Clientes com pet (`canal` = whatsapp).")):
        sep2 = sep if cond is None else S.separar(cond)
        _confere_falha(f"C {nome}", NuncaChama(), _linha(**campos), "filtro", falhas, sep=sep2)
        n += 1
    # `data em` e `visitas >=`
    sep3 = S.separar("Clientes com pet (`data` em 2026-09, `visitas` >= 2).")
    if sep3["filtros"] != [("data", "em", "2026-09"), ("visitas", ">=", "2")]:
        falhas.append(f"C separar dois filtros: {sep3['filtros']}")
    for campos, esperado in (({"data": "2026-09-30", "visitas": 2}, True), ({"data": "2026-08-30", "visitas": 2}, False),
                             ({"data": "2026-09-01", "visitas": 1}, False)):
        if S.passa_filtro({**LINHA["campos"], **campos}, sep3["filtros"]) != esperado:
            falhas.append(f"C passa_filtro {campos}: esperado {esperado}")
        n += 1
    return n + 2


def bateria_separar(falhas: list) -> int:
    casos = [
        ("Clientes com pet (`canal` = whatsapp).", "Clientes com pet.", [("canal", "=", "whatsapp")], None),
        ("Clientes que dependem de financiamento e têm orçamento de até R$ 500.000 (`orcamento` <= 500000, não nulo).",
         "Clientes que dependem de financiamento e têm orçamento de até R$ 500.000.", [("orcamento", "<=", "500000")], None),
        ("Clientes com pet, `canal` = whatsapp.", "Clientes com pet.", [("canal", "=", "whatsapp")], None),
        ("Clientes com urgência para fechar OU que estão avaliando outra imobiliária.", None, [], "OU"),
        ("Clientes com pet E com filhos (`finalidade` = locacao).", "Clientes com pet E com filhos.", [("finalidade", "=", "locacao")], "E"),
        ("Clientes de setembro (`data` em 2026-09) que reclamaram.", "Clientes de setembro que reclamaram.", [("data", "em", "2026-09")], None),
    ]
    for cond, semantica, filtros, conector in casos:
        sep = S.separar(cond)
        if (semantica is not None and sep["semantica"] != semantica) or sep["filtros"] != filtros or sep["conector"] != conector:
            falhas.append(f"D separar {cond!r}: {sep}")
    sep = S.separar(casos[3][0])
    if sep["partes"] != ["Clientes com urgência para fechar", "Clientes que estão avaliando outra imobiliária."]:
        falhas.append(f"D sujeito herdado: {sep['partes']}")
    if "condition_parts" not in S.state_de(sep, "x") or "condition_parts" in S.state_de(SEP, "x"):
        falhas.append("D state: `condition_parts` só nas compostas")
    if set(P.perguntas_de(sep["partes"])) != {"stated", "hinted", "stated_part_0", "stated_part_1"} or set(P.perguntas_de(SEP["partes"])) != {"stated", "hinted"}:
        falhas.append("D perguntas_de: cláusulas só nas compostas")
    for ruim in ("", "   ", None, "Clientes com `pet`.", "A E B OU C"):
        try:
            S.separar(ruim)
            falhas.append(f"D separar aceitou {ruim!r}")
        except ValueError:
            pass
    return len(casos) + 8


def bateria_politica(falhas: list) -> int:
    n = 0
    niveis = {"falso": BAIXO, "indecidivel": DUVIDA, "verdadeiro": ALTO}
    # faixas de `stated` e válvula do `hinted`, nas quatro variantes
    for (nome_s, st), (nome_h, hi) in itertools.product(niveis.items(), niveis.items()):
        for var in R.VARIANTES.values():
            saida, _ = S.decidir({"stated": st, "hinted": hi}, None, var)
            esperado = nome_s
            if var["pista"] and nome_s == "falso" and hi >= P.PISTA_SIM:
                esperado = "indecidivel"
            if saida != esperado:
                falhas.append(f"E decidir stated {nome_s} hinted {nome_h} {var}: {saida} (esperado {esperado})")
            n += 1
    # combinação E/OU sobre todos os pares de estados (regra 5 do LEIA-ME)
    regra = {"E": lambda a, b: "verdadeiro" if a == b == "verdadeiro" else ("falso" if "falso" in (a, b) else "indecidivel"),
             "OU": lambda a, b: "verdadeiro" if "verdadeiro" in (a, b) else ("falso" if a == b == "falso" else "indecidivel")}
    for conector, (a, b) in itertools.product(("E", "OU"), itertools.product(niveis, repeat=2)):
        if S.combinar([a, b], conector) != regra[conector](a, b):
            falhas.append(f"E combinar {a} {conector} {b}: {S.combinar([a, b], conector)}")
        valores = {"stated": BAIXO, "hinted": BAIXO, "stated_part_0": niveis[a], "stated_part_1": niveis[b]}
        saida, _ = S.decidir(valores, conector, {"composta": "clausulas", "pista": False})
        if saida != regra[conector](a, b):
            falhas.append(f"E decidir cláusulas {a} {conector} {b}: {saida}")
        # na variante inteira as cláusulas não pesam
        if S.decidir(valores, conector, {"composta": "inteira", "pista": False})[0] != "falso":
            falhas.append(f"E variante inteira leu as cláusulas: {a} {conector} {b}")
        n += 3
    # a decisão oficial usa `perguntas.VARIANTE`
    if S.decidir({"stated": ALTO, "hinted": BAIXO}, None)[0] != "verdadeiro":
        falhas.append("E decidir sem variante não usa a oficial")
    # texto acima do teto: sem chamada, `indecidivel` marcado `longo`
    longa = _linha("x" * (P.TETO_CARACTERES + 1))
    for f in (S.avaliar, S.avaliar_seguro):
        d = f(NuncaChama(), SEP, longa)
        if d["saida"] != "indecidivel" or not d.get("longo") or d["por"] != "longo":
            falhas.append(f"E texto longo em {f.__name__}: {d}")
    # redecidir do run respeita saídas sem números
    for por in ("filtro", "falha", "longo"):
        s = {"saida": "falso" if por == "filtro" else "indecidivel", "por": por, "valores": None}
        if R.redecidir(s, None, R.VARIANTES["inteira"]) != s["saida"]:
            falhas.append(f"E redecidir mexeu numa saída `{por}`")
    # métricas: perdida, FP em negação, humano, indecidível do gabarito
    m = R.metricas([("falso", "verdadeiro", "fácil"), ("verdadeiro", "falso", "negação"), ("indecidivel", "verdadeiro", "fácil"),
                    ("indecidivel", "indecidivel", "fácil"), ("verdadeiro", "indecidivel", "fácil"), ("verdadeiro", "verdadeiro", "fácil")])
    esperado = {"decidiveis": 4, "decididas": 3, "tp": 1, "fp": 1, "fn": 1, "humano": 1, "perdidas": 1, "fp_negacao": 1,
                "ind_total": 2, "ind_humano": 1, "ind_verdadeiro": 1}
    if {k: m[k] for k in esperado} != esperado:
        falhas.append(f"E metricas: {{k: m[k] for k in esperado}} ≠ {esperado}")
    return n + 7


def bateria_revisao(falhas: list) -> int:
    """Achados 1–4 da revisão do Codex (2026-10-02)."""
    n = 0
    # 1. cláusula estruturada inválida: `separar` recusa; `separar_seguro` devolve erro; toda linha sai `indecidivel`
    invalidas = ["Clientes com pet (`orcamento` < 500000).", "Clientes com pet (`orcamento` <= cem).", "Clientes (`canal` = sms).",
                 "Clientes (`finalidade` >= compra).", "Clientes (`data` em 2026).", "Clientes (`data` = 2026-09).",
                 "Clientes (`etapa` = fechado).", "Clientes com `pet`.", "Clientes com pet (`orcamento <= 500000).",
                 "Clientes (`orcamento` 500000).", "Clientes (`visitas` = -1)."]
    for cond in invalidas:
        try:
            S.separar(cond)
            falhas.append(f"F1 separar aceitou {cond!r}")
        except ValueError:
            pass
        sep = S.separar_seguro(cond)
        if not sep.get("erro", "").startswith("condição inválida") or sep["filtros"] or sep["semantica"]:
            falhas.append(f"F1 separar_seguro {cond!r}: {sep}")
        for linha in (LINHA, _linha(orcamento=None)):
            d = S.avaliar_seguro(NuncaChama(), sep, linha)
            if d["saida"] != "indecidivel" or not d.get("falha") or d["por"] != "falha" or "condição inválida" not in d["motivo"]:
                falhas.append(f"F1 avaliar_seguro {cond!r}: {d}")
            try:
                S.avaliar(NuncaChama(), sep, linha)
                falhas.append(f"F1 avaliar aceitou condição inválida {cond!r}")
            except ValueError:
                pass
            b = S.baseline_seguro(sep, linha)
            if b["saida"] != "indecidivel" or not b["falha"]:
                falhas.append(f"F1 baseline_seguro {cond!r}: {b}")
        n += 1
    # a condição inválida que o Codex demonstrou: nem o filtro nulo nem a semântica vazia a transformam em `verdadeiro`
    if S.avaliar_seguro(NuncaChama(), S.separar_seguro("(`orcamento` < 500000)"), _linha(orcamento=None))["saida"] != "indecidivel":
        falhas.append("F1 o caso do Codex ainda sai de outra forma que não `indecidivel`")
    # 2. resíduo só de pontuação = semântica vazia, zero chamada; resíduo com letra continua semântica
    for cond, esperado in (("(`canal` = whatsapp).", ""), ("(`canal` = whatsapp), (`visitas` >= 1).", ""), (" , `canal` = whatsapp ; ", ""),
                           ("Pet (`canal` = whatsapp).", "Pet.")):
        sep = S.separar(cond)
        if sep["semantica"] != esperado:
            falhas.append(f"F2 separar {cond!r}: semântica {sep['semantica']!r}")
        if not esperado:
            d = S.avaliar_seguro(NuncaChama(), sep, _linha(canal="whatsapp", visitas=1))
            if d["saida"] != "verdadeiro" or d["por"] != "filtro":
                falhas.append(f"F2 {cond!r} chamou o Jev ou saiu {d['saida']}")
        n += 1
    # 3. válvula da pista por cláusula, antes de combinar; negação do E preservada
    var = {"composta": "clausulas", "pista": True}
    alto_h, baixo_h = (P.PISTA_SIM + 1) / 2, P.PISTA_SIM / 2
    casos3 = [
        ("OU, nada afirmado, pista alta (SQ-T14/OB-062)", {"stated_part_0": BAIXO, "stated_part_1": BAIXO}, "OU", alto_h, "indecidivel"),
        ("OU, nada afirmado, pista baixa", {"stated_part_0": BAIXO, "stated_part_1": BAIXO}, "OU", baixo_h, "falso"),
        ("E, nada afirmado, pista alta", {"stated_part_0": BAIXO, "stated_part_1": BAIXO}, "E", alto_h, "indecidivel"),
        ("E, um afirmado e um negado, pista alta → negação vence", {"stated_part_0": ALTO, "stated_part_1": BAIXO}, "E", alto_h, "falso"),
        ("E, um afirmado e um fraco, pista alta", {"stated_part_0": ALTO, "stated_part_1": DUVIDA}, "E", alto_h, "indecidivel"),
        ("OU, um afirmado, pista alta", {"stated_part_0": ALTO, "stated_part_1": BAIXO}, "OU", alto_h, "verdadeiro"),
        ("OU, um fraco e um negado, pista alta", {"stated_part_0": DUVIDA, "stated_part_1": BAIXO}, "OU", alto_h, "indecidivel"),
    ]
    for nome, partes, conector, hinted, esperado in casos3:
        saida, _ = S.decidir({"stated": BAIXO, "hinted": hinted, **partes}, conector, var)
        if saida != esperado:
            falhas.append(f"F3 {nome}: {saida} (esperado {esperado})")
        sem_pista, _ = S.decidir({"stated": BAIXO, "hinted": hinted, **partes}, conector, {"composta": "clausulas", "pista": False})
        if sem_pista != S.combinar([S._faixa(partes[k], *P.FAIXA["stated"]) for k in sorted(partes)], conector):
            falhas.append(f"F3 sem pista mudou: {nome}")
        n += 1
    # 4. previsão de orçamento, avaliação e baseline protegidos: campo com tipo errado e condição inválida não abortam
    linhas = [LINHA, _linha(orcamento="muito"), _linha(orcamento=None)]
    casos = [{"id": "C1", "condicao": "Clientes com pet (`orcamento` <= 500000)."}, {"id": "C2", "condicao": "Clientes (`orcamento` < 1)."}]
    try:
        if R.requisicoes_previstas(casos, linhas) != 1:
            falhas.append(f"F4 previsão: {R.requisicoes_previstas(casos, linhas)} (esperado 1: só a linha válida da condição válida)")
    except Exception as e:  # noqa: BLE001
        falhas.append(f"F4 previsão levantou {type(e).__name__}")
    duble = Duble(resposta(stated=ALTO))
    jev_real, R.Jev = R.Jev, lambda pasta: duble
    try:
        saidas, custo = R.rodar(casos, linhas)
    except Exception as e:  # noqa: BLE001
        falhas.append(f"F4 rodar levantou {type(e).__name__}")
        saidas, custo = {}, {}
    finally:
        R.Jev = jev_real
    if [s["saida"] for s in saidas.get("C1", [])] != ["verdadeiro", "indecidivel", "falso"] or \
            [s["saida"] for s in saidas.get("C2", [])] != ["indecidivel"] * 3 or custo.get("falhas_operacionais") != 4 or duble.chamadas != 1:
        falhas.append(f"F4 rodar: {[s['saida'] for v in saidas.values() for s in v]} falhas {custo.get('falhas_operacionais')} chamadas {duble.chamadas}")
    for c in casos:
        sep = S.separar_seguro(c["condicao"])
        bs = [S.baseline_seguro(sep, l) for l in linhas]
        esperado = [False, True, False] if c["id"] == "C1" else [True, True, True]
        if [b["falha"] for b in bs] != esperado or any(b["falha"] and b["saida"] != "indecidivel" for b in bs):
            falhas.append(f"F4 baseline_seguro {c['id']}: {bs}")
    try:
        S.baseline(S.separar_seguro("Clientes (`orcamento` < 1)."), LINHA)
        falhas.append("F4 baseline (baixo nível) aceitou condição inválida")
    except ValueError:
        pass
    m = R.metricas([("indecidivel", "falso", "fácil"), ("indecidivel", "verdadeiro", "fácil"), ("verdadeiro", "verdadeiro", "fácil")])
    if (m["v_humano"], m["f_humano"], round(m["F1_v_humano_perdidas"], 3)) != (1, 1, 0.667):
        falhas.append(f"F5 métrica de humano: {m['v_humano']}, {m['f_humano']}, {m['F1_v_humano_perdidas']}")
    return n + 6


def main() -> None:
    falhas: list[str] = []
    a, b, c, d, e = bateria_falhas(falhas), bateria_sem_semantica(falhas), bateria_filtro(falhas), bateria_separar(falhas), bateria_politica(falhas)
    f = bateria_revisao(falhas)
    if falhas:
        sys.exit(f"FALHOU ({len(falhas)}):\n  " + "\n  ".join(falhas[:40]) + ("\n  …" if len(falhas) > 40 else ""))
    print(f"ok: A {a} falhas operacionais → `indecidivel` por linha (nenhuma `verdadeiro`/`falso`; lote não aborta; resposta inválida "
          f"sai do cache; baixo nível levanta) · B {b} condição só de campos sem chamada · C {c} filtro com campo nulo/ausente/tipo errado · "
          f"D {d} separações · E {e} conferências da política (faixas, válvula, E/OU, teto, métricas) · F {f} conferências dos achados "
          f"1–4 da revisão (condição inválida → indecidivel, resíduo de pontuação, válvula por cláusula, baseline/previsão protegidos)")


if __name__ == "__main__":
    main()
