# Dados do `motivo-de-perda` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item Q) e [DADOS.md](../../DADOS.md).
Conversas sintéticas de WhatsApp de venda e locação imobiliária que terminaram SEM negócio, pt-BR informal. Bairros
reais; nenhum nome, telefone, e-mail, documento, endereço ou unidade (imóvel citado por bairro ou código de
anúncio inventado). Gabarito = o que um gestor comercial experiente registraria como motivo da perda lendo só a
conversa.

Arquivos: `taxonomia.json`, `rascunho.json` (5 fáceis), `ajuste.json`, `teste.json` (abrir uma vez, no fim).
Envelope `{"versao", "autor": "fable", "casos"}` nos quatro. A ordem dos casos foi embaralhada.

## Esquema (o do briefing, sem campo extra)
- `taxonomia.json` → `casos` = lista de GRUPOS: `{"id", "nome", "descricao", "folhas": [{"id", "nome", "descricao"}]}`.
  8 grupos, 30 folhas; IDs de folha únicos na árvore inteira.
- Caso: `{"id", "conversa": [{"de", "texto"}], "folha", "grupo", "aceitaveis": [ids de folha], "nota"}`.
  - `conversa`: 4–12 turnos; `de` ∈ `cliente | corretor`.
  - `folha`: ID de folha, ou `null` quando só o grupo é decidível.
  - `grupo`: SEMPRE preenchido. Com `folha` não nula, é o pai dela. O grupo `sem_informacao` nunca vem com `folha`
    nula (as três folhas dele cobrem tudo).
  - `aceitaveis`: com `folha` não nula, começa por ela e pode trazer outras folhas (de qualquer grupo) que o gestor
    também aceitaria. Com `folha` nula, é `[]` ou a lista das folhas DO GRUPO entre as quais a conversa não decide.
  - `nota`: começa com `"difícil: <família> — …"` nos casos difíceis; `"fácil: …"` nos demais.

## Taxonomia
**`preco` — Preço e condições financeiras.** O negócio não fechou por causa de valor, custo ou forma de pagamento do imóvel oferecido.
- `preco_acima_orcamento` — O valor pedido (venda ou aluguel) está acima do que o cliente pode ou aceita pagar.
- `custos_extras` — O preço em si servia; pesaram os custos em volta: condomínio, IPTU, taxas da imobiliária, ITBI, escritura, registro.
- `negociacao_frustrada` — O cliente fez proposta ou pediu desconto e o proprietário recusou; não houve acordo de valor.
- `condicao_pagamento` — O valor servia, a forma não: entrada exigida, parcelamento direto, permuta, uso de FGTS ou financiamento recusados pelo vendedor.

**`credito_documentacao` — Crédito e documentação.** O cliente queria fechar, mas crédito, garantia, cadastro ou documentos impediram.
- `financiamento_negado` — O banco não aprovou o crédito do cliente ou aprovou valor menor que o necessário.
- `garantia_locaticia` — Locação: sem fiador aceito, seguro-fiança reprovado ou caro demais, caução ou título inviável.
- `restricao_cadastral` — A análise cadastral reprovou o cliente: nome negativado, renda não comprovada ou insuficiente para a locação.
- `documentacao_imovel` — Problema do lado do imóvel: matrícula irregular, inventário, penhora, dívida, área não averbada, falta de habite-se.

**`imovel` — Características do imóvel.** O imóvel visitado ou oferecido não agradou pelo que ele é.
- `tamanho_planta` — Pequeno, poucos cômodos, cômodos apertados ou mal distribuídos.
- `estado_conservacao` — Precisa de reforma: infiltração, mofo, instalações antigas, prédio malcuidado.
- `falta_item` — Falta algo de que o cliente não abre mão: vaga, elevador ou acesso sem escada, aceitar pet, varanda, quintal, mobília.
- `diferente_do_anuncio` — O imóvel visitado não corresponde às fotos ou à descrição do anúncio (metragem, vagas, estado, vista).

**`localizacao` — Localização.** O imóvel até servia; o lugar não.
- `distancia_deslocamento` — Longe do trabalho, da escola, da família ou do transporte; tempo de trajeto inviável.
- `entorno_seguranca` — Rua ou vizinhança: barulho, insegurança, alagamento, bar ou obra ao lado.
- `bairro_nao_desejado` — O cliente só aceita um bairro ou cidade e a imobiliária não tem imóvel lá que sirva.

**`concorrencia` — Fechou em outro lugar.** O cliente comprou ou alugou outro imóvel, ou o mesmo por outro caminho.
- `outra_imobiliaria` — Fechou por outra imobiliária ou por outro corretor.
- `direto_proprietario` — Fechou direto com um proprietário, sem imobiliária (o mesmo imóvel ou outro).
- `lancamento_construtora` — Comprou na planta ou em lançamento, direto com construtora ou incorporadora.

**`atendimento` — Atendimento e processo.** A perda nasceu do lado da imobiliária: demora, falha de visita, informação errada, imóvel que saiu, pressão.
- `demora_resposta` — O atendimento demorou a responder ou a dar um retorno prometido, e o cliente desistiu ou foi atendido antes por outro.
- `visita_falhou` — Visita desmarcada, corretor atrasado ou ausente, chave indisponível, ou nenhum horário compatível.
- `informacao_errada` — O atendimento passou informação errada ou desatualizada (valor, disponibilidade, característica, regra do condomínio).
- `imovel_indisponivel` — O imóvel foi vendido, alugado ou retirado pelo dono antes de o cliente fechar, e nenhuma alternativa foi aceita.
- `pressao_insistencia` — O cliente se incomodou com insistência, pressão para fechar ou com a postura do corretor.

**`momento_cliente` — Momento do cliente.** Nada contra o imóvel nem contra o atendimento: o plano do cliente mudou ou parou.
- `adiou_decisao` — Decidiu esperar por um motivo de momento declarado: juros, vender o imóvel atual antes, um evento, o ano que vem.
- `mudanca_de_vida` — Um fato da vida tirou o sentido do negócio: transferência, separação, desemprego, doença.
- `desistiu_de_mudar` — Resolveu ficar onde está: renovou o aluguel, vai reformar o imóvel atual, desistiu de vender.
- `decisor_vetou` — Cônjuge, pais ou sócio não aprovaram, sem motivo declarado sobre o imóvel.

**`sem_informacao` — Sem informação.** A conversa não diz por que o negócio não saiu.
- `sumiu_sem_resposta` — O cliente parou de responder, sem reação que indique motivo.
- `sumiu_apos_valor` — O cliente parou de responder logo depois de receber preço ou condições, sem comentar.
- `adiou_sem_motivo` — "Vou pensar", "qualquer coisa te chamo": adiamento educado sem motivo declarado nem pista na conversa.

### Fronteiras entre folhas vizinhas
- `preco_acima_orcamento` × `custos_extras`: o cliente diz que o preço/aluguel serve e reclama do que vem em volta
  (condomínio, IPTU, ITBI, taxa de contrato) → `custos_extras`. "O total não fecha", sem separar → grupo `preco`,
  `folha: null`.
- `negociacao_frustrada` exige proposta ou pedido de desconto RECUSADO na conversa; `preco_acima_orcamento` fica
  aceitável quando o cliente também diz que o valor passa do limite.
- `financiamento_negado` (banco × cliente) × `documentacao_imovel` (o banco devolve por causa da matrícula) ×
  `condicao_pagamento` (o VENDEDOR recusa financiamento, FGTS ou permuta).
- `restricao_cadastral` (o cliente não passa na análise) × `garantia_locaticia` (o cadastro passa; trava o tipo de
  garantia). Reprovação sem detalhe → grupo `credito_documentacao`, `folha: null`.
- `diferente_do_anuncio` (o ANÚNCIO não corresponde) × `informacao_errada` (o ATENDIMENTO afirmou algo errado na
  conversa ou ofereceu imóvel já indisponível).
- `imovel_indisponivel`: o imóvel saiu DEPOIS de oferecido. Se já estava alugado quando foi oferecido, a folha é
  `informacao_errada` (e `imovel_indisponivel` fica aceitável).
- `adiou_decisao` pede motivo de momento declarado (juros, vender antes, evento). Sem motivo → `adiou_sem_motivo`.
- `decisor_vetou` só quando o veto vem SEM motivo sobre o imóvel. Veto com motivo ("ela vetou por causa da
  escada") → a folha do motivo.
- `sumiu_apos_valor`: a última coisa antes do silêncio foi o cliente receber preço ou condições. Silêncio em
  qualquer outro ponto (depois das fotos, da visita, do pedido de documentos) → `sumiu_sem_resposta`.

## Como se escolhe a folha principal (precedência, em ordem)
1. **Motivo confessado vence motivo declarado.** Se o cliente dá uma desculpa e depois diz o motivo de verdade
   ("na real o banco só aprovou 310"), vale o confessado; a desculpa NÃO entra em `aceitaveis`.
2. **O que o cliente ordena.** "O preço eu engolia; o que pegou foi a distância" → distância, e só ela.
3. **Fechou em outro lugar.** Se o cliente diz POR QUE não fechou conosco, com queixa sobre a nossa oferta ou o
   nosso atendimento ("vocês demoraram três dias", "lá não cobram a taxa de contrato"), a folha é o porquê e a folha
   de `concorrencia` fica aceitável. Se o porquê é só uma vantagem do concorrente ("a construtora parcela a entrada")
   ou não existe, a folha é a de `concorrencia` (a folha da vantagem pode ficar aceitável). Sem dizer com quem →
   grupo `concorrencia`, `folha: null`.
4. **Evento que encerra vence queixa lateral.** Imóvel vendido a outro, crédito negado, garantia recusada, visita
   furada pela segunda vez: é isso que o gestor registra, mesmo que apareça outra reclamação no caminho.
5. **Causa vence consequência.** Separação que torna o imóvel grande e caro → `mudanca_de_vida`. Parcela alta por
   causa do juro, com decisão de esperar o juro cair → `adiou_decisao`.
6. **Educação com pista.** "Vou pensar" depois de uma reação ao preço ("bem acima do que eu imaginava") → a folha
   da pista. "Vou pensar" sem pista nenhuma → `adiou_sem_motivo`. Não se inventa motivo.
7. **Silêncio.** Reação fraca seguida de silêncio ("eita 😳") → a folha da reação, com `sumiu_apos_valor`
   aceitável. Silêncio sem reação → `sumiu_*`, e preço NÃO é aceitável.
8. **Empate sem ordem.** Dois motivos sem que o cliente ordene: principal = o da última palavra do cliente
   ("prefiro espaço"); o outro entra em `aceitaveis`.

`aceitaveis` não é "tudo o que foi mencionado": entra só a folha que também é verdade sobre a perda e que o gestor
aceitaria ver no relatório. Motivo desmentido, contornado pelo próprio cliente ("isso eu engolia") ou que só aparece
na alternativa oferecida pelo corretor fica de fora.

## Famílias de caso difícil (`nota` começa com "difícil:")
| Família (prefixo da `nota`) | ajuste | teste |
|---|---|---|
| fronteira entre folhas | 4 | 7 |
| motivo do corretor | 4 | 6 |
| só o grupo é decidível | 2 | 7 |
| fechou em outro lugar | 2 | 5 |
| dois motivos | 2 | 4 |
| motivo dito com educação | 2 | 3 |
| motivo real diferente do declarado | 1 | 3 |
| sumiço depois de preço | 1 | 3 |
| sumiço sem pista | 0 | 2 |
| decisor com motivo | 0 | 1 |

## Contagens (validador do rotulador, 2026-10-01, zero erros)
| arquivo | conversas | difíceis | `folha: null` | mais de uma aceitável | `preco` | `credito_documentacao` | `imovel` | `localizacao` | `concorrencia` | `atendimento` | `momento_cliente` | `sem_informacao` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `rascunho.json` | 5 | 0 (0%) | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 1 |
| `ajuste.json` | 34 | 18 (53%) | 2 | 5 | 5 | 4 | 5 | 3 | 4 | 6 | 4 | 3 |
| `teste.json` | 68 | 41 (60%) | 7 | 13 | 9 | 9 | 10 | 7 | 7 | 11 | 7 | 8 |

Folha por arquivo (ajuste / teste), como `folha` principal:
| folha | ajuste | teste |
|---|---|---|
| `preco_acima_orcamento` | 2 | 3 |
| `custos_extras` | 1 | 3 |
| `negociacao_frustrada` | 1 | 1 |
| `condicao_pagamento` | 1 | 1 |
| `financiamento_negado` | 1 | 2 |
| `garantia_locaticia` | 1 | 2 |
| `restricao_cadastral` | 1 | 2 |
| `documentacao_imovel` | 1 | 2 |
| `tamanho_planta` | 1 | 3 |
| `estado_conservacao` | 1 | 2 |
| `falta_item` | 1 | 3 |
| `diferente_do_anuncio` | 1 | 1 |
| `distancia_deslocamento` | 1 | 3 |
| `entorno_seguranca` | 1 | 2 |
| `bairro_nao_desejado` | 1 | 1 |
| `outra_imobiliaria` | 1 | 2 |
| `direto_proprietario` | 1 | 2 |
| `lancamento_construtora` | 1 | 1 |
| `demora_resposta` | 1 | 3 |
| `visita_falhou` | 2 | 2 |
| `informacao_errada` | 1 | 2 |
| `imovel_indisponivel` | 1 | 2 |
| `pressao_insistencia` | 1 | 1 |
| `adiou_decisao` | 1 | 2 |
| `mudanca_de_vida` | 1 | 2 |
| `desistiu_de_mudar` | 1 | 2 |
| `decisor_vetou` | 1 | 1 |
| `sumiu_sem_resposta` | 1 | 3 |
| `sumiu_apos_valor` | 1 | 2 |
| `adiou_sem_motivo` | 1 | 3 |

Todas as 30 folhas aparecem como principal ao menos uma vez no teste.

## Aviso ao construtor
- A folha mais frequente é pequena (`preco_acima_orcamento`, 3 de 68 no teste): não há baseline trivial de classe majoritária; o baseline de
  código natural é palavra-chave por folha.
- Métricas sugeridas: acerto exato em `folha` (casos com folha), acerto em `aceitaveis`, acerto em `grupo` (todos
  os casos) e, nos casos de `folha: null`, "o sistema se absteve de dar folha?".
- Erro caro: dar folha de motivo (preço, imóvel…) a um caso de `sem_informacao` — é inventar motivo no relatório.

## Ambiguidades decididas pelo rotulador (não estavam no briefing)
- `sem_informacao` é um GRUPO com três folhas (silêncio, silêncio depois do valor, adiamento educado), não uma
  folha solta; "o cliente simplesmente sumiu" é `sumiu_sem_resposta`.
- `folha: null` com `aceitaveis` não vazio = empate entre folhas do MESMO grupo; vazio = nenhuma folha indicada.
- "Fechou em outro lugar com porquê": o porquê só vira folha quando é queixa sobre nós (regra 3).
- Sumiço depois do valor sem reação NÃO é preço; com reação fraca é preço, com o sumiço aceitável.
- Veto de terceiro com motivo vai para a folha do motivo.
- `visita_falhou` cobre também "nenhum horário compatível", mesmo sem falta do corretor.
- `de` ∈ `cliente | corretor`; o sumiço é representado por mensagens finais do corretor sem resposta.
