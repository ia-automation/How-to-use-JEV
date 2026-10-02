# Motivo de perda (conversa de WhatsApp, pt-BR) — grupo › folha de uma taxonomia, `só grupo` ou `sem_informacao`

Lead perdido vira "sem interesse" no CRM; o motivo real (preço, documentação, visita furada, concorrente) está na
conversa e nunca chega ao relatório. Este exemplo lê a conversa inteira e devolve **um grupo e, quando a conversa
permite, uma folha** de uma taxonomia de 2 níveis (8 grupos, 30 folhas), com `folha = null` quando só o grupo é
decidível e `sem_informacao` quando a conversa não diz nada. Compara três desenhos com o Jev e um baseline de
código nas mesmas conversas. Os números vêm de [`resultados.md`](resultados.md), gerado pelo `run.py` — hoje a
**rodada 2 (pós-revisão do Codex, não cega)**, reproduzida do cache sem chamada nova; a rodada cega do teste está
preservada em [`resultados-rodada1.md`](resultados-rodada1.md). As duas têm os mesmos números no ponto de operação
(seção "Pós-revisão do Codex" abaixo). Candidato a **preenchimento automático
do motivo de perda no CRM**, com fila de revisão humana.

**A saída é sugestão para o relatório, não fechamento do lead.** `motivo.py` não muda status de nada; `revisar`
é a conversa que o código não fecha sozinho. Receita-irmã:
[classificacao-hierarquica](../../conhecimento/receitas/classificacao-hierarquica.md) (um Choice por nó; aqui a
árvore tem 2 níveis e não há beam — com 8 grupos cabe tudo numa requisição, ver variante c).

## Problema
Conversas sintéticas de venda e locação que terminaram sem negócio, 4–12 turnos, pt-BR informal
([`dados/LEIA-ME.md`](dados/LEIA-ME.md), taxonomia em [`dados/taxonomia.json`](dados/taxonomia.json)). Gabarito por
conversa: `grupo` (sempre), `folha` (ou `null`) e `aceitaveis` (folhas de qualquer grupo que o gestor também
aceitaria). Difíceis (60% do teste): dois motivos, motivo dito com educação, motivo real diferente do declarado,
sumiço depois do preço, fechou em outro lugar sem dizer por quê, motivo do corretor, só o grupo é decidível.

Erros, do mais caro ao mais barato:
- **motivo inventado** — gabarito `sem_informacao` e saiu outro grupo, sem revisão: o relatório inventa uma causa;
- **grupo errado automatizado** — o relatório de perda mente de categoria (preço no lugar de atendimento);
- **folha errada** com grupo certo; depois **absteve** (havia folha, saiu só o grupo: nem acerto nem erro).

Regra 8 do briefing, levada ao código: nenhuma leitura da Choice fecha o lead com motivo **do corretor**
(`atendimento`) nem com **fechou em outro lugar** (`concorrencia`) sem um Noul correspondente em sim.

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Validar conversa e taxonomia; teto de 6.000 caracteres; papéis `customer`/`agent`; última fala do cliente e quantas mensagens do corretor ficaram sem resposta | **código** | forma exata; recência e contagem são do código (lição 30) e entram no state como fato |
| EM QUE GRUPO está o motivo (8, inclusive `sem_informacao` com a política de "não inventar" escrita no critério) | Jev, Choice `group` | espaço fechado; a válvula é um grupo como os outros |
| QUAL folha dentro do grupo, ou `only_group` | Jev, Choice `leaf` por grupo (+ `only_group`, menos em `sem_informacao`) | a resposta do grupo decide as opções — ou, na variante c, uma Choice por grupo com premissa explícita, tudo numa requisição |
| Qual folha entre as 30 (variante b) | Jev, Choice única | compara o funil com a Choice plana; grupo = soma das probabilidades das folhas, em código |
| O cliente DIZ um motivo? · culpa o atendimento? · JÁ fechou em outro lugar? | Jev, três Nouls de guarda (mesma requisição) | segunda leitura do lado caro; o Noul é absoluto, a Choice é relativa |
| Limiares, `only_group`/folha fraca → só grupo, grupo fraco → revisar, guardas (tiram folha e mandam revisar; nunca promovem) | **código** (`motivo.decidir`) | política por risco: muda editando número |
| Validar toda resposta (IDs, tipo, opções, números reais em [0, 1]); falha ou conversa inválida → `sem_informacao` + `revisar` com `origem: "falha"` daquela conversa; resposta rejeitada sai do cache; taxonomia inválida para o lote antes de começar | **código** | ausência de resposta é erro, nunca um motivo nem um `sem_informacao` julgado; uma conversa torta não derruba o lote |
| Gravar no CRM, fechar o lead, falar com o cliente | processo que chama | efeito não é do Jev |

## Desenho
State: `{"conversation": [{"from", "text"}], "last_customer_message", "agent_messages_after_last_customer_message"}`.
A conversa vai inteira (é curta); os dois campos extras são calculados em código. Perguntas em inglês; nome e
descrição de grupos e folhas em português, como estão na taxonomia (são dado). As regras de precedência do
LEIA-ME (confessado vence declarado; o que o cliente ordena; evento que encerra vence queixa lateral; causa vence
consequência; educação com pista; silêncio sem reação não é motivo) vão escritas UMA vez (`_REGRAS`) em todas as
Choices. Tudo em [`perguntas.py`](perguntas.py); decisão em [`motivo.py`](motivo.py). Quatro formatos de requisição:

| Requisição | Perguntas | Tokens (teste) |
|---|---|---|
| `grupo` | Choice `group` (8 grupos; critério = descrição + nomes das folhas) + 3 Nouls | 1.541 |
| `folhas` | Choice `leaf` das folhas do grupo vencedor + `only_group` | 1.031 |
| `unica` | Choice `leaf` sobre as 30 folhas ("grupo › folha: descrição") + 3 Nouls | 2.584 |
| `tudo` | Choice `group` + 8 Choices `leaf.<grupo>` (premissa "assume the reason is in group X") + 3 Nouls | 6.067 |

| | Variante | Requisições | Como decide |
|---|---|---|---|
| a | duas etapas | `grupo` → `folhas` | grupo = vencedor (p < 0,5 → revisar); folha = vencedora (p < 0,5 ou `only_group` → só grupo); guardas |
| b | Choice única | `unica` | grupo = maior soma de probabilidades; folha = vencedora se p ≥ 0,5 e do grupo vencedor; guardas |
| c | uma requisição (**principal**) | `tudo` | igual a a, lendo a Choice `leaf.<grupo vencedor>` da mesma requisição (as outras 7 foram especulativas) |

Guardas (código, só tiram): grupo `atendimento` com `blames_agency` ≤ 0,5 ou `concorrencia` com `closed_elsewhere`
≤ 0,5 → só grupo + revisar (o empate exato é revisão, não sim — era `<` na rodada 1; nenhum caso mudou); grupo com
motivo e `reason_stated` < 0,4 → revisar. Noul alto nunca promove um grupo.

Por que c é a principal (decidido no ajuste, antes do teste; regra em `perguntas.py`): menos erros caros (a 2, b 2,
c 2 em 34) → abstém nos `folha: null` como o LEIA-ME pede (a 2/2, b 0/2, c 2/2) → acerto folgado (a 0,882, b
0,912, c 0,882) → menos requisições (c 1, a 2). Registro honesto: com "folgado antes de abstenção" a escolha seria
b; não a escolhi porque a Choice única não tem como dizer "só o grupo" (num `null` a folha errada saiu com 0,84,
acima de muitas certas) e o teste tem 7 `null` em 68.

## Baseline (código, sem Jev)
Palavras-chave por folha derivadas AUTOMATICAMENTE de nome + descrição de cada folha da taxonomia (minúsculas, sem
acento, sem palavras vazias, radical de 5 letras, peso 1/nº de folhas que têm o radical), contadas só nas mensagens
do cliente; sem nenhum radical em comum → `sem_informacao` por contagem de silêncio (≥ 2 mensagens do corretor sem
resposta: `sumiu_apos_valor` se há "R$" nelas, senão `sumiu_sem_resposta`; menos → `adiou_sem_motivo`).

## Critério de continuar/descartar (fixado ANTES de abrir o teste, 2026-10-01 15:51, manifesto [`congelamento.json`](congelamento.json))
Textos das perguntas: escritos uma vez a partir do LEIA-ME e **não mexidos** depois de medir. Só um limiar mudou no
ajuste (`sem_motivo` 0,5 → 0,4: a partida ficava a 0,02 de um acerto); os outros ficaram na partida porque nenhum
ponto da grade separava erro de acerto (detalhe ao lado de cada número em `perguntas.py`). Limites absolutos nos
erros caros + piso de acerto; o baseline entra só como "tem de ser melhor" (margem sobre baseline é critério frágil).

| Critério (principal, teste) | Limite | Medido | Passa |
|---|---|---|---|
| 1 motivo inventado | ≤ 1/8 | **0/8** | ✓ |
| 2 grupo errado automatizado (inclui inventados) | ≤ 0,09 (6/68) | 4/68 (0,059) | ✓ |
| 3 acerto folgado (revisão e falha = erro) | ≥ 0,70 | 0,853 | ✓ |
| 4 grupo certo (revisão e falha = erro) | ≥ 0,80 | 0,868 | ✓ |
| 5 revisão (inclui falha) | ≤ 20% | 5/68 (7,4%) | ✓ |
| 6 contra o baseline | > | 0,853 × 0,279 | ✓ |

**O critério passou (6 de 6)** na rodada cega e, com os mesmos números, na rodada 2. Folga menor no critério 2: 4 de
no máximo 6 — dois casos. A escolha da principal `c` em vez de `b` foi feita no ajuste, antes de abrir o teste: a
prova disso são só os carimbos locais (manifesto cego às 15:51:59, primeira chamada do teste às 15:52:05) e a
declaração do construtor — eles são compatíveis com a ordem declarada, não a demonstram.

## Resultados [testado, 2026-10-01, `jev-1.13.0`, rodada cega única]
Teste: 68 conversas (41 difíceis, 7 `folha: null`, 8 `sem_informacao`). Ajuste: 34 (18 difíceis, 2 `null`, 3
`sem_informacao`). Zero falha operacional. Revisão e falha contam como erro nas taxas de acerto.

| Variante (teste) | estrito | folgado | grupo certo | motivo inventado | grupo errado auto. | só-grupo certo | sem_info certo | folha errada | revisar | req | tokens | US$ por mil | p50 / p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| código: palavra-chave | 0,250 | 0,279 | 0,397 | 7/8 | 41/68 | 0/7 | 1/8 | 8/68 | 0 | 0 | — | — | — |
| a · duas etapas | 0,824 | 0,868 | 0,882 | 0/8 | 3/68 | 5/7 | 7/8 | 1/68 | 5/68 | 2,00 | 2.572 | 0,108 | 561 / 676 |
| b · Choice única | 0,824 | 0,868 | **0,926** | 0/8 | **1/68** | 0/7 | 8/8 | 3/68 | 4/68 | 1,00 | 2.584 | 0,109 | 270 / 323 |
| **c · uma requisição** | 0,809 | 0,853 | 0,868 | 0/8 | 4/68 | 5/7 | 7/8 | 1/68 | 5/68 | 1,00 | 6.067 | 0,255 | 286 / 338 |
| c sem as guardas (informativa) | 0,838 | 0,882 | 0,897 | 0/8 | 6/68 | 6/7 | 7/8 | 1/68 | 1/68 | 1,00 | 6.067 | 0,255 | 286 / 338 |

No ajuste (n = 34): baseline 0,500; a 0,882; b 0,912; c 0,882 (folgado); erros caros 2 em cada variante com Jev.

Quem aponta o grupo certo, sem limiar: Choice `group` 62/68 (`grupo`) e 61/68 (`tudo`); **soma das folhas da
Choice única 66/68**. Quem aponta a folha nos 61 casos com folha: `folhas` 53 (a principal) / 55 (aceitável);
`leaf.<grupo>` em `tudo` 52 / 54; **Choice única 58 / 59**. Nos 7 `null`, `only_group` saiu em 6 (em `folhas` e em
`tudo`); a Choice única deu folha nos 7 (2 delas aceitáveis, 3 erradas, 2 revisadas por outro motivo).

As guardas na principal (teste): `closed_elsewhere` disparou 2 vezes e **tirou 2 grupos errados** (T007, T028:
`concorrencia` no lugar de `demora_resposta`); `blames_agency` disparou 2 vezes e **tirou 2 acertos** (T024
`atendimento` só grupo, T055 `visita_falhou` por falta de horário — ninguém teve culpa); `reason_stated` não
disparou. Saldo: grupo errado automatizado 6 → 4, acerto folgado 0,882 → 0,853, revisão 1 → 5.

Sinais (teste, requisição `grupo`): p(grupo vencedor) certo mínimo 0,42, p10 0,80, mediana 0,98; errado 0,64–0,99
(mediana 0,71) — o limiar de grupo não separa; de 0,5 a 0,7 tira 3 erros caros e revisa 11. `reason_stated` onde há
motivo mínimo 0,52, nos `sem_informacao` máximo 0,24. `blames_agency` nos 11 casos de `atendimento` mínimo 0,13,
mediana 0,65 (o Noul lê a lista de condutas ao pé da letra); fora deles máximo 0,75. `closed_elsewhere` nos 7 de
`concorrencia` mínimo 0,62; fora deles máximo 0,97 (T048: fechou em outra imobiliária POR CAUSA da taxa — folha de
preço, concorrência aceitável). A mesma Choice `group` em duas requisições trocou de vencedor em 1/68 (T017: 0,54 ×
0,55); o mesmo Noul em requisições diferentes variou em média 0,005, máximo 0,09.

Custo desta medição: 428 requisições (20 rascunho, 136 ajuste, 272 teste), 1.200.218 tokens de entrada, US$ 0,050.
Retentativas internas do SDK, se houve, não são contadas. Latência medida com 8 conversas em paralelo.

## Pós-revisão do Codex (2026-10-01) — rodada 2, não cega
A revisão adversarial achou três defeitos de código (gravidade 2, todos aceitos na triagem). Aplicados depois de o
teste ter sido visto: **nenhuma pergunta, limiar ou política foi afinada olhando o teste**; só a lista abaixo. O
critério não mudou. Manifesto cego guardado em `congelamentos-anteriores/`; o atual é o da rodada 2.

| # | O que era | O que mudou |
|---|---|---|
| 1 | Conversa vazia, nula ou com turno inválido relançava a exceção em `julgar_seguro` e o `ex.map` do `run.py` abortava o lote inteiro | Conversa inválida vira `sem_informacao` + `revisar` + `origem: "falha"` (`invalida: true`) daquela conversa, contada à parte, sem chamada; o lote segue. Taxonomia inválida continua levantando erro e o `run.py` a valida uma vez antes do lote (parada com mensagem, não decisão). Bateria: 17 conversas inválidas (sem `de`, texto numérico, turno não-dicionário, conversa string…) em `julgar`, `julgar_seguro`, nas 5 linhas do relatório (baseline inclusive) e num lote de 18 pelo `rodar`; um turno só continua válido (o LEIA-ME descreve o dado, não exige do consumidor) |
| 2 | O cliente grava a resposta antes da validação; resposta com JSON válido mas fora do contrato ficava no cache e toda rodada seguinte a consumiria de novo | `julgar_seguro` chama `jev.invalidar` SÓ para o pedido rejeitado (as respostas válidas ficam); falha de chamada ou de entrada não invalida nada; a quarentena falhar não tira a escalada. Vale nos três desenhos. Bateria: 25 quebras de contrato nos 4 formatos provam que o pedido tirado é exatamente o rejeitado; 8 falhas de chamada não tiram nada; dublê com cache somente leitura ainda escala |
| 3 | Guardas com `< 0,50`: Noul exatamente 0,50 (sim e não igualmente prováveis) liberava `atendimento`/`concorrencia`, e a bateria exigia isso | `≤`: o empate vai a revisão nas duas guardas, nos três desenhos; expectativa da bateria corrigida (0,50 → revisão; 0,51 → fecha). Medido no cache: **zero** Noul em 0,50 no ajuste e no teste (o mais próximo com o grupo da guarda: 0,54, ajuste, Choice única) — nenhum caso mudou |

Rodada 1 (cega) × rodada 2 (pós-revisão), principal `c`, teste (n = 68), 0 chamadas novas (272 requisições, todas do cache):

| | estrito | folgado | grupo certo | motivo inventado | grupo errado auto. | só-grupo certo | sem_info certo | revisar | critério |
|---|---|---|---|---|---|---|---|---|---|
| rodada 1 | 0,809 | 0,853 | 0,868 | 0/8 | 4/68 | 5/7 | 7/8 | 5/68 | 6/6 ✓ |
| rodada 2 | 0,809 | 0,853 | 0,868 | 0/8 | 4/68 | 5/7 | 7/8 | 5/68 | 6/6 ✓ |

As variantes a e b, o ajuste e as guardas disparadas (T024, T055, T007, T028) também ficaram idênticos. **O que piorou:**
nada no ponto de operação; na curva informativa de `guarda` (um limiar por vez), o ponto 0,90 agora apanha um Noul
exatamente em 0,90 por conjunto (ajuste 30/34 → 29/34 automatizadas, folgado 0,824 → 0,794; teste 56/68 → 55/68,
0,765 → 0,750) — é o `≤` na grade, não uma mudança de resposta. O que a rodada 2 compra é código: lote que não aborta,
cache que não prende resposta inválida, empate que não fecha lead. Nada disso é medição nova do modelo.

## Veredito
Passou, e vale com ressalvas. **O funil hierárquico perde na raiz**: a Choice do grupo vê só a descrição do grupo e
os NOMES das folhas, e errou grupo onde a palavra decisiva mora na descrição de uma folha ("alaga" está em
`entorno_seguranca`; "FGTS" em `condicao_pagamento`) — a Choice única, que vê as 30 descrições, acertou o grupo em
66/68 contra 61–62/68. O que a hierarquia comprou foi a abstenção: `only_group` acertou 5/7 (6/7 sem guardas) onde a
Choice plana deu folha em 7/7. A variante b teria passado o mesmo critério com 1 erro caro, mas falhando o
`null` que o LEIA-ME pede. **As guardas pagaram pela metade**: a de "fechou em outro lugar" tirou 2 erros caros; a
de "culpa do atendimento" tirou 2 acertos, porque o grupo `atendimento` da taxonomia contém situações sem culpa
(nenhum horário compatível) e insatisfação sem detalhe, e o Noul foi escrito como lista de condutas.

## O que deu certo
1. **`sem_informacao` como grupo com a política escrita no critério**: 0 motivo inventado em 8 (7/8 certos na
   principal, 8/8 na Choice única); o baseline inventou em 7/8.
2. **`only_group` na Choice de folhas**: 6/7 abstenções certas e só 1 abstenção indevida em 61 casos com folha.
3. **A guarda de concorrência** (regra 8): os dois casos de "fui para outro lugar PORQUE vocês demoraram" saíram
   `concorrencia` na Choice e foram parados pelo Noul (0,13 e 0,27) — foram para revisão, não para o relatório.
4. **Famílias difíceis**: dois motivos 4/4, motivo dito com educação 3/3, motivo real diferente do declarado 3/3,
   sumiço sem pista 2/2, fechou em outro lugar 5/5, decisor com motivo 1/1 (principal, folgado).
5. Zero falha operacional e zero resposta fora do contrato em 428 requisições; a bateria sem rede prova o caminho
   da falha (`sem_informacao` + `revisar` + `origem: "falha"`, contada à parte).

## O que falhou no teste (principal `c`; NÃO corrigido)
| Caso | Saiu | Causa |
|---|---|---|
| T017 "o vendedor aceita FGTS e financiar o resto?" (`condicao_pagamento`) | `credito_documentacao/financiamento_negado` ✗G | grupo em 0,54 × 0,55 entre `preco` e `credito`: a requisição `grupo` disse preço, a `tudo` disse crédito (isolamento ≠ determinismo). a e b acertaram |
| T044 "disseram que alaga toda vez que chove" (`entorno_seguranca`) | `imovel/estado_conservacao` ✗G | "alagamento" mora na descrição da folha, que a Choice do grupo não vê; b acertou |
| T061 dono retirou a casa; cliente reclama que as alternativas não têm quintal (`imovel_indisponivel`) | `imovel/falta_item` ✗G | "evento que encerra vence queixa lateral" está nas regras, mas a última palavra do cliente pesou mais; as três variantes erraram |
| T068 anúncio dizia 82 m² e 2 vagas; corretor confirma 64 m² e 1 vaga (`diferente_do_anuncio`) | `atendimento/informacao_errada` ✗G | a fronteira ANÚNCIO × ATENDIMENTO do LEIA-ME: a informação errada foi dita pelo corretor na visita; b acertou |
| T060 "30% dá quanto?" → R$ 55.500 → silêncio (`sumiu_apos_valor`) | `sem_informacao/sumiu_sem_resposta` ✗f | 0,55 × 0,45 entre as duas folhas; o silêncio veio depois de um VALOR calculado, não do preço do anúncio; b acertou |
| T065 "meu pai disse que não é esse, não explicou" (`decisor_vetou`) | revisar (grupo 0,39) | `momento_cliente` 0,39 × `sem_informacao`: "não explicou" puxa para sem informação; b (soma 30 folhas) acertou |
| T024 "não fiquei satisfeita com o atendimento, só isso" (`atendimento`, só grupo) | revisar (`blames_agency` 0,20) | a Choice acertou `only_group`; o Noul lê a lista de condutas e não vê "insatisfeita com o atendimento" como culpa |
| T055 só pode visitar depois das 19h; o dono só permite em horário comercial (`visita_falhou`) | revisar (`blames_agency` 0,13) | Choice certa (0,99); a guarda pede culpa do corretor e a folha cobre "nenhum horário compatível", onde não há culpa |
| T007 "já marquei três visitas com outra corretora" depois de 3 dias sem resposta (`demora_resposta`) | revisar (`concorrencia` 0,61; `closed_elsewhere` 0,13) | regra 3 do LEIA-ME (o porquê é a folha) não venceu na Choice; a guarda segurou. b acertou |
| T028 simulação prometida não veio; "fiz no banco e vou de leilão" (`demora_resposta`) | revisar (`concorrencia` 0,99; `closed_elsewhere` 0,27) | idem; o destino (leilão) nem está na taxonomia. As três variantes foram para `concorrencia`; a guarda segurou |

## Lições
1. **Numa taxonomia de 2 níveis, o grupo não é "mais fácil" que a folha.** A Choice de grupo que só vê nomes de
   folhas errou onde a descrição da folha tinha a palavra; a Choice plana com as 30 descrições apontou o grupo
   certo em 66/68. Hipótese para a próxima rodada (não medida): levar a descrição das folhas para o critério do
   grupo, ou derivar o grupo da Choice plana e usar a hierarquia só para a abstenção.
2. **`only_group` é o que a Choice plana não tem.** Limiar de probabilidade não separa "só grupo" de folha (certa
   mínimo 0,41, errada até 0,84); uma opção explícita separou 6/7. Decompor rendeu exatamente onde a Choice não vê a
   classe (lição 32), e só aí.
3. **Guarda é literal e cobra o que a taxonomia não promete.** `blames_agency` = "culpa do corretor", mas o grupo
   `atendimento` inclui falta de horário e insatisfação sem detalhe. A guarda de `concorrencia` pagou (2 erros
   caros a menos); a de `atendimento` custou 2 acertos. Guarda só no lado caro (lição 31): a de concorrência
   protege o relatório contra um erro que a Choice comete de fato; a de atendimento protegeu contra um erro que não
   apareceu em 68 casos.
4. **Uma requisição custa 2,4× os tokens e devolve o mesmo acerto** (c × a: 0,853 × 0,868, diferença = 1 caso num
   empate 0,54 × 0,55). O que c compra é latência (286 × 561 ms) e um state só; o que paga são 7 Choices
   especulativas de folhas, com as regras repetidas em cada uma.
5. **Empates de 0,5 trocam de lado entre requisições**: a mesma Choice `group`, no mesmo state, deu `preco` 0,54
   numa requisição e `credito` 0,55 em outra. Grupo em 0,5–0,6 é revisão, não decisão — e o limiar 0,5 deixa passar.
6. **Ajuste pequeno não calibra limiar** (de novo): 2 `null` e 3 `sem_informacao` no ajuste; nenhum ponto da grade
   separou erro de acerto; os limiares ficaram na partida e o teste é quem disse.

## Limites
- Dados sintéticos, um rotulador (Fable), um modelo, uma rodada; 68 conversas com 30 folhas = 1–3 casos por folha.
  Um caso vale 1,5 ponto percentual; o critério 2 passou com folga de dois casos.
- A hipótese "Choice plana para o grupo + hierarquia só para abstenção" vem de olhar o teste: é hipótese, não
  desenho medido; a variante b não foi afinada para abster.
- Conversa inteira no state: aqui são 4–12 turnos; conversas longas de CRM exigem recorte (últimas N mensagens ou
  a janela depois da última visita) e isso não foi medido. Teto de 6.000 caracteres → revisar, sem chamada.
- As regras de precedência vão escritas na pergunta; o teste mede a política escrita, não a descoberta dela.
- Taxonomia maior: 8 Choices de folhas numa requisição escalam com o número de grupos; acima disso volta o funil
  em duas requisições (variante a) ou o beam da receita.
- Latência medida com 8 conversas em paralelo; a de a é a soma de duas requisições sequenciais.

## Como rodar
```
python run.py rascunho      # encanamento → resultados-rascunho.md
python run.py ajuste        # afinação
python run.py congelar      # manifesto (código, dados de teste, taxonomia, critério, principal)
python run.py               # ajuste + teste (só com o manifesto batendo)
python testa_falhas.py      # bateria do código, sem API
JEV_MODO=gravado python run.py   # reproduz do cache/, sem chave
```
Consumidor: `motivo.julgar_seguro(jev, conversa, taxonomia)` → `{"grupo", "folha", "revisar", "origem", "motivo", …}`.
`origem: "falha"` é "sem motivo por erro operacional ou conversa inválida" (`invalida: true` no segundo caso),
diferente do `sem_informacao` julgado (`origem: "jev"`); `revisar: true` é conversa que o código não fecha sozinho.
Taxonomia inválida levanta erro: é defeito de quem chama, antes de qualquer requisição.
