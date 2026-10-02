# Resultados — lint-semantico-de-diff

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, regex, faixa e baseline: `perguntas.py`; composição: `lint.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Desenho padrão: `gatilho`; FAIXA (0.3, 0.7); LIMIAR_APLICA 0.3.

Critério de continuar/descartar (fixado antes do teste): no teste, com o desenho padrão, a FAIXA e o LIMIAR_APLICA acima: (1) mecanicas: 100% (menos é bug de código); (2) semantico duro: acerto duro (noul ≥ 0,5, gabarito true/false) ≥ 0,90 E ≥ baseline + 10 p.p.; (3) erro caro: ≤ 5% das violações reais (gabarito true) passam como `ok` ou `nao_se_aplica`; (4) falso alarme: ≤ 10% dos gabaritos false viram `viola`; (5) nulo: ≥ 80% dos gabaritos null NÃO viram `viola`.

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T12:28:52-03:00, antes de abrir o teste): `perguntas.py` sha256 96c8c0d12f40ffa2… · `lint.py` sha256 45a31ecd84a395ea… · `run.py` sha256 c65d47cf50a9dd97… · `dados/teste.json` sha256 9c029ea96c18d5b8…

## Lado a lado

| conjunto | desenho | n_sem | acerto_duro | baseline | cobertura | acerto_decididos | erro_caro | falso_alarme | nulo_nao_se_aplica | nulo_sem_alarme | brier | mecânicas | p50_ms | p95_ms | US$_por_mil_PRs | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | valvula | 19 | 1.000 | 0.789 | 0.947 | 1.000 | 0/10 | 0/9 | 0/22 | 18/22 | 0.028 | 76/76 | 284 | 353 | 0.0524 | jev-1.13.0 |
| ajuste | aplicabilidade | 19 | 1.000 | 0.789 | 0.947 | 1.000 | 0/10 | 0/9 | 12/22 | 18/22 | 0.028 | 76/76 | 284 | 353 | 0.0524 | jev-1.13.0 |
| ajuste | gatilho | 19 | 1.000 | 0.789 | 0.947 | 1.000 | 0/10 | 0/9 | 22/22 | 22/22 | 0.028 | 76/76 | 284 | 353 | 0.0524 | jev-1.13.0 |
| teste | valvula | 33 | 0.909 | 0.727 | 0.909 | 0.967 | 1/18 | 0/15 | 0/36 | 34/36 | 0.062 | 137/137 | 251 | 375 | 0.0499 | jev-1.13.0 |
| teste | aplicabilidade | 33 | 0.909 | 0.727 | 0.909 | 0.967 | 1/18 | 0/15 | 25/36 | 34/36 | 0.062 | 137/137 | 251 | 375 | 0.0499 | jev-1.13.0 |
| teste | gatilho | 33 | 0.909 | 0.727 | 0.909 | 0.967 | 1/18 | 0/15 | 36/36 | 36/36 | 0.062 | 137/137 | 251 | 375 | 0.0499 | jev-1.13.0 |

## Conjunto `ajuste` — 36 diffs (arquivo versão 2026-10-01, autor fable)

### Semânticas (41 regras; 19 com gabarito true/false, 22 nulas) — Jev × baseline, por desenho

`acerto_duro` = viola ≥ 0,5 × gabarito (no desenho `aplicabilidade`, aplica < LIMIAR_APLICA conta como não viola). `cobertura`/`acerto_decididos`/`revisa` = com a FAIXA (0.3, 0.7) (e LIMIAR_APLICA 0.3). `erro_caro` = gabarito true que saiu `ok` ou `nao_se_aplica` (violação real passou). `falso_alarme` = gabarito false que saiu `viola`. `nulo_nao_se_aplica` = gabarito nulo que o lint marcou como não aplicável (só o desenho `aplicabilidade` sabe dizer isso); `nulo_sem_alarme` = nulo que não virou `viola`. `baseline` = regex de gatilho + palavra-chave (`None` = sem gatilho = não se aplica).

| desenho | n | acerto_duro | cobertura | acerto_decididos | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | nulo_sem_alarme | brier | baseline_acerto | baseline_erro_caro | baseline_falso_alarme | baseline_nulo_sinalizado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| valvula | 19 | 1.000 | 0.947 | 1.000 | 1 | 0/10 | 0/9 | 0/22 | 18/22 | 0.028 | 0.789 | 4/10 | 0/9 | 22/22 |
| aplicabilidade | 19 | 1.000 | 0.947 | 1.000 | 1 | 0/10 | 0/9 | 12/22 | 18/22 | 0.028 | 0.789 | 4/10 | 0/9 | 22/22 |
| gatilho | 19 | 1.000 | 0.947 | 1.000 | 1 | 0/10 | 0/9 | 22/22 | 22/22 | 0.028 | 0.789 | 4/10 | 0/9 | 22/22 |

### O Noul de aplicabilidade separa `null` de `false`?

Distribuição de `aplica` (e mediana de `viola`) por gabarito. Se os nulos ficam abaixo do LIMIAR_APLICA e os true/false acima, o Noul auxiliar paga; se o `viola` dos nulos já é baixo, a válvula na instrução basta; `sem_gatilho_regex` é o que a regex de gatilho (desenho `gatilho`) diria — para nulo, quanto maior melhor; para true, cada um é uma violação que o código esconderia do Jev.

| gabarito | n | aplica_min | aplica_p50 | aplica_max | abaixo_de_LIMIAR_APLICA | sem_gatilho_regex | viola_p50 |
|---|---|---|---|---|---|---|---|
| null | 22 | 0.060 | 0.270 | 0.930 | 12 | 22 | 0.110 |
| F | 9 | 0.200 | 0.970 | 0.980 | 1 | 1 | 0.140 |
| T | 10 | 0.930 | 0.960 | 0.970 | 0 | 0 | 0.940 |

| LIMIAR_APLICA | acerto_duro | cobertura | erro_decididos | erro_caro | falso_alarme | nulo_nao_se_aplica |
|---|---|---|---|---|---|---|
| 0.200 | 1.000 | 0.947 | 0.000 | 0/10 | 0/9 | 11/22 |
| 0.300 | 1.000 | 0.947 | 0.000 | 0/10 | 0/9 | 12/22 |
| 0.400 | 1.000 | 0.947 | 0.000 | 0/10 | 0/9 | 13/22 |
| 0.500 | 1.000 | 0.947 | 0.000 | 0/10 | 0/9 | 15/22 |

### Mecânicas (76 regras) — regex × gabarito (tem de ser 100%; menos é bug)

Acerto 1.000 (76/76); 0 erro(s).

| regra | n | acerto |
|---|---|---|
| DROP | 4 | 1.000 |
| LOG | 23 | 1.000 |
| SEG | 36 | 1.000 |
| TODO | 13 | 1.000 |

### Cobertura × erro por faixa — `valvula`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0/10 | 0/9 | 17/22 |
| 0.3–0.7 | 0.947 | 0.000 | 1 | 0/10 | 0/9 | 18/22 |
| 0.2–0.8 | 0.737 | 0.000 | 5 | 0/10 | 0/9 | 22/22 |
| 0.1–0.9 | 0.421 | 0.000 | 11 | 0/10 | 0/9 | 22/22 |
| 0.2–0.7 | 0.737 | 0.000 | 5 | 0/10 | 0/9 | 18/22 |
| 0.3–0.8 | 0.947 | 0.000 | 1 | 0/10 | 0/9 | 22/22 |
| 0.2–0.9 | 0.632 | 0.000 | 7 | 0/10 | 0/9 | 22/22 |

### Cobertura × erro por faixa — `aplicabilidade`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0/10 | 0/9 | 17/22 |
| 0.3–0.7 | 0.947 | 0.000 | 1 | 0/10 | 0/9 | 18/22 |
| 0.2–0.8 | 0.737 | 0.000 | 5 | 0/10 | 0/9 | 22/22 |
| 0.1–0.9 | 0.474 | 0.000 | 10 | 0/10 | 0/9 | 22/22 |
| 0.2–0.7 | 0.737 | 0.000 | 5 | 0/10 | 0/9 | 18/22 |
| 0.3–0.8 | 0.947 | 0.000 | 1 | 0/10 | 0/9 | 22/22 |
| 0.2–0.9 | 0.632 | 0.000 | 7 | 0/10 | 0/9 | 22/22 |

### Cobertura × erro por faixa — `gatilho`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0/10 | 0/9 | 22/22 |
| 0.3–0.7 | 0.947 | 0.000 | 1 | 0/10 | 0/9 | 22/22 |
| 0.2–0.8 | 0.737 | 0.000 | 5 | 0/10 | 0/9 | 22/22 |
| 0.1–0.9 | 0.474 | 0.000 | 10 | 0/10 | 0/9 | 22/22 |
| 0.2–0.7 | 0.737 | 0.000 | 5 | 0/10 | 0/9 | 22/22 |
| 0.3–0.8 | 0.947 | 0.000 | 1 | 0/10 | 0/9 | 22/22 |
| 0.2–0.9 | 0.632 | 0.000 | 7 | 0/10 | 0/9 | 22/22 |

### Por regra semântica e por dificuldade — `gatilho`

| chave | n | nulos | acerto_duro | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | baseline | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| DESVIO | 4 | 3 | 1.000 | 0 | 0/2 | 0/2 | 3/3 | 0.750 | 1/2 |
| JSDOC | 6 | 12 | 1.000 | 0 | 0/4 | 0/2 | 12/12 | 0.833 | 1/4 |
| SQL | 5 | 4 | 1.000 | 0 | 0/1 | 0/4 | 4/4 | 0.800 | 1/1 |
| VALID | 4 | 3 | 1.000 | 1 | 0/3 | 0/1 | 3/3 | 0.750 | 1/3 |

| dificil | n | nulos | acerto_duro | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | baseline | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| False | 1 | 3 | 1.000 | 0 | 0/0 | 0/1 | 3/3 | 1.000 | 0/0 |
| True | 18 | 19 | 1.000 | 1 | 0/10 | 0/8 | 19/19 | 0.778 | 4/10 |

### Custo e latência (medidos na chamada real; do cache também)

Uma requisição por diff com regras semânticas (2 Nouls por regra); diff só com mecânicas custa zero. Aqui 1 PR = 1 diff de 10–60 linhas; PR real tem vários arquivos e custa proporcionalmente mais.

| requisicoes | do_cache | perguntas | p50_ms | p95_ms | tokens_por_diff | US$_por_diff | US$_por_mil_PRs | modelo |
|---|---|---|---|---|---|---|---|---|
| 30 | 30 | 82 | 284 | 353 | 1247 | 0.0000524 | 0.0524 | jev-1.13.0 |

### Caso a caso (desenho padrão `gatilho`)

Por regra: `viola`/`aplica` do Jev, `g` = gatilho por regex (mecânica: regex), veredito com faixa, gabarito, baseline (T/F/null). `erro` = veredito decidido ≠ gabarito; `caro` = violação real que passou; `alarme` = false → viola; `nulo→viola` = nulo apontado como violação. Última coluna: comentário de CI do diff.

| id | regra | tipo | jev/regra | veredito | gab | marca | comentário de CI |
|---|---|---|---|---|---|---|---|
| LS-A001 | r1 VALID | sem | v=0.06 a=0.97 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A001 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A001 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A001 | r4 JSDOC | sem | v=0.14 a=0.92 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A002 | r1 VALID | sem | v=0.96 a=0.96 g=T · bl=T | viola | T | — | - r1 VALID: viola (p=0.96)<br>    `router.post('/visitas', async (req, res) => {` |
| LS-A002 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A002 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A002 | r4 TODO | mec | regex | ok | F | — |  |
| LS-A003 | r1 DESVIO | sem | v=0.11 a=0.92 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A003 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A003 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A003 | r4 JSDOC | sem | v=0.12 a=0.51 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A004 | r1 JSDOC | sem | v=0.93 a=0.96 g=T · bl=T | viola | T | — | - r1 JSDOC: viola (p=0.93)<br>    `export function valorFinanciado(valor: number, entrada: number): number {` |
| LS-A004 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A004 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A005 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `// para testar local usar o token *** (conta sandbox do time)` |
| LS-A005 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A005 | r3 JSDOC | sem | v=0.09 a=0.15 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A006 | r1 JSDOC | sem | v=0.09 a=0.15 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-A006 | r2 SQL | sem | v=0.08 a=0.17 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A006 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A006 | r4 LOG | mec | regex | ok | F | — |  |
| LS-A007 | r1 SQL | sem | v=0.14 a=0.97 g=T · bl=F | ok | F | — | - r2 JSDOC: viola (p=0.96)<br>    `export async function funilPorCorretor(mes: string) {` |
| LS-A007 | r2 JSDOC | sem | v=0.96 a=0.97 g=T · bl=T | viola | T | — |  |
| LS-A007 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A007 | r4 LOG | mec | regex | ok | F | — |  |
| LS-A008 | r1 SQL | sem | v=0.85 a=0.93 g=T · bl=F | viola | T | — | - r1 SQL: viola (p=0.85)<br>    `const r = await db.execute(sql`SELECT * FROM leads WHERE telefone = ${telefone}`);` |
| LS-A008 | r2 JSDOC | sem | v=0.78 a=0.87 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A008 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A009 | r1 LOG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A009 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A009 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A010 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `// console.log('job', job.id);` |
| LS-A010 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A010 | r3 JSDOC | sem | v=0.07 a=0.07 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A011 | r1 TODO | mec | regex | viola | T | — | - r1 TODO: viola<br>    `// TODO: CRM-418 tratar proposta com dois compradores` |
| LS-A011 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A011 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A011 | r4 JSDOC | sem | v=0.09 a=0.16 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A012 | r1 DROP | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A012 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A012 | r3 SQL | sem | v=0.08 a=0.10 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A013 | r1 DROP | mec | regex | viola | T | — | - r1 DROP: viola<br>    `ALTER TABLE imoveis DROP COLUMN area_total_antiga;` |
| LS-A013 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A013 | r3 SQL | sem | v=0.07 a=0.10 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A014 | r1 DROP | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A014 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A014 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A015 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `***,` |
| LS-A015 | r2 JSDOC | sem | v=0.22 a=0.40 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A015 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A016 | r1 SEG | mec | regex | ok | F | — | - r3 JSDOC: viola (p=0.97)<br>    `export function senhaValida(s: string): boolean {` |
| LS-A016 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A016 | r3 JSDOC | sem | v=0.97 a=0.97 g=T · bl=T | viola | T | — |  |
| LS-A017 | r1 VALID | sem | v=0.08 a=0.27 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-A017 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A017 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A018 | r1 VALID | sem | v=0.11 a=0.15 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-A018 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A018 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A018 | r4 TODO | mec | regex | ok | F | — |  |
| LS-A019 | r1 SQL | sem | v=0.11 a=0.20 g=F · bl=null | nao_se_aplica | F | — | nenhuma regra violada ou em revisão |
| LS-A019 | r2 JSDOC | sem | v=0.12 a=0.38 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A019 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A020 | r1 VALID | sem | v=0.60 a=0.96 g=T · bl=T | revisa | T | — | - r1 VALID: revisa (p=0.60)<br>    `router.put('/imoveis/:id', param('id').isUUID(), body('preco').isInt({ min: 0 }), async (req, res) => {` |
| LS-A020 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A020 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A021 | r1 DESVIO | sem | v=0.94 a=0.94 g=T · bl=T | viola | T | — | - r1 DESVIO: viola (p=0.94)<br>    `from .legado import *  # noqa` |
| LS-A021 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A021 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A022 | r1 DESVIO | sem | v=0.21 a=0.95 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A022 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A022 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A023 | r1 SQL | sem | v=0.22 a=0.90 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A023 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A023 | r3 DESVIO | sem | v=0.15 a=0.79 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A024 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `***` |
| LS-A024 | r2 DESVIO | sem | v=0.06 a=0.06 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A024 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A025 | r1 DROP | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A025 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A025 | r3 SQL | sem | v=0.07 a=0.08 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A026 | r1 DESVIO | sem | v=0.91 a=0.94 g=T · bl=F | viola | T | — | - r1 DESVIO: viola (p=0.91)<br>    `// @ts-ignore ok` |
| LS-A026 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A026 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A026 | r4 JSDOC | sem | v=0.78 a=0.41 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A027 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `curl -H "Authorization: Bearer ***" https://api.github.com/repos/exemplo/crm` |
| LS-A027 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A027 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A028 | r1 TODO | mec | regex | viola | T | — | - r1 TODO: viola<br>    `// FIXME remover filtro quando a agenda externa parar de devolver cancelados` |
| LS-A028 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A028 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A029 | r1 VALID | sem | v=0.94 a=0.96 g=T · bl=F | viola | T | — | - r1 VALID: viola (p=0.94)<br>    `router.get('/imoveis', query('bairro').optional().isString(), async (req, res) => {`<br>    `router.delete('/imoveis/:id', async (req, res) => {` |
| LS-A029 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A029 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A029 | r4 JSDOC | sem | v=0.75 a=0.93 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A030 | r1 SQL | sem | v=0.28 a=0.98 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A030 | r2 JSDOC | sem | v=0.24 a=0.97 g=T · bl=F | ok | F | — |  |
| LS-A030 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A031 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `console.log('publicando', imovel.id);`<br>- r2 SEG: viola<br>    `const TOKEN_PORTAL = '***.FAKEassinatura';` |
| LS-A031 | r2 SEG | mec | regex | viola | T | — |  |
| LS-A031 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A032 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `if (ok % 100 === 0) console.log(`${ok}/${linhas.length}`);`<br>    `console.log(`importados: ${ok}`);` |
| LS-A032 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A032 | r3 JSDOC | sem | v=0.08 a=0.06 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A033 | r1 VALID | sem | v=0.74 a=0.88 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-A033 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A033 | r3 DESVIO | sem | v=0.56 a=0.86 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-A034 | r1 JSDOC | sem | v=0.14 a=0.97 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A034 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A034 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A035 | r1 JSDOC | sem | v=0.81 a=0.96 g=T · bl=F | viola | T | — | - r1 JSDOC: viola (p=0.81)<br>    `export function formatarReais(v: number): string {` |
| LS-A035 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A035 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A036 | r1 SEG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A036 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A036 | r3 TODO | mec | regex | ok | F | — |  |

## Conjunto `teste` — 66 diffs (arquivo versão 2026-10-01, autor fable)

### Semânticas (69 regras; 33 com gabarito true/false, 36 nulas) — Jev × baseline, por desenho

`acerto_duro` = viola ≥ 0,5 × gabarito (no desenho `aplicabilidade`, aplica < LIMIAR_APLICA conta como não viola). `cobertura`/`acerto_decididos`/`revisa` = com a FAIXA (0.3, 0.7) (e LIMIAR_APLICA 0.3). `erro_caro` = gabarito true que saiu `ok` ou `nao_se_aplica` (violação real passou). `falso_alarme` = gabarito false que saiu `viola`. `nulo_nao_se_aplica` = gabarito nulo que o lint marcou como não aplicável (só o desenho `aplicabilidade` sabe dizer isso); `nulo_sem_alarme` = nulo que não virou `viola`. `baseline` = regex de gatilho + palavra-chave (`None` = sem gatilho = não se aplica).

| desenho | n | acerto_duro | cobertura | acerto_decididos | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | nulo_sem_alarme | brier | baseline_acerto | baseline_erro_caro | baseline_falso_alarme | baseline_nulo_sinalizado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| valvula | 33 | 0.909 | 0.909 | 0.967 | 3 | 1/18 | 0/15 | 0/36 | 34/36 | 0.062 | 0.727 | 3/18 | 6/15 | 36/36 |
| aplicabilidade | 33 | 0.909 | 0.909 | 0.967 | 3 | 1/18 | 0/15 | 25/36 | 34/36 | 0.062 | 0.727 | 3/18 | 6/15 | 36/36 |
| gatilho | 33 | 0.909 | 0.909 | 0.967 | 3 | 1/18 | 0/15 | 36/36 | 36/36 | 0.062 | 0.727 | 3/18 | 6/15 | 36/36 |

### O Noul de aplicabilidade separa `null` de `false`?

Distribuição de `aplica` (e mediana de `viola`) por gabarito. Se os nulos ficam abaixo do LIMIAR_APLICA e os true/false acima, o Noul auxiliar paga; se o `viola` dos nulos já é baixo, a válvula na instrução basta; `sem_gatilho_regex` é o que a regex de gatilho (desenho `gatilho`) diria — para nulo, quanto maior melhor; para true, cada um é uma violação que o código esconderia do Jev.

| gabarito | n | aplica_min | aplica_p50 | aplica_max | abaixo_de_LIMIAR_APLICA | sem_gatilho_regex | viola_p50 |
|---|---|---|---|---|---|---|---|
| null | 36 | 0.030 | 0.100 | 0.960 | 25 | 36 | 0.090 |
| F | 15 | 0.590 | 0.960 | 0.970 | 0 | 1 | 0.150 |
| T | 18 | 0.250 | 0.950 | 0.970 | 1 | 0 | 0.890 |

| LIMIAR_APLICA | acerto_duro | cobertura | erro_decididos | erro_caro | falso_alarme | nulo_nao_se_aplica |
|---|---|---|---|---|---|---|
| 0.200 | 0.909 | 0.909 | 0.033 | 1/18 | 0/15 | 24/36 |
| 0.300 | 0.909 | 0.909 | 0.033 | 1/18 | 0/15 | 25/36 |
| 0.400 | 0.909 | 0.909 | 0.033 | 1/18 | 0/15 | 25/36 |
| 0.500 | 0.909 | 0.909 | 0.033 | 1/18 | 0/15 | 27/36 |

### Mecânicas (137 regras) — regex × gabarito (tem de ser 100%; menos é bug)

Acerto 1.000 (137/137); 0 erro(s).

| regra | n | acerto |
|---|---|---|
| DROP | 8 | 1.000 |
| LOG | 44 | 1.000 |
| SEG | 66 | 1.000 |
| TODO | 19 | 1.000 |

### Cobertura × erro por faixa — `valvula`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.091 | 0 | 3/18 | 0/15 | 33/36 |
| 0.3–0.7 | 0.909 | 0.033 | 3 | 1/18 | 0/15 | 34/36 |
| 0.2–0.8 | 0.818 | 0.037 | 6 | 1/18 | 0/15 | 34/36 |
| 0.1–0.9 | 0.333 | 0.000 | 22 | 0/18 | 0/15 | 35/36 |
| 0.2–0.7 | 0.879 | 0.034 | 4 | 1/18 | 0/15 | 34/36 |
| 0.3–0.8 | 0.848 | 0.036 | 5 | 1/18 | 0/15 | 34/36 |
| 0.2–0.9 | 0.697 | 0.043 | 10 | 1/18 | 0/15 | 35/36 |

### Cobertura × erro por faixa — `aplicabilidade`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.091 | 0 | 3/18 | 0/15 | 33/36 |
| 0.3–0.7 | 0.909 | 0.033 | 3 | 1/18 | 0/15 | 34/36 |
| 0.2–0.8 | 0.818 | 0.037 | 6 | 1/18 | 0/15 | 34/36 |
| 0.1–0.9 | 0.364 | 0.083 | 21 | 1/18 | 0/15 | 35/36 |
| 0.2–0.7 | 0.879 | 0.034 | 4 | 1/18 | 0/15 | 34/36 |
| 0.3–0.8 | 0.848 | 0.036 | 5 | 1/18 | 0/15 | 34/36 |
| 0.2–0.9 | 0.697 | 0.043 | 10 | 1/18 | 0/15 | 35/36 |

### Cobertura × erro por faixa — `gatilho`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.091 | 0 | 3/18 | 0/15 | 36/36 |
| 0.3–0.7 | 0.909 | 0.033 | 3 | 1/18 | 0/15 | 36/36 |
| 0.2–0.8 | 0.848 | 0.036 | 5 | 1/18 | 0/15 | 36/36 |
| 0.1–0.9 | 0.364 | 0.000 | 21 | 0/18 | 0/15 | 36/36 |
| 0.2–0.7 | 0.909 | 0.033 | 3 | 1/18 | 0/15 | 36/36 |
| 0.3–0.8 | 0.848 | 0.036 | 5 | 1/18 | 0/15 | 36/36 |
| 0.2–0.9 | 0.727 | 0.042 | 9 | 1/18 | 0/15 | 36/36 |

### Por regra semântica e por dificuldade — `gatilho`

| chave | n | nulos | acerto_duro | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | baseline | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| DESVIO | 7 | 6 | 0.857 | 1 | 0/3 | 0/4 | 6/6 | 0.857 | 1/3 |
| JSDOC | 6 | 18 | 0.667 | 1 | 1/5 | 0/1 | 18/18 | 1.000 | 0/5 |
| SQL | 8 | 9 | 1.000 | 1 | 0/5 | 0/3 | 9/9 | 0.750 | 2/5 |
| VALID | 12 | 3 | 1.000 | 0 | 0/5 | 0/7 | 3/3 | 0.500 | 0/5 |

| dificil | n | nulos | acerto_duro | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | baseline | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| False | 5 | 4 | 1.000 | 0 | 0/2 | 0/3 | 4/4 | 0.600 | 0/2 |
| True | 28 | 32 | 0.893 | 3 | 1/16 | 0/12 | 32/32 | 0.750 | 3/16 |

### Custo e latência (medidos na chamada real; do cache também)

Uma requisição por diff com regras semânticas (2 Nouls por regra); diff só com mecânicas custa zero. Aqui 1 PR = 1 diff de 10–60 linhas; PR real tem vários arquivos e custa proporcionalmente mais.

| requisicoes | do_cache | perguntas | p50_ms | p95_ms | tokens_por_diff | US$_por_diff | US$_por_mil_PRs | modelo |
|---|---|---|---|---|---|---|---|---|
| 56 | 56 | 138 | 251 | 375 | 1189 | 0.0000499 | 0.0499 | jev-1.13.0 |

### Caso a caso (desenho padrão `gatilho`)

Por regra: `viola`/`aplica` do Jev, `g` = gatilho por regex (mecânica: regex), veredito com faixa, gabarito, baseline (T/F/null). `erro` = veredito decidido ≠ gabarito; `caro` = violação real que passou; `alarme` = false → viola; `nulo→viola` = nulo apontado como violação. Última coluna: comentário de CI do diff.

| id | regra | tipo | jev/regra | veredito | gab | marca | comentário de CI |
|---|---|---|---|---|---|---|---|
| LS-T001 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `accessKeyId: '***',` |
| LS-T001 | r2 LOG | mec | regex | ok | F | — |  |
| LS-T001 | r3 JSDOC | sem | v=0.09 a=0.08 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T002 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `console.log('gerando boleto', proposta.id, proposta.valor);` |
| LS-T002 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T002 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T003 | r1 JSDOC | sem | v=0.12 a=0.97 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T003 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T003 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T003 | r4 TODO | mec | regex | ok | F | — |  |
| LS-T004 | r1 DROP | mec | regex | viola | T | — | - r1 DROP: viola<br>    `ALTER TABLE imoveis DROP COLUMN cep_antigo;` |
| LS-T004 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T004 | r3 SQL | sem | v=0.07 a=0.09 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T005 | r1 VALID | sem | v=0.96 a=0.97 g=T · bl=T | viola | T | — | - r1 VALID: viola (p=0.96)<br>    `router.post('/corretores', async (req, res) => {` |
| LS-T005 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T005 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T006 | r1 VALID | sem | v=0.96 a=0.97 g=T · bl=T | viola | T | — | - r1 VALID: viola (p=0.96)<br>    `router.put('/propostas/:id', async (req, res) => {` |
| LS-T006 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T006 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T006 | r4 JSDOC | sem | v=0.95 a=0.96 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T007 | r1 VALID | sem | v=0.07 a=0.05 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-T007 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T007 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T008 | r1 DESVIO | sem | v=0.18 a=0.94 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T008 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T008 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T009 | r1 DESVIO | sem | v=0.49 a=0.90 g=T · bl=T | revisa | T | — | - r1 DESVIO: revisa (p=0.49)<br>    `// eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion` |
| LS-T009 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T009 | r3 JSDOC | sem | v=0.40 a=0.49 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T010 | r1 DESVIO | sem | v=0.09 a=0.15 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-T010 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T010 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T011 | r1 JSDOC | sem | v=0.89 a=0.97 g=T · bl=T | viola | T | — | - r1 JSDOC: viola (p=0.89)<br>    `export const diasAteProposta = (visita: Date, proposta: Date): number =>`<br>    `export function fimDeSemana(d: Date): boolean {` |
| LS-T011 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T011 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T012 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `# chave de sandbox usada nos testes manuais: ***` |
| LS-T012 | r2 DESVIO | sem | v=0.08 a=0.07 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T012 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T013 | r1 JSDOC | sem | v=0.07 a=0.11 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-T013 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T013 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T013 | r4 TODO | mec | regex | ok | F | — |  |
| LS-T014 | r1 JSDOC | sem | v=0.95 a=0.96 g=T · bl=T | viola | T | — | - r1 JSDOC: viola (p=0.95)<br>    `export async function buscarPorTelefone(telefone: string) {` |
| LS-T014 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T014 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T015 | r1 SQL | sem | v=0.16 a=0.89 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T015 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T015 | r3 JSDOC | sem | v=0.19 a=0.81 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T016 | r1 SQL | sem | v=0.56 a=0.80 g=T · bl=T | revisa | T | — | - r1 SQL: revisa (p=0.56)<br>    `const r = await db.execute(sql`SELECT bairro, count(*) AS n FROM imoveis GROUP BY bairro`);` |
| LS-T016 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T016 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T017 | r1 SQL | sem | v=0.82 a=0.91 g=T · bl=F | viola | T | — | - r1 SQL: viola (p=0.82)<br>    `const r = await client.query('SELECT * FROM propostas WHERE corretor_id = $1 AND etapa = $2', [corretorId, 'analise']);` |
| LS-T017 | r2 JSDOC | sem | v=0.81 a=0.86 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T017 | r3 SEG | mec | regex | ok | F | — |  |
| LS-T017 | r4 LOG | mec | regex | ok | F | — |  |
| LS-T018 | r1 LOG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T018 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T018 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T019 | r1 LOG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T019 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T019 | r3 JSDOC | sem | v=0.08 a=0.04 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T020 | r1 LOG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T020 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T020 | r3 JSDOC | sem | v=0.08 a=0.07 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T021 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `// atalho para quem ainda escreve console.log(...) por hábito: usa o pino por baixo` |
| LS-T021 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T021 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T022 | r1 TODO | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T022 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T022 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T023 | r1 TODO | mec | regex | viola | T | — | - r1 TODO: viola<br>    `await zap.enviar(v.lead.telefone, textoLembrete(v)); // FIXME texto fixo` |
| LS-T023 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T023 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T024 | r1 DROP | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T024 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T024 | r3 SQL | sem | v=0.07 a=0.10 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T025 | r1 DROP | mec | regex | viola | T | — | - r1 DROP: viola<br>    `await db.execute(sql`ALTER TABLE leads DROP COLUMN score_antigo`);`<br>    `await db.execute(sql`ALTER TABLE leads DROP COLUMN score`);` |
| LS-T025 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T025 | r3 SQL | sem | v=0.17 a=0.23 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T026 | r1 DROP | mec | regex | viola | T | — | - r1 DROP: viola<br>    `await db.execute(sql.raw(`DROP TABLE IF EXISTS ${nome}`));` |
| LS-T026 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T026 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T027 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `return Usuario(email="ana.teste@exemplo.com.br", ***, papel="corretor")` |
| LS-T027 | r2 DESVIO | sem | v=0.07 a=0.06 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T027 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T028 | r1 SEG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T028 | r2 LOG | mec | regex | ok | F | — |  |
| LS-T028 | r3 JSDOC | sem | v=0.08 a=0.11 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T029 | r1 VALID | sem | v=0.17 a=0.76 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-T029 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T029 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T030 | r1 VALID | sem | v=0.96 a=0.97 g=T · bl=T | viola | T | — | - r1 VALID: viola (p=0.96)<br>    `router.get('/imoveis/busca', async (req, res) => {` |
| LS-T030 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T030 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T030 | r4 TODO | mec | regex | ok | F | — |  |
| LS-T031 | r1 VALID | sem | v=0.18 a=0.92 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T031 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T031 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T032 | r1 DESVIO | sem | v=0.15 a=0.96 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T032 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T032 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T033 | r1 DESVIO | sem | v=0.93 a=0.94 g=T · bl=T | viola | T | — | - r1 DESVIO: viola (p=0.93)<br>    `corpo = mensagem.body  # type: ignore` |
| LS-T033 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T033 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T034 | r1 SQL | sem | v=0.78 a=0.95 g=T · bl=T | viola | T | — | - r1 SQL: viola (p=0.78)<br>    `cur.execute("UPDATE leads SET contatado = true WHERE id = %s", (lead_id,))` |
| LS-T034 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T034 | r3 DESVIO | sem | v=0.64 a=0.90 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T035 | r1 SEG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T035 | r2 DESVIO | sem | v=0.07 a=0.07 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T035 | r3 SQL | sem | v=0.07 a=0.07 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T036 | r1 VALID | sem | v=0.09 a=0.97 g=T · bl=T | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T036 | r2 LOG | mec | regex | ok | F | — |  |
| LS-T036 | r3 SEG | mec | regex | ok | F | — |  |
| LS-T037 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `console.log('movendo', id, equipeId);` |
| LS-T037 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T037 | r3 JSDOC | sem | v=0.08 a=0.08 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T038 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `const TOKEN_VALIDO = '***.FAKEassinaturaDeTeste';` |
| LS-T038 | r2 LOG | mec | regex | ok | F | — |  |
| LS-T038 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T039 | r1 DROP | mec | regex | viola | T | — | - r1 DROP: viola<br>    `ALTER TABLE leads DROP COLUMN importacao_lote_antigo;` |
| LS-T039 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T039 | r3 SQL | sem | v=0.08 a=0.10 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T040 | r1 JSDOC | sem | v=0.26 a=0.44 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-T040 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T040 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T041 | r1 JSDOC | sem | v=0.46 a=0.73 g=T · bl=T | revisa | T | — | - r1 JSDOC: revisa (p=0.46)<br>    `export default correlacao;` |
| LS-T041 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T041 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T042 | r1 DESVIO | sem | v=0.83 a=0.83 g=T · bl=F | viola | T | — | - r1 DESVIO: viola (p=0.83)<br>    `// @ts-expect-error` |
| LS-T042 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T042 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T043 | r1 DESVIO | sem | v=0.13 a=0.88 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T043 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T043 | r3 JSDOC | sem | v=0.17 a=0.50 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T044 | r1 SQL | sem | v=0.96 a=0.97 g=T · bl=T | viola | T | — | - r1 SQL: viola (p=0.96)<br>    `await db.execute(sql`TRUNCATE leads, visitas, propostas RESTART IDENTITY CASCADE`);` |
| LS-T044 | r2 LOG | mec | regex | ok | F | — |  |
| LS-T044 | r3 SEG | mec | regex | ok | F | — |  |
| LS-T045 | r1 SQL | sem | v=0.18 a=0.78 g=T · bl=F | ok | F | — | - r2 TODO: viola<br>    `// TODO trocar pelo builder quando a versão com window functions sair` |
| LS-T045 | r2 TODO | mec | regex | viola | T | — |  |
| LS-T045 | r3 SEG | mec | regex | ok | F | — |  |
| LS-T046 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `***` |
| LS-T046 | r2 SQL | sem | v=0.06 a=0.03 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T046 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T047 | r1 SEG | mec | regex | ok | F | — | - r3 JSDOC: viola (p=0.97)<br>    `export function chaveGeocode(): string {` |
| LS-T047 | r2 LOG | mec | regex | ok | F | — |  |
| LS-T047 | r3 JSDOC | sem | v=0.97 a=0.97 g=T · bl=T | viola | T | — |  |
| LS-T048 | r1 VALID | sem | v=0.07 a=0.97 g=T · bl=T | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T048 | r2 JSDOC | sem | v=0.16 a=0.94 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T048 | r3 SEG | mec | regex | ok | F | — |  |
| LS-T048 | r4 LOG | mec | regex | ok | F | — |  |
| LS-T049 | r1 DROP | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T049 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T049 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T050 | r1 DROP | mec | regex | viola | T | — | - r1 DROP: viola<br>    `-- renomeia em vez de DROP COLUMN + ADD, para não perder os valores` |
| LS-T050 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T050 | r3 SQL | sem | v=0.07 a=0.11 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T051 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `console.log('[dev]', fn.name);` |
| LS-T051 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T051 | r3 JSDOC | sem | v=0.09 a=0.11 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T052 | r1 SEG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T052 | r2 VALID | sem | v=0.08 a=0.05 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T052 | r3 SQL | sem | v=0.07 a=0.05 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T052 | r4 JSDOC | sem | v=0.09 a=0.08 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T053 | r1 VALID | sem | v=0.12 a=0.97 g=T · bl=T | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T053 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T053 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T053 | r4 JSDOC | sem | v=0.24 a=0.92 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T054 | r1 VALID | sem | v=0.12 a=0.97 g=T · bl=T | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T054 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T054 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T055 | r1 VALID | sem | v=0.96 a=0.96 g=T · bl=T | viola | T | — | - r1 VALID: viola (p=0.96)<br>    `router.post('/notificacoes', async (req, res) => {` |
| LS-T055 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T055 | r3 TODO | mec | regex | ok | F | — |  |
| LS-T056 | r1 TODO | mec | regex | viola | T | — | - r1 TODO: viola<br>    `// TODO gerar também a miniatura de 300px` |
| LS-T056 | r2 LOG | mec | regex | ok | F | — |  |
| LS-T056 | r3 SEG | mec | regex | ok | F | — |  |
| LS-T057 | r1 JSDOC | sem | v=0.14 a=0.25 g=T · bl=T | ok | T | caro | nenhuma regra violada ou em revisão |
| LS-T057 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T057 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T058 | r1 SQL | sem | v=0.22 a=0.59 g=F · bl=null | nao_se_aplica | F | — | - r2 SEG: viola<br>    `con = psycopg.connect(host="db.exemplo.com.br", user="relatorios", ***)` |
| LS-T058 | r2 SEG | mec | regex | viola | T | — |  |
| LS-T058 | r3 DESVIO | sem | v=0.18 a=0.55 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T059 | r1 SEG | mec | regex | ok | F | — | - r2 VALID: viola (p=0.87)<br>    `router.post('/webhooks/portal', header('x-portal-secret').isString().notEmpty(), async (req, res) => {` |
| LS-T059 | r2 VALID | sem | v=0.87 a=0.93 g=T · bl=T | viola | T | — |  |
| LS-T059 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T060 | r1 VALID | sem | v=0.18 a=0.96 g=T · bl=T | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T060 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T060 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T061 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `***,`<br>- r2 DROP: viola<br>    `DROP TABLE sessoes_antigas;` |
| LS-T061 | r2 DROP | mec | regex | viola | T | — |  |
| LS-T061 | r3 LOG | mec | regex | ok | F | — |  |
| LS-T062 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `POSTGRES_***` |
| LS-T062 | r2 LOG | mec | regex | ok | F | — |  |
| LS-T062 | r3 JSDOC | sem | v=0.07 a=0.03 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T063 | r1 JSDOC | sem | v=0.09 a=0.08 g=F · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-T063 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T063 | r3 SQL | sem | v=0.10 a=0.10 g=F · bl=null | nao_se_aplica | null | — |  |
| LS-T064 | r1 DESVIO | sem | v=0.16 a=0.95 g=T · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T064 | r2 LOG | mec | regex | ok | F | — |  |
| LS-T064 | r3 SEG | mec | regex | ok | F | — |  |
| LS-T065 | r1 VALID | sem | v=0.08 a=0.97 g=T · bl=T | ok | F | — | nenhuma regra violada ou em revisão |
| LS-T065 | r2 TODO | mec | regex | ok | F | — |  |
| LS-T065 | r3 SEG | mec | regex | ok | F | — |  |
| LS-T066 | r1 SQL | sem | v=0.75 a=0.88 g=T · bl=F | viola | T | — | - r1 SQL: viola (p=0.75)<br>    `const r = await db.execute(sql.raw(`SELECT ${colunas.join(', ')} FROM ${tabela} LIMIT 1000`));` |
| LS-T066 | r2 SEG | mec | regex | ok | F | — |  |
| LS-T066 | r3 LOG | mec | regex | ok | F | — |  |
