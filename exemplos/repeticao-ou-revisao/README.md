# Repetição ou revisão (fila de mensagens, pt-BR) — colapsar / substituir / somar / revisar

Na fila de mensagens de um cliente, "pode marcar terça" seguido de "não, terça não; quarta" é **revisão**; duas
cópias do mesmo pedido por falha de envio são **repetição**; "e também quero ver o da Rua X" é **pedido
adicional**. Este exemplo julga UM grupo de 2–3 mensagens do mesmo remetente por requisição e devolve um sinal de
reconciliação. Os números vêm dos relatórios gerados pelo `run.py`: a rodada cega está em
[`resultados-rodada1.md`](resultados-rodada1.md) ([`resultados.md`](resultados.md) é a rodada 2, pós-revisão e não
cega, regenerada do cache em modo `gravado` com o código corrigido: mesmos números) e as variantes de desenho em
[`resultados-variantes.md`](resultados-variantes.md).

Candidato à **fila de mensagens da Luci (0010)**: roda sobre o lote pendente do mesmo contato antes de o agente
agir. **É um sinal de reconciliação, nunca um mecanismo de "exatamente uma vez"**: nada é executado nem
descartado daqui; idempotência por ID, ordenação e controle de efeito continuam no processo que consome a fila.

## Problema
Colapsar errado perde a correção; executar tudo duplica o efeito. Os dois erros caros, contados à parte:
- **correção perdida**: uma `revision` sai `colapsar` — a última mensagem é tratada como cópia e a troca some;
- **efeito duplicado**: uma `same_intent` sai `somar` — o mesmo pedido é executado duas vezes.

O que confunde (regras em [`dados/LEIA-ME.md`](dados/LEIA-ME.md)): negativa que não revisa ("não precisa mudar
nada"); "também" que não soma ("sexta também não dá"); asterisco que só corrige grafia × que muda a hora; cópia
de terceiro ("minha esposa também pediu, é a mesma"); complemento (o horário que faltava é `additional_request`);
mudança de atributo sem palavra de troca nem de soma, cancelamento sem referente e mensagem fora de ordem
(`unclear`).

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Mesmo ID entregue duas vezes; texto idêntico ao da mensagem imediatamente anterior (caixa, espaços e pontuação final normalizados) → cópia, **sem chamada** | **código** (`relacao.preparar`) | igualdade é exata; acento e pontuação interna ficam de fora da normalização — atalho de código só decide com prova |
| Ordem e tempo: `minutos_desde_a_primeira` validado (não decrescente); fora de ordem = entrada inválida → `revisar` | **código** | limite #3; quem ordena é a fila, dona dos carimbos. O intervalo não decide a relação (LEIA-ME) e não vai ao state |
| QUAL das quatro relações a última mensagem tem com as anteriores | Jev, Choice `relation` (4 opções com `what`/`not_for`/`examples`) | relação semântica entre textos, espaço fechado |
| A última cancela ou muda algo? Faz um pedido novo? Traz um detalhe que faltava? Não traz nada novo? | Jev, Nouls `replaces_previous`, `adds_new_request`, `completes_previous`, `same_request_again` | Choice é relativa (sempre há vencedor); o Noul absoluto confirma a proposta e nega a leitura do erro caro (limite #8) |
| Atributo diferente sem palavra de troca nem de soma? Cancela sem dizer qual pedido? Chegou fora de ordem? | Jev, Nouls de dúvida `no_link_word`, `target_not_said`, `arrived_out_of_order` | o lado absoluto da opção `unclear`, uma condição por pergunta |
| Política assimétrica, faixas, validação da resposta, falha → `revisar` por grupo, `acao_vigente` | **código** (`relacao.politica`, `julgar_seguro`, `vigente`) | o Jev julga, o código decide; ausência de resposta nunca vira `colapsar`, `substituir` nem `somar` |
| Executar, cancelar, responder ao cliente | processo que consome a fila | efeito não é do Jev |

## Desenho
State `{"from": "client"|"broker", "earlier_messages": ["…"], "last_message": "…"}` — a última mensagem é apontada
por nome, não por índice (menos indireção; a mesma pergunta serve a grupos de 2 e de 3); IDs e minutos ficam no
código. Uma requisição com 8 perguntas (1 Choice + 7 Nouls), em inglês, todas em [`perguntas.py`](perguntas.py)
com as faixas e o critério. Decisão em [`relacao.py`](relacao.py):

1. Código: validação, idempotência por ID, cópia adjacente fora. Sobrou uma mensagem só → `same_intent`
   (`colapsar`) sem chamada. Mais de 3 distintas ou mais de 1.500 caracteres → `revisar` sem chamada.
2. Choice `unclear`, algum Noul de dúvida ≥ 0,7, ou confiança da Choice < 0,5 → `revisar`.
3. `colapsar` exige Choice `same_intent` + `same_request_again` ≥ 0,7 + `replaces_previous` ≤ 0,3 + os dois Nouls
   de soma ≤ 0,3.
4. `substituir` exige Choice `revision` + `replaces_previous` ≥ 0,7 (e `same_request_again` < 0,7).
5. `somar` exige Choice `additional_request` + (`adds_new_request` ou `completes_previous`) ≥ 0,7 +
   `same_request_again` ≤ 0,3 + `replaces_previous` ≤ 0,3.
6. Qualquer outra combinação → `revisar`. `acao_vigente`: a primeira em `colapsar`, a última em `substituir`,
   nenhuma em `somar` e `revisar` — calculada sobre o grupo **sem reentregas por ID**.
7. Toda saída leva `ids_de_contexto_obrigatorio` (as mensagens distintas do grupo, em qualquer sinal) e
   `descartar_anterior: false`. `acao_vigente` diz qual ação vale; o consumidor entrega ao agente TODAS as
   mensagens do contexto obrigatório. Nenhum sinal autoriza apagar mensagem.

Falha operacional (timeout, cache faltando, resposta fora do contrato, grupo inválido) sai `revisar` para aquele
grupo por `relacao.julgar_seguro`. [`testa_falhas.py`](testa_falhas.py) prova isso sem rede: 31 falhas, grade de
26.244 combinações da política, 38 checagens do código e um relatório com 3 grupos inválidos em 5.

**Duas decisões medidas no ajuste** ([`resultados-variantes.md`](resultados-variantes.md)): minutos no state não
mudaram nenhuma decisão (política 0,931 nas duas; diferença média nos Nouls 0,011) e custam +30 tokens → ficam
fora; grupo de 3 julgado em pares (duas requisições, composição no código) acertou 2 dos 3 grupos de 3 mensagens
distintas contra 3 de 3 do grupo inteiro — o par "?" → "alguém pode agendar…" sem a primeira mensagem é ilegível
— e custa uma requisição a mais → grupo inteiro. São 3 grupos: indica a direção, não mede.

## Baselines (código, sem Jev)
- **igualdade normalizada**: textos iguais ⇒ repetição; senão executa tudo (`additional_request`);
- **Jaccard de palavras** entre a última e a anterior mais parecida: ≥ 0,5 ⇒ repetição; ≥ 0,05 ⇒ revisão; abaixo
  ⇒ pedido novo (os melhores limiares da grade do ajuste: o baseline teve a mesma chance de afinação);
- **a última sempre vale**: sempre `revision`.
Nenhum diz `unclear`. Referência extra: "sempre revisa" (zero erro caro, 100% a humano).

## Critério de continuar/descartar (fixado ANTES de abrir o teste, 2026-10-01)
No teste (58 grupos): (1) correção perdida = 0 de 18; (2) efeito duplicado ≤ 1 de 16; (3) relação (4 classes)
≥ melhor baseline no próprio teste + 0,15. Secundário, não decide: `unclear` → `revisar` ≥ 70%; revisou sem
necessidade ≤ 20% dos decidíveis; `acao_vigente` certa ≥ 80%. Está no manifesto `congelamento.json` e o veredito
é calculado pelo `run.py`.

## Resultados (`jev-1.13.0`, 2026-10-01; rodada cega, uma execução)
Ajuste = 29 grupos (24 difíceis; 8 `same_intent`, 9 `revision`, 8 `additional_request`, 4 `unclear`); teste = 58
(42 difíceis; 16, 18, 17, 7). Manifesto gravado antes; teste rodado uma vez.

| | ajuste (n = 29) | teste (n = 58) |
|---|---|---|
| igualdade normalizada: relação · correção perdida · **efeito duplicado** | 0,345 · 0/9 · 6/8 | 0,345 · 0/18 · **13/16** |
| Jaccard de palavras: relação · correção perdida · efeito duplicado | 0,586 · 0/9 · 1/8 | 0,448 · 0/18 · 2/16 |
| a última sempre vale: relação | 0,310 | 0,310 |
| só Choice (vencedora, sem Nouls nem piso): relação · `unclear` → revisar | 0,897 · 2/4 | **0,931 (54/58)** · 4/7 |
| **Jev (política)**: relação · correção perdida · efeito duplicado | 0,931 · 0/9 · 0/8 | **0,862 (50/58) · 0/18 · 0/16** |
| Jev (política): `unclear` → revisar · revisou sem necessidade · `acao_vigente` certa | 4/4 · 2/25 · 28/29 | 7/7 · 8/51 (15,7%) · 54/58 |
| Nouls contra o gabarito (corte 0,5): troca · soma · repetição | 0,957 · 0,957 · 1,000 | 0,938 · 0,938 · 1,000 |
| código sem chamada (todos `same_intent`) · cópia adjacente tirada antes do Jev | 2 · 2 | 3 · 3 |
| requisições · p50 / p95 · tokens por requisição · US$ por mil grupos | 27 · 306 / 340 ms · 2.693 · 0,105 | 55 · 270 / 355 ms · 2.694 · 0,107 |

**Critério no teste: passou os três** — (1) 0/18 ✓ · (2) 0/16 ✓ · (3) 0,862 ≥ 0,598 (Jaccard 0,448 + 0,15) ✓.
Secundários: 7/7 ✓ · 15,7% ✓ · 93,1% ✓.

Matriz do teste, Jev (gabarito → previsto): `same_intent` 13, 3 → revisar · `revision` 17, 1 → revisar ·
`additional_request` 13, 4 → revisar · `unclear` 7/7. **Os 8 erros são todos `revisar` sem necessidade; nenhuma
relação foi trocada por outra.** Cobertura automática: 43 de 58 (74%), erro entre os automáticos 0.

Custo total da construção: 175 requisições (orçamento 300) — 6 de rascunho, 81 em três passadas de ajuste, 33 das
variantes, 55 de teste; 451.550 tokens de entrada, US$ 0,019.

## O que deu certo
- **O que é exato ficou no código e não custou requisição**: 3 dos 58 grupos do teste saíram por igualdade (3/3
  certos) e em outros 3 o código tirou a cópia adjacente antes de perguntar.
- **Zero erro caro, com as regras de código errando para os dois lados**: a igualdade exata duplicaria 13 das 16
  repetições (paráfrase, confirmação, erro de digitação, cópia de terceiro); o Jaccard acertou 45%.
- **Os Nouls de dúvida acharam o `unclear` que a Choice não achou**: 7/7 contra 4/7. `target_not_said` deu 0,95 em
  "desmarca" depois de dois pedidos (Choice: `revision` 0,59) e `no_link_word` 0,94–0,95 em dois grupos sem
  palavra de ligação — um "sem conectivo" e um "dia 12" × "dia 21" (Choice: `revision` 0,51 e 0,43). Fora dos
  `unclear`, nenhum dos três passou de 0,53 (0/48).
- **`same_request_again` separou limpo**: 13/13 repetições que foram ao Jev em ≥ 0,67 e todo o resto em ≤ 0,17.

## O que falhou (8 revisões sem necessidade no teste)
| Grupo | Família | Causa |
|---|---|---|
| RR-T004 | paráfrase ("dia 10" → "sábado dia 10") | `completes_previous` 0,54: o dia da semana lido como detalhe que faltava. A regra está na Choice, não no `false` do Noul novo |
| RR-T049 | retry com erro de digitação ("as 10" → "às 10h") | `completes_previous` 0,37, a 0,07 do corte: a mesma causa |
| RR-T052 | cópia de terceiro ("pode considerar uma só") | `replaces_previous` 0,53: a guarda do lado caro disparou numa repetição |
| RR-T024 | mudança de hora condicional ("se tiver à tarde eu prefiro, senão mantém 10h") | Choice `revision` com confiança 0,49 (piso 0,5); `replaces_previous` 0,23, `completes_previous` 0,89 — lida como ampliação |
| RR-T025 | segundo pedido parecido ("outra visita, agora com meu pai") | `adds_new_request` 0,64 e `replaces_previous` 0,61 |
| RR-T034 | "também" que amplia ("quarta também serve") | Choice certa com confiança 0,45; `completes_previous` 0,72 |
| RR-T043 | fácil: visita + "me manda o endereço certinho" | caiu ENTRE os dois Nouls de soma: pedido novo 0,37, complemento 0,39 |
| RR-T053 | complemento ("meu nome é Cristina, esqueci de falar") | a Choice errou (`same_intent`, confiança 0,31); o piso segurou |

- **A política perdeu para a Choice sozinha no acerto (0,862 × 0,931).** Os Nouls mudaram 11 decisões no teste:
  3 `unclear` recuperados, 1 erro da Choice trocado por revisão e **7 acertos mandados a `revisar`**. Erro caro
  evitado: nenhum — a Choice sozinha também teve 0/18 e 0/16. A guarda dos Nouls contra o erro caro é seguro por
  desenho, **não benefício medido** nesta amostra.
- **O ajuste não previu a taxa de revisão**: 2/25 (8%) no ajuste, 8/51 (15,7%) no teste.

## Lições
1. **Guarda só no lado caro.** Exigir `completes_previous` em "não" para colapsar não protege de nenhum dos dois
   erros caros e custou 2 das 8 revisões (paráfrase e retry que acrescentam uma palavra). Guarda extra tem de
   apontar para um erro com custo declarado; senão é só revisão a mais.
2. **Dividir um Noul em dois abre um vão entre eles.** Separar "pedido novo" de "complemento" consertou o
   complemento (0,21 → 0,92–0,94) e deixou o "me manda o endereço" sem dono (0,37 e 0,39). Ao dividir, conferir
   no ajuste o caso que fica no meio — ou somar as duas leituras em código antes de aplicar a faixa.
3. **Choice relativa + Noul absoluto é para a classe que a Choice não vê, não para tudo.** Onde rendeu: `unclear`
   (7/7 × 4/7). Nas três relações decidíveis a Choice sozinha acertou 50 de 51. A confiança dela já avisava: os 4
   erros da Choice no teste tinham confiança ≤ 0,59, e acima de 0,7 ela não errou (47 grupos) — leitura posterior
   ao teste, não regra validada: no ajuste um `unclear` saiu `revision` com 0,80.
4. **Ajuste pequeno e difícil calibra desenho, não limiar** (de novo): as três passadas acharam defeitos de
   pergunta (complemento, "*visita", `unclear` sem Noul próprio); a faixa 0,3–0,7 saiu de quatro valores de
   fronteira e no teste a curva é plana entre 0,3–0,7 e 0,5–0,5 (43–44 automáticos, zero erro).
5. **O que o código decide por igualdade tem de ser conservador**: só cópia adjacente (repetir a primeira depois
   de uma mudança desfaz a mudança) e sem mexer em acento nem em pontuação interna.

## Limites
- Dados sintéticos de um rotulador só (Fable), por famílias; os exemplos das opções da Choice vêm do LEIA-ME, e
  o teste tem casos das mesmas famílias. **Um placar assim valida o mecanismo, não o desempenho na fila real.**
  Uma rodada, um modelo.
- Os zeros são de amostra pequena: 0/18 correções perdidas não exclui uma taxa real de vários por cento.
- **`substituir` não autoriza descartar a mensagem anterior inteira.** Em revisão parcial (RR-T014: "agenda a
  visita e me manda a planta" → "a visita deixa pra domingo") a relação é `revision`, mas o pedido da planta
  continua de pé: o esquema tem uma relação por grupo e não diz O QUE foi substituído. Desde a revisão do Codex
  isso está na SAÍDA, não só neste texto: `ids_de_contexto_obrigatorio` traz as duas mensagens e
  `descartar_anterior` é sempre `false`. O que continua não medido: QUAL parte da anterior foi substituída.
- Grupos mistos (revisão numa mensagem e pedido novo em outra), mais de 3 mensagens distintas, remetentes
  diferentes e mensagens longas não foram medidos; os dois últimos casos e o grupo grande saem `revisar` sem
  chamada.
- Mensagem fora de ordem só é detectada pelo TEXTO (`arrived_out_of_order`: 0,93 e 0,80 nos dois casos vistos);
  minutos decrescentes na entrada são erro de quem chama.
- A normalização da igualdade não reconhece reenvio com acento ou digitação diferente: esses grupos vão ao Jev
  (custam uma requisição; no teste, os 3 "retry com erro de digitação" foram).
- Não medido: texto adversarial no corpo da mensagem (limite #6); mensagens que não são pedido (áudio transcrito,
  figurinha, "ok").

## Pós-revisão do Codex (2026-10-01) — rodada 2, não cega
Três achados, todos aceitos. As perguntas, as faixas e os dados não mudaram; nenhuma chamada nova à API. A rodada 2
é o mesmo cache lido pelo código corrigido e deu **os mesmos números** da rodada cega (o teste não tem ID
repetido). O manifesto da rodada cega está em `congelamentos-anteriores/`.

1. **Reentrega ressuscitava o pedido corrigido (gravidade 2).** Em `[m1 "quinta", m2 "sexta", m1 "quinta"]` a
   reentrega de `m1` saía da leitura do Jev, mas `acao_vigente` era calculada sobre o grupo cru e devolvia `m1`
   como a ação que vale. Conserto: `acao_vigente` sobre o grupo sem reentregas por ID (`relacao.sem_reentregas`).
   A bateria ganhou o caso.
2. **Revisão parcial saía com contrato igual ao de substituição integral (gravidade 2).** Em RR-T014 o consumidor
   que encaminhasse só a `acao_vigente` perdia o pedido da planta; a proteção estava só neste README. Conserto:
   `ids_de_contexto_obrigatorio` e `descartar_anterior: false` em toda saída, inclusive na de falha.
3. **Os 7 Nouls não mostraram ganho (gravidade 4, desenho).** Hipótese registrada, **não validada**: na ablação
   retrospectiva do cache do teste, a Choice com piso de confiança 0,5 mais só dois Nouls de dúvida
   (`no_link_word` e `target_not_said` ≥ 0,7) manteria `unclear` → `revisar` em 7/7, zero nos dois erros caros e
   acertaria 55/58, contra 50/58 da política medida. É conta feita DEPOIS de ver o teste, sobre respostas de uma
   requisição com 8 perguntas: não prova o que uma requisição com 3 perguntas responderia. Simplificar só com
   dados novos e teste congelado.

## Rodar
```
python run.py rascunho      # encanamento (5 grupos)
python run.py ajuste        # afinação
python run.py variantes     # minutos no state e grupo de 3 em pares, no ajuste
python run.py congelar      # grava congelamento.json
python run.py               # ajuste + teste (exige o manifesto batendo)
python testa_falhas.py      # bateria do código, sem chave nem rede
```
`JEV_MODO=gravado` reproduz tudo do `cache/` sem chave. O `cache/` guarda também as respostas das duas primeiras
passadas de ajuste e da primeira do rascunho (redações anteriores), que a versão congelada não usa. No Windows,
use `PYTHONIOENCODING=utf-8`. A primeira execução com o teste gravou `resultados-rodada1.md`; o `run.py` nunca o
reescreve.
