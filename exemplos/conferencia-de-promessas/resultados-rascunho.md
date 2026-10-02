# Rascunho — conferencia-de-promessas (encanamento)

## Conjunto `rascunho` — 5 fichas, 18 afirmações (arquivo versão 2026-10-01, autor fable)

> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**

### Relação e ação — Jev + código × baseline, por desenho

`acerto_relacao` = relação prevista (código ou Jev, resposta dura) × gabarito, todas as afirmações. `cobertura`/`erro_decididos`/`revisar` = ação com CONF_MANTER=0.7, CONF_RETIRAR=0.5; erro entre decididos = manteve o que não é supported ou retirou o que é. `erro_caro` = gabarito contradicted/not_stated → `manter` (promessa inventada passou); `_duro` = o mesmo sem faixa (relação prevista supported). `baseline` = número + palavra de promessa + booleano da ficha + palavras na ficha, sem faixa.

| desenho | n | acerto_relacao | cobertura | erro_decididos | revisar | erro_caro | erro_caro_duro | baseline_acerto | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| choice | 18 | 1.000 | 1.000 | 0.000 | 0 | 0/7 | 0/7 | 1.000 | 0/7 |
| choice+topico | 18 | 1.000 | 1.000 | 0.000 | 0 | 0/7 | 0/7 | 1.000 | 0/7 |

### Matriz gabarito × previsto — `choice`

| gabarito \ previsto | supported | contradicted | not_stated |
|---|---|---|---|
| supported | 11 | 0 | 0 |
| contradicted | 0 | 4 | 0 |
| not_stated | 0 | 0 | 3 |

### Por caminho (código puro / composta / Jev) — `choice`

`codigo` = número comparado em código, sem chamada; `composta` = número bate e o resto foi ao Jev (número contradito decide sozinho); `jev` = só a Choice.

| caminho | n | acerto_relacao | erro_caro | revisar | baseline |
|---|---|---|---|---|---|
| codigo | 7 | 1.000 | 0/1 | 0 | 1.000 |
| jev | 11 | 1.000 | 0/6 | 0 | 1.000 |

### Numéricas do gabarito (nota `numérica`) — por onde passaram — `choice`

| caminho | n | acerto_relacao | erros |
|---|---|---|---|
| codigo | 7 | 1.000 | — |
| composta | 0 | nan | — |
| jev | 0 | nan | — |
| codigo (não marcada numérica) | 0 | nan | — |

### Por família difícil (nota `difícil`) — `choice`

| familias | n | acerto_relacao | erro_caro | revisar | baseline |
|---|---|---|---|---|---|
| (fácil) | 18 | 1.000 | 0/7 | 0 | 1.000 |

### Cobertura × erro por limiares (só afirmações julgadas pelo Jev) — `choice`

| CONF_MANTER | CONF_RETIRAR | cobertura | erro_decididos | revisar | erro_caro |
|---|---|---|---|---|---|
| 0.000 | 0.000 | 1.000 | 0.000 | 0 | 0/6 |
| 0.500 | 0.500 | 1.000 | 0.000 | 0 | 0/6 |
| 0.700 | 0.500 | 1.000 | 0.000 | 0 | 0/6 |
| 0.800 | 0.500 | 1.000 | 0.000 | 0 | 0/6 |
| 0.700 | 0.700 | 1.000 | 0.000 | 0 | 0/6 |
| 0.900 | 0.500 | 1.000 | 0.000 | 0 | 0/6 |
| 0.900 | 0.700 | 1.000 | 0.000 | 0 | 0/6 |
| 0.900 | 0.900 | 1.000 | 0.000 | 0 | 0/6 |

### Cobertura × erro por limiares (só afirmações julgadas pelo Jev) — `choice+topico`

| CONF_MANTER | CONF_RETIRAR | cobertura | erro_decididos | revisar | erro_caro |
|---|---|---|---|---|---|
| 0.000 | 0.000 | 1.000 | 0.000 | 0 | 0/6 |
| 0.500 | 0.500 | 1.000 | 0.000 | 0 | 0/6 |
| 0.700 | 0.500 | 1.000 | 0.000 | 0 | 0/6 |
| 0.800 | 0.500 | 1.000 | 0.000 | 0 | 0/6 |
| 0.700 | 0.700 | 1.000 | 0.000 | 0 | 0/6 |
| 0.900 | 0.500 | 1.000 | 0.000 | 0 | 0/6 |
| 0.900 | 0.700 | 1.000 | 0.000 | 0 | 0/6 |
| 0.900 | 0.900 | 1.000 | 0.000 | 0 | 0/6 |

### Custo e latência (medidos na chamada real; do cache também)

Latência por REQUISIÇÃO (= por ficha com alguma afirmação no Jev). Mil fichas = mil rascunhos conferidos. As numéricas puras custam zero.

| desenho | requisicoes | perguntas | p50_ms | p95_ms | tokens_por_ficha | US$_por_ficha | US$_por_mil_fichas | US$_por_mil_afirmacoes | afirmacoes_no_jev | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| choice | 5 | 11 | 287 | 307 | 1995 | 0.0000838 | 0.0838 | 0.0233 | 11/18 | jev-1.13.0 |
| choice+topico | 5 | 22 | 295 | 319 | 2248 | 0.0000944 | 0.0944 | 0.0262 | 11/18 | jev-1.13.0 |

### Caso a caso — `choice` (`choice+topico` entre parênteses)

`jev` = opção vencedora (confiança); `tópico` = Noul auxiliar quando ligado. `marca`: `caro` = promessa inventada mantida; `erro` = ação decidida errada; `rel` = relação errada mas ação certa ou em revisão.

| id | af | afirmação | caminho | código | jev | relação | gab | ação | bl | marca |
|---|---|---|---|---|---|---|---|---|---|---|
| CP-R001 | a1 | O imóvel tem 2 quartos | codigo | quartos = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-R001 | a2 | O prédio aceita pet | jev | — | supported (1.00) (supported 1.00, tópico 0.99) | supported | supported | manter | supp | — |
| CP-R001 | a3 | Tem piscina | jev | — | not_stated (1.00) (not_stated 1.00, tópico 0.05) | not_stated | not_stated | retirar | not_ | — |
| CP-R002 | a1 | A casa vem mobiliada | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-R002 | a2 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-R002 | a3 | Tem churrasqueira | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-R003 | a1 | Fica a 500 metros do metrô | codigo | distancia = 500 × 500 → supported | — | supported | supported | manter | supp | — |
| CP-R003 | a2 | Aceita pet | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-R003 | a3 | O condomínio custa R$ 520 | codigo | condominio = 520 × 520 → supported | — | supported | supported | manter | supp | — |
| CP-R003 | a4 | Tem 2 vagas | jev | — | not_stated (1.00) (not_stated 1.00, tópico 0.06) | not_stated | not_stated | retirar | not_ | — |
| CP-R004 | a1 | Aceita financiamento | jev | — | supported (1.00) (supported 1.00, tópico 0.99) | supported | supported | manter | supp | — |
| CP-R004 | a2 | Tem 98 m² | codigo | area = 98 × 98 → supported | — | supported | supported | manter | supp | — |
| CP-R004 | a3 | Tem 3 vagas | codigo | vagas = 3 × 2 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-R004 | a4 | Tem academia | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-R005 | a1 | Vem mobiliado | jev | — | supported (0.99) (supported 0.99, tópico 0.97) | supported | supported | manter | supp | — |
| CP-R005 | a2 | Aceita financiamento | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-R005 | a3 | Não tem vaga | codigo | vagas = 0 × 0 → supported | — | supported | supported | manter | supp | — |
| CP-R005 | a4 | Aceita pet | jev | — | not_stated (1.00) (not_stated 1.00, tópico 0.06) | not_stated | not_stated | retirar | not_ | — |
