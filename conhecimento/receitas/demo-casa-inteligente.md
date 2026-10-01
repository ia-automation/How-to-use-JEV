---
name: demo-casa-inteligente
description: Demo de assistente de casa inteligente — todas as perguntas (inclusive as irrelevantes) numa única chamada em paralelo ("fan-out especulativo"), com LLM só para dividir pedido composto e para conversa livre.
tipo: receita
fonte: https://docs.typesafe.ai/demos/smart-home.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 12331–12404
estudado_em: 2026-09-30
---

# Demo de assistente de casa inteligente (Smart home assistant demo)

## Problema
Avaliar pedidos de usuário de casa inteligente, de tipos muito variados, com uma só lista de perguntas, de forma rápida e barata, usando um LLM só onde se precisa gerar texto. A página "Demos" apenas lista esta demo: "Evaluate user smart home requests with speculative questions and LLM fallback".

## Como o Jev entra
- **state:** o pedido do usuário (formato exato: não declarado no doc).
- **perguntas** (o doc dá só as paráfrases abaixo, para o pedido "Turn off all of the lights in the house"):
  - "What category of request is this?" -> smarthome command
  - "What domain is this request targeting?" -> whole house
  - "What type of device is this request targeting?" -> lights
  - "What action should be taken on the lights?" -> turn off (escrita já assumindo que o usuário comanda luzes)
  - Uma pergunta **Noul**: o pedido pede mais de uma ação distinta?
  - Tipos (Choice/Noul) das demais, opções e limiares: não declarado no doc.
- **chamadas:** uma chamada inicial com TODAS as perguntas em paralelo, inclusive as que acabam irrelevantes; o código filtra depois.

## O que o código faz com a resposta
- Filtra por código as respostas de perguntas irrelevantes ao tipo de pedido.
- Noul "mais de uma ação distinta" verdadeiro -> LLM divide o pedido numa lista de comandos atômicos; cada um é avaliado pelo Jev individualmente.
- Jev classifica o pedido como informação geral/conversa -> LLM gera resposta livre (fallback conversacional).
- Demais pedidos: comportamento determinístico a partir das respostas.

## Resultados medidos
Nenhum número no doc. Só afirmações qualitativas: a resposta inicial do Jev é tão rápida frente à do LLM que adiciona latência "negligible"; a abordagem sequencial é "much slower and more expensive" que uma chamada única.

## Técnicas reutilizáveis
- Fan-out especulativo: perguntar tudo de uma vez, inclusive o que pode ser irrelevante, e descartar por código -> quando chamadas sequenciais custam mais que perguntas a mais.
- Escrever a pergunta condicional já assumindo a premissa ("que ação nas luzes?") sem esperar confirmar que é sobre luzes.
- Evitar o anti-padrão sequencial (categoria -> domínio/dispositivo -> ação): minimiza nº de perguntas, mas é mais lento e caro.
- Noul como detector de "pedido composto": só então gastar um LLM para dividir; Jev reavalia cada parte.
- Jev como roteador rápido na frente do LLM: fluxo determinístico fica no Jev; conversa aberta cai no LLM.

## Limites e pegadinhas
- Receita só conceitual: sem código, sem texto literal das perguntas, sem números. O código-fonte "will be available on GitHub at release" (app Vite/React de página única).
- Padrão relacionado citado: /patterns/fan-out (Speculative Fan-Out).

## Esqueleto de código
(não declarado no doc — a página não traz código)
