---
name: autoconsistencia-nouls
description: Mede se 14 respostas True/False sobre um sinistro de seguro se mantêm estáveis em 15 repetições; Jev tem desvio-padrão médio de probabilidade 0,0102, abaixo de todas as condições de LLM, e uma faixa 0,30–0,70 manda o incerto para revisão humana.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 6035–6736
estudado_em: 2026-09-30
---

# Autoconsistência de Nouls (Self-consistency: nouls)

## Problema
Triagem de sinistros de seguro auto: cada sinistro vira pagar, negar ou mandar para humano, guiado por probabilidades. Perto de um limiar, pequenas oscilações trocam a ação (0,49 vs 0,51 = ações opostas). O cookbook roda a mesma rubrica de 14 perguntas sobre UM sinistro 15 vezes por condição e olha se cada resposta "fica parada". Há de propósito casos limítrofes no sinistro (juízo, não fato):
- perda em evento de track-day (apólice exclui "track/competitive driving"), mas no estacionamento, carro parado, fora da pista;
- item de aluguel de carro cobrado, mas a apólice não tem reembolso de aluguel;
- sem boletim de ocorrência, mas a apólice exige para colisão acima de US$ 2.000;
- nota do auto-triage já diz "approved, pay full amount" antes de revisão humana e sem reter a franquia.

## Como o Jev entra
- **state:** `{"uid": f"{sample_index}:{token_hex(4)}", "claim": CLAIM}`. O sinistro é um dict JSON passado direto como estrutura (não string). `uid` = valor único descartável, novo a cada chamada, sem relação com o conteúdo. CLAIM tem chaves `policy` (policy_id, policyholder, effective 2026-01-15, expires 2027-01-15, coverages {collision True, rental_reimbursement False}, deductible 500.00, per_incident_limit 10000.00, listed_drivers, exclusions, reporting_window_days 10, police_report_required_over 2000.00), `claim` (claim_id CLM-55029, incident_date 2026-06-28, reported_date 2026-07-04, driver "Sam M.", description, amount_claimed 3250.00, 4 line_items somando 1700+800+450+300, documentation), `adjuster_notes`, `claim_history` (claims_last_12mo 2, prior_denied 0).
- **perguntas:** 14 `Noul`, todas redigidas para que "sim" = a coisa verificada é verdadeira (mantém as linhas comparáveis entre modelos). Chave → texto literal:
  - `covered`: "Is the loss covered under the policy's collision coverage?"
  - `exclusion`: "Does a policy exclusion apply to this loss?"
  - `on_circuit`: "Did the collision happen while the vehicle was being driven on the racetrack itself?"
  - `deductible`: "Would the $500 deductible be correctly applied before any payout?"
  - `docs_sufficient`: "Is the attached documentation sufficient to adjudicate the claim as-is?"
  - `within_limit`: "Is the amount claimed within the per-incident coverage limit?"
  - `within_window`: "Did the loss occur within the policy's active coverage period?"
  - `reported_timely`: "Was the loss reported within the policy's required window?"
  - `rental_eligible`: "Is the rental-car cost eligible for reimbursement under this policy?"
  - `fraud_flag`: "Are there indicators that warrant a fraud review?"
  - `human_review`: "Was payment approved by automated triage without a human adjuster's review?"
  - `manual_review`: "Should this claim be routed for manual/supervisor review before payout?"
  - `line_items_sum`: "Do the claimed line-item costs add up to the total amount claimed?"
  - `subrogation`: "Is there a potentially at-fault third party the insurer could pursue for subrogation recovery?"
- **chamadas:** UMA chamada `system_one` responde as 14. 15 repetições por condição (`NUM_SAMPLES = 15`), cada uma com `uid` novo. Modelo: `jev-latest` (resolveu para `jev-1.13.0` nas 15 chamadas; o código guarda `requested_model` e `response_model`). `timeout=30.0`. As 15 chamadas do Jev rodam em sequência; as de LLM em `ThreadPoolExecutor(max_workers=16)`.

### Condições comparadas (cada uma 15 vezes, prompt único com JSON do sinistro + 14 perguntas)
| Modelo | Prob. t=0 | Prob. default | Yes/no t=0 |
|---|:-:|:-:|:-:|
| claude-haiku-4-5 | sim | sim | sim |
| gpt-5.4-mini | sim | sim | sim |
| gpt-5.5 (raciocínio) | — | sim | — |
| claude-opus-4-8 (raciocínio) | — | sim | — |
| jev-latest (`typesafe_noul`) | — | sim | — |
"default" = sem argumento de temperatura. Raciocínio não tem dial de temperatura. Yes/no: resposta seca "yes"/"no" mapeada para 1.0/0.0 (força decisão, sem massa no meio). Formato de probabilidade no prompt: "give your probability that the answer is yes... JSON object mapping each question's key to a number between 0.00 and 1.00". O prompt do LLM inclui `uid: {i}:{token_hex(4)}`. Raciocínio: Claude com `thinking={"type":"adaptive"}`, OpenAI com `reasoning_effort="high"`; `max_tokens=4096` no Claude.

## O que o código faz com a resposta
- Jev: `nouls[key] = response.answers[key].noul` = P(true) daquela pergunta.
- LLM: texto → tira cerca ```` ```json ```` (claude-haiku-4-5 embrulha quase toda resposta nela mesmo com "ONLY a JSON object") → `json.loads`; falha de parse vira NaN ("contada mas não pontuada"). `_parse_answer`: chave ausente/não numérica/nem yes nem no = NaN, nunca um valor de aparência legítima.
- **Faixa de incerteza (lógica da aplicação, sem pergunta nova nem segunda chamada):** `NOUL_UNCERTAINTY_LOW = 0.30`, `NOUL_UNCERTAINTY_HIGH = 0.70`. p < 0,30 → `no`; 0,30 ≤ p ≤ 0,70 (ambas as bordas incluídas) → `uncertain` (vai para humano); p > 0,70 → `yes`. Os valores de Noul continuam visíveis junto da decisão.
- Cache: amostras em `json_cache.json` com chave incluindo `sample_index`, `rubric_hash` (sha256[:12] de `[CLAIM, QUESTIONS]`) e modelo; editar sinistro/pergunta invalida o cache. Preço é aplicado DEPOIS do cache (mudar preço não exige reamostrar); guarda-se tokens, não custo.

## Resultados medidos
| Métrica | LLMs | Jev |
|---|---|---|
| Desvio-padrão médio por pergunta da probabilidade | "abaixo de todas as condições de LLM" diz o texto; números das LLMs só no gráfico (não declarado no texto) | 0,0102 |
| `covered` (15 amostras) | LLMs oscilam, inclusive a t=0 | 0,43 a 0,53 (cruza 0,5) |
| `exclusion` | oscila | 0,53 a 0,62 |
| demais 13 perguntas | — | ficam do mesmo lado de 0,5 em todas as 15 |

Custo e latência por chamada (14 perguntas, média de 15; preços históricos assumidos, "não verificados para jev-latest"; Jev a US$ 0,042/1M tokens de entrada, 0,00 de saída):
| Condição | Latência | Custo | Latência vs Jev | Custo vs Jev |
|---|---|---|---|---|
| claude-haiku-4-5 t=0 | 1780 ms | $0,001798 | 16,0x | 42,2x |
| claude-haiku-4-5 default | 1644 ms | $0,001798 | 14,8x | 42,2x |
| claude-haiku-4-5 yes/no t=0 | 1485 ms | $0,001650 | 13,4x | 38,8x |
| gpt-5.4-mini t=0 | 1405 ms | $0,001089 | 12,7x | 25,6x |
| gpt-5.4-mini default | 1177 ms | $0,001179 | 10,6x | 27,7x |
| gpt-5.4-mini yes/no t=0 | 1113 ms | $0,000950 | 10,0x | 22,3x |
| gpt-5.5 raciocínio | 11125 ms | $0,033157 | 100,2x | 778,9x |
| claude-opus-4-8 raciocínio | 13886 ms | $0,034275 | 125,0x | 805,1x |
| Jev (`typesafe_noul`) | 111 ms | $0,000043 | 1,0x | 1,0x |
Preços de LLM por 1M tokens (entrada, saída): haiku-4-5 (1,00; 5,00), gpt-5.4-mini (0,75; 4,50), gpt-5.5 (5,00; 30,00), opus-4-8 (5,00; 25,00). Data da amostragem: 2026-09-11.

Observações do texto: fatos estáveis entre condições; as perguntas de juízo (`exclusion`, `rental_eligible`, `fraud_flag`, `manual_review`) são onde as LLMs se movem ou discordam entre modelos (e consigo mesmas).

## Técnicas reutilizáveis
- Medir estabilidade repetindo N vezes a MESMA consulta com um campo `uid` único e irrelevante → quando quiser separar instabilidade do modelo de cache/idempotência.
- Redigir toda pergunta de rubrica com "sim = a coisa verificada é verdadeira" → quando precisar comparar probabilidades entre perguntas/modelos na mesma escala.
- Faixa de incerteza (abaixo/entre/acima) sobre P(true) em vez de corte único em 0,5 → quando decisões opostas perto do corte custam caro; o meio vai para humano.
- Uma chamada carregando todas as perguntas da rubrica (14) sobre o mesmo state → quando o custo/latência por pergunta importa.
- Modo yes/no forçado como linha de controle (1.0/0.0) → mostra o que o modelo faz quando não pode deixar massa no meio.
- Chave de cache = hash de (estado + texto de todas as perguntas) + modelo solicitado; guardar o modelo RESOLVIDO do alias → evita servir resposta velha depois de editar a rubrica ou de o alias `latest` mudar de versão.
- Guardar tokens no cache e aplicar preço depois → mudança de tabela de preço sem reamostrar.
- Resposta não parseável vira NaN (contada, não pontuada), nunca um valor plausível.

## Limites e pegadinhas
- A faixa 0,30–0,70 é ilustrativa: "nem garantia calibrada nem limiar otimizado"; definir limites de produção com exemplos rotulados e custo de decisão errada vs custo de revisão.
- A faixa tem bordas próprias: valor perto de 0,30 ou 0,70 ainda pode pular entre `uncertain` e yes/no. O modelo não fica mais determinístico por isso, e decisão automática fora da faixa não está provada correta.
- O desenho não separa sensibilidade ao campo irrelevante (`uid`) da variação que ocorreria em pedidos idênticos.
- Jev também varia: `covered` cruza 0,5 entre 0,43 e 0,53.
- Custos usam preços históricos/assumidos ("não são preços verificados de jev-latest nem cobrança atual"); o texto cita a taxa `speed_latest` para o Jev (linha 6504) enquanto o código define `TYPESAFE_PRICE = (0.042, 0.00)` "as of 2026-08".
- Latência medida sob a concorrência indicada (16 threads nas LLMs, Jev em série).
- Só UM sinistro e 14 perguntas; "reprodutível sem gasto" depende do `json_cache.json` que acompanha o cookbook.

## Esqueleto de código
```python
questions = {key: Noul(instructions=q) for key, q in QUESTIONS.items()}
response = typesafe_client.system_one(
    model="jev-latest",
    state={"uid": f"{sample_index}:{token_hex(4)}", "claim": CLAIM},
    questions=questions,
)
nouls = {key: response.answers[key].noul for key in QUESTIONS}   # P(true) por pergunta

NOUL_UNCERTAINTY_LOW, NOUL_UNCERTAINTY_HIGH = 0.30, 0.70
def noul_decision_with_uncertainty(p: float) -> str:
    if p < NOUL_UNCERTAINTY_LOW:  return "no"
    if p > NOUL_UNCERTAINTY_HIGH: return "yes"
    return "uncertain"            # 0.30 <= p <= 0.70 inclusive -> revisão humana
```
