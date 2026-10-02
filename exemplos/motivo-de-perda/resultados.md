# Resultados — motivo-de-perda

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, limiares, variante principal e critério: `perguntas.py`; validação, decisão e baseline: `motivo.py`; bateria do código (sem API): `testa_falhas.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Limiares: {'grupo': 0.5, 'folha': 0.5, 'folha_unica': 0.5, 'guarda': 0.5, 'sem_motivo': 0.4}; teto da conversa 6000 caracteres.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (68 conversas: 8 `sem_informacao`, 7 com `folha: null`), variante principal com os limiares acima; **variante_principal**: c; **1_motivo_inventado**: gabarito `sem_informacao` e saiu outro grupo sem revisar ≤ 1/8; **2_grupo_errado_automatizado**: grupo ≠ gabarito (e folha fora de `aceitaveis`) sem revisar ≤ 6/68 (≤ 0,09); **3_acerto_folgado**: folha ∈ `aceitaveis` (ou só o grupo certo quando `folha` é null), revisão e falha contam como erro ≥ 0,70; **4_grupo_certo**: grupo = gabarito ou folha ∈ `aceitaveis`, revisão e falha contam como erro ≥ 0,80; **5_revisao**: conversas mandadas a revisão (inclui falha operacional) ≤ 20% (≤ 13/68); **6_contra_baseline**: acerto folgado > o do baseline de palavras-chave nos mesmos casos; **se_falhar**: 1 = o relatório inventa motivo: não serve nem como sugestão; 2 = o relatório mente de grupo: não serve sem revisão humana de tudo; 3/4 = não lê a conversa melhor que um gestor apressado; 5 = revisa demais para valer a automação; 6 = palavra-chave basta

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T16:14:33-03:00): `perguntas.py` sha256 8b2914532a561610… · `motivo.py` sha256 44151a7e23ba2ec4… · `run.py` sha256 625005edb785efe1… · `dados/teste.json` sha256 015a04e1f083ddb7… · `dados/taxonomia.json` sha256 7ab1ad5faeeedc80…

## Lado a lado

| conjunto | variante | n | acerto estrito | acerto folgado | grupo certo | motivo INVENTADO | grupo errado auto. | só-grupo certo | sem_info certo | absteve | folha errada | revisar | falha | req/caso | tokens/caso | US$/1000 | p50_ms | p95_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | código: palavra-chave por folha | 34 | 0.471 | 0.500 | 0.529 | 1/3 | 16/34 | 0/2 | 2/3 | 0/32 | 1/34 | 0/34 | 0/34 | 0 | 0 | 0 | 0 | 0 |
| ajuste | a · duas etapas (grupo → folhas do grupo) | 34 | 0.794 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 3/3 | 0/32 | 0/34 | 2/34 | 0/34 | 2.00 | 2584 | 0.1085 | 557 | 957 |
| ajuste | b · Choice única sobre as 30 folhas | 34 | 0.882 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 3/3 | 0/32 | 1/34 | 0/34 | 0/34 | 1.00 | 2588 | 0.1087 | 266 | 363 |
| ajuste | c · uma requisição (grupo + folhas por grupo) | 34 | 0.824 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 3/3 | 0/32 | 0/34 | 2/34 | 0/34 | 1.00 | 6071 | 0.2550 | 286 | 353 |
| ajuste | c sem as guardas (informativa) | 34 | 0.824 | 0.882 | 0.882 | 0/3 | 3/34 | 2/2 | 3/3 | 0/32 | 0/34 | 1/34 | 0/34 | 1.00 | 6071 | 0.2550 | 286 | 353 |
| teste | código: palavra-chave por folha | 68 | 0.250 | 0.279 | 0.397 | 7/8 | 41/68 | 0/7 | 1/8 | 0/61 | 8/68 | 0/68 | 0/68 | 0 | 0 | 0 | 0 | 0 |
| teste | a · duas etapas (grupo → folhas do grupo) | 68 | 0.824 | 0.868 | 0.882 | 0/8 | 3/68 | 5/7 | 7/8 | 0/61 | 1/68 | 5/68 | 0/68 | 2.00 | 2572 | 0.1080 | 561 | 676 |
| teste | b · Choice única sobre as 30 folhas | 68 | 0.824 | 0.868 | 0.926 | 0/8 | 1/68 | 0/7 | 8/8 | 1/61 | 3/68 | 4/68 | 0/68 | 1.00 | 2584 | 0.1085 | 270 | 323 |
| teste | c · uma requisição (grupo + folhas por grupo) | 68 | 0.809 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 7/8 | 0/61 | 1/68 | 5/68 | 0/68 | 1.00 | 6067 | 0.2548 | 286 | 338 |
| teste | c sem as guardas (informativa) | 68 | 0.838 | 0.882 | 0.897 | 0/8 | 6/68 | 6/7 | 7/8 | 0/61 | 1/68 | 1/68 | 0/68 | 1.00 | 6067 | 0.2548 | 286 | 338 |

| conjunto | n | difíceis | `folha: null` | `sem_informacao` | falhas | requisições (todas as variantes) | novas (não cache) | tokens | modelo |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | 34 | 18 | 2 | 3 | 0 | 136 | 0 | 382250 | jev-1.13.0 |
| teste | 68 | 41 | 7 | 8 | 0 | 272 | 0 | 763081 | jev-1.13.0 |

## Conjunto `ajuste` — 34 conversas (arquivo versão 2026-10-01, autor fable); 18 difíceis, 2 com `folha: null`, 3 `sem_informacao`, 0 em revisão por falha operacional, entrada inválida ou teto; taxonomia de 8 grupos e 30 folhas

### Desfecho — baseline de código × variantes com Jev, nas mesmas conversas

`estrito` = a folha principal do gabarito (ou só o grupo certo quando `folha` é null). `folgado` = folha ∈ `aceitaveis` (ou só o grupo certo quando `folha` é null). `grupo certo` = grupo = gabarito ou folha aceitável. **Motivo INVENTADO** (erro caro) = gabarito `sem_informacao` e saiu outro grupo, automatizado (denominador = casos `sem_informacao`). **Grupo errado automatizado** (erro caro) = grupo ≠ gabarito sem revisão, inclui os inventados. `só-grupo certo` = nos casos `folha: null`, saiu só o grupo certo. `absteve` = havia folha, saiu só o grupo certo (nem acerto nem erro). Revisão e falha contam como erro em todas as taxas de acerto. Custo e latência: só as requisições que a variante envia em produção, medidas. Variante principal (a que o critério julga): **c · uma requisição (grupo + folhas por grupo)**.

| variante | n | acerto estrito | acerto folgado | grupo certo | motivo INVENTADO | grupo errado auto. | só-grupo certo | sem_info certo | absteve | folha errada | revisar | falha | req/caso | tokens/caso | US$/1000 | p50_ms | p95_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| código: palavra-chave por folha | 34 | 0.471 | 0.500 | 0.529 | 1/3 | 16/34 | 0/2 | 2/3 | 0/32 | 1/34 | 0/34 | 0/34 | 0 | 0 | 0 | 0 | 0 |
| a · duas etapas (grupo → folhas do grupo) | 34 | 0.794 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 3/3 | 0/32 | 0/34 | 2/34 | 0/34 | 2.00 | 2584 | 0.1085 | 557 | 957 |
| b · Choice única sobre as 30 folhas | 34 | 0.882 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 3/3 | 0/32 | 1/34 | 0/34 | 0/34 | 1.00 | 2588 | 0.1087 | 266 | 363 |
| c · uma requisição (grupo + folhas por grupo) | 34 | 0.824 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 3/3 | 0/32 | 0/34 | 2/34 | 0/34 | 1.00 | 6071 | 0.2550 | 286 | 353 |
| c sem as guardas (informativa) | 34 | 0.824 | 0.882 | 0.882 | 0/3 | 3/34 | 2/2 | 3/3 | 0/32 | 0/34 | 1/34 | 0/34 | 1.00 | 6071 | 0.2550 | 286 | 353 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 motivo INVENTADO (gabarito `sem_informacao`, saiu outro grupo, automatizado) | 0/3 | ≤ 1 | ✓ |
| 2 grupo errado automatizado (inclui os inventados) | 2/34 (0.059) | ≤ 0.09 | ✓ |
| 3 acerto folgado (revisão e falha = erro) | 0.882 | ≥ 0.70 | ✓ |
| 4 grupo certo (revisão e falha = erro) | 0.882 | ≥ 0.80 | ✓ |
| 5 revisão (inclui falha) | 2/34 (0.059) | ≤ 0.20 | ✓ |
| 6 contra o baseline de palavras-chave | 0.882 × 0.500 | > | ✓ |

### Por família difícil (pela `nota` do rotulador) — acertos folgados; erros caros e revisões da principal

| família | n | `null` | base | a | b | c | c-sg | inventado (principal) | grupo errado (principal) | revisar (principal) |
|---|---|---|---|---|---|---|---|---|---|---|
| dois motivos | 2 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 |
| sumiço depois de preço | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| motivo real diferente do declarado | 1 | 0 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| motivo do corretor | 4 | 0 | 1 | 4 | 4 | 4 | 4 | 0 | 0 | 0 |
| motivo dito com educação | 2 | 0 | 1 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |
| fronteira entre folhas | 4 | 0 | 4 | 3 | 4 | 3 | 3 | 0 | 1 | 0 |
| só o grupo é decidível | 2 | 2 | 0 | 2 | 0 | 2 | 2 | 0 | 0 | 0 |
| fechou em outro lugar | 2 | 0 | 1 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |
| fácil / outros | 16 | 0 | 8 | 14 | 16 | 14 | 14 | 0 | 0 | 2 |

### As guardas na principal (`c`) — o que cada Noul mudou

| guarda | disparou | tirou um erro | tirou um acerto | casos |
|---|---|---|---|---|
| `blames_agency` (grupo atendimento) | 0 | 0 | 0 | — |
| `closed_elsewhere` (grupo concorrencia) | 1 | 1 | 0 | MP-A020(✗G→?) |
| `reason_stated` (grupo ≠ sem_informacao) | 0 | 0 | 0 | — |

### Os sinais — quem aponta o grupo e a folha certos, sem limiar nenhum

| quem aponta o grupo | grupo certo |
|---|---|
| Choice `group` (requisição `grupo`) | 29/34 |
| soma das folhas por grupo (Choice única) | 32/34 |
| Choice `group` (requisição `tudo`) | 30/34 |

| quem aponta a folha | a principal | alguma aceitável | `only_group` |
|---|---|---|---|
| Choice das folhas do grupo vencedor (`folhas`) | 26/32 | 29/32 | 0/32 |
| Choice única (vencedora) | 30/32 | 31/32 | 0/32 |
| Choice `leaf.<grupo vencedor>` (`tudo`) | 27/32 | 29/32 | 0/32 |

Nos 2 casos `folha: null`: `only_group` saiu em `folhas` 2, em `tudo` 2; p da folha vencedora na Choice única: 0.84, 0.29.

p(grupo vencedor) na Choice `group` (`grupo`): quando certo (n = 29) mínimo 0.48, p10 0.67, mediana 0.99; quando errado (n = 5) mínimo 0.52, mediana 0.65, máximo 0.89. 
p(folha vencedora) em `folhas`: certa mínimo 0.68, p10 0.94, mediana 1.00; errada (fora de aceitáveis) 0.64, 0.99, 1.00. Na Choice única: certa mínimo 0.76, p10 0.86, mediana 1.00; errada 0.78.

A MESMA Choice `group` em duas requisições (`grupo` × `tudo`, isolamento ≠ determinismo) trocou de vencedor em 1/34: MP-A033 concorrencia→atendimento.

Noul `reason_stated` (requisição `grupo`): onde o gabarito pede sim (n = 31) mínimo 0.52, p10 0.86, mediana 0.97; onde pede não (n = 3) mediana 0.06, p90 0.37, máximo 0.37.

Noul `blames_agency` (requisição `grupo`): onde o gabarito pede sim (n = 6) mínimo 0.60, p10 0.60, mediana 0.91; onde pede não (n = 28) mediana 0.04, p90 0.15, máximo 0.69.

Noul `closed_elsewhere` (requisição `grupo`): onde o gabarito pede sim (n = 4) mínimo 0.93, p10 0.93, mediana 0.95; onde pede não (n = 30) mediana 0.02, p90 0.04, máximo 0.95.

O mesmo Noul em requisições diferentes: `grupo` × `unica` diferença absoluta média 0.006, máxima 0.100; `grupo` × `tudo` média 0.004, máxima 0.070 (n = 102).

### Cobertura × erro por limiar (um limiar por vez; os outros como em `perguntas.py`)

**c · uma requisição (grupo + folhas por grupo)** — limiar `grupo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 33/34 | 0.912 | 0.912 | 0/3 | 2/34 | 2/2 | 0 | 0 | 1 |
| 0.200 | 33/34 | 0.912 | 0.912 | 0/3 | 2/34 | 2/2 | 0 | 0 | 1 |
| 0.300 | 33/34 | 0.912 | 0.912 | 0/3 | 2/34 | 2/2 | 0 | 0 | 1 |
| 0.400 | 33/34 | 0.912 | 0.912 | 0/3 | 2/34 | 2/2 | 0 | 0 | 1 |
| 0.500 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.600 | 30/34 | 0.824 | 0.824 | 0/3 | 2/34 | 2/2 | 0 | 0 | 4 |
| 0.700 | 28/34 | 0.765 | 0.765 | 0/3 | 2/34 | 2/2 | 0 | 0 | 6 |
| 0.800 | 26/34 | 0.735 | 0.735 | 0/3 | 1/34 | 1/2 | 0 | 0 | 8 |
| 0.900 | 23/34 | 0.647 | 0.647 | 0/3 | 1/34 | 1/2 | 0 | 0 | 11 |

**c · uma requisição (grupo + folhas por grupo)** — limiar `folha` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.200 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.300 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.400 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.500 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.600 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.700 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.800 | 32/34 | 0.824 | 0.882 | 0/3 | 2/34 | 2/2 | 2 | 0 | 2 |
| 0.900 | 32/34 | 0.824 | 0.882 | 0/3 | 2/34 | 2/2 | 2 | 0 | 2 |

**c · uma requisição (grupo + folhas por grupo)** — limiar `guarda` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 33/34 | 0.882 | 0.882 | 0/3 | 3/34 | 2/2 | 0 | 0 | 1 |
| 0.200 | 33/34 | 0.882 | 0.882 | 0/3 | 3/34 | 2/2 | 0 | 0 | 1 |
| 0.300 | 33/34 | 0.882 | 0.882 | 0/3 | 3/34 | 2/2 | 0 | 0 | 1 |
| 0.400 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.500 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.600 | 31/34 | 0.853 | 0.853 | 0/3 | 2/34 | 2/2 | 0 | 0 | 3 |
| 0.700 | 31/34 | 0.853 | 0.853 | 0/3 | 2/34 | 2/2 | 0 | 0 | 3 |
| 0.800 | 31/34 | 0.853 | 0.853 | 0/3 | 2/34 | 2/2 | 0 | 0 | 3 |
| 0.900 | 29/34 | 0.794 | 0.794 | 0/3 | 2/34 | 2/2 | 0 | 0 | 5 |

**c · uma requisição (grupo + folhas por grupo)** — limiar `sem_motivo` (em uso: 0.4)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.200 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.300 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.400 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.500 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.600 | 31/34 | 0.853 | 0.853 | 0/3 | 2/34 | 2/2 | 0 | 0 | 3 |
| 0.700 | 31/34 | 0.853 | 0.853 | 0/3 | 2/34 | 2/2 | 0 | 0 | 3 |
| 0.800 | 31/34 | 0.853 | 0.853 | 0/3 | 2/34 | 2/2 | 0 | 0 | 3 |
| 0.900 | 29/34 | 0.794 | 0.794 | 0/3 | 2/34 | 2/2 | 0 | 0 | 5 |

**a · duas etapas (grupo → folhas do grupo)** — limiar `grupo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 33/34 | 0.912 | 0.912 | 0/3 | 2/34 | 2/2 | 0 | 0 | 1 |
| 0.200 | 33/34 | 0.912 | 0.912 | 0/3 | 2/34 | 2/2 | 0 | 0 | 1 |
| 0.300 | 33/34 | 0.912 | 0.912 | 0/3 | 2/34 | 2/2 | 0 | 0 | 1 |
| 0.400 | 33/34 | 0.912 | 0.912 | 0/3 | 2/34 | 2/2 | 0 | 0 | 1 |
| 0.500 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.600 | 30/34 | 0.824 | 0.824 | 0/3 | 2/34 | 2/2 | 0 | 0 | 4 |
| 0.700 | 28/34 | 0.765 | 0.765 | 0/3 | 2/34 | 2/2 | 0 | 0 | 6 |
| 0.800 | 26/34 | 0.735 | 0.735 | 0/3 | 1/34 | 1/2 | 0 | 0 | 8 |
| 0.900 | 22/34 | 0.647 | 0.647 | 0/3 | 0/34 | 1/2 | 0 | 0 | 12 |

**a · duas etapas (grupo → folhas do grupo)** — limiar `folha` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.200 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.300 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.400 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.500 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.600 | 32/34 | 0.882 | 0.882 | 0/3 | 2/34 | 2/2 | 0 | 0 | 2 |
| 0.700 | 32/34 | 0.853 | 0.882 | 0/3 | 2/34 | 2/2 | 1 | 0 | 2 |
| 0.800 | 32/34 | 0.853 | 0.882 | 0/3 | 2/34 | 2/2 | 1 | 0 | 2 |
| 0.900 | 32/34 | 0.824 | 0.882 | 0/3 | 2/34 | 2/2 | 2 | 0 | 2 |

**b · Choice única sobre as 30 folhas** — limiar `grupo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.200 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.300 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.400 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.500 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.600 | 33/34 | 0.912 | 0.941 | 0/3 | 1/34 | 0/2 | 0 | 1 | 1 |
| 0.700 | 33/34 | 0.912 | 0.941 | 0/3 | 1/34 | 0/2 | 0 | 1 | 1 |
| 0.800 | 30/34 | 0.853 | 0.882 | 0/3 | 0/34 | 0/2 | 0 | 1 | 4 |
| 0.900 | 29/34 | 0.824 | 0.853 | 0/3 | 0/34 | 0/2 | 0 | 1 | 5 |

**b · Choice única sobre as 30 folhas** — limiar `folha_unica` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.200 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.300 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.400 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.500 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.600 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.700 | 34/34 | 0.912 | 0.941 | 0/3 | 2/34 | 0/2 | 0 | 1 | 0 |
| 0.800 | 34/34 | 0.824 | 0.941 | 0/3 | 2/34 | 0/2 | 3 | 1 | 0 |
| 0.900 | 34/34 | 0.765 | 0.941 | 0/3 | 2/34 | 1/2 | 6 | 0 | 0 |

### Custo e latência por formato de requisição (medidos)

| requisição | enviadas | novas (não cache) | tokens por requisição | p50_ms | p95_ms | quem usa |
|---|---|---|---|---|---|---|
| grupo | 34 | 0 | 1545 | 297 | 693 | a |
| folhas | 34 | 0 | 1039 | 260 | 330 | a |
| unica | 34 | 0 | 2588 | 266 | 363 | b |
| tudo | 34 | 0 | 6071 | 286 | 353 | c |

Tudo o que esta execução usou: 136 requisições (0 novas), 382250 tokens, US$ 0.0161 · modelo: jev-1.13.0. Latência = a da chamada original de cada requisição (o cache a guarda), medida com 8 conversas em paralelo.

### Caso a caso

Marca: ✓ a folha principal · ≈ aceitável · ✓G só grupo, certo · ∅G absteve da folha (grupo certo) · ✗f folha errada (grupo certo) · ✗G grupo errado · ✗I motivo INVENTADO · ? revisar · ✗F falha. Célula = `grupo/folha marca`; `∅` = sem folha. `grupo` = Choice `group` com p(vencedor); `nouls` = reason_stated · blames_agency · closed_elsewhere (requisição `grupo`).

| id | fam | gabarito | outras aceitáveis | base | grupo | folhas | a | única | b | tudo | c | nouls | c-sg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MP-A001 | dois motivos | localizacao/distancia_deslocamento | — | localizacao/distancia_deslocamento ✓ | localizacao (1.00) | distancia_deslocamento (1.00) | localizacao/distancia_deslocamento ✓ | distancia_deslocamento (1.00; grupo 1.00) | localizacao/distancia_deslocamento ✓ | localizacao (1.00) › distancia_deslocamento (1.00) | localizacao/distancia_deslocamento ✓ | 0.98 · 0.03 · 0.03 | localizacao/distancia_deslocamento ✓ |
| MP-A002 | fácil / outros | credito_documentacao/restricao_cadastral | — | credito_documentacao/documentacao_imovel ✗f | credito_documentacao (0.99) | restricao_cadastral (1.00) | credito_documentacao/restricao_cadastral ✓ | restricao_cadastral (1.00; grupo 1.00) | credito_documentacao/restricao_cadastral ✓ | credito_documentacao (0.98) › restricao_cadastral (1.00) | credito_documentacao/restricao_cadastral ✓ | 0.94 · 0.04 · 0.02 | credito_documentacao/restricao_cadastral ✓ |
| MP-A003 | fácil / outros | credito_documentacao/documentacao_imovel | — | credito_documentacao/documentacao_imovel ✓ | credito_documentacao (0.95) | documentacao_imovel (1.00) | credito_documentacao/documentacao_imovel ✓ | documentacao_imovel (1.00; grupo 1.00) | credito_documentacao/documentacao_imovel ✓ | credito_documentacao (0.96) › documentacao_imovel (1.00) | credito_documentacao/documentacao_imovel ✓ | 0.98 · 0.14 · 0.02 | credito_documentacao/documentacao_imovel ✓ |
| MP-A004 | fácil / outros | imovel/falta_item | — | preco/preco_acima_orcamento ✗G | imovel (0.84) | falta_item (0.97) | imovel/falta_item ✓ | falta_item (0.96; grupo 0.96) | imovel/falta_item ✓ | imovel (0.80) › falta_item (0.98) | imovel/falta_item ✓ | 0.98 · 0.13 · 0.02 | imovel/falta_item ✓ |
| MP-A005 | fácil / outros | momento_cliente/decisor_vetou | — | sem_informacao/adiou_sem_motivo ✗G | momento_cliente (0.95) | decisor_vetou (0.80) | momento_cliente/decisor_vetou ✓ | decisor_vetou (1.00; grupo 1.00) | momento_cliente/decisor_vetou ✓ | momento_cliente (0.94) › decisor_vetou (0.78) | momento_cliente/decisor_vetou ✓ | 0.86 · 0.03 · 0.02 | momento_cliente/decisor_vetou ✓ |
| MP-A006 | fácil / outros | preco/preco_acima_orcamento | — | imovel/diferente_do_anuncio ✗G | preco (0.96) | preco_acima_orcamento (0.99) | preco/preco_acima_orcamento ✓ | preco_acima_orcamento (1.00; grupo 1.00) | preco/preco_acima_orcamento ✓ | preco (0.97) › preco_acima_orcamento (0.98) | preco/preco_acima_orcamento ✓ | 0.98 · 0.04 · 0.02 | preco/preco_acima_orcamento ✓ |
| MP-A007 | sumiço depois de preço | sem_informacao/sumiu_apos_valor | — | localizacao/entorno_seguranca ✗I | sem_informacao (1.00) | sumiu_apos_valor (0.68) | sem_informacao/sumiu_apos_valor ✓ | sumiu_apos_valor (0.84; grupo 1.00) | sem_informacao/sumiu_apos_valor ✓ | sem_informacao (1.00) › sumiu_apos_valor (0.76) | sem_informacao/sumiu_apos_valor ✓ | 0.04 · 0.02 · 0.01 | sem_informacao/sumiu_apos_valor ✓ |
| MP-A008 | motivo real diferente do declarado | atendimento/visita_falhou | — | atendimento/visita_falhou ✓ | atendimento (1.00) | visita_falhou (1.00) | atendimento/visita_falhou ✓ | visita_falhou (1.00; grupo 1.00) | atendimento/visita_falhou ✓ | atendimento (1.00) › visita_falhou (1.00) | atendimento/visita_falhou ✓ | 0.97 · 0.91 · 0.02 | atendimento/visita_falhou ✓ |
| MP-A009 | motivo do corretor | atendimento/visita_falhou | — | atendimento/visita_falhou ✓ | atendimento (0.98) | visita_falhou (1.00) | atendimento/visita_falhou ✓ | visita_falhou (0.98; grupo 0.99) | atendimento/visita_falhou ✓ | atendimento (0.98) › visita_falhou (1.00) | atendimento/visita_falhou ✓ | 0.97 · 0.80 · 0.03 | atendimento/visita_falhou ✓ |
| MP-A010 | fácil / outros | imovel/estado_conservacao | — | imovel/estado_conservacao ✓ | imovel (0.98) | estado_conservacao (1.00) | imovel/estado_conservacao ✓ | estado_conservacao (1.00; grupo 1.00) | imovel/estado_conservacao ✓ | imovel (0.98) › estado_conservacao (1.00) | imovel/estado_conservacao ✓ | 0.98 · 0.15 · 0.04 | imovel/estado_conservacao ✓ |
| MP-A011 | motivo dito com educação | sem_informacao/adiou_sem_motivo | — | sem_informacao/adiou_sem_motivo ✓ | sem_informacao (0.99) | adiou_sem_motivo (0.95) | sem_informacao/adiou_sem_motivo ✓ | adiou_sem_motivo (0.88; grupo 0.99) | sem_informacao/adiou_sem_motivo ✓ | sem_informacao (0.99) › adiou_sem_motivo (0.94) | sem_informacao/adiou_sem_motivo ✓ | 0.37 · 0.09 · 0.02 | sem_informacao/adiou_sem_motivo ✓ |
| MP-A012 | dois motivos | imovel/tamanho_planta | — | preco/preco_acima_orcamento ✗G | preco (0.89) | preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ✗G | preco_acima_orcamento (0.78; grupo 0.78) | preco/preco_acima_orcamento ✗G | preco (0.90) › preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ✗G | 0.98 · 0.03 · 0.02 | preco/preco_acima_orcamento ✗G |
| MP-A013 | fácil / outros | sem_informacao/sumiu_sem_resposta | — | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao (1.00) | sumiu_sem_resposta (1.00) | sem_informacao/sumiu_sem_resposta ✓ | sumiu_sem_resposta (1.00; grupo 1.00) | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao (1.00) › sumiu_sem_resposta (1.00) | sem_informacao/sumiu_sem_resposta ✓ | 0.06 · 0.04 · 0.02 | sem_informacao/sumiu_sem_resposta ✓ |
| MP-A014 | fácil / outros | concorrencia/direto_proprietario | — | credito_documentacao/garantia_locaticia ✗G | concorrencia (1.00) | direto_proprietario (1.00) | concorrencia/direto_proprietario ✓ | direto_proprietario (1.00; grupo 1.00) | concorrencia/direto_proprietario ✓ | concorrencia (1.00) › direto_proprietario (1.00) | concorrencia/direto_proprietario ✓ | 0.97 · 0.14 · 0.93 | concorrencia/direto_proprietario ✓ |
| MP-A015 | motivo do corretor | atendimento/pressao_insistencia | — | preco/preco_acima_orcamento ✗G | atendimento (1.00) | pressao_insistencia (1.00) | atendimento/pressao_insistencia ✓ | pressao_insistencia (1.00; grupo 1.00) | atendimento/pressao_insistencia ✓ | atendimento (1.00) › pressao_insistencia (1.00) | atendimento/pressao_insistencia ✓ | 0.98 · 0.96 · 0.03 | atendimento/pressao_insistencia ✓ |
| MP-A016 | fronteira entre folhas | momento_cliente/adiou_decisao | — | momento_cliente/adiou_decisao ✓ | preco (0.72) | condicao_pagamento (0.64) | preco/condicao_pagamento ✗G | adiou_decisao (1.00; grupo 1.00) | momento_cliente/adiou_decisao ✓ | preco (0.75) › condicao_pagamento (0.58) | preco/condicao_pagamento ✗G | 0.97 · 0.02 · 0.02 | preco/condicao_pagamento ✗G |
| MP-A017 | fácil / outros | localizacao/entorno_seguranca | — | localizacao/entorno_seguranca ✓ | localizacao (0.48) | entorno_seguranca (1.00) | localizacao/∅ ? | entorno_seguranca (0.95; grupo 0.95) | localizacao/entorno_seguranca ✓ | localizacao (0.49) › entorno_seguranca (1.00) | localizacao/∅ ? | 0.86 · 0.03 · 0.02 | localizacao/∅ ? |
| MP-A018 | fácil / outros | credito_documentacao/financiamento_negado | — | preco/condicao_pagamento ✗G | credito_documentacao (0.95) | financiamento_negado (0.98) | credito_documentacao/financiamento_negado ✓ | financiamento_negado (1.00; grupo 1.00) | credito_documentacao/financiamento_negado ✓ | credito_documentacao (0.96) › financiamento_negado (0.98) | credito_documentacao/financiamento_negado ✓ | 0.98 · 0.03 · 0.02 | credito_documentacao/financiamento_negado ✓ |
| MP-A019 | motivo dito com educação | preco/preco_acima_orcamento | — | sem_informacao/adiou_sem_motivo ✗G | preco (1.00) | preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ✓ | preco_acima_orcamento (1.00; grupo 1.00) | preco/preco_acima_orcamento ✓ | preco (1.00) › preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ✓ | 0.52 · 0.03 · 0.02 | preco/preco_acima_orcamento ✓ |
| MP-A020 | fácil / outros | momento_cliente/desistiu_de_mudar | — | momento_cliente/desistiu_de_mudar ✓ | concorrencia (0.61) | direto_proprietario (0.99) | concorrencia/∅ ? | desistiu_de_mudar (0.94; grupo 0.94) | momento_cliente/desistiu_de_mudar ✓ | concorrencia (0.61) › direto_proprietario (0.99) | concorrencia/∅ ? | 0.86 · 0.02 · 0.33 | concorrencia/direto_proprietario ✗G |
| MP-A021 | fronteira entre folhas | preco/custos_extras | — | preco/custos_extras ✓ | preco (1.00) | custos_extras (1.00) | preco/custos_extras ✓ | custos_extras (1.00; grupo 1.00) | preco/custos_extras ✓ | preco (1.00) › custos_extras (1.00) | preco/custos_extras ✓ | 0.98 · 0.03 · 0.03 | preco/custos_extras ✓ |
| MP-A022 | fácil / outros | credito_documentacao/garantia_locaticia | — | credito_documentacao/garantia_locaticia ✓ | credito_documentacao (0.81) | garantia_locaticia (1.00) | credito_documentacao/garantia_locaticia ✓ | garantia_locaticia (1.00; grupo 1.00) | credito_documentacao/garantia_locaticia ✓ | credito_documentacao (0.80) › garantia_locaticia (1.00) | credito_documentacao/garantia_locaticia ✓ | 0.97 · 0.05 · 0.02 | credito_documentacao/garantia_locaticia ✓ |
| MP-A023 | fácil / outros | preco/condicao_pagamento | — | preco/condicao_pagamento ✓ | preco (0.83) | condicao_pagamento (1.00) | preco/condicao_pagamento ✓ | condicao_pagamento (1.00; grupo 1.00) | preco/condicao_pagamento ✓ | preco (0.81) › condicao_pagamento (1.00) | preco/condicao_pagamento ✓ | 0.98 · 0.07 · 0.03 | preco/condicao_pagamento ✓ |
| MP-A024 | só o grupo é decidível | concorrencia/∅ | — | credito_documentacao/restricao_cadastral ✗G | concorrencia (1.00) | only_group (1.00) | concorrencia/∅ ✓G | outra_imobiliaria (0.84; grupo 0.90) | concorrencia/outra_imobiliaria ✗f | concorrencia (1.00) › only_group (1.00) | concorrencia/∅ ✓G | 0.97 · 0.04 · 0.96 | concorrencia/∅ ✓G |
| MP-A025 | fronteira entre folhas | preco/negociacao_frustrada | preco_acima_orcamento | preco/negociacao_frustrada ✓ | preco (1.00) | preco_acima_orcamento (0.93) | preco/preco_acima_orcamento ≈ | preco_acima_orcamento (0.70; grupo 1.00) | preco/preco_acima_orcamento ≈ | preco (1.00) › preco_acima_orcamento (0.94) | preco/preco_acima_orcamento ≈ | 0.97 · 0.04 · 0.02 | preco/preco_acima_orcamento ≈ |
| MP-A026 | fronteira entre folhas | imovel/diferente_do_anuncio | estado_conservacao | imovel/diferente_do_anuncio ✓ | imovel (0.99) | diferente_do_anuncio (0.99) | imovel/diferente_do_anuncio ✓ | diferente_do_anuncio (1.00; grupo 1.00) | imovel/diferente_do_anuncio ✓ | imovel (1.00) › diferente_do_anuncio (0.99) | imovel/diferente_do_anuncio ✓ | 0.98 · 0.69 · 0.02 | imovel/diferente_do_anuncio ✓ |
| MP-A027 | só o grupo é decidível | imovel/∅ | — | sem_informacao/adiou_sem_motivo ✗G | imovel (0.72) | only_group (1.00) | imovel/∅ ✓G | sumiu_sem_resposta (0.29; grupo 0.57) | sem_informacao/∅ ✗G | imovel (0.71) › only_group (1.00) | imovel/∅ ✓G | 0.93 · 0.04 · 0.02 | imovel/∅ ✓G |
| MP-A028 | motivo do corretor | atendimento/informacao_errada | preco_acima_orcamento | preco/custos_extras ✗G | preco (0.65) | preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ≈ | informacao_errada (0.76; grupo 0.76) | atendimento/informacao_errada ✓ | preco (0.69) › preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ≈ | 0.98 · 0.90 · 0.03 | preco/preco_acima_orcamento ≈ |
| MP-A029 | fechou em outro lugar | concorrencia/lancamento_construtora | condicao_pagamento | preco/condicao_pagamento ≈ | concorrencia (0.99) | lancamento_construtora (1.00) | concorrencia/lancamento_construtora ✓ | lancamento_construtora (1.00; grupo 1.00) | concorrencia/lancamento_construtora ✓ | concorrencia (0.99) › lancamento_construtora (1.00) | concorrencia/lancamento_construtora ✓ | 0.94 · 0.03 · 0.95 | concorrencia/lancamento_construtora ✓ |
| MP-A030 | fechou em outro lugar | concorrencia/outra_imobiliaria | — | credito_documentacao/garantia_locaticia ✗G | concorrencia (1.00) | outra_imobiliaria (0.99) | concorrencia/outra_imobiliaria ✓ | outra_imobiliaria (0.96; grupo 0.96) | concorrencia/outra_imobiliaria ✓ | concorrencia (1.00) › outra_imobiliaria (0.98) | concorrencia/outra_imobiliaria ✓ | 0.97 · 0.33 · 0.94 | concorrencia/outra_imobiliaria ✓ |
| MP-A031 | fácil / outros | momento_cliente/mudanca_de_vida | — | momento_cliente/mudanca_de_vida ✓ | momento_cliente (0.90) | mudanca_de_vida (1.00) | momento_cliente/mudanca_de_vida ✓ | mudanca_de_vida (1.00; grupo 1.00) | momento_cliente/mudanca_de_vida ✓ | momento_cliente (0.91) › mudanca_de_vida (1.00) | momento_cliente/mudanca_de_vida ✓ | 0.98 · 0.02 · 0.03 | momento_cliente/mudanca_de_vida ✓ |
| MP-A032 | fácil / outros | atendimento/imovel_indisponivel | — | preco/negociacao_frustrada ✗G | atendimento (0.67) | imovel_indisponivel (0.98) | atendimento/imovel_indisponivel ✓ | imovel_indisponivel (0.99; grupo 1.00) | atendimento/imovel_indisponivel ✓ | atendimento (0.64) › imovel_indisponivel (0.97) | atendimento/imovel_indisponivel ✓ | 0.81 · 0.60 · 0.03 | atendimento/imovel_indisponivel ✓ |
| MP-A033 | motivo do corretor | atendimento/demora_resposta | outra_imobiliaria | preco/preco_acima_orcamento ✗G | concorrencia (0.52) | outra_imobiliaria (1.00) | concorrencia/outra_imobiliaria ≈ | demora_resposta (0.86; grupo 0.86) | atendimento/demora_resposta ✓ | atendimento (0.58) › demora_resposta (1.00) | atendimento/demora_resposta ✓ | 0.98 · 0.93 · 0.95 | atendimento/demora_resposta ✓ |
| MP-A034 | fácil / outros | localizacao/bairro_nao_desejado | — | preco/preco_acima_orcamento ✗G | localizacao (0.55) | bairro_nao_desejado (0.94) | localizacao/bairro_nao_desejado ✓ | bairro_nao_desejado (0.76; grupo 0.77) | localizacao/bairro_nao_desejado ✓ | localizacao (0.56) › bairro_nao_desejado (0.94) | localizacao/bairro_nao_desejado ✓ | 0.95 · 0.08 · 0.03 | localizacao/bairro_nao_desejado ✓ |

## Conjunto `teste` — 68 conversas (arquivo versão 2026-10-01, autor fable); 41 difíceis, 7 com `folha: null`, 8 `sem_informacao`, 0 em revisão por falha operacional, entrada inválida ou teto; taxonomia de 8 grupos e 30 folhas

### Desfecho — baseline de código × variantes com Jev, nas mesmas conversas

`estrito` = a folha principal do gabarito (ou só o grupo certo quando `folha` é null). `folgado` = folha ∈ `aceitaveis` (ou só o grupo certo quando `folha` é null). `grupo certo` = grupo = gabarito ou folha aceitável. **Motivo INVENTADO** (erro caro) = gabarito `sem_informacao` e saiu outro grupo, automatizado (denominador = casos `sem_informacao`). **Grupo errado automatizado** (erro caro) = grupo ≠ gabarito sem revisão, inclui os inventados. `só-grupo certo` = nos casos `folha: null`, saiu só o grupo certo. `absteve` = havia folha, saiu só o grupo certo (nem acerto nem erro). Revisão e falha contam como erro em todas as taxas de acerto. Custo e latência: só as requisições que a variante envia em produção, medidas. Variante principal (a que o critério julga): **c · uma requisição (grupo + folhas por grupo)**.

| variante | n | acerto estrito | acerto folgado | grupo certo | motivo INVENTADO | grupo errado auto. | só-grupo certo | sem_info certo | absteve | folha errada | revisar | falha | req/caso | tokens/caso | US$/1000 | p50_ms | p95_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| código: palavra-chave por folha | 68 | 0.250 | 0.279 | 0.397 | 7/8 | 41/68 | 0/7 | 1/8 | 0/61 | 8/68 | 0/68 | 0/68 | 0 | 0 | 0 | 0 | 0 |
| a · duas etapas (grupo → folhas do grupo) | 68 | 0.824 | 0.868 | 0.882 | 0/8 | 3/68 | 5/7 | 7/8 | 0/61 | 1/68 | 5/68 | 0/68 | 2.00 | 2572 | 0.1080 | 561 | 676 |
| b · Choice única sobre as 30 folhas | 68 | 0.824 | 0.868 | 0.926 | 0/8 | 1/68 | 0/7 | 8/8 | 1/61 | 3/68 | 4/68 | 0/68 | 1.00 | 2584 | 0.1085 | 270 | 323 |
| c · uma requisição (grupo + folhas por grupo) | 68 | 0.809 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 7/8 | 0/61 | 1/68 | 5/68 | 0/68 | 1.00 | 6067 | 0.2548 | 286 | 338 |
| c sem as guardas (informativa) | 68 | 0.838 | 0.882 | 0.897 | 0/8 | 6/68 | 6/7 | 7/8 | 0/61 | 1/68 | 1/68 | 0/68 | 1.00 | 6067 | 0.2548 | 286 | 338 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 motivo INVENTADO (gabarito `sem_informacao`, saiu outro grupo, automatizado) | 0/8 | ≤ 1 | ✓ |
| 2 grupo errado automatizado (inclui os inventados) | 4/68 (0.059) | ≤ 0.09 | ✓ |
| 3 acerto folgado (revisão e falha = erro) | 0.853 | ≥ 0.70 | ✓ |
| 4 grupo certo (revisão e falha = erro) | 0.868 | ≥ 0.80 | ✓ |
| 5 revisão (inclui falha) | 5/68 (0.074) | ≤ 0.20 | ✓ |
| 6 contra o baseline de palavras-chave | 0.853 × 0.279 | > | ✓ |

### Por família difícil (pela `nota` do rotulador) — acertos folgados; erros caros e revisões da principal

| família | n | `null` | base | a | b | c | c-sg | inventado (principal) | grupo errado (principal) | revisar (principal) |
|---|---|---|---|---|---|---|---|---|---|---|
| sumiço depois de preço | 3 | 0 | 1 | 2 | 3 | 2 | 2 | 0 | 0 | 0 |
| fronteira entre folhas | 7 | 0 | 4 | 5 | 6 | 5 | 6 | 0 | 1 | 1 |
| fechou em outro lugar | 5 | 0 | 1 | 5 | 5 | 5 | 5 | 0 | 0 | 0 |
| motivo do corretor | 6 | 0 | 0 | 4 | 5 | 4 | 4 | 0 | 0 | 2 |
| motivo real diferente do declarado | 3 | 0 | 1 | 3 | 3 | 3 | 3 | 0 | 0 | 0 |
| dois motivos | 4 | 0 | 0 | 4 | 4 | 4 | 4 | 0 | 0 | 0 |
| só o grupo é decidível | 7 | 7 | 1 | 6 | 2 | 6 | 7 | 0 | 0 | 1 |
| sumiço sem pista | 2 | 0 | 0 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |
| motivo dito com educação | 3 | 0 | 0 | 3 | 3 | 3 | 3 | 0 | 0 | 0 |
| decisor com motivo | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| fácil / outros | 27 | 0 | 11 | 24 | 25 | 23 | 23 | 0 | 3 | 1 |

### As guardas na principal (`c`) — o que cada Noul mudou

| guarda | disparou | tirou um erro | tirou um acerto | casos |
|---|---|---|---|---|
| `blames_agency` (grupo atendimento) | 2 | 0 | 2 | MP-T024(✓G→?) MP-T055(✓→?) |
| `closed_elsewhere` (grupo concorrencia) | 2 | 2 | 0 | MP-T007(✗G→?) MP-T028(✗G→?) |
| `reason_stated` (grupo ≠ sem_informacao) | 0 | 0 | 0 | — |

### Os sinais — quem aponta o grupo e a folha certos, sem limiar nenhum

| quem aponta o grupo | grupo certo |
|---|---|
| Choice `group` (requisição `grupo`) | 62/68 |
| soma das folhas por grupo (Choice única) | 66/68 |
| Choice `group` (requisição `tudo`) | 61/68 |

| quem aponta a folha | a principal | alguma aceitável | `only_group` |
|---|---|---|---|
| Choice das folhas do grupo vencedor (`folhas`) | 53/61 | 55/61 | 1/61 |
| Choice única (vencedora) | 58/61 | 59/61 | 0/61 |
| Choice `leaf.<grupo vencedor>` (`tudo`) | 52/61 | 54/61 | 1/61 |

Nos 7 casos `folha: null`: `only_group` saiu em `folhas` 6, em `tudo` 6; p da folha vencedora na Choice única: 0.94, 0.69, 0.53, 0.52, 0.84, 0.22, 0.86.

p(grupo vencedor) na Choice `group` (`grupo`): quando certo (n = 62) mínimo 0.42, p10 0.80, mediana 0.98; quando errado (n = 6) mínimo 0.64, mediana 0.71, máximo 0.99. 
p(folha vencedora) em `folhas`: certa mínimo 0.65, p10 0.90, mediana 1.00; errada (fora de aceitáveis) 0.56, 0.90, 0.98, 1.00, 1.00. Na Choice única: certa mínimo 0.41, p10 0.69, mediana 0.99; errada 0.43, 0.76.

A MESMA Choice `group` em duas requisições (`grupo` × `tudo`, isolamento ≠ determinismo) trocou de vencedor em 1/68: MP-T017 preco→credito_documentacao.

Noul `reason_stated` (requisição `grupo`): onde o gabarito pede sim (n = 60) mínimo 0.52, p10 0.88, mediana 0.96; onde pede não (n = 8) mediana 0.10, p90 0.24, máximo 0.24.

Noul `blames_agency` (requisição `grupo`): onde o gabarito pede sim (n = 11) mínimo 0.13, p10 0.20, mediana 0.65; onde pede não (n = 57) mediana 0.04, p90 0.09, máximo 0.75.

Noul `closed_elsewhere` (requisição `grupo`): onde o gabarito pede sim (n = 7) mínimo 0.62, p10 0.62, mediana 0.95; onde pede não (n = 61) mediana 0.03, p90 0.05, máximo 0.97.

O mesmo Noul em requisições diferentes: `grupo` × `unica` diferença absoluta média 0.005, máxima 0.050; `grupo` × `tudo` média 0.004, máxima 0.090 (n = 204).

### Cobertura × erro por limiar (um limiar por vez; os outros como em `perguntas.py`)

**c · uma requisição (grupo + folhas por grupo)** — limiar `grupo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 64/68 | 0.868 | 0.882 | 0/8 | 4/68 | 5/7 | 0 | 1 | 4 |
| 0.200 | 64/68 | 0.868 | 0.882 | 0/8 | 4/68 | 5/7 | 0 | 1 | 4 |
| 0.300 | 64/68 | 0.868 | 0.882 | 0/8 | 4/68 | 5/7 | 0 | 1 | 4 |
| 0.400 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.500 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.600 | 61/68 | 0.838 | 0.853 | 0/8 | 3/68 | 5/7 | 0 | 1 | 7 |
| 0.700 | 57/68 | 0.809 | 0.824 | 0/8 | 1/68 | 5/7 | 0 | 1 | 11 |
| 0.800 | 55/68 | 0.779 | 0.794 | 0/8 | 1/68 | 5/7 | 0 | 1 | 13 |
| 0.900 | 46/68 | 0.662 | 0.676 | 0/8 | 0/68 | 3/7 | 0 | 1 | 22 |

**c · uma requisição (grupo + folhas por grupo)** — limiar `folha` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.200 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.300 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.400 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.500 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.600 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 1 | 0 | 5 |
| 0.700 | 63/68 | 0.809 | 0.868 | 0/8 | 4/68 | 5/7 | 4 | 0 | 5 |
| 0.800 | 63/68 | 0.809 | 0.868 | 0/8 | 4/68 | 5/7 | 4 | 0 | 5 |
| 0.900 | 63/68 | 0.779 | 0.868 | 0/8 | 4/68 | 6/7 | 6 | 0 | 5 |

**c · uma requisição (grupo + folhas por grupo)** — limiar `guarda` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 67/68 | 0.882 | 0.897 | 0/8 | 6/68 | 6/7 | 0 | 1 | 1 |
| 0.200 | 64/68 | 0.853 | 0.868 | 0/8 | 5/68 | 5/7 | 0 | 1 | 4 |
| 0.300 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.400 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.500 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.600 | 61/68 | 0.824 | 0.838 | 0/8 | 4/68 | 5/7 | 0 | 1 | 7 |
| 0.700 | 60/68 | 0.809 | 0.824 | 0/8 | 4/68 | 5/7 | 0 | 1 | 8 |
| 0.800 | 57/68 | 0.779 | 0.794 | 0/8 | 3/68 | 5/7 | 0 | 1 | 11 |
| 0.900 | 55/68 | 0.750 | 0.765 | 0/8 | 3/68 | 5/7 | 0 | 1 | 13 |

**c · uma requisição (grupo + folhas por grupo)** — limiar `sem_motivo` (em uso: 0.4)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.200 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.300 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.400 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.500 | 63/68 | 0.853 | 0.868 | 0/8 | 4/68 | 5/7 | 0 | 1 | 5 |
| 0.600 | 62/68 | 0.838 | 0.853 | 0/8 | 4/68 | 5/7 | 0 | 1 | 6 |
| 0.700 | 62/68 | 0.838 | 0.853 | 0/8 | 4/68 | 5/7 | 0 | 1 | 6 |
| 0.800 | 61/68 | 0.824 | 0.838 | 0/8 | 4/68 | 5/7 | 0 | 1 | 7 |
| 0.900 | 58/68 | 0.779 | 0.794 | 0/8 | 4/68 | 3/7 | 0 | 1 | 10 |

**a · duas etapas (grupo → folhas do grupo)** — limiar `grupo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 64/68 | 0.882 | 0.897 | 0/8 | 3/68 | 5/7 | 0 | 1 | 4 |
| 0.200 | 64/68 | 0.882 | 0.897 | 0/8 | 3/68 | 5/7 | 0 | 1 | 4 |
| 0.300 | 64/68 | 0.882 | 0.897 | 0/8 | 3/68 | 5/7 | 0 | 1 | 4 |
| 0.400 | 64/68 | 0.882 | 0.897 | 0/8 | 3/68 | 5/7 | 0 | 1 | 4 |
| 0.500 | 63/68 | 0.868 | 0.882 | 0/8 | 3/68 | 5/7 | 0 | 1 | 5 |
| 0.600 | 61/68 | 0.838 | 0.853 | 0/8 | 3/68 | 5/7 | 0 | 1 | 7 |
| 0.700 | 57/68 | 0.809 | 0.824 | 0/8 | 1/68 | 5/7 | 0 | 1 | 11 |
| 0.800 | 54/68 | 0.779 | 0.794 | 0/8 | 0/68 | 5/7 | 0 | 1 | 14 |
| 0.900 | 44/68 | 0.632 | 0.647 | 0/8 | 0/68 | 3/7 | 0 | 1 | 24 |

**a · duas etapas (grupo → folhas do grupo)** — limiar `folha` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 63/68 | 0.868 | 0.882 | 0/8 | 3/68 | 5/7 | 0 | 1 | 5 |
| 0.200 | 63/68 | 0.868 | 0.882 | 0/8 | 3/68 | 5/7 | 0 | 1 | 5 |
| 0.300 | 63/68 | 0.868 | 0.882 | 0/8 | 3/68 | 5/7 | 0 | 1 | 5 |
| 0.400 | 63/68 | 0.868 | 0.882 | 0/8 | 3/68 | 5/7 | 0 | 1 | 5 |
| 0.500 | 63/68 | 0.868 | 0.882 | 0/8 | 3/68 | 5/7 | 0 | 1 | 5 |
| 0.600 | 63/68 | 0.868 | 0.882 | 0/8 | 3/68 | 5/7 | 1 | 0 | 5 |
| 0.700 | 63/68 | 0.838 | 0.882 | 0/8 | 3/68 | 5/7 | 3 | 0 | 5 |
| 0.800 | 63/68 | 0.809 | 0.882 | 0/8 | 3/68 | 5/7 | 5 | 0 | 5 |
| 0.900 | 63/68 | 0.794 | 0.882 | 0/8 | 3/68 | 6/7 | 6 | 0 | 5 |

**b · Choice única sobre as 30 folhas** — limiar `grupo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 65/68 | 0.882 | 0.941 | 0/8 | 1/68 | 1/7 | 1 | 3 | 3 |
| 0.200 | 65/68 | 0.882 | 0.941 | 0/8 | 1/68 | 1/7 | 1 | 3 | 3 |
| 0.300 | 65/68 | 0.882 | 0.941 | 0/8 | 1/68 | 1/7 | 1 | 3 | 3 |
| 0.400 | 65/68 | 0.882 | 0.941 | 0/8 | 1/68 | 1/7 | 1 | 3 | 3 |
| 0.500 | 64/68 | 0.868 | 0.926 | 0/8 | 1/68 | 0/7 | 1 | 3 | 4 |
| 0.600 | 63/68 | 0.853 | 0.912 | 0/8 | 1/68 | 0/7 | 1 | 3 | 5 |
| 0.700 | 61/68 | 0.824 | 0.882 | 0/8 | 1/68 | 0/7 | 1 | 3 | 7 |
| 0.800 | 59/68 | 0.809 | 0.868 | 0/8 | 0/68 | 0/7 | 1 | 3 | 9 |
| 0.900 | 53/68 | 0.765 | 0.779 | 0/8 | 0/68 | 0/7 | 0 | 1 | 15 |

**b · Choice única sobre as 30 folhas** — limiar `folha_unica` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 64/68 | 0.882 | 0.926 | 0/8 | 1/68 | 0/7 | 0 | 3 | 4 |
| 0.200 | 64/68 | 0.882 | 0.926 | 0/8 | 1/68 | 0/7 | 0 | 3 | 4 |
| 0.300 | 64/68 | 0.882 | 0.926 | 0/8 | 1/68 | 0/7 | 0 | 3 | 4 |
| 0.400 | 64/68 | 0.882 | 0.926 | 0/8 | 1/68 | 0/7 | 0 | 3 | 4 |
| 0.500 | 64/68 | 0.868 | 0.926 | 0/8 | 1/68 | 0/7 | 1 | 3 | 4 |
| 0.600 | 64/68 | 0.824 | 0.926 | 0/8 | 1/68 | 1/7 | 4 | 3 | 4 |
| 0.700 | 64/68 | 0.779 | 0.926 | 0/8 | 1/68 | 2/7 | 8 | 2 | 4 |
| 0.800 | 64/68 | 0.750 | 0.926 | 0/8 | 1/68 | 2/7 | 10 | 2 | 4 |
| 0.900 | 64/68 | 0.735 | 0.926 | 0/8 | 1/68 | 4/7 | 13 | 0 | 4 |

### Custo e latência por formato de requisição (medidos)

| requisição | enviadas | novas (não cache) | tokens por requisição | p50_ms | p95_ms | quem usa |
|---|---|---|---|---|---|---|
| grupo | 68 | 0 | 1541 | 299 | 365 | a |
| folhas | 68 | 0 | 1031 | 260 | 298 | a |
| unica | 68 | 0 | 2584 | 270 | 323 | b |
| tudo | 68 | 0 | 6067 | 286 | 338 | c |

Tudo o que esta execução usou: 272 requisições (0 novas), 763081 tokens, US$ 0.0320 · modelo: jev-1.13.0. Latência = a da chamada original de cada requisição (o cache a guarda), medida com 8 conversas em paralelo.

### Caso a caso

Marca: ✓ a folha principal · ≈ aceitável · ✓G só grupo, certo · ∅G absteve da folha (grupo certo) · ✗f folha errada (grupo certo) · ✗G grupo errado · ✗I motivo INVENTADO · ? revisar · ✗F falha. Célula = `grupo/folha marca`; `∅` = sem folha. `grupo` = Choice `group` com p(vencedor); `nouls` = reason_stated · blames_agency · closed_elsewhere (requisição `grupo`).

| id | fam | gabarito | outras aceitáveis | base | grupo | folhas | a | única | b | tudo | c | nouls | c-sg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MP-T001 | sumiço depois de preço | preco/preco_acima_orcamento | sumiu_apos_valor | preco/preco_acima_orcamento ✓ | preco (0.58) | preco_acima_orcamento (0.65) | preco/preco_acima_orcamento ✓ | preco_acima_orcamento (0.84; grupo 0.85) | preco/preco_acima_orcamento ✓ | preco (0.59) › preco_acima_orcamento (0.68) | preco/preco_acima_orcamento ✓ | 0.52 · 0.06 · 0.02 | preco/preco_acima_orcamento ✓ |
| MP-T002 | fácil / outros | localizacao/bairro_nao_desejado | — | imovel/falta_item ✗G | localizacao (0.67) | bairro_nao_desejado (0.93) | localizacao/bairro_nao_desejado ✓ | bairro_nao_desejado (0.63; grupo 0.67) | localizacao/bairro_nao_desejado ✓ | localizacao (0.62) › bairro_nao_desejado (0.92) | localizacao/bairro_nao_desejado ✓ | 0.95 · 0.07 · 0.03 | localizacao/bairro_nao_desejado ✓ |
| MP-T003 | fronteira entre folhas | imovel/estado_conservacao | — | imovel/estado_conservacao ✓ | imovel (0.91) | estado_conservacao (1.00) | imovel/estado_conservacao ✓ | estado_conservacao (0.94; grupo 0.94) | imovel/estado_conservacao ✓ | imovel (0.92) › estado_conservacao (1.00) | imovel/estado_conservacao ✓ | 0.98 · 0.04 · 0.03 | imovel/estado_conservacao ✓ |
| MP-T004 | fechou em outro lugar | concorrencia/outra_imobiliaria | — | imovel/estado_conservacao ✗G | concorrencia (1.00) | outra_imobiliaria (1.00) | concorrencia/outra_imobiliaria ✓ | outra_imobiliaria (1.00; grupo 1.00) | concorrencia/outra_imobiliaria ✓ | concorrencia (1.00) › outra_imobiliaria (1.00) | concorrencia/outra_imobiliaria ✓ | 0.96 · 0.03 · 0.95 | concorrencia/outra_imobiliaria ✓ |
| MP-T005 | fácil / outros | credito_documentacao/restricao_cadastral | — | sem_informacao/adiou_sem_motivo ✗G | credito_documentacao (0.99) | restricao_cadastral (0.97) | credito_documentacao/restricao_cadastral ✓ | restricao_cadastral (0.82; grupo 0.98) | credito_documentacao/restricao_cadastral ✓ | credito_documentacao (0.99) › restricao_cadastral (0.96) | credito_documentacao/restricao_cadastral ✓ | 0.96 · 0.09 · 0.02 | credito_documentacao/restricao_cadastral ✓ |
| MP-T006 | fácil / outros | sem_informacao/sumiu_sem_resposta | — | preco/preco_acima_orcamento ✗I | sem_informacao (0.99) | sumiu_sem_resposta (1.00) | sem_informacao/sumiu_sem_resposta ✓ | sumiu_sem_resposta (0.99; grupo 0.99) | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao (0.99) › sumiu_sem_resposta (1.00) | sem_informacao/sumiu_sem_resposta ✓ | 0.06 · 0.06 · 0.01 | sem_informacao/sumiu_sem_resposta ✓ |
| MP-T007 | motivo do corretor | atendimento/demora_resposta | — | imovel/diferente_do_anuncio ✗G | concorrencia (0.71) | outra_imobiliaria (0.90) | concorrencia/∅ ? | demora_resposta (0.50; grupo 0.50) | atendimento/demora_resposta ✓ | concorrencia (0.61) › outra_imobiliaria (0.89) | concorrencia/∅ ? | 0.87 · 0.83 · 0.13 | concorrencia/outra_imobiliaria ✗G |
| MP-T008 | motivo do corretor | atendimento/imovel_indisponivel | — | credito_documentacao/financiamento_negado ✗G | atendimento (0.95) | imovel_indisponivel (0.96) | atendimento/imovel_indisponivel ✓ | imovel_indisponivel (0.99; grupo 1.00) | atendimento/imovel_indisponivel ✓ | atendimento (0.93) › imovel_indisponivel (0.96) | atendimento/imovel_indisponivel ✓ | 0.95 · 0.78 · 0.03 | atendimento/imovel_indisponivel ✓ |
| MP-T009 | fácil / outros | momento_cliente/desistiu_de_mudar | — | preco/preco_acima_orcamento ✗G | momento_cliente (0.85) | desistiu_de_mudar (1.00) | momento_cliente/desistiu_de_mudar ✓ | desistiu_de_mudar (1.00; grupo 1.00) | momento_cliente/desistiu_de_mudar ✓ | momento_cliente (0.86) › desistiu_de_mudar (1.00) | momento_cliente/desistiu_de_mudar ✓ | 0.96 · 0.02 · 0.02 | momento_cliente/desistiu_de_mudar ✓ |
| MP-T010 | motivo real diferente do declarado | localizacao/distancia_deslocamento | bairro_nao_desejado | imovel/tamanho_planta ✗G | localizacao (0.99) | distancia_deslocamento (0.98) | localizacao/distancia_deslocamento ✓ | distancia_deslocamento (0.86; grupo 0.97) | localizacao/distancia_deslocamento ✓ | localizacao (0.99) › distancia_deslocamento (0.97) | localizacao/distancia_deslocamento ✓ | 0.98 · 0.03 · 0.05 | localizacao/distancia_deslocamento ✓ |
| MP-T011 | dois motivos | localizacao/distancia_deslocamento | — | preco/preco_acima_orcamento ✗G | localizacao (0.99) | distancia_deslocamento (1.00) | localizacao/distancia_deslocamento ✓ | distancia_deslocamento (0.98; grupo 0.98) | localizacao/distancia_deslocamento ✓ | localizacao (1.00) › distancia_deslocamento (1.00) | localizacao/distancia_deslocamento ✓ | 0.95 · 0.06 · 0.04 | localizacao/distancia_deslocamento ✓ |
| MP-T012 | motivo do corretor | atendimento/informacao_errada | falta_item | preco/custos_extras ✗G | atendimento (0.88) | informacao_errada (1.00) | atendimento/informacao_errada ✓ | informacao_errada (0.93; grupo 0.93) | atendimento/informacao_errada ✓ | atendimento (0.90) › informacao_errada (1.00) | atendimento/informacao_errada ✓ | 0.98 · 0.85 · 0.03 | atendimento/informacao_errada ✓ |
| MP-T013 | fechou em outro lugar | concorrencia/direto_proprietario | — | preco/negociacao_frustrada ✗G | concorrencia (0.99) | direto_proprietario (1.00) | concorrencia/direto_proprietario ✓ | direto_proprietario (1.00; grupo 1.00) | concorrencia/direto_proprietario ✓ | concorrencia (0.99) › direto_proprietario (1.00) | concorrencia/direto_proprietario ✓ | 0.96 · 0.07 · 0.62 | concorrencia/direto_proprietario ✓ |
| MP-T014 | só o grupo é decidível | preco/∅ | preco_acima_orcamento custos_extras | preco/preco_acima_orcamento ≈ | preco (1.00) | preco_acima_orcamento (0.89) | preco/preco_acima_orcamento ≈ | preco_acima_orcamento (0.94; grupo 1.00) | preco/preco_acima_orcamento ≈ | preco (1.00) › preco_acima_orcamento (0.86) | preco/preco_acima_orcamento ≈ | 0.98 · 0.03 · 0.03 | preco/preco_acima_orcamento ≈ |
| MP-T015 | fácil / outros | momento_cliente/desistiu_de_mudar | — | momento_cliente/desistiu_de_mudar ✓ | momento_cliente (0.92) | desistiu_de_mudar (0.98) | momento_cliente/desistiu_de_mudar ✓ | desistiu_de_mudar (0.97; grupo 0.99) | momento_cliente/desistiu_de_mudar ✓ | momento_cliente (0.92) › desistiu_de_mudar (0.98) | momento_cliente/desistiu_de_mudar ✓ | 0.97 · 0.03 · 0.05 | momento_cliente/desistiu_de_mudar ✓ |
| MP-T016 | sumiço sem pista | sem_informacao/sumiu_sem_resposta | — | imovel/diferente_do_anuncio ✗I | sem_informacao (1.00) | sumiu_sem_resposta (1.00) | sem_informacao/sumiu_sem_resposta ✓ | sumiu_sem_resposta (1.00; grupo 1.00) | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao (1.00) › sumiu_sem_resposta (1.00) | sem_informacao/sumiu_sem_resposta ✓ | 0.06 · 0.07 · 0.02 | sem_informacao/sumiu_sem_resposta ✓ |
| MP-T017 | fácil / outros | preco/condicao_pagamento | — | preco/condicao_pagamento ✓ | preco (0.54) | condicao_pagamento (1.00) | preco/condicao_pagamento ✓ | condicao_pagamento (1.00; grupo 1.00) | preco/condicao_pagamento ✓ | credito_documentacao (0.55) › financiamento_negado (0.60) | credito_documentacao/financiamento_negado ✗G | 0.96 · 0.16 · 0.03 | credito_documentacao/financiamento_negado ✗G |
| MP-T018 | sumiço sem pista | sem_informacao/sumiu_sem_resposta | — | imovel/estado_conservacao ✗I | sem_informacao (0.97) | sumiu_sem_resposta (0.98) | sem_informacao/sumiu_sem_resposta ✓ | sumiu_sem_resposta (0.99; grupo 1.00) | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao (0.98) › sumiu_sem_resposta (0.98) | sem_informacao/sumiu_sem_resposta ✓ | 0.11 · 0.05 · 0.01 | sem_informacao/sumiu_sem_resposta ✓ |
| MP-T019 | motivo dito com educação | sem_informacao/adiou_sem_motivo | sumiu_sem_resposta | imovel/diferente_do_anuncio ✗I | sem_informacao (1.00) | adiou_sem_motivo (0.86) | sem_informacao/adiou_sem_motivo ✓ | adiou_sem_motivo (0.58; grupo 1.00) | sem_informacao/adiou_sem_motivo ✓ | sem_informacao (1.00) › adiou_sem_motivo (0.86) | sem_informacao/adiou_sem_motivo ✓ | 0.10 · 0.02 · 0.02 | sem_informacao/adiou_sem_motivo ✓ |
| MP-T020 | fácil / outros | sem_informacao/adiou_sem_motivo | — | sem_informacao/adiou_sem_motivo ✓ | sem_informacao (0.99) | adiou_sem_motivo (1.00) | sem_informacao/adiou_sem_motivo ✓ | adiou_sem_motivo (0.99; grupo 1.00) | sem_informacao/adiou_sem_motivo ✓ | sem_informacao (0.99) › adiou_sem_motivo (1.00) | sem_informacao/adiou_sem_motivo ✓ | 0.12 · 0.03 · 0.02 | sem_informacao/adiou_sem_motivo ✓ |
| MP-T021 | fronteira entre folhas | credito_documentacao/documentacao_imovel | — | credito_documentacao/financiamento_negado ✗f | credito_documentacao (0.86) | documentacao_imovel (0.97) | credito_documentacao/documentacao_imovel ✓ | documentacao_imovel (0.75; grupo 0.82) | credito_documentacao/documentacao_imovel ✓ | credito_documentacao (0.83) › documentacao_imovel (0.98) | credito_documentacao/documentacao_imovel ✓ | 0.85 · 0.13 · 0.04 | credito_documentacao/documentacao_imovel ✓ |
| MP-T022 | só o grupo é decidível | localizacao/∅ | — | atendimento/demora_resposta ✗G | localizacao (0.97) | only_group (0.97) | localizacao/∅ ✓G | bairro_nao_desejado (0.69; grupo 0.88) | localizacao/bairro_nao_desejado ✗f | localizacao (0.97) › only_group (0.97) | localizacao/∅ ✓G | 0.88 · 0.03 · 0.03 | localizacao/∅ ✓G |
| MP-T023 | motivo do corretor | atendimento/demora_resposta | outra_imobiliaria | imovel/falta_item ✗G | atendimento (0.85) | demora_resposta (1.00) | atendimento/demora_resposta ✓ | demora_resposta (0.98; grupo 0.98) | atendimento/demora_resposta ✓ | atendimento (0.90) › demora_resposta (1.00) | atendimento/demora_resposta ✓ | 0.98 · 0.94 · 0.95 | atendimento/demora_resposta ✓ |
| MP-T024 | só o grupo é decidível | atendimento/∅ | — | preco/condicao_pagamento ✗G | atendimento (0.98) | only_group (0.97) | atendimento/∅ ? | pressao_insistencia (0.53; grupo 0.80) | atendimento/∅ ? | atendimento (0.98) › only_group (0.97) | atendimento/∅ ? | 0.95 · 0.20 · 0.02 | atendimento/∅ ✓G |
| MP-T025 | fácil / outros | imovel/tamanho_planta | — | imovel/diferente_do_anuncio ✗f | imovel (0.99) | tamanho_planta (0.97) | imovel/tamanho_planta ✓ | tamanho_planta (0.96; grupo 0.99) | imovel/tamanho_planta ✓ | imovel (0.99) › tamanho_planta (0.98) | imovel/tamanho_planta ✓ | 0.97 · 0.06 · 0.03 | imovel/tamanho_planta ✓ |
| MP-T026 | fronteira entre folhas | credito_documentacao/garantia_locaticia | — | preco/preco_acima_orcamento ✗G | credito_documentacao (0.99) | garantia_locaticia (1.00) | credito_documentacao/garantia_locaticia ✓ | garantia_locaticia (1.00; grupo 1.00) | credito_documentacao/garantia_locaticia ✓ | credito_documentacao (0.98) › garantia_locaticia (1.00) | credito_documentacao/garantia_locaticia ✓ | 0.95 · 0.05 · 0.02 | credito_documentacao/garantia_locaticia ✓ |
| MP-T027 | fácil / outros | localizacao/entorno_seguranca | — | imovel/estado_conservacao ✗G | localizacao (1.00) | entorno_seguranca (1.00) | localizacao/entorno_seguranca ✓ | entorno_seguranca (1.00; grupo 1.00) | localizacao/entorno_seguranca ✓ | localizacao (1.00) › entorno_seguranca (1.00) | localizacao/entorno_seguranca ✓ | 0.96 · 0.03 · 0.02 | localizacao/entorno_seguranca ✓ |
| MP-T028 | motivo do corretor | atendimento/demora_resposta | — | credito_documentacao/financiamento_negado ✗G | concorrencia (0.99) | only_group (0.74) | concorrencia/∅ ? | outra_imobiliaria (0.43; grupo 0.62) | concorrencia/∅ ? | concorrencia (0.99) › only_group (0.75) | concorrencia/∅ ? | 0.97 · 0.48 · 0.27 | concorrencia/∅ ✗G |
| MP-T029 | fácil / outros | atendimento/visita_falhou | — | atendimento/visita_falhou ✓ | atendimento (1.00) | visita_falhou (1.00) | atendimento/visita_falhou ✓ | visita_falhou (1.00; grupo 1.00) | atendimento/visita_falhou ✓ | atendimento (0.99) › visita_falhou (1.00) | atendimento/visita_falhou ✓ | 0.97 · 0.58 · 0.03 | atendimento/visita_falhou ✓ |
| MP-T030 | fácil / outros | imovel/tamanho_planta | — | imovel/tamanho_planta ✓ | imovel (1.00) | tamanho_planta (1.00) | imovel/tamanho_planta ✓ | tamanho_planta (1.00; grupo 1.00) | imovel/tamanho_planta ✓ | imovel (1.00) › tamanho_planta (1.00) | imovel/tamanho_planta ✓ | 0.98 · 0.05 · 0.03 | imovel/tamanho_planta ✓ |
| MP-T031 | dois motivos | imovel/falta_item | — | imovel/estado_conservacao ✗f | imovel (0.85) | falta_item (1.00) | imovel/falta_item ✓ | falta_item (0.99; grupo 0.99) | imovel/falta_item ✓ | imovel (0.83) › falta_item (1.00) | imovel/falta_item ✓ | 0.98 · 0.02 · 0.03 | imovel/falta_item ✓ |
| MP-T032 | fácil / outros | credito_documentacao/garantia_locaticia | — | credito_documentacao/garantia_locaticia ✓ | credito_documentacao (0.92) | garantia_locaticia (1.00) | credito_documentacao/garantia_locaticia ✓ | garantia_locaticia (0.99; grupo 0.99) | credito_documentacao/garantia_locaticia ✓ | credito_documentacao (0.93) › garantia_locaticia (1.00) | credito_documentacao/garantia_locaticia ✓ | 0.95 · 0.03 · 0.04 | credito_documentacao/garantia_locaticia ✓ |
| MP-T033 | fronteira entre folhas | preco/custos_extras | — | preco/custos_extras ✓ | preco (1.00) | custos_extras (1.00) | preco/custos_extras ✓ | custos_extras (1.00; grupo 1.00) | preco/custos_extras ✓ | preco (1.00) › custos_extras (1.00) | preco/custos_extras ✓ | 0.92 · 0.04 · 0.03 | preco/custos_extras ✓ |
| MP-T034 | fácil / outros | preco/custos_extras | — | preco/preco_acima_orcamento ✗f | preco (0.99) | custos_extras (1.00) | preco/custos_extras ✓ | custos_extras (0.99; grupo 1.00) | preco/custos_extras ✓ | preco (0.99) › custos_extras (1.00) | preco/custos_extras ✓ | 0.98 · 0.03 · 0.02 | preco/custos_extras ✓ |
| MP-T035 | fácil / outros | localizacao/distancia_deslocamento | — | localizacao/distancia_deslocamento ✓ | localizacao (1.00) | distancia_deslocamento (1.00) | localizacao/distancia_deslocamento ✓ | distancia_deslocamento (1.00; grupo 1.00) | localizacao/distancia_deslocamento ✓ | localizacao (1.00) › distancia_deslocamento (1.00) | localizacao/distancia_deslocamento ✓ | 0.91 · 0.02 · 0.02 | localizacao/distancia_deslocamento ✓ |
| MP-T036 | motivo real diferente do declarado | credito_documentacao/financiamento_negado | preco_acima_orcamento | credito_documentacao/financiamento_negado ✓ | credito_documentacao (0.91) | financiamento_negado (1.00) | credito_documentacao/financiamento_negado ✓ | financiamento_negado (0.99; grupo 0.99) | credito_documentacao/financiamento_negado ✓ | credito_documentacao (0.90) › financiamento_negado (1.00) | credito_documentacao/financiamento_negado ✓ | 0.98 · 0.03 · 0.04 | credito_documentacao/financiamento_negado ✓ |
| MP-T037 | decisor com motivo | imovel/falta_item | tamanho_planta | credito_documentacao/documentacao_imovel ✗G | imovel (0.73) | falta_item (1.00) | imovel/falta_item ✓ | falta_item (0.96; grupo 0.96) | imovel/falta_item ✓ | imovel (0.74) › falta_item (1.00) | imovel/falta_item ✓ | 0.97 · 0.04 · 0.03 | imovel/falta_item ✓ |
| MP-T038 | só o grupo é decidível | credito_documentacao/∅ | restricao_cadastral garantia_locaticia | sem_informacao/sumiu_apos_valor ✗G | credito_documentacao (0.85) | only_group (0.84) | credito_documentacao/∅ ✓G | restricao_cadastral (0.52; grupo 0.68) | credito_documentacao/restricao_cadastral ≈ | credito_documentacao (0.84) › only_group (0.87) | credito_documentacao/∅ ✓G | 0.83 · 0.04 · 0.04 | credito_documentacao/∅ ✓G |
| MP-T039 | motivo dito com educação | preco/preco_acima_orcamento | — | imovel/tamanho_planta ✗G | preco (0.98) | preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ✓ | preco_acima_orcamento (1.00; grupo 1.00) | preco/preco_acima_orcamento ✓ | preco (0.99) › preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ✓ | 0.76 · 0.04 · 0.02 | preco/preco_acima_orcamento ✓ |
| MP-T040 | fácil / outros | credito_documentacao/financiamento_negado | — | credito_documentacao/restricao_cadastral ✗f | credito_documentacao (0.99) | financiamento_negado (0.97) | credito_documentacao/financiamento_negado ✓ | financiamento_negado (0.99; grupo 1.00) | credito_documentacao/financiamento_negado ✓ | credito_documentacao (0.99) › financiamento_negado (0.97) | credito_documentacao/financiamento_negado ✓ | 0.96 · 0.02 · 0.03 | credito_documentacao/financiamento_negado ✓ |
| MP-T041 | só o grupo é decidível | concorrencia/∅ | — | sem_informacao/adiou_sem_motivo ✗G | concorrencia (0.94) | only_group (0.99) | concorrencia/∅ ✓G | outra_imobiliaria (0.84; grupo 0.90) | concorrencia/outra_imobiliaria ✗f | concorrencia (0.92) › only_group (0.99) | concorrencia/∅ ✓G | 0.98 · 0.04 · 0.96 | concorrencia/∅ ✓G |
| MP-T042 | só o grupo é decidível | imovel/∅ | — | imovel/estado_conservacao ✗f | imovel (0.85) | only_group (1.00) | imovel/∅ ✓G | adiou_sem_motivo (0.22; grupo 0.44) | imovel/∅ ? | imovel (0.82) › only_group (1.00) | imovel/∅ ✓G | 0.95 · 0.03 · 0.02 | imovel/∅ ✓G |
| MP-T043 | só o grupo é decidível | concorrencia/∅ | — | preco/preco_acima_orcamento ✗G | concorrencia (1.00) | only_group (1.00) | concorrencia/∅ ✓G | outra_imobiliaria (0.86; grupo 0.97) | concorrencia/outra_imobiliaria ✗f | concorrencia (1.00) › only_group (1.00) | concorrencia/∅ ✓G | 0.97 · 0.04 · 0.96 | concorrencia/∅ ✓G |
| MP-T044 | fácil / outros | localizacao/entorno_seguranca | — | localizacao/entorno_seguranca ✓ | imovel (0.67) | estado_conservacao (0.98) | imovel/estado_conservacao ✗G | entorno_seguranca (0.99; grupo 0.99) | localizacao/entorno_seguranca ✓ | imovel (0.61) › estado_conservacao (0.99) | imovel/estado_conservacao ✗G | 0.96 · 0.04 · 0.02 | imovel/estado_conservacao ✗G |
| MP-T045 | motivo real diferente do declarado | credito_documentacao/restricao_cadastral | — | imovel/estado_conservacao ✗G | credito_documentacao (0.94) | restricao_cadastral (1.00) | credito_documentacao/restricao_cadastral ✓ | restricao_cadastral (0.96; grupo 0.96) | credito_documentacao/restricao_cadastral ✓ | credito_documentacao (0.93) › restricao_cadastral (1.00) | credito_documentacao/restricao_cadastral ✓ | 0.97 · 0.03 · 0.03 | credito_documentacao/restricao_cadastral ✓ |
| MP-T046 | fácil / outros | credito_documentacao/documentacao_imovel | — | credito_documentacao/documentacao_imovel ✓ | credito_documentacao (0.91) | documentacao_imovel (0.99) | credito_documentacao/documentacao_imovel ✓ | documentacao_imovel (1.00; grupo 1.00) | credito_documentacao/documentacao_imovel ✓ | credito_documentacao (0.92) › documentacao_imovel (1.00) | credito_documentacao/documentacao_imovel ✓ | 0.98 · 0.05 · 0.02 | credito_documentacao/documentacao_imovel ✓ |
| MP-T047 | fácil / outros | momento_cliente/adiou_decisao | — | localizacao/distancia_deslocamento ✗G | momento_cliente (1.00) | adiou_decisao (0.95) | momento_cliente/adiou_decisao ✓ | adiou_decisao (0.99; grupo 1.00) | momento_cliente/adiou_decisao ✓ | momento_cliente (1.00) › adiou_decisao (0.96) | momento_cliente/adiou_decisao ✓ | 0.94 · 0.02 · 0.02 | momento_cliente/adiou_decisao ✓ |
| MP-T048 | fechou em outro lugar | preco/custos_extras | outra_imobiliaria | imovel/diferente_do_anuncio ✗G | concorrencia (0.68) | outra_imobiliaria (1.00) | concorrencia/outra_imobiliaria ≈ | custos_extras (0.69; grupo 0.70) | preco/custos_extras ✓ | concorrencia (0.68) › outra_imobiliaria (1.00) | concorrencia/outra_imobiliaria ≈ | 0.98 · 0.08 · 0.97 | concorrencia/outra_imobiliaria ≈ |
| MP-T049 | fácil / outros | atendimento/pressao_insistencia | — | sem_informacao/sumiu_apos_valor ✗G | atendimento (0.99) | pressao_insistencia (1.00) | atendimento/pressao_insistencia ✓ | pressao_insistencia (1.00; grupo 1.00) | atendimento/pressao_insistencia ✓ | atendimento (0.99) › pressao_insistencia (1.00) | atendimento/pressao_insistencia ✓ | 0.95 · 0.65 · 0.02 | atendimento/pressao_insistencia ✓ |
| MP-T050 | fácil / outros | preco/preco_acima_orcamento | — | credito_documentacao/financiamento_negado ✗G | preco (0.83) | preco_acima_orcamento (0.78) | preco/preco_acima_orcamento ✓ | preco_acima_orcamento (0.41; grupo 0.81) | preco/∅ ∅G | preco (0.84) › preco_acima_orcamento (0.83) | preco/preco_acima_orcamento ✓ | 0.97 · 0.04 · 0.03 | preco/preco_acima_orcamento ✓ |
| MP-T051 | sumiço depois de preço | sem_informacao/sumiu_apos_valor | — | imovel/diferente_do_anuncio ✗I | sem_informacao (1.00) | sumiu_apos_valor (0.71) | sem_informacao/sumiu_apos_valor ✓ | sumiu_apos_valor (0.63; grupo 1.00) | sem_informacao/sumiu_apos_valor ✓ | sem_informacao (1.00) › sumiu_apos_valor (0.64) | sem_informacao/sumiu_apos_valor ✓ | 0.05 · 0.03 · 0.01 | sem_informacao/sumiu_apos_valor ✓ |
| MP-T052 | fácil / outros | momento_cliente/mudanca_de_vida | — | momento_cliente/desistiu_de_mudar ✗f | momento_cliente (1.00) | mudanca_de_vida (1.00) | momento_cliente/mudanca_de_vida ✓ | mudanca_de_vida (1.00; grupo 1.00) | momento_cliente/mudanca_de_vida ✓ | momento_cliente (1.00) › mudanca_de_vida (1.00) | momento_cliente/mudanca_de_vida ✓ | 0.96 · 0.02 · 0.03 | momento_cliente/mudanca_de_vida ✓ |
| MP-T053 | motivo do corretor | atendimento/informacao_errada | imovel_indisponivel | credito_documentacao/restricao_cadastral ✗G | atendimento (0.93) | informacao_errada (0.92) | atendimento/informacao_errada ✓ | informacao_errada (0.95; grupo 0.98) | atendimento/informacao_errada ✓ | atendimento (0.95) › informacao_errada (0.93) | atendimento/informacao_errada ✓ | 0.97 · 0.89 · 0.03 | atendimento/informacao_errada ✓ |
| MP-T054 | dois motivos | imovel/tamanho_planta | preco_acima_orcamento | atendimento/informacao_errada ✗G | imovel (0.80) | tamanho_planta (1.00) | imovel/tamanho_planta ✓ | tamanho_planta (0.98; grupo 0.98) | imovel/tamanho_planta ✓ | imovel (0.80) › tamanho_planta (1.00) | imovel/tamanho_planta ✓ | 0.98 · 0.04 · 0.07 | imovel/tamanho_planta ✓ |
| MP-T055 | fronteira entre folhas | atendimento/visita_falhou | — | atendimento/visita_falhou ✓ | atendimento (0.82) | visita_falhou (0.99) | atendimento/∅ ? | visita_falhou (0.98; grupo 0.98) | atendimento/∅ ? | atendimento (0.77) › visita_falhou (0.99) | atendimento/∅ ? | 0.85 · 0.13 · 0.02 | atendimento/visita_falhou ✓ |
| MP-T056 | fácil / outros | concorrencia/direto_proprietario | — | credito_documentacao/restricao_cadastral ✗G | concorrencia (1.00) | direto_proprietario (1.00) | concorrencia/direto_proprietario ✓ | direto_proprietario (1.00; grupo 1.00) | concorrencia/direto_proprietario ✓ | concorrencia (1.00) › direto_proprietario (1.00) | concorrencia/direto_proprietario ✓ | 0.95 · 0.03 · 0.98 | concorrencia/direto_proprietario ✓ |
| MP-T057 | fácil / outros | imovel/estado_conservacao | — | imovel/estado_conservacao ✓ | imovel (0.95) | estado_conservacao (1.00) | imovel/estado_conservacao ✓ | estado_conservacao (1.00; grupo 1.00) | imovel/estado_conservacao ✓ | imovel (0.95) › estado_conservacao (1.00) | imovel/estado_conservacao ✓ | 0.98 · 0.09 · 0.03 | imovel/estado_conservacao ✓ |
| MP-T058 | fechou em outro lugar | concorrencia/outra_imobiliaria | — | preco/negociacao_frustrada ✗G | concorrencia (0.98) | outra_imobiliaria (0.90) | concorrencia/outra_imobiliaria ✓ | outra_imobiliaria (0.93; grupo 0.95) | concorrencia/outra_imobiliaria ✓ | concorrencia (0.98) › outra_imobiliaria (0.92) | concorrencia/outra_imobiliaria ✓ | 0.98 · 0.04 · 0.62 | concorrencia/outra_imobiliaria ✓ |
| MP-T059 | fechou em outro lugar | concorrencia/lancamento_construtora | condicao_pagamento | preco/condicao_pagamento ≈ | concorrencia (0.99) | lancamento_construtora (1.00) | concorrencia/lancamento_construtora ✓ | lancamento_construtora (1.00; grupo 1.00) | concorrencia/lancamento_construtora ✓ | concorrencia (0.99) › lancamento_construtora (1.00) | concorrencia/lancamento_construtora ✓ | 0.93 · 0.05 · 0.94 | concorrencia/lancamento_construtora ✓ |
| MP-T060 | sumiço depois de preço | sem_informacao/sumiu_apos_valor | — | credito_documentacao/restricao_cadastral ✗I | sem_informacao (1.00) | sumiu_sem_resposta (0.56) | sem_informacao/sumiu_sem_resposta ✗f | sumiu_apos_valor (0.69; grupo 0.99) | sem_informacao/sumiu_apos_valor ✓ | sem_informacao (1.00) › sumiu_sem_resposta (0.55) | sem_informacao/sumiu_sem_resposta ✗f | 0.04 · 0.02 · 0.01 | sem_informacao/sumiu_sem_resposta ✗f |
| MP-T061 | fácil / outros | atendimento/imovel_indisponivel | — | atendimento/visita_falhou ✗f | imovel (0.79) | falta_item (1.00) | imovel/falta_item ✗G | falta_item (0.76; grupo 0.76) | imovel/falta_item ✗G | imovel (0.82) › falta_item (1.00) | imovel/falta_item ✗G | 0.95 · 0.26 · 0.04 | imovel/falta_item ✗G |
| MP-T062 | fronteira entre folhas | preco/negociacao_frustrada | preco_acima_orcamento | localizacao/entorno_seguranca ✗G | preco (0.73) | preco_acima_orcamento (0.68) | preco/preco_acima_orcamento ≈ | preco_acima_orcamento (0.55; grupo 0.94) | preco/preco_acima_orcamento ≈ | preco (0.70) › preco_acima_orcamento (0.62) | preco/preco_acima_orcamento ≈ | 0.98 · 0.10 · 0.05 | preco/preco_acima_orcamento ≈ |
| MP-T063 | motivo dito com educação | sem_informacao/adiou_sem_motivo | — | atendimento/demora_resposta ✗I | sem_informacao (0.99) | adiou_sem_motivo (1.00) | sem_informacao/adiou_sem_motivo ✓ | adiou_sem_motivo (0.99; grupo 1.00) | sem_informacao/adiou_sem_motivo ✓ | sem_informacao (0.99) › adiou_sem_motivo (1.00) | sem_informacao/adiou_sem_motivo ✓ | 0.24 · 0.03 · 0.02 | sem_informacao/adiou_sem_motivo ✓ |
| MP-T064 | fácil / outros | momento_cliente/adiou_decisao | — | preco/preco_acima_orcamento ✗G | momento_cliente (0.88) | adiou_decisao (1.00) | momento_cliente/adiou_decisao ✓ | adiou_decisao (1.00; grupo 1.00) | momento_cliente/adiou_decisao ✓ | momento_cliente (0.89) › adiou_decisao (1.00) | momento_cliente/adiou_decisao ✓ | 0.95 · 0.03 · 0.02 | momento_cliente/adiou_decisao ✓ |
| MP-T065 | fácil / outros | momento_cliente/decisor_vetou | — | preco/preco_acima_orcamento ✗G | momento_cliente (0.42) | decisor_vetou (0.83) | momento_cliente/∅ ? | decisor_vetou (0.96; grupo 0.96) | momento_cliente/decisor_vetou ✓ | momento_cliente (0.39) › decisor_vetou (0.81) | momento_cliente/∅ ? | 0.91 · 0.04 · 0.04 | momento_cliente/∅ ? |
| MP-T066 | dois motivos | momento_cliente/mudanca_de_vida | — | sem_informacao/adiou_sem_motivo ✗G | momento_cliente (1.00) | mudanca_de_vida (1.00) | momento_cliente/mudanca_de_vida ✓ | mudanca_de_vida (1.00; grupo 1.00) | momento_cliente/mudanca_de_vida ✓ | momento_cliente (1.00) › mudanca_de_vida (1.00) | momento_cliente/mudanca_de_vida ✓ | 0.96 · 0.02 · 0.02 | momento_cliente/mudanca_de_vida ✓ |
| MP-T067 | fácil / outros | imovel/falta_item | — | imovel/falta_item ✓ | imovel (1.00) | falta_item (1.00) | imovel/falta_item ✓ | falta_item (1.00; grupo 1.00) | imovel/falta_item ✓ | imovel (1.00) › falta_item (1.00) | imovel/falta_item ✓ | 0.98 · 0.05 · 0.02 | imovel/falta_item ✓ |
| MP-T068 | fronteira entre folhas | imovel/diferente_do_anuncio | falta_item | imovel/diferente_do_anuncio ✓ | atendimento (0.64) | informacao_errada (1.00) | atendimento/informacao_errada ✗G | diferente_do_anuncio (0.79; grupo 0.80) | imovel/diferente_do_anuncio ✓ | atendimento (0.68) › informacao_errada (1.00) | atendimento/informacao_errada ✗G | 0.98 · 0.75 · 0.03 | atendimento/informacao_errada ✗G |
