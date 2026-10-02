# Resultados — rerank-publico-ptbr

Gerado por `run.py` em 2026-10-01 (modo `auto`). Corpus: Quati 1M (unicamp-dl/quati, CC BY 4.0; Bueno et al., 2024), subconjunto de 21825 passagens (1896 julgadas + 19929 distratores), BM25 próprio k1 = 0.9, b = 0.4. Gabarito: notas 0–3 do Quati (GPT-4; kappa 0,31 com humanos [artigo]); relevante binário = nota ≥ 2. Perguntas e critério: `perguntas.py`; ordenação e política segura: `rerank.py`. Preço: US$ 0.042 por milhão de tokens de entrada.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (as consultas sorteadas de teste), rerank por trecho em inglês sobre o top-20 do BM25; **1_ganho_ndcg**: Δ NDCG@10 (Jev − BM25) médio ≥ 0,05 E limite inferior do intervalo de 95% > 0; **2_custo**: custo do Jev ≤ US$ 2,00 por mil consultas (20 requisições por consulta, preço de entrada); **3_latencia**: p95 por requisição ≤ 1.200 ms, medido na chamada real (8 em paralelo); **secundario_nao_decide**: Δ MRR@10 (nota ≥ 2) com intervalo que não cruza zero; Jev ≥ baseline de sobreposição em NDCG@10; variante 'lote' (20 trechos num state) relatada ao lado, sem decidir; **se_falhar**: 1 falhando = o Noul por trecho não paga a chamada neste corpus; 2 ou 3 falhando = reler em lote ou indexar na ingestão

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T23:57:21-03:00): `perguntas.py` sha256 d0aeb58b7274ef6b… · `rerank.py` sha256 4af218101f41873b… · `bm25.py` sha256 b7d568286c55c9c9… · `run.py` sha256 4a84d1f1d5a609c7… · `dados/teste.json` sha256 66ae35affd4afec5…

## Lado a lado

| conjunto | variante | n | NDCG@10 [IC] | Δ NDCG vs bm25 [IC] | MRR@10 [IC] | Δ MRR vs bm25 [IC] | req | US$/1000 | p50/p95 req (ms) | falhas |
|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | bm25 | 10 | 0.457 [0.302; 0.617] | — | 0.683 [0.417; 0.933] | — |  |  |  |  |
| ajuste | sobreposicao | 10 | 0.454 [0.293; 0.620] | -0.003 [-0.026; +0.020] | 0.711 [0.422; 1.000] | +0.028 [-0.067; +0.150] |  |  |  |  |
| ajuste | jev | 10 | 0.613 [0.444; 0.795] | +0.156 [+0.062; +0.247] | 0.850 [0.650; 1.000] | +0.167 [-0.050; +0.417] | 200 | 0.5981 | 256 / 373 | 0 |
| ajuste | jev_pt | 10 | 0.625 [0.450; 0.800] | +0.168 [+0.073; +0.258] | 0.850 [0.650; 1.000] | +0.167 [-0.050; +0.417] | 200 | 0.5998 | 250 / 347 | 0 |
| ajuste | jev_lote | 10 | 0.523 [0.366; 0.680] | +0.066 [-0.032; +0.145] | 0.750 [0.550; 0.950] | +0.067 [-0.150; +0.283] | 10 | 0.3866 | 332 / 388 | 0 |
| ajuste | teto | 10 | 0.680 [0.505; 0.853] | +0.224 [+0.147; +0.290] | 0.900 [0.700; 1.000] | +0.217 [+0.000; +0.433] |  |  |  |  |
| teste | bm25 | 39 | 0.387 [0.316; 0.461] | — | 0.524 [0.400; 0.646] | — |  |  |  |  |
| teste | sobreposicao | 39 | 0.376 [0.310; 0.446] | -0.011 [-0.035; +0.012] | 0.550 [0.429; 0.665] | +0.027 [-0.004; +0.081] |  |  |  |  |
| teste | jev | 39 | 0.712 [0.641; 0.774] | +0.325 [+0.262; +0.385] | 0.904 [0.801; 0.981] | +0.380 [+0.262; +0.503] | 780 | 0.5932 | 252 / 324 | 0 |
| teste | jev_lote | 39 | 0.588 [0.512; 0.662] | +0.202 [+0.153; +0.249] | 0.780 [0.662; 0.878] | +0.256 [+0.150; +0.366] | 39 | 0.3829 | 311 / 369 | 0 |
| teste | teto | 39 | 0.767 [0.695; 0.832] | +0.381 [+0.317; +0.444] | 0.949 [0.872; 1.000] | +0.425 [+0.299; +0.547] |  |  |  |  |

## Conjunto `ajuste` — 10 consultas × 20 trechos do BM25 (Quati 1M, semente da preparação 20261001)

Teto do rerank: **1** consulta(s) sem nenhum trecho com nota ≥ 2 no top-20 ([189]) — nelas nenhuma reordenação muda o MRR; `teto` = top-20 na ordem do gabarito. Trechos não julgados no top-20: 45/200 (contam como nota 0).

### Qualidade do ranking — média sobre as consultas, intervalo de 95% por bootstrap (1000 reamostras, semente 20261001); Δ pareado contra `bm25`

| variante | NDCG@10 | Δ NDCG@10 vs bm25 | MRR@10 (nota ≥ 2) | Δ MRR@10 vs bm25 | 1º relevante no top-10 | ganhou · empatou · perdeu (NDCG vs bm25) |
|---|---|---|---|---|---|---|
| bm25 | 0.457 [0.302; 0.617] | — | 0.683 [0.417; 0.933] | — | 8 | — |
| sobreposicao | 0.454 [0.293; 0.620] | -0.003 [-0.026; +0.020] | 0.711 [0.422; 1.000] | +0.028 [-0.067; +0.150] | 8 | 1 · 7 · 2 |
| jev | 0.613 [0.444; 0.795] | +0.156 [+0.062; +0.247] | 0.850 [0.650; 1.000] | +0.167 [-0.050; +0.417] | 9 | 8 · 1 · 1 |
| jev_pt | 0.625 [0.450; 0.800] | +0.168 [+0.073; +0.258] | 0.850 [0.650; 1.000] | +0.167 [-0.050; +0.417] | 9 | 8 · 1 · 1 |
| jev_lote | 0.523 [0.366; 0.680] | +0.066 [-0.032; +0.145] | 0.750 [0.550; 0.950] | +0.067 [-0.150; +0.283] | 9 | 7 · 2 · 1 |
| teto | 0.680 [0.505; 0.853] | +0.224 [+0.147; +0.290] | 0.900 [0.700; 1.000] | +0.217 [+0.000; +0.433] | 9 | 8 · 2 · 0 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 ganho NDCG@10 (Jev − BM25) | Δ +0.156 [+0.062; +0.247] | Δ ≥ 0.05 e IC > 0 | ✓ |
| 2 custo por mil consultas | US$ 0.598 | ≤ US$ 2.0 | ✓ |
| 3 p95 por requisição | 373 ms | ≤ 1200 ms | ✓ |
| secundário: Δ MRR@10 com IC > 0 | Δ +0.167 [-0.050; +0.417] | IC > 0 | ✗ |
| secundário: Jev ≥ sobreposição (NDCG@10) | 0.613 × 0.454 | ≥ | ✓ |

### Noul × nota do gabarito (todos os trechos julgados pelo Jev)

Média de P(responde) por nota; `acerto ≥ 0,5` compara P ≥ 0,5 com nota ≥ 2 (só trechos julgados); Brier contra o mesmo binário. Nota `—` = não julgado pelo gabarito.

| variante | nota — | nota 0 | nota 1 | nota 2 | nota 3 | acerto ≥ 0,5 | brier | n julgados |
|---|---|---|---|---|---|---|---|---|
| jev | 0.03 (n=45) | 0.11 (n=82) | 0.23 (n=24) | 0.59 (n=24) | 0.92 (n=25) | 0.890 | 0.080 | 155 |
| jev_pt | 0.04 (n=45) | 0.12 (n=82) | 0.24 (n=24) | 0.62 (n=24) | 0.92 (n=25) | 0.884 | 0.074 | 155 |
| jev_lote | 0.14 (n=45) | 0.11 (n=82) | 0.14 (n=24) | 0.43 (n=24) | 0.72 (n=25) | 0.858 | 0.114 | 155 |

### Custo e latência (medidos na chamada real; do cache também)

| variante | requisições (do cache) | falhas (→ ordem do BM25) | req/consulta | tokens/consulta | US$/1000 consultas | p50/p95 por requisição (ms) | p50/p95 por consulta (ms, 8 vagas) | modelo |
|---|---|---|---|---|---|---|---|---|
| jev | 200 (200) | 0 | 20.000 | 14240 | 0.5981 | 256 / 373 | 825 / 1013 | jev-1.13.0 |
| jev_pt | 200 (200) | 0 | 20.000 | 14280 | 0.5998 | 250 / 347 | 816 / 1014 | jev-1.13.0 |
| jev_lote | 10 (10) | 0 | 1.000 | 9205 | 0.3866 | 332 / 388 | = por requisição | jev-1.13.0 |

### Por consulta

`rel` = trechos com nota ≥ 2 (gabarito inteiro / no top-20); `n/j` = não julgados no top-20; `1º rel` = posição do primeiro relevante (bm25 → jev); `P máx` = maior P(responde) da consulta.

| consulta | rel | n/j | NDCG bm25 | NDCG sobreposicao | NDCG jev | NDCG jev_pt | NDCG jev_lote | NDCG teto | MRR bm25 → jev | 1º rel | P máx | ms | falha |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 9 | 11 / 1 | 9 | 0.135 | 0.135 | 0.135 | 0.135 | 0.135 | 0.135 | 1.00 → 1.00 | 1 → 1 | 0.28 | 1013 |  |
| 13 | 13 / 6 | 2 | 0.250 | 0.165 | 0.602 | 0.605 | 0.497 | 0.616 | 0.33 → 1.00 | 3 → 1 | 0.80 | 954 |  |
| 60 | 16 / 12 | 4 | 0.798 | 0.782 | 1.000 | 1.000 | 0.827 | 1.000 | 1.00 → 1.00 | 1 → 1 | 0.98 | 855 |  |
| 98 | 10 / 2 | 7 | 0.037 | 0.037 | 0.378 | 0.378 | 0.100 | 0.380 | 0.00 → 1.00 | 15 → 1 | 0.93 | 811 |  |
| 127 | 5 / 4 | 3 | 0.748 | 0.748 | 0.776 | 0.775 | 0.479 | 0.946 | 1.00 → 1.00 | 1 → 1 | 0.86 | 839 |  |
| 147 | 3 / 1 | 2 | 0.456 | 0.456 | 0.288 | 0.288 | 0.456 | 0.456 | 1.00 → 0.50 | 1 → 2 | 0.88 | 780 |  |
| 154 | 15 / 12 | 3 | 0.678 | 0.678 | 0.922 | 0.922 | 0.804 | 0.926 | 1.00 → 1.00 | 1 → 1 | 0.97 | 907 |  |
| 170 | 15 / 8 | 6 | 0.557 | 0.630 | 0.880 | 0.901 | 0.794 | 0.913 | 0.50 → 1.00 | 2 → 1 | 0.88 | 722 |  |
| 181 | 5 / 3 | 8 | 0.463 | 0.463 | 0.618 | 0.617 | 0.502 | 0.726 | 1.00 → 1.00 | 1 → 1 | 0.95 | 759 |  |
| 189 | 0 / 0 | 1 | 0.448 | 0.448 | 0.527 | 0.629 | 0.638 | 0.704 | 0.00 → 0.00 | — → — | 0.27 | 735 |  |

## Conjunto `teste` — 39 consultas × 20 trechos do BM25 (Quati 1M, semente da preparação 20261001)

Teto do rerank: **2** consulta(s) sem nenhum trecho com nota ≥ 2 no top-20 ([95, 117]) — nelas nenhuma reordenação muda o MRR; `teto` = top-20 na ordem do gabarito. Trechos não julgados no top-20: 146/780 (contam como nota 0).

### Qualidade do ranking — média sobre as consultas, intervalo de 95% por bootstrap (1000 reamostras, semente 20261001); Δ pareado contra `bm25`

| variante | NDCG@10 | Δ NDCG@10 vs bm25 | MRR@10 (nota ≥ 2) | Δ MRR@10 vs bm25 | 1º relevante no top-10 | ganhou · empatou · perdeu (NDCG vs bm25) |
|---|---|---|---|---|---|---|
| bm25 | 0.387 [0.316; 0.461] | — | 0.524 [0.400; 0.646] | — | 33 | — |
| sobreposicao | 0.376 [0.310; 0.446] | -0.011 [-0.035; +0.012] | 0.550 [0.429; 0.665] | +0.027 [-0.004; +0.081] | 34 | 11 · 17 · 11 |
| jev | 0.712 [0.641; 0.774] | +0.325 [+0.262; +0.385] | 0.904 [0.801; 0.981] | +0.380 [+0.262; +0.503] | 37 | 36 · 1 · 2 |
| jev_lote | 0.588 [0.512; 0.662] | +0.202 [+0.153; +0.249] | 0.780 [0.662; 0.878] | +0.256 [+0.150; +0.366] | 36 | 36 · 2 · 1 |
| teto | 0.767 [0.695; 0.832] | +0.381 [+0.317; +0.444] | 0.949 [0.872; 1.000] | +0.425 [+0.299; +0.547] | 37 | 38 · 1 · 0 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 ganho NDCG@10 (Jev − BM25) | Δ +0.325 [+0.262; +0.385] | Δ ≥ 0.05 e IC > 0 | ✓ |
| 2 custo por mil consultas | US$ 0.593 | ≤ US$ 2.0 | ✓ |
| 3 p95 por requisição | 324 ms | ≤ 1200 ms | ✓ |
| secundário: Δ MRR@10 com IC > 0 | Δ +0.380 [+0.262; +0.503] | IC > 0 | ✓ |
| secundário: Jev ≥ sobreposição (NDCG@10) | 0.712 × 0.376 | ≥ | ✓ |

### Noul × nota do gabarito (todos os trechos julgados pelo Jev)

Média de P(responde) por nota; `acerto ≥ 0,5` compara P ≥ 0,5 com nota ≥ 2 (só trechos julgados); Brier contra o mesmo binário. Nota `—` = não julgado pelo gabarito.

| variante | nota — | nota 0 | nota 1 | nota 2 | nota 3 | acerto ≥ 0,5 | brier | n julgados |
|---|---|---|---|---|---|---|---|---|
| jev | 0.09 (n=146) | 0.10 (n=292) | 0.26 (n=140) | 0.59 (n=109) | 0.90 (n=93) | 0.886 | 0.082 | 634 |
| jev_lote | 0.14 (n=146) | 0.12 (n=292) | 0.23 (n=140) | 0.45 (n=109) | 0.66 (n=93) | 0.801 | 0.145 | 634 |

### Custo e latência (medidos na chamada real; do cache também)

| variante | requisições (do cache) | falhas (→ ordem do BM25) | req/consulta | tokens/consulta | US$/1000 consultas | p50/p95 por requisição (ms) | p50/p95 por consulta (ms, 8 vagas) | modelo |
|---|---|---|---|---|---|---|---|---|
| jev | 780 (3) | 0 | 20.000 | 14122 | 0.5932 | 252 / 324 | 774 / 978 | jev-1.13.0 |
| jev_lote | 39 (0) | 0 | 1.000 | 9117 | 0.3829 | 311 / 369 | = por requisição | jev-1.13.0 |

### Por consulta

`rel` = trechos com nota ≥ 2 (gabarito inteiro / no top-20); `n/j` = não julgados no top-20; `1º rel` = posição do primeiro relevante (bm25 → jev); `P máx` = maior P(responde) da consulta.

| consulta | rel | n/j | NDCG bm25 | NDCG sobreposicao | NDCG jev | NDCG jev_lote | NDCG teto | MRR bm25 → jev | 1º rel | P máx | ms | falha |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 12 / 6 | 3 | 0.415 | 0.269 | 0.762 | 0.450 | 0.859 | 0.33 → 1.00 | 3 → 1 | 0.93 | 978 |  |
| 11 | 3 / 3 | 2 | 0.516 | 0.516 | 0.851 | 0.731 | 0.947 | 0.50 → 1.00 | 2 → 1 | 0.94 | 762 |  |
| 15 | 4 / 3 | 2 | 0.573 | 0.573 | 0.766 | 0.706 | 0.771 | 1.00 → 1.00 | 1 → 1 | 0.98 | 1043 |  |
| 17 | 13 / 8 | 2 | 0.641 | 0.644 | 0.889 | 0.788 | 0.889 | 1.00 → 1.00 | 1 → 1 | 0.98 | 774 |  |
| 20 | 17 / 2 | 5 | 0.186 | 0.186 | 0.340 | 0.275 | 0.352 | 0.14 → 1.00 | 7 → 1 | 0.85 | 764 |  |
| 21 | 16 / 6 | 10 | 0.500 | 0.500 | 0.820 | 0.799 | 0.833 | 1.00 → 1.00 | 1 → 1 | 0.98 | 771 |  |
| 22 | 1 / 1 | 2 | 0.860 | 0.850 | 0.858 | 0.864 | 0.935 | 1.00 → 1.00 | 1 → 1 | 0.98 | 740 |  |
| 24 | 7 / 3 | 5 | 0.564 | 0.564 | 0.716 | 0.605 | 0.731 | 1.00 → 1.00 | 1 → 1 | 0.96 | 781 |  |
| 26 | 16 / 14 | 0 | 0.581 | 0.581 | 0.938 | 0.732 | 1.000 | 1.00 → 1.00 | 1 → 1 | 0.97 | 773 |  |
| 28 | 5 / 4 | 5 | 0.714 | 0.645 | 0.800 | 0.830 | 0.926 | 1.00 → 1.00 | 1 → 1 | 0.96 | 774 |  |
| 47 | 17 / 6 | 4 | 0.154 | 0.154 | 0.453 | 0.390 | 0.490 | 0.33 → 1.00 | 3 → 1 | 0.88 | 749 |  |
| 49 | 7 / 4 | 8 | 0.263 | 0.263 | 0.553 | 0.450 | 0.554 | 0.20 → 1.00 | 5 → 1 | 0.54 | 781 |  |
| 51 | 6 / 5 | 0 | 0.205 | 0.233 | 0.803 | 0.538 | 0.936 | 0.33 → 0.50 | 3 → 2 | 0.60 | 768 |  |
| 54 | 31 / 13 | 3 | 0.714 | 0.714 | 0.890 | 0.711 | 0.926 | 1.00 → 1.00 | 1 → 1 | 0.99 | 763 |  |
| 62 | 7 / 1 | 6 | 0.111 | 0.212 | 0.389 | 0.314 | 0.419 | 0.00 → 1.00 | 14 → 1 | 0.22 | 941 |  |
| 64 | 7 / 2 | 4 | 0.156 | 0.150 | 0.703 | 0.459 | 0.709 | 0.00 → 1.00 | 15 → 1 | 0.96 | 976 |  |
| 68 | 26 / 9 | 3 | 0.441 | 0.493 | 0.924 | 0.809 | 0.967 | 1.00 → 1.00 | 1 → 1 | 0.81 | 756 |  |
| 84 | 2 / 1 | 4 | 0.337 | 0.337 | 0.337 | 0.337 | 0.337 | 1.00 → 1.00 | 1 → 1 | 0.84 | 783 |  |
| 95 | 1 / 0 | 2 | 0.389 | 0.302 | 0.263 | 0.389 | 0.402 | 0.00 → 0.00 | — → — | 0.59 | 754 |  |
| 105 | 7 / 6 | 0 | 0.366 | 0.469 | 0.883 | 0.718 | 0.916 | 0.50 → 1.00 | 2 → 1 | 0.96 | 806 |  |
| 113 | 26 / 13 | 5 | 0.651 | 0.598 | 0.874 | 0.749 | 0.926 | 1.00 → 1.00 | 1 → 1 | 0.98 | 754 |  |
| 115 | 25 / 9 | 7 | 0.469 | 0.387 | 0.726 | 0.661 | 0.791 | 0.50 → 1.00 | 2 → 1 | 0.97 | 757 |  |
| 117 | 3 / 0 | 6 | 0.159 | 0.159 | 0.189 | 0.183 | 0.278 | 0.00 → 0.00 | — → — | 0.68 | 740 |  |
| 126 | 8 / 3 | 4 | 0.072 | 0.072 | 0.533 | 0.505 | 0.533 | 0.10 → 1.00 | 10 → 1 | 0.86 | 826 |  |
| 128 | 2 / 2 | 0 | 0.000 | 0.000 | 0.641 | 0.244 | 0.925 | 0.00 → 0.50 | 15 → 2 | 0.97 | 892 |  |
| 136 | 7 / 5 | 3 | 0.060 | 0.230 | 0.833 | 0.623 | 0.835 | 0.12 → 1.00 | 8 → 1 | 0.94 | 774 |  |
| 152 | 2 / 1 | 8 | 0.096 | 0.096 | 0.374 | 0.174 | 0.529 | 0.00 → 0.25 | 17 → 4 | 0.49 | 836 |  |
| 153 | 6 / 5 | 3 | 0.716 | 0.493 | 0.969 | 0.787 | 0.969 | 0.50 → 1.00 | 2 → 1 | 0.94 | 863 |  |
| 160 | 3 / 3 | 7 | 0.673 | 0.413 | 0.937 | 0.968 | 1.000 | 1.00 → 1.00 | 1 → 1 | 0.96 | 930 |  |
| 161 | 4 / 4 | 1 | 0.254 | 0.223 | 0.829 | 0.886 | 1.000 | 0.33 → 1.00 | 3 → 1 | 0.92 | 729 |  |
| 163 | 6 / 6 | 1 | 0.753 | 0.753 | 0.934 | 0.838 | 1.000 | 1.00 → 1.00 | 1 → 1 | 0.93 | 729 |  |
| 167 | 3 / 1 | 4 | 0.114 | 0.114 | 0.446 | 0.275 | 0.469 | 0.14 → 1.00 | 7 → 1 | 0.25 | 816 |  |
| 172 | 15 / 8 | 4 | 0.165 | 0.166 | 0.744 | 0.287 | 0.744 | 0.50 → 1.00 | 2 → 1 | 0.96 | 798 |  |
| 180 | 7 / 5 | 3 | 0.167 | 0.194 | 0.755 | 0.660 | 0.773 | 0.12 → 1.00 | 8 → 1 | 0.94 | 752 |  |
| 182 | 2 / 2 | 6 | 0.670 | 0.671 | 1.000 | 1.000 | 1.000 | 0.50 → 1.00 | 2 → 1 | 0.94 | 754 |  |
| 193 | 23 / 8 | 3 | 0.368 | 0.405 | 0.658 | 0.688 | 0.805 | 0.50 → 1.00 | 2 → 1 | 0.94 | 906 |  |
| 195 | 26 / 12 | 4 | 0.553 | 0.584 | 0.843 | 0.707 | 0.886 | 1.00 → 1.00 | 1 → 1 | 0.96 | 785 |  |
| 196 | 24 / 10 | 4 | 0.253 | 0.252 | 0.770 | 0.541 | 0.796 | 0.25 → 1.00 | 4 → 1 | 0.98 | 884 |  |
| 199 | 16 / 8 | 3 | 0.195 | 0.195 | 0.758 | 0.270 | 0.771 | 0.50 → 1.00 | 2 → 1 | 0.98 | 770 |  |
