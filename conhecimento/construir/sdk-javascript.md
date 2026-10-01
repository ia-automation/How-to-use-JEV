---
name: sdk-javascript
description: SDK JavaScript/TypeScript @typesafe-ai/sdk v0.6.0 — cliente TypeSafeClient, choice()/noul()/score() com tipos inferidos, retentativa padrão (2 retries, 500 ms dobrando até 5 s), hierarquia de erros por status.
tipo: sdk
fonte: https://docs.typesafe.ai/sdk/javascript (e /sdk/javascript/api/*, /sdk/javascript/changelog)
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 14704–17913
estudado_em: 2026-09-30
---

# SDK JavaScript / TypeScript (JavaScript SDK)

## Instalação e versão
- `npm install @typesafe-ai/sdk` — exige **Node.js 20 ou mais novo**. Pacote traz ESM, CommonJS e declarações TypeScript.
- Versão atual no snapshot: **0.6.0** (`VERSION: "0.6.0"`). Fonte no GitHub `typesafe-ai/typesafe-sdk-js` (tag v0.6.0: `src/client.ts`, `src/types.ts` têm opções e padrões).
- Chave: `TYPESAFE_API_KEY` no ambiente (ou `apiKey`). Sem chave = erro no construtor.
- Endpoint por baixo: `POST /v1/systemone` (descrito em `SystemOneRequestPayload`).

## Cliente: `new TypeSafeClient(config?)`
Precedência: opção explícita > variável de ambiente > padrão do SDK. Variável vazia ou só espaços é ignorada.
Lança erro se: chave ausente, config inválida, ou runtime não suportado.

| Opção (`TypeSafeClientConfig`) | Padrão / fallback |
|---|---|
| `apiKey` | `TYPESAFE_API_KEY` (obrigatória) |
| `baseURL` | `TYPESAFE_BASE_URL`, depois `https://api.typesafe.ai` (propriedade `baseURL` sai sem barras finais) |
| `defaultModel` | `TYPESAFE_DEFAULT_MODEL`, depois `jev-latest` |
| `timeout` (ms, **por tentativa**) | `10000`; não há orçamento total de retentativas |
| `retry` (`Partial<RetryPolicy>`) | campos omitidos usam os padrões abaixo |
| `defaultHeaders` | `Record<string,string>`; cabeçalhos por chamada prevalecem |
| `fetch` | `fetch` global; tipo `Fetch = (input: string, init?: RequestInit) => Promise<Response>` (para proxy/transporte ou testes) |
| `logger` | `console` com prefixo; interface `Logger` = `debug/info/warn/error(message, ...args)` |
| `logLevel` | `TYPESAFE_LOG_LEVEL`, depois `warn` |
| `dangerouslyAllowBrowser` | `false` — liberar uso no navegador expõe a chave a quem abre a página |

- `LogLevel = "debug" | "info" | "warn" | "error" | "off"` (`LOG_LEVELS` lista do mais ao menos verboso). `info` loga resumo por requisição; `debug` acrescenta cabeçalhos e corpos. Cabeçalhos de credencial conhecidos são redigidos; **corpos não**.
- `ENV` (constante): `apiKey: "TYPESAFE_API_KEY"`, `baseURL: "TYPESAFE_BASE_URL"`, `defaultModel: "TYPESAFE_DEFAULT_MODEL"`, `logLevel: "TYPESAFE_LOG_LEVEL"`. Tipo `EnvVar` = valores de `ENV`.
- Propriedades somente leitura do cliente: `baseURL, defaultHeaders, defaultModel, fetch, logger, logLevel, models, retry, timeout`.

## Chamada: `client.systemOne(request, options?)`
`systemOne<Q extends Questions>(request: SystemOneRequest<Q>, options?: RequestOptions): APIPromise<SystemOneResult<Q>>`

- `request.state: EntryType` — texto, objeto JSON, array JSON ou `null`; a API responde **422** para `state: null` [testado 2026-09-30, [medicoes](../evidencias/medicoes-2026-09-30.md#contrato-da-api-fronteiras)].
- `request.questions: Q` — **não vazio**; dicionário nome → pergunta (nome é a chave da resposta).
- `request.model?: string` — sobrescreve `defaultModel`.
- Propriedades extras no request são **encaminhadas**, inclusive `null` (forward-compat).
- Lança: perguntas vazias ou critérios de `score` com menos de 2 entradas (validação local); erro HTTP não-2xx após retries; falha de conexão/timeout após retries; aborto do chamador.
- `RequestOptions` (por chamada): `headers` (mescla sobre `defaultHeaders`), `retry` (`Partial<RetryPolicy>`, campos omitidos herdam), `signal` (`AbortSignal`, cancela a requisição **e** retentativas pendentes), `timeout` (ms por tentativa).

### Declarar perguntas (funções auxiliares ou objetos literais)
`EntryType = string | {[k]: JsonValue} | JsonValue[] | null` vale para state, instructions e cada descrição de critério.

- `choice<T extends ChoiceCriteria>(instructions, criteria: T): ChoiceQuestion<T>` — `criteria` = `{ rótulo: descrição | null }` (`ChoiceCriteria` = `[label: string]: EntryType`). `null` = rótulo sem descrição.
- `noul(instructions?: EntryType = null, criteria?: {true?: EntryType; false?: EntryType} | null): NoulQuestion` — pergunta sim/não; `criteria.true` descreve o sim, `criteria.false` o não. Ambos opcionais.
- `score<T extends ScoreCriteria>(instructions, criteria: T): ScoreQuestion<T>` — `criteria` = lista ordenada, **pelo menos 2 entradas**, índice = nota a partir de **0**; entradas podem ser `null`. Tipo `ScoreCriteria = readonly [EntryType, EntryType, ...EntryType[]]`.
- Divergência: esse `null` é aceito pelo **tipo JS**, mas não por
  `ScoreQuestion.criteria.items` no OpenAPI v0.2.0 salvo em 2026-09-30.
  Descrever todos os níveis com valores não nulos: o endpoint devolveu **422** para nível `null` [testado 2026-09-30, [medicoes](../evidencias/medicoes-2026-09-30.md#contrato-da-api-fronteiras)].
- Objeto literal equivalente: `{ type: "choice"|"noul"|"score", instructions?, criteria }` (`instructions` opcional ou `null`). `Question = NoulQuestion | ScoreQuestion | ChoiceQuestion`.

### Resposta: `SystemOneResult<Q>`
- `answers` — um por nome de pergunta, tipado por `ResultFor<Q[K]>`.
- `model: string` — modelo que respondeu.
- `usage: { input_tokens: number; output_tokens: number }`.

Respostas (todas `readonly`, com discriminador `type`):
- `NoulResponse`: `{ type: "noul", noul: number }` — `noul` = probabilidade de "sim", de 0 a 1.
- `ChoiceResponse<T>`: `{ type: "choice", choice: keyof T & string, confidence: number, probabilities: {[label]: number} }`.
- `ScoreResponse<T>`: `{ type: "score", score: number, confidence: number, legend: ScoreLegend<T>, probabilities: {[score]: number} }` — `score` é esperado (**pode cair entre níveis inteiros**); `legend` = descrições do rubric por nota.

### Tipagem genérica (o ponto forte)
- `ResultFor<T>`: Noul→`NoulResponse`; `ScoreQuestion<S>`→`ScoreResponse<S>`; `ChoiceQuestion<E>`→`ChoiceResponse<E>`; senão `never`. Preserva as chaves dos critérios: `answers.category.choice` é tipado como a união dos rótulos declarados.
- Passar o objeto de critérios direto no `choice()` (o genérico `T` captura as chaves) — inferência do doc; o doc não discute `as const`.
- `ScoreOf<T>`: tupla de tamanho fixo → índices como chaves literais; senão `number`. `ScoreLegend<T> = { readonly [score in ScoreOf<T>]: T[score] }`.
- `Questions` = `{[name: string]: Question}`.

### `APIPromise<T>` (retorno)
Estende `Promise<T>`. Métodos extras:
- `asResponse()` → `Promise<Response>` bruto, sem parse; o SDK já bufferizou o corpo sob o timeout; **não** também dar `await` no resultado parseado da mesma promise (o corpo é do chamador).
- `withResponse()` → `{ data, response, requestId }` (`response` com corpo já consumido).
- `map(fn)` → `APIPromise<U>` compartilhando resposta e um único parse.
- Não-2xx rejeita com `APIError`, inclusive via `asResponse()`.

## Listagem de modelos
`client.models.list(options?: RequestOptions): APIPromise<ModelCard[]>`; `ModelCard = { name, description, release_date }` (strings).

## Erros (hierarquia)
```
TypeSafeError (extends Error)                     base do SDK
├─ APIConnectionError   DNS, TLS, conexão fechada, corpo interrompido; mensagem padrão "Connection error."
│   └─ APITimeoutError  resposta completa não chegou no timeout; campo timeoutMs
├─ APIUserAbortError    chamador cancelou via AbortSignal; mensagem padrão "Request was aborted."
└─ APIError             resposta HTTP não bem-sucedida
    ├─ BadRequestError 400        ├─ AuthenticationError 401
    ├─ PermissionDeniedError 403  ├─ NotFoundError 404
    ├─ UnprocessableEntityError 422  ├─ RateLimitError 429 (retryAfterMs)
    └─ InternalServerError 5xx
```
- `APIError` tem: `status`, `body` (JSON parseado, texto, ou `undefined` se vazio), `headers` (`Headers`), `requestId` (cabeçalho `x-typesafe-request-id` ou `undefined`). `APIError.fromResponse(status, body, headers)` devolve a subclasse certa. Construtor: `(status, body, headers, message?)`.
- `RateLimitError.retryAfterMs: number | undefined` — atraso pedido pelo servidor em ms; `undefined` se ausente ou inválido.
- Status sem classe própria (ex.: 408) não tem subclasse declarada no doc (não declarado no doc).

## Retentativa (`RetryPolicy`; sobrescrita parcial no cliente ou por chamada)
| Campo | Padrão |
|---|---|
| `maxRetries` (após a tentativa inicial; `0` desliga) | 2 |
| `httpStatuses` (`ReadonlySet<number>`) | 408, 429 e 500–599 |
| `backoffInitialMs` (dobra a cada tentativa até o máximo) | 500 |
| `backoffMaxMs` | 5000 |
| `backoffJitter` (fração do atraso subtraída ao acaso, 0–1) | 0.25 |
| `respectRetryAfter` (honra `Retry-After` e `retry-after-ms`) | true |
| `maxRetryAfterMs` (atraso do servidor maior que isso → usa backoff) | 60000 |
| `apiConnectionError` (retenta falhas de conexão, inclusive corpo interrompido) | true |
| `apiTimeoutError` | true |
- Timeout é por tentativa e **não há orçamento total**: pior caso = (maxRetries+1) × timeout + esperas (conta minha a partir dos padrões, não afirmação do doc).

## Pegadinhas
- Timeout padrão de 10 s por tentativa; com 2 retries o pior caso passa de 30 s.
- Logs `debug` imprimem o corpo (state e perguntas) sem redação.
- `dangerouslyAllowBrowser` expõe a chave; padrão bloqueia o navegador.
- `asResponse()` + `await` na mesma promise = corpo disputado.
- Validação local: perguntas vazias, `score` com < 2 critérios e formato errado em `choice()`/`score()` (medido em
  2026-09-30 no exemplo busca-imoveis). A RESPOSTA não é validada contra o tipo, e campos extras do request são
  repassados ao corpo — a API recusa campo desconhecido com 400 [testado].
- Score em v0.6.0: critérios são **lista**, não dicionário com chaves inteiras (quebra de v0.5.x).

## Exemplo mínimo completo (assíncrono; o SDK JS é só Promise, sem versão síncrona)
```ts
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient(); // lê TYPESAFE_API_KEY
const response = await client.systemOne({
  state: { document: "I was charged twice. Please fix this ASAP." },
  questions: {
    category: choice("What is this ticket about?", {
      billing: null, technical: null, other: null,
    }),
    billing: noul("Is this about billing?"),
    urgency: score("How urgent is this ticket?", ["can wait", "this week", "today"]),
  },
});
console.log(response.answers.category.choice);   // "billing" | "technical" | "other"
console.log(response.answers.billing.noul);      // 0..1
console.log(response.answers.urgency.score, response.usage.input_tokens, response.model);
```
(O quickstart do doc usa só `choice`; `noul`/`score` acima seguem as assinaturas da referência.)

## Changelog
- **v0.6.0 (2026-09-15)** — QUEBRA: `Score.criteria` passa a ser sequência ordenada em vez de dicionário com chaves inteiras.
- **v0.5.7 (2026-09-11)** — release público inicial.
