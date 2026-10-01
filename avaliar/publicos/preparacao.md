# Preparação R4/R5 — contagens e custo máximo (gerado por `preparar.py`, ANTES da API)

Semente `20260930` · protocolo sha256 `b1e4c959f62796a3…` · custo máximo estimado total **US$ 0.0818**. Só agregados, IDs e hashes; o texto licenciado fica em `.local/publicos/divisoes/`.

## hatebr — `HateBR.csv` (sha256 `0586a15eea2d9e77…`)

- Elegíveis **7000**; excluídos nenhum; classe positiva = ofensivo (label_final=1), prevalência 0.5 (3500).
- Estratos na população: {'unanime': 5684, 'disputado': 1316}; gold diferente da maioria dos votos: 0.
- Duplicatas: exatas 0 itens em 0 grupos; aproximadas 0 itens em 0 grupos (0 grupos com gabarito divergente); textos únicos 7000.
- Grupos: 78 (39 no lado do ajuste, 39 no do teste); itens por lado {'ajuste': 3314, 'teste': 3686}.

| amostra | n | grupos | positivos | prevalência | extra | sha256 dos IDs |
|---|---|---|---|---|---|---|
| ajuste | 100 | 24 | 40 | 0.4 | {'disputado': 19, 'unanime': 81} | `55214d837fb18070…` |
| teste | 300 | 34 | 151 | 0.503 | {'unanime': 253, 'disputado': 47} | `9fe130a439d7a86c…` |
| treino_amplo (outro regime do baseline) | 3314 | | | | | `84eeed462796cf28…` |

Custo máximo: 1320 requisições × ~726 tokens = 958004 tokens → **US$ 0.0402** (até 8 versões no ajuste + teste 1×, +20% de repetição).

## b2w — `B2W-Reviews01.csv` (sha256 `821fb0bf9f7230b0…`)

- Elegíveis **132283**; excluídos {'título e texto vazios': 72, 'recommend_to_a_friend vazio/ inválido': 18}; classe positiva = recomendaria (Yes), prevalência 0.7282 (96335).
- Notas na população: {'1': 27336, '2': 8383, '3': 16303, '4': 32336, '5': 47925}.
- Duplicatas: exatas 4553 itens em 1807 grupos; aproximadas 5171 itens em 1903 grupos (70 grupos com gabarito divergente); textos únicos 129015.
- Grupos: 47965 (23982 no lado do ajuste, 23983 no do teste); itens por lado {'ajuste': 67417, 'teste': 64866}.

| amostra | n | grupos | positivos | prevalência | extra | sha256 dos IDs |
|---|---|---|---|---|---|---|
| ajuste | 100 | 96 | 77 | 0.77 | {'1': 16, '2': 6, '3': 19, '4': 30, '5': 29} | `6f7be3cc7d7f67a3…` |
| teste | 300 | 280 | 218 | 0.727 | {'1': 67, '2': 21, '3': 39, '4': 67, '5': 106} | `289b6a9118786222…` |
| treino_amplo (outro regime do baseline) | 67339 | | | | | `17430dd6fac4c440…` |

Custo máximo: 1320 requisições × ~751 tokens = 991322 tokens → **US$ 0.0416** (até 8 versões no ajuste + teste 1×, +20% de repetição).
