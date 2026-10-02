"""Perguntas, limiares, glosas e baseline da conferência de promessas — o ÚNICO arquivo que um humano revisa.

O Jev só julga a RELAÇÃO afirmação × ficha (`supported` / `contradicted` / `not_stated`). O que é número
(quartos, vagas, área, preço, condomínio, distância ao metrô) é comparado pelo CÓDIGO em `conferir.py`:
o Jev não compara números (limite #2) e a regra é exata. Uma afirmação com número E mais alguma coisa
("2 vagas cobertas") é composta: o número é do código, o resto vai ao Jev.

Desenho: UMA requisição por ficha, com uma Choice por afirmação apontando `claims[i]` entre crases
(state compartilhado: as perguntas são isoladas, então agrupar não muda a resposta e divide o custo do
state). Perguntas em inglês sobre texto em pt-BR (medido em 2026-09-30: a língua do texto não muda o
acerto; perguntas em pt custam +10% de tokens). As regras de cada opção são as decisões de rotulagem do
`dados/LEIA-ME.md` (escritas antes dos casos), não casos do ajuste.
"""

RELACOES = ("supported", "contradicted", "not_stated")

# ---------------------------------------------------------------- state: campos da ficha em inglês
# O nome do campo vai ao modelo, e a pergunta é em inglês; o código traduz chave e valor de enum.
CAMPO_EN = {
    "quartos": "bedrooms", "vagas": "parking_spots", "area_m2": "area_m2", "orientacao_solar": "facing",
    "aceita_pet": "pets_allowed", "financiamento": "financing", "distancia_metro_m": "metro_distance_m",
    "condominio_reais": "condo_fee_brl", "mobiliado": "furnished",
}
FINANCIAMENTO_EN = {"aceita": "accepted", "proprietario_analisa": "owner evaluates case by case",
                    "nao_aceita": "not accepted"}
# Tabela de orientação solar do LEIA-ME (hemisfério sul, decidida como corretor experiente). É
# conhecimento de mundo fixo: fica no CÓDIGO, que expande o enum na própria ficha; o Jev só compara.
ORIENTACAO_EN = {
    "leste": "east (morning sun; no afternoon sun)",
    "oeste": "west (afternoon sun; no morning sun)",
    "norte": "north (sun during most of the day; the listing does not say morning-only or afternoon-only)",
    "sul": "south (little direct sun)",
}

# ---------------------------------------------------------------- a Choice (uma por afirmação)
# `{i}` = índice da afirmação em `claims`. Opções contrastivas com `what`/`not_for`/`examples`; os
# exemplos vêm das regras do LEIA-ME (exagero = not_stated; oposto = contradicted; paráfrase = supported).
_INSTRUCAO = {
    "question": "How does the listing in `listing` relate to the statement in `claims[{i}]`?",
    "context": "`listing` is the public record of a property: title and description in Brazilian Portuguese "
               "plus structured fields. `claims[{i}]` is one sentence from a draft reply an agent wants to "
               "send to a customer about this property.",
    "rules": "Judge only what the listing says, not what is plausible. A stronger, broader or unconditional "
             "version of what the listing says is not_stated, not supported: a possibility or a condition in "
             "the listing ('owner evaluates', 'small pets only', 'subject to approval', 'semi-furnished') does "
             "not support a guarantee, an approval or the unconditional claim. Saying the same thing in other "
             "words is supported. Stating the opposite, or what a condition in the listing excludes, is "
             "contradicted.",
}
_OPCOES = {
    "supported": {
        "what": "The listing states the same fact, literally or in other words that a real-estate agent would "
                "accept as strictly equivalent, or the statement respects a condition the listing sets",
        "not_for": "A stronger, broader or unconditional version of what the listing says; a guarantee built on "
                   "a possibility; a fact the listing never mentions",
        "examples": ["listing 'entregue sem mobília' → 'não vem mobiliado'",
                     "listing 'pets de até 10 kg' → 'aceita gato'",
                     "listing 'pronto para morar' → 'não precisa de reforma'",
                     "listing 'proprietário analisa financiamento' → 'pode aceitar financiamento, a confirmar'"],
    },
    "contradicted": {
        "what": "The listing states the opposite or something incompatible: an explicit negation, a mutually "
                "exclusive attribute, or a condition that excludes what the statement says",
        "not_for": "The listing merely does not mention it, or supports only a weaker version of it",
        "examples": ["listing 'não aceita animais' → 'aceita pet'",
                     "listing 'vaga rotativa' → 'vaga privativa'",
                     "listing 'pets de até 10 kg' → 'aceita cão grande'",
                     "listing 'precisa de reforma' → 'pronto para morar'",
                     "listing 'proprietário analisa financiamento' → 'não aceita financiamento'"],
    },
    "not_stated": {
        "what": "The listing says nothing about it, or supports only a weaker version: the statement adds a "
                "guarantee, an approval, a scope, a detail or an opinion the listing does not give",
        "not_for": "A fact the listing states in other words; a fact the listing explicitly denies or excludes",
        "examples": ["listing 'proprietário analisa financiamento' → 'financiamento aprovado'",
                     "listing 'semimobiliado' → 'mobiliado'",
                     "listing 'pets: consultar' → 'aceita pet'",
                     "listing 'aceita pets de pequeno porte' → 'aceita pet'",
                     "'ótima localização' (opinion)",
                     "'tem piscina' when the listing never mentions a pool"],
    },
}


def choice(i: int) -> dict:
    return {"type": "choice", "instructions": {k: v.format(i=i) for k, v in _INSTRUCAO.items()}, "criteria": _OPCOES}


# ---------------------------------------------------------------- Noul auxiliar (medido no ajuste)
# "A ficha trata do assunto?" — ideia: `supported` com assunto ausente vira `not_stated` (pega o Jev
# sustentando por plausibilidade). Só entra no desenho se o ajuste mostrar ganho.
def noul_topico(i: int) -> dict:
    return {
        "type": "noul",
        "instructions": f"Does `listing` (title, description or fields) explicitly address the subject of "
                        f"`claims[{i}]` — the same attribute, feature or condition — whether or not it agrees "
                        f"with the statement?",
        "criteria": {
            "true": "The listing mentions that attribute or feature (pets, parking, furniture, financing, sun, "
                    "distance to the metro, a pool, a fee...), agreeing or disagreeing with the statement",
            "false": "The listing says nothing about that subject, or the statement is a pure opinion",
        },
    }


TOPICO_MAX = 0.3  # com o Noul ligado: `supported` com tópico ≤ isto → `not_stated`

DESENHOS = ("choice", "choice+topico")
# Ajuste 2026-10-01 (30 fichas, 104 afirmações, 71 no Jev): os dois desenhos acertam 100/104 (0,962) com 0
# promessa inventada mantida; o Noul de tópico NUNCA agiu (onde o tópico ficou ≤ 0,3 a Choice já dizia
# not_stated) e custa +13% de tokens (2.101 → 2.377 por ficha). Sem ganho, fica fora.
DESENHO_PADRAO = "choice"

# ---------------------------------------------------------------- limiares (ação por afirmação)
# Choice `confidence` (não a probabilidade do vencedor). Três ações:
#   supported  com conf ≥ CONF_MANTER  → manter
#   contradicted / not_stated com conf ≥ CONF_RETIRAR → retirar
#   o resto → revisar (humano)
# Assimétrico de propósito: MANTER uma promessa inventada é o erro caro (o cliente lê), então manter exige
# mais certeza que retirar. Veredito do código (número) não tem confiança: age direto.
# Ajuste 2026-10-01: erro caro 0/48 em toda a grade (de 0/0 a 0,9/0,9). Os 7 julgamentos do Jev com conf
# < 0,7 estão todos CERTOS (condição e possibilidade×garantia, 0,28–0,55): no ajuste a faixa custa cobertura
# (0,90) sem comprar acerto. O único erro decidido (fato certo com adjetivo "barato", not_stated 0,54) retira
# um fato verdadeiro — erro barato. 0,7/0,5 fica pelo RISCO da ação, não por um caso (lição da triagem).
CONF_MANTER = 0.7
CONF_RETIRAR = 0.5

# ---------------------------------------------------------------- baseline de código
# O que um dev faria em 20 minutos sem modelo: número → mesma comparação do código; palavra de promessa
# → `not_stated`; atributo booleano da ficha (pet, mobiliado, financiamento) → igualdade com negação;
# senão, palavras da afirmação presentes na ficha (≥ metade, prefixo de 5 letras) → `supported`.
BASELINE_PROMESSA = ("garantid", "aprovad", "todos", "todas", "sempre", "qualquer", "com certeza", "certeza",
                     "ja esta", "ja foi", "o dia inteiro", "completo")
BASELINE_FRACAO = 0.5
BASELINE_STOP = {"o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "e", "é",
                 "tem", "fica", "vem", "esta", "sao", "ha", "com", "sem", "nao", "para", "que", "imovel",
                 "apartamento", "casa", "predio", "condominio", "ser", "ter", "pra"}

# ---------------------------------------------------------------- critério de continuar / descartar
# Fixado ANTES de abrir o teste (2026-10-01), a partir do ajuste. Falhar um item = o desenho não serve
# como está; o teste não se repete para consertar. Dicionário (não prosa) porque entra no manifesto
# `congelamento.json`: o critério congela junto com o código (mesmo texto da rodada 1, só mudou a forma).
CRITERIO_CONTINUAR = {
    "onde": "no teste, com o desenho padrão e os limiares acima",
    "1_numericas_puras": "pelo código 100% (menos é bug)",
    "2_acerto_relacao": "código + Jev, resposta dura, ≥ baseline + 15 p.p.",
    "3_promessa_inventada": "gabarito contradicted/not_stated → manter ≤ 3% dessas afirmações",
    "4_cobertura": "manter ou retirar sem humano ≥ 75%",
}
