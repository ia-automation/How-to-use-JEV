---
name: autoresearch-de-features
description: Laço em que um LLM propõe perguntas, o Jev as responde para cada linha e um CatBoost treina nas respostas; em 2.000 resenhas de vinho leva o RMSE held-out de 3,09 (média) para 1,77 pontos com 38 perguntas em 5 rodadas.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 1986–3461 (a receita termina na linha 3459; a linha 3461 já é a página seguinte, Citation check)
estudado_em: 2026-09-30
---

# Descoberta de features por autoresearch (Autoresearch feature discovery)

Nível Advanced no índice. Números de `jev-1.12` e `claude-sonnet-5` em 2026-08-03.

## Problema
CatBoost precisa de uma tabela de números e uma nota de degustação é texto livre. A receita monta a tabela com **perguntas sobre a nota**, nenhuma escrita à mão: um LLM propõe, o Jev responde para cada linha, o CatBoost treina nas respostas, e o laço devolve ao proponente o relatório (importâncias, erros) para a rodada seguinte. Dados: 2.000 resenhas (`GroNLP/ik-nlp-22_winemag`, CSV fixado por commit; notas repetidas verbatim descartadas; amostra embaralhada com seed 0), nota do crítico em escala 80–100 (no sample: 80–98, média 88,73, desvio 3,17). Métrica: RMSE em pontos (erros maiores pesam mais; menor é melhor). Split: `N_DEV=1200` (o laço lê só estes rótulos) e `N_TEST=800` (nunca vistos pelo laço nem pelo modelo; pontuados uma vez no fim).

## Como o Jev entra
- **state:** a própria nota de degustação, texto cru (~245 caracteres), sem ids.
- **perguntas:** não são fixas; o proponente gera. Cada proposta tem `kind` e vira:
  - `intensity` → `Score` com **5 níveis fixos** (criteria = lista):
    0. `Not present in this note at all`; 1. `Barely present - mentioned once, in passing`; 2. `Present at a moderate level`; 3. `Present strongly - the note dwells on it`; 4. `Dominant - the note is largely about this`.
  - `presence` → `Noul` com critérios fixos: true `The note states this or clearly implies it`; false `The note gives no indication of this`.
  - O texto da pergunta (`instructions`) vem do proponente. Exemplo da pergunta mais importante do final: `note_overall_tone_positivity`: "Setting aside specific descriptors, how positive is the overall emotional tone and word choice of the note taken as a whole (warm, admiring language throughout vs. flat, neutral, or lukewarm phrasing)?"
  - Braço "pedir a nota direto": um `Score` (`quality`: "Judging only by what this tasting note says, how good is the wine?") com **10 níveis**, de `Faulty or unpleasant - the note is mostly criticism` até `Profound - the note treats it as exceptional` (intermediários: Barely acceptable; Simple and sound; Pleasant everyday wine; Good; Very good; Excellent - complex and structured; Outstanding - depth and length, built to age; Superb - among the best of its type). Dez é o máximo que um `Score` aceita: onze volta erro de servidor.
- **chamadas:** **uma requisição por linha por rodada, carregando todas as perguntas novas daquela rodada** (mais uma pergunta não custa requisição extra). 8 requisições em voo (`ThreadPoolExecutor(max_workers=8)`). Uma rodada responde as perguntas novas para as 2.000 linhas (2.000 requisições); a contagem cresce com as linhas, não com as perguntas. Uma revisão conta como pergunta nova e custa outra passada em todas as linhas. Oito workers já bastam para bater rate limit em chave compartilhada. Nenhuma pergunta é filtrada antes de ser respondida ("uma pergunta que vale para 1 linha em 10 parece inútil nas 60 notas que o proponente lê e ainda assim pode ser a coluna mais útil").

### Da resposta para colunas (encoding `mean_spread`)
- `Score`: 5 probabilidades por nível (`got.probabilities.get(i, 0.0)` para i em 0..4). Coluna 1 = média `p @ levels`; coluna 2 = desvio `sqrt(max(0, p@levels² − mean²))`. Outros modos no código: `mean` (só a média) e um `_p{i}` por nível.
- `Noul`: uma coluna (`got.noul`).
- Resultado: 29 score × 2 colunas = 58 + 9 noul × 1 = 67 colunas para 38 perguntas.

## O laço (propor → responder → ajustar)
Parâmetros: `ROUNDS=5`, `PROPOSALS=18` (ações por rodada, corte `[:18]`), `EXAMPLES=60`, `MIN_SPREAD=0.05`, `CHANGE_TOLERANCE=0.0`, `ENCODING="mean_spread"`, CV `FOLDS=5`, `REPEATS=3` (média de 3 repetições, estratificada pelo rótulo), CatBoost `iterations=400, depth=4, learning_rate=0.05, loss_function="RMSE", random_seed=0, thread_count=1`.

Por rodada:
1. **Exemplos para o proponente.** Rodada 1: 60 notas dev espalhadas pela faixa de nota (quantis de 0 a 1), cada uma com sua nota (`- scored 91: <texto>`). Rodadas seguintes: as 30 piores previsões dev + as 30 melhores (por |erro| out-of-fold), cada linha com a nota real e a prevista (`- scored 91, predicted 88.3 (last round 89.0): <texto>`); o cabeçalho explica que a diferença entre as metades é o que as perguntas ainda não capturam.
2. **Chamada do proponente** (um único LLM, `claude-sonnet-5`, `effort: medium`, `max_tokens=16000`, saída estruturada JSON Schema; ramo alternativo `gpt-5.6-luna` com `reasoning_effort=high`, **não executado**). Prompt = `PROPOSER_TASK` + exemplos + lista das features atuais (`nome (kind): pergunta`, para `add` não duplicar e `revise`/`drop` referenciarem pelo nome) + feedback.
   - Ações: `{"op": "add"|"revise"|"drop", "target", "name", "kind": "intensity"|"presence", "question"}`; todas as propriedades são `required` (campos não usados voltam vazios; drop usa `kind: "intensity"` e strings vazias). Até 18 ações.
   - Brief (única string que menciona vinho): "You are designing numeric features for a gradient-boosting model that predicts the score a wine critic gave (an integer from 80 to 100) from the tasting note alone. The model sees nothing but the features you design." Orientação: boas features podem ser julgadas pelas palavras da própria nota, variam entre notas e trazem informação de qualidade que as outras não trazem; resenhistas descrevem estrutura, fruta, carvalho, final, complexidade, beberabilidade e sinalizam qualidade também pela escolha de palavras. O brief também imprime os 5 níveis do rubric intensity e diz que presence é a probabilidade de ser verdadeira.
3. **`to_candidates`:** separa ações em candidatas e nomes a largar; `slug` força nome simples e único; id = `nome@rodada` (colunas de rodadas anteriores não colidem); revisão pode manter o nome que substitui; revisão de algo que não existe é ignorada; drop de algo inexistente é ignorado.
4. **Responder:** `featurize` faz uma requisição por nota com todas as perguntas candidatas da rodada.
5. **Adds entram direto**, a menos que a coluna seja "flat": desvio padrão da coluna nas linhas dev `< MIN_SPREAD (0.05)` (registrada como `flat`, não mantida). Importância dirá depois se valeu a pena.
6. **Revisões e drops são testadas uma a uma** (refit do CV sem chamada de API; rejeitar é grátis): `try_change` aceita se `cv_trial <= cv + tolerance` (tolerância 0,0, então tem de melhorar ou empatar exato; o texto do doc diz "tem de melhorar, não só não piorar"). Revisão cujo alvo já foi largado = `stale`. Drop que esvaziaria o conjunto é ignorado. O journal registra `add/flat/revise/reject/stale/drop/keep` com o efeito no CV.
7. **Avaliação:** k-fold CatBoost sobre as colunas → `out_of_fold` (média das 3 repetições) e RMSE CV. Essas previsões fazem 3 trabalhos: julgar revisões/drops, escolher as notas da rodada seguinte, dizer ao proponente quais perguntas ajudaram (e quanto se moveram desde a rodada anterior).
8. **Feedback para a próxima chamada** (`feedback_for`, números arredondados para o cache repetir): RMSE CV de cada rodada até aqui; contagem de notas dev previstas melhor / pior que a rodada anterior por mais de 0,1 ponto; lista das features ordenada por importância (% do total, soma das colunas da mesma pergunta) e **spread** da coluna nas linhas dev ("baixa importância ou baixo spread significa que a pergunta não faz muito; revise ou largue").

### Trajetória registrada (dev CV RMSE)
| rodada | ações | resultado | features | dev CV |
| - | - | - | - | - |
| 1 | 18 add | — | 18 | 1,903 |
| 2 | 5 add, 3 revise, 3 drop | 2 revisões aceitas (1,897→1,894; →1,881), 1 rejeitada (+0,005), 3 drops recusados (+0,009, +0,001, +0,023) | 23 | 1,881 |
| 3 | 7 add, 2 revise, 1 drop | 2 revisões aceitas (1,868→1,864; 1,864→1,861), drop recusado (+0,014) | 30 | 1,861 |
| 4 | 5 add, 2 revise, 3 drop | 1 revisão aceita (1,843→1,838), 1 rejeitada (+0,014), 3 drops recusados | 35 | 1,838 |
| 5 | 4 add, 2 revise, 8 drop | 1 revisão aceita (1,849→1,843), 1 rejeitada (+0,010), 1 drop aceito (`underripe_green_character`, 1,843→1,840), 7 drops recusados (+0,000 a +0,006) | 38 | 1,840 (primeiro valor que não melhorou) |

Rodada 1 adicionou: complexity, fruit_intensity, tannin_structure, acidity_intensity, oak_intensity, finish_length, balance_harmony, aging_potential, positive_superlative_language, negative_critical_language, drinkability_easiness, body_richness, sweetness_level, texture_descriptors, earthy_savory_notes, flaw_or_defect_mentioned, single_vineyard_or_prestige_signal, varietal_blend_detail. Adições posteriores incluem power_concentration_language, flavor_distinctiveness, generic_fruit_language, candied_artificial_flavor, rustic_authentic_character (r2); elegance_finesse_language, minerality_precision_language, hedged_qualified_praise, underripe_green_character, reviewer_overall_verdict_strength, unusual_or_funky_descriptor_valence, botrytis_or_special_winemaking_signal (r3); excess_or_imbalance_signal, descriptive_detail_density, critic_enthusiasm_confidence, savory_food_wine_seriousness, note_overall_tone_positivity (r4); structural_seriousness, youthful_tension_signal, surface_prettiness_vs_depth, price_value_signal (r5). Revisões aceitas: negative_critical_language (r2, r3), single_vineyard_or_prestige_signal (r2), finish_length→finish_quality (r3), rustic_authentic_character (r4), flavor_distinctiveness (r5).

## Resultados medidos
Todos os números na **mesma amostra held-out de 800 linhas**, pontuados uma vez. (Custo e latência por rodada: não medidos no texto, salvo que uma rodada = 2.000 requisições.)

| braço | RMSE | Spearman |
| - | - | - |
| prever a média dos rótulos dev | 3,088 | −0,014 |
| a nota como contagem de palavras, mesmo CatBoost (`text_features`) | 2,466 | 0,605 |
| pedir a nota direto ao Jev (10 bandas, deslocamento −1,71 medido no dev) | 2,145 | 0,761 |
| 18 perguntas da rodada 1, sem laço | 1,869 | 0,778 |
| 38 perguntas após 5 rodadas | 1,772 | 0,799 |

- Rodada 1 → 5 no held-out: **−0,097 pontos, IC95% [−0,147, −0,050]** (bootstrap pareado, 2.000 reamostragens). "A maior parte do ganho está na primeira chamada"; as 4 rodadas seguintes valem 0,10 ponto. A linha held-out cai mais que a dev.
- A linha dev fica sempre acima da held-out: efeito de tamanho de treino (cada dobra treina com 4/5 das 1.200 linhas; o held-out sai de um modelo treinado nas 1.200). As duas linhas se movem juntas, então o número dev que o laço usa acompanha o held-out que ele nunca vê.
- Rodada 5 propôs 4 adds, 2 reescritas e 8 drops: "a proposta virou de adicionar para largar"; há um limite do que perguntar sobre uma nota de 245 caracteres.
- Resultado final: 38 perguntas (29 score, 9 noul).

Importância por pergunta (% do total CatBoost, colunas somadas por pergunta; top 12): note_overall_tone_positivity (score) 17,4; savory_food_wine_seriousness (score) 8,7; positive_superlative_language (score) 8,4; single_vineyard_or_prestige_signal (noul) 7,2; descriptive_detail_density (score) 5,7; elegance_finesse_language, complexity, aging_potential (score) 5,0 cada; balance_harmony, drinkability_easiness (score) 2,9 cada; critic_enthusiasm_confidence (score) 2,7; flavor_distinctiveness (score) 2,6. Nota: "importance share" não é parcela de linhas, de perguntas nem de acurácia.

Mapa de calor (visualização): 5 resenhas held-out em quartis da nota (80, 86, 89, 91, 97 pontos) contra 15 das 38 perguntas (as 8 score e as 7 noul mais importantes), linhas ordenadas por polaridade (correlação de Spearman da resposta com a nota no dev), de modo que as de cima sobem com a nota e as de baixo caem.

## Técnicas reutilizáveis
- **Perguntas como features** ("texto → tabela numérica") → quando um modelo tabular supervisionado precisa de sinal que está em texto livre: Score vira média + desvio, Noul vira uma probabilidade.
- **Proponente = LLM separado do Jev**, com saída estruturada por schema, ações `add/revise/drop` sobre um conjunto nomeado → quando o espaço de perguntas é aberto e quer-se busca guiada por erro.
- **Feedback ao proponente = placar numérico + exemplos**: RMSE por rodada, quantas linhas melhoraram/pioraram > 0,1, importância% e spread de cada feature, e as 30 piores + 30 melhores previsões com nota real, prevista e da rodada anterior. "O que separa as metades é o que as perguntas não capturaram."
- **Adicionar é barato, remover exige prova**: add entra direto (resposta já paga; importância julga depois); revisão e drop só ficam se o CV dev melhorar. Refit não chama API, então testar e rejeitar é grátis.
- **Filtro de coluna chata**: `std < 0,05` nas linhas dev = "flat", descarta.
- **Tudo de uma rodada em uma requisição por linha**: o custo cresce com linhas, não com perguntas; não filtrar perguntas antes de responder (uma pergunta rara pode ser a mais útil).
- **Disciplina de split**: o laço lê só dev (CV 5 dobras × 3 repetições); held-out pontuado uma vez; ganho reportado com IC bootstrap pareado.
- **Linhas de base honestas ao lado**: média, contagem de palavras, pedir a nota direto. Permite saber o que o laço adiciona.
- **Pedir o alvo direto é uma linha de base forte mas com calibração externa**: 10 bandas de qualidade reescaladas para 80–100 e um único deslocamento medido no dev (−1,71); é a única coisa que esse atalho aprende com os rótulos.
- **Nome e id por rodada** (`nome@rodada`) para colunas de rodadas anteriores sobreviverem a revisões; revisão pode manter o nome.
- **Arredondar números no prompt** para o cache do proponente repetir na reexecução.
- **Fator de adaptação**: só `PROPOSER_TASK` menciona vinho; `featurize()` aceita qualquer lista de strings.
- **Pergunta ampla de tom** (`overall_tone_positivity`) ficou no topo (17,4%): além de traços específicos, o sinal "palavra do crítico" pesa.

## Limites e pegadinhas
- Um dataset, uma execução do laço (o doc diz). O braço de contagem de palavras é o tratamento de texto do próprio CatBoost, "não um pipeline de regressão de texto afinado".
- `Score` aceita no máximo 10 níveis; 11 dá erro de servidor.
- O número de requisições é o custo oculto: 2.000 por rodada aqui; 100.000 linhas = 100.000 requisições por rodada; revisão = nova passada completa. 8 workers já batem rate limit em chave compartilhada.
- Mudar `PROPOSER_TASK` muda a chave de cache: todas as rodadas chamam a API de novo. Cache por nome de função + como cada argumento foi escrito (por isso `load_slice(..., seed=seed)` em keyword).
- Ganho principal vem da 1ª chamada; rodadas extras somam ~0,10 e saturam (r5 sem melhora dev e mais drops que adds). Risco admitido nos próximos passos: importância que depende de um split só (falta teste de estabilidade entre seeds).
- Drops e revisões são avaliados no CV dev, que o laço otimiza; o held-out serve de verificação, não de guia.
- Propostas de amostra dev pequena (60 notas) podem subestimar perguntas que valem para poucas linhas.
- O ramo `gpt-5.6-luna` do proponente existe no código mas não foi rodado; o cache guarda a corrida Anthropic.
- Extensões sugeridas pelo doc (não feitas): triar candidata antes de pagar (usar a própria pergunta como state e fazer 4 Nouls: dá para responder com o texto-fonte? significa uma coisa só? vale para a maioria das linhas? varia entre linhas?); podar colunas correlacionadas; baselines TF-IDF/contagens; misturar famílias de proponentes; outros modelos (elastic-net, SVR, random forest, recalibração); baseline de embeddings (`sentence-transformers/all-MiniLM-L6-v2` local, `text-embedding-3-small`); validação alinhada ao deploy (cronológica, agrupada, teste intocado); parar em platô ou orçamento; rodar em modo Goal de agente; checar estabilidade entre seeds.

## Esqueleto de código
```python
INTENSITY_LEVELS = ["Not present in this note at all", "Barely present - mentioned once, in passing",
  "Present at a moderate level", "Present strongly - the note dwells on it",
  "Dominant - the note is largely about this"]
PRESENCE_CRITERIA = NoulCriteria(true="The note states this or clearly implies it",
                                 false="The note gives no indication of this")

def feature_questions(features):
    return {f["name"]: (Score(instructions=f["question"], criteria=INTENSITY_LEVELS)
                        if f["kind"] == "intensity" else
                        Noul(instructions=f["question"], criteria=PRESENCE_CRITERIA))
            for f in features}

def answer(model, note, features):           # uma requisição por nota, todas as perguntas da rodada
    r = client.system_one(state=note, questions=feature_questions(features), model=model)
    return {f["name"]: ([r.answers[f["name"]].probabilities.get(i, 0.0) for i in range(5)]
                        if f["kind"] == "intensity" else [r.answers[f["name"]].noul])
            for f in features}

def encode(feature, P, mode):                # P: linhas x níveis
    if feature["kind"] == "presence": return [(feature["name"], P[:, 0])]
    lv = np.arange(P.shape[1]); mean = P @ lv
    var = P @ (lv**2) - mean**2
    return [(feature["name"], mean), (feature["name"] + "_sd", np.sqrt(np.clip(var, 0, None)))]

# aceitar revisão/drop só se o CV dev melhora (sem API):  cv_trial <= cv + tolerance
# add: manter salvo coluna flat (std nas linhas dev < 0.05)
```
