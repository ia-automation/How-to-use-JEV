"""Perguntas, limiares e conversões de R5 (HateBR) e R4 (B2W) — o ÚNICO arquivo que se afina, e só no AJUSTE.

O hash deste arquivo é gravado em `congelamento.json` antes do teste; `avaliar.py teste` recusa rodar
se o hash mudou. Mudar depois do teste = nova versão do protocolo (o teste antigo vira ajuste).

Perguntas em inglês sobre texto em português (medições de 2026-09-30: pt na mensagem ≈ en; pergunta em
pt não ajudou). `true` sempre descreve o sim da tarefa (lição 8). A definição de ofensivo é a do
PROTOCOLO (linguagem que ataca/insulta/ridiculariza pessoa ou grupo), com a "conotação pejorativa" do
HateBR; a tabela de definição do README do HateBR é imagem e não está no arquivo local.
"""

# Campos do state (as perguntas apontam para eles entre crases — limite #4: nomear a parte do state).
# HateBR: {"comment": comentario}. B2W: {"review_title": ..., "review_text": ...}.


def _noul(instrucao: str, sim: str | None = None, nao: str | None = None) -> dict:
    q = {"type": "noul", "instructions": instrucao}
    if sim is not None:
        q["criteria"] = {"true": sim, "false": nao}
    return q


# -------------------------------------------------------------------------------------------- R5
# Variantes medidas JUNTAS na mesma requisição do ajuste (perguntas isoladas; custo = tokens extras).
HATEBR = {
    "ofensivo": _noul(
        "`comment` is a comment on a Brazilian politician's Instagram post. Is `comment` offensive? Offensive "
        "means it uses a word or expression with a pejorative sense to attack, insult, curse at, mock or "
        "ridicule a person, an institution or a group, explicitly or implicitly.",
        "It attacks, insults, curses at, mocks or ridicules someone or some group, even in one short phrase, "
        "with sarcasm, or with a derogatory label or name-calling.",
        "It has no pejorative attack: support, praise, a neutral remark, a question, or disagreement and "
        "political criticism stated without insults, mockery or derogatory words.",
    ),
    "ofensivo_sem_criterio": _noul(
        "`comment` is a comment on a Brazilian politician's Instagram post. Does `comment` use a word or "
        "expression with a pejorative sense to attack, insult, curse at, mock or ridicule a person, an "
        "institution or a group, explicitly or implicitly?",
    ),
    # v2 (ajuste, passada 2): estreita para a PALAVRA/EXPRESSÃO pejorativa — o que o HateBR anota
    # ("termos ou expressões com conotação pejorativa"). Os falsos sim da v1 eram crítica sem termo pejorativo.
    "ofensivo_v2": _noul(
        "`comment` is a comment on a Brazilian politician's Instagram post. Does `comment` contain a word or "
        "expression used with a pejorative sense against a person, an institution or a group: an insult, a "
        "curse, a derogatory label or nickname, or mockery?",
        "It contains such a pejorative word or expression aimed at someone, even a single word, sarcastic or "
        "implicit (for example calling someone trash, a thief, a liar, crazy or a clown).",
        "It has no pejorative word or expression: support, praise, a question, advice, or criticism and "
        "disagreement worded without insults, derogatory labels or mockery.",
    ),
}

# -------------------------------------------------------------------------------------------- R4
B2W = {
    "recomenda": _noul(
        "`review_title` and `review_text` are a customer's review of a product bought online. Would this "
        "customer recommend the product to a friend?",
        "The review shows the customer is satisfied enough to recommend it: praise, 'I recommend', it met "
        "expectations, good value for money, even with small complaints.",
        "The review shows the customer would not recommend it: the product is bad, defective, different from "
        "the description or did not arrive, or the customer regrets the purchase.",
    ),
    "recomenda_sem_criterio": _noul(
        "`review_title` and `review_text` are a customer's review of a product bought online. Would this "
        "customer recommend the product to a friend?",
    ),
    # Score: cada nível é uma SITUAÇÃO julgada sozinha (lição 11); do pior ao melhor.
    "nota": {
        "type": "score",
        "instructions": "How satisfied is the customer who wrote `review_title` and `review_text` with this purchase?",
        "criteria": [
            "Very unhappy: the product is broken, useless, fake or never arrived, or the customer wants the money back.",
            "Unhappy: the problems clearly outweigh the good points.",
            "Lukewarm: the product is just average, or its good and bad points roughly balance.",
            "Happy, with a reservation: likes the product but mentions a limitation, a small defect or a delivery issue.",
            "Fully happy: only praise, no complaint at all.",
        ],
    },
    # v2 (ajuste, passada 2): separa "bom" (satisfeito) de "excelente" (encantado) — na v1 notas 3 e 4 com
    # texto só positivo caíam no nível de cima (score médio 2,94 para nota 3; 3,67 × 3,75 para 4 × 5).
    "nota_v2": {
        "type": "score",
        "instructions": "How satisfied is the customer who wrote `review_title` and `review_text` with this purchase?",
        "criteria": [
            "Very unhappy: the product is broken, useless or fake, it never arrived, or the customer wants the money back.",
            "Unhappy: the problems clearly outweigh the good points.",
            "Mixed: the product is just okay or average, or its good and bad points roughly balance.",
            "Satisfied: calls the product good or fine, or likes it but mentions a limitation, a small defect or a delivery issue.",
            "Delighted: enthusiastic praise (excellent, perfect, loved it) with no complaint at all.",
        ],
    },
}

PERGUNTAS = {"hatebr": HATEBR, "b2w": B2W}

# Pergunta que cada tarefa USA no teste (as outras só serviram ao ajuste). Escolha no ajuste (2 passadas):
# R5 ofensivo_v2 — mesmo acerto da v1 (0,93) no limiar 0,5 em vez de 0,6, Brier 0,058 × 0,071, PR-AUC 0,971 ×
#   0,957, curva de acerto mais plana entre 0,4 e 0,6 (0,92–0,93) e mais cobertura na faixa (0,78 × 0,71).
# R4a recomenda (com critério) — 0,97 no limiar 0,5; sem critério empata no acerto com Brier pior (0,057).
# R4b nota_v2 — MAE 0,65 × 0,71, ±1 0,92 × 0,86, exato igual (0,46).
USAR = {"R5": ("hatebr", "ofensivo_v2"), "R4a": ("b2w", "recomenda"), "R4b": ("b2w", "nota_v2")}

# Limiar único do Noul (sim se noul >= LIMIAR). Custo do erro DECLARADO simétrico (FP = FN = 1) nas duas
# tarefas: o alvo é rotular (protocolo: não estender para bloquear). Escolhido no ajuste pela grade abaixo
# (menor custo; empate → mais perto de 0,5).
GRADE_LIMIAR = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
LIMIAR = {"R5": 0.5, "R4a": 0.5}  # regra no ajuste: R5 (ofensivo_v2) → 0,5; R4a (recomenda) → 0,5

# Faixa de dúvida (relatada à parte): noul <= NAO decide não; >= SIM decide sim; meio = revisão humana.
# Não afinada (padrão do doc NO=0,2 / YES=0,8): no ajuste, R5 cobre 0,78 com 0,974 nos decididos; R4a 0,83 / 0,964.
FAIXA = {"R5": (0.2, 0.8), "R4a": (0.2, 0.8)}


def nota_de_score(score: float) -> int:
    """Score 0..4 → nota 1..5 por arredondamento (conversão congelada no ajuste; protocolo R4b)."""
    return min(5, max(1, int(score + 0.5) + 1))
