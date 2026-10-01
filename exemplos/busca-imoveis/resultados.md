# Resultados — busca-imoveis

Gerado por `src/run.ts` em 2026-09-30 (modo `gravado`). Modelo pedido `jev-1.13.0`; preço US$ 0.042 por milhão de tokens de entrada. Perguntas, limiares e pesos: `src/perguntas.ts`.

Versão congelada (gravada em 2026-09-30 23:04 UTC, antes de abrir o teste): `perguntas.ts` sha256 1705f8f252dee6e7… · `busca.ts` sha256 b25edfc73c91de41…

> **Demonstração de mecanismo, não desempenho em portal real.** Catálogo sintético e controlado (Codex): cada anúncio tem 8 fatos ternários (afirma / nega / omite) escritos com um de três enunciados fixos; o gabarito foi DERIVADO desses fatos de autoria pela escala congelada, não anotado por humano sobre anúncios reais. O teste mede consultas novas sobre o MESMO catálogo.

## Lado a lado

Sistemas: `jev` = filtro (Jev lê a consulta) + ranking pelo ganho esperado (Jev lê cada anúncio); `filtro_so` = mesmo filtro, ordem do catálogo (sem ranking); `palavras` = linha de base SEM Jev: BM25 sobre título+descrição+tipo+bairro+cidade, catálogo inteiro, sem filtro; `filtro_palavras` = mesmo filtro, ranking por BM25 na descrição (isola o valor do Jev no anúncio); `teto` = mesmo filtro, recuperados na ordem do gabarito (só a perda da recuperação limita).

**Qualidade do ranking (média por consulta)**

| conjunto | métrica | jev | filtro_so | palavras | filtro_palavras | teto |
|---|---|---|---|---|---|---|
| ajuste | NDCG@10 | 1.000 | 0.682 | 0.194 | 0.731 | 1.000 |
| ajuste | P@5 (rel≥1) | 0.950 | 0.800 | 0.200 | 0.675 | 0.950 |
| teste | NDCG@10 | 1.000 | 0.581 | 0.233 | 0.694 | 1.000 |
| teste | P@5 (rel≥1) | 0.950 | 0.750 | 0.175 | 0.700 | 0.950 |


**Recuperação (o filtro, antes do Jev ler anúncio) e ranking (top-10)** — somas sobre as consultas. `teto top-10` = Σ min(10, relevantes da consulta).

| conjunto | n | rel≥1 após recuperação | rel=3 após recuperação | PERDA da recuperação rel≥1 · rel=3 | rel≥1 no top-10 jev · filtro_palavras · palavras | rel=3 no top-10 jev · filtro_palavras · palavras |
|---|---|---|---|---|---|---|
| ajuste | 8 | 92/92 (100%) | 38/38 (100%) | 0 · 0 | 63/63 (100%) · 49 · 11 | 33/33 (100%) · 23 · 10 |
| teste | 16 | 206/206 (100%) | 75/75 (100%) | 0 · 0 | 135/135 (100%) · 106 · 31 | 71/71 (100%) · 58 · 26 |


**Leitura do anúncio (relevância prevista = argmax da distribuição, entre os recuperados)** — matriz linhas = gabarito 0..3, colunas = previsto 0..3

| conjunto | acerto da relevância prevista | matriz |
|---|---|---|
| ajuste | 124/124 (100%) | 0: 32/0/0/0 · 1: 0/23/0/0 · 2: 0/0/31/0 · 3: 0/0/0/38 |
| teste | 311/311 (100%) | 0: 105/0/0/0 · 1: 0/58/0/0 · 2: 0/0/73/0 · 3: 0/0/0/75 |


**Margem das leituras** — quão longe dos limiares tudo caiu. Limiar que nenhuma leitura chegou perto de cruzar NÃO foi calibrado.

| conjunto | consulta: menor Noul pedido · maior Noul não pedido (limiar 0,5) | consulta: menor confiança das Choices duras | anúncio: leituras ternárias com prob. máxima < 0,9 | anúncio: menor prob. máxima |
|---|---|---|---|---|
| ajuste | 0.99 · 0.15 | 1.000 | 0/218 | 0.970 |
| teste | 0.68 · 0.29 | 0.980 | 0/655 | 0.970 |


**Custo e latência** (latência por requisição = medida na chamada real, 8 em paralelo; por consulta = leitura + fila de 8 vagas com os ms medidos)

| conjunto | requisições/consulta | tokens/consulta | US$/consulta | US$/1000 consultas | p50/p95 por requisição (ms) | p50/p95 por consulta (ms) | requisições (do cache) | retentativas do SDK nesta execução | modelo |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | 16.5 | 18959 | 0.000796 | 0.796 | 261 / 344 | 873 / 1994 | 132 (132) | 0 | jev-1.13.0 |
| teste | 20.4 | 21826 | 0.000917 | 0.917 | 271 / 346 | 993 / 2789 | 327 (327) | 0 | jev-1.13.0 |


## Conjunto `ajuste` — 8 consultas (arquivo versão 2026-09-30, autor codex)

### Por consulta

| consulta | recuperados | requisicoes | rel≥1 recuperados | rel=3 recuperados | NDCG@10 jev | filtro_so | palavras | filtro_palavras | teto | P@5 jev | ms (simulado) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BI-A001 | 7 | 8 | 5/5 | 1/1 | 1.000 | 0.718 | 0.183 | 0.899 | 1.000 | 1.000 | 779 |
| BI-A002 | 4 | 5 | 3/3 | 2/2 | 1.000 | 0.631 | 0.000 | 0.700 | 1.000 | 0.600 | 591 |
| BI-A003 | 18 | 19 | 11/11 | 3/3 | 1.000 | 0.615 | 0.072 | 0.388 | 1.000 | 1.000 | 1061 |
| BI-A004 | 6 | 7 | 6/6 | 1/1 | 1.000 | 1.000 | 0.000 | 0.762 | 1.000 | 1.000 | 713 |
| BI-A005 | 20 | 21 | 16/16 | 8/8 | 1.000 | 0.487 | 0.460 | 0.813 | 1.000 | 1.000 | 1203 |
| BI-A006 | 11 | 12 | 9/9 | 3/3 | 1.000 | 0.853 | 0.220 | 0.888 | 1.000 | 1.000 | 837 |
| BI-A007 | 14 | 15 | 10/10 | 5/5 | 1.000 | 0.496 | 0.393 | 0.825 | 1.000 | 1.000 | 873 |
| BI-A008 | 44 | 45 | 32/32 | 15/15 | 1.000 | 0.657 | 0.224 | 0.572 | 1.000 | 1.000 | 1994 |


### Leitura da consulta (Jev) → filtro (código)

Critério pedido = Noul ≥ limiar (valor entre parênteses). `conf mín` = menor confiança entre as 7 Choices duras.

| consulta | texto | filtro | pedidos | quase pedidos (0,2–0,5) | conf mín |
|---|---|---|---|---|---|
| BI-A001 | Apartamento em Cidade Aurora, até 600 mil, com pelo menos 2 quartos e 1 vaga. Preciso que aceite pet e fique em rua tranquila. | apartamento · Cidade Aurora · ≥2 quartos · ≥1 vagas · ≤ R$ 600 mil | pet (0.99), rua_tranquila (0.99) | — | 1.000 |
| BI-A002 | Casa em Cidade Horizonte até R$ 750 mil, ao menos três quartos e duas vagas, com espaço adequado para home office. | casa · Cidade Horizonte · ≥3 quartos · ≥2 vagas · ≤ R$ 750 mil | home_office (0.99) | — | 1.000 |
| BI-A003 | Quero sobrado em Cidade Aurora, dois quartos ou mais e preço máximo de 800 mil. Rua silenciosa e sol da manhã são importantes. | sobrado · Cidade Aurora · ≥2 quartos · ≤ R$ 800 mil | rua_tranquila (0.99), sol_manha (0.99) | — | 1.000 |
| BI-A004 | Apartamento de pelo menos um quarto em Cidade Horizonte, até 500 mil, perto do metrô para ir a pé. | apartamento · Cidade Horizonte · ≥1 quartos · ≤ R$ 500 mil | metro (0.99) | — | 1.000 |
| BI-A005 | Imóvel no Jardim Norte, Cidade Aurora, com dois quartos ou mais, no máximo 750 mil e já reformado, pronto para morar. | qualquer tipo · Cidade Aurora · Jardim Norte · ≥2 quartos · ≤ R$ 750 mil | reformado (0.99) | — | 1.000 |
| BI-A006 | Apartamento em Cidade Horizonte até 650 mil, pelo menos dois quartos, que permita animais e receba sol da manhã. | apartamento · Cidade Horizonte · ≥2 quartos · ≤ R$ 650 mil | pet (0.99), sol_manha (0.99) | — | 1.000 |
| BI-A007 | Casa em Cidade Aurora até 850 mil com duas vagas ou mais. Preciso de rua tranquila e ambiente próprio para trabalhar em casa. | casa · Cidade Aurora · ≥2 vagas · ≤ R$ 850 mil | rua_tranquila (0.99), home_office (0.99) | — | 1.000 |
| BI-A008 | Procuro imóvel em Cidade Horizonte até 700 mil, pelo menos dois quartos, vista livre e permissão para cães e gatos. | qualquer tipo · Cidade Horizonte · ≥2 quartos · ≤ R$ 700 mil | pet (0.99), vista (0.99) | — | 1.000 |


### Perda da recuperação (relevantes descartados pelo filtro ANTES do Jev): 0


### Leitura do anúncio: relevância prevista ≠ gabarito (0 de 124 recuperados)

A ordem usa o ganho esperado, não a prevista; a prevista (argmax) mede a leitura. Recortes da descrição ao lado.

## Conjunto `teste` — 16 consultas (arquivo versão 2026-09-30, autor codex)

### Por consulta

| consulta | recuperados | requisicoes | rel≥1 recuperados | rel=3 recuperados | NDCG@10 jev | filtro_so | palavras | filtro_palavras | teto | P@5 jev | ms (simulado) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BI-T001 | 10 | 11 | 8/8 | 5/5 | 1.000 | 0.683 | 0.178 | 0.802 | 1.000 | 1.000 | 993 |
| BI-T002 | 8 | 9 | 7/7 | 2/2 | 1.000 | 0.854 | 0.000 | 0.584 | 1.000 | 1.000 | 695 |
| BI-T003 | 22 | 23 | 13/13 | 7/7 | 1.000 | 0.580 | 0.529 | 0.756 | 1.000 | 1.000 | 1150 |
| BI-T004 | 11 | 12 | 9/9 | 3/3 | 1.000 | 0.559 | 0.121 | 0.818 | 1.000 | 1.000 | 895 |
| BI-T005 | 20 | 21 | 14/14 | 5/5 | 1.000 | 0.398 | 0.092 | 0.698 | 1.000 | 1.000 | 1132 |
| BI-T006 | 21 | 22 | 19/19 | 8/8 | 1.000 | 0.706 | 0.391 | 0.806 | 1.000 | 1.000 | 1089 |
| BI-T007 | 17 | 18 | 14/14 | 6/6 | 1.000 | 0.567 | 0.421 | 0.974 | 1.000 | 1.000 | 1008 |
| BI-T008 | 15 | 16 | 12/12 | 1/1 | 1.000 | 0.641 | 0.328 | 0.676 | 1.000 | 1.000 | 935 |
| BI-T009 | 11 | 12 | 8/8 | 4/4 | 1.000 | 0.519 | 0.126 | 0.721 | 1.000 | 1.000 | 858 |
| BI-T010 | 44 | 45 | 27/27 | 5/5 | 1.000 | 0.189 | 0.166 | 0.395 | 1.000 | 1.000 | 2005 |
| BI-T011 | 32 | 33 | 25/25 | 14/14 | 1.000 | 0.376 | 0.278 | 0.860 | 1.000 | 1.000 | 1453 |
| BI-T012 | 4 | 5 | 2/2 | 0/0 | 1.000 | 0.532 | 0.249 | 0.640 | 1.000 | 0.400 | 617 |
| BI-T013 | 10 | 11 | 7/7 | 4/4 | 1.000 | 0.940 | 0.459 | 0.741 | 1.000 | 1.000 | 865 |
| BI-T014 | 13 | 14 | 10/10 | 6/6 | 1.000 | 0.717 | 0.330 | 0.675 | 1.000 | 1.000 | 897 |
| BI-T015 | 6 | 7 | 4/4 | 3/3 | 1.000 | 0.881 | 0.000 | 0.870 | 1.000 | 0.800 | 887 |
| BI-T016 | 67 | 68 | 27/27 | 2/2 | 1.000 | 0.152 | 0.064 | 0.096 | 1.000 | 1.000 | 2789 |


### Leitura da consulta (Jev) → filtro (código)

Critério pedido = Noul ≥ limiar (valor entre parênteses). `conf mín` = menor confiança entre as 7 Choices duras.

| consulta | texto | filtro | pedidos | quase pedidos (0,2–0,5) | conf mín |
|---|---|---|---|---|---|
| BI-T001 | Uma casa em Cidade Horizonte de até 650 mil, dois quartos no mínimo e uma vaga ou mais; meu cachorro precisa poder morar comigo. | casa · Cidade Horizonte · ≥2 quartos · ≥1 vagas · ≤ R$ 650 mil | pet (0.98) | — | 1.000 |
| BI-T002 | Apartamento em Cidade Aurora: até R$ 750.000 e ao menos três quartos. Não quero rua barulhenta. | apartamento · Cidade Aurora · ≥3 quartos · ≤ R$ 750 mil | rua_tranquila (0.98) | — | 1.000 |
| BI-T003 | Sobrado em Cidade Horizonte, no máximo 850 mil, ao menos dois quartos. Trabalho de casa e faço questão de sol da manhã. | sobrado · Cidade Horizonte · ≥2 quartos · ≤ R$ 850 mil | home_office (0.68), sol_manha (0.99) | — | 1.000 |
| BI-T004 | Apartamento em Cidade Horizonte com 2 quartos ou mais e pelo menos uma vaga, até 700 mil. Quero silêncio na rua e metrô a pé. | apartamento · Cidade Horizonte · ≥2 quartos · ≥1 vagas · ≤ R$ 700 mil | rua_tranquila (0.99), metro (0.99) | — | 1.000 |
| BI-T005 | No Jardim Norte de Cidade Horizonte, imóvel de até 900 mil e pelo menos dois quartos. Já reformado e com sol matinal. | qualquer tipo · Cidade Horizonte · Jardim Norte · ≥2 quartos · ≤ R$ 900 mil | sol_manha (0.98), reformado (0.98) | jardim (0.29) | 1.000 |
| BI-T006 | Na Vila Verde de Cidade Aurora, aceito qualquer tipo com pelo menos um quarto até 850 mil, mas tem de aceitar meu gato. | qualquer tipo · Cidade Aurora · Vila Verde · ≥1 quartos · ≤ R$ 850 mil | pet (0.99) | — | 0.980 |
| BI-T007 | Casa em Cidade Aurora por até 800 mil, com no mínimo dois quartos e jardim exclusivo para cultivar plantas. | casa · Cidade Aurora · ≥2 quartos · ≤ R$ 800 mil | jardim (0.99) | — | 1.000 |
| BI-T008 | Sobrado em Cidade Aurora até 800 mil, 2 quartos ou mais e uma vaga no mínimo; preciso trabalhar em casa e levar meu pet. | sobrado · Cidade Aurora · ≥2 quartos · ≥1 vagas · ≤ R$ 800 mil | pet (0.94), home_office (0.91) | — | 1.000 |
| BI-T009 | Apartamento em Cidade Horizonte com ao menos 3 quartos e 1 vaga, teto de 900 mil. Vista aberta e rua sossegada, por favor. | apartamento · Cidade Horizonte · ≥3 quartos · ≥1 vagas · ≤ R$ 900 mil | rua_tranquila (0.98), vista (0.99) | — | 1.000 |
| BI-T010 | Procuro imóvel em Cidade Aurora até 740 mil, dois quartos ou mais. Não serve se precisar de reforma; quero pronto e numa rua silenciosa. | qualquer tipo · Cidade Aurora · ≥2 quartos · ≤ R$ 740 mil | rua_tranquila (0.99), reformado (0.90) | — | 1.000 |
| BI-T011 | Qualquer tipo em Cidade Horizonte até R$ 590 mil, pelo menos 2 quartos. Precisa ter um ambiente reservado para escritório. | qualquer tipo · Cidade Horizonte · ≥2 quartos · ≤ R$ 590 mil | home_office (0.98) | — | 1.000 |
| BI-T012 | Casa de três quartos ou mais e no mínimo duas vagas em Cidade Horizonte, até 950 mil. Quero reforma concluída e sol da manhã. | casa · Cidade Horizonte · ≥3 quartos · ≥2 vagas · ≤ R$ 950 mil | sol_manha (0.99), reformado (0.97) | — | 1.000 |
| BI-T013 | Apartamento em Cidade Aurora entre 350 e 650 mil, pelo menos dois quartos, com espaço de home office e acesso ao metrô caminhando. | apartamento · Cidade Aurora · ≥2 quartos · ≥ R$ 350 mil · ≤ R$ 650 mil | home_office (0.99), metro (0.99) | — | 1.000 |
| BI-T014 | Imóvel no Centro de Cidade Horizonte, máximo de 750 mil e ao menos 2 quartos. Preciso que a reforma já tenha sido feita. | qualquer tipo · Cidade Horizonte · Centro · ≥2 quartos · ≤ R$ 750 mil | reformado (0.97) | — | 0.990 |
| BI-T015 | Sobrado em Cidade Aurora até 900 mil com pelo menos três quartos e duas vagas. Jardim privativo e rua tranquila são requisitos. | sobrado · Cidade Aurora · ≥3 quartos · ≥2 vagas · ≤ R$ 900 mil | rua_tranquila (0.99), jardim (0.99) | — | 1.000 |
| BI-T016 | Até 900 mil em Cidade Aurora, qualquer tipo, ao menos um quarto. Quero vista livre, escritório, permissão para animais e rua silenciosa. | qualquer tipo · Cidade Aurora · ≥1 quartos · ≤ R$ 900 mil | pet (0.99), rua_tranquila (0.99), home_office (0.98), vista (0.99) | — | 1.000 |


### Perda da recuperação (relevantes descartados pelo filtro ANTES do Jev): 0


### Leitura do anúncio: relevância prevista ≠ gabarito (0 de 311 recuperados)

A ordem usa o ganho esperado, não a prevista; a prevista (argmax) mede a leitura. Recortes da descrição ao lado.
