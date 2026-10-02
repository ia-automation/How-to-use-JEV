# Rascunho — compromisso-real (encanamento)

## Conjunto `rascunho` — 5 conversas, 10 candidatos (arquivo versão 2026-10-01, autor fable); 0 difíceis

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Por candidato — baseline × sempre compromisso × Jev (principal e informativas) nos mesmos casos

`acerto_total` = veredito exato (`revisar` conta como erro); `acerto_nao_compromisso` = só nos candidatos cujo gabarito não é `compromisso`. **TAREFA FANTASMA** = gabarito `proposta`/`cancelado`/`citacao_antiga`/`pedido_sem_aceite` que saiu `compromisso` (a dor: tarefa criada do nada). **COMPROMISSO PERDIDO** = gabarito `compromisso` que saiu `cancelado` ou `citacao_antiga` (tarefa real fechada). `compromisso → proposta/pedido` = compromisso enfraquecido (não cria tarefa; menos caro). `prazo certo` = data (ou nulo) igual ao gabarito entre os acertados. `sempre compromisso` = baseline trivial do LEIA-ME (prazo = primeira expressão com dia da conversa).

| variante | candidatos | acerto_total | acerto_nao_compromisso | TAREFA FANTASMA (não compromisso → compromisso) | COMPROMISSO PERDIDO (compromisso → cancelado/citação) | compromisso → proposta/pedido | revisar | prazo certo nos compromissos acertados | prazo certo nos vivos acertados |
|---|---|---|---|---|---|---|---|---|---|
| baseline (regex) | 10 | 1.000 | 1.000 | 0/5 | 0/5 | 0/5 | 0/10 | 5/5 | 7/8 |
| sempre compromisso | 10 | 0.500 | 0.000 | 5/5 | 0/5 | 0/5 | 0/10 | 2/5 | 2/5 |
| Jev choice | 10 | 1.000 | 1.000 | 0/5 | 0/5 | 0/5 | 0/10 | 5/5 | 8/8 |
| Jev nouls | 10 | 1.000 | 1.000 | 0/5 | 0/5 | 0/5 | 0/10 | 5/5 | 8/8 |
| Jev choice+nouls | 10 | 1.000 | 1.000 | 0/5 | 0/5 | 0/5 | 0/10 | 5/5 | 8/8 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 tarefa fantasma | 0/5 | ≤ 3 | ✓ |
| 2 compromisso perdido | 0/5 | ≤ 3 | ✓ |
| 3 prazo nos compromissos acertados | 5/5 (1.000) | ≥ 0.85 | ✓ |
| 4 acerto total | 1.000 (10) | ≥ 0.8 | ✓ |
| 5 acerto nos não-compromisso | 1.000 (5) | ≥ 0.7 | ✓ |
| secundário: revisar | 0/10 (0.000) | ≤ 0.15 | ✓ |
| secundário: prazo nos vivos acertados | 8/8 (1.000) | ≥ 0.85 | ✓ |

**Matriz de confusão — Jev choice** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 5/5 · `proposta` 2/2 · `cancelado` 1/1 · `citacao_antiga` 1/1 · `pedido_sem_aceite` 1/1

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 5 | 0 | 0 | 0 | 0 | 0 |
| proposta | 0 | 2 | 0 | 0 | 0 | 0 |
| cancelado | 0 | 0 | 1 | 0 | 0 | 0 |
| citacao_antiga | 0 | 0 | 0 | 1 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 1 | 0 |

**Matriz de confusão — Jev nouls** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 5/5 · `proposta` 2/2 · `cancelado` 1/1 · `citacao_antiga` 1/1 · `pedido_sem_aceite` 1/1

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 5 | 0 | 0 | 0 | 0 | 0 |
| proposta | 0 | 2 | 0 | 0 | 0 | 0 |
| cancelado | 0 | 0 | 1 | 0 | 0 | 0 |
| citacao_antiga | 0 | 0 | 0 | 1 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 1 | 0 |

**Matriz de confusão — Jev choice+nouls** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 5/5 · `proposta` 2/2 · `cancelado` 1/1 · `citacao_antiga` 1/1 · `pedido_sem_aceite` 1/1

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 5 | 0 | 0 | 0 | 0 | 0 |
| proposta | 0 | 2 | 0 | 0 | 0 | 0 |
| cancelado | 0 | 0 | 1 | 0 | 0 | 0 |
| citacao_antiga | 0 | 0 | 0 | 1 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 1 | 0 |

**Matriz de confusão — baseline (regex)** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 5/5 · `proposta` 2/2 · `cancelado` 1/1 · `citacao_antiga` 1/1 · `pedido_sem_aceite` 1/1

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 5 | 0 | 0 | 0 | 0 | 0 |
| proposta | 0 | 2 | 0 | 0 | 0 | 0 |
| cancelado | 0 | 0 | 1 | 0 | 0 | 0 |
| citacao_antiga | 0 | 0 | 0 | 1 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 1 | 0 |

### Choice de veredito — probabilidade do vencedor e da classe certa, por classe do gabarito

| gabarito | n | P(vencedor) mín–mediana–máx | P(classe certa) mín–mediana–máx | P(classe certa) < 0,5 |
|---|---|---|---|---|
| compromisso | 5 | 0.94–1.00–1.00 | 0.94–1.00–1.00 | 0 |
| proposta | 2 | 1.00–1.00–1.00 | 1.00–1.00–1.00 | 0 |
| cancelado | 1 | 1.00–1.00–1.00 | 1.00–1.00–1.00 | 0 |
| citacao_antiga | 1 | 1.00–1.00–1.00 | 1.00–1.00–1.00 | 0 |
| pedido_sem_aceite | 1 | 1.00–1.00–1.00 | 1.00–1.00–1.00 | 0 |

### Nouls informativos — valores por classe do gabarito (mín–máx, n) e faixa

| noul | faixa | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite |
|---|---|---|---|---|---|---|
| accepted | 0.3–0.7 | 0.91–0.98 (5) | 0.06–0.07 (2) | 0.67–0.67 (1) | 0.36–0.36 (1) | 0.04–0.04 (1) |
| undone | 0.3–0.7 | 0.05–0.11 (5) | 0.06–0.06 (2) | 0.97–0.97 (1) | 0.08–0.08 (1) | 0.06–0.06 (1) |
| quoted | 0.3–0.7 | 0.02–0.03 (5) | 0.02–0.02 (2) | 0.04–0.04 (1) | 0.87–0.87 (1) | 0.04–0.04 (1) |
| open_request | 0.3–0.7 | 0.03–0.08 (5) | 0.05–0.06 (2) | 0.08–0.08 (1) | 0.10–0.10 (1) | 0.93–0.93 (1) |

### Prazo — expressões lidas pelo código e escolha do Jev nos candidatos vivos do gabarito

`gabarito entre as expressões` = alguma expressão extraída resolve para a data do gabarito (cobertura do extrator, código); `escolha` = opção vencedora da Choice do prazo e sua probabilidade.

Cobertura do extrator: 8/8 candidatos vivos com o gabarito entre as expressões (ou gabarito nulo).

| id | k | gabarito | prazo gab. | n_expr | gabarito entre as expressões | escolha (P) | saiu | ok |
|---|---|---|---|---|---|---|---|---|
| CR-R001 | k1 | compromisso | 2026-10-07 | 2 | sim | m2: quarta (0.93) | 2026-10-07 | ✓ |
| CR-R001 | k2 | proposta | null | 2 | sim | none (0.77) | null | ✓ |
| CR-R002 | k1 | compromisso | 2026-10-07 | 3 | sim | m3: amanhã de manhã (0.96) | 2026-10-07 | ✓ |
| CR-R003 | k1 | compromisso | 2026-10-12 | 2 | sim | m2: segunda (0.99) | 2026-10-12 | ✓ |
| CR-R003 | k2 | pedido_sem_aceite | 2026-10-09 | 2 | sim | m1: sexta (1.00) | 2026-10-09 | ✓ |
| CR-R004 | k2 | compromisso | 2026-10-14 | 2 | sim | m2: hoje (0.85) | 2026-10-14 | ✓ |
| CR-R005 | k1 | proposta | null | 0 | sim | — | null | ✓ |
| CR-R005 | k2 | compromisso | null | 0 | sim | — | null | ✓ |

### Por família difícil (pela `nota` do rotulador) — acerto e erros caros, Jev principal × baseline

| família | conversas | candidatos | acerto Jev | acerto baseline | fantasma Jev | perdido Jev | revisar Jev | prazo ok Jev | fantasma baseline | perdido baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| fácil / outros | 5 | 10 | 1.000 | 1.000 | 0 | 0 | 0 | 8/8 | 0 | 0 |

### Curva da Choice principal — piso do vencedor (mesmas respostas; informativo no teste)

| piso do vencedor | cobertura (não revisar) | erro entre decididos | tarefa fantasma | compromisso perdido | acerto total |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 1.000 |
| 0.400 | 1.000 | 0.000 | 0 | 0 | 1.000 |
| 0.500 | 1.000 | 0.000 | 0 | 0 | 1.000 |
| 0.600 | 1.000 | 0.000 | 0 | 0 | 1.000 |
| 0.700 | 1.000 | 0.000 | 0 | 0 | 1.000 |
| 0.800 | 1.000 | 0.000 | 0 | 0 | 1.000 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | conversas longas (sem chamada) | falhas operacionais (→ revisar) | perguntas | p50_ms | p95_ms | tokens_por_conversa | US$_total | US$_por_1000_conversas | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | 0 | 0 | 58 | 340 | 366 | 9067 | 0.001904 | 0.3808 | jev-1.13.0 |

### Caso a caso (um candidato por linha)

`P` = probabilidade do vencedor da Choice de veredito; `acc/und/quo/opn` = Nouls `accepted`/`undone`/`quoted`/`open_request`; `ok` compara o veredito da variante principal com o gabarito; `caro` = tarefa fantasma, compromisso perdido ou prazo errado em compromisso acertado; `base` = baseline.

| id | fam | k | responsável | trecho | gab | Jev | P | acc/und/quo/opn | nouls→ | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CR-R001 | fácil / outros | k1 | Caio | subo até quarta | compromisso → 2026-10-07 | compromisso → 2026-10-07 | 1.00 | 0.98/0.07/0.02/0.03 | compromisso | ✓ |  | compromisso → 2026-10-07 | commitment P=1.00; prazo do próprio trecho 'm2: quarta' → 2026-10-07 (Jev apontou 'm2: quarta' P=0.93) |
| CR-R001 | fácil / outros | k2 | Dani | Posso revisar o PR se quiserem. | proposta | proposta | 1.00 | 0.06/0.06/0.02/0.05 | proposta | ✓ |  | proposta → 2026-10-07 | proposal P=1.00; prazo `none` P=0.77 |
| CR-R002 | fácil / outros | k1 | Hugo | Mando sim, amanhã de manhã. | compromisso → 2026-10-07 | compromisso → 2026-10-07 | 0.94 | 0.97/0.11/0.02/0.05 | compromisso | ✓ |  | compromisso → 2026-10-07 | commitment P=0.94; prazo do próprio trecho 'm3: amanhã de manhã' → 2026-10-07 (Jev apontou 'm3: amanhã de manhã' P=0.96) |
| CR-R002 | fácil / outros | k2 | Hugo | Fico de pedir o orçamento da gráfica hoje. | cancelado | cancelado | 1.00 | 0.67/0.97/0.04/0.08 | cancelado | ✓ |  | cancelado | cancelled P=1.00; sem prazo em cancelado |
| CR-R003 | fácil / outros | k1 | Aline | Eu envio o contrato revisado na segunda. | compromisso → 2026-10-12 | compromisso → 2026-10-12 | 1.00 | 0.93/0.06/0.03/0.08 | compromisso | ✓ |  | compromisso → 2026-10-12 | commitment P=1.00; prazo do próprio trecho 'm2: segunda' → 2026-10-12 (Jev apontou 'm2: segunda' P=0.99) |
| CR-R003 | fácil / outros | k2 | Vítor | pode entregar a planilha de custos na sexta? | pedido_sem_aceite → 2026-10-09 | pedido_sem_aceite → 2026-10-09 | 1.00 | 0.04/0.06/0.04/0.93 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-10-09 | unaccepted_request P=1.00; prazo do próprio trecho 'm1: sexta' → 2026-10-09 (Jev apontou 'm1: sexta' P=1.00) |
| CR-R004 | fácil / outros | k1 | Fábio | vocês prometeram o reembolso para o dia 20 | citacao_antiga | citacao_antiga | 1.00 | 0.36/0.08/0.87/0.10 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=1.00; sem prazo em citacao_antiga |
| CR-R004 | fácil / outros | k2 | Fábio | Eu ligo para ele hoje e explico. | compromisso → 2026-10-14 | compromisso → 2026-10-14 | 1.00 | 0.91/0.07/0.03/0.07 | compromisso | ✓ |  | compromisso → 2026-10-14 | commitment P=1.00; prazo do próprio trecho 'm2: hoje' → 2026-10-14 (Jev apontou 'm2: hoje' P=0.85) |
| CR-R005 | fácil / outros | k1 | Ivo | Eu poderia ajudar com os exemplos, se sobrar tempo | proposta | proposta | 1.00 | 0.07/0.06/0.02/0.06 | proposta | ✓ |  | proposta | proposal P=1.00; sem expressão de tempo na conversa |
| CR-R005 | fácil / outros | k2 | Helô | Pode deixar, faço isso. | compromisso | compromisso | 1.00 | 0.98/0.05/0.02/0.03 | compromisso | ✓ |  | compromisso | commitment P=1.00; sem expressão de tempo na conversa |
