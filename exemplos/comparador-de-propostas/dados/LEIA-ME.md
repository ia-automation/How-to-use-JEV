# Dados do `comparador-de-propostas` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item T) e [DADOS.md](../../DADOS.md).
Disputas sintéticas: uma imobiliária (sede na capital) pede cotação de um serviço ou produto a três fornecedores e
compara as propostas contra uma lista de requisitos. Serviços variados (ar-condicionado, CRM, fachada, CFTV,
telefonia, contabilidade, mobiliário, energia solar, portaria remota, e-mail marketing, impressoras, pintura,
drone, seguro, treinamento, elevadores, buffet, LGPD, gerador, café, mudança, chatbot, piso, uniformes, paisagismo,
motoboy, letreiro, internet, auditoria, notebooks). Fornecedores sem nome; nenhum dado pessoal; valores em
reais plausíveis. Gabarito = o que um comprador atento marcaria lendo só o texto da proposta.

Arquivos: `rascunho.json` (5 fáceis), `ajuste.json` (10), `teste.json` (20, abrir uma vez, no fim). Envelope
`{"versao", "autor": "fable", "casos"}`.

## Esquema (o do briefing, sem campo extra)
- Caso: `{"id", "requisitos", "propostas", "matriz", "trechos", "elegiveis", "nota"}`.
- `requisitos[]`: `{"id": "r1"…, "texto", "obrigatorio": bool, "tipo": "semantico" | "numerico"}`, 3–4 por disputa.
- `propostas[]`: sempre 3, `{"id": "p1" | "p2" | "p3", "texto", "campos"}`. `texto` = trecho da proposta em voz de
  fornecedor, 2–5 frases. `campos` traz UMA chave por requisito numérico da disputa (`preco_total`, `prazo_dias`,
  `garantia_meses`, `suporte_meses`, `franquia`, `horas`, `kva`, `mbps`, `contrato_meses`), valor inteiro ou
  `null` quando a proposta não declara.
- `matriz[p][r]` ∈ `atende | contradiz | nao_informado`; `trechos[p][r]` = substring **literal** do `texto` da
  proposta que decide a célula, ou `null` quando `nao_informado`.
- `elegiveis`: IDs das propostas sem `contradiz` em requisito obrigatório, na ordem `p1, p2, p3`; pode ser `[]`.
- `nota`: `"difícil: <família> — …"` ou `"fácil: …"`.

## Requisito numérico — formato que o código lê
O `texto` termina com `(\`campo\` <= N)` ou `(\`campo\` >= N)`, por exemplo
`Preço total de até R$ 30.000 (\`preco_total\` <= 30000)`. A célula é calculada pelo código a partir de
`campos`: valor que satisfaz → `atende`; que viola → `contradiz`; `null` → `nao_informado`. O validador recalcula
e exige igualdade com a `matriz`. O `trecho` da célula numérica é o fragmento com o número ("R$ 28.900,00",
"75 dias corridos").
- Os `campos` já vêm **normalizados** (a extração do número não é o que este exemplo mede): dias úteis viram
  corridos (5 úteis = 7; 20 úteis = 28), semanas viram dias, anos viram meses, "24 horas" vira `prazo_dias` 1.
- Duas garantias ("12 meses para o LED e 36 para a estrutura") → vale a **menor**. Franquia "10% com mínimo de
  R$ 3.000" → vale o mínimo.
- Preço numérico é o valor base declarado; adicionais e opcionais não entram no campo (aparecem na célula
  semântica que eles afetam).

## As três células — regras semânticas
| célula | quando |
|---|---|
| `atende` | a proposta afirma, sem condição, que entrega o que o requisito pede (sinônimo vale: "sem custo adicional" = incluso; "ilimitados" cobre "até 50 mil"; "2 anos" = 24 meses) |
| `contradiz` | a proposta diz que NÃO entrega, entrega outra coisa, cobra à parte, ou só entrega mediante adicional/opcional/acréscimo sobre o preço cotado |
| `nao_informado` | a proposta não toca no ponto, usa termo vago que não decide ("suporte incluso" sem duração, "piloto habilitado" sem ANAC), remete a anexo que não veio, ou condiciona a algo que o pedido não define |

Precedência dentro da mesma proposta: **a frase de exclusão vence a frase de inclusão** ("instalação inclusa… os
valores não contemplam infraestrutura" → `contradiz`, trecho = a exclusão). "Peças inclusas, exceto X" é
`contradiz` para "peças inclusas".

### Promessa condicionada
- Condição que o pedido **não satisfaz** ou que custa a mais ("fim de semana com acréscimo de 20%", "QTA
  opcional", "monitoramento 24h mediante adicional") → `contradiz`: o preço cotado não cobre o requisito.
- Condição que depende de **escolha do comprador fora do pedido** ("treinamento incluso no plano anual" quando o
  pedido é o plano mensal; "gravação no plano Pro" quando o preço é do Básico) → `nao_informado` (vira pergunta).
- Condição que o pedido **já satisfaz** ("montagem inclusa na capital", e a sede é na capital) → `atende`.
- "Registro em processo de renovação" não é registro vigente → `nao_informado`.

### Elegibilidade
`elegiveis` = sem `contradiz` em obrigatório. `nao_informado` em obrigatório **mantém** a proposta elegível, com
pergunta ao fornecedor (o exemplo mede se o sistema faz a pergunta certa, não se adivinha). Requisito opcional
nunca derruba. Disputa sem elegível existe (CP-T06).

## Famílias de caso difícil (prefixo da `nota`)
| família | ajuste | teste | mecanismo |
|---|---|---|---|
| exclusão escondida | 1 | 5 | "incluso" no começo, exclusão na última frase ou na observação |
| promessa condicionada | 1 | 2 | só no plano anual / só com acréscimo / em renovação |
| termo vago | 3 | 8 | "suporte incluso", "manutenção inclusa", "cadeiras ergonômicas", "atendimento prioritário" → pergunta |
| anexo citado mas ausente | 1 | 2 | "conforme memorial anexo", "cronograma a ser enviado" |
| atende tudo menos o prazo | 2 | 1 | a melhor proposta cai só no numérico obrigatório |
| fácil | 2 | 2 | tudo declarado com todas as letras |

Uma disputa difícil costuma combinar duas famílias; o prefixo é a principal, a `nota` cita a segunda.

## Contagens (validador do rotulador, 2026-10-01, zero erros)
| arquivo | disputas | propostas | difíceis | elegíveis por disputa |
|---|---|---|---|---|
| `rascunho.json` | 5 | 15 | 0 | 1 · 2 · 1 · 1 · 2 |
| `ajuste.json` | 10 | 30 | 8 (80%) | 2 · 2 · 1 · 1 · 2 · 1 · 1 · 1 · 1 · 2 |
| `teste.json` | 20 | 60 | 18 (90%) | 1 · 1 · 2 · 1 · 2 · 0 · 1 · 2 · 1 · 1 · 1 · 2 · 1 · 1 · 2 · 2 · 1 · 2 · 2 · 2 |

Toda disputa tem ao menos uma célula `nao_informado` ou um `contradiz` fora do óbvio no ajuste e no teste; o
rascunho não tem `nao_informado` em obrigatório.

## Aviso ao construtor
- Células numéricas são do código (pelos `campos`); o Jev só julga as semânticas. Medir as duas à parte.
- Erros caros, contados à parte: (1) `atende` numa exclusão escondida (comprar a proposta errada); (2) `contradiz`
  onde é `nao_informado` (descartar fornecedor sem perguntar); (3) proposta elegível fora da lista.
- O `trecho` serve para medir se o sistema aponta a evidência certa (substring literal); comparar por contenção,
  não por igualdade exata.
- Baseline natural: palavra-chave do requisito presente no texto → `atende`. Ele erra exatamente nas famílias
  acima.

## Ambiguidades decididas pelo rotulador (não estavam no briefing)
- O pedido é sempre da sede na capital, plano mensal quando há planos, serviço único quando há "anual × avulso".
- "Incluso" seguido de exclusão parcial é `contradiz`, não `nao_informado`.
- Adicional/opcional/acréscimo = `contradiz`; plano superior não cotado = `nao_informado`.
- Garantia dupla → menor valor; franquia com mínimo → o mínimo; dias úteis → corridos ×7/5.
- `trechos` de célula numérica = fragmento com o número; de `nao_informado` = `null` sempre.

## v2 (2026-10-02) — células numéricas que estavam como `semantico` (revisão adversarial, achado 1)
Aplicado pelo construtor com autorização do coordenador (o rotulador não estava disponível). O Jev estava comparando
número em quatro requisitos (4.000 × 5.000 páginas, 48 × 4 horas, 25.000 × 50.000 contatos) — trabalho do código.
`versao` dos dois arquivos subiu para `2026-10-02`; `rascunho.json` não mudou. A matriz NÃO mudou em nenhuma célula
(o validador recalcula as numéricas e exige igualdade; conferido). Os `trechos` já eram o fragmento com o número.

| arquivo | disputa | requisito | campo novo | valores p1 · p2 · p3 |
|---|---|---|---|---|
| `ajuste.json` | CP-A10 | r2 "Até 50 mil contatos no plano" | `contatos` >= 50000 | 50000 · 25000 · 999999999 |
| `teste.json` | CP-T01 | r3 "Franquia mínima de 5 mil páginas por mês" | `paginas_mes` >= 5000 | 6000 · 5000 · 4000 |
| `teste.json` | CP-T18 | r2 "SLA de reparo de até 4 horas" | `sla_horas` <= 4 | 4 · 48 · `null` ("atendimento prioritário") |
| `teste.json` | CP-T20 | r2 "Substituição em até 24 horas em caso de defeito" | `troca_horas` <= 24 | 24 · 48 · `null` ("substituição rápida") |

- Convenção nova: **"ilimitados" (sem teto declarado) → `999999999`** — sentinela maior que qualquer limite deste
  conjunto; o esquema só aceita inteiro ou `null`, e `null` significaria "não declara", que não é o caso.
- Ficaram `semantico`, de propósito, os requisitos COMPOSTOS em que o número é só uma das partes (CP-A04 r1 "nuvem
  por 30 dias", CP-T06 r2 "emergência 24h com chegada em até 2 horas", CP-T15 r2 "quinzenal por 6 meses", CP-T16 r1
  "até 3 horas" × "mesmo dia", CP-T05/T07 capacidade de pessoas): a parte semântica decide tanto quanto o número.
- `valida.py` ainda exige `versao == "2026-10-01"` (constante do rotulador, não editada): acusa 2 erros de envelope
  até o rotulador atualizar a constante; o restante do validador passa.
