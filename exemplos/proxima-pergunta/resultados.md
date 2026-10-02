# Resultados — proxima-pergunta

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, limiares e variante principal: `perguntas.py`; valores em dinheiro: `valores.py`; validação, portão, regra do orçamento, candidatas e baselines: `proxima.py`; bateria do código (sem API): `testa_codigo.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Teto da conversa: 12 turnos / 3000 caracteres (acima → sem sugestão, sem chamada). Limiares: {'respondida': 0.5, 'retirado': 0.5, 'aluguel': 0.7, 'investidor': 0.5, 'imovel_especifico': 0.8, 'reacao_positiva': 0.5, 'declarado_nao': 0.2}; piso de preço de compra: 50000.

**Rodada 2 — pós-revisão do Codex (2026-10-01), NÃO cega**: o teste já tinha sido aberto e rodado na rodada 1 (`resultados-rodada1.md`, intocado). Perguntas `answered.budget`/`neighbourhood`/`bedrooms` reescritas, valores em dinheiro lidos pelo código (`valores.py`) e postos no state, regra do orçamento em código, validação da 2ª etapa e custo da principal medido em requisições próprias → o state e as perguntas mudaram: chamadas novas.

Critério de continuar/descartar (fixado antes da rodada 1 e mantido igual): **onde**: no teste (40 conversas), variante principal `hibrida` com os limiares acima; **1_pergunta_proibida**: escolha ∈ `proibidas` (perguntou o que já sabia ou o que não faz sentido) ≤ 1/40; **2_acerto**: escolha ∈ `aceitaveis` ≥ melhor baseline de código + 0,15; **3_deixou_de_perguntar**: `no_question_needed` indevido ≤ 2/23; **4_contra_choice_unica**: acerto ≥ o da Choice única E proibidas ≤ as da Choice única; **secundario_nao_decide**: portão: proibidas bloqueadas ≥ 90%; aceitáveis bloqueadas indevidamente ≤ 5%; **se_falhar**: 1 falhando = o portão não serve como guarda contra repetição sem mudança; 2 = a regra de palavras-chave basta; 3 = a etapa cala onde devia qualificar; 4 = decompor não paga: a Choice única (uma requisição, sem portão) faz o mesmo

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T14:07:00-03:00; rodada 2, NÃO cega): `perguntas.py` sha256 4dd88f1027453ca1… · `proxima.py` sha256 fdcd07c188186768… · `valores.py` sha256 8cae98534d74b5b7… · `run.py` sha256 9a44d433dadcc3b3… · `dados/teste.json` sha256 7e7c79562367f542…

## Lado a lado

### Escolha por variante e conjunto

| conjunto | variante | n | acerto (∈ aceitáveis) | PROIBIDA escolhida | NQN indevido | fora do conjunto | sem sugestão (revisão) | acerto onde NQN não é aceitável | perguntou algo |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | primeira lacuna (só CRM) | 20 | 0.150 | 14/20 | 0/11 | 3/20 | 0/20 | 1/11 | 19/20 |
| ajuste | lacuna + palavras-chave | 20 | 0.700 | 2/20 | 4/11 | 0/20 | 0/20 | 6/11 | 10/20 |
| ajuste | sempre no_question_needed | 20 | 0.450 | 0/20 | 11/11 | 0/20 | 0/20 | 0/11 | 0/20 |
| ajuste | Jev: Choice única (catálogo inteiro) | 20 | 0.850 | 1/20 | 1/11 | 1/20 | 0/20 | 9/11 | 11/20 |
| ajuste | Jev: Nouls + Choice única mascarada | 20 | 0.900 | 0/20 | 2/11 | 0/20 | 0/20 | 9/11 | 9/20 |
| ajuste | Jev: Nouls → candidatas → Choice `next` | 20 | 0.900 | 0/20 | 2/11 | 0/20 | 0/20 | 9/11 | 10/20 |
| ajuste | Jev: Nouls + política de código | 20 | 1.000 | 0/20 | 0/11 | 0/20 | 0/20 | 11/11 | 13/20 |
| ajuste | Jev: Nouls + código nas essenciais, Choice `next` no resto | 20 | 1.000 | 0/20 | 0/11 | 0/20 | 0/20 | 11/11 | 14/20 |
| teste | primeira lacuna (só CRM) | 40 | 0.350 | 20/40 | 0/23 | 6/40 | 0/40 | 5/23 | 39/40 |
| teste | lacuna + palavras-chave | 40 | 0.750 | 5/40 | 5/23 | 0/40 | 0/40 | 15/23 | 25/40 |
| teste | sempre no_question_needed | 40 | 0.425 | 0/40 | 23/23 | 0/40 | 0/40 | 0/23 | 0/40 |
| teste | Jev: Choice única (catálogo inteiro) | 40 | 0.875 | 4/40 | 1/23 | 0/40 | 0/40 | 19/23 | 23/40 |
| teste | Jev: Nouls + Choice única mascarada | 40 | 0.900 | 0/40 | 4/23 | 0/40 | 0/40 | 19/23 | 19/40 |
| teste | Jev: Nouls → candidatas → Choice `next` | 40 | 0.950 | 0/40 | 2/23 | 0/40 | 0/40 | 21/23 | 23/40 |
| teste | Jev: Nouls + política de código | 40 | 0.975 | 0/40 | 1/23 | 0/40 | 0/40 | 22/23 | 27/40 |
| teste | Jev: Nouls + código nas essenciais, Choice `next` no resto | 40 | 0.975 | 0/40 | 1/23 | 0/40 | 0/40 | 22/23 | 29/40 |

### Portão e custo (medido)

| conjunto | n | difíceis | proibidas bloqueadas | aceitáveis bloqueadas | em revisão (proibidas · aceitáveis) | falhas operacionais | principal: requisições | principal: tokens por conversa | principal: US$_por_1000 | principal: p50_ms | principal: p95_ms | tudo (com comparação): requisições | novas (não cache) | tudo: US$_por_1000 | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | 20 | 13 | 88/88 | 0/29 | 0 · 0 | 0 | 27 | 2675 | 0.1123 | 328 | 595 | 47 | 0 | 0.1630 | jev-1.13.0 |
| teste | 40 | 29 | 161/163 | 1/55 | 1 · 0 | 0 | 52 | 2616 | 0.1099 | 316 | 594 | 92 | 92 | 0.1617 | jev-1.13.0 |

## Conjunto `ajuste` — 20 conversas (arquivo versão 2026-10-01, autor fable); 13 difíceis, 11 em que `no_question_needed` NÃO é aceitável, 0 acima do teto, 0 falhas operacionais

### Escolha — baselines de código × variantes com Jev, nos mesmos casos

`acerto` = escolha ∈ `aceitaveis`. **PROIBIDA escolhida** = erro caro: perguntou o que o cliente já disse, o que o CRM já tem ou o que não faz sentido (∈ `proibidas`). **NQN indevido** = respondeu `no_question_needed` onde ele não é aceitável (deixou de perguntar o essencial); denominador = casos em que NQN não é aceitável. `fora do conjunto` = pergunta nem aceitável nem proibida (fora de hora). `sem sugestão (revisão)` = a etapa não devolveu pergunta: item essencial em revisão, falha operacional ou teto — NÃO conta como acerto. `perguntou algo` = escolha ≠ NQN. Variante principal (a que o critério julga): **Jev: Nouls + código nas essenciais, Choice `next` no resto**.

| variante | n | acerto (∈ aceitáveis) | PROIBIDA escolhida | NQN indevido | fora do conjunto | sem sugestão (revisão) | acerto onde NQN não é aceitável | perguntou algo |
|---|---|---|---|---|---|---|---|---|
| primeira lacuna (só CRM) | 20 | 0.150 | 14/20 | 0/11 | 3/20 | 0/20 | 1/11 | 19/20 |
| lacuna + palavras-chave | 20 | 0.700 | 2/20 | 4/11 | 0/20 | 0/20 | 6/11 | 10/20 |
| sempre no_question_needed | 20 | 0.450 | 0/20 | 11/11 | 0/20 | 0/20 | 0/11 | 0/20 |
| Jev: Choice única (catálogo inteiro) | 20 | 0.850 | 1/20 | 1/11 | 1/20 | 0/20 | 9/11 | 11/20 |
| Jev: Nouls + Choice única mascarada | 20 | 0.900 | 0/20 | 2/11 | 0/20 | 0/20 | 9/11 | 9/20 |
| Jev: Nouls → candidatas → Choice `next` | 20 | 0.900 | 0/20 | 2/11 | 0/20 | 0/20 | 9/11 | 10/20 |
| Jev: Nouls + política de código | 20 | 1.000 | 0/20 | 0/11 | 0/20 | 0/20 | 11/11 | 13/20 |
| Jev: Nouls + código nas essenciais, Choice `next` no resto | 20 | 1.000 | 0/20 | 0/11 | 0/20 | 0/20 | 11/11 | 14/20 |

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

Bloqueada = campo do CRM não retirado (regra exata) · `answered` ≥ limiar (preferência DECLARADA pelo cliente) · `orcamento` pela regra do LEIA-ME sobre o valor lido pelo código · bairro e quartos do anúncio específico (regra) · sem sentido (`financiamento` em aluguel, `pet` de investidor). Em revisão = o código não deixa perguntar nem dá por respondido (não conta como bloqueada). `Noul cru` compara só o `answered` com o gabarito (proibida ⇒ alto; aceitável ⇒ baixo): na rodada 2 ele deixou de ser o portão em `orcamento` (o Noul diz se o valor é do cliente; aluguel + "até 600" é declarado E aceitável), em `bairro`/`quartos` com anúncio citado, e em `financiamento`/`pet` sem sentido — ali quem bloqueia é a regra. Item fora dos dois conjuntos não entra.

| item | proibidas bloqueadas | aceitáveis bloqueadas (indevido) | em revisão (proibidas · aceitáveis) | Noul cru ≥ limiar × proibida | menor Noul entre proibidas | maior Noul entre aceitáveis | brier |
|---|---|---|---|---|---|---|---|
| finalidade | 19/19 | 0/1 | 0 · 0 | 1.000 | 0.72 | 0.06 | 0.006 |
| orcamento | 13/13 | 0/7 | 0 · 0 | 0.900 | 0.85 | 0.98 | 0.101 |
| bairro | 17/17 | 0/3 | 0 · 0 | 1.000 | 0.71 | 0.31 | 0.017 |
| quartos | 16/16 | 0/4 | 0 · 0 | 1.000 | 0.72 | 0.03 | 0.011 |
| vagas | 2/2 | 0/4 | 0 · 0 | 1.000 | 0.92 | 0.03 | 0.002 |
| prazo | 2/2 | 0/4 | 0 · 0 | 1.000 | 0.97 | 0.06 | 0.001 |
| pet | 4/4 | 0/3 | 0 · 0 | 0.857 | 0.03 | 0.02 | 0.136 |
| financiamento | 14/14 | 0/2 | 0 · 0 | 0.500 | 0.02 | 0.08 | 0.471 |
| visita | 1/1 | 0/1 | 0 · 0 | 1.000 | 0.98 | 0.03 | 0.001 |

Total: proibidas bloqueadas 88/88 · aceitáveis bloqueadas indevidamente 0/29 · em revisão: 0 proibidas, 0 aceitáveis

Cada bloqueio sai com `motivo` (`noul` | `regra`), a evidência e a margem (menor distância ao limiar, ×2, entre os Nouls que o sustentam: 0 = em cima do limiar):

| motivo | detalhe | n | em proibidas | em aceitáveis | fora dos dois | menor margem | margem < 0,3 |
|---|---|---|---|---|---|---|---|
| regra | orçamento declarado, lido pelo código | 7 | 7 | 0 | 0 | 0.34 | 0 |
| noul | declarado pelo cliente | 46 | 45 | 0 | 1 | 0.00 | 1 |
| regra | sem sentido (aluguel) | 8 | 8 | 0 | 0 | 0.34 | 0 |
| regra | CRM | 27 | 27 | 0 | 0 | 0.48 | 0 |
| regra | sem sentido (investidor) | 1 | 1 | 0 | 0 | 0.92 | 0 |

`withdrawn.<campo>` (campo do CRM retirado sem valor novo; gabarito = o campo voltou a ser aceitável): acerto a 0.5 = 1.000 (n = 28; 1 retirados; maior valor entre os não retirados 0.26; menor entre os retirados 0.95)

### Regra do orçamento em código (CRM sem o campo) × gabarito

`respondida` = valor declarado (Noul) e lido pela regra → bloqueia · `confirmar` = aluguel + centenas sem unidade → candidata · `aberta` = sem valor, prestação em compra ou valor que não é limite do cliente → candidata · `revisar` = a regra não decide → nem pergunta nem bloqueio.

| estado | n | orcamento proibida | orcamento aceitável | fora dos dois |
|---|---|---|---|---|
| respondida | 7 | 7 | 0 | 0 |
| confirmar | 1 | 0 | 1 | 0 |
| aberta | 6 | 0 | 6 | 0 |

Itens em revisão: nenhum

### Por família difícil (pela `nota` do rotulador) — acertos

| família | n | primeira lacuna (só CRM) | lacuna + palavras-chave | Choice única (catálogo inteiro) | Nouls + Choice única mascarada | Nouls → candidatas → Choice `next` | Nouls + política de código | Nouls + código nas essenciais, Choice `next` no resto | proibidas (principal) | NQN indevido (principal) | sem sugestão (principal) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| valor ambíguo | 4 | 1 | 2 | 2 | 2 | 2 | 4 | 4 | 0 | 0 | 0 |
| já respondida de modo informal | 3 | 0 | 2 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 |
| correção tardia | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| campo conhecido contradito | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |
| nada faltando | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| cliente recusa repetição | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| sem sentido no contexto | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| fácil / outros | 7 | 0 | 6 | 7 | 7 | 7 | 7 | 7 | 0 | 0 | 0 |

### Cobertura × erro por confiança (abaixo do limiar = sem sugestão; o agente decide sozinho)

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 20 |
| 0.300 | 0.950 | 0.000 | 0 | 0 | 19 |
| 0.500 | 0.800 | 0.000 | 0 | 0 | 16 |
| 0.700 | 0.800 | 0.000 | 0 | 0 | 16 |
| 0.900 | 0.800 | 0.000 | 0 | 0 | 16 |

**Jev: Nouls → candidatas → Choice `next`** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.100 | 0 | 2 | 20 |
| 0.300 | 0.900 | 0.111 | 0 | 2 | 18 |
| 0.500 | 0.750 | 0.133 | 0 | 2 | 15 |
| 0.700 | 0.600 | 0.000 | 0 | 0 | 12 |
| 0.900 | 0.450 | 0.000 | 0 | 0 | 9 |

**Jev: Nouls + Choice única mascarada** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.100 | 0 | 2 | 20 |
| 0.300 | 0.950 | 0.053 | 0 | 1 | 19 |
| 0.500 | 0.850 | 0.059 | 0 | 1 | 17 |
| 0.700 | 0.650 | 0.000 | 0 | 0 | 13 |
| 0.900 | 0.500 | 0.000 | 0 | 0 | 10 |

**Jev: Choice única (catálogo inteiro)** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.150 | 1 | 1 | 20 |
| 0.300 | 0.950 | 0.105 | 1 | 0 | 19 |
| 0.500 | 0.850 | 0.118 | 1 | 0 | 17 |
| 0.700 | 0.650 | 0.077 | 1 | 0 | 13 |
| 0.900 | 0.500 | 0.100 | 1 | 0 | 10 |

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — pelo Noul mais fraco (menor distância ao limiar ×2 entre os Nouls do portão)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 20 |
| 0.300 | 0.900 | 0.000 | 0 | 0 | 18 |
| 0.500 | 0.750 | 0.000 | 0 | 0 | 15 |
| 0.700 | 0.700 | 0.000 | 0 | 0 | 14 |
| 0.900 | 0.250 | 0.000 | 0 | 0 | 5 |

### Custo e latência — medidos por grupo de requisições (nada estimado)

| requisições medidas | requisições | novas (não cache) | tokens por conversa | US$_por_1000_conversas | p50_ms por conversa | p95_ms por conversa |
|---|---|---|---|---|---|---|
| `hibrida` em produção (`todas=False`): 1ª + 2ª quando precisa | 27 | 0 | 2675 | 0.1123 | 328 | 595 |
| `codigo` em produção: só a 1ª | 20 | 0 | 2398 | 0.1007 | 297 | 378 |
| comparação (só na medição): Choice única + `next` onde a principal não chama | 20 | 0 | 1205 | 0.0506 | 325 | 383 |
| tudo o que esta execução usou | 47 | 0 | 3880 | 0.1630 | 678 | 896 |

Conversas com 2ª requisição: 7/20 · tokens médios: 1ª 2398, 2ª 791, comparação 1205 · p50 / p95 por requisição: 295 / 367 ms · modelo: jev-1.13.0. A linha da principal é o que `proxima.julgar(todas=False)` envia: a Choice única de comparação não está nela. Latência = a da chamada original de cada requisição (o cache a guarda).

### Caso a caso

`bloqueadas`: C = CRM · N = Noul `answered` (declarado pelo cliente) · O = regra do orçamento sobre o valor lido pelo código · A = anúncio específico (regra) · S = sem sentido; o número é a margem do bloqueio. `rev` = em revisão. `orçamento` = estado da regra e leitura do código (CRM sem o campo). `cand` = candidatas. Escolhas: `lac` primeira lacuna · `pal` palavras-chave · `única` (confiança) · `masc` · `next` (confiança) · `cód` · `híb`. Marca: ✓ aceitável · ✗P proibida · ✗N NQN indevido · ✗F fora do conjunto · ✗∅ sem sugestão. `answered` = Nouls crus; `ret` = `withdrawn`; `sinais` = rental / investor_not_living / specific_property / positive_reaction.

| id | fam | aceitáveis | proibidas | bloqueadas | rev | orçamento | cand | lac | pal | única | masc | next | cód | híb | answered | ret | sinais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PP-A001 | valor ambíguo | fin | orc bai qua | orc:O0.34 bai:N0.96 qua:N0.92 |  | respondida (até 600 → R$ 600.000 preco) | fin NQN | fin ✓ | fin ✓ | fin ✓ (0.92) | fin ✓ | fin ✓ (0.88) | fin ✓ | fin ✓ | fin 0.06 orc 0.97 bai 0.98 qua 0.96 vag 0.03 pra 0.02 pet 0.02 fnc 0.08 vis 0.03 |  | 0.53 / 0.12 / 0.03 / 0.02 |
| PP-A002 | valor ambíguo | orc | fin bai qua fnc | fin:N0.96 bai:N0.94 qua:N0.88 fnc:S0.52 |  | confirmar (até 600) | orc NQN | fin ✗P | NQN ✗N | pra ✗F (0.60) | NQN ✗N | NQN ✗N (0.69) | orc ✓ | orc ✓ | fin 0.98 orc 0.98 bai 0.97 qua 0.94 vag 0.02 pra 0.02 pet 0.02 fnc 0.04 vis 0.03 |  | 0.96 / 0.02 / 0.03 / 0.02 |
| PP-A003 | valor ambíguo | orc | fin bai qua fnc | fin:N0.44 bai:N0.94 qua:N0.52 fnc:N0.62 |  | aberta (pagar uns 2500 por mês → R$ 2.500 prestacao) | orc NQN | fin ✗P | fin ✗P | NQN ✗N (0.27) | NQN ✗N | NQN ✗N (0.50) | orc ✓ | orc ✓ | fin 0.72 orc 0.98 bai 0.97 qua 0.76 vag 0.03 pra 0.03 pet 0.02 fnc 0.81 vis 0.03 |  | 0.03 / 0.05 / 0.03 / 0.02 |
| PP-A004 | já respondida de modo informal | qua | fin orc bai pet fnc | fin:N0.96 orc:O0.54 bai:N0.96 pet:N0.96 fnc:S0.54 |  | respondida (até 4 mil → R$ 4.000 aluguel) | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.98) | qua ✓ | qua ✓ (0.90) | qua ✓ | qua ✓ | fin 0.98 orc 0.98 bai 0.98 qua 0.03 vag 0.03 pra 0.03 pet 0.98 fnc 0.05 vis 0.03 |  | 0.97 / 0.02 / 0.03 / 0.02 |
| PP-A005 | correção tardia | vag pra pet NQN | fin orc bai qua fnc | fin:N0.96 orc:O0.94 bai:N0.96 qua:N0.96 fnc:N0.96 |  | respondida (até 900 → R$ 900.000 preco) | vag pra pet NQN | fin ✗P | NQN ✓ | NQN ✓ (0.68) | NQN ✓ | NQN ✓ (0.44) | NQN ✓ | NQN ✓ | fin 0.98 orc 0.97 bai 0.98 qua 0.98 vag 0.03 pra 0.03 pet 0.02 fnc 0.98 vis 0.03 |  | 0.02 / 0.02 / 0.06 / 0.03 |
| PP-A006 | campo conhecido contradito | bai | fin orc qua | fin:C0.94 orc:C0.48 qua:C0.96 |  | — | bai NQN | vag ✗F | NQN ✗N | bai ✓ (0.98) | bai ✓ | bai ✓ (0.99) | bai ✓ | bai ✓ | fin 0.97 orc 0.87 bai 0.31 qua 0.91 vag 0.03 pra 0.02 pet 0.02 fnc 0.03 vis 0.04 | fin 0.03 orc 0.26 bai 0.95 qua 0.02 | 0.02 / 0.02 / 0.18 / 0.02 |
| PP-A007 | nada faltando | NQN | fin orc bai qua vag pra pet fnc | fin:C0.96 orc:C0.96 bai:C0.96 qua:C0.96 vag:C0.96 pra:C0.96 pet:C0.96 fnc:C0.96 |  | — | NQN | NQN ✓ | NQN ✓ | NQN ✓ (0.99) | NQN ✓ | NQN ✓ (sem Choice) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.93 bai 0.93 qua 0.95 vag 0.97 pra 0.97 pet 0.97 fnc 0.96 vis 0.05 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 | 0.03 / 0.02 / 0.13 / 0.02 |
| PP-A008 | fácil / outros | NQN orc qua | fin bai fnc | fin:N0.94 bai:N0.88 fnc:S0.34 |  | aberta | orc qua NQN | fin ✗P | orc ✓ | NQN ✓ (0.73) | NQN ✓ | NQN ✓ (0.50) | orc ✓ | orc ✓ | fin 0.97 orc 0.03 bai 0.94 qua 0.03 vag 0.05 pra 0.03 pet 0.48 fnc 0.03 vis 0.07 |  | 0.87 / 0.43 / 0.05 / 0.02 |
| PP-A009 | cliente recusa repetição | NQN | fin orc bai qua fnc | fin:N0.82 orc:O0.96 bai:N0.96 qua:N0.96 fnc:N0.96 |  | respondida (até 1.2 mi → R$ 1.200.000 preco) | vag pra pet NQN | fin ✗P | bai ✗P | NQN ✓ (0.97) | NQN ✓ | NQN ✓ (0.94) | NQN ✓ | NQN ✓ | fin 0.91 orc 0.98 bai 0.98 qua 0.98 vag 0.03 pra 0.03 pet 0.03 fnc 0.98 vis 0.04 |  | 0.02 / 0.05 / 0.04 / 0.02 |
| PP-A010 | fácil / outros | vis | fin orc bai qua pet fnc | fin:C0.96 orc:C0.96 bai:C0.96 qua:C0.96 pet:C0.96 fnc:S0.56 |  | — | vag pra vis NQN | vag ✗F | NQN ✗N | vis ✓ (1.00) | vis ✓ | vis ✓ (0.92) | vis ✓ | vis ✓ | fin 0.97 orc 0.90 bai 0.73 qua 0.72 vag 0.04 pra 0.02 pet 0.90 fnc 0.02 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 pet 0.02 | 0.98 / 0.02 / 0.94 / 0.98 |
| PP-A011 | fácil / outros | NQN | fin orc bai qua vis | fin:C0.96 orc:C0.96 bai:C0.94 qua:C0.96 vis:N0.96 |  | — | vag pra pet fnc NQN | vag ✗F | NQN ✓ | NQN ✓ (0.95) | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.85 bai 0.71 qua 0.77 vag 0.03 pra 0.31 pet 0.02 fnc 0.03 vis 0.98 | fin 0.02 orc 0.02 bai 0.03 qua 0.02 | 0.03 / 0.04 / 0.95 / 0.05 |
| PP-A012 | sem sentido no contexto | vag pra NQN | fin orc bai qua fnc pet | fin:N0.88 orc:O0.90 bai:N0.96 qua:N0.86 pet:S0.92 fnc:N0.96 |  | respondida (até 450 → R$ 450.000 preco) | vag pra NQN | fin ✗P | NQN ✓ | qua ✗P (0.95) | NQN ✓ | pra ✓ (0.36) | NQN ✓ | pra ✓ | fin 0.94 orc 0.95 bai 0.98 qua 0.93 vag 0.03 pra 0.04 pet 0.03 fnc 0.98 vis 0.03 |  | 0.07 / 0.96 / 0.03 / 0.02 |
| PP-A013 | fácil / outros | qua | fin orc bai fnc | fin:C0.96 orc:C0.96 bai:N0.96 fnc:S0.52 |  | — | qua NQN | bai ✗P | qua ✓ | qua ✓ (0.56) | qua ✓ | qua ✓ (0.74) | qua ✓ | qua ✓ | fin 0.97 orc 0.87 bai 0.98 qua 0.03 vag 0.03 pra 0.04 pet 0.09 fnc 0.05 vis 0.16 | fin 0.02 orc 0.02 | 0.96 / 0.02 / 0.04 / 0.03 |
| PP-A014 | valor ambíguo | vag pra pet fnc NQN | fin orc bai qua | fin:C0.94 orc:O0.90 bai:N0.94 qua:N0.82 |  | respondida (até 600 → R$ 600.000 preco) | vag pra pet fnc NQN | orc ✗P | NQN ✓ | NQN ✓ (0.31) | NQN ✓ | NQN ✓ (0.27) | NQN ✓ | NQN ✓ | fin 0.96 orc 0.95 bai 0.97 qua 0.91 vag 0.03 pra 0.03 pet 0.02 fnc 0.08 vis 0.04 | fin 0.03 | 0.10 / 0.04 / 0.06 / 0.02 |
| PP-A015 | já respondida de modo informal | orc | fin bai qua | fin:N0.82 bai:N0.96 qua:N0.92 |  | aberta | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.52) | orc ✓ | orc ✓ (0.98) | orc ✓ | orc ✓ | fin 0.91 orc 0.03 bai 0.98 qua 0.96 vag 0.02 pra 0.03 pet 0.02 fnc 0.02 vis 0.03 |  | 0.10 / 0.09 / 0.04 / 0.02 |
| PP-A016 | já respondida de modo informal | bai | fin orc qua fnc | fin:N0.96 orc:O0.96 qua:N0.94 fnc:N0.84 |  | respondida (até 750 mil → R$ 750.000 preco) | bai NQN | fin ✗P | NQN ✗N | bai ✓ (1.00) | bai ✓ | bai ✓ (0.98) | bai ✓ | bai ✓ | fin 0.98 orc 0.98 bai 0.03 qua 0.97 vag 0.02 pra 0.03 pet 0.02 fnc 0.92 vis 0.03 |  | 0.01 / 0.02 / 0.03 / 0.02 |
| PP-A017 | campo conhecido contradito | vag pra pet fnc NQN | fin orc bai qua | fin:C0.94 orc:C0.96 bai:C0.96 qua:C0.96 |  | — | vag pra pet fnc NQN | vag ✓ | NQN ✓ | NQN ✓ (0.71) | NQN ✓ | NQN ✓ (0.34) | NQN ✓ | NQN ✓ | fin 0.96 orc 0.85 bai 0.75 qua 0.97 vag 0.03 pra 0.06 pet 0.02 fnc 0.03 vis 0.03 | fin 0.03 orc 0.02 bai 0.02 qua 0.02 | 0.02 / 0.03 / 0.60 / 0.03 |
| PP-A018 | fácil / outros | orc | fin bai qua vag fnc | fin:N0.96 bai:N0.84 qua:N0.92 vag:N0.84 fnc:S0.52 |  | aberta | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.94) | orc ✓ | orc ✓ (0.91) | orc ✓ | orc ✓ | fin 0.98 orc 0.03 bai 0.92 qua 0.96 vag 0.92 pra 0.03 pet 0.03 fnc 0.02 vis 0.04 |  | 0.96 / 0.04 / 0.03 / 0.03 |
| PP-A019 | fácil / outros | NQN orc | fin bai qua fnc | fin:N0.92 bai:N0.94 qua:N0.92 pra:N0.00 fnc:S0.38 |  | aberta | orc NQN | fin ✗P | orc ✓ | NQN ✓ (0.87) | NQN ✓ | NQN ✓ (0.83) | orc ✓ | orc ✓ | fin 0.96 orc 0.03 bai 0.97 qua 0.96 vag 0.02 pra 0.50 pet 0.02 fnc 0.02 vis 0.02 |  | 0.89 / 0.04 / 0.04 / 0.02 |
| PP-A020 | fácil / outros | orc bai qua | fin pra fnc | fin:N0.94 pra:N0.94 fnc:S0.52 |  | aberta | orc bai qua NQN | fin ✗P | orc ✓ | orc ✓ (0.42) | orc ✓ | bai ✓ (0.23) | orc ✓ | orc ✓ | fin 0.97 orc 0.03 bai 0.03 qua 0.03 vag 0.03 pra 0.97 pet 0.03 fnc 0.03 vis 0.03 |  | 0.96 / 0.02 / 0.03 / 0.02 |

## Conjunto `teste` — 40 conversas (arquivo versão 2026-10-01, autor fable); 29 difíceis, 23 em que `no_question_needed` NÃO é aceitável, 0 acima do teto, 0 falhas operacionais

### Escolha — baselines de código × variantes com Jev, nos mesmos casos

`acerto` = escolha ∈ `aceitaveis`. **PROIBIDA escolhida** = erro caro: perguntou o que o cliente já disse, o que o CRM já tem ou o que não faz sentido (∈ `proibidas`). **NQN indevido** = respondeu `no_question_needed` onde ele não é aceitável (deixou de perguntar o essencial); denominador = casos em que NQN não é aceitável. `fora do conjunto` = pergunta nem aceitável nem proibida (fora de hora). `sem sugestão (revisão)` = a etapa não devolveu pergunta: item essencial em revisão, falha operacional ou teto — NÃO conta como acerto. `perguntou algo` = escolha ≠ NQN. Variante principal (a que o critério julga): **Jev: Nouls + código nas essenciais, Choice `next` no resto**.

| variante | n | acerto (∈ aceitáveis) | PROIBIDA escolhida | NQN indevido | fora do conjunto | sem sugestão (revisão) | acerto onde NQN não é aceitável | perguntou algo |
|---|---|---|---|---|---|---|---|---|
| primeira lacuna (só CRM) | 40 | 0.350 | 20/40 | 0/23 | 6/40 | 0/40 | 5/23 | 39/40 |
| lacuna + palavras-chave | 40 | 0.750 | 5/40 | 5/23 | 0/40 | 0/40 | 15/23 | 25/40 |
| sempre no_question_needed | 40 | 0.425 | 0/40 | 23/23 | 0/40 | 0/40 | 0/23 | 0/40 |
| Jev: Choice única (catálogo inteiro) | 40 | 0.875 | 4/40 | 1/23 | 0/40 | 0/40 | 19/23 | 23/40 |
| Jev: Nouls + Choice única mascarada | 40 | 0.900 | 0/40 | 4/23 | 0/40 | 0/40 | 19/23 | 19/40 |
| Jev: Nouls → candidatas → Choice `next` | 40 | 0.950 | 0/40 | 2/23 | 0/40 | 0/40 | 21/23 | 23/40 |
| Jev: Nouls + política de código | 40 | 0.975 | 0/40 | 1/23 | 0/40 | 0/40 | 22/23 | 27/40 |
| Jev: Nouls + código nas essenciais, Choice `next` no resto | 40 | 0.975 | 0/40 | 1/23 | 0/40 | 0/40 | 22/23 | 29/40 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 pergunta proibida escolhida | 0/40 | ≤ 1 | ✓ |
| 2 acerto (∈ aceitáveis) | 0.975 (melhor baseline de código: lacuna + palavras-chave, 0.750) | ≥ 0.900 | ✓ |
| 3 `no_question_needed` indevido | 1/23 | ≤ 2 | ✓ |
| 4 contra a Choice única | acerto 0.975 × 0.875; proibidas 0 × 4 | acerto ≥ e proibidas ≤ | ✓ |
| secundário: proibidas bloqueadas pelo código | 161/163 (0.988) | ≥ 0.9 | ✓ |
| secundário: aceitável bloqueada indevidamente | 1/55 (0.018) | ≤ 0.05 | ✓ |

### Portão — o que o código bloqueou × `proibidas` do gabarito, por item

Bloqueada = campo do CRM não retirado (regra exata) · `answered` ≥ limiar (preferência DECLARADA pelo cliente) · `orcamento` pela regra do LEIA-ME sobre o valor lido pelo código · bairro e quartos do anúncio específico (regra) · sem sentido (`financiamento` em aluguel, `pet` de investidor). Em revisão = o código não deixa perguntar nem dá por respondido (não conta como bloqueada). `Noul cru` compara só o `answered` com o gabarito (proibida ⇒ alto; aceitável ⇒ baixo): na rodada 2 ele deixou de ser o portão em `orcamento` (o Noul diz se o valor é do cliente; aluguel + "até 600" é declarado E aceitável), em `bairro`/`quartos` com anúncio citado, e em `financiamento`/`pet` sem sentido — ali quem bloqueia é a regra. Item fora dos dois conjuntos não entra.

| item | proibidas bloqueadas | aceitáveis bloqueadas (indevido) | em revisão (proibidas · aceitáveis) | Noul cru ≥ limiar × proibida | menor Noul entre proibidas | maior Noul entre aceitáveis | brier |
|---|---|---|---|---|---|---|---|
| finalidade | 32/32 | 0/8 | 0 · 0 | 1.000 | 0.90 | 0.24 | 0.003 |
| orcamento | 24/25 | 1/13 | 1 · 0 | 0.895 | 0.29 | 0.98 | 0.086 |
| bairro | 33/33 | 0/5 | 0 · 0 | 0.921 | 0.04 | 0.03 | 0.080 |
| quartos | 30/30 | 0/8 | 0 · 0 | 0.895 | 0.02 | 0.56 | 0.088 |
| vagas | 5/5 | 0/5 | 0 · 0 | 1.000 | 0.94 | 0.03 | 0.001 |
| prazo | 4/4 | 0/6 | 0 · 0 | 1.000 | 0.96 | 0.34 | 0.015 |
| pet | 6/7 | 0/4 | 0 · 0 | 0.818 | 0.02 | 0.03 | 0.141 |
| financiamento | 23/23 | 0/2 | 0 · 0 | 0.360 | 0.02 | 0.05 | 0.558 |
| visita | 4/4 | 0/4 | 0 · 0 | 1.000 | 0.91 | 0.04 | 0.002 |

Total: proibidas bloqueadas 161/163 · aceitáveis bloqueadas indevidamente 1/55 · em revisão: 1 proibidas, 0 aceitáveis

Cada bloqueio sai com `motivo` (`noul` | `regra`), a evidência e a margem (menor distância ao limiar, ×2, entre os Nouls que o sustentam: 0 = em cima do limiar):

| motivo | detalhe | n | em proibidas | em aceitáveis | fora dos dois | menor margem | margem < 0,3 |
|---|---|---|---|---|---|---|---|
| regra | orçamento declarado, lido pelo código | 15 | 15 | 0 | 0 | 0.44 | 0 |
| noul | declarado pelo cliente | 75 | 75 | 0 | 0 | 0.32 | 0 |
| regra | sem sentido (aluguel) | 16 | 16 | 0 | 0 | 0.42 | 0 |
| regra | CRM | 49 | 48 | 1 | 0 | 0.16 | 1 |
| regra | sem sentido (investidor) | 1 | 1 | 0 | 0 | 0.94 | 0 |
| regra | anúncio específico | 6 | 6 | 0 | 0 | 0.24 | 4 |

`withdrawn.<campo>` (campo do CRM retirado sem valor novo; gabarito = o campo voltou a ser aceitável): acerto a 0.5 = 0.980 (n = 50; 2 retirados; maior valor entre os não retirados 0.24; menor entre os retirados 0.42)

### Regra do orçamento em código (CRM sem o campo) × gabarito

`respondida` = valor declarado (Noul) e lido pela regra → bloqueia · `confirmar` = aluguel + centenas sem unidade → candidata · `aberta` = sem valor, prestação em compra ou valor que não é limite do cliente → candidata · `revisar` = a regra não decide → nem pergunta nem bloqueio.

| estado | n | orcamento proibida | orcamento aceitável | fora dos dois |
|---|---|---|---|---|
| aberta | 13 | 0 | 11 | 2 |
| respondida | 15 | 15 | 0 | 0 |
| confirmar | 1 | 0 | 1 | 0 |
| revisar | 1 | 1 | 0 | 0 |

Itens em revisão: PP-T022 (`orcamento`: o código leu um valor do cliente e o Jev ficou em dúvida se é limite declarado; margem 0.42)

### Por família difícil (pela `nota` do rotulador) — acertos

| família | n | primeira lacuna (só CRM) | lacuna + palavras-chave | Choice única (catálogo inteiro) | Nouls + Choice única mascarada | Nouls → candidatas → Choice `next` | Nouls + política de código | Nouls + código nas essenciais, Choice `next` no resto | proibidas (principal) | NQN indevido (principal) | sem sugestão (principal) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| valor ambíguo | 6 | 1 | 4 | 3 | 4 | 5 | 6 | 6 | 0 | 0 | 0 |
| já respondida de modo informal | 7 | 1 | 4 | 7 | 7 | 7 | 7 | 7 | 0 | 0 | 0 |
| correção tardia | 3 | 0 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 |
| campo conhecido contradito | 3 | 1 | 1 | 3 | 2 | 2 | 2 | 2 | 0 | 1 | 0 |
| nada faltando | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |
| cliente recusa repetição | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| visita já pedida ou recusada | 4 | 2 | 4 | 4 | 4 | 4 | 4 | 4 | 0 | 0 | 0 |
| sem sentido no contexto | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| anúncio específico | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| reação negativa ao imóvel | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| fácil / outros | 11 | 6 | 9 | 9 | 10 | 11 | 11 | 11 | 0 | 0 | 0 |

### Cobertura × erro por confiança (abaixo do limiar = sem sugestão; o agente decide sozinho)

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.025 | 0 | 1 | 40 |
| 0.300 | 0.975 | 0.026 | 0 | 1 | 39 |
| 0.500 | 0.925 | 0.000 | 0 | 0 | 37 |
| 0.700 | 0.875 | 0.000 | 0 | 0 | 35 |
| 0.900 | 0.800 | 0.000 | 0 | 0 | 32 |

**Jev: Nouls → candidatas → Choice `next`** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.050 | 0 | 2 | 40 |
| 0.300 | 0.950 | 0.053 | 0 | 2 | 38 |
| 0.500 | 0.875 | 0.029 | 0 | 1 | 35 |
| 0.700 | 0.800 | 0.000 | 0 | 0 | 32 |
| 0.900 | 0.475 | 0.000 | 0 | 0 | 19 |

**Jev: Nouls + Choice única mascarada** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.100 | 0 | 4 | 40 |
| 0.300 | 1.000 | 0.100 | 0 | 4 | 40 |
| 0.500 | 0.875 | 0.086 | 0 | 3 | 35 |
| 0.700 | 0.725 | 0.069 | 0 | 2 | 29 |
| 0.900 | 0.550 | 0.000 | 0 | 0 | 22 |

**Jev: Choice única (catálogo inteiro)** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.125 | 4 | 1 | 40 |
| 0.300 | 1.000 | 0.125 | 4 | 1 | 40 |
| 0.500 | 0.875 | 0.086 | 3 | 0 | 35 |
| 0.700 | 0.725 | 0.034 | 1 | 0 | 29 |
| 0.900 | 0.550 | 0.000 | 0 | 0 | 22 |

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — pelo Noul mais fraco (menor distância ao limiar ×2 entre os Nouls do portão)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.025 | 0 | 1 | 40 |
| 0.300 | 0.950 | 0.000 | 0 | 0 | 38 |
| 0.500 | 0.825 | 0.000 | 0 | 0 | 33 |
| 0.700 | 0.625 | 0.000 | 0 | 0 | 25 |
| 0.900 | 0.250 | 0.000 | 0 | 0 | 10 |

### Custo e latência — medidos por grupo de requisições (nada estimado)

| requisições medidas | requisições | novas (não cache) | tokens por conversa | US$_por_1000_conversas | p50_ms por conversa | p95_ms por conversa |
|---|---|---|---|---|---|---|
| `hibrida` em produção (`todas=False`): 1ª + 2ª quando precisa | 52 | 52 | 2616 | 0.1099 | 316 | 594 |
| `codigo` em produção: só a 1ª | 40 | 40 | 2378 | 0.0999 | 296 | 355 |
| comparação (só na medição): Choice única + `next` onde a principal não chama | 40 | 40 | 1234 | 0.0518 | 256 | 301 |
| tudo o que esta execução usou | 92 | 92 | 3850 | 0.1617 | 574 | 856 |

Conversas com 2ª requisição: 12/40 · tokens médios: 1ª 2378, 2ª 796, comparação 1234 · p50 / p95 por requisição: 273 / 345 ms · modelo: jev-1.13.0. A linha da principal é o que `proxima.julgar(todas=False)` envia: a Choice única de comparação não está nela. Latência = a da chamada original de cada requisição (o cache a guarda).

### Caso a caso

`bloqueadas`: C = CRM · N = Noul `answered` (declarado pelo cliente) · O = regra do orçamento sobre o valor lido pelo código · A = anúncio específico (regra) · S = sem sentido; o número é a margem do bloqueio. `rev` = em revisão. `orçamento` = estado da regra e leitura do código (CRM sem o campo). `cand` = candidatas. Escolhas: `lac` primeira lacuna · `pal` palavras-chave · `única` (confiança) · `masc` · `next` (confiança) · `cód` · `híb`. Marca: ✓ aceitável · ✗P proibida · ✗N NQN indevido · ✗F fora do conjunto · ✗∅ sem sugestão. `answered` = Nouls crus; `ret` = `withdrawn`; `sinais` = rental / investor_not_living / specific_property / positive_reaction.

| id | fam | aceitáveis | proibidas | bloqueadas | rev | orçamento | cand | lac | pal | única | masc | next | cód | híb | answered | ret | sinais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PP-T001 | fácil / outros | fin orc bai qua |  |  |  | aberta | fin orc bai qua NQN | fin ✓ | fin ✓ | fin ✓ (0.37) | fin ✓ | fin ✓ (0.74) | fin ✓ | fin ✓ | fin 0.13 orc 0.02 bai 0.03 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.03 |  | 0.02 / 0.12 / 0.04 / 0.02 |
| PP-T002 | valor ambíguo | fin | orc bai qua vag | orc:O0.48 bai:N0.96 qua:N0.96 vag:N0.88 |  | respondida (até 600 → R$ 600.000 preco) | fin NQN | fin ✓ | fin ✓ | fin ✓ (0.93) | fin ✓ | fin ✓ (0.87) | fin ✓ | fin ✓ | fin 0.06 orc 0.97 bai 0.98 qua 0.98 vag 0.94 pra 0.03 pet 0.03 fnc 0.09 vis 0.03 |  | 0.46 / 0.08 / 0.03 / 0.02 |
| PP-T003 | valor ambíguo | orc | fin bai qua fnc | fin:N0.96 bai:N0.96 qua:N0.88 fnc:S0.52 |  | confirmar (até 600) | orc NQN | fin ✗P | NQN ✗N | qua ✗P (0.72) | NQN ✗N | NQN ✗N (0.56) | orc ✓ | orc ✓ | fin 0.98 orc 0.98 bai 0.98 qua 0.94 vag 0.03 pra 0.03 pet 0.02 fnc 0.08 vis 0.03 |  | 0.96 / 0.02 / 0.03 / 0.02 |
| PP-T004 | valor ambíguo | orc | fin bai qua fnc | fin:N0.94 bai:N0.94 qua:N0.90 fnc:N0.68 |  | aberta (prestação de no máximo 3 mil → R$ 3.000 prestacao) | orc NQN | fin ✗P | NQN ✗N | bai ✗P (0.63) | NQN ✗N | orc ✓ (0.20) | orc ✓ | orc ✓ | fin 0.97 orc 0.94 bai 0.97 qua 0.95 vag 0.03 pra 0.03 pet 0.02 fnc 0.84 vis 0.03 |  | 0.02 / 0.02 / 0.04 / 0.02 |
| PP-T005 | já respondida de modo informal | qua | fin orc bai pet fnc | fin:N0.96 orc:O0.52 bai:N0.96 pet:N0.94 fnc:S0.52 |  | respondida (até 3 mil → R$ 3.000 aluguel) | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.96) | qua ✓ | qua ✓ (0.80) | qua ✓ | qua ✓ | fin 0.98 orc 0.98 bai 0.98 qua 0.03 vag 0.03 pra 0.03 pet 0.97 fnc 0.08 vis 0.03 |  | 0.96 / 0.02 / 0.03 / 0.02 |
| PP-T006 | correção tardia | qua | fin orc bai fnc | fin:N0.94 orc:O0.48 bai:N0.92 fnc:S0.48 |  | respondida (até 2500 → R$ 2.500 aluguel) | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.52) | qua ✓ | qua ✓ (0.72) | qua ✓ | qua ✓ | fin 0.97 orc 0.97 bai 0.96 qua 0.03 vag 0.02 pra 0.03 pet 0.02 fnc 0.06 vis 0.03 |  | 0.94 / 0.06 / 0.07 / 0.02 |
| PP-T007 | campo conhecido contradito | orc | fin bai qua | fin:C0.94 orc:C0.16 bai:C0.94 qua:C0.94 |  | — | vag pra pet fnc NQN | vag ✗F | NQN ✗N | orc ✓ (0.89) | NQN ✗N | NQN ✗N (0.35) | NQN ✗N | NQN ✗N | fin 0.97 orc 0.87 bai 0.85 qua 0.90 vag 0.03 pra 0.03 pet 0.03 fnc 0.05 vis 0.16 | fin 0.03 orc 0.42 bai 0.03 qua 0.03 | 0.03 / 0.03 / 0.23 / 0.02 |
| PP-T008 | nada faltando | NQN | fin orc bai qua vag pra pet fnc | fin:C0.96 orc:C0.96 bai:C0.96 qua:C0.96 vag:C0.96 pra:C0.96 pet:C0.96 fnc:C0.96 |  | — | NQN | NQN ✓ | NQN ✓ | NQN ✓ (0.94) | NQN ✓ | NQN ✓ (sem Choice) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.93 bai 0.88 qua 0.93 vag 0.97 pra 0.96 pet 0.96 fnc 0.77 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 | 0.96 / 0.02 / 0.04 / 0.02 |
| PP-T009 | cliente recusa repetição | NQN | fin orc bai qua pet fnc | fin:N0.94 orc:O0.52 bai:N0.96 qua:N0.92 pet:N0.94 fnc:S0.52 |  | respondida (até 3500 → R$ 3.500 aluguel) | vag pra NQN | fin ✗P | bai ✗P | NQN ✓ (0.94) | NQN ✓ | NQN ✓ (0.77) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.98 bai 0.98 qua 0.96 vag 0.03 pra 0.03 pet 0.97 fnc 0.04 vis 0.04 |  | 0.96 / 0.03 / 0.05 / 0.02 |
| PP-T010 | fácil / outros | vis | fin orc bai qua fnc | fin:C0.96 orc:C0.96 bai:C0.96 qua:C0.96 fnc:C0.96 |  | — | vag pra pet vis NQN | vag ✗F | NQN ✗N | vis ✓ (1.00) | vis ✓ | vis ✓ (0.96) | vis ✓ | vis ✓ | fin 0.97 orc 0.88 bai 0.70 qua 0.84 vag 0.05 pra 0.02 pet 0.03 fnc 0.94 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 fnc 0.02 | 0.02 / 0.02 / 0.97 / 0.98 |
| PP-T011 | visita já pedida ou recusada | NQN | fin orc bai qua fnc vis | fin:C0.96 orc:C0.96 bai:C0.94 qua:C0.96 fnc:S0.54 vis:N0.96 |  | — | vag pra pet NQN | vag ✗F | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.82 bai 0.68 qua 0.84 vag 0.03 pra 0.24 pet 0.03 fnc 0.05 vis 0.98 | fin 0.02 orc 0.02 bai 0.03 qua 0.02 | 0.97 / 0.02 / 0.94 / 0.03 |
| PP-T012 | visita já pedida ou recusada | vag pra pet fnc NQN | fin orc bai qua vis | fin:C0.96 orc:C0.96 bai:C0.90 qua:C0.96 vis:N0.94 |  | — | vag pra pet fnc NQN | vag ✓ | NQN ✓ | NQN ✓ (0.94) | NQN ✓ | NQN ✓ (0.66) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.87 bai 0.88 qua 0.86 vag 0.03 pra 0.34 pet 0.03 fnc 0.03 vis 0.97 | fin 0.02 orc 0.02 bai 0.05 qua 0.02 | 0.02 / 0.04 / 0.33 / 0.03 |
| PP-T013 | sem sentido no contexto | vag pra NQN | fin orc bai qua fnc pet | fin:N0.92 orc:O0.96 bai:N0.94 qua:N0.86 pet:S0.94 fnc:N0.96 |  | respondida (até 400 mil → R$ 400.000 preco) | vag pra NQN | fin ✗P | NQN ✓ | NQN ✓ (0.32) | NQN ✓ | pra ✓ (0.15) | NQN ✓ | pra ✓ | fin 0.96 orc 0.98 bai 0.97 qua 0.93 vag 0.02 pra 0.03 pet 0.02 fnc 0.98 vis 0.03 |  | 0.02 / 0.97 / 0.03 / 0.02 |
| PP-T014 | fácil / outros | orc | fin qua bai | fin:C0.94 bai:N0.92 qua:C0.94 |  | aberta | orc NQN | orc ✓ | orc ✓ | orc ✓ (0.81) | orc ✓ | orc ✓ (0.91) | orc ✓ | orc ✓ | fin 0.97 orc 0.04 bai 0.96 qua 0.92 vag 0.03 pra 0.03 pet 0.03 fnc 0.03 vis 0.16 | fin 0.03 qua 0.03 | 0.02 / 0.03 / 0.06 / 0.03 |
| PP-T015 | fácil / outros | NQN fin orc qua | bai | bai:N0.84 |  | aberta | fin orc qua NQN | fin ✓ | fin ✓ | NQN ✓ (0.83) | NQN ✓ | NQN ✓ (0.71) | fin ✓ | fin ✓ | fin 0.05 orc 0.03 bai 0.92 qua 0.03 vag 0.03 pra 0.02 pet 0.02 fnc 0.03 vis 0.03 |  | 0.20 / 0.11 / 0.04 / 0.02 |
| PP-T016 | já respondida de modo informal | orc | fin bai qua pra fnc | fin:N0.96 bai:N0.94 qua:N0.68 pra:N0.92 fnc:S0.42 |  | aberta | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.94) | orc ✓ | orc ✓ (0.96) | orc ✓ | orc ✓ | fin 0.98 orc 0.03 bai 0.97 qua 0.84 vag 0.03 pra 0.96 pet 0.03 fnc 0.02 vis 0.03 |  | 0.91 / 0.02 / 0.03 / 0.02 |
| PP-T017 | já respondida de modo informal | qua | fin orc bai fnc | fin:N0.88 orc:O0.80 bai:N0.96 fnc:N0.94 |  | respondida (até 350 → R$ 350.000 preco) | qua NQN | fin ✗P | fin ✗P | qua ✓ (0.95) | qua ✓ | qua ✓ (0.95) | qua ✓ | qua ✓ | fin 0.94 orc 0.90 bai 0.98 qua 0.03 vag 0.03 pra 0.03 pet 0.02 fnc 0.97 vis 0.03 |  | 0.03 / 0.02 / 0.04 / 0.02 |
| PP-T018 | fácil / outros | orc | fin bai qua vag fnc | fin:N0.92 bai:N0.96 qua:N0.32 vag:N0.96 fnc:S0.46 |  | aberta | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.93) | orc ✓ | orc ✓ (0.90) | orc ✓ | orc ✓ | fin 0.96 orc 0.03 bai 0.98 qua 0.66 vag 0.98 pra 0.02 pet 0.02 fnc 0.02 vis 0.05 |  | 0.93 / 0.03 / 0.06 / 0.04 |
| PP-T019 | anúncio específico | NQN vis fin orc | bai qua | bai:A0.34 qua:A0.34 |  | aberta | fin orc vis NQN | fin ✓ | fin ✓ | NQN ✓ (0.99) | NQN ✓ | NQN ✓ (1.00) | fin ✓ | fin ✓ | fin 0.04 orc 0.03 bai 0.04 qua 0.03 vag 0.02 pra 0.02 pet 0.03 fnc 0.03 vis 0.03 |  | 0.34 / 0.10 / 0.97 / 0.02 |
| PP-T020 | campo conhecido contradito | vag pra NQN | fin orc bai qua pet fnc | fin:C0.96 orc:C0.96 bai:C0.96 qua:C0.96 pet:C0.52 fnc:S0.54 |  | — | vag pra NQN | vag ✓ | NQN ✓ | NQN ✓ (0.98) | NQN ✓ | NQN ✓ (0.82) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.89 bai 0.86 qua 0.84 vag 0.03 pra 0.04 pet 0.96 fnc 0.03 vis 0.04 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 pet 0.24 | 0.97 / 0.02 / 0.24 / 0.03 |
| PP-T021 | valor ambíguo | vag pra pet fnc NQN | fin orc bai qua | fin:N0.96 orc:O0.94 bai:N0.96 qua:N0.96 |  | respondida (até 600 → R$ 600.000 preco) | vag pra pet fnc NQN | fin ✗P | NQN ✓ | NQN ✓ (0.38) | NQN ✓ | NQN ✓ (0.43) | NQN ✓ | NQN ✓ | fin 0.98 orc 0.97 bai 0.98 qua 0.98 vag 0.02 pra 0.02 pet 0.02 fnc 0.05 vis 0.03 |  | 0.04 / 0.02 / 0.04 / 0.02 |
| PP-T022 | valor ambíguo | bai | fin orc qua fnc | fin:N0.94 qua:N0.94 fnc:S0.46 | orc | revisar (até 6 → R$ 6.000 aluguel) | bai NQN | fin ✗P | bai ✓ | orc ✗P (0.44) | bai ✓ | bai ✓ (0.90) | bai ✓ | bai ✓ | fin 0.97 orc 0.29 bai 0.03 qua 0.97 vag 0.02 pra 0.02 pet 0.02 fnc 0.03 vis 0.04 |  | 0.93 / 0.10 / 0.06 / 0.02 |
| PP-T023 | fácil / outros | fin |  |  |  | aberta | fin orc bai qua NQN | fin ✓ | fin ✓ | fin ✓ (0.97) | fin ✓ | fin ✓ (0.99) | fin ✓ | fin ✓ | fin 0.02 orc 0.02 bai 0.02 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.03 |  | 0.05 / 0.06 / 0.03 / 0.02 |
| PP-T024 | visita já pedida ou recusada | NQN fin orc | vis bai qua | bai:A0.28 qua:A0.28 vis:N0.92 |  | aberta | fin orc NQN | fin ✓ | fin ✓ | NQN ✓ (0.96) | NQN ✓ | NQN ✓ (1.00) | fin ✓ | fin ✓ | fin 0.04 orc 0.03 bai 0.08 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.96 |  | 0.22 / 0.08 / 0.94 / 0.03 |
| PP-T025 | nada faltando | NQN | fin orc bai qua vag pra pet fnc | fin:N0.96 orc:O0.54 bai:N0.96 qua:N0.96 vag:N0.94 pra:N0.94 pet:N0.96 fnc:S0.54 |  | respondida (até 3 mil → R$ 3.000 aluguel) | NQN | fin ✗P | NQN ✓ | NQN ✓ (0.60) | NQN ✓ | NQN ✓ (sem Choice) | NQN ✓ | NQN ✓ | fin 0.98 orc 0.98 bai 0.98 qua 0.98 vag 0.97 pra 0.97 pet 0.98 fnc 0.07 vis 0.03 |  | 0.97 / 0.01 / 0.03 / 0.02 |
| PP-T026 | correção tardia | qua | fin orc bai | fin:N0.92 orc:O0.90 bai:N0.92 |  | respondida (até 300 → R$ 300.000 preco) | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.60) | qua ✓ | qua ✓ (0.90) | qua ✓ | qua ✓ | fin 0.96 orc 0.95 bai 0.96 qua 0.03 vag 0.03 pra 0.03 pet 0.02 fnc 0.04 vis 0.03 |  | 0.05 / 0.04 / 0.08 / 0.04 |
| PP-T027 | campo conhecido contradito | qua | fin bai orc | fin:C0.88 orc:C0.94 bai:C0.96 |  | — | qua NQN | vag ✗F | NQN ✗N | qua ✓ (0.73) | qua ✓ | qua ✓ (0.86) | qua ✓ | qua ✓ | fin 0.94 orc 0.89 bai 0.98 qua 0.56 vag 0.03 pra 0.03 pet 0.03 fnc 0.03 vis 0.03 | fin 0.06 orc 0.03 bai 0.02 qua 0.68 | 0.08 / 0.02 / 0.13 / 0.03 |
| PP-T028 | já respondida de modo informal | NQN orc vis | fin bai qua pet fnc | fin:C0.96 bai:A0.24 qua:A0.24 fnc:S0.54 |  | aberta (aluguel tá 3800 → R$ 3.800 aluguel) | orc vis NQN | orc ✓ | orc ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ (0.99) | orc ✓ | orc ✓ | fin 0.97 orc 0.04 bai 0.15 qua 0.19 vag 0.03 pra 0.02 pet 0.24 fnc 0.03 vis 0.04 | fin 0.02 | 0.97 / 0.03 / 0.92 / 0.03 |
| PP-T029 | fácil / outros | orc | fin bai qua fnc | fin:N0.96 bai:N0.88 qua:N0.90 fnc:S0.46 |  | aberta | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.98) | orc ✓ | orc ✓ (0.97) | orc ✓ | orc ✓ | fin 0.98 orc 0.03 bai 0.94 qua 0.95 vag 0.03 pra 0.03 pet 0.02 fnc 0.04 vis 0.03 |  | 0.93 / 0.02 / 0.03 / 0.02 |
| PP-T030 | fácil / outros | NQN vis | fin orc bai qua | fin:C0.96 orc:C0.96 bai:C0.96 qua:C0.96 |  | — | vag pra pet fnc vis NQN | vag ✗F | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ (0.99) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.91 bai 0.68 qua 0.90 vag 0.04 pra 0.02 pet 0.03 fnc 0.03 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 | 0.02 / 0.03 / 0.97 / 0.02 |
| PP-T031 | já respondida de modo informal | bai | fin orc qua pra fnc | fin:N0.80 orc:O0.84 qua:N0.90 pra:N0.96 fnc:N0.96 |  | respondida (até 650 → R$ 650.000 preco) | bai NQN | fin ✗P | fin ✗P | bai ✓ (0.98) | bai ✓ | bai ✓ (0.96) | bai ✓ | bai ✓ | fin 0.90 orc 0.92 bai 0.03 qua 0.95 vag 0.03 pra 0.98 pet 0.02 fnc 0.98 vis 0.04 |  | 0.04 / 0.03 / 0.06 / 0.03 |
| PP-T032 | já respondida de modo informal | orc | fin bai qua fnc | fin:N0.96 bai:N0.90 qua:N0.46 fnc:S0.52 |  | aberta | orc NQN | fin ✗P | orc ✓ | orc ✓ (0.91) | orc ✓ | orc ✓ (0.86) | orc ✓ | orc ✓ | fin 0.98 orc 0.03 bai 0.95 qua 0.73 vag 0.03 pra 0.03 pet 0.02 fnc 0.03 vis 0.03 |  | 0.96 / 0.02 / 0.04 / 0.03 |
| PP-T033 | fácil / outros | fin | orc bai qua | orc:O0.94 bai:N0.96 qua:N0.96 |  | respondida (até 800 → R$ 800.000 preco) | fin NQN | fin ✓ | fin ✓ | NQN ✗N (0.37) | NQN ✗N | fin ✓ (0.37) | fin ✓ | fin ✓ | fin 0.24 orc 0.97 bai 0.98 qua 0.98 vag 0.03 pra 0.03 pet 0.02 fnc 0.04 vis 0.03 |  | 0.03 / 0.10 / 0.03 / 0.02 |
| PP-T034 | fácil / outros | pra pet NQN | fin orc bai qua vag fnc | fin:N0.88 orc:O0.44 bai:N0.76 qua:N0.86 vag:N0.96 fnc:S0.44 |  | respondida (até 2800 → R$ 2.800 aluguel) | pra pet NQN | fin ✗P | bai ✗P | qua ✗P (0.50) | NQN ✓ | pra ✓ (0.54) | NQN ✓ | pra ✓ | fin 0.94 orc 0.96 bai 0.88 qua 0.93 vag 0.98 pra 0.15 pet 0.03 fnc 0.14 vis 0.11 |  | 0.92 / 0.14 / 0.09 / 0.03 |
| PP-T035 | correção tardia | bai | fin orc qua | fin:N0.92 orc:O0.92 qua:N0.94 |  | respondida (esticar até 800 → R$ 800.000 preco) | bai NQN | fin ✗P | bai ✓ | bai ✓ (0.83) | bai ✓ | bai ✓ (0.84) | bai ✓ | bai ✓ | fin 0.96 orc 0.96 bai 0.03 qua 0.97 vag 0.02 pra 0.03 pet 0.02 fnc 0.04 vis 0.03 |  | 0.15 / 0.03 / 0.06 / 0.06 |
| PP-T036 | fácil / outros | NQN fin |  |  |  | aberta | fin orc bai qua NQN | fin ✓ | fin ✓ | NQN ✓ (0.97) | NQN ✓ | NQN ✓ (0.89) | fin ✓ | fin ✓ | fin 0.04 orc 0.02 bai 0.03 qua 0.02 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.03 |  | 0.16 / 0.09 / 0.04 / 0.02 |
| PP-T037 | já respondida de modo informal | bai | fin orc qua fnc | fin:N0.96 orc:O0.54 qua:N0.68 fnc:S0.54 |  | respondida (até 4500 → R$ 4.500 aluguel) | bai NQN | fin ✗P | qua ✗P | bai ✓ (0.99) | bai ✓ | bai ✓ (0.98) | bai ✓ | bai ✓ | fin 0.98 orc 0.98 bai 0.02 qua 0.84 vag 0.03 pra 0.03 pet 0.03 fnc 0.04 vis 0.03 |  | 0.97 / 0.01 / 0.04 / 0.02 |
| PP-T038 | reação negativa ao imóvel | vag pra pet NQN | fin orc bai qua fnc | fin:C0.96 orc:C0.96 bai:C0.96 qua:C0.96 fnc:C0.96 |  | — | vag pra pet vis NQN | vag ✓ | NQN ✓ | NQN ✓ (0.89) | NQN ✓ | NQN ✓ (0.70) | NQN ✓ | NQN ✓ | fin 0.97 orc 0.83 bai 0.71 qua 0.85 vag 0.03 pra 0.03 pet 0.03 fnc 0.91 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 fnc 0.02 | 0.02 / 0.03 / 0.96 / 0.02 |
| PP-T039 | valor ambíguo | qua | fin orc bai fnc | fin:N0.94 orc:O0.46 bai:N0.88 fnc:S0.46 |  | respondida (1600 → R$ 1.600 aluguel) | qua NQN | fin ✗P | qua ✓ | qua ✓ (0.65) | qua ✓ | qua ✓ (0.86) | qua ✓ | qua ✓ | fin 0.97 orc 0.97 bai 0.94 qua 0.03 vag 0.03 pra 0.03 pet 0.03 fnc 0.44 vis 0.03 |  | 0.93 / 0.05 / 0.07 / 0.03 |
| PP-T040 | visita já pedida ou recusada | NQN | fin orc bai qua vis | fin:C0.96 orc:C0.96 bai:C0.96 qua:C0.96 vis:N0.82 |  | — | vag pra pet fnc NQN | vag ✗F | NQN ✓ | NQN ✓ (0.91) | NQN ✓ | NQN ✓ (1.00) | NQN ✓ | NQN ✓ | fin 0.96 orc 0.90 bai 0.74 qua 0.82 vag 0.04 pra 0.02 pet 0.02 fnc 0.03 vis 0.91 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 | 0.02 / 0.03 / 0.96 / 0.91 |
