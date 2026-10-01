---
name: contradicoes-da-documentacao
description: Divergências dentro da documentação TypeSafe (prosa × OpenAPI × SDKs × receitas) e erros das próprias receitas, com linha do snapshot e o que ficou FECHADO pela medição de 2026-09-30 (tetos 10/255 impostos com 400, instructions opcional, nível null 422, state null 422, fórmula de confiança só em Choice e Score-3).
tipo: pendencia
fonte: https://docs.typesafe.ai (snapshot llms-full-2026-09-30.txt e páginas individuais) · https://api.typesafe.ai/openapi.json (spec 0.2.0) · medições de 2026-09-30
estudado_em: 2026-09-30
---

# Contradições da documentação

Fusão de `memoria/perguntas-abertas.md` (Claude, seção de contradições), `memory/open-questions.md` (Codex,
"Contratos que merecem cuidado") e da triagem E1–E4/C1–C4 de `lacunas-fechadas.md` (originais em
`.local/antigos/2026-09-30/`). Linhas "l." referem-se a `fontes/docs/llms-full-2026-09-30.txt` (fora do Git;
página viva: https://docs.typesafe.ai/llms-full.txt). O que ainda precisa de medição está em [pendencias](pendencias.md).

## Contrato: prosa × OpenAPI × SDK — situação após medir
| Ponto | Prosa | OpenAPI 0.2.0 / SDK | Situação |
|---|---|---|---|
| Teto de níveis do Score | "at least two … accepts up to 10" | `minItems=1`, sem `maxItems`; JS exige 2; Python só recusa lista vazia | **FECHADO** — 11 níveis → 400; 1 nível → 200 (inútil) |
| Teto de opções da Choice | 255 (l. 231, 9886, 11240, 13801) | sem `maxProperties` | **FECHADO** — 256 → 400; 255 → 200 |
| `instructions` | obrigatório na página `/api` | opcional/nulo no OpenAPI e nos dois SDKs | **FECHADO** — omitida/`null` → 200; enviar mesmo assim (o ID não vai ao modelo) |
| Nível `null` no Score | — | tipo JS aceita ("null leaves a score undescribed"); OpenAPI não | **FECHADO** — 422 |
| `state: null` | — | tipo JS aceita; Python recusa `None` | **FECHADO** — 422 |
| Erros | 401/422/429/529 na prosa | OpenAPI só 200 e 422 (`detail[]` com `loc`/`msg`/`type`) | **Ampliado** — existe **400** com corpo `{detail:{error_type,message}}` fora do doc e do OpenAPI |
| `usage` | saída não cobrada | inteiros obrigatórios; Python tipa `int \| None` | documental: tolerância do SDK não muda o contrato |
| `legend` estruturada | exemplo de Score com objetos | `legend` aceita string/objeto/array | fechado documentalmente (sem teste nosso) |
| Fórmula de `confidence` | aproximação do demo para 3 opções, `(3·máx−1)/2` (`paginas/confidence.md` l. 28–32) | nenhuma no contrato | **Medido** — bate em Choice n=2…8 e Score-3; não em Score 4–5. Não é contrato: usar o campo |
Todas as medições: [medicoes](medicoes-2026-09-30.md#contrato-da-api-fronteiras). Nota de referência: [api-http](../construir/api-http.md).
Divergência menor: a receita de classificação diz que a Choice "funciona de forma confiável até cerca de 240
opções" (orientação de qualidade), enquanto 255 é o teto aceito pelo servidor.

## Dentro da documentação e das receitas
- Paralelismo: a página Primitives diz "13 perguntas juntas = **11,5×** mais barato e **9,6×** mais
  rápido" (l. 13577); a receita e o índice dizem **12,2× / 10,0×**. Execuções diferentes.
- A razão 10,0× de latência soma as 13 chamadas como se fossem sequenciais; o próprio doc diz que em
  paralelo a diferença encolhe (l. 9237, 9498–9520).
- Function calling: confiança 0,82 maior que o argumento mais fraco (0,78), contra a regra "confiança =
  julgamento menos certo" (l. 7860–7866).
- O agent skill oficial aponta um "migration guide" (`/migrating-to-v1.md`) que responde **Page Not Found**.
- Cookbooks rodaram em `jev-1.12` (ago/2026) e alguns em `jev-latest`→`jev-1.13.0`; números não
  comparáveis entre si. Custos são "históricos" (0,042/0) e não recalculados.
- Autoconsistência (choices): latência do Jev medida sequencial, LLMs num pool de 16 vias — os fatores
  7× a 114× não comparam condições iguais (l. 5513, 5585).
- Autoconsistência (nouls): "desvio menor que todos os LLMs" sem os números dos LLMs no texto (l. 6062).
- Cascata SDE: parse falho vira `{}` e o portão **aceitaria** em vez de escalar (l. 10750–10756 × 10918;
  conferência estática do Codex em [cascata-sde](../receitas/cascata-sde.md)); ganho agregado de 100 prompts só em gráfico.
- Guardrails: severidade alta sem nenhum perigo disparado dá `pass`; `self_harm` entre 0,35 e o
  limiar de ação cai em `review` (l. 9013–9023). Exemplos ilustram, não medem acerto.
- Alinhamento de entidades: diz "sem limiar", mas o arredondamento cria cortes em 0,5 e 1,5;
  `known_same_as` é carregado e nunca comparado → sem acurácia reportada (l. 7299+).
- Classificação hierárquica: nota recomenda média geométrica acima de 10 camadas, o código usa
  produto com `MAX_DEPTH = 12` (l. 7959 × 8556); amostra de 4 documentos.
- Datas: "Six questions across four short documents", mas são 7 Choices e 6 exemplos (l. 7033).
- Structure recovery: custo no texto US$ 0,0015, saída impressa US$ 0,0003, conta dá ~US$ 0,0004 (l. 1374, 1861).
- Busca linha a linha: comentário "ausente ≤ 0,05", caso ausente leu 0,14 (l. 11316).
- Sugestão de skill: 16,8% de 315 ≈ 53 erros, a análise fala em 36 (os 17 restantes são turnos sem
  carga); pedidos de teste escritos por Sonnet a partir do próprio SKILL.md (mais fáceis que reais).
- Reranking: top-1 de 18% é baixo em absoluto; 40 consultas, um domínio; sem latência.
- SDK Python: padrões confirmados no `SdkSignature` de `sdk/python/api/retries.md` (componente ausente do
  texto consolidado): 2 retries, 0,5→5 s, jitter 0,25, 408/429/5xx e orçamento total padrão de 30 s.

## Correções que os dois estudos fizeram um no outro (histórico)
- "Fórmula de confiança não publicada" (Claude) → há aproximação publicada no demo, não contratual (E1).
- "Padrões de RetryPolicy Python não declarados" (Claude) → declarados na assinatura (E2).
- "`instructions` obrigatório" (Codex, seguindo a prosa) → opcional no OpenAPI (E3), agora medido.
- "Score aceita `null`" (nota JS) → só no tipo JS (E4), agora medido 422.
- "Nenhuma serve nunca vem de Choice", "custo não cresce com perguntas", "confiança composta = mínimo"
  (Claude) → relativizados pelo Codex ([padroes-das-receitas](../receitas/padroes-das-receitas.md)).
- Contagens: "17 receitas" e "111 páginas" → 18 cookbooks + 1 demo; 112 arquivos de página (inclui o
  retorno Page Not Found). Ver [proveniencia](proveniencia.md).
