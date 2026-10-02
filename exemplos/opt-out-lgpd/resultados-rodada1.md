# Resultados — opt-out-lgpd

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; validação, ação e baseline: `optout.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Teto da mensagem: 2000 caracteres (acima → revisar, sem chamada). Isto não é parecer jurídico.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (60 mensagens), com a política acima; **1_infracao**: opt-out ou pedido LGPD real que saiu `seguir` = 0; **2_obrigacao_pela_metade**: opt-out real → `pausar`, pedido LGPD real sem pedido aberto, ou pedido aberto sem bloqueio ≤ 1; **3_bloqueio_indevido**: mensagem sem opt-out nem LGPD com envio bloqueado ≤ 1/28 (3,6%); **4_acerto_acao**: ação (5 classes) ≥ baseline + 0,15; **secundario_nao_decide**: `opt_out` nulo → `revisar`; revisou sem necessidade ≤ 15% dos decidíveis; tipo LGPD certo ≥ 85% dos pedidos reais; **se_falhar**: 1, 2 ou 3 falhando = o desenho não serve como guarda de entrada sem mudança; 4 falhando = a lista de expressões basta

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T13:07:34-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 bd839986d8b3eab0… · `optout.py` sha256 99515b087057bdad… · `run.py` sha256 2695bda4d2ae0edf… · `dados/teste.json` sha256 1207d0b7d4d14d6a…

## Lado a lado

### Ação por variante e conjunto

| conjunto | variante | n | acerto_acao | INFRAÇÃO (opt-out/LGPD real → seguir) | obrigação pela metade | BLOQUEIO INDEVIDO (sem opt-out nem LGPD → bloqueia) | bloqueou c/ opt_out falso (todos) | null → revisar | revisou sem necessidade | tipo LGPD certo (pedidos reais) |
|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | baseline (expressões) | 30 | 0.733 | 2/14 | 0/14 | 3/14 | 3/20 | 0/2 | 0/28 | 8/9 |
| ajuste | sempre revisa | 30 | 0.067 | 0/14 | 0/14 | 0/14 | 0/20 | 2/2 | 28/28 | 0/9 |
| ajuste | Jev | 30 | 0.967 | 0/14 | 0/14 | 0/14 | 0/20 | 2/2 | 1/28 | 9/9 |
| teste | baseline (expressões) | 60 | 0.717 | 4/31 | 1/31 | 5/28 | 6/40 | 0/1 | 0/59 | 14/18 |
| teste | sempre revisa | 60 | 0.017 | 0/31 | 0/31 | 0/28 | 0/40 | 1/1 | 59/59 | 0/18 |
| teste | Jev | 60 | 0.883 | 0/31 | 0/31 | 0/28 | 0/40 | 1/1 | 6/59 | 16/18 |

### Perguntas, tipo, custo

| conjunto | n | difíceis | nulos | opt_out ≥0,5 | temporary_pause ≥0,5 | lgpd_request ≥0,5 | opt_out (sem exclusões) ≥0,5 | bloqueio composto Jev | bloqueio composto baseline | tipo LGPD (Choice crua) | tipo baseline | p50_ms | p95_ms | tokens_por_mensagem | US$_por_1000 | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | 30 | 15 | 2 | 0.964 | 1.000 | 1.000 | 0.960 | 0.964 | 0.857 | 1.000 | 0.889 | 299 | 393 | 2026 | 0.0851 | jev-1.13.0 |
| teste | 60 | 30 | 1 | 0.983 | 1.000 | 0.950 | 1.000 | 0.898 | 0.881 | 0.944 | 0.778 | 324 | 663 | 2028 | 0.0852 | jev-1.13.0 |

## Conjunto `ajuste` — 30 mensagens (arquivo versão 2026-10-01, autor fable); 15 difíceis, 2 com `opt_out` nulo

### Ação (5 classes) — métrica principal, baseline × sempre revisa × Jev nos mesmos casos

Gabarito da ação: `pedido_lgpd` → `abrir_pedido_lgpd`; `opt_out` nulo → `revisar`; `opt_out` → `bloquear_envios`; `pausa_temporaria` → `pausar`; senão `seguir`. **INFRAÇÃO** = opt-out ou pedido LGPD real que saiu `seguir`. `obrigação pela metade` = sem `seguir` e sem `revisar`, mas a obrigação não foi cumprida inteira: opt-out real → `pausar`; pedido LGPD real sem `abrir_pedido_lgpd`; pedido aberto sem bloquear quem também pediu para parar. **BLOQUEIO INDEVIDO** = mensagem sem opt-out nem pedido LGPD (cliente interessado, pausa, preferência, filtro) cujo envio foi bloqueado. `sempre revisa` = o custo de evitar todo erro: zero infração, 100% das mensagens a humano. `tipo LGPD certo` = pedido aberto com o tipo do gabarito, sobre os pedidos reais.

| variante | n | acerto_acao | INFRAÇÃO (opt-out/LGPD real → seguir) | obrigação pela metade | BLOQUEIO INDEVIDO (sem opt-out nem LGPD → bloqueia) | bloqueou c/ opt_out falso (todos) | null → revisar | revisou sem necessidade | tipo LGPD certo (pedidos reais) |
|---|---|---|---|---|---|---|---|---|---|
| baseline (expressões) | 30 | 0.733 | 2/14 | 0/14 | 3/14 | 3/20 | 0/2 | 0/28 | 8/9 |
| sempre revisa | 30 | 0.067 | 0/14 | 0/14 | 0/14 | 0/20 | 2/2 | 28/28 | 0/9 |
| Jev | 30 | 0.967 | 0/14 | 0/14 | 0/14 | 0/20 | 2/2 | 1/28 | 9/9 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 infração | 0/14 | ≤ 0 | ✓ |
| 2 obrigação pela metade | 0/14 | ≤ 1 | ✓ |
| 3 bloqueio indevido | 0/14 | ≤ 1 | ✓ |
| 4 acerto da ação | 0.967 (baseline 0.733) | ≥ 0.883 | ✓ |
| secundário: nulo → revisar | 2/2 | todos | ✓ |
| secundário: revisou sem necessidade | 1/28 (0.036) | ≤ 0.15 | ✓ |
| secundário: tipo LGPD certo | 9/9 (1.000) | ≥ 0.85 | ✓ |

**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | bloquear_envios | abrir_pedido_lgpd | pausar | seguir | revisar |
|---|---|---|---|---|---|
| bloquear_envios | 4 | 0 | 0 | 0 | 1 |
| abrir_pedido_lgpd | 0 | 9 | 0 | 0 | 0 |
| pausar | 0 | 0 | 4 | 0 | 0 |
| seguir | 0 | 0 | 0 | 10 | 0 |
| revisar | 0 | 0 | 0 | 0 | 2 |

**Matriz de confusão — baseline**

| gabarito ↓ / previsto → | bloquear_envios | abrir_pedido_lgpd | pausar | seguir | revisar |
|---|---|---|---|---|---|
| bloquear_envios | 4 | 0 | 0 | 1 | 0 |
| abrir_pedido_lgpd | 0 | 8 | 0 | 1 | 0 |
| pausar | 1 | 0 | 3 | 0 | 0 |
| seguir | 2 | 0 | 1 | 7 | 0 |
| revisar | 2 | 0 | 0 | 0 | 0 |

### Nouls principais — acerto (≥ 0,5) contra o gabarito, faixa atual e Brier

`opt_out` é o pedido EXPLÍCITO de parar: nas exclusões o gabarito é `true` por regra de código (exclusão ⇒ opt-out), por isso há a linha sem os casos de exclusão. Gabarito nulo fica fora. `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela.

| noul | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|
| opt_out | 0.964 | 0.2–0.7 | 0.929 | 1.000 | 2 | 28 | 0.025 |
| temporary_pause | 1.000 | 0.4–0.6 | 0.967 | 1.000 | 1 | 30 | 0.014 |
| lgpd_request | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 30 | 0.005 |
| opt_out (sem exclusões) | 0.960 | 0.2–0.7 | 0.960 | 1.000 | 1 | 25 | 0.020 |

**`opt_out` composto** (bloqueio decidido pelo código: Noul + regra exclusão ⇒ opt-out; dúvida/`revisar` conta como erro aqui): Jev 0.964 · baseline 0.857 (n = 28)

### Nouls de guarda — valores por grupo (não têm campo próprio no gabarito)

| noul | grupo | n_grupo | mín–máx no grupo | mín–máx fora | fora ≥ sim | faixa |
|---|---|---|---|---|---|---|
| stop_without_object | `opt_out` nulo | 2 | 0.96–0.97 | 0.01–0.16 | 0 | 0.2–0.5 |
| wants_contact_to_continue | família negação | 2 | 0.06–0.93 | 0.01–0.87 | 4 | 0.2–0.7 |
| about_another_contact | família terceiro | 3 | 0.04–0.88 | 0.01–0.10 | 0 | 0.2–0.7 |

### Tipo LGPD — Choice `lgpd_type` entre os 9 pedidos reais

| Choice crua (vencedor) | na ação (pedido aberto com o tipo certo) | baseline | n | Choice ≠ none sem pedido real | piso de confiança |
|---|---|---|---|---|---|
| 1.000 | 1.000 | 0.889 | 9 | 2/21 | 0.500 |

| gabarito ↓ / Choice → | exclusao | origem_dos_dados | acesso | correcao | None |
|---|---|---|---|---|---|
| exclusao | 3 | 0 | 0 | 0 | 0 |
| origem_dos_dados | 0 | 2 | 0 | 0 | 0 |
| acesso | 0 | 0 | 2 | 0 | 0 |
| correcao | 0 | 0 | 0 | 2 | 0 |

**Cobertura × erro por confiança da Choice** (pedidos reais)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 9 |
| 0.300 | 1.000 | 0.000 | 9 |
| 0.500 | 1.000 | 0.000 | 9 |
| 0.700 | 1.000 | 0.000 | 9 |
| 0.900 | 1.000 | 0.000 | 9 |

### Por família difícil (pela `nota` do rotulador)

| família | n | ação Jev | ação baseline | Jev → revisar | obrigação perdida Jev | bloqueio indevido Jev | obrigação perdida baseline |
|---|---|---|---|---|---|---|---|
| negação | 2 | 1.000 | 0.500 | 0 | 0 | 0 | 0 |
| ironia | 2 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| terceiro | 3 | 0.667 | 0.667 | 1 | 0 | 0 | 1 |
| pausa × opt-out | 2 | 1.000 | 0.500 | 0 | 0 | 0 | 0 |
| reclamação longa | 1 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| origem sem pedir exclusão | 1 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| 'para' ambíguo | 3 | 1.000 | 0.000 | 2 | 0 | 0 | 0 |
| fim de interesse sem pedido de parar | 1 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| fácil / outros | 15 | 1.000 | 0.867 | 0 | 0 | 0 | 1 |

### Cobertura × erro por faixa

**Política inteira** (mesmas respostas, outra faixa nos três Nouls principais; informativo no teste)

| faixa (3 Nouls principais) | cobertura_auto | erro_automatico | infrações | obrigação pela metade | bloqueios indevidos | n_auto |
|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.900 | 0.000 | 0 | 0 | 0 | 27 |
| 0.5–0.5 | 0.933 | 0.036 | 1 | 0 | 0 | 28 |
| 0.4–0.6 | 0.933 | 0.036 | 1 | 0 | 0 | 28 |
| 0.3–0.7 | 0.900 | 0.000 | 0 | 0 | 0 | 27 |
| 0.2–0.8 | 0.800 | 0.000 | 0 | 0 | 0 | 24 |
| 0.1–0.9 | 0.600 | 0.000 | 0 | 0 | 0 | 18 |

**Cada Noul principal sozinho** (cobertura = decidido fora da faixa; acerto entre os decididos)

| noul | faixa | cobertura | acerto_decididos | revisao | n |
|---|---|---|---|---|---|
| opt_out (sem exclusões) | 0.5–0.5 | 1.000 | 0.960 | 0 | 25 |
| opt_out (sem exclusões) | 0.4–0.6 | 1.000 | 0.960 | 0 | 25 |
| opt_out (sem exclusões) | 0.3–0.7 | 0.960 | 1.000 | 1 | 25 |
| opt_out (sem exclusões) | 0.2–0.8 | 0.960 | 1.000 | 1 | 25 |
| opt_out (sem exclusões) | 0.1–0.9 | 0.800 | 1.000 | 5 | 25 |
| temporary_pause | 0.5–0.5 | 1.000 | 1.000 | 0 | 30 |
| temporary_pause | 0.4–0.6 | 0.967 | 1.000 | 1 | 30 |
| temporary_pause | 0.3–0.7 | 0.967 | 1.000 | 1 | 30 |
| temporary_pause | 0.2–0.8 | 0.900 | 1.000 | 3 | 30 |
| temporary_pause | 0.1–0.9 | 0.833 | 1.000 | 5 | 30 |
| lgpd_request | 0.5–0.5 | 1.000 | 1.000 | 0 | 30 |
| lgpd_request | 0.4–0.6 | 1.000 | 1.000 | 0 | 30 |
| lgpd_request | 0.3–0.7 | 1.000 | 1.000 | 0 | 30 |
| lgpd_request | 0.2–0.8 | 0.967 | 1.000 | 1 | 30 |
| lgpd_request | 0.1–0.9 | 0.900 | 1.000 | 3 | 30 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | mensagens_longas (sem chamada) | perguntas | p50_ms | p95_ms | tokens_por_mensagem | US$_total | US$_por_1000_mensagens | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 30 | 0 | 0 | 210 | 299 | 393 | 2026 | 0.002552 | 0.0851 | jev-1.13.0 |

### Caso a caso

`opt`/`pausa`/`lgpd` = Nouls `opt_out`, `temporary_pause`, `lgpd_request`; `tipo` = vencedor da Choice (confiança); `cont`/`s/obj`/`terc` = guardas `wants_contact_to_continue`, `stop_without_object`, `about_another_contact`; `ok` compara a ação do Jev com o gabarito; `caro` marca obrigação perdida ou bloqueio indevido; `base` = baseline.

| id | fam | gab | opt | pausa | lgpd | tipo | cont | s/obj | terc | ação Jev | bloq | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OL-A001 | fácil / outros | bloquear_envios | 0.80 | 0.04 | 0.03 | none (0.98) | 0.01 | 0.03 | 0.08 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-A002 | fácil / outros | seguir | 0.01 | 0.01 | 0.01 | none (1.00) | 0.04 | 0.01 | 0.01 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-A003 | negação | seguir | 0.05 | 0.06 | 0.03 | none (0.95) | 0.93 | 0.02 | 0.10 | seguir | não | ✓ |  | bloquear_envios | nenhum pedido de parar, pausar ou de titular |
| OL-A004 | ironia | bloquear_envios | 0.87 | 0.05 | 0.04 | none (0.96) | 0.03 | 0.04 | 0.10 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-A005 | terceiro | seguir | 0.16 | 0.03 | 0.06 | none (0.96) | 0.10 | 0.03 | 0.88 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-A006 | terceiro | bloquear_envios | 0.40 | 0.03 | 0.19 | deletion (0.60) | 0.05 | 0.03 | 0.48 | revisar | ? | ✗ |  | seguir | dúvida de opt-out (0.40) |
| OL-A007 | fácil / outros | abrir_pedido_lgpd(acesso) | 0.01 | 0.01 | 0.99 | access (1.00) | 0.03 | 0.01 | 0.01 | abrir_pedido_lgpd(acesso) | não | ✓ |  | abrir_pedido_lgpd(acesso) | direito de titular: acesso |
| OL-A008 | fácil / outros | abrir_pedido_lgpd(correcao) | 0.01 | 0.01 | 0.98 | correction (1.00) | 0.15 | 0.01 | 0.01 | abrir_pedido_lgpd(correcao) | não | ✓ |  | abrir_pedido_lgpd(correcao) | direito de titular: correcao |
| OL-A009 | fácil / outros | pausar | 0.03 | 0.72 | 0.01 | none (1.00) | 0.08 | 0.03 | 0.02 | pausar | não | ✓ |  | pausar | pausa com retomada |
| OL-A010 | pausa × opt-out | bloquear_envios | 0.94 | 0.46 | 0.07 | none (0.89) | 0.01 | 0.16 | 0.09 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-A011 | reclamação longa | abrir_pedido_lgpd(exclusao) | 0.91 | 0.03 | 0.91 | deletion (1.00) | 0.01 | 0.02 | 0.03 | abrir_pedido_lgpd(exclusao) | sim | ✓ |  | abrir_pedido_lgpd(exclusao) | direito de titular: exclusao |
| OL-A012 | origem sem pedir exclusão | abrir_pedido_lgpd(origem_dos_dados) | 0.02 | 0.02 | 0.96 | data_source (1.00) | 0.03 | 0.01 | 0.02 | abrir_pedido_lgpd(origem_dos_dados) | não | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | direito de titular: origem_dos_dados |
| OL-A013 | fácil / outros | seguir | 0.02 | 0.12 | 0.02 | none (1.00) | 0.07 | 0.01 | 0.01 | seguir | não | ✓ |  | pausar | nenhum pedido de parar, pausar ou de titular |
| OL-A014 | 'para' ambíguo | revisar | 0.07 | 0.03 | 0.05 | none (0.99) | 0.11 | 0.96 | 0.03 | revisar | ? | ✓ |  | bloquear_envios | 'para' / 'não quero mais' sem dizer o quê |
| OL-A015 | 'para' ambíguo | seguir | 0.09 | 0.04 | 0.04 | none (0.92) | 0.13 | 0.03 | 0.08 | seguir | não | ✓ |  | bloquear_envios | nenhum pedido de parar, pausar ou de titular |
| OL-A016 | fácil / outros | abrir_pedido_lgpd(exclusao) | 0.89 | 0.03 | 0.97 | deletion (0.99) | 0.01 | 0.02 | 0.04 | abrir_pedido_lgpd(exclusao) | sim | ✓ |  | abrir_pedido_lgpd(exclusao) | direito de titular: exclusao |
| OL-A017 | fácil / outros | pausar | 0.03 | 0.86 | 0.02 | none (1.00) | 0.09 | 0.01 | 0.03 | pausar | não | ✓ |  | pausar | pausa com retomada |
| OL-A018 | fácil / outros | seguir | 0.01 | 0.01 | 0.01 | none (1.00) | 0.87 | 0.01 | 0.02 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-A019 | 'para' ambíguo | revisar | 0.33 | 0.04 | 0.11 | none (0.92) | 0.02 | 0.97 | 0.07 | revisar | ? | ✓ |  | bloquear_envios | dúvida de opt-out (0.33) |
| OL-A020 | fácil / outros | abrir_pedido_lgpd(correcao) | 0.03 | 0.01 | 0.98 | correction (1.00) | 0.58 | 0.01 | 0.03 | abrir_pedido_lgpd(correcao) | não | ✓ |  | abrir_pedido_lgpd(correcao) | direito de titular: correcao |
| OL-A021 | negação | seguir | 0.04 | 0.21 | 0.05 | none (0.59) | 0.06 | 0.01 | 0.04 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-A022 | fácil / outros | abrir_pedido_lgpd(exclusao) | 0.59 | 0.02 | 0.97 | deletion (1.00) | 0.01 | 0.02 | 0.03 | abrir_pedido_lgpd(exclusao) | sim | ✓ |  | abrir_pedido_lgpd(exclusao) | direito de titular: exclusao |
| OL-A023 | fácil / outros | seguir | 0.08 | 0.06 | 0.03 | none (0.97) | 0.77 | 0.03 | 0.04 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-A024 | ironia | seguir | 0.03 | 0.02 | 0.06 | none (0.84) | 0.85 | 0.01 | 0.03 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-A025 | fácil / outros | abrir_pedido_lgpd(origem_dos_dados) | 0.07 | 0.02 | 0.97 | data_source (1.00) | 0.03 | 0.01 | 0.05 | abrir_pedido_lgpd(origem_dos_dados) | não | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | direito de titular: origem_dos_dados |
| OL-A026 | fim de interesse sem pedido de parar | seguir | 0.16 | 0.03 | 0.05 | none (0.99) | 0.02 | 0.15 | 0.05 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-A027 | fácil / outros | pausar | 0.03 | 0.94 | 0.02 | none (1.00) | 0.07 | 0.04 | 0.03 | pausar | não | ✓ |  | pausar | pausa com retomada |
| OL-A028 | fácil / outros | abrir_pedido_lgpd(acesso) | 0.01 | 0.01 | 0.93 | access (1.00) | 0.03 | 0.01 | 0.01 | abrir_pedido_lgpd(acesso) | não | ✓ |  | seguir | direito de titular: acesso |
| OL-A029 | terceiro | bloquear_envios | 0.96 | 0.10 | 0.21 | deletion (0.68) | 0.02 | 0.02 | 0.04 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-A030 | pausa × opt-out | pausar | 0.05 | 0.95 | 0.03 | none (0.90) | 0.82 | 0.02 | 0.06 | pausar | não | ✓ |  | bloquear_envios | pausa com retomada |

## Conjunto `teste` — 60 mensagens (arquivo versão 2026-10-01, autor fable); 30 difíceis, 1 com `opt_out` nulo

### Ação (5 classes) — métrica principal, baseline × sempre revisa × Jev nos mesmos casos

Gabarito da ação: `pedido_lgpd` → `abrir_pedido_lgpd`; `opt_out` nulo → `revisar`; `opt_out` → `bloquear_envios`; `pausa_temporaria` → `pausar`; senão `seguir`. **INFRAÇÃO** = opt-out ou pedido LGPD real que saiu `seguir`. `obrigação pela metade` = sem `seguir` e sem `revisar`, mas a obrigação não foi cumprida inteira: opt-out real → `pausar`; pedido LGPD real sem `abrir_pedido_lgpd`; pedido aberto sem bloquear quem também pediu para parar. **BLOQUEIO INDEVIDO** = mensagem sem opt-out nem pedido LGPD (cliente interessado, pausa, preferência, filtro) cujo envio foi bloqueado. `sempre revisa` = o custo de evitar todo erro: zero infração, 100% das mensagens a humano. `tipo LGPD certo` = pedido aberto com o tipo do gabarito, sobre os pedidos reais.

| variante | n | acerto_acao | INFRAÇÃO (opt-out/LGPD real → seguir) | obrigação pela metade | BLOQUEIO INDEVIDO (sem opt-out nem LGPD → bloqueia) | bloqueou c/ opt_out falso (todos) | null → revisar | revisou sem necessidade | tipo LGPD certo (pedidos reais) |
|---|---|---|---|---|---|---|---|---|---|
| baseline (expressões) | 60 | 0.717 | 4/31 | 1/31 | 5/28 | 6/40 | 0/1 | 0/59 | 14/18 |
| sempre revisa | 60 | 0.017 | 0/31 | 0/31 | 0/28 | 0/40 | 1/1 | 59/59 | 0/18 |
| Jev | 60 | 0.883 | 0/31 | 0/31 | 0/28 | 0/40 | 1/1 | 6/59 | 16/18 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 infração | 0/31 | ≤ 0 | ✓ |
| 2 obrigação pela metade | 0/31 | ≤ 1 | ✓ |
| 3 bloqueio indevido | 0/28 | ≤ 1 | ✓ |
| 4 acerto da ação | 0.883 (baseline 0.717) | ≥ 0.867 | ✓ |
| secundário: nulo → revisar | 1/1 | todos | ✓ |
| secundário: revisou sem necessidade | 6/59 (0.102) | ≤ 0.15 | ✓ |
| secundário: tipo LGPD certo | 16/18 (0.889) | ≥ 0.85 | ✓ |

**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | bloquear_envios | abrir_pedido_lgpd | pausar | seguir | revisar |
|---|---|---|---|---|---|
| bloquear_envios | 10 | 1 | 0 | 0 | 2 |
| abrir_pedido_lgpd | 0 | 17 | 0 | 0 | 1 |
| pausar | 0 | 0 | 5 | 0 | 2 |
| seguir | 0 | 0 | 0 | 20 | 1 |
| revisar | 0 | 0 | 0 | 0 | 1 |

**Matriz de confusão — baseline**

| gabarito ↓ / previsto → | bloquear_envios | abrir_pedido_lgpd | pausar | seguir | revisar |
|---|---|---|---|---|---|
| bloquear_envios | 11 | 1 | 0 | 1 | 0 |
| abrir_pedido_lgpd | 1 | 14 | 0 | 3 | 0 |
| pausar | 1 | 0 | 1 | 5 | 0 |
| seguir | 4 | 0 | 0 | 17 | 0 |
| revisar | 1 | 0 | 0 | 0 | 0 |

### Nouls principais — acerto (≥ 0,5) contra o gabarito, faixa atual e Brier

`opt_out` é o pedido EXPLÍCITO de parar: nas exclusões o gabarito é `true` por regra de código (exclusão ⇒ opt-out), por isso há a linha sem os casos de exclusão. Gabarito nulo fica fora. `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela.

| noul | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|
| opt_out | 0.983 | 0.2–0.7 | 0.915 | 0.981 | 5 | 59 | 0.034 |
| temporary_pause | 1.000 | 0.4–0.6 | 1.000 | 1.000 | 0 | 60 | 0.007 |
| lgpd_request | 0.950 | 0.3–0.7 | 0.950 | 0.982 | 3 | 60 | 0.028 |
| opt_out (sem exclusões) | 1.000 | 0.2–0.7 | 0.925 | 1.000 | 4 | 53 | 0.018 |

**`opt_out` composto** (bloqueio decidido pelo código: Noul + regra exclusão ⇒ opt-out; dúvida/`revisar` conta como erro aqui): Jev 0.898 · baseline 0.881 (n = 59)

### Nouls de guarda — valores por grupo (não têm campo próprio no gabarito)

| noul | grupo | n_grupo | mín–máx no grupo | mín–máx fora | fora ≥ sim | faixa |
|---|---|---|---|---|---|---|
| stop_without_object | `opt_out` nulo | 1 | 0.91–0.91 | 0.01–0.12 | 0 | 0.2–0.5 |
| wants_contact_to_continue | família negação | 5 | 0.24–0.92 | 0.01–0.93 | 6 | 0.2–0.7 |
| about_another_contact | família terceiro | 5 | 0.09–0.79 | 0.01–0.17 | 0 | 0.2–0.7 |

### Tipo LGPD — Choice `lgpd_type` entre os 18 pedidos reais

| Choice crua (vencedor) | na ação (pedido aberto com o tipo certo) | baseline | n | Choice ≠ none sem pedido real | piso de confiança |
|---|---|---|---|---|---|
| 0.944 | 0.889 | 0.778 | 18 | 5/42 | 0.500 |

| gabarito ↓ / Choice → | exclusao | origem_dos_dados | acesso | correcao | None |
|---|---|---|---|---|---|
| exclusao | 6 | 0 | 0 | 0 | 0 |
| origem_dos_dados | 1 | 4 | 0 | 0 | 0 |
| acesso | 0 | 0 | 4 | 0 | 0 |
| correcao | 0 | 0 | 0 | 3 | 0 |

**Cobertura × erro por confiança da Choice** (pedidos reais)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.056 | 18 |
| 0.300 | 1.000 | 0.056 | 18 |
| 0.500 | 1.000 | 0.056 | 18 |
| 0.700 | 1.000 | 0.056 | 18 |
| 0.900 | 0.889 | 0.000 | 16 |

### Por família difícil (pela `nota` do rotulador)

| família | n | ação Jev | ação baseline | Jev → revisar | obrigação perdida Jev | bloqueio indevido Jev | obrigação perdida baseline |
|---|---|---|---|---|---|---|---|
| negação | 5 | 1.000 | 0.400 | 0 | 0 | 0 | 0 |
| ironia | 3 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| terceiro | 5 | 0.600 | 0.800 | 2 | 0 | 0 | 1 |
| pausa × opt-out | 4 | 0.750 | 0.500 | 1 | 0 | 0 | 0 |
| 'para' ambíguo | 3 | 0.667 | 0.333 | 2 | 0 | 0 | 0 |
| fim de interesse sem pedido de parar | 1 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| reclamação longa | 2 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| tipo | 3 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| dois pedidos | 1 | 1.000 | 0.000 | 0 | 0 | 0 | 1 |
| origem sem pedir exclusão | 2 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| exclusão parcial | 1 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| fácil / outros | 30 | 0.900 | 0.733 | 2 | 0 | 0 | 3 |

### Cobertura × erro por faixa

**Política inteira** (mesmas respostas, outra faixa nos três Nouls principais; informativo no teste)

| faixa (3 Nouls principais) | cobertura_auto | erro_automatico | infrações | obrigação pela metade | bloqueios indevidos | n_auto |
|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.883 | 0.019 | 0 | 0 | 0 | 53 |
| 0.5–0.5 | 0.983 | 0.051 | 0 | 1 | 0 | 59 |
| 0.4–0.6 | 0.917 | 0.018 | 0 | 0 | 0 | 55 |
| 0.3–0.7 | 0.867 | 0.019 | 0 | 0 | 0 | 52 |
| 0.2–0.8 | 0.733 | 0.000 | 0 | 0 | 0 | 44 |
| 0.1–0.9 | 0.600 | 0.000 | 0 | 0 | 0 | 36 |

**Cada Noul principal sozinho** (cobertura = decidido fora da faixa; acerto entre os decididos)

| noul | faixa | cobertura | acerto_decididos | revisao | n |
|---|---|---|---|---|---|
| opt_out (sem exclusões) | 0.5–0.5 | 1.000 | 1.000 | 0 | 53 |
| opt_out (sem exclusões) | 0.4–0.6 | 0.962 | 1.000 | 2 | 53 |
| opt_out (sem exclusões) | 0.3–0.7 | 0.943 | 1.000 | 3 | 53 |
| opt_out (sem exclusões) | 0.2–0.8 | 0.887 | 1.000 | 6 | 53 |
| opt_out (sem exclusões) | 0.1–0.9 | 0.755 | 1.000 | 13 | 53 |
| temporary_pause | 0.5–0.5 | 1.000 | 1.000 | 0 | 60 |
| temporary_pause | 0.4–0.6 | 1.000 | 1.000 | 0 | 60 |
| temporary_pause | 0.3–0.7 | 0.967 | 1.000 | 2 | 60 |
| temporary_pause | 0.2–0.8 | 0.933 | 1.000 | 4 | 60 |
| temporary_pause | 0.1–0.9 | 0.933 | 1.000 | 4 | 60 |
| lgpd_request | 0.5–0.5 | 1.000 | 0.950 | 0 | 60 |
| lgpd_request | 0.4–0.6 | 0.967 | 0.983 | 2 | 60 |
| lgpd_request | 0.3–0.7 | 0.950 | 0.982 | 3 | 60 |
| lgpd_request | 0.2–0.8 | 0.900 | 1.000 | 6 | 60 |
| lgpd_request | 0.1–0.9 | 0.850 | 1.000 | 9 | 60 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | mensagens_longas (sem chamada) | perguntas | p50_ms | p95_ms | tokens_por_mensagem | US$_total | US$_por_1000_mensagens | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 60 | 60 | 0 | 420 | 324 | 663 | 2028 | 0.005110 | 0.0852 | jev-1.13.0 |

### Caso a caso

`opt`/`pausa`/`lgpd` = Nouls `opt_out`, `temporary_pause`, `lgpd_request`; `tipo` = vencedor da Choice (confiança); `cont`/`s/obj`/`terc` = guardas `wants_contact_to_continue`, `stop_without_object`, `about_another_contact`; `ok` compara a ação do Jev com o gabarito; `caro` marca obrigação perdida ou bloqueio indevido; `base` = baseline.

| id | fam | gab | opt | pausa | lgpd | tipo | cont | s/obj | terc | ação Jev | bloq | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OL-T001 | fácil / outros | bloquear_envios | 0.90 | 0.04 | 0.04 | none (0.98) | 0.01 | 0.09 | 0.06 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-T002 | fácil / outros | seguir | 0.01 | 0.01 | 0.01 | none (1.00) | 0.04 | 0.01 | 0.01 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T003 | fácil / outros | bloquear_envios | 0.85 | 0.05 | 0.04 | none (0.96) | 0.01 | 0.02 | 0.05 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-T004 | fácil / outros | abrir_pedido_lgpd(origem_dos_dados) | 0.02 | 0.02 | 0.97 | data_source (1.00) | 0.03 | 0.01 | 0.03 | abrir_pedido_lgpd(origem_dos_dados) | não | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | direito de titular: origem_dos_dados |
| OL-T005 | fácil / outros | pausar | 0.04 | 0.96 | 0.02 | none (1.00) | 0.26 | 0.09 | 0.09 | pausar | não | ✓ |  | seguir | pausa com retomada |
| OL-T006 | fácil / outros | abrir_pedido_lgpd(exclusao) | 0.05 | 0.02 | 0.98 | deletion (1.00) | 0.02 | 0.02 | 0.02 | abrir_pedido_lgpd(exclusao) | sim | ✓ |  | abrir_pedido_lgpd(exclusao) | direito de titular: exclusao |
| OL-T007 | fácil / outros | abrir_pedido_lgpd(correcao) | 0.01 | 0.01 | 0.98 | correction (1.00) | 0.04 | 0.01 | 0.01 | abrir_pedido_lgpd(correcao) | não | ✓ |  | abrir_pedido_lgpd(correcao) | direito de titular: correcao |
| OL-T008 | negação | seguir | 0.03 | 0.06 | 0.03 | none (0.95) | 0.92 | 0.03 | 0.17 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T009 | ironia | bloquear_envios | 0.97 | 0.04 | 0.10 | none (0.42) | 0.01 | 0.03 | 0.03 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-T010 | terceiro | seguir | 0.05 | 0.03 | 0.04 | none (0.93) | 0.93 | 0.02 | 0.79 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T011 | terceiro | abrir_pedido_lgpd(exclusao) | 0.92 | 0.04 | 0.43 | deletion (0.76) | 0.01 | 0.03 | 0.12 | revisar | ? | ✗ |  | abrir_pedido_lgpd(exclusao) | dúvida se há pedido de titular (0.43) |
| OL-T012 | pausa × opt-out | pausar | 0.03 | 0.69 | 0.02 | none (1.00) | 0.24 | 0.02 | 0.02 | pausar | não | ✓ |  | seguir | pausa com retomada |
| OL-T013 | fácil / outros | abrir_pedido_lgpd(exclusao) | 0.91 | 0.03 | 0.95 | deletion (1.00) | 0.01 | 0.03 | 0.03 | abrir_pedido_lgpd(exclusao) | sim | ✓ |  | abrir_pedido_lgpd(exclusao) | direito de titular: exclusao |
| OL-T014 | fácil / outros | seguir | 0.01 | 0.01 | 0.02 | none (1.00) | 0.16 | 0.01 | 0.01 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T015 | negação | bloquear_envios | 0.81 | 0.06 | 0.04 | none (0.81) | 0.25 | 0.02 | 0.09 | bloquear_envios | sim | ✓ |  | abrir_pedido_lgpd(exclusao) | opt-out definitivo |
| OL-T016 | fácil / outros | abrir_pedido_lgpd(acesso) | 0.01 | 0.01 | 0.97 | access (1.00) | 0.05 | 0.01 | 0.02 | abrir_pedido_lgpd(acesso) | não | ✓ |  | seguir | direito de titular: acesso |
| OL-T017 | fácil / outros | pausar | 0.11 | 0.95 | 0.04 | none (0.98) | 0.04 | 0.07 | 0.13 | pausar | não | ✓ |  | pausar | pausa com retomada |
| OL-T018 | fácil / outros | seguir | 0.01 | 0.02 | 0.01 | none (1.00) | 0.03 | 0.01 | 0.01 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T019 | ironia | seguir | 0.02 | 0.02 | 0.02 | none (1.00) | 0.44 | 0.01 | 0.02 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T020 | 'para' ambíguo | seguir | 0.47 | 0.08 | 0.05 | none (0.89) | 0.01 | 0.03 | 0.11 | revisar | ? | ✗ |  | bloquear_envios | dúvida de opt-out (0.47) |
| OL-T021 | fácil / outros | bloquear_envios | 0.97 | 0.03 | 0.25 | deletion (0.79) | 0.01 | 0.04 | 0.06 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-T022 | fácil / outros | abrir_pedido_lgpd(origem_dos_dados) | 0.02 | 0.01 | 0.86 | data_source (1.00) | 0.03 | 0.01 | 0.02 | abrir_pedido_lgpd(origem_dos_dados) | não | ✓ |  | seguir | direito de titular: origem_dos_dados |
| OL-T023 | fácil / outros | seguir | 0.01 | 0.01 | 0.01 | none (1.00) | 0.04 | 0.01 | 0.01 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T024 | fácil / outros | bloquear_envios | 0.90 | 0.04 | 0.04 | none (0.99) | 0.01 | 0.05 | 0.07 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-T025 | negação | seguir | 0.04 | 0.02 | 0.03 | none (1.00) | 0.24 | 0.02 | 0.03 | seguir | não | ✓ |  | bloquear_envios | nenhum pedido de parar, pausar ou de titular |
| OL-T026 | fácil / outros | bloquear_envios | 0.89 | 0.03 | 0.08 | none (0.96) | 0.01 | 0.12 | 0.05 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-T027 | fim de interesse sem pedido de parar | seguir | 0.06 | 0.03 | 0.02 | none (1.00) | 0.03 | 0.08 | 0.03 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T028 | fácil / outros | pausar | 0.27 | 0.93 | 0.02 | none (1.00) | 0.01 | 0.04 | 0.14 | revisar | ? | ✗ |  | seguir | dúvida de opt-out (0.27) |
| OL-T029 | fácil / outros | abrir_pedido_lgpd(correcao) | 0.02 | 0.01 | 0.98 | correction (1.00) | 0.05 | 0.01 | 0.02 | abrir_pedido_lgpd(correcao) | não | ✓ |  | abrir_pedido_lgpd(correcao) | direito de titular: correcao |
| OL-T030 | terceiro | abrir_pedido_lgpd(exclusao) | 0.90 | 0.03 | 0.93 | deletion (1.00) | 0.01 | 0.04 | 0.09 | abrir_pedido_lgpd(exclusao) | sim | ✓ |  | abrir_pedido_lgpd(exclusao) | direito de titular: exclusao |
| OL-T031 | reclamação longa | bloquear_envios | 0.91 | 0.03 | 0.09 | none (0.82) | 0.01 | 0.02 | 0.03 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-T032 | reclamação longa | seguir | 0.01 | 0.02 | 0.02 | none (1.00) | 0.33 | 0.01 | 0.01 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T033 | tipo | abrir_pedido_lgpd(acesso) | 0.02 | 0.01 | 0.84 | access (0.97) | 0.03 | 0.01 | 0.01 | abrir_pedido_lgpd(acesso) | não | ✓ |  | abrir_pedido_lgpd(acesso) | direito de titular: acesso |
| OL-T034 | fácil / outros | seguir | 0.13 | 0.02 | 0.05 | none (0.97) | 0.74 | 0.06 | 0.04 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T035 | 'para' ambíguo | bloquear_envios | 0.76 | 0.09 | 0.04 | none (0.99) | 0.02 | 0.05 | 0.12 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-T036 | negação | seguir | 0.02 | 0.02 | 0.05 | none (0.88) | 0.86 | 0.02 | 0.03 | seguir | não | ✓ |  | bloquear_envios | nenhum pedido de parar, pausar ou de titular |
| OL-T037 | terceiro | seguir | 0.05 | 0.02 | 0.02 | none (1.00) | 0.13 | 0.02 | 0.32 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T038 | fácil / outros | abrir_pedido_lgpd(acesso) | 0.02 | 0.01 | 0.91 | access (1.00) | 0.02 | 0.01 | 0.01 | abrir_pedido_lgpd(acesso) | não | ✓ |  | seguir | direito de titular: acesso |
| OL-T039 | fácil / outros | pausar | 0.05 | 0.92 | 0.02 | none (1.00) | 0.06 | 0.08 | 0.03 | pausar | não | ✓ |  | seguir | pausa com retomada |
| OL-T040 | dois pedidos | abrir_pedido_lgpd(origem_dos_dados) | 0.95 | 0.04 | 0.79 | deletion (0.79) | 0.02 | 0.02 | 0.07 | abrir_pedido_lgpd(exclusao) | sim | ✓ tipo✗ |  | bloquear_envios | direito de titular: exclusao |
| OL-T041 | fácil / outros | seguir | 0.02 | 0.03 | 0.02 | none (1.00) | 0.38 | 0.02 | 0.02 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T042 | fácil / outros | seguir | 0.02 | 0.01 | 0.02 | none (1.00) | 0.03 | 0.01 | 0.01 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T043 | fácil / outros | seguir | 0.04 | 0.24 | 0.04 | none (0.96) | 0.80 | 0.02 | 0.06 | seguir | não | ✓ |  | bloquear_envios | nenhum pedido de parar, pausar ou de titular |
| OL-T044 | fácil / outros | abrir_pedido_lgpd(exclusao) | 0.67 | 0.05 | 0.96 | deletion (1.00) | 0.01 | 0.05 | 0.04 | abrir_pedido_lgpd(exclusao) | sim | ✓ |  | abrir_pedido_lgpd(exclusao) | direito de titular: exclusao |
| OL-T045 | ironia | seguir | 0.03 | 0.01 | 0.03 | none (0.83) | 0.60 | 0.01 | 0.04 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T046 | fácil / outros | bloquear_envios | 0.94 | 0.03 | 0.79 | deletion (0.95) | 0.01 | 0.05 | 0.09 | abrir_pedido_lgpd(exclusao) | sim | ✗ |  | bloquear_envios | direito de titular: exclusao |
| OL-T047 | tipo | abrir_pedido_lgpd(correcao) | 0.01 | 0.01 | 0.97 | correction (1.00) | 0.04 | 0.01 | 0.01 | abrir_pedido_lgpd(correcao) | não | ✓ |  | abrir_pedido_lgpd(correcao) | direito de titular: correcao |
| OL-T048 | pausa × opt-out | pausar | 0.40 | 0.91 | 0.04 | none (0.98) | 0.02 | 0.03 | 0.07 | revisar | ? | ✗ |  | bloquear_envios | dúvida de opt-out (0.40) |
| OL-T049 | origem sem pedir exclusão | abrir_pedido_lgpd(origem_dos_dados) | 0.17 | 0.03 | 0.96 | data_source (1.00) | 0.02 | 0.02 | 0.06 | abrir_pedido_lgpd(origem_dos_dados) | não | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | direito de titular: origem_dos_dados |
| OL-T050 | pausa × opt-out | bloquear_envios | 0.79 | 0.02 | 0.04 | none (0.97) | 0.01 | 0.03 | 0.06 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-T051 | pausa × opt-out | seguir | 0.02 | 0.21 | 0.02 | none (0.99) | 0.86 | 0.01 | 0.02 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T052 | origem sem pedir exclusão | abrir_pedido_lgpd(origem_dos_dados) | 0.03 | 0.02 | 0.90 | data_source (1.00) | 0.03 | 0.01 | 0.03 | abrir_pedido_lgpd(origem_dos_dados) | não | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | direito de titular: origem_dos_dados |
| OL-T053 | negação | seguir | 0.02 | 0.03 | 0.06 | access (0.60) | 0.50 | 0.01 | 0.02 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T054 | exclusão parcial | abrir_pedido_lgpd(exclusao) | 0.03 | 0.03 | 0.93 | deletion (1.00) | 0.91 | 0.02 | 0.03 | abrir_pedido_lgpd(exclusao) | não | ✓ |  | abrir_pedido_lgpd(exclusao) | direito de titular: exclusao |
| OL-T055 | fácil / outros | bloquear_envios | 0.56 | 0.03 | 0.32 | deletion (0.87) | 0.17 | 0.04 | 0.06 | revisar | ? | ✗ |  | bloquear_envios | dúvida se há pedido de titular (0.32) |
| OL-T056 | fácil / outros | seguir | 0.02 | 0.01 | 0.02 | none (1.00) | 0.87 | 0.01 | 0.05 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-T057 | tipo | abrir_pedido_lgpd(acesso) | 0.03 | 0.02 | 0.89 | access (0.96) | 0.04 | 0.02 | 0.02 | abrir_pedido_lgpd(acesso) | não | ✓ |  | abrir_pedido_lgpd(acesso) | direito de titular: acesso |
| OL-T058 | fácil / outros | pausar | 0.04 | 0.66 | 0.01 | none (1.00) | 0.04 | 0.04 | 0.03 | pausar | não | ✓ |  | seguir | pausa com retomada |
| OL-T059 | terceiro | bloquear_envios | 0.87 | 0.03 | 0.59 | deletion (0.83) | 0.01 | 0.04 | 0.16 | revisar | ? | ✗ |  | seguir | dúvida se há pedido de titular (0.59) |
| OL-T060 | 'para' ambíguo | revisar | 0.38 | 0.03 | 0.07 | none (0.90) | 0.02 | 0.91 | 0.08 | revisar | ? | ✓ |  | bloquear_envios | dúvida de opt-out (0.38) |
