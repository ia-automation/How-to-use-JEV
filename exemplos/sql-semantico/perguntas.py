"""Perguntas, faixas e política do SQL semântico — o ÚNICO arquivo que um humano precisa revisar.

Uma CONDIÇÃO de filtro escrita por um gestor ("clientes que mencionaram mudança de cidade", "observações de locação
em que o cliente reclamou do atendimento") é separada pelo código em duas partes (`sql.separar`):
- a parte entre crases (`` `orcamento` <= 500000 ``, `` `canal` = whatsapp ``) é do CÓDIGO: filtro sobre `campos`,
  resolvido em Python antes de qualquer chamada (limite #2: o Jev não compara número nem data);
- o resto é a parte SEMÂNTICA: para cada linha que passou no filtro, UM state `{"condition", "note"}` e UMA
  requisição ao Jev. O Jev julga "a observação diz isso?"; o código devolve `verdadeiro` / `falso` / `indecidivel`
  com os números daqui. Mudar política = editar número, sem chamar a API de novo.

Desenho (regras de rotulagem em dados/LEIA-ME.md; receita-irmã: conhecimento/receitas/classificar-passagens-rag.md —
um state por par consulta × item, Nouls atômicos, destino em código):
- `stated` (Noul): a observação AFIRMA o fato que a condição pede (negação explícita e silêncio são `false`; para
  condição negativa — "descartaram", "declararam NÃO ter" — o fato pedido é a própria negação). Três faixas: ≥ `sim`
  → verdadeiro; ≤ `nao` → falso; meio → `indecidivel` (vai para humano).
- `hinted` (Noul, mesma requisição, ≈ 60 tokens): a observação afirma OU só sugere o fato. Serve de válvula para a
  "pista fraca" do LEIA-ME (regra 3): `stated` baixo com `hinted` alto = sugere sem afirmar → `indecidivel`, não
  `falso`. Ligada ou não pela política (`VARIANTE["pista"]`), medida nas duas formas a partir das mesmas respostas.
- Condição composta ("A OU B", "A E B", conector em MAIÚSCULAS como o rotulador escreve): além de `stated` sobre a
  condição inteira, um Noul `stated_part_<i>` por cláusula (`condition_parts[i]`, mesmo state, mesma requisição);
  o código combina pela regra 5 do LEIA-ME (E: os dois afirmados → verdadeiro, um afirmado e o outro fraco →
  indecidível, qualquer um negado/ausente → falso; OU: um afirmado → verdadeiro, nenhum afirmado e algum fraco →
  indecidível). `VARIANTE["composta"]` escolhe entre a pergunta inteira e as cláusulas; as duas são medidas.
- Os `campos` NÃO vão no state: ou o código já os consumiu (filtro) ou enviesariam o julgamento — a condição é
  sobre o que a observação DIZ (LEIA-ME, regra 1); `etapa = perdido` não pode virar "desistiu".
- Perguntas em inglês sobre dados em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram e custaram +10%).
  A condição (pt-BR) é DADO: vai no state, não na pergunta — a pergunta é a mesma para toda condição.

Afinação (só no rascunho e no ajuste, 2026-10-01; números completos em resultados-ajuste-passada1.md e resultados.md):
- 1ª passada (2.174 requisições: 871 do rascunho + 1.303 do ajuste), state só com `condition` e `note`: F1 0,976 nas
  decidíveis decididas, 0 perdida, 0 FP em negação, mas 118/1.669 (7,1%) a humano com a faixa 0,2–0,8 — 103 falsas
  entre 0,2 e 0,8, concentradas nas condições cuja frase semântica REPETE em palavras a parte de campo ("têm orçamento
  de até R$ 500.000", "tendo feito ao menos 1 visita"): nelas o piso das falsas sobe de 0,02–0,05 para 0,21–0,41 (o
  Jev vê metade da condição satisfeita). `hinted` ≥ 0,8 com `stated` ≤ 0,2 não ocorreu: a válvula não mudou nada.
- 2ª passada (mais 2.174 requisições): a parte de campo entra no state como fato conferido (`checked_by_code`) e o
  `false` diz "circunstância não é afirmação". Efeito: nenhum sobre o piso das falsas (SQ-A03 continua com 38 a humano
  na faixa 0,2–0,8); F1 0,968 (inteira) / 0,977 (cláusulas); 1 perdida (SQ-A06 OB-107 "fechou com outra
  imobiliária", 0,16; na 1ª passada 0,34 — zona de variação entre chamadas). As perguntas da 2ª passada ficam.
- Política fixada com as respostas da 2ª passada (grade em resultados.md): faixa 0,3–0,8 (o `nao` sobe para 0,3
  porque a massa de falsas hesitantes para em 0,21–0,30 e nenhuma verdadeira do ajuste cai entre 0,2 e 0,3; o `sim`
  fica em 0,8 porque 0,7 deixaria passar uma falsa de negação a 0,72 — o erro caro); cláusulas (um Noul por cláusula
  combinado pela regra 5 do LEIA-ME — uma condição por pergunta; na única composta do ajuste, +3 linhas certas na 2ª
  passada e −2 na 1ª: diferença dentro do ruído, decidida pelo desenho); `hinted` ligado a 0,7 (manda a humano 4
  indecidíveis a mais do gabarito ao custo de 18 falsas a mais: 77/1.669 = 4,6% a humano, 9/14 indecidíveis
  revisados). Resultado no ajuste com a política final: F1 0,977, 1 perdida, 0 FP em negação.
Nenhuma pergunta foi alargada para consertar um caso: as duas mudanças escrevem regra que já estava no LEIA-ME.
"""

# ---------------------------------------------------------------------------------------- perguntas
_CONTEXTO = (
    "`note` is a short observation in Brazilian Portuguese, written by a real-estate agent right after talking to a "
    "client (one to three sentences; the client is never named). "
)
_FILTRO_DO_CODIGO = (
    "When `checked_by_code` is present, it lists the parts of the condition about database fields (budget amount, "
    "number of visits, contact channel, purpose, pipeline stage, date) that code already verified for this record: "
    "they hold, even if `condition` restates them in words, and they must not be judged from the note. The answer "
    "depends only on the remaining fact(s), the ones about what the client said or what the property is like."
)
_SIM = (
    "The note itself states the fact the condition asks for, in any wording: synonym, slang, figure of speech or "
    "paraphrase count as stating it. When the condition asks for a refusal, a denial or giving up (ruled out, "
    "declared NOT having, gave up), the note explicitly states that refusal, denial or giving up."
)
_NAO = (
    "The note does not state the fact: it does not mention it at all (silence is not satisfaction), or it gives only "
    "a circumstance from which the fact could be guessed (the fact must be stated, not inferred); or it states the "
    "opposite of what the condition asks for, even with the same keyword ('não tem pet', 'não vai financiar', 'largou "
    "o home office'); or it uses a related word in another sense (a property that NEEDS renovation is not a "
    "renovated property; dropping a competitor is not evaluating a competitor; a complaint about a landlord is not a "
    "complaint about our service)."
)


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


# State: {"condition": "<parte semântica, pt-BR>", "note": "<texto da linha>"} (+ "checked_by_code": ["orcamento <= 500000"] quando
# há parte de campo; + "condition_parts": [...] nas compostas).
PERGUNTAS = {
    "stated": _noul(
        _CONTEXTO + "`condition` is a filter condition a manager wrote, also in Portuguese, to select such records. "
        "Judging only by what `note` states, does this record satisfy `condition`? " + _FILTRO_DO_CODIGO,
        _SIM,
        _NAO,
    ),
    "hinted": _noul(
        _CONTEXTO + "`condition` is a filter condition a manager wrote, also in Portuguese, to select such records. "
        "Does `note` state, or at least suggest, the fact that `condition` asks for — even indirectly, without "
        "saying it outright? " + _FILTRO_DO_CODIGO,
        "The note states the fact, or gives a hint that points to it without stating it: a question that the fact "
        "would explain, a wish or a circumstance that fits it, a plan that would lead to it.",
        "Nothing in the note points to the fact, or the note states the opposite of it.",
    ),
}


def pergunta_parte(i: int) -> dict:
    """Noul de UMA cláusula de condição composta (`condition_parts[i]`); mesma leitura literal de `stated`."""
    return _noul(
        _CONTEXTO + f"`condition_parts[{i}]` is ONE clause of a compound filter condition a manager wrote in "
        "Portuguese (the other clauses are judged separately). Judging only by what `note` states, does this record "
        f"satisfy the clause `condition_parts[{i}]`? " + _FILTRO_DO_CODIGO,
        _SIM,
        _NAO,
    )


def perguntas_de(partes: list[str]) -> dict:
    """As perguntas de uma requisição: as duas fixas e, se a condição é composta, uma por cláusula."""
    q = dict(PERGUNTAS)
    if len(partes) > 1:
        for i in range(len(partes)):
            q[f"stated_part_{i}"] = pergunta_parte(i)
    return q


# ---------------------------------------------------------------------------------------- política
# Noul `stated` em três faixas: ≤ nao → falso; ≥ sim → verdadeiro; meio → indecidível (humano). Partida 0,2–0,8
# (NÚCLEO §6); afinada no ajuste (2ª passada): verdadeiras p10 0,61 / p50 0,90; falsas p90 0,19, com uma massa
# hesitante em 0,21–0,30 (condições com resíduo numérico) e 3 acima de 0,8; indecidíveis do gabarito p50 0,28.
FAIXA = {"stated": (0.3, 0.8)}
# `hinted` ≥ este valor com `stated` ≤ `nao` = "sugere sem afirmar" → indecidível (só quando `VARIANTE["pista"]`).
# Ajuste: a 0,8 não muda nada; a 0,7 revisa 4 indecidíveis a mais e 18 falsas a mais.
PISTA_SIM = 0.7
# Variante oficial (as outras são calculadas das mesmas respostas, sem chamada nova):
#   composta: "inteira" (um Noul sobre a condição inteira) | "clausulas" (um Noul por cláusula, combinados em código)
#   pista: liga a válvula do `hinted`
VARIANTE = {"composta": "clausulas", "pista": True}
# Faixa validada: as observações têm até ~140 caracteres. Acima do teto a linha NÃO vai ao Jev: `indecidivel`,
# motivo "texto longo" (família do achado 6 do imovel-errado). Não é limiar afinado.
TETO_CARACTERES = 2000
# Orçamento de requisições (uma por linha que passa no filtro, por condição). O teste tem 18 condições × ≤ 187 linhas.
ORCAMENTO = {"teste": 3500, "construcao_total": 9000}

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado em 2026-10-01 depois do ajuste e ANTES de abrir `dados/condicoes_teste.json`. Denominadores pela tabela do
# LEIA-ME (teste: 18 condições, 131 linhas verdadeiras, 27 indecidíveis, 3 condições de negação). Métricas sobre as
# linhas DECIDÍVEIS (fora de `linhas_indecidiveis`) de todas as condições juntas (micro); linha mandada a humano fica
# fora de P/R/F1 e é contada à parte. O teto de humano (8%) foi posto acima do ajuste (4,6%) porque o teste tem o
# dobro de condições compostas e com resíduo numérico, onde a hesitação mora.
CRITERIO_CONTINUAR = {
    "onde": "no teste (18 condições × 187 linhas), com a política acima",
    "1_f1": "F1 do Jev sobre as decidíveis decididas ≥ 0,85 e ≥ F1 do baseline (LIKE) + 0,15",
    "2_perdidas": "linha verdadeira do gabarito que saiu `falso` ≤ 5% das verdadeiras",
    "3_negacao": "linha falsa marcada `verdadeiro` em condição de negação ≤ 2",
    "4_humano": "decidíveis mandadas a humano (`indecidivel`) ≤ 8%",
    "secundario_nao_decide": "indecidíveis do gabarito que foram a humano ≥ 50%; falha operacional = 0",
    "se_falhar": "1 falhando = o LIKE basta ou o Jev não lê a condição; 2 ou 3 = o filtro perde ou inverte o que "
                 "deveria achar (não serve sem mudança); 4 = custa humano demais",
    "limites": {"f1_min": 0.85, "margem_baseline": 0.15, "perdidas_max": 0.05, "fp_negacao_max": 2,
                "humano_max": 0.08, "indecidiveis_a_humano_min": 0.5},
}

# ---------------------------------------------------------------------------------------- baseline de código
# "LIKE": palavras da parte semântica da condição (sem acento, minúsculas, sem as genéricas abaixo), cortadas na
# 5ª letra — o que um dev escreveria em meia hora: `WHERE texto ILIKE '%reform%' OR texto ILIKE '%pet%'`.
# Qualquer palavra presente = verdadeiro. Não tem `indecidivel`: LIKE não sabe que não sabe.
BASELINE_IGNORAR = {
    "clientes", "cliente", "observacoes", "observacao", "corretor", "descreve", "mencionaram", "mencionou", "registradas",
    "registrada", "nosso", "nossa", "imovel", "visitado", "oferecido", "para", "como", "quem", "tendo", "feito", "menos",
    "pelo", "pela", "estao", "esta", "tem", "uma", "por", "ora", "ate", "sem", "mais", "quais", "seus", "suas", "que",
    "com", "dos", "das", "nao", "vao", "vem", "fora", "embora", "outra", "outro", "outros", "outras", "sao", "foi",
    "forma", "sobre", "qual", "algum", "alguma", "ainda", "mesmo", "mesma", "esse", "essa", "este", "esta", "isso",
    "disseram", "dizem", "disse", "fazem", "faz", "ter", "tem", "seu", "sua", "nos", "nas", "aos", "ao", "no", "na",
    "de", "do", "da", "em", "ou", "e", "o", "a", "os", "as", "um", "se", "ja", "so", "ha", "bem", "muito", "pouco",
    # valores e nomes de campo: a parte estruturada vai no WHERE, não no LIKE
    "compra", "locacao", "whatsapp", "telefone", "email", "presencial", "orcamento", "visita", "visitas", "reais", "mil",
    "etapa", "novo", "contato", "proposta", "perdido",
}
BASELINE_CORTE = 5  # letras mantidas de cada palavra ("financiamento" → "finan", que também pega "financiar")
