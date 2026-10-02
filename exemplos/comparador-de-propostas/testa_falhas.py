"""Bateria do código do comparador — roda sem chave e sem rede (`python testa_falhas.py`).

O que se prova, com um dublê no lugar do Jev (nenhum número daqui é medição do modelo):
  A. falha operacional — resposta falsa (bool no lugar de número, ID faltando, Choice sem distribuição, vencedor
     que não é o mais provável…), exceção de rede, cache faltando ou entrada inválida: `comparar_proposta_seguro`
     devolve TODAS as semânticas daquela proposta como `nao_informado` com `falha`, nunca `atende` nem `contradiz`;
     as numéricas continuam pelo código; a disputa não aborta; o baixo nível levanta; resposta JSON válida mas
     rejeitada sai do cache (`invalidar` é chamado) — resposta inválida não fica presa;
  B. número é do código — limite lido do texto do requisito, `<=`/`>=`, `null`/bool/string → nao_informado,
     igualdade no limite = atende; nada disso passa pelo Jev;
  C. válvula e combinação — `meets`/`contradicts` abaixo do limiar → nao_informado; Nouls: exclusão vence inclusão
     em toda a grade, dúvida → nao_informado;
  D. elegíveis e perguntas — contradiz em obrigatório derruba; nao_informado em obrigatório mantém e vira pergunta;
     opcional nunca derruba; disputa sem elegível existe.
"""
from __future__ import annotations

import copy
import itertools
import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import comparador as C  # noqa: E402
import perguntas as P  # noqa: E402

DISPUTA = {
    "id": "X1",
    "requisitos": [
        {"id": "r1", "texto": "Instalação inclusa no preço.", "obrigatorio": True, "tipo": "semantico"},
        {"id": "r2", "texto": "Garantia de pelo menos 12 meses (`garantia_meses` >= 12).", "obrigatorio": True, "tipo": "numerico"},
        {"id": "r3", "texto": "Preço total de até R$ 20.000 (`preco_total` <= 20000).", "obrigatorio": True, "tipo": "numerico"},
        {"id": "r4", "texto": "Manutenção no primeiro ano inclusa.", "obrigatorio": False, "tipo": "semantico"},
    ],
    "propostas": [
        {"id": "p1", "texto": "Instalação inclusa. Garantia de 12 meses. Total R$ 20.000,00.", "campos": {"garantia_meses": 12, "preco_total": 20000}},
        {"id": "p2", "texto": "Instalação cobrada à parte. Garantia de 24 meses. Total R$ 15.000,00.", "campos": {"garantia_meses": 24, "preco_total": 15000}},
        {"id": "p3", "texto": "Instalação inclusa. Garantia conforme fabricante. Total R$ 18.000,00.", "campos": {"garantia_meses": None, "preco_total": 18000}},
    ],
}
OPCOES = list(P.CELULA_DA_OPCAO)


def resposta(opcoes: tuple[str, ...] = ("meets", "meets"), conf: float = 1.0) -> dict:
    """Resposta VÁLIDA no formato da API: tudo `meets` confiante → o pior destino para uma falha tolerada."""
    answers = {}
    for i, o in enumerate(opcoes):
        resto = (1.0 - conf) / (len(OPCOES) - 1)
        answers[f"req_{i}"] = {"type": "choice", "choice": o, "confidence": conf,
                               "probabilities": {k: (conf if k == o else resto) for k in OPCOES}}
    return {"model": "duble", "answers": answers}


class Duble:
    """Jev de mentira: devolve a resposta dada ou levanta a exceção dada; por proposta, se `por_texto`."""

    def __init__(self, padrao=None, por_texto: dict | None = None):
        self.padrao = padrao if padrao is not None else resposta()
        self.por_texto, self.invalidados = por_texto or {}, []

    def perguntar(self, state, questions):
        saida = self.por_texto.get(state["proposal"], self.padrao)
        if isinstance(saida, Exception):
            raise saida
        return saida

    def invalidar(self, state, questions):
        self.invalidados.append(state["proposal"])
        return True

    def resumo(self):
        return {}


class DubleSemInvalidar:
    """Cliente mínimo, sem `invalidar`: o invólucro não pode depender do método."""

    def __init__(self, padrao):
        self.padrao = padrao

    def perguntar(self, state, questions):
        return self.padrao


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
    ("confiança bool True", _mexe(["answers", "req_0", "confidence"], True)),
    ("confiança string", _mexe(["answers", "req_0", "confidence"], "0.9")),
    ("confiança NaN", _mexe(["answers", "req_0", "confidence"], math.nan)),
    ("confiança > 1", _mexe(["answers", "req_0", "confidence"], 1.5)),
    ("confiança ausente", _mexe(["answers", "req_0", "confidence"], apaga=True)),
    ("probabilidade bool", _mexe(["answers", "req_0", "probabilities", "meets"], True)),
    ("distribuição incompleta", _mexe(["answers", "req_0", "probabilities"], {"meets": 1.0})),
    ("distribuição que não soma 1", _mexe(["answers", "req_0", "probabilities"], {o: 0.5 for o in OPCOES})),
    ("distribuição ausente", _mexe(["answers", "req_0", "probabilities"], apaga=True)),
    ("vencedor fora das opções", _mexe(["answers", "req_0", "choice"], "atende")),
    ("vencedor que não é o mais provável", _mexe(["answers", "req_0", "choice"], "not_stated")),
    ("discriminador `type` trocado (noul)", _mexe(["answers", "req_0", "type"], "noul")),
    ("ID da 2ª pergunta faltando", _mexe(["answers", "req_1"], apaga=True)),
    ("resposta de um ID que não é objeto", _mexe(["answers", "req_0"], 0.9)),
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


def _confere_falha(nome: str, jev, proposta: dict, etapa: str, falhas: list, invalida: bool) -> None:
    d = C.comparar_proposta_seguro(jev, DISPUTA, proposta)
    sem = {r["id"]: d["celulas"].get(r["id"]) for r in DISPUTA["requisitos"] if r["tipo"] == "semantico"}
    if not d.get("falha", "").startswith(f"{C.FALHA}: {etapa} (") or set(sem.values()) != {"nao_informado"}:
        falhas.append(f"A {nome}: seguro devolveu {d.get('falha')!r} / {sem}")
    if d["celulas"].get("r2") != "atende" or d["celulas"].get("r3") != "atende":
        falhas.append(f"A {nome}: numéricas deixaram de ser calculadas pelo código: {d['celulas']}")
    if invalida != bool(getattr(jev, "invalidados", [])):
        falhas.append(f"A {nome}: invalidar {'não ' if invalida else ''}foi chamado ({getattr(jev, 'invalidados', None)})")
    try:
        C.comparar_proposta(jev, DISPUTA, proposta)
        falhas.append(f"A {nome}: comparar_proposta (baixo nível) não levantou erro")
    except Exception:  # noqa: BLE001 — qualquer exceção serve: o ponto é não devolver matriz
        pass


def bateria_falhas(falhas: list) -> int:
    p1 = DISPUTA["propostas"][0]
    ok = C.comparar_proposta_seguro(Duble(), DISPUTA, p1)
    assert ok["celulas"] == {"r1": "atende", "r2": "atende", "r3": "atende", "r4": "atende"} and "falha" not in ok, ok
    n = 0
    for nome, corrompe in RESPOSTAS_FALSAS:
        _confere_falha(nome, Duble(corrompe(copy.deepcopy(resposta()))), p1, "resposta inválida", falhas, True)
        n += 1
    for nome, inteira in RESPOSTAS_INTEIRAS:
        jev = Duble()
        jev.padrao = inteira
        _confere_falha(nome, jev, p1, "resposta inválida", falhas, True)
        n += 1
    jev = DubleSemInvalidar(_mexe(["answers", "req_0", "confidence"], True)(resposta()))
    _confere_falha("resposta inválida com cliente sem `invalidar`", jev, p1, "resposta inválida", falhas, False)
    n += 1
    for nome, erro in EXCECOES:
        _confere_falha(nome, Duble(erro), p1, "chamada", falhas, False)
        n += 1
    for nome, texto in ENTRADAS:
        _confere_falha(nome, Duble(), {**p1, "texto": texto}, "entrada inválida", falhas, False)
        n += 1
    # a disputa não aborta: p2 com timeout, p3 com resposta falsa; p1 válida
    duble = Duble(por_texto={DISPUTA["propostas"][1]["texto"]: TimeoutError(),
                             DISPUTA["propostas"][2]["texto"]: _mexe(["answers", "req_0", "confidence"], True)(resposta())})
    s = C.comparar_disputa_seguro(duble, DISPUTA)
    if len(s["falhas"]) != 2 or s["matriz"]["p2"]["r1"] != "nao_informado" or s["matriz"]["p3"]["r1"] != "nao_informado" \
            or s["matriz"]["p1"]["r1"] != "atende" or s["elegiveis"] != ["p1", "p2", "p3"] \
            or [q["requisito"] for q in s["perguntas"]["p2"]] != ["r1"] or [q["requisito"] for q in s["perguntas"]["p3"]] != ["r1", "r2"]:
        falhas.append(f"A disputa com falhas: {s['matriz']} elegíveis {s['elegiveis']} perguntas {s['perguntas']} falhas {s['falhas']}")
    return n + 1


def bateria_numero(falhas: list) -> int:
    r_ge = DISPUTA["requisitos"][1]
    r_le = DISPUTA["requisitos"][2]
    casos = [
        (r_ge, 12, "atende"), (r_ge, 11, "contradiz"), (r_ge, 120, "atende"), (r_ge, None, "nao_informado"),
        (r_ge, True, "nao_informado"), (r_ge, "12", "nao_informado"), (r_ge, 12.0, "atende"),
        (r_le, 20000, "atende"), (r_le, 20001, "contradiz"), (r_le, 0, "atende"), (r_le, None, "nao_informado"),
    ]
    for req, v, esperado in casos:
        got = C.celula_numerica(req, {"campos": {"garantia_meses": v, "preco_total": v}})
        if got != esperado:
            falhas.append(f"B {req['texto'][:30]} × {v!r}: {got} ≠ {esperado}")
    if C.celula_numerica(r_le, {"campos": {}}) != "nao_informado":
        falhas.append("B campo ausente deveria ser nao_informado")
    try:
        C.celula_numerica({"id": "rx", "texto": "Preço de até R$ 100.", "tipo": "numerico"}, {"campos": {}})
        falhas.append("B requisito numérico sem limite legível não levantou")
    except ValueError:
        pass
    if C.limite(r_le) != ("preco_total", "<=", 20000) or C.limite({"texto": "x"}) is not None:
        falhas.append("B limite() não lê o formato do LEIA-ME")
    ped = C.pedido(DISPUTA, DISPUTA["propostas"][0])
    if ped[2] != ["r1", "r4"] or ped[0]["requirements"] != ["Instalação inclusa no preço.", "Manutenção no primeiro ano inclusa."]:
        falhas.append(f"B numérico foi ao Jev: {ped[0]['requirements']} {ped[2]}")
    return len(casos) + 4


def bateria_valvula(falhas: list) -> int:
    n = 0
    for conf in (0.0, 0.3, 0.49, 0.5, 0.69, 0.7, 0.9, 1.0):
        n += 3
        if C.valvula_choice("meets", conf) != ("atende" if conf >= P.CONF_ATENDE else "nao_informado"):
            falhas.append(f"C válvula meets {conf}")
        if C.valvula_choice("contradicts", conf) != ("contradiz" if conf >= P.CONF_CONTRADIZ else "nao_informado"):
            falhas.append(f"C válvula contradicts {conf}")
        if C.valvula_choice("not_stated", conf) != "nao_informado":
            falhas.append(f"C válvula not_stated {conf}")
    for e, x in itertools.product((0.0, 0.2, 0.5, 0.8, 1.0), repeat=2):
        n += 1
        got = C.combinar_nouls(e, x)
        if x >= P.FAIXA_EXCLUI[1] and got != "contradiz":
            falhas.append(f"C exclusão não venceu: entrega {e} exclui {x} → {got}")
        if got == "atende" and not (e >= P.FAIXA_ENTREGA[1] and x <= P.FAIXA_EXCLUI[0]):
            falhas.append(f"C atende sem certeza: entrega {e} exclui {x}")
        if P.FAIXA_EXCLUI[0] < x < P.FAIXA_EXCLUI[1] and got != "nao_informado":
            falhas.append(f"C dúvida na exclusão não virou pergunta: entrega {e} exclui {x} → {got}")
    return n


def bateria_elegiveis(falhas: list) -> int:
    m = {"p1": {"r1": "atende", "r2": "atende", "r3": "atende", "r4": "contradiz"},
         "p2": {"r1": "contradiz", "r2": "atende", "r3": "atende", "r4": "atende"},
         "p3": {"r1": "nao_informado", "r2": "nao_informado", "r3": "atende", "r4": "nao_informado"}}
    if C.elegiveis(DISPUTA, m) != ["p1", "p3"]:
        falhas.append(f"D elegíveis: {C.elegiveis(DISPUTA, m)}")
    q = C.perguntas_ao_fornecedor(DISPUTA, m)
    if set(q) != {"p1", "p3"} or q["p1"] != [] or [x["requisito"] for x in q["p3"]] != ["r1", "r2"] \
            or "garantia em meses" not in q["p3"][1]["pergunta"] or "`" in q["p3"][1]["pergunta"]:
        falhas.append(f"D perguntas: {q}")
    todos = {p: {"r1": "contradiz", "r2": "atende", "r3": "atende", "r4": "atende"} for p in ("p1", "p2", "p3")}
    if C.elegiveis(DISPUTA, todos) != []:
        falhas.append("D disputa sem elegível deveria dar []")
    return 3


def bateria_revisao(falhas: list) -> int:
    """Achados da revisão adversarial (Codex, 2026-10-01): 2 estrutura, 5 abstenção dos Nouls, 6 negação terminal,
    7 pergunta legível, 3 P/R filtrados pela elegibilidade."""
    import run as R  # noqa: PLC0415 — só aqui, para não puxar o run no resto da bateria
    n = 0
    # 2. estrutura: requisito sem `tipo`, disputa sem propostas, proposta sem campos — nada aborta, nada reacessa
    quebrada = copy.deepcopy(DISPUTA)
    del quebrada["requisitos"][0]["tipo"]
    d = C.comparar_proposta_seguro(Duble(), quebrada, quebrada["propostas"][0])
    n += 1
    if not d.get("falha", "").startswith(f"{C.FALHA}: entrada inválida") or d["celulas"].get("r1") != "nao_informado" \
            or d["celulas"].get("r2") != "atende":
        falhas.append(f"R2 requisito sem tipo: {d}")
    for nome, disputa in (("sem propostas", {**DISPUTA, "propostas": []}), ("propostas None", {**DISPUTA, "propostas": None}),
                          ("sem requisitos", {**DISPUTA, "requisitos": []}), ("disputa None", None), ("disputa lista", [])):
        s = C.comparar_disputa_seguro(Duble(), disputa)
        n += 1
        if s["elegiveis"] != [] or not s["falhas"] or "estrutura" not in s["falhas"][0]:
            falhas.append(f"R2 {nome}: {s}")
    sem_campos = copy.deepcopy(DISPUTA)
    del sem_campos["propostas"][2]["campos"]
    s = C.comparar_disputa_seguro(Duble(), sem_campos)
    n += 1
    if s["elegiveis"] != [] or "sem campos" not in s["falhas"][0]:
        falhas.append(f"R2 proposta sem campos: {s['falhas']} {s['elegiveis']}")
    try:
        R.rodar([DISPUTA, quebrada], "choice")
        falhas.append("R2 run.rodar não recusou dado quebrado antes do lote")
    except ValueError as e:
        if "r1 com tipo None" not in str(e):
            falhas.append(f"R2 run.rodar: mensagem sem o requisito quebrado: {e}")
    n += 1
    # 5. Nouls: leitura dura e abstenção registradas
    for e, x, bruto in ((0.9, 0.1, "atende"), (0.1, 0.9, "contradiz"), (0.6, 0.4, "atende"), (0.4, 0.4, "nao_informado")):
        n += 1
        if C.bruto_nouls(e, x) != bruto:
            falhas.append(f"R5 bruto_nouls({e}, {x}) = {C.bruto_nouls(e, x)} ≠ {bruto}")
    resp = {"model": "duble", "answers": {"entrega_0": {"type": "noul", "noul": 0.6}, "exclui_0": {"type": "noul", "noul": 0.4},
                                          "entrega_1": {"type": "noul", "noul": 0.9}, "exclui_1": {"type": "noul", "noul": 0.1}}}
    lidas = C.ler_resposta(resp, ["r1", "r4"], "nouls")
    n += 1
    if lidas["r1"] != {"celula": "nao_informado", "bruto": "atende", "entrega": 0.6, "exclui": 0.4, "abstencao": True} \
            or lidas["r4"]["abstencao"] or lidas["r4"]["celula"] != "atende":
        falhas.append(f"R5 abstenção dos Nouls não registrada: {lidas}")
    # 6. baseline: negação terminal e antes de pontuação
    req = DISPUTA["requisitos"][0]
    for texto, esperado in (("Instalação: não.", "contradiz"), ("Instalação inclusa? Não", "contradiz"),
                            ("Instalação inclusa.", "atende"), ("Instalação não inclusa.", "contradiz"),
                            ("Garantia de 12 meses.", "nao_informado"), ("Instalação por conta do cliente.", "contradiz")):
        n += 1
        got = C.baseline_celula(req, {"texto": texto, "campos": {}})
        if got != esperado:
            falhas.append(f"R6 baseline {texto!r}: {got} ≠ {esperado}")
    # 7. pergunta ao fornecedor legível: sem crase, sem parêntese operacional, com a unidade
    for r, trecho in ((DISPUTA["requisitos"][1], "garantia em meses"), (DISPUTA["requisitos"][2], "preço total em reais"),
                      (DISPUTA["requisitos"][0], "Instalação inclusa no preço.")):
        n += 1
        q = C.texto_pergunta(r)
        if "`" in q or "<=" in q or ">=" in q or "_" in q or trecho not in q:
            falhas.append(f"R7 pergunta: {q!r}")
    # 3. P/R das perguntas só sobre propostas elegíveis (gabarito de um lado, previsão do outro)
    caso = copy.deepcopy(DISPUTA)
    caso["matriz"] = {"p1": {"r1": "atende", "r2": "atende", "r3": "atende", "r4": "atende"},
                      "p2": {"r1": "contradiz", "r2": "atende", "r3": "atende", "r4": "nao_informado"},
                      "p3": {"r1": "nao_informado", "r2": "nao_informado", "r3": "atende", "r4": "atende"}}
    caso["elegiveis"], caso["nota"] = ["p1", "p3"], "fácil"
    saida = {"id": "X1", "propostas": [
        {"id": "p1", "celulas": {"r1": "nao_informado", "r2": "atende", "r3": "atende", "r4": "atende"},
         "detalhes": {"r1": {"origem": "jev", "bruto": "atende", "conf": 0.3, "abstencao": True}, "r2": {"origem": "codigo"},
                      "r3": {"origem": "codigo"}, "r4": {"origem": "jev", "bruto": "atende", "conf": 0.9, "abstencao": False}}},
        {"id": "p2", "celulas": {"r1": "nao_informado", "r2": "atende", "r3": "atende", "r4": "nao_informado"},  # previsto elegível, gabarito não
         "detalhes": {"r1": {"origem": "jev", "bruto": "nao_informado", "conf": 0.9, "abstencao": False}, "r2": {"origem": "codigo"},
                      "r3": {"origem": "codigo"}, "r4": {"origem": "jev", "bruto": "nao_informado", "conf": 0.9, "abstencao": False}}},
        {"id": "p3", "celulas": {"r1": "contradiz", "r2": "nao_informado", "r3": "atende", "r4": "atende"},  # previsto inelegível, gabarito sim
         "detalhes": {"r1": {"origem": "jev", "bruto": "contradiz", "conf": 0.9, "abstencao": False}, "r2": {"origem": "codigo"},
                      "r3": {"origem": "codigo"}, "r4": {"origem": "jev", "bruto": "atende", "conf": 0.9, "abstencao": False}}}]}
    itens = R.itens_de([saida], [caso], "choice")
    r = R.resumo(itens, [caso])
    n += 1
    # gabarito: perguntas só de p3 (elegível): r1, r2 → 2. previsto: só de p1 e p2 (elegíveis previstos): p1/r1, p2/r1 → 2 (r4 é opcional)
    # interseção vazia → precisão 0, recall 0; a versão antiga contava p3/r2 (inelegível previsto) e p2/r1 (inelegível no gabarito)
    # 6 células semânticas (r1, r4 × 3 propostas), 1 abstenção (p1/r1) → cobertura 5/6
    if (r["perguntas_precisao"], r["perguntas_recall"], r["valvula"]) != (0.0, 0.0, 1) or abs(r["cobertura"] - 5 / 6) > 1e-9:
        falhas.append(f"R3/R5 P/R filtrados ou abstenção: {r['perguntas_precisao']} {r['perguntas_recall']} {r['valvula']} {r['cobertura']}")
    return n


def main() -> None:
    falhas: list[str] = []
    a, b, c, d = bateria_falhas(falhas), bateria_numero(falhas), bateria_valvula(falhas), bateria_elegiveis(falhas)
    e = bateria_revisao(falhas)
    if falhas:
        sys.exit(f"FALHOU ({len(falhas)}):\n  " + "\n  ".join(falhas[:40]))
    print(f"ok: A {a} falhas operacionais → nao_informado por proposta (nenhuma atende/contradiz; disputa não aborta; "
          f"baixo nível levanta; resposta inválida sai do cache) · B {b} comparações numéricas pelo código · "
          f"C {c} combinações de válvula/Nouls · D {d} conferências de elegíveis e perguntas · "
          f"E {e} conferências da revisão (estrutura, abstenção, negação terminal, pergunta legível, P/R)")


if __name__ == "__main__":
    main()
