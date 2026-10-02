# Rascunho — triagem-de-documentos (encanamento)

## Conjunto `rascunho` — 5 condições (4 semânticas) × 44 documentos (arquivo versão 2026-10-02, autor fable); 0 difíceis; 38 verdadeiros e 0 indecidíveis no gabarito

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Total (micro, sobre os documentos decidíveis de todas as condições) — desenho A × desenho B × baseline

P/R/F1 sobre os decidíveis que o sistema DECIDIU; `humano` = decidíveis mandados a `indecidivel` (fora de P/R/F1). **PERDIDAS** = verdadeiro do gabarito que saiu `falso`. **FP NEGADA/REVOGADA** = falso marcado `verdadeiro` em condição das famílias negada/revogada (cláusula negada ou revogada lida como presente — o erro caro). `prova certa` = entre os verdadeiros das condições semânticas, a seção apontada (A: maior `establishes`; B: Choice) é a do gabarito. Desenho padrão: `mapa`; faixas {'establishes': (0.2, 0.8), 'revokes': (0.2, 0.8), 'holds': (0.2, 0.8)}; `deferred` ≥ 0.7.

| desenho | decidíveis | decididas | P | R | F1 | humano (decidíveis) | V a humano | PERDIDAS (V → falso) | FP | FP NEGADA/REVOGADA | prova certa (V semânticos) | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A: mapa por seção (padrão) | 220 | 214 | 1.000 | 1.000 | 1.000 | 6 (0.027) | 0 | 0/38 | 0 | 0 | 30/30 (1.000) | 0/0 (V: 0) | 0 |
| B: documento inteiro | 220 | 217 | 1.000 | 1.000 | 1.000 | 3 (0.014) | 1 | 0/38 | 0 | 0 | 30/30 (1.000) | 0/0 (V: 0) | 0 |
| baseline palavras-chave | 220 | 220 | 0.400 | 1.000 | 0.571 | 0 (0.000) | 0 | 0/38 | 57 | 0 | 26/30 (0.867) | 0/0 (V: 0) | 0 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 F1 (decididas) | 1.000 (baseline 0.571) | ≥ 0.9 e ≥ 0.771 | ✓ |
| 2 perdidas (V → falso) | 0/38 (0.000) | ≤ 0.05 | ✓ |
| 3 FP negada/revogada | 0 | ≤ 1 | ✓ |
| 4 humano (decidíveis) | 6/220 (0.027) | ≤ 0.06 | ✓ |
| secundário: seção que prova | 30/30 (1.000) | ≥ 0.8 | ✓ |
| secundário: indecidíveis → humano | 0/0 | ≥ 0.5 | ✓ |
| secundário: falhas operacionais | 0 | 0 | ✓ |

### Desenho A × desenho B (só condições semânticas; mesmos documentos, pareado)

| n (decidíveis) | F1 A | F1 B | F1 A − B | A certo, B errado | B certo, A errado | os dois errados | humano A / B | perdidas A / B | FP A / B | prova certa A / B |
|---|---|---|---|---|---|---|---|---|---|---|
| 176 | 1.000 | 1.000 | 0.000 | 1 | 4 | 2 | 6 / 3 | 0 / 0 | 0 / 0 | 30/30 / 30/30 |

### Por condição

`tipo` = semântica (Jev) ou numérica (código, igual nos dois desenhos); `V/I` = verdadeiros / indecidíveis do gabarito; `hum` = a humano; `perd` = perdidas; `prova` = seção que prova certa; `base` = palavras-chave (radicais entre colchetes).

| id | família | tipo | V/I | A P | A R | A F1 | A hum | A perd | A FP | A prova | A I→hum | B P | B R | B F1 | B hum | B perd | B FP | B prova | B I→hum | base F1 | base FP | base perd | radicais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TD-R01 | fácil | semântica | 8/0 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 8/8 | 0/0 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 8/8 | 0/0 | 0.308 | 36 | 0 | [reaju, igp] |
| TD-R02 | fácil | semântica | 5/0 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 5/5 | 0/0 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 5/5 | 0/0 | 0.714 | 4 | 0 | [aprov, obra, refor, areas, comun] |
| TD-R03 | fácil | numérica garantia_meses >= 12 | 8/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 0 | 0 | — |
| TD-R04 | fácil | semântica | 7/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 7/7 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 7/7 | 0/0 | 0.583 | 10 | 0 | [garan, prest, fiado] |
| TD-R05 | fácil | semântica | 10/0 | 1.000 | 1.000 | 1.000 | 3 | 0 | 0 | 10/10 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 10/10 | 0/0 | 0.741 | 7 | 0 | [confi, sigil, infor] |

### Por família difícil (pela `nota` do rotulador)

| família | condições | F1 A | F1 B | F1 base | perdidas A/B/base | FP A/B/base | humano A/B | prova A/B |
|---|---|---|---|---|---|---|---|---|
| fácil | 5 | 1.000 | 1.000 | 0.571 | 0/0/0 | 0/0/57 | 6/3 | 30/30 · 30/30 |

### Onde os Nouls caem, por gabarito (só documentos que foram ao Jev)

A: `establishes` da seção que prova (verdadeiros) ou o MÁXIMO entre as seções (falsos/indecidíveis); `revokes` = máximo no documento; B: `holds`. `deferred` = máximo no documento (A) ou o do documento (B).

| gabarito | desenho | n | mín | p10 | p50 | p90 | máx | ≤ 0,2 | 0,2–0,8 | ≥ 0,8 | revokes p50 / ≥ 0,8 | deferred p50 / ≥ 0,7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| verdadeiro | mapa | 30 | 0.970 | 0.980 | 0.980 | 0.990 | 0.990 | 0 | 0 | 30 | 0.03 / 0 | 0.15 / 0 |
| verdadeiro | inteiro | 30 | 0.600 | 0.950 | 0.980 | 0.990 | 0.990 | 0 | 1 | 29 | — | 0.03 / 0 |
| falso | mapa | 146 | 0.010 | 0.020 | 0.020 | 0.060 | 0.980 | 140 | 5 | 1 | 0.03 / 1 | 0.13 / 1 |
| falso | inteiro | 146 | 0.010 | 0.010 | 0.020 | 0.040 | 0.740 | 144 | 2 | 0 | — | 0.07 / 0 |
| indecidivel | mapa | 0 | nan | nan | nan | nan | nan | 0 | 0 | 0 | — | — |
| indecidivel | inteiro | 0 | nan | nan | nan | nan | nan | 0 | 0 | 0 | — | — |

### Cobertura × erro por faixa (mesmas respostas, outra faixa; `deferred` fixo)

| desenho | faixa | cobertura (decididas/decidíveis) | erro entre decididas | F1 | humano | perdidas | FP | FP neg/rev | I → humano |
|---|---|---|---|---|---|---|---|---|---|
| mapa | atual (perguntas.py) | 0.973 | 0.000 | 1.000 | 6 | 0 | 0 | 0 | 0/0 |
| mapa | 0.5–0.5 | 0.995 | 0.000 | 1.000 | 1 | 0 | 0 | 0 | 0/0 |
| mapa | 0.4–0.6 | 0.986 | 0.000 | 1.000 | 3 | 0 | 0 | 0 | 0/0 |
| mapa | 0.3–0.7 | 0.973 | 0.000 | 1.000 | 6 | 0 | 0 | 0 | 0/0 |
| mapa | 0.2–0.8 | 0.973 | 0.000 | 1.000 | 6 | 0 | 0 | 0 | 0/0 |
| mapa | 0.1–0.9 | 0.964 | 0.000 | 1.000 | 8 | 0 | 0 | 0 | 0/0 |
| inteiro | atual (perguntas.py) | 0.986 | 0.000 | 1.000 | 3 | 0 | 0 | 0 | 0/0 |
| inteiro | 0.5–0.5 | 1.000 | 0.009 | 0.974 | 0 | 0 | 2 | 0 | 0/0 |
| inteiro | 0.4–0.6 | 0.995 | 0.005 | 0.987 | 1 | 0 | 1 | 0 | 0/0 |
| inteiro | 0.3–0.7 | 0.991 | 0.005 | 0.987 | 2 | 0 | 1 | 0 | 0/0 |
| inteiro | 0.2–0.8 | 0.986 | 0.000 | 1.000 | 3 | 0 | 0 | 0 | 0/0 |
| inteiro | 0.1–0.9 | 0.977 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 0/0 |

### Custo e latência por desenho (medidos na chamada real; do cache também)

| desenho | documentos avaliados (cond × doc) | sem chamada (numérica) | requisições | novas (não cache) | falhas | p50_ms / p95_ms por requisição | tokens por requisição | tokens por documento (p50) | ms por documento serial p50 / p95 | ms por documento paralelo p50 / p95 | US$ total | US$ por mil documentos avaliados (semânticos) | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mapa | 220 | 44 | 1264 | 1068 | 0 | 258 / 327 | 1467 | 10354 | 1924 / 2257 | 312 / 454 | 0.077879 | 0.4425 | jev-1.13.0 |
| inteiro | 220 | 44 | 176 | 176 | 0 | 284 / 362 | 2704 | 2746 | 284 / 362 | 284 / 362 | 0.019987 | 0.1136 | jev-1.13.0 |

### Caso a caso — erros, documentos mandados a humano e indecidíveis do gabarito (em qualquer desenho)

`A` = mapa (motivo = passos da redução; `prova` = seção de maior `establishes`); `B` = inteiro (`holds`; prova = Choice); `gab prova` = `secao_que_prova`.

| cond | doc | gab | gab prova | A | A ok | A prova | A motivo | B | B ok | B prova | B motivo | base |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TD-R01 | L05 | verdadeiro | L05-s3 | verdadeiro | ✓ | L05-s3 | L05-s3 institui 0.99 | indecidivel | ✗ | L05-s3 | holds 0.60; prova L05-s3 0.86 | verdadeiro |
| TD-R01 | L08 | falso | — | indecidivel | ✗ | L08-s3 | L08-s3 deixa em aberto 0.72 | falso | ✓ | — | holds 0.03; prova none 0.97 | verdadeiro |
| TD-R02 | A08 | falso | — | indecidivel | ✗ | A08-s5 | A08-s5 institui? 0.38 | indecidivel | ✗ | — | holds 0.52; prova none 0.62 | falso |
| TD-R02 | A10 | falso | — | indecidivel | ✗ | A10-s6 | A10-s6 institui? 0.33 | indecidivel | ✗ | A10-s6 | holds 0.74; prova A10-s6 0.77 | verdadeiro |
| TD-R05 | A02 | falso | — | indecidivel | ✗ | A02-s6 | A02-s6 institui? 0.48 | falso | ✓ | — | holds 0.06; prova none 0.98 | falso |
| TD-R05 | A04 | falso | — | indecidivel | ✗ | A04-s5 | A04-s5 institui? 0.41 | falso | ✓ | — | holds 0.08; prova none 0.94 | falso |
| TD-R05 | A08 | falso | — | indecidivel | ✗ | A08-s6 | A08-s6 institui? 0.34 | falso | ✓ | — | holds 0.09; prova none 0.93 | falso |
