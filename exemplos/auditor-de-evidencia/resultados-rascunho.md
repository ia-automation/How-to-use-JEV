# Rascunho — auditor-de-evidencia (encanamento)

## Conjunto `rascunho` — 5 afirmações (arquivo versão 2026-10-01, autor fable); 0 difíceis; gabarito: supported 4, contradicted 1, insufficient_evidence 0

> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**

### Relação — métrica principal, baseline × sempre pede prova × Jev nos mesmos casos

`acerto (revisa=erro)` compara o veredito com o gabarito contando `revisa` como erro; `cobertura` = fração decidida sem humano. **FALSA APROVAÇÃO** = gabarito `insufficient_evidence` ou `contradicted` que saiu `supported` (o relatório passaria no portão sem prova): critério 1. `falso alarme` = gabarito `supported` que saiu `contradicted`. `sempre pede prova` = o custo de evitar toda falsa aprovação: nada aprovado. Apoio: precisão/recall micro dos `registros_de_apoio` previstos contra o gabarito, por PAR (registro, papel) — papel = `contradiz` quando a relação é `contradicted`, `sustenta` nas demais; citar como sustentação o registro que contradiz não pontua; `exato` = conjunto de pares igual.

| variante | n | acerto (revisa=erro) | cobertura | acerto_decididos | revisa | FALSA APROVAÇÃO | falso alarme | apoio precisão | apoio recall | apoio exato |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (palavra-chave) | 5 | 1.000 | 1.000 | 1.000 | 0 | 0/1 | 0/4 | 0.667 | 1.000 | 2/5 |
| sempre pede prova | 5 | 0.000 | 1.000 | 0.000 | 0 | 0/1 | 0/4 | nan | 0.000 | 0/5 |
| Jev | 5 | 1.000 | 1.000 | 1.000 | 0 | 0/1 | 0/4 | 0.857 | 1.000 | 4/5 |

**Leituras de "provada" nas mesmas respostas** (`COMPOSICAO` atual: `parts`): só o Noul global `established`; só os 4 Nouls por parte; ambos; e sem leitura global (algum registro sustenta parte → supported).

| composição | n | acerto (revisa=erro) | cobertura | acerto_decididos | revisa | FALSA APROVAÇÃO | falso alarme | apoio precisão | apoio recall | apoio exato |
|---|---|---|---|---|---|---|---|---|---|---|
| established | 5 | 1.000 | 1.000 | 1.000 | 0 | 0/1 | 0/4 | 0.857 | 1.000 | 4/5 |
| parts | 5 | 1.000 | 1.000 | 1.000 | 0 | 0/1 | 0/4 | 0.857 | 1.000 | 4/5 |
| both | 5 | 1.000 | 1.000 | 1.000 | 0 | 0/1 | 0/4 | 0.857 | 1.000 | 4/5 |
| nenhuma (só supports_i) | 5 | 1.000 | 1.000 | 1.000 | 0 | 0/1 | 0/4 | 0.857 | 1.000 | 4/5 |

**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto; `revisa` = foi para humano)

| gabarito ↓ / previsto → | supported | contradicted | insufficient_evidence | revisa |
|---|---|---|---|---|
| supported | 4 | 0 | 0 | 0 |
| contradicted | 0 | 1 | 0 | 0 |
| insufficient_evidence | 0 | 0 | 0 | 0 |

**Matriz de confusão — baseline**

| gabarito ↓ / previsto → | supported | contradicted | insufficient_evidence | revisa |
|---|---|---|---|---|
| supported | 4 | 0 | 0 | 0 |
| contradicted | 0 | 1 | 0 | 0 |
| insufficient_evidence | 0 | 0 | 0 | 0 |

### Nouls — acerto (≥ 0,5) e Brier no que cada um decide

| noul | gabarito | n | acerto | faixa | cobertura | acerto_decididos | revisao | brier |
|---|---|---|---|---|---|---|---|---|
| supports_i | registro sustenta parte (rótulo inequívoco) | 9 | 0.889 | 0.5–0.5 | 1.000 | 0.889 | 0 | 0.059 |
| contradicts_i | registro está no apoio de contradicted | 10 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 0.002 |
| established | relação = supported | 5 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 0.015 |
| object_shown | relação = supported (leitura) | 5 | 0.800 | 0.3–0.7 | 1.000 | 0.800 | 0 | 0.194 |
| state_shown | relação = supported (leitura) | 5 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 0.017 |
| place_shown | relação = supported (leitura) | 5 | 0.800 | 0.3–0.7 | 0.800 | 1.000 | 1 | 0.085 |
| scope_shown | relação = supported (leitura) | 5 | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 0.028 |

`supports_i` é medido só onde o gabarito rotula o registro sem ambiguidade: em `supported` e `insufficient_evidence`, apoio = sustenta e o resto = não sustenta; em `contradicted`, o apoio contradiz (não sustenta) e os registros FORA do apoio não têm rótulo de sustentação — **1 registros ficaram fora** da métrica de `supports_i` neste conjunto. `contradicts_i` não perde nenhum (fora do apoio de `contradicted`, e qualquer registro das outras relações, não contradiz).

**Trabalho do código**: antes da chamada, 0 registros de outra revisão/migration e 0 de número refeito por outro mais recente saíram do state (0 afirmações ficaram sem registro e não foram ao Jev), e 0 registros de outro ambiente/componente ficaram sem check numérico; 4 checks no state (0 falham); depois da chamada, 0 registros superados por outro mais recente do mesmo assunto (0 afirmações com 2ª passada sem o superado); 0 afirmações com registros reordenados por carimbo.

### Por família difícil (pela `nota` do rotulador; heurística por palavra)

| família | n | Jev | revisa | falsas aprov. Jev | baseline | falsas aprov. base |
|---|---|---|---|---|---|---|
| fácil / outros | 5 | 1.000 | 0 | 0 | 1.000 | 0 |

### Cobertura × erro por faixa de `contradicts` × faixa de `established`/partes (mesmas respostas; informativo no teste)

| faixa_contradicts | faixa_established | atual | cobertura | erro_decididos | falsas_aprovacoes | acerto (revisa=erro) |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 0.5–0.5 |  | 1.000 | 0.000 | 0 | 1.000 |
| 0.5–0.5 | 0.3–0.7 |  | 1.000 | 0.000 | 0 | 1.000 |
| 0.5–0.5 | 0.2–0.8 |  | 0.800 | 0.000 | 0 | 0.800 |
| 0.3–0.7 | 0.5–0.5 |  | 1.000 | 0.000 | 0 | 1.000 |
| 0.3–0.7 | 0.3–0.7 | ← | 1.000 | 0.000 | 0 | 1.000 |
| 0.3–0.7 | 0.2–0.8 |  | 0.800 | 0.000 | 0 | 0.800 |
| 0.2–0.8 | 0.5–0.5 |  | 1.000 | 0.000 | 0 | 1.000 |
| 0.2–0.8 | 0.3–0.7 |  | 1.000 | 0.000 | 0 | 1.000 |
| 0.2–0.8 | 0.2–0.8 |  | 0.800 | 0.000 | 0 | 0.800 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | 2as_passadas | perguntas | p50_ms | p95_ms | tokens_por_afirmacao | US$_total | US$_por_1000_afirmacoes | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | 0 | 45 | 333 | 357 | 3611 | 0.000758 | 0.1516 | jev-1.13.0 |

### Caso a caso

`sup/con` = Nouls `supports_i` / `contradicts_i` por registro (ordem cronológica); `est` = `established`; `partes` = `object_shown` / `state_shown` / `place_shown` / `scope_shown`; `ok` compara o veredito do Jev com o gabarito; `base` = baseline. `código` = trabalho do código: checks no state, registros fora do state antes da chamada (outra revisão/migration; número refeito), registros sem check (outro ambiente/componente) e superados depois da chamada. Registro fora do state não tem Noul.

| id | fam | gab | Jev | ok | apoio gab | apoio Jev | est | partes | sup/con | código | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AE-R001 | fácil | supported | supported | ✓ | e1 | e1 | 0.91 | obj 0.97 sta 0.96 pla 0.96 sco 0.74 | e1 0.95/0.02 e2 0.12/0.03 | — | supported | provada (partes object 0.97 state 0.96 place 0.96 scope 0.74) |
| AE-R002 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.97 sta 0.24 pla 0.64 sco 0.22 | e1 0.23/0.96 e2 0.56/0.11 | — | contradicted | contradição 0.96 |
| AE-R003 | fácil | supported | supported | ✓ | e1,e2 | e1,e2 | 0.92 | obj 0.97 sta 0.98 pla 0.96 sco 0.91 | e1 0.95/0.03 e2 0.96/0.02 | e1 migration ok; e2 migration ok | supported | provada (partes object 0.97 state 0.98 place 0.96 scope 0.91) |
| AE-R004 | fácil | supported | supported | ✓ | e1 | e1 | 0.76 | obj 0.83 sta 0.85 pla 0.89 sco 0.88 | e1 0.68/0.03 e2 0.22/0.04 | — | supported | provada (partes object 0.83 state 0.85 place 0.89 scope 0.88) |
| AE-R005 | fácil | supported | supported | ✓ | e1 | e1,e2 | 0.96 | obj 0.98 sta 0.97 pla 0.97 sco 0.95 | e1 0.98/0.02 e2 0.55/0.03 | e1 version ok; e2 version ok | supported | provada (partes object 0.98 state 0.97 place 0.97 scope 0.95) |
