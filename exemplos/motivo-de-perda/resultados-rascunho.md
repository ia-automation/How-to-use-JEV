# Rascunho — motivo-de-perda (encanamento)

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, limiares, variante principal e critério: `perguntas.py`; validação, decisão e baseline: `motivo.py`; bateria do código (sem API): `testa_falhas.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Limiares: {'grupo': 0.5, 'folha': 0.5, 'folha_unica': 0.5, 'guarda': 0.5, 'sem_motivo': 0.5}; teto da conversa 6000 caracteres.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (68 conversas: 8 `sem_informacao`, 7 com `folha: null`), variante principal com os limiares acima; **variante_principal**: a; **1_motivo_inventado**: gabarito `sem_informacao` e saiu outro grupo sem revisar ≤ 1/8; **2_grupo_errado_automatizado**: grupo ≠ gabarito (e folha fora de `aceitaveis`) sem revisar ≤ 6/68 (≤ 0,09); **3_acerto_folgado**: folha ∈ `aceitaveis` (ou só o grupo certo quando `folha` é null), revisão e falha contam como erro ≥ 0,70; **4_grupo_certo**: grupo = gabarito ou folha ∈ `aceitaveis`, revisão e falha contam como erro ≥ 0,80; **5_revisao**: conversas mandadas a revisão (inclui falha operacional) ≤ 20% (≤ 13/68); **6_contra_baseline**: acerto folgado > o do baseline de palavras-chave nos mesmos casos; **se_falhar**: 1 = o relatório inventa motivo: não serve nem como sugestão; 2 = o relatório mente de grupo: não serve sem revisão humana de tudo; 3/4 = não lê a conversa melhor que um gestor apressado; 5 = revisa demais para valer a automação; 6 = palavra-chave basta

Versão em afinação (NÃO congelada): `perguntas.py` sha256 0ac0dd4a5c362f38… · `motivo.py` sha256 54d584cf63e8fb59… · `run.py` sha256 8eba4a080f659cc0… · `dados/teste.json` sha256 015a04e1f083ddb7… · `dados/taxonomia.json` sha256 7ab1ad5faeeedc80…

## Conjunto `rascunho` — 5 conversas (arquivo versão 2026-10-01, autor fable); 0 difíceis, 0 com `folha: null`, 1 `sem_informacao`, 0 em revisão por falha operacional ou teto; taxonomia de 8 grupos e 30 folhas

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Desfecho — baseline de código × variantes com Jev, nas mesmas conversas

`estrito` = a folha principal do gabarito (ou só o grupo certo quando `folha` é null). `folgado` = folha ∈ `aceitaveis` (ou só o grupo certo quando `folha` é null). `grupo certo` = grupo = gabarito ou folha aceitável. **Motivo INVENTADO** (erro caro) = gabarito `sem_informacao` e saiu outro grupo, automatizado (denominador = casos `sem_informacao`). **Grupo errado automatizado** (erro caro) = grupo ≠ gabarito sem revisão, inclui os inventados. `só-grupo certo` = nos casos `folha: null`, saiu só o grupo certo. `absteve` = havia folha, saiu só o grupo certo (nem acerto nem erro). Revisão e falha contam como erro em todas as taxas de acerto. Custo e latência: só as requisições que a variante envia em produção, medidas. Variante principal (a que o critério julga): **a · duas etapas (grupo → folhas do grupo)**.

| variante | n | acerto estrito | acerto folgado | grupo certo | motivo INVENTADO | grupo errado auto. | só-grupo certo | sem_info certo | absteve | folha errada | revisar | falha | req/caso | tokens/caso | US$/1000 | p50_ms | p95_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| código: palavra-chave por folha | 5 | 0.200 | 0.200 | 0.400 | 1/1 | 3/5 | 0/0 | 0/1 | 0/5 | 1/5 | 0/5 | 0/5 | 0 | 0 | 0 | 0 | 0 |
| a · duas etapas (grupo → folhas do grupo) | 5 | 1.000 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 1/1 | 0/5 | 0/5 | 0/5 | 0/5 | 2.00 | 2441 | 0.1025 | 656 | 744 |
| b · Choice única sobre as 30 folhas | 5 | 1.000 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 1/1 | 0/5 | 0/5 | 0/5 | 0/5 | 1.00 | 2527 | 0.1061 | 260 | 263 |
| c · uma requisição (grupo + folhas por grupo) | 5 | 1.000 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 1/1 | 0/5 | 0/5 | 0/5 | 0/5 | 1.00 | 6010 | 0.2524 | 313 | 345 |
| a sem as guardas (informativa) | 5 | 1.000 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 1/1 | 0/5 | 0/5 | 0/5 | 0/5 | 2.00 | 2441 | 0.1025 | 656 | 744 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 motivo INVENTADO (gabarito `sem_informacao`, saiu outro grupo, automatizado) | 0/1 | ≤ 1 | ✓ |
| 2 grupo errado automatizado (inclui os inventados) | 0/5 (0.000) | ≤ 0.09 | ✓ |
| 3 acerto folgado (revisão e falha = erro) | 1.000 | ≥ 0.70 | ✓ |
| 4 grupo certo (revisão e falha = erro) | 1.000 | ≥ 0.80 | ✓ |
| 5 revisão (inclui falha) | 0/5 (0.000) | ≤ 0.20 | ✓ |
| 6 contra o baseline de palavras-chave | 1.000 × 0.200 | > | ✓ |

### Por família difícil (pela `nota` do rotulador) — acertos folgados; erros caros e revisões da principal

| família | n | `null` | base | a | b | c | a-sg | inventado (principal) | grupo errado (principal) | revisar (principal) |
|---|---|---|---|---|---|---|---|---|---|---|
| fácil / outros | 5 | 0 | 1 | 5 | 5 | 5 | 5 | 0 | 0 | 0 |

### As guardas na principal (`a`) — o que cada Noul mudou

| guarda | disparou | tirou um erro | tirou um acerto | casos |
|---|---|---|---|---|
| `blames_agency` (grupo atendimento) | 0 | 0 | 0 | — |
| `closed_elsewhere` (grupo concorrencia) | 0 | 0 | 0 | — |
| `reason_stated` (grupo ≠ sem_informacao) | 0 | 0 | 0 | — |

### Os sinais — quem aponta o grupo e a folha certos, sem limiar nenhum

| quem aponta o grupo | grupo certo |
|---|---|
| Choice `group` (requisição `grupo`) | 5/5 |
| soma das folhas por grupo (Choice única) | 5/5 |
| Choice `group` (requisição `tudo`) | 5/5 |

| quem aponta a folha | a principal | alguma aceitável | `only_group` |
|---|---|---|---|
| Choice das folhas do grupo vencedor (`folhas`) | 5/5 | 5/5 | 0/5 |
| Choice única (vencedora) | 5/5 | 5/5 | 0/5 |
| Choice `leaf.<grupo vencedor>` (`tudo`) | 5/5 | 5/5 | 0/5 |

p(grupo vencedor) na Choice `group` (`grupo`): quando certo (n = 5) mínimo 0.83, p10 0.83, mediana 0.94; quando errado (n = 0) mínimo —, mediana —, máximo —. 
p(folha vencedora) em `folhas`: certa mínimo 1.00, p10 1.00, mediana 1.00; errada (fora de aceitáveis) —. Na Choice única: certa mínimo 0.93, p10 0.93, mediana 1.00; errada —.

A MESMA Choice `group` em duas requisições (`grupo` × `tudo`, isolamento ≠ determinismo) trocou de vencedor em 0/5.

Noul `reason_stated` (requisição `grupo`): onde o gabarito pede sim (n = 4) mínimo 0.95, p10 0.95, mediana 0.96; onde pede não (n = 1) mediana 0.04, p90 0.04, máximo 0.04.

Noul `blames_agency` (requisição `grupo`): onde o gabarito pede sim (n = 0) mínimo —, p10 —, mediana —; onde pede não (n = 5) mediana 0.04, p90 0.05, máximo 0.05.

Noul `closed_elsewhere` (requisição `grupo`): onde o gabarito pede sim (n = 1) mínimo 0.97, p10 0.97, mediana 0.97; onde pede não (n = 4) mediana 0.02, p90 0.03, máximo 0.03.

O mesmo Noul em requisições diferentes: `grupo` × `unica` diferença absoluta média 0.001, máxima 0.010; `grupo` × `tudo` média 0.001, máxima 0.010 (n = 15).

### Cobertura × erro por limiar (um limiar por vez; os outros como em `perguntas.py`)

**a · duas etapas (grupo → folhas do grupo)** — limiar `grupo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.200 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.300 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.400 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.500 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.600 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.700 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.800 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.900 | 4/5 | 0.800 | 0.800 | 0/1 | 0/5 | 0/0 | 0 | 0 | 1 |

**a · duas etapas (grupo → folhas do grupo)** — limiar `folha` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.200 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.300 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.400 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.500 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.600 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.700 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.800 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.900 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |

**a · duas etapas (grupo → folhas do grupo)** — limiar `guarda` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.200 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.300 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.400 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.500 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.600 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.700 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.800 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.900 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |

**a · duas etapas (grupo → folhas do grupo)** — limiar `sem_motivo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.200 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.300 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.400 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.500 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.600 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.700 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.800 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.900 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |

**b · Choice única sobre as 30 folhas** — limiar `grupo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.200 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.300 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.400 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.500 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.600 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.700 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.800 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.900 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |

**b · Choice única sobre as 30 folhas** — limiar `folha_unica` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.200 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.300 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.400 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.500 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.600 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.700 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.800 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.900 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |

**c · uma requisição (grupo + folhas por grupo)** — limiar `grupo` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.200 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.300 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.400 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.500 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.600 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.700 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.800 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.900 | 4/5 | 0.800 | 0.800 | 0/1 | 0/5 | 0/0 | 0 | 0 | 1 |

**c · uma requisição (grupo + folhas por grupo)** — limiar `folha` (em uso: 0.5)

| limiar | automatizadas | folgado | grupo certo | inventado | grupo errado auto. | só-grupo certo | absteve | folha errada | revisar |
|---|---|---|---|---|---|---|---|---|---|
| 0.100 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.200 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.300 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.400 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.500 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.600 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.700 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.800 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |
| 0.900 | 5/5 | 1.000 | 1.000 | 0/1 | 0/5 | 0/0 | 0 | 0 | 0 |

### Custo e latência por formato de requisição (medidos)

| requisição | enviadas | novas (não cache) | tokens por requisição | p50_ms | p95_ms | quem usa |
|---|---|---|---|---|---|---|
| grupo | 5 | 5 | 1484 | 341 | 439 | a |
| folhas | 5 | 5 | 957 | 287 | 345 | a |
| unica | 5 | 5 | 2527 | 260 | 263 | b |
| tudo | 5 | 5 | 6010 | 313 | 345 | c |

Tudo o que esta execução usou: 20 requisições (20 novas), 54887 tokens, US$ 0.0023 · modelo: jev-1.13.0. Latência = a da chamada original de cada requisição (o cache a guarda), medida com 8 conversas em paralelo.

### Caso a caso

Marca: ✓ a folha principal · ≈ aceitável · ✓G só grupo, certo · ∅G absteve da folha (grupo certo) · ✗f folha errada (grupo certo) · ✗G grupo errado · ✗I motivo INVENTADO · ? revisar · ✗F falha. Célula = `grupo/folha marca`; `∅` = sem folha. `grupo` = Choice `group` com p(vencedor); `nouls` = reason_stated · blames_agency · closed_elsewhere (requisição `grupo`).

| id | fam | gabarito | outras aceitáveis | base | grupo | folhas | a | única | b | tudo | c | nouls | a-sg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MP-R001 | fácil / outros | preco/preco_acima_orcamento | — | localizacao/bairro_nao_desejado ✗G | preco (0.83) | preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ✓ | preco_acima_orcamento (0.93; grupo 0.93) | preco/preco_acima_orcamento ✓ | preco (0.83) › preco_acima_orcamento (1.00) | preco/preco_acima_orcamento ✓ | 0.95 · 0.05 · 0.02 | preco/preco_acima_orcamento ✓ |
| MP-R002 | fácil / outros | credito_documentacao/financiamento_negado | — | credito_documentacao/financiamento_negado ✓ | credito_documentacao (0.94) | financiamento_negado (1.00) | credito_documentacao/financiamento_negado ✓ | financiamento_negado (1.00; grupo 1.00) | credito_documentacao/financiamento_negado ✓ | credito_documentacao (0.94) › financiamento_negado (1.00) | credito_documentacao/financiamento_negado ✓ | 0.97 · 0.02 · 0.01 | credito_documentacao/financiamento_negado ✓ |
| MP-R003 | fácil / outros | concorrencia/outra_imobiliaria | — | preco/preco_acima_orcamento ✗G | concorrencia (1.00) | outra_imobiliaria (1.00) | concorrencia/outra_imobiliaria ✓ | outra_imobiliaria (1.00; grupo 1.00) | concorrencia/outra_imobiliaria ✓ | concorrencia (1.00) › outra_imobiliaria (1.00) | concorrencia/outra_imobiliaria ✓ | 0.96 · 0.04 · 0.97 | concorrencia/outra_imobiliaria ✓ |
| MP-R004 | fácil / outros | sem_informacao/sumiu_sem_resposta | — | atendimento/imovel_indisponivel ✗I | sem_informacao (0.99) | sumiu_sem_resposta (1.00) | sem_informacao/sumiu_sem_resposta ✓ | sumiu_sem_resposta (0.99; grupo 0.99) | sem_informacao/sumiu_sem_resposta ✓ | sem_informacao (0.99) › sumiu_sem_resposta (1.00) | sem_informacao/sumiu_sem_resposta ✓ | 0.04 · 0.03 · 0.01 | sem_informacao/sumiu_sem_resposta ✓ |
| MP-R005 | fácil / outros | imovel/falta_item | — | imovel/estado_conservacao ✗f | imovel (0.90) | falta_item (1.00) | imovel/falta_item ✓ | falta_item (1.00; grupo 1.00) | imovel/falta_item ✓ | imovel (0.95) › falta_item (1.00) | imovel/falta_item ✓ | 0.95 · 0.04 · 0.03 | imovel/falta_item ✓ |
