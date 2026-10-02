# Resultados — requisito-mudou

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, política e critério: `perguntas.py`; state, candidatos, validação, `reavaliar` e baseline: `requisitos.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Variante principal: `choice`; piso do vencedor 0.5; teto 4000 caracteres / 12 requisitos (acima → tudo `incerto`, sem chamada).

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (44 histórias, 181 requisitos), variante principal `choice` com a política acima; **variante_principal**: choice; **1_mudanca_perdida**: requisito `substituido` ou `negado` no gabarito que saiu `mantido` ≤ 2 de 28 (a dor: shortlist velha continua valendo); **2_troca_indevida**: requisito `incerto` (hipótese/terceiro) ou `mantido` no gabarito que saiu `substituido` ou `negado` ≤ 4 de 153; **3_acerto_mudados**: rótulo exato nos 40 requisitos mudados (`substituido`/`negado`/`incerto`) ≥ 0,75; **4_reavaliar**: `reavaliar` exato (conjunto e ordem) ≥ 0,85 das 44 histórias; **5_acerto_total**: rótulo exato nos 181 requisitos ≥ 0,90 (sempre-mantido = 0,779); **secundario_nao_decide**: `novo_valor` certo ≥ 0,85 dos `substituido` acertados; detectou que algo mudou ≥ 0,85 das 34 histórias com mudança; baseline informativo; **se_falhar**: 1 ou 2 falhando = o desenho não serve para atualizar o cadastro sem humano; 3, 4 ou 5 falhando = volta ao ajuste com dados novos

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T15:41:37-03:00; variante principal `choice`; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 18d651ccebb2743c… · `requisitos.py` sha256 6ff62506b8f9c7de… · `run.py` sha256 8ae5b6e032b90ce8… · `dados/teste.json` sha256 20234bc9baf6b7c1…

## Lado a lado

### Por variante e conjunto

| conjunto | variante | requisitos | acerto_total | acerto_mudados | MUDANÇA PERDIDA (subst/negado → mantido) | TROCA INDEVIDA (incerto/mantido → subst/negado) | hipótese/terceiro → substituido | novo_valor certo | reavaliar exato (histórias) | detectou mudança | alarme falso (história sem mudança) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | baseline (palavras-chave) | 95 | 0.874 | 0.556 | 4/13 | 2/82 | 0/5 | 5/5 | 18/22 | 10/17 | 0/5 |
| ajuste | sempre mantido | 95 | 0.811 | 0.000 | 13/13 | 0/82 | 0/5 | 0/0 | 16/22 | 0/17 | 0/5 |
| ajuste | Jev choice | 95 | 1.000 | 1.000 | 0/13 | 0/82 | 0/5 | 10/10 | 22/22 | 17/17 | 0/5 |
| ajuste | Jev nouls | 95 | 0.905 | 0.944 | 0/13 | 1/82 | 0/5 | 10/10 | 22/22 | 17/17 | 3/5 |
| teste | baseline (palavras-chave) | 181 | 0.823 | 0.350 | 15/28 | 7/153 | 1/12 | 6/10 | 30/44 | 14/34 | 4/10 |
| teste | sempre mantido | 181 | 0.779 | 0.000 | 28/28 | 0/153 | 0/12 | 0/0 | 29/44 | 0/34 | 0/10 |
| teste | Jev choice | 181 | 0.961 | 0.900 | 0/28 | 1/153 | 0/12 | 21/21 | 42/44 | 33/34 | 0/10 |
| teste | Jev nouls | 181 | 0.923 | 0.925 | 0/28 | 1/153 | 0/12 | 21/21 | 42/44 | 34/34 | 5/10 |

### Custo

| conjunto | histórias | difíceis | requisitos | p50_ms | p95_ms | tokens_por_historia | US$_por_1000 | modelo |
|---|---|---|---|---|---|---|---|---|
| ajuste | 22 | 19 | 95 | 404 | 485 | 12729 | 0.5346 | jev-1.13.0 |
| teste | 44 | 41 | 181 | 342 | 439 | 12156 | 0.5105 | jev-1.13.0 |

## Conjunto `ajuste` — 22 histórias, 95 requisitos (arquivo versão 2026-10-01, autor fable); 19 difíceis

### Por requisito e por história — baseline × sempre mantido × Jev (principal e informativa) nos mesmos casos

`acerto_total` = rótulo exato nos requisitos; `acerto_mudados` = só nos que o gabarito marca `substituido`/`negado`/`incerto`. **MUDANÇA PERDIDA** = requisito substituído ou negado que saiu `mantido` (a shortlist velha continua valendo: a dor do exemplo). **TROCA INDEVIDA** = requisito mantido ou incerto (hipótese, terceiro) que saiu `substituido` ou `negado` (cadastro trocado por fala que não decide). `novo_valor certo` = entre os `substituido` acertados. `reavaliar exato` = conjunto e ordem iguais ao gabarito (conta do código). `detectou mudança` = história com algum requisito mudado em que a variante marcou algum. `sempre mantido` = o baseline trivial do LEIA-ME.

| variante | requisitos | acerto_total | acerto_mudados | MUDANÇA PERDIDA (subst/negado → mantido) | TROCA INDEVIDA (incerto/mantido → subst/negado) | hipótese/terceiro → substituido | novo_valor certo | reavaliar exato (histórias) | detectou mudança | alarme falso (história sem mudança) |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (palavras-chave) | 95 | 0.874 | 0.556 | 4/13 | 2/82 | 0/5 | 5/5 | 18/22 | 10/17 | 0/5 |
| sempre mantido | 95 | 0.811 | 0.000 | 13/13 | 0/82 | 0/5 | 0/0 | 16/22 | 0/17 | 0/5 |
| Jev choice | 95 | 1.000 | 1.000 | 0/13 | 0/82 | 0/5 | 10/10 | 22/22 | 17/17 | 0/5 |
| Jev nouls | 95 | 0.905 | 0.944 | 0/13 | 1/82 | 0/5 | 10/10 | 22/22 | 17/17 | 3/5 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 mudança perdida | 0/13 | ≤ 2 | ✓ |
| 2 troca indevida | 0/82 | ≤ 4 | ✓ |
| 3 acerto nos mudados | 1.000 (18) | ≥ 0.75 | ✓ |
| 4 reavaliar exato | 22/22 (1.000) | ≥ 0.85 | ✓ |
| 5 acerto total | 1.000 (95) | ≥ 0.9 | ✓ |
| secundário: novo_valor certo | 10/10 (1.000) | ≥ 0.85 | ✓ |
| secundário: detectou mudança | 17/17 (1.000) | ≥ 0.85 | ✓ |

**Matriz de confusão — Jev choice** (linhas = gabarito, colunas = previsto) · por classe: `mantido` 77/77 · `substituido` 10/10 · `negado` 3/3 · `incerto` 5/5

| gabarito ↓ / previsto → | mantido | substituido | negado | incerto |
|---|---|---|---|---|
| mantido | 77 | 0 | 0 | 0 |
| substituido | 0 | 10 | 0 | 0 |
| negado | 0 | 0 | 3 | 0 |
| incerto | 0 | 0 | 0 | 5 |

**Matriz de confusão — Jev nouls** (linhas = gabarito, colunas = previsto) · por classe: `mantido` 69/77 · `substituido` 10/10 · `negado` 2/3 · `incerto` 5/5

| gabarito ↓ / previsto → | mantido | substituido | negado | incerto |
|---|---|---|---|---|
| mantido | 69 | 1 | 0 | 7 |
| substituido | 0 | 10 | 0 | 0 |
| negado | 0 | 0 | 2 | 1 |
| incerto | 0 | 0 | 0 | 5 |

**Matriz de confusão — baseline (palavras-chave)** (linhas = gabarito, colunas = previsto) · por classe: `mantido` 73/77 · `substituido` 5/10 · `negado` 3/3 · `incerto` 2/5

| gabarito ↓ / previsto → | mantido | substituido | negado | incerto |
|---|---|---|---|---|
| mantido | 73 | 1 | 1 | 2 |
| substituido | 4 | 5 | 1 | 0 |
| negado | 0 | 0 | 3 | 0 |
| incerto | 3 | 0 | 0 | 2 |

### Choice de status — probabilidade do vencedor e da classe certa, por classe do gabarito

| gabarito | n | P(vencedor) mín–mediana–máx | P(classe certa) mín–mediana–máx | P(classe certa) < 0,5 |
|---|---|---|---|---|
| mantido | 77 | 0.61–1.00–1.00 | 0.61–1.00–1.00 | 0 |
| substituido | 10 | 0.99–1.00–1.00 | 0.99–1.00–1.00 | 0 |
| negado | 3 | 0.88–0.95–0.99 | 0.88–0.95–0.99 | 0 |
| incerto | 5 | 0.68–0.94–1.00 | 0.68–0.94–1.00 | 0 |

### Nouls informativos — valores por classe do gabarito (mín–máx) e acerto a 0,5

| noul | faixa | mantido | substituido | negado | incerto |
|---|---|---|---|---|---|
| changed | 0.3–0.7 | 0.04–0.83 (77) | 0.87–0.97 (10) | 0.96–0.96 (3) | 0.07–0.18 (5) |
| dropped | 0.3–0.7 | 0.03–0.19 (77) | 0.03–0.28 (10) | 0.65–0.94 (3) | 0.04–0.10 (5) |
| open | 0.3–0.7 | 0.03–0.78 (77) | 0.03–0.14 (10) | 0.04–0.10 (3) | 0.82–0.95 (5) |

### Valor novo — candidatos do código e escolha do Jev nos `substituido` do gabarito

| id | q | atributo | gabarito | n_cand | gabarito entre os candidatos | escolha (P) | saiu | ok |
|---|---|---|---|---|---|---|---|---|
| RM-A001 | q2 | elevador | sim | 0 | sim | — | sim | ✓ |
| RM-A002 | q3 | vagas | 2 | 4 | sim | 2 (0.93) | 2 | ✓ |
| RM-A008 | q3 | vagas | 1 | 4 | sim | 1 (1.00) | 1 | ✓ |
| RM-A009 | q4 | vagas | 2 | 4 | sim | 2 (1.00) | 2 | ✓ |
| RM-A010 | q1 | mobilia | mobiliado | 2 | sim | mobiliado (0.99) | mobiliado | ✓ |
| RM-A011 | q4 | pet | sim | 0 | sim | — | sim | ✓ |
| RM-A014 | q4 | bairro | Pompeia ou Lapa | 2 | sim | Pompeia ou Lapa (0.74) | Pompeia ou Lapa | ✓ |
| RM-A016 | q3 | vagas | 1 | 4 | sim | 1 (1.00) | 1 | ✓ |
| RM-A019 | q2 | orcamento | até R$ 850.000 | 1 | sim | até R$ 850.000 (0.98) | até R$ 850.000 | ✓ |
| RM-A019 | q5 | quartos | 3 | 4 | sim | 3 (0.98) | 3 | ✓ |

### Por família difícil (pela `nota` do rotulador) — requisitos mudados e erros caros

| família | histórias | requisitos | mudados | acerto mudados Jev | acerto mudados baseline | mudança perdida Jev | troca indevida Jev | reavaliar exato Jev | mudança perdida baseline | troca indevida baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| mudança indireta | 3 | 14 | 3 | 1.000 | 0.000 | 0 | 0 | 3/3 | 3 | 0 |
| hipótese sobre o futuro | 2 | 8 | 2 | 1.000 | 0.500 | 0 | 0 | 2/2 | 0 | 0 |
| preferência de terceiro | 2 | 9 | 2 | 1.000 | 0.500 | 0 | 0 | 2/2 | 0 | 0 |
| orçamento de outra pessoa | 1 | 4 | 0 | nan | nan | 0 | 0 | 1/1 | 0 | 0 |
| correção explícita | 2 | 8 | 2 | 1.000 | 1.000 | 0 | 0 | 2/2 | 0 | 1 |
| "não faço questão" → "agora preciso" | 1 | 4 | 1 | 1.000 | 0.000 | 0 | 0 | 1/1 | 0 | 0 |
| nada mudou | 3 | 13 | 0 | nan | nan | 0 | 0 | 3/3 | 0 | 0 |
| sugestão do corretor | 1 | 4 | 1 | 1.000 | 0.000 | 0 | 0 | 1/1 | 1 | 0 |
| mudança sem valor | 1 | 4 | 1 | 1.000 | 0.000 | 0 | 0 | 1/1 | 0 | 0 |
| negado × substituído | 2 | 8 | 2 | 1.000 | 1.000 | 0 | 0 | 2/2 | 0 | 1 |
| duas mudanças | 1 | 5 | 2 | 1.000 | 1.000 | 0 | 0 | 1/1 | 0 | 0 |
| fácil / outros | 3 | 14 | 2 | 1.000 | 1.000 | 0 | 0 | 3/3 | 0 | 0 |

### Curva da Choice principal — piso do vencedor (mesmas respostas; informativo no teste)

| piso do vencedor | cobertura (não incerto) | erro entre decididos | mudança perdida | troca indevida | acerto total | reavaliar exato |
|---|---|---|---|---|---|---|
| 0.000 | 0.947 | 0.000 | 0 | 0 | 1.000 | 22 |
| 0.400 | 0.947 | 0.000 | 0 | 0 | 1.000 | 22 |
| 0.500 | 0.947 | 0.000 | 0 | 0 | 1.000 | 22 |
| 0.600 | 0.947 | 0.000 | 0 | 0 | 1.000 | 22 |
| 0.700 | 0.926 | 0.000 | 0 | 0 | 0.979 | 22 |
| 0.800 | 0.905 | 0.000 | 0 | 0 | 0.958 | 22 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | histórias longas (sem chamada) | falhas operacionais (→ incerto) | perguntas | p50_ms | p95_ms | tokens_por_historia | US$_total | US$_por_1000_historias | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| 22 | 0 | 0 | 0 | 434 | 404 | 485 | 12729 | 0.011761 | 0.5346 | jev-1.13.0 |

### Caso a caso (um requisito por linha)

`P` = probabilidade do vencedor da Choice; `chg/drop/open` = Nouls informativos; `ok` compara o rótulo da variante principal com o gabarito; `caro` = mudança perdida ou troca indevida; `base` = baseline. A linha `reavaliar` fecha cada história.

| id | fam | q | atributo | valor | gab | Jev | P | chg/drop/open | nouls→ | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RM-A001 | mudança indireta | q1 | bairro | Santana ou Tucuruvi | mantido | mantido | 1.00 | 0.06/0.05/0.13 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A001 | mudança indireta | q2 | elevador | indiferente | substituido → sim | substituido → sim | 1.00 | 0.93/0.06/0.14 | substituido | ✓ |  | mantido | replaced P=1.00; regra: único valor novo possível |
| RM-A001 | mudança indireta | q3 | vagas | 1 | mantido | mantido | 0.99 | 0.10/0.08/0.13 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-A001 | mudança indireta | q4 | quartos | 2 | mantido | mantido | 0.61 | 0.44/0.08/0.22 | incerto | ✓ |  | mantido | kept P=0.61 |
| RM-A001 | mudança indireta | q5 | orcamento | até R$ 520.000 | mantido | mantido | 1.00 | 0.06/0.04/0.17 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A001 |  | reavaliar |  |  | IM-01, IM-03 | IM-01, IM-03 |  |  | IM-01, IM-03 | ✓ |  | [] |  |
| RM-A002 | mudança indireta | q1 | quartos | 3 | mantido | mantido | 1.00 | 0.06/0.07/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A002 | mudança indireta | q2 | pet | sim | mantido | mantido | 1.00 | 0.08/0.11/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A002 | mudança indireta | q3 | vagas | 1 | substituido → 2 | substituido → 2 | 1.00 | 0.87/0.05/0.08 | substituido | ✓ |  | mantido | replaced P=1.00; valor '2' P=0.93 |
| RM-A002 | mudança indireta | q4 | orcamento | até R$ 780.000 | mantido | mantido | 1.00 | 0.04/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A002 |  | reavaliar |  |  | IM-02, IM-04 | IM-02, IM-04 |  |  | IM-02, IM-04 | ✓ |  | [] |  |
| RM-A003 | fácil / outros | q1 | orcamento | até R$ 3.200/mês | mantido | mantido | 1.00 | 0.04/0.05/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A003 | fácil / outros | q2 | mobilia | mobiliado | mantido | mantido | 1.00 | 0.04/0.12/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A003 | fácil / outros | q3 | bairro | Bom Fim ou Menino Deus | mantido | mantido | 1.00 | 0.04/0.07/0.04 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A003 | fácil / outros | q4 | quartos | 1 | mantido | mantido | 1.00 | 0.04/0.09/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A003 | fácil / outros | q5 | vagas | 1 | negado | negado | 0.99 | 0.96/0.94/0.07 | negado | ✓ |  | negado | denied P=0.99 |
| RM-A003 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A004 | hipótese sobre o futuro | q1 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A004 | hipótese sobre o futuro | q2 | orcamento | até R$ 700.000 | incerto | incerto | 0.97 | 0.11/0.05/0.92 | incerto | ✓ |  | mantido | uncertain P=0.97 |
| RM-A004 | hipótese sobre o futuro | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A004 | hipótese sobre o futuro | q4 | financiamento | sim | mantido | mantido | 0.94 | 0.05/0.04/0.19 | mantido | ✓ |  | mantido | kept P=0.94 |
| RM-A004 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A005 | preferência de terceiro | q1 | quartos | 3 | mantido | mantido | 1.00 | 0.06/0.03/0.16 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A005 | preferência de terceiro | q2 | vagas | 2 | mantido | mantido | 1.00 | 0.06/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A005 | preferência de terceiro | q3 | elevador | sim | mantido | mantido | 1.00 | 0.05/0.03/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A005 | preferência de terceiro | q4 | bairro | Saúde | incerto | incerto | 0.75 | 0.11/0.04/0.82 | incerto | ✓ |  | mantido | uncertain P=0.75 |
| RM-A005 | preferência de terceiro | q5 | orcamento | até R$ 950.000 | mantido | mantido | 0.98 | 0.06/0.04/0.18 | mantido | ✓ |  | mantido | kept P=0.98 |
| RM-A005 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A006 | orçamento de outra pessoa | q1 | bairro | Buritis | mantido | mantido | 1.00 | 0.07/0.05/0.19 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A006 | orçamento de outra pessoa | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.05/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A006 | orçamento de outra pessoa | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.04/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A006 | orçamento de outra pessoa | q4 | orcamento | até R$ 600.000 | mantido | mantido | 1.00 | 0.08/0.05/0.17 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A006 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A007 | preferência de terceiro | q1 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A007 | preferência de terceiro | q2 | financiamento | sim | mantido | mantido | 0.84 | 0.08/0.06/0.62 | incerto | ✓ |  | incerto | kept P=0.84 |
| RM-A007 | preferência de terceiro | q3 | orcamento | até R$ 450.000 | incerto | incerto | 0.68 | 0.07/0.05/0.84 | incerto | ✓ |  | incerto | uncertain P=0.68 |
| RM-A007 | preferência de terceiro | q4 | vagas | 1 | mantido | mantido | 1.00 | 0.05/0.04/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A007 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A008 | correção explícita | q1 | orcamento | até R$ 4.500/mês | mantido | mantido | 1.00 | 0.05/0.04/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A008 | correção explícita | q2 | quartos | 3 | mantido | mantido | 1.00 | 0.05/0.04/0.05 | mantido | ✓ |  | substituido → 1 | kept P=1.00 |
| RM-A008 | correção explícita | q3 | vagas | 2 | substituido → 1 | substituido → 1 | 1.00 | 0.96/0.05/0.04 | substituido | ✓ |  | substituido → 1 | replaced P=1.00; valor '1' P=1.00 |
| RM-A008 | correção explícita | q4 | pet | sim | mantido | mantido | 1.00 | 0.07/0.08/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A008 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A009 | correção explícita | q1 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A009 | correção explícita | q2 | elevador | sim | mantido | mantido | 1.00 | 0.05/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A009 | correção explícita | q3 | orcamento | até R$ 560.000 | mantido | mantido | 1.00 | 0.04/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A009 | correção explícita | q4 | vagas | 1 | substituido → 2 | substituido → 2 | 1.00 | 0.94/0.04/0.04 | substituido | ✓ |  | substituido → 2 | replaced P=1.00; valor '2' P=1.00 |
| RM-A009 |  | reavaliar |  |  | IM-01, IM-04 | IM-01, IM-04 |  |  | IM-01, IM-04 | ✓ |  | IM-01, IM-04 |  |
| RM-A010 | "não faço questão" → "agora preciso" | q1 | mobilia | indiferente | substituido → mobiliado | substituido → mobiliado | 1.00 | 0.95/0.05/0.04 | substituido | ✓ |  | negado | replaced P=1.00; valor 'mobiliado' P=0.99 |
| RM-A010 | "não faço questão" → "agora preciso" | q2 | quartos | 1 | mantido | mantido | 1.00 | 0.05/0.06/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A010 | "não faço questão" → "agora preciso" | q3 | bairro | Boa Viagem | mantido | mantido | 1.00 | 0.06/0.05/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A010 | "não faço questão" → "agora preciso" | q4 | orcamento | até R$ 3.800/mês | mantido | mantido | 1.00 | 0.05/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A010 |  | reavaliar |  |  | IM-02, IM-03 | IM-02, IM-03 |  |  | IM-02, IM-03 | ✓ |  | [] |  |
| RM-A011 | mudança indireta | q1 | vagas | 0 | mantido | mantido | 1.00 | 0.07/0.08/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A011 | mudança indireta | q2 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A011 | mudança indireta | q3 | orcamento | até R$ 2.600/mês | mantido | mantido | 1.00 | 0.05/0.04/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A011 | mudança indireta | q4 | pet | não | substituido → sim | substituido → sim | 1.00 | 0.94/0.28/0.09 | substituido | ✓ |  | mantido | replaced P=1.00; regra: único valor novo possível |
| RM-A011 | mudança indireta | q5 | elevador | indiferente | mantido | mantido | 1.00 | 0.07/0.08/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A011 |  | reavaliar |  |  | IM-01, IM-04 | IM-01, IM-04 |  |  | IM-01, IM-04 | ✓ |  | [] |  |
| RM-A012 | nada mudou | q1 | elevador | indiferente | mantido | mantido | 0.91 | 0.30/0.10/0.43 | incerto | ✓ |  | mantido | kept P=0.91 |
| RM-A012 | nada mudou | q2 | quartos | 2 | mantido | mantido | 1.00 | 0.07/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A012 | nada mudou | q3 | orcamento | até R$ 480.000 | mantido | mantido | 1.00 | 0.05/0.04/0.16 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A012 | nada mudou | q4 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.06/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A012 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A013 | nada mudou | q1 | vagas | 2 | mantido | mantido | 1.00 | 0.06/0.07/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A013 | nada mudou | q2 | financiamento | sim | mantido | mantido | 1.00 | 0.12/0.05/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A013 | nada mudou | q3 | orcamento | até R$ 600.000 | mantido | mantido | 1.00 | 0.13/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A013 | nada mudou | q4 | quartos | 3 | mantido | mantido | 1.00 | 0.06/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A013 | nada mudou | q5 | bairro | Cambuí ou Taquaral | mantido | mantido | 0.78 | 0.39/0.04/0.08 | incerto | ✓ |  | mantido | kept P=0.78 |
| RM-A013 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A014 | sugestão do corretor | q1 | orcamento | até R$ 700.000 | mantido | mantido | 1.00 | 0.05/0.03/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A014 | sugestão do corretor | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A014 | sugestão do corretor | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.04/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A014 | sugestão do corretor | q4 | bairro | Pompeia | substituido → Pompeia ou Lapa | substituido → Pompeia ou Lapa | 0.99 | 0.89/0.04/0.07 | substituido | ✓ |  | mantido | replaced P=0.99; valor 'Pompeia ou Lapa' P=0.74 |
| RM-A014 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A015 | mudança sem valor | q1 | bairro | Savassi ou Funcionários | mantido | mantido | 1.00 | 0.05/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A015 | mudança sem valor | q2 | pet | sim | mantido | mantido | 1.00 | 0.06/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A015 | mudança sem valor | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.04/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A015 | mudança sem valor | q4 | orcamento | até R$ 3.000/mês | incerto | incerto | 1.00 | 0.10/0.10/0.95 | incerto | ✓ |  | mantido | uncertain P=1.00 |
| RM-A015 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A016 | fácil / outros | q1 | elevador | sim | mantido | mantido | 1.00 | 0.05/0.04/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A016 | fácil / outros | q2 | orcamento | até R$ 820.000 | mantido | mantido | 1.00 | 0.04/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A016 | fácil / outros | q3 | vagas | 2 | substituido → 1 | substituido → 1 | 1.00 | 0.96/0.07/0.04 | substituido | ✓ |  | substituido → 1 | replaced P=1.00; valor '1' P=1.00 |
| RM-A016 | fácil / outros | q4 | quartos | 3 | mantido | mantido | 1.00 | 0.05/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A016 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A017 | negado × substituído | q1 | orcamento | até R$ 2.900/mês | mantido | mantido | 1.00 | 0.04/0.07/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A017 | negado × substituído | q2 | mobilia | mobiliado | negado | negado | 0.88 | 0.96/0.91/0.10 | negado | ✓ |  | negado | denied P=0.88 |
| RM-A017 | negado × substituído | q3 | quartos | 1 | mantido | mantido | 1.00 | 0.05/0.19/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A017 | negado × substituído | q4 | prazo | mudança até 11/2026 | mantido | mantido | 1.00 | 0.05/0.10/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A017 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A018 | negado × substituído | q1 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.11/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A018 | negado × substituído | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.13/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A018 | negado × substituído | q3 | financiamento | sim | negado | negado | 0.95 | 0.96/0.65/0.04 | incerto | ✓ |  | negado | denied P=0.95 |
| RM-A018 | negado × substituído | q4 | orcamento | até R$ 520.000 | mantido | mantido | 1.00 | 0.33/0.06/0.04 | incerto | ✓ |  | negado | kept P=1.00 |
| RM-A018 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A019 | duas mudanças | q1 | vagas | 2 | mantido | mantido | 1.00 | 0.06/0.08/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A019 | duas mudanças | q2 | orcamento | até R$ 900.000 | substituido → até R$ 850.000 | substituido → até R$ 850.000 | 1.00 | 0.96/0.03/0.04 | substituido | ✓ |  | substituido → até R$ 850.000 | replaced P=1.00; valor 'até R$ 850.000' P=0.98 |
| RM-A019 | duas mudanças | q3 | elevador | sim | mantido | mantido | 1.00 | 0.05/0.07/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A019 | duas mudanças | q4 | bairro | Moema | mantido | mantido | 1.00 | 0.31/0.03/0.03 | incerto | ✓ |  | mantido | kept P=1.00 |
| RM-A019 | duas mudanças | q5 | quartos | 2 | substituido → 3 | substituido → 3 | 1.00 | 0.97/0.03/0.03 | substituido | ✓ |  | substituido → 3 | replaced P=1.00; valor '3' P=0.98 |
| RM-A019 |  | reavaliar |  |  | IM-01, IM-02, IM-04 | IM-01, IM-02, IM-04 |  |  | IM-01, IM-02, IM-04 | ✓ |  | IM-01, IM-02, IM-04 |  |
| RM-A020 | nada mudou | q1 | bairro | Menino Deus ou Petrópolis | mantido | mantido | 1.00 | 0.07/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A020 | nada mudou | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A020 | nada mudou | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A020 | nada mudou | q4 | orcamento | até R$ 600.000 | mantido | mantido | 0.67 | 0.83/0.03/0.15 | substituido | ✓ |  | mantido | kept P=0.67 |
| RM-A020 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A021 | hipótese sobre o futuro | q1 | pet | sim | mantido | mantido | 1.00 | 0.09/0.05/0.14 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A021 | hipótese sobre o futuro | q2 | orcamento | até R$ 3.500/mês | mantido | mantido | 0.76 | 0.08/0.03/0.78 | incerto | ✓ |  | incerto | kept P=0.76 |
| RM-A021 | hipótese sobre o futuro | q3 | vagas | 1 | incerto | incerto | 0.94 | 0.18/0.06/0.93 | incerto | ✓ |  | incerto | uncertain P=0.94 |
| RM-A021 | hipótese sobre o futuro | q4 | quartos | 2 | mantido | mantido | 0.97 | 0.07/0.03/0.15 | mantido | ✓ |  | mantido | kept P=0.97 |
| RM-A021 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-A022 | fácil / outros | q1 | vagas | 2 | mantido | mantido | 1.00 | 0.06/0.05/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A022 | fácil / outros | q2 | quartos | 3 | mantido | mantido | 1.00 | 0.05/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A022 | fácil / outros | q3 | bairro | Casa Forte | mantido | mantido | 1.00 | 0.06/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A022 | fácil / outros | q4 | andar_baixo | indiferente | mantido | mantido | 1.00 | 0.06/0.09/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A022 | fácil / outros | q5 | orcamento | até R$ 1.200.000 | mantido | mantido | 1.00 | 0.05/0.04/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-A022 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |

## Conjunto `teste` — 44 histórias, 181 requisitos (arquivo versão 2026-10-01, autor fable); 41 difíceis

### Por requisito e por história — baseline × sempre mantido × Jev (principal e informativa) nos mesmos casos

`acerto_total` = rótulo exato nos requisitos; `acerto_mudados` = só nos que o gabarito marca `substituido`/`negado`/`incerto`. **MUDANÇA PERDIDA** = requisito substituído ou negado que saiu `mantido` (a shortlist velha continua valendo: a dor do exemplo). **TROCA INDEVIDA** = requisito mantido ou incerto (hipótese, terceiro) que saiu `substituido` ou `negado` (cadastro trocado por fala que não decide). `novo_valor certo` = entre os `substituido` acertados. `reavaliar exato` = conjunto e ordem iguais ao gabarito (conta do código). `detectou mudança` = história com algum requisito mudado em que a variante marcou algum. `sempre mantido` = o baseline trivial do LEIA-ME.

| variante | requisitos | acerto_total | acerto_mudados | MUDANÇA PERDIDA (subst/negado → mantido) | TROCA INDEVIDA (incerto/mantido → subst/negado) | hipótese/terceiro → substituido | novo_valor certo | reavaliar exato (histórias) | detectou mudança | alarme falso (história sem mudança) |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (palavras-chave) | 181 | 0.823 | 0.350 | 15/28 | 7/153 | 1/12 | 6/10 | 30/44 | 14/34 | 4/10 |
| sempre mantido | 181 | 0.779 | 0.000 | 28/28 | 0/153 | 0/12 | 0/0 | 29/44 | 0/34 | 0/10 |
| Jev choice | 181 | 0.961 | 0.900 | 0/28 | 1/153 | 0/12 | 21/21 | 42/44 | 33/34 | 0/10 |
| Jev nouls | 181 | 0.923 | 0.925 | 0/28 | 1/153 | 0/12 | 21/21 | 42/44 | 34/34 | 5/10 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 mudança perdida | 0/28 | ≤ 2 | ✓ |
| 2 troca indevida | 1/153 | ≤ 4 | ✓ |
| 3 acerto nos mudados | 0.900 (40) | ≥ 0.75 | ✓ |
| 4 reavaliar exato | 42/44 (0.955) | ≥ 0.85 | ✓ |
| 5 acerto total | 0.961 (181) | ≥ 0.9 | ✓ |
| secundário: novo_valor certo | 21/21 (1.000) | ≥ 0.85 | ✓ |
| secundário: detectou mudança | 33/34 (0.971) | ≥ 0.85 | ✓ |

**Matriz de confusão — Jev choice** (linhas = gabarito, colunas = previsto) · por classe: `mantido` 138/141 · `substituido` 21/22 · `negado` 5/6 · `incerto` 10/12

| gabarito ↓ / previsto → | mantido | substituido | negado | incerto |
|---|---|---|---|---|
| mantido | 138 | 1 | 0 | 2 |
| substituido | 0 | 21 | 0 | 1 |
| negado | 0 | 0 | 5 | 1 |
| incerto | 2 | 0 | 0 | 10 |

**Matriz de confusão — Jev nouls** (linhas = gabarito, colunas = previsto) · por classe: `mantido` 130/141 · `substituido` 21/22 · `negado` 4/6 · `incerto` 12/12

| gabarito ↓ / previsto → | mantido | substituido | negado | incerto |
|---|---|---|---|---|
| mantido | 130 | 1 | 0 | 10 |
| substituido | 0 | 21 | 0 | 1 |
| negado | 0 | 0 | 4 | 2 |
| incerto | 0 | 0 | 0 | 12 |

**Matriz de confusão — baseline (palavras-chave)** (linhas = gabarito, colunas = previsto) · por classe: `mantido` 135/141 · `substituido` 10/22 · `negado` 3/6 · `incerto` 1/12

| gabarito ↓ / previsto → | mantido | substituido | negado | incerto |
|---|---|---|---|---|
| mantido | 135 | 5 | 1 | 0 |
| substituido | 12 | 10 | 0 | 0 |
| negado | 3 | 0 | 3 | 0 |
| incerto | 10 | 1 | 0 | 1 |

### Choice de status — probabilidade do vencedor e da classe certa, por classe do gabarito

| gabarito | n | P(vencedor) mín–mediana–máx | P(classe certa) mín–mediana–máx | P(classe certa) < 0,5 |
|---|---|---|---|---|
| mantido | 141 | 0.51–1.00–1.00 | 0.11–1.00–1.00 | 3 |
| substituido | 22 | 0.95–1.00–1.00 | 0.95–1.00–1.00 | 0 |
| negado | 6 | 0.68–0.93–1.00 | 0.28–0.93–1.00 | 1 |
| incerto | 12 | 0.54–0.88–0.99 | 0.00–0.85–0.94 | 2 |

### Nouls informativos — valores por classe do gabarito (mín–máx) e acerto a 0,5

| noul | faixa | mantido | substituido | negado | incerto |
|---|---|---|---|---|---|
| changed | 0.3–0.7 | 0.04–0.82 (141) | 0.92–0.97 (22) | 0.89–0.97 (6) | 0.06–0.44 (12) |
| dropped | 0.3–0.7 | 0.02–0.38 (141) | 0.03–0.16 (22) | 0.16–0.95 (6) | 0.04–0.28 (12) |
| open | 0.3–0.7 | 0.03–0.86 (141) | 0.04–0.19 (22) | 0.04–0.23 (6) | 0.14–0.94 (12) |

### Valor novo — candidatos do código e escolha do Jev nos `substituido` do gabarito

| id | q | atributo | gabarito | n_cand | gabarito entre os candidatos | escolha (P) | saiu | ok |
|---|---|---|---|---|---|---|---|---|
| RM-T001 | q4 | elevador | sim | 0 | sim | — | sim | ✓ |
| RM-T002 | q2 | pet | sim | 0 | sim | — | sim | ✓ |
| RM-T003 | q2 | quartos | 3 | 4 | sim | 3 (0.83) | 3 | ✓ |
| RM-T005 | q1 | prazo | mudança até 10/2026 | 2 | sim | mudança até 10/2026 (0.86) | mudança até 10/2026 | ✓ |
| RM-T006 | q3 | quartos | 3 | 4 | sim | 3 (1.00) | 3 | ✓ |
| RM-T008 | q4 | bairro | Perdizes | 2 | sim | Perdizes (0.99) | Perdizes | ✓ |
| RM-T012 | q3 | vagas | 2 | 4 | sim | 2 (1.00) | 2 | ✓ |
| RM-T015 | q3 | orcamento | até R$ 850.000 | 2 | sim | até R$ 850.000 (0.95) | até R$ 850.000 | ✓ |
| RM-T019 | q3 | orcamento | até R$ 3.900/mês | 3 | sim | até R$ 3.900/mês (1.00) | até R$ 3.900/mês | ✓ |
| RM-T020 | q1 | elevador | sim | 0 | sim | — | sim | ✓ |
| RM-T021 | q5 | andar_baixo | sim | 0 | sim | — | sim | ✓ |
| RM-T022 | q3 | financiamento | sim | 0 | sim | — | sim | ✓ |
| RM-T035 | q3 | bairro | Vila Mariana ou Saúde | 2 | NÃO | none (0.75) | — | ✗ |
| RM-T036 | q3 | prazo | mudança até 11/2026 | 2 | sim | mudança até 11/2026 (0.81) | mudança até 11/2026 | ✓ |
| RM-T036 | q4 | mobilia | mobiliado | 2 | sim | mobiliado (1.00) | mobiliado | ✓ |
| RM-T037 | q3 | orcamento | até R$ 640.000 | 1 | sim | até R$ 640.000 (0.73) | até R$ 640.000 | ✓ |
| RM-T038 | q1 | elevador | sim | 0 | sim | — | sim | ✓ |
| RM-T042 | q1 | quartos | 2 | 4 | sim | 2 (0.94) | 2 | ✓ |
| RM-T042 | q3 | orcamento | até R$ 4.200/mês | 1 | sim | até R$ 4.200/mês (0.95) | até R$ 4.200/mês | ✓ |
| RM-T043 | q1 | orcamento | até R$ 750.000 | 1 | sim | até R$ 750.000 (1.00) | até R$ 750.000 | ✓ |
| RM-T043 | q4 | quartos | 2 | 4 | sim | 2 (0.97) | 2 | ✓ |
| RM-T044 | q1 | orcamento | até R$ 660.000 | 1 | sim | até R$ 660.000 (0.98) | até R$ 660.000 | ✓ |

### Por família difícil (pela `nota` do rotulador) — requisitos mudados e erros caros

| família | histórias | requisitos | mudados | acerto mudados Jev | acerto mudados baseline | mudança perdida Jev | troca indevida Jev | reavaliar exato Jev | mudança perdida baseline | troca indevida baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| mudança indireta | 6 | 26 | 6 | 1.000 | 0.167 | 0 | 1 | 5/6 | 5 | 1 |
| mudança sem valor | 4 | 16 | 4 | 0.750 | 0.000 | 0 | 0 | 4/4 | 0 | 0 |
| hipótese sobre o futuro | 2 | 8 | 2 | 1.000 | 0.500 | 0 | 0 | 2/2 | 0 | 0 |
| preferência de terceiro | 3 | 12 | 2 | 1.000 | 0.500 | 0 | 0 | 3/3 | 0 | 0 |
| orçamento de outra pessoa | 2 | 8 | 1 | 1.000 | 1.000 | 0 | 0 | 2/2 | 0 | 2 |
| correção explícita | 5 | 20 | 3 | 1.000 | 0.667 | 0 | 0 | 5/5 | 1 | 1 |
| "não faço questão" → "agora preciso" | 3 | 13 | 3 | 1.000 | 0.667 | 0 | 0 | 3/3 | 1 | 0 |
| nada mudou | 2 | 8 | 0 | nan | nan | 0 | 0 | 2/2 | 0 | 0 |
| sugestão do corretor | 3 | 12 | 1 | 1.000 | 0.000 | 0 | 0 | 3/3 | 0 | 1 |
| negado × substituído | 2 | 9 | 2 | 0.500 | 0.500 | 0 | 0 | 2/2 | 1 | 0 |
| duas mudanças | 6 | 24 | 12 | 0.833 | 0.417 | 0 | 0 | 5/6 | 5 | 0 |
| ambíguo | 2 | 8 | 2 | 1.000 | 0.000 | 0 | 0 | 2/2 | 0 | 1 |
| ironia | 1 | 4 | 0 | nan | nan | 0 | 0 | 1/1 | 0 | 1 |
| fácil / outros | 3 | 13 | 2 | 1.000 | 0.000 | 0 | 0 | 3/3 | 2 | 0 |

### Curva da Choice principal — piso do vencedor (mesmas respostas; informativo no teste)

| piso do vencedor | cobertura (não incerto) | erro entre decididos | mudança perdida | troca indevida | acerto total | reavaliar exato |
|---|---|---|---|---|---|---|
| 0.000 | 0.923 | 0.018 | 0 | 1 | 0.961 | 42 |
| 0.400 | 0.923 | 0.018 | 0 | 1 | 0.961 | 42 |
| 0.500 | 0.923 | 0.018 | 0 | 1 | 0.961 | 42 |
| 0.600 | 0.917 | 0.012 | 0 | 1 | 0.967 | 42 |
| 0.700 | 0.901 | 0.012 | 0 | 1 | 0.950 | 42 |
| 0.800 | 0.901 | 0.012 | 0 | 1 | 0.950 | 42 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | histórias longas (sem chamada) | falhas operacionais (→ incerto) | perguntas | p50_ms | p95_ms | tokens_por_historia | US$_total | US$_por_1000_historias | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| 44 | 44 | 0 | 0 | 827 | 342 | 439 | 12156 | 0.022464 | 0.5105 | jev-1.13.0 |

### Caso a caso (um requisito por linha)

`P` = probabilidade do vencedor da Choice; `chg/drop/open` = Nouls informativos; `ok` compara o rótulo da variante principal com o gabarito; `caro` = mudança perdida ou troca indevida; `base` = baseline. A linha `reavaliar` fecha cada história.

| id | fam | q | atributo | valor | gab | Jev | P | chg/drop/open | nouls→ | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RM-T001 | mudança indireta | q1 | orcamento | até R$ 4.200/mês | mantido | mantido | 1.00 | 0.05/0.04/0.14 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T001 | mudança indireta | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.10/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T001 | mudança indireta | q3 | andar_baixo | indiferente | mantido | substituido → sim | 0.88 | 0.82/0.14/0.17 | substituido | ✗ | troca indevida | negado | replaced P=0.88; regra: único valor novo possível |
| RM-T001 | mudança indireta | q4 | elevador | indiferente | substituido → sim | substituido → sim | 1.00 | 0.93/0.05/0.11 | substituido | ✓ |  | mantido | replaced P=1.00; regra: único valor novo possível |
| RM-T001 | mudança indireta | q5 | quartos | 3 | mantido | incerto | 0.51 | 0.41/0.08/0.19 | incerto | ✗ |  | mantido | replaced P=0.51; valor `none` P=0.81 |
| RM-T001 |  | reavaliar |  |  | IM-01, IM-04 | IM-01, IM-02, IM-04 |  |  | IM-01, IM-02, IM-04 | ✗ |  | [] |  |
| RM-T002 | mudança indireta | q1 | bairro | Mooca ou Tatuapé | mantido | mantido | 1.00 | 0.05/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T002 | mudança indireta | q2 | pet | não | substituido → sim | substituido → sim | 0.98 | 0.92/0.16/0.19 | substituido | ✓ |  | mantido | replaced P=0.98; regra: único valor novo possível |
| RM-T002 | mudança indireta | q3 | orcamento | até R$ 520.000 | mantido | mantido | 1.00 | 0.05/0.04/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T002 | mudança indireta | q4 | vagas | 1 | mantido | mantido | 1.00 | 0.05/0.05/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T002 | mudança indireta | q5 | quartos | 2 | mantido | mantido | 1.00 | 0.04/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T002 |  | reavaliar |  |  | IM-02, IM-04 | IM-02, IM-04 |  |  | IM-02, IM-04 | ✓ |  | [] |  |
| RM-T003 | mudança indireta | q1 | vagas | 1 | mantido | mantido | 1.00 | 0.08/0.07/0.13 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T003 | mudança indireta | q2 | quartos | 2 | substituido → 3 | substituido → 3 | 0.99 | 0.92/0.03/0.09 | substituido | ✓ |  | substituido → 1 | replaced P=0.99; valor '3' P=0.83 |
| RM-T003 | mudança indireta | q3 | elevador | sim | mantido | mantido | 1.00 | 0.06/0.07/0.12 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T003 | mudança indireta | q4 | orcamento | até R$ 640.000 | mantido | mantido | 1.00 | 0.09/0.03/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T003 |  | reavaliar |  |  | IM-02, IM-04 | IM-02, IM-04 |  |  | IM-02, IM-04 | ✓ |  | [] |  |
| RM-T004 | mudança sem valor | q1 | quartos | 2 | incerto | mantido | 0.54 | 0.06/0.05/0.33 | incerto | ✗ |  | mantido | kept P=0.54 |
| RM-T004 | mudança sem valor | q2 | orcamento | até R$ 3.400/mês | mantido | mantido | 0.80 | 0.05/0.04/0.33 | incerto | ✓ |  | mantido | kept P=0.80 |
| RM-T004 | mudança sem valor | q3 | bairro | Graças ou Casa Forte | mantido | mantido | 0.92 | 0.06/0.04/0.19 | mantido | ✓ |  | mantido | kept P=0.92 |
| RM-T004 | mudança sem valor | q4 | pet | sim | mantido | mantido | 0.95 | 0.07/0.05/0.15 | mantido | ✓ |  | mantido | kept P=0.95 |
| RM-T004 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T005 | mudança indireta | q1 | prazo | mudança até 01/2027 | substituido → mudança até 10/2026 | substituido → mudança até 10/2026 | 1.00 | 0.93/0.07/0.08 | substituido | ✓ |  | mantido | replaced P=1.00; valor 'mudança até 10/2026' P=0.86 |
| RM-T005 | mudança indireta | q2 | mobilia | indiferente | mantido | mantido | 1.00 | 0.06/0.10/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T005 | mudança indireta | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T005 | mudança indireta | q4 | orcamento | até R$ 3.000/mês | mantido | mantido | 1.00 | 0.04/0.04/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T005 |  | reavaliar |  |  | IM-02, IM-03 | IM-02, IM-03 |  |  | IM-02, IM-03 | ✓ |  | [] |  |
| RM-T006 | mudança indireta | q1 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.08/0.13 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T006 | mudança indireta | q2 | orcamento | até R$ 890.000 | mantido | mantido | 1.00 | 0.04/0.05/0.12 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T006 | mudança indireta | q3 | quartos | 2 | substituido → 3 | substituido → 3 | 1.00 | 0.95/0.05/0.05 | substituido | ✓ |  | mantido | replaced P=1.00; valor '3' P=1.00 |
| RM-T006 | mudança indireta | q4 | bairro | Perdizes ou Pompeia | mantido | mantido | 1.00 | 0.05/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T006 |  | reavaliar |  |  | IM-01, IM-04 | IM-01, IM-04 |  |  | IM-01, IM-04 | ✓ |  | [] |  |
| RM-T007 | mudança sem valor | q1 | quartos | 1 | mantido | mantido | 1.00 | 0.06/0.06/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T007 | mudança sem valor | q2 | mobilia | sem mobília | incerto | incerto | 0.93 | 0.20/0.28/0.91 | incerto | ✓ |  | mantido | uncertain P=0.93 |
| RM-T007 | mudança sem valor | q3 | orcamento | até R$ 2.400/mês | mantido | incerto | 0.68 | 0.09/0.07/0.81 | incerto | ✗ |  | mantido | uncertain P=0.68 |
| RM-T007 | mudança sem valor | q4 | bairro | Portão ou Água Verde | mantido | mantido | 1.00 | 0.06/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T007 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T008 | fácil / outros | q1 | vagas | 2 | mantido | mantido | 1.00 | 0.09/0.11/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T008 | fácil / outros | q2 | quartos | 3 | mantido | mantido | 1.00 | 0.06/0.06/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T008 | fácil / outros | q3 | orcamento | até R$ 1.300.000 | mantido | mantido | 1.00 | 0.05/0.05/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T008 | fácil / outros | q4 | bairro | Pinheiros ou Vila Madalena | substituido → Perdizes | substituido → Perdizes | 1.00 | 0.96/0.04/0.05 | substituido | ✓ |  | mantido | replaced P=1.00; valor 'Perdizes' P=0.99 |
| RM-T008 |  | reavaliar |  |  | IM-01, IM-02, IM-03, IM-04 | IM-01, IM-02, IM-03, IM-04 |  |  | IM-01, IM-02, IM-03, IM-04 | ✓ |  | [] |  |
| RM-T009 | hipótese sobre o futuro | q1 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.04/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T009 | hipótese sobre o futuro | q2 | orcamento | até R$ 580.000 | mantido | mantido | 0.61 | 0.07/0.04/0.86 | incerto | ✓ |  | mantido | kept P=0.61 |
| RM-T009 | hipótese sobre o futuro | q3 | quartos | 2 | incerto | incerto | 0.82 | 0.23/0.06/0.91 | incerto | ✓ |  | incerto | uncertain P=0.82 |
| RM-T009 | hipótese sobre o futuro | q4 | financiamento | sim | mantido | mantido | 0.99 | 0.05/0.05/0.14 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-T009 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T010 | hipótese sobre o futuro | q1 | quartos | 2 | mantido | mantido | 0.94 | 0.06/0.03/0.28 | mantido | ✓ |  | mantido | kept P=0.94 |
| RM-T010 | hipótese sobre o futuro | q2 | bairro | Santana | mantido | mantido | 0.99 | 0.04/0.03/0.13 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-T010 | hipótese sobre o futuro | q3 | elevador | indiferente | incerto | incerto | 0.84 | 0.13/0.10/0.94 | incerto | ✓ |  | mantido | uncertain P=0.84 |
| RM-T010 | hipótese sobre o futuro | q4 | orcamento | até R$ 450.000 | mantido | mantido | 0.98 | 0.04/0.03/0.16 | mantido | ✓ |  | mantido | kept P=0.98 |
| RM-T010 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T011 | preferência de terceiro | q1 | orcamento | até R$ 610.000 | mantido | mantido | 1.00 | 0.04/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T011 | preferência de terceiro | q2 | quartos | 2 | mantido | mantido | 1.00 | 0.22/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T011 | preferência de terceiro | q3 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.08/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T011 | preferência de terceiro | q4 | bairro | Vila Mariana ou Saúde | mantido | mantido | 1.00 | 0.05/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T011 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T012 | preferência de terceiro | q1 | elevador | sim | mantido | mantido | 1.00 | 0.06/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T012 | preferência de terceiro | q2 | orcamento | até R$ 980.000 | mantido | mantido | 1.00 | 0.04/0.04/0.12 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T012 | preferência de terceiro | q3 | vagas | 1 | substituido → 2 | substituido → 2 | 1.00 | 0.97/0.03/0.04 | substituido | ✓ |  | substituido → 2 | replaced P=1.00; valor '2' P=1.00 |
| RM-T012 | preferência de terceiro | q4 | quartos | 3 | mantido | mantido | 1.00 | 0.05/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T012 |  | reavaliar |  |  | IM-02, IM-04 | IM-02, IM-04 |  |  | IM-02, IM-04 | ✓ |  | IM-02, IM-04 |  |
| RM-T013 | preferência de terceiro | q1 | quartos | 2 | mantido | mantido | 0.99 | 0.06/0.03/0.08 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-T013 | preferência de terceiro | q2 | pet | sim | mantido | mantido | 1.00 | 0.10/0.03/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T013 | preferência de terceiro | q3 | orcamento | até R$ 3.300/mês | mantido | mantido | 1.00 | 0.06/0.03/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T013 | preferência de terceiro | q4 | andar_baixo | sim | incerto | incerto | 0.69 | 0.22/0.06/0.81 | incerto | ✓ |  | mantido | uncertain P=0.69 |
| RM-T013 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T014 | orçamento de outra pessoa | q1 | orcamento | até R$ 700.000 | mantido | mantido | 1.00 | 0.08/0.05/0.35 | incerto | ✓ |  | substituido → até R$ 2.000 | kept P=1.00 |
| RM-T014 | orçamento de outra pessoa | q2 | bairro | Cambuí | mantido | mantido | 1.00 | 0.06/0.04/0.13 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T014 | orçamento de outra pessoa | q3 | vagas | 2 | mantido | mantido | 1.00 | 0.07/0.07/0.13 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T014 | orçamento de outra pessoa | q4 | quartos | 3 | mantido | mantido | 1.00 | 0.08/0.05/0.15 | mantido | ✓ |  | substituido → 2 | kept P=1.00 |
| RM-T014 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | IM-01, IM-02, IM-03, IM-04 |  |
| RM-T015 | orçamento de outra pessoa | q1 | quartos | 3 | mantido | mantido | 1.00 | 0.05/0.07/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T015 | orçamento de outra pessoa | q2 | financiamento | sim | mantido | mantido | 0.90 | 0.10/0.10/0.15 | mantido | ✓ |  | mantido | kept P=0.90 |
| RM-T015 | orçamento de outra pessoa | q3 | orcamento | até R$ 700.000 | substituido → até R$ 850.000 | substituido → até R$ 850.000 | 1.00 | 0.94/0.07/0.07 | substituido | ✓ |  | substituido → até R$ 150.000 | replaced P=1.00; valor 'até R$ 850.000' P=0.95 |
| RM-T015 | orçamento de outra pessoa | q4 | vagas | 2 | mantido | mantido | 1.00 | 0.05/0.08/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T015 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | IM-01, IM-02, IM-03, IM-04 |  |
| RM-T016 | correção explícita | q1 | bairro | Butantã | mantido | mantido | 1.00 | 0.06/0.03/0.04 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T016 | correção explícita | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.04/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T016 | correção explícita | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.03/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T016 | correção explícita | q4 | orcamento | até R$ 650.000 | mantido | mantido | 1.00 | 0.49/0.02/0.04 | incerto | ✓ |  | substituido → até R$ 700.000 | kept P=1.00 |
| RM-T016 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T017 | correção explícita | q1 | orcamento | até R$ 5.000/mês | mantido | mantido | 1.00 | 0.17/0.04/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T017 | correção explícita | q2 | pet | sim | mantido | mantido | 1.00 | 0.15/0.05/0.04 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T017 | correção explícita | q3 | quartos | 3 | mantido | mantido | 1.00 | 0.39/0.03/0.03 | incerto | ✓ |  | mantido | kept P=1.00 |
| RM-T017 | correção explícita | q4 | vagas | 2 | mantido | mantido | 0.99 | 0.14/0.04/0.04 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-T017 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T018 | correção explícita | q1 | elevador | sim | negado | negado | 0.94 | 0.94/0.94/0.06 | negado | ✓ |  | negado | denied P=0.94 |
| RM-T018 | correção explícita | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.12/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T018 | correção explícita | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.09/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T018 | correção explícita | q4 | orcamento | até R$ 380.000 | mantido | mantido | 1.00 | 0.06/0.06/0.12 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T018 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T019 | correção explícita | q1 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T019 | correção explícita | q2 | bairro | Petrópolis ou Bom Fim | mantido | mantido | 1.00 | 0.05/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T019 | correção explícita | q3 | orcamento | até R$ 3.500/mês | substituido → até R$ 3.900/mês | substituido → até R$ 3.900/mês | 1.00 | 0.96/0.03/0.06 | substituido | ✓ |  | substituido → até R$ 4.000/mês | replaced P=1.00; valor 'até R$ 3.900/mês' P=1.00 |
| RM-T019 | correção explícita | q4 | vagas | 1 | mantido | mantido | 1.00 | 0.05/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T019 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T020 | "não faço questão" → "agora preciso" | q1 | elevador | indiferente | substituido → sim | substituido → sim | 1.00 | 0.96/0.04/0.04 | substituido | ✓ |  | substituido → sim | replaced P=1.00; regra: único valor novo possível |
| RM-T020 | "não faço questão" → "agora preciso" | q2 | quartos | 1 | mantido | mantido | 1.00 | 0.06/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T020 | "não faço questão" → "agora preciso" | q3 | vagas | 0 | mantido | mantido | 0.99 | 0.07/0.18/0.10 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-T020 | "não faço questão" → "agora preciso" | q4 | orcamento | até R$ 2.200/mês | mantido | mantido | 1.00 | 0.05/0.04/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T020 |  | reavaliar |  |  | IM-02, IM-04 | IM-02, IM-04 |  |  | IM-02, IM-04 | ✓ |  | IM-02, IM-04 |  |
| RM-T021 | "não faço questão" → "agora preciso" | q1 | vagas | 2 | mantido | mantido | 1.00 | 0.06/0.09/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T021 | "não faço questão" → "agora preciso" | q2 | quartos | 3 | mantido | mantido | 1.00 | 0.05/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T021 | "não faço questão" → "agora preciso" | q3 | elevador | sim | mantido | mantido | 0.60 | 0.35/0.12/0.24 | incerto | ✓ |  | mantido | kept P=0.60 |
| RM-T021 | "não faço questão" → "agora preciso" | q4 | orcamento | até R$ 1.100.000 | mantido | mantido | 1.00 | 0.05/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T021 | "não faço questão" → "agora preciso" | q5 | andar_baixo | indiferente | substituido → sim | substituido → sim | 1.00 | 0.96/0.04/0.05 | substituido | ✓ |  | substituido → sim | replaced P=1.00; regra: único valor novo possível |
| RM-T021 |  | reavaliar |  |  | IM-01, IM-03 | IM-01, IM-03 |  |  | IM-01, IM-03 | ✓ |  | IM-01, IM-03 |  |
| RM-T022 | "não faço questão" → "agora preciso" | q1 | quartos | 3 | mantido | mantido | 1.00 | 0.05/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T022 | "não faço questão" → "agora preciso" | q2 | vagas | 2 | mantido | mantido | 1.00 | 0.06/0.07/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T022 | "não faço questão" → "agora preciso" | q3 | financiamento | não | substituido → sim | substituido → sim | 1.00 | 0.95/0.09/0.08 | substituido | ✓ |  | mantido | replaced P=1.00; regra: único valor novo possível |
| RM-T022 | "não faço questão" → "agora preciso" | q4 | orcamento | até R$ 750.000 | mantido | mantido | 0.99 | 0.05/0.05/0.16 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-T022 |  | reavaliar |  |  | IM-02, IM-04 | IM-02, IM-04 |  |  | IM-02, IM-04 | ✓ |  | [] |  |
| RM-T023 | nada mudou | q1 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T023 | nada mudou | q2 | bairro | Lapa | mantido | mantido | 1.00 | 0.06/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T023 | nada mudou | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T023 | nada mudou | q4 | orcamento | até R$ 500.000 | mantido | mantido | 1.00 | 0.19/0.02/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T023 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T024 | sugestão do corretor | q1 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.06/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T024 | sugestão do corretor | q2 | orcamento | até R$ 2.800/mês | mantido | mantido | 1.00 | 0.11/0.02/0.04 | mantido | ✓ |  | substituido → até R$ 800/mês | kept P=1.00 |
| RM-T024 | sugestão do corretor | q3 | pet | sim | mantido | mantido | 1.00 | 0.07/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T024 | sugestão do corretor | q4 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.04/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T024 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | IM-01, IM-02, IM-03, IM-04 |  |
| RM-T025 | nada mudou | q1 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.08/0.12 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T025 | nada mudou | q2 | orcamento | até R$ 430.000 | mantido | mantido | 1.00 | 0.05/0.04/0.13 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T025 | nada mudou | q3 | elevador | indiferente | mantido | mantido | 0.97 | 0.35/0.38/0.19 | incerto | ✓ |  | mantido | kept P=0.97 |
| RM-T025 | nada mudou | q4 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.05/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T025 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T026 | fácil / outros | q1 | vagas | 2 | mantido | mantido | 1.00 | 0.06/0.05/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T026 | fácil / outros | q2 | elevador | sim | mantido | mantido | 1.00 | 0.04/0.03/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T026 | fácil / outros | q3 | orcamento | até R$ 950.000 | mantido | mantido | 1.00 | 0.05/0.04/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T026 | fácil / outros | q4 | bairro | Batel | mantido | mantido | 1.00 | 0.05/0.03/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T026 | fácil / outros | q5 | quartos | 3 | mantido | mantido | 1.00 | 0.04/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T026 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T027 | sugestão do corretor | q1 | orcamento | até R$ 800.000 | incerto | incerto | 0.89 | 0.08/0.04/0.90 | incerto | ✓ |  | mantido | uncertain P=0.89 |
| RM-T027 | sugestão do corretor | q2 | bairro | Funcionários | mantido | mantido | 0.95 | 0.06/0.03/0.13 | mantido | ✓ |  | mantido | kept P=0.95 |
| RM-T027 | sugestão do corretor | q3 | vagas | 2 | mantido | mantido | 1.00 | 0.06/0.04/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T027 | sugestão do corretor | q4 | quartos | 3 | mantido | mantido | 1.00 | 0.05/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T027 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T028 | sugestão do corretor | q1 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.05/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T028 | sugestão do corretor | q2 | mobilia | mobiliado | mantido | mantido | 1.00 | 0.06/0.03/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T028 | sugestão do corretor | q3 | orcamento | até R$ 3.000/mês | mantido | mantido | 1.00 | 0.05/0.03/0.12 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T028 | sugestão do corretor | q4 | bairro | Boa Viagem | mantido | mantido | 1.00 | 0.06/0.04/0.64 | incerto | ✓ |  | mantido | kept P=1.00 |
| RM-T028 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T029 | mudança sem valor | q1 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.05/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T029 | mudança sem valor | q2 | quartos | 2 | incerto | incerto | 0.75 | 0.07/0.06/0.91 | incerto | ✓ |  | mantido | uncertain P=0.75 |
| RM-T029 | mudança sem valor | q3 | elevador | sim | mantido | mantido | 1.00 | 0.05/0.04/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T029 | mudança sem valor | q4 | orcamento | até R$ 720.000 | mantido | mantido | 1.00 | 0.05/0.04/0.13 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T029 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T030 | mudança sem valor | q1 | pet | sim | mantido | mantido | 1.00 | 0.06/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T030 | mudança sem valor | q2 | prazo | mudança até 02/2027 | incerto | incerto | 0.94 | 0.13/0.09/0.91 | incerto | ✓ |  | mantido | uncertain P=0.94 |
| RM-T030 | mudança sem valor | q3 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T030 | mudança sem valor | q4 | orcamento | até R$ 2.900/mês | mantido | mantido | 0.99 | 0.05/0.04/0.10 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-T030 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T031 | negado × substituído | q1 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.06/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T031 | negado × substituído | q2 | bairro | Moema | negado | negado | 0.68 | 0.95/0.68/0.21 | incerto | ✓ |  | negado | denied P=0.68 |
| RM-T031 | negado × substituído | q3 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.11/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T031 | negado × substituído | q4 | orcamento | até R$ 780.000 | mantido | mantido | 1.00 | 0.09/0.08/0.24 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T031 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T032 | fácil / outros | q1 | orcamento | até R$ 2.300/mês | mantido | mantido | 1.00 | 0.05/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T032 | fácil / outros | q2 | quartos | 1 | mantido | mantido | 1.00 | 0.05/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T032 | fácil / outros | q3 | mobilia | indiferente | mantido | mantido | 1.00 | 0.06/0.13/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T032 | fácil / outros | q4 | prazo | mudança até 11/2026 | negado | negado | 0.80 | 0.95/0.94/0.23 | negado | ✓ |  | mantido | denied P=0.80 |
| RM-T032 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T033 | negado × substituído | q1 | andar_baixo | sim | negado | incerto | 0.72 | 0.95/0.16/0.07 | incerto | ✗ |  | mantido | replaced P=0.72; já era `sim`: não há valor novo |
| RM-T033 | negado × substituído | q2 | quartos | 2 | mantido | mantido | 1.00 | 0.06/0.07/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T033 | negado × substituído | q3 | orcamento | até R$ 560.000 | mantido | mantido | 1.00 | 0.05/0.05/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T033 | negado × substituído | q4 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.10/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T033 | negado × substituído | q5 | elevador | sim | mantido | mantido | 0.90 | 0.08/0.07/0.12 | mantido | ✓ |  | mantido | kept P=0.90 |
| RM-T033 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T034 | mudança indireta | q1 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.12/0.13 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T034 | mudança indireta | q2 | quartos | 3 | mantido | mantido | 0.99 | 0.29/0.05/0.05 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-T034 | mudança indireta | q3 | elevador | sim | negado | negado | 0.93 | 0.89/0.90/0.20 | negado | ✓ |  | mantido | denied P=0.93 |
| RM-T034 | mudança indireta | q4 | orcamento | até R$ 690.000 | mantido | mantido | 1.00 | 0.06/0.08/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T034 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T035 | duas mudanças | q1 | orcamento | até R$ 540.000 | mantido | mantido | 1.00 | 0.05/0.05/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T035 | duas mudanças | q2 | vagas | 1 | negado | negado | 1.00 | 0.97/0.95/0.04 | negado | ✓ |  | negado | denied P=1.00 |
| RM-T035 | duas mudanças | q3 | bairro | Tatuapé ou Vila Mariana | substituido → Vila Mariana ou Saúde | incerto | 1.00 | 0.96/0.06/0.04 | incerto | ✗ |  | mantido | replaced P=1.00; valor `none` P=0.75 |
| RM-T035 | duas mudanças | q4 | quartos | 2 | mantido | mantido | 1.00 | 0.04/0.07/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T035 |  | reavaliar |  |  | IM-01, IM-03 | [] |  |  | [] | ✗ |  | [] |  |
| RM-T036 | duas mudanças | q1 | quartos | 1 | mantido | mantido | 1.00 | 0.06/0.05/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T036 | duas mudanças | q2 | orcamento | até R$ 3.000/mês | mantido | mantido | 1.00 | 0.05/0.05/0.14 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T036 | duas mudanças | q3 | prazo | mudança até 01/2027 | substituido → mudança até 11/2026 | substituido → mudança até 11/2026 | 1.00 | 0.93/0.08/0.08 | substituido | ✓ |  | mantido | replaced P=1.00; valor 'mudança até 11/2026' P=0.81 |
| RM-T036 | duas mudanças | q4 | mobilia | indiferente | substituido → mobiliado | substituido → mobiliado | 1.00 | 0.96/0.05/0.04 | substituido | ✓ |  | mantido | replaced P=1.00; valor 'mobiliado' P=1.00 |
| RM-T036 |  | reavaliar |  |  | IM-02, IM-03 | IM-02, IM-03 |  |  | IM-02, IM-03 | ✓ |  | [] |  |
| RM-T037 | duas mudanças | q1 | pet | não | incerto | incerto | 0.88 | 0.10/0.12/0.93 | incerto | ✓ |  | mantido | uncertain P=0.88 |
| RM-T037 | duas mudanças | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.07/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T037 | duas mudanças | q3 | orcamento | até R$ 600.000 | substituido → até R$ 640.000 | substituido → até R$ 640.000 | 0.95 | 0.93/0.06/0.12 | substituido | ✓ |  | mantido | replaced P=0.95; valor 'até R$ 640.000' P=0.73 |
| RM-T037 | duas mudanças | q4 | quartos | 2 | mantido | mantido | 1.00 | 0.08/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T037 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T038 | duas mudanças | q1 | elevador | indiferente | substituido → sim | substituido → sim | 1.00 | 0.94/0.04/0.08 | substituido | ✓ |  | mantido | replaced P=1.00; regra: único valor novo possível |
| RM-T038 | duas mudanças | q2 | vagas | 1 | mantido | mantido | 1.00 | 0.09/0.07/0.15 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T038 | duas mudanças | q3 | orcamento | até R$ 2.600/mês | incerto | mantido | 0.99 | 0.44/0.04/0.14 | incerto | ✗ |  | mantido | kept P=0.99 |
| RM-T038 | duas mudanças | q4 | quartos | 2 | mantido | mantido | 0.82 | 0.15/0.06/0.17 | mantido | ✓ |  | mantido | kept P=0.82 |
| RM-T038 |  | reavaliar |  |  | IM-01, IM-04 | IM-01, IM-04 |  |  | IM-01, IM-04 | ✓ |  | [] |  |
| RM-T039 | ambíguo | q1 | vagas | 1 | incerto | incerto | 0.94 | 0.19/0.05/0.91 | incerto | ✓ |  | substituido → 2 | uncertain P=0.94 |
| RM-T039 | ambíguo | q2 | bairro | Perdizes | mantido | mantido | 1.00 | 0.05/0.04/0.07 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T039 | ambíguo | q3 | quartos | 3 | mantido | mantido | 1.00 | 0.05/0.03/0.09 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T039 | ambíguo | q4 | orcamento | até R$ 870.000 | mantido | mantido | 1.00 | 0.04/0.04/0.10 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T039 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | IM-01, IM-03 |  |
| RM-T040 | ambíguo | q1 | orcamento | até R$ 3.800/mês | mantido | mantido | 1.00 | 0.05/0.03/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T040 | ambíguo | q2 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.04/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T040 | ambíguo | q3 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.06/0.12 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T040 | ambíguo | q4 | bairro | Savassi | incerto | incerto | 0.85 | 0.42/0.08/0.90 | incerto | ✓ |  | mantido | uncertain P=0.85 |
| RM-T040 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T041 | ironia | q1 | financiamento | sim | mantido | mantido | 1.00 | 0.06/0.07/0.13 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T041 | ironia | q2 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.06/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T041 | ironia | q3 | orcamento | até R$ 420.000 | mantido | mantido | 1.00 | 0.08/0.16/0.19 | mantido | ✓ |  | substituido → até R$ 2.000.000 | kept P=1.00 |
| RM-T041 | ironia | q4 | vagas | 1 | mantido | mantido | 1.00 | 0.06/0.08/0.08 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T041 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
| RM-T042 | duas mudanças | q1 | quartos | 1 | substituido → 2 | substituido → 2 | 1.00 | 0.96/0.04/0.04 | substituido | ✓ |  | substituido → 2 | replaced P=1.00; valor '2' P=0.94 |
| RM-T042 | duas mudanças | q2 | mobilia | mobiliado | mantido | mantido | 1.00 | 0.29/0.03/0.03 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T042 | duas mudanças | q3 | orcamento | até R$ 2.500/mês | substituido → até R$ 4.200/mês | substituido → até R$ 4.200/mês | 1.00 | 0.97/0.05/0.05 | substituido | ✓ |  | substituido → até R$ 4.000/mês | replaced P=1.00; valor 'até R$ 4.200/mês' P=0.95 |
| RM-T042 | duas mudanças | q4 | vagas | 0 | mantido | mantido | 1.00 | 0.08/0.17/0.15 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T042 |  | reavaliar |  |  | IM-02, IM-03 | IM-02, IM-03 |  |  | IM-02, IM-03 | ✓ |  | IM-02, IM-03 |  |
| RM-T043 | duas mudanças | q1 | orcamento | até R$ 900.000 | substituido → até R$ 750.000 | substituido → até R$ 750.000 | 1.00 | 0.96/0.03/0.04 | substituido | ✓ |  | substituido → até R$ 750.000 | replaced P=1.00; valor 'até R$ 750.000' P=1.00 |
| RM-T043 | duas mudanças | q2 | elevador | sim | mantido | mantido | 1.00 | 0.06/0.05/0.11 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T043 | duas mudanças | q3 | vagas | 2 | mantido | mantido | 0.99 | 0.08/0.09/0.10 | mantido | ✓ |  | mantido | kept P=0.99 |
| RM-T043 | duas mudanças | q4 | quartos | 3 | substituido → 2 | substituido → 2 | 1.00 | 0.95/0.05/0.06 | substituido | ✓ |  | substituido → 2 | replaced P=1.00; valor '2' P=0.97 |
| RM-T043 |  | reavaliar |  |  | IM-02, IM-03 | IM-02, IM-03 |  |  | IM-02, IM-03 | ✓ |  | IM-02, IM-03 |  |
| RM-T044 | correção explícita | q1 | orcamento | até R$ 600.000 | substituido → até R$ 660.000 | substituido → até R$ 660.000 | 1.00 | 0.95/0.04/0.06 | substituido | ✓ |  | mantido | replaced P=1.00; valor 'até R$ 660.000' P=0.98 |
| RM-T044 | correção explícita | q2 | quartos | 2 | mantido | mantido | 1.00 | 0.05/0.05/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T044 | correção explícita | q3 | vagas | 1 | mantido | mantido | 1.00 | 0.07/0.08/0.05 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T044 | correção explícita | q4 | financiamento | sim | mantido | mantido | 1.00 | 0.05/0.07/0.06 | mantido | ✓ |  | mantido | kept P=1.00 |
| RM-T044 |  | reavaliar |  |  | [] | [] |  |  | [] | ✓ |  | [] |  |
