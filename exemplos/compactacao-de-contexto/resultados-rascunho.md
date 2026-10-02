# Rascunho — compactacao-de-contexto (encanamento)

## Conjunto `rascunho` — 5 sessões, 61 mensagens (arquivo versão 2026-10-01, autor fable); 22 `manter`, 39 `descartar`, 0 discutíveis (fora da métrica); 0 difíceis

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Por mensagem — métrica principal, baselines × manter tudo × Jev nas mesmas mensagens

**NECESSÁRIA DESCARTADA** = gabarito `manter` que saiu `descartar` (erro caro: restrição válida, decisão vigente, valor em uso ou erro aberto somem). **manter demais** = gabarito `descartar` que saiu `manter` (custa tokens). `papel = usuario` = toda mensagem do usuário fica; `últimas N` = as últimas 6 ficam; `palavras da tarefa` = ≥ 1 palavra(s) de conteúdo em comum com `tarefa_atual`; `manter tudo` = zero erro caro, zero compactação; `só needed` = `needed` ≥ 0,5 sem guarda nem faixa de dúvida; `Jev (política)` = `needed` em sim ou dúvida → manter, guarda por papel em sim sem `superseded` em sim → manter, senão descartar. As duas variantes do Jev leem a MESMA resposta.

| variante | mensagens | acerto | precisão manter | cobertura manter | NECESSÁRIA DESCARTADA (gab. manter → descartar) | manter demais (gab. descartar → manter) | necessária descartada: usuario |
|---|---|---|---|---|---|---|---|
| baseline: papel = usuario | 61 | 0.754 | 0.684 | 0.591 | 9/22 | 6/39 | 0/13 |
| baseline: últimas N | 61 | 0.508 | 0.367 | 0.500 | 11/22 | 19/39 | 8/13 |
| baseline: palavras da tarefa | 61 | 0.607 | 0.471 | 0.727 | 6/22 | 18/39 | 5/13 |
| manter tudo | 61 | 0.361 | 0.361 | 1.000 | 0/22 | 39/39 | 0/13 |
| só needed (≥ 0,5) | 61 | 0.836 | 1.000 | 0.545 | 10/22 | 0/39 | 2/13 |
| Jev (política) | 61 | 0.902 | 0.833 | 0.909 | 2/22 | 4/39 | 0/13 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

_(critério ainda não fixado em `perguntas.py`)_

### Por papel

| papel | mensagens | gab. manter | Jev (política): acerto | Jev (política): nec. descartada | só needed (≥ 0,5): acerto | só needed (≥ 0,5): nec. descartada | baseline: papel = usuario: acerto | baseline: papel = usuario: nec. descartada | baseline: últimas N: acerto | baseline: últimas N: nec. descartada | baseline: palavras da tarefa: acerto | baseline: palavras da tarefa: nec. descartada |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| usuario | 19 | 13 | 0.947 | 0/13 | 0.895 | 2/13 | 0.684 | 0/13 | 0.316 | 8/13 | 0.684 | 5/13 |
| assistente | 28 | 6 | 0.964 | 0/6 | 0.821 | 5/6 | 0.786 | 6/6 | 0.643 | 1/6 | 0.714 | 0/6 |
| ferramenta | 14 | 3 | 0.714 | 2/3 | 0.786 | 3/3 | 0.786 | 3/3 | 0.500 | 2/3 | 0.286 | 1/3 |

### Nouls contra o gabarito — 5 sessões que foram ao Jev

`needed` ↔ gabarito `manter` (corte 0,5; faixa = fração fora da dúvida e acerto entre as decididas). A guarda de cada papel contra o gabarito do papel. `superseded` só é lido como veto: aqui, quanto deu nas mantidas e nas descartadas.

| noul | positivos | acerto ≥0,5 | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| needed (todos) | 22 | 0.836 | 0.3–0.7 | 0.754 | 0.891 | 15 | 61 | 0.123 |
| rule (usuario) | 13 | 1.000 | ≥ 0.7 | 1.000 | 1.000 | 0 | 19 | 0.017 |
| status (assistente) | 6 | 0.714 | ≥ 0.7 | 1.000 | 0.786 | 0 | 28 | 0.224 |
| literal (ferramenta) | 3 | 0.857 | ≥ 0.7 | 1.000 | 0.929 | 0 | 14 | 0.131 |

`superseded` nas mantidas: 0.10–0.74 (média 0.40); ≥ 0.7 em 2/22. Nas descartadas: 0.09–0.92 (média 0.49); ≥ 0.7 em 9/39.

**A guarda e a faixa acrescentam algo a `needed` ≥ 0,5?** Mudaram 12 decisão(ões): 8 acerto(s) ganho(s), 4 erro(s) novo(s), 0 discutível(is).

### Por família difícil (pela `nota` do rotulador; a sessão inteira conta na família)

| família | sessões | mensagens | Jev | Jev nec. descartada | Jev manter demais | só needed | usuario | últimas N | palavras |
|---|---|---|---|---|---|---|---|---|---|
| fácil | 5 | 61 | 0.902 | 2/22 | 4/39 | 0.836 | 0.754 | 0.508 | 0.607 |

### Por tamanho de sessão (o state inteiro vai numa requisição; acerto cai com sessões maiores?)

| tamanho | sessões | mensagens | Jev | Jev nec. descartada | Jev manter demais | só needed | usuario |
|---|---|---|---|---|---|---|---|
| 12–13 msgs | 5 | 61 | 0.902 | 2/22 | 4/39 | 0.836 | 0.754 |

### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)

**Faixa de `needed` (≤ nao → não; ≥ sim → sim; meio = dúvida → manter); o resto como em `perguntas.py`**

| faixa de needed | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| atual (perguntas.py) | 0.902 | 0.833 | 0.909 | 2/22 | 4/39 |
| 0.5–0.5 | 0.951 | 0.952 | 0.909 | 2/22 | 1/39 |
| 0.4–0.6 | 0.934 | 0.909 | 0.909 | 2/22 | 2/39 |
| 0.3–0.7 | 0.902 | 0.833 | 0.909 | 2/22 | 4/39 |
| 0.2–0.8 | 0.852 | 0.724 | 0.955 | 1/22 | 8/39 |
| 0.1–0.9 | 0.574 | 0.458 | 1.000 | 0/22 | 26/39 |

**Corte da guarda por papel (`rule`/`status`/`literal`)**

| guarda ≥ | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| atual (perguntas.py) | 0.902 | 0.833 | 0.909 | 2/22 | 4/39 |
| 0.500 | 0.869 | 0.769 | 0.909 | 2/22 | 6/39 |
| 0.600 | 0.869 | 0.769 | 0.909 | 2/22 | 6/39 |
| 0.700 | 0.902 | 0.833 | 0.909 | 2/22 | 4/39 |
| 0.800 | 0.902 | 0.864 | 0.864 | 3/22 | 3/39 |
| 0.900 | 0.885 | 0.857 | 0.818 | 4/22 | 3/39 |
| desligada | 0.869 | 0.850 | 0.773 | 5/22 | 3/39 |

**Corte do veto `superseded` (anula a guarda)**

| superseded ≥ | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| atual (perguntas.py) | 0.902 | 0.833 | 0.909 | 2/22 | 4/39 |
| 0.500 | 0.918 | 0.870 | 0.909 | 2/22 | 3/39 |
| 0.600 | 0.902 | 0.833 | 0.909 | 2/22 | 4/39 |
| 0.700 | 0.902 | 0.833 | 0.909 | 2/22 | 4/39 |
| 0.800 | 0.918 | 0.840 | 0.955 | 1/22 | 4/39 |
| 0.900 | 0.869 | 0.750 | 0.955 | 1/22 | 7/39 |
| desligado | 0.836 | 0.700 | 0.955 | 1/22 | 9/39 |

**Baselines — grade de parâmetros neste conjunto (os de `perguntas.py` foram escolhidos no ajuste)**

| últimas N | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| 2 | 0.574 | 0.300 | 0.136 | 19/22 | 7/39 |
| 4 | 0.541 | 0.350 | 0.318 | 15/22 | 13/39 |
| 6 | 0.508 | 0.367 | 0.500 | 11/22 | 19/39 |
| 8 | 0.475 | 0.375 | 0.682 | 7/22 | 25/39 |
| 10 | 0.410 | 0.360 | 0.818 | 4/22 | 32/39 |
| 12 | 0.377 | 0.367 | 1.000 | 0/22 | 38/39 |
| palavras K=1 | 0.607 | 0.471 | 0.727 | 6/22 | 18/39 |
| palavras K=2 | 0.672 | 0.556 | 0.455 | 12/22 | 8/39 |
| palavras K=3 | 0.689 | 0.636 | 0.318 | 15/22 | 4/39 |

### Custo e latência (medidos na chamada real; do cache também)

| sessões | requisicoes | novas (não cache) | fora da faixa (sem chamada) | falhas operacionais (→ manter tudo) | perguntas | p50_ms | p95_ms | tokens_por_sessao | tokens_por_mensagem | US$_total | US$_por_1000_sessoes | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 5 | 5 | 0 | 0 | 183 | 564 | 711 | 17181 | 1408 | 0.003608 | 0.7216 | jev-1.13.0 |

### Sessão a sessão

`gab.` = quantas o gabarito manda manter / descartar; `Jev` = quantas a política manteve; `nec. descartada` e `manter demais` listam os IDs; `usuario` = acerto do baseline na sessão.

| id | família | msgs | gab. | Jev manteve | acerto | nec. descartada | manter demais | usuario | origem |
|---|---|---|---|---|---|---|---|---|---|
| CC-R001 | fácil | 12 | 4/8 | 5 | 0.917 | — | m04 | 0.750 | jev |
| CC-R002 | fácil | 13 | 4/9 | 4 | 1.000 | — | — | 0.769 | jev |
| CC-R003 | fácil | 12 | 5/7 | 4 | 0.917 | m05 | — | 0.833 | jev |
| CC-R004 | fácil | 12 | 4/8 | 3 | 0.917 | m08 | — | 0.833 | jev |
| CC-R005 | fácil | 12 | 5/7 | 8 | 0.750 | — | m07, m09, m10 | 0.583 | jev |

### Erros da política, mensagem a mensagem

`needed`/`sup`/`guarda` = os três Nouls da mensagem; `motivo` = o da política. Discutíveis ficam fora.

| sessão | msg | papel | gabarito | erro | needed | sup | guarda | motivo | texto |
|---|---|---|---|---|---|---|---|---|---|
| CC-R001 | m04 | assistente | descartar | manter demais | 0.13 | 0.53 | 0.79 | guarda status (0.79) | A falha é de ponto flutuante em total.test.ts. Vou olhar como o total é calculado. |
| CC-R003 | m05 | ferramenta | manter | NECESSÁRIA DESCARTADA | 0.16 | 0.74 | 0.56 | não necessária (0.16); literal 0.56 | $ docker service logs api-agenda --tail 4 Starting api-agenda 1.9.0 Error: connect ECONNRE… |
| CC-R004 | m08 | ferramenta | manter | NECESSÁRIA DESCARTADA | 0.30 | 0.74 | 0.80 | literal 0.80 anulada: substituída depois (0.74) | $ pnpm vitest run src/frete/calcular.test.ts  ✓ CEP inválido lança erro  ✓ frete grátis a … |
| CC-R005 | m07 | ferramenta | descartar | manter demais | 0.43 | 0.68 | 0.69 | dúvida (0.43) — manter | $ pnpm migration:create renomear-dt-criacao Created migrations/0151_renomear-dt-criacao.ts |
| CC-R005 | m09 | usuario | descartar | manter demais | 0.36 | 0.85 | 0.36 | dúvida (0.36) — manter | Roda em dev antes. |
| CC-R005 | m10 | ferramenta | descartar | manter demais | 0.35 | 0.52 | 0.24 | dúvida (0.35) — manter | $ pnpm migration:run --env dev Applied 0151_renomear-dt-criacao (0.4s) |
