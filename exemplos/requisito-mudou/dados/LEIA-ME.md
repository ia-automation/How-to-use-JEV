# Dados do `requisito-mudou` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item P) e [DADOS.md](../../DADOS.md).
Histórias sintéticas de WhatsApp entre cliente e corretor (compra e locação), pt-BR informal. Bairros reais;
nenhum nome, telefone, e-mail, endereço ou número de unidade. Gabarito = o que um corretor experiente anotaria no
cadastro depois de ler só os turnos novos.

Arquivos: `rascunho.json` (5 fáceis), `ajuste.json`, `teste.json` (abrir uma vez, no fim). Envelope
`{"versao", "autor": "fable", "casos"}`.

## Esquema (o do briefing, sem campo extra)
`{"id", "requisitos_anteriores": [{"id", "atributo", "valor"}], "conversa": [{"de", "texto"}], "shortlist":
[{"id", "resumo"}], "atualizacoes": {…}, "novo_valor": {…}, "reavaliar": […], "nota"}`
- `requisitos_anteriores`: 3–6 itens, IDs `q1`…, um por atributo (sem atributo repetido no caso). A ordem foi
  embaralhada: o requisito que muda não é sempre o `q1`.
- `conversa`: só os turnos NOVOS (3–5), em ordem; `de` ∈ `cliente | corretor`.
- `shortlist`: sempre 4 itens, `IM-01`…`IM-04`. **Todos atendem aos requisitos anteriores** (o validador confere):
  a shortlist era boa antes da conversa; a pergunta é quem deixa de servir depois.
- `atualizacoes`: uma chave para CADA requisito anterior, valor ∈ `mantido | substituido | negado | incerto`.
- `novo_valor`: uma chave para CADA requisito anterior; texto só em `substituido`, `null` nos outros três.
- `reavaliar`: IDs da shortlist, em ordem; pode ser `[]`.
- `nota`: começa com `"difícil: <família> — …"` nos casos difíceis; `"fácil: …"` nos demais.

## Formato canônico de `valor` e `novo_valor` (é o que o código lê)
| `atributo` | valores | o item atende quando |
|---|---|---|
| `orcamento` | `até R$ 650.000` (compra) · `até R$ 3.200/mês` (locação) | preço do item ≤ teto |
| `quartos` | `1`…`4` (mínimo) | quartos do item ≥ valor |
| `vagas` | `0`…`3` (mínimo; `0` = não precisa) | vagas do item ≥ valor |
| `bairro` | `Moema` · `Pompeia ou Lapa` · `A, B ou C` | bairro do item está na lista |
| `elevador` | `sim` · `indiferente` | `sim`: "com elevador", OU térreo, OU casa térrea (acesso sem escada) |
| `pet` | `sim` (o imóvel tem de aceitar) · `não` (não tem pet) | `sim`: "aceita pet" |
| `mobilia` | `mobiliado` · `sem mobília` · `indiferente` | igual ao valor; `indiferente` aceita os dois |
| `andar_baixo` | `sim` · `indiferente` | `sim`: térreo, 1º, 2º ou 3º andar, ou casa térrea |
| `financiamento` | `sim` (precisa financiar) · `não` (paga à vista) | `sim`: "aceita financiamento" |
| `prazo` | `mudança até MM/AAAA` | "pronto para morar" / "disponível imediato", ou mês de entrega ≤ mês do prazo |

Valores que **não restringem** nada: `indiferente`, `não`, `0`. Eles existem em `requisitos_anteriores` (o cliente
já tinha dito que não fazia questão) e **nunca** aparecem em `novo_valor`.

## Formato do `resumo` da shortlist (gerado por um molde só, para o código extrair)
`<Apartamento | Casa térrea> em <bairro>, <N quarto(s)>, <N vaga(s) | sem vaga>, R$ <preço>[/mês]. <térreo | Nº
andar>, <com | sem> elevador; <aceita pet | não aceita pet>; <mobiliado | sem mobília>; [<aceita financiamento | não
aceita financiamento>;] <pronto para morar | entrega em MM/AAAA | disponível imediato | disponível a partir de
MM/AAAA>.` — casa térrea não traz andar nem elevador; locação (preço com `/mês`) não traz financiamento.

## As quatro atualizações
Pergunta-chave, feita por requisito: **depois destes turnos, o cliente continua com a mesma restrição?**

| rótulo | quando | `novo_valor` |
|---|---|---|
| `mantido` | nada nos turnos novos toca o requisito, ou o cliente o reafirma, ou rejeita a mudança proposta | `null` |
| `substituido` | o cliente (quem decide) passa a ter OUTRA restrição neste atributo, com valor dito ou inescapável | o valor novo, no formato canônico |
| `negado` | o cliente deixa de querer/precisar: a restrição some e nada entra no lugar | `null` |
| `incerto` | hipótese, fala de terceiro não adotada, mudança sem valor, ou ambíguo | `null` |

### `substituido` × `negado` — o teste é "sobra restrição?"
- Sobra, com outro valor → `substituido` (`2` vagas → `1`; teto 700 → 850; `Pompeia` → `Pompeia ou Lapa`).
- Nasce uma restrição onde havia `indiferente` / `não` / `0` → `substituido` ("não fazia questão" → "agora preciso").
- Não sobra nenhuma → `negado` ("não preciso mais de vaga", "pode ser com ou sem mobília", "vou pagar à vista",
  "tanto faz o bairro"). Não se escreve `novo_valor: "indiferente"`.
- Preferência nova que **não cabe no atributo** ("agora quero andar alto"; "desde que tenha metrô") não vira valor:
  o requisito antigo cai (`negado`) e a nota registra o limite do esquema.
- Afrouxar também é `substituido` (teto sobe, vagas descem); só não tira ninguém da shortlist.

### Mudança indireta — quando é `substituido` e quando é `incerto`
Um fato da vida do cliente muda um requisito sem nomeá-lo. Tabela de ligação usada (fato → atributo):
morador com mobilidade reduzida → `elevador` · carro a mais/a menos → `vagas` · morador a mais/a menos, cômodo de
trabalho → `quartos` · animal → `pet` · renda, ajuda de parente → `orcamento` · data de trabalho/contrato → `prazo`
· ficar com/sem móveis → `mobilia`.
- **Consequência dita ou inescapável** → `substituido`: "minha mãe não sobe escada e vai morar comigo" → `elevador:
  sim`; "adotamos um cachorro" → `pet: sim`; "dois carros e na rua não dá" → `vagas: 2`. O número pode ser dito
  pelo corretor e **confirmado** pelo cliente ("3 no total?" — "isso mesmo").
- **Consequência que depende de uma escolha não declarada** → `incerto` só no atributo ligado: "tô grávida" (sem
  dizer se quer mais um quarto); "fiquei sem móvel nenhum" (mobiliado ou comprar de novo?).
- O fato não contamina os outros atributos: mãe que vem morar e "fica no segundo quarto" → `quartos` mantido.
- Quando o fato que criou o requisito some ("minha mãe não vem mais") e o cliente confirma → `negado`.

### `incerto` × `mantido`
- Hipótese sobre o futuro ("se eu for promovida subo pra 800", "talvez a gente tenha filho") → `incerto`, mesmo com
  valor dito. Vira `mantido` só quando o cliente **reafirma o valor antigo ou rejeita a mudança** ("meu limite é
  esse mesmo", "segue como tá", "2.800 é o teto"). "Vamos ver", "por enquanto não sei", "depois te falo" deixam em
  aberto → `incerto`.
- Fala de terceiro (cônjuge, pais, sogra, filho): relatada sem decisão → `incerto`; **adotada** pelo cliente ("então
  fechou, 2 vagas") → `substituido`; **rejeitada** ("quem vai morar somos nós, 2 tá ótimo") → `mantido`.
- Dinheiro de outra pessoa: valor que pertence a OUTRO negócio (o irmão pagou 1,1 milhão; a amiga tem 400 mil) →
  `mantido`. Ajuda de parente confirmada e convertida em teto pelo cliente → `substituido`; "talvez ajude" → `incerto`.
- Mudança sem valor ("dá pra esticar um pouco", "meu prazo apertou") → `incerto`: sem valor não há substituição.
- Sugestão do corretor: aceita → `substituido`; recusada ou ignorada → `mantido`; "deixa eu ver" → `incerto`. Número
  dito só pelo corretor ("com 3 quartos sobe para 680") não é valor do cliente.
- Pergunta do cliente sobre um atributo ("o segundo tem elevador?") não cria nem muda requisito → `mantido`.
- Ironia evidente ("com meu salário de milionário subo pra 2 milhões kkk") → `mantido`.

### Correção e ordem
- Vale a **última** fala do cliente sobre o requisito. Subiu o teto e voltou atrás → `mantido`. Três valores em
  sequência → o último. Asterisco corrige a mensagem anterior ("3 vagas" → "*2 vagas").
- Correção que restaura o registrado (o corretor recapitula errado, o cliente conserta) → `mantido`.
- "Nunca pedi isso, pra mim tanto faz" (o cadastro estava errado) → `negado`.
- Exceção condicionada que o próprio cliente separa do limite ("meu limite é 600; 650 só se for excepcional") →
  `mantido` em 600.

## Regra do `reavaliar` (conta do CÓDIGO, não do Jev)
1. Requisitos vigentes = `mantido` e `incerto` com o valor ANTIGO · `substituido` com o `novo_valor` · `negado` fora.
   (`incerto` não mexe na shortlist: é sinal para o corretor perguntar, não para descartar imóvel.)
2. `reavaliar` = itens da shortlist que falham em pelo menos um requisito vigente, pela tabela "o item atende
   quando" acima, lendo os atributos do `resumo`. Ordem dos IDs preservada.
3. Como todos os itens atendiam antes, só `substituido` que APERTA tira alguém; afrouxar, negar e duvidar dão `[]`.
4. Granularidade: prazo e entrega em mês/ano; térreo e casa térrea contam como "sem escada" para `elevador: sim`.
Os rótulos de `atualizacoes` são julgamento; `reavaliar` foi calculado pelo gerador e recalculado pelo validador a
partir do TEXTO do `resumo` e dos valores (duas implementações), com zero divergência.

## Famílias de caso difícil (`nota` começa com "difícil:")
| Família (prefixo da `nota`) | ajuste | teste |
|---|---|---|
| mudança indireta | 3 | 6 |
| correção explícita | 2 | 5 |
| duas mudanças | 1 | 6 |
| mudança sem valor | 1 | 4 |
| nada mudou | 3 | 2 |
| preferência de terceiro | 2 | 3 |
| "não faço questão" → "agora preciso" | 1 | 3 |
| hipótese sobre o futuro | 2 | 2 |
| negado × substituído | 2 | 2 |
| sugestão do corretor | 1 | 3 |
| orçamento de outra pessoa | 1 | 2 |
| ambíguo | 0 | 2 |
| ironia | 0 | 1 |

## Contagens (validador do rotulador, 2026-10-01, zero erros)
| arquivo | histórias | difíceis | requisitos | `mantido` | `substituido` | `negado` | `incerto` | tudo `mantido` | `reavaliar` vazio | locação |
|---|---|---|---|---|---|---|---|---|---|---|
| `rascunho.json` | 5 | 0 (0%) | 19 | 15 | 3 | 1 | 0 | 1 (20%) | 2 | 2 |
| `ajuste.json` | 22 | 19 (86%) | 95 | 77 | 10 | 3 | 5 | 5 (23%) | 16 | 7 |
| `teste.json` | 44 | 41 (93%) | 181 | 141 | 22 | 6 | 12 | 10 (23%) | 29 | 16 |

"tudo `mantido`" = histórias em que nenhum requisito muda (meta do briefing: ~20%). "locação" = histórias de aluguel
(orçamento com `/mês`); as demais são de compra.

## Aviso ao construtor — baseline trivial
Quem responde sempre `mantido` acerta a maioria dos REQUISITOS (a coluna `mantido` acima, sobre o total de
requisitos), porque cada história muda um ou dois de 3–6. A métrica que discrimina é por requisito **mudado**
(acerto em `substituido`/`negado`/`incerto`) e, por história, "detectou que algo mudou?" e `reavaliar` exato.

## Ambiguidades decididas pelo rotulador (não estavam no briefing)
- `de` ∈ `cliente | corretor`; shortlist sempre com 4 itens que atendiam antes.
- `novo_valor` tem chave para todo requisito (`null` fora de `substituido`).
- `incerto` conserva o valor antigo no cálculo de `reavaliar`.
- Afrouxar é `substituido`; deixar de restringir é `negado`; `indiferente`/`não`/`0` nunca são `novo_valor`.
- Requisito NOVO em atributo que não estava na lista não é representável: toda mudança dos casos cai num atributo
  já listado (às vezes como `indiferente`, `não` ou `0`).
- `elevador: sim` é lido como "acesso sem escada": térreo e casa térrea atendem.
- `andar_baixo: sim` = até o 3º andar.
- Fato indireto sem consequência declarada marca `incerto` só o atributo ligado pela tabela, não os demais.
