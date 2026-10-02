# Rascunho — imovel-duplicado (encanamento)

## Conjunto `rascunho` — 5 pares (arquivo versão 2026-10-01, autor fable); 3 duplicatas, 2 diferentes, 0 indecidíveis; 0 difíceis

> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**

### Ação (3 classes) — métrica principal, baseline × sempre revisa × Jev nos mesmos pares

Gabarito da ação: `mesmo_imovel` true → `unir`; false → `manter_separados`; null → `revisar`. **DIFERENTE UNIDO** = par de imóveis diferentes que saiu `unir` (a união apagaria um imóvel do catálogo). `indecidível unido` = gabarito `null` que saiu `unir` (união sem prova). **DUPLICATA SEPARADA** = mesmo imóvel que saiu `manter_separados` (a duplicata fica e ninguém revisa). `baseline` = mesmos bairro/cidade + quartos + vagas + área ±3% + preço ±5% ⇒ unir, senão separados. `sempre revisa` = zero erro caro, 100% dos pares a humano. `só Score` = arredondamento do Score (cortes 0,5 e 1,5), como na receita; `só Nouls` = política sem o Score; `Jev (política)` = Nouls + Score como segunda leitura da união. As três leem a MESMA resposta.

| variante | n | acerto_acao | DIFERENTE UNIDO (apagaria um imóvel) | indecidível unido | DUPLICATA SEPARADA | duplicata unida | null → revisar | revisou sem necessidade |
|---|---|---|---|---|---|---|---|---|
| baseline (4 sinais) | 5 | 1.000 | 0/2 | 0/0 | 0/3 | 3/3 | 0/0 | 0/5 |
| sempre revisa | 5 | 0.000 | 0/2 | 0/0 | 0/3 | 0/3 | 0/0 | 5/5 |
| só Score | 5 | 1.000 | 0/2 | 0/0 | 0/3 | 3/3 | 0/0 | 0/5 |
| só Nouls | 5 | 1.000 | 0/2 | 0/0 | 0/3 | 3/3 | 0/0 | 0/5 |
| Jev (política) | 5 | 1.000 | 0/2 | 0/0 | 0/3 | 3/3 | 0/0 | 0/5 |

**Critério conferido no `rascunho`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 diferente unido | 0/2 | ≤ 0 | ✓ |
| 2 indecidível unido | 0/0 | ≤ 1 | ✓ |
| 3 duplicata separada | 0/3 (0.000) | ≤ 0.05 | ✓ |
| 4 acerto da ação | 1.000 (baseline 1.000) | ≥ 1.150 | ✗ |
| secundário: nulo → revisar | 0/0 | todos | ✓ |
| secundário: revisou sem necessidade | 0/5 (0.000) | ≤ 0.15 | ✓ |
| secundário: sinais numéricos do código | 100% | 100% (senão é bug) | ✓ |

**Matriz de confusão — Jev (política)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 3 | 0 | 0 |
| revisar | 0 | 0 | 0 |
| manter_separados | 0 | 0 | 2 |

**Matriz de confusão — só Nouls** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 3 | 0 | 0 |
| revisar | 0 | 0 | 0 |
| manter_separados | 0 | 0 | 2 |

**Matriz de confusão — só Score** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 3 | 0 | 0 |
| revisar | 0 | 0 | 0 |
| manter_separados | 0 | 0 | 2 |

**Matriz de confusão — baseline (4 sinais)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 3 | 0 | 0 |
| revisar | 0 | 0 | 0 |
| manter_separados | 0 | 0 | 2 |

**Erros caros, par a par** (todas as variantes)

_(nenhum)_

### Sinais numéricos do código — têm de bater 100% com o gabarito (senão é bug)

| sinal | certos | ok |
|---|---|---|
| `mesma_area` (±3%) | 5/5 | ✓ |
| `mesmo_preco` (±5%) | 5/5 | ✓ |
| quartos ou vagas diferentes ⇒ `mesma_planta` false | 2/2 | ✓ |
| decidido pelo código sem chamada (cidade, quartos ou vagas) ⇒ gabarito false | 2/2 | ✓ |

Área fora da tolerância entre os pares que foram ao Jev: 0; conciliada pelo código pela relação total × privativa rotulada no texto: 0 (destes, duplicatas reais: 0); indefinida (uma metragem do texto bate, mas sem rótulo de área da unidade → não concilia): 0.

Bairro que difere no texto dentro da mesma cidade (não prova outro imóvel: o código não separa sozinho, o par vai ao Jev e não pode sair `unir`): 0.

### Sinais de texto (Nouls) contra os `sinais` do gabarito — 3 pares que foram ao Jev

`mesmo_endereco` tem três valores (true / false / `null` = um dos anúncios não cita prédio nem rua): `same_building_or_street` mede o true, `address_conflict` mede o false. `mesma_planta` false, entre os pares que chegam ao Jev (quartos e vagas iguais), é `layout_contradiction`. Acerto com corte 0,5; `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela.

| noul | positivos | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| same_building_or_street | 3 | 1.000 | 0.2–0.8 | 1.000 | 1.000 | 0 | 3 | 0.003 |
| address_conflict | 0 | 1.000 | 0.2–0.7 | 1.000 | 1.000 | 0 | 3 | 0.001 |
| layout_contradiction | 0 | 1.000 | 0.2–0.7 | 1.000 | 1.000 | 0 | 3 | 0.000 |

**`mesmo_endereco` em três valores** (os dois Nouls juntos, corte 0,5): 3/3 certos

| gabarito ↓ / previsto → | True | False | None |
|---|---|---|---|
| True | 3 | 0 | 0 |
| False | 0 | 0 | 0 |
| None | 0 | 0 | 0 |

**`mesma_planta` composta** (quartos e vagas iguais pelo CÓDIGO e nenhum cômodo estrutural contradito pelo Noul; par decidido pelo código sem chamada entra só com a parte do código): 1.000 (n = 5)

### Nouls sem campo próprio no gabarito — valores por grupo

| noul | grupo | n_grupo | mín–máx no grupo | grupo ≥ sim | grupo ≤ nao | mín–máx fora | fora ≥ sim | fora ≤ nao | faixa |
|---|---|---|---|---|---|---|---|---|---|
| fixed_contradiction | família detalhe fixo contradiz | 0 | — | 0 | 0 | 0.02–0.03 | 0 | 3 | 0.2–0.7 |
| state_contradiction | família mobiliado × vazio | 0 | — | 0 | 0 | 0.02–0.03 | 0 | 3 | 0.2–0.8 |
| shared_distinctive_details | duplicatas reais (true) | 3 | 0.95–0.97 | 3 | 0 | — | 0 | 0 | 0.2–0.8 |
| shared_distinctive_details | família sem detalhe distintivo | 0 | — | 0 | 0 | 0.95–0.97 | 3 | 0 | 0.2–0.8 |

### Score `same_listing` (0 = diferentes · 1 = não dá para saber · 2 = a mesma unidade)

| gabarito `mesmo_imovel` | esperado | n | média | mín–máx | → 0 (≤ 0,5) | → 1 | → 2 (≥ 1,5) | ≥ 1.7 (mínimo da política) |
|---|---|---|---|---|---|---|---|---|
| True | 2 | 3 | 1.897 | 1.75–1.99 | 0 | 0 | 3 | 3 |
| None | 1 | 0 | nan | — | 0 | 0 | 0 | 0 |
| False | 0 | 0 | nan | — | 0 | 0 | 0 | 0 |

**Cobertura × erro por confiança do Score** (acerto = arredondamento igual ao gabarito)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 3 |
| 0.300 | 1.000 | 0.000 | 3 |
| 0.500 | 1.000 | 0.000 | 3 |
| 0.700 | 0.667 | 0.000 | 2 |
| 0.900 | 0.667 | 0.000 | 2 |

**O Score acrescenta algo aos Nouls?** Na política ele só pode tirar uma união. Mudou a decisão dos Nouls em 0 par(es): 0 união(ões) sem prova evitada(s), 0 união(ões) certa(s) mandada(s) a `revisar`. Sozinho (arredondamento): 0 diferente(s) e 0 indecidível(is) unidos, 0 duplicata(s) separada(s), acerto 1.000; só Nouls: 0, 0, 0, acerto 1.000.

### Por família (pela `nota` do rotulador)

| família | gabarito | n | ação Jev | ação baseline | Jev → revisar | sem chamada (código) | erro caro Jev | erro caro baseline |
|---|---|---|---|---|---|---|---|---|
| fácil: bairros/cidades diferentes | False | 2 | 1.000 | 1.000 | 0 | 2 | 0 | 0 |
| fácil: dois corretores, mesmo imóvel | True | 3 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |

### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)

`cobertura_auto` = par que não foi a `revisar` (inclui os decididos pelo código sem chamada). **Vetos** (a mesma faixa em `address_conflict`, `layout_contradiction` e `fixed_contradiction`):

| faixa (3 vetos) | cobertura_auto | erro_automatico | diferentes unidos | indecidíveis unidos | duplicatas separadas | duplicatas unidas | n_auto |
|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| 0.4–0.6 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| 0.3–0.7 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| 0.2–0.8 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| 0.1–0.9 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| 0.05–0.95 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |

**O que autoriza a união** (um parâmetro por vez, o resto como em `perguntas.py`):

| parâmetro | valor | cobertura_auto | erro_automatico | diferentes unidos | indecidíveis unidos | duplicatas separadas | duplicatas unidas | n_auto |
|---|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | — | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| `sim` do sinal forte | 0.500 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| `sim` do sinal forte | 0.700 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| `sim` do sinal forte | 0.800 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| `sim` do sinal forte | 0.900 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| Score mínimo para unir | sem Score | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| Score mínimo para unir | 1.000 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| Score mínimo para unir | 1.500 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| Score mínimo para unir | 1.700 | 1.000 | 0.000 | 0 | 0 | 0 | 3 | 5 |
| Score mínimo para unir | 1.800 | 0.800 | 0.000 | 0 | 0 | 0 | 2 | 4 |
| Score mínimo para unir | 1.900 | 0.800 | 0.000 | 0 | 0 | 0 | 2 | 4 |

### Custo e latência (medidos na chamada real; do cache também)

| pares | requisicoes | novas (não cache) | sem chamada (código decide) | longos (sem chamada) | falhas operacionais (→ revisar) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_par | US$_por_1000_pares | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 3 | 0 | 2 | 0 | 0 | 21 | 365 | 381 | 1803 | 0.000227 | 0.0000454 | 0.0454 | jev-1.13.0 |

### Caso a caso

`end`/`conf` = Nouls `same_building_or_street` e `address_conflict`; `planta` = `layout_contradiction`; `fixo` = `fixed_contradiction`; `estado` = `state_contradiction`; `comum` = `shared_distinctive_details`; `score` = `same_listing` (confiança); `área`/`preço` = fatos do código (`expl.` = fora de ±3% mas conciliada pela relação total × privativa rotulada no texto; `indef.` = uma metragem do texto bate, sem rótulo: não concilia); `ok` compara a ação do Jev com o gabarito; `caro` marca o erro caro; `base` = baseline; `—` = par decidido pelo código sem chamada, ou sem fatos (entrada inválida).

| id | fam | gab | end | conf | planta | fixo | estado | comum | score | área | preço | ação Jev | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ID-R001 | fácil: dois corretores, mesmo imóvel | unir | 0.98 | 0.02 | 0.02 | 0.03 | 0.03 | 0.96 | 1.99 (0.98) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-R002 | fácil: bairros/cidades diferentes | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | cidades diferentes (código) |
| ID-R003 | fácil: dois corretores, mesmo imóvel | unir | 0.92 | 0.04 | 0.01 | 0.02 | 0.02 | 0.95 | 1.95 (0.93) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-R004 | fácil: bairros/cidades diferentes | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | cidades diferentes (código) |
| ID-R005 | fácil: dois corretores, mesmo imóvel | unir | 0.97 | 0.02 | 0.02 | 0.03 | 0.02 | 0.97 | 1.75 (0.62) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
