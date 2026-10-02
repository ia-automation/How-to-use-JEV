# Imóvel errado — decisões de rotulagem

Autor: fable (rotulador). Data: 2026-10-01. Escrito ANTES dos casos. Conversas sintéticas em pt-BR
informal (abreviações, erros leves), candidatos com resumo de 1–2 linhas. Bairros e cidades reais;
nenhum endereço com número, nenhum andar, unidade, nome, telefone ou e-mail.

Arquivos: `rascunho.json` (5 fáceis), `ajuste.json` (24 conversas), `teste.json` (48 conversas,
abrir uma vez no fim). Envelope `{"versao", "autor": "fable", "casos"}`.

## Esquema (o do briefing, sem campo extra)
`{"id", "conversa": [{"de": "cliente" | "agente", "texto"}], "candidatos": [{"id", "resumo"}],
"rascunho", "referente", "rascunho_usa_outro", "nota"}`
- `conversa`: 3–10 turnos; a última mensagem é sempre do **cliente**; `rascunho` é a resposta
  preparada pelo agente para ela.
- `candidatos`: 2–4, IDs `IM-01`…`IM-04` **na ordem em que foram apresentados na conversa** ("o
  primeiro" = `IM-01`). Os IDs nunca aparecem no texto da conversa (o cliente não os conhece).
- `referente`: ID do candidato de que a **última mensagem do cliente** trata, resolvido com a conversa
  inteira como um corretor experiente faria; `null` quando não dá para saber.
- `rascunho_usa_outro`: `true` se o rascunho afirma fatos (preço, quartos, bairro, vaga, pet,
  condomínio, metragem…) de um candidato diferente do referente — mesmo que nomeie o referente
  certo; `true` também quando mistura fatos de dois. `false` quando usa só fatos do referente ou
  nenhum fato de candidato ("vou confirmar e te retorno").
- `nota`: começa com `"difícil: <família>"` nos casos difíceis; explica todo `null`.

## Como o referente é resolvido (precedência)
1. **Correção do cliente** ("não, o primeiro"; "na vdd quero falar do outro") vale sobre tudo o que
   veio antes: o referente é o alvo corrigido.
2. **Nome/atributo que só um candidato tem** (bairro, preço, metragem, "o que tem piscina", "o da
   varanda") → esse candidato, mesmo que o foco anterior fosse outro (troca de foco).
3. **Citação de fala antiga** ("você disse que o da varanda aceita pet") → o candidato sobre o qual o
   agente disse aquilo; se o agente falou errado, o referente é o imóvel que o agente **descreveu**
   naquela fala (é dele que o cliente está falando).
4. **Referência relativa** ("o outro", "esse", "ele", "o primeiro/segundo"): com dois candidatos, "o
   outro" = o que não estava em foco; com três ou mais, "o outro" = o único ainda não discutido, se
   houver um só; senão `null`. "Esse/ele" = o candidato em foco no turno anterior.
5. **Continuidade**: sem marca nova, o referente é o candidato em foco na troca anterior.
6. **Contexto que descarta** ("o de Moema já descartei") retira o candidato do jogo: um atributo
   partilhado por dois pode ficar único.

## Quando é `null` (~15% dos casos, com nota)
- Atributo partilhado por dois candidatos ainda em jogo ("o que aceita pet", "o de 2 quartos").
- "O outro" com mais de um candidato ainda não discutido.
- Última mensagem sobre os dois ao mesmo tempo ("qual dos dois você recomenda?") ou sobre nenhum
  (pergunta geral sobre a imobiliária, saudação, imóvel que não está entre os candidatos: "o mesmo de
  ontem").
- Com `referente: null`, `rascunho_usa_outro` é `true` se o rascunho se compromete com um candidato
  como se fosse o referente (ou mistura); `false` se pede esclarecimento, responde genericamente ou
  compara nomeando cada candidato.

## Famílias difíceis (todas nos dois conjuntos; contagem do validador do rotulador em 2026-10-01)
Rascunho: 5 conversas, 0 nulos, 1 rascunho com outro imóvel, fáceis.
Ajuste: 24 conversas, 4 `referente: null` (17%), `rascunho_usa_outro` 10 true / 14 false, 18 difíceis.
Teste: 48 conversas, 8 `referente: null` (17%), `rascunho_usa_outro` 19 true / 29 false, 33 difíceis.

| Família | ajuste | teste |
|---|---|---|
| troca de foco no meio | 2 | 4 |
| citação de fala antiga | 2 | 7 |
| dois imóveis parecidos (mesmo bairro, preço próximo) | 3 | 5 |
| referência vaga ("o outro", "esse") | 2 | 5 |
| correção do cliente | 2 | 3 |
| atributo que só um tem | 3 | 9 |
| atributo que dois têm (→ null) | 3 | 6 |
| outros nulos: imóvel fora da conversa ("o de ontem", "o do telefone"), pergunta geral | 1 | 2 |
| pergunta elíptica que herda o tema ("e o da barra funda?") | 0 | 2 |

Além delas, em ambos os conjuntos: rascunho que nomeia o referente certo e usa fato do outro (ex.:
IE-A020, IE-T035), e rascunho que cita o outro candidato atribuindo o fato certo a cada um (`false`,
ex.: IE-A013, IE-T030). O validador conferiu: envelope, campos e tipos, `de` ∈ cliente|agente, 3–10
turnos, última mensagem do cliente, 2–4 candidatos `IM-01…`, `referente` entre os candidatos ou
`null` com nota, booleano, nenhum ID de candidato dentro do texto, ≥ 30% difíceis, UTF-8 sem BOM, LF.
