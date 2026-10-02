# Rerank em corpus público pt-BR (Quati) — BM25 → Jev "o trecho responde?"

Busca por palavra traz o trecho errado em primeiro; reordenar com LLM custa caro por consulta. O irmão
[`busca-imoveis`](../busca-imoveis/README.md) mediu rerank só em catálogo sintético; este mede em **dado público
com gabarito de terceiros**: o Quati (UNICAMP, CC BY 4.0), consultas de falantes nativos sobre passagens pt-BR do
ClueWeb22, julgadas por GPT-4 em escala 0–3. Os números vêm de [`resultados-rodada1.md`](resultados-rodada1.md)
(rodada cega, preservada) e [`resultados.md`](resultados.md), gerados pelo `run.py`. Fonte, licença, sorteio e
contagens: [`preparacao.md`](preparacao.md), escrito ANTES de qualquer chamada.

## Problema
- Uma consulta curta (uma pergunta de uma frase; o texto das consultas fica fora do Git, aqui só IDs) e 20 trechos
  de ~1.000 caracteres que o BM25 trouxe; vários
  só **mencionam** o tema (nota 1 do Quati), poucos **respondem** (notas 2–3). O BM25 não distingue os dois.
- O erro caro é o trecho que responde ficar fora do top-10 (quem lê só vê 10). O rerank só reordena o que o BM25
  trouxe: relevante fora do top-20 não volta — por isso o "teto" é relatado à parte.

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Recuperar 20 candidatos | código (`bm25.py`, BM25 próprio k1 = 0,9, b = 0,4) | busca exata por termo é do código; ~22 mil passagens |
| "O trecho responde à consulta?" | Jev, um Noul por trecho (`perguntas.py`), state `{query, passage}` | julgamento semântico sim/não; o `true` descreve as notas 2–3 do Quati, o `false` a nota 1 |
| Ordenar | código (`rerank.py`): P(responde) desc., desempate pelo BM25, depois posição | não há limiar: a ordem é o produto |
| Falha (chamada, cache, resposta fora do contrato, trecho acima do teto) | código: `reordenar_seguro` devolve a ordem do BM25 **inteira**, marcada `falha` | nunca uma ordem parcial inventada; ausência de resposta não é P = 0 |
| Métricas, bootstrap, veredito | código (`run.py`) | NDCG@10 com ideal pelo gabarito inteiro; MRR@10 com relevante = nota ≥ 2 |

## Desenho
- **Preparação** (`preparar.py`, semente 20261001): o TSV de 1 milhão de passagens é lido em fluxo (1.173 MB
  transferidos) e só 26,6 MB ficam em `.local/`: as 1.896 passagens julgadas + 19.929 distratores (Bernoulli
  p = 0,02). Consulta elegível = ≥ 1 passagem com nota ≥ 1 na coleção (49 de 50). Sorteio **antes** de olhar
  qualquer resultado: 10 de ajuste + 39 de teste. Top-20 do BM25 por consulta congelado em `dados/` (só IDs,
  escore e nota). Nenhum trecho ou consulta em texto entra no repositório.
- **Variantes**: `bm25` (puro) · `sobreposicao` (fração dos termos da consulta presentes no trecho; baseline de
  rerank sem Jev) · `jev` (uma requisição por trecho, 8 em paralelo, pergunta em inglês) · `jev_pt` (a mesma em
  português, só no ajuste) · `jev_lote` (os 20 trechos num state, um Noul por `passages[i].text`, uma requisição
  por consulta) · `teto` (top-20 na ordem do gabarito).
- **Intervalos**: bootstrap sobre as consultas (1.000 reamostras, semente fixa), pareado para o Δ contra o BM25.
- **Critério** (em `perguntas.py`, no manifesto, fixado antes de abrir o teste): (1) Δ NDCG@10 ≥ 0,05 com IC de 95%
  acima de zero; (2) ≤ US$ 2,00 por mil consultas; (3) p95 por requisição ≤ 1.200 ms. Secundários: Δ MRR@10 com IC
  > 0; Jev ≥ sobreposição. Orçamento declarado ≤ 2.500 requisições.

## Resultados (`jev-1.13.0`, 2026-10-01, rodada 1 cega; a rodada 2, pós-revisão, não muda nenhum número — ver abaixo)
Ajuste: 10 consultas, **uma passada** (a redação em inglês escrita antes do rascunho ficou; nada foi alargado).
Manifesto gravado em 2026-10-01 23:57 (`perguntas.py` `d0aeb58b…`, `rerank.py` `4af21810…`, `bm25.py` `b7d56828…`,
`run.py` `4a84d1f1…`, `dados/teste.json` `66ae35af…`); o teste rodou uma vez depois disso.

| teste (39 consultas × 20 trechos) | NDCG@10 [IC 95%] | Δ vs BM25 [IC] | MRR@10 (nota ≥ 2) [IC] | Δ vs BM25 [IC] |
|---|---|---|---|---|
| bm25 | 0,387 [0,316; 0,461] | — | 0,524 [0,400; 0,646] | — |
| sobreposição | 0,376 [0,310; 0,446] | −0,011 [−0,035; +0,012] | 0,550 [0,429; 0,665] | +0,027 [−0,004; +0,081] |
| **jev** (1 req/trecho) | **0,712 [0,641; 0,774]** | **+0,325 [+0,262; +0,385]** | **0,904 [0,801; 0,981]** | **+0,380 [+0,262; +0,503]** |
| jev_lote (20 trechos/state) | 0,588 [0,512; 0,662] | +0,202 [+0,153; +0,249] | 0,780 [0,662; 0,878] | +0,256 [+0,150; +0,366] |
| teto (ordem do gabarito) | 0,767 [0,695; 0,832] | +0,381 [+0,317; +0,444] | 0,949 [0,872; 1,000] | +0,425 [+0,299; +0,547] |

- **Critério: passou os três** — Δ +0,325 [+0,262; +0,385] ✓ · US$ 0,593 por mil consultas ✓ · p95 324 ms ✓;
  secundários ✓ ✓. O Jev ganhou do BM25 em 36 consultas, empatou 1, perdeu 2; chegou a 93% do teto (0,712 de 0,767).
- **Teto do rerank**: 2 consultas (95, 117) sem nenhum trecho com nota ≥ 2 no top-20; no gabarito inteiro há 413
  trechos com nota ≥ 2 no teste, só 202 no top-20 do BM25 — metade do ganho possível morre na recuperação, e
  nenhuma métrica do rerank a recupera (lição do busca-imoveis, agora medida em dado real).
- **Noul × nota** (634 trechos julgados do teste): P(responde) média 0,10 na nota 0 · 0,26 na 1 · 0,59 na 2 · 0,90
  na 3; não julgados 0,09. Acerto a 0,5 contra "nota ≥ 2" 0,886, Brier 0,082. A fronteira 1 × 2 (menciona ×
  responde) é a mais dura: 0,26 × 0,59.
- **Custo e latência** (chamada real, 8 em paralelo): 20 requisições e ~14 mil tokens por consulta; p50/p95 por
  requisição 252/324 ms; por consulta (fila de 8 vagas) 774/978 ms. Lote: 1 requisição, ~9 mil tokens, 311/369 ms,
  US$ 0,383 por mil.
- Ajuste (10 consultas): `jev` 0,613 [+0,156 vs BM25], `jev_pt` 0,625 — a pergunta em português não ficou atrás
  (NÚCLEO §9: diferença dentro do ruído, 10 consultas); `jev_lote` 0,523.
- Custo total da construção: 1.234 requisições (orçamento 2.500: 20 rascunho reaproveitadas + 200 ajuste en + 200
  pt + 10 lote + ~8 do top-20 refeito + 780 teste + 39 lote), 1,34 milhão de tokens, **US$ 0,056**.

## O que deu certo
- O Noul por trecho leu a diferença que o BM25 não vê: em 20 consultas do teste o primeiro trecho que responde
  saiu de posição 2–15 para a 1ª (e em outras 3 subiu sem chegar à 1ª); `sobreposicao` (o rerank sem Jev) não moveu nada (Δ −0,011).
- A probabilidade cresce com a nota do gabarito (0,10 → 0,26 → 0,59 → 0,90): o Noul se comporta como grau de
  "responde", útil para ordenar mesmo sem limiar.
- Nenhuma falha operacional em 1.234 requisições; o `*_seguro` só foi exercitado pela bateria.

## O que falhou ou ficou frágil (visto no teste, NÃO corrigido)
1. **A configuração "lote" perde para a "trecho isolado"**: 0,588 × 0,712 no teste (ajuste 0,523 × 0,613). No lote
   a P média da nota 3 cai de 0,90 para 0,66 e a dos não julgados sobe de 0,09 para 0,14. **Hipótese, não medição
   da causa**: as duas configurações diferem em DUAS coisas ao mesmo tempo — o tamanho do state (1 × 20 trechos,
   limite #7) e o endereçamento (`passage` × `passages[i].text`, indireção) — e o experimento não as separa; a
   conclusão vale só para estas duas configurações. O lote é 20× mais barato em requisições e 35% em tokens, e
   entrega 62% do ganho.
2. **Perdas do Jev em NDCG** (2 de 39): consulta **22** (0,860 → 0,858: 1 relevante, já em 1º nos dois; a diferença vem
   da ordem dos trechos de nota 1 contra os de nota 0 e não julgados abaixo dele) e consulta **95** (0,389 → 0,263: nenhum trecho com nota ≥ 2 no
   top-20; só notas 0–1, P máx 0,59). À parte, as **2 consultas sem relevante no top-20** (95 e 117): nelas o MRR é
   0 para qualquer ordem; a 117 até sobe em NDCG (0,159 → 0,189) por promover trechos de nota 1. No ajuste, a 147
   (1 relevante, nota 3 em 1º no BM25) caiu para 2º: o Jev pôs à frente um trecho com nota 0 ou não julgado (P máx
   0,88) — conta como erro, e pode ser gabarito faltando.
3. **P máxima baixa em consultas com resposta**: 62 (P máx 0,22, nota 2 em 1º mesmo assim) e 167 (0,25): o Jev
   acertou a ordem por diferença relativa, não por convicção — um limiar "só mostra se P ≥ 0,5" perderia as duas.
4. **Gabarito de LLM**: kappa 0,31 com humanos [artigo]. Parte do que conta como erro do Jev é desacordo com o
   GPT-4, não com uma pessoa; 146 dos 780 trechos do top-20 nem foram julgados.

## Lições
1. **A recuperação é o teto, não o rerank**: 202 de 413 relevantes no top-20; o Jev chegou a 93% do teto. Medir o
   teto à parte é o que separa "o rerank é bom" de "a busca perde metade".
2. **Nestas duas configurações, trecho isolado > 20 trechos num state**, com custo 20×: a chamada barata não foi
   grátis em qualidade. Se a causa é o tamanho do state ou a indireção `passages[i].text` fica em aberto (uma
   terceira configuração — lotes de 5, ou 20 states de 1 trecho com o mesmo endereçamento — separaria as duas).
3. **Ordenar pela probabilidade dispensa limiar** e aguenta P absoluta baixa (consultas 62 e 167); limiar entraria
   só para "não mostrar nada".
4. **Baseline de código honesto**: sobreposição de termos ≈ BM25 (Δ −0,011): o ganho não é "qualquer rerank
   ajuda", é a leitura semântica.
5. **Palavras vazias com acento**: a bateria pegou "não" escapando da lista (normalização diferente dos tokens);
   corrigido ANTES do congelamento, top-20 refeito, ~8 requisições extras.

## Limites
- **Um corpus, subconjunto**: 21.825 passagens (julgadas + distratores aleatórios), não o 1 milhão; o BM25 sobre a
  coleção inteira traria outro top-20 (mais não julgados). 49 consultas (10/39), não 20/60 como o briefing pedia —
  o Quati tem 50 tópicos julgados.
- **BM25 próprio** sem radicalização nem afinação de k1/b; a baseline é deliberadamente a de "meia hora de código".
- **Gabarito de terceiros com lacunas**: notas de GPT-4 (kappa 0,31 com humanos), pool de top-10 de outros sistemas;
  não julgado = nota 0. O Δ mede concordância com esse gabarito.
- Um modelo (`jev-1.13.0`), uma rodada cega; perguntas em pt só no ajuste; a variante lote não foi afinada.
- Reproduzir exige `preparar.py` (download de 1,1 GB do Hugging Face) porque o texto fica fora do Git; com o
  subconjunto no lugar, o cache em `.local/publicos/rerank/cache-jev/` reproduz as 1.234 respostas sem chave.
  O manifesto guarda também o sha256 dos textos consumidos no teste (consultas e trechos do top-20, por ID): texto
  trocado em `.local/` com o mesmo ID é recusado pelo `run.py`.

## Rodada 2 (pós-revisão do Codex, NÃO cega; 2026-10-02; zero chamada nova)
Revisão adversarial sobre a rodada 1: 7 achados, todos aceitos e aplicados; o teste já estava aberto. As 1.234
respostas vieram do cache (`JEV_MODO=gravado`). O manifesto da rodada cega (2026-10-01 23:57) está em
`congelamentos-anteriores/`; `resultados-rodada1.md` ficou intocado.

| Achado | O que mudou | Efeito medido |
|---|---|---|
| 1 (grav. 2) resposta JSON válida mas rejeitada pela validação ficava no cache e era relida para sempre | `rerank.py`: só o pedido rejeitado é invalidado (`jev.invalidar`), as respostas válidas da consulta ficam; retorno seguro (ordem do BM25) igual | nenhum caso real (0 rejeições em 1.234); provado pela bateria E |
| 2 (grav. 2) julgamento cuja passagem não estava na coleção saía do ideal do NDCG | `preparar.py`: gabarito = todos os qrels da consulta; ausentes da coleção contados à parte | **0 ausentes** (as 1.896 passagens julgadas estão todas na coleção): NDCG, MRR, teto e veredito idênticos |
| 3 (grav. 2) reprodução do zero parava antes do download (qrels/tópicos não baixados) | `preparar.py` baixa e confere pelo sha256 qrels, tópicos, README e LICENSE da fonte | só reprodução |
| 4 (grav. 2) texto trocado em `.local/` com o mesmo ID passava pelo manifesto | hash dos textos consumidos no teste no manifesto; `run.py` recusa se diferir | só auditoria |
| 5 (grav. 2) consulta real do Quati (tópico 54) literal no README e na bateria | removida do README (só IDs); bateria com frases sintéticas próprias | só texto |
| 6 (grav. 3) perda do lote atribuída ao tamanho do state sem separar do endereçamento | reescrito como hipótese, conclusão limitada às duas configurações | só texto |
| 7 (grav. 3) 117 citada como segunda perda (ela melhora) | perdas corrigidas para 22 e 95, separadas das sem relevante no top-20 | só texto |

Números do teste, rodada 1 → rodada 2: **idênticos** (NDCG@10 Jev 0,712, Δ +0,325 [+0,262; +0,385]; MRR 0,904;
lote 0,588; teto 0,767; custo e p50/p95 por requisição iguais). A única coluna que varia é "ms por consulta"
(simulação da fila de 8 vagas, que segue a ordem de conclusão das threads mesmo lendo do cache: p50/p95 774/978 →
781/924 ms); não é medição nova.

**Varredura de texto do corpus no repositório** (README, `resultados*.md`, `dados/*.json`, `testa_falhas.py`,
`preparacao.md`): a única ocorrência era a consulta do tópico 54 (README e bateria); removida. `dados/` e os
relatórios só têm IDs de consulta (`query_id`) e de passagem (`clueweb22-pt…`), notas e escores.

## Como rodar
**Do zero** (cópia sem `.local/`): 1) `preparar.py` baixa os arquivos pequenos da fonte (qrels 1M, tópicos de
teste, README e LICENSE do dataset) para `.local/publicos/quati/`, confere o sha256 de cada um contra o registrado
em `preparacao.md` (fonte mudou = para), lê o TSV de 1 milhão de passagens em fluxo (1,1 GB transferidos, 26,6 MB
gravados), monta o BM25, sorteia e grava `dados/` e `.local/publicos/rerank/consultas.json`; 2) `run.py` lê os
textos de `.local/` e as respostas de `.local/publicos/rerank/cache-jev/` (sem o cache, chama a API: é outra rodada).

```
..\..\.venv\Scripts\python.exe preparar.py        # download filtrado do Quati 1M → .local/ (uma vez); top-20 e sorteio
..\..\.venv\Scripts\python.exe run.py             # ajuste + teste (recusa se o manifesto congelamento.json não bate)
..\..\.venv\Scripts\python.exe run.py ajuste      # afinação; run.py rascunho = 1 consulta; run.py congelar = grava o manifesto
set JEV_MODO=gravado                               # só o cache (fora do Git, em .local/), sem chave
..\..\.venv\Scripts\python.exe testa_falhas.py    # bateria do código: falha → ordem do BM25, ordenação, métricas, BM25 (sem chave, sem corpus)
```
No Windows, `PYTHONIOENCODING=utf-8`. Crédito: Quati — Bueno, Seiti de Oliveira, Nogueira, Lotufo, Pereira (2024),
arXiv:2404.06976, CC BY 4.0, https://huggingface.co/datasets/unicamp-dl/quati.
