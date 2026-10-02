# Variantes do state — triagem-de-alerta (só no ajuste, 40 alertas)

Gerado por `run.py variantes` em 2026-10-01 (modo `auto`). Pergunta: os fatos calculados pelo código (`computed_by_code`: dia do alerta e hora × faixa do contexto) ajudam o Jev, e movem Nouls que não deviam mudar (lição 30)? O veto de horário é código e vale com ou sem os fatos no state.

| variante | acerto_acao | E1 | E2 | E3 | auto_close indevido | expected_activity ≥0,5 | critical_asset ≥0,5 | compromise_indication ≥0,5 | ongoing ≥0,5 | Choice única |
|---|---|---|---|---|---|---|---|---|---|---|
| fatos no state + veto (principal) | 1.000 | 0 | 0 | 0 | 0 | 0.975 | 1.000 | 0.974 | 0.925 | 0.900 |
| fatos no state, sem veto | 1.000 | 0 | 0 | 0 | 0 | 0.975 | 1.000 | 0.974 | 0.925 | 0.900 |
| sem fatos no state, com veto | 0.950 | 0 | 0 | 0 | 0 | 0.975 | 1.000 | 0.947 | 0.975 | 0.850 |
| sem fatos no state, sem veto | 0.950 | 0 | 0 | 0 | 0 | 0.975 | 1.000 | 0.947 | 0.975 | 0.850 |

## Quanto cada Noul se moveu (com fatos − sem fatos)

| noul | média |Δ| | máx |Δ| | trocaram de lado em 0,5 |
|---|---|---|---|
| expected_activity | 0.029 | 0.090 | 0 |
| critical_asset | 0.007 | 0.030 | 0 |
| compromise_indication | 0.020 | 0.360 | 1 |
| ongoing | 0.017 | 0.100 | 2 |

## Alertas com faixa de horário no contexto (onde o fato existe)

| id | gabarito | esperada | expected com | expected sem | indício com | indício sem | ação com | ação sem | veto |
|---|---|---|---|---|---|---|---|---|---|
| TA-A001 | auto_close | True | 0.70 | 0.74 | 0.03 | 0.03 | auto_close | auto_close | não |
| TA-A007 | notify_owner | False | 0.19 | 0.12 | 0.07 | 0.05 | notify_owner | notify_owner | sim |
| TA-A014 | auto_close | True | 0.88 | 0.87 | 0.03 | 0.03 | auto_close | auto_close | não |
| TA-A022 | queue_tier2 | False | 0.31 | 0.26 | 0.73 | 0.37 | queue_tier2 | queue_tier2 | sim |
| TA-A024 | auto_close | True | 0.93 | 0.90 | 0.03 | 0.03 | auto_close | auto_close | não |
| TA-A029 | auto_close | True | 0.87 | 0.88 | 0.17 | 0.14 | auto_close | auto_close | não |
| TA-A032 | auto_close | True | 0.72 | 0.63 | 0.02 | 0.03 | auto_close | notify_owner | não |
| TA-A033 | contain_now | False | 0.10 | 0.05 | 0.90 | 0.91 | contain_now | contain_now | sim |
| TA-A038 | queue_tier2 | False | 0.13 | 0.06 | 0.65 | 0.67 | queue_tier2 | queue_tier2 | não |

## Custo

| variante | requisicoes | novas | tokens_por_alerta | falhas |
|---|---|---|---|---|
| com fatos | 40 | 0 | 2304 | 0 |
| sem fatos | 40 | 40 | 2229 | 0 |
