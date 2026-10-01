"""Perguntas, limiares e pesos da triagem — o ÚNICO arquivo que um humano precisa revisar.

Duas variantes das MESMAS perguntas (os IDs não vão ao modelo, então são iguais nas duas):
  "en" — instruções em inglês. É a que roda sobre o ticket em pt E em en: mede a língua do TICKET.
  "pt" — tradução fiel das instruções. Só roda fora do conjunto de teste: mede a língua da PERGUNTA.
Mudar política (limiar, peso) = editar número aqui, sem nova chamada à API.
Limiares iniciais = pontos de partida das notas de memória; afinar SÓ no conjunto de ajuste.
"""

SETORES = ["pagamento", "entrega", "troca_devolucao", "conta_acesso", "produto_duvida", "outro"]
NOULS = ["pede_reembolso", "quer_humano", "ameaca_cancelar"]

# Nome do campo do state por variante — as instruções apontam para ele entre crases.
CAMPO_STATE = {"en": "message", "pt": "mensagem"}

# Opção da Choice → rótulo do código. Em inglês as opções têm nome inglês (o nome da opção vai ao
# modelo; misturar português na variante "en" contaminaria a medição de língua).
SETOR_DA_OPCAO = {
    "en": {"payment": "pagamento", "delivery": "entrega", "exchange_return": "troca_devolucao",
           "account_access": "conta_acesso", "product_question": "produto_duvida", "other": "outro",
           "unclear": None},
    "pt": {**{s: s for s in SETORES}, "sem_informacao": None},
}
# `unclear`/`sem_informacao` é a válvula (lição 9): DADOS.md §final item 2 congelou que `outro` é assunto
# FORA da taxonomia, não falta de informação. Sem a válvula, "resolve aquilo para mim" só teria `outro`.

# ---------------------------------------------------------------- perguntas em inglês
_EN = {
    # Choice contrastiva: `what`/`not_for`/`examples` com os mesmos nomes em todas as opções.
    # O foco em "pedido principal" é proposital: o 2º assunto sai da distribuição (cópia), não do vencedor.
    "setor": {
        "type": "choice",
        "instructions": {
            "question": "Which store team should handle the main request in `message`?",
            "focus": "Classify the customer's primary request, not every topic mentioned.",
        },
        "criteria": {
            "payment": {"what": "Charges, duplicate or wrong charges, card, PIX, boleto, installments, invoices, charge reversals",
                        "not_for": "Where a package is, returning an item, logging in",
                        "examples": ["I was charged twice", "My PIX payment is not showing up"]},
            "delivery": {"what": "Order status, tracking, late or missing package, wrong address, carrier, shipping time or cost",
                         "not_for": "An item that already arrived and must be returned or exchanged; charges",
                         "examples": ["My order has not arrived", "Tracking has not updated in a week"]},
            "exchange_return": {"what": "Returning, exchanging or cancelling an order or item, defective or wrong item received, warranty",
                                "not_for": "A package that has not arrived yet; questions before buying",
                                "examples": ["The shoe came with a loose seam, I want to exchange it", "I want to return this jacket"]},
            "account_access": {"what": "Login, password, blocked account, registration, changing email, phone or personal data",
                               "not_for": "Payment or order problems",
                               "examples": ["I can't log in", "How do I change the email on my account?"]},
            "product_question": {"what": "Questions about a product: size, specs, stock, compatibility, how to use the product",
                                 "not_for": "A defective or wrong item received; how to use the website or the account",
                                 "examples": ["Does this jacket come in XL?", "Is this charger compatible with my phone?"]},
            "other": {"what": "A subject outside these teams: thanks, compliments, partnerships, jobs, spam",
                      "not_for": "Any request that fits one of the other teams; a message that does not say what it is about",
                      "examples": ["Congratulations on the service!", "Are you hiring?"]},
            "unclear": {"what": "The message does not say what the problem or request is, so no team can act on it",
                        "not_for": "A clear request, even a short one",
                        "examples": ["Fix that thing for me, please", "Hello?"]},
        },
    },
    # Nouls: uma condição cada; alto = sim; `false` lista os casos do MEDO (negação, hipótese, terceiro).
    "pede_reembolso": {
        "type": "noul",
        "instructions": "The customer who wrote `message` is asking the store to give them money back "
                        "(a refund, a charge reversal, or store credit) for their own purchase.",
        "criteria": {
            "true": "They ask for their money back or for a charge to be reversed, or say they want it.",
            "false": "They say they do not want a refund, ask only for an exchange, repair, delivery or information, "
                     "mention a refund only as a hypothesis, or talk about someone else's refund.",
        },
    },
    "quer_humano": {
        "type": "noul",
        "instructions": "The customer who wrote `message` asks to be served by a human person "
                        "(an agent, attendant, supervisor or a phone call) instead of the automated service.",
        "criteria": {
            "true": "They ask now for a person, attendant, supervisor, manager, a phone call, or 'not a bot'.",
            "false": "They do not ask for a person: they only describe the problem, mention a person they talked to before, "
                     "repeat what someone else said, or say they do not need an agent.",
        },
    },
    "ameaca_cancelar": {
        "type": "noul",
        "instructions": "The customer who wrote `message` threatens to cancel their order or account, or to stop buying "
                        "from the store, because of a problem with the store.",
        "criteria": {
            "true": "They say they will cancel, are cancelling, will close the account, never buy again or switch to a "
                    "competitor, including as a condition ('if this is not fixed today I will cancel').",
            "false": "No such threat: a cancellation for their own reasons (wrong size, change of mind) without complaint, "
                     "a threat only to complain elsewhere (consumer agency, lawsuit, social media), or quoting someone else.",
        },
    },
    # Score de 3 níveis = os 3 valores do gabarito. Níveis descrevem situações (cada um é julgado sozinho).
    "frustracao": {
        "type": "score",
        "instructions": {
            "question": "How frustrated is the customer who wrote `message`?",
            "note": "Judge only the customer's own tone. Reporting a problem, insisting or giving an instruction is "
                    "not frustration by itself, and a threat stated calmly is not anger. Sarcasm counts. "
                    "Words quoted from someone else do not count.",
        },
        "criteria": [
            {"summary": "Calm", "signals": ["Neutral, polite or friendly tone",
                                            "Reports a problem or asks something without expressing negative feelings"]},
            {"summary": "Frustrated but polite", "signals": ["Says they are frustrated, disappointed or annoyed",
                                                            "Sarcasm", "No insults and no shouting"]},
            {"summary": "Very angry or hostile", "signals": ["Insults, profanity or shouting in capital letters",
                                                            "Furious or aggressive tone"]},
        ],
    },
}

# ---------------------------------------------------------------- tradução fiel (variante "pt")
_PT = {
    "setor": {
        "type": "choice",
        "instructions": {
            "question": "Qual equipe da loja deve cuidar do pedido principal em `mensagem`?",
            "focus": "Classifique o pedido principal do cliente, não todos os assuntos mencionados.",
        },
        "criteria": {
            "pagamento": {"what": "Cobranças, cobrança duplicada ou errada, cartão, PIX, boleto, parcelas, notas fiscais, estornos",
                          "not_for": "Onde está o pacote, devolver item, entrar na conta",
                          "examples": ["Fui cobrado duas vezes", "Meu PIX não aparece"]},
            "entrega": {"what": "Status do pedido, rastreio, pacote atrasado ou sumido, endereço errado, transportadora, prazo ou frete",
                        "not_for": "Item que já chegou e precisa ser devolvido ou trocado; cobranças",
                        "examples": ["Meu pedido não chegou", "O rastreio não atualiza há uma semana"]},
            "troca_devolucao": {"what": "Devolver, trocar ou cancelar pedido ou item, item com defeito ou errado, garantia",
                                "not_for": "Pacote que ainda não chegou; dúvidas antes de comprar",
                                "examples": ["O tênis veio com a costura solta, quero trocar", "Quero devolver esta jaqueta"]},
            "conta_acesso": {"what": "Login, senha, conta bloqueada, cadastro, troca de e-mail, telefone ou dados pessoais",
                             "not_for": "Problemas de pagamento ou de pedido",
                             "examples": ["Não consigo entrar", "Como troco o e-mail da minha conta?"]},
            "produto_duvida": {"what": "Dúvidas sobre um produto: tamanho, especificação, estoque, compatibilidade, como usar o produto",
                               "not_for": "Item com defeito ou errado recebido; como usar o site ou a conta",
                               "examples": ["Essa jaqueta tem GG?", "Esse carregador serve no meu celular?"]},
            "outro": {"what": "Assunto fora destas equipes: agradecimento, elogio, parceria, vaga de emprego, spam",
                      "not_for": "Qualquer pedido que caiba em outra equipe; mensagem que não diz do que se trata",
                      "examples": ["Parabéns pelo atendimento!", "Vocês estão contratando?"]},
            "sem_informacao": {"what": "A mensagem não diz qual é o problema ou o pedido, então nenhuma equipe consegue agir",
                               "not_for": "Um pedido claro, mesmo que curto",
                               "examples": ["Resolve aquela coisa pra mim, por favor", "Alô?"]},
        },
    },
    "pede_reembolso": {
        "type": "noul",
        "instructions": "O cliente que escreveu `mensagem` está pedindo que a loja devolva dinheiro "
                        "(reembolso, estorno de cobrança ou crédito na loja) de uma compra dele.",
        "criteria": {
            "true": "Pede o dinheiro de volta ou o estorno de uma cobrança, ou diz que quer isso.",
            "false": "Diz que não quer reembolso, pede só troca, conserto, entrega ou informação, "
                     "cita reembolso só como hipótese, ou fala do reembolso de outra pessoa.",
        },
    },
    "quer_humano": {
        "type": "noul",
        "instructions": "O cliente que escreveu `mensagem` pede para ser atendido por uma pessoa "
                        "(atendente, supervisor ou ligação) em vez do atendimento automático.",
        "criteria": {
            "true": "Pede agora uma pessoa, atendente, supervisor, gerente, uma ligação ou 'não um robô'.",
            "false": "Não pede uma pessoa: só descreve o problema, menciona alguém com quem falou antes, "
                     "repete o que outra pessoa disse, ou diz que não precisa de atendente.",
        },
    },
    "ameaca_cancelar": {
        "type": "noul",
        "instructions": "O cliente que escreveu `mensagem` ameaça cancelar o pedido ou a conta, ou deixar de comprar "
                        "na loja, por causa de um problema com a loja.",
        "criteria": {
            "true": "Diz que vai cancelar, está cancelando, vai fechar a conta, nunca mais compra ou vai para o "
                    "concorrente, inclusive como condição ('se não resolverem hoje eu cancelo').",
            "false": "Nenhuma ameaça assim: cancelamento por motivo próprio (tamanho errado, desistência) sem reclamação, "
                     "ameaça só de reclamar em outro lugar (Procon, processo, redes sociais), ou citação de outra pessoa.",
        },
    },
    "frustracao": {
        "type": "score",
        "instructions": {
            "question": "Quão frustrado está o cliente que escreveu `mensagem`?",
            "note": "Julgue só o tom do próprio cliente. Relatar um problema, insistir ou dar uma instrução não é "
                    "frustração por si só, e uma ameaça dita com calma não é raiva. Ironia conta. "
                    "Palavras citadas de outra pessoa não contam.",
        },
        "criteria": [
            {"summary": "Calmo", "signals": ["Tom neutro, educado ou simpático",
                                             "Relata um problema ou pergunta algo sem expressar sentimento negativo"]},
            {"summary": "Frustrado, mas educado", "signals": ["Diz que está frustrado, decepcionado ou incomodado",
                                                              "Ironia", "Sem ofensa e sem gritar"]},
            {"summary": "Muito irritado ou hostil", "signals": ["Ofensa, palavrão ou gritando em maiúsculas",
                                                               "Tom furioso ou agressivo"]},
        ],
    },
}

# ---------------------------------------------------------------- "também é com este setor?" (cópia)
# Por que Noul e não o 2º lugar da Choice: medido no rascunho (2026-09-30), "cobrado 2x E pedido
# atrasado" deu pagamento 0,99–1,00 de confiança em en e pt — a Choice é RELATIVA e, com o foco em
# "pedido principal", concentra tudo no vencedor; o 2º assunto some da distribuição. O Noul é ABSOLUTO:
# pergunta de cada setor se há um pedido para ele. Gerado das mesmas descrições da Choice (fonte única).
# 1ª versão ("contém um pedido ou problema que a equipe precisa tratar?") leu ao pé da letra a
# história da irmã (r04: entrega 0,89, troca 0,76) — o "de quem é o pedido" virou a nota.
_TAMBEM = {
    "en": {"question": "Does the customer who wrote `message` ask `team` to act on a problem or request of their own?",
           "note": "It may be besides the main request. Stories about other people, hypotheses and threats do not count."},
    "pt": {"question": "O cliente que escreveu `mensagem` pede que a `equipe` aja sobre um problema ou pedido dele mesmo?",
           "note": "Pode ser além do pedido principal. Histórias de outras pessoas, hipóteses e ameaças não contam."},
}
_CAMPO_EQUIPE = {"en": "team", "pt": "equipe"}


def _tambem(variante: str, perguntas: dict) -> dict:
    return {
        f"tambem_{SETOR_DA_OPCAO[variante][opcao]}": {
            "type": "noul",
            "instructions": {**_TAMBEM[variante], _CAMPO_EQUIPE[variante]: {"name": opcao, **desc}},
        }
        for opcao, desc in perguntas["setor"]["criteria"].items()
        if SETOR_DA_OPCAO[variante][opcao] not in ("outro", None)  # cópia para "outro"/válvula não ajuda ninguém
    }


PERGUNTAS = {"en": {**_EN, **_tambem("en", _EN)}, "pt": {**_PT, **_tambem("pt", _PT)}}

# ---------------------------------------------------------------- limiares (roteamento por confiança)
SETOR_CONF_MIN = 0.5    # abaixo: setor incerto → humano faz a triagem (piso das notas: 0,5–0,6)
# Setor ≠ vencedor com tambem_<setor> ≥ isto recebe cópia. Perder a cópia deixa metade do problema
# parada; cópia a mais custa uma olhada de outra equipe. Rascunho: cópia real 0,92–0,93; falsas 0,50–0,73.
SETOR_COPIA_SIM = 0.7
# Com cópia, o vencedor precisa ser CLARO; senão são duas intenções sem principal (DADOS.md: setor nulo →
# humano). Ajuste 2026-09-30: principal claro com cópia deu 1,00; "senha E troca, mesma prioridade" deu
# 0,48–0,75. Política, não pergunta nova: estreita o automático só onde já há dois setores.
SETOR_CONF_MIN_COM_COPIA = 0.9
# Noul em três faixas: ≤ NÃO decide não; ≥ SIM decide sim; o meio vai para revisão humana.
FAIXA_NOUL = {
    "pede_reembolso": (0.2, 0.8),
    "quer_humano": (0.2, 0.8),
    "ameaca_cancelar": (0.2, 0.8),
}

# ---------------------------------------------------------------- prioridade composta (0..1)
# Soma ponderada das probabilidades brutas (frustração normalizada por len(criteria)-1).
# Peso é política: churn (ameaça) e irritação pesam mais que dinheiro e pedido de humano.
PESOS_PRIORIDADE = {"frustracao": 0.4, "ameaca_cancelar": 0.3, "pede_reembolso": 0.15, "quer_humano": 0.15}
FAIXAS_PRIORIDADE = ((0.6, "alta"), (0.3, "media"), (0.0, "baixa"))  # primeiro piso atingido vence
