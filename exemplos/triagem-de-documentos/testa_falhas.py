"""Bateria do código da triagem de documentos — roda sem chave e sem rede (`python testa_falhas.py`).

O que se testa aqui é código nosso, não o modelo (dublê no lugar do Jev); nenhum número desta bateria é medição.
  A. falha operacional — resposta falsa (bool no lugar de número, string, NaN, fora de [0,1], ID faltando, `type`
     trocado, `answers` ausente, resposta que não é objeto, Choice com opção fora da lista ou contraditória), exceção
     de rede simulada ou documento fora do esquema (seção vazia, sem seções, tipo desconhecido): as `*_seguro` devolvem
     `indecidivel` com motivo "falha operacional" para AQUELE documento, nunca `verdadeiro` nem `falso`; o baixo nível
     levanta; o lote (`run.rodar`) não aborta; resposta inválida é tirada do cache (`jev.invalidar`) e falha de chamada
     não é; no mapa, UMA seção que falha derruba o documento inteiro para `indecidivel` (não dá para garantir que
     nenhuma seção posterior revoga);
  B. condição numérica (sem parte semântica) — resolvida em código, ZERO chamada; campo nulo/ausente = `falso`; tipo
     errado = falha; cláusula inválida (campo desconhecido, operador, não inteiro, duas crases) = condição inválida →
     `indecidivel` em TODOS os documentos, zero chamada, também no baseline;
  C. redução em código (desenho A) — institui; institui e revoga depois; revoga ANTES e institui depois (vale a
     ordem); valor no meio; `deferred` só com documento `falso`; a redução nunca inverte o Noul (institui alto sem
     revogação = `verdadeiro`; nada institui = `falso`); `prova` = maior `establishes`; grade das faixas;
  D. política do desenho B (`decidir_inteiro`), `redecidir` respeita saídas sem números, teto de caracteres,
     `requisicoes_previstas`, métricas (perdida, FP negada/revogada, humano, prova, indecidível do gabarito);
  F. revisão do Codex (2026-10-02, achados 1–3) — `tipo` preservado e validado (numérica sem expressão, semântica com
     crase, tipo ausente = condição inválida, zero chamada); expressão estruturada validada inteira (`< 12.5`, `12e1`,
     `<<`, sem parênteses = recusa); regra 6 "duas seções" por cláusula (`A E B` → um Noul por cláusula, combinados em
     código: uma cláusula só NUNCA é `verdadeiro`; prova = a seção que completa).
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
import triagem as T  # noqa: E402

NAO_E, SIM_E = P.FAIXA["establishes"]
NAO_R, SIM_R = P.FAIXA["revokes"]
BAIXO, MEIO, ALTO = 0.02, (NAO_E + SIM_E) / 2, 0.97
DOC = {"id": "X1", "tipo": "locacao",
       "secoes": [{"id": "X1-s1", "titulo": "Do prazo", "texto": "A locação vigorará por trinta meses."},
                  {"id": "X1-s2", "titulo": "Da rescisão", "texto": "Multa de três aluguéis na devolução antecipada."},
                  {"id": "X1-s3", "titulo": "Disposições finais", "texto": "As demais cláusulas permanecem íntegras."}],
       "campos": {"valor_aluguel": 1000, "prazo_meses": 30, "multa_alugueis": 3, "indice_reajuste": "IGP-M", "garantia": "fiador",
                  "renovacao_automatica": True}}
SEP = T.separar("Contrato de locação que prevê multa por devolução antecipada.", "semantica")
SEP_NUM = T.separar("Multa superior a dois aluguéis (`multa_alugueis` > 2).", "numerica")
SEP_COMPOSTA = T.separar("Contrato de locação garantido por fiador E cuja responsabilidade do fiador se estende até as chaves.", "semantica")
IDS = [s["id"] for s in DOC["secoes"]]


def resp_secao(establishes=BAIXO, revokes=BAIXO, deferred=BAIXO, **partes) -> dict:
    """`partes`: Nouls por cláusula (`establishes_part_0=…`) das condições compostas."""
    return {"model": "duble", "answers": {"establishes": {"type": "noul", "noul": establishes}, "revokes": {"type": "noul", "noul": revokes},
                                          "deferred": {"type": "noul", "noul": deferred}, **{k: {"type": "noul", "noul": v} for k, v in partes.items()}}}


def resp_doc(holds=BAIXO, deferred=BAIXO, prova=P.PROVA_NENHUMA, **partes) -> dict:
    probs = {i: 0.0 for i in [*IDS, P.PROVA_NENHUMA]}
    probs[prova] = 1.0
    return {"model": "duble", "answers": {"holds": {"type": "noul", "noul": holds}, "deferred": {"type": "noul", "noul": deferred},
                                          "proving_section": {"type": "choice", "choice": prova, "probabilities": probs, "confidence": 1.0},
                                          **{k: {"type": "noul", "noul": v} for k, v in partes.items()}}}


class Duble:
    """Jev de mentira: por seção (`por_secao[titulo]`) ou por documento; devolve resposta ou levanta. Conta chamadas e invalidações."""

    def __init__(self, padrao=None, por_secao: dict | None = None, invalidar_quebra: bool = False):
        self.padrao, self.por_secao, self.invalidar_quebra = padrao, por_secao or {}, invalidar_quebra
        self.n_chamadas, self.invalidados = 0, 0
        self.chamadas: list = []  # `run.rodar` lê a lista de medições do cliente real; o dublê não mede nada

    def perguntar(self, state, questions):
        self.n_chamadas += 1
        if "section" in state:
            saida = self.por_secao.get(state["section"]["title"], self.padrao if self.padrao is not None else resp_secao())
        else:
            saida = self.padrao if self.padrao is not None else resp_doc()
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


class NuncaChama(Duble):
    def perguntar(self, state, questions):
        raise AssertionError("o Jev foi chamado quando não devia")


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


# Corrupções sobre a resposta de SEÇÃO (A) — o Noul alto que viraria `verdadeiro` é o caso que importa.
FALSAS_SECAO = [
    ("Noul bool True (viraria 1.0 → institui)", _mexe(["answers", "establishes", "noul"], True)),
    ("Noul bool False", _mexe(["answers", "revokes", "noul"], False)),
    ("Noul string", _mexe(["answers", "establishes", "noul"], "0.95")),
    ("Noul None", _mexe(["answers", "deferred", "noul"], None)),
    ("Noul NaN", _mexe(["answers", "establishes", "noul"], math.nan)),
    ("Noul infinito", _mexe(["answers", "establishes", "noul"], math.inf)),
    ("Noul 1.5", _mexe(["answers", "establishes", "noul"], 1.5)),
    ("Noul negativo", _mexe(["answers", "revokes", "noul"], -0.1)),
    ("sem o campo `noul`", _mexe(["answers", "establishes", "noul"], apaga=True)),
    ("ID `establishes` faltando", _mexe(["answers", "establishes"], apaga=True)),
    ("ID `revokes` faltando", _mexe(["answers", "revokes"], apaga=True)),
    ("ID `deferred` faltando", _mexe(["answers", "deferred"], apaga=True)),
    ("`type` trocado", _mexe(["answers", "establishes", "type"], "choice")),
    ("resposta de um ID que não é objeto", _mexe(["answers", "establishes"], 0.9)),
    ("`answers` vazio", _mexe(["answers"], {})),
    ("`answers` None", _mexe(["answers"], None)),
    ("sem `answers`", _mexe(["answers"], apaga=True)),
]
FALSAS_DOC = [
    ("holds bool True", _mexe(["answers", "holds", "noul"], True)),
    ("holds string", _mexe(["answers", "holds", "noul"], "0.9")),
    ("holds 2.0", _mexe(["answers", "holds", "noul"], 2.0)),
    ("ID `holds` faltando", _mexe(["answers", "holds"], apaga=True)),
    ("ID `proving_section` faltando", _mexe(["answers", "proving_section"], apaga=True)),
    ("Choice com opção fora da lista", _mexe(["answers", "proving_section", "choice"], "X1-s9")),
    ("Choice contraditória (escolhida não é a de maior probabilidade)", _mexe(["answers", "proving_section", "choice"], "X1-s2")),
    ("Choice com probabilidades a menos", _mexe(["answers", "proving_section", "probabilities"], {"X1-s1": 1.0})),
    ("Choice com `type` de noul", _mexe(["answers", "proving_section", "type"], "noul")),
    ("Choice sem `confidence`", _mexe(["answers", "proving_section", "confidence"], apaga=True)),
]
INTEIRAS = [("resposta None", None), ("resposta lista", []), ("resposta string", "ok"), ("resposta {}", {})]
EXCECOES = [("timeout", TimeoutError("tempo esgotado")), ("conexão recusada", ConnectionError("sem rede")),
            ("erro HTTP 503", ErroHTTP("503")), ("erro HTTP 429", ErroHTTP("429")),
            ("cache faltando no modo gravado", RuntimeError("resposta não gravada no cache")), ("erro não previsto", KeyError("usage"))]


def _doc(**mudancas) -> dict:
    d = copy.deepcopy(DOC)
    d.update(mudancas)
    return d


def _confere_falha(nome: str, desenho: str, jev, doc: dict, falhas: list, sep: dict = SEP, invalida: bool | None = None) -> None:
    """Uma falha: o invólucro devolve `indecidivel` marcado; o baixo nível levanta; o cache é (ou não) invalidado."""
    seguro = T.AVALIAR[desenho]
    baixo = T.avaliar_mapa if desenho == "mapa" else T.avaliar_inteiro
    d = seguro(jev, sep, doc)
    if d["saida"] != "indecidivel" or not d.get("falha") or d["por"] != "falha" or not d["motivo"].startswith(("falha operacional", "condição inválida")):
        falhas.append(f"A {desenho} {nome}: seguro devolveu {d['saida']!r} / {d['motivo']!r}")
    if invalida is not None and bool(jev.invalidados) != invalida:
        falhas.append(f"A {desenho} {nome}: invalidações {jev.invalidados} (esperado {'≥1' if invalida else '0'})")
    try:
        baixo(jev, sep, doc)
        falhas.append(f"A {desenho} {nome}: baixo nível não levantou")
    except Exception:  # noqa: BLE001 — qualquer exceção serve: o ponto é não devolver decisão
        pass


def bateria_falhas(falhas: list) -> int:
    n = 0
    # dublês válidos: A `falso` (nada institui) e B `falso`
    for desenho in T.AVALIAR:
        base = T.AVALIAR[desenho](Duble(), SEP, DOC)
        assert base["saida"] == "falso" and base["por"] == "jev", f"o dublê válido tem de dar `falso` pelo Jev: {base}"
    for nome, corrompe in FALSAS_SECAO:
        # a seção corrompida é a 2ª: a 1ª já foi respondida (válida) — o documento inteiro ainda tem de cair em `indecidivel`
        jev = Duble(por_secao={"Da rescisão": corrompe(copy.deepcopy(resp_secao()))})
        _confere_falha(nome, "mapa", jev, DOC, falhas, invalida=True)
        n += 1
    for nome, corrompe in FALSAS_DOC:
        _confere_falha(nome, "inteiro", Duble(corrompe(copy.deepcopy(resp_doc()))), DOC, falhas, invalida=True)
        n += 1
    for nome, inteira in INTEIRAS:
        for desenho in T.AVALIAR:
            jev = Duble()
            jev.padrao = inteira
            if inteira is None:  # `None` cairia no padrão válido do dublê: força o retorno
                jev.perguntar = lambda state, questions: None
            _confere_falha(nome, desenho, jev, DOC, falhas, invalida=None if inteira is None else True)
            n += 1
    for nome, erro in EXCECOES:
        for desenho in T.AVALIAR:
            _confere_falha(nome, desenho, Duble(erro), DOC, falhas, invalida=False)  # nada gravado: nada a invalidar
            n += 1
    # falha numa seção do MEIO, depois de uma válida que institui: o documento não pode sair `verdadeiro`
    jev = Duble(por_secao={"Do prazo": resp_secao(establishes=ALTO), "Disposições finais": TimeoutError()})
    _confere_falha("timeout na última seção após institui", "mapa", jev, DOC, falhas, invalida=False)
    n += 1
    # documento fora do esquema
    for nome, doc in (("seção com texto vazio", _doc(secoes=[{"id": "X1-s1", "titulo": "t", "texto": "   "}])),
                      ("seção sem texto", _doc(secoes=[{"id": "X1-s1", "titulo": "t"}])),
                      ("sem seções", _doc(secoes=[])), ("seções None", _doc(secoes=None)),
                      ("ids de seção repetidos", _doc(secoes=[DOC["secoes"][0], DOC["secoes"][0]])),
                      ("tipo desconhecido", _doc(tipo="edital")), ("tipo None", _doc(tipo=None))):
        for desenho in T.AVALIAR:
            _confere_falha(nome, desenho, NuncaChama() if nome != "seção com texto vazio" else Duble(), doc, falhas)
            n += 1
    # invalidar que quebra não muda o desfecho
    _confere_falha("invalidar que quebra", "mapa", Duble(_mexe(["answers", "establishes", "noul"], True)(resp_secao()), invalidar_quebra=True), DOC, falhas)
    _confere_falha("invalidar que quebra (B)", "inteiro", Duble(_mexe(["answers", "holds", "noul"], True)(resp_doc()), invalidar_quebra=True), DOC, falhas)
    n += 2
    # o lote não aborta: `run.rodar` com dublês; só os documentos com falha saem `indecidivel`
    docs = [_doc(id=f"D{i}", secoes=[{"id": f"D{i}-s1", "titulo": f"t{i}", "texto": "x"}]) for i in range(4)]
    mapa = Duble(por_secao={"t1": TimeoutError(), "t2": resp_secao(establishes=ALTO), "t3": _mexe(["answers", "establishes", "noul"], True)(resp_secao())})
    jev_real, R.Jev = R.Jev, lambda pasta: mapa
    try:
        saidas, custos = R.rodar([{"id": "C1", "condicao": "Multa.", "tipo": "semantica"}], docs)
    finally:
        R.Jev = jev_real
    a = [s["saida"] for s in saidas["mapa"]["C1"]]
    if a != ["falso", "indecidivel", "verdadeiro", "indecidivel"] or custos["mapa"]["falhas_operacionais"] != 2:
        falhas.append(f"A lote: saídas {a}, falhas contadas {custos['mapa']['falhas_operacionais']}")
    return n + 1


def bateria_numerica(falhas: list) -> int:
    n = 0
    for desenho in T.AVALIAR:
        for nome, campos, esperado in (("multa 3 > 2", {"multa_alugueis": 3}, "verdadeiro"), ("multa 2 > 2", {"multa_alugueis": 2}, "falso"),
                                       ("multa nula (negada/revogada)", {"multa_alugueis": None}, "falso")):
            d = T.AVALIAR[desenho](NuncaChama(), SEP_NUM, _doc(campos={**DOC["campos"], **campos}))
            if d["saida"] != esperado or d["por"] != "codigo":
                falhas.append(f"B {desenho} {nome}: {d}")
            n += 1
        doc = _doc(campos={k: v for k, v in DOC["campos"].items() if k != "multa_alugueis"})
        d = T.AVALIAR[desenho](NuncaChama(), SEP_NUM, doc)
        if d["saida"] != "falso" or d["por"] != "codigo":
            falhas.append(f"B {desenho} campo ausente: {d}")
        d = T.AVALIAR[desenho](NuncaChama(), SEP_NUM, _doc(tipo="ata_condominio", campos={"data": "2026-01-01"}))
        if d["saida"] != "falso":
            falhas.append(f"B {desenho} outro tipo sem o campo: {d}")
        for nome, campos in (("string", {"multa_alugueis": "3"}), ("bool", {"multa_alugueis": True}), ("float", {"multa_alugueis": 2.5})):
            _confere_falha(f"B tipo {nome}", desenho, NuncaChama(), _doc(campos={**DOC["campos"], **campos}), falhas, sep=SEP_NUM)
            n += 1
        n += 2
    # cláusula inválida → condição inválida → `indecidivel` em todo documento, zero chamada, nos dois desenhos e no baseline
    for cond in ("Multa (`multa` > 2).", "Multa (`multa_alugueis` >> 2).", "Multa (`multa_alugueis` > dois).", "Multa (`multa_alugueis` = 2).",
                 "Multa (`multa_alugueis` > 2) e prazo (`prazo_meses` < 12).", "Multa `multa_alugueis.", "", "   ", None):
        try:
            T.separar(cond, "numerica")
            falhas.append(f"B separar aceitou {cond!r}")
        except ValueError:
            pass
        sep = T.separar_seguro(cond, "numerica")
        if not sep.get("erro", "").startswith("condição inválida"):
            falhas.append(f"B separar_seguro {cond!r}: {sep}")
        for desenho in T.AVALIAR:
            _confere_falha(f"B condição inválida {cond!r}", desenho, NuncaChama(), DOC, falhas, sep=sep)
        b = T.baseline_seguro(sep, DOC)
        if b["saida"] != "indecidivel" or not b.get("falha"):
            falhas.append(f"B baseline_seguro {cond!r}: {b}")
        n += 1
    # grade dos operadores
    for op, v, esperado in (("<", 11, True), ("<", 12, False), ("<=", 12, True), (">", 12, False), (">=", 12, True)):
        sep = T.separar(f"Prazo (`prazo_meses` {op} 12).", "numerica")
        if (T.avaliar_numerica(sep, _doc(campos={**DOC["campos"], "prazo_meses": v}))["saida"] == "verdadeiro") != esperado:
            falhas.append(f"B operador {op} com {v}")
        n += 1
    return n


def _sec(i: int, e=BAIXO, r=BAIXO, d=BAIXO) -> dict:
    return {"id": f"s{i}", "establishes": e, "revokes": r, "deferred": d}


def bateria_reducao(falhas: list) -> int:
    casos = [
        ("nada institui", [_sec(1), _sec(2)], "falso", "s1"),
        ("institui alto → verdadeiro (a redução não inverte o Noul)", [_sec(1), _sec(2, e=ALTO)], "verdadeiro", "s2"),
        ("institui e revoga depois", [_sec(1, e=ALTO), _sec(2, r=ALTO)], "falso", "s1"),
        ("revoga ANTES e institui depois: vale a ordem", [_sec(1, r=ALTO), _sec(2, e=ALTO)], "verdadeiro", "s2"),
        ("institui, revoga, institui de novo", [_sec(1, e=ALTO), _sec(2, r=ALTO), _sec(3, e=ALTO)], "verdadeiro", "s1"),
        ("institui no meio", [_sec(1, e=MEIO)], "indecidivel", "s1"),
        ("institui no meio e depois alto", [_sec(1, e=MEIO), _sec(2, e=ALTO)], "verdadeiro", "s2"),
        ("institui alto e revoga no meio", [_sec(1, e=ALTO), _sec(2, r=(NAO_R + SIM_R) / 2)], "indecidivel", "s1"),
        ("institui alto e revoga baixo", [_sec(1, e=ALTO), _sec(2, r=NAO_R)], "verdadeiro", "s1"),
        ("revoga no meio sem nada instituído", [_sec(1, r=(NAO_R + SIM_R) / 2)], "falso", "s1"),
        ("institui no meio e revoga alto depois", [_sec(1, e=MEIO), _sec(2, r=ALTO)], "falso", "s1"),
        ("falso com deferred alto → indecidível", [_sec(1, d=P.ADIADO_SIM)], "indecidivel", "s1"),
        ("verdadeiro com deferred alto fica verdadeiro", [_sec(1, e=ALTO, d=ALTO)], "verdadeiro", "s1"),
        ("revogado com deferred alto → indecidível (falso ao final)", [_sec(1, e=ALTO), _sec(2, r=ALTO, d=ALTO)], "indecidivel", "s1"),
        ("deferred abaixo do limiar não dispara", [_sec(1, d=P.ADIADO_SIM - 0.05)], "falso", "s1"),
        ("prova = maior establishes mesmo revogado", [_sec(1, e=0.9), _sec(2, e=0.95), _sec(3, r=ALTO)], "falso", "s2"),
        ("limiar exato: establishes == sim institui", [_sec(1, e=SIM_E)], "verdadeiro", "s1"),
        ("limiar exato: establishes == nao é falso", [_sec(1, e=NAO_E)], "falso", "s1"),
    ]
    for nome, secoes, esperado, prova in casos:
        saida, p, _ = T.reduzir(secoes)
        if saida != esperado or p != prova:
            falhas.append(f"C {nome}: {saida}/{p} (esperado {esperado}/{prova})")
    try:
        T.reduzir([])
        falhas.append("C reduzir aceitou lista vazia")
    except ValueError:
        pass
    # faixa passada por fora (curva do relatório) muda a decisão; a oficial é `perguntas.FAIXA`
    larga = {k: (0.1, 0.9) for k in P.FAIXA}
    if T.reduzir([_sec(1, e=0.85)], larga)[0] != "indecidivel" or T.reduzir([_sec(1, e=0.85)])[0] != "verdadeiro":
        falhas.append("C faixa alternativa não é respeitada")
    # ponta a ponta no desenho A com dublê por seção: revogação posterior
    jev = Duble(por_secao={"Da rescisão": resp_secao(establishes=ALTO), "Disposições finais": resp_secao(revokes=ALTO)})
    d = T.avaliar_mapa_seguro(jev, SEP, DOC)
    if d["saida"] != "falso" or d["prova"] != "X1-s2" or jev.n_chamadas != 3:
        falhas.append(f"C ponta a ponta revogação: {d['saida']} prova {d['prova']} chamadas {jev.chamadas}")
    jev = Duble(por_secao={"Da rescisão": resp_secao(establishes=ALTO)})
    d = T.avaliar_mapa_seguro(jev, SEP, DOC)
    if d["saida"] != "verdadeiro" or d["prova"] != "X1-s2":
        falhas.append(f"C ponta a ponta institui: {d}")
    return len(casos) + 4


def bateria_politica(falhas: list) -> int:
    n = 0
    nao, sim = P.FAIXA["holds"]
    niveis = {"falso": nao, "indecidivel": (nao + sim) / 2, "verdadeiro": sim}
    for (nome_h, h), (nome_d, dv) in itertools.product(niveis.items(), {"baixo": 0.0, "alto": P.ADIADO_SIM}.items()):
        saida, _ = T.decidir_inteiro({"holds": h, "deferred": dv})
        esperado = "indecidivel" if nome_h == "falso" and nome_d == "alto" else nome_h
        if saida != esperado:
            falhas.append(f"D decidir_inteiro holds {nome_h} deferred {nome_d}: {saida} (esperado {esperado})")
        n += 1
    # ponta a ponta B: prova vem da Choice; `none` → prova None
    d = T.avaliar_inteiro_seguro(Duble(resp_doc(holds=ALTO, prova="X1-s2")), SEP, DOC)
    if d["saida"] != "verdadeiro" or d["prova"] != "X1-s2":
        falhas.append(f"D ponta a ponta B: {d}")
    d = T.avaliar_inteiro_seguro(Duble(resp_doc()), SEP, DOC)
    if d["saida"] != "falso" or d["prova"] is not None:
        falhas.append(f"D ponta a ponta B none: {d}")
    # redecidir respeita saídas sem números
    for por in ("codigo", "falha", "longo"):
        s = {"saida": "falso" if por == "codigo" else "indecidivel", "por": por}
        for desenho in T.AVALIAR:
            if R.redecidir(s, desenho, P.FAIXA, P.ADIADO_SIM) != s["saida"]:
                falhas.append(f"D redecidir mexeu numa saída `{por}` ({desenho})")
    # teto de caracteres: sem chamada, `indecidivel` marcado `longo`
    longo = _doc(secoes=[{"id": "X1-s1", "titulo": "t", "texto": "x" * (P.TETO_CARACTERES["secao"] + 1)}])
    d = T.avaliar_mapa_seguro(NuncaChama(), SEP, longo)
    if d["saida"] != "indecidivel" or not d.get("longo"):
        falhas.append(f"D teto seção: {d}")
    muito = _doc(secoes=[{"id": f"X1-s{i}", "titulo": "t", "texto": "x" * 3999} for i in range(1, 8)])
    d = T.avaliar_inteiro_seguro(NuncaChama(), SEP, muito)
    if d["saida"] != "indecidivel" or not d.get("longo"):
        falhas.append(f"D teto documento: {d}")
    # previsão de requisições: semântica = seções + documentos; numérica e inválida = 0
    casos = [{"id": "a", "condicao": "Multa.", "tipo": "semantica"}, {"id": "b", "condicao": "Multa (`multa_alugueis` > 2).", "tipo": "numerica"},
             {"id": "c", "condicao": "Multa (`x` > 2).", "tipo": "numerica"}, {"id": "d", "condicao": "Multa superior a dois aluguéis.", "tipo": "numerica"}]
    if R.requisicoes_previstas(casos, [DOC, DOC]) != 2 * 3 + 2:
        falhas.append(f"D previsão: {R.requisicoes_previstas(casos, [DOC, DOC])}")
    # métricas
    m = R.metricas([("falso", "verdadeiro", "fácil", True), ("verdadeiro", "falso", "negada", None), ("verdadeiro", "falso", "fácil", None),
                    ("indecidivel", "verdadeiro", "fácil", False), ("indecidivel", "indecidivel", "fácil", None), ("verdadeiro", "indecidivel", "fácil", None),
                    ("verdadeiro", "verdadeiro", "revogada", True), ("verdadeiro", "verdadeiro", "fácil", False)])
    esperado = {"decidiveis": 6, "decididas": 5, "tp": 2, "fp": 2, "fn": 1, "humano": 1, "v_humano": 1, "perdidas": 1, "fp_negada_revogada": 1,
                "prova_ok": 2, "prova_n": 4, "ind_total": 2, "ind_humano": 1, "ind_verdadeiro": 1}
    if {k: m[k] for k in esperado} != esperado:
        falhas.append(f"D metricas: { {k: m[k] for k in esperado} } ≠ {esperado}")
    # família pela nota
    for nota, fam in (("difícil: negada — x", "negada"), ("difícil: revogada — x", "revogada"), ("difícil: duas seções — x", "duas seções"),
                      ("difícil: termo só no título — x", "termo só no título"), ("difícil: seção parecida de outro assunto", "seção parecida"),
                      ("difícil: sem a cláusula", "sem a cláusula"), ("fácil: x", "fácil"), (None, "fácil")):
        if R.familia({"nota": nota}) != fam:
            falhas.append(f"D família {nota!r}: {R.familia({'nota': nota})}")
        n += 1
    # baseline: radicais e seção que prova; nunca indecidível
    b = T.baseline(SEP, DOC)
    if b["saida"] != "verdadeiro" or b["prova"] != "X1-s2":
        falhas.append(f"D baseline: {b}")
    if T.baseline(T.separar("Cláusula de confidencialidade."), DOC)["saida"] != "falso":
        falhas.append("D baseline achou confidencialidade onde não há")
    return n + 9


def bateria_revisao(falhas: list) -> int:
    """Achados 1–3 da revisão do Codex (2026-10-02)."""
    n = 0
    # 1. `tipo` preservado e validado: numérica sem expressão (o caso do Codex: "multa superior a dois aluguéis") é condição
    #    inválida → `indecidivel` em todo documento, ZERO chamada, nos dois desenhos e no baseline; semântica com crase idem;
    #    `tipo` ausente ou desconhecido idem.
    invalidas = [("Contrato de locação com multa superior a dois aluguéis.", "numerica"),
                 ("Contrato de locação com multa superior a dois aluguéis (`multa_alugueis` > 2).", "semantica"),
                 ("Contrato de locação com multa.", None), ("Contrato de locação com multa.", "booleana"),
                 ("Multa (`multa_alugueis` > 2).", ""), ("Multa.", 3)]
    for cond, tipo in invalidas:
        try:
            T.separar(cond, tipo)
            falhas.append(f"F1 separar aceitou {cond!r} com tipo {tipo!r}")
        except ValueError:
            pass
        sep = T.separar_seguro(cond, tipo)
        if not sep.get("erro", "").startswith("condição inválida") or sep["numerica"] or sep["partes"]:
            falhas.append(f"F1 separar_seguro {cond!r}/{tipo!r}: {sep}")
        for desenho in T.AVALIAR:
            _confere_falha(f"F1 {cond!r}/{tipo!r}", desenho, NuncaChama(), DOC, falhas, sep=sep)
        b = T.baseline_seguro(sep, DOC)
        if b["saida"] != "indecidivel" or not b.get("falha"):
            falhas.append(f"F1 baseline_seguro {cond!r}/{tipo!r}: {b}")
        n += 1
    # `run.separar` lê o `tipo` da condição do arquivo; sem `tipo`, inválida; previsão de requisições = 0 para ela
    if not R.separar({"condicao": "Multa."}).get("erro") or R.separar({"condicao": "Multa.", "tipo": "semantica"}).get("erro"):
        falhas.append("F1 run.separar não usa/valida o tipo")
    if R.requisicoes_previstas([{"id": "d", "condicao": "Multa superior a dois aluguéis.", "tipo": "numerica"}], [DOC, DOC]) != 0:
        falhas.append("F1 previsão contou chamadas para numérica inválida")
    n += 2
    # 2. expressão estruturada validada INTEIRA: sufixo decimal/científico/operador extra, sem parênteses, dois grupos = recusa
    for cond in ("Prazo (`prazo_meses` < 12.5).", "Prazo (`prazo_meses` < 12e1).", "Prazo (`prazo_meses` << 12).", "Prazo (`prazo_meses` < 12 e 5).",
                 "Prazo (`prazo_meses` < -12).", "Prazo (`prazo_meses` < 12,5).", "Prazo `prazo_meses` < 12.", "Prazo (`prazo_meses` < 12) (`prazo_meses` > 1).",
                 "Prazo (`prazo_meses` <).", "Prazo (`prazo_meses` 12).", "Prazo (`prazo_meses` < 12 meses)."):
        try:
            T.separar(cond, "numerica")
            falhas.append(f"F2 separar aceitou {cond!r}")
        except ValueError:
            pass
        sep = T.separar_seguro(cond, "numerica")
        for desenho in T.AVALIAR:
            _confere_falha(f"F2 {cond!r}", desenho, NuncaChama(), _doc(campos={**DOC["campos"], "prazo_meses": 12}), falhas, sep=sep)
        n += 1
    for cond, esperado in (("Prazo (`prazo_meses` < 12).", ("prazo_meses", "<", 12)), ("Prazo ( `prazo_meses`  >=  12 ) curto.", ("prazo_meses", ">=", 12)),
                           ("(`garantia_meses` > 0)", ("garantia_meses", ">", 0))):
        if T.separar(cond, "numerica")["numerica"] != esperado:
            falhas.append(f"F2 separar {cond!r}: {T.separar(cond, 'numerica')['numerica']}")
        n += 1
    # 3. regra 6 (duas seções): condição composta "A E B" → um Noul por cláusula; só as duas cláusulas instituídas (em seções
    #    iguais ou diferentes) dão `verdadeiro`; uma só → falso; prova = a seção que COMPLETA (a mais tardia)
    if SEP_COMPOSTA["partes"] != ["Contrato de locação garantido por fiador", "cuja responsabilidade do fiador se estende até as chaves."]:
        falhas.append(f"F3 separar composta: {SEP_COMPOSTA['partes']}")
    if T.separar("Contrato com multa e com fiador.", "semantica")["partes"] != ["Contrato com multa e com fiador."]:
        falhas.append("F3 'e' minúsculo virou conector")
    st, st1 = T.state_secao(SEP_COMPOSTA, DOC, DOC["secoes"][0]), T.state_secao(SEP, DOC, DOC["secoes"][0])
    if st.get("condition_parts") != SEP_COMPOSTA["partes"] or "condition_parts" in st1 or "condition_parts" in T.state_documento(SEP, DOC):
        falhas.append("F3 state: `condition_parts` só nas compostas")
    if set(P.perguntas_secao(SEP_COMPOSTA["partes"])) != {*P.PERGUNTAS_SECAO, "establishes_part_0", "establishes_part_1"} \
            or P.perguntas_secao(SEP["partes"]) != P.PERGUNTAS_SECAO \
            or set(P.perguntas_documento(IDS, SEP_COMPOSTA["partes"])) != {*P.PERGUNTAS_DOCUMENTO, "proving_section", "holds_part_0", "holds_part_1"}:
        falhas.append("F3 perguntas por cláusula só nas compostas")
    n += 4
    c = lambda i, p0=BAIXO, p1=BAIXO, e=BAIXO, r=BAIXO, d=BAIXO: {"id": f"s{i}", "establishes": e, "revokes": r, "deferred": d,  # noqa: E731
                                                                 "establishes_part_0": p0, "establishes_part_1": p1}
    casos = [
        ("uma cláusula só, mesmo com `establishes` inteiro alto (o caso do Codex: L01 sem garantia)", [c(1), c(2, p1=ALTO, e=ALTO)], "falso", "s2"),
        ("as duas em seções diferentes", [c(1, p0=ALTO), c(2), c(3, p1=ALTO)], "verdadeiro", "s3"),
        ("as duas na mesma seção", [c(1, p0=ALTO, p1=ALTO)], "verdadeiro", "s1"),
        ("segunda ANTES da primeira: ordem não importa entre cláusulas", [c(1, p1=ALTO), c(2, p0=ALTO)], "verdadeiro", "s2"),
        ("uma instituída, a outra no meio → indecidível", [c(1, p0=ALTO), c(2, p1=MEIO)], "indecidivel", "s2"),
        ("uma instituída e depois revogada, a outra instituída → falso", [c(1, p0=ALTO), c(2, p1=ALTO), c(3, r=ALTO)], "falso", "s2"),
        ("nenhuma, com deferred alto → indecidível", [c(1, d=P.ADIADO_SIM)], "indecidivel", "s1"),
        ("nenhuma → falso", [c(1), c(2)], "falso", "s1"),
    ]
    for nome, secoes, esperado, prova in casos:
        saida, p, _ = T.reduzir(secoes)
        if saida != esperado or p != prova:
            falhas.append(f"F3 {nome}: {saida}/{p} (esperado {esperado}/{prova})")
        n += 1
    for nome, valores, esperado in (("B: as duas", {"holds": BAIXO, "deferred": BAIXO, "holds_part_0": ALTO, "holds_part_1": ALTO}, "verdadeiro"),
                                    ("B: uma só, com holds inteiro alto", {"holds": ALTO, "deferred": BAIXO, "holds_part_0": ALTO, "holds_part_1": BAIXO}, "falso"),
                                    ("B: uma no meio", {"holds": BAIXO, "deferred": BAIXO, "holds_part_0": ALTO, "holds_part_1": MEIO}, "indecidivel"),
                                    ("B: nenhuma com deferred", {"holds": BAIXO, "deferred": ALTO, "holds_part_0": BAIXO, "holds_part_1": BAIXO}, "indecidivel")):
        if T.decidir_inteiro(valores)[0] != esperado:
            falhas.append(f"F3 {nome}: {T.decidir_inteiro(valores)}")
        n += 1
    # ponta a ponta A: cláusula 0 na seção 2 (via `establishes_part_0`), cláusula 1 só na seção 3; faltar o Noul da cláusula = falha
    jev = Duble(por_secao={"Da rescisão": resp_secao(establishes=ALTO, establishes_part_0=ALTO, establishes_part_1=BAIXO),
                           "Disposições finais": resp_secao(establishes_part_0=BAIXO, establishes_part_1=ALTO)},
                padrao=resp_secao(establishes_part_0=BAIXO, establishes_part_1=BAIXO))
    d = T.avaliar_mapa_seguro(jev, SEP_COMPOSTA, DOC)
    if d["saida"] != "verdadeiro" or d["prova"] != "X1-s3":
        falhas.append(f"F3 ponta a ponta A composta: {d['saida']} prova {d['prova']}")
    jev = Duble(por_secao={"Da rescisão": resp_secao(establishes=ALTO, establishes_part_0=ALTO, establishes_part_1=BAIXO)},
                padrao=resp_secao(establishes_part_0=BAIXO, establishes_part_1=BAIXO))
    if T.avaliar_mapa_seguro(jev, SEP_COMPOSTA, DOC)["saida"] != "falso":
        falhas.append("F3 ponta a ponta A: uma cláusula só saiu de outra forma que não `falso`")
    _confere_falha("F3 resposta sem o Noul da cláusula", "mapa", Duble(resp_secao(establishes=ALTO)), DOC, falhas, sep=SEP_COMPOSTA, invalida=True)
    d = T.avaliar_inteiro_seguro(Duble(resp_doc(holds=ALTO, prova="X1-s3", holds_part_0=ALTO, holds_part_1=ALTO)), SEP_COMPOSTA, DOC)
    if d["saida"] != "verdadeiro" or d["prova"] != "X1-s3":
        falhas.append(f"F3 ponta a ponta B composta: {d}")
    _confere_falha("F3 B sem o Noul da cláusula", "inteiro", Duble(resp_doc(holds=ALTO)), DOC, falhas, sep=SEP_COMPOSTA, invalida=True)
    # baseline composto: cada cláusula tem de bater (em qualquer seção); prova = a mais tardia
    b = T.baseline(T.separar("Contrato com multa na devolução antecipada E com prazo de trinta meses.", "semantica"), DOC)
    if b["saida"] != "verdadeiro" or b["prova"] != "X1-s2":
        falhas.append(f"F3 baseline composto: {b}")
    if T.baseline(T.separar("Contrato com multa na devolução antecipada E com cláusula de confidencialidade.", "semantica"), DOC)["saida"] != "falso":
        falhas.append("F3 baseline composto aceitou uma cláusula só")
    return n + 7


def main() -> int:
    falhas: list[str] = []
    n = bateria_falhas(falhas) + bateria_numerica(falhas) + bateria_reducao(falhas) + bateria_politica(falhas) + bateria_revisao(falhas)
    for f in falhas:
        print("FALHOU:", f)
    print(f"{n} conferências, {len(falhas)} falhas")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
