# Resultados — triagem-de-documentos

Gerado por `run.py` em 2026-10-02 (modo `gravado`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; parte numérica, states, redução, decisão e baseline: `triagem.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Tetos: {'secao': 4000, 'documento': 25000} caracteres (acima → indecidivel, sem chamada). Orçamento: 4500 requisições no teste.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (12 condições × 44 documentos), desenho padrão `mapa` (A) com a política acima; **1_f1**: F1 do desenho padrão sobre os decidíveis decididos ≥ 0,90 e ≥ F1 do baseline (palavras-chave por seção) + 0,20; **2_perdidas**: documento verdadeiro do gabarito que saiu `falso` ≤ 5% dos verdadeiros; **3_negada_revogada**: documento falso marcado `verdadeiro` em condição das famílias negada/revogada ≤ 1; **4_humano**: decidíveis mandados a humano (`indecidivel`) ≤ 6%; **secundario_nao_decide**: seção que prova certa ≥ 80% dos verdadeiros das condições semânticas; indecidíveis do gabarito que foram a humano ≥ 50%; falha operacional = 0; desenho B medido ao lado, com n; **se_falhar**: 1 falhando = palavra-chave basta ou o Jev não lê a condição; 2 ou 3 = o mapa perde ou inverte o que deveria achar (não serve sem mudança); 4 = custa humano demais

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-02T01:00:43-03:00): `perguntas.py` sha256 606ab91b92da6114… · `triagem.py` sha256 5f9862eb82116c92… · `run.py` sha256 aeacd4e816bfcc72… · `dados/documentos.json` sha256 a88bf9ddaf8c4c45… · `dados/condicoes_teste.json` sha256 0898f3fc86bc1c52…

## Lado a lado

| conjunto | desenho | decidíveis | decididas | P | R | F1 | humano (decidíveis) | V a humano | PERDIDAS (V → falso) | FP | FP NEGADA/REVOGADA | prova certa (V semânticos) | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | A: mapa por seção | 264 | 262 | 1.000 | 1.000 | 1.000 | 2 (0.008) | 0 | 0/31 | 0 | 0 | 22/22 (1.000) | 0/0 (V: 0) | 0 |
| ajuste | B: documento inteiro | 264 | 259 | 1.000 | 1.000 | 1.000 | 5 (0.019) | 2 | 0/31 | 0 | 0 | 22/22 (1.000) | 0/0 (V: 0) | 0 |
| ajuste | baseline palavras-chave | 264 | 264 | 0.484 | 1.000 | 0.653 | 0 (0.000) | 0 | 0/31 | 33 | 23 | 22/22 (1.000) | 0/0 (V: 0) | 0 |
| teste | A: mapa por seção | 524 | 522 | 1.000 | 1.000 | 1.000 | 2 (0.004) | 2 | 0/58 | 0 | 0 | 45/45 (1.000) | 3/4 (V: 1) | 0 |
| teste | B: documento inteiro | 524 | 521 | 1.000 | 1.000 | 1.000 | 3 (0.006) | 3 | 0/58 | 0 | 0 | 45/45 (1.000) | 3/4 (V: 1) | 0 |
| teste | baseline palavras-chave | 524 | 524 | 0.454 | 0.845 | 0.590 | 0 (0.000) | 0 | 9/58 | 59 | 22 | 35/45 (0.778) | 0/4 (V: 4) | 0 |

| conjunto | desenho | condições | semânticas | difíceis | documentos | requisições | p50_ms | p95_ms | tokens por requisição | US$ por mil documentos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | mapa | 6 | 4 | 4 | 44 | 1264 | 259 | 333 | 1782 | 0.5374 | jev-1.13.0 |
| ajuste | inteiro | 6 | 4 | 4 | 44 | 176 | 281 | 351 | 3064 | 0.1287 | jev-1.13.0 |
| teste | mapa | 12 | 9 | 8 | 44 | 2844 | 257 | 317 | 1642 | 0.4954 | jev-1.13.0 |
| teste | inteiro | 12 | 9 | 8 | 44 | 396 | 283 | 339 | 2909 | 0.1222 | jev-1.13.0 |

## Conjunto `ajuste` — 6 condições (4 semânticas) × 44 documentos (arquivo versão 2026-10-02b, autor fable); 4 difíceis; 31 verdadeiros e 0 indecidíveis no gabarito

### Total (micro, sobre os documentos decidíveis de todas as condições) — desenho A × desenho B × baseline

P/R/F1 sobre os decidíveis que o sistema DECIDIU; `humano` = decidíveis mandados a `indecidivel` (fora de P/R/F1). **PERDIDAS** = verdadeiro do gabarito que saiu `falso`. **FP NEGADA/REVOGADA** = falso marcado `verdadeiro` em condição das famílias negada/revogada (cláusula negada ou revogada lida como presente — o erro caro). `prova certa` = entre os verdadeiros das condições semânticas, a seção apontada (A: maior `establishes`; B: Choice) é a do gabarito. Desenho padrão: `mapa`; faixas {'establishes': (0.3, 0.8), 'revokes': (0.4, 0.8), 'holds': (0.3, 0.8)}; `deferred` ≥ 0.7.

| desenho | decidíveis | decididas | P | R | F1 | humano (decidíveis) | V a humano | PERDIDAS (V → falso) | FP | FP NEGADA/REVOGADA | prova certa (V semânticos) | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A: mapa por seção (padrão) | 264 | 262 | 1.000 | 1.000 | 1.000 | 2 (0.008) | 0 | 0/31 | 0 | 0 | 22/22 (1.000) | 0/0 (V: 0) | 0 |
| B: documento inteiro | 264 | 259 | 1.000 | 1.000 | 1.000 | 5 (0.019) | 2 | 0/31 | 0 | 0 | 22/22 (1.000) | 0/0 (V: 0) | 0 |
| baseline palavras-chave | 264 | 264 | 0.484 | 1.000 | 0.653 | 0 (0.000) | 0 | 0/31 | 33 | 23 | 22/22 (1.000) | 0/0 (V: 0) | 0 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 F1 (decididas) | 1.000 (baseline 0.653) | ≥ 0.9 e ≥ 0.853 | ✓ |
| 2 perdidas (V → falso) | 0/31 (0.000) | ≤ 0.05 | ✓ |
| 3 FP negada/revogada | 0 | ≤ 1 | ✓ |
| 4 humano (decidíveis) | 2/264 (0.008) | ≤ 0.06 | ✓ |
| secundário: seção que prova | 22/22 (1.000) | ≥ 0.8 | ✓ |
| secundário: indecidíveis → humano | 0/0 | ≥ 0.5 | ✓ |
| secundário: falhas operacionais | 0 | 0 | ✓ |

### Desenho A × desenho B (só condições semânticas; mesmos documentos, pareado)

| n (decidíveis) | F1 A | F1 B | F1 A − B | A certo, B errado | B certo, A errado | os dois errados | humano A / B | perdidas A / B | FP A / B | prova certa A / B |
|---|---|---|---|---|---|---|---|---|---|---|
| 176 | 1.000 | 1.000 | 0.000 | 3 | 0 | 2 | 2 / 5 | 0 / 0 | 0 / 0 | 22/22 / 22/22 |

### Por condição

`tipo` = semântica (Jev) ou numérica (código, igual nos dois desenhos); `V/I` = verdadeiros / indecidíveis do gabarito; `hum` = a humano; `perd` = perdidas; `prova` = seção que prova certa; `base` = palavras-chave (radicais entre colchetes).

| id | família | tipo | V/I | A P | A R | A F1 | A hum | A perd | A FP | A prova | A I→hum | B P | B R | B F1 | B hum | B perd | B FP | B prova | B I→hum | base F1 | base FP | base perd | radicais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TD-A01 | negada | semântica | 6/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 6/6 | 0/0 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 6/6 | 0/0 | 0.632 | 7 | 0 | [multa, locat, devol, antec, resci] |
| TD-A02 | fácil | numérica multa_alugueis > 2 | 4/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 0 | 0 | — |
| TD-A03 | duas seções | semântica | 5/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 5/5 | 0/0 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 5/5 | 0/0 | 0.625 | 6 | 0 | [conce, desco, preco, condi, exclu, pagam, vista] |
| TD-A04 | termo só no título | semântica | 5/0 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 5/5 | 0/0 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 5/5 | 0/0 | 0.714 | 4 | 0 | [exclu, restr, contr, atend, conco] |
| TD-A05 | fácil | numérica prazo_meses < 12 | 5/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 0 | 0 | — |
| TD-A06 | negada | semântica | 6/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 6/6 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 6/6 | 0/0 | 0.429 | 16 | 0 | [aprov, reaju, taxa] |

### Por família difícil (pela `nota` do rotulador)

| família | condições | F1 A | F1 B | F1 base | perdidas A/B/base | FP A/B/base | humano A/B | prova A/B |
|---|---|---|---|---|---|---|---|---|
| negada | 2 | 1.000 | 1.000 | 0.511 | 0/0/0 | 0/0/23 | 0/2 | 12/12 · 12/12 |
| fácil | 2 | 1.000 | 1.000 | 1.000 | 0/0/0 | 0/0/0 | 0/0 | 0/0 · 0/0 |
| duas seções | 1 | 1.000 | 1.000 | 0.625 | 0/0/0 | 0/0/6 | 0/1 | 5/5 · 5/5 |
| termo só no título | 1 | 1.000 | 1.000 | 0.714 | 0/0/0 | 0/0/4 | 2/2 | 5/5 · 5/5 |

### Onde os Nouls caem, por gabarito (só documentos que foram ao Jev)

A: `establishes` da seção que prova (verdadeiros) ou o MÁXIMO entre as seções (falsos/indecidíveis); `revokes` = máximo no documento; B: `holds`. `deferred` = máximo no documento (A) ou o do documento (B).

| gabarito | desenho | n | mín | p10 | p50 | p90 | máx | ≤ 0,2 | 0,2–0,8 | ≥ 0,8 | revokes p50 / ≥ 0,8 | deferred p50 / ≥ 0,7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| verdadeiro | mapa | 22 | 0.970 | 0.980 | 0.980 | 0.980 | 0.980 | 0 | 0 | 22 | 0.03 / 0 | 0.13 / 0 |
| verdadeiro | inteiro | 22 | 0.510 | 0.880 | 0.970 | 0.980 | 0.980 | 0 | 2 | 20 | — | 0.03 / 0 |
| falso | mapa | 154 | 0.010 | 0.020 | 0.030 | 0.080 | 0.980 | 149 | 4 | 1 | 0.03 / 2 | 0.10 / 0 |
| falso | inteiro | 154 | 0.010 | 0.020 | 0.030 | 0.050 | 0.630 | 151 | 3 | 0 | — | 0.06 / 0 |
| indecidivel | mapa | 0 | nan | nan | nan | nan | nan | 0 | 0 | 0 | — | — |
| indecidivel | inteiro | 0 | nan | nan | nan | nan | nan | 0 | 0 | 0 | — | — |

### Cobertura × erro por faixa (mesmas respostas, outra faixa; `deferred` fixo)

| desenho | faixa | cobertura (decididas/decidíveis) | erro entre decididas | F1 | humano | perdidas | FP | FP neg/rev | I → humano |
|---|---|---|---|---|---|---|---|---|---|
| mapa | atual (perguntas.py) | 0.992 | 0.000 | 1.000 | 2 | 0 | 0 | 0 | 0/0 |
| mapa | 0.5–0.5 | 1.000 | 0.008 | 0.969 | 0 | 0 | 2 | 0 | 0/0 |
| mapa | 0.4–0.6 | 1.000 | 0.008 | 0.969 | 0 | 0 | 2 | 0 | 0/0 |
| mapa | 0.3–0.7 | 0.996 | 0.008 | 0.968 | 1 | 0 | 2 | 0 | 0/0 |
| mapa | 0.2–0.8 | 0.981 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 0/0 |
| mapa | 0.1–0.9 | 0.947 | 0.000 | 1.000 | 14 | 0 | 0 | 0 | 0/0 |
| inteiro | atual (perguntas.py) | 0.981 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 0/0 |
| inteiro | 0.5–0.5 | 1.000 | 0.008 | 0.969 | 0 | 0 | 2 | 0 | 0/0 |
| inteiro | 0.4–0.6 | 0.989 | 0.004 | 0.983 | 3 | 0 | 1 | 0 | 0/0 |
| inteiro | 0.3–0.7 | 0.981 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 0/0 |
| inteiro | 0.2–0.8 | 0.981 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 0/0 |
| inteiro | 0.1–0.9 | 0.966 | 0.000 | 1.000 | 9 | 0 | 0 | 0 | 0/0 |

### Custo e latência por desenho (medidos na chamada real; do cache também)

| desenho | documentos avaliados (cond × doc) | sem chamada (numérica) | requisições | novas (não cache) | falhas | p50_ms / p95_ms por requisição | tokens por requisição | tokens por documento (p50) | ms por documento serial p50 / p95 | ms por documento, estimativa idealizada = máx das seções (chamadas em sequência) p50 / p95 | US$ total | US$ por mil documentos avaliados (semânticos) | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mapa | 264 | 88 | 1264 | 0 | 0 | 259 / 333 | 1782 | 12124 | 1957 / 2258 | 309 / 601 | 0.094588 | 0.5374 | jev-1.13.0 |
| inteiro | 264 | 88 | 176 | 0 | 0 | 281 / 351 | 3064 | 2888 | 281 / 351 | 281 / 351 | 0.022650 | 0.1287 | jev-1.13.0 |

### Caso a caso — erros, documentos mandados a humano e indecidíveis do gabarito (em qualquer desenho)

`A` = mapa (motivo = passos da redução; `prova` = seção de maior `establishes`); `B` = inteiro (`holds`; prova = Choice); `gab prova` = `secao_que_prova`.

| cond | doc | gab | gab prova | A | A ok | A prova | A motivo | B | B ok | B prova | B motivo | base |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TD-A01 | L02 | verdadeiro | L02-s5 | verdadeiro | ✓ | L02-s5 | L02-s5 institui 0.98 | indecidivel | ✗ | L02-s5 | holds 0.53; prova L02-s5 0.87 | verdadeiro |
| TD-A01 | L11 | verdadeiro | L11-s5 | verdadeiro | ✓ | L11-s5 | L11-s5 institui 0.98 | indecidivel | ✗ | L11-s5 | holds 0.51; prova L11-s5 0.89 | verdadeiro |
| TD-A03 | P05 | falso | — | falso | ✓ | P05-s3 | cláusula 0 verdadeiro: P05-s3 institui 0.96; cláusula 1 falso: nada institui | indecidivel | ✗ | — | cláusulas 0.92, 0.39; prova none 0.51 | verdadeiro |
| TD-A04 | S04 | falso | — | indecidivel | ✗ | S04-s6 | S04-s6 institui? 0.73 | indecidivel | ✗ | S04-s6 | holds 0.59; prova S04-s6 0.72 | falso |
| TD-A04 | S09 | falso | — | indecidivel | ✗ | S09-s6 | S09-s6 institui? 0.73 | indecidivel | ✗ | S09-s6 | holds 0.63; prova S09-s6 0.75 | falso |

## Conjunto `teste` — 12 condições (9 semânticas) × 44 documentos (arquivo versão 2026-10-02b, autor fable); 8 difíceis; 58 verdadeiros e 4 indecidíveis no gabarito

### Total (micro, sobre os documentos decidíveis de todas as condições) — desenho A × desenho B × baseline

P/R/F1 sobre os decidíveis que o sistema DECIDIU; `humano` = decidíveis mandados a `indecidivel` (fora de P/R/F1). **PERDIDAS** = verdadeiro do gabarito que saiu `falso`. **FP NEGADA/REVOGADA** = falso marcado `verdadeiro` em condição das famílias negada/revogada (cláusula negada ou revogada lida como presente — o erro caro). `prova certa` = entre os verdadeiros das condições semânticas, a seção apontada (A: maior `establishes`; B: Choice) é a do gabarito. Desenho padrão: `mapa`; faixas {'establishes': (0.3, 0.8), 'revokes': (0.4, 0.8), 'holds': (0.3, 0.8)}; `deferred` ≥ 0.7.

| desenho | decidíveis | decididas | P | R | F1 | humano (decidíveis) | V a humano | PERDIDAS (V → falso) | FP | FP NEGADA/REVOGADA | prova certa (V semânticos) | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A: mapa por seção (padrão) | 524 | 522 | 1.000 | 1.000 | 1.000 | 2 (0.004) | 2 | 0/58 | 0 | 0 | 45/45 (1.000) | 3/4 (V: 1) | 0 |
| B: documento inteiro | 524 | 521 | 1.000 | 1.000 | 1.000 | 3 (0.006) | 3 | 0/58 | 0 | 0 | 45/45 (1.000) | 3/4 (V: 1) | 0 |
| baseline palavras-chave | 524 | 524 | 0.454 | 0.845 | 0.590 | 0 (0.000) | 0 | 9/58 | 59 | 22 | 35/45 (0.778) | 0/4 (V: 4) | 0 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 F1 (decididas) | 1.000 (baseline 0.590) | ≥ 0.9 e ≥ 0.790 | ✓ |
| 2 perdidas (V → falso) | 0/58 (0.000) | ≤ 0.05 | ✓ |
| 3 FP negada/revogada | 0 | ≤ 1 | ✓ |
| 4 humano (decidíveis) | 2/524 (0.004) | ≤ 0.06 | ✓ |
| secundário: seção que prova | 45/45 (1.000) | ≥ 0.8 | ✓ |
| secundário: indecidíveis → humano | 3/4 | ≥ 0.5 | ✓ |
| secundário: falhas operacionais | 0 | 0 | ✓ |

### Desenho A × desenho B (só condições semânticas; mesmos documentos, pareado)

| n (decidíveis) | F1 A | F1 B | F1 A − B | A certo, B errado | B certo, A errado | os dois errados | humano A / B | perdidas A / B | FP A / B | prova certa A / B |
|---|---|---|---|---|---|---|---|---|---|---|
| 392 | 1.000 | 1.000 | 0.000 | 3 | 2 | 0 | 2 / 3 | 0 / 0 | 0 / 0 | 45/45 / 45/45 |

### Por condição

`tipo` = semântica (Jev) ou numérica (código, igual nos dois desenhos); `V/I` = verdadeiros / indecidíveis do gabarito; `hum` = a humano; `perd` = perdidas; `prova` = seção que prova certa; `base` = palavras-chave (radicais entre colchetes).

| id | família | tipo | V/I | A P | A R | A F1 | A hum | A perd | A FP | A prova | A I→hum | B P | B R | B F1 | B hum | B perd | B FP | B prova | B I→hum | base F1 | base FP | base perd | radicais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TD-T01 | negada | semântica | 5/1 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 5/5 | 0/1 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 5/5 | 0/1 | 0.667 | 5 | 0 | [aprov, insta, camer, monit] |
| TD-T02 | revogada | semântica | 6/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 6/6 | 0/0 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 6/6 | 0/0 | 0.462 | 4 | 3 | [renov, autom, fim, prazo, nenhu, manif] |
| TD-T03 | duas seções | semântica | 4/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 4/4 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 4/4 | 0/0 | 0.800 | 2 | 0 | [garan, prest, fiado, respo, esten, ate, efeti, devol, chave, inclu, prorr] |
| TD-T04 | termo só no título | semântica | 4/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 4/4 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 4/4 | 0/0 | 0.276 | 21 | 0 | [soluc, contr, arbit] |
| TD-T05 | seção parecida | semântica | 5/1 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 5/5 | 1/1 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 5/5 | 1/1 | 0.833 | 2 | 0 | [desco, multa, penal, descu, nivei, sla] |
| TD-T06 | fácil | numérica reajuste_percentual >= 10 | 4/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 0 | 0 | — |
| TD-T07 | fácil | numérica validade_dias < 15 | 4/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 0 | 0 | — |
| TD-T08 | negada | semântica | 5/2 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 5/5 | 2/2 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 5/5 | 2/2 | 0.444 | 9 | 1 | [autor, prese, anima, estim, locad] |
| TD-T09 | sem a cláusula | semântica | 4/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 4/4 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 4/4 | 0/0 | 0.533 | 7 | 0 | [inclu, trein, equip, clien, escop] |
| TD-T10 | fácil | numérica quorum_percentual < 50 | 5/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 0 | 0 | — |
| TD-T11 | revogada | semântica | 5/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 5/5 | 0/0 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 5/5 | 0/0 | 0.714 | 4 | 0 | [proib, sublo] |
| TD-T12 | fácil | semântica | 7/0 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 7/7 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 7/7 | 0/0 | 0.286 | 5 | 5 | [aprov, conta, admin, ainda, ressa] |

### Por família difícil (pela `nota` do rotulador)

| família | condições | F1 A | F1 B | F1 base | perdidas A/B/base | FP A/B/base | humano A/B | prova A/B |
|---|---|---|---|---|---|---|---|---|
| negada | 2 | 1.000 | 1.000 | 0.545 | 0/0/1 | 0/0/14 | 1/0 | 10/10 · 10/10 |
| revogada | 2 | 1.000 | 1.000 | 0.593 | 0/0/3 | 0/0/8 | 0/3 | 11/11 · 11/11 |
| duas seções | 1 | 1.000 | 1.000 | 0.800 | 0/0/0 | 0/0/2 | 0/0 | 4/4 · 4/4 |
| termo só no título | 1 | 1.000 | 1.000 | 0.276 | 0/0/0 | 0/0/21 | 0/0 | 4/4 · 4/4 |
| seção parecida | 1 | 1.000 | 1.000 | 0.833 | 0/0/0 | 0/0/2 | 0/0 | 5/5 · 5/5 |
| fácil | 4 | 1.000 | 1.000 | 0.750 | 0/0/5 | 0/0/5 | 1/0 | 7/7 · 7/7 |
| sem a cláusula | 1 | 1.000 | 1.000 | 0.533 | 0/0/0 | 0/0/7 | 0/0 | 4/4 · 4/4 |

### Onde os Nouls caem, por gabarito (só documentos que foram ao Jev)

A: `establishes` da seção que prova (verdadeiros) ou o MÁXIMO entre as seções (falsos/indecidíveis); `revokes` = máximo no documento; B: `holds`. `deferred` = máximo no documento (A) ou o do documento (B).

| gabarito | desenho | n | mín | p10 | p50 | p90 | máx | ≤ 0,2 | 0,2–0,8 | ≥ 0,8 | revokes p50 / ≥ 0,8 | deferred p50 / ≥ 0,7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| verdadeiro | mapa | 45 | 0.770 | 0.890 | 0.970 | 0.980 | 0.990 | 0 | 1 | 44 | 0.03 / 0 | 0.12 / 0 |
| verdadeiro | inteiro | 45 | 0.540 | 0.830 | 0.970 | 0.980 | 0.990 | 0 | 3 | 42 | — | 0.03 / 0 |
| falso | mapa | 347 | 0.010 | 0.010 | 0.020 | 0.050 | 0.980 | 341 | 3 | 3 | 0.03 / 3 | 0.09 / 0 |
| falso | inteiro | 347 | 0.010 | 0.010 | 0.020 | 0.050 | 0.180 | 347 | 0 | 0 | — | 0.06 / 0 |
| indecidivel | mapa | 4 | 0.030 | 0.030 | 0.360 | 0.870 | 0.870 | 2 | 1 | 1 | 0.04 / 0 | 0.82 / 3 |
| indecidivel | inteiro | 4 | 0.040 | 0.040 | 0.270 | 0.850 | 0.850 | 2 | 1 | 1 | — | 0.84 / 3 |

### Cobertura × erro por faixa (mesmas respostas, outra faixa; `deferred` fixo)

| desenho | faixa | cobertura (decididas/decidíveis) | erro entre decididas | F1 | humano | perdidas | FP | FP neg/rev | I → humano |
|---|---|---|---|---|---|---|---|---|---|
| mapa | atual (perguntas.py) | 0.996 | 0.000 | 1.000 | 2 | 0 | 0 | 0 | 3/4 |
| mapa | 0.5–0.5 | 1.000 | 0.002 | 0.991 | 0 | 1 | 0 | 0 | 3/4 |
| mapa | 0.4–0.6 | 0.998 | 0.000 | 1.000 | 1 | 0 | 0 | 0 | 3/4 |
| mapa | 0.3–0.7 | 0.996 | 0.000 | 1.000 | 2 | 0 | 0 | 0 | 3/4 |
| mapa | 0.2–0.8 | 0.990 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 3/4 |
| mapa | 0.1–0.9 | 0.968 | 0.000 | 1.000 | 17 | 0 | 0 | 0 | 4/4 |
| inteiro | atual (perguntas.py) | 0.994 | 0.000 | 1.000 | 3 | 0 | 0 | 0 | 3/4 |
| inteiro | 0.5–0.5 | 1.000 | 0.000 | 1.000 | 0 | 0 | 0 | 0 | 3/4 |
| inteiro | 0.4–0.6 | 0.998 | 0.000 | 1.000 | 1 | 0 | 0 | 0 | 3/4 |
| inteiro | 0.3–0.7 | 0.994 | 0.000 | 1.000 | 3 | 0 | 0 | 0 | 3/4 |
| inteiro | 0.2–0.8 | 0.994 | 0.000 | 1.000 | 3 | 0 | 0 | 0 | 3/4 |
| inteiro | 0.1–0.9 | 0.979 | 0.000 | 1.000 | 11 | 0 | 0 | 0 | 4/4 |

### Custo e latência por desenho (medidos na chamada real; do cache também)

| desenho | documentos avaliados (cond × doc) | sem chamada (numérica) | requisições | novas (não cache) | falhas | p50_ms / p95_ms por requisição | tokens por requisição | tokens por documento (p50) | ms por documento serial p50 / p95 | ms por documento, estimativa idealizada = máx das seções (chamadas em sequência) p50 / p95 | US$ total | US$ por mil documentos avaliados (semânticos) | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mapa | 528 | 132 | 2844 | 0 | 0 | 257 / 317 | 1642 | 10811 | 1909 / 2236 | 299 / 436 | 0.196173 | 0.4954 | jev-1.13.0 |
| inteiro | 528 | 132 | 396 | 0 | 0 | 283 / 339 | 2909 | 2851 | 283 / 339 | 283 / 339 | 0.048389 | 0.1222 | jev-1.13.0 |

### Caso a caso — erros, documentos mandados a humano e indecidíveis do gabarito (em qualquer desenho)

`A` = mapa (motivo = passos da redução; `prova` = seção de maior `establishes`); `B` = inteiro (`holds`; prova = Choice); `gab prova` = `secao_que_prova`.

| cond | doc | gab | gab prova | A | A ok | A prova | A motivo | B | B ok | B prova | B motivo | base |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TD-T01 | A05 | verdadeiro | A05-s5 | indecidivel | ✗ | A05-s5 | A05-s5 institui 0.97; A05-s6 revoga? 0.55 | verdadeiro | ✓ | A05-s5 | holds 0.95; prova A05-s5 0.93 | verdadeiro |
| TD-T01 | A09 | indecidivel | — | verdadeiro | ✗ | A09-s5 | A09-s5 institui 0.87 | verdadeiro | ✗ | A09-s5 | holds 0.85; prova A09-s5 0.99 | verdadeiro |
| TD-T02 | L05 | verdadeiro | L05-s2 | verdadeiro | ✓ | L05-s2 | L05-s2 institui 0.98 | indecidivel | ✗ | L05-s2 | holds 0.61; prova L05-s2 0.83 | verdadeiro |
| TD-T05 | S05 | indecidivel | — | indecidivel | ✓ | S05-s6 | nenhuma seção institui (máx 0.10 em S05-s6); S05-s6 deixa em aberto 0.72 | indecidivel | ✓ | — | holds 0.16, deferred 0.72: deixa em aberto; prova none 0.78 | verdadeiro |
| TD-T08 | L08 | indecidivel | — | indecidivel | ✓ | L08-s6 | L08-s6 institui? 0.36 | indecidivel | ✓ | L08-s6 | holds 0.27, deferred 0.89: deixa em aberto; prova L08-s6 0.54 | verdadeiro |
| TD-T08 | A08 | indecidivel | — | indecidivel | ✓ | A08-s4 | nenhuma seção institui (máx 0.03 em A08-s4); A08-s4 deixa em aberto 0.82 | indecidivel | ✓ | — | holds 0.04, deferred 0.84: deixa em aberto; prova none 0.93 | verdadeiro |
| TD-T11 | L05 | verdadeiro | L05-s6 | verdadeiro | ✓ | L05-s6 | L05-s6 institui 0.89 | indecidivel | ✗ | L05-s6 | holds 0.54; prova L05-s6 0.86 | verdadeiro |
| TD-T11 | L11 | verdadeiro | L11-s6 | verdadeiro | ✓ | L11-s6 | L11-s6 institui 0.89 | indecidivel | ✗ | L11-s6 | holds 0.62; prova L11-s6 0.90 | verdadeiro |
| TD-T12 | A05 | verdadeiro | A05-s2 | indecidivel | ✗ | A05-s2 | A05-s2 institui? 0.77 | verdadeiro | ✓ | A05-s2 | holds 0.88; prova A05-s2 0.62 | falso |
