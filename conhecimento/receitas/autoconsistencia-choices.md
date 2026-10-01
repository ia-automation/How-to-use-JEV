---
name: autoconsistencia-choices
description: Mede se 8 Choices de moderação repetem a mesma decisão em 15 repetições, Jev x 6 condições de LLM; com regra "uncertain se prob. máx < 0,60", Jev chega a 99,2% de concordância (74,2% automático) a 114 ms e US$ 0,000046 por chamada.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 4960–6032
estudado_em: 2026-09-30
---

# Autoconsistência: Choices (Self-consistency: choices)

## Problema
Um post de usuário na fronteira da política de moderação é avaliado por uma rubrica de 8 Choices. Cada rótulo é decisão de roteamento (remover ou deixar, escalar ou auto-resolver, qual fila). Se o rótulo oscila de uma execução para outra, o mesmo post vai para lugares diferentes sem motivo. A receita roda a rubrica 15 vezes por condição, plota todos os rótulos, e compara concordância entre repetições, variação de probabilidade, custo e latência. Mede repetibilidade, NÃO acurácia (o doc repete isso várias vezes).

## Como o Jev entra
- **state:** `{"uid": "<rubric_hash>:<sample_index>:<token_hex(4)>", "post": POST}`. O `POST` é um dict; o Jev recebe o dict direto, os LLMs recebem `json.dumps(POST)` no prompt. O `uid` é um valor único descartável por chamada (também vai no prompt dos LLMs), igual ao setup do cookbook noul; o doc admite que este arranjo não separa a sensibilidade ao campo irrelevante da variação de requisições idênticas.
- **O post (estado):** `post_id` P-88213; `author` {user_id u/4471, account_age_days 38, prior_strikes 1, followers 210}; `context` {surface "public reply", in_reply_to "another user defending a game patch", community r/gamedebates}; `content` {texto insultuoso com "Come say it to my face, invite's right here. Keep it up and I'll end your whole channel.", has_link True, link_domain discord.gg, language en}; `reports` {user_reports 4, report_reasons [harassment, spam, threat]}. Construído para ficar na fronteira.
- **perguntas:** 8, todas **Choice**, rótulos mutuamente exclusivos cada um com descrição curta (texto em inglês, literal):
  - `category` "What is the single most applicable content-policy category for this post?": None, Harass, Hate, Violence, Spam, Sexual.
  - `primary_risk` "What is the primary moderation risk that should drive triage for this post?": Harassment, Violence, LinkAbuse, AccountHistory, LowRisk.
  - `target` "Who or what is the content primarily directed at?": None, Person, Group, Platform.
  - `action` "What enforcement action should be taken on this post?": Allow, Warn, Remove, Strike, Escalate.
  - `queue` "Which single moderation queue should own this post?": Auto, General, Threat, Spam, TSLead.
  - `link_handling` "How should any external link or off-platform invite in the post be handled?": Allow, RmLink, Brigade, Escalate.
  - `review_path` "Who should make the final call on this post?": Auto, Human, Senior, Legal.
  - `severity` "What is the overall severity of this post?": None, Low, Medium, High.
- **chamadas:** 1 `system_one` por execução da rubrica, respondendo as 8 perguntas juntas. 15 execuções (`NUM_SAMPLES = 15`) por condição, sequenciais para o Jev (para a latência ser ida-e-volta limpa), num pool de 16 threads para os LLMs. Modelo pedido `jev-latest`, resolvido em `jev-1.13.0` nas 15 chamadas (`response.model` é guardado porque o alias pode mudar); amostrado em 2026-09-11 na API de produção; timeout do cliente 30 s.

### Condições comparadas (15 repetições cada, 9 condições = 135 chamadas)
| grupo | modelo | distribuição t=0 | distribuição padrão | single-pick t=0 |
|---|---|---|---|---|
| Não-reasoning | `claude-haiku-4-5` | sim | sim | sim |
| Não-reasoning | `gpt-5.4-mini` | sim | sim | sim |
| Reasoning | `gpt-5.5` (`reasoning_effort="high"`) | - | sim | - |
| Reasoning | `claude-opus-4-8` (`thinking: adaptive`, `max_tokens=4096`) | - | sim | - |
| Jev | `jev-latest` (`typesafe_choice`) | - | sim | - |

Coluna "padrão" = sem argumento de temperatura (reasoning models e Jev não têm temperatura). Nos LLMs, um prompt só com o post, as 8 perguntas com todos os rótulos, instrução de exclusividade ("pick the single most severe / most specific label") e um de dois formatos de resposta: `dist` (objeto JSON com probabilidades 0,00-1,00 somando 1 por rótulo) ou `single` (um rótulo por pergunta; a análise põe toda a massa nele, vetor one-hot sintético).

## O que o código faz com a resposta
- Rótulo = argmax das probabilidades; qualquer valor ausente/não numérico ou fora de [0,1] → `None` (falha de parsing conta contra a concordância; nunca se vira "pick" confiante).
- Decisão de aplicação: `MIN_CHOICE_PROBABILITY = 0.60` (ilustrativo): se `max(prob) >= 0,60` → rótulo (em exatamente 0,60 escolhe o rótulo); senão `"uncertain"` → revisão humana. Usa as PROBABILIDADES devolvidas, não o campo `confidence` da API; não adiciona chamadas.
- Concordância crua (`raw agree`): média sobre as 8 perguntas da fatia do rótulo plural (argmax) sobre 15. Concordância de política (`policy agree`): igual, mas `uncertain` conta como decisão.
- `automatic` = fatia de respostas que escolhem rótulo; `conflicts` = nº de perguntas com mais de um rótulo concreto entre as repetições (ignora abstenções).
- Desvio-padrão de probabilidade: por condição, std de cada probabilidade de rótulo entre as 15 repetições, média sobre todos os rótulos e perguntas; também o maior desvio individual e taxa de falha de parsing. Single-pick fica fora (não emite distribuições).
- Preços aplicados depois de ler o cache (mudar preço não exige nova amostra): LLM em US$/1M tokens (entrada, saída): haiku-4-5 1,00/5,00; gpt-5.4-mini 0,75/4,50; gpt-5.5 5,00/30,00; opus-4-8 5,00/25,00 ("prices + model ids as of 2026-07"). Jev `TYPESAFE_PRICE = (0.042, 0.00)` descrito no código como "Historical TypeSafe rate, as of 2026-08".

## Resultados medidos
**Custo e latência por chamada da rubrica (8 perguntas), média de 15:**

| condição | tempo/chamada | custo/chamada | x vel. Jev | x custo Jev |
|---|---|---|---|---|
| claude-haiku-4-5 t=0 | 3853 ms | $0,003498 | 33,8x | 76,1x |
| claude-haiku-4-5 t=default | 3860 ms | $0,003494 | 33,8x | 76,0x |
| claude-haiku-4-5 single-pick t=0 | 992 ms | $0,001527 | 8,7x | 33,2x |
| gpt-5.4-mini t=0 | 2293 ms | $0,002299 | 20,1x | 50,0x |
| gpt-5.4-mini t=default | 1986 ms | $0,002164 | 17,4x | 47,1x |
| gpt-5.4-mini single-pick t=0 | 826 ms | $0,000936 | 7,2x | 20,3x |
| gpt-5.5-reasoning | 12978 ms | $0,041255 | 113,7x | 897,4x |
| claude-opus-4-8-reasoning | 10376 ms | $0,028375 | 90,9x | 617,2x |
| typesafe_choice (jev-latest) | 114 ms | $0,000046 | 1,0x | 1,0x |

Os custos usam as suposições históricas de preço, "não são preços verificados de `jev-latest` nem faturamento atual".

**Desvio-padrão de probabilidade (mean / max / parse fail / x Jev):**
- haiku t=0: 0,0012 / 0,0221 / 0% / 0,12x
- haiku default: 0,0516 / 0,3150 / 1% / 5,29x
- gpt-5.4-mini t=0: 0,0312 / 0,0905 / 0% / 3,20x
- gpt-5.4-mini default: 0,0543 / 0,2303 / 0% / 5,56x
- gpt-5.5-reasoning: 0,0305 / 0,1047 / 0% / 3,12x
- claude-opus-4-8-reasoning: 0,0245 / 0,0693 / 0% / 2,52x
- typesafe_choice: 0,0098 / 0,0515 / 0% / 1,00x

**Concordância:**

| condição | raw agree | policy agree | uncertain | automatic | conflicts |
|---|---|---|---|---|---|
| haiku t=0 | 100,0% | 100,0% | 0,0% | 100,0% | 0 |
| haiku t=default | 87,5% | 86,7% | 0,8% | 98,3% | 2 |
| gpt-5.4-mini t=0 | 99,2% | 87,5% | 12,5% | 87,5% | 0 |
| gpt-5.4-mini default | 90,8% | 84,2% | 22,5% | 77,5% | 2 |
| gpt-5.5-reasoning | 90,0% | 93,3% | 30,8% | 69,2% | 1 |
| claude-opus-4-8-reasoning | 92,5% | 94,2% | 33,3% | 66,7% | 0 |
| typesafe_choice | 90,8% | 99,2% | 25,8% | 74,2% | 0 |

- Perguntas estáveis em todas as condições: `target` = Person, `severity` = High. As que divergem: `category`, `primary_risk`, `action`, `review_path`, `link_handling`.
- Jev, antes da abstenção: flips em `primary_risk` (Harassment 11x, Violence 4x) e `link_handling` (RmLink 8x, Brigade 7x); as duas ficam `uncertain` em todas as repetições (prob. máx < 0,60). `category` alterna entre Violence e `uncertain`. Nenhuma pergunta produziu dois rótulos concretos diferentes no Jev.
- Haiku t=0 tem 100% de concordância sem nenhuma abstenção; o doc avisa que isso não implica correção.
- Jev tem std médio menor que 5 das 6 condições de distribuição de LLM; Haiku t=0 tem menor (0,0012). As outras 5 ficam entre 0,0245 e 0,0543 (cerca de 2,5x a 5,6x o do Jev).

## Técnicas reutilizáveis
- Rubrica de N Choices respondida em UMA chamada sobre o mesmo state → roteamento multi-dimensional por chamada; custo e latência por chamada, não por pergunta.
- Decisão `uncertain` por limiar sobre a probabilidade do topo (aqui 0,60), com resultado "revisão humana" → trocar rótulos concorrentes por um desfecho estável; sem chamadas extras.
- Medir repetibilidade com K repetições e um `uid` descartável no state → avaliar estabilidade do modelo sem que cache ou deduplicação interfiram.
- Medir com concordância crua E de política (incluindo `uncertain`), e contar `automatic` e `conflicts` → ver o custo de abstenção junto do ganho de estabilidade.
- Tratar falha de parsing como "sem decisão" (contra a concordância), nunca consertar a resposta → não mascarar formato ruim de LLM.
- Guardar o modelo devolvido (`response.model`) numa chamada feita por alias → detectar troca de versão dentro de um experimento.
- Comparar LLMs pedindo também distribuição de probabilidades (não só rótulo) e aplicar a mesma regra de limiar → comparação justa; single-pick não mede incerteza.
- Colocar o limiar em constante e escolher o de produção com exemplos rotulados e custo de erro/revisão → o 0,60 do doc é ilustrativo.
- Rodar o Jev em sequência (latência limpa) separado do pool concorrente dos LLMs → não medir latência sob contenção.

## Limites e pegadinhas
- Mede repetibilidade, não acurácia nem superioridade: "None of this shows accuracy or superiority". Um único post, 15 repetições por condição.
- A política não torna o modelo determinístico: uma probabilidade perto de 0,60 ainda pode oscilar entre rótulo concreto e `uncertain`.
- O 0,60 é "illustrative", não calibrado e não escolhido para maximizar a concordância desta execução.
- O `uid` está no state e no prompt: não separa sensibilidade ao campo irrelevante da variação entre requisições idênticas.
- Latências: LLMs medidos num pool de 16 vias, Jev sequencial (condições de medição diferentes, admitido pelo doc).
- Preços do Jev são "históricos" (2026-08) e os LLMs "as of 2026-07"; o doc menciona "the `speed_latest` rate" no texto, mas o código só define `TYPESAFE_PRICE`.
- Custo do Jev de US$ 0,000046/chamada com preço 0,042 por 1M tokens de entrada implica cerca de 1.100 tokens de entrada por chamada (derivado; o doc não imprime os tokens).
- Haiku (default) teve 1% de falha de parsing; Haiku às vezes envolve o JSON em cerca de "```json" apesar de pedir só JSON (o código remove uma cerca).
- Os números do heatmap dizem que o 100% de Haiku t=0 "não implica correção".

## Esqueleto de código
```python
MIN_CHOICE_PROBABILITY = 0.60

questions = {key: Choice(instructions=instr, criteria=labels)
             for key, (instr, labels) in QUESTIONS.items()}          # 8 Choices

response = typesafe_client.system_one(
    model="jev-latest",
    state={"uid": f"{rubric_hash}:{sample_index}:{token_hex(4)}", "post": POST},
    questions=questions)
dist = {key: [dict(response.answers[key].probabilities).get(l, float("nan"))
              for l in labels] for key, (_i, labels) in QUESTIONS.items()}

def decision(values, labels):
    label = labels[int(np.argmax(values))]         # None se algum valor for inválido
    return label if max(values) >= MIN_CHOICE_PROBABILITY else "uncertain"

def agreement(picks):                               # 15 decisões de uma pergunta
    return Counter(p for p in picks if p is not None).most_common(1)[0][1] / 15
```
