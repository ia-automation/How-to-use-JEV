---
name: extracao-de-datas
description: Extrai datas absolutas e relativas com 7 Choices em uma chamada (Jev só lê as partes; o código faz a matemática de calendário) e manda para revisão o que tiver confiança < 0,60; 5 de 6 exemplos aceitos, 1 corretamente barrado com 0,46.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/date_extraction_cookbook.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 6737–7151
estudado_em: 2026-09-30
---

# Extração de datas (Date extraction)

## Problema
Dado um documento e uma frase que nomeia a data desejada ("the deadline to return the form"), devolver uma `date` mais uma confiança. Deve sinalizar leitura de baixa confiança e partes que não formam data, inclusive data que o documento nunca declara. A data pode ser escrita ("August 14, 2027") ou relativa a hoje ("tomorrow", "next Thursday"). Princípio: o modelo lê o que o texto diz; nunca faz conta de calendário.

## Como o Jev entra
- **state:** o documento como string (`state=document`).
- **perguntas:** 7 `Choice` em UMA chamada, geradas por `date_questions(role)` (`role` = a frase que nomeia a data). Texto literal entre aspas; `absent` = "The document does not state this, or it is not this kind of date."
  - `mode`: "How is {role} written? 'absolute' = a calendar date naming a month (e.g. 'August 14', 'the 3rd of March'); 'relative' = given relative to today (today, tomorrow, the day after tomorrow, or a named weekday such as 'next Thursday'); 'none' = the document does not state this date." Opções: `absolute`, `relative`, `none` (sem descrição).
  - `month`: "If {role} is an absolute calendar date, which month is it in?" Opções: January…December + `none` (absent).
  - `day`: "If {role} is an absolute calendar date, which day of the month (1-31)?" Opções: "1"…"31" + `none`.
  - `year`: "If {role} is an absolute calendar date, which year? Pick 'none' if the document states no year (code infers it), or 'out_of_range' if a year is stated but not in the list." Opções: "1900"…"2050" (151 opções) + `out_of_range` ("A year is stated for this date but is outside the listed range.") + `none` ("No year is stated for this date.").
  - `day_anchor`: "If {role} is relative to today, which day is it? 'today', 'tomorrow', 'day_after' (the day after tomorrow), or 'weekday' (a named day of the week)." Opções: `today`, `tomorrow`, `day_after`, `weekday`, `none`.
  - `weekday`: "If {role} names a day of the week, which one?" Opções: Monday…Sunday + `none`.
  - `week_offset`: "If {role} names a weekday, which week is it in? 'next' for 'next Thursday' or 'Thursday next week'; 'current' for 'this Thursday'; 'none' for a bare weekday with no qualifier (just 'Thursday' / 'on Thursday')." Opções: `current`, `next`, `none`.
- **chamadas:** 1 por (documento, role). Cada resposta volta como `{choice, confidence}`. Modelo `jev-1.12`. O código só lê as partes que o `mode` exige (absoluta: month/day/year; relativa: day_anchor e, se weekday, weekday+week_offset).

## O que o código faz com a resposta
- `TODAY` fixo em `date(2026, 7, 30)` (quinta) para reprodutibilidade. `REVIEW_BELOW = 0.60`.
- Confiança da data = `min` das confianças das partes efetivamente usadas (começa com a de `mode`; soma month/day/year, ou day_anchor, ou weekday/week_offset). Uma parte fraca manda a data inteira para revisão.
- `needs_review = data é None OU confiança é None OU confiança < 0,60`.
- `mode == "none"` → data None, nota "no such date stated".
- Absoluta:
  - `month` ou `day` = `none`, `day` não numérico ou mês fora de MONTHS → None, "absolute date incomplete".
  - `year == "out_of_range"` → None ("year outside 1900-2050"): sinaliza, não adivinha.
  - `year == "none"` → usa o ano de `TODAY`; se a data resultante for anterior a `today - 31 dias`, usa o ano seguinte. Data impossível (ex.: 30 de fevereiro) → `ValueError` → None, "impossible date: ...".
  - Ano declarado → `date(int(year), mês, dia)`; `ValueError` → None, "impossible date".
- Relativa: `today` → hoje; `tomorrow` → +1; `day_after` → +2; `weekday` → `resolve_weekday`; outro → None ("relative day not read"); weekday fora da lista → None.
- `resolve_weekday` (convenção declarada no código): `this_monday = today - weekday()`; `week_offset == "next"` → segunda atual + 7 + w (semana seguinte); `"current"` → segunda atual + w (esta semana); `none` (dia da semana pelado) → próxima ocorrência em/depois de hoje: `today + ((w - today.weekday()) % 7)`. O texto avisa que "next Thursday" tem dois sentidos possíveis e quem decide é o código.
- Dica do doc: se a lista de 151 anos incomoda, extrair do texto os números parecidos com ano e oferecer só esses ao modelo.

## Resultados medidos
(`TODAY` = 2026-07-30; 4 documentos, 6 perguntas; todos OK contra o esperado)
| Pergunta | Esperado | Obtido | Confiança | Destino |
|---|---|---|---|---|
| data em que o contrato entra em vigor (CONTRACT: "effective January 1, 2025 and expires December 31, 2027") | 2025-01-01 | 2025-01-01 | 0,97 | aceita |
| data em que o contrato expira | 2027-12-31 | 2027-12-31 | 0,91 | aceita |
| prazo para devolver o formulário (FORM: "by August 14.") | 2026-08-14 | 2026-08-14 | 0,95 | aceita (ano 2026 preenchido pelo código) |
| data da chamada de kickoff (FORM não menciona) | none | none | 0,46 | revisão ("absolute date incomplete") |
| fechamento da pesquisa (SURVEY: "closes today at 5pm") | 2026-07-30 | 2026-07-30 | 0,94 | aceita |
| review de design (REVIEW: "next Thursday") | 2026-08-06 | 2026-08-06 | 0,92 | aceita |
Resultado: 5 aceitas automaticamente, 1 para revisão. No caso do kickoff o `mode` voltou `absolute` sem mês correspondente (há uma data no formulário, só não a pedida). Latência/custo: não declarados no doc.

## Técnicas reutilizáveis
- Perguntar ao modelo as PARTES (forma + componentes) e montar o valor em código → quando a saída exige aritmética/calendário/regra determinística que o modelo erraria.
- Pergunta de "modo" com saída `none` para "o documento não diz isso" → quando o item pode não existir; evita alucinar valor.
- Opção-válvula em listas fechadas (`none` = não declarado, `out_of_range` = declarado fora da lista) → o código sinaliza em vez de chutar.
- Confiança do composto = mínimo das confianças das partes usadas (só as que o ramo consumiu) → uma parte fraca derruba o todo; não multiplicar.
- Falha estrutural do código (partes que não fecham uma data) também vai para revisão, não só confiança baixa → dois portões em `needs_review`.
- Convenção de ambiguidade decidida em código e documentada (bare weekday / next / current) → quando a linguagem natural admite duas leituras.
- Data de referência ("hoje") injetada como parâmetro fixo → resolução relativa reprodutível e testável.
- Funções puras de resolução (`resolve_weekday`, `assemble`) separadas da chamada → teste unitário da matemática sem a API.
- Parafrasear o que se quer por `role` dentro de cada pergunta → mesmo conjunto de perguntas serve a qualquer data do documento.

## Limites e pegadinhas
- O texto reconhece lista de 151 anos como possível incômodo (sugere pré-filtrar números tipo ano).
- Regra "ano ausente": ano corrente, próximo ano só se já passou mais de ~1 mês (31 dias); é convenção do código, não do modelo.
- Confiança 0,60 é limiar do cookbook (não declarado como calibrado para outros dados).
- Só 6 exemplos; não há taxa de acerto em escala.

## Esqueleto de código
```python
@json_cache
def read_parts(document: str, role: str) -> dict:
    answers = client.system_one(
        state=document, questions=date_questions(role), model="jev-1.12"
    ).answers
    return {p: {"choice": a.choice, "confidence": a.confidence} for p, a in answers.items()}

def resolve_weekday(today, weekday, week_offset):
    w = WEEKDAYS.index(weekday)
    this_monday = today - timedelta(days=today.weekday())
    if week_offset == "next":    return this_monday + timedelta(days=7 + w)
    if week_offset == "current": return this_monday + timedelta(days=w)
    return today + timedelta(days=(w - today.weekday()) % 7)

# dentro de assemble(): confs = [mode.confidence, + partes usadas]
# confidence = min(confs); needs_review = resolved is None or confidence < 0.60
```
