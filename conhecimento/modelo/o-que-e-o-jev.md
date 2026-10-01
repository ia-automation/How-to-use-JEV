---
name: o-que-e-o-jev
description: Jev = 1º modelo "System One" da TypeSafe; recebe state + perguntas tipadas e devolve decisões com probabilidade calibrada, não texto. Treino RLCD. Não é LLM de chat nem de código.
tipo: conceito
fonte: https://docs.typesafe.ai/introduction · /concepts/system-one · /introduction/machine-learning-primer · /introduction/coding-agents
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 942–995 e 12405–12592
estudado_em: 2026-09-30
---

# O que é o Jev

## Em uma frase
Modelo que **decide em vez de escrever**: você manda um `state` (o conteúdo) e um mapa de perguntas
tipadas; ele devolve, para cada pergunta, uma resposta tipada com a distribuição de probabilidade
— numa requisição só, com todas as perguntas avaliadas **em paralelo e isoladas** entre si.

## System One
- Classe de modelo criada pela TypeSafe; o Jev é o primeiro e o carro-chefe. Nome vem de Kahneman
  (*Rápido e Devagar*): Sistema 1 = julgamento rápido e intuitivo; Sistema 2 = deliberado.
- Pergunta boa para ele = "o julgamento que uma pessoa bem informada faz em poucos segundos, com o
  contexto certo". Se precisa de raciocínio longo ou pesa fatores independentes → decompor (ver
  [como-construir](../construir/como-construir.md)).
- Não escreve resposta, não gera código, não explica o próprio raciocínio. O espaço de resposta é
  sempre o que você definiu: nunca devolve valor fora das opções.

## Por que existe (a tese da TypeSafe)
- LLM é feito para produzir texto para humano ler; usar LLM para decidir algo que o código consome é
  "coagir um gerador de texto a devolver decisão e depois parsear".
- **Machine Native Intelligence**: IA com propriedades de software — estrutura, confiabilidade,
  observabilidade, testabilidade, velocidade, consistência, custo baixo.
- "Building prod, not God": não quer fazer tudo; quer a decisão estreita que o código inspeciona.
  Aposta: automação em escala será ~99% máquina↔máquina e 1% humano.
- Meta declarada: razão inteligência/(velocidade·custo) > 100× a de um LLM; aposta de que inteligência
  mais barata cria muito mais demanda.

## Treino: RLCD
| Técnica | O que otimiza | Resultado |
|---|---|---|
| RLHF | preferência humana | chatbots; bajulação, alucinação confiante, *mode dropping* |
| RLVR | recompensa verificável | modelos de raciocínio; bons em matemática, lentos e caros |
| **RLCD** | decisões com probabilidade **calibrada** | Jev: sem texto; probabilidade alta ↔ chance alta de acerto |

- Calibração vale para **grupos** de previsões (das respostas com 0,8, ~80% acertam), não garante
  uma resposta individual.
- Cofundador Diogo Almeida é coinventor do RLHF (InstructGPT/ChatGPT) — citado pelo doc.
- O método de treino não foi aberto (vídeo 1: há projeto parecido aberto no Reddit, BERT
  bidirecional de 421 M parâmetros — afirmação do vídeo, não do doc).

## O que o Jev NÃO é
- Não substitui o LLM do Claude Code/Cursor/Codex: não há `model: "jev-latest"` que transforme o
  agente de código em Jev. O uso certo é o agente de código **escrever código que chama o Jev**.
- Não gera texto. Dá para forçar encadeando Choices, mas é lento e ruim ([limites-jev-1-13](limites-jev-1-13.md) #9).
- Não aceita imagem, áudio, vídeo (ainda): só texto — string, objeto JSON ou array.

## Propriedades que o doc promete
Estruturado (tipado por construção) · paralelo (uma pergunta não vira contexto de outra) ·
comparável (ordenável, vira `if`) · rápido (maioria ~100 ms; "tempo real ~150 ms") · confiança
calibrada · autoconsistente (respostas estáveis em repetição — ver [autoconsistencia-nouls](../receitas/autoconsistencia-nouls.md) e
[autoconsistencia-choices](../receitas/autoconsistencia-choices.md)).

## Relacionados
[primitivas](primitivas.md) · [state](state.md) · [confianca](confianca.md) · [como-construir](../construir/como-construir.md) · [modelos-precos-limites](modelos-precos-limites.md) ·
[limites-jev-1-13](limites-jev-1-13.md) · [casos-de-uso](casos-de-uso.md)
