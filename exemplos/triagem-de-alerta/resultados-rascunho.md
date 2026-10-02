# Rascunho — triagem-de-alerta (encanamento)

## Conjunto `rascunho` — 5 alertas (arquivo versão 2026-10-01, autor fable); 0 difíceis; gabarito: auto_close 2 · notify_owner 1 · queue_tier2 1 · contain_now 1

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Ação (4 classes) — baseline × sempre fila × Choice única × Jev (Nouls + política) nos mesmos casos

**Erros caros** (pelo gabarito): **E1** = gabarito `contain_now` que saiu `auto_close` ou `notify_owner` (ataque fechado ou só avisado); **E2** = `auto_close` em alerta cujo indício no gabarito não é falso (verdadeiro ou nulo); **E3** = `contain_now` em alerta com atividade esperada no gabarito. `contenção perdida` = gabarito `contain_now` que foi à fila (não é erro caro: um analista vê, mas ninguém age na hora). `sempre fila` = o custo de evitar todo erro caro: tudo a humano. **Variante principal (declarada antes do teste): Jev (Nouls + política)**; a Choice única é o vencedor cru da pergunta `action`, na mesma requisição, sem política nem veto do código.

| variante | n | acerto_acao | E1 ataque sem contenção nem fila | E2 fechou com indício | E3 conteve atividade esperada | contenção perdida (→ fila) | contenção indevida (qualquer) | auto_close indevido (qualquer) | indício → só dono | indício nulo → fila |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (regras de código) | 5 | 1.000 | 0/1 | 0/2 | 0/2 | 0/1 | 0/4 | 0/3 | 0/2 | 0/0 |
| sempre fila | 5 | 0.200 | 0/1 | 0/2 | 0/2 | 1/1 | 0/4 | 0/3 | 0/2 | 0/0 |
| Choice única (informativa) | 5 | 1.000 | 0/1 | 0/2 | 0/2 | 0/1 | 0/4 | 0/3 | 0/2 | 0/0 |
| Jev (Nouls + política) | 5 | 1.000 | 0/1 | 0/2 | 0/2 | 0/1 | 0/4 | 0/3 | 0/2 | 0/0 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

_(critério de aceite ainda não fixado)_

**Matriz de confusão — Jev (Nouls + política)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | auto_close | notify_owner | queue_tier2 | contain_now |
|---|---|---|---|---|
| auto_close | 2 | 0 | 0 | 0 |
| notify_owner | 0 | 1 | 0 | 0 |
| queue_tier2 | 0 | 0 | 1 | 0 |
| contain_now | 0 | 0 | 0 | 1 |

**Matriz de confusão — baseline (regras de código)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | auto_close | notify_owner | queue_tier2 | contain_now |
|---|---|---|---|---|
| auto_close | 2 | 0 | 0 | 0 |
| notify_owner | 0 | 1 | 0 | 0 |
| queue_tier2 | 0 | 0 | 1 | 0 |
| contain_now | 0 | 0 | 0 | 1 |

**Matriz de confusão — Choice única (informativa)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | auto_close | notify_owner | queue_tier2 | contain_now |
|---|---|---|---|---|
| auto_close | 2 | 0 | 0 | 0 |
| notify_owner | 0 | 1 | 0 | 0 |
| queue_tier2 | 0 | 0 | 1 | 0 |
| contain_now | 0 | 0 | 0 | 1 |

### Os quatro sinais — Noul (≥ 0,5) contra o gabarito, faixa atual e Brier

Gabarito `null` fica fora da métrica (a coluna da direita mostra onde o Noul caiu nesses casos). `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela. `baseline` = o mesmo sinal pelas regras de código.

| noul | gabarito | acerto ≥0,5 | baseline | faixa | cobertura | acerto_decididos | revisao | n | brier | nulos no gabarito (valores do Noul) |
|---|---|---|---|---|---|---|---|---|---|---|
| expected_activity | atividade_esperada | 1.000 | 0.800 | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 | 0.008 | — |
| critical_asset | ativo_critico | 1.000 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 | 0.021 | — |
| compromise_indication | indicio_de_comprometimento | 1.000 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 | 0.006 | — |
| ongoing | em_andamento | 1.000 | 0.800 | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 | 0.009 | — |

**`atividade_esperada` depois do código** (faixa + contexto vazio + veto de horário; dúvida conta como erro): 1.000 (n = 5)

**Urgência do aviso ao dono** (acordar = ativo crítico E em andamento; entre os `notify_owner` acertados): Jev 1/1 · baseline 1/1

### Fatos do código (hora do alerta × faixa de horário escrita no contexto)

| alertas com faixa de horário no contexto | veto de horário disparou | veto em atividade esperada no gabarito (veto errado) | veto que mudou a decisão (Noul dizia esperado) | contexto vazio |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | 2 |

### Por família difícil (pela `nota` do rotulador)

| família | n | Jev | baseline | Choice única | erros caros Jev | erros caros baseline | erros caros Choice |
|---|---|---|---|---|---|---|---|
| fácil / outros | 5 | 1.000 | 1.000 | 1.000 | — | — | — |

### Cobertura × erro por faixa

**Política inteira** (mesmas respostas, outra faixa nos quatro Nouls; informativo no teste)

| faixa (4 Nouls) | acerto_acao | E1 | E2 | E3 | contenção perdida | contenção indevida | dúvida de indício → fila | n |
|---|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 1.000 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| 0.5–0.5 | 1.000 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| 0.4–0.6 | 1.000 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| 0.3–0.7 | 1.000 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| 0.2–0.8 | 0.800 | 0 | 0 | 0 | 1 | 0 | 0 | 5 |
| 0.1–0.9 | 0.600 | 0 | 0 | 0 | 1 | 0 | 1 | 5 |

**Cada Noul sozinho** (cobertura = decidido fora da faixa; acerto entre os decididos)

| noul | faixa | cobertura | acerto_decididos | revisao | n |
|---|---|---|---|---|---|
| expected_activity | 0.5–0.5 | 1.000 | 1.000 | 0 | 5 |
| expected_activity | 0.4–0.6 | 1.000 | 1.000 | 0 | 5 |
| expected_activity | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 |
| expected_activity | 0.2–0.8 | 1.000 | 1.000 | 0 | 5 |
| expected_activity | 0.1–0.9 | 0.800 | 1.000 | 1 | 5 |
| critical_asset | 0.5–0.5 | 1.000 | 1.000 | 0 | 5 |
| critical_asset | 0.4–0.6 | 1.000 | 1.000 | 0 | 5 |
| critical_asset | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 |
| critical_asset | 0.2–0.8 | 0.800 | 1.000 | 1 | 5 |
| critical_asset | 0.1–0.9 | 0.600 | 1.000 | 2 | 5 |
| compromise_indication | 0.5–0.5 | 1.000 | 1.000 | 0 | 5 |
| compromise_indication | 0.4–0.6 | 1.000 | 1.000 | 0 | 5 |
| compromise_indication | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 |
| compromise_indication | 0.2–0.8 | 1.000 | 1.000 | 0 | 5 |
| compromise_indication | 0.1–0.9 | 0.800 | 1.000 | 1 | 5 |
| ongoing | 0.5–0.5 | 1.000 | 1.000 | 0 | 5 |
| ongoing | 0.4–0.6 | 1.000 | 1.000 | 0 | 5 |
| ongoing | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 |
| ongoing | 0.2–0.8 | 1.000 | 1.000 | 0 | 5 |
| ongoing | 0.1–0.9 | 0.800 | 1.000 | 1 | 5 |

**Choice única: cobertura × erro por confiança** (informativa)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 5 |
| 0.300 | 1.000 | 0.000 | 5 |
| 0.500 | 1.000 | 0.000 | 5 |
| 0.700 | 1.000 | 0.000 | 5 |
| 0.900 | 1.000 | 0.000 | 5 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | falhas operacionais (→ fila) | perguntas | p50_ms | p95_ms | tokens_por_alerta | tokens_total | US$_total | US$_por_1000_alertas | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | 0 | 25 | 428 | 455 | 2140 | 10700 | 0.000449 | 0.0898 | jev-1.13.0 |

### Caso a caso

`esp`/`crit`/`ind`/`and` = Nouls `expected_activity`, `critical_asset`, `compromise_indication`, `ongoing` (gabarito entre parênteses: T/F/?); `Choice` = vencedor da pergunta `action` (confiança); `ok` compara a ação do Jev com o gabarito; `caro` marca E1/E2/E3; `base` = baseline; `urg` = urgência do aviso ao dono.

| id | fam | gab | esp | crit | ind | and | Choice | ação Jev | urg | ok | caro | base | origem | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TA-R001 | fácil / outros | auto_close | 0.82 (T) | 0.94 (T) | 0.02 (F) | 0.10 (F) | auto_close (1.00) | auto_close |  | ✓ |  | auto_close | jev | o contexto explica o alerta inteiro e não há indício |
| TA-R002 | fácil / outros | notify_owner | 0.03 (F) | 0.14 (F) | 0.02 (F) | 0.87 (T) | notify_owner (0.98) | notify_owner | manha | ✓ |  | notify_owner | jev | sem indício e o contexto não explica o alerta inteiro |
| TA-R003 | fácil / outros | queue_tier2 | 0.03 (F) | 0.06 (F) | 0.84 (T) | 0.09 (F) | queue_tier2 (0.98) | queue_tier2 |  | ✓ |  | queue_tier2 | jev | indício sem as três condições de contenção |
| TA-R004 | fácil / outros | contain_now | 0.02 (F) | 0.73 (T) | 0.96 (T) | 0.93 (T) | contain_now (1.00) | contain_now |  | ✓ |  | contain_now | jev | indício de comprometimento em andamento em ativo crítico (proposta de contenção) |
| TA-R005 | fácil / outros | auto_close | 0.92 (T) | 0.06 (F) | 0.02 (F) | 0.94 (T) | auto_close (1.00) | auto_close |  | ✓ |  | auto_close | jev | o contexto explica o alerta inteiro e não há indício |
