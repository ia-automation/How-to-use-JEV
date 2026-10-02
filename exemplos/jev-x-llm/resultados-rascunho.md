# Rascunho — jev-x-llm (encanamento; não é métrica)

Gerado por `run.py` em 2026-10-01 (modo LLM `gravado`; Jev sempre `gravado`, 0 chamadas). LLM: `claude-haiku-4-5-20251001`, temperatura 0.0, max_tokens 400, uma chamada por caso em série, 2 retries; preço US$ 1.00/M entrada e US$ 5.00/M saída (tabela pública da Anthropic, consultada em 2026-10-01). Jev: `jev-1.13.0`, US$ 0,042/M entrada, latência da rodada original (8 em paralelo). Prompt = state + perguntas de `perguntas.py` do exemplo, serializados em JSON, mais o texto fixo `comparar.SISTEMA`; resposta validada por `llmcache.validar_resposta` (fora do esquema = falha operacional, contada à parte, nunca gravada como resposta); decisão pela regra do próprio exemplo (`comparar.py`).

Critério (fixado antes da primeira chamada): **fixado_em**: 2026-10-01, antes da primeira chamada ao LLM; **lado_a_lado**: mesmo teste congelado (hash do manifesto de cada exemplo conferido), mesmas instructions/criteria/opções de perguntas.py serializadas em JSON, mesma validação estrita, mesma regra de decisão do módulo do exemplo (respostas do LLM injetadas no lugar das do Jev: Noul true/false → 1,0/0,0; Choice → one-hot), mesmo baseline; **metrica_principal**: LLM ganha se acerta ≥ 3 casos a mais que o Jev; perde se ≥ 3 a menos; senão empata. Falha operacional do LLM conta como erro (como `revisar`) e é reportada à parte; **erro_caro**: contagem absoluta: LLM ganha se tem MENOS erros caros que o Jev, perde se tem MAIS, empata se igual (erro caro é raro: cada caso conta); **custo_latencia**: razão = US$ por mil casos do LLM ÷ do Jev (tokens de entrada + saída ao preço publicado, input US$ 1,00/M e output US$ 5,00/M em 2026-10-01; Jev US$ 0,042/M só entrada); latência = p50 do LLM ÷ p50 do Jev, as duas medidas na chamada real (Jev com 8 em paralelo na rodada original; LLM em série); **concordancia**: fração dos casos em que a decisão final do Jev e a do LLM são iguais (ação+tipo / grupo+folha+revisar / relação); informativa, não decide; **o_que_nao_conclui**: um fornecedor, um modelo barato (Haiku 4.5), uma rodada, temperatura 0, prompt sem exemplos e sem raciocínio pedido; dados sintéticos do mesmo fornecedor do LLM. Nada aqui mede o topo da linha nem o que um prompt afinado faria.

Versão NÃO congelada (rascunho): `comparar.py` sha256 8e3d2ec9e2cc3199… · `criterio.py` sha256 ae51b3a8cde4c604… · `run.py` sha256 a285e87000b8f889… · `../_comum/llmcache.py` sha256 8f025cc9d147da23… · `../opt-out-lgpd/perguntas.py` sha256 a494a14de522a0d1… · `../opt-out-lgpd/optout.py` sha256 50f780a69cd3c413… · `../opt-out-lgpd/run.py` sha256 f8ef07f6e3a22368… · `../opt-out-lgpd/dados/teste.json` sha256 1207d0b7d4d14d6a… · `../motivo-de-perda/perguntas.py` sha256 8b2914532a561610… · `../motivo-de-perda/motivo.py` sha256 44151a7e23ba2ec4… · `../motivo-de-perda/run.py` sha256 625005edb785efe1… · `../motivo-de-perda/dados/teste.json` sha256 015a04e1f083ddb7… · `../auditor-de-evidencia/perguntas.py` sha256 bc1f1307eaabb826… · `../auditor-de-evidencia/auditor.py` sha256 47832e24fe065ea4… · `../auditor-de-evidencia/run.py` sha256 15865525a2d7cbbb… · `../auditor-de-evidencia/dados/teste.json` sha256 6bdb935ba4030be2… · `../motivo-de-perda/dados/taxonomia.json` sha256 7ab1ad5faeeedc80…

> 2 casos do rascunho de cada exemplo, só para provar o encanamento (prompt, validação, injeção, métricas). **Não é métrica.**

## `motivo-de-perda` — 2 casos do teste congelado

Métrica principal: **acerto folgado (folha ∈ aceitáveis ou só-grupo certo; revisão e falha = erro), variante c**. Erro caro: **motivo inventado + grupo errado automatizado (contados juntos, como no exemplo)**. Baseline: palavra-chave por folha (motivo.baseline).

### Métricas do próprio exemplo (funções do `run.py` dele), Jev × LLM × baseline nos mesmos casos

| lado | n | acerto estrito | acerto folgado | grupo certo | motivo INVENTADO | grupo errado auto. | só-grupo certo | sem_info certo | absteve | folha errada | revisar | falha |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev | 2 | 1.000 | 1.000 | 1.000 | 0/0 | 0/2 | 0/0 | 0/0 | 0/2 | 0/2 | 0/2 | 0/2 |
| LLM | 2 | 0.000 | 0.000 | 0.000 | 0/0 | 0/2 | 0/0 | 0/0 | 0/2 | 0/2 | 0/2 | 2/2 |
| LLM tolerante (secundária) | 2 | 1.000 | 1.000 | 1.000 | 0/0 | 0/2 | 0/0 | 0/0 | 0/2 | 0/2 | 0/2 | 0/2 |
| baseline | 2 | 0.500 | 0.500 | 0.500 | 0/0 | 1/2 | 0/0 | 0/0 | 0/2 | 0/2 | 0/2 | 0/2 |

### Veredito pelo critério congelado (gerado pelo script)

| o quê | Jev | LLM | baseline | LLM − Jev | o LLM |
|---|---|---|---|---|---|
| métrica principal (acertos) | 2/2 (1.000) | 0/2 (0.000) | 1/2 (0.500) | -2 casos | **empata** |
| erro caro (contagem) | 0 | 0 | 1 | +0 | **empata** |
| falha operacional | 0 | 2 | 0 |  |  |

Veredito: na métrica principal o LLM **empata** (-2 casos em n = 2; empate abaixo de 3); no erro caro o LLM **empata** (0 × 0). Razão de custo LLM ÷ Jev: **30×** (US$ 7.4605 × 0.2528 por mil casos); razão de latência (p50): **6.6×** (2008 × 306 ms).

Leitura secundária **LLM tolerante (secundária)** (2 casos tolerados; violação só em Choice de folhas de grupo não vencedor (campo que a decisão não lê) → caso decidido; qualquer outra violação continua falha. Não é o critério: só mostra o julgamento que a regra estrita esconde): acertos 2/2 (1.000) × Jev 2/2 (+0 casos); erro caro 0 × Jev 0.

Concordância Jev × LLM: decisão final igual em **0/2** (0.000); por pergunta (Jev ≥ 0,5 × LLM true, Choice = mesma opção) 0/0 (nan).

### Custo e latência (medidos na chamada real; do cache também)

| lado | requisições | novas (não cache) | respostas inválidas | tentativas HTTP | p50_ms | p95_ms | tokens entrada/caso | tokens saída/caso | US$ total | US$/1000 casos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev | 2 | 0 | 0 | — | 306 | 345 | 6018 | 0 | 0.0005 | 0.2528 | jev-1.13.0 |
| LLM | 2 | 0 | 2 | 0 | 2008 | 2198 | 6568 | 178 | 0.0149 | 7.4605 | claude-haiku-4-5-20251001 |

### Caso a caso

erro caro = grupo errado automatizado (inclui motivo inventado). Marcas: ✓ folha · ≈ aceitavel · ✓G so_grupo · ∅G absteve · ✗f folha_errada · ✗G grupo_errado · ✗I motivo_inventado · ? revisar · ✗F falha. Sinais do LLM: Choice do grupo › Choice de folhas desse grupo; S/n = os 3 Nouls reason_stated·blames_agency·closed_elsewhere.

| id | fam | gabarito | outras aceitáveis | Jev | LLM | LLM tol. | base | LLM: grupo › folha · reason·blames·closed | motivo LLM (estrita) |
|---|---|---|---|---|---|---|---|---|---|
| MP-R001 | fácil / outros | preco/preco_acima_orcamento | — | preco/preco_acima_orcamento ✓ | sem_informacao/∅ ✗F | preco/preco_acima_orcamento ✓ | localizacao/bairro_nao_desejado ✗G | preco › preco_acima_orcamento · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
| MP-R002 | fácil / outros | credito_documentacao/financiamento_negado | — | credito_documentacao/financiamento_negado ✓ | sem_informacao/∅ ✗F | credito_documentacao/financiamento_negado ✓ | credito_documentacao/financiamento_negado ✓ | credito_documentacao › financiamento_negado · S·n·n | falha operacional: requisição `tudo` (RespostaInvalida) |
