---
name: recuperacao-de-estrutura
description: Reconstrói Markdown de texto puro sem formatação em 2 requisições (costura de linhas + classificação de blocos); memo de 28 linhas vira 17 blocos em 0,8 s e 10.211 tokens, sem o modelo gerar uma palavra.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/autoformat.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 1338–1986
estudado_em: 2026-09-30
---

# Recuperação de estrutura (Structure recovery)

Contexto do índice "Cookbooks" (linhas 1271–1338, sem nota própria): é a seção de receitas de ponta a ponta, pressupõe primitivos e confiança lidos antes. Agrupa: Self-consistency (nouls, choices), Batching (Parallel questions: 13 perguntas em 1 chamada, 12,2x mais barato e 10,0x mais rápido), How-to (Re-ranking 5%→18% top-1 e 38%→62% top-10; Line-by-line search com 218 ids; **Structure recovery** nível Beginner; Function calling; Skill suggestion com 182 skills do Hermes; Entity alignment com 450 pares; Classifying RAG passages; Citation check; LLM guardrails), Extraction (SDE cascade, Date extraction, Pre-parsed value extraction), Classification (Hierarchical classification, Autoresearch feature discovery nível Advanced, Classification using confidence com 75 grupos SEC).

## Problema
Texto cujo markup foi removido: linhas quebradas no meio da frase, sem marcadores de título, sem bullets, comando de shell numa linha solta, aviso sem marcação. Reescrever com um modelo gerador pode alterar as palavras. Aqui o modelo **nunca gera texto**: responde perguntas estreitas sobre o documento e o código renderiza, então todo caractere da saída vem da entrada e cada julgamento carrega probabilidade. Documento de teste: memo de migração de build system (28 linhas não vazias).

## Como o Jev entra
Pipeline de 2 requisições **em sequência** por documento (a 2ª depende do resultado da 1ª, porque os blocos só existem depois da costura).

- **state:** o texto com ids de linha no próprio texto, formato `L014| texto`. Linhas em branco do original viram uma linha vazia extra antes da linha seguinte (marca `gap`); em código, `to_lines` normaliza espaços/tabs (`[\t ]+` → um espaço), descarta vazias e marca `gap=True` na linha seguinte a uma vazia (vazia inicial não conta). Pass 2 usa o mesmo esquema com prefixo `B` (`B000| ...`) sobre os blocos costurados. Os ids são texto comum que o modelo lê; perguntas e respostas referem as linhas por eles (mesmo esquema da receita semantic_find).
- **perguntas, Pass 1 (Noul, uma por par de linhas adjacentes, chave = id da linha `L001`…):**
  - instructions: `Does line {Lii} pick up mid-sentence, continuing a sentence left unfinished at the end of line {Lii-1}?`
  - criteria.true: `The line starts in the middle of a sentence that began on the previous line - the line break tore the sentence apart`
  - criteria.false: `The line begins a new sentence, item, heading, or thought of its own`
  - Pares separados por linha em branco (`gap`) **não são perguntados**. No memo: 16 perguntas, 1 requisição, 0,32 s.
- **perguntas, Pass 2 (por bloco `Bnnn`, todas na mesma requisição):**
  - `type_Bnnn` Choice: `What kind of content is block {Bnnn}?` com 6 opções (texto literal dos critérios):
    - heading: `A short label or title that names the document or the section that follows it - not a full sentence of content`
    - paragraph: `Running prose: one or more complete sentences of explanatory or narrative text`
    - list_item: `One entry in a list of parallel items - an ingredient, a feature, a task, an attendee; reads as one of several sibling entries`
    - quote: `Words attributed to a person or source - quoted speech, a citation, an excerpt someone else wrote`
    - code: `Computer code, a shell command, terminal output, or a config snippet meant to be read verbatim`
    - callout: `A warning, tip, or important note that interrupts the flow to flag something the reader must not miss`
  - `hlevel_Bnnn` Choice (só se o bloco tem ≤ 90 caracteres, `HEADING_MAX_CHARS=90`): `As a heading, what level would block {Bnnn} occupy in this document's structure?` com title (`The title of the whole document`), section (`A major section heading within the document`), subsection (`A minor heading nested under a section`).
  - `step_Bnnn` Noul: `Is block {Bnnn} an instruction in a sequence where the order of the items matters?` true: `It is one step of a procedure - the items around it must happen in order`; false: `Order is irrelevant - it is a loose collection, or not a list item at all`.
  - `callout_Bnnn` Choice: `What kind of aside is block {Bnnn}?` com note (`Neutral extra information the reader should be aware of`), tip (`A helpful suggestion or shortcut that makes things easier`), warning (`A caution about something that can go wrong or cause harm`).
- **chamadas:** 2 no total. Pass 1: 16 perguntas. Pass 2: 62 perguntas sobre 17 blocos (17 type + 17 step + 17 callout + 11 hlevel, já que só 11 blocos têm ≤ 90 caracteres), 0,51 s. As perguntas companheiras (nível do título, ordem, tipo de callout) são feitas **de antemão** na mesma requisição, mesmo que só se leia a resposta quando o tipo do bloco as torna relevantes; esperar o tipo custaria uma 3ª ida e volta.
- **Evidência direta fica no código:** linhas em branco e marcadores explícitos (`- `, `1.`, `#`) são lidos em código, nunca mandados ao modelo. O modelo só recebe o que o código não responde pelo texto.
- Toda a especificação do classificador = 3 dicts de descrições de uma linha + os critérios true/false da pergunta `step`. "Para adaptar a pipeline aos seus documentos, edite essas descrições."

## O que o código faz com a resposta
- **Costura (merge):** o limiar depende de como a linha ANTERIOR termina.
  - Anterior "pendurada" (sem pontuação final): junta se `join >= JOIN_AFTER_DANGLING = 0.2`.
  - Anterior com pontuação terminal (regex `[.!?:;…]` opcionalmente seguido de aspas/parêntese/colchete): junta se `join >= JOIN_AFTER_TERMINAL = 0.5`.
  - Nunca junta se a linha tem `gap`. Texto junto com um espaço. Resultado: 28 linhas → 17 blocos (11 quebras curadas).
  - Probabilidades do memo: quebras que partiram a frase pontuam de 0,39 para cima (ex.: L004 `make the switch for real.` 0,39; L002 0,77; L003 0,62; L007 0,42; L008 0,59; L011 0,48; L012 0,40; L014 0,50); quebras intencionais ficam perto de zero (L016 0,11; L017 0,12; L021 0,05). Exceção instrutiva: L015 `The platform team`, que vem depois de `:`, pontua 0,22 e passaria o corte de 0,2 fundindo a lista na frase que a introduz; por isso o corte sobe a 0,5 após pontuação. "Nenhum limiar único serve aos dois casos; quando o código checa a pontuação antes, as duas faixas se separam." Um corte único e cauteloso de 0,5 quebraria parágrafos saudáveis (L004 = 0,39).
- **Classificação:** tipo = `.choice` da pergunta `type_`; `confidence` e `probabilities` ficam guardados. Só se lê o companheiro relevante: heading → `hlevel` (se não foi perguntado por ter > 90 caracteres, padrão `"section"`); list_item → `step`; callout → `callout`.
- **Renderização (código puro):**
  - Agrupa blocos consecutivos de `list_item` e de `code` (um grupo só); os demais tipos não se agrupam.
  - Lista é numerada se a **média** das probabilidades `step` dos itens ≥ `STEP_THRESHOLD = 0.5` (decisão de grupo que nenhuma pergunta pediu diretamente); senão, bullets `- `.
  - heading: `#` title, `##` section, `###` subsection. code: cerca de três crases. quote: `> `. callout: `> [!WARNING]` (ou NOTE/TIP) + linha `> texto`. paragraph: texto cru. Partes separadas por linha em branco.
- **Revisão humana (sugestão do doc):** sublinhar para revisão todo bloco cuja confiança do tipo vencedor fique abaixo de 0,55.

## Resultados medidos
| métrica | linha de base | com Jev | custo | latência |
| - | - | - | - | - |
| blocos costurados | 28 linhas | 17 blocos (11 quebras curadas) | Pass 1: 16 perguntas | 0,32 s |
| classificação | — | 17 blocos, 62 perguntas | Pass 2 | 0,51 s |
| total (modelo `jev-1.12`) | — | 2 idas e voltas, 10.211 tokens | texto do doc: $0,0015 (a saída impressa mostra $0,0003) | 0,8 s |
| pergunta "mesmo parágrafo" (naive) | — | 12 blocos (listas colapsam) | — | — |
| pergunta "meio de frase" | — | 17 blocos | — | — |

Preço usado no código: `PRICE = (0.042, 0.00)` US$ por 1M tokens (entrada, saída), `jev-1.12` em 2026-09.

Classificações do memo (tipo, confiança, companheiro lido): B000 heading 0,99 level=title; B001 paragraph 0,98; B002 heading 0,75 level=section; B003 paragraph 0,89; B004 code 1,00; B005 paragraph 0,90; **B006 paragraph 0,43** (frase que introduz a lista de times, a menos confiante: paragraph 0,53, list_item 0,24, callout 0,19); B007–B009 list_item 0,99/1,00/0,99 com step 0,15/0,16/0,12 (bullets); B010 heading 0,96 section; B011–B013 list_item 0,98/0,99/0,92 com step 0,86/0,87/0,90 (numerada); B014 callout 0,65 kind=warning; B015 quote 0,99; B016 paragraph 0,92.

## Técnicas reutilizáveis
- **Modelo julga, código renderiza** ("reescrever" → quando o conteúdo não pode mudar: o modelo só responde perguntas, o texto sai byte a byte da entrada).
- **Id no texto do state** (`L014| ...`) → quando perguntas e respostas precisam apontar para pedaços do documento sem copiar o trecho.
- **Uma pergunta Noul por par adjacente, todas numa requisição** → quando a decisão é local (juntar/separar) e o custo marginal de mais uma pergunta é quase zero porque o state, que domina os tokens, vai uma vez só.
- **Perguntar o fato mais estreito que decide o limiar**: "esta linha retoma no meio da frase?" em vez de "as duas linhas são do mesmo parágrafo?". Quando um julgamento alimenta um limiar, nomeie o fato do texto, não o tema.
- **Limiar condicionado a um fato que o código lê** (pontuação final da linha anterior) → quando nenhum corte único separa as faixas de probabilidade; 0,2 vs 0,5.
- **Perguntas companheiras de antemão** → quando a pergunta relevante depende do resultado de outra, pergunte todas na mesma requisição e leia só a aplicável; ignorar respostas é grátis, uma ida e volta a mais custa latência inteira.
- **Não perguntar o que já é evidente** (marcadores, linhas em branco, limite de 90 caracteres para título) → poupa perguntas e evita que o modelo reconsidere um fato direto.
- **Agregar probabilidades por grupo em código** (média do `step` dos itens contra 0,5) → decisões de grupo que nenhuma pergunta individual formulou.
- **A especificação é só descrições de opção**: adaptar a novo domínio = editar os dicts de critérios.
- **Usar a confiança do tipo vencedor como gatilho de revisão humana** (< 0,55).
- **Inspecionar a menos confiante** (`min` por confiança + 3 maiores probabilidades) para achar ambiguidade genuína.

## Limites e pegadinhas
- A 1ª versão do pipeline usava "são do mesmo parágrafo?" e falhou: itens de lista sem bullet "são" um parágrafo no sentido frouxo (ficam juntos e compartilham tema), todo par pontuou acima de 0,75 (L015 0,77; L016 0,81; L017 0,78; L020 0,88; L021 0,91) e as duas listas colapsaram: 12 blocos contra 17.
- Um bloco genuinamente ambíguo existe (B006, confiança 0,43); o doc não o corrige, sugere apenas sinalizá-lo.
- Um corte único de costura não funciona (ver acima); a pontuação precisa ser lida em código.
- Só 1 documento de teste (memo de 28 linhas); o doc não mede acurácia, nem compara com um gerador.
- Perguntas de companheiros inúteis são respondidas e descartadas (a maior parte delas nunca é lida).
- Cache: toda chamada é cacheada em `json_cache.json` (vem com o cookbook); apagar para rodar ao vivo. Requer `TYPESAFE_API_KEY`, `pip install ipython 'cooksafe>=0.2.0,<0.3.0'`.

## Esqueleto de código
```python
TYPESAFE_MODEL = "jev-1.12"
client = TypeSafeClient(api_key=os.environ["TYPESAFE_API_KEY"], timeout=120.0)

def join_question(i):
    return Noul(
        instructions=f"Does line {line_id(i)} pick up mid-sentence, continuing a sentence left unfinished at the end of line {line_id(i - 1)}?",
        criteria=NoulCriteria(
            true="The line starts in the middle of a sentence that began on the previous line - the line break tore the sentence apart",
            false="The line begins a new sentence, item, heading, or thought of its own"))

# Pass 1: um Noul por par sem linha em branco no meio, tudo numa requisição
questions = {line_id(i): join_question(i) for i in range(1, len(LINES)) if not LINES[i]["gap"]}
r = client.system_one(state=tag(LINES, "L"), questions=questions, model=TYPESAFE_MODEL)
joins = [r.answers[line_id(i)].noul if line_id(i) in r.answers else 0.0 for i in range(len(LINES))]

JOIN_AFTER_DANGLING, JOIN_AFTER_TERMINAL = 0.2, 0.5
bar = JOIN_AFTER_TERMINAL if i and ends_terminal(LINES[i-1]["text"]) else JOIN_AFTER_DANGLING
merge = blocks and not line["gap"] and joins[i] >= bar

# Pass 2: por bloco, type + (hlevel se <= 90 chars) + step + callout, tudo junto
q[f"type_{bid}"] = Choice(instructions=f"What kind of content is block {bid}?", criteria=TYPE_CRITERIA)
q[f"step_{bid}"] = Noul(instructions=f"Is block {bid} an instruction in a sequence where the order of the items matters?", criteria=NoulCriteria(true="...", false="..."))
r = client.system_one(state=tag(blocks, "B"), questions=q, model=TYPESAFE_MODEL)
a = r.answers[f"type_{bid}"]; a.choice, a.confidence, a.probabilities
r.answers[f"step_{bid}"].noul   # lista numerada se a média do grupo >= 0.5
```
