# Variantes de desenho — repeticao-ou-revisao (só no ajuste)

Gerado por `run.py variantes` em 2026-10-01; 29 grupos do `ajuste`; mesmas perguntas e política, muda só o state (minutos) ou o número de requisições por grupo de 3 (inteiro × pares).

| configuração | requisições | falhas | Jev (política) | só Choice | correções perdidas | efeitos duplicados | unclear → revisar | revisou sem necessidade | grupos de 3 distintas certos | tokens_por_requisicao |
|---|---|---|---|---|---|---|---|---|---|---|
| sem minutos · grupo de 3 inteiro (a de `perguntas.py`) | 27 | 0 | 0.931 | 0.897 | 0 | 0 | 4/4 | 2/25 | 3/3 | 2693 |
| COM minutos · grupo de 3 inteiro | 27 | 0 | 0.931 | 0.862 | 0 | 0 | 4/4 | 2/25 | 3/3 | 2723 |
| sem minutos · grupo de 3 em PARES | 30 | 0 | 0.897 | 0.862 | 0 | 0 | 4/4 | 3/25 | 2/3 | 2690 |

## O que muda, grupo a grupo, contra a primeira configuração

**COM minutos · grupo de 3 inteiro**

| id | gabarito | antes | nesta | motivo |
|---|---|---|---|---|
| RR-A026 | unclear | unclear (choice unclear) | unclear (choice revision) | Noul de dúvida: no_link_word 0.94; arrived_out_of_order 0.93 |

Diferença absoluta nos Nouls contra a primeira configuração: média 0.011, máxima 0.14.

**sem minutos · grupo de 3 em PARES**

| id | gabarito | antes | nesta | motivo |
|---|---|---|---|---|
| RR-A023 | same_intent | same_intent (choice same_intent) | unclear (choice unclear) | pares: same_intent depois unclear — o texto não decide entre corrigir e somar (Choice) |

Diferença absoluta nos Nouls contra a primeira configuração: média 0.013, máxima 0.91.
