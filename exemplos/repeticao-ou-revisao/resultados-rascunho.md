# Rascunho — repeticao-ou-revisao (encanamento)

## Conjunto `rascunho` — 5 grupos (arquivo versão 2026-10-01, autor fable); 2 `same_intent`, 2 `revision`, 1 `additional_request`, 0 `unclear`; 0 difíceis; 0 grupos de 3

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Relação (4 classes) — métrica principal, baselines × sempre revisa × Jev nos mesmos grupos

Sinal de reconciliação: `same_intent` → colapsar · `revision` → substituir · `additional_request` → somar · `unclear` → revisar. **CORREÇÃO PERDIDA** = gabarito `revision` que saiu `same_intent` (colapsar apaga a correção). **EFEITO DUPLICADO** = gabarito `same_intent` que saiu `additional_request` (somar executa duas vezes). `igualdade normalizada` = textos iguais ⇒ repetição, senão executa tudo; `Jaccard de palavras` = ≥ 0.5 ⇒ repetição, ≥ 0.05 ⇒ revisão, abaixo ⇒ pedido novo (limiares da grade do ajuste); `a última sempre vale` = sempre revisão; `sempre revisa` = zero erro caro, 100% dos grupos a humano; `só Choice` = a opção vencedora, sem Nouls nem piso; `Jev (política)` = Choice confirmada pelos Nouls, dúvida → revisar. `acao_vigente` é derivada da relação prevista. As duas variantes do Jev leem a MESMA resposta.

| variante | n | acerto_relacao | CORREÇÃO PERDIDA (revision → colapsar) | EFEITO DUPLICADO (same_intent → somar) | acao_vigente certa | unclear → revisar | revisou sem necessidade |
|---|---|---|---|---|---|---|---|
| baseline: igualdade normalizada | 5 | 0.600 | 0/2 | 0/2 | 3/5 | 0/0 | 0/5 |
| baseline: Jaccard de palavras | 5 | 0.800 | 0/2 | 0/2 | 4/5 | 0/0 | 0/5 |
| baseline: a última sempre vale | 5 | 0.400 | 0/2 | 0/2 | 2/5 | 0/0 | 0/5 |
| sempre revisa | 5 | 0.000 | 0/2 | 0/2 | 1/5 | 0/0 | 5/5 |
| só Choice | 5 | 1.000 | 0/2 | 0/2 | 5/5 | 0/0 | 0/5 |
| Jev (política) | 5 | 1.000 | 0/2 | 0/2 | 5/5 | 0/0 | 0/5 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 correção perdida | 0/2 | ≤ 0 | ✓ |
| 2 efeito duplicado | 0/2 | ≤ 1 | ✓ |
| 3 acerto da relação | 1.000 (melhor baseline: Jaccard de palavras 0.800) | ≥ 0.950 | ✓ |
| secundário: unclear → revisar | 0/0 (0.000) | ≥ 0.7 | ✗ |
| secundário: revisou sem necessidade | 0/5 (0.000) | ≤ 0.2 | ✓ |
| secundário: acao_vigente certa | 5/5 (1.000) | ≥ 0.8 | ✓ |

**Matriz de confusão — Jev (política)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 2 | 0 | 0 | 0 |
| revision | 0 | 2 | 0 | 0 |
| additional_request | 0 | 0 | 1 | 0 |
| unclear | 0 | 0 | 0 | 0 |

**Matriz de confusão — só Choice** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 2 | 0 | 0 | 0 |
| revision | 0 | 2 | 0 | 0 |
| additional_request | 0 | 0 | 1 | 0 |
| unclear | 0 | 0 | 0 | 0 |

**Matriz de confusão — baseline: igualdade normalizada** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 2 | 0 | 0 | 0 |
| revision | 0 | 0 | 2 | 0 |
| additional_request | 0 | 0 | 1 | 0 |
| unclear | 0 | 0 | 0 | 0 |

**Matriz de confusão — baseline: Jaccard de palavras** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 2 | 0 | 0 | 0 |
| revision | 0 | 1 | 1 | 0 |
| additional_request | 0 | 0 | 1 | 0 |
| unclear | 0 | 0 | 0 | 0 |

**Matriz de confusão — baseline: a última sempre vale** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 0 | 2 | 0 | 0 |
| revision | 0 | 2 | 0 | 0 |
| additional_request | 0 | 1 | 0 | 0 |
| unclear | 0 | 0 | 0 | 0 |

**Erros caros, grupo a grupo** (todas as variantes)

_(nenhum)_

### O que o código resolveu sem o Jev

Texto idêntico após normalização em todas as mensagens ⇒ `same_intent` sem chamada: 2 grupos, 2/2 com gabarito `same_intent` (RR-R001, RR-R005). Grupos em que o código tirou uma cópia adjacente e mandou ao Jev só as mensagens distintas: 0.

### Nouls contra a relação do gabarito — 3 grupos que foram ao Jev

Cada Noul é o sim/não de UMA relação (`replaces_previous` ↔ `revision`; `soma` = o maior entre `adds_new_request` e `completes_previous` ↔ `additional_request`; `same_request_again` ↔ `same_intent`); grupos `unclear` ficam fora (o gabarito não diz sim nem não). Acerto com corte 0,5; `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela.

| noul | positivos | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| replaces_previous | 2 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 3 | 0.001 |
| soma | 1 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 3 | 0.013 |
| same_request_again | 0 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 3 | 0.001 |

**Nouls de dúvida** (o lado absoluto da opção `unclear`; qualquer um ≥ `sim` → revisar): mín–máx dentro e fora dos grupos `unclear`, e quantos passam do `sim`.

| noul | unclear: mín–máx | unclear ≥ sim | demais: mín–máx | demais ≥ sim | faixa |
|---|---|---|---|---|---|
| no_link_word | — | 0/0 | 0.02–0.10 | 0/3 | 0.3–0.7 |
| target_not_said | — | 0/0 | 0.02–0.03 | 0/3 | 0.3–0.7 |
| arrived_out_of_order | — | 0/0 | 0.05–0.06 | 0/3 | 0.3–0.7 |

Os Nouls de relação nos grupos `unclear`: `replaces_previous` —; `adds_new_request` —; `completes_previous` —; `same_request_again` —.

### Choice `relation` sozinha — cobertura × erro por confiança

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 3 |
| 0.300 | 1.000 | 0.000 | 3 |
| 0.500 | 1.000 | 0.000 | 3 |
| 0.700 | 1.000 | 0.000 | 3 |
| 0.900 | 1.000 | 0.000 | 3 |

**Os Nouls acrescentam algo à Choice?** A política só pode mandar a `revisar` o que a Choice propôs. Mudou 0 grupo(s): 0 `unclear` recuperado(s), 0 erro(s) caro(s) evitado(s), 0 outro(s) erro(s) trocado(s) por revisão, 0 acerto(s) da Choice mandado(s) a `revisar` sem necessidade.

### Por família (pela `nota` do rotulador; fáceis agrupadas pela relação)

| família | gabarito | n | Jev | só Choice | igualdade | Jaccard | última vale | Jev → revisar | sem chamada (código) | erro caro Jev |
|---|---|---|---|---|---|---|---|---|---|---|
| fácil: additional_request | add | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0 | 0 | 0 |
| fácil: revision | rev | 2 | 1.000 | 1.000 | 0.000 | 0.500 | 1.000 | 0 | 0 | 0 |
| fácil: same_intent | same | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0 | 2 | 0 |

### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)

`cobertura_auto` = grupo que não foi a `revisar` (inclui os resolvidos pelo código sem chamada). **Faixa dos Nouls** (a mesma em todos):

| faixa (todos os Nouls) | cobertura_auto | erro_automatico | correções perdidas | efeitos duplicados | unclear automatizado | n_auto |
|---|---|---|---|---|---|---|
| atual (perguntas.py) | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.4–0.6 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.3–0.7 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.2–0.8 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.1–0.9 | 0.800 | 0.000 | 0 | 0 | 0 | 4 |
| 0.05–0.95 | 0.800 | 0.000 | 0 | 0 | 0 | 4 |

**Piso de confiança da Choice** (o resto como em `perguntas.py`):

| piso de confiança da Choice | cobertura_auto | erro_automatico | correções perdidas | efeitos duplicados | unclear automatizado | n_auto |
|---|---|---|---|---|---|---|
| atual (perguntas.py) | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.000 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.300 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.500 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.700 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| 0.900 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |

**Baseline Jaccard — grade de limiares neste conjunto** (os de `perguntas.py` foram escolhidos no ajuste):

| ≥ mesmo | ≥ revisão | acerto_relacao | correções perdidas | efeitos duplicados |
|---|---|---|---|---|
| 0.400 | 0.050 | 0.800 | 0 | 0 |
| 0.400 | 0.100 | 0.800 | 0 | 0 |
| 0.400 | 0.200 | 0.800 | 0 | 0 |
| 0.500 | 0.050 | 0.800 | 0 | 0 |
| 0.500 | 0.100 | 0.800 | 0 | 0 |
| 0.500 | 0.200 | 0.800 | 0 | 0 |

### Custo e latência (medidos na chamada real; do cache também)

| grupos | requisicoes | novas (não cache) | sem chamada (código resolve) | fora da faixa (sem chamada) | falhas operacionais (→ revisar) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_1000_grupos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 3 | 3 | 2 | 0 | 0 | 24 | 318 | 606 | 2686 | 0.000338 | 0.0676 | jev-1.13.0 |

### Caso a caso

`choice` = opção vencedora da Choice (confiança); `troca`/`soma`/`compl`/`mesma` = Nouls `replaces_previous`, `adds_new_request`, `completes_previous`, `same_request_again`; `s/elo`/`s/alvo`/`ordem` = Nouls de dúvida `no_link_word`, `target_not_said`, `arrived_out_of_order`; `Jev` = relação da política (`unclear` = revisar); `ok` compara com o gabarito; `caro` marca o erro caro; `vig` = `acao_vigente` derivada bate com o gabarito; `=`/`J`/`últ` = baselines igualdade, Jaccard e última vale; `—` = grupo resolvido pelo código sem chamada, ou falha.

| id | fam | gab | msgs | choice | troca | soma | compl | mesma | s/elo | s/alvo | ordem | Jev | sinal | ok | caro | vig | = | J | últ | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RR-R001 | fácil: same_intent | same | 2 | — | — | — | — | — | — | — | — | same | colapsar | ✓ |  | ✓ | same | same | rev | texto idêntico após normalização (código) |
| RR-R002 | fácil: revision | rev | 2 | rev (1.00) | 0.98 | 0.04 | 0.08 | 0.02 | 0.05 | 0.02 | 0.06 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-R003 | fácil: additional_request | add | 2 | add (1.00) | 0.05 | 0.83 | 0.62 | 0.03 | 0.10 | 0.02 | 0.05 | add | somar | ✓ |  | ✓ | add | add | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-R004 | fácil: revision | rev | 2 | rev (1.00) | 0.99 | 0.03 | 0.05 | 0.02 | 0.02 | 0.03 | 0.05 | rev | substituir | ✓ |  | ✓ | add | add | rev | a última corrige, troca ou cancela |
| RR-R005 | fácil: same_intent | same | 2 | — | — | — | — | — | — | — | — | same | colapsar | ✓ |  | ✓ | same | same | rev | texto idêntico após normalização (código) |
