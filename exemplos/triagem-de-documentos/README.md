# Triagem de documentos (quais destes documentos têm X?) — mapa por seção × documento inteiro

"Quais destes 500 contratos têm multa por rescisão / exclusividade / reajuste fora do índice?" é leitura manual ou um
LLM por documento. Este exemplo aplica uma CONDIÇÃO escrita por advogado ou gestor a cada documento longo (4–8
seções) e devolve, por documento, `verdadeiro` / `falso` / `indecidivel` (humano lê) e a seção que prova. O que ele
MEDE é o limite #7 do NÚCLEO, "state grande com lixo derruba acerto", em dois desenhos nos MESMOS dados: **A, mapa
por seção** (um Noul por seção, redução em código) e **B, documento inteiro num state**. Números dos relatórios
gerados pelo `run.py`: rodada cega do teste em [`resultados-rodada1.md`](resultados-rodada1.md); a rodada 3
(pós-revisão do Codex, dado v2b com as condições compostas reescritas, **não cega**) é o
[`resultados.md`](resultados.md) atual; 1ª passada do ajuste em [`resultados-ajuste-passada1.md`](resultados-ajuste-passada1.md).
Candidato a filtro sobre contratos, atas e propostas guardados no CRM.

**Nada é executado daqui**: `triagem.py` devolve uma saída por documento; o consumidor decide o que fazer com a lista.

## Problema
44 documentos sintéticos (11 por tipo: locação, prestação de serviço, ata de condomínio, proposta comercial; 316
seções de 74–115 palavras), montados por receita a partir de 94 textos de seção escritos à mão
([`dados/LEIA-ME.md`](dados/LEIA-ME.md)) — placar bom valida o MECANISMO, não a leitura de contratos reais. Condições
semânticas e numéricas; a maioria dos documentos é falsa para qualquer condição (4–10 verdadeiros em 44): medem-se
precisão/recall/F1 por condição e no total, não acurácia. Erros caros: documento verdadeiro **perdido** e cláusula
**negada ou revogada lida como presente** ("NÃO haverá multa"; "fica sem efeito a multa prevista na cláusula…" numa
seção final) — o erro da busca por palavra. Difíceis: negada, revogada em seção posterior, prova em DUAS seções,
termo só no título, seção parecida de outro assunto, documento sem a cláusula; indecidível só quando o texto deixa a
decisão em aberto ("mediante consulta prévia", comodato experimental, "poderá ensejar revisão").

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Condição numérica (`tipo: numerica`, expressão `` (`multa_alugueis` > 2) `` validada inteira): comparar com `campos`; campo nulo/ausente = falso; `tipo` em desacordo com a forma = condição inválida (humano, zero chamada) | **código** (`triagem.separar`, `avaliar_numerica`) | limite #2: o Jev não compara número; "dois aluguéis" não é "superior a dois"; zero chamada |
| Condição composta "A E B" (regra 6, duas seções): um Noul por cláusula por seção/documento, combinados em código — uma cláusula só nunca é verdadeiro | **código** (`triagem.separar`, `combinar`) + Jev (`establishes_part_<i>` / `holds_part_<i>`) | rodada 2 (código) e rodada 3 (TD-A03 e TD-T03 reescritas com o conector pelo rotulador, medidas na API) |
| A seção, por si, INSTITUI o que a condição pede? (A) | Jev, Noul `establishes` | leitura: paráfrase, negação com a mesma palavra, termo só no título, cláusula parecida |
| A seção REVOGA/cancela uma cláusula anterior sobre o assunto? (A, mesma requisição) | Jev, Noul `revokes` | a revogação mora noutra seção; o code precisa do sinal por seção |
| A seção deixa a decisão EM ABERTO? (A e B, mesma requisição) | Jev, Noul `deferred` | válvula do indecidível (regra 7 do LEIA-ME): falso + aberto → humano |
| Redução na ORDEM do texto: institui e nenhuma posterior revoga → verdadeiro; meio → indecidível; `secao_que_prova` = maior `establishes` | **código** (`triagem.reduzir`) | "alguma seção afirma" não basta (revogação posterior, duas seções) |
| O documento INTEIRO, como fica ao final, dispõe o que a condição pede? + qual seção prova (Choice sobre ids + `none`) (B) | Jev, Noul `holds` + Choice `proving_section` | a variante de comparação: 1 requisição por documento |
| Faixas, válvula, teto, validação da resposta, falha → `indecidivel` por documento | **código** (`triagem.*_seguro`) | política por risco; ausência de resposta nunca é `verdadeiro` |
| Baseline: radicais da condição por seção (≥ metade numa seção) | **código** (`triagem.baseline`) | o que um dev escreveria em meia hora |

## Desenho
State A `{"condition", "document_type", "section": {"title", "text"}}` (as outras seções NÃO vão); state B
`{"condition", "document_type", "sections": [{"id", "title", "text"}, …]}`. A condição (pt-BR) é DADO: vai no state;
a pergunta é a mesma para toda condição, em inglês, com as regras 1–9 do LEIA-ME nos `criteria` (silêncio, negação,
revogação, título, cláusula parecida, outro tipo de documento). Os `campos` não vão ao Jev. Tudo em
[`perguntas.py`](perguntas.py) (perguntas, faixas, variante padrão, critério, orçamento). Decisão em [`triagem.py`](triagem.py):
`establishes`/`holds` ≥ 0,8 → sim, ≤ 0,3 → não, meio → `indecidivel`; `revokes` ≥ 0,8 revoga, ≤ 0,4 não, meio →
`indecidivel` se havia cláusula instituída; `deferred` ≥ 0,7 com documento `falso` → `indecidivel`. Texto acima do
teto não vai ao Jev. Falha operacional (timeout, cache faltando, resposta fora do contrato, Choice contraditória,
seção vazia, campo com tipo errado) → `indecidivel` naquele documento — no mapa, UMA seção que falha derruba o
documento inteiro (não dá para garantir que nenhuma posterior revoga) — e a resposta inválida sai do cache
(`jev.invalidar`). [`testa_falhas.py`](testa_falhas.py) prova o código sem rede (185 conferências: 27 respostas
corrompidas, 12 exceções, documentos fora do esquema, numérica sem chamada, 9 cláusulas inválidas, 18 casos da
redução, política do B, teto, métricas, e os achados 1–3 da revisão: `tipo` validado, expressão inteira, composta
por cláusula).

## Baseline (código, sem Jev)
Radicais da condição (sem acento, fora das genéricas e dos nomes de tipo, cortados na 5ª letra) por seção; seção
com ≥ metade dos radicais bate; documento verdadeiro se alguma bate. Nunca `indecidivel`. No teste: F1 0,594, 9 das
58 verdadeiras perdidas, 58 FP (22 em condições de negada/revogada), os 4 indecidíveis marcados `verdadeiro`.

## Critério de continuar/descartar (fixado depois do ajuste e ANTES de abrir o teste, 2026-10-02)
Para o desenho padrão **A**, no teste (12 condições × 44 documentos), sobre os documentos decidíveis: (1) F1 das
decididas ≥ 0,90 e ≥ baseline + 0,20; (2) perdidas ≤ 5% das verdadeiras; (3) FP em condição de negada/revogada ≤ 1;
(4) decidíveis a humano ≤ 6%. Secundário, não decide: seção que prova certa ≥ 80%; indecidíveis do gabarito a humano
≥ 50%; falha operacional = 0; B medido ao lado, com n. Está no manifesto `congelamento.json`; o veredito é do `run.py`.

## Resultados (`jev-1.13.0`, 2026-10-02)
Ajuste = 6 condições (4 semânticas, 4 difíceis; 31 verdadeiros), afinado em duas passadas (faixas e dois `criteria`;
detalhes no cabeçalho de `perguntas.py`); teste = 12 condições (9 semânticas, 8 difíceis; 58 verdadeiros, 4
indecidíveis), congelado por hash (manifesto de 2026-10-02 00:37:25) e rodado UMA vez: 9 × (316 + 44) = **3.240
requisições** (orçamento 4.500), 0 falhas.

| | ajuste A · B · baseline | **teste A · B · baseline** |
|---|---|---|
| P · R · **F1** (decididos) | 1,000 · 1,000 · **1,000** / 1,000 / 0,660 | 1,000 · 1,000 · **1,000** / 1,000 / 0,594 |
| **perdidas** · **FP negada/revogada** · FP total | **0/31 · 0** · 0 / 0 · 0 · 0 / 0 · 23 · 32 | **0/58 · 0** · 0 / 0 · 0 · 0 / 9 · 22 · 58 |
| humano (decidíveis) · V a humano | 2 (0,8%) · 0 / 4 (1,5%) · 2 / — | 2 (0,4%) · 2 / 5 (1,0%) · 4 / — |
| seção que prova certa (V semânticos) | 22/22 / 22/22 / 22/22 | 45/45 / 45/45 / 35/45 |
| indecidíveis do gabarito → humano | — | 3/4 (1 virou `verdadeiro`) / 3/4 (idem) / 0/4 |
| A × B pareado (n decidíveis semânticos): A certo-B errado · B certo-A errado | 176: 2 · 0 | 392: 5 · 2 |
| requisições por documento · tokens · US$ por mil documentos | ≈7 · 10,8 mil · 0,46 / 1 · 2,8 mil · 0,12 | idem |
| p50 / p95 por requisição · por documento (serial medido / estimativa idealizada = máx das seções) | 256 / 316 ms · 1,9 s / 0,30 s // 278 / 326 ms | 256 / 312 ms · 1,9 s / 0,30 s // 282 / 333 ms |

A latência "por documento em paralelo" do mapa NÃO foi medida: as 5–8 seções de cada documento foram chamadas em
sequência (o paralelismo do `run.py` é entre documentos); 0,30 s é o máximo entre as seções, estimativa idealizada
sem espera nem coordenação (revisão do Codex, achado 4). O serial (1,9 s) é medido.

**Critério no teste: passou os quatro** — (1) 1,000 ≥ 0,90 e ≥ 0,794 ✓ · (2) 0/58 ✓ · (3) 0 ✓ · (4) 2/524 = 0,4% ✓;
secundários 45/45 ✓ · 3/4 ✓ · 0 falhas ✓. Por condição: as 12 com P = R = 1,000 nos dois desenhos; por família, F1
1,000 em todas (baseline: negada 0,545, revogada 0,593, título 0,276).

**O que o A × B mediu.** Com documentos de 5–8 seções (~2,8 mil tokens), o state inteiro NÃO derrubou o acerto: F1
igual, zero FP, zero perdida. O efeito apareceu na **hesitação**, e com uma causa que só vi depois do teste: os 7
documentos que o B mandou a humano (ajuste + teste) são L02, L05 e L11 — três das quatro locações **não
residenciais** do conjunto — e o rótulo `document_type` que o `triagem.py` põe no state diz "contrato de locação
**residencial**" para todo `tipo = locacao`. O B leu a contradição (`holds` 0,38–0,75 em cláusulas que o mapa leu
a 0,89–0,98 nas mesmas seções); em L05 soma-se a seção final que revoga OUTRA cláusula (a multa). O mapa, com a
seção sozinha no state, não se moveu. É lixo no state posto pelo MEU código, não pelo documento — e é exatamente o
limite que o exemplo mede: o desenho inteiro é o mais sensível a ele. O B custa 4× menos (US$ 0,12 × 0,46 por mil
documentos; 0,28 s × 1,9 s serial) e acertou a seção que prova 45/45 pela Choice. Com n = 392 e 5 × 2 discordâncias,
a diferença é de hesitação, não de erro; documentos maiores que o teto validado (8 seções) não foram medidos. O
rótulo errado fica como está (corrigi-lo exigiria chamada nova: rodada não cega com respostas novas).

### Rodada 2 (pós-revisão do Codex, não cega; manifesto de 2026-10-02 00:55:17; `resultados.md`)
Quatro achados, todos aceitos e aplicados; **zero chamada nova** — as 3.240 requisições do teste e as 1.440 do
ajuste vieram do cache. Faixas, textos das perguntas e critério intactos; o manifesto da rodada cega foi para
`congelamentos-anteriores/`.

| Achado | O que mudou | Efeito medido |
|---|---|---|
| 1 (grav. 2) `tipo` da condição era descartado: `numerica` sem crase iria ao Jev como semântica | `run.separar` passa o `tipo`; `triagem.separar` valida (`numerica` exige a expressão; `semantica` não pode ter crase; ausente/desconhecido = inválido) → `indecidivel` em todos os documentos, 0 chamada, erro registrado | nenhuma condição dos três conjuntos é afetada: números iguais; bateria (6 condições inválidas por `tipo`) |
| 2 (grav. 2) a regex aceitava o prefixo de expressão inválida (`< 12.5` virava `< 12`) | expressão validada INTEIRA: `(`campo` op inteiro)` entre parênteses, uma vez; sufixo decimal/científico, operador extra, sem parênteses = recusa | idem; bateria (11 expressões inválidas, 3 válidas) |
| 3 (grav. 2) regra 6 não era exigida: uma seção com `establishes` alto bastava (L01 sem a garantia continuaria `verdadeiro` por L01-s8) | gramática de condição composta `A E B` (conector maiúsculo, como no sql-semantico): um Noul por cláusula por seção (`establishes_part_<i>`) e por documento (`holds_part_<i>`), máquina de estados por cláusula com o mesmo `revokes`, `combinar` (E) em código; prova = a seção que completa (a mais tardia); baseline por cláusula | **as duas condições "duas seções" (TD-A03, TD-T03) não têm o conector**: continuam simples e os números não mudam. Exercitar o mecanismo exige o rotulador reescrevê-las com `E` e custaria chamada nova: 2 × (316 + 44) = 720 nominais, ~622 únicas (~1,1 M tokens, ~US$ 0,05) — não feito, por ordem |
| 4 (grav. 2) "latência paralela" era `max(ms)` de seções chamadas em sequência | rotulada "estimativa idealizada" no relatório e aqui; nada medido de novo | só rótulo |

Também: a família de TD-T09 ("documento sem a cláusula") passou de "fácil" para "sem a cláusula" na tabela por
família (8 difíceis, como no LEIA-ME; F1 baseline da família 0,533). Métricas do teste, rodada 1 → rodada 2: A F1
1,000 → 1,000, 0 → 0 perdidas, 0 → 0 FP, 2 → 2 a humano; B idem (5 → 5 a humano); baseline 0,594 → 0,594.

### Rodada 3 (pós-revisão, dado v2b, não cega; manifesto em `congelamento.json`; `resultados.md`)
O rotulador reescreveu as duas condições "duas seções" com o conector (dados versão `2026-10-02b`; só o texto
`condicao` mudou; gabaritos e `secao_que_prova` iguais): TD-A03 "Proposta comercial que concede desconto sobre o
preço **E** condiciona esse desconto exclusivamente ao pagamento à vista." e TD-T03 "Contrato de locação em que a
garantia é prestada por fiador **E** a responsabilidade do fiador se estende até a efetiva devolução das chaves,
inclusive na prorrogação.". Agora a gramática `A E B` é exercitada na API: **622 chamadas novas** (720 nominais:
2 × (316 seções + 44 documentos); o resto do cache), 1,71 M tokens, US$ 0,072 (as perguntas por cláusula pesam ~250 tokens a mais por requisição); 0 falhas, 0 429. Faixas, perguntas e critério intactos.

Por cláusula, nas duas condições (A: máximo de `establishes_part_<i>` por documento; B: `holds_part_<i>`):

| | TD-A03 (ajuste; 5 verdadeiros, 11 propostas + 33 outros) | TD-T03 (teste; 4 verdadeiros, 11 locações + 33 outros) |
|---|---|---|
| A: cláusula 0 / cláusula 1 nos verdadeiros | 0,96–0,97 (s3 ou s4) / 0,98 (s4) | 0,98 (s4, garantia) / 0,98 (s8, disposições finais) |
| A: falsos com UMA cláusula só (o caso do Codex) | P02, P05, P07, P10: desconto 0,95–0,96, "só à vista" 0,12–0,13 → `falso` | L05, L06, L09: fiador 0,98, extensão 0,05–0,06 → `falso` |
| A: verdadeiros · perdidas · FP · humano · prova certa | 5 · 0 · 0 · 0 · 5/5 (s4, a que completa) | 4 · 0 · 0 · 0 · 4/4 (s8, a que completa) |
| B: cláusulas nos verdadeiros / nos falsos de uma cláusula | 0,98 / 0,98 — 0,87–0,96 / 0,03–0,39 | 0,96–0,99 / 0,96–0,98 — 0,92–0,98 / 0,08–0,14 |
| B: verdadeiros · perdidas · FP · humano · prova certa | 5 · 0 · 0 · **1** (P05: "só à vista" 0,39) · 5/5 | 4 · 0 · 0 · 0 · 4/4 |
| baseline (radicais por cláusula): F1 · FP | 0,625 · 6 | 0,800 · 2 |

Contratos de serviço com desconto em outro sentido leram a cláusula 0 de TD-A03 a 0,30–0,33 (faixa do meio) com a
cláusula 1 a 0,03: `combinar` dá `falso` (uma cláusula negada decide), como a regra 6 manda. No B, as cláusulas foram
mais decisivas que a condição inteira: L11 (locação não residencial) saiu de `holds` 0,75 (humano, rodada 2) para
0,96/0,96 (`verdadeiro`), e L05 falso de 0,38 (humano) para 0,10.

| teste | rodada 2 | **rodada 3** |
|---|---|---|
| A: F1 · perdidas · FP neg/rev · humano (V) · prova | 1,000 · 0/58 · 0 · 2 (2) · 45/45 | 1,000 · 0/58 · 0 · 2 (2) · 45/45 |
| B: F1 · perdidas · FP · humano (V) · prova | 1,000 · 0/58 · 0 · 5 (4) · 45/45 | 1,000 · 0/58 · 0 · **3 (3)** · 45/45 |
| baseline: F1 · perdidas · FP | 0,594 · 9 · 58 | 0,590 · 9 · 59 |
| A × B (n = 392): A certo-B errado · B certo-A errado | 5 · 2 | 3 · 2 |
| ajuste: humano A / B · baseline F1 | 2 / 4 · 0,660 | 2 / 5 (P05) · 0,653 |
| requisições teste A / B · tokens por requisição A / B | 2.844 / 396 · 1.527 / 2.782 | 2.844 / 396 · 1.642 / 2.909 |

**Critério no teste (rodada 3): passou os quatro** — 1,000 ≥ 0,90 e ≥ 0,790 ✓ · 0/58 ✓ · 0 ✓ · 2/524 ✓; secundários
45/45 ✓ · 3/4 ✓ · 0 falhas ✓. O que mudou de verdade: o mecanismo da regra 6 passou de "provado só pela bateria" a
medido — 7 documentos com uma cláusula só (4 propostas, 3 locações) saem `falso` pela combinação em código, não
porque o Noul da condição inteira os leu baixo (ele já lia 0,11–0,18); a seção que prova passa a ser a que completa.

## O que deu certo
- Negada: "NÃO haverá multa", "NÃO estabelece exclusividade", "MANTER a taxa sem reajuste", "REJEITADA" → 0 FP nos
  dois desenhos (ajuste e teste); o baseline marcou 23 + 22.
- Revogada: `revokes` leu 0,96–0,98 nas cinco revogações reais (L05 multa, S03, L09 e S05 renovação, L02
  sublocação), ≤ 0,28 nas negações ("NÃO haverá multa") e 0,34–0,55 na retificação da OBRA quando a condição era
  outra (A05-s6); a redução derrubou as cinco sem perder nenhuma verdadeira.
- Duas seções (fiador + extensão até as chaves; desconto + "exclusivamente à vista"): a seção que completa a prova
  institui sozinha a 0,97–0,98 no mapa — não precisou de state com duas seções.
- Indecidíveis: `deferred` 0,72–0,89 nos três casos de "deixa em aberto" (consulta prévia, tolerância provisória,
  "poderá ensejar revisão") e ≤ 0,47 em tudo o mais do teste (0,41–0,47 em contas adiadas para a próxima assembleia).

## O que falhou no teste (NÃO corrigido)
| Caso | Documento | Saída | Causa |
|---|---|---|---|
| TD-T01 A09 | duas câmeras em comodato por noventa dias, decisão futura (gabarito indecidível) | `verdadeiro` nos dois (`establishes` 0,87; `holds` 0,85) | o Jev leu "aprovou a instalação" como instituído; a válvula `deferred` só age com documento `falso` |
| TD-T01 A05 | câmeras aprovadas; a seção final declara SEM EFEITO a OBRA (gabarito verdadeiro) | A: `indecidivel` (`revokes` 0,55 na retificação) | revogação de outro assunto no meio da faixa; B acertou (0,95) |
| TD-T12 A05 | contas "aprovadas com ressalvas" (gabarito verdadeiro) | A: `indecidivel` (0,77) | a 0,03 do limiar; B 0,88 |
| TD-T02/T03/T11 L05, L11 | verdadeiros em locações NÃO residenciais (L05 também revoga a multa na seção final) | B: `indecidivel` (0,54–0,75) | rótulo `document_type` = "locação residencial" posto pelo código contradiz o texto; o state inteiro sentiu, o mapa não (0,89–0,98) |
| TD-T03 L05 | fiador sem a extensão (gabarito falso) | B: `indecidivel` (0,38) | mesma causa; A 0,16 |

Na rodada 1, a família "documento sem a cláusula" (TD-T09) saiu como "fácil" na tabela por família (expressão do
`run.py`); corrigido na rodada 2 — só rótulo, o critério não usa essa família.

## Lições
1. **O state grande não derrubou o acerto neste porte, derrubou a certeza — e o lixo foi meu**: um rótulo de tipo
   errado no state ("residencial" num contrato não residencial) e uma revogação de outro assunto no fim levam
   `holds` a 0,4–0,75 onde o mapa lê 0,9+ na mesma seção. Quem pode pagar humano para 1% fica com o B por 1/4 do
   custo; quem precisa da leitura por seção (revogação, prova) ou não controla o que mais vai no state fica com o A.
2. **Revogação precisa de Noul próprio**: "institui" baixo numa seção que revoga não diz NADA sobre o documento; é o
   `revokes` + a ordem em código que derruba a cláusula. A redução é regra, não limiar.
3. **Negação e revogação de outro assunto ficam a 0,26–0,28 no `revokes`; a real a 0,97**: o `nao` subiu para 0,4
   (não 0,3) para deixar a variação máxima medida entre chamadas (0,15) fora do bolo — ainda assim A05 chegou a 0,55
   no teste. Faixa é compromisso, não garantia.
4. **Válvula só num lado**: `deferred` manda a humano o que o Jev leu como ausente, não o que leu como presente
   (A09). Um gate "`establishes` alto E `deferred` alto → humano" é a correção óbvia — e não teria pego o A09: para
   a condição de câmeras, `deferred` leu 0,36 no B e abaixo de 0,3 em toda seção no A ("aprovou a instalação" pesou
   mais que "em caráter experimental"). Não medido além disso.
5. **"Detalhe a definir" não é "decisão em aberto"**: "índice a ser definido" disparou `deferred` 0,72 na 1ª passada;
   a 2ª escreveu a regra do LEIA-ME no critério (ausência, não abertura) e exigiu o assunto da condição — o único
   ajuste de pergunta além da faixa.
6. **Custo do mapa é linear nas seções**: 7 requisições por documento, US$ 0,46 por mil (condição × documento);
   agrupar as perguntas de várias condições na mesma requisição por seção (uma chamada, N Nouls) cortaria o custo
   por condição — não medido.

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só, mesmo fornecedor de quem construiu; textos de uma
  mesma variante se repetem entre documentos (o cache deduplicou ~14% das requisições); o teste mede condições
  inéditas sobre os MESMOS 44 documentos do ajuste.
- `perguntas.TIPOS_DOCUMENTO` rotula todo `tipo = locacao` como "contrato de locação residencial"; quatro dos onze
  são não residenciais (L02, L05, L08, L11). O rótulo é dado do código, não do documento; ficou congelado como está
  e o efeito dele é a maior parte da diferença A × B (acima).
- Uma versão do modelo, uma rodada cega. Valores perto do limiar trocam de lado entre chamadas (p95 ~0,05, máx 0,15).
- Documentos de 5–8 seções (≤ 3 mil tokens): o teto em que o B empata não vale para documentos maiores.
- `secao_que_prova` no A é a seção de maior `establishes` mesmo no documento revogado (serve para auditoria, não
  como prova de verdade); numéricas não têm seção (o código não sabe onde o número está).
- A gramática da condição é a do rotulador: `tipo` + UMA expressão `(`campo` op inteiro)` na numérica; conector `E`
  maiúsculo na composta; fora dela, a condição é recusada (`indecidivel` para todos os documentos), não adivinhada.
  Composta medida em duas condições (uma por conjunto); a cláusula 2 chega sem sujeito ("condiciona esse desconto…")
  e o Noul a lê junto de `condition` — não medido com três ou mais cláusulas.
- `redecidir` da curva do relatório não re-decide o `prova`; compostas usam o mesmo `revokes` para todas as cláusulas.
- `*_seguro` pega qualquer exceção: defeito de programação também vira `indecidivel` "falha operacional" — a
  contagem à parte é o que o denuncia.
- O documento é dado de terceiro: texto que "argumenta pela própria classificação" move o Noul (limite #6); o
  filtro não é fronteira de segurança.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa se o manifesto congelamento.json não bate ou se passa do orçamento)
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação (marca "em afinação")
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 condições fáceis → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # grava o manifesto (código, documentos.json, condicoes_teste.json, critério)
set JEV_MODO=gravado                              # só o cache/ (respostas reais), sem chave
..\..\.venv\Scripts\python.exe testa_falhas.py   # bateria do código (sem chave, sem rede)
```
No Windows, use `PYTHONIOENCODING=utf-8`. A primeira execução com o teste grava `resultados-rodada1.md` e nunca o
reescreve. `cache/passada1/` guarda as respostas da 1ª passada (perguntas antigas; não são lidas).
Como filtro: `triagem.separar(condicao)` uma vez, depois `triagem.avaliar_mapa_seguro(jev, sep, doc)` (ou
`avaliar_inteiro_seguro`) por documento devolve `saida` (`verdadeiro` / `falso` / `indecidivel`), `por` (`codigo` /
`jev` / `longo` / `falha`), `motivo`, `prova` e os números; **não levanta**: falha da chamada ou resposta fora do
contrato → `indecidivel` com motivo `falha operacional: …`. `avaliar_mapa` / `avaliar_inteiro` são o baixo nível.
