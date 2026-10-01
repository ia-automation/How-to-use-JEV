"""Perguntas ao Jev e limiares do roteador — o ÚNICO arquivo que um humano precisa revisar.

Mudar política = editar número aqui, sem nova chamada à API (as respostas brutas ficam no cache).
Perguntas em inglês (idioma principal do Jev); o pedido, em português, vai no state sob `message`.
Afinado SÓ em dados/ajuste.json (30 casos, 6 por destino). O porquê de cada mudança está na linha.
"""

# ---------------------------------------------------------------- limiares (política)
# Risco: o erro caro é mandar ao LLM algo arriscado → limiar BAIXO (na dúvida, humano).
LIM_RISCO = 0.5
# Irritação: P(nível >= NIVEL_IRRITADO) no Score. É massa de probabilidade de Score, não Noul:
# limiar próprio (limiar de Noul não se reaproveita em Choice/Score — limite #8).
NIVEL_IRRITADO = 2
LIM_IRRITACAO = 0.5
# Status: a consulta é código; errar manda "seu pedido está a caminho" a quem pediu outra coisa.
# 0,5 porque o número (regex) já é porta: o Noul só separa "quer consulta" de "número de passagem".
# No ajuste: com número, quem queria consulta deu 0,56–0,98; quem não queria, ≤ 0,09.
LIM_STATUS = 0.5
# FAQ: dois sinais diferentes (limite #8) — a Choice diz QUAL (relativo), o Noul diz SE basta (absoluto).
# "Basta" em 0,6: no ajuste as FAQs certas deram 0,68–0,87; "onde está meu pedido? estou sem o
# número" (gabarito: barato pede o número) deu 0,51 na FAQ de rastreamento.
LIM_FAQ_CONF = 0.5
LIM_FAQ_COBRE = 0.6
# Raciocínio vem ANTES de status e FAQ (precedência congelada no DADOS.md): falso-sim aqui rouba rota
# de código, por isso não é baixo.
LIM_RACIOCINIO = 0.5
# Piso da rota automática barata (faq, status, llm_barato): abaixo → llm_raciocinio.
# 0 = desligado; a curva cobertura × erro do resultados.md mostra o efeito de cada valor.
PISO_ROTA = 0.0


def _noul(instrucao: str, sim: str | None = None, nao: str | None = None) -> dict:
    """Noul no formato da API; `criteria` só quando há fronteira a explicar (sim/não, nunca invertidos)."""
    q = {"type": "noul", "instructions": instrucao}
    if sim:
        q["criteria"] = {"true": sim, "false": nao}
    return q


# ---------------------------------------------------------------- perguntas
# Nouls de risco: um fato por pergunta (lição 5), alto = alerta; o código compõe com max.
# "Do próprio autor" em todas: no ajuste, a ameaça CITADA ("um cliente disse: vou processar") deu
# jurídico 0,92 com "mention or threaten" (leitura literal, limite #1).
RISCO = {
    "risco_juridico": _noul(
        "Is the customer who wrote `message` taking or threatening legal action about their own case?",
        sim="The author threatens or starts legal action: a lawsuit, a lawyer, court, Procon or another "
            "consumer protection agency.",
        nao="No legal action, or legal action only quoted from someone else or mentioned as an example."),
    "risco_ameaca": _noul(
        "Does the customer who wrote `message` threaten to harm a person or to damage something? "
        "A threat quoted from someone else does not count."),
    # Dado sensível e dado de terceiro eram UMA pergunta com "ou" (dois fatos): "meu amigo já recebeu o
    # dele" dava 0,52–0,63. Separadas (lição 5).
    "risco_dado_sensivel": _noul(
        "Does the customer who wrote `message` share, offer to send, or ask for sensitive data such as a "
        "card number, a password, bank account details or health information?"),
    "risco_dado_terceiro": _noul(
        "Does the customer who wrote `message` ask the store to reveal personal data of another customer, "
        "such as their name, document number, phone, e-mail or address?"),
    # Antes: "explicitly ask to talk to a human" deu 0,31 em "não me mande para o suporte automático".
    "risco_pede_humano": _noul(
        "Does the customer who wrote `message` ask to be served by a human person, or refuse automated support?"),
    # Novo: cobrança não reconhecida é risco financeiro e jurídico que o DADOS.md manda a humano.
    "risco_fraude": _noul(
        "Does the customer who wrote `message` report a charge or purchase they did not make, or suspect fraud?"),
    # Removido "risco_instrui_sistema": o ajuste não tem injeção, e neste domínio pedir "reescreva",
    # "transforme" é legítimo — deu 0,72 num pedido de reescrita. Premissa não sustentada pelo ajuste.
}

# Score descreve situações, não graus (lição 11). O nível "hostil" existe porque exige ação própria.
IRRITACAO = [
    "Calm, neutral or friendly",
    "Disappointed or annoyed, but polite",
    "Very angry: shouting, all caps, accusations or repeated complaints",
    "Hostile: insults, curses or aggressive language toward the store or its staff",
]
# "Palavras do próprio autor": a frase citada "vou processar a loja" levava a irritação a 0,6.
IRRITACAO_INSTRUCAO = ("Which description best matches the tone of the customer's own words in `message`? "
                       "Ignore text the customer quotes from other people.")

# Antes: "asking where an order is / its status" deu 0,39 em "não estou pedindo instruções de rastreio:
# consulte o pedido 81004" — a negação do rastreio contaminou. Agora a fronteira vai nos critérios.
STATUS = _noul(
    "Does the customer who wrote `message` want the store to look up one of their orders?",
    sim="The customer asks to check a specific order: where it is, whether it shipped, its status or delivery.",
    nao="The customer only mentions an order, says it does not need checking, asks how tracking works in "
        "general, or asks for something else.")

# FAQ: Choice sobre as perguntas da FAQ + válvula "none" (lição 9); Noul por FAQ com a resposta
# oficial no texto — a resposta é o que decide se basta, não o título da pergunta.
NENHUMA = "none"
FAQ_ESCOLHA = ("Which of these frequently asked questions is the customer who wrote `message` asking? "
               "Choose 'none' if the customer asks something else or asks nothing.")
FAQ_NENHUMA = "The customer asks something that is not in this list, or asks nothing"
# Texto = definição congelada de `faq` no DADOS.md ("responde por inteiro, sem consulta individual").
FAQ_COBRE = ("Does this official store answer fully answer what the customer who wrote `message` wants, "
             "without looking up their order, account or individual case? Official answer: \"{resposta}\"")

# Nouls de raciocínio = a definição congelada: conflito de política, exceção, plano de vários passos.
# Removido "rac_calculo": cálculo exato é do código; o LLM de raciocínio não é calculadora (DADOS.md).
RACIOCINIO = {
    # "Depende da situação dele" pegava pergunta de FAQ feita com contexto pessoal (0,60): a fronteira
    # vai nos critérios, em termos genéricos (sem copiar caso do ajuste).
    "rac_plano": _noul(
        "Is the customer who wrote `message` asking for a plan or for help choosing between options?",
        sim="A plan with several steps or decisions, an ordered set of checks, or a comparison of "
            "alternatives for the customer's case.",
        nao="A question about a single standard procedure or rule, even when asked with personal context."),
    "rac_varias_regras": _noul(
        "Does a correct reply to `message` require combining two or more store policies, such as exchange, "
        "return, refund, shipping, coupons or address changes?"),
    # "Conflicting information" (leitura literal) pegava "o irmão disse que podia" e "consta entregue mas
    # não chegou" (0,72–0,73). Agora só exceção ou conflito entre REGRAS da loja.
    "rac_excecao": _noul(
        "Is the customer who wrote `message` asking the store for an exception to one of its rules, or "
        "pointing out that two store rules conflict?"),
}


def montar(faq: list[dict]) -> dict:
    """Todas as perguntas de UMA requisição por pedido (fan-out especulativo: o código lê só o ramo
    que usa; pergunta extra custa ~20 tokens e não muda a latência).

    @param faq: itens {"id", "pergunta", "resposta"}
    @returns: mapa id → pergunta no formato JSON da API (só type/instructions/criteria: campo extra = 400)
    """
    q = dict(RISCO)
    q["irritacao"] = {"type": "score", "instructions": IRRITACAO_INSTRUCAO, "criteria": IRRITACAO}
    q["status_pedido"] = STATUS
    q["faq"] = {"type": "choice", "instructions": FAQ_ESCOLHA,
                "criteria": {**{str(f["id"]): f["pergunta"] for f in faq}, NENHUMA: FAQ_NENHUMA}}
    for f in faq:
        q[f"faq_cobre::{f['id']}"] = _noul(FAQ_COBRE.format(resposta=f["resposta"]))
    q.update(RACIOCINIO)
    return q
