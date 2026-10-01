# R4/R5 — Jev em texto real em português com gabarito humano (resultados)

**Fontes (crédito e licença):** HateBR — Vargas, Carvalho, Rodrigues de Góes, Pardo e Benevenuto, LREC 2022 (https://github.com/franciellevargas/HateBR), CC BY-NC 4.0. B2W-Reviews01 — **B2W Digital** (https://github.com/americanas-tech/b2w-reviews01), CC BY-NC-SA 4.0. Este arquivo tem só agregados, IDs e hashes; nenhum texto dos conjuntos. Gerado por `avaliar.py teste`.

Protocolo `PROTOCOLO.md` (sha256 `b1e4c959f62796a3…`). Modelo pedido `jev-1.13.0`; respondido ['jev-1.13.0'] / ['jev-1.13.0']. Semente 20260930; bootstrap 2000× por grupo (post no HateBR, produto no B2W), IC 95% percentil.

## Congelamento (antes do teste)

- Congelado em 2026-09-30T23:20:35+00:00; teste executado em 2026-09-30T23:25:52+00:00 (uma vez; relatórios seguintes saem do cache).
- `perguntas.py` sha256 `cc8188e3be9475a4c3575b5fe77a77caa1b871b07fc364c7670857649bc33057` · `baselines.py` `6b6088bf479db483d9c02cb3c50d9172e33a77df5ec20c0ccb463ce579c61293` · `preparacao.json` `b90e921809aa3614e6f4af1bb0de8a40edde08b44642512afe8b1d89eefe54da`.
- Perguntas usadas: {'R5': ['hatebr', 'ofensivo_v2'], 'R4a': ['b2w', 'recomenda'], 'R4b': ['b2w', 'nota_v2']}; limiar único {'R5': 0.5, 'R4a': 0.5} (custo simétrico FP = FN = 1); faixa de dúvida {'R5': [0.2, 0.8], 'R4a': [0.2, 0.8]}; nota = arredondar(score) + 1.
- Entradas ao Jev: HateBR `{comment}`; B2W `{review_title, review_text}`. Nada de estrelas, recomendação, produto, marca, categoria ou avaliador. Perguntas em inglês (texto integral em `perguntas.py`).

## Amostras

| corpus | parte | n | grupos | prevalência (classe positiva) | extra | sha256 IDs |
|---|---|---|---|---|---|---|
| hatebr (arquivo `0586a15eea2d…`) | ajuste | 100 | 24 | 0.4 (ofensivo (label_final=1)) | {'disputado': 19, 'unanime': 81} | `55214d837fb18070…` |
| hatebr (arquivo `0586a15eea2d…`) | teste | 300 | 34 | 0.503 (ofensivo (label_final=1)) | {'unanime': 253, 'disputado': 47} | `9fe130a439d7a86c…` |
| b2w (arquivo `821fb0bf9f72…`) | ajuste | 100 | 96 | 0.77 (recomendaria (Yes)) | {'1': 16, '2': 6, '3': 19, '4': 30, '5': 29} | `6f7be3cc7d7f67a3…` |
| b2w (arquivo `821fb0bf9f72…`) | teste | 300 | 280 | 0.727 (recomendaria (Yes)) | {'1': 67, '2': 21, '3': 39, '4': 67, '5': 106} | `289b6a9118786222…` |

Elegíveis, exclusões e duplicatas: `preparacao.md` (publicado antes da primeira chamada). A prevalência 50/50 do HateBR é a do CONJUNTO (balanceado pelos autores), não a do Instagram.

## R5 · HateBR — o comentário é ofensivo? (positivo = ofensivo)

Status das respostas: {'ok': 300, 'invalida': 0, 'erro_operacional': 0} (inválida e erro operacional ficam fora e são contados aqui). Prevalência positiva no teste 0.503.

| sistema | regime | acerto | macro-F1 [IC] | P1 | R1 | F1₁ | P0 | R0 | F1₀ | PR-AUC₁ | PR-AUC₀ | Brier | matriz tp/fp/fn/tn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Jev** | zero-shot, limiar do ajuste | 0.937 | 0.937 [0.906; 0.962] | 0.940 | 0.934 | 0.937 | 0.933 | 0.940 | 0.936 | 0.981 | 0.977 | 0.055 | 141/9/10/140 |
| maioria | ajuste-100 | 0.497 | 0.332 [0.260; 0.398] | 0.000 | 0.000 | 0.000 | 0.497 | 1.000 | 0.664 | 0.503 | 0.497 | 0.261 | 0/0/151/149 |
| lexico | ajuste-100 | 0.587 | 0.579 [0.502; 0.641] | 0.624 | 0.450 | 0.523 | 0.565 | 0.725 | 0.635 | 0.621 | 0.598 | n/a | 68/41/83/108 |
| tfidf_lr | ajuste-100 | 0.503 | 0.346 [0.270; 0.419] | 1.000 | 0.013 | 0.026 | 0.500 | 1.000 | 0.667 | 0.748 | 0.785 | 0.241 | 2/0/149/149 |
| tfidf_lr_amplo | amplo-3314 | 0.800 | 0.798 [0.733; 0.849] | 0.882 | 0.695 | 0.778 | 0.746 | 0.906 | 0.818 | 0.918 | 0.914 | 0.159 | 105/14/46/135 |

Jev: IC do acerto [0.909; 0.962]; PR-AUC₁ [0.957; 0.993]; PR-AUC₀ [0.951; 0.991]; Brier [0.040; 0.073]. PR-AUC de referência (aleatório) = prevalência da classe.

**Comparação pareada** (mesmos itens; Δ = Jev − baseline; IC por bootstrap pareado por grupo):

| baseline | regime | Δ macro-F1 [IC] | Jev certo / base errado | Jev errado / base certo |
|---|---|---|---|---|
| maioria | ajuste-100 | 0.605 [0.528; 0.675] | 141 | 9 |
| lexico | ajuste-100 | 0.357 [0.300; 0.423] | 117 | 12 |
| tfidf_lr | ajuste-100 | 0.590 [0.509; 0.663] | 139 | 9 |
| tfidf_lr_amplo | amplo-3314 | 0.139 [0.097; 0.186] | 52 | 11 |

**Faixa de dúvida** (não ≤ 0.2, sim ≥ 0.8, meio → humano): cobertura 0.810, acerto nos decididos 0.971 (7 erros), 57 à revisão; no conjunto todo (limiar único) acerto 0.937.

**Estratos** (votos individuais; concordância entre anotadores = referência de ambiguidade, não teto):

| estrato | n | ofensivos | Jev acerto [IC] | Jev macro-F1 | Jev Brier | Jev na faixa de dúvida | |noul − 0,5| médio | maioria acerto | lexico acerto | tfidf_lr acerto | tfidf_lr_amplo acerto |
|---|---|---|---|---|---|---|---|---|---|---|---|
| unanime | 253 | 114 | 0.957 [0.929; 0.977] | 0.956 | 0.037 | 0.150 | 0.403 | 0.549 | 0.585 | 0.557 | 0.842 |
| disputado | 47 | 37 | 0.830 [0.765; 0.917] | 0.776 | 0.152 | 0.404 | 0.309 | 0.213 | 0.596 | 0.213 | 0.574 |

Erros do Jev no teste (IDs): [541, 570, 1347, 1714, 1757, 1805, 1857, 2890, 3011, 3385, 3598, 3734, 4738, 4932, 5261, 5930, 6134, 6195, 6285]

**Auditoria das divergências** (amostra de 19 por semente; texto lido só localmente):

- Jev viu zombaria/sarcasmo que os anotadores não marcaram — leitura defensável: 7 (IDs 3598, 4738, 4932, 5261, 5930, 6134, 6285)
- gabarito = ofensa implícita (insinuação/ironia) em item DISPUTADO — discutível: 6 (IDs 570, 1347, 1714, 1757, 1805, 1857)
- Jev perdeu ataque sem palavra pejorativa (apologia/incitação política) — custo do estreitamento da v2: 2 (IDs 2890, 3011)
- Jev perdeu termo pejorativo de gíria/neologismo, logo abaixo do limiar (0,46–0,47): 2 (IDs 541, 3385)
- Jev errou: palavra potencialmente pejorativa em uso afetuoso ou rótulo político neutro: 2 (IDs 3734, 6195)

## R4a · B2W — recomendaria a um amigo? (positivo = Yes)

Status das respostas: {'ok': 300, 'invalida': 0, 'erro_operacional': 0} (inválida e erro operacional ficam fora e são contados aqui). Prevalência positiva no teste 0.727.

| sistema | regime | acerto | macro-F1 [IC] | P1 | R1 | F1₁ | P0 | R0 | F1₀ | PR-AUC₁ | PR-AUC₀ | Brier | matriz tp/fp/fn/tn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Jev** | zero-shot, limiar do ajuste | 0.913 | 0.899 [0.859; 0.932] | 0.990 | 0.890 | 0.937 | 0.769 | 0.976 | 0.860 | 0.994 | 0.925 | 0.065 | 194/2/24/80 |
| maioria | ajuste-100 | 0.727 | 0.421 [0.402; 0.438] | 0.727 | 1.000 | 0.842 | 0.000 | 0.000 | 0.000 | 0.727 | 0.273 | 0.201 | 218/82/0/0 |
| lexico | ajuste-100 | 0.777 | 0.683 [0.619; 0.745] | 0.808 | 0.908 | 0.855 | 0.636 | 0.427 | 0.511 | 0.927 | 0.601 | n/a | 198/47/20/35 |
| tfidf_lr | ajuste-100 | 0.727 | 0.421 [0.402; 0.438] | 0.727 | 1.000 | 0.842 | 0.000 | 0.000 | 0.000 | 0.967 | 0.779 | 0.174 | 218/82/0/0 |
| tfidf_lr_amplo | amplo-67339 | 0.910 | 0.886 [0.843; 0.925] | 0.936 | 0.940 | 0.938 | 0.840 | 0.829 | 0.834 | 0.989 | 0.910 | 0.064 | 205/14/13/68 |

Jev: IC do acerto [0.880; 0.943]; PR-AUC₁ [0.988; 0.997]; PR-AUC₀ [0.854; 0.981]; Brier [0.047; 0.085]. PR-AUC de referência (aleatório) = prevalência da classe.

**Comparação pareada** (mesmos itens; Δ = Jev − baseline; IC por bootstrap pareado por grupo):

| baseline | regime | Δ macro-F1 [IC] | Jev certo / base errado | Jev errado / base certo |
|---|---|---|---|---|
| maioria | ajuste-100 | 0.478 [0.425; 0.523] | 80 | 24 |
| lexico | ajuste-100 | 0.216 [0.144; 0.287] | 60 | 19 |
| tfidf_lr | ajuste-100 | 0.478 [0.425; 0.523] | 80 | 24 |
| tfidf_lr_amplo | amplo-67339 | 0.012 [-0.029; 0.055] | 14 | 13 |

**Faixa de dúvida** (não ≤ 0.2, sim ≥ 0.8, meio → humano): cobertura 0.853, acerto nos decididos 0.961 (10 erros), 44 à revisão; no conjunto todo (limiar único) acerto 0.913.

Erros do Jev no teste (IDs): [297, 14355, 24087, 29482, 34246, 35142, 36724, 40764, 52041, 54428, 63930, 67683, 68336, 75752, 78375, 79156, 81744, 85868, 88370, 103438, 104876, 106428, 113207, 113384, 119291, 127004]

**Auditoria das divergências** (amostra de 20 por semente; texto lido só localmente):

- Jev errou: ressalva ou defeito leve lido como não recomenda (o critério dizia 'mesmo com pequenas queixas'): 8 (IDs 297, 34246, 68336, 79156, 104876, 113384, 119291, 78375)
- texto só queixa da loja/entrega/frete/cupom/nota fiscal, gabarito Yes — texto não informa sobre o produto: 5 (IDs 52041, 54428, 67683, 85868, 106428)
- gabarito contradiz o texto (nota 1 ou recusa explícita, com recomendaria = Yes): 4 (IDs 29482, 81744, 127004, 88370)
- Jev disse recomenda em texto misto; gabarito No — fronteira real: 2 (IDs 24087, 103438)
- texto sem opinião (só dúvida/pergunta): 1 (IDs 40764)

## R4b · B2W — nota geral 1–5 (Score de 5 situações → arredondar + 1)

Status: {'ok': 300, 'invalida': 0, 'erro_operacional': 0}.

| sistema | regime | MAE [IC] | exato | ±1 | Δ MAE Jev − base [IC] |
|---|---|---|---|---|---|
| **Jev** | zero-shot | 0.430 [0.359; 0.502] | 0.623 [0.566; 0.682] | 0.953 | |
| maioria | ajuste-100 | 1.293 [1.169; 1.418] | 0.223 | 0.707 | [-1.017; -0.711] |
| lexico | ajuste-100 | 1.143 [1.045; 1.247] | 0.227 | 0.737 | [-0.845; -0.581] |
| tfidf_lr | ajuste-100 | 1.337 [1.184; 1.492] | 0.320 | 0.673 | [-1.079; -0.740] |
| tfidf_lr_amplo | amplo-67339 | 0.497 [0.414; 0.584] | 0.617 | 0.927 | [-0.148; 0.020] |

Matriz 5×5 do Jev (linha = nota real 1..5, coluna = prevista 1..5):

| real \ prevista | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| 1 | 50 | 17 | 0 | 0 | 0 |
| 2 | 4 | 12 | 4 | 1 | 0 |
| 3 | 2 | 3 | 4 | 24 | 6 |
| 4 | 2 | 1 | 4 | 28 | 32 |
| 5 | 0 | 0 | 2 | 11 | 93 |

**Auditoria (erros de ≥ 2 níveis, amostra):** nota média com texto só de elogio — o texto não sustenta a nota: 6; nota alta com texto só de queixa da loja/entrega: 3; texto misto: Jev pesou o lado oposto ao da nota: 3; humor/ironia lido como satisfação média: 2

## Ajuste (100 por corpus) das perguntas congeladas — referência, não resultado

- R5: acerto 0.930, macro-F1 0.927, Brier 0.058, limiar pela regra 0.5.
- R4a: acerto 0.970, macro-F1 0.959, Brier 0.047, limiar pela regra 0.5.
- R4b: MAE 0.650, exato 0.460, ±1 0.920.

## Custo, latência, tokens

- Teste: 600 requisições, 311958 tokens de entrada, US$ 0.0131; latência p50 269 ms, p95 333 ms (medida na chamada real, 8 em paralelo); modelos ['jev-1.13.0'].
- Ajuste (todas as versões e variantes, inclusive as descartadas): 400 requisições, 258454 tokens, US$ 0.01086.
- Total gasto: US$ 0.02396 (teto publicado antes: US$ 0.0818). Preço US$ 0.042/M de entrada.

## O que isto NÃO mostra

- n = 300 por tarefa: exploratório; não prova taxa de erro rara. HateBR com 34 posts no teste: o IC por post é largo de propósito.
- HateBR 50/50 é prevalência do conjunto (balanceado), não do Instagram; precisão em tráfego real (ofensa rara) seria menor.
- Uma versão do modelo (`jev-1.13.0`), uma rodada; ruído entre chamadas idênticas medido em ~0,01 (máx. 0,15) — itens perto do limiar podem trocar de lado.
- Baseline LLM real não entrou (sem autorização para outro provedor). `tfidf_lr_amplo` é OUTRO regime (milhares de rótulos), não comparável ao zero-shot.
- Nunca misturar R4 com R5 numa média.
