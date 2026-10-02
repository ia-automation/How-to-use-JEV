# Resultados — jev-x-llm (o mesmo teste congelado, respondido por um LLM barato)

rodada 2 — pós-revisão do Codex (2026-10-01), NÃO cega, reproduzida do cache da rodada 1 sem chamada nova.

Gerado por `run.py` em 2026-10-01 (modo LLM `gravado`; Jev sempre `gravado`, 0 chamadas). LLM: `claude-haiku-4-5-20251001`, temperatura 0.0, max_tokens 400, uma chamada por caso em série, 2 retries; preço US$ 1.00/M entrada e US$ 5.00/M saída (tabela pública da Anthropic, consultada em 2026-10-01). Jev: `jev-1.13.0`, US$ 0,042/M entrada, latência da rodada original (8 em paralelo). Prompt = state + perguntas de `perguntas.py` do exemplo, serializados em JSON, mais o texto fixo `comparar.SISTEMA`; resposta validada por `llmcache.validar_resposta` (fora do esquema = falha operacional, contada à parte, nunca gravada como resposta); decisão pela regra do próprio exemplo (`comparar.py`).

Critério (fixado antes da primeira chamada): **fixado_em**: 2026-10-01, antes da primeira chamada ao LLM; **lado_a_lado**: mesmo teste congelado (hash do manifesto de cada exemplo conferido), mesmas instructions/criteria/opções de perguntas.py serializadas em JSON, mesma validação estrita, mesma regra de decisão do módulo do exemplo (respostas do LLM injetadas no lugar das do Jev: Noul true/false → 1,0/0,0; Choice → one-hot), mesmo baseline; **metrica_principal**: LLM ganha se acerta ≥ 3 casos a mais que o Jev; perde se ≥ 3 a menos; senão empata. Falha operacional do LLM conta como erro (como `revisar`) e é reportada à parte; **erro_caro**: contagem absoluta: LLM ganha se tem MENOS erros caros que o Jev, perde se tem MAIS, empata se igual (erro caro é raro: cada caso conta); **custo_latencia**: razão = US$ por mil casos do LLM ÷ do Jev (tokens de entrada + saída ao preço publicado, input US$ 1,00/M e output US$ 5,00/M em 2026-10-01; Jev US$ 0,042/M só entrada); latência = p50 do LLM ÷ p50 do Jev, as duas medidas na chamada real (Jev com 8 em paralelo na rodada original; LLM em série); **concordancia**: fração dos casos em que a decisão final do Jev e a do LLM são iguais (ação+tipo / grupo+folha+revisar / relação); informativa, não decide; **o_que_nao_conclui**: um fornecedor, um modelo barato (Haiku 4.5), uma rodada, temperatura 0, prompt sem exemplos e sem raciocínio pedido; dados sintéticos do mesmo fornecedor do LLM. Nada aqui mede o topo da linha nem o que um prompt afinado faria.

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T23:45:23-03:00): `comparar.py` sha256 077e2e546eb7b97c… · `criterio.py` sha256 ae51b3a8cde4c604… · `run.py` sha256 f6c25497fbf906c7… · `../_comum/llmcache.py` sha256 75b0227322b5eaf4… · `../opt-out-lgpd/perguntas.py` sha256 a494a14de522a0d1… · `../opt-out-lgpd/optout.py` sha256 50f780a69cd3c413… · `../opt-out-lgpd/run.py` sha256 f8ef07f6e3a22368… · `../opt-out-lgpd/dados/teste.json` sha256 1207d0b7d4d14d6a… · `../motivo-de-perda/perguntas.py` sha256 8b2914532a561610… · `../motivo-de-perda/motivo.py` sha256 44151a7e23ba2ec4… · `../motivo-de-perda/run.py` sha256 625005edb785efe1… · `../motivo-de-perda/dados/teste.json` sha256 015a04e1f083ddb7… · `../auditor-de-evidencia/perguntas.py` sha256 bc1f1307eaabb826… · `../auditor-de-evidencia/auditor.py` sha256 47832e24fe065ea4… · `../auditor-de-evidencia/run.py` sha256 15865525a2d7cbbb… · `../auditor-de-evidencia/dados/teste.json` sha256 6bdb935ba4030be2… · `../motivo-de-perda/dados/taxonomia.json` sha256 7ab1ad5faeeedc80…

Tentativas HTTP ao LLM nesta execução: 0; acumulado em `orcamento.json`: 215 de 250.

## Resumo

| exemplo | n | principal Jev | principal LLM | principal baseline | LLM − Jev (casos) | LLM na principal | erro caro Jev | erro caro LLM | erro caro baseline | LLM no erro caro | falha op. LLM | p50 Jev/LLM ms | p95 Jev/LLM ms | US$/1000 Jev | US$/1000 LLM | concordância |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| opt-out-lgpd | 60 | 0.867 | 0.850 | 0.717 | -1 | empata | 0 | 1 | 10 | perde | 0 | 324/1323 | 663/1394 | 0.0852 | 2.7659 | 47/60 |
| motivo-de-perda | 68 | 0.853 | 0.147 | 0.279 | -48 | perde | 4 | 1 | 41 | ganha | 57 | 286/2049 | 338/2286 | 0.2548 | 7.4989 | 9/68 |
| auditor-de-evidencia | 73 | 0.795 | 0.685 | 0.425 | -8 | perde | 1 | 15 | 26 | perde | 0 | 287/1344 | 387/1513 | 0.1516 | 4.4561 | 45/73 |

## `opt-out-lgpd` — 60 casos do teste congelado

Métrica principal: **acerto da ação (5 classes)**. Erro caro: **infração + obrigação pela metade + bloqueio indevido (os três somados; cada um reportado)**. Baseline: lista de expressões (optout.baseline).

### Métricas do próprio exemplo (funções do `run.py` dele), Jev × LLM × baseline nos mesmos casos

| lado | n | acerto_acao | INFRAÇÃO (opt-out/LGPD real → seguir) | obrigação pela metade | BLOQUEIO INDEVIDO (sem opt-out nem LGPD → bloqueia) | bloqueou c/ opt_out falso (todos) | null → revisar | revisou sem necessidade | tipo LGPD certo (pedidos reais) |
|---|---|---|---|---|---|---|---|---|---|
| Jev | 60 | 0.867 | 0/31 | 0/31 | 0/28 | 1/40 | 1/1 | 7/59 | 15/18 |
| LLM | 60 | 0.850 | 0/31 | 0/31 | 1/28 | 2/40 | 1/1 | 3/59 | 18/18 |
| baseline | 60 | 0.717 | 4/31 | 1/31 | 5/28 | 6/40 | 0/1 | 0/59 | 14/18 |

### Veredito pelo critério congelado (gerado pelo script)

| o quê | Jev | LLM | baseline | LLM − Jev | o LLM |
|---|---|---|---|---|---|
| métrica principal (acertos) | 52/60 (0.867) | 51/60 (0.850) | 43/60 (0.717) | -1 casos | **empata** |
| erro caro (contagem) | 0 | 1 | 10 | +1 | **perde** |
| falha operacional | 0 | 0 | 0 |  |  |

Veredito: na métrica principal o LLM **empata** (-1 casos em n = 60; empate abaixo de 3); no erro caro o LLM **perde** (1 × 0). Razão de custo LLM ÷ Jev: **32×** (US$ 2.7659 × 0.0852 por mil casos); razão de latência (p50): **4.1×** (1323 × 324 ms).

Concordância Jev × LLM: decisão final igual em **47/60** (0.783); por pergunta (Jev ≥ 0,5 × LLM true, Choice = mesma opção) 387/420 (0.921).

### Custo e latência (medidos na chamada real; do cache também)

| lado | requisições | novas (não cache) | respostas inválidas | tentativas HTTP | p50_ms | p95_ms | tokens entrada/caso | tokens saída/caso | US$ total | US$/1000 casos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev | 60 | 0 | 0 | — | 324 | 663 | 2028 | 0 | 0.0051 | 0.0852 | jev-1.13.0 |
| LLM | 60 | 0 | 0 | 0 | 1323 | 1394 | 2290 | 95 | 0.1660 | 2.7659 | claude-haiku-4-5-20251001 |

### Caso a caso

erro caro = infração (opt-out/LGPD real → seguir) + obrigação pela metade + bloqueio indevido; `caro` na tabela nomeia a perda. ✗F = falha operacional (não pontua, mesmo com gabarito `revisar`). Sinais do LLM: S = true, n = false, na ordem dos 6 Nouls; tipo = Choice.

| id | fam | gab | Jev | ok J | caro J | LLM | ok L | caro L | base | ok B | LLM: nouls opt·pausa·lgpd·cont·s/obj·terc / tipo | motivo LLM |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OL-T001 | fácil / outros | bloquear_envios | bloquear_envios | ✓ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T002 | fácil / outros | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·S·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T003 | fácil / outros | bloquear_envios | bloquear_envios | ✓ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T004 | fácil / outros | abrir_pedido_lgpd(origem_dos_dados) | abrir_pedido_lgpd(origem_dos_dados) | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | ✓ | n·n·S·n·n·n / data_source | direito de titular: origem_dos_dados |
| OL-T005 | fácil / outros | pausar | pausar | ✓ |  | pausar | ✓ |  | seguir | ✗ | n·S·n·n·n·n / none | pausa com retomada |
| OL-T006 | fácil / outros | abrir_pedido_lgpd(exclusao) | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ | S·n·S·n·n·n / deletion | direito de titular: exclusao |
| OL-T007 | fácil / outros | abrir_pedido_lgpd(correcao) | abrir_pedido_lgpd(correcao) | ✓ |  | abrir_pedido_lgpd(correcao) | ✓ |  | abrir_pedido_lgpd(correcao) | ✓ | n·n·S·n·n·n / correction | direito de titular: correcao |
| OL-T008 | negação | seguir | seguir | ✓ |  | pausar | ✗ |  | seguir | ✓ | n·S·n·S·n·n / none | pausa com retomada |
| OL-T009 | ironia | bloquear_envios | bloquear_envios | ✓ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T010 | terceiro | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·S·n·S / none | nenhum pedido de parar, pausar ou de titular |
| OL-T011 | terceiro | abrir_pedido_lgpd(exclusao) | revisar | ✗ |  | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ | S·n·S·n·n·n / deletion | direito de titular: exclusao |
| OL-T012 | pausa × opt-out | pausar | pausar | ✓ |  | pausar | ✓ |  | seguir | ✗ | n·S·n·n·n·n / none | pausa com retomada |
| OL-T013 | fácil / outros | abrir_pedido_lgpd(exclusao) | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ | S·n·S·n·n·n / deletion | direito de titular: exclusao |
| OL-T014 | fácil / outros | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·n·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T015 | negação | bloquear_envios | bloquear_envios | ✓ |  | abrir_pedido_lgpd(exclusao) | ✗ |  | abrir_pedido_lgpd(exclusao) | ✗ | S·n·S·n·n·n / deletion | direito de titular: exclusao |
| OL-T016 | fácil / outros | abrir_pedido_lgpd(acesso) | abrir_pedido_lgpd(acesso) | ✓ |  | abrir_pedido_lgpd(acesso) | ✓ |  | seguir | ✗ | n·n·S·n·n·n / access | direito de titular: acesso |
| OL-T017 | fácil / outros | pausar | pausar | ✓ |  | pausar | ✓ |  | pausar | ✓ | n·S·n·n·n·n / none | pausa com retomada |
| OL-T018 | fácil / outros | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·S·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T019 | ironia | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·S·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T020 | 'para' ambíguo | seguir | revisar | ✗ |  | bloquear_envios | ✗ | bloqueio indevido | bloquear_envios | ✗ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T021 | fácil / outros | bloquear_envios | bloquear_envios | ✓ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T022 | fácil / outros | abrir_pedido_lgpd(origem_dos_dados) | abrir_pedido_lgpd(origem_dos_dados) | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | ✓ |  | seguir | ✗ | n·n·S·n·n·n / data_source | direito de titular: origem_dos_dados |
| OL-T023 | fácil / outros | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·S·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T024 | fácil / outros | bloquear_envios | bloquear_envios | ✓ |  | revisar | ✗ |  | bloquear_envios | ✓ | S·n·n·n·S·n / none | opt-out em conflito: não diz o que parar |
| OL-T025 | negação | seguir | seguir | ✓ |  | seguir | ✓ |  | bloquear_envios | ✗ | n·n·n·S·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T026 | fácil / outros | bloquear_envios | bloquear_envios | ✓ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T027 | fim de interesse sem pedido de parar | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·n·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T028 | fácil / outros | pausar | revisar | ✗ |  | pausar | ✓ |  | seguir | ✗ | n·S·n·n·n·n / none | pausa com retomada |
| OL-T029 | fácil / outros | abrir_pedido_lgpd(correcao) | abrir_pedido_lgpd(correcao) | ✓ |  | abrir_pedido_lgpd(correcao) | ✓ |  | abrir_pedido_lgpd(correcao) | ✓ | n·n·S·n·n·n / correction | direito de titular: correcao |
| OL-T030 | terceiro | abrir_pedido_lgpd(exclusao) | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ | S·n·S·n·n·n / deletion | direito de titular: exclusao |
| OL-T031 | reclamação longa | bloquear_envios | bloquear_envios | ✓ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T032 | reclamação longa | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·S·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T033 | tipo | abrir_pedido_lgpd(acesso) | abrir_pedido_lgpd(acesso) | ✓ |  | abrir_pedido_lgpd(acesso) | ✓ |  | abrir_pedido_lgpd(acesso) | ✓ | n·n·S·n·n·n / access | direito de titular: acesso |
| OL-T034 | fácil / outros | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·n·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T035 | 'para' ambíguo | bloquear_envios | bloquear_envios | ✓ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T036 | negação | seguir | seguir | ✓ |  | seguir | ✓ |  | bloquear_envios | ✗ | n·n·n·S·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T037 | terceiro | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·S·n·S / none | nenhum pedido de parar, pausar ou de titular |
| OL-T038 | fácil / outros | abrir_pedido_lgpd(acesso) | abrir_pedido_lgpd(acesso) | ✓ |  | abrir_pedido_lgpd(acesso) | ✓ |  | seguir | ✗ | n·n·S·n·n·n / access | direito de titular: acesso |
| OL-T039 | fácil / outros | pausar | pausar | ✓ |  | pausar | ✓ |  | seguir | ✗ | n·S·n·n·n·n / none | pausa com retomada |
| OL-T040 | dois pedidos | abrir_pedido_lgpd(origem_dos_dados) | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | ✓ |  | bloquear_envios | ✗ | S·n·S·n·n·n / data_source | direito de titular: origem_dos_dados |
| OL-T041 | fácil / outros | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·S·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T042 | fácil / outros | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·n·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T043 | fácil / outros | seguir | seguir | ✓ |  | pausar | ✗ |  | bloquear_envios | ✗ | n·S·n·S·n·n / none | pausa com retomada |
| OL-T044 | fácil / outros | abrir_pedido_lgpd(exclusao) | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ | n·n·S·n·n·n / deletion | direito de titular: exclusao |
| OL-T045 | ironia | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·n·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T046 | fácil / outros | bloquear_envios | abrir_pedido_lgpd(exclusao) | ✗ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T047 | tipo | abrir_pedido_lgpd(correcao) | abrir_pedido_lgpd(correcao) | ✓ |  | abrir_pedido_lgpd(correcao) | ✓ |  | abrir_pedido_lgpd(correcao) | ✓ | n·n·S·n·n·n / correction | direito de titular: correcao |
| OL-T048 | pausa × opt-out | pausar | revisar | ✗ |  | revisar | ✗ |  | bloquear_envios | ✗ | S·S·n·n·n·n / none | opt-out em conflito: pausa com retomada |
| OL-T049 | origem sem pedir exclusão | abrir_pedido_lgpd(origem_dos_dados) | abrir_pedido_lgpd(origem_dos_dados) | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | ✓ | n·n·S·n·n·n / data_source | direito de titular: origem_dos_dados |
| OL-T050 | pausa × opt-out | bloquear_envios | bloquear_envios | ✓ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T051 | pausa × opt-out | seguir | seguir | ✓ |  | pausar | ✗ |  | seguir | ✓ | n·S·n·S·n·n / none | pausa com retomada |
| OL-T052 | origem sem pedir exclusão | abrir_pedido_lgpd(origem_dos_dados) | abrir_pedido_lgpd(origem_dos_dados) | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | ✓ | n·n·S·n·n·n / data_source | direito de titular: origem_dos_dados |
| OL-T053 | negação | seguir | seguir | ✓ |  | abrir_pedido_lgpd(acesso) | ✗ |  | seguir | ✓ | n·n·S·S·n·n / access | direito de titular: acesso |
| OL-T054 | exclusão parcial | abrir_pedido_lgpd(exclusao) | revisar(exclusao) | ✗ |  | abrir_pedido_lgpd(exclusao) | ✓ |  | abrir_pedido_lgpd(exclusao) | ✓ | S·n·S·S·n·n / deletion | direito de titular: exclusao |
| OL-T055 | fácil / outros | bloquear_envios | revisar | ✗ |  | bloquear_envios | ✓ |  | bloquear_envios | ✓ | S·n·n·n·n·n / none | opt-out definitivo |
| OL-T056 | fácil / outros | seguir | seguir | ✓ |  | seguir | ✓ |  | seguir | ✓ | n·n·n·S·n·n / none | nenhum pedido de parar, pausar ou de titular |
| OL-T057 | tipo | abrir_pedido_lgpd(acesso) | abrir_pedido_lgpd(acesso) | ✓ |  | abrir_pedido_lgpd(acesso) | ✓ |  | abrir_pedido_lgpd(acesso) | ✓ | n·n·S·n·n·n / access | direito de titular: acesso |
| OL-T058 | fácil / outros | pausar | pausar | ✓ |  | pausar | ✓ |  | seguir | ✗ | n·S·n·n·n·n / none | pausa com retomada |
| OL-T059 | terceiro | bloquear_envios | revisar | ✗ |  | revisar | ✗ |  | seguir | ✗ | S·n·n·n·n·S / none | opt-out em conflito: pedido sobre outro número |
| OL-T060 | 'para' ambíguo | revisar | revisar | ✓ |  | revisar | ✓ |  | bloquear_envios | ✗ | S·n·n·n·S·n / none | opt-out em conflito: não diz o que parar |

## `motivo-de-perda` — 68 casos do teste congelado

Métrica principal: **acerto folgado (folha ∈ aceitáveis ou só-grupo certo; revisão e falha = erro), variante c**. Erro caro: **motivo inventado + grupo errado automatizado (contados juntos, como no exemplo)**. Baseline: palavra-chave por folha (motivo.baseline).

### Métricas do próprio exemplo (funções do `run.py` dele), Jev × LLM × baseline nos mesmos casos

| lado | n | acerto estrito | acerto folgado | grupo certo | motivo INVENTADO | grupo errado auto. | só-grupo certo | sem_info certo | absteve | folha errada | revisar | falha |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev | 68 | 0.809 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 7/8 | 0/61 | 1/68 | 5/68 | 0/68 |
| LLM | 68 | 0.147 | 0.147 | 0.147 | 0/8 | 1/68 | 0/7 | 8/8 | 0/61 | 0/68 | 0/68 | 57/68 |
| LLM tolerante (secundária) | 68 | 0.765 | 0.809 | 0.882 | 0/8 | 7/68 | 3/7 | 8/8 | 0/61 | 5/68 | 1/68 | 0/68 |
| baseline | 68 | 0.250 | 0.279 | 0.397 | 7/8 | 41/68 | 0/7 | 1/8 | 0/61 | 8/68 | 0/68 | 0/68 |

### Veredito pelo critério congelado (gerado pelo script)

| o quê | Jev | LLM | baseline | LLM − Jev | o LLM |
|---|---|---|---|---|---|
| métrica principal (acertos) | 58/68 (0.853) | 10/68 (0.147) | 19/68 (0.279) | -48 casos | **perde** |
| erro caro (contagem) | 4 | 1 | 41 | -3 | **ganha** |
| falha operacional | 0 | 57 | 0 |  |  |

Veredito: na métrica principal o LLM **perde** (-48 casos em n = 68; empate abaixo de 3); no erro caro o LLM **ganha** (1 × 4). Razão de custo LLM ÷ Jev: **29×** (US$ 7.4989 × 0.2548 por mil casos); razão de latência (p50): **7.2×** (2049 × 286 ms).

Leitura secundária **LLM tolerante (secundária)** (57 casos tolerados; violação só em Choice de folhas de grupo não vencedor (campo que a decisão não lê) → caso decidido; qualquer outra violação continua falha. Não é o critério: só mostra o julgamento que a regra estrita esconde): acertos 55/68 (0.809) × Jev 58/68 (-3 casos); erro caro 7 × Jev 4.

Concordância Jev × LLM: decisão final igual em **9/68** (0.132); por pergunta (Jev ≥ 0,5 × LLM true, Choice = mesma opção) 124/132 (0.939).

### Custo e latência (medidos na chamada real; do cache também)

| lado | requisições | novas (não cache) | respostas inválidas | tentativas HTTP | p50_ms | p95_ms | tokens entrada/caso | tokens saída/caso | US$ total | US$/1000 casos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev | 68 | 0 | 0 | — | 286 | 338 | 6067 | 0 | 0.0173 | 0.2548 | jev-1.13.0 |
| LLM | 68 | 0 | 57 | 0 | 2049 | 2286 | 6623 | 175 | 0.5099 | 7.4989 | claude-haiku-4-5-20251001 |

### Caso a caso

erro caro = grupo errado automatizado (inclui motivo inventado). Marcas: ✓ folha · ≈ aceitavel · ✓G so_grupo · ∅G absteve · ✗f folha_errada · ✗G grupo_errado · ✗I motivo_inventado · ? revisar · ✗F falha. Sinais do LLM: Choice do grupo › Choice de folhas desse grupo; S/n = os 3 Nouls reason_stated·blames_agency·closed_elsewhere.

| id | fam | gabarito | outras aceitáveis | Jev | LLM | LLM tol. | base | LLM: grupo › folha · reason·blames·closed | motivo LLM (estrita) |
|---|---|---|---|---|---|---|---|---|---|
| MP-T001 | sumiço depois de preço | preco/preco_acima_orcamento | sumiu_apos_valor | preco/preco_acima_orcamento ✓ | sem_informacao/∅ ✗F | preco/preco_acima_orcamento ✓ | preco/preco_acima_orcamento ✓ | preco › preco_acima_orcamento · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T002 | fácil / outros | localizacao/bairro_nao_desejado | — | localizacao/bairro_nao_desejado ✓ | sem_informacao/∅ ✗F | localizacao/bairro_nao_desejado ✓ | imovel/falta_item ✗G | localizacao › bairro_nao_desejado · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T003 | fronteira entre folhas | imovel/estado_conservacao | — | imovel/estado_conservacao ✓ | sem_informacao/∅ ✗F | imovel/estado_conservacao ✓ | imovel/estado_conservacao ✓ | imovel › estado_conservacao · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T004 | fechou em outro lugar | concorrencia/outra_imobiliaria | — | concorrencia/outra_imobiliaria ✓ | sem_informacao/∅ ✗F | concorrencia/direto_proprietario ✗f | imovel/estado_conservacao ✗G | concorrencia › direto_proprietario · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T005 | fácil / outros | credito_documentacao/restricao_cadastral | — | credito_documentacao/restricao_cadastral ✓ | sem_informacao/∅ ✗F | credito_documentacao/restricao_cadastral ✓ | sem_informacao/adiou_sem_motivo ✗G | credito_documentacao › restricao_cadastral · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T006 | fácil / outros | sem_informacao/sumiu_sem_resposta | — | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao/sumiu_sem_resposta ✓ | preco/preco_acima_orcamento ✗I | sem_informacao › sumiu_sem_resposta · n·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T007 | motivo do corretor | atendimento/demora_resposta | — | concorrencia/∅ ? | sem_informacao/∅ ✗F | concorrencia/∅ ? | imovel/diferente_do_anuncio ✗G | concorrencia › outra_imobiliaria · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T008 | motivo do corretor | atendimento/imovel_indisponivel | — | atendimento/imovel_indisponivel ✓ | sem_informacao/∅ ✗F | atendimento/imovel_indisponivel ✓ | credito_documentacao/financiamento_negado ✗G | atendimento › imovel_indisponivel · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T009 | fácil / outros | momento_cliente/desistiu_de_mudar | — | momento_cliente/desistiu_de_mudar ✓ | sem_informacao/∅ ✗F | momento_cliente/desistiu_de_mudar ✓ | preco/preco_acima_orcamento ✗G | momento_cliente › desistiu_de_mudar · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T010 | motivo real diferente do declarado | localizacao/distancia_deslocamento | bairro_nao_desejado | localizacao/distancia_deslocamento ✓ | sem_informacao/∅ ✗F | localizacao/distancia_deslocamento ✓ | imovel/tamanho_planta ✗G | localizacao › distancia_deslocamento · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T011 | dois motivos | localizacao/distancia_deslocamento | — | localizacao/distancia_deslocamento ✓ | sem_informacao/∅ ✗F | localizacao/distancia_deslocamento ✓ | preco/preco_acima_orcamento ✗G | localizacao › distancia_deslocamento · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T012 | motivo do corretor | atendimento/informacao_errada | falta_item | atendimento/informacao_errada ✓ | sem_informacao/∅ ✗F | atendimento/informacao_errada ✓ | preco/custos_extras ✗G | atendimento › informacao_errada · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T013 | fechou em outro lugar | concorrencia/direto_proprietario | — | concorrencia/direto_proprietario ✓ | sem_informacao/∅ ✗F | concorrencia/direto_proprietario ✓ | preco/negociacao_frustrada ✗G | concorrencia › direto_proprietario · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T014 | só o grupo é decidível | preco/∅ | preco_acima_orcamento custos_extras | preco/preco_acima_orcamento ≈ | sem_informacao/∅ ✗F | preco/preco_acima_orcamento ≈ | preco/preco_acima_orcamento ≈ | preco › preco_acima_orcamento · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T015 | fácil / outros | momento_cliente/desistiu_de_mudar | — | momento_cliente/desistiu_de_mudar ✓ | momento_cliente/desistiu_de_mudar ✓ | momento_cliente/desistiu_de_mudar ✓ | momento_cliente/desistiu_de_mudar ✓ | momento_cliente › desistiu_de_mudar · S·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T016 | sumiço sem pista | sem_informacao/sumiu_sem_resposta | — | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao/sumiu_sem_resposta ✓ | imovel/diferente_do_anuncio ✗I | sem_informacao › sumiu_sem_resposta · n·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T017 | fácil / outros | preco/condicao_pagamento | — | credito_documentacao/financiamento_negado ✗G | sem_informacao/∅ ✗F | preco/condicao_pagamento ✓ | preco/condicao_pagamento ✓ | preco › condicao_pagamento · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T018 | sumiço sem pista | sem_informacao/sumiu_sem_resposta | — | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao/sumiu_sem_resposta ✓ | imovel/estado_conservacao ✗I | sem_informacao › sumiu_sem_resposta · n·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T019 | motivo dito com educação | sem_informacao/adiou_sem_motivo | sumiu_sem_resposta | sem_informacao/adiou_sem_motivo ✓ | sem_informacao/adiou_sem_motivo ✓ | sem_informacao/adiou_sem_motivo ✓ | imovel/diferente_do_anuncio ✗I | sem_informacao › adiou_sem_motivo · n·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T020 | fácil / outros | sem_informacao/adiou_sem_motivo | — | sem_informacao/adiou_sem_motivo ✓ | sem_informacao/adiou_sem_motivo ✓ | sem_informacao/adiou_sem_motivo ✓ | sem_informacao/adiou_sem_motivo ✓ | sem_informacao › adiou_sem_motivo · n·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T021 | fronteira entre folhas | credito_documentacao/documentacao_imovel | — | credito_documentacao/documentacao_imovel ✓ | credito_documentacao/documentacao_imovel ✓ | credito_documentacao/documentacao_imovel ✓ | credito_documentacao/financiamento_negado ✗f | credito_documentacao › documentacao_imovel · S·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T022 | só o grupo é decidível | localizacao/∅ | — | localizacao/∅ ✓G | sem_informacao/∅ ✗F | localizacao/bairro_nao_desejado ✗f | atendimento/demora_resposta ✗G | localizacao › bairro_nao_desejado · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T023 | motivo do corretor | atendimento/demora_resposta | outra_imobiliaria | atendimento/demora_resposta ✓ | sem_informacao/∅ ✗F | atendimento/demora_resposta ✓ | imovel/falta_item ✗G | atendimento › demora_resposta · S·S·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T024 | só o grupo é decidível | atendimento/∅ | — | atendimento/∅ ? | sem_informacao/∅ ✗F | atendimento/pressao_insistencia ✗f | preco/condicao_pagamento ✗G | atendimento › pressao_insistencia · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T025 | fácil / outros | imovel/tamanho_planta | — | imovel/tamanho_planta ✓ | sem_informacao/∅ ✗F | imovel/tamanho_planta ✓ | imovel/diferente_do_anuncio ✗f | imovel › tamanho_planta · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T026 | fronteira entre folhas | credito_documentacao/garantia_locaticia | — | credito_documentacao/garantia_locaticia ✓ | sem_informacao/∅ ✗F | credito_documentacao/garantia_locaticia ✓ | preco/preco_acima_orcamento ✗G | credito_documentacao › garantia_locaticia · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T027 | fácil / outros | localizacao/entorno_seguranca | — | localizacao/entorno_seguranca ✓ | sem_informacao/∅ ✗F | localizacao/entorno_seguranca ✓ | imovel/estado_conservacao ✗G | localizacao › entorno_seguranca · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T028 | motivo do corretor | atendimento/demora_resposta | — | concorrencia/∅ ? | sem_informacao/∅ ✗F | concorrencia/direto_proprietario ✗G | credito_documentacao/financiamento_negado ✗G | concorrencia › direto_proprietario · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T029 | fácil / outros | atendimento/visita_falhou | — | atendimento/visita_falhou ✓ | sem_informacao/∅ ✗F | atendimento/visita_falhou ✓ | atendimento/visita_falhou ✓ | atendimento › visita_falhou · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T030 | fácil / outros | imovel/tamanho_planta | — | imovel/tamanho_planta ✓ | sem_informacao/∅ ✗F | imovel/tamanho_planta ✓ | imovel/tamanho_planta ✓ | imovel › tamanho_planta · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T031 | dois motivos | imovel/falta_item | — | imovel/falta_item ✓ | sem_informacao/∅ ✗F | imovel/falta_item ✓ | imovel/estado_conservacao ✗f | imovel › falta_item · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T032 | fácil / outros | credito_documentacao/garantia_locaticia | — | credito_documentacao/garantia_locaticia ✓ | sem_informacao/∅ ✗F | credito_documentacao/garantia_locaticia ✓ | credito_documentacao/garantia_locaticia ✓ | credito_documentacao › garantia_locaticia · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T033 | fronteira entre folhas | preco/custos_extras | — | preco/custos_extras ✓ | sem_informacao/∅ ✗F | preco/custos_extras ✓ | preco/custos_extras ✓ | preco › custos_extras · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T034 | fácil / outros | preco/custos_extras | — | preco/custos_extras ✓ | sem_informacao/∅ ✗F | preco/custos_extras ✓ | preco/preco_acima_orcamento ✗f | preco › custos_extras · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T035 | fácil / outros | localizacao/distancia_deslocamento | — | localizacao/distancia_deslocamento ✓ | sem_informacao/∅ ✗F | localizacao/distancia_deslocamento ✓ | localizacao/distancia_deslocamento ✓ | localizacao › distancia_deslocamento · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T036 | motivo real diferente do declarado | credito_documentacao/financiamento_negado | preco_acima_orcamento | credito_documentacao/financiamento_negado ✓ | sem_informacao/∅ ✗F | credito_documentacao/financiamento_negado ✓ | credito_documentacao/financiamento_negado ✓ | credito_documentacao › financiamento_negado · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T037 | decisor com motivo | imovel/falta_item | tamanho_planta | imovel/falta_item ✓ | sem_informacao/∅ ✗F | momento_cliente/decisor_vetou ✗G | credito_documentacao/documentacao_imovel ✗G | momento_cliente › decisor_vetou · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T038 | só o grupo é decidível | credito_documentacao/∅ | restricao_cadastral garantia_locaticia | credito_documentacao/∅ ✓G | sem_informacao/∅ ✗F | credito_documentacao/restricao_cadastral ≈ | sem_informacao/sumiu_apos_valor ✗G | credito_documentacao › restricao_cadastral · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T039 | motivo dito com educação | preco/preco_acima_orcamento | — | preco/preco_acima_orcamento ✓ | sem_informacao/adiou_sem_motivo ✗G | sem_informacao/adiou_sem_motivo ✗G | imovel/tamanho_planta ✗G | sem_informacao › adiou_sem_motivo · n·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T040 | fácil / outros | credito_documentacao/financiamento_negado | — | credito_documentacao/financiamento_negado ✓ | sem_informacao/∅ ✗F | credito_documentacao/financiamento_negado ✓ | credito_documentacao/restricao_cadastral ✗f | credito_documentacao › financiamento_negado · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T041 | só o grupo é decidível | concorrencia/∅ | — | concorrencia/∅ ✓G | sem_informacao/∅ ✗F | concorrencia/∅ ✓G | sem_informacao/adiou_sem_motivo ✗G | concorrencia › only_group · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T042 | só o grupo é decidível | imovel/∅ | — | imovel/∅ ✓G | sem_informacao/∅ ✗F | imovel/∅ ✓G | imovel/estado_conservacao ✗f | imovel › only_group · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T043 | só o grupo é decidível | concorrencia/∅ | — | concorrencia/∅ ✓G | sem_informacao/∅ ✗F | concorrencia/∅ ✓G | preco/preco_acima_orcamento ✗G | concorrencia › only_group · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T044 | fácil / outros | localizacao/entorno_seguranca | — | imovel/estado_conservacao ✗G | sem_informacao/∅ ✗F | imovel/estado_conservacao ✗G | localizacao/entorno_seguranca ✓ | imovel › estado_conservacao · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T045 | motivo real diferente do declarado | credito_documentacao/restricao_cadastral | — | credito_documentacao/restricao_cadastral ✓ | sem_informacao/∅ ✗F | credito_documentacao/restricao_cadastral ✓ | imovel/estado_conservacao ✗G | credito_documentacao › restricao_cadastral · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T046 | fácil / outros | credito_documentacao/documentacao_imovel | — | credito_documentacao/documentacao_imovel ✓ | sem_informacao/∅ ✗F | credito_documentacao/documentacao_imovel ✓ | credito_documentacao/documentacao_imovel ✓ | credito_documentacao › documentacao_imovel · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T047 | fácil / outros | momento_cliente/adiou_decisao | — | momento_cliente/adiou_decisao ✓ | sem_informacao/∅ ✗F | momento_cliente/adiou_decisao ✓ | localizacao/distancia_deslocamento ✗G | momento_cliente › adiou_decisao · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T048 | fechou em outro lugar | preco/custos_extras | outra_imobiliaria | concorrencia/outra_imobiliaria ≈ | sem_informacao/∅ ✗F | concorrencia/outra_imobiliaria ≈ | imovel/diferente_do_anuncio ✗G | concorrencia › outra_imobiliaria · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T049 | fácil / outros | atendimento/pressao_insistencia | — | atendimento/pressao_insistencia ✓ | sem_informacao/∅ ✗F | atendimento/pressao_insistencia ✓ | sem_informacao/sumiu_apos_valor ✗G | atendimento › pressao_insistencia · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T050 | fácil / outros | preco/preco_acima_orcamento | — | preco/preco_acima_orcamento ✓ | sem_informacao/∅ ✗F | preco/negociacao_frustrada ✗f | credito_documentacao/financiamento_negado ✗G | preco › negociacao_frustrada · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T051 | sumiço depois de preço | sem_informacao/sumiu_apos_valor | — | sem_informacao/sumiu_apos_valor ✓ | sem_informacao/sumiu_apos_valor ✓ | sem_informacao/sumiu_apos_valor ✓ | imovel/diferente_do_anuncio ✗I | sem_informacao › sumiu_apos_valor · n·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T052 | fácil / outros | momento_cliente/mudanca_de_vida | — | momento_cliente/mudanca_de_vida ✓ | sem_informacao/∅ ✗F | momento_cliente/mudanca_de_vida ✓ | momento_cliente/desistiu_de_mudar ✗f | momento_cliente › mudanca_de_vida · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T053 | motivo do corretor | atendimento/informacao_errada | imovel_indisponivel | atendimento/informacao_errada ✓ | sem_informacao/∅ ✗F | atendimento/informacao_errada ✓ | credito_documentacao/restricao_cadastral ✗G | atendimento › informacao_errada · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T054 | dois motivos | imovel/tamanho_planta | preco_acima_orcamento | imovel/tamanho_planta ✓ | sem_informacao/∅ ✗F | imovel/tamanho_planta ✓ | atendimento/informacao_errada ✗G | imovel › tamanho_planta · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T055 | fronteira entre folhas | atendimento/visita_falhou | — | atendimento/∅ ? | sem_informacao/∅ ✗F | atendimento/visita_falhou ✓ | atendimento/visita_falhou ✓ | atendimento › visita_falhou · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T056 | fácil / outros | concorrencia/direto_proprietario | — | concorrencia/direto_proprietario ✓ | sem_informacao/∅ ✗F | concorrencia/direto_proprietario ✓ | credito_documentacao/restricao_cadastral ✗G | concorrencia › direto_proprietario · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T057 | fácil / outros | imovel/estado_conservacao | — | imovel/estado_conservacao ✓ | sem_informacao/∅ ✗F | imovel/estado_conservacao ✓ | imovel/estado_conservacao ✓ | imovel › estado_conservacao · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T058 | fechou em outro lugar | concorrencia/outra_imobiliaria | — | concorrencia/outra_imobiliaria ✓ | sem_informacao/∅ ✗F | concorrencia/direto_proprietario ✗f | preco/negociacao_frustrada ✗G | concorrencia › direto_proprietario · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T059 | fechou em outro lugar | concorrencia/lancamento_construtora | condicao_pagamento | concorrencia/lancamento_construtora ✓ | sem_informacao/∅ ✗F | concorrencia/lancamento_construtora ✓ | preco/condicao_pagamento ≈ | concorrencia › lancamento_construtora · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T060 | sumiço depois de preço | sem_informacao/sumiu_apos_valor | — | sem_informacao/sumiu_sem_resposta ✗f | sem_informacao/sumiu_apos_valor ✓ | sem_informacao/sumiu_apos_valor ✓ | credito_documentacao/restricao_cadastral ✗I | sem_informacao › sumiu_apos_valor · n·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T061 | fácil / outros | atendimento/imovel_indisponivel | — | imovel/falta_item ✗G | sem_informacao/∅ ✗F | imovel/falta_item ✗G | atendimento/visita_falhou ✗f | imovel › falta_item · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T062 | fronteira entre folhas | preco/negociacao_frustrada | preco_acima_orcamento | preco/preco_acima_orcamento ≈ | sem_informacao/∅ ✗F | preco/negociacao_frustrada ✓ | localizacao/entorno_seguranca ✗G | preco › negociacao_frustrada · S·n·S | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T063 | motivo dito com educação | sem_informacao/adiou_sem_motivo | — | sem_informacao/adiou_sem_motivo ✓ | sem_informacao/adiou_sem_motivo ✓ | sem_informacao/adiou_sem_motivo ✓ | atendimento/demora_resposta ✗I | sem_informacao › adiou_sem_motivo · n·n·n | variante `c`: p(grupo) 1.00, p(folha) 1.00 |
| MP-T064 | fácil / outros | momento_cliente/adiou_decisao | — | momento_cliente/adiou_decisao ✓ | sem_informacao/∅ ✗F | momento_cliente/adiou_decisao ✓ | preco/preco_acima_orcamento ✗G | momento_cliente › adiou_decisao · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T065 | fácil / outros | momento_cliente/decisor_vetou | — | momento_cliente/∅ ? | sem_informacao/∅ ✗F | imovel/∅ ✗G | preco/preco_acima_orcamento ✗G | imovel › only_group · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T066 | dois motivos | momento_cliente/mudanca_de_vida | — | momento_cliente/mudanca_de_vida ✓ | sem_informacao/∅ ✗F | momento_cliente/mudanca_de_vida ✓ | sem_informacao/adiou_sem_motivo ✗G | momento_cliente › mudanca_de_vida · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T067 | fácil / outros | imovel/falta_item | — | imovel/falta_item ✓ | sem_informacao/∅ ✗F | imovel/falta_item ✓ | imovel/falta_item ✓ | imovel › falta_item · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-T068 | fronteira entre folhas | imovel/diferente_do_anuncio | falta_item | atendimento/informacao_errada ✗G | sem_informacao/∅ ✗F | atendimento/informacao_errada ✗G | imovel/diferente_do_anuncio ✓ | atendimento › informacao_errada · S·S·n | falha operacional: requisição `tudo` (RespostaInvalida) |

## `auditor-de-evidencia` — 73 casos do teste congelado

Métrica principal: **acerto da relação (revisa = erro)**. Erro caro: **falsa aprovação (gabarito não sustentado → supported)**. Baseline: palavra-chave + regex de falha (auditor.baseline).

### Métricas do próprio exemplo (funções do `run.py` dele), Jev × LLM × baseline nos mesmos casos

| lado | n | acerto (revisa=erro) | cobertura | acerto_decididos | revisa | FALSA APROVAÇÃO | falso alarme | apoio precisão | apoio recall | apoio exato |
|---|---|---|---|---|---|---|---|---|---|---|
| Jev | 73 | 0.795 | 0.836 | 0.951 | 12 | 1/48 | 1/25 | 0.824 | 0.875 | 55/73 |
| LLM | 73 | 0.685 | 1.000 | 0.685 | 0 | 15/48 | 2/25 | 0.663 | 0.859 | 45/73 |
| baseline | 73 | 0.425 | 1.000 | 0.425 | 0 | 26/48 | 1/25 | 0.407 | 0.547 | 18/73 |

### Veredito pelo critério congelado (gerado pelo script)

| o quê | Jev | LLM | baseline | LLM − Jev | o LLM |
|---|---|---|---|---|---|
| métrica principal (acertos) | 58/73 (0.795) | 50/73 (0.685) | 31/73 (0.425) | -8 casos | **perde** |
| erro caro (contagem) | 1 | 15 | 26 | +14 | **perde** |
| falha operacional | 0 | 0 | 0 |  |  |

Veredito: na métrica principal o LLM **perde** (-8 casos em n = 73; empate abaixo de 3); no erro caro o LLM **perde** (15 × 1). Razão de custo LLM ÷ Jev: **29×** (US$ 4.4561 × 0.1516 por mil casos); razão de latência (p50): **4.7×** (1344 × 287 ms).

Concordância Jev × LLM: decisão final igual em **45/73** (0.616); por pergunta (Jev ≥ 0,5 × LLM true, Choice = mesma opção) 555/661 (0.840).

### Custo e latência (medidos na chamada real; do cache também)

| lado | requisições | novas (não cache) | respostas inválidas | tentativas HTTP | p50_ms | p95_ms | tokens entrada/caso | tokens saída/caso | US$ total | US$/1000 casos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev | 73 | 0 | 0 | — | 287 | 387 | 3609 | 0 | 0.0111 | 0.1516 | jev-1.13.0 |
| LLM | 73 | 0 | 0 | 0 | 1344 | 1513 | 3954 | 101 | 0.3253 | 4.4561 | claude-haiku-4-5-20251001 |

### Caso a caso

erro caro = FALSA APROVAÇÃO (gabarito insufficient_evidence ou contradicted → supported). Sinais do LLM por registro: S = sustenta, C = contradiz, n = não; est = established; partes = object·state·place·scope.

| id | fam | gab | Jev | ok J | caro J | LLM | ok L | caro L | base | ok B | LLM: sup/con por registro · established · partes | motivo LLM |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AE-T001 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T002 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | n/C S/n · est n · partes SnSS | contradição 1.00 |
| AE-T003 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T004 | 1 | insufficient_evidence | insufficient_evidence | ✓ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T005 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T006 | 2 | insufficient_evidence | revisa | ✗ |  | contradicted | ✗ |  | supported | ✗ | n/C S/n · est n · partes SnSS | contradição 1.00 |
| AE-T007 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T008 | 3 | insufficient_evidence | insufficient_evidence | ✓ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T009 | 3 | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T010 | 4 | supported | revisa | ✗ |  | supported | ✓ |  | supported | ✓ | S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T011 | 4 | insufficient_evidence | revisa | ✗ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T012 | 4 | insufficient_evidence | revisa | ✗ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T013 | 6 | contradicted | contradicted | ✓ |  | insufficient_evidence | ✗ |  | supported | ✗ | S/n n/n · est n · partes SSnn | não provada (partes object 1.00 state 1.00 place 0.00 scope 0.00) |
| AE-T014 | 5 | insufficient_evidence | insufficient_evidence | ✓ |  | contradicted | ✗ |  | supported | ✗ | S/n n/C · est n · partes Snnn | contradição 1.00 |
| AE-T015 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T016 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | S/n n/C · est n · partes Snnn | contradição 1.00 |
| AE-T017 | 6 | insufficient_evidence | revisa | ✗ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | n/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T018 | 6 | supported | revisa | ✗ |  | supported | ✓ |  | supported | ✓ | S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T019 | difícil: | insufficient_evidence | insufficient_evidence | ✓ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | n/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T020 | 11 | insufficient_evidence | revisa | ✗ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T021 | fácil | supported | revisa | ✗ |  | supported | ✓ |  | insufficient_evidence | ✗ | S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T022 | 7 | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | insufficient_evidence | ✗ | S/n n/C · est n · partes Snnn | contradição 1.00 |
| AE-T023 | difícil: | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | S/n n/n n/C · est n · partes SnSn | contradição 1.00 |
| AE-T024 | 1 | supported | contradicted | ✗ |  | contradicted | ✗ |  | contradicted | ✗ | S/C n/n S/n · est S · partes SSSS | contradição 1.00 |
| AE-T025 | 9 | insufficient_evidence | insufficient_evidence | ✓ |  | insufficient_evidence | ✓ |  | contradicted | ✗ | n/n S/n · est n · partes SSnS | não provada (partes object 1.00 state 1.00 place 0.00 scope 1.00) |
| AE-T026 | 5 | insufficient_evidence | insufficient_evidence | ✓ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T027 | 10 | insufficient_evidence | revisa | ✗ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T028 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T029 | 10 | insufficient_evidence | insufficient_evidence | ✓ |  | supported | ✗ | FALSA APROVAÇÃO | insufficient_evidence | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T030 | 10 | supported | supported | ✓ |  | supported | ✓ |  | insufficient_evidence | ✗ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T031 | 11 | insufficient_evidence | insufficient_evidence | ✓ |  | supported | ✗ | FALSA APROVAÇÃO | insufficient_evidence | ✓ | S/n n/n · est n · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T032 | fácil | supported | revisa | ✗ |  | supported | ✓ |  | insufficient_evidence | ✗ | n/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T033 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | n/C n/n · est n · partes SnnS | contradição 1.00 |
| AE-T034 | 12a | supported | supported | ✓ |  | contradicted | ✗ |  | insufficient_evidence | ✗ | S/C n/n · est n · partes SnSn | contradição 1.00 |
| AE-T035 | 12a | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | insufficient_evidence | ✗ | S/C n/n · est n · partes SnSn | contradição 1.00 |
| AE-T036 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | n/C n/n · est n · partes SnSn | contradição 1.00 |
| AE-T037 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | insufficient_evidence | ✗ | n/C S/n · est n · partes SnSn | código: e1 coverage lines 84.6% não satisfaz lines > 85% |
| AE-T038 | fácil | supported | supported | ✓ |  | supported | ✓ |  | insufficient_evidence | ✗ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T039 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | insufficient_evidence | ✗ | n/C S/n · est n · partes SnSn | código: e1 coverage statements 80.0% não satisfaz statements > 80% |
| AE-T040 | 9 | insufficient_evidence | insufficient_evidence | ✓ |  | insufficient_evidence | ✓ |  | contradicted | ✗ | S/n n/n · est n · partes SSnS | não provada (partes object 1.00 state 1.00 place 0.00 scope 1.00) |
| AE-T041 | 13 | insufficient_evidence | insufficient_evidence | ✓ |  | insufficient_evidence | ✓ |  | insufficient_evidence | ✓ | n/n S/n · est n · partes nSSS | não provada (partes object 0.00 state 1.00 place 1.00 scope 1.00) |
| AE-T042 | 13 | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | S/n n/C · est n · partes SnnS | contradição 1.00 |
| AE-T043 | 13 | supported | insufficient_evidence | ✗ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T044 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | supported | ✗ | n/C S/n · est n · partes SnnS | contradição 1.00 |
| AE-T045 | 2 | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | n/C S/n · est n · partes SnSS | contradição 1.00 |
| AE-T046 | 12b | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | supported | ✗ | n/C S/n · est n · partes SnnS | código: e1 version 1.9.2 não satisfaz 1.9.3 |
| AE-T047 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T048 | 10 | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T049 | difícil: | insufficient_evidence | insufficient_evidence | ✓ |  | contradicted | ✗ |  | contradicted | ✗ | n/C n/n · est n · partes SnSn | contradição 1.00 |
| AE-T050 | 10 | insufficient_evidence | insufficient_evidence | ✓ |  | contradicted | ✗ |  | supported | ✗ | S/C n/n · est n · partes SnSn | contradição 1.00 |
| AE-T051 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | supported | ✗ | n/C n/n · est n · partes SnSn | código: e1 latency 412 ms não satisfaz ms < 300 ms |
| AE-T052 | fácil | supported | revisa | ✗ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T053 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T054 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | supported | ✗ | S/C n/n · est n · partes SSSn | código: e1 replicas 1/1 não satisfaz 3 replicas running |
| AE-T055 | 14 | insufficient_evidence | insufficient_evidence | ✓ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T056 | 14 | insufficient_evidence | insufficient_evidence | ✓ |  | insufficient_evidence | ✓ |  | supported | ✗ | S/n n/n · est n · partes SnSS | não provada (partes object 1.00 state 0.00 place 1.00 scope 1.00) |
| AE-T057 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | n/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T058 | 8 | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | supported | ✗ | n/n S/C · est n · partes SnSS | contradição 1.00 |
| AE-T059 | fácil | supported | supported | ✓ |  | supported | ✓ |  | insufficient_evidence | ✗ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T060 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | n/C n/n · est n · partes SnSS | contradição 1.00 |
| AE-T061 | 10 | insufficient_evidence | insufficient_evidence | ✓ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T062 | 9 | insufficient_evidence | insufficient_evidence | ✓ |  | contradicted | ✗ |  | contradicted | ✗ | n/C n/n · est n · partes SSnS | contradição 1.00 |
| AE-T063 | difícil: | insufficient_evidence | revisa | ✗ |  | insufficient_evidence | ✓ |  | supported | ✗ | S/n n/n · est n · partes SSnS | não provada (partes object 1.00 state 1.00 place 0.00 scope 1.00) |
| AE-T064 | difícil: | insufficient_evidence | insufficient_evidence | ✓ |  | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | n/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T065 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T066 | fácil | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | n/C n/n · est n · partes SnSS | contradição 1.00 |
| AE-T067 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T068 | difícil: | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | contradicted | ✓ | S/C S/n · est n · partes SnSn | contradição 1.00 |
| AE-T069 | difícil: | insufficient_evidence | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | FALSA APROVAÇÃO | supported | ✗ | S/n S/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
| AE-T070 | 6 | contradicted | contradicted | ✓ |  | contradicted | ✓ |  | supported | ✗ | S/n n/C · est n · partes SSnS | contradição 1.00 |
| AE-T071 | 5 | insufficient_evidence | insufficient_evidence | ✓ |  | insufficient_evidence | ✓ |  | contradicted | ✗ | S/n n/n · est n · partes SSnS | não provada (partes object 1.00 state 1.00 place 0.00 scope 1.00) |
| AE-T072 | difícil: | insufficient_evidence | insufficient_evidence | ✓ |  | insufficient_evidence | ✓ |  | supported | ✗ | n/n n/n · est n · partes SnSn | não provada (partes object 1.00 state 0.00 place 1.00 scope 0.00) |
| AE-T073 | fácil | supported | supported | ✓ |  | supported | ✓ |  | supported | ✓ | S/n n/n · est S · partes SSSS | provada (partes object 1.00 state 1.00 place 1.00 scope 1.00) |
