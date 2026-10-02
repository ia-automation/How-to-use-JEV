# Dados do `lint-semantico-de-diff` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item F) e [DADOS.md](../../DADOS.md).
Diffs sintéticos de um CRM imobiliário fictício (TypeScript/Express/Drizzle, alguns Python); rotas, módulos e
nomes inventados; todo segredo é `FAKE` (`sk_test_FAKE…`, `ghp_FAKE…`, `AKIAFAKE…`, JWT com assinatura `FAKE…`).

## Conjunto fixo de regras (8) — texto literal, igual em todos os casos
Cada caso traz de 3 a 6 destas regras, numeradas `r1…rn` na ordem em que aparecem no caso (a numeração NÃO é
estável entre casos: `r1` pode ser qualquer regra; o texto identifica a regra). Pelo menos uma mecânica por caso.

| chave (só neste LEIA-ME) | tipo | texto literal |
|---|---|---|
| SEG | mecanica | Nenhuma linha adicionada contém valor de segredo em literal: chave com prefixo `sk_live_`, `sk_test_`, `ghp_` ou `AKIA`, JWT (`eyJ…`), ou `password`/`senha`/`secret`/`api_key`/`token` recebendo string literal de 6 ou mais caracteres — vale também em comentário, teste, documentação e arquivo de exemplo. |
| LOG | mecanica | Nenhum `console.log(` em linha adicionada, mesmo comentado, exceto em arquivo de teste (caminho com `.test.`, `.spec.`, ou pasta `test/`, `tests/`, `__tests__/`). |
| DROP | mecanica | Nenhuma linha adicionada contém `DROP TABLE` ou `DROP COLUMN` sem o marcador `confirmado por` na mesma linha ou na linha adicionada imediatamente anterior. |
| TODO | mecanica | Todo `TODO` ou `FIXME` (maiúsculas) em linha adicionada vem seguido de referência de ticket entre parênteses, no formato `TODO(CRM-123)` / `FIXME(CRM-123)`. |
| JSDOC | semantica | Toda função nova exportada em TypeScript (`export function`, `export async function` ou `export const nome = (...) =>`) tem JSDoc imediatamente acima com a tag `@description`. Função que já existia e foi só modificada não entra. |
| DESVIO | semantica | Supressão de lint ou de tipo em linha adicionada (`eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `# noqa`, `# type: ignore`) leva, na mesma linha ou na linha imediatamente anterior, comentário dizendo o porquê do desvio. |
| VALID | semantica | Rota nova de Express (`router.<verbo>(` ou `app.<verbo>(`) que lê `req.body`, `req.params` ou `req.query` valida essa entrada com express-validator (cadeia `body()`/`param()`/`query()` E checagem de `validationResult`); zod, joi, yup ou checagem manual no backend não substituem. Rota que já existia não entra. |
| SQL | semantica | Query SQL crua em código adicionado (`db.execute(sql`…`)`, `pool.query`/`client.query` com string SQL, `cursor.execute`/`cur.execute`) leva comentário imediatamente acima justificando por que o query builder não serve. Fragmento `sql`…`` dentro de `.where()`/`.orderBy()` do builder e arquivo de migration não contam. |

## Regras mecânicas: o gabarito É a regex (conferido por código na validação)
Aplicadas só às **linhas adicionadas** (`+`, excluindo `+++`); o arquivo vem do `+++ b/<caminho>`. Mecânica
nunca recebe `null`: a regex sempre responde. Onde a regex diverge do que um humano relevaria, o gabarito segue
a regex e a `nota` registra (é o ponto do exemplo: regra mecânica é literal, e o custo disso fica visível).

- SEG — `(?i)` sobre a linha: `sk_(?:live|test)_[A-Za-z0-9]{8,}` | `ghp_[A-Za-z0-9]{10,}` | `AKIA[A-Z0-9]{12,}` |
  `eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}` | `(?:password|senha|secret|api_key|apikey|token)\b\s*[:=]+\s*["'`][^"'`]{6,}["'`]`.
  Consequências assumidas: `TOKEN_HEADER = 'x-crm-token'`, `token_header = "…"`, `secretAccessKey: process.env…`,
  `senhaMinima = 8`, `"senha": "…"` (chave JSON entre aspas) e `.set('x-portal-secret', '…')` **não** casam;
  `senha = "…"`, `password: '…'`, `POSTGRES_PASSWORD: "…"` casam. Limite registrado em `LS-T064`.
- LOG — `console\.log\s*\(` na linha E o caminho **não** casa `(\.test\.|\.spec\.|(^|/)tests?/|(^|/)__tests__/)`.
  `console.error`, `logger.log` não casam; `// console.log(` comentado casa; `scripts/` e `src/util/teste-util.ts` não
  são teste.
- DROP — `(?i)\bDROP\s+(?:TABLE|COLUMN)\b` na linha sem `(?i)confirmado por` na mesma linha nem na linha `+`
  imediatamente anterior (linha em branco adicionada entre as duas quebra a sequência). `DROP INDEX` não casa;
  `DROP COLUMN` dentro de comentário SQL casa.
- TODO — para cada ocorrência de `\b(TODO|FIXME)\b` (sensível a maiúsculas), viola se nela não começa
  `\b(TODO|FIXME)\(([A-Z]{2,}-\d+)\)`. `TODO: CRM-418` viola; `todo:` minúsculo não entra.

## `null` × `false` nas regras semânticas
`null` = o diff **não toca o assunto** da regra; `false` = toca e não viola; `true` = viola. Decisões:
- JSDOC: função **modificada** (assinatura aparece como linha de contexto, sem `+`) → `null`; diff sem função
  nova exportada (interface, tipo, `export const` de objeto/array, helper interno, `export default router`) →
  `null`; Python → `null` (a regra fala de JSDoc em TypeScript). **Função renomeada** aparece no diff como
  `+export function …` nova → conta como nova (`LS-T057`; o diff não distingue). `export default` de uma const
  arrow definida no diff conta como função nova exportada (`LS-T041`). Helper interno sem JSDoc não pesa; JSDoc
  no helper e não na exportada → `true`. JSDoc com `@param`/`@returns` mas sem `@description` → `true`.
- DESVIO: nenhuma supressão em linha `+` (inclusive quando ela só aparece em linha `-`) → `null`. Comentário
  que não diz o porquê (`ok`, `temporário`, `legado`, `fix later`) → `true`. Porquê a 2+ linhas de distância com
  código no meio → `true` (regra literal). Porquê na mesma linha após `--` ou na linha imediatamente anterior →
  `false`.
- VALID: sem rota nova de Express (migration, config, front, FastAPI) → `null`; rota nova que não lê
  body/params/query (health, logout por header) → `null`; rota **existente** que passa a ler campo novo →
  `null` (o revisor pediria, a regra não cobre). Cadeia sem `validationResult` → `true`; cadeia que valida só o
  header enquanto `req.body` vai sem validação → `true`; `checkSchema` → `false`; cadeia + middleware `validar`
  do projeto (padrão visível nas rotas vizinhas) → `false`; cadeia e `validationResult` num array local de
  middlewares → `false`; zod/joi/manual → `true`; zod presente no arquivo mas a rota validada com
  express-validator → `false`.
- SQL: sem SQL cru em código (builder, migration, fragmento em `.where()`) → `null`. Comentário descritivo
  ("busca por telefone", "dinâmico") → `true`; justificativa concreta (o que o builder não faz) imediatamente
  acima, em uma linha, em bloco `/* */` ou em bloco contíguo de `//` → `false`. Teste/apoio de teste não é
  exceção desta regra.

## Famílias de caso difícil (todas em `ajuste.json` E `teste.json`; `nota` começa com "difícil:")
Contagem ajuste / teste (um caso pode estar em mais de uma família):
1. Desvio COM porquê (não viola) × sem porquê / porquê vazio / porquê longe / supressão só removida — 4 / 8.
2. JSDoc presente sem `@description` — 1 / 1. JSDoc na função errada, helper interno, `export default` — 2 / 4.
3. Função modificada, não nova (`null`) × renomeada (nova) — 1 / 3.
4. Segredo em comentário, documentação, `.env.example`, fixture de teste (TS e Python) — 3 / 4.
5. Nomes com `token`/`secret`/`senha`/`password` sem literal (não viola) — 2 / 3.
6. zod/joi no backend (viola) × zod no front (`null`) — 1 / 3.
7. SQL cru com comentário que justifica (não viola) × que só descreve × sem comentário × fragmento em `.where()` × em teste — 4 / 6.
8. `console.log` em teste (`tests/`, `__tests__/`, `test/*.spec.js`) × comentado × em `scripts/` × `console.error` × em comentário — 3 / 6.
9. `TODO` fora do formato, `FIXME` sem ticket, `todo` minúsculo — 2 / 3.
10. `DROP` com marcador na mesma linha / anterior × duas linhas acima × `DROP INDEX` × em migration TS × em comentário × em código com guarda — 3 / 5.
11. Rota nova sem entrada, rota existente, FastAPI (`null`) — 3 / 2.
12. Cadeia sem `validationResult`, validação manual, só header — 2 / 3.
13. Diff de configuração (semânticas `null`, mecânica `false`) — 0 / 1.

## Contagens (validação de 2026-10-01, zero erros: JSON, UTF-8 sem BOM, LF, campos, enums, IDs, mínimos, 10–60
linhas por diff, ≥ 1 mecânica por caso, mecânicas conferidas contra a regex, ≥ 30% difíceis)
| arquivo | casos | difíceis | vereditos true / false / null |
|---|---|---|---|
| `rascunho.json` | 5 | 0 (por desenho: só encanamento) | 3 / 11 / 2 |
| `ajuste.json` | 36 | 32 (88%) | 21 / 74 / 22 |
| `teste.json` | 66 | 54 (81%) | 39 / 131 / 36 |

Ambiguidades decididas pelo rotulador (não estavam no briefing): mecânica nunca é `null`; função renomeada e
`export default` de arrow contam como nova; rota existente que lê campo novo é `null`; cadeia sem
`validationResult` viola; middleware `validar` do projeto após a cadeia conta como checagem; `checkSchema` conta
como express-validator; migration e fragmento `sql` em `.where()` não são SQL cru; a regra de SQL não excetua
teste; `scripts/` não é teste; `.env.example` sem valor não viola; a regex de SEG não pega chave JSON entre aspas
nem valor passado como argumento (limite deliberado, registrado em `LS-T064`).
