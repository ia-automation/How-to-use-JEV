---
name: state
description: State = o conteúdo avaliado (string, objeto ou array de texto); um state por requisição, todas as perguntas veem o mesmo; mandar só o que as perguntas precisam, com campos nomeados.
tipo: conceito
fonte: https://docs.typesafe.ai/concepts/state · /concepts/how-to-build-with-system-one
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 880–940 e 536–552
estudado_em: 2026-09-30
---

# State

## O que é
O material que o modelo avalia — mensagem, passagem, registro, estado da aplicação. Vai no campo
`state`. **Uma requisição = um state + N perguntas**; todas veem o mesmo state e são avaliadas
independentemente (tipos misturados à vontade).

"Pense no state como o material que você apresentaria a um painel de especialistas antes de pedir
o julgamento."

## Formatos
| Formato | Serve para | Exemplo |
|---|---|---|
| string | um texto só | `"My card was charged twice."` |
| objeto | campos nomeados, registros relacionados, estado da app | `{"message": "...", "order_id": "A-104"}` |
| array | sequência de mensagens/registros | `["Hi", "My customer number is TS1337.", "..."]` |

- **Preferir objeto** na maioria dos casos: cada parte ganha nome e a relação fica clara.
- Um objeto com conversa + pedido + política é UM state — juntar o que a decisão precisa comparar.
- Só texto. Pré-processar imagem/áudio/vídeo/binário em texto ou campos antes.

## Regras de ouro
1. **Separar conteúdo de pergunta.** State = conteúdo e fatos de apoio (ex.: pedido de reembolso +
   política). Perguntas = os julgamentos ("pediu reembolso?", "a política cobre?").
2. **Mandar só o relevante.** Estado grande cheio de detalhe irrelevante derruba acurácia (distrator
   e *context rot*) e dificulta achar a causa do erro. Filtrar/recuperar em código antes; se não der,
   usar um Noul de relevância para filtrar ([classificar-passagens-rag](../receitas/classificar-passagens-rag.md)).
3. **Não depender do conhecimento dos pesos** quando a informação atual pode vir da sua base: ponha no
   state (é assim que se "customiza" o Jev — não há fine-tuning por cliente; ver [modelos-precos-limites](modelos-precos-limites.md)).
4. **Apontar com caminho entre crases.** Pergunta que fala de uma parte do state usa caminho com
   ponto e índice, **com as crases dentro do texto**: `` `support.tickets[0].message` ``,
   `` `commerce.orders[0].charges` ``. Tira ambiguidade.

## Exemplo (do doc)
```json
{
  "ticket": {"subject": "Duplicate charge",
             "messages": [{"from": "customer", "text": "I was charged twice for order A-104. Please refund the duplicate."},
                          {"from": "support",  "text": "We are checking the charges."}]},
  "order": {"id": "A-104", "charges": [{"amount_usd": 49, "status": "captured"}, {"amount_usd": 49, "status": "captured"}]},
  "refund_policy": "Duplicate charges are eligible for a refund."
}
```
Perguntas: `"Does `ticket.messages[0].text` request a refund?"` e
`"Does `refund_policy` support the refund requested in `ticket.messages[0].text`, given `order.charges`?"`.

## Limites
- Contexto do jev-1.13: 64k tokens por requisição (state + todas as perguntas); 32k para state + a
  maior pergunta. O state é ingerido **uma vez** e reaproveitado por todas as perguntas.
- Idioma: inglês é o principal; outros (inclusive CJK) aceitos com acurácia menor — **testar em
  português antes de confiar** (medição nossa: [medicoes-2026-09-30](../evidencias/medicoes-2026-09-30.md#idioma)).

## Relacionados
[primitivas](primitivas.md) · [estrutura-nas-perguntas](estrutura-nas-perguntas.md) · [limites-jev-1-13](limites-jev-1-13.md)
