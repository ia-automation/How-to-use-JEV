---
name: classificacao-hierarquica
description: Classifica um documento até a folha de uma taxonomia profunda com um Choice por nó e beam search paralelo (K=3) por média geométrica das probabilidades das arestas; em 4 exemplos o beam acertou 4/4 e o greedy 2/4.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/hierarchical_classification.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 7898–8772
estudado_em: 2026-09-30
---

# Classificação hierárquica (Hierarchical classification)

## Problema
Muitos dados são hierarquias: taxonomias, sistemas de arquivos, estruturas de site, bases de código, organogramas, ontologias biológicas, skills de LLM, políticas de moderação. Objetivo: descer da raiz até a folha correta (a classificação final). Cada nó é um `Choice` cujas opções são seus filhos diretos. **Greedy**: escolhe o filho mais provável e descarta o resto; um erro cedo não se recupera. **Beam**: mantém K caminhos plausíveis e classifica todas as fronteiras em paralelo; evidência mais fundo pode consertar uma decisão inicial ambígua. Benefícios extras citados: observabilidade (em quais nós ocorrem os erros; quantas vezes cada nó/aresta é percorrido) e testabilidade (teste unitário e medição do impacto de mudanças na hierarquia).

Hierarquias usadas: CPC 2026.05 (patentes), Shopify 2026-02 (categorias de produto), MeSH 2026 (biomédico; é um DAG, então cada descritor é expandido em todos os seus caminhos de tree-number), CookSafe files (repositório do próprio cookbook, de pastas a arquivos; snapshot 2026-08-06). Quantidades de nós: calculadas em tempo de execução, não declaradas no texto.

## Como o Jev entra
- **state:** o texto do documento (string), o mesmo em todas as chamadas da busca.
- **perguntas:** UM `Choice` por nó visitado, nome `child`:
  - texto literal: "Which direct child category best matches this document?"
  - `criteria` = `{ "c0": <rótulo do filho 0>, "c1": <rótulo do filho 1>, ... }` — chaves opacas `c{i}` (mapa reversível chave→rótulo) com o rótulo do filho como descrição. A ordem das opções é a ordem dos irmãos na árvore e "faz parte da pergunta, não da apresentação" (comentário do carregador do codebase).
  - Nó com 1 só filho: nenhuma chamada; devolve `{filho: 1.0}` (não conta como decisão).
  - Resposta lida: `response.answers["child"].probabilities[chave]` → distribuição sobre os rótulos dos filhos.
- **chamadas:** 1 chamada por nó expandido. No beam, todos os candidatos expansíveis da rodada vão em paralelo (`ThreadPoolExecutor(max_workers=BEAM_WIDTH)`), então K caminhos custam ~1 nível de latência por rodada ("extra exploration adds little wall-clock latency" — afirmação do texto, sem medição). Os 4 exemplos rodam também em paralelo entre si (`max_workers=len(HIERARCHIES)`). Modelo `jev-1.12`; `RetryPolicy(max_retries=5, backoff_initial=1.0, backoff_max=20.0)`; `choose` é cacheada por (documento, tupla de rótulos).

## O que o código faz com a resposta
Constantes: `BEAM_WIDTH = 3`, `MAX_DEPTH = 12`, `EPSILON = 1e-9`.

**Pontuação de caminho:** `path_score = product(edge_probabilities) ** (1 / decisions)` (média geométrica; normaliza por comprimento para comparar folhas rasas e fundas). Só contam como "decisão" as arestas de nós com mais de um filho (`is_decision = len(probabilities) > 1`); aresta forçada multiplica por 1 e não incrementa `decisions`. Probabilidade usada = `max(p, EPSILON)`. Com 0 decisões, score = 1,0.

**Beam search passo a passo (`beam_search`):**
1. Beam inicial = um candidato: caminho `()`, produto 1.0, 0 decisões, score 1.0.
2. Repetir até `MAX_DEPTH` (12) rodadas:
   a. `expandable` = candidatos do beam cuja subárvore (filhos do último nó) não é vazia; `finished` = candidatos já em folha.
   b. Se não há expansíveis, parar.
   c. Para cada expansível, em paralelo, `choose(documento, tupla dos filhos)` → distribuição de probabilidade sobre os filhos.
   d. Para CADA filho de CADA expansível (todos, sem corte por nó), criar o candidato estendido (`extend_candidate`: multiplica o produto, incrementa decisões se houve decisão, recalcula o score).
   e. Novo beam = os K=3 melhores por `score` entre `finished + expanded` (folhas já completas competem com as expansões).
   f. Registrar os caminhos retidos e os registros (pai, probabilidades) da rodada.
3. Ordenar o beam por score; o primeiro é a classificação final (folha do caminho de maior média geométrica).

**Greedy (`greedy_search`):** a cada nível, `max` da distribuição; acumula produto/decisões do mesmo jeito; para na folha ou em `MAX_DEPTH`. Rodado à parte (para comparação); reutiliza o cache de `choose`.

**Separação:** `separation = top_path_score / second_path_score` (segundo = `beam[1]`; dividido por `max(second, EPSILON)`). Perto de 1x = ambíguo; razão grande = separação clara. É métrica de leitura, NÃO usada na poda. Exibida como ">999×" acima de 999.

**Notas do texto sobre a métrica:**
- Uma métrica alternativa como `min(top_prob/second_top_prob)` otimizaria caminhos com decisões muito claras em todo nó.
- Para hierarquias muito fundas (mais de ~10 camadas), usar `exp(mean(log(probs)))` em vez de `product ** (1/decisions)` para evitar erro de precisão.

**Procedimento de carga (resumo):** CPC: XML em zip, raízes = nível 2, rótulo = `"{símbolo} {título}"`; Shopify: linhas `id : A > B > C` viram caminhos; MeSH: cada tree-number vira caminho prefixado pela categoria (A Anatomy … Z Geographicals); CookSafe: lista congelada `codebase_files.txt` (um caminho por linha, prefixo "CookSafe"), congelada de propósito para que a taxonomia e todos os números não dependam do checkout do leitor.

## Resultados medidos
Quatro exemplos rotulados; beam K=3 acertou 4 de 4, greedy acertou 2 de 4 (o beam recuperou CPC e Shopify).
| Hierarquia | Documento (resumo) | Folha esperada | Greedy | Beam K=3 |
|---|---|---|---|---|
| CPC patents | resumo de patente: poleiro de madeira para aves, travessas, montado em aviário | A01K31/12 Perches for poultry or birds, e.g. roosts | E99Z99/00 Subject matter not otherwise provided for in this section (errado) | A01K31/12 ... (correto) |
| Shopify products | anúncio: prateleira-cama de janela com ventosas e almofada lavável para um gato | Cat Window Beds & Perches | Pet Chairs (errado) | Cat Window Beds & Perches (correto) |
| MeSH | resumo clínico de doença de Crohn (inflamação transmural, lesões salteadas, granulomas não caseosos, infliximabe) | C06.405.469.432.500 Crohn Disease | igual (correto) | igual (correto) |
| CookSafe files | "find the experimental Python module under x/eugene that implements BM25, dense, and fused retrievers for legal RAG" | retrievers.py | retrievers.py (correto) | retrievers.py (correto) |
Colunas "mean p" e "top/second" são calculadas pelo código mas os valores não aparecem no texto. Latência e custo: não declarados no doc.

## Técnicas reutilizáveis
- Hierarquia → uma pergunta `Choice` por nó com os filhos diretos como opções → quando a classificação é uma descida em árvore; o erro fica localizável por nó.
- Chaves opacas `c0..cn` + mapa reversível para rótulo → evita rótulos longos/ambíguos/com caracteres como chaves de opção.
- Beam paralelo sobre probabilidades completas (não só top-1) → quando erro cedo é caro e a chamada é barata/paralela; K caminhos ~ mesma latência.
- Média geométrica (normalizada por decisões) para comparar caminhos de comprimentos diferentes → folhas rasas e fundas justas; contar só nós com mais de uma opção.
- Folhas finalizadas permanecem no beam e competem com as expansões → a busca pode terminar antes do fundo.
- Razão top/segundo como indicador de ambiguidade (não de poda) → sinalizar casos para revisão.
- Nó com filho único resolvido sem chamada → economiza chamadas e não distorce o score.
- Piso EPSILON nas probabilidades → evita log/produto zero.
- Log-espaço (`exp(mean(log p))`) para árvores muito fundas.
- Congelar a taxonomia (snapshot versionado) e registrar a ordem dos irmãos como parte da pergunta → resultados e cache reprodutíveis.
- Cache de `choose` por (documento, rótulos) → greedy e beam compartilham chamadas.
- Observabilidade por nó: guardar os registros (pai, probabilidades) de cada decisão → achar nós onde ocorrem os erros e testar mudanças na hierarquia.

## Limites e pegadinhas
- Amostra minúscula: 4 documentos, 1 por hierarquia; "4/4 vs 2/4" não é estimativa de acurácia.
- Greedy no CPC caiu num nó "Subject matter not otherwise provided for" (catch-all): armadilha típica de taxonomias.
- O código usa `product ** (1/decisions)` mesmo com `MAX_DEPTH = 12`, apesar do comentário "Use log space for very deep trees" e da nota do texto recomendando `exp(mean(log))` acima de ~10 camadas (snapshot: código nas linhas 8556–8557, nota nas linhas 7959–7962). O produto usa `max(p, EPSILON)`; o efeito prático não é medido no doc.
- Observação do código: `separation_ratio` lê `beam[1]`; se o beam final tiver um só candidato, falharia (não tratado no doc).
- Cada chamada de nó contém TODOS os filhos como opções; tamanho das listas de irmãos em CPC/Shopify/MeSH não é declarado; nó muito largo = pergunta longa.
- "Leaf" do CookSafe é só o nome do arquivo (`retrievers.py`); a comparação é por rótulo, que pode não ser único.
- Em MeSH (DAG) a expansão por tree-number duplica descritores em várias posições.
- Latência do beam "quase igual à do greedy" é afirmação do texto, sem medição.

## Esqueleto de código
```python
def child_question(labels):
    keys = {f"c{i}": label for i, label in enumerate(labels)}
    return Choice(instructions="Which direct child category best matches this document?",
                  criteria=keys), keys

@json_cache
def choose(state, labels):
    if len(labels) == 1: return {labels[0]: 1.0}
    question, keys = child_question(labels)
    r = client.system_one(state=state, questions={"child": question}, model="jev-1.12")
    p = r.answers["child"].probabilities
    return {label: p[key] for key, label in keys.items()}

def extend_candidate(c, label, probs):
    is_dec = len(probs) > 1
    prod = c["probability_product"] * (max(probs[label], 1e-9) if is_dec else 1.0)
    n = c["decision_count"] + is_dec
    return {"path": c["path"] + (label,), "probability_product": prod,
            "decision_count": n, "score": prod ** (1 / n) if n else 1.0}

# por rodada (BEAM_WIDTH=3, MAX_DEPTH=12):
#   expandable -> choose(doc, filhos) em paralelo -> estende todos os filhos
#   beam = sorted(finished + expanded, key=score, reverse=True)[:3]
# separation = beam[0].score / max(beam[1].score, 1e-9)
```
