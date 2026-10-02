# Rascunho — sql-semantico (encanamento)

## Conjunto `rascunho` — 5 condições × 187 linhas (arquivo versão 2026-10-01, autor fable); 0 difíceis; 61 verdadeiras e 9 indecidíveis no gabarito

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Total (micro, sobre as linhas decidíveis de todas as condições) — Jev × variantes × baseline LIKE

P/R/F1 sobre as decidíveis que o sistema DECIDIU; `humano` = decidíveis mandadas a `indecidivel` (fora de P/R/F1; `F1 estrito` as conta como erro). **PERDIDAS** = verdadeira do gabarito que saiu `falso` (o filtro perdeu a linha). **FP EM NEGAÇÃO** = falsa marcada `verdadeiro` numa condição da família negação (o erro do LIKE). `indecidíveis → humano` = linhas de pista fraca do gabarito que o sistema mandou revisar (e quantas virou `verdadeiro`). Variante oficial: `clausulas` + pista; faixa de `stated` 0.3–0.8; `hinted` ≥ 0.7.

| variante | decidíveis | decididas | P | R | F1 | F1 estrito (humano = erro) | humano (decidíveis) | PERDIDAS (V → falso) | FP EM NEGAÇÃO | indecidíveis → humano | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev (oficial) | 926 | 885 | 1.000 | 0.980 | 0.990 | 0.881 | 41 (0.044) | 1/61 | 0 | 5/9 (V: 0) | 0 |
| Jev: inteira | 926 | 896 | 1.000 | 0.980 | 0.990 | 0.881 | 30 (0.032) | 1/61 | 0 | 4/9 (V: 0) | 0 |
| Jev: inteira+pista | 926 | 885 | 1.000 | 0.980 | 0.990 | 0.881 | 41 (0.044) | 1/61 | 0 | 5/9 (V: 0) | 0 |
| Jev: cláusulas | 926 | 896 | 1.000 | 0.980 | 0.990 | 0.881 | 30 (0.032) | 1/61 | 0 | 4/9 (V: 0) | 0 |
| Jev: cláusulas+pista | 926 | 885 | 1.000 | 0.980 | 0.990 | 0.881 | 41 (0.044) | 1/61 | 0 | 5/9 (V: 0) | 0 |
| baseline LIKE | 926 | 926 | 0.652 | 0.246 | 0.357 | 0.357 | 0 (0.000) | 46/61 | 0 | 0/9 (V: 3) | 0 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 F1 (decididas) | 0.990 (baseline 0.357) | ≥ 0.85 e ≥ 0.507 | ✓ |
| 2 perdidas (V → falso) | 1/61 (0.016) | ≤ 0.05 | ✓ |
| 3 FP em negação | 0 | ≤ 2 | ✓ |
| 4 humano (decidíveis) | 41/926 (0.044) | ≤ 0.08 | ✓ |
| secundário: indecidíveis → humano | 5/9 | ≥ 0.5 | ✓ |
| secundário: falhas operacionais | 0 | 0 | ✓ |

### Por condição

`filtro` = parte de campo resolvida pelo código; `chamadas` = linhas que passaram no filtro e foram ao Jev; `V/I` = verdadeiras / indecidíveis do gabarito; `base` = baseline LIKE (radicais entre colchetes).

| id | família | filtro | composta | chamadas | V/I | P | R | F1 | humano | perdidas | FP | I → humano | base F1 | base FP | base perdidas | LIKE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SQ-R01 | fácil | — | — | 187 | 13/2 | 1.000 | 0.857 | 0.923 | 16 | 1 | 0 | 0/2 | 0.235 | 2 | 11 | [mudar, cidad] |
| SQ-R02 | fácil | — | — | 187 | 10/2 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 | 2/2 | 0.000 | 2 | 10 | [anima, estim] |
| SQ-R03 | fácil | — | — | 187 | 15/1 | 1.000 | 1.000 | 1.000 | 16 | 0 | 0 | 0/1 | 0.316 | 1 | 12 | [achar, valor, alto] |
| SQ-R04 | fácil | finalidade = compra | — | 123 | 15/2 | 1.000 | 1.000 | 1.000 | 4 | 0 | 0 | 2/2 | 0.714 | 3 | 5 | [depen, finan, banca] |
| SQ-R05 | fácil | — | — | 187 | 8/2 | 1.000 | 1.000 | 1.000 | 3 | 0 | 0 | 1/2 | 0.000 | 0 | 8 | [neces, acess] |

### Por família difícil (pela `nota` do rotulador)

| família | condições | F1 Jev | F1 baseline | humano Jev | perdidas Jev | FP Jev | perdidas base | FP base | I → humano |
|---|---|---|---|---|---|---|---|---|---|
| fácil | 5 | 0.990 | 0.357 | 41 | 1 | 0 | 46 | 8 | 5/9 |

### Onde `stated` cai, por gabarito (só linhas que foram ao Jev)

| gabarito | n | stated mín | p10 | p50 | p90 | máx | ≤ 0,2 | 0,2–0,8 | ≥ 0,8 | hinted p50 | hinted ≥ 0,8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| verdadeiro | 61 | 0.130 | 0.670 | 0.930 | 0.970 | 0.980 | 1 | 12 | 48 | 0.960 | 60 |
| falso | 801 | 0.030 | 0.040 | 0.050 | 0.150 | 0.760 | 758 | 43 | 0 | 0.140 | 11 |
| indecidivel | 9 | 0.070 | 0.070 | 0.300 | 0.510 | 0.510 | 4 | 5 | 0 | 0.820 | 5 |

### Cobertura × erro por faixa de `stated` (variante oficial; mesmas respostas, outra faixa)

| faixa | cobertura (decididas/decidíveis) | erro entre decididas | F1 | humano | perdidas | FP em negação | I → humano |
|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.956 | 0.001 | 0.990 | 41 | 1 | 0 | 5/9 |
| 0.5–0.5 | 0.982 | 0.009 | 0.937 | 17 | 1 | 0 | 4/9 |
| 0.4–0.6 | 0.974 | 0.007 | 0.949 | 24 | 1 | 0 | 5/9 |
| 0.3–0.7 | 0.965 | 0.004 | 0.964 | 32 | 1 | 0 | 5/9 |
| 0.2–0.8 | 0.936 | 0.001 | 0.990 | 59 | 1 | 0 | 5/9 |
| 0.1–0.9 | 0.819 | 0.000 | 1.000 | 168 | 0 | 0 | 7/9 |

### Custo e latência (medidos na chamada real; do cache também)

| linhas avaliadas (cond × linha) | sem chamada (filtro) | requisicoes | novas (não cache) | textos longos (sem chamada) | falhas operacionais (→ indecidivel) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_1000_linhas_avaliadas | US$_por_1000_requisicoes | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 935 | 64 | 871 | 0 | 0 | 0 | 1742 | 249 | 317 | 948 | 0.034681 | 0.0371 | 0.0398 | jev-1.13.0 |

### Caso a caso — erros, linhas mandadas a humano e indecidíveis do gabarito

`st`/`hi` = Nouls `stated` e `hinted`; `partes` = Nouls por cláusula (compostas); `saída` = variante oficial; `base` = LIKE.

| cond | linha | gab | st | hi | partes | saída | ok | base | por | texto |
|---|---|---|---|---|---|---|---|---|---|---|
| SQ-R01 | OB-001 | verdadeiro | 0.72 | 0.91 | — | indecidivel | ✗ | falso | jev | Cliente ligou de Curitiba: a empresa transferiu ele pra cá e precisa de apartamento pronto pra morar. Vai fina… |
| SQ-R01 | OB-007 | verdadeiro | 0.53 | 0.90 | — | indecidivel | ✗ | falso | jev | Veio de Manaus há duas semanas, está em hotel e precisa fechar aluguel até sexta. Documentação já em mãos. |
| SQ-R01 | OB-008 | indecidivel | 0.18 | 0.59 | — | falso | ✗ | falso | jev | Cliente comentou que a filha vai prestar vestibular em São Paulo; por enquanto procura só pra ele aqui, 2 quar… |
| SQ-R01 | OB-009 | indecidivel | 0.17 | 0.68 | — | falso | ✗ | falso | jev | Perguntou se o condomínio tem portaria 24h e se a região é bem servida de ônibus pra rodoviária. |
| SQ-R01 | OB-028 | falso | 0.21 | 0.80 | — | indecidivel | ✗ | falso | jev | Pediu pra agilizar a documentação porque o bebê nasce em janeiro e quer estar instalada antes. |
| SQ-R01 | OB-055 | falso | 0.21 | 0.87 | — | indecidivel | ✗ | falso | jev | Grávida de 6 meses, quer 3 quartos e escola perto. Marido vai ver as opções no fim de semana. |
| SQ-R01 | OB-058 | falso | 0.19 | 0.76 | — | indecidivel | ✗ | falso | jev | Está com um filho de 4 anos e outro a caminho; o atual ficou pequeno. |
| SQ-R01 | OB-097 | falso | 0.39 | 0.60 | — | indecidivel | ✗ | falso | jev | É pra morar mesmo, primeira casa. Nada de investimento. |
| SQ-R01 | OB-114 | falso | 0.76 | 0.89 | — | indecidivel | ✗ | falso | jev | Disse que o metro quadrado da região 'está fora da realidade' e que vai olhar mais longe. |
| SQ-R01 | OB-138 | falso | 0.36 | 0.79 | — | indecidivel | ✗ | falso | jev | Marido trabalha na zona norte e ela na zona sul; querem algo no meio do caminho. |
| SQ-R01 | OB-153 | verdadeiro | 0.79 | 0.92 | — | indecidivel | ✗ | falso | jev | Vem transferida de Brasília em janeiro, prazo apertado: a empresa só paga hotel por 15 dias. Financia 80%. |
| SQ-R01 | OB-154 | verdadeiro | 0.60 | 0.90 | — | indecidivel | ✗ | falso | jev | Estudante vindo de Goiânia, precisa alugar antes das aulas em fevereiro; os pais assinam o contrato. |
| SQ-R01 | OB-160 | verdadeiro | 0.52 | 0.85 | — | indecidivel | ✗ | falso | jev | Família com três crianças pequenas vindo do interior; o pai trabalha em casa e quer um escritório longe dos qu… |
| SQ-R01 | OB-163 | falso | 0.69 | 0.89 | — | indecidivel | ✗ | falso | jev | Mãe idosa com dificuldade de locomoção vai morar junto, e o apto da rua de trás tem obra que não acaba: quer t… |
| SQ-R01 | OB-168 | falso | 0.27 | 0.82 | — | indecidivel | ✗ | falso | jev | Quer um apto perto do trabalho dela e da escola do filho; o condomínio não pode cobrar mais de 800. |
| SQ-R01 | OB-170 | verdadeiro | 0.13 | 0.37 | — | falso | ✗ | falso | jev | Chegou da Argentina mês passado, ainda sem CPF regularizado; pediu locação temporária de 6 meses. |
| SQ-R01 | OB-178 | verdadeiro | 0.79 | 0.96 | — | indecidivel | ✗ | verdadeiro | jev | Mudança de cidade confirmada pra março e precisa resolver o aluguel antes de fevereiro; orçamento até 3 mil. |
| SQ-R01 | OB-181 | falso | 0.42 | 0.87 | — | indecidivel | ✗ | falso | jev | Trouxe o pai de 79 anos pra morar junto e procura locação de térreo com banheiro adaptado. |
| SQ-R01 | OB-186 | falso | 0.71 | 0.85 | — | indecidivel | ✗ | verdadeiro | jev | Achou o aluguel pedido fora da realidade e desistiu de se mudar por enquanto. |
| SQ-R02 | OB-002 | falso | 0.08 | 0.74 | — | indecidivel | ✗ | falso | jev | Está vindo de Belo Horizonte com a família no começo do ano, quer casa com quintal. Orçamento folgado, paga à … |
| SQ-R02 | OB-048 | indecidivel | 0.31 | 0.82 | — | indecidivel | ✓ | verdadeiro | jev | Cliente perguntou das regras do condomínio pra animais, 'por curiosidade'. |
| SQ-R02 | OB-052 | indecidivel | 0.43 | 0.84 | — | indecidivel | ✓ | falso | jev | Perguntou se há pet shop perto do condomínio. |
| SQ-R02 | OB-054 | falso | 0.35 | 0.65 | — | indecidivel | ✗ | falso | jev | Alérgico a pelo, descartou unidade onde o antigo morador tinha gato. |
| SQ-R03 | OB-013 | falso | 0.09 | 0.71 | — | indecidivel | ✗ | falso | jev | O imóvel oferecido passou por reforma completa no ano passado (elétrica, hidráulica, banheiros). Mandei as fot… |
| SQ-R03 | OB-019 | falso | 0.47 | 0.64 | — | indecidivel | ✗ | falso | jev | Imóvel precisa de reforma geral, infiltração no quarto e piso solto. Cliente descartou na hora. |
| SQ-R03 | OB-020 | falso | 0.72 | 0.87 | — | indecidivel | ✗ | falso | jev | O apto está original de 1998, nunca foi mexido. Ele topa reformar se o preço cair. |
| SQ-R03 | OB-021 | falso | 0.23 | 0.74 | — | indecidivel | ✗ | falso | jev | Anúncio diz 'oportunidade para reforma'. Cliente perguntou quanto custaria deixar habitável. |
| SQ-R03 | OB-027 | falso | 0.32 | 0.78 | — | indecidivel | ✗ | falso | jev | Disse que não tem pressa alguma, mora com os pais e vai esperar o mercado baixar. |
| SQ-R03 | OB-037 | falso | 0.55 | 0.86 | — | indecidivel | ✗ | falso | jev | Vai pagar à vista, dinheiro da herança já está na conta. Só quer desconto por isso. |
| SQ-R03 | OB-038 | falso | 0.24 | 0.79 | — | indecidivel | ✗ | falso | jev | Simulação do Santander deu parcela de 3.800; ela quer tentar no Itaú antes de decidir. |
| SQ-R03 | OB-079 | falso | 0.10 | 0.77 | — | indecidivel | ✗ | verdadeiro | jev | Ficou em silêncio depois que mandei o valor do condomínio. |
| SQ-R03 | OB-081 | falso | 0.50 | 0.89 | — | indecidivel | ✗ | falso | jev | Está em contato com duas imobiliárias e vai fechar com quem conseguir desconto. Pediu proposta por escrito. |
| SQ-R03 | OB-082 | verdadeiro | 0.71 | 0.95 | — | indecidivel | ✗ | falso | jev | Viu um apto parecido com outro corretor na mesma rua por 40 mil a menos. Pediu pra cobrir. |
| SQ-R03 | OB-111 | falso | 0.47 | 0.76 | — | indecidivel | ✗ | falso | jev | Avisou que vai ficar onde está, reformar a casa atual sai mais barato. |
| SQ-R03 | OB-115 | indecidivel | 0.07 | 0.66 | — | falso | ✗ | falso | jev | Perguntou se o proprietário aceita negociação. Não disse se achou caro. |
| SQ-R03 | OB-118 | verdadeiro | 0.71 | 0.92 | — | indecidivel | ✗ | falso | jev | Comentou que a parcela ficaria pesada demais com os juros atuais. |
| SQ-R03 | OB-119 | verdadeiro | 0.67 | 0.92 | — | indecidivel | ✗ | falso | jev | Pediu um imóvel 'mais em conta' que os três que mostrei. |
| SQ-R03 | OB-149 | falso | 0.21 | 0.76 | — | indecidivel | ✗ | falso | jev | Cliente perguntou sobre IPTU e taxa de condomínio da unidade 3 quartos; vai comparar com outra. |
| SQ-R03 | OB-168 | falso | 0.28 | 0.75 | — | indecidivel | ✗ | falso | jev | Quer um apto perto do trabalho dela e da escola do filho; o condomínio não pode cobrar mais de 800. |
| SQ-R03 | OB-169 | falso | 0.48 | 0.77 | — | indecidivel | ✗ | falso | jev | Fez duas visitas, elogiou a pontualidade da equipe, mas disse que vai esperar o fim do ano por causa dos juros… |
| SQ-R04 | OB-038 | verdadeiro | 0.70 | 0.93 | — | indecidivel | ✗ | falso | jev | Simulação do Santander deu parcela de 3.800; ela quer tentar no Itaú antes de decidir. |
| SQ-R04 | OB-041 | indecidivel | 0.46 | 0.90 | — | indecidivel | ✓ | verdadeiro | jev | Quer saber se o imóvel aceita financiamento, mas ainda não decidiu se vai financiar ou usar a venda do carro m… |
| SQ-R04 | OB-042 | indecidivel | 0.51 | 0.92 | — | indecidivel | ✓ | verdadeiro | jev | Perguntou se a gente tem parceria com correspondente bancário. |
| SQ-R04 | OB-118 | verdadeiro | 0.51 | 0.89 | — | indecidivel | ✗ | falso | jev | Comentou que a parcela ficaria pesada demais com os juros atuais. |
| SQ-R04 | OB-169 | verdadeiro | 0.42 | 0.80 | — | indecidivel | ✗ | falso | jev | Fez duas visitas, elogiou a pontualidade da equipe, mas disse que vai esperar o fim do ano por causa dos juros… |
| SQ-R04 | OB-184 | falso | 0.47 | 0.47 | — | indecidivel | ✗ | falso | jev | Desistiu: os valores da região passaram do que ele consegue pagar e vai ficar no aluguel atual. |
| SQ-R05 | OB-054 | falso | 0.33 | 0.47 | — | indecidivel | ✗ | falso | jev | Alérgico a pelo, descartou unidade onde o antigo morador tinha gato. |
| SQ-R05 | OB-056 | falso | 0.60 | 0.88 | — | indecidivel | ✗ | falso | jev | Casal com gêmeos de 2 anos, procura condomínio com playground e piso que não seja escada aberta. |
| SQ-R05 | OB-089 | indecidivel | 0.30 | 0.85 | — | indecidivel | ✓ | falso | jev | Perguntou se o prédio tem elevador. Não explicou o motivo. |
| SQ-R05 | OB-090 | falso | 0.40 | 0.47 | — | indecidivel | ✗ | falso | jev | Não tem restrição de escada, pode ser até 4º andar sem elevador. |
| SQ-R05 | OB-093 | indecidivel | 0.09 | 0.24 | — | falso | ✗ | falso | jev | Pai idoso visita com frequência, mas 'ele sobe escada numa boa'. |
