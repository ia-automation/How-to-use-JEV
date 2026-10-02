# Rascunho — lint-semantico-de-diff (encanamento, não é métrica)

## Conjunto `rascunho` — 5 diffs (arquivo versão 2026-10-01, autor fable)

> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**

### Semânticas (4 regras; 2 com gabarito true/false, 2 nulas) — Jev × baseline, por desenho

`acerto_duro` = viola ≥ 0,5 × gabarito (no desenho `aplicabilidade`, aplica < LIMIAR_APLICA conta como não viola). `cobertura`/`acerto_decididos`/`revisa` = com a FAIXA (0.3, 0.7) (e LIMIAR_APLICA 0.3). `erro_caro` = gabarito true que saiu `ok` ou `nao_se_aplica` (violação real passou). `falso_alarme` = gabarito false que saiu `viola`. `nulo_nao_se_aplica` = gabarito nulo que o lint marcou como não aplicável (só o desenho `aplicabilidade` sabe dizer isso); `nulo_sem_alarme` = nulo que não virou `viola`. `baseline` = regex de gatilho + palavra-chave (`None` = sem gatilho = não se aplica).

| desenho | n | acerto_duro | cobertura | acerto_decididos | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | nulo_sem_alarme | brier | baseline_acerto | baseline_erro_caro | baseline_falso_alarme | baseline_nulo_sinalizado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| valvula | 2 | 1.000 | 1.000 | 1.000 | 0 | 0/0 | 0/2 | 0/2 | 2/2 | 0.006 | 1.000 | 0/0 | 0/2 | 2/2 |
| aplicabilidade | 2 | 1.000 | 1.000 | 1.000 | 0 | 0/0 | 0/2 | 2/2 | 2/2 | 0.006 | 1.000 | 0/0 | 0/2 | 2/2 |
| gatilho | 2 | 1.000 | 1.000 | 1.000 | 0 | 0/0 | 0/2 | 2/2 | 2/2 | 0.006 | 1.000 | 0/0 | 0/2 | 2/2 |

### O Noul de aplicabilidade separa `null` de `false`?

Distribuição de `aplica` (e mediana de `viola`) por gabarito. Se os nulos ficam abaixo do LIMIAR_APLICA e os true/false acima, o Noul auxiliar paga; se o `viola` dos nulos já é baixo, a válvula na instrução basta; `sem_gatilho_regex` é o que a regex de gatilho (desenho `gatilho`) diria — para nulo, quanto maior melhor; para true, cada um é uma violação que o código esconderia do Jev.

| gabarito | n | aplica_min | aplica_p50 | aplica_max | abaixo_de_LIMIAR_APLICA | sem_gatilho_regex | viola_p50 |
|---|---|---|---|---|---|---|---|
| null | 2 | 0.090 | 0.100 | 0.100 | 2 | 2 | 0.080 |
| F | 2 | 0.970 | 0.970 | 0.970 | 0 | 0 | 0.080 |

| LIMIAR_APLICA | acerto_duro | cobertura | erro_decididos | erro_caro | falso_alarme | nulo_nao_se_aplica |
|---|---|---|---|---|---|---|
| 0.200 | 1.000 | 1.000 | 0.000 | 0/0 | 0/2 | 2/2 |
| 0.300 | 1.000 | 1.000 | 0.000 | 0/0 | 0/2 | 2/2 |
| 0.400 | 1.000 | 1.000 | 0.000 | 0/0 | 0/2 | 2/2 |
| 0.500 | 1.000 | 1.000 | 0.000 | 0/0 | 0/2 | 2/2 |

### Mecânicas (12 regras) — regex × gabarito (tem de ser 100%; menos é bug)

Acerto 1.000 (12/12); 0 erro(s).

| regra | n | acerto |
|---|---|---|
| DROP | 1 | 1.000 |
| LOG | 4 | 1.000 |
| SEG | 5 | 1.000 |
| TODO | 2 | 1.000 |

### Cobertura × erro por faixa — `valvula`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.3–0.7 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.2–0.8 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.1–0.9 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.2–0.7 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.3–0.8 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.2–0.9 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |

### Cobertura × erro por faixa — `aplicabilidade`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.3–0.7 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.2–0.8 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.1–0.9 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.2–0.7 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.3–0.8 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.2–0.9 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |

### Cobertura × erro por faixa — `gatilho`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.3–0.7 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.2–0.8 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.1–0.9 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.2–0.7 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.3–0.8 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |
| 0.2–0.9 | 1.000 | 0.000 | 0 | 0/0 | 0/2 | 2/2 |

### Por regra semântica e por dificuldade — `gatilho`

| chave | n | nulos | acerto_duro | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | baseline | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| JSDOC | 1 | 1 | 1.000 | 0 | 0/0 | 0/1 | 1/1 | 1.000 | 0/0 |
| SQL | 0 | 1 | nan | 0 | 0/0 | 0/0 | 1/1 | nan | 0/0 |
| VALID | 1 | 0 | 1.000 | 0 | 0/0 | 0/1 | 0/0 | 1.000 | 0/0 |

| dificil | n | nulos | acerto_duro | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | baseline | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| False | 2 | 2 | 1.000 | 0 | 0/0 | 0/2 | 2/2 | 1.000 | 0/0 |

### Custo e latência (medidos na chamada real; do cache também)

Uma requisição por diff com regras semânticas (2 Nouls por regra); diff só com mecânicas custa zero. Aqui 1 PR = 1 diff de 10–60 linhas; PR real tem vários arquivos e custa proporcionalmente mais.

| requisicoes | do_cache | perguntas | p50_ms | p95_ms | tokens_por_diff | US$_por_diff | US$_por_mil_PRs | modelo |
|---|---|---|---|---|---|---|---|---|
| 4 | 4 | 8 | 306 | 354 | 978 | 0.0000410 | 0.0410 | jev-1.13.0 |

### Caso a caso (desenho padrão `gatilho`)

Por regra: `viola`/`aplica` do Jev, `g` = gatilho por regex (mecânica: regex), veredito com faixa, gabarito, baseline (T/F/null). `erro` = veredito decidido ≠ gabarito; `caro` = violação real que passou; `alarme` = false → viola; `nulo→viola` = nulo apontado como violação. Última coluna: comentário de CI do diff.

| id | regra | tipo | jev/regra | veredito | gab | marca | comentário de CI |
|---|---|---|---|---|---|---|---|
| LS-R001 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `chave: '***',` |
| LS-R001 | r2 LOG | mec | regex | ok | F | — |  |
| LS-R001 | r3 TODO | mec | regex | ok | F | — |  |
| LS-R002 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `console.log('criando lead', telefone);` |
| LS-R002 | r2 SEG | mec | regex | ok | F | — |  |
| LS-R002 | r3 JSDOC | sem | v=0.07 a=0.09 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-R003 | r1 JSDOC | sem | v=0.08 a=0.97 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-R003 | r2 SEG | mec | regex | ok | F | — |  |
| LS-R003 | r3 LOG | mec | regex | ok | F | — |  |
| LS-R004 | r1 DROP | mec | regex | viola | T | — | - r1 DROP: viola<br>    `DROP TABLE visitas_antigas;` |
| LS-R004 | r2 SEG | mec | regex | ok | F | — |  |
| LS-R004 | r3 SQL | sem | v=0.08 a=0.10 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-R005 | r1 VALID | sem | v=0.07 a=0.97 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-R005 | r2 SEG | mec | regex | ok | F | — |  |
| LS-R005 | r3 LOG | mec | regex | ok | F | — |  |
| LS-R005 | r4 TODO | mec | regex | ok | F | — |  |
