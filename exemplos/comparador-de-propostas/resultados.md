# Resultados — comparador-de-propostas

Gerado por `run.py` em 2026-10-02 (modo `auto`; modelo e amostra em cada seção). Perguntas, limiares, contexto do comprador e baseline: `perguntas.py`; comparação numérica, válvula, elegíveis e perguntas: `comparador.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Desenho padrão: `choice`; CONF_ATENDE 0.7, CONF_CONTRADIZ 0.5; Nouls FAIXA_ENTREGA (0.3, 0.7), FAIXA_EXCLUI (0.3, 0.5).

Critério de continuar/descartar (fixado antes do teste): no teste (20 disputas, 60 propostas), com o desenho padrão e os limiares de perguntas.py: (1) células numéricas pelo código 100% (menos é bug); (2) células semânticas (Jev, com válvula) ≥ baseline + 15 p.p.; (3) gabarito contradiz semântico → atende ≤ 5% dessas células; (4) proposta inelegível no gabarito dentro de `elegiveis` ≤ 10% das inelegíveis; (5) lista `elegiveis` igual ao gabarito em ≥ 70% das disputas.

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-02T00:04:09-03:00): `perguntas.py` sha256 4297fcc11a5d6898… · `comparador.py` sha256 6dc606205375367f… · `run.py` sha256 40bd3de98eb0253d… · `dados/teste.json` sha256 3fc35c8f5b174463…

## Lado a lado

### Células, erros caros, elegíveis — Jev + código × baseline

| conjunto | desenho | células_sem | acerto_semantico | baseline | numericas | exclusao_aprovada | baseline_excl | descartou_sem_perguntar | inelegivel_elegivel | elegivel_fora | elegiveis_exatos | perguntas_P/R | valvula |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | choice | 69 | 0.913 | 0.652 | 1.000 (51) | 0/18 | 11/18 | 2/8 | 0/16 | 2/14 | 0.800 | 0.75/0.60 | 3 |
| ajuste | nouls | 69 | 0.855 | 0.652 | 1.000 (51) | 0/18 | 11/18 | 2/8 | 2/16 | 2/14 | 0.600 | 0.38/0.60 | 4 |
| teste | choice | 132 | 0.894 | 0.667 | 1.000 (102) | 0/37 | 19/37 | 1/15 | 0/32 | 0/28 | 1.000 | 0.71/0.91 | 9 |

### Latência e custo

| conjunto | desenho | disputas | propostas | requisicoes | p50_ms | p95_ms | tokens_por_proposta | US$_por_mil_disputas | falhas | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | choice | 10 | 30 | 30 | 288 | 465 | 3313 | 0.4174 | 0 | jev-1.13.0 |
| ajuste | nouls | 10 | 30 | 30 | 260 | 333 | 1733 | 0.2183 | 0 | jev-1.13.0 |
| teste | choice | 20 | 60 | 60 | 273 | 459 | 3178 | 0.4005 | 0 | jev-1.13.0 |

## Veredito do critério (teste, desenho padrão)

| item | regra | valor | passa |
|---|---|---|---|
| 1_numericas | células numéricas pelo código 100% (menos é bug) | 1.000 (102) | ✓ |
| 2_acerto_semantico | células semânticas (Jev, com válvula) ≥ baseline + 15 p.p. | 0.894 × baseline 0.667 | ✓ |
| 3_exclusao_aprovada | gabarito contradiz semântico → atende ≤ 5% dessas células | 0/37 | ✓ |
| 4_inelegivel_elegivel | proposta inelegível no gabarito dentro de `elegiveis` ≤ 10% das inelegíveis | 0/32 | ✓ |
| 5_elegiveis_exatos | lista `elegiveis` igual ao gabarito em ≥ 70% das disputas | 1.000 | ✓ |

**CONTINUAR**: 5/5 itens.

## Conjunto `ajuste` — 10 disputas, 30 propostas, 120 células (arquivo versão 2026-10-02, autor fable)

### Matriz, elegíveis e perguntas — Jev + código × baseline, por desenho

`acerto_semantico` = células semânticas (Jev, depois da válvula) × gabarito; `acerto_numerico` = células numéricas pelo código; `classe_*` = acerto dentro de cada classe do gabarito. Erros caros: `exclusao_aprovada` = gabarito contradiz → atende (`_bruto` = antes da válvula); `inelegivel_elegivel` = proposta com contradiz obrigatório no gabarito que entrou em `elegiveis`. Secundários: `descartou_sem_perguntar` = gabarito nao_informado → contradiz; `falso_alarme` = atende → contradiz; `elegivel_fora` = elegível do gabarito que ficou fora. `valvula` = abstenções: células cuja leitura dura (`bruto`: opção da Choice; Nouls com corte em 0,5) decidia e a válvula/faixa mandou para nao_informado; `cobertura` = o resto; `erro_decididos` = erro entre as não movidas. `perguntas_*` = nao_informado em obrigatório de proposta ELEGÍVEL (o que a saída pergunta ao fornecedor) × gabarito, cada lado filtrado pela própria elegibilidade. `baseline` = palavra-chave + marca de exclusão na mesma frase.

| desenho | n_sem | n_num | acerto_semantico | acerto_numerico | acerto_total | classe_atende | classe_contradiz | classe_nao_informado | exclusao_aprovada | exclusao_aprovada_bruto | descartou_sem_perguntar | falso_alarme | valvula | cobertura | erro_decididos | inelegivel_elegivel | elegivel_fora | elegiveis_exatos | perguntas_precisao | perguntas_recall | baseline_semantico | baseline_exclusao_aprovada | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| choice | 69 | 51 | 0.913 | 1.000 | 0.950 | 0.907 | 1.000 | 0.750 | 0/18 | 0/18 | 2/8 | 0/43 | 3 | 0.957 | 0.045 | 0/16 | 2/14 | 0.800 | 0.750 | 0.600 | 0.652 | 11/18 | 0 |
| nouls | 69 | 51 | 0.855 | 1.000 | 0.917 | 0.860 | 0.889 | 0.750 | 0/18 | 1/18 | 2/8 | 0/43 | 4 | 0.942 | 0.092 | 2/16 | 2/14 | 0.600 | 0.375 | 0.600 | 0.652 | 11/18 | 0 |

### Matriz de confusão (células semânticas) gabarito × previsto — `choice`

| gabarito \ previsto | atende | contradiz | nao_informado |
|---|---|---|---|
| atende | 39 | 0 | 4 |
| contradiz | 0 | 18 | 0 |
| nao_informado | 0 | 2 | 6 |

### Por família (prefixo da `nota`) — `choice`

| família | disputas | células_sem | acerto_semantico | exclusao_aprovada | descartou_sem_perguntar | elegiveis_exatos | baseline |
|---|---|---|---|---|---|---|---|
| anexo citado mas ausente | 1 | 6 | 0.667 | 0/2 | 0/0 | 1.000 | 0.833 |
| atende tudo menos o prazo | 2 | 12 | 1.000 | 0/2 | 0/2 | 1.000 | 0.833 |
| exclusão escondida | 1 | 6 | 1.000 | 0/2 | 0/0 | 1.000 | 0.500 |
| fácil | 2 | 15 | 0.933 | 0/4 | 0/2 | 1.000 | 0.667 |
| promessa condicionada | 1 | 9 | 0.889 | 0/2 | 1/1 | 0.000 | 0.556 |
| termo vago | 3 | 21 | 0.905 | 0/6 | 1/3 | 0.667 | 0.571 |

### Cobertura × erro por limiares (células semânticas; elegíveis recalculados) — `choice`

| CONF_ATENDE | CONF_CONTRADIZ | acerto_semantico | cobertura | erro_decididos | valvula | exclusao_aprovada | descartou_sem_perguntar | inelegivel_elegivel | elegiveis_exatos |
|---|---|---|---|---|---|---|---|---|---|
| 0.000 | 0.000 | 0.957 | 1.000 | 0.043 | 0 | 0/18 | 2/8 | 0/16 | 0.800 |
| 0.500 | 0.500 | 0.942 | 0.986 | 0.044 | 1 | 0/18 | 2/8 | 0/16 | 0.800 |
| 0.700 | 0.500 | 0.913 | 0.957 | 0.045 | 3 | 0/18 | 2/8 | 0/16 | 0.800 |
| 0.800 | 0.500 | 0.899 | 0.942 | 0.046 | 4 | 0/18 | 2/8 | 0/16 | 0.800 |
| 0.700 | 0.700 | 0.884 | 0.928 | 0.047 | 5 | 0/18 | 2/8 | 1/16 | 0.700 |
| 0.900 | 0.500 | 0.855 | 0.899 | 0.048 | 7 | 0/18 | 2/8 | 0/16 | 0.800 |
| 0.900 | 0.700 | 0.826 | 0.870 | 0.050 | 9 | 0/18 | 2/8 | 1/16 | 0.700 |
| 0.900 | 0.900 | 0.826 | 0.841 | 0.034 | 11 | 0/18 | 1/8 | 2/16 | 0.700 |

### Cobertura × erro por limiares (células semânticas; elegíveis recalculados) — `nouls`

| SIM_ENTREGA | SIM_EXCLUI | acerto_semantico | cobertura | erro_decididos | valvula | exclusao_aprovada | descartou_sem_perguntar | inelegivel_elegivel | elegiveis_exatos |
|---|---|---|---|---|---|---|---|---|---|
| 0.500 | 0.500 | 0.855 | 0.942 | 0.092 | 4 | 0/18 | 2/8 | 2/16 | 0.600 |
| 0.700 | 0.500 | 0.855 | 0.942 | 0.092 | 4 | 0/18 | 2/8 | 2/16 | 0.600 |
| 0.700 | 0.700 | 0.841 | 0.928 | 0.094 | 5 | 0/18 | 2/8 | 2/16 | 0.600 |
| 0.800 | 0.500 | 0.783 | 0.870 | 0.100 | 9 | 0/18 | 2/8 | 2/16 | 0.600 |
| 0.900 | 0.500 | 0.580 | 0.667 | 0.130 | 23 | 0/18 | 2/8 | 2/16 | 0.600 |
| 0.900 | 0.700 | 0.565 | 0.652 | 0.133 | 24 | 0/18 | 2/8 | 2/16 | 0.600 |

### Custo e latência (medidos na chamada real; do cache também)

Latência por REQUISIÇÃO (= por proposta). Mil disputas = 3 mil propostas comparadas.

| desenho | requisicoes | perguntas | p50_ms | p95_ms | tokens_por_proposta | US$_por_disputa | US$_por_mil_disputas | falhas_operacionais | modelo |
|---|---|---|---|---|---|---|---|---|---|
| choice | 30 | 69 | 288 | 465 | 3313 | 0.000417 | 0.4174 | 0 | jev-1.13.0 |
| nouls | 30 | 138 | 260 | 333 | 1733 | 0.000218 | 0.2183 | 0 | jev-1.13.0 |

### Por proposta — elegível e perguntas — `choice`

| id | p | elegível gab | elegível prev | perguntas ao fornecedor |
|---|---|---|---|---|
| CP-A01 | p1 | False | False | (inelegível) |
| CP-A01 | p2 | True | True | — |
| CP-A01 | p3 | True | True | Informar a garantia em meses — requisito: Garantia de pelo menos 12 meses. |
| CP-A02 | p1 | True | True | Informar a duração do suporte em meses — requisito: Suporte técnico por pelo menos 12 meses. |
| CP-A02 | p2 | True | False | (inelegível) |
| CP-A02 | p3 | False | False | (inelegível) |
| CP-A03 | p1 | False | False | (inelegível) |
| CP-A03 | p2 | False | False | (inelegível) |
| CP-A03 | p3 | True | True | Confirmar, por escrito e dentro do preço cotado: Pintura externa com textura e impermeabilização das platibandas. |
| CP-A04 | p1 | True | True | — |
| CP-A04 | p2 | False | False | (inelegível) |
| CP-A04 | p3 | False | False | (inelegível) |
| CP-A05 | p1 | True | True | — |
| CP-A05 | p2 | True | False | (inelegível) |
| CP-A05 | p3 | False | False | (inelegível) |
| CP-A06 | p1 | True | True | — |
| CP-A06 | p2 | False | False | (inelegível) |
| CP-A06 | p3 | False | False | (inelegível) |
| CP-A07 | p1 | True | True | — |
| CP-A07 | p2 | False | False | (inelegível) |
| CP-A07 | p3 | False | False | (inelegível) |
| CP-A08 | p1 | True | True | — |
| CP-A08 | p2 | False | False | (inelegível) |
| CP-A08 | p3 | False | False | (inelegível) |
| CP-A09 | p1 | True | True | — |
| CP-A09 | p2 | False | False | (inelegível) |
| CP-A09 | p3 | False | False | (inelegível) |
| CP-A10 | p1 | True | True | — |
| CP-A10 | p2 | False | False | (inelegível) |
| CP-A10 | p3 | True | True | Confirmar, por escrito e dentro do preço cotado: Plataforma de e-mail marketing com automação (fluxos por comportamento). |

### Célula a célula — `choice` (`nouls` entre parênteses)

`jev` = opção bruta (confiança) ou Nouls entrega/exclui → leitura dura; `marca`: `caro` = exclusão aprovada (contradiz → atende); `desc` = descartou sem perguntar (nao_informado → contradiz); `erro` = outra célula errada.

| id | p | r | requisito | tipo | jev | célula | gab | bl | marca |
|---|---|---|---|---|---|---|---|---|---|
| CP-A01 | p1 | r1 | Instalação dos 6 aparelhos inclusa no preço. | sem | cont (0.85) (e 0.90 / x 0.34 → aten → nao_) | cont | cont | aten | — |
| CP-A01 | p1 | r2 | Garantia de pelo menos 12 meses (`garantia_meses` >= 12). | num | — (— → aten) | aten | aten | aten | — |
| CP-A01 | p1 | r3 | Preço total de até R$ 30.000 (`preco_total` <= 30000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A01 | p1 | r4 | Manutenção preventiva no primeiro ano inclusa. | sem | aten (0.92) (e 0.90 / x 0.08 → aten → aten) | aten | aten | cont | — |
| CP-A01 | p2 | r1 | Instalação dos 6 aparelhos inclusa no preço. | sem | aten (0.83) (e 0.75 / x 0.08 → aten → aten) | aten | aten | aten | — |
| CP-A01 | p2 | r2 | Garantia de pelo menos 12 meses (`garantia_meses` >= 12). | num | — (— → aten) | aten | aten | aten | — |
| CP-A01 | p2 | r3 | Preço total de até R$ 30.000 (`preco_total` <= 30000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A01 | p2 | r4 | Manutenção preventiva no primeiro ano inclusa. | sem | cont (0.97) (e 0.02 / x 0.96 → cont → cont) | cont | cont | aten | — |
| CP-A01 | p3 | r1 | Instalação dos 6 aparelhos inclusa no preço. | sem | aten (1.00) (e 0.95 / x 0.02 → aten → aten) | aten | aten | aten | — |
| CP-A01 | p3 | r2 | Garantia de pelo menos 12 meses (`garantia_meses` >= 12). | num | — (— → nao_) | nao_ | nao_ | nao_ | — |
| CP-A01 | p3 | r3 | Preço total de até R$ 30.000 (`preco_total` <= 30000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A01 | p3 | r4 | Manutenção preventiva no primeiro ano inclusa. | sem | aten (0.76) (e 0.67 / x 0.41 → aten → nao_) | aten | aten | aten | — |
| CP-A02 | p1 | r1 | Treinamento da equipe de vendas incluso. | sem | aten (0.81) (e 0.70 / x 0.08 → aten → aten) | aten | aten | aten | — |
| CP-A02 | p1 | r2 | Suporte técnico por pelo menos 12 meses (`suporte_meses` >=  | num | — (— → nao_) | nao_ | nao_ | nao_ | — |
| CP-A02 | p1 | r3 | Integração com os portais de anúncio (importar leads automat | sem | aten (0.99) (e 0.86 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A02 | p1 | r4 | Prazo de implantação de até 30 dias (`prazo_dias` <= 30). | num | — (— → aten) | aten | aten | aten | — |
| CP-A02 | p2 | r1 | Treinamento da equipe de vendas incluso. | sem | cont (0.98) (e 0.04 / x 0.94 → cont → cont) | cont | nao_ | aten | desc |
| CP-A02 | p2 | r2 | Suporte técnico por pelo menos 12 meses (`suporte_meses` >=  | num | — (— → aten) | aten | aten | aten | — |
| CP-A02 | p2 | r3 | Integração com os portais de anúncio (importar leads automat | sem | aten (0.98) (e 0.84 / x 0.06 → aten → aten) | aten | aten | aten | — |
| CP-A02 | p2 | r4 | Prazo de implantação de até 30 dias (`prazo_dias` <= 30). | num | — (— → aten) | aten | aten | aten | — |
| CP-A02 | p3 | r1 | Treinamento da equipe de vendas incluso. | sem | aten (0.53) (e 0.71 / x 0.18 → aten → aten) | nao_ | aten | aten | erro |
| CP-A02 | p3 | r2 | Suporte técnico por pelo menos 12 meses (`suporte_meses` >=  | num | — (— → aten) | aten | aten | aten | — |
| CP-A02 | p3 | r3 | Integração com os portais de anúncio (importar leads automat | sem | cont (1.00) (e 0.02 / x 0.94 → cont → cont) | cont | cont | aten | — |
| CP-A02 | p3 | r4 | Prazo de implantação de até 30 dias (`prazo_dias` <= 30). | num | — (— → aten) | aten | aten | aten | — |
| CP-A03 | p1 | r1 | Pintura externa com textura e impermeabilização das platiban | sem | aten (1.00) (e 0.90 / x 0.04 → aten → aten) | aten | aten | aten | — |
| CP-A03 | p1 | r2 | Andaime e proteção de fachada por conta da contratada. | sem | aten (1.00) (e 0.93 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A03 | p1 | r3 | Prazo de obra de até 60 dias (`prazo_dias` <= 60). | num | — (— → cont) | cont | cont | cont | — |
| CP-A03 | p1 | r4 | Preço total de até R$ 85.000 (`preco_total` <= 85000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A03 | p2 | r1 | Pintura externa com textura e impermeabilização das platiban | sem | aten (0.92) (e 0.85 / x 0.19 → aten → aten) | aten | aten | aten | — |
| CP-A03 | p2 | r2 | Andaime e proteção de fachada por conta da contratada. | sem | cont (1.00) (e 0.02 / x 0.97 → cont → cont) | cont | cont | cont | — |
| CP-A03 | p2 | r3 | Prazo de obra de até 60 dias (`prazo_dias` <= 60). | num | — (— → aten) | aten | aten | aten | — |
| CP-A03 | p2 | r4 | Preço total de até R$ 85.000 (`preco_total` <= 85000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A03 | p3 | r1 | Pintura externa com textura e impermeabilização das platiban | sem | nao_ (0.89) (e 0.26 / x 0.38 → nao_ → nao_) | nao_ | nao_ | aten | — |
| CP-A03 | p3 | r2 | Andaime e proteção de fachada por conta da contratada. | sem | aten (0.95) (e 0.85 / x 0.04 → aten → aten) | aten | aten | aten | — |
| CP-A03 | p3 | r3 | Prazo de obra de até 60 dias (`prazo_dias` <= 60). | num | — (— → aten) | aten | aten | aten | — |
| CP-A03 | p3 | r4 | Preço total de até R$ 85.000 (`preco_total` <= 85000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A04 | p1 | r1 | Câmeras com gravação em nuvem por 30 dias. | sem | aten (1.00) (e 0.90 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A04 | p1 | r2 | Monitoramento 24 horas por central própria. | sem | aten (0.95) (e 0.87 / x 0.05 → aten → aten) | aten | aten | aten | — |
| CP-A04 | p1 | r3 | Equipamentos em comodato (sem compra). | sem | aten (1.00) (e 0.87 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A04 | p1 | r4 | Mensalidade de até R$ 1.500 (`preco_total` <= 1500). | num | — (— → aten) | aten | aten | aten | — |
| CP-A04 | p2 | r1 | Câmeras com gravação em nuvem por 30 dias. | sem | cont (1.00) (e 0.01 / x 0.97 → cont → cont) | cont | cont | aten | — |
| CP-A04 | p2 | r2 | Monitoramento 24 horas por central própria. | sem | cont (1.00) (e 0.04 / x 0.95 → cont → cont) | cont | cont | cont | — |
| CP-A04 | p2 | r3 | Equipamentos em comodato (sem compra). | sem | cont (1.00) (e 0.02 / x 0.96 → cont → cont) | cont | cont | aten | — |
| CP-A04 | p2 | r4 | Mensalidade de até R$ 1.500 (`preco_total` <= 1500). | num | — (— → aten) | aten | aten | aten | — |
| CP-A04 | p3 | r1 | Câmeras com gravação em nuvem por 30 dias. | sem | nao_ (0.71) (e 0.15 / x 0.45 → nao_ → nao_) | nao_ | nao_ | aten | — |
| CP-A04 | p3 | r2 | Monitoramento 24 horas por central própria. | sem | cont (1.00) (e 0.03 / x 0.97 → cont → cont) | cont | cont | cont | — |
| CP-A04 | p3 | r3 | Equipamentos em comodato (sem compra). | sem | aten (0.99) (e 0.90 / x 0.36 → aten → nao_) | aten | aten | cont | — |
| CP-A04 | p3 | r4 | Mensalidade de até R$ 1.500 (`preco_total` <= 1500). | num | — (— → aten) | aten | aten | aten | — |
| CP-A05 | p1 | r1 | Central telefônica com URA (atendimento automático) e gravaç | sem | aten (0.99) (e 0.88 / x 0.04 → aten → aten) | aten | aten | aten | — |
| CP-A05 | p1 | r2 | Portabilidade dos números atuais inclusa. | sem | aten (1.00) (e 0.94 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A05 | p1 | r3 | Sem fidelidade contratual. | sem | aten (1.00) (e 0.90 / x 0.03 → aten → aten) | aten | aten | cont | — |
| CP-A05 | p1 | r4 | Mensalidade de até R$ 800 (`preco_total` <= 800). | num | — (— → aten) | aten | aten | aten | — |
| CP-A05 | p2 | r1 | Central telefônica com URA (atendimento automático) e gravaç | sem | cont (0.81) (e 0.07 / x 0.88 → cont → cont) | cont | nao_ | aten | desc |
| CP-A05 | p2 | r2 | Portabilidade dos números atuais inclusa. | sem | aten (0.99) (e 0.81 / x 0.07 → aten → aten) | aten | aten | aten | — |
| CP-A05 | p2 | r3 | Sem fidelidade contratual. | sem | cont (1.00) (e 0.02 / x 0.88 → cont → cont) | cont | cont | aten | — |
| CP-A05 | p2 | r4 | Mensalidade de até R$ 800 (`preco_total` <= 800). | num | — (— → aten) | aten | aten | aten | — |
| CP-A05 | p3 | r1 | Central telefônica com URA (atendimento automático) e gravaç | sem | aten (0.98) (e 0.88 / x 0.08 → aten → aten) | aten | aten | aten | — |
| CP-A05 | p3 | r2 | Portabilidade dos números atuais inclusa. | sem | cont (1.00) (e 0.06 / x 0.93 → cont → cont) | cont | cont | cont | — |
| CP-A05 | p3 | r3 | Sem fidelidade contratual. | sem | aten (0.87) (e 0.76 / x 0.21 → aten → aten) | aten | aten | cont | — |
| CP-A05 | p3 | r4 | Mensalidade de até R$ 800 (`preco_total` <= 800). | num | — (— → aten) | aten | aten | aten | — |
| CP-A06 | p1 | r1 | Emissão das notas fiscais de comissão. | sem | aten (1.00) (e 0.92 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A06 | p1 | r2 | Folha de pagamento dos funcionários inclusa. | sem | aten (0.99) (e 0.85 / x 0.04 → aten → aten) | aten | aten | aten | — |
| CP-A06 | p1 | r3 | Atendimento por contador dedicado. | sem | aten (1.00) (e 0.91 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A06 | p1 | r4 | Honorário mensal de até R$ 2.000 (`preco_total` <= 2000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A06 | p2 | r1 | Emissão das notas fiscais de comissão. | sem | aten (0.92) (e 0.75 / x 0.09 → aten → aten) | aten | aten | aten | — |
| CP-A06 | p2 | r2 | Folha de pagamento dos funcionários inclusa. | sem | cont (0.98) (e 0.13 / x 0.84 → cont → cont) | cont | cont | cont | — |
| CP-A06 | p2 | r3 | Atendimento por contador dedicado. | sem | cont (0.68) (e 0.18 / x 0.53 → cont → cont) | cont | cont | aten | — |
| CP-A06 | p2 | r4 | Honorário mensal de até R$ 2.000 (`preco_total` <= 2000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A06 | p3 | r1 | Emissão das notas fiscais de comissão. | sem | aten (0.93) (e 0.82 / x 0.04 → aten → aten) | aten | aten | aten | — |
| CP-A06 | p3 | r2 | Folha de pagamento dos funcionários inclusa. | sem | aten (1.00) (e 0.93 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A06 | p3 | r3 | Atendimento por contador dedicado. | sem | nao_ (1.00) (e 0.06 / x 0.16 → nao_ → nao_) | nao_ | nao_ | aten | — |
| CP-A06 | p3 | r4 | Honorário mensal de até R$ 2.000 (`preco_total` <= 2000). | num | — (— → cont) | cont | cont | cont | — |
| CP-A07 | p1 | r1 | Entrega e montagem dos móveis inclusas. | sem | aten (0.99) (e 0.80 / x 0.37 → aten → nao_) | aten | aten | aten | — |
| CP-A07 | p1 | r2 | Cadeiras com certificação ergonômica (NR-17). | sem | aten (1.00) (e 0.90 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A07 | p1 | r3 | Prazo de entrega de até 20 dias (`prazo_dias` <= 20). | num | — (— → aten) | aten | aten | aten | — |
| CP-A07 | p1 | r4 | Preço total de até R$ 18.000 (`preco_total` <= 18000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A07 | p2 | r1 | Entrega e montagem dos móveis inclusas. | sem | cont (1.00) (e 0.03 / x 0.96 → cont → cont) | cont | cont | cont | — |
| CP-A07 | p2 | r2 | Cadeiras com certificação ergonômica (NR-17). | sem | nao_ (0.89) (e 0.07 / x 0.36 → nao_ → nao_) | nao_ | nao_ | aten | — |
| CP-A07 | p2 | r3 | Prazo de entrega de até 20 dias (`prazo_dias` <= 20). | num | — (— → aten) | aten | aten | aten | — |
| CP-A07 | p2 | r4 | Preço total de até R$ 18.000 (`preco_total` <= 18000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A07 | p3 | r1 | Entrega e montagem dos móveis inclusas. | sem | aten (1.00) (e 0.95 / x 0.02 → aten → aten) | aten | aten | cont | — |
| CP-A07 | p3 | r2 | Cadeiras com certificação ergonômica (NR-17). | sem | aten (1.00) (e 0.93 / x 0.02 → aten → aten) | aten | aten | cont | — |
| CP-A07 | p3 | r3 | Prazo de entrega de até 20 dias (`prazo_dias` <= 20). | num | — (— → cont) | cont | cont | cont | — |
| CP-A07 | p3 | r4 | Preço total de até R$ 18.000 (`preco_total` <= 18000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A08 | p1 | r1 | Energia solar com instalação inclusa e homologação na conces | sem | aten (1.00) (e 0.95 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A08 | p1 | r2 | Garantia dos painéis de pelo menos 10 anos (`garantia_meses` | num | — (— → aten) | aten | aten | aten | — |
| CP-A08 | p1 | r3 | Prazo de instalação de até 90 dias (`prazo_dias` <= 90). | num | — (— → aten) | aten | aten | aten | — |
| CP-A08 | p1 | r4 | Monitoramento da geração por aplicativo. | sem | aten (1.00) (e 0.95 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A08 | p2 | r1 | Energia solar com instalação inclusa e homologação na conces | sem | cont (0.92) (e 0.32 / x 0.77 → cont → cont) | cont | cont | aten | — |
| CP-A08 | p2 | r2 | Garantia dos painéis de pelo menos 10 anos (`garantia_meses` | num | — (— → nao_) | nao_ | nao_ | nao_ | — |
| CP-A08 | p2 | r3 | Prazo de instalação de até 90 dias (`prazo_dias` <= 90). | num | — (— → aten) | aten | aten | aten | — |
| CP-A08 | p2 | r4 | Monitoramento da geração por aplicativo. | sem | nao_ (1.00) (e 0.04 / x 0.22 → nao_ → nao_) | nao_ | nao_ | nao_ | — |
| CP-A08 | p3 | r1 | Energia solar com instalação inclusa e homologação na conces | sem | aten (0.97) (e 0.85 / x 0.05 → aten → aten) | aten | aten | aten | — |
| CP-A08 | p3 | r2 | Garantia dos painéis de pelo menos 10 anos (`garantia_meses` | num | — (— → aten) | aten | aten | aten | — |
| CP-A08 | p3 | r3 | Prazo de instalação de até 90 dias (`prazo_dias` <= 90). | num | — (— → cont) | cont | cont | cont | — |
| CP-A08 | p3 | r4 | Monitoramento da geração por aplicativo. | sem | aten (1.00) (e 0.93 / x 0.02 → aten → aten) | aten | aten | aten | — |
| CP-A09 | p1 | r1 | Portaria remota com abertura de portão e atendimento de visi | sem | aten (1.00) (e 0.92 / x 0.04 → aten → aten) | aten | aten | aten | — |
| CP-A09 | p1 | r2 | Instalação de interfone e fechaduras inclusa. | sem | aten (1.00) (e 0.94 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A09 | p1 | r3 | Mensalidade de até R$ 3.000 (`preco_total` <= 3000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A09 | p1 | r4 | Prazo de implantação de até 45 dias (`prazo_dias` <= 45). | num | — (— → aten) | aten | aten | aten | — |
| CP-A09 | p2 | r1 | Portaria remota com abertura de portão e atendimento de visi | sem | aten (0.67) (e 0.45 / x 0.24 → nao_ → nao_) | nao_ | aten | aten | erro |
| CP-A09 | p2 | r2 | Instalação de interfone e fechaduras inclusa. | sem | cont (0.61) (e 0.42 / x 0.43 → nao_ → nao_) | cont | cont | cont | — |
| CP-A09 | p2 | r3 | Mensalidade de até R$ 3.000 (`preco_total` <= 3000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A09 | p2 | r4 | Prazo de implantação de até 45 dias (`prazo_dias` <= 45). | num | — (— → nao_) | nao_ | nao_ | nao_ | — |
| CP-A09 | p3 | r1 | Portaria remota com abertura de portão e atendimento de visi | sem | cont (1.00) (e 0.03 / x 0.95 → cont → cont) | cont | cont | aten | — |
| CP-A09 | p3 | r2 | Instalação de interfone e fechaduras inclusa. | sem | nao_ (0.27) (e 0.28 / x 0.36 → nao_ → nao_) | nao_ | aten | aten | erro |
| CP-A09 | p3 | r3 | Mensalidade de até R$ 3.000 (`preco_total` <= 3000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A09 | p3 | r4 | Prazo de implantação de até 45 dias (`prazo_dias` <= 45). | num | — (— → aten) | aten | aten | aten | — |
| CP-A10 | p1 | r1 | Plataforma de e-mail marketing com automação (fluxos por com | sem | aten (0.98) (e 0.83 / x 0.04 → aten → aten) | aten | aten | aten | — |
| CP-A10 | p1 | r2 | Até 50 mil contatos no plano (`contatos` >= 50000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A10 | p1 | r3 | Suporte em português. | sem | aten (1.00) (e 0.85 / x 0.03 → aten → aten) | aten | aten | aten | — |
| CP-A10 | p1 | r4 | Mensalidade de até R$ 600 (`preco_total` <= 600). | num | — (— → aten) | aten | aten | aten | — |
| CP-A10 | p2 | r1 | Plataforma de e-mail marketing com automação (fluxos por com | sem | cont (1.00) (e 0.03 / x 0.96 → cont → cont) | cont | cont | aten | — |
| CP-A10 | p2 | r2 | Até 50 mil contatos no plano (`contatos` >= 50000). | num | — (— → cont) | cont | cont | cont | — |
| CP-A10 | p2 | r3 | Suporte em português. | sem | cont (1.00) (e 0.02 / x 0.94 → cont → cont) | cont | cont | aten | — |
| CP-A10 | p2 | r4 | Mensalidade de até R$ 600 (`preco_total` <= 600). | num | — (— → aten) | aten | aten | aten | — |
| CP-A10 | p3 | r1 | Plataforma de e-mail marketing com automação (fluxos por com | sem | aten (0.44) (e 0.49 / x 0.08 → nao_ → nao_) | nao_ | aten | aten | erro |
| CP-A10 | p3 | r2 | Até 50 mil contatos no plano (`contatos` >= 50000). | num | — (— → aten) | aten | aten | aten | — |
| CP-A10 | p3 | r3 | Suporte em português. | sem | nao_ (0.64) (e 0.40 / x 0.08 → nao_ → nao_) | nao_ | nao_ | aten | — |
| CP-A10 | p3 | r4 | Mensalidade de até R$ 600 (`preco_total` <= 600). | num | — (— → aten) | aten | aten | aten | — |

## Conjunto `teste` — 20 disputas, 60 propostas, 234 células (arquivo versão 2026-10-02, autor fable)

### Matriz, elegíveis e perguntas — Jev + código × baseline, por desenho

`acerto_semantico` = células semânticas (Jev, depois da válvula) × gabarito; `acerto_numerico` = células numéricas pelo código; `classe_*` = acerto dentro de cada classe do gabarito. Erros caros: `exclusao_aprovada` = gabarito contradiz → atende (`_bruto` = antes da válvula); `inelegivel_elegivel` = proposta com contradiz obrigatório no gabarito que entrou em `elegiveis`. Secundários: `descartou_sem_perguntar` = gabarito nao_informado → contradiz; `falso_alarme` = atende → contradiz; `elegivel_fora` = elegível do gabarito que ficou fora. `valvula` = abstenções: células cuja leitura dura (`bruto`: opção da Choice; Nouls com corte em 0,5) decidia e a válvula/faixa mandou para nao_informado; `cobertura` = o resto; `erro_decididos` = erro entre as não movidas. `perguntas_*` = nao_informado em obrigatório de proposta ELEGÍVEL (o que a saída pergunta ao fornecedor) × gabarito, cada lado filtrado pela própria elegibilidade. `baseline` = palavra-chave + marca de exclusão na mesma frase.

| desenho | n_sem | n_num | acerto_semantico | acerto_numerico | acerto_total | classe_atende | classe_contradiz | classe_nao_informado | exclusao_aprovada | exclusao_aprovada_bruto | descartou_sem_perguntar | falso_alarme | valvula | cobertura | erro_decididos | inelegivel_elegivel | elegivel_fora | elegiveis_exatos | perguntas_precisao | perguntas_recall | baseline_semantico | baseline_exclusao_aprovada | falhas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| choice | 132 | 102 | 0.894 | 1.000 | 0.940 | 0.863 | 0.973 | 0.867 | 0/37 | 0/37 | 1/15 | 0/80 | 9 | 0.932 | 0.049 | 0/32 | 0/28 | 1.000 | 0.714 | 0.909 | 0.667 | 19/37 | 0 |

### Matriz de confusão (células semânticas) gabarito × previsto — `choice`

| gabarito \ previsto | atende | contradiz | nao_informado |
|---|---|---|---|
| atende | 69 | 0 | 11 |
| contradiz | 0 | 36 | 1 |
| nao_informado | 1 | 1 | 13 |

### Por família (prefixo da `nota`) — `choice`

| família | disputas | células_sem | acerto_semantico | exclusao_aprovada | descartou_sem_perguntar | elegiveis_exatos | baseline |
|---|---|---|---|---|---|---|---|
| anexo citado mas ausente | 2 | 15 | 0.933 | 0/4 | 0/3 | 1.000 | 0.667 |
| atende tudo menos o prazo | 1 | 6 | 0.833 | 0/2 | 0/1 | 1.000 | 0.500 |
| exclusão escondida | 5 | 33 | 0.939 | 0/9 | 0/1 | 1.000 | 0.788 |
| fácil | 2 | 15 | 0.800 | 0/5 | 0/0 | 1.000 | 0.667 |
| promessa condicionada | 2 | 15 | 0.867 | 0/4 | 1/4 | 1.000 | 0.533 |
| termo vago | 8 | 48 | 0.896 | 0/13 | 0/6 | 1.000 | 0.646 |

### Cobertura × erro por limiares (células semânticas; elegíveis recalculados) — `choice`

| CONF_ATENDE | CONF_CONTRADIZ | acerto_semantico | cobertura | erro_decididos | valvula | exclusao_aprovada | descartou_sem_perguntar | inelegivel_elegivel | elegiveis_exatos |
|---|---|---|---|---|---|---|---|---|---|
| 0.000 | 0.000 | 0.932 | 1.000 | 0.068 | 0 | 0/37 | 1/15 | 0/32 | 0.950 |
| 0.500 | 0.500 | 0.924 | 0.962 | 0.047 | 5 | 0/37 | 1/15 | 0/32 | 1.000 |
| 0.700 | 0.500 | 0.894 | 0.932 | 0.049 | 9 | 0/37 | 1/15 | 0/32 | 1.000 |
| 0.800 | 0.500 | 0.871 | 0.909 | 0.050 | 12 | 0/37 | 1/15 | 0/32 | 1.000 |
| 0.700 | 0.700 | 0.902 | 0.924 | 0.041 | 10 | 0/37 | 0/15 | 0/32 | 1.000 |
| 0.900 | 0.500 | 0.795 | 0.833 | 0.055 | 22 | 0/37 | 1/15 | 0/32 | 1.000 |
| 0.900 | 0.700 | 0.803 | 0.826 | 0.046 | 23 | 0/37 | 0/15 | 0/32 | 1.000 |
| 0.900 | 0.900 | 0.773 | 0.795 | 0.048 | 27 | 0/37 | 0/15 | 2/32 | 0.900 |

### Custo e latência (medidos na chamada real; do cache também)

Latência por REQUISIÇÃO (= por proposta). Mil disputas = 3 mil propostas comparadas.

| desenho | requisicoes | perguntas | p50_ms | p95_ms | tokens_por_proposta | US$_por_disputa | US$_por_mil_disputas | falhas_operacionais | modelo |
|---|---|---|---|---|---|---|---|---|---|
| choice | 60 | 132 | 273 | 459 | 3178 | 0.000400 | 0.4005 | 0 | jev-1.13.0 |

### Por proposta — elegível e perguntas — `choice`

| id | p | elegível gab | elegível prev | perguntas ao fornecedor |
|---|---|---|---|---|
| CP-T01 | p1 | True | True | — |
| CP-T01 | p2 | False | False | (inelegível) |
| CP-T01 | p3 | False | False | (inelegível) |
| CP-T02 | p1 | True | True | — |
| CP-T02 | p2 | False | False | (inelegível) |
| CP-T02 | p3 | False | False | (inelegível) |
| CP-T03 | p1 | True | True | — |
| CP-T03 | p2 | False | False | (inelegível) |
| CP-T03 | p3 | True | True | Confirmar, por escrito e dentro do preço cotado: Vídeo aéreo com drone de cada empreendimento, editado.; Confirmar, por escrito e dentro do preço cotado: Piloto com cadastro na ANAC e seguro do equipamento. |
| CP-T04 | p1 | True | True | — |
| CP-T04 | p2 | False | False | (inelegível) |
| CP-T04 | p3 | False | False | (inelegível) |
| CP-T05 | p1 | True | True | — |
| CP-T05 | p2 | False | False | (inelegível) |
| CP-T05 | p3 | True | True | Confirmar, por escrito e dentro do preço cotado: Treinamento presencial de vendas para 15 corretores.; Informar a quantidade de horas — requisito: Carga horária de pelo menos 16 horas. |
| CP-T06 | p1 | False | False | (inelegível) |
| CP-T06 | p2 | False | False | (inelegível) |
| CP-T06 | p3 | False | False | (inelegível) |
| CP-T07 | p1 | True | True | — |
| CP-T07 | p2 | False | False | (inelegível) |
| CP-T07 | p3 | False | False | (inelegível) |
| CP-T08 | p1 | True | True | — |
| CP-T08 | p2 | False | False | (inelegível) |
| CP-T08 | p3 | True | True | Confirmar, por escrito e dentro do preço cotado: Treinamento da equipe sobre LGPD. |
| CP-T09 | p1 | True | True | Confirmar, por escrito e dentro do preço cotado: Gerador a diesel com partida automática (QTA). |
| CP-T09 | p2 | False | False | (inelegível) |
| CP-T09 | p3 | False | False | (inelegível) |
| CP-T10 | p1 | True | True | Confirmar, por escrito e dentro do preço cotado: Insumos (café, leite, copos) inclusos na mensalidade. |
| CP-T10 | p2 | False | False | (inelegível) |
| CP-T10 | p3 | False | False | (inelegível) |
| CP-T11 | p1 | True | True | — |
| CP-T11 | p2 | False | False | (inelegível) |
| CP-T11 | p3 | False | False | (inelegível) |
| CP-T12 | p1 | True | True | — |
| CP-T12 | p2 | False | False | (inelegível) |
| CP-T12 | p3 | True | True | Confirmar, por escrito e dentro do preço cotado: Integração com o CRM atual (API). |
| CP-T13 | p1 | True | True | — |
| CP-T13 | p2 | False | False | (inelegível) |
| CP-T13 | p3 | False | False | (inelegível) |
| CP-T14 | p1 | True | True | — |
| CP-T14 | p2 | False | False | (inelegível) |
| CP-T14 | p3 | False | False | (inelegível) |
| CP-T15 | p1 | True | True | — |
| CP-T15 | p2 | False | False | (inelegível) |
| CP-T15 | p3 | True | True | Confirmar, por escrito e dentro do preço cotado: Manutenção quinzenal por 6 meses inclusa. |
| CP-T16 | p1 | True | True | — |
| CP-T16 | p2 | False | False | (inelegível) |
| CP-T16 | p3 | True | True | Confirmar, por escrito e dentro do preço cotado: Entregas de documentos com motoboy em até 3 horas na cidade.; Confirmar, por escrito e dentro do preço cotado: Comprovante de entrega com foto e assinatura. |
| CP-T17 | p1 | True | True | — |
| CP-T17 | p2 | False | False | (inelegível) |
| CP-T17 | p3 | False | False | (inelegível) |
| CP-T18 | p1 | True | True | — |
| CP-T18 | p2 | False | False | (inelegível) |
| CP-T18 | p3 | True | True | Informar o prazo de reparo em horas — requisito: SLA de reparo de até 4 horas. |
| CP-T19 | p1 | True | True | — |
| CP-T19 | p2 | True | True | Confirmar, por escrito e dentro do preço cotado: Equipe com registro na CVM. |
| CP-T19 | p3 | False | False | (inelegível) |
| CP-T20 | p1 | True | True | — |
| CP-T20 | p2 | False | False | (inelegível) |
| CP-T20 | p3 | True | True | Informar o prazo de substituição em horas — requisito: Substituição em até 24 horas em caso de defeito. |

### Célula a célula — `choice`

`jev` = opção bruta (confiança) ou Nouls entrega/exclui → leitura dura; `marca`: `caro` = exclusão aprovada (contradiz → atende); `desc` = descartou sem perguntar (nao_informado → contradiz); `erro` = outra célula errada.

| id | p | r | requisito | tipo | jev | célula | gab | bl | marca |
|---|---|---|---|---|---|---|---|---|---|
| CP-T01 | p1 | r1 | Instalação e configuração das impressoras inclusas. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T01 | p1 | r2 | Toner e manutenção inclusos na mensalidade. | sem | aten (0.97) | aten | aten | aten | — |
| CP-T01 | p1 | r3 | Franquia mínima de 5 mil páginas por mês (`paginas_mes` >= 5 | num | — | aten | aten | aten | — |
| CP-T01 | p1 | r4 | Mensalidade de até R$ 1.200 (`preco_total` <= 1200). | num | — | aten | aten | aten | — |
| CP-T01 | p2 | r1 | Instalação e configuração das impressoras inclusas. | sem | aten (0.88) | aten | aten | aten | — |
| CP-T01 | p2 | r2 | Toner e manutenção inclusos na mensalidade. | sem | cont (0.97) | cont | cont | aten | — |
| CP-T01 | p2 | r3 | Franquia mínima de 5 mil páginas por mês (`paginas_mes` >= 5 | num | — | aten | aten | aten | — |
| CP-T01 | p2 | r4 | Mensalidade de até R$ 1.200 (`preco_total` <= 1200). | num | — | aten | aten | aten | — |
| CP-T01 | p3 | r1 | Instalação e configuração das impressoras inclusas. | sem | aten (0.92) | aten | aten | aten | — |
| CP-T01 | p3 | r2 | Toner e manutenção inclusos na mensalidade. | sem | aten (0.88) | aten | aten | aten | — |
| CP-T01 | p3 | r3 | Franquia mínima de 5 mil páginas por mês (`paginas_mes` >= 5 | num | — | cont | cont | cont | — |
| CP-T01 | p3 | r4 | Mensalidade de até R$ 1.200 (`preco_total` <= 1200). | num | — | aten | aten | aten | — |
| CP-T02 | p1 | r1 | Pintura interna de todas as salas com tinta lavável. | sem | aten (0.74) | aten | aten | cont | — |
| CP-T02 | p1 | r2 | Serviço executado fora do horário comercial (noite ou fim de | sem | aten (1.00) | aten | aten | cont | — |
| CP-T02 | p1 | r3 | Prazo de até 10 dias (`prazo_dias` <= 10). | num | — | aten | aten | aten | — |
| CP-T02 | p1 | r4 | Preço total de até R$ 12.000 (`preco_total` <= 12000). | num | — | aten | aten | aten | — |
| CP-T02 | p2 | r1 | Pintura interna de todas as salas com tinta lavável. | sem | cont (0.53) | cont | nao_ | aten | desc |
| CP-T02 | p2 | r2 | Serviço executado fora do horário comercial (noite ou fim de | sem | cont (1.00) | cont | cont | aten | — |
| CP-T02 | p2 | r3 | Prazo de até 10 dias (`prazo_dias` <= 10). | num | — | aten | aten | aten | — |
| CP-T02 | p2 | r4 | Preço total de até R$ 12.000 (`preco_total` <= 12000). | num | — | aten | aten | aten | — |
| CP-T02 | p3 | r1 | Pintura interna de todas as salas com tinta lavável. | sem | aten (0.49) | nao_ | aten | aten | erro |
| CP-T02 | p3 | r2 | Serviço executado fora do horário comercial (noite ou fim de | sem | cont (0.99) | cont | cont | aten | — |
| CP-T02 | p3 | r3 | Prazo de até 10 dias (`prazo_dias` <= 10). | num | — | cont | cont | cont | — |
| CP-T02 | p3 | r4 | Preço total de até R$ 12.000 (`preco_total` <= 12000). | num | — | aten | aten | aten | — |
| CP-T03 | p1 | r1 | Vídeo aéreo com drone de cada empreendimento, editado. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T03 | p1 | r2 | Piloto com cadastro na ANAC e seguro do equipamento. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T03 | p1 | r3 | Entrega em até 7 dias após a captação (`prazo_dias` <= 7). | num | — | aten | aten | aten | — |
| CP-T03 | p1 | r4 | Preço por empreendimento de até R$ 1.500 (`preco_total` <= 1 | num | — | aten | aten | aten | — |
| CP-T03 | p2 | r1 | Vídeo aéreo com drone de cada empreendimento, editado. | sem | cont (0.93) | cont | cont | aten | — |
| CP-T03 | p2 | r2 | Piloto com cadastro na ANAC e seguro do equipamento. | sem | nao_ (0.98) | nao_ | nao_ | aten | — |
| CP-T03 | p2 | r3 | Entrega em até 7 dias após a captação (`prazo_dias` <= 7). | num | — | aten | aten | aten | — |
| CP-T03 | p2 | r4 | Preço por empreendimento de até R$ 1.500 (`preco_total` <= 1 | num | — | aten | aten | aten | — |
| CP-T03 | p3 | r1 | Vídeo aéreo com drone de cada empreendimento, editado. | sem | aten (0.53) | nao_ | aten | aten | erro |
| CP-T03 | p3 | r2 | Piloto com cadastro na ANAC e seguro do equipamento. | sem | nao_ (0.90) | nao_ | nao_ | aten | — |
| CP-T03 | p3 | r3 | Entrega em até 7 dias após a captação (`prazo_dias` <= 7). | num | — | cont | cont | cont | — |
| CP-T03 | p3 | r4 | Preço por empreendimento de até R$ 1.500 (`preco_total` <= 1 | num | — | aten | aten | aten | — |
| CP-T04 | p1 | r1 | Cobertura contra incêndio, roubo e danos elétricos. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T04 | p1 | r2 | Responsabilidade civil para visitantes do escritório. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T04 | p1 | r3 | Franquia de até R$ 2.000 por sinistro (`franquia` <= 2000). | num | — | aten | aten | aten | — |
| CP-T04 | p1 | r4 | Prêmio anual de até R$ 4.500 (`preco_total` <= 4500). | num | — | aten | aten | aten | — |
| CP-T04 | p2 | r1 | Cobertura contra incêndio, roubo e danos elétricos. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T04 | p2 | r2 | Responsabilidade civil para visitantes do escritório. | sem | cont (1.00) | cont | cont | nao_ | — |
| CP-T04 | p2 | r3 | Franquia de até R$ 2.000 por sinistro (`franquia` <= 2000). | num | — | aten | aten | aten | — |
| CP-T04 | p2 | r4 | Prêmio anual de até R$ 4.500 (`preco_total` <= 4500). | num | — | aten | aten | aten | — |
| CP-T04 | p3 | r1 | Cobertura contra incêndio, roubo e danos elétricos. | sem | aten (0.98) | aten | aten | aten | — |
| CP-T04 | p3 | r2 | Responsabilidade civil para visitantes do escritório. | sem | aten (0.97) | aten | aten | nao_ | — |
| CP-T04 | p3 | r3 | Franquia de até R$ 2.000 por sinistro (`franquia` <= 2000). | num | — | cont | cont | cont | — |
| CP-T04 | p3 | r4 | Prêmio anual de até R$ 4.500 (`preco_total` <= 4500). | num | — | aten | aten | aten | — |
| CP-T05 | p1 | r1 | Treinamento presencial de vendas para 15 corretores. | sem | aten (0.88) | aten | aten | aten | — |
| CP-T05 | p1 | r2 | Material didático incluso. | sem | aten (0.98) | aten | aten | nao_ | — |
| CP-T05 | p1 | r3 | Carga horária de pelo menos 16 horas (`horas` >= 16). | num | — | aten | aten | aten | — |
| CP-T05 | p1 | r4 | Preço total de até R$ 9.000 (`preco_total` <= 9000). | num | — | aten | aten | aten | — |
| CP-T05 | p2 | r1 | Treinamento presencial de vendas para 15 corretores. | sem | cont (0.99) | cont | cont | aten | — |
| CP-T05 | p2 | r2 | Material didático incluso. | sem | aten (0.98) | aten | aten | aten | — |
| CP-T05 | p2 | r3 | Carga horária de pelo menos 16 horas (`horas` >= 16). | num | — | cont | cont | cont | — |
| CP-T05 | p2 | r4 | Preço total de até R$ 9.000 (`preco_total` <= 9000). | num | — | aten | aten | aten | — |
| CP-T05 | p3 | r1 | Treinamento presencial de vendas para 15 corretores. | sem | aten (0.13) | nao_ | nao_ | aten | — |
| CP-T05 | p3 | r2 | Material didático incluso. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T05 | p3 | r3 | Carga horária de pelo menos 16 horas (`horas` >= 16). | num | — | nao_ | nao_ | nao_ | — |
| CP-T05 | p3 | r4 | Preço total de até R$ 9.000 (`preco_total` <= 9000). | num | — | aten | aten | aten | — |
| CP-T06 | p1 | r1 | Manutenção mensal preventiva dos 2 elevadores. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T06 | p1 | r2 | Atendimento de emergência 24h com chegada em até 2 horas. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T06 | p1 | r3 | Peças de reposição inclusas no contrato. | sem | cont (0.99) | cont | cont | cont | — |
| CP-T06 | p1 | r4 | Mensalidade de até R$ 2.200 (`preco_total` <= 2200). | num | — | aten | aten | aten | — |
| CP-T06 | p2 | r1 | Manutenção mensal preventiva dos 2 elevadores. | sem | nao_ (0.48) | nao_ | aten | aten | erro |
| CP-T06 | p2 | r2 | Atendimento de emergência 24h com chegada em até 2 horas. | sem | nao_ (0.89) | nao_ | nao_ | aten | — |
| CP-T06 | p2 | r3 | Peças de reposição inclusas no contrato. | sem | aten (0.92) | aten | aten | cont | — |
| CP-T06 | p2 | r4 | Mensalidade de até R$ 2.200 (`preco_total` <= 2200). | num | — | cont | cont | cont | — |
| CP-T06 | p3 | r1 | Manutenção mensal preventiva dos 2 elevadores. | sem | aten (0.93) | aten | aten | aten | — |
| CP-T06 | p3 | r2 | Atendimento de emergência 24h com chegada em até 2 horas. | sem | aten (0.98) | aten | aten | aten | — |
| CP-T06 | p3 | r3 | Peças de reposição inclusas no contrato. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T06 | p3 | r4 | Mensalidade de até R$ 2.200 (`preco_total` <= 2200). | num | — | aten | aten | aten | — |
| CP-T07 | p1 | r1 | Buffet para 120 pessoas com opção vegetariana. | sem | aten (0.75) | aten | aten | aten | — |
| CP-T07 | p1 | r2 | Garçons e louça inclusos. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T07 | p1 | r3 | Bebidas não alcoólicas inclusas. | sem | aten (1.00) | aten | aten | nao_ | — |
| CP-T07 | p1 | r4 | Preço total de até R$ 15.000 (`preco_total` <= 15000). | num | — | aten | aten | aten | — |
| CP-T07 | p2 | r1 | Buffet para 120 pessoas com opção vegetariana. | sem | nao_ (0.76) | nao_ | nao_ | aten | — |
| CP-T07 | p2 | r2 | Garçons e louça inclusos. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T07 | p2 | r3 | Bebidas não alcoólicas inclusas. | sem | cont (0.88) | cont | cont | cont | — |
| CP-T07 | p2 | r4 | Preço total de até R$ 15.000 (`preco_total` <= 15000). | num | — | aten | aten | aten | — |
| CP-T07 | p3 | r1 | Buffet para 120 pessoas com opção vegetariana. | sem | cont (0.27) | nao_ | aten | aten | erro |
| CP-T07 | p3 | r2 | Garçons e louça inclusos. | sem | aten (1.00) | aten | aten | cont | — |
| CP-T07 | p3 | r3 | Bebidas não alcoólicas inclusas. | sem | aten (1.00) | aten | aten | cont | — |
| CP-T07 | p3 | r4 | Preço total de até R$ 15.000 (`preco_total` <= 15000). | num | — | cont | cont | cont | — |
| CP-T08 | p1 | r1 | Mapeamento dos dados pessoais e relatório de impacto (RIPD). | sem | aten (0.99) | aten | aten | aten | — |
| CP-T08 | p1 | r2 | Treinamento da equipe sobre LGPD. | sem | aten (0.98) | aten | aten | aten | — |
| CP-T08 | p1 | r3 | Atuação como encarregado (DPO) terceirizado por 12 meses. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T08 | p1 | r4 | Preço total de até R$ 25.000 (`preco_total` <= 25000). | num | — | aten | aten | aten | — |
| CP-T08 | p2 | r1 | Mapeamento dos dados pessoais e relatório de impacto (RIPD). | sem | cont (0.89) | cont | cont | aten | — |
| CP-T08 | p2 | r2 | Treinamento da equipe sobre LGPD. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T08 | p2 | r3 | Atuação como encarregado (DPO) terceirizado por 12 meses. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T08 | p2 | r4 | Preço total de até R$ 25.000 (`preco_total` <= 25000). | num | — | aten | aten | aten | — |
| CP-T08 | p3 | r1 | Mapeamento dos dados pessoais e relatório de impacto (RIPD). | sem | aten (0.96) | aten | aten | aten | — |
| CP-T08 | p3 | r2 | Treinamento da equipe sobre LGPD. | sem | nao_ (0.26) | nao_ | nao_ | aten | — |
| CP-T08 | p3 | r3 | Atuação como encarregado (DPO) terceirizado por 12 meses. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T08 | p3 | r4 | Preço total de até R$ 25.000 (`preco_total` <= 25000). | num | — | aten | aten | aten | — |
| CP-T09 | p1 | r1 | Gerador a diesel com partida automática (QTA). | sem | nao_ (0.44) | nao_ | aten | aten | erro |
| CP-T09 | p1 | r2 | Instalação e ligação ao quadro inclusas. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T09 | p1 | r3 | Potência de pelo menos 60 kVA (`kva` >= 60). | num | — | aten | aten | aten | — |
| CP-T09 | p1 | r4 | Preço total de até R$ 70.000 (`preco_total` <= 70000). | num | — | aten | aten | aten | — |
| CP-T09 | p2 | r1 | Gerador a diesel com partida automática (QTA). | sem | cont (1.00) | cont | cont | aten | — |
| CP-T09 | p2 | r2 | Instalação e ligação ao quadro inclusas. | sem | aten (0.88) | aten | aten | cont | — |
| CP-T09 | p2 | r3 | Potência de pelo menos 60 kVA (`kva` >= 60). | num | — | aten | aten | aten | — |
| CP-T09 | p2 | r4 | Preço total de até R$ 70.000 (`preco_total` <= 70000). | num | — | aten | aten | aten | — |
| CP-T09 | p3 | r1 | Gerador a diesel com partida automática (QTA). | sem | aten (0.39) | nao_ | aten | aten | erro |
| CP-T09 | p3 | r2 | Instalação e ligação ao quadro inclusas. | sem | cont (1.00) | cont | cont | aten | — |
| CP-T09 | p3 | r3 | Potência de pelo menos 60 kVA (`kva` >= 60). | num | — | aten | aten | aten | — |
| CP-T09 | p3 | r4 | Preço total de até R$ 70.000 (`preco_total` <= 70000). | num | — | aten | aten | aten | — |
| CP-T10 | p1 | r1 | Máquinas de café em comodato com manutenção inclusa. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T10 | p1 | r2 | Insumos (café, leite, copos) inclusos na mensalidade. | sem | cont (0.19) | nao_ | aten | aten | erro |
| CP-T10 | p1 | r3 | Mensalidade de até R$ 900 (`preco_total` <= 900). | num | — | aten | aten | aten | — |
| CP-T10 | p1 | r4 | Troca da máquina em até 48 horas em caso de defeito (`prazo_ | num | — | aten | aten | aten | — |
| CP-T10 | p2 | r1 | Máquinas de café em comodato com manutenção inclusa. | sem | aten (0.94) | aten | aten | aten | — |
| CP-T10 | p2 | r2 | Insumos (café, leite, copos) inclusos na mensalidade. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T10 | p2 | r3 | Mensalidade de até R$ 900 (`preco_total` <= 900). | num | — | aten | aten | aten | — |
| CP-T10 | p2 | r4 | Troca da máquina em até 48 horas em caso de defeito (`prazo_ | num | — | cont | cont | cont | — |
| CP-T10 | p3 | r1 | Máquinas de café em comodato com manutenção inclusa. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T10 | p3 | r2 | Insumos (café, leite, copos) inclusos na mensalidade. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T10 | p3 | r3 | Mensalidade de até R$ 900 (`preco_total` <= 900). | num | — | cont | cont | cont | — |
| CP-T10 | p3 | r4 | Troca da máquina em até 48 horas em caso de defeito (`prazo_ | num | — | nao_ | nao_ | nao_ | — |
| CP-T11 | p1 | r1 | Mudança do escritório com embalagem e desmontagem/montagem d | sem | aten (0.89) | aten | aten | aten | — |
| CP-T11 | p1 | r2 | Seguro da carga incluso. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T11 | p1 | r3 | Execução em um único fim de semana. | sem | aten (0.98) | aten | aten | aten | — |
| CP-T11 | p1 | r4 | Preço total de até R$ 8.000 (`preco_total` <= 8000). | num | — | aten | aten | aten | — |
| CP-T11 | p2 | r1 | Mudança do escritório com embalagem e desmontagem/montagem d | sem | cont (0.98) | cont | cont | aten | — |
| CP-T11 | p2 | r2 | Seguro da carga incluso. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T11 | p2 | r3 | Execução em um único fim de semana. | sem | aten (0.59) | nao_ | aten | aten | erro |
| CP-T11 | p2 | r4 | Preço total de até R$ 8.000 (`preco_total` <= 8000). | num | — | aten | aten | aten | — |
| CP-T11 | p3 | r1 | Mudança do escritório com embalagem e desmontagem/montagem d | sem | aten (0.96) | aten | aten | aten | — |
| CP-T11 | p3 | r2 | Seguro da carga incluso. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T11 | p3 | r3 | Execução em um único fim de semana. | sem | cont (0.94) | cont | cont | aten | — |
| CP-T11 | p3 | r4 | Preço total de até R$ 8.000 (`preco_total` <= 8000). | num | — | aten | aten | aten | — |
| CP-T12 | p1 | r1 | Chatbot de WhatsApp com transferência para atendente humano. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T12 | p1 | r2 | Integração com o CRM atual (API). | sem | aten (0.85) | aten | aten | aten | — |
| CP-T12 | p1 | r3 | Número oficial da API do WhatsApp (não app comum). | sem | aten (0.78) | aten | aten | aten | — |
| CP-T12 | p1 | r4 | Mensalidade de até R$ 700 (`preco_total` <= 700). | num | — | aten | aten | aten | — |
| CP-T12 | p2 | r1 | Chatbot de WhatsApp com transferência para atendente humano. | sem | aten (0.97) | aten | aten | aten | — |
| CP-T12 | p2 | r2 | Integração com o CRM atual (API). | sem | cont (0.94) | cont | cont | aten | — |
| CP-T12 | p2 | r3 | Número oficial da API do WhatsApp (não app comum). | sem | cont (0.97) | cont | cont | aten | — |
| CP-T12 | p2 | r4 | Mensalidade de até R$ 700 (`preco_total` <= 700). | num | — | aten | aten | aten | — |
| CP-T12 | p3 | r1 | Chatbot de WhatsApp com transferência para atendente humano. | sem | aten (0.96) | aten | aten | aten | — |
| CP-T12 | p3 | r2 | Integração com o CRM atual (API). | sem | nao_ (0.43) | nao_ | nao_ | aten | — |
| CP-T12 | p3 | r3 | Número oficial da API do WhatsApp (não app comum). | sem | aten (0.93) | aten | aten | aten | — |
| CP-T12 | p3 | r4 | Mensalidade de até R$ 700 (`preco_total` <= 700). | num | — | aten | aten | aten | — |
| CP-T13 | p1 | r1 | Piso vinílico em régua, com instalação inclusa. | sem | aten (0.98) | aten | aten | aten | — |
| CP-T13 | p1 | r2 | Remoção e descarte do carpete atual inclusos. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T13 | p1 | r3 | Prazo de até 5 dias (`prazo_dias` <= 5). | num | — | aten | aten | aten | — |
| CP-T13 | p1 | r4 | Preço total de até R$ 22.000 (`preco_total` <= 22000). | num | — | aten | aten | aten | — |
| CP-T13 | p2 | r1 | Piso vinílico em régua, com instalação inclusa. | sem | aten (0.97) | aten | aten | aten | — |
| CP-T13 | p2 | r2 | Remoção e descarte do carpete atual inclusos. | sem | cont (0.93) | cont | cont | cont | — |
| CP-T13 | p2 | r3 | Prazo de até 5 dias (`prazo_dias` <= 5). | num | — | aten | aten | aten | — |
| CP-T13 | p2 | r4 | Preço total de até R$ 22.000 (`preco_total` <= 22000). | num | — | aten | aten | aten | — |
| CP-T13 | p3 | r1 | Piso vinílico em régua, com instalação inclusa. | sem | cont (0.98) | cont | cont | aten | — |
| CP-T13 | p3 | r2 | Remoção e descarte do carpete atual inclusos. | sem | aten (0.50) | nao_ | aten | aten | erro |
| CP-T13 | p3 | r3 | Prazo de até 5 dias (`prazo_dias` <= 5). | num | — | aten | aten | aten | — |
| CP-T13 | p3 | r4 | Preço total de até R$ 22.000 (`preco_total` <= 22000). | num | — | aten | aten | aten | — |
| CP-T14 | p1 | r1 | Uniformes com bordado do logotipo. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T14 | p1 | r2 | Amostra para aprovação antes da produção. | sem | aten (0.94) | aten | aten | aten | — |
| CP-T14 | p1 | r3 | Entrega em até 25 dias (`prazo_dias` <= 25). | num | — | aten | aten | aten | — |
| CP-T14 | p1 | r4 | Preço total de até R$ 6.000 (`preco_total` <= 6000). | num | — | aten | aten | aten | — |
| CP-T14 | p2 | r1 | Uniformes com bordado do logotipo. | sem | cont (0.97) | cont | cont | aten | — |
| CP-T14 | p2 | r2 | Amostra para aprovação antes da produção. | sem | cont (0.89) | cont | cont | nao_ | — |
| CP-T14 | p2 | r3 | Entrega em até 25 dias (`prazo_dias` <= 25). | num | — | aten | aten | aten | — |
| CP-T14 | p2 | r4 | Preço total de até R$ 6.000 (`preco_total` <= 6000). | num | — | aten | aten | aten | — |
| CP-T14 | p3 | r1 | Uniformes com bordado do logotipo. | sem | nao_ (0.61) | nao_ | aten | aten | erro |
| CP-T14 | p3 | r2 | Amostra para aprovação antes da produção. | sem | nao_ (0.67) | nao_ | nao_ | aten | — |
| CP-T14 | p3 | r3 | Entrega em até 25 dias (`prazo_dias` <= 25). | num | — | cont | cont | cont | — |
| CP-T14 | p3 | r4 | Preço total de até R$ 6.000 (`preco_total` <= 6000). | num | — | aten | aten | aten | — |
| CP-T15 | p1 | r1 | Paisagismo da entrada com irrigação automática. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T15 | p1 | r2 | Manutenção quinzenal por 6 meses inclusa. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T15 | p1 | r3 | Preço total de até R$ 14.000 (`preco_total` <= 14000). | num | — | aten | aten | aten | — |
| CP-T15 | p2 | r1 | Paisagismo da entrada com irrigação automática. | sem | cont (0.98) | cont | cont | aten | — |
| CP-T15 | p2 | r2 | Manutenção quinzenal por 6 meses inclusa. | sem | cont (1.00) | cont | cont | aten | — |
| CP-T15 | p2 | r3 | Preço total de até R$ 14.000 (`preco_total` <= 14000). | num | — | aten | aten | aten | — |
| CP-T15 | p3 | r1 | Paisagismo da entrada com irrigação automática. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T15 | p3 | r2 | Manutenção quinzenal por 6 meses inclusa. | sem | nao_ (0.94) | nao_ | nao_ | aten | — |
| CP-T15 | p3 | r3 | Preço total de até R$ 14.000 (`preco_total` <= 14000). | num | — | aten | aten | aten | — |
| CP-T16 | p1 | r1 | Entregas de documentos com motoboy em até 3 horas na cidade. | sem | aten (0.87) | aten | aten | aten | — |
| CP-T16 | p1 | r2 | Comprovante de entrega com foto e assinatura. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T16 | p1 | r3 | Mensalidade de até R$ 1.800 para 60 entregas (`preco_total`  | num | — | aten | aten | aten | — |
| CP-T16 | p2 | r1 | Entregas de documentos com motoboy em até 3 horas na cidade. | sem | nao_ (0.24) | nao_ | cont | aten | erro |
| CP-T16 | p2 | r2 | Comprovante de entrega com foto e assinatura. | sem | cont (0.86) | cont | cont | aten | — |
| CP-T16 | p2 | r3 | Mensalidade de até R$ 1.800 para 60 entregas (`preco_total`  | num | — | aten | aten | aten | — |
| CP-T16 | p3 | r1 | Entregas de documentos com motoboy em até 3 horas na cidade. | sem | aten (0.65) | nao_ | aten | aten | erro |
| CP-T16 | p3 | r2 | Comprovante de entrega com foto e assinatura. | sem | nao_ (0.85) | nao_ | nao_ | aten | — |
| CP-T16 | p3 | r3 | Mensalidade de até R$ 1.800 para 60 entregas (`preco_total`  | num | — | aten | aten | aten | — |
| CP-T17 | p1 | r1 | Placas de fachada em ACM com iluminação em LED. | sem | aten (0.97) | aten | aten | aten | — |
| CP-T17 | p1 | r2 | Instalação inclusa, com ART. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T17 | p1 | r3 | Garantia de pelo menos 24 meses (`garantia_meses` >= 24). | num | — | aten | aten | aten | — |
| CP-T17 | p1 | r4 | Preço total de até R$ 16.000 (`preco_total` <= 16000). | num | — | aten | aten | aten | — |
| CP-T17 | p2 | r1 | Placas de fachada em ACM com iluminação em LED. | sem | aten (0.81) | aten | aten | aten | — |
| CP-T17 | p2 | r2 | Instalação inclusa, com ART. | sem | cont (0.96) | cont | cont | aten | — |
| CP-T17 | p2 | r3 | Garantia de pelo menos 24 meses (`garantia_meses` >= 24). | num | — | cont | cont | cont | — |
| CP-T17 | p2 | r4 | Preço total de até R$ 16.000 (`preco_total` <= 16000). | num | — | aten | aten | aten | — |
| CP-T17 | p3 | r1 | Placas de fachada em ACM com iluminação em LED. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T17 | p3 | r2 | Instalação inclusa, com ART. | sem | aten (0.89) | aten | aten | aten | — |
| CP-T17 | p3 | r3 | Garantia de pelo menos 24 meses (`garantia_meses` >= 24). | num | — | aten | aten | aten | — |
| CP-T17 | p3 | r4 | Preço total de até R$ 16.000 (`preco_total` <= 16000). | num | — | aten | aten | aten | — |
| CP-T18 | p1 | r1 | Internet dedicada com IP fixo. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T18 | p1 | r2 | SLA de reparo de até 4 horas (`sla_horas` <= 4). | num | — | aten | aten | aten | — |
| CP-T18 | p1 | r3 | Velocidade de pelo menos 200 Mbps (`mbps` >= 200). | num | — | aten | aten | aten | — |
| CP-T18 | p1 | r4 | Mensalidade de até R$ 1.200 (`preco_total` <= 1200). | num | — | aten | aten | aten | — |
| CP-T18 | p2 | r1 | Internet dedicada com IP fixo. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T18 | p2 | r2 | SLA de reparo de até 4 horas (`sla_horas` <= 4). | num | — | cont | cont | cont | — |
| CP-T18 | p2 | r3 | Velocidade de pelo menos 200 Mbps (`mbps` >= 200). | num | — | aten | aten | aten | — |
| CP-T18 | p2 | r4 | Mensalidade de até R$ 1.200 (`preco_total` <= 1200). | num | — | aten | aten | aten | — |
| CP-T18 | p3 | r1 | Internet dedicada com IP fixo. | sem | aten (1.00) | aten | aten | aten | — |
| CP-T18 | p3 | r2 | SLA de reparo de até 4 horas (`sla_horas` <= 4). | num | — | nao_ | nao_ | nao_ | — |
| CP-T18 | p3 | r3 | Velocidade de pelo menos 200 Mbps (`mbps` >= 200). | num | — | aten | aten | aten | — |
| CP-T18 | p3 | r4 | Mensalidade de até R$ 1.200 (`preco_total` <= 1200). | num | — | aten | aten | aten | — |
| CP-T19 | p1 | r1 | Auditoria anual das demonstrações com parecer assinado. | sem | aten (0.97) | aten | aten | aten | — |
| CP-T19 | p1 | r2 | Revisão trimestral dos controles internos. | sem | aten (0.99) | aten | aten | aten | — |
| CP-T19 | p1 | r3 | Equipe com registro na CVM. | sem | aten (0.93) | aten | aten | aten | — |
| CP-T19 | p1 | r4 | Honorários anuais de até R$ 40.000 (`preco_total` <= 40000). | num | — | aten | aten | aten | — |
| CP-T19 | p2 | r1 | Auditoria anual das demonstrações com parecer assinado. | sem | aten (0.80) | aten | aten | aten | — |
| CP-T19 | p2 | r2 | Revisão trimestral dos controles internos. | sem | cont (0.94) | cont | cont | cont | — |
| CP-T19 | p2 | r3 | Equipe com registro na CVM. | sem | nao_ (0.98) | nao_ | nao_ | aten | — |
| CP-T19 | p2 | r4 | Honorários anuais de até R$ 40.000 (`preco_total` <= 40000). | num | — | aten | aten | aten | — |
| CP-T19 | p3 | r1 | Auditoria anual das demonstrações com parecer assinado. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T19 | p3 | r2 | Revisão trimestral dos controles internos. | sem | nao_ (0.47) | nao_ | nao_ | aten | — |
| CP-T19 | p3 | r3 | Equipe com registro na CVM. | sem | nao_ (0.98) | nao_ | nao_ | nao_ | — |
| CP-T19 | p3 | r4 | Honorários anuais de até R$ 40.000 (`preco_total` <= 40000). | num | — | aten | aten | aten | — |
| CP-T20 | p1 | r1 | Locação de 5 notebooks com Windows e Office licenciados. | sem | aten (0.98) | aten | aten | aten | — |
| CP-T20 | p1 | r2 | Substituição em até 24 horas em caso de defeito (`troca_hora | num | — | aten | aten | aten | — |
| CP-T20 | p1 | r3 | Prazo mínimo de contrato de no máximo 12 meses (`contrato_me | num | — | aten | aten | aten | — |
| CP-T20 | p1 | r4 | Mensalidade de até R$ 1.000 (`preco_total` <= 1000). | num | — | aten | aten | aten | — |
| CP-T20 | p2 | r1 | Locação de 5 notebooks com Windows e Office licenciados. | sem | cont (1.00) | cont | cont | cont | — |
| CP-T20 | p2 | r2 | Substituição em até 24 horas em caso de defeito (`troca_hora | num | — | cont | cont | cont | — |
| CP-T20 | p2 | r3 | Prazo mínimo de contrato de no máximo 12 meses (`contrato_me | num | — | cont | cont | cont | — |
| CP-T20 | p2 | r4 | Mensalidade de até R$ 1.000 (`preco_total` <= 1000). | num | — | aten | aten | aten | — |
| CP-T20 | p3 | r1 | Locação de 5 notebooks com Windows e Office licenciados. | sem | aten (0.92) | aten | nao_ | aten | erro |
| CP-T20 | p3 | r2 | Substituição em até 24 horas em caso de defeito (`troca_hora | num | — | nao_ | nao_ | nao_ | — |
| CP-T20 | p3 | r3 | Prazo mínimo de contrato de no máximo 12 meses (`contrato_me | num | — | aten | aten | aten | — |
| CP-T20 | p3 | r4 | Mensalidade de até R$ 1.000 (`preco_total` <= 1000). | num | — | aten | aten | aten | — |
