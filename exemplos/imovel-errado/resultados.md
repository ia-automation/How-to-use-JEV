# Resultados — imovel-errado

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; comparativos, validação e ação: `referente.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Teto da conversa: 12 turnos / 3000 caracteres (acima → pedir, sem chamada).

Critério de continuar/descartar (fixado antes do teste): no teste (48 conversas), com a política acima: (1) erro caro (rascunho de outro imóvel → manter) + troca sugerindo candidato errado + sugeriu candidato com gabarito nulo ≤ 1/48 (2,1%); (2) acerto do referente nulo incluído, ≥ baseline + 0,15. Secundário: nulos → pedir ≥ 6/8; pediu sem necessidade ≤ 10% dos não nulos.

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T12:34:25-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 61af98a2c1f26b2c… · `referente.py` sha256 e3ad2c924efdccd4… · `run.py` sha256 efca1f2be577aa21… · `dados/teste.json` sha256 2c07ffb6e6e37c45…

## Lado a lado

### Ação por variante e conjunto

| conjunto | variante | n | acerto_acao | ERRO CARO (usa outro → manter) | troca p/ candidato errado | sugeriu candidato c/ gabarito nulo | RESPOSTA ERRADA (soma) | pediu sem necessidade | trocou sem necessidade | nulo → pedir | acerto_referente (c/ nulo) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | baseline (último citado) | 24 | 0.500 | 3/10 | 2/20 | 1/4 | 6/24 | 6/20 | 2/13 | 3/4 | 0.500 |
| ajuste | sempre pergunta | 24 | 0.167 | 0/10 | 0/20 | 0/4 | 0/24 | 20/20 | 0/13 | 4/4 | 0.000 |
| ajuste | Jev | 24 | 1.000 | 0/10 | 0/20 | 0/4 | 0/24 | 0/20 | 0/13 | 4/4 | 1.000 |
| teste | baseline (último citado) | 48 | 0.542 | 8/19 | 2/40 | 3/8 | 13/48 | 9/40 | 3/25 | 5/8 | 0.700 |
| teste | sempre pergunta | 48 | 0.167 | 0/19 | 0/40 | 0/8 | 0/48 | 40/40 | 0/25 | 8/8 | 0.000 |
| teste | Jev | 48 | 0.958 | 0/19 | 0/40 | 0/8 | 0/48 | 0/40 | 2/25 | 8/8 | 1.000 |

### Referente, rascunho, custo

| conjunto | n | nulos | difíceis | referente Jev (c/ nulo) | referente Jev (não nulos) | referente baseline | nulo→válvula | usa_outro Jev | usa_outro baseline | p50_ms | p95_ms | tokens_por_conversa | US$_por_1000 | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | 24 | 4 | 18 | 1.000 | 1.000 | 0.500 | 4/4 | 1.000 | 0.458 | 302 | 378 | 1656 | 0.0695 | jev-1.13.0 |
| teste | 48 | 8 | 33 | 1.000 | 1.000 | 0.700 | 8/8 | 0.958 | 0.562 | 264 | 346 | 1634 | 0.0686 | jev-1.13.0 |

## Conjunto `ajuste` — 24 conversas (arquivo versão 2026-10-01, autor fable); 4 com referente nulo, 18 difíceis

### Ação — métrica principal, baseline × sempre pergunta × Jev nos mesmos casos

Gabarito da ação: referente nulo → `pedir_esclarecimento`; `rascunho_usa_outro` → `trocar_referente`; senão `manter`. **Erro caro** = rascunho que usa fato de outro imóvel e recebeu `manter` (a resposta errada iria ao cliente). `troca p/ candidato errado` = trocou sugerindo outro que não o referente do gabarito. `sugeriu candidato c/ gabarito nulo` = o gabarito exige esclarecimento e a saída foi `manter`/`trocar_referente` (assumiu um imóvel que o cliente não identificou; achado 4 da revisão). **RESPOSTA ERRADA (soma)** = os três somados, sobre n: é o critério 1. `sempre pergunta` = o custo de evitar todo erro: zero resposta errada, 100% das conversas interrompidas. `acerto_referente` compara o referente decidido (nulo = pediu) com o gabarito, nulo incluído.

| variante | n | acerto_acao | ERRO CARO (usa outro → manter) | troca p/ candidato errado | sugeriu candidato c/ gabarito nulo | RESPOSTA ERRADA (soma) | pediu sem necessidade | trocou sem necessidade | nulo → pedir | acerto_referente (c/ nulo) |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (último citado) | 24 | 0.500 | 3/10 | 2/20 | 1/4 | 6/24 | 6/20 | 2/13 | 3/4 | 0.500 |
| sempre pergunta | 24 | 0.167 | 0/10 | 0/20 | 0/4 | 0/24 | 20/20 | 0/13 | 4/4 | 0.000 |
| Jev | 24 | 1.000 | 0/10 | 0/20 | 0/4 | 0/24 | 0/20 | 0/13 | 4/4 | 1.000 |

**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | manter | trocar_referente | pedir_esclarecimento |
|---|---|---|---|
| manter | 13 | 0 | 0 |
| trocar_referente | 0 | 7 | 0 |
| pedir_esclarecimento | 0 | 0 | 4 |

**Matriz de confusão — baseline**

| gabarito ↓ / previsto → | manter | trocar_referente | pedir_esclarecimento |
|---|---|---|---|
| manter | 5 | 2 | 6 |
| trocar_referente | 3 | 4 | 0 |
| pedir_esclarecimento | 0 | 1 | 3 |

### Referente — Choice crua (vencedor; válvula = nulo), antes dos portões

| acerto Jev (c/ nulo) | acerto Jev (só não nulos) | acerto baseline (c/ nulo) | nulo → válvula | não nulo → válvula (perda) | piso atual |
|---|---|---|---|---|---|
| 1.000 | 1.000 | 0.500 | 4/4 | 0/20 | 0.500 |

**Cobertura × erro por confiança da Choice** (todos os casos; `erro` = vencedor ≠ gabarito, nulo incluído)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 24 |
| 0.300 | 1.000 | 0.000 | 24 |
| 0.500 | 1.000 | 0.000 | 24 |
| 0.700 | 1.000 | 0.000 | 24 |
| 0.900 | 0.875 | 0.000 | 21 |

### Nouls — acerto (≥ 0,5) no subconjunto que cada um decide, faixa atual e Brier

| noul | subconjunto | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| unambiguous_reference | todos (gabarito = referente não nulo) | 1.000 | 0.3–0.3 | 1.000 | 1.000 | 0 | 24 | 0.007 |
| draft_uses_other | referente não nulo | 1.000 | 0.3–0.7 | 0.950 | 1.000 | 1 | 20 | 0.012 |
| draft_commits_to_one | referente nulo | 1.000 | 0.3–0.7 | 0.750 | 1.000 | 1 | 4 | 0.041 |

**`rascunho_usa_outro` composto** (relacional se o referente foi decidido, senão "se compromete com um"; ≥ 0,5): Jev 1.000 · baseline por palavra-chave 0.458 (n = 24)

### Por família difícil (pela `nota` do rotulador)

| família | n | referente Jev | referente baseline | ação Jev | ação baseline | erros caros Jev |
|---|---|---|---|---|---|---|
| troca de foco no meio | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0 |
| citação de fala antiga | 2 | 1.000 | 0.500 | 1.000 | 0.500 | 0 |
| dois imóveis parecidos | 3 | 1.000 | 0.667 | 1.000 | 0.333 | 0 |
| referência vaga | 2 | 1.000 | 0.000 | 1.000 | 0.000 | 0 |
| correção do cliente | 2 | 1.000 | 0.500 | 1.000 | 0.500 | 0 |
| atributo que só um tem | 3 | 1.000 | 0.000 | 1.000 | 0.333 | 0 |
| atributo que dois têm (null) | 3 | nan | nan | 1.000 | 0.667 | 0 |
| difícil: outra | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 0 |
| outro nulo (fora da lista / geral) | 1 | nan | nan | 1.000 | 1.000 | 0 |
| fácil / outros | 5 | 1.000 | 0.600 | 1.000 | 0.400 | 0 |

### Cobertura automática × erro por piso da Choice e faixa dos Nouls (mesmas respostas; informativo no teste)

| piso_choice | faixa_nouls | atual | cobertura_auto | erro_automatico | erros_caros | n_auto |
|---|---|---|---|---|---|---|
| 0.000 | 0.5–0.5 |  | 0.833 | 0.000 | 0 | 20 |
| 0.000 | 0.3–0.7 |  | 0.833 | 0.000 | 0 | 20 |
| 0.000 | 0.2–0.8 |  | 0.833 | 0.000 | 0 | 20 |
| 0.500 | 0.5–0.5 |  | 0.833 | 0.000 | 0 | 20 |
| 0.500 | 0.3–0.7 | ← | 0.833 | 0.000 | 0 | 20 |
| 0.500 | 0.2–0.8 |  | 0.833 | 0.000 | 0 | 20 |
| 0.700 | 0.5–0.5 |  | 0.833 | 0.000 | 0 | 20 |
| 0.700 | 0.3–0.7 |  | 0.833 | 0.000 | 0 | 20 |
| 0.700 | 0.2–0.8 |  | 0.833 | 0.000 | 0 | 20 |
| 0.900 | 0.5–0.5 |  | 0.833 | 0.000 | 0 | 20 |
| 0.900 | 0.3–0.7 |  | 0.833 | 0.000 | 0 | 20 |
| 0.900 | 0.2–0.8 |  | 0.833 | 0.000 | 0 | 20 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | conversas_longas (sem chamada) | perguntas | p50_ms | p95_ms | tokens_por_conversa | US$_total | US$_por_1000_conversas | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 24 | 0 | 0 | 96 | 302 | 378 | 1656 | 0.001669 | 0.0695 | jev-1.13.0 |

### Caso a caso

`ref` = vencedor da Choice (confiança); `unamb`/`usa`/`comp` = Nouls `unambiguous_reference`, `draft_uses_other`, `draft_commits_to_one`; `ok` compara a ação do Jev com o gabarito; `base` = ação do baseline.

| id | fam | gab ref | usa_outro | ref | unamb | usa | comp | ação Jev | gab ação | ok | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IE-A001 | troca de foco no meio | IM-02 | True | IM-02 (1.00) | 0.93 | 0.79 | 0.64 | trocar_referente | trocar_referente | ✓ | trocar_referente (IM-02) | rascunho usa fato de outro candidato |
| IE-A002 | citação de fala antiga | IM-01 | False | IM-01 (1.00) | 0.95 | 0.05 | 0.96 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-A003 | dois imóveis parecidos | IM-01 | False | IM-01 (1.00) | 0.97 | 0.03 | 0.97 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-A004 | referência vaga | IM-02 | True | IM-02 (0.99) | 0.92 | 0.82 | 0.71 | trocar_referente | trocar_referente | ✓ | manter (IM-01) | rascunho usa fato de outro candidato |
| IE-A005 | correção do cliente | IM-01 | True | IM-01 (1.00) | 0.96 | 0.96 | 0.85 | trocar_referente | trocar_referente | ✓ | trocar_referente (IM-01) | rascunho usa fato de outro candidato |
| IE-A006 | atributo que só um tem | IM-03 | False | IM-03 (0.99) | 0.95 | 0.04 | 0.96 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-A007 | atributo que dois têm | null | True | null (0.85) | 0.23 | 0.22 | 0.84 | pedir_esclarecimento | pedir_esclarecimento | ✓ | pedir_esclarecimento (null) | o Jev não identificou um candidato |
| IE-A008 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.92 | 0.04 | 0.97 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-A009 | referência vaga | IM-03 | False | IM-03 (0.98) | 0.94 | 0.04 | 0.97 | manter | manter | ✓ | trocar_referente (IM-02) | rascunho sobre o referente |
| IE-A010 | citação de fala antiga | IM-02 | False | IM-02 (1.00) | 0.95 | 0.04 | 0.91 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-A011 | troca de foco no meio | IM-01 | True | IM-01 (1.00) | 0.94 | 0.97 | 0.83 | trocar_referente | trocar_referente | ✓ | trocar_referente (IM-01) | rascunho usa fato de outro candidato |
| IE-A012 | dois imóveis parecidos | IM-02 | False | IM-02 (1.00) | 0.91 | 0.08 | 0.97 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-A013 | atributo que só um tem | IM-01 | False | IM-01 (1.00) | 0.94 | 0.07 | 0.66 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-A014 | atributo que dois têm | null | True | null (0.87) | 0.18 | 0.44 | 0.64 | pedir_esclarecimento | pedir_esclarecimento | ✓ | pedir_esclarecimento (null) | o Jev não identificou um candidato |
| IE-A015 | correção do cliente | IM-02 | False | IM-02 (1.00) | 0.97 | 0.08 | 0.58 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-A016 | fácil / outros | IM-02 | True | IM-02 (1.00) | 0.97 | 0.64 | 0.45 | trocar_referente | trocar_referente | ✓ | manter (IM-02) | dúvida sobre o rascunho (0.64) |
| IE-A017 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.96 | 0.05 | 0.88 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-A018 | atributo que só um tem | IM-02 | False | IM-02 (1.00) | 0.95 | 0.05 | 0.96 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-A019 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.96 | 0.03 | 0.97 | manter | manter | ✓ | trocar_referente (IM-02) | rascunho sobre o referente |
| IE-A020 | difícil: outra | IM-01 | True | IM-01 (1.00) | 0.95 | 0.97 | 0.85 | trocar_referente | trocar_referente | ✓ | trocar_referente (IM-01) | rascunho usa fato de outro candidato |
| IE-A021 | atributo que dois têm | null | False | null (0.99) | 0.05 | 0.05 | 0.09 | pedir_esclarecimento | pedir_esclarecimento | ✓ | trocar_referente (IM-01) | o Jev não identificou um candidato |
| IE-A022 | outro nulo | null | True | null (0.85) | 0.12 | 0.32 | 0.96 | pedir_esclarecimento | pedir_esclarecimento | ✓ | pedir_esclarecimento (null) | o Jev não identificou um candidato |
| IE-A023 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.97 | 0.03 | 0.98 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-A024 | dois imóveis parecidos | IM-03 | True | IM-03 (1.00) | 0.95 | 0.97 | 0.52 | trocar_referente | trocar_referente | ✓ | manter (IM-03) | rascunho usa fato de outro candidato |

## Conjunto `teste` — 48 conversas (arquivo versão 2026-10-01, autor fable); 8 com referente nulo, 33 difíceis

### Ação — métrica principal, baseline × sempre pergunta × Jev nos mesmos casos

Gabarito da ação: referente nulo → `pedir_esclarecimento`; `rascunho_usa_outro` → `trocar_referente`; senão `manter`. **Erro caro** = rascunho que usa fato de outro imóvel e recebeu `manter` (a resposta errada iria ao cliente). `troca p/ candidato errado` = trocou sugerindo outro que não o referente do gabarito. `sugeriu candidato c/ gabarito nulo` = o gabarito exige esclarecimento e a saída foi `manter`/`trocar_referente` (assumiu um imóvel que o cliente não identificou; achado 4 da revisão). **RESPOSTA ERRADA (soma)** = os três somados, sobre n: é o critério 1. `sempre pergunta` = o custo de evitar todo erro: zero resposta errada, 100% das conversas interrompidas. `acerto_referente` compara o referente decidido (nulo = pediu) com o gabarito, nulo incluído.

| variante | n | acerto_acao | ERRO CARO (usa outro → manter) | troca p/ candidato errado | sugeriu candidato c/ gabarito nulo | RESPOSTA ERRADA (soma) | pediu sem necessidade | trocou sem necessidade | nulo → pedir | acerto_referente (c/ nulo) |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (último citado) | 48 | 0.542 | 8/19 | 2/40 | 3/8 | 13/48 | 9/40 | 3/25 | 5/8 | 0.700 |
| sempre pergunta | 48 | 0.167 | 0/19 | 0/40 | 0/8 | 0/48 | 40/40 | 0/25 | 8/8 | 0.000 |
| Jev | 48 | 0.958 | 0/19 | 0/40 | 0/8 | 0/48 | 0/40 | 2/25 | 8/8 | 1.000 |

**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | manter | trocar_referente | pedir_esclarecimento |
|---|---|---|---|
| manter | 23 | 2 | 0 |
| trocar_referente | 0 | 15 | 0 |
| pedir_esclarecimento | 0 | 0 | 8 |

**Matriz de confusão — baseline**

| gabarito ↓ / previsto → | manter | trocar_referente | pedir_esclarecimento |
|---|---|---|---|
| manter | 16 | 3 | 6 |
| trocar_referente | 7 | 5 | 3 |
| pedir_esclarecimento | 2 | 1 | 5 |

### Referente — Choice crua (vencedor; válvula = nulo), antes dos portões

| acerto Jev (c/ nulo) | acerto Jev (só não nulos) | acerto baseline (c/ nulo) | nulo → válvula | não nulo → válvula (perda) | piso atual |
|---|---|---|---|---|---|
| 1.000 | 1.000 | 0.700 | 8/8 | 0/40 | 0.500 |

**Cobertura × erro por confiança da Choice** (todos os casos; `erro` = vencedor ≠ gabarito, nulo incluído)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 48 |
| 0.300 | 1.000 | 0.000 | 48 |
| 0.500 | 1.000 | 0.000 | 48 |
| 0.700 | 0.917 | 0.000 | 44 |
| 0.900 | 0.875 | 0.000 | 42 |

### Nouls — acerto (≥ 0,5) no subconjunto que cada um decide, faixa atual e Brier

| noul | subconjunto | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| unambiguous_reference | todos (gabarito = referente não nulo) | 1.000 | 0.3–0.3 | 1.000 | 0.958 | 0 | 48 | 0.012 |
| draft_uses_other | referente não nulo | 0.950 | 0.3–0.7 | 0.925 | 0.973 | 3 | 40 | 0.039 |
| draft_commits_to_one | referente nulo | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 8 | 0.011 |

**`rascunho_usa_outro` composto** (relacional se o referente foi decidido, senão "se compromete com um"; ≥ 0,5): Jev 0.958 · baseline por palavra-chave 0.562 (n = 48)

### Por família difícil (pela `nota` do rotulador)

| família | n | referente Jev | referente baseline | ação Jev | ação baseline | erros caros Jev |
|---|---|---|---|---|---|---|
| troca de foco no meio | 4 | 1.000 | 1.000 | 1.000 | 0.500 | 0 |
| citação de fala antiga | 6 | 1.000 | 0.667 | 1.000 | 0.667 | 0 |
| dois imóveis parecidos | 5 | 1.000 | 0.600 | 1.000 | 0.400 | 0 |
| referência vaga | 8 | 1.000 | 0.429 | 0.750 | 0.375 | 0 |
| correção do cliente | 2 | 1.000 | 0.500 | 1.000 | 0.000 | 0 |
| atributo que só um tem | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 0 |
| atributo que dois têm (null) | 5 | nan | nan | 1.000 | 0.600 | 0 |
| difícil: outra | 1 | 1.000 | 0.000 | 1.000 | 0.000 | 0 |
| outro nulo (fora da lista / geral) | 2 | nan | nan | 1.000 | 0.500 | 0 |
| fácil / outros | 13 | 1.000 | 0.846 | 1.000 | 0.692 | 0 |

### Cobertura automática × erro por piso da Choice e faixa dos Nouls (mesmas respostas; informativo no teste)

| piso_choice | faixa_nouls | atual | cobertura_auto | erro_automatico | erros_caros | n_auto |
|---|---|---|---|---|---|---|
| 0.000 | 0.5–0.5 |  | 0.833 | 0.050 | 1 | 40 |
| 0.000 | 0.3–0.7 |  | 0.833 | 0.050 | 0 | 40 |
| 0.000 | 0.2–0.8 |  | 0.833 | 0.075 | 0 | 40 |
| 0.500 | 0.5–0.5 |  | 0.833 | 0.050 | 1 | 40 |
| 0.500 | 0.3–0.7 | ← | 0.833 | 0.050 | 0 | 40 |
| 0.500 | 0.2–0.8 |  | 0.833 | 0.075 | 0 | 40 |
| 0.700 | 0.5–0.5 |  | 0.792 | 0.026 | 1 | 38 |
| 0.700 | 0.3–0.7 |  | 0.792 | 0.000 | 0 | 38 |
| 0.700 | 0.2–0.8 |  | 0.792 | 0.026 | 0 | 38 |
| 0.900 | 0.5–0.5 |  | 0.792 | 0.026 | 1 | 38 |
| 0.900 | 0.3–0.7 |  | 0.792 | 0.000 | 0 | 38 |
| 0.900 | 0.2–0.8 |  | 0.792 | 0.026 | 0 | 38 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | conversas_longas (sem chamada) | perguntas | p50_ms | p95_ms | tokens_por_conversa | US$_total | US$_por_1000_conversas | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 48 | 0 | 0 | 192 | 264 | 346 | 1634 | 0.003295 | 0.0686 | jev-1.13.0 |

### Caso a caso

`ref` = vencedor da Choice (confiança); `unamb`/`usa`/`comp` = Nouls `unambiguous_reference`, `draft_uses_other`, `draft_commits_to_one`; `ok` compara a ação do Jev com o gabarito; `base` = ação do baseline.

| id | fam | gab ref | usa_outro | ref | unamb | usa | comp | ação Jev | gab ação | ok | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IE-T001 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.96 | 0.05 | 0.93 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-T002 | fácil / outros | IM-02 | True | IM-02 (1.00) | 0.95 | 0.98 | 0.85 | trocar_referente | trocar_referente | ✓ | trocar_referente (IM-02) | rascunho usa fato de outro candidato |
| IE-T003 | troca de foco no meio | IM-02 | True | IM-02 (0.92) | 0.82 | 0.54 | 0.70 | trocar_referente | trocar_referente | ✓ | manter (IM-02) | dúvida sobre o rascunho (0.54) |
| IE-T004 | citação de fala antiga | IM-02 | False | IM-02 (1.00) | 0.96 | 0.03 | 0.96 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-T005 | dois imóveis parecidos | IM-02 | True | IM-02 (0.99) | 0.96 | 0.97 | 0.69 | trocar_referente | trocar_referente | ✓ | trocar_referente (IM-02) | rascunho usa fato de outro candidato |
| IE-T006 | referência vaga | IM-02 | False | IM-02 (0.93) | 0.94 | 0.05 | 0.96 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T007 | referência vaga | IM-01 | True | IM-01 (1.00) | 0.94 | 0.95 | 0.70 | trocar_referente | trocar_referente | ✓ | manter (IM-01) | rascunho usa fato de outro candidato |
| IE-T008 | atributo que só um tem | IM-02 | False | IM-02 (1.00) | 0.96 | 0.03 | 0.98 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T009 | referência vaga | null | True | null (0.61) | 0.31 | 0.48 | 0.92 | pedir_esclarecimento | pedir_esclarecimento | ✓ | pedir_esclarecimento (null) | o Jev não identificou um candidato |
| IE-T010 | fácil / outros | IM-02 | False | IM-02 (1.00) | 0.96 | 0.03 | 0.95 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T011 | referência vaga | IM-03 | False | IM-03 (0.97) | 0.91 | 0.05 | 0.97 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-T012 | citação de fala antiga | IM-02 | True | IM-02 (1.00) | 0.96 | 0.97 | 0.59 | trocar_referente | trocar_referente | ✓ | pedir_esclarecimento (null) | rascunho usa fato de outro candidato |
| IE-T013 | dois imóveis parecidos | IM-02 | False | IM-02 (1.00) | 0.96 | 0.03 | 0.94 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-T014 | fácil / outros | IM-02 | False | IM-02 (1.00) | 0.94 | 0.04 | 0.96 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T015 | referência vaga | IM-01 | True | IM-01 (0.99) | 0.94 | 0.96 | 0.43 | trocar_referente | trocar_referente | ✓ | pedir_esclarecimento (null) | rascunho usa fato de outro candidato |
| IE-T016 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.95 | 0.12 | 0.86 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-T017 | atributo que dois têm | null | True | null (0.80) | 0.16 | 0.21 | 0.80 | pedir_esclarecimento | pedir_esclarecimento | ✓ | manter (IM-03) | o Jev não identificou um candidato |
| IE-T018 | troca de foco no meio | IM-01 | True | IM-01 (1.00) | 0.93 | 0.95 | 0.70 | trocar_referente | trocar_referente | ✓ | manter (IM-01) | rascunho usa fato de outro candidato |
| IE-T019 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.96 | 0.03 | 0.97 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-T020 | citação de fala antiga | IM-02 | False | IM-02 (1.00) | 0.96 | 0.03 | 0.97 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T021 | dois imóveis parecidos | IM-02 | True | IM-02 (1.00) | 0.96 | 0.94 | 0.69 | trocar_referente | trocar_referente | ✓ | manter (IM-02) | rascunho usa fato de outro candidato |
| IE-T022 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.97 | 0.03 | 0.96 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-T023 | dois imóveis parecidos | IM-02 | True | IM-02 (0.99) | 0.93 | 0.94 | 0.44 | trocar_referente | trocar_referente | ✓ | pedir_esclarecimento (null) | rascunho usa fato de outro candidato |
| IE-T024 | atributo que dois têm | null | False | null (0.96) | 0.07 | 0.07 | 0.08 | pedir_esclarecimento | pedir_esclarecimento | ✓ | pedir_esclarecimento (null) | o Jev não identificou um candidato |
| IE-T025 | atributo que só um tem | IM-02 | False | IM-02 (1.00) | 0.95 | 0.04 | 0.96 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T026 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.96 | 0.03 | 0.97 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-T027 | outro nulo | null | True | null (0.82) | 0.33 | 0.24 | 0.95 | pedir_esclarecimento | pedir_esclarecimento | ✓ | pedir_esclarecimento (null) | o Jev não identificou um candidato |
| IE-T028 | fácil / outros | IM-02 | True | IM-02 (1.00) | 0.95 | 0.45 | 0.75 | trocar_referente | trocar_referente | ✓ | manter (IM-02) | dúvida sobre o rascunho (0.45) |
| IE-T029 | fácil / outros | IM-01 | False | IM-01 (1.00) | 0.96 | 0.04 | 0.96 | manter | manter | ✓ | pedir_esclarecimento (null) | rascunho sobre o referente |
| IE-T030 | correção do cliente | IM-01 | False | IM-01 (1.00) | 0.95 | 0.17 | 0.43 | manter | manter | ✓ | trocar_referente (IM-01) | rascunho sobre o referente |
| IE-T031 | troca de foco no meio | IM-02 | False | IM-02 (0.96) | 0.89 | 0.22 | 0.92 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T032 | citação de fala antiga | IM-02 | True | IM-02 (1.00) | 0.97 | 0.97 | 0.87 | trocar_referente | trocar_referente | ✓ | trocar_referente (IM-02) | rascunho usa fato de outro candidato |
| IE-T033 | atributo que dois têm | null | False | null (0.92) | 0.11 | 0.07 | 0.12 | pedir_esclarecimento | pedir_esclarecimento | ✓ | pedir_esclarecimento (null) | o Jev não identificou um candidato |
| IE-T034 | referência vaga | IM-02 | False | IM-02 (0.54) | 0.85 | 0.46 | 0.90 | trocar_referente | manter | ✗ | pedir_esclarecimento (null) | dúvida sobre o rascunho (0.46) |
| IE-T035 | fácil / outros | IM-01 | True | IM-01 (1.00) | 0.89 | 0.85 | 0.86 | trocar_referente | trocar_referente | ✓ | manter (IM-01) | rascunho usa fato de outro candidato |
| IE-T036 | citação de fala antiga | IM-02 | False | IM-02 (1.00) | 0.97 | 0.03 | 0.97 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T037 | fácil / outros | IM-02 | False | IM-02 (1.00) | 0.97 | 0.02 | 0.98 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T038 | difícil: outra | IM-02 | True | IM-02 (1.00) | 0.96 | 0.93 | 0.63 | trocar_referente | trocar_referente | ✓ | manter (IM-01) | rascunho usa fato de outro candidato |
| IE-T039 | outro nulo | null | False | null (0.98) | 0.06 | 0.04 | 0.05 | pedir_esclarecimento | pedir_esclarecimento | ✓ | manter (IM-01) | o Jev não identificou um candidato |
| IE-T040 | fácil / outros | IM-01 | True | IM-01 (1.00) | 0.96 | 0.96 | 0.78 | trocar_referente | trocar_referente | ✓ | trocar_referente (IM-01) | rascunho usa fato de outro candidato |
| IE-T041 | dois imóveis parecidos | IM-01 | False | IM-01 (1.00) | 0.96 | 0.04 | 0.96 | manter | manter | ✓ | manter (IM-01) | rascunho sobre o referente |
| IE-T042 | atributo que dois têm | null | True | null (0.68) | 0.17 | 0.23 | 0.91 | pedir_esclarecimento | pedir_esclarecimento | ✓ | trocar_referente (IM-02) | o Jev não identificou um candidato |
| IE-T043 | correção do cliente | IM-01 | False | IM-01 (1.00) | 0.96 | 0.05 | 0.96 | manter | manter | ✓ | trocar_referente (IM-02) | rascunho sobre o referente |
| IE-T044 | referência vaga | IM-02 | False | IM-02 (0.51) | 0.64 | 0.81 | 0.87 | trocar_referente | manter | ✗ | manter (IM-02) | rascunho usa fato de outro candidato |
| IE-T045 | atributo que dois têm | null | False | null (1.00) | 0.05 | 0.06 | 0.08 | pedir_esclarecimento | pedir_esclarecimento | ✓ | pedir_esclarecimento (null) | o Jev não identificou um candidato |
| IE-T046 | citação de fala antiga | IM-02 | False | IM-02 (1.00) | 0.97 | 0.03 | 0.97 | manter | manter | ✓ | manter (IM-02) | rascunho sobre o referente |
| IE-T047 | troca de foco no meio | IM-02 | True | IM-02 (0.99) | 0.93 | 0.94 | 0.68 | trocar_referente | trocar_referente | ✓ | trocar_referente (IM-02) | rascunho usa fato de outro candidato |
| IE-T048 | referência vaga | IM-02 | False | IM-02 (1.00) | 0.96 | 0.04 | 0.97 | manter | manter | ✓ | trocar_referente (IM-01) | rascunho sobre o referente |
