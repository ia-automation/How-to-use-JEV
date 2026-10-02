# Rascunho — requisito-mudou (encanamento)

## Conjunto `rascunho` — 5 histórias, 19 requisitos (arquivo versão 2026-10-01, autor fable); 0 difíceis

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Por requisito e por história — baseline × sempre mantido × Jev (principal e informativa) nos mesmos casos

`acerto_total` = rótulo exato nos requisitos; `acerto_mudados` = só nos que o gabarito marca `substituido`/`negado`/`incerto`. **MUDANÇA PERDIDA** = requisito substituído ou negado que saiu `mantido` (a shortlist velha continua valendo: a dor do exemplo). **TROCA INDEVIDA** = requisito mantido ou incerto (hipótese, terceiro) que saiu `substituido` ou `negado` (cadastro trocado por fala que não decide). `novo_valor certo` = entre os `substituido` acertados. `reavaliar exato` = conjunto e ordem iguais ao gabarito (conta do código). `detectou mudança` = história com algum requisito mudado em que a variante marcou algum. `sempre mantido` = o baseline trivial do LEIA-ME.

| variante | requisitos | acerto_total | acerto_mudados | MUDANÇA PERDIDA (subst/negado → mantido) | TROCA INDEVIDA (incerto/mantido → subst/negado) | hipótese/terceiro → substituido | novo_valor certo | reavaliar exato (histórias) | detectou mudança | alarme falso (história sem mudança) |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (palavras-chave) | 19 | 0.947 | 0.750 | 1/4 | 0/15 | 0/0 | 2/2 | 4/5 | 3/4 | 0/1 |
| sempre mantido | 19 | 0.789 | 0.000 | 4/4 | 0/15 | 0/0 | 0/0 | 2/5 | 0/4 | 0/1 |
| Jev choice | 19 | 1.000 | 1.000 | 0/4 | 0/15 | 0/0 | 3/3 | 5/5 | 4/4 | 0/1 |
| Jev nouls | 19 | 1.000 | 1.000 | 0/4 | 0/15 | 0/0 | 3/3 | 5/5 | 4/4 | 0/1 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 mudança perdida | 0/4 | ≤ 2 | ✓ |
| 2 troca indevida | 0/15 | ≤ 4 | ✓ |
| 3 acerto nos mudados | 1.000 (4) | ≥ 0.7 | ✓ |
| 4 reavaliar exato | 5/5 (1.000) | ≥ 0.85 | ✓ |
| 5 acerto total | 1.000 (19) | ≥ 0.9 | ✓ |
| secundário: novo_valor certo | 3/3 (1.000) | ≥ 0.85 | ✓ |
| secundário: detectou mudança | 4/4 (1.000) | ≥ 0.85 | ✓ |

**Matriz de confusão — Jev choice** (linhas = gabarito, colunas = previsto) · por classe: `mantido` 15/15 · `substituido` 3/3 · `negado` 1/1 · `incerto` 0/0

| gabarito ↓ / previsto → | mantido | substituido | negado | incerto |
|---|---|---|---|---|
| mantido | 15 | 0 | 0 | 0 |
| substituido | 0 | 3 | 0 | 0 |
| negado | 0 | 0 | 1 | 0 |
| incerto | 0 | 0 | 0 | 0 |

**Matriz de confusão — Jev nouls** (linhas = gabarito, colunas = previsto) · por classe: `mantido` 15/15 · `substituido` 3/3 · `negado` 1/1 · `incerto` 0/0

| gabarito ↓ / previsto → | mantido | substituido | negado | incerto |
|---|---|---|---|---|
| mantido | 15 | 0 | 0 | 0 |
| substituido | 0 | 3 | 0 | 0 |
| negado | 0 | 0 | 1 | 0 |
| incerto | 0 | 0 | 0 | 0 |

**Matriz de confusão — baseline (palavras-chave)** (linhas = gabarito, colunas = previsto) · por classe: `mantido` 15/15 · `substituido` 2/3 · `negado` 1/1 · `incerto` 0/0

| gabarito ↓ / previsto → | mantido | substituido | negado | incerto |
|---|---|---|---|---|
| mantido | 15 | 0 | 0 | 0 |
| substituido | 1 | 2 | 0 | 0 |
| negado | 0 | 0 | 1 | 0 |
| incerto | 0 | 0 | 0 | 0 |

### Choice de status — probabilidade do vencedor e da classe certa, por classe do gabarito

| gabarito | n | P(vencedor) mín–mediana–máx | P(classe certa) mín–mediana–máx | P(classe certa) < 0,5 |
|---|---|---|---|---|
| mantido | 15 | 1.00–1.00–1.00 | 1.00–1.00–1.00 | 0 |
| substituido | 3 | 1.00–1.00–1.00 | 1.00–1.00–1.00 | 0 |
| negado | 1 | 0.99–0.99–0.99 | 0.99–0.99–0.99 | 0 |

### Nouls informativos — valores por classe do gabarito (mín–máx) e acerto a 0,5

| noul | faixa | mantido | substituido | negado | incerto |
|---|---|---|---|---|---|
| changed | 0.3–0.7 | 0.04–0.08 (15) | 0.96–0.97 (3) | 0.96–0.96 (1) | — |
| dropped | 0.3–0.7 | 0.04–0.26 (15) | 0.03–0.04 (3) | 0.94–0.94 (1) | — |
| open | 0.3–0.7 | 0.05–0.10 (15) | 0.03–0.04 (3) | 0.05–0.05 (1) | — |

### Valor novo — candidatos do código e escolha do Jev nos `substituido` do gabarito

| id | q | atributo | gabarito | n_cand | gabarito entre os candidatos | escolha (P) | saiu | ok |
|---|---|---|---|---|---|---|---|---|
| RM-R001 | q2 | vagas | 2 | 4 | sim | 2 (1.00) | 2 | ✓ |
| RM-R003 | q4 | orcamento | até R$ 680.000 | 1 | sim | até R$ 680.000 (1.00) | até R$ 680.000 | ✓ |
| RM-R005 | q3 | quartos | 3 | 4 | sim | 3 (0.96) | 3 | ✓ |

### Por família difícil (pela `nota` do rotulador) — requisitos mudados e erros caros

| família | histórias | requisitos | mudados | acerto mudados Jev | acerto mudados baseline | mudança perdida Jev | troca indevida Jev | reavaliar exato Jev | mudança perdida baseline | troca indevida baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| fácil / outros | 5 | 19 | 4 | 1.000 | 0.750 | 0 | 0 | 5/5 | 1 | 0 |

### Curva da Choice principal — piso do vencedor (mesmas respostas; informativo no teste)

| piso do vencedor | cobertura (não incerto) | erro entre decididos | mudança perdida | troca indevida | acerto total | reavaliar exato |
|---|---|---|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 0 | 0 | 1.000 | 5 |
| 0.400 | 1.000 | 0.000 | 0 | 0 | 1.000 | 5 |
| 0.500 | 1.000 | 0.000 | 0 | 0 | 1.000 | 5 |
| 0.600 | 1.000 | 0.000 | 0 | 0 | 1.000 | 5 |
| 0.700 | 1.000 | 0.000 | 0 | 0 | 1.000 | 5 |
| 0.800 | 1.000 | 0.000 | 0 | 0 | 1.000 | 5 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | histórias longas (sem chamada) | falhas operacionais (→ incerto) | perguntas | p50_ms | p95_ms | tokens_por_historia | US$_total | US$_por_1000_historias | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | 0 | 0 | 86 | 386 | 389 | 11134 | 0.002338 | 0.4676 | jev-1.13.0 |

### Caso a caso (um requisito por linha)

`P` = probabilidade do vencedor da Choice; `chg/drop/open` = Nouls informativos; `ok` compara o rótulo da variante principal com o gabarito; `caro` = mudança perdida ou troca indevida; `base` = baseline. A linha `reavaliar` fecha cada história.

| id | fam | q | atributo | valor | gab | Jev | P | chg/drop/open | nouls→ | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RM-R001 | fácil / outros | q1 | orcamento | até R$ 600.000 | mantido | mantido | 1.00 | 0.06/0.04/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R001 | fácil / outros | q2 | vagas | 1 | substituido → 2 | substituido → 2 | 1.00 | 0.97/0.04/0.03 | substituido | ✓ |  | substituido → 2 | replaced P=1.00; valor '2' P=1.00 |
| RM-R001 | fácil / outros | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.05/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R001 | fácil / outros | q4 | bairro | Tatuapé ou Mooca | mantido | mantido | 1.00 | 0.07/0.04/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R001 |  | reavaliar |  |  | IM-01, IM-03 | IM-01, IM-03 |  |  | IM-01, IM-03 | ✓ |  | IM-01, IM-03 |  |
| RM-R002 | fácil / outros | q1 | orcamento | até R$ 3.000/mês | mantido | mantido | 1.00 | 0.04/0.04/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R002 | fácil / outros | q2 | quartos | 1 | mantido | mantido | 1.00 | 0.05/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R002 | fácil / outros | q3 | pet | sim | mantido | mantido | 1.00 | 0.06/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R002 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-R003 | fácil / outros | q1 | quartos | 3 | mantido | mantido | 1.00 | 0.06/0.06/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R003 | fácil / outros | q2 | financiamento | sim | mantido | mantido | 1.00 | 0.08/0.07/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R003 | fácil / outros | q3 | vagas | 2 | mantido | mantido | 1.00 | 0.05/0.07/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R003 | fácil / outros | q4 | orcamento | até R$ 750.000 | substituido → até R$ 680.000 | substituido → até R$ 680.000 | 1.00 | 0.96/0.03/0.04 | substituido | ✓ |  | substituido → até R$ 680.000 | replaced P=1.00; valor 'até R$ 680.000' P=1.00 |
| RM-R003 |  | reavaliar |  |  | IM-02, IM-03 | IM-02, IM-03 |  |  | IM-02, IM-03 | ✓ |  | IM-02, IM-03 |  |
| RM-R004 | fácil / outros | q1 | pet | sim | negado | negado | 0.99 | 0.96/0.94/0.05 | negado | ✓ |  | negado | denied P=0.99 |
| RM-R004 | fácil / outros | q2 | orcamento | até R$ 2.800/mês | mantido | mantido | 1.00 | 0.05/0.08/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R004 | fácil / outros | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.04/0.12/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R004 | fácil / outros | q4 | mobilia | indiferente | mantido | mantido | 1.00 | 0.05/0.26/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R004 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-R005 | fácil / outros | q1 | orcamento | até R$ 900.000 | mantido | mantido | 1.00 | 0.05/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R005 | fácil / outros | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.06/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R005 | fácil / outros | q3 | quartos | 2 | substituido → 3 | substituido → 3 | 1.00 | 0.96/0.03/0.03 | substituido | ✓ |  | mantido | replaced P=1.00; valor '3' P=0.96 |
| RM-R005 | fácil / outros | q4 | bairro | Batel ou Água Verde | mantido | mantido | 1.00 | 0.08/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-R005 |  | reavaliar |  |  | IM-01, IM-03 | IM-01, IM-03 |  |  | IM-01, IM-03 | ✓ |  | [] |  |
