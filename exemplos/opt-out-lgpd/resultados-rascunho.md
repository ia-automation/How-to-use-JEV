# Rascunho — opt-out-lgpd (encanamento)

## Conjunto `rascunho` — 5 mensagens (arquivo versão 2026-10-01, autor fable); 0 difíceis, 0 com `opt_out` nulo

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Ação (5 classes) — métrica principal, baseline × sempre revisa × Jev nos mesmos casos

Gabarito da ação: `pedido_lgpd` → `abrir_pedido_lgpd`; `opt_out` nulo → `revisar`; `opt_out` → `bloquear_envios`; `pausa_temporaria` → `pausar`; senão `seguir`. **INFRAÇÃO** = opt-out ou pedido LGPD real que saiu `seguir`. `obrigação pela metade` = sem `seguir` e sem `revisar`, mas a obrigação não foi cumprida inteira: opt-out real → `pausar`; pedido LGPD real sem `abrir_pedido_lgpd`; pedido aberto sem bloquear quem também pediu para parar (bloqueio pendente, `bloq` = `?`, conta como não cumprido). **BLOQUEIO INDEVIDO** = mensagem sem opt-out nem pedido LGPD (cliente interessado, pausa, preferência, filtro) cujo envio foi bloqueado. `sempre revisa` = o custo de evitar todo erro: zero infração, 100% das mensagens a humano. `tipo LGPD certo` = pedido aberto com o tipo do gabarito, sobre os pedidos reais.

| variante | n | acerto_acao | INFRAÇÃO (opt-out/LGPD real → seguir) | obrigação pela metade | BLOQUEIO INDEVIDO (sem opt-out nem LGPD → bloqueia) | bloqueou c/ opt_out falso (todos) | null → revisar | revisou sem necessidade | tipo LGPD certo (pedidos reais) |
|---|---|---|---|---|---|---|---|---|---|
| baseline (expressões) | 5 | 1.000 | 0/3 | 0/3 | 0/2 | 0/3 | 0/0 | 0/5 | 2/2 |
| sempre revisa | 5 | 0.000 | 0/3 | 0/3 | 0/2 | 0/3 | 0/0 | 5/5 | 0/2 |
| Jev | 5 | 1.000 | 0/3 | 0/3 | 0/2 | 0/3 | 0/0 | 0/5 | 2/2 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 infração | 0/3 | ≤ 0 | ✓ |
| 2 obrigação pela metade | 0/3 | ≤ 1 | ✓ |
| 3 bloqueio indevido | 0/2 | ≤ 1 | ✓ |
| 4 acerto da ação | 1.000 (baseline 1.000) | ≥ 1.150 | ✗ |
| secundário: nulo → revisar | 0/0 | todos | ✓ |
| secundário: revisou sem necessidade | 0/5 (0.000) | ≤ 0.15 | ✓ |
| secundário: tipo LGPD certo | 2/2 (1.000) | ≥ 0.85 | ✓ |

**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | bloquear_envios | abrir_pedido_lgpd | pausar | seguir | revisar |
|---|---|---|---|---|---|
| bloquear_envios | 1 | 0 | 0 | 0 | 0 |
| abrir_pedido_lgpd | 0 | 2 | 0 | 0 | 0 |
| pausar | 0 | 0 | 1 | 0 | 0 |
| seguir | 0 | 0 | 0 | 1 | 0 |
| revisar | 0 | 0 | 0 | 0 | 0 |

**Matriz de confusão — baseline**

| gabarito ↓ / previsto → | bloquear_envios | abrir_pedido_lgpd | pausar | seguir | revisar |
|---|---|---|---|---|---|
| bloquear_envios | 1 | 0 | 0 | 0 | 0 |
| abrir_pedido_lgpd | 0 | 2 | 0 | 0 | 0 |
| pausar | 0 | 0 | 1 | 0 | 0 |
| seguir | 0 | 0 | 0 | 1 | 0 |
| revisar | 0 | 0 | 0 | 0 | 0 |

### Nouls principais — acerto (≥ 0,5) contra o gabarito, faixa atual e Brier

`opt_out` é o pedido EXPLÍCITO de parar: nas exclusões o gabarito é `true` por regra de código (exclusão ⇒ opt-out), por isso há a linha sem os casos de exclusão. Gabarito nulo fica fora. `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela.

| noul | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|
| opt_out | 0.800 | 0.2–0.7 | 1.000 | 0.800 | 0 | 5 | 0.153 |
| temporary_pause | 1.000 | 0.4–0.6 | 1.000 | 1.000 | 0 | 5 | 0.001 |
| lgpd_request | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 | 0.002 |
| opt_out (sem exclusões) | 1.000 | 0.2–0.7 | 1.000 | 1.000 | 0 | 4 | 0.002 |

**`opt_out` composto** (bloqueio decidido pelo código: Noul + regra exclusão ⇒ opt-out; dúvida/`revisar` conta como erro aqui): Jev 1.000 · baseline 1.000 (n = 5)

### Nouls de guarda — valores por grupo (não têm campo próprio no gabarito)

| noul | grupo | n_grupo | mín–máx no grupo | mín–máx fora | fora ≥ sim | faixa |
|---|---|---|---|---|---|---|
| stop_without_object | `opt_out` nulo | 0 | — | 0.01–0.05 | 0 | 0.2–0.5 |
| wants_contact_to_continue | família negação | 0 | — | 0.01–0.85 | 1 | 0.2–0.7 |
| about_another_contact | família terceiro | 0 | — | 0.01–0.06 | 0 | 0.2–0.7 |

### Tipo LGPD — Choice `lgpd_type` entre os 2 pedidos reais

| Choice crua (vencedor) | na ação (pedido aberto com o tipo certo) | baseline | n | Choice ≠ none sem pedido real | piso de confiança |
|---|---|---|---|---|---|
| 1.000 | 1.000 | 1.000 | 2 | 0/3 | 0.500 |

| gabarito ↓ / Choice → | exclusao | origem_dos_dados | acesso | correcao | None |
|---|---|---|---|---|---|
| exclusao | 1 | 0 | 0 | 0 | 0 |
| origem_dos_dados | 0 | 1 | 0 | 0 | 0 |
| acesso | 0 | 0 | 0 | 0 | 0 |
| correcao | 0 | 0 | 0 | 0 | 0 |

**Cobertura × erro por confiança da Choice** (pedidos reais)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 2 |
| 0.300 | 1.000 | 0.000 | 2 |
| 0.500 | 1.000 | 0.000 | 2 |
| 0.700 | 1.000 | 0.000 | 2 |
| 0.900 | 1.000 | 0.000 | 2 |

### Por família difícil (pela `nota` do rotulador)

| família | n | ação Jev | ação baseline | Jev → revisar | obrigação perdida Jev | bloqueio indevido Jev | obrigação perdida baseline |
|---|---|---|---|---|---|---|---|
| fácil / outros | 5 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |

### Cobertura × erro por faixa

**Política inteira** (mesmas respostas, outra faixa nos três Nouls principais; informativo no teste). `cobertura_auto` = não foi a `revisar` nem deixou bloqueio pendente (`bloqueia=None` num pedido aberto).

| faixa (3 Nouls principais) | cobertura_auto | erro_automatico | infrações | obrigação pela metade | bloqueios indevidos | bloqueio pendente (fora da cobertura) | n_auto |
|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 1.000 | 0.000 | 0 | 0 | 0 | 0 | 5 |
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0 | 0 | 0 | 5 |
| 0.4–0.6 | 1.000 | 0.000 | 0 | 0 | 0 | 0 | 5 |
| 0.3–0.7 | 1.000 | 0.000 | 0 | 0 | 0 | 0 | 5 |
| 0.2–0.8 | 1.000 | 0.000 | 0 | 0 | 0 | 0 | 5 |
| 0.1–0.9 | 1.000 | 0.000 | 0 | 0 | 0 | 0 | 5 |

**Cada Noul principal sozinho** (cobertura = decidido fora da faixa; acerto entre os decididos)

| noul | faixa | cobertura | acerto_decididos | revisao | n |
|---|---|---|---|---|---|
| opt_out (sem exclusões) | 0.5–0.5 | 1.000 | 1.000 | 0 | 4 |
| opt_out (sem exclusões) | 0.4–0.6 | 1.000 | 1.000 | 0 | 4 |
| opt_out (sem exclusões) | 0.3–0.7 | 1.000 | 1.000 | 0 | 4 |
| opt_out (sem exclusões) | 0.2–0.8 | 1.000 | 1.000 | 0 | 4 |
| opt_out (sem exclusões) | 0.1–0.9 | 1.000 | 1.000 | 0 | 4 |
| temporary_pause | 0.5–0.5 | 1.000 | 1.000 | 0 | 5 |
| temporary_pause | 0.4–0.6 | 1.000 | 1.000 | 0 | 5 |
| temporary_pause | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 |
| temporary_pause | 0.2–0.8 | 1.000 | 1.000 | 0 | 5 |
| temporary_pause | 0.1–0.9 | 1.000 | 1.000 | 0 | 5 |
| lgpd_request | 0.5–0.5 | 1.000 | 1.000 | 0 | 5 |
| lgpd_request | 0.4–0.6 | 1.000 | 1.000 | 0 | 5 |
| lgpd_request | 0.3–0.7 | 1.000 | 1.000 | 0 | 5 |
| lgpd_request | 0.2–0.8 | 1.000 | 1.000 | 0 | 5 |
| lgpd_request | 0.1–0.9 | 1.000 | 1.000 | 0 | 5 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | mensagens_longas (sem chamada) | falhas operacionais (→ revisar) | perguntas | p50_ms | p95_ms | tokens_por_mensagem | US$_total | US$_por_1000_mensagens | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | 0 | 0 | 35 | 340 | 770 | 2023 | 0.000425 | 0.0850 | jev-1.13.0 |

### Caso a caso

`opt`/`pausa`/`lgpd` = Nouls `opt_out`, `temporary_pause`, `lgpd_request`; `tipo` = vencedor da Choice (confiança); `cont`/`s/obj`/`terc` = guardas `wants_contact_to_continue`, `stop_without_object`, `about_another_contact`; `ok` compara a ação do Jev com o gabarito; `caro` marca obrigação perdida ou bloqueio indevido; `base` = baseline.

| id | fam | gab | opt | pausa | lgpd | tipo | cont | s/obj | terc | ação Jev | bloq | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OL-R001 | fácil / outros | bloquear_envios | 0.96 | 0.03 | 0.10 | none (0.70) | 0.01 | 0.03 | 0.05 | bloquear_envios | sim | ✓ |  | bloquear_envios | opt-out definitivo |
| OL-R002 | fácil / outros | seguir | 0.01 | 0.01 | 0.01 | none (1.00) | 0.85 | 0.01 | 0.01 | seguir | não | ✓ |  | seguir | nenhum pedido de parar, pausar ou de titular |
| OL-R003 | fácil / outros | abrir_pedido_lgpd(exclusao) | 0.13 | 0.02 | 0.98 | deletion (1.00) | 0.03 | 0.03 | 0.02 | abrir_pedido_lgpd(exclusao) | sim | ✓ |  | abrir_pedido_lgpd(exclusao) | direito de titular: exclusao |
| OL-R004 | fácil / outros | pausar | 0.03 | 0.96 | 0.02 | none (0.99) | 0.27 | 0.05 | 0.05 | pausar | não | ✓ |  | pausar | pausa com retomada |
| OL-R005 | fácil / outros | abrir_pedido_lgpd(origem_dos_dados) | 0.07 | 0.02 | 0.97 | data_source (1.00) | 0.03 | 0.01 | 0.06 | abrir_pedido_lgpd(origem_dos_dados) | não | ✓ |  | abrir_pedido_lgpd(origem_dos_dados) | direito de titular: origem_dos_dados |
