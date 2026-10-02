"""Motivo de perda — perguntas, limiares, variante principal e critério. O arquivo que o humano revisa.

Receita-irmã: `conhecimento/receitas/classificacao-hierarquica.md` (um Choice por nó da árvore; aqui a árvore tem
2 níveis: grupo → folha). O que veio de lá está marcado [receita]; adaptação nossa, [local].

State: `{"conversation": [{"from": "customer" | "agent", "text"}], "last_customer_message", "agent_messages_after_last_customer_message"}`.
A conversa vai inteira (4–12 turnos curtos); os dois campos extras são FATOS calculados em código (lição 30 de
`licoes-transversais`): o silêncio do cliente é "mensagens do corretor sem resposta no fim", e isso é contagem, não
julgamento. Perguntas em inglês; nome e descrição de grupos e folhas ficam em português, como estão em
`dados/taxonomia.json` (são dado, não pergunta).

Quatro formatos de requisição (cada variante paga só os seus — `motivo.ETAPAS`):
  `grupo`   Choice `group` sobre os 8 grupos + os 3 Nouls de guarda                       (a, 1ª requisição)
  `folhas`  Choice `leaf` sobre as folhas do grupo vencedor + `only_group`                 (a, 2ª requisição: a
            resposta da 1ª decide as OPÇÕES da 2ª — o único motivo legítimo para outra chamada)
  `unica`   Choice `leaf` sobre as 30 folhas com descrição completa + os 3 Nouls           (b, 1 requisição)
  `tudo`    Choice `group` + uma Choice `leaf.<grupo>` por grupo (premissa explícita) + os 3 Nouls   (c, 1 requisição)

Política de `null` (só o grupo): `only_group` na Choice de folhas (a, c) ou probabilidade da folha vencedora abaixo
do limiar (b). Política de `sem_informacao`: é um GRUPO como os outros, com a válvula escrita no critério dele —
"nomear um motivo seria chute". Guardas (Nouls, regra 8 do briefing): nenhuma leitura da Choice fecha o lead com
motivo "do corretor" (`atendimento`) nem "fechou em outro lugar" (`concorrencia`) sem o Noul correspondente em sim.
"""
from __future__ import annotations

SO_GRUPO = "only_group"      # válvula da Choice de folhas; nunca é ID de folha (o código confere)
SEM_INFORMACAO = "sem_informacao"
ATENDIMENTO, CONCORRENCIA = "atendimento", "concorrencia"
TETO_CARACTERES = 6000       # conversa maior que isto não é enviada: revisar (a faixa medida é de 4–12 turnos curtos)
MAX_FOLHAS = 254             # Choice aceita ≤ 255 opções; sobra uma para a válvula
PAPEL = {"cliente": "customer", "corretor": "agent"}  # `de` do dado → papel no state (estrutura, não dado)

# ---------------------------------------------------------------------------------------- textos
# Regras de leitura do LEIA-ME (precedência do rotulador), escritas uma vez e iguais em todas as Choices. Escritas
# antes de qualquer medição; não foram mexidas na afinação (ver README).
_REGRAS = (
    "Judge only by what the `customer` says or does; the `agent`'s offers and excuses are not the customer's reason. "
    "A reason the customer confesses later beats the polite excuse given first. When the customer ranks two reasons "
    "('the price I could handle; the real problem is the distance'), take the one they rank first. An event that ends "
    "the deal (credit refused, guarantee rejected, the property sold to someone else, a visit that fell through again) "
    "beats a side complaint made along the way. The cause beats its consequence (a separation that makes the home too "
    "big and too expensive is a life change, not price). If the customer closed elsewhere AND complains about our offer "
    "or our service as the reason, the complaint is the reason; if they only praise the other option or give no "
    "reason, it is closing elsewhere. A polite postponement ('I'll think about it') right after a reaction ('way above "
    "what I had in mind') takes the reason of that reaction; with no hint anywhere, there is no information. Silence "
    "with no reaction is no information, even right after a price. Never invent a reason the conversation does not give."
)

_SEM_INFORMACAO = (
    "The conversation does not say why the deal did not happen: the customer stopped answering (with or without a "
    "price just before the silence) or postponed politely without any hint of a reason anywhere. Use this whenever "
    "naming a reason would be a guess."
)

_PERGUNTA_GRUPO = (
    "The WhatsApp conversation in `conversation` is between a real-estate agency (`agent`) and a lead (`customer`), "
    "and the deal did NOT happen. Which group of reasons best explains why the lead was lost? "
    "`agent_messages_after_last_customer_message` counts how many agent messages went unanswered at the end."
)

_PERGUNTA_UNICA = (
    "The WhatsApp conversation in `conversation` is between a real-estate agency (`agent`) and a lead (`customer`), "
    "and the deal did NOT happen. Which specific reason best explains why the lead was lost? Each option is "
    "'group › reason'. `agent_messages_after_last_customer_message` counts how many agent messages went unanswered at the end."
)

_SO_GRUPO = (
    "The conversation shows the reason is in this group but does not say which specific one — for example, the "
    "customer says the monthly total does not fit without separating the rent from the fees, or says the home was "
    "rejected without saying what was wrong with it, or says they closed elsewhere without saying through whom. "
    "Prefer this over guessing a specific reason."
)

# Guardas (Noul = sim/não absoluto). Cada uma aponta para um erro caro declarado no critério:
#   `reason_stated`    baixo com grupo ≠ sem_informacao → motivo possivelmente INVENTADO → revisar.
#   `blames_agency`    baixo com grupo `atendimento` → não fechar o lead com culpa do corretor → só grupo + revisar.
#   `closed_elsewhere` baixo com grupo `concorrencia` → não registrar "fechou em outro lugar" → só grupo + revisar.
NOULS = {
    "reason_stated": (
        "Does the `customer` state, or clearly hint at, a reason why the deal did not go forward — a complaint, a "
        "refusal, an event, a decision — as opposed to only stopping answering or postponing politely with no hint? "
        "The agent's guesses do not count."
    ),
    "blames_agency": (
        "Does the `customer` attribute the loss to the agency's or the agent's own conduct: slow or missing replies, a "
        "visit that did not happen, wrong or outdated information given by the agent, the property being sold or "
        "rented to someone else before the customer could close, or pressure and insistence?"
    ),
    "closed_elsewhere": (
        "Does the `customer` say they have ALREADY bought or rented another property, or the same property through "
        "another channel (another agency or broker, directly with an owner, a developer or a new-build launch)? "
        "'I will keep looking elsewhere' is not closing elsewhere."
    ),
}


def rotulo(no: dict) -> str:
    """Nome + descrição, como estão na taxonomia.
    @example rotulo({"nome": "Preço", "descricao": "O valor pedido não cabe."}) → "Preço: O valor pedido não cabe."
    """
    return f"{no['nome']}: {no['descricao'].strip()}"


def criterio_grupo(grupo: dict) -> str:
    """Critério de um grupo na Choice `group`: descrição + nomes das folhas (o que o grupo contém). A válvula de
    `sem_informacao` leva a política escrita."""
    if grupo["id"] == SEM_INFORMACAO:
        return f"{grupo['nome']}: {_SEM_INFORMACAO} Includes: " + "; ".join(f["nome"] for f in grupo["folhas"]) + "."
    return f"{rotulo(grupo)} Includes: " + "; ".join(f["nome"] for f in grupo["folhas"]) + "."


def choice_grupo(taxonomia: list[dict]) -> dict:
    """Choice `group` [receita: um Choice por nó; local: válvula escrita no critério de `sem_informacao`]."""
    return {
        "type": "choice",
        "instructions": {"question": _PERGUNTA_GRUPO, "rules": _REGRAS},
        "criteria": {g["id"]: criterio_grupo(g) for g in taxonomia},
    }


def choice_folhas(grupo: dict) -> dict:
    """Choice `leaf` das folhas de UM grupo, com a premissa explícita (fan-out especulativo quando vai no `tudo`).
    `only_group` entra em todo grupo menos `sem_informacao` (as três folhas dele cobrem tudo — LEIA-ME)."""
    criterios = {f["id"]: rotulo(f) for f in grupo["folhas"]}
    if grupo["id"] != SEM_INFORMACAO:
        criterios[SO_GRUPO] = _SO_GRUPO
    return {
        "type": "choice",
        "instructions": {
            "question": (f"Assume the reason the lead in `conversation` was lost belongs to the group '{grupo['nome']}' "
                         f"({grupo['descricao'].strip()}). Which specific reason in this group does the conversation show?"),
            "rules": _REGRAS,
        },
        "criteria": criterios,
    }


def choice_unica(taxonomia: list[dict]) -> dict:
    """Choice `leaf` sobre TODAS as folhas, descrição completa, na ordem da taxonomia (variante b). Sem `only_group`:
    o "só grupo" sai da probabilidade da folha vencedora, em código."""
    criterios = {}
    for g in taxonomia:
        for f in g["folhas"]:
            criterios[f["id"]] = f"{g['nome']} › {rotulo(f)}"
    return {"type": "choice", "instructions": {"question": _PERGUNTA_UNICA, "rules": _REGRAS}, "criteria": criterios}


def nouls() -> dict:
    return {k: {"type": "noul", "instructions": texto} for k, texto in NOULS.items()}


# ---------------------------------------------------------------------------------------- política
# Variantes medidas (o `run.py` compara todas nos mesmos casos; a produção roda só a principal):
#   a   duas etapas: Choice do grupo (+ guardas) → Choice das folhas do grupo vencedor (+ `only_group`).  2 requisições
#   b   uma etapa: Choice única sobre as 30 folhas (+ guardas); grupo = soma das probabilidades das folhas.  1 requisição
#   c   uma requisição: Choice do grupo + uma Choice de folhas POR grupo (premissa explícita) + guardas;
#       o código lê a Choice de folhas do grupo vencedor.                                                 1 requisição
VARIANTES = ["a", "b", "c"]

# Limiares afinados SÓ no ajuste (34 conversas). Partida: 0,5 em tudo (Noul 0,5 = "sim e não igualmente prováveis";
# Choice: a probabilidade do vencedor, não a `confidence`). O que mudou na afinação está anotado ao lado do número.
LIMIAR = {
    # probabilidade do grupo vencedor (Choice `group`, ou soma das folhas do grupo em b) < → revisar (sem folha).
    # Ajuste (a/c): p(grupo) nos 5 grupos errados 0,52–0,89 (os 2 que viraram erro: 0,72 e 0,89); nos certos, mínimo 0,48,
    # p10 0,67. Nenhum ponto da grade separa; de 0,4 a 0,9 só troca acerto por revisão. Fica a partida.
    "grupo": 0.50,
    # probabilidade da folha vencedora na Choice de folhas do grupo (a, c) < → `folha = null`. Ajuste: certa mínimo 0,68,
    # p10 0,94; errada (fora de aceitáveis) 0,64–1,00. Não separa; fica a partida.
    "folha": 0.50,
    # o mesmo na Choice única de 30 folhas (b). Ajuste: certa mínimo 0,76; errada 0,78 e 0,84 (um deles num `null`).
    # Não separa — b não consegue "só grupo" por limiar; fica a partida.
    "folha_unica": 0.50,
    # `blames_agency` (grupo atendimento) e `closed_elsewhere` (grupo concorrencia) ≤ → só grupo + revisar (o empate
    # exato é revisão, não sim — revisão do Codex 2026-10-01; antes era `<`). Ajuste:
    # `blames_agency` sim mínimo 0,60, não máximo 0,69 (num caso de `imovel`, onde a guarda não se aplica);
    # `closed_elsewhere` sim mínimo 0,93; o único disparo (0,33) tirou um grupo errado. Fica a partida.
    "guarda": 0.50,
    # `reason_stated` < com grupo ≠ sem_informacao → revisar (motivo possivelmente inventado). Ajuste: onde há motivo,
    # mínimo 0,52 ("vou pensar com carinho" depois de "bem acima do que eu imaginava"); nos 3 `sem_informacao`, máximo
    # 0,37. A partida 0,5 fica a 0,02 de um acerto (variação entre chamadas chega a 0,05): desce para o vão.
    "sem_motivo": 0.40,
}
# A que o critério julga. Regra de escolha, aplicada ao AJUSTE com os limiares acima: menos erros caros (motivo
# inventado + grupo errado automatizado); empate → abstém nos `folha: null` como o LEIA-ME pede (só-grupo certo);
# empate → maior acerto folgado; empate → menos requisições. Ajuste (34): erros caros a 2, b 2, c 2; só-grupo certo
# a 2/2, b 0/2, c 2/2; folgado a 0,882, b 0,912, c 0,882; requisições a 2, c 1 → c.
# Registro honesto: a ordem "folgado antes de abstenção" escolheria b (0,912). Não escolhi b porque ela não tem como
# dizer "só o grupo" — a Choice única não tem `only_group` e a probabilidade da folha errada num `null` foi 0,84, acima
# da certa em muitos casos — e o teste tem 7 `null` em 68 (LEIA-ME); o ajuste tem 2. Decidido no ajuste, antes do teste.
VARIANTE_PRINCIPAL = "c"

# ---------------------------------------------------------------------------------------- baseline de código
# Palavras-chave por folha, derivadas AUTOMATICAMENTE de nome + descrição de cada folha da taxonomia (minúsculas, sem
# acento, sem palavras vazias, radical = 5 primeiras letras), contadas só nas mensagens do cliente, cada radical
# pesando 1/(nº de folhas que o têm); a folha com mais pontos vence (empate: ordem da taxonomia). Sem nenhuma palavra
# em comum → `sem_informacao` por contagem de silêncio. O que um dev escreve em meia hora.
RADICAL = 5
VAZIAS = set("""a o as os um uma uns umas de do da dos das em no na nos nas por pra pro para com sem e ou que se
ao aos é ser tem ter foi isso isto esse essa esses essas este esta aqui ai la ja so mais menos muito
me te eu voce ele ela meu minha seu sua como quando onde qual quais quem porque nao não
ta to esta estao vai vou faz fazer preciso quero cliente imovel imóvel outro outra mesmo pelo pela antes depois
sobre lado parte""".split())
SILENCIO_MINIMO = 2  # mensagens do corretor sem resposta no fim para o baseline dizer "sumiu"

# ---------------------------------------------------------------------------------------- critério
# Critério de continuar/descartar — entra no manifesto `congelamento.json`. Fixado em 2026-10-01, depois do ajuste
# e ANTES de abrir `dados/teste.json`; mudar isto exige congelar de novo. Denominadores pela tabela do LEIA-ME
# (teste: 68 conversas, 8 `sem_informacao`, 7 com `folha: null`). Limites ABSOLUTOS nos erros caros + piso de acerto;
# o baseline entra só como "tem de ser melhor" (margem sobre baseline é critério frágil — metodo.md, 2026-10-01).
CRITERIO_CONTINUAR = {
    "onde": "no teste (68 conversas: 8 `sem_informacao`, 7 com `folha: null`), variante principal com os limiares acima",
    "variante_principal": VARIANTE_PRINCIPAL,
    "1_motivo_inventado": "gabarito `sem_informacao` e saiu outro grupo sem revisar ≤ 1/8",
    "2_grupo_errado_automatizado": "grupo ≠ gabarito (e folha fora de `aceitaveis`) sem revisar ≤ 6/68 (≤ 0,09)",
    "3_acerto_folgado": "folha ∈ `aceitaveis` (ou só o grupo certo quando `folha` é null), revisão e falha contam como erro ≥ 0,70",
    "4_grupo_certo": "grupo = gabarito ou folha ∈ `aceitaveis`, revisão e falha contam como erro ≥ 0,80",
    "5_revisao": "conversas mandadas a revisão (inclui falha operacional) ≤ 20% (≤ 13/68)",
    "6_contra_baseline": "acerto folgado > o do baseline de palavras-chave nos mesmos casos",
    "se_falhar": ("1 = o relatório inventa motivo: não serve nem como sugestão; 2 = o relatório mente de grupo: não serve "
                  "sem revisão humana de tudo; 3/4 = não lê a conversa melhor que um gestor apressado; 5 = revisa demais "
                  "para valer a automação; 6 = palavra-chave basta"),
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"inventado_max": 1, "grupo_errado_max_fracao": 0.09, "folgado_min": 0.70, "grupo_min": 0.80,
                "revisao_max_fracao": 0.20},
}
