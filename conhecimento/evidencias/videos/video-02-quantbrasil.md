---
name: video-02-quantbrasil
description: QuantBrasil (Rafael Quintanilha, 20/09/2026) — teste real em produção contra DeepSeek V4 Flash e GPT-6 Astra; Jev 6–7× mais rápido e ~7× mais barato em sentimento; ~200× mais barato em "empresa mencionada?" com pré-filtro; errou o caso ambíguo (MS — vencedor 0,50, confidence 0,25) e acertou após decompor.
tipo: visao-externa
fonte: https://www.youtube.com/watch?v=VI7r1-BMN8I (42:04, pt-BR)
transcricao: fontes/videos/02-quantbrasil-por-que-o-lancamento-e-melhor-noticia.md (fora do Git)
estudado_em: 2026-09-30
---

# Vídeo 2 — "Por que o lançamento do Jev é uma notícia melhor do que parece" (QuantBrasil)

[terceiro] Publicado em 2026-09-20; 42min04s. Claude: transcrição por legenda automática. Codex: legenda
original completa e **quadros conferidos** em 23:18, 36:05 e 37:20 (números dos quadros abaixo marcados
"quadro"). Os benchmarks são relatos do autor, não testes nossos.

O vídeo mais útil dos três: o autor tem um caso em produção (análise de sentimento de notícias por
ação, hoje com DeepSeek V4 Flash devolvendo sentimento + confiança + motivo em JSON) e mediu.

## Playground ([20:17](https://www.youtube.com/watch?v=VI7r1-BMN8I&t=1217s), quadro [23:18](https://www.youtube.com/watch?v=VI7r1-BMN8I&t=1398s))
- Triagem de mensagem de aluno (curso de Python, "access denied", "não quero reembolso, quero
  assistir"): Choice de departamento (technical support / billing / teaching / other), Noul "pede
  reembolso?", Score de frustração de 4 níveis (neutro → inconveniência → frustração forte → abusivo).
- Resultado: technical support 100%; `requests_refund` 3% sim (97% "não"); frustração no nível 2 com
  confiança 100% (quadro: "4 levels 0~3" → 2). Quadro: "jev-latest 104ms + 314ms" = **~104 ms de
  inferência + ~314 ms de ida e volta de rede**, mostrados separadamente.
- A interface confirma o nome **Noul**, não `null`.
- Tirando "não quero reembolso", a probabilidade de reembolso subiu um pouco (continuou baixa).
- Inserindo um palavrão, a frustração foi para o nível mais alto (abusivo) → "moderação fica fácil".
- [16:44](https://www.youtube.com/watch?v=VI7r1-BMN8I&t=1004s): distingue classificação categórica,
  pontuação por rubrica e avaliação probabilística de uma proposição.

## Teste 1 — sentimento de notícia (Choice positivo/negativo/neutro)
6 artigos × 2 execuções = 12 chamadas por modelo.
| | DeepSeek V4 Flash (via provedor barato) | Jev |
|---|---|---|
| latência média | 2,6 s | 0,4 s (6–7× mais rápido) |
| custo projetado por 1.000 classificações | 0,14 | 0,02 (~7×; "80%+ mais barato") |
Preço citado: Jev 0,042 por milhão de entrada e 0 de saída — ~3× mais barato que o DeepSeek na
entrada e ~200× mais barato que o GPT-6 Astra.

## Teste 2 — "a empresa X é mencionada no artigo?" (Noul) ([31:50](https://www.youtube.com/watch?v=VI7r1-BMN8I&t=1910s))
Universo de 1.667 ações acompanhadas.
- **Universo inteiro** (1 Noul por ação por artigo): tempo parecido entre Jev e GPT-6 Astra; Jev
  **errou bastante**; GPT-6 acertou mas custo projetado de 507 por 1.000 artigos — impraticável.
- **Lista curta** (primeiro regex do ticker no texto, que dá falsos positivos; depois o Jev elimina
  os falsos): Jev e GPT-6 com **o mesmo resultado**, Jev ~200× mais barato e mais rápido.
- Lição: o Jev precisa do **pré-filtro em código** (candidato → Jev confirma); não é para varrer
  milhares de opções irrelevantes (bate com [limites-jev-1-13](../../modelo/limites-jev-1-13.md) #5 e
  [extracao-de-valor-pre-parseado](../../receitas/extracao-de-valor-pre-parseado.md)). A lista de
  candidatos ajuda aqui, mas não é regra universal para toda Choice.

## O caso que o Jev errou (e o conserto) — quadros [36:05](https://www.youtube.com/watch?v=VI7r1-BMN8I&t=2165s) e [37:20](https://www.youtube.com/watch?v=VI7r1-BMN8I&t=2240s)
Notícia "Trump proíbe CNN, MS NOW e Politico na Casa Branca". "MS" é ticker do Morgan Stanley;
"MS NOW" é o antigo MSNBC. Pedindo sentimento para o ticker MS:
- DeepSeek: `neutral`, confiança 0,9, motivo "sem relação com o banco" — o LLM foi inteligente.
- **Jev: `negative`** — quadro: negative 0,50 / neutral 0,49 / positive 0,01 → **`confidence` 0,25**
  (a opção escolhida tem 0,50; `confidence` é outro campo; bate com (3×0,5−1)/2); usage 668 entrada /
  39 saída. Avaliação na tela: "a false company match reached the sentiment classifier" — problema de
  pipeline. A confiança baixa sinalizou o erro.
- Conserto por desenho: Noul "o artigo referencia Morgan Stanley (MS)?" → **0,09**; "referencia
  ServiceNow (NOW)?" → **0,12**; com limiar 0,5, ambos "não" → não se pede sentimento. Quadro: state
  `{article, rules}` com as regras do que conta como referência **dentro do state**; instrução "Under
  `rules`, does `article` reference the i[ssuer]…"; IDs das perguntas gerados em código (`q1048`, `q1108`).
- Frase do autor: "Eu precisei fazer uma etapa anterior antes de passar pro Jev. No LLM eu não
  preciso, confio na inteligência dele — só que essa inteligência vem a um custo."
- [38:04](https://www.youtube.com/watch?v=VI7r1-BMN8I&t=2284s): limiar e encaminhamento dependem do risco da ação.

## Lições para nós
1. Decompor: **relevância antes de julgamento** (Noul de menção → só então o Choice de sentimento).
   As duas perguntas podem ir na mesma requisição; a ordem é de consumo no código.
2. Confiança baixa é informação: 0,25 teria mandado o caso para revisão.
3. O Jev não é "LLM mais barato": exige desenho de sistema (pré-filtro, perguntas atômicas).
4. Prompt de LLM ("responda só com JSON válido aderente ao esquema…") é mais frágil que a pergunta
   tipada.

## Confiabilidade
Teste real mas pequeno (12 chamadas no teste 1), DeepSeek por provedor barato e lento (o autor
admite), unidades de custo não ditas (presumivelmente US$). Tem propaganda do curso do autor. Saída
tipada não prova acerto semântico nem determinismo. Preços e disponibilidade mostrados são históricos.

## Relacionados
[limites-jev-1-13](../../modelo/limites-jev-1-13.md) · [confianca](../../modelo/confianca.md) · [checagem-de-citacoes](../../receitas/checagem-de-citacoes.md) · [alinhamento-de-entidades](../../receitas/alinhamento-de-entidades.md) · [jev-llm-codigo](../../decidir/jev-llm-codigo.md)
