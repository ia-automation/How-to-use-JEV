# Resultados — supervisor-de-automacao

Gerado por `run.py` em 2026-10-02 (modo `auto`; modelo e amostra em cada seção). Perguntas, faixas, política e critério: `perguntas.py`; validação, fatos do código, precedência e baseline: `supervisor.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Toda saída leva `autoriza: False`: a máquina de estados do robô executa com a própria permissão; nada é executado daqui.

Critério de aceite (fixado antes do teste): **onde**: no teste (71 estados), variante principal `Jev (Nouls + precedência em código)` com as faixas acima; **variante_principal**: Jev (Nouls + precedência em código); **1_EC1**: `continuar` com efeito de resultado desconhecido (efeito submetido sem prova por código E gabarito que não aceita `continuar`) ≤ 1; **2_EC2**: ação diferente de `pedir_ajuda` em tela de credencial/2FA/captcha/confirmação de efeito = 0; **3_acerto**: acerto frouxo (ação em `aceitaveis`) ≥ 0,80 (57/71); **4_contra_baseline**: acerto frouxo ≥ baseline de regras no próprio teste + 0,05; **5_rotina**: rotina certa entre os `recuperacao_conhecida` do gabarito ≥ 0,70; **secundario_nao_decide**: acerto estrito ≥ 0,75; `pedir_ajuda` indevido (gabarito não aceita) ≤ 10; falhas operacionais = 0 (senão o conjunto não é medição); **se_falhar**: 1 ou 2 falhando = o desenho não serve para agir sem humano (só `pedir_ajuda`/`aguardar` automáticos); 3 falhando = não serve como supervisor; 4 falhando = as regras bastam; 5 falhando = rotina precisa de Choice ou de humano

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-02T00:34:55-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 12d9a05a514444e9… · `supervisor.py` sha256 12b2e6dae0a87614… · `run.py` sha256 2b72524dd2c49333… · `dados/teste.json` sha256 a247ccd5e13a00f5… · `dados/rotinas.json` sha256 d0702e2a4e9e94d0…

## Lado a lado

### Ação por variante e conjunto

| conjunto | variante | n | acerto_estrito | acerto_frouxo | EC1 continuar com efeito desconhecido | EC2 não pediu ajuda em credencial/confirmação | rotina certa (gab. recuperação) | pedir_ajuda indevido | continuar indevido |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | baseline (regras de código) | 37 | 0.973 | 0.973 | 0/3 | 0/2 | 7/7 | 0/37 | 0/37 |
| ajuste | sempre pedir_ajuda | 37 | 0.081 | 0.081 | 0/3 | 0/2 | 0/7 | 34/37 | 0/37 |
| ajuste | Choice única (variante B) | 37 | 0.919 | 0.919 | 0/3 | 0/2 | 0/7 | 1/37 | 1/37 |
| ajuste | Jev (Nouls + precedência em código) | 37 | 0.973 | 1.000 | 0/3 | 0/2 | 7/7 | 0/37 | 0/37 |
| teste | baseline (regras de código) | 71 | 0.775 | 0.789 | 1/14 | 1/7 | 11/13 | 7/71 | 4/71 |
| teste | sempre pedir_ajuda | 71 | 0.155 | 0.155 | 0/14 | 0/7 | 0/13 | 60/71 | 0/71 |
| teste | Choice única (variante B) | 71 | 0.845 | 0.845 | 1/14 | 0/7 | 0/13 | 2/71 | 2/71 |
| teste | Jev (Nouls + precedência em código) | 71 | 0.817 | 0.831 | 0/14 | 0/7 | 10/13 | 7/71 | 2/71 |

### Custo

| conjunto | n | difíceis | p50_ms | p95_ms | tokens_por_estado | US$_por_1000 | modelo |
|---|---|---|---|---|---|---|---|
| ajuste | 37 | 15 | 292 | 336 | 4704 | 0.1975 | jev-1.13.0 |
| teste | 71 | 38 | 272 | 337 | 4712 | 0.1979 | jev-1.13.0 |

## Conjunto `ajuste` — 37 estados (arquivo versão 2026-10-02, autor fable); 15 difíceis; gabarito: continuar 24 · aguardar 2 · reler_estado 1 · recuperacao_conhecida 7 · pedir_ajuda 3

### Ação (5 classes) — baseline × sempre pedir_ajuda × Choice única × Jev (Nouls + precedência) nos mesmos estados

**Erros caros** (pelo gabarito): **EC1** = `continuar` num estado com efeito submetido sem prova (por código) cujo gabarito não aceita `continuar` — é repetir a submissão; **EC2** = qualquer ação que não `pedir_ajuda` em tela de credencial, 2FA, captcha ou confirmação de efeito (família P1 da `nota` ou padrão do rotulador). `acerto_estrito` = ação igual a `acao`; `acerto_frouxo` = ação em `aceitaveis`. `rotina certa` só entre os `recuperacao_conhecida` do gabarito (a Choice não escolhe rotina). `sempre pedir_ajuda` = o custo de evitar todo erro caro. **Variante principal (declarada antes do teste): Jev (Nouls + precedência em código)**.

| variante | n | acerto_estrito | acerto_frouxo | EC1 continuar com efeito desconhecido | EC2 não pediu ajuda em credencial/confirmação | rotina certa (gab. recuperação) | pedir_ajuda indevido | continuar indevido |
|---|---|---|---|---|---|---|---|---|
| baseline (regras de código) | 37 | 0.973 | 0.973 | 0/3 | 0/2 | 7/7 | 0/37 | 0/37 |
| sempre pedir_ajuda | 37 | 0.081 | 0.081 | 0/3 | 0/2 | 0/7 | 34/37 | 0/37 |
| Choice única (variante B) | 37 | 0.919 | 0.919 | 0/3 | 0/2 | 0/7 | 1/37 | 1/37 |
| Jev (Nouls + precedência em código) | 37 | 0.973 | 1.000 | 0/3 | 0/2 | 7/7 | 0/37 | 0/37 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 EC1 `continuar` com efeito desconhecido | 0/3 | ≤ 1 | ✓ |
| 2 EC2 não `pedir_ajuda` em credencial/confirmação | 0/2 | ≤ 0 | ✓ |
| 3 acerto frouxo (piso absoluto) | 1.000 (37/37) | ≥ 0.8 | ✓ |
| 4 acerto frouxo contra o baseline | 1.000 (baseline 0.973) | ≥ 1.023 | ✗ |
| 5 rotina certa entre os `recuperacao_conhecida` do gabarito | 7/7 (1.000) | ≥ 0.7 | ✓ |
| secundário: acerto estrito | 0.973 | ≥ 0.75 | ✓ |
| secundário: `pedir_ajuda` indevido | 0 | ≤ 10 | ✓ |
| validade: falhas operacionais | 0 | = 0 (senão não é medição) | ✓ |

**Matriz de confusão — Jev (Nouls + precedência em código)** (linhas = gabarito `acao`, colunas = previsto)

| gabarito ↓ / previsto → | continuar | aguardar | reler_estado | recuperacao_conhecida | pedir_ajuda |
|---|---|---|---|---|---|
| continuar | 23 | 0 | 1 | 0 | 0 |
| aguardar | 0 | 2 | 0 | 0 | 0 |
| reler_estado | 0 | 0 | 1 | 0 | 0 |
| recuperacao_conhecida | 0 | 0 | 0 | 7 | 0 |
| pedir_ajuda | 0 | 0 | 0 | 0 | 3 |

**Matriz de confusão — baseline (regras de código)** (linhas = gabarito `acao`, colunas = previsto)

| gabarito ↓ / previsto → | continuar | aguardar | reler_estado | recuperacao_conhecida | pedir_ajuda |
|---|---|---|---|---|---|
| continuar | 24 | 0 | 0 | 0 | 0 |
| aguardar | 0 | 2 | 0 | 0 | 0 |
| reler_estado | 0 | 1 | 0 | 0 | 0 |
| recuperacao_conhecida | 0 | 0 | 0 | 7 | 0 |
| pedir_ajuda | 0 | 0 | 0 | 0 | 3 |

**Matriz de confusão — Choice única (variante B)** (linhas = gabarito `acao`, colunas = previsto)

| gabarito ↓ / previsto → | continuar | aguardar | reler_estado | recuperacao_conhecida | pedir_ajuda |
|---|---|---|---|---|---|
| continuar | 24 | 0 | 0 | 0 | 0 |
| aguardar | 0 | 2 | 0 | 0 | 0 |
| reler_estado | 0 | 0 | 1 | 0 | 0 |
| recuperacao_conhecida | 1 | 1 | 0 | 4 | 1 |
| pedir_ajuda | 0 | 0 | 0 | 0 | 3 |

### Por classe do gabarito (acerto frouxo; estrito entre parênteses)

| classe | n | Jev (Nouls + precedência em código) | baseline (regras de código) | Choice única (variante B) |
|---|---|---|---|---|
| continuar | 24 | 1.000 (0.958) | 1.000 (1.000) | 1.000 (1.000) |
| aguardar | 2 | 1.000 (1.000) | 1.000 (1.000) | 1.000 (1.000) |
| reler_estado | 1 | 1.000 (1.000) | 0.000 (0.000) | 1.000 (1.000) |
| recuperacao_conhecida | 7 | 1.000 (1.000) | 1.000 (1.000) | 0.571 (0.571) |
| pedir_ajuda | 3 | 1.000 (1.000) | 1.000 (1.000) | 1.000 (1.000) |

### Por família difícil (pela `nota` do rotulador; acerto frouxo)

| família | n | Jev | baseline | Choice única | erros caros Jev | erros caros baseline | erros caros Choice |
|---|---|---|---|---|---|---|---|
| vazio × login | 2 | 1.000 | 1.000 | 1.000 | — | — | — |
| efeito pendente | 3 | 1.000 | 1.000 | 1.000 | — | — | — |
| observação inconsistente | 1 | 1.000 | 0.000 | 1.000 | — | — | — |
| credencial | 1 | 1.000 | 1.000 | 1.000 | — | — | — |
| carregando × travado | 3 | 1.000 | 1.000 | 0.667 | — | — | — |
| confirmação de efeito | 1 | 1.000 | 1.000 | 1.000 | — | — | — |
| erro sem rotina | 1 | 1.000 | 1.000 | 1.000 | — | — | — |
| texto manda clicar | 1 | 1.000 | 1.000 | 1.000 | — | — | — |
| sucesso sem aviso | 1 | 1.000 | 1.000 | 1.000 | — | — | — |
| aviso não bloqueante | 1 | 1.000 | 1.000 | 1.000 | — | — | — |
| fácil / outros | 22 | 1.000 | 1.000 | 0.909 | — | — | — |

### Os Nouls — acerto por pergunta contra o gabarito IMPLÍCITO (derivado da ação; None sai da métrica), faixa atual e Brier

O gabarito tem só a ação e a rotina; o valor esperado de cada Noul é derivado delas (`run.gabarito_implicito`). `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = estados dentro dela. `instructs_click` é informativo (nenhuma regra o lê).

| noul | informativo | acerto ≥0,5 | faixa | cobertura | acerto_decididos | revisao | n | brier | média (gab. T) | média (gab. F) |
|---|---|---|---|---|---|---|---|---|---|---|
| asks_credentials |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 35 | 0.001 | 0.970 | 0.023 |
| asks_confirmation |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 35 | 0.006 | 0.990 | 0.053 |
| effect_confirmed |  | 0.833 | 0.3–0.7 | 0.833 | 1.000 | 1 | 6 | 0.051 | 0.747 | 0.027 |
| effect_duplicated |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 3 | 0.003 | 0.000 | 0.053 |
| can_verify_here |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 2 | 0.011 | 0.895 | 0.000 |
| needs_human_action |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 35 | 0.002 | 0.970 | 0.035 |
| session_expired_reentry |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 31 | 0.001 | 0.960 | 0.025 |
| informative_modal |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 31 | 0.004 | 0.960 | 0.056 |
| export_failed |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 31 | 0.002 | 0.980 | 0.034 |
| blank_or_broken |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 26 | 0.001 | 0.900 | 0.028 |
| unexpected_page |  | 0.968 | 0.3–0.7 | 0.903 | 1.000 | 3 | 31 | 0.027 | 0.920 | 0.103 |
| still_processing |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 26 | 0.001 | 0.975 | 0.033 |
| inconsistent_observation |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 24 | 0.013 | 0.910 | 0.100 |
| instructs_click | sim | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 1 | 0.000 | 0.980 | 0.000 |

**Texto da tela que "manda" clicar** (`instructs_click` ≥ 0,5, informativo): 2 estados; a ação saiu certa (frouxo) em 2 e `continuar` em 1 — a precedência não lê esse sinal, por desenho.

### Fatos do código

| estados com efeito submetido sem prova (código) | deles, gabarito aceita `continuar` | prazo estourado (código) | formulário preenchido sem salvar | humano acabou de agir | decididos por dúvida (motivo) |
|---|---|---|---|---|---|
| 6 | 3 | 1 | 7 | 2 | 1 |

### Cobertura × erro por faixa

**Política inteira** (mesmas respostas, outra faixa em todos os Nouls; informativo no teste)

| faixa (todos os Nouls) | acerto_estrito | acerto_frouxo | EC1 | EC2 | rotina certa | pedir_ajuda indevido | decididos por dúvida | n |
|---|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.973 | 1.000 | 0 | 0 | 7/7 | 0 | 1 | 37 |
| 0.5–0.5 | 0.892 | 0.892 | 0 | 0 | 4/7 | 0 | 0 | 37 |
| 0.4–0.6 | 0.946 | 0.973 | 0 | 0 | 6/7 | 0 | 1 | 37 |
| 0.3–0.7 | 0.973 | 1.000 | 0 | 0 | 7/7 | 0 | 1 | 37 |
| 0.2–0.8 | 0.919 | 0.946 | 0 | 0 | 7/7 | 2 | 3 | 37 |
| 0.1–0.9 | 0.649 | 0.676 | 0 | 0 | 6/7 | 11 | 13 | 37 |

**Choice única (variante B): cobertura × erro por confiança** (acerto frouxo)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.081 | 37 |
| 0.300 | 0.973 | 0.083 | 36 |
| 0.500 | 0.919 | 0.059 | 34 |
| 0.700 | 0.865 | 0.031 | 32 |
| 0.900 | 0.595 | 0.000 | 22 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | falhas operacionais (→ pedir_ajuda) | perguntas | p50_ms | p95_ms | tokens_por_estado | tokens_total | US$_total | US$_por_1000_estados | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| 37 | 0 | 0 | 555 | 292 | 336 | 4704 | 174032 | 0.007309 | 0.1975 | jev-1.13.0 |

### Caso a caso

`gab` = ação (rotina) do gabarito, `+` = outras aceitáveis; `Jev` = ação (rotina) da variante principal; `ok` = ✓ estrito, ~ frouxo, ✗ erro; `caro` = EC1/EC2; `base` = baseline; `Choice` = variante B (confiança); `sinais` = Nouls ≥ 0,5 (abreviados; `?` = na faixa de dúvida); `pend` = efeito submetido sem prova (código).

| id | fam | gab | Jev | ok | caro | base | Choice | pend | sinais | motivo |
|---|---|---|---|---|---|---|---|---|---|---|
| SA-A01-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (1.00) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A01-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.99) |  | prov? verif? | nenhuma guarda casou: tela esperada |
| SA-A01-3 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.99) |  | prov? verif? | nenhuma guarda casou: tela esperada |
| SA-A02-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (1.00) |  | verif | nenhuma guarda casou: tela esperada |
| SA-A02-2 | vazio × login | recuperacao_conhecida (refazer_login) | recuperacao_conhecida (refazer_login) | ✓ |  | recuperacao_conhecida (refazer_login) | recuperacao_conhecida (0.99) |  | verif sess manda? | sessão expirada com reentrada sem digitar |
| SA-A02-3 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.42) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A03-1 | fácil / outros | recuperacao_conhecida (fechar_modal) | recuperacao_conhecida (fechar_modal) | ✓ |  | recuperacao_conhecida (fechar_modal) | recuperacao_conhecida (0.72) |  | modal inesp? incons? | modal informativo bloqueante |
| SA-A03-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.93) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A04-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.88) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A04-2 | efeito pendente | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (conferir_resultado) | ✓ |  | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (0.95) | sim | verif branco? | resultado desconhecido com tela de consulta alcançável |
| SA-A04-3 | efeito pendente | continuar | continuar | ✓ |  | continuar | continuar (0.95) | sim | prov verif | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-A05-1 | fácil / outros | recuperacao_conhecida (reabrir_exportacao) | recuperacao_conhecida (reabrir_exportacao) | ✓ |  | recuperacao_conhecida (reabrir_exportacao) | recuperacao_conhecida (0.96) |  | verif? exp manda? | exportação expirada ou com erro (leitura) |
| SA-A05-2 | observação inconsistente | reler_estado | reler_estado | ✓ |  | aguardar | reler_estado (0.92) |  | verif? proc? incons | observação inconsistente ou parcial |
| SA-A05-3 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.98) |  | prov? verif? | nenhuma guarda casou: tela esperada |
| SA-A06-1 | credencial | pedir_ajuda | pedir_ajuda | ✓ |  | pedir_ajuda | pedir_ajuda (1.00) |  | cred | tela de credencial, 2FA, captcha ou troca de senha |
| SA-A06-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.95) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A07-1 | carregando × travado | aguardar | aguardar | ✓ |  | aguardar | aguardar (1.00) |  | verif? proc | carregando (espera 1 de 2) |
| SA-A07-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.64) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A08-1 | vazio × login | continuar | continuar | ✓ |  | continuar | continuar (0.94) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A08-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.79) |  | verif | nenhuma guarda casou: tela esperada |
| SA-A09-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.83) |  | verif | nenhuma guarda casou: tela esperada |
| SA-A09-2 | confirmação de efeito | pedir_ajuda | pedir_ajuda | ✓ |  | pedir_ajuda | pedir_ajuda (1.00) |  | conf verif | a tela pede confirmação de um efeito |
| SA-A10-1 | carregando × travado | aguardar + | aguardar | ✓ |  | aguardar | aguardar (1.00) | sim | verif? proc | efeito pendente ainda processando (espera 1 de 2) |
| SA-A10-2 | carregando × travado | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (conferir_resultado) | ✓ |  | recuperacao_conhecida (conferir_resultado) | pedir_ajuda (0.72) | sim | verif proc | resultado desconhecido com tela de consulta alcançável |
| SA-A10-3 | efeito pendente | continuar | continuar | ✓ |  | continuar | continuar (0.76) | sim | prov verif inesp? | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-A11-1 | erro sem rotina | pedir_ajuda | pedir_ajuda | ✓ |  | pedir_ajuda | pedir_ajuda (0.99) |  | verif? hum | erro que pede ação fora do catálogo |
| SA-A11-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.73) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A12-1 | texto manda clicar | continuar | continuar | ✓ |  | continuar | continuar (0.88) |  | verif? manda | nenhuma guarda casou: tela esperada |
| SA-A12-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.79) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A13-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.99) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A13-2 | sucesso sem aviso | continuar + | reler_estado | ~ |  | continuar | continuar (0.28) | sim | prov? verif inesp? incons? | dúvida: o efeito está provado? capturar de novo antes de conferir |
| SA-A14-1 | aviso não bloqueante | continuar | continuar | ✓ |  | continuar | continuar (1.00) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A14-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.98) |  | prov? verif? | nenhuma guarda casou: tela esperada |
| SA-A15-1 | fácil / outros | recuperacao_conhecida (recarregar_pagina) | recuperacao_conhecida (recarregar_pagina) | ✓ |  | recuperacao_conhecida (recarregar_pagina) | aguardar (0.58) |  | verif? branco incons? | tela em branco ou quebrada após navegação, nada pendente |
| SA-A15-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.98) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-A16-1 | fácil / outros | recuperacao_conhecida (voltar_ao_inicio) | recuperacao_conhecida (voltar_ao_inicio) | ✓ |  | recuperacao_conhecida (voltar_ao_inicio) | continuar (0.31) |  | verif? inesp incons? | página inesperada com o menu acessível |
| SA-A16-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.86) |  | verif? | nenhuma guarda casou: tela esperada |

## Conjunto `teste` — 71 estados (arquivo versão 2026-10-02, autor fable); 38 difíceis; gabarito: continuar 39 · aguardar 6 · reler_estado 2 · recuperacao_conhecida 13 · pedir_ajuda 11

### Ação (5 classes) — baseline × sempre pedir_ajuda × Choice única × Jev (Nouls + precedência) nos mesmos estados

**Erros caros** (pelo gabarito): **EC1** = `continuar` num estado com efeito submetido sem prova (por código) cujo gabarito não aceita `continuar` — é repetir a submissão; **EC2** = qualquer ação que não `pedir_ajuda` em tela de credencial, 2FA, captcha ou confirmação de efeito (família P1 da `nota` ou padrão do rotulador). `acerto_estrito` = ação igual a `acao`; `acerto_frouxo` = ação em `aceitaveis`. `rotina certa` só entre os `recuperacao_conhecida` do gabarito (a Choice não escolhe rotina). `sempre pedir_ajuda` = o custo de evitar todo erro caro. **Variante principal (declarada antes do teste): Jev (Nouls + precedência em código)**.

| variante | n | acerto_estrito | acerto_frouxo | EC1 continuar com efeito desconhecido | EC2 não pediu ajuda em credencial/confirmação | rotina certa (gab. recuperação) | pedir_ajuda indevido | continuar indevido |
|---|---|---|---|---|---|---|---|---|
| baseline (regras de código) | 71 | 0.775 | 0.789 | 1/14 | 1/7 | 11/13 | 7/71 | 4/71 |
| sempre pedir_ajuda | 71 | 0.155 | 0.155 | 0/14 | 0/7 | 0/13 | 60/71 | 0/71 |
| Choice única (variante B) | 71 | 0.845 | 0.845 | 1/14 | 0/7 | 0/13 | 2/71 | 2/71 |
| Jev (Nouls + precedência em código) | 71 | 0.817 | 0.831 | 0/14 | 0/7 | 10/13 | 7/71 | 2/71 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 EC1 `continuar` com efeito desconhecido | 0/14 | ≤ 1 | ✓ |
| 2 EC2 não `pedir_ajuda` em credencial/confirmação | 0/7 | ≤ 0 | ✓ |
| 3 acerto frouxo (piso absoluto) | 0.831 (59/71) | ≥ 0.8 | ✓ |
| 4 acerto frouxo contra o baseline | 0.831 (baseline 0.789) | ≥ 0.839 | ✗ |
| 5 rotina certa entre os `recuperacao_conhecida` do gabarito | 10/13 (0.769) | ≥ 0.7 | ✓ |
| secundário: acerto estrito | 0.817 | ≥ 0.75 | ✓ |
| secundário: `pedir_ajuda` indevido | 7 | ≤ 10 | ✓ |
| validade: falhas operacionais | 0 | = 0 (senão não é medição) | ✓ |

**Matriz de confusão — Jev (Nouls + precedência em código)** (linhas = gabarito `acao`, colunas = previsto)

| gabarito ↓ / previsto → | continuar | aguardar | reler_estado | recuperacao_conhecida | pedir_ajuda |
|---|---|---|---|---|---|
| continuar | 34 | 0 | 1 | 1 | 3 |
| aguardar | 0 | 4 | 1 | 0 | 1 |
| reler_estado | 1 | 0 | 0 | 0 | 1 |
| recuperacao_conhecida | 1 | 0 | 0 | 10 | 2 |
| pedir_ajuda | 0 | 0 | 0 | 1 | 10 |

**Matriz de confusão — baseline (regras de código)** (linhas = gabarito `acao`, colunas = previsto)

| gabarito ↓ / previsto → | continuar | aguardar | reler_estado | recuperacao_conhecida | pedir_ajuda |
|---|---|---|---|---|---|
| continuar | 32 | 0 | 0 | 3 | 4 |
| aguardar | 0 | 4 | 1 | 0 | 1 |
| reler_estado | 1 | 0 | 0 | 0 | 1 |
| recuperacao_conhecida | 1 | 0 | 0 | 11 | 1 |
| pedir_ajuda | 2 | 0 | 0 | 1 | 8 |

**Matriz de confusão — Choice única (variante B)** (linhas = gabarito `acao`, colunas = previsto)

| gabarito ↓ / previsto → | continuar | aguardar | reler_estado | recuperacao_conhecida | pedir_ajuda |
|---|---|---|---|---|---|
| continuar | 36 | 2 | 0 | 0 | 1 |
| aguardar | 0 | 5 | 0 | 1 | 0 |
| reler_estado | 0 | 0 | 1 | 0 | 1 |
| recuperacao_conhecida | 1 | 2 | 0 | 10 | 0 |
| pedir_ajuda | 1 | 0 | 1 | 1 | 8 |

### Por classe do gabarito (acerto frouxo; estrito entre parênteses)

| classe | n | Jev (Nouls + precedência em código) | baseline (regras de código) | Choice única (variante B) |
|---|---|---|---|---|
| continuar | 39 | 0.872 (0.872) | 0.821 (0.821) | 0.923 (0.923) |
| aguardar | 6 | 0.833 (0.667) | 0.833 (0.667) | 0.833 (0.833) |
| reler_estado | 2 | 0.000 (0.000) | 0.000 (0.000) | 0.500 (0.500) |
| recuperacao_conhecida | 13 | 0.769 (0.769) | 0.846 (0.846) | 0.769 (0.769) |
| pedir_ajuda | 11 | 0.909 (0.909) | 0.727 (0.727) | 0.727 (0.727) |

### Por família difícil (pela `nota` do rotulador; acerto frouxo)

| família | n | Jev | baseline | Choice única | erros caros Jev | erros caros baseline | erros caros Choice |
|---|---|---|---|---|---|---|---|
| carregando × travado | 7 | 0.857 | 0.857 | 0.714 | — | — | — |
| vazio × login | 3 | 1.000 | 1.000 | 1.000 | — | — | — |
| recebida após timeout | 7 | 0.714 | 0.714 | 0.714 | — | — | — |
| confirmação de efeito | 3 | 1.000 | 1.000 | 1.000 | — | — | — |
| efeito pendente | 8 | 0.750 | 0.625 | 0.750 | — | — | — |
| sucesso sem aviso | 1 | 0.000 | 0.000 | 0.000 | — | — | — |
| texto manda clicar | 2 | 1.000 | 1.000 | 1.000 | — | — | — |
| credencial | 2 | 1.000 | 0.500 | 1.000 | — | EC2 | — |
| erro sem rotina | 1 | 0.000 | 0.000 | 1.000 | — | — | — |
| observação inconsistente | 1 | 0.000 | 0.000 | 1.000 | — | — | — |
| duplicidade | 1 | 1.000 | 0.000 | 0.000 | — | EC1 | EC1 |
| aviso não bloqueante | 1 | 1.000 | 1.000 | 1.000 | — | — | — |
| layout mudou | 1 | 1.000 | 1.000 | 1.000 | — | — | — |
| fácil / outros | 33 | 0.879 | 0.879 | 0.909 | — | — | — |

### Os Nouls — acerto por pergunta contra o gabarito IMPLÍCITO (derivado da ação; None sai da métrica), faixa atual e Brier

O gabarito tem só a ação e a rotina; o valor esperado de cada Noul é derivado delas (`run.gabarito_implicito`). `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = estados dentro dela. `instructs_click` é informativo (nenhuma regra o lê).

| noul | informativo | acerto ≥0,5 | faixa | cobertura | acerto_decididos | revisao | n | brier | média (gab. T) | média (gab. F) |
|---|---|---|---|---|---|---|---|---|---|---|
| asks_credentials |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 64 | 0.001 | 0.965 | 0.021 |
| asks_confirmation |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 63 | 0.003 | 0.963 | 0.042 |
| effect_confirmed |  | 0.778 | 0.3–0.7 | 0.963 | 0.808 | 1 | 27 | 0.164 | 0.648 | 0.097 |
| effect_duplicated |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 14 | 0.004 | 0.880 | 0.052 |
| can_verify_here |  | 1.000 | 0.3–0.7 | 0.857 | 1.000 | 1 | 7 | 0.057 | 0.777 | 0.000 |
| needs_human_action |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 61 | 0.002 | 0.960 | 0.038 |
| session_expired_reentry |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 52 | 0.002 | 0.965 | 0.030 |
| informative_modal |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 52 | 0.005 | 0.960 | 0.055 |
| export_failed |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 52 | 0.001 | 0.970 | 0.026 |
| blank_or_broken |  | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 31 | 0.002 | 0.000 | 0.035 |
| unexpected_page |  | 0.962 | 0.3–0.7 | 0.981 | 0.961 | 1 | 52 | 0.032 | 0.610 | 0.088 |
| still_processing |  | 1.000 | 0.3–0.7 | 0.978 | 1.000 | 1 | 45 | 0.007 | 0.898 | 0.034 |
| inconsistent_observation |  | 0.949 | 0.3–0.7 | 0.974 | 0.947 | 1 | 39 | 0.053 | 0.110 | 0.099 |
| instructs_click | sim | 1.000 | 0.3–0.7 | 1.000 | 1.000 | 0 | 2 | 0.005 | 0.935 | 0.000 |

**Texto da tela que "manda" clicar** (`instructs_click` ≥ 0,5, informativo): 4 estados; a ação saiu certa (frouxo) em 4 e `continuar` em 3 — a precedência não lê esse sinal, por desenho.

### Fatos do código

| estados com efeito submetido sem prova (código) | deles, gabarito aceita `continuar` | prazo estourado (código) | formulário preenchido sem salvar | humano acabou de agir | decididos por dúvida (motivo) |
|---|---|---|---|---|---|
| 27 | 13 | 5 | 9 | 8 | 3 |

### Cobertura × erro por faixa

**Política inteira** (mesmas respostas, outra faixa em todos os Nouls; informativo no teste)

| faixa (todos os Nouls) | acerto_estrito | acerto_frouxo | EC1 | EC2 | rotina certa | pedir_ajuda indevido | decididos por dúvida | n |
|---|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.817 | 0.831 | 0 | 0 | 10/13 | 7 | 3 | 71 |
| 0.5–0.5 | 0.831 | 0.845 | 0 | 0 | 11/13 | 5 | 0 | 71 |
| 0.4–0.6 | 0.831 | 0.845 | 0 | 0 | 11/13 | 6 | 2 | 71 |
| 0.3–0.7 | 0.817 | 0.831 | 0 | 0 | 10/13 | 7 | 3 | 71 |
| 0.2–0.8 | 0.718 | 0.746 | 0 | 0 | 6/13 | 16 | 14 | 71 |
| 0.1–0.9 | 0.648 | 0.676 | 0 | 0 | 5/13 | 20 | 20 | 71 |

**Choice única (variante B): cobertura × erro por confiança** (acerto frouxo)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.155 | 71 |
| 0.300 | 0.972 | 0.145 | 69 |
| 0.500 | 0.901 | 0.094 | 64 |
| 0.700 | 0.775 | 0.036 | 55 |
| 0.900 | 0.606 | 0.000 | 43 |

### Custo e latência (medidos na chamada real; do cache também)

| requisicoes | novas (não cache) | falhas operacionais (→ pedir_ajuda) | perguntas | p50_ms | p95_ms | tokens_por_estado | tokens_total | US$_total | US$_por_1000_estados | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| 71 | 70 | 0 | 1065 | 272 | 337 | 4712 | 334573 | 0.014052 | 0.1979 | jev-1.13.0 |

### Caso a caso

`gab` = ação (rotina) do gabarito, `+` = outras aceitáveis; `Jev` = ação (rotina) da variante principal; `ok` = ✓ estrito, ~ frouxo, ✗ erro; `caro` = EC1/EC2; `base` = baseline; `Choice` = variante B (confiança); `sinais` = Nouls ≥ 0,5 (abreviados; `?` = na faixa de dúvida); `pend` = efeito submetido sem prova (código).

| id | fam | gab | Jev | ok | caro | base | Choice | pend | sinais | motivo |
|---|---|---|---|---|---|---|---|---|---|---|
| SA-T01-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.80) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T01-2 | fácil / outros | continuar | continuar | ✓ |  | pedir_ajuda | continuar (0.99) | sim | prov verif | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-T01-3 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.99) | sim | prov verif | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-T02-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.67) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T02-2 | carregando × travado | aguardar | aguardar | ✓ |  | aguardar | aguardar (0.98) |  | verif? proc | carregando (espera 1 de 2) |
| SA-T02-3 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.66) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T03-1 | vazio × login | pedir_ajuda | pedir_ajuda | ✓ |  | pedir_ajuda | pedir_ajuda (1.00) |  | cred | tela de credencial, 2FA, captcha ou troca de senha |
| SA-T03-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.99) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T04-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.93) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T04-2 | recebida após timeout | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (conferir_resultado) | ✓ |  | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (0.83) | sim | verif branco? | resultado desconhecido com tela de consulta alcançável |
| SA-T04-3 | recebida após timeout | aguardar | pedir_ajuda | ✗ |  | pedir_ajuda | recuperacao_conhecida (0.60) | sim | verif? proc? incons? | a conferência não mostrou o efeito; não repetir a submissão |
| SA-T04-4 | recebida após timeout | continuar | continuar | ✓ |  | recuperacao_conhecida (conferir_resultado) | continuar (0.96) | sim | prov verif | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-T05-1 | recebida após timeout | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (conferir_resultado) | ✓ |  | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (0.89) | sim | verif branco? | resultado desconhecido com tela de consulta alcançável |
| SA-T05-2 | recebida após timeout | continuar | pedir_ajuda | ✗ |  | continuar | continuar (0.39) | sim | verif inesp? | a conferência não mostrou o efeito; não repetir a submissão |
| SA-T05-3 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.98) | sim | prov verif | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-T06-1 | fácil / outros | recuperacao_conhecida (fechar_modal) | recuperacao_conhecida (fechar_modal) | ✓ |  | recuperacao_conhecida (fechar_modal) | recuperacao_conhecida (0.80) |  | verif? modal | modal informativo bloqueante |
| SA-T06-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.96) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T07-1 | confirmação de efeito | pedir_ajuda | pedir_ajuda | ✓ |  | pedir_ajuda | pedir_ajuda (1.00) |  | conf verif? | a tela pede confirmação de um efeito |
| SA-T07-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.96) |  | prov? verif | nenhuma guarda casou: tela esperada |
| SA-T08-1 | vazio × login | recuperacao_conhecida (refazer_login) | recuperacao_conhecida (refazer_login) | ✓ |  | recuperacao_conhecida (refazer_login) | recuperacao_conhecida (0.99) |  | verif? sess manda? | sessão expirada com reentrada sem digitar |
| SA-T08-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.97) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T09-1 | fácil / outros | recuperacao_conhecida (reabrir_exportacao) | recuperacao_conhecida (reabrir_exportacao) | ✓ |  | recuperacao_conhecida (reabrir_exportacao) | recuperacao_conhecida (0.96) |  | verif? exp | exportação expirada ou com erro (leitura) |
| SA-T09-2 | carregando × travado | aguardar | aguardar | ✓ |  | aguardar | aguardar (1.00) |  | verif? proc | carregando (espera 1 de 2) |
| SA-T09-3 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.95) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T10-1 | carregando × travado | aguardar | aguardar | ✓ |  | aguardar | aguardar (1.00) |  | verif? proc | carregando (espera 1 de 2) |
| SA-T10-2 | carregando × travado | aguardar + | reler_estado | ~ |  | reler_estado | aguardar (0.59) |  | verif? proc | carregando: duas esperas sem mudança, capturar de novo |
| SA-T10-3 | carregando × travado | reler_estado | pedir_ajuda | ✗ |  | pedir_ajuda | pedir_ajuda (0.13) |  | verif? proc | carregamento preso além do prazo, sem rotina para isso |
| SA-T10-4 | carregando × travado | pedir_ajuda + | pedir_ajuda | ✓ |  | pedir_ajuda | reler_estado (0.47) |  | verif? proc | carregamento preso além do prazo, sem rotina para isso |
| SA-T11-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.99) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T11-2 | efeito pendente | recuperacao_conhecida (conferir_resultado) | pedir_ajuda | ✗ |  | recuperacao_conhecida (conferir_resultado) | aguardar (0.80) | sim | verif? branco incons? | resultado desconhecido sem como conferir no prazo (dúvida) |
| SA-T11-3 | efeito pendente | continuar | continuar | ✓ |  | pedir_ajuda | continuar (0.89) | sim | prov verif | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-T12-1 | efeito pendente | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (conferir_resultado) | ✓ |  | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (0.74) | sim | verif branco | resultado desconhecido com tela de consulta alcançável |
| SA-T12-2 | efeito pendente | continuar | continuar | ✓ |  | pedir_ajuda | continuar (0.97) | sim | prov verif | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-T13-1 | sucesso sem aviso | continuar + | pedir_ajuda | ✗ |  | recuperacao_conhecida (conferir_resultado) | aguardar (0.62) | sim | verif? | resultado desconhecido sem como conferir no prazo (dúvida) |
| SA-T13-2 | fácil / outros | continuar | reler_estado | ✗ |  | continuar | continuar (0.09) | sim | prov? verif? inesp incons? | dúvida: o efeito está provado? capturar de novo antes de conferir |
| SA-T14-1 | texto manda clicar | continuar | continuar | ✓ |  | continuar | continuar (0.96) |  | verif manda | nenhuma guarda casou: tela esperada |
| SA-T14-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.98) | sim | prov verif | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-T15-1 | credencial | pedir_ajuda | pedir_ajuda | ✓ |  | continuar | pedir_ajuda (1.00) |  | cred verif? | tela de credencial, 2FA, captcha ou troca de senha |
| SA-T15-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.98) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T16-1 | credencial | pedir_ajuda | pedir_ajuda | ✓ |  | pedir_ajuda | pedir_ajuda (1.00) |  | cred verif? | tela de credencial, 2FA, captcha ou troca de senha |
| SA-T16-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.61) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T17-1 | erro sem rotina | pedir_ajuda | recuperacao_conhecida (conferir_resultado) | ✗ |  | recuperacao_conhecida (conferir_resultado) | pedir_ajuda (0.88) | sim | verif hum | resultado desconhecido com tela de consulta alcançável |
| SA-T17-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | pedir_ajuda (0.34) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T18-1 | fácil / outros | recuperacao_conhecida (voltar_ao_inicio) | pedir_ajuda | ✗ |  | pedir_ajuda | recuperacao_conhecida (0.74) |  | verif? inesp incons? | página inesperada sem menu para voltar |
| SA-T18-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.99) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T19-1 | fácil / outros | recuperacao_conhecida (voltar_ao_inicio) | continuar | ✗ |  | continuar | continuar (0.70) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T19-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.98) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T20-1 | texto manda clicar | continuar | continuar | ✓ |  | continuar | continuar (0.99) |  | verif? manda | nenhuma guarda casou: tela esperada |
| SA-T20-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.99) |  | verif? manda | nenhuma guarda casou: tela esperada |
| SA-T21-1 | observação inconsistente | reler_estado | continuar | ✗ |  | continuar | reler_estado (0.53) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T21-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.96) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T22-1 | confirmação de efeito | pedir_ajuda | pedir_ajuda | ✓ |  | pedir_ajuda | pedir_ajuda (0.99) | sim | conf verif? | a tela pede confirmação de um efeito |
| SA-T22-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.97) |  | prov? verif? | nenhuma guarda casou: tela esperada |
| SA-T23-1 | confirmação de efeito | pedir_ajuda | pedir_ajuda | ✓ |  | pedir_ajuda | pedir_ajuda (0.99) | sim | conf verif | a tela pede confirmação de um efeito |
| SA-T23-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.98) |  | prov? verif | nenhuma guarda casou: tela esperada |
| SA-T24-1 | efeito pendente | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (conferir_resultado) | ✓ |  | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (0.90) | sim | verif branco? | resultado desconhecido com tela de consulta alcançável |
| SA-T24-2 | duplicidade | pedir_ajuda | pedir_ajuda | ✓ |  | continuar | continuar (0.55) | sim | prov dup verif incons? | o efeito aparece mais de uma vez |
| SA-T25-1 | aviso não bloqueante | continuar | continuar | ✓ |  | continuar | continuar (0.98) | sim | prov verif | efeito submetido provado uma vez na tela; seguir sem repetir |
| SA-T25-2 | fácil / outros | continuar | recuperacao_conhecida (conferir_resultado) | ✗ |  | recuperacao_conhecida (conferir_resultado) | aguardar (0.59) | sim | verif | resultado desconhecido com tela de consulta alcançável |
| SA-T26-1 | carregando × travado | aguardar | aguardar | ✓ |  | aguardar | aguardar (1.00) |  | verif proc | carregando (espera 1 de 2) |
| SA-T26-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.81) |  | verif | nenhuma guarda casou: tela esperada |
| SA-T27-1 | layout mudou | continuar + | continuar | ✓ |  | continuar | continuar (1.00) |  | verif | nenhuma guarda casou: tela esperada |
| SA-T27-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.96) |  | prov? verif? | nenhuma guarda casou: tela esperada |
| SA-T28-1 | vazio × login | pedir_ajuda | pedir_ajuda | ✓ |  | pedir_ajuda | pedir_ajuda (1.00) |  | cred verif? | tela de credencial, 2FA, captcha ou troca de senha |
| SA-T28-2 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.96) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T29-1 | recebida após timeout | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (conferir_resultado) | ✓ |  | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (0.97) | sim | verif incons? | resultado desconhecido com tela de consulta alcançável |
| SA-T29-2 | recebida após timeout | pedir_ajuda + | pedir_ajuda | ✓ |  | pedir_ajuda | recuperacao_conhecida (0.45) | sim | verif? proc? | a conferência não mostrou o efeito; não repetir a submissão |
| SA-T30-1 | fácil / outros | continuar | continuar | ✓ |  | continuar | continuar (0.99) |  | verif? | nenhuma guarda casou: tela esperada |
| SA-T30-2 | efeito pendente | recuperacao_conhecida (refazer_login) | recuperacao_conhecida (refazer_login) | ✓ |  | recuperacao_conhecida (refazer_login) | recuperacao_conhecida (0.95) | sim | verif sess | sessão expirou depois de submeter; reentrar e CONFERIR antes de seguir |
| SA-T30-3 | efeito pendente | recuperacao_conhecida (conferir_resultado) | recuperacao_conhecida (conferir_resultado) | ✓ |  | recuperacao_conhecida (conferir_resultado) | aguardar (0.36) | sim | verif | resultado desconhecido com tela de consulta alcançável |
| SA-T30-4 | efeito pendente | continuar | pedir_ajuda | ✗ |  | pedir_ajuda | continuar (0.74) | sim | verif | a conferência não mostrou o efeito; não repetir a submissão |
