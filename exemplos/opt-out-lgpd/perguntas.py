"""Perguntas, faixas e política do opt-out/LGPD — o ÚNICO arquivo que um humano precisa revisar.

Uma mensagem de cliente (WhatsApp, pt-BR) vira UM state `{"message"}` e UMA requisição ao Jev. O Jev julga
sinais atômicos; `optout.py` decide a ação (`bloquear_envios` / `abrir_pedido_lgpd(tipo)` / `pausar` /
`seguir` / `revisar`) com os números daqui. Mudar política = editar número, sem chamar a API de novo.

Desenho (regras de rotulagem em dados/LEIA-ME.md):
- `opt_out` (Noul): pede para parar o contato NESTE número, sem prazo de retomada. Só o pedido explícito —
  "exclusão implica opt-out" é regra do CÓDIGO (optout.decidir), não entra na pergunta.
- `temporary_pause` (Noul): pede para não ser procurado agora, com prazo ou condição de retomada.
- `lgpd_request` (Noul): exerce direito de titular (exclusão, acesso, origem, correção).
- `lgpd_type` (Choice + `none`): qual direito; consumida SÓ se `lgpd_request` passar (Choice é relativa: sempre
  há vencedor; o Noul absoluto é o portão — limite #8: as duas não somam nem se substituem).
- Nouls de guarda (absolutos, na mesma requisição — pergunta extra ≈ 20 tokens):
  `wants_contact_to_continue` — diz que podem continuar mandando (negação "não precisa parar"; exceção do
  LEIA-ME: exclusão parcial com "continuem mandando" → `revisar` com o envio suspenso até confirmar — guarda
  não dispensa bloqueio sozinho, revisão de 2026-10-01);
  `stop_without_object` — "para" / "não quero mais" sem dizer o quê (gabarito `null` → humano confirma);
  `about_another_contact` — o pedido de parar é sobre o número de OUTRA pessoa (terceiro).

`false` de cada Noul lista os casos do MEDO: negação, pausa × definitivo, preferência de canal, filtro,
terceiro, fim de interesse sem pedido. Perguntas em inglês sobre mensagens em pt-BR (triagem 2026-09-30:
perguntas em pt não ajudaram e custaram +10% de tokens).

Afinação (só no ajuste, 2026-10-01, duas passadas de 30 requisições):
- 1ª passada: `opt_out` exigia "for good" na INSTRUÇÃO e hesitou em pedido explícito ("para de me mandar
  mensagem" 0,76; "pode parar" 0,72) — o cliente não escreve "para sempre" (limite #1, literal). A 2ª passada
  tirou "for good" da instrução e deixou "sem data de retomada" no critério: 0,80 e 0,87.
- `temporary_pause` leu "se um dia eu precisar eu procuro" como condição de retomada (0,82): o `false` passou a
  dizer que a porta aberta do lado do CLIENTE não é pausa (LEIA-ME) → 0,46.
- `lgpd_request` ficou em 0,24–0,26 em "tirem meu número da lista" (lido como exclusão): o `false` ganhou a
  frase do LEIA-ME ("tirar da lista / remover meu número é opt-out, não exclusão") → 0,19–0,21. A Choice
  continua dizendo `deletion` (0,60–0,68) nesses dois casos: é o Noul que segura.
- `stop_without_object` deu 0,60 para "para" sozinho (em português, também preposição) e 0,77 em "não tenho
  mais interesse": a instrução passou a dizer que a mensagem é em português e a citar as palavras → 0,96–0,97
  nos dois nulos e ≤ 0,16 no resto.
Nenhuma pergunta foi alargada para consertar um caso: as quatro mudanças escrevem regra que já estava no LEIA-ME.
"""

# Opção da Choice → rótulo do gabarito (dados em pt). `none` é a válvula: sem ela a Choice daria um "tipo" a
# qualquer mensagem.
TIPO_DA_OPCAO = {"deletion": "exclusao", "data_source": "origem_dos_dados", "access": "acesso",
                 "correction": "correcao", "none": None}


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


# State: {"message": "<texto do cliente>"} — as perguntas apontam `message` entre crases.
PERGUNTAS = {
    "opt_out": _noul(
        "The person who wrote `message` asks the company to stop sending messages to, or calling, the phone "
        "number they are writing from.",
        "They ask to stop receiving messages or calls, to be taken off the list, or to have this number removed "
        "or unsubscribed, and name no date or condition for the company to come back. It still counts when the "
        "number belongs to a relative and they ask to remove this "
        "number, when they add 'if I ever need it I will look for you', when the request comes after sarcasm "
        "or inside a long complaint, or when it is about one kind of mass mailing (launch announcements, "
        "promotions).",
        "They do not ask for contact to stop: they say it is not necessary to stop or to remove them; "
        "ask to be contacted later (next month, after a date, when something happens); only choose a channel or "
        "a time of day (messages instead of calls); ask to stop receiving one kind of property (a filter, such "
        "as price or size); reject one property; say only that they are no longer interested, or complain, "
        "without asking to stop; say only 'stop' or 'I don't want it anymore' without saying what; or report "
        "that another person does not want messages on that other person's number.",
    ),
    "temporary_pause": _noul(
        "The person who wrote `message` asks not to be contacted for now, and gives a time or a condition for "
        "contact to resume later.",
        "They say 'not now' or 'for the time being' and point to a later moment or condition: next month, next "
        "year, after a holiday or a trip, 'when the financing is approved I will let you know'.",
        "No pause is asked: they ask to stop with no date for the company to come back, even if they add that "
        "they will look for the company themselves if they ever need it; keep talking about properties now; "
        "only schedule a visit for a later date; say they are travelling but messages can continue; only "
        "choose a channel or a time of day; or say they are no longer interested without naming a later moment.",
    ),
    "lgpd_request": _noul(
        "The person who wrote `message` exercises a data-protection right over their own personal data held by "
        "the company: asks to delete the data or close their registration, asks what data the company holds "
        "about them, asks where the company got their contact from, or asks to correct or update a personal "
        "detail in the company's records.",
        "They ask to delete or erase their data, registration, tax ID or history; ask what data is stored, for "
        "how long or with whom it is shared; ask who gave the company their number or how it got their contact "
        "(even out of curiosity, even without asking for deletion); or ask to fix or update their name, phone "
        "or another personal detail in the registration or in a document.",
        "None of these: they only ask to stop messages, to be removed from the mailing list or to have their "
        "number taken off the list (that is not deletion of data); ask to be called on another number just this once; say their data does NOT need to "
        "be deleted; mention their registration while showing interest ('you still have my registration? use "
        "it'); say they are not the person the company is looking for; or talk about properties, visits, "
        "prices or contact preferences.",
    ),
    "lgpd_type": {
        "type": "choice",
        "instructions": {
            "question": "Which data-protection request does the person who wrote `message` make about their own "
                        "personal data held by the company?",
            "precedence": "If the message makes two of these requests, choose the first that applies in this "
                          "order: deletion, data_source, access, correction.",
        },
        "criteria": {
            "deletion": {"what": "Asks the company to delete, erase or exclude their data, tax ID or history, or to "
                                 "cancel or close their registration",
                         "not_for": "Only asking to stop messages, to be removed from a mailing list or to have their "
                                    "number taken off the list; saying the data need not be deleted",
                         "examples": ["Delete everything you have about me", "Please close my registration"]},
            "data_source": {"what": "Asks where the company got their contact or data, who passed on their number, "
                                    "or what legal basis the company had to collect it",
                            "not_for": "Asking what data is stored now; asking to delete it",
                            "examples": ["How did you get my number?", "Did you buy my contact from a list?"]},
            "access": {"what": "Asks what personal data the company holds about them, for how long it is kept, or "
                               "with whom it is shared",
                       "not_for": "Asking where the contact came from; asking about a property or a visit",
                       "examples": ["What information do you have about me?", "Do you share my data with banks?"]},
            "correction": {"what": "Asks to correct or update a personal detail (name, phone, e-mail, address) in "
                                   "the company's registration or in a document",
                           "not_for": "Asking to be called on another number just this once; correcting a detail "
                                      "of a property or of a visit",
                           "examples": ["My surname is misspelled in your records", "I moved, update my address"]},
            "none": {"what": "The message makes no request about their personal data: it is about properties, "
                             "visits, interest, stopping or pausing messages, or anything else",
                     "not_for": "Any of the four requests above, even when informal or indirect",
                     "examples": ["Stop sending me messages", "Is the house still available?"]},
        },
    },
    "wants_contact_to_continue": _noul(
        "The person who wrote `message` says the company may or should keep sending messages to them, on the "
        "number they are writing from.",
        "They say messages can continue, that it is not necessary to stop or to take them off the list, or ask "
        "the company to send them more properties, photos or information.",
        "They do not say that: there is no statement that messages to them may continue and no request for "
        "more; or they say messages may continue to ANOTHER person (a spouse, a relative) while asking to "
        "remove their own number.",
    ),
    "stop_without_object": _noul(
        "`message` is in Brazilian Portuguese. It consists only of an order to stop or a refusal, such as "
        "'para', 'pare', 'chega' or 'não quero mais' (stop / enough / I don't want anymore), and does not say "
        "WHAT should stop or what is no longer wanted.",
        "The whole message is a bare stop word or 'I don't want anymore', possibly with a greeting or thanks, "
        "and names no object.",
        "The message says what should stop or what is no longer wanted: messages, calls, contact, receiving, "
        "the list, this number, a kind of property, one property, or interest ('I am no longer interested'); "
        "or it is not about stopping at all.",
    ),
    "about_another_contact": _noul(
        "`message` reports that ANOTHER person does not want to receive the company's messages on that other "
        "person's own phone number, and does not ask to remove the number the message was sent from.",
        "The writer passes on that someone else (mother, spouse, friend) does not want messages on that "
        "person's number, while the writer's own number is not asked to be removed.",
        "The writer asks to remove the number they are writing from (even when it belongs to a relative: 'this "
        "number is my mother's, take it off'), asks to stop for themselves, or the message has no request to "
        "stop at all.",
    ),
}

NOULS = [q for q, p in PERGUNTAS.items() if p["type"] == "noul"]

# ---------------------------------------------------------------------------------------- política
# Noul em três faixas: ≤ nao → não; ≥ sim → sim; meio = dúvida. Partida 0,2–0,8 (NÚCLEO §6); afinadas SÓ no
# ajuste (2ª passada, 30 mensagens). Política ASSIMÉTRICA: perder opt-out ou pedido de titular é infração, então
# o `nao` fica colado no grupo dos falsos (não no meio do vão) e toda dúvida vira `revisar`, nunca `seguir`.
FAIXA = {
    # Ajuste: opt-out explícito 0,80–0,96 (um a 0,40: "esse número é da minha mãe… pode tirar" → revisar);
    # falsos ≤ 0,16; os dois nulos 0,07 e 0,33. Vão 0,16–0,40; `nao` em 0,2, não no meio (0,28).
    "opt_out": (0.2, 0.7),
    # Ajuste: pausas 0,72–0,95; falsos ≤ 0,21 (e 0,46 num opt-out, que tem precedência). Pausar × seguir é erro
    # barato dos dois lados → faixa estreita.
    "temporary_pause": (0.4, 0.6),
    # Ajuste: pedidos reais 0,91–0,99; falsos ≤ 0,11, salvo "tirar o número" (0,19 e 0,21).
    "lgpd_request": (0.3, 0.7),
    # Guardas: só o `sim` é consumido (o `nao` existe para a função de faixa).
    # Veto do bloqueio e sinal da exclusão parcial (os dois só movem para `revisar`; nunca liberam envio sozinhos).
    # Ajuste: 0,77–0,93 em quem diz "pode mandar"; não mudou nenhuma decisão do ajuste — fica ligado por desenho
    # (exceção do LEIA-ME), como segunda leitura do lado caro.
    "wants_contact_to_continue": (0.2, 0.7),
    # Ajuste: nulos 0,96 e 0,97; resto ≤ 0,16. `sim` baixo de propósito: "para" sem objeto que saísse `seguir`
    # pode ser um opt-out perdido.
    "stop_without_object": (0.2, 0.5),
    # Veto do bloqueio. Ajuste: 0,88 no recado sobre o número da mãe; 0,48 quando o número DESTE canal é da mãe;
    # resto ≤ 0,10. Não mudou nenhuma decisão do ajuste — ligado por desenho.
    "about_another_contact": (0.2, 0.7),
}
# Tipo LGPD: abaixo deste piso de confiança da Choice (ou vencedor `none` com o Noul dizendo sim) o pedido vai a
# `revisar` — o encarregado decide o tipo. Piso global das notas (NÚCLEO §6).
TIPO_CONF_MIN = 0.5
# Faixa validada: os dados têm mensagens de até ~300 caracteres. Acima do teto a mensagem NÃO vai ao Jev:
# `revisar`, motivo "mensagem longa" (família do achado 6 do imovel-errado). Não é limiar afinado.
TETO_CARACTERES = 2000

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado em 2026-10-01, antes de abrir `dados/teste.json`. Denominadores pela tabela do LEIA-ME (teste: 60
# mensagens, 28 sem opt-out nem LGPD). "≤ 2%" de bloqueio indevido não é mensurável com n = 28 (só admitiria
# zero): o teto é 1 caso.
CRITERIO_CONTINUAR = {
    "onde": "no teste (60 mensagens), com a política acima",
    "1_infracao": "opt-out ou pedido LGPD real que saiu `seguir` = 0",
    "2_obrigacao_pela_metade": "opt-out real → `pausar`, pedido LGPD real sem pedido aberto, ou pedido aberto sem bloqueio ≤ 1",
    "3_bloqueio_indevido": "mensagem sem opt-out nem LGPD com envio bloqueado ≤ 1/28 (3,6%)",
    "4_acerto_acao": "ação (5 classes) ≥ baseline + 0,15",
    "secundario_nao_decide": "`opt_out` nulo → `revisar`; revisou sem necessidade ≤ 15% dos decidíveis; tipo LGPD certo ≥ 85% dos pedidos reais",
    "se_falhar": "1, 2 ou 3 falhando = o desenho não serve como guarda de entrada sem mudança; 4 falhando = a lista de expressões basta",
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"infracao_max": 0, "metade_max": 1, "bloqueio_indevido_max": 1, "margem_acao": 0.15,
                "revisou_sem_necessidade_max": 0.15, "tipo_certo_min": 0.85},
}

# ---------------------------------------------------------------------------------------- baseline de código
# Lista de expressões (sem acento, minúsculas) — o que um dev escreveria em meia hora. Precedência no código:
# LGPD > opt-out > pausa > seguir; o baseline não tem `revisar` (regex não sabe que não sabe).
BASELINE_LGPD = {
    "exclusao": [r"\bapag\w+", r"\bexclu\w+", r"\b(encerr|cancel)\w+ (o )?meu cadastro", r"\blgpd\b"],
    "origem_dos_dados": [r"\bquem (te |lhe )?pass\w+", r"\bde onde\b",
                         r"\bcomo (voces |vcs )?(tem|conseguiram|pegaram) (o )?meu"],
    "acesso": [r"\bquais (dados|informacoes)", r"\bo que (voces|vcs) (tem|sabem|guardam)", r"\bmeus dados\b"],
    "correcao": [r"\bcorrig\w+", r"\batualiz\w+", r"\b(ta|esta) errado\b"],
}
BASELINE_OPT_OUT = [r"\bpar(a|e|em) de\b", r"\b(pode|podem) parar\b", r"^par(a|e|em)\W*$", r"\bnao quero mais\b",
                    r"\b(sair|tir\w+|remov\w+) .{0,20}\blista\b", r"\bdescadastr\w+", r"\bnao me (mand|lig|envi)\w+",
                    r"\b(remov|tir)\w+ (o )?meu numero", r"\bchega de\b", r"\bspam\b"]
BASELINE_PAUSA = [r"\b(mes|ano|semana) que vem\b", r"\bdepois d[eoa]\b", r"\bpor enquanto\b", r"\bagora nao\b",
                  r"\bmais pra frente\b", r"\bquando .{0,40}\b(aviso|chamo|procuro)\b"]
