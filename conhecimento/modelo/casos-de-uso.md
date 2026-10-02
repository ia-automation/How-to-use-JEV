---
name: casos-de-uso
description: Mapa de casos de uso do doc — 5 categorias (automação, tempo real, map-reduce em big data, verificação universal, harness), 10 formatos de decisão e exemplos por setor, com a receita que demonstra cada um.
tipo: conceito
fonte: https://docs.typesafe.ai/concepts/use-case-map · /introduction/coding-agents
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 996–1183 e 12485–12494
estudado_em: 2026-09-30
---

# Casos de uso

## Cinco categorias
| Categoria | Tese |
|---|---|
| Software de automação com IA | rodar 1 milhão de vezes em segundo plano, sem copiloto humano; código (não markdown) dono do fluxo |
| Tempo real | ~150 ms: decide mais rápido que a percepção humana; dá para jogos e UI |
| Map-reduce sobre big data | ~100× mais barato: busca em corpus gigante, classificar traces de agente, extrair features |
| Verificação universal | checar prompt de entrada, extrações, traces de raciocínio, tool calls de outra IA — jailbreak, citação errada, alucinação — a uma fração do custo da chamada do LLM |
| Engenharia de harness | roteamento de modelo, recuperação semântica de contexto, guardrails, classificar traces |

## Formatos de decisão → receita que demonstra
| Formato | Quando | Receita |
|---|---|---|
| Classificação | uma categoria conhecida vence | [classificacao-com-confianca](../receitas/classificacao-com-confianca.md), [classificacao-hierarquica](../receitas/classificacao-hierarquica.md) |
| Detecção | probabilidade de uma propriedade estar presente | [guardrails-llm](../receitas/guardrails-llm.md) |
| Pontuação | resposta numa rubrica ordenada | [pontuacao-composta](../construir/padroes/pontuacao-composta.md), [autoconsistencia-nouls](../receitas/autoconsistencia-nouls.md) |
| Roteamento | categoria escolhe o próximo caminho do código | [roteamento-por-intencao](../construir/padroes/roteamento-por-intencao.md), [function-calling](../receitas/function-calling.md), [sugestao-de-skill](../receitas/sugestao-de-skill.md) |
| Busca | achar itens que batem com consulta em linguagem natural | [busca-linha-a-linha](../receitas/busca-linha-a-linha.md) |
| Recuperação | contexto/registro mais relevante para o fluxo | [classificar-passagens-rag](../receitas/classificar-passagens-rag.md) |
| Ranqueamento | ordenar por relevância/qualidade | [reranking](../receitas/reranking.md) |
| Verificação | checar modos de falha de um artefato | [checagem-de-citacoes](../receitas/checagem-de-citacoes.md), [cascata-sde](../receitas/cascata-sde.md) |
| Feature para ML | sinais semânticos para modelo clássico | [autoresearch-de-features](../receitas/autoresearch-de-features.md) |
| Extração estruturada | campos conhecidos de texto livre | [extracao-de-datas](../receitas/extracao-de-datas.md), [extracao-de-valor-pre-parseado](../receitas/extracao-de-valor-pre-parseado.md), [alinhamento-de-entidades](../receitas/alinhamento-de-entidades.md), [recuperacao-de-estrutura](../receitas/recuperacao-de-estrutura.md) |

## Exemplos por setor (resumo do doc)
- **Busca/RAG**: substituir ou complementar embeddings; relevância consulta↔candidato; rerank
  par a par; *cross-encode*; escolher contexto para o LLM.
- **Roteamento de modelo**: roteador próprio que escolhe qual LLM recebe cada prompt; intenção,
  domínio, dificuldade e risco; escalar para modelo caro.
- **Guardrails**: checagem semântica em toda entrada, saída e tool call; jailbreak, injeção de prompt,
  violação de política, exposição de dado sensível; registrar resultados e probabilidades.
- **Lint semântico de código/texto**: convenções do time como checagens, rodando no CI.
- **Features preditivas**: probabilidades como features junto de dado estruturado; *autoresearch*
  propõe definições e mede valor preditivo contra verdade separada.
- **Recrutamento**: currículo contra critério explícito; competências; casar candidato-vaga; incerto → humano.
- **Geração de leads**: perfil de empresa/biografia/mensagem contra ICP; aderência de setor e
  maturidade; dor, relevância, intenção de compra; priorizar e rotear.
- **Atendimento**: classificar tickets (assunto, área, intenção); extrair compromissos de ligações;
  urgência, frustração, risco de churn, pedido de reembolso; conferir resposta contra política.
- **Seguros, crime financeiro, jurídico/compliance, marketplaces, moderação, publicidade, games,
  risco, previsão de demanda, grafos de conhecimento** — sempre o mesmo molde: classificar, detectar,
  pontuar, rotear o incerto para humano.
- Moderação cita explicitamente **conversas automáticas de SDR** e **pedidos de opt-out**.

## Quando vale a pena (página "coding agents")
Rotear para um conjunto fixo de destinos sabendo a confiança; pontuar numa rubrica e ramificar pelo
número; checar se uma afirmação vale para um documento antes de agir; **trocar um prompt frágil que
pede "devolva JSON" por uma chamada que devolve valor tipado por construção**.

## Prompt de brainstorm sugerido pelo doc
"Using the TypeSafe skill, explore the project and find opportunities for using intelligent
judgement to stand in for complex parsing or other fragile code."

## Programação e agentes (casos externos, 2026-10-01) [terceiro]
Família que o doc chama de "harness" e que apareceu com mais força fora do doc: guarda de tool-call de agente de
código (irreversível / fora da tarefa / vindo de conteúdo lido), juiz de eval no lugar de LLM-as-judge, lint
semântico de PR em CI, SQL semântico (`WHERE jev(linha, 'condição')`), injeção de prompt em resultado de
ferramenta, agente de navegador que escolhe operação + alvo. Números, fontes e limites: [casos-externos](../evidencias/casos-externos.md).
Exemplos nossos medidos: [guarda-tool-call](../../exemplos/guarda-tool-call/README.md) · [juiz-de-eval](../../exemplos/juiz-de-eval/README.md) ·
[lint-semantico-de-diff](../../exemplos/lint-semantico-de-diff/README.md) · [auditor-de-evidencia](../../exemplos/auditor-de-evidencia/README.md) ·
[injecao-em-ferramenta](../../exemplos/injecao-em-ferramenta/README.md) · [selecao-de-skill](../../exemplos/selecao-de-skill/README.md).
Atendimento e imóveis, medidos na mesma onda: [imovel-errado](../../exemplos/imovel-errado/README.md) ·
[conferencia-de-promessas](../../exemplos/conferencia-de-promessas/README.md) · [opt-out-lgpd](../../exemplos/opt-out-lgpd/README.md) ·
[proxima-pergunta](../../exemplos/proxima-pergunta/README.md) · [imovel-duplicado](../../exemplos/imovel-duplicado/README.md) ·
[repeticao-ou-revisao](../../exemplos/repeticao-ou-revisao/README.md) · [requisito-mudou](../../exemplos/requisito-mudou/README.md) ·
[motivo-de-perda](../../exemplos/motivo-de-perda/README.md) · [compromisso-real](../../exemplos/compromisso-real/README.md).
Operação e agentes, tarde de 2026-10-01: [triagem-de-alerta](../../exemplos/triagem-de-alerta/README.md) ·
[compactacao-de-contexto](../../exemplos/compactacao-de-contexto/README.md) (reprovado para descarte automático) ·
[roteador-email](../../exemplos/roteador-email/README.md) (dado real, concordância com produção).
Madrugada de 2026-10-02: [sql-semantico](../../exemplos/sql-semantico/README.md) ·
[triagem-de-documentos](../../exemplos/triagem-de-documentos/README.md) (mapa por seção × documento inteiro) ·
[supervisor-de-automacao](../../exemplos/supervisor-de-automacao/README.md) (erro caro zero, critério de acerto reprovado) ·
[comparador-de-propostas](../../exemplos/comparador-de-propostas/README.md) ·
[rerank-publico-ptbr](../../exemplos/rerank-publico-ptbr/README.md) (dado público, gabarito de terceiros) ·
[jev-x-llm](../../exemplos/jev-x-llm/README.md) (um LLM barato nos mesmos testes) ·
[latencia-interface](../../exemplos/latencia-interface/README.md) (p95 303 ms: não cabe em 300).

## Relacionados
[o-que-e-o-jev](o-que-e-o-jev.md) · [como-construir](../construir/como-construir.md) · [casos-externos](../evidencias/casos-externos.md) · receitas: [índice](../INDICE.md#receitas-cookbooks-destilados)
