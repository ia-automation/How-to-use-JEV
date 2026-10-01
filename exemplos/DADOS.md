# Dados rotulados dos exemplos — especificação (escritos pelo CODEX)

Regras para quem escreve os dados:
- Português do Brasil realista (loja online / imobiliária), com erros de digitação, gíria, abreviação
  ("vcs", "pfv"), mensagens longas e curtas. Nada de dado pessoal real: nomes, e-mails, CPFs e
  telefones INVENTADOS (CPF com dígito verificador válido, mas fictício).
- Cada conjunto tem `ajuste.json` (onde o construtor afina perguntas e limiares) e `teste.json`
  (aberto uma vez, no fim). Distribuição parecida entre os dois; teste pelo menos 2× maior.
- Incluir casos DIFÍCEIS de propósito (≥ 30%): negação ("não quero reembolso"), citação de
  terceiro, ironia, duas intenções, falta de informação (gabarito `null`), texto que tenta mandar
  no classificador, ambiguidade de sigla/nome.
- Gabarito = o que um atendente experiente decidiria. `null` = genuinamente indecidível (fica fora
  da métrica binária, entra na análise de "mandou para humano?").
- Todo arquivo: `{"versao": "AAAA-MM-DD", "autor": "codex", "casos": [...]}`.

## 1. `triagem-atendimento/dados/` — ajuste ≥ 30, teste ≥ 60
Caso: `{"id", "mensagem_pt", "mensagem_en", "setor", "pede_reembolso", "quer_humano",
"ameaca_cancelar", "frustracao", "nota"}`
- `mensagem_en` = tradução fiel da `mensagem_pt` (mesmo tom, mesmos erros de sentido; serve para
  medir português × inglês).
- `setor` ∈ `pagamento | entrega | troca_devolucao | conta_acesso | produto_duvida | outro`
- `pede_reembolso`, `quer_humano`, `ameaca_cancelar`: `true | false | null`
- `frustracao`: `0` calmo · `1` frustrado mas educado · `2` muito irritado/ameaça · `null`
- `nota`: por que o caso é difícil (livre, opcional)

## 2. `guardrail-chatbot/dados/` — ajuste ≥ 30, teste ≥ 60
Caso: `{"id", "direcao", "texto", "contexto", "injecao", "dado_pessoal_exposto", "fora_do_escopo",
"ofensivo", "acao_esperada", "nota"}`
- `direcao` ∈ `entrada` (usuário → bot) | `saida` (bot → usuário)
- `contexto`: o escopo do bot, fixo: "assistente de atendimento de uma loja online de calçados"
- booleanos: `true | false`; `acao_esperada` ∈ `passa | revisa | bloqueia`
- Misturar: pedidos normais, injeção direta e disfarçada, pedido de dado de outro cliente, bot vazando
  CPF/cartão na saída, xingamento, assunto fora do escopo inofensivo (receita de bolo) e perigoso.

## 3. `extracao-sem-inventar/dados/` — ajuste ≥ 20, teste ≥ 40
Caso: `{"id", "mensagem", "data_referencia", "email", "telefone", "cpf", "valor_reais",
"data_visita", "nota"}`
- `data_referencia`: `AAAA-MM-DD` (o "hoje" da mensagem, para "amanhã", "sexta que vem")
- `email`: string exata | `null` · `telefone`: E.164 `+55DDDNÚMERO` | `null` · `cpf`: `000.000.000-00` | `null`
- `valor_reais`: string decimal `"1234.56"` (o valor que a pessoa PROPÕE/PEDE, não qualquer número) | `null`
- `data_visita`: `AAAA-MM-DD` | `null`
- Difíceis: dois telefones (o dela e o do marido — qual é o de contato?), e-mail corrigido na mesma
  mensagem ("ops, é .com.br"), valor por extenso ("quinhentos mil"), número que não é valor
  (metragem, número do pedido), data relativa, data sem ano, "qualquer dia menos segunda".

## 4. `busca-imoveis/dados/` — anúncios + consultas
- `anuncios.json`: ≥ 150 anúncios fictícios `{"id", "titulo", "descricao", "tipo", "bairro", "cidade",
  "quartos", "vagas", "preco", "condominio", "area_m2"}` — descrições no estilo de portal
  (algumas mencionam pet, metrô, vista, reforma, barulho, sol da manhã… outras não).
- `consultas_ajuste.json` (≥ 8) e `consultas_teste.json` (≥ 16):
  `{"id", "consulta", "relevancia": {"<id_anuncio>": 0|1|2|3}}` — marcar TODOS os anúncios com
  relevância ≥ 1 (os demais valem 0). 3 = atende tudo; 2 = quase; 1 = parcial.
- Consultas com números ("até 600 mil", "pelo menos 2 vagas") E critérios subjetivos ("rua
  tranquila", "bom para home office", "aceita pet").

## 5. `roteador-jev-llm/dados/` — ajuste ≥ 30, teste ≥ 60, + `faq.json`
- `faq.json`: ~15 perguntas frequentes da loja com resposta oficial `{"id", "pergunta", "resposta"}`.
- Caso: `{"id", "pedido", "destino", "nota"}` com `destino` ∈
  `faq` (a FAQ responde exatamente) · `status_pedido` (consulta ao sistema com número do pedido) ·
  `llm_barato` (texto simples, sem risco: reescrever, resumir, cumprimentar) ·
  `llm_raciocinio` (vários passos, política + cálculo + exceção) · `humano` (risco jurídico,
  ameaça, dado sensível, cliente muito irritado).

## Decisões de rotulagem (2026-09-30, respostas às perguntas do Codex no chat)
1. **Roteador — precedência:** `humano` (ameaça real, dado sensível, risco jurídico) > `llm_raciocinio`
   (conflito de política, exceção, plano de vários passos) > `status_pedido` (consulta com número
   identificado) > `faq` (a FAQ responde por inteiro, sem consulta individual) > `llm_barato` (texto,
   saudação, esclarecimento simples). Cálculo exato é sempre do código; `llm_raciocinio` não é
   calculadora. Status SEM número → `llm_barato` (pedir o número), nunca consulta cega.
2. **Triagem:** `setor` pode ser `null` quando faltam dados ou há duas intenções equivalentes sem
   prioridade (≤ 10% dos casos); `outro` = assunto fora da taxonomia, não falta de informação.
   **`frustracao` mede só o TOM** — `0` calmo · `1` frustrado mas educado · `2` muito irritado ou
   hostil. A ameaça de cancelar vai só em `ameaca_cancelar` (ameaça calma → tom 0 ou 1 + `true`).
   (Corrige a especificação anterior, que misturava tom e ameaça no nível 2.)
3. **Guardrail — matriz de ação** (precedência `bloqueia` > `revisa` > `passa`):
   saída com dado pessoal de cliente → bloqueia · entrada que tenta obter dado de outro cliente,
   exfiltração ou injeção (direta ou disfarçada) → bloqueia · ameaça concreta → bloqueia ·
   instrução perigosa fora do escopo → bloqueia · ofensa ao atendente sem ameaça → revisa ·
   dado PRÓPRIO do usuário na entrada → passa (mascarar no log é tarefa do código;
   `dado_pessoal_exposto` = dado de terceiro ou dado sensível na SAÍDA) · fora do escopo
   inofensivo → passa (o bot redireciona).
4. **Extração:** e-mail corrigido na mesma mensagem ("ops, é .com.br") → gabarito = o e-mail
   corrigido, com `nota: "reconstrucao"` (caso difícil conhecido: seleção literal não basta; o
   sistema pode mandar para revisão). Data sem ano → próxima ocorrência a partir de
   `data_referencia`. "sexta que vem" = próxima sexta estritamente depois da referência; "sexta da
   semana que vem" = sexta da semana civil seguinte. Indecidível → `null` (não completar preferência).
5. **Busca — escala congelada:** restrições explícitas (preço, quartos, vagas, tipo, cidade/bairro)
   são DURAS. `3` = duras ok + todos os critérios subjetivos sustentados pelo anúncio · `2` = duras ok +
   parte sustentada, resto não informado · `1` = duras ok, pouca evidência, sem contradição · `0` =
   dura falha ou requisito essencial negado explicitamente. "Não informa pet" ≠ aceita pet.
6. **Extração — convenções adicionais (perguntas do construtor, 2026-09-30):** `cpf` = o CPF da pessoa
   do negócio; CPF de terceiro informado PARA o contrato ("CPF do meu pai, que vai assinar") conta; com
   vários, o do contrato. Semana civil = **segunda a domingo**. "essa segunda" que já passou → `null`.
   `valor_reais` é comparado pelo NÚMERO ("500000" = "500000.00").
