# Rascunho — selecao-de-skill (encanamento)

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, limiares, variante principal e critério: `perguntas.py`; validação, decisão e baseline: `selecao.py`; bateria do código (sem API): `testa_falhas.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Limiares: {'porta': 0.2, 'fits': 0.5, 'fits_todos': 0.5, 'baseline': 4.0}; shortlist 3; descrição curta 60 caracteres; teto do pedido 600 caracteres.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (87 pedidos: 24 `null`, 63 com skill), variante principal com os limiares acima; **variante_principal**: b; **1_skill_indevida**: carregou skill com gabarito `null` ≤ 2/24; **2_acerto_folgado**: escolha ∈ `aceitaveis` (ou nenhuma quando vazio) ≥ baseline de código (BM25) + 0,20; **3_contra_choice_unica**: acerto folgado ≥ o da Choice única (a) E skill indevida ≤ a dela; **4_null_indevido**: não carregou quando havia skill ≤ 10% (≤ 6/63); **5_skill_errada**: carregou skill fora de `aceitaveis` ≤ 5% (≤ 3/63); **se_falhar**: 1 = a sugestão carrega skill onde não devia: não serve como dica automática; 2 = a sobreposição de palavras basta; 3 = o Noul do vencedor não paga a 2ª requisição: a Choice única faz o mesmo; 4 = a etapa cala demais (o agente fica sozinho); 5 = sugestão errada e confiante é pior que nenhuma

Versão em afinação (NÃO congelada): `perguntas.py` sha256 963fa924f1683ca5… · `selecao.py` sha256 114f23269487a583… · `run.py` sha256 279c6ee354bb4b60… · `dados/teste.json` sha256 a0fda5b28211387b… · `dados/skills.json` sha256 0d33c8a448652ad0…

## Conjunto `rascunho` — 5 pedidos (arquivo versão 2026-10-01, autor fable); 0 difíceis, 1 com gabarito `null`, 0 sem sugestão por falha operacional ou teto; catálogo de 42 skills

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Escolha — baseline de código × variantes com Jev, nos mesmos pedidos

`estrito` = a skill exata do gabarito (ou nenhuma quando o gabarito é `null`). `folgado` = escolha ∈ `aceitaveis` (ou nenhuma quando `aceitaveis` é vazio). **Skill INDEVIDA** = erro caro: carregou skill com gabarito `null` (denominador = pedidos `null`). **Null indevido** = não carregou quando havia skill; **skill errada** = carregou outra, fora de `aceitaveis` (denominador dos dois = pedidos com skill). Custo e latência: só as requisições que a variante envia em produção, medidas. Variante principal (a que o critério julga): **b · Choice + `fits` do vencedor**.

| variante | n | acerto estrito | acerto folgado | skill INDEVIDA | null indevido | skill errada | aceitável (não a melhor) | sem sugestão (falha) | req/pedido | tokens/pedido | US$/1000 | p50_ms | p95_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| código: BM25 + limiar | 5 | 1.000 | 1.000 | 0/1 | 0/4 | 0/4 | 0/4 | 0/5 | 0 | 0 | 0 | 0 | 0 |
| a · Choice única | 5 | 1.000 | 1.000 | 0/1 | 0/4 | 0/4 | 0/4 | 0/5 | 1.00 | 1964 | 0.0825 | 434 | 485 |
| b · Choice + `fits` do vencedor | 5 | 1.000 | 1.000 | 0/1 | 0/4 | 0/4 | 0/4 | 0/5 | 1.80 | 2245 | 0.0943 | 690 | 881 |
| c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`) | 5 | 1.000 | 1.000 | 0/1 | 0/4 | 0/4 | 0/4 | 0/5 | 2.00 | 2871 | 0.1206 | 701 | 751 |
| c2 · receita + portão no vencedor consumido | 5 | 1.000 | 1.000 | 0/1 | 0/4 | 0/4 | 0/4 | 0/5 | 2.00 | 2871 | 0.1206 | 701 | 751 |
| d · receita corrigida (vencedor = maior `fits`) | 5 | 1.000 | 1.000 | 0/1 | 0/4 | 0/4 | 0/4 | 0/5 | 2.00 | 2871 | 0.1206 | 701 | 751 |
| e · um `fits` por skill (42 Nouls) | 5 | 1.000 | 1.000 | 0/1 | 0/4 | 0/4 | 0/4 | 0/5 | 1.00 | 3275 | 0.1375 | 251 | 264 |
| a2 · Choice única com a descrição completa — informativa | 5 | 1.000 | 1.000 | 0/1 | 0/4 | 0/4 | 0/4 | 0/5 | 1.00 | 2572 | 0.1080 | 321 | 374 |
| c com os limiares publicados (porta 0,30; `fits` 0,30) — informativa | 5 | 0.800 | 0.800 | 0/1 | 1/4 | 0/4 | 0/4 | 0/5 | 2.00 | 2871 | 0.1206 | 701 | 751 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 skill indevida (gabarito `null`, carregou skill) | 0/1 (0.000) | ≤ 0.083 | ✓ |
| 2 acerto folgado | 1.000 (baseline de código 1.000) | ≥ 1.200 | ✗ |
| 3 contra a Choice única (a) | folgado 1.000 × 1.000; indevidas 0 × 0 | folgado ≥ e indevidas ≤ | ✓ |
| 4 null indevido (havia skill, não carregou) | 0/4 (0.000) | ≤ 0.100 | ✓ |
| 5 skill errada (carregou outra, fora de `aceitaveis`) | 0/4 (0.000) | ≤ 0.050 | ✓ |

### A ressalva da receita oficial — o portão olha um candidato, o vencedor é outro?

Porta aberta (≥ 0.2) em 4/5 pedidos. Neles, o vencedor da Choice `rerank` e o candidato de maior `fits` são skills DIFERENTES em **0**; nesses, acerto folgado de `c` (fica com a Choice) 0/0 × `d` (fica com o maior `fits`) 0/0. O furo que a ressalva descreve — o maior `fits` passa o portão (≥ 0.5) mas o `fits` do vencedor consumido está abaixo — aconteceu em **0** pedidos; neles, acerto folgado: `c` 0, `c2` (devolve nenhuma) 0, `d` 0 de 0. Decisão final diferente: `c` × `c2` em 0 pedidos, `c` × `d` em 0.

### Por família difícil (pela `nota` do rotulador) — acertos folgados; erros caros da principal

| família | n | `null` | base | a | b | c | c2 | d | e | a2 | indevida (principal) | null indevido (principal) | errada (principal) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fácil / outros | 5 | 1 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 0 | 0 | 0 |

### Os sinais — o `fits` separa "serve" de "não serve"? E as portas da receita?

`fits` (requisição `todos`) da skill do gabarito, nos 4 pedidos com skill: mínimo 0.96, p10 0.96, mediana 0.98. Maior `fits` do catálogo nos 1 pedidos `null` (aqui alto = skill indevida em `e`): mediana 0.28, p90 0.28, máximo 0.28. A skill do gabarito é a de maior `fits` do catálogo em 4/4; está na shortlist da ampla em 4/4 (alguma aceitável: 4/4) — o que a 2ª requisição não recebe, ela não recupera.

Quem aponta a skill certa nos 4 pedidos com skill, sem portão (a 1ª skill do ranking, mesmo quando a Choice preferiu `none`):

| quem aponta | a melhor | alguma aceitável |
|---|---|---|
| ampla, descrição curta (1ª skill do ranking) | 4/4 | 4/4 |
| Choice `rerank`, texto completo, entre as 3 | 4/4 | 4/4 |
| maior `fits` entre as 3 da shortlist | 4/4 | 4/4 |
| maior `fits` entre as 42 | 4/4 | 4/4 |
| ampla, descrição completa (1ª skill do ranking) | 4/4 | 4/4 |

A releitura com o texto completo (`rerank`) trocou a 1ª skill da ampla em 0/4 pedidos com skill: passou a apontar a melhor em 0, deixou de apontá-la em 0.

Porta da receita (média das 3 orientadas; < 0.2 = nenhuma): fechou em 1/1 pedidos `null` e em 0/4 pedidos com skill. Valores nos `null`: mínimo 0.04, mediana 0.04, máximo 0.04; nos com skill: mínimo 0.21, mediana 0.68. A Choice ampla disse `none` em 1/1 pedidos `null` e em 0/4 com skill.

O mesmo Noul em requisições diferentes (isolamento ≠ determinismo): o `fits` do vencedor da ampla foi pedido sozinho (`fits_vencedor`), junto de 2 candidatas (`rerank`) e junto das 42 (`todos`). Diferença absoluta sozinho × `rerank`: média 0.000, máxima 0.000 (n = 4); sozinho × `todos`: média 0.000, máxima 0.000 (n = 4).

### Cobertura × erro por limiar (o portão de cada variante em cada ponto da grade)

**b · Choice + `fits` do vencedor** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.200 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.300 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.400 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.500 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.600 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.700 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.800 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.900 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |

**código: BM25 + limiar** — limiar na pontuação BM25; em uso: 4.0

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.000 | 5/5 | 1/1 | 0/4 | 0/4 | 0.800 | 0.800 |
| 2.000 | 5/5 | 1/1 | 0/4 | 0/4 | 0.800 | 0.800 |
| 3.000 | 5/5 | 1/1 | 0/4 | 0/4 | 0.800 | 0.800 |
| 4.000 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 5.000 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 6.000 | 3/5 | 0/1 | 0/4 | 1/4 | 0.800 | 0.800 |
| 8.000 | 2/5 | 0/1 | 0/4 | 2/4 | 0.600 | 0.600 |

**a · Choice única** — piso na confiança da Choice (a variante medida não tem piso)

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.200 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.300 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.400 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.500 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.600 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.700 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.800 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.900 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |

**c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`)** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.200 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.300 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.400 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.500 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.600 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.700 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.800 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.900 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |

**c2 · receita + portão no vencedor consumido** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.200 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.300 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.400 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.500 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.600 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.700 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.800 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.900 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |

**d · receita corrigida (vencedor = maior `fits`)** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.200 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.300 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.400 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.500 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.600 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.700 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.800 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.900 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |

**e · um `fits` por skill (42 Nouls)** — limiar no maior `fits` do catálogo; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 5/5 | 1/1 | 0/4 | 0/4 | 0.800 | 0.800 |
| 0.200 | 5/5 | 1/1 | 0/4 | 0/4 | 0.800 | 0.800 |
| 0.300 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.400 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.500 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.600 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.700 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.800 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.900 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |

**a2 · Choice única com a descrição completa — informativa** — piso na confiança da Choice (idem)

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.200 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.300 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.400 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.500 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.600 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.700 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.800 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.900 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |

**c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`)** — limiar na PORTA da receita (média das 3 portas orientadas); em uso: 0.2

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.200 | 4/5 | 0/1 | 0/4 | 0/4 | 1.000 | 1.000 |
| 0.300 | 3/5 | 0/1 | 0/4 | 1/4 | 0.800 | 0.800 |
| 0.400 | 3/5 | 0/1 | 0/4 | 1/4 | 0.800 | 0.800 |
| 0.500 | 2/5 | 0/1 | 0/4 | 2/4 | 0.600 | 0.600 |
| 0.600 | 2/5 | 0/1 | 0/4 | 2/4 | 0.600 | 0.600 |
| 0.700 | 1/5 | 0/1 | 0/4 | 3/4 | 0.400 | 0.400 |
| 0.800 | 1/5 | 0/1 | 0/4 | 3/4 | 0.400 | 0.400 |
| 0.900 | 1/5 | 0/1 | 0/4 | 3/4 | 0.400 | 0.400 |

### Custo e latência por formato de requisição (medidos)

| requisição | enviadas | novas (não cache) | tokens por requisição | p50_ms | p95_ms | quem usa |
|---|---|---|---|---|---|---|
| ampla | 5 | 0 | 1964 | 434 | 485 | a, b, c, c2, d |
| fits_vencedor | 4 | 0 | 352 | 262 | 396 | b |
| rerank | 5 | 0 | 908 | 263 | 272 | c, c2, d |
| todos | 5 | 0 | 3275 | 251 | 264 | e |
| ampla_completa | 5 | 0 | 2572 | 321 | 374 | a2 |

Tudo o que esta execução usou: 24 requisições (0 novas), 44996 tokens, US$ 0.0019 · modelo: jev-1.13.0. Latência = a da chamada original de cada requisição (o cache a guarda), medida com 8 pedidos em paralelo.

### Caso a caso

Marca: ✓ a melhor · ≈ aceitável · ✓∅ nenhuma (certo) · ✗I skill INDEVIDA · ✗N null indevido · ✗E skill errada · ✗F sem sugestão por falha. `ampla` = vencedor (confiança; p(`none`)); `fits venc.` = Noul pedido sozinho; `shortlist` = as 3 da ampla com o `fits` de cada uma na `rerank`; `rerank` = vencedor (confiança); `porta` = média das 3 portas; `e` = skill de maior `fits` do catálogo (valor); `a2` = Choice com descrição completa (confiança).

| id | fam | gabarito | outras aceitáveis | base | a | ampla | fits venc. | b | shortlist | rerank | porta | c | c2 | d | e | a2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SS-R001 | fácil / outros | code-review | — | code-review ✓ | code-review ✓ | code-review (0.99; 0.01) | 0.98 | code-review ✓ | code-review 0.98 · security-review 0.32 · simplify 0.40 | code-review (1.00) | 0.68 | code-review ✓ | code-review ✓ | code-review ✓ | code-review ✓ [code-review 0.98] | code-review ✓ (1.00) |
| SS-R002 | fácil / outros | test-writer | — | test-writer ✓ | test-writer ✓ | test-writer (0.99; 0.01) | 0.97 | test-writer ✓ | test-writer 0.97 · code-review 0.04 · security-review 0.02 | test-writer (1.00) | 0.44 | test-writer ✓ | test-writer ✓ | test-writer ✓ | test-writer ✓ [test-writer 0.97] | test-writer ✓ (1.00) |
| SS-R003 | fácil / outros | ad-creative | — | ad-creative ✓ | ad-creative ✓ | ad-creative (1.00; 0.00) | 0.98 | ad-creative ✓ | ad-creative 0.98 · code-review 0.01 · security-review 0.01 | ad-creative (1.00) | 0.21 | ad-creative ✓ | ad-creative ✓ | ad-creative ✓ | ad-creative ✓ [ad-creative 0.98] | ad-creative ✓ (1.00) |
| SS-R004 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (1.00; 1.00) | — | ∅ ✓∅ | code-review 0.04 · security-review 0.02 · simplify 0.04 | simplify (0.42) | 0.04 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [docs-writer 0.28] | ∅ ✓∅ (1.00) |
| SS-R005 | fácil / outros | deploy-dev | — | deploy-dev ✓ | deploy-dev ✓ | deploy-dev (0.99; 0.00) | 0.96 | deploy-dev ✓ | deploy-dev 0.96 · code-review 0.02 · security-review 0.03 | deploy-dev (1.00) | 0.90 | deploy-dev ✓ | deploy-dev ✓ | deploy-dev ✓ | deploy-dev ✓ [deploy-dev 0.96] | deploy-dev ✓ (1.00) |
