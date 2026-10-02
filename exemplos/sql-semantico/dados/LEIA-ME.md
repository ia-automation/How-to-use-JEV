# Dados do `sql-semantico` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item R) e [DADOS.md](../../DADOS.md).
Tabela sintética de **observações de atendimento** de uma imobiliária (a nota que o corretor escreve depois de
falar com o lead), pt-BR informal, 1–3 frases. Nenhum nome, telefone, e-mail, documento ou endereço; bairros e
cidades reais, bancos citados pelo nome como no cotidiano. Gabarito = o que um gestor lendo a observação
responderia à pergunta "esta linha satisfaz a condição?".

Arquivos: `linhas.json` (a tabela, compartilhada), `rascunho.json` (5 condições fáceis), `condicoes_ajuste.json`,
`condicoes_teste.json` (abrir uma vez, no fim). Envelope `{"versao", "autor": "fable", "casos"}`; em
`linhas.json` a chave é `"linhas"`. A separação é entre **condições**, não entre linhas: o teste mede condições
novas sobre a mesma tabela.

## Esquema (o do briefing, sem campo extra)
- Linha: `{"id", "texto", "campos"}` com `campos` sempre os seis: `data` (`AAAA-MM-DD`, jul–set/2026),
  `canal` ∈ `whatsapp | telefone | email | presencial`, `finalidade` ∈ `compra | locacao`, `orcamento` (inteiro em
  reais; mensal na locação; `null` quando não registrado), `visitas` (inteiro ≥ 0), `etapa` ∈
  `novo | em_contato | visita | proposta | perdido`.
- Condição: `{"id", "condicao", "linhas_verdadeiras", "linhas_indecidiveis", "nota"}`. Linha fora das duas listas
  vale **falso**. `nota` começa com `"difícil: <tipo> — …"` (tipo ∈ `negação | composta | inferência fraca`) ou `"fácil"`.

## Como o gabarito foi construído
Cada linha foi escrita com **fatos de autoria** (17 fatos semânticos: mudança de cidade, reforma recente,
urgência, financiamento, pet, filhos, home office, reclamação, elogio, concorrente, acessibilidade, investidor,
desistência, achou caro, barulho, decisor terceiro, perto do trabalho), cada um em um de três estados:
**afirmado**, **negado explicitamente** ou **pista fraca**. As frases variam de propósito (sinônimo, gíria,
paráfrase, negação com a mesma palavra-chave) para que `LIKE` não resolva. O rótulo de cada condição foi
calculado sobre esses fatos mais os `campos`, antes de qualquer resposta do Jev; não é anotação humana
independente de texto real. Como no `busca-imoveis`, placar bom valida o mecanismo, não a qualidade em dados reais.

## Convenções (o que conta e o que não conta)
1. **A condição é sobre o que a observação DIZ.** Silêncio = falso. "Clientes com pet" só é verdadeira onde a
   observação afirma o animal; "não informa" não é "não tem".
2. **Negação explícita** ("não tem pet", "não vai financiar", "largou o home office", "anúncio dizia reformado mas
   é piso de 30 anos") é **falsa** para a condição afirmativa e **verdadeira** para a condição negativa
   correspondente ("declararam NÃO ter animal", "descartaram financiamento"). Para a condição negativa, silêncio
   também é falso.
3. **Pista fraca → indecidível.** "Perguntou se o prédio tem elevador" (sem motivo), "quer um quarto sobrando" (sem
   dizer pra quê), "filha vai prestar vestibular em outra cidade": um gestor não afirmaria nem negaria. Entram em
   `linhas_indecidiveis`. Não se completa preferência.
4. **Parte numérica/categórica é do código** e vem entre crases na condição: `` `orcamento` <= 500000 ``,
   `` `visitas` >= 2 ``, `` `canal` = whatsapp ``, `` `finalidade` = locacao ``, `` `data` em 2026-09 ``.
   Linha que falha a parte de campo é **falsa** mesmo que o fato semântico seja fraco (o filtro de código vem
   antes; não entra nos indecidíveis). `orcamento` nulo falha qualquer comparação de orçamento.
5. **Composta E:** verdadeira só com os dois fatos afirmados; um afirmado e o outro fraco → indecidível; qualquer
   um negado ou ausente → falso. **Composta OU:** verdadeira com um lado afirmado; nenhum afirmado e algum fraco
   → indecidível.
6. **"Acharam caro mas seguem procurando" (SQ-T12):** exige caro afirmado E continuação explícita ("segue na
   busca", "pediu outras opções"); caro + desistiu → falso; caro sem dizer se continua → indecidível (é a condição
   com mais indecidíveis, de propósito).
7. **Elogio × reclamação:** as duas falam de "atendimento"; elogio só conta quando o cliente avalia o nosso
   atendimento positivamente — "prefere nosso portfólio" não é elogio ao atendimento (falso), "perguntou por que
   demorou" não é reclamação (fraco).
8. **Investidor:** compra para renda ou revenda. "Quanto renderia, só pra saber, vai morar" é falso; "pro filho
   morar e depois talvez alugar" é fraco.
9. **Acessibilidade:** necessidade declarada (idoso com dificuldade, cadeirante, cirurgia, não sobe escada). "Tem
   elevador?" sem motivo e "pai idoso que sobe escada numa boa" são fracos.
10. **Reforma recente** descreve o imóvel visitado ou oferecido; "precisa de reforma", "oportunidade para reforma"
    e "topa reformar" são falsos; "dono trocou o chuveiro e pintou um quarto" é fraco.

## Tipos de caso difícil (prefixo da `nota`)
| tipo | ajuste | teste | o que mede |
|---|---|---|---|
| negação | 2 | 3 | palavra-chave presente com sentido invertido; condição negativa |
| composta | 4 | 7 | E / OU, com ou sem parte numérica |
| inferência fraca | 2 | 2 | pista que não decide → indecidível |
| fácil | 1 | 6 | fato afirmado com paráfrases (algumas com filtro de campo) |

## Contagens (validador do rotulador, 2026-10-01, zero erros)
`linhas.json`: 187 linhas · `finalidade` 123 compra / 64 locação · `canal` 97 whatsapp / 33 telefone / 30
presencial / 27 e-mail · `data` jul 65 / ago 58 / set 64 · `visitas` 0: 77, 1: 69, 2: 37, 3: 4 · `orcamento` nulo em 37.

Fatos por estado nas linhas (afirmado / negado / fraco): mudança de cidade 13/2/2 · reforma 9/4/2 · urgência 12/4/2 ·
financiamento 15/7/2 · pet 10/4/2 · filhos 11/3/2 · home office 7/3/2 · reclamou 5/0/2 · elogiou 5/0/0 ·
concorrente 9/3/1 · acessibilidade 8/2/2 · investidor 6/4/1 · desistiu 10/7/4 · caro 15/3/1 · barulho 7/1/3 ·
decisor 7/2/2 · perto do trabalho 6/2/1. Cerca de 20 linhas são neutras (sem fato).

Verdadeiras / indecidíveis por condição:
| arquivo | condições | difíceis | V/I por condição |
|---|---|---|---|
| `rascunho.json` | 5 | 0 | 13/2 · 10/2 · 15/1 · 15/2 · 8/2 |
| `condicoes_ajuste.json` | 9 | 8 (89%) | A01 13/2 · A02 9/2 · A03 6/0 · A04 7/0 · A05 6/2 · A06 19/3 · A07 4/1 · A08 7/2 · A09 6/2 |
| `condicoes_teste.json` | 18 | 12 (67%) | T01 11/2 · T02 8/2 · T03 4/0 · T04 15/1 · T05 7/3 · T06 7/2 · T07 6/1 · T08 4/0 · T09 4/0 · T10 8/0 · T11 9/2 · T12 4/7 · T13 4/1 · T14 17/4 · T15 5/0 · T16 6/1 · T17 5/0 · T18 7/1 |

Toda condição tem ≥ 4 verdadeiras. A maioria das linhas é falsa para qualquer condição (4 a 19 verdadeiras em
187): o baseline "tudo falso" tem acurácia alta e recall zero — medir precisão/recall por condição, não acurácia.

## Aviso ao construtor
- A parte entre crases é do código: filtrar pelos `campos` ANTES de perguntar ao Jev; o Jev só vê a frase
  semântica e o `texto` da linha (uma requisição por linha ou um Noul por linha no mesmo state, a critério).
- Erro caro: marcar como verdadeira uma linha de negação (SQ-A02, A04, T08, T11, T15) — é o erro que o `LIKE`
  comete, e o exemplo existe para mostrar a diferença.
- Indecidíveis ficam fora da métrica binária; medir à parte "o sistema mandou para revisão?" (faixa do meio do Noul).
- `rascunho.json` repete a condição SQ-A01 e quatro fáceis, só para o encanamento.

## Ambiguidades decididas pelo rotulador (não estavam no briefing)
- Os `campos` são seis e fixos; `orcamento` nulo falha a comparação (não vira indecidível).
- Condição negativa ("declararam NÃO ter") = negação explícita; silêncio é falso nos dois sentidos.
- Filtro de campo falhando → falso, mesmo com fato fraco (código antes do Jev).
- Linha com mais de um fato pode ser verdadeira em várias condições; isso é esperado, não erro.
- A mesma tabela serve a ajuste e teste; o teste não mede linhas inéditas.
