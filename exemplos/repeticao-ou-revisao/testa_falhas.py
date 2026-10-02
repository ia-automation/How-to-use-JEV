"""Bateria do código do repetição-ou-revisão — roda sem chave e sem rede (`python testa_falhas.py`).

Por que existe: os conjuntos rotulados não exercitam o que é do CÓDIGO e custa caro quando falha (zero falha de
rede, zero resposta fora do contrato, nenhum grupo inválido ou fora da faixa). A bateria prova, com um dublê no
lugar do Jev:
  A. falha operacional — resposta falsa (bool no lugar de número, ID faltando, opção fora da lista, distribuição
     que não soma 1…), exceção de rede simulada ou grupo inválido: `julgar_seguro` devolve `revisar` com motivo
     "falha operacional" para AQUELE grupo, nunca `colapsar`, `substituir` nem `somar`; `julgar` (baixo nível)
     continua levantando erro;
  B. política — grade com as 4 opções da Choice × os três valores de cada Noul (não / dúvida / sim) × confiança:
     `colapsar` só sai com Choice repetição + Noul de repetição em `sim` + troca e soma em `não`; `somar` só com
     repetição em `não` e troca em `não`; Choice `unclear`, Noul de dúvida em `sim` ou confiança baixa → `revisar`;
  C. o que é do código — normalização conservadora, idempotência por ID, cópia só ADJACENTE, grupo todo igual sem
     chamada, `acao_vigente` derivada, state enxuto, grupo fora da faixa sem chamada, baselines, grupo de 3 em pares;
  D. o relatório não aborta com grupo inválido e conta a falha à parte.
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import copy
import itertools
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import perguntas as P  # noqa: E402
import relacao as R  # noqa: E402
import run as RUN  # noqa: E402

BAIXO = {q: P.FAIXA[q][0] / 2 for q in P.NOULS}                      # dentro do "não"
DUVIDA = {q: (P.FAIXA[q][0] + P.FAIXA[q][1]) / 2 for q in P.NOULS}  # dentro da faixa do meio
ALTO = {q: (P.FAIXA[q][1] + 1) / 2 for q in P.NOULS}                # dentro do "sim"
# O Noul que CONFIRMA cada opção da Choice (o resto em "não") — a resposta "limpa" de cada relação.
CONFIRMA = {"same_intent": "same_request_again", "revision": "replaces_previous", "additional_request": "adds_new_request"}


def msg(i: int, texto: str, minutos: int = 0, de: str = "cliente") -> dict:
    return {"id": f"m{i}", "de": de, "texto": texto, "minutos_desde_a_primeira": minutos}


G2 = [msg(1, "Pode marcar a visita terça às 15h"), msg(2, "Não, terça não dá. Marca quarta às 15h", 12)]


def resposta(choice: str = "same_intent", conf: float = 0.95, **nouls: float) -> dict:
    """Resposta VÁLIDA no formato da API, "limpa" para a opção dada. Sem argumentos → `colapsar`: o pior destino
    para uma falha tolerada num grupo que é revisão (se a validação deixar passar, a bateria vê)."""
    padrao = {**BAIXO, **({CONFIRMA[choice]: ALTO[CONFIRMA[choice]]} if choice in CONFIRMA else {})}
    resto = (1 - 0.94) / 3
    return {"model": "duble", "answers": {
        P.CHOICE: {"type": "choice", "choice": choice, "confidence": conf,
                   "probabilities": {o: 0.94 if o == choice else resto for o in P.OPCOES}},
        **{q: {"type": "noul", "noul": nouls.get(q, padrao[q])} for q in P.NOULS}}}


class Duble:
    """Jev de mentira: devolve a resposta dada (ou a de uma função do state) ou levanta a exceção dada; conta as
    chamadas e guarda os states."""

    def __init__(self, saida=None):
        self.saida, self.chamadas, self.states = saida if saida is not None else resposta(), 0, []

    def perguntar(self, state, questions):
        self.chamadas += 1
        self.states.append(state)
        if isinstance(self.saida, Exception):
            raise self.saida
        return self.saida(state) if callable(self.saida) else self.saida

    def resumo(self) -> dict:
        return {}  # o `run.py` cai no custo zerado: aqui não há medição


def _quebrada(mexe) -> dict:
    r = copy.deepcopy(resposta())
    mexe(r["answers"])
    return r


def testa_falha_operacional() -> int:
    assert R.julgar_seguro(Duble(), G2)["sinal"] == "colapsar", "o controle da bateria tem de dar `colapsar`"
    quebras = {
        "noul bool": lambda a: a["replaces_previous"].update(noul=False),
        "noul string": lambda a: a["adds_new_request"].update(noul="0.01"),
        "noul fora de [0,1]": lambda a: a["same_request_again"].update(noul=1.2),
        "noul NaN": lambda a: a["no_link_word"].update(noul=float("nan")),
        "noul faltando": lambda a: a.pop("target_not_said"),
        "noul com tipo trocado": lambda a: a["arrived_out_of_order"].update(type="score"),
        "choice fora das opções": lambda a: a[P.CHOICE].update(choice="duplicate"),
        "choice faltando": lambda a: a.pop(P.CHOICE),
        "choice com tipo trocado": lambda a: a[P.CHOICE].update(type="noul"),
        "choice sem distribuição": lambda a: a[P.CHOICE].pop("probabilities"),
        "choice com opção a mais": lambda a: a[P.CHOICE]["probabilities"].update({"other": 0.0}),
        "choice que não soma 1": lambda a: a[P.CHOICE]["probabilities"].update({"same_intent": 0.2}),
        "choice com probabilidade bool": lambda a: a[P.CHOICE]["probabilities"].update({"unclear": False}),
        "choice sem confiança": lambda a: a[P.CHOICE].pop("confidence"),
        "answers vazio": lambda a: a.clear(),
    }
    saidas = [(nome, Duble(_quebrada(mexe))) for nome, mexe in quebras.items()]
    saidas += [("timeout", Duble(TimeoutError("x"))), ("cache faltando", Duble(RuntimeError("resposta não gravada"))),
               ("resposta não é objeto", Duble(lambda state: None))]
    for nome, duble in saidas:
        s = R.julgar_seguro(duble, G2)
        assert s["sinal"] == "revisar" and s["relacao"] == "unclear" and s["origem"] == "falha", (nome, s)
        assert s["motivo"].startswith("falha operacional") and s["acao_vigente"] is None, (nome, s)
        try:
            R.julgar(duble, G2)
        except Exception:  # noqa: BLE001 — o baixo nível tem de levantar
            pass
        else:
            raise AssertionError(f"`julgar` não levantou em: {nome}")
    invalidos = {
        "não é lista": None, "uma mensagem só": G2[:1], "mensagem não é objeto": [G2[0], "texto"],
        "texto vazio": [G2[0], msg(2, "  ", 1)], "sem id": [G2[0], {**G2[1], "id": ""}],
        "texto não textual": [G2[0], {**G2[1], "texto": 15}],
        "minutos bool": [G2[0], {**G2[1], "minutos_desde_a_primeira": True}],
        "minutos ausentes": [G2[0], {k: v for k, v in G2[1].items() if k != "minutos_desde_a_primeira"}],
        "minutos negativos": [{**G2[0], "minutos_desde_a_primeira": -1}, G2[1]],
        "fora de ordem (minutos decrescentes)": [msg(1, "a", 10), msg(2, "b", 3)],
        "remetentes diferentes": [G2[0], {**G2[1], "de": "corretor"}],
        "remetente desconhecido": [{**m, "de": "bot"} for m in G2],
        "mesmo ID, textos diferentes": [G2[0], {**G2[1], "id": "m1"}],
    }
    for nome, ruim in invalidos.items():
        duble = Duble()
        s = R.julgar_seguro(duble, ruim)
        assert s["sinal"] == "revisar" and s["origem"] == "falha" and "entrada inválida" in s["motivo"] and duble.chamadas == 0, (nome, s)
        assert R.baselines_seguro(ruim) == {b: "unclear" for b in R.BASELINES}, nome
    return len(saidas) + len(invalidos)


def testa_politica() -> int:
    """Grade inteira de `politica`: 4 opções × 3^7 Nouls × 3 confianças, contra a regra escrita de novo aqui."""
    n = contagem = 0
    vistos = set()
    for op, conf in itertools.product(P.OPCOES, (P.CONF_MIN - 0.1, P.CONF_MIN, 0.95)):
        for combo in itertools.product((BAIXO, DUVIDA, ALTO), repeat=len(P.NOULS)):
            nouls = {q: nivel[q] for q, nivel in zip(P.NOULS, combo)}
            s = {q: R._faixa(nouls[q], *P.FAIXA[q]) for q in P.NOULS}
            rel, motivo = R.politica({"choice": op, "conf": conf, "nouls": nouls})
            n += 1
            livre = op != "unclear" and conf >= P.CONF_MIN and not any(s[q] is True for q in P.NOULS_DUVIDA)
            troca, mesma = s["replaces_previous"], s["same_request_again"]
            esperado = "unclear"
            if livre and op == "same_intent" and mesma is True and troca is False and all(s[q] is False for q in P.NOULS_SOMA):
                esperado = "same_intent"
            if livre and op == "revision" and troca is True and mesma is not True:
                esperado = "revision"
            if livre and op == "additional_request" and any(s[q] is True for q in P.NOULS_SOMA) and mesma is False and troca is False:
                esperado = "additional_request"
            assert rel == esperado, (op, conf, nouls, rel, motivo)
            # as duas guardas do erro caro, ditas à parte
            assert rel != "same_intent" or troca is False, "colapsou sem a troca em `não`"
            assert rel != "additional_request" or mesma is False, "somou sem a repetição em `não`"
            assert rel in ("unclear", op), "a política só confirma a Choice ou manda revisar"
            vistos.add(rel)
            contagem += rel != "unclear"
    assert vistos == set(P.OPCOES) and contagem > 0
    return n


def testa_codigo() -> int:
    n = 0

    def ok(cond, nome):
        nonlocal n
        assert cond, nome
        n += 1

    # normalização conservadora
    ok(R.normalizar("  Vocês têm horário  pra visita no SÁBADO??") == R.normalizar("vocês têm horário pra visita no sábado?"), "caixa, espaços e pontuação final")
    ok(R.normalizar("visita às 10,30") != R.normalizar("visita às 10.30"), "pontuação interna fica (número não é adivinhado)")
    ok(R.normalizar("ape da vila nova sabado") != R.normalizar("apê da Vila Nova sábado"), "acento fica: retry com erro de digitação vai ao Jev")
    ok(R.normalizar("*11h") != R.normalizar("11h"), "o asterisco de correção fica")
    ok(R.palavras("Quarta 15h, pode ser?") == {"quarta", "15h", "pode", "ser"} and R.jaccard("a b", "b c") == 1 / 3, "palavras e Jaccard")

    # grupo todo igual: same_intent sem chamada; acao_vigente = a primeira
    for grupo in ([msg(1, "Quero visita sábado 10h"), msg(2, "quero visita  sábado 10h!", 95)],
                  [msg(1, "?"), msg(2, "??", 1), msg(3, "?", 2)]):
        duble = Duble(resposta("revision"))
        s = R.julgar_seguro(duble, grupo)
        ok(s["relacao"] == "same_intent" and s["sinal"] == "colapsar" and s["origem"] == "codigo" and duble.chamadas == 0
           and s["acao_vigente"] == "m1", f"igualdade exata sem chamada: {s}")
    # idempotência por ID: a mesma mensagem entregue duas vezes sai antes de tudo
    duble = Duble(resposta("revision"))
    s = R.julgar_seguro(duble, [G2[0], G2[0], G2[1]])
    ok(duble.chamadas == 1 and duble.states[0]["earlier_messages"] == [G2[0]["texto"]] and s["colapsadas_pelo_codigo"] == ["m1"]
       and s["acao_vigente"] == "m2", f"mesmo ID duas vezes: {s}")

    # reentrega NO FIM não ressuscita o pedido corrigido (Codex 2026-10-01): [m1 quinta, m2 sexta, m1 quinta]
    re_fim = [msg(1, "pode ser quinta"), msg(2, "melhor sexta"), msg(1, "pode ser quinta")]
    duble = Duble(resposta("revision"))
    s = R.julgar_seguro(duble, re_fim)
    ok(duble.chamadas == 1 and s["sinal"] == "substituir" and s["acao_vigente"] == "m2" and s["colapsadas_pelo_codigo"] == ["m1"]
       and R.vigente("revision", re_fim) == "m2" and R.vigente("same_intent", re_fim) == "m1", f"reentrega no fim: {s}")
    # contrato da saída: contexto obrigatório = as distintas; `substituir` nunca autoriza descarte
    ok(s["ids_de_contexto_obrigatorio"] == ["m1", "m2"] and s["descartar_anterior"] is False, f"contexto na revisão: {s}")
    for nome, s in (("falha", R.julgar_seguro(Duble({}), G2)), ("entrada inválida", R.julgar_seguro(Duble(), [G2[0], "x", G2[1]])),
                    ("colapsar", R.julgar_seguro(Duble(), G2)), ("somar", R.julgar_seguro(Duble(resposta("additional_request")), G2))):
        ok(s["ids_de_contexto_obrigatorio"] == ["m1", "m2"] and s["descartar_anterior"] is False, f"contexto em {nome}: {s}")
    ok(R.julgar_seguro(Duble(), None)["ids_de_contexto_obrigatorio"] == [] and R.sem_reentregas("x") == [], "contexto sem grupo legível")

    # cópia adjacente sai; o Jev vê só as distintas; acao_vigente continua sendo a ÚLTIMA do grupo
    g3 = [msg(1, "quero agendar visita quarta 14h"), msg(2, "Quero agendar visita quarta 14h.", 1), msg(3, "na verdade quinta 14h", 9)]
    duble = Duble(resposta("revision"))
    s = R.julgar_seguro(duble, g3)
    ok(duble.chamadas == 1 and duble.states[0] == {"from": "client", "earlier_messages": [g3[0]["texto"]], "last_message": g3[2]["texto"]},
       f"state enxuto: {duble.states}")
    ok(s["relacao"] == "revision" and s["sinal"] == "substituir" and s["acao_vigente"] == "m3" and s["colapsadas_pelo_codigo"] == ["m2"]
       and s["ids_de_contexto_obrigatorio"] == ["m1", "m3"], f"{s}")
    # a cópia da ÚLTIMA também sai, e a vigente segue a regra do LEIA-ME (a última do grupo)
    s = R.julgar_seguro(Duble(resposta("revision")), [g3[0], g3[2], {**g3[2], "id": "m9"}])
    ok(s["acao_vigente"] == "m9" and s["colapsadas_pelo_codigo"] == ["m9"], f"{s}")
    # NÃO adjacente não é cópia: voltar à primeira depois de uma mudança desfaz a mudança
    volta = [msg(1, "Marca terça 15h"), msg(2, "Melhor quarta 15h", 20), msg(3, "marca terça 15h", 26)]
    duble = Duble(resposta("revision"))
    s = R.julgar_seguro(duble, volta)
    ok(duble.chamadas == 1 and len(duble.states[0]["earlier_messages"]) == 2 and s["colapsadas_pelo_codigo"] == [], f"{s}")
    # acao_vigente por relação
    ok(R.julgar_seguro(Duble(resposta("additional_request")), G2)["acao_vigente"] is None
       and R.julgar_seguro(Duble(resposta("unclear")), G2)["acao_vigente"] is None
       and R.julgar_seguro(Duble(), G2)["acao_vigente"] == "m1", "acao_vigente derivada")
    # corretor vira `broker`; minutos só entram na variante
    duble = Duble()
    R.julgar_seguro(duble, [{**m, "de": "corretor"} for m in G2])
    ok(duble.states[0]["from"] == "broker" and isinstance(duble.states[0]["last_message"], str), "remetente e state sem minutos")
    with RUN._com(MINUTOS_NO_STATE=True):
        duble = Duble()
        R.julgar_seguro(duble, G2)
        ok(duble.states[0]["last_message"] == {"text": G2[1]["texto"], "minutes_since_first": 12}, "variante com minutos")

    # fora da faixa validada: revisar sem chamada
    quatro = [msg(i, f"pedido número {i}", i) for i in range(1, 5)]
    longo = [msg(1, "x" * P.TETO_CARACTERES), msg(2, "y", 1)]
    for grupo in (quatro, longo):
        duble = Duble()
        s = R.julgar_seguro(duble, grupo)
        ok(s["sinal"] == "revisar" and s["origem"] == "longo" and duble.chamadas == 0, f"fora da faixa: {s}")

    # baselines: nunca dizem unclear em grupo válido
    b = R.baselines([msg(1, "Agenda visita no cód. 2041 sexta 9h"), msg(2, "agenda visita no cód. 2041 sexta 9h", 1)])
    ok(b == {"igualdade": "same_intent", "jaccard": "same_intent", "ultima": "revision"}, f"{b}")
    b = R.baselines([msg(1, "Me manda as fotos da casa"), msg(2, "E aceita financiamento?", 1)])
    ok(b == {"igualdade": "additional_request", "jaccard": "additional_request", "ultima": "revision"}, f"{b}")

    # grupo de 3 em pares: composição no código
    tres = [msg(1, "primeira"), msg(2, "segunda", 1), msg(3, "terceira", 2)]
    tabela = {("same_intent", "revision"): "revision", ("same_intent", "additional_request"): "additional_request",
              ("revision", "revision"): "revision", ("revision", "same_intent"): "revision",
              ("additional_request", "additional_request"): "additional_request", ("additional_request", "same_intent"): "additional_request",
              ("additional_request", "revision"): "unclear", ("revision", "additional_request"): "unclear",
              ("unclear", "revision"): "unclear", ("same_intent", "unclear"): "unclear", ("same_intent", "same_intent"): "same_intent"}
    with RUN._com(GRUPO_DE_3="pares"):
        for (a, b2), esperado in tabela.items():
            duble = Duble(lambda state, a=a, b2=b2: resposta(a if state["earlier_messages"] == ["primeira"] else b2))
            s = R.julgar_seguro(duble, tres)
            ok(s["relacao"] == esperado and duble.chamadas == 2, f"pares {a} + {b2}: {s}")
        duble = Duble()
        R.julgar_seguro(duble, G2)
        ok(duble.chamadas == 1, "grupo de 2 não muda na variante em pares")
    return n


def testa_relatorio() -> int:
    """Grupo inválido não aborta o relatório: conta como `revisar` no Jev E nos baselines, à parte."""
    caso = lambda i, mensagens, relacao, vigente: {"id": f"BT-{i}", "mensagens": mensagens, "relacao": relacao,  # noqa: E731
                                                  "acao_vigente": vigente, "nota": "difícil: bateria — dublê"}
    casos = [caso(1, [G2[0], {**G2[0], "id": "m2", "minutos_desde_a_primeira": 1}], "same_intent", "m1"),  # código, sem chamada
             caso(2, G2, "revision", "m2"),                                                                # dublê diz revisão
             caso(3, None, "unclear", None), caso(4, [msg(1, "a", 5), msg(2, "b", 1)], "revision", "m2"),  # inválidos
             caso(5, [G2[0], {**G2[1], "texto": ""}], "additional_request", None)]
    jev_real, RUN.Jev = RUN.Jev, lambda pasta: Duble(resposta("revision"))
    try:
        texto, resumo = RUN.secao_conjunto("bateria", {"versao": 0, "autor": "bateria", "casos": casos})
    finally:
        RUN.Jev = jev_real
    assert resumo["custo"]["falha"] == 3 and resumo["custo"]["codigo"] == 1, resumo["custo"]
    assert "3 falha(s) operacional(is)" in texto and "BT-3, BT-4, BT-5" in texto
    j, b = resumo["variantes"][RUN.JEV]["_bruto"], resumo["variantes"][RUN.B_ULT]["_bruto"]
    assert j["acerto"] == 3 / 5 and j["revisou_sem"] == 2 and j["unclear_revisar"] == 1 and j["perdida"] == 0, j
    assert b["revisou_sem"] == 2 and b["unclear_revisar"] == 1, b
    return len(casos)


if __name__ == "__main__":
    print(f"A. falha operacional → revisar: {testa_falha_operacional()} casos ok")
    print(f"B. política (grade): {testa_politica()} combinações ok")
    print(f"C. código (normalização, ID, cópia adjacente, state, faixa, baselines, pares): {testa_codigo()} checagens ok")
    print(f"D. relatório com grupo inválido: {testa_relatorio()} grupos, relatório fechado e falhas contadas à parte")
