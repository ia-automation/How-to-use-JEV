# Rascunho — proxima-pergunta (encanamento)

**Rodada 2 — pós-revisão do Codex (2026-10-01), NÃO cega**: o teste já tinha sido aberto e rodado na rodada 1 (`resultados-rodada1.md`, intocado). Perguntas `answered.budget`/`neighbourhood`/`bedrooms` reescritas, valores em dinheiro lidos pelo código (`valores.py`) e postos no state, regra do orçamento em código, validação da 2ª etapa e custo da principal medido em requisições próprias → o state e as perguntas mudaram: chamadas novas.

## Conjunto `rascunho` — 5 conversas (arquivo versão 2026-10-01, autor fable); 0 difíceis, 2 em que `no_question_needed` NÃO é aceitável, 0 acima do teto, 0 falhas operacionais

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

> Sem requisição de comparação neste conjunto (`todas=False`): só as baselines de código e as variantes que a 1ª e a 2ª requisição da principal alimentam.

### Escolha — baselines de código × variantes com Jev, nos mesmos casos

`acerto` = escolha ∈ `aceitaveis`. **PROIBIDA escolhida** = erro caro: perguntou o que o cliente já disse, o que o CRM já tem ou o que não faz sentido (∈ `proibidas`). **NQN indevido** = respondeu `no_question_needed` onde ele não é aceitável (deixou de perguntar o essencial); denominador = casos em que NQN não é aceitável. `fora do conjunto` = pergunta nem aceitável nem proibida (fora de hora). `sem sugestão (revisão)` = a etapa não devolveu pergunta: item essencial em revisão, falha operacional ou teto — NÃO conta como acerto. `perguntou algo` = escolha ≠ NQN. Variante principal (a que o critério julga): **Jev: Nouls + código nas essenciais, Choice `next` no resto**.

| variante | n | acerto (∈ aceitáveis) | PROIBIDA escolhida | NQN indevido | fora do conjunto | sem sugestão (revisão) | acerto onde NQN não é aceitável | perguntou algo |
|---|---|---|---|---|---|---|---|---|
| primeira lacuna (só CRM) | 5 | 0.000 | 4/5 | 0/2 | 1/5 | 0/5 | 0/2 | 5/5 |
| lacuna + palavras-chave | 5 | 0.800 | 0/5 | 1/2 | 0/5 | 0/5 | 1/2 | 2/5 |
| sempre no_question_needed | 5 | 0.600 | 0/5 | 2/2 | 0/5 | 0/5 | 0/2 | 0/5 |
| Jev: Nouls + política de código | 5 | 1.000 | 0/5 | 0/2 | 0/5 | 0/5 | 2/2 | 3/5 |
| Jev: Nouls + código nas essenciais, Choice `next` no resto | 5 | 1.000 | 0/5 | 0/2 | 0/5 | 0/5 | 2/2 | 3/5 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 pergunta proibida escolhida | 0/5 | ≤ 1 | ✓ |
| 2 acerto (∈ aceitáveis) | 1.000 (melhor baseline de código: lacuna + palavras-chave, 0.800) | ≥ 0.950 | ✓ |
| 3 `no_question_needed` indevido | 0/2 | ≤ 2 | ✓ |
| 4 contra a Choice única | não medida neste conjunto (sem requisição de comparação) | acerto ≥ e proibidas ≤ | — |
| secundário: proibidas bloqueadas pelo código | 17/17 (1.000) | ≥ 0.9 | ✓ |
| secundário: aceitável bloqueada indevidamente | 0/15 (0.000) | ≤ 0.05 | ✓ |

### Portão — o que o código bloqueou × `proibidas` do gabarito, por item

Bloqueada = campo do CRM não retirado (regra exata) · `answered` ≥ limiar (preferência DECLARADA pelo cliente) · `orcamento` pela regra do LEIA-ME sobre o valor lido pelo código · bairro e quartos do anúncio específico (regra) · sem sentido (`financiamento` em aluguel, `pet` de investidor). Em revisão = o código não deixa perguntar nem dá por respondido (não conta como bloqueada). `Noul cru` compara só o `answered` com o gabarito (proibida ⇒ alto; aceitável ⇒ baixo): na rodada 2 ele deixou de ser o portão em `orcamento` (o Noul diz se o valor é do cliente; aluguel + "até 600" é declarado E aceitável), em `bairro`/`quartos` com anúncio citado, e em `financiamento`/`pet` sem sentido — ali quem bloqueia é a regra. Item fora dos dois conjuntos não entra.

| item | proibidas bloqueadas | aceitáveis bloqueadas (indevido) | em revisão (proibidas · aceitáveis) | Noul cru ≥ limiar × proibida | menor Noul entre proibidas | maior Noul entre aceitáveis | brier |
|---|---|---|---|---|---|---|---|
| finalidade | 5/5 | 0/0 | 0 · 0 | 1.000 | 0.96 | — | 0.001 |
| orcamento | 3/3 | 0/2 | 0 · 0 | 1.000 | 0.87 | 0.03 | 0.004 |
| bairro | 4/4 | 0/1 | 0 · 0 | 0.800 | 0.47 | 0.03 | 0.057 |
| quartos | 3/3 | 0/2 | 0 · 0 | 1.000 | 0.78 | 0.03 | 0.017 |
| vagas | 0/0 | 0/2 | 0 · 0 | 1.000 | — | 0.03 | 0.001 |
| prazo | 0/0 | 0/2 | 0 · 0 | 1.000 | — | 0.03 | 0.001 |
| pet | 0/0 | 0/2 | 0 · 0 | 1.000 | — | 0.02 | 0.000 |
| financiamento | 2/2 | 0/3 | 0 · 0 | 0.600 | 0.02 | 0.03 | 0.385 |
| visita | 0/0 | 0/1 | 0 · 0 | 1.000 | — | 0.03 | 0.001 |

Total: proibidas bloqueadas 17/17 · aceitáveis bloqueadas indevidamente 0/15 · em revisão: 0 proibidas, 0 aceitáveis

Cada bloqueio sai com `motivo` (`noul` | `regra`), a evidência e a margem (menor distância ao limiar, ×2, entre os Nouls que o sustentam: 0 = em cima do limiar):

| motivo | detalhe | n | em proibidas | em aceitáveis | fora dos dois | menor margem | margem < 0,3 |
|---|---|---|---|---|---|---|---|
| noul | declarado pelo cliente | 9 | 9 | 0 | 0 | 0.56 | 0 |
| regra | orçamento declarado, lido pelo código | 2 | 2 | 0 | 0 | 0.96 | 0 |
| regra | sem sentido (aluguel) | 2 | 2 | 0 | 0 | 0.38 | 0 |
| regra | CRM | 4 | 4 | 0 | 0 | 0.96 | 0 |

`withdrawn.<campo>` (campo do CRM retirado sem valor novo; gabarito = o campo voltou a ser aceitável): acerto a 0.5 = 1.000 (n = 4; 0 retirados; maior valor entre os não retirados 0.02; menor entre os retirados nan)

### Regra do orçamento em código (CRM sem o campo) × gabarito

`respondida` = valor declarado (Noul) e lido pela regra → bloqueia · `confirmar` = aluguel + centenas sem unidade → candidata · `aberta` = sem valor, prestação em compra ou valor que não é limite do cliente → candidata · `revisar` = a regra não decide → nem pergunta nem bloqueio.

| estado | n | orcamento proibida | orcamento aceitável | fora dos dois |
|---|---|---|---|---|
| respondida | 2 | 2 | 0 | 0 |
| aberta | 2 | 0 | 2 | 0 |

Itens em revisão: nenhum

### Por família difícil (pela `nota` do rotulador) — acertos

| família | n | primeira lacuna (só CRM) | lacuna + palavras-chave | Nouls + política de código | Nouls + código nas essenciais, Choice `next` no resto | proibidas (principal) | NQN indevido (principal) | sem sugestão (principal) |
|---|---|---|---|---|---|---|---|---|
| fácil / outros | 5 | 0 | 4 | 5 | 5 | 0 | 0 | 0 |

### Cobertura × erro por confiança (abaixo do limiar = sem sugestão; o agente decide sozinho)

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — confiança da Choice que decidiu (sem Choice = 1,0)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.300 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.500 | 0.600 | 0.000 | 0 | 0 | 3 |
| 0.700 | 0.600 | 0.000 | 0 | 0 | 3 |
| 0.900 | 0.600 | 0.000 | 0 | 0 | 3 |

**Jev: Nouls + código nas essenciais, Choice `next` no resto** — pelo Noul mais fraco (menor distância ao limiar ×2 entre os Nouls do portão)

| limiar | cobertura | erro_automatico | proibidas | nqn_indevido | n_auto |
|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.300 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.500 | 1.000 | 0.000 | 0 | 0 | 5 |
| 0.700 | 0.800 | 0.000 | 0 | 0 | 4 |
| 0.900 | 0.600 | 0.000 | 0 | 0 | 3 |

### Custo e latência — medidos por grupo de requisições (nada estimado)

| requisições medidas | requisições | novas (não cache) | tokens por conversa | US$_por_1000_conversas | p50_ms por conversa | p95_ms por conversa |
|---|---|---|---|---|---|---|
| `hibrida` em produção (`todas=False`): 1ª + 2ª quando precisa | 8 | 0 | 2791 | 0.1172 | 571 | 628 |
| `codigo` em produção: só a 1ª | 5 | 0 | 2299 | 0.0965 | 303 | 310 |
| comparação (só na medição): Choice única + `next` onde a principal não chama | 0 | 0 | 0 | 0.0000 | 0 | 0 |
| tudo o que esta execução usou | 8 | 0 | 2791 | 0.1172 | 571 | 628 |

Conversas com 2ª requisição: 3/5 · tokens médios: 1ª 2299, 2ª 821, comparação 0 · p50 / p95 por requisição: 303 / 342 ms · modelo: jev-1.13.0. A linha da principal é o que `proxima.julgar(todas=False)` envia: a Choice única de comparação não está nela. Latência = a da chamada original de cada requisição (o cache a guarda).

### Caso a caso

`bloqueadas`: C = CRM · N = Noul `answered` (declarado pelo cliente) · O = regra do orçamento sobre o valor lido pelo código · A = anúncio específico (regra) · S = sem sentido; o número é a margem do bloqueio. `rev` = em revisão. `orçamento` = estado da regra e leitura do código (CRM sem o campo). `cand` = candidatas. Escolhas: `lac` primeira lacuna · `pal` palavras-chave · `única` (confiança) · `masc` · `next` (confiança) · `cód` · `híb`. Marca: ✓ aceitável · ✗P proibida · ✗N NQN indevido · ✗F fora do conjunto · ✗∅ sem sugestão. `answered` = Nouls crus; `ret` = `withdrawn`; `sinais` = rental / investor_not_living / specific_property / positive_reaction.

| id | fam | aceitáveis | proibidas | bloqueadas | rev | orçamento | cand | lac | pal | única | masc | next | cód | híb | answered | ret | sinais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PP-R001 | fácil / outros | vag pra pet fnc NQN | fin orc bai qua | fin:N0.94 orc:O0.96 bai:N0.96 qua:N0.56 |  | respondida (até 800 mil → R$ 800.000 preco) | vag pra pet fnc NQN | fin ✗P | NQN ✓ | — | — | — | NQN ✓ | NQN ✓ | fin 0.97 orc 0.98 bai 0.98 qua 0.78 vag 0.02 pra 0.02 pet 0.02 fnc 0.03 vis 0.03 |  | 0.02 / 0.02 / 0.03 / 0.02 |
| PP-R002 | fácil / outros | orc bai qua | fin fnc | fin:N0.96 fnc:S0.52 |  | aberta | orc bai qua NQN | fin ✗P | orc ✓ | — | — | — | orc ✓ | orc ✓ | fin 0.98 orc 0.03 bai 0.03 qua 0.03 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.03 |  | 0.96 / 0.03 / 0.03 / 0.02 |
| PP-R003 | fácil / outros | vis fnc | fin orc bai qua | fin:C0.96 orc:C0.96 bai:C0.96 qua:C0.96 |  | — | vag pra pet fnc vis NQN | vag ✗F | NQN ✗N | — | — | — | vis ✓ | vis ✓ | fin 0.96 orc 0.87 bai 0.47 qua 0.82 vag 0.04 pra 0.02 pet 0.03 fnc 0.03 vis 0.03 | fin 0.02 orc 0.02 bai 0.02 qua 0.02 | 0.02 / 0.03 / 0.97 / 0.97 |
| PP-R004 | fácil / outros | vag pra pet fnc NQN | fin orc bai qua | fin:N0.94 orc:O0.96 bai:N0.94 qua:N0.90 |  | respondida (até 300 mil → R$ 300.000 preco) | vag pra pet fnc NQN | fin ✗P | NQN ✓ | — | — | — | NQN ✓ | NQN ✓ | fin 0.97 orc 0.98 bai 0.97 qua 0.95 vag 0.03 pra 0.03 pet 0.02 fnc 0.03 vis 0.03 |  | 0.02 / 0.02 / 0.03 / 0.02 |
| PP-R005 | fácil / outros | NQN orc qua | fin bai fnc | fin:N0.94 bai:N0.94 fnc:S0.38 |  | aberta | orc qua NQN | fin ✗P | orc ✓ | — | — | — | orc ✓ | orc ✓ | fin 0.97 orc 0.03 bai 0.97 qua 0.03 vag 0.02 pra 0.02 pet 0.02 fnc 0.02 vis 0.03 |  | 0.89 / 0.06 / 0.03 / 0.02 |
