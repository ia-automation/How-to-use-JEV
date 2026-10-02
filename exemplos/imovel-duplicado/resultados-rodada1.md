# Resultados — imovel-duplicado

Gerado por `run.py` em 2026-10-01 (modo `auto`; modelo e amostra em cada seção). Perguntas, faixas e política: `perguntas.py`; fatos do código, validação, ação e baseline: `duplicado.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Teto do par: 4000 caracteres (acima → revisar, sem chamada). `unir` é proposta: nada é apagado.

Critério de continuar/descartar (fixado antes do teste): **onde**: no teste (80 pares: 40 duplicatas, 32 diferentes, 8 indecidíveis), com a política acima; **1_diferente_unido**: par de imóveis diferentes (gabarito false) que saiu `unir` = 0; **2_indecidivel_unido**: par indecidível (gabarito null) que saiu `unir` ≤ 1 (de 8); **3_duplicata_separada**: duplicata real (gabarito true) que saiu `manter_separados` ≤ 5% (≤ 2 de 40); **4_acerto_acao**: ação (3 classes) ≥ baseline + 0,15; **secundario_nao_decide**: todo nulo → `revisar`; revisou sem necessidade ≤ 15% dos decidíveis; sinais numéricos do código = 100% (senão é bug); **se_falhar**: 1 ou 2 falhando = não serve para propor união sem humano conferir cada uma; 3 falhando = os vetos separam demais; 4 falhando = a regra de código basta

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T13:39:34-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 bc7dfcced4da9e7f… · `duplicado.py` sha256 fcb8543a85911dd9… · `run.py` sha256 5205dde8dc6037c8… · `dados/teste.json` sha256 4d3613efeb8272a7…

## Lado a lado

### Ação por variante e conjunto

| conjunto | variante | n | acerto_acao | DIFERENTE UNIDO (apagaria um imóvel) | indecidível unido | DUPLICATA SEPARADA | duplicata unida | null → revisar | revisou sem necessidade |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | baseline (4 sinais) | 40 | 0.550 | 7/16 | 3/4 | 7/20 | 13/20 | 0/4 | 0/36 |
| ajuste | sempre revisa | 40 | 0.100 | 0/16 | 0/4 | 0/20 | 0/20 | 4/4 | 36/36 |
| ajuste | só Score | 40 | 0.950 | 0/16 | 2/4 | 0/20 | 20/20 | 2/4 | 0/36 |
| ajuste | só Nouls | 40 | 1.000 | 0/16 | 0/4 | 0/20 | 20/20 | 4/4 | 0/36 |
| ajuste | Jev (política) | 40 | 1.000 | 0/16 | 0/4 | 0/20 | 20/20 | 4/4 | 0/36 |
| teste | baseline (4 sinais) | 80 | 0.550 | 14/32 | 6/8 | 14/40 | 26/40 | 0/8 | 0/72 |
| teste | sempre revisa | 80 | 0.100 | 0/32 | 0/8 | 0/40 | 0/40 | 8/8 | 72/72 |
| teste | só Score | 80 | 0.938 | 0/32 | 5/8 | 0/40 | 40/40 | 3/8 | 0/72 |
| teste | só Nouls | 80 | 0.975 | 0/32 | 0/8 | 0/40 | 40/40 | 8/8 | 2/72 |
| teste | Jev (política) | 80 | 0.963 | 0/32 | 0/8 | 0/40 | 39/40 | 8/8 | 3/72 |

### Sinais, custo

| conjunto | n | difíceis | nulos | same_building_or_street ≥0,5 | address_conflict ≥0,5 | layout_contradiction ≥0,5 | mesmo_endereco (3 valores) | mesma_planta composta | sinais do código 100% | Score mudou a decisão | requisições | sem chamada | p50_ms | p95_ms | tokens_por_requisicao | US$_por_1000_pares | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | 40 | 33 | 4 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | ✓ | 0 | 36 | 4 | 286 | 332 | 1794 | 0.0678 | jev-1.13.0 |
| teste | 80 | 66 | 8 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | ✓ | 1 | 73 | 7 | 273 | 404 | 1785 | 0.0684 | jev-1.13.0 |

## Conjunto `ajuste` — 40 pares (arquivo versão 2026-10-01, autor fable); 20 duplicatas, 16 diferentes, 4 indecidíveis; 33 difíceis

### Ação (3 classes) — métrica principal, baseline × sempre revisa × Jev nos mesmos pares

Gabarito da ação: `mesmo_imovel` true → `unir`; false → `manter_separados`; null → `revisar`. **DIFERENTE UNIDO** = par de imóveis diferentes que saiu `unir` (a união apagaria um imóvel do catálogo). `indecidível unido` = gabarito `null` que saiu `unir` (união sem prova). **DUPLICATA SEPARADA** = mesmo imóvel que saiu `manter_separados` (a duplicata fica e ninguém revisa). `baseline` = mesmos bairro/cidade + quartos + vagas + área ±3% + preço ±5% ⇒ unir, senão separados. `sempre revisa` = zero erro caro, 100% dos pares a humano. `só Score` = arredondamento do Score (cortes 0,5 e 1,5), como na receita; `só Nouls` = política sem o Score; `Jev (política)` = Nouls + Score como segunda leitura da união. As três leem a MESMA resposta.

| variante | n | acerto_acao | DIFERENTE UNIDO (apagaria um imóvel) | indecidível unido | DUPLICATA SEPARADA | duplicata unida | null → revisar | revisou sem necessidade |
|---|---|---|---|---|---|---|---|---|
| baseline (4 sinais) | 40 | 0.550 | 7/16 | 3/4 | 7/20 | 13/20 | 0/4 | 0/36 |
| sempre revisa | 40 | 0.100 | 0/16 | 0/4 | 0/20 | 0/20 | 4/4 | 36/36 |
| só Score | 40 | 0.950 | 0/16 | 2/4 | 0/20 | 20/20 | 2/4 | 0/36 |
| só Nouls | 40 | 1.000 | 0/16 | 0/4 | 0/20 | 20/20 | 4/4 | 0/36 |
| Jev (política) | 40 | 1.000 | 0/16 | 0/4 | 0/20 | 20/20 | 4/4 | 0/36 |

**Critério conferido no `ajuste`** (informativo: só o `teste` decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 diferente unido | 0/16 | ≤ 0 | ✓ |
| 2 indecidível unido | 0/4 | ≤ 1 | ✓ |
| 3 duplicata separada | 0/20 (0.000) | ≤ 0.05 | ✓ |
| 4 acerto da ação | 1.000 (baseline 0.550) | ≥ 0.700 | ✓ |
| secundário: nulo → revisar | 4/4 | todos | ✓ |
| secundário: revisou sem necessidade | 0/36 (0.000) | ≤ 0.15 | ✓ |
| secundário: sinais numéricos do código | 100% | 100% (senão é bug) | ✓ |

**Matriz de confusão — Jev (política)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 20 | 0 | 0 |
| revisar | 0 | 4 | 0 |
| manter_separados | 0 | 0 | 16 |

**Matriz de confusão — só Nouls** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 20 | 0 | 0 |
| revisar | 0 | 4 | 0 |
| manter_separados | 0 | 0 | 16 |

**Matriz de confusão — só Score** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 20 | 0 | 0 |
| revisar | 2 | 2 | 0 |
| manter_separados | 0 | 0 | 16 |

**Matriz de confusão — baseline (4 sinais)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 13 | 0 | 7 |
| revisar | 3 | 0 | 1 |
| manter_separados | 7 | 0 | 9 |

**Erros caros, par a par** (todas as variantes)

| id | variante | erro | família |
|---|---|---|---|
| ID-A008 | só Score | indecidível unido | sem detalhe distintivo |
| ID-A040 | só Score | indecidível unido | sem detalhe distintivo |
| ID-A002 | baseline (4 sinais) | DIFERENTE UNIDO | mesmo bairro e números parecidos |
| ID-A003 | baseline (4 sinais) | DUPLICATA SEPARADA | área útil × total |
| ID-A006 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-A007 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-A008 | baseline (4 sinais) | indecidível unido | sem detalhe distintivo |
| ID-A009 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-A010 | baseline (4 sinais) | DUPLICATA SEPARADA | área útil × total |
| ID-A013 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-A017 | baseline (4 sinais) | indecidível unido | sem detalhe distintivo |
| ID-A018 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-A023 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-A026 | baseline (4 sinais) | DUPLICATA SEPARADA | área útil × total |
| ID-A031 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-A032 | baseline (4 sinais) | DIFERENTE UNIDO | mesmo bairro e números parecidos |
| ID-A035 | baseline (4 sinais) | DIFERENTE UNIDO | mesmo bairro e números parecidos |
| ID-A039 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-A040 | baseline (4 sinais) | indecidível unido | sem detalhe distintivo |

### Sinais numéricos do código — têm de bater 100% com o gabarito (senão é bug)

| sinal | certos | ok |
|---|---|---|
| `mesma_area` (±3%) | 40/40 | ✓ |
| `mesmo_preco` (±5%) | 40/40 | ✓ |
| quartos ou vagas diferentes ⇒ `mesma_planta` false | 3/3 | ✓ |
| decidido pelo código sem chamada (bairro/cidade, quartos ou vagas) ⇒ gabarito false | 4/4 | ✓ |

Área fora da tolerância entre os pares que foram ao Jev: 6; conciliada pelo código por outra metragem citada no texto: 3 (destes, duplicatas reais: 3).

### Sinais de texto (Nouls) contra os `sinais` do gabarito — 36 pares que foram ao Jev

`mesmo_endereco` tem três valores (true / false / `null` = um dos anúncios não cita prédio nem rua): `same_building_or_street` mede o true, `address_conflict` mede o false. `mesma_planta` false, entre os pares que chegam ao Jev (quartos e vagas iguais), é `layout_contradiction`. Acerto com corte 0,5; `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela.

| noul | positivos | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| same_building_or_street | 27 | 1.000 | 0.2–0.8 | 1.000 | 1.000 | 0 | 36 | 0.003 |
| address_conflict | 6 | 1.000 | 0.2–0.7 | 1.000 | 1.000 | 0 | 36 | 0.002 |
| layout_contradiction | 2 | 1.000 | 0.2–0.7 | 1.000 | 1.000 | 0 | 36 | 0.002 |

**`mesmo_endereco` em três valores** (os dois Nouls juntos, corte 0,5): 36/36 certos

| gabarito ↓ / previsto → | True | False | None |
|---|---|---|---|
| True | 27 | 0 | 0 |
| False | 0 | 6 | 0 |
| None | 0 | 0 | 3 |

**`mesma_planta` composta** (quartos e vagas iguais pelo CÓDIGO e nenhum cômodo estrutural contradito pelo Noul; par decidido pelo código sem chamada entra só com a parte do código): 1.000 (n = 40)

### Nouls sem campo próprio no gabarito — valores por grupo

| noul | grupo | n_grupo | mín–máx no grupo | grupo ≥ sim | grupo ≤ nao | mín–máx fora | fora ≥ sim | fora ≤ nao | faixa |
|---|---|---|---|---|---|---|---|---|---|
| fixed_contradiction | família detalhe fixo contradiz | 4 | 0.86–0.90 | 4 | 0 | 0.02–0.70 | 1 | 30 | 0.2–0.7 |
| state_contradiction | família mobiliado × vazio | 1 | 0.96–0.96 | 1 | 0 | 0.02–0.94 | 3 | 31 | 0.2–0.8 |
| shared_distinctive_details | duplicatas reais (true) | 20 | 0.92–0.97 | 20 | 0 | 0.06–0.96 | 5 | 9 | 0.2–0.8 |
| shared_distinctive_details | família sem detalhe distintivo | 3 | 0.11–0.15 | 0 | 3 | 0.06–0.97 | 25 | 6 | 0.2–0.8 |

### Score `same_listing` (0 = diferentes · 1 = não dá para saber · 2 = a mesma unidade)

| gabarito `mesmo_imovel` | esperado | n | média | mín–máx | → 0 (≤ 0,5) | → 1 | → 2 (≥ 1,5) | ≥ 1.7 (mínimo da política) |
|---|---|---|---|---|---|---|---|---|
| True | 2 | 20 | 1.927 | 1.83–1.99 | 0 | 0 | 20 | 20 |
| None | 1 | 4 | 1.403 | 1.24–1.57 | 0 | 2 | 2 | 0 |
| False | 0 | 12 | 0.059 | 0.01–0.24 | 12 | 0 | 0 | 0 |

**Cobertura × erro por confiança do Score** (acerto = arredondamento igual ao gabarito)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.056 | 36 |
| 0.300 | 1.000 | 0.056 | 36 |
| 0.500 | 0.944 | 0.000 | 34 |
| 0.700 | 0.861 | 0.000 | 31 |
| 0.900 | 0.500 | 0.000 | 18 |

**O Score acrescenta algo aos Nouls?** Na política ele só pode tirar uma união. Mudou a decisão dos Nouls em 0 par(es): 0 união(ões) sem prova evitada(s), 0 união(ões) certa(s) mandada(s) a `revisar`. Sozinho (arredondamento): 0 diferente(s) e 2 indecidível(is) unidos, 0 duplicata(s) separada(s), acerto 0.950; só Nouls: 0, 0, 0, acerto 1.000.

### Por família (pela `nota` do rotulador)

| família | gabarito | n | ação Jev | ação baseline | Jev → revisar | sem chamada (código) | erro caro Jev | erro caro baseline |
|---|---|---|---|---|---|---|---|---|
| anúncio sem endereço | True | 2 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| descrição copiada com pequenas mudanças | True | 3 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| detalhe fixo contradiz | False | 4 | 1.000 | 0.000 | 0 | 0 | 0 | 4 |
| mesma rua, prédios diferentes | False | 2 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| mesmo bairro e números parecidos | False | 3 | 1.000 | 0.000 | 0 | 0 | 0 | 3 |
| mobiliado só num | True | 3 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| mobiliado × vazio | None | 1 | 1.000 | 0.000 | 1 | 0 | 0 | 0 |
| preço reajustado | True | 4 | 1.000 | 0.000 | 0 | 0 | 0 | 4 |
| sem detalhe distintivo | None | 3 | 1.000 | 0.000 | 3 | 0 | 0 | 3 |
| texto reaproveitado | False | 1 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| unidade diferente | False | 4 | 1.000 | 1.000 | 0 | 2 | 0 | 0 |
| área útil × total | True | 3 | 1.000 | 0.000 | 0 | 0 | 0 | 3 |
| fácil: bairros/cidades diferentes | False | 2 | 1.000 | 1.000 | 0 | 2 | 0 | 0 |
| fácil: dois corretores, mesmo imóvel | True | 5 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |

### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)

`cobertura_auto` = par que não foi a `revisar` (inclui os decididos pelo código sem chamada). **Vetos** (a mesma faixa em `address_conflict`, `layout_contradiction` e `fixed_contradiction`):

| faixa (3 vetos) | cobertura_auto | erro_automatico | diferentes unidos | indecidíveis unidos | duplicatas separadas | duplicatas unidas | n_auto |
|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| 0.5–0.5 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| 0.4–0.6 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| 0.3–0.7 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| 0.2–0.8 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| 0.1–0.9 | 0.800 | 0.000 | 0 | 0 | 0 | 20 | 32 |
| 0.05–0.95 | 0.725 | 0.000 | 0 | 0 | 0 | 18 | 29 |

**O que autoriza a união** (um parâmetro por vez, o resto como em `perguntas.py`):

| parâmetro | valor | cobertura_auto | erro_automatico | diferentes unidos | indecidíveis unidos | duplicatas separadas | duplicatas unidas | n_auto |
|---|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | — | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| `sim` do sinal forte | 0.500 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| `sim` do sinal forte | 0.700 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| `sim` do sinal forte | 0.800 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| `sim` do sinal forte | 0.900 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| Score mínimo para unir | sem Score | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| Score mínimo para unir | 1.000 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| Score mínimo para unir | 1.500 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| Score mínimo para unir | 1.700 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| Score mínimo para unir | 1.800 | 0.900 | 0.000 | 0 | 0 | 0 | 20 | 36 |
| Score mínimo para unir | 1.900 | 0.825 | 0.000 | 0 | 0 | 0 | 17 | 33 |

### Custo e latência (medidos na chamada real; do cache também)

| pares | requisicoes | novas (não cache) | sem chamada (código decide) | longos (sem chamada) | falhas operacionais (→ revisar) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_par | US$_por_1000_pares | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | 36 | 0 | 4 | 0 | 0 | 252 | 286 | 332 | 1794 | 0.002712 | 0.0000678 | 0.0678 | jev-1.13.0 |

### Caso a caso

`end`/`conf` = Nouls `same_building_or_street` e `address_conflict`; `planta` = `layout_contradiction`; `fixo` = `fixed_contradiction`; `estado` = `state_contradiction`; `comum` = `shared_distinctive_details`; `score` = `same_listing` (confiança); `área`/`preço` = fatos do código (`expl.` = fora de ±3% mas conciliada por outra metragem do texto); `ok` compara a ação do Jev com o gabarito; `caro` marca o erro caro; `base` = baseline; `—` = par decidido pelo código sem chamada.

| id | fam | gab | end | conf | planta | fixo | estado | comum | score | área | preço | ação Jev | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ID-A001 | anúncio sem endereço | unir | 0.08 | 0.08 | 0.02 | 0.03 | 0.03 | 0.96 | 1.95 (0.92) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A002 | mesmo bairro e números parecidos | manter_separados | 0.03 | 0.95 | 0.08 | 0.10 | 0.07 | 0.08 | 0.09 (0.86) | ok | ok | manter_separados | ✓ |  | unir | prédios ou ruas diferentes |
| ID-A003 | área útil × total | unir | 0.98 | 0.02 | 0.02 | 0.03 | 0.02 | 0.95 | 1.97 (0.95) | expl. | ok | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-A004 | mobiliado só num | unir | 0.96 | 0.04 | 0.02 | 0.03 | 0.06 | 0.95 | 1.85 (0.77) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A005 | descrição copiada com pequenas mudanças | unir | 0.99 | 0.01 | 0.02 | 0.02 | 0.02 | 0.97 | 1.98 (0.97) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A006 | preço reajustado | unir | 0.95 | 0.04 | 0.02 | 0.03 | 0.03 | 0.95 | 1.92 (0.87) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-A007 | detalhe fixo contradiz | manter_separados | 0.97 | 0.03 | 0.02 | 0.88 | 0.20 | 0.94 | 0.24 (0.64) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-A008 | sem detalhe distintivo | revisar | 0.98 | 0.02 | 0.03 | 0.03 | 0.03 | 0.15 | 1.57 (0.36) | ok | ok | revisar | ✓ |  | unir | sem detalhe distintivo em comum (0.15) |
| ID-A009 | preço reajustado | unir | 0.96 | 0.03 | 0.03 | 0.03 | 0.03 | 0.96 | 1.94 (0.91) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-A010 | área útil × total | unir | 0.98 | 0.02 | 0.02 | 0.06 | 0.03 | 0.94 | 1.99 (0.99) | expl. | ok | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-A011 | texto reaproveitado | manter_separados | 0.02 | 0.98 | 0.02 | 0.05 | 0.02 | 0.93 | 0.01 (0.99) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-A012 | fácil: dois corretores, mesmo imóvel | unir | 0.96 | 0.03 | 0.02 | 0.03 | 0.03 | 0.96 | 1.92 (0.88) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A013 | detalhe fixo contradiz | manter_separados | 0.97 | 0.02 | 0.05 | 0.86 | 0.92 | 0.66 | 0.07 (0.89) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-A014 | descrição copiada com pequenas mudanças | unir | 0.99 | 0.02 | 0.02 | 0.02 | 0.02 | 0.94 | 1.96 (0.94) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A015 | fácil: bairros/cidades diferentes | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | bairro ou cidade diferentes (código) |
| ID-A016 | mobiliado só num | unir | 0.97 | 0.03 | 0.02 | 0.03 | 0.04 | 0.95 | 1.92 (0.88) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A017 | sem detalhe distintivo | revisar | 0.06 | 0.16 | 0.03 | 0.03 | 0.03 | 0.11 | 1.24 (0.60) | ok | ok | revisar | ✓ |  | unir | sem detalhe distintivo em comum (0.11) |
| ID-A018 | detalhe fixo contradiz | manter_separados | 0.97 | 0.03 | 0.02 | 0.89 | 0.06 | 0.88 | 0.10 (0.85) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-A019 | unidade diferente | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | quartos ou vagas diferentes: outra planta (código) |
| ID-A020 | unidade diferente | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | quartos ou vagas diferentes: outra planta (código) |
| ID-A021 | mobiliado só num | unir | 0.96 | 0.03 | 0.02 | 0.04 | 0.07 | 0.97 | 1.83 (0.75) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A022 | mesma rua, prédios diferentes | manter_separados | 0.14 | 0.97 | 0.07 | 0.11 | 0.05 | 0.07 | 0.04 (0.94) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-A023 | preço reajustado | unir | 0.98 | 0.02 | 0.02 | 0.02 | 0.02 | 0.95 | 1.98 (0.98) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-A024 | unidade diferente | manter_separados | 0.95 | 0.04 | 0.88 | 0.70 | 0.87 | 0.16 | 0.04 (0.93) | ok | ✗ | manter_separados | ✓ |  | manter_separados | planta contradiz (cômodo estrutural); detalhe fixo contradiz |
| ID-A025 | fácil: bairros/cidades diferentes | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | bairro ou cidade diferentes (código) |
| ID-A026 | área útil × total | unir | 0.97 | 0.04 | 0.02 | 0.03 | 0.03 | 0.95 | 1.97 (0.96) | expl. | ok | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-A027 | fácil: dois corretores, mesmo imóvel | unir | 0.97 | 0.03 | 0.02 | 0.02 | 0.02 | 0.94 | 1.98 (0.97) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A028 | fácil: dois corretores, mesmo imóvel | unir | 0.96 | 0.03 | 0.02 | 0.03 | 0.02 | 0.94 | 1.83 (0.74) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A029 | mesma rua, prédios diferentes | manter_separados | 0.19 | 0.96 | 0.08 | 0.12 | 0.04 | 0.07 | 0.02 (0.98) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-A030 | descrição copiada com pequenas mudanças | unir | 0.99 | 0.02 | 0.02 | 0.02 | 0.03 | 0.96 | 1.90 (0.85) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A031 | detalhe fixo contradiz | manter_separados | 0.98 | 0.03 | 0.03 | 0.90 | 0.35 | 0.95 | 0.02 (0.96) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-A032 | mesmo bairro e números parecidos | manter_separados | 0.03 | 0.97 | 0.06 | 0.08 | 0.04 | 0.06 | 0.05 (0.92) | ok | ok | manter_separados | ✓ |  | unir | prédios ou ruas diferentes |
| ID-A033 | mobiliado × vazio | revisar | 0.95 | 0.06 | 0.02 | 0.07 | 0.96 | 0.96 | 1.25 (0.51) | ok | ✗ | revisar | ✓ |  | manter_separados | estado ou mobília opostos (0.96): mesma unidade em outro momento ou a vizinha |
| ID-A034 | anúncio sem endereço | unir | 0.07 | 0.05 | 0.02 | 0.02 | 0.02 | 0.96 | 1.91 (0.87) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A035 | mesmo bairro e números parecidos | manter_separados | 0.02 | 0.97 | 0.08 | 0.10 | 0.06 | 0.27 | 0.01 (0.98) | ok | ok | manter_separados | ✓ |  | unir | prédios ou ruas diferentes |
| ID-A036 | fácil: dois corretores, mesmo imóvel | unir | 0.95 | 0.03 | 0.02 | 0.02 | 0.02 | 0.92 | 1.92 (0.89) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A037 | fácil: dois corretores, mesmo imóvel | unir | 0.95 | 0.03 | 0.02 | 0.04 | 0.02 | 0.96 | 1.90 (0.85) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-A038 | unidade diferente | manter_separados | 0.97 | 0.03 | 0.98 | 0.67 | 0.94 | 0.12 | 0.02 (0.96) | ok | ✗ | manter_separados | ✓ |  | manter_separados | planta contradiz (cômodo estrutural) |
| ID-A039 | preço reajustado | unir | 0.97 | 0.03 | 0.02 | 0.04 | 0.04 | 0.96 | 1.93 (0.90) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-A040 | sem detalhe distintivo | revisar | 0.97 | 0.03 | 0.03 | 0.03 | 0.03 | 0.12 | 1.55 (0.33) | ok | ok | revisar | ✓ |  | unir | sem detalhe distintivo em comum (0.12) |

## Conjunto `teste` — 80 pares (arquivo versão 2026-10-01, autor fable); 40 duplicatas, 32 diferentes, 8 indecidíveis; 66 difíceis

### Ação (3 classes) — métrica principal, baseline × sempre revisa × Jev nos mesmos pares

Gabarito da ação: `mesmo_imovel` true → `unir`; false → `manter_separados`; null → `revisar`. **DIFERENTE UNIDO** = par de imóveis diferentes que saiu `unir` (a união apagaria um imóvel do catálogo). `indecidível unido` = gabarito `null` que saiu `unir` (união sem prova). **DUPLICATA SEPARADA** = mesmo imóvel que saiu `manter_separados` (a duplicata fica e ninguém revisa). `baseline` = mesmos bairro/cidade + quartos + vagas + área ±3% + preço ±5% ⇒ unir, senão separados. `sempre revisa` = zero erro caro, 100% dos pares a humano. `só Score` = arredondamento do Score (cortes 0,5 e 1,5), como na receita; `só Nouls` = política sem o Score; `Jev (política)` = Nouls + Score como segunda leitura da união. As três leem a MESMA resposta.

| variante | n | acerto_acao | DIFERENTE UNIDO (apagaria um imóvel) | indecidível unido | DUPLICATA SEPARADA | duplicata unida | null → revisar | revisou sem necessidade |
|---|---|---|---|---|---|---|---|---|
| baseline (4 sinais) | 80 | 0.550 | 14/32 | 6/8 | 14/40 | 26/40 | 0/8 | 0/72 |
| sempre revisa | 80 | 0.100 | 0/32 | 0/8 | 0/40 | 0/40 | 8/8 | 72/72 |
| só Score | 80 | 0.938 | 0/32 | 5/8 | 0/40 | 40/40 | 3/8 | 0/72 |
| só Nouls | 80 | 0.975 | 0/32 | 0/8 | 0/40 | 40/40 | 8/8 | 2/72 |
| Jev (política) | 80 | 0.963 | 0/32 | 0/8 | 0/40 | 39/40 | 8/8 | 3/72 |

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 diferente unido | 0/32 | ≤ 0 | ✓ |
| 2 indecidível unido | 0/8 | ≤ 1 | ✓ |
| 3 duplicata separada | 0/40 (0.000) | ≤ 0.05 | ✓ |
| 4 acerto da ação | 0.963 (baseline 0.550) | ≥ 0.700 | ✓ |
| secundário: nulo → revisar | 8/8 | todos | ✓ |
| secundário: revisou sem necessidade | 3/72 (0.042) | ≤ 0.15 | ✓ |
| secundário: sinais numéricos do código | 100% | 100% (senão é bug) | ✓ |

**Matriz de confusão — Jev (política)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 39 | 1 | 0 |
| revisar | 0 | 8 | 0 |
| manter_separados | 0 | 2 | 30 |

**Matriz de confusão — só Nouls** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 40 | 0 | 0 |
| revisar | 0 | 8 | 0 |
| manter_separados | 0 | 2 | 30 |

**Matriz de confusão — só Score** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 40 | 0 | 0 |
| revisar | 5 | 3 | 0 |
| manter_separados | 0 | 0 | 32 |

**Matriz de confusão — baseline (4 sinais)** (linhas = gabarito, colunas = previsto)

| gabarito ↓ / previsto → | unir | revisar | manter_separados |
|---|---|---|---|
| unir | 26 | 0 | 14 |
| revisar | 6 | 0 | 2 |
| manter_separados | 14 | 0 | 18 |

**Erros caros, par a par** (todas as variantes)

| id | variante | erro | família |
|---|---|---|---|
| ID-T024 | só Score | indecidível unido | sem detalhe distintivo |
| ID-T050 | só Score | indecidível unido | sem detalhe distintivo |
| ID-T063 | só Score | indecidível unido | sem detalhe distintivo |
| ID-T071 | só Score | indecidível unido | sem detalhe distintivo |
| ID-T079 | só Score | indecidível unido | sem detalhe distintivo |
| ID-T004 | baseline (4 sinais) | DIFERENTE UNIDO | mesmo bairro e números parecidos |
| ID-T005 | baseline (4 sinais) | DUPLICATA SEPARADA | área útil × total |
| ID-T008 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-T010 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-T014 | baseline (4 sinais) | indecidível unido | sem detalhe distintivo |
| ID-T015 | baseline (4 sinais) | DUPLICATA SEPARADA | área útil × total |
| ID-T017 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-T018 | baseline (4 sinais) | DIFERENTE UNIDO | mesmo bairro e números parecidos |
| ID-T021 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-T024 | baseline (4 sinais) | indecidível unido | sem detalhe distintivo |
| ID-T026 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-T029 | baseline (4 sinais) | DUPLICATA SEPARADA | área útil × total |
| ID-T030 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-T033 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-T034 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-T036 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-T043 | baseline (4 sinais) | DIFERENTE UNIDO | mesmo bairro e números parecidos |
| ID-T045 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-T046 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-T048 | baseline (4 sinais) | DIFERENTE UNIDO | mesmo bairro e números parecidos |
| ID-T050 | baseline (4 sinais) | indecidível unido | sem detalhe distintivo |
| ID-T053 | baseline (4 sinais) | DUPLICATA SEPARADA | área útil × total |
| ID-T058 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-T060 | baseline (4 sinais) | DUPLICATA SEPARADA | área útil × total |
| ID-T063 | baseline (4 sinais) | indecidível unido | sem detalhe distintivo |
| ID-T064 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-T066 | baseline (4 sinais) | DIFERENTE UNIDO | detalhe fixo contradiz |
| ID-T071 | baseline (4 sinais) | indecidível unido | sem detalhe distintivo |
| ID-T073 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-T074 | baseline (4 sinais) | DIFERENTE UNIDO | mesmo bairro e números parecidos |
| ID-T075 | baseline (4 sinais) | DUPLICATA SEPARADA | área útil × total |
| ID-T076 | baseline (4 sinais) | DIFERENTE UNIDO | unidade diferente |
| ID-T078 | baseline (4 sinais) | DUPLICATA SEPARADA | preço reajustado |
| ID-T079 | baseline (4 sinais) | indecidível unido | sem detalhe distintivo |

### Sinais numéricos do código — têm de bater 100% com o gabarito (senão é bug)

| sinal | certos | ok |
|---|---|---|
| `mesma_area` (±3%) | 80/80 | ✓ |
| `mesmo_preco` (±5%) | 80/80 | ✓ |
| quartos ou vagas diferentes ⇒ `mesma_planta` false | 6/6 | ✓ |
| decidido pelo código sem chamada (bairro/cidade, quartos ou vagas) ⇒ gabarito false | 7/7 | ✓ |

Área fora da tolerância entre os pares que foram ao Jev: 13; conciliada pelo código por outra metragem citada no texto: 6 (destes, duplicatas reais: 6).

### Sinais de texto (Nouls) contra os `sinais` do gabarito — 73 pares que foram ao Jev

`mesmo_endereco` tem três valores (true / false / `null` = um dos anúncios não cita prédio nem rua): `same_building_or_street` mede o true, `address_conflict` mede o false. `mesma_planta` false, entre os pares que chegam ao Jev (quartos e vagas iguais), é `layout_contradiction`. Acerto com corte 0,5; `cobertura` = fração decidida fora da faixa de dúvida; `revisao` = casos dentro dela.

| noul | positivos | acerto | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|---|
| same_building_or_street | 55 | 1.000 | 0.2–0.8 | 0.973 | 1.000 | 2 | 73 | 0.004 |
| address_conflict | 12 | 1.000 | 0.2–0.7 | 0.973 | 1.000 | 2 | 73 | 0.003 |
| layout_contradiction | 5 | 1.000 | 0.2–0.7 | 1.000 | 1.000 | 0 | 73 | 0.001 |

**`mesmo_endereco` em três valores** (os dois Nouls juntos, corte 0,5): 73/73 certos

| gabarito ↓ / previsto → | True | False | None |
|---|---|---|---|
| True | 55 | 0 | 0 |
| False | 0 | 12 | 0 |
| None | 0 | 0 | 6 |

**`mesma_planta` composta** (quartos e vagas iguais pelo CÓDIGO e nenhum cômodo estrutural contradito pelo Noul; par decidido pelo código sem chamada entra só com a parte do código): 1.000 (n = 80)

### Nouls sem campo próprio no gabarito — valores por grupo

| noul | grupo | n_grupo | mín–máx no grupo | grupo ≥ sim | grupo ≤ nao | mín–máx fora | fora ≥ sim | fora ≤ nao | faixa |
|---|---|---|---|---|---|---|---|---|---|
| fixed_contradiction | família detalhe fixo contradiz | 8 | 0.56–0.95 | 6 | 0 | 0.02–0.72 | 2 | 60 | 0.2–0.7 |
| state_contradiction | família mobiliado × vazio | 2 | 0.97–0.97 | 2 | 0 | 0.02–0.95 | 11 | 58 | 0.2–0.8 |
| shared_distinctive_details | duplicatas reais (true) | 40 | 0.91–0.97 | 40 | 0 | 0.05–0.97 | 9 | 13 | 0.2–0.8 |
| shared_distinctive_details | família sem detalhe distintivo | 6 | 0.05–0.26 | 0 | 4 | 0.07–0.97 | 49 | 9 | 0.2–0.8 |

### Score `same_listing` (0 = diferentes · 1 = não dá para saber · 2 = a mesma unidade)

| gabarito `mesmo_imovel` | esperado | n | média | mín–máx | → 0 (≤ 0,5) | → 1 | → 2 (≥ 1,5) | ≥ 1.7 (mínimo da política) |
|---|---|---|---|---|---|---|---|---|
| True | 2 | 40 | 1.911 | 1.59–1.99 | 0 | 0 | 40 | 39 |
| None | 1 | 8 | 1.438 | 1.14–1.75 | 0 | 3 | 5 | 1 |
| False | 0 | 25 | 0.079 | 0.01–0.24 | 25 | 0 | 0 | 0 |

**Cobertura × erro por confiança do Score** (acerto = arredondamento igual ao gabarito)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.068 | 73 |
| 0.300 | 0.959 | 0.029 | 70 |
| 0.500 | 0.918 | 0.015 | 67 |
| 0.700 | 0.808 | 0.000 | 59 |
| 0.900 | 0.534 | 0.000 | 39 |

**O Score acrescenta algo aos Nouls?** Na política ele só pode tirar uma união. Mudou a decisão dos Nouls em 1 par(es): 0 união(ões) sem prova evitada(s), 1 união(ões) certa(s) mandada(s) a `revisar` (ID-T006). Sozinho (arredondamento): 0 diferente(s) e 5 indecidível(is) unidos, 0 duplicata(s) separada(s), acerto 0.938; só Nouls: 0, 0, 0, acerto 0.975.

### Por família (pela `nota` do rotulador)

| família | gabarito | n | ação Jev | ação baseline | Jev → revisar | sem chamada (código) | erro caro Jev | erro caro baseline |
|---|---|---|---|---|---|---|---|---|
| anúncio sem endereço | True | 4 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| descrição copiada com pequenas mudanças | True | 6 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| detalhe fixo contradiz | False | 8 | 0.750 | 0.000 | 2 | 0 | 0 | 8 |
| mesma rua, prédios diferentes | False | 4 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| mesmo bairro e números parecidos | False | 5 | 1.000 | 0.000 | 0 | 0 | 0 | 5 |
| mobiliado só num | True | 6 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| mobiliado × vazio | None | 2 | 1.000 | 0.000 | 2 | 0 | 0 | 0 |
| preço reajustado | True | 8 | 1.000 | 0.000 | 0 | 0 | 0 | 8 |
| sem detalhe distintivo | None | 6 | 1.000 | 0.000 | 6 | 0 | 0 | 6 |
| texto reaproveitado | False | 3 | 1.000 | 1.000 | 0 | 0 | 0 | 0 |
| unidade diferente | False | 8 | 1.000 | 0.875 | 0 | 3 | 0 | 1 |
| área útil × total | True | 6 | 1.000 | 0.000 | 0 | 0 | 0 | 6 |
| fácil: bairros/cidades diferentes | False | 4 | 1.000 | 1.000 | 0 | 4 | 0 | 0 |
| fácil: dois corretores, mesmo imóvel | True | 10 | 0.900 | 1.000 | 1 | 0 | 0 | 0 |

### Cobertura × erro por limiar (mesmas respostas, zero chamada nova; informativo no teste)

`cobertura_auto` = par que não foi a `revisar` (inclui os decididos pelo código sem chamada). **Vetos** (a mesma faixa em `address_conflict`, `layout_contradiction` e `fixed_contradiction`):

| faixa (3 vetos) | cobertura_auto | erro_automatico | diferentes unidos | indecidíveis unidos | duplicatas separadas | duplicatas unidas | n_auto |
|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | 0.863 | 0.000 | 0 | 0 | 0 | 39 | 69 |
| 0.5–0.5 | 0.887 | 0.000 | 0 | 0 | 0 | 39 | 71 |
| 0.4–0.6 | 0.875 | 0.000 | 0 | 0 | 0 | 39 | 70 |
| 0.3–0.7 | 0.863 | 0.000 | 0 | 0 | 0 | 39 | 69 |
| 0.2–0.8 | 0.850 | 0.000 | 0 | 0 | 0 | 39 | 68 |
| 0.1–0.9 | 0.800 | 0.000 | 0 | 0 | 0 | 38 | 64 |
| 0.05–0.95 | 0.662 | 0.000 | 0 | 0 | 0 | 30 | 53 |

**O que autoriza a união** (um parâmetro por vez, o resto como em `perguntas.py`):

| parâmetro | valor | cobertura_auto | erro_automatico | diferentes unidos | indecidíveis unidos | duplicatas separadas | duplicatas unidas | n_auto |
|---|---|---|---|---|---|---|---|---|
| atual (perguntas.py) | — | 0.863 | 0.000 | 0 | 0 | 0 | 39 | 69 |
| `sim` do sinal forte | 0.500 | 0.863 | 0.000 | 0 | 0 | 0 | 39 | 69 |
| `sim` do sinal forte | 0.700 | 0.863 | 0.000 | 0 | 0 | 0 | 39 | 69 |
| `sim` do sinal forte | 0.800 | 0.863 | 0.000 | 0 | 0 | 0 | 39 | 69 |
| `sim` do sinal forte | 0.900 | 0.863 | 0.000 | 0 | 0 | 0 | 39 | 69 |
| Score mínimo para unir | sem Score | 0.875 | 0.000 | 0 | 0 | 0 | 40 | 70 |
| Score mínimo para unir | 1.000 | 0.875 | 0.000 | 0 | 0 | 0 | 40 | 70 |
| Score mínimo para unir | 1.500 | 0.875 | 0.000 | 0 | 0 | 0 | 40 | 70 |
| Score mínimo para unir | 1.700 | 0.863 | 0.000 | 0 | 0 | 0 | 39 | 69 |
| Score mínimo para unir | 1.800 | 0.812 | 0.000 | 0 | 0 | 0 | 35 | 65 |
| Score mínimo para unir | 1.900 | 0.762 | 0.000 | 0 | 0 | 0 | 31 | 61 |

### Custo e latência (medidos na chamada real; do cache também)

| pares | requisicoes | novas (não cache) | sem chamada (código decide) | longos (sem chamada) | falhas operacionais (→ revisar) | perguntas | p50_ms | p95_ms | tokens_por_requisicao | US$_total | US$_por_par | US$_por_1000_pares | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 | 73 | 73 | 7 | 0 | 0 | 511 | 273 | 404 | 1785 | 0.005473 | 0.0000684 | 0.0684 | jev-1.13.0 |

### Caso a caso

`end`/`conf` = Nouls `same_building_or_street` e `address_conflict`; `planta` = `layout_contradiction`; `fixo` = `fixed_contradiction`; `estado` = `state_contradiction`; `comum` = `shared_distinctive_details`; `score` = `same_listing` (confiança); `área`/`preço` = fatos do código (`expl.` = fora de ±3% mas conciliada por outra metragem do texto); `ok` compara a ação do Jev com o gabarito; `caro` marca o erro caro; `base` = baseline; `—` = par decidido pelo código sem chamada.

| id | fam | gab | end | conf | planta | fixo | estado | comum | score | área | preço | ação Jev | ok | caro | base | motivo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ID-T001 | fácil: dois corretores, mesmo imóvel | unir | 0.96 | 0.03 | 0.02 | 0.02 | 0.02 | 0.97 | 1.94 (0.91) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T002 | unidade diferente | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | quartos ou vagas diferentes: outra planta (código) |
| ID-T003 | mobiliado só num | unir | 0.96 | 0.06 | 0.02 | 0.04 | 0.08 | 0.96 | 1.74 (0.60) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T004 | mesmo bairro e números parecidos | manter_separados | 0.03 | 0.97 | 0.08 | 0.11 | 0.05 | 0.37 | 0.03 (0.95) | ok | ok | manter_separados | ✓ |  | unir | prédios ou ruas diferentes |
| ID-T005 | área útil × total | unir | 0.98 | 0.02 | 0.07 | 0.04 | 0.03 | 0.91 | 1.97 (0.96) | expl. | ok | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T006 | fácil: dois corretores, mesmo imóvel | unir | 0.95 | 0.05 | 0.03 | 0.05 | 0.06 | 0.94 | 1.59 (0.39) | ok | ok | revisar | ✗ |  | unir | Nouls dizem unir, Score não confirma (1.59) |
| ID-T007 | unidade diferente | manter_separados | 0.95 | 0.03 | 0.98 | 0.67 | 0.95 | 0.22 | 0.02 (0.97) | ok | ✗ | manter_separados | ✓ |  | manter_separados | planta contradiz (cômodo estrutural) |
| ID-T008 | detalhe fixo contradiz | manter_separados | 0.97 | 0.03 | 0.03 | 0.56 | 0.91 | 0.74 | 0.24 (0.64) | ok | ok | revisar | ✗ |  | unir | dúvida: detalhe fixo contradiz? (0.56) |
| ID-T009 | fácil: dois corretores, mesmo imóvel | unir | 0.97 | 0.03 | 0.02 | 0.02 | 0.02 | 0.96 | 1.95 (0.93) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T010 | detalhe fixo contradiz | manter_separados | 0.97 | 0.03 | 0.02 | 0.95 | 0.92 | 0.95 | 0.01 (0.98) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-T011 | anúncio sem endereço | unir | 0.08 | 0.06 | 0.02 | 0.03 | 0.02 | 0.95 | 1.93 (0.89) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T012 | anúncio sem endereço | unir | 0.09 | 0.08 | 0.02 | 0.03 | 0.02 | 0.95 | 1.87 (0.81) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T013 | fácil: bairros/cidades diferentes | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | bairro ou cidade diferentes (código) |
| ID-T014 | sem detalhe distintivo | revisar | 0.08 | 0.25 | 0.03 | 0.03 | 0.04 | 0.09 | 1.14 (0.73) | ok | ok | revisar | ✓ |  | unir | dúvida: prédios ou ruas diferentes? (0.25) |
| ID-T015 | área útil × total | unir | 0.98 | 0.02 | 0.02 | 0.03 | 0.03 | 0.96 | 1.98 (0.97) | expl. | ok | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T016 | descrição copiada com pequenas mudanças | unir | 0.98 | 0.03 | 0.02 | 0.02 | 0.02 | 0.97 | 1.92 (0.89) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T017 | detalhe fixo contradiz | manter_separados | 0.95 | 0.04 | 0.03 | 0.84 | 0.82 | 0.66 | 0.05 (0.92) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-T018 | mesmo bairro e números parecidos | manter_separados | 0.03 | 0.97 | 0.07 | 0.05 | 0.04 | 0.08 | 0.07 (0.90) | ok | ok | manter_separados | ✓ |  | unir | prédios ou ruas diferentes |
| ID-T019 | texto reaproveitado | manter_separados | 0.02 | 0.96 | 0.02 | 0.04 | 0.02 | 0.95 | 0.03 (0.96) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-T020 | fácil: dois corretores, mesmo imóvel | unir | 0.97 | 0.02 | 0.02 | 0.02 | 0.02 | 0.96 | 1.96 (0.93) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T021 | detalhe fixo contradiz | manter_separados | 0.96 | 0.03 | 0.02 | 0.74 | 0.74 | 0.88 | 0.18 (0.73) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-T022 | descrição copiada com pequenas mudanças | unir | 0.99 | 0.02 | 0.02 | 0.02 | 0.02 | 0.97 | 1.93 (0.89) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T023 | unidade diferente | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | quartos ou vagas diferentes: outra planta (código) |
| ID-T024 | sem detalhe distintivo | revisar | 0.09 | 0.22 | 0.03 | 0.03 | 0.03 | 0.06 | 1.50 (0.26) | ok | ok | revisar | ✓ |  | unir | dúvida: prédios ou ruas diferentes? (0.22) |
| ID-T025 | unidade diferente | manter_separados | 0.96 | 0.04 | 0.98 | 0.42 | 0.90 | 0.18 | 0.06 (0.92) | ok | ✗ | manter_separados | ✓ |  | manter_separados | planta contradiz (cômodo estrutural) |
| ID-T026 | preço reajustado | unir | 0.92 | 0.09 | 0.02 | 0.03 | 0.03 | 0.92 | 1.86 (0.79) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T027 | descrição copiada com pequenas mudanças | unir | 0.99 | 0.01 | 0.02 | 0.02 | 0.02 | 0.97 | 1.94 (0.91) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T028 | texto reaproveitado | manter_separados | 0.02 | 0.99 | 0.02 | 0.07 | 0.03 | 0.96 | 0.01 (0.99) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-T029 | área útil × total | unir | 0.97 | 0.02 | 0.02 | 0.03 | 0.03 | 0.94 | 1.98 (0.97) | expl. | ok | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T030 | preço reajustado | unir | 0.93 | 0.10 | 0.02 | 0.03 | 0.03 | 0.95 | 1.78 (0.66) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T031 | fácil: dois corretores, mesmo imóvel | unir | 0.97 | 0.02 | 0.02 | 0.02 | 0.02 | 0.93 | 1.96 (0.93) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T032 | unidade diferente | manter_separados | 0.96 | 0.03 | 0.98 | 0.70 | 0.93 | 0.24 | 0.02 (0.96) | ok | ✗ | manter_separados | ✓ |  | manter_separados | planta contradiz (cômodo estrutural); detalhe fixo contradiz |
| ID-T033 | preço reajustado | unir | 0.97 | 0.03 | 0.02 | 0.03 | 0.03 | 0.93 | 1.91 (0.87) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T034 | detalhe fixo contradiz | manter_separados | 0.95 | 0.04 | 0.04 | 0.92 | 0.92 | 0.76 | 0.03 (0.96) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-T035 | mobiliado só num | unir | 0.96 | 0.02 | 0.02 | 0.03 | 0.04 | 0.96 | 1.95 (0.92) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T036 | detalhe fixo contradiz | manter_separados | 0.98 | 0.02 | 0.02 | 0.86 | 0.67 | 0.96 | 0.15 (0.77) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-T037 | anúncio sem endereço | unir | 0.09 | 0.09 | 0.02 | 0.02 | 0.03 | 0.96 | 1.94 (0.92) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T038 | mesma rua, prédios diferentes | manter_separados | 0.25 | 0.95 | 0.07 | 0.07 | 0.04 | 0.14 | 0.13 (0.81) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-T039 | fácil: dois corretores, mesmo imóvel | unir | 0.96 | 0.02 | 0.02 | 0.02 | 0.02 | 0.95 | 1.96 (0.94) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T040 | descrição copiada com pequenas mudanças | unir | 0.98 | 0.02 | 0.02 | 0.02 | 0.02 | 0.95 | 1.95 (0.92) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T041 | mesma rua, prédios diferentes | manter_separados | 0.14 | 0.94 | 0.07 | 0.07 | 0.04 | 0.07 | 0.24 (0.63) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-T042 | mobiliado × vazio | revisar | 0.98 | 0.03 | 0.02 | 0.05 | 0.97 | 0.96 | 1.25 (0.51) | ok | ✗ | revisar | ✓ |  | manter_separados | estado ou mobília opostos (0.97): mesma unidade em outro momento ou a vizinha |
| ID-T043 | mesmo bairro e números parecidos | manter_separados | 0.03 | 0.97 | 0.08 | 0.08 | 0.06 | 0.21 | 0.01 (0.98) | ok | ok | manter_separados | ✓ |  | unir | prédios ou ruas diferentes |
| ID-T044 | descrição copiada com pequenas mudanças | unir | 0.98 | 0.02 | 0.02 | 0.02 | 0.02 | 0.96 | 1.91 (0.87) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T045 | preço reajustado | unir | 0.96 | 0.03 | 0.02 | 0.03 | 0.03 | 0.91 | 1.91 (0.86) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T046 | preço reajustado | unir | 0.98 | 0.02 | 0.02 | 0.03 | 0.03 | 0.95 | 1.96 (0.94) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T047 | mobiliado × vazio | revisar | 0.97 | 0.04 | 0.02 | 0.06 | 0.97 | 0.97 | 1.21 (0.46) | ok | ✗ | revisar | ✓ |  | manter_separados | estado ou mobília opostos (0.97): mesma unidade em outro momento ou a vizinha |
| ID-T048 | mesmo bairro e números parecidos | manter_separados | 0.03 | 0.97 | 0.08 | 0.06 | 0.05 | 0.14 | 0.03 (0.96) | ok | ok | manter_separados | ✓ |  | unir | prédios ou ruas diferentes |
| ID-T049 | fácil: bairros/cidades diferentes | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | bairro ou cidade diferentes (código) |
| ID-T050 | sem detalhe distintivo | revisar | 0.98 | 0.02 | 0.02 | 0.02 | 0.03 | 0.05 | 1.51 (0.27) | ok | ok | revisar | ✓ |  | unir | sem detalhe distintivo em comum (0.05) |
| ID-T051 | mobiliado só num | unir | 0.97 | 0.03 | 0.02 | 0.03 | 0.03 | 0.95 | 1.95 (0.92) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T052 | mesma rua, prédios diferentes | manter_separados | 0.26 | 0.97 | 0.07 | 0.11 | 0.05 | 0.07 | 0.06 (0.92) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-T053 | área útil × total | unir | 0.96 | 0.05 | 0.02 | 0.03 | 0.02 | 0.96 | 1.98 (0.98) | expl. | ok | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T054 | fácil: dois corretores, mesmo imóvel | unir | 0.94 | 0.04 | 0.02 | 0.03 | 0.03 | 0.93 | 1.91 (0.86) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T055 | fácil: dois corretores, mesmo imóvel | unir | 0.96 | 0.03 | 0.02 | 0.03 | 0.02 | 0.95 | 1.94 (0.91) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T056 | descrição copiada com pequenas mudanças | unir | 0.98 | 0.02 | 0.02 | 0.02 | 0.02 | 0.97 | 1.75 (0.63) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T057 | unidade diferente | manter_separados | 0.96 | 0.03 | 0.91 | 0.72 | 0.88 | 0.47 | 0.06 (0.91) | ok | ✗ | manter_separados | ✓ |  | manter_separados | planta contradiz (cômodo estrutural); detalhe fixo contradiz |
| ID-T058 | detalhe fixo contradiz | manter_separados | 0.98 | 0.02 | 0.03 | 0.66 | 0.82 | 0.83 | 0.17 (0.75) | ok | ok | revisar | ✗ |  | unir | dúvida: detalhe fixo contradiz? (0.66) |
| ID-T059 | fácil: dois corretores, mesmo imóvel | unir | 0.94 | 0.03 | 0.02 | 0.03 | 0.03 | 0.97 | 1.91 (0.87) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T060 | área útil × total | unir | 0.96 | 0.04 | 0.02 | 0.03 | 0.03 | 0.97 | 1.97 (0.95) | expl. | ok | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T061 | mobiliado só num | unir | 0.95 | 0.04 | 0.02 | 0.03 | 0.05 | 0.93 | 1.85 (0.77) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T062 | mesma rua, prédios diferentes | manter_separados | 0.20 | 0.96 | 0.07 | 0.11 | 0.05 | 0.07 | 0.08 (0.88) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-T063 | sem detalhe distintivo | revisar | 0.98 | 0.02 | 0.03 | 0.03 | 0.04 | 0.21 | 1.75 (0.63) | ok | ok | revisar | ✓ |  | unir | sem detalhe distintivo em comum (0.21) |
| ID-T064 | preço reajustado | unir | 0.97 | 0.03 | 0.02 | 0.03 | 0.04 | 0.96 | 1.92 (0.88) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T065 | fácil: dois corretores, mesmo imóvel | unir | 0.97 | 0.03 | 0.02 | 0.02 | 0.02 | 0.95 | 1.98 (0.97) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T066 | detalhe fixo contradiz | manter_separados | 0.96 | 0.03 | 0.02 | 0.87 | 0.84 | 0.79 | 0.20 (0.71) | ok | ok | manter_separados | ✓ |  | unir | detalhe fixo contradiz |
| ID-T067 | mobiliado só num | unir | 0.97 | 0.03 | 0.02 | 0.03 | 0.05 | 0.91 | 1.95 (0.92) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T068 | mobiliado só num | unir | 0.97 | 0.03 | 0.02 | 0.03 | 0.04 | 0.95 | 1.97 (0.95) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T069 | texto reaproveitado | manter_separados | 0.03 | 0.96 | 0.02 | 0.05 | 0.02 | 0.96 | 0.03 (0.96) | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | prédios ou ruas diferentes |
| ID-T070 | fácil: bairros/cidades diferentes | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | bairro ou cidade diferentes (código) |
| ID-T071 | sem detalhe distintivo | revisar | 0.98 | 0.02 | 0.03 | 0.03 | 0.03 | 0.06 | 1.63 (0.45) | ok | ok | revisar | ✓ |  | unir | sem detalhe distintivo em comum (0.06) |
| ID-T072 | unidade diferente | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | quartos ou vagas diferentes: outra planta (código) |
| ID-T073 | preço reajustado | unir | 0.97 | 0.03 | 0.02 | 0.03 | 0.03 | 0.97 | 1.76 (0.65) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T074 | mesmo bairro e números parecidos | manter_separados | 0.02 | 0.97 | 0.08 | 0.07 | 0.05 | 0.16 | 0.01 (0.99) | ok | ok | manter_separados | ✓ |  | unir | prédios ou ruas diferentes |
| ID-T075 | área útil × total | unir | 0.96 | 0.03 | 0.02 | 0.04 | 0.03 | 0.96 | 1.99 (0.98) | expl. | ok | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T076 | unidade diferente | manter_separados | 0.95 | 0.04 | 0.97 | 0.49 | 0.94 | 0.10 | 0.05 (0.93) | ok | ok | manter_separados | ✓ |  | unir | planta contradiz (cômodo estrutural) |
| ID-T077 | anúncio sem endereço | unir | 0.10 | 0.06 | 0.02 | 0.02 | 0.03 | 0.95 | 1.97 (0.95) | ok | ok | unir | ✓ |  | unir | mesmos detalhes da unidade, nenhuma contradição |
| ID-T078 | preço reajustado | unir | 0.94 | 0.12 | 0.02 | 0.04 | 0.03 | 0.97 | 1.87 (0.80) | ok | ✗ | unir | ✓ |  | manter_separados | mesmos detalhes da unidade, nenhuma contradição |
| ID-T079 | sem detalhe distintivo | revisar | 0.98 | 0.02 | 0.03 | 0.03 | 0.04 | 0.26 | 1.51 (0.26) | ok | ok | revisar | ✓ |  | unir | sem detalhe distintivo em comum (0.26) |
| ID-T080 | fácil: bairros/cidades diferentes | manter_separados | — | — | — | — | — | — | — | ✗ | ✗ | manter_separados | ✓ |  | manter_separados | bairro ou cidade diferentes (código) |
