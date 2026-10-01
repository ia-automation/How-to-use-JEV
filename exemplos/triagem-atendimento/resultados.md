# Resultados — triagem-atendimento

Gerado por `run.py` em 2026-09-30 (modo `gravado`; modelo e amostra em cada seção). Perguntas, limiares e pesos: `perguntas.py`. Preço: US$ 0,042 por milhão de tokens de entrada.

Versão congelada: `perguntas.py` sha256 047fee075567f18b… · `triagem.py` sha256 7acaab2599cdc2dd…

## Lado a lado

### Acerto por pergunta (resposta dura) e desacordo pt × en

| pergunta | ajuste en | ajuste pt | ajuste pt+perg_pt | teste en | teste pt | teste pt+perg_pt | desacordo ajuste | desacordo teste |
|---|---|---|---|---|---|---|---|---|
| setor | 0.964 | 0.964 | 0.964 | 0.964 | 0.982 | 0.964 | 0.000 | 0.017 |
| pede_reembolso | 0.966 | 1.000 | 1.000 | 0.983 | 0.983 | 0.983 | 0.026 | 0.025 |
| quer_humano | 1.000 | 1.000 | 1.000 | 0.966 | 1.000 | 0.983 | 0.009 | 0.019 |
| ameaca_cancelar | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.007 | 0.005 |
| frustracao | 0.967 | 0.933 | 0.933 | 0.933 | 0.933 | 0.900 | 0.028 | 0.042 |

### Roteamento, prioridade, latência e custo

| conjunto | variante | n | humano | cobertura_auto | erro_entre_automaticos | humano_sem_necessidade | nulo_tratado_como_duvida | prioridade_acerto_faixa | p50_ms | p95_ms | tokens_por_ticket | US$_por_1000_tickets | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | en | 30 | 12 | 0.600 | 0.000 | 0 | 2/3 | 1.000 | 284 | 384 | 2223 | 0.0934 | jev-1.13.0 |
| ajuste | pt | 30 | 12 | 0.600 | 0.000 | 0 | 2/3 | 1.000 | 284 | 338 | 2225 | 0.0935 | jev-1.13.0 |
| ajuste | pt+perg_pt | 30 | 12 | 0.600 | 0.000 | 0 | 2/3 | 0.966 | 273 | 334 | 2449 | 0.1029 | jev-1.13.0 |
| teste | en | 60 | 21 | 0.650 | 0.000 | 2 | 4/9 | 1.000 | 271 | 434 | 2225 | 0.0935 | jev-1.13.0 |
| teste | pt | 60 | 17 | 0.717 | 0.047 | 0 | 2/9 | 0.983 | 280 | 355 | 2228 | 0.0936 | jev-1.13.0 |
| teste | pt+perg_pt | 60 | 20 | 0.667 | 0.025 | 2 | 2/9 | 0.966 | 272 | 493 | 2452 | 0.1030 | jev-1.13.0 |

## Conjunto `ajuste` — 30 casos (arquivo versão 2026-09-30, autor codex)

### Acerto por pergunta e por língua

Resposta dura, sem faixa de dúvida: setor = opção vencedora; sim/não = noul ≥ 0,5; frustração = nível mais próximo do score. `en` e `pt` usam as MESMAS perguntas em inglês; `pt+perg_pt` troca também a pergunta. `desacordo pt×en`: setor = fração de escolhas diferentes; sim/não = média de |noul_pt − noul_en|; frustração = média de |score_pt − score_en| (escala 0–2). Referência de ruído (mesma requisição repetida, 30 pares, rascunho 2026-09-30): noul média 0,011 (p95 0,05); score média 0,008 — desacordo nessa ordem de grandeza não pode ser atribuído à língua (a média do ruído não identifica a causa de cada diferença).

| pergunta | n | acerto_en | acerto_pt | acerto_pt+perg_pt | Δ pt−en | desacordo pt×en |
|---|---|---|---|---|---|---|
| setor | 28 | 0.964 | 0.964 | 0.964 | 0.000 | 0.000 |
| pede_reembolso | 29 | 0.966 | 1.000 | 1.000 | 0.034 | 0.026 |
| quer_humano | 30 | 1.000 | 1.000 | 1.000 | 0.000 | 0.009 |
| ameaca_cancelar | 30 | 1.000 | 1.000 | 1.000 | 0.000 | 0.007 |
| frustracao | 30 | 0.967 | 0.933 | 0.933 | -0.033 | 0.028 |

### Setor — cobertura automática × erro por limiar de confiança

**en** — atual SETOR_CONF_MIN=0.5, SETOR_COPIA_SIM=0.7; tickets com cópia: 3; gabarito no vencedor ou numa cópia: 27/28

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.036 | 28 |
| 0.300 | 1.000 | 0.036 | 28 |
| 0.500 | 1.000 | 0.036 | 28 |
| 0.700 | 0.964 | 0.000 | 27 |
| 0.900 | 0.929 | 0.000 | 26 |

**pt** — atual SETOR_CONF_MIN=0.5, SETOR_COPIA_SIM=0.7; tickets com cópia: 4; gabarito no vencedor ou numa cópia: 27/28

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.036 | 28 |
| 0.300 | 1.000 | 0.036 | 28 |
| 0.500 | 1.000 | 0.036 | 28 |
| 0.700 | 0.964 | 0.000 | 27 |
| 0.900 | 0.857 | 0.000 | 24 |

**pt+perg_pt** — atual SETOR_CONF_MIN=0.5, SETOR_COPIA_SIM=0.7; tickets com cópia: 7; gabarito no vencedor ou numa cópia: 27/28

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.036 | 28 |
| 0.300 | 1.000 | 0.036 | 28 |
| 0.500 | 0.964 | 0.000 | 27 |
| 0.700 | 0.964 | 0.000 | 27 |
| 0.900 | 0.929 | 0.000 | 26 |

### Sim/não — faixa de dúvida (limiares de `perguntas.py`) e Brier

| pergunta | variante | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|
| pede_reembolso | en | 0.2–0.8 | 0.966 | 1.000 | 1 | 29 | 0.022 |
| pede_reembolso | pt | 0.2–0.8 | 0.966 | 1.000 | 1 | 29 | 0.006 |
| pede_reembolso | pt+perg_pt | 0.2–0.8 | 0.966 | 1.000 | 1 | 29 | 0.004 |
| quer_humano | en | 0.2–0.8 | 1.000 | 1.000 | 0 | 30 | 0.002 |
| quer_humano | pt | 0.2–0.8 | 0.967 | 1.000 | 1 | 30 | 0.003 |
| quer_humano | pt+perg_pt | 0.2–0.8 | 0.967 | 1.000 | 1 | 30 | 0.006 |
| ameaca_cancelar | en | 0.2–0.8 | 1.000 | 1.000 | 0 | 30 | 0.001 |
| ameaca_cancelar | pt | 0.2–0.8 | 0.967 | 1.000 | 1 | 30 | 0.002 |
| ameaca_cancelar | pt+perg_pt | 0.2–0.8 | 0.967 | 1.000 | 1 | 30 | 0.004 |

### Frustração — cobertura × erro por confiança do Score

Informativo: frustração não manda para humano (só alimenta a prioridade, pelo score contínuo).

**en**

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.033 | 30 |
| 0.300 | 1.000 | 0.033 | 30 |
| 0.500 | 0.900 | 0.000 | 27 |
| 0.700 | 0.867 | 0.000 | 26 |
| 0.900 | 0.867 | 0.000 | 26 |

**pt**

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.067 | 30 |
| 0.300 | 0.967 | 0.034 | 29 |
| 0.500 | 0.933 | 0.036 | 28 |
| 0.700 | 0.900 | 0.000 | 27 |
| 0.900 | 0.867 | 0.000 | 26 |

**pt+perg_pt**

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.067 | 30 |
| 0.300 | 0.967 | 0.034 | 29 |
| 0.500 | 0.967 | 0.034 | 29 |
| 0.700 | 0.900 | 0.000 | 27 |
| 0.900 | 0.867 | 0.000 | 26 |

### Prioridade composta — faixa prevista × faixa do gabarito (mesma fórmula sobre os rótulos)

| variante | n | acerto_faixa | confusao (gab→prev) |
|---|---|---|---|
| en | 29 | 1.000 | {('alta', 'alta'): 4, ('baixa', 'baixa'): 18, ('media', 'media'): 7} |
| pt | 29 | 1.000 | {('alta', 'alta'): 4, ('baixa', 'baixa'): 18, ('media', 'media'): 7} |
| pt+perg_pt | 29 | 0.966 | {('alta', 'alta'): 4, ('baixa', 'baixa'): 17, ('baixa', 'media'): 1, ('media', 'media'): 7} |

### Roteamento — o incerto vai para humano

Erro entre automáticos = setor ou algum sim/não decidido errado; gabarito nulo decidido sozinho conta como erro. Frustração fica fora (não roteia). `nulo_tratado_como_duvida`: setor sem informação, abaixo do piso ou com cópia sem principal claro; sim/não na faixa do meio.

| variante | humano | automatico | erro_entre_automaticos | humano_sem_necessidade | nulo_tratado_como_duvida | setor_nulo_com_copia |
|---|---|---|---|---|---|---|
| en | 12 | 18 | 0.000 | 0 | 2/3 | 1 |
| pt | 12 | 18 | 0.000 | 0 | 2/3 | 1 |
| pt+perg_pt | 12 | 18 | 0.000 | 0 | 2/3 | 1 |

**Curva do roteamento** — mesmas respostas, outros limiares (piso de confiança do setor × faixa de dúvida dos sim/não, a mesma nos três; piso com cópia fixo em 0.9). Linha atual: piso 0.5, faixas [(0.2, 0.8)].

**en**

| piso_setor | faixa_sim_nao | cobertura | erro_automatico | n_auto |
|---|---|---|---|---|
| 0.000 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.000 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.000 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.000 | 0.1–0.9 | 0.600 | 0.000 | 18 |
| 0.500 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.500 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.500 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.500 | 0.1–0.9 | 0.600 | 0.000 | 18 |
| 0.700 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.700 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.700 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.700 | 0.1–0.9 | 0.600 | 0.000 | 18 |
| 0.900 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.900 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.900 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.900 | 0.1–0.9 | 0.600 | 0.000 | 18 |

**pt**

| piso_setor | faixa_sim_nao | cobertura | erro_automatico | n_auto |
|---|---|---|---|---|
| 0.000 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.000 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.000 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.000 | 0.1–0.9 | 0.567 | 0.000 | 17 |
| 0.500 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.500 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.500 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.500 | 0.1–0.9 | 0.567 | 0.000 | 17 |
| 0.700 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.700 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.700 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.700 | 0.1–0.9 | 0.567 | 0.000 | 17 |
| 0.900 | 0.5–0.5 | 0.567 | 0.000 | 17 |
| 0.900 | 0.3–0.7 | 0.567 | 0.000 | 17 |
| 0.900 | 0.2–0.8 | 0.567 | 0.000 | 17 |
| 0.900 | 0.1–0.9 | 0.533 | 0.000 | 16 |

**pt+perg_pt**

| piso_setor | faixa_sim_nao | cobertura | erro_automatico | n_auto |
|---|---|---|---|---|
| 0.000 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.000 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.000 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.000 | 0.1–0.9 | 0.600 | 0.000 | 18 |
| 0.500 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.500 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.500 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.500 | 0.1–0.9 | 0.600 | 0.000 | 18 |
| 0.700 | 0.5–0.5 | 0.600 | 0.000 | 18 |
| 0.700 | 0.3–0.7 | 0.600 | 0.000 | 18 |
| 0.700 | 0.2–0.8 | 0.600 | 0.000 | 18 |
| 0.700 | 0.1–0.9 | 0.600 | 0.000 | 18 |
| 0.900 | 0.5–0.5 | 0.567 | 0.000 | 17 |
| 0.900 | 0.3–0.7 | 0.567 | 0.000 | 17 |
| 0.900 | 0.2–0.8 | 0.567 | 0.000 | 17 |
| 0.900 | 0.1–0.9 | 0.567 | 0.000 | 17 |

### Custo e latência (medidos na chamada real; do cache também)

| variante | requisicoes | perguntas | p50_ms | p95_ms | tokens_por_ticket | US$_total | US$_por_1000_tickets | modelo |
|---|---|---|---|---|---|---|---|---|
| en | 30 | 300 | 284 | 384 | 2223 | 0.002802 | 0.0934 | jev-1.13.0 |
| pt | 30 | 300 | 284 | 338 | 2225 | 0.002804 | 0.0935 | jev-1.13.0 |
| pt+perg_pt | 30 | 300 | 273 | 334 | 2449 | 0.003086 | 0.1029 | jev-1.13.0 |

### Caso a caso

| id | var | setor | reemb | humano | cancelar | frustr | prior | destino | erros |
|---|---|---|---|---|---|---|---|---|---|
| TR-A001 | en | pagamento (1.00) | 0.990 | 0.020 | 0.020 | 0.00 (1.00) | 0.16 baixa | fila:pagamento | — |
| TR-A001 | pt | pagamento (1.00) | 0.980 | 0.030 | 0.020 | 0.01 (0.98) | 0.16 baixa | fila:pagamento | — |
| TR-A001 | pt+perg_pt | pagamento (1.00) +troca_devolucao | 0.980 | 0.030 | 0.020 | 0.03 (0.95) | 0.16 baixa | fila:pagamento | — |
| TR-A002 | en | pagamento (1.00) | 0.050 | 0.030 | 0.020 | 0.00 (0.99) | 0.02 baixa | fila:pagamento | — |
| TR-A002 | pt | pagamento (1.00) | 0.060 | 0.030 | 0.020 | 0.01 (0.99) | 0.02 baixa | fila:pagamento | — |
| TR-A002 | pt+perg_pt | pagamento (1.00) | 0.050 | 0.040 | 0.030 | 0.02 (0.97) | 0.03 baixa | fila:pagamento | — |
| TR-A003 | en | pagamento (1.00) | 0.980 | 0.980 | 0.030 | 1.00 (1.00) | 0.50 media | humano | — |
| TR-A003 | pt | pagamento (1.00) | 0.960 | 0.980 | 0.040 | 1.00 (1.00) | 0.50 media | humano | — |
| TR-A003 | pt+perg_pt | pagamento (1.00) +troca_devolucao | 0.980 | 0.980 | 0.040 | 1.00 (1.00) | 0.51 media | humano | — |
| TR-A004 | en | pagamento (1.00) +troca_devolucao | 0.780 | 0.960 | 0.980 | 2.00 (1.00) | 0.95 alta | humano | pede_reembolso |
| TR-A004 | pt | pagamento (1.00) +troca_devolucao | 0.330 | 0.920 | 0.980 | 2.00 (1.00) | 0.88 alta | humano | — |
| TR-A004 | pt+perg_pt | pagamento (1.00) +troca_devolucao | 0.300 | 0.920 | 0.980 | 2.00 (1.00) | 0.88 alta | humano | — |
| TR-A005 | en | pagamento (1.00) | 0.020 | 0.030 | 0.020 | 0.01 (0.99) | 0.02 baixa | fila:pagamento | — |
| TR-A005 | pt | pagamento (0.98) | 0.020 | 0.030 | 0.020 | 0.02 (0.98) | 0.02 baixa | fila:pagamento | — |
| TR-A005 | pt+perg_pt | pagamento (1.00) | 0.020 | 0.030 | 0.020 | 0.02 (0.96) | 0.02 baixa | fila:pagamento | — |
| TR-A006 | en | entrega (1.00) | 0.030 | 0.030 | 0.020 | 0.06 (0.91) | 0.03 baixa | fila:entrega | — |
| TR-A006 | pt | entrega (1.00) | 0.020 | 0.030 | 0.020 | 0.07 (0.89) | 0.03 baixa | fila:entrega | — |
| TR-A006 | pt+perg_pt | entrega (1.00) | 0.030 | 0.030 | 0.030 | 0.14 (0.79) | 0.05 baixa | fila:entrega | — |
| TR-A007 | en | entrega (1.00) | 0.100 | 0.030 | 0.970 | 1.00 (1.00) | 0.51 media | fila:entrega | — |
| TR-A007 | pt | entrega (1.00) | 0.110 | 0.030 | 0.980 | 1.00 (1.00) | 0.52 media | fila:entrega | — |
| TR-A007 | pt+perg_pt | entrega (1.00) | 0.090 | 0.030 | 0.970 | 1.00 (1.00) | 0.51 media | fila:entrega | — |
| TR-A008 | en | entrega (1.00) | 0.020 | 0.950 | 0.020 | 0.07 (0.90) | 0.17 baixa | humano | — |
| TR-A008 | pt | entrega (1.00) | 0.020 | 0.950 | 0.020 | 0.04 (0.94) | 0.16 baixa | humano | — |
| TR-A008 | pt+perg_pt | entrega (1.00) | 0.020 | 0.940 | 0.030 | 0.02 (0.97) | 0.16 baixa | humano | — |
| TR-A009 | en | entrega (0.71) | 0.980 | 0.980 | 0.040 | 2.00 (1.00) | 0.71 alta | humano | — |
| TR-A009 | pt | entrega (0.73) | 0.970 | 0.980 | 0.050 | 2.00 (1.00) | 0.71 alta | humano | — |
| TR-A009 | pt+perg_pt | entrega (0.95) | 0.970 | 0.970 | 0.090 | 2.00 (1.00) | 0.72 alta | humano | — |
| TR-A010 | en | entrega (1.00) | 0.020 | 0.020 | 0.050 | 0.01 (0.99) | 0.02 baixa | fila:entrega | — |
| TR-A010 | pt | entrega (1.00) | 0.020 | 0.030 | 0.060 | 0.03 (0.96) | 0.03 baixa | fila:entrega | — |
| TR-A010 | pt+perg_pt | entrega (1.00) | 0.020 | 0.030 | 0.070 | 0.03 (0.95) | 0.03 baixa | fila:entrega | — |
| TR-A011 | en | troca_devolucao (1.00) | 0.020 | 0.020 | 0.020 | 0.03 (0.96) | 0.02 baixa | fila:troca_devolucao | — |
| TR-A011 | pt | troca_devolucao (1.00) +produto_duvida | 0.020 | 0.030 | 0.020 | 0.03 (0.95) | 0.02 baixa | fila:troca_devolucao | — |
| TR-A011 | pt+perg_pt | troca_devolucao (1.00) +produto_duvida | 0.030 | 0.030 | 0.030 | 0.03 (0.96) | 0.02 baixa | fila:troca_devolucao | — |
| TR-A012 | en | troca_devolucao (1.00) | 0.970 | 0.970 | 0.030 | 0.02 (0.96) | 0.30 media | humano | — |
| TR-A012 | pt | troca_devolucao (1.00) | 0.970 | 0.940 | 0.060 | 0.01 (0.98) | 0.31 media | humano | — |
| TR-A012 | pt+perg_pt | troca_devolucao (1.00) | 0.970 | 0.960 | 0.070 | 0.01 (0.98) | 0.31 media | humano | — |
| TR-A013 | en | troca_devolucao (1.00) | 0.040 | 0.090 | 0.020 | 1.00 (1.00) | 0.23 baixa | fila:troca_devolucao | — |
| TR-A013 | pt | troca_devolucao (1.00) | 0.090 | 0.070 | 0.020 | 0.99 (0.98) | 0.23 baixa | fila:troca_devolucao | — |
| TR-A013 | pt+perg_pt | troca_devolucao (1.00) +conta_acesso | 0.080 | 0.080 | 0.020 | 0.99 (0.98) | 0.23 baixa | fila:troca_devolucao | — |
| TR-A014 | en | troca_devolucao (1.00) | 0.970 | 0.980 | 0.970 | 2.00 (1.00) | 0.98 alta | humano | — |
| TR-A014 | pt | troca_devolucao (0.89) | 0.960 | 0.980 | 0.970 | 2.00 (1.00) | 0.98 alta | humano | — |
| TR-A014 | pt+perg_pt | troca_devolucao (0.90) | 0.980 | 0.980 | 0.960 | 2.00 (1.00) | 0.98 alta | humano | — |
| TR-A015 | en | troca_devolucao (1.00) | 0.970 | 0.020 | 0.030 | 0.44 (0.34) | 0.25 baixa | fila:troca_devolucao | — |
| TR-A015 | pt | troca_devolucao (0.98) | 0.940 | 0.030 | 0.040 | 0.56 (0.15) | 0.27 baixa | fila:troca_devolucao | frustracao |
| TR-A015 | pt+perg_pt | troca_devolucao (0.99) | 0.960 | 0.030 | 0.050 | 0.87 (0.00) | 0.34 media | fila:troca_devolucao | frustracao |
| TR-A016 | en | conta_acesso (1.00) | 0.010 | 0.020 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:conta_acesso | — |
| TR-A016 | pt | conta_acesso (1.00) | 0.010 | 0.030 | 0.020 | 0.01 (0.99) | 0.01 baixa | fila:conta_acesso | — |
| TR-A016 | pt+perg_pt | conta_acesso (1.00) | 0.010 | 0.030 | 0.020 | 0.00 (0.99) | 0.01 baixa | fila:conta_acesso | — |
| TR-A017 | en | conta_acesso (1.00) | 0.010 | 0.970 | 0.020 | 1.00 (1.00) | 0.35 media | humano | — |
| TR-A017 | pt | conta_acesso (1.00) | 0.020 | 0.980 | 0.020 | 1.00 (1.00) | 0.36 media | humano | — |
| TR-A017 | pt+perg_pt | conta_acesso (1.00) | 0.020 | 0.980 | 0.030 | 1.00 (1.00) | 0.36 media | humano | — |
| TR-A018 | en | conta_acesso (0.99) | 0.080 | 0.030 | 0.980 | 0.05 (0.93) | 0.32 media | fila:conta_acesso | — |
| TR-A018 | pt | conta_acesso (0.97) | 0.090 | 0.030 | 0.970 | 0.02 (0.97) | 0.31 media | fila:conta_acesso | — |
| TR-A018 | pt+perg_pt | conta_acesso (0.98) | 0.080 | 0.040 | 0.960 | 0.06 (0.91) | 0.32 media | fila:conta_acesso | — |
| TR-A019 | en | pagamento (0.51) +troca_devolucao | 0.980 | 0.980 | 0.130 | 2.00 (1.00) | 0.73 alta | humano | setor |
| TR-A019 | pt | pagamento (0.69) +troca_devolucao | 0.980 | 0.980 | 0.220 | 2.00 (1.00) | 0.76 alta | humano | setor |
| TR-A019 | pt+perg_pt | pagamento (0.45) +troca_devolucao | 0.980 | 0.970 | 0.290 | 2.00 (1.00) | 0.78 alta | humano | setor |
| TR-A020 | en | conta_acesso (1.00) | 0.020 | 0.030 | 0.020 | 0.36 (0.46) | 0.09 baixa | fila:conta_acesso | — |
| TR-A020 | pt | conta_acesso (1.00) | 0.010 | 0.030 | 0.020 | 0.04 (0.94) | 0.02 baixa | fila:conta_acesso | — |
| TR-A020 | pt+perg_pt | conta_acesso (1.00) | 0.020 | 0.030 | 0.020 | 0.03 (0.95) | 0.02 baixa | fila:conta_acesso | — |
| TR-A021 | en | produto_duvida (1.00) | 0.010 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-A021 | pt | produto_duvida (1.00) | 0.010 | 0.010 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-A021 | pt+perg_pt | produto_duvida (1.00) | 0.010 | 0.020 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-A022 | en | produto_duvida (1.00) | 0.010 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-A022 | pt | produto_duvida (1.00) | 0.020 | 0.030 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-A022 | pt+perg_pt | produto_duvida (1.00) | 0.010 | 0.030 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-A023 | en | produto_duvida (0.98) | 0.020 | 0.810 | 0.020 | 1.00 (1.00) | 0.33 media | humano | — |
| TR-A023 | pt | produto_duvida (1.00) | 0.020 | 0.750 | 0.030 | 1.00 (1.00) | 0.32 media | humano | — |
| TR-A023 | pt+perg_pt | produto_duvida (1.00) | 0.020 | 0.630 | 0.040 | 1.00 (1.00) | 0.31 media | humano | — |
| TR-A024 | en | produto_duvida (0.98) | 0.080 | 0.040 | 0.930 | 0.24 (0.63) | 0.34 media | fila:produto_duvida | — |
| TR-A024 | pt | produto_duvida (0.99) | 0.060 | 0.040 | 0.940 | 0.36 (0.46) | 0.37 media | fila:produto_duvida | — |
| TR-A024 | pt+perg_pt | produto_duvida (0.97) | 0.060 | 0.060 | 0.930 | 0.30 (0.54) | 0.36 media | fila:produto_duvida | — |
| TR-A025 | en | produto_duvida (1.00) | 0.010 | 0.020 | 0.020 | 0.65 (0.47) | 0.14 baixa | fila:produto_duvida | frustracao |
| TR-A025 | pt | produto_duvida (0.81) | 0.020 | 0.020 | 0.020 | 0.73 (0.59) | 0.16 baixa | fila:produto_duvida | frustracao |
| TR-A025 | pt+perg_pt | produto_duvida (0.86) | 0.020 | 0.030 | 0.030 | 0.77 (0.66) | 0.17 baixa | fila:produto_duvida | frustracao |
| TR-A026 | en | outro (0.99) | 0.020 | 0.010 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:outro | — |
| TR-A026 | pt | outro (0.99) | 0.020 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:outro | — |
| TR-A026 | pt+perg_pt | outro (0.99) | 0.020 | 0.010 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:outro | — |
| TR-A027 | en | outro (1.00) | 0.010 | 0.940 | 0.010 | 0.00 (1.00) | 0.15 baixa | humano | — |
| TR-A027 | pt | outro (1.00) | 0.010 | 0.960 | 0.010 | 0.00 (1.00) | 0.15 baixa | humano | — |
| TR-A027 | pt+perg_pt | outro (1.00) | 0.010 | 0.950 | 0.010 | 0.00 (1.00) | 0.15 baixa | humano | — |
| TR-A028 | en | outro (1.00) | 0.020 | 0.050 | 0.010 | 0.06 (0.91) | 0.03 baixa | fila:outro | — |
| TR-A028 | pt | outro (1.00) | 0.020 | 0.040 | 0.020 | 0.04 (0.94) | 0.02 baixa | fila:outro | — |
| TR-A028 | pt+perg_pt | outro (1.00) | 0.020 | 0.040 | 0.020 | 0.07 (0.90) | 0.03 baixa | fila:outro | — |
| TR-A029 | en | None (1.00) | 0.100 | 0.040 | 0.020 | 0.02 (0.97) | 0.03 baixa | humano | — |
| TR-A029 | pt | None (1.00) | 0.190 | 0.050 | 0.020 | 0.01 (0.99) | 0.04 baixa | humano | — |
| TR-A029 | pt+perg_pt | None (1.00) | 0.140 | 0.050 | 0.020 | 0.02 (0.97) | 0.04 baixa | humano | — |
| TR-A030 | en | conta_acesso (0.48) +troca_devolucao | 0.030 | 0.030 | 0.020 | 0.02 (0.97) | 0.02 baixa | humano | — |
| TR-A030 | pt | conta_acesso (0.64) +troca_devolucao | 0.030 | 0.030 | 0.020 | 0.03 (0.96) | 0.02 baixa | humano | — |
| TR-A030 | pt+perg_pt | conta_acesso (0.75) +troca_devolucao | 0.020 | 0.030 | 0.020 | 0.01 (0.99) | 0.02 baixa | humano | — |

## Conjunto `teste` — 60 casos (arquivo versão 2026-09-30, autor codex)

### Acerto por pergunta e por língua

Resposta dura, sem faixa de dúvida: setor = opção vencedora; sim/não = noul ≥ 0,5; frustração = nível mais próximo do score. `en` e `pt` usam as MESMAS perguntas em inglês; `pt+perg_pt` troca também a pergunta. `desacordo pt×en`: setor = fração de escolhas diferentes; sim/não = média de |noul_pt − noul_en|; frustração = média de |score_pt − score_en| (escala 0–2). Referência de ruído (mesma requisição repetida, 30 pares, rascunho 2026-09-30): noul média 0,011 (p95 0,05); score média 0,008 — desacordo nessa ordem de grandeza não pode ser atribuído à língua (a média do ruído não identifica a causa de cada diferença).

| pergunta | n | acerto_en | acerto_pt | acerto_pt+perg_pt | Δ pt−en | desacordo pt×en |
|---|---|---|---|---|---|---|
| setor | 56 | 0.964 | 0.982 | 0.964 | 0.018 | 0.017 |
| pede_reembolso | 58 | 0.983 | 0.983 | 0.983 | 0.000 | 0.025 |
| quer_humano | 59 | 0.966 | 1.000 | 0.983 | 0.034 | 0.019 |
| ameaca_cancelar | 58 | 1.000 | 1.000 | 1.000 | 0.000 | 0.005 |
| frustracao | 60 | 0.933 | 0.933 | 0.900 | 0.000 | 0.042 |

### Setor — cobertura automática × erro por limiar de confiança

**en** — atual SETOR_CONF_MIN=0.5, SETOR_COPIA_SIM=0.7; tickets com cópia: 5; gabarito no vencedor ou numa cópia: 56/56

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.036 | 56 |
| 0.300 | 1.000 | 0.036 | 56 |
| 0.500 | 0.982 | 0.036 | 55 |
| 0.700 | 0.964 | 0.019 | 54 |
| 0.900 | 0.929 | 0.000 | 52 |

**pt** — atual SETOR_CONF_MIN=0.5, SETOR_COPIA_SIM=0.7; tickets com cópia: 6; gabarito no vencedor ou numa cópia: 55/56

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.018 | 56 |
| 0.300 | 1.000 | 0.018 | 56 |
| 0.500 | 0.982 | 0.018 | 55 |
| 0.700 | 0.964 | 0.019 | 54 |
| 0.900 | 0.946 | 0.000 | 53 |

**pt+perg_pt** — atual SETOR_CONF_MIN=0.5, SETOR_COPIA_SIM=0.7; tickets com cópia: 6; gabarito no vencedor ou numa cópia: 54/56

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.036 | 56 |
| 0.300 | 1.000 | 0.036 | 56 |
| 0.500 | 0.982 | 0.018 | 55 |
| 0.700 | 0.982 | 0.018 | 55 |
| 0.900 | 0.911 | 0.000 | 51 |

### Sim/não — faixa de dúvida (limiares de `perguntas.py`) e Brier

| pergunta | variante | faixa | cobertura | acerto_decididos | revisao | n | brier |
|---|---|---|---|---|---|---|---|
| pede_reembolso | en | 0.2–0.8 | 0.931 | 1.000 | 4 | 58 | 0.014 |
| pede_reembolso | pt | 0.2–0.8 | 0.983 | 0.982 | 1 | 58 | 0.016 |
| pede_reembolso | pt+perg_pt | 0.2–0.8 | 0.948 | 1.000 | 3 | 58 | 0.014 |
| quer_humano | en | 0.2–0.8 | 0.949 | 1.000 | 3 | 59 | 0.016 |
| quer_humano | pt | 0.2–0.8 | 0.966 | 1.000 | 2 | 59 | 0.008 |
| quer_humano | pt+perg_pt | 0.2–0.8 | 0.949 | 1.000 | 3 | 59 | 0.012 |
| ameaca_cancelar | en | 0.2–0.8 | 1.000 | 1.000 | 0 | 58 | 0.001 |
| ameaca_cancelar | pt | 0.2–0.8 | 0.983 | 1.000 | 1 | 58 | 0.002 |
| ameaca_cancelar | pt+perg_pt | 0.2–0.8 | 1.000 | 1.000 | 0 | 58 | 0.002 |

### Frustração — cobertura × erro por confiança do Score

Informativo: frustração não manda para humano (só alimenta a prioridade, pelo score contínuo).

**en**

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.067 | 60 |
| 0.300 | 1.000 | 0.067 | 60 |
| 0.500 | 0.933 | 0.018 | 56 |
| 0.700 | 0.833 | 0.020 | 50 |
| 0.900 | 0.617 | 0.000 | 37 |

**pt**

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.067 | 60 |
| 0.300 | 0.950 | 0.035 | 57 |
| 0.500 | 0.917 | 0.018 | 55 |
| 0.700 | 0.833 | 0.020 | 50 |
| 0.900 | 0.600 | 0.000 | 36 |

**pt+perg_pt**

| limiar | cobertura | erro_automatico | n_auto |
|---|---|---|---|
| 0.000 | 1.000 | 0.100 | 60 |
| 0.300 | 1.000 | 0.100 | 60 |
| 0.500 | 0.900 | 0.037 | 54 |
| 0.700 | 0.750 | 0.022 | 45 |
| 0.900 | 0.600 | 0.000 | 36 |

### Prioridade composta — faixa prevista × faixa do gabarito (mesma fórmula sobre os rótulos)

| variante | n | acerto_faixa | confusao (gab→prev) |
|---|---|---|---|
| en | 58 | 1.000 | {('alta', 'alta'): 3, ('baixa', 'baixa'): 43, ('media', 'media'): 12} |
| pt | 58 | 0.983 | {('alta', 'alta'): 3, ('baixa', 'baixa'): 42, ('baixa', 'media'): 1, ('media', 'media'): 12} |
| pt+perg_pt | 58 | 0.966 | {('alta', 'alta'): 3, ('baixa', 'baixa'): 41, ('baixa', 'media'): 2, ('media', 'media'): 12} |

### Roteamento — o incerto vai para humano

Erro entre automáticos = setor ou algum sim/não decidido errado; gabarito nulo decidido sozinho conta como erro. Frustração fica fora (não roteia). `nulo_tratado_como_duvida`: setor sem informação, abaixo do piso ou com cópia sem principal claro; sim/não na faixa do meio.

| variante | humano | automatico | erro_entre_automaticos | humano_sem_necessidade | nulo_tratado_como_duvida | setor_nulo_com_copia |
|---|---|---|---|---|---|---|
| en | 21 | 39 | 0.000 | 2 | 4/9 | 1 |
| pt | 17 | 43 | 0.047 | 0 | 2/9 | 2 |
| pt+perg_pt | 20 | 40 | 0.025 | 2 | 2/9 | 2 |

**Curva do roteamento** — mesmas respostas, outros limiares (piso de confiança do setor × faixa de dúvida dos sim/não, a mesma nos três; piso com cópia fixo em 0.9). Linha atual: piso 0.5, faixas [(0.2, 0.8)].

**en**

| piso_setor | faixa_sim_nao | cobertura | erro_automatico | n_auto |
|---|---|---|---|---|
| 0.000 | 0.5–0.5 | 0.733 | 0.068 | 44 |
| 0.000 | 0.3–0.7 | 0.650 | 0.000 | 39 |
| 0.000 | 0.2–0.8 | 0.650 | 0.000 | 39 |
| 0.000 | 0.1–0.9 | 0.633 | 0.000 | 38 |
| 0.500 | 0.5–0.5 | 0.717 | 0.070 | 43 |
| 0.500 | 0.3–0.7 | 0.650 | 0.000 | 39 |
| 0.500 | 0.2–0.8 | 0.650 | 0.000 | 39 |
| 0.500 | 0.1–0.9 | 0.633 | 0.000 | 38 |
| 0.700 | 0.5–0.5 | 0.717 | 0.070 | 43 |
| 0.700 | 0.3–0.7 | 0.650 | 0.000 | 39 |
| 0.700 | 0.2–0.8 | 0.650 | 0.000 | 39 |
| 0.700 | 0.1–0.9 | 0.633 | 0.000 | 38 |
| 0.900 | 0.5–0.5 | 0.700 | 0.071 | 42 |
| 0.900 | 0.3–0.7 | 0.633 | 0.000 | 38 |
| 0.900 | 0.2–0.8 | 0.633 | 0.000 | 38 |
| 0.900 | 0.1–0.9 | 0.617 | 0.000 | 37 |

**pt**

| piso_setor | faixa_sim_nao | cobertura | erro_automatico | n_auto |
|---|---|---|---|---|
| 0.000 | 0.5–0.5 | 0.733 | 0.068 | 44 |
| 0.000 | 0.3–0.7 | 0.717 | 0.047 | 43 |
| 0.000 | 0.2–0.8 | 0.717 | 0.047 | 43 |
| 0.000 | 0.1–0.9 | 0.617 | 0.027 | 37 |
| 0.500 | 0.5–0.5 | 0.733 | 0.068 | 44 |
| 0.500 | 0.3–0.7 | 0.717 | 0.047 | 43 |
| 0.500 | 0.2–0.8 | 0.717 | 0.047 | 43 |
| 0.500 | 0.1–0.9 | 0.617 | 0.027 | 37 |
| 0.700 | 0.5–0.5 | 0.717 | 0.070 | 43 |
| 0.700 | 0.3–0.7 | 0.700 | 0.048 | 42 |
| 0.700 | 0.2–0.8 | 0.700 | 0.048 | 42 |
| 0.700 | 0.1–0.9 | 0.617 | 0.027 | 37 |
| 0.900 | 0.5–0.5 | 0.700 | 0.048 | 42 |
| 0.900 | 0.3–0.7 | 0.683 | 0.024 | 41 |
| 0.900 | 0.2–0.8 | 0.683 | 0.024 | 41 |
| 0.900 | 0.1–0.9 | 0.600 | 0.000 | 36 |

**pt+perg_pt**

| piso_setor | faixa_sim_nao | cobertura | erro_automatico | n_auto |
|---|---|---|---|---|
| 0.000 | 0.5–0.5 | 0.733 | 0.091 | 44 |
| 0.000 | 0.3–0.7 | 0.700 | 0.048 | 42 |
| 0.000 | 0.2–0.8 | 0.667 | 0.025 | 40 |
| 0.000 | 0.1–0.9 | 0.617 | 0.027 | 37 |
| 0.500 | 0.5–0.5 | 0.733 | 0.091 | 44 |
| 0.500 | 0.3–0.7 | 0.700 | 0.048 | 42 |
| 0.500 | 0.2–0.8 | 0.667 | 0.025 | 40 |
| 0.500 | 0.1–0.9 | 0.617 | 0.027 | 37 |
| 0.700 | 0.5–0.5 | 0.733 | 0.091 | 44 |
| 0.700 | 0.3–0.7 | 0.700 | 0.048 | 42 |
| 0.700 | 0.2–0.8 | 0.667 | 0.025 | 40 |
| 0.700 | 0.1–0.9 | 0.617 | 0.027 | 37 |
| 0.900 | 0.5–0.5 | 0.700 | 0.071 | 42 |
| 0.900 | 0.3–0.7 | 0.667 | 0.025 | 40 |
| 0.900 | 0.2–0.8 | 0.633 | 0.000 | 38 |
| 0.900 | 0.1–0.9 | 0.583 | 0.000 | 35 |

### Custo e latência (medidos na chamada real; do cache também)

| variante | requisicoes | perguntas | p50_ms | p95_ms | tokens_por_ticket | US$_total | US$_por_1000_tickets | modelo |
|---|---|---|---|---|---|---|---|---|
| en | 60 | 600 | 271 | 434 | 2225 | 0.005608 | 0.0935 | jev-1.13.0 |
| pt | 60 | 600 | 280 | 355 | 2228 | 0.005615 | 0.0936 | jev-1.13.0 |
| pt+perg_pt | 60 | 600 | 272 | 493 | 2452 | 0.006179 | 0.1030 | jev-1.13.0 |

### Caso a caso

| id | var | setor | reemb | humano | cancelar | frustr | prior | destino | erros |
|---|---|---|---|---|---|---|---|---|---|
| TR-T001 | en | pagamento (1.00) | 0.030 | 0.020 | 0.020 | 0.01 (0.99) | 0.02 baixa | fila:pagamento | — |
| TR-T001 | pt | pagamento (1.00) | 0.090 | 0.030 | 0.020 | 0.01 (0.99) | 0.03 baixa | fila:pagamento | — |
| TR-T001 | pt+perg_pt | pagamento (1.00) | 0.090 | 0.030 | 0.020 | 0.02 (0.97) | 0.03 baixa | fila:pagamento | — |
| TR-T002 | en | pagamento (1.00) | 0.070 | 0.940 | 0.030 | 0.67 (0.49) | 0.29 baixa | humano | frustracao |
| TR-T002 | pt | pagamento (1.00) | 0.100 | 0.940 | 0.040 | 0.53 (0.28) | 0.27 baixa | humano | frustracao |
| TR-T002 | pt+perg_pt | pagamento (1.00) | 0.090 | 0.940 | 0.060 | 0.74 (0.61) | 0.32 media | humano | frustracao |
| TR-T003 | en | pagamento (1.00) | 0.980 | 0.020 | 0.020 | 0.19 (0.71) | 0.19 baixa | fila:pagamento | — |
| TR-T003 | pt | pagamento (1.00) +troca_devolucao | 0.970 | 0.020 | 0.030 | 0.15 (0.78) | 0.19 baixa | fila:pagamento | — |
| TR-T003 | pt+perg_pt | pagamento (1.00) +troca_devolucao | 0.980 | 0.020 | 0.030 | 0.29 (0.57) | 0.22 baixa | fila:pagamento | — |
| TR-T004 | en | pagamento (0.85) | 0.050 | 0.040 | 0.020 | 1.00 (1.00) | 0.22 baixa | fila:pagamento | — |
| TR-T004 | pt | pagamento (0.97) | 0.030 | 0.050 | 0.020 | 1.00 (0.97) | 0.22 baixa | fila:pagamento | — |
| TR-T004 | pt+perg_pt | pagamento (0.97) | 0.040 | 0.040 | 0.030 | 0.99 (0.98) | 0.22 baixa | fila:pagamento | — |
| TR-T005 | en | pagamento (0.98) +troca_devolucao | 0.530 | 0.030 | 0.970 | 0.15 (0.77) | 0.41 media | humano | pede_reembolso |
| TR-T005 | pt | pagamento (0.98) +troca_devolucao | 0.130 | 0.020 | 0.980 | 0.12 (0.82) | 0.34 media | fila:pagamento | — |
| TR-T005 | pt+perg_pt | pagamento (0.98) | 0.070 | 0.030 | 0.980 | 0.32 (0.52) | 0.37 media | fila:pagamento | — |
| TR-T006 | en | pagamento (1.00) | 0.970 | 0.980 | 0.050 | 2.00 (1.00) | 0.71 alta | humano | — |
| TR-T006 | pt | pagamento (1.00) | 0.940 | 0.960 | 0.050 | 2.00 (1.00) | 0.70 alta | humano | — |
| TR-T006 | pt+perg_pt | pagamento (1.00) | 0.960 | 0.960 | 0.070 | 2.00 (1.00) | 0.71 alta | humano | — |
| TR-T007 | en | pagamento (1.00) | 0.020 | 0.030 | 0.020 | 0.14 (0.79) | 0.04 baixa | fila:pagamento | — |
| TR-T007 | pt | pagamento (1.00) | 0.030 | 0.030 | 0.020 | 0.19 (0.72) | 0.05 baixa | fila:pagamento | — |
| TR-T007 | pt+perg_pt | pagamento (1.00) | 0.030 | 0.030 | 0.030 | 0.08 (0.89) | 0.03 baixa | fila:pagamento | — |
| TR-T008 | en | pagamento (1.00) | 0.950 | 0.030 | 0.020 | 0.09 (0.86) | 0.17 baixa | fila:pagamento | — |
| TR-T008 | pt | pagamento (1.00) | 0.920 | 0.030 | 0.020 | 0.21 (0.69) | 0.19 baixa | fila:pagamento | — |
| TR-T008 | pt+perg_pt | pagamento (1.00) +troca_devolucao | 0.950 | 0.040 | 0.030 | 0.28 (0.58) | 0.21 baixa | fila:pagamento | — |
| TR-T009 | en | pagamento (1.00) | 0.030 | 0.030 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:pagamento | — |
| TR-T009 | pt | pagamento (1.00) | 0.030 | 0.040 | 0.020 | 0.00 (1.00) | 0.02 baixa | fila:pagamento | — |
| TR-T009 | pt+perg_pt | pagamento (1.00) | 0.030 | 0.040 | 0.020 | 0.00 (1.00) | 0.02 baixa | fila:pagamento | — |
| TR-T010 | en | pagamento (0.94) +troca_devolucao | 0.970 | 0.020 | 0.030 | 0.04 (0.93) | 0.17 baixa | fila:pagamento | — |
| TR-T010 | pt | pagamento (1.00) +troca_devolucao | 0.980 | 0.030 | 0.020 | 0.09 (0.87) | 0.18 baixa | fila:pagamento | — |
| TR-T010 | pt+perg_pt | pagamento (0.87) +troca_devolucao | 0.980 | 0.030 | 0.030 | 0.11 (0.83) | 0.18 baixa | humano | — |
| TR-T011 | en | entrega (1.00) | 0.020 | 0.020 | 0.010 | 0.01 (0.99) | 0.01 baixa | fila:entrega | — |
| TR-T011 | pt | entrega (1.00) | 0.020 | 0.020 | 0.010 | 0.01 (0.98) | 0.01 baixa | fila:entrega | — |
| TR-T011 | pt+perg_pt | entrega (1.00) | 0.020 | 0.020 | 0.020 | 0.01 (0.98) | 0.01 baixa | fila:entrega | — |
| TR-T012 | en | entrega (0.99) | 0.020 | 0.040 | 0.020 | 0.02 (0.97) | 0.02 baixa | fila:entrega | — |
| TR-T012 | pt | entrega (0.99) | 0.020 | 0.040 | 0.020 | 0.06 (0.92) | 0.03 baixa | fila:entrega | — |
| TR-T012 | pt+perg_pt | entrega (0.97) | 0.030 | 0.040 | 0.020 | 0.08 (0.89) | 0.03 baixa | fila:entrega | — |
| TR-T013 | en | entrega (1.00) | 0.030 | 0.980 | 0.020 | 1.00 (1.00) | 0.36 media | humano | — |
| TR-T013 | pt | entrega (1.00) | 0.030 | 0.970 | 0.030 | 1.00 (1.00) | 0.36 media | humano | — |
| TR-T013 | pt+perg_pt | entrega (1.00) | 0.020 | 0.960 | 0.040 | 1.00 (1.00) | 0.36 media | humano | — |
| TR-T014 | en | entrega (1.00) | 0.020 | 0.040 | 0.020 | 0.32 (0.52) | 0.08 baixa | fila:entrega | — |
| TR-T014 | pt | entrega (1.00) | 0.020 | 0.050 | 0.020 | 0.41 (0.38) | 0.10 baixa | fila:entrega | — |
| TR-T014 | pt+perg_pt | entrega (1.00) | 0.020 | 0.060 | 0.020 | 0.62 (0.42) | 0.14 baixa | fila:entrega | frustracao |
| TR-T015 | en | entrega (0.46) | 0.340 | 0.030 | 0.940 | 0.33 (0.50) | 0.40 media | humano | — |
| TR-T015 | pt | entrega (0.67) | 0.140 | 0.030 | 0.940 | 0.17 (0.75) | 0.34 media | fila:entrega | — |
| TR-T015 | pt+perg_pt | entrega (0.91) | 0.210 | 0.030 | 0.930 | 0.24 (0.64) | 0.36 media | humano | — |
| TR-T016 | en | entrega (0.96) | 0.120 | 0.420 | 0.990 | 2.00 (1.00) | 0.78 alta | humano | quer_humano |
| TR-T016 | pt | entrega (0.94) | 0.120 | 0.530 | 0.990 | 2.00 (1.00) | 0.79 alta | humano | — |
| TR-T016 | pt+perg_pt | entrega (0.98) | 0.120 | 0.570 | 0.980 | 2.00 (1.00) | 0.80 alta | humano | — |
| TR-T017 | en | entrega (1.00) | 0.020 | 0.020 | 0.060 | 0.03 (0.95) | 0.03 baixa | fila:entrega | — |
| TR-T017 | pt | entrega (0.99) | 0.030 | 0.030 | 0.080 | 0.03 (0.96) | 0.04 baixa | fila:entrega | — |
| TR-T017 | pt+perg_pt | entrega (0.98) | 0.030 | 0.030 | 0.100 | 0.03 (0.96) | 0.04 baixa | fila:entrega | — |
| TR-T018 | en | pagamento (0.79) +entrega | 0.980 | 0.030 | 0.030 | 0.01 (0.98) | 0.16 baixa | humano | setor |
| TR-T018 | pt | pagamento (0.82) | 0.980 | 0.030 | 0.030 | 0.02 (0.97) | 0.16 baixa | fila:pagamento | setor |
| TR-T018 | pt+perg_pt | pagamento (0.89) | 0.980 | 0.030 | 0.030 | 0.05 (0.92) | 0.17 baixa | fila:pagamento | setor |
| TR-T019 | en | entrega (0.99) | 0.020 | 0.030 | 0.020 | 0.03 (0.96) | 0.02 baixa | fila:entrega | — |
| TR-T019 | pt | entrega (1.00) | 0.020 | 0.030 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:entrega | — |
| TR-T019 | pt+perg_pt | entrega (1.00) | 0.020 | 0.030 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:entrega | — |
| TR-T020 | en | entrega (1.00) | 0.050 | 0.040 | 0.030 | 1.00 (1.00) | 0.22 baixa | fila:entrega | — |
| TR-T020 | pt | entrega (1.00) | 0.040 | 0.070 | 0.030 | 1.01 (0.99) | 0.23 baixa | fila:entrega | — |
| TR-T020 | pt+perg_pt | entrega (1.00) | 0.050 | 0.070 | 0.040 | 1.00 (1.00) | 0.23 baixa | fila:entrega | — |
| TR-T021 | en | troca_devolucao (1.00) | 0.020 | 0.020 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:troca_devolucao | — |
| TR-T021 | pt | troca_devolucao (1.00) | 0.020 | 0.020 | 0.020 | 0.00 (0.99) | 0.01 baixa | fila:troca_devolucao | — |
| TR-T021 | pt+perg_pt | troca_devolucao (1.00) | 0.020 | 0.020 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:troca_devolucao | — |
| TR-T022 | en | troca_devolucao (1.00) | 0.980 | 0.020 | 0.030 | 0.22 (0.67) | 0.20 baixa | fila:troca_devolucao | — |
| TR-T022 | pt | troca_devolucao (1.00) | 0.980 | 0.020 | 0.020 | 0.04 (0.93) | 0.16 baixa | fila:troca_devolucao | — |
| TR-T022 | pt+perg_pt | troca_devolucao (1.00) | 0.980 | 0.030 | 0.030 | 0.05 (0.92) | 0.17 baixa | fila:troca_devolucao | — |
| TR-T023 | en | troca_devolucao (1.00) | 0.070 | 0.980 | 0.030 | 1.40 (0.40) | 0.45 media | humano | frustracao |
| TR-T023 | pt | troca_devolucao (0.99) | 0.080 | 0.980 | 0.040 | 1.53 (0.29) | 0.48 media | humano | — |
| TR-T023 | pt+perg_pt | troca_devolucao (1.00) | 0.100 | 0.960 | 0.050 | 1.60 (0.41) | 0.49 media | humano | — |
| TR-T024 | en | troca_devolucao (1.00) | 0.470 | 0.050 | 0.030 | 1.00 (1.00) | 0.29 baixa | humano | — |
| TR-T024 | pt | troca_devolucao (1.00) | 0.810 | 0.040 | 0.020 | 1.00 (1.00) | 0.33 media | fila:troca_devolucao | pede_reembolso |
| TR-T024 | pt+perg_pt | troca_devolucao (1.00) | 0.730 | 0.040 | 0.030 | 1.00 (1.00) | 0.32 media | humano | pede_reembolso |
| TR-T025 | en | troca_devolucao (0.99) | 0.980 | 0.030 | 0.030 | 0.22 (0.66) | 0.20 baixa | fila:troca_devolucao | — |
| TR-T025 | pt | troca_devolucao (0.98) | 0.980 | 0.020 | 0.030 | 0.11 (0.84) | 0.18 baixa | fila:troca_devolucao | — |
| TR-T025 | pt+perg_pt | troca_devolucao (0.96) | 0.980 | 0.030 | 0.040 | 0.16 (0.76) | 0.20 baixa | fila:troca_devolucao | — |
| TR-T026 | en | troca_devolucao (0.93) | 0.070 | 0.050 | 0.950 | 0.54 (0.31) | 0.41 media | fila:troca_devolucao | frustracao |
| TR-T026 | pt | troca_devolucao (0.96) | 0.120 | 0.050 | 0.970 | 0.57 (0.36) | 0.43 media | fila:troca_devolucao | frustracao |
| TR-T026 | pt+perg_pt | troca_devolucao (0.99) | 0.130 | 0.060 | 0.970 | 0.81 (0.71) | 0.48 media | fila:troca_devolucao | frustracao |
| TR-T027 | en | troca_devolucao (1.00) | 0.020 | 0.040 | 0.030 | 0.03 (0.96) | 0.02 baixa | fila:troca_devolucao | — |
| TR-T027 | pt | troca_devolucao (0.99) | 0.020 | 0.030 | 0.020 | 0.02 (0.97) | 0.02 baixa | fila:troca_devolucao | — |
| TR-T027 | pt+perg_pt | troca_devolucao (0.97) | 0.020 | 0.030 | 0.030 | 0.04 (0.95) | 0.02 baixa | fila:troca_devolucao | — |
| TR-T028 | en | troca_devolucao (0.99) | 0.960 | 0.910 | 0.050 | 0.13 (0.80) | 0.32 media | humano | — |
| TR-T028 | pt | troca_devolucao (0.94) | 0.970 | 0.960 | 0.060 | 0.26 (0.61) | 0.36 media | humano | — |
| TR-T028 | pt+perg_pt | troca_devolucao (0.84) | 0.970 | 0.970 | 0.070 | 0.41 (0.39) | 0.39 media | humano | — |
| TR-T029 | en | troca_devolucao (1.00) | 0.070 | 0.030 | 0.020 | 0.03 (0.96) | 0.03 baixa | fila:troca_devolucao | — |
| TR-T029 | pt | troca_devolucao (1.00) | 0.120 | 0.030 | 0.020 | 0.01 (0.98) | 0.03 baixa | fila:troca_devolucao | — |
| TR-T029 | pt+perg_pt | troca_devolucao (1.00) | 0.110 | 0.030 | 0.020 | 0.02 (0.98) | 0.03 baixa | fila:troca_devolucao | — |
| TR-T030 | en | troca_devolucao (0.98) | 0.980 | 0.040 | 0.050 | 1.97 (0.95) | 0.56 media | fila:troca_devolucao | — |
| TR-T030 | pt | troca_devolucao (0.95) | 0.980 | 0.030 | 0.060 | 1.99 (0.98) | 0.57 media | fila:troca_devolucao | — |
| TR-T030 | pt+perg_pt | troca_devolucao (0.94) | 0.980 | 0.030 | 0.090 | 1.98 (0.98) | 0.57 media | fila:troca_devolucao | — |
| TR-T031 | en | conta_acesso (1.00) | 0.010 | 0.030 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:conta_acesso | — |
| TR-T031 | pt | conta_acesso (1.00) | 0.010 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:conta_acesso | — |
| TR-T031 | pt+perg_pt | conta_acesso (1.00) | 0.010 | 0.020 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:conta_acesso | — |
| TR-T032 | en | conta_acesso (1.00) | 0.020 | 0.030 | 0.020 | 0.01 (0.99) | 0.02 baixa | fila:conta_acesso | — |
| TR-T032 | pt | conta_acesso (1.00) | 0.020 | 0.030 | 0.020 | 0.07 (0.90) | 0.03 baixa | fila:conta_acesso | — |
| TR-T032 | pt+perg_pt | conta_acesso (0.97) | 0.020 | 0.020 | 0.030 | 0.05 (0.93) | 0.03 baixa | fila:conta_acesso | — |
| TR-T033 | en | conta_acesso (1.00) | 0.020 | 0.980 | 0.020 | 1.00 (1.00) | 0.36 media | humano | — |
| TR-T033 | pt | conta_acesso (1.00) | 0.010 | 0.980 | 0.020 | 1.00 (1.00) | 0.35 media | humano | — |
| TR-T033 | pt+perg_pt | conta_acesso (1.00) | 0.010 | 0.970 | 0.030 | 1.00 (1.00) | 0.36 media | humano | — |
| TR-T034 | en | conta_acesso (1.00) | 0.010 | 0.960 | 0.020 | 0.00 (0.99) | 0.15 baixa | humano | — |
| TR-T034 | pt | conta_acesso (1.00) | 0.010 | 0.970 | 0.020 | 0.01 (0.98) | 0.15 baixa | humano | — |
| TR-T034 | pt+perg_pt | conta_acesso (1.00) | 0.010 | 0.970 | 0.020 | 0.01 (0.98) | 0.15 baixa | humano | — |
| TR-T035 | en | conta_acesso (0.92) | 0.110 | 0.030 | 0.970 | 0.27 (0.60) | 0.37 media | fila:conta_acesso | — |
| TR-T035 | pt | conta_acesso (0.91) | 0.100 | 0.030 | 0.980 | 0.31 (0.53) | 0.38 media | fila:conta_acesso | — |
| TR-T035 | pt+perg_pt | conta_acesso (0.93) | 0.080 | 0.030 | 0.960 | 0.66 (0.47) | 0.44 media | fila:conta_acesso | frustracao |
| TR-T036 | en | pagamento (0.55) +conta_acesso | 0.960 | 0.910 | 0.170 | 2.00 (1.00) | 0.73 alta | humano | setor |
| TR-T036 | pt | conta_acesso (0.39) +troca_devolucao +pagamento | 0.910 | 0.950 | 0.210 | 2.00 (1.00) | 0.74 alta | humano | — |
| TR-T036 | pt+perg_pt | pagamento (0.46) +troca_devolucao | 0.890 | 0.900 | 0.180 | 2.00 (1.00) | 0.72 alta | humano | setor |
| TR-T037 | en | conta_acesso (0.92) | 0.010 | 0.020 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:conta_acesso | — |
| TR-T037 | pt | conta_acesso (0.91) | 0.010 | 0.020 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:conta_acesso | — |
| TR-T037 | pt+perg_pt | conta_acesso (0.91) | 0.010 | 0.020 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:conta_acesso | — |
| TR-T038 | en | conta_acesso (1.00) | 0.020 | 0.040 | 0.020 | 0.28 (0.58) | 0.07 baixa | fila:conta_acesso | — |
| TR-T038 | pt | conta_acesso (0.96) | 0.040 | 0.070 | 0.030 | 0.51 (0.23) | 0.13 baixa | fila:conta_acesso | frustracao |
| TR-T038 | pt+perg_pt | conta_acesso (0.86) | 0.040 | 0.080 | 0.040 | 0.76 (0.43) | 0.18 baixa | fila:conta_acesso | frustracao |
| TR-T039 | en | conta_acesso (1.00) | 0.020 | 0.030 | 0.040 | 0.12 (0.82) | 0.04 baixa | fila:conta_acesso | — |
| TR-T039 | pt | conta_acesso (1.00) | 0.020 | 0.020 | 0.040 | 0.21 (0.68) | 0.06 baixa | fila:conta_acesso | — |
| TR-T039 | pt+perg_pt | conta_acesso (1.00) | 0.010 | 0.030 | 0.040 | 0.22 (0.67) | 0.06 baixa | fila:conta_acesso | — |
| TR-T040 | en | conta_acesso (1.00) | 0.010 | 0.030 | 0.020 | 0.06 (0.91) | 0.02 baixa | fila:conta_acesso | — |
| TR-T040 | pt | conta_acesso (1.00) | 0.020 | 0.050 | 0.020 | 0.09 (0.86) | 0.03 baixa | fila:conta_acesso | — |
| TR-T040 | pt+perg_pt | conta_acesso (1.00) | 0.010 | 0.050 | 0.030 | 0.19 (0.72) | 0.06 baixa | fila:conta_acesso | — |
| TR-T041 | en | produto_duvida (1.00) | 0.010 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-T041 | pt | produto_duvida (1.00) | 0.010 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-T041 | pt+perg_pt | produto_duvida (1.00) | 0.010 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-T042 | en | produto_duvida (1.00) | 0.020 | 0.370 | 0.020 | 0.00 (1.00) | 0.06 baixa | humano | quer_humano |
| TR-T042 | pt | produto_duvida (1.00) | 0.020 | 0.630 | 0.020 | 0.00 (1.00) | 0.10 baixa | humano | — |
| TR-T042 | pt+perg_pt | produto_duvida (1.00) | 0.020 | 0.440 | 0.030 | 0.00 (1.00) | 0.08 baixa | humano | quer_humano |
| TR-T043 | en | produto_duvida (1.00) | 0.010 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-T043 | pt | produto_duvida (1.00) | 0.010 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-T043 | pt+perg_pt | produto_duvida (1.00) | 0.010 | 0.020 | 0.020 | 0.00 (1.00) | 0.01 baixa | fila:produto_duvida | — |
| TR-T044 | en | produto_duvida (1.00) | 0.010 | 0.020 | 0.020 | 1.00 (1.00) | 0.21 baixa | fila:produto_duvida | — |
| TR-T044 | pt | produto_duvida (1.00) | 0.010 | 0.030 | 0.020 | 1.00 (1.00) | 0.21 baixa | fila:produto_duvida | — |
| TR-T044 | pt+perg_pt | produto_duvida (1.00) | 0.010 | 0.030 | 0.020 | 1.00 (1.00) | 0.21 baixa | fila:produto_duvida | — |
| TR-T045 | en | produto_duvida (1.00) | 0.010 | 0.020 | 0.010 | 0.09 (0.87) | 0.03 baixa | fila:produto_duvida | — |
| TR-T045 | pt | produto_duvida (1.00) | 0.010 | 0.020 | 0.010 | 0.08 (0.87) | 0.02 baixa | fila:produto_duvida | — |
| TR-T045 | pt+perg_pt | produto_duvida (1.00) | 0.020 | 0.020 | 0.020 | 0.08 (0.88) | 0.03 baixa | fila:produto_duvida | — |
| TR-T046 | en | produto_duvida (0.99) | 0.040 | 0.030 | 0.920 | 0.12 (0.82) | 0.31 media | fila:produto_duvida | — |
| TR-T046 | pt | produto_duvida (0.99) | 0.040 | 0.030 | 0.890 | 0.13 (0.81) | 0.30 media | fila:produto_duvida | — |
| TR-T046 | pt+perg_pt | produto_duvida (0.92) | 0.040 | 0.040 | 0.890 | 0.18 (0.72) | 0.32 media | fila:produto_duvida | — |
| TR-T047 | en | produto_duvida (1.00) | 0.030 | 0.640 | 0.030 | 2.00 (1.00) | 0.51 media | humano | — |
| TR-T047 | pt | produto_duvida (0.99) | 0.030 | 0.890 | 0.030 | 2.00 (1.00) | 0.55 media | humano | — |
| TR-T047 | pt+perg_pt | produto_duvida (0.97) | 0.030 | 0.820 | 0.040 | 2.00 (1.00) | 0.54 media | humano | — |
| TR-T048 | en | produto_duvida (1.00) | 0.020 | 0.030 | 0.010 | 0.10 (0.85) | 0.03 baixa | fila:produto_duvida | — |
| TR-T048 | pt | produto_duvida (0.98) | 0.020 | 0.030 | 0.020 | 0.05 (0.92) | 0.02 baixa | fila:produto_duvida | — |
| TR-T048 | pt+perg_pt | produto_duvida (0.97) | 0.030 | 0.030 | 0.020 | 0.04 (0.94) | 0.02 baixa | fila:produto_duvida | — |
| TR-T049 | en | produto_duvida (1.00) | 0.030 | 0.020 | 0.030 | 0.91 (0.86) | 0.20 baixa | fila:produto_duvida | frustracao |
| TR-T049 | pt | produto_duvida (1.00) | 0.030 | 0.030 | 0.020 | 0.83 (0.74) | 0.18 baixa | fila:produto_duvida | frustracao |
| TR-T049 | pt+perg_pt | produto_duvida (1.00) | 0.050 | 0.030 | 0.030 | 0.67 (0.49) | 0.15 baixa | fila:produto_duvida | frustracao |
| TR-T050 | en | produto_duvida (1.00) | 0.020 | 0.030 | 0.020 | 1.00 (1.00) | 0.21 baixa | fila:produto_duvida | — |
| TR-T050 | pt | produto_duvida (1.00) | 0.020 | 0.040 | 0.020 | 1.00 (1.00) | 0.21 baixa | fila:produto_duvida | — |
| TR-T050 | pt+perg_pt | produto_duvida (1.00) | 0.020 | 0.040 | 0.030 | 1.00 (1.00) | 0.22 baixa | fila:produto_duvida | — |
| TR-T051 | en | outro (1.00) | 0.010 | 0.020 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:outro | — |
| TR-T051 | pt | outro (1.00) | 0.010 | 0.010 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:outro | — |
| TR-T051 | pt+perg_pt | outro (0.99) | 0.010 | 0.010 | 0.010 | 0.00 (1.00) | 0.01 baixa | fila:outro | — |
| TR-T052 | en | outro (1.00) | 0.010 | 0.940 | 0.010 | 0.00 (1.00) | 0.15 baixa | humano | — |
| TR-T052 | pt | outro (1.00) | 0.010 | 0.860 | 0.010 | 0.00 (1.00) | 0.13 baixa | humano | — |
| TR-T052 | pt+perg_pt | outro (1.00) | 0.010 | 0.850 | 0.010 | 0.00 (1.00) | 0.13 baixa | humano | — |
| TR-T053 | en | outro (0.94) | 0.020 | 0.030 | 0.010 | 0.07 (0.90) | 0.02 baixa | fila:outro | — |
| TR-T053 | pt | outro (0.95) | 0.020 | 0.030 | 0.010 | 0.05 (0.93) | 0.02 baixa | fila:outro | — |
| TR-T053 | pt+perg_pt | outro (0.91) | 0.010 | 0.040 | 0.020 | 0.05 (0.93) | 0.02 baixa | fila:outro | — |
| TR-T054 | en | outro (1.00) | 0.010 | 0.030 | 0.010 | 0.09 (0.86) | 0.03 baixa | fila:outro | — |
| TR-T054 | pt | outro (1.00) | 0.010 | 0.030 | 0.020 | 0.16 (0.75) | 0.04 baixa | fila:outro | — |
| TR-T054 | pt+perg_pt | outro (0.99) | 0.010 | 0.040 | 0.020 | 0.16 (0.76) | 0.05 baixa | fila:outro | — |
| TR-T055 | en | outro (0.98) | 0.020 | 0.090 | 0.030 | 1.00 (1.00) | 0.23 baixa | fila:outro | — |
| TR-T055 | pt | outro (0.99) | 0.020 | 0.070 | 0.030 | 1.00 (1.00) | 0.22 baixa | fila:outro | — |
| TR-T055 | pt+perg_pt | outro (0.92) | 0.020 | 0.090 | 0.040 | 1.02 (0.96) | 0.23 baixa | fila:outro | — |
| TR-T056 | en | outro (1.00) | 0.010 | 0.870 | 0.010 | 0.00 (1.00) | 0.14 baixa | humano | — |
| TR-T056 | pt | outro (1.00) | 0.010 | 0.900 | 0.010 | 0.00 (1.00) | 0.14 baixa | humano | — |
| TR-T056 | pt+perg_pt | outro (1.00) | 0.010 | 0.790 | 0.010 | 0.00 (1.00) | 0.12 baixa | humano | — |
| TR-T057 | en | None (0.98) | 0.270 | 0.050 | 0.030 | 0.16 (0.76) | 0.09 baixa | humano | — |
| TR-T057 | pt | None (0.97) | 0.150 | 0.040 | 0.020 | 0.07 (0.89) | 0.05 baixa | humano | — |
| TR-T057 | pt+perg_pt | None (0.93) | 0.170 | 0.050 | 0.030 | 0.05 (0.92) | 0.05 baixa | humano | — |
| TR-T058 | en | pagamento (0.86) +conta_acesso | 0.370 | 0.030 | 0.020 | 0.12 (0.83) | 0.09 baixa | humano | — |
| TR-T058 | pt | pagamento (0.93) +conta_acesso | 0.360 | 0.030 | 0.020 | 0.16 (0.77) | 0.10 baixa | humano | — |
| TR-T058 | pt+perg_pt | pagamento (0.96) +conta_acesso | 0.310 | 0.030 | 0.030 | 0.23 (0.66) | 0.11 baixa | humano | — |
| TR-T059 | en | None (0.51) | 0.080 | 0.970 | 0.030 | 1.38 (0.42) | 0.44 media | humano | — |
| TR-T059 | pt | None (0.54) | 0.070 | 0.960 | 0.030 | 1.22 (0.67) | 0.41 media | humano | — |
| TR-T059 | pt+perg_pt | None (0.85) | 0.080 | 0.960 | 0.040 | 1.29 (0.57) | 0.43 media | humano | — |
| TR-T060 | en | troca_devolucao (0.98) | 0.970 | 0.880 | 0.040 | 0.06 (0.91) | 0.30 media | humano | — |
| TR-T060 | pt | troca_devolucao (0.94) +conta_acesso | 0.970 | 0.890 | 0.040 | 0.18 (0.73) | 0.33 media | humano | — |
| TR-T060 | pt+perg_pt | troca_devolucao (0.97) +conta_acesso | 0.970 | 0.870 | 0.060 | 0.21 (0.69) | 0.34 media | humano | — |
