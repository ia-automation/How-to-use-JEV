# Resultados — sql-semantico

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; separação da condição, filtro, validação, decisão e baseline: `sql.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Teto do texto: 2000 caracteres (acima → indecidivel, sem chamada). Orçamento: 3500 requisições no teste.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (18 condições × 187 linhas), com a política acima; **1_f1**: F1 do Jev sobre as decidíveis decididas ≥ 0,85 e ≥ F1 do baseline (LIKE) + 0,15; **2_perdidas**: linha verdadeira do gabarito que saiu `falso` ≤ 5% das verdadeiras; **3_negacao**: linha falsa marcada `verdadeiro` em condição de negação ≤ 2; **4_humano**: decidíveis mandadas a humano (`indecidivel`) ≤ 5%; **secundario_nao_decide**: indecidíveis do gabarito que foram a humano ≥ 50%; falha operacional = 0; **se_falhar**: 1 falhando = o LIKE basta ou o Jev não lê a condição; 2 ou 3 = o filtro perde ou inverte o que deveria achar (não serve sem mudança); 4 = custa humano demais

Versão em afinação (NÃO congelada): `perguntas.py` sha256 325429056f68ed58… · `sql.py` sha256 cc456c73a5a53a1b… · `run.py` sha256 2be2af17baa09ae9… · `dados/linhas.json` sha256 b11253f810da103e… · `dados/condicoes_teste.json` sha256 2310fb5836605d52…

## Lado a lado

| conjunto | variante | decidíveis | decididas | P | R | F1 | F1 estrito (humano = erro) | humano (decidíveis) | PERDIDAS (V → falso) | FP EM NEGAÇÃO | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | Jev (oficial) | 1669 | 1551 | 0.954 | 1.000 | 0.976 | 0.873 | 118 (0.071) | 0/77 | 0 | 8/14 (V: 1) | 0 |
| ajuste | baseline LIKE | 1669 | 1669 | 0.364 | 0.558 | 0.441 | 0.441 | 0 (0.000) | 34/77 | 27 | 0/14 (V: 1) | 0 |

| conjunto | condições | difíceis | linhas | requisições | p50_ms | p95_ms | tokens_por_requisicao | US$_por_1000_linhas | modelo |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | 9 | 8 | 187 | 1303 | 249 | 305 | 920 | 0.0299 | jev-1.13.0 |

## Conjunto `ajuste` — 9 condições × 187 linhas (arquivo versão 2026-10-01, autor fable); 8 difíceis; 77 verdadeiras e 14 indecidíveis no gabarito

### Total (micro, sobre as linhas decidíveis de todas as condições) — Jev × variantes × baseline LIKE

P/R/F1 sobre as decidíveis que o sistema DECIDIU; `humano` = decidíveis mandadas a `indecidivel` (fora de P/R/F1; `F1 estrito` as conta como erro). **PERDIDAS** = verdadeira do gabarito que saiu `falso` (o filtro perdeu a linha). **FP EM NEGAÇÃO** = falsa marcada `verdadeiro` numa condição da família negação (o erro do LIKE). `indecidíveis → humano` = linhas de pista fraca do gabarito que o sistema mandou revisar (e quantas virou `verdadeiro`). Variante oficial: `inteira`; faixa de `stated` 0.2–0.8; `hinted` ≥ 0.8.

| variante | decidíveis | decididas | P | R | F1 | F1 estrito (humano = erro) | humano (decidíveis) | PERDIDAS (V → falso) | FP EM NEGAÇÃO | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev (oficial) | 1669 | 1551 | 0.954 | 1.000 | 0.976 | 0.873 | 118 (0.071) | 0/77 | 0 | 8/14 (V: 1) | 0 |
| Jev: inteira | 1669 | 1551 | 0.954 | 1.000 | 0.976 | 0.873 | 118 (0.071) | 0/77 | 0 | 8/14 (V: 1) | 0 |
| Jev: inteira+pista | 1669 | 1551 | 0.954 | 1.000 | 0.976 | 0.873 | 118 (0.071) | 0/77 | 0 | 8/14 (V: 1) | 0 |
| Jev: cláusulas | 1669 | 1548 | 0.940 | 1.000 | 0.969 | 0.875 | 121 (0.072) | 0/77 | 0 | 8/14 (V: 1) | 0 |
| Jev: cláusulas+pista | 1669 | 1548 | 0.940 | 1.000 | 0.969 | 0.875 | 121 (0.072) | 0/77 | 0 | 8/14 (V: 1) | 0 |
| baseline LIKE | 1669 | 1669 | 0.364 | 0.558 | 0.441 | 0.441 | 0 (0.000) | 34/77 | 27 | 0/14 (V: 1) | 0 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 F1 (decididas) | 0.976 (baseline 0.441) | ≥ 0.85 e ≥ 0.591 | ✓ |
| 2 perdidas (V → falso) | 0/77 (0.000) | ≤ 0.05 | ✓ |
| 3 FP em negação | 0 | ≤ 2 | ✓ |
| 4 humano (decidíveis) | 118/1669 (0.071) | ≤ 0.05 | ✗ |
| secundário: indecidíveis → humano | 8/14 | ≥ 0.5 | ✓ |
| secundário: falhas operacionais | 0 | 0 | ✓ |

### Por condição

`filtro` = parte de campo resolvida pelo código; `chamadas` = linhas que passaram no filtro e foram ao Jev; `V/I` = verdadeiras / indecidíveis do gabarito; `base` = baseline LIKE (radicais entre colchetes).

| id | família | filtro | composta | chamadas | V/I | P | R | F1 | humano | perdidas | FP | I → humano | base F1 | base FP | base perdidas | LIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SQ-A01 | inferência fraca | — | — | 187 | 13/2 | 1.000 | 1.000 | 1.000 | 19 | 0 | 0 | 2/2 | 0.235 | 2 | 11 | [mudar, cidad] |
| SQ-A02 | negação | — | — | 187 | 9/2 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 1/2 | 0.571 | 6 | 3 | [recem, refor] |
| SQ-A03 | composta | orcamento <= 500000 | — | 97 | 6/0 | 1.000 | 1.000 | 1.000 | 38 | 0 | 0 | 0/0 | 0.769 | 2 | 1 | [depen, finan, banca] |
| SQ-A04 | negação | — | — | 187 | 7/0 | 1.000 | 1.000 | 1.000 | 20 | 0 | 0 | 0/0 | 0.400 | 21 | 0 | [desca, finan, pagar, recur, propr, vista, heran, venda] |
| SQ-A05 | fácil | canal = whatsapp | — | 97 | 6/2 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 2/2 | nan | 1 | 6 | [anima, estim] |
| SQ-A06 | composta | — | OU | 187 | 19/3 | 0.944 | 1.000 | 0.971 | 16 | 0 | 1 | 1/3 | 0.444 | 9 | 11 | [urgen, fecha, avali, propo, imobi] |
| SQ-A07 | composta | finalidade = locacao | — | 64 | 4/1 | 1.000 | 1.000 | 1.000 | 5 | 0 | 0 | 0/1 | 0.600 | 3 | 1 | [recla, atend] |
| SQ-A08 | inferência fraca | — | — | 187 | 7/2 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 0/2 | 0.333 | 28 | 0 | [traba, casa, home, offic, remot, consu, virtu] |
| SQ-A09 | inferência fraca | visitas >= 1 | — | 110 | 6/2 | 0.750 | 1.000 | 0.857 | 15 | 0 | 2 | 2/2 | 0.714 | 3 | 1 | [desis, busca, encer] |

### Por família difícil (pela `nota` do rotulador)

| família | condições | F1 Jev | F1 baseline | humano Jev | perdidas Jev | FP Jev | perdidas base | FP base | I → humano |
|---|---|---|---|---|---|---|---|---|---|
| inferência fraca | 3 | 0.962 | 0.384 | 36 | 0 | 2 | 12 | 33 | 4/6 |
| negação | 2 | 1.000 | 0.464 | 22 | 0 | 0 | 3 | 27 | 1/2 |
| composta | 3 | 0.978 | 0.542 | 59 | 0 | 1 | 13 | 14 | 1/4 |
| fácil | 1 | 1.000 | nan | 1 | 0 | 0 | 6 | 1 | 2/2 |

### Onde `stated` cai, por gabarito (só linhas que foram ao Jev)

| gabarito | n | stated mín | p10 | p50 | p90 | máx | ≤ 0,2 | 0,2–0,8 | ≥ 0,8 | hinted p50 | hinted ≥ 0,8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| verdadeiro | 77 | 0.280 | 0.660 | 0.940 | 0.970 | 0.980 | 0 | 15 | 62 | 0.950 | 69 |
| falso | 1212 | 0.020 | 0.030 | 0.050 | 0.190 | 0.890 | 1106 | 103 | 3 | 0.160 | 21 |
| indecidivel | 14 | 0.070 | 0.110 | 0.380 | 0.700 | 0.800 | 5 | 8 | 1 | 0.800 | 7 |

### Cobertura × erro por faixa de `stated` (variante oficial; mesmas respostas, outra faixa)

| faixa | cobertura (decididas/decidíveis) | erro entre decididas | F1 | humano | perdidas | FP em negação | I → humano |
|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.929 | 0.002 | 0.976 | 118 | 0 | 0 | 8/14 |
| 0.5–0.5 | 1.000 | 0.016 | 0.844 | 0 | 4 | 3 | 0/14 |
| 0.4–0.6 | 0.991 | 0.010 | 0.893 | 15 | 2 | 0 | 3/14 |
| 0.3–0.7 | 0.974 | 0.006 | 0.932 | 44 | 1 | 0 | 4/14 |
| 0.2–0.8 | 0.929 | 0.002 | 0.976 | 118 | 0 | 0 | 8/14 |
| 0.1–0.9 | 0.845 | 0.000 | 1.000 | 259 | 0 | 0 | 13/14 |

### Custo e latência (medidos na chamada real; do cache também)

| linhas avaliadas (cond × linha) | sem chamada (filtro) | requisicoes | novas (não cache) | textos longos (sem chamada) | falhas operacionais (→ indecidivel) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_1000_linhas_avaliadas | US$_por_1000_requisicoes | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1683 | 380 | 1303 | 1303 | 0 | 0 | 2980 | 249 | 305 | 920 | 0.050364 | 0.0299 | 0.0387 | jev-1.13.0 |

### Caso a caso — erros, linhas mandadas a humano e indecidíveis do gabarito

`st`/`hi` = Nouls `stated` e `hinted`; `partes` = Nouls por cláusula (compostas); `saída` = variante oficial; `base` = LIKE.

| cond | linha | gab | st | hi | partes | saída | ok | base | por | texto |
|---|---|---|---|---|---|---|---|---|---|---|
| SQ-A01 | OB-008 | indecidivel | 0.24 | 0.60 | — | indecidivel | ✓ | falso | jev | Cliente comentou que a filha vai prestar vestibular em São Paulo; por enquanto procura só pra ele aqui, 2 quar… |
| SQ-A01 | OB-009 | indecidivel | 0.24 | 0.76 | — | indecidivel | ✓ | falso | jev | Perguntou se o condomínio tem portaria 24h e se a região é bem servida de ônibus pra rodoviária. |
| SQ-A01 | OB-010 | falso | 0.25 | 0.05 | — | indecidivel | ✗ | verdadeiro | jev | Disse que não vai mudar de cidade de jeito nenhum, a família toda é daqui; quer trocar de bairro só. |
| SQ-A01 | OB-011 | falso | 0.26 | 0.31 | — | indecidivel | ✗ | falso | jev | Trabalha remoto pra uma empresa de fora, mas faz questão de continuar morando aqui. Procura algo com um escrit… |
| SQ-A01 | OB-024 | falso | 0.23 | 0.60 | — | indecidivel | ✗ | falso | jev | Precisa fechar em 10 dias, o contrato atual vence e o dono não renova. Aceita qualquer bairro da zona sul. |
| SQ-A01 | OB-028 | falso | 0.27 | 0.78 | — | indecidivel | ✗ | falso | jev | Pediu pra agilizar a documentação porque o bebê nasce em janeiro e quer estar instalada antes. |
| SQ-A01 | OB-030 | falso | 0.36 | 0.58 | — | indecidivel | ✗ | falso | jev | Quer visitar amanhã cedo e assinar na mesma semana se gostar; empresa paga a mudança até o fim do mês. |
| SQ-A01 | OB-055 | falso | 0.26 | 0.79 | — | indecidivel | ✗ | falso | jev | Grávida de 6 meses, quer 3 quartos e escola perto. Marido vai ver as opções no fim de semana. |
| SQ-A01 | OB-087 | falso | 0.23 | 0.63 | — | indecidivel | ✗ | falso | jev | A mãe de 82 anos vai morar junto; precisa ser térreo ou prédio com elevador, sem degrau na entrada. |
| SQ-A01 | OB-100 | falso | 0.28 | 0.61 | — | indecidivel | ✗ | falso | jev | Compra pro filho morar durante a faculdade e depois decide se aluga. |
| SQ-A01 | OB-114 | falso | 0.63 | 0.85 | — | indecidivel | ✗ | falso | jev | Disse que o metro quadrado da região 'está fora da realidade' e que vai olhar mais longe. |
| SQ-A01 | OB-138 | falso | 0.37 | 0.72 | — | indecidivel | ✗ | falso | jev | Marido trabalha na zona norte e ela na zona sul; querem algo no meio do caminho. |
| SQ-A01 | OB-143 | falso | 0.26 | 0.47 | — | indecidivel | ✗ | falso | jev | Cliente antigo, comprou com a gente em 2019 e quer vender pra comprar maior. Quatro pessoas em casa. |
| SQ-A01 | OB-163 | falso | 0.35 | 0.69 | — | indecidivel | ✗ | falso | jev | Mãe idosa com dificuldade de locomoção vai morar junto, e o apto da rua de trás tem obra que não acaba: quer t… |
| SQ-A01 | OB-167 | falso | 0.24 | 0.23 | — | indecidivel | ✗ | falso | jev | Cliente de locação achou caro e desistiu; vai continuar na casa dos pais. |
| SQ-A01 | OB-168 | falso | 0.24 | 0.63 | — | indecidivel | ✗ | falso | jev | Quer um apto perto do trabalho dela e da escola do filho; o condomínio não pode cobrar mais de 800. |
| SQ-A01 | OB-178 | verdadeiro | 0.66 | 0.94 | — | indecidivel | ✗ | verdadeiro | jev | Mudança de cidade confirmada pra março e precisa resolver o aluguel antes de fevereiro; orçamento até 3 mil. |
| SQ-A01 | OB-179 | falso | 0.24 | 0.66 | — | indecidivel | ✗ | falso | jev | Locatário com pressa: foi despejado por venda do imóvel e tem 30 dias pra sair. |
| SQ-A01 | OB-181 | falso | 0.74 | 0.89 | — | indecidivel | ✗ | falso | jev | Trouxe o pai de 79 anos pra morar junto e procura locação de térreo com banheiro adaptado. |
| SQ-A01 | OB-184 | falso | 0.35 | 0.35 | — | indecidivel | ✗ | falso | jev | Desistiu: os valores da região passaram do que ele consegue pagar e vai ficar no aluguel atual. |
| SQ-A01 | OB-186 | falso | 0.67 | 0.83 | — | indecidivel | ✗ | verdadeiro | jev | Achou o aluguel pedido fora da realidade e desistiu de se mudar por enquanto. |
| SQ-A02 | OB-022 | indecidivel | 0.42 | 0.89 | — | indecidivel | ✓ | falso | jev | O proprietário disse que trocou o chuveiro e pintou um quarto antes de anunciar. Cliente quer ver pessoalmente… |
| SQ-A02 | OB-023 | indecidivel | 0.07 | 0.45 | — | falso | ✗ | falso | jev | Fotos mostram piso cerâmico claro e paredes brancas; não sei se é recente ou só limpo. Cliente pediu visita. |
| SQ-A02 | OB-155 | falso | 0.26 | 0.74 | — | indecidivel | ✗ | verdadeiro | jev | Reclamou que o anúncio dizia 'reformado' e o apto está com piso de 30 anos; se sentiu enrolado. |
| SQ-A02 | OB-159 | verdadeiro | 0.42 | 0.74 | — | indecidivel | ✗ | verdadeiro | jev | Cliente investidor, não vai financiar; quer dois studios reformados pra alugar por temporada. |
| SQ-A03 | OB-010 | falso | 0.22 | 0.22 | — | indecidivel | ✗ | falso | jev | Disse que não vai mudar de cidade de jeito nenhum, a família toda é daqui; quer trocar de bairro só. |
| SQ-A03 | OB-014 | falso | 0.30 | 0.46 | — | indecidivel | ✗ | falso | jev | Mostrei a casa do Jardim Europa, toda repaginada pelo dono há uns meses, janelas e portas trocadas. Ela achou … |
| SQ-A03 | OB-015 | falso | 0.26 | 0.29 | — | indecidivel | ✗ | falso | jev | Apartamento de 3 quartos que o proprietário acabou de reformar; entregou com armários novos. Cliente pediu seg… |
| SQ-A03 | OB-025 | verdadeiro | 0.73 | 0.79 | — | indecidivel | ✗ | falso | jev | Cliente com pressa: casamento em março e quer entrar no apto antes. Já aprovou crédito na Caixa. |
| SQ-A03 | OB-035 | verdadeiro | 0.50 | 0.72 | — | indecidivel | ✗ | verdadeiro | jev | Depende de aprovação do banco; a renda dele é informal e isso pode travar. Pedi documentos. |
| SQ-A03 | OB-039 | verdadeiro | 0.69 | 0.76 | — | indecidivel | ✗ | verdadeiro | jev | Explicou que o financiamento seria pelo nome do pai, que tem renda comprovada. Decisão final é dele mesmo assi… |
| SQ-A03 | OB-059 | falso | 0.24 | 0.14 | — | indecidivel | ✗ | falso | jev | Perguntou se o condomínio tem área kids e salão de festas. |
| SQ-A03 | OB-071 | falso | 0.22 | 0.18 | — | indecidivel | ✗ | falso | jev | Cliente reclamou que ficou 3 dias sem resposta e que quase fechou com outra imobiliária. Pediu desculpas em no… |
| SQ-A03 | OB-072 | falso | 0.24 | 0.16 | — | indecidivel | ✗ | falso | jev | Irritado: a visita de ontem foi desmarcada em cima da hora pela segunda vez. Disse que vai procurar em outro l… |
| SQ-A03 | OB-074 | falso | 0.25 | 0.14 | — | indecidivel | ✗ | falso | jev | Falou que o anúncio estava com metragem errada e se sentiu enganada. Expliquei e ela aceitou continuar. |
| SQ-A03 | OB-077 | falso | 0.21 | 0.10 | — | indecidivel | ✗ | falso | jev | Achou tudo ótimo no atendimento, só o imóvel que não serviu. |
| SQ-A03 | OB-085 | falso | 0.22 | 0.44 | — | indecidivel | ✗ | falso | jev | Vai visitar um lançamento da construtora no sábado e depois decide entre o nosso e o deles. |
| SQ-A03 | OB-094 | falso | 0.22 | 0.16 | — | indecidivel | ✗ | falso | jev | Filho autista precisa de ambiente tranquilo e sem escada aberta; busca casa térrea em rua calma. |
| SQ-A03 | OB-095 | falso | 0.36 | 0.71 | — | indecidivel | ✗ | falso | jev | Compra pra alugar, quer rendimento acima de 0,5% ao mês; não vai morar. Tem até 450 mil. |
| SQ-A03 | OB-096 | falso | 0.37 | 0.69 | — | indecidivel | ✗ | falso | jev | Quer um studio perto da faculdade pra colocar no Airbnb, até 420 mil. Já tem outros dois. |
| SQ-A03 | OB-097 | falso | 0.27 | 0.54 | — | indecidivel | ✗ | falso | jev | É pra morar mesmo, primeira casa. Nada de investimento. |
| SQ-A03 | OB-100 | falso | 0.29 | 0.53 | — | indecidivel | ✗ | falso | jev | Compra pro filho morar durante a faculdade e depois decide se aluga. |
| SQ-A03 | OB-103 | falso | 0.27 | 0.18 | — | indecidivel | ✗ | falso | jev | Desistiu da busca: vai renovar o aluguel atual por mais um ano. Pediu pra tirar da lista. |
| SQ-A03 | OB-105 | falso | 0.26 | 0.56 | — | indecidivel | ✗ | falso | jev | Continua procurando, mesmo tendo achado tudo caro até agora. Pediu opções em bairros mais afastados. |
| SQ-A03 | OB-107 | falso | 0.27 | 0.20 | — | indecidivel | ✗ | falso | jev | Fechou com outra imobiliária na semana passada. Agradeceu o atendimento. |
| SQ-A03 | OB-108 | falso | 0.25 | 0.38 | — | indecidivel | ✗ | falso | jev | Disse que pausou a procura até vender o carro. Deve voltar em dois meses. |
| SQ-A03 | OB-109 | falso | 0.40 | 0.59 | — | indecidivel | ✗ | falso | jev | Não desistiu, mas reduziu o orçamento pra 350 mil depois da demissão da esposa. |
| SQ-A03 | OB-111 | falso | 0.21 | 0.25 | — | indecidivel | ✗ | falso | jev | Avisou que vai ficar onde está, reformar a casa atual sai mais barato. |
| SQ-A03 | OB-117 | falso | 0.22 | 0.50 | — | indecidivel | ✗ | falso | jev | Achou barato pro padrão do prédio e perguntou se tem algum problema escondido. |
| SQ-A03 | OB-119 | falso | 0.26 | 0.59 | — | indecidivel | ✗ | falso | jev | Pediu um imóvel 'mais em conta' que os três que mostrei. |
| SQ-A03 | OB-126 | falso | 0.27 | 0.14 | — | indecidivel | ✗ | falso | jev | Reclamou do barulho da obra ao lado durante a visita e pediu outra opção. |
| SQ-A03 | OB-128 | falso | 0.23 | 0.49 | — | indecidivel | ✗ | falso | jev | Os pais vão pagar a entrada e querem aprovar o imóvel antes. |
| SQ-A03 | OB-149 | falso | 0.24 | 0.35 | — | indecidivel | ✗ | falso | jev | Cliente perguntou sobre IPTU e taxa de condomínio da unidade 3 quartos; vai comparar com outra. |
| SQ-A03 | OB-157 | falso | 0.21 | 0.19 | — | indecidivel | ✗ | falso | jev | Trabalha de casa e tem dois gatos; condomínio precisa aceitar bicho e ter sala extra. |
| SQ-A03 | OB-160 | falso | 0.22 | 0.25 | — | indecidivel | ✗ | falso | jev | Família com três crianças pequenas vindo do interior; o pai trabalha em casa e quer um escritório longe dos qu… |
| SQ-A03 | OB-162 | falso | 0.21 | 0.25 | — | indecidivel | ✗ | falso | jev | Avaliando uma proposta nossa e outra de um corretor autônomo; falou que o nosso atendimento foi 'nota dez' até… |
| SQ-A03 | OB-172 | falso | 0.22 | 0.13 | — | indecidivel | ✗ | falso | jev | Cliente perguntou se o prédio tem gerador e se a vizinhança é tranquila à noite. |
| SQ-A03 | OB-173 | falso | 0.26 | 0.22 | — | indecidivel | ✗ | falso | jev | Casal sem filhos e sem pet, ambos presenciais, só querem 2 vagas de garagem. |
| SQ-A03 | OB-174 | falso | 0.26 | 0.25 | — | indecidivel | ✗ | falso | jev | Disse que não está vendo com mais ninguém e não tem pressa; prefere receber opções por e-mail uma vez por sema… |
| SQ-A03 | OB-177 | verdadeiro | 0.73 | 0.73 | — | indecidivel | ✗ | verdadeiro | jev | Vai financiar 70% e já fez 2 visitas com a gente; aguardando laudo do banco. |
| SQ-A03 | OB-184 | falso | 0.41 | 0.52 | — | indecidivel | ✗ | falso | jev | Desistiu: os valores da região passaram do que ele consegue pagar e vai ficar no aluguel atual. |
| SQ-A03 | OB-185 | falso | 0.32 | 0.54 | — | indecidivel | ✗ | falso | jev | Encerrou a busca depois da terceira visita; tudo acima do orçamento dela, não quer mais receber anúncios. |
| SQ-A03 | OB-186 | falso | 0.29 | 0.29 | — | indecidivel | ✗ | falso | jev | Achou o aluguel pedido fora da realidade e desistiu de se mudar por enquanto. |
| SQ-A04 | OB-002 | verdadeiro | 0.55 | 0.92 | — | indecidivel | ✗ | verdadeiro | jev | Está vindo de Belo Horizonte com a família no começo do ano, quer casa com quintal. Orçamento folgado, paga à … |
| SQ-A04 | OB-006 | falso | 0.55 | 0.87 | — | indecidivel | ✗ | falso | jev | Recebeu proposta de emprego em outro estado e vai vender o apto dele aqui pra comprar lá. Pediu avaliação. |
| SQ-A04 | OB-019 | falso | 0.55 | 0.73 | — | indecidivel | ✗ | verdadeiro | jev | Imóvel precisa de reforma geral, infiltração no quarto e piso solto. Cliente descartou na hora. |
| SQ-A04 | OB-037 | verdadeiro | 0.73 | 0.95 | — | indecidivel | ✗ | verdadeiro | jev | Vai pagar à vista, dinheiro da herança já está na conta. Só quer desconto por isso. |
| SQ-A04 | OB-039 | falso | 0.51 | 0.73 | — | indecidivel | ✗ | verdadeiro | jev | Explicou que o financiamento seria pelo nome do pai, que tem renda comprovada. Decisão final é dele mesmo assi… |
| SQ-A04 | OB-040 | verdadeiro | 0.28 | 0.42 | — | indecidivel | ✗ | verdadeiro | jev | Cliente de locação, nada de financiamento no caso dele. Perguntou de seguro-fiança. |
| SQ-A04 | OB-043 | verdadeiro | 0.47 | 0.72 | — | indecidivel | ✗ | verdadeiro | jev | Disse que não precisa financiar, mas que talvez use consórcio contemplado. Avaliar se o vendedor aceita. |
| SQ-A04 | OB-044 | falso | 0.25 | 0.74 | — | indecidivel | ✗ | verdadeiro | jev | Metade financiada, metade com a venda do apto atual. Precisa vender primeiro. |
| SQ-A04 | OB-095 | falso | 0.21 | 0.64 | — | indecidivel | ✗ | falso | jev | Compra pra alugar, quer rendimento acima de 0,5% ao mês; não vai morar. Tem até 450 mil. |
| SQ-A04 | OB-107 | falso | 0.23 | 0.45 | — | indecidivel | ✗ | falso | jev | Fechou com outra imobiliária na semana passada. Agradeceu o atendimento. |
| SQ-A04 | OB-108 | falso | 0.36 | 0.86 | — | indecidivel | ✗ | falso | jev | Disse que pausou a procura até vender o carro. Deve voltar em dois meses. |
| SQ-A04 | OB-118 | falso | 0.36 | 0.71 | — | indecidivel | ✗ | falso | jev | Comentou que a parcela ficaria pesada demais com os juros atuais. |
| SQ-A04 | OB-128 | falso | 0.33 | 0.82 | — | indecidivel | ✗ | verdadeiro | jev | Os pais vão pagar a entrada e querem aprovar o imóvel antes. |
| SQ-A04 | OB-152 | verdadeiro | 0.63 | 0.96 | — | indecidivel | ✗ | verdadeiro | jev | Casal de aposentados mudando de Recife pra ficar perto dos netos; querem apto com elevador e sem escada, e pag… |
| SQ-A04 | OB-159 | verdadeiro | 0.73 | 0.88 | — | indecidivel | ✗ | verdadeiro | jev | Cliente investidor, não vai financiar; quer dois studios reformados pra alugar por temporada. |
| SQ-A04 | OB-166 | falso | 0.30 | 0.51 | — | indecidivel | ✗ | falso | jev | Vai desistir se o banco não aprovar; já foi reprovado uma vez. |
| SQ-A04 | OB-167 | falso | 0.29 | 0.20 | — | indecidivel | ✗ | falso | jev | Cliente de locação achou caro e desistiu; vai continuar na casa dos pais. |
| SQ-A04 | OB-169 | falso | 0.23 | 0.73 | — | indecidivel | ✗ | falso | jev | Fez duas visitas, elogiou a pontualidade da equipe, mas disse que vai esperar o fim do ano por causa dos juros… |
| SQ-A04 | OB-171 | falso | 0.31 | 0.71 | — | indecidivel | ✗ | falso | jev | Investidor com orçamento de 380 mil quer comprar na planta pra revender. |
| SQ-A04 | OB-185 | falso | 0.28 | 0.51 | — | indecidivel | ✗ | falso | jev | Encerrou a busca depois da terceira visita; tudo acima do orçamento dela, não quer mais receber anúncios. |
| SQ-A05 | OB-048 | indecidivel | 0.38 | 0.81 | — | indecidivel | ✓ | verdadeiro | jev | Cliente perguntou das regras do condomínio pra animais, 'por curiosidade'. |
| SQ-A05 | OB-052 | indecidivel | 0.54 | 0.84 | — | indecidivel | ✓ | falso | jev | Perguntou se há pet shop perto do condomínio. |
| SQ-A05 | OB-054 | falso | 0.52 | 0.62 | — | indecidivel | ✗ | falso | jev | Alérgico a pelo, descartou unidade onde o antigo morador tinha gato. |
| SQ-A06 | OB-001 | falso | 0.76 | 0.84 | 0.73, 0.05 | indecidivel | ✗ | falso | jev | Cliente ligou de Curitiba: a empresa transferiu ele pra cá e precisa de apartamento pronto pra morar. Vai fina… |
| SQ-A06 | OB-003 | falso | 0.24 | 0.69 | 0.35, 0.06 | indecidivel | ✗ | falso | jev | Vai sair da cidade em dezembro por causa do mestrado e procura um studio mobiliado lá; quer indicação de parce… |
| SQ-A06 | OB-006 | falso | 0.62 | 0.76 | 0.64, 0.05 | indecidivel | ✗ | verdadeiro | jev | Recebeu proposta de emprego em outro estado e vai vender o apto dele aqui pra comprar lá. Pediu avaliação. |
| SQ-A06 | OB-030 | verdadeiro | 0.77 | 0.88 | 0.89, 0.05 | indecidivel | ✗ | falso | jev | Quer visitar amanhã cedo e assinar na mesma semana se gostar; empresa paga a mudança até o fim do mês. |
| SQ-A06 | OB-031 | indecidivel | 0.12 | 0.62 | 0.20, 0.06 | falso | ✗ | falso | jev | Perguntou qual o prazo médio de entrega das chaves depois da assinatura. |
| SQ-A06 | OB-032 | indecidivel | 0.59 | 0.80 | 0.68, 0.05 | indecidivel | ✓ | falso | jev | Mandou quatro mensagens no mesmo dia pedindo retorno sobre o apto. |
| SQ-A06 | OB-037 | falso | 0.30 | 0.77 | 0.47, 0.05 | indecidivel | ✗ | falso | jev | Vai pagar à vista, dinheiro da herança já está na conta. Só quer desconto por isso. |
| SQ-A06 | OB-038 | falso | 0.53 | 0.79 | 0.13, 0.49 | indecidivel | ✗ | falso | jev | Simulação do Santander deu parcela de 3.800; ela quer tentar no Itaú antes de decidir. |
| SQ-A06 | OB-072 | falso | 0.69 | 0.87 | 0.14, 0.51 | indecidivel | ✗ | falso | jev | Irritado: a visita de ontem foi desmarcada em cima da hora pela segunda vez. Disse que vai procurar em outro l… |
| SQ-A06 | OB-084 | indecidivel | 0.11 | 0.60 | 0.05, 0.16 | falso | ✗ | falso | jev | Mencionou que 'um conhecido' tem um imóvel pra vender direto. Não sei se é concorrência real. |
| SQ-A06 | OB-086 | falso | 0.76 | 0.85 | 0.15, 0.56 | indecidivel | ✗ | verdadeiro | jev | Disse que largou a outra imobiliária porque não respondiam. Agora é só com a gente. |
| SQ-A06 | OB-106 | falso | 0.35 | 0.39 | 0.19, 0.12 | indecidivel | ✗ | falso | jev | Encerrou a busca por enquanto, separação em andamento. |
| SQ-A06 | OB-107 | verdadeiro | 0.34 | 0.60 | 0.16, 0.27 | indecidivel | ✗ | verdadeiro | jev | Fechou com outra imobiliária na semana passada. Agradeceu o atendimento. |
| SQ-A06 | OB-113 | falso | 0.36 | 0.63 | 0.26, 0.06 | indecidivel | ✗ | verdadeiro | jev | Preço dentro do esperado, não reclamou de nada. Vai fazer proposta. |
| SQ-A06 | OB-114 | falso | 0.24 | 0.52 | 0.08, 0.11 | indecidivel | ✗ | falso | jev | Disse que o metro quadrado da região 'está fora da realidade' e que vai olhar mais longe. |
| SQ-A06 | OB-133 | falso | 0.66 | 0.81 | 0.60, 0.05 | indecidivel | ✗ | verdadeiro | jev | É a única compradora; já tem procuração do irmão pra fechar. |
| SQ-A06 | OB-145 | falso | 0.30 | 0.76 | 0.05, 0.40 | indecidivel | ✗ | falso | jev | Visita feita, achou a sala escura. Vai ver outras duas opções na quarta. |
| SQ-A06 | OB-149 | falso | 0.83 | 0.92 | 0.07, 0.86 | verdadeiro | ✗ | falso | jev | Cliente perguntou sobre IPTU e taxa de condomínio da unidade 3 quartos; vai comparar com outra. |
| SQ-A06 | OB-164 | falso | 0.79 | 0.84 | 0.80, 0.05 | indecidivel | ✗ | verdadeiro | jev | Decisão é do marido, que acha tudo caro; ela gostaria de fechar logo. |
| SQ-A06 | OB-176 | falso | 0.56 | 0.85 | 0.62, 0.05 | indecidivel | ✗ | verdadeiro | jev | Precisa de financiamento; visitou 3 unidades em uma tarde e quer proposta na de 2 quartos. |
| SQ-A07 | OB-074 | verdadeiro | 0.76 | 0.87 | — | indecidivel | ✗ | falso | jev | Falou que o anúncio estava com metragem errada e se sentiu enganada. Expliquei e ela aceitou continuar. |
| SQ-A07 | OB-078 | indecidivel | 0.80 | 0.91 | — | verdadeiro | ✗ | falso | jev | Perguntou por que a gente demorou pra responder. Expliquei o feriado, ela entendeu. |
| SQ-A07 | OB-103 | falso | 0.24 | 0.28 | — | indecidivel | ✗ | falso | jev | Desistiu da busca: vai renovar o aluguel atual por mais um ano. Pediu pra tirar da lista. |
| SQ-A07 | OB-126 | falso | 0.31 | 0.89 | — | indecidivel | ✗ | verdadeiro | jev | Reclamou do barulho da obra ao lado durante a visita e pediu outra opção. |
| SQ-A07 | OB-167 | falso | 0.72 | 0.81 | — | indecidivel | ✗ | falso | jev | Cliente de locação achou caro e desistiu; vai continuar na casa dos pais. |
| SQ-A07 | OB-186 | falso | 0.47 | 0.73 | — | indecidivel | ✗ | falso | jev | Achou o aluguel pedido fora da realidade e desistiu de se mudar por enquanto. |
| SQ-A08 | OB-066 | indecidivel | 0.16 | 0.73 | — | falso | ✗ | falso | jev | Pediu que o apto tivesse 'um quarto sobrando'. Não disse pra quê. |
| SQ-A08 | OB-068 | indecidivel | 0.20 | 0.78 | — | falso | ✗ | falso | jev | Perguntou se a região tem boa cobertura de internet. |
| SQ-A08 | OB-120 | falso | 0.27 | 0.52 | — | indecidivel | ✗ | verdadeiro | jev | Preocupada com barulho: trabalha à noite e dorme de dia; descartou apto de frente pra avenida. |
| SQ-A08 | OB-125 | falso | 0.24 | 0.63 | — | indecidivel | ✗ | verdadeiro | jev | Músico, toca bateria em casa; precisa de vizinhança tolerante ou casa isolada. |
| SQ-A09 | OB-008 | falso | 0.77 | 0.90 | — | indecidivel | ✗ | falso | jev | Cliente comentou que a filha vai prestar vestibular em São Paulo; por enquanto procura só pra ele aqui, 2 quar… |
| SQ-A09 | OB-016 | falso | 0.24 | 0.75 | — | indecidivel | ✗ | falso | jev | Visita no sobrado: fachada pintada agora, box e louças novas, só a área de serviço ficou original. Vai pensar. |
| SQ-A09 | OB-018 | falso | 0.54 | 0.82 | — | indecidivel | ✗ | falso | jev | A casa está com tudo renovado, dono trocou até o telhado em 2025. Cliente só achou pequeno pra família. |
| SQ-A09 | OB-019 | falso | 0.89 | 0.87 | — | verdadeiro | ✗ | falso | jev | Imóvel precisa de reforma geral, infiltração no quarto e piso solto. Cliente descartou na hora. |
| SQ-A09 | OB-033 | falso | 0.60 | 0.85 | — | indecidivel | ✗ | falso | jev | Comentou que o aluguel dele vence em maio do ano que vem; está só olhando o mercado. |
| SQ-A09 | OB-070 | falso | 0.26 | 0.69 | — | indecidivel | ✗ | falso | jev | Comentou que largou o home office e voltou pro presencial, então pode ser menor. |
| SQ-A09 | OB-076 | falso | 0.35 | 0.74 | — | indecidivel | ✗ | falso | jev | Não gostou do tom do corretor anterior; pediu pra ser atendido por outra pessoa. |
| SQ-A09 | OB-077 | falso | 0.33 | 0.76 | — | indecidivel | ✗ | falso | jev | Achou tudo ótimo no atendimento, só o imóvel que não serviu. |
| SQ-A09 | OB-082 | falso | 0.28 | 0.72 | — | indecidivel | ✗ | falso | jev | Viu um apto parecido com outro corretor na mesma rua por 40 mil a menos. Pediu pra cobrir. |
| SQ-A09 | OB-083 | falso | 0.37 | 0.65 | — | indecidivel | ✗ | falso | jev | Só está vendo com a gente, por indicação de um amigo; não procurou mais ninguém. |
| SQ-A09 | OB-091 | falso | 0.37 | 0.62 | — | indecidivel | ✗ | falso | jev | Teve cirurgia no joelho e por enquanto não consegue subir escada; prefere térreo. |
| SQ-A09 | OB-100 | falso | 0.30 | 0.74 | — | indecidivel | ✗ | falso | jev | Compra pro filho morar durante a faculdade e depois decide se aluga. |
| SQ-A09 | OB-104 | indecidivel | 0.70 | 0.91 | — | indecidivel | ✓ | falso | jev | Depois de 3 visitas, parou de responder. Última mensagem dela foi 'vou pensar'. |
| SQ-A09 | OB-126 | falso | 0.21 | 0.69 | — | indecidivel | ✗ | falso | jev | Reclamou do barulho da obra ao lado durante a visita e pediu outra opção. |
| SQ-A09 | OB-127 | falso | 0.44 | 0.80 | — | indecidivel | ✗ | falso | jev | Ele gostou, mas quem bate o martelo é a esposa, que só volta de viagem semana que vem. |
| SQ-A09 | OB-145 | falso | 0.55 | 0.74 | — | indecidivel | ✗ | falso | jev | Visita feita, achou a sala escura. Vai ver outras duas opções na quarta. |
| SQ-A09 | OB-155 | falso | 0.24 | 0.76 | — | indecidivel | ✗ | falso | jev | Reclamou que o anúncio dizia 'reformado' e o apto está com piso de 30 anos; se sentiu enrolado. |
| SQ-A09 | OB-169 | indecidivel | 0.70 | 0.90 | — | indecidivel | ✓ | falso | jev | Fez duas visitas, elogiou a pontualidade da equipe, mas disse que vai esperar o fim do ano por causa dos juros… |
| SQ-A09 | OB-174 | falso | 0.88 | 0.92 | — | verdadeiro | ✗ | falso | jev | Disse que não está vendo com mais ninguém e não tem pressa; prefere receber opções por e-mail uma vez por sema… |
