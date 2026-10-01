# Português × inglês no Jev — resultados

Conjunto `jev-pt-en-paired-40-v1` (Codex, sintético): 40 pares, pergunta idêntica em inglês; só a mensagem muda de idioma. 2 repetições. Modelo: ['jev-1.13.0'].

## Noul
- Brier pt 0.001 · en 0.001 (menor é melhor) — n=28 (casos×repetições com gabarito)
- Acerto no corte ilustrativo 0.5: pt 100.0% · en 100.0%
- Diferença média |p_pt − p_en| no mesmo caso: 0.017

## Choice
- Acerto pt 90.9% · en 90.9% — n=22
- Vencedor diferente entre idiomas: 0.0%
- Confiança média pt 0.90 · en 0.93

## Score
- Erro absoluto médio ao nível de referência: pt 0.00 · en 0.01 — n=22
- Nível arredondado = referência: pt 100.0% · en 100.0%
- Diferença média |score_pt − score_en|: 0.03

## Estabilidade (mesma requisição, 2 chamadas)
- Variação média entre repetições (|Δ| em Noul/Score; troca de vencedor em Choice): 0.002

## Casos para olhar (erro em algum idioma ou divergência pt × en)

| caso | tipo | gabarito | pt | en | tags |
|---|---|---|---|---|---|
| N14 | noul | None | 0.32 | 0.11 | ambiguous, missing_referent |
| N15 | noul | None | 0.66 | 0.64 | ambiguous, missing_context |
| C11 | choice | None | other | other | multiple_intents, ambiguous |
| C12 | choice | other | billing | billing | adversarial_instruction, no_service_request |
| S12 | score | None | 1.3 | 1.03 | ambiguous, insufficient_impact |

## Custo e latência
- 160 requisições (160 do cache) · p50 270 ms · p95 868 ms · 72432 tokens · US$ 0.003042

Limites: dados sintéticos escritos por um LLM; tradução sem revisão independente; mede só o idioma da mensagem (perguntas em português são outro experimento).
