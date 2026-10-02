# Dados do `selecao-de-skill` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item L) e [DADOS.md](../../DADOS.md).
Catálogo e pedidos são fictícios: um parque de desenvolvimento + marketing de uma imobiliária, com nomes de skill
realistas. Gabarito = a skill que um engenheiro sênior do parque mandaria carregar lendo só o pedido e o catálogo.

Arquivos: `skills.json` (42 skills), `rascunho.json` (5 fáceis), `ajuste.json`, `teste.json` (abrir uma vez, no
fim). Envelope `{"versao", "autor": "fable", "casos"}` em todos — em `skills.json`, `casos` é a lista de skills
(mesma convenção do `faq.json` do roteador). A ordem dos pedidos foi embaralhada.

## Esquema (o do briefing, sem campo extra)
- `skills.json`: `{"id", "nome", "descricao"}` — `id` em hífen-minúsculo (é o que os casos referenciam), `nome` em
  português, `descricao` de 1–2 linhas dizendo o que a skill faz e quando usar.
- Caso: `{"id", "pedido", "skill", "aceitaveis": [ids], "nota"}`.
  - `skill`: a melhor, ou `null` se nenhuma serve.
  - `aceitaveis`: todas as que o engenheiro aceitaria ver carregadas; contém `skill`; `[]` se e só se `skill` é `null`.
  - `nota`: começa com `"difícil: <família>"` nos casos difíceis.

## Como se decide `skill`
1. **Vale a intenção, não a palavra.** "Faz um code review do texto da landing" quer reescrita de texto de página
   (`copywriting`), não `code-review`. "Desfaz o deploy" é `rollback`.
2. **A descrição da skill é o contrato.** Se o pedido cabe no "quando usar" de uma skill, é ela. Se cabe em duas, a
   melhor é a mais específica para o OBJETO do pedido; a outra entra em `aceitaveis` quando também resolveria.
3. **Pedido composto** (duas etapas com skills diferentes): `skill` = a da primeira etapa a executar; `aceitaveis`
   leva as skills de todas as etapas.
4. **Negação** tira a skill negada de `aceitaveis` ("não precisa revisar, só abre o PR" → só `pr-open`).

## Quando é `null` (≥ 25% dos pedidos) — `aceitaveis: []`
- **Trivial**: o agente resolve direto, sem rito — renomear variável, corrigir typo, trocar uma cor ou um rótulo,
  rodar um comando (testes, lint), fazer commit ou merge local, explicar um erro literal, pergunta conceitual.
  Carregar skill aqui é o erro que o exemplo mede (skill desnecessária custa contexto).
- **Fora do catálogo**: planilha de despesas, tradução, logo, e-mail pessoal, lembrete, responder cliente,
  publicar post (o catálogo planeja a pauta, não publica), migrar conteúdo de blog.
- **Vago sem objeto**: "dá uma olhada nisso", "tá lento", "melhora" — o certo é perguntar antes; nenhuma skill.
- **Conversa / pergunta sobre o catálogo**: "valeu!", "qual skill eu uso pra deploy?".

Vago COM objeto e com padrão claro do parque escolhe skill: "sobe isso aí" → `deploy-dev` (dev é o destino padrão;
produção exige pedido explícito).

## Pares próximos e a regra de desempate
| Par | Desempate |
|---|---|
| `code-review` × `security-review` | revisão genérica → `code-review`; pedido cita auth, permissão, token, segredo → `security-review` (a outra aceitável) |
| `code-review` × `simplify` | "tem bug?" → `code-review`; "tá verboso/duplicado, enxuga" no diff recém-escrito → `simplify` |
| `simplify` × `refactor-safe` | diff recém-escrito → `simplify`; código antigo a mover/dividir/renomear em vários arquivos → `refactor-safe` |
| `diagnosing-bugs` × `perf-profile` × `fix-ci` × `logs-prod` | intermitente/"às vezes" → `diagnosing-bugs`; lentidão com alvo → `perf-profile`; pipeline vermelho → `fix-ci`; "o que aconteceu em prod às 14h" → `logs-prod` |
| `migration-2bancos` × `db-query` × `perf-profile` | mudar schema ou dado em massa (coluna, índice, backfill) → `migration-2bancos`; pergunta de dado → `db-query`; medir consulta (EXPLAIN) → `perf-profile` |
| `deploy-dev` × `deploy-prod` × `rollback` | "homolog", "dev", sem ambiente → `deploy-dev`; "produção", "publica" → `deploy-prod`; "volta", "desfaz" → `rollback` |
| `test-writer` × `e2e-browser` | teste de função/módulo → `test-writer`; conferir fluxo no front real → `e2e-browser` |
| `grilling` × `to-tickets` | decisão em aberto → `grilling`; plano fechado a dividir → `to-tickets` |
| `frontend-design` × `ux-review` | tela nova ou remodelar → `frontend-design`; avaliar tela existente → `ux-review` |
| `prompt-tuning` × `llm-eval` | mudar o prompt → `prompt-tuning`; medir/comparar → `llm-eval` |
| `api-contract` × `docs-writer` | endpoint (parâmetros, respostas, compatibilidade) → `api-contract`; README, guia, ADR → `docs-writer` |
| `copywriting` × `ad-creative` | texto de página → `copywriting`; título/descrição de anúncio pago → `ad-creative` |
| `ads-audit` × `lead-report` | por que a campanha piorou/onde vai a verba → `ads-audit`; números de leads por canal → `lead-report` |
| `seo-audit` × `ai-seo` × `schema-markup` × `programmatic-seo` | diagnóstico no Google → `seo-audit`; ser citado por assistentes, `llms.txt` → `ai-seo`; JSON-LD/resultado rico → `schema-markup`; páginas em escala por template → `programmatic-seo` |
| `email-sequence` × `whatsapp-template` | régua de e-mails → `email-sequence`; HSM/template para aprovar na Meta → `whatsapp-template` |
| `video-listing` × `social-calendar` | um vídeo/roteiro → `video-listing`; pauta do mês → `social-calendar` |
| `dataviz` × `lead-report` | construir gráfico/painel → `dataviz`; relatório pronto de leads → `lead-report` |

## Famílias de caso difícil (`nota` começa com "difícil:")
1. Duas skills próximas (tabela acima).
2. Cita o nome de uma skill mas quer outra coisa (ou nenhuma).
3. Pedido composto.
4. Pedido vago (com e sem objeto).
5. Jargão do parque ("homolog", "HSM", "CPL", "502 na borda", "EXPLAIN", "ADR", "llms.txt", "CVE").
6. Trivial que parece pedir skill (→ `null`).
7. Negação ("não precisa revisar", "não precisa fazer deploy").
8. Fora do catálogo que parece dentro (logo × `frontend-design`; publicar post × `social-calendar`).

## Contagens (validador do rotulador, 2026-10-01, zero erros)
| arquivo | casos | difíceis | `skill: null` | com skill | mais de uma aceitável |
|---|---|---|---|---|---|
| `skills.json` | 42 skills | — | — | — | — |
| `rascunho.json` | 5 | 0 | 1 | 4 | 0 |
| `ajuste.json` | 36 | 24 (67%) | 10 (28%) | 26 | 9 |
| `teste.json` | 87 | 43 (49%) | 24 (28%) | 63 | 20 |

No teste, as 42 skills aparecem pelo menos uma vez como a melhor; no ajuste, 26 delas. Nenhuma skill do catálogo
fica sem uso em `aceitaveis`.

Por família (ajuste / teste): duas próximas 9/10 · jargão 4/9 · cita o nome de uma skill 3/7 · trivial que parece
pedir skill 3/5 · composto 2/5 · vago 2/5 · negação 1/1 · fora do catálogo que parece dentro 0/1.

O validador conferiu: envelope, campos e tipos, IDs em sequência, todo ID de `skill` e de `aceitaveis` existe em
`skills.json`, `skill` ∈ `aceitaveis`, `aceitaveis` vazio se e só se `skill` é `null`, ≥ 25% de `null`, mínimos,
≥ 30% difíceis, nenhum pedido repetido (nem entre arquivos), descrições de 30–260 caracteres, UTF-8 sem BOM, LF.

Ambiguidades decididas pelo rotulador (não estavam no briefing): `id` da skill em hífen-minúsculo e `nome` em
português; `skills.json` com o mesmo envelope dos casos; pedido composto → `skill` é a da primeira etapa; vago sem
objeto → `null` (perguntar), vago com padrão do parque → skill ("sobe isso aí" → `deploy-dev`); trivial → `null`
mesmo quando existe skill do assunto; pergunta sobre o catálogo → `null`; negação tira a skill negada de `aceitaveis`.
