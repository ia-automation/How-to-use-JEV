"""Bateria do CÓDIGO da próxima pergunta — roda sem chave e sem rede (`python testa_codigo.py`).

Por que existe (revisão do Codex, 2026-10-01): os quatro achados são de código, e os conjuntos rotulados têm um caso
de cada no máximo. Com um dublê no lugar do Jev (o que se testa é código nosso, não o modelo), a bateria prova:
  A. normalizador (`valores.py`) — frases com "até 600", "600 mil", "600k", "1,2 mi", por extenso, prestação, valor
     mensal, correção, preço citado, e números que NÃO são dinheiro (quartos, anos, data, anúncio): número, escala e
     a leitura da regra do LEIA-ME com aluguel e sem aluguel. Inclui a frase do PP-T022.
  B. regra do orçamento (`proxima.regra_orcamento`) — grade de leituras × Noul × aluguel: só bloqueia com valor
     declarado E lido; leitura ambígua nunca bloqueia nem vira candidata.
  C. portão de ponta a ponta — o PP-T022 com o Noul da rodada 1 (0,43) não pergunta `orcamento`; preço de anúncio
     não bloqueia; anúncio citado bloqueia bairro e quartos por regra; todo bloqueio sai com motivo, evidência e margem.
  D. 2ª etapa — resposta da Choice `next` com discriminador trocado, opção de fora, distribuição incompleta,
     confiança booleana, ID faltando ou exceção: `julgar` levanta erro; `julgar_seguro` devolve revisão, nunca pergunta.
  E. custo — com `todas=False` nenhuma requisição leva `single_choice`; com `todas=True` ela vai numa requisição
     à parte, depois das da principal.
Nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import perguntas as P  # noqa: E402
import proxima as X  # noqa: E402
import valores as V  # noqa: E402

CATALOGO = json.loads((AQUI / "dados" / "rascunho.json").read_text(encoding="utf-8"))["casos"][0]["catalogo"]
falhas: list[str] = []


def confere(ok: bool, nome: str) -> None:
    if not ok:
        falhas.append(nome)


# ---------------------------------------------------------------------------------------- A. normalizador
# frase → (número com a escala dita, escala dita, leitura com aluguel, leitura sem aluguel).
# Leitura = (estado, valor em reais, tipo). None no lugar do número = a frase não tem valor em dinheiro.
R, C, PR, AMB = "respondida", "confirmar", "prestacao", "ambiguo"
FRASES = [
    ("alugar, 3 quartos, até 6",                 6, None,      (R, 6000, "aluguel"),     (AMB, None, None)),          # PP-T022
    ("quero alugar kitnet, até 600",             600, None,    (C, None, None),          (R, 600000, "preco")),
    ("até 600 mil",                              600000, "mil", (AMB, None, None),        (R, 600000, "preco")),
    ("uns 600k",                                 600000, "mil", (AMB, None, None),        (R, 600000, "preco")),
    ("até 1,2 mi, financiado",                   1200000, "milhão", (AMB, None, None),    (R, 1200000, "preco")),
    ("pensei em seiscentos mil",                 600000, "mil", (AMB, None, None),        (R, 600000, "preco")),
    ("até seiscentos",                           600, None,    (C, None, None),          (R, 600000, "preco")),
    ("um milhão e meio",                         1500000, "milhão", (AMB, None, None),    (R, 1500000, "preco")),
    ("meio milhão no máximo",                    500000, "milhão", (AMB, None, None),     (R, 500000, "preco")),
    ("1 milhão e 200 mil",                       1200000, "milhão", (AMB, None, None),    (R, 1200000, "preco")),
    ("consigo pagar 2.500 por mês",              2500, None,   (R, 2500, "aluguel"),     (PR, 2500, "prestacao")),
    ("dois mil e quinhentos por mês",            2500, "mil",  (R, 2500, "aluguel"),     (PR, 2500, "prestacao")),
    ("prestação de 3 mil",                       3000, "mil",  (AMB, None, None),        (PR, 3000, "prestacao")),
    ("cabe 3 mil de prestação",                  3000, "mil",  (AMB, None, None),        (PR, 3000, "prestacao")),
    ("parcela de no máximo 1.800",               1800, None,   (AMB, None, None),        (PR, 1800, "prestacao")),
    ("até 4 mil",                                4000, "mil",  (R, 4000, "aluguel"),     (AMB, None, None)),
    ("até 2500",                                 2500, None,   (R, 2500, "aluguel"),     (AMB, None, None)),
    ("até R$ 3.300",                             3300, "reais", (R, 3300, "aluguel"),     (AMB, None, None)),
    ("até 600 reais",                            600, "reais", (R, 600, "aluguel"),      (AMB, None, None)),
    ("até 450000",                               450000, None, (AMB, None, None),        (R, 450000, "preco")),
    ("até 800.000",                              800000, None, (AMB, None, None),        (R, 800000, "preco")),
    ("meu orçamento é 500 mil",                  500000, "mil", (AMB, None, None),        (R, 500000, "preco")),
    ("na faixa dos 700",                         700, None,    (C, None, None),          (R, 700000, "preco")),
    ("até 600 por mês... quer dizer, 1600",      1600, None,   (R, 1600, "aluguel"),     (PR, 1600, "prestacao")),   # vale a correção
    ("até 700. se for bom dá pra esticar até 800", 800, None,  (C, None, None),          (R, 800000, "preco")),      # vale a última
    ("o anúncio diz R$ 2.900",                   2900, "reais", (R, 2900, "aluguel"),     (AMB, None, None)),         # quem decide se é do cliente é o Noul
    ("tenho 100 mil de entrada",                 100000, "mil", (AMB, None, None),        (AMB, None, None)),
    ("preciso mudar até 2026",                   2026, None,   (AMB, None, None),        (AMB, None, None)),          # pode ser ano
    ("mil e duzentos reais",                     1200, "mil",  (R, 1200, "aluguel"),     (AMB, None, None)),
    # números que NÃO são dinheiro
    ("3 quartos, 2 vagas, 68 m2",                None, None, None, None),
    ("o apê do anúncio 4521 ainda tá disponível?", None, None, None, None),
    ("tô viajando até o dia 20",                 None, None, None, None),
    ("meu pai tem 80 anos, 1 quarto",            None, None, None, None),
    ("preciso mudar até 20 de outubro",          None, None, None, None),
    ("um quarto já serve, 2 no máximo",          None, None, None, None),
    ("o condomínio de 800 pesa",                 None, None, None, None),
    ("quanto tá o aluguel de um 2 quartos no cambuí?", None, None, None, None),
    ("visita amanhã às 10",                      None, None, None, None),
]


def bateria_normalizador() -> int:
    for frase, numero, escala, com_aluguel, sem_aluguel in FRASES:
        m = V.principal(V.mencoes([{"de": "agente", "texto": "Tenho um de R$ 990 mil."}, {"de": "cliente", "texto": frase}]))
        if numero is None:
            confere(m is None, f"A: {frase!r} não devia ter valor, leu {m and m['trecho']!r}")
            continue
        if m is None:
            confere(False, f"A: {frase!r} sem valor lido")
            continue
        confere(m["numero"] == numero and m["escala"] == escala, f"A: {frase!r} → {m['numero']} / {m['escala']}")
        for aluguel, esperado in ((True, com_aluguel), (False, sem_aluguel)):
            l = V.ler(m, aluguel, P.PISO_PRECO)
            confere((l["estado"], l["valor"], l["tipo"]) == esperado,
                    f"A: {frase!r} aluguel={aluguel} → {(l['estado'], l['valor'], l['tipo'])}, esperado {esperado}")
    # o agente citando preço nunca vira menção do cliente
    confere(V.mencoes([{"de": "agente", "texto": "R$ 440 mil, 2 quartos"}, {"de": "cliente", "texto": "gostei"}]) == [],
            "A: preço dito pelo agente virou valor do cliente")
    return len(FRASES) + 1


# ---------------------------------------------------------------------------------------- B. regra do orçamento
def bateria_regra() -> int:
    n = 0
    for (frase, numero, *_), declarado, aluguel in itertools.product(FRASES, [0.02, 0.2, 0.35, 0.49, 0.5, 0.9], [True, False]):
        achadas = V.mencoes([{"de": "cliente", "texto": frase}])
        r, n = X.regra_orcamento(achadas, declarado, aluguel), n + 1
        leitura = V.ler(V.principal(achadas), aluguel, P.PISO_PRECO)["estado"] if numero is not None else None
        nome = f"B: {frase!r} declarado={declarado} aluguel={aluguel} → {r['estado']}"
        if r["estado"] == "respondida":  # bloqueio só com valor declarado E lido pela regra
            confere(declarado >= P.LIMIAR["respondida"] and leitura == "respondida", nome + " (bloqueio sem base)")
        if leitura == "ambiguo":  # ambíguo nunca bloqueia e só fica em aberto se o Jev diz que não é do cliente
            confere(r["estado"] == ("aberta" if declarado <= P.LIMIAR["declarado_nao"] else "revisar"), nome + " (ambíguo)")
        if leitura is None:  # o código não leu nada: Noul alto não bloqueia sozinho
            confere(r["estado"] == ("revisar" if declarado >= P.LIMIAR["respondida"] else "aberta"), nome + " (sem valor)")
        if leitura == "respondida" and P.LIMIAR["declarado_nao"] < declarado < P.LIMIAR["respondida"]:
            confere(r["estado"] == "revisar", nome + " (dúvida do Noul com valor lido)")
        if leitura in ("confirmar", "prestacao"):
            confere(r["estado"] in ("confirmar", "aberta"), nome + " (devia ser candidata)")
    return n


# ---------------------------------------------------------------------------------------- dublê
def resposta_valida(questions: dict, nouls: dict, escolhas: dict) -> dict:
    """Resposta no formato da API para QUALQUER conjunto de perguntas: Noul = valor dado (padrão 0,02); Choice =
    opção dada (padrão: a última, que é a válvula) com 0,9 de probabilidade."""
    answers = {}
    for q, p in questions.items():
        if p["type"] == "noul":
            answers[q] = {"type": "noul", "noul": nouls.get(q, 0.02)}
        else:
            opcoes = list(p["criteria"])
            vence = escolhas.get(q, opcoes[-1])
            resto = 0.1 / max(len(opcoes) - 1, 1)
            answers[q] = {"type": "choice", "choice": vence, "confidence": 0.85,
                          "probabilities": {o: (0.9 if o == vence else resto) for o in opcoes} if len(opcoes) > 1 else {vence: 1.0}}
    return {"model": "duble", "answers": answers, "usage": {"input_tokens": 0}}


class Duble:
    """Jev de mentira. `estraga` recebe (questions, resposta válida) e devolve a resposta a entregar ou levanta."""

    def __init__(self, nouls: dict | None = None, escolhas: dict | None = None, estraga=None):
        self.nouls, self.escolhas, self.estraga, self.pedidos = nouls or {}, escolhas or {}, estraga, []

    def perguntar(self, state, questions):
        self.pedidos.append({"state": state, "questions": questions})
        r = resposta_valida(questions, self.nouls, self.escolhas)
        return self.estraga(questions, r) if self.estraga else r


def conversa(texto: str) -> list[dict]:
    return [{"de": "cliente", "texto": texto}]


# ---------------------------------------------------------------------------------------- C. portão de ponta a ponta
T022 = conversa("alugar, 3 quartos, até 6")
ALUGUEL = {"answered.purpose": 0.97, "answered.bedrooms": 0.98, "rental": 0.94}


def bateria_portao() -> int:
    ids = lambda s, campo: [b["id"] for b in s[campo]]  # noqa: E731
    # 1. PP-T022 com o valor declarado: `orcamento` bloqueada pela REGRA, com R$ 6 mil de evidência; pergunta bairro
    s = X.julgar(Duble({**ALUGUEL, "answered.budget": 0.9}), T022, {}, CATALOGO)
    b = next((x for x in s["bloqueadas"] if x["id"] == "orcamento"), None)
    confere(s["pergunta"] == "bairro" and b is not None and b["motivo"] == "regra" and b["valor"]["valor"] == 6000
            and b["valor"]["tipo"] == "aluguel", f"C1: PP-T022 declarado → {s['pergunta']}, {b}")
    # 2. PP-T022 com o Noul que a rodada 1 mediu (0,43): revisão do item; a pergunta é bairro, NUNCA orcamento
    s = X.julgar(Duble({**ALUGUEL, "answered.budget": 0.43}), T022, {}, CATALOGO)
    confere(s["pergunta"] == "bairro" and ids(s, "em_revisao") == ["orcamento"] and "orcamento" not in s["candidatas"],
            f"C2: PP-T022 com Noul 0,43 → {s['pergunta']}, revisão {ids(s, 'em_revisao')}")
    # 3. o mesmo, mas sem outra essencial faltando: sem sugestão (revisar), nem pergunta nem NQN
    s = X.julgar(Duble({**ALUGUEL, "answered.budget": 0.43, "answered.neighbourhood": 0.97}), T022, {}, CATALOGO)
    confere(s["pergunta"] is None and s["revisar"] and not s["falha"], f"C3: essencial em revisão → {s['pergunta']}")
    # 4. em toda a grade do Noul, o PP-T022 nunca sai com `orcamento` como pergunta (valor lido = respondida)
    for v in [0.0, 0.1, 0.2, 0.21, 0.3, 0.43, 0.49, 0.5, 0.7, 1.0]:
        s = X.julgar(Duble({**ALUGUEL, "answered.budget": v, "answered.neighbourhood": 0.97}), T022, {}, CATALOGO)
        esperado = "orcamento" if v <= P.LIMIAR["declarado_nao"] else None if v < P.LIMIAR["respondida"] else "NQN ou secundária"
        confere((s["pergunta"] == "orcamento") == (esperado == "orcamento"), f"C4: Noul {v} → {s['pergunta']}")
    # 5. aluguel + "até 600": candidata como confirmação (LEIA-ME), com a leitura na saída
    s = X.julgar(Duble({**ALUGUEL, "answered.budget": 0.9, "answered.neighbourhood": 0.97}), conversa("alugar kitnet na pampulha, até 600"), {}, CATALOGO)
    confere(s["pergunta"] == "orcamento" and s["orcamento"]["estado"] == "confirmar", f"C5: {s['pergunta']} {s['orcamento']}")
    # 6. "até 600" sem aluguel: R$ 600 mil, bloqueada pela regra
    s = X.julgar(Duble({"answered.budget": 0.9, "rental": 0.49}), conversa("procuro apê em pinheiros, até 600"), {}, CATALOGO)
    b = next((x for x in s["bloqueadas"] if x["id"] == "orcamento"), None)
    confere(b is not None and b["valor"]["valor"] == 600000 and b["valor"]["tipo"] == "preco", f"C6: {b}")
    # 7. preço do anúncio (Noul baixo): não bloqueia `orcamento`; anúncio citado bloqueia bairro e quartos por REGRA
    s = X.julgar(Duble({"answered.purpose": 0.97, "rental": 0.97, "specific_property": 0.91, "answered.budget": 0.05}),
                 conversa("esse apê da rua x aceita cachorro? o anúncio diz R$ 2.900"), {}, CATALOGO)
    regra = {x["id"]: x for x in s["bloqueadas"] if x["detalhe"] == "anúncio específico"}
    confere("orcamento" not in ids(s, "bloqueadas") and s["pergunta"] == "orcamento" and set(regra) == {"bairro", "quartos"}
            and all(x["motivo"] == "regra" for x in regra.values()), f"C7: {s['pergunta']} {ids(s, 'bloqueadas')}")
    # 8. todo bloqueio carrega motivo, evidência, Nouls e margem em [0, 1]
    for x in s["bloqueadas"] + s["em_revisao"]:
        confere(x["motivo"] in ("noul", "regra") and {"id", "detalhe", "valor", "nouls", "margem"} <= set(x)
                and 0.0 <= x["margem"] <= 1.0, f"C8: bloqueio sem evidência {x}")
    # 9. o Jev vê valor declarado e o código não leu nenhum → revisão, não bloqueio
    s = X.julgar(Duble({"answered.budget": 0.9}), conversa("isso, esse valor que vc falou"), {}, CATALOGO)
    confere(ids(s, "em_revisao") == ["orcamento"] and "orcamento" not in ids(s, "bloqueadas"), f"C9: {s['orcamento']}")
    return 18


# ---------------------------------------------------------------------------------------- D. validação da 2ª etapa
COMPLETA = {"answered.purpose": 0.97, "answered.budget": 0.97, "answered.neighbourhood": 0.97, "answered.bedrooms": 0.97}
CONVERSA_COMPLETA = conversa("quero comprar pra morar, até 800 mil, 2 quartos em moema")


def _muda(campo: str, valor):
    def f(questions, r):
        if "next" in questions:
            r["answers"]["next"][campo] = valor
        return r
    return f


def _sem(campo: str):
    def f(questions, r):
        if "next" in questions:
            r["answers"]["next"].pop(campo, None)
        return r
    return f


def _so_na_next(troca):
    def f(questions, r):
        return troca(r) if "next" in questions else r
    return f


def _levanta(erro: Exception):
    def f(questions, r):
        if "next" in questions:
            raise erro
        return r
    return f


ESTRAGOS = {
    "discriminador `type` trocado": _muda("type", "noul"),
    "discriminador `type` de score": _muda("type", "score"),
    "opção fora das candidatas": _muda("choice", "budget"),
    "opção inexistente": _muda("choice", "qualquer"),
    "`choice` ausente": _sem("choice"),
    "distribuição ausente": _sem("probabilities"),
    "distribuição incompleta": _muda("probabilities", {"no_question_needed": 1.0}),
    "distribuição que não soma 1": _so_na_next(lambda r: (r["answers"]["next"]["probabilities"].update(no_question_needed=0.5), r)[1]),
    "probabilidade em string": _so_na_next(lambda r: (r["answers"]["next"]["probabilities"].update(no_question_needed="0.9"), r)[1]),
    "confiança booleana": _muda("confidence", True),
    "confiança ausente": _sem("confidence"),
    "confiança NaN": _muda("confidence", float("nan")),
    "ID `next` faltando": _so_na_next(lambda r: (r["answers"].pop("next"), r)[1]),
    "`next` que não é objeto": _so_na_next(lambda r: (r["answers"].update(next="parking"), r)[1]),
    "resposta sem `answers`": _so_na_next(lambda r: {"model": "duble"}),
    "resposta que não é objeto": _so_na_next(lambda r: None),
    "timeout": _levanta(TimeoutError("tempo esgotado")),
    "erro de rede": _levanta(ConnectionError("sem rede")),
    "cache faltando": _levanta(RuntimeError("resposta não gravada no cache")),
}


def bateria_etapa2() -> int:
    ok = X.julgar(Duble(COMPLETA, {"next": "parking"}), CONVERSA_COMPLETA, {}, CATALOGO)
    confere(ok["pergunta"] == "vagas" and ok["etapas"] == ["1", "2"], f"D0: caminho válido → {ok['pergunta']} {ok['etapas']}")
    for nome, estraga in ESTRAGOS.items():
        try:
            saida = X.julgar(Duble(COMPLETA, {"next": "parking"}, estraga), CONVERSA_COMPLETA, {}, CATALOGO)
            confere(False, f"D: {nome} — `julgar` consumiu a resposta e devolveu {saida['pergunta']!r}")
        except Exception:  # noqa: BLE001 — o baixo nível tem de levantar
            pass
        s = X.julgar_seguro(Duble(COMPLETA, {"next": "parking"}, estraga), CONVERSA_COMPLETA, {}, CATALOGO)
        confere(s["pergunta"] is None and s["revisar"] and s["falha"] and s["motivo"].startswith("falha operacional: 2ª requisição")
                and s["etapas"] in (["1"], ["1", "2"]), f"D: {nome} — `julgar_seguro` devolveu {s['pergunta']!r} / {s['motivo']}")
    # a mesma validação vale para a `next` que vem na requisição de comparação (essencial faltando, todas=True)
    s = X.julgar_seguro(Duble({"rental": 0.9}, {}, ESTRAGOS["discriminador `type` trocado"]), conversa("quero alugar"), {}, CATALOGO, todas=True)
    confere(s["pergunta"] is None and s["falha"] and "comparação" in s["motivo"], f"D: comparação inválida → {s['motivo']}")
    # 1ª etapa inválida também vira revisão; entrada inválida continua levantando erro
    s = X.julgar_seguro(Duble(estraga=lambda q, r: {"answers": {}}), CONVERSA_COMPLETA, {}, CATALOGO)
    confere(s["pergunta"] is None and s["falha"] and "1ª requisição" in s["motivo"], f"D: 1ª inválida → {s['motivo']}")
    try:
        X.julgar_seguro(Duble(), [], {}, CATALOGO)
        confere(False, "D: entrada inválida não levantou erro")
    except ValueError:
        pass
    # lote: uma falha não aborta as outras
    lote = [X.julgar_seguro(Duble(COMPLETA, {"next": "parking"}, e), CONVERSA_COMPLETA, {}, CATALOGO)
            for e in (None, ESTRAGOS["timeout"], None)]
    confere([x["pergunta"] for x in lote] == ["vagas", None, "vagas"], "D: lote abortou ou trocou a saída")
    return 1 + 2 * len(ESTRAGOS) + 4


# ---------------------------------------------------------------------------------------- E. custo
def bateria_custo() -> int:
    for conv, nouls in ((CONVERSA_COMPLETA, COMPLETA), (conversa("quero alugar"), {"rental": 0.9})):
        d = Duble(nouls)
        s = X.julgar(d, conv, {}, CATALOGO)
        confere(all("single_choice" not in p["questions"] for p in d.pedidos) and "comparacao" not in s["etapas"]
                and s["escolhas"]["unica"] is None, f"E: produção enviou a Choice única ({s['etapas']})")
        d = Duble(nouls)
        s = X.julgar(d, conv, {}, CATALOGO, todas=True)
        confere(s["etapas"][-1] == "comparacao" and "single_choice" in d.pedidos[-1]["questions"]
                and all("single_choice" not in p["questions"] for p in d.pedidos[:-1]) and s["escolhas"]["unica"] is not None
                and s["escolhas"]["jev"] is not None, f"E: comparação fora do lugar ({s['etapas']})")
        confere("customer_amounts" in d.pedidos[0]["state"], "E: fato calculado fora do state")
    return 6


def main() -> None:
    partes = {"A normalizador": bateria_normalizador(), "B regra do orçamento": bateria_regra(), "C portão": bateria_portao(),
              "D 2ª etapa": bateria_etapa2(), "E custo": bateria_custo()}
    for nome, n in partes.items():
        print(f"{nome}: {n} conferências")
    if falhas:
        print(f"\n{len(falhas)} FALHAS:")
        for f in falhas:
            print("  -", f)
        sys.exit(1)
    print(f"\nbateria ok: {sum(partes.values())} conferências, 0 falhas")


if __name__ == "__main__":
    main()
