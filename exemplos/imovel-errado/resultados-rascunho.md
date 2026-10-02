# Rascunho — imovel-errado (encanamento)

## Conjunto `rascunho` — 5 conversas (arquivo versão 2026-10-01, autor fable); 0 com referente nulo, 0 difíceis

> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**

### Ação — métrica principal, baseline × sempre pergunta × Jev nos mesmos casos

Gabarito da ação: referente nulo → `pedir_esclarecimento`; `rascunho_usa_outro` → `trocar_referente`; senão `manter`. **Erro caro** = rascunho que usa fato de outro imóvel e recebeu `manter` (a resposta errada iria ao cliente). `troca p/ candidato errado` = trocou sugerindo outro que não o referente do gabarito. `sugeriu candidato c/ gabarito nulo` = o gabarito exige esclarecimento e a saída foi `manter`/`trocar_referente` (assumiu um imóvel que o cliente não identificou; achado 4 da revisão). **RESPOSTA ERRADA (soma)** = os três somados, sobre n: é o critério 1. `sempre pergunta` = o custo de evitar todo erro: zero resposta errada, 100% das conversas interrompidas. `acerto_referente` compara o referente decidido (nulo = pediu) com o gabarito, nulo incluído.

| variante | n | acerto_acao | ERRO CARO (usa outro → manter) | troca p/ candidato errado | sugeriu candidato c/ gabarito nulo | RESPOSTA ERRADA (soma) | pediu sem necessidade | trocou sem necessidade | nulo → pedir | acerto_referente (c/ nulo) |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (último citado) | 5 | 0.800 | 1/1 | 0/5 | 0/0 | 1/5 | 0/5 | 0/4 | 0/0 | 1.000 |
| sempre pergunta | 5 | 0.000 | 0/1 | 0/5 | 0/0 | 0/5 | 5/5 | 0/4 | 0/0 | 0.000 |
| Jev | 5 | 1.000 | 0/1 | 0/5 | 0/0 | 0/5 | 0/5 | 0/4 | 0/0 | 1.000 |

**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | manter | trocar_referente | pedir_esclarecimento |
|---|---|---|---|
| manter | 4 | 0 | 0 |
| trocar_referente | 0 | 1 | 0 |
| pedir_esclarecimento | 0 | 0 | 0 |

**Matriz de confusão — baseline**

| gabarito ↓ / previsto → | manter | trocar_referente | pedir_esclarecimento |
|---|---|---|---|
| manter | 4 | 0 | 0 |
| trocar_referente | 1 | 0 | 0 |
| pedir_esclarecimento | 0 | 0 | 0 |

### Referente — Choice crua (vencedor; válvula = nulo), antes dos portões

| acerto Jev (c/ nulo) | acerto Jev (só não nulos) | acerto baseline (c/ nulo) | nulo → válvula | não nulo → válvula (perda) | piso atual |
|---|---|---|---|---|---|
| 1.000 | 1.000 | 1.000 | 0/0 | 0/5 | 0.500 |

**Cobertura × erro por confiança da Choice** (todos os casos; `erro` = vencedor ≠ gabarito, nulo incluído)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 5 |
| 0.300 | 1.000 | 0.000 | 5 |
| 0.500 | 1.000 | 0.000 | 5 |
| 0.700 | 1.000 | 0.000 | 5 |
| 0.900 | 1.000 | 0.000 | 5 |

### Nouls — acerto (≥ 0,5) no subconjunto que cada um decide, faixa atual e Brier

| noul | subconjunto | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| unambiguous_reference | todos (gabarito = referente não nulo) | 1.000 | 0.3–0.3 | 1.000 | 1.000 | 0 | 5 | 0.001 |
| draft_uses_other | referente não nulo | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 | 0.006 |
| draft_commits_to_one | referente nulo | nan | 0.3–0.7 | nan | nan | 0 | 0 | nan |

**`rascunho_usa_outro` composto** (relacional se o referente foi decidido, senão "se compromete com um"; ≥ 0,5): Jev 1.000 · baseline por palavra-chave 0.800 (n = 5)

### Por família difícil (pela `nota` do rotulador)

| família | n | referente Jev | referente baseline | ação Jev | ação baseline | erros caros Jev |
|---|---|---|---|---|---|---|
| fácil / outros | 5 | 1.000 | 1.000 | 1.000 | 0.800 | 0 |

### Cobertura automática × erro por piso da Choice e faixa dos Nouls (mesmas respostas; informativo no teste)

| piso_choice | faixa_nouls | atual | cobertura_auto | erro_automatico | erros_caros | n_auto |
|---|---|---|---|---|---|---|
| 0.000 | 0.5–0.5 |  | 1.000 | 0.000 | 0 | 5 |
| 0.000 | 0.3–0.7 |  | 1.000 | 0.000 | 0 | 5 |
| 0.000 | 0.2–0.8 |  | 1.000 | 0.000 | 0 | 5 |
| 0.500 | 0.5–0.5 |  | 1.000 | 0.000 | 0 | 5 |
| 0.500 | 0.3–0.7 | ← | 1.000 | 0.000 | 0 | 5 |
| 0.500 | 0.2–0.8 |  | 1.000 | 0.000 | 0 | 5 |
| 0.700 | 0.5–0.5 |  | 1.000 | 0.000 | 0 | 5 |
| 0.700 | 0.3–0.7 |  | 1.000 | 0.000 | 0 | 5 |
| 0.700 | 0.2–0.8 |  | 1.000 | 0.000 | 0 | 5 |
| 0.900 | 0.5–0.5 |  | 1.000 | 0.000 | 0 | 5 |
| 0.900 | 0.3–0.7 |  | 1.000 | 0.000 | 0 | 5 |
| 0.900 | 0.2–0.8 |  | 1.000 | 0.000 | 0 | 5 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | conversas_longas (sem chamada) | perguntas | p50_ms | p95_ms | tokens_por_conversa | US$_total | US$_por_1000_conversas | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 5 | 0 | 20 | 325 | 348 | 1653 | 0.000347 | 0.0694 | jev-1.13.0 |

### Caso a caso

`ref` = vencedor da Choice (confiança); `unamb`/`usa`/`comp` = Nouls `unambiguous_reference`, `draft_uses_other`, `draft_commits_to_one`; `ok` compara a ação do Jev com o gabarito; `base` = ação do baseline.

| id | fam | gab ref | usa_outro | ref | unamb | usa | comp | ação Jev | gab ação | ok | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IE-R001 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.97 | 0.02 | 0.97 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-R002 | fácil / outros | IM-02 | True | IM-02 (1.00) | 0.96 | 0.84 | 0.39 | trocar_referente | trocar_referente | ✓ | manter (IM-02) | rascunho usa fato de outro candidato |
| IE-R003 | fácil / outros | IM-02 | False | IM-02 (1.00) | 0.96 | 0.05 | 0.97 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-R004 | fácil / outros | IM-02 | False | IM-02 (1.00) | 0.97 | 0.03 | 0.98 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-R005 | fácil / outros | IM-03 | False | IM-03 (1.00) | 0.97 | 0.03 | 0.97 | manter | manter | ✓ | manter (IM-03) | rascunho sobre o referente |
