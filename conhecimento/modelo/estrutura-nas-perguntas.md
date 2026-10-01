---
name: estrutura-nas-perguntas
description: instructions e criteria aceitam objeto/array (EntryType) — pergunta num campo, dado em outros; critérios contrastivos what/not_for/examples; subárvore como valor de opção para andar taxonomia.
tipo: conceito
fonte: https://docs.typesafe.ai/primitives/advanced · /concepts/how-to-build-with-system-one#use-structure-in-the-questions
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 574–606 e 13616–13694; exemplos completos em fontes/docs/paginas/primitives/advanced.md
estudado_em: 2026-09-30
---

# Estrutura nas perguntas

## Onde cabe estrutura

`EntryType` do JS inclui string, objeto, array e null. O OpenAPI v0.2.0 diverge
para níveis de Score: aceita string/objeto/array, sem null. Não transportar o tipo
JS como contrato universal; usar descrições não nulas nos níveis.
| Campo | Tipo de pergunta |
|---|---|
| `instructions` | Choice, Score, Noul |
| valores de `criteria` (descrição de cada opção) | Choice |
| entradas de `criteria` (descrição de cada nível) | Score |
| `criteria.true` / `criteria.false` | Noul |

**Comece com string.** Estruture quando separa orientação que de outro jeito se mistura.

## Quando estruturar
1. A pergunta precisa de contexto ou exemplos → campos nomeados ao lado da pergunta, que o código
   troca sem reescrever a pergunta.
2. Parte da pergunta vem do código (linha do banco) → campo próprio, **não** interpolar em template.
3. Várias perguntas parecidas numa requisição → dado suplementar as diferencia.
4. Esquema, taxonomia ou registro que já é JSON → passar o JSON (inteiro ou os subcampos úteis).

Os nomes de campo (`question`, `focus`, `what`, `not_for`, `examples`, `inspect`, `compare`,
`signals`, `summary`, `note`…) **não são da API nem reservados** — você escolhe; o modelo vê o nome
junto com o valor, então use nomes curtos que rotulem. **Mesmos nomes em todas as opções/níveis**
para o modelo comparar igual com igual.

## Padrões com exemplo do doc
**Pergunta + dado do código (Noul de duplicata):**
```json
"instructions": {
  "potential_duplicate": {"name": "John Smith", "location": "Oakland, California", "last_employer": "Google"},
  "question": "Is the resume for the same person as `potential_duplicate`?"
}
```
Resultado: registro 18 (grafia diferente, mesmo local e empregador) 0,74; 42 (mesmo nome, outra
cidade e empregador) 0,09; 77 (nome parecido, mesmo local) 0,08.

**Instrução com foco e comparação:**
```json
"instructions": {"question": "Does the claimed sender identity conflict with the sending domain?",
                 "compare": ["ticket.sender.display_name", "ticket.sender.email"],
                 "focus": "Compare the named organization with the email domain."}
```

**Choice contrastiva (opções que se confundem):**
```json
"criteria": {
  "billing": {"what": "Charges, invoices, refunds, or subscriptions", "not_for": "Order tracking or account access",
              "examples": ["I was charged twice", "Where is my refund?"]},
  "orders":  {"what": "Order status, delivery, cancellation, or returns", "not_for": "Charges or account access",
              "examples": ["Where is my package?", "Cancel my order"]}
}
```
E `"focus": "Classify the customer's primary request, not every topic mentioned."` na instrução.

**Mesmo objeto `field` dirigindo 4 tipos (verificação de extração):** Noul "o `extracted_value` bate
com o `field` no `source_text`?"; Choice cujas opções são candidatos (`'Beaver Logistics'`,
`'Beaver Dam Logistics'`… todas `null`); Scores com faixas ("Under $1,000" … "Over $1,000,000";
"Due on receipt"/"Net 10"/"Net 30"/"Net 60"/"Net 90"). Em código: laço sobre os campos, uma pergunta
por campo, tudo numa chamada — é o que a [cascata-sde](../receitas/cascata-sde.md) faz.

**Andar taxonomia:** cada valor de opção é a **subárvore** do filho:
```json
"criteria": {
  "Sporting Goods": {"Cycling": ["Bike Bottles & Cages", "Bike Lights", "Helmets"], "Outdoor": ["Tents", "..."]},
  "Home & Kitchen": {"Drinkware": ["Water Bottles", "Travel Mugs", "Tumblers"], "Cookware": ["..."]},
  "Baby & Toddler": ["Sippy Cups", "Bottle Warmers", "Bibs"]
}
```
O modelo vê o que mora sob cada ramo antes de escolher (a garrafa de bike pode ir para dois
departamentos). Depois, nova Choice com os filhos do escolhido; `probabilities` dizem se vale
explorar os dois ramos (beam — [classificacao-hierarquica](../receitas/classificacao-hierarquica.md)). Subárvore grande → podar para filhos
diretos + amostra de folhas.

**Níveis de Score com sinais:**
```json
{"summary": "One change, clearly stated", "signals": ["A single fix or feature", "Nothing described as \"also\""]}
```
Com `"note": "Judge the number of independent changes, not the size of any one change."` na instrução.

**Noul com fronteira sutil:** `true`/`false` como objetos `what` + `examples`, e `focus` dizendo
"um pedido para ENVIAR a credencial, não para trocar/redefinir".

## Exemplos em níveis: cuidado
Exemplos **guiam** o modelo e só ajudam se parecem com suas entradas reais. No bug do Safari:
string simples 1,43 / conf 0,35; com exemplo parecido ("export fails in one browser but works in
another") 1,03 / 0,96; com exemplo sem relação 1,43 / 0,35. **Confiança maior não prova que ficou
mais certo** — escolher exemplos com nível esperado conhecido e testar em entradas separadas.

## Relacionados
No exemplo do spinner em `primitives/score.md` (935–1015), níveis textuais dão
1,11/conf 0,84; objetos `{what, examples}` dão 1,09/conf 0,87. A `legend` devolve
os objetos inteiros. O efeito é pequeno e não prova melhoria de acerto.

Na Choice contrastiva de cartões (`concepts/how-to-build-with-system-one.md`),
as alternativas setup versus limites usam `what`/`not_for` simétricos: o que
define uma exclui a outra. A simetria ajuda a explicitar a fronteira desejada.

[primitivas](primitivas.md) · [state](state.md) · [como-construir](../construir/como-construir.md)
