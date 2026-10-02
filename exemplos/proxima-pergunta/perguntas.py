"""Perguntas, limiares e política da "próxima pergunta" — o ÚNICO arquivo que um humano precisa revisar.

Uma conversa de WhatsApp (cliente × agente, pt-BR) + o que o CRM já sabe viram UM state
`{"conversation", "known_fields", "customer_amounts"}` (o último é fato calculado pelo código: os valores em dinheiro
que o cliente escreveu, lidos por `valores.py`). O Jev julga; `proxima.py` decide qual pergunta-modelo do catálogo
vai no próximo turno (ou `no_question_needed`) e devolve o ID — o texto da pergunta sai do catálogo, pelo código.

Desenho (regras de rotulagem em dados/LEIA-ME.md):
- `answered.<campo>` (Noul absoluto, um por item do catálogo): o cliente já deu esta informação, na conversa ou
  no CRM. É o portão do erro caro: pergunta respondida NÃO entra nas candidatas (receita function-calling: o Noul
  `stated` separa "informado" de "não disse").
- `withdrawn.<campo>` (Noul, só para campo que o CRM tem — pergunta montada por caso): o cliente retirou o valor
  do cadastro SEM dar outro. Campo do CRM é respondido por regra de CÓDIGO (o código sabe o que o CRM tem, exato);
  só este Noul o reabre. Com valor novo ("tá 2 no cadastro, agora 3") continua respondido.
- Regras de sentido, do código, sobre sinais do Jev: `rental` (aluguel → `financiamento` não se pergunta),
  `investor_not_living` (investidor que não mora → `pet` não se pergunta), `specific_property` (sem imóvel
  específico na conversa, `visita` não é candidata; com ele, bairro e quartos do anúncio contam como respondidos —
  rodada 2).
- Candidatas = não respondidas e com sentido; por regra do LEIA-ME (tabela, regras 1–3), com essencial faltando
  as secundárias não entram. Quem escolhe entre as candidatas é a variante principal (`VARIANTE_PRINCIPAL`):
    `jev`       o desenho de partida. 2ª requisição: Choice relativa `next` só entre as candidatas +
                `no_question_needed` (receita sugestão-de-skill: Noul absoluto decide SE, Choice decide QUAL);
    `mascarada` a Choice única do catálogo inteiro (1ª requisição), lida só nas candidatas — sem 2ª requisição;
    `codigo`    a tabela do LEIA-ME em código: primeira essencial faltando na ordem fixa → senão `visita` se há
                imóvel específico com reação positiva (`positive_reaction`) → senão `no_question_needed`;
    `hibrida`   essencial faltando → o código escolhe (como `codigo`, sem 2ª requisição); essenciais completas →
                a Choice `next` escolhe entre secundárias, `visita` e `no_question_needed` (como `jev`).
  `single_choice` (Choice única, catálogo inteiro, sem portão) é COMPARAÇÃO: só é enviada com `todas=True`, numa
  requisição à parte (rodada 2; na rodada 1 ia sempre dentro da 1ª requisição e o custo da principal era estimado).
- O catálogo NÃO vai no state (desvio do briefing, de propósito): é fixo, então cada item vira pergunta literal
  com as regras do LEIA-ME no critério; apontar `catalog[i]` seria indireção (limite #4) e ~250 tokens parados.

Perguntas em inglês sobre conversa em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram, +10% de tokens).
Os exemplos entre aspas nos critérios são os do LEIA-ME, não frases dos casos do ajuste (na rodada 2, o exemplo de
preço de anúncio em `answered.budget` foi escrito para a pergunta; não é frase de caso do ajuste nem do teste).

Afinação (só no ajuste, 2026-10-01, duas passadas de 20 conversas; 39 requisições cada):
- 1ª passada, tudo a 0,5. Portão: 87/88 proibidas bloqueadas, 0/29 aceitáveis bloqueadas. A que escapou:
  `answered.purpose` 0,37 em quem compra "o primeiro apê" do casal — o `true` só aceitava "morar" dito por
  extenso. A 2ª passada escreveu "dito ou claramente implicado (casa para si ou para a família)": 0,70. É a regra
  do LEIA-ME ("respondida de modo informal"), não a frase do caso.
- `rental` deu 0,54 num "até 600" sem operação (não é aluguel) e ≥ 0,88 nos aluguéis de verdade → limiar 0,7.
  `specific_property` deu 0,65 numa correção de cadastro (sem imóvel na mesa) e ≥ 0,95 nos reais → limiar 0,8.
- A Choice `next` RE-JULGA o portão: nos dois casos em que o orçamento estava "meio dito" (aluguel "até 600";
  compra só com prestação) o Noul liberou `orcamento` (0,40 e 0,44) e a Choice respondeu `no_question_needed`
  (confiança 0,77 e 0,59). A 2ª passada disse na instrução que as opções "já foram conferidas e continuam em
  aberto; não escolha no_question_needed só porque o cliente tocou no assunto": não moveu (0,64 e 0,42, mesma
  escolha). Com essencial faltando a tabela do LEIA-ME já decide (perguntar a essencial é sempre aceitável), então
  a Choice ali só pode empatar ou errar → a variante principal passou de `jev` para `hibrida`: código nas
  essenciais, Choice `next` só onde a tabela deixa escolha (secundárias × visita × nada). No ajuste `hibrida` e
  `codigo` empataram (20/20); ficou a `hibrida` por ser o menor desvio do desenho de partida — `codigo` é medida
  ao lado e custa uma requisição a menos.
- Limiar de `answered` ficou em 0,5: aceitáveis ≤ 0,44, proibidas ≥ 0,62 (as duas pontas são `orcamento`). A folga
  é estreita e mora toda no valor ambíguo; não há faixa do meio porque os dois lados têm custo (perguntar o que
  já sabe × deixar de perguntar o essencial) e uma faixa "não pergunta e não conta como respondida" não tem ação.

Rodada 2 (pós-revisão do Codex, 2026-10-01, NÃO cega: o teste já tinha sido aberto). O que mudou neste arquivo:
- `answered.budget` deixou de julgar tamanho e unidade ("até 6" × "até 600" ficaram em 0,40–0,46 na rodada 1: o
  Noul não separa magnitude). Agora pergunta só o que é semântico — o cliente DECLAROU um valor como limite dele? —
  e exclui o preço do imóvel citado ou consultado. Tamanho, unidade e tipo saem de `valores.py`; a regra do LEIA-ME
  ("Ambiguidade 'até 600'") é aplicada em `proxima.regra_orcamento`. O que a regra não cobre vai para REVISÃO.
- Família do mesmo defeito: `answered.neighbourhood` e `answered.bedrooms` também passaram a perguntar só a
  preferência declarada; o bairro e os quartos do ANÚNCIO citado respondem por regra de código (LEIA-ME: "anúncio
  específico citado pelo cliente responde bairro e quartos"), com o sinal `specific_property` que já existia.
- Limiar novo `declarado_nao` e constante `PISO_PRECO`: não são afinados (o ajuste não tem caso de preço de anúncio
  sem orçamento no CRM); são prioridade por risco, ditos como tal. Os outros limiares são os da rodada 1.
- Uma passada no ajuste com as perguntas novas (2026-10-01, 20 conversas), sem mexer em texto nem limiar depois
  dela. `answered.budget` (CRM sem o campo): ≥ 0,95 nos 9 casos em que o cliente declarou valor (inclusive aluguel
  "até 600" e prestação, que a REGRA deixa em aberto) e 0,03 nos 5 sem valor — o Noul passou a separar. `rental`:
  aluguéis ≥ 0,87, resto ≤ 0,53 (limiar 0,7 mantido). `specific_property`: reais ≥ 0,94, resto ≤ 0,60 (0,8 mantido).
  Portão 88/88 e 0/29, como na rodada 1. O ajuste não tem anúncio citado sem CRM nem preço de anúncio: a regra do
  anúncio e o piso `declarado_nao` só são exercitados no teste e na bateria `testa_codigo.py`.
"""

NQN = "no_question_needed"
VISITA = "visita"
ESSENCIAIS = ["finalidade", "orcamento", "bairro", "quartos"]  # ordem fixa = ordem de abertura (LEIA-ME, regra 2)
SECUNDARIAS = ["vagas", "prazo", "pet", "financiamento"]
CAMPOS = ESSENCIAIS + SECUNDARIAS  # chaves possíveis de `campos_conhecidos`
# ID do catálogo (pt) → nome que o Jev lê (chave de `known_fields` e opção das Choices). O código traduz de volta.
EN = {"finalidade": "purpose", "orcamento": "budget", "bairro": "neighbourhood", "quartos": "bedrooms",
      "vagas": "parking", "prazo": "timeframe", "pet": "pet", "financiamento": "financing", VISITA: "visit", NQN: NQN}
PT = {v: k for k, v in EN.items()}
# Faixa validada (família do achado 6 do imovel-errado): os dados têm 1–6 turnos. Acima do teto a conversa NÃO vai
# ao Jev: sem sugestão, contada à parte. Não é limiar afinado.
TETO_TURNOS = 12
TETO_CARACTERES = 3000


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


# State: {"conversation": [{"from": "customer"|"agent", "text"}], "known_fields": {"purpose": ..., "budget": ...},
#         "customer_amounts": [{"quote": "até 6", "value": 6, "unit": "none stated"}]}  ← calculado por `valores.py`
# ---------------------------------------------------------------------------------------- answered.<campo>
RESPONDIDA = {
    "finalidade": _noul(
        "The customer has already told the agency what the property is for: to rent, or to buy to live in, or to "
        "buy as an investment. It counts whether it was said in `conversation` or is recorded in "
        "`known_fields.purpose`.",
        "Renting is stated (renting alone is enough: it means own use). Or buying is stated together with living "
        "in the property or with investing, outright or by clear implication (they are buying a home for "
        "themselves or their family). Or the customer says they have not decided yet between buying and "
        "renting: that is their answer, and asking again would repeat the question. Or `known_fields.purpose` has "
        "a value.",
        "Neither buying nor renting is stated anywhere: a place, a size and an amount alone do not say it. Or the "
        "customer only says they want to buy, with nothing about living in the property or investing.",
    ),
    # Rodada 2: só o julgamento semântico (o cliente DECLAROU um valor como limite dele?). Tamanho, unidade e tipo
    # do valor são do código (`valores.py`); a regra do LEIA-ME é aplicada em `proxima.regra_orcamento`.
    "orcamento": _noul(
        "The customer has already stated an amount of money as their OWN limit or budget for the property they "
        "are looking for (what they can or want to pay), in `conversation` or in `known_fields.budget`. "
        "`customer_amounts` lists the money amounts that code found in the customer's messages.",
        "The customer states an amount as what they can or want to pay, even informally, as an upper limit or as "
        "a bare number: 'até 800 mil', 'até 1,2 mi', 'até 4 mil', 'até 600', 'até 6', 'consigo pagar 3 mil por "
        "mês'. The size and the unit of the amount do not matter for this question: code reads them. A later "
        "correction of the amount still counts. Or `known_fields.budget` has a value.",
        "The customer states no amount of their own. An amount that is only the price or the rent of a property "
        "being discussed, advertised or asked about (the agent quotes it, or the customer repeats it or asks "
        "about it: 'esse de 500 mil ainda está disponível?') is a fact about that listing, not the customer's "
        "limit. Or the customer says the amount on record no longer holds and gives no new amount.",
    ),
    # Rodada 2 (família do mesmo defeito): preferência DECLARADA pelo cliente × atributo do anúncio citado. O anúncio
    # específico responde bairro e quartos por regra de código (`specific_property`), não por este Noul.
    "bairro": _noul(
        "The customer has already said where THEY want the property (a neighbourhood, a region or a city), in "
        "`conversation` or in `known_fields.neighbourhood`.",
        "The customer names the place they are looking in: a neighbourhood; or a broad region ('zona leste', "
        "'perto da Paulista'); or a small city. Or `known_fields.neighbourhood` has a value that the customer "
        "keeps.",
        "No place is named as where the customer is looking. The street or address of one specific listing that "
        "the customer cites or asks about is a fact about that listing, not a stated preference, and does not "
        "count here. Or the customer says the place on record no longer serves and names no other place.",
    ),
    "quartos": _noul(
        "The customer has already said how many bedrooms THEY need, in `conversation` or in "
        "`known_fields.bedrooms`.",
        "The customer gives the number of bedrooms they need ('2 qts', '3 quartos'), or a type that fixes it "
        "('studio', 'kitnet'). A later correction still counts, with the new number ('na vdd 2 quartos tá bom'). "
        "Or `known_fields.bedrooms` has a value, also when the customer replaces it with a new number.",
        "No number of bedrooms and no such type is given as what the customer needs: 'apartamento', 'apê' or "
        "'casa' alone do not say it. The number of bedrooms of one specific listing that the customer cites or "
        "asks about is a fact about that listing, not a stated need, and does not count here.",
    ),
    "vagas": _noul(
        "The customer has already said whether they need a parking space, or how many, in `conversation` or in "
        "`known_fields.parking`.",
        "They say it outright or informally ('tenho dois carros', 'não tenho carro', 'com 1 vaga'). Or "
        "`known_fields.parking` has a value.",
        "The customer says nothing about cars or parking. Parking mentioned only by the agent while describing a "
        "property does not count.",
    ),
    "prazo": _noul(
        "The customer has already said by when they need the property, in `conversation` or in "
        "`known_fields.timeframe`.",
        "A date, a deadline or an urgency is given, even informally ('a gente casa em outubro e quer entrar "
        "antes'). Or `known_fields.timeframe` has a value.",
        "The customer says nothing about when they need it.",
    ),
    "pet": _noul(
        "The customer has already said whether they have a pet, in `conversation` or in `known_fields.pet`.",
        "They say they have, or do not have, an animal, outright or informally ('meu labrador precisa de "
        "quintal'). Or `known_fields.pet` has a value (true or false).",
        "The customer says nothing about animals. An agent saying that a property accepts pets does not count.",
    ),
    "financiamento": _noul(
        "The customer has already said whether they intend to finance the purchase or to pay cash, in "
        "`conversation` or in `known_fields.financing`.",
        "They say it outright or informally: 'à vista', 'financiado', 'já tenho carta de crédito'. A buyer who "
        "says how much they can pay per month ('consigo pagar 3 mil por mês') is saying they will finance. Or "
        "`known_fields.financing` has a value.",
        "The customer says nothing about how the purchase will be paid.",
    ),
    VISITA: _noul(
        "The customer has already asked for, or scheduled, a visit to a property, or has said they do not want to "
        "visit for now.",
        "The customer asks to visit or to see one specific property in person, proposes or confirms a day for "
        "it, or declines a visit for now.",
        "No visit was asked for, scheduled or declined. Wanting to see options or apartments in general, or "
        "liking a property, is not a visit request.",
    ),
}

_ASSUNTO = {"finalidade": "what the property is for (to buy or to rent, to live in or to invest)",
            "orcamento": "the amount of money the customer has in mind",
            "bairro": "the neighbourhood or region the customer wants",
            "quartos": "the number of bedrooms", "vagas": "parking spaces",
            "prazo": "when the customer needs the property", "pet": "whether the customer has a pet",
            "financiamento": "financing or paying cash"}


def retirado(campo: str) -> dict:
    """Noul `withdrawn.<campo>`, montado só para campo que o CRM tem: valor do cadastro retirado SEM valor novo."""
    return _noul(
        f"`known_fields.{EN[campo]}` is what the agency already had on record, before this conversation, about "
        f"{_ASSUNTO[campo]}. In `conversation`, the customer says that this recorded value no longer holds AND "
        "does not give a new value to replace it.",
        "The customer drops the recorded value (changed their mind about it, can no longer afford it, it no "
        "longer serves) and leaves open what the new value is.",
        "The customer does not talk about it; or keeps it; or replaces it with a new value (the record says one "
        "thing and the customer now states another): then the information is still known.",
    )


# ---------------------------------------------------------------------------------------- sinais das regras de sentido
SINAIS = {
    "rental": _noul(
        "The customer is looking for a property to RENT as a tenant, according to `conversation` and "
        "`known_fields.purpose`.",
        "They want to rent a place for themselves.",
        "They want to buy, including an investor who buys a property to rent it out to other people; or they have "
        "not decided between buying and renting; or it is not stated.",
    ),
    "investor_not_living": _noul(
        "The customer is an investor who will NOT live in the property: they buy it to rent it out or to resell.",
        "They say they are an investor, or that the property is to rent out to others, for short-stay rental or "
        "for resale.",
        "They will live in the property, they are renting a home, or nothing says they are an investor.",
    ),
    "specific_property": _noul(
        "`conversation` is about ONE specific property: a listing the customer cited (by its street, by an ad, "
        "'the one you sent me') or a property the agent presented with its details.",
        "One particular property is on the table and the last customer message is about it.",
        "The customer describes what they are looking for, or asks whether the agency has properties of some kind "
        "in some area, or about prices in general, with no particular property on the table.",
    ),
    "positive_reaction": _noul(
        "In the LAST customer message of `conversation`, the customer reacts positively to one specific property "
        "that is being discussed: they say they liked it or that it suits them.",
        "The last customer message shows they like that property ('gostei', 'parece perfeito').",
        "No specific property is being discussed; or the last message only asks something about it (is it "
        "available, how much); or it asks for a visit; or the reaction is negative or neutral.",
    ),
}

# ---------------------------------------------------------------------------------------- Choices
# Descrição de cada opção (o que o agente faria). As chaves em inglês são as de EN.
OPCAO = {
    "finalidade": "Ask whether the property is to buy or to rent, and whether to live in or to invest. Key fact; "
                  "the opening question on a first contact.",
    "orcamento": "Ask what amount they have in mind (purchase price or monthly rent). Key fact.",
    "bairro": "Ask which neighbourhood or region they prefer. Key fact.",
    "quartos": "Ask how many bedrooms they need. Key fact.",
    "vagas": "Ask whether they need a parking space, and how many. Secondary detail.",
    "prazo": "Ask by when they need the property. Secondary detail.",
    "pet": "Ask whether they have a pet. Secondary detail.",
    "financiamento": "Ask whether they intend to finance or to pay cash. Secondary detail; also fits right after a "
                     "buyer liked one specific property.",
    VISITA: "Offer to schedule a visit. Right when the customer has just shown they like one specific property "
            "and has not asked for a visit yet.",
    NQN: "Ask nothing now: answer what the customer asked, confirm what they requested, or send options.",
}
_PERGUNTA = ("The agent must reply to the LAST customer message in `conversation`. Which ONE of these moves is the "
             "best next step for an experienced real-estate broker?")
# A tabela de decisão do LEIA-ME (regras 1–6) em linguagem literal. `{faltando}` muda entre as duas Choices: na
# Choice entre candidatas, "estar entre as opções" já significa "não respondida".
_COMO = ("The key facts are purpose, budget, neighbourhood and bedrooms: the agent cannot send good options without "
         "them. First: if the last customer message asks something the agent has to answer (is it still available, "
         "how much is it, do you have any, does it accept pets) or asks to visit a property, choose "
         "no_question_needed. Second: otherwise, if a key fact {faltando}, choose a key fact; when the customer has "
         "given no information at all yet, that key fact is purpose. Asking the agent to send options does not "
         "change this while a key fact {faltando}. Third: if no key fact {faltando}, choose visit when the customer "
         "has just reacted positively to one specific property; choose no_question_needed when the customer asks "
         "not to be asked more questions or complains about repeating themselves; otherwise a secondary detail or "
         "no_question_needed are both fine.")


def choice_proxima(candidatas: list[str]) -> dict:
    """Choice `next` da 2ª requisição: as opções SÃO as candidatas que o código deixou passar + a válvula."""
    return {
        "type": "choice",
        "instructions": {
            "question": _PERGUNTA + " Every option except no_question_needed has already been checked and "
                                    "is still open: the customer has not answered it, or what they said about it "
                                    "was unclear or incomplete. Do not choose no_question_needed merely because "
                                    "the customer touched on that subject.",
            "how_to_choose": _COMO.format(faltando="is among the options"),
        },
        "criteria": {EN[c]: OPCAO[c] for c in candidatas},
    }


def choice_unica(itens: list[str]) -> dict:
    """Choice única sobre o catálogo inteiro (comparação): a regra "não repita" vai na instrução, sem portão."""
    return {
        "type": "choice",
        "instructions": {
            "question": _PERGUNTA,
            "never_repeat": (
                "Never choose a question whose answer the customer has already given in `conversation`, even "
                "informally, or that is recorded in `known_fields` (unless the customer says the recorded value no "
                "longer holds and gives no new one). Never ask about financing when the customer is renting, never "
                "ask about pets when the customer is an investor who will not live in the property, and never "
                "offer a visit the customer has already asked for or declined."),
            "how_to_choose": _COMO.format(faltando="is still missing"),
        },
        "criteria": {EN[i]: OPCAO[i] for i in itens},
    }


# ---------------------------------------------------------------------------------------- política
# Limiares de partida 0,5 em tudo; afinados SÓ no ajuste (números da 2ª passada ao lado).
LIMIAR = {
    "respondida": 0.5,         # answered.<campo> ≥ → respondida: sai das candidatas. Aceitáveis ≤ 0,44; proibidas ≥ 0,62
    "retirado": 0.5,           # withdrawn.<campo> ≥ → campo do CRM reaberto. O único retirado 0,96; os 27 mantidos ≤ 0,28
    "aluguel": 0.7,            # rental ≥ → `financiamento` sem sentido. Aluguéis ≥ 0,88; resto ≤ 0,49
    "investidor": 0.5,         # investor_not_living ≥ → `pet` sem sentido. O investidor 0,96; resto ≤ 0,30
    "imovel_especifico": 0.8,  # specific_property ≥ → `visita` pode ser candidata. Reais ≥ 0,95; resto ≤ 0,66
    "reacao_positiva": 0.5,    # positive_reaction ≥ → (só variante `codigo`) `visita`. Reais 0,98; resto ≤ 0,05
    # Rodada 2 — NÃO afinado (o ajuste não tem preço de anúncio sem orçamento no CRM): prioridade por risco. O código
    # leu um valor do cliente que bloquearia `orcamento`; `answered.budget` ≤ este piso → não é limite declarado
    # (preço de anúncio): fica em aberto. Entre o piso e `respondida` → REVISÃO, nunca pergunta nem bloqueio.
    "declarado_nao": 0.2,
}
# Regra do orçamento em código (rodada 2): abaixo disto um valor com unidade não é preço de compra; a partir disto
# não é aluguel mensal. Constante de bom senso, não afinada; o que cai do lado errado vai para revisão.
PISO_PRECO = 50_000
VARIANTE_PRINCIPAL = "hibrida"  # `jev` | `mascarada` | `codigo` | `hibrida` — é a que o critério julga

# ---------------------------------------------------------------------------------------- baseline de código
# "Lacuna + palavras-chave": o que um dev escreveria em meia hora. Texto do CLIENTE, minúsculas, sem acento.
# Campo essencial "preenchido" = está no CRM ou a expressão bate; primeira essencial vazia → pergunta; senão nada.
BASELINE = {
    "finalidade": [r"\balug\w*", r"\binvest\w*", r"\bcompr\w*.*\bmorar\b", r"\bmorar\b.*\bcompr\w*"],
    "orcamento": [r"\bate \d", r"\d+ ?(mil|k|mi|milhao|milhoes)\b", r"r\$ ?\d"],
    "bairro": [r"\b(em|no|na|nos|nas) (?!um\b|uma\b|\d)[a-z]{3,}", r"\bzona (sul|norte|leste|oeste)\b", r"\bcentro\b"],
    "quartos": [r"\d ?(quartos?|qts?|dorm\w*|suites?)\b", r"\b(studio|kitnet|quitinete)\b"],
}

# ---------------------------------------------------------------------------------------- critério
# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado em 2026-10-01, antes de abrir `dados/teste.json`. Denominadores pela tabela do LEIA-ME (teste: 40
# conversas, 23 em que `no_question_needed` não é aceitável). "Melhor baseline de código" = o de maior acerto no
# próprio teste entre primeira lacuna, lacuna + palavras-chave e sempre `no_question_needed`.
CRITERIO_CONTINUAR = {
    "onde": "no teste (40 conversas), variante principal `hibrida` com os limiares acima",
    "1_pergunta_proibida": "escolha ∈ `proibidas` (perguntou o que já sabia ou o que não faz sentido) ≤ 1/40",
    "2_acerto": "escolha ∈ `aceitaveis` ≥ melhor baseline de código + 0,15",
    "3_deixou_de_perguntar": "`no_question_needed` indevido ≤ 2/23",
    "4_contra_choice_unica": "acerto ≥ o da Choice única E proibidas ≤ as da Choice única",
    "secundario_nao_decide": "portão: proibidas bloqueadas ≥ 90%; aceitáveis bloqueadas indevidamente ≤ 5%",
    "se_falhar": ("1 falhando = o portão não serve como guarda contra repetição sem mudança; 2 = a regra de "
                  "palavras-chave basta; 3 = a etapa cala onde devia qualificar; 4 = decompor não paga: a Choice "
                  "única (uma requisição, sem portão) faz o mesmo"),
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"proibida_max": 1, "margem_acerto": 0.15, "nqn_indevido_max": 2,
                "proibidas_bloqueadas_min": 0.9, "aceitavel_bloqueada_max": 0.05},
}
