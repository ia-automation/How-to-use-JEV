# Próxima pergunta — decisões de rotulagem

Autor: fable (rotulador). Data: 2026-10-01. Escrito ANTES dos casos. Conversas sintéticas em pt-BR
informal (abreviações, erros leves), 1–6 turnos, última mensagem sempre do **cliente**. Bairros e
cidades reais; nenhum nome, telefone, e-mail, andar ou unidade.

Arquivos: `rascunho.json` (5 fáceis), `ajuste.json` (20), `teste.json` (40, abrir uma vez no fim).
Envelope `{"versao", "autor": "fable", "casos"}`.

## Esquema (o do briefing, sem campo extra)
`{"id", "conversa": [{"de": "cliente" | "agente", "texto"}], "campos_conhecidos": {…}, "catalogo":
[{"id", "pergunta"}], "aceitaveis": [ids], "proibidas": [ids], "nota"}`
- `campos_conhecidos`: o que o CRM já tem antes da conversa; chaves iguais aos IDs do catálogo
  (`finalidade`, `orcamento`, `bairro`, `quartos`, `vagas`, `prazo`, `pet`, `financiamento`); pode ser `{}`.
- `catalogo`: o MESMO catálogo fixo em todo caso (abaixo). `aceitaveis` nunca vazio; `proibidas` pode
  ser vazio; os dois disjuntos; todo ID existe no catálogo.
- `nota`: começa com `"difícil: <família>"` nos casos difíceis.

## Catálogo fixo (10 perguntas-modelo)
| id | pergunta-modelo | grupo |
|---|---|---|
| `finalidade` | O imóvel é para comprar ou alugar? E é para morar ou para investir? | essencial |
| `orcamento` | Qual valor você tem em mente (preço de compra ou aluguel mensal)? | essencial |
| `bairro` | Em qual bairro ou região você prefere? | essencial |
| `quartos` | Quantos quartos você precisa? | essencial |
| `vagas` | Precisa de vaga de garagem? Quantas? | secundária |
| `prazo` | Para quando você precisa do imóvel? | secundária |
| `pet` | Você tem pet? | secundária |
| `financiamento` | Pretende financiar ou pagar à vista? | secundária |
| `visita` | Quer agendar uma visita? | ação |
| `no_question_needed` | Nenhuma pergunta é necessária agora: responder ou enviar opções. | nula |

## Quando uma pergunta é `proibida`
Pergunta cujo campo **já foi respondido** — explicitamente, de modo informal ("meu labrador precisa de
quintal" responde `pet`; "tenho dois carros" responde `vagas`; "a gente casa em outubro e quer entrar
antes" responde `prazo`; "já tenho carta de crédito" responde `financiamento`) ou pelos
`campos_conhecidos` não contraditos pela conversa. Também:
- **Correção tardia**: vale a última declaração ("na vdd 2 quartos tá bom") — o campo está respondido.
- **Campo conhecido contradito COM valor novo** ("tá 2 no cadastro, mas precisa ser 3") → respondido.
  Contradito SEM valor novo ("não dá mais pra ir até 500") → NÃO é proibida; vira aceitável (se essencial).
- **Sem sentido no contexto** conta como proibida: `financiamento` em aluguel; `pet` para investidor que
  não vai morar.
- `finalidade`: "alugar" sem mais = uso próprio → respondida. "comprar" sem mais deixa morar × investir em
  aberto → NÃO respondida. "ainda não sei se compro ou alugo" = respondida (perguntar de novo é repetir).
- `bairro`: região ampla (zona leste, "perto da Paulista", cidade pequena) conta como respondida — o
  corretor refina enquanto manda opções. Anúncio específico citado pelo cliente responde `bairro` e
  `quartos` implicitamente.
- `visita`: proibida se o cliente já pediu/marcou visita ou recusou visitar por agora.

## Quando uma pergunta é `aceitável` (tabela de decisão, aplicada em ordem)
1. **Pergunta factual ou pedido de visita na última mensagem** ("tem?", "quanto tá?", "aceita pet?",
   "ainda disponível?", "quero visitar o da rua X"):
   `no_question_needed` (responder primeiro) + essenciais que faltam + `visita` se há imóvel específico
   e interesse. Secundárias não entram.
2. **Primeiro contato sem informação** ("oi, boa tarde"; pergunta sobre a imobiliária): só `finalidade`
   entre as essenciais (é a pergunta de abertura) — mais `no_question_needed` se houve pergunta factual.
3. **Essencial faltando** (sem pergunta factual): todas as essenciais que faltam. `visita` junto se há
   imóvel específico com reação positiva. "me manda opções" com essencial faltando segue esta regra
   (não dá para mandar sem bairro/orçamento).
4. **Essenciais completas, sem imóvel específico**: todas as secundárias não respondidas +
   `no_question_needed` (o corretor pode mandar opções direto ou qualificar mais um ponto).
5. **Essenciais completas, imóvel específico com reação positiva, sem pergunta factual**: `visita`
   (+ `financiamento` se compra e não respondido). Reação negativa ao imóvel → regra 4, sem `visita`.
6. **Cliente pede para não perguntar mais / reclama de pergunta repetida** ou **tudo respondido**:
   só `no_question_needed`.

## Ambiguidade "até 600"
- Operação desconhecida + "até 600" → lido como R$ 600 mil de compra (uso corrente); `orcamento`
  proibida (o número foi dado), `finalidade` aceitável (compra × aluguel resolve a unidade).
- Compra conhecida + "até 600" → R$ 600 mil; `orcamento` proibida.
- Aluguel conhecido + "até 600" → unidade duvidosa (600/mês? 6 mil?); `orcamento` **aceitável** como
  confirmação — confirmar não é "perguntar tudo de novo". "até 6" em aluguel = R$ 6 mil, proibida.
- Prestação em compra ("consigo pagar 3 mil por mês") → `financiamento` respondida (vai financiar);
  `orcamento` aceitável (valor total/entrada em aberto).

## Famílias difíceis (contagem do validador do rotulador, 2026-10-01)
| Família (prefixo da `nota`) | ajuste | teste |
|---|---|---|
| valor ambíguo ("até 600", "até 6", prestação, valor corrigido) | 4 | 6 |
| já respondida de modo informal | 3 | 7 |
| correção tardia | 1 | 3 |
| campo conhecido contradito (com e sem valor novo) | 2 | 3 |
| nada faltando | 1 | 2 |
| cliente recusa repetição | 1 | 1 |
| sem sentido no contexto (pet de investidor) | 1 | 1 |
| visita já pedida ou recusada | 0 | 4 |
| anúncio específico / reação negativa ao imóvel | 0 | 2 |

Rascunho: 5 fáceis. Ajuste: 20 casos, 13 difíceis (65%). Teste: 40 casos, 29 difíceis (72%).
`proibidas` vazio: 0 no ajuste, 3 no teste. Só `no_question_needed` aceitável: 3 no ajuste, 5 no teste.

## Aviso ao construtor — baseline trivial
`no_question_needed` é aceitável em 9/20 casos do ajuste e 17/40 do teste (regras 1, 4 e 6). Quem
responde SEMPRE `no_question_needed` "acerta" 45% / 42% pelo critério "escolha ∈ aceitáveis" e nunca
cai em `proibidas`. Esse baseline tem de ser medido ao lado do Jev; a métrica que discrimina é o par
(acerto em aceitáveis, taxa de proibidas) — e, à parte, o acerto nos casos em que
`no_question_needed` NÃO é aceitável (11 no ajuste, 23 no teste). A primeira versão destes dados tinha
essa taxa em 60% / 78%; os casos foram reescritos (uma essencial retirada) para baixá-la.

O validador conferiu: envelope, campos e tipos, `de` ∈ cliente|agente, última mensagem do cliente,
catálogo idêntico em todos os casos, `aceitaveis` não vazio, IDs do catálogo, disjunção aceitáveis ×
proibidas, todo campo de `campos_conhecidos` em um dos dois conjuntos, ≥ 30% difíceis, nenhum texto
final repetido entre ajuste e teste, UTF-8 sem BOM, LF.
