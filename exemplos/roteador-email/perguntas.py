"""Perguntas, limiares e política do roteador de e-mail — o ÚNICO arquivo que um humano precisa revisar.

Um e-mail vira UM state `{"sender_name", "subject", "body", "signals"}` e UMA requisição ao Jev: uma Choice de
classe (6 opções) + 5 Nouls atômicos nas fronteiras caras. `roteador.py` compõe: confiança da Choice ≥ limiar da
classe E nenhum Noul em conflito → o Jev DECIDE sozinho; senão → ESCALA ao LLM (o classificador que já existe).
Mudar política = editar número aqui, sem chamar a API de novo.

A caixa: e-mails de uma empresa imobiliária brasileira (venda, locação, administração). Por isso boleto e
circular de administradora de condomínio são `principal` (trabalho), não `notificacoes` — é a regra `condominio`
do classificador em produção, dita ao Jev na descrição das opções.

Perguntas em inglês sobre e-mails em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram e custaram +10%).
Os exemplos (`examples`) foram escritos à mão, genéricos; nenhum foi copiado dos dados. Pós-revisão (2026-10-01):
um exemplo coincidia com o assunto-padrão de uma plataforma presente nos dados e dois dividiam uma sequência de
quatro palavras com algum e-mail; os três foram trocados por frases inventadas (conferido contra assunto e corpo).

Afinação (só nos 152 registros `conjunto == "ajuste"`, 2026-10-01; o teste não foi lido):
- 1ª passada (Choice + os 5 Nouls do briefing): leitura forçada 0,750 (recorte IA 0,696). Três defeitos de DESENHO:
  (a) a descrição dizia que DKIM alinhado prova o remetente — fraude assinada pelo próprio domínio saía
  `notificacoes` e boleto de administradora sem DKIM alinhado saía `golpe` (7 `principal` lidos como `golpe`);
  (b) `impersonates_known_sender` disparava só com `dkim_aligned` falso (9 de 18 notificações reais ≥ 0,8);
  (c) nada dizia que e-mail de administradora de condomínio é trabalho desta caixa.
- 2ª passada (este arquivo): o contexto diz o que DKIM alinhado prova e NÃO prova (o domínio do remetente não
  existe no dado anonimizado); `impersonates_known_sender` passou a exigir sinal no TEXTO; entraram dois Nouls
  atômicos — `pushes_to_act_on_pretext` (pretexto de urgência) e `property_admin_mail` (e-mail de administração de
  imóvel, a trava do "cliente perdido"). Leitura forçada 0,822 (IA 0,772); `principal` lido como `golpe`: 7 → 2.
- Limiares: escolhidos nos vãos do ajuste, por classe (explicados junto das constantes). Com eles o ajuste dá
  48% de cobertura no recorte IA e nenhum decidido discordando — número OTIMISTA (limiar escolhido no próprio
  ajuste); o teste é que mede.
- No ajuste só duas travas mudaram alguma decisão (`impersonates_known_sender` em `promocoes`, 2 erros barrados; e
  a regra do corpo curto, 1). As outras ficam ligadas POR DESENHO (segunda leitura do lado caro, ~190 tokens
  cada); o relatório mede no teste o que cada uma barrou.
Nenhuma pergunta foi alargada para consertar um caso; as mudanças da 2ª passada são de família (DKIM, pretexto,
condomínio).
"""

CLASSES = ["principal", "notificacoes", "promocoes", "redes_sociais", "spam", "golpe"]

# Sinais do registro que entram no state (calculados em CÓDIGO na extração; o Jev só os lê como fato pronto).
# Ficam fora os constantes ou redundantes no ajuste (`auth_header_present`, `list_id`, `dkim_pass`,
# `link_domains`) e os que descrevem a extração, não o e-mail (`body_from`, `body_truncated`): state enxuto.
SINAIS_NO_STATE = ["sender_kind", "dkim_aligned", "spf_pass", "dmarc_pass", "reply_to_differs", "list_unsubscribe",
                   "bulk_precedence", "auto_submitted", "attachment_types", "links_outside_sender_domain"]

_CAIXA = ("The state is one e-mail received by a mailbox of a Brazilian real-estate company (sales, rentals and "
          "property management): `sender_name` is the display name of the sender, `subject` and `body` are the "
          "message (Brazilian Portuguese, personal data masked with tags like [NOME_1]), and `signals` are facts "
          "computed by code from the headers. The sender's address and domain are NOT available. "
          "`signals.dkim_aligned` true only means that the sending domain signed the message: it does not prove "
          "that the sender is who the display name says (fraudsters sign their own domains), and false is common "
          "in legitimate mail sent through third-party mailing platforms.")


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


PERGUNTAS = {
    "class": {
        "type": "choice",
        "instructions": {
            "context": _CAIXA,
            "question": "Which mailbox category does this e-mail belong to?",
            "focus": "Judge what the message is and whether it is what it claims to be, not only its topic. A "
                     "message that pretends to be something it is not is `golpe`, whatever its topic.",
        },
        "criteria": {
            "principal": {
                "what": "Work mail that a person at the company has to read or act on: a message a person wrote "
                        "to this recipient (client, owner, tenant, partner, lawyer, accountant, supplier), a reply "
                        "or forward in an ongoing conversation, contracts, deeds and documents of a deal, and "
                        "operational mail from condominium administrators or contracted service providers about a "
                        "specific property or account, even when generated by their system (condominium fee slips, "
                        "circulars, assembly notices or minutes, a parcel delivered at the building, the invoice "
                        "and boleto of a supplier or accountant the company uses).",
                "not_for": "Automatic receipts or alerts of online services; marketing; mass mail; a message that "
                           "fakes its sender.",
                "examples": ["RES: documentos para a escritura do apartamento", "Boleto da cota condominial de outubro",
                             "Boa tarde, envio em anexo a minuta revisada do aluguel"],
            },
            "notificacoes": {
                "what": "Automatic informational message that a real online service, platform or system sends "
                        "about the recipient's own account or activity: receipt, order or subscription "
                        "confirmation, security or login alert, status of an ad or of a request, technical "
                        "report, job alert the recipient subscribed to.",
                "not_for": "Offers and newsletters; a message written by a person; condominium or supplier mail "
                           "about a property; a fake alert that imitates a service.",
                "examples": ["Seu recibo de pagamento da assinatura", "Sua solicitação de suporte foi atualizada",
                             "Relatório agregado de autenticação do domínio"],
            },
            "promocoes": {
                "what": "Marketing from an identifiable, legitimate brand, store, bank, school or publisher: "
                        "newsletter, coupon, sale, product news, event or course invitation, usually sent through "
                        "a mailing list with an unsubscribe option (`signals.list_unsubscribe`).",
                "not_for": "A cold offer from an unknown sender with no identifiable brand; fraud; a receipt or "
                           "alert about the recipient's account.",
                "examples": ["Até 50% de desconto só esta semana", "Newsletter: resumo semanal do mercado",
                             "Inscreva-se no nosso webinar gratuito"],
            },
            "redes_sociais": {
                "what": "Message generated by a social network about social activity: new follower or connection "
                        "request, like, comment, mention, message waiting, people or posts suggested.",
                "not_for": "Notices of an advertising or business account (billing, ad approval); marketing; a "
                           "fake social-network alert.",
                "examples": ["Fulano quer se conectar com você", "Você tem 3 novas notificações",
                             "Fulana comentou na sua publicação"],
            },
            "spam": {
                "what": "Unsolicited mass mail from an unknown sender with no relationship with the recipient: "
                        "cold commercial offer, lead or company list for sale, dubious product, mail in a foreign "
                        "language about unrelated business, bounce noise or meaningless content. Annoying, but it "
                        "does not fake an identity and does not try to steal money or credentials.",
                "not_for": "Marketing of an identifiable brand with an unsubscribe option; a message that fakes a "
                           "known sender or pushes the recipient to pay, log in, or open a link or attachment "
                           "under a false pretext.",
                "examples": ["Base de contatos qualificados por apenas R$ 99", "Luxury watches from $99, limited offer",
                             "Aumente seus seguidores hoje"],
            },
            "golpe": {
                "what": "Fraud or phishing: the message pretends to be a bank, marketplace, court, tax authority, "
                        "carrier, big brand or a business contact in order to make the recipient click a link, open "
                        "an attachment, pay, or give credentials or data. Typical pretexts: fake lawsuit or "
                        "summons, fake invoice, receipt or payment proof, fake purchase or delivery, account "
                        "or mailbox blocked, security confirmation or registration update, a signed document to "
                        "view, a tax guide, a prize or exclusive upgrade, a stranger asking for a quote or sending "
                        "a job application with a link or attachment to open.",
                "not_for": "An ordinary, specific notice of a service the recipient uses; an honest offer, even "
                           "if unsolicited; a real person writing about a real deal; a condominium administrator's "
                           "fee slip or circular about a named building.",
                "examples": ["Intimação: processo trabalhista em seu nome, acesse o link",
                             "Atualização cadastral obrigatória, sua conta será bloqueada",
                             "Segue comprovante do pix em anexo"],
            },
        },
    },
    "asks_money_or_credentials": _noul(
        "The e-mail (`subject` and `body`) asks the recipient to pay or transfer money, or to provide, confirm or "
        "update a password, login, banking or registration data, including by logging in through a link.",
        "It contains a request to pay (boleto, pix, transfer, invoice to settle) or to provide or update "
        "credentials or personal, banking or registration data.",
        "It asks for neither payment nor credentials or data: it only informs, offers, confirms, or talks about a "
        "subject without such a request.",
    ),
    "impersonates_known_sender": _noul(
        "The e-mail uses the name of a well-known organization (bank, card issuer, marketplace, carrier, court, tax "
        "or government body, big technology or retail brand) or poses as a business contact, and the message "
        "itself gives signs that it does not really come from them.",
        "A known name is used AND the text betrays it: the greeting uses the e-mail address or a generic word "
        "instead of the recipient's name, the sender name or subject carries random codes, the story is a generic "
        "pretext (blocked account, registration update, lawsuit, unexpected receipt, invoice or delivery), or the "
        "reply address differs (`signals.reply_to_differs`). `signals.dkim_aligned` false supports this only "
        "together with one of those signs.",
        "No known organization or contact is named; or one is named and the content is the ordinary, specific "
        "mail such a sender sends (a receipt with the details of the transaction, a newsletter, a report), even if "
        "`signals.dkim_aligned` is false.",
    ),
    "pushes_to_act_on_pretext": _noul(
        "The e-mail pushes the recipient to click a link, open an attachment, reply with data or pay, using an "
        "alarming or unexplained pretext.",
        "It creates urgency or alarm (account or mailbox will be blocked, security confirmation, deadline today, "
        "lawsuit, summons, fine, debt) or dangles a prize or exclusive benefit; or it only points to a document, "
        "receipt, invoice, quote or attachment without saying which deal it belongs to.",
        "It makes no such push: it informs, documents or offers something with its context explained (which "
        "property, order, account or service it refers to), or it is a conversation between people.",
    ),
    "property_admin_mail": _noul(
        "The e-mail is about the administration of a specific condominium, building, or rented or sold property.",
        "It names a specific condominium, building, unit or rental and deals with its fee slip, circular, "
        "assembly notice or minutes, parcel delivery, maintenance, tenant registration, rental contract or deed "
        "documents.",
        "It is not about managing a specific property: generic real-estate marketing, or mail of a platform, "
        "bank, store or any other subject.",
    ),
    "human_wrote_to_this_recipient": _noul(
        "A person individually wrote this e-mail to this specific recipient or company, about a real matter "
        "between them (a deal, a property, a document, a question), as part of a real conversation.",
        "It reads as written by a person for this recipient: a reply or forward with the earlier messages, a "
        "specific request or answer naming the deal, property or document, a personal greeting and signature.",
        "It was produced by a system or sent as the same text to many recipients: receipts, alerts, newsletters, "
        "offers, templates with generic greetings; or a short generic text that could be sent to anyone.",
    ),
    "transactional_notice": _noul(
        "The e-mail is an automatic message generated by a system because of a specific event in an account, "
        "order, payment, subscription, delivery, property or service of the recipient.",
        "It reports or documents one specific event or item: receipt, confirmation, bill or fee slip, statement, "
        "status change, delivery, report, scheduled notice.",
        "It is not tied to a specific event of the recipient: marketing, newsletter, cold offer, a person's "
        "conversation, or a generic call to action.",
    ),
    "unsolicited_bulk_offer": _noul(
        "The e-mail is an advertisement or commercial offer sent in bulk: it tries to sell or promote a product, "
        "service, discount, event or business opportunity with the same text for many recipients.",
        "Its main purpose is to sell or promote something to a broad audience: sale, coupon, product or service "
        "pitch, opportunity, invitation to buy, subscribe or sign up.",
        "It does not advertise: it is a conversation, a document, a bill, a receipt, an alert or a report.",
    ),
}

CHOICE = "class"
NOULS = [q for q, p in PERGUNTAS.items() if p["type"] == "noul"]

# ---------------------------------------------------------------------------------------- política
# A Choice diz O QUÊ; a confiança diz SE o Jev decide sozinho (padrão roteamento-por-confiança). Limiar por
# classe, pelo custo de decidir errado: `principal`/`notificacoes` decididos sozinhos põem o e-mail na caixa de
# entrada (um golpe ali é o erro caro 1); `spam`/`golpe` decididos sozinhos tiram da caixa (um e-mail de cliente
# ali é o erro caro 2); `promocoes`/`redes_sociais` erram barato.
# No ajuste (2ª passada, todos os recortes), confiança das leituras que DISCORDAM de produção, por classe lida:
#   principal ≤ 0,20 · notificacoes ≤ 0,66 (+ uma a 0,93 com corpo de 19 caracteres) · promocoes ≤ 0,79 (as duas
#   acima de 0,7 são spam × promoções, erro barato) · spam ≤ 0,69 · golpe ≤ 0,59.
# Limiar no vão acima delas: 0,7 nas classes de caixa (concordantes mais baixas logo acima: 0,74) e em promoções;
# 0,8 em golpe (vão 0,59–0,79); 0,9 em spam (só 9 leituras `spam` no recorte IA e é o lado do cliente perdido).
# `redes_sociais` não tem caso no ajuste: herda o de promoções e fica fora do critério.
LIMIAR_CONF = {"principal": 0.7, "notificacoes": 0.7, "promocoes": 0.7, "redes_sociais": 0.7, "spam": 0.9, "golpe": 0.8}

# Noul em três faixas (NÚCLEO §6): ≤ NOUL_NAO = não; ≥ NOUL_SIM = sim; meio = dúvida.
NOUL_NAO, NOUL_SIM = 0.2, 0.8

# Conflito = a Choice escolheu a classe, mas um Noul atômico (absoluto, isolado) diz o contrário → ESCALA.
#   "alto":      o Noul não pode estar em `sim` (≥ NOUL_SIM);
#   "nao_baixo": o Noul tem de estar em `nao` (≤ NOUL_NAO): dúvida também escala — só no lado do erro caro 2
#                (e-mail de condomínio/negócio tirado da caixa de entrada).
_FRAUDE = ["impersonates_known_sender", "pushes_to_act_on_pretext"]
CONFLITOS = {
    "principal": {"alto": _FRAUDE + ["unsolicited_bulk_offer"]},
    "notificacoes": {"alto": _FRAUDE + ["asks_money_or_credentials", "unsolicited_bulk_offer"]},
    "promocoes": {"alto": _FRAUDE + ["asks_money_or_credentials", "human_wrote_to_this_recipient", "transactional_notice"]},
    "redes_sociais": {"alto": _FRAUDE + ["asks_money_or_credentials"]},
    "spam": {"alto": ["human_wrote_to_this_recipient", "transactional_notice"], "nao_baixo": ["property_admin_mail"]},
    "golpe": {"alto": ["human_wrote_to_this_recipient"], "nao_baixo": ["property_admin_mail"]},
}
USAR_CONFLITOS = True   # False = só a confiança da Choice (variante medida no relatório)

# Faixa validada: a extração corta o corpo em 4.000 caracteres. Acima do teto o e-mail NÃO vai ao Jev: escala,
# motivo "corpo longo". Não é limiar afinado.
TETO_CORPO = 4500
# Corpo curto demais: o Jev julgaria só pelo assunto. Para as classes que põem o e-mail na caixa de entrada
# (`principal`, `notificacoes`) isso não basta para decidir sozinho → escala. Regra de CÓDIGO (contagem).
MIN_CORPO_CAIXA = 80
CLASSES_CAIXA = ["principal", "notificacoes"]
# Corpo cortado pela extração (`sinais.body_truncated`, 4.000 caracteres): o Jev leu só o começo. Regra posta
# DEPOIS do teste (revisão do Codex, 2026-10-01), conservadora: leitura truncada nunca decide sozinha uma classe
# cara — nem as de caixa de entrada (o pedaço cortado pode ser o golpe) nem `spam`/`golpe` (pode ser a conversa
# que mostra que é gente). Só `promocoes` e `redes_sociais` (erro barato) se decidem com corpo truncado. O sinal
# NÃO entra no state nem na pergunta: é regra de CÓDIGO; o relatório mede quantos casos ela barrou.
CLASSES_CARAS = ["principal", "notificacoes", "spam", "golpe"]

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado em 2026-10-01, ANTES de ler qualquer registro do teste. O veredito é calculado pelo `run.py`.
CRITERIO_CONTINUAR = {
    "onde": "no teste, recorte `só IA` (produção decidiu por LLM: `decidido_por` = ai_*), sem os casos `redes_sociais`, "
            "com a política acima. Gabarito = decisão de produção (concordância, não acerto)",
    "1_golpe_na_caixa": "golpe de produção decidido sozinho como `principal`/`notificacoes` ≤ 1% dos golpes do recorte",
    "2_cliente_perdido": "`principal` de produção decidido sozinho como `spam`/`golpe` ≤ 1% dos principais do recorte",
    "3_concordancia": "concordância com produção entre os decididos sozinho ≥ 0,95",
    "4_cobertura": "decide sozinho ≥ 40% do recorte (o briefing sugeria 50% como exemplo; o ajuste, com limiares "
                   "escolhidos nele mesmo, deu 48% — o relatório mostra a linha dos 50% como informativa)",
    "5_contra_baseline": "o baseline de código NÃO chega lá: falha em 1, 2 ou 3, ou cobre menos que o Jev (se o "
                         "baseline passar em 1–3 com cobertura ≥ a do Jev, a regra de código basta)",
    "secundario_nao_decide": "os mesmos números nos recortes `todos` e `só regra`; `redes_sociais` à parte; custo "
                             "roteado × tudo no LLM; o que cada trava de Noul barrou",
    "se_falhar": "1 ou 2 falhando = não serve para decidir sozinho o lado caro; 3 falhando = a confiança não separa "
                 "o que concorda; 4 falhando = seguro, mas tira pouco do LLM; 5 falhando = a regra de código basta",
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"golpe_na_caixa_max": 0.01, "cliente_perdido_max": 0.01, "concordancia_min": 0.95,
                "cobertura_min": 0.40, "cobertura_sugerida_no_briefing": 0.50},
}
