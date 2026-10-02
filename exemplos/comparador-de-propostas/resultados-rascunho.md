# Rascunho — comparador-de-propostas (encanamento)

## Conjunto `rascunho` — 5 disputas, 15 propostas, 45 células (arquivo versão 2026-10-01, autor fable)

> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**

### Matriz, elegíveis e perguntas — Jev + código × baseline, por desenho

`acerto_semantico` = células semânticas (Jev, depois da válvula) × gabarito; `acerto_numerico` = células numéricas pelo código; `classe_*` = acerto dentro de cada classe do gabarito. Erros caros: `exclusao_aprovada` = gabarito contradiz → atende (`_bruto` = antes da válvula); `inelegivel_elegivel` = proposta com contradiz obrigatório no gabarito que entrou em `elegiveis`. Secundários: `descartou_sem_perguntar` = gabarito nao_informado → contradiz; `falso_alarme` = atende → contradiz; `elegivel_fora` = elegível do gabarito que ficou fora. `valvula` = abstenções: células cuja leitura dura (`bruto`: opção da Choice; Nouls com corte em 0,5) decidia e a válvula/faixa mandou para nao_informado; `cobertura` = o resto; `erro_decididos` = erro entre as não movidas. `perguntas_*` = nao_informado em obrigatório de proposta ELEGÍVEL (o que a saída pergunta ao fornecedor) × gabarito, cada lado filtrado pela própria elegibilidade. `baseline` = palavra-chave + marca de exclusão na mesma frase.

| desenho | n_sem | n_num | acerto_semantico | acerto_numerico | acerto_total | classe_atende | classe_contradiz | classe_nao_informado | exclusao_aprovada | exclusao_aprovada_bruto | descartou_sem_perguntar | falso_alarme | valvula | cobertura | erro_decididos | inelegivel_elegivel | elegivel_fora | elegiveis_exatos | perguntas_precisao | perguntas_recall | baseline_semantico | baseline_exclusao_aprovada | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| choice | 24 | 21 | 0.000 | 1.000 | 0.467 | 0.000 | 0.000 | nan | 0/7 | 0/7 | 0/0 | 0/17 | 0 | 1.000 | 1.000 | 3/8 | 0/7 | 0.400 | 0.000 | nan | 0.958 | 1/7 | 15 |
| nouls | 24 | 21 | 0.000 | 1.000 | 0.467 | 0.000 | 0.000 | nan | 0/7 | 0/7 | 0/0 | 0/17 | 0 | 1.000 | 1.000 | 3/8 | 0/7 | 0.400 | 0.000 | nan | 0.958 | 1/7 | 15 |

### Matriz de confusão (células semânticas) gabarito × previsto — `choice`

| gabarito \ previsto | atende | contradiz | nao_informado |
|---|---|---|---|
| atende | 0 | 0 | 17 |
| contradiz | 0 | 0 | 7 |
| nao_informado | 0 | 0 | 0 |

### Por família (prefixo da `nota`) — `choice`

| família | disputas | células_sem | acerto_semantico | exclusao_aprovada | descartou_sem_perguntar | elegiveis_exatos | baseline |
|---|---|---|---|---|---|---|---|
| fácil | 5 | 24 | 0.000 | 0/7 | 0/0 | 0.400 | 0.958 |

### Cobertura × erro por limiares (células semânticas; elegíveis recalculados) — `choice`

| CONF_ATENDE | CONF_CONTRADIZ | acerto_semantico | cobertura | erro_decididos | valvula | exclusao_aprovada | descartou_sem_perguntar | inelegivel_elegivel | elegiveis_exatos |
|---|---|---|---|---|---|---|---|---|---|
| 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.500 | 0.500 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.700 | 0.500 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.800 | 0.500 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.700 | 0.700 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.900 | 0.500 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.900 | 0.700 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.900 | 0.900 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |

### Cobertura × erro por limiares (células semânticas; elegíveis recalculados) — `nouls`

| SIM_ENTREGA | SIM_EXCLUI | acerto_semantico | cobertura | erro_decididos | valvula | exclusao_aprovada | descartou_sem_perguntar | inelegivel_elegivel | elegiveis_exatos |
|---|---|---|---|---|---|---|---|---|---|
| 0.500 | 0.500 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.700 | 0.500 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.700 | 0.700 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.800 | 0.500 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.900 | 0.500 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |
| 0.900 | 0.700 | 0.000 | 1.000 | 1.000 | 0 | 0/7 | 0/0 | 3/8 | 0.400 |

### Custo e latência (medidos na chamada real; do cache também)

Latência por REQUISIÇÃO (= por proposta). Mil disputas = 3 mil propostas comparadas.

| desenho | requisicoes | falhas_operacionais |
|---|---|---|
| choice | 0 | 15 |
| nouls | 0 | 15 |

### Por proposta — elegível e perguntas — `choice`

| id | p | elegível gab | elegível prev | perguntas ao fornecedor |
|---|---|---|---|---|
| CP-R01 | p1 | True | True | Confirmar, por escrito e dentro do preço cotado: Instalação dos aparelhos inclusa no preço. |
| CP-R01 | p2 | False | True | Confirmar, por escrito e dentro do preço cotado: Instalação dos aparelhos inclusa no preço. |
| CP-R01 | p3 | False | False | (inelegível) |
| CP-R02 | p1 | True | True | Confirmar, por escrito e dentro do preço cotado: Treinamento da equipe incluso. |
| CP-R02 | p2 | True | True | Confirmar, por escrito e dentro do preço cotado: Treinamento da equipe incluso. |
| CP-R02 | p3 | False | False | (inelegível) |
| CP-R03 | p1 | True | True | Confirmar, por escrito e dentro do preço cotado: Fotos editadas entregues em alta resolução.; Confirmar, por escrito e dentro do preço cotado: Tour virtual 360º incluso. |
| CP-R03 | p2 | False | True | Confirmar, por escrito e dentro do preço cotado: Fotos editadas entregues em alta resolução.; Confirmar, por escrito e dentro do preço cotado: Tour virtual 360º incluso. |
| CP-R03 | p3 | False | False | (inelegível) |
| CP-R04 | p1 | True | True | Confirmar, por escrito e dentro do preço cotado: Materiais de limpeza fornecidos pela contratada.; Confirmar, por escrito e dentro do preço cotado: Atendimento de segunda a sábado. |
| CP-R04 | p2 | False | True | Confirmar, por escrito e dentro do preço cotado: Materiais de limpeza fornecidos pela contratada.; Confirmar, por escrito e dentro do preço cotado: Atendimento de segunda a sábado. |
| CP-R04 | p3 | False | False | (inelegível) |
| CP-R05 | p1 | True | True | Confirmar, por escrito e dentro do preço cotado: Site responsivo (funciona em celular). |
| CP-R05 | p2 | False | False | (inelegível) |
| CP-R05 | p3 | True | True | Confirmar, por escrito e dentro do preço cotado: Site responsivo (funciona em celular). |

### Célula a célula — `choice` (`nouls` entre parênteses)

`jev` = opção bruta (confiança) ou Nouls entrega/exclui → leitura dura; `marca`: `caro` = exclusão aprovada (contradiz → atende); `desc` = descartou sem perguntar (nao_informado → contradiz); `erro` = outra célula errada.

| id | p | r | requisito | tipo | jev | célula | gab | bl | marca |
|---|---|---|---|---|---|---|---|---|---|
| CP-R01 | p1 | r1 | Instalação dos aparelhos inclusa no preço. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R01 | p1 | r2 | Garantia de pelo menos 12 meses (`garantia_meses` >= 12). | num | — (— → aten) | aten | aten | aten | — |
| CP-R01 | p1 | r3 | Preço total de até R$ 20.000 (`preco_total` <= 20000). | num | — (— → aten) | aten | aten | aten | — |
| CP-R01 | p2 | r1 | Instalação dos aparelhos inclusa no preço. | sem | falha (falha → nao_) | nao_ | cont | cont | erro |
| CP-R01 | p2 | r2 | Garantia de pelo menos 12 meses (`garantia_meses` >= 12). | num | — (— → aten) | aten | aten | aten | — |
| CP-R01 | p2 | r3 | Preço total de até R$ 20.000 (`preco_total` <= 20000). | num | — (— → aten) | aten | aten | aten | — |
| CP-R01 | p3 | r1 | Instalação dos aparelhos inclusa no preço. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R01 | p3 | r2 | Garantia de pelo menos 12 meses (`garantia_meses` >= 12). | num | — (— → aten) | aten | aten | aten | — |
| CP-R01 | p3 | r3 | Preço total de até R$ 20.000 (`preco_total` <= 20000). | num | — (— → cont) | cont | cont | cont | — |
| CP-R02 | p1 | r1 | Treinamento da equipe incluso. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R02 | p1 | r2 | Suporte por pelo menos 12 meses (`suporte_meses` >= 12). | num | — (— → aten) | aten | aten | aten | — |
| CP-R02 | p1 | r3 | Prazo de implantação de até 30 dias (`prazo_dias` <= 30). | num | — (— → aten) | aten | aten | aten | — |
| CP-R02 | p2 | r1 | Treinamento da equipe incluso. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R02 | p2 | r2 | Suporte por pelo menos 12 meses (`suporte_meses` >= 12). | num | — (— → aten) | aten | aten | aten | — |
| CP-R02 | p2 | r3 | Prazo de implantação de até 30 dias (`prazo_dias` <= 30). | num | — (— → cont) | cont | cont | cont | — |
| CP-R02 | p3 | r1 | Treinamento da equipe incluso. | sem | falha (falha → nao_) | nao_ | cont | cont | erro |
| CP-R02 | p3 | r2 | Suporte por pelo menos 12 meses (`suporte_meses` >= 12). | num | — (— → cont) | cont | cont | cont | — |
| CP-R02 | p3 | r3 | Prazo de implantação de até 30 dias (`prazo_dias` <= 30). | num | — (— → aten) | aten | aten | aten | — |
| CP-R03 | p1 | r1 | Fotos editadas entregues em alta resolução. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R03 | p1 | r2 | Tour virtual 360º incluso. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R03 | p1 | r3 | Preço por imóvel de até R$ 400 (`preco_total` <= 400). | num | — (— → aten) | aten | aten | aten | — |
| CP-R03 | p2 | r1 | Fotos editadas entregues em alta resolução. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R03 | p2 | r2 | Tour virtual 360º incluso. | sem | falha (falha → nao_) | nao_ | cont | cont | erro |
| CP-R03 | p2 | r3 | Preço por imóvel de até R$ 400 (`preco_total` <= 400). | num | — (— → aten) | aten | aten | aten | — |
| CP-R03 | p3 | r1 | Fotos editadas entregues em alta resolução. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R03 | p3 | r2 | Tour virtual 360º incluso. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R03 | p3 | r3 | Preço por imóvel de até R$ 400 (`preco_total` <= 400). | num | — (— → cont) | cont | cont | cont | — |
| CP-R04 | p1 | r1 | Materiais de limpeza fornecidos pela contratada. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R04 | p1 | r2 | Atendimento de segunda a sábado. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R04 | p1 | r3 | Valor mensal de até R$ 6.000 (`preco_total` <= 6000). | num | — (— → aten) | aten | aten | aten | — |
| CP-R04 | p2 | r1 | Materiais de limpeza fornecidos pela contratada. | sem | falha (falha → nao_) | nao_ | cont | cont | erro |
| CP-R04 | p2 | r2 | Atendimento de segunda a sábado. | sem | falha (falha → nao_) | nao_ | cont | aten | erro |
| CP-R04 | p2 | r3 | Valor mensal de até R$ 6.000 (`preco_total` <= 6000). | num | — (— → aten) | aten | aten | aten | — |
| CP-R04 | p3 | r1 | Materiais de limpeza fornecidos pela contratada. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R04 | p3 | r2 | Atendimento de segunda a sábado. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R04 | p3 | r3 | Valor mensal de até R$ 6.000 (`preco_total` <= 6000). | num | — (— → cont) | cont | cont | cont | — |
| CP-R05 | p1 | r1 | Site responsivo (funciona em celular). | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R05 | p1 | r2 | Hospedagem no primeiro ano inclusa. | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R05 | p1 | r3 | Prazo de entrega de até 45 dias (`prazo_dias` <= 45). | num | — (— → aten) | aten | aten | aten | — |
| CP-R05 | p2 | r1 | Site responsivo (funciona em celular). | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R05 | p2 | r2 | Hospedagem no primeiro ano inclusa. | sem | falha (falha → nao_) | nao_ | cont | cont | erro |
| CP-R05 | p2 | r3 | Prazo de entrega de até 45 dias (`prazo_dias` <= 45). | num | — (— → cont) | cont | cont | cont | — |
| CP-R05 | p3 | r1 | Site responsivo (funciona em celular). | sem | falha (falha → nao_) | nao_ | aten | aten | erro |
| CP-R05 | p3 | r2 | Hospedagem no primeiro ano inclusa. | sem | falha (falha → nao_) | nao_ | cont | cont | erro |
| CP-R05 | p3 | r3 | Prazo de entrega de até 45 dias (`prazo_dias` <= 45). | num | — (— → aten) | aten | aten | aten | — |
