---
name: cascata-sde
description: Cascata de extração estruturada (mini gpt-5.4-mini, verificação por bateria de Nouls do Jev por campo, escalada para gpt-5.5 só se algum campo passar de 0,7) — a fronteira custo x qualidade de 100 prompts fica acima e à esquerda de cada modelo sozinho.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/sde_cascade.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 10454–11111
estudado_em: 2026-09-30
---

# Cascata SDE (SDE cascade)

## Problema
Modelos grandes de raciocínio extraem dados estruturados bem, mas são lentos e caros; modelos pequenos são baratos e erram. Uma cascata pega a maior parte da qualidade por uma fração do custo: (1) extrai com modelo barato; (2) verifica com perguntas Noul do Jev, cada uma devolvendo P(algo está errado); (3) escala para o modelo caro se algum sinal dispara; senão fica com a resposta barata. Os dois degraus de extração usam OpenAI em modo texto, sem structured outputs, tool calls nem json mode: o erro que se espera não é de seguir o schema (fácil de sintetizar), e quando o LLM falha o schema costuma estar muito confuso, então decodificação restrita não resolve o problema de fundo.

Preços (US$ por 1M tokens, entrada/saída, tarifas padrão de 15 de setembro de 2026): degrau 0 `gpt-5.4-mini` 0,75/4,50; degrau 1 `gpt-5.5` 5,00/30,00 (~7x o mini); verificador `jev-1.12` 0,042/0,00 (saída gratuita).

## Como o Jev entra
- **state** (uma chamada `system_one` por registro, em `verify`):
  ```
  {"system_message": EXTRACT_SYSTEM, "instruction": "Extract the structured record from this document",
   "source_text": row["content"], "schema": schema, "extraction": record}
  ```
  Dado de exemplo: linha 516 do dataset `scrapegraphai/scrapegraphai-100k` (revisão fixa `4bb9fba1dff9181c5acdb60a5a26fea62fa54fe9`): página de calendário de eventos da NYU; o schema pede `registration_open_date` (mm/dd/yyyy, "Return a blank string if you are unsure.") e `description` (com exemplo "Registration opens for the fall semester" na própria descrição). A página só tem navegação/boilerplate, sem data nem descrição. Logo um bom extrator deve deixar vazio. (Nessa faixa, "Mobile Navigation" e "Events Calendar" são o conteúdo da página de exemplo, não conceitos do Jev.)
- **perguntas:** todas `Noul`, construídas por `build_questions(record)`; `true` = algo está errado (caso de escalada). Id `campo::métrica`. A `instructions` de cada pergunta de campo é um DICT `{"field_spec": spec, "extracted_field": value, "main_question": <texto>}`; `field_spec` = `{path, type, description, required}` tirado do schema (desembrulha `anyOf` com `null`; tipo `unknown` se não achar).
  - Cabeça holística `__overall__::judge`: "Is this extracted record an incorrect extraction -- some value unsupported by the source or not conforming to the schema, required information missing or wrong, or some field hallucinated -- so it should be escalated to a smarter model?" true "the record is an incorrect extraction" / false "the record is a correct extraction". É calculada e exibida para contraste, mas o portão NÃO a usa.
  - Campo NÃO vazio (qualquer valor que não seja `None`, `""`, `[]`, `{}`) recebe 7 cabeças (`MAIN_QUESTIONS`), com `true`/`false` literais:
    - `name_desc_mismatch`: "Does the `extracted_field` fail to match the field at `path` or the `description` in the `field_spec`? If the `description` is empty, judge against the `path` alone." true "...does not match the field name or its `description`" / false "...matches the field name and `description`".
    - `type_mismatch`: "Does the `extracted_field` violate the `type` declared in the `field_spec`?" (pulada se `type == "unknown"`).
    - `unreasonable`: "Is the `extracted_field` one that a reasonable person would not have extracted for this `field_spec`?"
    - `hallucinated`: "Is the `extracted_field` unsupported by, or absent from, the source text?" true "...is a hallucination -- not supported by, or absent from, the source text".
    - `off_target`: "Does the source text fail to genuinely report the thing the `field_spec` describes, so the value was pulled from incidental text?" true "the source does not genuinely provide this field -- the value was pulled from incidental text".
    - `incomplete`: "Does the `extracted_field` fail to capture a value the source supports (note whether the `field_spec` is `required`)?" true "the field is wrongly empty, null, or missing a value the source supports".
    - `format_violation`: "Does the `extracted_field` violate the format or constraints implied by the `description`, the schema `type`, and the extraction instructions (e.g. date format, units, enum membership)?"
  - Campo VAZIO recebe só `absence_wrong`: "The `extracted_field` is empty, null, or an empty collection. Does the source text contain the information the `field_spec` describes, making the empty result wrong?" true "a value was wrongly omitted" / false "returning nothing is correct".
  - O pipeline completo tem também uma cabeça `spurious` (contêineres inteiros) e um score geral `difficulty`; não mostrados.
- **chamadas:** 1 extração barata + 1 chamada ao Jev com toda a bateria do registro (no exemplo, 9 Nouls: 1 overall + 7 de `description` + 1 `absence_wrong` de `registration_open_date`) + 1 extração cara só se escalar. Extração: `extract(model, prompt, schema, content, *, reasoning_effort=None, temperature=None)`; system message `EXTRACT_SYSTEM` = "You extract structured data from documents. Return only values supported by the text. Follow any value format specified by the schema or its field descriptions."; user message = prompt + "Return ONLY a JSON object matching this JSON Schema:" + schema + "Document:" + content. O degrau 1 roda com `reasoning_effort="high"`. Nenhuma paralelização declarada.

## O que o código faz com a resposta
- Portão `any_flag` (estilo max): escalar se QUALQUER campo dispara `p > FIRE_T`, com `FIRE_T = 0.7` (estritamente maior), o mesmo valor do marcador `<== FIRES`. Filtra fora ids que começam com `__overall__`. Um vermelho confiante basta, não é diluído por média.
- Se escalar: `final_record = extract(REASONING, ..., reasoning_effort="high")`; senão `mini_record`.
- Resposta não parseável (`json.loads` falha) vira `{}`.
- Validação de schema (`jsonschema.Draft202012Validator(schema).is_valid`) é necessária mas não suficiente: pega erro estrutural, nunca semântico. O registro do exemplo é válido e mesmo assim errado.

## Resultados medidos
Exemplo de ponta a ponta (registro do mini fixado no código: `{"registration_open_date": "", "description": "Registration opens for the fall semester"}`; o doc diz que o `gpt-5.4-mini` é muito estocástico nesta entrada, inventa uma `description` diferente quase a cada execução mesmo com `temperature=0`, então a fabricação canônica foi codificada fixa):

| pergunta | P(errado) |
|---|---|
| description::hallucinated | 0,95 (dispara) |
| description::off_target | 0,85 (dispara) |
| description::unreasonable | 0,58 |
| __overall__::judge | 0,56 |
| description::incomplete | 0,16 |
| registration_open_date::absence_wrong | 0,14 |
| description::format_violation | 0,10 |
| description::name_desc_mismatch | 0,08 |
| description::type_mismatch | 0,02 |

Decisão: ESCALATE. O `gpt-5.5` devolve `{"description": "", "registration_open_date": ""}`: corta a `description` inventada.

100 prompts scrapegraphai (resultados INTERNOS da TypeSafe, método `extract → verify → escalate`, `gpt-5.4-mini → gpt-5.5-reasoning`, portão `any_flag`; limiar varrido de 0 a 1, cada configuração plotada em custo x qualidade): o modelo mais forte sozinho (`gpt-5.5-reasoning`) fica em ≈0,81 de qualidade por ≈US$ 0,10/extração; a fronteira de Pareto da cascata fica "acima e à esquerda" de cada modelo sozinho (4 modelos avaliados). O gráfico é "retrato histórico": custos não recalculados pelo preço atual do Jev. Os demais números (qualidade da cascata, economia, taxa de escalada) só existem no gráfico, não no texto.

## Técnicas reutilizáveis
- Cascata extrair-barato, verificar, escalar-só-se-sinal → quando um modelo pequeno acerta a maioria e só uma minoria precisa do caro.
- Decomposição programática: uma pergunta estreita por campo e por tipo de erro → "maximiza a inteligência de cada prompt, torna o algoritmo ajustável e interpretável" e localiza o erro no campo.
- Bom sinal verificador (Apêndice A): estreito e ancorado (sim/não verificável sobre um campo contra a fonte, não "esta extração é boa?"); "ruim = TRUE" com critérios `true`/`false` explícitos; por campo e depois `max` (um vermelho confiante escala); independente e barato (verificador dedicado pega pontos cegos do extrator e não come a economia); separador/calibrado (alto nos erros reais, baixo nos corretos, então um limiar só divide aceitar de escalar).
- Campo vazio recebe só a pergunta de ausência errada → não gastar perguntas de tipo/formato em valor vazio.
- Teste de fabricação típica: o schema tem valor de exemplo na descrição e o modelo pequeno o copia como resposta (ou narra "não foi encontrado") → incluir `hallucinated` e `off_target`.
- Validação de schema não vê erro semântico; o verificador semântico cobre a lacuna.
- O exemplo converte falha de parse em `{}`, mas isso **não é seguro no portão
  mostrado**: não sobram verificações por campo. Ao adaptar, tratar erro estrutural
  e campos obrigatórios ausentes explicitamente antes de aceitar o registro.
- Não misturar a cabeça holística no portão (0,56 no exemplo; o doc a mostra só para contraste com um juiz "bruto" do registro inteiro) → sinal por campo concentra o erro no campo errado ("calibrado: alto no errado, baixo no certo, médio no que parece estranho sem ser claramente errado").
- Varrer o limiar do portão e plotar custo x qualidade → escolher o ponto operacional na fronteira de Pareto.
- Ids `campo::métrica` em uma chamada só → juntar toda a bateria do registro.

## Limites e pegadinhas
- O exemplo foi de uma linha em que o correto é vazio; o registro do mini é fixado à mão por ser instável.
- Resultados de 100 prompts são internos, sem tabela no texto; custos do gráfico são históricos, não recalculados pelo preço atual.
- `FIRE_T = 0.7` é um único valor por cascata; o doc faz varredura, sem recomendar um valor geral.
- Só dois degraus (mini e raciocínio); cabeças `spurious` e `difficulty` do pipeline completo não são mostradas.
- (Observação sobre o código, não sobre o texto do doc) o comentário em `extract` diz que, após falha de parse, "cada campo parece ausente, o que o verificador sinaliza e o portão escala", mas `build_questions` itera os campos de `record` e `{}` não tem campos: só sobra `__overall__::judge`, que o portão exclui. Nesse caso o portão aceitaria; o doc não trata isso.
  Conferido estaticamente pelo Codex no snapshot da página `sde_cascade.md`: `extract` devolve `{}` após
  erro de parse (linhas 303–306), `build_questions` percorre só `record.items()` (460–468), o portão exclui
  `__overall__` (559–565). Ao adaptar: tratar falha estrutural antes do julgamento, verificar os campos
  exigidos pelo schema mesmo quando faltam no registro, e nunca converter falha em aceitação. Não
  executamos a cascata nem o endpoint.
- A instalação listada (`pip install openai datasets jsonschema ipython cooksafe`) não inclui o cliente TypeSafe; o doc diz que ele é servido pelo índice de pacotes da TypeSafe.

## Esqueleto de código
```python
FIRE_T = 0.7
def build_questions(record):
    qs = {"__overall__::judge": Noul(instructions=OVERALL_JUDGE, criteria=OVERALL_JUDGE_CRITERIA)}
    for name, value in record.items():
        spec = field_spec(name)        # {path, type, description, required}
        if is_empty(value):
            qs[f"{name}::absence_wrong"] = Noul(
                instructions={"field_spec": spec, "extracted_field": value,
                              "main_question": ABSENCE_QUESTION}, criteria=ABSENCE_CRITERIA)
            continue
        for metric, (question, criteria) in MAIN_QUESTIONS.items():   # 7 cabeças
            qs[f"{name}::{metric}"] = Noul(
                instructions={"field_spec": spec, "extracted_field": value,
                              "main_question": question}, criteria=criteria)
    return qs

state = {"system_message": EXTRACT_SYSTEM, "instruction": "Extract the structured record from this document",
         "source_text": content, "schema": schema, "extraction": record}
answers = ts.system_one(state=state, questions=build_questions(record), model="jev-1.12").answers
checks = {qid: a.noul for qid, a in answers.items()}
fired = {q: p for q, p in checks.items() if not q.startswith("__overall__") and p > FIRE_T}
final = extract(REASONING, prompt, schema, content, reasoning_effort="high") if fired else record
```
