---
name: reranking
description: Re-ranqueia a shortlist BM25 (30 candidatos) de 40 consultas jurídicas CLERC com 1 Noul por par consulta-candidato — top-1 de 5% para 18% e top-10 de 38% para 62%, 1.200 chamadas por US$ 0,0645.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/rerank_typesafe.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 9895–10454
estudado_em: 2026-09-30
---

# Re-ranking (Re-ranking)

## Problema
Milhares de documentos, uma consulta, um documento que responde. Duas etapas: (1) busca rápida (BM25, embeddings ou os dois) corta milhares em uma shortlist que roda no acervo inteiro; (2) re-ranking pontua cada candidato da shortlist contra a consulta e põe o melhor primeiro. A busca rápida acerta a shortlist mas raramente a ordem. Re-ranking só reordena; não consegue adicionar o que a busca rápida não trouxe.

## Como o Jev entra
- **state:** `{"query_excerpt": query, "candidate_passage": candidate}`. Consulta = trecho de parecer de tribunal federal dos EUA com a citação removida; candidato = uma passagem da shortlist.
- **pergunta (1 Noul, id `is_cited_source`):**
  instructions: "The query excerpt comes from a US federal court opinion and was written immediately around a citation to a precedent; the citation itself has been removed. Could the candidate passage be from that cited precedent — does it establish the specific legal proposition the query excerpt invokes at its citation point?"
  - true: "The candidate passage states or establishes the specific rule, standard, holding, or fact pattern that the query excerpt attributes to its removed citation."
  - false: "The candidate passage is merely on a similar topic or doctrine; it does not supply the specific proposition the query excerpt relies on."
  - Versão simplificada no texto explicativo: "Could this candidate passage be from the cited precedent?" / "Is this candidate the cited case?" (true "The candidate states the specific rule the query cites." / false "The candidate is only on a similar topic.").
- **chamadas:** 1 por par: 40 consultas × 30 candidatos = 1.200 chamadas independentes ("nenhuma requisição vê outra"), disparadas em paralelo com `ThreadPoolExecutor(max_workers=12)`. A pergunta vai como JSON (`is_cited_source.model_dump_json(exclude_none=True)`, decodificada com `json.loads` dentro da chamada cacheada); `client.system_one(state=..., questions={"is_cited_source": question}, model="jev-1.12")`.

Busca rápida (só BM25, `bm25s`, tokenização com `stopwords="en"`): corpus de 3.565 passagens (170 linhas do CLERC `jhu-clsp/CLERC`, arquivo `teva_train_dir/train_data.jsonl.gz`, lidas em streaming; só linhas com `positive_passages` e exatamente 20 `negative_passages`, primeiras 1.000; amostra de 170 com seed 0). Cada linha: 1 gold (passagem que a citação removida apontava) + 20 negativas; `cid` = hash sha1 de 16 caracteres do texto (dedupe). 40 das 170 são avaliadas como consultas (amostradas de `pool[20:]`, os 20 primeiros do pool ficam de fora); as demais só aparecem como candidatos. `TOP_K = 30`, `N_ROWS = 170`, `N_QUERIES = 40`; BM25 escolhe os 30 candidatos no corpus inteiro de 3.565, não só nas 20 negativas da linha.

## O que o código faz com a resposta
`reranked[q] = sorted(candidates[q], key=lambda c: -pair_scores[q][c]["noul"])`: ordena a shortlist pelo noul decrescente. Métrica: posição 1-based do gold (`gold_rank`), parcela das consultas com gold em top 1/5/10. Custo = tokens de entrada × 0,042/1e6 + tokens de saída × 0/1e6.

## Resultados medidos
Modelo `jev-1.12`; `PRICE = (0.042, 0.00)` US$ por 1M tokens, preço de 2026-08. Linha de base: BM25 sozinho.

| métrica | BM25 | + re-rank Jev |
|---|---|---|
| gold na shortlist de 30 | 100% (40/40) | (mesma shortlist) |
| top 1 | 5% | 18% |
| top 5 | 15% | 35% |
| top 10 | 38% | 62% |

Custo: 1.200 chamadas, 1.536.002 tokens de entrada e 25.200 de saída = US$ 0,0645 (todas as 40 shortlists). Latência: não declarada. Média por chamada (conta aqui, não no doc): ~1.280 tokens de entrada e ~21 de saída. O doc não compara com outro re-ranker nem com LLM geral; só com a ordem do BM25.

## Técnicas reutilizáveis
- Funil de duas etapas: busca barata no acervo inteiro + pontuação cara só na shortlist → quando o acervo é grande demais para pontuar tudo.
- Transformar "quão bem este candidato responde?" em um Noul cujos critérios (`true`/`false`) definem o que conta → score comparável em [0,1] sem inventar uma escala para um LLM geral.
- Critério `false` descreve o ruído esperado ("só é do mesmo tema ou doutrina") → separar "parecido" de "é este".
- Uma requisição por par, sem requisição ver outra → pontuação independente e paralelizável (12 threads); o ranking vem de ordenar os noul.
- Re-ranking só reordena: a qualidade do recall da etapa rápida é teto (aqui 100% em 30).
- Medir em top-K (1/5/10) contra a base da etapa rápida → mostrar o ganho em posição, não só em acerto.
- Em produção, várias perguntas sobre o mesmo par vão numa chamada só (remete a perguntas-em-paralelo e ao padrão "Speculative Fan-Out").
- Cache de cada chamada por (modelo, consulta, candidato, pergunta em JSON) → reexecutar sem custo.
- Receitas vizinhas citadas pelo doc: Noul (primitiva), Speculative Fan-Out (várias perguntas sobre um documento numa chamada), Line-by-line Search (busca por significado, não por palavra).

## Limites e pegadinhas
- Só 40 consultas, um conjunto (CLERC, jurídico); top-1 de 18% ainda é baixo em termos absolutos (7 a 8 de 40).
- Re-ranking não adiciona o que a busca rápida não trouxe; aqui o recall é 100% na shortlist de 30, favorável.
- "One question per pair" foi feito "para clareza"; o doc admite que uma aplicação real perguntaria várias coisas por par numa chamada.
- A afirmação de que Jev é "mais rápido, barato e consistente" que um LLM geral na pontuação de pares não é medida aqui (sem comparação, sem latência).
- Comentário do código: os 20 primeiros do pool ficam de fora da avaliação ("hold out"), enquanto o texto diz que as 130 linhas restantes só aparecem como candidatos; as 40 consultas vêm dos 150 restantes (não declarado no doc o destino dos 20 separados além do corte).

## Esqueleto de código
```python
is_cited_source = Noul(
    instructions=("The query excerpt comes from a US federal court opinion ... Could the candidate "
                  "passage be from that cited precedent — does it establish the specific legal "
                  "proposition the query excerpt invokes at its citation point?"),
    criteria=NoulCriteria(
        true="The candidate passage states or establishes the specific rule, standard, holding, "
             "or fact pattern that the query excerpt attributes to its removed citation.",
        false="The candidate passage is merely on a similar topic or doctrine; it does not supply "
              "the specific proposition the query excerpt relies on."),
)

def score_candidate(model, query, candidate, question_json):
    r = client.system_one(
        state={"query_excerpt": query, "candidate_passage": candidate},
        questions={"is_cited_source": json.loads(question_json)},
        model=model)
    return {"noul": r.answers["is_cited_source"].noul,
            "input_tokens": r.usage.input_tokens or 0}

pairs = [(q, c) for q in queries for c in candidates[q]]          # 40 x 30 = 1.200
with ThreadPoolExecutor(max_workers=12) as pool:
    results = pool.map(lambda p: score_candidate(MODEL, queries[p[0]], corpus[p[1]], qjson), pairs)
pair_scores = {q: {} for q in queries}
for (q, c), r in zip(pairs, results):
    pair_scores[q][c] = r
reranked = {q: sorted(candidates[q], key=lambda c: -pair_scores[q][c]["noul"]) for q in queries}
```
