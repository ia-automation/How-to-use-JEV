# Resultados — sql-semantico

Gerado por `run.py` em 2026-10-02 (modo `gravado`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; separação da condição, filtro, validação, decisão e baseline: `sql.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Teto do texto: 2000 caracteres (acima → indecidivel, sem chamada). Orçamento: 3500 requisições no teste.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (18 condições × 187 linhas), com a política acima; **1_f1**: F1 do Jev sobre as decidíveis decididas ≥ 0,85 e ≥ F1 do baseline (LIKE) + 0,15; **2_perdidas**: linha verdadeira do gabarito que saiu `falso` ≤ 5% das verdadeiras; **3_negacao**: linha falsa marcada `verdadeiro` em condição de negação ≤ 2; **4_humano**: decidíveis mandadas a humano (`indecidivel`) ≤ 8%; **secundario_nao_decide**: indecidíveis do gabarito que foram a humano ≥ 50%; falha operacional = 0; **se_falhar**: 1 falhando = o LIKE basta ou o Jev não lê a condição; 2 ou 3 = o filtro perde ou inverte o que deveria achar (não serve sem mudança); 4 = custa humano demais

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-02T00:05:23-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 ca1f9374f7123aa5… · `sql.py` sha256 9852132b9f2c9e1b… · `run.py` sha256 925d91a4b370df76… · `dados/linhas.json` sha256 b11253f810da103e… · `dados/condicoes_teste.json` sha256 2310fb5836605d52…

## Lado a lado

| conjunto | variante | decidíveis | decididas | P | R | F1 | F1 com V a humano = perdidas | humano (decidíveis) | V a humano | F a humano | PERDIDAS (V → falso) | FP EM NEGAÇÃO | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | Jev (oficial) | 1669 | 1591 | 0.970 | 0.985 | 0.977 | 0.895 | 78 (0.047) | 12 | 66 | 1/77 | 0 | 9/14 (V: 1) | 0 |
| ajuste | baseline LIKE | 1669 | 1669 | 0.364 | 0.558 | 0.441 | 0.441 | 0 (0.000) | 0 | 0 | 34/77 | 27 | 0/14 (V: 1) | 0 |
| teste | Jev (oficial) | 3339 | 3151 | 0.980 | 0.980 | 0.980 | 0.843 | 188 (0.056) | 32 | 156 | 2/131 | 1 | 15/27 (V: 1) | 0 |
| teste | baseline LIKE | 3339 | 3339 | 0.293 | 0.626 | 0.399 | 0.399 | 0 (0.000) | 0 | 0 | 49/131 | 17 | 0/27 (V: 7) | 0 |

| conjunto | condições | difíceis | linhas | requisições | p50_ms | p95_ms | tokens_por_requisicao | US$_por_1000_linhas | modelo |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | 9 | 8 | 187 | 1303 | 249 | 308 | 1083 | 0.0352 | jev-1.13.0 |
| teste | 18 | 12 | 187 | 2665 | 255 | 317 | 1131 | 0.0376 | jev-1.13.0 |

## Conjunto `ajuste` — 9 condições × 187 linhas (arquivo versão 2026-10-01, autor fable); 8 difíceis; 77 verdadeiras e 14 indecidíveis no gabarito

### Total (micro, sobre as linhas decidíveis de todas as condições) — Jev × variantes × baseline LIKE

P/R/F1 sobre as decidíveis que o sistema DECIDIU; `humano` = decidíveis mandadas a `indecidivel` (fora de P/R/F1), separadas em `V a humano` e `F a humano`; `F1 com V a humano = perdidas` conta só as verdadeiras mandadas a humano como perdidas (as falsas a humano não o alteram). **PERDIDAS** = verdadeira do gabarito que saiu `falso` (o filtro perdeu a linha). **FP EM NEGAÇÃO** = falsa marcada `verdadeiro` numa condição da família negação (o erro do LIKE). `indecidíveis → humano` = linhas de pista fraca do gabarito que o sistema mandou revisar (e quantas virou `verdadeiro`). Variante oficial: `clausulas` + pista; faixa de `stated` 0.3–0.8; `hinted` ≥ 0.7.

| variante | decidíveis | decididas | P | R | F1 | F1 com V a humano = perdidas | humano (decidíveis) | V a humano | F a humano | PERDIDAS (V → falso) | FP EM NEGAÇÃO | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev (oficial) | 1669 | 1591 | 0.970 | 0.985 | 0.977 | 0.895 | 78 (0.047) | 12 | 66 | 1/77 | 0 | 9/14 (V: 1) | 0 |
| Jev: inteira | 1669 | 1607 | 0.952 | 0.984 | 0.968 | 0.857 | 62 (0.037) | 16 | 46 | 1/77 | 0 | 5/14 (V: 1) | 0 |
| Jev: inteira+pista | 1669 | 1589 | 0.952 | 0.984 | 0.968 | 0.857 | 80 (0.048) | 16 | 64 | 1/77 | 0 | 9/14 (V: 1) | 0 |
| Jev: cláusulas | 1669 | 1610 | 0.970 | 0.985 | 0.977 | 0.895 | 59 (0.035) | 12 | 47 | 1/77 | 0 | 5/14 (V: 1) | 0 |
| Jev: cláusulas+pista | 1669 | 1591 | 0.970 | 0.985 | 0.977 | 0.895 | 78 (0.047) | 12 | 66 | 1/77 | 0 | 9/14 (V: 1) | 0 |
| baseline LIKE | 1669 | 1669 | 0.364 | 0.558 | 0.441 | 0.441 | 0 (0.000) | 0 | 0 | 34/77 | 27 | 0/14 (V: 1) | 0 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 F1 (decididas) | 0.977 (baseline 0.441) | ≥ 0.85 e ≥ 0.591 | ✓ |
| 2 perdidas (V → falso) | 1/77 (0.013) | ≤ 0.05 | ✓ |
| 3 FP em negação | 0 | ≤ 2 | ✓ |
| 4 humano (decidíveis) | 78/1669 (0.047) | ≤ 0.08 | ✓ |
| secundário: indecidíveis → humano | 9/14 | ≥ 0.5 | ✓ |
| secundário: falhas operacionais | 0 | 0 | ✓ |

### Por condição

`filtro` = parte de campo resolvida pelo código; `chamadas` = linhas que passaram no filtro e foram ao Jev; `V/I` = verdadeiras / indecidíveis do gabarito; `base` = baseline LIKE (radicais entre colchetes).

| id | família | filtro | composta | chamadas | V/I | P | R | F1 | humano | perdidas | FP | I → humano | base F1 | base FP | base perdidas | LIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SQ-A01 | inferência fraca | — | — | 187 | 13/2 | 1.000 | 1.000 | 1.000 | 9 | 0 | 0 | 1/2 | 0.235 | 2 | 11 | [mudar, cidad] |
| SQ-A02 | negação | — | — | 187 | 9/2 | 1.000 | 1.000 | 1.000 | 3 | 0 | 0 | 1/2 | 0.571 | 6 | 3 | [recem, refor] |
| SQ-A03 | composta | orcamento <= 500000 | — | 97 | 6/0 | 1.000 | 1.000 | 1.000 | 11 | 0 | 0 | 0/0 | 0.769 | 2 | 1 | [depen, finan, banca] |
| SQ-A04 | negação | — | — | 187 | 7/0 | 1.000 | 1.000 | 1.000 | 15 | 0 | 0 | 0/0 | 0.400 | 21 | 0 | [desca, finan, pagar, recur, propr, vista, heran, venda] |
| SQ-A05 | fácil | canal = whatsapp | — | 97 | 6/2 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 2/2 | 0.000 | 1 | 6 | [anima, estim] |
| SQ-A06 | composta | — | OU | 187 | 19/3 | 1.000 | 0.941 | 0.970 | 14 | 1 | 0 | 1/3 | 0.444 | 9 | 11 | [urgen, fecha, avali, propo, imobi] |
| SQ-A07 | composta | finalidade = locacao | — | 64 | 4/1 | 1.000 | 1.000 | 1.000 | 7 | 0 | 0 | 0/1 | 0.600 | 3 | 1 | [recla, atend] |
| SQ-A08 | inferência fraca | — | — | 187 | 7/2 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 2/2 | 0.333 | 28 | 0 | [traba, casa, home, offic, remot, consu, virtu] |
| SQ-A09 | inferência fraca | visitas >= 1 | — | 110 | 6/2 | 0.750 | 1.000 | 0.857 | 17 | 0 | 2 | 2/2 | 0.714 | 3 | 1 | [desis, busca, encer] |

### Por família difícil (pela `nota` do rotulador)

| família | condições | F1 Jev | F1 baseline | humano Jev | perdidas Jev | FP Jev | perdidas base | FP base | I → humano |
|---|---|---|---|---|---|---|---|---|---|
| inferência fraca | 3 | 0.960 | 0.384 | 27 | 0 | 2 | 12 | 33 | 5/6 |
| negação | 2 | 1.000 | 0.464 | 18 | 0 | 0 | 3 | 27 | 1/2 |
| composta | 3 | 0.980 | 0.542 | 32 | 1 | 0 | 13 | 14 | 1/4 |
| fácil | 1 | 1.000 | 0.000 | 1 | 0 | 0 | 6 | 1 | 2/2 |

### Onde `stated` cai, por gabarito (só linhas que foram ao Jev)

| gabarito | n | stated mín | p10 | p50 | p90 | máx | ≤ 0,2 | 0,2–0,8 | ≥ 0,8 | hinted p50 | hinted ≥ 0,8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| verdadeiro | 77 | 0.160 | 0.610 | 0.900 | 0.970 | 0.970 | 1 | 16 | 60 | 0.950 | 73 |
| falso | 1212 | 0.020 | 0.030 | 0.060 | 0.190 | 0.900 | 1105 | 104 | 3 | 0.170 | 22 |
| indecidivel | 14 | 0.060 | 0.120 | 0.280 | 0.620 | 0.840 | 5 | 8 | 1 | 0.800 | 8 |

### Cobertura × erro por faixa de `stated` (variante oficial; mesmas respostas, outra faixa)

| faixa | cobertura (decididas/decidíveis) | erro entre decididas | F1 | humano | perdidas | FP em negação | I → humano |
|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.953 | 0.002 | 0.977 | 78 | 1 | 0 | 9/14 |
| 0.5–0.5 | 0.979 | 0.010 | 0.896 | 35 | 2 | 1 | 6/14 |
| 0.4–0.6 | 0.973 | 0.009 | 0.909 | 45 | 2 | 1 | 7/14 |
| 0.3–0.7 | 0.957 | 0.004 | 0.958 | 71 | 1 | 1 | 9/14 |
| 0.2–0.8 | 0.925 | 0.002 | 0.977 | 126 | 1 | 0 | 11/14 |
| 0.1–0.9 | 0.829 | 0.001 | 0.978 | 286 | 1 | 0 | 13/14 |

### Custo e latência (medidos na chamada real; do cache também)

| linhas avaliadas (cond × linha) | sem chamada (filtro) | requisicoes | novas (não cache) | textos longos (sem chamada) | falhas operacionais (→ indecidivel) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_1000_linhas_avaliadas | US$_por_1000_requisicoes | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1683 | 380 | 1303 | 0 | 0 | 0 | 2980 | 249 | 308 | 1083 | 0.059260 | 0.0352 | 0.0455 | jev-1.13.0 |

### Caso a caso — erros, linhas mandadas a humano e indecidíveis do gabarito

`st`/`hi` = Nouls `stated` e `hinted`; `partes` = Nouls por cláusula (compostas); `saída` = variante oficial; `base` = LIKE.

| cond | linha | gab | st | hi | partes | saída | ok | base | por | texto |
|---|---|---|---|---|---|---|---|---|---|---|
| SQ-A01 | OB-008 | indecidivel | 0.22 | 0.55 | — | falso | ✗ | falso | jev | Cliente comentou que a filha vai prestar vestibular em São Paulo; por enquanto procura só pra ele aqui, 2 quar… |
| SQ-A01 | OB-009 | indecidivel | 0.28 | 0.80 | — | indecidivel | ✓ | falso | jev | Perguntou se o condomínio tem portaria 24h e se a região é bem servida de ônibus pra rodoviária. |
| SQ-A01 | OB-028 | falso | 0.25 | 0.74 | — | indecidivel | ✗ | falso | jev | Pediu pra agilizar a documentação porque o bebê nasce em janeiro e quer estar instalada antes. |
| SQ-A01 | OB-055 | falso | 0.23 | 0.78 | — | indecidivel | ✗ | falso | jev | Grávida de 6 meses, quer 3 quartos e escola perto. Marido vai ver as opções no fim de semana. |
| SQ-A01 | OB-114 | falso | 0.54 | 0.83 | — | indecidivel | ✗ | falso | jev | Disse que o metro quadrado da região 'está fora da realidade' e que vai olhar mais longe. |
| SQ-A01 | OB-138 | falso | 0.26 | 0.72 | — | indecidivel | ✗ | falso | jev | Marido trabalha na zona norte e ela na zona sul; querem algo no meio do caminho. |
| SQ-A01 | OB-163 | falso | 0.38 | 0.68 | — | indecidivel | ✗ | falso | jev | Mãe idosa com dificuldade de locomoção vai morar junto, e o apto da rua de trás tem obra que não acaba: quer t… |
| SQ-A01 | OB-178 | verdadeiro | 0.58 | 0.90 | — | indecidivel | ✗ | verdadeiro | jev | Mudança de cidade confirmada pra março e precisa resolver o aluguel antes de fevereiro; orçamento até 3 mil. |
| SQ-A01 | OB-181 | falso | 0.60 | 0.88 | — | indecidivel | ✗ | falso | jev | Trouxe o pai de 79 anos pra morar junto e procura locação de térreo com banheiro adaptado. |
| SQ-A01 | OB-184 | falso | 0.31 | 0.30 | — | indecidivel | ✗ | falso | jev | Desistiu: os valores da região passaram do que ele consegue pagar e vai ficar no aluguel atual. |
| SQ-A01 | OB-186 | falso | 0.66 | 0.77 | — | indecidivel | ✗ | verdadeiro | jev | Achou o aluguel pedido fora da realidade e desistiu de se mudar por enquanto. |
| SQ-A02 | OB-001 | falso | 0.15 | 0.71 | — | indecidivel | ✗ | falso | jev | Cliente ligou de Curitiba: a empresa transferiu ele pra cá e precisa de apartamento pronto pra morar. Vai fina… |
| SQ-A02 | OB-022 | indecidivel | 0.43 | 0.83 | — | indecidivel | ✓ | falso | jev | O proprietário disse que trocou o chuveiro e pintou um quarto antes de anunciar. Cliente quer ver pessoalmente… |
| SQ-A02 | OB-023 | indecidivel | 0.06 | 0.40 | — | falso | ✗ | falso | jev | Fotos mostram piso cerâmico claro e paredes brancas; não sei se é recente ou só limpo. Cliente pediu visita. |
| SQ-A02 | OB-155 | falso | 0.48 | 0.84 | — | indecidivel | ✗ | verdadeiro | jev | Reclamou que o anúncio dizia 'reformado' e o apto está com piso de 30 anos; se sentiu enrolado. |
| SQ-A02 | OB-159 | verdadeiro | 0.37 | 0.70 | — | indecidivel | ✗ | verdadeiro | jev | Cliente investidor, não vai financiar; quer dois studios reformados pra alugar por temporada. |
| SQ-A03 | OB-035 | verdadeiro | 0.54 | 0.85 | — | indecidivel | ✗ | verdadeiro | jev | Depende de aprovação do banco; a renda dele é informal e isso pode travar. Pedi documentos. |
| SQ-A03 | OB-039 | verdadeiro | 0.73 | 0.86 | — | indecidivel | ✗ | verdadeiro | jev | Explicou que o financiamento seria pelo nome do pai, que tem renda comprovada. Decisão final é dele mesmo assi… |
| SQ-A03 | OB-045 | falso | 0.36 | 0.25 | — | indecidivel | ✗ | falso | jev | Tem um gato e um cachorro pequeno; prédio precisa aceitar bichos, isso é inegociável. |
| SQ-A03 | OB-063 | falso | 0.37 | 0.49 | — | indecidivel | ✗ | falso | jev | Trabalha de casa 100%, precisa de um cômodo isolado com porta pra reuniões. Internet fibra é condição. |
| SQ-A03 | OB-088 | falso | 0.32 | 0.26 | — | indecidivel | ✗ | falso | jev | Cadeirante, só considera unidades com porta larga no banheiro e vaga coberta perto do elevador. |
| SQ-A03 | OB-094 | falso | 0.31 | 0.25 | — | indecidivel | ✗ | falso | jev | Filho autista precisa de ambiente tranquilo e sem escada aberta; busca casa térrea em rua calma. |
| SQ-A03 | OB-096 | falso | 0.35 | 0.57 | — | indecidivel | ✗ | falso | jev | Quer um studio perto da faculdade pra colocar no Airbnb, até 420 mil. Já tem outros dois. |
| SQ-A03 | OB-109 | falso | 0.43 | 0.52 | — | indecidivel | ✗ | falso | jev | Não desistiu, mas reduziu o orçamento pra 350 mil depois da demissão da esposa. |
| SQ-A03 | OB-134 | falso | 0.31 | 0.26 | — | indecidivel | ✗ | falso | jev | Quer até 20 minutos a pé do hospital onde trabalha, plantão noturno. |
| SQ-A03 | OB-162 | falso | 0.31 | 0.30 | — | indecidivel | ✗ | falso | jev | Avaliando uma proposta nossa e outra de um corretor autônomo; falou que o nosso atendimento foi 'nota dez' até… |
| SQ-A03 | OB-184 | falso | 0.51 | 0.48 | — | indecidivel | ✗ | falso | jev | Desistiu: os valores da região passaram do que ele consegue pagar e vai ficar no aluguel atual. |
| SQ-A04 | OB-002 | verdadeiro | 0.59 | 0.93 | — | indecidivel | ✗ | verdadeiro | jev | Está vindo de Belo Horizonte com a família no começo do ano, quer casa com quintal. Orçamento folgado, paga à … |
| SQ-A04 | OB-006 | falso | 0.35 | 0.86 | — | indecidivel | ✗ | falso | jev | Recebeu proposta de emprego em outro estado e vai vender o apto dele aqui pra comprar lá. Pediu avaliação. |
| SQ-A04 | OB-019 | falso | 0.72 | 0.73 | — | indecidivel | ✗ | verdadeiro | jev | Imóvel precisa de reforma geral, infiltração no quarto e piso solto. Cliente descartou na hora. |
| SQ-A04 | OB-037 | verdadeiro | 0.69 | 0.93 | — | indecidivel | ✗ | verdadeiro | jev | Vai pagar à vista, dinheiro da herança já está na conta. Só quer desconto por isso. |
| SQ-A04 | OB-039 | falso | 0.49 | 0.63 | — | indecidivel | ✗ | verdadeiro | jev | Explicou que o financiamento seria pelo nome do pai, que tem renda comprovada. Decisão final é dele mesmo assi… |
| SQ-A04 | OB-040 | verdadeiro | 0.32 | 0.57 | — | indecidivel | ✗ | verdadeiro | jev | Cliente de locação, nada de financiamento no caso dele. Perguntou de seguro-fiança. |
| SQ-A04 | OB-043 | verdadeiro | 0.47 | 0.76 | — | indecidivel | ✗ | verdadeiro | jev | Disse que não precisa financiar, mas que talvez use consórcio contemplado. Avaliar se o vendedor aceita. |
| SQ-A04 | OB-101 | falso | 0.20 | 0.70 | — | indecidivel | ✗ | falso | jev | Fundo familiar comprando pra renda, orçamento de 2 milhões em até 3 unidades. |
| SQ-A04 | OB-108 | falso | 0.34 | 0.86 | — | indecidivel | ✗ | falso | jev | Disse que pausou a procura até vender o carro. Deve voltar em dois meses. |
| SQ-A04 | OB-118 | falso | 0.24 | 0.78 | — | indecidivel | ✗ | falso | jev | Comentou que a parcela ficaria pesada demais com os juros atuais. |
| SQ-A04 | OB-128 | falso | 0.31 | 0.80 | — | indecidivel | ✗ | verdadeiro | jev | Os pais vão pagar a entrada e querem aprovar o imóvel antes. |
| SQ-A04 | OB-152 | verdadeiro | 0.64 | 0.96 | — | indecidivel | ✗ | verdadeiro | jev | Casal de aposentados mudando de Recife pra ficar perto dos netos; querem apto com elevador e sem escada, e pag… |
| SQ-A04 | OB-167 | falso | 0.46 | 0.51 | — | indecidivel | ✗ | falso | jev | Cliente de locação achou caro e desistiu; vai continuar na casa dos pais. |
| SQ-A04 | OB-171 | falso | 0.26 | 0.72 | — | indecidivel | ✗ | falso | jev | Investidor com orçamento de 380 mil quer comprar na planta pra revender. |
| SQ-A04 | OB-185 | falso | 0.31 | 0.45 | — | indecidivel | ✗ | falso | jev | Encerrou a busca depois da terceira visita; tudo acima do orçamento dela, não quer mais receber anúncios. |
| SQ-A05 | OB-048 | indecidivel | 0.26 | 0.80 | — | indecidivel | ✓ | verdadeiro | jev | Cliente perguntou das regras do condomínio pra animais, 'por curiosidade'. |
| SQ-A05 | OB-052 | indecidivel | 0.40 | 0.89 | — | indecidivel | ✓ | falso | jev | Perguntou se há pet shop perto do condomínio. |
| SQ-A05 | OB-054 | falso | 0.43 | 0.72 | — | indecidivel | ✗ | falso | jev | Alérgico a pelo, descartou unidade onde o antigo morador tinha gato. |
| SQ-A06 | OB-001 | falso | 0.68 | 0.84 | 0.63, 0.05 | indecidivel | ✗ | falso | jev | Cliente ligou de Curitiba: a empresa transferiu ele pra cá e precisa de apartamento pronto pra morar. Vai fina… |
| SQ-A06 | OB-003 | falso | 0.22 | 0.56 | 0.33, 0.05 | indecidivel | ✗ | falso | jev | Vai sair da cidade em dezembro por causa do mestrado e procura um studio mobiliado lá; quer indicação de parce… |
| SQ-A06 | OB-006 | falso | 0.52 | 0.80 | 0.48, 0.05 | indecidivel | ✗ | verdadeiro | jev | Recebeu proposta de emprego em outro estado e vai vender o apto dele aqui pra comprar lá. Pediu avaliação. |
| SQ-A06 | OB-031 | indecidivel | 0.16 | 0.63 | 0.25, 0.05 | falso | ✗ | falso | jev | Perguntou qual o prazo médio de entrega das chaves depois da assinatura. |
| SQ-A06 | OB-032 | indecidivel | 0.44 | 0.81 | 0.59, 0.04 | indecidivel | ✓ | falso | jev | Mandou quatro mensagens no mesmo dia pedindo retorno sobre o apto. |
| SQ-A06 | OB-037 | falso | 0.28 | 0.67 | 0.40, 0.06 | indecidivel | ✗ | falso | jev | Vai pagar à vista, dinheiro da herança já está na conta. Só quer desconto por isso. |
| SQ-A06 | OB-038 | falso | 0.54 | 0.76 | 0.17, 0.42 | indecidivel | ✗ | falso | jev | Simulação do Santander deu parcela de 3.800; ela quer tentar no Itaú antes de decidir. |
| SQ-A06 | OB-072 | falso | 0.64 | 0.86 | 0.15, 0.43 | indecidivel | ✗ | falso | jev | Irritado: a visita de ontem foi desmarcada em cima da hora pela segunda vez. Disse que vai procurar em outro l… |
| SQ-A06 | OB-084 | indecidivel | 0.12 | 0.58 | 0.05, 0.13 | falso | ✗ | falso | jev | Mencionou que 'um conhecido' tem um imóvel pra vender direto. Não sei se é concorrência real. |
| SQ-A06 | OB-086 | falso | 0.34 | 0.88 | 0.12, 0.30 | indecidivel | ✗ | verdadeiro | jev | Disse que largou a outra imobiliária porque não respondiam. Agora é só com a gente. |
| SQ-A06 | OB-107 | verdadeiro | 0.16 | 0.50 | 0.08, 0.10 | falso | ✗ | verdadeiro | jev | Fechou com outra imobiliária na semana passada. Agradeceu o atendimento. |
| SQ-A06 | OB-133 | falso | 0.48 | 0.81 | 0.50, 0.05 | indecidivel | ✗ | verdadeiro | jev | É a única compradora; já tem procuração do irmão pra fechar. |
| SQ-A06 | OB-145 | falso | 0.37 | 0.69 | 0.07, 0.32 | indecidivel | ✗ | falso | jev | Visita feita, achou a sala escura. Vai ver outras duas opções na quarta. |
| SQ-A06 | OB-149 | falso | 0.80 | 0.92 | 0.08, 0.78 | indecidivel | ✗ | falso | jev | Cliente perguntou sobre IPTU e taxa de condomínio da unidade 3 quartos; vai comparar com outra. |
| SQ-A06 | OB-154 | verdadeiro | 0.71 | 0.88 | 0.77, 0.04 | indecidivel | ✗ | falso | jev | Estudante vindo de Goiânia, precisa alugar antes das aulas em fevereiro; os pais assinam o contrato. |
| SQ-A06 | OB-164 | falso | 0.66 | 0.81 | 0.77, 0.05 | indecidivel | ✗ | verdadeiro | jev | Decisão é do marido, que acha tudo caro; ela gostaria de fechar logo. |
| SQ-A06 | OB-176 | falso | 0.39 | 0.82 | 0.46, 0.05 | indecidivel | ✗ | verdadeiro | jev | Precisa de financiamento; visitou 3 unidades em uma tarde e quer proposta na de 2 quartos. |
| SQ-A06 | OB-180 | verdadeiro | 0.61 | 0.81 | 0.73, 0.05 | indecidivel | ✗ | falso | jev | Precisa alugar até o dia 15, quando entrega as chaves do atual; aceita sem mobília. |
| SQ-A07 | OB-019 | falso | 0.34 | 0.33 | — | indecidivel | ✗ | falso | jev | Imóvel precisa de reforma geral, infiltração no quarto e piso solto. Cliente descartou na hora. |
| SQ-A07 | OB-078 | indecidivel | 0.84 | 0.91 | — | verdadeiro | ✗ | falso | jev | Perguntou por que a gente demorou pra responder. Expliquei o feriado, ela entendeu. |
| SQ-A07 | OB-103 | falso | 0.47 | 0.34 | — | indecidivel | ✗ | falso | jev | Desistiu da busca: vai renovar o aluguel atual por mais um ano. Pediu pra tirar da lista. |
| SQ-A07 | OB-119 | falso | 0.32 | 0.68 | — | indecidivel | ✗ | falso | jev | Pediu um imóvel 'mais em conta' que os três que mostrei. |
| SQ-A07 | OB-121 | falso | 0.24 | 0.70 | — | indecidivel | ✗ | falso | jev | Perguntou se há bar ou casa noturna na rua. Mora hoje em cima de um e não aguenta mais. |
| SQ-A07 | OB-126 | falso | 0.68 | 0.90 | — | indecidivel | ✗ | verdadeiro | jev | Reclamou do barulho da obra ao lado durante a visita e pediu outra opção. |
| SQ-A07 | OB-167 | falso | 0.63 | 0.65 | — | indecidivel | ✗ | falso | jev | Cliente de locação achou caro e desistiu; vai continuar na casa dos pais. |
| SQ-A07 | OB-186 | falso | 0.65 | 0.79 | — | indecidivel | ✗ | falso | jev | Achou o aluguel pedido fora da realidade e desistiu de se mudar por enquanto. |
| SQ-A08 | OB-064 | verdadeiro | 0.79 | 0.94 | — | indecidivel | ✗ | verdadeiro | jev | Faz atendimento online de manhã, então quer um canto silencioso pra montar o consultório virtual. |
| SQ-A08 | OB-066 | indecidivel | 0.13 | 0.73 | — | indecidivel | ✓ | falso | jev | Pediu que o apto tivesse 'um quarto sobrando'. Não disse pra quê. |
| SQ-A08 | OB-068 | indecidivel | 0.19 | 0.74 | — | indecidivel | ✓ | falso | jev | Perguntou se a região tem boa cobertura de internet. |
| SQ-A09 | OB-006 | falso | 0.21 | 0.76 | — | indecidivel | ✗ | falso | jev | Recebeu proposta de emprego em outro estado e vai vender o apto dele aqui pra comprar lá. Pediu avaliação. |
| SQ-A09 | OB-008 | falso | 0.63 | 0.89 | — | indecidivel | ✗ | falso | jev | Cliente comentou que a filha vai prestar vestibular em São Paulo; por enquanto procura só pra ele aqui, 2 quar… |
| SQ-A09 | OB-014 | falso | 0.16 | 0.73 | — | indecidivel | ✗ | falso | jev | Mostrei a casa do Jardim Europa, toda repaginada pelo dono há uns meses, janelas e portas trocadas. Ela achou … |
| SQ-A09 | OB-016 | falso | 0.31 | 0.78 | — | indecidivel | ✗ | falso | jev | Visita no sobrado: fachada pintada agora, box e louças novas, só a área de serviço ficou original. Vai pensar. |
| SQ-A09 | OB-018 | falso | 0.25 | 0.80 | — | indecidivel | ✗ | falso | jev | A casa está com tudo renovado, dono trocou até o telhado em 2025. Cliente só achou pequeno pra família. |
| SQ-A09 | OB-019 | falso | 0.90 | 0.90 | — | verdadeiro | ✗ | falso | jev | Imóvel precisa de reforma geral, infiltração no quarto e piso solto. Cliente descartou na hora. |
| SQ-A09 | OB-033 | falso | 0.45 | 0.86 | — | indecidivel | ✗ | falso | jev | Comentou que o aluguel dele vence em maio do ano que vem; está só olhando o mercado. |
| SQ-A09 | OB-076 | falso | 0.34 | 0.76 | — | indecidivel | ✗ | falso | jev | Não gostou do tom do corretor anterior; pediu pra ser atendido por outra pessoa. |
| SQ-A09 | OB-077 | falso | 0.23 | 0.74 | — | indecidivel | ✗ | falso | jev | Achou tudo ótimo no atendimento, só o imóvel que não serviu. |
| SQ-A09 | OB-082 | falso | 0.18 | 0.77 | — | indecidivel | ✗ | falso | jev | Viu um apto parecido com outro corretor na mesma rua por 40 mil a menos. Pediu pra cobrir. |
| SQ-A09 | OB-091 | falso | 0.34 | 0.62 | — | indecidivel | ✗ | falso | jev | Teve cirurgia no joelho e por enquanto não consegue subir escada; prefere térreo. |
| SQ-A09 | OB-098 | falso | 0.15 | 0.72 | — | indecidivel | ✗ | falso | jev | Perguntou quanto o imóvel renderia de aluguel, 'só pra saber'. Vai morar nele. |
| SQ-A09 | OB-100 | falso | 0.35 | 0.75 | — | indecidivel | ✗ | falso | jev | Compra pro filho morar durante a faculdade e depois decide se aluga. |
| SQ-A09 | OB-104 | indecidivel | 0.62 | 0.92 | — | indecidivel | ✓ | falso | jev | Depois de 3 visitas, parou de responder. Última mensagem dela foi 'vou pensar'. |
| SQ-A09 | OB-112 | falso | 0.12 | 0.70 | — | indecidivel | ✗ | falso | jev | Achou o valor do condomínio um absurdo, 1.400 por mês num prédio sem lazer. |
| SQ-A09 | OB-126 | falso | 0.24 | 0.71 | — | indecidivel | ✗ | falso | jev | Reclamou do barulho da obra ao lado durante a visita e pediu outra opção. |
| SQ-A09 | OB-127 | falso | 0.30 | 0.83 | — | indecidivel | ✗ | falso | jev | Ele gostou, mas quem bate o martelo é a esposa, que só volta de viagem semana que vem. |
| SQ-A09 | OB-145 | falso | 0.44 | 0.84 | — | indecidivel | ✗ | falso | jev | Visita feita, achou a sala escura. Vai ver outras duas opções na quarta. |
| SQ-A09 | OB-155 | falso | 0.14 | 0.74 | — | indecidivel | ✗ | falso | jev | Reclamou que o anúncio dizia 'reformado' e o apto está com piso de 30 anos; se sentiu enrolado. |
| SQ-A09 | OB-169 | indecidivel | 0.62 | 0.90 | — | indecidivel | ✓ | falso | jev | Fez duas visitas, elogiou a pontualidade da equipe, mas disse que vai esperar o fim do ano por causa dos juros… |
| SQ-A09 | OB-174 | falso | 0.80 | 0.91 | — | verdadeiro | ✗ | falso | jev | Disse que não está vendo com mais ninguém e não tem pressa; prefere receber opções por e-mail uma vez por sema… |

## Conjunto `teste` — 18 condições × 187 linhas (arquivo versão 2026-10-01, autor fable); 12 difíceis; 131 verdadeiras e 27 indecidíveis no gabarito

### Total (micro, sobre as linhas decidíveis de todas as condições) — Jev × variantes × baseline LIKE

P/R/F1 sobre as decidíveis que o sistema DECIDIU; `humano` = decidíveis mandadas a `indecidivel` (fora de P/R/F1), separadas em `V a humano` e `F a humano`; `F1 com V a humano = perdidas` conta só as verdadeiras mandadas a humano como perdidas (as falsas a humano não o alteram). **PERDIDAS** = verdadeira do gabarito que saiu `falso` (o filtro perdeu a linha). **FP EM NEGAÇÃO** = falsa marcada `verdadeiro` numa condição da família negação (o erro do LIKE). `indecidíveis → humano` = linhas de pista fraca do gabarito que o sistema mandou revisar (e quantas virou `verdadeiro`). Variante oficial: `clausulas` + pista; faixa de `stated` 0.3–0.8; `hinted` ≥ 0.7.

| variante | decidíveis | decididas | P | R | F1 | F1 com V a humano = perdidas | humano (decidíveis) | V a humano | F a humano | PERDIDAS (V → falso) | FP EM NEGAÇÃO | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev (oficial) | 3339 | 3151 | 0.980 | 0.980 | 0.980 | 0.843 | 188 (0.056) | 32 | 156 | 2/131 | 1 | 15/27 (V: 1) | 0 |
| Jev: inteira | 3339 | 3183 | 0.970 | 0.980 | 0.975 | 0.840 | 156 (0.047) | 32 | 124 | 2/131 | 1 | 12/27 (V: 1) | 0 |
| Jev: inteira+pista | 3339 | 3145 | 0.970 | 0.990 | 0.980 | 0.840 | 194 (0.058) | 33 | 161 | 1/131 | 1 | 15/27 (V: 1) | 0 |
| Jev: cláusulas | 3339 | 3190 | 0.980 | 0.970 | 0.975 | 0.843 | 149 (0.045) | 31 | 118 | 3/131 | 1 | 11/27 (V: 1) | 0 |
| Jev: cláusulas+pista | 3339 | 3151 | 0.980 | 0.980 | 0.980 | 0.843 | 188 (0.056) | 32 | 156 | 2/131 | 1 | 15/27 (V: 1) | 0 |
| baseline LIKE | 3339 | 3339 | 0.293 | 0.626 | 0.399 | 0.399 | 0 (0.000) | 0 | 0 | 49/131 | 17 | 0/27 (V: 7) | 0 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 F1 (decididas) | 0.980 (baseline 0.399) | ≥ 0.85 e ≥ 0.549 | ✓ |
| 2 perdidas (V → falso) | 2/131 (0.015) | ≤ 0.05 | ✓ |
| 3 FP em negação | 1 | ≤ 2 | ✓ |
| 4 humano (decidíveis) | 188/3339 (0.056) | ≤ 0.08 | ✓ |
| secundário: indecidíveis → humano | 15/27 | ≥ 0.5 | ✓ |
| secundário: falhas operacionais | 0 | 0 | ✓ |

### Por condição

`filtro` = parte de campo resolvida pelo código; `chamadas` = linhas que passaram no filtro e foram ao Jev; `V/I` = verdadeiras / indecidíveis do gabarito; `base` = baseline LIKE (radicais entre colchetes).

| id | família | filtro | composta | chamadas | V/I | P | R | F1 | humano | perdidas | FP | I → humano | base F1 | base FP | base perdidas | LIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SQ-T01 | fácil | — | — | 187 | 11/2 | 1.000 | 1.000 | 1.000 | 8 | 0 | 0 | 1/2 | 0.552 | 10 | 3 | [famil, filho, peque, bebe, camin] |
| SQ-T02 | inferência fraca | — | — | 187 | 8/2 | 1.000 | 1.000 | 1.000 | 4 | 0 | 0 | 1/2 | 0.600 | 6 | 2 | [neces, acess, idoso, dific, cadei, pode, subir, escad] |
| SQ-T03 | composta | orcamento >= 400000 | — | 78 | 4/0 | 1.000 | 1.000 | 1.000 | 38 | 0 | 0 | 0/0 | 0.462 | 6 | 1 | [inves, renda, reven, morar] |
| SQ-T04 | fácil | — | — | 187 | 15/1 | 1.000 | 1.000 | 1.000 | 16 | 0 | 0 | 0/1 | 0.298 | 25 | 8 | [achar, valor, alto, preco, alugu, condo, parce] |
| SQ-T05 | inferência fraca | — | — | 187 | 7/3 | 1.000 | 1.000 | 1.000 | 5 | 0 | 0 | 2/3 | 0.714 | 2 | 2 | [preoc, barul, tranq, vizin] |
| SQ-T06 | inferência fraca | — | — | 187 | 7/2 | 0.833 | 1.000 | 0.909 | 7 | 0 | 1 | 2/2 | 0.308 | 15 | 3 | [decis, fecha, depen, pesso, conju, pais, socio] |
| SQ-T07 | fácil | — | — | 187 | 6/1 | 1.000 | 1.000 | 1.000 | 11 | 0 | 0 | 1/1 | 0.323 | 20 | 1 | [quere, perto, traba, escol, traje, diari] |
| SQ-T08 | negação | — | — | 187 | 4/0 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 | 0/0 | 0.286 | 2 | 3 | [decla, anima, estim] |
| SQ-T09 | composta | — | E | 187 | 4/0 | 1.000 | 1.000 | 1.000 | 10 | 0 | 0 | 0/0 | 0.286 | 8 | 2 | [mudar, cidad, urgen, fecha] |
| SQ-T10 | fácil | finalidade = locacao | — | 64 | 8/0 | 1.000 | 1.000 | 1.000 | 22 | 0 | 0 | 0/0 | 0.364 | 1 | 6 | [urgen, fecha] |
| SQ-T11 | negação | visitas >= 1 | — | 110 | 9/2 | 1.000 | 1.000 | 1.000 | 3 | 0 | 0 | 2/2 | 0.444 | 12 | 3 | [imove, descr, recem, refor, feita] |
| SQ-T12 | composta | — | — | 187 | 4/7 | 1.000 | 1.000 | 1.000 | 21 | 0 | 0 | 3/7 | 0.182 | 26 | 1 | [achar, caro, mas, segue, procu, diz, conti] |
| SQ-T13 | fácil | data em 2026-09 | — | 64 | 4/1 | 1.000 | 1.000 | 1.000 | 7 | 0 | 0 | 0/1 | 0.667 | 2 | 1 | [avali, imobi, setem] |
| SQ-T14 | composta | — | OU | 187 | 17/4 | 1.000 | 0.846 | 0.917 | 9 | 2 | 0 | 1/4 | 0.395 | 44 | 2 | [preci, comod, extra, traba, casa, filho, peque, bebe, camin] |
| SQ-T15 | negação | — | — | 187 | 5/0 | 0.833 | 1.000 | 0.909 | 4 | 0 | 1 | 0/0 | 0.667 | 3 | 1 | [elogi, atend] |
| SQ-T16 | composta | visitas >= 2 | — | 41 | 6/1 | 1.000 | 1.000 | 1.000 | 6 | 0 | 0 | 1/1 | 0.727 | 1 | 2 | [depen, finan, fizer] |
| SQ-T17 | composta | — | E | 187 | 5/0 | 1.000 | 1.000 | 1.000 | 16 | 0 | 0 | 0/0 | 0.348 | 14 | 1 | [desis, busca, motiv, ligad, preco, achar, caro] |
| SQ-T18 | fácil | finalidade = locacao | — | 64 | 7/1 | 1.000 | 1.000 | 1.000 | 0 | 0 | 0 | 1/1 | 0.000 | 1 | 7 | [anima, estim] |

### Por família difícil (pela `nota` do rotulador)

| família | condições | F1 Jev | F1 baseline | humano Jev | perdidas Jev | FP Jev | perdidas base | FP base | I → humano |
|---|---|---|---|---|---|---|---|---|---|
| fácil | 6 | 1.000 | 0.370 | 64 | 0 | 0 | 26 | 59 | 3/6 |
| inferência fraca | 3 | 0.971 | 0.500 | 16 | 0 | 1 | 7 | 23 | 5/7 |
| composta | 6 | 0.969 | 0.365 | 100 | 2 | 0 | 9 | 99 | 5/12 |
| negação | 3 | 0.970 | 0.478 | 8 | 0 | 1 | 7 | 17 | 2/2 |

### Onde `stated` cai, por gabarito (só linhas que foram ao Jev)

| gabarito | n | stated mín | p10 | p50 | p90 | máx | ≤ 0,2 | 0,2–0,8 | ≥ 0,8 | hinted p50 | hinted ≥ 0,8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| verdadeiro | 131 | 0.220 | 0.660 | 0.910 | 0.960 | 0.980 | 0 | 34 | 97 | 0.940 | 125 |
| falso | 2507 | 0.020 | 0.030 | 0.060 | 0.220 | 0.890 | 2231 | 273 | 3 | 0.150 | 42 |
| indecidivel | 27 | 0.040 | 0.070 | 0.300 | 0.610 | 0.930 | 6 | 20 | 1 | 0.760 | 8 |

### Cobertura × erro por faixa de `stated` (variante oficial; mesmas respostas, outra faixa)

| faixa | cobertura (decididas/decidíveis) | erro entre decididas | F1 | humano | perdidas | FP em negação | I → humano |
|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.944 | 0.001 | 0.980 | 188 | 2 | 1 | 15/27 |
| 0.5–0.5 | 0.979 | 0.009 | 0.899 | 70 | 2 | 3 | 10/27 |
| 0.4–0.6 | 0.971 | 0.005 | 0.942 | 97 | 2 | 2 | 13/27 |
| 0.3–0.7 | 0.950 | 0.002 | 0.971 | 166 | 2 | 1 | 14/27 |
| 0.2–0.8 | 0.909 | 0.001 | 0.990 | 303 | 0 | 1 | 20/27 |
| 0.1–0.9 | 0.810 | 0.000 | 1.000 | 634 | 0 | 0 | 21/27 |

### Custo e latência (medidos na chamada real; do cache também)

| linhas avaliadas (cond × linha) | sem chamada (filtro) | requisicoes | novas (não cache) | textos longos (sem chamada) | falhas operacionais (→ indecidivel) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_1000_linhas_avaliadas | US$_por_1000_requisicoes | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3366 | 701 | 2665 | 0 | 0 | 0 | 6452 | 255 | 317 | 1131 | 0.126552 | 0.0376 | 0.0475 | jev-1.13.0 |

### Caso a caso — erros, linhas mandadas a humano e indecidíveis do gabarito

`st`/`hi` = Nouls `stated` e `hinted`; `partes` = Nouls por cláusula (compostas); `saída` = variante oficial; `base` = LIKE.

| cond | linha | gab | st | hi | partes | saída | ok | base | por | texto |
|---|---|---|---|---|---|---|---|---|---|---|
| SQ-T01 | OB-002 | falso | 0.66 | 0.85 | — | indecidivel | ✗ | verdadeiro | jev | Está vindo de Belo Horizonte com a família no começo do ano, quer casa com quintal. Orçamento folgado, paga à … |
| SQ-T01 | OB-018 | falso | 0.58 | 0.78 | — | indecidivel | ✗ | verdadeiro | jev | A casa está com tudo renovado, dono trocou até o telhado em 2025. Cliente só achou pequeno pra família. |
| SQ-T01 | OB-049 | verdadeiro | 0.76 | 0.87 | — | indecidivel | ✗ | verdadeiro | jev | Disse que o filho cria um coelho e que isso 'não deve ser problema'. |
| SQ-T01 | OB-059 | indecidivel | 0.21 | 0.79 | — | indecidivel | ✓ | falso | jev | Perguntou se o condomínio tem área kids e salão de festas. |
| SQ-T01 | OB-061 | verdadeiro | 0.67 | 0.93 | — | indecidivel | ✗ | verdadeiro | jev | Precisa de um quarto a mais 'pro bebê'. Não falou prazo. |
| SQ-T01 | OB-062 | indecidivel | 0.24 | 0.68 | — | falso | ✗ | falso | jev | Comentou que a sobrinha vai morar com eles por uns meses. |
| SQ-T01 | OB-094 | verdadeiro | 0.70 | 0.81 | — | indecidivel | ✗ | verdadeiro | jev | Filho autista precisa de ambiente tranquilo e sem escada aberta; busca casa térrea em rua calma. |
| SQ-T01 | OB-100 | falso | 0.32 | 0.71 | — | indecidivel | ✗ | verdadeiro | jev | Compra pro filho morar durante a faculdade e depois decide se aluga. |
| SQ-T01 | OB-123 | verdadeiro | 0.68 | 0.80 | — | indecidivel | ✗ | verdadeiro | jev | Quer rua tranquila, sem trânsito pesado, por causa do sono do bebê. |
| SQ-T01 | OB-135 | verdadeiro | 0.32 | 0.72 | — | indecidivel | ✗ | falso | jev | Precisa ficar na rota da escola das crianças, bairro vizinho no máximo. |
| SQ-T02 | OB-053 | verdadeiro | 0.60 | 0.90 | — | indecidivel | ✗ | verdadeiro | jev | Tem um cachorro idoso que não sobe escada; precisa de térreo ou elevador. |
| SQ-T02 | OB-056 | falso | 0.42 | 0.73 | — | indecidivel | ✗ | verdadeiro | jev | Casal com gêmeos de 2 anos, procura condomínio com playground e piso que não seja escada aberta. |
| SQ-T02 | OB-089 | indecidivel | 0.26 | 0.83 | — | indecidivel | ✓ | falso | jev | Perguntou se o prédio tem elevador. Não explicou o motivo. |
| SQ-T02 | OB-093 | indecidivel | 0.04 | 0.06 | — | falso | ✗ | verdadeiro | jev | Pai idoso visita com frequência, mas 'ele sobe escada numa boa'. |
| SQ-T02 | OB-094 | verdadeiro | 0.76 | 0.91 | — | indecidivel | ✗ | verdadeiro | jev | Filho autista precisa de ambiente tranquilo e sem escada aberta; busca casa térrea em rua calma. |
| SQ-T02 | OB-144 | falso | 0.34 | 0.65 | — | indecidivel | ✗ | falso | jev | Mandou lista com 6 anúncios de portais pra eu conferir disponibilidade. |
| SQ-T03 | OB-006 | falso | 0.41 | 0.64 | — | indecidivel | ✗ | falso | jev | Recebeu proposta de emprego em outro estado e vai vender o apto dele aqui pra comprar lá. Pediu avaliação. |
| SQ-T03 | OB-009 | falso | 0.37 | 0.61 | — | indecidivel | ✗ | falso | jev | Perguntou se o condomínio tem portaria 24h e se a região é bem servida de ônibus pra rodoviária. |
| SQ-T03 | OB-010 | falso | 0.34 | 0.42 | — | indecidivel | ✗ | falso | jev | Disse que não vai mudar de cidade de jeito nenhum, a família toda é daqui; quer trocar de bairro só. |
| SQ-T03 | OB-016 | falso | 0.36 | 0.33 | — | indecidivel | ✗ | falso | jev | Visita no sobrado: fachada pintada agora, box e louças novas, só a área de serviço ficou original. Vai pensar. |
| SQ-T03 | OB-022 | falso | 0.37 | 0.31 | — | indecidivel | ✗ | falso | jev | O proprietário disse que trocou o chuveiro e pintou um quarto antes de anunciar. Cliente quer ver pessoalmente… |
| SQ-T03 | OB-026 | falso | 0.39 | 0.41 | — | indecidivel | ✗ | falso | jev | Está sem prazo nenhum, 'quando aparecer o certo a gente vê'. Pediu pra não ligar, só mandar anúncio por mensag… |
| SQ-T03 | OB-037 | falso | 0.35 | 0.52 | — | indecidivel | ✗ | falso | jev | Vai pagar à vista, dinheiro da herança já está na conta. Só quer desconto por isso. |
| SQ-T03 | OB-041 | falso | 0.32 | 0.47 | — | indecidivel | ✗ | falso | jev | Quer saber se o imóvel aceita financiamento, mas ainda não decidiu se vai financiar ou usar a venda do carro m… |
| SQ-T03 | OB-050 | falso | 0.40 | 0.27 | — | indecidivel | ✗ | falso | jev | Não quer saber de vizinho com cachorro barulhento; ela mesma não tem pet. |
| SQ-T03 | OB-057 | falso | 0.35 | 0.58 | — | indecidivel | ✗ | falso | jev | Sem filhos, os dois trabalham fora; apto compacto está bom. |
| SQ-T03 | OB-068 | falso | 0.34 | 0.24 | — | indecidivel | ✗ | falso | jev | Perguntou se a região tem boa cobertura de internet. |
| SQ-T03 | OB-072 | falso | 0.45 | 0.33 | — | indecidivel | ✗ | falso | jev | Irritado: a visita de ontem foi desmarcada em cima da hora pela segunda vez. Disse que vai procurar em outro l… |
| SQ-T03 | OB-081 | falso | 0.38 | 0.61 | — | indecidivel | ✗ | falso | jev | Está em contato com duas imobiliárias e vai fechar com quem conseguir desconto. Pediu proposta por escrito. |
| SQ-T03 | OB-083 | falso | 0.33 | 0.26 | — | indecidivel | ✗ | falso | jev | Só está vendo com a gente, por indicação de um amigo; não procurou mais ninguém. |
| SQ-T03 | OB-086 | falso | 0.32 | 0.24 | — | indecidivel | ✗ | falso | jev | Disse que largou a outra imobiliária porque não respondiam. Agora é só com a gente. |
| SQ-T03 | OB-091 | falso | 0.33 | 0.16 | — | indecidivel | ✗ | falso | jev | Teve cirurgia no joelho e por enquanto não consegue subir escada; prefere térreo. |
| SQ-T03 | OB-092 | falso | 0.34 | 0.45 | — | indecidivel | ✗ | falso | jev | Casal jovem, 'escada não é problema'. Quer cobertura duplex. |
| SQ-T03 | OB-104 | falso | 0.33 | 0.28 | — | indecidivel | ✗ | falso | jev | Depois de 3 visitas, parou de responder. Última mensagem dela foi 'vou pensar'. |
| SQ-T03 | OB-110 | falso | 0.39 | 0.35 | — | indecidivel | ✗ | falso | jev | Perdeu o interesse: achou que 900 mil era demais pra 70 m² e não quer ver mais nada. |
| SQ-T03 | OB-113 | falso | 0.39 | 0.51 | — | indecidivel | ✗ | falso | jev | Preço dentro do esperado, não reclamou de nada. Vai fazer proposta. |
| SQ-T03 | OB-114 | falso | 0.39 | 0.34 | — | indecidivel | ✗ | falso | jev | Disse que o metro quadrado da região 'está fora da realidade' e que vai olhar mais longe. |
| SQ-T03 | OB-117 | falso | 0.37 | 0.42 | — | indecidivel | ✗ | falso | jev | Achou barato pro padrão do prédio e perguntou se tem algum problema escondido. |
| SQ-T03 | OB-118 | falso | 0.38 | 0.27 | — | indecidivel | ✗ | falso | jev | Comentou que a parcela ficaria pesada demais com os juros atuais. |
| SQ-T03 | OB-120 | falso | 0.41 | 0.28 | — | indecidivel | ✗ | falso | jev | Preocupada com barulho: trabalha à noite e dorme de dia; descartou apto de frente pra avenida. |
| SQ-T03 | OB-123 | falso | 0.37 | 0.38 | — | indecidivel | ✗ | falso | jev | Quer rua tranquila, sem trânsito pesado, por causa do sono do bebê. |
| SQ-T03 | OB-128 | falso | 0.33 | 0.54 | — | indecidivel | ✗ | falso | jev | Os pais vão pagar a entrada e querem aprovar o imóvel antes. |
| SQ-T03 | OB-132 | falso | 0.32 | 0.20 | — | indecidivel | ✗ | falso | jev | Comentou que a sogra 'tem opinião sobre tudo', mas a decisão é dos dois. |
| SQ-T03 | OB-133 | falso | 0.32 | 0.36 | — | indecidivel | ✗ | falso | jev | É a única compradora; já tem procuração do irmão pra fechar. |
| SQ-T03 | OB-140 | falso | 0.34 | 0.32 | — | indecidivel | ✗ | falso | jev | Aposentado, não tem trajeto diário; quer perto do parque. |
| SQ-T03 | OB-141 | falso | 0.42 | 0.47 | — | indecidivel | ✗ | falso | jev | Primeiro contato pelo site, pediu mais fotos do apto de 2 quartos. Sem detalhes ainda. |
| SQ-T03 | OB-143 | falso | 0.62 | 0.87 | — | indecidivel | ✗ | falso | jev | Cliente antigo, comprou com a gente em 2019 e quer vender pra comprar maior. Quatro pessoas em casa. |
| SQ-T03 | OB-151 | falso | 0.41 | 0.48 | — | indecidivel | ✗ | falso | jev | Interessado em terreno no litoral pra construir. Fora do nosso portfólio; indiquei parceiro. |
| SQ-T03 | OB-153 | falso | 0.31 | 0.48 | — | indecidivel | ✗ | falso | jev | Vem transferida de Brasília em janeiro, prazo apertado: a empresa só paga hotel por 15 dias. Financia 80%. |
| SQ-T03 | OB-156 | falso | 0.39 | 0.51 | — | indecidivel | ✗ | falso | jev | Viu o sobrado recém-reformado da Vila Mariana e disse que o preço não condiz com a região; ainda assim pediu p… |
| SQ-T03 | OB-163 | falso | 0.31 | 0.30 | — | indecidivel | ✗ | verdadeiro | jev | Mãe idosa com dificuldade de locomoção vai morar junto, e o apto da rua de trás tem obra que não acaba: quer t… |
| SQ-T03 | OB-165 | falso | 0.34 | 0.38 | — | indecidivel | ✗ | falso | jev | Precisa ficar a no máximo 15 min do escritório, de bicicleta. Vai financiar. |
| SQ-T03 | OB-166 | falso | 0.34 | 0.40 | — | indecidivel | ✗ | falso | jev | Vai desistir se o banco não aprovar; já foi reprovado uma vez. |
| SQ-T03 | OB-184 | falso | 0.55 | 0.33 | — | indecidivel | ✗ | falso | jev | Desistiu: os valores da região passaram do que ele consegue pagar e vai ficar no aluguel atual. |
| SQ-T04 | OB-020 | falso | 0.51 | 0.88 | — | indecidivel | ✗ | verdadeiro | jev | O apto está original de 1998, nunca foi mexido. Ele topa reformar se o preço cair. |
| SQ-T04 | OB-021 | falso | 0.23 | 0.77 | — | indecidivel | ✗ | falso | jev | Anúncio diz 'oportunidade para reforma'. Cliente perguntou quanto custaria deixar habitável. |
| SQ-T04 | OB-027 | falso | 0.23 | 0.76 | — | indecidivel | ✗ | falso | jev | Disse que não tem pressa alguma, mora com os pais e vai esperar o mercado baixar. |
| SQ-T04 | OB-037 | falso | 0.47 | 0.80 | — | indecidivel | ✗ | falso | jev | Vai pagar à vista, dinheiro da herança já está na conta. Só quer desconto por isso. |
| SQ-T04 | OB-038 | falso | 0.29 | 0.77 | — | indecidivel | ✗ | verdadeiro | jev | Simulação do Santander deu parcela de 3.800; ela quer tentar no Itaú antes de decidir. |
| SQ-T04 | OB-079 | falso | 0.10 | 0.83 | — | indecidivel | ✗ | verdadeiro | jev | Ficou em silêncio depois que mandei o valor do condomínio. |
| SQ-T04 | OB-081 | falso | 0.50 | 0.90 | — | indecidivel | ✗ | falso | jev | Está em contato com duas imobiliárias e vai fechar com quem conseguir desconto. Pediu proposta por escrito. |
| SQ-T04 | OB-082 | verdadeiro | 0.66 | 0.94 | — | indecidivel | ✗ | falso | jev | Viu um apto parecido com outro corretor na mesma rua por 40 mil a menos. Pediu pra cobrir. |
| SQ-T04 | OB-108 | falso | 0.20 | 0.74 | — | indecidivel | ✗ | falso | jev | Disse que pausou a procura até vender o carro. Deve voltar em dois meses. |
| SQ-T04 | OB-109 | falso | 0.29 | 0.78 | — | indecidivel | ✗ | falso | jev | Não desistiu, mas reduziu o orçamento pra 350 mil depois da demissão da esposa. |
| SQ-T04 | OB-111 | falso | 0.34 | 0.82 | — | indecidivel | ✗ | falso | jev | Avisou que vai ficar onde está, reformar a casa atual sai mais barato. |
| SQ-T04 | OB-115 | indecidivel | 0.06 | 0.60 | — | falso | ✗ | falso | jev | Perguntou se o proprietário aceita negociação. Não disse se achou caro. |
| SQ-T04 | OB-118 | verdadeiro | 0.79 | 0.95 | — | indecidivel | ✗ | verdadeiro | jev | Comentou que a parcela ficaria pesada demais com os juros atuais. |
| SQ-T04 | OB-119 | verdadeiro | 0.74 | 0.94 | — | indecidivel | ✗ | falso | jev | Pediu um imóvel 'mais em conta' que os três que mostrei. |
| SQ-T04 | OB-149 | falso | 0.21 | 0.80 | — | indecidivel | ✗ | verdadeiro | jev | Cliente perguntou sobre IPTU e taxa de condomínio da unidade 3 quartos; vai comparar com outra. |
| SQ-T04 | OB-168 | falso | 0.44 | 0.86 | — | indecidivel | ✗ | verdadeiro | jev | Quer um apto perto do trabalho dela e da escola do filho; o condomínio não pode cobrar mais de 800. |
| SQ-T04 | OB-176 | falso | 0.17 | 0.76 | — | indecidivel | ✗ | falso | jev | Precisa de financiamento; visitou 3 unidades em uma tarde e quer proposta na de 2 quartos. |
| SQ-T05 | OB-050 | verdadeiro | 0.79 | 0.92 | — | indecidivel | ✗ | verdadeiro | jev | Não quer saber de vizinho com cachorro barulhento; ela mesma não tem pet. |
| SQ-T05 | OB-051 | falso | 0.20 | 0.70 | — | indecidivel | ✗ | falso | jev | Três gatos, procura casa térrea com quintal murado. |
| SQ-T05 | OB-063 | falso | 0.29 | 0.70 | — | indecidivel | ✗ | falso | jev | Trabalha de casa 100%, precisa de um cômodo isolado com porta pra reuniões. Internet fibra é condição. |
| SQ-T05 | OB-064 | falso | 0.75 | 0.94 | — | indecidivel | ✗ | falso | jev | Faz atendimento online de manhã, então quer um canto silencioso pra montar o consultório virtual. |
| SQ-T05 | OB-124 | indecidivel | 0.31 | 0.83 | — | indecidivel | ✓ | falso | jev | Perguntou se o apto é de frente ou de fundos. |
| SQ-T05 | OB-125 | indecidivel | 0.53 | 0.85 | — | indecidivel | ✓ | verdadeiro | jev | Músico, toca bateria em casa; precisa de vizinhança tolerante ou casa isolada. |
| SQ-T05 | OB-160 | falso | 0.34 | 0.76 | — | indecidivel | ✗ | falso | jev | Família com três crianças pequenas vindo do interior; o pai trabalha em casa e quer um escritório longe dos qu… |
| SQ-T05 | OB-172 | indecidivel | 0.93 | 0.96 | — | verdadeiro | ✗ | verdadeiro | jev | Cliente perguntou se o prédio tem gerador e se a vizinhança é tranquila à noite. |
| SQ-T06 | OB-015 | verdadeiro | 0.49 | 0.88 | — | indecidivel | ✗ | falso | jev | Apartamento de 3 quartos que o proprietário acabou de reformar; entregou com armários novos. Cliente pediu seg… |
| SQ-T06 | OB-039 | falso | 0.86 | 0.93 | — | verdadeiro | ✗ | verdadeiro | jev | Explicou que o financiamento seria pelo nome do pai, que tem renda comprovada. Decisão final é dele mesmo assi… |
| SQ-T06 | OB-055 | verdadeiro | 0.71 | 0.92 | — | indecidivel | ✗ | falso | jev | Grávida de 6 meses, quer 3 quartos e escola perto. Marido vai ver as opções no fim de semana. |
| SQ-T06 | OB-085 | falso | 0.15 | 0.74 | — | indecidivel | ✗ | falso | jev | Vai visitar um lançamento da construtora no sábado e depois decide entre o nosso e o deles. |
| SQ-T06 | OB-109 | falso | 0.21 | 0.74 | — | indecidivel | ✗ | falso | jev | Não desistiu, mas reduziu o orçamento pra 350 mil depois da demissão da esposa. |
| SQ-T06 | OB-130 | indecidivel | 0.41 | 0.75 | — | indecidivel | ✓ | falso | jev | Vai mostrar as fotos pro namorado 'só pra ele ver'. |
| SQ-T06 | OB-132 | indecidivel | 0.77 | 0.92 | — | indecidivel | ✓ | verdadeiro | jev | Comentou que a sogra 'tem opinião sobre tudo', mas a decisão é dos dois. |
| SQ-T06 | OB-138 | falso | 0.39 | 0.73 | — | indecidivel | ✗ | falso | jev | Marido trabalha na zona norte e ela na zona sul; querem algo no meio do caminho. |
| SQ-T06 | OB-168 | falso | 0.35 | 0.83 | — | indecidivel | ✗ | falso | jev | Quer um apto perto do trabalho dela e da escola do filho; o condomínio não pode cobrar mais de 800. |
| SQ-T06 | OB-185 | falso | 0.33 | 0.46 | — | indecidivel | ✗ | falso | jev | Encerrou a busca depois da terceira visita; tudo acima do orçamento dela, não quer mais receber anúncios. |
| SQ-T07 | OB-004 | falso | 0.68 | 0.93 | — | indecidivel | ✗ | verdadeiro | jev | Mora hoje em Campinas e vem toda semana a trabalho; disse que vai 'fixar residência aqui de vez'. Prefere pert… |
| SQ-T07 | OB-009 | falso | 0.25 | 0.78 | — | indecidivel | ✗ | falso | jev | Perguntou se o condomínio tem portaria 24h e se a região é bem servida de ônibus pra rodoviária. |
| SQ-T07 | OB-055 | falso | 0.61 | 0.87 | — | indecidivel | ✗ | verdadeiro | jev | Grávida de 6 meses, quer 3 quartos e escola perto. Marido vai ver as opções no fim de semana. |
| SQ-T07 | OB-060 | falso | 0.30 | 0.71 | — | indecidivel | ✗ | verdadeiro | jev | Mora sozinho, divorciado, os filhos já são adultos e moram fora. Quer 1 quarto perto do centro. |
| SQ-T07 | OB-070 | falso | 0.14 | 0.73 | — | indecidivel | ✗ | falso | jev | Comentou que largou o home office e voltou pro presencial, então pode ser menor. |
| SQ-T07 | OB-096 | falso | 0.50 | 0.80 | — | indecidivel | ✗ | verdadeiro | jev | Quer um studio perto da faculdade pra colocar no Airbnb, até 420 mil. Já tem outros dois. |
| SQ-T07 | OB-134 | verdadeiro | 0.70 | 0.87 | — | indecidivel | ✗ | verdadeiro | jev | Quer até 20 minutos a pé do hospital onde trabalha, plantão noturno. |
| SQ-T07 | OB-135 | verdadeiro | 0.70 | 0.90 | — | indecidivel | ✗ | verdadeiro | jev | Precisa ficar na rota da escola das crianças, bairro vizinho no máximo. |
| SQ-T07 | OB-137 | indecidivel | 0.31 | 0.76 | — | indecidivel | ✓ | falso | jev | Perguntou qual a distância até o centro. |
| SQ-T07 | OB-138 | verdadeiro | 0.78 | 0.94 | — | indecidivel | ✗ | verdadeiro | jev | Marido trabalha na zona norte e ela na zona sul; querem algo no meio do caminho. |
| SQ-T07 | OB-139 | verdadeiro | 0.77 | 0.91 | — | indecidivel | ✗ | verdadeiro | jev | Prefere perto do metrô pra não depender de carro no trajeto pra firma. |
| SQ-T07 | OB-165 | verdadeiro | 0.79 | 0.94 | — | indecidivel | ✗ | falso | jev | Precisa ficar a no máximo 15 min do escritório, de bicicleta. Vai financiar. |
| SQ-T08 | OB-054 | verdadeiro | 0.23 | 0.73 | — | indecidivel | ✗ | falso | jev | Alérgico a pelo, descartou unidade onde o antigo morador tinha gato. |
| SQ-T09 | OB-001 | falso | 0.72 | 0.91 | 0.89, 0.61 | indecidivel | ✗ | falso | jev | Cliente ligou de Curitiba: a empresa transferiu ele pra cá e precisa de apartamento pronto pra morar. Vai fina… |
| SQ-T09 | OB-006 | falso | 0.46 | 0.83 | 0.96, 0.37 | indecidivel | ✗ | falso | jev | Recebeu proposta de emprego em outro estado e vai vender o apto dele aqui pra comprar lá. Pediu avaliação. |
| SQ-T09 | OB-024 | falso | 0.60 | 0.73 | 0.31, 0.95 | indecidivel | ✗ | verdadeiro | jev | Precisa fechar em 10 dias, o contrato atual vence e o dono não renova. Aceita qualquer bairro da zona sul. |
| SQ-T09 | OB-028 | falso | 0.58 | 0.85 | 0.32, 0.92 | indecidivel | ✗ | falso | jev | Pediu pra agilizar a documentação porque o bebê nasce em janeiro e quer estar instalada antes. |
| SQ-T09 | OB-030 | falso | 0.48 | 0.77 | 0.33, 0.53 | indecidivel | ✗ | falso | jev | Quer visitar amanhã cedo e assinar na mesma semana se gostar; empresa paga a mudança até o fim do mês. |
| SQ-T09 | OB-031 | falso | 0.22 | 0.73 | 0.14, 0.27 | indecidivel | ✗ | falso | jev | Perguntou qual o prazo médio de entrega das chaves depois da assinatura. |
| SQ-T09 | OB-032 | falso | 0.30 | 0.72 | 0.07, 0.48 | indecidivel | ✗ | falso | jev | Mandou quatro mensagens no mesmo dia pedindo retorno sobre o apto. |
| SQ-T09 | OB-154 | verdadeiro | 0.76 | 0.92 | 0.84, 0.70 | indecidivel | ✗ | falso | jev | Estudante vindo de Goiânia, precisa alugar antes das aulas em fevereiro; os pais assinam o contrato. |
| SQ-T09 | OB-176 | falso | 0.37 | 0.71 | 0.16, 0.67 | indecidivel | ✗ | falso | jev | Precisa de financiamento; visitou 3 unidades em uma tarde e quer proposta na de 2 quartos. |
| SQ-T09 | OB-180 | falso | 0.52 | 0.77 | 0.31, 0.46 | indecidivel | ✗ | falso | jev | Precisa alugar até o dia 15, quando entrega as chaves do atual; aceita sem mobília. |
| SQ-T10 | OB-003 | falso | 0.38 | 0.81 | — | indecidivel | ✗ | falso | jev | Vai sair da cidade em dezembro por causa do mestrado e procura um studio mobiliado lá; quer indicação de parce… |
| SQ-T10 | OB-005 | falso | 0.23 | 0.78 | — | indecidivel | ✗ | falso | jev | Casal se mudando de Porto Alegre, chegam em novembro. Dois cachorros grandes, só casa. |
| SQ-T10 | OB-017 | falso | 0.24 | 0.72 | — | indecidivel | ✗ | falso | jev | Unidade reformada mês passado, mobília nova; o cliente quer entrar sem mexer em nada e gostou disso. |
| SQ-T10 | OB-019 | falso | 0.48 | 0.31 | — | indecidivel | ✗ | falso | jev | Imóvel precisa de reforma geral, infiltração no quarto e piso solto. Cliente descartou na hora. |
| SQ-T10 | OB-030 | verdadeiro | 0.76 | 0.92 | — | indecidivel | ✗ | falso | jev | Quer visitar amanhã cedo e assinar na mesma semana se gostar; empresa paga a mudança até o fim do mês. |
| SQ-T10 | OB-040 | falso | 0.37 | 0.66 | — | indecidivel | ✗ | falso | jev | Cliente de locação, nada de financiamento no caso dele. Perguntou de seguro-fiança. |
| SQ-T10 | OB-047 | falso | 0.31 | 0.49 | — | indecidivel | ✗ | falso | jev | Não tem animal nenhum e não pretende ter; indiferente à regra do condomínio. |
| SQ-T10 | OB-071 | falso | 0.76 | 0.92 | — | indecidivel | ✗ | falso | jev | Cliente reclamou que ficou 3 dias sem resposta e que quase fechou com outra imobiliária. Pediu desculpas em no… |
| SQ-T10 | OB-075 | falso | 0.30 | 0.70 | — | indecidivel | ✗ | falso | jev | Agradeceu a agilidade no contrato e vai indicar a gente pra uma colega. |
| SQ-T10 | OB-078 | falso | 0.42 | 0.68 | — | indecidivel | ✗ | falso | jev | Perguntou por que a gente demorou pra responder. Expliquei o feriado, ela entendeu. |
| SQ-T10 | OB-085 | falso | 0.39 | 0.81 | — | indecidivel | ✗ | falso | jev | Vai visitar um lançamento da construtora no sábado e depois decide entre o nosso e o deles. |
| SQ-T10 | OB-088 | falso | 0.42 | 0.57 | — | indecidivel | ✗ | falso | jev | Cadeirante, só considera unidades com porta larga no banheiro e vaga coberta perto do elevador. |
| SQ-T10 | OB-103 | falso | 0.36 | 0.25 | — | indecidivel | ✗ | falso | jev | Desistiu da busca: vai renovar o aluguel atual por mais um ano. Pediu pra tirar da lista. |
| SQ-T10 | OB-116 | falso | 0.38 | 0.70 | — | indecidivel | ✗ | falso | jev | Afirmou que o aluguel pedido é quase o dobro do que paga hoje; segue na busca por algo menor. |
| SQ-T10 | OB-129 | falso | 0.58 | 0.81 | — | indecidivel | ✗ | falso | jev | Decide sozinha, não precisa consultar ninguém. Proposta na segunda. |
| SQ-T10 | OB-154 | verdadeiro | 0.69 | 0.90 | — | indecidivel | ✗ | falso | jev | Estudante vindo de Goiânia, precisa alugar antes das aulas em fevereiro; os pais assinam o contrato. |
| SQ-T10 | OB-157 | falso | 0.32 | 0.56 | — | indecidivel | ✗ | falso | jev | Trabalha de casa e tem dois gatos; condomínio precisa aceitar bicho e ter sala extra. |
| SQ-T10 | OB-167 | falso | 0.54 | 0.19 | — | indecidivel | ✗ | falso | jev | Cliente de locação achou caro e desistiu; vai continuar na casa dos pais. |
| SQ-T10 | OB-168 | falso | 0.35 | 0.78 | — | indecidivel | ✗ | falso | jev | Quer um apto perto do trabalho dela e da escola do filho; o condomínio não pode cobrar mais de 800. |
| SQ-T10 | OB-181 | falso | 0.30 | 0.74 | — | indecidivel | ✗ | falso | jev | Trouxe o pai de 79 anos pra morar junto e procura locação de térreo com banheiro adaptado. |
| SQ-T10 | OB-182 | falso | 0.33 | 0.62 | — | indecidivel | ✗ | falso | jev | Quer alugar e tem um gato; perguntou se o condomínio permite. |
| SQ-T10 | OB-186 | falso | 0.50 | 0.34 | — | indecidivel | ✗ | falso | jev | Achou o aluguel pedido fora da realidade e desistiu de se mudar por enquanto. |
| SQ-T11 | OB-001 | falso | 0.20 | 0.75 | — | indecidivel | ✗ | falso | jev | Cliente ligou de Curitiba: a empresa transferiu ele pra cá e precisa de apartamento pronto pra morar. Vai fina… |
| SQ-T11 | OB-022 | indecidivel | 0.61 | 0.87 | — | indecidivel | ✓ | falso | jev | O proprietário disse que trocou o chuveiro e pintou um quarto antes de anunciar. Cliente quer ver pessoalmente… |
| SQ-T11 | OB-023 | indecidivel | 0.33 | 0.76 | — | indecidivel | ✓ | falso | jev | Fotos mostram piso cerâmico claro e paredes brancas; não sei se é recente ou só limpo. Cliente pediu visita. |
| SQ-T11 | OB-159 | verdadeiro | 0.50 | 0.69 | — | indecidivel | ✗ | verdadeiro | jev | Cliente investidor, não vai financiar; quer dois studios reformados pra alugar por temporada. |
| SQ-T11 | OB-184 | falso | 0.31 | 0.22 | — | indecidivel | ✗ | falso | jev | Desistiu: os valores da região passaram do que ele consegue pagar e vai ficar no aluguel atual. |
| SQ-T12 | OB-010 | falso | 0.31 | 0.60 | — | indecidivel | ✗ | falso | jev | Disse que não vai mudar de cidade de jeito nenhum, a família toda é daqui; quer trocar de bairro só. |
| SQ-T12 | OB-014 | indecidivel | 0.25 | 0.40 | — | falso | ✗ | falso | jev | Mostrei a casa do Jardim Europa, toda repaginada pelo dono há uns meses, janelas e portas trocadas. Ela achou … |
| SQ-T12 | OB-015 | falso | 0.22 | 0.70 | — | indecidivel | ✗ | falso | jev | Apartamento de 3 quartos que o proprietário acabou de reformar; entregou com armários novos. Cliente pediu seg… |
| SQ-T12 | OB-020 | falso | 0.32 | 0.69 | — | indecidivel | ✗ | falso | jev | O apto está original de 1998, nunca foi mexido. Ele topa reformar se o preço cair. |
| SQ-T12 | OB-026 | falso | 0.34 | 0.75 | — | indecidivel | ✗ | falso | jev | Está sem prazo nenhum, 'quando aparecer o certo a gente vê'. Pediu pra não ligar, só mandar anúncio por mensag… |
| SQ-T12 | OB-030 | falso | 0.33 | 0.74 | — | indecidivel | ✗ | falso | jev | Quer visitar amanhã cedo e assinar na mesma semana se gostar; empresa paga a mudança até o fim do mês. |
| SQ-T12 | OB-032 | falso | 0.25 | 0.75 | — | indecidivel | ✗ | falso | jev | Mandou quatro mensagens no mesmo dia pedindo retorno sobre o apto. |
| SQ-T12 | OB-033 | falso | 0.32 | 0.80 | — | indecidivel | ✗ | falso | jev | Comentou que o aluguel dele vence em maio do ano que vem; está só olhando o mercado. |
| SQ-T12 | OB-038 | falso | 0.29 | 0.80 | — | indecidivel | ✗ | falso | jev | Simulação do Santander deu parcela de 3.800; ela quer tentar no Itaú antes de decidir. |
| SQ-T12 | OB-074 | falso | 0.33 | 0.59 | — | indecidivel | ✗ | verdadeiro | jev | Falou que o anúncio estava com metragem errada e se sentiu enganada. Expliquei e ela aceitou continuar. |
| SQ-T12 | OB-080 | falso | 0.30 | 0.72 | — | indecidivel | ✗ | verdadeiro | jev | Disse que a concorrente respondeu mais rápido, mas que prefere nosso portfólio. |
| SQ-T12 | OB-081 | falso | 0.52 | 0.89 | — | indecidivel | ✗ | falso | jev | Está em contato com duas imobiliárias e vai fechar com quem conseguir desconto. Pediu proposta por escrito. |
| SQ-T12 | OB-082 | indecidivel | 0.48 | 0.86 | — | indecidivel | ✓ | falso | jev | Viu um apto parecido com outro corretor na mesma rua por 40 mil a menos. Pediu pra cobrir. |
| SQ-T12 | OB-085 | falso | 0.22 | 0.79 | — | indecidivel | ✗ | falso | jev | Vai visitar um lançamento da construtora no sábado e depois decide entre o nosso e o deles. |
| SQ-T12 | OB-098 | falso | 0.33 | 0.64 | — | indecidivel | ✗ | falso | jev | Perguntou quanto o imóvel renderia de aluguel, 'só pra saber'. Vai morar nele. |
| SQ-T12 | OB-109 | falso | 0.63 | 0.83 | — | indecidivel | ✗ | verdadeiro | jev | Não desistiu, mas reduziu o orçamento pra 350 mil depois da demissão da esposa. |
| SQ-T12 | OB-111 | falso | 0.32 | 0.42 | — | indecidivel | ✗ | falso | jev | Avisou que vai ficar onde está, reformar a casa atual sai mais barato. |
| SQ-T12 | OB-112 | indecidivel | 0.21 | 0.34 | — | falso | ✗ | falso | jev | Achou o valor do condomínio um absurdo, 1.400 por mês num prédio sem lazer. |
| SQ-T12 | OB-115 | indecidivel | 0.10 | 0.45 | — | falso | ✗ | verdadeiro | jev | Perguntou se o proprietário aceita negociação. Não disse se achou caro. |
| SQ-T12 | OB-118 | indecidivel | 0.30 | 0.58 | — | falso | ✗ | falso | jev | Comentou que a parcela ficaria pesada demais com os juros atuais. |
| SQ-T12 | OB-119 | indecidivel | 0.49 | 0.82 | — | indecidivel | ✓ | falso | jev | Pediu um imóvel 'mais em conta' que os três que mostrei. |
| SQ-T12 | OB-144 | falso | 0.27 | 0.70 | — | indecidivel | ✗ | falso | jev | Mandou lista com 6 anúncios de portais pra eu conferir disponibilidade. |
| SQ-T12 | OB-149 | falso | 0.27 | 0.80 | — | indecidivel | ✗ | falso | jev | Cliente perguntou sobre IPTU e taxa de condomínio da unidade 3 quartos; vai comparar com outra. |
| SQ-T12 | OB-164 | indecidivel | 0.41 | 0.68 | — | indecidivel | ✓ | verdadeiro | jev | Decisão é do marido, que acha tudo caro; ela gostaria de fechar logo. |
| SQ-T12 | OB-169 | falso | 0.55 | 0.87 | — | indecidivel | ✗ | verdadeiro | jev | Fez duas visitas, elogiou a pontualidade da equipe, mas disse que vai esperar o fim do ano por causa dos juros… |
| SQ-T12 | OB-174 | falso | 0.47 | 0.79 | — | indecidivel | ✗ | falso | jev | Disse que não está vendo com mais ninguém e não tem pressa; prefere receber opções por e-mail uma vez por sema… |
| SQ-T12 | OB-175 | falso | 0.31 | 0.67 | — | indecidivel | ✗ | falso | jev | Dependendo de financiamento e com orçamento de 300 mil, fez 2 visitas e gostou da segunda. |
| SQ-T12 | OB-176 | falso | 0.32 | 0.81 | — | indecidivel | ✗ | falso | jev | Precisa de financiamento; visitou 3 unidades em uma tarde e quer proposta na de 2 quartos. |
| SQ-T13 | OB-029 | verdadeiro | 0.59 | 0.85 | — | indecidivel | ✗ | verdadeiro | jev | Precisa de resposta hoje sobre a proposta, senão perde o imóvel que viu com outra imobiliária. |
| SQ-T13 | OB-071 | verdadeiro | 0.73 | 0.96 | — | indecidivel | ✗ | verdadeiro | jev | Cliente reclamou que ficou 3 dias sem resposta e que quase fechou com outra imobiliária. Pediu desculpas em no… |
| SQ-T13 | OB-084 | indecidivel | 0.21 | 0.68 | — | falso | ✗ | falso | jev | Mencionou que 'um conhecido' tem um imóvel pra vender direto. Não sei se é concorrência real. |
| SQ-T13 | OB-085 | verdadeiro | 0.72 | 0.92 | — | indecidivel | ✗ | falso | jev | Vai visitar um lançamento da construtora no sábado e depois decide entre o nosso e o deles. |
| SQ-T13 | OB-086 | falso | 0.54 | 0.94 | — | indecidivel | ✗ | verdadeiro | jev | Disse que largou a outra imobiliária porque não respondiam. Agora é só com a gente. |
| SQ-T13 | OB-116 | falso | 0.41 | 0.76 | — | indecidivel | ✗ | falso | jev | Afirmou que o aluguel pedido é quase o dobro do que paga hoje; segue na busca por algo menor. |
| SQ-T13 | OB-174 | falso | 0.34 | 0.41 | — | indecidivel | ✗ | falso | jev | Disse que não está vendo com mais ninguém e não tem pressa; prefere receber opções por e-mail uma vez por sema… |
| SQ-T13 | OB-185 | falso | 0.32 | 0.42 | — | indecidivel | ✗ | falso | jev | Encerrou a busca depois da terceira visita; tudo acima do orçamento dela, não quer mais receber anúncios. |
| SQ-T14 | OB-002 | falso | 0.19 | 0.71 | 0.06, 0.26 | indecidivel | ✗ | verdadeiro | jev | Está vindo de Belo Horizonte com a família no começo do ano, quer casa com quintal. Orçamento folgado, paga à … |
| SQ-T14 | OB-018 | falso | 0.45 | 0.78 | 0.05, 0.37 | indecidivel | ✗ | verdadeiro | jev | A casa está com tudo renovado, dono trocou até o telhado em 2025. Cliente só achou pequeno pra família. |
| SQ-T14 | OB-049 | verdadeiro | 0.42 | 0.72 | 0.04, 0.42 | indecidivel | ✗ | verdadeiro | jev | Disse que o filho cria um coelho e que isso 'não deve ser problema'. |
| SQ-T14 | OB-059 | indecidivel | 0.08 | 0.45 | 0.05, 0.09 | falso | ✗ | falso | jev | Perguntou se o condomínio tem área kids e salão de festas. |
| SQ-T14 | OB-062 | indecidivel | 0.35 | 0.78 | 0.04, 0.04 | indecidivel | ✓ | falso | jev | Comentou que a sobrinha vai morar com eles por uns meses. |
| SQ-T14 | OB-064 | verdadeiro | 0.80 | 0.91 | 0.76, 0.03 | indecidivel | ✗ | falso | jev | Faz atendimento online de manhã, então quer um canto silencioso pra montar o consultório virtual. |
| SQ-T14 | OB-066 | indecidivel | 0.15 | 0.68 | 0.06, 0.04 | falso | ✗ | falso | jev | Pediu que o apto tivesse 'um quarto sobrando'. Não disse pra quê. |
| SQ-T14 | OB-068 | indecidivel | 0.07 | 0.68 | 0.13, 0.04 | falso | ✗ | falso | jev | Perguntou se a região tem boa cobertura de internet. |
| SQ-T14 | OB-094 | verdadeiro | 0.40 | 0.60 | 0.06, 0.21 | falso | ✗ | verdadeiro | jev | Filho autista precisa de ambiente tranquilo e sem escada aberta; busca casa térrea em rua calma. |
| SQ-T14 | OB-102 | falso | 0.29 | 0.55 | 0.49, 0.03 | indecidivel | ✗ | falso | jev | Quer sala comercial pra montar a própria clínica. Uso próprio. |
| SQ-T14 | OB-123 | verdadeiro | 0.58 | 0.86 | 0.05, 0.74 | indecidivel | ✗ | verdadeiro | jev | Quer rua tranquila, sem trânsito pesado, por causa do sono do bebê. |
| SQ-T14 | OB-125 | falso | 0.48 | 0.68 | 0.53, 0.03 | indecidivel | ✗ | verdadeiro | jev | Músico, toca bateria em casa; precisa de vizinhança tolerante ou casa isolada. |
| SQ-T14 | OB-128 | falso | 0.19 | 0.70 | 0.06, 0.28 | indecidivel | ✗ | falso | jev | Os pais vão pagar a entrada e querem aprovar o imóvel antes. |
| SQ-T14 | OB-135 | verdadeiro | 0.22 | 0.63 | 0.06, 0.21 | falso | ✗ | verdadeiro | jev | Precisa ficar na rota da escola das crianças, bairro vizinho no máximo. |
| SQ-T14 | OB-168 | verdadeiro | 0.60 | 0.82 | 0.11, 0.71 | indecidivel | ✗ | verdadeiro | jev | Quer um apto perto do trabalho dela e da escola do filho; o condomínio não pode cobrar mais de 800. |
| SQ-T15 | OB-012 | falso | 0.36 | 0.56 | — | indecidivel | ✗ | falso | jev | Visitamos o apto da rua das Acácias: piso novo, cozinha planejada recém-instalada, ainda com cheiro de tinta. … |
| SQ-T15 | OB-017 | falso | 0.38 | 0.71 | — | indecidivel | ✗ | falso | jev | Unidade reformada mês passado, mobília nova; o cliente quer entrar sem mexer em nada e gostou disso. |
| SQ-T15 | OB-086 | falso | 0.65 | 0.90 | — | indecidivel | ✗ | falso | jev | Disse que largou a outra imobiliária porque não respondiam. Agora é só com a gente. |
| SQ-T15 | OB-107 | falso | 0.82 | 0.92 | — | verdadeiro | ✗ | verdadeiro | jev | Fechou com outra imobiliária na semana passada. Agradeceu o atendimento. |
| SQ-T15 | OB-127 | falso | 0.52 | 0.52 | — | indecidivel | ✗ | falso | jev | Ele gostou, mas quem bate o martelo é a esposa, que só volta de viagem semana que vem. |
| SQ-T16 | OB-038 | verdadeiro | 0.64 | 0.85 | — | indecidivel | ✗ | falso | jev | Simulação do Santander deu parcela de 3.800; ela quer tentar no Itaú antes de decidir. |
| SQ-T16 | OB-042 | indecidivel | 0.51 | 0.79 | — | indecidivel | ✓ | falso | jev | Perguntou se a gente tem parceria com correspondente bancário. |
| SQ-T16 | OB-110 | falso | 0.31 | 0.34 | — | indecidivel | ✗ | falso | jev | Perdeu o interesse: achou que 900 mil era demais pra 70 m² e não quer ver mais nada. |
| SQ-T16 | OB-116 | falso | 0.28 | 0.71 | — | indecidivel | ✗ | falso | jev | Afirmou que o aluguel pedido é quase o dobro do que paga hoje; segue na busca por algo menor. |
| SQ-T16 | OB-169 | verdadeiro | 0.45 | 0.85 | — | indecidivel | ✗ | falso | jev | Fez duas visitas, elogiou a pontualidade da equipe, mas disse que vai esperar o fim do ano por causa dos juros… |
| SQ-T16 | OB-174 | falso | 0.32 | 0.42 | — | indecidivel | ✗ | falso | jev | Disse que não está vendo com mais ninguém e não tem pressa; prefere receber opções por e-mail uma vez por sema… |
| SQ-T16 | OB-185 | falso | 0.43 | 0.53 | — | indecidivel | ✗ | falso | jev | Encerrou a busca depois da terceira visita; tudo acima do orçamento dela, não quer mais receber anúncios. |
| SQ-T17 | OB-014 | falso | 0.43 | 0.87 | 0.44, 0.48 | indecidivel | ✗ | falso | jev | Mostrei a casa do Jardim Europa, toda repaginada pelo dono há uns meses, janelas e portas trocadas. Ela achou … |
| SQ-T17 | OB-020 | falso | 0.47 | 0.80 | 0.42, 0.39 | indecidivel | ✗ | verdadeiro | jev | O apto está original de 1998, nunca foi mexido. Ele topa reformar se o preço cair. |
| SQ-T17 | OB-021 | falso | 0.10 | 0.72 | 0.11, 0.12 | indecidivel | ✗ | falso | jev | Anúncio diz 'oportunidade para reforma'. Cliente perguntou quanto custaria deixar habitável. |
| SQ-T17 | OB-027 | falso | 0.41 | 0.83 | 0.41, 0.43 | indecidivel | ✗ | falso | jev | Disse que não tem pressa alguma, mora com os pais e vai esperar o mercado baixar. |
| SQ-T17 | OB-079 | falso | 0.11 | 0.77 | 0.11, 0.11 | indecidivel | ✗ | falso | jev | Ficou em silêncio depois que mandei o valor do condomínio. |
| SQ-T17 | OB-082 | falso | 0.27 | 0.82 | 0.33, 0.26 | indecidivel | ✗ | falso | jev | Viu um apto parecido com outro corretor na mesma rua por 40 mil a menos. Pediu pra cobrir. |
| SQ-T17 | OB-103 | falso | 0.28 | 0.47 | 0.41, 0.88 | indecidivel | ✗ | verdadeiro | jev | Desistiu da busca: vai renovar o aluguel atual por mais um ano. Pediu pra tirar da lista. |
| SQ-T17 | OB-108 | falso | 0.25 | 0.65 | 0.34, 0.55 | indecidivel | ✗ | falso | jev | Disse que pausou a procura até vender o carro. Deve voltar em dois meses. |
| SQ-T17 | OB-111 | falso | 0.65 | 0.90 | 0.64, 0.64 | indecidivel | ✗ | falso | jev | Avisou que vai ficar onde está, reformar a casa atual sai mais barato. |
| SQ-T17 | OB-112 | falso | 0.46 | 0.88 | 0.48, 0.39 | indecidivel | ✗ | falso | jev | Achou o valor do condomínio um absurdo, 1.400 por mês num prédio sem lazer. |
| SQ-T17 | OB-114 | falso | 0.89 | 0.94 | 0.83, 0.79 | indecidivel | ✗ | falso | jev | Disse que o metro quadrado da região 'está fora da realidade' e que vai olhar mais longe. |
| SQ-T17 | OB-116 | falso | 0.31 | 0.75 | 0.44, 0.24 | indecidivel | ✗ | verdadeiro | jev | Afirmou que o aluguel pedido é quase o dobro do que paga hoje; segue na busca por algo menor. |
| SQ-T17 | OB-118 | falso | 0.36 | 0.87 | 0.42, 0.31 | indecidivel | ✗ | falso | jev | Comentou que a parcela ficaria pesada demais com os juros atuais. |
| SQ-T17 | OB-119 | falso | 0.30 | 0.82 | 0.28, 0.26 | indecidivel | ✗ | falso | jev | Pediu um imóvel 'mais em conta' que os três que mostrei. |
| SQ-T17 | OB-164 | falso | 0.37 | 0.76 | 0.34, 0.31 | indecidivel | ✗ | verdadeiro | jev | Decisão é do marido, que acha tudo caro; ela gostaria de fechar logo. |
| SQ-T17 | OB-169 | falso | 0.37 | 0.73 | 0.36, 0.39 | indecidivel | ✗ | falso | jev | Fez duas visitas, elogiou a pontualidade da equipe, mas disse que vai esperar o fim do ano por causa dos juros… |
| SQ-T18 | OB-048 | indecidivel | 0.22 | 0.79 | — | indecidivel | ✓ | verdadeiro | jev | Cliente perguntou das regras do condomínio pra animais, 'por curiosidade'. |
