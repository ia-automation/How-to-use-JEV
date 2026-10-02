# Variantes de desenho — compactacao-de-contexto (só no ajuste)

Gerado por `run.py variantes` em 2026-10-01; 18 sessões do `ajuste`; mesmas perguntas e política, muda só como o state apresenta as mensagens (objeto por ID × lista de objetos).

| configuração | requisições | falhas | Jev (política) | só needed | nec. descartada | manter demais | tokens_por_sessao |
|---|---|---|---|---|---|---|---|
| state `dict` — `messages.m07` (a de `perguntas.py`) | 18 | 0 | 0.917 | 0.852 | 1/84 | 18/145 | 19905 |
| state `list` — entrada cujo `id` é m07 | 18 | 0 | 0.921 | 0.860 | 0/84 | 18/145 | 20597 |

## O que muda, mensagem a mensagem, contra a primeira configuração

**state `list` — entrada cujo `id` é m07**

| sessão | msg | gabarito | antes | nesta |
|---|---|---|---|---|
| CC-A001 | m03 | manter | descartar (needed 0.16) | manter (needed 0.19) |
| CC-A014 | m08 | descartar | manter (needed 0.31) | descartar (needed 0.27) |
| CC-A015 | m03 | descartar | descartar (needed 0.24) | manter (needed 0.31) |

Diferença absoluta nos Nouls contra a primeira configuração: média 0.029, máxima 0.17.
