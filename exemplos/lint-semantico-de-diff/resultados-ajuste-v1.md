# Resultados — lint-semantico-de-diff

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, regex, faixa e baseline: `perguntas.py`; composição: `lint.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Desenho padrão: `aplicabilidade`; FAIXA (0.2, 0.8); LIMIAR_APLICA 0.3.

Critério de continuar/descartar (fixado antes do teste): no teste, com o desenho padrão, a FAIXA e o LIMIAR_APLICA acima: (1) mecanicas: 100% (menos é bug de código); (2) semantico duro: acerto duro (noul ≥ 0,5, gabarito true/false) ≥ baseline + 15 p.p.; (3) erro caro: ≤ 5% das violações reais (gabarito true) passam como `ok` ou `nao_se_aplica`; (4) falso alarme: ≤ 10% dos gabaritos false viram `viola`; (5) nulo: ≥ 80% dos gabaritos null NÃO viram `viola`.

Versão em afinação (NÃO congelada): `perguntas.py` sha256 2fa9fb36dfd65dbe… · `lint.py` sha256 853ef2ce6c14b7a4… · `run.py` sha256 5c5167f9a8137cc8… · `dados/teste.json` sha256 9c029ea96c18d5b8…

## Lado a lado

| conjunto | desenho | n_sem | acerto_duro | baseline | cobertura | acerto_decididos | erro_caro | falso_alarme | nulo_nao_se_aplica | nulo_sem_alarme | brier | mecânicas | p50_ms | p95_ms | US$_por_mil_PRs | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | valvula | 19 | 0.947 | 0.789 | 0.895 | 1.000 | 0/10 | 0/9 | 0/22 | 20/22 | 0.046 | 76/76 | 278 | 368 | 0.0451 | jev-1.13.0 |
| ajuste | aplicabilidade | 19 | 0.947 | 0.789 | 0.895 | 1.000 | 0/10 | 0/9 | 13/22 | 20/22 | 0.046 | 76/76 | 278 | 368 | 0.0451 | jev-1.13.0 |

## Conjunto `ajuste` — 36 diffs (arquivo versão 2026-10-01, autor fable)

### Semânticas (41 regras; 19 com gabarito true/false, 22 nulas) — Jev × baseline, por desenho

`acerto_duro` = viola ≥ 0,5 × gabarito (no desenho `aplicabilidade`, aplica < LIMIAR_APLICA conta como não viola). `cobertura`/`acerto_decididos`/`revisa` = com a FAIXA (0.2, 0.8) (e LIMIAR_APLICA 0.3). `erro_caro` = gabarito true que saiu `ok` ou `nao_se_aplica` (violação real passou). `falso_alarme` = gabarito false que saiu `viola`. `nulo_nao_se_aplica` = gabarito nulo que o lint marcou como não aplicável (só o desenho `aplicabilidade` sabe dizer isso); `nulo_sem_alarme` = nulo que não virou `viola`. `baseline` = regex de gatilho + palavra-chave (`None` = sem gatilho = não se aplica).

| desenho | n | acerto_duro | cobertura | acerto_decididos | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | nulo_sem_alarme | brier | baseline_acerto | baseline_erro_caro | baseline_falso_alarme | baseline_nulo_sinalizado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| valvula | 19 | 0.947 | 0.895 | 1.000 | 2 | 0/10 | 0/9 | 0/22 | 20/22 | 0.046 | 0.789 | 4/10 | 0/9 | 22/22 |
| aplicabilidade | 19 | 0.947 | 0.895 | 1.000 | 2 | 0/10 | 0/9 | 13/22 | 20/22 | 0.046 | 0.789 | 4/10 | 0/9 | 22/22 |

### O Noul de aplicabilidade separa `null` de `false`?

Distribuição de `aplica` (e mediana de `viola`) por gabarito. Se os nulos ficam abaixo do LIMIAR_APLICA e os true/false acima, o Noul auxiliar paga; se o `viola` dos nulos já é baixo, a válvula na instrução basta.

| gabarito | n | aplica_min | aplica_p50 | aplica_max | abaixo_de_LIMIAR_APLICA | viola_p50 |
|---|---|---|---|---|---|---|
| null | 22 | 0.050 | 0.280 | 0.780 | 13 | 0.090 |
| F | 9 | 0.260 | 0.980 | 0.980 | 1 | 0.140 |
| T | 10 | 0.950 | 0.970 | 0.970 | 0 | 0.950 |

| LIMIAR_APLICA | acerto_duro | cobertura | erro_decididos | erro_caro | falso_alarme | nulo_nao_se_aplica |
|---|---|---|---|---|---|---|
| 0.200 | 0.947 | 0.895 | 0.000 | 0/10 | 0/9 | 11/22 |
| 0.300 | 0.947 | 0.895 | 0.000 | 0/10 | 0/9 | 13/22 |
| 0.400 | 0.947 | 0.895 | 0.000 | 0/10 | 0/9 | 17/22 |
| 0.500 | 0.947 | 0.895 | 0.000 | 0/10 | 0/9 | 18/22 |

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
| 0.5–0.5 | 1.000 | 0.053 | 0 | 1/10 | 0/9 | 19/22 |
| 0.3–0.7 | 0.895 | 0.000 | 2 | 0/10 | 0/9 | 20/22 |
| 0.2–0.8 | 0.895 | 0.000 | 2 | 0/10 | 0/9 | 20/22 |
| 0.1–0.9 | 0.526 | 0.000 | 9 | 0/10 | 0/9 | 22/22 |
| 0.2–0.7 | 0.895 | 0.000 | 2 | 0/10 | 0/9 | 20/22 |
| 0.3–0.8 | 0.895 | 0.000 | 2 | 0/10 | 0/9 | 20/22 |
| 0.2–0.9 | 0.842 | 0.000 | 3 | 0/10 | 0/9 | 22/22 |

### Cobertura × erro por faixa — `aplicabilidade`

| faixa | cobertura | erro_decididos | revisa | erro_caro | falso_alarme | nulo_sem_alarme |
|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.053 | 0 | 1/10 | 0/9 | 19/22 |
| 0.3–0.7 | 0.895 | 0.000 | 2 | 0/10 | 0/9 | 20/22 |
| 0.2–0.8 | 0.895 | 0.000 | 2 | 0/10 | 0/9 | 20/22 |
| 0.1–0.9 | 0.579 | 0.000 | 8 | 0/10 | 0/9 | 22/22 |
| 0.2–0.7 | 0.895 | 0.000 | 2 | 0/10 | 0/9 | 20/22 |
| 0.3–0.8 | 0.895 | 0.000 | 2 | 0/10 | 0/9 | 20/22 |
| 0.2–0.9 | 0.842 | 0.000 | 3 | 0/10 | 0/9 | 22/22 |

### Por regra semântica e por dificuldade — `aplicabilidade`

| chave | n | nulos | acerto_duro | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | baseline | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| DESVIO | 4 | 3 | 1.000 | 0 | 0/2 | 0/2 | 1/3 | 0.750 | 1/2 |
| JSDOC | 6 | 12 | 1.000 | 1 | 0/4 | 0/2 | 7/12 | 0.833 | 1/4 |
| SQL | 5 | 4 | 1.000 | 0 | 0/1 | 0/4 | 4/4 | 0.800 | 1/1 |
| VALID | 4 | 3 | 0.750 | 1 | 0/3 | 0/1 | 1/3 | 0.750 | 1/3 |

| dificil | n | nulos | acerto_duro | revisa | erro_caro | falso_alarme | nulo_nao_se_aplica | baseline | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| False | 1 | 3 | 1.000 | 0 | 0/0 | 0/1 | 3/3 | 1.000 | 0/0 |
| True | 18 | 19 | 0.944 | 2 | 0/10 | 0/8 | 10/19 | 0.778 | 4/10 |

### Custo e latência (medidos na chamada real; do cache também)

Uma requisição por diff com regras semânticas (2 Nouls por regra); diff só com mecânicas custa zero. Aqui 1 PR = 1 diff de 10–60 linhas; PR real tem vários arquivos e custa proporcionalmente mais.

| requisicoes | do_cache | perguntas | p50_ms | p95_ms | tokens_por_diff | US$_por_diff | US$_por_mil_PRs | modelo |
|---|---|---|---|---|---|---|---|---|
| 30 | 0 | 82 | 278 | 368 | 1074 | 0.0000451 | 0.0451 | jev-1.13.0 |

### Caso a caso (desenho padrão `aplicabilidade`)

Por regra: `viola`/`aplica` do Jev (mecânica: regex), veredito com faixa, gabarito, baseline (T/F/null). `erro` = veredito decidido ≠ gabarito; `caro` = violação real que passou; `alarme` = false → viola; `nulo→viola` = nulo apontado como violação. Última coluna: comentário de CI do diff.

| id | regra | tipo | jev/regra | veredito | gab | marca | comentário de CI |
|---|---|---|---|---|---|---|---|
| LS-A001 | r1 VALID | sem | v=0.06 a=0.98 · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A001 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A001 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A001 | r4 JSDOC | sem | v=0.12 a=0.29 · bl=null | nao_se_aplica | null | — |  |
| LS-A002 | r1 VALID | sem | v=0.97 a=0.97 · bl=T | viola | T | — | - r1 VALID: viola (p=0.97)<br>    `router.post('/visitas', async (req, res) => {` |
| LS-A002 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A002 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A002 | r4 TODO | mec | regex | ok | F | — |  |
| LS-A003 | r1 DESVIO | sem | v=0.10 a=0.97 · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A003 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A003 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A003 | r4 JSDOC | sem | v=0.11 a=0.50 · bl=null | ok | null | — |  |
| LS-A004 | r1 JSDOC | sem | v=0.95 a=0.97 · bl=T | viola | T | — | - r1 JSDOC: viola (p=0.95)<br>    `export function valorFinanciado(valor: number, entrada: number): number {` |
| LS-A004 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A004 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A005 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `// para testar local usar o token sk_test_FAKEb81c0d2e9f7a (conta sandbox do time)` |
| LS-A005 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A005 | r3 JSDOC | sem | v=0.08 a=0.17 · bl=null | nao_se_aplica | null | — |  |
| LS-A006 | r1 JSDOC | sem | v=0.08 a=0.14 · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-A006 | r2 SQL | sem | v=0.07 a=0.15 · bl=null | nao_se_aplica | null | — |  |
| LS-A006 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A006 | r4 LOG | mec | regex | ok | F | — |  |
| LS-A007 | r1 SQL | sem | v=0.14 a=0.98 · bl=F | ok | F | — | - r2 JSDOC: viola (p=0.96)<br>    `export async function funilPorCorretor(mes: string) {` |
| LS-A007 | r2 JSDOC | sem | v=0.96 a=0.97 · bl=T | viola | T | — |  |
| LS-A007 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A007 | r4 LOG | mec | regex | ok | F | — |  |
| LS-A008 | r1 SQL | sem | v=0.91 a=0.95 · bl=F | viola | T | — | - r1 SQL: viola (p=0.91)<br>    `const r = await db.execute(sql`SELECT * FROM leads WHERE telefone = ${telefone}`);`<br>- r2 JSDOC: viola (p=0.86) |
| LS-A008 | r2 JSDOC | sem | v=0.86 a=0.71 · bl=null | viola | null | nulo→viola |  |
| LS-A008 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A009 | r1 LOG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A009 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A009 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A010 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `// console.log('job', job.id);` |
| LS-A010 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A010 | r3 JSDOC | sem | v=0.07 a=0.09 · bl=null | nao_se_aplica | null | — |  |
| LS-A011 | r1 TODO | mec | regex | viola | T | — | - r1 TODO: viola<br>    `// TODO: CRM-418 tratar proposta com dois compradores` |
| LS-A011 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A011 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A011 | r4 JSDOC | sem | v=0.08 a=0.18 · bl=null | nao_se_aplica | null | — |  |
| LS-A012 | r1 DROP | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A012 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A012 | r3 SQL | sem | v=0.09 a=0.12 · bl=null | nao_se_aplica | null | — |  |
| LS-A013 | r1 DROP | mec | regex | viola | T | — | - r1 DROP: viola<br>    `ALTER TABLE imoveis DROP COLUMN area_total_antiga;` |
| LS-A013 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A013 | r3 SQL | sem | v=0.08 a=0.10 · bl=null | nao_se_aplica | null | — |  |
| LS-A014 | r1 DROP | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A014 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A014 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A015 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `senha: 'Senha@Teste123',` |
| LS-A015 | r2 JSDOC | sem | v=0.15 a=0.30 · bl=null | ok | null | — |  |
| LS-A015 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A016 | r1 SEG | mec | regex | ok | F | — | - r3 JSDOC: viola (p=0.97)<br>    `export function senhaValida(s: string): boolean {` |
| LS-A016 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A016 | r3 JSDOC | sem | v=0.97 a=0.97 · bl=T | viola | T | — |  |
| LS-A017 | r1 VALID | sem | v=0.07 a=0.30 · bl=null | ok | null | — | nenhuma regra violada ou em revisão |
| LS-A017 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A017 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A018 | r1 VALID | sem | v=0.10 a=0.19 · bl=null | nao_se_aplica | null | — | nenhuma regra violada ou em revisão |
| LS-A018 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A018 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A018 | r4 TODO | mec | regex | ok | F | — |  |
| LS-A019 | r1 SQL | sem | v=0.11 a=0.26 · bl=null | nao_se_aplica | F | — | nenhuma regra violada ou em revisão |
| LS-A019 | r2 JSDOC | sem | v=0.11 a=0.37 · bl=null | ok | null | — |  |
| LS-A019 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A020 | r1 VALID | sem | v=0.33 a=0.97 · bl=T | revisa | T | — | - r1 VALID: revisa (p=0.33)<br>    `router.put('/imoveis/:id', param('id').isUUID(), body('preco').isInt({ min: 0 }), async (req, res) => {` |
| LS-A020 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A020 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A021 | r1 DESVIO | sem | v=0.95 a=0.97 · bl=T | viola | T | — | - r1 DESVIO: viola (p=0.95)<br>    `from .legado import *  # noqa` |
| LS-A021 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A021 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A022 | r1 DESVIO | sem | v=0.20 a=0.97 · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A022 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A022 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A023 | r1 SQL | sem | v=0.16 a=0.97 · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A023 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A023 | r3 DESVIO | sem | v=0.09 a=0.32 · bl=null | ok | null | — |  |
| LS-A024 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `senha = "Mudar123!"` |
| LS-A024 | r2 DESVIO | sem | v=0.06 a=0.05 · bl=null | nao_se_aplica | null | — |  |
| LS-A024 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A025 | r1 DROP | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A025 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A025 | r3 SQL | sem | v=0.07 a=0.09 · bl=null | nao_se_aplica | null | — |  |
| LS-A026 | r1 DESVIO | sem | v=0.91 a=0.97 · bl=F | viola | T | — | - r1 DESVIO: viola (p=0.91)<br>    `// @ts-ignore ok`<br>- r4 JSDOC: viola (p=0.82) |
| LS-A026 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A026 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A026 | r4 JSDOC | sem | v=0.82 a=0.58 · bl=null | viola | null | nulo→viola |  |
| LS-A027 | r1 SEG | mec | regex | viola | T | — | - r1 SEG: viola<br>    `curl -H "Authorization: Bearer ghp_FAKE4kd92nsl02KSjd8" https://api.github.com/repos/exemplo/crm` |
| LS-A027 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A027 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A028 | r1 TODO | mec | regex | viola | T | — | - r1 TODO: viola<br>    `// FIXME remover filtro quando a agenda externa parar de devolver cancelados` |
| LS-A028 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A028 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A029 | r1 VALID | sem | v=0.89 a=0.95 · bl=F | viola | T | — | - r1 VALID: viola (p=0.89)<br>    `router.get('/imoveis', query('bairro').optional().isString(), async (req, res) => {`<br>    `router.delete('/imoveis/:id', async (req, res) => {` |
| LS-A029 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A029 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A029 | r4 JSDOC | sem | v=0.14 a=0.28 · bl=null | nao_se_aplica | null | — |  |
| LS-A030 | r1 SQL | sem | v=0.18 a=0.98 · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A030 | r2 JSDOC | sem | v=0.18 a=0.98 · bl=F | ok | F | — |  |
| LS-A030 | r3 SEG | mec | regex | ok | F | — |  |
| LS-A031 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `console.log('publicando', imovel.id);`<br>- r2 SEG: viola<br>    `const TOKEN_PORTAL = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJjcm0ifQ.FAKEassinatura';` |
| LS-A031 | r2 SEG | mec | regex | viola | T | — |  |
| LS-A031 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A032 | r1 LOG | mec | regex | viola | T | — | - r1 LOG: viola<br>    `if (ok % 100 === 0) console.log(`${ok}/${linhas.length}`);`<br>    `console.log(`importados: ${ok}`);` |
| LS-A032 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A032 | r3 JSDOC | sem | v=0.07 a=0.06 · bl=null | nao_se_aplica | null | — |  |
| LS-A033 | r1 VALID | sem | v=0.56 a=0.78 · bl=null | revisa | null | — | - r1 VALID: revisa (p=0.56)<br>    `@router.post("/leads", status_code=201)` |
| LS-A033 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A033 | r3 DESVIO | sem | v=0.14 a=0.43 · bl=null | ok | null | — |  |
| LS-A034 | r1 JSDOC | sem | v=0.10 a=0.98 · bl=F | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A034 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A034 | r3 LOG | mec | regex | ok | F | — |  |
| LS-A035 | r1 JSDOC | sem | v=0.56 a=0.97 · bl=F | revisa | T | — | - r1 JSDOC: revisa (p=0.56)<br>    `export function formatarReais(v: number): string {` |
| LS-A035 | r2 SEG | mec | regex | ok | F | — |  |
| LS-A035 | r3 TODO | mec | regex | ok | F | — |  |
| LS-A036 | r1 SEG | mec | regex | ok | F | — | nenhuma regra violada ou em revisão |
| LS-A036 | r2 LOG | mec | regex | ok | F | — |  |
| LS-A036 | r3 TODO | mec | regex | ok | F | — |  |
