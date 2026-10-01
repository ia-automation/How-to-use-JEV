---
name: alinhamento-de-entidades
description: Decide se 450 pares candidatos de cervejas de dois catálogos são o mesmo produto com 1 Score de 3 níveis (+3 Nouls de diagnóstico) e regra de arredondamento sem limiar ajustado; resultado 360 separados, 50 para curador, 40 fundidos.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/entity_alignment.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 7152–7523
estudado_em: 2026-09-30
---

# Alinhamento de entidades em grafo de conhecimento (Knowledge graph entity alignment)

## Problema
Duas fontes descrevem coisas sobrepostas; uma triagem barata e grosseira já escolheu 450 pares candidatos (benchmark Beer da coleção Magellan: dois catálogos de cerveja raspados de sites diferentes). Falta julgar cada par. Fundir indevidamente é o erro caro (todo fato de qualquer das entidades passa a descrever a fundida; desfazer exige descobrir a origem de cada fato); perder um par só deixa duplicata. Logo o julgamento precisa de um terceiro resultado: nem seguro fundir, nem seguro descartar. Cada entidade tem 4 campos: name, brewery, style, abv. Cada par traz `known_same_as` (resposta do benchmark). O texto foi deixado como publicado (entidades HTML não convertidas, apóstrofos separados, caracteres mal decodificados), sem pré-processamento.

## Como o Jev entra
- **state:** `{"entity_a": {...}, "entity_b": {...}}` — as duas entidades no MESMO state, para as perguntas serem sobre o PAR. Exemplo: `{"name": "C N Red Imperial Red Ale", "brewery": "Redwood Lodge", "style": "American Amber / Red Ale", "abv": "8.10 %"}`.
- **perguntas (4, todas na mesma requisição):**
  - `link_state` — **Score**, "How do the two entity descriptions relate as products?", 3 níveis (`LEVELS`, índice 0→2):
    0. "They describe two different products."
    1. "They describe closely related products that may or may not be the same one: a variant, a special edition, or a name that could plausibly refer to either."
    2. "They describe one and the same product."
  - `same_name` — **Noul**: "Do the two entities state the same beer name?"
  - `same_brewery` — **Noul**: "Are the two entities from the same brewery?"
  - `same_style` — **Noul**: "Do the two entities describe the same beer style?"
  - `abv` NÃO tem pergunta: comparar dois números é aritmética, feita em código se quiser.
- **chamadas:** 1 requisição por par (450 no total; o gasto segue o número de pares, não o tamanho das fontes). `ThreadPoolExecutor(max_workers=6)` ("endpoint público limita acima de cerca de oito"). `timeout=120.0`. Modelo `jev-1.12`, números de 2026-08-11.
- Por que Score e não Noul/Choice: o Score liga um rótulo semântico (critério) a cada resultado, inclusive o do meio; um Noul faria isso só indiretamente por limiar; um Choice perderia a relação de ordem entre os três.
- Resposta lida: `link.score`, `link.probabilities`, `link.confidence`, `response.answers[k].noul` para os três Nouls; `usage.input_tokens/output_tokens` (guardam-se tokens, não custo derivado).

## O que o código faz com a resposta
- `OUTCOME = {0: "leave unlinked", 1: "curator queue", 2: "assert sameAs"}` (sameAs = forma padrão de registrar que duas entidades são a mesma coisa; escrevê-lo é a fusão).
- `route(score) = OUTCOME[min(int(score + 0.5), 2)]` — arredonda ao nível mais próximo. Pontos de corte implícitos: 0,5 e 1,5. Não há constante de limiar no arquivo; os níveis podem ser escritos antes de ver um único score.
- Os Nouls de campo (nome/cervejaria/estilo) só servem ao curador: mostram em que campo os dois discordam quando o par cai no nível do meio.
- Para outro domínio: reescrever `QUESTIONS` e `LEVELS`; o único outro código que conhece cerveja são as duas funções de impressão.
- O nível do meio deve ser redigido com cuidado: cobre variantes, edições especiais e nomes que plausivelmente servem a qualquer dos dois produtos; é ele que move pares entre curador e "não ligados".

## Resultados medidos
Exemplos (score · confiança · Nouls name/brewery/style):
| Par | Score | Confiança | Noul name | brewery | style | Rota |
|---|---|---|---|---|---|---|
| c446 Thomas Hooker Old Marley Barleywine (estilos "American Barleywine" vs "Barley Wine") | 1,94 | 0,92 | 0,97 | 0,99 | 0,81 | assert sameAs |
| c427 Frost Quake Bourbon Barrel Aged Barley Wine vs Lompoc ... Proletariat Red A | 0,03 | 0,95 | 0,02 | 0,09 | 0,08 | leave unlinked |
| c100 Belle Gueule Rousse (Brasseurs R.J. vs RJ; estilos diferentes) | 1,30 | 0,27 | 0,95 | 0,94 | 0,35 | curator queue |
| c428 Ambleside Amber Ale vs "Bridge Ambleside Amber Ale - Pomegranate & G…" | 1,10 | 0,77 | 0,63 | 0,98 | 0,74 | curator queue |

Todos os 450 pares:
| Rota | Pares | % |
|---|---|---|
| assert sameAs | 40 | 8,9% |
| curator queue | 50 | 11,1% |
| leave unlinked | 360 | 80,0% |
- Mais pares ficam perto de 0,25 que dos inteiros (modelo dá alguma probabilidade ao nível do meio quando há estilo/cervejaria parecidos). Decide o lado do corte, não a proximidade do nível.
- Perto do corte superior (1,5, o que decide fusão): 9 pares a menos de 0,1. Perto do inferior (0,5, só decide se o curador vê): 47 pares.
- Custo e latência: não declarados no doc. Acurácia contra `known_same_as`: não declarada no doc (o campo é carregado mas a comparação não é mostrada).

## Técnicas reutilizáveis
- Score ordinal com um nível por resultado de negócio (incluindo "talvez") + arredondamento ao nível mais próximo → quando quiser um roteamento de 3 vias sem limiar ajustado em dados rotulados.
- Escrever o significado de cada nível antes de ver scores; o texto do nível do meio é a alavanca de ajuste → trocar "ajuste de limiar" por "ajuste de redação".
- Nouls companheiros por campo na mesma requisição, usados só para EXPLICAR ao revisor humano onde há discordância → custo marginal quase zero, não entram na decisão.
- Campos numéricos fora do modelo (comparar em código) → não gastar pergunta em aritmética.
- Colocar ambas as entidades num único state para a pergunta ser sobre o par → julgamento relacional.
- Assimetria de custo de erro (fusão errada > duplicata) decide o desenho: o "incerto" vai para humano.
- Medir quantos pares ficam perto de cada corte para saber qual corte é arriscado (o que funde vs o que só enfileira).
- Cache por par; guardar tokens em vez de custo derivado.

## Limites e pegadinhas
- "Sem limiar ajustado": na prática os cortes 0,5/1,5 existem (vêm da redação dos níveis e do arredondamento); o doc diz que ambos "não são algo que você ajusta".
- Só 9 pares a menos de 0,1 de 1,5: a fusão automática, mesmo assim, não tem garantia de acerto declarada.
- O doc não reporta precisão/recall contra o gabarito, nem custo nem latência.
- Limite de taxa do endpoint público (~8 concorrentes).
- Texto sujo do benchmark foi mantido de propósito.

## Esqueleto de código
```python
LEVELS = [
    "They describe two different products.",
    "They describe closely related products that may or may not be the same one: "
    "a variant, a special edition, or a name that could plausibly refer to either.",
    "They describe one and the same product.",
]
OUTCOME = {0: "leave unlinked", 1: "curator queue", 2: "assert sameAs"}
QUESTIONS = {
    "link_state": Score(instructions="How do the two entity descriptions relate as products?", criteria=LEVELS),
    "same_name": Noul(instructions="Do the two entities state the same beer name?"),
    "same_brewery": Noul(instructions="Are the two entities from the same brewery?"),
    "same_style": Noul(instructions="Do the two entities describe the same beer style?"),
}
response = client.system_one(
    state={"entity_a": pair["entity_a"], "entity_b": pair["entity_b"]},
    questions=QUESTIONS, model="jev-1.12")
link = response.answers["link_state"]          # .score .probabilities .confidence
def route(score_value):                         # a regra de decisão inteira
    return OUTCOME[min(int(score_value + 0.5), len(LEVELS) - 1)]
```
