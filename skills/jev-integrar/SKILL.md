---
name: jev-integrar
description: Implementar ou revisar uma integração com a API do Jev (TypeSafe) por HTTP, SDK Python (typesafe-sdk) ou SDK JS (@typesafe-ai/sdk) — montar state/questions, conferir answers, tipos, limites, erros, retentativas, chave e logs. Use quando houver código concreto chamando o Jev; não confundir a API direta com envelopes de gateways (OpenRouter, Vercel, Pydantic).
---

# Integrar a API do Jev

Procedimento. Fatos em `conhecimento/construir/` (raiz = dois níveis acima). Contrato:
[api-http](../../conhecimento/construir/api-http.md) · SDKs: [sdk-python](../../conhecimento/construir/sdk-python.md),
[sdk-javascript](../../conhecimento/construir/sdk-javascript.md) · regras de operação:
[integracao-segura](../../conhecimento/construir/integracao-segura.md) · versão, preço e limites:
[modelos-precos-limites](../../conhecimento/modelo/modelos-precos-limites.md). Desenho das perguntas antes:
[jev-desenhar](../jev-desenhar/SKILL.md).

## Procedimento
1. **Identifique o provedor.** API direta → endpoint e envelope de [api-http](../../conhecimento/construir/api-http.md).
   Gateway → contrato dele; não misture campos de chat, IDs de modelo e autenticação entre provedores.
2. **Localize produtor e consumidor.** Preserve a ligação entre ID da pergunta e registro de origem. A
   resposta é `answers[id]`, não texto em `choices[0]`.
3. **Monte state e perguntas** explícitas (o ID não vai ao modelo), perguntas do mesmo state juntas, dentro
   dos limites (255 opções, 2–10 níveis, 64k/32k). Não acrescente `messages`, `reasoning`, `temperature`,
   `response_format` nem campo inventado: a API responde 400.
4. **Valide a resposta antes de qualquer efeito**: todos os IDs esperados, `type` correspondente, opção
   entre as enviadas, números finitos em [0,1], distribuições somando 1, Score na faixa. Ausência,
   timeout, tipo inesperado ou cancelamento viram estado explícito (`erro`/`pendente`), nunca `noul=0`.
5. **Trate erros por classe**: 400/401/422 corrigem-se (sem retentar); 429/529/408/5xx e conexão entram
   na retentativa. Os SDKs já fazem 2 retries com backoff — defina **um** orçamento (tentativas, tempo
   total, concorrência) em vez de empilhar retentativa da aplicação sobre a do SDK.
6. **Mantenha efeitos fora da chamada** de classificação e sob a autorização que o processo exige:
   retentativa não duplica efeito e confiança alta não autoriza nada.
7. **Registre** `model` efetivo, versão/hash das perguntas e limiares, `usage`, latência, tentativas,
   status e origem `live`/`replay`. Chave só no servidor, por nome de variável (`TYPESAFE_API_KEY`);
   sem log `debug` com dado real (os SDKs imprimem corpos); não logar `input` de 422.
8. **Verifique e diga como verificou**: conferência estática, teste com mock ou inferência real. Resposta
   sintética não é evidência de desempenho.

## Exemplos locais
- [support-triage.request.json](assets/support-triage.request.json): requisição sintética com as três primitivas.
- [support-triage.response.mock.json](assets/support-triage.response.mock.json): resposta fictícia para
  testar o consumidor — **não obtida da API**.
- Código real medido: [exemplos/](../../exemplos/README.md) (Python com cache em `exemplos/_comum/`; TypeScript em
  `exemplos/busca-imoveis/`).

## Pontos fáceis de errar
`Noul` devolve número, não `bool` nem `null`; `confidence` só em Choice/Score. `Score` é fracionário e sua
escala vem do número de níveis. No JSON HTTP as chaves de nível em `legend`/`probabilities` são strings
(no SDK Python, inteiros). O tipo do SDK aceitar algo (JS: `state: null`, nível `null`) não prova que o
endpoint aceite — o servidor devolveu 422. "O SDK não lançou erro" não prova que todos os IDs voltaram.
