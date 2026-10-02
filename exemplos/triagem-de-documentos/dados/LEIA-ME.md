# Dados do `triagem-de-documentos` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-02, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item X) e [DADOS.md](../../DADOS.md).
Documentos longos fictícios de quatro tipos (contrato de locação, prestação de serviço, ata de assembleia de
condomínio, proposta comercial) e condições do tipo "quais destes documentos têm X?". Partes, imóveis, empresas,
condomínios e valores são inventados; não há CPF, CNPJ, e-mail nem telefone. Gabarito = o que um advogado ou gestor
lendo o documento INTEIRO responderia à pergunta "este documento satisfaz a condição?".

Arquivos: `documentos.json` (compartilhado por ajuste e teste), `rascunho.json` (5 condições fáceis),
`condicoes_ajuste.json`, `condicoes_teste.json` (abrir uma vez, no fim), `gera.py` (gerador) e `valida.py`.
Envelope `{"versao": "2026-10-02", "autor": "fable", "casos"}`; em `documentos.json` a chave é `"documentos"`.
Como no `sql-semantico`, a separação é entre **condições**, não entre documentos.

## Como os documentos foram montados (mecanismo, não dado real)
`gera.py` monta os 44 documentos a partir de um **banco de 94 textos de seção escritos à mão** (contando as
variantes de trecho dentro de uma mesma seção, como as três frases de renovação da cláusula de prazo), em **4
moldes** (um por tipo, com ordem fixa de seções: 5 obrigatórias + até 3 opcionais na locação; 4 + até 4 no serviço;
4 + até 4 na ata; 6 + até 2 na proposta) e **44 receitas explícitas** — uma por documento, dizendo qual variante
entra em cada seção. A semente fixa (`20261002`) só sorteia nomes, endereços, valores e datas; o que cada documento
afirma, nega, omite ou revoga vem da receita. Cada variante carrega **fatos de autoria** (ex.: `multa=True`,
`exclusividade=False`, `animais="ind"`) e o gabarito de cada condição é calculado desses fatos, antes de qualquer
chamada ao Jev. Consequência honesta: placar bom valida o mecanismo (mapa por seção × documento inteiro), não a
qualidade em contratos reais — os textos de uma mesma variante se repetem entre documentos, mudando só os
parâmetros.

## Esquema (o do briefing, sem campo extra)
- Documento: `{"id", "tipo", "secoes": [{"id", "titulo", "texto"}], "campos"}`. `id` = `L01…L11`, `S01…S11`,
  `A01…A11`, `P01…P11`; seção = `<doc>-s<n>` na ordem do texto. `tipo` ∈ `locacao | prestacao_servico |
  ata_condominio | proposta_comercial`. 4–8 seções de 60–200 palavras (medido: 5–8 seções, 74–115 palavras).
- `campos`, fixos por tipo e com o valor **EFETIVO depois de ler o documento inteiro**:
  - locação: `valor_aluguel`, `prazo_meses`, `multa_alugueis` (int | `null` quando negada, ausente ou revogada),
    `indice_reajuste` (`"IGP-M" | "IPCA" | null`), `garantia` (`fiador | caucao | seguro_fianca`), `renovacao_automatica`.
  - serviço: `valor_mensal`, `prazo_meses`, `multa_percentual` (idem), `indice_reajuste`, `exclusividade`, `renovacao_automatica`.
  - ata: `data`, `quorum_percentual`, `taxa_valor` (valor vigente após a assembleia), `reajuste_percentual` (0 quando
    mantida ou rejeitado), `obra_aprovada` (false quando a aprovação foi declarada sem efeito).
  - proposta: `valor_total`, `validade_dias`, `prazo_entrega_dias` (| null), `desconto_percentual` (0 sem desconto), `garantia_meses`.
- Condição: `{"id", "condicao", "tipo": "semantica" | "numerica", "documentos_verdadeiros", "documentos_indecidiveis",
  "secao_que_prova", "nota"}`. Documento fora das duas listas vale **falso** (inclusive os de outro tipo: a condição
  diz a que tipo se aplica). `nota` começa com `"difícil: <tipo> — …"` ou `"fácil"`.

## Convenções (o que conta e o que não conta)
1. **A condição é sobre o que o documento DISPÕE ao final.** Silêncio = falso ("documento sem a cláusula").
2. **Negação explícita** ("NÃO haverá multa", "NÃO estabelece exclusividade", "não é permitida a permanência de
   animais", "MANTER a taxa sem reajuste", "REJEITADA") é **falsa** para a condição afirmativa.
3. **Revogação em seção posterior** ("fica sem efeito a multa prevista na cláusula…", "afastam a prorrogação
   automática", "declarou SEM EFEITO a aprovação da obra") torna a condição **falsa** e o campo numérico `null`/0/false.
   A seção que revoga vem sempre DEPOIS da que institui (disposições finais; retificação antes do encerramento).
4. **Termo só no título** ("Da exclusividade, da confidencialidade e da propriedade intelectual" com texto só de
   confidencialidade; "Do foro e da arbitragem" com texto só de foro; "Animais e uso das áreas comuns" que diz que o
   ponto não foi discutido; "Do uso e da sublocação" só sobre uso) = **falso**.
5. **Seção parecida de outro assunto** (multa por atraso ≠ multa por rescisão; controle de acesso por biometria ≠
   câmeras; multa rescisória ≠ penalidade de SLA; implantação com suporte e manuais ≠ treinamento) = **falso**.
6. **Depende de DUAS seções**: verdadeiro só com as duas (desconto na seção de preço + "exclusivamente à vista" na de
   pagamento; fiador na garantia + extensão até as chaves nas disposições finais). Uma só → falso. A `secao_que_prova`
   é a que **completa** a prova (a segunda); a `nota` da condição diz qual é a outra.
7. **Indecidível** (`documentos_indecidiveis`) só quando o texto deixa a decisão para depois sem negar nem afirmar:
   animais "mediante consulta prévia ao locador" (L08) e comissão com tolerância provisória (A08); duas câmeras em
   comodato por noventa dias com decisão futura (A09); SLA cujo descumprimento "poderá ensejar revisão do contrato"
   (S05). Adiamento de deliberação ("ficará para a próxima assembleia") é **falso**, não indecidível: a ata não
   aprovou. Condição numérica nunca tem indecidível.
8. **Numérica é do código**: a expressão entre crases (`` `multa_alugueis` > 2 ``) resolve-se pelos `campos`;
   documento sem o campo vale falso; `secao_que_prova` aponta a seção onde o número está. "Dois aluguéis" não é
   "superior a dois"; "quinze dias" não é "inferior a quinze".
9. **Exclusividade restrita** (lista fechada de concorrentes, S06) conta como exclusividade; "aprovadas com ressalvas"
   conta como contas aprovadas; proposta com desconto "para qualquer modalidade" NÃO é desconto condicionado à vista.

## Tipos de caso difícil (prefixo da `nota` da condição; a dificuldade mora nos documentos que a condição atinge)
| tipo | ajuste | teste | onde |
|---|---|---|---|
| negada | 2 (A01, A06) | 2 (T01, T08) | L03, L04, S02, S10, A02–A04, A06, A09–A11 |
| revogada | (dentro de A01) | 2 (T02, T11) | L02, L05, L09, S03, S05, A05 |
| duas seções | 1 (A03) | 1 (T03) | P01–P11, L01–L11 |
| termo só no título | 1 (A04) | 1 (T04) | S04, S09, L04, L08, S05, A06 |
| seção parecida de outro assunto | (dentro de A01) | 1 (T05) | L07, A07, S01/S06/S09 |
| documento sem a cláusula | (dentro de A01) | 1 (T09) | P02, P03, P07, P10, P11 e todo documento silente |
| fácil / numérica | 2 (A02, A05) | 4 (T06, T07, T10, T12) | — |

## Contagens (validador do rotulador, 2026-10-02, zero erros)
`documentos.json`: 44 documentos (11 por tipo), 316 seções, 74–115 palavras por seção (média 92).

Verdadeiros / indecidíveis por condição:
| arquivo | condições | difíceis | V/I por condição |
|---|---|---|---|
| `rascunho.json` | 5 | 0 (por desenho) | R01 8/0 · R02 5/0 · R03 8/0 · R04 7/0 · R05 10/0 |
| `condicoes_ajuste.json` | 6 | 4 (67%) | A01 6/0 · A02 4/0 · A03 5/0 · A04 5/0 · A05 5/0 · A06 6/0 |
| `condicoes_teste.json` | 12 | 8 (67%) | T01 5/1 · T02 6/0 · T03 4/0 · T04 4/0 · T05 5/1 · T06 4/0 · T07 4/0 · T08 5/2 · T09 4/0 · T10 5/0 · T11 5/0 · T12 7/0 |

Toda condição tem ≥ 4 verdadeiros; numéricas: 2 no ajuste, 4 no teste, 1 no rascunho. A maioria dos documentos é
falsa para qualquer condição (4 a 10 verdadeiros em 44): medir precisão/recall por condição, não acurácia.

O validador conferiu: envelope, chaves exatas, IDs de seção em sequência, 4–8 seções de 60–200 palavras, `campos`
fixos por tipo e tipados, ≥ 4 verdadeiros, `secao_que_prova` igual aos verdadeiros e pertencente ao documento,
verdadeiro ∩ indecidível vazio, condições numéricas recalculadas pelos `campos` (sem indecidível), ≥ 30% difíceis em
ajuste e teste, os seis tipos difíceis presentes, nenhuma condição repetida entre ajuste e teste, UTF-8 sem BOM, LF.

## Aviso ao construtor
- Erro caro: marcar como verdadeiro o documento que **nega** ou **revoga** a cláusula (A01: L03, L04, L05; T02: L09,
  S05; T11: L02) — é o erro que a busca por palavra comete e que o "documento inteiro num state" tende a repetir
  quando a revogação está longe da cláusula.
- O mapa por seção precisa de redução em código: "alguma seção afirma" NÃO basta (revogação posterior, duas
  seções). Sugestão: um Noul de afirmação e um de revogação por seção; o código combina pela ordem.
- Indecidíveis ficam fora da métrica binária; medir à parte "mandou para revisão?".
- `rascunho.json` repete o mecanismo com condições fáceis, só para o encanamento.

## v2 (2026-10-02b) — condições compostas escritas com " E "
A revisão do Codex apontou que as duas condições "depende de DUAS seções" (TD-A03 e TD-T03) estavam escritas como
condição simples, enquanto o construtor implementou a gramática composta com o conector ` E ` (maiúsculo, como no
`sql-semantico`: "<cláusula A> E <cláusula B>"). Mudou SÓ o texto `condicao` das duas, agora com as duas premissas
explícitas que a convenção 6 já descrevia:
- TD-A03: "Proposta comercial que concede desconto sobre o preço E condiciona esse desconto exclusivamente ao
  pagamento à vista." (premissa A na seção de preço; premissa B na de pagamento).
- TD-T03: "Contrato de locação em que a garantia é prestada por fiador E a responsabilidade do fiador se estende
  até a efetiva devolução das chaves, inclusive na prorrogação." (A na garantia; B nas disposições finais).

`documentos_verdadeiros`, `documentos_indecidiveis` e `secao_que_prova` não mudaram (conferido por diff contra a
versão anterior: só `condicao` difere nesses dois casos). `secao_que_prova` continua sendo a seção que COMPLETA a
prova, a mais tardia das duas (`P??-s4` pagamento, depois de `s3` preço; `L??-s8` disposições finais, última do
contrato). `versao` de `condicoes_ajuste.json` e `condicoes_teste.json` subiu para `2026-10-02b`; `documentos.json` e
`rascunho.json` seguem em `2026-10-02`. `gera.py` e `valida.py` acompanham (constante de versão por arquivo).

## Ambiguidades decididas pelo rotulador (não estavam no briefing)
- `campos` traz o valor efetivo (após revogação), não o literal da cláusula; a condição semântica e a numérica
  correspondentes concordam sempre.
- A condição declara o tipo de documento a que se aplica; os demais tipos valem falso sem precisar de nota.
- Em "duas seções", `secao_que_prova` é a seção que completa a prova.
- Adiamento, comodato experimental e "mediante consulta" foram separados: adiamento é falso; os outros dois,
  indecidível.
- Os 44 documentos servem a ajuste e teste; o teste mede condições inéditas sobre documentos já vistos.
