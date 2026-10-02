# Resultados — compromisso-real

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, política e critério: `perguntas.py`; state, expressões de tempo, validação, guarda de citação e baseline: `compromisso.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Variante principal: `choice`; piso do vencedor 0.5; piso do prazo 0.5; guarda de citação ligada; teto 4000 caracteres / 8 candidatos (acima → tudo `revisar`, sem chamada).

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (46 conversas, 102 candidatos), variante principal `choice` com a política acima; **variante_principal**: choice; **1_tarefa_fantasma**: candidato `proposta`, `cancelado`, `citacao_antiga` ou `pedido_sem_aceite` no gabarito que saiu `compromisso` ≤ 3 de 45; **2_compromisso_perdido**: candidato `compromisso` no gabarito que saiu `cancelado` ou `citacao_antiga` ≤ 3 de 57; **3_prazo_dos_compromissos**: entre os `compromisso` acertados, `prazo` igual ao gabarito (data ou nulo) ≥ 0,85; **4_acerto_total**: veredito exato nos 102 candidatos (`revisar` conta como erro) ≥ 0,80 (sempre-compromisso = 0,559); **5_acerto_nao_compromisso**: veredito exato nos 45 candidatos que não são `compromisso` ≥ 0,70; **secundario_nao_decide**: `revisar` ≤ 15% dos candidatos; `prazo` exato nos vivos acertados (compromisso/proposta/pedido) ≥ 0,85; baseline informativo; **se_falhar**: 1 ou 2 falhando = o desenho não serve para criar/fechar tarefa sem humano; 3, 4 ou 5 falhando = volta ao ajuste com dados novos

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T16:30:34-03:00; variante principal `choice`; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 6ee7f8a8524eeac8… · `compromisso.py` sha256 908e2b385fc624ec… · `run.py` sha256 ede2eb604d43f82c… · `dados/teste.json` sha256 2d603138083f3ea4…

## Lado a lado

### Por variante e conjunto

| conjunto | variante | candidatos | acerto_total | acerto_nao_compromisso | TAREFA FANTASMA (não compromisso → compromisso) | COMPROMISSO PERDIDO (compromisso → cancelado/citação) | compromisso → proposta/pedido | revisar | prazo certo nos compromissos acertados | prazo certo nos vivos acertados |
|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | baseline (regex) | 47 | 0.872 | 0.783 | 5/23 | 0/24 | 1/24 | 0/47 | 21/23 | 32/34 |
| ajuste | sempre compromisso | 47 | 0.511 | 0.000 | 23/23 | 0/24 | 0/24 | 0/47 | 10/24 | 10/24 |
| ajuste | Jev choice | 47 | 1.000 | 1.000 | 0/23 | 0/24 | 0/24 | 0/47 | 24/24 | 36/36 |
| ajuste | Jev nouls | 47 | 0.851 | 0.739 | 0/23 | 0/24 | 0/24 | 7/47 | 23/23 | 30/30 |
| ajuste | Jev choice+nouls | 47 | 1.000 | 1.000 | 0/23 | 0/24 | 0/24 | 0/47 | 24/24 | 36/36 |
| teste | baseline (regex) | 102 | 0.716 | 0.600 | 11/45 | 0/57 | 11/57 | 0/102 | 40/46 | 57/65 |
| teste | sempre compromisso | 102 | 0.559 | 0.000 | 45/45 | 0/57 | 0/57 | 0/102 | 27/57 | 27/57 |
| teste | Jev choice | 102 | 0.961 | 0.933 | 0/45 | 0/57 | 0/57 | 2/102 | 53/56 | 73/76 |
| teste | Jev nouls | 102 | 0.843 | 0.844 | 0/45 | 0/57 | 1/57 | 14/102 | 47/48 | 62/63 |
| teste | Jev choice+nouls | 102 | 0.971 | 0.956 | 0/45 | 0/57 | 1/57 | 0/102 | 53/56 | 73/76 |

### Custo

| conjunto | conversas | difíceis | candidatos | p50_ms | p95_ms | tokens_por_conversa | US$_por_1000 | cobertura do extrator de datas | modelo |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | 23 | 21 | 47 | 343 | 389 | 9517 | 0.3997 | 36/36 | jev-1.13.0 |
| teste | 46 | 43 | 102 | 339 | 414 | 10379 | 0.4359 | 78/78 | jev-1.13.0 |

## Conjunto `ajuste` — 23 conversas, 47 candidatos (arquivo versão 2026-10-01, autor fable); 21 difíceis

### Por candidato — baseline × sempre compromisso × Jev (principal e informativas) nos mesmos casos

`acerto_total` = veredito exato (`revisar` conta como erro); `acerto_nao_compromisso` = só nos candidatos cujo gabarito não é `compromisso`. **TAREFA FANTASMA** = gabarito `proposta`/`cancelado`/`citacao_antiga`/`pedido_sem_aceite` que saiu `compromisso` (a dor: tarefa criada do nada). **COMPROMISSO PERDIDO** = gabarito `compromisso` que saiu `cancelado` ou `citacao_antiga` (tarefa real fechada). `compromisso → proposta/pedido` = compromisso enfraquecido (não cria tarefa; menos caro). `prazo certo` = data (ou nulo) igual ao gabarito entre os acertados. `sempre compromisso` = baseline trivial do LEIA-ME (prazo = primeira expressão com dia da conversa).

| variante | candidatos | acerto_total | acerto_nao_compromisso | TAREFA FANTASMA (não compromisso → compromisso) | COMPROMISSO PERDIDO (compromisso → cancelado/citação) | compromisso → proposta/pedido | revisar | prazo certo nos compromissos acertados | prazo certo nos vivos acertados |
|---|---|---|---|---|---|---|---|---|---|
| baseline (regex) | 47 | 0.872 | 0.783 | 5/23 | 0/24 | 1/24 | 0/47 | 21/23 | 32/34 |
| sempre compromisso | 47 | 0.511 | 0.000 | 23/23 | 0/24 | 0/24 | 0/47 | 10/24 | 10/24 |
| Jev choice | 47 | 1.000 | 1.000 | 0/23 | 0/24 | 0/24 | 0/47 | 24/24 | 36/36 |
| Jev nouls | 47 | 0.851 | 0.739 | 0/23 | 0/24 | 0/24 | 7/47 | 23/23 | 30/30 |
| Jev choice+nouls | 47 | 1.000 | 1.000 | 0/23 | 0/24 | 0/24 | 0/47 | 24/24 | 36/36 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 tarefa fantasma | 0/23 | ≤ 3 | ✓ |
| 2 compromisso perdido | 0/24 | ≤ 3 | ✓ |
| 3 prazo nos compromissos acertados | 24/24 (1.000) | ≥ 0.85 | ✓ |
| 4 acerto total | 1.000 (47) | ≥ 0.8 | ✓ |
| 5 acerto nos não-compromisso | 1.000 (23) | ≥ 0.7 | ✓ |
| secundário: revisar | 0/47 (0.000) | ≤ 0.15 | ✓ |
| secundário: prazo nos vivos acertados | 36/36 (1.000) | ≥ 0.85 | ✓ |

**Matriz de confusão — Jev choice** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 24/24 · `proposta` 5/5 · `cancelado` 7/7 · `citacao_antiga` 4/4 · `pedido_sem_aceite` 7/7

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 24 | 0 | 0 | 0 | 0 | 0 |
| proposta | 0 | 5 | 0 | 0 | 0 | 0 |
| cancelado | 0 | 0 | 7 | 0 | 0 | 0 |
| citacao_antiga | 0 | 0 | 0 | 4 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 7 | 0 |

**Matriz de confusão — Jev nouls** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 23/24 · `proposta` 1/5 · `cancelado` 6/7 · `citacao_antiga` 4/4 · `pedido_sem_aceite` 6/7

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 23 | 0 | 0 | 0 | 0 | 1 |
| proposta | 0 | 1 | 0 | 0 | 0 | 4 |
| cancelado | 0 | 0 | 6 | 0 | 0 | 1 |
| citacao_antiga | 0 | 0 | 0 | 4 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 6 | 1 |

**Matriz de confusão — Jev choice+nouls** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 24/24 · `proposta` 5/5 · `cancelado` 7/7 · `citacao_antiga` 4/4 · `pedido_sem_aceite` 7/7

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 24 | 0 | 0 | 0 | 0 | 0 |
| proposta | 0 | 5 | 0 | 0 | 0 | 0 |
| cancelado | 0 | 0 | 7 | 0 | 0 | 0 |
| citacao_antiga | 0 | 0 | 0 | 4 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 7 | 0 |

**Matriz de confusão — baseline (regex)** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 23/24 · `proposta` 4/5 · `cancelado` 3/7 · `citacao_antiga` 4/4 · `pedido_sem_aceite` 7/7 · fantasma por classe {'cancelado': 4, 'proposta': 1}

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 23 | 0 | 0 | 0 | 1 | 0 |
| proposta | 1 | 4 | 0 | 0 | 0 | 0 |
| cancelado | 4 | 0 | 3 | 0 | 0 | 0 |
| citacao_antiga | 0 | 0 | 0 | 4 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 7 | 0 |

### Choice de veredito — probabilidade do vencedor e da classe certa, por classe do gabarito

| gabarito | n | P(vencedor) mín–mediana–máx | P(classe certa) mín–mediana–máx | P(classe certa) < 0,5 |
|---|---|---|---|---|
| compromisso | 24 | 0.92–1.00–1.00 | 0.92–1.00–1.00 | 0 |
| proposta | 5 | 0.97–1.00–1.00 | 0.97–1.00–1.00 | 0 |
| cancelado | 7 | 0.91–1.00–1.00 | 0.91–1.00–1.00 | 0 |
| citacao_antiga | 4 | 0.89–0.94–1.00 | 0.89–0.94–1.00 | 0 |
| pedido_sem_aceite | 7 | 1.00–1.00–1.00 | 1.00–1.00–1.00 | 0 |

### Nouls informativos — valores por classe do gabarito (mín–máx, n) e faixa

| noul | faixa | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite |
|---|---|---|---|---|---|---|
| accepted | 0.3–0.7 | 0.57–0.98 (24) | 0.05–0.51 (5) | 0.03–0.96 (7) | 0.34–0.89 (4) | 0.04–0.09 (7) |
| undone | 0.3–0.7 | 0.04–0.11 (24) | 0.05–0.34 (5) | 0.65–0.96 (7) | 0.17–0.46 (4) | 0.06–0.11 (7) |
| quoted | 0.3–0.7 | 0.02–0.05 (24) | 0.02–0.03 (5) | 0.02–0.05 (7) | 0.87–0.92 (4) | 0.03–0.07 (7) |
| open_request | 0.3–0.7 | 0.02–0.13 (24) | 0.07–0.22 (5) | 0.05–0.28 (7) | 0.07–0.10 (4) | 0.51–0.95 (7) |

### Prazo — expressões lidas pelo código e escolha do Jev nos candidatos vivos do gabarito

`gabarito entre as expressões` = alguma expressão extraída resolve para a data do gabarito (cobertura do extrator, código); `escolha` = opção vencedora da Choice do prazo e sua probabilidade.

Cobertura do extrator: 36/36 candidatos vivos com o gabarito entre as expressões (ou gabarito nulo).

| id | k | gabarito | prazo gab. | n_expr | gabarito entre as expressões | escolha (P) | saiu | ok |
|---|---|---|---|---|---|---|---|---|
| CR-A001 | k1 | compromisso | 2026-11-20 | 2 | sim | m2: sexta da semana que vem (1.00) | 2026-11-20 | ✓ |
| CR-A001 | k2 | compromisso | 2026-11-30 | 2 | sim | m4: Até o fim do mês (0.76) | 2026-11-30 | ✓ |
| CR-A002 | k1 | compromisso | 2026-10-07 | 2 | sim | m4: agora (0.84) | 2026-10-07 | ✓ |
| CR-A002 | k2 | proposta | null | 2 | sim | m2: sprint que vem (0.99) | null | ✓ |
| CR-A003 | k1 | pedido_sem_aceite | 2026-10-08 | 3 | sim | m1: amanhã (1.00) | 2026-10-08 | ✓ |
| CR-A003 | k2 | compromisso | 2026-10-07 | 3 | sim | m4: até o fim do dia (0.66) | 2026-10-07 | ✓ |
| CR-A004 | k1 | compromisso | 2026-10-16 | 2 | sim | m1: sexta (1.00) | 2026-10-16 | ✓ |
| CR-A005 | k1 | compromisso | 2026-10-15 | 3 | sim | m3: dia 15 (0.98) | 2026-10-15 | ✓ |
| CR-A006 | k1 | compromisso | 2026-12-30 | 2 | sim | m4: quarta (0.95) | 2026-12-30 | ✓ |
| CR-A006 | k2 | compromisso | 2027-01-04 | 2 | sim | m2: segunda, dia 4 (1.00) | 2027-01-04 | ✓ |
| CR-A007 | k1 | compromisso | 2026-11-30 | 3 | sim | m4: segunda (0.98) | 2026-11-30 | ✓ |
| CR-A007 | k2 | compromisso | null | 3 | sim | m2: próxima semana (0.93) | null | ✓ |
| CR-A008 | k1 | pedido_sem_aceite | 2026-12-11 | 2 | sim | m1: amanhã (0.99) | 2026-12-11 | ✓ |
| CR-A008 | k2 | proposta | null | 2 | sim | none (0.93) | null | ✓ |
| CR-A009 | k1 | compromisso | 2026-10-23 | 2 | sim | m1: amanhã (1.00) | 2026-10-23 | ✓ |
| CR-A009 | k2 | pedido_sem_aceite | null | 2 | sim | none (0.79) | null | ✓ |
| CR-A010 | k1 | compromisso | 2026-10-27 | 3 | sim | m3: terça (0.44) | 2026-10-27 | ✓ |
| CR-A010 | k2 | compromisso | 2026-10-30 | 3 | sim | m2: no dia 30 (0.87) | 2026-10-30 | ✓ |
| CR-A011 | k2 | pedido_sem_aceite | null | 1 | sim | none (0.96) | null | ✓ |
| CR-A012 | k1 | compromisso | 2026-10-13 | 2 | sim | m1: terça (0.78) | 2026-10-13 | ✓ |
| CR-A012 | k3 | compromisso | 2026-10-14 | 2 | sim | m4: quarta (0.96) | 2026-10-14 | ✓ |
| CR-A013 | k1 | proposta | 2026-10-29 | 4 | sim | m2: quinta (1.00) | 2026-10-29 | ✓ |
| CR-A013 | k2 | compromisso | 2026-10-27 | 4 | sim | m3: amanhã sem falta (1.00) | 2026-10-27 | ✓ |
| CR-A014 | k1 | proposta | null | 1 | sim | none (0.76) | null | ✓ |
| CR-A014 | k2 | compromisso | 2026-10-22 | 1 | sim | m1: quinta (1.00) | 2026-10-22 | ✓ |
| CR-A015 | k1 | pedido_sem_aceite | 2026-10-08 | 2 | sim | m1: quinta (1.00) | 2026-10-08 | ✓ |
| CR-A015 | k2 | compromisso | 2026-10-06 | 2 | sim | m3: à tarde (0.93) | 2026-10-06 | ✓ |
| CR-A016 | k1 | proposta | 2026-10-13 | 4 | sim | m2: terça (0.96) | 2026-10-13 | ✓ |
| CR-A016 | k2 | compromisso | 2026-10-08 | 4 | sim | m3: agora (0.76) | 2026-10-08 | ✓ |
| CR-A017 | k2 | compromisso | 2026-10-30 | 6 | sim | m2: amanhã até meio-dia (0.75) | 2026-10-30 | ✓ |
| CR-A018 | k2 | compromisso | 2026-10-05 | 2 | sim | m1: hoje (0.92) | 2026-10-05 | ✓ |
| CR-A019 | k1 | compromisso | 2026-10-09 | 3 | sim | m4: hoje (0.97) | 2026-10-09 | ✓ |
| CR-A020 | k1 | pedido_sem_aceite | 2026-11-10 | 2 | sim | m4: no dia 10 (0.98) | 2026-11-10 | ✓ |
| CR-A021 | k1 | pedido_sem_aceite | null | 2 | sim | none (1.00) | null | ✓ |
| CR-A022 | k1 | compromisso | 2026-10-19 | 3 | sim | m3: em até 3 dias úteis (0.98) | 2026-10-19 | ✓ |
| CR-A023 | k1 | compromisso | 2026-10-08 | 3 | sim | m4: quinta (1.00) | 2026-10-08 | ✓ |

### Por família difícil (pela `nota` do rotulador) — acerto e erros caros, Jev principal × baseline

| família | conversas | candidatos | acerto Jev | acerto baseline | fantasma Jev | perdido Jev | revisar Jev | prazo ok Jev | fantasma baseline | perdido baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| prazo | 3 | 6 | 1.000 | 1.000 | 0 | 0 | 0 | 6/6 | 0 | 0 |
| proposta × compromisso | 1 | 2 | 1.000 | 0.500 | 0 | 0 | 0 | 2/2 | 0 | 0 |
| pedido sem aceite | 2 | 4 | 1.000 | 1.000 | 0 | 0 | 0 | 4/4 | 0 | 0 |
| responsável ambíguo | 3 | 7 | 1.000 | 0.857 | 0 | 0 | 0 | 5/5 | 1 | 0 |
| citação antiga | 4 | 8 | 1.000 | 1.000 | 0 | 0 | 0 | 4/4 | 0 | 0 |
| aceite curto | 1 | 2 | 1.000 | 1.000 | 0 | 0 | 0 | 2/2 | 0 | 0 |
| cancelamento implícito | 3 | 6 | 1.000 | 0.667 | 0 | 0 | 0 | 3/3 | 2 | 0 |
| aceite condicional | 2 | 4 | 1.000 | 0.750 | 0 | 0 | 0 | 4/4 | 1 | 0 |
| oferta aceita | 1 | 2 | 1.000 | 1.000 | 0 | 0 | 0 | 2/2 | 0 | 0 |
| correção tardia | 1 | 2 | 1.000 | 1.000 | 0 | 0 | 0 | 1/1 | 0 | 0 |
| fácil / outros | 2 | 4 | 1.000 | 0.750 | 0 | 0 | 0 | 3/3 | 1 | 0 |

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
| 23 | 0 | 0 | 0 | 282 | 343 | 389 | 9517 | 0.009194 | 0.3997 | jev-1.13.0 |

### Caso a caso (um candidato por linha)

`P` = probabilidade do vencedor da Choice de veredito; `acc/und/quo/opn` = Nouls `accepted`/`undone`/`quoted`/`open_request`; `ok` compara o veredito da variante principal com o gabarito; `caro` = tarefa fantasma, compromisso perdido ou prazo errado em compromisso acertado; `base` = baseline.

| id | fam | k | responsável | trecho | gab | Jev | P | acc/und/quo/opn | nouls→ | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CR-A001 | prazo | k1 | Dani | Entrego na sexta da semana que vem. | compromisso → 2026-11-20 | compromisso → 2026-11-20 | 1.00 | 0.93/0.06/0.02/0.11 | compromisso | ✓ |  | compromisso → 2026-11-20 | commitment P=1.00; prazo do próprio trecho 'm2: sexta da semana que vem' → 2026-11-20 (Jev apontou 'm2: sexta da semana que vem' P=1.00) |
| CR-A001 | prazo | k2 | Dani | Até o fim do mês eu fecho. | compromisso → 2026-11-30 | compromisso → 2026-11-30 | 1.00 | 0.93/0.06/0.02/0.07 | compromisso | ✓ |  | compromisso → 2026-11-30 | commitment P=1.00; prazo do próprio trecho 'm4: Até o fim do mês' → 2026-11-30 (Jev apontou 'm4: Até o fim do mês' P=0.76) |
| CR-A002 | proposta × compromisso | k1 | Ivo | reinicia o serviço? | compromisso → 2026-10-07 | compromisso → 2026-10-07 | 0.96 | 0.94/0.05/0.03/0.03 | compromisso | ✓ |  | pedido_sem_aceite | commitment P=0.96; prazo 'm4: agora' P=0.84 → 2026-10-07 |
| CR-A002 | proposta × compromisso | k2 | Ivo | Que tal eu reescrever o worker na sprint que vem? | proposta | proposta | 1.00 | 0.07/0.34/0.03/0.09 | revisar | ✓ |  | proposta | proposal P=1.00; prazo do próprio trecho 'm2: sprint que vem' → sem dia (Jev apontou 'm2: sprint que vem' P=0.99) |
| CR-A003 | pedido sem aceite | k1 | Ígor | pode retornar para o cliente da clínica amanhã? | pedido_sem_aceite → 2026-10-08 | pedido_sem_aceite → 2026-10-08 | 1.00 | 0.08/0.06/0.03/0.93 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-10-08 | unaccepted_request P=1.00; prazo do próprio trecho 'm1: amanhã' → 2026-10-08 (Jev apontou 'm1: amanhã' P=1.00) |
| CR-A003 | pedido sem aceite | k2 | Nanda | Consigo, mando até o fim do dia. | compromisso → 2026-10-07 | compromisso → 2026-10-07 | 1.00 | 0.98/0.07/0.02/0.03 | compromisso | ✓ |  | compromisso → 2026-10-07 | commitment P=1.00; prazo do próprio trecho 'm4: até o fim do dia' → 2026-10-07 (Jev apontou 'm4: até o fim do dia' P=0.66) |
| CR-A004 | responsável ambíguo | k1 | Tati | Eu pego. | compromisso → 2026-10-16 | compromisso → 2026-10-16 | 1.00 | 0.87/0.10/0.03/0.05 | compromisso | ✓ |  | compromisso | commitment P=1.00; prazo 'm1: sexta' P=1.00 → 2026-10-16 |
| CR-A004 | responsável ambíguo | k2 | Hugo | Alguém precisa mandar o relatório de mídia pro cli | cancelado | cancelado | 0.91 | 0.03/0.80/0.05/0.28 | cancelado | ✓ |  | cancelado | cancelled P=0.91; sem prazo em cancelado |
| CR-A005 | citação antiga | k1 | Jonas | entrego dia 15 | compromisso → 2026-10-15 | compromisso → 2026-10-15 | 1.00 | 0.89/0.07/0.05/0.09 | compromisso | ✓ |  | compromisso → 2026-10-15 | commitment P=1.00; prazo do próprio trecho 'm3: dia 15' → 2026-10-15 (Jev apontou 'm3: dia 15' P=0.98) |
| CR-A005 | citação antiga | k2 | Jonas | Jonas ficou de entregar o manual da marca até dia  | citacao_antiga | citacao_antiga | 0.89 | 0.55/0.28/0.92/0.08 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=0.89; sem prazo em citacao_antiga |
| CR-A006 | prazo | k1 | Bia | Renovo na quarta. | compromisso → 2026-12-30 | compromisso → 2026-12-30 | 1.00 | 0.94/0.08/0.02/0.07 | compromisso | ✓ |  | compromisso → 2026-12-30 | commitment P=1.00; prazo do próprio trecho 'm4: quarta' → 2026-12-30 (Jev apontou 'm4: quarta' P=0.95) |
| CR-A006 | prazo | k2 | Bia | Faço na segunda, dia 4. | compromisso → 2027-01-04 | compromisso → 2027-01-04 | 1.00 | 0.94/0.05/0.03/0.08 | compromisso | ✓ |  | compromisso → 2027-01-04 | commitment P=1.00; prazo do próprio trecho 'm2: segunda, dia 4' → 2027-01-04 (Jev apontou 'm2: segunda, dia 4' P=1.00) |
| CR-A007 | prazo | k1 | Cris | Essa eu emito na segunda. | compromisso → 2026-11-30 | compromisso → 2026-11-30 | 1.00 | 0.94/0.07/0.03/0.09 | compromisso | ✓ |  | compromisso → 2026-11-30 | commitment P=1.00; prazo do próprio trecho 'm4: segunda' → 2026-11-30 (Jev apontou 'm4: segunda' P=0.98) |
| CR-A007 | prazo | k2 | Cris | Ficou para a próxima semana, te mando assim que re | compromisso | compromisso | 1.00 | 0.88/0.05/0.03/0.13 | compromisso | ✓ |  | compromisso | commitment P=1.00; prazo 'm2: próxima semana' P=0.93 → sem dia |
| CR-A008 | responsável ambíguo | k1 | Jonas | O Jonas manda o vídeo editado amanhã | pedido_sem_aceite → 2026-12-11 | pedido_sem_aceite → 2026-12-11 | 1.00 | 0.09/0.08/0.07/0.51 | revisar | ✓ |  | pedido_sem_aceite → 2026-12-11 | unaccepted_request P=1.00; prazo do próprio trecho 'm1: amanhã' → 2026-12-11 (Jev apontou 'm1: amanhã' P=0.99) |
| CR-A008 | responsável ambíguo | k2 | Lívia | eu aviso o cliente só depois que ele confirmar | proposta | proposta | 0.97 | 0.34/0.07/0.03/0.22 | revisar | ✓ |  | proposta | proposal P=0.97; prazo do próprio trecho 'm4: depois' → sem dia (Jev apontou 'none' P=0.93) |
| CR-A009 | aceite curto | k1 | Ivo | revisa o PR do checkout até amanhã? | compromisso → 2026-10-23 | compromisso → 2026-10-23 | 1.00 | 0.97/0.05/0.03/0.05 | compromisso | ✓ |  | compromisso → 2026-10-23 | commitment P=1.00; prazo do próprio trecho 'm1: amanhã' → 2026-10-23 (Jev apontou 'm1: amanhã' P=1.00) |
| CR-A009 | aceite curto | k2 | Helô | Helô, e os testes de carga? | pedido_sem_aceite | pedido_sem_aceite | 1.00 | 0.05/0.11/0.03/0.92 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite | unaccepted_request P=1.00; prazo `none` P=0.79 |
| CR-A010 | fácil / outros | k1 | Beto | Eu confiro os encargos antes, até terça. | compromisso → 2026-10-27 | compromisso → 2026-10-27 | 0.99 | 0.57/0.06/0.03/0.12 | revisar | ✓ |  | compromisso → 2026-10-27 | commitment P=0.99; prazo do próprio trecho 'm3: terça' → 2026-10-27 (Jev apontou 'm3: terça' P=0.44) |
| CR-A010 | fácil / outros | k2 | Cris | Envio no dia 30, combinado. | compromisso → 2026-10-30 | compromisso → 2026-10-30 | 0.99 | 0.97/0.07/0.03/0.03 | compromisso | ✓ |  | compromisso → 2026-10-30 | commitment P=0.99; prazo do próprio trecho 'm2: no dia 30' → 2026-10-30 (Jev apontou 'm2: no dia 30' P=0.87) |
| CR-A011 | cancelamento implícito | k1 | Dani | Olho, primeira coisa do dia. | cancelado | cancelado | 1.00 | 0.93/0.90/0.02/0.10 | cancelado | ✓ |  | compromisso → 2026-10-21 | cancelled P=1.00; sem prazo em cancelado |
| CR-A011 | cancelamento implícito | k2 | Dani | então pega o bug do filtro de datas, pode ser? | pedido_sem_aceite | pedido_sem_aceite | 1.00 | 0.07/0.07/0.03/0.91 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite | unaccepted_request P=1.00; prazo `none` P=0.96 |
| CR-A012 | responsável ambíguo | k1 | Jonas | Eu fecho o texto | compromisso → 2026-10-13 | compromisso → 2026-10-13 | 0.96 | 0.88/0.06/0.03/0.08 | compromisso | ✓ |  | compromisso | commitment P=0.96; prazo 'm1: terça' P=0.78 → 2026-10-13 |
| CR-A012 | responsável ambíguo | k2 | Jonas | A gente entrega a campanha revisada na terça. | cancelado | cancelado | 0.98 | 0.50/0.65/0.05/0.08 | revisar | ✓ |  | compromisso → 2026-10-13 | cancelled P=0.98; sem prazo em cancelado |
| CR-A012 | responsável ambíguo | k3 | Tati | as peças só na quarta | compromisso → 2026-10-14 | compromisso → 2026-10-14 | 0.98 | 0.76/0.06/0.03/0.12 | compromisso | ✓ |  | compromisso → 2026-10-14 | commitment P=0.98; prazo do próprio trecho 'm4: quarta' → 2026-10-14 (Jev apontou 'm4: quarta' P=0.96) |
| CR-A013 | aceite condicional | k1 | Vítor | Vou tentar protocolar na quinta | proposta → 2026-10-29 | proposta → 2026-10-29 | 0.99 | 0.51/0.07/0.03/0.19 | revisar | ✓ |  | proposta → 2026-10-29 | proposal P=0.99; prazo do próprio trecho 'm2: quinta' → 2026-10-29 (Jev apontou 'm2: quinta' P=1.00) |
| CR-A013 | aceite condicional | k2 | Aline | você me passa a procuração assinada amanhã sem fal | compromisso → 2026-10-27 | compromisso → 2026-10-27 | 1.00 | 0.97/0.04/0.02/0.03 | compromisso | ✓ |  | compromisso → 2026-10-27 | commitment P=1.00; prazo do próprio trecho 'm3: amanhã sem falta' → 2026-10-27 (Jev apontou 'm3: amanhã sem falta' P=1.00) |
| CR-A014 | oferta aceita | k1 | Fábio | Eu poderia gravar um vídeo também, mas não sei se  | proposta | proposta | 1.00 | 0.05/0.05/0.02/0.07 | proposta | ✓ |  | proposta | proposal P=1.00; prazo `none` P=0.76 |
| CR-A014 | oferta aceita | k2 | Duda | Posso mandar o passo a passo para o cliente na qui | compromisso → 2026-10-22 | compromisso → 2026-10-22 | 1.00 | 0.97/0.04/0.02/0.05 | compromisso | ✓ |  | compromisso → 2026-10-22 | commitment P=1.00; prazo do próprio trecho 'm1: quinta' → 2026-10-22 (Jev apontou 'm1: quinta' P=1.00) |
| CR-A015 | pedido sem aceite | k1 | Vítor | preciso da minuta do distrato até quinta | pedido_sem_aceite → 2026-10-08 | pedido_sem_aceite → 2026-10-08 | 1.00 | 0.07/0.07/0.04/0.92 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-10-08 | unaccepted_request P=1.00; prazo do próprio trecho 'm1: quinta' → 2026-10-08 (Jev apontou 'm1: quinta' P=1.00) |
| CR-A015 | pedido sem aceite | k2 | Aline | me lembra de cobrar ele à tarde? | compromisso → 2026-10-06 | compromisso → 2026-10-06 | 1.00 | 0.96/0.04/0.03/0.02 | compromisso | ✓ |  | compromisso → 2026-10-06 | commitment P=1.00; prazo do próprio trecho 'm3: à tarde' → 2026-10-06 (Jev apontou 'm3: à tarde' P=0.93) |
| CR-A016 | aceite condicional | k1 | Cris | fecho na terça | proposta → 2026-10-13 | proposta → 2026-10-13 | 1.00 | 0.50/0.05/0.03/0.10 | revisar | ✓ |  | compromisso → 2026-10-13 | proposal P=1.00; prazo do próprio trecho 'm2: terça' → 2026-10-13 (Jev apontou 'm2: terça' P=0.96) |
| CR-A016 | aceite condicional | k2 | Beto | vou cobrar os extratos dele agora | compromisso → 2026-10-08 | compromisso → 2026-10-08 | 0.99 | 0.90/0.05/0.02/0.06 | compromisso | ✓ |  | compromisso → 2026-10-08 | commitment P=0.99; prazo do próprio trecho 'm3: agora' → 2026-10-08 (Jev apontou 'm3: agora' P=0.76) |
| CR-A017 | citação antiga | k1 | Hugo | entrego o roteiro na quarta | citacao_antiga | citacao_antiga | 0.94 | 0.89/0.46/0.87/0.07 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=0.94; sem prazo em citacao_antiga |
| CR-A017 | citação antiga | k2 | Hugo | Entrego amanhã até meio-dia. | compromisso → 2026-10-30 | compromisso → 2026-10-30 | 1.00 | 0.97/0.05/0.02/0.06 | compromisso | ✓ |  | compromisso → 2026-10-30 | commitment P=1.00; prazo do próprio trecho 'm2: amanhã até meio-dia' → 2026-10-30 (Jev apontou 'm2: amanhã até meio-dia' P=0.75) |
| CR-A018 | cancelamento implícito | k1 | Fábio | Respondo depois do almoço. | cancelado | cancelado | 1.00 | 0.38/0.95/0.03/0.24 | cancelado | ✓ |  | cancelado | cancelled P=1.00; sem prazo em cancelado |
| CR-A018 | cancelamento implícito | k2 | Paula | Deixa que eu respondo, já estou com o histórico ab | compromisso → 2026-10-05 | compromisso → 2026-10-05 | 1.00 | 0.97/0.06/0.02/0.04 | compromisso | ✓ |  | compromisso → 2026-10-05 | commitment P=1.00; prazo 'm1: hoje' P=0.92 → 2026-10-05 |
| CR-A019 | cancelamento implícito | k1 | Leo | eu aviso o time de infra hoje | compromisso → 2026-10-09 | compromisso → 2026-10-09 | 0.92 | 0.90/0.07/0.03/0.06 | compromisso | ✓ |  | compromisso → 2026-10-09 | commitment P=0.92; prazo do próprio trecho 'm4: hoje' → 2026-10-09 (Jev apontou 'm4: hoje' P=0.97) |
| CR-A019 | cancelamento implícito | k2 | Bia | Migro, segunda cedo. | cancelado | cancelado | 1.00 | 0.96/0.95/0.03/0.05 | cancelado | ✓ |  | compromisso → 2026-10-12 | cancelled P=1.00; sem prazo em cancelado |
| CR-A020 | fácil / outros | k1 | Ígor | consegue ir lá no dia 10? | pedido_sem_aceite → 2026-11-10 | pedido_sem_aceite → 2026-11-10 | 1.00 | 0.04/0.06/0.03/0.90 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-11-10 | unaccepted_request P=1.00; prazo do próprio trecho 'm4: no dia 10' → 2026-11-10 (Jev apontou 'm4: no dia 10' P=0.98) |
| CR-A020 | fácil / outros | k2 | Nanda | você liga para a escola hoje para agendar a visita | cancelado | cancelado | 1.00 | 0.92/0.96/0.03/0.12 | cancelado | ✓ |  | compromisso → 2026-11-03 | cancelled P=1.00; sem prazo em cancelado |
| CR-A021 | citação antiga | k1 | Caio | que tal você atualizar a documentação da v2? | pedido_sem_aceite | pedido_sem_aceite | 1.00 | 0.04/0.08/0.03/0.95 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite | unaccepted_request P=1.00; prazo `none` P=1.00 |
| CR-A021 | citação antiga | k2 | Leo | Leo ficou de remover o endpoint v1 até setembro | citacao_antiga | citacao_antiga | 0.93 | 0.70/0.36/0.92/0.07 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=0.93; sem prazo em citacao_antiga |
| CR-A022 | citação antiga | k1 | Ígor | Retorno para ele em até 3 dias úteis com a solução | compromisso → 2026-10-19 | compromisso → 2026-10-19 | 1.00 | 0.95/0.11/0.04/0.06 | compromisso | ✓ |  | compromisso → 2026-10-19 | commitment P=1.00; prazo do próprio trecho 'm3: em até 3 dias úteis' → 2026-10-19 (Jev apontou 'm3: em até 3 dias úteis' P=0.98) |
| CR-A022 | citação antiga | k2 | Ígor | nossa equipe retornará em até 2 dias úteis | citacao_antiga | citacao_antiga | 1.00 | 0.34/0.17/0.87/0.10 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=1.00; sem prazo em citacao_antiga |
| CR-A023 | correção tardia | k1 | Caio | Mando na quinta, pode ser? | compromisso → 2026-10-08 | compromisso → 2026-10-08 | 0.99 | 0.96/0.05/0.02/0.05 | compromisso | ✓ |  | compromisso → 2026-10-08 | commitment P=0.99; prazo do próprio trecho 'm4: quinta' → 2026-10-08 (Jev apontou 'm4: quinta' P=1.00) |
| CR-A023 | correção tardia | k2 | Caio | Mando na quarta. | cancelado | cancelado | 1.00 | 0.92/0.96/0.02/0.06 | cancelado | ✓ |  | cancelado | cancelled P=1.00; sem prazo em cancelado |

## Conjunto `teste` — 46 conversas, 102 candidatos (arquivo versão 2026-10-01, autor fable); 43 difíceis

### Por candidato — baseline × sempre compromisso × Jev (principal e informativas) nos mesmos casos

`acerto_total` = veredito exato (`revisar` conta como erro); `acerto_nao_compromisso` = só nos candidatos cujo gabarito não é `compromisso`. **TAREFA FANTASMA** = gabarito `proposta`/`cancelado`/`citacao_antiga`/`pedido_sem_aceite` que saiu `compromisso` (a dor: tarefa criada do nada). **COMPROMISSO PERDIDO** = gabarito `compromisso` que saiu `cancelado` ou `citacao_antiga` (tarefa real fechada). `compromisso → proposta/pedido` = compromisso enfraquecido (não cria tarefa; menos caro). `prazo certo` = data (ou nulo) igual ao gabarito entre os acertados. `sempre compromisso` = baseline trivial do LEIA-ME (prazo = primeira expressão com dia da conversa).

| variante | candidatos | acerto_total | acerto_nao_compromisso | TAREFA FANTASMA (não compromisso → compromisso) | COMPROMISSO PERDIDO (compromisso → cancelado/citação) | compromisso → proposta/pedido | revisar | prazo certo nos compromissos acertados | prazo certo nos vivos acertados |
|---|---|---|---|---|---|---|---|---|---|
| baseline (regex) | 102 | 0.716 | 0.600 | 11/45 | 0/57 | 11/57 | 0/102 | 40/46 | 57/65 |
| sempre compromisso | 102 | 0.559 | 0.000 | 45/45 | 0/57 | 0/57 | 0/102 | 27/57 | 27/57 |
| Jev choice | 102 | 0.961 | 0.933 | 0/45 | 0/57 | 0/57 | 2/102 | 53/56 | 73/76 |
| Jev nouls | 102 | 0.843 | 0.844 | 0/45 | 0/57 | 1/57 | 14/102 | 47/48 | 62/63 |
| Jev choice+nouls | 102 | 0.971 | 0.956 | 0/45 | 0/57 | 1/57 | 0/102 | 53/56 | 73/76 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 tarefa fantasma | 0/45 | ≤ 3 | ✓ |
| 2 compromisso perdido | 0/57 | ≤ 3 | ✓ |
| 3 prazo nos compromissos acertados | 53/56 (0.946) | ≥ 0.85 | ✓ |
| 4 acerto total | 0.961 (102) | ≥ 0.8 | ✓ |
| 5 acerto nos não-compromisso | 0.933 (45) | ≥ 0.7 | ✓ |
| secundário: revisar | 2/102 (0.020) | ≤ 0.15 | ✓ |
| secundário: prazo nos vivos acertados | 73/76 (0.961) | ≥ 0.85 | ✓ |

**Matriz de confusão — Jev choice** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 56/57 · `proposta` 10/10 · `cancelado` 15/17 · `citacao_antiga` 7/7 · `pedido_sem_aceite` 10/11

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 56 | 0 | 0 | 0 | 0 | 1 |
| proposta | 0 | 10 | 0 | 0 | 0 | 0 |
| cancelado | 0 | 0 | 15 | 0 | 1 | 1 |
| citacao_antiga | 0 | 0 | 0 | 7 | 0 | 0 |
| pedido_sem_aceite | 0 | 1 | 0 | 0 | 10 | 0 |

**Matriz de confusão — Jev nouls** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 48/57 · `proposta` 6/10 · `cancelado` 16/17 · `citacao_antiga` 7/7 · `pedido_sem_aceite` 9/11

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 48 | 1 | 0 | 0 | 0 | 8 |
| proposta | 0 | 6 | 0 | 0 | 0 | 4 |
| cancelado | 0 | 0 | 16 | 0 | 1 | 0 |
| citacao_antiga | 0 | 0 | 0 | 7 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 9 | 2 |

**Matriz de confusão — Jev choice+nouls** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 56/57 · `proposta` 10/10 · `cancelado` 16/17 · `citacao_antiga` 7/7 · `pedido_sem_aceite` 10/11

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 56 | 1 | 0 | 0 | 0 | 0 |
| proposta | 0 | 10 | 0 | 0 | 0 | 0 |
| cancelado | 0 | 0 | 16 | 0 | 1 | 0 |
| citacao_antiga | 0 | 0 | 0 | 7 | 0 | 0 |
| pedido_sem_aceite | 0 | 1 | 0 | 0 | 10 | 0 |

**Matriz de confusão — baseline (regex)** (linhas = gabarito, colunas = previsto) · por classe: `compromisso` 46/57 · `proposta` 8/10 · `cancelado` 1/17 · `citacao_antiga` 7/7 · `pedido_sem_aceite` 11/11 · fantasma por classe {'cancelado': 9, 'proposta': 2}

| gabarito ↓ / previsto → | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite | revisar |
|---|---|---|---|---|---|---|
| compromisso | 46 | 2 | 0 | 0 | 9 | 0 |
| proposta | 2 | 8 | 0 | 0 | 0 | 0 |
| cancelado | 9 | 1 | 1 | 0 | 6 | 0 |
| citacao_antiga | 0 | 0 | 0 | 7 | 0 | 0 |
| pedido_sem_aceite | 0 | 0 | 0 | 0 | 11 | 0 |

### Choice de veredito — probabilidade do vencedor e da classe certa, por classe do gabarito

| gabarito | n | P(vencedor) mín–mediana–máx | P(classe certa) mín–mediana–máx | P(classe certa) < 0,5 |
|---|---|---|---|---|
| compromisso | 57 | 0.47–1.00–1.00 | 0.43–1.00–1.00 | 1 |
| proposta | 10 | 0.96–1.00–1.00 | 0.96–1.00–1.00 | 0 |
| cancelado | 17 | 0.47–0.99–1.00 | 0.17–0.99–1.00 | 2 |
| citacao_antiga | 7 | 0.77–0.98–1.00 | 0.77–0.98–1.00 | 0 |
| pedido_sem_aceite | 11 | 0.61–0.99–1.00 | 0.22–0.99–1.00 | 1 |

### Nouls informativos — valores por classe do gabarito (mín–máx, n) e faixa

| noul | faixa | compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite |
|---|---|---|---|---|---|---|
| accepted | 0.3–0.7 | 0.09–0.98 (57) | 0.05–0.55 (10) | 0.03–0.95 (17) | 0.05–0.84 (7) | 0.02–0.12 (11) |
| undone | 0.3–0.7 | 0.03–0.26 (57) | 0.05–0.26 (10) | 0.54–0.97 (17) | 0.06–0.92 (7) | 0.05–0.43 (11) |
| quoted | 0.3–0.7 | 0.02–0.10 (57) | 0.02–0.05 (10) | 0.03–0.09 (17) | 0.79–0.94 (7) | 0.03–0.04 (11) |
| open_request | 0.3–0.7 | 0.02–0.32 (57) | 0.05–0.56 (10) | 0.05–0.82 (17) | 0.08–0.27 (7) | 0.51–0.93 (11) |

### Prazo — expressões lidas pelo código e escolha do Jev nos candidatos vivos do gabarito

`gabarito entre as expressões` = alguma expressão extraída resolve para a data do gabarito (cobertura do extrator, código); `escolha` = opção vencedora da Choice do prazo e sua probabilidade.

Cobertura do extrator: 78/78 candidatos vivos com o gabarito entre as expressões (ou gabarito nulo).

| id | k | gabarito | prazo gab. | n_expr | gabarito entre as expressões | escolha (P) | saiu | ok |
|---|---|---|---|---|---|---|---|---|
| CR-T001 | k1 | compromisso | 2026-10-06 | 1 | sim | m1: amanhã (0.93) | 2026-10-06 | ✓ |
| CR-T002 | k1 | compromisso | null | 2 | sim | m2: semana que vem (0.64) | null | ✓ |
| CR-T002 | k2 | compromisso | 2026-11-30 | 2 | sim | m4: segunda (0.98) | 2026-11-30 | ✓ |
| CR-T003 | k1 | compromisso | 2027-01-01 | 3 | sim | m2: sexta (0.92) | 2027-01-01 | ✓ |
| CR-T003 | k2 | compromisso | 2027-01-02 | 3 | sim | m4: no dia 2 (0.99) | 2027-01-02 | ✓ |
| CR-T004 | k1 | compromisso | 2026-10-22 | 3 | sim | m1: hoje (0.76) | 2026-10-22 | ✓ |
| CR-T004 | k2 | compromisso | 2026-10-23 | 3 | sim | m3: amanhã (0.89) | 2026-10-23 | ✓ |
| CR-T005 | k2 | compromisso | 2026-12-16 | 4 | sim | m4: quarta (0.91) | 2026-12-16 | ✓ |
| CR-T006 | k1 | compromisso | 2026-10-07 | 4 | sim | m3: depois de amanhã (0.64) | 2026-10-07 | ✓ |
| CR-T007 | k1 | compromisso | 2026-12-16 | 6 | sim | m1: até dia 16 (0.76) | 2026-12-16 | ✓ |
| CR-T007 | k2 | pedido_sem_aceite | 2026-12-16 | 6 | sim | m4: para o dia 16 (0.92) | 2026-12-16 | ✓ |
| CR-T008 | k1 | compromisso | 2026-11-06 | 2 | sim | m3: sexta (0.67) | 2026-11-06 | ✓ |
| CR-T009 | k1 | compromisso | null | 3 | sim | m2: Assim que fechar (0.57) | null | ✓ |
| CR-T009 | k2 | compromisso | 2026-10-28 | 3 | sim | m4: em 2 dias (0.97) | 2026-10-28 | ✓ |
| CR-T010 | k1 | compromisso | 2026-10-12 | 1 | sim | m2: até o dia 12 (1.00) | 2026-10-12 | ✓ |
| CR-T010 | k2 | compromisso | 2026-10-12 | 1 | sim | m2: até o dia 12 (0.98) | 2026-10-12 | ✓ |
| CR-T011 | k1 | pedido_sem_aceite | 2026-10-06 | 2 | sim | m1: hoje (0.97) | 2026-10-06 | ✓ |
| CR-T011 | k2 | pedido_sem_aceite | 2026-10-06 | 2 | sim | m1: hoje (0.97) | 2026-10-06 | ✓ |
| CR-T012 | k1 | compromisso | 2026-10-28 | 3 | sim | m4: no dia 28 (0.98) | 2026-10-28 | ✓ |
| CR-T013 | k2 | compromisso | 2026-10-07 | 3 | sim | m3: quinta (0.78) | 2026-10-08 | ✗ |
| CR-T013 | k3 | compromisso | 2026-10-08 | 3 | sim | m3: quinta (1.00) | 2026-10-08 | ✓ |
| CR-T014 | k1 | compromisso | 2026-10-23 | 4 | sim | m2: sexta (0.58) | 2026-10-23 | ✓ |
| CR-T014 | k3 | compromisso | null | 4 | sim | m3: sexta (0.57) | 2026-10-23 | ✗ |
| CR-T015 | k2 | proposta | 2026-11-16 | 5 | sim | m4: segunda (0.93) | 2026-11-16 | ✓ |
| CR-T015 | k3 | compromisso | 2026-11-13 | 5 | sim | m3: amanhã cedo (0.73) | 2026-11-13 | ✓ |
| CR-T016 | k1 | compromisso | 2026-10-06 | 4 | sim | m4: hoje (0.81) | 2026-10-06 | ✓ |
| CR-T017 | k1 | pedido_sem_aceite | 2026-12-14 | 5 | sim | m1: segunda (0.90) | 2026-12-14 | ✓ |
| CR-T017 | k2 | pedido_sem_aceite | null | 5 | sim | m3: este mês (0.95) | null | ✓ |
| CR-T017 | k3 | proposta | null | 5 | sim | m3: este mês (0.87) | null | ✓ |
| CR-T018 | k1 | compromisso | 2026-10-28 | 3 | sim | m1: amanhã (0.59) | 2026-10-27 | ✗ |
| CR-T018 | k2 | pedido_sem_aceite | 2026-10-27 | 3 | sim | m1: amanhã (0.99) | 2026-10-27 | ✓ |
| CR-T019 | k1 | pedido_sem_aceite | 2026-11-05 | 2 | sim | m1: quinta (0.99) | 2026-11-05 | ✓ |
| CR-T019 | k2 | pedido_sem_aceite | null | 2 | sim | none (0.97) | null | ✓ |
| CR-T020 | k1 | pedido_sem_aceite | null | 2 | sim | none (0.98) | null | ✓ |
| CR-T021 | k1 | proposta | 2026-11-07 | 5 | sim | m4: sábado (0.50) | 2026-11-07 | ✓ |
| CR-T021 | k2 | compromisso | 2026-11-06 | 5 | sim | m2: sexta (0.95) | 2026-11-06 | ✓ |
| CR-T022 | k1 | pedido_sem_aceite | 2026-10-08 | 2 | sim | m1: amanhã (0.99) | 2026-10-08 | ✓ |
| CR-T022 | k2 | compromisso | 2026-10-07 | 2 | sim | m1: amanhã (0.55) | null | ✗ |
| CR-T023 | k1 | compromisso | 2026-10-26 | 4 | sim | m4: segunda (0.81) | 2026-10-26 | ✓ |
| CR-T023 | k2 | compromisso | 2026-10-28 | 4 | sim | m4: quarta (0.97) | 2026-10-28 | ✓ |
| CR-T024 | k2 | compromisso | 2026-10-22 | 3 | sim | m4: quinta (0.47) | 2026-10-22 | ✓ |
| CR-T026 | k2 | compromisso | 2026-10-13 | 3 | sim | m4: terça (1.00) | 2026-10-13 | ✓ |
| CR-T027 | k1 | compromisso | 2026-10-07 | 6 | sim | m3: Quarta (0.50) | 2026-10-07 | ✓ |
| CR-T028 | k1 | compromisso | 2026-11-20 | 4 | sim | m5: até dia 20 (1.00) | 2026-11-20 | ✓ |
| CR-T029 | k1 | compromisso | 2026-11-05 | 3 | sim | m1: quinta (0.55) | 2026-11-05 | ✓ |
| CR-T029 | k2 | compromisso | 2026-11-04 | 3 | sim | m4: quarta à noite (0.96) | 2026-11-04 | ✓ |
| CR-T030 | k1 | compromisso | 2026-10-19 | 2 | sim | m5: Segunda (1.00) | 2026-10-19 | ✓ |
| CR-T030 | k3 | compromisso | 2026-10-16 | 2 | sim | m1: sexta (1.00) | 2026-10-16 | ✓ |
| CR-T031 | k1 | pedido_sem_aceite | 2026-10-23 | 3 | sim | m3: amanhã cedo (0.85) | 2026-10-23 | ✓ |
| CR-T031 | k2 | compromisso | 2026-10-22 | 3 | sim | m1: hoje à noite (0.99) | 2026-10-22 | ✓ |
| CR-T032 | k1 | compromisso | 2026-10-23 | 1 | sim | m4: até o fim da semana (1.00) | 2026-10-23 | ✓ |
| CR-T032 | k2 | proposta | null | 1 | sim | none (0.98) | null | ✓ |
| CR-T033 | k2 | compromisso | 2026-12-01 | 3 | sim | m4: terça (1.00) | 2026-12-01 | ✓ |
| CR-T034 | k1 | compromisso | 2026-12-15 | 3 | sim | m5: terça (0.83) | 2026-12-15 | ✓ |
| CR-T034 | k2 | compromisso | 2026-12-14 | 3 | sim | m1: segunda (0.94) | 2026-12-14 | ✓ |
| CR-T035 | k2 | compromisso | 2026-10-29 | 3 | sim | m5: hoje mesmo (0.99) | 2026-10-29 | ✓ |
| CR-T036 | k1 | proposta | 2026-10-30 | 2 | sim | m4: sexta (1.00) | 2026-10-30 | ✓ |
| CR-T037 | k2 | proposta | null | 3 | sim | m1: terça (0.61) | null | ✓ |
| CR-T037 | k3 | compromisso | 2026-10-29 | 3 | sim | m1: terça (0.56) | 2026-10-29 | ✓ |
| CR-T038 | k1 | compromisso | 2026-10-10 | 3 | sim | m1: sábado (0.81) | 2026-10-10 | ✓ |
| CR-T038 | k2 | compromisso | 2026-10-12 | 3 | sim | m3: segunda (0.99) | 2026-10-12 | ✓ |
| CR-T039 | k1 | compromisso | 2026-10-28 | 3 | sim | m4: quarta (0.95) | 2026-10-28 | ✓ |
| CR-T039 | k2 | compromisso | 2026-10-28 | 3 | sim | m4: quarta (0.55) | 2026-10-28 | ✓ |
| CR-T040 | k1 | compromisso | 2026-11-30 | 2 | sim | m2: até o fim do mês (0.96) | 2026-11-30 | ✓ |
| CR-T040 | k2 | compromisso | 2026-12-05 | 2 | sim | m4: no dia 5 (0.99) | 2026-12-05 | ✓ |
| CR-T041 | k1 | compromisso | 2026-10-16 | 3 | sim | m1: sexta (1.00) | 2026-10-16 | ✓ |
| CR-T041 | k2 | compromisso | 2026-10-15 | 3 | sim | m3: amanhã (0.88) | 2026-10-15 | ✓ |
| CR-T041 | k3 | proposta | null | 3 | sim | none (1.00) | null | ✓ |
| CR-T042 | k1 | proposta | null | 3 | sim | m3: Um dia (0.56) | null | ✓ |
| CR-T042 | k2 | proposta | null | 3 | sim | none (0.59) | null | ✓ |
| CR-T042 | k3 | compromisso | 2026-10-09 | 3 | sim | m5: sexta (0.88) | 2026-10-09 | ✓ |
| CR-T043 | k1 | proposta | 2026-11-16 | 3 | sim | m1: segunda (0.65) | 2026-11-16 | ✓ |
| CR-T043 | k2 | compromisso | 2026-11-13 | 3 | sim | m5: amanhã cedo (0.99) | 2026-11-13 | ✓ |
| CR-T044 | k2 | compromisso | 2026-10-16 | 2 | sim | m3: em 2 dias úteis (0.99) | 2026-10-16 | ✓ |
| CR-T045 | k1 | compromisso | 2026-10-09 | 4 | sim | m4: amanhã (0.85) | 2026-10-09 | ✓ |
| CR-T045 | k2 | compromisso | 2026-10-09 | 4 | sim | m2: amanhã (0.67) | 2026-10-09 | ✓ |
| CR-T046 | k1 | compromisso | 2026-11-20 | 2 | sim | m4: dia 20 (0.92) | 2026-11-20 | ✓ |
| CR-T046 | k2 | compromisso | 2026-11-17 | 2 | sim | m2: Terça que vem (0.99) | 2026-11-17 | ✓ |

### Por família difícil (pela `nota` do rotulador) — acerto e erros caros, Jev principal × baseline

| família | conversas | candidatos | acerto Jev | acerto baseline | fantasma Jev | perdido Jev | revisar Jev | prazo ok Jev | fantasma baseline | perdido baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| cancelamento implícito | 5 | 10 | 1.000 | 0.400 | 0 | 0 | 0 | 4/4 | 4 | 0 |
| prazo | 5 | 10 | 1.000 | 1.000 | 0 | 0 | 0 | 10/10 | 0 | 0 |
| citação antiga | 8 | 18 | 1.000 | 0.889 | 0 | 0 | 0 | 11/11 | 0 | 0 |
| correção tardia | 5 | 12 | 0.917 | 0.583 | 0 | 0 | 1 | 6/7 | 4 | 0 |
| pedido sem aceite | 5 | 12 | 0.750 | 0.833 | 0 | 0 | 1 | 8/9 | 0 | 0 |
| responsável ambíguo | 6 | 14 | 1.000 | 0.643 | 0 | 0 | 0 | 10/11 | 0 | 0 |
| aceite condicional | 4 | 8 | 1.000 | 0.750 | 0 | 0 | 0 | 8/8 | 1 | 0 |
| aceite curto | 1 | 2 | 1.000 | 1.000 | 0 | 0 | 0 | 2/2 | 0 | 0 |
| proposta × compromisso | 3 | 7 | 1.000 | 0.714 | 0 | 0 | 0 | 6/6 | 1 | 0 |
| oferta aceita | 1 | 2 | 1.000 | 0.000 | 0 | 0 | 0 | 2/2 | 0 | 0 |
| fácil / outros | 3 | 7 | 1.000 | 0.571 | 0 | 0 | 0 | 6/6 | 1 | 0 |

### Curva da Choice principal — piso do vencedor (mesmas respostas; informativo no teste)

| piso do vencedor | cobertura (não revisar) | erro entre decididos | tarefa fantasma | compromisso perdido | acerto total |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.039 | 1 | 0 | 0.961 |
| 0.400 | 1.000 | 0.039 | 1 | 0 | 0.961 |
| 0.500 | 0.980 | 0.020 | 0 | 0 | 0.961 |
| 0.600 | 0.951 | 0.021 | 0 | 0 | 0.931 |
| 0.700 | 0.931 | 0.021 | 0 | 0 | 0.912 |
| 0.800 | 0.892 | 0.011 | 0 | 0 | 0.882 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | conversas longas (sem chamada) | falhas operacionais (→ revisar) | perguntas | p50_ms | p95_ms | tokens_por_conversa | US$_total | US$_por_1000_conversas | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| 46 | 0 | 0 | 0 | 612 | 339 | 414 | 10379 | 0.020053 | 0.4359 | jev-1.13.0 |

### Caso a caso (um candidato por linha)

`P` = probabilidade do vencedor da Choice de veredito; `acc/und/quo/opn` = Nouls `accepted`/`undone`/`quoted`/`open_request`; `ok` compara o veredito da variante principal com o gabarito; `caro` = tarefa fantasma, compromisso perdido ou prazo errado em compromisso acertado; `base` = baseline.

| id | fam | k | responsável | trecho | gab | Jev | P | acc/und/quo/opn | nouls→ | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CR-T001 | cancelamento implícito | k1 | Duda | deixa comigo, fui eu que resolvi o caso | compromisso → 2026-10-06 | compromisso → 2026-10-06 | 0.95 | 0.96/0.05/0.04/0.06 | compromisso | ✓ |  | compromisso | commitment P=0.95; prazo 'm1: amanhã' P=0.93 → 2026-10-06 |
| CR-T001 | cancelamento implícito | k2 | Nanda | você atualiza a base de conhecimento com o erro 50 | cancelado | cancelado | 1.00 | 0.54/0.93/0.04/0.18 | cancelado | ✓ |  | pedido_sem_aceite → 2026-10-06 | cancelled P=1.00; sem prazo em cancelado |
| CR-T002 | prazo | k1 | Hugo | Fica para a semana que vem | compromisso | compromisso | 0.79 | 0.48/0.12/0.03/0.29 | revisar | ✓ |  | compromisso | commitment P=0.79; prazo do próprio trecho 'm2: semana que vem' → sem dia (Jev apontou 'm2: semana que vem' P=0.64) |
| CR-T002 | prazo | k2 | Hugo | te digo na segunda | compromisso → 2026-11-30 | compromisso → 2026-11-30 | 1.00 | 0.69/0.06/0.03/0.13 | revisar | ✓ |  | compromisso → 2026-11-30 | commitment P=1.00; prazo do próprio trecho 'm4: segunda' → 2026-11-30 (Jev apontou 'm4: segunda' P=0.98) |
| CR-T003 | prazo | k1 | Ivo | Eu renovo na sexta. | compromisso → 2027-01-01 | compromisso → 2027-01-01 | 1.00 | 0.85/0.05/0.03/0.10 | compromisso | ✓ |  | compromisso → 2027-01-01 | commitment P=1.00; prazo do próprio trecho 'm2: sexta' → 2027-01-01 (Jev apontou 'm2: sexta' P=0.92) |
| CR-T003 | prazo | k2 | Ivo | Rodo no dia 2. | compromisso → 2027-01-02 | compromisso → 2027-01-02 | 1.00 | 0.86/0.05/0.04/0.07 | compromisso | ✓ |  | compromisso → 2027-01-02 | commitment P=1.00; prazo do próprio trecho 'm4: no dia 2' → 2027-01-02 (Jev apontou 'm4: no dia 2' P=0.99) |
| CR-T004 | fácil / outros | k1 | Cris | Mando agora. | compromisso → 2026-10-22 | compromisso → 2026-10-22 | 1.00 | 0.97/0.09/0.02/0.04 | compromisso | ✓ |  | compromisso → 2026-10-22 | commitment P=1.00; prazo do próprio trecho 'm2: agora' → 2026-10-22 (Jev apontou 'm1: hoje' P=0.76) |
| CR-T004 | fácil / outros | k2 | Beto | Eu ligo para confirmar o recebimento amanhã. | compromisso → 2026-10-23 | compromisso → 2026-10-23 | 1.00 | 0.85/0.06/0.03/0.07 | compromisso | ✓ |  | compromisso → 2026-10-23 | commitment P=1.00; prazo do próprio trecho 'm3: amanhã' → 2026-10-23 (Jev apontou 'm3: amanhã' P=0.89) |
| CR-T005 | citação antiga | k1 | Ígor | o técnico Ígor prometeu voltar na sexta para troca | citacao_antiga | citacao_antiga | 0.83 | 0.12/0.74/0.84/0.17 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=0.83; sem prazo em citacao_antiga |
| CR-T005 | citação antiga | k2 | Ígor | Vou lá na quarta. | compromisso → 2026-12-16 | compromisso → 2026-12-16 | 0.94 | 0.88/0.06/0.03/0.09 | compromisso | ✓ |  | compromisso → 2026-12-16 | commitment P=0.94; prazo do próprio trecho 'm4: quarta' → 2026-12-16 (Jev apontou 'm4: quarta' P=0.91) |
| CR-T006 | correção tardia | k1 | Leo | Publico depois de amanhã. | compromisso → 2026-10-07 | compromisso → 2026-10-07 | 0.99 | 0.89/0.06/0.02/0.07 | compromisso | ✓ |  | compromisso → 2026-10-07 | commitment P=0.99; prazo do próprio trecho 'm3: depois de amanhã' → 2026-10-07 (Jev apontou 'm3: depois de amanhã' P=0.64) |
| CR-T006 | correção tardia | k2 | Leo | Publico amanhã. | cancelado | cancelado | 0.99 | 0.76/0.95/0.03/0.07 | cancelado | ✓ |  | compromisso → 2026-10-06 | cancelled P=0.99; sem prazo em cancelado |
| CR-T007 | pedido sem aceite | k1 | Tati | Tati, o vídeo de fim de ano até dia 16. | compromisso → 2026-12-16 | compromisso → 2026-12-16 | 1.00 | 0.96/0.05/0.04/0.03 | compromisso | ✓ |  | pedido_sem_aceite → 2026-12-16 | commitment P=1.00; prazo do próprio trecho 'm1: até dia 16' → 2026-12-16 (Jev apontou 'm1: até dia 16' P=0.76) |
| CR-T007 | pedido sem aceite | k2 | Hugo | Então antecipa para o dia 16 também? | pedido_sem_aceite → 2026-12-16 | pedido_sem_aceite → 2026-12-16 | 0.99 | 0.06/0.07/0.03/0.84 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-12-16 | unaccepted_request P=0.99; prazo do próprio trecho 'm4: para o dia 16' → 2026-12-16 (Jev apontou 'm4: para o dia 16' P=0.92) |
| CR-T007 | pedido sem aceite | k3 | Hugo | Hugo, o relatório de dezembro até dia 18. | cancelado | pedido_sem_aceite → 2026-12-18 | 0.81 | 0.19/0.54/0.04/0.82 | pedido_sem_aceite | ✗ |  | pedido_sem_aceite → 2026-12-18 | unaccepted_request P=0.81; prazo do próprio trecho 'm1: até dia 18' → 2026-12-18 (Jev apontou 'm1: até dia 18' P=0.55) |
| CR-T008 | correção tardia | k1 | Ígor | Ígor, você vai no lugar dele? | compromisso → 2026-11-06 | compromisso → 2026-11-06 | 1.00 | 0.97/0.04/0.02/0.02 | compromisso | ✓ |  | pedido_sem_aceite → 2026-11-06 | commitment P=1.00; prazo 'm3: sexta' P=0.67 → 2026-11-06 |
| CR-T008 | correção tardia | k2 | Fábio | você visita o cliente do galpão na sexta? | cancelado | cancelado | 0.99 | 0.77/0.94/0.03/0.11 | cancelado | ✓ |  | cancelado | cancelled P=0.99; sem prazo em cancelado |
| CR-T009 | prazo | k1 | Ivo | Assim que fechar a sprint eu olho. | compromisso | compromisso | 0.98 | 0.69/0.06/0.02/0.32 | revisar | ✓ |  | compromisso | commitment P=0.98; prazo do próprio trecho 'm2: Assim que fechar' → sem dia (Jev apontou 'm2: Assim que fechar' P=0.57) |
| CR-T009 | prazo | k2 | Ivo | Esse eu resolvo em 2 dias. | compromisso → 2026-10-28 | compromisso → 2026-10-28 | 1.00 | 0.94/0.05/0.02/0.07 | compromisso | ✓ |  | compromisso → 2026-10-28 | commitment P=1.00; prazo do próprio trecho 'm4: em 2 dias' → 2026-10-28 (Jev apontou 'm4: em 2 dias' P=0.97) |
| CR-T010 | responsável ambíguo | k1 | Tati | A gente manda até o dia 12. | compromisso → 2026-10-12 | compromisso → 2026-10-12 | 1.00 | 0.90/0.04/0.03/0.06 | compromisso | ✓ |  | compromisso → 2026-10-12 | commitment P=1.00; prazo do próprio trecho 'm2: até o dia 12' → 2026-10-12 (Jev apontou 'm2: até o dia 12' P=1.00) |
| CR-T010 | responsável ambíguo | k2 | Tati | Pode, eu mesma envio. | compromisso → 2026-10-12 | compromisso → 2026-10-12 | 1.00 | 0.96/0.06/0.02/0.05 | compromisso | ✓ |  | compromisso | commitment P=1.00; prazo 'm2: até o dia 12' P=0.98 → 2026-10-12 |
| CR-T011 | responsável ambíguo | k1 | Tati | Alguém consegue ligar para a gráfica hoje e confir | pedido_sem_aceite → 2026-10-06 | pedido_sem_aceite → 2026-10-06 | 0.95 | 0.02/0.43/0.03/0.51 | revisar | ✓ |  | pedido_sem_aceite → 2026-10-06 | unaccepted_request P=0.95; prazo do próprio trecho 'm1: hoje' → 2026-10-06 (Jev apontou 'm1: hoje' P=0.97) |
| CR-T011 | responsável ambíguo | k2 | Jonas | Alguém consegue ligar para a gráfica hoje e confir | pedido_sem_aceite → 2026-10-06 | pedido_sem_aceite → 2026-10-06 | 0.92 | 0.03/0.40/0.03/0.64 | revisar | ✓ |  | pedido_sem_aceite → 2026-10-06 | unaccepted_request P=0.92; prazo do próprio trecho 'm1: hoje' → 2026-10-06 (Jev apontou 'm1: hoje' P=0.97) |
| CR-T012 | responsável ambíguo | k1 | Vítor | Assumo, entrego no dia 28. | compromisso → 2026-10-28 | compromisso → 2026-10-28 | 1.00 | 0.98/0.13/0.03/0.03 | compromisso | ✓ |  | compromisso → 2026-10-28 | commitment P=1.00; prazo do próprio trecho 'm4: no dia 28' → 2026-10-28 (Jev apontou 'm4: no dia 28' P=0.98) |
| CR-T012 | responsável ambíguo | k2 | Aline | Aline faz. | cancelado | cancelado | 0.92 | 0.08/0.83/0.07/0.70 | cancelado | ✓ |  | pedido_sem_aceite → 2026-10-28 | cancelled P=0.92; sem prazo em cancelado |
| CR-T013 | responsável ambíguo | k1 | Vítor | Vítor precisa assinar a procuração até amanhã. | cancelado | cancelado | 0.92 | 0.03/0.91/0.09/0.55 | cancelado | ✓ |  | pedido_sem_aceite → 2026-10-07 | cancelled P=0.92; sem prazo em cancelado |
| CR-T013 | responsável ambíguo | k2 | Sônia | Então assino eu como substituta. | compromisso → 2026-10-07 | compromisso → 2026-10-08 | 0.60 | 0.67/0.26/0.03/0.06 | revisar | ✓ | prazo errado | compromisso → 2026-10-08 | commitment P=0.60; prazo 'm3: quinta' P=0.78 → 2026-10-08 |
| CR-T013 | responsável ambíguo | k3 | Aline | você leva ao cartório na quinta? | compromisso → 2026-10-08 | compromisso → 2026-10-08 | 1.00 | 0.97/0.03/0.02/0.03 | compromisso | ✓ |  | pedido_sem_aceite → 2026-10-08 | commitment P=1.00; prazo do próprio trecho 'm3: quinta' → 2026-10-08 (Jev apontou 'm3: quinta' P=1.00) |
| CR-T014 | correção tardia | k1 | Ígor | *sexta, quinta eu tô no outro cliente | compromisso → 2026-10-23 | compromisso → 2026-10-23 | 0.51 | 0.77/0.16/0.04/0.13 | compromisso | ✓ |  | compromisso → 2026-10-23 | commitment P=0.51; prazo 'm2: sexta' P=0.58 → 2026-10-23 |
| CR-T014 | correção tardia | k2 | Ígor | vou na quinta | cancelado | cancelado | 0.99 | 0.42/0.95/0.04/0.14 | cancelado | ✓ |  | compromisso → 2026-10-22 | cancelled P=0.99; sem prazo em cancelado |
| CR-T014 | correção tardia | k3 | Paula | Aviso a diretora. | compromisso | compromisso → 2026-10-23 | 1.00 | 0.86/0.06/0.03/0.06 | compromisso | ✓ | prazo errado | compromisso → 2026-10-23 | commitment P=1.00; prazo 'm3: sexta' P=0.57 → 2026-10-23 |
| CR-T015 | citação antiga | k1 | Duda | Duda abre reclamação formal com o fornecedor até o | citacao_antiga | citacao_antiga | 0.98 | 0.17/0.36/0.92/0.10 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=0.98; sem prazo em citacao_antiga |
| CR-T015 | citação antiga | k2 | Duda | Se quiserem, eu escalo para o gerente deles na seg | proposta → 2026-11-16 | proposta → 2026-11-16 | 1.00 | 0.08/0.06/0.03/0.05 | proposta | ✓ |  | proposta → 2026-11-16 | proposal P=1.00; prazo do próprio trecho 'm4: segunda' → 2026-11-16 (Jev apontou 'm4: segunda' P=0.93) |
| CR-T015 | citação antiga | k3 | Fábio | pode cobrar eles amanhã? | compromisso → 2026-11-13 | compromisso → 2026-11-13 | 1.00 | 0.96/0.05/0.03/0.03 | compromisso | ✓ |  | pedido_sem_aceite → 2026-11-13 | commitment P=1.00; prazo do próprio trecho 'm2: amanhã' → 2026-11-13 (Jev apontou 'm3: amanhã cedo' P=0.73) |
| CR-T016 | citação antiga | k1 | Tati | Mando até as 18h. | compromisso → 2026-10-06 | compromisso → 2026-10-06 | 1.00 | 0.97/0.09/0.03/0.03 | compromisso | ✓ |  | compromisso → 2026-10-06 | commitment P=1.00; prazo do próprio trecho 'm5: até as 18h' → 2026-10-06 (Jev apontou 'm4: hoje' P=0.81) |
| CR-T016 | citação antiga | k2 | Tati | Tati apresenta o plano de mídia na sexta | citacao_antiga | citacao_antiga | 0.98 | 0.84/0.07/0.93/0.08 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=0.98; sem prazo em citacao_antiga |
| CR-T017 | pedido sem aceite | k1 | Vítor | você revisa o contrato de locação do cliente novo  | pedido_sem_aceite → 2026-12-14 | pedido_sem_aceite → 2026-12-14 | 0.99 | 0.06/0.08/0.03/0.89 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-12-14 | unaccepted_request P=0.99; prazo do próprio trecho 'm1: segunda' → 2026-12-14 (Jev apontou 'm1: segunda' P=0.90) |
| CR-T017 | pedido sem aceite | k2 | Aline | consegue organizar o arquivo morto este mês? | pedido_sem_aceite | proposta | 0.78 | 0.12/0.28/0.03/0.71 | pedido_sem_aceite | ✗ |  | pedido_sem_aceite | proposal P=0.78; prazo do próprio trecho 'm3: este mês' → sem dia (Jev apontou 'm3: este mês' P=0.95) |
| CR-T017 | pedido sem aceite | k3 | Aline | Que tal eu começar pelas caixas de 2020 e a gente  | proposta | proposta | 0.99 | 0.14/0.23/0.03/0.29 | proposta | ✓ |  | proposta | proposal P=0.99; prazo do próprio trecho 'm4: depois' → sem dia (Jev apontou 'm3: este mês' P=0.87) |
| CR-T018 | pedido sem aceite | k1 | Hugo | eu reservo a sala de edição para quarta | compromisso → 2026-10-28 | compromisso → 2026-10-27 | 0.98 | 0.67/0.06/0.03/0.05 | revisar | ✓ | prazo errado | compromisso → 2026-10-28 | commitment P=0.98; prazo 'm1: amanhã' P=0.59 → 2026-10-27; 'm5: quarta' está no trecho mas fora da oração da entrega, o Jev decide |
| CR-T018 | pedido sem aceite | k2 | Jonas | pode entregar o storyboard amanhã? | pedido_sem_aceite → 2026-10-27 | pedido_sem_aceite → 2026-10-27 | 0.99 | 0.11/0.08/0.03/0.86 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-10-27 | unaccepted_request P=0.99; prazo do próprio trecho 'm1: amanhã' → 2026-10-27 (Jev apontou 'm1: amanhã' P=0.99) |
| CR-T019 | pedido sem aceite | k1 | Hugo | você consegue entregar a planilha de verba até qui | pedido_sem_aceite → 2026-11-05 | pedido_sem_aceite → 2026-11-05 | 1.00 | 0.06/0.07/0.03/0.91 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-11-05 | unaccepted_request P=1.00; prazo do próprio trecho 'm1: quinta' → 2026-11-05 (Jev apontou 'm1: quinta' P=0.99) |
| CR-T019 | pedido sem aceite | k2 | Tati | que tal você adiantar as artes do carrossel? | pedido_sem_aceite | pedido_sem_aceite | 0.61 | 0.08/0.05/0.03/0.93 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-11-05 | unaccepted_request P=0.61; prazo `none` P=0.97 |
| CR-T020 | cancelamento implícito | k1 | Marina | você confirma com a auditoria a data exata de libe | pedido_sem_aceite | pedido_sem_aceite | 1.00 | 0.05/0.06/0.03/0.92 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite | unaccepted_request P=1.00; prazo `none` P=0.98 |
| CR-T020 | cancelamento implícito | k2 | Bia | Rodo hoje à tarde. | cancelado | cancelado | 1.00 | 0.87/0.96/0.03/0.25 | cancelado | ✓ |  | compromisso → 2026-10-09 | cancelled P=1.00; sem prazo em cancelado |
| CR-T021 | aceite condicional | k1 | Caio | Eu poderia revisar no sábado, mas prefiro não trab | proposta → 2026-11-07 | proposta → 2026-11-07 | 0.96 | 0.05/0.05/0.03/0.15 | proposta | ✓ |  | proposta → 2026-11-07 | proposal P=0.96; prazo 'm4: sábado' P=0.50 → 2026-11-07 |
| CR-T021 | aceite condicional | k2 | Dani | Se nada pegar fogo, entrego na sexta. | compromisso → 2026-11-06 | compromisso → 2026-11-06 | 1.00 | 0.91/0.07/0.02/0.09 | compromisso | ✓ |  | compromisso → 2026-11-06 | commitment P=1.00; prazo do próprio trecho 'm2: sexta' → 2026-11-06 (Jev apontou 'm2: sexta' P=0.95) |
| CR-T022 | pedido sem aceite | k1 | Fábio | pode entregar o laudo do equipamento amanhã? | pedido_sem_aceite → 2026-10-08 | pedido_sem_aceite → 2026-10-08 | 1.00 | 0.04/0.06/0.04/0.92 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-10-08 | unaccepted_request P=1.00; prazo do próprio trecho 'm1: amanhã' → 2026-10-08 (Jev apontou 'm1: amanhã' P=0.99) |
| CR-T022 | pedido sem aceite | k2 | Paula | Eu retorno para ele agora. | compromisso → 2026-10-07 | revisar | 0.47 | 0.09/0.07/0.02/0.08 | proposta | ✗ |  | compromisso → 2026-10-07 | vencedor unaccepted_request com P=0.47 < 0.5; sem prazo em revisar |
| CR-T023 | correção tardia | k1 | Jonas | mando duas na segunda | compromisso → 2026-10-26 | compromisso → 2026-10-26 | 0.59 | 0.52/0.07/0.03/0.29 | revisar | ✓ |  | compromisso → 2026-10-26 | commitment P=0.59; prazo do próprio trecho 'm4: segunda' → 2026-10-26 (Jev apontou 'm4: segunda' P=0.81) |
| CR-T023 | correção tardia | k2 | Jonas | a terceira na quarta | compromisso → 2026-10-28 | compromisso → 2026-10-28 | 0.55 | 0.38/0.06/0.03/0.22 | revisar | ✓ |  | compromisso → 2026-10-28 | commitment P=0.55; prazo do próprio trecho 'm4: quarta' → 2026-10-28 (Jev apontou 'm4: quarta' P=0.97) |
| CR-T023 | correção tardia | k3 | Jonas | A cliente pediu três opções de logo até segunda. J | cancelado | revisar | 0.47 | 0.21/0.73/0.06/0.63 | cancelado | ✗ |  | compromisso → 2026-10-26 | vencedor commitment com P=0.47 < 0.5; sem prazo em revisar |
| CR-T024 | cancelamento implícito | k1 | Bia | Atualizo na quinta. | cancelado | cancelado | 0.99 | 0.67/0.91/0.03/0.19 | cancelado | ✓ |  | compromisso → 2026-10-22 | cancelled P=0.99; sem prazo em cancelado |
| CR-T024 | cancelamento implícito | k2 | Bia | Então eu uso a quinta para revisar o changelog. | compromisso → 2026-10-22 | compromisso → 2026-10-22 | 0.76 | 0.71/0.06/0.02/0.20 | compromisso | ✓ |  | compromisso → 2026-10-22 | commitment P=0.76; prazo do próprio trecho 'm4: quinta' → 2026-10-22 (Jev apontou 'm4: quinta' P=0.47) |
| CR-T025 | cancelamento implícito | k1 | Ivo | Eu faço os testes dela na quinta. | cancelado | cancelado | 1.00 | 0.85/0.96/0.03/0.09 | cancelado | ✓ |  | compromisso → 2026-10-15 | cancelled P=1.00; sem prazo em cancelado |
| CR-T025 | cancelamento implícito | k2 | Helô | você termina a tela de exportação até quarta? | cancelado | cancelado | 1.00 | 0.95/0.97/0.03/0.05 | cancelado | ✓ |  | pedido_sem_aceite → 2026-10-14 | cancelled P=1.00; sem prazo em cancelado |
| CR-T026 | citação antiga | k1 | Cris | Cris, favor enviar o balanço até sexta. | citacao_antiga | citacao_antiga | 0.99 | 0.75/0.12/0.94/0.12 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=0.99; sem prazo em citacao_antiga |
| CR-T026 | citação antiga | k2 | Cris | Esse eu preparo e mando na terça. | compromisso → 2026-10-13 | compromisso → 2026-10-13 | 1.00 | 0.97/0.07/0.03/0.05 | compromisso | ✓ |  | compromisso → 2026-10-13 | commitment P=1.00; prazo do próprio trecho 'm4: terça' → 2026-10-13 (Jev apontou 'm4: terça' P=1.00) |
| CR-T027 | correção tardia | k1 | Helô | Quarta consigo uma versão sem filtros. | compromisso → 2026-10-07 | compromisso → 2026-10-07 | 1.00 | 0.97/0.03/0.02/0.06 | compromisso | ✓ |  | compromisso → 2026-10-07 | commitment P=1.00; prazo do próprio trecho 'm3: Quarta' → 2026-10-07 (Jev apontou 'm3: Quarta' P=0.50) |
| CR-T027 | correção tardia | k2 | Helô | Entrego o protótipo da busca na sexta. | cancelado | cancelado | 0.97 | 0.65/0.90/0.03/0.09 | cancelado | ✓ |  | compromisso → 2026-10-09 | cancelled P=0.97; sem prazo em cancelado |
| CR-T028 | fácil / outros | k1 | Cris | mantém a conferência do FGTS dele que você ia faze | compromisso → 2026-11-20 | compromisso → 2026-11-20 | 1.00 | 0.96/0.03/0.05/0.03 | compromisso | ✓ |  | pedido_sem_aceite → 2026-11-20 | commitment P=1.00; prazo do próprio trecho 'm5: até dia 20' → 2026-11-20 (Jev apontou 'm5: até dia 20' P=1.00) |
| CR-T028 | fácil / outros | k2 | Cris | Calculo e mando no dia 17. | cancelado | cancelado | 1.00 | 0.85/0.96/0.03/0.09 | cancelado | ✓ |  | compromisso → 2026-11-17 | cancelled P=1.00; sem prazo em cancelado |
| CR-T029 | citação antiga | k1 | Fábio | o Fábio instala a atualização no servidor do clien | compromisso → 2026-11-05 | compromisso → 2026-11-05 | 0.99 | 0.94/0.03/0.10/0.03 | compromisso | ✓ |  | pedido_sem_aceite → 2026-11-05 | commitment P=0.99; prazo do próprio trecho 'm1: quinta' → 2026-11-05 (Jev apontou 'm1: quinta' P=0.55) |
| CR-T029 | citação antiga | k2 | Fábio | Faço na quarta à noite. | compromisso → 2026-11-04 | compromisso → 2026-11-04 | 1.00 | 0.95/0.05/0.03/0.06 | compromisso | ✓ |  | compromisso → 2026-11-04 | commitment P=1.00; prazo do próprio trecho 'm4: quarta à noite' → 2026-11-04 (Jev apontou 'm4: quarta à noite' P=0.96) |
| CR-T030 | responsável ambíguo | k1 | Jonas | Eu fico com o briefing do estande, então. | compromisso → 2026-10-19 | compromisso → 2026-10-19 | 1.00 | 0.82/0.05/0.02/0.06 | compromisso | ✓ |  | compromisso | commitment P=1.00; prazo 'm5: Segunda' P=1.00 → 2026-10-19 |
| CR-T030 | responsável ambíguo | k2 | Jonas | Jonas ou Hugo, um de vocês fecha o orçamento da fe | cancelado | cancelado | 0.97 | 0.04/0.82/0.03/0.51 | cancelado | ✓ |  | pedido_sem_aceite → 2026-10-16 | cancelled P=0.97; sem prazo em cancelado |
| CR-T030 | responsável ambíguo | k3 | Hugo | Eu fecho. | compromisso → 2026-10-16 | compromisso → 2026-10-16 | 1.00 | 0.97/0.04/0.02/0.03 | compromisso | ✓ |  | compromisso → 2026-10-16 | commitment P=1.00; prazo 'm1: sexta' P=1.00 → 2026-10-16 |
| CR-T031 | aceite curto | k1 | Dani | você acompanha o monitoramento amanhã cedo? | pedido_sem_aceite → 2026-10-23 | pedido_sem_aceite → 2026-10-23 | 1.00 | 0.06/0.10/0.03/0.84 | pedido_sem_aceite | ✓ |  | pedido_sem_aceite → 2026-10-23 | unaccepted_request P=1.00; prazo do próprio trecho 'm3: amanhã cedo' → 2026-10-23 (Jev apontou 'm3: amanhã cedo' P=0.85) |
| CR-T031 | aceite curto | k2 | Caio | sobe o hotfix do boleto hoje à noite? | compromisso → 2026-10-22 | compromisso → 2026-10-22 | 1.00 | 0.91/0.07/0.03/0.06 | compromisso | ✓ |  | compromisso → 2026-10-22 | commitment P=1.00; prazo do próprio trecho 'm1: hoje à noite' → 2026-10-22 (Jev apontou 'm1: hoje à noite' P=0.99) |
| CR-T032 | proposta × compromisso | k1 | Ígor | Eu fecho os chamados antigos até o fim da semana. | compromisso → 2026-10-23 | compromisso → 2026-10-23 | 0.99 | 0.91/0.06/0.03/0.06 | compromisso | ✓ |  | compromisso → 2026-10-23 | commitment P=0.99; prazo do próprio trecho 'm4: até o fim da semana' → 2026-10-23 (Jev apontou 'm4: até o fim da semana' P=1.00) |
| CR-T032 | proposta × compromisso | k2 | Nanda | Posso montar um FAQ com as dúvidas da semana, se a | proposta | proposta | 1.00 | 0.22/0.26/0.02/0.06 | proposta | ✓ |  | proposta | proposal P=1.00; prazo `none` P=0.98 |
| CR-T033 | proposta × compromisso | k1 | Dani | Posso refatorar o serviço de e-mail na semana que  | cancelado | cancelado | 0.99 | 0.04/0.88/0.03/0.18 | cancelado | ✓ |  | proposta | cancelled P=0.99; sem prazo em cancelado |
| CR-T033 | proposta × compromisso | k2 | Dani | o ajuste do template de boas-vindas você faz até t | compromisso → 2026-12-01 | compromisso → 2026-12-01 | 1.00 | 0.97/0.04/0.03/0.02 | compromisso | ✓ |  | compromisso → 2026-12-01 | commitment P=1.00; prazo do próprio trecho 'm4: terça' → 2026-12-01 (Jev apontou 'm4: terça' P=1.00) |
| CR-T034 | responsável ambíguo | k1 | Jonas | Eu seleciono na terça. | compromisso → 2026-12-15 | compromisso → 2026-12-15 | 0.99 | 0.81/0.06/0.03/0.09 | compromisso | ✓ |  | compromisso → 2026-12-15 | commitment P=0.99; prazo do próprio trecho 'm5: terça' → 2026-12-15 (Jev apontou 'm5: terça' P=0.83) |
| CR-T034 | responsável ambíguo | k2 | Karen | O pessoal do estúdio entrega as fotos tratadas na  | compromisso → 2026-12-14 | compromisso → 2026-12-14 | 1.00 | 0.79/0.06/0.09/0.09 | compromisso | ✓ |  | pedido_sem_aceite → 2026-12-14 | commitment P=1.00; prazo do próprio trecho 'm1: segunda' → 2026-12-14 (Jev apontou 'm1: segunda' P=0.94) |
| CR-T035 | cancelamento implícito | k1 | Fábio | terça às 10h eu dou o treinamento | cancelado | cancelado | 0.99 | 0.93/0.81/0.04/0.05 | cancelado | ✓ |  | compromisso → 2026-11-03 | cancelled P=0.99; sem prazo em cancelado |
| CR-T035 | cancelamento implícito | k2 | Duda | Eu mando o material de apoio para ele hoje mesmo a | compromisso → 2026-10-29 | compromisso → 2026-10-29 | 0.87 | 0.94/0.06/0.03/0.06 | compromisso | ✓ |  | compromisso → 2026-10-29 | commitment P=0.87; prazo do próprio trecho 'm5: hoje mesmo' → 2026-10-29 (Jev apontou 'm5: hoje mesmo' P=0.99) |
| CR-T036 | citação antiga | k1 | Helô | Eu poderia limpar esse README na sexta, se ninguém | proposta → 2026-10-30 | proposta → 2026-10-30 | 1.00 | 0.13/0.07/0.03/0.08 | proposta | ✓ |  | proposta → 2026-10-30 | proposal P=1.00; prazo do próprio trecho 'm4: sexta' → 2026-10-30 (Jev apontou 'm4: sexta' P=1.00) |
| CR-T036 | citação antiga | k2 | Ivo | o Ivo vai migrar os testes para o novo runner até  | citacao_antiga | citacao_antiga | 0.77 | 0.10/0.92/0.93/0.27 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=0.77; sem prazo em citacao_antiga |
| CR-T037 | citação antiga | k1 | Tati | mando as legendas na terça | citacao_antiga | citacao_antiga | 0.90 | 0.47/0.06/0.92/0.09 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=0.90; sem prazo em citacao_antiga |
| CR-T037 | citação antiga | k2 | Tati | Assim que ele aprovar o vídeo eu mando. | proposta | proposta | 0.96 | 0.55/0.07/0.03/0.11 | revisar | ✓ |  | proposta | proposal P=0.96; prazo do próprio trecho 'm2: Assim que ele' → sem dia (Jev apontou 'm1: terça' P=0.61) |
| CR-T037 | citação antiga | k3 | Hugo | vou cobrar a aprovação dele hoje | compromisso → 2026-10-29 | compromisso → 2026-10-29 | 0.91 | 0.73/0.07/0.02/0.08 | compromisso | ✓ |  | compromisso → 2026-10-29 | commitment P=0.91; prazo do próprio trecho 'm3: hoje' → 2026-10-29 (Jev apontou 'm1: terça' P=0.56) |
| CR-T038 | oferta aceita | k1 | Nanda | Posso ficar no plantão de sábado no lugar do Fábio | compromisso → 2026-10-10 | compromisso → 2026-10-10 | 0.99 | 0.96/0.06/0.02/0.04 | compromisso | ✓ |  | proposta → 2026-10-10 | commitment P=0.99; prazo 'm1: sábado' P=0.81 → 2026-10-10; 'm1: sábado' está no trecho mas fora da oração da entrega, o Jev decide |
| CR-T038 | oferta aceita | k2 | Fábio | você cobre a segunda dela? | compromisso → 2026-10-12 | compromisso → 2026-10-12 | 1.00 | 0.96/0.03/0.02/0.03 | compromisso | ✓ |  | pedido_sem_aceite → 2026-10-12 | commitment P=1.00; prazo do próprio trecho 'm3: segunda' → 2026-10-12 (Jev apontou 'm3: segunda' P=0.99) |
| CR-T039 | aceite condicional | k1 | Aline | Então quarta está pronto, pode confirmar com ele. | compromisso → 2026-10-28 | compromisso → 2026-10-28 | 1.00 | 0.71/0.07/0.02/0.06 | compromisso | ✓ |  | compromisso → 2026-10-28 | commitment P=1.00; prazo do próprio trecho 'm4: quarta' → 2026-10-28 (Jev apontou 'm4: quarta' P=0.95) |
| CR-T039 | aceite condicional | k2 | Aline | Vou tentar terminar na quarta. | compromisso → 2026-10-28 | compromisso → 2026-10-28 | 0.99 | 0.76/0.07/0.02/0.08 | compromisso | ✓ |  | proposta → 2026-10-28 | commitment P=0.99; prazo do próprio trecho 'm2: quarta' → 2026-10-28 (Jev apontou 'm4: quarta' P=0.55) |
| CR-T040 | prazo | k1 | Cris | Fecho até o fim do mês. | compromisso → 2026-11-30 | compromisso → 2026-11-30 | 1.00 | 0.77/0.05/0.04/0.11 | compromisso | ✓ |  | compromisso → 2026-11-30 | commitment P=1.00; prazo do próprio trecho 'm2: até o fim do mês' → 2026-11-30 (Jev apontou 'm2: até o fim do mês' P=0.96) |
| CR-T040 | prazo | k2 | Cris | Emito no dia 5. | compromisso → 2026-12-05 | compromisso → 2026-12-05 | 1.00 | 0.82/0.05/0.03/0.10 | compromisso | ✓ |  | compromisso → 2026-12-05 | commitment P=1.00; prazo do próprio trecho 'm4: no dia 5' → 2026-12-05 (Jev apontou 'm4: no dia 5' P=0.99) |
| CR-T041 | fácil / outros | k1 | Tati | você entrega o calendário editorial na sexta? | compromisso → 2026-10-16 | compromisso → 2026-10-16 | 1.00 | 0.96/0.04/0.02/0.03 | compromisso | ✓ |  | compromisso → 2026-10-16 | commitment P=1.00; prazo do próprio trecho 'm1: sexta' → 2026-10-16 (Jev apontou 'm1: sexta' P=1.00) |
| CR-T041 | fácil / outros | k2 | Hugo | as métricas de setembro até amanhã? | compromisso → 2026-10-15 | compromisso → 2026-10-15 | 0.98 | 0.90/0.04/0.03/0.05 | compromisso | ✓ |  | pedido_sem_aceite → 2026-10-15 | commitment P=0.98; prazo do próprio trecho 'm3: amanhã' → 2026-10-15 (Jev apontou 'm3: amanhã' P=0.88) |
| CR-T041 | fácil / outros | k3 | Jonas | Se quiserem eu faço a capa do relatório. | proposta | proposta | 1.00 | 0.08/0.05/0.02/0.05 | proposta | ✓ |  | proposta → 2026-10-15 | proposal P=1.00; prazo `none` P=1.00 |
| CR-T042 | proposta × compromisso | k1 | Caio | A gente devia escrever testes para o módulo de cob | proposta | proposta | 0.99 | 0.49/0.16/0.03/0.13 | revisar | ✓ |  | compromisso | proposal P=0.99; prazo 'm3: Um dia' P=0.56 → sem dia |
| CR-T042 | proposta × compromisso | k2 | Caio | Um dia eu faço isso. | proposta | proposta | 1.00 | 0.41/0.07/0.03/0.14 | revisar | ✓ |  | proposta | proposal P=1.00; prazo do próprio trecho 'm3: Um dia' → sem dia (Jev apontou 'none' P=0.59) |
| CR-T042 | proposta × compromisso | k3 | Caio | Corrijo até sexta. | compromisso → 2026-10-09 | compromisso → 2026-10-09 | 1.00 | 0.97/0.06/0.02/0.03 | compromisso | ✓ |  | compromisso → 2026-10-09 | commitment P=1.00; prazo do próprio trecho 'm5: sexta' → 2026-10-09 (Jev apontou 'm5: sexta' P=0.88) |
| CR-T043 | aceite condicional | k1 | Vítor | Protocolo, desde que o cliente pague as custas até | proposta → 2026-11-16 | proposta → 2026-11-16 | 0.99 | 0.18/0.12/0.05/0.56 | revisar | ✓ |  | compromisso → 2026-11-13 | proposal P=0.99; prazo 'm1: segunda' P=0.65 → 2026-11-16; 'm2: sexta' está no trecho mas fora da oração da entrega, o Jev decide |
| CR-T043 | aceite condicional | k2 | Sônia | Eu cobro o comprovante dele amanhã cedo. | compromisso → 2026-11-13 | compromisso → 2026-11-13 | 0.98 | 0.89/0.05/0.03/0.08 | compromisso | ✓ |  | compromisso → 2026-11-13 | commitment P=0.98; prazo do próprio trecho 'm5: amanhã cedo' → 2026-11-13 (Jev apontou 'm5: amanhã cedo' P=0.99) |
| CR-T044 | citação antiga | k1 | Paula | a contratada responderá em até 4 horas úteis | citacao_antiga | citacao_antiga | 1.00 | 0.05/0.15/0.79/0.11 | citacao_antiga | ✓ |  | citacao_antiga | old_quote P=1.00; sem prazo em citacao_antiga |
| CR-T044 | citação antiga | k2 | Paula | o chamado da prefeitura eu respondo em 2 dias útei | compromisso → 2026-10-16 | compromisso → 2026-10-16 | 0.99 | 0.90/0.07/0.05/0.11 | compromisso | ✓ |  | compromisso → 2026-10-16 | commitment P=0.99; prazo do próprio trecho 'm3: em 2 dias úteis' → 2026-10-16 (Jev apontou 'm3: em 2 dias úteis' P=0.99) |
| CR-T045 | aceite condicional | k1 | Cris | Então amanhã está entregue. | compromisso → 2026-10-09 | compromisso → 2026-10-09 | 1.00 | 0.88/0.06/0.02/0.06 | compromisso | ✓ |  | compromisso → 2026-10-09 | commitment P=1.00; prazo do próprio trecho 'm4: amanhã' → 2026-10-09 (Jev apontou 'm4: amanhã' P=0.85) |
| CR-T045 | aceite condicional | k2 | Cris | Se a cliente me passar o faturamento de setembro h | compromisso → 2026-10-09 | compromisso → 2026-10-09 | 0.98 | 0.79/0.04/0.03/0.07 | compromisso | ✓ |  | compromisso → 2026-10-08 | commitment P=0.98; prazo 'm2: amanhã' P=0.67 → 2026-10-09 |
| CR-T046 | prazo | k1 | Leo | Esse só dia 20. | compromisso → 2026-11-20 | compromisso → 2026-11-20 | 0.87 | 0.43/0.06/0.04/0.23 | revisar | ✓ |  | compromisso → 2026-11-20 | commitment P=0.87; prazo do próprio trecho 'm4: dia 20' → 2026-11-20 (Jev apontou 'm4: dia 20' P=0.92) |
| CR-T046 | prazo | k2 | Leo | Terça que vem eu faço. | compromisso → 2026-11-17 | compromisso → 2026-11-17 | 1.00 | 0.94/0.05/0.03/0.07 | compromisso | ✓ |  | compromisso → 2026-11-17 | commitment P=1.00; prazo do próprio trecho 'm2: Terça que vem' → 2026-11-17 (Jev apontou 'm2: Terça que vem' P=0.99) |
