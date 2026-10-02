# Resultados — triagem-de-documentos

Gerado por `run.py` em 2026-10-02 (modo `auto`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; parte numérica, states, redução, decisão e baseline: `triagem.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Tetos: {'secao': 4000, 'documento': 25000} caracteres (acima → indecidivel, sem chamada). Orçamento: 4500 requisições no teste.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (12 condições × 44 documentos), desenho padrão `mapa` (A) com a política acima; **1_f1**: F1 do desenho padrão sobre os decidíveis decididos ≥ 0,90 e ≥ F1 do baseline (palavras-chave por seção) + 0,20; **2_perdidas**: documento verdadeiro do gabarito que saiu `falso` ≤ 5% dos verdadeiros; **3_negada_revogada**: documento falso marcado `verdadeiro` em condição das famílias negada/revogada ≤ 1; **4_humano**: decidíveis mandados a humano (`indecidivel`) ≤ 6%; **secundario_nao_decide**: seção que prova certa ≥ 80% dos verdadeiros das condições semânticas; indecidíveis do gabarito que foram a humano ≥ 50%; falha operacional = 0; desenho B medido ao lado, com n; **se_falhar**: 1 falhando = palavra-chave basta ou o Jev não lê a condição; 2 ou 3 = o mapa perde ou inverte o que deveria achar (não serve sem mudança); 4 = custa humano demais

Versão em afinação (NÃO congelada): `perguntas.py` sha256 09b759c95790c518… · `triagem.py` sha256 2d67ca35b8bcfa46… · `run.py` sha256 6b3e3d8d49e352b4… · `dados/documentos.json` sha256 a88bf9ddaf8c4c45… · `dados/condicoes_teste.json` sha256 7a3e17812df7f004…

## Lado a lado

| conjunto | desenho | decidíveis | decididas | P | R | F1 | humano (decidíveis) | V a humano | PERDIDAS (V → falso) | FP | FP NEGADA/REVOGADA | prova certa (V semânticos) | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | A: mapa por seção | 264 | 259 | 1.000 | 1.000 | 1.000 | 5 (0.019) | 1 | 0/31 | 0 | 0 | 22/22 (1.000) | 0/0 (V: 0) | 0 |
| ajuste | B: documento inteiro | 264 | 259 | 1.000 | 1.000 | 1.000 | 5 (0.019) | 2 | 0/31 | 0 | 0 | 22/22 (1.000) | 0/0 (V: 0) | 0 |
| ajuste | baseline palavras-chave | 264 | 264 | 0.492 | 1.000 | 0.660 | 0 (0.000) | 0 | 0/31 | 32 | 23 | 22/22 (1.000) | 0/0 (V: 0) | 0 |

| conjunto | desenho | condições | semânticas | difíceis | documentos | requisições | p50_ms | p95_ms | tokens por requisição | US$ por mil documentos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | mapa | 6 | 4 | 4 | 44 | 1264 | 254 | 333 | 1474 | 0.4446 | jev-1.13.0 |
| ajuste | inteiro | 6 | 4 | 4 | 44 | 176 | 280 | 362 | 2711 | 0.1139 | jev-1.13.0 |

## Conjunto `ajuste` — 6 condições (4 semânticas) × 44 documentos (arquivo versão 2026-10-02, autor fable); 4 difíceis; 31 verdadeiros e 0 indecidíveis no gabarito

### Total (micro, sobre os documentos decidíveis de todas as condições) — desenho A × desenho B × baseline

P/R/F1 sobre os decidíveis que o sistema DECIDIU; `humano` = decidíveis mandados a `indecidivel` (fora de P/R/F1). **PERDIDAS** = verdadeiro do gabarito que saiu `falso`. **FP NEGADA/REVOGADA** = falso marcado `verdadeiro` em condição das famílias negada/revogada (cláusula negada ou revogada lida como presente — o erro caro). `prova certa` = entre os verdadeiros das condições semânticas, a seção apontada (A: maior `establishes`; B: Choice) é a do gabarito. Desenho padrão: `mapa`; faixas {'establishes': (0.2, 0.8), 'revokes': (0.2, 0.8), 'holds': (0.2, 0.8)}; `deferred` ≥ 0.7.

| desenho | decidíveis | decididas | P | R | F1 | humano (decidíveis) | V a humano | PERDIDAS (V → falso) | FP | FP NEGADA/REVOGADA | prova certa (V semânticos) | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A: mapa por seção (padrão) | 264 | 259 | 1.000 | 1.000 | 1.000 | 5 (0.019) | 1 | 0/31 | 0 | 0 | 22/22 (1.000) | 0/0 (V: 0) | 0 |
| B: documento inteiro | 264 | 259 | 1.000 | 1.000 | 1.000 | 5 (0.019) | 2 | 0/31 | 0 | 0 | 22/22 (1.000) | 0/0 (V: 0) | 0 |
| baseline palavras-chave | 264 | 264 | 0.492 | 1.000 | 0.660 | 0 (0.000) | 0 | 0/31 | 32 | 23 | 22/22 (1.000) | 0/0 (V: 0) | 0 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 F1 (decididas) | 1.000 (baseline 0.660) | ≥ 0.9 e ≥ 0.860 | ✓ |
| 2 perdidas (V → falso) | 0/31 (0.000) | ≤ 0.05 | ✓ |
| 3 FP negada/revogada | 0 | ≤ 1 | ✓ |
| 4 humano (decidíveis) | 5/264 (0.019) | ≤ 0.06 | ✓ |
| secundário: seção que prova | 22/22 (1.000) | ≥ 0.8 | ✓ |
| secundário: indecidíveis → humano | 0/0 | ≥ 0.5 | ✓ |
| secundário: falhas operacionais | 0 | 0 | ✓ |

### Desenho A × desenho B (só condições semânticas; mesmos documentos, pareado)

| n (decidíveis) | F1 A | F1 B | F1 A − B | A certo, B errado | B certo, A errado | os dois errados | humano A / B | perdidas A / B | FP A / B | prova certa A / B |
|---|---|---|---|---|---|---|---|---|---|---|
| 176 | 1.000 | 1.000 | 0.000 | 3 | 3 | 2 | 5 / 5 | 0 / 0 | 0 / 0 | 22/22 / 22/22 |

### Por condição

`tipo` = semântica (Jev) ou numérica (código, igual nos dois desenhos); `V/I` = verdadeiros / indecidíveis do gabarito; `hum` = a humano; `perd` = perdidas; `prova` = seção que prova certa; `base` = palavras-chave (radicais entre colchetes).

| id | família | tipo | V/I | A P | A R | A F1 | A hum | A perd | A FP | A prova | A I→hum | B P | B R | B F1 | B hum | B perd | B FP | B prova | B I→hum | base F1 | base FP | base perd | radicais |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TD-A01 | negada | semântica | 6/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 6/6 | 0/0 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 6/6 | 0/0 | 0.632 | 7 | 0 | [multa, locat, devol, antec, resci] |
| TD-A02 | fácil | numérica multa_alugueis > 2 | 4/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 0 | 0 | — |
| TD-A03 | duas seções | semântica | 5/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 5/5 | 0/0 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 5/5 | 0/0 | 0.667 | 5 | 0 | [desco, pagam, vista] |
| TD-A04 | termo só no título | semântica | 5/0 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 5/5 | 0/0 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 5/5 | 0/0 | 0.714 | 4 | 0 | [exclu, restr, contr, atend, conco] |
| TD-A05 | fácil | numérica prazo_meses < 12 | 5/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 0/0 | 0/0 | 1.000 | 0 | 0 | — |
| TD-A06 | negada | semântica | 6/0 | 1.000 | 1.000 | 1.000 | 3 | 0 | 0 | 6/6 | 0/0 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 6/6 | 0/0 | 0.429 | 16 | 0 | [aprov, reaju, taxa] |

### Por família difícil (pela `nota` do rotulador)

| família | condições | F1 A | F1 B | F1 base | perdidas A/B/base | FP A/B/base | humano A/B | prova A/B |
|---|---|---|---|---|---|---|---|---|
| negada | 2 | 1.000 | 1.000 | 0.511 | 0/0/0 | 0/0/23 | 3/2 | 12/12 · 12/12 |
| fácil | 2 | 1.000 | 1.000 | 1.000 | 0/0/0 | 0/0/0 | 0/0 | 0/0 · 0/0 |
| duas seções | 1 | 1.000 | 1.000 | 0.667 | 0/0/0 | 0/0/5 | 0/1 | 5/5 · 5/5 |
| termo só no título | 1 | 1.000 | 1.000 | 0.714 | 0/0/0 | 0/0/4 | 2/2 | 5/5 · 5/5 |

### Onde os Nouls caem, por gabarito (só documentos que foram ao Jev)

A: `establishes` da seção que prova (verdadeiros) ou o MÁXIMO entre as seções (falsos/indecidíveis); `revokes` = máximo no documento; B: `holds`. `deferred` = máximo no documento (A) ou o do documento (B).

| gabarito | desenho | n | mín | p10 | p50 | p90 | máx | ≤ 0,2 | 0,2–0,8 | ≥ 0,8 | revokes p50 / ≥ 0,8 | deferred p50 / ≥ 0,7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| verdadeiro | mapa | 22 | 0.970 | 0.980 | 0.980 | 0.980 | 0.980 | 0 | 0 | 22 | 0.03 / 0 | 0.16 / 0 |
| verdadeiro | inteiro | 22 | 0.400 | 0.880 | 0.970 | 0.980 | 0.980 | 0 | 2 | 20 | — | 0.04 / 0 |
| falso | mapa | 154 | 0.010 | 0.020 | 0.020 | 0.110 | 0.980 | 149 | 4 | 1 | 0.03 / 2 | 0.15 / 0 |
| falso | inteiro | 154 | 0.010 | 0.020 | 0.020 | 0.050 | 0.630 | 151 | 3 | 0 | — | 0.10 / 0 |
| indecidivel | mapa | 0 | nan | nan | nan | nan | nan | 0 | 0 | 0 | — | — |
| indecidivel | inteiro | 0 | nan | nan | nan | nan | nan | 0 | 0 | 0 | — | — |

### Cobertura × erro por faixa (mesmas respostas, outra faixa; `deferred` fixo)

| desenho | faixa | cobertura (decididas/decidíveis) | erro entre decididas | F1 | humano | perdidas | FP | FP neg/rev | I → humano |
|---|---|---|---|---|---|---|---|---|---|
| mapa | atual (perguntas.py) | 0.981 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 0/0 |
| mapa | 0.5–0.5 | 1.000 | 0.008 | 0.969 | 0 | 0 | 2 | 0 | 0/0 |
| mapa | 0.4–0.6 | 1.000 | 0.008 | 0.969 | 0 | 0 | 2 | 0 | 0/0 |
| mapa | 0.3–0.7 | 0.992 | 0.000 | 1.000 | 2 | 0 | 0 | 0 | 0/0 |
| mapa | 0.2–0.8 | 0.981 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 0/0 |
| mapa | 0.1–0.9 | 0.939 | 0.000 | 1.000 | 16 | 0 | 0 | 0 | 0/0 |
| inteiro | atual (perguntas.py) | 0.981 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 0/0 |
| inteiro | 0.5–0.5 | 1.000 | 0.011 | 0.952 | 0 | 1 | 2 | 0 | 0/0 |
| inteiro | 0.4–0.6 | 0.996 | 0.011 | 0.951 | 1 | 1 | 2 | 0 | 0/0 |
| inteiro | 0.3–0.7 | 0.985 | 0.000 | 1.000 | 4 | 0 | 0 | 0 | 0/0 |
| inteiro | 0.2–0.8 | 0.981 | 0.000 | 1.000 | 5 | 0 | 0 | 0 | 0/0 |
| inteiro | 0.1–0.9 | 0.970 | 0.000 | 1.000 | 8 | 0 | 0 | 0 | 0/0 |

### Custo e latência por desenho (medidos na chamada real; do cache também)

| desenho | documentos avaliados (cond × doc) | sem chamada (numérica) | requisições | novas (não cache) | falhas | p50_ms / p95_ms por requisição | tokens por requisição | tokens por documento (p50) | ms por documento serial p50 / p95 | ms por documento paralelo p50 / p95 | US$ total | US$ por mil documentos avaliados (semânticos) | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mapa | 264 | 88 | 1264 | 1068 | 0 | 254 / 333 | 1474 | 10378 | 1917 / 2316 | 304 / 554 | 0.078250 | 0.4446 | jev-1.13.0 |
| inteiro | 264 | 88 | 176 | 176 | 0 | 280 / 362 | 2711 | 2747 | 281 / 362 | 281 / 362 | 0.020038 | 0.1139 | jev-1.13.0 |

### Caso a caso — erros, documentos mandados a humano e indecidíveis do gabarito (em qualquer desenho)

`A` = mapa (motivo = passos da redução; `prova` = seção de maior `establishes`); `B` = inteiro (`holds`; prova = Choice); `gab prova` = `secao_que_prova`.

| cond | doc | gab | gab prova | A | A ok | A prova | A motivo | B | B ok | B prova | B motivo | base |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TD-A01 | L02 | verdadeiro | L02-s5 | verdadeiro | ✓ | L02-s5 | L02-s5 institui 0.98 | indecidivel | ✗ | L02-s5 | holds 0.52; prova L02-s5 0.87 | verdadeiro |
| TD-A01 | L11 | verdadeiro | L11-s5 | verdadeiro | ✓ | L11-s5 | L11-s5 institui 0.98 | indecidivel | ✗ | L11-s5 | holds 0.40; prova L11-s5 0.81 | verdadeiro |
| TD-A03 | P05 | falso | — | falso | ✓ | P05-s3 | nenhuma seção institui (máx 0.15 em P05-s3) | indecidivel | ✗ | — | holds 0.26; prova none 0.49 | verdadeiro |
| TD-A04 | S04 | falso | — | indecidivel | ✗ | S04-s6 | S04-s6 institui? 0.68 | indecidivel | ✗ | S04-s6 | holds 0.60; prova S04-s6 0.80 | falso |
| TD-A04 | S09 | falso | — | indecidivel | ✗ | S09-s6 | S09-s6 institui? 0.68 | indecidivel | ✗ | S09-s6 | holds 0.63; prova S09-s6 0.81 | falso |
| TD-A06 | S06 | falso | — | indecidivel | ✗ | S06-s3 | S06-s3 institui? 0.21 | falso | ✓ | — | holds 0.05; prova none 0.93 | verdadeiro |
| TD-A06 | S09 | falso | — | indecidivel | ✗ | S09-s3 | S09-s3 institui? 0.21 | falso | ✓ | — | holds 0.06; prova none 0.84 | verdadeiro |
| TD-A06 | A05 | verdadeiro | A05-s3 | indecidivel | ✗ | A05-s3 | A05-s3 institui 0.98; A05-s6 revoga? 0.28 | verdadeiro | ✓ | A05-s3 | holds 0.96; prova A05-s3 0.94 | verdadeiro |
