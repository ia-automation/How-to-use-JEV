---
name: proveniencia
description: Quem estudou o quê em 2026-09-30 (Claude, Codex, medições, consolidação), cobertura honesta de cada estudo (download ≠ leitura; Codex 23 páginas + revisão dirigida; ninguém cobriu 100%), verificações feitas e a tabela de rastreio origem → destino da consolidação.
tipo: referencia
fonte: CODEX-STUDY.md, memory/study-log.md, memory/claude-study-review.md, memory/validation.md, sources/04-documentation.md, CHANGELOG.md e CLAUDE.md anteriores (originais em .local/antigos/2026-09-30/)
estudado_em: 2026-09-30
---

# Proveniência e cobertura

## Resumo honesto
- **Ninguém estudou 100% da documentação.** Arquivos baixados, páginas realmente lidas e comportamento
  testado são contagens diferentes.
- Fatos do doc levam [doc]; o que medimos, [testado] com data e n; vídeos, [terceiro]; conclusões e
  recomendações nossas, [local]. Medição local nunca vira contrato geral.
- Hierarquia: doc oficial > medição nossa > vídeo/opinião; quando doc e medição divergem, as duas ficam
  registradas ([contradicoes-da-documentacao](contradicoes-da-documentacao.md)).

## Estudo do Claude (2026-09-30)
- Baixou a documentação inteira: `fontes/docs/llms-full-2026-09-30.txt` (21.111 linhas), índice
  `llms-2026-09-30.txt` e as páginas `.md` individuais em `fontes/docs/paginas/` — **112 arquivos**,
  incluindo o retorno Page Not Found de `migrating-to-v1.md` (o histórico dizia 111). Fora do Git; fonte
  viva: https://docs.typesafe.ai/llms.txt (acrescentar `.md` a qualquer página).
- Estado estudado: `jev-1.13.0`, SDK Python 0.7.2, SDK JS 0.6.0.
- Produziu as notas temáticas (9 conceitos, 4 padrões, receitas, API + 2 SDKs, 3 vídeos, lições,
  pendências) e as skills `jev` e `jev-atualizar-memoria`. Receitas: **18 cookbooks + 1 demo** (o histórico
  dizia 17).
- Vídeos por transcrição de legenda automática (`fontes/videos/`, fora do Git).
- Revisão de lacunas (`lacunas-fechadas.md`): comparou cada linha > 40 caracteres das páginas com o
  llms-full (1.528 linhas ausentes, quase todas JSX/exemplos de requisição), leu na íntegra
  ConfidenceExplorer, ScoreExplorer e SdkSignature, extraiu `sdk/python/api/**` e leu o OpenAPI
  0.2.0 — sem chamada à API. Resultado: 4 ERRO · 7 LACUNA · 4 CONFIRMA (triagem abaixo).
- **Download não comprova leitura integral** de todas as páginas; o manifesto da empresa só foi lido por
  resumo de WebFetch (sem conferência primária).

## Estudo do Codex (2026-09-30)
- Vídeos na ordem pedida, por **legenda original completa** (`pt-orig`; as traduzidas deram HTTP 429) e
  quadros selecionados: vídeo 1 a cada 20 s; vídeo 2 em 23:18, 36:05, 37:20; vídeo 3 em 12:50, 19:55, 43:57.
  Duração somada 1h33min24s (material coberto, não tempo assistido). Uma tentativa de ASR local foi
  interrompida e não fundamenta as notas.
- Depois, **23 páginas centrais** da documentação (catálogo com URL, data e sha256 em
  `fontes/catalogo/catalogo.json`; snapshots em `.local/docs/`): introdução, quickstart, coding agents,
  System One, State, Primitives + Choice/Score/Noul/Advanced, Confidence, How to build, 4 padrões, Models,
  API, Agent skill, jaggedness 1.13, entradas dos SDKs. Componentes de interface e repetições em várias
  linguagens foram omitidos de algumas leituras. Sem busca geral na web.
- Revisão dirigida do material do Claude: comparou notas, SDKs, skills e seções de problema/técnicas/
  limites das 19 notas de receitas; conferiu OpenAPI, assinaturas Python, tipos JS, componentes
  interativos e exemplos críticos (catálogo adicional de 21 artefatos). Nem todos os blocos de código
  das receitas ou das fontes foram lidos. **O Codex não estudou 100% da documentação.**
- Destinos da documentação estudada pelo Codex (hoje): Introduction/System One/State/Primitives →
  [o-que-e-o-jev](../modelo/o-que-e-o-jev.md), [state](../modelo/state.md), [primitivas](../modelo/primitivas.md);
  How to build + padrões → [como-construir](../construir/como-construir.md) e `construir/padroes/`;
  API/Quickstart/Models → [api-http](../construir/api-http.md), [modelos-precos-limites](../modelo/modelos-precos-limites.md);
  Confidence + jaggedness → [confianca](../modelo/confianca.md), [limites-jev-1-13](../modelo/limites-jev-1-13.md), [metodo](../avaliar/metodo.md).
- Distinções que o Codex trouxe contra simplificações dos vídeos (todas absorvidas nas notas): Noul não é
  nulo; saída restrita não assegura acerto; várias perguntas não criam cadeia interna; contexto ainda
  importa; demos de voz usam uma etapa anterior de transcrição.

### Triagem das 15 observações do Claude (feita pelo Codex)
| ID | Tratamento |
|---|---|
| E1 confiança | Há aproximação no demo, sem fórmula contratual; diferença em Score conferida. Hoje medido ([confianca](../modelo/confianca.md)). |
| E2 retry Python | Padrões confirmados na assinatura: 2 retries e orçamento de 30 s; sem prometer interrupção rígida aos 30 s. |
| E3 instructions | Opcional/nulo no OpenAPI; obrigatório na prosa HTTP. Hoje medido: omitida → 200. |
| E4 Score nulo | Divergência JS × OpenAPI; hoje medido: 422. |
| C1 limites Score | Schema mínimo 1, JS 2, prosa até 10. Hoje medido: 11 → 400. |
| C2 limite Choice | 255 na prosa, ausente do schema. Hoje medido: 256 → 400. |
| C3 422 | Estrutura `detail/loc/msg/type` incorporada; outros corpos não presumidos. |
| C4 usage | Inteiros obrigatórios no HTTP × tolerância a `None` no Python. |
| L1 manifesto | Preservado como relato, **sem incorporação como fato** (só resumo de WebFetch). |
| L2 ScoreExplorer | Dados conferidos; os 5 exemplos hoje em [primitivas](../modelo/primitivas.md#exemplos-publicados-de-score-página-primitivesscore). |
| L3 leitura de Score | Distinção entre média ordinal, fração de clientes e acerto; tabela em [primitivas](../modelo/primitivas.md). |
| L4 níveis estruturados | 1,09/conf 0,87 e `legend` com objetos conferidos ([estrutura-nas-perguntas](../modelo/estrutura-nas-perguntas.md)). |
| L5 1 − Noul | Exemplo de orientação das parcelas em [como-construir](../construir/como-construir.md). |
| L6 state/caminhos | Política injetada no state e caminhos explícitos em [como-construir](../construir/como-construir.md). |
| L7 contraste/fan-out | Critérios simétricos em [estrutura-nas-perguntas](../modelo/estrutura-nas-perguntas.md). |

## Medições nossas (2026-09-30)
Chamadas reais à API (`jev-1.13.0`, do Brasil): contrato de fronteira, confiança, escala, estabilidade,
pt × en (40 pares sintéticos do Codex), 5 exemplos com dados rotulados pelo Codex e teste congelado, e texto
real pt-BR em corpora públicos (HateBR, B2W) com protocolo congelado. Tudo em
[medicoes](medicoes-2026-09-30.md); brutos em `.local/medicoes/`; caches nos projetos.

## Verificações registradas
- Codex, pacote inicial: `quick_validate.py` aprovou as skills; links relativos; JSONs; par
  requisição/resposta mock consistente; semente de 8 casos; normalizador VTT testado; hashes dos 23
  documentos e 3 legendas conferidos; exclusões do Git testadas; sem remoto.
- Codex, consolidação do Claude: 5 skills aprovadas (Python com `-X utf8`); 71 arquivos Markdown, 135
  links relativos e 141 wikilinks resolvidos; backup de 60 arquivos; 3 cópias do handoff por SHA-256;
  hashes dos 21 artefatos do catálogo adicional. Nenhuma inferência nessas duas etapas.
- Consolidação desta estrutura: `ferramentas/validar.py` (links, frontmatter, índice, JSON, skills, segredo,
  hashes do catálogo quando o arquivo local existe).

## Consolidação (2026-09-30)
Os dois acervos (`memoria/` do Claude e `memory/` + `sources/` + skills do Codex) viraram uma estrutura só:
`AGENTS.md` (instruções + núcleo), `conhecimento/` (um fato, um lugar, links relativos), 4 skills só de
procedimento, `fontes/catalogo/` e `ferramentas/`. Nenhum arquivo foi apagado: todos os originais estão em
`.local/antigos/2026-09-30/` com o caminho relativo de antes (inclusive as versões anteriores dos arquivos
reescritos no lugar). Conteúdo dos arquivos de handoff (`lacunas-fechadas.md`, `absorver-do-codex.md`) foi
absorvido nas notas indicadas na tabela.

## Rastreio da consolidação (origem → destino)
Cada linha é um arquivo que existia antes da consolidação de 2026-09-30. O original, byte a byte, está em
`.local/antigos/2026-09-30/<origem>` (conferido com `diff -r` antes de sair da árvore). 82 arquivos: nenhum
sem destino, nenhum perdido. Arquivos que não foram tocados (`exemplos/*/`, `avaliar/`, `propostas/`, `prova/`,
`fontes/`, `chat.txt`, `.claude-plugin/`) não entram na tabela.

| Origem (antes) | Destino (agora) |
|---|---|
| `.gitignore` | .gitignore (+ `fontes/docs/`, `fontes/videos/`) |
| `AGENTS.md` | AGENTS.md (reescrito: instruções + NÚCLEO) |
| `CHANGELOG.md` | CHANGELOG.md (entrada nova no topo; histórico mantido) |
| `CLAUDE.md` | CLAUDE.md (só `@AGENTS.md`); regras de nota → AGENTS.md |
| `CODEX-STUDY.md` | conhecimento/evidencias/proveniencia.md |
| `README.md` | README.md (reescrito) |
| `conhecimento/decidir/jev-llm-codigo.md` | conhecimento/decidir/jev-llm-codigo.md (links, híbridos, evidência R4/R5 e leads) |
| `conhecimento/evidencias/medicoes-2026-09-30.md` | conhecimento/evidencias/medicoes-2026-09-30.md (links, R4/R5, leads) |
| `memoria/INDICE.md` | conhecimento/INDICE.md |
| `memoria/conceitos/casos-de-uso.md` | conhecimento/modelo/casos-de-uso.md |
| `memoria/conceitos/como-construir.md` | conhecimento/construir/como-construir.md |
| `memoria/conceitos/confianca.md` | conhecimento/modelo/confianca.md |
| `memoria/conceitos/estrutura-nas-perguntas.md` | conhecimento/modelo/estrutura-nas-perguntas.md |
| `memoria/conceitos/limites-jev-1-13.md` | conhecimento/modelo/limites-jev-1-13.md |
| `memoria/conceitos/modelos-precos-limites.md` | conhecimento/modelo/modelos-precos-limites.md |
| `memoria/conceitos/o-que-e-o-jev.md` | conhecimento/modelo/o-que-e-o-jev.md |
| `memoria/conceitos/primitivas.md` | conhecimento/modelo/primitivas.md |
| `memoria/conceitos/state.md` | conhecimento/modelo/state.md |
| `memoria/licoes-transversais.md` | conhecimento/licoes-transversais.md |
| `memoria/padroes/fan-out-especulativo.md` | conhecimento/construir/padroes/fan-out-especulativo.md |
| `memoria/padroes/pontuacao-composta.md` | conhecimento/construir/padroes/pontuacao-composta.md |
| `memoria/padroes/roteamento-por-confianca.md` | conhecimento/construir/padroes/roteamento-por-confianca.md |
| `memoria/padroes/roteamento-por-intencao.md` | conhecimento/construir/padroes/roteamento-por-intencao.md |
| `memoria/perguntas-abertas.md` | conhecimento/evidencias/contradicoes-da-documentacao.md + conhecimento/evidencias/pendencias.md |
| `memoria/receitas/alinhamento-de-entidades.md` | conhecimento/receitas/alinhamento-de-entidades.md |
| `memoria/receitas/autoconsistencia-choices.md` | conhecimento/receitas/autoconsistencia-choices.md |
| `memoria/receitas/autoconsistencia-nouls.md` | conhecimento/receitas/autoconsistencia-nouls.md |
| `memoria/receitas/autoresearch-de-features.md` | conhecimento/receitas/autoresearch-de-features.md |
| `memoria/receitas/busca-linha-a-linha.md` | conhecimento/receitas/busca-linha-a-linha.md |
| `memoria/receitas/cascata-sde.md` | conhecimento/receitas/cascata-sde.md |
| `memoria/receitas/checagem-de-citacoes.md` | conhecimento/receitas/checagem-de-citacoes.md |
| `memoria/receitas/classificacao-com-confianca.md` | conhecimento/receitas/classificacao-com-confianca.md |
| `memoria/receitas/classificacao-hierarquica.md` | conhecimento/receitas/classificacao-hierarquica.md |
| `memoria/receitas/classificar-passagens-rag.md` | conhecimento/receitas/classificar-passagens-rag.md |
| `memoria/receitas/demo-casa-inteligente.md` | conhecimento/receitas/demo-casa-inteligente.md |
| `memoria/receitas/extracao-de-datas.md` | conhecimento/receitas/extracao-de-datas.md |
| `memoria/receitas/extracao-de-valor-pre-parseado.md` | conhecimento/receitas/extracao-de-valor-pre-parseado.md |
| `memoria/receitas/function-calling.md` | conhecimento/receitas/function-calling.md |
| `memoria/receitas/guardrails-llm.md` | conhecimento/receitas/guardrails-llm.md |
| `memoria/receitas/perguntas-em-paralelo.md` | conhecimento/receitas/perguntas-em-paralelo.md |
| `memoria/receitas/recuperacao-de-estrutura.md` | conhecimento/receitas/recuperacao-de-estrutura.md |
| `memoria/receitas/reranking.md` | conhecimento/receitas/reranking.md |
| `memoria/receitas/sugestao-de-skill.md` | conhecimento/receitas/sugestao-de-skill.md |
| `memoria/sdk/api-http.md` | conhecimento/construir/api-http.md |
| `memoria/sdk/javascript.md` | conhecimento/construir/sdk-javascript.md |
| `memoria/sdk/python.md` | conhecimento/construir/sdk-python.md |
| `memoria/visoes-externas/video-01-max-carrau.md` | conhecimento/evidencias/videos/video-01-max-carrau.md (+ timestamps e quadros do Codex) |
| `memoria/visoes-externas/video-02-quantbrasil.md` | conhecimento/evidencias/videos/video-02-quantbrasil.md (+ timestamps e quadros do Codex) |
| `memoria/visoes-externas/video-03-maestros-da-ia.md` | conhecimento/evidencias/videos/video-03-maestros-da-ia.md (+ timestamps e quadros do Codex) |
| `memory/INDEX.md` | AGENTS.md (NÚCLEO) + conhecimento/INDICE.md |
| `memory/claude-study-review.md` | conhecimento/evidencias/proveniencia.md |
| `memory/decisions.md` | conhecimento/evidencias/decisoes.md |
| `memory/open-questions.md` | conhecimento/evidencias/pendencias.md + conhecimento/evidencias/contradicoes-da-documentacao.md |
| `memory/study-log.md` | conhecimento/evidencias/proveniencia.md |
| `memory/validation.md` | conhecimento/evidencias/proveniencia.md |
| `scripts/__pycache__/normalize_youtube_vtt.cpython-312.pyc` | (bytecode; não recriado) |
| `scripts/normalize_youtube_vtt.py` | ferramentas/normalize_youtube_vtt.py |
| `skills/jev-api/SKILL.md` | skills/jev-integrar/SKILL.md + conhecimento/construir/integracao-segura.md |
| `skills/jev-api/assets/support-triage.request.json` | skills/jev-integrar/assets/support-triage.request.json |
| `skills/jev-api/assets/support-triage.response.mock.json` | skills/jev-integrar/assets/support-triage.response.mock.json |
| `skills/jev-api/references/http-contract.md` | conhecimento/construir/api-http.md + conhecimento/construir/integracao-segura.md |
| `skills/jev-api/references/model-snapshot.md` | conhecimento/modelo/modelos-precos-limites.md |
| `skills/jev-api/references/sdk-details.md` | conhecimento/construir/sdk-python.md + conhecimento/construir/sdk-javascript.md + conhecimento/construir/integracao-segura.md |
| `skills/jev-atualizar-memoria/SKILL.md` | skills/jev-manter/SKILL.md |
| `skills/jev-design/SKILL.md` | skills/jev-desenhar/SKILL.md |
| `skills/jev-design/references/application-patterns.md` | conhecimento/decidir/jev-llm-codigo.md + conhecimento/evidencias/videos/ + conhecimento/construir/padroes/fan-out-especulativo.md |
| `skills/jev-design/references/cookbook-patterns.md` | conhecimento/receitas/padroes-das-receitas.md (falha SDE → receitas/cascata-sde.md) |
| `skills/jev-design/references/decision-model.md` | conhecimento/modelo/primitivas.md + conhecimento/modelo/confianca.md |
| `skills/jev-evaluate/SKILL.md` | skills/jev-avaliar/SKILL.md + conhecimento/avaliar/metodo.md (armadilhas) |
| `skills/jev-evaluate/assets/seed-cases.json` | skills/jev-avaliar/assets/seed-cases.json |
| `skills/jev-evaluate/references/cookbook-evidence.md` | conhecimento/avaliar/leitura-critica-das-receitas.md |
| `skills/jev-evaluate/references/evaluation.md` | conhecimento/avaliar/metodo.md |
| `skills/jev/SKILL.md` | skills/jev-desenhar/SKILL.md |
| `sources/01-video-visao-geral.md` | conhecimento/evidencias/videos/video-01-max-carrau.md |
| `sources/02-video-arquitetura-e-limites.md` | conhecimento/evidencias/videos/video-02-quantbrasil.md |
| `sources/03-video-aplicacoes.md` | conhecimento/evidencias/videos/video-03-maestros-da-ia.md |
| `sources/04-documentation.md` | conhecimento/evidencias/proveniencia.md |
| `sources/catalog.json` | fontes/catalogo/catalogo.json (`estudo_codex`) |
| `sources/claude-handoff/2026-09-30/absorver-do-codex.md` | conhecimento/evidencias/videos/ (quadros) + conhecimento/construir/integracao-segura.md + conhecimento/evidencias/pendencias.md |
| `sources/claude-handoff/2026-09-30/lacunas-fechadas.md` | conhecimento/modelo/primitivas.md (L2, L3) + conhecimento/modelo/confianca.md (E1) + conhecimento/evidencias/contradicoes-da-documentacao.md + conhecimento/evidencias/proveniencia.md (triagem) + pendencias (L1) |
| `sources/claude-handoff/2026-09-30/manifest.json` | fontes/catalogo/catalogo.json (`handoff_claude`) |
| `sources/review-catalog.json` | fontes/catalogo/catalogo.json (`revisao_dirigida_codex`) |
