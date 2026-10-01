---
name: roteamento-por-intencao
description: Padrão — Jev na frente como classificador rápido e barato; cada intenção vai ao manipulador certo (código determinístico, LLM especialista ou humano); LLM caro só para quem precisa.
tipo: padrao
fonte: https://docs.typesafe.ai/patterns/intent-routing
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 13322–13394; exemplo em fontes/docs/paginas/patterns/intent-routing.md
estudado_em: 2026-09-30
---

# Roteamento por intenção (Intent routing)

**Ideia:** nem todo pedido precisa do mesmo manipulador. Classificar primeiro (barato) e só então
gastar com o recurso caro. Benefício: custo e velocidade.

## Exemplo do doc (atendimento)
```json
"intent": {"type": "choice", "instructions": "The primary intent of this customer message",
  "criteria": {"order_status": "Asking about an existing order",
               "product_question": "Asking about a product before buying",
               "return_exchange": "Wants to return or exchange something",
               "complaint": "Unhappy with experience, wants resolution"}},
"complexity": {"type": "score", "instructions": "How complex is this request to resolve",
  "criteria": ["Simple lookup or standard procedure",
               "Requires some judgment or multi-step process",
               "Unusual situation, edge case, or escalation needed"]}
```
```python
if intent.confidence < 0.5:                  return route_to_human_agent(id)
if intent.choice == "order_status":          handle_order_status(id)                  # código, sem LLM
elif intent.choice == "product_question":    handle_with_llm(id, PRODUCT_SPECIALIST)
elif intent.choice == "return_exchange":     handle_with_llm(id, RETURNS_SPECIALIST)
elif intent.choice == "complaint":
    if complexity.score > 1 or complexity.confidence < 0.5: route_to_human_agent(id)
    else:                                    handle_with_llm(id, COMPLAINT_RESOLUTION)
```

## Regras
- Uma intenção pode ir para **código puro** — o maior ganho.
- LLMs especialistas carregam contextos diferentes; o Jev decide qual acordar.
- Confiança baixa na **complexidade** também escala: "sempre pensar no que confiança baixa significa
  naquele ponto do sistema e no que está em jogo".
- Variações mais ricas: [function-calling](../../receitas/function-calling.md) (rota + argumentos tipados), [sugestao-de-skill](../../receitas/sugestao-de-skill.md)
  (qual skill carregar para o agente, ou nenhuma), roteamento de modelo em [casos-de-uso](../../modelo/casos-de-uso.md).

## Visto nos vídeos
Triagem de suporte no Playground (vídeo 2): Choice de departamento + Noul "pediu reembolso?" + Score
de frustração de 4 níveis; ~104 ms de inferência + ~314 ms de rede.

## Relacionados
[roteamento-por-confianca](roteamento-por-confianca.md) · [fan-out-especulativo](fan-out-especulativo.md) · [confianca](../../modelo/confianca.md)
