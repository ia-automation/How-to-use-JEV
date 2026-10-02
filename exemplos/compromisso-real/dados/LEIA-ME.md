# Dados do `compromisso-real` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item S) e [DADOS.md](../../DADOS.md).
Trechos sintéticos de conversa de trabalho (chat de equipe), pt-BR informal, em quatro domínios: equipe de
desenvolvimento, agência, escritório (contabilidade e advocacia) e suporte. Só primeiros nomes inventados; nenhum
telefone, e-mail, documento ou empresa real. Gabarito = o que um gerente de projeto cuidadoso anotaria ao fim do
trecho: isto vira tarefa de alguém, ou é tarefa fantasma?

Arquivos: `rascunho.json` (5 fáceis), `ajuste.json`, `teste.json` (abrir uma vez, no fim). Envelope
`{"versao", "autor": "fable", "casos"}`. A ordem dos casos e a dos candidatos dentro de cada caso foram
embaralhadas (o candidato morto não é sempre o `k1`).

## Esquema (o do briefing, sem campo extra)
`{"id", "data_referencia", "conversa": [{"id", "autor", "texto"}], "candidatos": [{"id", "trecho",
"responsavel_candidato"}], "vereditos": {…}, "prazo": {…}, "nota"}`
- `data_referencia`: `AAAA-MM-DD`, o dia em que TODAS as mensagens do trecho foram escritas.
- `conversa`: 2–6 mensagens, IDs `m1`…, em ordem.
- `candidatos`: 2–4, IDs `k1`…. `trecho` é cópia LITERAL de um pedaço de uma mensagem (o validador confere).
  `responsavel_candidato` é um primeiro nome: quase sempre um autor da conversa; às vezes alguém citado que não
  escreveu (ausente). O mesmo trecho pode aparecer em dois candidatos com responsáveis diferentes.
- `vereditos`: uma chave por candidato ∈ `compromisso | proposta | cancelado | citacao_antiga | pedido_sem_aceite`.
- `prazo`: uma chave por candidato, `AAAA-MM-DD` ou `null`.
- `nota`: começa com `"difícil: <família> — …"` nos casos difíceis; `"fácil: …"` nos demais.

## O que o veredito julga
O PAR (trecho, responsável), lido **no fim da conversa**: *ao terminar o trecho, esta pessoa deve esta entrega?*
O trecho pode ser o pedido ("você revisa até amanhã?") ou a resposta ("reviso"); o veredito é o mesmo para os
dois, porque é a entrega que se julga.

| veredito | quando |
|---|---|
| `compromisso` | o responsável assumiu (disse ele mesmo, ou aceitou um pedido: "pode deixar", "fechado", "consigo", "👍") e nada depois desfez |
| `proposta` | oferta, sugestão ou intenção que ninguém confirmou ("posso mandar, se quiserem", "que tal eu…", "um dia eu faço"), tentativa sem firmeza ("vou tentar… depende"), ou aceite condicionado a um fato de TERCEIRO ainda não ocorrido |
| `cancelado` | era pedido, proposta ou compromisso DESTA conversa e uma mensagem posterior o desfez: cancelou, tornou desnecessário, trocou a data, trocou o dono ou trocou o escopo |
| `citacao_antiga` | o trecho é texto citado, colado ou encaminhado de ANTES desta conversa (e-mail antigo, ata, mensagem de cliente, cláusula, resposta automática): não é fala de agora |
| `pedido_sem_aceite` | alguém pediu ou atribuiu, e o responsável não aceitou: não respondeu, desconversou, recusou, ou nem estava na conversa |

### Precedência
`citacao_antiga` > `cancelado` > (`compromisso` | `proposta` | `pedido_sem_aceite`). Primeiro se pergunta "isto é
fala desta conversa?"; depois "alguma mensagem posterior matou?"; só então o estado do que sobrou.

### Decisões que desempatam
- **Oferta aceita vira compromisso.** "Posso mandar na quinta, se ajudar" + "manda sim" → `compromisso`. Elogio não
  aceita ("boa ideia, mas antes…") → segue `proposta`. Proposta recusada com todas as letras ("deixa para lá") →
  `cancelado`; proposta adiada ("vamos discutir na planning") → segue `proposta`.
- **Condição.** Fato de terceiro pendente ("se o cliente mandar os extratos", "desde que ele pague as custas",
  "assim que ele aprovar") → `proposta`. Condição cumprida DENTRO do trecho ("ela acabou de mandar" — "recebi") →
  `compromisso`. Ressalva de cortesia ("se nada pegar fogo") e ordem do próprio trabalho ("assim que fechar a
  sprint eu olho") não são condição → `compromisso`.
- **"Vou tentar".** Sozinho → `proposta`. Se a mesma pessoa firma a mesma entrega depois ("então quarta está
  pronto") → `compromisso` nos dois trechos (é a mesma entrega; nada foi trocado).
- **Troca × confirmação.** Mensagem posterior que TROCA data, dono ou escopo mata o trecho anterior (`cancelado`)
  e o trecho novo carrega o que vale. Mensagem posterior que só CONFIRMA a mesma entrega não mata nada.
- **Troca de dono.** "Deixa que eu faço", "você vai no lugar dele?" — "vou": o primeiro responsável → `cancelado`;
  o novo → `compromisso`.
- **Pedido para "alguém" / "um de vocês".** O candidato que não assumiu: se OUTRA pessoa assumiu → `cancelado`
  (para ele a tarefa não existe mais); se ninguém assumiu → `pedido_sem_aceite` (a necessidade segue sem dono).
- **Recusa.** Pedido recusado ("essa semana não rola", "tenho médico") → `pedido_sem_aceite`, não `cancelado`: quem
  pediu não retirou o pedido.
- **Responsável ausente.** "O Jonas manda amanhã" dito por outra pessoa, sem ele ter sido consultado →
  `pedido_sem_aceite`. Aceite relatado ("falei com a Karen, ela confirmou segunda") → `compromisso`.
- **"A gente".** Dito por quem depois assume em primeira pessoa → `compromisso` dessa pessoa. Desdobrado em donos e
  datas diferentes → a frase coletiva é `cancelado` e os desdobramentos são os compromissos.
- **Citação reafirmada.** "Como combinado ontem, o Fábio instala na quinta" + "isso, quinta às 8h" → `compromisso`:
  não há texto citado, e o responsável reafirma agora. Citação usada para cobrar ("você disse \"entrego na
  quarta\"") → `citacao_antiga`; o que vale é o que o responsável assume em seguida.
- **Cancelamento implícito.** O motivo da tarefa some (projeto cancelado, funcionalidade fora do escopo, "já
  resolvi", cliente adiou sem data, ordem contrária de outra área) → `cancelado`, mesmo sem a palavra "cancela".

## `prazo` — convenção (a conta é do CÓDIGO; o rotulador preencheu por função e o validador refez)
Preenchido para `compromisso`, `proposta` e `pedido_sem_aceite` quando a entrega tem dia resolvível; **sempre
`null`** para `cancelado` e `citacao_antiga` (não há tarefa viva). A data é a da ENTREGA, esteja ela no trecho, no
pedido que o trecho aceita ou numa resposta posterior ("Briefing para quando?" — "Segunda."): quem aceita ou assume
um pedido **herda** a data do pedido, salvo se disser outra.

| expressão | resolução a partir de `data_referencia` |
|---|---|
| "hoje", "agora", "hoje à tarde/noite", "até o fim do dia", "até as 18h" | a própria referência |
| "amanhã", "depois de amanhã", "em N dias" | referência + 1, + 2, + N dias corridos |
| dia da semana solto ("sexta", "na sexta", "até sexta", "sexta cedo") e "X que vem" | primeira ocorrência ESTRITAMENTE depois da referência (a referência não conta) — igual ao "sexta que vem" do `DADOS.md` |
| "X da semana que vem" | o dia X da semana civil seguinte (semana civil = segunda a domingo) |
| "dia 15", "no dia 5" | próxima ocorrência desse dia do mês, a referência CONTA (dia já passado → mês seguinte; vira o ano se preciso) |
| "até o fim do mês" | último dia do mês da referência |
| "até o fim da semana" | sexta-feira da semana civil da referência |
| "em N dias úteis" | N dias de segunda a sexta depois da referência, sem feriados |
| "semana que vem", "próxima semana", "essa semana", "este mês", "em breve", "assim que…", "um dia", sem data | `null` |

Sem ajuste para dia útil nem feriado: "dia 5" que cai num sábado fica no sábado; "sexta" que cai em 1º de janeiro
fica em 1º de janeiro. Horário ("às 10h") é ignorado. Nenhum caso usa um dia da semana igual ao da referência,
exceto um ("segunda, dia 4" dito numa segunda), em que as duas leituras coincidem.

### Datas de referência usadas e seus dias da semana
| `data_referencia` | dia da semana | casos |
|---|---|---|
| 2026-10-05 | segunda-feira | 6 |
| 2026-10-06 | terça-feira | 6 |
| 2026-10-07 | quarta-feira | 5 |
| 2026-10-08 | quinta-feira | 6 |
| 2026-10-09 | sexta-feira | 3 |
| 2026-10-14 | quarta-feira | 6 |
| 2026-10-20 | terça-feira | 6 |
| 2026-10-22 | quinta-feira | 6 |
| 2026-10-26 | segunda-feira | 4 |
| 2026-10-29 | quinta-feira | 5 |
| 2026-11-03 | terça-feira | 5 |
| 2026-11-12 | quinta-feira | 5 |
| 2026-11-27 | sexta-feira | 4 |
| 2026-12-10 | quinta-feira | 5 |
| 2026-12-28 | segunda-feira | 2 |

## Famílias de caso difícil (`nota` começa com "difícil:")
| Família (prefixo da `nota`) | ajuste | teste |
|---|---|---|
| citação antiga | 4 | 8 |
| responsável ambíguo | 3 | 6 |
| cancelamento implícito | 3 | 5 |
| prazo | 3 | 5 |
| pedido sem aceite | 2 | 5 |
| aceite condicional | 2 | 4 |
| correção tardia | 1 | 5 |
| proposta × compromisso | 1 | 3 |
| aceite curto | 1 | 1 |
| oferta aceita | 1 | 1 |

## Contagens (validador do rotulador, 2026-10-01, zero erros)
| arquivo | trechos | difíceis | candidatos | `compromisso` | `proposta` | `cancelado` | `citacao_antiga` | `pedido_sem_aceite` | com `prazo` |
|---|---|---|---|---|---|---|---|---|---|
| `rascunho.json` | 5 | 0 (0%) | 10 | 5 (50%) | 2 | 1 | 1 | 1 | 5 |
| `ajuste.json` | 23 | 21 (91%) | 47 | 24 (51%) | 5 | 7 | 4 | 7 | 29 |
| `teste.json` | 46 | 43 (93%) | 102 | 57 (56%) | 10 | 17 | 7 | 11 | 66 |

Por domínio (rascunho / ajuste / teste): agência 1/5/12 · dev 2/8/13 · escritório 1/5/10 · suporte 1/5/11.

## Aviso ao construtor
- `compromisso` é a classe majoritária dos candidatos (coluna acima): medir o baseline "sempre compromisso" e
  reportar acerto POR veredito. Erro caro: `cancelado`, `citacao_antiga`, `proposta` ou `pedido_sem_aceite` lidos
  como `compromisso` (tarefa fantasma).
- `prazo` é do código: o Jev decide o veredito e, no máximo, aponta QUAL expressão de data vale para o candidato;
  a conversão para `AAAA-MM-DD` segue a tabela acima. O prazo herdado de outra mensagem é a parte difícil.
- O trecho sozinho raramente decide: o veredito depende das mensagens POSTERIORES (aceite, troca, cancelamento).

## Ambiguidades decididas pelo rotulador (não estavam no briefing)
- Dia da semana solto = próxima ocorrência estritamente depois da referência (não inclusiva).
- `prazo` nulo em `cancelado` e `citacao_antiga`; preenchido em `proposta` e `pedido_sem_aceite` quando há dia.
- Quem aceita ou assume herda a data do pedido.
- Correção de data, dono ou escopo sempre aparece como candidato próprio; o trecho antigo é `cancelado`.
- Pedido recusado = `pedido_sem_aceite`; pedido assumido por outra pessoa = `cancelado` para o candidato original.
- Proposta recusada explicitamente = `cancelado`; proposta adiada ou ignorada = `proposta`.
- Aceite relatado de um ausente = `compromisso`; atribuição a um ausente não consultado = `pedido_sem_aceite`.
- "Semana que vem" sem dia = compromisso com `prazo` null.
- `responsavel_candidato` pode não ser autor de nenhuma mensagem.
