# Resultados — rerank-publico-ptbr

Gerado por `run.py` em 2026-10-01 (modo `auto`). Corpus: Quati 1M (unicamp-dl/quati, CC BY 4.0; Bueno et al., 2024), subconjunto de 21825 passagens (1896 julgadas + 19929 distratores), BM25 próprio k1 = 0.9, b = 0.4. Gabarito: notas 0–3 do Quati (GPT-4; kappa 0,31 com humanos [artigo]); relevante binário = nota ≥ 2. Perguntas e critério: `perguntas.py`; ordenação e política segura: `rerank.py`. Preço: US$ 0.042 por milhão de tokens de entrada.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (as consultas sorteadas de teste), rerank por trecho em inglês sobre o top-20 do BM25; **1_ganho_ndcg**: Δ NDCG@10 (Jev − BM25) médio ≥ 0,05 E limite inferior do intervalo de 95% > 0; **2_custo**: custo do Jev ≤ US$ 2,00 por mil consultas (20 requisições por consulta, preço de entrada); **3_latencia**: p95 por requisição ≤ 1.200 ms, medido na chamada real (8 em paralelo); **secundario_nao_decide**: Δ MRR@10 (nota ≥ 2) com intervalo que não cruza zero; Jev ≥ baseline de sobreposição em NDCG@10; variante 'lote' (20 trechos num state) relatada ao lado, sem decidir; **se_falhar**: 1 falhando = o Noul por trecho não paga a chamada neste corpus; 2 ou 3 falhando = reler em lote ou indexar na ingestão

Versão em afinação (NÃO congelada): `perguntas.py` sha256 d0aeb58b7274ef6b… · `rerank.py` sha256 4af218101f41873b… · `bm25.py` sha256 b2ca3518da36f2b7… · `run.py` sha256 4a84d1f1d5a609c7… · `dados/teste.json` sha256 81142b3f979f917d…

## Conjunto `rascunho` — 1 consultas × 20 trechos do BM25 (Quati 1M, semente da preparação 20261001)

> Rascunho: 1 consulta do ajuste, só o encanamento. **Não é métrica.**

Teto do rerank: **0** consulta(s) sem nenhum trecho com nota ≥ 2 no top-20 (—) — nelas nenhuma reordenação muda o MRR; `teto` = top-20 na ordem do gabarito. Trechos não julgados no top-20: 9/20 (contam como nota 0).

### Qualidade do ranking — média sobre as consultas, intervalo de 95% por bootstrap (1000 reamostras, semente 20261001); Δ pareado contra `bm25`

| variante | NDCG@10 | Δ NDCG@10 vs bm25 | MRR@10 (nota ≥ 2) | Δ MRR@10 vs bm25 | 1º relevante no top-10 | ganhou · empatou · perdeu (NDCG vs bm25) |
|---|---|---|---|---|---|---|
| bm25 | 0.135 [0.135; 0.135] | — | 1.000 [1.000; 1.000] | — | 1 | — |
| sobreposicao | 0.135 [0.135; 0.135] | +0.000 [+0.000; +0.000] | 1.000 [1.000; 1.000] | +0.000 [+0.000; +0.000] | 1 | 0 · 1 · 0 |
| jev | 0.135 [0.135; 0.135] | +0.000 [+0.000; +0.000] | 1.000 [1.000; 1.000] | +0.000 [+0.000; +0.000] | 1 | 0 · 1 · 0 |
| teto | 0.135 [0.135; 0.135] | +0.000 [+0.000; +0.000] | 1.000 [1.000; 1.000] | +0.000 [+0.000; +0.000] | 1 | 0 · 1 · 0 |

### Noul × nota do gabarito (todos os trechos julgados pelo Jev)

Média de P(responde) por nota; `acerto ≥ 0,5` compara P ≥ 0,5 com nota ≥ 2 (só trechos julgados); Brier contra o mesmo binário. Nota `—` = não julgado pelo gabarito.

| variante | nota — | nota 0 | nota 1 | nota 2 | nota 3 | acerto ≥ 0,5 | brier | n julgados |
|---|---|---|---|---|---|---|---|---|
| jev | 0.01 (n=9) | 0.02 (n=10) | — | 0.28 (n=1) | — | 0.909 | 0.047 | 11 |

### Custo e latência (medidos na chamada real; do cache também)

| variante | requisições (do cache) | falhas (→ ordem do BM25) | req/consulta | tokens/consulta | US$/1000 consultas | p50/p95 por requisição (ms) | p50/p95 por consulta (ms, 8 vagas) | modelo |
|---|---|---|---|---|---|---|---|---|
| jev | 20 (0) | 0 | 20.000 | 14474 | 0.6080 | 323 / 417 | 1056 / 1056 | jev-1.13.0 |

### Por consulta

`rel` = trechos com nota ≥ 2 (gabarito inteiro / no top-20); `n/j` = não julgados no top-20; `1º rel` = posição do primeiro relevante (bm25 → jev); `P máx` = maior P(responde) da consulta.

| consulta | rel | n/j | NDCG bm25 | NDCG sobreposicao | NDCG jev | NDCG teto | MRR bm25 → jev | 1º rel | P máx | ms | falha |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 9 | 11 / 1 | 9 | 0.135 | 0.135 | 0.135 | 0.135 | 1.00 → 1.00 | 1 → 1 | 0.28 | 1056 |  |
