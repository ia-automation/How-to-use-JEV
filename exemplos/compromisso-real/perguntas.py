"""Perguntas, faixas, política e critério do `compromisso-real` — o ÚNICO arquivo que um humano precisa revisar.

Uma conversa curta de trabalho (chat/e-mail, pt-BR) com `data_referencia` e candidatos já marcados (trecho literal +
responsável candidato) vira UM state e UMA requisição ao Jev com as perguntas de TODOS os candidatos. Para cada
candidato o Jev julga o PAR (trecho, responsável) lido no FIM da conversa: `compromisso | proposta | cancelado |
citacao_antiga | pedido_sem_aceite`. O código (`compromisso.py`) localiza o trecho na mensagem, lê os fatos que são
dele (quem escreveu, se o responsável falou, se o trecho está entre aspas), extrai as EXPRESSÕES DE TEMPO da
conversa ("sexta", "dia 15", "amanhã", "em 3 dias úteis") e as resolve contra `data_referencia`; o Jev só aponta
QUAL expressão dá o dia da entrega (ou nenhuma) — nunca compara datas nem faz conta (limite #3 do jev-1.13).

Desenho (regras de rotulagem em dados/LEIA-ME.md):
- Variante PRINCIPAL `choice`: uma Choice por candidato com as 5 classes descritas por inteiro (lição 37) e as
  regras de precedência do LEIA-ME; vence a maior probabilidade; vencedor abaixo de `P_MIN_VENCEDOR` → `revisar`
  (o lado barato: não cria nem cancela tarefa; um humano olha).
- Variante INFORMATIVA `nouls`: quatro Nouls atômicos por candidato, na MESMA requisição — `accepted` (há aceite
  explícito do responsável?), `undone` (uma mensagem posterior desfez?), `quoted` (é texto citado de antes?),
  `open_request` (é pedido sem resposta/aceite?) — combinados em código pela precedência do LEIA-ME e por `FAIXA`.
- Variante `choice+nouls`: a Choice decide; onde ela hesita (abaixo do piso) os Nouls decidem se forem
  conclusivos; senão `revisar`.
- `deadline` (Choice por candidato, só quando o código achou expressões de tempo na conversa): o Jev escolhe,
  entre as expressões LIDAS PELO CÓDIGO (com a mensagem onde estão) + `none`, qual dá o dia da entrega deste
  candidato — inclusive a herdada do pedido que o trecho aceita ou de uma resposta posterior. O código resolve a
  expressão escolhida contra `data_referencia` pela tabela do LEIA-ME e copia a data; `none`, expressão sem dia
  ("semana que vem") ou vencedor abaixo de `P_MIN_PRAZO` → `prazo` nulo.
- Guarda de código (regra 8 do briefing): trecho DENTRO DE ASPAS (fato lido pelo código) que a Choice chama de
  `commitment` sai `revisar`, nunca `compromisso` — texto citado não cria tarefa sozinho; o que o responsável
  assume fora da citação é outro candidato.
- `prazo` é SEMPRE nulo em `cancelado`, `citacao_antiga` e `revisar`.

Perguntas em inglês sobre conversa em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram e custaram +10%).

Afinação (só rascunho + ajuste; cada passada registrada aqui e no README):
- 1ª passada: texto escrito do LEIA-ME antes de qualquer chamada. Rascunho 10/10 vereditos e 8/8 prazos; ajuste
  47/47 vereditos (P do vencedor ≥ 0,86: fácil demais para calibrar o piso), prazo 31/36 nos vivos acertados. Os 5
  erros de prazo: em 3 (CR-A010 k1 "até terça", CR-A015 k2 "à tarde", CR-A016 k2 "agora") a expressão estava DENTRO
  do próprio trecho e o Jev apontou outra mensagem; CR-A012 k1 herança "terça" acertada mas a 0,49 (→ nulo pelo
  piso); CR-A008 k2 pegou o "amanhã" da entrega de OUTRA pessoa. Nouls: `accepted` e `open_request` separam bem;
  `quoted` 0,47–0,87 × ≤ 0,19; `undone` quase não separa (cancelado 0,50–0,70 × compromisso 0,14–0,68) e, com a
  dúvida bloqueando a precedência, 30/47 saíram `revisar`.
- 2ª passada: (a) regra do LEIA-ME em código — expressão única dentro do trecho é o prazo (`PRAZO_DO_TRECHO`) — e dita
  na pergunta do prazo, que também ganhou "entrega de OUTRA pessoa → none" e "'só depois que…'/'assim que…' → none";
  (b) `por_nouls`: dúvida no meio da faixa não bloqueia um sinal conclusivo posterior (o `accepted` alto separa
  compromisso de cancelado melhor que o `undone`); (c) Nouls com regras curtas (`_REGRAS_CURTAS`) para cortar
  tokens. A Choice de veredito não mudou de texto. Resultado: ajuste 47/47 vereditos (P do vencedor ≥ 0,89), prazo
  36/36 nos vivos (24/24 nos compromissos), 0 `revisar`; Nouls 40/47 com 7 `revisar` e 0 erro caro (`undone` passou a
  separar: cancelado 0,65–0,96 × compromisso ≤ 0,11 — o bloco longo de regras embaralhava os Nouls); 9,5 mil tokens
  por conversa (antes 15,8 mil). Rascunho 10/10 e 8/8 nas duas passadas. O ajuste no teto não calibra o piso
  (curva plana de 0,0 a 0,8): `P_MIN_VENCEDOR` fica no 0,5 de partida.
"""

# ---------------------------------------------------------------------------------------- vocabulário
VEREDITOS = ["commitment", "proposal", "cancelled", "old_quote", "unaccepted_request"]
# Opção da Choice → rótulo do gabarito (dados em pt). `revisar` é a 6ª saída do sistema, nunca do gabarito.
ROTULO_DA_OPCAO = {"commitment": "compromisso", "proposal": "proposta", "cancelled": "cancelado",
                   "old_quote": "citacao_antiga", "unaccepted_request": "pedido_sem_aceite"}
REVISAR = "revisar"
NOULS = ["accepted", "undone", "quoted", "open_request"]

# Regras comuns (do LEIA-ME) — vão na Choice de veredito e nos Nouls de cada candidato.
_REGRAS = (
    "Judge the PAIR (excerpt, owner) as of the END of the conversation: when the last message has been read, does "
    "the owner owe this delivery? The excerpt may be the request ('você revisa até amanhã?') or the answer "
    "('reviso'); the verdict is about the DELIVERY, not about the sentence. Precedence: first ask whether the "
    "excerpt is something said NOW in this conversation or text quoted, pasted or forwarded from BEFORE it (an old "
    "e-mail, meeting minutes, a client's message, a clause, an automatic reply, 'you said \"…\"') — quoted text is "
    "old_quote whatever it says; then ask whether a LATER message in this conversation undid it — cancelled it, "
    "made it unnecessary, changed the day, handed it to someone else, changed the scope, or the reason for it "
    "disappeared (project cancelled, feature dropped, 'já resolvi', client postponed without a date, contrary order "
    "from another area) — that is cancelled even without the word 'cancela'; only then judge what is left. "
    "Taken on = commitment: the owner states it in first person or accepts a request made to them, including short "
    "acceptances ('pode deixar', 'consigo', 'fechado', 'combinado', 'ok', '👍', 'passo sim'); an offer by the owner "
    "that the other person accepts ('posso mandar quinta, se ajudar' — 'manda sim') becomes a commitment even if "
    "the offerer only answers 'combinado' or says nothing more; a reported acceptance ('falei com a Karen, ela "
    "confirmou segunda') is a commitment; 'a gente' followed by the same person taking it in first person is that "
    "person's commitment. Offered or hedged = proposal: 'posso', 'poderia', 'que tal eu', 'se quiserem', 'um dia', "
    "'vou tentar' alone, praise without acceptance ('boa ideia, mas antes…'), a proposal postponed ('vamos "
    "discutir na planning'), or a delivery conditioned on a THIRD PARTY's act that has not happened ('se o cliente "
    "mandar os extratos', 'desde que ele pague', 'assim que ele aprovar', 'só depois que ele confirmar'); a "
    "condition already met inside the conversation ('ela acabou de mandar' — 'recebi'), a courtesy caveat ('se nada "
    "pegar fogo') or the order of one's own work ('assim que fechar a sprint eu olho') do NOT make it a proposal; "
    "'vou tentar' followed by the same person firming the same delivery ('então quarta está pronto') is a "
    "commitment in both excerpts. Asked without acceptance = unaccepted_request: someone asked or assigned it and "
    "the owner did not accept — no reply, changed the subject, said they would check ('vou ver minha agenda e te "
    "falo'), refused ('essa semana não rola', 'tenho médico', 'agora não consigo'; a refusal is NOT cancelled, the "
    "asker did not withdraw it), or was not in the conversation / was not consulted ('o Jonas manda amanhã' said by "
    "someone else, 'ele está em audiência' answered by a third person). A later message that CHANGES the day, the "
    "owner or the scope cancels the earlier excerpt and the new excerpt carries what is valid; a later message that "
    "only CONFIRMS the same delivery changes nothing. When someone else takes the task over ('deixa que eu faço'), "
    "the first owner's excerpt is cancelled and the new owner's is a commitment. A request to 'alguém' / 'um de "
    "vocês': for a candidate who did not take it, it is cancelled if ANOTHER person took it and unaccepted_request "
    "if nobody did. 'A gente' later split into different owners and days: the collective sentence is cancelled and "
    "the split parts are the commitments. A proposal refused in so many words ('deixa pra lá') is cancelled; a "
    "proposal ignored or postponed stays a proposal. 'Como combinado ontem, o Fábio instala na quinta' + 'isso, "
    "quinta às 8h' is a commitment (nothing is quoted and the owner reaffirms now); 'você disse \"entrego na "
    "quarta\"' is old_quote — what counts is what the owner takes on afterwards, in another excerpt. The resolution "
    "of an EARLIER task does not touch a NEW request made after it."
)


# Regras curtas para os Nouls (informativos): cada Noul já diz a condição; repetir o bloco inteiro em quatro perguntas por
# candidato custava ~45% dos tokens da requisição (1ª passada: 15,8 mil tokens por conversa).
_REGRAS_CURTAS = (
    "Judge the PAIR (excerpt, owner) by what the conversation shows; the excerpt may be the request or the answer. "
    "Short acceptances count ('👍', 'ok', 'fechado', 'pode deixar'); an offer accepted by the other person counts as "
    "accepted; a reported acceptance counts; a refusal is not an undoing; a request to 'alguém' taken by another person "
    "is undone for the one who did not take it; a later message that only confirms the same delivery undoes nothing."
)


def _par(cand: dict) -> str:
    """Frase que identifica o par (trecho, responsável) com os caminhos do state entre crases."""
    return (f"Candidate `{cand['id']}` in `candidates` is the excerpt \"{cand['excerpt']}\" — a literal piece of message "
            f"`{cand['in_message']}` in `messages`, written by {cand['excerpt_author']} — paired with {cand['owner']} as "
            f"the possible OWNER of the delivery it describes"
            + (" (the owner wrote no message in this conversation)" if not cand["owner_messages"] else
               f" (the owner wrote {', '.join('`' + m + '`' for m in cand['owner_messages'])})")
            + (". Code found this excerpt INSIDE quotation marks or a forwarded block." if cand["inside_quotes"] else "."))


def pergunta_veredito(cand: dict) -> dict:
    """Choice `commitment | proposal | cancelled | old_quote | unaccepted_request` para UM candidato. Exemplos escritos à mão."""
    owner = cand["owner"]
    return {
        "type": "choice",
        "instructions": {
            "question": f"`messages` is a short work-chat conversation in Brazilian Portuguese, all written on "
                        f"`reference_date`, in order (`m1` first). {_par(cand)}. Read the WHOLE conversation to its end: "
                        f"when it ends, does {owner} owe this delivery — and if not, why not?",
            "rules": _REGRAS,
        },
        "criteria": {
            "commitment": {
                "what": f"{owner} took this delivery on and nothing later undid it: said it in first person ('mando "
                        f"amanhã', 'eu fecho o texto'), accepted a request made to them ('consigo', 'pode deixar', "
                        f"'fechado', '👍', 'passo sim'), had their offer accepted by the other person ('manda sim', 'pode "
                        f"ser') or had their acceptance reported ('ela confirmou segunda'). A caveat of courtesy or the "
                        f"order of their own work does not weaken it.",
                "not_for": "Text quoted from before this conversation (old_quote); a delivery that a later message "
                           "cancelled, replaced (other day, other owner, other scope) or made unnecessary (cancelled); an "
                           "offer or 'vou tentar' nobody confirmed, or an acceptance conditioned on a third party "
                           "(proposal); a request the owner never accepted, refused or was not asked about "
                           "(unaccepted_request).",
                "examples": ["Consigo, subo até quarta.", "Pode deixar, faço isso.", "Eu pego.",
                             "Posso mandar na quinta, se ajudar. — Manda sim. — Combinado."],
            },
            "proposal": {
                "what": f"{owner} offered, suggested or hedged and nobody confirmed it: 'posso revisar se quiserem', "
                        f"'que tal eu reescrever', 'eu poderia ajudar se sobrar tempo', 'um dia eu faço', 'vou tentar… "
                        f"depende'; an offer only praised or postponed ('boa ideia, mas antes…', 'vamos discutir na "
                        f"planning'); or an acceptance that depends on a THIRD PARTY's pending act ('se o cliente mandar "
                        f"os extratos, fecho na terça', 'aviso só depois que ele confirmar').",
                "not_for": "An offer the other person accepted (commitment); 'vou tentar' later firmed by the same person "
                           "(commitment); a proposal refused in so many words (cancelled); a condition already met in the "
                           "conversation, a courtesy caveat or the order of one's own work (commitment); a request made TO "
                           "the owner without acceptance (unaccepted_request).",
                "examples": ["Posso revisar o PR se quiserem.", "Que tal eu reescrever o worker na sprint que vem? — Vamos discutir na planning.",
                             "Se o cliente mandar os extratos até amanhã, fecho na terça."],
            },
            "cancelled": {
                "what": f"It was a request, proposal or commitment of THIS conversation and a LATER message undid it for "
                        f"{owner}: 'não precisa mais', 'deixa pra lá', the task was done by someone else ('já resolvi'), "
                        f"the day was changed ('mando na quinta' after 'mando na quarta'), another person took it over "
                        f"('deixa que eu faço'; 'eu pego' after a request to 'alguém'), the scope or the owner was split "
                        f"('eu fecho o texto e a Tati fecha as peças' after 'a gente entrega'), or the reason for it "
                        f"disappeared (project cancelled, client postponed without date).",
                "not_for": "Text quoted from before this conversation (old_quote); a later message that only confirms the "
                           "same delivery (commitment); a refusal by the owner — the asker did not withdraw the request "
                           "(unaccepted_request); a proposal merely ignored or postponed (proposal); a NEW request made "
                           "after another task was resolved: the resolution concerns the earlier task, not this one.",
                "examples": ["Fico de pedir o orçamento hoje. — O orçamento não precisa mais, o cliente desistiu.",
                             "Mando na quarta. — Ops, quarta tenho plantão. Mando na quinta.",
                             "Olho amanhã. — Já resolvi, era o índice que faltava."],
            },
            "old_quote": {
                "what": "The excerpt is text quoted, pasted or forwarded from BEFORE this conversation: an old e-mail or "
                        "ticket, meeting minutes, a changelog line, a contract clause, an automatic reply, a client's "
                        "message, or what someone 'said' on another day ('você disse \"entrego na quarta\"', 'segue o que "
                        "o cliente escreveu: \"…\"'). It is not something said now, whatever it promises.",
                "not_for": "A sentence said now that refers to an earlier agreement without quoting it ('como combinado "
                           "ontem, instalo na quinta' — commitment if reaffirmed); a sentence of this conversation that "
                           "merely mentions the past ('removi em agosto'); the new delivery the owner takes on after the "
                           "quote (another excerpt).",
                "examples": ["Segue o que o cliente escreveu no chamado de setembro: \"vocês prometeram o reembolso para o dia 20\".",
                             "Do changelog antigo: \"Leo ficou de remover o endpoint v1 até setembro\".",
                             "Na reunião de segunda você disse \"entrego o roteiro na quarta\"."],
            },
            "unaccepted_request": {
                "what": f"Someone asked {owner} for this delivery or assigned it to them ('pode entregar na sexta?', "
                        f"'preciso da minuta até quinta', 'o Jonas manda amanhã') and {owner} did not accept: no reply "
                        f"before the conversation ends, changed the subject, said they would check ('vou ver minha agenda "
                        f"e te falo'), refused ('essa semana não rola', 'agora não consigo'), was answered by a third "
                        f"person ('ele está em audiência'), or was not in the conversation / was not consulted.",
                "not_for": "A request the owner accepted, even briefly ('👍', 'ok', 'ligo') (commitment); a reported "
                           "acceptance (commitment); a request to 'alguém' that ANOTHER person took (cancelled for this "
                           "owner); a request later withdrawn or made unnecessary (cancelled); an offer made BY the owner "
                           "(proposal); quoted text (old_quote).",
                "examples": ["Vítor, pode entregar a planilha de custos na sexta? — (Vítor never answers)",
                             "Pode retornar para o cliente amanhã? — Vou ver minha agenda e te falo.",
                             "O Jonas manda o vídeo editado amanhã. — Ele confirmou? — Ainda não falei com ele."],
            },
        },
    }


def perguntas_nouls(cand: dict) -> dict:
    """Variante informativa: quatro Nouls atômicos por candidato, combinados em código (`compromisso.por_nouls`)."""
    kid, owner = cand["id"], cand["owner"]
    cab = (f"`messages` is a short work-chat conversation in Brazilian Portuguese, all written on `reference_date`, in "
           f"order. {_par(cand)}. ")
    return {
        f"{kid}_accepted": {
            "type": "noul",
            "instructions": cab + f"In THIS conversation {owner} takes this delivery on in their own words, or their "
                                  f"offer is accepted by the other person, or their acceptance is reported: a first-person "
                                  f"statement ('mando amanhã'), an acceptance of a request made to them ('consigo', 'pode "
                                  f"deixar', '👍', 'passo sim'), 'manda sim' / 'pode ser' answering their offer, 'ela "
                                  f"confirmou segunda'. Ignore whether something LATER undid it. " + _REGRAS_CURTAS,
            "criteria": {"true": f"There is an explicit acceptance or first-person statement that makes {owner} the owner of "
                                 f"this delivery, by {owner} or accepting {owner}'s offer, or reported.",
                         "false": "No acceptance: the request got no reply, was deflected or refused; the owner only offered "
                                  "or hedged; the acceptance depends on a third party; someone else spoke for an absent "
                                  "owner; or the excerpt is quoted text."},
        },
        f"{kid}_undone": {
            "type": "noul",
            "instructions": cab + f"A message AFTER `{cand['in_message']}` in this conversation undoes this delivery for "
                                  f"{owner}: cancels it, says it is no longer needed, says it was already done, moves it "
                                  f"to another day, hands it to another person, splits or changes its scope, or removes "
                                  f"the reason for it (project cancelled). " + _REGRAS_CURTAS,
            "criteria": {"true": f"A later message of this conversation cancels, replaces or makes unnecessary this delivery "
                                 f"for {owner}.",
                         "false": "Nothing later undoes it: later messages only confirm it, talk about other tasks, or the "
                                  "owner merely refused (the asker did not withdraw); or the excerpt is quoted text from "
                                  "before this conversation."},
        },
        f"{kid}_quoted": {
            "type": "noul",
            "instructions": cab + "The excerpt is text quoted, pasted or forwarded from BEFORE this conversation (an old "
                                  "e-mail, ticket or changelog, meeting minutes, a client's message, a clause, an automatic "
                                  "reply, what someone 'said' on another day) — not a sentence said now. " + _REGRAS_CURTAS,
            "criteria": {"true": "The excerpt is quoted or forwarded text from before this conversation.",
                         "false": "The excerpt is said now in this conversation, even if it refers to an earlier agreement "
                                  "without quoting it."},
        },
        f"{kid}_open_request": {
            "type": "noul",
            "instructions": cab + f"Someone asked {owner} for this delivery or assigned it to them, and {owner} did not "
                                  f"accept it by the end of the conversation: no reply, changed the subject, said they would "
                                  f"check, refused, was answered by a third person, or was absent / not consulted. "
                                  + _REGRAS_CURTAS,
            "criteria": {"true": f"It is a request or assignment to {owner} that {owner} never accepted.",
                         "false": f"{owner} accepted it, or it was never a request to {owner} (an offer by {owner}, a "
                                  f"first-person statement, quoted text), or another person took the task over."},
        },
    }


def pergunta_prazo(cand: dict, expressoes: list[dict]) -> dict:
    """Choice da expressão de tempo que dá o DIA da entrega, entre expressões LIDAS PELO CÓDIGO (+ `none`). O Jev
    aponta; o código resolve contra `reference_date` e copia a data. Consumida só em compromisso/proposta/pedido."""
    kid, owner = cand["id"], cand["owner"]
    return {
        "type": "choice",
        "instructions": {
            "question": f"`messages` is a short work-chat conversation in Brazilian Portuguese, all written on "
                        f"`reference_date`, in order. {_par(cand)}. The options below are the time expressions code found "
                        f"in the messages (each with the message it is in). Which one states the DAY this delivery is "
                        f"asked or promised for — whether or not {owner} accepted it?",
            "rules": "An expression INSIDE the excerpt itself is the day of this delivery ('confiro os encargos antes, "
                     "até terça' → 'até terça'; 'me lembra à tarde?' → 'à tarde'; 'cobro agora' → 'agora'), even when "
                     "another day is mentioned around it for another task. Otherwise the day can be in the request the "
                     "excerpt answers (whoever accepts or takes over a request inherits its day unless they say another "
                     "day) or in a later answer about this delivery ('Para quando?' — 'Segunda.'). When the day was "
                     "changed later, pick the LAST day stated for this delivery. Pick `none` when no expression gives the "
                     "day of THIS delivery: the expressions belong to another task or to ANOTHER PERSON's delivery "
                     "('o Jonas manda amanhã' says nothing about when Lívia will warn the client), describe a past event "
                     "('removi em agosto', 'na reunião de segunda você disse'), describe the moment of speaking about "
                     "something else ('agora não consigo'), or the delivery waits for someone else ('só depois que ele "
                     "confirmar', 'assim que ele aprovar') and so has no day. An expression without a day ('semana que "
                     "vem', 'em breve') may be picked when it is what was said for this delivery. Do not compute dates: "
                     "just point to the expression.",
        },
        "criteria": {
            **{e["chave"]: f"The day of this delivery is given by \"{e['bruto']}\" in message `{e['msg']}`." for e in expressoes},
            "none": "No listed expression gives the day asked or promised for this delivery.",
        },
    }


# ---------------------------------------------------------------------------------------- política
# Variante principal declarada ANTES do teste (entra no manifesto via CRITERIO_CONTINUAR); as outras são informativas.
VARIANTE_PRINCIPAL = "choice"
# Choice de veredito: vence a maior probabilidade; vencedor abaixo deste piso → `revisar`. Partida = piso global
# das notas (NÚCLEO §6: ~0,5–0,6); afinado só no ajuste.
P_MIN_VENCEDOR = 0.5
# Choice do prazo: vencedor abaixo do piso → `prazo` nulo (tarefa sem dia é mais barata que tarefa com dia errado).
P_MIN_PRAZO = 0.5
# Regra de código do LEIA-ME ("a data é a da entrega, esteja ela no trecho…"): quando o PRÓPRIO trecho contém exatamente
# uma expressão de tempo, ela é o prazo e a Choice do prazo não é consultada (fica registrada para comparação). Com zero
# ou duas+ expressões no trecho, o Jev escolhe (herança do pedido, resposta posterior, troca de data).
PRAZO_DO_TRECHO = True
# Nouls da variante informativa: ≤ nao → não; ≥ sim → sim; meio = dúvida (→ `revisar`). Partida 0,3–0,7.
FAIXA = {"accepted": (0.3, 0.7), "undone": (0.3, 0.7), "quoted": (0.3, 0.7), "open_request": (0.3, 0.7)}
# Guarda de código (regra 8): trecho entre aspas / bloco encaminhado nunca sai `compromisso` sozinho → `revisar`.
GUARDA_CITACAO = True
# Faixa validada: conversas de 2–6 mensagens curtas e 2–4 candidatos. Acima do teto a conversa NÃO vai ao Jev: tudo
# `revisar`, origem `longa` (contada à parte). Não é limiar afinado.
TETO_CARACTERES = 4000
TETO_CANDIDATOS = 8

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado em 2026-10-01, depois da 2ª passada do ajuste e ANTES de abrir `dados/teste.json`, com os denominadores da
# tabela do LEIA-ME (teste: 46 conversas, 102 candidatos; 57 `compromisso`, 10 `proposta`, 17 `cancelado`, 7
# `citacao_antiga`, 11 `pedido_sem_aceite`; 66 com `prazo`). Limites ABSOLUTOS no erro caro + piso de acerto; o
# baseline fica informativo (margem sobre baseline é critério frágil: metodo.md 2026-10-01). "Sempre compromisso"
# acerta 57/102 = 0,559: o piso 4 fica bem acima disso. Os pisos ficam abaixo do ajuste de propósito, porque o
# teste tem 93% de difíceis e famílias com 1 caso no ajuste (correção tardia 1→5, aceite curto, oferta aceita).
# (Os números do ajuste que embasaram cada limite estão no README; este bloco foi fechado antes do congelamento.)
CRITERIO_CONTINUAR = {
    "onde": "no teste (46 conversas, 102 candidatos), variante principal `choice` com a política acima",
    "variante_principal": VARIANTE_PRINCIPAL,
    "1_tarefa_fantasma": "candidato `proposta`, `cancelado`, `citacao_antiga` ou `pedido_sem_aceite` no gabarito que saiu `compromisso` ≤ 3 de 45",
    "2_compromisso_perdido": "candidato `compromisso` no gabarito que saiu `cancelado` ou `citacao_antiga` ≤ 3 de 57",
    "3_prazo_dos_compromissos": "entre os `compromisso` acertados, `prazo` igual ao gabarito (data ou nulo) ≥ 0,85",
    "4_acerto_total": "veredito exato nos 102 candidatos (`revisar` conta como erro) ≥ 0,80 (sempre-compromisso = 0,559)",
    "5_acerto_nao_compromisso": "veredito exato nos 45 candidatos que não são `compromisso` ≥ 0,70",
    "secundario_nao_decide": "`revisar` ≤ 15% dos candidatos; `prazo` exato nos vivos acertados (compromisso/proposta/pedido) ≥ 0,85; baseline informativo",
    "se_falhar": "1 ou 2 falhando = o desenho não serve para criar/fechar tarefa sem humano; 3, 4 ou 5 falhando = volta ao ajuste com dados novos",
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"fantasma_max": 3, "perdido_max": 3, "prazo_compromisso_min": 0.85, "acerto_total_min": 0.80,
                "acerto_nao_compromisso_min": 0.70, "revisar_max": 0.15, "prazo_vivos_min": 0.85},
}

# ---------------------------------------------------------------------------------------- baseline de código
# O que um dev escreveria em meia hora: verbos de compromisso em 1ª pessoa, negação/cancelamento, pergunta
# ("pode…?") e aceite curto. Sem acento, minúsculas. Precedência no código (`compromisso.baseline`):
# aspas → citacao_antiga; cancelamento depois do trecho → cancelado; pergunta/pedido ao responsável → aceite
# posterior dele? compromisso : pedido_sem_aceite; hedge → proposta; verbo de compromisso → compromisso;
# senão: autor é o responsável → compromisso, senão pedido_sem_aceite.
BASELINE_CANCELAMENTO = [r"nao precisa mais", r"cancel", r"deixa (que eu|pra la|para la)", r"ja resolvi", r"desist",
                         r"nao precisa", r"esquece", r"fica para (a )?(proxima|depois)", r"\bops\b", r"\beu pego\b",
                         r"\bno lugar\b", r"adiou", r"sem data"]
BASELINE_PEDIDO = [r"^(pode|consegue|consegu|da pra|voce|vc|tem como|preciso|precisamos|precisa|alguem|me lembra|me passa|me manda|revisa|envia|entrega|manda)\b",
                   r"\?\s*$", r"\bque tal voce\b", r"\bficou de\b", r"\bprecisa mandar\b"]
BASELINE_ACEITE = [r"\b(sim|consigo|pode deixar|fechado|combinado|ok|beleza|claro|pego|deixa comigo|passo|ligo|olho|envio|mando|entrego|respondo|migro|reviso|renovo|faco|subo|fecho|emito|aviso|retorno|assumo)\b",
                   r"👍", r"\bmando\b", r"\bbora\b", r"\btranquilo\b"]
BASELINE_RECUSA = [r"nao rola", r"nao consigo", r"nao da\b", r"nao vai dar", r"tenho medico", r"to lotad", r"vou ver", r"te falo", r"nao posso"]
BASELINE_HEDGE = [r"\bposso\b", r"\bpoderia\b", r"\bque tal eu\b", r"\bse quiserem\b", r"\bse ajudar\b", r"\bvou tentar\b",
                  r"\bse sobrar\b", r"\btalvez\b", r"\bum dia\b", r"\bdepende\b", r"\bse o cliente\b", r"\bse ele\b", r"\bse ela\b",
                  r"\bassim que ele\b", r"\bassim que ela\b", r"\bdepois que ele\b", r"\bnao sei se\b", r"\bse der\b", r"\bse rolar\b"]
BASELINE_COMPROMISSO = [r"\b(mando|envio|entrego|faco|subo|fecho|reviso|ligo|aviso|respondo|migro|renovo|emito|retorno|assumo|olho|passo|confiro|protocolo|cobro|instalo|resolvo|publico|atualizo|documento|preparo|agendo|marco)\b",
                       r"\bfico de\b", r"\bvou (mandar|enviar|entregar|fazer|subir|fechar|revisar|ligar|avisar|responder|cobrar|resolver|olhar|preparar|instalar|protocolar|publicar|atualizar|documentar|agendar|marcar)\b",
                       r"\beu (pego|fecho|faco|mando|envio|entrego|aviso|ligo|respondo|olho|resolvo|cuido)\b", r"\bpode deixar\b", r"\bdeixa comigo\b",
                       r"\bdeixa que eu\b", r"\breiniciando\b", r"\bvou cobrar\b"]
