# SQL semântico (filtro em linguagem natural sobre uma tabela, pt-BR) — verdadeiro / falso / indecidivel

"Clientes que mencionaram que vão mudar de cidade", "observações de locação em que o cliente reclamou do nosso
atendimento", "clientes que descartaram financiamento": condições que o `WHERE` não expressa e que hoje são leitura
manual ou um LLM por linha. Este exemplo separa cada condição em **parte estruturada** (entre crases → filtro sobre
`campos`, resolvido em Python) e **parte semântica** (uma requisição ao Jev por linha que passou no filtro) e devolve,
por linha, `verdadeiro` / `falso` / `indecidivel` (humano lê). Os números vêm dos relatórios gerados pelo `run.py`:
a rodada cega do teste está preservada em [`resultados-rodada1.md`](resultados-rodada1.md) e a rodada 2 (pós-revisão
do Codex, **não cega**, zero chamada nova) é o [`resultados.md`](resultados.md) atual; a 1ª passada do ajuste está em
[`resultados-ajuste-passada1.md`](resultados-ajuste-passada1.md). Candidato a
filtro "em linguagem natural" sobre tabelas do CRM (observações, notas de visita, histórico).

**Nada é executado daqui**: `sql.py` devolve uma lista de linhas com a saída; o consumidor decide o que fazer com ela.

## Problema
Tabela sintética de 187 observações de atendimento (1–3 frases, pt-BR informal, 17 fatos de autoria em três estados:
afirmado, negado, pista fraca — [`dados/LEIA-ME.md`](dados/LEIA-ME.md)). A maioria das linhas é falsa para qualquer
condição (4 a 19 verdadeiras em 187): acurácia não mede nada; medem-se precisão/recall/F1 por condição e no total.
O erro caro tem dois lados:
- **perdida**: linha verdadeira que sai `falso` — o filtro não achou quem o gestor procurava;
- **negação lida como afirmação**: "não tem pet", "precisa de reforma", "largou o home office" marcadas
  `verdadeiro` — é o erro que o `LIKE` comete, e o exemplo existe para mostrar a diferença.

O que confunde: a mesma palavra com sentido invertido; condição NEGATIVA ("descartaram financiamento": silêncio é
falso nos dois sentidos); pista fraca que não decide ("perguntou se tem elevador" → indecidível); composta E/OU; parte
numérica repetida em palavras na própria condição ("têm orçamento de até R$ 500.000").

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Separar a condição: `` `orcamento` <= 500000 ``, `` `canal` = whatsapp ``, `` `data` em 2026-09 `` saem da frase | **código** (`sql.separar`) | gramática fixa do rotulador (campo, operador, valor) |
| Filtro de campos: nulo ou ausente falha; linha que falha é `falso` sem chamada | **código** (`sql.passa_filtro`) | comparação e igualdade (limite #2); regra 4 do LEIA-ME; no ajuste 380 das 1.683 (condição × linha) não custaram requisição |
| A observação AFIRMA o fato que a condição pede? | Jev, Noul `stated` | leitura: sinônimo, gíria, paráfrase, negação com a mesma palavra |
| A observação afirma OU só sugere o fato? | Jev, Noul `hinted` (mesma requisição) | válvula da pista fraca: baixo em `stated`, alto aqui → humano |
| Condição composta "A OU B" / "A E B": um Noul por cláusula (`condition_parts[i]`) | Jev, Nouls `stated_part_<i>` (mesma requisição) | uma condição por pergunta; a combinação é a regra 5 do LEIA-ME, em código |
| Faixas, combinação E/OU, dúvida → `indecidivel`; validar a resposta; falha operacional → `indecidivel` por linha | **código** (`sql.decidir`, `sql.avaliar_seguro`) | política por risco; ausência de resposta nunca é `verdadeiro` nem `falso` |
| Baseline: `LIKE` com os radicais da condição | **código** (`sql.baseline`) | o que um dev escreveria em meia hora |

## Desenho
State `{"condition": "<parte semântica, pt-BR>", "note": "<texto da linha>"}`, mais `checked_by_code` (a parte de
campo, como fato já conferido) quando há filtro e `condition_parts` nas compostas. A pergunta é a mesma para toda
condição (a condição é DADO, vai no state); perguntas em inglês, em [`perguntas.py`](perguntas.py) com as faixas, a
variante oficial e o critério. Os `campos` NÃO vão ao Jev: ou o código já os consumiu, ou enviesariam (a condição é
sobre o que a observação DIZ; `etapa = perdido` não pode virar "desistiu"). Decisão em [`sql.py`](sql.py):

1. Toda crase da condição é validada como cláusula (campo conhecido, operador do campo, valor do domínio) ANTES de
   qualquer remoção; cláusula inválida = condição inválida → `indecidivel` em todas as linhas, com o erro (rodada 2).
   Filtro de campos em Python; condição só de campos (ou cujo resíduo não tem letra) → resolvida sem chamada.
2. Uma requisição por linha que passou: `stated`, `hinted` e, se composta, um Noul por cláusula.
3. Simples: `stated` ≥ 0,8 → `verdadeiro`; ≤ 0,3 → `falso`, salvo `hinted` ≥ 0,7 (sugere sem afirmar →
   `indecidivel`); entre 0,3 e 0,8 → `indecidivel`.
4. Composta: cada cláusula nas mesmas três faixas; a válvula do `hinted` entra ANTES de combinar (rodada 2) — só
   quando nenhuma cláusula está afirmada, porque `hinted` é da condição inteira e, com um lado afirmado, a pista vem
   dele; **E** = todas afirmadas → `verdadeiro`, alguma negada/ausente → `falso`, senão `indecidivel`; **OU** = alguma
   afirmada → `verdadeiro`, todas negadas → `falso`, senão `indecidivel`.
5. Texto acima de 2.000 caracteres não vai ao Jev (`indecidivel`; a maior linha tem 135). Falha operacional
   (timeout, cache faltando, resposta fora do contrato, campo com tipo errado) → `indecidivel` naquela linha, o lote
   não aborta, e a resposta inválida sai do cache (`jev.invalidar`) para a repetição refazê-la. Baseline e previsão
   de orçamento têm a mesma proteção (rodada 2).

As quatro variantes (pergunta inteira × cláusulas; com × sem `hinted`) e a grade de faixas são calculadas das mesmas
respostas no relatório, sem chamada nova. [`testa_falhas.py`](testa_falhas.py) prova o código sem rede: 32 falhas
operacionais, condição só de campos sem chamada, filtro com campo nulo/ausente/tipo errado, 14 separações, 97
conferências da política (faixas, válvula, E/OU sobre todos os estados, teto, métricas) e 28 dos achados da revisão
(condição inválida → `indecidivel`, resíduo de pontuação, válvula por cláusula, baseline/previsão protegidos).

## Baseline (código, sem Jev)
Filtro de campos igual + `LIKE` de qualquer radical da parte semântica (palavras sem acento, fora de uma lista de
genéricas e dos nomes/valores de campo, cortadas na 5ª letra: "financiamento" → `finan`). Não tem `indecidivel`:
LIKE não sabe que não sabe. No ajuste: F1 0,441, 34 das 77 verdadeiras perdidas ("cachorro" não contém `anima`) e 27
negações marcadas verdadeiras ("precisa de reforma" contém `refor`).

## Critério de continuar/descartar (fixado depois do ajuste e ANTES de abrir o teste, 2026-10-01)
No teste (18 condições × 187 linhas; 131 verdadeiras, 27 indecidíveis, 3 condições de negação), sobre as linhas
decidíveis: (1) F1 das decididas ≥ 0,85 e ≥ baseline + 0,15; (2) perdidas ≤ 5% das verdadeiras; (3) FP em condição
de negação ≤ 2; (4) decidíveis mandadas a humano ≤ 8% (o ajuste deu 4,6%; o teste tem o dobro de compostas e de
condições com resíduo numérico, onde a hesitação mora). Secundário, não decide: indecidíveis do gabarito revisados
≥ 50%; falha operacional = 0. 1 falhando = o LIKE basta ou o Jev não lê a condição; 2 ou 3 = o filtro perde ou
inverte o que deveria achar; 4 = custa humano demais. O critério está no manifesto `congelamento.json` e o veredito é
calculado pelo `run.py`.

## Resultados (`jev-1.13.0`, 2026-10-01; detalhes, curvas e caso a caso nos relatórios)
Ajuste = 9 condições (8 difíceis; 77 verdadeiras, 14 indecidíveis), afinado em duas passadas; teste = 18 condições
(12 difíceis), congelado por hash e rodado UMA vez.

### Ajuste (duas passadas, 4.348 requisições; política final sobre as respostas da 2ª)
| | 1ª passada (faixa 0,2–0,8, inteira) | 2ª passada, política final (0,3–0,8, cláusulas, `hinted` 0,7) |
|---|---|---|
| Jev: P · R · **F1** (decididas) · F1 com V a humano = perdidas | 0,954 · 1,000 · **0,976** · 0,873 | 0,970 · 0,985 · **0,977** · 0,895 |
| Jev: **perdidas** · **FP em negação** · humano · indecidíveis → humano | **0/77 · 0** · 118 (7,1%) · 8/14 | **1/77 · 0** · 77 (4,6%) · 9/14 |
| baseline LIKE: F1 · perdidas · FP em negação | 0,441 · 34/77 · 27 | idem |
| p50 / p95 · tokens por requisição · US$ por mil linhas avaliadas | 249 / 305 ms · 920 · 0,030 | 249 / 308 ms · 1.083 · 0,035 |

O que a 2ª passada mudou e o que não mudou: a parte de campo passou a ir no state como fato conferido
(`checked_by_code`) e o `false` ganhou "circunstância não é afirmação". O piso das falsas nas condições com resíduo
numérico **não** desceu (SQ-A03 continua com 38 linhas entre 0,21 e 0,41); o que resolveu foi subir o `nao` para 0,3
(humano 120 → 59) — limiar, não pergunta. `hinted` a 0,8 nunca disparou; a 0,7 revisa 4 indecidíveis a mais ao custo
de 18 falsas a mais. A variante por cláusulas ganhou 3 linhas na 2ª passada e perdeu 2 na 1ª (uma única composta no
ajuste): ficou pelo desenho (uma condição por pergunta), não pela medição.

### Teste (rodada cega; [resultados-rodada1.md](resultados-rodada1.md))
Manifesto gravado em 2026-10-01 23:39:57 (`perguntas.py` `ca1f9374f7123aa5…`, `sql.py` `1be64866ae7f02d0…`, `run.py`
`103cdfb7c4d5b97d…`, `dados/linhas.json` `b11253f810da103e…`, `dados/condicoes_teste.json` `2310fb5836605d52…`),
teste aberto e rodado UMA vez depois disso: 18 condições × 187 linhas = 3.366 pares, 701 resolvidos pelo filtro sem
chamada, **2.665 requisições** (orçamento 3.500), 0 falhas operacionais.

| | ajuste (9 cond., política final) | **teste (18 cond.)** |
|---|---|---|
| Jev: P · R · **F1** (decididas) · F1 com V a humano = perdidas | 0,970 · 0,985 · **0,977** · 0,895 | 0,980 · 0,980 · **0,980** · 0,843 |
| Jev: **perdidas** · **FP em negação** · humano (decidíveis) · indecidíveis → humano | **1/77 · 0** · 77 (4,6%) · 9/14 | **2/131 · 1** · 178 (5,3%) · 14/27 (1 virou `verdadeiro`) |
| baseline LIKE: F1 · perdidas · FP em negação · indecidíveis marcados `verdadeiro` | 0,441 · 34/77 · 27 · 1/14 | 0,399 · 49/131 · 17 · 7/27 |
| variantes (F1 · humano · perdidas): inteira · inteira+pista · cláusulas | 0,968 · 62 · 1 · — · 0,977 · 59 · 1 | 0,975 · 156 · 2 · 0,980 · 194 · 1 · 0,975 · 149 · 3 |
| p50 / p95 · tokens por requisição · US$ por mil pares · por mil requisições | 249 / 308 ms · 1.083 · 0,035 · 0,045 | 255 / 317 ms · 1.131 · 0,038 · 0,048 |

**Critério no teste: passou os quatro** — (1) 0,980 ≥ 0,85 e ≥ 0,549 ✓ · (2) 2/131 = 1,5% ≤ 5% ✓ · (3) 1 ≤ 2 ✓ ·
(4) 178/3.339 = 5,3% ≤ 8% ✓. Secundários: 14/27 ✓ · 0 falhas ✓. Folga: o critério 3 admite 2 e saiu 1; o 4 admite
8% e saiu 5,3% (seria ✗ com o teto original de 5%, que o ajuste fez subir antes do congelamento).

Por condição: 14 das 18 com P = R = 1,000 nas decididas; as outras: SQ-T06 (decisor terceiro) 0,909 com 1 FP,
SQ-T14 (cômodo extra: home office OU filhos) 0,917 com 2 perdidas, SQ-T15 (elogio ao atendimento, negação) 0,909
com 1 FP. Por família (F1 Jev × baseline): fácil 1,000 × 0,370 · inferência fraca 0,971 × 0,500 · composta
0,969 × 0,365 · negação 0,970 × 0,478. As três condições de negação: 0 perdidas, 1 FP (abaixo). Humano por
condição: a mais cara é SQ-T03 (investidor com `orcamento` >= 400000: 38 das 78 linhas que passaram no filtro
foram a humano — o resíduo numérico "com orçamento de R$ 400.000 ou mais" de novo), depois T10 (22) e T12 (21,
a condição com 7 indecidíveis de propósito: 3 revisados, 4 saíram `falso`).

Curva do teste (mesmas respostas, outra faixa; informativa): 0,5 único → 98,5% decidido, 3 perdidas, 3 FP em
negação; 0,3–0,7 → 95,3%, 2 e 1; política congelada (0,3–0,8 + `hinted`) → 94,7%, 2 e 1; 0,2–0,8 → 91,1%, 0 e 1;
0,1–0,9 → 81%, 0 e 0. As duas perdidas estão a 0,21–0,22: um `nao` em 0,2 as teria mandado a humano ao custo de
120 revisões a mais.

Custo total da construção: **7.013 requisições** (871 + 1.303 em cada uma das duas passadas de rascunho + ajuste,
2.665 no teste), 7,16 milhões de tokens de entrada, US$ 0,30.

### Rodada 2 (pós-revisão do Codex, não cega; manifesto gravado em 2026-10-02 00:05:23; `resultados.md`)
Revisão adversarial do Codex sobre a rodada 1: cinco achados, todos aceitos e aplicados. O teste já estava aberto:
esta rodada **não é cega**. Não mexe no texto das perguntas, no state, nas faixas nem no critério; **zero chamada
nova** — as 1.303 + 2.665 requisições vieram do cache em `JEV_MODO=gravado`. O manifesto da rodada cega
(2026-10-01 23:39:57) foi para `congelamentos-anteriores/`.

| Achado | O que mudou | Efeito medido |
|---|---|---|
| 1 (grav. 2) parêntese com crase mal formado (`` `orcamento` < 500000 ``) era apagado antes de validar: filtro e semântica vazios → `verdadeiro` para toda linha | `sql.validar_clausulas` valida cada crase ANTES de remover (campo, operador do campo, valor do domínio); `sql.separar_seguro` transforma condição inválida em `indecidivel` para todas as linhas, com o erro, sem chamada | nenhuma condição dos três conjuntos é inválida: nenhum número muda; provado pela bateria (10 condições inválidas) |
| 2 (grav. 2) resíduo só de pontuação ("." de "(`canal` = whatsapp).") virava semântica e chamava o Jev | resíduo sem letra = semântica vazia | idem: nenhum número muda |
| 3 (grav. 2) o retorno antecipado das compostas ignorava a válvula do `hinted` (SQ-T14/OB-062: cláusulas 0,04/0,04, `hinted` 0,78 → `falso`, gabarito indecidível) | válvula por cláusula ANTES de combinar, só com nenhuma cláusula afirmada (`hinted` é da condição inteira); negação no E preservada (`combinar` não muda) | **12 linhas mudam `falso` → `indecidivel`**: 11 no teste (OB-062 de T14 — o caso do Codex — mais 10 falsas de T09, T14 e T17), 1 no ajuste (A06/OB-086) |
| 4 (grav. 2) `baseline` e a previsão de orçamento chamavam o filtro sem proteção: campo com tipo errado abortava o relatório | `sql.baseline_seguro` (falha por linha, `indecidivel` marcado) e previsão que ignora a linha inválida; relatório conta "falhas (baseline)" e marca "não é medição" | 0 falhas nos três conjuntos; provado pela bateria |
| 5 (grav. 3) "F1 estrito (humano = erro)" só punia verdadeiras a humano | coluna renomeada para "F1 com V a humano = perdidas"; colunas novas "V a humano" e "F a humano" | só rótulo; teste: 32 V e 156 F a humano |

**Números do teste, Jev, rodada 1 → rodada 2** (baseline não muda: F1 0,399, 49/131 perdidas, 17 FP em negação):

| | rodada 1 (cega) | rodada 2 (não cega) |
|---|---|---|
| P · R · F1 (decididas) | 0,980 · 0,980 · 0,980 | 0,980 · 0,980 · 0,980 |
| perdidas · FP em negação | 2/131 · 1 | 2/131 · 1 |
| humano (decidíveis) · V a humano · F a humano | 178 (5,3%) · 32 · 146 | **188 (5,6%)** · 32 · **156** |
| indecidíveis → humano | 14/27 | **15/27** |
| ajuste: humano · indecidíveis → humano | 77 (4,6%) · 9/14 | 78 (4,7%) · 9/14 |

**Critério no teste (rodada 2)**: (1) 0,980 ✓ · (2) 2/131 ✓ · (3) 1 ✓ · (4) 188/3.339 = 5,6% ≤ 8% ✓ · secundários
15/27 ✓ e 0 falhas ✓. O preço da válvula nas compostas: 1 indecidível a mais revisado (OB-062) por 10 falsas a mais
a humano — a mesma proporção da válvula nas condições simples (4 por 18 no ajuste).

## O que deu certo (ajuste)
- Negação 2/2 condições com F1 1,000 e zero FP: "precisa de reforma", "anúncio dizia reformado mas não é",
  "financiamento pelo nome do pai" não passaram; o LIKE marcou 27.
- 7 das 9 condições com P = R = 1,000 nas decididas; a composta OU (SQ-A06) 0,923.
- Zero perdida na 1ª passada e uma na 2ª (OB-107 "fechou com outra imobiliária", 0,34 → 0,16 entre passadas: a
  pergunta mudou e a linha está na zona em que chamadas idênticas variam).
- Custo: US$ 0,035 por mil (condição × linha), 249 ms por requisição com 8 em paralelo; 1.303 linhas em ~45 s.

## O que falhou no teste (NÃO corrigido)
| Caso | Observação | Saída | Causa |
|---|---|---|---|
| SQ-T06 OB-039 | "o financiamento seria pelo nome do pai… Decisão final é dele mesmo assim" (gabarito falso: decide sozinho) | `verdadeiro` (`stated` 0,86) | negação lida como afirmação: a dependência financeira do pai venceu o "decisão é dele". Único FP fora de negação |
| SQ-T15 OB-107 | "Fechou com outra imobiliária na semana passada. Agradeceu o atendimento." (gabarito falso: agradecer não é elogiar) | `verdadeiro` (0,82) | o único **FP em condição de negação**; a 0,02 do limiar |
| SQ-T14 OB-094 | "Filho autista precisa de ambiente tranquilo…" (gabarito verdadeiro: filhos pequenos) | `falso` (cláusulas 0,06 e 0,21; inteira 0,40) | perdida: a cláusula "têm filhos pequenos/bebê a caminho" não leu "filho autista" como filho pequeno; a pergunta inteira teria mandado a humano |
| SQ-T14 OB-135 | "Precisa ficar na rota da escola das crianças" (gabarito verdadeiro) | `falso` (0,06 e 0,21; inteira 0,22) | perdida: "crianças" ≠ "filhos pequenos" para o Jev; o rotulador contou |
| SQ-T05 OB-172 | "perguntou se… a vizinhança é tranquila à noite" (gabarito indecidível) | `verdadeiro` (0,93) | pergunta lida como preocupação afirmada — o único indecidível que virou `verdadeiro` |
| SQ-T14 OB-049 · OB-064 · OB-123 · OB-168 | 4 verdadeiras de T14 a humano (cláusulas 0,42 / 0,76 / 0,74 / 0,71) | `indecidivel` | "home office" e "filhos" lidos a 0,7–0,76, abaixo do `sim` de 0,8: a composta por cláusulas é mais exigente |

Doze dos 27 indecidíveis do gabarito saíram `falso` (`stated` 0,04–0,30): pista fraca que o Jev leu como silêncio
("perguntou se aceita negociação. Não disse se achou caro" 0,10; "um quarto sobrando, não disse pra quê" 0,15). Para
o consumidor isso é uma linha a menos na lista, não um erro de filtro; para quem queria "mandar a humano", é a
metade que não foi.

## O que falhou ou ficou frágil (ajuste)
1. **Resíduo numérico na frase semântica.** "…e têm orçamento de até R$ 500.000 (`orcamento` <= 500000)": o filtro
   resolve a parte entre crases, mas a repetição em palavras fica na frase e o Jev hesita (falsas a 0,21–0,41 em vez
   de ≤ 0,05). No teste, SQ-T03 repetiu o sintoma: 38 das 78 linhas a humano. Dizer na instrução e no state que a parte foi conferida não moveu o piso. Apagar a repetição em código
   seria apagar texto semântico às cegas (uma cláusula "E com filhos" sumiria igual); ficou o limiar.
2. **Palavra da condição no texto com outro sentido**: "desistiu de se mudar" (0,66 em "mudar de cidade"),
   "Cliente descartou na hora" (0,72 em "descartaram financiamento" — a 0,7 seria FP de negação; o `sim` em 0,8
   existe por isso), "vai comparar com outra" (0,80 → `verdadeiro` em "avaliando outra imobiliária", FP).
3. **"Urgência para fechar" é vaga**: 8 falsas de SQ-A06 entre 0,39 e 0,68 (bebê nasce em janeiro, procuração pra
   fechar, visitou 3 unidades numa tarde) e 6 verdadeiras entre 0,61 e 0,77 — a faixa do meio é o que segura.

## Lições
1. **Parte numérica dita em palavras é parte numérica pedida ao Jev.** O filtro de código só protege o que sai da
   frase; o que fica nela volta como hesitação, e nenhuma instrução "já foi conferido" a tirou. O jeito certo é a
   condição não repetir: gramática de entrada (campo entre crases, sem paráfrase) — regra para quem escreve, não
   para o modelo.
2. **Dois erros caros, dois limiares.** O `nao` sobe para cortar hesitação de falsas (custa recall só em quem está
   abaixo de 0,3 — nenhuma verdadeira do ajuste); o `sim` fica alto porque a falsa de negação a 0,72 é o erro que
   o exemplo existe para evitar.
3. **Válvula que nunca dispara é peso**: `hinted` a 0,8 não mudou uma linha em 2.606 requisições; a 0,7 compra 4
   revisões úteis por 18 inúteis. Ficou ligada porque a pista fraca é exatamente o que o LEIA-ME manda a humano.
4. **Variante medida numa condição só não é medição**: cláusulas × inteira trocou de sinal entre passadas (+3/−2).
5. **A mesma linha a 0,34 e 0,16 em duas chamadas com pergunta diferente**: perto do limiar, mudar a pergunta é
   jogar o dado de novo (NÚCLEO §6).
6. **O LIKE erra dos dois lados e não avisa**: no teste, 49 das 131 verdadeiras perdidas e 17 negações marcadas,
   zero revisão; F1 0,399 contra 0,980.
7. **Cláusula é mais exigente que frase** (teste): a composta por cláusulas pede cada lado ≥ 0,8 e mandou 4
   verdadeiras de T14 a humano e perdeu 2 que a frase inteira teria segurado (0,40 → humano). No ajuste foi o
   contrário. Com duas compostas semânticas em 27 condições, a escolha continua sendo de desenho.
8. **O teto de humano fixado pelo ajuste foi o que decidiu o critério 4**: 5,3% no teste (5,6% na rodada 2) contra
   4,6% no ajuste; o teto original (5%) reprovaria. Humano cresce com condições compostas e com resíduo numérico — e o teste tinha
   o dobro delas, como previsto ao subir o teto.

9. **Apagar antes de validar inverte a falha** (rodada 2): uma cláusula estruturada mal escrita (`<`) sumia da
   condição e o que sobrava — nada — era "condição satisfeita" para toda linha. Entrada inválida tem de falhar
   fechada (`indecidivel`), e a validação vem antes de qualquer remoção.
10. **Válvula que existe num caminho tem de existir no outro**: a pista valia para a pergunta inteira e não para
    as cláusulas; o Codex achou o caso (OB-062) que o teste tinha e eu não vi. Um `hinted` por cláusula seria o
    desenho certo, mas custaria chamada nova: ficou a pista da condição inteira, gated por "nenhuma cláusula
    afirmada".

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só, mesmo fornecedor de quem construiu; o gabarito vem de
  fatos de autoria, não de anotação humana sobre notas reais; o teste usa condições novas sobre a **mesma** tabela.
- Uma versão do modelo, uma rodada cega. Valores perto do limiar trocam de lado entre chamadas (p95 ~0,05, máx 0,15).
- Uma requisição por (condição × linha): 187 linhas custam ~45 s e US$ 0,007 por condição; agrupar várias linhas
  num state (variante do briefing) não foi medido.
- A gramática da condição é a do rotulador (campo entre crases, conector E/OU em maiúsculas); condição com crase
  fora dessa gramática, ou que mistura E e OU, é recusada (`separar` levanta; `separar_seguro` manda todas as
  linhas a humano com o erro), não adivinhada. Parêntese sem fechar não é erro de gramática: a cláusula vale e o
  "(" sobra na frase.
- A válvula da pista nas compostas usa o `hinted` da condição inteira: "um lado afirmado e o outro fraco →
  indecidível" (regra 5) não é detectável sem um `hinted` por cláusula (não medido).
- `avaliar_seguro` pega qualquer exceção: defeito de programação também vira `indecidivel` "falha operacional" — a
  contagem à parte é o que o denuncia.
- A observação é dado de cliente: texto que "argumenta pela própria classificação" move o Noul (limite #6); o
  filtro não é fronteira de segurança.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa se o manifesto congelamento.json não bate ou se passa do orçamento)
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação (marca "em afinação")
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 condições fáceis → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # grava o manifesto (código, linhas.json, condicoes_teste.json, critério)
set JEV_MODO=gravado                              # só o cache/ (respostas reais), sem chave
..\..\.venv\Scripts\python.exe testa_falhas.py   # bateria do código (sem chave, sem rede)
```
No Windows, use `PYTHONIOENCODING=utf-8`. A primeira execução com o teste grava `resultados-rodada1.md` e nunca o
reescreve. `cache/passada1/` guarda as respostas da 1ª passada do ajuste (perguntas antigas; não são lidas).
Como filtro: `sql.separar(condicao)` uma vez, depois `sql.avaliar_seguro(jev, sep, linha)` por linha devolve
`saida` (`verdadeiro` / `falso` / `indecidivel`), `por` (`filtro` / `jev` / `longo` / `falha`), `motivo` e os
números; **não levanta**: falha da chamada ou resposta fora do contrato → `indecidivel` com motivo
`falha operacional: …`. `sql.avaliar` é o baixo nível, que levanta a exceção.
