# Resultados — compactacao-de-contexto

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; validação, state, composição e baselines: `compactacao.py`. Preço: US$ 0,042 por milhão de tokens de entrada. State: `dict`; faixa de `needed` 0.3–0.7; guarda ≥ 0.7; veto `superseded` ≥ 0.7. Faixa validada: até 25 mensagens e 20000 caracteres por sessão (acima → manter tudo, sem chamada). A saída é a lista para o compactador: nada é apagado daqui.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (36 sessões, 477 mensagens: 169 manter, 299 descartar, 9 discutíveis fora da métrica), com a política acima; **1_necessaria_descartada**: gabarito `manter` que saiu `descartar` ≤ 6% das necessárias (≤ 10 de 169) — limite ABSOLUTO, não margem (no ajuste: 1 de 84); **2_acerto_piso**: acerto por mensagem ≥ 0,85 (absoluto; no ajuste 0,917); **3_acerto_sobre_baseline**: acerto ≥ melhor baseline de código no próprio teste + 0,08 (o LEIA-ME avisa 0,75 para `papel = usuario`); **secundario_nao_decide**: manter demais ≤ 20% das descartáveis; precisão de `manter` ≥ 0,75; **se_falhar**: 1 falhando = não serve para descartar sem revisão (só a faixa de dúvida vira `manter`, o resto vai a humano); 2 ou 3 falhando = a regra `papel = usuario` basta e o exemplo é descartado

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T16:18:32-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 e69e622b3cdf00fb… · `compactacao.py` sha256 ef1b952c22121b1d… · `run.py` sha256 2569eae48dd62535… · `dados/teste.json` sha256 24c25f9281f1e91e…

## Lado a lado

### Por mensagem, variante e conjunto

| conjunto | variante | mensagens | acerto | precisão manter | cobertura manter | NECESSÁRIA DESCARTADA (gab. manter → descartar) | manter demais (gab. descartar → manter) | necessária descartada: usuario |
|---|---|---|---|---|---|---|---|---|
| ajuste | baseline: papel = usuario | 229 | 0.795 | 0.761 | 0.643 | 30/84 | 17/145 | 0/54 |
| ajuste | baseline: últimas N | 229 | 0.633 | 0.500 | 0.417 | 49/84 | 35/145 | 39/54 |
| ajuste | baseline: palavras da tarefa | 229 | 0.677 | 0.596 | 0.369 | 53/84 | 21/145 | 35/54 |
| ajuste | manter tudo | 229 | 0.367 | 0.367 | 1.000 | 0/84 | 145/145 | 0/54 |
| ajuste | só needed (≥ 0,5) | 229 | 0.852 | 1.000 | 0.595 | 34/84 | 0/145 | 13/54 |
| ajuste | Jev (política) | 229 | 0.917 | 0.822 | 0.988 | 1/84 | 18/145 | 0/54 |
| teste | baseline: papel = usuario | 468 | 0.752 | 0.667 | 0.627 | 63/169 | 53/299 | 0/106 |
| teste | baseline: últimas N | 468 | 0.628 | 0.482 | 0.402 | 101/169 | 73/299 | 78/106 |
| teste | baseline: palavras da tarefa | 468 | 0.682 | 0.593 | 0.379 | 105/169 | 44/299 | 64/106 |
| teste | manter tudo | 468 | 0.361 | 0.361 | 1.000 | 0/169 | 299/299 | 0/106 |
| teste | só needed (≥ 0,5) | 468 | 0.823 | 0.939 | 0.544 | 77/169 | 6/299 | 35/106 |
| teste | Jev (política) | 468 | 0.861 | 0.748 | 0.929 | 12/169 | 53/299 | 2/106 |

### Nouls, custo

| conjunto | sessões | mensagens | difíceis | needed (todos) ≥0,5 | rule (usuario) ≥0,5 | status (assistente) ≥0,5 | literal (ferramenta) ≥0,5 | guarda/faixa mudaram | requisições | p50_ms | p95_ms | tokens_por_sessao | US$_por_1000_sessoes | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | 18 | 235 | 16 | 0.852 | 0.986 | 0.818 | 0.797 | 54 | 18 | 438 | 536 | 19905 | 0.8360 | jev-1.13.0 |
| teste | 36 | 477 | 31 | 0.823 | 0.887 | 0.742 | 0.730 | 117 | 36 | 415 | 672 | 20226 | 0.8495 | jev-1.13.0 |

## Conjunto `ajuste` — 18 sessões, 235 mensagens (arquivo versão 2026-10-01, autor fable); 84 `manter`, 145 `descartar`, 6 discutíveis (fora da métrica); 16 difíceis

### Por mensagem — métrica principal, baselines × manter tudo × Jev nas mesmas mensagens

**NECESSÁRIA DESCARTADA** = gabarito `manter` que saiu `descartar` (erro caro: restrição válida, decisão vigente, valor em uso ou erro aberto somem). **manter demais** = gabarito `descartar` que saiu `manter` (custa tokens). `papel = usuario` = toda mensagem do usuário fica; `últimas N` = as últimas 4 ficam; `palavras da tarefa` = ≥ 2 palavra(s) de conteúdo em comum com `tarefa_atual`; `manter tudo` = zero erro caro, zero compactação; `só needed` = `needed` ≥ 0,5 sem guarda nem faixa de dúvida; `Jev (política)` = `needed` em sim ou dúvida → manter, guarda por papel em sim sem `superseded` em sim → manter, senão descartar. As duas variantes do Jev leem a MESMA resposta.

| variante | mensagens | acerto | precisão manter | cobertura manter | NECESSÁRIA DESCARTADA (gab. manter → descartar) | manter demais (gab. descartar → manter) | necessária descartada: usuario |
|---|---|---|---|---|---|---|---|
| baseline: papel = usuario | 229 | 0.795 | 0.761 | 0.643 | 30/84 | 17/145 | 0/54 |
| baseline: últimas N | 229 | 0.633 | 0.500 | 0.417 | 49/84 | 35/145 | 39/54 |
| baseline: palavras da tarefa | 229 | 0.677 | 0.596 | 0.369 | 53/84 | 21/145 | 35/54 |
| manter tudo | 229 | 0.367 | 0.367 | 1.000 | 0/84 | 145/145 | 0/54 |
| só needed (≥ 0,5) | 229 | 0.852 | 1.000 | 0.595 | 34/84 | 0/145 | 13/54 |
| Jev (política) | 229 | 0.917 | 0.822 | 0.988 | 1/84 | 18/145 | 0/54 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 necessária descartada (absoluto) | 1/84 (0.012) | ≤ 0.06 | ✓ |
| 2 acerto por mensagem (piso) | 0.917 | ≥ 0.85 | ✓ |
| 3 acerto ≥ melhor baseline + margem | 0.917 (papel = usuario 0.795) | ≥ 0.875 | ✓ |
| secundário: manter demais | 18/145 (0.124) | ≤ 0.2 | ✓ |
| secundário: precisão de manter | 0.822 | ≥ 0.75 | ✓ |

### Por papel

| papel | mensagens | gab. manter | Jev (política): acerto | Jev (política): nec. descartada | só needed (≥ 0,5): acerto | só needed (≥ 0,5): nec. descartada | baseline: papel = usuario: acerto | baseline: papel = usuario: nec. descartada | baseline: últimas N: acerto | baseline: últimas N: nec. descartada | baseline: palavras da tarefa: acerto | baseline: palavras da tarefa: nec. descartada |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| usuario | 71 | 54 | 0.986 | 0/54 | 0.817 | 13/54 | 0.761 | 0/54 | 0.366 | 39/54 | 0.507 | 35/54 |
| assistente | 99 | 25 | 0.929 | 0/25 | 0.818 | 18/25 | 0.747 | 25/25 | 0.768 | 7/25 | 0.788 | 14/25 |
| ferramenta | 59 | 5 | 0.814 | 1/5 | 0.949 | 3/5 | 0.915 | 5/5 | 0.729 | 3/5 | 0.695 | 4/5 |

### Nouls contra o gabarito — 18 sessões que foram ao Jev

`needed` ↔ gabarito `manter` (corte 0,5; faixa = fração fora da dúvida e acerto entre as decididas). A guarda de cada papel contra o gabarito do papel. `superseded` só é lido como veto: aqui, quanto deu nas mantidas e nas descartadas.

| noul | positivos | acerto ≥0,5 | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| needed (todos) | 84 | 0.852 | 0.3–0.7 | 0.699 | 0.938 | 69 | 229 | 0.111 |
| rule (usuario) | 54 | 0.986 | ≥ 0.7 | 1.000 | 0.944 | 0 | 71 | 0.030 |
| status (assistente) | 25 | 0.818 | ≥ 0.7 | 1.000 | 0.848 | 0 | 99 | 0.159 |
| literal (ferramenta) | 5 | 0.797 | ≥ 0.7 | 1.000 | 0.915 | 0 | 59 | 0.141 |

`superseded` nas mantidas: 0.08–0.92 (média 0.42); ≥ 0.7 em 15/84. Nas descartadas: 0.07–0.97 (média 0.53); ≥ 0.7 em 45/145.

**A guarda e a faixa acrescentam algo a `needed` ≥ 0,5?** Mudaram 54 decisão(ões): 33 acerto(s) ganho(s), 18 erro(s) novo(s), 3 discutível(is).

### Por família difícil (pela `nota` do rotulador; a sessão inteira conta na família)

| família | sessões | mensagens | Jev | Jev nec. descartada | Jev manter demais | só needed | usuario | últimas N | palavras |
|---|---|---|---|---|---|---|---|---|---|
| conclusão anterior é premissa | 1 | 12 | 0.917 | 0/5 | 1/7 | 0.833 | 0.750 | 0.583 | 0.667 |
| contorno em vigor | 1 | 12 | 0.833 | 0/4 | 2/8 | 0.833 | 0.917 | 0.583 | 0.833 |
| decisão embutida | 1 | 12 | 0.917 | 0/5 | 1/7 | 0.833 | 0.750 | 0.417 | 0.583 |
| decisão revertida | 2 | 25 | 0.920 | 0/9 | 2/16 | 0.840 | 0.760 | 0.720 | 0.640 |
| hipótese descartada | 2 | 24 | 0.833 | 1/10 | 3/14 | 0.792 | 0.667 | 0.667 | 0.667 |
| progresso parcial | 1 | 11 | 0.909 | 0/4 | 1/7 | 0.727 | 0.727 | 0.727 | 0.727 |
| redundância | 1 | 12 | 0.917 | 0/4 | 1/8 | 0.833 | 0.917 | 0.667 | 0.333 |
| resposta curta que depende da pergunta | 1 | 13 | 0.923 | 0/5 | 1/8 | 0.846 | 0.769 | 0.462 | 0.769 |
| restrição antiga ainda válida | 2 | 34 | 0.912 | 0/12 | 3/22 | 0.882 | 0.794 | 0.647 | 0.765 |
| restrição que caducou | 1 | 14 | 0.929 | 0/4 | 1/10 | 0.857 | 0.786 | 0.714 | 0.786 |
| saída longa com uma linha necessária | 1 | 12 | 0.917 | 0/4 | 1/8 | 0.917 | 0.917 | 0.667 | 0.750 |
| tarefa interrompida | 1 | 11 | 0.909 | 0/4 | 1/7 | 0.909 | 0.909 | 0.818 | 0.636 |
| valor corrigido | 1 | 14 | 1.000 | 0/6 | 0/8 | 0.929 | 0.786 | 0.429 | 0.429 |
| fácil | 2 | 23 | 1.000 | 0/8 | 0/15 | 0.870 | 0.826 | 0.652 | 0.739 |

### Por tamanho de sessão (o state inteiro vai numa requisição; acerto cai com sessões maiores?)

| tamanho | sessões | mensagens | Jev | Jev nec. descartada | Jev manter demais | só needed | usuario |
|---|---|---|---|---|---|---|---|
| 12–13 msgs | 13 | 154 | 0.916 | 1/57 | 12/97 | 0.838 | 0.805 |
| 17–25 msgs | 1 | 20 | 0.850 | 0/7 | 3/13 | 0.900 | 0.750 |
| 14–16 msgs | 4 | 55 | 0.945 | 0/20 | 3/35 | 0.873 | 0.782 |

### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)

**Faixa de `needed` (≤ nao → não; ≥ sim → sim; meio = dúvida → manter); o resto como em `perguntas.py`**

| faixa de needed | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| atual (perguntas.py) | 0.917 | 0.822 | 0.988 | 1/84 | 18/145 |
| 0.5–0.5 | 0.952 | 0.929 | 0.940 | 5/84 | 6/145 |
| 0.4–0.6 | 0.939 | 0.889 | 0.952 | 4/84 | 10/145 |
| 0.3–0.7 | 0.917 | 0.822 | 0.988 | 1/84 | 18/145 |
| 0.2–0.8 | 0.803 | 0.654 | 0.988 | 1/84 | 44/145 |
| 0.1–0.9 | 0.541 | 0.444 | 1.000 | 0/84 | 105/145 |

**Corte da guarda por papel (`rule`/`status`/`literal`)**

| guarda ≥ | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| atual (perguntas.py) | 0.917 | 0.822 | 0.988 | 1/84 | 18/145 |
| 0.500 | 0.908 | 0.800 | 1.000 | 0/84 | 21/145 |
| 0.600 | 0.917 | 0.816 | 1.000 | 0/84 | 19/145 |
| 0.700 | 0.917 | 0.822 | 0.988 | 1/84 | 18/145 |
| 0.800 | 0.921 | 0.851 | 0.952 | 4/84 | 14/145 |
| 0.900 | 0.917 | 0.849 | 0.940 | 5/84 | 14/145 |
| desligada | 0.895 | 0.841 | 0.881 | 10/84 | 14/145 |

**Corte do veto `superseded` (anula a guarda)**

| superseded ≥ | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| atual (perguntas.py) | 0.917 | 0.822 | 0.988 | 1/84 | 18/145 |
| 0.500 | 0.921 | 0.837 | 0.976 | 2/84 | 16/145 |
| 0.600 | 0.917 | 0.828 | 0.976 | 2/84 | 17/145 |
| 0.700 | 0.917 | 0.822 | 0.988 | 1/84 | 18/145 |
| 0.800 | 0.913 | 0.814 | 0.988 | 1/84 | 19/145 |
| 0.900 | 0.895 | 0.783 | 0.988 | 1/84 | 23/145 |
| desligado | 0.873 | 0.748 | 0.988 | 1/84 | 28/145 |

**Baselines — grade de parâmetros neste conjunto (os de `perguntas.py` foram escolhidos no ajuste)**

| últimas N | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| 2 | 0.633 | 0.500 | 0.214 | 66/84 | 18/145 |
| 4 | 0.633 | 0.500 | 0.417 | 49/84 | 35/145 |
| 6 | 0.594 | 0.457 | 0.571 | 36/84 | 57/145 |
| 8 | 0.537 | 0.421 | 0.702 | 25/84 | 81/145 |
| 10 | 0.454 | 0.383 | 0.798 | 17/84 | 108/145 |
| 12 | 0.384 | 0.365 | 0.917 | 7/84 | 134/145 |
| palavras K=1 | 0.555 | 0.424 | 0.595 | 34/84 | 68/145 |
| palavras K=2 | 0.677 | 0.596 | 0.369 | 53/84 | 21/145 |
| palavras K=3 | 0.672 | 0.696 | 0.190 | 68/84 | 7/145 |

### Custo e latência (medidos na chamada real; do cache também)

| sessões | requisicoes | novas (não cache) | fora da faixa (sem chamada) | falhas operacionais (→ manter tudo) | perguntas | p50_ms | p95_ms | tokens_por_sessao | tokens_por_mensagem | US$_total | US$_por_1000_sessoes | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18 | 18 | 0 | 0 | 0 | 705 | 438 | 536 | 19905 | 1525 | 0.015048 | 0.8360 | jev-1.13.0 |

### Sessão a sessão

`gab.` = quantas o gabarito manda manter / descartar; `Jev` = quantas a política manteve; `nec. descartada` e `manter demais` listam os IDs; `usuario` = acerto do baseline na sessão.

| id | família | msgs | gab. | Jev manteve | acerto | nec. descartada | manter demais | usuario | origem |
|---|---|---|---|---|---|---|---|---|---|
| CC-A001 | hipótese descartada | 12 | 5/7 | 4 | 0.917 | m03 | — | 0.667 | jev |
| CC-A002 | restrição antiga ainda válida | 20 | 7/13 | 10 | 0.850 | — | m14, m15, m16 | 0.750 | jev |
| CC-A003 | restrição que caducou | 14 | 4/10 | 5 | 0.929 | — | m13 | 0.786 | jev |
| CC-A004 | fácil | 12 | 4/7 | 4 | 1.000 | — | — | 0.909 | jev |
| CC-A005 | restrição antiga ainda válida | 14 | 5/9 | 5 | 1.000 | — | — | 0.857 | jev |
| CC-A006 | resposta curta que depende da pergunta | 13 | 5/8 | 6 | 0.923 | — | m07 | 0.769 | jev |
| CC-A007 | hipótese descartada | 12 | 5/7 | 8 | 0.750 | — | m03, m06, m08 | 0.667 | jev |
| CC-A008 | saída longa com uma linha necessária | 12 | 4/8 | 5 | 0.917 | — | m07 | 0.917 | jev |
| CC-A009 | decisão revertida | 14 | 5/8 | 8 | 0.846 | — | m05, m14 | 0.692 | jev |
| CC-A010 | contorno em vigor | 13 | 4/8 | 7 | 0.833 | — | m08, m11 | 0.917 | jev |
| CC-A011 | tarefa interrompida | 13 | 4/7 | 5 | 0.909 | — | m08 | 0.909 | jev |
| CC-A012 | fácil | 12 | 4/8 | 4 | 1.000 | — | — | 0.750 | jev |
| CC-A013 | conclusão anterior é premissa | 12 | 5/7 | 6 | 0.917 | — | m12 | 0.750 | jev |
| CC-A014 | progresso parcial | 12 | 4/7 | 6 | 0.909 | — | m08 | 0.727 | jev |
| CC-A015 | decisão revertida | 12 | 4/8 | 4 | 1.000 | — | — | 0.833 | jev |
| CC-A016 | decisão embutida | 12 | 5/7 | 6 | 0.917 | — | m06 | 0.750 | jev |
| CC-A017 | redundância | 12 | 4/8 | 5 | 0.917 | — | m07 | 0.917 | jev |
| CC-A018 | valor corrigido | 14 | 6/8 | 6 | 1.000 | — | — | 0.786 | jev |

### Erros da política, mensagem a mensagem

`needed`/`sup`/`guarda` = os três Nouls da mensagem; `motivo` = o da política. Discutíveis ficam fora.

| sessão | msg | papel | gabarito | erro | needed | sup | guarda | motivo | texto |
|---|---|---|---|---|---|---|---|---|---|
| CC-A001 | m03 | ferramenta | manter | NECESSÁRIA DESCARTADA | 0.16 | 0.54 | 0.62 | não necessária (0.16); literal 0.62 | $ for i in $(seq 20); do pnpm vitest run src/fila/fila.test.ts -t reprocessa >/dev/null \|\|… |
| CC-A002 | m14 | ferramenta | descartar | manter demais | 0.42 | 0.48 | 0.26 | dúvida (0.42) — manter | $ psql "$DEV_DB" -c 'CREATE EXTENSION IF NOT EXISTS unaccent' CREATE EXTENSION |
| CC-A002 | m15 | ferramenta | descartar | manter demais | 0.44 | 0.49 | 0.56 | dúvida (0.44) — manter | $ pnpm migration:create idx-imoveis-bairro-sem-acento Created migrations/0164_idx-imoveis-… |
| CC-A002 | m16 | ferramenta | descartar | manter demais | 0.29 | 0.69 | 0.72 | guarda literal (0.72) | $ pnpm migration:run --env dev Error: functions in index expression must be marked IMMUTAB… |
| CC-A003 | m13 | ferramenta | descartar | manter demais | 0.29 | 0.33 | 0.78 | guarda literal (0.78) | $ curl -s localhost:3000/saude {"status":"ok"} |
| CC-A006 | m07 | assistente | descartar | manter demais | 0.33 | 0.78 | 0.85 | dúvida (0.33) — manter | Ok, opção 1. Qual o padrão de chave que vocês usam? |
| CC-A007 | m03 | ferramenta | descartar | manter demais | 0.27 | 0.47 | 0.78 | guarda literal (0.78) | $ ./scripts/mem.sh worker-relatorios 5m 4 14:00  312MiB 14:05  398MiB 14:10  487MiB 14:15 … |
| CC-A007 | m06 | ferramenta | descartar | manter demais | 0.40 | 0.75 | 0.77 | dúvida (0.40) — manter | $ TEMPLATE_CACHE=off ./scripts/mem.sh worker-relatorios 5m 3 14:30  305MiB 14:35  391MiB 1… |
| CC-A007 | m08 | usuario | descartar | manter demais | 0.33 | 0.40 | 0.22 | dúvida (0.33) — manter | E os listeners da fila? Lembro de alguém ter mexido na reconexão. |
| CC-A008 | m07 | assistente | descartar | manter demais | 0.39 | 0.93 | 0.93 | dúvida (0.39) — manter | Sobrou o de sessao.ts: `usuarioId` vem do header x-usuario, que pode faltar. Posso lançar … |
| CC-A009 | m05 | ferramenta | descartar | manter demais | 0.33 | 0.69 | 0.60 | dúvida (0.33) — manter | $ pnpm migration:create add-canal-origem Created migrations/0142_add-canal-origem.ts |
| CC-A009 | m14 | assistente | descartar | manter demais | 0.32 | 0.12 | 0.81 | dúvida (0.32) — manter | Deu lock timeout em dev: outra sessão está segurando a tabela. Vou ver quem é antes de ten… |
| CC-A010 | m08 | ferramenta | descartar | manter demais | 0.48 | 0.26 | 0.34 | dúvida (0.48) — manter | $ DOCKER_BUILDKIT=0 docker build -t registro.exemplo.com/api-notas:8c1d2e4 . Successfully … |
| CC-A010 | m11 | assistente | descartar | manter demais | 0.31 | 0.66 | 0.91 | dúvida (0.31) — manter | Push negado: não estou autenticado no registro. Como faço o login? |
| CC-A011 | m08 | assistente | descartar | manter demais | 0.17 | 0.54 | 0.70 | guarda status (0.70) | Em src/carrinho/total.ts:12 o código trunca com Math.floor: 9990 × 0,85 = 8491,5 centavos … |
| CC-A013 | m12 | assistente | descartar | manter demais | 0.38 | 0.08 | 0.24 | dúvida (0.38) — manter | Fechado: 5 mil, retomável pelo último id processado. |
| CC-A014 | m08 | ferramenta | descartar | manter demais | 0.31 | 0.47 | 0.61 | dúvida (0.31) — manter | $ grep -rn FILA_URL api-agenda/ api-agenda/src/config.ts:8:  filaUrl: process.env.FILA_URL… |
| CC-A016 | m06 | assistente | descartar | manter demais | 0.45 | 0.32 | 0.32 | dúvida (0.45) — manter | Troquei o botão. Para o valor, vou aceitar '1.234,56' na tela e converter para centavos. |
| CC-A017 | m07 | ferramenta | descartar | manter demais | 0.32 | 0.67 | 0.39 | dúvida (0.32) — manter | $ pnpm migration:create idx-pedidos-cliente --no-transaction Created migrations/0153_idx-p… |

## Conjunto `teste` — 36 sessões, 477 mensagens (arquivo versão 2026-10-01, autor fable); 169 `manter`, 299 `descartar`, 9 discutíveis (fora da métrica); 31 difíceis

### Por mensagem — métrica principal, baselines × manter tudo × Jev nas mesmas mensagens

**NECESSÁRIA DESCARTADA** = gabarito `manter` que saiu `descartar` (erro caro: restrição válida, decisão vigente, valor em uso ou erro aberto somem). **manter demais** = gabarito `descartar` que saiu `manter` (custa tokens). `papel = usuario` = toda mensagem do usuário fica; `últimas N` = as últimas 4 ficam; `palavras da tarefa` = ≥ 2 palavra(s) de conteúdo em comum com `tarefa_atual`; `manter tudo` = zero erro caro, zero compactação; `só needed` = `needed` ≥ 0,5 sem guarda nem faixa de dúvida; `Jev (política)` = `needed` em sim ou dúvida → manter, guarda por papel em sim sem `superseded` em sim → manter, senão descartar. As duas variantes do Jev leem a MESMA resposta.

| variante | mensagens | acerto | precisão manter | cobertura manter | NECESSÁRIA DESCARTADA (gab. manter → descartar) | manter demais (gab. descartar → manter) | necessária descartada: usuario |
|---|---|---|---|---|---|---|---|
| baseline: papel = usuario | 468 | 0.752 | 0.667 | 0.627 | 63/169 | 53/299 | 0/106 |
| baseline: últimas N | 468 | 0.628 | 0.482 | 0.402 | 101/169 | 73/299 | 78/106 |
| baseline: palavras da tarefa | 468 | 0.682 | 0.593 | 0.379 | 105/169 | 44/299 | 64/106 |
| manter tudo | 468 | 0.361 | 0.361 | 1.000 | 0/169 | 299/299 | 0/106 |
| só needed (≥ 0,5) | 468 | 0.823 | 0.939 | 0.544 | 77/169 | 6/299 | 35/106 |
| Jev (política) | 468 | 0.861 | 0.748 | 0.929 | 12/169 | 53/299 | 2/106 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 necessária descartada (absoluto) | 12/169 (0.071) | ≤ 0.06 | ✗ |
| 2 acerto por mensagem (piso) | 0.861 | ≥ 0.85 | ✓ |
| 3 acerto ≥ melhor baseline + margem | 0.861 (papel = usuario 0.752) | ≥ 0.832 | ✓ |
| secundário: manter demais | 53/299 (0.177) | ≤ 0.2 | ✓ |
| secundário: precisão de manter | 0.748 | ≥ 0.75 | ✗ |

### Por papel

| papel | mensagens | gab. manter | Jev (política): acerto | Jev (política): nec. descartada | só needed (≥ 0,5): acerto | só needed (≥ 0,5): nec. descartada | baseline: papel = usuario: acerto | baseline: papel = usuario: nec. descartada | baseline: últimas N: acerto | baseline: últimas N: nec. descartada | baseline: palavras da tarefa: acerto | baseline: palavras da tarefa: nec. descartada |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| usuario | 159 | 106 | 0.868 | 2/106 | 0.748 | 35/106 | 0.667 | 0/106 | 0.403 | 78/106 | 0.591 | 64/106 |
| assistente | 198 | 54 | 0.864 | 10/54 | 0.803 | 39/54 | 0.727 | 54/54 | 0.763 | 18/54 | 0.763 | 34/54 |
| ferramenta | 111 | 9 | 0.847 | 0/9 | 0.964 | 3/9 | 0.919 | 9/9 | 0.712 | 5/9 | 0.667 | 7/9 |

### Nouls contra o gabarito — 36 sessões que foram ao Jev

`needed` ↔ gabarito `manter` (corte 0,5; faixa = fração fora da dúvida e acerto entre as decididas). A guarda de cada papel contra o gabarito do papel. `superseded` só é lido como veto: aqui, quanto deu nas mantidas e nas descartadas.

| noul | positivos | acerto ≥0,5 | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| needed (todos) | 169 | 0.823 | 0.3–0.7 | 0.652 | 0.938 | 163 | 468 | 0.124 |
| rule (usuario) | 106 | 0.887 | ≥ 0.7 | 1.000 | 0.881 | 0 | 159 | 0.079 |
| status (assistente) | 54 | 0.742 | ≥ 0.7 | 1.000 | 0.828 | 0 | 198 | 0.180 |
| literal (ferramenta) | 9 | 0.730 | ≥ 0.7 | 1.000 | 0.874 | 0 | 111 | 0.185 |

`superseded` nas mantidas: 0.07–0.93 (média 0.43); ≥ 0.7 em 31/169. Nas descartadas: 0.07–0.97 (média 0.51); ≥ 0.7 em 82/299.

**A guarda e a faixa acrescentam algo a `needed` ≥ 0,5?** Mudaram 117 decisão(ões): 65 acerto(s) ganho(s), 47 erro(s) novo(s), 5 discutível(is).

### Por família difícil (pela `nota` do rotulador; a sessão inteira conta na família)

| família | sessões | mensagens | Jev | Jev nec. descartada | Jev manter demais | só needed | usuario | últimas N | palavras |
|---|---|---|---|---|---|---|---|---|---|
| conclusão anterior é premissa | 3 | 37 | 0.838 | 2/14 | 4/23 | 0.784 | 0.730 | 0.676 | 0.514 |
| contorno em vigor | 2 | 25 | 1.000 | 0/8 | 0/17 | 0.880 | 0.840 | 0.600 | 0.800 |
| decisão embutida | 1 | 14 | 0.929 | 0/4 | 1/10 | 0.929 | 0.786 | 0.857 | 0.786 |
| decisão revertida | 5 | 68 | 0.853 | 1/23 | 9/45 | 0.838 | 0.794 | 0.676 | 0.735 |
| hipótese descartada | 3 | 48 | 0.896 | 2/17 | 3/31 | 0.771 | 0.729 | 0.646 | 0.604 |
| progresso parcial | 2 | 26 | 0.769 | 1/9 | 5/17 | 0.731 | 0.654 | 0.654 | 0.731 |
| redundância | 1 | 11 | 0.727 | 1/5 | 2/6 | 0.818 | 0.818 | 0.545 | 0.545 |
| resposta curta que depende da pergunta | 2 | 27 | 0.889 | 2/13 | 1/14 | 0.778 | 0.704 | 0.519 | 0.630 |
| restrição antiga ainda válida | 2 | 25 | 0.880 | 0/9 | 3/16 | 0.840 | 0.680 | 0.600 | 0.760 |
| restrição que caducou | 2 | 26 | 0.962 | 0/9 | 1/17 | 0.846 | 0.731 | 0.692 | 0.769 |
| saída longa com uma linha necessária | 5 | 66 | 0.773 | 1/23 | 14/43 | 0.833 | 0.682 | 0.591 | 0.727 |
| tarefa interrompida | 1 | 10 | 0.700 | 0/3 | 3/7 | 0.800 | 0.800 | 0.500 | 0.800 |
| valor corrigido | 2 | 24 | 0.792 | 1/10 | 4/14 | 0.833 | 0.875 | 0.583 | 0.625 |
| fácil | 5 | 61 | 0.934 | 1/22 | 3/39 | 0.852 | 0.803 | 0.607 | 0.623 |

### Por tamanho de sessão (o state inteiro vai numa requisição; acerto cai com sessões maiores?)

| tamanho | sessões | mensagens | Jev | Jev nec. descartada | Jev manter demais | só needed | usuario |
|---|---|---|---|---|---|---|---|
| 12–13 msgs | 26 | 315 | 0.851 | 7/117 | 40/198 | 0.810 | 0.768 |
| 17–25 msgs | 2 | 41 | 0.854 | 2/15 | 4/26 | 0.805 | 0.659 |
| 14–16 msgs | 8 | 112 | 0.893 | 3/37 | 9/75 | 0.866 | 0.741 |

### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)

**Faixa de `needed` (≤ nao → não; ≥ sim → sim; meio = dúvida → manter); o resto como em `perguntas.py`**

| faixa de needed | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| atual (perguntas.py) | 0.861 | 0.748 | 0.929 | 12/169 | 53/299 |
| 0.5–0.5 | 0.889 | 0.855 | 0.834 | 28/169 | 24/299 |
| 0.4–0.6 | 0.895 | 0.845 | 0.870 | 22/169 | 27/299 |
| 0.3–0.7 | 0.861 | 0.748 | 0.929 | 12/169 | 53/299 |
| 0.2–0.8 | 0.765 | 0.606 | 0.994 | 1/169 | 109/299 |
| 0.1–0.9 | 0.472 | 0.406 | 1.000 | 0/169 | 247/299 |

**Corte da guarda por papel (`rule`/`status`/`literal`)**

| guarda ≥ | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| atual (perguntas.py) | 0.861 | 0.748 | 0.929 | 12/169 | 53/299 |
| 0.500 | 0.810 | 0.667 | 0.947 | 9/169 | 80/299 |
| 0.600 | 0.842 | 0.717 | 0.929 | 12/169 | 62/299 |
| 0.700 | 0.861 | 0.748 | 0.929 | 12/169 | 53/299 |
| 0.800 | 0.857 | 0.748 | 0.911 | 15/169 | 52/299 |
| 0.900 | 0.859 | 0.754 | 0.905 | 16/169 | 50/299 |
| desligada | 0.855 | 0.754 | 0.888 | 19/169 | 49/299 |

**Corte do veto `superseded` (anula a guarda)**

| superseded ≥ | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| atual (perguntas.py) | 0.861 | 0.748 | 0.929 | 12/169 | 53/299 |
| 0.500 | 0.863 | 0.754 | 0.923 | 13/169 | 51/299 |
| 0.600 | 0.865 | 0.755 | 0.929 | 12/169 | 51/299 |
| 0.700 | 0.861 | 0.748 | 0.929 | 12/169 | 53/299 |
| 0.800 | 0.853 | 0.734 | 0.929 | 12/169 | 57/299 |
| 0.900 | 0.840 | 0.706 | 0.953 | 8/169 | 67/299 |
| desligado | 0.827 | 0.683 | 0.970 | 5/169 | 76/299 |

**Baselines — grade de parâmetros neste conjunto (os de `perguntas.py` foram escolhidos no ajuste)**

| últimas N | acerto | precisão | cobertura | necessária descartada | manter demais |
|---|---|---|---|---|---|
| 2 | 0.658 | 0.563 | 0.237 | 129/169 | 31/299 |
| 4 | 0.628 | 0.482 | 0.402 | 101/169 | 73/299 |
| 6 | 0.598 | 0.455 | 0.574 | 72/169 | 116/299 |
| 8 | 0.534 | 0.413 | 0.692 | 52/169 | 166/299 |
| 10 | 0.434 | 0.364 | 0.757 | 41/169 | 224/299 |
| 12 | 0.363 | 0.348 | 0.870 | 22/169 | 276/299 |
| palavras K=1 | 0.553 | 0.413 | 0.562 | 74/169 | 135/299 |
| palavras K=2 | 0.682 | 0.593 | 0.379 | 105/169 | 44/299 |
| palavras K=3 | 0.684 | 0.744 | 0.189 | 137/169 | 11/299 |

### Custo e latência (medidos na chamada real; do cache também)

| sessões | requisicoes | novas (não cache) | fora da faixa (sem chamada) | falhas operacionais (→ manter tudo) | perguntas | p50_ms | p95_ms | tokens_por_sessao | tokens_por_mensagem | US$_total | US$_por_1000_sessoes | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 36 | 36 | 0 | 0 | 0 | 1431 | 415 | 672 | 20226 | 1526 | 0.030581 | 0.8495 | jev-1.13.0 |

### Sessão a sessão

`gab.` = quantas o gabarito manda manter / descartar; `Jev` = quantas a política manteve; `nec. descartada` e `manter demais` listam os IDs; `usuario` = acerto do baseline na sessão.

| id | família | msgs | gab. | Jev manteve | acerto | nec. descartada | manter demais | usuario | origem |
|---|---|---|---|---|---|---|---|---|---|
| CC-T001 | contorno em vigor | 12 | 4/8 | 4 | 1.000 | — | — | 0.833 | jev |
| CC-T002 | decisão revertida | 13 | 4/9 | 5 | 0.923 | — | m11 | 0.846 | jev |
| CC-T003 | valor corrigido | 12 | 5/7 | 7 | 0.667 | m09 | m04, m06, m12 | 0.833 | jev |
| CC-T004 | hipótese descartada | 22 | 8/14 | 10 | 0.818 | m05 | m14, m17, m21 | 0.591 | jev |
| CC-T005 | fácil | 12 | 4/8 | 6 | 0.833 | — | m07, m09 | 0.667 | jev |
| CC-T006 | decisão revertida | 12 | 4/6 | 7 | 0.900 | — | m03 | 0.800 | jev |
| CC-T007 | fácil | 12 | 3/9 | 4 | 0.917 | — | m07 | 0.833 | jev |
| CC-T008 | decisão revertida | 20 | 7/12 | 7 | 0.895 | m17 | m10 | 0.737 | jev |
| CC-T009 | decisão embutida | 14 | 4/10 | 5 | 0.929 | — | m04 | 0.786 | jev |
| CC-T010 | saída longa com uma linha necessária | 14 | 5/9 | 8 | 0.786 | — | m08, m10, m11 | 0.786 | jev |
| CC-T011 | redundância | 12 | 5/6 | 7 | 0.727 | m07 | m03, m10 | 0.818 | jev |
| CC-T012 | saída longa com uma linha necessária | 12 | 4/8 | 6 | 0.667 | m07 | m03, m09, m11 | 0.750 | jev |
| CC-T013 | saída longa com uma linha necessária | 14 | 5/9 | 7 | 0.857 | — | m08, m11 | 0.500 | jev |
| CC-T014 | fácil | 12 | 5/7 | 4 | 0.917 | m08 | — | 0.833 | jev |
| CC-T015 | resposta curta que depende da pergunta | 13 | 6/6 | 6 | 0.917 | m02 | — | 0.750 | jev |
| CC-T016 | contorno em vigor | 13 | 4/9 | 4 | 1.000 | — | — | 0.846 | jev |
| CC-T017 | progresso parcial | 12 | 5/7 | 9 | 0.667 | — | m04, m05, m08, m11 | 0.583 | jev |
| CC-T018 | progresso parcial | 14 | 4/10 | 4 | 0.857 | m11 | m06 | 0.714 | jev |
| CC-T019 | saída longa com uma linha necessária | 13 | 5/8 | 6 | 0.923 | — | m12 | 0.769 | jev |
| CC-T020 | conclusão anterior é premissa | 12 | 4/8 | 3 | 0.917 | m04 | — | 0.833 | jev |
| CC-T021 | decisão revertida | 13 | 4/9 | 7 | 0.769 | — | m05, m08, m12 | 0.846 | jev |
| CC-T022 | restrição que caducou | 14 | 4/9 | 4 | 1.000 | — | — | 0.769 | jev |
| CC-T023 | restrição antiga ainda válida | 14 | 4/10 | 5 | 0.929 | — | m12 | 0.786 | jev |
| CC-T024 | fácil | 13 | 5/8 | 5 | 1.000 | — | — | 0.769 | jev |
| CC-T025 | saída longa com uma linha necessária | 13 | 4/9 | 9 | 0.615 | — | m03, m07, m08, m09, m12 | 0.615 | jev |
| CC-T026 | decisão revertida | 13 | 4/9 | 7 | 0.769 | — | m08, m10, m11 | 0.769 | jev |
| CC-T027 | restrição antiga ainda válida | 12 | 5/6 | 8 | 0.818 | — | m05, m07 | 0.545 | jev |
| CC-T028 | fácil | 12 | 5/7 | 5 | 1.000 | — | — | 0.917 | jev |
| CC-T029 | resposta curta que depende da pergunta | 15 | 7/8 | 7 | 0.867 | m05 | m15 | 0.667 | jev |
| CC-T030 | conclusão anterior é premissa | 13 | 5/8 | 8 | 0.769 | — | m01, m02, m04 | 0.692 | jev |
| CC-T031 | tarefa interrompida | 12 | 3/7 | 6 | 0.700 | — | m09, m10, m12 | 0.800 | jev |
| CC-T032 | hipótese descartada | 12 | 5/7 | 5 | 1.000 | — | — | 0.750 | jev |
| CC-T033 | hipótese descartada | 14 | 4/10 | 3 | 0.929 | m01 | — | 0.929 | jev |
| CC-T034 | valor corrigido | 12 | 5/7 | 6 | 0.917 | — | m09 | 0.917 | jev |
| CC-T035 | restrição que caducou | 13 | 5/8 | 6 | 0.923 | — | m12 | 0.692 | jev |
| CC-T036 | conclusão anterior é premissa | 12 | 5/7 | 5 | 0.833 | m05 | m10 | 0.667 | jev |

### Erros da política, mensagem a mensagem

`needed`/`sup`/`guarda` = os três Nouls da mensagem; `motivo` = o da política. Discutíveis ficam fora.

| sessão | msg | papel | gabarito | erro | needed | sup | guarda | motivo | texto |
|---|---|---|---|---|---|---|---|---|---|
| CC-T002 | m11 | ferramenta | descartar | manter demais | 0.32 | 0.43 | 0.88 | dúvida (0.32) — manter | $ pnpm vitest run src/relatorios  ✓ 5 rotas em ISO com fuso  ✗ GET /relatorios/funil devol… |
| CC-T003 | m04 | assistente | descartar | manter demais | 0.34 | 0.94 | 0.42 | dúvida (0.34) — manter | Consumidor criado em worker-notas/src/consumidores/notas.ts, com prefetch 20. |
| CC-T003 | m06 | assistente | descartar | manter demais | 0.38 | 0.19 | 0.37 | dúvida (0.38) — manter | Ajustado para 5. |
| CC-T003 | m09 | assistente | manter | NECESSÁRIA DESCARTADA | 0.28 | 0.72 | 0.59 | não necessária (0.28); status 0.59 | Conecta, mas a declaração da fila diverge: a notas.emitir.dev já existe com x-dead-letter-… |
| CC-T003 | m12 | usuario | descartar | manter demais | 0.31 | 0.17 | 0.18 | dúvida (0.31) — manter | show |
| CC-T004 | m05 | assistente | manter | NECESSÁRIA DESCARTADA | 0.19 | 0.23 | 0.56 | não necessária (0.19); status 0.56 | Em 24 h de prod: 18.422 envios, e 1.307 ids de mensagem aparecem mais de uma vez — cerca d… |
| CC-T004 | m14 | usuario | descartar | manter demais | 0.44 | 0.62 | 0.14 | dúvida (0.44) — manter | E reconexão? Quando o canal cai, tudo que estava sem ack volta pra fila. |
| CC-T004 | m17 | usuario | descartar | manter demais | 0.34 | 0.42 | 0.15 | dúvida (0.34) — manter | Faz sentido. Mas por que o canal cai 212 vezes? |
| CC-T004 | m21 | ferramenta | descartar | manter demais | 0.44 | 0.51 | 0.82 | dúvida (0.44) — manter | $ ./scripts/dev/derrubar-canal.sh worker-email && sleep 20 && ./scripts/logs.sh dev worker… |
| CC-T005 | m07 | usuario | descartar | manter demais | 0.36 | 0.86 | 0.57 | dúvida (0.36) — manter | Testei aqui: reconecta, mas as notificações que chegaram enquanto estava fora se perdem. |
| CC-T005 | m09 | usuario | descartar | manter demais | 0.66 | 0.68 | 0.89 | dúvida (0.66) — manter | O servidor já aceita ?desde=<id>. Usa. |
| CC-T006 | m03 | usuario | descartar | manter demais | 0.54 | 0.94 | 0.60 | dúvida (0.54) — manter | TabelaV2, o conserto do foco no Modal e a remoção do BotaoAntigo. Essa remoção não quebra … |
| CC-T007 | m07 | usuario | descartar | manter demais | 0.32 | 0.82 | 0.45 | dúvida (0.32) — manter | Corrige as duas. |
| CC-T008 | m10 | usuario | descartar | manter demais | 0.33 | 0.86 | 0.50 | dúvida (0.33) — manter | Sem limite. São poucas, umas 200 por dia. |
| CC-T008 | m17 | assistente | manter | NECESSÁRIA DESCARTADA | 0.27 | 0.84 | 0.80 | status 0.80 anulada: substituída depois (0.84) | Rotina pronta em scripts/jobs/arquivar-vencidas.ts, agendada para 04:30, com a opção --lot… |
| CC-T009 | m04 | assistente | descartar | manter demais | 0.32 | 0.20 | 0.63 | dúvida (0.32) — manter | A tabela vendas tem assinado_em e criado_em; as devoluções ficam em vendas_devolucoes, com… |
| CC-T010 | m08 | assistente | descartar | manter demais | 0.44 | 0.59 | 0.73 | dúvida (0.44) — manter | O provedor manda um POST com um desafio e espera o mesmo valor de volta em até 5 s. Nosso … |
| CC-T010 | m10 | assistente | descartar | manter demais | 0.49 | 0.44 | 0.57 | dúvida (0.49) — manter | Implementado em src/webhooks/pagamento.ts: responde o desafio e não registra o corpo. |
| CC-T010 | m11 | ferramenta | descartar | manter demais | 0.32 | 0.41 | 0.79 | dúvida (0.32) — manter | $ pnpm tsx scripts/provedor.ts webhooks:verify --env sandbox --id wh_test_7Qk2 Error: veri… |
| CC-T011 | m03 | assistente | descartar | manter demais | 0.15 | 0.49 | 0.73 | guarda status (0.73) | O erro é um TypeError em formatarValor (src/pdf/ajudantes.ts:14), chamado na linha 58 do m… |
| CC-T011 | m07 | assistente | manter | NECESSÁRIA DESCARTADA | 0.29 | 0.87 | 0.93 | status 0.93 anulada: substituída depois (0.87) | Então o ajudante tem que tratar a ausência. Mostro 'R$ 0,00' ou um traço? |
| CC-T011 | m10 | ferramenta | descartar | manter demais | 0.35 | 0.52 | 0.81 | dúvida (0.35) — manter | $ pnpm vitest run src/pdf  ✓ formata 1250 como R$ 12,50  ✗ valor ausente vira traço    Ass… |
| CC-T012 | m03 | ferramenta | descartar | manter demais | 0.33 | 0.51 | 0.50 | dúvida (0.33) — manter | $ pnpm playwright test e2e/checkout Running 7 tests using 2 workers   ✓ carrinho vazio mos… |
| CC-T012 | m07 | assistente | manter | NECESSÁRIA DESCARTADA | 0.23 | 0.83 | 0.88 | status 0.88 anulada: substituída depois (0.83) | Causa: o commit a41c9d0 ('padroniza test ids') renomeou os identificadores de teste do Pix… |
| CC-T012 | m09 | assistente | descartar | manter demais | 0.33 | 0.24 | 0.53 | dúvida (0.33) — manter | Troquei qr-pix por pix-qr-code em e2e/checkout/pix.spec.ts. |
| CC-T012 | m11 | assistente | descartar | manter demais | 0.17 | 0.15 | 0.83 | guarda status (0.83) | Passou do QR e parou em outro identificador. |
| CC-T013 | m08 | ferramenta | descartar | manter demais | 0.48 | 0.17 | 0.82 | dúvida (0.48) — manter | $ pnpm tsx scripts/email.ts dominios:verificar dom_4h7Kp TXT: ok CNAME: pendente (NXDOMAIN… |
| CC-T013 | m11 | usuario | descartar | manter demais | 0.36 | 0.74 | 0.70 | dúvida (0.36) — manter | Enquanto isso, já deixa a variável EMAIL_DOMINIO no stack de dev. |
| CC-T014 | m08 | assistente | manter | NECESSÁRIA DESCARTADA | 0.29 | 0.91 | 0.95 | status 0.95 anulada: substituída depois (0.91) | Com juros a parcela é fixa e a diferença costuma ir na última. Sigo essa convenção ou mant… |
| CC-T015 | m02 | assistente | manter | NECESSÁRIA DESCARTADA | 0.29 | 0.90 | 0.89 | status 0.89 anulada: substituída depois (0.90) | Três formas: (1) janela fixa em memória, simples, mas não vale com várias réplicas; (2) ja… |
| CC-T017 | m04 | assistente | descartar | manter demais | 0.40 | 0.75 | 0.87 | dúvida (0.40) — manter | Hoje é um POST único, sem fila. Para retentar preciso de persistência: uso a tabela webhoo… |
| CC-T017 | m05 | usuario | descartar | manter demais | 0.56 | 0.44 | 0.88 | dúvida (0.56) — manter | Usa. |
| CC-T017 | m08 | assistente | descartar | manter demais | 0.39 | 0.30 | 0.57 | dúvida (0.39) — manter | Sigo com o recuo e a regra dos 4xx, e deixo o máximo de tentativas configurável. |
| CC-T017 | m11 | usuario | descartar | manter demais | 0.60 | 0.29 | 0.25 | dúvida (0.60) — manter | Uma dúvida: se o cliente responder 200 mas demorar mais de 10 s, conta como falha? |
| CC-T018 | m06 | usuario | descartar | manter demais | 0.36 | 0.95 | 0.42 | dúvida (0.36) — manter | No (3), usa o CEP 00000000 como inexistente, é o que o parceiro documenta. |
| CC-T018 | m11 | assistente | manter | NECESSÁRIA DESCARTADA | 0.21 | 0.84 | 0.82 | status 0.82 anulada: substituída depois (0.84) | Placar: (1), (2) e (4) prontos, um commit cada. (3) parado: o teste com 00000000 estoura o… |
| CC-T019 | m12 | ferramenta | descartar | manter demais | 0.42 | 0.12 | 0.87 | dúvida (0.42) — manter | $ pnpm tsx scripts/csv-para-xlsx.ts saida/inadimplencia-2026-09-c21b.csv Error: Cannot fin… |
| CC-T020 | m04 | usuario | manter | NECESSÁRIA DESCARTADA | 0.29 | 0.44 | 0.42 | não necessária (0.29); rule 0.42 | contract_name virou obrigatório ontem, na migration 0158. O front novo manda; quem não man… |
| CC-T021 | m05 | usuario | descartar | manter demais | 0.34 | 0.84 | 0.47 | dúvida (0.34) — manter | Isso. E inglês americano. |
| CC-T021 | m08 | assistente | descartar | manter demais | 0.32 | 0.96 | 0.51 | dúvida (0.32) — manter | Arquivos criados e tela usando as chaves. O idioma é escolhido pelo cabeçalho Accept-Langu… |
| CC-T021 | m12 | ferramenta | descartar | manter demais | 0.57 | 0.32 | 0.88 | dúvida (0.57) — manter | $ pnpm vitest run src/i18n  ✓ usa inglês quando o perfil pede  ✗ sem perfil usa português … |
| CC-T023 | m12 | ferramenta | descartar | manter demais | 0.32 | 0.19 | 0.70 | dúvida (0.32) — manter | $ curl -s 'localhost:3000/leads/exportar?de=2026-09-01&ate=2026-09-30' \| head -3 nome;emai… |
| CC-T025 | m03 | ferramenta | descartar | manter demais | 0.32 | 0.77 | 0.50 | dúvida (0.32) — manter | $ pnpm tsx scripts/preencher-canal.ts --env dev --lote 5000 [lote 1] ids 1..5000 ok (812 m… |
| CC-T025 | m07 | assistente | descartar | manter demais | 0.35 | 0.62 | 0.59 | dúvida (0.35) — manter | Com a tarefa agendada fecha-pedidos, que atualiza os mesmos pedidos em outra ordem. Ela ro… |
| CC-T025 | m08 | usuario | descartar | manter demais | 0.50 | 0.73 | 0.86 | dúvida (0.50) — manter | Pausa a fecha-pedidos em dev enquanto o script roda. Só em dev. |
| CC-T025 | m09 | ferramenta | descartar | manter demais | 0.44 | 0.32 | 0.25 | dúvida (0.44) — manter | $ ./scripts/agendador.sh dev pausar fecha-pedidos paused: fecha-pedidos (dev) |
| CC-T025 | m12 | usuario | descartar | manter demais | 0.39 | 0.12 | 0.47 | dúvida (0.39) — manter | Interrompi sem querer, foi mal. Pode continuar. |
| CC-T026 | m08 | assistente | descartar | manter demais | 0.21 | 0.66 | 0.90 | guarda status (0.90) | Entendido. Isso pede migration para a coluna e filtro de excluídos nas listagens. Posso cr… |
| CC-T026 | m10 | ferramenta | descartar | manter demais | 0.37 | 0.30 | 0.57 | dúvida (0.37) — manter | $ pnpm migration:create anuncios-excluido-em Created migrations/0160_anuncios-excluido-em.… |
| CC-T026 | m11 | ferramenta | descartar | manter demais | 0.44 | 0.33 | 0.82 | dúvida (0.44) — manter | $ pnpm vitest run src/anuncios  ✓ excluir marca excluido_em  ✓ listagem pública esconde ex… |
| CC-T027 | m05 | usuario | descartar | manter demais | 0.34 | 0.91 | 0.53 | dúvida (0.34) — manter | O servidor está em UTC, então esses horários aí são UTC? O relatório diário devia sair 06:… |
| CC-T027 | m07 | assistente | descartar | manter demais | 0.34 | 0.37 | 0.59 | dúvida (0.34) — manter | Conferido: o servidor está em UTC e o relatório é gerado às 06:30 UTC, ou seja, 03:30 de B… |
| CC-T029 | m05 | assistente | manter | NECESSÁRIA DESCARTADA | 0.27 | 0.90 | 0.90 | status 0.90 anulada: substituída depois (0.90) | Quatro grupos: 2026-07 (19 GB), 2026-08 (12 GB), import-legado (6,3 GB) e 2026-09-28 (1,1 … |
| CC-T029 | m15 | assistente | descartar | manter demais | 0.32 | 0.08 | 0.92 | dúvida (0.32) — manter | Aguardo sua decisão sobre os três arquivos. |
| CC-T030 | m01 | usuario | descartar | manter demais | 0.32 | 0.79 | 0.61 | dúvida (0.32) — manter | Antes do upload, precisamos do bucket em dev. Cria pelo script de infra. |
| CC-T030 | m02 | ferramenta | descartar | manter demais | 0.33 | 0.50 | 0.60 | dúvida (0.33) — manter | $ ./scripts/infra/criar-bucket.sh dev anexos-proposta bucket created: acme-dev-anexos-prop… |
| CC-T030 | m04 | usuario | descartar | manter demais | 0.34 | 0.65 | 0.70 | dúvida (0.34) — manter | Põe a variável no stack de dev. No de prod não: o bucket de prod ainda não existe. |
| CC-T031 | m09 | usuario | descartar | manter demais | 0.46 | 0.52 | 0.78 | dúvida (0.46) — manter | Tolerância de 60 segundos. Mais que isso não, segurança não deixa. |
| CC-T031 | m10 | assistente | descartar | manter demais | 0.30 | 0.69 | 0.89 | guarda status (0.89) | Mas o caso do suporte é de 3 minutos; com 60 s ele continua recusado. Sigo com 60 s mesmo … |
| CC-T031 | m12 | assistente | descartar | manter demais | 0.31 | 0.09 | 0.42 | dúvida (0.31) — manter | Implementando a variável AUTH_TOLERANCIA_RELOGIO_S com padrão 60. |
| CC-T033 | m01 | usuario | manter | NECESSÁRIA DESCARTADA | 0.29 | 0.88 | 0.50 | não necessária (0.29); rule 0.50 | O GET /agenda/dia leva 4 s num dia cheio. Descobre e corrige. |
| CC-T034 | m09 | ferramenta | descartar | manter demais | 0.34 | 0.33 | 0.56 | dúvida (0.34) — manter | $ pnpm migration:create dominios-bloqueados Created migrations/0161_dominios-bloqueados.ts |
| CC-T035 | m12 | ferramenta | descartar | manter demais | 0.34 | 0.21 | 0.80 | dúvida (0.34) — manter | $ pnpm openapi:lint docs/openapi.yaml docs/openapi.yaml:412:9  error  operation-operationI… |
| CC-T036 | m05 | assistente | manter | NECESSÁRIA DESCARTADA | 0.28 | 0.50 | 0.52 | não necessária (0.28); status 0.52 | Revertido no commit 7f1e2d3 (desfaz o c4d2f80) e publicado em dev. O checkout voltou a fun… |
| CC-T036 | m10 | ferramenta | descartar | manter demais | 0.36 | 0.31 | 0.49 | dúvida (0.36) — manter | $ git revert --no-edit 7f1e2d3 [feat/checkout a2c4e6f] Reapply "feat(checkout): cupom prog… |
