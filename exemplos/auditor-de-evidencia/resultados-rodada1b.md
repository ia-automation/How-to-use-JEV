# Resultados — auditor-de-evidencia

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; checks, recência, composição e validação: `auditor.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Faixas: contradicts (0.3, 0.7), established (0.3, 0.7), partes (0.3, 0.7), apoio ≥ 0.5; leitura de provada: `parts`.

Critério de continuar/descartar (fixado antes do teste): no teste (73 afirmações), com a política acima, revisa contado como erro no acerto: (1) gabarito insufficient_evidence ou contradicted → supported: ≤ 2% (≤ 1/73); (2) acerto da relação (revisa = erro) ≥ baseline + 0,15. Secundário: falso alarme (supported → contradicted) ≤ 2; cobertura (não revisa) ≥ 0,80; precisão e recall dos registros_de_apoio reportados.

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T12:38:39-03:00, antes de abrir o teste): `perguntas.py` sha256 e0ff7f963ba22a7d… · `auditor.py` sha256 2a892ba9644a51e1… · `run.py` sha256 9b14cd24f5315ffb… · `dados/teste.json` sha256 6bdb935ba4030be2…

## Lado a lado

### Relação por variante e conjunto

| conjunto | variante | n | acerto (revisa=erro) | cobertura | acerto_decididos | revisa | FALSA APROVAÇÃO | falso alarme | apoio precisão | apoio recall | apoio exato |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | baseline (palavra-chave) | 31 | 0.419 | 1.000 | 0.419 | 0 | 9/23 | 1/8 | 0.552 | 0.615 | 11/31 |
| ajuste | sempre pede prova | 31 | 0.484 | 1.000 | 0.484 | 0 | 0/23 | 0/8 | nan | 0.000 | 8/31 |
| ajuste | Jev | 31 | 0.806 | 0.806 | 1.000 | 6 | 0/23 | 0/8 | 0.917 | 0.846 | 25/31 |
| teste | baseline (palavra-chave) | 73 | 0.425 | 1.000 | 0.425 | 0 | 26/48 | 1/25 | 0.500 | 0.672 | 24/73 |
| teste | sempre pede prova | 73 | 0.370 | 1.000 | 0.370 | 0 | 0/48 | 0/25 | nan | 0.000 | 12/73 |
| teste | Jev | 73 | 0.808 | 0.836 | 0.967 | 12 | 1/48 | 0/25 | 0.824 | 0.875 | 54/73 |

### Custo e trabalho do código

| conjunto | n | difíceis | checks | checks_falham | superados | reordenados | segundas_passadas | p50_ms | p95_ms | tokens_por_afirmacao | US$_por_1000 | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | 31 | 26 | 13 | 4 | 2 | 1 | 1 | 304 | 361 | 3765 | 0.1581 | jev-1.13.0 |
| teste | 73 | 45 | 30 | 7 | 3 | 1 | 2 | 285 | 432 | 3722 | 0.1563 | jev-1.13.0 |

## Conjunto `ajuste` — 31 afirmações (arquivo versão 2026-10-01, autor fable); 26 difíceis; gabarito: supported 8, contradicted 8, insufficient_evidence 15

### Relação — métrica principal, baseline × sempre pede prova × Jev nos mesmos casos

`acerto (revisa=erro)` compara o veredito com o gabarito contando `revisa` como erro; `cobertura` = fração decidida sem humano. **FALSA APROVAÇÃO** = gabarito `insufficient_evidence` ou `contradicted` que saiu `supported` (o relatório passaria no portão sem prova): critério 1. `falso alarme` = gabarito `supported` que saiu `contradicted`. `sempre pede prova` = o custo de evitar toda falsa aprovação: nada aprovado. Apoio: precisão/recall micro dos `registros_de_apoio` previstos contra o gabarito; `exato` = conjunto igual.

| variante | n | acerto (revisa=erro) | cobertura | acerto_decididos | revisa | FALSA APROVAÇÃO | falso alarme | apoio precisão | apoio recall | apoio exato |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (palavra-chave) | 31 | 0.419 | 1.000 | 0.419 | 0 | 9/23 | 1/8 | 0.552 | 0.615 | 11/31 |
| sempre pede prova | 31 | 0.484 | 1.000 | 0.484 | 0 | 0/23 | 0/8 | nan | 0.000 | 8/31 |
| Jev | 31 | 0.806 | 0.806 | 1.000 | 6 | 0/23 | 0/8 | 0.917 | 0.846 | 25/31 |

**Leituras de "provada" nas mesmas respostas** (`COMPOSICAO` atual: `parts`): só o Noul global `established`; só os 4 Nouls por parte; ambos; e sem leitura global (algum registro sustenta parte → supported).

| composição | n | acerto (revisa=erro) | cobertura | acerto_decididos | revisa | FALSA APROVAÇÃO | falso alarme | apoio precisão | apoio recall | apoio exato |
|---|---|---|---|---|---|---|---|---|---|---|
| established | 31 | 0.774 | 0.839 | 0.923 | 5 | 1/23 | 0/8 | 0.917 | 0.846 | 25/31 |
| parts | 31 | 0.806 | 0.806 | 1.000 | 6 | 0/23 | 0/8 | 0.917 | 0.846 | 25/31 |
| both | 31 | 0.806 | 0.839 | 0.962 | 5 | 0/23 | 0/8 | 0.917 | 0.846 | 25/31 |
| nenhuma (só supports_i) | 31 | 0.774 | 0.968 | 0.800 | 1 | 6/23 | 0/8 | 0.917 | 0.846 | 25/31 |

**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto; `revisa` = foi para humano)

| gabarito ↓ / previsto → | supported | contradicted | insufficient_evidence | revisa |
|---|---|---|---|---|
| supported | 7 | 0 | 0 | 1 |
| contradicted | 0 | 7 | 0 | 1 |
| insufficient_evidence | 0 | 0 | 11 | 4 |

**Matriz de confusão — baseline**

| gabarito ↓ / previsto → | supported | contradicted | insufficient_evidence | revisa |
|---|---|---|---|---|
| supported | 4 | 1 | 3 | 0 |
| contradicted | 2 | 4 | 2 | 0 |
| insufficient_evidence | 7 | 3 | 5 | 0 |

### Nouls — acerto (≥ 0,5) e Brier no que cada um decide

| noul | gabarito | n | acerto | faixa | cobertura | acerto_decididos | revisao | brier |
|---|---|---|---|---|---|---|---|---|
| supports_i | registro está no apoio de supported/insufficient | 63 | 0.857 | 0.5–0.5 | 1.000 | 0.857 | 0 | 0.122 |
| contradicts_i | registro está no apoio de contradicted | 63 | 0.984 | 0.3–0.7 | 0.968 | 0.984 | 2 | 0.020 |
| established | relação = supported | 31 | 0.839 | 0.3–0.7 | 0.871 | 0.889 | 4 | 0.089 |
| object_shown | relação = supported (leitura) | 31 | 0.419 | 0.3–0.7 | 0.806 | 0.400 | 6 | 0.463 |
| state_shown | relação = supported (leitura) | 31 | 0.677 | 0.3–0.7 | 0.613 | 0.789 | 12 | 0.200 |
| place_shown | relação = supported (leitura) | 31 | 0.452 | 0.3–0.7 | 0.903 | 0.464 | 3 | 0.447 |
| scope_shown | relação = supported (leitura) | 31 | 0.677 | 0.3–0.7 | 0.774 | 0.792 | 7 | 0.186 |

**Trabalho do código**: 13 checks numéricos/de revisão (4 falham), 2 registros superados por outro mais recente do mesmo tipo (1 afirmações com 2ª passada sem o superado), 1 afirmações com registros reordenados por carimbo.

### Por família difícil (pela `nota` do rotulador; heurística por palavra)

| família | n | Jev | revisa | falsas aprov. Jev | baseline | falsas aprov. base |
|---|---|---|---|---|---|---|
| 8 verde velho × vermelho novo | 2 | 0.500 | 1 | 0 | 0.500 | 0 |
| 13 404 / saúde no lugar da rota | 3 | 1.000 | 0 | 0 | 1.000 | 0 |
| 2 HTTP 200 sem conteúdo / com erro | 2 | 0.500 | 1 | 0 | 0.000 | 2 |
| 9 homolog/localhost como produção | 2 | 1.000 | 0 | 0 | 0.000 | 0 |
| 4 teste com mock | 1 | 0.000 | 1 | 0 | 0.000 | 1 |
| 6 registro manual | 2 | 1.000 | 0 | 0 | 0.500 | 1 |
| 12a lint sem erros × limpo | 2 | 0.500 | 1 | 0 | 0.000 | 0 |
| 12b numéricas | 1 | 1.000 | 0 | 0 | 0.000 | 1 |
| 1 teste de outra revisão | 1 | 1.000 | 0 | 0 | 0.000 | 1 |
| 11 commit ≠ push / push recusado / gh | 4 | 0.500 | 2 | 0 | 0.750 | 1 |
| 10 subconjunto / pulados / cancelada | 4 | 1.000 | 0 | 0 | 0.250 | 1 |
| 5 dev generalizado / prod com erro / cofre | 1 | 1.000 | 0 | 0 | 0.000 | 1 |
| 3 build sem teste | 1 | 1.000 | 0 | 0 | 1.000 | 0 |
| fácil / outros | 5 | 1.000 | 0 | 0 | 0.600 | 0 |

### Cobertura × erro por faixa de `contradicts` × faixa de `established`/partes (mesmas respostas; informativo no teste)

| faixa_contradicts | faixa_established | atual | cobertura | erro_decididos | falsas_aprovacoes | acerto (revisa=erro) |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 0.5–0.5 |  | 1.000 | 0.065 | 1 | 0.935 |
| 0.5–0.5 | 0.3–0.7 |  | 0.839 | 0.000 | 0 | 0.839 |
| 0.5–0.5 | 0.2–0.8 |  | 0.710 | 0.000 | 0 | 0.710 |
| 0.3–0.7 | 0.5–0.5 |  | 1.000 | 0.097 | 1 | 0.903 |
| 0.3–0.7 | 0.3–0.7 | ← | 0.806 | 0.000 | 0 | 0.806 |
| 0.3–0.7 | 0.2–0.8 |  | 0.677 | 0.000 | 0 | 0.677 |
| 0.2–0.8 | 0.5–0.5 |  | 0.968 | 0.100 | 1 | 0.871 |
| 0.2–0.8 | 0.3–0.7 |  | 0.774 | 0.000 | 0 | 0.774 |
| 0.2–0.8 | 0.2–0.8 |  | 0.677 | 0.000 | 0 | 0.677 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | 2as_passadas | perguntas | p50_ms | p95_ms | tokens_por_afirmacao | US$_total | US$_por_1000_afirmacoes | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 32 | 0 | 1 | 292 | 304 | 361 | 3765 | 0.004902 | 0.1581 | jev-1.13.0 |

### Caso a caso

`sup/con` = Nouls `supports_i` / `contradicts_i` por registro (ordem cronológica); `est` = `established`; `partes` = `object_shown` / `state_shown` / `place_shown` / `scope_shown`; `ok` compara o veredito do Jev com o gabarito; `base` = baseline. `checks` e `superados` = trabalho do código.

| id | fam | gab | Jev | ok | apoio gab | apoio Jev | est | partes | sup/con | código | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AE-A001 | 1 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.03 | obj 0.56 sta 0.21 pla 0.95 sco 0.05 | e2 0.11/0.76 e1 0.16/0.06 | e2 revision FALHA; e1 revision ok; e2 neutro (revision 4c1d8aa ≠ b7e2f90) | supported | não provada (partes object 0.56 state 0.21 place 0.95 scope 0.05) |
| AE-A002 | 2 | insufficient_evidence | revisa | ✗ | e1 | e1,e2 | 0.44 | obj 0.96 sta 0.52 pla 0.91 sco 0.80 | e1 0.67/0.06 e2 0.79/0.03 | — | supported | dúvida (partes object 0.96 state 0.52 place 0.91 scope 0.80) |
| AE-A003 | 3 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.04 | obj 0.14 sta 0.46 pla 0.95 sco 0.28 | e1 0.15/0.05 e2 0.08/0.04 | — | insufficient_evidence | não provada (partes object 0.14 state 0.46 place 0.95 scope 0.28) |
| AE-A004 | 4 | insufficient_evidence | revisa | ✗ | — | — | 0.06 | obj 0.63 sta 0.32 pla 0.96 sco 0.65 | e1 0.18/0.08 e2 0.11/0.05 | — | supported | dúvida (partes object 0.63 state 0.32 place 0.96 scope 0.65) |
| AE-A005 | 5 | insufficient_evidence | insufficient_evidence | ✓ | e1 | e1 | 0.05 | obj 0.95 sta 0.62 pla 0.08 sco 0.16 | e1 0.86/0.10 e2 0.22/0.06 | e1 migration ok | supported | não provada (partes object 0.95 state 0.62 place 0.08 scope 0.16) |
| AE-A006 | 6 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.03 | obj 0.53 sta 0.20 pla 0.95 sco 0.87 | e1 0.05/0.03 e2 0.05/0.03 | — | supported | não provada (partes object 0.53 state 0.20 place 0.95 scope 0.87) |
| AE-A007 | 11 | insufficient_evidence | revisa | ✗ | e1,e2 | e1 | 0.11 | obj 0.45 sta 0.48 pla 0.88 sco 0.73 | e1 0.65/0.05 e2 0.28/0.06 | — | insufficient_evidence | dúvida (partes object 0.45 state 0.48 place 0.88 scope 0.73) |
| AE-A008 | 8 | contradicted | contradicted | ✓ | e3 | e3 | 0.03 | obj 0.84 sta 0.69 pla 0.68 sco 0.09 | e1 0.44/0.05 e2 0.10/0.11 e3 0.06/0.95 | — | contradicted | contradição 0.95 |
| AE-A009 | 8 | supported | revisa | ✗ | e3 | e3 | 0.47 | obj 0.71 sta 0.71 pla 0.48 sco 0.75 | e2 0.18/0.06 e3 0.65/0.04 | e1 superado por e3 (test_log mais recente, sup); 2ª passada sem o superado | contradicted | dúvida (partes object 0.71 state 0.71 place 0.48 scope 0.75) |
| AE-A010 | 9 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.03 | obj 0.94 sta 0.46 pla 0.04 sco 0.35 | e1 0.14/0.15 e2 0.36/0.04 | e1 version ok; e2 version ok | contradicted | não provada (partes object 0.94 state 0.46 place 0.04 scope 0.35) |
| AE-A011 | 10 | insufficient_evidence | insufficient_evidence | ✓ | e1 | e1 | 0.10 | obj 0.85 sta 0.79 pla 0.97 sco 0.06 | e1 0.52/0.09 e2 0.05/0.04 | — | insufficient_evidence | não provada (partes object 0.85 state 0.79 place 0.97 scope 0.06) |
| AE-A012 | 10 | insufficient_evidence | insufficient_evidence | ✓ | e1 | e1 | 0.81 | obj 0.97 sta 0.93 pla 0.97 sco 0.24 | e1 0.81/0.07 e2 0.06/0.04 | — | supported | não provada (partes object 0.97 state 0.93 place 0.97 scope 0.24) |
| AE-A013 | 11 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.06 | obj 0.38 sta 0.15 pla 0.07 sco 0.59 | e1 0.14/0.08 e2 0.05/0.03 | — | insufficient_evidence | não provada (partes object 0.38 state 0.15 place 0.07 scope 0.59) |
| AE-A014 | 11 | contradicted | contradicted | ✓ | e2 | e2 | 0.03 | obj 0.92 sta 0.02 pla 0.11 sco 0.34 | e1 0.11/0.14 e2 0.08/0.94 | — | contradicted | contradição 0.94 |
| AE-A015 | fácil | contradicted | contradicted | ✓ | e2 | e2 | 0.02 | obj 0.97 sta 0.77 pla 0.06 sco 0.06 | e1 0.87/0.09 e2 0.05/0.97 | e1 migration ok; e1 superado por e2 (deploy_event mais recente, contra) | contradicted | contradição 0.97 |
| AE-A016 | fácil | supported | supported | ✓ | e1,e2 | e1,e2 | 0.97 | obj 0.98 sta 0.98 pla 0.98 sco 0.94 | e1 0.97/0.02 e2 0.98/0.02 | e1 migration ok; e2 migration ok | supported | provada (partes object 0.98 state 0.98 place 0.98 scope 0.94) |
| AE-A017 | 12a | supported | supported | ✓ | e1 | e1 | 0.92 | obj 0.79 sta 0.93 pla 0.97 sco 0.87 | e1 0.91/0.11 e2 0.09/0.06 | — | insufficient_evidence | provada (partes object 0.79 state 0.93 place 0.97 scope 0.87) |
| AE-A018 | 12a | contradicted | revisa | ✗ | e1 | — | 0.72 | obj 0.48 sta 0.62 pla 0.89 sco 0.75 | e1 0.40/0.62 e2 0.16/0.30 | — | insufficient_evidence | contradição possível (0.62) |
| AE-A019 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.87 sta 0.14 pla 0.96 sco 0.05 | e1 0.42/0.92 e2 0.10/0.03 | e1 coverage FALHA | insufficient_evidence | código: e1 coverage statements 78.4% não satisfaz statements > 80% |
| AE-A020 | fácil | supported | supported | ✓ | e1 | e1 | 0.69 | obj 0.90 sta 0.85 pla 0.96 sco 0.75 | e1 0.91/0.22 e2 0.15/0.03 | e1 coverage ok | insufficient_evidence | provada (partes object 0.90 state 0.85 place 0.96 scope 0.75) |
| AE-A021 | 9 | insufficient_evidence | insufficient_evidence | ✓ | e1 | — | 0.03 | obj 0.96 sta 0.63 pla 0.05 sco 0.66 | e1 0.21/0.14 e2 0.23/0.04 | — | contradicted | não provada (partes object 0.96 state 0.63 place 0.05 scope 0.66) |
| AE-A022 | 13 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.06 | obj 0.09 sta 0.52 pla 0.40 sco 0.60 | e1 0.13/0.07 e2 0.39/0.04 | — | insufficient_evidence | não provada (partes object 0.09 state 0.52 place 0.40 scope 0.60) |
| AE-A023 | 13 | contradicted | contradicted | ✓ | e2 | e2 | 0.02 | obj 0.95 sta 0.79 pla 0.91 sco 0.23 | e1 0.97/0.11 e2 0.08/0.96 | e1 version ok | contradicted | contradição 0.96 |
| AE-A024 | 6 | supported | supported | ✓ | e2 | e2 | 0.87 | obj 0.97 sta 0.96 pla 0.96 sco 0.84 | e1 0.13/0.02 e2 0.93/0.02 | — | supported | provada (partes object 0.97 state 0.96 place 0.96 scope 0.84) |
| AE-A025 | 11 | insufficient_evidence | revisa | ✗ | — | e1 | 0.54 | obj 0.70 sta 0.41 pla 0.97 sco 0.87 | e1 0.67/0.03 e2 0.30/0.03 | — | supported | dúvida (partes object 0.70 state 0.41 place 0.97 scope 0.87) |
| AE-A026 | 13 | supported | supported | ✓ | e1 | e1 | 0.23 | obj 0.96 sta 0.91 pla 0.72 sco 0.87 | e1 0.74/0.08 e2 0.35/0.05 | — | supported | provada (partes object 0.96 state 0.91 place 0.72 scope 0.87) |
| AE-A027 | 2 | contradicted | contradicted | ✓ | e1 | e1 | 0.06 | obj 0.97 sta 0.33 pla 0.74 sco 0.50 | e1 0.35/0.88 e2 0.73/0.08 | — | supported | contradição 0.88 |
| AE-A028 | 12b | contradicted | contradicted | ✓ | e1,e2 | e1,e2 | 0.01 | obj 0.96 sta 0.02 pla 0.89 sco 0.04 | e1 0.54/0.97 e2 0.25/0.96 | e1 version FALHA; e2 version FALHA | supported | código: e1 version 1.9.1 não satisfaz 1.9.2; e2 version 1.9.1 não satisfaz 1.9.2 |
| AE-A029 | fácil | supported | supported | ✓ | e1 | e1 | 0.85 | obj 0.91 sta 0.93 pla 0.88 sco 0.83 | e1 0.89/0.02 e2 0.09/0.03 | — | supported | provada (partes object 0.91 state 0.93 place 0.88 scope 0.83) |
| AE-A030 | 10 | supported | supported | ✓ | e1 | e1 | 0.92 | obj 0.94 sta 0.96 pla 0.96 sco 0.89 | e1 0.94/0.03 e2 0.08/0.04 | — | insufficient_evidence | provada (partes object 0.94 state 0.96 place 0.96 scope 0.89) |
| AE-A031 | 10 | insufficient_evidence | insufficient_evidence | ✓ | e1 | — | 0.14 | obj 0.90 sta 0.15 pla 0.95 sco 0.11 | e1 0.25/0.37 e2 0.04/0.07 | — | contradicted | não provada (partes object 0.90 state 0.15 place 0.95 scope 0.11); contradição possível (0.37) |

## Conjunto `teste` — 73 afirmações (arquivo versão 2026-10-01, autor fable); 45 difíceis; gabarito: supported 25, contradicted 21, insufficient_evidence 27

### Relação — métrica principal, baseline × sempre pede prova × Jev nos mesmos casos

`acerto (revisa=erro)` compara o veredito com o gabarito contando `revisa` como erro; `cobertura` = fração decidida sem humano. **FALSA APROVAÇÃO** = gabarito `insufficient_evidence` ou `contradicted` que saiu `supported` (o relatório passaria no portão sem prova): critério 1. `falso alarme` = gabarito `supported` que saiu `contradicted`. `sempre pede prova` = o custo de evitar toda falsa aprovação: nada aprovado. Apoio: precisão/recall micro dos `registros_de_apoio` previstos contra o gabarito; `exato` = conjunto igual.

| variante | n | acerto (revisa=erro) | cobertura | acerto_decididos | revisa | FALSA APROVAÇÃO | falso alarme | apoio precisão | apoio recall | apoio exato |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (palavra-chave) | 73 | 0.425 | 1.000 | 0.425 | 0 | 26/48 | 1/25 | 0.500 | 0.672 | 24/73 |
| sempre pede prova | 73 | 0.370 | 1.000 | 0.370 | 0 | 0/48 | 0/25 | nan | 0.000 | 12/73 |
| Jev | 73 | 0.808 | 0.836 | 0.967 | 12 | 1/48 | 0/25 | 0.824 | 0.875 | 54/73 |

**Leituras de "provada" nas mesmas respostas** (`COMPOSICAO` atual: `parts`): só o Noul global `established`; só os 4 Nouls por parte; ambos; e sem leitura global (algum registro sustenta parte → supported).

| composição | n | acerto (revisa=erro) | cobertura | acerto_decididos | revisa | FALSA APROVAÇÃO | falso alarme | apoio precisão | apoio recall | apoio exato |
|---|---|---|---|---|---|---|---|---|---|---|
| established | 73 | 0.822 | 0.863 | 0.952 | 10 | 2/48 | 0/25 | 0.824 | 0.875 | 54/73 |
| parts | 73 | 0.808 | 0.836 | 0.967 | 12 | 1/48 | 0/25 | 0.824 | 0.875 | 54/73 |
| both | 73 | 0.849 | 0.877 | 0.969 | 9 | 0/48 | 0/25 | 0.824 | 0.875 | 54/73 |
| nenhuma (só supports_i) | 73 | 0.877 | 1.000 | 0.877 | 0 | 9/48 | 0/25 | 0.824 | 0.875 | 54/73 |

**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto; `revisa` = foi para humano)

| gabarito ↓ / previsto → | supported | contradicted | insufficient_evidence | revisa |
|---|---|---|---|---|
| supported | 19 | 0 | 1 | 5 |
| contradicted | 0 | 21 | 0 | 0 |
| insufficient_evidence | 1 | 0 | 19 | 7 |

**Matriz de confusão — baseline**

| gabarito ↓ / previsto → | supported | contradicted | insufficient_evidence | revisa |
|---|---|---|---|---|
| supported | 18 | 1 | 6 | 0 |
| contradicted | 7 | 10 | 4 | 0 |
| insufficient_evidence | 19 | 5 | 3 | 0 |

### Nouls — acerto (≥ 0,5) e Brier no que cada um decide

| noul | gabarito | n | acerto | faixa | cobertura | acerto_decididos | revisao | brier |
|---|---|---|---|---|---|---|---|---|
| supports_i | registro está no apoio de supported/insufficient | 148 | 0.797 | 0.5–0.5 | 1.000 | 0.797 | 0 | 0.128 |
| contradicts_i | registro está no apoio de contradicted | 148 | 0.980 | 0.3–0.7 | 0.986 | 0.986 | 2 | 0.020 |
| established | relação = supported | 73 | 0.890 | 0.3–0.7 | 0.836 | 0.951 | 12 | 0.081 |
| object_shown | relação = supported (leitura) | 73 | 0.397 | 0.3–0.7 | 0.877 | 0.406 | 9 | 0.448 |
| state_shown | relação = supported (leitura) | 73 | 0.822 | 0.3–0.7 | 0.712 | 0.865 | 21 | 0.140 |
| place_shown | relação = supported (leitura) | 73 | 0.534 | 0.3–0.7 | 0.932 | 0.544 | 5 | 0.370 |
| scope_shown | relação = supported (leitura) | 73 | 0.781 | 0.3–0.7 | 0.740 | 0.889 | 19 | 0.143 |

**Trabalho do código**: 30 checks numéricos/de revisão (7 falham), 3 registros superados por outro mais recente do mesmo tipo (2 afirmações com 2ª passada sem o superado), 1 afirmações com registros reordenados por carimbo.

### Por família difícil (pela `nota` do rotulador; heurística por palavra)

| família | n | Jev | revisa | falsas aprov. Jev | baseline | falsas aprov. base |
|---|---|---|---|---|---|---|
| 8 verde velho × vermelho novo | 1 | 1.000 | 0 | 0 | 0.000 | 1 |
| 13 404 / saúde no lugar da rota | 3 | 0.667 | 0 | 0 | 1.000 | 0 |
| 2 HTTP 200 sem conteúdo / com erro | 2 | 0.500 | 1 | 0 | 0.500 | 1 |
| 9 homolog/localhost como produção | 3 | 1.000 | 0 | 0 | 0.000 | 0 |
| 4 teste com mock | 3 | 0.000 | 3 | 0 | 0.333 | 2 |
| 6 registro manual | 4 | 0.500 | 2 | 0 | 0.250 | 3 |
| 12a lint sem erros × limpo | 2 | 1.000 | 0 | 0 | 0.000 | 0 |
| 12b numéricas | 1 | 1.000 | 0 | 0 | 0.000 | 1 |
| 14 aceito ≠ entregue / backup / down | 2 | 1.000 | 0 | 0 | 0.000 | 2 |
| 1 teste de outra revisão | 2 | 1.000 | 0 | 0 | 0.000 | 1 |
| 11 commit ≠ push / push recusado / gh | 2 | 0.500 | 1 | 0 | 0.500 | 1 |
| 10 subconjunto / pulados / cancelada | 6 | 0.833 | 1 | 0 | 0.333 | 3 |
| 5 dev generalizado / prod com erro / cofre | 3 | 1.000 | 0 | 0 | 0.000 | 2 |
| 7 testado estendido a publicado | 1 | 1.000 | 0 | 0 | 0.000 | 0 |
| 3 build sem teste | 2 | 1.000 | 0 | 0 | 0.500 | 1 |
| difícil: outra | 8 | 0.750 | 1 | 1 | 0.250 | 5 |
| fácil / outros | 28 | 0.893 | 3 | 0 | 0.679 | 3 |

### Cobertura × erro por faixa de `contradicts` × faixa de `established`/partes (mesmas respostas; informativo no teste)

| faixa_contradicts | faixa_established | atual | cobertura | erro_decididos | falsas_aprovacoes | acerto (revisa=erro) |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 0.5–0.5 |  | 0.986 | 0.083 | 3 | 0.904 |
| 0.5–0.5 | 0.3–0.7 |  | 0.836 | 0.049 | 1 | 0.795 |
| 0.5–0.5 | 0.2–0.8 |  | 0.671 | 0.041 | 1 | 0.644 |
| 0.3–0.7 | 0.5–0.5 |  | 0.986 | 0.069 | 3 | 0.918 |
| 0.3–0.7 | 0.3–0.7 | ← | 0.836 | 0.033 | 1 | 0.808 |
| 0.3–0.7 | 0.2–0.8 |  | 0.671 | 0.020 | 1 | 0.658 |
| 0.2–0.8 | 0.5–0.5 |  | 0.973 | 0.113 | 3 | 0.863 |
| 0.2–0.8 | 0.3–0.7 |  | 0.808 | 0.068 | 1 | 0.753 |
| 0.2–0.8 | 0.2–0.8 |  | 0.644 | 0.064 | 1 | 0.603 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | 2as_passadas | perguntas | p50_ms | p95_ms | tokens_por_afirmacao | US$_total | US$_por_1000_afirmacoes | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 75 | 0 | 2 | 681 | 285 | 432 | 3722 | 0.011410 | 0.1563 | jev-1.13.0 |

### Caso a caso

`sup/con` = Nouls `supports_i` / `contradicts_i` por registro (ordem cronológica); `est` = `established`; `partes` = `object_shown` / `state_shown` / `place_shown` / `scope_shown`; `ok` compara o veredito do Jev com o gabarito; `base` = baseline. `checks` e `superados` = trabalho do código.

| id | fam | gab | Jev | ok | apoio gab | apoio Jev | est | partes | sup/con | código | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AE-T001 | fácil | supported | supported | ✓ | e1 | e1 | 0.93 | obj 0.97 sta 0.96 pla 0.97 sco 0.84 | e1 0.96/0.02 e2 0.14/0.04 | — | supported | provada (partes object 0.97 state 0.96 place 0.97 scope 0.84) |
| AE-T002 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.97 sta 0.23 pla 0.62 sco 0.17 | e1 0.20/0.95 e2 0.59/0.11 | — | contradicted | contradição 0.95 |
| AE-T003 | fácil | supported | supported | ✓ | e1 | e1,e2 | 0.96 | obj 0.98 sta 0.97 pla 0.97 sco 0.93 | e1 0.98/0.02 e2 0.51/0.03 | e1 version ok; e2 version ok | supported | provada (partes object 0.98 state 0.97 place 0.97 scope 0.93) |
| AE-T004 | 1 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.03 | obj 0.46 sta 0.35 pla 0.94 sco 0.04 | e1 0.22/0.07 e2 0.04/0.83 e3 0.10/0.79 | e1 revision ok; e2 revision FALHA; e3 revision FALHA; e2 neutro (revision 2b2b2b2 ≠ 1a1a1a1); e3 neutro (revision 2b2b2b2 ≠ 1a1a1a1) | supported | não provada (partes object 0.46 state 0.35 place 0.94 scope 0.04) |
| AE-T005 | fácil | supported | supported | ✓ | e2 | e2 | 0.92 | obj 0.94 sta 0.97 pla 0.97 sco 0.93 | e1 0.37/0.03 e2 0.97/0.02 | e1 revision ok; e2 revision ok | supported | provada (partes object 0.94 state 0.97 place 0.97 scope 0.93) |
| AE-T006 | 2 | insufficient_evidence | revisa | ✗ | e1 | — | 0.18 | obj 0.93 sta 0.40 pla 0.76 sco 0.66 | e1 0.37/0.14 e2 0.45/0.06 | — | supported | dúvida (partes object 0.93 state 0.40 place 0.76 scope 0.66) |
| AE-T007 | fácil | supported | supported | ✓ | e1 | e1,e2 | 0.56 | obj 0.95 sta 0.95 pla 0.88 sco 0.85 | e1 0.82/0.03 e2 0.62/0.03 | — | supported | provada (partes object 0.95 state 0.95 place 0.88 scope 0.85) |
| AE-T008 | 3 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.03 | obj 0.23 sta 0.28 pla 0.86 sco 0.26 | e1 0.11/0.06 e2 0.04/0.04 | — | supported | não provada (partes object 0.23 state 0.28 place 0.86 scope 0.26) |
| AE-T009 | 3 | supported | supported | ✓ | e1 | e1 | 0.89 | obj 0.94 sta 0.96 pla 0.96 sco 0.83 | e1 0.93/0.02 e2 0.07/0.04 | — | supported | provada (partes object 0.94 state 0.96 place 0.96 scope 0.83) |
| AE-T010 | 4 | supported | revisa | ✗ | e1 | e1 | 0.31 | obj 0.90 sta 0.59 pla 0.96 sco 0.57 | e1 0.76/0.04 e2 0.21/0.04 | — | supported | dúvida (partes object 0.90 state 0.59 place 0.96 scope 0.57) |
| AE-T011 | 4 | insufficient_evidence | revisa | ✗ | — | — | 0.14 | obj 0.73 sta 0.46 pla 0.95 sco 0.85 | e1 0.37/0.05 e2 0.17/0.04 | — | supported | dúvida (partes object 0.73 state 0.46 place 0.95 scope 0.85) |
| AE-T012 | 4 | insufficient_evidence | revisa | ✗ | — | — | 0.18 | obj 0.71 sta 0.57 pla 0.95 sco 0.84 | e1 0.46/0.04 e2 0.19/0.04 | — | supported | dúvida (partes object 0.71 state 0.57 place 0.95 scope 0.84) |
| AE-T013 | 6 | contradicted | contradicted | ✓ | e2 | e2 | 0.04 | obj 0.96 sta 0.60 pla 0.12 sco 0.15 | e1 0.79/0.23 e2 0.05/0.76 | e1 migration ok | supported | contradição 0.76 |
| AE-T014 | 5 | insufficient_evidence | insufficient_evidence | ✓ | e1 | — | 0.03 | obj 0.57 sta 0.08 pla 0.13 sco 0.08 | e2 0.16/0.59 | e1 superado por e2 (deploy_event mais recente, contra); 2ª passada sem o superado | supported | não provada (partes object 0.57 state 0.08 place 0.13 scope 0.08); contradição possível (0.59) |
| AE-T015 | fácil | supported | supported | ✓ | e1,e2 | e2,e1 | 0.93 | obj 0.98 sta 0.98 pla 0.97 sco 0.94 | e2 0.95/0.03 e1 0.96/0.02 | e2 migration ok; e1 migration ok | supported | provada (partes object 0.98 state 0.98 place 0.97 scope 0.94) |
| AE-T016 | fácil | contradicted | contradicted | ✓ | e2 | e2 | 0.02 | obj 0.98 sta 0.78 pla 0.05 sco 0.05 | e1 0.89/0.12 e2 0.05/0.97 | e1 superado por e2 (deploy_event mais recente, contra) | contradicted | contradição 0.97 |
| AE-T017 | 6 | insufficient_evidence | revisa | ✗ | — | — | 0.05 | obj 0.63 sta 0.38 pla 0.96 sco 0.90 | e1 0.12/0.03 e2 0.16/0.03 | — | supported | dúvida (partes object 0.63 state 0.38 place 0.96 scope 0.90) |
| AE-T018 | 6 | supported | revisa | ✗ | e1 | e1 | 0.09 | obj 0.75 sta 0.32 pla 0.96 sco 0.93 | e1 0.76/0.03 e2 0.42/0.05 | — | supported | dúvida (partes object 0.75 state 0.32 place 0.96 scope 0.93) |
| AE-T019 | difícil: | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.05 | obj 0.82 sta 0.12 pla 0.95 sco 0.73 | e1 0.10/0.07 e2 0.31/0.07 | — | supported | não provada (partes object 0.82 state 0.12 place 0.95 scope 0.73) |
| AE-T020 | 11 | insufficient_evidence | revisa | ✗ | e1 | e1,e2,e3 | 0.24 | obj 0.89 sta 0.83 pla 0.90 sco 0.69 | e1 0.85/0.04 e2 0.51/0.05 e3 0.62/0.05 | — | supported | dúvida (partes object 0.89 state 0.83 place 0.90 scope 0.69) |
| AE-T021 | fácil | supported | revisa | ✗ | e1,e2 | e1,e2 | 0.53 | obj 0.67 sta 0.87 pla 0.93 sco 0.76 | e1 0.73/0.04 e2 0.84/0.04 | — | insufficient_evidence | dúvida (partes object 0.67 state 0.87 place 0.93 scope 0.76) |
| AE-T022 | 7 | contradicted | contradicted | ✓ | e2 | e2 | 0.05 | obj 0.65 sta 0.25 pla 0.92 sco 0.36 | e1 0.68/0.11 e2 0.05/0.84 | — | insufficient_evidence | contradição 0.84 |
| AE-T023 | difícil: | contradicted | contradicted | ✓ | e3 | e3 | 0.04 | obj 0.81 sta 0.68 pla 0.89 sco 0.16 | e1 0.32/0.07 e2 0.07/0.10 e3 0.08/0.95 | — | contradicted | contradição 0.95 |
| AE-T024 | 1 | supported | supported | ✓ | e3 | e3 | 0.83 | obj 0.83 sta 0.95 pla 0.92 sco 0.78 | e2 0.13/0.05 e3 0.87/0.03 | e1 superado por e3 (test_log mais recente, sup); 2ª passada sem o superado | contradicted | provada (partes object 0.83 state 0.95 place 0.92 scope 0.78) |
| AE-T025 | 9 | insufficient_evidence | insufficient_evidence | ✓ | — | e2 | 0.04 | obj 0.93 sta 0.45 pla 0.04 sco 0.41 | e1 0.18/0.15 e2 0.57/0.04 | e1 version ok; e2 version ok | contradicted | não provada (partes object 0.93 state 0.45 place 0.04 scope 0.41) |
| AE-T026 | 5 | insufficient_evidence | insufficient_evidence | ✓ | e1 | e1,e2 | 0.05 | obj 0.95 sta 0.82 pla 0.06 sco 0.37 | e1 0.96/0.05 e2 0.63/0.03 | e1 version ok; e2 version ok | supported | não provada (partes object 0.95 state 0.82 place 0.06 scope 0.37) |
| AE-T027 | 10 | insufficient_evidence | revisa | ✗ | e1 | e1 | 0.79 | obj 0.89 sta 0.82 pla 0.93 sco 0.69 | e1 0.86/0.03 e2 0.06/0.04 | — | supported | dúvida (partes object 0.89 state 0.82 place 0.93 scope 0.69) |
| AE-T028 | fácil | supported | supported | ✓ | e1 | e1 | 0.63 | obj 0.78 sta 0.83 pla 0.90 sco 0.86 | e1 0.77/0.02 e2 0.07/0.04 | — | supported | provada (partes object 0.78 state 0.83 place 0.90 scope 0.86) |
| AE-T029 | 10 | insufficient_evidence | insufficient_evidence | ✓ | e1 | e1 | 0.75 | obj 0.95 sta 0.92 pla 0.97 sco 0.21 | e1 0.80/0.13 e2 0.04/0.04 | — | insufficient_evidence | não provada (partes object 0.95 state 0.92 place 0.97 scope 0.21) |
| AE-T030 | 10 | supported | supported | ✓ | e1 | e1 | 0.91 | obj 0.93 sta 0.93 pla 0.98 sco 0.92 | e1 0.94/0.03 e2 0.04/0.03 | — | insufficient_evidence | provada (partes object 0.93 state 0.93 place 0.98 scope 0.92) |
| AE-T031 | 11 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.09 | obj 0.16 sta 0.13 pla 0.10 sco 0.78 | e1 0.19/0.07 e2 0.05/0.04 | — | insufficient_evidence | não provada (partes object 0.16 state 0.13 place 0.10 scope 0.78) |
| AE-T032 | fácil | supported | revisa | ✗ | e2 | e2 | 0.63 | obj 0.62 sta 0.90 pla 0.91 sco 0.87 | e1 0.22/0.05 e2 0.85/0.04 | — | insufficient_evidence | dúvida (partes object 0.62 state 0.90 place 0.91 scope 0.87) |
| AE-T033 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.06 | obj 0.56 sta 0.04 pla 0.10 sco 0.45 | e1 0.06/0.95 e2 0.07/0.13 | — | contradicted | contradição 0.95 |
| AE-T034 | 12a | supported | supported | ✓ | e1 | e1 | 0.91 | obj 0.84 sta 0.84 pla 0.97 sco 0.77 | e1 0.88/0.16 e2 0.10/0.06 | — | insufficient_evidence | provada (partes object 0.84 state 0.84 place 0.97 scope 0.77) |
| AE-T035 | 12a | contradicted | contradicted | ✓ | e1 | e1 | 0.66 | obj 0.75 sta 0.39 pla 0.90 sco 0.66 | e1 0.47/0.74 e2 0.21/0.20 | — | insufficient_evidence | contradição 0.74 |
| AE-T036 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.01 | obj 0.84 sta 0.03 pla 0.96 sco 0.05 | e1 0.03/0.96 e2 0.04/0.07 | — | contradicted | contradição 0.96 |
| AE-T037 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.88 sta 0.13 pla 0.96 sco 0.04 | e1 0.08/0.95 e2 0.08/0.03 | e1 coverage FALHA | insufficient_evidence | código: e1 coverage lines 84.6% não satisfaz lines > 85% |
| AE-T038 | fácil | supported | supported | ✓ | e1 | e1 | 0.92 | obj 0.87 sta 0.93 pla 0.97 sco 0.94 | e1 0.93/0.02 e2 0.19/0.02 | e1 coverage ok | insufficient_evidence | provada (partes object 0.87 state 0.93 place 0.97 scope 0.94) |
| AE-T039 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.87 sta 0.17 pla 0.96 sco 0.04 | e1 0.07/0.85 e2 0.10/0.03 | e1 coverage FALHA | insufficient_evidence | código: e1 coverage statements 80.0% não satisfaz statements > 80% |
| AE-T040 | 9 | insufficient_evidence | insufficient_evidence | ✓ | e1 | — | 0.03 | obj 0.95 sta 0.52 pla 0.06 sco 0.51 | e1 0.21/0.12 e2 0.11/0.04 | — | contradicted | não provada (partes object 0.95 state 0.52 place 0.06 scope 0.51) |
| AE-T041 | 13 | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.04 | obj 0.07 sta 0.29 pla 0.24 sco 0.50 | e1 0.05/0.05 e2 0.24/0.05 | — | insufficient_evidence | não provada (partes object 0.07 state 0.29 place 0.24 scope 0.50) |
| AE-T042 | 13 | contradicted | contradicted | ✓ | e2 | e2 | 0.02 | obj 0.90 sta 0.42 pla 0.74 sco 0.21 | e1 0.92/0.13 e2 0.08/0.97 | — | contradicted | contradição 0.97 |
| AE-T043 | 13 | supported | insufficient_evidence | ✗ | e1 | e1 | 0.44 | obj 0.96 sta 0.94 pla 0.21 sco 0.89 | e1 0.88/0.07 e2 0.20/0.04 | — | supported | não provada (partes object 0.96 state 0.94 place 0.21 scope 0.89) |
| AE-T044 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.97 sta 0.25 pla 0.45 sco 0.25 | e1 0.05/0.95 e2 0.52/0.08 | — | supported | contradição 0.95 |
| AE-T045 | 2 | contradicted | contradicted | ✓ | e1 | e1 | 0.05 | obj 0.97 sta 0.32 pla 0.72 sco 0.32 | e1 0.35/0.90 e2 0.56/0.17 | — | contradicted | contradição 0.90 |
| AE-T046 | 12b | contradicted | contradicted | ✓ | e1 | e1 | 0.03 | obj 0.93 sta 0.31 pla 0.43 sco 0.08 | e1 0.09/0.94 e2 0.38/0.06 | e1 version FALHA; e2 version ok | supported | código: e1 version 1.9.2 não satisfaz 1.9.3 |
| AE-T047 | fácil | supported | supported | ✓ | e1,e2 | e1,e2 | 0.95 | obj 0.98 sta 0.98 pla 0.97 sco 0.94 | e1 0.98/0.02 e2 0.82/0.02 | e1 version ok; e2 version ok | supported | provada (partes object 0.98 state 0.98 place 0.97 scope 0.94) |
| AE-T048 | 10 | supported | supported | ✓ | e1 | e1 | 0.80 | obj 0.82 sta 0.95 pla 0.95 sco 0.81 | e1 0.80/0.02 e2 0.11/0.04 | — | supported | provada (partes object 0.82 state 0.95 place 0.95 scope 0.81) |
| AE-T049 | difícil: | insufficient_evidence | insufficient_evidence | ✓ | e1 | — | 0.14 | obj 0.83 sta 0.13 pla 0.94 sco 0.14 | e1 0.25/0.28 e2 0.06/0.09 | — | contradicted | não provada (partes object 0.83 state 0.13 place 0.94 scope 0.14) |
| AE-T050 | 10 | insufficient_evidence | insufficient_evidence | ✓ | e1 | e1 | 0.44 | obj 0.81 sta 0.45 pla 0.95 sco 0.27 | e1 0.59/0.45 e2 0.10/0.08 | — | supported | não provada (partes object 0.81 state 0.45 place 0.95 scope 0.27); contradição possível (0.45) |
| AE-T051 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.96 sta 0.29 pla 0.74 sco 0.04 | e1 0.42/0.90 e2 0.44/0.05 | e1 latency FALHA | supported | código: e1 latency 412 ms não satisfaz ms < 300 ms |
| AE-T052 | fácil | supported | revisa | ✗ | e1 | e1,e2 | 0.33 | obj 0.96 sta 0.93 pla 0.81 sco 0.53 | e1 0.73/0.04 e2 0.66/0.03 | e1 latency ok | supported | dúvida (partes object 0.96 state 0.93 place 0.81 scope 0.53) |
| AE-T053 | fácil | supported | supported | ✓ | e1 | e1 | 0.85 | obj 0.93 sta 0.86 pla 0.97 sco 0.89 | e1 0.91/0.03 e2 0.36/0.04 | — | supported | provada (partes object 0.93 state 0.86 place 0.97 scope 0.89) |
| AE-T054 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.92 sta 0.04 pla 0.69 sco 0.03 | e1 0.77/0.90 e2 0.12/0.08 | e1 replicas FALHA | supported | código: e1 replicas 1/1 não satisfaz 3 replicas running |
| AE-T055 | 14 | insufficient_evidence | insufficient_evidence | ✓ | — | e1 | 0.03 | obj 0.93 sta 0.33 pla 0.24 sco 0.26 | e1 0.62/0.07 e2 0.20/0.04 | — | supported | não provada (partes object 0.93 state 0.33 place 0.24 scope 0.26) |
| AE-T056 | 14 | insufficient_evidence | insufficient_evidence | ✓ | e1 | — | 0.03 | obj 0.73 sta 0.03 pla 0.85 sco 0.60 | e1 0.22/0.12 e2 0.08/0.04 | — | supported | não provada (partes object 0.73 state 0.03 place 0.85 scope 0.60) |
| AE-T057 | fácil | supported | supported | ✓ | e2 | e1,e2 | 0.54 | obj 0.84 sta 0.84 pla 0.90 sco 0.85 | e1 0.55/0.04 e2 0.85/0.07 | — | supported | provada (partes object 0.84 state 0.84 place 0.90 scope 0.85) |
| AE-T058 | 8 | contradicted | contradicted | ✓ | e2 | e2 | 0.04 | obj 0.84 sta 0.13 pla 0.64 sco 0.67 | e1 0.10/0.08 e2 0.38/0.78 | — | supported | contradição 0.78 |
| AE-T059 | fácil | supported | supported | ✓ | e1 | e1 | 0.73 | obj 0.75 sta 0.89 pla 0.87 sco 0.86 | e1 0.85/0.03 e2 0.22/0.06 | — | insufficient_evidence | provada (partes object 0.75 state 0.89 place 0.87 scope 0.86) |
| AE-T060 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.70 sta 0.04 pla 0.82 sco 0.37 | e1 0.02/0.95 e2 0.05/0.14 | — | contradicted | contradição 0.95 |
| AE-T061 | 10 | insufficient_evidence | insufficient_evidence | ✓ | e1 | — | 0.11 | obj 0.60 sta 0.51 pla 0.95 sco 0.30 | e1 0.24/0.10 e2 0.05/0.05 | — | supported | não provada (partes object 0.60 state 0.51 place 0.95 scope 0.30) |
| AE-T062 | 9 | insufficient_evidence | insufficient_evidence | ✓ | e1 | — | 0.02 | obj 0.84 sta 0.33 pla 0.04 sco 0.25 | e1 0.16/0.09 e2 0.07/0.10 | — | contradicted | não provada (partes object 0.84 state 0.33 place 0.04 scope 0.25) |
| AE-T063 | difícil: | insufficient_evidence | revisa | ✗ | — | e1 | 0.05 | obj 0.93 sta 0.37 pla 0.94 sco 0.31 | e1 0.79/0.10 e2 0.17/0.05 | — | supported | dúvida (partes object 0.93 state 0.37 place 0.94 scope 0.31) |
| AE-T064 | difícil: | insufficient_evidence | insufficient_evidence | ✓ | — | — | 0.04 | obj 0.64 sta 0.05 pla 0.84 sco 0.23 | e1 0.15/0.08 e2 0.09/0.07 | — | supported | não provada (partes object 0.64 state 0.05 place 0.84 scope 0.23) |
| AE-T065 | fácil | supported | supported | ✓ | e1 | e1 | 0.74 | obj 0.90 sta 0.78 pla 0.75 sco 0.91 | e1 0.94/0.05 e2 0.17/0.04 | — | supported | provada (partes object 0.90 state 0.78 place 0.75 scope 0.91) |
| AE-T066 | fácil | contradicted | contradicted | ✓ | e1 | e1 | 0.02 | obj 0.88 sta 0.02 pla 0.88 sco 0.22 | e1 0.03/0.96 e2 0.05/0.10 | — | contradicted | contradição 0.96 |
| AE-T067 | fácil | supported | supported | ✓ | e1 | e1,e2 | 0.77 | obj 0.96 sta 0.96 pla 0.95 sco 0.88 | e1 0.97/0.02 e2 0.61/0.03 | e1 version ok; e2 version ok | supported | provada (partes object 0.96 state 0.96 place 0.95 scope 0.88) |
| AE-T068 | difícil: | contradicted | contradicted | ✓ | e1 | e1 | 0.33 | obj 0.96 sta 0.77 pla 0.94 sco 0.50 | e1 0.93/0.71 e2 0.59/0.04 | e1 version ok; e2 version ok | contradicted | contradição 0.71 |
| AE-T069 | difícil: | insufficient_evidence | supported | ✗ | e1 | e1,e2 | 0.62 | obj 0.97 sta 0.92 pla 0.95 sco 0.81 | e1 0.95/0.03 e2 0.64/0.03 | e1 version ok; e2 version ok | supported | provada (partes object 0.97 state 0.92 place 0.95 scope 0.81) |
| AE-T070 | 6 | contradicted | contradicted | ✓ | e2 | e2 | 0.02 | obj 0.84 sta 0.30 pla 0.06 sco 0.17 | e1 0.88/0.10 e2 0.03/0.89 | — | supported | contradição 0.89 |
| AE-T071 | 5 | insufficient_evidence | insufficient_evidence | ✓ | e1 | e1 | 0.04 | obj 0.84 sta 0.38 pla 0.05 sco 0.22 | e1 0.88/0.05 e2 0.17/0.04 | — | contradicted | não provada (partes object 0.84 state 0.38 place 0.05 scope 0.22) |
| AE-T072 | difícil: | insufficient_evidence | insufficient_evidence | ✓ | e1 | — | 0.13 | obj 0.82 sta 0.21 pla 0.94 sco 0.64 | e1 0.30/0.08 e2 0.22/0.05 | — | supported | não provada (partes object 0.82 state 0.21 place 0.94 scope 0.64) |
| AE-T073 | fácil | supported | supported | ✓ | e1 | e1 | 0.76 | obj 0.92 sta 0.89 pla 0.96 sco 0.90 | e1 0.84/0.04 e2 0.26/0.04 | — | supported | provada (partes object 0.92 state 0.89 place 0.96 scope 0.90) |
