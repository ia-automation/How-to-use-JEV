# Resultados — repeticao-ou-revisao

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; validação, deduplicação exata, composição e baselines: `relacao.py`. Preço: US$ 0,042 por milhão de tokens de entrada. State: minutos fora; grupo de 3: inteiro. Faixa validada: até 3 mensagens distintas e 1500 caracteres (acima → revisar, sem chamada). O sinal é proposta de reconciliação: nada é executado nem descartado.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (58 grupos: 16 same_intent, 18 revision, 17 additional_request, 7 unclear), com a política acima; **1_correcao_perdida**: revisão (gabarito revision) que saiu `colapsar` = 0 (de 18); **2_efeito_duplicado**: repetição (gabarito same_intent) que saiu `somar` ≤ 1 (de 16); **3_acerto_relacao**: relação (4 classes) ≥ melhor baseline de código no próprio teste + 0,15; **secundario_nao_decide**: unclear → `revisar` ≥ 70% (≥ 5 de 7); revisou sem necessidade ≤ 20% dos decidíveis; `acao_vigente` certa ≥ 80%; **se_falhar**: 1 falhando = não serve para colapsar sem humano (só a igualdade exata do código colapsa); 2 falhando = `somar` precisa de confirmação; 3 falhando = a regra de código basta

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T14:52:05-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 f60a3cf35481f94d… · `relacao.py` sha256 b26f238bcbedd18e… · `run.py` sha256 f5f5c884bcb23925… · `dados/teste.json` sha256 a47e759ecfc81136…

## Lado a lado

### Relação por variante e conjunto

| conjunto | variante | n | acerto_relacao | CORREÇÃO PERDIDA (revision → colapsar) | EFEITO DUPLICADO (same_intent → somar) | acao_vigente certa | unclear → revisar | revisou sem necessidade |
|---|---|---|---|---|---|---|---|---|
| ajuste | baseline: igualdade normalizada | 29 | 0.345 | 0/9 | 6/8 | 14/29 | 0/4 | 0/25 |
| ajuste | baseline: Jaccard de palavras | 29 | 0.586 | 0/9 | 1/8 | 18/29 | 0/4 | 0/25 |
| ajuste | baseline: a última sempre vale | 29 | 0.310 | 0/9 | 0/8 | 9/29 | 0/4 | 0/25 |
| ajuste | sempre revisa | 29 | 0.138 | 0/9 | 0/8 | 12/29 | 4/4 | 25/25 |
| ajuste | só Choice | 29 | 0.897 | 0/9 | 0/8 | 26/29 | 2/4 | 0/25 |
| ajuste | Jev (política) | 29 | 0.931 | 0/9 | 0/8 | 28/29 | 4/4 | 2/25 |
| teste | baseline: igualdade normalizada | 58 | 0.345 | 0/18 | 13/16 | 27/58 | 0/7 | 0/51 |
| teste | baseline: Jaccard de palavras | 58 | 0.448 | 0/18 | 2/16 | 28/58 | 0/7 | 0/51 |
| teste | baseline: a última sempre vale | 58 | 0.310 | 0/18 | 0/16 | 18/58 | 0/7 | 0/51 |
| teste | sempre revisa | 58 | 0.121 | 0/18 | 0/16 | 24/58 | 7/7 | 51/51 |
| teste | só Choice | 58 | 0.931 | 0/18 | 0/16 | 54/58 | 4/7 | 0/51 |
| teste | Jev (política) | 58 | 0.862 | 0/18 | 0/16 | 54/58 | 7/7 | 8/51 |

### Nouls, código, custo

| conjunto | n | difíceis | replaces_previous ≥0,5 | soma ≥0,5 | same_request_again ≥0,5 | código sem chamada (certos) | Nouls mudaram a Choice | requisições | p50_ms | p95_ms | tokens_por_requisicao | US$_por_1000_grupos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | 29 | 24 | 0.957 | 0.957 | 1.000 | 2/2 | 4 | 27 | 306 | 340 | 2693 | 0.1053 | jev-1.13.0 |
| teste | 58 | 42 | 0.938 | 0.938 | 1.000 | 3/3 | 11 | 55 | 270 | 355 | 2694 | 0.1073 | jev-1.13.0 |

## Conjunto `ajuste` — 29 grupos (arquivo versão 2026-10-01, autor fable); 8 `same_intent`, 9 `revision`, 8 `additional_request`, 4 `unclear`; 24 difíceis; 5 grupos de 3

### Relação (4 classes) — métrica principal, baselines × sempre revisa × Jev nos mesmos grupos

Sinal de reconciliação: `same_intent` → colapsar · `revision` → substituir · `additional_request` → somar · `unclear` → revisar. **CORREÇÃO PERDIDA** = gabarito `revision` que saiu `same_intent` (colapsar apaga a correção). **EFEITO DUPLICADO** = gabarito `same_intent` que saiu `additional_request` (somar executa duas vezes). `igualdade normalizada` = textos iguais ⇒ repetição, senão executa tudo; `Jaccard de palavras` = ≥ 0.5 ⇒ repetição, ≥ 0.05 ⇒ revisão, abaixo ⇒ pedido novo (limiares da grade do ajuste); `a última sempre vale` = sempre revisão; `sempre revisa` = zero erro caro, 100% dos grupos a humano; `só Choice` = a opção vencedora, sem Nouls nem piso; `Jev (política)` = Choice confirmada pelos Nouls, dúvida → revisar. `acao_vigente` é derivada da relação prevista. As duas variantes do Jev leem a MESMA resposta.

| variante | n | acerto_relacao | CORREÇÃO PERDIDA (revision → colapsar) | EFEITO DUPLICADO (same_intent → somar) | acao_vigente certa | unclear → revisar | revisou sem necessidade |
|---|---|---|---|---|---|---|---|
| baseline: igualdade normalizada | 29 | 0.345 | 0/9 | 6/8 | 14/29 | 0/4 | 0/25 |
| baseline: Jaccard de palavras | 29 | 0.586 | 0/9 | 1/8 | 18/29 | 0/4 | 0/25 |
| baseline: a última sempre vale | 29 | 0.310 | 0/9 | 0/8 | 9/29 | 0/4 | 0/25 |
| sempre revisa | 29 | 0.138 | 0/9 | 0/8 | 12/29 | 4/4 | 25/25 |
| só Choice | 29 | 0.897 | 0/9 | 0/8 | 26/29 | 2/4 | 0/25 |
| Jev (política) | 29 | 0.931 | 0/9 | 0/8 | 28/29 | 4/4 | 2/25 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 correção perdida | 0/9 | ≤ 0 | ✓ |
| 2 efeito duplicado | 0/8 | ≤ 1 | ✓ |
| 3 acerto da relação | 0.931 (melhor baseline: Jaccard de palavras 0.586) | ≥ 0.736 | ✓ |
| secundário: unclear → revisar | 4/4 (1.000) | ≥ 0.7 | ✓ |
| secundário: revisou sem necessidade | 2/25 (0.080) | ≤ 0.2 | ✓ |
| secundário: acao_vigente certa | 28/29 (0.966) | ≥ 0.8 | ✓ |

**Matriz de confusão — Jev (política)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 7 | 0 | 0 | 1 |
| revision | 0 | 9 | 0 | 0 |
| additional_request | 0 | 0 | 7 | 1 |
| unclear | 0 | 0 | 0 | 4 |

**Matriz de confusão — só Choice** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 8 | 0 | 0 | 0 |
| revision | 0 | 9 | 0 | 0 |
| additional_request | 0 | 1 | 7 | 0 |
| unclear | 0 | 2 | 0 | 2 |

**Matriz de confusão — baseline: igualdade normalizada** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 2 | 0 | 6 | 0 |
| revision | 0 | 0 | 9 | 0 |
| additional_request | 0 | 0 | 8 | 0 |
| unclear | 0 | 0 | 4 | 0 |

**Matriz de confusão — baseline: Jaccard de palavras** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 4 | 3 | 1 | 0 |
| revision | 0 | 8 | 1 | 0 |
| additional_request | 1 | 2 | 5 | 0 |
| unclear | 0 | 3 | 1 | 0 |

**Matriz de confusão — baseline: a última sempre vale** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 0 | 8 | 0 | 0 |
| revision | 0 | 9 | 0 | 0 |
| additional_request | 0 | 8 | 0 | 0 |
| unclear | 0 | 4 | 0 | 0 |

**Erros caros, grupo a grupo** (todas as variantes)

| id | variante | erro | família |
|---|---|---|---|
| RR-A003 | baseline: igualdade normalizada | EFEITO DUPLICADO | negativa que não revisa |
| RR-A005 | baseline: igualdade normalizada | EFEITO DUPLICADO | cópia de terceiro |
| RR-A006 | baseline: igualdade normalizada | EFEITO DUPLICADO | asterisco que só corrige grafia |
| RR-A008 | baseline: igualdade normalizada | EFEITO DUPLICADO | paráfrase |
| RR-A017 | baseline: igualdade normalizada | EFEITO DUPLICADO | retry com erro de digitação |
| RR-A023 | baseline: igualdade normalizada | EFEITO DUPLICADO | fácil: same_intent |
| RR-A006 | baseline: Jaccard de palavras | EFEITO DUPLICADO | asterisco que só corrige grafia |

### O que o código resolveu sem o Jev

Texto idêntico após normalização em todas as mensagens ⇒ `same_intent` sem chamada: 2 grupos, 2/2 com gabarito `same_intent` (RR-A004, RR-A013). Grupos em que o código tirou uma cópia adjacente e mandou ao Jev só as mensagens distintas: 2 (RR-A011, RR-A015).

### Nouls contra a relação do gabarito — 27 grupos que foram ao Jev

Cada Noul é o sim/não de UMA relação (`replaces_previous` ↔ `revision`; `soma` = o maior entre `adds_new_request` e `completes_previous` ↔ `additional_request`; `same_request_again` ↔ `same_intent`); grupos `unclear` ficam fora (o gabarito não diz sim nem não). Acerto com corte 0,5; `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela.

| noul | positivos | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| replaces_previous | 9 | 0.957 | 0.3–0.7 | 1.000 | 0.957 | 0 | 23 | 0.029 |
| soma | 8 | 0.957 | 0.3–0.7 | 0.870 | 1.000 | 3 | 23 | 0.040 |
| same_request_again | 6 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 23 | 0.010 |

**Nouls de dúvida** (o lado absoluto da opção `unclear`; qualquer um ≥ `sim` → revisar): mín–máx dentro e fora dos grupos `unclear`, e quantos passam do `sim`.

| noul | unclear: mín–máx | unclear ≥ sim | demais: mín–máx | demais ≥ sim | faixa |
|---|---|---|---|---|---|
| no_link_word | 0.03–0.94 | 3/4 | 0.02–0.87 | 1/23 | 0.3–0.7 |
| target_not_said | 0.03–0.95 | 1/4 | 0.01–0.09 | 0/23 | 0.3–0.7 |
| arrived_out_of_order | 0.07–0.93 | 1/4 | 0.04–0.18 | 0/23 | 0.3–0.7 |

Os Nouls de relação nos grupos `unclear`: `replaces_previous` 0.80–0.96; `adds_new_request` 0.04–0.10; `completes_previous` 0.04–0.10; `same_request_again` 0.02–0.09.

### Choice `relation` sozinha — cobertura × erro por confiança

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.111 | 27 |
| 0.300 | 0.963 | 0.077 | 26 |
| 0.500 | 0.889 | 0.042 | 24 |
| 0.700 | 0.889 | 0.042 | 24 |
| 0.900 | 0.815 | 0.000 | 22 |

**Os Nouls acrescentam algo à Choice?** A política só pode mandar a `revisar` o que a Choice propôs. Mudou 4 grupo(s): 2 `unclear` recuperado(s), 0 erro(s) caro(s) evitado(s), 1 outro(s) erro(s) trocado(s) por revisão, 1 acerto(s) da Choice mandado(s) a `revisar` sem necessidade (RR-A001, RR-A005, RR-A025, RR-A028).

### Por família (pela `nota` do rotulador; fáceis agrupadas pela relação)

| família | gabarito | n | Jev | só Choice | igualdade | Jaccard | última vale | Jev → revisar | sem chamada (código) | erro caro Jev |
|---|---|---|---|---|---|---|---|---|---|---|
| 'e também' que soma | add | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0 | 0 | 0 |
| 'também' que amplia | add | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0 | 0 | 0 |
| 'também' que não soma | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| asterisco que só corrige grafia | same | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| complemento | add | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0 | 0 | 0 |
| cópia de terceiro | same | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 1 | 0 | 0 |
| grupo de 3 | add/rev | 3 | 1.000 | 1.000 | 0.333 | 0.667 | 0.667 | 0 | 0 | 0 |
| mensagem atrasada | same/unclear | 2 | 1.000 | 1.000 | 0.500 | 0.500 | 0.000 | 1 | 1 | 0 |
| mudança de hora | rev | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0 | 0 | 0 |
| mudança de imóvel | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| negativa | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| negativa da negativa | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| negativa que não revisa | same | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| negativa sem referente | unclear | 1 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1 | 0 | 0 |
| paráfrase | same | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| retry com erro de digitação | same | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 0.000 | 0 | 0 | 0 |
| revisão + pedido novo na mesma mensagem | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| segundo pedido intencional parecido | add | 1 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 1 | 0 | 0 |
| sem conectivo | unclear | 2 | 1.000 | 0.500 | 0.000 | 0.000 | 0.000 | 2 | 0 | 0 |
| terceiro com pedido novo | add | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0 | 0 | 0 |
| fácil: additional_request | add | 2 | 1.000 | 1.000 | 1.000 | 0.500 | 0.000 | 0 | 0 | 0 |
| fácil: revision | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| fácil: same_intent | same | 2 | 1.000 | 1.000 | 0.500 | 1.000 | 0.000 | 0 | 1 | 0 |

### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)

`cobertura_auto` = grupo que não foi a `revisar` (inclui os resolvidos pelo código sem chamada). **Faixa dos Nouls** (a mesma em todos):

| faixa (todos os Nouls) | cobertura_auto | erro_automatico | correções perdidas | efeitos duplicados | unclear automatizado | n_auto |
|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.793 | 0.000 | 0 | 0 | 0 | 23 |
| 0.5–0.5 | 0.828 | 0.000 | 0 | 0 | 0 | 24 |
| 0.4–0.6 | 0.828 | 0.000 | 0 | 0 | 0 | 24 |
| 0.3–0.7 | 0.793 | 0.000 | 0 | 0 | 0 | 23 |
| 0.2–0.8 | 0.724 | 0.000 | 0 | 0 | 0 | 21 |
| 0.1–0.9 | 0.621 | 0.000 | 0 | 0 | 0 | 18 |
| 0.05–0.95 | 0.345 | 0.000 | 0 | 0 | 0 | 10 |

**Piso de confiança da Choice** (o resto como em `perguntas.py`):

| piso de confiança da Choice | cobertura_auto | erro_automatico | correções perdidas | efeitos duplicados | unclear automatizado | n_auto |
|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.793 | 0.000 | 0 | 0 | 0 | 23 |
| 0.000 | 0.793 | 0.000 | 0 | 0 | 0 | 23 |
| 0.300 | 0.793 | 0.000 | 0 | 0 | 0 | 23 |
| 0.500 | 0.793 | 0.000 | 0 | 0 | 0 | 23 |
| 0.700 | 0.793 | 0.000 | 0 | 0 | 0 | 23 |
| 0.900 | 0.793 | 0.000 | 0 | 0 | 0 | 23 |

**Baseline Jaccard — grade de limiares neste conjunto** (os de `perguntas.py` foram escolhidos no ajuste):

| ≥ mesmo | ≥ revisão | acerto_relacao | correções perdidas | efeitos duplicados |
|---|---|---|---|---|
| 0.400 | 0.050 | 0.586 | 0 | 1 |
| 0.500 | 0.050 | 0.586 | 0 | 1 |
| 0.600 | 0.050 | 0.552 | 0 | 1 |
| 0.700 | 0.050 | 0.552 | 0 | 1 |
| 0.800 | 0.050 | 0.552 | 0 | 1 |
| 0.900 | 0.050 | 0.517 | 0 | 1 |

### Custo e latência (medidos na chamada real; do cache também)

| grupos | requisicoes | novas (não cache) | sem chamada (código resolve) | fora da faixa (sem chamada) | falhas operacionais (→ revisar) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_1000_grupos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 29 | 27 | 0 | 2 | 0 | 0 | 216 | 306 | 340 | 2693 | 0.003054 | 0.1053 | jev-1.13.0 |

### Caso a caso

`choice` = opção vencedora da Choice (confiança); `troca`/`soma`/`compl`/`mesma` = Nouls `replaces_previous`, `adds_new_request`, `completes_previous`, `same_request_again`; `s/elo`/`s/alvo`/`ordem` = Nouls de dúvida `no_link_word`, `target_not_said`, `arrived_out_of_order`; `Jev` = relação da política (`unclear` = revisar); `ok` compara com o gabarito; `caro` marca o erro caro; `vig` = `acao_vigente` derivada bate com o gabarito; `=`/`J`/`últ` = baselines igualdade, Jaccard e última vale; `—` = grupo resolvido pelo código sem chamada, ou falha.

| id | fam | gab | msgs | choice | troca | soma | compl | mesma | s/elo | s/alvo | ordem | Jev | sinal | ok | caro | vig | = | J | últ | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RR-A001 | sem conectivo | unclear | 2 | rev (0.46) | 0.80 | 0.10 | 0.10 | 0.09 | 0.92 | 0.04 | 0.19 | unclear | revisar | ✓ |  | ✓ | add | rev | rev | Noul de dúvida: no_link_word 0.92 |
| RR-A002 | mudança de hora | rev | 2 | rev (0.99) | 0.88 | 0.07 | 0.14 | 0.09 | 0.46 | 0.04 | 0.18 | rev | substituir | ✓ |  | ✓ | add | add | rev | a última corrige, troca ou cancela |
| RR-A003 | negativa que não revisa | same | 2 | same (1.00) | 0.02 | 0.02 | 0.09 | 0.95 | 0.02 | 0.02 | 0.04 | same | colapsar | ✓ |  | ✓ | add | rev | rev | mesmo pedido, nada muda nem se soma |
| RR-A004 | mensagem atrasada | same | 2 | — | — | — | — | — | — | — | — | same | colapsar | ✓ |  | ✓ | same | same | rev | texto idêntico após normalização (código) |
| RR-A005 | cópia de terceiro | same | 2 | same (0.98) | 0.05 | 0.08 | 0.35 | 0.76 | 0.02 | 0.02 | 0.06 | unclear | revisar | ✗ |  | ✗ | add | rev | rev | repetição ou pedido novo/complemento? (0.08/0.35) |
| RR-A006 | asterisco que só corrige grafia | same | 2 | same (0.93) | 0.21 | 0.06 | 0.11 | 0.79 | 0.06 | 0.02 | 0.08 | same | colapsar | ✓ |  | ✓ | add | add | rev | mesmo pedido, nada muda nem se soma |
| RR-A007 | 'também' que não soma | rev | 2 | rev (0.98) | 0.92 | 0.08 | 0.16 | 0.03 | 0.08 | 0.03 | 0.10 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-A008 | paráfrase | same | 2 | same (1.00) | 0.04 | 0.03 | 0.12 | 0.95 | 0.06 | 0.02 | 0.07 | same | colapsar | ✓ |  | ✓ | add | rev | rev | mesmo pedido, nada muda nem se soma |
| RR-A009 | revisão + pedido novo na mesma mensagem | rev | 2 | rev (1.00) | 0.97 | 0.40 | 0.09 | 0.02 | 0.03 | 0.03 | 0.05 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-A010 | sem conectivo | unclear | 2 | unclear (0.72) | 0.84 | 0.07 | 0.06 | 0.03 | 0.94 | 0.03 | 0.14 | unclear | revisar | ✓ |  | ✓ | add | rev | rev | o texto não decide entre corrigir e somar (Choice) |
| RR-A011 | grupo de 3 | add | 3 | add (0.94) | 0.05 | 0.77 | 0.45 | 0.22 | 0.07 | 0.02 | 0.07 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-A012 | fácil: revision | rev | 2 | rev (0.99) | 0.96 | 0.03 | 0.06 | 0.03 | 0.17 | 0.03 | 0.07 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-A013 | fácil: same_intent | same | 2 | — | — | — | — | — | — | — | — | same | colapsar | ✓ |  | ✓ | same | same | rev | texto idêntico após normalização (código) |
| RR-A014 | negativa | rev | 2 | rev (1.00) | 0.98 | 0.02 | 0.07 | 0.02 | 0.03 | 0.03 | 0.05 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-A015 | grupo de 3 | rev | 3 | rev (1.00) | 0.98 | 0.04 | 0.06 | 0.03 | 0.04 | 0.02 | 0.05 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-A016 | negativa da negativa | rev | 2 | rev (1.00) | 0.96 | 0.03 | 0.24 | 0.04 | 0.03 | 0.03 | 0.06 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-A017 | retry com erro de digitação | same | 2 | same (1.00) | 0.04 | 0.02 | 0.10 | 0.96 | 0.06 | 0.01 | 0.05 | same | colapsar | ✓ |  | ✓ | add | same | rev | mesmo pedido, nada muda nem se soma |
| RR-A018 | terceiro com pedido novo | add | 2 | add (1.00) | 0.14 | 0.91 | 0.30 | 0.02 | 0.09 | 0.03 | 0.05 | add | somar | ✓ |  | ✓ | add | add | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-A019 | complemento | add | 2 | add (0.96) | 0.08 | 0.05 | 0.92 | 0.08 | 0.25 | 0.02 | 0.05 | add | somar | ✓ |  | ✓ | add | add | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-A020 | fácil: additional_request | add | 2 | add (0.98) | 0.05 | 0.90 | 0.19 | 0.02 | 0.04 | 0.02 | 0.06 | add | somar | ✓ |  | ✓ | add | add | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-A021 | fácil: additional_request | add | 2 | add (1.00) | 0.04 | 0.95 | 0.44 | 0.02 | 0.04 | 0.02 | 0.05 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-A022 | 'e também' que soma | add | 2 | add (1.00) | 0.05 | 0.97 | 0.40 | 0.02 | 0.06 | 0.02 | 0.05 | add | somar | ✓ |  | ✓ | add | add | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-A023 | fácil: same_intent | same | 3 | same (1.00) | 0.04 | 0.04 | 0.10 | 0.95 | 0.04 | 0.02 | 0.07 | same | colapsar | ✓ |  | ✓ | add | same | rev | mesmo pedido, nada muda nem se soma |
| RR-A024 | grupo de 3 | rev | 3 | rev (1.00) | 0.91 | 0.03 | 0.08 | 0.16 | 0.03 | 0.09 | 0.11 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-A025 | segundo pedido intencional parecido | add | 2 | rev (0.29) | 0.74 | 0.39 | 0.09 | 0.02 | 0.87 | 0.03 | 0.18 | unclear | revisar | ✗ |  | ✓ | add | same | rev | Noul de dúvida: no_link_word 0.87 |
| RR-A026 | mensagem atrasada | unclear | 2 | unclear (0.38) | 0.86 | 0.06 | 0.04 | 0.02 | 0.93 | 0.05 | 0.93 | unclear | revisar | ✓ |  | ✓ | add | rev | rev | o texto não decide entre corrigir e somar (Choice) |
| RR-A027 | mudança de imóvel | rev | 2 | rev (1.00) | 0.97 | 0.04 | 0.11 | 0.14 | 0.08 | 0.03 | 0.04 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-A028 | negativa sem referente | unclear | 3 | rev (0.80) | 0.96 | 0.04 | 0.04 | 0.04 | 0.03 | 0.95 | 0.07 | unclear | revisar | ✓ |  | ✓ | add | add | rev | Noul de dúvida: target_not_said 0.95 |
| RR-A029 | 'também' que amplia | add | 2 | add (0.98) | 0.08 | 0.18 | 0.94 | 0.10 | 0.07 | 0.03 | 0.08 | add | somar | ✓ |  | ✓ | add | add | rev | pedido novo ou complemento; o anterior continua de pé |

## Conjunto `teste` — 58 grupos (arquivo versão 2026-10-01, autor fable); 16 `same_intent`, 18 `revision`, 17 `additional_request`, 7 `unclear`; 42 difíceis; 8 grupos de 3

### Relação (4 classes) — métrica principal, baselines × sempre revisa × Jev nos mesmos grupos

Sinal de reconciliação: `same_intent` → colapsar · `revision` → substituir · `additional_request` → somar · `unclear` → revisar. **CORREÇÃO PERDIDA** = gabarito `revision` que saiu `same_intent` (colapsar apaga a correção). **EFEITO DUPLICADO** = gabarito `same_intent` que saiu `additional_request` (somar executa duas vezes). `igualdade normalizada` = textos iguais ⇒ repetição, senão executa tudo; `Jaccard de palavras` = ≥ 0.5 ⇒ repetição, ≥ 0.05 ⇒ revisão, abaixo ⇒ pedido novo (limiares da grade do ajuste); `a última sempre vale` = sempre revisão; `sempre revisa` = zero erro caro, 100% dos grupos a humano; `só Choice` = a opção vencedora, sem Nouls nem piso; `Jev (política)` = Choice confirmada pelos Nouls, dúvida → revisar. `acao_vigente` é derivada da relação prevista. As duas variantes do Jev leem a MESMA resposta.

| variante | n | acerto_relacao | CORREÇÃO PERDIDA (revision → colapsar) | EFEITO DUPLICADO (same_intent → somar) | acao_vigente certa | unclear → revisar | revisou sem necessidade |
|---|---|---|---|---|---|---|---|
| baseline: igualdade normalizada | 58 | 0.345 | 0/18 | 13/16 | 27/58 | 0/7 | 0/51 |
| baseline: Jaccard de palavras | 58 | 0.448 | 0/18 | 2/16 | 28/58 | 0/7 | 0/51 |
| baseline: a última sempre vale | 58 | 0.310 | 0/18 | 0/16 | 18/58 | 0/7 | 0/51 |
| sempre revisa | 58 | 0.121 | 0/18 | 0/16 | 24/58 | 7/7 | 51/51 |
| só Choice | 58 | 0.931 | 0/18 | 0/16 | 54/58 | 4/7 | 0/51 |
| Jev (política) | 58 | 0.862 | 0/18 | 0/16 | 54/58 | 7/7 | 8/51 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 correção perdida | 0/18 | ≤ 0 | ✓ |
| 2 efeito duplicado | 0/16 | ≤ 1 | ✓ |
| 3 acerto da relação | 0.862 (melhor baseline: Jaccard de palavras 0.448) | ≥ 0.598 | ✓ |
| secundário: unclear → revisar | 7/7 (1.000) | ≥ 0.7 | ✓ |
| secundário: revisou sem necessidade | 8/51 (0.157) | ≤ 0.2 | ✓ |
| secundário: acao_vigente certa | 54/58 (0.931) | ≥ 0.8 | ✓ |

**Matriz de confusão — Jev (política)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 13 | 0 | 0 | 3 |
| revision | 0 | 17 | 0 | 1 |
| additional_request | 0 | 0 | 13 | 4 |
| unclear | 0 | 0 | 0 | 7 |

**Matriz de confusão — só Choice** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 16 | 0 | 0 | 0 |
| revision | 0 | 18 | 0 | 0 |
| additional_request | 1 | 0 | 16 | 0 |
| unclear | 0 | 3 | 0 | 4 |

**Matriz de confusão — baseline: igualdade normalizada** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 3 | 0 | 13 | 0 |
| revision | 0 | 0 | 18 | 0 |
| additional_request | 0 | 0 | 17 | 0 |
| unclear | 0 | 0 | 7 | 0 |

**Matriz de confusão — baseline: Jaccard de palavras** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 8 | 6 | 2 | 0 |
| revision | 0 | 13 | 5 | 0 |
| additional_request | 0 | 12 | 5 | 0 |
| unclear | 3 | 2 | 2 | 0 |

**Matriz de confusão — baseline: a última sempre vale** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | same_intent | revision | additional_request | unclear |
|---|---|---|---|---|
| same_intent | 0 | 16 | 0 | 0 |
| revision | 0 | 18 | 0 | 0 |
| additional_request | 0 | 17 | 0 | 0 |
| unclear | 0 | 7 | 0 | 0 |

**Erros caros, grupo a grupo** (todas as variantes)

| id | variante | erro | família |
|---|---|---|---|
| RR-T004 | baseline: igualdade normalizada | EFEITO DUPLICADO | paráfrase |
| RR-T005 | baseline: igualdade normalizada | EFEITO DUPLICADO | cópia de terceiro |
| RR-T007 | baseline: igualdade normalizada | EFEITO DUPLICADO | negativa que não revisa |
| RR-T020 | baseline: igualdade normalizada | EFEITO DUPLICADO | fácil: same_intent |
| RR-T035 | baseline: igualdade normalizada | EFEITO DUPLICADO | retry com erro de digitação |
| RR-T036 | baseline: igualdade normalizada | EFEITO DUPLICADO | mensagem atrasada |
| RR-T041 | baseline: igualdade normalizada | EFEITO DUPLICADO | negativa que não revisa |
| RR-T045 | baseline: igualdade normalizada | EFEITO DUPLICADO | paráfrase |
| RR-T049 | baseline: igualdade normalizada | EFEITO DUPLICADO | retry com erro de digitação |
| RR-T050 | baseline: igualdade normalizada | EFEITO DUPLICADO | asterisco que só corrige grafia |
| RR-T052 | baseline: igualdade normalizada | EFEITO DUPLICADO | cópia de terceiro |
| RR-T056 | baseline: igualdade normalizada | EFEITO DUPLICADO | fácil: same_intent |
| RR-T057 | baseline: igualdade normalizada | EFEITO DUPLICADO | fácil: same_intent |
| RR-T050 | baseline: Jaccard de palavras | EFEITO DUPLICADO | asterisco que só corrige grafia |
| RR-T052 | baseline: Jaccard de palavras | EFEITO DUPLICADO | cópia de terceiro |

### O que o código resolveu sem o Jev

Texto idêntico após normalização em todas as mensagens ⇒ `same_intent` sem chamada: 3 grupos, 3/3 com gabarito `same_intent` (RR-T002, RR-T006, RR-T047). Grupos em que o código tirou uma cópia adjacente e mandou ao Jev só as mensagens distintas: 3 (RR-T016, RR-T038, RR-T056).

### Nouls contra a relação do gabarito — 55 grupos que foram ao Jev

Cada Noul é o sim/não de UMA relação (`replaces_previous` ↔ `revision`; `soma` = o maior entre `adds_new_request` e `completes_previous` ↔ `additional_request`; `same_request_again` ↔ `same_intent`); grupos `unclear` ficam fora (o gabarito não diz sim nem não). Acerto com corte 0,5; `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela.

| noul | positivos | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| replaces_previous | 18 | 0.938 | 0.3–0.7 | 0.958 | 0.978 | 2 | 48 | 0.034 |
| soma | 17 | 0.938 | 0.3–0.7 | 0.896 | 0.977 | 5 | 48 | 0.053 |
| same_request_again | 13 | 1.000 | 0.3–0.7 | 0.979 | 1.000 | 1 | 48 | 0.007 |

**Nouls de dúvida** (o lado absoluto da opção `unclear`; qualquer um ≥ `sim` → revisar): mín–máx dentro e fora dos grupos `unclear`, e quantos passam do `sim`.

| noul | unclear: mín–máx | unclear ≥ sim | demais: mín–máx | demais ≥ sim | faixa |
|---|---|---|---|---|---|
| no_link_word | 0.03–0.95 | 6/7 | 0.02–0.53 | 0/48 | 0.3–0.7 |
| target_not_said | 0.03–0.95 | 1/7 | 0.01–0.25 | 0/48 | 0.3–0.7 |
| arrived_out_of_order | 0.06–0.80 | 1/7 | 0.04–0.23 | 0/48 | 0.3–0.7 |

Os Nouls de relação nos grupos `unclear`: `replaces_previous` 0.54–0.96; `adds_new_request` 0.03–0.30; `completes_previous` 0.03–0.12; `same_request_again` 0.02–0.06.

### Choice `relation` sozinha — cobertura × erro por confiança

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.073 | 55 |
| 0.300 | 1.000 | 0.073 | 55 |
| 0.500 | 0.927 | 0.039 | 51 |
| 0.700 | 0.855 | 0.000 | 47 |
| 0.900 | 0.745 | 0.000 | 41 |

**Os Nouls acrescentam algo à Choice?** A política só pode mandar a `revisar` o que a Choice propôs. Mudou 11 grupo(s): 3 `unclear` recuperado(s), 0 erro(s) caro(s) evitado(s), 1 outro(s) erro(s) trocado(s) por revisão, 7 acerto(s) da Choice mandado(s) a `revisar` sem necessidade (RR-T004, RR-T024, RR-T025, RR-T029, RR-T034, RR-T037, RR-T043, RR-T049, RR-T051, RR-T052, RR-T053).

### Por família (pela `nota` do rotulador; fáceis agrupadas pela relação)

| família | gabarito | n | Jev | só Choice | igualdade | Jaccard | última vale | Jev → revisar | sem chamada (código) | erro caro Jev |
|---|---|---|---|---|---|---|---|---|---|---|
| 'e também' que soma | add | 1 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| 'também' que amplia | add | 1 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 1 | 0 | 0 |
| 'também' que não soma | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| asterisco que só corrige grafia | same | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| complemento | add | 3 | 0.667 | 0.667 | 1.000 | 0.667 | 0.000 | 1 | 0 | 0 |
| cópia de terceiro | same | 2 | 0.500 | 1.000 | 0.000 | 0.000 | 0.000 | 1 | 0 | 0 |
| grupo de 3 | add/rev | 4 | 1.000 | 1.000 | 0.250 | 0.750 | 0.750 | 0 | 0 | 0 |
| m1 já é uma remarcação | add | 1 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| mensagem atrasada | same/unclear | 3 | 1.000 | 1.000 | 0.333 | 0.667 | 0.000 | 1 | 1 | 0 |
| mudança de atributo que não é dia nem hora | rev | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0 | 0 | 0 |
| mudança de dia | rev | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0 | 0 | 0 |
| mudança de hora condicional | rev | 1 | 0.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| mudança de imóvel | rev | 2 | 1.000 | 1.000 | 0.000 | 0.500 | 1.000 | 0 | 0 | 0 |
| negativa | rev | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0 | 0 | 0 |
| negativa da negativa | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| negativa que não revisa | same | 2 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| negativa sem referente | unclear | 1 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1 | 0 | 0 |
| paráfrase | same | 2 | 0.500 | 1.000 | 0.000 | 0.500 | 0.000 | 1 | 0 | 0 |
| retry com erro de digitação | same/unclear | 3 | 0.667 | 0.667 | 0.000 | 0.667 | 0.000 | 2 | 0 | 0 |
| revisão + pedido novo na mesma mensagem | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| revisão parcial | rev | 1 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0 | 0 | 0 |
| segundo pedido intencional parecido | add | 3 | 0.667 | 1.000 | 1.000 | 0.333 | 0.000 | 1 | 0 | 0 |
| sem conectivo | unclear | 3 | 1.000 | 0.667 | 0.000 | 0.000 | 0.000 | 3 | 0 | 0 |
| terceiro ambíguo | unclear | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 1 | 0 | 0 |
| terceiro com pedido novo | add | 1 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| fácil: additional_request | add | 6 | 0.833 | 1.000 | 1.000 | 0.333 | 0.000 | 1 | 0 | 0 |
| fácil: revision | rev | 5 | 1.000 | 1.000 | 0.000 | 0.800 | 1.000 | 0 | 0 | 0 |
| fácil: same_intent | same | 5 | 1.000 | 1.000 | 0.400 | 0.600 | 0.000 | 0 | 2 | 0 |

### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)

`cobertura_auto` = grupo que não foi a `revisar` (inclui os resolvidos pelo código sem chamada). **Faixa dos Nouls** (a mesma em todos):

| faixa (todos os Nouls) | cobertura_auto | erro_automatico | correções perdidas | efeitos duplicados | unclear automatizado | n_auto |
|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.741 | 0.000 | 0 | 0 | 0 | 43 |
| 0.5–0.5 | 0.741 | 0.000 | 0 | 0 | 0 | 43 |
| 0.4–0.6 | 0.759 | 0.000 | 0 | 0 | 0 | 44 |
| 0.3–0.7 | 0.741 | 0.000 | 0 | 0 | 0 | 43 |
| 0.2–0.8 | 0.655 | 0.000 | 0 | 0 | 0 | 38 |
| 0.1–0.9 | 0.500 | 0.000 | 0 | 0 | 0 | 29 |
| 0.05–0.95 | 0.276 | 0.000 | 0 | 0 | 0 | 16 |

**Piso de confiança da Choice** (o resto como em `perguntas.py`):

| piso de confiança da Choice | cobertura_auto | erro_automatico | correções perdidas | efeitos duplicados | unclear automatizado | n_auto |
|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.741 | 0.000 | 0 | 0 | 0 | 43 |
| 0.000 | 0.759 | 0.000 | 0 | 0 | 0 | 44 |
| 0.300 | 0.759 | 0.000 | 0 | 0 | 0 | 44 |
| 0.500 | 0.741 | 0.000 | 0 | 0 | 0 | 43 |
| 0.700 | 0.741 | 0.000 | 0 | 0 | 0 | 43 |
| 0.900 | 0.690 | 0.000 | 0 | 0 | 0 | 40 |

**Baseline Jaccard — grade de limiares neste conjunto** (os de `perguntas.py` foram escolhidos no ajuste):

| ≥ mesmo | ≥ revisão | acerto_relacao | correções perdidas | efeitos duplicados |
|---|---|---|---|---|
| 0.400 | 0.100 | 0.483 | 0 | 2 |
| 0.500 | 0.100 | 0.483 | 0 | 2 |
| 0.600 | 0.100 | 0.483 | 0 | 2 |
| 0.400 | 0.050 | 0.448 | 0 | 2 |
| 0.500 | 0.050 | 0.448 | 0 | 2 |
| 0.600 | 0.050 | 0.448 | 0 | 2 |

### Custo e latência (medidos na chamada real; do cache também)

| grupos | requisicoes | novas (não cache) | sem chamada (código resolve) | fora da faixa (sem chamada) | falhas operacionais (→ revisar) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_1000_grupos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 58 | 55 | 0 | 3 | 0 | 0 | 440 | 270 | 355 | 2694 | 0.006223 | 0.1073 | jev-1.13.0 |

### Caso a caso

`choice` = opção vencedora da Choice (confiança); `troca`/`soma`/`compl`/`mesma` = Nouls `replaces_previous`, `adds_new_request`, `completes_previous`, `same_request_again`; `s/elo`/`s/alvo`/`ordem` = Nouls de dúvida `no_link_word`, `target_not_said`, `arrived_out_of_order`; `Jev` = relação da política (`unclear` = revisar); `ok` compara com o gabarito; `caro` marca o erro caro; `vig` = `acao_vigente` derivada bate com o gabarito; `=`/`J`/`últ` = baselines igualdade, Jaccard e última vale; `—` = grupo resolvido pelo código sem chamada, ou falha.

| id | fam | gab | msgs | choice | troca | soma | compl | mesma | s/elo | s/alvo | ordem | Jev | sinal | ok | caro | vig | = | J | últ | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RR-T001 | fácil: revision | rev | 2 | rev (1.00) | 0.97 | 0.05 | 0.08 | 0.02 | 0.05 | 0.03 | 0.06 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T002 | fácil: same_intent | same | 2 | — | — | — | — | — | — | — | — | same | colapsar | ✓ |  | ✓ | same | same | rev | texto idêntico após normalização (código) |
| RR-T003 | fácil: revision | rev | 2 | rev (1.00) | 0.96 | 0.04 | 0.07 | 0.04 | 0.06 | 0.03 | 0.06 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T004 | paráfrase | same | 2 | same (0.98) | 0.09 | 0.03 | 0.54 | 0.85 | 0.16 | 0.02 | 0.07 | unclear | revisar | ✗ |  | ✗ | add | same | rev | repetição ou pedido novo/complemento? (0.03/0.54) |
| RR-T005 | cópia de terceiro | same | 2 | same (1.00) | 0.02 | 0.03 | 0.08 | 0.96 | 0.03 | 0.02 | 0.04 | same | colapsar | ✓ |  | ✓ | add | rev | rev | mesmo pedido, nada muda nem se soma |
| RR-T006 | fácil: same_intent | same | 2 | — | — | — | — | — | — | — | — | same | colapsar | ✓ |  | ✓ | same | same | rev | texto idêntico após normalização (código) |
| RR-T007 | negativa que não revisa | same | 2 | same (0.99) | 0.03 | 0.04 | 0.13 | 0.93 | 0.02 | 0.02 | 0.07 | same | colapsar | ✓ |  | ✓ | add | rev | rev | mesmo pedido, nada muda nem se soma |
| RR-T008 | fácil: additional_request | add | 2 | add (1.00) | 0.03 | 0.90 | 0.75 | 0.02 | 0.05 | 0.02 | 0.05 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T009 | fácil: revision | rev | 2 | rev (0.98) | 0.91 | 0.05 | 0.12 | 0.05 | 0.21 | 0.03 | 0.06 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T010 | fácil: additional_request | add | 2 | add (0.99) | 0.03 | 0.78 | 0.25 | 0.02 | 0.05 | 0.02 | 0.05 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T011 | 'e também' que soma | add | 2 | add (1.00) | 0.07 | 0.97 | 0.29 | 0.02 | 0.06 | 0.02 | 0.05 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T012 | sem conectivo | unclear | 2 | unclear (0.52) | 0.76 | 0.10 | 0.05 | 0.06 | 0.94 | 0.03 | 0.21 | unclear | revisar | ✓ |  | ✓ | add | same | rev | o texto não decide entre corrigir e somar (Choice) |
| RR-T013 | fácil: additional_request | add | 2 | add (0.99) | 0.08 | 0.92 | 0.60 | 0.03 | 0.07 | 0.02 | 0.07 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T014 | revisão parcial | rev | 2 | rev (0.97) | 0.94 | 0.05 | 0.04 | 0.03 | 0.53 | 0.25 | 0.10 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T015 | fácil: revision | rev | 2 | rev (1.00) | 0.97 | 0.02 | 0.03 | 0.02 | 0.02 | 0.03 | 0.07 | rev | substituir | ✓ |  | ✓ | add | add | rev | a última corrige, troca ou cancela |
| RR-T016 | grupo de 3 | rev | 3 | rev (1.00) | 0.96 | 0.04 | 0.06 | 0.05 | 0.09 | 0.02 | 0.06 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T017 | mudança de dia | rev | 2 | rev (0.72) | 0.87 | 0.09 | 0.07 | 0.04 | 0.43 | 0.04 | 0.22 | rev | substituir | ✓ |  | ✓ | add | add | rev | a última corrige, troca ou cancela |
| RR-T018 | 'também' que não soma | rev | 2 | rev (1.00) | 0.97 | 0.06 | 0.12 | 0.03 | 0.07 | 0.04 | 0.11 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T019 | grupo de 3 | rev | 3 | rev (1.00) | 0.96 | 0.03 | 0.05 | 0.14 | 0.03 | 0.07 | 0.11 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T020 | fácil: same_intent | same | 2 | same (1.00) | 0.03 | 0.02 | 0.05 | 0.97 | 0.03 | 0.02 | 0.07 | same | colapsar | ✓ |  | ✓ | add | rev | rev | mesmo pedido, nada muda nem se soma |
| RR-T021 | negativa da negativa | rev | 2 | rev (1.00) | 0.80 | 0.03 | 0.13 | 0.04 | 0.02 | 0.02 | 0.10 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T022 | segundo pedido intencional parecido | add | 2 | add (0.99) | 0.08 | 0.76 | 0.35 | 0.02 | 0.07 | 0.03 | 0.07 | add | somar | ✓ |  | ✓ | add | add | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T023 | fácil: revision | rev | 2 | rev (1.00) | 0.97 | 0.04 | 0.06 | 0.02 | 0.04 | 0.03 | 0.07 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T024 | mudança de hora condicional | rev | 2 | rev (0.49) | 0.23 | 0.11 | 0.89 | 0.15 | 0.17 | 0.02 | 0.07 | unclear | revisar | ✗ |  | ✗ | add | rev | rev | confiança da Choice baixa (0.49, revision) |
| RR-T025 | segundo pedido intencional parecido | add | 2 | add (0.90) | 0.61 | 0.64 | 0.25 | 0.02 | 0.05 | 0.03 | 0.05 | unclear | revisar | ✗ |  | ✓ | add | rev | rev | Choice diz pedido adicional, Nouls não confirmam (0.64/0.25) |
| RR-T026 | mudança de atributo que não é dia nem hora | rev | 2 | rev (1.00) | 0.96 | 0.07 | 0.20 | 0.02 | 0.05 | 0.04 | 0.07 | rev | substituir | ✓ |  | ✓ | add | add | rev | a última corrige, troca ou cancela |
| RR-T027 | negativa | rev | 2 | rev (1.00) | 0.97 | 0.07 | 0.09 | 0.02 | 0.02 | 0.04 | 0.04 | rev | substituir | ✓ |  | ✓ | add | add | rev | a última corrige, troca ou cancela |
| RR-T028 | segundo pedido intencional parecido | add | 2 | add (0.92) | 0.24 | 0.85 | 0.21 | 0.03 | 0.12 | 0.03 | 0.07 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T029 | negativa sem referente | unclear | 3 | rev (0.59) | 0.96 | 0.03 | 0.03 | 0.02 | 0.03 | 0.95 | 0.06 | unclear | revisar | ✓ |  | ✓ | add | add | rev | Noul de dúvida: target_not_said 0.95 |
| RR-T030 | fácil: additional_request | add | 3 | add (1.00) | 0.04 | 0.93 | 0.43 | 0.04 | 0.09 | 0.02 | 0.05 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T031 | sem conectivo | unclear | 2 | unclear (0.68) | 0.82 | 0.06 | 0.06 | 0.03 | 0.94 | 0.03 | 0.15 | unclear | revisar | ✓ |  | ✓ | add | rev | rev | o texto não decide entre corrigir e somar (Choice) |
| RR-T032 | complemento | add | 2 | add (0.97) | 0.11 | 0.48 | 0.92 | 0.04 | 0.07 | 0.02 | 0.05 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T033 | mensagem atrasada | unclear | 2 | unclear (0.76) | 0.54 | 0.30 | 0.07 | 0.02 | 0.87 | 0.03 | 0.80 | unclear | revisar | ✓ |  | ✓ | add | add | rev | o texto não decide entre corrigir e somar (Choice) |
| RR-T034 | 'também' que amplia | add | 2 | add (0.45) | 0.24 | 0.21 | 0.72 | 0.05 | 0.07 | 0.04 | 0.11 | unclear | revisar | ✗ |  | ✓ | add | rev | rev | confiança da Choice baixa (0.45, additional_request) |
| RR-T035 | retry com erro de digitação | same | 2 | same (1.00) | 0.03 | 0.02 | 0.03 | 0.96 | 0.03 | 0.02 | 0.08 | same | colapsar | ✓ |  | ✓ | add | same | rev | mesmo pedido, nada muda nem se soma |
| RR-T036 | mensagem atrasada | same | 2 | same (1.00) | 0.02 | 0.02 | 0.10 | 0.95 | 0.03 | 0.01 | 0.06 | same | colapsar | ✓ |  | ✓ | add | same | rev | mesmo pedido, nada muda nem se soma |
| RR-T037 | sem conectivo | unclear | 2 | rev (0.51) | 0.81 | 0.06 | 0.10 | 0.04 | 0.94 | 0.04 | 0.17 | unclear | revisar | ✓ |  | ✓ | add | same | rev | Noul de dúvida: no_link_word 0.94 |
| RR-T038 | grupo de 3 | add | 3 | add (0.95) | 0.08 | 0.89 | 0.25 | 0.09 | 0.07 | 0.03 | 0.08 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T039 | m1 já é uma remarcação | add | 2 | add (0.93) | 0.05 | 0.86 | 0.22 | 0.02 | 0.04 | 0.02 | 0.10 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T040 | terceiro com pedido novo | add | 2 | add (1.00) | 0.08 | 0.93 | 0.17 | 0.02 | 0.14 | 0.03 | 0.06 | add | somar | ✓ |  | ✓ | add | rev | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T041 | negativa que não revisa | same | 2 | same (1.00) | 0.02 | 0.03 | 0.05 | 0.97 | 0.03 | 0.01 | 0.05 | same | colapsar | ✓ |  | ✓ | add | rev | rev | mesmo pedido, nada muda nem se soma |
| RR-T042 | grupo de 3 | rev | 3 | rev (0.95) | 0.94 | 0.04 | 0.09 | 0.06 | 0.15 | 0.21 | 0.23 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T043 | fácil: additional_request | add | 2 | add (0.85) | 0.04 | 0.37 | 0.39 | 0.07 | 0.05 | 0.02 | 0.05 | unclear | revisar | ✗ |  | ✓ | add | add | rev | Choice diz pedido adicional, Nouls não confirmam (0.37/0.39) |
| RR-T044 | complemento | add | 2 | add (0.87) | 0.20 | 0.08 | 0.94 | 0.05 | 0.29 | 0.02 | 0.07 | add | somar | ✓ |  | ✓ | add | add | rev | pedido novo ou complemento; o anterior continua de pé |
| RR-T045 | paráfrase | same | 2 | same (0.99) | 0.05 | 0.03 | 0.16 | 0.95 | 0.06 | 0.02 | 0.08 | same | colapsar | ✓ |  | ✓ | add | rev | rev | mesmo pedido, nada muda nem se soma |
| RR-T046 | mudança de imóvel | rev | 2 | rev (1.00) | 0.97 | 0.05 | 0.10 | 0.03 | 0.03 | 0.02 | 0.06 | rev | substituir | ✓ |  | ✓ | add | add | rev | a última corrige, troca ou cancela |
| RR-T047 | mensagem atrasada | same | 2 | — | — | — | — | — | — | — | — | same | colapsar | ✓ |  | ✓ | same | same | rev | texto idêntico após normalização (código) |
| RR-T048 | revisão + pedido novo na mesma mensagem | rev | 2 | rev (1.00) | 0.94 | 0.40 | 0.06 | 0.02 | 0.09 | 0.03 | 0.06 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T049 | retry com erro de digitação | same | 2 | same (0.99) | 0.05 | 0.03 | 0.37 | 0.94 | 0.07 | 0.02 | 0.06 | unclear | revisar | ✗ |  | ✗ | add | same | rev | repetição ou pedido novo/complemento? (0.03/0.37) |
| RR-T050 | asterisco que só corrige grafia | same | 2 | same (0.92) | 0.17 | 0.07 | 0.11 | 0.77 | 0.06 | 0.02 | 0.09 | same | colapsar | ✓ |  | ✓ | add | add | rev | mesmo pedido, nada muda nem se soma |
| RR-T051 | retry com erro de digitação | unclear | 2 | rev (0.43) | 0.83 | 0.06 | 0.05 | 0.04 | 0.95 | 0.04 | 0.17 | unclear | revisar | ✓ |  | ✓ | add | same | rev | Noul de dúvida: no_link_word 0.95 |
| RR-T052 | cópia de terceiro | same | 2 | same (0.91) | 0.53 | 0.05 | 0.24 | 0.67 | 0.03 | 0.05 | 0.09 | unclear | revisar | ✗ |  | ✗ | add | add | rev | repetição ou revisão? (0.53) — colapsar apagaria a correção |
| RR-T053 | complemento | add | 2 | same (0.31) | 0.03 | 0.03 | 0.89 | 0.07 | 0.03 | 0.02 | 0.05 | unclear | revisar | ✗ |  | ✓ | add | add | rev | confiança da Choice baixa (0.31, same_intent) |
| RR-T054 | mudança de imóvel | rev | 2 | rev (0.99) | 0.94 | 0.04 | 0.14 | 0.17 | 0.03 | 0.02 | 0.04 | rev | substituir | ✓ |  | ✓ | add | rev | rev | a última corrige, troca ou cancela |
| RR-T055 | terceiro ambíguo | unclear | 2 | unclear (0.71) | 0.79 | 0.11 | 0.12 | 0.04 | 0.72 | 0.05 | 0.11 | unclear | revisar | ✓ |  | ✓ | add | rev | rev | o texto não decide entre corrigir e somar (Choice) |
| RR-T056 | fácil: same_intent | same | 3 | same (0.99) | 0.14 | 0.02 | 0.06 | 0.96 | 0.04 | 0.02 | 0.06 | same | colapsar | ✓ |  | ✓ | add | same | rev | mesmo pedido, nada muda nem se soma |
| RR-T057 | fácil: same_intent | same | 3 | same (1.00) | 0.03 | 0.03 | 0.08 | 0.96 | 0.06 | 0.02 | 0.06 | same | colapsar | ✓ |  | ✓ | add | rev | rev | mesmo pedido, nada muda nem se soma |
| RR-T058 | fácil: additional_request | add | 2 | add (0.72) | 0.09 | 0.72 | 0.16 | 0.02 | 0.29 | 0.02 | 0.07 | add | somar | ✓ |  | ✓ | add | add | rev | pedido novo ou complemento; o anterior continua de pé |
