"""Bateria do código do `requisito-mudou` — roda sem chave e sem rede (`python testa_falhas.py`).

Por que existe: os conjuntos rotulados não exercitam o que é do CÓDIGO e custa caro quando falha (zero falha de
rede, zero resposta fora do contrato, nenhuma história acima do teto, e o `reavaliar` só é conferido contra o
gabarito nos casos que existem). A bateria prova, com um dublê no lugar do Jev:
  A. falha operacional — resposta falsa (bool no lugar de número, ID faltando, Choice sem distribuição, vencedor fora
     dos candidatos…), exceção de rede simulada ou entrada inválida: `julgar_seguro` devolve TODOS os requisitos
     `incerto`, `reavaliar` vazio e `origem: "falha"` para AQUELA história, nunca `mantido`; o lote não aborta;
     `julgar` (baixo nível) continua levantando erro;
  B. política — grade da Choice de status (4 vencedores × probabilidades) × Choice de valor (`none`, candidato, piso):
     `substituido` só sai com valor COPIADO de um candidato; `replaced` sem valor utilizável vira `incerto`; vencedor
     abaixo do piso vira `incerto`; o valor nunca é inventado; atributo sim/indiferente só recebe `sim`; a variante
     por Nouls respeita a mesma tabela (`dropped` → negado; `changed` → substituido; `open`/dúvida → incerto);
  C. fatos do código — `reavaliar` em cada regra da tabela "o item atende quando" (térreo e casa térrea contam como
     sem escada; andar baixo até o 3º; prazo por mês/ano; locação × compra; bairro em lista; `indiferente`/`não`/`0`
     não restringem; `negado` sai do cálculo; `incerto` conserva o valor antigo; item fora do molde conta como a
     reavaliar); candidatos (número brasileiro, "850" = R$ 850.000 em compra, "3,5" = R$ 3.500 em locação, datas e
     horas fora, bairros sozinhos e somados, meses, faixa de quartos/vagas sem o atual); teto; state; baseline.
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import perguntas as P  # noqa: E402
import requisitos as R  # noqa: E402
import run as RUN  # noqa: E402

REQS = [{"id": "q1", "atributo": "orcamento", "valor": "até R$ 600.000"}, {"id": "q2", "atributo": "vagas", "valor": "1"},
        {"id": "q3", "atributo": "elevador", "valor": "indiferente"}, {"id": "q4", "atributo": "bairro", "valor": "Mooca"}]
CONVERSA = [{"de": "cliente", "texto": "oi, agora preciso de 2 vagas, compramos outro carro"},
            {"de": "corretor", "texto": "Anotado, 2 vagas. O resto segue?"}, {"de": "cliente", "texto": "segue"}]
SHORTLIST = [
    {"id": "IM-01", "resumo": "Apartamento em Mooca, 2 quartos, 1 vaga, R$ 540.000. 7º andar, com elevador; aceita pet; sem mobília; aceita financiamento; pronto para morar."},
    {"id": "IM-02", "resumo": "Apartamento em Mooca, 2 quartos, 2 vagas, R$ 585.000. 4º andar, sem elevador; não aceita pet; mobiliado; aceita financiamento; entrega em 03/2027."},
    {"id": "IM-03", "resumo": "Casa térrea em Mooca, 3 quartos, 2 vagas, R$ 598.000. Aceita pet; sem mobília; não aceita financiamento; pronto para morar."},
    {"id": "IM-04", "resumo": "Apartamento em Mooca, 2 quartos, 1 vaga, R$ 560.000. Térreo, sem elevador; aceita pet; sem mobília; aceita financiamento; pronto para morar."},
]


def _choice(vencedor: str, opcoes: list[str], p: float = 0.9) -> dict:
    resto = (1.0 - p) / (len(opcoes) - 1) if len(opcoes) > 1 else 0.0
    probs = {o: (p if o == vencedor else resto) for o in opcoes}
    return {"type": "choice", "choice": vencedor, "confidence": p, "probabilities": probs}


def resposta(status: dict | None = None, valor: dict | None = None, nouls: dict | None = None,
             requisitos: list = REQS, conversa: list = CONVERSA) -> dict:
    """Resposta VÁLIDA no formato da API para `pedido(requisitos, conversa)`. Sem argumentos: tudo `kept` com P=0,9 →
    tudo `mantido` (o pior destino possível para uma falha tolerada: se a validação deixar passar, a bateria vê)."""
    _, questions, cands = R.pedido(requisitos, conversa)
    answers = {}
    for r in requisitos:
        rid = r["id"]
        vencedor, p = (status or {}).get(rid, ("kept", 0.9))
        answers[f"{rid}_status"] = _choice(vencedor, P.STATUS, p)
        if cands[rid]:
            v = (valor or {}).get(rid, ("none", 0.9))
            answers[f"{rid}_new_value"] = _choice(v[0], [*cands[rid], "none"], v[1])
        for k in ("changed", "dropped", "open"):
            answers[f"{rid}_{k}"] = {"type": "noul", "noul": (nouls or {}).get(rid, {}).get(k, 0.05)}
    return {"model": "duble", "answers": answers, "usage": {"input_tokens": 1}}


class Duble:
    """Jev de mentira: devolve a resposta dada ou levanta a exceção dada; por história (texto do 1º turno), se pedido."""

    def __init__(self, padrao=None, por_historia: dict | None = None):
        self.padrao = padrao if padrao is not None else resposta()
        self.por_historia = por_historia or {}
        self.invalidados: list[tuple] = []  # (state, questions) que `julgar_seguro` mandou tirar do cache

    def perguntar(self, state, questions):
        saida = self.por_historia.get(state["new_turns"][0]["text"], self.padrao)
        if isinstance(saida, Exception):
            raise saida
        return saida

    def invalidar(self, state, questions) -> bool:
        self.invalidados.append((state, questions))
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
    ("Noul bool no lugar de número", _mexe(["answers", "q1_changed", "noul"], True)),
    ("Noul string", _mexe(["answers", "q2_open", "noul"], "0.9")),
    ("Noul None", _mexe(["answers", "q3_dropped", "noul"], None)),
    ("Noul fora de [0, 1]", _mexe(["answers", "q1_open", "noul"], 1.5)),
    ("Noul faltando", _mexe(["answers", "q4_changed"], apaga=True)),
    ("Choice de status faltando", _mexe(["answers", "q1_status"], apaga=True)),
    ("Choice de status com vencedor fora das opções", _mexe(["answers", "q1_status", "choice"], "maybe")),
    ("Choice de status sem distribuição", _mexe(["answers", "q2_status", "probabilities"], apaga=True)),
    ("Choice de status com distribuição incompleta", _mexe(["answers", "q2_status", "probabilities"], {"kept": 1.0})),
    ("Choice de status que não soma 1", _mexe(["answers", "q3_status", "probabilities"], {o: 0.5 for o in P.STATUS})),
    ("Choice de status contraditória (vencedor não é o máximo)",
     _mexe(["answers", "q3_status", "probabilities"], {"kept": 0.1, "replaced": 0.8, "denied": 0.05, "uncertain": 0.05})),
    ("Choice de status com confiança bool", _mexe(["answers", "q4_status", "confidence"], True)),
    ("Choice de status com probabilidade string", _mexe(["answers", "q4_status", "probabilities", "kept"], "0.9")),
    ("Choice de valor faltando (havia candidatos)", _mexe(["answers", "q2_new_value"], apaga=True)),
    ("Choice de valor com vencedor fora dos candidatos (valor inventado)", _mexe(["answers", "q2_new_value", "choice"], "7")),
    ("discriminador `type` trocado", _mexe(["answers", "q1_status", "type"], "noul")),
    ("resposta de um ID que não é objeto", _mexe(["answers", "q1_changed"], 0.5)),
    ("`answers` vazio", _mexe(["answers"], {})),
    ("`answers` None", _mexe(["answers"], None)),
    ("sem `answers`", _mexe(["answers"], apaga=True)),
]
RESPOSTAS_INTEIRAS = [("resposta None", None), ("resposta lista", []), ("resposta string", "ok"), ("resposta {}", {})]
EXCECOES = [("timeout", TimeoutError("tempo esgotado")), ("conexão recusada", ConnectionError("sem rede")),
            ("erro HTTP 503", ErroHTTP("503")), ("erro HTTP 429", ErroHTTP("429")),
            ("cache faltando no modo gravado", RuntimeError("resposta não gravada no cache")),
            ("erro não previsto dentro do cliente", KeyError("usage"))]
ENTRADAS = [("requisitos vazios", [], CONVERSA), ("requisitos None", None, CONVERSA), ("conversa vazia", REQS, []),
            ("atributo fora do vocabulário", [{"id": "q1", "atributo": "piscina", "valor": "sim"}], CONVERSA),
            ("valor vazio", [{"id": "q1", "atributo": "vagas", "valor": " "}], CONVERSA),
            ("id repetido", [REQS[0], {**REQS[1], "id": "q1"}], CONVERSA),
            ("turno sem `de` válido", REQS, [{"de": "bot", "texto": "oi"}]), ("turno sem texto", REQS, [{"de": "cliente", "texto": ""}])]


def _confere_falha(nome: str, jev, reqs, conversa, etapa: str, falhas: list) -> None:
    s = R.julgar_seguro(jev, reqs, conversa, SHORTLIST)
    ids = [r["id"] for r in reqs] if isinstance(reqs, list) and all(isinstance(r, dict) and isinstance(r.get("id"), str) for r in reqs) else []
    if s["origem"] != "falha" or s["reavaliar"] != [] or set(s["atualizacoes"]) != set(ids) \
            or any(v != "incerto" for v in s["atualizacoes"].values()) or any(v is not None for v in s["novo_valor"].values()) \
            or any(not m.startswith(f"falha operacional: {etapa} (") for m in s["motivo"].values()):
        falhas.append(f"A {nome}: julgar_seguro devolveu {s['origem']!r} / {s['atualizacoes']} / {list(s['motivo'].values())[:1]}")
    # invalidação do cache: SÓ o pedido cuja resposta veio em JSON válido e foi rejeitada pelo contrato, e exatamente ele
    esperado = [R.pedido(reqs, conversa, R.bairros_da_shortlist(SHORTLIST))[:2]] if etapa == "resposta inválida" else []
    if jev.invalidados != esperado:
        falhas.append(f"A {nome}: invalidou {len(jev.invalidados)} pedido(s), esperado {len(esperado)}")
    try:
        R.julgar(jev, reqs, conversa, SHORTLIST)
        falhas.append(f"A {nome}: julgar (baixo nível) não levantou erro")
    except Exception:  # noqa: BLE001 — qualquer exceção serve: o ponto é não devolver decisão
        pass


def bateria_falhas(falhas: list) -> int:
    n = 0
    s = R.julgar_seguro(Duble(), REQS, CONVERSA, SHORTLIST)
    assert s["origem"] == "jev" and all(v == "mantido" for v in s["atualizacoes"].values()), "o dublê válido tem de dar tudo `mantido`"
    for nome, corrompe in RESPOSTAS_FALSAS:
        _confere_falha(nome, Duble(corrompe(copy.deepcopy(resposta()))), REQS, CONVERSA, "resposta inválida", falhas)
        n += 1
    for nome, inteira in RESPOSTAS_INTEIRAS:
        jev = Duble()
        jev.padrao = inteira
        _confere_falha(nome, jev, REQS, CONVERSA, "resposta inválida", falhas)
        n += 1
    # dublê sem `invalidar` (ou que falha ao invalidar): a falha fechada continua fechando em `incerto`
    sem = Duble(_mexe(["answers", "q1_status"], apaga=True)(resposta()))
    sem.invalidar = lambda state, questions: (_ for _ in ()).throw(OSError("disco"))
    if R.julgar_seguro(sem, REQS, CONVERSA, SHORTLIST)["origem"] != "falha":
        falhas.append("A invalidar que falha derrubou a falha fechada")
    n += 1
    for nome, erro in EXCECOES:
        _confere_falha(nome, Duble(erro), REQS, CONVERSA, "chamada", falhas)
        n += 1
    for nome, reqs, conversa in ENTRADAS:
        _confere_falha(nome, Duble(), reqs, conversa, "entrada inválida", falhas)
        n += 1
    # teto: sem chamada, tudo `incerto`, origem `longa`
    longa = [{"de": "cliente", "texto": "x" * (P.TETO_CARACTERES + 1)}]
    s = R.julgar_seguro(Duble(TimeoutError()), REQS, longa, SHORTLIST)
    if s["origem"] != "longa" or any(v != "incerto" for v in s["atualizacoes"].values()) or s["reavaliar"]:
        falhas.append(f"A teto: {s['origem']} {s['atualizacoes']}")
    muitos = [{"id": f"q{i}", "atributo": "vagas", "valor": "1"} for i in range(P.TETO_REQUISITOS + 1)]
    if R.julgar_seguro(Duble(TimeoutError()), muitos, CONVERSA, SHORTLIST)["origem"] != "longa":
        falhas.append("A teto de requisitos não segurou a chamada")
    n += 2
    # o lote não aborta: `run.rodar` com o dublê; só a história com falha sai `incerto`
    casos = [{"id": f"X{i}", "requisitos_anteriores": REQS, "conversa": [{"de": "cliente", "texto": f"h{i}"}], "shortlist": SHORTLIST}
             for i in range(4)]
    duble = Duble(por_historia={"h1": TimeoutError(), "h2": _mexe(["answers", "q1_status"], apaga=True)(resposta(conversa=casos[2]["conversa"]))})
    jev_real, RUN.Jev = RUN.Jev, lambda pasta: duble
    try:
        saidas, custo = RUN.rodar(casos)
    finally:
        RUN.Jev = jev_real
    origens = [s["origem"] for s in saidas]
    if origens != ["jev", "falha", "falha", "jev"] or custo["falhas_operacionais"] != 2:
        falhas.append(f"A lote: origens {origens}, falhas contadas {custo['falhas_operacionais']}")
    return n + 1


def bateria_politica(falhas: list) -> int:
    n = 0
    cands_q2 = R.candidatos(REQS[1], CONVERSA)  # vagas: 0,2,3,4
    for vencedor in P.STATUS:
        for p in (0.3, P.P_MIN_VENCEDOR - 0.01, P.P_MIN_VENCEDOR, 0.95):
            for val in ("none", "2", "4", "baixo"):
                pv = (val if val != "baixo" else "2", 0.95 if val != "baixo" else P.P_MIN_VALOR - 0.01)
                r = resposta(status={"q2": (vencedor, p), "q3": (vencedor, p), "q1": (vencedor, p)}, valor={"q2": pv})
                s = R.decidir(r, REQS, SHORTLIST, R.pedido(REQS, CONVERSA)[2])
                n += 1
                esperado = "incerto" if p < P.P_MIN_VENCEDOR else P.ROTULO_DA_OPCAO[vencedor]
                # vagas (q2): `replaced` só vira substituido com valor copiado de um candidato acima do piso
                rot, nv = s["atualizacoes"]["q2"], s["novo_valor"]["q2"]
                if esperado == "substituido":
                    if val in ("none", "baixo"):
                        if rot != "incerto" or nv is not None:
                            falhas.append(f"B q2 replaced sem valor utilizável ({val}) → {rot} {nv!r}")
                    elif rot != "substituido" or nv != pv[0] or nv not in cands_q2:
                        falhas.append(f"B q2 replaced com valor {pv[0]!r} → {rot} {nv!r}")
                elif rot != esperado or nv is not None:
                    falhas.append(f"B q2 {vencedor} P={p} → {rot} {nv!r} (esperado {esperado}, sem valor)")
                # elevador (q3, indiferente): replaced → `sim` por regra; nunca outro valor
                rot3, nv3 = s["atualizacoes"]["q3"], s["novo_valor"]["q3"]
                if esperado == "substituido" and (rot3 != "substituido" or nv3 != "sim"):
                    falhas.append(f"B q3 replaced → {rot3} {nv3!r}")
                if esperado != "substituido" and (rot3 != esperado or nv3 is not None):
                    falhas.append(f"B q3 {vencedor} P={p} → {rot3} {nv3!r}")
                # orçamento (q1): a conversa não tem número → sem candidato → `replaced` vira `incerto`
                rot1, nv1 = s["atualizacoes"]["q1"], s["novo_valor"]["q1"]
                if (esperado == "substituido" and (rot1 != "incerto" or nv1 is not None)) or (esperado != "substituido" and rot1 != esperado):
                    falhas.append(f"B q1 sem candidato: {vencedor} P={p} → {rot1} {nv1!r}")
                # reavaliar coerente: elevador → `sim` tira IM-02 (4º andar sem elevador); 2 vagas tira IM-01 e IM-04;
                # 4 vagas tira todos; negado/incerto/mantido não tira ninguém
                fora = set()
                if rot3 == "substituido":
                    fora.add("IM-02")
                if rot == "substituido":
                    fora |= {"IM-01", "IM-04"} if nv == "2" else {"IM-01", "IM-02", "IM-03", "IM-04"}
                esp_reav = [i["id"] for i in SHORTLIST if i["id"] in fora]
                if s["reavaliar"] != esp_reav:
                    falhas.append(f"B reavaliar {vencedor} P={p} val={val}: {s['reavaliar']} (esperado {esp_reav})")
    # atributo já em `sim`: replaced não tem valor novo → incerto
    reqs = [{"id": "q1", "atributo": "pet", "valor": "sim"}]
    s = R.decidir(resposta(status={"q1": ("replaced", 0.9)}, requisitos=reqs), reqs, SHORTLIST, R.pedido(reqs, CONVERSA)[2])
    if s["atualizacoes"]["q1"] != "incerto" or s["novo_valor"]["q1"] is not None:
        falhas.append(f"B pet já `sim` + replaced → {s['atualizacoes']} {s['novo_valor']}")
    n += 1
    # variante por Nouls: tabela de combinação nas três faixas de cada Noul
    nao, meio, sim = 0.1, 0.5, 0.9
    for ch in (nao, meio, sim):
        for dr in (nao, meio, sim):
            for op in (nao, meio, sim):
                rot, _ = R.status_por_nouls({"changed": ch, "dropped": dr, "open": op})
                n += 1
                if ch == sim and dr == sim:
                    esp = "negado"
                elif ch == sim:
                    esp = "substituido"
                elif op == sim or meio in (ch, dr, op):
                    esp = "incerto"
                else:
                    esp = "mantido"
                if rot != esp:
                    falhas.append(f"B nouls {ch}/{dr}/{op} → {rot} (esperado {esp})")
    # redecidir com outra variante usa a MESMA resposta e nunca inventa valor
    r = resposta(status={"q2": ("replaced", 0.9)}, valor={"q2": ("3", 0.9)}, nouls={"q2": {"changed": 0.9}})
    s = R.decidir(r, REQS, SHORTLIST, R.pedido(REQS, CONVERSA)[2])
    o = R.redecidir(s, REQS, SHORTLIST, "nouls")
    if o["atualizacoes"]["q2"] != "substituido" or o["novo_valor"]["q2"] != "3" or o["reavaliar"] != [i["id"] for i in SHORTLIST]:
        falhas.append(f"B redecidir nouls: {o['atualizacoes']} {o['novo_valor']} {o['reavaliar']}")
    n += 1
    return n


def bateria_codigo(falhas: list) -> int:
    n = 0
    item = {i["id"]: R.ler_resumo(i["resumo"]) for i in SHORTLIST}
    casos = [  # (atributo, valor, {item: atende?})
        ("orcamento", "até R$ 560.000", {"IM-01": True, "IM-02": False, "IM-03": False, "IM-04": True}),
        ("quartos", "3", {"IM-01": False, "IM-02": False, "IM-03": True, "IM-04": False}),
        ("vagas", "2", {"IM-01": False, "IM-02": True, "IM-03": True, "IM-04": False}),
        ("vagas", "0", {"IM-01": True, "IM-02": True, "IM-03": True, "IM-04": True}),
        ("bairro", "Mooca", {"IM-01": True, "IM-02": True, "IM-03": True, "IM-04": True}),
        ("bairro", "Tatuapé ou Lapa", {"IM-01": False, "IM-02": False, "IM-03": False, "IM-04": False}),
        ("elevador", "sim", {"IM-01": True, "IM-02": False, "IM-03": True, "IM-04": True}),   # casa térrea e térreo = sem escada
        ("elevador", "indiferente", {"IM-01": True, "IM-02": True, "IM-03": True, "IM-04": True}),
        ("pet", "sim", {"IM-01": True, "IM-02": False, "IM-03": True, "IM-04": True}),
        ("pet", "não", {"IM-01": True, "IM-02": True, "IM-03": True, "IM-04": True}),
        ("mobilia", "mobiliado", {"IM-01": False, "IM-02": True, "IM-03": False, "IM-04": False}),
        ("mobilia", "sem mobília", {"IM-01": True, "IM-02": False, "IM-03": True, "IM-04": True}),
        ("mobilia", "indiferente", {"IM-01": True, "IM-02": True, "IM-03": True, "IM-04": True}),
        ("andar_baixo", "sim", {"IM-01": False, "IM-02": False, "IM-03": True, "IM-04": True}),
        ("financiamento", "sim", {"IM-01": True, "IM-02": True, "IM-03": False, "IM-04": True}),
        ("financiamento", "não", {"IM-01": True, "IM-02": True, "IM-03": True, "IM-04": True}),
        ("prazo", "mudança até 02/2027", {"IM-01": True, "IM-02": False, "IM-03": True, "IM-04": True}),
        ("prazo", "mudança até 03/2027", {"IM-01": True, "IM-02": True, "IM-03": True, "IM-04": True}),
    ]
    for atr, val, esperado in casos:
        for iid, ok in esperado.items():
            n += 1
            if R.atende(atr, val, item[iid]) != ok:
                falhas.append(f"C atende({atr}, {val!r}, {iid}) ≠ {ok}")
    # locação: preço mensal × teto mensal
    loc = R.ler_resumo("Apartamento em Pinheiros, 1 quarto, sem vaga, R$ 2.800/mês. 6º andar, com elevador; aceita pet; mobiliado; disponível a partir de 11/2026.")
    if not loc["locacao"] or loc["vagas"] != 0 or loc["entrega"] != (2026, 11) or loc["financiamento"] is not None \
            or R.atende("orcamento", "até R$ 2.700/mês", loc) or not R.atende("orcamento", "até R$ 2.800/mês", loc) \
            or R.atende("prazo", "mudança até 10/2026", loc) or not R.atende("prazo", "mudança até 11/2026", loc):
        falhas.append(f"C locação: {loc}")
    n += 1
    # reavaliar: negado sai do cálculo; incerto conserva o antigo; substituido usa o novo; fora do molde = a reavaliar
    at = {"q1": "negado", "q2": "incerto", "q3": "substituido", "q4": "mantido"}
    nv = {"q1": None, "q2": None, "q3": "sim", "q4": None}
    if R.reavaliar(REQS, at, nv, SHORTLIST) != ["IM-02"]:
        falhas.append(f"C reavaliar misto: {R.reavaliar(REQS, at, nv, SHORTLIST)}")
    at2 = {"q1": "mantido", "q2": "substituido", "q3": "mantido", "q4": "mantido"}
    if R.reavaliar(REQS, at2, {**nv, "q3": None, "q2": "2"}, [*SHORTLIST, {"id": "IM-05", "resumo": "Cobertura linda, 2 vagas"}]) != ["IM-01", "IM-04", "IM-05"]:
        falhas.append("C reavaliar: item fora do molde não foi marcado")
    n += 2
    # candidatos
    conv = lambda *t: [{"de": "cliente", "texto": x} for x in t]  # noqa: E731
    testes = [
        (("orcamento", "até R$ 750.000"), conv("meu teto agora é 680 mil", "no máximo 850", "ela tem 79 anos", "às 18h30 em 11/2026", "ele pagou 1,1 milhão"),
         ["até R$ 680.000", "até R$ 850.000", "até R$ 1.100.000"]),
        (("orcamento", "até R$ 3.000/mês"), conv("dá pra ir até 3.500", "ou 3,2 mil", "subo pra 4", "são 2 quartos"), ["até R$ 3.500", "até R$ 3.200", "até R$ 4.000"]),
        (("quartos", "2"), conv("qualquer coisa"), ["1", "3", "4", "5"]),
        (("vagas", "1"), conv("qualquer coisa"), ["0", "2", "3", "4"]),
        (("bairro", "Pompeia"), conv("pode incluir a lapa, e talvez perdizes"),  # ordem do texto, não do dicionário
         ["Lapa", "Pompeia ou Lapa", "Perdizes", "Pompeia ou Perdizes", "Lapa ou Perdizes", "Pompeia ou Lapa ou Perdizes"]),
        (("bairro", "Moema"), conv("nada de bairro novo"), []),
        (("mobilia", "indiferente"), conv("x"), ["mobiliado", "sem mobília"]),
        (("mobilia", "mobiliado"), conv("x"), ["sem mobília"]),
        (("prazo", "mudança até 11/2026"), conv("meu contrato começa em março", "ou 02/2027", "até dezembro de 2027"),
         ["mudança até 03/2027", "mudança até 02/2027", "mudança até 12/2027"]),
        (("elevador", "indiferente"), conv("minha mãe não sobe escada"), []),
        # revisão do Codex (2026-10-01), item 1: quantia explícita vale como veio; milhares implícitos só sem escala
        (("orcamento", "até R$ 600.000"), conv("tenho 15 mil de entrada", "mais 80 mil do meu pai", "o apê dele foi 1,2 milhão", "e 900k é meu limite", "ou 850"),
         ["até R$ 15.000", "até R$ 80.000", "até R$ 1.200.000", "até R$ 900.000", "até R$ 850.000"]),
        (("orcamento", "até R$ 3.000/mês"), conv("a empresa paga 70 mil por ano", "subo pra 3,5", "ou R$ 3.800"), ["até R$ 70.000", "até R$ 3.500", "até R$ 3.800"]),
        # item 3: redução ("só Vila Mariana"), "tira um e põe outro" (T035) e nome curto cadastrado ("Ahú")
        (("bairro", "Tatuapé ou Vila Mariana"), conv("pode deixar só Vila Mariana"), ["Tatuapé", "Vila Mariana"]),
        (("bairro", "Tatuapé ou Vila Mariana"), conv("quero tirar o Tatuapé e ficar com Vila Mariana ou Saúde"),
         ["Saúde", "Tatuapé ou Vila Mariana ou Saúde", "Tatuapé", "Tatuapé ou Saúde", "Vila Mariana", "Vila Mariana ou Saúde"]),
        (("bairro", "Batel"), conv("pode ser no Ahú também"), ["Ahú", "Batel ou Ahú"]),
        # item 4: ano declarado prevalece, com ou sem separador; sem ano, a data de referência
        (("prazo", "mudança até 01/2027"), conv("novembro de 2027"), ["mudança até 11/2027"]),
        (("prazo", "mudança até 01/2027"), conv("novembro 2027"), ["mudança até 11/2027"]),
        (("prazo", "mudança até 01/2027"), conv("nov/2027"), ["mudança até 11/2027"]),
        (("prazo", "mudança até 01/2027"), conv("11/2027"), ["mudança até 11/2027"]),
        (("prazo", "mudança até 01/2027"), conv("em novembro"), ["mudança até 11/2026"]),
        # item 5: data e hora em cada formato saem antes do dinheiro (nenhuma vira R$ 3.000 / R$ 15.000)
        (("orcamento", "até R$ 3.000/mês"), conv("dia 3 de novembro", "ou 3 de Novembro mesmo"), []),
        (("orcamento", "até R$ 600.000"), conv("posso dia 15", "ou 15/11", "ou 15/11/2026 às 18h30", "às 18h"), []),
    ]
    for (atr, val), c, esperado in testes:
        got = R.candidatos({"id": "q", "atributo": atr, "valor": val}, c)
        got = [g.replace("/mês", "") for g in got] if atr == "orcamento" and "/mês" in val else got
        n += 1
        if got != esperado:
            falhas.append(f"C candidatos({atr}, {val!r}): {got} (esperado {esperado})")
    if R.candidatos({"id": "q", "atributo": "orcamento", "valor": "até R$ 3.000/mês"}, conv("vai até 3.500"))[0] != "até R$ 3.500/mês":
        falhas.append("C candidatos de locação sem `/mês`")
    n += 1
    # state e pedido: nomes que as perguntas citam; uma pergunta de status e três Nouls por requisito; valor só com candidato
    st, qs, cands = R.pedido(REQS, CONVERSA)
    if set(st) != {"previous_requirements", "new_turns"} or st["new_turns"][1]["from"] != "broker" or st["previous_requirements"][0]["attribute"] != "orcamento":
        falhas.append(f"C state: {st}")
    esperadas = {f"{r['id']}_{k}" for r in REQS for k in ("status", "changed", "dropped", "open")} | {"q2_new_value"}
    if set(qs) != esperadas or qs["q2_new_value"]["criteria"].keys() != {*cands["q2"], "none"}:
        falhas.append(f"C pedido: {sorted(qs)}")
    if any(k in str(list(qs.values())) for k in ("q1_status", "q2_new_value", "q1_changed")):  # o ID não vai ao modelo
        falhas.append("C ID de pergunta dentro do texto da pergunta")
    n += 3
    # baseline: negação, número novo, "agora", hipótese, nada
    b = R.baseline([{"id": "q1", "atributo": "vagas", "valor": "2"}, {"id": "q2", "atributo": "orcamento", "valor": "até R$ 700.000"},
                    {"id": "q3", "atributo": "pet", "valor": "não"}, {"id": "q4", "atributo": "quartos", "valor": "2"},
                    {"id": "q5", "atributo": "financiamento", "valor": "sim"}],
                   conv("não preciso mais de vaga", "meu teto agora é 650 mil", "talvez a gente adote um cachorro", "vou pagar à vista"), [])
    esperado = {"q1": "negado", "q2": "substituido", "q3": "incerto", "q4": "mantido", "q5": "negado"}
    if b["atualizacoes"] != esperado or b["novo_valor"]["q2"] != "até R$ 650.000":
        falhas.append(f"C baseline: {b}")
    n += 1
    # baseline, item 2 da revisão do Codex: o ponto de milhar não parte a frase ("2.800 é o teto" reafirma, não substitui)
    # e, item 1, "15 mil" é R$ 15.000, não 15 milhões
    loc = [{"id": "q1", "atributo": "orcamento", "valor": "até R$ 2.800/mês"}]
    b = R.baseline(loc, conv("2.800 é o teto. Não passo disso"), [])
    if b["atualizacoes"]["q1"] != "mantido" or b["novo_valor"]["q1"] is not None:
        falhas.append(f"C baseline ponto de milhar: {b}")
    b = R.baseline(loc, conv("meu teto agora é 2.500"), [])
    if b["atualizacoes"]["q1"] != "substituido" or b["novo_valor"]["q1"] != "até R$ 2.500/mês":
        falhas.append(f"C baseline número com ponto: {b}")
    b = R.baseline([{"id": "q1", "atributo": "orcamento", "valor": "até R$ 600.000"}], conv("meu teto agora é 15 mil"), [])
    if b["novo_valor"]["q1"] != "até R$ 15.000":
        falhas.append(f"C baseline escala explícita: {b}")
    n += 3
    return n


def main() -> None:
    falhas: list[str] = []
    a, b, c = bateria_falhas(falhas), bateria_politica(falhas), bateria_codigo(falhas)
    if falhas:
        sys.exit(f"FALHOU ({len(falhas)}):\n  " + "\n  ".join(falhas[:40]) + ("\n  …" if len(falhas) > 40 else ""))
    print(f"ok: A {a} falhas operacionais → tudo `incerto` por história (nenhum `mantido`; lote não aborta; baixo nível levanta) · "
          f"B {b} combinações da política (valor sempre copiado de candidato; `replaced` sem valor → incerto; Nouls pela tabela) · "
          f"C {c} fatos do código (`reavaliar` por regra, candidatos, state, baseline)")


if __name__ == "__main__":
    main()
