# Lint semântico de diff (convenções do time sobre pull requests)

## Problema
Convenções do time ("desvio proposital de lint leva comentário dizendo o porquê", "JSDoc com `@description`",
"rota nova valida com express-validator", "nada de segredo literal", "`DROP` sem confirmação não passa") só são
conferidas por humano na revisão; o lint sintático não vê semântica. Aqui: 8 regras literais (4 mecânicas, 4
semânticas; texto em [dados/LEIA-ME.md](dados/LEIA-ME.md)), diffs sintéticos de um CRM imobiliário (TypeScript/
Express/Drizzle e Python, 10–60 linhas), gabarito `true` (viola) / `false` (não viola) / `null` (o diff não toca
o assunto da regra). Candidato a job de CI do parque: comentário no PR com IDs e trechos, sem texto gerado.

## Quem faz o quê
| Parte | Onde | Por quê |
|---|---|---|
| regras **mecânicas** (segredo literal, `console.log(`, `DROP TABLE/COLUMN` sem `confirmado por`, `TODO`/`FIXME` sem ticket) | código (`lint.mecanica`: as regex do LEIA-ME sobre linhas `+`) | a regra é literal e o gabarito É a regex; o Jev não vê essas regras |
| **aplicabilidade** de cada regra semântica (há função nova exportada? supressão em linha `+`? rota nova lendo `req.*`? SQL cru fora de migration?) | código (regex de gatilho em `perguntas.BASELINE`; desenho `gatilho`) | é a metade mecânica da regra; o código sabe quais linhas são novas, o Jev não lê a notação do diff com segurança (abaixo) |
| **julgamento** da regra disparada (o comentário justifica? a tag está na função certa? a cadeia vem com `validationResult`?) | Jev, 1 Noul por regra, todas as regras do diff numa requisição (`rules[i]`) | julgamento sobre texto livre com resposta fechada |
| veredito por regra (`viola` / `revisa` / `ok` / `nao_se_aplica`) e comentário de CI | código (`FAIXA` em `perguntas.py`; `lint.comentario_ci`) | política por risco; o Jev não gera texto — o comentário são IDs, probabilidades e linhas do próprio diff |

## Desenho (`perguntas.py` = perguntas, regex, faixa, baseline, critério; `lint.py` = leitura do diff e composição)
- **State**: `{"diff": <diff unificado inteiro>, "rules": [texto das regras semânticas]}` — 1 requisição por diff;
  diff só com mecânicas não chama nada (10 dos 66 do teste).
- **Segredo e teto, antes da chamada** (rodada 3, revisão do Codex): a regex de SEG roda em TODAS as linhas do diff
  (`+`, `-`, contexto) e o trecho casado entra no state como `***`; a mesma máscara passa por todo trecho do
  comentário de CI, venha ele de que regra vier (`lint.mascarar`; bateria em `testa_mascara.py`). Diff acima de
  `TETO_LINHAS` 120 / `TETO_CARACTERES` 8.000 (`perguntas.py`) não chama nada e não é truncado: as semânticas saem
  `revisa` com motivo "diff grande", contadas à parte no relatório.
- **Pergunta de violação** (inglês; a regra fica em pt-BR): explica a notação (`+` adicionada, `-` removida, resto
  contexto; "nova" = linha de declaração com `+`) e pergunta "Does the code ADDED in `diff` violate the rule in
  `rules[i]`, read exactly as written?" · `true` = elemento exigido ausente, fora do lugar que a regra nomeia, ou
  que não diz o que ela pede ("ok" não é porquê; "E" exige os dois) · `false` = satisfeita ou **a regra não toca o
  diff** (válvula).
- **Pergunta auxiliar de aplicabilidade**, mesma requisição: "Does `diff` ADD something of the kind the rule
  governs?" — medida, não adotada (abaixo).
- **Três desenhos para o `null`**, todos da MESMA requisição (zero chamada extra): `valvula` (só o Noul de
  violação), `aplicabilidade` (Noul auxiliar < `LIMIAR_APLICA` 0,3 → `nao_se_aplica`), **`gatilho`** (regex do
  código decide; padrão).
- **Faixa** `(0,3, 0,7)`: noul ≤ 0,3 → `ok`; ≥ 0,7 → `viola`; meio → `revisa`. Escolhida no ajuste v2 dentro da
  lacuna 0,28–0,60 entre `false` e `true`, com margem para a variação entre chamadas (máx. 0,15 medido).
- **Validação estrita**: ID faltando, bool, string, NaN ou valor fora de [0,1] é exceção (`_comum/congelamento.py`),
  nunca `ok`. Regra mecânica sem regex conhecida é exceção.
- **Baseline de código** (só semânticas): gatilho por regex + palavra-chave em linhas `+` (`@description`; comentário
  na própria linha ou na anterior; `express-validator` no import adicionado E `validationResult`; linha de
  comentário acima do SQL). Sem gatilho → `null`.
- **Critério de continuar/descartar**, fixado antes do teste (dicionário em `perguntas.py`, congelado no manifesto
  `congelamento.json` com `perguntas.py`, `lint.py`, `run.py` e `dados/teste.json`): (1) mecânicas 100% · (2) acerto
  semântico duro ≥ 0,90 **e** ≥ baseline + 10 p.p. · (3) ≤ 5% das violações reais passam (`ok`/`nao_se_aplica`) ·
  (4) ≤ 10% dos `false` viram `viola` · (5) ≥ 80% dos `null` não viram `viola`. Por que +10 e não +15: o baseline
  já embute a metade mecânica das regras (0,789 no ajuste); +15 exigiria ~0,94, impossível por construção com
  baseline ≥ 0,85.

## Afinação (ajuste: 36 diffs, 41 regras semânticas — 19 com gabarito, 22 nulas — e 76 mecânicas; 88% difíceis)
| | v1 | v2 (notação do diff na instrução; "E" exige os dois; elemento em outra função não conta) |
|---|---|---|
| semântico duro (19) | 0,947 (18/19) | **1,000** |
| erro caro · falso alarme | 0/10 · 0/9 | 0/10 · 0/9 |
| nulos sem alarme (22), faixa 0,3/0,7 — `valvula` / `gatilho` | 20/22 / 22/22 | 18/22 / **22/22** |
| nulos que o Noul auxiliar marca (< 0,3) | 13/22 | 12/22 |
| Brier | 0,046 | 0,028 |
| mecânicas | 76/76 | 76/76 |

v1 → v2 acrescentou só a NOTAÇÃO à instrução (a metade literal que faltava, limite #1), não um caso — e o overfit
foi medido: os dois nulos que v1 apontava como violação (função **modificada** lida como nova: LS-A008 0,86,
LS-A026 0,82) caíram só para 0,78 e dois outros nulos **subiram** (LS-A029 0,14 → 0,75; LS-A033 0,56 → 0,74).
O Noul auxiliar errou junto nesses cinco (aplica 0,41–0,93). Só a regex de gatilho os separou (22/22) — por
isso `gatilho` virou o padrão, com o risco declarado antes do teste: forma de "função nova"/"SQL cru" que a regex
não conheça esconde a violação do Jev. v1 inteiro em [resultados-ajuste-v1.md](resultados-ajuste-v1.md).

## Resultados no teste (jev-1.13.0, 2026-10-01; 66 diffs, 69 regras semânticas — 18 `true`, 15 `false`, 36 nulas — e 137 mecânicas; 81% difíceis)
Três rodadas, cada uma com o relatório gerado pelo script: 1 (cega) em `resultados-rodada1.md`, 2 em
`resultados-rodada2.md`, 3 (atual) em `resultados.md`. Desenho padrão `gatilho`, FAIXA (0,3, 0,7).

### Rodada 1 (cega, manifesto gravado em 2026-10-01 12:23:20; [resultados-rodada1.md](resultados-rodada1.md))
| Teste (n) | Jev `gatilho` | Jev `valvula` / `aplicabilidade` | baseline de código |
|---|---|---|---|
| semântico, acerto duro (noul ≥ 0,5; 33) | **0,879** (29/33) | 0,909 | 0,727 |
| com faixa: cobertura · erro entre decididos · revisões | 90,9% · 6,7% (2/30) · 3 | 90,9% · 3,3% · 3 | — |
| **erro caro**: violação real que passou (18) | **2/18** (1 escondido pela regex, 1 do Jev) | 1/18 | 3/18 |
| falso alarme: `false` → `viola` (15) | **0/15** | 0/15 | 6/15 |
| nulo: não virou `viola` (36) · marcado `nao_se_aplica` | **36/36 · 36/36** | 34/36 · 0 / 25 de 36 | 36/36 |
| mecânicas (137: SEG 66, LOG 44, TODO 19, DROP 8) | **137/137** | idem | idem (mesmo código) |
| Brier (33) | 0,062 | 0,062 | — |
| requisições · tokens por diff · p50 · p95 | 56 (10 diffs sem chamada) · 1.189 · 251 ms · 375 ms | idem | 0 |
| US$ por diff · por mil PRs (1 PR = 1 diff desta amostra) | 0,00005 · **0,05** | idem | 0 |

**Critério (rodada 1): (1) ✓ · (2) 0,879 < 0,90 ✗ (≥ baseline + 10 p.p. ✓) · (3) 2/18 = 11% ✗ · (4) ✓ · (5) ✓** —
o desenho **não passou** cego. Os números ficam como rodaram.

### Rodada 2 (não cega: só o conserto da regex de gatilho do SQL; respostas do Jev idênticas, do cache, 56/56; [resultados-rodada2.md](resultados-rodada2.md))
A regex `db\.execute\(\s*sql\`` não disparava em `db.execute(sql.raw(...))` (LS-T066) e escondia a violação do
Jev, que a via (0,75). Com `\bdb\.execute\(`: duro **0,909** (30/33), erro decididos 3,3% (1/30), erro caro
**1/18**, falso alarme 0/15, nulos 36/36, 3 revisões; o resto igual. Critério: (2) ✓ · **(3) 1/18 = 5,6% > 5% ✗**
(LS-T057, abaixo) · demais ✓. Segunda correção da rodada 2, também sem efeito em número: o comentário de CI
ecoava o literal de segredo do diff (`TOKEN = "ghp_…"`) — o validador do repositório pegou; agora o trecho casado
pela regex de SEG sai mascarado (`***`), porque bot que repete o segredo no PR espalha o vazamento. Manifesto da
rodada 2 gravado em 2026-10-01 12:28:52; os anteriores (12:23:20 da rodada cega; 12:25:40 só da regex) em
`congelamentos-anteriores/`.

Por regra (rodada 2, Jev × baseline, acerto duro): VALID **12/12 × 6/12** (o baseline não vê import nem middleware
`validar` em linha de contexto; o Jev lê o arquivo) · SQL 8/8 × 6/8 · DESVIO 6/7 × 6/7 · **JSDOC 4/6 × 6/6** (regra
estrutural: a regex ganha).

### Rodada 3 (pós-revisão do Codex, não cega; manifesto gravado em 2026-10-01 12:47:41; `resultados.md`)
Revisão adversarial do Codex sobre a rodada 2: quatro achados, três aplicados aqui e um de família. O teste já
estava aberto: esta rodada **não é cega** e não mexe em pergunta, faixa, regex de regra nem critério.

| Achado | O que mudou | Efeito medido |
|---|---|---|
| 1 (grav. 1) o diff ia inteiro ao Jev antes de a regex de SEG rodar | `lint.pedido` mascara o diff (todas as linhas) antes de montar o state | state novo em 9 diffs → **9 requisições novas** (abaixo); 77 do cache |
| 2 (grav. 1) máscara só no trecho da regra SEG | `lint.compor` mascara todo trecho de toda regra antes do comentário | nenhum comentário dos 102 diffs mudou (nenhum trecho de LOG/TODO/DROP/gatilho carregava segredo); provado só pela bateria |
| 3 (grav. 2) sem teto de tamanho | `TETO_LINHAS`/`TETO_CARACTERES`; acima → `revisa` "diff grande", sem chamada, contado à parte | **nenhum caso dispara** (maior diff: 24 linhas, 847 caracteres); provado só pela bateria |
| 4 (grav. 2, família) cabeçalho dizia "antes de abrir o teste" em toda rodada | `run.py`: "cega ou não, conforme a rodada declarada no README" | só texto |

**Por que mascarar e não mandar o diff com segredo direto para `revisa`**: a máscara preserva a medição (os 9
diffs e suas 10 regras semânticas continuam julgados; cobertura igual) e o valor do segredo não é assunto de
nenhuma regra semântica. Custo: o trecho casado some inteiro (`senha = "…"` vira `***`), então o Jev vê menos
daquela linha.

**Números (teste, `gatilho`)**: idênticos aos da rodada 2 — duro 0,909 (30/33), erro entre decididos 3,3% (1/30),
erro caro 1/18, falso alarme 0/15, nulos 36/36, 3 revisões, mecânicas 137/137; Brier 0,062 → 0,061. Critério:
como na rodada 2, **(3) 1/18 = 5,6% > 5% ✗** (LS-T057); o desenho continua sem passar.

**Chamadas novas: 9** (ajuste LS-A005, A015, A024; teste LS-T001, T012, T027, T046, T058, T062), `JEV_MODO=auto`,
11.386 tokens, US$ 0,0005, 294–373 ms; as outras 77 requisições vieram do cache. Nesses 9 diffs há 10 regras
semânticas, **todas `nao_se_aplica` pelo gatilho nas duas rodadas** (9 nulas e LS-T058 r1 SQL, gabarito `false`):
o veredito do desenho padrão não tinha como mudar. O que se moveu, regra a regra (viola · aplica, rodada 2 → 3):
A005 JSDOC, T001 JSDOC, T012 DESVIO, T062 JSDOC sem mudança · A015 JSDOC 0,22 → 0,20 · 0,40 → 0,36 · A024 DESVIO
0,06 → 0,10 · 0,06 → 0,07 · T027 DESVIO viola 0,07 → 0,08 · T046 SQL aplica 0,03 → 0,04 · T058 SQL 0,22 → 0,20 · 0,59 →
0,60 · T058 DESVIO 0,18 → 0,16 · 0,55 → 0,59. Máximo 0,04, dentro da variação entre chamadas idênticas (máx. 0,15
medido): não dá para separar efeito da máscara de ruído. Fora do padrão, dois valores cruzaram borda de grade:
T058 SQL (0,20) sai de `revisa` nas faixas 0,2–x de `valvula`/`aplicabilidade` (uma revisão a menos) e A015
(aplica 0,36) passa a contar em LIMIAR_APLICA 0,4 no ajuste (13 → 14 de 22). Nada muda na faixa adotada.

**Bateria** (`testa_mascara.py`, sem chave nem rede; dublê no lugar do Jev porque o que se testa é código): 13
diffs com segredo em contextos diferentes (linha de `console.log`, `TODO`, `DROP`, cada gatilho semântico, linha de
contexto, linha removida, Python, arquivo de teste, dois segredos na linha, comentário de documentação) — 0 valor
bruto no state, em 27 trechos e no comentário; sem a máscara a mesma bateria acusa 100 falhas. Confere também o
teto por linhas e por caracteres, e que diff dentro do teto sem resposta continua sendo erro.

O manifesto da rodada 2 (12:28:52) foi para `congelamentos-anteriores/`. Varredura da família (achado 4): os
irmãos `juiz-de-eval`, `imovel-errado` e `conferencia-de-promessas` já tinham a frase nova.

## Erros um a um (teste, desenho padrão)
1. **LS-T066 SQL** (`// dinâmico` + `db.execute(sql.raw(...))`, gabarito viola): regex de gatilho estreita demais →
   `nao_se_aplica`, o Jev (0,75) nunca foi consultado. **Erro caro de código**, o risco declarado do desenho
   `gatilho`. Corrigido na rodada 2.
2. **LS-T057 JSDOC** (função **renomeada**: `-export async function buscarPorFone` / `+export async function
   buscarPorTelefone`, sem JSDoc; gabarito viola por decisão do rotulador — "o diff não distingue"): Jev 0,14,
   aplicabilidade 0,25 → `ok`. O gatilho disparou (o código sabia que havia `+export function`); o Jev usou bom
   senso ("é a mesma função") onde a regra foi lida ao pé da letra. **Erro caro em todos os desenhos**; único da
   rodada 2.
3. **LS-T041 JSDOC** (`const correlacao: RequestHandler = (...) =>` + `export default correlacao`; viola): 0,46 →
   `revisa`. A regra lista três formas e esta não é nenhuma; o gatilho (`export default` de arrow definida no diff,
   decisão do LEIA-ME) disparou e o Jev hesitou — desfecho certo para o que o texto da regra não cobre.
4. **LS-T009 DESVIO** (porquê três linhas acima, com código no meio; viola): 0,49 → `revisa`. "Imediatamente
   anterior" lido com hesitação; o baseline (que mede adjacência) acertou.
5. **LS-T016 SQL** (SQL cru **sem comentário nenhum**; viola): 0,56 → `revisa`, enquanto comentário que só descreve
   deu 0,82 (LS-T017) e 0,85 (LS-A008). Ausência de elemento exigido é condição negativa (limite #4): o Jev fica
   menos seguro no caso mais fácil.
6. **Nulos com noul alto** (só aparecem nos desenhos sem regex): LS-T006 r4 JSDOC **0,95** (rota nova num arquivo
   cujo `export default router` é linha de contexto), LS-T017 r2 JSDOC 0,81 (função modificada), LS-T034 r3 DESVIO
   0,64 (Python sem supressão alguma), LS-T009 r3 JSDOC 0,40. Em `valvula` dois viram `viola`; o Noul auxiliar
   também os dá como aplicáveis (0,86–0,96).

## Lições
1. **A aplicabilidade é do código quando a estrutura denuncia**: a regex sinalizou 36/36 nulos; a válvula na
   instrução deixou 2 virar alarme; o Noul auxiliar marcou só 25/36 e errou nos mesmos casos que o Noul principal
   (aplica ≥ 0,41 nos cinco nulos ruins do ajuste). O Noul auxiliar **não** paga: mesma confusão, mais tokens.
2. **O Jev não lê a notação do diff com segurança**: função modificada vira "nova" (A008, A026, T006, T017) mesmo com
   a notação explicada na instrução (v2 moveu 0,86 → 0,78, não resolveu). É indireção (limite #4) — o código sabe
   exatamente quais linhas são novas e deve DIZER (ou filtrar), não pedir ao modelo para descobrir.
3. **Decompor mais do que eu decompus**: das quatro "semânticas", só duas têm miolo semântico (o comentário
   *justifica* por que o builder não serve? o comentário *diz o porquê*?). JSDoc (`@description` imediatamente acima)
   e VALID (cadeia E `validationResult`) são estruturais pelo LEIA-ME — o baseline fez JSDOC 6/6 contra 4/6 do Jev.
   Para SQL/DESVIO, presença e posição do comentário são código; o Jev deveria receber só o comentário e a pergunta
   **positiva** ("this comment states a reason why the builder cannot do it") — a ausência (T016, 0,56) nunca
   chegaria a ele.
4. **Decisão de rotulagem contra-intuitiva tem de estar na pergunta ou no código** (renomear = nova, T057): onde a
   regra é literal e o bom senso discorda, o Jev vai de bom senso. O custo da regra literal apareceu nas mecânicas
   também (LS-A010 `// console.log(` comentado viola; LS-A013 `confirmado por` com linha em branco no meio viola) —
   ali o gabarito é a regex e o exemplo paga para mostrar.
5. **Faixa**: 0,3/0,7 deu 3 revisões e 1 erro decidido (T057, 0,14 — fora de qualquer faixa razoável); 0,1/0,9
   zeraria o erro caro ao custo de 21 revisões (cobertura 36%). Erros moram perto do limiar, exceto o de bom senso.
6. **Baseline forte onde a regra é estrutural, fraco onde o contexto importa**: VALID 6/12 porque o import de
   `express-validator` e o middleware `validar` já existiam (linhas de contexto) — o Jev leu o arquivo (12/12).
7. **Critério "≥ baseline + 15 p.p." não serve quando o baseline embute metade da regra**; +10 e ≥ 0,90 era o
   justo — e a rodada cega falhou mesmo assim, por dois erros caros, um deles de regex.

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só, mesmo fornecedor do construtor; diffs curtos de um
  arquivo. n = 33 regras semânticas com gabarito no teste: 1 regra = 3 p.p.; 18 violações reais: 1 = 5,6%.
- Uma versão (`jev-1.13.0`), uma rodada cega; T041 (0,46), T009 (0,49) e T016 (0,56) podem trocar de faixa.
- As regras "semânticas" aqui são mais estruturais que as de um time real; regra em texto livre ("código legível")
  não foi medida. O desenho `gatilho` tem a recall da regex como teto (T066).
- Guardrail, não fronteira: comentário que *argumenta* ("o builder não serve porque sim") move o Noul (limite #6).
- A máscara tem a recall da regex de SEG: segredo que ela não conhece (chave JSON entre aspas, valor passado como
  argumento — LS-T064) segue para o Jev e para o comentário. O teto (120 linhas / 8.000 caracteres) é 2× a faixa
  especificada, não um limite medido: entre 24 linhas (o maior diff medido) e o teto o lint roda fora do que se mediu.
- PR real tem vários arquivos: dividir por arquivo (10–60 linhas por state), custo proporcional; US$ 0,05 por mil
  diffs desta amostra, 250 ms p50 por diff.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa sem congelamento.json ou com arquivo mudado)
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 diffs, só encanamento → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # roda o ajuste e grava o manifesto antes de abrir o teste
set JEV_MODO=gravado                              # reproduz tudo do cache/, sem chave
..\..\.venv\Scripts\python.exe testa_mascara.py   # bateria da máscara de segredo e do teto (sem chave, sem rede)
```
Como job de CI: `git diff` da base para o PR → um state por arquivo → mecânicas em código (segredo mascarado antes
de qualquer chamada; arquivo acima do teto → `revisa`) → só regras disparadas vão ao Jev (1 requisição por arquivo)
→ comentário com `lint.comentario_ci`; `revisa` pede olhar humano.
