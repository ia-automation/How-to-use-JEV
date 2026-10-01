# Índice do conhecimento sobre o Jev

Uma linha por nota. Comece pelo NÚCLEO em [AGENTS.md](../AGENTS.md); abra aqui só a nota que o assunto pede.
Estado: **2026-09-30**, modelo `jev-1.13.0`, SDK Python 0.7.2, SDK JS 0.6.0. Rótulos nas notas:
[doc] documentação · [testado] medido por nós (data, n) · [terceiro] vídeo · [local] proposta/conclusão nossa.

## Comece aqui
- [Lições transversais](licoes-transversais.md) — 25 regras que valem em toda integração + anti-padrões
- [Código × Jev × LLM](decidir/jev-llm-codigo.md) — 5 perguntas de triagem, matriz, custos medidos, os híbridos, erros comuns, checklist

## Modelo
- [O que é o Jev](modelo/o-que-e-o-jev.md) — System One, RLCD, calibração em grupo; o que não é (não é LLM de chat/código)
- [State](modelo/state.md) — string/objeto/array; só o relevante; caminhos entre crases; só texto
- [Primitivas](modelo/primitivas.md) — Choice (≤255), Score (2–10 níveis), Noul (sem confidence); tetos medidos; exemplos publicados de Score
- [Estrutura nas perguntas](modelo/estrutura-nas-perguntas.md) — EntryType; what/not_for/examples; subárvore; exemplos em níveis
- [Confiança](modelo/confianca.md) — derivada das probabilidades; fórmula só aproxima (medido); 3 faixas; limiar por risco
- [Modelos, preço e limites](modelo/modelos-precos-limites.md) — US$ 0,042/M entrada, saída grátis; 64k/32k; 100K tok/s e 40 req/s; aliases; gateways; skill oficial
- [Limites do jev-1.13](modelo/limites-jev-1-13.md) — 9 falhas conhecidas e o contorno de cada
- [Casos de uso](modelo/casos-de-uso.md) — 5 categorias, 10 formatos de decisão → receita

## Construir
- [Como construir](construir/como-construir.md) — 8 passos; exemplo de triagem completo; quando fazer 2ª chamada
- [Fan-out especulativo](construir/padroes/fan-out-especulativo.md) — todas as perguntas numa chamada; código ignora o que não usa
- [Roteamento por confiança](construir/padroes/roteamento-por-confianca.md) — piso 0,6; limiar por ação
- [Pontuação composta](construir/padroes/pontuacao-composta.md) — Scores atômicos + pesos no código
- [Roteamento por intenção](construir/padroes/roteamento-por-intencao.md) — Jev na frente; código, LLM especialista ou humano
- [API HTTP](construir/api-http.md) — endpoint, corpo, resposta, prosa × schema × servidor, erros 400/401/422/429/529
- [SDK Python](construir/sdk-python.md) — `typesafe-sdk` 0.7.2; síncrono/assíncrono; response_model; RetryPolicy com orçamento 30 s; divergências JS × Python
- [SDK JavaScript](construir/sdk-javascript.md) — `@typesafe-ai/sdk` 0.6.0; tipos inferidos; retentativa padrão; APIPromise
- [Integração segura](construir/integracao-segura.md) — ausência = erro, validar antes do efeito, orçamento único de retentativa, chave e logs

## Receitas (cookbooks destilados)
- [Padrões das receitas](receitas/padroes-das-receitas.md) — síntese do Codex: desenho reutilizável e cuidado de cada receita
- [Perguntas em paralelo](receitas/perguntas-em-paralelo.md) — 13 perguntas numa chamada: 12,2× mais barato, 10× mais rápido (contra sequencial)
- [Classificação com confiança](receitas/classificacao-com-confianca.md) — 75 grupos SIC; conf < 0,9 → divisão pai; 80% × 65%
- [Classificação hierárquica](receitas/classificacao-hierarquica.md) — Choice por nó + beam K=3
- [Autoconsistência: choices](receitas/autoconsistencia-choices.md) — 8 Choices × 15 repetições; 99,2% concordância; 114 ms
- [Autoconsistência: nouls](receitas/autoconsistencia-nouls.md) — 14 Nouls; desvio 0,0102; faixa 0,30–0,70 → humano
- [Checagem de citações](receitas/checagem-de-citacoes.md) — string match + 1 Choice; auto-aceita ≥ 0,8
- [Classificar passagens de RAG](receitas/classificar-passagens-rag.md) — 4 Nouls por passagem: evidência, conflito ou descarte
- [Guardrails para LLM](receitas/guardrails-llm.md) — 4 Nouls de perigo + Score de severidade; pass/review/block/support
- [Cascata de extração (SDE)](receitas/cascata-sde.md) — mini extrai, Jev verifica por campo, grande só se algum > 0,7; falha de parse aceita
- [Extração de valor pré-parseado](receitas/extracao-de-valor-pre-parseado.md) — regex acha candidatos, Choice escolhe, código copia
- [Extração de datas](receitas/extracao-de-datas.md) — Choice por parte da data; código faz o calendário; < 0,60 → revisão
- [Alinhamento de entidades](receitas/alinhamento-de-entidades.md) — Score de 3 níveis + 3 Nouls de diagnóstico; 450 pares
- [Function calling](receitas/function-calling.md) — 54 perguntas por comando; confiança = julgamento mais fraco
- [Sugestão de skill](receitas/sugestao-de-skill.md) — ≤ 1 skill entre 182; 2 requisições; erro 16,8% → 7,3%
- [Busca linha a linha](receitas/busca-linha-a-linha.md) — Choice sobre 218 ids de linha + Noul "existe resposta?"
- [Reranking](receitas/reranking.md) — 1 Noul por par; top-10 38% → 62%; 1.200 chamadas por US$ 0,0645
- [Recuperação de estrutura](receitas/recuperacao-de-estrutura.md) — Markdown de texto puro em 2 requisições, sem gerar palavra
- [Autoresearch de features](receitas/autoresearch-de-features.md) — LLM propõe perguntas, Jev responde, CatBoost aprende; RMSE 3,09 → 1,77
- [Demo casa inteligente](receitas/demo-casa-inteligente.md) — fan-out extremo; LLM só para conversa

## Avaliar
- [Método](avaliar/metodo.md) — protocolo, métricas por primitiva, limiares, e as lições de método das nossas execuções
- [Leitura crítica das receitas](avaliar/leitura-critica-das-receitas.md) — o que os benchmarks oficiais concluem e o que não
- [Prova fria](avaliar/prova-fria.md) — como avaliamos o próprio acervo com agente frio; condições comparáveis; contêiner; rodada 1

## Evidências
- [Medições de 2026-09-30](evidencias/medicoes-2026-09-30.md) — contrato, confiança, escala, estabilidade, pt × en, exemplos, texto real pt-BR (HateBR/B2W), leads reais
- [Contradições da documentação](evidencias/contradicoes-da-documentacao.md) — prosa × OpenAPI × SDK × servidor; erros das receitas
- [Pendências](evidencias/pendencias.md) — o que falta provar (gateways, limites de taxa, retry Python, limiares reais, instalação)
- [Decisões](evidencias/decisoes.md) — decisões do acervo e do dono
- [Proveniência](evidencias/proveniencia.md) — quem estudou o quê, cobertura honesta, verificações, rastreio da consolidação
- [Vídeo 1 — Max Carrau](evidencias/videos/video-01-max-carrau.md) — a tese em 4 min; "a gaveta da automação"
- [Vídeo 2 — QuantBrasil](evidencias/videos/video-02-quantbrasil.md) — teste real: 6–7× mais rápido, ~7× e ~200× mais barato; o erro do "MS"
- [Vídeo 3 — Maestros da IA](evidencias/videos/video-03-maestros-da-ia.md) — 4 apps de demo; 1 pergunta por item; quadros com latência/custo; cuidado com a propaganda

## Fora de `conhecimento/`
- [Exemplos medidos](../exemplos/README.md) — 5 projetos na API real (roteador, triagem, extração, guardrail, busca)
- [pt × en sintético](../avaliar/resultados-pt-en.md) · [texto real pt-BR](../avaliar/publicos/README.md)
- Skills (procedimentos): [jev-desenhar](../skills/jev-desenhar/SKILL.md) · [jev-integrar](../skills/jev-integrar/SKILL.md) · [jev-avaliar](../skills/jev-avaliar/SKILL.md) · [jev-manter](../skills/jev-manter/SKILL.md)
