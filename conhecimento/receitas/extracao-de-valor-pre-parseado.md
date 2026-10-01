---
name: extracao-de-valor-pre-parseado
description: Regex acha os candidatos (e-mail, telefone, valor), o Jev escolhe qual o texto pede via Choice cujas opções SÃO os trechos, e o código copia o valor literal e normaliza (E.164, Decimal); o valor devolvido nunca é inventado.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 9582–9895
estudado_em: 2026-09-30
---

# Extração de valor pré-parseado (Pre-parsed value extraction)

## Problema
Extrair de um documento o valor certo (o e-mail para onde mandar o recibo, o celular, o total a pagar) sem risco de o modelo inventar um valor ou trocar um dígito. O Jev escolhe UMA das opções que lhe são dadas, então os candidatos precisam existir antes. Três passos: (1) uma regex acha os candidatos, afinada para achar demais; (2) o Jev escolhe qual candidato a pergunta pede e lê atributos de que o código precisa adiante (moeda, país, se é crédito ou cobrança); (3) o código copia o valor escolhido e o normaliza. Como o Jev só escolhe entre trechos que a regex achou, o valor devolvido é um desses trechos, copiado sem alteração.

## Como o Jev entra
- **state:** o texto do documento (string pura, `state=document`). Nos três casos o doc é curto (e-mail com cabeçalhos; parágrafo com 3 telefones; fatura de 5 linhas).
- **perguntas:** três helpers, todos uma pergunta por chamada, model `jev-1.12`:
  - `pick(document, candidates, question)` → `Choice(instructions=question, criteria={c: None for c in candidates} | {"none": "None of these is the requested value."})`. A pergunta é `"pick"`; devolve `{choice, confidence}` (`answer.choice`, `answer.confidence`). As opções são os trechos literais (criteria com valor `None`, sem descrição) mais a válvula de escape `none` (constante `NONE = "none"`, presente em toda seleção).
  - `classify(document, question, options)` → `Choice` sobre rótulos fixos (`criteria={o: None for o in options}`); devolve `{choice, confidence}`.
  - `is_true(document, question)` → `Noul(instructions=question)`; devolve `answer.noul` = P(sim).
- **regex candidatos (recall alto, dedupe por ordem do documento em `find`):**
  - `EMAIL_RE = [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`
  - `PHONE_RE = \(?\+?\d[\d\s()\-.]{6,}\d`
  - `MONEY_RE = [$€£¥]\s?\d[\d,]*(?:\.\d{2})?`
- **chamadas por caso (todas sequenciais, não agrupadas no doc):**
  - E-mail: 2 `pick`. Doc: `From: Dana Whit <dana.whit@acme-corp.com>`, `To: billing@acme-corp.com`, `Cc: orders@acme-corp.com`, `Reply-To: dana.personal@gmail.com`, corpo pedindo para não usar o alias de cobrança e mandar o recibo para o endereço pessoal. Perguntas: "Which email address does the sender want their receipt sent to?" e "Which email address did this message come from (the From line)?".
  - Telefone: 1 `pick` ("Which of these is the direct mobile / cell number?") + 1 `classify` ("In what country is this office located?", opções `["US","GB","DE","FR","CA","AU"]`). Texto: escritório de San Francisco com "main desk (415) 555-0199, billing fax (415) 555-0142, and my direct cell (415) 555-0177".
  - Dinheiro: 1 `classify` de moeda ("What currency are these amounts in?", `["USD","EUR","GBP","JPY","CAD"]`) + 2 `pick` ("Which amount is the total the customer must pay?" / "Which amount is the courtesy credit that was applied?") + 1 `is_true` por valor escolhido: `f"Is the amount {chosen['choice']} a credit or refund to the customer, not a charge?"`. Fatura: Subtotal $1,200.00, Sales tax $115.50, Total due $1,315.50, crédito de cortesia $50.00 "already been applied".

## O que o código faz com a resposta
- E-mail: copia `choice` e faz `.lower()` (nunca redigita).
- Telefone: `phonenumbers.parse(mobile["choice"], region["choice"])` e `format_number(..., E164)`; o país vem do Jev, o formato do código.
- Dinheiro: `to_decimal` = `Decimal(re.sub(r"[^\d.]", "", value))` (supõe vírgula = milhar e ponto = decimal); `kind = "credit" if is_credit > 0.5 else "charge"` (limiar 0,5 do `is_true`).
- Nenhum limiar é aplicado sobre `confidence` no doc: é só impresso.

## Resultados medidos
Sem medição agregada; três exemplos únicos, `jev-1.12`:

| caso | candidatos achados | escolhido | confiança / P |
|---|---|---|---|
| e-mail recibo | dana.whit@acme-corp.com, billing@acme-corp.com, orders@acme-corp.com, dana.personal@gmail.com | dana.personal@gmail.com | 0,98 |
| e-mail remetente | (os mesmos 4) | dana.whit@acme-corp.com | 1,00 |
| telefone celular | (415) 555-0199, (415) 555-0142, (415) 555-0177 | (415) 555-0177 | 1,00 |
| país | lista fixa | US | 0,90 |
| E.164 | | +14155550177 | |
| total devido | $1,200.00, $115.50, $1,315.50, $50.00 | $1,315.50 → 1315.50 USD, charge | P(credit)=0,01 |
| crédito | (os mesmos 4) | $50.00 → 50.00 USD, credit | P(credit)=0,99 |

Custo e latência: não declarados no doc.

## Técnicas reutilizáveis
- Transformar extração em seleção: as opções do `Choice` SÃO os trechos candidatos → o valor é sempre cópia literal, sem invenção nem dígito trocado.
- Regex com recall alto (achar demais) + Jev para o julgamento → quando o formato é regular mas o papel (quem é o remetente, qual é o celular) só se lê pelo contexto.
- Válvula de escape `none` em toda seleção → quando nenhum candidato pode servir; o código trata `none`.
- Ler atributos com perguntas pequenas e fechadas (`Choice` de rótulos fixos para moeda/país; `Noul` para "é crédito?") e deixar a normalização em bibliotecas (`phonenumbers`, `Decimal`) → combinar julgamento do modelo com formatação determinística.
- Fronteira 0,5 sobre um Noul para virar booleano (`is_credit > 0.5`) → sinal de um valor decidido por pergunta ao Jev.
- Mesma técnica para o mesmo par `find` + `pick` em qualquer documento seu.
- Mais de 255 candidatos: estreitar em dois estágios (primeiro a seção, depois o trecho dentro dela).
- Candidatos sem regex (nomes): vêm de um cadastro, de um NER ou de um LLM que propõe; o Jev escolhe.
- Formato local do número: perguntar a um Noul qual convenção o documento usa (`$1,315.50` vs `€1.315,50`) e ramificar no código.

## Limites e pegadinhas
- `Choice` aceita no máximo 255 opções.
- Achar os candidatos é a parte que dá trabalho; para nome não há regex.
- `to_decimal` assume milhar com vírgula e decimal com ponto; em `€1.315,50` é o contrário.
- As perguntas de moeda/crédito/papel são chamadas separadas; o doc não as agrupa (a receita de perguntas em paralelo mostra como juntar).
- A `confidence` do Choice não é usada como portão aqui.
- A receita depende de `phonenumbers` além do SDK; chave ausente → `"cache-only"` (só reproduz cache).

## Esqueleto de código
```python
NONE = "none"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def find(pattern, text):                      # regex afinada para achar demais
    seen, out = set(), []
    for m in pattern.findall(text):
        s = m.strip()
        if s and s not in seen:
            seen.add(s); out.append(s)
    return out

def pick(document, candidates, question):     # as opções SÃO os trechos
    criteria = {c: None for c in candidates} | {NONE: "None of these is the requested value."}
    a = ts.system_one(state=document,
                      questions={"pick": Choice(instructions=question, criteria=criteria)},
                      model="jev-1.12").answers["pick"]
    return {"choice": a.choice, "confidence": a.confidence}

emails = find(EMAIL_RE, EMAIL_DOC)
receipt = pick(EMAIL_DOC, emails, "Which email address does the sender want their receipt sent to?")
print(receipt["choice"].lower(), receipt["confidence"])   # cópia literal, normalizada no código
```
