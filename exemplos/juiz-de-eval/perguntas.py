"""Pergunta, limiares e baseline do juiz de eval — o ÚNICO arquivo que um humano precisa revisar.

O Jev só vê critérios SEMÂNTICOS. Os FORMAIS (contar frases, R$, horário, link, palavra, emoji,
tamanho, termina com "?") são regra de código em `juiz.py` e nunca viram pergunta: o Jev não conta
nem compara (limites #2 e #3) e a regra é exata — pedir ao modelo seria pagar para errar.

Uma pergunta só (um Noul por critério: "a resposta atende o critério, como escrito?"), em dois
DESENHOS de state, medidos no ajuste (o teste roda o escolhido em `DESENHO_PADRAO`):
  "um_por_requisicao" — state {question, answer, criterion}; 1 Noul; 1 requisição por critério.
  "agrupado"          — state {question, answer, criteria: [...]}; 1 Noul por critério apontando
                        `criteria[i]` entre crases; 1 requisição por RESPOSTA (state compartilhado:
                        mais barato, mas o Noul precisa achar o item certo — indireção, limite #4).
Perguntas em inglês sobre texto em pt-BR (medido em 2026-09-30: a língua do texto não muda o acerto;
perguntas em pt custam +10% de tokens). As regras de `true`/`false` são as decisões de rotulagem do
`dados/LEIA-ME.md` (escritas antes dos casos), não casos do ajuste.
"""

# ---------------------------------------------------------------- a pergunta (um Noul por critério)
# `{ref}` = caminho do critério no state, entre crases. Alto = sim = atende.
_INSTRUCAO = (
    "`answer` is what an attendant replied to the customer or user message in `question` (texts in "
    "Brazilian Portuguese). When `question` starts with 'Contexto:', that part is the record the attendant "
    "had; the message itself comes after 'Cliente:' or 'Usuário:'. "
    "Does `answer` satisfy the criterion written in {ref}, taken as written?"
)
_TRUE = (
    "The answer does what the criterion says: explicitly, in other words, or plainly implied by what it "
    "states (e.g. 'the building rules do not allow animals' informs that pets are not accepted; 'I will check "
    "with the owner and confirm' informs that a visit needs prior scheduling). For a criterion written as "
    "'Não ...' (does not ...), true when the forbidden thing is absent from the answer."
)
_FALSE = (
    "The answer does not mention what the criterion asks for; states the opposite; touches it only vaguely "
    "without actually doing it (e.g. 'in the settings' for 'indicates the path'); repeats the question or "
    "answers a different one; or would satisfy it only if the reader assumed something the answer does not "
    "say. For a 'Não ...' criterion, false when the forbidden thing appears, even softened or wrapped in "
    "courtesy. For 'Não inventa ...' (does not make up), false when the answer asserts any fact about the "
    "property or product that the 'Contexto:' does not support, including plausible guesses."
)


def noul(ref: str) -> dict:
    """Noul no formato JSON da API, apontando o critério em `ref` (ex.: "`criterion`" ou "`criteria[2]`")."""
    return {"type": "noul", "instructions": _INSTRUCAO.format(ref=ref), "criteria": {"true": _TRUE, "false": _FALSE}}


DESENHOS = ("um_por_requisicao", "agrupado")
# Ajuste 2026-10-01 (55 critérios semânticos): os dois desenhos acertaram 54/55 (o mesmo caso errado,
# "responde outra pergunta", 0,52 × 0,54) e 0 erro com faixa; o agrupado custa 24% menos (US$ 39 × 52
# por milhão de respostas) e põe os 3 gabaritos nulos na faixa do meio (2/3 no outro). A indireção de
# `criteria[i]` (limite #4) não apareceu com 2–4 critérios por resposta.
DESENHO_PADRAO = "agrupado"

# ---------------------------------------------------------------- limiares (três faixas por critério)
# noul ≤ NAO → nao_atende; noul ≥ SIM → atende; meio → revisa (humano). Assimétrica de propósito:
# aprovar critério não atendido é o erro caro (aprova resposta ruim), então `atende` exige mais certeza
# que `nao_atende`. Ajuste 2026-10-01: de 0,3/0,7 a 0,1/0,9 todas zeram o erro entre decididos (o único
# erro duro fica em 0,52–0,54); 0,3/0,8 cobre 94,5% com 3 revisões — escolha pelo risco, não por um caso.
# Aviso da triagem: o ajuste tem quase tudo perto de 0 ou 1; a faixa só é posta à prova no teste.
FAIXA = (0.3, 0.8)

# ---------------------------------------------------------------- baseline de código (só semânticos)
# "Palavras-chave do critério presentes na resposta": conteúdo do critério (sem stopwords e sem os
# verbos de rubrica) casado por prefixo de 5 letras, sem acento; ≥ metade presente = menciona.
# Critério negado ("Não promete desconto") inverte: atende quando NÃO menciona. É o que um dev faria
# em 20 minutos sem modelo — e é o piso que o Jev precisa superar.
BASELINE_FRACAO = 0.5
BASELINE_STOP = {
    "que", "não", "nao", "para", "com", "uma", "sem", "como", "onde", "pelo", "pela", "seja", "são", "sao",
    "está", "esta", "esteja", "tem", "ter", "ser", "faz", "feita", "feito", "num", "numa", "dos", "das",
    "ou", "e", "o", "a", "os", "as", "de", "do", "da", "em", "no", "na", "se", "ao", "à", "por", "um",
    # verbos e substantivos de rubrica: dizem o que a resposta deve FAZER, não o conteúdo
    "informa", "responde", "menciona", "explica", "indica", "oferece", "convida", "confirma", "especifica",
    "pede", "promete", "garante", "culpa", "inventa", "afirma", "contém", "contem", "resposta", "pergunta",
    "critério", "criterio", "contexto", "tom", "forma", "base",
}

# ---------------------------------------------------------------- critério de continuar / descartar
# Fixado ANTES de abrir o teste (2026-10-01), a partir do ajuste. Falhar um item = o desenho não serve
# como está; o teste não se repete para consertar.
# Dicionário (não prosa) porque entra no manifesto `congelamento.json`: o critério congela junto com o código.
CRITERIO_CONTINUAR = {
    "onde": "no teste, com o desenho padrão e a FAIXA acima",
    "1_formais": "100% (menos é bug de código)",
    "2_semantico_duro": "acerto duro (noul ≥ 0,5, gabarito não nulo) ≥ baseline + 15 p.p.",
    "3_erro_caro": "≤ 5% dos critérios semânticos com gabarito false (gabarito false → `atende`)",
    "4_resposta_ruim_aprovada": "nenhuma resposta com algum critério false aprovada inteira (`aprovada` com gabarito reprovada)",
}
