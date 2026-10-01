---
name: jev-desenhar
description: Decidir se um fluxo usa código, Jev (TypeSafe, System One), LLM ou um híbrido, e desenhar as decisões do Jev — state, perguntas Choice/Score/Noul, composição em código, limiares e desfecho da incerteza. Use quando a tarefa envolver Jev, TypeSafe ou System One; quando um fluxo precisa classificar, rotear, pontuar, detectar, ranquear, verificar ou escolher entre candidatos em escala, rápido e barato; quando um prompt "responda só com JSON" puder virar decisão tipada; ou para revisar perguntas e limiares de um código que já usa o Jev. Não serve para trocar o modelo de um agente de programação.
---

# Desenhar com o Jev

Procedimento. Os fatos moram em `conhecimento/` (raiz do repositório = dois níveis acima desta pasta);
comece pelo NÚCLEO em [AGENTS.md](../../AGENTS.md) e abra só as notas que o caso pede. Se a skill estiver
sozinha, use os docs vivos: https://docs.typesafe.ai/llms.txt (acrescente `.md` a qualquer página).

## Procedimento
1. **Comece pelo comportamento.** O que a aplicação vai mostrar, selecionar, mudar ou encaminhar, e quem
   consome cada resposta? Volte daí para os julgamentos necessários.
2. **Triagem código × Jev × LLM** pelas 5 perguntas de [jev-llm-codigo](../../conhecimento/decidir/jev-llm-codigo.md):
   regra, cálculo, busca exata, data, contagem, permissão e efeito → código; texto novo → LLM; espaço
   fechado de resposta → Jev; raciocínio de várias etapas ou valor impossível de listar → LLM ou decompor.
   Se passar por "Jev" e "LLM", escolha um dos híbridos da nota.
3. **Ache a receita-irmã** (tabela abaixo) e leia a nota dela antes de desenhar — costuma ter decomposição
   melhor que um classificador genérico. Síntese: [padroes-das-receitas](../../conhecimento/receitas/padroes-das-receitas.md).
4. **Monte o state enxuto** ([state](../../conhecimento/modelo/state.md)): objeto com campos nomeados, só o
   que as perguntas usam, IDs que o código precisa para religar resultados. Filtre/recupere em código antes
   (regex, BM25, SQL). Áudio, imagem e vídeo viram texto antes.
5. **Escolha a primitiva e escreva cada pergunta** ([primitivas](../../conhecimento/modelo/primitivas.md),
   [estrutura-nas-perguntas](../../conhecimento/modelo/estrutura-nas-perguntas.md)) passando pelo checklist abaixo.
6. **Agrupe perguntas por state**, inclusive especulativas com premissa explícita
   ([fan-out-especulativo](../../conhecimento/construir/padroes/fan-out-especulativo.md)). Outra chamada só
   quando a resposta decide o próximo state ou as próximas opções, ou quando limite/isolamento exigem.
7. **Componha em código** ([pontuacao-composta](../../conhecimento/construir/padroes/pontuacao-composta.md))
   e ponha **perguntas + limiares num arquivo só de constantes** — é o que o humano revisa. Três faixas
   (age / revisa / não age), limiar por risco da ação ([confianca](../../conhecimento/modelo/confianca.md),
   [roteamento-por-confianca](../../conhecimento/construir/padroes/roteamento-por-confianca.md)).
8. **Dê desfecho a cada ramo**: sem informação, incerto, fora das categorias, falha da chamada
   ([integracao-segura](../../conhecimento/construir/integracao-segura.md)).
9. **Entregue o desenho** com state, perguntas, tipos, dependências, consumidor, custo/latência estimados
   ([modelos-precos-limites](../../conhecimento/modelo/modelos-precos-limites.md),
   [medicoes](../../conhecimento/evidencias/medicoes-2026-09-30.md)) e o plano de avaliação
   ([jev-avaliar](../jev-avaliar/SKILL.md)). Limiares são parâmetros a medir, não fatos do doc.

## Checklist de cada pergunta
- [ ] Uma condição / uma dimensão / uma decisão (senão dividir e combinar em código), sem destruir a
      relação que está sendo julgada.
- [ ] Texto completo em `instructions` (o ID não vai ao modelo); aponta a parte do state com caminho
      entre crases (`` `ticket.messages[0].text` ``).
- [ ] Literal: diz exatamente a condição; casos de fronteira nos `criteria`
      ([limites-jev-1-13](../../conhecimento/modelo/limites-jev-1-13.md) #1).
- [ ] Alto = sim; `true` descreve o sim; instrução e critério não se contradizem.
- [ ] Choice tem lista completa + `other`/`none`; opções que se confundem têm `what`/`not_for`/`examples`
      com os mesmos nomes de campo; condições que coexistem viram perguntas separadas.
- [ ] Score descreve **situações** em cada nível (não "moderado"); normalizar por `len(criteria)-1` antes de pesar.
- [ ] Noul não está sendo usado como escala de grau (grau → Score).
- [ ] Ausência tem desfecho: `none` na Choice ou Noul de existência/adequação; ranking sozinho não prova
      que algum candidato serve.
- [ ] Nada que o código calcula (conta, soma, diferença de datas, comparação numérica).
- [ ] Se o state pode não tratar do alvo (sigla ambígua, entidade errada): Noul de relevância antes de
      consumir o julgamento — pode ir na mesma requisição.
- [ ] Nada pergunta ao Jev o que o state não diz (ex.: "de quem é este dado?" sem o dono no texto).
- [ ] O desenho tem **baseline** (regra de código, sistema atual ou contagem simples) e um **critério
      mensurável para continuar ou descartar**, fixado antes de medir ([jev-avaliar](../jev-avaliar/SKILL.md)).

## Problema → receita (em `conhecimento/receitas/`)
| Preciso… | Nota |
|---|---|
| classificar com "não sei" útil | [classificacao-com-confianca](../../conhecimento/receitas/classificacao-com-confianca.md) · taxonomia funda: [classificacao-hierarquica](../../conhecimento/receitas/classificacao-hierarquica.md) |
| rotear pedido para código/LLM/humano | [roteamento-por-intencao](../../conhecimento/construir/padroes/roteamento-por-intencao.md) · com argumentos: [function-calling](../../conhecimento/receitas/function-calling.md) · exemplo medido: [roteador](../../exemplos/roteador-jev-llm/README.md) |
| escolher skill/ferramenta (ou nenhuma) | [sugestao-de-skill](../../conhecimento/receitas/sugestao-de-skill.md) |
| filtrar entrada/saída de LLM | [guardrails-llm](../../conhecimento/receitas/guardrails-llm.md) · exemplo: [guardrail](../../exemplos/guardrail-chatbot/README.md) |
| escolher contexto para RAG · ordenar candidatos | [classificar-passagens-rag](../../conhecimento/receitas/classificar-passagens-rag.md) · [reranking](../../conhecimento/receitas/reranking.md) |
| achar trecho num documento | [busca-linha-a-linha](../../conhecimento/receitas/busca-linha-a-linha.md) |
| extrair valor sem inventar · datas | [extracao-de-valor-pre-parseado](../../conhecimento/receitas/extracao-de-valor-pre-parseado.md) · [extracao-de-datas](../../conhecimento/receitas/extracao-de-datas.md) · exemplo: [extração](../../exemplos/extracao-sem-inventar/README.md) |
| verificar extração/resposta de LLM · citações | [cascata-sde](../../conhecimento/receitas/cascata-sde.md) · [checagem-de-citacoes](../../conhecimento/receitas/checagem-de-citacoes.md) |
| casar registros duplicados | [alinhamento-de-entidades](../../conhecimento/receitas/alinhamento-de-entidades.md) |
| triagem de atendimento multi-pergunta | exemplo: [triagem](../../exemplos/triagem-atendimento/README.md) |
| pontuar em várias dimensões · virar feature de ML | [pontuacao-composta](../../conhecimento/construir/padroes/pontuacao-composta.md) · [autoresearch-de-features](../../conhecimento/receitas/autoresearch-de-features.md) |
| provar estabilidade | [autoconsistencia-nouls](../../conhecimento/receitas/autoconsistencia-nouls.md) · [autoconsistencia-choices](../../conhecimento/receitas/autoconsistencia-choices.md) |
| muitas perguntas num documento grande | [perguntas-em-paralelo](../../conhecimento/receitas/perguntas-em-paralelo.md) |

## Não faça
Fragmentar sem motivo perguntas agrupáveis · pedir ao Jev texto, conta, contagem ou comparação de datas ·
state com o documento inteiro quando a pergunta usa um trecho · limiar espalhado pelo código · confiar em
confiança alta como prova de acerto · tratar guardrail com Jev como fronteira de segurança ou resposta do
Jev como autorização · chave de API no front · trocar o modelo do agente de programação pelo Jev (o agente
escreve código que **chama** o Jev).

## Depois de usar
Aprendeu algo que o repositório não tem (medição, pegadinha, limiar que funcionou)? Registre com a skill
[jev-manter](../jev-manter/SKILL.md).
