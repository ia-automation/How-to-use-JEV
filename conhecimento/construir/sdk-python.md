---
name: sdk-python
description: SDK Python typesafe-sdk v0.7.2 — clientes TypeSafeClient (síncrono) e AsyncTypeSafeClient, perguntas Noul/Choice/Score (objeto ou dict), response_model Pydantic, RetryPolicy com orçamento total, exceções por status.
tipo: sdk
fonte: https://docs.typesafe.ai/sdk/python (e /sdk/python/api/*, /usage, /changelog)
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 17914–21111
estudado_em: 2026-09-30
---

# SDK Python (TypeSafe Python SDK)

## Instalação e versão
- `uv add typesafe-sdk` ou `pip install typesafe-sdk`. Extra HTTP/2: `typesafe-sdk[http2]` (desde v0.7.2). Python ≥ 3.10 (quickstart).
- Versão mais nova no changelog: **0.7.2 (2026-09-26)**. Código em `github.com/typesafe-ai/typesafe-sdk-python`. Cliente HTTP por baixo: `httpx2`; validação/serialização: **Pydantic** (desde 0.7.0).
- Chave: `TYPESAFE_API_KEY` (criada em console.typesafe.ai) ou `api_key=`.

## Clientes
`TypeSafeClient` (síncrono) e `AsyncTypeSafeClient` (assíncrono); mesma API, o assíncrono usa `await`. Ambos são gerenciadores de contexto (`with` / `async with`). Fechar: `close()` (síncrono) / `await aclose()` (assíncrono) — fecha também o `http_client` fornecido.

Precedência: opção explícita > variável de ambiente > padrão. Variável vazia/só espaços é ignorada. **Chave explicitamente vazia não cai para o ambiente.**

| Parâmetro | Padrão / fallback |
|---|---|
| `api_key: str \| None` | `TYPESAFE_API_KEY`. Espaços nas pontas (inclusive quebra de linha de arquivo de chave) são removidos; vazia, com espaço interno, caractere de controle ou não-ASCII = rejeitada (`TypeSafeError` já na criação, antes de qualquer requisição) |
| `model` | `TYPESAFE_DEFAULT_MODEL`, depois `jev-latest` |
| `base_url` | `TYPESAFE_BASE_URL`, depois `https://api.typesafe.ai` |
| `timeout: float \| httpx2.Timeout` | `DEFAULT_TIMEOUT = 10.0` s **por operação HTTP**; herda `http_client.timeout` se fornecido |
| `retry: RetryPolicy` | ver abaixo; `RetryPolicy(max_retries=0)` desliga |
| `headers: Mapping[str,str]` | cabeçalhos extras |
| `transport` | transporte `httpx2` custom (fechado junto com o cliente) |
| `http_client` | `httpx2.Client`/`httpx2.AsyncClient`; **mutuamente exclusivo com `transport`** (`ValueError` se ambos) |

- Constantes (`typesafe_sdk.constants`): `API_KEY_ENV='TYPESAFE_API_KEY'`, `BASE_URL_ENV='TYPESAFE_BASE_URL'`, `DEFAULT_MODEL_ENV='TYPESAFE_DEFAULT_MODEL'`, `LOG_LEVEL_ENV='TYPESAFE_LOG_LEVEL'`, `DEFAULT_BASE_URL='https://api.typesafe.ai'`, `DEFAULT_MODEL='jev-latest'`, `DEFAULT_TIMEOUT=10.0`.
- Log: logger `typesafe_sdk` (padrão `logging`), ou `TYPESAFE_LOG_LEVEL` = `debug|info|warning|error|off`, **aplicada uma vez no import** (padrão: não definida). `info` = uma linha por requisição; `debug` = também cabeçalhos e corpos. Cabeçalhos secretos (authorization, chaves de API, cookies, qualquer nome com `token` ou `secret`) são redigidos; **corpos não**.
- HTTP/2: `AsyncTypeSafeClient(http_client=httpx2.AsyncClient(http2=True))` (síncrono: `httpx2.Client(http2=True)`); útil com muitas requisições concorrentes (multiplexação).
- Base URL alternativa: a API de destino precisa seguir o OpenAPI da TypeSafe (`api.typesafe.ai/docs`). Exemplos do doc (gateways):
  - OpenRouter: `base_url="https://openrouter.ai/api"`, `model="~typesafe/jev-latest"`, chave `OPENROUTER_API_KEY`.
  - Vercel AI Gateway: `base_url="https://ai-gateway.vercel.sh/typesafe"`, `model="typesafe-ai/jev"`, chave `AI_GATEWAY_API_KEY`.
  - Pydantic AI Gateway: `base_url="https://gateway-us.pydantic.dev/proxy/typesafe"`, `model="jev-latest"`, chave `PYDANTIC_AI_GATEWAY_API_KEY`.

## Chamada: `client.system_one(state, questions, *, model=None, retry=None, timeout=None, extra_headers=None, extra_body=None, response_model=None)`
(`state` e `questions` podem ir posicionais, como no guia de uso.)
- `state: JSONContent` — texto, objeto JSON ou array. **Não pode ser `None`**, mas valores dentro de um objeto podem.
- `questions: Mapping[str, Question]` — **não vazio**; nome → objeto de pergunta **ou dict** (pode misturar os dois na mesma chamada).
- `model` — sobrescreve o do cliente; `retry`, `timeout` (s ou `httpx2.Timeout`), `extra_headers` — só desta chamada.
- `extra_body` — campos de topo extras, **mesclados por cima** do corpo depois de `state`/`model`/`questions`: último vence, chave colidente substitui, objetos **não** são mesclados em profundidade.
- `response_model` — tipo Pydantic `BaseModel` para a resposta (ver abaixo).
- Levanta: `TypeSafeError` (perguntas vazias ou lista de critérios do Score vazia), `TypeSafeAPIError` (HTTP não-sucesso após retries), `TypeSafeAPIConnectionError` (sem conexão/timeout após retries), `TypeSafeAPIResponseValidationError` (corpo não bate com o modelo).

### Declarar perguntas
Objetos Pydantic (argumentos nomeados) — todos aceitam `instructions` (texto, objeto ou array; opcional, padrão `None`):
- `Noul(instructions=..., criteria=NoulCriteria | None)` — `NoulCriteria` é TypedDict com chaves `true`/`false` (descrição do sim/não, `None` = sem descrição).
- `Choice(instructions=..., criteria={"rótulo": descrição | None, ...})` — `criteria` **obrigatório**; `Mapping[str, JSONContent | None]`.
- `Score(instructions=..., criteria=[desc0, desc1, ...])` — `criteria` **obrigatório**: lista ordenada não vazia, um item por nota a partir de **0** (`Sequence[JSONContent]`).
- Os três têm `additionalProperties: false` no JSON Schema (campo desconhecido no objeto é rejeitado pelo modelo; só dict aceita campo extra, ver Compatibilidade futura).

Dicts equivalentes (TypedDicts `NoulModel`/`ChoiceModel`/`ScoreModel`) com a chave `type`:
```python
{"type": "noul", "instructions": "..."}
{"type": "choice", "instructions": "...", "criteria": {"calm": None, "angry": None}}
# score: {"type": "score", "instructions": "...", "criteria": ["low", "medium", "high"]}
```
Tipos comuns: `JSONValue` (JSON aninhado, pode conter `None`), `JSONContent` (string ou mapping/sequência de `JSONValue`).

### Resposta: `SystemOneResponse` (Pydantic, `frozen=True`, `strict=True`, `extra="ignore"`)
- `model: str` — modelo que respondeu.
- `usage: Usage` — `input_tokens: int | None`, `output_tokens: int | None` (None se a API não reportou; difere do JS, onde são `number`).
- `answers: dict[str, Answer]` — todas as respostas por nome; `Answer` é união discriminada por `type`.
- Atalhos (cacheados): `nouls`, `choices`, `scores` — dicts por nome, por tipo. Uso: `r.nouls["billing"].noul`, `r.choices["tone"].choice`, `r.scores["urgency"].score`.
- `request_id` (cabeçalho `x-typesafe-request-id`), `raw_http_response` (`httpx2.Response` com status, cabeçalhos, corpo).
- `NoulAnswer`: `type="noul"`, `noul: float` — probabilidade de sim/verdadeiro, 0–1 (perto de 1 = sim, perto de 0 = não, ~0.5 = incerteza). Exemplo no schema: 0.98.
- `ChoiceAnswer`: `type="choice"`, `choice: str` (rótulo de maior probabilidade), `confidence: float` 0–1, `probabilities: dict[str, float]` (soma ≈ 1). Exemplo do schema: `{"angry":0.8,"calm":0.1,"excited":0.1}`, choice `angry`, confidence 0.9.
- `ScoreAnswer`: `type="score"`, `score: float` (**média ponderada pelas probabilidades dos níveis**; pode cair entre inteiros; exemplo 1.7), `confidence: float` 0–1, `legend` (descrição por nota inteira), `probabilities` (por nota inteira).
- Texto do schema: usar valores baixos de `confidence` para sinalizar seleções/notas incertas para revisão.

### Resposta tipada com `response_model`
```python
class BillingResponse(SystemOneResponse):   # herda: ganha request_id, nouls, etc.
    billing: NoulAnswer                     # campo ao lado de model/usage/answers
```
(`result.billing == result.nouls["billing"]`.) Ou um `BaseModel` totalmente novo, sem herdar: `class R(BaseModel): answers: BillingAnswers`, onde `BillingAnswers(BaseModel): billing: NoulAnswer`; acesso `result.answers.billing.noul`. Descompasso entre corpo e modelo → `TypeSafeAPIResponseValidationError`.

## Listagem de modelos
`client.models.list(retry=None, timeout=None, extra_headers=None)` (`await` no assíncrono) → `ListModelsResponse` com `models: tuple[ModelMetadata, ...]`, `request_id`, `raw_http_response`. `ModelMetadata`: `name` (nome ou alias aceito no campo `model`), `description`, `release_date` (`YYYY-MM-DD`). Em `extra_headers`, autenticação, identificação do SDK e `Accept` ficam protegidos. Exemplo do guia: `client = TypeSafeClient(model="jev")`.

## Exceções (hierarquia)
```
TypeSafeError (Exception)
├─ TypeSafeAPIError        status, body (JSON/texto/None), headers, endpoint (método+URL sem credenciais/query), request_id
│   ├─ TypeSafeBadRequestError 400        ├─ TypeSafeAuthenticationError 401
│   ├─ TypeSafePermissionDeniedError 403  ├─ TypeSafeNotFoundError 404
│   ├─ TypeSafeUnprocessableEntityError 422
│   ├─ TypeSafeRateLimitError 429         retry_after_ms (ms pedidos pelo servidor, ou None)
│   ├─ TypeSafeInternalServerError 5xx
│   └─ TypeSafeAPIResponseValidationError  resposta 2xx com corpo ausente/estruturalmente inválido; field_path ex.: "answers.tone.confidence"
└─ TypeSafeAPIConnectionError (+ ConnectionError builtin)  falha sem resposta HTTP
    └─ TypeSafeAPITimeoutError (+ TimeoutError builtin)    campo timeout
```
- v0.6.0: exceções e respostas são picklable; mensagens de erro incluem detalhes HTTP. v0.7.1: valida a chave cedo e **não inclui o valor da chave** nas exceções logadas.
- Não há equivalente ao `APIUserAbortError` do JS (cancelamento por `AbortSignal`) no doc Python.

## Retentativa (`RetryPolicy`, dataclass; no cliente ou por chamada)
Campos: `max_retries` (após a inicial; `0` desliga), `backoff_initial` (s; dobra a cada tentativa até `backoff_max`; zero desliga backoff), `backoff_max` (s; zero desliga backoff), `backoff_jitter` (fração subtraída ao acaso, 0–1), `http_statuses` (códigos retentados), `respect_retry_after` (honra `Retry-After` e `retry-after-ms`), `api_connection_error` (retentar `TypeSafeAPIConnectionError`), `api_timeout_error` (retentar `TypeSafeAPITimeoutError`), `exceptions` (tipos extras que disparam retry), `predicate` (função da exceção; `True` = retenta, somando às outras regras), **`timeout`** (orçamento TOTAL em s por chamada do SDK, incluindo tentativa inicial e esperas; `None` = sem limite; para antes de um retry cujo atraso alcançaria/excederia o orçamento e relança o último erro).
- **Valores padrão publicados na assinatura de `sdk/python/api/retries.md`:**
  `max_retries=2`, `backoff_initial=0.5` s, `backoff_max=5.0` s,
  `backoff_jitter=0.25`, `http_statuses={408,429,500–599}`,
  `respect_retry_after=True`, `api_connection_error=True`, `api_timeout_error=True`,
  `exceptions=set()`, `predicate=None`, **`timeout=30.0` s de orçamento total**.
  A assinatura está no componente `SdkSignature`, ausente do texto consolidado.
  `None` desliga esse orçamento. O exemplo com 3 retries/10 s é uma sobrescrita.
  A referência diz que uma espera que alcançaria o orçamento impede nova tentativa;
  não verificamos interrupção de operação em andamento exatamente aos 30 s (pendência em
  [pendencias](../evidencias/pendencias.md)). Efeito prático: 3 tentativas lentas de 10 s esbarram no
  orçamento de 30 s; quem precisa de mais tempo sobe `RetryPolicy.timeout`.
- Exemplo de uso do guia: `RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0)`.
- v0.6.0 corrigiu o tratamento de valores inválidos em `RetryPolicy`.

## Compatibilidade futura
- Campo novo da API: `extra_body={"beam_width": 4}` (`beam_width` é ilustrativo; só enviar campos que a API suporta). Campo de topo desconhecido (ex.: `temperature`) faz a API responder **400** [testado 2026-09-30, [medicoes](../evidencias/medicoes-2026-09-30.md#contrato-da-api-fronteiras)].
- Dict de pergunta com campo desconhecido (ex.: `"weight": 2`) é aceito; erros de tipagem nele devem ser ignorados — preferir atualizar o SDK.
- Tipo de resposta desconhecido: o SDK **loga aviso e ignora** a resposta; ver tudo via `result.raw_http_response.json()["answers"]`. Campos extras em respostas conhecidas são ignorados.

## Pegadinhas
- Timeout é por operação HTTP (pode ser `httpx2.Timeout`); o orçamento total está em `RetryPolicy.timeout`, não no `timeout` do cliente.
- `http_client` e `transport` juntos = `ValueError`.
- `TYPESAFE_LOG_LEVEL` só vale se definida antes do import.
- Corpos aparecem em log `debug`.
- Respostas são estritas (`strict=True`): tipo errado vira `TypeSafeAPIResponseValidationError`, não coerção.
- `state=None` é inválido.

## Exemplos mínimos completos
Assíncrono:
```python
import asyncio
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score

async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        response = await client.system_one(
            state={"document": "I was charged twice. Please fix this ASAP."},
            questions={
                "billing": Noul(instructions="Is this ticket about billing?"),
                "tone": Choice(instructions="What is the customer's tone?",
                               criteria={"calm": None, "frustrated": None, "angry": None}),
                "urgency": Score(instructions="How urgent is this ticket?",
                                 criteria=["can wait", "this week", "today"]),
            },
        )
    print(response.nouls["billing"].noul, response.choices["tone"].choice,
          response.scores["urgency"].score)

asyncio.run(main())
```
Síncrono (mesmas perguntas):
```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(state=..., questions={...})
print(response.nouls["billing"].noul)
```
Erros: `except TypeSafeAPIError as error: print(error.status, error.request_id)`.

Esqueleto com perguntas e limiares num lugar só (da antiga skill `jev`; `send_to_human`/`open_refund_flow`
são funções da aplicação):
```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

QUESTIONS = {  # perguntas e limiares vivem aqui, num lugar só
    "topic": Choice(instructions="Which team should handle `ticket.message`?",
                    criteria={"billing": "Charges, invoices, refunds", "orders": "Delivery, returns",
                              "other": "Anything else"}),
    "refund_requested": Noul(instructions="Does `ticket.message` explicitly request a refund or credit?"),
    "frustration": Score(instructions="How frustrated is the customer in `ticket.message`?",
                         criteria=["Calm, matter-of-fact", "Frustrated but civil", "Very angry or threatening to leave"]),
}
FLOOR, YES = 0.6, 0.7

with TypeSafeClient(model="jev-1.13.0") as client:          # versão fixada depois de afinar
    r = client.system_one(state={"ticket": {"message": msg}}, questions=QUESTIONS)
a = r.answers                                               # r.model = versão que respondeu → logar
if a["topic"].confidence < FLOOR: send_to_human()
elif a["topic"].choice == "billing" and a["refund_requested"].noul >= YES: open_refund_flow()
```
Antes de consumir `a[...]`, validar IDs e tipos ([integracao-segura](integracao-segura.md)).

## Changelog
- **v0.7.2 (2026-09-26)** — extra `http2` no pacote; doc de HTTP/2.
- **v0.7.1 (2026-09-21)** — valida a chave cedo e a exclui das exceções logadas; exemplos com gateways de IA.
- **v0.7.0 (2026-09-18)** — QUEBRA: ser/de trocado de `msgspec` para `pydantic`. Correção: subclasses de `str` serializam como string (antes virava lista de caracteres). Novo: argumento `response_model` em `system_one`.
- **v0.6.0 (2026-09-15)** — QUEBRA: `Score.criteria` vira sequência ordenada (antes dicionário com chaves inteiras). Tipos de entrada aceitam abstratos (`Mapping`, `Sequence`); erros com detalhes HTTP; `RetryPolicy` com valores inválidos tratada; exceções/respostas picklable.
- **v0.5.7 (2026-09-14)** — release público inicial.

## Divergências JS × Python
| Tema | JavaScript | Python |
|---|---|---|
| Versão no snapshot | 0.6.0 | 0.7.2 |
| Método | `systemOne` (Promise) | `system_one` (sync e async) |
| Acesso às respostas | `answers.nome.choice` (tipado por pergunta) | `nouls/choices/scores["nome"]` ou `response_model` |
| Timeout padrão | 10000 ms por tentativa, sem orçamento total | 10.0 s por operação HTTP + `RetryPolicy.timeout=30.0` s por chamada |
| Padrões de retry | declarados (2; 500→5000 ms; jitter 0.25; 408/429/5xx) | mesmos números em segundos; sem `maxRetryAfterMs` declarado |
| Retry extensível | não | `exceptions` e `predicate` |
| Mínimo de critérios do Score | 2 | lista não vazia (mínimo 2 não declarado) |
| `usage` | números | `int \| None` |
| Cancelamento | `signal` (`APIUserAbortError`) | não declarado |
| Nível de log padrão | `warn` (`TYPESAFE_LOG_LEVEL`) | não definido; níveis `debug/info/warning/error/off` |
| Erro de validação de resposta | não há classe | `TypeSafeAPIResponseValidationError` |
| Uso no navegador | `dangerouslyAllowBrowser` | n/a |
| Escape hatch | propriedades extras no request | `extra_body`, dicts com campos desconhecidos |
| Nomes de classe de erro | `BadRequestError`... | `TypeSafeBadRequestError`... |
