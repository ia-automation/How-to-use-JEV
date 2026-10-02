# Rascunho — proxima-pergunta (encanamento)

## Conjunto `rascunho` — 5 conversas (arquivo versão 2026-10-01, autor fable); 0 difíceis, 2 em que `no_question_needed` NÃO é aceitável, 0 acima do teto

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Escolha — baselines de código × variantes com Jev, nos mesmos casos

`acerto` = escolha ∈ `aceitaveis`. **PROIBIDA escolhida** = erro caro: perguntou o que o cliente já disse, o que o CRM já tem ou o que não faz sentido (∈ `proibidas`). **NQN indevido** = respondeu `no_question_needed` onde ele não é aceitável (deixou de perguntar o essencial); denominador = casos em que NQN não é aceitável. `fora do conjunto` = pergunta nem aceitável nem proibida (fora de hora). `perguntou algo` = escolha ≠ NQN. Variante principal (a que o critério julga): **Jev: Nouls + código nas essenciais, Choice `next` no resto**.

| variante | n | acerto (∈ aceitáveis) | PROIBIDA escolhida | NQN indevido | fora do conjunto | acerto onde NQN não é aceitável | perguntou algo |
|---|---|---|---|---|---|---|---|
| primeira lacuna (só CRM) | 5 | 0.000 | 4/5 | 0/2 | 1/5 | 0/2 | 5/5 |
| lacuna + palavras-chave | 5 | 0.800 | 0/5 | 1/2 | 0/5 | 1/2 | 2/5 |
| sempre no_question_needed | 5 | 0.600 | 0/5 | 2/2 | 0/5 | 0/2 | 0/5 |
| Jev: Choice única (catálogo inteiro) | 5 | 1.000 | 0/5 | 0/2 | 0/5 | 2/2 | 2/5 |
| Jev: Nouls + Choice única mascarada | 5 | 1.000 | 0/5 | 0/2 | 0/5 | 2/2 | 2/5 |
| Jev: Nouls → candidatas → Choice `next` | 5 | 1.000 | 0/5 | 0/2 | 0/5 | 2/2 | 2/5 |
| Jev: Nouls + política de código | 5 | 1.000 | 0/5 | 0/2 | 0/5 | 2/2 | 3/5 |
| Jev: Nouls + código nas essenciais, Choice `next` no resto | 5 | 1.000 | 0/5 | 0/2 | 0/5 | 2/2 | 3/5 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 pergunta proibida escolhida | 0/5 | ≤ 1 | ✓ |
| 2 acerto (∈ aceitáveis) | 1.000 (melhor baseline de código: lacuna + palavras-chave, 0.800) | ≥ 0.950 | ✓ |
| 3 `no_question_needed` indevido | 0/2 | ≤ 2 | ✓ |
| 4 contra a Choice única | acerto 1.000 × 1.000; proibidas 0 × 0 | acerto ≥ e proibidas ≤ | ✓ |
| secundário: proibidas bloqueadas pelo código | 17/17 (1.000) | ≥ 0.9 | ✓ |
| secundário: aceitável bloqueada indevidamente | 0/15 (0.000) | ≤ 0.05 | ✓ |

### Portão — o que o código bloqueou × `proibidas` do gabarito, por item

Bloqueada = campo do CRM não retirado (regra exata) · `answered` ≥ limiar · sem sentido (`financiamento` em aluguel, `pet` de investidor). `Noul cru` compara só o `answered` com o gabarito (proibida ⇒ alto; aceitável ⇒ baixo): em `financiamento` e `pet` parte das proibidas é "sem sentido", onde o Noul cru é baixo de propósito — quem bloqueia ali é a regra de sentido. Item fora dos dois conjuntos não entra.

| item | proibidas bloqueadas | aceitáveis bloqueadas (indevido) | Noul cru ≥ limiar × proibida | menor Noul entre proibidas | maior Noul entre aceitáveis | brier |
|---|---|---|---|---|---|---|
| finalidade | 5/5 | 0/0 | 1.000 | 0.96 | — | 0.001 |
| orcamento | 3/3 | 0/2 | 1.000 | 0.95 | 0.03 | 0.001 |
| bairro | 4/4 | 0/1 | 1.000 | 0.96 | 0.02 | 0.001 |
| quartos | 3/3 | 0/2 | 1.000 | 0.69 | 0.03 | 0.021 |
| vagas | 0/0 | 0/2 | 1.000 | — | 0.03 | 0.001 |
| prazo | 0/0 | 0/2 | 1.000 | — | 0.03 | 0.001 |
| pet | 0/0 | 0/2 | 1.000 | — | 0.02 | 0.000 |
| financiamento | 2/2 | 0/3 | 0.600 | 0.02 | 0.04 | 0.381 |
| visita | 0/0 | 0/1 | 1.000 | — | 0.03 | 0.001 |

Total: proibidas bloqueadas 17/17 · aceitáveis bloqueadas indevidamente 0/15

| motivo do bloqueio | n | em proibidas | em aceitáveis | fora dos dois |
|---|---|---|---|---|
| respondida | 11 | 11 | 0 | 0 |
| sem sentido (aluguel) | 2 | 2 | 0 | 0 |
| CRM | 4 | 4 | 0 | 0 |

`withdrawn.<campo>` (campo do CRM retirado sem valor novo; gabarito = o campo voltou a ser aceitável): acerto a 0.5 = 1.000 (n = 4; 0 retirados; maior valor entre os não retirados 0.02; menor entre os retirados nan)

### Por família difícil (pela `nota` do rotulador) — acertos

| família | n | primeira lacuna (só CRM) | lacuna + palavras-chave | Choice única (catálogo inteiro) | Nouls + Choice única mascarada | Nouls → candidatas → Choice `next` | Nouls + política de código | Nouls + código nas essenciais, Choice `next` no resto | proibidas (principal) | NQN indevido (principal) |
|---|---|---|---|---|---|---|---|---|---|---|
| fácil / outros | 5 | 0 | 4 | 5 | 5 | 5 | 5 | 5 | 0 | 0 |

### Cobertura × erro por confiança (abaixo do limiar = sem sugestão; o agente decide sozinho)

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.300 | 0.800 | 0.000 | 0 | 0 | 4 |
| 0.500 | 0.600 | 0.000 | 0 | 0 | 3 |
| 0.700 | 0.600 | 0.000 | 0 | 0 | 3 |
| 0.900 | 0.600 | 0.000 | 0 | 0 | 3 |

**Jev: Nouls → candidatas → Choice `next`** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.300 | 0.600 | 0.000 | 0 | 0 | 3 |
| 0.500 | 0.400 | 0.000 | 0 | 0 | 2 |
| 0.700 | 0.400 | 0.000 | 0 | 0 | 2 |
| 0.900 | 0.200 | 0.000 | 0 | 0 | 1 |

**Jev: Nouls + Choice única mascarada** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.300 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.500 | 0.800 | 0.000 | 0 | 0 | 4 |
| 0.700 | 0.400 | 0.000 | 0 | 0 | 2 |
| 0.900 | 0.200 | 0.000 | 0 | 0 | 1 |

**Jev: Choice única (catálogo inteiro)** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.300 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.500 | 0.800 | 0.000 | 0 | 0 | 4 |
| 0.700 | 0.400 | 0.000 | 0 | 0 | 2 |
| 0.900 | 0.200 | 0.000 | 0 | 0 | 1 |

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — pelo Noul mais fraco (menor distância ao limiar ×2 entre os Nouls do portão)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.300 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.500 | 0.800 | 0.000 | 0 | 0 | 4 |
| 0.700 | 0.800 | 0.000 | 0 | 0 | 4 |
| 0.900 | 0.800 | 0.000 | 0 | 0 | 4 |

### Custo e latência (medidos na chamada real; do cache também)

| conversas | requisições | novas (não cache) | com 2ª requisição | p50_ms por conversa (1ª+2ª) | p95_ms por conversa | p50_ms por requisição | p95_ms por requisição | tokens 1ª (média) | tokens 2ª (média) | tokens por conversa | US$_por_1000_conversas | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 10 | 10 | 5 | 734 | 847 | 378 | 533 | 2805 | 747 | 3552 | 0.1492 | jev-1.13.0 |

**Em produção, por variante** — a 1ª requisição medida carrega a Choice única de comparação (~26% do texto das perguntas, por caracteres, com CRM vazio); quem não a usa tem essa fatia descontada (estimativa). A 2ª requisição só entra onde a variante a faz. Latência = soma das requisições que a variante faz, medidas com 8 conversas em paralelo.

| variante | requisições | tokens por conversa (estimado) | US$_por_1000_conversas (estimado) | p50_ms por conversa | p95_ms por conversa |
|---|---|---|---|---|---|
| Jev: Choice única (catálogo inteiro) | 5 | 720 | 0.0302 | 455 | 533 |
| Jev: Nouls + Choice única mascarada | 5 | 2805 | 0.1178 | 455 | 533 |
| Jev: Nouls → candidatas → Choice `next` | 10 | 2832 | 0.1190 | 734 | 847 |
| Jev: Nouls + política de código | 5 | 2085 | 0.0876 | 455 | 533 |
| Jev: Nouls + código nas essenciais, Choice `next` no resto | 8 | 2558 | 0.1074 | 731 | 847 |

### Caso a caso

`bloqueadas`: C = CRM, R = `answered` ≥ limiar, S = sem sentido. `cand` = candidatas enviadas à Choice `next`. Escolhas: `lac` primeira lacuna · `pal` palavras-chave · `única` (confiança) · `masc` · `next` (confiança) · `cód` · `híb`. Marca: ✓ aceitável · ✗P proibida · ✗N NQN indevido · ✗F fora do conjunto. `answered` = Nouls crus; `ret` = `withdrawn`; `sinais` = rental / investor_not_living / specific_property / positive_reaction.

| id | fam | aceitáveis | proibidas | bloqueadas | cand | lac | pal | única | masc | next | cód | híb | answered | ret | sinais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PP-R001 | fácil / outros | vag pra pet fnc NQN | fin orc bai qua | fin:R orc:R bai:R qua:R | vag pra pet fnc NQN | fin ✗P | NQN ✓ | NQN ✓ (0.35) | NQN ✓ | NQN ✓ (0.27) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.98 bai 0.98 qua 0.69 vag 0.02 pra 0.02 pet 0.02 fnc 0.03 vis 0.03 |  | 0.02 / 0.02 / 0.03 / 0.02 |
| PP-R002 | fácil / outros | orc bai qua | fin fnc | fin:R fnc:S | orc bai qua NQN | fin ✗P | orc ✓ | orc ✓ (0.53) | orc ✓ | orc ✓ (0.25) | orc ✓ | orc ✓ | fin 0.98 orc 0.03 bai 0.02 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.03 |  | 0.96 / 0.03 / 0.03 / 0.02 |
| PP-R003 | fácil / outros | vis fnc | fin orc bai qua | fin:C orc:C bai:C qua:C | vag pra pet fnc vis NQN | vag ✗F | NQN ✗N | vis ✓ (1.00) | vis ✓ | vis ✓ (0.95) | vis ✓ | vis ✓ | fin 0.96 orc 0.95 bai 0.96 qua 0.92 vag 0.05 pra 0.02 pet 0.02 fnc 0.03 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.01 | 0.02 / 0.03 / 0.97 / 0.97 |
| PP-R004 | fácil / outros | vag pra pet fnc NQN | fin orc bai qua | fin:R orc:R bai:R qua:R | vag pra pet fnc NQN | fin ✗P | NQN ✓ | NQN ✓ (0.53) | NQN ✓ | NQN ✓ (0.39) | NQN ✓ | NQN ✓ | fin 0.98 orc 0.97 bai 0.96 qua 0.97 vag 0.03 pra 0.03 pet 0.02 fnc 0.04 vis 0.03 |  | 0.02 / 0.02 / 0.03 / 0.02 |
| PP-R005 | fácil / outros | NQN orc qua | fin bai fnc | fin:R bai:R fnc:S | orc qua NQN | fin ✗P | orc ✓ | NQN ✓ (0.84) | NQN ✓ | NQN ✓ (0.76) | orc ✓ | orc ✓ | fin 0.97 orc 0.02 bai 0.97 qua 0.03 vag 0.02 pra 0.02 pet 0.02 fnc 0.03 vis 0.03 |  | 0.89 / 0.06 / 0.03 / 0.02 |
