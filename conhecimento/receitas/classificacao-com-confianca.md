---
name: classificacao-com-confianca
description: Classifica relatórios 10-K da SEC em 75 grupos SIC com 1 Choice e, quando confidence < 0,9, reporta a divisão pai; em 60 filings, acerto útil 48/60 (80%) contra 39/60 (65%) forçando o grupo, a 1 requisição por documento.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/classification_using_confidence.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 3808–4225
estudado_em: 2026-09-30
---

# Classificação com confiança (Classification using confidence)

## Problema
Classificar a descrição de negócio (Item 1 "Business") de um relatório anual 10-K na SIC (Standard Industrial Classification): 75 grupos da indústria (major groups). A maioria dos casos é fácil; alguns não (empresa que vendeu um de dois segmentos; startup que descreve um negócio que pretende abrir). O modelo precisa escolher um grupo de qualquer forma e a resposta difícil parece igual à fácil. Normalmente separar os casos difíceis custa um segundo modelo, chamadas extras ou revisão humana.

Ideia: o `confidence` do Choice já separa as respostas confiáveis das não confiáveis; como os rótulos SIC são hierárquicos (grupo → divisão), uma resposta não confiável vira a divisão do grupo escolhido, sem segunda chamada.

## Como o Jev entra
- **state:** o texto puro do Item 1 (string, sem dict), de 700 a 2.200 palavras (média 1.438 nos 60 filings).
- **perguntas:** 1, chave `group`, tipo **Choice** com 75 opções.
  - instructions (literal): `"Which broad industry does this company operate in? Judge the company's own operations as this filing describes them."`
  - criteria: `{grupo: describe(grupo)}` para cada um dos 75 grupos (chave = 2 primeiros dígitos do código SIC, ex. "28").
  - descrição de cada grupo = título guarda-chuva do código `<grupo>00` (quando existe) + " — includes: " + até `MAX_NAMED = 8` indústrias do grupo separadas por "; ". Sem guarda-chuva, só a lista; sem lista, só o guarda-chuva. Motivo do doc: 42 dos 75 grupos têm título guarda-chuva na lista da SEC e os demais não têm nenhum; então se descreve cada grupo pelas indústrias dentro dele.
  - Exemplo: `group 20: food and kindred products — includes: meat packing plants; sausages & other prepared meat products; poultry slaughtering and processing; dairy product...`
- **chamadas:** 1 `system_one` por documento; nada em paralelo declarado. Modelo `jev-1.12`, 2026-08-12, timeout 120 s. "Um Choice funciona de forma confiável até cerca de 240 opções; 75 está bem dentro."

Taxonomia construída sem modelo a partir de `sic_codes.tsv` (lista da SEC de 2026-08-10): 444 códigos de 4 dígitos → 75 major groups (de `01` agricultura a `99` não classificável) → 10 divisões. Divisões por faixa de grupo:
- 1–9 agriculture, forestry and fishing; 10–14 mining; 15–17 construction; 20–39 manufacturing; 40–49 transportation, communications and utilities; 50–51 wholesale trade; 52–59 retail trade; 60–67 finance, insurance and real estate; 70–89 services; 91–99 public administration.

## O que o código faz com a resposta
- Lê `confidence`, não a probabilidade do vencedor: "0,45 com vice em 0,44" e "0,45 com o resto espalhado" são situações diferentes e só o `confidence` as separa.
- `CONFIDENT = 0.9`:
  - `confidence >= 0.9` → reporta o grupo (`level = "group"`);
  - abaixo → reporta a divisão do grupo vencedor (`level = "division"`), via `division(group)` (faixa numérica).
- Todo filing volta com rótulo útil; nenhum é descartado. Se a divisão for grossa demais para a aplicação, é neste ramo que se entrega a um humano (sugestão do doc).
- Pontuação: acerto do grupo contra o código do próprio filer (2 primeiros dígitos); no ramo `division`, acerto se a divisão bate com a divisão do código correto.

## Resultados medidos
60 filings (1993–2024), `jev-1.12`; gabarito = código SIC autoescolhido pelo filer (filtrado para filings cujo texto sustenta o código).

| política | acertos | observação |
|---|---|---|
| forçar um grupo sempre | 39/60 (65%) | |
| ...dos 30 com confidence ≥ 0,9 | 27/30 (90%) | |
| ...dos 30 com confidence < 0,9 | 12/30 (40%) | |
| responder grosso quando incerto | 48/60 (80%) | os 30 incertos sobem de 40% para 70% (21/30, derivado) |

- O corte de 0,9 divide os 60 exatamente ao meio (30/30).
- Mais confiantes (1,00): grupos 28 (químicos), 63 (seguro de vida), 49 (energia, gás e saneamento). Menos: 0,22 (grupo 38 → manufacturing), 0,23 (grupo 50 → wholesale trade), 0,29 (grupo 87 → services).
- Custo e latência: (não declarado no doc); só afirma "uma requisição por documento".

## Técnicas reutilizáveis
- Ler `confidence` do Choice para decidir o que fazer com a resposta, em vez de um segundo modelo ou revisão → qualquer classificação em que casos difíceis parecem iguais aos fáceis.
- Com rótulos hierárquicos, degradar para o nível pai quando a confiança é baixa, sem nova chamada → o rótulo amplo decorre do estreito; resposta menos específica e mais acertada.
- Devolver "rótulo + nível de especificidade" em vez de só o rótulo → o consumidor sabe quanto pode confiar/agir.
- Gerar as descrições das opções a partir dos filhos de cada categoria (até 8 exemplos) → quando a categoria não tem definição própria boa; é o que um leitor casaria com o texto.
- Construir os níveis da taxonomia em código a partir de um arquivo (prefixo do código + faixas), sem modelo → a hierarquia é determinística.
- Reescrever só `describe()` para a própria taxonomia e apontar `ask()` para os próprios documentos → o resto da receita é reaproveitável (palavra do doc).
- Usar como referência só o trecho relevante do documento (Item 1) → o que o rótulo realmente descreve.

## Limites e pegadinhas
- O gabarito é autorreportado e pode ficar desatualizado (empresa vende o negócio e mantém o código); os 60 foram filtrados para filings cujo texto sustenta o código, então os números medem a receita, não a qualidade dos metadados do EDGAR.
- O doc cita "Nevaeh" e "Barricode" como casos de startups em estágio de desenvolvimento e um terceiro com dois segmentos, mas não diz qual filing corresponde a qual dos três de menor confiança (não declarado no doc).
- A pergunta diz "broad industry" embora as opções sejam 75 grupos (texto do doc).
- Amostra pequena (60) e limiar 0,9 sem calibração declarada.
- Um único modelo e uma única passagem; nada sobre variância entre repetições.

## Esqueleto de código
```python
CONFIDENT = 0.9

def questions() -> dict:
    return {"group": Choice(
        instructions=("Which broad industry does this company operate in? Judge the "
                      "company's own operations as this filing describes them."),
        criteria={group: describe(group) for group in sorted(GROUPS)})}

def ask(filing_id, text):
    r = client.system_one(state=text, questions=questions(), model="jev-1.12")
    a = r.answers["group"]
    return {"group": a.choice, "confidence": a.confidence,
            "probabilities": dict(a.probabilities)}

def classify(filing):
    answer = ask(filing["id"], filing["text"])
    sure = answer["confidence"] >= CONFIDENT
    return {"level": "group" if sure else "division",
            "label": answer["group"] if sure else division(answer["group"]),
            "confidence": answer["confidence"], "group": answer["group"]}
```
