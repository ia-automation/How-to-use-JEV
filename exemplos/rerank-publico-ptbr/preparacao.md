# Preparação — rerank em corpus público pt-BR (registrado ANTES de qualquer chamada ao Jev)

Protocolo: o de [`avaliar/publicos/PROTOCOLO.md`](../../avaliar/publicos/PROTOCOLO.md). Fonte e licença lidas na
origem em 2026-10-01; o que a fonte não diz está marcado "(não declarado)". Dado cru só em `.local/publicos/quati/`
(fora do Git). No repositório: código, IDs sorteados, julgamentos (IDs + nota), agregados e crédito.

## Candidato 1 — Quati (UNICAMP) — ESCOLHIDO
- Página: https://huggingface.co/datasets/unicamp-dl/quati · scripts: https://github.com/unicamp-dl/quati ·
  artigo: https://arxiv.org/abs/2404.06976 (Bueno, Seiti de Oliveira, Nogueira, Lotufo, Pereira, 2024).
- **Licença** (README do dataset, lido 2026-10-01): "Quati is licensed under Creative Commons Attribution 4.0
  International (CC BY 4.0)". O arquivo `LICENSE` do repositório é o texto da CC BY 4.0 (18.656 bytes). Uso em
  avaliação permitido com atribuição. (O repositório GitHub dos scripts é MIT; não usamos os scripts.)
- **O que é**: passagens em pt-BR nativo (subconjunto português do ClueWeb22 categoria B, segmentado em trechos de
  ~1.000 caracteres [artigo]) e consultas escritas por falantes nativos. Duas versões: 1M e 10M passagens.
- **Tamanho** (listagem da API do Hugging Face): `quati_1M.tsv` 1.173.426.846 bytes (1.119 MB); 10M em 5 partes de
  ~2.300 MB cada; qrels 1M 68.982 bytes (1.933 linhas) e 10M 174.350 bytes (4.889 linhas); 200 tópicos no total,
  50 com julgamento (`topics/quati_test_topics.tsv`, 2.751 bytes).
- **Formato dos julgamentos** (`qrels/quati_1M_qrels.txt`, formato TREC `query_id 0 passage_id score`): escala
  0–3. Definição no artigo (HTML do arXiv, lido 2026-10-01): "Irrelevant: … outside the scope of the question.
  Relevant: … pertains to the question's topic but does not provide a direct answer. Highly relevant: the passage
  answers the question, but lacks in clarity or includes unrelated information. Perfectly relevant: … answers the
  question with clarity and precision." Quem julgou: GPT-4 (`gpt-4-1106-preview`) [artigo]; concordância com
  humanos Cohen's kappa 0,31 em 24 tópicos, humano × humano 0,43 [artigo]. Pool: top-10 de vários sistemas
  (BM25, mT5, E5, ColBERT-X, SPLADE, embeddings da OpenAI, fusões) [artigo]. Média de 38,66 passagens julgadas
  por consulta na versão 1M [README].
- Contagem local dos qrels 1M (50 consultas): notas {0: 1.039, 1: 388, 2: 318, 3: 188}; consulta 2 não tem
  nenhuma passagem com nota ≥ 1; consultas 2 e 189 não têm nota ≥ 2.
- **Lacunas do gabarito, declaradas**: julgamento por LLM (kappa 0,31 contra humanos); só as passagens do pool
  foram julgadas — passagem não julgada que entrar no top-20 do BM25 conta como nota 0 (prática padrão; a fração
  é relatada); **só 50 consultas** — o briefing pedia 20 de ajuste + 60 de teste; aqui o teto do corpus manda:
  10 de ajuste + o restante elegível (39) de teste, declarado como desvio.

## Candidato 2 — mMARCO pt-BR (não usado; registrado para o caso de o Quati faltar)
- Página: https://huggingface.co/datasets/unicamp-dl/mmarco (Bonifacio et al., 2021, arXiv:2108.13897).
- Licença (página, lida 2026-10-01): "This dataset is released under Apache license 2.0". Tradução automática do
  MS MARCO (14 idiomas, português incluído); 93,8 GB no total. Formato dos julgamentos na página: (não declarado) —
  a página lista triplas de treino, consultas e coleções; os qrels seriam os do MS MARCO original (binários, ~1
  por consulta), não conferidos aqui. Não usado porque o Quati é nativo e viável.

## Decisões do preparador (antes de olhar qualquer resultado)
- Versão **1M** (qrels 1M + passagens do `quati_1M.tsv`). O arquivo é lido em fluxo (`urllib`, 1.119 MB
  transferidos) e **só o subconjunto é gravado**: todas as passagens julgadas nos qrels 1M + amostra aleatória de
  passagens não julgadas (distratores; Bernoulli p = 0,02 com semente `20261001`, ≈ 20 mil).
- Coleção da busca = esse subconjunto. BM25 próprio (k1 = 0,9, b = 0,4 — valores do Anserini para passagens;
  tokens = NFKD sem acento, minúsculas, `[a-z0-9]{2,}`, lista curta de palavras vazias). Sem dependência nova.
- Consulta elegível = tópico com julgamento e ≥ 1 passagem com nota ≥ 1 na coleção carregada. Sorteio com
  semente: 10 de ajuste, o resto de teste. Hashes das listas em `preparacao.json` e `congelamento.json`.
- Cada consulta leva os **20 primeiros do BM25**; nota do gabarito por passagem gravada em `dados/` (IDs e
  notas, nunca o texto).
- "Relevante" binário (MRR@10, teto do rerank) = nota ≥ 2 ("answers the question" — é o que o Noul pergunta);
  NDCG@10 graduado com ganho 2^nota − 1 e ideal pelo gabarito INTEIRO da consulta (passagens julgadas fora do
  top-20 do BM25 pesam contra).
- Orçamento declarado: ≤ 2.500 requisições. Plano: ajuste por trecho em inglês 10 × 20 = 200 (+200 se houver
  2ª redação), variante em português 200, variante "20 trechos num state" 10; teste por trecho 39 × 20 = 780 e
  lote 39. Total previsto ≈ 1.430.

<!-- contagens: início (gerado por preparar.py) -->
## Contagens (geradas por `preparar.py`, antes da API)

- Download em fluxo: 1173 MB transferidos (1000000 linhas); gravados 26.6 MB em `.local/publicos/quati/quati_1M.subconjunto.jsonl` (1896 julgadas + 19929 distratores, p = 0.02).
- Coleção da busca: **21825** passagens (1896 julgadas, 19929 distratores); sha256 dos IDs `1f44cbc09c367900…`; qrels sha256 `aafab4294572a043…`; tópicos `61936c7b582b3d9b…`.
- BM25 k1 = 0.9, b = 0.4, top-20. Elegíveis **49** de 50; excluídas {2: 'nenhuma passagem com nota ≥ 1'}.

| parte | n | relevantes (nota ≥ 2) no gabarito | no top-20 do BM25 | consultas sem relevante no top-20 (teto) | não julgadas no top-20 | sha256 dos IDs |
|---|---|---|---|---|---|---|
| ajuste | 10 | 93 | 49 | 1 | 45/200 | `1958c7ad921d89eb…` |
| teste | 39 | 413 | 202 | 2 | 146/780 | `165495753716f405…` |

Julgamentos cuja passagem NÃO está na coleção (ficam no ideal do NDCG, contados à parte): {'ajuste': 0, 'teste': 0}.

IDs: ajuste [9, 13, 60, 98, 127, 147, 154, 170, 181, 189] · teste [1, 11, 15, 17, 20, 21, 22, 24, 26, 28, 47, 49, 51, 54, 62, 64, 68, 84, 95, 105, 113, 115, 117, 126, 128, 136, 152, 153, 160, 161, 163, 167, 172, 180, 182, 193, 195, 196, 199]
<!-- contagens: fim -->
