# Resultados — roteador-email

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, limiares e política: `perguntas.py`; validação, composição e baseline: `roteador.py`.

> **Dado real, relatório sem texto.** E-mails de produção já classificados pelo F11, anonimizados; o texto e o cache do Jev ficam fora do Git. Aqui só há agregados, IDs `EM-xxxx`, classes e números.
>
> **Gabarito = a decisão do sistema em produção** (regra, Claude, Codex, API ou CRM). Toda taxa é CONCORDÂNCIA com produção, não acerto contra verdade independente. Escalar = mandar ao LLM de produção, que concorda por definição.

Limiares em vigor: confiança por classe {'principal': 0.7, 'notificacoes': 0.7, 'promocoes': 0.7, 'redes_sociais': 0.7, 'spam': 0.9, 'golpe': 0.8}; Noul sim ≥ 0.8, não ≤ 0.2; corpo < 80 caracteres não decide classe de caixa de entrada; teto do corpo 4500.

Custo: Jev MEDIDO (tokens reais × US$ 0.042/M de entrada). LLM ESTIMADO, nada é chamado — `gpt-6-luna` US$ 0.1/0.5 e `gpt-6-astra` US$ 10.0/50.0 por 1M entrada/saída (premissas de `../roteador-jev-llm/run.py`); por e-mail: 1500 tokens de instruções + caracteres × 0.25 → 150 de saída.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste, recorte `só IA` (produção decidiu por LLM: `decidido_por` = ai_*), sem os casos `redes_sociais`, com a política acima. Gabarito = decisão de produção (concordância, não acerto); **1_golpe_na_caixa**: golpe de produção decidido sozinho como `principal`/`notificacoes` ≤ 1% dos golpes do recorte; **2_cliente_perdido**: `principal` de produção decidido sozinho como `spam`/`golpe` ≤ 1% dos principais do recorte; **3_concordancia**: concordância com produção entre os decididos sozinho ≥ 0,95; **4_cobertura**: decide sozinho ≥ 40% do recorte (o briefing sugeria 50% como exemplo; o ajuste, com limiares escolhidos nele mesmo, deu 48% — o relatório mostra a linha dos 50% como informativa); **5_contra_baseline**: o baseline de código NÃO chega lá: falha em 1, 2 ou 3, ou cobre menos que o Jev (se o baseline passar em 1–3 com cobertura ≥ a do Jev, a regra de código basta); **secundario_nao_decide**: os mesmos números nos recortes `todos` e `só regra`; `redes_sociais` à parte; custo roteado × tudo no LLM; o que cada trava de Noul barrou; **se_falhar**: 1 ou 2 falhando = não serve para decidir sozinho o lado caro; 3 falhando = a confiança não separa o que concorda; 4 falhando = seguro, mas tira pouco do LLM; 5 falhando = a regra de código basta

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T15:41:06-03:00): `perguntas.py` sha256 65d020c4d58b9728… · `roteador.py` sha256 4cdf8ef5f4aee6ee… · `run.py` sha256 a8971be31696da89… · `emails-anon-v2.jsonl` sha256 409b5cc3ef22911c…

## Lado a lado

Gabarito = decisão de produção (concordância, não acerto); escalado conta como concordante.

| conjunto | recorte | variante | n | cobertura (decide sozinho) | concordância entre decididos | decidido E concorda / n | escalados | GOLPE NA CAIXA (golpe → principal/notificações, sozinho) | CLIENTE PERDIDO (principal → spam/golpe, sozinho) | concordância ponta a ponta (escalado = 1) |
|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | todos | baseline (regras de código) | 152 | 0.605 | 0.717 | 0.434 | 60 | 4/62 | 7/35 | 0.829 |
| ajuste | todos | Jev forçado (sem limiar) | 152 | 1.000 | 0.836 | 0.836 | 0 | 5/62 | 6/35 | 0.836 |
| ajuste | todos | Jev roteador (política) | 152 | 0.388 | 1.000 | 0.388 | 93 | 0/62 | 0/35 | 1.000 |
| ajuste | só regra | baseline (regras de código) | 57 | 0.632 | 0.861 | 0.544 | 21 | 1/30 | 2/20 | 0.912 |
| ajuste | só regra | Jev forçado (sem limiar) | 57 | 1.000 | 0.895 | 0.895 | 0 | 0/30 | 5/20 | 0.895 |
| ajuste | só regra | Jev roteador (política) | 57 | 0.333 | 1.000 | 0.333 | 38 | 0/30 | 0/20 | 1.000 |
| ajuste | só IA | baseline (regras de código) | 92 | 0.609 | 0.625 | 0.380 | 36 | 3/32 | 5/12 | 0.772 |
| ajuste | só IA | Jev forçado (sem limiar) | 92 | 1.000 | 0.793 | 0.793 | 0 | 5/32 | 1/12 | 0.793 |
| ajuste | só IA | Jev roteador (política) | 92 | 0.402 | 1.000 | 0.402 | 55 | 0/32 | 0/12 | 1.000 |
| teste | todos | baseline (regras de código) | 580 | 0.672 | 0.579 | 0.390 | 190 | 13/147 | 15/223 | 0.717 |
| teste | todos | Jev forçado (sem limiar) | 580 | 0.995 | 0.669 | 0.666 | 3 | 21/147 | 39/223 | 0.671 |
| teste | todos | Jev roteador (política) | 580 | 0.303 | 0.977 | 0.297 | 404 | 0/147 | 2/223 | 0.993 |
| teste | só regra | baseline (regras de código) | 329 | 0.669 | 0.682 | 0.456 | 109 | 1/75 | 2/147 | 0.787 |
| teste | só regra | Jev forçado (sem limiar) | 329 | 0.994 | 0.645 | 0.641 | 2 | 9/75 | 30/147 | 0.647 |
| teste | só regra | Jev roteador (política) | 329 | 0.210 | 0.986 | 0.207 | 260 | 0/75 | 1/147 | 0.997 |
| teste | só IA | baseline (regras de código) | 242 | 0.665 | 0.435 | 0.289 | 81 | 12/72 | 10/68 | 0.624 |
| teste | só IA | Jev forçado (sem limiar) | 242 | 0.996 | 0.693 | 0.690 | 1 | 12/72 | 9/68 | 0.694 |
| teste | só IA | Jev roteador (política) | 242 | 0.430 | 0.971 | 0.417 | 138 | 0/72 | 1/68 | 0.988 |

| conjunto | e-mails | requisições | falhas | p50_ms | p95_ms | tokens_por_e-mail | US$_por_1000_e-mails (Jev) | modelo | critério |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | 152 | 152 | 0 | 280 | 338 | 2978 | 0.1251 | jev-1.13.0 | PASSOU (informativo) |
| teste | 586 | 583 | 0 | 274 | 323 | 3045 | 0.1272 | jev-1.13.0 | NÃO PASSOU |

## Conjunto `ajuste` — 152 e-mails reais anonimizados, 69 remetentes (grupos)

Classe em produção: `principal` 35, `notificacoes` 18, `promocoes` 29, `spam` 8, `golpe` 62. Quem decidiu em produção: `ai_api` 1, `ai_claude` 60, `ai_codex` 31, `crm` 3, `rule` 57. Corpo truncado na extração: 23/152. Máscara de última milha na carga (nome em maiúsculas após saudação → `[NOME]`): 0 registro(s), 0 troca(s). Registros inválidos na carga (→ falha operacional): 0. `redes_sociais`: 0 caso(s), fora das tabelas principais e do critério (seção própria).

### Roteamento por recorte — baseline × tudo no LLM × Jev, nos mesmos e-mails

**Gabarito = decisão de produção: tudo é concordância com produção, não acerto.** `cobertura` = fração que a variante decide sozinha (o resto escala ao LLM). `concordância entre decididos` = dos decididos sozinho, quantos batem com produção. `decidido E concorda / n` = automação útil. **GOLPE NA CAIXA** = golpe de produção decidido sozinho como `principal`/`notificacoes` (denominador: golpes do recorte). **CLIENTE PERDIDO** = `principal` de produção decidido sozinho como `spam`/`golpe` (denominador: principais do recorte). `ponta a ponta` conta o escalado como concordante (o LLM É o gabarito). Recortes: `só regra` = produção decidiu por regra; `só IA` = produção mandou a um LLM (o resíduo ambíguo: o caso de uso real do roteador); `todos` inclui também os decididos por `crm`. Variantes do Jev leem a MESMA resposta: `forçado` = sempre a classe mais provável; `só confiança` = limiar por classe, sem Nouls nem regra do corpo curto; `roteador` = a política de `perguntas.py`.

| recorte | variante | n | cobertura (decide sozinho) | concordância entre decididos | decidido E concorda / n | escalados | GOLPE NA CAIXA (golpe → principal/notificações, sozinho) | CLIENTE PERDIDO (principal → spam/golpe, sozinho) | concordância ponta a ponta (escalado = 1) |
|---|---|---|---|---|---|---|---|---|---|
| todos | baseline (regras de código) | 152 | 0.605 | 0.717 | 0.434 | 60 | 4/62 | 7/35 | 0.829 |
| todos | tudo no LLM (hoje) | 152 | 0.000 | — | 0.000 | 152 | 0/62 | 0/35 | 1.000 |
| todos | Jev forçado (sem limiar) | 152 | 1.000 | 0.836 | 0.836 | 0 | 5/62 | 6/35 | 0.836 |
| todos | Jev só confiança | 152 | 0.447 | 0.956 | 0.428 | 84 | 0/62 | 0/35 | 0.980 |
| todos | Jev roteador (política) | 152 | 0.388 | 1.000 | 0.388 | 93 | 0/62 | 0/35 | 1.000 |
| só regra | baseline (regras de código) | 57 | 0.632 | 0.861 | 0.544 | 21 | 1/30 | 2/20 | 0.912 |
| só regra | tudo no LLM (hoje) | 57 | 0.000 | — | 0.000 | 57 | 0/30 | 0/20 | 1.000 |
| só regra | Jev forçado (sem limiar) | 57 | 1.000 | 0.895 | 0.895 | 0 | 0/30 | 5/20 | 0.895 |
| só regra | Jev só confiança | 57 | 0.368 | 1.000 | 0.368 | 36 | 0/30 | 0/20 | 1.000 |
| só regra | Jev roteador (política) | 57 | 0.333 | 1.000 | 0.333 | 38 | 0/30 | 0/20 | 1.000 |
| só IA | baseline (regras de código) | 92 | 0.609 | 0.625 | 0.380 | 36 | 3/32 | 5/12 | 0.772 |
| só IA | tudo no LLM (hoje) | 92 | 0.000 | — | 0.000 | 92 | 0/32 | 0/12 | 1.000 |
| só IA | Jev forçado (sem limiar) | 92 | 1.000 | 0.793 | 0.793 | 0 | 5/32 | 1/12 | 0.793 |
| só IA | Jev só confiança | 92 | 0.478 | 0.932 | 0.446 | 48 | 0/32 | 0/12 | 0.967 |
| só IA | Jev roteador (política) | 92 | 0.402 | 1.000 | 0.402 | 55 | 0/32 | 0/12 | 1.000 |

### IC 95% da política — bootstrap agrupado por remetente (`grupo`), 2000 reamostragens

| recorte | grupos | cobertura | concordância entre decididos | golpe na caixa / golpes | cliente perdido / principais | ponta a ponta |
|---|---|---|---|---|---|---|
| todos | 69 | 0.388 [0.279; 0.519] | 1.000 [1.000; 1.000] | 0.000 [0.000; 0.000] | 0.000 [0.000; 0.000] | 1.000 [1.000; 1.000] |
| só regra | 17 | 0.333 [0.157; 0.581] | 1.000 [1.000; 1.000] | 0.000 [0.000; 0.000] | 0.000 [0.000; 0.000] | 1.000 [1.000; 1.000] |
| só IA | 51 | 0.402 [0.269; 0.562] | 1.000 [1.000; 1.000] | 0.000 [0.000; 0.000] | 0.000 [0.000; 0.000] | 1.000 [1.000; 1.000] |

### Política por state único — campanhas repetidas contadas uma vez

O mesmo texto (state idêntico depois da máscara) aparece em vários e-mails, inclusive entre ajuste e teste. `por e-mail` = as tabelas acima (cada registro conta 1). `state único` = cada state distinto conta 1 (fica o primeiro registro). `sem states do ajuste` = state único, tirando os states que também aparecem no ajuste (no `ajuste`, tira os repetidos dentro dele mesmo). Mesmas respostas do Jev, nenhuma chamada nova.

| recorte | denominador | n | cobertura | concordância entre decididos | golpe na caixa | cliente perdido |
|---|---|---|---|---|---|---|
| todos | por e-mail | 152 | 0.388 | 59/59 (1.000) | 0/62 | 0/35 |
| todos | state único | 143 | 0.399 | 57/57 (1.000) | 0/60 | 0/34 |
| todos | sem states do ajuste | 135 | 0.407 | 55/55 (1.000) | 0/58 | 0/33 |
| só regra | por e-mail | 57 | 0.333 | 19/19 (1.000) | 0/30 | 0/20 |
| só regra | state único | 55 | 0.345 | 19/19 (1.000) | 0/29 | 0/19 |
| só regra | sem states do ajuste | 53 | 0.358 | 19/19 (1.000) | 0/28 | 0/18 |
| só IA | por e-mail | 92 | 0.402 | 37/37 (1.000) | 0/32 | 0/12 |
| só IA | state único | 85 | 0.412 | 35/35 (1.000) | 0/31 | 0/12 |
| só IA | sem states do ajuste | 79 | 0.418 | 33/33 (1.000) | 0/30 | 0/12 |

**Critério conferido no `ajuste`, recorte `só IA`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 golpe na caixa (sozinho) | 0/32 (0.000) | ≤ 0.01 | ✓ |
| 2 cliente perdido (sozinho) | 0/12 (0.000) | ≤ 0.01 | ✓ |
| 3 concordância entre decididos | 37/37 (1.000) | ≥ 0.95 | ✓ |
| 4 cobertura | 37/92 (0.402) | ≥ 0.4 | ✓ |
| 5 o baseline de código não chega lá | baseline: golpe na caixa 3/32, cliente perdido 5/12, concordância 0.625, cobertura 0.609 | baseline falha em 1, 2 ou 3, ou cobre menos que o Jev | ✓ |
| informativo: cobertura ≥ 0.5 (sugestão do briefing) | 0.402 | ≥ 0.5 | ✗ (não decide) |

**Veredito calculado: PASSOU** (os 5 itens numerados).

### Curva cobertura × concordância × erro caro por limiar (mesmas respostas, zero chamada nova)

O MESMO limiar de confiança em todas as classes. `com a política` mantém os conflitos de Noul e a regra do corpo curto; `só confiança` desliga os dois. A linha de `perguntas.py` (limiar por classe) está na tabela principal.

**Recorte `só IA` — com a política**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.772 | 0.859 | 0/32 | 0/12 | 71 |
| 0.500 | 0.576 | 0.925 | 0/32 | 0/12 | 53 |
| 0.600 | 0.511 | 0.936 | 0/32 | 0/12 | 47 |
| 0.700 | 0.435 | 0.975 | 0/32 | 0/12 | 40 |
| 0.800 | 0.315 | 1.000 | 0/32 | 0/12 | 29 |
| 0.900 | 0.239 | 1.000 | 0/32 | 0/12 | 22 |
| 0.950 | 0.207 | 1.000 | 0/32 | 0/12 | 19 |
| 0.990 | 0.098 | 1.000 | 0/32 | 0/12 | 9 |

**Recorte `só IA` — só confiança**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.946 | 0.782 | 5/32 | 1/12 | 87 |
| 0.500 | 0.696 | 0.844 | 3/32 | 0/12 | 64 |
| 0.600 | 0.587 | 0.889 | 0/32 | 0/12 | 54 |
| 0.700 | 0.467 | 0.907 | 0/32 | 0/12 | 43 |
| 0.800 | 0.337 | 0.935 | 0/32 | 0/12 | 31 |
| 0.900 | 0.250 | 0.957 | 0/32 | 0/12 | 23 |
| 0.950 | 0.207 | 1.000 | 0/32 | 0/12 | 19 |
| 0.990 | 0.098 | 1.000 | 0/32 | 0/12 | 9 |

**Recorte `todos` — com a política**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.822 | 0.904 | 0/62 | 1/35 | 125 |
| 0.500 | 0.586 | 0.944 | 0/62 | 0/35 | 89 |
| 0.600 | 0.500 | 0.947 | 0/62 | 0/35 | 76 |
| 0.700 | 0.414 | 0.984 | 0/62 | 0/35 | 63 |
| 0.800 | 0.309 | 1.000 | 0/62 | 0/35 | 47 |
| 0.900 | 0.217 | 1.000 | 0/62 | 0/35 | 33 |
| 0.950 | 0.191 | 1.000 | 0/62 | 0/35 | 29 |
| 0.990 | 0.105 | 1.000 | 0/62 | 0/35 | 16 |

**Recorte `todos` — só confiança**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.954 | 0.828 | 5/62 | 6/35 | 145 |
| 0.500 | 0.658 | 0.890 | 3/62 | 0/35 | 100 |
| 0.600 | 0.546 | 0.916 | 0/62 | 0/35 | 83 |
| 0.700 | 0.434 | 0.939 | 0/62 | 0/35 | 66 |
| 0.800 | 0.322 | 0.959 | 0/62 | 0/35 | 49 |
| 0.900 | 0.224 | 0.971 | 0/62 | 0/35 | 34 |
| 0.950 | 0.191 | 1.000 | 0/62 | 0/35 | 29 |
| 0.990 | 0.105 | 1.000 | 0/62 | 0/35 | 16 |

### Por classe (política) — o que o Jev decide sozinho em cada classe

**Recorte `só IA`**

| classe | n em produção | decididos sozinho | … que concordam | concordância forçada (sem limiar) | Jev decidiu esta classe | … e produção concorda (precisão) |
|---|---|---|---|---|---|---|
| principal | 12 | 2 | 2 | 0.917 | 2 | 1.000 |
| notificacoes | 13 | 4 | 4 | 0.769 | 4 | 1.000 |
| promocoes | 27 | 15 | 15 | 0.926 | 15 | 1.000 |
| spam | 8 | 2 | 2 | 0.500 | 2 | 1.000 |
| golpe | 32 | 14 | 14 | 0.719 | 14 | 1.000 |

**Recorte `todos`**

| classe | n em produção | decididos sozinho | … que concordam | concordância forçada (sem limiar) | Jev decidiu esta classe | … e produção concorda (precisão) |
|---|---|---|---|---|---|---|
| principal | 35 | 14 | 14 | 0.800 | 14 | 1.000 |
| notificacoes | 18 | 8 | 8 | 0.833 | 8 | 1.000 |
| promocoes | 29 | 16 | 16 | 0.931 | 16 | 1.000 |
| spam | 8 | 2 | 2 | 0.500 | 2 | 1.000 |
| golpe | 62 | 19 | 19 | 0.855 | 19 | 1.000 |

### Matrizes de confusão (linhas = produção, colunas = Jev)

**Recorte `só IA` — decididos sozinho pela política** (37)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 2 | 0 | 0 | 0 | 0 | 0 |
| notificacoes | 0 | 4 | 0 | 0 | 0 | 0 |
| promocoes | 0 | 0 | 15 | 0 | 0 | 0 |
| spam | 0 | 0 | 0 | 0 | 2 | 0 |
| golpe | 0 | 0 | 0 | 0 | 0 | 14 |

**Recorte `só IA` — leitura forçada, todos os e-mails** (92)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 11 | 0 | 0 | 0 | 0 | 1 |
| notificacoes | 1 | 10 | 1 | 0 | 0 | 1 |
| promocoes | 0 | 0 | 25 | 0 | 1 | 1 |
| spam | 0 | 1 | 3 | 0 | 4 | 0 |
| golpe | 0 | 5 | 1 | 0 | 3 | 23 |

**Recorte `todos` — decididos sozinho pela política** (59)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 14 | 0 | 0 | 0 | 0 | 0 |
| notificacoes | 0 | 8 | 0 | 0 | 0 | 0 |
| promocoes | 0 | 0 | 16 | 0 | 0 | 0 |
| spam | 0 | 0 | 0 | 0 | 2 | 0 |
| golpe | 0 | 0 | 0 | 0 | 0 | 19 |

**Recorte `todos` — leitura forçada, todos os e-mails** (152)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 28 | 1 | 0 | 0 | 5 | 1 |
| notificacoes | 1 | 15 | 1 | 0 | 0 | 1 |
| promocoes | 0 | 0 | 27 | 0 | 1 | 1 |
| spam | 0 | 1 | 3 | 0 | 4 | 0 |
| golpe | 0 | 5 | 1 | 0 | 3 | 53 |

### Nouls por classe de produção — média (≥ 0.8 / ≤ 0.2), 152 e-mails com resposta

| noul | principal (n=35) | notificacoes (n=18) | promocoes (n=29) | spam (n=8) | golpe (n=62) |
|---|---|---|---|---|---|
| asks_money_or_credentials | 0.33 (9/23) | 0.08 (0/17) | 0.10 (0/24) | 0.21 (0/5) | 0.26 (5/36) |
| impersonates_known_sender | 0.37 (0/2) | 0.56 (5/1) | 0.34 (0/7) | 0.41 (2/4) | 0.59 (16/1) |
| pushes_to_act_on_pretext | 0.19 (0/25) | 0.14 (0/16) | 0.23 (1/19) | 0.18 (0/5) | 0.34 (7/24) |
| property_admin_mail | 0.73 (22/3) | 0.01 (0/18) | 0.06 (0/26) | 0.01 (0/8) | 0.04 (0/60) |
| human_wrote_to_this_recipient | 0.36 (10/22) | 0.03 (0/18) | 0.03 (0/29) | 0.03 (0/8) | 0.10 (0/59) |
| transactional_notice | 0.46 (12/16) | 0.74 (11/3) | 0.05 (0/29) | 0.12 (0/7) | 0.51 (21/22) |
| unsolicited_bulk_offer | 0.18 (6/29) | 0.16 (2/15) | 0.83 (23/1) | 0.82 (6/1) | 0.18 (6/50) |

**O que cada trava fez** (e-mails com confiança ≥ limiar da classe que a política mandou escalar mesmo assim): `erros barrados` = a classe do Jev discordava de produção; `acertos barrados` = concordava (cobertura perdida). `corpo truncado (código)` é a regra posta depois da rodada 1 (`P.CLASSES_CARAS`).

| trava | erros barrados | … dos quais erro caro | acertos barrados |
|---|---|---|---|
| `promocoes` × `impersonates_known_sender` | 2 | 0 | 0 |
| corpo curto (código) | 1 | 0 | 0 |
| truncado (código) | 0 | 0 | 6 |

### Por que escalou (política, todos os recortes)

| motivo | e-mails |
|---|---|
| confiança abaixo do limiar (`golpe` < 0.8) | 37 |
| confiança abaixo do limiar (`promocoes` < 0.7) | 14 |
| confiança abaixo do limiar (`notificacoes` < 0.7) | 12 |
| confiança abaixo do limiar (`spam` < 0.9) | 11 |
| confiança abaixo do limiar (`principal` < 0.7) | 10 |
| corpo truncado na extração (`principal` é classe cara) | 5 |
| conflito de Noul com `promocoes` | 2 |
| corpo curto para decidir classe de caixa de entrada | 1 |
| corpo truncado na extração (`notificacoes` é classe cara) | 1 |

**Regra do corpo truncado** (código, posta depois da rodada 1): 23 e-mail(s) com resposta do Jev e corpo truncado; 6 barrado(s) por ela (confiança ≥ limiar, classe cara, sem corpo curto antes): 6 concordavam com produção, 0 discordavam, dos quais 0 erro(s) caro(s).

### `redes_sociais` à parte (0 caso(s); nenhum no ajuste: fora do critério)

_(nenhum neste conjunto)_

### Custo e latência — Jev MEDIDO; LLM ESTIMADO (premissas no cabeçalho)

| e-mails | requisições | novas (não cache) | sem chamada (longo/vazio) | falhas operacionais (→ escala) | perguntas | p50_ms | p95_ms | tokens_por_e-mail | US$_total | US$_por_1000_e-mails | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 152 | 152 | 0 | 0 | 0 | 1216 | 280 | 338 | 2978 | 0.019010 | 0.1251 | jev-1.13.0 |

| recorte | LLM (premissa) | n | escalados | US$/1000: tudo no LLM | US$/1000: roteado (Jev + LLM nos escalados) | … só a parte Jev (medida) | economia |
|---|---|---|---|---|---|---|---|
| só IA | gpt-6-luna | 92 | 55 | 0.2505 | 0.2748 | 0.1255 | -9.7% |
| só IA | gpt-6-astra | 92 | 55 | 25.0477 | 15.0506 | 0.1255 | 39.9% |
| todos | gpt-6-luna | 152 | 93 | 0.2497 | 0.2772 | 0.1251 | -11.0% |
| todos | gpt-6-astra | 152 | 93 | 24.9679 | 15.3337 | 0.1251 | 38.6% |

No recorte `só regra` a produção não gasta LLM (a regra decide): o custo de `todos` é hipotético — vale o recorte `só IA`, que é o que hoje vai ao LLM.

### Decididos sozinho que discordam de produção — um a um (0; só IDs e números)

Por categoria: nenhum.

## Conjunto `teste` — 586 e-mails reais anonimizados, 179 remetentes (grupos)

Classe em produção: `principal` 223, `notificacoes` 64, `promocoes` 74, `redes_sociais` 6, `spam` 72, `golpe` 147. Quem decidiu em produção: `ai_api` 7, `ai_claude` 151, `ai_codex` 84, `crm` 9, `rule` 335. Corpo truncado na extração: 64/586. Máscara de última milha na carga (nome em maiúsculas após saudação → `[NOME]`): 0 registro(s), 0 troca(s). Registros inválidos na carga (→ falha operacional): 0. `redes_sociais`: 6 caso(s), fora das tabelas principais e do critério (seção própria).

### Roteamento por recorte — baseline × tudo no LLM × Jev, nos mesmos e-mails

**Gabarito = decisão de produção: tudo é concordância com produção, não acerto.** `cobertura` = fração que a variante decide sozinha (o resto escala ao LLM). `concordância entre decididos` = dos decididos sozinho, quantos batem com produção. `decidido E concorda / n` = automação útil. **GOLPE NA CAIXA** = golpe de produção decidido sozinho como `principal`/`notificacoes` (denominador: golpes do recorte). **CLIENTE PERDIDO** = `principal` de produção decidido sozinho como `spam`/`golpe` (denominador: principais do recorte). `ponta a ponta` conta o escalado como concordante (o LLM É o gabarito). Recortes: `só regra` = produção decidiu por regra; `só IA` = produção mandou a um LLM (o resíduo ambíguo: o caso de uso real do roteador); `todos` inclui também os decididos por `crm`. Variantes do Jev leem a MESMA resposta: `forçado` = sempre a classe mais provável; `só confiança` = limiar por classe, sem Nouls nem regra do corpo curto; `roteador` = a política de `perguntas.py`.

| recorte | variante | n | cobertura (decide sozinho) | concordância entre decididos | decidido E concorda / n | escalados | GOLPE NA CAIXA (golpe → principal/notificações, sozinho) | CLIENTE PERDIDO (principal → spam/golpe, sozinho) | concordância ponta a ponta (escalado = 1) |
|---|---|---|---|---|---|---|---|---|---|
| todos | baseline (regras de código) | 580 | 0.672 | 0.579 | 0.390 | 190 | 13/147 | 15/223 | 0.717 |
| todos | tudo no LLM (hoje) | 580 | 0.000 | — | 0.000 | 580 | 0/147 | 0/223 | 1.000 |
| todos | Jev forçado (sem limiar) | 580 | 0.995 | 0.669 | 0.666 | 3 | 21/147 | 39/223 | 0.671 |
| todos | Jev só confiança | 580 | 0.352 | 0.961 | 0.338 | 376 | 0/147 | 2/223 | 0.986 |
| todos | Jev roteador (política) | 580 | 0.303 | 0.977 | 0.297 | 404 | 0/147 | 2/223 | 0.993 |
| só regra | baseline (regras de código) | 329 | 0.669 | 0.682 | 0.456 | 109 | 1/75 | 2/147 | 0.787 |
| só regra | tudo no LLM (hoje) | 329 | 0.000 | — | 0.000 | 329 | 0/75 | 0/147 | 1.000 |
| só regra | Jev forçado (sem limiar) | 329 | 0.994 | 0.645 | 0.641 | 2 | 9/75 | 30/147 | 0.647 |
| só regra | Jev só confiança | 329 | 0.249 | 0.963 | 0.240 | 247 | 0/75 | 1/147 | 0.991 |
| só regra | Jev roteador (política) | 329 | 0.210 | 0.986 | 0.207 | 260 | 0/75 | 1/147 | 0.997 |
| só IA | baseline (regras de código) | 242 | 0.665 | 0.435 | 0.289 | 81 | 12/72 | 10/68 | 0.624 |
| só IA | tudo no LLM (hoje) | 242 | 0.000 | — | 0.000 | 242 | 0/72 | 0/68 | 1.000 |
| só IA | Jev forçado (sem limiar) | 242 | 0.996 | 0.693 | 0.690 | 1 | 12/72 | 9/68 | 0.694 |
| só IA | Jev só confiança | 242 | 0.483 | 0.957 | 0.463 | 125 | 0/72 | 1/68 | 0.979 |
| só IA | Jev roteador (política) | 242 | 0.430 | 0.971 | 0.417 | 138 | 0/72 | 1/68 | 0.988 |

### IC 95% da política — bootstrap agrupado por remetente (`grupo`), 2000 reamostragens

| recorte | grupos | cobertura | concordância entre decididos | golpe na caixa / golpes | cliente perdido / principais | ponta a ponta |
|---|---|---|---|---|---|---|
| todos | 178 | 0.303 [0.234; 0.384] | 0.977 [0.952; 0.995] | 0.000 [0.000; 0.000] | 0.009 [0.000; 0.023] | 0.993 [0.985; 0.999] |
| só regra | 57 | 0.210 [0.117; 0.315] | 0.986 [0.942; 1.000] | 0.000 [0.000; 0.000] | 0.007 [0.000; 0.022] | 0.997 [0.990; 1.000] |
| só IA | 123 | 0.430 [0.326; 0.549] | 0.971 [0.932; 1.000] | 0.000 [0.000; 0.000] | 0.015 [0.000; 0.056] | 0.988 [0.971; 1.000] |

### Política por state único — campanhas repetidas contadas uma vez

O mesmo texto (state idêntico depois da máscara) aparece em vários e-mails, inclusive entre ajuste e teste. `por e-mail` = as tabelas acima (cada registro conta 1). `state único` = cada state distinto conta 1 (fica o primeiro registro). `sem states do ajuste` = state único, tirando os states que também aparecem no ajuste (no `ajuste`, tira os repetidos dentro dele mesmo). Mesmas respostas do Jev, nenhuma chamada nova.

| recorte | denominador | n | cobertura | concordância entre decididos | golpe na caixa | cliente perdido |
|---|---|---|---|---|---|---|
| todos | por e-mail | 580 | 0.303 | 172/176 (0.977) | 0/147 | 2/223 |
| todos | state único | 520 | 0.290 | 148/151 (0.980) | 0/137 | 2/216 |
| todos | sem states do ajuste | 517 | 0.292 | 148/151 (0.980) | 0/134 | 2/216 |
| só regra | por e-mail | 329 | 0.210 | 68/69 (0.986) | 0/75 | 1/147 |
| só regra | state único | 288 | 0.170 | 48/49 (0.980) | 0/72 | 1/141 |
| só regra | sem states do ajuste | 285 | 0.172 | 48/49 (0.980) | 0/69 | 1/141 |
| só IA | por e-mail | 242 | 0.430 | 101/104 (0.971) | 0/72 | 1/68 |
| só IA | state único | 228 | 0.434 | 97/99 (0.980) | 0/65 | 1/67 |
| só IA | sem states do ajuste | 228 | 0.434 | 97/99 (0.980) | 0/65 | 1/67 |

**Critério congelado conferido no teste, recorte `só IA`** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 golpe na caixa (sozinho) | 0/72 (0.000) | ≤ 0.01 | ✓ |
| 2 cliente perdido (sozinho) | 1/68 (0.015) | ≤ 0.01 | ✗ |
| 3 concordância entre decididos | 101/104 (0.971) | ≥ 0.95 | ✓ |
| 4 cobertura | 104/242 (0.430) | ≥ 0.4 | ✓ |
| 5 o baseline de código não chega lá | baseline: golpe na caixa 12/72, cliente perdido 10/68, concordância 0.435, cobertura 0.665 | baseline falha em 1, 2 ou 3, ou cobre menos que o Jev | ✓ |
| informativo: cobertura ≥ 0.5 (sugestão do briefing) | 0.430 | ≥ 0.5 | ✗ (não decide) |

**Veredito calculado: NÃO PASSOU** (os 5 itens numerados).

### Curva cobertura × concordância × erro caro por limiar (mesmas respostas, zero chamada nova)

O MESMO limiar de confiança em todas as classes. `com a política` mantém os conflitos de Noul e a regra do corpo curto; `só confiança` desliga os dois. A linha de `perguntas.py` (limiar por classe) está na tabela principal.

**Recorte `só IA` — com a política**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.831 | 0.721 | 6/72 | 7/68 | 201 |
| 0.500 | 0.636 | 0.805 | 2/72 | 2/68 | 154 |
| 0.600 | 0.545 | 0.886 | 2/72 | 1/68 | 132 |
| 0.700 | 0.438 | 0.972 | 0/72 | 1/68 | 106 |
| 0.800 | 0.376 | 0.989 | 0/72 | 1/68 | 91 |
| 0.900 | 0.285 | 1.000 | 0/72 | 0/68 | 69 |
| 0.950 | 0.190 | 1.000 | 0/72 | 0/68 | 46 |
| 0.990 | 0.050 | 1.000 | 0/72 | 0/68 | 12 |

**Recorte `só IA` — só confiança**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.934 | 0.686 | 12/72 | 8/68 | 226 |
| 0.500 | 0.678 | 0.780 | 3/72 | 2/68 | 164 |
| 0.600 | 0.566 | 0.861 | 2/72 | 1/68 | 137 |
| 0.700 | 0.450 | 0.954 | 0/72 | 1/68 | 109 |
| 0.800 | 0.384 | 0.978 | 0/72 | 1/68 | 93 |
| 0.900 | 0.293 | 0.986 | 0/72 | 0/68 | 71 |
| 0.950 | 0.190 | 1.000 | 0/72 | 0/68 | 46 |
| 0.990 | 0.050 | 1.000 | 0/72 | 0/68 | 12 |

**Recorte `todos` — com a política**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.847 | 0.690 | 15/147 | 24/223 | 491 |
| 0.500 | 0.574 | 0.715 | 5/147 | 14/223 | 333 |
| 0.600 | 0.445 | 0.826 | 3/147 | 7/223 | 258 |
| 0.700 | 0.319 | 0.941 | 0/147 | 2/223 | 185 |
| 0.800 | 0.224 | 0.985 | 0/147 | 2/223 | 130 |
| 0.900 | 0.157 | 1.000 | 0/147 | 0/223 | 91 |
| 0.950 | 0.107 | 1.000 | 0/147 | 0/223 | 62 |
| 0.990 | 0.034 | 1.000 | 0/147 | 0/223 | 20 |

**Recorte `todos` — só confiança**

| limiar (todas as classes) | cobertura | concordância entre decididos | golpe na caixa | cliente perdido | n decididos |
|---|---|---|---|---|---|
| 0.000 | 0.938 | 0.654 | 21/147 | 38/223 | 544 |
| 0.500 | 0.609 | 0.700 | 6/147 | 16/223 | 353 |
| 0.600 | 0.469 | 0.805 | 3/147 | 9/223 | 272 |
| 0.700 | 0.329 | 0.921 | 0/147 | 2/223 | 191 |
| 0.800 | 0.229 | 0.977 | 0/147 | 2/223 | 133 |
| 0.900 | 0.162 | 0.989 | 0/147 | 0/223 | 94 |
| 0.950 | 0.107 | 1.000 | 0/147 | 0/223 | 62 |
| 0.990 | 0.034 | 1.000 | 0/147 | 0/223 | 20 |

### Por classe (política) — o que o Jev decide sozinho em cada classe

**Recorte `só IA`**

| classe | n em produção | decididos sozinho | … que concordam | concordância forçada (sem limiar) | Jev decidiu esta classe | … e produção concorda (precisão) |
|---|---|---|---|---|---|---|
| principal | 68 | 27 | 24 | 0.750 | 24 | 1.000 |
| notificacoes | 25 | 7 | 7 | 0.720 | 9 | 0.778 |
| promocoes | 42 | 28 | 28 | 0.810 | 28 | 1.000 |
| spam | 35 | 3 | 3 | 0.143 | 3 | 1.000 |
| golpe | 72 | 39 | 39 | 0.819 | 40 | 0.975 |

**Recorte `todos`**

| classe | n em produção | decididos sozinho | … que concordam | concordância forçada (sem limiar) | Jev decidiu esta classe | … e produção concorda (precisão) |
|---|---|---|---|---|---|---|
| principal | 223 | 57 | 53 | 0.695 | 53 | 1.000 |
| notificacoes | 64 | 16 | 16 | 0.703 | 18 | 0.889 |
| promocoes | 74 | 53 | 53 | 0.878 | 53 | 1.000 |
| spam | 72 | 3 | 3 | 0.069 | 3 | 1.000 |
| golpe | 147 | 47 | 47 | 0.789 | 49 | 0.959 |

### Matrizes de confusão (linhas = produção, colunas = Jev)

**Recorte `só IA` — decididos sozinho pela política** (104)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 24 | 2 | 0 | 0 | 0 | 1 |
| notificacoes | 0 | 7 | 0 | 0 | 0 | 0 |
| promocoes | 0 | 0 | 28 | 0 | 0 | 0 |
| spam | 0 | 0 | 0 | 0 | 3 | 0 |
| golpe | 0 | 0 | 0 | 0 | 0 | 39 |

**Recorte `só IA` — leitura forçada, todos os e-mails** (242)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe | sem resposta |
|---|---|---|---|---|---|---|---|
| principal | 51 | 8 | 0 | 0 | 1 | 8 | 0 |
| notificacoes | 0 | 18 | 0 | 0 | 0 | 6 | 1 |
| promocoes | 1 | 0 | 34 | 0 | 6 | 1 | 0 |
| spam | 0 | 2 | 28 | 0 | 5 | 0 | 0 |
| golpe | 6 | 6 | 1 | 0 | 0 | 59 | 0 |

**Recorte `todos` — decididos sozinho pela política** (176)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe |
|---|---|---|---|---|---|---|
| principal | 53 | 2 | 0 | 0 | 0 | 2 |
| notificacoes | 0 | 16 | 0 | 0 | 0 | 0 |
| promocoes | 0 | 0 | 53 | 0 | 0 | 0 |
| spam | 0 | 0 | 0 | 0 | 3 | 0 |
| golpe | 0 | 0 | 0 | 0 | 0 | 47 |

**Recorte `todos` — leitura forçada, todos os e-mails** (580)

| produção ↓ / Jev → | principal | notificacoes | promocoes | redes_sociais | spam | golpe | sem resposta |
|---|---|---|---|---|---|---|---|
| principal | 155 | 28 | 1 | 0 | 6 | 33 | 0 |
| notificacoes | 4 | 45 | 0 | 0 | 0 | 12 | 3 |
| promocoes | 1 | 0 | 65 | 0 | 7 | 1 | 0 |
| spam | 0 | 2 | 65 | 0 | 5 | 0 | 0 |
| golpe | 8 | 13 | 1 | 0 | 9 | 116 | 0 |

### Nouls por classe de produção — média (≥ 0.8 / ≤ 0.2), 577 e-mails com resposta

| noul | principal (n=223) | notificacoes (n=61) | promocoes (n=74) | spam (n=72) | golpe (n=147) |
|---|---|---|---|---|---|
| asks_money_or_credentials | 0.47 (73/91) | 0.18 (1/45) | 0.20 (2/58) | 0.27 (1/6) | 0.42 (36/53) |
| impersonates_known_sender | 0.33 (1/40) | 0.34 (0/9) | 0.31 (0/25) | 0.19 (2/65) | 0.58 (37/7) |
| pushes_to_act_on_pretext | 0.25 (1/106) | 0.19 (0/44) | 0.24 (1/45) | 0.12 (0/67) | 0.43 (20/29) |
| property_admin_mail | 0.64 (132/55) | 0.20 (9/45) | 0.05 (0/68) | 0.01 (0/72) | 0.06 (0/135) |
| human_wrote_to_this_recipient | 0.29 (44/150) | 0.08 (0/59) | 0.03 (0/73) | 0.03 (0/72) | 0.13 (0/130) |
| transactional_notice | 0.64 (122/44) | 0.84 (52/4) | 0.07 (0/67) | 0.09 (0/70) | 0.49 (38/50) |
| unsolicited_bulk_offer | 0.06 (1/214) | 0.05 (0/60) | 0.86 (59/2) | 0.94 (69/1) | 0.21 (16/112) |

**O que cada trava fez** (e-mails com confiança ≥ limiar da classe que a política mandou escalar mesmo assim): `erros barrados` = a classe do Jev discordava de produção; `acertos barrados` = concordava (cobertura perdida). `corpo truncado (código)` é a regra posta depois da rodada 1 (`P.CLASSES_CARAS`).

| trava | erros barrados | … dos quais erro caro | acertos barrados |
|---|---|---|---|
| `notificacoes` × `asks_money_or_credentials` | 2 | 0 | 0 |
| `promocoes` × `asks_money_or_credentials` | 0 | 0 | 1 |
| `promocoes` × `impersonates_known_sender` | 1 | 0 | 0 |
| corpo curto (código) | 1 | 0 | 1 |
| truncado (código) | 0 | 0 | 22 |

### Por que escalou (política, todos os recortes)

| motivo | e-mails |
|---|---|
| confiança abaixo do limiar (`golpe` < 0.8) | 113 |
| confiança abaixo do limiar (`principal` < 0.7) | 92 |
| confiança abaixo do limiar (`promocoes` < 0.7) | 77 |
| confiança abaixo do limiar (`notificacoes` < 0.7) | 67 |
| confiança abaixo do limiar (`spam` < 0.9) | 24 |
| corpo truncado na extração (`principal` é classe cara) | 22 |
| corpo vazio (sem chamada) | 3 |
| corpo curto para decidir classe de caixa de entrada | 2 |
| conflito de Noul com `promocoes` | 2 |
| conflito de Noul com `notificacoes` | 2 |

**Regra do corpo truncado** (código, posta depois da rodada 1): 63 e-mail(s) com resposta do Jev e corpo truncado; 22 barrado(s) por ela (confiança ≥ limiar, classe cara, sem corpo curto antes): 22 concordavam com produção, 0 discordavam, dos quais 0 erro(s) caro(s).

### `redes_sociais` à parte (6 caso(s); nenhum no ajuste: fora do critério)

| id | decidido_por | Jev leu | confiança | ação | concorda |
|---|---|---|---|---|---|
| EM-0317 | rule | redes_sociais | 0.910 | decide | ✓ |
| EM-0444 | rule | redes_sociais | 0.850 | decide | ✓ |
| EM-0607 | rule | redes_sociais | 0.850 | decide | ✓ |
| EM-0659 | rule | redes_sociais | 0.810 | decide | ✓ |
| EM-0686 | rule | golpe | 0.630 | escala | ✗ |
| EM-0696 | rule | redes_sociais | 0.920 | decide | ✓ |

### Custo e latência — Jev MEDIDO; LLM ESTIMADO (premissas no cabeçalho)

| e-mails | requisições | novas (não cache) | sem chamada (longo/vazio) | falhas operacionais (→ escala) | perguntas | p50_ms | p95_ms | tokens_por_e-mail | US$_total | US$_por_1000_e-mails | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 586 | 583 | 0 | 3 | 0 | 4664 | 274 | 323 | 3045 | 0.074552 | 0.1272 | jev-1.13.0 |

| recorte | LLM (premissa) | n | escalados | US$/1000: tudo no LLM | US$/1000: roteado (Jev + LLM nos escalados) | … só a parte Jev (medida) | economia |
|---|---|---|---|---|---|---|---|
| só IA | gpt-6-luna | 242 | 138 | 0.2568 | 0.2778 | 0.1286 | -8.2% |
| só IA | gpt-6-astra | 242 | 138 | 25.6812 | 15.0427 | 0.1286 | 41.4% |
| todos | gpt-6-luna | 580 | 404 | 0.2556 | 0.3069 | 0.1273 | -20.1% |
| todos | gpt-6-astra | 580 | 404 | 25.5637 | 18.0885 | 0.1273 | 29.2% |

No recorte `só regra` a produção não gasta LLM (a regra decide): o custo de `todos` é hipotético — vale o recorte `só IA`, que é o que hoje vai ao LLM.

### Decididos sozinho que discordam de produção — um a um (4; só IDs e números)

Por categoria: `principal → golpe` 2; `principal → notificacoes` 2.

| id | decidido_por | produção | Jev | confiança | caro | asks_money_or_credentials | impersonates_known_sender | pushes_to_act_on_pretext | property_admin_mail | human_wrote_to_this_recipient | transactional_notice | unsolicited_bulk_offer | dkim_aligned | list_unsubscribe | corpo (caracteres) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EM-0207 | ai_claude | principal | golpe | 0.82 | CLIENTE PERDIDO | 0.63 | 0.46 | 0.57 | 0.02 | 0.04 | 0.88 | 0.26 | True | False | 3231 |
| EM-0624 | ai_claude | principal | notificacoes | 0.72 |  | 0.12 | 0.34 | 0.15 | 0.24 | 0.14 | 0.93 | 0.05 | True | False | 717 |
| EM-0701 | ai_codex | principal | notificacoes | 0.76 |  | 0.51 | 0.62 | 0.17 | 0.02 | 0.06 | 0.95 | 0.04 | True | True | 475 |
| EM-0728 | rule | principal | golpe | 0.89 | CLIENTE PERDIDO | 0.69 | 0.87 | 0.53 | 0.01 | 0.02 | 0.75 | 0.05 | True | True | 104 |
