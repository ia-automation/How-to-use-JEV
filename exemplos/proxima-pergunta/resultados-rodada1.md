# Resultados — proxima-pergunta

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, limiares e variante principal: `perguntas.py`; validação, portão, candidatas e baselines: `proxima.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Teto da conversa: 12 turnos / 3000 caracteres (acima → sem sugestão, sem chamada). Limiares: {'respondida': 0.5, 'retirado': 0.5, 'aluguel': 0.7, 'investidor': 0.5, 'imovel_especifico': 0.8, 'reacao_positiva': 0.5}.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (40 conversas), variante principal `hibrida` com os limiares acima; **1_pergunta_proibida**: escolha ∈ `proibidas` (perguntou o que já sabia ou o que não faz sentido) ≤ 1/40; **2_acerto**: escolha ∈ `aceitaveis` ≥ melhor baseline de código + 0,15; **3_deixou_de_perguntar**: `no_question_needed` indevido ≤ 2/23; **4_contra_choice_unica**: acerto ≥ o da Choice única E proibidas ≤ as da Choice única; **secundario_nao_decide**: portão: proibidas bloqueadas ≥ 90%; aceitáveis bloqueadas indevidamente ≤ 5%; **se_falhar**: 1 falhando = o portão não serve como guarda contra repetição sem mudança; 2 = a regra de palavras-chave basta; 3 = a etapa cala onde devia qualificar; 4 = decompor não paga: a Choice única (uma requisição, sem portão) faz o mesmo

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T13:30:04-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 43b4435668feb2c5… · `proxima.py` sha256 a1a5d1199d270580… · `run.py` sha256 fa3709876f26bfc4… · `dados/teste.json` sha256 7e7c79562367f542…

## Lado a lado

### Escolha por variante e conjunto

| conjunto | variante | n | acerto (∈ aceitáveis) | PROIBIDA escolhida | NQN indevido | fora do conjunto | acerto onde NQN não é aceitável | perguntou algo |
|---|---|---|---|---|---|---|---|---|
| ajuste | primeira lacuna (só CRM) | 20 | 0.150 | 14/20 | 0/11 | 3/20 | 1/11 | 19/20 |
| ajuste | lacuna + palavras-chave | 20 | 0.700 | 2/20 | 4/11 | 0/20 | 6/11 | 10/20 |
| ajuste | sempre no_question_needed | 20 | 0.450 | 0/20 | 11/11 | 0/20 | 0/11 | 0/20 |
| ajuste | Jev: Choice única (catálogo inteiro) | 20 | 0.850 | 1/20 | 1/11 | 1/20 | 9/11 | 11/20 |
| ajuste | Jev: Nouls + Choice única mascarada | 20 | 0.900 | 0/20 | 2/11 | 0/20 | 9/11 | 9/20 |
| ajuste | Jev: Nouls → candidatas → Choice `next` | 20 | 0.900 | 0/20 | 2/11 | 0/20 | 9/11 | 10/20 |
| ajuste | Jev: Nouls + política de código | 20 | 1.000 | 0/20 | 0/11 | 0/20 | 11/11 | 13/20 |
| ajuste | Jev: Nouls + código nas essenciais, Choice `next` no resto | 20 | 1.000 | 0/20 | 0/11 | 0/20 | 11/11 | 14/20 |
| teste | primeira lacuna (só CRM) | 40 | 0.350 | 20/40 | 0/23 | 6/40 | 5/23 | 39/40 |
| teste | lacuna + palavras-chave | 40 | 0.750 | 5/40 | 5/23 | 0/40 | 15/23 | 25/40 |
| teste | sempre no_question_needed | 40 | 0.425 | 0/40 | 23/23 | 0/40 | 0/23 | 0/40 |
| teste | Jev: Choice única (catálogo inteiro) | 40 | 0.900 | 3/40 | 1/23 | 0/40 | 20/23 | 23/40 |
| teste | Jev: Nouls + Choice única mascarada | 40 | 0.925 | 0/40 | 3/23 | 0/40 | 20/23 | 20/40 |
| teste | Jev: Nouls → candidatas → Choice `next` | 40 | 0.925 | 1/40 | 2/23 | 0/40 | 20/23 | 23/40 |
| teste | Jev: Nouls + política de código | 40 | 0.975 | 1/40 | 0/23 | 0/40 | 22/23 | 27/40 |
| teste | Jev: Nouls + código nas essenciais, Choice `next` no resto | 40 | 0.975 | 1/40 | 0/23 | 0/40 | 22/23 | 29/40 |

### Portão e custo

| conjunto | n | difíceis | proibidas bloqueadas | aceitáveis bloqueadas | requisições (tudo) | tokens por conversa (tudo) | US$_por_1000 (tudo) | principal: requisições | principal: US$_por_1000 (estimado) | principal: p50_ms | principal: p95_ms | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | 20 | 13 | 88/88 | 0/29 | 39 | 3575 | 0.1501 | 27 | 0.1019 | 346 | 777 | jev-1.13.0 |
| teste | 40 | 29 | 160/163 | 1/55 | 78 | 3559 | 0.1495 | 52 | 0.0996 | 322 | 638 | jev-1.13.0 |

## Conjunto `ajuste` — 20 conversas (arquivo versão 2026-10-01, autor fable); 13 difíceis, 11 em que `no_question_needed` NÃO é aceitável, 0 acima do teto

### Escolha — baselines de código × variantes com Jev, nos mesmos casos

`acerto` = escolha ∈ `aceitaveis`. **PROIBIDA escolhida** = erro caro: perguntou o que o cliente já disse, o que o CRM já tem ou o que não faz sentido (∈ `proibidas`). **NQN indevido** = respondeu `no_question_needed` onde ele não é aceitável (deixou de perguntar o essencial); denominador = casos em que NQN não é aceitável. `fora do conjunto` = pergunta nem aceitável nem proibida (fora de hora). `perguntou algo` = escolha ≠ NQN. Variante principal (a que o critério julga): **Jev: Nouls + código nas essenciais, Choice `next` no resto**.

| variante | n | acerto (∈ aceitáveis) | PROIBIDA escolhida | NQN indevido | fora do conjunto | acerto onde NQN não é aceitável | perguntou algo |
|---|---|---|---|---|---|---|---|
| primeira lacuna (só CRM) | 20 | 0.150 | 14/20 | 0/11 | 3/20 | 1/11 | 19/20 |
| lacuna + palavras-chave | 20 | 0.700 | 2/20 | 4/11 | 0/20 | 6/11 | 10/20 |
| sempre no_question_needed | 20 | 0.450 | 0/20 | 11/11 | 0/20 | 0/11 | 0/20 |
| Jev: Choice única (catálogo inteiro) | 20 | 0.850 | 1/20 | 1/11 | 1/20 | 9/11 | 11/20 |
| Jev: Nouls + Choice única mascarada | 20 | 0.900 | 0/20 | 2/11 | 0/20 | 9/11 | 9/20 |
| Jev: Nouls → candidatas → Choice `next` | 20 | 0.900 | 0/20 | 2/11 | 0/20 | 9/11 | 10/20 |
| Jev: Nouls + política de código | 20 | 1.000 | 0/20 | 0/11 | 0/20 | 11/11 | 13/20 |
| Jev: Nouls + código nas essenciais, Choice `next` no resto | 20 | 1.000 | 0/20 | 0/11 | 0/20 | 11/11 | 14/20 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 pergunta proibida escolhida | 0/20 | ≤ 1 | ✓ |
| 2 acerto (∈ aceitáveis) | 1.000 (melhor baseline de código: lacuna + palavras-chave, 0.700) | ≥ 0.850 | ✓ |
| 3 `no_question_needed` indevido | 0/11 | ≤ 2 | ✓ |
| 4 contra a Choice única | acerto 1.000 × 0.850; proibidas 0 × 1 | acerto ≥ e proibidas ≤ | ✓ |
| secundário: proibidas bloqueadas pelo código | 88/88 (1.000) | ≥ 0.9 | ✓ |
| secundário: aceitável bloqueada indevidamente | 0/29 (0.000) | ≤ 0.05 | ✓ |

### Portão — o que o código bloqueou × `proibidas` do gabarito, por item

Bloqueada = campo do CRM não retirado (regra exata) · `answered` ≥ limiar · sem sentido (`financiamento` em aluguel, `pet` de investidor). `Noul cru` compara só o `answered` com o gabarito (proibida ⇒ alto; aceitável ⇒ baixo): em `financiamento` e `pet` parte das proibidas é "sem sentido", onde o Noul cru é baixo de propósito — quem bloqueia ali é a regra de sentido. Item fora dos dois conjuntos não entra.

| item | proibidas bloqueadas | aceitáveis bloqueadas (indevido) | Noul cru ≥ limiar × proibida | menor Noul entre proibidas | maior Noul entre aceitáveis | brier |
|---|---|---|---|---|---|---|
| finalidade | 19/19 | 0/1 | 1.000 | 0.70 | 0.07 | 0.007 |
| orcamento | 13/13 | 0/7 | 1.000 | 0.62 | 0.44 | 0.029 |
| bairro | 17/17 | 0/3 | 0.950 | 0.90 | 0.61 | 0.020 |
| quartos | 16/16 | 0/4 | 1.000 | 0.70 | 0.03 | 0.009 |
| vagas | 2/2 | 0/4 | 1.000 | 0.93 | 0.03 | 0.002 |
| prazo | 2/2 | 0/4 | 1.000 | 0.97 | 0.06 | 0.001 |
| pet | 4/4 | 0/3 | 0.857 | 0.02 | 0.03 | 0.139 |
| financiamento | 14/14 | 0/2 | 0.500 | 0.02 | 0.05 | 0.473 |
| visita | 1/1 | 0/1 | 1.000 | 0.98 | 0.03 | 0.001 |

Total: proibidas bloqueadas 88/88 · aceitáveis bloqueadas indevidamente 0/29

| motivo do bloqueio | n | em proibidas | em aceitáveis | fora dos dois |
|---|---|---|---|---|
| respondida | 52 | 52 | 0 | 0 |
| sem sentido (aluguel) | 8 | 8 | 0 | 0 |
| CRM | 27 | 27 | 0 | 0 |
| sem sentido (investidor) | 1 | 1 | 0 | 0 |

`withdrawn.<campo>` (campo do CRM retirado sem valor novo; gabarito = o campo voltou a ser aceitável): acerto a 0.5 = 1.000 (n = 28; 1 retirados; maior valor entre os não retirados 0.28; menor entre os retirados 0.96)

### Por família difícil (pela `nota` do rotulador) — acertos

| família | n | primeira lacuna (só CRM) | lacuna + palavras-chave | Choice única (catálogo inteiro) | Nouls + Choice única mascarada | Nouls → candidatas → Choice `next` | Nouls + política de código | Nouls + código nas essenciais, Choice `next` no resto | proibidas (principal) | NQN indevido (principal) |
|---|---|---|---|---|---|---|---|---|---|---|
| valor ambíguo | 4 | 1 | 2 | 2 | 2 | 2 | 4 | 4 | 0 | 0 |
| já respondida de modo informal | 3 | 0 | 2 | 3 | 3 | 3 | 3 | 3 | 0 | 0 |
| correção tardia | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| campo conhecido contradito | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 0 | 0 |
| nada faltando | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| cliente recusa repetição | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| sem sentido no contexto | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 0 |
| fácil / outros | 7 | 0 | 6 | 7 | 7 | 7 | 7 | 7 | 0 | 0 |

### Cobertura × erro por confiança (abaixo do limiar = sem sugestão; o agente decide sozinho)

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 20 |
| 0.300 | 0.900 | 0.000 | 0 | 0 | 18 |
| 0.500 | 0.800 | 0.000 | 0 | 0 | 16 |
| 0.700 | 0.800 | 0.000 | 0 | 0 | 16 |
| 0.900 | 0.750 | 0.000 | 0 | 0 | 15 |

**Jev: Nouls → candidatas → Choice `next`** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.100 | 0 | 2 | 20 |
| 0.300 | 0.850 | 0.118 | 0 | 2 | 17 |
| 0.500 | 0.650 | 0.077 | 0 | 1 | 13 |
| 0.700 | 0.600 | 0.000 | 0 | 0 | 12 |
| 0.900 | 0.400 | 0.000 | 0 | 0 | 8 |

**Jev: Nouls + Choice única mascarada** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.100 | 0 | 2 | 20 |
| 0.300 | 0.950 | 0.053 | 0 | 1 | 19 |
| 0.500 | 0.850 | 0.059 | 0 | 1 | 17 |
| 0.700 | 0.600 | 0.000 | 0 | 0 | 12 |
| 0.900 | 0.450 | 0.000 | 0 | 0 | 9 |

**Jev: Choice única (catálogo inteiro)** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.150 | 1 | 1 | 20 |
| 0.300 | 0.950 | 0.105 | 1 | 0 | 19 |
| 0.500 | 0.850 | 0.118 | 1 | 0 | 17 |
| 0.700 | 0.600 | 0.083 | 1 | 0 | 12 |
| 0.900 | 0.450 | 0.111 | 1 | 0 | 9 |

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — pelo Noul mais fraco (menor distância ao limiar ×2 entre os Nouls do portão)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 20 |
| 0.300 | 0.750 | 0.000 | 0 | 0 | 15 |
| 0.500 | 0.650 | 0.000 | 0 | 0 | 13 |
| 0.700 | 0.550 | 0.000 | 0 | 0 | 11 |
| 0.900 | 0.200 | 0.000 | 0 | 0 | 4 |

### Custo e latência (medidos na chamada real; do cache também)

| conversas | requisições | novas (não cache) | com 2ª requisição | p50_ms por conversa (1ª+2ª) | p95_ms por conversa | p50_ms por requisição | p95_ms por requisição | tokens 1ª (média) | tokens 2ª (média) | tokens por conversa | US$_por_1000_conversas | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 39 | 0 | 19 | 606 | 777 | 298 | 375 | 2904 | 706 | 3575 | 0.1501 | jev-1.13.0 |

**Em produção, por variante** — a 1ª requisição medida carrega a Choice única de comparação (~26% do texto das perguntas, por caracteres, com CRM vazio); quem não a usa tem essa fatia descontada (estimativa). A 2ª requisição só entra onde a variante a faz. Latência = soma das requisições que a variante faz, medidas com 8 conversas em paralelo.

| variante | requisições | tokens por conversa (estimado) | US$_por_1000_conversas (estimado) | p50_ms por conversa | p95_ms por conversa |
|---|---|---|---|---|---|
| Jev: Choice única (catálogo inteiro) | 20 | 745 | 0.0313 | 321 | 520 |
| Jev: Nouls + Choice única mascarada | 20 | 2904 | 0.1220 | 321 | 520 |
| Jev: Nouls → candidatas → Choice `next` | 39 | 2829 | 0.1188 | 606 | 777 |
| Jev: Nouls + política de código | 20 | 2158 | 0.0906 | 321 | 520 |
| Jev: Nouls + código nas essenciais, Choice `next` no resto | 27 | 2425 | 0.1019 | 346 | 777 |

### Caso a caso

`bloqueadas`: C = CRM, R = `answered` ≥ limiar, S = sem sentido. `cand` = candidatas enviadas à Choice `next`. Escolhas: `lac` primeira lacuna · `pal` palavras-chave · `única` (confiança) · `masc` · `next` (confiança) · `cód` · `híb`. Marca: ✓ aceitável · ✗P proibida · ✗N NQN indevido · ✗F fora do conjunto. `answered` = Nouls crus; `ret` = `withdrawn`; `sinais` = rental / investor_not_living / specific_property / positive_reaction.

| id | fam | aceitáveis | proibidas | bloqueadas | cand | lac | pal | única | masc | next | cód | híb | answered | ret | sinais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PP-A001 | valor ambíguo | fin | orc bai qua | orc:R bai:R qua:R | fin NQN | fin ✓ | fin ✓ | fin ✓ (0.88) | fin ✓ | fin ✓ (0.77) | fin ✓ | fin ✓ | fin 0.07 orc 0.83 bai 0.98 qua 0.95 vag 0.03 pra 0.03 pet 0.02 fnc 0.05 vis 0.04 |  | 0.49 / 0.14 / 0.03 / 0.02 |
| PP-A002 | valor ambíguo | orc | fin bai qua fnc | fin:R bai:R qua:R fnc:S | orc NQN | fin ✗P | NQN ✗N | pra ✗F (0.52) | NQN ✗N | NQN ✗N (0.64) | orc ✓ | orc ✓ | fin 0.98 orc 0.40 bai 0.95 qua 0.77 vag 0.02 pra 0.03 pet 0.02 fnc 0.03 vis 0.02 |  | 0.96 / 0.02 / 0.03 / 0.02 |
| PP-A003 | valor ambíguo | orc | fin bai qua fnc | fin:R bai:R qua:R fnc:R | orc NQN | fin ✗P | fin ✗P | NQN ✗N (0.19) | NQN ✗N | NQN ✗N (0.42) | orc ✓ | orc ✓ | fin 0.70 orc 0.44 bai 0.96 qua 0.70 vag 0.02 pra 0.02 pet 0.02 fnc 0.82 vis 0.02 |  | 0.02 / 0.05 / 0.03 / 0.02 |
| PP-A004 | já respondida de modo informal | qua | fin orc bai pet fnc | fin:R orc:R bai:R pet:R fnc:S | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.98) | qua ✓ | qua ✓ (0.91) | qua ✓ | qua ✓ | fin 0.98 orc 0.98 bai 0.98 qua 0.02 vag 0.03 pra 0.03 pet 0.98 fnc 0.04 vis 0.03 |  | 0.97 / 0.01 / 0.03 / 0.02 |
| PP-A005 | correção tardia | vag pra pet NQN | fin orc bai qua fnc | fin:R orc:R bai:R qua:R fnc:R | vag pra pet NQN | fin ✗P | NQN ✓ | NQN ✓ (0.61) | NQN ✓ | NQN ✓ (0.42) | NQN ✓ | NQN ✓ | fin 0.98 orc 0.81 bai 0.98 qua 0.98 vag 0.03 pra 0.03 pet 0.02 fnc 0.98 vis 0.03 |  | 0.01 / 0.02 / 0.05 / 0.03 |
| PP-A006 | campo conhecido contradito | bai | fin orc qua | fin:C orc:C qua:C | bai NQN | vag ✗F | NQN ✗N | bai ✓ (0.99) | bai ✓ | bai ✓ (0.99) | bai ✓ | bai ✓ | fin 0.97 orc 0.95 bai 0.61 qua 0.98 vag 0.03 pra 0.02 pet 0.03 fnc 0.03 vis 0.04 | fin 0.03 orc 0.28 bai 0.96 qua 0.03 | 0.02 / 0.02 / 0.21 / 0.02 |
| PP-A007 | nada faltando | NQN | fin orc bai qua vag pra pet fnc | fin:C orc:C bai:C qua:C vag:C pra:C pet:C fnc:C | NQN | NQN ✓ | NQN ✓ | NQN ✓ (0.99) | NQN ✓ | NQN ✓ (sem Choice) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.98 bai 0.98 qua 0.98 vag 0.97 pra 0.97 pet 0.97 fnc 0.97 vis 0.05 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 | 0.03 / 0.02 / 0.14 / 0.02 |
| PP-A008 | fácil / outros | NQN orc qua | fin bai fnc | fin:R bai:R fnc:S | orc qua NQN | fin ✗P | orc ✓ | NQN ✓ (0.76) | NQN ✓ | NQN ✓ (0.32) | orc ✓ | orc ✓ | fin 0.97 orc 0.03 bai 0.97 qua 0.03 vag 0.09 pra 0.02 pet 0.46 fnc 0.03 vis 0.08 |  | 0.88 / 0.30 / 0.06 / 0.02 |
| PP-A009 | cliente recusa repetição | NQN | fin orc bai qua fnc | fin:R orc:R bai:R qua:R fnc:R | vag pra pet NQN | fin ✗P | bai ✗P | NQN ✓ (0.97) | NQN ✓ | NQN ✓ (0.86) | NQN ✓ | NQN ✓ | fin 0.90 orc 0.98 bai 0.98 qua 0.98 vag 0.03 pra 0.03 pet 0.02 fnc 0.98 vis 0.04 |  | 0.03 / 0.06 / 0.05 / 0.02 |
| PP-A010 | fácil / outros | vis | fin orc bai qua pet fnc | fin:C orc:C bai:C qua:C pet:C fnc:S | vag pra vis NQN | vag ✗F | NQN ✗N | vis ✓ (1.00) | vis ✓ | vis ✓ (0.91) | vis ✓ | vis ✓ | fin 0.97 orc 0.96 bai 0.93 qua 0.92 vag 0.05 pra 0.02 pet 0.91 fnc 0.02 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.01 pet 0.02 | 0.98 / 0.02 / 0.95 / 0.98 |
| PP-A011 | fácil / outros | NQN | fin orc bai qua vis | fin:C orc:C bai:C qua:C vis:R | vag pra pet fnc NQN | vag ✗F | NQN ✓ | NQN ✓ (0.94) | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.97 bai 0.96 qua 0.96 vag 0.03 pra 0.30 pet 0.02 fnc 0.03 vis 0.98 | fin 0.02 orc 0.02 bai 0.03 qua 0.02 | 0.03 / 0.04 / 0.95 / 0.05 |
| PP-A012 | sem sentido no contexto | vag pra NQN | fin orc bai qua fnc pet | fin:R orc:R bai:R qua:R fnc:R pet:S | vag pra NQN | fin ✗P | NQN ✓ | qua ✗P (0.91) | NQN ✓ | pra ✓ (0.22) | NQN ✓ | pra ✓ | fin 0.92 orc 0.62 bai 0.97 qua 0.92 vag 0.03 pra 0.04 pet 0.02 fnc 0.98 vis 0.03 |  | 0.06 / 0.96 / 0.04 / 0.02 |
| PP-A013 | fácil / outros | qua | fin orc bai fnc | fin:C orc:C bai:R fnc:S | qua NQN | bai ✗P | qua ✓ | qua ✓ (0.62) | qua ✓ | qua ✓ (0.74) | qua ✓ | qua ✓ | fin 0.97 orc 0.96 bai 0.98 qua 0.03 vag 0.03 pra 0.04 pet 0.08 fnc 0.04 vis 0.15 | fin 0.02 orc 0.02 | 0.97 / 0.02 / 0.05 / 0.02 |
| PP-A014 | valor ambíguo | vag pra pet fnc NQN | fin orc bai qua | fin:C orc:R bai:R qua:R | vag pra pet fnc NQN | orc ✗P | NQN ✓ | NQN ✓ (0.32) | NQN ✓ | NQN ✓ (0.24) | NQN ✓ | NQN ✓ | fin 0.96 orc 0.93 bai 0.96 qua 0.94 vag 0.03 pra 0.03 pet 0.02 fnc 0.05 vis 0.04 | fin 0.02 | 0.06 / 0.04 / 0.08 / 0.03 |
| PP-A015 | já respondida de modo informal | orc | fin bai qua | fin:R bai:R qua:R | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.49) | orc ✓ | orc ✓ (0.96) | orc ✓ | orc ✓ | fin 0.92 orc 0.03 bai 0.98 qua 0.97 vag 0.03 pra 0.03 pet 0.02 fnc 0.03 vis 0.03 |  | 0.10 / 0.11 / 0.04 / 0.02 |
| PP-A016 | já respondida de modo informal | bai | fin orc qua fnc | fin:R orc:R qua:R fnc:R | bai NQN | fin ✗P | NQN ✗N | bai ✓ (1.00) | bai ✓ | bai ✓ (0.98) | bai ✓ | bai ✓ | fin 0.98 orc 0.97 bai 0.02 qua 0.98 vag 0.02 pra 0.03 pet 0.02 fnc 0.93 vis 0.03 |  | 0.01 / 0.02 / 0.03 / 0.02 |
| PP-A017 | campo conhecido contradito | vag pra pet fnc NQN | fin orc bai qua | fin:C orc:C bai:C qua:C | vag pra pet fnc NQN | vag ✓ | NQN ✓ | NQN ✓ (0.63) | NQN ✓ | NQN ✓ (0.37) | NQN ✓ | NQN ✓ | fin 0.96 orc 0.97 bai 0.94 qua 0.98 vag 0.03 pra 0.06 pet 0.03 fnc 0.03 vis 0.04 | fin 0.03 orc 0.03 bai 0.02 qua 0.02 | 0.02 / 0.03 / 0.66 / 0.04 |
| PP-A018 | fácil / outros | orc | fin bai qua vag fnc | fin:R bai:R qua:R vag:R fnc:S | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.90) | orc ✓ | orc ✓ (0.90) | orc ✓ | orc ✓ | fin 0.97 orc 0.03 bai 0.90 qua 0.95 vag 0.93 pra 0.03 pet 0.06 fnc 0.03 vis 0.04 |  | 0.96 / 0.04 / 0.04 / 0.03 |
| PP-A019 | fácil / outros | NQN orc | fin bai qua fnc | fin:R bai:R qua:R fnc:S | orc NQN | fin ✗P | orc ✓ | NQN ✓ (0.84) | NQN ✓ | NQN ✓ (0.74) | orc ✓ | orc ✓ | fin 0.96 orc 0.03 bai 0.97 qua 0.97 vag 0.02 pra 0.47 pet 0.02 fnc 0.02 vis 0.02 |  | 0.90 / 0.04 / 0.03 / 0.02 |
| PP-A020 | fácil / outros | orc bai qua | fin pra fnc | fin:R pra:R fnc:S | orc bai qua NQN | fin ✗P | orc ✓ | orc ✓ (0.50) | orc ✓ | orc ✓ (0.25) | orc ✓ | orc ✓ | fin 0.97 orc 0.03 bai 0.03 qua 0.03 vag 0.03 pra 0.97 pet 0.02 fnc 0.03 vis 0.03 |  | 0.97 / 0.02 / 0.04 / 0.02 |

## Conjunto `teste` — 40 conversas (arquivo versão 2026-10-01, autor fable); 29 difíceis, 23 em que `no_question_needed` NÃO é aceitável, 0 acima do teto

### Escolha — baselines de código × variantes com Jev, nos mesmos casos

`acerto` = escolha ∈ `aceitaveis`. **PROIBIDA escolhida** = erro caro: perguntou o que o cliente já disse, o que o CRM já tem ou o que não faz sentido (∈ `proibidas`). **NQN indevido** = respondeu `no_question_needed` onde ele não é aceitável (deixou de perguntar o essencial); denominador = casos em que NQN não é aceitável. `fora do conjunto` = pergunta nem aceitável nem proibida (fora de hora). `perguntou algo` = escolha ≠ NQN. Variante principal (a que o critério julga): **Jev: Nouls + código nas essenciais, Choice `next` no resto**.

| variante | n | acerto (∈ aceitáveis) | PROIBIDA escolhida | NQN indevido | fora do conjunto | acerto onde NQN não é aceitável | perguntou algo |
|---|---|---|---|---|---|---|---|
| primeira lacuna (só CRM) | 40 | 0.350 | 20/40 | 0/23 | 6/40 | 5/23 | 39/40 |
| lacuna + palavras-chave | 40 | 0.750 | 5/40 | 5/23 | 0/40 | 15/23 | 25/40 |
| sempre no_question_needed | 40 | 0.425 | 0/40 | 23/23 | 0/40 | 0/23 | 0/40 |
| Jev: Choice única (catálogo inteiro) | 40 | 0.900 | 3/40 | 1/23 | 0/40 | 20/23 | 23/40 |
| Jev: Nouls + Choice única mascarada | 40 | 0.925 | 0/40 | 3/23 | 0/40 | 20/23 | 20/40 |
| Jev: Nouls → candidatas → Choice `next` | 40 | 0.925 | 1/40 | 2/23 | 0/40 | 20/23 | 23/40 |
| Jev: Nouls + política de código | 40 | 0.975 | 1/40 | 0/23 | 0/40 | 22/23 | 27/40 |
| Jev: Nouls + código nas essenciais, Choice `next` no resto | 40 | 0.975 | 1/40 | 0/23 | 0/40 | 22/23 | 29/40 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 pergunta proibida escolhida | 1/40 | ≤ 1 | ✓ |
| 2 acerto (∈ aceitáveis) | 0.975 (melhor baseline de código: lacuna + palavras-chave, 0.750) | ≥ 0.900 | ✓ |
| 3 `no_question_needed` indevido | 0/23 | ≤ 2 | ✓ |
| 4 contra a Choice única | acerto 0.975 × 0.900; proibidas 1 × 3 | acerto ≥ e proibidas ≤ | ✓ |
| secundário: proibidas bloqueadas pelo código | 160/163 (0.982) | ≥ 0.9 | ✓ |
| secundário: aceitável bloqueada indevidamente | 1/55 (0.018) | ≤ 0.05 | ✓ |

### Portão — o que o código bloqueou × `proibidas` do gabarito, por item

Bloqueada = campo do CRM não retirado (regra exata) · `answered` ≥ limiar · sem sentido (`financiamento` em aluguel, `pet` de investidor). `Noul cru` compara só o `answered` com o gabarito (proibida ⇒ alto; aceitável ⇒ baixo): em `financiamento` e `pet` parte das proibidas é "sem sentido", onde o Noul cru é baixo de propósito — quem bloqueia ali é a regra de sentido. Item fora dos dois conjuntos não entra.

| item | proibidas bloqueadas | aceitáveis bloqueadas (indevido) | Noul cru ≥ limiar × proibida | menor Noul entre proibidas | maior Noul entre aceitáveis | brier |
|---|---|---|---|---|---|---|
| finalidade | 32/32 | 0/8 | 1.000 | 0.91 | 0.21 | 0.003 |
| orcamento | 24/25 | 1/13 | 0.921 | 0.43 | 0.89 | 0.064 |
| bairro | 32/33 | 0/5 | 0.974 | 0.31 | 0.03 | 0.018 |
| quartos | 30/30 | 0/8 | 0.974 | 0.52 | 0.79 | 0.035 |
| vagas | 5/5 | 0/5 | 1.000 | 0.95 | 0.03 | 0.001 |
| prazo | 4/4 | 0/6 | 1.000 | 0.95 | 0.28 | 0.011 |
| pet | 6/7 | 0/4 | 0.818 | 0.02 | 0.03 | 0.134 |
| financiamento | 23/23 | 0/2 | 0.400 | 0.02 | 0.06 | 0.555 |
| visita | 4/4 | 0/4 | 1.000 | 0.90 | 0.03 | 0.002 |

Total: proibidas bloqueadas 160/163 · aceitáveis bloqueadas indevidamente 1/55

| motivo do bloqueio | n | em proibidas | em aceitáveis | fora dos dois |
|---|---|---|---|---|
| respondida | 97 | 96 | 1 | 0 |
| sem sentido (aluguel) | 15 | 15 | 0 | 0 |
| CRM | 48 | 48 | 0 | 0 |
| sem sentido (investidor) | 1 | 1 | 0 | 0 |

`withdrawn.<campo>` (campo do CRM retirado sem valor novo; gabarito = o campo voltou a ser aceitável): acerto a 0.5 = 1.000 (n = 50; 2 retirados; maior valor entre os não retirados 0.20; menor entre os retirados 0.59)

### Por família difícil (pela `nota` do rotulador) — acertos

| família | n | primeira lacuna (só CRM) | lacuna + palavras-chave | Choice única (catálogo inteiro) | Nouls + Choice única mascarada | Nouls → candidatas → Choice `next` | Nouls + política de código | Nouls + código nas essenciais, Choice `next` no resto | proibidas (principal) | NQN indevido (principal) |
|---|---|---|---|---|---|---|---|---|---|---|
| valor ambíguo | 6 | 1 | 4 | 4 | 4 | 4 | 5 | 5 | 1 | 0 |
| já respondida de modo informal | 7 | 1 | 4 | 7 | 7 | 7 | 7 | 7 | 0 | 0 |
| correção tardia | 3 | 0 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 0 |
| campo conhecido contradito | 3 | 1 | 1 | 3 | 3 | 3 | 3 | 3 | 0 | 0 |
| nada faltando | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 0 | 0 |
| cliente recusa repetição | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| visita já pedida ou recusada | 4 | 2 | 4 | 4 | 4 | 4 | 4 | 4 | 0 | 0 |
| sem sentido no contexto | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| anúncio específico | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| reação negativa ao imóvel | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| fácil / outros | 11 | 6 | 9 | 9 | 10 | 10 | 11 | 11 | 0 | 0 |

### Cobertura × erro por confiança (abaixo do limiar = sem sugestão; o agente decide sozinho)

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.025 | 1 | 0 | 40 |
| 0.300 | 0.975 | 0.026 | 1 | 0 | 39 |
| 0.500 | 0.925 | 0.027 | 1 | 0 | 37 |
| 0.700 | 0.850 | 0.029 | 1 | 0 | 34 |
| 0.900 | 0.825 | 0.030 | 1 | 0 | 33 |

**Jev: Nouls → candidatas → Choice `next`** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.075 | 1 | 2 | 40 |
| 0.300 | 0.925 | 0.027 | 0 | 1 | 37 |
| 0.500 | 0.850 | 0.029 | 0 | 1 | 34 |
| 0.700 | 0.725 | 0.000 | 0 | 0 | 29 |
| 0.900 | 0.425 | 0.000 | 0 | 0 | 17 |

**Jev: Nouls + Choice única mascarada** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.075 | 0 | 3 | 40 |
| 0.300 | 0.975 | 0.077 | 0 | 3 | 39 |
| 0.500 | 0.875 | 0.086 | 0 | 3 | 35 |
| 0.700 | 0.725 | 0.000 | 0 | 0 | 29 |
| 0.900 | 0.500 | 0.000 | 0 | 0 | 20 |

**Jev: Choice única (catálogo inteiro)** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.100 | 3 | 1 | 40 |
| 0.300 | 0.975 | 0.103 | 3 | 1 | 39 |
| 0.500 | 0.875 | 0.114 | 3 | 1 | 35 |
| 0.700 | 0.725 | 0.000 | 0 | 0 | 29 |
| 0.900 | 0.500 | 0.000 | 0 | 0 | 20 |

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — pelo Noul mais fraco (menor distância ao limiar ×2 entre os Nouls do portão)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.025 | 1 | 0 | 40 |
| 0.300 | 0.850 | 0.000 | 0 | 0 | 34 |
| 0.500 | 0.675 | 0.000 | 0 | 0 | 27 |
| 0.700 | 0.500 | 0.000 | 0 | 0 | 20 |
| 0.900 | 0.150 | 0.000 | 0 | 0 | 6 |

### Custo e latência (medidos na chamada real; do cache também)

| conversas | requisições | novas (não cache) | com 2ª requisição | p50_ms por conversa (1ª+2ª) | p95_ms por conversa | p50_ms por requisição | p95_ms por requisição | tokens 1ª (média) | tokens 2ª (média) | tokens por conversa | US$_por_1000_conversas | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | 78 | 78 | 38 | 567 | 644 | 286 | 343 | 2880 | 715 | 3559 | 0.1495 | jev-1.13.0 |

**Em produção, por variante** — a 1ª requisição medida carrega a Choice única de comparação (~26% do texto das perguntas, por caracteres, com CRM vazio); quem não a usa tem essa fatia descontada (estimativa). A 2ª requisição só entra onde a variante a faz. Latência = soma das requisições que a variante faz, medidas com 8 conversas em paralelo.

| variante | requisições | tokens por conversa (estimado) | US$_por_1000_conversas (estimado) | p50_ms por conversa | p95_ms por conversa |
|---|---|---|---|---|---|
| Jev: Choice única (catálogo inteiro) | 40 | 739 | 0.0311 | 312 | 389 |
| Jev: Nouls + Choice única mascarada | 40 | 2880 | 0.1210 | 312 | 389 |
| Jev: Nouls → candidatas → Choice `next` | 78 | 2820 | 0.1184 | 567 | 644 |
| Jev: Nouls + política de código | 40 | 2141 | 0.0899 | 312 | 389 |
| Jev: Nouls + código nas essenciais, Choice `next` no resto | 52 | 2372 | 0.0996 | 322 | 638 |

### Caso a caso

`bloqueadas`: C = CRM, R = `answered` ≥ limiar, S = sem sentido. `cand` = candidatas enviadas à Choice `next`. Escolhas: `lac` primeira lacuna · `pal` palavras-chave · `única` (confiança) · `masc` · `next` (confiança) · `cód` · `híb`. Marca: ✓ aceitável · ✗P proibida · ✗N NQN indevido · ✗F fora do conjunto. `answered` = Nouls crus; `ret` = `withdrawn`; `sinais` = rental / investor_not_living / specific_property / positive_reaction.

| id | fam | aceitáveis | proibidas | bloqueadas | cand | lac | pal | única | masc | next | cód | híb | answered | ret | sinais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PP-T001 | fácil / outros | fin orc bai qua |  |  | fin orc bai qua NQN | fin ✓ | fin ✓ | fin ✓ (0.43) | fin ✓ | fin ✓ (0.83) | fin ✓ | fin ✓ | fin 0.14 orc 0.02 bai 0.02 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.03 |  | 0.02 / 0.13 / 0.04 / 0.02 |
| PP-T002 | valor ambíguo | fin | orc bai qua vag | orc:R bai:R qua:R vag:R | fin NQN | fin ✓ | fin ✓ | fin ✓ (0.95) | fin ✓ | fin ✓ (0.86) | fin ✓ | fin ✓ | fin 0.06 orc 0.82 bai 0.98 qua 0.98 vag 0.95 pra 0.03 pet 0.03 fnc 0.05 vis 0.03 |  | 0.49 / 0.08 / 0.03 / 0.02 |
| PP-T003 | valor ambíguo | orc | fin bai qua fnc | fin:R bai:R qua:R fnc:S | orc NQN | fin ✗P | NQN ✗N | qua ✗P (0.59) | NQN ✗N | NQN ✗N (0.54) | orc ✓ | orc ✓ | fin 0.98 orc 0.46 bai 0.98 qua 0.94 vag 0.03 pra 0.03 pet 0.02 fnc 0.05 vis 0.03 |  | 0.96 / 0.02 / 0.03 / 0.02 |
| PP-T004 | valor ambíguo | orc | fin bai qua fnc | fin:R bai:R qua:R fnc:R | orc NQN | fin ✗P | NQN ✗N | bai ✗P (0.67) | NQN ✗N | orc ✓ (0.43) | orc ✓ | orc ✓ | fin 0.97 orc 0.33 bai 0.97 qua 0.95 vag 0.02 pra 0.03 pet 0.02 fnc 0.86 vis 0.03 |  | 0.02 / 0.02 / 0.03 / 0.02 |
| PP-T005 | já respondida de modo informal | qua | fin orc bai pet fnc | fin:R orc:R bai:R pet:R fnc:S | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.97) | qua ✓ | qua ✓ (0.76) | qua ✓ | qua ✓ | fin 0.98 orc 0.95 bai 0.98 qua 0.03 vag 0.03 pra 0.03 pet 0.97 fnc 0.06 vis 0.03 |  | 0.97 / 0.02 / 0.03 / 0.02 |
| PP-T006 | correção tardia | qua | fin orc bai fnc | fin:R orc:R bai:R fnc:S | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.47) | qua ✓ | qua ✓ (0.71) | qua ✓ | qua ✓ | fin 0.97 orc 0.87 bai 0.97 qua 0.03 vag 0.02 pra 0.03 pet 0.02 fnc 0.07 vis 0.03 |  | 0.95 / 0.07 / 0.07 / 0.02 |
| PP-T007 | campo conhecido contradito | orc | fin bai qua | fin:C bai:C qua:C | orc NQN | vag ✗F | NQN ✗N | orc ✓ (0.91) | orc ✓ | orc ✓ (0.97) | orc ✓ | orc ✓ | fin 0.97 orc 0.89 bai 0.95 qua 0.98 vag 0.03 pra 0.02 pet 0.02 fnc 0.04 vis 0.17 | fin 0.03 orc 0.59 bai 0.03 qua 0.03 | 0.02 / 0.03 / 0.29 / 0.02 |
| PP-T008 | nada faltando | NQN | fin orc bai qua vag pra pet fnc | fin:C orc:C bai:C qua:C vag:C pra:C pet:C fnc:C | NQN | NQN ✓ | NQN ✓ | NQN ✓ (0.88) | NQN ✓ | NQN ✓ (sem Choice) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.97 bai 0.96 qua 0.97 vag 0.97 pra 0.97 pet 0.96 fnc 0.77 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 | 0.97 / 0.02 / 0.04 / 0.02 |
| PP-T009 | cliente recusa repetição | NQN | fin orc bai qua pet fnc | fin:R orc:R bai:R qua:R pet:R fnc:S | vag pra NQN | fin ✗P | bai ✗P | NQN ✓ (0.95) | NQN ✓ | NQN ✓ (0.65) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.95 bai 0.98 qua 0.97 vag 0.03 pra 0.03 pet 0.97 fnc 0.03 vis 0.04 |  | 0.96 / 0.03 / 0.05 / 0.02 |
| PP-T010 | fácil / outros | vis | fin orc bai qua fnc | fin:C orc:C bai:C qua:C fnc:C | vag pra pet vis NQN | vag ✗F | NQN ✗N | vis ✓ (1.00) | vis ✓ | vis ✓ (0.95) | vis ✓ | vis ✓ | fin 0.97 orc 0.95 bai 0.90 qua 0.94 vag 0.05 pra 0.02 pet 0.02 fnc 0.95 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 fnc 0.02 | 0.01 / 0.02 / 0.97 / 0.98 |
| PP-T011 | visita já pedida ou recusada | NQN | fin orc bai qua fnc vis | fin:C orc:C bai:C qua:C vis:R fnc:S | vag pra pet NQN | vag ✗F | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.96 bai 0.97 qua 0.97 vag 0.02 pra 0.32 pet 0.03 fnc 0.09 vis 0.98 | fin 0.02 orc 0.02 bai 0.03 qua 0.02 | 0.97 / 0.03 / 0.93 / 0.03 |
| PP-T012 | visita já pedida ou recusada | vag pra pet fnc NQN | fin orc bai qua vis | fin:C orc:C bai:C qua:C vis:R | vag pra pet fnc NQN | vag ✓ | NQN ✓ | NQN ✓ (0.92) | NQN ✓ | NQN ✓ (0.59) | NQN ✓ | NQN ✓ | fin 0.96 orc 0.97 bai 0.96 qua 0.97 vag 0.03 pra 0.28 pet 0.03 fnc 0.03 vis 0.96 | fin 0.02 orc 0.02 bai 0.05 qua 0.02 | 0.02 / 0.04 / 0.34 / 0.03 |
| PP-T013 | sem sentido no contexto | vag pra NQN | fin orc bai qua fnc pet | fin:R orc:R bai:R qua:R fnc:R pet:S | vag pra NQN | fin ✗P | NQN ✓ | NQN ✓ (0.44) | NQN ✓ | pra ✓ (0.19) | NQN ✓ | pra ✓ | fin 0.96 orc 0.97 bai 0.94 qua 0.96 vag 0.03 pra 0.02 pet 0.02 fnc 0.98 vis 0.03 |  | 0.02 / 0.97 / 0.03 / 0.02 |
| PP-T014 | fácil / outros | orc | fin qua bai | fin:C bai:R qua:C | orc NQN | orc ✓ | orc ✓ | orc ✓ (0.85) | orc ✓ | orc ✓ (0.89) | orc ✓ | orc ✓ | fin 0.97 orc 0.05 bai 0.95 qua 0.98 vag 0.03 pra 0.03 pet 0.03 fnc 0.03 vis 0.20 | fin 0.02 qua 0.03 | 0.02 / 0.04 / 0.08 / 0.03 |
| PP-T015 | fácil / outros | NQN fin orc qua | bai | bai:R | fin orc qua NQN | fin ✓ | fin ✓ | NQN ✓ (0.80) | NQN ✓ | NQN ✓ (0.65) | fin ✓ | fin ✓ | fin 0.05 orc 0.03 bai 0.92 qua 0.02 vag 0.03 pra 0.02 pet 0.02 fnc 0.03 vis 0.03 |  | 0.17 / 0.10 / 0.04 / 0.02 |
| PP-T016 | já respondida de modo informal | orc | fin bai qua pra fnc | fin:R bai:R qua:R pra:R fnc:S | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.97) | orc ✓ | orc ✓ (0.96) | orc ✓ | orc ✓ | fin 0.98 orc 0.03 bai 0.97 qua 0.80 vag 0.03 pra 0.95 pet 0.03 fnc 0.03 vis 0.03 |  | 0.91 / 0.03 / 0.03 / 0.02 |
| PP-T017 | já respondida de modo informal | qua | fin orc bai fnc | fin:R orc:R bai:R fnc:R | qua NQN | fin ✗P | fin ✗P | qua ✓ (0.95) | qua ✓ | qua ✓ (0.94) | qua ✓ | qua ✓ | fin 0.94 orc 0.85 bai 0.97 qua 0.03 vag 0.03 pra 0.03 pet 0.02 fnc 0.97 vis 0.03 |  | 0.03 / 0.02 / 0.04 / 0.02 |
| PP-T018 | fácil / outros | orc | fin bai qua vag fnc | fin:R bai:R qua:R vag:R fnc:S | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.89) | orc ✓ | orc ✓ (0.88) | orc ✓ | orc ✓ | fin 0.97 orc 0.03 bai 0.98 qua 0.66 vag 0.98 pra 0.02 pet 0.02 fnc 0.02 vis 0.06 |  | 0.92 / 0.03 / 0.06 / 0.04 |
| PP-T019 | anúncio específico | NQN vis fin orc | bai qua | qua:R | fin orc bai vis NQN | fin ✓ | fin ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ (1.00) | fin ✓ | fin ✓ | fin 0.04 orc 0.03 bai 0.31 qua 0.63 vag 0.02 pra 0.02 pet 0.03 fnc 0.02 vis 0.03 |  | 0.32 / 0.10 / 0.97 / 0.02 |
| PP-T020 | campo conhecido contradito | vag pra NQN | fin orc bai qua pet fnc | fin:C orc:C bai:C qua:C pet:C fnc:S | vag pra NQN | vag ✓ | NQN ✓ | NQN ✓ (0.97) | NQN ✓ | NQN ✓ (0.88) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.96 bai 0.94 qua 0.97 vag 0.03 pra 0.04 pet 0.97 fnc 0.04 vis 0.04 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 pet 0.20 | 0.97 / 0.02 / 0.26 / 0.02 |
| PP-T021 | valor ambíguo | vag pra pet fnc NQN | fin orc bai qua | fin:R orc:R bai:R qua:R | vag pra pet fnc NQN | fin ✗P | NQN ✓ | NQN ✓ (0.28) | NQN ✓ | NQN ✓ (0.46) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.93 bai 0.98 qua 0.98 vag 0.02 pra 0.02 pet 0.02 fnc 0.06 vis 0.03 |  | 0.05 / 0.02 / 0.03 / 0.02 |
| PP-T022 | valor ambíguo | bai | fin orc qua fnc | fin:R qua:R fnc:S | orc bai NQN | fin ✗P | bai ✓ | bai ✓ (0.42) | bai ✓ | orc ✗P (0.27) | orc ✗P | orc ✗P | fin 0.97 orc 0.43 bai 0.02 qua 0.98 vag 0.02 pra 0.03 pet 0.02 fnc 0.03 vis 0.03 |  | 0.94 / 0.07 / 0.06 / 0.02 |
| PP-T023 | fácil / outros | fin |  |  | fin orc bai qua NQN | fin ✓ | fin ✓ | fin ✓ (0.97) | fin ✓ | fin ✓ (0.98) | fin ✓ | fin ✓ | fin 0.02 orc 0.02 bai 0.02 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.02 |  | 0.06 / 0.06 / 0.03 / 0.02 |
| PP-T024 | visita já pedida ou recusada | NQN fin orc | vis bai qua | bai:R qua:R vis:R | fin orc NQN | fin ✓ | fin ✓ | NQN ✓ (0.97) | NQN ✓ | NQN ✓ (0.99) | fin ✓ | fin ✓ | fin 0.04 orc 0.03 bai 0.75 qua 0.52 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.96 |  | 0.21 / 0.09 / 0.92 / 0.04 |
| PP-T025 | nada faltando | NQN | fin orc bai qua vag pra pet fnc | fin:R orc:R bai:R qua:R vag:R pra:R pet:R fnc:S | NQN | fin ✗P | NQN ✓ | NQN ✓ (0.81) | NQN ✓ | NQN ✓ (sem Choice) | NQN ✓ | NQN ✓ | fin 0.98 orc 0.95 bai 0.97 qua 0.98 vag 0.98 pra 0.97 pet 0.98 fnc 0.05 vis 0.03 |  | 0.97 / 0.01 / 0.03 / 0.02 |
| PP-T026 | correção tardia | qua | fin orc bai | fin:R orc:R bai:R | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.52) | qua ✓ | qua ✓ (0.88) | qua ✓ | qua ✓ | fin 0.96 orc 0.86 bai 0.94 qua 0.02 vag 0.03 pra 0.03 pet 0.02 fnc 0.06 vis 0.03 |  | 0.04 / 0.04 / 0.08 / 0.05 |
| PP-T027 | campo conhecido contradito | qua | fin bai orc | fin:C orc:C bai:C | qua NQN | vag ✗F | NQN ✗N | qua ✓ (0.77) | qua ✓ | qua ✓ (0.88) | qua ✓ | qua ✓ | fin 0.94 orc 0.93 bai 0.98 qua 0.79 vag 0.03 pra 0.03 pet 0.03 fnc 0.03 vis 0.03 | fin 0.04 orc 0.03 bai 0.02 qua 0.73 | 0.08 / 0.02 / 0.15 / 0.02 |
| PP-T028 | já respondida de modo informal | NQN orc vis | fin bai qua pet fnc | fin:C orc:R bai:R qua:R fnc:S | vag pra pet vis NQN | orc ✓ | orc ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.88 bai 0.92 qua 0.92 vag 0.02 pra 0.02 pet 0.29 fnc 0.02 vis 0.03 | fin 0.02 | 0.97 / 0.03 / 0.91 / 0.03 |
| PP-T029 | fácil / outros | orc | fin bai qua fnc | fin:R bai:R qua:R fnc:S | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.99) | orc ✓ | orc ✓ (0.97) | orc ✓ | orc ✓ | fin 0.98 orc 0.03 bai 0.92 qua 0.97 vag 0.03 pra 0.03 pet 0.02 fnc 0.06 vis 0.03 |  | 0.93 / 0.02 / 0.03 / 0.02 |
| PP-T030 | fácil / outros | NQN vis | fin orc bai qua | fin:C orc:C bai:C qua:C | vag pra pet fnc vis NQN | vag ✗F | NQN ✓ | NQN ✓ (0.99) | NQN ✓ | NQN ✓ (0.99) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.96 bai 0.91 qua 0.96 vag 0.04 pra 0.03 pet 0.03 fnc 0.03 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 | 0.02 / 0.03 / 0.97 / 0.02 |
| PP-T031 | já respondida de modo informal | bai | fin orc qua pra fnc | fin:R orc:R qua:R pra:R fnc:R | bai NQN | fin ✗P | fin ✗P | bai ✓ (0.99) | bai ✓ | bai ✓ (0.97) | bai ✓ | bai ✓ | fin 0.91 orc 0.75 bai 0.03 qua 0.98 vag 0.03 pra 0.98 pet 0.02 fnc 0.98 vis 0.04 |  | 0.02 / 0.03 / 0.05 / 0.03 |
| PP-T032 | já respondida de modo informal | orc | fin bai qua fnc | fin:R bai:R qua:R fnc:S | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.93) | orc ✓ | orc ✓ (0.86) | orc ✓ | orc ✓ | fin 0.98 orc 0.02 bai 0.95 qua 0.67 vag 0.03 pra 0.03 pet 0.02 fnc 0.02 vis 0.03 |  | 0.96 / 0.02 / 0.04 / 0.02 |
| PP-T033 | fácil / outros | fin | orc bai qua | orc:R bai:R qua:R | fin NQN | fin ✓ | fin ✓ | NQN ✗N (0.51) | NQN ✗N | NQN ✗N (0.17) | fin ✓ | fin ✓ | fin 0.21 orc 0.91 bai 0.97 qua 0.98 vag 0.02 pra 0.03 pet 0.02 fnc 0.03 vis 0.03 |  | 0.02 / 0.11 / 0.03 / 0.03 |
| PP-T034 | fácil / outros | pra pet NQN | fin orc bai qua vag fnc | fin:R orc:R bai:R qua:R vag:R fnc:S | pra pet NQN | fin ✗P | bai ✗P | qua ✗P (0.65) | NQN ✓ | pra ✓ (0.49) | NQN ✓ | pra ✓ | fin 0.95 orc 0.93 bai 0.78 qua 0.93 vag 0.98 pra 0.14 pet 0.03 fnc 0.15 vis 0.09 |  | 0.90 / 0.07 / 0.11 / 0.03 |
| PP-T035 | correção tardia | bai | fin orc qua | fin:R orc:R qua:R | bai NQN | fin ✗P | bai ✓ | bai ✓ (0.72) | bai ✓ | bai ✓ (0.87) | bai ✓ | bai ✓ | fin 0.96 orc 0.95 bai 0.03 qua 0.97 vag 0.02 pra 0.02 pet 0.02 fnc 0.04 vis 0.03 |  | 0.09 / 0.02 / 0.05 / 0.07 |
| PP-T036 | fácil / outros | NQN fin |  |  | fin orc bai qua NQN | fin ✓ | fin ✓ | NQN ✓ (0.96) | NQN ✓ | NQN ✓ (0.93) | fin ✓ | fin ✓ | fin 0.04 orc 0.03 bai 0.02 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.03 |  | 0.15 / 0.08 / 0.04 / 0.02 |
| PP-T037 | já respondida de modo informal | bai | fin orc qua fnc | fin:R orc:R qua:R fnc:S | bai NQN | fin ✗P | qua ✗P | bai ✓ (1.00) | bai ✓ | bai ✓ (0.98) | bai ✓ | bai ✓ | fin 0.98 orc 0.96 bai 0.02 qua 0.88 vag 0.03 pra 0.03 pet 0.02 fnc 0.03 vis 0.03 |  | 0.97 / 0.01 / 0.04 / 0.02 |
| PP-T038 | reação negativa ao imóvel | vag pra pet NQN | fin orc bai qua fnc | fin:C orc:C bai:C qua:C fnc:C | vag pra pet vis NQN | vag ✓ | NQN ✓ | NQN ✓ (0.87) | NQN ✓ | NQN ✓ (0.63) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.94 bai 0.88 qua 0.95 vag 0.03 pra 0.02 pet 0.03 fnc 0.92 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 fnc 0.02 | 0.02 / 0.03 / 0.96 / 0.01 |
| PP-T039 | valor ambíguo | qua | fin orc bai fnc | fin:R orc:R bai:R fnc:R | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.68) | qua ✓ | qua ✓ (0.87) | qua ✓ | qua ✓ | fin 0.97 orc 0.88 bai 0.93 qua 0.03 vag 0.03 pra 0.04 pet 0.02 fnc 0.51 vis 0.04 |  | 0.94 / 0.05 / 0.08 / 0.04 |
| PP-T040 | visita já pedida ou recusada | NQN | fin orc bai qua vis | fin:C orc:C bai:C qua:C vis:R | vag pra pet fnc NQN | vag ✗F | NQN ✓ | NQN ✓ (0.89) | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ | fin 0.96 orc 0.94 bai 0.91 qua 0.93 vag 0.04 pra 0.02 pet 0.02 fnc 0.02 vis 0.90 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 | 0.02 / 0.03 / 0.96 / 0.93 |
