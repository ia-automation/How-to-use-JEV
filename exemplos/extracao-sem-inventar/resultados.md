# Resultados — extração sem inventar

Gerado por `run.py` em 2026-09-30. Modelo pedido: `jev-1.13.0` (o respondido aparece na tabela de custo). Preço: US$ 0,042 por milhão de tokens de entrada.

## Congelamento

Registrado em 2026-09-30 19:40:48, depois de afinar no ajuste e ANTES de abrir `teste.json`. **Arquivos atuais iguais ao registro: o teste vale.**

| arquivo | sha256 registrado | sha256 atual | igual |
|---|---|---|---|
| perguntas.py | 4f8529765f0d2164 | 4f8529765f0d2164 | True |
| extrator.py | 3a7f76b7b63cdabc | 3a7f76b7b63cdabc | True |
| candidatos.py | 3e1234fc4a84cf0a | 3e1234fc4a84cf0a | True |

## Resumo — ajuste × teste

| campo | ajuste: exatidão | ajuste: cobertura_cand | ajuste: acerto_escolha | ajuste: auto | ajuste: erro_auto | ajuste: inventou | teste: exatidão | teste: cobertura_cand | teste: acerto_escolha | teste: auto | teste: erro_auto | teste: inventou |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| email | 1.000 | 4/4 | 1.000 | 19/20 | 0.000 | 0 | 0.975 | 8/8 | 0.875 | 39/40 | 0.026 | 0 |
| telefone | 1.000 | 5/5 | 1.000 | 20/20 | 0.000 | 0 | 1.000 | 5/5 | 1.000 | 40/40 | 0.000 | 0 |
| cpf | 1.000 | 2/2 | 1.000 | 20/20 | 0.000 | 0 | 1.000 | 4/4 | 1.000 | 40/40 | 0.000 | 0 |
| valor | 1.000 | 4/4 | 1.000 | 20/20 | 0.000 | 0 | 0.975 | 8/9 | 1.000 | 39/40 | 0.026 | 0 |
| data_visita | 1.000 | 8/8 | 1.000 | 19/20 | 0.000 | 0 | 0.925 | 13/13 | 0.923 | 37/40 | 0.027 | 0 |

| conjunto | n_msgs | requisicoes | perguntas_por_req | p50_ms | p95_ms | tokens_entrada | US$_total | US$_por_1000_msgs | modelo |
|---|---|---|---|---|---|---|---|---|---|
| ajuste | 20 | 19 | 4.300 | 326 | 452 | 19649 | 0.000825 | 0.0412 | jev-1.13.0 |
| teste | 40 | 39 | 3.700 | 280 | 545 | 36601 | 0.001537 | 0.0384 | jev-1.13.0 |

## Conjunto `ajuste` — 20 mensagens (arquivo versão 2026-09-30, autor codex)

### Exatidão por campo

`cobertura_cand` = gabarito entre os candidatos da regex (data: havia pista de data); `acerto_escolha` = acerto só entre os cobertos (mede o Jev + normalização); `exatidao` = todos os casos, null certo conta; `auto` = decididos sem revisão; `inventou` = valor que não se reconstrói do texto (tem de ser 0).

| campo | n | n_com_valor | cobertura_cand | acerto_escolha | exatidao | preencheu_null | omitiu | auto | erro_auto | inventou |
|---|---|---|---|---|---|---|---|---|---|---|
| email | 20 | 4 | 4/4 | 1.000 | 1.000 | 0 | 0 | 19/20 | 0.000 | 0 |
| telefone | 20 | 5 | 5/5 | 1.000 | 1.000 | 0 | 0 | 20/20 | 0.000 | 0 |
| cpf | 20 | 2 | 2/2 | 1.000 | 1.000 | 0 | 0 | 20/20 | 0.000 | 0 |
| valor | 20 | 4 | 4/4 | 1.000 | 1.000 | 0 | 0 | 20/20 | 0.000 | 0 |
| data_visita | 20 | 8 | 8/8 | 1.000 | 1.000 | 0 | 0 | 19/20 | 0.000 | 0 |

**Inventou (total): 0** 

### Cobertura automática × erro por limiar de confiança

Só casos em que houve pergunta (há confiança). Limiar atual por campo em `perguntas.CONF_MIN`.

**email** (CONF_MIN=0.6, n=4)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 4 |
| 0.500 | 1.000 | 0.000 | 4 |
| 0.600 | 1.000 | 0.000 | 4 |
| 0.700 | 1.000 | 0.000 | 4 |
| 0.800 | 1.000 | 0.000 | 4 |
| 0.900 | 1.000 | 0.000 | 4 |

**telefone** (CONF_MIN=0.6, n=5)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 5 |
| 0.500 | 1.000 | 0.000 | 5 |
| 0.600 | 1.000 | 0.000 | 5 |
| 0.700 | 1.000 | 0.000 | 5 |
| 0.800 | 1.000 | 0.000 | 5 |
| 0.900 | 1.000 | 0.000 | 5 |

**cpf** (CONF_MIN=0.6, n=2)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 2 |
| 0.500 | 1.000 | 0.000 | 2 |
| 0.600 | 1.000 | 0.000 | 2 |
| 0.700 | 1.000 | 0.000 | 2 |
| 0.800 | 1.000 | 0.000 | 2 |
| 0.900 | 1.000 | 0.000 | 2 |

**valor** (CONF_MIN=0.6, n=6)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 6 |
| 0.500 | 1.000 | 0.000 | 6 |
| 0.600 | 1.000 | 0.000 | 6 |
| 0.700 | 1.000 | 0.000 | 6 |
| 0.800 | 1.000 | 0.000 | 6 |
| 0.900 | 1.000 | 0.000 | 6 |

**data_visita** (CONF_MIN=0.6, n=10)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 10 |
| 0.500 | 1.000 | 0.000 | 10 |
| 0.600 | 1.000 | 0.000 | 10 |
| 0.700 | 0.900 | 0.000 | 9 |
| 0.800 | 0.800 | 0.000 | 8 |
| 0.900 | 0.800 | 0.000 | 8 |

### Custo e latência (medidos na chamada real; do cache também)

| mensagens | requisicoes | sem_chamada | perguntas_por_req | p50_ms | p95_ms | tokens_por_req | US$_total | US$_por_1000_msgs | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 19 | 1 | 4.300 | 326 | 452 | 1034 | 0.000825 | 0.0412 | jev-1.13.0 |

### Caso a caso (só campos errados ou em revisão)

| id | campo | gabarito | previsto | ok | revisar | motivo | conf | escolha/partes | candidatos | nota |
|---|---|---|---|---|---|---|---|---|---|---|
| EX-A003 | email | lu@exemplo.test | lu@exemplo.test | True | True | e-mail reconstruído de correção | 1.000 | lu@exemplo.test | 2 | Difícil: reconstrucao do domínio explicitamente corrigido. |
| EX-A014 | data_visita | None | None | True | True | data impossível: 31 November 2026 | 0.940 | {'modo': 'absolute', 'dia': '31', 'mes': 'November', 'ano': '2026'} |  | Difícil: data impossível não deve ser corrigida silenciosamente. |

## Conjunto `teste` — 40 mensagens (arquivo versão 2026-09-30, autor codex)

### Exatidão por campo

`cobertura_cand` = gabarito entre os candidatos da regex (data: havia pista de data); `acerto_escolha` = acerto só entre os cobertos (mede o Jev + normalização); `exatidao` = todos os casos, null certo conta; `auto` = decididos sem revisão; `inventou` = valor que não se reconstrói do texto (tem de ser 0).

| campo | n | n_com_valor | cobertura_cand | acerto_escolha | exatidao | preencheu_null | omitiu | auto | erro_auto | inventou |
|---|---|---|---|---|---|---|---|---|---|---|
| email | 40 | 8 | 8/8 | 0.875 | 0.975 | 0 | 1 | 39/40 | 0.026 | 0 |
| telefone | 40 | 5 | 5/5 | 1.000 | 1.000 | 0 | 0 | 40/40 | 0.000 | 0 |
| cpf | 40 | 4 | 4/4 | 1.000 | 1.000 | 0 | 0 | 40/40 | 0.000 | 0 |
| valor | 40 | 9 | 8/9 | 1.000 | 0.975 | 0 | 0 | 39/40 | 0.026 | 0 |
| data_visita | 40 | 13 | 13/13 | 0.923 | 0.925 | 2 | 1 | 37/40 | 0.027 | 0 |

**Inventou (total): 0** 

### Cobertura automática × erro por limiar de confiança

Só casos em que houve pergunta (há confiança). Limiar atual por campo em `perguntas.CONF_MIN`.

**email** (CONF_MIN=0.6, n=9)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.111 | 9 |
| 0.500 | 1.000 | 0.111 | 9 |
| 0.600 | 1.000 | 0.111 | 9 |
| 0.700 | 0.889 | 0.125 | 8 |
| 0.800 | 0.889 | 0.125 | 8 |
| 0.900 | 0.778 | 0.000 | 7 |

**telefone** (CONF_MIN=0.6, n=7)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 7 |
| 0.500 | 1.000 | 0.000 | 7 |
| 0.600 | 1.000 | 0.000 | 7 |
| 0.700 | 1.000 | 0.000 | 7 |
| 0.800 | 1.000 | 0.000 | 7 |
| 0.900 | 1.000 | 0.000 | 7 |

**cpf** (CONF_MIN=0.6, n=4)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.000 | 4 |
| 0.500 | 1.000 | 0.000 | 4 |
| 0.600 | 1.000 | 0.000 | 4 |
| 0.700 | 1.000 | 0.000 | 4 |
| 0.800 | 1.000 | 0.000 | 4 |
| 0.900 | 1.000 | 0.000 | 4 |

**valor** (CONF_MIN=0.6, n=12)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.083 | 12 |
| 0.500 | 0.917 | 0.091 | 11 |
| 0.600 | 0.917 | 0.091 | 11 |
| 0.700 | 0.917 | 0.091 | 11 |
| 0.800 | 0.917 | 0.091 | 11 |
| 0.900 | 0.917 | 0.091 | 11 |

**data_visita** (CONF_MIN=0.6, n=18)

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.167 | 18 |
| 0.500 | 0.944 | 0.118 | 17 |
| 0.600 | 0.944 | 0.118 | 17 |
| 0.700 | 0.889 | 0.062 | 16 |
| 0.800 | 0.889 | 0.062 | 16 |
| 0.900 | 0.833 | 0.067 | 15 |

### Custo e latência (medidos na chamada real; do cache também)

| mensagens | requisicoes | sem_chamada | perguntas_por_req | p50_ms | p95_ms | tokens_por_req | US$_total | US$_por_1000_msgs | modelo |
|---|---|---|---|---|---|---|---|---|---|
| 40 | 39 | 1 | 3.700 | 280 | 545 | 938 | 0.001537 | 0.0384 | jev-1.13.0 |

### Caso a caso (só campos errados ou em revisão)

| id | campo | gabarito | previsto | ok | revisar | motivo | conf | escolha/partes | candidatos | nota |
|---|---|---|---|---|---|---|---|---|---|---|
| EX-T002 | email | lia@exemplo.test | None | False | False | jev: nenhum | 0.830 | None | 1 | Difícil: data relativa de dois dias. |
| EX-T005 | email | caio@exemplo.test | caio@exemplo.test | True | True | e-mail reconstruído de correção | 0.990 | caio@exemplo.test | 2 | Difícil: reconstrucao de e-mail por correção parcial. |
| EX-T008 | valor | None | None | True | True | jev: nenhum (conf. baixa) | 0.400 | None | 1 | Difícil: identificador com aparência de preço não é oferta. |
| EX-T011 | data_visita | None | None | True | True | data impossível: 29 February 2027 | 0.990 | {'modo': 'absolute', 'dia': '29', 'mes': 'February', 'ano': '2027'} |  | Difícil: fevereiro inválido em ano não bissexto explícito. |
| EX-T012 | data_visita | 2028-02-29 | None | False | True | data impossível: 29 February none | 0.920 | {'modo': 'absolute', 'dia': '29', 'mes': 'February'} |  | Difícil: próxima ocorrência válida de data sem ano. |
| EX-T030 | data_visita | None | 2026-10-01 | False | False |  | 0.660 | {'modo': 'relative', 'relativo': 'tomorrow'} |  | Difícil: data negada não deve virar agendamento. |
| EX-T034 | valor | 1234.56 | 1234.00 | False | False |  | 0.970 | mil duzentos e trinta e quatro reais | 1 | Difícil: centavos por extenso. |
| EX-T038 | data_visita | None | 2026-10-03 | False | True | conf. baixa | 0.360 | {'modo': 'relative', 'dia_semana': 'Saturday', 'semana': 'plain'} |  | Difícil: hipótese expressamente não escolhida não é data de visita. |
