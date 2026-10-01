# Protocolo congelado — R4 (B2W-Reviews01) e R5 (HateBR) — 2026-09-30

Autoria: Claude (coordenador), com a crítica P8 do Codex (chat.txt, 2026-09-30) incorporada. Congelado
ANTES de qualquer chamada à API. Mudança depois disto = nova versão com data, e o teste antigo vira ajuste.

## Fontes e licenças (conferidas)
- **HateBR** — https://github.com/franciellevargas/HateBR — CC BY-NC 4.0. 7.000 comentários do Instagram
  (6 contas de políticos), `label_final` (0/1, balanceado 3.500/3.500) + votos `anotator1..3` + `links_post`.
- **B2W-Reviews01** — https://github.com/americanas-tech/b2w-reviews01 (B2W Digital) — CC BY-NC-SA 4.0.
  132.373 avaliações com `overall_rating` (1–5) e `recommend_to_a_friend` (Yes/No; 18 vazios).
- Dados crus só em `.local/publicos/` (fora do Git). No repositório: só agregados, com crédito às fontes.

## Tarefas (o alvo ORIGINAL de cada conjunto — sem estender)
- **R5 HateBR — "o comentário é ofensivo?"** Noul com a definição do próprio conjunto (comentário
  ofensivo = linguagem que ataca/insulta/ridiculariza pessoa ou grupo; ver README do HateBR). Gold =
  `label_final`. NÃO estender para "bloquear", ilegalidade ou segurança.
- **R4a B2W — "recomendaria a um amigo?"** Noul. Gold = `recommend_to_a_friend` (Yes=1, No=0); vazio = excluído.
- **R4b B2W — nota geral 1–5.** Score de 5 níveis descritivos; a conversão Score→nota inteira (arredondar)
  é congelada no ajuste. Métricas ordinais (não igualdade de float).
- Entrada ao Jev = SÓ o texto que existiria no uso real: HateBR `comentario`; B2W `review_title` +
  `review_text`. Nunca estrelas, "recomendaria", produto, marca, categoria ou dados do avaliador como entrada.

## Amostragem e divisão (antes de afinar)
- Deduplicação exata (texto normalizado) e aproximada (mesmo texto após tirar pontuação/caixa); duplicatas
  ficam do mesmo lado.
- Grupos disjuntos entre ajuste e teste: HateBR por `links_post` (post); B2W por `product_id` (declarado:
  a alegação é generalizar para produto novo).
- Semente fixa; hashes das listas de IDs registrados.
- Tamanho (exploratório; não prova erro raro): por corpus, **100 ajuste + 300 teste**.
- Teste principal com a **prevalência natural** da população definida (B2W: ~73% recomendaria; HateBR:
  50/50 é a prevalência DO CONJUNTO, não do Instagram — dito no relatório). Conjunto difícil deliberado,
  se houver, relatado à parte, nunca misturado.
- Antes da API: publicar elegíveis, excluídos, duplicatas, classes e custo máximo estimado.

## Estratos que o dado permite
- HateBR: unânime (3/3) × disputado (2/1), a partir dos votos individuais. A concordância entre anotadores é
  referência de ambiguidade, **não teto** de acurácia contra o consenso.

## Baselines (mesmas entradas, mesmo split)
- Maioria/prevalência.
- Regras simples: léxico de ofensa (HateBR); léxico de polaridade (B2W) — construídos só com o ajuste.
- TF-IDF + regressão logística treinada no AJUSTE (100) — comparação honesta com Jev zero-shot; se
  treinado com mais dados (fora do teste), declarado como outro regime.
- LLM real: só se houver autorização/chave; senão, não entra (nada simulado como qualidade).

## Métricas
- Booleanos: precisão/recall/F1 por classe, macro-F1, matriz de confusão, PR-AUC com prevalência
  informada (Noul como escore), Brier. Limiar escolhido no AJUSTE pelo custo do erro; faixa de dúvida
  relatada como cobertura + qualidade nos decididos + resultado no conjunto todo.
- Nota (R4b): MAE, acerto exato, acerto ±1, matriz de confusão 5×5.
- Separar abstenção, resposta inválida e erro operacional.
- Incerteza: intervalo por bootstrap por grupo (post / produto).
- Custo: requisições, tokens, US$ (0,042/M), latência p50/p95, versão do modelo (`jev-1.13.0` fixada).

## Relatório
N, split, hashes do corpus e das listas, modelo, perguntas e limiares congelados, entradas fornecidas,
custo/latência, erros com intervalo, comparação pareada com baselines, divergências amostradas e auditadas
(exemplos de texto só localmente; no repositório só agregados). Nunca misturar R4 com R5 numa média.
