---
name: perguntas-em-paralelo
description: Mandar as 13 perguntas de um briefing regulatório (GDPR, ~54 mil caracteres) numa única chamada custa 12,2x menos e leva 10,0x menos tempo que 13 chamadas de 1 pergunta, sem mudar as respostas.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/parallel_questions.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 9235–9582
estudado_em: 2026-09-30
---

# Perguntas em paralelo (Parallel questions)

## Problema
Um documento e N perguntas sobre ele: uma requisição com as N perguntas, ou N requisições de 1 pergunta? No Jev as respostas saem iguais nos dois jeitos: cada pergunta é pontuada por conta própria contra o documento, então a resposta não depende do que mais está na requisição. O documento domina o custo de cada requisição; N chamadas pagam por ele N vezes e N viagens de rede; a chamada em lote paga uma vez. Quanto maior o documento, mais o ganho chega a Nx cheio.

## Como o Jev entra
- **state:** `{"article": DOCUMENT}` onde `DOCUMENT = {"source": "https://en.wikipedia.org/?oldid=1363040264", "text": <artigo>}`. Artigo = Wikipedia "General Data Protection Regulation", revisão fixa 1363040264 (2026-07), 53.777 caracteres (~54 mil), texto puro via API do MediaWiki (`explaintext=1`), cacheado junto com as chamadas para o documento não mudar. O documento é byte-idêntico em toda chamada.
- **perguntas (13 = 8 Noul + 2 Choice + 3 Score):**
  Noul (só `instructions`, sem `criteria`):
  - `breach_72h`: "Must a personal data breach be reported to the supervisory authority within 72 hours?"
  - `applies_non_eu`: "Does the regulation apply to organisations established outside the EU that offer goods or services to people in the EU?"
  - `dpo_all_orgs`: "Must every organisation appoint a Data Protection Officer, regardless of what data it processes?"
  - `pre_ticked_consent`: "Can valid consent be obtained through pre-ticked boxes or inactivity?"
  - `right_erasure`: "Does the regulation grant individuals a right to erasure of their personal data?"
  - `data_portability`: "Does the regulation include a right to data portability?"
  - `us_federal_law`: "Is the GDPR a United States federal law?"
  - `criminal_penalties`: "Does the GDPR itself impose criminal penalties such as imprisonment?"

  Choice (`criteria` = dict rótulo → significado):
  - `instrument_type` "What kind of EU legal instrument is the GDPR?": `Regulation` (Directly binding law in all member states, no national implementation needed.) · `Directive` (Sets goals that member states implement through national law.) · `Treaty` (An international treaty between states.) · `Recommendation` (Non-binding guidance.)
  - `max_fine` "What is the maximum administrative fine for the most serious infringements?": `TwentyM_or_4pct` (Up to EUR 20 million or 4% of annual worldwide turnover, whichever is greater.) · `TenM_or_2pct` (Up to EUR 10 million or 2% ..., whichever is greater.) · `FixedCap` (A fixed amount not tied to turnover.) · `NoFines` (The GDPR provides no administrative fines.)

  Score (`criteria` = lista de descrições do nível 0 para cima):
  - `individual_rights` "How strong are the rights the GDPR grants to individuals over their data?": 4 níveis None / Weak / Moderate / Strong
  - `penalty_severity` "How severe are the penalties the GDPR provides for non-compliance?": 4 níveis None / Symbolic / Substantial / Severe
  - `compliance_burden` "How heavy is the compliance burden the GDPR places on organisations?": 5 níveis Negligible / Light / Moderate / Heavy / Extreme

  Um número rastreado por resposta: Noul → `p(yes)` (`answer.noul`); Choice → `max prob` (`max(answer.probabilities.values())`); Score → nota normalizada 0–1 = `answer.score / (len(criteria) - 1)`.
- **chamadas:** dois modos comparados, `RUNS = 5` repetições cada: (a) 1 chamada com as 13 perguntas; (b) 13 chamadas de 1 pergunta. `ask(keys, run)` monta `questions={key: QUESTIONS[key] for key in keys}`; `run` só força uma chamada viva distinta por repetição (cache). Preço aplicado depois da leitura do cache: `PRICE = (0.042, 0.00)` US$ por 1M tokens (entrada, saída) para `jev-1.12` em 2026-09; saída é gratuita, então o custo é só tokens de entrada.

## O que o código faz com a resposta
Só mede: por pergunta, média e desvio-padrão (`statistics.stdev`) das 5 repetições nos dois modos, para provar que o lote não desloca a média (viés) nem aumenta o desvio (ruído). Depois soma custo e latência: para o modo unitário soma as 13 latências, isto é, assume execução sequencial.

## Resultados medidos
Modelo `jev-1.12`, média das 5 repetições:

| modo | chamadas | custo | tempo total |
|---|---|---|---|
| 1 chamada, as 13 | 1 | US$ 0,000497 | 0,27 s |
| 13 chamadas, 1 cada | 13 | US$ 0,006090 | 2,71 s |
| razão | | **12,2x mais barato** | **10,0x mais rápido** |

Respostas (média lote / média unitária; desvio lote / unitário):
- 6 dos 8 Noul, os 2 Choice e os 3 Score: idênticos nas 5 repetições, desvio exatamente 0,0 nos dois modos. Ex.: `applies_non_eu` 0,990; `dpo_all_orgs` 0,030; `pre_ticked_consent` 0,040; `right_erasure` 0,990; `data_portability` 0,990; `us_federal_law` 0,010; `instrument_type` 1,000; `max_fine` 1,000; `individual_rights` 1,000; `penalty_severity` 1,000; `compliance_burden` 0,750.
- `breach_72h`: 0,804 / 0,814; desvio 0,0055 / 0,0055.
- `criminal_penalties`: 0,108 / 0,108; desvio 0,0045 / 0,0084.
- Conclusão do doc: o ruído de `breach_72h` e `criminal_penalties` é propriedade da pergunta, igual nos dois modos; "nenhuma resposta depende das outras 12 perguntas na mesma requisição".

Como foi medido o 12,2x / 10,0x: `singles_cost / batched_cost` e `singles_latency / batched_latency`; ambos médias de 5 execuções; custo = tokens de entrada × 0,042/1e6 (+ saída × 0), tokens e latências cacheados junto das respostas. O custo do modo unitário é a soma dos 13 custos por execução; a latência do modo unitário é a soma das 13 latências. (Conta derivada aqui, não afirmada no doc: US$ 0,000497 ÷ 0,042/1M ≈ 11,8 mil tokens de entrada no lote; 12,2x em vez de 13x porque cada chamada unitária também carrega sua própria pergunta.)

## Técnicas reutilizáveis
- Todas as perguntas sobre o mesmo documento vão numa só chamada → sempre que o documento domina o custo da requisição (documento longo, muitas perguntas).
- O lote não contamina respostas: cada pergunta é avaliada de forma independente → pode juntar perguntas de tipos diferentes (Noul, Choice, Score) sem medo de viés.
- Guardar um número por pergunta e tipo (p(yes), prob. máxima, score normalizado) → comparar e auditar respostas heterogêneas com a mesma régua.
- Medir estabilidade repetindo a mesma chamada várias vezes e olhando desvio-padrão por pergunta (RUNS=5) → separar ruído da pergunta de efeito do método.
- Citar uma revisão fixa do documento e cachear o texto junto das chamadas → números reproduzíveis mesmo com a fonte mudando.
- Montar cada pergunta como Noul curto e factual ("Must ... within 72 hours?"), com Choice rotulado quando a resposta é uma categoria fechada (inclusive valores numéricos como rótulos: `TwentyM_or_4pct`) → checagem de conformidade/briefing.
- A receita de re-ranking remete a esta: numa aplicação real, várias perguntas sobre o mesmo par (consulta, candidato) vão numa chamada só.

## Limites e pegadinhas
- A razão de 10,0x de velocidade soma as 13 latências, portanto supõe chamadas sequenciais. "Se você disparar concorrentemente, a diferença diminui, mas o custo de 13x em tokens permanece."
- O ganho de custo vale "independentemente de como você dispara as chamadas"; chega perto de Nx só com documento grande.
- Dois Noul (`breach_72h`, `criminal_penalties`) têm ruído de amostragem pequeno (desvios ~0,005–0,008), igual nos dois modos.
- O caso é intensivo em documento (~54 mil caracteres): o doc não mede com documentos curtos.
- Latência absoluta de 0,27 s por lote de 13 perguntas é medida em uma máquina/rede não descrita (não declarado no doc).
- O preço tem data 2026-09 nesta receita e 2026-08 na de re-ranking (mesmo 0,042/0,00).

## Esqueleto de código
```python
state = {"article": DOCUMENT}               # documento byte-idêntico em toda chamada

def ask(keys, run):
    response = client.system_one(
        state=state,
        questions={key: QUESTIONS[key] for key in keys},
        model="jev-1.12",
    )
    values = {}
    for key in keys:
        answer = response.answers[key]
        if isinstance(answer, NoulAnswer):
            values[key] = answer.noul
        elif isinstance(answer, ChoiceAnswer):
            values[key] = max(answer.probabilities.values())
        else:
            values[key] = answer.score / (len(QUESTIONS[key].criteria) - 1)
    return values, response.usage.input_tokens, response.usage.output_tokens

batched = ask(tuple(QUESTIONS), run)                          # 1 chamada, 13 perguntas
singles = {k: ask((k,), run) for k in QUESTIONS}              # 13 chamadas, 1 pergunta
```
