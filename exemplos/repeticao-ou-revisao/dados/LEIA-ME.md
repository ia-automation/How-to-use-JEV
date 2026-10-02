# Dados do `repeticao-ou-revisao` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item M) e [DADOS.md](../../DADOS.md).
Mensagens sintéticas de WhatsApp de uma imobiliária (pedido de visita, fotos, valores), pt-BR informal. Só primeiros
nomes inventados; nenhum telefone, e-mail ou CPF; imóvel citado por rua, bairro ou código de anúncio ("cód. 2041"),
nunca por andar ou número de unidade. Gabarito = o que um atendente experiente faria lendo só o grupo.

Arquivos: `rascunho.json` (5 fáceis), `ajuste.json`, `teste.json` (abrir uma vez, no fim). Envelope
`{"versao", "autor": "fable", "casos"}`. A ordem dos grupos foi embaralhada.

## Esquema (o do briefing, sem campo extra)
`{"id", "mensagens": [{"id", "de", "texto", "minutos_desde_a_primeira"}], "relacao", "acao_vigente", "nota"}`
- `mensagens`: 2 ou 3, IDs `m1`…`m3`, do MESMO remetente, na ordem de chegada. `de` ∈ `cliente | corretor`
  (`corretor` = corretor da casa pedindo à central de agendamento; igual em todas as mensagens do grupo).
- `minutos_desde_a_primeira`: inteiro ≥ 0, não decrescente; `m1` = 0.
- `relacao` ∈ `same_intent | revision | additional_request | unclear`.
- `acao_vigente`: `"m1"` em `same_intent`; a ÚLTIMA mensagem em `revision`; `null` em `additional_request` (valem
  todas) e em `unclear`.
- `nota`: começa com `"difícil: <família>"` nos casos difíceis.

## O que cada relação significa na prática (é o que o código faz com ela)
| `relacao` | O que o atendente faz | `acao_vigente` |
|---|---|---|
| `same_intent` | executa UMA vez; as outras são cópia, cobrança ou confirmação | `m1` |
| `revision` | executa só o que a última diz; o pedido anterior deixa de valer | a última |
| `additional_request` | executa tudo: nada é descartado | `null` |
| `unclear` | pergunta antes de agir | `null` |

## `same_intent` — mesma intenção, nenhum atributo muda
- Reenvio idêntico (falha de envio), com ou sem erro de digitação; paráfrase com os mesmos atributos (imóvel, dia,
  hora); mesma data dita de outro jeito ("dia 10" → "sábado dia 10").
- Cobrança ("?", "oi?", "alguém aí?") e reforço ("não esquece hein, sábado 9h").
- Confirmação com palavra negativa que não muda nada ("não precisa mudar nada, só confirmando terça 15h").
- **Cópia de terceiro**: "minha esposa também pediu essa visita, é a mesma" → repetição (uma visita só).
- Correção com asterisco que só conserta a grafia ("vizita" → "*visita").
- **O intervalo não decide**: texto igual 95 ou 180 minutos depois continua repetição (o aplicativo reenviou a
  pendente, ou o cliente cobrou). Só vira pedido novo quando o texto diz ("outra visita", "de novo, agora com meu pai").
- Um pedido de cancelamento repetido também é `same_intent` (o pedido repetido é o cancelamento).

## `revision` — a última corrige, substitui ou cancela
- Muda um atributo do pedido anterior: dia, hora, imóvel ("em vez de"), código do anúncio, quantas pessoas vão.
- Cancela ("cancela", "deixa pra lá, fechei com outro", "não vou conseguir ir, depois remarco").
- Desfaz uma revisão ("esquece, deixa terça mesmo"): vale a última, que restaura a primeira.
- Correção com asterisco que muda o conteúdo ("às 10h" → "*11h").
- "Também" que não soma ("sexta também não vai dar, vê segunda").
- Revisão + pedido novo NA MESMA mensagem ("muda pra domingo e me manda a planta") → `revision`: a última mensagem
  carrega tudo o que vale.
- **Limite do esquema, rotulado com nota**: quando `m1` tinha dois pedidos e a última corrige só um ("a visita deixa
  pra domingo"), a relação é `revision` e `acao_vigente` é a última, mas o outro pedido de `m1` continua de pé.
- Em grupo de 3, repetição seguida de correção (`m1` = `m2`, `m3` corrige) é `revision`.

## `additional_request` — pedido novo que se soma
- Outro imóvel, outra visita, outro tipo de pedido (fotos + visita; valor + financiamento), anunciado ou não por "e
  também", "outra", "a segunda".
- **Complemento** (decisão do rotulador): mensagem que traz o detalhe que faltava sem contradizer nada — o horário
  de um dia já dito, o nome de quem vai, "também pode ser à tarde" (amplia a disponibilidade) — é
  `additional_request`: vale a soma das mensagens, nenhuma é descartada. Rotular como `revision` diria que algo de `m1` deixou de valer, e nada deixou;
  como `same_intent`, perderia o detalhe.
- Terceiro com pedido NOVO ("minha esposa também quer ver, mas no domingo; marca uma pra ela").
- Segunda visita intencional ao mesmo imóvel ("volto na terça com o engenheiro, já deixa agendado também").
- Em grupo de 3, repetição seguida de pedido novo (`m1` = `m2`, `m3` soma) é `additional_request`.

## `unclear` (~10%) — o texto não decide entre corrigir e somar
- Sem conectivo: "marca terça 15h" → "quarta 15h" (troca ou segunda visita?).
- Mesmo imóvel, dois horários no mesmo dia; mesmo horário, dois imóveis; ruas de nome parecido.
- Negativa sem referente: "cancela" depois de dois pedidos.
- **Mensagem atrasada fora de ordem**: chega primeiro "então fica quarta mesmo" e depois "consegue terça 15h?" — a
  ordem de chegada contradiz a lógica; o atendente confirma.
- Terceiro ambíguo: "minha esposa pediu domingo" (trocou a visita ou pediu outra?).

## Precedência quando duas leituras disputam
1. O texto diz que é o mesmo pedido → `same_intent`, mesmo com intervalo grande.
2. A última nega, troca ou cancela algo dito antes → `revision`.
3. A última acrescenta sem contradizer → `additional_request`.
4. Há mudança de atributo sem marca de troca nem de soma → `unclear`.
Grupos mistos em mensagens separadas (revisão em `m2` e pedido novo em `m3`) ficaram de fora: o esquema tem uma
relação por grupo.

## Famílias de caso difícil (`nota` começa com "difícil:")
1. Mudança de dia, hora, imóvel ou outro atributo (inclui asterisco que muda o conteúdo e código parecido).
2. Negativa: cancelamento implícito; negativa que NÃO revisa; negativa da negativa.
3. Segundo pedido intencional parecido.
4. Cópia de terceiro (mesmo pedido) × terceiro com pedido novo × terceiro ambíguo.
5. Mensagem atrasada: cópia tardia (repetição) × fora de ordem (`unclear`).
6. Retry idêntico com erro de digitação; asterisco que só corrige grafia; paráfrase.
7. "E também" que soma × "também" que não soma × "também" que amplia.
8. Complemento (detalhe que faltava).
9. Grupo de 3: repetição + revisão; repetição + pedido novo; cadeia de revisões; revisão desfeita.
10. Revisão + pedido novo na mesma mensagem; revisão parcial.
11. Sem conectivo / sem referente → `unclear`.

## Contagens (validador do rotulador, 2026-10-01, zero erros)
| arquivo | grupos | difíceis | `same_intent` | `revision` | `additional_request` | `unclear` | grupos de 3 | de `corretor` |
|---|---|---|---|---|---|---|---|---|
| `rascunho.json` | 5 | 0 | 2 | 2 | 1 | 0 | 0 | 0 |
| `ajuste.json` | 29 | 24 (83%) | 8 (28%) | 9 (31%) | 8 (28%) | 4 (14%) | 5 | 3 |
| `teste.json` | 58 | 42 (72%) | 16 (28%) | 18 (31%) | 17 (29%) | 7 (12%) | 8 | 5 |

Por família (ajuste / teste): grupo de 3 3/4 · sem conectivo 2/3 · mensagem atrasada 2/3 · retry com erro de
digitação 1/3 · segundo pedido intencional parecido 1/3 · complemento 1/3 · paráfrase 1/2 · cópia de terceiro 1/2 ·
negativa que não revisa 1/2 · mudança de imóvel 1/2 · mudança de hora (asterisco) 1/0 · mudança de dia (asterisco)
0/1 · mudança de hora condicional 0/1 · mudança de atributo que não é dia nem hora 0/1 · negativa (cancelamento
implícito) 1/1 · negativa da negativa 1/1 · negativa sem referente 1/1 · "e também" que soma 1/1 · "também" que não
soma 1/1 · "também" que amplia 1/1 · terceiro com pedido novo 1/1 · terceiro ambíguo 0/1 · asterisco que só
corrige grafia 1/1 · revisão + pedido novo na mesma mensagem 1/1 · revisão parcial 0/1 · `m1` já é uma remarcação 0/1.
Os casos fáceis também cobrem mudança de dia, de hora e cancelamento explícitos.

O validador conferiu: envelope, campos e tipos, enums (`relacao`, `de`), 2–3 mensagens com IDs `m1`…`m3`, mesmo
remetente no grupo, minutos inteiros não decrescentes com `m1` = 0, `acao_vigente` × `relacao` (`m1` em
`same_intent`, a última em `revision`, `null` nas outras), IDs em sequência, mínimos, ≥ 30% difíceis, nenhum grupo
repetido (nem entre arquivos), nenhum padrão de telefone, CPF, e-mail ou URL, UTF-8 sem BOM, LF.

Ambiguidades decididas pelo rotulador (não estavam no briefing): `de` ∈ `cliente | corretor`; complemento é
`additional_request`; intervalo longo não transforma cópia em pedido novo; mensagem fora de ordem é `unclear` (a
regra "a última em `revision`" não deixa apontar a primeira); cancelamento é `revision`; cancelamento repetido é
`same_intent`; revisão + pedido novo na mesma mensagem é `revision`; revisão parcial é `revision` com nota do
limite; grupos mistos em mensagens separadas ficaram de fora; `unclear` também cobre "sem conectivo" (terça 15h →
"quarta 15h").
