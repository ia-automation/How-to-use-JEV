# Auditor de evidência (relatório de agente × registros) — supported / contradicted / insufficient_evidence

O relatório do coder diz "rota funcionando em produção", "migration nos dois bancos", "testado e publicado"; os
registros anexados mostram um build local, um teste com dublê, só o dev. Antes de aceitar a fatia, decidir se os
registros **sustentam a afirmação inteira**, se algum a **contradiz**, ou se **falta prova** — e apontar quais
registros sustentam ou contradizem. Os números são gerados pelo `run.py`: a **rodada 1 (cega, a que conta como
teste)** está em [`resultados-rodada1.md`](resultados-rodada1.md); a **rodada 2 (pós-revisão do Codex, não cega)**,
em [`resultados.md`](resultados.md) — o que mudou entre elas está na seção "Rodada 2".
Candidato a portão do rito `/fechar-fatia` do parque: "o relatório do coder prova o que afirma?". **Nada é
aprovado daqui**: `supported` é um veredito sobre a relação afirmação × registros; `insufficient_evidence` e
`revisa` mandam pedir prova ou chamar humano.

## Problema
A dor é a **falsa aprovação**: uma afirmação não sustentada ou contradita que passa como `supported` — o rito
confiaria num "testado e publicado" que foi só testado, num "nos dois bancos" que foi só dev, num "integração
funcionando" cujo teste dublou a integração. É o erro caro, contado à parte. Do outro lado, o falso alarme
(`supported` → `contradicted`) trava uma fatia pronta; e `revisa`/`insufficient_evidence` custam uma ida ao
humano ou um pedido de prova. Regras de rotulagem em [`dados/LEIA-ME.md`](dados/LEIA-ME.md) — precedência
contradicted > insufficient_evidence > supported; decomposição da afirmação em o quê / onde / estado / quantidade;
"o registro mais recente prevalece"; 200 ≠ funcionando; build ≠ teste ≠ deploy; manual não sustenta prova mecânica.

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Ordem temporal dos registros (carimbo `10:02 ·`, `· 2026-09-30 14:40`; sem carimbo, a ordem da lista) | código (`auditor.ordenar`) | o Jev não compara datas (limite #3); o state vai em ordem cronológica e a pergunta diz "oldest first" |
| "O mais recente prevalece": entre registros do MESMO ASSUNTO — tipo, objeto, ambiente, componente (rodada 2; na rodada 1 era "do mesmo tipo") —, o sinal forte mais recente apaga o sinal oposto dos anteriores | código (`auditor.assunto`, `auditor.superados`) | verde velho + vermelho novo → só o vermelho conta (e o inverso); assuntos diferentes não se apagam (dev aplicado + prod falhando; deploy ok + saúde 503); **registro cujo assunto o código não reconhece não supera nem é superado** — os dois ficam |
| Cobertura %, latência ms, réplicas N/N, versão x.y.z, revisão (hash), número de migration | código (`auditor.checks`, `auditor.triagem`), ANTES da chamada, resultado no state como `checks` | comparar 78,4 × 80 é conta (limite #2); revisão/migration diferente → registro neutralizado, **fora do state** (rodada 2; na rodada 1 ficava no state e só o código o ignorava); limiar/versão só é comparado em registro pertinente (mesmo ambiente e componente) e vigente (o número mais recente do mesmo assunto) — aí, se falha → `contradicted` direto |
| `records[i]` sustenta parte da afirmação (mesma revisão/ambiente)? | Jev, Noul absoluto `supports_i` por registro | é o que vira `registros_de_apoio` de `supported` e `insufficient_evidence` |
| `records[i]` relata uma parte falsa? | Jev, Noul absoluto `contradicts_i` por registro | falta de prova não é contradição — a pergunta diz isso em letras (localhost, outra revisão, mock, cancelada → `false`) |
| A afirmação está provada em cada PARTE: coisa (`object_shown`), estado alcançado (`state_shown`), cada ambiente nomeado (`place_shown`), escopo — todos/nenhum/N/limiar/revisão (`scope_shown`)? | Jev, 4 Nouls por afirmação; o código exige os quatro | a leitura "todas as partes cobertas" decomposta em sinais atômicos (NÚCLEO §5); o código não enumera as partes de uma frase livre |
| "Os registros juntos provam a afirmação inteira" | Jev, Noul global `established` — **informativo**, não decide | medido contra as partes no ajuste e no teste (abaixo): deixa passar "todos passando" com pulados e nega o "404 afirmado" |
| Faixas, precedência, veredito, apoio, 2ª passada | código (`auditor.compor`, números em `perguntas.py`) | política: muda editando número, sem chamada nova |
| Registros válidos antes da chamada (1–8, IDs únicos, tipo conhecido, texto) · resposta validada (todo ID esperado, nenhum a mais, número real em [0,1]) | código → **erro**, nunca `supported` | NÚCLEO §10; ID repetido religaria duas respostas ao mesmo registro em silêncio |

Fora do Jev de propósito: produzir a prova que falta (é o coder), e autorizar a fatia (é o rito).

## Desenho
- **State** `{"claim", "records": [{"id", "kind", "text"}], "checks": [{"record", "check", "claimed", "observed", "holds"}]}`
  — registros em ordem cronológica, tipo literal em inglês (`manual_note`, `test_log`…), e os checks que o código
  já comparou. ~3.700 tokens por afirmação, dos quais ~3.300 são as perguntas (2n+5 Nouls com critérios longos).
- **Uma requisição por afirmação**, 2n+5 Nouls (n = registros, 2–6 nos dados): `supports_i`, `contradicts_i`,
  `object_shown`, `state_shown`, `place_shown`, `scope_shown`, `established`. Cada registro é julgado pelo
  próprio conteúdo ("judge the record on its own"): recência é do código.
- **Política** (`auditor.compor`): check numérico/versão que falha → `contradicted`; registro de outra
  revisão/migration e registro superado saem do jogo; maior `contradicts` vivo ≥ 0,7 → `contradicted` (apoio =
  os ≥ 0,5); 0,3–0,7 → `revisa` se as partes dizem provada, senão `insufficient_evidence` (mesma ação: pedir
  prova); senão as 4 partes ≥ 0,7 → `supported` (exige ≥ 1 registro com `supports` ≥ 0,5), alguma ≤ 0,3 →
  `insufficient_evidence`, meio → `revisa`.
- **2ª passada** só quando um registro foi superado e nenhuma contradição ficou de pé: os Nouls de parte da 1ª
  passada ainda viram o registro superado; a 2ª manda o state sem ele (NÚCLEO §5: a resposta decidiu o próximo
  state). 1/31 no ajuste, 2/73 no teste — não mudou veredito em nenhum (ver "O que falhou"). Na rodada 2, com a
  recência por assunto: 1/31 e 0/73.
- **Triagem antes da chamada** (`auditor.triagem`, rodada 2): registro de outra revisão/migration e registro com
  número refeito por outro mais recente do mesmo assunto saem do state; registro de outro ambiente/componente fica,
  mas não gera check numérico; state que fica sem registro não vai ao Jev (`insufficient_evidence` pelo código).
- **Afinação no ajuste** (31 afirmações, 26 difíceis), 3 rodadas, 0 faixa movida:
  1. desenho inicial (`supports_i`, `contradicts_i`, `established`): acerto 0,645, cobertura 0,81, 0 falsa
     aprovação — `established` rígido (sustentados em 0,09–0,33) e `contradicts` lendo homolog/localhost/cancelada
     como contradição parcial (0,47–0,64 → `revisa`);
  2. perguntas reescritas com regras do LEIA-ME ("parte não declarada não é exigida", "falta de prova não é
     contradição") + dúvida de contradição com nada provado → `insufficient_evidence`: acerto 0,774, cobertura
     0,84, **1 falsa aprovação** ("todos passando" com 4 pulados, `established` 0,82);
  3. 4 Nouls por parte, composição em código: `parts` acerto 0,806, cobertura 0,81, **0 falsa aprovação, 1,000
     entre os decididos**; `established` sozinho 0,774 com 1 falsa aprovação; `both` 0,806 mas erra o "404 afirmado".
     `COMPOSICAO = "parts"`. A curva do ajuste mostra que a faixa única 0,5 cobriria 100% com 1 falsa aprovação
     ("200 com corpo vazio", `state_shown` 0,52); 0,3–0,7 fica.

## Baseline (código, sem Jev)
`auditor.baseline`, regra do briefing: palavra de falha num registro (`failed`, `ERROR`, `rejected`, 5xx, `rollback`,
`cancelad`…) → `contradicted`; afirmação de produção com registro de localhost/homolog/dev e nenhum de prod →
`contradicted` (o LEIA-ME diz insuficiente — o baseline erra de propósito); palavra-chave da afirmação (sem as
genéricas) presente em registro de processo → `supported`; senão `insufficient_evidence`. Mede o que "a palavra
está lá" resolve: nada de escopo, ambiente, dublê, recência. Segundo baseline, **`sempre pede prova`**: tudo
`insufficient_evidence` — zero falsa aprovação ao custo de nunca aprovar.

## Critério de continuar/descartar (fixado ANTES de abrir o teste, 2026-10-01 12:37; em `perguntas.CRITERIO_CONTINUAR` e no manifesto)
Continua se, no teste (73 afirmações), o Jev tiver: (1) **falsa aprovação ≤ 2% (≤ 1/73)**; (2) **acerto da relação
(revisa = erro) ≥ baseline + 0,15**. Secundário (não decide): falso alarme ≤ 2; cobertura ≥ 0,80; precisão e
recall dos `registros_de_apoio` reportados.

**Resultado: PASSOU, com o item 1 no limite** — 1 falsa aprovação (AE-T069), dentro do número fixado (≤ 1); sobre
as 48 afirmações não sustentadas são 2,1%, acima dos 2% se lidos como fração — o critério foi escrito com o
número absoluto entre parênteses e é esse que vale; fica registrado que a leitura por fração reprovaria por um
caso. (2) 0,808 ≥ 0,425 + 0,15 = 0,575 ✓. Secundário: falso alarme 0/25 ✓; cobertura 0,836 ✓; apoio precisão
0,824 / recall 0,875, conjunto exato 54/73.

## Resultados da rodada 1 — cega (`jev-1.13.0`, 2026-10-01; detalhes, curvas e caso a caso em `resultados-rodada1.md`; com o baseline corrigido, `resultados-rodada1b.md`)
Ajuste = 31 afirmações (26 difíceis: 8 supported / 8 contradicted / 15 insufficient); teste = 73 (45 difíceis:
25 / 21 / 27). Teste congelado em 2026-10-01 12:37:35 (`perguntas.py` `e0ff7f963ba22a7d…`, `auditor.py`
`2a892ba9644a51e1…`, `dados/teste.json` `6bdb935ba4030be2…`) e rodado UMA vez; relatório dessa rodada preservado
em [`resultados-rodada1.md`](resultados-rodada1.md).

| Relação | ajuste (n = 31) | teste (n = 73) |
|---|---|---|
| baseline palavra-chave: acerto · **falsa aprovação** · falso alarme · apoio P/R | 0,419 · 9/23 · 1/8 · 0,55/0,62 | 0,425 · **26/48** · 1/25 · 0,50/0,67 |
| sempre pede prova: acerto · falsa aprovação | 0,484 · 0/23 | 0,370 · 0/48 |
| **Jev** (`parts`, congelado): acerto (revisa = erro) · cobertura · acerto entre decididos · **falsa aprovação** · falso alarme · apoio P/R · apoio exato | 0,806 · 0,806 · 1,000 · 0/23 · 0/8 · 0,92/0,85 · 25/31 | **0,808 · 0,836 · 0,967 · 1/48 · 0/25 · 0,82/0,88 · 54/73** |
| Leituras de "provada" nas mesmas respostas: `established` só · `parts` · `both` · nenhuma — acerto / falsa aprovação | 0,774 / 1 · 0,806 / 0 · 0,806 / 0 · 0,774 / 6 | 0,822 / **2** · 0,808 / 1 · **0,849 / 0** · 0,877 / 9 |
| Nouls (≥ 0,5): `supports_i` · `contradicts_i` · `established` (Brier) | 0,859 · 0,969 · 0,871 (0,085) | 0,797 · 0,980 · 0,890 (0,081) |
| Trabalho do código: checks (falham) · superados · 2ª passada · reordenados | 13 (4) · 2 · 1 · 1 | 30 (7) · 3 · 2 · 1 |
| p50 / p95 · tokens por afirmação · US$ por mil afirmações | 304 / 361 ms · 3.765 · 0,158 | 285 / 432 ms · 3.722 · 0,156 |

Matriz do teste, Jev (linhas = gabarito; colunas supported / contradicted / insufficient / revisa): supported
19/0/1/5 · contradicted 0/**21**/0/0 · insufficient 1/0/19/7. Os 21 contraditos foram todos pegos — 5 pelo
código (cobertura abaixo do limiar, versão diferente, latência acima) e 16 pelo `contradicts_i` (≥ 0,71 no teste;
"lint limpo" ficou em 0,62 no ajuste). Por família difícil (teste, acerto Jev / baseline): verde velho × vermelho novo
1/1 vs 0; 404 e saúde 2/3 vs 3/3; 200 sem conteúdo 1/2 (1 revisa) vs 1/2; homolog/localhost 3/3 vs 0; **mock 0/3
(3 revisa) vs 1/3**; manual 2/4 (2 revisa) vs 1/4; lint 2/2 vs 0; outra revisão 2/2 vs 0; commit ≠ push 1/2 vs
1/2; subconjunto/pulados/cancelada 5/6 vs 2/6; dev generalizado/prod com erro 3/3 vs 1/3; aceito ≠ entregue 2/2
vs 0; build sem teste 2/2 vs 1/2; outras 6/8 vs 2/8; fáceis 25/28 vs 19/28. Curva do teste (informativa): faixa
única 0,5 → cobertura 0,99 com **3 falsas aprovações**; 0,3–0,7 (atual) → 0,84 com 1; 0,2–0,8 → 0,67 com 1.

**Mudança depois do teste, só no relatório:** o baseline recebia, nos 2 casos com 2ª passada, o state já sem o
registro superado pelo Jev (vazamento: o baseline "via" a decisão do Jev). Corrigido em `run.py` (baseline lê o
state original), manifesto gravado de novo às 12:38:39 (o anterior está em `congelamentos-anteriores/`), tudo
reproduzido do cache com zero chamada nova: as 73 linhas do Jev são idênticas às de `resultados-rodada1.md`;
o baseline do teste foi de 0,452 para 0,425 (ajuste 0,452 → 0,419). Esse relatório (rodada 1 + baseline
corrigido) está preservado em [`resultados-rodada1b.md`](resultados-rodada1b.md).

### Rodada 2 (pós-revisão do Codex, NÃO cega, com 4 chamadas novas; manifesto gravado em 2026-10-01 13:05:11; `resultados.md`)
Revisão adversarial do Codex sobre a rodada 1 (2026-10-01; triagem da sessão principal: 5 achados, 5 aceitos, mais 1
de família). O teste já tinha sido aberto: esta rodada **não aprova nada às cegas — a rodada que conta como teste é
a 1**. Nenhuma pergunta, faixa ou critério mudou; mudou código (`auditor.py`, `run.py`) e, por consequência, o state
de 4 afirmações.

| Achado | O que mudou | Efeito medido |
|---|---|---|
| 1 (grav. 1) recência agrupava por TIPO de registro | `auditor.assunto` deriva (tipo, objeto, ambiente, componente) do texto do registro; `superados` só compara registros de assunto IGUAL; assunto não reconhecido → sem recência, os dois ficam | superados: ajuste 2 → 1, teste 3 → 0; 2ª passada no teste 2 → 0. **AE-T024 virou falso alarme** (abaixo); AE-T014 ficou certo pelo motivo certo |
| 2 (grav. 1) registro neutralizado continuava no state e influía nos 4 Nouls de parte | `auditor.triagem`: registro de outra revisão/migration sai do state ANTES da chamada; `compor` não devolve `supported` de um state que ainda tem registro superado (→ `revisa`; a 2ª passada decide); state sem registro → `insufficient_evidence` sem chamada | state novo em AE-A001 e AE-T004 → **2 chamadas novas**; veredito igual nos dois; nenhum caso dos 104 chegava a `supported` por registro excluído (provado só pela bateria) |
| 3 (grav. 2) check numérico negativo decidia antes de pertinência e vigência | número só vira `check` em registro pertinente (ambiente reconhecível dentro dos que a afirmação nomeia; componente igual ao serviço afirmado) e vigente (o mais recente do mesmo assunto; o antigo sai do state) | **nenhum check negativo dos dados era de registro não pertinente ou vencido**; 2 checks POSITIVOS de homolog saíram do state (AE-A010, AE-T025) → **2 chamadas novas**, veredito igual; o resto provado só pela bateria |
| 4 (grav. 2) `_ascii()` apagava `≥`/`≤` | `≥` → `>=`, `≤` → `<=` antes de normalizar | nenhuma afirmação dos dados usa `≥`/`≤`; na bateria, 6 das 19 frases falhavam no código da rodada 1 (5 sem check; "≥ 3 réplicas" lido como "exatamente 3") |
| 5 (grav. 2) métrica de apoio contava ID solto; `supports_i` rotulava "não" todo registro de caso contradito | P/R e `exato` por par (registro, `sustenta`\|`contradiz`); `supports_i` medido só onde o gabarito rotula o registro sem ambiguidade | só métrica (abaixo): o Jev não muda; o baseline perde o crédito indevido |
| 6 (família) cabeçalho dizia "antes de abrir o teste" em toda rodada | `run.py`: "cega ou não, conforme a rodada declarada no README" | só texto |

**Assunto, como o código deriva** (só o que o registro traz escrito): *ambiente* = campo `prod` / `dev` / `homolog` /
`local` (ou `ambiente: X`) ou o host da URL (`localhost` → local, host com `homolog` → homolog, outro host fica
literal — o código não sabe qual host é produção); *componente* = serviço em forma de imagem (`api-leads:1.9.3`)
ou campo que é só o nome (`CI api-leads ·`); *objeto* = migration NNNN ou o deploy do componente, verbo + caminho da
URL, o comando de teste/build como escrito (`vitest run`, `vitest tests/agenda`, `eslint .`), push do branch, PR N.
Deploy e resposta HTTP sem ambiente reconhecível, rodada de teste sem comando escrito (`29 passed, 1 failed`), "No
migrations to apply", commit e anotação manual **não têm assunto**: não superam nem são superados. **Quando o
código não consegue dizer que dois registros falam da mesma coisa, não aplica recência — os dois ficam**, e uma
falha antiga sem assunto continua contradizendo. É o lado seguro (trava, nunca aprova) e tem custo medido: AE-T024.

| Número (teste, n = 73) | Rodada 1 (cega; baseline do 1b) | Rodada 2 | Por quê |
|---|---|---|---|
| Jev: acerto (revisa = erro) · cobertura · acerto entre decididos | 0,808 · 0,836 · 0,967 | **0,795 · 0,836 · 0,951** | um veredito mudou: AE-T024 |
| **falsa aprovação** | 1/48 (AE-T069) | **1/48 (AE-T069)** | nenhum achado toca "afirmação de ausência"; mesma resposta do cache |
| falso alarme | 0/25 | **1/25 (AE-T024)** | recência não se aplica a rodada de teste sem comando escrito |
| `revisa` | 12 | 12 | os mesmos 12 |
| Jev: apoio P/R · exato | por ID 0,824 / 0,875 · 54/73 | por par 0,824 / 0,875 · **55/73** | para o Jev, par = ID nas duas rodadas (nunca citou registro com o papel trocado). Movimento real: AE-T014 `—` → `e1` ✓, AE-T025 `e2` → `—` ✓, AE-T024 `e3` → `e1` ✗ |
| baseline: acerto · falsa aprovação · falso alarme | 0,425 · 26/48 · 1/25 | iguais | o baseline lê todos os registros, sem a triagem do auditor |
| baseline: apoio P/R · exato | por ID 0,500 / 0,672 · 24/73 | por par **0,407 / 0,547 · 18/73** | só métrica: 8 acertos por ID tinham o papel trocado — em 4 casos o baseline citava como sustentação o registro que contradiz (AE-T044, T051, T054, T058) e em 4 dizia `contradicted` citando o registro que só sustenta parte (AE-T040, T049, T062, T071). Ajuste: 0,552 / 0,615 · 11/31 → 0,414 / 0,462 · 9/31 |
| `supports_i` (≥ 0,5) · Brier · n | 0,797 · 0,128 · 148 | **0,841 · 0,107 · 126** | **22 registros ficaram fora da métrica** (fora do apoio em caso contradito; no ajuste, 8). Com as respostas da rodada 1 e a regra nova: 0,833 · 0,108 — quase todo o ganho é da métrica, não do modelo. 9 dos 22 tinham `supports` ≥ 0,5 e contavam como erro (AE-T042 e1 0,92: rollout completo, que sustenta parte) |
| `contradicts_i` (≥ 0,5) · Brier | 0,980 · 0,020 | 0,986 · 0,016 | erros 3 → 2 em 148: os 2 registros de outra revisão de AE-T004 (0,83 e 0,79) não vão mais ao Jev; entra a falha antiga de AE-T024 (0,93), que o gabarito dá por superada; AE-T014 e2 continua na borda (0,59 → 0,50) |
| leituras de "provada": `established` · `parts` · `both` · nenhuma — acerto / falsa aprovação | 0,822 / 2 · 0,808 / 1 · 0,849 / 0 · 0,877 / 9 | 0,808 / 2 · 0,795 / 1 · 0,836 / 0 · 0,877 / 8 | AE-T024 em todas; em "nenhuma", AE-T025 deixou de aprovar (`supports` de e2 0,57 → 0,48) |
| código: checks no state (falham) · fora do state · sem check · superados · 2ª passada | 30 (7) · — · — · 3 · 2 | 28 (5) · 2 · 1 · 0 · 0 | os 2 checks de revisão que falhavam saíram com os registros (AE-T004) |
| requisições · tokens por afirmação · p50 / p95 · US$ por mil | 75 · 3.722 · 285 / 432 ms · 0,156 | 73 · 3.609 · 287 / 387 ms · 0,152 | sem 2ª passada; states menores |

Ajuste (n = 31): Jev idêntico (0,806 · 0 falsa aprovação · 0 falso alarme · apoio 0,917 / 0,846 · 25/31); 1 registro
fora do state (AE-A001), 1 sem check (AE-A010), 11 checks (3 falham), 1 superado e 1 2ª passada (AE-A009, mesmo
comando `vitest run` — idêntica à da rodada 1, do cache). Critério (rodada 2): (1) 1/73 ≤ 1 ✓, de novo no limite ·
(2) 0,795 ≥ 0,425 + 0,15 ✓ · secundário: falso alarme 1 ≤ 2 ✓, cobertura 0,836 ✓ — **não vale como aprovação cega**.

**Caso a caso** (só o que se mexeu; os outros 98 têm state, resposta e veredito idênticos aos da rodada 1):
- **AE-T069 — a falsa aprovação continua.** "Deploy … sem indisponibilidade" com rollout completo: `supported`, mesmas
  partes (0,81–0,97), mesma resposta do cache. Nenhum dos 5 achados trata de afirmação de ausência.
- **AE-T043 — continua `insufficient_evidence` (gabarito `supported`).** `place_shown` 0,21 sem ambiente na frase;
  mesma resposta. Aplicabilidade pelo código (lição 3) não estava na lista aceita.
- **AE-T014 — mesmo veredito (`insufficient_evidence` ✓), agora pelo motivo certo.** Rodada 1: "prod · No migrations
  to apply" (contra) superava "dev · 0015 aplicada" por serem do mesmo tipo; a prova válida de dev saía e o apoio
  ficava vazio (gabarito: `e1`). Rodada 2: ambientes diferentes, e o registro de prod nem tem assunto — os dois
  ficam; apoio `e1` ✓; 1 requisição em vez de 2 (a 1ª passada já estava no cache). `contradicts` de e2 0,50: dúvida
  de contradição com partes não provadas (`place_shown` 0,11) → pedir prova.
- **AE-T024 — `supported` ✓ → `contradicted` ✗ (falso alarme novo).** "Testes do fila-cobranca passando" com
  `08:41 · revisão 5g5g5g5 · 29 passed, 1 failed` e `09:02 · revisão 6h6h6h6 · 30 passed (30)`: os registros não
  trazem comando, suíte nem serviço; o código não sabe se são a mesma suíte e não aplica recência; a falha antiga
  (`contradicts` 0,93) fica de pé. Na rodada 1 o acerto vinha de agrupar por tipo — o mesmo palpite que errava
  AE-T014. AE-A009, o caso gêmeo do ajuste, tem `vitest run` nos dois registros e continua com recência. Tratar
  "rodada sem comando" como um assunto só devolveria o acerto e o palpite; ficou a regra da triagem (sem assunto,
  sem recência). Na tabela por família do `resultados.md` ele aparece em "1 teste de outra revisão" (1/2): a
  heurística de família lê "revisão atual" na nota; o caso é da família 8.
- **AE-T004 e AE-A001 — mesmo veredito, state novo.** Os registros de outra revisão (T004: e2, e3; A001: e2) não vão
  mais ao Jev; sobra o commit da revisão afirmada. `state_shown` 0,11 e 0,06 seguram o `insufficient_evidence`. Efeito
  colateral que só a medição mostra: com um commit e o check `revision ok` no state, `scope_shown` **subiu** (T004
  0,04 → 0,72; A001 0,05 → 0,38) — o Noul de escopo lê "é da revisão afirmada" como escopo coberto. Não aprova
  porque as partes são exigidas juntas.
- **AE-T025 e AE-A010 — mesmo veredito, state novo.** O deploy em homolog não gera mais check de versão contra uma
  afirmação de produção; partes dentro da variação entre chamadas (`state_shown` 0,45 → 0,32 e 0,46 → 0,28). Em
  AE-T025 o commit e2 saiu do apoio (`supports` 0,57 → 0,48, borda) e o apoio passou a bater com o gabarito.
- **AE-A015 e AE-T016 — mesmo veredito, sem "superado".** Dev aplicado + prod com erro: o dev não é mais marcado
  como superado pelo prod (ambientes diferentes); `contradicted` pelo registro de prod (0,97), como antes.

**Chamadas novas: 4** (AE-A001, AE-A010, AE-T004, AE-T025), `JEV_MODO=auto`, 12.638 tokens de entrada, US$ 0,0005,
362–387 ms; as outras 101 requisições das duas seções vieram do cache (o rascunho, 5/5 do cache). Orçamento da
rodada: ≤ 150. Duas requisições do teste foram enviadas uma vez a mais: a primeira execução ficou 5 minutos parada
com a conexão fechada pelo servidor, foi encerrada à mão sem gravar resposta e repetida — o que está no `cache/` é
a resposta da repetição. O manifesto da rodada 1b (12:38:39) foi para `congelamentos-anteriores/`.

**Bateria** (`testa_auditor.py`, sem chave nem rede; dublê no lugar do Jev porque o que se testa é código): 57
verificações — 19 frases com comparador (`≥`, `≤`, `>=`, `<=`, "pelo menos", "no mínimo", "no máximo", "abaixo
de", "acima de", "menos de", vírgula decimal, `%`, ms, réplicas, limiar exato); recência só no mesmo assunto (dev ×
prod nas duas ordens, mesmo comando, alvos diferentes, rodada sem comando); triagem (outra revisão e outra migration
fora do state; cobertura 78% antiga × 85% atual; o inverso; dois números sem assunto; localhost e homolog ×
produção; outro componente); `compor` sem `supported` com superado no state; state vazio sem chamada; métrica por par.

**Visto e NÃO aplicado** (fora da lista triada): o comparador "até" casa dentro de palavra na afirmação sem acento
("update 3 réplicas" vira "≤ 3 réplicas"); pertinência de OBJETO além de ambiente e componente (cobertura de outro
módulo do mesmo serviço) o código não deriva; em caso contradito, o registro DO apoio conta como "não sustenta"
em `supports_i`, embora possa sustentar outra parte (AE-T068 e1: rollout completo com 502 na sonda, 0,93).

## O que deu certo
- **Zero falso alarme e 21/21 contradições** nos dois conjuntos: `contradicts_i` em 0,87–0,97 quando o registro
  relata falha, e ≤ 0,15 quando só não prova (localhost, mock, build sem teste) — a reescrita "RELATA uma parte
  falsa; falta de prova não é contradição" fez a diferença entre a rodada 1 (0,47–0,64) e a 2.
- **Checks em código decidiram 5 contradições do teste sem o Jev** (7 checks falhando: cobertura abaixo do
  limiar, versão diferente da afirmada em dois registros, latência acima); e neutralizaram o log de teste de
  outra revisão (família 1: 2/2).
- **Decompor "está provada" em 4 partes pegou o que o Noul global deixou passar**: "todos os testes passando" com
  4 pulados (`scope_shown` 0,24 × `established` 0,81) e, no teste, uma 2ª falsa aprovação do global. Entre os
  decididos, `parts` acerta 0,967 no teste (1,000 no ajuste).
- **Famílias do briefing**: outra revisão, homolog/localhost como produção, dev generalizado, build sem teste,
  verde velho × vermelho novo, lint "sem erros" × "limpo", aceito ≠ entregue — 100% no teste. O baseline de
  palavra-chave fica em 0–0,50 nessas famílias e aprova 26/48 afirmações sem prova.
- **`registros_de_apoio` saem do mesmo Noul que decide o apoio**: precisão 0,82 / recall 0,88 no teste, conjunto
  exato em 54/73 — sem pergunta extra.
- Custo: US$ 0,16 por mil afirmações, ~290 ms p50; um portão de rito pode auditar todas as afirmações de um
  relatório por menos de um centésimo de centavo.

## O que falhou no teste (NÃO corrigido; perguntas e faixas são as congeladas; a lista é a da rodada 1 — na rodada 2 os mesmos erros continuam e soma-se o falso alarme AE-T024, ver "Rodada 2")
1. **AE-T069 — a falsa aprovação.** "Deploy da api-leads 1.9.4 **sem indisponibilidade**" com rollout `3/3`
   completo e release: as 4 partes deram 0,81–0,97 (`state_shown` 0,92). O rollout completo foi lido como "estado
   alcançado"; a afirmação é sobre a **ausência** de um evento que ninguém mediu (sem sonda). `state_shown` fala
   de estados alcançados (passing, applied, completed); "sem indisponibilidade" não é um estado que um registro
   de rollout mostre — é uma família ("afirmação de ausência") que a pergunta não nomeia. O baseline também aprova.
2. **AE-T043 — supported → insufficient.** "Rota GET /leads/:id devolve 404 para lead inexistente" (sem ambiente
   na frase) com o 404 vindo do host de produção: `place_shown` **0,21**. A pergunta diz "se a afirmação não nomeia
   ambiente, responda true" — o Jev respondeu como se faltasse ambiente. O mesmo condicional deu 0,48 em "Suíte do
   api-leads verde" (AE-A009, ajuste). **"Responda true quando não se aplica" é indireção (limite #4)**: a
   aplicabilidade é do código (regex de produção/dev/homolog/bancos/remoto na afirmação) — não feito.
3. **11 `revisa` (lado seguro, custo de humano)**, por grupo:
   - **mock, 3/3 em `revisa`** (`state_shown` 0,46–0,59): o dublê do Zap (T011) e o `nock` do portal (T012),
     que deveriam dar não, e o `vi.mock` de um arquivo que a afirmação não toca (T010), que deveria dar sim, caíram
     todos na faixa de dúvida — a pergunta não distingue "dublê DA coisa afirmada" de "dublê no processo". Zero
     erro, zero automação nessa família.
   - **manual, 2/4** (T017 `state_shown` 0,38 — certo em espírito, mas dúvida; T018 "dono autorizou" com fonte,
     0,32): a exceção do LEIA-ME para ato humano com fonte está em `supports_i` (0,76 ✓) mas não nas partes, que
     exigem "process record" em letras. Contradição entre perguntas que o código não concilia (limite #8).
   - **borda 0,53–0,69 no `scope_shown`**: "testada e publicada" com push (T020, 0,69 — push ≠ deploy, o gabarito
     é insuficiente), "suíte inteira" com só uma pasta (T027, 0,69), latência com o check satisfeito (T052, 0,53 —
     o Jev duvida do escopo embora `checks` diga `holds: true`; o código podia dar o escopo por satisfeito quando
     todos os checks valem e a afirmação não diz "todos/nenhum/inteira"). E `object_shown` 0,62–0,67 em "mudança
     enviada ao remoto" (T032, objeto vago) e "testada e publicada" com deploy (T021).
   - **200 com lista vazia** (T006, `state_shown` 0,40), **down não testada** (T063, 0,37/0,31): dúvida onde o
     gabarito é não; a faixa 0,2–0,8 fecharia esses sem abrir nada — e cortaria a cobertura para 0,67.
4. **2ª passada não mudou veredito** (AE-A009 no ajuste; 2 no teste): o que segurava a decisão não era o registro
   superado, era a dúvida de `place_shown`/`object_shown` (item 2). O mecanismo custa 1 requisição a mais em 3%
   dos casos e fica porque é o único jeito de os Nouls de parte não verem o superado; a evidência de que ajuda
   ainda não apareceu.

## Lições
1. **Contradição se pergunta como "relata falha", não como "mostra falso"**: a 1ª versão lia ambiente diferente e
   rodada cancelada como contradição parcial; "falta de prova NÃO é contradição" no texto da pergunta levou o
   Brier de 0,032 para 0,020 e tirou 3 `revisa` do ajuste.
2. **Um Noul holístico ("provam a afirmação inteira") esconde várias perguntas**; decomposto nas partes do
   LEIA-ME, cada Noul fica literal e o código faz o "todas" — é a regra "uma condição por pergunta" aplicada à
   verificação. O preço: 4 Nouls com conflito entre si quando a afirmação é curta ("Suíte verde": sem ambiente,
   sem escopo), e o condicional "se não se aplica, true" que o Jev não honra sempre.
3. **Aplicabilidade é do código**: "a afirmação nomeia um ambiente?" e "a afirmação fixa um escopo?" são regex;
   só a parte aplicável deve ir ao Jev. Próxima versão: `place_shown` e `scope_shown` só quando o código acha a
   parte na frase (exato, limite #4 evitado).
4. **Afirmação de ausência ("sem indisponibilidade", "sem erro no console") exige registro de sonda**: um rollout
   completo não a prova. Nenhuma pergunta nomeia essa família; o gabarito a tem. É a única falsa aprovação.
5. **A faixa de dúvida é o que protege o caso do LEIA-ME que mais engana**: "200 com corpo vazio" deu
   `state_shown` 0,52 no ajuste e 0,40 no teste; limiar único 0,5 aprovaria o primeiro. No teste, 0,5 único daria
   3 falsas aprovações contra 1.
6. **Mocks moram na faixa de dúvida nas duas direções**: distinguir "dublê da coisa afirmada" de "dublê no
   processo" é uma pergunta própria (`the mocked module is the thing the claim is about`), não um critério a mais
   em `state_shown`.
7. **O baseline de palavra-chave aprova 54% do que não tem prova** (26/48): a palavra da afirmação quase sempre
   está em algum registro — o que decide é escopo, ambiente, dublê e recência, que o Jev vê e a regra não.
8. **Guardar o relatório da rodada cega antes de qualquer conserto** (mesmo de relatório): o vazamento do baseline
   na 2ª passada só ficou provado inofensivo porque as 73 linhas do Jev puderam ser comparadas uma a uma.

## Limites
- **Dados sintéticos** (Fable, um rotulador, sem ver o código), registros normalizados de 1–4 linhas: logs reais
  são longos, com ruído e caminhos; o state enxuto aqui é dado, na prática é trabalho de extração em código.
  n = 31 e 73: uma afirmação vale 1,4 ponto no teste; "1/48 falsa aprovação" é um teste de 48 afirmações.
- Um modelo (`jev-1.13.0`), uma rodada; repetir a chamada varia ~0,01 (máx. 0,15): os 11 `revisa` em 0,31–0,69
  e o `contradicts` 0,62 do "lint limpo" podem trocar de lado.
- As perguntas carregam decisões do LEIA-ME (warnings × "limpo"; retry passou; "nenhum falhou" com pulados;
  manual com fonte para ato humano): outro time com outras regras reescreve os critérios, não o código.
- O **assunto** (rodada 2) é derivado por regex sobre registros normalizados: lista fechada de comandos (`vitest`,
  `jest`, `eslint`, `tsc`, `next build`, `docker build`, `npm test`, `coverage`), ambiente como campo, serviço como
  imagem ou campo. Log real fora desse molde fica sem assunto → sem recência → falha antiga continua contradizendo
  (falso alarme, como AE-T024); nunca o contrário. Host que não é `localhost` nem `homolog` não é mapeado para
  produção: um número vindo dele é sempre tratado como pertinente.
- `checks` cobre cobertura (%, métrica `statements` por padrão), latência (ms; p95 ou valor único), réplicas,
  versão x.y.z, revisão e migration — o resto dos números fica com o Jev (limite #2).
- Não é fronteira de segurança (limite #6): um registro redigido para parecer prova ("rollout completed" num
  registro manual) move a resposta — o tipo `manual_note` ajuda, não garante.
- Um `revisa` em 6 ainda vai para humano (16%); o portão automatiza 84% com 2 erros em 61 decididos (1 falsa
  aprovação, 1 sustentada lida como insuficiente).

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa se o manifesto congelamento.json não bate)
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação (marca "em afinação")
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 casos do construtor → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # grava o manifesto (código, teste.json, critério); o anterior vai para congelamentos-anteriores/
..\..\.venv\Scripts\python.exe testa_auditor.py  # bateria do código (comparadores, recência, triagem, métrica), sem chave nem rede
set JEV_MODO=gravado                              # só o cache/ (183 respostas reais: 104 do ajuste/rascunho em 3 rodadas + 75 do teste na rodada 1 + 4 da rodada 2), sem chave
```
No Windows, use `PYTHONIOENCODING=utf-8`. Como portão: `auditor.auditar(jev, caso)` recebe `{"afirmacao",
"registros": [{"id", "tipo", "texto"}]}` e devolve `relacao` (`supported` / `contradicted` /
`insufficient_evidence` / `revisa`), `apoio` (IDs), `motivo`, os Nouls brutos e o trabalho do código (`neutros`, `vencidos`, `nao_pertinentes`,
`superados`, `passada`). Registros inválidos ou resposta fora do contrato → exceção, nunca `supported`.
