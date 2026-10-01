---
name: fan-out-especulativo
description: Padrão — mandar numa chamada todas as perguntas que o código PODE precisar (inclusive as que só valem para alguns ramos) e deixar o código ignorar as irrelevantes; poupa idas e vindas a custo de poucos tokens.
tipo: padrao
fonte: https://docs.typesafe.ai/patterns/fan-out
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 13244–13319; exemplo em fontes/docs/paginas/patterns/fan-out.md
estudado_em: 2026-09-30
---

# Fan-out especulativo (Speculative fan-out)

**Ideia:** em vez de "classifica → depois pergunta a gravidade", pergunta tudo junto. Perguntas são
avaliadas em paralelo; somar perguntas quase não muda a latência. Benefício: custo e velocidade.

## Exemplo do doc (triagem de suporte)
State: `"Hi, I placed an order (#98423) last Thursday and was charged twice. I also can't log in
after the site update, and adding Apple Pay would be really helpful. This is getting frustrating."`

| ID | Tipo | Pergunta | Só importa se |
|---|---|---|---|
| `category` | Choice | "Determine the broad category of this support ticket" — `bug_report` / `billing` / `feature_request` / `account` | sempre |
| `bug_severity` | Score | "How severe is the reported issue" — Cosmetic / Broken, workaround / Blocking | bug |
| `has_reproducible_steps` | Noul | "The user describes specific steps to reproduce the issue" | bug |
| `refund_requested` | Noul | "The user is explicitly asking for a refund or credit" | billing |
| `frustration` | Score | "How frustrated the user appears" — Calm / Frustrated but civil / Very angry | sempre |

```python
if category.choice == "bug_report":
    if bug_severity.score > 1.5 and bug_repro.noul > 0.6: escalate_to_engineering(id, severity="high")
    else: add_to_bug_backlog(id)
elif category.choice == "billing":
    route_to_billing_with_flag(id, refund_likely=True) if refund.noul > 0.7 else route_to_billing(id)
elif category.choice == "feature_request":
    log_feature_request(id)
if frustration.score > 1.5:            # vale em qualquer categoria
    flag_for_priority_response(id)
```

## Regras
- Perguntas especulativas **declaram a premissa** no texto ("If the customer wants to return
  something, why?", "If this is a shipping problem, which kind is it?").
- Incerteza em ramo não usado **se ignora** (o `shipping_issue` dividido 0,74/0,26 não importa se o
  departamento não é shipping).
- Custo real: tokens das perguntas extras. O state domina os tokens e vai uma vez → pergunta extra é
  quase grátis quando o documento é grande ([perguntas-em-paralelo](../../receitas/perguntas-em-paralelo.md): 13 perguntas juntas 12,2×
  mais barato e 10× mais rápido que 13 chamadas).
- Limite: 64k de contexto para state + todas as perguntas ([modelos-precos-limites](../../modelo/modelos-precos-limites.md)). Medir o
  orçamento real de tokens, custo e latência ponta a ponta.
- "Pouco impacto na latência" é orientação do fornecedor, não licença para ignorar contexto, custo e
  limites: perguntas descartadas também consumiram tokens. Medido por nós: ~20 tokens por Noul curto e
  283 → 322 ms de 1 para 100 perguntas ([medicoes](../../evidencias/medicoes-2026-09-30.md#escala-latência-custo)).
- Demo extrema: [demo-casa-inteligente](../../receitas/demo-casa-inteligente.md) (categoria, cômodo, aparelho, ação — tudo de uma vez);
  [function-calling](../../receitas/function-calling.md) manda 54 perguntas por comando.

## Relacionados
[primitivas](../../modelo/primitivas.md) · [roteamento-por-intencao](roteamento-por-intencao.md) · [como-construir](../como-construir.md)
