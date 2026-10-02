# Resultados — conferencia-de-promessas

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Perguntas, limiares, glosas e baseline: `perguntas.py`; comparação numérica e composição: `conferir.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Desenho padrão: `choice`; CONF_MANTER 0.7, CONF_RETIRAR 0.5.

Critério de continuar/descartar (fixado antes do teste): no teste, com o desenho padrão e os limiares acima: (1) numericas puras pelo código 100% (menos é bug); (2) acerto relacao código + Jev, resposta dura, ≥ baseline + 15 p.p.; (3) promessa inventada gabarito contradicted/not_stated → manter ≤ 3% dessas afirmações; (4) cobertura manter ou retirar sem humano ≥ 75%.

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T23:52:27-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 e717ed831fd15d91… · `conferir.py` sha256 8606bd531793b516… · `run.py` sha256 587181f6e1473606… · `dados/teste.json` sha256 c3f34fe6be0329f0…

## Lado a lado

### Relação, ação e erro caro — Jev + código × baseline

| conjunto | desenho | afirmações | acerto_relacao | baseline | cobertura | erro_decididos | revisar | erro_caro | erro_caro_duro | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | choice | 104 | 0.962 | 0.788 | 0.933 | 0.010 | 7 | 0/48 | 0/48 | 10/48 |
| ajuste | choice+topico | 104 | 0.962 | 0.788 | 0.952 | 0.010 | 5 | 0/48 | 0/48 | 10/48 |
| teste | choice | 200 | 0.930 | 0.720 | 0.950 | 0.032 | 10 | 1/88 | 5/88 | 27/88 |

### Numéricas pelo código, latência e custo

| conjunto | desenho | fichas | numéricas_código | requisicoes | p50_ms | p95_ms | tokens_por_ficha | US$_por_ficha | US$_por_mil_fichas | modelo |
|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | choice | 30 | 32 (1.000) | 28 | 280 | 383 | 2101 | 0.0000882 | 0.0882 | jev-1.13.0 |
| ajuste | choice+topico | 30 | 32 (1.000) | 28 | 268 | 324 | 2377 | 0.0000998 | 0.0998 | jev-1.13.0 |
| teste | choice | 60 | 72 (0.972) | 53 | 260 | 318 | 1884 | 0.0000791 | 0.0791 | jev-1.13.0 |

## Conjunto `ajuste` — 30 fichas, 104 afirmações (arquivo versão 2026-10-01, autor fable)

### Relação e ação — Jev + código × baseline, por desenho

`acerto_relacao` = relação prevista (código ou Jev, resposta dura) × gabarito, todas as afirmações. `cobertura`/`erro_decididos`/`revisar` = ação com CONF_MANTER=0.7, CONF_RETIRAR=0.5; erro entre decididos = manteve o que não é supported ou retirou o que é. `erro_caro` = gabarito contradicted/not_stated → `manter` (promessa inventada passou); `_duro` = o mesmo sem faixa (relação prevista supported). `baseline` = número + palavra de promessa + booleano da ficha + palavras na ficha, sem faixa.

| desenho | n | acerto_relacao | cobertura | erro_decididos | revisar | erro_caro | erro_caro_duro | baseline_acerto | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| choice | 104 | 0.962 | 0.933 | 0.010 | 7 | 0/48 | 0/48 | 0.788 | 10/48 |
| choice+topico | 104 | 0.962 | 0.952 | 0.010 | 5 | 0/48 | 0/48 | 0.788 | 10/48 |

### Matriz gabarito × previsto — `choice`

| gabarito \ previsto | supported | contradicted | not_stated |
|---|---|---|---|
| supported | 55 | 0 | 1 |
| contradicted | 0 | 28 | 1 |
| not_stated | 0 | 2 | 17 |

### Por caminho (código puro / composta / Jev) — `choice`

`codigo` = número comparado em código, sem chamada; `composta` = número bate e o resto foi ao Jev (número contradito decide sozinho); `jev` = só a Choice.

| caminho | n | acerto_relacao | erro_caro | revisar | baseline |
|---|---|---|---|---|---|
| codigo | 32 | 1.000 | 0/10 | 0 | 1.000 |
| composta | 9 | 0.889 | 0/6 | 1 | 0.444 |
| jev | 63 | 0.952 | 0/32 | 6 | 0.730 |

### Numéricas do gabarito (nota `numérica`) — por onde passaram — `choice`

| caminho | n | acerto_relacao | erros |
|---|---|---|---|
| codigo | 32 | 1.000 | — |
| composta | 4 | 0.750 | CP-A028/a3 |
| jev | 0 | nan | — |
| codigo (não marcada numérica) | 0 | nan | — |

### Por família difícil (nota `difícil`) — `choice`

| familias | n | acerto_relacao | erro_caro | revisar | baseline |
|---|---|---|---|---|---|
| (fácil) | 61 | 1.000 | 0/16 | 0 | 0.967 |
| composta | 3 | 1.000 | 0/3 | 1 | 0.333 |
| condição | 5 | 0.800 | 0/4 | 2 | 0.400 |
| distância estimada | 5 | 1.000 | 0/4 | 1 | 0.800 |
| negação | 4 | 1.000 | 0/2 | 0 | 1.000 |
| opinião | 2 | 0.500 | 0/1 | 0 | 1.000 |
| orientação×iluminação | 8 | 0.875 | 0/6 | 1 | 0.375 |
| outra | 1 | 0.000 | 0/1 | 0 | 0.000 |
| paráfrase | 4 | 1.000 | 0/0 | 0 | 0.500 |
| paráfrase negativa | 1 | 1.000 | 0/1 | 0 | 0.000 |
| possibilidade×garantia | 7 | 1.000 | 0/7 | 2 | 0.714 |
| vaga rotativa×privativa | 3 | 1.000 | 0/3 | 0 | 0.000 |

### Cobertura × erro por limiares (só afirmações julgadas pelo Jev) — `choice`

| CONF_MANTER | CONF_RETIRAR | cobertura | erro_decididos | revisar | erro_caro |
|---|---|---|---|---|---|
| 0.000 | 0.000 | 1.000 | 0.014 | 0 | 0/37 |
| 0.500 | 0.500 | 0.915 | 0.015 | 6 | 0/37 |
| 0.700 | 0.500 | 0.901 | 0.016 | 7 | 0/37 |
| 0.800 | 0.500 | 0.901 | 0.016 | 7 | 0/37 |
| 0.700 | 0.700 | 0.831 | 0.000 | 12 | 0/37 |
| 0.900 | 0.500 | 0.873 | 0.016 | 9 | 0/37 |
| 0.900 | 0.700 | 0.803 | 0.000 | 14 | 0/37 |
| 0.900 | 0.900 | 0.761 | 0.000 | 17 | 0/37 |

### Cobertura × erro por limiares (só afirmações julgadas pelo Jev) — `choice+topico`

| CONF_MANTER | CONF_RETIRAR | cobertura | erro_decididos | revisar | erro_caro |
|---|---|---|---|---|---|
| 0.000 | 0.000 | 1.000 | 0.014 | 0 | 0/37 |
| 0.500 | 0.500 | 0.944 | 0.015 | 4 | 0/37 |
| 0.700 | 0.500 | 0.930 | 0.015 | 5 | 0/37 |
| 0.800 | 0.500 | 0.915 | 0.015 | 6 | 0/37 |
| 0.700 | 0.700 | 0.845 | 0.000 | 11 | 0/37 |
| 0.900 | 0.500 | 0.901 | 0.016 | 7 | 0/37 |
| 0.900 | 0.700 | 0.817 | 0.000 | 13 | 0/37 |
| 0.900 | 0.900 | 0.746 | 0.000 | 18 | 0/37 |

### Custo e latência (medidos na chamada real; do cache também)

Latência por REQUISIÇÃO (= por ficha com alguma afirmação no Jev). Mil fichas = mil rascunhos conferidos. As numéricas puras custam zero.

| desenho | requisicoes | perguntas | p50_ms | p95_ms | tokens_por_ficha | US$_por_ficha | US$_por_mil_fichas | US$_por_mil_afirmacoes | afirmacoes_no_jev | falhas_operacionais | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| choice | 28 | 72 | 280 | 383 | 2101 | 0.0000882 | 0.0882 | 0.0255 | 71/104 | 0 | jev-1.13.0 |
| choice+topico | 28 | 144 | 268 | 324 | 2377 | 0.0000998 | 0.0998 | 0.0288 | 71/104 | 0 | jev-1.13.0 |

### Caso a caso — `choice` (`choice+topico` entre parênteses)

`jev` = opção vencedora (confiança); `tópico` = Noul auxiliar quando ligado. `marca`: `caro` = promessa inventada mantida; `erro` = ação decidida errada; `rel` = relação errada mas ação certa ou em revisão.

| id | af | afirmação | caminho | código | jev | relação | gab | ação | bl | marca |
|---|---|---|---|---|---|---|---|---|---|---|
| CP-A001 | a1 | O financiamento já está aprovado | jev | — | not_stated (0.59) (not_stated 0.62, tópico 0.93) | not_stated | not_stated | retirar | not_ | — |
| CP-A001 | a2 | O proprietário aceita analisar proposta com financiamento | jev | — | supported (1.00) (supported 0.99, tópico 0.98) | supported | supported | manter | not_ | — |
| CP-A001 | a3 | O condomínio é de R$ 780 | codigo | condominio = 780 × 780 → supported | — | supported | supported | manter | supp | — |
| CP-A001 | a4 | Tem portaria 24 horas | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A002 | a1 | Tem vaga privativa | composta | vagas >= 1 × 1 → supported | contradicted (1.00) (contradicted 1.00, tópico 0.96) | contradicted | contradicted | retirar | supp | — |
| CP-A002 | a2 | Tem uma vaga de garagem | codigo | vagas = 1 × 1 → supported | — | supported | supported | manter | supp | — |
| CP-A002 | a3 | Fica a 600 metros do metrô | codigo | distancia = 600 × 600 → supported | — | supported | supported | manter | supp | — |
| CP-A002 | a4 | Aceita pet de pequeno porte | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-A003 | a1 | Aceita pet | jev | — | not_stated (0.49) (not_stated 0.54, tópico 0.96) | not_stated | not_stated | revisar | supp | — |
| CP-A003 | a2 | Aceita cachorro de grande porte | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.82) | contradicted | contradicted | retirar | supp | — |
| CP-A003 | a3 | Aceita pet pequeno, sujeito à aprovação do condomínio | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A003 | a4 | Não tem vaga | codigo | vagas = 0 × 0 → supported | — | supported | supported | manter | supp | — |
| CP-A004 | a1 | Fica a 300 metros do metrô | codigo | distancia = 300 × 800 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A004 | a2 | Dá para ir a pé até o metrô | jev | — | supported (0.98) (supported 0.99, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A004 | a3 | Tem 70 m² | codigo | area = 70 × 70 → supported | — | supported | supported | manter | supp | — |
| CP-A004 | a4 | Tem 90 m² | codigo | area = 90 × 70 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A005 | a1 | Bate sol da manhã na sala | jev | — | not_stated (0.67) (not_stated 0.72, tópico 0.80) | not_stated | not_stated | retirar | not_ | — |
| CP-A005 | a2 | A sala é bem iluminada | jev | — | supported (1.00) (supported 0.99, tópico 0.97) | supported | supported | manter | supp | — |
| CP-A005 | a3 | É face norte | jev | — | supported (1.00) (supported 1.00, tópico 0.99) | supported | supported | manter | supp | — |
| CP-A005 | a4 | Tem 3 vagas | codigo | vagas = 3 × 2 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A006 | a1 | Vem mobiliado | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A006 | a2 | Não precisa de reforma | jev | — | supported (0.98) (supported 0.99, tópico 0.83) | supported | supported | manter | not_ | — |
| CP-A006 | a3 | O condomínio inclui água e gás | jev | — | supported (0.99) (supported 0.98, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A006 | a4 | Condomínio de 450 reais já inclui luz | composta | condominio = 450 × 450 → supported | not_stated (0.28) (contradicted 0.25, tópico 0.50) | not_stated | not_stated | revisar | supp | — |
| CP-A007 | a1 | É mobiliado | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-A007 | a2 | Vai sem móveis | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A007 | a3 | Não aceita animais | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A007 | a4 | As vagas são cobertas | composta | vagas >= 1 × 2 → supported | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A007 | a5 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-A008 | a1 | 220 m² de área construída | codigo | area = 220 × 220 → supported | — | supported | supported | manter | supp | — |
| CP-A008 | a2 | Terreno de 500 m² | codigo | terreno = 500 × 400 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A008 | a3 | Mais de 200 m² | codigo | area > 200 × 220 → supported | — | supported | supported | manter | supp | — |
| CP-A008 | a4 | Condomínio de R$ 1.500 | codigo | condominio = 1500 × 1200 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A009 | a1 | Aceita financiamento | jev | — | supported (1.00) (supported 1.00, tópico 0.99) | supported | supported | manter | supp | — |
| CP-A009 | a2 | Dá para usar o FGTS | jev | — | supported (0.99) (supported 0.99, tópico 0.97) | supported | supported | manter | supp | — |
| CP-A009 | a3 | O financiamento já foi aprovado pela Caixa | jev | — | not_stated (1.00) (not_stated 1.00, tópico 0.45) | not_stated | not_stated | retirar | not_ | — |
| CP-A009 | a4 | Tem vista para o mar | jev | — | supported (0.99) (supported 0.99, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A010 | a1 | Aceita financiamento | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-A010 | a2 | Só vende à vista | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A010 | a3 | Está pronto para morar | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.87) | contradicted | contradicted | retirar | not_ | — |
| CP-A011 | a1 | Pega sol da manhã na varanda | jev | — | supported (0.99) (supported 0.98, tópico 0.97) | supported | supported | manter | not_ | — |
| CP-A011 | a2 | Pega sol da tarde | jev | — | contradicted (0.99) (contradicted 0.99, tópico 0.87) | contradicted | contradicted | retirar | not_ | — |
| CP-A011 | a3 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-A012 | a1 | Pega sol da manhã | jev | — | contradicted (0.99) (contradicted 1.00, tópico 0.95) | contradicted | contradicted | retirar | not_ | — |
| CP-A012 | a2 | É um apartamento claro | jev | — | supported (0.80) (supported 0.79, tópico 0.94) | supported | supported | manter | supp | — |
| CP-A012 | a3 | O condomínio fica abaixo de 700 reais | codigo | condominio < 700 × 600 → supported | — | supported | supported | manter | supp | — |
| CP-A013 | a1 | Aceita pet | jev | — | not_stated (1.00) (not_stated 1.00, tópico 0.05) | not_stated | not_stated | retirar | not_ | — |
| CP-A013 | a2 | Tem lazer completo | jev | — | not_stated (1.00) (not_stated 1.00, tópico 0.05) | not_stated | not_stated | retirar | not_ | — |
| CP-A013 | a3 | Tem 95 m² | codigo | area = 95 × 95 → supported | — | supported | supported | manter | supp | — |
| CP-A013 | a4 | Tem suíte | jev | — | supported (1.00) (supported 1.00, tópico 0.97) | supported | supported | manter | supp | — |
| CP-A014 | a1 | A vaga é rotativa | composta | vagas >= 1 × 1 → supported | contradicted (0.99) (contradicted 1.00, tópico 0.84) | contradicted | contradicted | retirar | supp | — |
| CP-A014 | a2 | Tem vaga própria | composta | vagas >= 1 × 1 → supported | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A014 | a3 | É mobiliado | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-A015 | a1 | Fica pertinho do metrô, uns 5 minutos a pé | composta | distancia = 400 × 1200 → contradicted | not_stated (0.23) (not_stated 0.24, tópico 0.97) | contradicted | contradicted | retirar | cont | — |
| CP-A015 | a2 | Fica a menos de 1,5 km do metrô | codigo | distancia < 1500 × 1200 → supported | — | supported | supported | manter | supp | — |
| CP-A015 | a3 | Aceita pet | jev | — | supported (1.00) (supported 1.00, tópico 0.99) | supported | supported | manter | supp | — |
| CP-A016 | a1 | Aceita pet | jev | — | not_stated (0.97) (not_stated 0.98, tópico 0.93) | not_stated | not_stated | retirar | not_ | — |
| CP-A016 | a2 | Não aceita pet | jev | — | not_stated (0.45) (not_stated 0.40, tópico 0.85) | not_stated | not_stated | revisar | not_ | — |
| CP-A016 | a3 | Tem 180 m² | codigo | area = 180 × 180 → supported | — | supported | supported | manter | supp | — |
| CP-A016 | a4 | Tem 4 dormitórios | codigo | quartos = 4 × 4 → supported | — | supported | supported | manter | supp | — |
| CP-A017 | a1 | Tem 3 quartos e 3 vagas | codigo | quartos = 3 × 3 → supported; vagas = 3 × 2 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A017 | a2 | Tem churrasqueira | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A017 | a3 | Aceita financiamento com entrada de 20% | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-A018 | a1 | Vem mobiliado | jev | — | contradicted (0.75) (contradicted 0.77, tópico 0.94) | contradicted | not_stated | retirar | not_ | rel |
| CP-A018 | a2 | Tem armários planejados | jev | — | supported (0.99) (supported 0.99, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A018 | a3 | Fica na quadra da praia | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A018 | a4 | Vem com geladeira e fogão | jev | — | not_stated (0.91) (not_stated 0.88, tópico 0.12) | not_stated | not_stated | retirar | not_ | — |
| CP-A019 | a1 | Aceita seu golden retriever | jev | — | contradicted (0.98) (contradicted 0.97, tópico 0.88) | contradicted | contradicted | retirar | not_ | — |
| CP-A019 | a2 | Aceita pet de até 10 kg | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A019 | a3 | Aceita gato | jev | — | supported (0.55) (supported 0.60, tópico 0.86) | supported | supported | revisar | supp | — |
| CP-A020 | a1 | Custa 890 mil | codigo | preco = 890000 × 890000 → supported | — | supported | supported | manter | supp | — |
| CP-A020 | a2 | Custa menos de 800 mil | codigo | preco < 800000 × 890000 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A020 | a3 | Condomínio de 950 | codigo | condominio = 950 × 950 → supported | — | supported | supported | manter | supp | — |
| CP-A020 | a4 | Fica a menos de 1 km do metrô | codigo | distancia < 1000 × 900 → supported | — | supported | supported | manter | supp | — |
| CP-A021 | a1 | Tem vaga | codigo | vagas >= 1 × 0 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A021 | a2 | Tem elevador | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A021 | a3 | Fica perto do metrô República | jev | — | not_stated (0.97) (not_stated 0.96, tópico 0.19) | not_stated | not_stated | retirar | not_ | — |
| CP-A022 | a1 | Pega sol o dia inteiro | jev | — | not_stated (0.33) (not_stated 0.25, tópico 0.77) | not_stated | not_stated | revisar | not_ | — |
| CP-A022 | a2 | Os quartos pegam sol de manhã | jev | — | supported (1.00) (supported 1.00, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A022 | a3 | A sala tem vista livre | jev | — | not_stated (0.52) (contradicted 0.24, tópico 0.43) | not_stated | contradicted | retirar | not_ | rel |
| CP-A023 | a1 | Não aceita financiamento | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.97) | contradicted | contradicted | retirar | not_ | — |
| CP-A023 | a2 | Pode aceitar financiamento, dependendo da proposta | jev | — | supported (1.00) (supported 1.00, tópico 0.97) | supported | supported | manter | not_ | — |
| CP-A023 | a3 | Aceita financiamento | jev | — | not_stated (0.49) (not_stated 0.61, tópico 0.97) | not_stated | not_stated | revisar | not_ | — |
| CP-A024 | a1 | Tem 2 vagas cobertas | composta | vagas = 2 × 2 → supported | not_stated (0.76) (not_stated 0.82, tópico 0.91) | not_stated | not_stated | retirar | supp | — |
| CP-A024 | a2 | Tem piscina | jev | — | supported (0.99) (supported 0.99, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A024 | a3 | Tem 1 vaga | codigo | vagas = 1 × 2 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A025 | a1 | Uns 5 minutos a pé do metrô | codigo | distancia = 400 × 400 → supported | — | supported | supported | manter | supp | — |
| CP-A025 | a2 | Fica a 400 metros do metrô | codigo | distancia = 400 × 400 → supported | — | supported | supported | manter | supp | — |
| CP-A025 | a3 | Fica colado no metrô | jev | — | not_stated (0.40) (not_stated 0.51, tópico 0.93) | not_stated | not_stated | revisar | supp | — |
| CP-A026 | a1 | É mobiliado | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-A026 | a2 | Tem armários | jev | — | supported (0.98) (supported 0.99, tópico 0.98) | supported | supported | manter | supp | — |
| CP-A026 | a3 | É bem ensolarado | jev | — | contradicted (0.99) (contradicted 0.99, tópico 0.96) | contradicted | contradicted | retirar | not_ | — |
| CP-A027 | a1 | Tem garagem para dois carros | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-A027 | a2 | Todos os quartos são suítes | jev | — | supported (0.87) (supported 0.86, tópico 0.97) | supported | supported | manter | not_ | — |
| CP-A027 | a3 | Tem piscina do condomínio | jev | — | contradicted (0.64) (contradicted 0.63, tópico 0.89) | contradicted | not_stated | retirar | supp | rel |
| CP-A028 | a1 | Fica numa rua tranquila | jev | — | supported (1.00) (supported 1.00, tópico 0.97) | supported | supported | manter | supp | — |
| CP-A028 | a2 | Ótima localização | jev | — | not_stated (0.99) (not_stated 0.99, tópico 0.27) | not_stated | not_stated | retirar | not_ | — |
| CP-A028 | a3 | Condomínio barato, R$ 520 | composta | condominio = 520 × 520 → supported | not_stated (0.54) (not_stated 0.54, tópico 0.96) | not_stated | supported | retirar | supp | erro |
| CP-A029 | a1 | Não aceita pet | jev | — | contradicted (1.00) (contradicted 1.00, tópico 0.98) | contradicted | contradicted | retirar | cont | — |
| CP-A029 | a2 | Condomínio de 1.800 reais | codigo | condominio = 1800 × 1800 → supported | — | supported | supported | manter | supp | — |
| CP-A029 | a3 | Condomínio abaixo de mil | codigo | condominio < 1000 × 1800 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-A030 | a1 | Aceita pet | jev | — | not_stated (0.88) (not_stated 0.87, tópico 0.96) | not_stated | not_stated | retirar | supp | — |
| CP-A030 | a2 | Duas vagas privativas | composta | vagas = 2 × 2 → supported | contradicted (0.99) (contradicted 0.99, tópico 0.97) | contradicted | contradicted | retirar | supp | — |
| CP-A030 | a3 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |

## Conjunto `teste` — 60 fichas, 200 afirmações (arquivo versão 2026-10-01, autor fable)

### Relação e ação — Jev + código × baseline, por desenho

`acerto_relacao` = relação prevista (código ou Jev, resposta dura) × gabarito, todas as afirmações. `cobertura`/`erro_decididos`/`revisar` = ação com CONF_MANTER=0.7, CONF_RETIRAR=0.5; erro entre decididos = manteve o que não é supported ou retirou o que é. `erro_caro` = gabarito contradicted/not_stated → `manter` (promessa inventada passou); `_duro` = o mesmo sem faixa (relação prevista supported). `baseline` = número + palavra de promessa + booleano da ficha + palavras na ficha, sem faixa.

| desenho | n | acerto_relacao | cobertura | erro_decididos | revisar | erro_caro | erro_caro_duro | baseline_acerto | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|
| choice | 200 | 0.930 | 0.950 | 0.032 | 10 | 1/88 | 5/88 | 0.720 | 27/88 |

### Matriz gabarito × previsto — `choice`

| gabarito \ previsto | supported | contradicted | not_stated |
|---|---|---|---|
| supported | 107 | 4 | 1 |
| contradicted | 0 | 49 | 1 |
| not_stated | 5 | 3 | 30 |

### Por caminho (código puro / composta / Jev) — `choice`

`codigo` = número comparado em código, sem chamada; `composta` = número bate e o resto foi ao Jev (número contradito decide sozinho); `jev` = só a Choice.

| caminho | n | acerto_relacao | erro_caro | revisar | baseline |
|---|---|---|---|---|---|
| codigo | 72 | 0.972 | 0/15 | 0 | 0.972 |
| composta | 15 | 0.867 | 0/8 | 0 | 0.333 |
| jev | 113 | 0.912 | 1/65 | 10 | 0.611 |

### Numéricas do gabarito (nota `numérica`) — por onde passaram — `choice`

| caminho | n | acerto_relacao | erros |
|---|---|---|---|
| codigo | 72 | 0.972 | CP-T015/a2, CP-T038/a3 |
| composta | 4 | 1.000 | — |
| jev | 1 | 1.000 | — |
| codigo (não marcada numérica) | 0 | nan | — |

### Por família difícil (nota `difícil`) — `choice`

| familias | n | acerto_relacao | erro_caro | revisar | baseline |
|---|---|---|---|---|---|
| (fácil) | 117 | 0.974 | 0/26 | 0 | 0.880 |
| aproximação numérica | 3 | 1.000 | 0/1 | 0 | 1.000 |
| composta | 5 | 1.000 | 0/4 | 0 | 0.400 |
| condição | 11 | 0.545 | 0/11 | 3 | 0.273 |
| distância estimada | 8 | 0.750 | 1/3 | 0 | 0.500 |
| negação | 11 | 1.000 | 0/8 | 0 | 0.818 |
| numérica com dois números na ficha | 1 | 1.000 | 0/1 | 0 | 1.000 |
| opinião | 2 | 0.500 | 0/2 | 1 | 0.500 |
| orientação×iluminação | 16 | 0.938 | 0/12 | 2 | 0.438 |
| outra | 1 | 0.000 | 0/1 | 1 | 0.000 |
| paráfrase | 7 | 0.857 | 0/2 | 2 | 0.571 |
| paráfrase negativa | 2 | 1.000 | 0/2 | 0 | 0.000 |
| possibilidade×garantia | 10 | 1.000 | 0/9 | 1 | 0.700 |
| vaga rotativa×privativa | 6 | 1.000 | 0/6 | 0 | 0.000 |

### Cobertura × erro por limiares (só afirmações julgadas pelo Jev) — `choice`

| CONF_MANTER | CONF_RETIRAR | cobertura | erro_decididos | revisar | erro_caro |
|---|---|---|---|---|---|
| 0.000 | 0.000 | 1.000 | 0.048 | 0 | 5/73 |
| 0.500 | 0.500 | 0.952 | 0.033 | 6 | 3/73 |
| 0.700 | 0.500 | 0.921 | 0.017 | 10 | 1/73 |
| 0.800 | 0.500 | 0.921 | 0.017 | 10 | 1/73 |
| 0.700 | 0.700 | 0.873 | 0.018 | 16 | 1/73 |
| 0.900 | 0.500 | 0.905 | 0.009 | 12 | 0/73 |
| 0.900 | 0.700 | 0.857 | 0.009 | 18 | 0/73 |
| 0.900 | 0.900 | 0.833 | 0.010 | 21 | 0/73 |

### Custo e latência (medidos na chamada real; do cache também)

Latência por REQUISIÇÃO (= por ficha com alguma afirmação no Jev). Mil fichas = mil rascunhos conferidos. As numéricas puras custam zero.

| desenho | requisicoes | perguntas | p50_ms | p95_ms | tokens_por_ficha | US$_por_ficha | US$_por_mil_fichas | US$_por_mil_afirmacoes | afirmacoes_no_jev | falhas_operacionais | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| choice | 53 | 128 | 260 | 318 | 1884 | 0.0000791 | 0.0791 | 0.0237 | 126/200 | 0 | jev-1.13.0 |

### Caso a caso — `choice`

`jev` = opção vencedora (confiança); `tópico` = Noul auxiliar quando ligado. `marca`: `caro` = promessa inventada mantida; `erro` = ação decidida errada; `rel` = relação errada mas ação certa ou em revisão.

| id | af | afirmação | caminho | código | jev | relação | gab | ação | bl | marca |
|---|---|---|---|---|---|---|---|---|---|---|
| CP-T001 | a1 | Tem 58 m² | codigo | area = 58 × 58 → supported | — | supported | supported | manter | supp | — |
| CP-T001 | a2 | Aceita pet | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T001 | a3 | Tem 2 vagas | codigo | vagas = 2 × 1 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T001 | a4 | É mobiliado | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T002 | a1 | Aceita financiamento | jev | — | not_stated (0.24) | not_stated | not_stated | revisar | not_ | — |
| CP-T002 | a2 | O proprietário avalia propostas financiadas | jev | — | supported (1.00) | supported | supported | manter | not_ | — |
| CP-T002 | a3 | Financiamento aprovado | jev | — | not_stated (0.95) | not_stated | not_stated | retirar | not_ | — |
| CP-T003 | a1 | A vaga é rotativa | composta | vagas >= 1 × 1 → supported | supported (1.00) | supported | supported | manter | supp | — |
| CP-T003 | a2 | Tem vaga privativa demarcada | composta | vagas >= 1 × 1 → supported | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T003 | a3 | Fica a 350 m do metrô | codigo | distancia = 350 × 350 → supported | — | supported | supported | manter | supp | — |
| CP-T003 | a4 | Fica a mais de 500 m do metrô | codigo | distancia > 500 × 350 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T004 | a1 | Aceita pet | jev | — | supported (0.47) | supported | not_stated | revisar | supp | rel |
| CP-T004 | a2 | Aceita pet de até 15 kg | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T004 | a3 | Aceita cachorro de 30 kg | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T005 | a1 | Fica a uns 500 m do metrô | codigo | distancia = 500 × 560 → supported | — | supported | supported | manter | supp | — |
| CP-T005 | a2 | Pega sol da manhã | jev | — | supported (0.99) | supported | supported | manter | not_ | — |
| CP-T005 | a3 | Dá para ir a pé ao metrô | jev | — | supported (0.99) | supported | supported | manter | supp | — |
| CP-T006 | a1 | É face norte | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T006 | a2 | É bem iluminado | jev | — | supported (0.98) | supported | supported | manter | not_ | — |
| CP-T006 | a3 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-T007 | a1 | Já está reformado | jev | — | supported (1.00) | supported | supported | manter | not_ | — |
| CP-T007 | a2 | Tem ar-condicionado nos quartos | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T007 | a3 | Vem totalmente mobiliado | jev | — | not_stated (0.98) | not_stated | not_stated | retirar | not_ | — |
| CP-T007 | a4 | Precisa de reforma | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T008 | a1 | Aceita pet | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | cont | — |
| CP-T008 | a2 | Não tem vaga | codigo | vagas = 0 × 0 → supported | — | supported | supported | manter | supp | — |
| CP-T008 | a3 | Não é mobiliado | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T008 | a4 | Tem 45 m² | codigo | area = 45 × 45 → supported | — | supported | supported | manter | supp | — |
| CP-T009 | a1 | Tem 320 m² | codigo | area = 320 × 320 → supported | — | supported | supported | manter | supp | — |
| CP-T009 | a2 | Condomínio de 2.400 | codigo | condominio = 2400 × 2400 → supported | — | supported | supported | manter | supp | — |
| CP-T009 | a3 | Custa 1,9 milhão | codigo | preco = 1.9e+06 × 2.1e+06 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T009 | a4 | Tem 4 vagas | codigo | vagas = 4 × 4 → supported | — | supported | supported | manter | supp | — |
| CP-T009 | a5 | Tem mais de 300 m² | codigo | area > 300 × 320 → supported | — | supported | supported | manter | supp | — |
| CP-T010 | a1 | Dá para financiar | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | cont | — |
| CP-T010 | a2 | Só à vista | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T010 | a3 | Aceita FGTS | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T011 | a1 | Pega bastante sol | jev | — | contradicted (0.98) | contradicted | contradicted | retirar | not_ | — |
| CP-T011 | a2 | É fresco no verão | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T011 | a3 | Pega sol da manhã | jev | — | contradicted (0.81) | contradicted | contradicted | retirar | not_ | — |
| CP-T012 | a1 | Aceita financiamento | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T012 | a2 | Fica perto do metrô | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T012 | a3 | Tem 85 m² | codigo | area = 85 × 85 → supported | — | supported | supported | manter | supp | — |
| CP-T012 | a4 | Tem 3 quartos | codigo | quartos = 3 × 3 → supported | — | supported | supported | manter | supp | — |
| CP-T013 | a1 | Tem 2 vagas cobertas | composta | vagas = 2 × 2 → supported | contradicted (0.99) | contradicted | contradicted | retirar | supp | — |
| CP-T013 | a2 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-T013 | a3 | Tem quintal | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T014 | a1 | Aceita pet | jev | — | supported (0.59) | supported | not_stated | revisar | not_ | rel |
| CP-T014 | a2 | Aceita gato | jev | — | supported (0.97) | supported | supported | manter | not_ | — |
| CP-T014 | a3 | Aceita cão de grande porte | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | not_ | — |
| CP-T015 | a1 | Fica a 250 m do metrô | codigo | distancia = 250 × 250 → supported | — | supported | supported | manter | supp | — |
| CP-T015 | a2 | Menos de 3 minutos a pé do metrô | codigo | distancia < 240 × 250 → contradicted | — | contradicted | supported | retirar | cont | erro |
| CP-T015 | a3 | Fica a 1 km do metrô | codigo | distancia = 1000 × 250 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T015 | a4 | Condomínio de 900 | codigo | condominio = 900 × 900 → supported | — | supported | supported | manter | supp | — |
| CP-T016 | a1 | Tem cerca de 120 m² | codigo | area = 120 × 118 → supported | — | supported | supported | manter | supp | — |
| CP-T016 | a2 | Tem 100 m² | codigo | area = 100 × 118 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T016 | a3 | É frente para o mar | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T016 | a4 | Tem 2 vagas | codigo | vagas = 2 × 1 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T017 | a1 | Aceita financiamento | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T017 | a2 | Já tem financiamento aprovado para você | jev | — | not_stated (0.99) | not_stated | not_stated | retirar | not_ | — |
| CP-T017 | a3 | Aceita financiamento pela Caixa | jev | — | not_stated (0.95) | not_stated | supported | retirar | supp | erro |
| CP-T018 | a1 | Não é mobiliado | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | cont | — |
| CP-T018 | a2 | A vaga é rotativa | composta | vagas >= 1 × 1 → supported | supported (1.00) | supported | supported | manter | supp | — |
| CP-T018 | a3 | Não aceita pet | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | cont | — |
| CP-T018 | a4 | A vaga é fixa | composta | vagas >= 1 × 1 → supported | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T019 | a1 | Tem 130 m² e 2 vagas | codigo | area = 130 × 130 → supported; vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-T019 | a2 | Tem 130 m² e 3 vagas | codigo | area = 130 × 130 → supported; vagas = 3 × 2 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T019 | a3 | Pega sol da manhã | jev | — | not_stated (0.50) | not_stated | not_stated | retirar | not_ | — |
| CP-T019 | a4 | É face norte | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T020 | a1 | É um lugar seguro | jev | — | supported (0.39) | supported | not_stated | revisar | supp | rel |
| CP-T020 | a2 | Tem segurança 24 horas | jev | — | supported (0.99) | supported | supported | manter | supp | — |
| CP-T020 | a3 | Fica numa rua sem saída | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T021 | a1 | Aceita pet | jev | — | supported (0.95) | supported | supported | manter | not_ | — |
| CP-T021 | a2 | Não aceita pet | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | not_ | — |
| CP-T021 | a3 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-T022 | a1 | Fica perto da estação Vila Olímpia | jev | — | not_stated (0.99) | not_stated | not_stated | retirar | supp | — |
| CP-T022 | a2 | O condomínio inclui gás | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T022 | a3 | Condomínio de 700 com água inclusa | composta | condominio = 700 × 700 → supported | not_stated (0.90) | not_stated | not_stated | retirar | supp | — |
| CP-T022 | a4 | Tem 38 m² | codigo | area = 38 × 38 → supported | — | supported | supported | manter | supp | — |
| CP-T023 | a1 | Tem 300 m² de área construída | codigo | area = 300 × 180 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T023 | a2 | Terreno de 300 m² | codigo | terreno = 300 × 300 → supported | — | supported | supported | manter | supp | — |
| CP-T023 | a3 | Tem 180 m² | codigo | area = 180 × 180 → supported | — | supported | supported | manter | supp | — |
| CP-T024 | a1 | É ensolarado pela manhã | jev | — | supported (0.98) | supported | supported | manter | not_ | — |
| CP-T024 | a2 | Tem elevador | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T024 | a3 | Pega sol da tarde | jev | — | not_stated (0.66) | not_stated | contradicted | retirar | not_ | rel |
| CP-T025 | a1 | Aceita financiamento | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T025 | a2 | Aceita permuta | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | supp | — |
| CP-T025 | a3 | Entrada mínima de 20% | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T026 | a1 | Custa menos de 750 mil | codigo | preco < 750000 × 720000 → supported | — | supported | supported | manter | supp | — |
| CP-T026 | a2 | Condomínio de 1.100 | codigo | condominio = 1100 × 1100 → supported | — | supported | supported | manter | supp | — |
| CP-T026 | a3 | Tem 96 m² | codigo | area = 96 × 96 → supported | — | supported | supported | manter | supp | — |
| CP-T026 | a4 | Condomínio de 900 | codigo | condominio = 900 × 1100 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T027 | a1 | Tem vaga | codigo | vagas >= 1 × 1 → supported | — | supported | supported | manter | supp | — |
| CP-T027 | a2 | Vaga demarcada só sua | composta | vagas >= 1 × 1 → supported | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T027 | a3 | Tem 1 vaga | codigo | vagas = 1 × 1 → supported | — | supported | supported | manter | supp | — |
| CP-T028 | a1 | Pega sol da manhã | jev | — | supported (0.99) | supported | supported | manter | supp | — |
| CP-T028 | a2 | É face oeste | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T028 | a3 | Pega sol da tarde | jev | — | contradicted (0.88) | contradicted | contradicted | retirar | not_ | — |
| CP-T029 | a1 | É mobiliado | jev | — | supported (0.97) | supported | supported | manter | supp | — |
| CP-T029 | a2 | Os móveis ficam garantidos no negócio | jev | — | contradicted (0.82) | contradicted | not_stated | retirar | not_ | rel |
| CP-T029 | a3 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-T030 | a1 | Aceita pet | jev | — | supported (0.66) | supported | not_stated | revisar | not_ | rel |
| CP-T030 | a2 | Aceita cachorro | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | not_ | — |
| CP-T030 | a3 | Aceita gato | jev | — | supported (0.89) | supported | supported | manter | not_ | — |
| CP-T030 | a4 | Tem 50 m² | codigo | area = 50 × 50 → supported | — | supported | supported | manter | supp | — |
| CP-T031 | a1 | Tem vista para o mar | jev | — | supported (0.63) | supported | supported | revisar | supp | — |
| CP-T031 | a2 | Aceita pet | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T031 | a3 | Tem 1 vaga | codigo | vagas = 1 × 1 → supported | — | supported | supported | manter | supp | — |
| CP-T032 | a1 | A vaga é coberta | composta | vagas >= 1 × 1 → supported | supported (1.00) | supported | supported | manter | supp | — |
| CP-T032 | a2 | Aceita pet pequeno | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | cont | — |
| CP-T032 | a3 | Tem 2 vagas | codigo | vagas = 2 × 1 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T033 | a1 | Fica a 700 m do metrô | codigo | distancia = 700 × 700 → supported | — | supported | supported | manter | supp | — |
| CP-T033 | a2 | Menos de 10 minutos a pé do metrô | codigo | distancia < 800 × 700 → supported | — | supported | supported | manter | supp | — |
| CP-T033 | a3 | Fica do lado do metrô | jev | — | not_stated (0.54) | not_stated | not_stated | retirar | supp | — |
| CP-T033 | a4 | Aceita financiamento | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T034 | a1 | Está totalmente reformado | jev | — | contradicted (0.91) | contradicted | not_stated | retirar | supp | rel |
| CP-T034 | a2 | A cozinha é reformada | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T034 | a3 | Precisa de reforma | jev | — | contradicted (0.38) | contradicted | not_stated | revisar | supp | rel |
| CP-T035 | a1 | Aceita pet pequeno | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | cont | — |
| CP-T035 | a2 | Não aceita pet | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T035 | a3 | Tem 210 m² | codigo | area = 210 × 210 → supported | — | supported | supported | manter | supp | — |
| CP-T035 | a4 | Tem 3 vagas | codigo | vagas = 3 × 3 → supported | — | supported | supported | manter | supp | — |
| CP-T036 | a1 | Pode ser que aceite financiamento | jev | — | supported (1.00) | supported | supported | manter | not_ | — |
| CP-T036 | a2 | Aceita financiamento | jev | — | not_stated (0.90) | not_stated | not_stated | retirar | not_ | — |
| CP-T036 | a3 | Não financia | jev | — | contradicted (0.98) | contradicted | contradicted | retirar | not_ | — |
| CP-T037 | a1 | Pega sol da manhã | jev | — | supported (0.99) | supported | supported | manter | not_ | — |
| CP-T037 | a2 | Pega sol da tarde | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | not_ | — |
| CP-T037 | a3 | Tem 1 vaga | codigo | vagas = 1 × 1 → supported | — | supported | supported | manter | supp | — |
| CP-T038 | a1 | Tem 78 m² de área útil | codigo | area = 78 × 62 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T038 | a2 | Tem 62 m² | codigo | area = 62 × 62 → supported | — | supported | supported | manter | supp | — |
| CP-T038 | a3 | Área total de 78 m² | codigo | area = 78 × 62 → contradicted | — | contradicted | supported | retirar | cont | erro |
| CP-T039 | a1 | Aceita pet | jev | — | not_stated (0.50) | not_stated | not_stated | retirar | supp | — |
| CP-T039 | a2 | Aceita pet com autorização do síndico | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T039 | a3 | Não aceita pet | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T040 | a1 | Pega sol da manhã | jev | — | not_stated (0.98) | not_stated | not_stated | retirar | not_ | — |
| CP-T040 | a2 | É claro e arejado | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T040 | a3 | É face norte | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T041 | a1 | Tem vaga | codigo | vagas >= 1 × 0 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T041 | a2 | Dá para alugar vaga perto | composta | vagas >= 1 × 0 → contradicted | supported (0.59) | contradicted | supported | retirar | cont | erro |
| CP-T041 | a3 | Não tem vaga própria | composta | vagas = 0 × 0 → supported | supported (1.00) | supported | supported | manter | supp | — |
| CP-T042 | a1 | Condomínio de 650 com água | composta | condominio = 650 × 650 → supported | contradicted (0.99) | contradicted | contradicted | retirar | supp | — |
| CP-T042 | a2 | Condomínio de 650 | codigo | condominio = 650 × 650 → supported | — | supported | supported | manter | supp | — |
| CP-T042 | a3 | Condomínio abaixo de 700 | codigo | condominio < 700 × 650 → supported | — | supported | supported | manter | supp | — |
| CP-T043 | a1 | Aceita pet sem taxa | jev | — | not_stated (0.99) | not_stated | not_stated | retirar | cont | — |
| CP-T043 | a2 | Aceita pet | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T043 | a3 | 580 de condomínio | codigo | condominio = 580 × 580 → supported | — | supported | supported | manter | supp | — |
| CP-T044 | a1 | Fica perto do metrô | jev | — | supported (0.85) | supported | not_stated | manter | supp | caro |
| CP-T044 | a2 | Fica a mais de 1 km do metrô | codigo | distancia > 1000 × 1800 → supported | — | supported | supported | manter | supp | — |
| CP-T044 | a3 | Uns 20 minutos a pé do metrô | codigo | distancia = 1600 × 1800 → supported | — | supported | supported | manter | supp | — |
| CP-T045 | a1 | Está pronto para morar | jev | — | contradicted (0.98) | contradicted | contradicted | retirar | not_ | — |
| CP-T045 | a2 | Entrega em 2027 | jev | — | supported (0.97) | supported | supported | manter | supp | — |
| CP-T045 | a3 | Já está construído | jev | — | contradicted (0.98) | contradicted | contradicted | retirar | not_ | — |
| CP-T046 | a1 | Tem 3 quartos | codigo | quartos = 3 × 3 → supported | — | supported | supported | manter | supp | — |
| CP-T046 | a2 | Tem 2 suítes | jev | — | contradicted (0.97) | contradicted | contradicted | retirar | supp | — |
| CP-T046 | a3 | Tem 90 m² | codigo | area = 90 × 90 → supported | — | supported | supported | manter | supp | — |
| CP-T047 | a1 | A vaga é garantida | composta | vagas >= 1 × 1 → supported | contradicted (1.00) | contradicted | contradicted | retirar | supp | — |
| CP-T047 | a2 | Tem vaga rotativa | composta | vagas >= 1 × 1 → supported | supported (1.00) | supported | supported | manter | supp | — |
| CP-T047 | a3 | Não tem vaga | codigo | vagas = 0 × 1 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T048 | a1 | Pega sol a maior parte do dia | jev | — | supported (0.95) | supported | supported | manter | not_ | — |
| CP-T048 | a2 | Pega sol da manhã | jev | — | not_stated (0.45) | not_stated | not_stated | revisar | not_ | — |
| CP-T048 | a3 | É face norte | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T049 | a1 | Água inclusa no condomínio | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T049 | a2 | É mobiliado | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | cont | — |
| CP-T049 | a3 | Condomínio de 820 | codigo | condominio = 820 × 820 → supported | — | supported | supported | manter | supp | — |
| CP-T049 | a4 | O condomínio inclui luz | jev | — | not_stated (0.90) | not_stated | not_stated | retirar | supp | — |
| CP-T050 | a1 | Aceita pet | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T050 | a2 | Tem churrasqueira | jev | — | supported (0.98) | supported | supported | manter | supp | — |
| CP-T050 | a3 | Tem academia | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T050 | a4 | Tem 1 vaga | codigo | vagas = 1 × 1 → supported | — | supported | supported | manter | supp | — |
| CP-T051 | a1 | Tem mais de 100 m² | codigo | area > 100 × 98 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T051 | a2 | Tem quase 100 m² | codigo | area = 100 × 98 → supported | — | supported | supported | manter | supp | — |
| CP-T051 | a3 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-T052 | a1 | Pode aceitar financiamento | jev | — | contradicted (1.00) | contradicted | contradicted | retirar | cont | — |
| CP-T052 | a2 | Não financia | jev | — | supported (0.97) | supported | supported | manter | supp | — |
| CP-T052 | a3 | Tem 1 vaga | codigo | vagas = 1 × 1 → supported | — | supported | supported | manter | supp | — |
| CP-T053 | a1 | É mobiliado | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T053 | a2 | Vem com geladeira | jev | — | supported (0.51) | supported | supported | revisar | not_ | — |
| CP-T053 | a3 | Tem vaga | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T054 | a1 | Pega sol da manhã na sala | jev | — | contradicted (0.99) | contradicted | contradicted | retirar | supp | — |
| CP-T054 | a2 | Pega sol da manhã no quarto | jev | — | supported (0.95) | supported | supported | manter | supp | — |
| CP-T054 | a3 | É ensolarado | jev | — | not_stated (0.39) | not_stated | not_stated | revisar | not_ | — |
| CP-T055 | a1 | Fica a 1,1 km do metrô | codigo | distancia = 1100 × 1100 → supported | — | supported | supported | manter | supp | — |
| CP-T055 | a2 | Menos de 1 km do metrô | codigo | distancia < 1000 × 1100 → contradicted | — | contradicted | contradicted | retirar | cont | — |
| CP-T055 | a3 | Uns 15 minutos a pé do metrô | codigo | distancia = 1200 × 1100 → supported | — | supported | supported | manter | supp | — |
| CP-T056 | a1 | Aceita financiamento | jev | — | not_stated (0.55) | not_stated | not_stated | retirar | not_ | — |
| CP-T056 | a2 | Não aceita financiamento | jev | — | contradicted (0.99) | contradicted | contradicted | retirar | not_ | — |
| CP-T056 | a3 | Tem 3 vagas | codigo | vagas = 3 × 3 → supported | — | supported | supported | manter | supp | — |
| CP-T057 | a1 | Tem 2 vagas privativas | composta | vagas = 2 × 2 → supported | contradicted (0.96) | contradicted | contradicted | retirar | supp | — |
| CP-T057 | a2 | Tem 2 vagas | codigo | vagas = 2 × 2 → supported | — | supported | supported | manter | supp | — |
| CP-T057 | a3 | Tem 1 vaga escriturada | composta | vagas = 1 × 2 → contradicted | supported (1.00) | contradicted | supported | retirar | cont | erro |
| CP-T058 | a1 | Fica numa rua arborizada | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T058 | a2 | Bairro tranquilo | jev | — | not_stated (0.99) | not_stated | not_stated | retirar | not_ | — |
| CP-T058 | a3 | Menos de 1 km do metrô | codigo | distancia < 1000 × 900 → supported | — | supported | supported | manter | supp | — |
| CP-T059 | a1 | Aceita pet | jev | — | not_stated (0.60) | not_stated | not_stated | retirar | supp | — |
| CP-T059 | a2 | Pets aceitos com aprovação do síndico | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T059 | a3 | Tem 1 vaga | codigo | vagas = 1 × 1 → supported | — | supported | supported | manter | supp | — |
| CP-T060 | a1 | Tem 105 m² | codigo | area = 105 × 105 → supported | — | supported | supported | manter | supp | — |
| CP-T060 | a2 | Aceita pet | jev | — | supported (1.00) | supported | supported | manter | supp | — |
| CP-T060 | a3 | É mobiliado | jev | — | not_stated (1.00) | not_stated | not_stated | retirar | not_ | — |
| CP-T060 | a4 | Condomínio de 700 | codigo | condominio = 700 × 700 → supported | — | supported | supported | manter | supp | — |
| CP-T060 | a5 | Aceita financiamento | jev | — | supported (1.00) | supported | supported | manter | supp | — |
