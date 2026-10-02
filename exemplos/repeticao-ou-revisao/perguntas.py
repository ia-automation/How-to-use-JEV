"""Perguntas, faixas e política do repetição-ou-revisão — o ÚNICO arquivo que um humano precisa revisar.

Um GRUPO de 2–3 mensagens do mesmo remetente (WhatsApp de imobiliária, pt-BR), já ordenadas pelo código, vira UM
state `{"from", "earlier_messages", "last_message"}` e UMA requisição ao Jev. O código resolve antes o que é exato
(mesmo ID, texto idêntico após normalização); o Jev julga a RELAÇÃO SEMÂNTICA da última mensagem com as anteriores;
`relacao.py` compõe o sinal de reconciliação com os números daqui:
  colapsar (same_intent) · substituir (revision → vale a última) · somar (additional_request) · revisar (unclear/dúvida).
Nada é executado nem descartado daqui: é um sinal para a fila, não mecanismo de "exatamente uma vez".

Desenho (regras de rotulagem em dados/LEIA-ME.md; receita-irmã: conhecimento/receitas/alinhamento-de-entidades.md):
- `relation` (Choice, 4 opções com `what`/`not_for`/`examples`) — a leitura relativa: QUAL das quatro relações.
- Nouls absolutos na mesma requisição (limite #8: Choice diz "qual", Noul diz "se"; os dois não se substituem):
  `replaces_previous`   — a última cancela ou muda algo pedido antes;
  `adds_new_request`    — a última faz um pedido NOVO e o anterior continua de pé;
  `completes_previous`  — a última traz o detalhe que faltava sem contradizer (complemento = `additional_request`
                          por decisão do rotulador; condição própria, pergunta própria);
  `same_request_again`  — a última não traz nada novo: repete, confirma, cobra ou conserta a grafia;
  e três Nouls de DÚVIDA, o lado absoluto da opção `unclear` (cada um uma família do LEIA-ME):
  `no_link_word` (atributo diferente sem palavra de troca nem de soma), `target_not_said` (cancela depois de
  dois pedidos sem dizer qual), `arrived_out_of_order` (a última pede o que a anterior já tinha recusado).
- O state aponta a última mensagem por NOME (`last_message`), não por índice: menos indireção (limite #4) e a
  pergunta é a mesma para grupos de 2 e de 3.
- Ordem e tempo são do CÓDIGO (limite #3): a ordem vem pronta (posição no array); `minutos_desde_a_primeira` é só
  validado (não decrescente) e NÃO vai ao state — o LEIA-ME diz que o intervalo não decide, e número no state é
  distrator (limite #5). Medido no ajuste: ver `MINUTOS_NO_STATE`.

Perguntas em inglês sobre mensagens em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram e custaram +10%);
as palavras-marca do português ("também", "em vez", "*") aparecem entre aspas porque a leitura é literal (limite #1).
Os exemplos das opções são os do LEIA-ME (regra de rotulagem), não casos do ajuste.

Afinação (só no ajuste, 2026-10-01; 29 grupos, 27 requisições por passada — 2 grupos o código resolve sem chamada):
- 1ª passada (Choice + 3 Nouls: troca, soma, repetição; faixa 0,2–0,8): só Choice 0,897; política 0,793, zero erro
  caro. Três defeitos de desenho, nenhum de limiar:
  (a) complemento ("Pode ser às 10h" depois de "visita no sábado") deu `adds_new_request` 0,21: um detalhe que
      faltava não é, ao pé da letra, "pedir algo a mais" (limite #1). Virou pergunta própria, `completes_previous`
      (uma condição por pergunta) → 0,93 e 0,94 nos dois complementos;
  (b) "*visita" (asterisco que só corrige grafia) deu `same_request_again` 0,36: a mensagem sozinha não "pede" nada.
      A instrução passou de "pede a mesma coisa" para "não traz nada novo: repete, confirma, cobra ou conserta a
      grafia" → 0,80;
  (c) os 4 `unclear` tinham `replaces_previous` 0,81–0,96 apesar do `false` escrito para eles; a dúvida morava só
      na Choice (relativa), por margens de 0,01 na confiança (0,49 contra piso 0,5), e "desmarca" depois de dois
      pedidos saiu `substituir` (Choice revision 0,78). Entraram três Nouls de dúvida, um por família do LEIA-ME.
- 2ª passada (Choice + 7 Nouls, faixa 0,2–0,8): política 0,897, 4/4 `unclear` a revisar, zero erro caro. Três
  revisões sem necessidade; em duas, valores a 0,01–0,06 dos cortes (soma 0,79; repetição 0,26 e 0,76), e um
  acerto passou por 0,01 (troca 0,19 no "*visita").
- 3ª passada: `completes_previous` lia "minha esposa também pediu essa visita, é a mesma" como complemento (0,63);
  o `false` ganhou a regra do LEIA-ME (cópia de terceiro é repetição) → 0,35. E a faixa foi para 0,3–0,7 (ver
  FAIXA). Política 0,931 (27/29); sobram dois `revisar` sem necessidade: a cópia de terceiro (0,35 > 0,3) e o
  "segundo pedido parecido" sem conectivo (a Choice hesita, confiança 0,29, e `no_link_word` dá 0,87).
- Variantes medidas (`run.py variantes` → resultados-variantes.md): minutos no state não mudaram nenhuma decisão
  (diferença média nos Nouls 0,011, a ordem da variação entre chamadas idênticas) e custam +30 tokens → ficam
  fora. Grupo de 3 em pares perdeu 1 dos 3 grupos (o par "?" → "alguém pode agendar…" sem a primeira mensagem é
  ilegível) e custa uma requisição a mais → grupo inteiro.
A redação da Choice não mudou entre as passadas, e mesmo assim ela trocou de lado no grupo fora de ordem
(RR-A026: unclear 0,36 → revision 0,37 → unclear 0,38): é o que os Nouls de dúvida seguram. Nenhuma pergunta foi
alargada para consertar um caso: as mudanças escrevem regra do LEIA-ME ou separam uma condição em pergunta própria.
"""

OPCOES = ["same_intent", "revision", "additional_request", "unclear"]
# Relação → sinal de reconciliação que o consumidor recebe.
SINAL = {"same_intent": "colapsar", "revision": "substituir", "additional_request": "somar", "unclear": "revisar"}
# `de` dos dados (pt) → `from` do state (en). Remetente fora da lista = entrada inválida.
REMETENTES = {"cliente": "client", "corretor": "broker"}


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


# State: {"from": "client"|"broker", "earlier_messages": ["…", …], "last_message": "…"} — só grupos que o código
# não resolveu por igualdade exata.
PERGUNTAS = {
    "relation": {
        "type": "choice",
        "instructions": {
            "question": "`earlier_messages` and `last_message` are WhatsApp messages in Brazilian Portuguese that "
                        "the same person (`from`) sent to a real-estate agency, in order of arrival. What does "
                        "`last_message` do to what `earlier_messages` asked for?",
            "focus": "Decide by what the messages say about the request (which property, day, time, people, kind "
                     "of request), not by how similar the wording is.",
        },
        "criteria": {
            "same_intent": {
                "what": "`last_message` asks again for the same thing: a resend, a paraphrase, a retyped version "
                        "with typos fixed, a nudge ('?', 'alguém aí?'), a reminder or a confirmation. Property, day "
                        "and time are the same as before, nothing is cancelled and nothing new is asked. Also: "
                        "telling the agency that a request made by another person (a spouse) is this very same "
                        "request, and a `*` correction that only fixes spelling.",
                "not_for": "Any change of day, time, property, listing code or people; a cancellation; a second "
                           "request; a detail that was missing before.",
                "examples": ["earlier 'visita dia 10' / last 'visita sábado dia 10'",
                             "last 'não precisa mudar nada, só confirmando terça 15h'",
                             "earlier '... vizita ...' / last '*visita'",
                             "last 'minha esposa também pediu essa visita, é a mesma'"],
            },
            "revision": {
                "what": "`last_message` changes, replaces or cancels something asked before: another day, time, "
                        "property or listing code INSTEAD of the earlier one, a different number of people, giving "
                        "up ('cancela', 'deixa pra lá', 'não vou conseguir ir'), or undoing an earlier change "
                        "('esquece, deixa terça mesmo'). After it the earlier request is no longer valid as it "
                        "was. It still counts when the same message also asks for something new, and when a `*` "
                        "correction changes the content.",
                "not_for": "A second request that leaves the first one standing; a missing detail added without "
                           "contradicting anything; the same request repeated or confirmed.",
                "examples": ["earlier 'marca terça 15h' / last 'não, terça não; quarta'",
                             "earlier 'às 10h' / last '*11h'",
                             "last 'sexta também não vai dar, vê segunda'",
                             "last 'muda pra domingo e me manda a planta'"],
            },
            "additional_request": {
                "what": "`last_message` asks for something more and everything asked before still stands: another "
                        "property, a second visit, or another kind of request (photos, price, location, "
                        "financing), with or without 'e também'. A complete second visit request for a different "
                        "property at a different time counts even without a connective. Also a complement: a "
                        "detail that was missing and contradicts nothing (the time for a day already given, who is "
                        "coming, 'também pode ser à tarde' widening the availability), and a new visit asked for "
                        "another person.",
                "not_for": "Replacing or cancelling what was asked; repeating the same request; 'também' inside a "
                           "refusal ('sexta também não dá').",
                "examples": ["earlier 'me manda as fotos' / last 'e quero agendar uma visita'",
                             "earlier 'visita no sábado' / last 'pode ser às 10h'",
                             "last 'minha esposa também quer ver, mas no domingo; marca uma pra ela'",
                             "last 'volto na terça com o engenheiro, já deixa agendado também'"],
            },
            "unclear": {
                "what": "The text does not tell whether `last_message` replaces the earlier request or adds a "
                        "second one, so a person has to ask. Typical: the request is stated again with ONE "
                        "attribute different (another day, another time on the same day, or another property at "
                        "the very same day and time) and no word of change ('não', 'em vez', 'na verdade', "
                        "'melhor', 'muda') or of addition ('e', 'também', 'outra'); a cancellation after two "
                        "different requests that does not say which one; another person's wish reported without "
                        "saying whether it replaces or adds; or the messages seem to have arrived out of order "
                        "(`last_message` asks for what an earlier message had already rejected or corrected).",
                "not_for": "Messages whose wording says what happens: an explicit change or cancellation, an "
                           "explicit addition, or a plain repetition.",
                "examples": ["earlier 'marca terça 15h' / last 'quarta 15h'",
                             "earlier 'então fica quarta mesmo' / last 'consegue terça 15h?'",
                             "earlier two visit requests / last 'cancela'",
                             "last 'minha esposa pediu domingo'"],
            },
        },
    },
    "replaces_previous": _noul(
        "`last_message` cancels or changes something that `earlier_messages` asked for.",
        "It moves the earlier request to another day, time or property, corrects a listing code or the number of "
        "people, cancels or gives up ('cancela', 'deixa pra lá', 'não vou conseguir ir'), undoes an earlier "
        "change, or is a `*` correction that changes the content. It counts even if the same message also asks "
        "for something new.",
        "Nothing asked before is cancelled or changed: `last_message` repeats, confirms ('não precisa mudar nada') "
        "or nudges; fixes only spelling; adds another request or a missing detail while the earlier request "
        "stands; widens the availability without dropping the earlier option ('também pode ser à tarde'); or "
        "states a different day, time or property with no word saying that it replaces the earlier one.",
    ),
    "adds_new_request": _noul(
        "`last_message` makes a new request in addition, and what `earlier_messages` asked for still stands.",
        "It asks for another property, a second visit or another kind of request (photos, price, location, "
        "financing) on top of the earlier one, with or without 'e também'; or asks for a new visit for another "
        "person. A complete second visit request for a different property at a different time counts even "
        "without a connective.",
        "No new request is made on top: `last_message` repeats or confirms the same request; says that a request "
        "made by another person is this very same request; replaces or cancels the earlier request (even with "
        "'também', as in 'sexta também não dá', and even if it also asks for something new); or only restates "
        "the request with one attribute different and no word of addition.",
    ),
    "completes_previous": _noul(
        "`last_message` adds a detail that the earlier request left open, and contradicts nothing that was asked.",
        "It gives the time for a day already given, says who is coming, or widens the availability ('também pode "
        "ser à tarde'): the earlier request stays as it was and gains the detail.",
        "It supplies no missing detail: it repeats or confirms what was already said; or it says that a request "
        "made by another person is this very same request; or it CHANGES a detail that was already given "
        "(another day or time instead of the one stated); or it cancels; or it makes a separate second request.",
    ),
    "same_request_again": _noul(
        "`last_message` brings nothing new: it only repeats, rephrases, confirms, nudges or fixes the spelling "
        "of what `earlier_messages` already asked for.",
        "It is a resend or copy, a paraphrase with the same property, day and time, a retyped version that only "
        "fixes typos or spelling (including a `*` spelling correction), a nudge ('?', 'oi?', 'alguém aí?'), a "
        "reminder, or a confirmation that nothing changes; or it says that a request made by another person is "
        "this very same request.",
        "Something differs or is new: another day, time, property, listing code or number of people; a "
        "cancellation; a second request; a detail that was missing before; or going back to what the first "
        "message asked after a change (that undoes a change, it is not a repetition).",
    ),
    # --- Nouls de dúvida: o lado absoluto da opção `unclear` (uma condição por pergunta; regras do LEIA-ME)
    "no_link_word": _noul(
        "`last_message` states a request with a day, time or property different from the one in "
        "`earlier_messages`, and contains no word telling whether it replaces the earlier request or is a second "
        "request.",
        "The request is just stated again with one thing different (another day, another time on the same day, "
        "or another property at the very same day and time), with no word of change ('não', 'em vez', 'na "
        "verdade', 'melhor', 'muda', 'corrigindo', a `*`) and no word of addition ('e', 'também', 'outra', 'mais').",
        "`last_message` says how it relates: it has a word of change, refusal, cancellation or correction, or a "
        "word of addition, or gives a reason; or it is a repetition with nothing different; or it is a complete "
        "second request for a different property at a different time (two visits that fit one after the other).",
    ),
    "target_not_said": _noul(
        "`earlier_messages` contain more than one request, and `last_message` cancels or changes a request "
        "without saying which one.",
        "After two different requests (two visits, two properties), `last_message` says only 'cancela', "
        "'desmarca', 'muda' or similar, with nothing that identifies which request it means.",
        "There is only one earlier request (possibly repeated or already revised); or `last_message` names what "
        "it cancels or changes (the day, the property, 'os dois', 'tudo'); or it does not cancel or change anything.",
    ),
    "arrived_out_of_order": _noul(
        "The messages seem to have arrived out of order: `last_message` asks for exactly what an earlier message "
        "had already rejected, corrected or replaced.",
        "An earlier message already says that an option is not possible or was replaced ('terça não consigo', "
        "'então fica quarta mesmo'), and `last_message` asks for that same option as if nothing had been said: "
        "it reads as written BEFORE the earlier message.",
        "The order makes sense: `last_message` reacts to the earlier messages (corrects, cancels, adds, repeats), "
        "or explicitly goes back to an earlier option ('esquece, deixa terça mesmo').",
    ),
}

CHOICE = "relation"
NOULS = [q for q, p in PERGUNTAS.items() if p["type"] == "noul"]
NOULS_SOMA = ["adds_new_request", "completes_previous"]                        # qualquer um em `sim` sustenta `somar`
NOULS_DUVIDA = ["no_link_word", "target_not_said", "arrived_out_of_order"]     # qualquer um em `sim` → revisar

# ---------------------------------------------------------------------------------------- state (medido no ajuste)
MINUTOS_NO_STATE = False   # True = cada mensagem vai como {"text", "minutes_since_first"} (variante medida)
GRUPO_DE_3 = "inteiro"     # "inteiro" = 1 requisição com as 3 mensagens; "pares" = 2 requisições (m1→m2, m2→m3)

# ---------------------------------------------------------------------------------------- política
# Noul em três faixas: ≤ nao → não; ≥ sim → sim; meio = dúvida. Partida 0,2–0,8 (NÚCLEO §6).
# Política ASSIMÉTRICA. Erros caros: `revision` lida como `same_intent` (colapsar apaga a correção) e `same_intent`
# lida como `additional_request` (somar duplica o efeito). Por isso:
#   colapsar   exige Choice same_intent + `same_request_again` sim + `replaces_previous` NÃO + os dois de soma NÃO;
#   somar      exige Choice additional_request + (`adds_new_request` OU `completes_previous`) sim +
#              `same_request_again` NÃO + `replaces_previous` NÃO;
#   substituir exige Choice revision + `replaces_previous` sim (e `same_request_again` não pode estar em sim);
#   qualquer Noul de dúvida em `sim`, qualquer outra combinação, Choice `unclear` ou confiança da Choice abaixo
#   do piso → revisar.
# Faixa 0,3–0,7 (e não 0,2–0,8): no ajuste o Noul que confirma a relação do gabarito ficou em ≥ 0,76 (tirando
# o caso difícil sem conectivo), mas quatro valores caíam a 0,01–0,06 dos cortes de partida — troca 0,19–0,21 no
# "*visita"; repetição 0,22–0,26 e soma 0,77–0,79 no mesmo grupo de 3; repetição 0,76 na cópia de terceiro —, a
# mesma ordem da variação entre chamadas idênticas (p95 ~0,05, NÚCLEO §6). 0,3 e 0,7 ficam no vão. O lado caro
# continua com duas chaves: a Choice tem de propor E o Noul contrário tem de estar em `não` (no ajuste, revisões
# reais: `replaces_previous` ≥ 0,88; repetições reais: ≤ 0,21).
FAIXA = {q: (0.3, 0.7) for q in NOULS}
CONF_MIN = 0.5           # piso da confiança da Choice (NÚCLEO §6: piso global ~0,5–0,6)
# Faixa validada: os dados têm 2–3 mensagens de até ~110 caracteres. Fora disso o grupo NÃO vai ao Jev: `revisar`.
MAX_MENSAGENS = 3        # mensagens DISTINTAS depois da deduplicação exata
TETO_CARACTERES = 1500

# ---------------------------------------------------------------------------------------- baselines de código
# Similaridade lexical (Jaccard de palavras entre a última e a anterior mais parecida): ≥ MESMO → same_intent;
# ≥ REVISAO → revision (parecida mas mudou); abaixo → additional_request. Limiares = os melhores da grade do
# ajuste (17/29 = 0,586; o patamar vai de 0,40 a 0,55 no MESMO, com REVISAO 0,05): o baseline recebe a mesma
# chance de afinação que o Jev.
JACCARD_MESMO = 0.5
JACCARD_REVISAO = 0.05

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado em 2026-10-01, ANTES de abrir `dados/teste.json`. Denominadores pela tabela do LEIA-ME (teste: 58 grupos =
# 16 same_intent, 18 revision, 17 additional_request, 7 unclear). No ajuste: Jev 0,931; melhor baseline 0,586.
CRITERIO_CONTINUAR = {
    "onde": "no teste (58 grupos: 16 same_intent, 18 revision, 17 additional_request, 7 unclear), com a política acima",
    "1_correcao_perdida": "revisão (gabarito revision) que saiu `colapsar` = 0 (de 18)",
    "2_efeito_duplicado": "repetição (gabarito same_intent) que saiu `somar` ≤ 1 (de 16)",
    "3_acerto_relacao": "relação (4 classes) ≥ melhor baseline de código no próprio teste + 0,15",
    "secundario_nao_decide": "unclear → `revisar` ≥ 70% (≥ 5 de 7); revisou sem necessidade ≤ 20% dos decidíveis; `acao_vigente` certa ≥ 80%",
    "se_falhar": "1 falhando = não serve para colapsar sem humano (só a igualdade exata do código colapsa); 2 falhando = `somar` precisa de confirmação; 3 falhando = a regra de código basta",
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"correcao_perdida_max": 0, "efeito_duplicado_max": 1, "margem_relacao": 0.15,
                "unclear_revisar_min_fracao": 0.7, "revisou_sem_necessidade_max": 0.2, "vigente_min_fracao": 0.8},
}
