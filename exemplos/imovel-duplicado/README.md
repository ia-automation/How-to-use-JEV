# Imóvel duplicado (pares de anúncios, pt-BR) — unir / revisar / manter_separados

O mesmo apartamento entra no catálogo por dois portais ou dois corretores, com título, área e preço diferentes.
Este exemplo julga UM par de anúncios por requisição e devolve a ação. Os números vêm dos relatórios gerados pelo
`run.py`: a rodada cega está preservada em [`resultados-rodada1.md`](resultados-rodada1.md) e a rodada 2
(pós-revisão do Codex, **não cega**) é o [`resultados.md`](resultados.md) atual. Candidato a **dedup de
captação/portais no CRM**: roda sobre pares candidatos antes de o imóvel entrar no catálogo.

**Nada é apagado daqui.** `unir` é uma PROPOSTA de união para o processo que chama (com a permissão dele);
`duplicado.py` não escreve em lugar nenhum.

## Problema
O erro tem dois lados, de custo diferente:
- **diferente unido**: dois imóveis diferentes saem `unir` — a união apaga um imóvel do catálogo. É o erro caro;
- **duplicata separada**: o mesmo imóvel sai `manter_separados` — a duplicata fica e ninguém revisa.

O que confunde (regras em [`dados/LEIA-ME.md`](dados/LEIA-ME.md)): **mesmo prédio não é mesmo imóvel** — a vizinha
tem a mesma planta, a mesma área e quase o mesmo preço, e só um detalhe FIXO a denuncia (vista, face, frente ×
fundos, lareira, pé-direito); preço reajustado e área total × privativa são a mesma unidade com número
diferente; mesmo prédio e mesma planta sem nenhum detalhe da unidade é indecidível (`null` → humano);
"mobiliado" × "entregue vazio" também.

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Mesmo bairro e cidade, mesmos quartos, mesmas vagas, área ±3%, preço ±5% | **código** (`duplicado.fatos`) | é conta e igualdade (limite #2); entra no state como fato pronto em `numeric_checks` |
| A área diverge, mas o texto de um anúncio declara a relação com rótulo nos dois números ("92 m² de área total, 68 m² privativos"). Metragem que bate sem rótulo de área da unidade ("salão comum de 68 m²") não concilia → `revisar` (rodada 2; na rodada 1 qualquer metragem citada conciliava) | **código** (`duplicado.leitura_area`: leitor de números brasileiros de `_comum/numeros_br.py` + a mesma tolerância) | o número está escrito; comparar é do código |
| Cidade, quartos ou vagas diferentes → `manter_separados` **sem chamada**. Bairro que difere no texto dentro da mesma cidade não separa sozinho: o par vai ao Jev e não pode sair `unir` (rodada 2; na rodada 1 separava sem chamada) | **código** (`duplicado.local`) | regra exata do LEIA-ME onde há prova; no teste, 7 dos 80 pares não custaram requisição na rodada 1 e 6 na rodada 2 |
| Citam o mesmo prédio ou a mesma rua? Citam prédios ou ruas diferentes? | Jev, Nouls `same_building_or_street` e `address_conflict` | texto livre; são duas perguntas porque "sem endereço" não é nem um nem outro |
| Um diz que tem sacada/varanda/dependência e o outro diz que não tem? | Jev, Noul `layout_contradiction` | a parte da planta que não é número |
| Detalhe permanente incompatível (vista, face, frente × fundos, lareira, pé-direito)? | Jev, Noul `fixed_contradiction` | o sinal decisivo do "mesmo prédio, outra unidade" |
| Estado ou mobília opostos (mobiliado × vazio, reformado × original)? | Jev, Noul `state_contradiction` | não prova unidade diferente nem a mesma → humano |
| Os dois citam o mesmo detalhe da unidade? | Jev, Noul `shared_distinctive_details` | o sinal forte que autoriza a união (sem ele: `revisar`) |
| Leitura inteira do par em 3 níveis | Jev, Score `same_listing` (receita [alinhamento-de-entidades](../../conhecimento/receitas/alinhamento-de-entidades.md)) | medido contra os Nouls; na política só pode TIRAR uma união |
| Precedência, faixas, dúvida → `revisar`; validar a resposta; falha operacional → `revisar` por par | **código** | política por risco; ausência de resposta nunca é `unir` nem `manter_separados` |
| Unir de fato, escolher qual anúncio fica | processo que chama, com humano | efeito não é do Jev |

## Desenho
State `{"a": {"title", "description"}, "b": {…}, "numeric_checks": {…}}` — área, preço, quartos e vagas **não**
vão como valor, só como fato calculado. Uma requisição com 7 perguntas (1 Score + 6 Nouls), em inglês, todas em
[`perguntas.py`](perguntas.py) com as faixas e o critério. Decisão em [`duplicado.py`](duplicado.py):

1. Código: cidade, quartos ou vagas diferentes → `manter_separados`, sem chamada. (Rodada 1: bairro diferente
   também; rodada 2: bairro que difere só no texto segue para os passos abaixo e para no 4.)
2. Algum veto (`address_conflict`, `layout_contradiction`, `fixed_contradiction`) ≥ 0,7 → `manter_separados`
   (endereço lido como igual E diferente → `revisar`).
3. Algum veto entre 0,2 e 0,7 → `revisar`.
4. Bairro que difere no texto → `revisar` (rodada 2); `state_contradiction` > 0,2 → `revisar`; área fora de
   ±3% sem a relação total × privativa rotulada no texto → `revisar`; `shared_distinctive_details` < 0,8 →
   `revisar`.
5. Sobrou: `unir` — se o Score `same_listing` ≥ 1,7; senão `revisar`.

Política assimétrica: dúvida nunca vira `unir`; o Score nunca cria união. O "só" de "só o estado difere" é do
código (estado alto E nenhum veto): uma condição por pergunta. Falha operacional (timeout, cache faltando,
resposta fora do contrato, anúncio inválido) sai `revisar` para aquele par por `duplicado.julgar_seguro`; par
acima de 4.000 caracteres não vai ao Jev. `testa_falhas.py` prova isso sem rede (19 falhas, grade de 23.328
combinações da política — 8.748 na rodada 1 —, fatos do código e 36 casos dos achados da revisão).

Duas regras da rodada 2 (revisão do Codex), as duas de código: **fato do código tem três valores** — bairro
`igual` / `distinto` (só cidades diferentes provam) / `indefinido`; área `dentro` / `conciliada` / `indefinida` /
`diverge` — e **indefinido nunca une**. O state que vai ao Jev não mudou: as mesmas seis chaves booleanas em
`numeric_checks`, `true` só com prova.

## Baseline (código, sem Jev)
O dedup por regra: mesmos bairro/cidade + quartos + vagas + área ±3% + preço ±5% ⇒ `unir`; senão
`manter_separados`. Não tem `revisar`. Segunda referência: "sempre revisa" (zero erro caro, 100% a humano).

## Critério de continuar/descartar (fixado ANTES de abrir o teste, 2026-10-01)
No teste (80 pares): (1) diferente unido = 0; (2) indecidível unido ≤ 1 de 8; (3) duplicata separada ≤ 5%
(≤ 2 de 40); (4) acerto da ação (3 classes) ≥ baseline + 0,15. Secundário, não decide: todo nulo → `revisar`;
revisou sem necessidade ≤ 15%; sinais numéricos do código = 100%. Está no manifesto `congelamento.json` e o
veredito é calculado pelo `run.py`.

## Resultados (`jev-1.13.0`, 2026-10-01; detalhes, curvas e caso a caso nos dois relatórios)
Duas rodadas, cada uma com o relatório gerado pelo script: 1 (cega) em `resultados-rodada1.md`, 2 (pós-revisão
do Codex, não cega) em `resultados.md`.

### Rodada 1 (cega, uma execução; [resultados-rodada1.md](resultados-rodada1.md))
Ajuste = 40 pares (33 difíceis; 20 duplicatas, 16 diferentes, 4 indecidíveis); teste = 80 (66 difíceis; 40, 32, 8),
com imóveis-base que não aparecem no ajuste. Manifesto gravado em 2026-10-01 13:39:34; teste rodado uma vez depois.

| | ajuste (n = 40) | teste (n = 80) |
|---|---|---|
| baseline: ação · **diferente unido** · indecidível unido · **duplicata separada** | 0,550 · 7/16 · 3/4 · 7/20 | 0,550 · **14/32** · 6/8 · **14/40** |
| **Jev (política)**: ação · **diferente unido** · indecidível unido · **duplicata separada** | 1,000 · 0/16 · 0/4 · 0/20 | **0,963 (77/80) · 0/32 · 0/8 · 0/40** |
| Jev: duplicata unida · nulo → `revisar` · revisou sem necessidade | 20/20 · 4/4 · 0/36 | 39/40 · 8/8 · 3/72 (4,2%) |
| só Nouls (política sem o Score): ação · indecidível unido | 1,000 · 0/4 | 0,975 (78/80) · 0/8 |
| só Score (arredondamento da receita): ação · indecidível unido | 0,950 · 2/4 | 0,938 · **5/8** |
| Nouls contra o gabarito (corte 0,5): `mesmo_endereco` em 3 valores · `mesma_planta` composta | 36/36 · 40/40 | 73/73 · 80/80 |
| sinais numéricos do código (`mesma_area`, `mesmo_preco`) | 40/40 · 40/40 | 80/80 · 80/80 |
| requisições · sem chamada (código) · p50 / p95 · tokens por requisição · US$ por mil pares | 36 · 4 · 286 / 332 ms · 1.794 · 0,068 | 73 · 7 · 273 / 404 ms · 1.785 · 0,068 |

**Critério no teste: passou os quatro** — (1) 0/32 ✓ · (2) 0/8 ✓ · (3) 0/40 ✓ · (4) 0,963 ≥ 0,700 ✓.
Secundários: 8/8 ✓ · 4,2% ✓ · 100% ✓.

Matriz do teste, Jev (gabarito → previsto): `unir` 39, 1 → revisar · `revisar` 8/8 · `manter_separados` 30,
2 → revisar. Os 3 erros de ação são `revisar` desnecessários; nenhum é caro.

Por família (teste, ação Jev × baseline): detalhe fixo contradiz 6/8 × 0/8 · mesmo bairro e números parecidos
5/5 × 0/5 · preço reajustado 8/8 × 0/8 · área útil × total 6/6 × 0/6 · sem detalhe distintivo 6/6 × 0/6 ·
mobiliado × vazio 2/2 × 0/2 · unidade diferente 8/8 × 7/8 · dois corretores (fácil) 9/10 × 10/10 · as demais
iguais (anúncio sem endereço, descrição copiada, mobiliado só num, mesma rua, texto reaproveitado, bairros
diferentes: todas certas nas duas).

Curva do teste (mesmas respostas; informativa): vetos com corte único 0,5 → 89% automático, 0 erro; política
congelada (0,2–0,7) → 86%, 0 erro; 0,1–0,9 → 80%; 0,05–0,95 → 66%, sempre 0 erro entre os automáticos. Sem o
Score, ou com mínimo 1,5 → 40/40 duplicatas unidas; 1,7 (congelado) → 39; 1,8 → 35; 1,9 → 31.

Custo total da construção: 148 requisições (orçamento 400) — 3 de rascunho, 36 + 36 nas duas passadas de
ajuste, 73 de teste; 266.046 tokens de entrada, US$ 0,011.

### Rodada 2 (pós-revisão do Codex, não cega; manifesto gravado em 2026-10-01 14:13:26; `resultados.md`)
Revisão adversarial do Codex sobre a rodada 1: quatro achados de gravidade 2, **todos no código, nenhum no Jev**,
todos aceitos e aplicados. O teste já estava aberto: esta rodada **não é cega**. Não mexe no texto das
perguntas, nas faixas, na política dos Nouls e do Score nem no critério (`perguntas.py` tem o mesmo hash). O
state dos pares que já iam ao Jev é idêntico, então as 109 respostas de ajuste e teste vieram do cache; houve
**1 chamada nova** (ID-T049, 1.778 tokens, US$ 0,00007; orçamento da rodada: 100), em `JEV_MODO=auto`. Total do
exemplo: 149 requisições, 267.824 tokens, US$ 0,011.

| Achado | O que mudou | Efeito medido |
|---|---|---|
| 1. Qualquer metragem citada conciliava a área: "apartamento de 92 m² com salão comum de 68 m²" casava com um apartamento de 68 m² | `duplicado.leitura_area`: só concilia quando o texto de UM anúncio rotula os dois números como área da unidade, com tipos diferentes (total × privativa/útil; "apartamento de N m²" vale para a própria área), sem conflito no texto (o mesmo número com dois rótulos, dois valores para o mesmo tipo) e sem o outro anúncio desmentir. Metragem que bate sem essa prova = área `indefinida` → `revisar` | **nenhum par muda**: as 9 conciliações dos conjuntos (3 no ajuste, 6 no teste) têm os dois rótulos; 0 indefinidas. Provado só pela bateria |
| 2. Regex de área: `1.068 m²` lido como 1,068 e `1.068,50 m²` como 68,5 | a regex saiu; leitura por `_comum/numeros_br.ler_numeros` (número completo, unidade `m2`); decimal à inglesa ("68.5 m²") é ambíguo e não serve de prova | **nenhum par muda** (nenhum anúncio dos conjuntos tem metragem com ponto de milhar ou decimal). Provado só pela bateria |
| 3. `Vila Mariana` × `V. Mariana` saía `manter_separados` sem chamada | comparação sem acento, caixa e pontuação, com `V.`/`Vl.`/`Jd.`/`Sta.`/`Sto.` por extenso antes de um nome; `duplicado.local` em três valores: cidades diferentes = `distinto` (o código separa sem chamada, como antes); bairro que ainda difere na mesma cidade = `indefinido` → vai ao Jev, um veto do Jev pode separar, e **nunca sai `unir`** | **1 par muda de caminho: ID-T049** (abaixo). Ajuste 0 de 40, rascunho 0 de 5. Nenhum bairro abreviado nos dados: a normalização está provada só pela bateria |
| 4. `area_m2: null` num par abortava o relatório inteiro (o baseline refazia a conta com `None`) | `duplicado.baseline_seguro`: anúncio inválido conta como `revisar` também no baseline; o `run.py` usa os fatos que `julgar_seguro` já calculou (nenhum, se a entrada é inválida), tira o par da conferência dos sinais do código e o conta à parte | **0 entradas inválidas** nos três conjuntos; nenhum número muda. Provado só pela bateria |

**Números do teste, rodada 1 → rodada 2** (ajuste idêntico: 1,000, 36 requisições, 4 sem chamada):

| | rodada 1 (cega) | rodada 2 (não cega) |
|---|---|---|
| Jev: ação (3 classes) | 0,963 (77/80) | 0,963 (77/80) |
| Jev: diferente unido · indecidível unido · duplicata separada | 0/32 · 0/8 · 0/40 | 0/32 · 0/8 · 0/40 |
| Jev: duplicata unida · nulo → `revisar` · revisou sem necessidade | 39/40 · 8/8 · 3/72 | 39/40 · 8/8 · 3/72 |
| baseline · só Nouls · só Score (ação) | 0,550 · 0,975 · 0,938 | 0,550 · 0,975 · 0,938 |
| requisições · sem chamada (código) | 73 · 7 | **74 · 6** |
| `mesmo_endereco` em 3 valores (pares que foram ao Jev) | 73/73 | **74/74** |
| sinais numéricos do código (`mesma_area`, `mesmo_preco`) | 80/80 · 80/80 | 80/80 · 80/80 |
| área fora de ±3% entre os que foram ao Jev · conciliada · indefinida | 13 · 6 · (não existia) | **14** · 6 · 0 |
| tokens por requisição · US$ por mil pares | 1.785 · 0,068 | 1.785 · **0,069** |
| falhas operacionais · entradas inválidas | 0 · não contadas | 0 · 0 |

**Critério no teste (rodada 2): passou os quatro, com os mesmos números** — (1) 0/32 ✓ · (2) 0/8 ✓ · (3) 0/40 ✓ ·
(4) 0,963 ≥ 0,700 ✓. Secundários: 8/8 ✓ · 4,2% ✓ · 100% ✓. Curvas e matrizes iguais às da rodada 1.

**O par que mudou de caminho — ID-T049** (Tatuapé × Pinheiros, os dois em São Paulo; gabarito
`manter_separados`). Rodada 1: `manter_separados` pelo código, sem chamada. Rodada 2: foi ao Jev —
`address_conflict` 0,97, `same_building_or_street` 0,02, Score 0,00 — e saiu `manter_separados` por "prédios ou
ruas diferentes". Mesma ação por outro caminho, ao preço de uma requisição. É um caso só: mostra o veto de
endereço segurando um par de bairros diferentes; **não mede o caso que motivou o achado** (o mesmo prédio com
dois nomes de bairro, ou `V. Mariana`), que não existe nos conjuntos.

**Varredura da família dos achados** (texto comparado por igualdade decidindo sozinho; número lido de texto):
cidade continua separando sem chamada por decisão da triagem (cidade diferente é a prova) — grafia divergente
da MESMA cidade ainda cai aí (ver Limites); quartos e vagas são inteiros validados, igualdade exata; preço e área
declarados são campos numéricos validados; a única leitura de número em texto do exemplo é a das metragens,
agora pelo leitor comum. No `run.py`, os quatro pontos que refaziam conta com o anúncio cru (baseline da
variante, da tabela por família e do caso a caso; os sinais do código) passaram por `baseline_seguro` ou pelos
fatos já calculados.

**Bateria** ([`testa_falhas.py`](testa_falhas.py), sem chave nem rede; dublê no lugar do Jev porque o que se
testa é código): **A** 19 falhas operacionais → `revisar` · **B** 23.328 combinações de `compor` (três níveis por
Noul × 4 Scores × 4 leituras de área × 2 de bairro): `unir` só com tudo limpo, área `dentro` ou `conciliada` e
bairro `igual` · **C** 8 checagens dos fatos · **D** 36 casos dos achados — 20 de área (8 que não conciliam por
falta de rótulo ou conflito, 4 de número brasileiro, 8 formas rotuladas que continuam conciliando), 6 bairros
iguais depois da normalização, 3 indefinidos (o dublê responde "unir" e sai `revisar`; com veto de endereço sai
`manter_separados`), 3 de cidade/quartos sem chamada, 1 do state (seis chaves booleanas) e 3 de entrada inválida
(um relatório inteiro com 3 pares inválidos em 5 fecha e conta os três à parte). Contra o código da rodada 1, a
parte D acusa 33 dos 36: 19 por comportamento (o "salão comum", `1.068,50 m²`, `V. Mariana`, o relatório
abortando com `TypeError`…) e 14 que param na leitura que ainda não existia.

O manifesto da rodada cega (13:39:34; `duplicado.py` `fcb8543a85911dd9…`, `run.py` `5205dde8dc6037c8…`) foi para
`congelamentos-anteriores/`. `perguntas.py` e `dados/teste.json` têm o mesmo hash nas duas rodadas.

## O que deu certo (rodada 1; o que a rodada 2 muda está dito em cada item)
- **Dividir o trabalho.** Os números ficaram no código (100% contra o gabarito, inclusive a área total ×
  privativa conciliada por regex: 6/6 no teste) e o Jev leu só o texto: endereço 73/73, planta 80/80. (Rodada 2:
  a regex saiu; as mesmas 6/6, agora pela relação rotulada; endereço 74/74.)
- **O sinal decisivo é o que a regra não vê.** O baseline uniu 14 de 32 pares diferentes — todos os "detalhe fixo
  contradiz" e "mesmo bairro, ruas diferentes" — e separou 14 duplicatas por preço ou área. O Jev: zero dos dois.
- **Indecidível tem dono.** O Noul `shared_distinctive_details` separou os 6 "sem detalhe distintivo" (≤ 0,26)
  das 40 duplicatas (≥ 0,91); `state_contradiction` pegou os 2 "mobiliado × vazio" (0,97).

## O que falhou
- **ID-T008 e ID-T058 (detalhe fixo → `revisar`, não `manter_separados`)**: "varanda voltada para a rua" × "vista
  para o parque" deu 0,56; "vista para a quadra arborizada" × "vista para o estacionamento" deu 0,66. O `true` de
  `fixed_contradiction` lista PARES de opostos (parque × sem vista, piscina × rua); as duas combinações não estão
  na lista e caíram na dúvida (limite #1, literal). A faixa segurou o lado seguro: foram a humano.
- **ID-T006 (duplicata fácil → `revisar`)**: os Nouls disseram unir; o Score deu 1,59 e o mínimo é 1,7.
- **O Score não acrescentou nada aos Nouls.** Na política ele mudou 1 decisão no teste, para pior (ID-T006), e
  não evitou nenhuma união. Sozinho, acertou duplicata × diferente (40/40 e 32/32), mas **uniu 5 dos 8
  indecidíveis**: o nível do meio não segura "mesmo prédio, mesma planta, textos genéricos" (1,50–1,75). O mínimo
  de 1,7, tirado de 4 indecidíveis do ajuste (1,24–1,57), não separa no teste: indecidíveis foram até 1,75 e uma
  duplicata desceu a 1,59.

## Lições
1. **Score de 3 níveis responde "mesmo ou diferente"; "não dá para saber" precisa de pergunta própria.** A
   receita usa o nível do meio como fila do curador; aqui ele falhou em 5 de 8. O que achou os indecidíveis foi
   um Noul absoluto de existência ("os dois citam o mesmo detalhe da unidade?").
2. **Lista de pares de opostos é teto.** Escrever a condição geral ("dizem que a unidade dá para coisas
   diferentes") em vez de enumerar pares; a enumeração acerta o que lista e hesita no vizinho.
3. **Ajuste fácil não calibra limiar** (de novo): o ajuste deu 40/40 com vãos largos; qualquer corte dentro do
   vão era igual. Os dois que afinei: `sim` dos vetos em 0,7 rendeu 1 par (ID-T021, 0,74); o mínimo do Score
   custou 1.
4. **Mudança sem caso que a sustente se reverte.** Escrever "um cita só o prédio, o outro só a rua" nas perguntas
   de endereço não mudou decisão no ajuste e derrubou `address_conflict` de 0,95 para 0,81 num par de ruas
   diferentes. Voltou a redação anterior.
5. **O que o código decide não vai ao Jev**: 9% dos pares do teste saíram sem requisição. (Rodada 2: 6 de 80.)
6. **O código também precisa de "não sei"** (rodada 2). Os quatro achados da revisão eram do código, não do Jev:
   igualdade de texto e "qualquer número que bate" decidiam com certeza o que não estava provado, e número lido
   por regex própria errava o ponto de milhar. Atalho de código só decide com prova; sem ela o fato é
   `indefinido`, e indefinido vai ao Jev ou a humano — nunca a `unir`.

## Limites
- Dados sintéticos de um rotulador só (Fable), gerados por famílias a partir de 45 imóveis-base e 3 moldes de
  texto genérico; a mesma base aparece em mais de um par. **Um placar assim valida o mecanismo, não o desempenho
  em portal real.** Uma rodada, um modelo.
- Os zeros são de amostra pequena: 0/32 diferentes unidos não exclui uma taxa real de alguns por cento.
- "Bairro diferente ⇒ outro imóvel" e "quartos ou vagas diferentes ⇒ outra planta" são regras do LEIA-ME. Em
  portal real o mesmo prédio aparece com dois nomes de bairro e corretor erra o número de vagas: ali esses
  pares deveriam ir a `revisar`, não a `manter_separados`. (Rodada 2, 2026-10-01: a metade do bairro foi
  aplicada — bairro que difere na mesma cidade vai ao Jev e a `revisar`; quartos e vagas continuam separando por
  regra.)
- **As correções da rodada 2 estão provadas por bateria com dublê, não por tráfego**: nenhum par dos conjuntos
  tem metragem sem rótulo que coincide, número com ponto de milhar, bairro abreviado nem anúncio inválido. O
  único par que mudou de caminho (ID-T049) acertou; é um caso.
- Cidade com grafia divergente ("São Paulo" × "São Paulo/SP" × "S. Paulo") ainda sai `manter_separados` sem
  chamada: a normalização cobre acento, caixa, pontuação e cinco abreviações, não apelido nem UF colada.
- Rótulo de área é lista fechada (total; privativa/privativo(s); útil/úteis; "apartamento/apto/unidade/imóvel de
  N m²"), colado ao número. "Área construída", "área interna" ou rótulo separado do número por vírgula não são
  reconhecidos: o par vai a `revisar` (lado seguro, custa uma revisão).
- Par com bairro `indefinido` vai ao Jev com `same_neighborhood_and_city: false` no state, enquanto a instrução
  do Score diz "same neighborhood (checked by code)". Combinação medida em 1 par; o Score não cria união e esse
  par não pode sair `unir`.
- Não medido: um anúncio que cita só o prédio contra outro que cita só a rua (o LEIA-ME diz "nada a comparar";
  as perguntas não escrevem esse caso); estado oposto sem ser mobília (reformado × original) como única
  diferença; anúncios longos; texto adversarial (limite #6).
- O exemplo julga pares já formados. Formar os pares candidatos (bloqueio por bairro, faixa de área) é do
  código e fica fora daqui; o custo cresce com o número de pares, não de anúncios.

## Rodar
```
python run.py rascunho      # encanamento (5 pares)
python run.py ajuste        # afinação
python run.py congelar      # grava congelamento.json
python run.py               # ajuste + teste (exige o manifesto batendo)
python testa_falhas.py      # bateria do código, sem chave nem rede
```
`JEV_MODO=gravado` reproduz tudo do `cache/` sem chave (a rodada 2 inteira, inclusive a resposta nova do
ID-T049). O `cache/` guarda também as 36 respostas da 2ª passada de ajuste (redação revertida), que a versão
congelada não usa. No Windows, use `PYTHONIOENCODING=utf-8`. A primeira execução com o teste gravou
`resultados-rodada1.md`; o `run.py` nunca o reescreve.
