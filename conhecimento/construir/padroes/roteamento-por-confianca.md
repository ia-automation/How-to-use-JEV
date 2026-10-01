---
name: roteamento-por-confianca
description: Padrão — a resposta diz O QUÊ, a confiança diz SE age; piso global (0,6) e limiar por ação conforme o risco (transferência > 0,85 age, 0,6–0,85 confirma).
tipo: padrao
fonte: https://docs.typesafe.ai/patterns/confidence-routing
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 13182–13241
estudado_em: 2026-09-30
---

# Roteamento por confiança (Confidence-gated routing)

**Ideia:** confiança é um segundo eixo de decisão. Benefício: confiabilidade e segurança.

## Exemplo do doc (comandos de banco por voz)
Pergunta única:
```json
"intent": {"type": "choice", "instructions": "What action is the user requesting?",
           "criteria": {"check_balance": "Check the balance of an account",
                        "approve_transfer": "Approve the pending transfer request",
                        "other": "Something else"}}
```
```python
action = response.answers["intent"]
if action.confidence < 0.6:                 route_to_support_agent(acct)   # piso para qualquer ação
elif action.choice == "check_balance":      show_balance(acct)             # risco baixo: 0,6 basta
elif action.choice == "approve_transfer":
    if action.confidence > 0.85:            approve_transfer(acct)         # risco alto, confiança alta
    else:                                   ask_user_to_confirm("Just to confirm: ...")
else:                                       route_to_support_agent(acct)   # "other"
```

## Regras
- O piso pega "o modelo está genuinamente em dúvida". Acima dele, **cada ação tem seu limiar** pelo
  custo de agir errado (ouvir o saldo errado é barato; aprovar transferência errada não).
- Sempre ter um destino para `other`.
- Valores são exemplos: começar conservador, medir, ajustar ([confianca](../../modelo/confianca.md)).
- Variante com Noul: faixa de dois lados (`NO < v < YES` → humano).

## Relacionados
[confianca](../../modelo/confianca.md) · [roteamento-por-intencao](roteamento-por-intencao.md) · [classificacao-com-confianca](../../receitas/classificacao-com-confianca.md)
