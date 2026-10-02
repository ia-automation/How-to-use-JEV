"""Perguntas, faixas e política do "imóvel errado" — o ÚNICO arquivo que um humano precisa revisar.

Uma conversa (cliente × agente), os candidatos discutidos (na ordem em que foram apresentados) e o rascunho
de resposta viram UM state e UMA requisição ao Jev com 4 perguntas. O Jev julga; `referente.py` decide a
ação (manter / trocar_referente / pedir_esclarecimento) com os números daqui. Mudar política = editar
número, sem chamar a API de novo.

Desenho:
- `referent` (Choice): uma opção por candidato (chave = ID, descrição = resumo + posição de apresentação)
  + a válvula `not_enough_information`. Choice é RELATIVA (sempre há vencedor): sem a válvula, "o que aceita
  pet" com dois que aceitam ganharia um vencedor por acaso.
- `unambiguous_reference` (Noul, absoluto): segunda leitura do "não dá para saber", medida no ajuste como
  portão extra sobre a Choice (NÚCLEO §6: a confiança da Choice não denuncia empate de intenções).
- `draft_uses_other` (Noul, relacional): o rascunho usa fato de OUTRO candidato que não o referente. É
  relacional por natureza (o gabarito é "fato de outro atribuído ao referente"; nomear cada candidato com o
  fato certo NÃO conta) — decompor em "fato de cada candidato" perderia justamente essa distinção.
- `draft_commits_to_one` (Noul, absoluto): o rascunho responde como se UM candidato fosse o referente. Serve
  ao caso de referente nulo (LEIA-ME: aí `rascunho_usa_outro` = "se compromete com um" ou mistura; pedir
  esclarecimento, responder genérico ou comparar nomeando cada um = false). Um Noul só, em vez de um por
  candidato: a pergunta é "se compromete com algum", não "com qual".

O que fica no código: filtrar/ordenar candidatos, mapear a resposta ao ID, limiares, ação, sugestão do
candidato certo (nunca reescreve o rascunho), baseline por palavra-chave, e — desde a revisão de 2026-10-01
(achado 5) — os COMPARATIVOS numéricos: o código extrai preço, área, quartos e vagas do resumo de cada
candidato e põe no state `comparatives` (cheapest, most_expensive, largest, smallest, most_bedrooms,
most_parking; só quando todos têm o valor e não há empate). "O mais barato" deixa de ser uma comparação de
720 × 740 entregue ao Jev: é um fato pronto que a instrução manda consultar. Perguntas em inglês sobre dados
em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram). Faixas de partida 0,3–0,7 e piso 0,5 na Choice,
afinados SÓ no conjunto de ajuste (uma passada: a 1ª versão já acertou os 24; a 2ª, que explicitava a
resposta sim/não no `draft_uses_other`, não moveu nada e foi revertida).
"""

NEI = "not_enough_information"  # válvula da Choice; o código traduz para referente nulo
ORDINAIS = ["first", "second", "third", "fourth"]  # "o primeiro" = candidates[0] (LEIA-ME)
MIN_CANDIDATOS, MAX_CANDIDATOS = 2, 4  # LEIA-ME: 2–4 candidatos; fora disso é erro antes da chamada (achado 2)
# Teto da conversa (achado 6): acima disto a conversa NÃO vai ao Jev — a ação é `pedir_esclarecimento` com motivo
# "conversa longa", contada à parte. Os dados têm 3–10 turnos (LEIA-ME) e no máximo ~300 caracteres de conversa,
# então o teto não dispara em nenhum caso medido: é a faixa validada de funcionamento, não um limiar afinado.
TETO_TURNOS = 12
TETO_CARACTERES = 3000


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


def choice_referente(candidatos: list[dict]) -> dict:
    """Choice montada por conversa: as opções SÃO os candidatos (receita "extração pré-parseada": o valor
    devolvido é sempre um ID que existe). Descrição = posição + resumo, porque o cliente diz "o primeiro"
    e "o de 720", nunca o ID."""
    opcoes = {c["id"]: f"Presented {ORDINAIS[i]}: {c['summary']}" for i, c in enumerate(candidatos)}
    opcoes[NEI] = ("The last customer message does not single out one candidate: it fits two or more of "
                   "them, is about all or none of them, or refers to something the conversation never identifies.")
    return {
        "type": "choice",
        "instructions": {
            "question": "Which property in `candidates` is the LAST customer message in `conversation` about?",
            # Regras do LEIA-ME §"Como o referente é resolvido", na ordem de precedência, em linguagem literal.
            "how_to_resolve": (
                "Read the whole conversation as an experienced broker would. `candidates` are listed in the "
                "order they were presented ('the first one' is the first in the list). A correction by the "
                "customer ('no, the first one', 'actually I mean the other one') overrides everything before "
                "it. A name or an attribute that only one candidate has (neighbourhood, price, size, 'the one "
                "with a pool') identifies that candidate even if another one was in focus. A comparison ('the "
                "cheaper one', 'the bigger one', 'the one with more bedrooms / parking spaces') is already "
                "resolved in `comparatives`: use the candidate id given there (cheapest, most_expensive, largest, "
                "smallest, most_bedrooms, most_parking); a comparison that is not in `comparatives` has no "
                "single answer. "
                "When the customer quotes something the agent said ('you said the one with the balcony "
                "accepts pets'), the referent is the property the agent was describing in that statement. "
                "'The other one' with two candidates is the one not in focus; with more candidates it is the "
                "only one not yet discussed. A pronoun ('it', 'that one') or a question with no new mark keeps "
                "the candidate that was in focus in the previous turn. A candidate the customer has discarded "
                "is out of play."
            ),
            "when_not_enough_information": (
                "Choose not_enough_information when the message fits two or more candidates still in play "
                "(an attribute they share, 'the other one' with more than one candidate not yet discussed), "
                "when it asks about both or all of them at once, when it is about none of them (a general "
                "question, or a property that is not in the list such as 'the one we visited yesterday'), or "
                "when the conversation does not say which one it is."
            ),
        },
        "criteria": opcoes,
    }


# State: {"conversation": [{"from": "customer"|"agent", "text"}], "candidates": [{"id", "summary"}], "draft",
#         "comparatives": {"cheapest": id, ...}} — `comparatives` é calculado pelo código (referente.comparativos).
# As perguntas apontam os campos entre crases (limite #4: nomear a parte do state).
NOULS = {
    "unambiguous_reference": _noul(
        "The LAST customer message in `conversation`, read with the whole conversation, points to exactly one "
        "of the properties in `candidates`.",
        "One candidate is identified: by its name or neighbourhood, by an attribute only it has, by a "
        "correction ('no, the first one'), by 'the other one' when only one other candidate is in play, or by "
        "continuity with the candidate that was in focus in the previous turn.",
        "The message fits two or more candidates (an attribute they share; 'the other one' with several not "
        "yet discussed), asks about all of them or about none of them, or refers to a property the "
        "conversation never identifies ('the one we visited yesterday').",
    ),
    "draft_uses_other": _noul(
        "`draft` is the agent's reply to the last customer message. It states at least one fact (price, "
        "rooms, neighbourhood, parking, pets, condo fee, size, distance, furniture, elevator, financing, "
        "balcony...) that, according to the summaries in `candidates`, belongs to a candidate OTHER than the "
        "property the customer is asking about, presenting it as a fact of that property.",
        "At least one fact in the draft comes from another candidate's summary and is given as the answer "
        "about the property the customer means, or facts of two candidates are mixed as if they were one "
        "property, even if the draft names the right property.",
        "Every fact in the draft is a fact of the property the customer means; or the draft states no fact "
        "from any candidate (it asks which one, or says it will check); or it names each candidate separately "
        "with that candidate's own facts, as a comparison.",
    ),
    "draft_commits_to_one": _noul(
        "`draft` answers as if ONE specific candidate in `candidates` were the property the customer means: "
        "it names that candidate as the subject, or states facts that, by the summaries, are facts of that "
        "candidate.",
        "The draft answers about one candidate (named, or recognisable by its facts) as the property in "
        "question, or mixes facts of candidates into a single answer about one property.",
        "The draft asks the customer which property they mean, answers without any fact from the candidate "
        "summaries, or names each candidate side by side with that candidate's own facts.",
    ),
}


def perguntas(candidatos: list[dict]) -> dict:
    """Todas as perguntas de uma conversa, na mesma requisição (fan-out: mesmo state, isoladas)."""
    return {"referent": choice_referente(candidatos), **NOULS}


# ---------------------------------------------------------------------------------------- política
# Choice: abaixo do piso de confiança, o referente é tratado como desconhecido → pedir esclarecimento.
# Piso 0,5 = piso global das notas (NÚCLEO §6); afinado pela curva cobertura × erro do ajuste.
REFERENTE_CONF_MIN = 0.5
# Portão extra sobre a Choice: `unambiguous_reference` ≤ este valor = referência ambígua mesmo que a Choice tenha
# vencedor. None desliga o portão. Ajuste 2026-10-01: nunca mudou uma decisão — a Choice mandou os 4 nulos
# para a válvula e o Noul concordou (0,05–0,22); nos 20 não nulos ficou ≥ 0,91. Fica ligado por desenho: duas
# leituras independentes do "não dá para saber" (limite #8: identidades entre perguntas não valem).
UNAMBIGUOUS_MIN = 0.3
# Nouls do rascunho em três faixas: ≤ nao → não; ≥ sim → sim; meio = dúvida. Dúvida sobre o rascunho com
# referente conhecido vira `trocar_referente` (regenerar com o candidato certo é barato; enviar fato errado é
# o erro caro). Ajuste 2026-10-01: `draft_uses_other` deu ≤ 0,11 em todo `false` e ≥ 0,60 em todo `true`; três
# `true` caíram na faixa (0,60–0,67: "Aceita sim", "É sim, mobiliado" — resposta sim/não com o fato do outro,
# sem nomear ninguém). Explicitar esse caso no critério não moveu os valores (±0,04 = ruído), então a pergunta
# ficou como estava e a faixa 0,3–0,7 com dúvida→trocar é o que segura essa família.
FAIXA = {"draft_uses_other": (0.3, 0.7), "draft_commits_to_one": (0.3, 0.7)}

# Critério de continuar/descartar — entra no manifesto `congelamento.json` (achado 1): mudar isto exige congelar de novo.
# Rodada 1 (cega, 2026-10-01 11:38): item 1 era só erro caro + troca p/ candidato errado. A revisão (achado 4) somou
# "sugeriu candidato quando o gabarito exige esclarecimento" (gabarito nulo → `manter`/`trocar_referente`): a resposta
# sobre um imóvel que o cliente não identificou também é resposta errada que iria ao cliente.
CRITERIO_CONTINUAR = {
    "onde": "no teste (48 conversas), com a política acima",
    "1_resposta_errada_ao_cliente": ("erro caro (rascunho de outro imóvel → manter) + troca sugerindo candidato errado "
                                     "+ sugeriu candidato com gabarito nulo ≤ 1/48 (2,1%)"),
    "2_acerto_referente": "nulo incluído, ≥ baseline + 0,15",
    "secundario_nao_decide": "nulos → pedir ≥ 6/8; pediu sem necessidade ≤ 10% dos não nulos",
}

# ---------------------------------------------------------------------------------------- baseline de código
# Palavras do resumo que não identificam imóvel (aparecem em qualquer anúncio). O que sobra e é único de um
# candidato (bairro, preço, metragem) vira a assinatura dele. "piscina"/"varanda" ficam fora da assinatura de
# propósito: o baseline é "último imóvel citado por NOME/preço", não por atributo — é o que o Jev acrescenta.
PALAVRAS_GENERICAS = {
    "apto", "apartamento", "casa", "sobrado", "studio", "kitnet", "quarto", "quartos", "vaga", "vagas",
    "aceita", "pet", "sem", "com", "para", "mil", "metro", "metrô", "condominio", "condomínio", "venda",
    "prédio", "predio", "porte", "pequeno", "cobertas", "coberta", "descoberta", "elevador", "lazer",
    "completo", "financiamento", "vista", "frente", "mar", "varanda", "sacada", "churrasqueira", "gourmet",
    "mobiliado", "antigo", "portaria", "piscina", "academia", "quintal", "pequena", "grande", "lateral",
}
# Bairros e cidades NÃO entram aqui: o que aparece em todos os resumos (ex.: "Barra da Tijuca" nos três)
# deixa de ser único pela regra de unicidade; o que distingue (Tijuca × Vila Isabel) precisa continuar valendo.
MIN_DIGITOS_NUMERO = 2  # "720", "72", "1,3" contam; "1 vaga"/"2 quartos" não (número de 1 dígito é genérico)
