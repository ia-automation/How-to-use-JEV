# Resultados — selecao-de-skill

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, limiares, variante principal e critério: `perguntas.py`; validação, decisão e baseline: `selecao.py`; bateria do código (sem API): `testa_falhas.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Limiares: {'porta': 0.2, 'fits': 0.5, 'fits_todos': 0.5, 'baseline': 4.0}; shortlist 3; descrição curta 60 caracteres; teto do pedido 600 caracteres.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (87 pedidos: 24 `null`, 63 com skill), variante principal com os limiares acima; **variante_principal**: b; **1_skill_indevida**: carregou skill com gabarito `null` ≤ 2/24; **2_acerto_folgado**: escolha ∈ `aceitaveis` (ou nenhuma quando vazio) ≥ baseline de código (BM25) + 0,20; **3_contra_choice_unica**: acerto folgado ≥ o da Choice única (a) E skill indevida ≤ a dela; **4_null_indevido**: não carregou quando havia skill ≤ 10% (≤ 6/63); **5_skill_errada**: carregou skill fora de `aceitaveis` ≤ 5% (≤ 3/63); **se_falhar**: 1 = a sugestão carrega skill onde não devia: não serve como dica automática; 2 = a sobreposição de palavras basta; 3 = o Noul do vencedor não paga a 2ª requisição: a Choice única faz o mesmo; 4 = a etapa cala demais (o agente fica sozinho); 5 = sugestão errada e confiante é pior que nenhuma

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T14:35:02-03:00): `perguntas.py` sha256 963fa924f1683ca5… · `selecao.py` sha256 114f23269487a583… · `run.py` sha256 279c6ee354bb4b60… · `dados/teste.json` sha256 a0fda5b28211387b… · `dados/skills.json` sha256 0d33c8a448652ad0…

## Lado a lado

| conjunto | variante | n | acerto estrito | acerto folgado | skill INDEVIDA | null indevido | skill errada | aceitável (não a melhor) | sem sugestão (falha) | req/pedido | tokens/pedido | US$/1000 | p50_ms | p95_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | código: BM25 + limiar | 36 | 0.667 | 0.722 | 2/10 | 7/26 | 1/26 | 2/26 | 0/36 | 0 | 0 | 0 | 0 | 0 |
| ajuste | a · Choice única | 36 | 0.833 | 0.917 | 2/10 | 1/26 | 0/26 | 3/26 | 0/36 | 1.00 | 1966 | 0.0826 | 285 | 335 |
| ajuste | b · Choice + `fits` do vencedor | 36 | 0.861 | 0.944 | 1/10 | 1/26 | 0/26 | 3/26 | 0/36 | 1.75 | 2232 | 0.0938 | 527 | 638 |
| ajuste | c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`) | 36 | 0.861 | 0.917 | 3/10 | 0/26 | 0/26 | 2/26 | 0/36 | 2.00 | 2870 | 0.1205 | 536 | 597 |
| ajuste | c2 · receita + portão no vencedor consumido | 36 | 0.861 | 0.917 | 3/10 | 0/26 | 0/26 | 2/26 | 0/36 | 2.00 | 2870 | 0.1205 | 536 | 597 |
| ajuste | d · receita corrigida (vencedor = maior `fits`) | 36 | 0.833 | 0.917 | 3/10 | 0/26 | 0/26 | 3/26 | 0/36 | 2.00 | 2870 | 0.1205 | 536 | 597 |
| ajuste | e · um `fits` por skill (42 Nouls) | 36 | 0.861 | 0.917 | 3/10 | 0/26 | 0/26 | 2/26 | 0/36 | 1.00 | 3276 | 0.1376 | 272 | 366 |
| ajuste | c com os limiares publicados (porta 0,30; `fits` 0,30) — informativa | 36 | 0.778 | 0.833 | 4/10 | 2/26 | 0/26 | 2/26 | 0/36 | 2.00 | 2870 | 0.1205 | 536 | 597 |
| teste | código: BM25 + limiar | 87 | 0.678 | 0.759 | 5/24 | 8/63 | 8/63 | 7/63 | 0/87 | 0 | 0 | 0 | 0 | 0 |
| teste | a · Choice única | 87 | 0.885 | 0.920 | 3/24 | 2/63 | 2/63 | 3/63 | 0/87 | 1.00 | 1965 | 0.0825 | 287 | 438 |
| teste | b · Choice + `fits` do vencedor | 87 | 0.908 | 0.931 | 0/24 | 5/63 | 1/63 | 2/63 | 0/87 | 1.74 | 2225 | 0.0935 | 534 | 714 |
| teste | c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`) | 87 | 0.885 | 0.897 | 3/24 | 4/63 | 2/63 | 1/63 | 0/87 | 2.00 | 2854 | 0.1199 | 555 | 727 |
| teste | c2 · receita + portão no vencedor consumido | 87 | 0.862 | 0.874 | 3/24 | 7/63 | 1/63 | 1/63 | 0/87 | 2.00 | 2854 | 0.1199 | 555 | 727 |
| teste | d · receita corrigida (vencedor = maior `fits`) | 87 | 0.851 | 0.897 | 3/24 | 4/63 | 2/63 | 4/63 | 0/87 | 2.00 | 2854 | 0.1199 | 555 | 727 |
| teste | e · um `fits` por skill (42 Nouls) | 87 | 0.828 | 0.897 | 6/24 | 1/63 | 2/63 | 6/63 | 0/87 | 1.00 | 3276 | 0.1376 | 275 | 364 |
| teste | a2 · Choice única com a descrição completa — informativa | 87 | 0.954 | 0.977 | 1/24 | 1/63 | 0/63 | 2/63 | 0/87 | 1.00 | 2573 | 0.1081 | 263 | 350 |
| teste | c com os limiares publicados (porta 0,30; `fits` 0,30) — informativa | 87 | 0.770 | 0.782 | 6/24 | 11/63 | 2/63 | 1/63 | 0/87 | 2.00 | 2854 | 0.1199 | 555 | 727 |

| conjunto | n | difíceis | gabarito `null` | sem sugestão (falha) | requisições (todas as variantes) | novas (não cache) | tokens | modelo |
|---|---|---|---|---|---|---|---|---|
| ajuste | 36 | 24 | 10 | 0 | 135 | 0 | 230870 | jev-1.13.0 |
| teste | 87 | 43 | 24 | 0 | 412 | 412 | 779803 | jev-1.13.0 |

## Conjunto `ajuste` — 36 pedidos (arquivo versão 2026-10-01, autor fable); 24 difíceis, 10 com gabarito `null`, 0 sem sugestão por falha operacional ou teto; catálogo de 42 skills

> A variante informativa a2 (Choice única com a descrição completa) não foi medida neste conjunto.

### Escolha — baseline de código × variantes com Jev, nos mesmos pedidos

`estrito` = a skill exata do gabarito (ou nenhuma quando o gabarito é `null`). `folgado` = escolha ∈ `aceitaveis` (ou nenhuma quando `aceitaveis` é vazio). **Skill INDEVIDA** = erro caro: carregou skill com gabarito `null` (denominador = pedidos `null`). **Null indevido** = não carregou quando havia skill; **skill errada** = carregou outra, fora de `aceitaveis` (denominador dos dois = pedidos com skill). Custo e latência: só as requisições que a variante envia em produção, medidas. Variante principal (a que o critério julga): **b · Choice + `fits` do vencedor**.

| variante | n | acerto estrito | acerto folgado | skill INDEVIDA | null indevido | skill errada | aceitável (não a melhor) | sem sugestão (falha) | req/pedido | tokens/pedido | US$/1000 | p50_ms | p95_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| código: BM25 + limiar | 36 | 0.667 | 0.722 | 2/10 | 7/26 | 1/26 | 2/26 | 0/36 | 0 | 0 | 0 | 0 | 0 |
| a · Choice única | 36 | 0.833 | 0.917 | 2/10 | 1/26 | 0/26 | 3/26 | 0/36 | 1.00 | 1966 | 0.0826 | 285 | 335 |
| b · Choice + `fits` do vencedor | 36 | 0.861 | 0.944 | 1/10 | 1/26 | 0/26 | 3/26 | 0/36 | 1.75 | 2232 | 0.0938 | 527 | 638 |
| c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`) | 36 | 0.861 | 0.917 | 3/10 | 0/26 | 0/26 | 2/26 | 0/36 | 2.00 | 2870 | 0.1205 | 536 | 597 |
| c2 · receita + portão no vencedor consumido | 36 | 0.861 | 0.917 | 3/10 | 0/26 | 0/26 | 2/26 | 0/36 | 2.00 | 2870 | 0.1205 | 536 | 597 |
| d · receita corrigida (vencedor = maior `fits`) | 36 | 0.833 | 0.917 | 3/10 | 0/26 | 0/26 | 3/26 | 0/36 | 2.00 | 2870 | 0.1205 | 536 | 597 |
| e · um `fits` por skill (42 Nouls) | 36 | 0.861 | 0.917 | 3/10 | 0/26 | 0/26 | 2/26 | 0/36 | 1.00 | 3276 | 0.1376 | 272 | 366 |
| c com os limiares publicados (porta 0,30; `fits` 0,30) — informativa | 36 | 0.778 | 0.833 | 4/10 | 2/26 | 0/26 | 2/26 | 0/36 | 2.00 | 2870 | 0.1205 | 536 | 597 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 skill indevida (gabarito `null`, carregou skill) | 1/10 (0.100) | ≤ 0.083 | ✗ |
| 2 acerto folgado | 0.944 (baseline de código 0.722) | ≥ 0.922 | ✓ |
| 3 contra a Choice única (a) | folgado 0.944 × 0.917; indevidas 1 × 2 | folgado ≥ e indevidas ≤ | ✓ |
| 4 null indevido (havia skill, não carregou) | 1/26 (0.038) | ≤ 0.100 | ✓ |
| 5 skill errada (carregou outra, fora de `aceitaveis`) | 0/26 (0.000) | ≤ 0.050 | ✓ |

### A ressalva da receita oficial — o portão olha um candidato, o vencedor é outro?

Porta aberta (≥ 0.2) em 33/36 pedidos. Neles, o vencedor da Choice `rerank` e o candidato de maior `fits` são skills DIFERENTES em **2**; nesses, acerto folgado de `c` (fica com a Choice) 2/2 × `d` (fica com o maior `fits`) 2/2. O furo que a ressalva descreve — o maior `fits` passa o portão (≥ 0.5) mas o `fits` do vencedor consumido está abaixo — aconteceu em **0** pedidos; neles, acerto folgado: `c` 0, `c2` (devolve nenhuma) 0, `d` 0 de 0. Decisão final diferente: `c` × `c2` em 0 pedidos, `c` × `d` em 1.

| id | gabarito | aceitáveis | vencedor rerank (fits) | maior fits | c | c2 | d | furo |
|---|---|---|---|---|---|---|---|---|
| SS-A009 | security-review | security-review code-review | security-review (0.95) | code-review (0.96) | security-review ✓ | security-review ✓ | code-review ≈ |  |
| SS-A033 | ∅ | — | migration-2bancos (0.06) | db-query (0.08) | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ |  |

### Por família difícil (pela `nota` do rotulador) — acertos folgados; erros caros da principal

| família | n | `null` | base | a | b | c | c2 | d | e | indevida (principal) | null indevido (principal) | errada (principal) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| duas próximas | 9 | 0 | 5 | 9 | 9 | 9 | 9 | 9 | 9 | 0 | 0 | 0 |
| cita o nome de uma skill | 3 | 2 | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 0 | 0 | 0 |
| jargão | 4 | 0 | 1 | 3 | 3 | 4 | 4 | 4 | 4 | 0 | 1 | 0 |
| trivial que parece pedir skill | 3 | 3 | 2 | 3 | 3 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| vago | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
| negação | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| composto | 2 | 0 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |
| fácil / outros | 12 | 3 | 11 | 12 | 12 | 12 | 12 | 12 | 12 | 0 | 0 | 0 |

### Os sinais — o `fits` separa "serve" de "não serve"? E as portas da receita?

`fits` (requisição `todos`) da skill do gabarito, nos 26 pedidos com skill: mínimo 0.51, p10 0.72, mediana 0.93. Maior `fits` do catálogo nos 10 pedidos `null` (aqui alto = skill indevida em `e`): mediana 0.29, p90 0.89, máximo 0.89. A skill do gabarito é a de maior `fits` do catálogo em 24/26; está na shortlist da ampla em 25/26 (alguma aceitável: 26/26) — o que a 2ª requisição não recebe, ela não recupera.

Quem aponta a skill certa nos 26 pedidos com skill, sem portão (a 1ª skill do ranking, mesmo quando a Choice preferiu `none`):

| quem aponta | a melhor | alguma aceitável |
|---|---|---|
| ampla, descrição curta (1ª skill do ranking) | 23/26 | 26/26 |
| Choice `rerank`, texto completo, entre as 3 | 24/26 | 26/26 |
| maior `fits` entre as 3 da shortlist | 23/26 | 26/26 |
| maior `fits` entre as 42 | 24/26 | 26/26 |

A releitura com o texto completo (`rerank`) trocou a 1ª skill da ampla em 1/26 pedidos com skill: passou a apontar a melhor em 1, deixou de apontá-la em 0 (SS-A009: code-review → security-review).

Porta da receita (média das 3 orientadas; < 0.2 = nenhuma): fechou em 3/10 pedidos `null` e em 0/26 pedidos com skill. Valores nos `null`: mínimo 0.06, mediana 0.46, máximo 0.86; nos com skill: mínimo 0.24, mediana 0.63. A Choice ampla disse `none` em 8/10 pedidos `null` e em 1/26 com skill.

O mesmo Noul em requisições diferentes (isolamento ≠ determinismo): o `fits` do vencedor da ampla foi pedido sozinho (`fits_vencedor`), junto de 2 candidatas (`rerank`) e junto das 42 (`todos`). Diferença absoluta sozinho × `rerank`: média 0.009, máxima 0.030 (n = 27); sozinho × `todos`: média 0.006, máxima 0.050 (n = 27).

### Cobertura × erro por limiar (o portão de cada variante em cada ponto da grade)

**b · Choice + `fits` do vencedor** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 26/36 | 1/10 | 0/26 | 1/26 | 0.944 | 0.861 |
| 0.200 | 26/36 | 1/10 | 0/26 | 1/26 | 0.944 | 0.861 |
| 0.300 | 26/36 | 1/10 | 0/26 | 1/26 | 0.944 | 0.861 |
| 0.400 | 26/36 | 1/10 | 0/26 | 1/26 | 0.944 | 0.861 |
| 0.500 | 26/36 | 1/10 | 0/26 | 1/26 | 0.944 | 0.861 |
| 0.600 | 26/36 | 1/10 | 0/26 | 1/26 | 0.944 | 0.861 |
| 0.700 | 25/36 | 1/10 | 0/26 | 2/26 | 0.917 | 0.833 |
| 0.800 | 21/36 | 0/10 | 0/26 | 5/26 | 0.861 | 0.778 |
| 0.900 | 16/36 | 0/10 | 0/26 | 10/26 | 0.722 | 0.667 |

**código: BM25 + limiar** — limiar na pontuação BM25; em uso: 4.0

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.000 | 33/36 | 7/10 | 7/26 | 0/26 | 0.611 | 0.556 |
| 2.000 | 33/36 | 7/10 | 7/26 | 0/26 | 0.611 | 0.556 |
| 3.000 | 29/36 | 5/10 | 5/26 | 2/26 | 0.667 | 0.611 |
| 4.000 | 21/36 | 2/10 | 1/26 | 7/26 | 0.722 | 0.667 |
| 5.000 | 17/36 | 1/10 | 0/26 | 10/26 | 0.694 | 0.667 |
| 6.000 | 14/36 | 1/10 | 0/26 | 13/26 | 0.611 | 0.583 |
| 8.000 | 8/36 | 0/10 | 0/26 | 18/26 | 0.500 | 0.500 |

**a · Choice única** — piso na confiança da Choice (a variante medida não tem piso)

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 27/36 | 2/10 | 0/26 | 1/26 | 0.917 | 0.833 |
| 0.200 | 27/36 | 2/10 | 0/26 | 1/26 | 0.917 | 0.833 |
| 0.300 | 27/36 | 2/10 | 0/26 | 1/26 | 0.917 | 0.833 |
| 0.400 | 26/36 | 1/10 | 0/26 | 1/26 | 0.944 | 0.861 |
| 0.500 | 26/36 | 1/10 | 0/26 | 1/26 | 0.944 | 0.861 |
| 0.600 | 26/36 | 1/10 | 0/26 | 1/26 | 0.944 | 0.861 |
| 0.700 | 25/36 | 1/10 | 0/26 | 2/26 | 0.917 | 0.861 |
| 0.800 | 25/36 | 1/10 | 0/26 | 2/26 | 0.917 | 0.861 |
| 0.900 | 23/36 | 0/10 | 0/26 | 3/26 | 0.917 | 0.861 |

**c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`)** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 31/36 | 5/10 | 0/26 | 0/26 | 0.861 | 0.806 |
| 0.200 | 30/36 | 4/10 | 0/26 | 0/26 | 0.889 | 0.833 |
| 0.300 | 30/36 | 4/10 | 0/26 | 0/26 | 0.889 | 0.833 |
| 0.400 | 29/36 | 3/10 | 0/26 | 0/26 | 0.917 | 0.861 |
| 0.500 | 29/36 | 3/10 | 0/26 | 0/26 | 0.917 | 0.861 |
| 0.600 | 28/36 | 3/10 | 0/26 | 1/26 | 0.889 | 0.833 |
| 0.700 | 27/36 | 3/10 | 0/26 | 2/26 | 0.861 | 0.806 |
| 0.800 | 23/36 | 2/10 | 0/26 | 5/26 | 0.806 | 0.750 |
| 0.900 | 17/36 | 1/10 | 0/26 | 10/26 | 0.694 | 0.667 |

**c2 · receita + portão no vencedor consumido** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 31/36 | 5/10 | 0/26 | 0/26 | 0.861 | 0.806 |
| 0.200 | 30/36 | 4/10 | 0/26 | 0/26 | 0.889 | 0.833 |
| 0.300 | 30/36 | 4/10 | 0/26 | 0/26 | 0.889 | 0.833 |
| 0.400 | 29/36 | 3/10 | 0/26 | 0/26 | 0.917 | 0.861 |
| 0.500 | 29/36 | 3/10 | 0/26 | 0/26 | 0.917 | 0.861 |
| 0.600 | 28/36 | 3/10 | 0/26 | 1/26 | 0.889 | 0.833 |
| 0.700 | 27/36 | 3/10 | 0/26 | 2/26 | 0.861 | 0.806 |
| 0.800 | 23/36 | 2/10 | 0/26 | 5/26 | 0.806 | 0.750 |
| 0.900 | 17/36 | 1/10 | 0/26 | 10/26 | 0.694 | 0.667 |

**d · receita corrigida (vencedor = maior `fits`)** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 31/36 | 5/10 | 0/26 | 0/26 | 0.861 | 0.778 |
| 0.200 | 30/36 | 4/10 | 0/26 | 0/26 | 0.889 | 0.806 |
| 0.300 | 30/36 | 4/10 | 0/26 | 0/26 | 0.889 | 0.806 |
| 0.400 | 29/36 | 3/10 | 0/26 | 0/26 | 0.917 | 0.833 |
| 0.500 | 29/36 | 3/10 | 0/26 | 0/26 | 0.917 | 0.833 |
| 0.600 | 28/36 | 3/10 | 0/26 | 1/26 | 0.889 | 0.806 |
| 0.700 | 27/36 | 3/10 | 0/26 | 2/26 | 0.861 | 0.778 |
| 0.800 | 23/36 | 2/10 | 0/26 | 5/26 | 0.806 | 0.722 |
| 0.900 | 17/36 | 1/10 | 0/26 | 10/26 | 0.694 | 0.639 |

**e · um `fits` por skill (42 Nouls)** — limiar no maior `fits` do catálogo; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 35/36 | 9/10 | 0/26 | 0/26 | 0.750 | 0.694 |
| 0.200 | 33/36 | 7/10 | 0/26 | 0/26 | 0.806 | 0.750 |
| 0.300 | 30/36 | 4/10 | 0/26 | 0/26 | 0.889 | 0.833 |
| 0.400 | 30/36 | 4/10 | 0/26 | 0/26 | 0.889 | 0.833 |
| 0.500 | 29/36 | 3/10 | 0/26 | 0/26 | 0.917 | 0.861 |
| 0.600 | 28/36 | 3/10 | 0/26 | 1/26 | 0.889 | 0.833 |
| 0.700 | 27/36 | 3/10 | 0/26 | 2/26 | 0.861 | 0.806 |
| 0.800 | 25/36 | 3/10 | 0/26 | 4/26 | 0.806 | 0.750 |
| 0.900 | 17/36 | 0/10 | 0/26 | 9/26 | 0.750 | 0.722 |

**c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`)** — limiar na PORTA da receita (média das 3 portas orientadas); em uso: 0.2

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 29/36 | 3/10 | 0/26 | 0/26 | 0.917 | 0.861 |
| 0.200 | 29/36 | 3/10 | 0/26 | 0/26 | 0.917 | 0.861 |
| 0.300 | 27/36 | 3/10 | 0/26 | 2/26 | 0.861 | 0.806 |
| 0.400 | 24/36 | 2/10 | 0/26 | 4/26 | 0.833 | 0.778 |
| 0.500 | 19/36 | 1/10 | 0/26 | 8/26 | 0.750 | 0.694 |
| 0.600 | 14/36 | 0/10 | 0/26 | 12/26 | 0.667 | 0.639 |
| 0.700 | 11/36 | 0/10 | 0/26 | 15/26 | 0.583 | 0.556 |
| 0.800 | 3/36 | 0/10 | 0/26 | 23/26 | 0.361 | 0.361 |
| 0.900 | 0/36 | 0/10 | 0/26 | 26/26 | 0.278 | 0.278 |

### Custo e latência por formato de requisição (medidos)

| requisição | enviadas | novas (não cache) | tokens por requisição | p50_ms | p95_ms | quem usa |
|---|---|---|---|---|---|---|
| ampla | 36 | 0 | 1966 | 285 | 335 | a, b, c, c2, d |
| fits_vencedor | 27 | 0 | 356 | 251 | 364 | b |
| rerank | 36 | 0 | 904 | 252 | 276 | c, c2, d |
| todos | 36 | 0 | 3276 | 272 | 366 | e |

Tudo o que esta execução usou: 135 requisições (0 novas), 230870 tokens, US$ 0.0097 · modelo: jev-1.13.0. Latência = a da chamada original de cada requisição (o cache a guarda), medida com 8 pedidos em paralelo.

### Caso a caso

Marca: ✓ a melhor · ≈ aceitável · ✓∅ nenhuma (certo) · ✗I skill INDEVIDA · ✗N null indevido · ✗E skill errada · ✗F sem sugestão por falha. `ampla` = vencedor (confiança; p(`none`)); `fits venc.` = Noul pedido sozinho; `shortlist` = as 3 da ampla com o `fits` de cada uma na `rerank`; `rerank` = vencedor (confiança); `porta` = média das 3 portas; `e` = skill de maior `fits` do catálogo (valor); `a2` = Choice com descrição completa (confiança).

| id | fam | gabarito | outras aceitáveis | base | a | ampla | fits venc. | b | shortlist | rerank | porta | c | c2 | d | e |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SS-A001 | duas próximas | simplify | refactor-safe | docs-writer ✗E | simplify ✓ | simplify (0.97; 0.02) | 0.93 | simplify ✓ | simplify 0.94 · code-review 0.42 · security-review 0.02 | simplify (1.00) | 0.71 | simplify ✓ | simplify ✓ | simplify ✓ | simplify ✓ [simplify 0.93] |
| SS-A002 | cita o nome de uma skill | copywriting | — | copywriting ✓ | copywriting ✓ | copywriting (0.90; 0.03) | 0.75 | copywriting ✓ | copywriting 0.77 · code-review 0.08 · ux-review 0.23 | copywriting (0.95) | 0.34 | copywriting ✓ | copywriting ✓ | copywriting ✓ | copywriting ✓ [copywriting 0.77] |
| SS-A003 | duas próximas | incident-postmortem | logs-prod | incident-postmortem ✓ | incident-postmortem ✓ | incident-postmortem (0.99; 0.00) | 0.97 | incident-postmortem ✓ | incident-postmortem 0.97 · code-review 0.02 · security-review 0.02 | incident-postmortem (1.00) | 0.50 | incident-postmortem ✓ | incident-postmortem ✓ | incident-postmortem ✓ | incident-postmortem ✓ [incident-postmortem 0.97] |
| SS-A004 | jargão | dependency-upgrade | — | ∅ ✗N | dependency-upgrade ✓ | dependency-upgrade (1.00; 0.00) | 0.95 | dependency-upgrade ✓ | dependency-upgrade 0.95 · code-review 0.09 · security-review 0.14 | dependency-upgrade (1.00) | 0.69 | dependency-upgrade ✓ | dependency-upgrade ✓ | dependency-upgrade ✓ | dependency-upgrade ✓ [dependency-upgrade 0.95] |
| SS-A005 | trivial que parece pedir skill | ∅ | — | test-writer ✗I | ∅ ✓∅ | ∅ (0.99; 1.00) | — | ∅ ✓∅ | code-review 0.04 · security-review 0.02 · simplify 0.03 | code-review (0.71) | 0.84 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [test-writer 0.28] |
| SS-A006 | vago | ∅ | — | ∅ ✓∅ | perf-profile ✗I | perf-profile (0.82; 0.17) | 0.75 | perf-profile ✗I | perf-profile 0.78 · code-review 0.07 · security-review 0.06 | perf-profile (1.00) | 0.38 | perf-profile ✗I | perf-profile ✗I | perf-profile ✗I | perf-profile ✗I [perf-profile 0.80] |
| SS-A007 | jargão | whatsapp-template | — | whatsapp-template ✓ | whatsapp-template ✓ | whatsapp-template (1.00; 0.00) | 0.96 | whatsapp-template ✓ | whatsapp-template 0.95 · code-review 0.02 · security-review 0.09 | whatsapp-template (1.00) | 0.55 | whatsapp-template ✓ | whatsapp-template ✓ | whatsapp-template ✓ | whatsapp-template ✓ [whatsapp-template 0.96] |
| SS-A008 | duas próximas | ai-seo | — | ∅ ✗N | ai-seo ✓ | ai-seo (0.96; 0.02) | 0.89 | ai-seo ✓ | ai-seo 0.89 · prompt-tuning 0.15 · code-review 0.01 | ai-seo (0.99) | 0.44 | ai-seo ✓ | ai-seo ✓ | ai-seo ✓ | ai-seo ✓ [ai-seo 0.90] |
| SS-A009 | duas próximas | security-review | code-review | code-review ≈ | code-review ≈ | code-review (0.95; 0.00) | 0.96 | code-review ≈ | code-review 0.96 · security-review 0.95 · simplify 0.12 | security-review (0.87) | 0.63 | security-review ✓ | security-review ✓ | code-review ≈ | code-review ≈ [code-review 0.96] |
| SS-A010 | negação | pr-open | — | pr-open ✓ | pr-open ✓ | pr-open (1.00; 0.00) | 0.94 | pr-open ✓ | pr-open 0.95 · code-review 0.07 · security-review 0.04 | pr-open (1.00) | 0.79 | pr-open ✓ | pr-open ✓ | pr-open ✓ | pr-open ✓ [pr-open 0.95] |
| SS-A011 | composto | test-writer | pr-open | test-writer ✓ | test-writer ✓ | test-writer (1.00; 0.00) | 0.69 | test-writer ✓ | test-writer 0.69 · code-review 0.05 · security-review 0.03 | test-writer (1.00) | 0.88 | test-writer ✓ | test-writer ✓ | test-writer ✓ | test-writer ✓ [test-writer 0.69] |
| SS-A012 | duas próximas | api-contract | docs-writer | ∅ ✗N | docs-writer ≈ | docs-writer (0.66; 0.00) | 0.87 | docs-writer ≈ | docs-writer 0.88 · api-contract 0.87 · code-review 0.04 | docs-writer (0.30) | 0.59 | docs-writer ≈ | docs-writer ≈ | docs-writer ≈ | docs-writer ≈ [docs-writer 0.88] |
| SS-A013 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (1.00; 1.00) | — | ∅ ✓∅ | code-review 0.06 · security-review 0.05 · simplify 0.08 | simplify (0.58) | 0.16 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [frontend-design 0.12] |
| SS-A014 | fácil / outros | frontend-design | — | ∅ ✗N | frontend-design ✓ | frontend-design (0.98; 0.02) | 0.91 | frontend-design ✓ | frontend-design 0.91 · code-review 0.02 · security-review 0.02 | frontend-design (1.00) | 0.26 | frontend-design ✓ | frontend-design ✓ | frontend-design ✓ | frontend-design ✓ [frontend-design 0.90] |
| SS-A015 | jargão | deploy-dev | — | ∅ ✗N | ∅ ✗N | ∅ (0.32; 0.35) | — | ∅ ✗N | deploy-dev 0.56 · deploy-prod 0.04 · code-review 0.16 | deploy-dev (1.00) | 0.72 | deploy-dev ✓ | deploy-dev ✓ | deploy-dev ✓ | deploy-dev ✓ [deploy-dev 0.51] |
| SS-A016 | jargão | ads-audit | lead-report | ∅ ✗N | ads-audit ✓ | ads-audit (0.90; 0.09) | 0.86 | ads-audit ✓ | ads-audit 0.85 · code-review 0.01 · security-review 0.02 | ads-audit (1.00) | 0.30 | ads-audit ✓ | ads-audit ✓ | ads-audit ✓ | ads-audit ✓ [ads-audit 0.86] |
| SS-A017 | fácil / outros | diagnosing-bugs | — | diagnosing-bugs ✓ | diagnosing-bugs ✓ | diagnosing-bugs (0.98; 0.00) | 0.86 | diagnosing-bugs ✓ | diagnosing-bugs 0.84 · logs-prod 0.54 · code-review 0.07 | diagnosing-bugs (0.94) | 0.44 | diagnosing-bugs ✓ | diagnosing-bugs ✓ | diagnosing-bugs ✓ | diagnosing-bugs ✓ [diagnosing-bugs 0.85] |
| SS-A018 | composto | prompt-tuning | llm-eval | prompt-tuning ✓ | prompt-tuning ✓ | prompt-tuning (0.99; 0.00) | 0.79 | prompt-tuning ✓ | prompt-tuning 0.81 · code-review 0.08 · security-review 0.02 | prompt-tuning (1.00) | 0.53 | prompt-tuning ✓ | prompt-tuning ✓ | prompt-tuning ✓ | prompt-tuning ✓ [prompt-tuning 0.80] |
| SS-A019 | duas próximas | grilling | — | ∅ ✗N | grilling ✓ | grilling (0.98; 0.01) | 0.81 | grilling ✓ | grilling 0.78 · code-review 0.03 · security-review 0.04 | grilling (1.00) | 0.24 | grilling ✓ | grilling ✓ | grilling ✓ | grilling ✓ [grilling 0.80] |
| SS-A020 | vago | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.99; 1.00) | — | ∅ ✓∅ | code-review 0.32 · security-review 0.18 · simplify 0.08 | code-review (0.91) | 0.46 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [ux-review 0.45] |
| SS-A021 | duas próximas | ux-review | — | ux-review ✓ | ux-review ✓ | ux-review (0.99; 0.00) | 0.96 | ux-review ✓ | ux-review 0.96 · code-review 0.12 · security-review 0.02 | ux-review (1.00) | 0.42 | ux-review ✓ | ux-review ✓ | ux-review ✓ | ux-review ✓ [ux-review 0.96] |
| SS-A022 | fácil / outros | migration-2bancos | — | migration-2bancos ✓ | migration-2bancos ✓ | migration-2bancos (0.89; 0.06) | 0.74 | migration-2bancos ✓ | migration-2bancos 0.71 · db-query 0.04 · code-review 0.05 | migration-2bancos (1.00) | 0.71 | migration-2bancos ✓ | migration-2bancos ✓ | migration-2bancos ✓ | migration-2bancos ✓ [migration-2bancos 0.72] |
| SS-A023 | fácil / outros | rollback | — | rollback ✓ | rollback ✓ | rollback (1.00; 0.00) | 0.98 | rollback ✓ | rollback 0.97 · code-review 0.05 · security-review 0.03 | rollback (1.00) | 0.84 | rollback ✓ | rollback ✓ | rollback ✓ | rollback ✓ [rollback 0.98] |
| SS-A024 | fácil / outros | email-sequence | — | email-sequence ✓ | email-sequence ✓ | email-sequence (1.00; 0.00) | 0.96 | email-sequence ✓ | email-sequence 0.96 · code-review 0.03 · security-review 0.02 | email-sequence (1.00) | 0.62 | email-sequence ✓ | email-sequence ✓ | email-sequence ✓ | email-sequence ✓ [email-sequence 0.96] |
| SS-A025 | duas próximas | db-query | lead-report | lead-report ≈ | lead-report ≈ | lead-report (0.99; 0.00) | 0.92 | lead-report ≈ | lead-report 0.92 · code-review 0.01 · security-review 0.01 | lead-report (1.00) | 0.73 | lead-report ≈ | lead-report ≈ | lead-report ≈ | db-query ✓ [db-query 0.92] |
| SS-A026 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.93; 0.93) | — | ∅ ✓∅ | dataviz 0.13 · lead-report 0.01 · code-review 0.01 | dataviz (0.91) | 0.39 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [dataviz 0.12] |
| SS-A027 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.99; 0.99) | — | ∅ ✓∅ | diagnosing-bugs 0.29 · code-review 0.08 · security-review 0.02 | diagnosing-bugs (1.00) | 0.06 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [diagnosing-bugs 0.28] |
| SS-A028 | fácil / outros | secrets-vault | — | secrets-vault ✓ | secrets-vault ✓ | secrets-vault (0.99; 0.00) | 0.93 | secrets-vault ✓ | secrets-vault 0.94 · code-review 0.02 · security-review 0.19 | secrets-vault (1.00) | 0.86 | secrets-vault ✓ | secrets-vault ✓ | secrets-vault ✓ | secrets-vault ✓ [secrets-vault 0.93] |
| SS-A029 | fácil / outros | programmatic-seo | — | programmatic-seo ✓ | programmatic-seo ✓ | programmatic-seo (0.99; 0.00) | 0.97 | programmatic-seo ✓ | programmatic-seo 0.97 · db-query 0.10 · code-review 0.03 | programmatic-seo (0.96) | 0.75 | programmatic-seo ✓ | programmatic-seo ✓ | programmatic-seo ✓ | programmatic-seo ✓ [programmatic-seo 0.97] |
| SS-A030 | fácil / outros | fix-ci | — | fix-ci ✓ | fix-ci ✓ | fix-ci (0.99; 0.01) | 0.96 | fix-ci ✓ | fix-ci 0.96 · code-review 0.41 · security-review 0.05 | fix-ci (1.00) | 0.76 | fix-ci ✓ | fix-ci ✓ | fix-ci ✓ | fix-ci ✓ [fix-ci 0.96] |
| SS-A031 | cita o nome de uma skill | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.77; 0.78) | — | ∅ ✓∅ | copywriting 0.09 · email-sequence 0.06 · code-review 0.01 | copywriting (0.48) | 0.07 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [copywriting 0.09] |
| SS-A032 | trivial que parece pedir skill | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.59; 0.61) | — | ∅ ✓∅ | refactor-safe 0.90 · code-review 0.14 · security-review 0.01 | refactor-safe (1.00) | 0.53 | refactor-safe ✗I | refactor-safe ✗I | refactor-safe ✗I | refactor-safe ✗I [refactor-safe 0.89] |
| SS-A033 | cita o nome de uma skill | ∅ | — | migration-2bancos ✗I | migration-2bancos ✗I | migration-2bancos (0.31; 0.23) | 0.07 | ∅ ✓∅ | migration-2bancos 0.06 · programmatic-seo 0.06 · db-query 0.08 | migration-2bancos (0.62) | 0.86 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [frontend-design 0.29] |
| SS-A034 | fácil / outros | changelog-release | — | changelog-release ✓ | changelog-release ✓ | changelog-release (1.00; 0.00) | 0.97 | changelog-release ✓ | changelog-release 0.97 · code-review 0.03 · security-review 0.02 | changelog-release (1.00) | 0.78 | changelog-release ✓ | changelog-release ✓ | changelog-release ✓ | changelog-release ✓ [changelog-release 0.97] |
| SS-A035 | trivial que parece pedir skill | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.90; 0.90) | — | ∅ ✓∅ | docs-writer 0.89 · code-review 0.33 · security-review 0.01 | docs-writer (1.00) | 0.48 | docs-writer ✗I | docs-writer ✗I | docs-writer ✗I | docs-writer ✗I [docs-writer 0.88] |
| SS-A036 | duas próximas | perf-profile | diagnosing-bugs | perf-profile ✓ | perf-profile ✓ | perf-profile (1.00; 0.00) | 0.96 | perf-profile ✓ | perf-profile 0.96 · code-review 0.15 · security-review 0.02 | perf-profile (1.00) | 0.58 | perf-profile ✓ | perf-profile ✓ | perf-profile ✓ | perf-profile ✓ [perf-profile 0.96] |

## Conjunto `teste` — 87 pedidos (arquivo versão 2026-10-01, autor fable); 43 difíceis, 24 com gabarito `null`, 0 sem sugestão por falha operacional ou teto; catálogo de 42 skills

### Escolha — baseline de código × variantes com Jev, nos mesmos pedidos

`estrito` = a skill exata do gabarito (ou nenhuma quando o gabarito é `null`). `folgado` = escolha ∈ `aceitaveis` (ou nenhuma quando `aceitaveis` é vazio). **Skill INDEVIDA** = erro caro: carregou skill com gabarito `null` (denominador = pedidos `null`). **Null indevido** = não carregou quando havia skill; **skill errada** = carregou outra, fora de `aceitaveis` (denominador dos dois = pedidos com skill). Custo e latência: só as requisições que a variante envia em produção, medidas. Variante principal (a que o critério julga): **b · Choice + `fits` do vencedor**.

| variante | n | acerto estrito | acerto folgado | skill INDEVIDA | null indevido | skill errada | aceitável (não a melhor) | sem sugestão (falha) | req/pedido | tokens/pedido | US$/1000 | p50_ms | p95_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| código: BM25 + limiar | 87 | 0.678 | 0.759 | 5/24 | 8/63 | 8/63 | 7/63 | 0/87 | 0 | 0 | 0 | 0 | 0 |
| a · Choice única | 87 | 0.885 | 0.920 | 3/24 | 2/63 | 2/63 | 3/63 | 0/87 | 1.00 | 1965 | 0.0825 | 287 | 438 |
| b · Choice + `fits` do vencedor | 87 | 0.908 | 0.931 | 0/24 | 5/63 | 1/63 | 2/63 | 0/87 | 1.74 | 2225 | 0.0935 | 534 | 714 |
| c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`) | 87 | 0.885 | 0.897 | 3/24 | 4/63 | 2/63 | 1/63 | 0/87 | 2.00 | 2854 | 0.1199 | 555 | 727 |
| c2 · receita + portão no vencedor consumido | 87 | 0.862 | 0.874 | 3/24 | 7/63 | 1/63 | 1/63 | 0/87 | 2.00 | 2854 | 0.1199 | 555 | 727 |
| d · receita corrigida (vencedor = maior `fits`) | 87 | 0.851 | 0.897 | 3/24 | 4/63 | 2/63 | 4/63 | 0/87 | 2.00 | 2854 | 0.1199 | 555 | 727 |
| e · um `fits` por skill (42 Nouls) | 87 | 0.828 | 0.897 | 6/24 | 1/63 | 2/63 | 6/63 | 0/87 | 1.00 | 3276 | 0.1376 | 275 | 364 |
| a2 · Choice única com a descrição completa — informativa | 87 | 0.954 | 0.977 | 1/24 | 1/63 | 0/63 | 2/63 | 0/87 | 1.00 | 2573 | 0.1081 | 263 | 350 |
| c com os limiares publicados (porta 0,30; `fits` 0,30) — informativa | 87 | 0.770 | 0.782 | 6/24 | 11/63 | 2/63 | 1/63 | 0/87 | 2.00 | 2854 | 0.1199 | 555 | 727 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 skill indevida (gabarito `null`, carregou skill) | 0/24 (0.000) | ≤ 0.083 | ✓ |
| 2 acerto folgado | 0.931 (baseline de código 0.759) | ≥ 0.959 | ✗ |
| 3 contra a Choice única (a) | folgado 0.931 × 0.920; indevidas 0 × 3 | folgado ≥ e indevidas ≤ | ✓ |
| 4 null indevido (havia skill, não carregou) | 5/63 (0.079) | ≤ 0.100 | ✓ |
| 5 skill errada (carregou outra, fora de `aceitaveis`) | 1/63 (0.016) | ≤ 0.050 | ✓ |

### A ressalva da receita oficial — o portão olha um candidato, o vencedor é outro?

Porta aberta (≥ 0.2) em 79/87 pedidos. Neles, o vencedor da Choice `rerank` e o candidato de maior `fits` são skills DIFERENTES em **12**; nesses, acerto folgado de `c` (fica com a Choice) 10/12 × `d` (fica com o maior `fits`) 10/12. O furo que a ressalva descreve — o maior `fits` passa o portão (≥ 0.5) mas o `fits` do vencedor consumido está abaixo — aconteceu em **3** pedidos; neles, acerto folgado: `c` 2, `c2` (devolve nenhuma) 0, `d` 2 de 3. Decisão final diferente: `c` × `c2` em 3 pedidos, `c` × `d` em 8.

| id | gabarito | aceitáveis | vencedor rerank (fits) | maior fits | c | c2 | d | furo |
|---|---|---|---|---|---|---|---|---|
| SS-T008 | dataviz | dataviz lead-report | lead-report (0.69) | dataviz (0.95) | lead-report ≈ | lead-report ≈ | dataviz ✓ |  |
| SS-T017 | frontend-design | frontend-design copywriting | frontend-design (0.71) | copywriting (0.92) | frontend-design ✓ | frontend-design ✓ | copywriting ≈ |  |
| SS-T026 | lead-report | lead-report ads-audit db-query | lead-report (0.59) | ads-audit (0.84) | lead-report ✓ | lead-report ✓ | ads-audit ≈ |  |
| SS-T032 | ∅ | — | social-calendar (0.26) | e2e-browser (0.31) | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ |  |
| SS-T039 | ∅ | — | code-review (0.04) | simplify (0.06) | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ |  |
| SS-T042 | code-review | code-review deploy-prod | code-review (0.54) | deploy-prod (0.76) | code-review ✓ | code-review ✓ | deploy-prod ≈ |  |
| SS-T046 | ∅ | — | deploy-dev (0.82) | deploy-prod (0.83) | deploy-dev ✗I | deploy-dev ✗I | deploy-prod ✗I |  |
| SS-T058 | ∅ | — | changelog-release (0.16) | db-query (0.31) | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ |  |
| SS-T070 | deploy-dev | deploy-dev | deploy-dev (0.25) | dependency-upgrade (0.52) | deploy-dev ✓ | ∅ ✗N | dependency-upgrade ✗E | sim |
| SS-T071 | ∅ | — | code-review (0.04) | dependency-upgrade (0.04) | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ |  |
| SS-T077 | logs-prod | logs-prod diagnosing-bugs | ads-audit (0.36) | logs-prod (0.56) | ads-audit ✗E | ∅ ✗N | logs-prod ✓ | sim |
| SS-T079 | migration-2bancos | migration-2bancos api-contract | migration-2bancos (0.03) | api-contract (0.57) | migration-2bancos ✓ | ∅ ✗N | api-contract ≈ | sim |

### Por família difícil (pela `nota` do rotulador) — acertos folgados; erros caros da principal

| família | n | `null` | base | a | b | c | c2 | d | e | a2 | indevida (principal) | null indevido (principal) | errada (principal) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cita o nome de uma skill | 7 | 3 | 7 | 4 | 6 | 5 | 5 | 6 | 6 | 6 | 0 | 1 | 0 |
| jargão | 9 | 0 | 6 | 8 | 7 | 8 | 8 | 8 | 9 | 9 | 0 | 1 | 1 |
| trivial que parece pedir skill | 5 | 5 | 4 | 5 | 5 | 4 | 4 | 4 | 3 | 5 | 0 | 0 | 0 |
| duas próximas | 10 | 0 | 6 | 10 | 10 | 10 | 10 | 10 | 9 | 10 | 0 | 0 | 0 |
| composto | 5 | 0 | 5 | 5 | 4 | 4 | 3 | 4 | 5 | 5 | 0 | 1 | 0 |
| fora do catálogo que parece dentro | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| vago | 5 | 2 | 2 | 3 | 3 | 4 | 3 | 3 | 2 | 4 | 0 | 2 | 0 |
| negação | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| fácil / outros | 44 | 12 | 35 | 44 | 44 | 41 | 41 | 41 | 42 | 44 | 0 | 0 | 0 |

### Os sinais — o `fits` separa "serve" de "não serve"? E as portas da receita?

`fits` (requisição `todos`) da skill do gabarito, nos 63 pedidos com skill: mínimo 0.03, p10 0.63, mediana 0.93. Maior `fits` do catálogo nos 24 pedidos `null` (aqui alto = skill indevida em `e`): mediana 0.23, p90 0.58, máximo 0.83. A skill do gabarito é a de maior `fits` do catálogo em 55/63; está na shortlist da ampla em 62/63 (alguma aceitável: 62/63) — o que a 2ª requisição não recebe, ela não recupera.

Quem aponta a skill certa nos 63 pedidos com skill, sem portão (a 1ª skill do ranking, mesmo quando a Choice preferiu `none`):

| quem aponta | a melhor | alguma aceitável |
|---|---|---|
| ampla, descrição curta (1ª skill do ranking) | 57/63 | 60/63 |
| Choice `rerank`, texto completo, entre as 3 | 60/63 | 61/63 |
| maior `fits` entre as 3 da shortlist | 56/63 | 61/63 |
| maior `fits` entre as 42 | 55/63 | 61/63 |
| ampla, descrição completa (1ª skill do ranking) | 60/63 | 62/63 |

A releitura com o texto completo (`rerank`) trocou a 1ª skill da ampla em 4/63 pedidos com skill: passou a apontar a melhor em 3, deixou de apontá-la em 0 (SS-T012: code-review → db-query; SS-T070: deploy-prod → deploy-dev; SS-T079: api-contract → migration-2bancos; SS-T080: db-query → perf-profile).

Porta da receita (média das 3 orientadas; < 0.2 = nenhuma): fechou em 5/24 pedidos `null` e em 3/63 pedidos com skill. Valores nos `null`: mínimo 0.05, mediana 0.47, máximo 0.86; nos com skill: mínimo 0.10, mediana 0.59. A Choice ampla disse `none` em 21/24 pedidos `null` e em 2/63 com skill.

O mesmo Noul em requisições diferentes (isolamento ≠ determinismo): o `fits` do vencedor da ampla foi pedido sozinho (`fits_vencedor`), junto de 2 candidatas (`rerank`) e junto das 42 (`todos`). Diferença absoluta sozinho × `rerank`: média 0.011, máxima 0.070 (n = 64); sozinho × `todos`: média 0.009, máxima 0.040 (n = 64).

### Cobertura × erro por limiar (o portão de cada variante em cada ponto da grade)

**b · Choice + `fits` do vencedor** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 64/87 | 3/24 | 2/63 | 2/63 | 0.920 | 0.885 |
| 0.200 | 63/87 | 2/24 | 2/63 | 2/63 | 0.931 | 0.897 |
| 0.300 | 60/87 | 0/24 | 2/63 | 3/63 | 0.943 | 0.908 |
| 0.400 | 58/87 | 0/24 | 1/63 | 5/63 | 0.931 | 0.908 |
| 0.500 | 58/87 | 0/24 | 1/63 | 5/63 | 0.931 | 0.908 |
| 0.600 | 57/87 | 0/24 | 1/63 | 6/63 | 0.920 | 0.897 |
| 0.700 | 49/87 | 0/24 | 0/63 | 14/63 | 0.839 | 0.839 |
| 0.800 | 47/87 | 0/24 | 0/63 | 16/63 | 0.816 | 0.816 |
| 0.900 | 40/87 | 0/24 | 0/63 | 23/63 | 0.736 | 0.736 |

**código: BM25 + limiar** — limiar na pontuação BM25; em uso: 4.0

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.000 | 83/87 | 20/24 | 13/63 | 0/63 | 0.621 | 0.540 |
| 2.000 | 83/87 | 20/24 | 13/63 | 0/63 | 0.621 | 0.540 |
| 3.000 | 79/87 | 16/24 | 13/63 | 0/63 | 0.667 | 0.586 |
| 4.000 | 60/87 | 5/24 | 8/63 | 8/63 | 0.759 | 0.678 |
| 5.000 | 51/87 | 3/24 | 4/63 | 15/63 | 0.747 | 0.667 |
| 6.000 | 46/87 | 2/24 | 3/63 | 19/63 | 0.724 | 0.644 |
| 8.000 | 28/87 | 0/24 | 0/63 | 35/63 | 0.598 | 0.563 |

**a · Choice única** — piso na confiança da Choice (a variante medida não tem piso)

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 64/87 | 3/24 | 2/63 | 2/63 | 0.920 | 0.885 |
| 0.200 | 64/87 | 3/24 | 2/63 | 2/63 | 0.920 | 0.885 |
| 0.300 | 64/87 | 3/24 | 2/63 | 2/63 | 0.920 | 0.885 |
| 0.400 | 64/87 | 3/24 | 2/63 | 2/63 | 0.920 | 0.885 |
| 0.500 | 60/87 | 1/24 | 1/63 | 4/63 | 0.931 | 0.897 |
| 0.600 | 58/87 | 1/24 | 0/63 | 6/63 | 0.920 | 0.885 |
| 0.700 | 54/87 | 0/24 | 0/63 | 9/63 | 0.897 | 0.862 |
| 0.800 | 52/87 | 0/24 | 0/63 | 11/63 | 0.874 | 0.851 |
| 0.900 | 44/87 | 0/24 | 0/63 | 19/63 | 0.782 | 0.770 |

**c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`)** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 72/87 | 12/24 | 2/63 | 3/63 | 0.805 | 0.793 |
| 0.200 | 69/87 | 9/24 | 2/63 | 3/63 | 0.839 | 0.828 |
| 0.300 | 65/87 | 6/24 | 2/63 | 4/63 | 0.862 | 0.851 |
| 0.400 | 62/87 | 3/24 | 2/63 | 4/63 | 0.897 | 0.885 |
| 0.500 | 62/87 | 3/24 | 2/63 | 4/63 | 0.897 | 0.885 |
| 0.600 | 57/87 | 1/24 | 1/63 | 7/63 | 0.897 | 0.885 |
| 0.700 | 53/87 | 1/24 | 1/63 | 11/63 | 0.851 | 0.839 |
| 0.800 | 50/87 | 1/24 | 0/63 | 14/63 | 0.828 | 0.816 |
| 0.900 | 40/87 | 0/24 | 0/63 | 23/63 | 0.736 | 0.724 |

**c2 · receita + portão no vencedor consumido** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 71/87 | 12/24 | 2/63 | 4/63 | 0.793 | 0.782 |
| 0.200 | 67/87 | 8/24 | 2/63 | 4/63 | 0.839 | 0.828 |
| 0.300 | 61/87 | 4/24 | 2/63 | 6/63 | 0.862 | 0.851 |
| 0.400 | 59/87 | 3/24 | 1/63 | 7/63 | 0.874 | 0.862 |
| 0.500 | 59/87 | 3/24 | 1/63 | 7/63 | 0.874 | 0.862 |
| 0.600 | 55/87 | 1/24 | 1/63 | 9/63 | 0.874 | 0.862 |
| 0.700 | 50/87 | 1/24 | 1/63 | 14/63 | 0.816 | 0.816 |
| 0.800 | 47/87 | 1/24 | 0/63 | 17/63 | 0.793 | 0.793 |
| 0.900 | 38/87 | 0/24 | 0/63 | 25/63 | 0.713 | 0.713 |

**d · receita corrigida (vencedor = maior `fits`)** — limiar no `fits`; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 72/87 | 12/24 | 2/63 | 3/63 | 0.805 | 0.759 |
| 0.200 | 69/87 | 9/24 | 2/63 | 3/63 | 0.839 | 0.793 |
| 0.300 | 65/87 | 6/24 | 2/63 | 4/63 | 0.862 | 0.816 |
| 0.400 | 62/87 | 3/24 | 2/63 | 4/63 | 0.897 | 0.851 |
| 0.500 | 62/87 | 3/24 | 2/63 | 4/63 | 0.897 | 0.851 |
| 0.600 | 57/87 | 1/24 | 1/63 | 7/63 | 0.897 | 0.862 |
| 0.700 | 53/87 | 1/24 | 1/63 | 11/63 | 0.851 | 0.816 |
| 0.800 | 50/87 | 1/24 | 0/63 | 14/63 | 0.828 | 0.805 |
| 0.900 | 40/87 | 0/24 | 0/63 | 23/63 | 0.736 | 0.724 |

**e · um `fits` por skill (42 Nouls)** — limiar no maior `fits` do catálogo; em uso: 0.5

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 81/87 | 18/24 | 2/63 | 0/63 | 0.770 | 0.701 |
| 0.200 | 77/87 | 14/24 | 2/63 | 0/63 | 0.816 | 0.747 |
| 0.300 | 70/87 | 8/24 | 2/63 | 1/63 | 0.874 | 0.805 |
| 0.400 | 68/87 | 6/24 | 2/63 | 1/63 | 0.897 | 0.828 |
| 0.500 | 68/87 | 6/24 | 2/63 | 1/63 | 0.897 | 0.828 |
| 0.600 | 60/87 | 2/24 | 1/63 | 5/63 | 0.908 | 0.874 |
| 0.700 | 57/87 | 2/24 | 1/63 | 8/63 | 0.874 | 0.839 |
| 0.800 | 53/87 | 1/24 | 0/63 | 11/63 | 0.862 | 0.839 |
| 0.900 | 43/87 | 0/24 | 0/63 | 20/63 | 0.770 | 0.759 |

**a2 · Choice única com a descrição completa — informativa** — piso na confiança da Choice (idem)

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 63/87 | 1/24 | 0/63 | 1/63 | 0.977 | 0.954 |
| 0.200 | 63/87 | 1/24 | 0/63 | 1/63 | 0.977 | 0.954 |
| 0.300 | 63/87 | 1/24 | 0/63 | 1/63 | 0.977 | 0.954 |
| 0.400 | 63/87 | 1/24 | 0/63 | 1/63 | 0.977 | 0.954 |
| 0.500 | 60/87 | 1/24 | 0/63 | 4/63 | 0.943 | 0.931 |
| 0.600 | 60/87 | 1/24 | 0/63 | 4/63 | 0.943 | 0.931 |
| 0.700 | 58/87 | 0/24 | 0/63 | 5/63 | 0.943 | 0.931 |
| 0.800 | 53/87 | 0/24 | 0/63 | 10/63 | 0.885 | 0.885 |
| 0.900 | 49/87 | 0/24 | 0/63 | 14/63 | 0.839 | 0.839 |

**c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`)** — limiar na PORTA da receita (média das 3 portas orientadas); em uso: 0.2

| limiar | sugeriu skill | skill indevida | skill errada | null indevido | folgado | estrito |
|---|---|---|---|---|---|---|
| 0.100 | 64/87 | 3/24 | 2/63 | 2/63 | 0.920 | 0.908 |
| 0.200 | 62/87 | 3/24 | 2/63 | 4/63 | 0.897 | 0.885 |
| 0.300 | 55/87 | 3/24 | 2/63 | 11/63 | 0.816 | 0.805 |
| 0.400 | 51/87 | 3/24 | 2/63 | 15/63 | 0.770 | 0.759 |
| 0.500 | 44/87 | 2/24 | 2/63 | 21/63 | 0.713 | 0.701 |
| 0.600 | 30/87 | 0/24 | 1/63 | 33/63 | 0.609 | 0.598 |
| 0.700 | 18/87 | 0/24 | 1/63 | 45/63 | 0.471 | 0.471 |
| 0.800 | 6/87 | 0/24 | 0/63 | 57/63 | 0.345 | 0.345 |
| 0.900 | 0/87 | 0/24 | 0/63 | 63/63 | 0.276 | 0.276 |

### Custo e latência por formato de requisição (medidos)

| requisição | enviadas | novas (não cache) | tokens por requisição | p50_ms | p95_ms | quem usa |
|---|---|---|---|---|---|---|
| ampla | 87 | 87 | 1965 | 287 | 438 | a, b, c, c2, d |
| fits_vencedor | 64 | 64 | 354 | 258 | 331 | b |
| rerank | 87 | 87 | 889 | 259 | 327 | c, c2, d |
| todos | 87 | 87 | 3276 | 275 | 364 | e |
| ampla_completa | 87 | 87 | 2573 | 263 | 350 | a2 |

Tudo o que esta execução usou: 412 requisições (412 novas), 779803 tokens, US$ 0.0328 · modelo: jev-1.13.0. Latência = a da chamada original de cada requisição (o cache a guarda), medida com 8 pedidos em paralelo.

### Caso a caso

Marca: ✓ a melhor · ≈ aceitável · ✓∅ nenhuma (certo) · ✗I skill INDEVIDA · ✗N null indevido · ✗E skill errada · ✗F sem sugestão por falha. `ampla` = vencedor (confiança; p(`none`)); `fits venc.` = Noul pedido sozinho; `shortlist` = as 3 da ampla com o `fits` de cada uma na `rerank`; `rerank` = vencedor (confiança); `porta` = média das 3 portas; `e` = skill de maior `fits` do catálogo (valor); `a2` = Choice com descrição completa (confiança).

| id | fam | gabarito | outras aceitáveis | base | a | ampla | fits venc. | b | shortlist | rerank | porta | c | c2 | d | e | a2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SS-T001 | fácil / outros | dependency-upgrade | — | dependency-upgrade ✓ | dependency-upgrade ✓ | dependency-upgrade (1.00; 0.00) | 0.95 | dependency-upgrade ✓ | dependency-upgrade 0.95 · code-review 0.16 · security-review 0.04 | dependency-upgrade (1.00) | 0.76 | dependency-upgrade ✓ | dependency-upgrade ✓ | dependency-upgrade ✓ | dependency-upgrade ✓ [dependency-upgrade 0.95] | dependency-upgrade ✓ (1.00) |
| SS-T002 | fácil / outros | diagnosing-bugs | — | ∅ ✗N | diagnosing-bugs ✓ | diagnosing-bugs (0.96; 0.00) | 0.92 | diagnosing-bugs ✓ | diagnosing-bugs 0.92 · logs-prod 0.58 · code-review 0.08 | diagnosing-bugs (0.72) | 0.54 | diagnosing-bugs ✓ | diagnosing-bugs ✓ | diagnosing-bugs ✓ | diagnosing-bugs ✓ [diagnosing-bugs 0.93] | diagnosing-bugs ✓ (0.96) |
| SS-T003 | cita o nome de uma skill | email-sequence | landing-ab-test | email-sequence ✓ | email-sequence ✓ | email-sequence (0.84; 0.01) | 0.65 | email-sequence ✓ | email-sequence 0.62 · landing-ab-test 0.08 · copywriting 0.22 | email-sequence (0.89) | 0.44 | email-sequence ✓ | email-sequence ✓ | email-sequence ✓ | email-sequence ✓ [email-sequence 0.68] | email-sequence ✓ (0.86) |
| SS-T004 | fácil / outros | prompt-tuning | — | prompt-tuning ✓ | prompt-tuning ✓ | prompt-tuning (0.99; 0.01) | 0.95 | prompt-tuning ✓ | prompt-tuning 0.95 · code-review 0.03 · security-review 0.03 | prompt-tuning (1.00) | 0.36 | prompt-tuning ✓ | prompt-tuning ✓ | prompt-tuning ✓ | prompt-tuning ✓ [prompt-tuning 0.95] | prompt-tuning ✓ (1.00) |
| SS-T005 | jargão | docs-writer | — | ∅ ✗N | docs-writer ✓ | docs-writer (0.99; 0.00) | 0.96 | docs-writer ✓ | docs-writer 0.96 · code-review 0.10 · security-review 0.03 | docs-writer (1.00) | 0.53 | docs-writer ✓ | docs-writer ✓ | docs-writer ✓ | docs-writer ✓ [docs-writer 0.96] | docs-writer ✓ (0.99) |
| SS-T006 | trivial que parece pedir skill | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.99; 1.00) | — | ∅ ✓∅ | code-review 0.05 · security-review 0.01 · simplify 0.03 | code-review (0.34) | 0.66 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | frontend-design ✗I [frontend-design 0.75] | ∅ ✓∅ (0.99) |
| SS-T007 | fácil / outros | logs-prod | — | logs-prod ✓ | logs-prod ✓ | logs-prod (0.95; 0.03) | 0.94 | logs-prod ✓ | logs-prod 0.94 · incident-postmortem 0.51 · code-review 0.01 | logs-prod (1.00) | 0.65 | logs-prod ✓ | logs-prod ✓ | logs-prod ✓ | logs-prod ✓ [logs-prod 0.95] | logs-prod ✓ (0.99) |
| SS-T008 | duas próximas | dataviz | lead-report | dataviz ✓ | lead-report ≈ | lead-report (0.76; 0.00) | 0.66 | lead-report ≈ | lead-report 0.69 · dataviz 0.95 · db-query 0.42 | lead-report (0.27) | 0.63 | lead-report ≈ | lead-report ≈ | dataviz ✓ | dataviz ✓ [dataviz 0.95] | dataviz ✓ (0.48) |
| SS-T009 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.98; 0.98) | — | ∅ ✓∅ | to-tickets 0.05 · social-calendar 0.01 · code-review 0.01 | to-tickets (0.52) | 0.41 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [to-tickets 0.05] | ∅ ✓∅ (0.99) |
| SS-T010 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.92; 0.93) | — | ∅ ✓∅ | code-review 0.09 · security-review 0.03 · simplify 0.02 | code-review (0.95) | 0.85 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [code-review 0.08] | ∅ ✓∅ (0.93) |
| SS-T011 | composto | code-review | simplify | simplify ≈ | code-review ✓ | code-review (0.99; 0.00) | 0.97 | code-review ✓ | code-review 0.97 · security-review 0.05 · simplify 0.43 | code-review (1.00) | 0.53 | code-review ✓ | code-review ✓ | code-review ✓ | code-review ✓ [code-review 0.97] | code-review ✓ (1.00) |
| SS-T012 | jargão | api-contract | — | api-contract ✓ | code-review ✗E | code-review (0.58; 0.07) | 0.66 | code-review ✗E | code-review 0.61 · db-query 0.74 · diagnosing-bugs 0.30 | db-query (0.65) | 0.75 | db-query ✗E | db-query ✗E | db-query ✗E | api-contract ✓ [api-contract 0.93] | api-contract ✓ (0.94) |
| SS-T013 | duas próximas | simplify | code-review | docs-writer ✗E | simplify ✓ | simplify (0.98; 0.01) | 0.93 | simplify ✓ | simplify 0.93 · code-review 0.77 · security-review 0.02 | simplify (1.00) | 0.49 | simplify ✓ | simplify ✓ | simplify ✓ | simplify ✓ [simplify 0.93] | simplify ✓ (0.97) |
| SS-T014 | cita o nome de uma skill | ∅ | — | ∅ ✓∅ | simplify ✗I | simplify (0.48; 0.39) | 0.15 | ∅ ✓∅ | simplify 0.13 · copywriting 0.40 · docs-writer 0.22 | simplify (0.60) | 0.11 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [copywriting 0.38] | ∅ ✓∅ (0.62) |
| SS-T015 | fácil / outros | copywriting | — | copywriting ✓ | copywriting ✓ | copywriting (1.00; 0.00) | 0.97 | copywriting ✓ | copywriting 0.98 · code-review 0.02 · security-review 0.02 | copywriting (1.00) | 0.38 | copywriting ✓ | copywriting ✓ | copywriting ✓ | copywriting ✓ [copywriting 0.97] | copywriting ✓ (1.00) |
| SS-T016 | jargão | logs-prod | diagnosing-bugs | api-contract ✗E | logs-prod ✓ | logs-prod (0.95; 0.01) | 0.70 | logs-prod ✓ | logs-prod 0.73 · diagnosing-bugs 0.37 · code-review 0.04 | logs-prod (1.00) | 0.62 | logs-prod ✓ | logs-prod ✓ | logs-prod ✓ | logs-prod ✓ [logs-prod 0.72] | logs-prod ✓ (0.97) |
| SS-T017 | composto | frontend-design | copywriting | copywriting ≈ | frontend-design ✓ | frontend-design (0.88; 0.02) | 0.71 | frontend-design ✓ | frontend-design 0.71 · copywriting 0.92 · grilling 0.05 | frontend-design (0.59) | 0.22 | frontend-design ✓ | frontend-design ✓ | copywriting ≈ | copywriting ≈ [copywriting 0.91] | frontend-design ✓ (0.75) |
| SS-T018 | duas próximas | refactor-safe | — | refactor-safe ✓ | refactor-safe ✓ | refactor-safe (1.00; 0.00) | 0.95 | refactor-safe ✓ | refactor-safe 0.95 · code-review 0.14 · security-review 0.03 | refactor-safe (1.00) | 0.63 | refactor-safe ✓ | refactor-safe ✓ | refactor-safe ✓ | refactor-safe ✓ [refactor-safe 0.96] | refactor-safe ✓ (1.00) |
| SS-T019 | fora do catálogo que parece dentro | ∅ | — | ∅ ✓∅ | frontend-design ✗I | frontend-design (0.46; 0.45) | 0.21 | ∅ ✓∅ | frontend-design 0.23 · grilling 0.03 · ad-creative 0.03 | frontend-design (0.62) | 0.35 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [frontend-design 0.23] | ∅ ✓∅ (0.47) |
| SS-T020 | fácil / outros | pr-open | — | pr-open ✓ | pr-open ✓ | pr-open (0.99; 0.01) | 0.80 | pr-open ✓ | pr-open 0.82 · code-review 0.05 · security-review 0.03 | pr-open (1.00) | 0.86 | pr-open ✓ | pr-open ✓ | pr-open ✓ | pr-open ✓ [pr-open 0.82] | pr-open ✓ (0.99) |
| SS-T021 | fácil / outros | ∅ | — | ai-seo ✗I | ∅ ✓∅ | ∅ (0.85; 0.86) | — | ∅ ✓∅ | whatsapp-template 0.32 · copywriting 0.18 · code-review 0.01 | whatsapp-template (0.58) | 0.38 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [whatsapp-template 0.28] | ∅ ✓∅ (0.86) |
| SS-T022 | trivial que parece pedir skill | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (1.00; 1.00) | — | ∅ ✓∅ | code-review 0.02 · security-review 0.02 · simplify 0.03 | simplify (0.76) | 0.12 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [docs-writer 0.29] | ∅ ✓∅ (1.00) |
| SS-T023 | fácil / outros | to-tickets | — | to-tickets ✓ | to-tickets ✓ | to-tickets (0.99; 0.01) | 0.96 | to-tickets ✓ | to-tickets 0.96 · code-review 0.03 · security-review 0.03 | to-tickets (1.00) | 0.47 | to-tickets ✓ | to-tickets ✓ | to-tickets ✓ | to-tickets ✓ [to-tickets 0.96] | to-tickets ✓ (0.99) |
| SS-T024 | vago | e2e-browser | test-writer | ∅ ✗N | e2e-browser ✓ | e2e-browser (0.93; 0.06) | 0.94 | e2e-browser ✓ | e2e-browser 0.94 · test-writer 0.53 · code-review 0.05 | e2e-browser (0.99) | 0.74 | e2e-browser ✓ | e2e-browser ✓ | e2e-browser ✓ | e2e-browser ✓ [e2e-browser 0.94] | e2e-browser ✓ (0.94) |
| SS-T025 | fácil / outros | changelog-release | — | changelog-release ✓ | changelog-release ✓ | changelog-release (0.97; 0.02) | 0.95 | changelog-release ✓ | changelog-release 0.95 · code-review 0.07 · security-review 0.05 | changelog-release (1.00) | 0.61 | changelog-release ✓ | changelog-release ✓ | changelog-release ✓ | changelog-release ✓ [changelog-release 0.95] | changelog-release ✓ (0.98) |
| SS-T026 | duas próximas | lead-report | ads-audit db-query | lead-report ✓ | lead-report ✓ | lead-report (0.65; 0.01) | 0.66 | lead-report ✓ | lead-report 0.59 · ads-audit 0.84 · db-query 0.82 | lead-report (0.69) | 0.75 | lead-report ✓ | lead-report ✓ | ads-audit ≈ | ads-audit ≈ [ads-audit 0.83] | lead-report ✓ (0.93) |
| SS-T027 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (1.00; 1.00) | — | ∅ ✓∅ | code-review 0.09 · security-review 0.04 · simplify 0.04 | code-review (0.56) | 0.06 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [docs-writer 0.23] | ∅ ✓∅ (1.00) |
| SS-T028 | fácil / outros | grilling | — | grilling ✓ | grilling ✓ | grilling (0.99; 0.01) | 0.91 | grilling ✓ | grilling 0.91 · code-review 0.04 · security-review 0.07 | grilling (1.00) | 0.25 | grilling ✓ | grilling ✓ | grilling ✓ | grilling ✓ [grilling 0.92] | grilling ✓ (0.99) |
| SS-T029 | vago | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (1.00; 1.00) | — | ∅ ✓∅ | code-review 0.18 · security-review 0.09 · simplify 0.06 | code-review (0.50) | 0.47 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [code-review 0.20] | ∅ ✓∅ (1.00) |
| SS-T030 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (1.00; 1.00) | — | ∅ ✓∅ | code-review 0.02 · security-review 0.03 · simplify 0.03 | simplify (0.73) | 0.06 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [whatsapp-template 0.08] | ∅ ✓∅ (1.00) |
| SS-T031 | trivial que parece pedir skill | ∅ | — | copywriting ✗I | ∅ ✓∅ | ∅ (0.92; 0.93) | — | ∅ ✓∅ | copywriting 0.54 · code-review 0.09 · security-review 0.02 | copywriting (0.99) | 0.56 | copywriting ✗I | copywriting ✗I | copywriting ✗I | copywriting ✗I [copywriting 0.56] | ∅ ✓∅ (0.95) |
| SS-T032 | cita o nome de uma skill | ∅ | — | ∅ ✓∅ | social-calendar ✗I | social-calendar (0.67; 0.21) | 0.25 | ∅ ✓∅ | social-calendar 0.26 · deploy-prod 0.22 · e2e-browser 0.31 | social-calendar (0.49) | 0.86 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [e2e-browser 0.28] | social-calendar ✗I (0.65) |
| SS-T033 | fácil / outros | code-review | — | code-review ✓ | code-review ✓ | code-review (1.00; 0.00) | 0.98 | code-review ✓ | code-review 0.98 · security-review 0.34 · simplify 0.17 | code-review (1.00) | 0.74 | code-review ✓ | code-review ✓ | code-review ✓ | code-review ✓ [code-review 0.98] | code-review ✓ (1.00) |
| SS-T034 | fácil / outros | landing-ab-test | — | copywriting ✗E | landing-ab-test ✓ | landing-ab-test (0.94; 0.05) | 0.94 | landing-ab-test ✓ | landing-ab-test 0.94 · code-review 0.01 · security-review 0.01 | landing-ab-test (1.00) | 0.24 | landing-ab-test ✓ | landing-ab-test ✓ | landing-ab-test ✓ | landing-ab-test ✓ [landing-ab-test 0.94] | landing-ab-test ✓ (0.99) |
| SS-T035 | fácil / outros | perf-profile | diagnosing-bugs | lead-report ✗E | perf-profile ✓ | perf-profile (0.99; 0.01) | 0.82 | perf-profile ✓ | perf-profile 0.85 · code-review 0.08 · security-review 0.03 | perf-profile (1.00) | 0.47 | perf-profile ✓ | perf-profile ✓ | perf-profile ✓ | perf-profile ✓ [perf-profile 0.84] | perf-profile ✓ (0.99) |
| SS-T036 | duas próximas | video-listing | social-calendar | video-listing ✓ | video-listing ✓ | video-listing (0.99; 0.01) | 0.90 | video-listing ✓ | video-listing 0.91 · code-review 0.01 · security-review 0.01 | video-listing (1.00) | 0.26 | video-listing ✓ | video-listing ✓ | video-listing ✓ | video-listing ✓ [video-listing 0.90] | video-listing ✓ (0.99) |
| SS-T037 | vago | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.99; 1.00) | — | ∅ ✓∅ | code-review 0.20 · security-review 0.12 · simplify 0.27 | simplify (0.69) | 0.38 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | copywriting ✗I [copywriting 0.52] | ∅ ✓∅ (0.99) |
| SS-T038 | fácil / outros | ∅ | — | refactor-safe ✗I | ∅ ✓∅ | ∅ (0.85; 0.87) | — | ∅ ✓∅ | code-review 0.14 · pr-open 0.03 · security-review 0.07 | code-review (0.87) | 0.85 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [code-review 0.16] | ∅ ✓∅ (0.91) |
| SS-T039 | trivial que parece pedir skill | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (1.00; 1.00) | — | ∅ ✓∅ | code-review 0.04 · security-review 0.04 · simplify 0.06 | code-review (0.49) | 0.83 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [prompt-tuning 0.12] | ∅ ✓∅ (0.99) |
| SS-T040 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (1.00; 1.00) | — | ∅ ✓∅ | code-review 0.25 · security-review 0.05 · simplify 0.16 | code-review (0.69) | 0.75 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | fix-ci ✗I [fix-ci 0.58] | ∅ ✓∅ (0.95) |
| SS-T041 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.99; 1.00) | — | ∅ ✓∅ | code-review 0.12 · security-review 0.03 · simplify 0.03 | code-review (0.64) | 0.42 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [code-review 0.13] | ∅ ✓∅ (0.99) |
| SS-T042 | composto | code-review | deploy-prod | deploy-prod ≈ | code-review ✓ | code-review (0.87; 0.02) | 0.58 | code-review ✓ | code-review 0.54 · deploy-prod 0.76 · security-review 0.23 | code-review (0.90) | 0.86 | code-review ✓ | code-review ✓ | deploy-prod ≈ | deploy-prod ≈ [deploy-prod 0.75] | code-review ✓ (0.79) |
| SS-T043 | fácil / outros | ad-creative | — | ad-creative ✓ | ad-creative ✓ | ad-creative (1.00; 0.00) | 0.98 | ad-creative ✓ | ad-creative 0.97 · code-review 0.01 · security-review 0.01 | ad-creative (1.00) | 0.10 | ∅ ✗N | ∅ ✗N | ∅ ✗N | ad-creative ✓ [ad-creative 0.97] | ad-creative ✓ (1.00) |
| SS-T044 | fácil / outros | social-calendar | — | ∅ ✗N | social-calendar ✓ | social-calendar (1.00; 0.00) | 0.97 | social-calendar ✓ | social-calendar 0.97 · code-review 0.01 · security-review 0.01 | social-calendar (1.00) | 0.22 | social-calendar ✓ | social-calendar ✓ | social-calendar ✓ | social-calendar ✓ [social-calendar 0.97] | social-calendar ✓ (1.00) |
| SS-T045 | duas próximas | copywriting | ad-creative | copywriting ✓ | copywriting ✓ | copywriting (0.99; 0.00) | 0.98 | copywriting ✓ | copywriting 0.98 · ad-creative 0.45 · code-review 0.01 | copywriting (1.00) | 0.22 | copywriting ✓ | copywriting ✓ | copywriting ✓ | copywriting ✓ [copywriting 0.98] | copywriting ✓ (1.00) |
| SS-T046 | cita o nome de uma skill | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.92; 0.93) | — | ∅ ✓∅ | deploy-prod 0.83 · deploy-dev 0.82 · code-review 0.02 | deploy-dev (0.80) | 0.47 | deploy-dev ✗I | deploy-dev ✗I | deploy-prod ✗I | deploy-prod ✗I [deploy-prod 0.83] | ∅ ✓∅ (0.92) |
| SS-T047 | composto | whatsapp-template | email-sequence | email-sequence ≈ | whatsapp-template ✓ | whatsapp-template (0.89; 0.00) | 0.28 | ∅ ✗N | whatsapp-template 0.25 · email-sequence 0.61 · code-review 0.01 | whatsapp-template (0.95) | 0.19 | ∅ ✗N | ∅ ✗N | ∅ ✗N | email-sequence ≈ [email-sequence 0.58] | whatsapp-template ✓ (0.94) |
| SS-T048 | fácil / outros | deploy-prod | — | deploy-prod ✓ | deploy-prod ✓ | deploy-prod (0.96; 0.00) | 0.86 | deploy-prod ✓ | deploy-prod 0.87 · pr-open 0.06 · code-review 0.04 | deploy-prod (0.79) | 0.89 | deploy-prod ✓ | deploy-prod ✓ | deploy-prod ✓ | deploy-prod ✓ [deploy-prod 0.84] | deploy-prod ✓ (0.95) |
| SS-T049 | fácil / outros | docs-writer | — | docs-writer ✓ | docs-writer ✓ | docs-writer (1.00; 0.00) | 0.98 | docs-writer ✓ | docs-writer 0.98 · code-review 0.02 · security-review 0.03 | docs-writer (1.00) | 0.51 | docs-writer ✓ | docs-writer ✓ | docs-writer ✓ | docs-writer ✓ [docs-writer 0.98] | docs-writer ✓ (1.00) |
| SS-T050 | fácil / outros | fix-ci | — | fix-ci ✓ | fix-ci ✓ | fix-ci (0.99; 0.01) | 0.93 | fix-ci ✓ | fix-ci 0.92 · code-review 0.04 · security-review 0.02 | fix-ci (1.00) | 0.52 | fix-ci ✓ | fix-ci ✓ | fix-ci ✓ | fix-ci ✓ [fix-ci 0.93] | fix-ci ✓ (1.00) |
| SS-T051 | cita o nome de uma skill | prompt-tuning | llm-eval | prompt-tuning ✓ | prompt-tuning ✓ | prompt-tuning (0.87; 0.10) | 0.63 | prompt-tuning ✓ | prompt-tuning 0.63 · code-review 0.22 · llm-eval 0.44 | prompt-tuning (0.65) | 0.52 | prompt-tuning ✓ | prompt-tuning ✓ | prompt-tuning ✓ | prompt-tuning ✓ [prompt-tuning 0.64] | prompt-tuning ✓ (0.74) |
| SS-T052 | duas próximas | diagnosing-bugs | fix-ci | test-writer ✗E | diagnosing-bugs ✓ | diagnosing-bugs (0.54; 0.01) | 0.82 | diagnosing-bugs ✓ | diagnosing-bugs 0.81 · fix-ci 0.70 · code-review 0.13 | diagnosing-bugs (0.84) | 0.51 | diagnosing-bugs ✓ | diagnosing-bugs ✓ | diagnosing-bugs ✓ | diagnosing-bugs ✓ [diagnosing-bugs 0.81] | diagnosing-bugs ✓ (0.73) |
| SS-T053 | fácil / outros | security-review | — | security-review ✓ | security-review ✓ | security-review (0.99; 0.00) | 0.98 | security-review ✓ | security-review 0.97 · code-review 0.93 · simplify 0.13 | security-review (1.00) | 0.65 | security-review ✓ | security-review ✓ | security-review ✓ | security-review ✓ [security-review 0.98] | security-review ✓ (1.00) |
| SS-T054 | fácil / outros | ux-review | — | ux-review ✓ | ux-review ✓ | ux-review (0.95; 0.00) | 0.92 | ux-review ✓ | ux-review 0.92 · e2e-browser 0.47 · code-review 0.19 | ux-review (0.84) | 0.58 | ux-review ✓ | ux-review ✓ | ux-review ✓ | ux-review ✓ [ux-review 0.92] | ux-review ✓ (0.95) |
| SS-T055 | jargão | ai-seo | — | ai-seo ✓ | ai-seo ✓ | ai-seo (0.61; 0.16) | 0.92 | ai-seo ✓ | ai-seo 0.93 · docs-writer 0.20 · e2e-browser 0.26 | ai-seo (0.96) | 0.75 | ai-seo ✓ | ai-seo ✓ | ai-seo ✓ | ai-seo ✓ [ai-seo 0.92] | ai-seo ✓ (0.98) |
| SS-T056 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (1.00; 1.00) | — | ∅ ✓∅ | code-review 0.01 · security-review 0.01 · simplify 0.02 | simplify (0.86) | 0.05 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [llm-eval 0.04] | ∅ ✓∅ (1.00) |
| SS-T057 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.98; 0.99) | — | ∅ ✓∅ | db-query 0.51 · code-review 0.01 · security-review 0.01 | db-query (1.00) | 0.58 | db-query ✗I | db-query ✗I | db-query ✗I | db-query ✗I [db-query 0.51] | ∅ ✓∅ (0.98) |
| SS-T058 | negação | ∅ | — | deploy-dev ✗I | ∅ ✓∅ | ∅ (0.91; 0.92) | — | ∅ ✓∅ | changelog-release 0.16 · db-query 0.31 · deploy-dev 0.06 | changelog-release (0.28) | 0.59 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [db-query 0.30] | ∅ ✓∅ (0.90) |
| SS-T059 | fácil / outros | video-listing | — | video-listing ✓ | video-listing ✓ | video-listing (0.99; 0.01) | 0.96 | video-listing ✓ | video-listing 0.96 · code-review 0.01 · security-review 0.02 | video-listing (1.00) | 0.75 | video-listing ✓ | video-listing ✓ | video-listing ✓ | video-listing ✓ [video-listing 0.96] | video-listing ✓ (0.99) |
| SS-T060 | trivial que parece pedir skill | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.97; 0.98) | — | ∅ ✓∅ | dependency-upgrade 0.07 · pr-open 0.03 · code-review 0.04 | dependency-upgrade (0.46) | 0.83 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [dependency-upgrade 0.07] | ∅ ✓∅ (0.96) |
| SS-T061 | fácil / outros | secrets-vault | — | secrets-vault ✓ | secrets-vault ✓ | secrets-vault (0.98; 0.01) | 0.94 | secrets-vault ✓ | secrets-vault 0.93 · code-review 0.05 · security-review 0.07 | secrets-vault (1.00) | 0.79 | secrets-vault ✓ | secrets-vault ✓ | secrets-vault ✓ | secrets-vault ✓ [secrets-vault 0.94] | secrets-vault ✓ (1.00) |
| SS-T062 | fácil / outros | ∅ | — | api-contract ✗I | ∅ ✓∅ | ∅ (0.99; 1.00) | — | ∅ ✓∅ | code-review 0.01 · security-review 0.01 · simplify 0.02 | simplify (0.77) | 0.29 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [docs-writer 0.09] | ∅ ✓∅ (0.99) |
| SS-T063 | duas próximas | migration-2bancos | — | lead-report ✗E | migration-2bancos ✓ | migration-2bancos (0.40; 0.42) | 0.62 | migration-2bancos ✓ | migration-2bancos 0.65 · db-query 0.04 · pr-open 0.03 | migration-2bancos (0.98) | 0.62 | migration-2bancos ✓ | migration-2bancos ✓ | migration-2bancos ✓ | migration-2bancos ✓ [migration-2bancos 0.66] | migration-2bancos ✓ (0.83) |
| SS-T064 | duas próximas | incident-postmortem | logs-prod | incident-postmortem ✓ | incident-postmortem ✓ | incident-postmortem (0.87; 0.00) | 0.96 | incident-postmortem ✓ | incident-postmortem 0.95 · logs-prod 0.43 · code-review 0.02 | incident-postmortem (0.68) | 0.68 | incident-postmortem ✓ | incident-postmortem ✓ | incident-postmortem ✓ | incident-postmortem ✓ [incident-postmortem 0.95] | incident-postmortem ✓ (0.93) |
| SS-T065 | jargão | whatsapp-template | — | whatsapp-template ✓ | whatsapp-template ✓ | whatsapp-template (0.99; 0.00) | 0.93 | whatsapp-template ✓ | whatsapp-template 0.93 · copywriting 0.62 · code-review 0.03 | whatsapp-template (1.00) | 0.29 | whatsapp-template ✓ | whatsapp-template ✓ | whatsapp-template ✓ | whatsapp-template ✓ [whatsapp-template 0.93] | whatsapp-template ✓ (0.99) |
| SS-T066 | fácil / outros | frontend-design | — | frontend-design ✓ | frontend-design ✓ | frontend-design (0.98; 0.00) | 0.95 | frontend-design ✓ | frontend-design 0.95 · grilling 0.17 · code-review 0.02 | frontend-design (0.97) | 0.35 | frontend-design ✓ | frontend-design ✓ | frontend-design ✓ | frontend-design ✓ [frontend-design 0.95] | frontend-design ✓ (0.97) |
| SS-T067 | fácil / outros | api-contract | — | api-contract ✓ | api-contract ✓ | api-contract (0.99; 0.00) | 0.95 | api-contract ✓ | api-contract 0.95 · code-review 0.14 · security-review 0.08 | api-contract (1.00) | 0.74 | api-contract ✓ | api-contract ✓ | api-contract ✓ | api-contract ✓ [api-contract 0.95] | api-contract ✓ (1.00) |
| SS-T068 | jargão | schema-markup | — | schema-markup ✓ | schema-markup ✓ | schema-markup (0.98; 0.01) | 0.94 | schema-markup ✓ | schema-markup 0.95 · seo-audit 0.22 · code-review 0.02 | schema-markup (1.00) | 0.48 | schema-markup ✓ | schema-markup ✓ | schema-markup ✓ | schema-markup ✓ [schema-markup 0.95] | schema-markup ✓ (1.00) |
| SS-T069 | fácil / outros | e2e-browser | — | e2e-browser ✓ | e2e-browser ✓ | e2e-browser (0.98; 0.01) | 0.95 | e2e-browser ✓ | e2e-browser 0.96 · code-review 0.37 · security-review 0.05 | e2e-browser (1.00) | 0.82 | e2e-browser ✓ | e2e-browser ✓ | e2e-browser ✓ | e2e-browser ✓ [e2e-browser 0.96] | e2e-browser ✓ (1.00) |
| SS-T070 | vago | deploy-dev | — | ∅ ✗N | ∅ ✗N | ∅ (0.88; 0.90) | — | ∅ ✗N | deploy-prod 0.31 · dependency-upgrade 0.52 · deploy-dev 0.25 | deploy-dev (0.69) | 0.40 | deploy-dev ✓ | ∅ ✗N | dependency-upgrade ✗E | dependency-upgrade ✗E [dependency-upgrade 0.53] | ∅ ✗N (0.90) |
| SS-T071 | fácil / outros | ∅ | — | ∅ ✓∅ | ∅ ✓∅ | ∅ (0.95; 0.96) | — | ∅ ✓∅ | dependency-upgrade 0.04 · code-review 0.04 · security-review 0.04 | code-review (0.35) | 0.74 | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ | ∅ ✓∅ [docs-writer 0.10] | ∅ ✓∅ (0.96) |
| SS-T072 | vago | grilling | to-tickets | ∅ ✗N | ∅ ✗N | ∅ (0.41; 0.44) | — | ∅ ✗N | grilling 0.28 · api-contract 0.28 · to-tickets 0.16 | grilling (0.89) | 0.64 | ∅ ✗N | ∅ ✗N | ∅ ✗N | ∅ ✗N [grilling 0.28] | grilling ✓ (0.44) |
| SS-T073 | jargão | schema-markup | — | schema-markup ✓ | schema-markup ✓ | schema-markup (1.00; 0.00) | 0.97 | schema-markup ✓ | schema-markup 0.97 · code-review 0.09 · security-review 0.02 | schema-markup (1.00) | 0.67 | schema-markup ✓ | schema-markup ✓ | schema-markup ✓ | schema-markup ✓ [schema-markup 0.97] | schema-markup ✓ (1.00) |
| SS-T074 | fácil / outros | db-query | — | lead-report ✗E | db-query ✓ | db-query (0.77; 0.02) | 0.93 | db-query ✓ | db-query 0.94 · lead-report 0.45 · logs-prod 0.33 | db-query (0.94) | 0.79 | db-query ✓ | db-query ✓ | db-query ✓ | db-query ✓ [db-query 0.94] | db-query ✓ (0.81) |
| SS-T075 | fácil / outros | programmatic-seo | — | programmatic-seo ✓ | programmatic-seo ✓ | programmatic-seo (0.99; 0.00) | 0.93 | programmatic-seo ✓ | programmatic-seo 0.93 · code-review 0.03 · security-review 0.02 | programmatic-seo (1.00) | 0.45 | programmatic-seo ✓ | programmatic-seo ✓ | programmatic-seo ✓ | programmatic-seo ✓ [programmatic-seo 0.94] | programmatic-seo ✓ (1.00) |
| SS-T076 | fácil / outros | seo-audit | — | seo-audit ✓ | seo-audit ✓ | seo-audit (1.00; 0.00) | 0.92 | seo-audit ✓ | seo-audit 0.93 · code-review 0.02 · security-review 0.02 | seo-audit (1.00) | 0.74 | seo-audit ✓ | seo-audit ✓ | seo-audit ✓ | seo-audit ✓ [seo-audit 0.92] | seo-audit ✓ (1.00) |
| SS-T077 | cita o nome de uma skill | logs-prod | diagnosing-bugs | diagnosing-bugs ≈ | ads-audit ✗E | ads-audit (0.49; 0.01) | 0.33 | ∅ ✗N | ads-audit 0.36 · diagnosing-bugs 0.54 · logs-prod 0.56 | ads-audit (0.13) | 0.54 | ads-audit ✗E | ∅ ✗N | logs-prod ✓ | diagnosing-bugs ≈ [diagnosing-bugs 0.54] | diagnosing-bugs ≈ (0.44) |
| SS-T078 | cita o nome de uma skill | rollback | — | rollback ✓ | rollback ✓ | rollback (1.00; 0.00) | 0.98 | rollback ✓ | rollback 0.98 · code-review 0.08 · security-review 0.13 | rollback (1.00) | 0.88 | rollback ✓ | rollback ✓ | rollback ✓ | rollback ✓ [rollback 0.98] | rollback ✓ (1.00) |
| SS-T079 | composto | migration-2bancos | api-contract | api-contract ≈ | api-contract ≈ | api-contract (0.85; 0.07) | 0.60 | api-contract ≈ | api-contract 0.57 · migration-2bancos 0.03 · db-query 0.03 | migration-2bancos (0.76) | 0.61 | migration-2bancos ✓ | ∅ ✗N | api-contract ≈ | api-contract ≈ [api-contract 0.56] | api-contract ≈ (0.74) |
| SS-T080 | jargão | perf-profile | db-query | db-query ≈ | db-query ≈ | db-query (0.93; 0.02) | 0.39 | ∅ ✗N | db-query 0.39 · perf-profile 0.86 · code-review 0.09 | perf-profile (0.85) | 0.68 | perf-profile ✓ | perf-profile ✓ | perf-profile ✓ | perf-profile ✓ [perf-profile 0.84] | perf-profile ✓ (0.88) |
| SS-T081 | fácil / outros | test-writer | — | ∅ ✗N | test-writer ✓ | test-writer (0.89; 0.07) | 0.86 | test-writer ✓ | test-writer 0.88 · refactor-safe 0.17 · code-review 0.17 | test-writer (0.82) | 0.51 | test-writer ✓ | test-writer ✓ | test-writer ✓ | test-writer ✓ [test-writer 0.87] | test-writer ✓ (0.93) |
| SS-T082 | jargão | migration-2bancos | — | frontend-design ✗E | migration-2bancos ✓ | migration-2bancos (0.92; 0.01) | 0.89 | migration-2bancos ✓ | migration-2bancos 0.88 · db-query 0.08 · code-review 0.05 | migration-2bancos (0.98) | 0.68 | migration-2bancos ✓ | migration-2bancos ✓ | migration-2bancos ✓ | migration-2bancos ✓ [migration-2bancos 0.89] | migration-2bancos ✓ (0.98) |
| SS-T083 | fácil / outros | ads-audit | — | ads-audit ✓ | ads-audit ✓ | ads-audit (0.99; 0.01) | 0.96 | ads-audit ✓ | ads-audit 0.96 · code-review 0.02 · security-review 0.02 | ads-audit (1.00) | 0.56 | ads-audit ✓ | ads-audit ✓ | ads-audit ✓ | ads-audit ✓ [ads-audit 0.96] | ads-audit ✓ (1.00) |
| SS-T084 | fácil / outros | lead-report | — | lead-report ✓ | lead-report ✓ | lead-report (0.99; 0.00) | 0.90 | lead-report ✓ | lead-report 0.92 · code-review 0.01 · security-review 0.01 | lead-report (1.00) | 0.84 | lead-report ✓ | lead-report ✓ | lead-report ✓ | lead-report ✓ [lead-report 0.90] | lead-report ✓ (1.00) |
| SS-T085 | fácil / outros | llm-eval | — | llm-eval ✓ | llm-eval ✓ | llm-eval (0.98; 0.01) | 0.88 | llm-eval ✓ | llm-eval 0.88 · db-query 0.51 · code-review 0.04 | llm-eval (0.86) | 0.70 | llm-eval ✓ | llm-eval ✓ | llm-eval ✓ | llm-eval ✓ [llm-eval 0.88] | llm-eval ✓ (0.99) |
| SS-T086 | duas próximas | llm-eval | — | ∅ ✗N | llm-eval ✓ | llm-eval (0.60; 0.14) | 0.69 | llm-eval ✓ | llm-eval 0.67 · logs-prod 0.48 · prompt-tuning 0.28 | llm-eval (0.26) | 0.59 | llm-eval ✓ | llm-eval ✓ | llm-eval ✓ | db-query ✗E [db-query 0.77] | llm-eval ✓ (0.67) |
| SS-T087 | fácil / outros | email-sequence | — | email-sequence ✓ | email-sequence ✓ | email-sequence (1.00; 0.00) | 0.95 | email-sequence ✓ | email-sequence 0.95 · code-review 0.01 · security-review 0.03 | email-sequence (1.00) | 0.13 | ∅ ✗N | ∅ ✗N | ∅ ✗N | email-sequence ✓ [email-sequence 0.96] | email-sequence ✓ (1.00) |
