"""Perguntas, limiares, contexto do comprador e baseline do comparador de propostas — o ÚNICO arquivo que um
humano revisa.

Uma disputa = requisitos + 3 propostas. Por (proposta, requisito) a célula vale `atende` / `contradiz` /
`nao_informado`. Requisito `numerico` ("(`campo` <= N)") é do CÓDIGO em `comparador.py`: compara `campos` com
o limite extraído do texto do requisito (limite #2: o Jev não compara números); `null` → `nao_informado`. O Jev
só julga os requisitos `semantico`.

Desenho: UM state por PROPOSTA (`proposal` + `buyer` + `requirements[]`, só os semânticos) e uma pergunta por
requisito apontando `requirements[i]` — as perguntas são isoladas, então agrupar não muda a resposta e divide o
custo do state. Dois desenhos medidos no ajuste, com as MESMAS regras do `dados/LEIA-ME.md` (escritas antes dos
casos): `choice` (Choice de 3 com válvula de `nao_informado` por confiança) e `nouls` (dois Nouls — "afirma que
entrega" / "exclui ou contradiz" — combinados em código, exclusão vence). Perguntas em inglês sobre texto em
pt-BR (medido em 2026-09-30: a língua da pergunta não muda o acerto; em pt custa +10% de tokens).

Afinação (só no ajuste, 2026-10-01, duas passadas de 30 requisições por desenho; números em `resultados.md`):
- 1ª passada: Choice 65/72 células semânticas (0,903), Nouls 63/72 (0,875); exclusão escondida aprovada 0/19 nos
  dois. Os erros fora da válvula eram regras do LEIA-ME que a pergunta não dizia com todas as letras: requisito
  com DUAS partes e uma delas "feita pelo cliente" (homologação, CP-A08) saiu `contradicts` a 0,36 → válvula;
  "instalação cobrada em parcela única" (CP-A09) saiu `not_stated` 0,33 ("cobra à parte" não cobria valor único
  sobre a mensalidade); "Instalação inclusa" genérico para "instalação de interfone e fechaduras" saiu
  `not_stated` 0,28.
- 2ª passada: as `rules` ganharam as frases do LEIA-ME (várias partes → todas; plano/opção COM preço = contradiz,
  SEM preço = nao_informado; valor único sobre o recorrente = cobra à parte; "incluso" sobre o próprio item cobre
  um requisito que só lista as partes). Choice 66/72 (0,917), Nouls 61/72 (0,847); CP-A08 → `contradicts` 0,92 e
  CP-A09 p2 → 0,61. NÃO moveu: "gravação disponível no plano Pro" sem preço (CP-A05, `contradicts` 0,81 nas
  duas passadas — o modelo lê "em outro plano" como "não neste"), "Instalação inclusa" genérico (0,27) e
  "treinamento no plano anual; no mensal, cobrado à parte" (CP-A02, `contradicts` 0,98 — o texto diz "cobrado à
  parte" para o plano do pedido; o gabarito marca nao_informado pela regra do plano; discordância de rotulagem,
  a pergunta não foi torcida para isso).
- Nenhuma pergunta foi alargada para consertar um caso isolado; cada frase nova cita uma regra do LEIA-ME.
"""

CELULAS = ("atende", "contradiz", "nao_informado")
# Campo numérico (dos `campos` do rotulador) → como o comprador o nomeia na pergunta ao fornecedor (achado 7 da
# revisão: a pergunta expunha `garantia_meses` e o parêntese operacional). Campo fora da lista: nome sem sublinhado.
CAMPO_LEGIVEL = {
    "preco_total": "o preço total em reais", "prazo_dias": "o prazo em dias corridos",
    "garantia_meses": "a garantia em meses", "suporte_meses": "a duração do suporte em meses",
    "franquia": "a franquia em reais", "horas": "a quantidade de horas", "kva": "a potência em kVA",
    "mbps": "a velocidade em Mbps", "contrato_meses": "a duração mínima do contrato em meses",
    "paginas_mes": "a franquia de páginas por mês", "sla_horas": "o prazo de reparo em horas",
    "troca_horas": "o prazo de substituição em horas", "contatos": "a quantidade máxima de contatos do plano",
}
# Opção da Choice (inglês, vai ao modelo) → célula (pt, dos dados).
CELULA_DA_OPCAO = {"meets": "atende", "contradicts": "contradiz", "not_stated": "nao_informado"}

# ---------------------------------------------------------------- state: contexto fixo do comprador
# As ambiguidades que o LEIA-ME decidiu ("o pedido é sempre da sede na capital, plano mensal, serviço único") são
# fatos do PEDIDO, não julgamento: entram no state para o Jev ler, nunca na pergunta como regra escondida.
BUYER = ("A real-estate agency headquartered in the capital city (so 'in the capital' is satisfied). It is buying "
         "exactly what the proposal prices: the monthly plan when there are plans, the single service when there is "
         "'annual vs one-off', the base price stated — nothing optional, no higher plan, no surcharge.")

# ---------------------------------------------------------------- desenho `choice`: uma Choice por requisito
_INSTRUCAO = {
    "question": "Does `proposal` meet the requirement in `requirements[{i}]` at the price it quotes?",
    "context": "`proposal` is the text of a supplier's quote, in Brazilian Portuguese. `buyer` describes what is "
               "being bought. `requirements[{i}]` is one item of the buyer's requirement list.",
    "rules": "Judge only what the proposal text says, not what is plausible or usual. An exclusion anywhere in the "
             "text (a final remark, 'os valores não contemplam', 'exceto', 'à parte', 'por conta do cliente') wins "
             "over an earlier 'included'. Something delivered only as an optional item, add-on, surcharge, priced "
             "higher plan or under a condition the buyer does not meet is NOT delivered at the quoted price. A "
             "vague term that does not settle the requirement, or a reference to an attachment that is not in the "
             "text, does not meet it and does not contradict it. A requirement that names several things is met only "
             "when every one of them is delivered: one of them excluded, charged or left to the buyer → contradicts; "
             "one of them not stated → not_stated. An item available only in another plan, option or add-on: if the "
             "text gives its price or says it is charged, that is contradicts; if the text gives no price for it, "
             "that is not_stated (the buyer will ask).",
}
_OPCOES = {
    "meets": {
        "what": "The proposal states, without condition or extra charge, that it delivers what the requirement asks, "
                "literally or in words a buyer would accept as equivalent; a condition the buyer already satisfies "
                "(see `buyer`) counts as met; a plain 'included' statement about the item itself ('instalação "
                "inclusa', 'montagem inclusa') meets a requirement that only lists which parts get installed — it is "
                "vague only when the requirement asks for a measure, duration, certification or scope the text does "
                "not give",
        "not_for": "A vague term that does not settle the point; an item delivered only as an option, add-on, "
                   "surcharge or higher plan; a text that includes it in one sentence and excludes part of it in "
                   "another; a reference to an attachment",
        "examples": ["requirement 'instalação inclusa' → 'instalação inclusa no valor'",
                     "requirement 'montagem inclusa' → 'montagem inclusa na capital' (the buyer is in the capital)",
                     "requirement 'até 50 mil contatos' → 'contatos ilimitados'",
                     "requirement 'garantia de 2 anos' → 'garantia de 24 meses'",
                     "requirement 'sem custo' → 'sem custo adicional'"],
    },
    "contradicts": {
        "what": "The proposal says it does NOT deliver it, delivers something different (another schedule, method, "
                "provider or scope), leaves it to the buyer, charges for it separately (including a one-off amount on "
                "top of the recurring price), or delivers it only as an optional item, add-on, surcharge, or a higher "
                "plan with a stated price — the quoted price does not cover the requirement",
        "not_for": "A requirement the proposal never addresses; a vague term; an attachment not in the text; a "
                   "higher plan or option whose price is not given",
        "examples": ["'instalação inclusa… Observação: os valores não contemplam infraestrutura' (exclusion wins)",
                     "'peças inclusas, exceto compressor' for 'peças inclusas'",
                     "'monitoramento em horário comercial, extensão para 24h mediante adicional' for '24h'",
                     "'montagem opcional por R$ 900,00' for 'montagem inclusa'",
                     "'automação disponível a partir do plano Pro (R$ 890,00)' when the quote is another plan",
                     "'central parceira terceirizada' for 'central própria'",
                     "'de segunda a sábado, das 6h às 22h' for 'atendimento 24h'",
                     "'tratada diretamente com a operadora, sem envolvimento nosso' for 'portabilidade inclusa'"],
    },
    "not_stated": {
        "what": "The proposal does not address the requirement, uses a vague term that does not settle it, refers to "
                "an attachment that is not in the text, conditions it on a plan or option the buyer did not quote and "
                "whose price is not given, or says it is in process (renewal, to be sent)",
        "not_for": "A fact the proposal states in other words; an explicit exclusion, surcharge or priced option",
        "examples": ["'suporte incluso' for 'suporte por 12 meses' (no duration)",
                     "'cadeiras ergonômicas' for 'certificação NR-17' (no certification)",
                     "'conforme memorial descritivo anexo' (attachment not in the text)",
                     "'prazo conforme cronograma a ser enviado'",
                     "'gravação disponível no plano Pro' when the quote is the Básico plan and Pro has no price",
                     "'treinamento incluso no plano anual' when the buyer takes the monthly plan",
                     "'registro em processo de renovação' for 'registro vigente'",
                     "a requirement the text never mentions"],
    },
}


def choice(i: int) -> dict:
    return {"type": "choice", "instructions": {k: v.format(i=i) for k, v in _INSTRUCAO.items()}, "criteria": _OPCOES}


# ---------------------------------------------------------------- desenho `nouls`: dois Nouls por requisito
def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


def noul_entrega(i: int) -> dict:
    return _noul(
        f"`proposal` (a supplier's quote in Brazilian Portuguese) states that it delivers what `requirements[{i}]` "
        f"asks, included in the price it quotes, without an option, surcharge, higher plan or a condition the "
        f"buyer in `buyer` does not meet. A requirement that names several things is delivered only when every "
        f"one of them is. Judge only what the text says.",
        "The text affirms the item is delivered and included — literally or in equivalent words ('sem custo "
        "adicional' = included; 'ilimitados' covers any limit; '24 meses' = 2 years; a condition the buyer "
        "satisfies, such as 'na capital', counts; a plain 'instalação inclusa' covers a requirement that only lists "
        "which parts get installed).",
        "The text never addresses the item; uses a vague term that does not settle a measure, duration, "
        "certification or scope the requirement asks ('suporte incluso' without duration, 'cadeiras ergonômicas' "
        "without the certification asked); refers to an attachment not in the text; delivers it only as an option, "
        "add-on, surcharge or in another plan; leaves one of its parts to the buyer; or excludes it or part of it "
        "elsewhere in the text ('os valores não contemplam…', 'exceto…').",
    )


def noul_exclui(i: int) -> dict:
    return _noul(
        f"`proposal` states that it does NOT deliver what `requirements[{i}]` asks at the quoted price: it denies "
        f"it, delivers something different (another schedule, method, provider or scope), leaves one of its parts "
        f"to the buyer, charges for it separately (including a one-off amount on top of the recurring price), or "
        f"offers it only as an optional item, add-on, surcharge or a higher plan with a stated price. An exclusion "
        f"anywhere in the text — a final remark, 'exceto', 'à parte', 'por conta do cliente' — counts even if an "
        f"earlier sentence says 'incluso'.",
        "The text excludes it or one of its parts, charges for it, delivers another thing instead ('central "
        "parceira' for 'central própria'; '6h às 22h' for '24h'; 'gravação local em DVR' for 'nuvem'), or makes it "
        "an option, add-on, surcharge or priced higher plan.",
        "The text never addresses the item, affirms it as included, uses a vague term, refers to an attachment "
        "not in the text, or mentions a higher plan or option WITHOUT a price (that is unknown, not excluded).",
    )


DESENHOS = ("choice", "nouls")
# Ajuste 2026-10-01 (10 disputas, 30 propostas, 72 células semânticas, 2ª passada): Choice 0,917 × Nouls 0,847,
# exclusão escondida aprovada 0/19 nos dois, elegíveis exatos 0,80 × 0,60. A Choice custa quase o dobro de tokens
# (3.439 × 1.790 por proposta: as glosas `what`/`not_for`/`examples` repetem por requisito) — US$ 0,43 × 0,23 por
# mil disputas; os Nouls hesitam no "entrega" (0,42–0,45 em três células certas). Choice fica, pelo acerto.
DESENHO_PADRAO = "choice"

# ---------------------------------------------------------------- limiares (válvula de `nao_informado`)
# Choice: `confidence` (não a probabilidade do vencedor). `meets` com conf < CONF_ATENDE → nao_informado;
# `contradicts` com conf < CONF_CONTRADIZ → nao_informado; `not_stated` fica. `nao_informado` é a válvula porque é a
# ação segura: vira PERGUNTA ao fornecedor (a proposta continua elegível, LEIA-ME "Elegibilidade"), nunca aprova
# nem descarta. Assimétrico: aprovar uma exclusão escondida é o erro caro (compra a proposta errada), então
# `atende` exige mais certeza que `contradiz`. Célula numérica (código) não tem confiança: decide direto.
# Ajuste 2026-10-01 (curva em `resultados.md`): exclusão aprovada 0/19 e inelegível elegível 0/16 em TODA a grade
# (de 0/0 a 0,9/0,9) — a válvula não comprou nada mensurável; a 0,7/0,5 moveu 3 `meets` CERTOS (0,44–0,67) para
# pergunta (acerto 0,958 sem válvula, 0,944 a 0,5/0,5, 0,917 a 0,7/0,5). Fica 0,7/0,5 pelo RISCO da ação
# (lição da conferência de promessas): o custo de um falso nao_informado é UMA pergunta ao fornecedor; o de um
# falso atende é comprar a proposta errada. O teste diz se a faixa paga.
CONF_ATENDE = 0.7
CONF_CONTRADIZ = 0.5
# Nouls: ≥ sim → sim; ≤ nao → não; meio = dúvida. Combinação em código (`comparador.combinar_nouls`):
# exclui ≥ sim → contradiz (exclusão vence inclusão, LEIA-ME); senão entrega ≥ sim e exclui ≤ nao → atende; o
# resto (dúvida em qualquer um, ou os dois baixos) → nao_informado.
FAIXA_ENTREGA = (0.3, 0.7)
FAIXA_EXCLUI = (0.3, 0.5)

# ---------------------------------------------------------------- baseline de código
# O que um dev faria em 20 minutos sem modelo: numérico → mesma comparação do código; semântico → a frase da
# proposta que contém uma palavra-chave do requisito (prefixo de 5 letras, sem palavras de ligação): frase com
# marca de exclusão → contradiz; frase sem marca → atende; nenhuma frase → nao_informado. Erra de propósito
# nas famílias do LEIA-ME: exclusão escondida em OUTRA frase, termo vago, plano superior.
# Regex sobre o texto normalizado (sem acento, minúsculas), com fronteira de palavra: "Instalação: não." e "não" no
# fim do texto contam (revisão do Codex, 2026-10-01, achado 6 — "nao " com espaço deixava a negação terminal passar).
BASELINE_EXCLUSAO = (r"\bnao\b", r"\bsem\b", r"\ba parte\b", r"\bpor conta d", r"\bopcional", r"\badicional",
                     r"\bmediante\b", r"\bcobrad", r"\bexceto\b", r"\bsomente\b", r"\bapenas\b", r"terceiriz",
                     r"parceir")
BASELINE_STOP = {"o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "e", "com",
                 "sem", "por", "para", "que", "ate", "pelo", "pela", "menos", "preco", "inclus", "inclusa",
                 "incluso", "inclusas", "inclusos", "conta", "contratada", "contratante", "proprio", "propria"}
