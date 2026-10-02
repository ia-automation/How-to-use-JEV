# Resultados — roteador-email

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, limiares e política: `perguntas.py`; validação, composição e baseline: `roteador.py`.

> **Dado real, relatório sem texto.** E-mails de produção já classificados pelo F11, anonimizados; o texto e o cache do Jev ficam fora do Git. Aqui só há agregados, IDs `EM-xxxx`, classes e números.
>
> **Gabarito = a decisão do sistema em produção** (regra, Claude, Codex, API ou CRM). Toda taxa é CONCORDÂNCIA com produção, não acerto contra verdade independente. Escalar = mandar ao LLM de produção, que concorda por definição.

Limiares em vigor: confiança por classe {'principal': 0.7, 'notificacoes': 0.7, 'promocoes': 0.7, 'redes_sociais': 0.7, 'spam': 0.9, 'golpe': 0.8}; Noul sim ≥ 0.8, não ≤ 0.2; corpo < 80 caracteres não decide classe de caixa de entrada; teto do corpo 4500.

Custo: Jev MEDIDO (tokens reais × US$ 0.042/M de entrada). LLM ESTIMADO, nada é chamado — `gpt-6-luna` US$ 0.1/0.5 e `gpt-6-astra` US$ 10.0/50.0 por 1M entrada/saída (premissas de `../roteador-jev-llm/run.py`); por e-mail: 1500 tokens de instruções + caracteres × 0.25 → 150 de saída.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste, recorte `só IA` (produção decidiu por LLM: `decidido_por` = ai_*), sem os casos `redes_sociais`, com a política acima. Gabarito = decisão de produção (concordância, não acerto); **1_golpe_na_caixa**: golpe de produção decidido sozinho como `principal`/`notificacoes` ≤ 1% dos golpes do recorte; **2_cliente_perdido**: `principal` de produção decidido sozinho como `spam`/`golpe` ≤ 1% dos principais do recorte; **3_concordancia**: concordância com produção entre os decididos sozinho ≥ 0,95; **4_cobertura**: decide sozinho ≥ 40% do recorte (o briefing sugeria 50% como exemplo; o ajuste, com limiares escolhidos nele mesmo, deu 48% — o relatório mostra a linha dos 50% como informativa); **5_contra_baseline**: o baseline de código NÃO chega lá: falha em 1, 2 ou 3, ou cobre menos que o Jev (se o baseline passar em 1–3 com cobertura ≥ a do Jev, a regra de código basta); **secundario_nao_decide**: os mesmos números nos recortes `todos` e `só regra`; `redes_sociais` à parte; custo roteado × tudo no LLM; o que cada trava de Noul barrou; **se_falhar**: 1 ou 2 falhando = não serve para decidir sozinho o lado caro; 3 falhando = a confiança não separa o que concorda; 4 falhando = seguro, mas tira pouco do LLM; 5 falhando = a regra de código basta

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T14:56:49-03:00): `perguntas.py` sha256 71c6427c49b5414b… · `roteador.py` sha256 f877d291ad674a2a… · `run.py` sha256 cff4c7df8dc3e2e5… · `emails-anon.jsonl` sha256 25bda431016cb6d7…

## Lado a lado

Gabarito = decisão de produção (concordância, não acerto); escalado conta como concordante.

| conjunto | recorte | variante | n | cobertura (decide sozinho) | concordância entre decididos | decidido E concorda / n | escalados | GOLPE NA CAIXA (golpe → principal/notificações, sozinho) | CLIENTE PERDIDO (principal → spam/golpe, sozinho) | concordância ponta a ponta (escalado = 1) |
|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | todos | baseline (regras de código) | 152 | 0.605 | 0.717 | 0.434 | 60 | 4/62 | 7/35 | 0.829 |
| ajuste | todos | Jev forçado (sem limiar) | 152 | 1.000 | 0.822 | 0.822 | 0 | 5/62 | 7/35 | 0.822 |
| ajuste | todos | Jev roteador (política) | 152 | 0.454 | 1.000 | 0.454 | 83 | 0/62 | 0/35 | 1.000 |
| ajuste | só regra | baseline (regras de código) | 57 | 0.632 | 0.861 | 0.544 | 21 | 1/30 | 2/20 | 0.912 |
| ajuste | só regra | Jev forçado (sem limiar) | 57 | 1.000 | 0.895 | 0.895 | 0 | 0/30 | 5/20 | 0.895 |
| ajuste | só regra | Jev roteador (política) | 57 | 0.386 | 1.000 | 0.386 | 35 | 0/30 | 0/20 | 1.000 |
| ajuste | só IA | baseline (regras de código) | 92 | 0.609 | 0.625 | 0.380 | 36 | 3/32 | 5/12 | 0.772 |
| ajuste | só IA | Jev forçado (sem limiar) | 92 | 1.000 | 0.772 | 0.772 | 0 | 5/32 | 2/12 | 0.772 |
| ajuste | só IA | Jev roteador (política) | 92 | 0.478 | 1.000 | 0.478 | 48 | 0/32 | 0/12 | 1.000 |
| teste | todos | baseline (regras de código) | 580 | 0.672 | 0.579 | 0.390 | 190 | 13/147 | 15/223 | 0.717 |
| teste | todos | Jev forçado (sem limiar) | 580 | 1.000 | 0.667 | 0.667 | 0 | 22/147 | 35/223 | 0.667 |
| teste | todos | Jev roteador (política) | 580 | 0.340 | 0.975 | 0.331 | 383 | 0/147 | 2/223 | 0.991 |
| teste | só regra | baseline (regras de código) | 329 | 0.669 | 0.682 | 0.456 | 109 | 1/75 | 2/147 | 0.787 |
| teste | só regra | Jev forçado (sem limiar) | 329 | 1.000 | 0.644 | 0.644 | 0 | 9/75 | 29/147 | 0.644 |
| teste | só regra | Jev roteador (política) | 329 | 0.240 | 0.975 | 0.234 | 250 | 0/75 | 1/147 | 0.994 |
| teste | só IA | baseline (regras de código) | 242 | 0.665 | 0.435 | 0.289 | 81 | 12/72 | 10/68 | 0.624 |
| teste | só IA | Jev forçado (sem limiar) | 242 | 1.000 | 0.690 | 0.690 | 0 | 13/72 | 6/68 | 0.690 |
| teste | só IA | Jev roteador (política) | 242 | 0.463 | 0.973 | 0.450 | 130 | 0/72 | 1/68 | 0.988 |

| conjunto | e-mails | requisições | falhas | p50_ms | p95_ms | tokens_por_e-mail | US$_por_1000_e-mails (Jev) | modelo | critério |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | 152 | 152 | 0 | 260 | 342 | 2960 | 0.1243 | jev-1.13.0 | PASSOU (informativo) |
| teste | 586 | 586 | 0 | 269 | 320 | 3025 | 0.1270 | jev-1.13.0 | NÃO PASSOU |

## Conjunto `ajuste` — 152 e-mails reais anonimizados, 69 remetentes (grupos)

Classe em produção: `principal` 35, `notificacoes` 18, `promocoes` 29, `spam` 8, `golpe` 62. Quem decidiu em produção: `ai_api` 1, `ai_claude` 60, `ai_codex` 31, `crm` 3, `rule` 57. Corpo truncado na extração: 23/152. Registros com nome em maiúsculas mascarado na carga (última milha): 2. `redes_sociais`: 0 caso(s), fora das tabelas principais e do critério (seção própria).

### Roteamento por recorte — baseline × tudo no LLM × Jev, nos mesmos e-mails

**Gabarito = decisão de produção: tudo é concordância com produção, não acerto.** `cobertura` = fração que a variante decide sozinha (o resto escala ao LLM). `concordância entre decididos` = dos decididos sozinho, quantos batem com produção. `decidido E concorda / n` = automação útil. **GOLPE NA CAIXA** = golpe de produção decidido sozinho como `principal`/`notificacoes` (denominador: golpes do recorte). **CLIENTE PERDIDO** = `principal` de produção decidido sozinho como `spam`/`golpe` (denominador: principais do recorte). `ponta a ponta` conta o escalado como concordante (o LLM É o gabarito). Recortes: `só regra` = produção decidiu por regra; `só IA` = produção mandou a um LLM (o resíduo ambíguo: o caso de uso real do roteador); `todos` inclui também os decididos por `crm`. Variantes do Jev leem a MESMA resposta: `forçado` = sempre a classe mais provável; `só confiança` = limiar por classe, sem Nouls nem regra do corpo curto; `roteador` = a política de `perguntas.py`.

| recorte | variante | n | cobertura (decide sozinho) | concordância entre decididos | decidido E concorda / n | escalados | GOLPE NA CAIXA (golpe → principal/notificações, sozinho) | CLIENTE PERDIDO (principal → spam/golpe, sozinho) | concordância ponta a ponta (escalado = 1) |
|---|---|---|---|---|---|---|---|---|---|
| todos | baseline (regras de código) | 152 | 0.605 | 0.717 | 0.434 | 60 | 4/62 | 7/35 | 0.829 |
| todos | tudo no LLM (hoje) | 152 | 0.000 | — | 0.000 | 152 | 0/62 | 0/35 | 1.000 |
| todos | Jev forçado (sem limiar) | 152 | 1.000 | 0.822 | 0.822 | 0 | 5/62 | 7/35 | 0.822 |
| todos | Jev só confiança | 152 | 0.474 | 0.958 | 0.454 | 80 | 0/62 | 0/35 | 0.980 |
| todos | Jev roteador (política) | 152 | 0.454 | 1.000 | 0.454 | 83 | 0/62 | 0/35 | 1.000 |
| só regra | baseline (regras de código) | 57 | 0.632 | 0.861 | 0.544 | 21 | 1/30 | 2/20 | 0.912 |
| só regra | tudo no LLM (hoje) | 57 | 0.000 | — | 0.000 | 57 | 0/30 | 0/20 | 1.000 |
| só regra | Jev forçado (sem limiar) | 57 | 1.000 | 0.895 | 0.895 | 0 | 0/30 | 5/20 | 0.895 |
| só regra | Jev só confiança | 57 | 0.386 | 1.000 | 0.386 | 35 | 0/30 | 0/20 | 1.000 |
| só regra | Jev roteador (política) | 57 | 0.386 | 1.000 | 0.386 | 35 | 0/30 | 0/20 | 1.000 |
| só IA | baseline (regras de código) | 92 | 0.609 | 0.625 | 0.380 | 36 | 3/32 | 5/12 | 0.772 |
| só IA | tudo no LLM (hoje) | 92 | 0.000 | — | 0.000 | 92 | 0/32 | 0/12 | 1.000 |
| só IA | Jev forçado (sem limiar) | 92 | 1.000 | 0.772 | 0.772 | 0 | 5/32 | 2/12 | 0.772 |
| só IA | Jev só confiança | 92 | 0.511 | 0.936 | 0.478 | 45 | 0/32 | 0/12 | 0.967 |
| só IA | Jev roteador (política) | 92 | 0.478 | 1.000 | 0.478 | 48 | 0/32 | 0/12 | 1.000 |

### IC 95% da política — bootstrap agrupado por remetente (`grupo`), 2000 reamostragens

| recorte | grupos | cobertura | concordância entre decididos | golpe na caixa / golpes | cliente perdido / principais | ponta a ponta |
|---|---|---|---|---|---|---|
| todos | 69 | 0.454 [0.333; 0.597] | 1.000 [1.000; 1.000] | 0.000 [0.000; 0.000] | 0.000 [0.000; 0.000] | 1.000 [1.000; 1.000] |
| só regra | 17 | 0.386 [0.179; 0.674] | 1.000 [1.000; 1.000] | 0.000 [0.000; 0.000] | 0.000 [0.000; 0.000] | 1.000 [1.000; 1.000] |
| só IA | 51 | 0.478 [0.338; 0.634] | 1.000 [1.000; 1.000] | 0.000 [0.000; 0.000] | 0.000 [0.000; 0.000] | 1.000 [1.000; 1.000] |

**Critério conferido no `ajuste`, recorte `só IA`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 golpe na caixa (sozinho) | 0/32 (0.000) | ≤ 0.01 | ✓ |
| 2 cliente perdido (sozinho) | 0/12 (0.000) | ≤ 0.01 | ✓ |
| 3 concordância entre decididos | 44/44 (1.000) | ≥ 0.95 | ✓ |
| 4 cobertura | 44/92 (0.478) | ≥ 0.4 | ✓ |
| 5 o baseline de código não chega lá | baseline: golpe na caixa 3/32, cliente perdido 5/12, concordância 0.625, cobertura 0.609 | baseline falha em 1, 2 ou 3, ou cobre menos que o Jev | ✓ |
| informativo: cobertura ≥ 0.5 (sugestão do briefing) | 0.478 | ≥ 0.5 | ✗ (não decide) |

**Veredito calculado: PASSOU** (os 5 itens numerados).

### Curva cobertura × concordância × erro caro por limiar (mesmas respostas, zero chamada nova)

O MESMO limiar de confiança em todas as classes. `com a política` mantém os conflitos de Noul e a regra do corpo curto; `só confiança` desliga os dois. A linha de `perguntas.py` (limiar por classe) está na tabela principal.

**Recorte `só IA` — com a política**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.804 | 0.851 | 0/32 | 0/12 | 74 |
| 0.500 | 0.674 | 0.935 | 0/32 | 0/12 | 62 |
| 0.600 | 0.565 | 0.962 | 0/32 | 0/12 | 52 |
| 0.700 | 0.500 | 1.000 | 0/32 | 0/12 | 46 |
| 0.800 | 0.370 | 1.000 | 0/32 | 0/12 | 34 |
| 0.900 | 0.261 | 1.000 | 0/32 | 0/12 | 24 |
| 0.950 | 0.217 | 1.000 | 0/32 | 0/12 | 20 |
| 0.990 | 0.109 | 1.000 | 0/32 | 0/12 | 10 |

**Recorte `só IA` — só confiança**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.772 | 5/32 | 2/12 | 92 |
| 0.500 | 0.804 | 0.838 | 5/32 | 0/12 | 74 |
| 0.600 | 0.630 | 0.897 | 1/32 | 0/12 | 58 |
| 0.700 | 0.533 | 0.939 | 0/32 | 0/12 | 49 |
| 0.800 | 0.380 | 0.971 | 0/32 | 0/12 | 35 |
| 0.900 | 0.272 | 0.960 | 0/32 | 0/12 | 25 |
| 0.950 | 0.217 | 1.000 | 0/32 | 0/12 | 20 |
| 0.990 | 0.109 | 1.000 | 0/32 | 0/12 | 10 |

**Recorte `todos` — com a política**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.849 | 0.907 | 0/62 | 0/35 | 129 |
| 0.500 | 0.678 | 0.951 | 0/62 | 0/35 | 103 |
| 0.600 | 0.539 | 0.963 | 0/62 | 0/35 | 82 |
| 0.700 | 0.474 | 1.000 | 0/62 | 0/35 | 72 |
| 0.800 | 0.349 | 1.000 | 0/62 | 0/35 | 53 |
| 0.900 | 0.243 | 1.000 | 0/62 | 0/35 | 37 |
| 0.950 | 0.197 | 1.000 | 0/62 | 0/35 | 30 |
| 0.990 | 0.112 | 1.000 | 0/62 | 0/35 | 17 |

**Recorte `todos` — só confiança**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.822 | 5/62 | 7/35 | 152 |
| 0.500 | 0.757 | 0.887 | 5/62 | 0/35 | 115 |
| 0.600 | 0.579 | 0.920 | 1/62 | 0/35 | 88 |
| 0.700 | 0.493 | 0.960 | 0/62 | 0/35 | 75 |
| 0.800 | 0.355 | 0.981 | 0/62 | 0/35 | 54 |
| 0.900 | 0.250 | 0.974 | 0/62 | 0/35 | 38 |
| 0.950 | 0.197 | 1.000 | 0/62 | 0/35 | 30 |
| 0.990 | 0.112 | 1.000 | 0/62 | 0/35 | 17 |

### Por classe (política) — o que o Jev decide sozinho em cada classe

**Recorte `só IA`**

| classe | n em produção | decididos sozinho | … que concordam | concordância forçada (sem limiar) | Jev decidiu esta classe | … e produção concorda (precisão) |
|---|---|---|---|---|---|---|
| principal | 12 | 6 | 6 | 0.833 | 6 | 1.000 |
| notificacoes | 13 | 4 | 4 | 0.846 | 4 | 1.000 |
| promocoes | 27 | 18 | 18 | 0.889 | 18 | 1.000 |
| spam | 8 | 2 | 2 | 0.500 | 2 | 1.000 |
| golpe | 32 | 14 | 14 | 0.688 | 14 | 1.000 |

**Recorte `todos`**

| classe | n em produção | decididos sozinho | … que concordam | concordância forçada (sem limiar) | Jev decidiu esta classe | … e produção concorda (precisão) |
|---|---|---|---|---|---|---|
| principal | 35 | 20 | 20 | 0.771 | 20 | 1.000 |
| notificacoes | 18 | 9 | 9 | 0.889 | 9 | 1.000 |
| promocoes | 29 | 19 | 19 | 0.897 | 19 | 1.000 |
| spam | 8 | 2 | 2 | 0.500 | 2 | 1.000 |
| golpe | 62 | 19 | 19 | 0.839 | 19 | 1.000 |

### Matrizes de confusão (linhas = produção, colunas = Jev)

**Recorte `só IA` — decididos sozinho pela política** (44)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 6 | 0 | 0 | 0 | 0 | 0 |
| notificacoes | 0 | 4 | 0 | 0 | 0 | 0 |
| promocoes | 0 | 0 | 18 | 0 | 0 | 0 |
| spam | 0 | 0 | 0 | 0 | 2 | 0 |
| golpe | 0 | 0 | 0 | 0 | 0 | 14 |

**Recorte `só IA` — leitura forçada, todos os e-mails** (92)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 10 | 0 | 0 | 0 | 0 | 2 |
| notificacoes | 1 | 11 | 0 | 0 | 0 | 1 |
| promocoes | 0 | 0 | 24 | 0 | 2 | 1 |
| spam | 0 | 1 | 3 | 0 | 4 | 0 |
| golpe | 0 | 5 | 2 | 0 | 3 | 22 |

**Recorte `todos` — decididos sozinho pela política** (69)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 20 | 0 | 0 | 0 | 0 | 0 |
| notificacoes | 0 | 9 | 0 | 0 | 0 | 0 |
| promocoes | 0 | 0 | 19 | 0 | 0 | 0 |
| spam | 0 | 0 | 0 | 0 | 2 | 0 |
| golpe | 0 | 0 | 0 | 0 | 0 | 19 |

**Recorte `todos` — leitura forçada, todos os e-mails** (152)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 27 | 1 | 0 | 0 | 5 | 2 |
| notificacoes | 1 | 16 | 0 | 0 | 0 | 1 |
| promocoes | 0 | 0 | 26 | 0 | 2 | 1 |
| spam | 0 | 1 | 3 | 0 | 4 | 0 |
| golpe | 0 | 5 | 2 | 0 | 3 | 52 |

### Nouls por classe de produção — média (≥ 0.8 / ≤ 0.2), 152 e-mails com resposta

| noul | principal (n=35) | notificacoes (n=18) | promocoes (n=29) | spam (n=8) | golpe (n=62) |
|---|---|---|---|---|---|
| asks_money_or_credentials | 0.33 (9/23) | 0.08 (0/17) | 0.10 (0/24) | 0.21 (0/5) | 0.25 (5/36) |
| impersonates_known_sender | 0.37 (0/3) | 0.56 (5/1) | 0.34 (0/5) | 0.42 (3/4) | 0.59 (14/1) |
| pushes_to_act_on_pretext | 0.18 (0/26) | 0.14 (0/16) | 0.22 (1/18) | 0.18 (0/5) | 0.35 (7/24) |
| property_admin_mail | 0.74 (22/2) | 0.01 (0/18) | 0.06 (0/26) | 0.01 (0/8) | 0.04 (0/60) |
| human_wrote_to_this_recipient | 0.36 (10/22) | 0.02 (0/18) | 0.03 (0/29) | 0.03 (0/8) | 0.10 (0/59) |
| transactional_notice | 0.45 (12/16) | 0.75 (11/3) | 0.05 (0/29) | 0.13 (0/6) | 0.51 (21/20) |
| unsolicited_bulk_offer | 0.18 (6/29) | 0.16 (2/15) | 0.83 (23/1) | 0.82 (6/1) | 0.18 (6/48) |

**O que cada trava fez** (e-mails com confiança ≥ limiar da classe que a política mandou escalar mesmo assim): `erros barrados` = a classe do Jev discordava de produção; `acertos barrados` = concordava (cobertura perdida).

| trava | erros barrados | … dos quais erro caro | acertos barrados |
|---|---|---|---|
| `promocoes` × `impersonates_known_sender` | 2 | 0 | 0 |
| corpo curto (código) | 1 | 0 | 0 |

### Por que escalou (política, todos os recortes)

| motivo | e-mails |
|---|---|
| confiança abaixo do limiar (`golpe` < 0.8) | 37 |
| confiança abaixo do limiar (`notificacoes` < 0.7) | 13 |
| confiança abaixo do limiar (`spam` < 0.9) | 12 |
| confiança abaixo do limiar (`promocoes` < 0.7) | 10 |
| confiança abaixo do limiar (`principal` < 0.7) | 8 |
| conflito de Noul com `promocoes` | 2 |
| corpo curto para decidir classe de caixa de entrada | 1 |

### `redes_sociais` à parte (0 caso(s); nenhum no ajuste: fora do critério)

_(nenhum neste conjunto)_

### Custo e latência — Jev MEDIDO; LLM ESTIMADO (premissas no cabeçalho)

| e-mails | requisições | novas (não cache) | sem chamada (longo/vazio) | falhas operacionais (→ escala) | perguntas | p50_ms | p95_ms | tokens_por_e-mail | US$_total | US$_por_1000_e-mails | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 152 | 152 | 0 | 0 | 0 | 1216 | 260 | 342 | 2960 | 0.018895 | 0.1243 | jev-1.13.0 |

| recorte | LLM (premissa) | n | escalados | US$/1000: tudo no LLM | US$/1000: roteado (Jev + LLM nos escalados) | … só a parte Jev (medida) | economia |
|---|---|---|---|---|---|---|---|
| só IA | gpt-6-luna | 92 | 48 | 0.2505 | 0.2531 | 0.1248 | -1.1% |
| só IA | gpt-6-astra | 92 | 48 | 25.0476 | 12.9598 | 0.1248 | 48.3% |
| todos | gpt-6-luna | 152 | 83 | 0.2497 | 0.2582 | 0.1243 | -3.4% |
| todos | gpt-6-astra | 152 | 83 | 24.9680 | 13.5108 | 0.1243 | 45.9% |

No recorte `só regra` a produção não gasta LLM (a regra decide): o custo de `todos` é hipotético — vale o recorte `só IA`, que é o que hoje vai ao LLM.

### Decididos sozinho que discordam de produção — um a um (0; só IDs e números)

Por categoria: nenhum.

## Conjunto `teste` — 586 e-mails reais anonimizados, 179 remetentes (grupos)

Classe em produção: `principal` 223, `notificacoes` 64, `promocoes` 74, `redes_sociais` 6, `spam` 72, `golpe` 147. Quem decidiu em produção: `ai_api` 7, `ai_claude` 151, `ai_codex` 84, `crm` 9, `rule` 335. Corpo truncado na extração: 64/586. Registros com nome em maiúsculas mascarado na carga (última milha): 16. `redes_sociais`: 6 caso(s), fora das tabelas principais e do critério (seção própria).

### Roteamento por recorte — baseline × tudo no LLM × Jev, nos mesmos e-mails

**Gabarito = decisão de produção: tudo é concordância com produção, não acerto.** `cobertura` = fração que a variante decide sozinha (o resto escala ao LLM). `concordância entre decididos` = dos decididos sozinho, quantos batem com produção. `decidido E concorda / n` = automação útil. **GOLPE NA CAIXA** = golpe de produção decidido sozinho como `principal`/`notificacoes` (denominador: golpes do recorte). **CLIENTE PERDIDO** = `principal` de produção decidido sozinho como `spam`/`golpe` (denominador: principais do recorte). `ponta a ponta` conta o escalado como concordante (o LLM É o gabarito). Recortes: `só regra` = produção decidiu por regra; `só IA` = produção mandou a um LLM (o resíduo ambíguo: o caso de uso real do roteador); `todos` inclui também os decididos por `crm`. Variantes do Jev leem a MESMA resposta: `forçado` = sempre a classe mais provável; `só confiança` = limiar por classe, sem Nouls nem regra do corpo curto; `roteador` = a política de `perguntas.py`.

| recorte | variante | n | cobertura (decide sozinho) | concordância entre decididos | decidido E concorda / n | escalados | GOLPE NA CAIXA (golpe → principal/notificações, sozinho) | CLIENTE PERDIDO (principal → spam/golpe, sozinho) | concordância ponta a ponta (escalado = 1) |
|---|---|---|---|---|---|---|---|---|---|
| todos | baseline (regras de código) | 580 | 0.672 | 0.579 | 0.390 | 190 | 13/147 | 15/223 | 0.717 |
| todos | tudo no LLM (hoje) | 580 | 0.000 | — | 0.000 | 580 | 0/147 | 0/223 | 1.000 |
| todos | Jev forçado (sem limiar) | 580 | 1.000 | 0.667 | 0.667 | 0 | 22/147 | 35/223 | 0.667 |
| todos | Jev só confiança | 580 | 0.348 | 0.965 | 0.336 | 378 | 0/147 | 2/223 | 0.988 |
| todos | Jev roteador (política) | 580 | 0.340 | 0.975 | 0.331 | 383 | 0/147 | 2/223 | 0.991 |
| só regra | baseline (regras de código) | 329 | 0.669 | 0.682 | 0.456 | 109 | 1/75 | 2/147 | 0.787 |
| só regra | tudo no LLM (hoje) | 329 | 0.000 | — | 0.000 | 329 | 0/75 | 0/147 | 1.000 |
| só regra | Jev forçado (sem limiar) | 329 | 1.000 | 0.644 | 0.644 | 0 | 9/75 | 29/147 | 0.644 |
| só regra | Jev só confiança | 329 | 0.246 | 0.975 | 0.240 | 248 | 0/75 | 1/147 | 0.994 |
| só regra | Jev roteador (política) | 329 | 0.240 | 0.975 | 0.234 | 250 | 0/75 | 1/147 | 0.994 |
| só IA | baseline (regras de código) | 242 | 0.665 | 0.435 | 0.289 | 81 | 12/72 | 10/68 | 0.624 |
| só IA | tudo no LLM (hoje) | 242 | 0.000 | — | 0.000 | 242 | 0/72 | 0/68 | 1.000 |
| só IA | Jev forçado (sem limiar) | 242 | 1.000 | 0.690 | 0.690 | 0 | 13/72 | 6/68 | 0.690 |
| só IA | Jev só confiança | 242 | 0.475 | 0.957 | 0.455 | 127 | 0/72 | 1/68 | 0.979 |
| só IA | Jev roteador (política) | 242 | 0.463 | 0.973 | 0.450 | 130 | 0/72 | 1/68 | 0.988 |

### IC 95% da política — bootstrap agrupado por remetente (`grupo`), 2000 reamostragens

| recorte | grupos | cobertura | concordância entre decididos | golpe na caixa / golpes | cliente perdido / principais | ponta a ponta |
|---|---|---|---|---|---|---|
| todos | 178 | 0.340 [0.260; 0.426] | 0.975 [0.948; 0.995] | 0.000 [0.000; 0.000] | 0.009 [0.000; 0.023] | 0.991 [0.984; 0.998] |
| só regra | 57 | 0.240 [0.141; 0.348] | 0.975 [0.919; 1.000] | 0.000 [0.000; 0.000] | 0.007 [0.000; 0.022] | 0.994 [0.985; 1.000] |
| só IA | 123 | 0.463 [0.354; 0.579] | 0.973 [0.937; 1.000] | 0.000 [0.000; 0.000] | 0.015 [0.000; 0.056] | 0.988 [0.971; 1.000] |

**Critério congelado conferido no teste, recorte `só IA`** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 golpe na caixa (sozinho) | 0/72 (0.000) | ≤ 0.01 | ✓ |
| 2 cliente perdido (sozinho) | 1/68 (0.015) | ≤ 0.01 | ✗ |
| 3 concordância entre decididos | 109/112 (0.973) | ≥ 0.95 | ✓ |
| 4 cobertura | 112/242 (0.463) | ≥ 0.4 | ✓ |
| 5 o baseline de código não chega lá | baseline: golpe na caixa 12/72, cliente perdido 10/68, concordância 0.435, cobertura 0.665 | baseline falha em 1, 2 ou 3, ou cobre menos que o Jev | ✓ |
| informativo: cobertura ≥ 0.5 (sugestão do briefing) | 0.463 | ≥ 0.5 | ✗ (não decide) |

**Veredito calculado: NÃO PASSOU** (os 5 itens numerados).

### Curva cobertura × concordância × erro caro por limiar (mesmas respostas, zero chamada nova)

O MESMO limiar de confiança em todas as classes. `com a política` mantém os conflitos de Noul e a regra do corpo curto; `só confiança` desliga os dois. A linha de `perguntas.py` (limiar por classe) está na tabela principal.

**Recorte `só IA` — com a política**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.893 | 0.727 | 7/72 | 5/68 | 216 |
| 0.500 | 0.702 | 0.794 | 4/72 | 2/68 | 170 |
| 0.600 | 0.620 | 0.860 | 2/72 | 1/68 | 150 |
| 0.700 | 0.500 | 0.975 | 0/72 | 1/68 | 121 |
| 0.800 | 0.393 | 0.989 | 0/72 | 1/68 | 95 |
| 0.900 | 0.310 | 1.000 | 0/72 | 0/68 | 75 |
| 0.950 | 0.227 | 1.000 | 0/72 | 0/68 | 55 |
| 0.990 | 0.062 | 1.000 | 0/72 | 0/68 | 15 |

**Recorte `só IA` — só confiança**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.690 | 13/72 | 6/68 | 242 |
| 0.500 | 0.752 | 0.769 | 5/72 | 2/68 | 182 |
| 0.600 | 0.657 | 0.830 | 3/72 | 1/68 | 159 |
| 0.700 | 0.512 | 0.960 | 0/72 | 1/68 | 124 |
| 0.800 | 0.401 | 0.979 | 0/72 | 1/68 | 97 |
| 0.900 | 0.318 | 0.987 | 0/72 | 0/68 | 77 |
| 0.950 | 0.227 | 1.000 | 0/72 | 0/68 | 55 |
| 0.990 | 0.062 | 1.000 | 0/72 | 0/68 | 15 |

**Recorte `todos` — com a política**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.907 | 0.700 | 16/147 | 22/223 | 526 |
| 0.500 | 0.633 | 0.728 | 5/147 | 12/223 | 367 |
| 0.600 | 0.505 | 0.812 | 2/147 | 4/223 | 293 |
| 0.700 | 0.367 | 0.944 | 0/147 | 3/223 | 213 |
| 0.800 | 0.255 | 0.980 | 0/147 | 2/223 | 148 |
| 0.900 | 0.197 | 0.991 | 0/147 | 1/223 | 114 |
| 0.950 | 0.140 | 1.000 | 0/147 | 0/223 | 81 |
| 0.990 | 0.041 | 1.000 | 0/147 | 0/223 | 24 |

**Recorte `todos` — só confiança**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.667 | 22/147 | 35/223 | 580 |
| 0.500 | 0.672 | 0.710 | 6/147 | 14/223 | 390 |
| 0.600 | 0.534 | 0.794 | 3/147 | 5/223 | 310 |
| 0.700 | 0.378 | 0.932 | 0/147 | 4/223 | 219 |
| 0.800 | 0.260 | 0.974 | 0/147 | 2/223 | 151 |
| 0.900 | 0.202 | 0.983 | 0/147 | 1/223 | 117 |
| 0.950 | 0.140 | 1.000 | 0/147 | 0/223 | 81 |
| 0.990 | 0.041 | 1.000 | 0/147 | 0/223 | 24 |

### Por classe (política) — o que o Jev decide sozinho em cada classe

**Recorte `só IA`**

| classe | n em produção | decididos sozinho | … que concordam | concordância forçada (sem limiar) | Jev decidiu esta classe | … e produção concorda (precisão) |
|---|---|---|---|---|---|---|
| principal | 68 | 37 | 34 | 0.779 | 34 | 1.000 |
| notificacoes | 25 | 6 | 6 | 0.680 | 8 | 0.750 |
| promocoes | 42 | 28 | 28 | 0.810 | 28 | 1.000 |
| spam | 35 | 3 | 3 | 0.143 | 3 | 1.000 |
| golpe | 72 | 38 | 38 | 0.806 | 39 | 0.974 |

**Recorte `todos`**

| classe | n em produção | decididos sozinho | … que concordam | concordância forçada (sem limiar) | Jev decidiu esta classe | … e produção concorda (precisão) |
|---|---|---|---|---|---|---|
| principal | 223 | 81 | 77 | 0.713 | 77 | 1.000 |
| notificacoes | 64 | 15 | 15 | 0.672 | 17 | 0.882 |
| promocoes | 74 | 51 | 51 | 0.878 | 52 | 0.981 |
| spam | 72 | 4 | 3 | 0.069 | 3 | 1.000 |
| golpe | 147 | 46 | 46 | 0.782 | 48 | 0.958 |

### Matrizes de confusão (linhas = produção, colunas = Jev)

**Recorte `só IA` — decididos sozinho pela política** (112)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 34 | 2 | 0 | 0 | 0 | 1 |
| notificacoes | 0 | 6 | 0 | 0 | 0 | 0 |
| promocoes | 0 | 0 | 28 | 0 | 0 | 0 |
| spam | 0 | 0 | 0 | 0 | 3 | 0 |
| golpe | 0 | 0 | 0 | 0 | 0 | 38 |

**Recorte `só IA` — leitura forçada, todos os e-mails** (242)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 53 | 9 | 0 | 0 | 1 | 5 |
| notificacoes | 0 | 17 | 0 | 0 | 0 | 8 |
| promocoes | 1 | 0 | 34 | 0 | 6 | 1 |
| spam | 0 | 2 | 28 | 0 | 5 | 0 |
| golpe | 7 | 6 | 1 | 0 | 0 | 58 |

**Recorte `todos` — decididos sozinho pela política** (197)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 77 | 2 | 0 | 0 | 0 | 2 |
| notificacoes | 0 | 15 | 0 | 0 | 0 | 0 |
| promocoes | 0 | 0 | 51 | 0 | 0 | 0 |
| spam | 0 | 0 | 1 | 0 | 3 | 0 |
| golpe | 0 | 0 | 0 | 0 | 0 | 46 |

**Recorte `todos` — leitura forçada, todos os e-mails** (580)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 159 | 28 | 1 | 0 | 5 | 30 |
| notificacoes | 7 | 43 | 0 | 0 | 0 | 14 |
| promocoes | 1 | 0 | 65 | 0 | 7 | 1 |
| spam | 0 | 2 | 65 | 0 | 5 | 0 |
| golpe | 9 | 13 | 1 | 0 | 9 | 115 |

### Nouls por classe de produção — média (≥ 0.8 / ≤ 0.2), 580 e-mails com resposta

| noul | principal (n=223) | notificacoes (n=64) | promocoes (n=74) | spam (n=72) | golpe (n=147) |
|---|---|---|---|---|---|
| asks_money_or_credentials | 0.47 (74/92) | 0.18 (1/48) | 0.20 (3/58) | 0.27 (1/6) | 0.42 (35/53) |
| impersonates_known_sender | 0.34 (1/35) | 0.34 (0/9) | 0.31 (0/24) | 0.19 (2/64) | 0.58 (33/8) |
| pushes_to_act_on_pretext | 0.25 (1/102) | 0.19 (0/46) | 0.24 (1/47) | 0.12 (0/68) | 0.43 (20/28) |
| property_admin_mail | 0.64 (129/54) | 0.19 (9/48) | 0.05 (0/68) | 0.01 (0/72) | 0.06 (0/135) |
| human_wrote_to_this_recipient | 0.29 (46/148) | 0.08 (0/62) | 0.03 (0/73) | 0.03 (0/72) | 0.13 (0/129) |
| transactional_notice | 0.64 (121/44) | 0.82 (52/4) | 0.07 (0/67) | 0.09 (0/70) | 0.49 (38/51) |
| unsolicited_bulk_offer | 0.06 (1/214) | 0.05 (0/63) | 0.86 (60/2) | 0.94 (69/1) | 0.21 (16/113) |

**O que cada trava fez** (e-mails com confiança ≥ limiar da classe que a política mandou escalar mesmo assim): `erros barrados` = a classe do Jev discordava de produção; `acertos barrados` = concordava (cobertura perdida).

| trava | erros barrados | … dos quais erro caro | acertos barrados |
|---|---|---|---|
| `promocoes` × `asks_money_or_credentials` | 0 | 0 | 1 |
| `promocoes` × `impersonates_known_sender` | 1 | 0 | 0 |
| corpo curto (código) | 1 | 0 | 2 |

### Por que escalou (política, todos os recortes)

| motivo | e-mails |
|---|---|
| confiança abaixo do limiar (`golpe` < 0.8) | 112 |
| confiança abaixo do limiar (`principal` < 0.7) | 97 |
| confiança abaixo do limiar (`promocoes` < 0.7) | 78 |
| confiança abaixo do limiar (`notificacoes` < 0.7) | 68 |
| confiança abaixo do limiar (`spam` < 0.9) | 23 |
| corpo curto para decidir classe de caixa de entrada | 3 |
| conflito de Noul com `promocoes` | 2 |

### `redes_sociais` à parte (6 caso(s); nenhum no ajuste: fora do critério)

| id | decidido_por | Jev leu | confiança | ação | concorda |
|---|---|---|---|---|---|
| EM-0317 | rule | redes_sociais | 0.910 | decide | ✓ |
| EM-0444 | rule | redes_sociais | 0.870 | decide | ✓ |
| EM-0607 | rule | redes_sociais | 0.890 | decide | ✓ |
| EM-0659 | rule | redes_sociais | 0.800 | decide | ✓ |
| EM-0686 | rule | golpe | 0.600 | escala | ✗ |
| EM-0696 | rule | redes_sociais | 0.920 | decide | ✓ |

### Custo e latência — Jev MEDIDO; LLM ESTIMADO (premissas no cabeçalho)

| e-mails | requisições | novas (não cache) | sem chamada (longo/vazio) | falhas operacionais (→ escala) | perguntas | p50_ms | p95_ms | tokens_por_e-mail | US$_total | US$_por_1000_e-mails | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 586 | 586 | 537 | 0 | 0 | 4688 | 269 | 320 | 3025 | 0.074444 | 0.1270 | jev-1.13.0 |

| recorte | LLM (premissa) | n | escalados | US$/1000: tudo no LLM | US$/1000: roteado (Jev + LLM nos escalados) | … só a parte Jev (medida) | economia |
|---|---|---|---|---|---|---|---|
| só IA | gpt-6-luna | 242 | 130 | 0.2568 | 0.2669 | 0.1283 | -3.9% |
| só IA | gpt-6-astra | 242 | 130 | 25.6800 | 13.9849 | 0.1283 | 45.5% |
| todos | gpt-6-luna | 580 | 383 | 0.2556 | 0.2957 | 0.1271 | -15.7% |
| todos | gpt-6-astra | 580 | 383 | 25.5631 | 16.9799 | 0.1271 | 33.6% |

No recorte `só regra` a produção não gasta LLM (a regra decide): o custo de `todos` é hipotético — vale o recorte `só IA`, que é o que hoje vai ao LLM.

### Decididos sozinho que discordam de produção — um a um (5; só IDs e números)

Por categoria: `principal → golpe` 2; `principal → notificacoes` 2; `spam → promocoes` 1.

| id | decidido_por | produção | Jev | confiança | caro | asks_money_or_credentials | impersonates_known_sender | pushes_to_act_on_pretext | property_admin_mail | human_wrote_to_this_recipient | transactional_notice | unsolicited_bulk_offer | dkim_aligned | list_unsubscribe | corpo (caracteres) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EM-0207 | ai_claude | principal | golpe | 0.81 | CLIENTE PERDIDO | 0.68 | 0.51 | 0.59 | 0.02 | 0.04 | 0.87 | 0.25 | True | False | 3231 |
| EM-0624 | ai_claude | principal | notificacoes | 0.71 |  | 0.14 | 0.34 | 0.15 | 0.27 | 0.13 | 0.93 | 0.05 | True | False | 717 |
| EM-0675 | rule | spam | promocoes | 0.71 |  | 0.29 | 0.18 | 0.11 | 0.01 | 0.02 | 0.09 | 0.97 | False | False | 2752 |
| EM-0701 | ai_codex | principal | notificacoes | 0.77 |  | 0.58 | 0.70 | 0.20 | 0.02 | 0.05 | 0.94 | 0.04 | True | True | 475 |
| EM-0728 | rule | principal | golpe | 0.92 | CLIENTE PERDIDO | 0.67 | 0.89 | 0.52 | 0.01 | 0.02 | 0.73 | 0.05 | True | True | 104 |
