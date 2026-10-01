---
name: api-http
description: API HTTP — POST https://api.typesafe.ai/v1/systemone com Bearer; corpo {state, model, questions}; resposta {model, answers, usage}; erros documentados 401/422/429/529 e, medido por nós, 400 para campo extra, tipo inválido, modelo inexistente e tetos (255 opções / 10 níveis); GET /v1/models.
tipo: sdk
fonte: https://docs.typesafe.ai/api · /introduction/quickstart · /models#listing-models · https://api.typesafe.ai/openapi.json (spec 0.2.0) · chamadas reais em 2026-09-30
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 110–445, 12621–12729 e 13051–13098
estudado_em: 2026-09-30
---

# API HTTP

Fundida em 2026-09-30 com o contrato do Codex (`skills/jev-api/references/http-contract.md`, hoje em
`.local/antigos/`). Regras de operação (validação da resposta, retentativa, efeitos, chave, logs) estão em
[integracao-segura](integracao-segura.md).

## Endpoint
```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
Content-Type: application/json
```
Chave em https://console.typesafe.ai/keys; convenção de ambiente `TYPESAFE_API_KEY`.

## Corpo
| Campo | Tipo | |
|---|---|---|
| `state` | string \| object \| array | o conteúdo avaliado ([state](../modelo/state.md)) |
| `model` | string | `"jev-latest"` (ou versionado `"jev-1.13.0"`) |
| `questions` | map<string, Question> | a chave é sua; NÃO vai ao modelo; a resposta volta sob ela. É um mapa de IDs para perguntas, **não** uma lista de mensagens de chat |

Question: `type` é obrigatório; `criteria` também em Choice/Score. No OpenAPI
v0.2.0 salvo em 2026-09-30, `instructions` é opcional e aceita string, objeto,
array ou `null`, embora a página `/api` o marque obrigatório (omitida/`null` → 200, [testado]).
Preferimos enviar instruções explícitas; critérios também fornecem contexto, mas o ID não vai ao modelo.
- `{"type": "noul", "instructions": ..., "criteria"?: {"true": ..., "false": ...}}`
- `{"type": "choice", "instructions": ..., "criteria": {"opção": "descrição" | objeto | array | null}}` — máx. 255 opções
- `{"type": "score", "instructions": ..., "criteria": ["nível 0", "nível 1", ...]}` — 2 a 10 níveis, do baixo ao alto

## Resposta
```json
{
  "model": "jev-1.13.0",
  "answers": {
    "is_urgent":   {"type": "noul", "noul": 0.95},
    "department":  {"type": "choice", "choice": "billing",
                    "probabilities": {"billing": 0.88, "technical": 0.12, "sales": 0.0}, "confidence": 0.81},
    "frustration": {"type": "score", "score": 1.05, "legend": {"0": "Calm", "1": "Frustrated", "2": "Very angry"},
                    "probabilities": {"0": 0.0, "1": 0.95, "2": 0.05}, "confidence": 0.92}
  },
  "usage": {"input_tokens": 304, "output_tokens": 18}
}
```
- `model` = versão que respondeu; pode diferir do alias enviado (texto do OpenAPI) → logar.
- `answers` usa os mesmos IDs da requisição (OpenAPI: `minProperties: 1`). Ligue cada resposta ao
  registro de origem pelo ID; falta de um ID esperado é erro ([integracao-segura](integracao-segura.md)).
- Choice/Score: `probabilities` somam 1 (validar com tolerância numérica); `confidence` derivada delas;
  `choice` = opção de maior probabilidade. `confidence` e `noul` ∈ [0,1]. Score: chaves de nível são
  **strings** no JSON, índices a partir de 0.
- `usage`: consumo, não valor monetário. `input_tokens` = tokens faturáveis; `output_tokens` "currently
  free of charge" (OpenAPI; sujeito a mudança) — preço em [modelos-precos-limites](../modelo/modelos-precos-limites.md).
- No OpenAPI, ambas as contagens de `usage` são inteiros obrigatórios; o tipo
  `int | None` do SDK Python é mais tolerante que o contrato HTTP.
- `legend` pode devolver objetos/arrays, além de strings: preserva os níveis
  estruturados, como o exemplo de `/primitives/score` (linhas 935–1015).

## Prosa, schema e servidor
| Ponto | Prosa do doc | OpenAPI 0.2.0 / tipos | Servidor [testado 2026-09-30] |
|---|---|---|---|
| níveis de Score | 2–10 | `minItems=1`, sem `maxItems`; JS exige 2 | 11 → **400** "Too many score levels. Must have at most 10"; 1 → 200, confiança 1,0 |
| nível `null` no Score | — | não aceito no schema; aceito no tipo JS | **422** |
| opções de Choice | até 255 | sem `maxProperties` | 256 → **400** "Too many choices…"; 255 → 200; 1 → 200 |
| `instructions` | obrigatório | opcional/nulo | omitida ou `null` → 200 |
| `questions` vazio · sem `model` | — | `questions.minProperties=1` | **422** |
| `state: null` | — | tipo JS aceita `null` | **422** (Python já recusa `None`) |
| campo extra no corpo (`temperature`) · `type` inválido | — | — | **400** "Invalid request." |
| modelo inexistente | — | — | **400** `{"detail":{"error_type":"api_usage_error","message":"Unknown model: …"}}` |
Tabela completa e amostra: [medicoes](../evidencias/medicoes-2026-09-30.md#contrato-da-api-fronteiras).
Consequência: um cliente que repasse campos desconhecidos (JS encaminha extras; Python `extra_body`)
quebra a chamada; o tipo do SDK aceitar algo não prova que o endpoint aceite.

## Erros
| Status | Significado | Ação |
|---|---|---|
| 400 | [testado] campo desconhecido, `type` inválido, modelo inexistente, teto de opções/níveis; corpo `{"detail":{"error_type","message"}}` fora da tabela do doc e do OpenAPI | corrigir o pedido; não retentar |
| 401 | chave ausente/inválida | conferir `Authorization`; não insistir com a mesma credencial |
| 422 | corpo inválido (campo faltando, pergunta malformada) — o corpo diz o campo | corrigir; não retentar |
| 429 | limite de taxa (tokens/s ou req/s) | backoff exponencial limitado; respeitar `retry-after` |
| 529 | TypeSafe sobrecarregada | backoff exponencial limitado |
Os SDKs já retentam 408/429/5xx com backoff por padrão ([sdk-javascript](sdk-javascript.md),
[sdk-python](sdk-python.md)); 400/401/422 não são retentados.

O OpenAPI documenta 422 como `{"detail":[{"loc":[...],"msg":"...","type":"..."}]}`,
com `input` e `ctx` possíveis. `loc` identifica campo/índice; não logar `input`
indiscriminadamente (ecoa dados). O spec só declara respostas 200/422; os demais status vêm da
prosa (ou da nossa medição) e não têm corpo padronizado ali. Erro de validação respondeu em ~220 ms [testado].

Fonte adicional: https://api.typesafe.ai/openapi.json (spec 0.2.0), captura do Claude
preservada em `.local/docs/openapi-claude-2026-09-30.json`; proveniência em `fontes/catalogo/catalogo.json`.

## cURL mínimo
```bash
curl -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" -H "Content-Type: application/json" \
  -d '{"state": "Help! My payouts have been failing for 3 days.", "model": "jev-latest",
       "questions": {"is_urgent": {"type": "noul", "instructions": "Does this convey urgency?"}}}'
```

## Modelos
`GET https://api.typesafe.ai/v1/models` (Bearer) → `{"models": [{"name", "description", "release_date"}]}`.
Lista nomes aceitos pela conta; IDs versionados podem ser aceitos mesmo quando só aliases aparecem
([modelos-precos-limites](../modelo/modelos-precos-limites.md)).

## Intermediários
Gateways (OpenRouter, Vercel, Pydantic) têm contrato, IDs de modelo e autenticação próprios; não
presumir que o envelope seja idêntico ao da API direta ([integracao-segura](integracao-segura.md)).

## Relacionados
[sdk-python](sdk-python.md) · [sdk-javascript](sdk-javascript.md) · [primitivas](../modelo/primitivas.md) ·
[integracao-segura](integracao-segura.md)
