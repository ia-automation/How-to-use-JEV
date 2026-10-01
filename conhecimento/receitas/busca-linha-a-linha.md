---
name: busca-linha-a-linha
description: Busca semântica em documento de 218 linhas com 1 requisição (Choice sobre os ids de linha + Noul "existe resposta?"), separando resposta direta (exists >= 0.7), parcial e ausente (< 0.35).
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/semantic_find.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 11111–11408
estudado_em: 2026-09-30
---

# Busca linha a linha (Line-by-line search)

## Problema
Há um documento (Termos de Serviço do GitHub, 218 cláusulas, 43.980 caracteres) e uma pergunta em linguagem comum. Quer-se (a) as linhas que respondem, citáveis, e (b) saber quando o documento NÃO responde. Resultado: `find()` devolve a probabilidade `exists` e um score de relevância por linha. Problema central: probabilidades de Choice somam 1, então alguma linha sempre fica em primeiro, mesmo sem resposta no texto.

## Como o Jev entra
- **state:** uma string única, o documento inteiro com cada linha prefixada por id: `f"{line_id(i)}| {line}"`, com `line_id(i) = f"L{i:03d}"` (L000, L001, ...), unidas por `\n`. O state NÃO muda entre buscas; a pergunta do usuário vai em `instructions`.
- **perguntas:**
  - `where` — **Choice**. `instructions`: `Which line of the document contains the answer to: "{query}"?`. `criteria`: `{line_id(i): None for i in range(len(LINES))}` (descrição `None`, pois o texto de cada id já está no state). Limite declarado: Choice aceita até 255 opções.
  - `exists` — **Noul**. `instructions`: `Does any line of the document address or answer: "{query}"?`. `criteria=NoulCriteria(true="At least one line of the document states or directly implies the answer", false="No line of the document addresses this")`.
- **chamadas:** 1 só (`client.system_one(state=..., questions={"where": ..., "exists": ...}, model="jev-1.12")`). O state vai uma vez; a checagem de existência custa "pouca saída extra". Nada em paralelo além das duas perguntas na mesma requisição.

Leitura: `response.answers["where"].probabilities` (dict id -> prob; `.get(id, 0.0)` para ids ausentes) e `response.answers["exists"].noul` (float).

## O que o código faz com a resposta
- `relevance`: lista com um score por linha, em ordem do documento. Ranking = ordenar por score desc.
- Limiares: `FOUND, ABSENT = 0.7, 0.35`; comentário do doc: "present answers typically read >=0.9, absent <=0.05".
  - `exists >= 0.7` -> "answered in this document"
  - `exists < 0.35` -> "not in this document"
  - entre os dois -> "partially addressed"
- O doc avisa: os limiares separam os exemplos dados; "tune them against your own documents before using them in production".
- Documento > 255 linhas: duas passadas — um Choice escolhe uma janela de linhas, um segundo ranqueia as linhas dentro dela.

## Resultados medidos
Quatro consultas de demonstração (sem modelo de comparação; só o jev-1.12):

| consulta | exists | veredito | linha 1 (score) |
|---|---|---|---|
| who owns the code I upload? | 0.98 | respondida | L052 (0.95) |
| can GitHub kick me off the platform without warning? | 0.97 | respondida | L168 (0.97) |
| do I have to take disputes to arbitration? | 0.14 | ausente | L205 (0.86) |
| can minors use GitHub with parental permission? | 0.46 | parcial | L029 (0.90) |

Custo e latência: não declarados no doc para esta receita.

## Técnicas reutilizáveis
- "Apontar em vez de gerar": prefixar itens com id curto e fazer Choice sobre os ids -> "escolher opção" vira "apontar linha"; quando precisar citar/verificar trecho.
- Opções com descrição `None` quando o state já contém o texto de cada opção -> evita repetir conteúdo em state e criteria.
- Par Choice + Noul na mesma requisição: Choice dá "onde" (relativo, soma 1), Noul dá "se" (absoluto, pode ir perto de 0) -> quando o ranking sempre devolveria um vencedor.
- Choice alto com Noul baixo = linha mais próxima, não resposta.
- Três estados em vez de binário (respondida / parcial / ausente) com dois limiares, em código local.
- State fixo + pergunta variável em `instructions` -> várias consultas sobre o mesmo documento sem reformatar o state.
- Cache de respostas (`JsonCache`) para reexecutar sem chave e sem custo.

## Limites e pegadinhas
- Choice máximo de 255 opções por pergunta (declarado); documento de 218 linhas cabe.
- Choice sempre soma 1: sozinho não detecta ausência (arbitragem: 0.86 na linha mais próxima com exists 0.14).
- Limiares calibrados só nos 4 exemplos; o doc manda ajustar no seu documento.
- O comentário do código diz "absent <=0.05", mas o caso ausente (arbitragem) leu 0.14; o limiar 0.35 é que o cobre.
- Caso parcial (0.46): a linha de idade mínima ranqueia primeiro (0.90) mas não responde se a permissão dos pais muda a regra.

## Esqueleto de código
```python
TYPESAFE_MODEL = "jev-1.12"
def line_id(i): return f"L{i:03d}"
DOCUMENT = "\n".join(f"{line_id(i)}| {line}" for i, line in enumerate(LINES))

def where_question(query):
    return Choice(
        instructions=f'Which line of the document contains the answer to: "{query}"?',
        criteria={line_id(i): None for i in range(len(LINES))})

def exists_question(query):
    return Noul(
        instructions=f'Does any line of the document address or answer: "{query}"?',
        criteria=NoulCriteria(
            true="At least one line of the document states or directly implies the answer",
            false="No line of the document addresses this"))

response = client.system_one(
    state=DOCUMENT,
    questions={"where": where_question(q), "exists": exists_question(q)},
    model=TYPESAFE_MODEL)
probs = response.answers["where"].probabilities
relevance = [probs.get(line_id(i), 0.0) for i in range(len(LINES))]
exists = response.answers["exists"].noul

FOUND, ABSENT = 0.7, 0.35
def verdict(e):
    if e >= FOUND: return "answered in this document"
    return "not in this document" if e < ABSENT else "partially addressed"
```
