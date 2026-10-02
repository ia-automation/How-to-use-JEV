"""Perguntas, faixas e política da triagem de documentos — o ÚNICO arquivo que um humano precisa revisar.

"Quais destes contratos têm multa por rescisão / exclusividade / reajuste fora do índice?" Uma CONDIÇÃO escrita por
um advogado ou gestor é aplicada a cada documento longo (4–8 seções) e o código devolve, por documento,
`verdadeiro` / `falso` / `indecidivel` (humano lê) e a seção que prova. O que este exemplo MEDE é o limite "state
grande com lixo derruba acerto": dois desenhos com as MESMAS perguntas de fundo, medidos no ajuste e no teste.

- Desenho A, **mapa por seção**: um state por seção `{"condition", "document_type", "section": {"title", "text"}}`
  e UMA requisição por seção com três Nouls — `establishes` (a seção, por si, institui o que a condição pede),
  `revokes` (a seção revoga/cancela/declara sem efeito uma cláusula ANTERIOR sobre o mesmo assunto) e `deferred`
  (a seção deixa a decisão para depois sem conceder nem negar — válvula do indecidível). O CÓDIGO reduz na ordem
  do texto (`triagem.reduzir`): o documento é verdadeiro se alguma seção institui e nenhuma posterior revoga;
  `secao_que_prova` = seção de maior `establishes`.
- Desenho B, **documento inteiro num state**: `{"condition", "document_type", "sections": [...]}` e UMA requisição
  por documento com `holds` (o documento, lido inteiro e como fica ao final, dispõe o que a condição pede),
  `deferred` e uma Choice `proving_section` (qual seção completa a prova; `none` se nenhuma).
- Condição `numerica` (crase: `` `multa_alugueis` > 2 ``) é do CÓDIGO sobre `campos` — zero chamada (limite #2);
  a contagem "quantos têm" é do código nos dois desenhos.
- Perguntas em inglês sobre dados em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram e custaram +10%);
  a condição (pt-BR) é DADO: vai no state, não na pergunta — a pergunta é a mesma para toda condição.
- Os `campos` NÃO vão ao Jev: a condição semântica é sobre o que o TEXTO dispõe (regra 1 do LEIA-ME).

Afinação (só no rascunho e no ajuste, 2026-10-02; números em resultados-rascunho*.md, resultados-ajuste-passada1.md e
resultados.md; o teste NÃO foi aberto):
- 1ª passada (2.488 requisições únicas; faixa 0,2–0,8 nos três Nouls; `deferred` sem exigir o assunto da condição):
  rascunho e ajuste com F1 1,000 nos dois desenhos, 0 perdida, 0 FP; baseline F1 0,571 / 0,660 (57 / 32 FP, 23 deles
  em condições de negada). O que custou humano: (a) negação lida pelo `revokes` a 0,26–0,28 ("NÃO haverá multa", "NÃO
  estabelece exclusividade") e a retificação da OBRA (A05-s6) a 0,28 para a condição de reajuste da TAXA — uma
  verdadeira do A a humano; as revogações reais leram 0,97–0,98; (b) `establishes` de falsas a 0,21 (reajuste de
  contrato de serviço para a condição de ata) e 0,33–0,68 (câmeras para "obra"; não concorrência pós-contrato para
  "exclusividade"); (c) `deferred` 0,72 em "índice a ser definido" (L08-s3) para "reajuste pelo IGP-M" (gabarito
  falso) e 0,51–0,55 em matéria aberta de OUTRO assunto. No B, duas verdadeiras de multa (L02, L11) a 0,40–0,52:
  o documento inteiro hesita quando uma seção final revoga OUTRA cláusula (sublocação) — o efeito que o exemplo mede.
- 2ª passada (mais 2.488): `deferred` passou a exigir o assunto exato da condição e a tratar "detalhe a definir" como
  ausência (regra 7 + nota de R01 do LEIA-ME); `holds` ganhou "revogação de outro assunto não afeta"; faixa do
  `establishes`/`holds` 0,3–0,8 (nenhuma verdadeira abaixo de 0,97 na seção que prova no A; falsas p90 0,08) e do
  `revokes` 0,4–0,8 (negações e revogação de outro assunto ≤ 0,28, revogações reais ≥ 0,97; 0,4 deixa a variação
  máxima medida entre chamadas, 0,15, fora do bolo). Ajuste: A F1 1,000, 2 a humano (não concorrência a 0,73), 0
  perdida, 0 FP, prova 22/22; B F1 1,000, 4 a humano (L02 0,53 e L11 0,51 continuam), 0 FP, prova 22/22. Rascunho: A
  5 a humano (seções de ata a 0,39–0,52), B 3 (1 verdadeira, L05 0,68), prova 30/30 × 29/30. `deferred` não disparou.
- Custo medido: A ≈ 7 requisições por documento (1.530 tokens cada, 10,8 mil por documento, US$ 0,46 por mil
  documentos avaliados; 1,9 s serial medido / 0,30 s estimativa idealizada = máx das seções); B 1 requisição (2.711 tokens, US$ 0,11 por
  mil; 0,28 s). Desenho padrão **A** (mapa por seção): mesma F1, metade do humano no ajuste, nenhuma verdadeira a
  humano e a revogação de outro assunto não o move; o B custa 4× menos e é a variante medida ao lado.
Nenhuma pergunta foi alargada para consertar um caso: as duas mudanças escrevem regra que já estava no LEIA-ME.

Rodada 2 (pós-revisão do Codex, 2026-10-02, NÃO cega, zero chamada nova — tudo do cache): `tipo` da condição passa
a ser lido e validado (numérica sem expressão = inválida, 0 chamada); a expressão numérica é validada inteira;
condição composta "A E B" ganha um Noul por cláusula (`perguntas_secao` / `perguntas_documento`) combinado em código
(regra 6, "duas seções") — na rodada 2 as condições do rotulador não usavam o conector (nenhum state mudou); a
latência "paralela" do mapa é estimativa idealizada (máx das seções, chamadas em sequência). Faixas, critério e
textos das perguntas da rodada 1 intactos.
Rodada 3 (dado v2b, 2026-10-02, não cega): TD-A03 e TD-T03 reescritas com " E " pelo rotulador → 622 chamadas
novas (1,71 M tokens, US$ 0,072); cláusulas lidas a 0,96–0,98 nos verdadeiros e a cláusula faltante a ≤ 0,14 nos falsos de uma
cláusula só (A e B); prova = a seção que completa (5/5 e 4/4). Números no README e em resultados.md.
"""

# ---------------------------------------------------------------------------------------- perguntas
TIPOS_DOCUMENTO = {"locacao": "contrato de locação residencial", "prestacao_servico": "contrato de prestação de serviços",
                   "ata_condominio": "ata de assembleia de condomínio", "proposta_comercial": "proposta comercial"}

_CONTEXTO = (
    "`condition` is a filter condition written in Brazilian Portuguese by a lawyer or a manager, describing something a "
    "document must PROVIDE (a clause, a decision, a term) and, usually, the kind of document it refers to. "
    "`document_type` is the kind of this document. "
)
_REGRAS = (
    "Rules: the condition is about what the text actually provides; silence is not satisfaction. A restricted or "
    "conditional version of the clause still counts (exclusivity limited to a list of competitors, approval 'with "
    "reservations'). A term that appears only in a title, while the text is about something else, does not count. A "
    "similar clause about another subject does not count (a late-payment penalty is not an early-termination penalty; "
    "a service-level penalty is not a termination penalty; access control by biometrics is not cameras; implementation "
    "with manuals is not training). An EXPRESS denial or rejection is the opposite of providing it ('NÃO haverá "
    "multa', 'não estabelece exclusividade', 'MANTER a taxa sem reajuste', 'proposta REJEITADA'). A decision postponed "
    "to a next meeting is not an approval. If `document_type` is not the kind of document the condition refers to, "
    "the condition is not satisfied."
)
_SIM_INSTITUI = (
    "The text itself provides what the condition asks for, in force as written here: the clause, obligation, right, "
    "decision or term exists in this text, even in a restricted, conditional or paraphrased form."
)
_NAO_INSTITUI = (
    "The text does not provide it: it is about another subject or a similar but different clause; the term is only in "
    "the title; the text expressly denies, rejects or excludes it; the text revokes, cancels or declares without effect "
    "a clause (cancelling is not providing); the text merely postpones the decision or makes it depend on a future "
    "consent; or the document is not of the kind the condition refers to."
)
_SIM_ADIADO = (
    "The text addresses precisely the matter the condition asks for and neither grants nor denies it: it makes that "
    "matter depend on a future case-by-case consent or consultation ('mediante consulta prévia', 'será avaliado caso a "
    "caso'), sets a provisional or experimental arrangement on it with the final decision left for later (a trial "
    "period, a temporary tolerance), or says a breach 'may' lead to a revision without saying what follows."
)
_NAO_ADIADO = (
    "The text grants it, denies it, or says nothing about it; the open matter is about ANOTHER subject than the "
    "condition's; a detail is merely left to be defined later (an index, a date, an amount 'a ser definido'), which is "
    "absence of what the condition asks for, not an open decision; or the whole deliberation is only postponed to a "
    "next meeting with no provisional arrangement (plain absence)."
)


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


# Desenho A — state {"condition", "document_type", "section": {"title", "text"}}; as outras seções NÃO estão no state.
PERGUNTAS_SECAO = {
    "establishes": _noul(
        _CONTEXTO + "`section` is ONE section (title and text) of that document; the other sections are judged "
        "separately and are not shown. Judging only by this section's text, does this section itself establish what "
        "`condition` asks for? " + _REGRAS,
        _SIM_INSTITUI, _NAO_INSTITUI,
    ),
    "revokes": _noul(
        _CONTEXTO + "`section` is ONE section (title and text) of that document; the other sections are not shown. "
        "Does this section revoke, cancel, set aside or declare without effect a clause or decision made EARLIER in the "
        "same document about the subject of `condition` — so that, after this section, the document no longer "
        "provides it?",
        "The text expressly cancels, revokes, declares without effect or 'considers unwritten' a provision made in "
        "another clause or item of the same document on that subject ('fica sem efeito a multa prevista na cláusula…', "
        "'afastam a renovação automática prevista na cláusula de vigência', 'declarou SEM EFEITO a aprovação registrada "
        "acima'), or replaces it with the opposite.",
        "The section does not undo an earlier provision on that subject: it establishes or confirms it, extends it, "
        "says the other clauses remain intact, is about another subject, denies something that was never granted "
        "elsewhere, or revokes a clause about a DIFFERENT subject.",
    ),
    "deferred": _noul(
        _CONTEXTO + "`section` is ONE section (title and text) of that document. Regarding what `condition` asks for, "
        "does this section leave the decision open — neither granting nor denying it?",
        _SIM_ADIADO, _NAO_ADIADO,
    ),
}

# Desenho B — state {"condition", "document_type", "sections": [{"id", "title", "text"}, …]} (documento inteiro).
PERGUNTAS_DOCUMENTO = {
    "holds": _noul(
        _CONTEXTO + "`sections` is the WHOLE document, in order (id, title, text of every section). Read it to the end "
        "as a lawyer would: a later section (final provisions, a rectification before closing) may revoke, cancel or "
        "declare without effect what an earlier section granted, and what counts is what the document provides AT THE "
        "END. Does the document, as it stands at the end, provide what `condition` asks for? " + _REGRAS +
        " A clause granted in one section and revoked or declared without effect in a later one is NOT provided; a "
        "revocation of a clause on ANOTHER subject does not affect this condition.",
        _SIM_INSTITUI + " Nothing later in the document revokes or cancels it.",
        _NAO_INSTITUI + " Or: an earlier section provided it, but a later section revoked it or declared it without effect.",
    ),
    "deferred": _noul(
        _CONTEXTO + "`sections` is the WHOLE document, in order. Regarding what `condition` asks for, does the "
        "document leave the decision open — neither granting nor denying it?",
        _SIM_ADIADO, _NAO_ADIADO,
    ),
}
PROVA_NENHUMA = "none"


def pergunta_prova(ids_secoes: list[str]) -> dict:
    """Choice sobre os ids das seções (texto já no state → descrição `None`) + `none`: qual seção completa a prova?"""
    return {
        "type": "choice",
        "instructions": _CONTEXTO + "`sections` is the WHOLE document, in order. Which section is the one that proves "
        "— or completes the proof of — what `condition` asks for, as the document stands at the end? When the proof "
        "needs two sections, choose the one that completes it (the later one). If the document does not provide it, "
        f"or a later section revoked it, choose `{PROVA_NENHUMA}`.",
        "criteria": {**{i: None for i in ids_secoes}, PROVA_NENHUMA: "The document does not provide what the condition asks for."},
    }


def pergunta_parte_secao(i: int) -> dict:
    """Noul de UMA cláusula de condição composta (`condition_parts[i]`) sobre a seção; mesma leitura de `establishes`."""
    return _noul(
        _CONTEXTO + f"`condition_parts[{i}]` is ONE clause of the compound condition `condition` (the other clauses are "
        "judged separately). `section` is ONE section (title and text) of that document; the other sections are judged "
        f"separately and are not shown. Judging only by this section's text, does this section itself establish what the "
        f"clause `condition_parts[{i}]` asks for? " + _REGRAS,
        _SIM_INSTITUI, _NAO_INSTITUI,
    )


def pergunta_parte_documento(i: int) -> dict:
    """Noul de UMA cláusula (`condition_parts[i]`) sobre o documento inteiro; mesma leitura de `holds`."""
    return _noul(
        _CONTEXTO + f"`condition_parts[{i}]` is ONE clause of the compound condition `condition` (the other clauses are "
        "judged separately). `sections` is the WHOLE document, in order. Read it to the end as a lawyer would: a later "
        "section may revoke, cancel or declare without effect what an earlier section granted, and what counts is what "
        f"the document provides AT THE END. Does the document, as it stands at the end, provide what the clause "
        f"`condition_parts[{i}]` asks for? " + _REGRAS,
        _SIM_INSTITUI + " Nothing later in the document revokes or cancels it.",
        _NAO_INSTITUI + " Or: an earlier section provided it, but a later section revoked it or declared it without effect.",
    )


def perguntas_secao(partes: list[str]) -> dict:
    """As perguntas de uma requisição por seção: as três fixas e, se a condição é composta (regra 6 do LEIA-ME, achado 3
    do Codex), um Noul por cláusula. Condição simples = o mesmo dicionário da rodada 1 (cache intacto)."""
    q = dict(PERGUNTAS_SECAO)
    if len(partes) > 1:
        for i in range(len(partes)):
            q[f"establishes_part_{i}"] = pergunta_parte_secao(i)
    return q


def perguntas_documento(ids_secoes: list[str], partes: list[str] = ()) -> dict:
    q = {**PERGUNTAS_DOCUMENTO, "proving_section": pergunta_prova(ids_secoes)}
    if len(partes) > 1:
        for i in range(len(partes)):
            q[f"holds_part_{i}"] = pergunta_parte_documento(i)
    return q


# ---------------------------------------------------------------------------------------- política
# Três faixas por Noul: ≤ nao → falso; ≥ sim → verdadeiro; meio → indecidível (humano). Partida 0,2–0,8 (NÚCLEO §6);
# no ajuste as verdadeiras ficaram ≥ 0,85 (A: `establishes` da seção que prova p10 0,90; B: `holds` p10 0,87) e as
# falsas ≤ 0,15 (p90 A 0,03 / B 0,06), com as falsas de negada do B em 0,82–0,93 — o `sim` não desce.
FAIXA = {"establishes": (0.3, 0.8), "revokes": (0.4, 0.8), "holds": (0.3, 0.8)}
# `deferred` ≥ este valor com o documento `falso` = "deixa em aberto" → indecidível (regra 7 do LEIA-ME).
ADIADO_SIM = 0.7
# Desenho padrão (o critério vale para ele; o outro é medido nos mesmos dados): "mapa" (A) | "inteiro" (B).
DESENHO_PADRAO = "mapa"
# Faixa validada: seções de 60–200 palavras (≤ ~1.500 caracteres) e documentos de até 8 seções. Acima do teto a
# seção/documento NÃO vai ao Jev: `indecidivel` ("texto longo"). Não é limiar afinado.
TETO_CARACTERES = {"secao": 4000, "documento": 25000}
# Orçamento de requisições: no teste, 12 condições (8 semânticas) × 316 seções (A) + 44 documentos (B); numéricas não
# chamam. Previsão calculada pelo `run.py` ANTES de rodar; acima do teto, o teste é recusado.
ORCAMENTO = {"teste": 4500, "construcao_total": 9000}

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado em 2026-10-02 depois do ajuste e ANTES de abrir `dados/condicoes_teste.json`, para o DESENHO PADRÃO (A).
# Denominadores pela tabela do LEIA-ME (teste: 12 condições, 8 semânticas, 58 verdadeiros, 4 indecidíveis; famílias
# negada em T01/T08 e revogada em T02/T11). Métricas sobre os documentos DECIDÍVEIS (fora de `documentos_indecidiveis`)
# de todas as condições juntas (micro); documento mandado a humano fica fora de P/R/F1 e é contado à parte.
CRITERIO_CONTINUAR = {
    "onde": "no teste (12 condições × 44 documentos), desenho padrão `mapa` (A) com a política acima",
    "1_f1": "F1 do desenho padrão sobre os decidíveis decididos ≥ 0,90 e ≥ F1 do baseline (palavras-chave por seção) + 0,20",
    "2_perdidas": "documento verdadeiro do gabarito que saiu `falso` ≤ 5% dos verdadeiros",
    "3_negada_revogada": "documento falso marcado `verdadeiro` em condição das famílias negada/revogada ≤ 1",
    "4_humano": "decidíveis mandados a humano (`indecidivel`) ≤ 6%",
    "secundario_nao_decide": "seção que prova certa ≥ 80% dos verdadeiros das condições semânticas; indecidíveis do "
                             "gabarito que foram a humano ≥ 50%; falha operacional = 0; desenho B medido ao lado, com n",
    "se_falhar": "1 falhando = palavra-chave basta ou o Jev não lê a condição; 2 ou 3 = o mapa perde ou inverte o que "
                 "deveria achar (não serve sem mudança); 4 = custa humano demais",
    "limites": {"f1_min": 0.90, "margem_baseline": 0.20, "perdidas_max": 0.05, "fp_negada_revogada_max": 1,
                "humano_max": 0.06, "prova_min": 0.80, "indecidiveis_a_humano_min": 0.5},
}

# ---------------------------------------------------------------------------------------- baseline de código
# Palavras-chave por seção: radicais da condição (sem acento, minúsculas, fora das genéricas abaixo e dos nomes de
# tipo de documento, cortados na 5ª letra). Uma seção "bate" quando contém pelo menos METADE dos radicais; o documento
# é verdadeiro se alguma seção bate, e a seção que prova é a que mais radicais contém. Sem `indecidivel`: a busca por
# palavra não sabe que não sabe, nem lê negação ou revogação.
BASELINE_IGNORAR = {
    "documento", "documentos", "contrato", "contratos", "locacao", "prestacao", "servico", "servicos", "ata", "atas",
    "proposta", "propostas", "comercial", "assembleia", "condominio", "condominial", "registra", "registre", "preve",
    "contem", "clausula", "clausulas", "caso", "casos", "imovel", "parte", "partes", "que", "com", "sem", "para", "por",
    "pelo", "pela", "dos", "das", "nos", "nas", "aos", "ao", "no", "na", "de", "do", "da", "em", "ou", "e", "o", "a",
    "os", "as", "um", "uma", "se", "ja", "so", "ha", "qual", "quais", "cujo", "cuja", "sobre", "entre", "mais", "menos",
    "superior", "inferior", "igual", "doze", "meses", "dias", "ser", "sao", "foi", "esta", "este", "esse", "essa",
    "vale", "valor", "cargo", "outra", "outro", "outras", "outros", "sua", "seu", "suas", "seus",
}
BASELINE_CORTE = 5  # letras mantidas ("exclusividade" → "exclu", que também pega "exclusivamente")
