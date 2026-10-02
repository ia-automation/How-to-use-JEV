---
name: casos-externos
description: Catálogo de casos reais de uso do Jev relatados fora deste repositório (2026-09-15 → 2026-10-01) — 30 casos em 6 famílias, com número, fonte, o que o Jev substituiu e o que cada relato NÃO prova; os 26 exemplos novos que o repositório vai construir a partir deles.
tipo: visao-externa
fonte: leitura pela sessão de 2026-10-01 das fontes listadas em cada linha (páginas lidas por WebFetch; 1ª mão = repositório/post do autor; 2ª mão = reportagem ou agregador que cita o autor)
estudado_em: 2026-10-01
---

# Casos externos — onde o Jev está sendo usado no lugar de um LLM

Tudo aqui é **[terceiro]**: relato de quem construiu ou de quem reportou. Nenhum número foi reproduzido por nós.
"1ª mão" = README/post do próprio autor; "2ª mão" = agregador ou imprensa citando o autor. Os números promocionais
("40–400× mais barato") são do fornecedor e não entram nas linhas. Fidelidade: o que a fonte não diz está "(não declarado)".

## Por que esta nota existe
O doc da TypeSafe define 5 categorias ([casos-de-uso](../modelo/casos-de-uso.md)); até 2026-10-01 os exemplos deste
repositório cobriam só "automação com IA" e parte de "verificação". As famílias **programação/harness**, **tempo
real** e **map-reduce** não tinham exemplo medido. Este catálogo é a matéria-prima dos exemplos novos
([BRIEFING-2026-10-01](../../exemplos/BRIEFING-2026-10-01-casos-novos.md)).

## 1. Programação e agentes de código (harness)
| Caso | Desenho | Número relatado | O que NÃO prova | Fonte |
|---|---|---|---|---|
| **pi-warden** — guarda de tool-call para o agente Pi | Nouls por chamada: irreversível, fora da tarefa, muda algo, contradiz o plano, efeito fora da árvore; retém só por padrão destrutivo offline OU irreversível ≥ 0,7; os demais "orientam" o agente pelo contexto em vez de interromper | 321 sessões, 17.160 chamadas, 42 retenções, 5 aprovadas depois pelo usuário; regras de projeto: 0/150 violações com guarda × 6/150 sem; ~1.000 tokens, ~US$ 0,00004, ~0,3 s por julgamento | amostra de 15 tarefas e 2 modelos; instrumento no mesmo repo do medido; "88% corretas" é 2ª mão | 1ª mão: github.com/badgerexplore/pi-warden · 2ª: firecrawl.dev/blog/what-is-jev |
| **jev-guard** — "modo automático" para Claude Code, Codex, Copilot, Gemini CLI, Cursor, pi, OpenCode | Score de risco 4 níveis (só leitura → destrutivo) + Nouls `approval`, `user_requested`, `from_untrusted`; deny se risco ≥ 2,5 ou `from_untrusted` ≥ 0,7; ask se risco ≥ 1,5 ou approval ≥ 0,75, salvo `user_requested` ≥ 0,85; pós-ferramenta: `directed` ≥ 0,6 + `kind` (injection/canary/discussion/benign) | ~580 ms por chamada via Vercel AI Gateway; calibração mostrada em 3 exemplos (`ls` 0,0–0,1 · `git push` 2,0 · `rm -rf /` 3,0) | sem conjunto rotulado nem taxa de erro; "guardrail, não sandbox" | 1ª mão: github.com/leepokai/jev-guard |
| **Vercel** — revisor de segurança de comando em modo padrão | (não declarado) | "até 18× mais rápido (p95) e mais acurado" que o mesmo revisor em GPT Luna; "5 a 18× mais rápido" | 2ª mão (CEO/engenheiro citados); sem n, sem definição de acurácia | 2ª mão: thenextweb.com (TypeSafe Jev… Vercel), eesel.ai/blog/typesafe-jev-review |
| **Juiz de eval** (Good Start Labs, via Langfuse) | rubrica → Noul por item; mesmas instruções para Jev e 5 LLMs | 6.003 checagens em 1.203 respostas financeiras; Jev concorda com Fable 5.1 em 91,5% (86–92% com cada LLM; LLMs entre si 88–95%); US$ 160 por milhão de veredictos × US$ 33.000 (Fable 5.1), US$ 400 (GPT-5.6 Luna), US$ 1.600 (Gemini 3.8 Flash) | concordância ≠ acerto contra gabarito humano; a Langfuse diz que o Jev "não abstém" — contradiz o doc (faixa de confiança); sem rationale | 2ª mão: langfuse.com/blog/2026-09-18-using-typesafes-jev-for-evals |
| **Revisão de PR com checagens tipadas** (Paolo Rosson) | 14 checagens de segurança por diff | US$ 0,00007 por revisão × "US$ 0,14+" no Claude | 2ª mão; sem taxa de acerto | 2ª mão: ayautomate.com/jev-builds |
| **SQL semântico** — pg-jev, jevql (Postgres), duckdb-jev | `WHERE jev(linha, 'condição')` com limiar 0,5; `jev_prob`, `jev_score`, `jev_choice`; 20 linhas por requisição num state compartilhado, 1 Noul por linha; leitura em ordem física com memória constante | 129 linhas em ~1 s por US$ 0,0009 | sem medição de acerto | 1ª mão: github.com/realZachi/pg-jev, github.com/kylemclaren/jevql, github.com/recodelabs/duckdb-jev |
| **Classificar um crawl de documentação** (Firecrawl) | 3 perguntas por página (tipo, obsoleta, tem código) em passada paralela | 500 páginas × poucos mil tokens "abaixo de dez centavos"; "777 julgamentos em 0,7 s" (Every) | números de lista, não de acerto | 1ª/2ª mão: firecrawl.dev/blog/what-is-jev |
| **Injeção de prompt em página buscada** (Firecrawl) | 4 Nouls por passagem: relevante, tem evidência, contradiz a premissa, tenta instruir | post injetado 0,99 → descartado; páginas em 0,6 "ainda chegam ao prompt" | "filtro, não fronteira de segurança" | 1ª mão: idem |
| **Compactação de contexto** | (não declarado) | sessão de 1 M → 86 K tokens (um desenvolvedor) | sem método nem medida de perda | 2ª mão: eesel.ai/blog/typesafe-jev-review |
| **Seleção de skill** (receita oficial) | ver [sugestao-de-skill](../receitas/sugestao-de-skill.md) | erro 16,8% → 7,3% | — | doc |

## 2. Agentes que agem no mundo (navegador, PC, mundo físico)
| Caso | Desenho | Número | O que NÃO prova | Fonte |
|---|---|---|---|---|
| **browser-use/jev-ultrafast** | DOM vira tabela numerada; 1 Choice decide operação (CLICK, TYPE_TEXT, SELECT, SCROLL, WAIT, DONE, BLOCKED) e alvo numa chamada; LLM pequeno só gera o texto de TYPE_TEXT; alvo validado no DOM vivo | voo Zürich→Londres em 7,1 s; US$ 0,0039; mediana 9,45 → 7,09 s e 1.092 → 101 chamadas de protocolo contra a versão LLM | "3/3 em uma tarefa, um perfil — não é benchmark"; sem shadow DOM, frames, canvas, upload | 1ª mão: github.com/browser-use/jev-ultrafast |
| **awlevin/typesafe-computer-use** (Mac) | OmniParser local → símbolos; Jev decide | US$ 0,0002 por decisão × US$ 0,032 (Opus 5); tarefa de 12 passos US$ 0,003 × US$ 0,40–0,90; 0,13–0,38 s × 5,2 s | "todo raciocínio que o modelo de fronteira faz de graça tem de ser reconstruído como estado determinístico" | 2ª mão: dev.to/valyuai (how-to-use-jev) |
| **jev-drone** | Jev só na camada tática a 2,5 Hz: Choice de manobra, Score de risco, Noul "alvo perdido × ocluso"; controle (500 Hz) e guiagem (50 Hz) em código; visão clássica a 15 Hz | — | "o Jev não pode ser a percepção nem rodar na taxa de controle" | 2ª mão: idem |
| **jev-trader** (Monad) | decisão compra/venda a cada bloco de ~300 ms, ordens limit post-only | 81 ms de modelo | sem resultado financeiro declarado | 2ª mão: idem; github.com/jarrodwatts/jev-trader |
| **Semáforo / Doom / Rubik** | 1 pergunta por decisão de jogo | ~350 ms e ~US$ 0,001 por minuto de tráfego; ~10 decisões/s no Doom; cubo em 94 movimentos, ~4 s de modelo | demos | 2ª mão: ayautomate.com/jev-builds, datacamp.com (system-one-models-jev) |

## 3. Verificação, moderação e triagem em volume
| Caso | Desenho | Número | O que NÃO prova | Fonte |
|---|---|---|---|---|
| **Roteador de e-mail com escalada** (nutlope/jev-fraud) | Jev classifica; abaixo de 0,95 de confiança vai ao Kimi K3 | 100 e-mails em 1,42 s; 31 escalados; 96/100; ~US$ 0,07 | 100 e-mails, uma rodada, sem IC | 1ª mão: github.com/Nutlope/jev-fraud |
| **Bryo AI** — classificação de e-mail comercial | — | Gemini "um pouco mais acurado, 10–20× mais caro" | 2ª mão, sem números | 2ª mão: ayautomate.com/blog/jev-use-cases |
| **Triagem de 1.018 papers** (nutlope) | DeepSeek V4 Flash resume → 1 Choice de tópico por paper | resumos US$ 3,99 + classificação US$ 0,08; mediana 256 ms | sem gabarito | 2ª mão: dev.to/valyuai |
| **Notícias × marcas** | pontua cada notícia para 15 marcas | 384 itens em 24,9 s por US$ 0,19; "390× mais barato que Opus 5" | sem acerto | 2ª mão: ayautomate.com/jev-builds |
| **SOC / incidentes** (kenhuangus/jev-usecases) | 27 harnesses: triagem com 8 perguntas fechadas → auto_close / notify / queue_tier2 / contain_now; faixas 0,45 / 0,72 / 0,88; mitigação só se triagem = contain_now; contas a pagar, sinistros, AML, cláusulas | 27/30 runners passam nas fixtures; 3 que combinam Jev + LLM falharam ao vivo | o próprio README: "não é afirmação de que limiares e procedimentos estão prontos para rodar sem supervisão" | 1ª mão: github.com/kenhuangus/jev-usecases |
| **Suporte, teste de 284 chats** (eesel) | triagem + spam + rascunho (LLM) | triagem 93%; spam 100% pego, 0 falso positivo; rascunhos 93% sem erro, só 12% prontos para enviar | "a decisão é a polegada fácil; o trabalho ponta a ponta é a milha" | 2ª mão: eesel.ai/blog/typesafe-jev-review |
| **Debate político** (fact-check ao vivo) | 5 Nouls por fala | 1.191 chamadas, US$ 0,0497 | sem gabarito | 2ª mão: ayautomate.com/jev-builds |

## 4. Busca, rerank e features
| Caso | Desenho | Número | O que NÃO prova | Fonte |
|---|---|---|---|---|
| **JevRerank (LlamaIndex)** | 1 pergunta por par consulta–passagem | nDCG@5 0,340 → 0,396 no BEIR nfcorpus; ~US$ 0,0003 por consulta | um corpus | 2ª mão: ayautomate.com/jev-builds |
| **Rerank de busca web** (Firecrawl, receita oficial) | BM25 shortlist → Noul por par | top-1 5% → 18%, top-10 38% → 62%; 1.200 chamadas por US$ 0,0645 | ver [reranking](../receitas/reranking.md) | doc + firecrawl |
| **Relevância de memória** (Hugo Sequier) | classificação passagem-apoio | mais rápido que GPT-5.6 Luna, **27% mais caro** | contraexemplo ao "sempre mais barato": state grande por chamada | 2ª mão: ayautomate.com/jev-builds |
| **Ad-tech** (Amod Agashe) | previsão de desfecho sintético × GPT-5.6 Sol | 64× menos custo, 5,4× menos latência | dado sintético | 2ª mão: idem |

## 5. Comparações diretas com LLM (os números de "no lugar de")
| Fonte | Jev | Comparado | Observação |
|---|---|---|---|
| TypeSafe (via DataCamp) | 67,8% · US$ 0,0004 · 0,4 s por caso | GPT-5.6 Terra 67,9% · US$ 0,0304 · 10,1 s; Sol 74,1% · US$ 0,0836 · 23,3 s; Opus 5 73,1% · US$ 0,1761 · 37,8 s | benchmark do fornecedor, sem reprodução independente; 5–6 pontos abaixo dos melhores |
| QuantBrasil (vídeo 2) | 0,4 s · 0,02 por mil | DeepSeek V4 Flash 2,6 s · 0,14 | ver [video-02](videos/video-02-quantbrasil.md) |
| OpenRouter | ticket de 3 perguntas ≈ 447 tokens ≈ US$ 0,00002; 1 milhão ≈ US$ 19 | — | gateway: `typesafe/jev-1.13`, contexto 32k |

## 6. Onde o LLM ganha (evidência externa para [jev-llm-codigo](../decidir/jev-llm-codigo.md))
- **Sem justificativa**: nenhuma explicação em prosa → inviável onde a decisão precisa de rastro auditável (DataCamp, Langfuse).
- **Acurácia de topo**: 5–6 pontos abaixo de Sol/Opus 5 no benchmark do fornecedor.
- **State grande por chamada** pode sair mais caro que um LLM pequeno (relevância de memória: +27% contra Luna).
- **Raciocínio implícito**: no computer-use, "todo raciocínio que o modelo de fronteira faz de graça tem de ser reconstruído como estado determinístico".
- **Ponta a ponta**: decidir é a parte barata; escrever a resposta, agir e verificar continuam custando (eesel).
- **Percepção e taxa de controle**: não é camada de visão nem roda a 50–500 Hz (drone).

## Agregadores (para achar mais casos)
ayautomate.com/jev-builds (índice com ~1.300 entradas de X/LinkedIn/GitHub, "não usamos Jev em cliente ainda") ·
madewithjev.com (685 builds por tarefa) · github.com/devnacho/awesome-jev-use-cases (CC0, 150+ repos) ·
Discord da TypeSafe. Nenhum deles valida números.

## Do catálogo aos exemplos deste repositório
26 exemplos novos mapeados em 2026-10-01 (5 já existiam). Onda 1: guarda de tool-call · juiz de eval · conferência de
promessas · imóvel errado · roteador de e-mail (dado real F11). Lista completa, dados e ordem:
[BRIEFING-2026-10-01](../../exemplos/BRIEFING-2026-10-01-casos-novos.md). As 11 propostas do Codex de 2026-09-30
(pilotos do CRM e fora dele) vivem na pasta de estudo e entram nas ondas seguintes.

## Relacionados
[casos-de-uso](../modelo/casos-de-uso.md) · [jev-llm-codigo](../decidir/jev-llm-codigo.md) · [video-02](videos/video-02-quantbrasil.md) ·
[video-03](videos/video-03-maestros-da-ia.md) · [pendencias](pendencias.md)
