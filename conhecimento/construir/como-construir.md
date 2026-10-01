---
name: como-construir
description: Método oficial — código manda no fluxo, Jev entra só onde precisa de bom senso; 8 passos (código primeiro, state enxuto, estrutura, decompor, muitas perguntas por chamada, compor em código, rotear por incerteza) + quando fazer 2ª chamada.
tipo: conceito
fonte: https://docs.typesafe.ai/concepts/how-to-build-with-system-one · /primitives#when-one-question-depends-on-another
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 447–877 e 13589–13595; exemplos em fontes/docs/paginas/concepts/how-to-build-with-system-one.md
estudado_em: 2026-09-30
---

# Como construir com o Jev

## Três arquiteturas
| | Quem manda no fluxo | Risco |
|---|---|---|
| Software tradicional | código (primitivas confiáveis compostas) | não entende texto livre |
| Agente LLM | o modelo escolhe o próximo passo | cada laço é nova chance de sair dos trilhos |
| **Software com IA** (alvo do Jev) | **código**; o modelo só dá julgamentos atômicos | — |

System One é para **software com IA, não para agentes**: o modelo não escolhe a *sua própria* próxima
ação (no original, "its own next action") nem conduz o laço. Selecionar uma ação ou ferramenta entre opções
fechadas, a pedido do código que depois executa, é uso válido (passo 4 abaixo; receita
[function-calling](../receitas/function-calling.md)). "Código em controle; o modelo dá o bom senso
programável sobre dado não estruturado."

## Os 8 passos
1. **Código quando der.** Regra determinística fica no código (`if days_overdue > 30:
   route_to_collections(...)`). Evitar `while` de agente quando um fluxo expressa o mesmo.
2. **Decompor o state.** Só o contexto que as perguntas usam (evita distração e *context rot*). Não
   depender do conhecimento dos pesos quando sua base tem a informação atual.
3. **Estrutura no state.** JSON aninhado; apontar valores com caminho entre crases
   (`` `support.tickets[0].message` ``).
4. **Decompor as perguntas** — *"provavelmente o conceito mais importante deste guia"*. Perguntas
   explícitas, estreitas, atômicas. Pergunta ampla esconde vários julgamentos numa resposta; atômicas
   expõem cada um para inspecionar, afinar e combinar.
   - Ruim: `is_spam` = "Is `message` spam?". Bom: `requests_credentials`, `offers_unexpected_reward`,
     `creates_time_pressure`, `sender_identity_mismatch`, `link_domain_mismatch`,
     `disguises_link_destination` (cada uma apontando o campo exato).
   - Ruim: "Is `trace.tool_calls` correct?". Bom: 9 Nouls — ferramenta certa? argumento bate com o
     pedido? argumentos seguem o esquema? resultado casa com a chamada? coordenadas vêm do resultado
     anterior? data bate? unidade bate? (o exemplo pega o `unit: celsius` errado).
   - "Atômico" não é extração literal de fato nem limite de uma frase: seleção de ação limitada ou
     interpretação contextual é válida. **Não destruir a relação que está sendo julgada** ao dividir.
5. **Estrutura nas perguntas** quando ajuda ([estrutura-nas-perguntas](../modelo/estrutura-nas-perguntas.md)).
6. **Muitas perguntas por chamada** (inclusive especulativas) — é assim que se maximiza
   inteligência por dólar ([fan-out-especulativo](padroes/fan-out-especulativo.md), [perguntas-em-paralelo](../receitas/perguntas-em-paralelo.md)).
7. **Compor em código** (regras, somas ponderadas) ou usar as probabilidades como **features** de um
   modelo clássico. Sem rótulos? Gerar com ensemble de LLMs de raciocínio caros
   ([autoresearch-de-features](../receitas/autoresearch-de-features.md)).
   No exemplo de qualidade do guia: `0.4*answers_request + 0.4*citations_are_supported
   + 0.2*(1-contradicts_context)`. A inversão alinha o sentido das parcelas;
   pesos são política de aplicação, não uma probabilidade conjunta.
8. **Rotear pela incerteza.** Confiante → age; incerto → humano ou LLM caro. Testar limiares plotando
   confiança × acurácia nos seus dados ([confianca](../modelo/confianca.md)).

> "Decompor não exige mais idas e vindas: perguntas sobre o mesmo state rodam em paralelo."

## Exemplo completo do doc (triagem de ticket) — o esqueleto
- No exemplo simples do guia, `refund_policy` entra no state junto de
  `ticket_message`; a política atual vem do código. Em estado aninhado, perguntas
  apontam para caminhos como `support.tickets[0].message` e
  `commerce.orders[0].charges`, evitando depender dos IDs invisíveis das perguntas.
- Sai cedo sem modelo: `if ticket["status"] == "closed": return "no_action"`; filtra pedidos abertos em código.
- State só com o necessário: `ticket` (message, sender, links), `customer` (plan, open_orders), `policy`
  (lista de credenciais sensíveis).
- 7 perguntas numa chamada: `topic` (Choice contrastiva billing/orders/account), 5 Nouls com
  `criteria` estruturados (`requests_credentials`, `sender_identity_mismatch`, `unexpected_reward`,
  `refund_requested`, `mentions_open_order`) e `frustration` (Score de 3 níveis com `signals`).
- Composição: `spam_risk = 0.45*credenciais + 0.30*identidade + 0.25*recompensa`;
  `0.4 < spam_risk < 0.6` ou `topic.confidence < 0.75` → humano; `spam_risk ≥ 0.6` → quarentena;
  billing → `refund_requested ≥ 0.7`; orders → `mentions_open_order ≥ 0.7`; prioridade alta se
  `frustration.confidence ≥ 0.7 and frustration.score ≥ 1.5`.

## Quando fazer uma 2ª requisição
Só quando o código **não consegue montar** a segunda sem a primeira resposta: precisa dela para buscar
mais dados, decidir de que o novo state é feito, ou escolher as opções da próxima pergunta. Se as
perguntas da 2ª poderiam ser feitas contra o state original → vão na 1ª e o código ignora as sobras.
Casos legítimos no doc: [sugestao-de-skill](../receitas/sugestao-de-skill.md) (rankeia 182, depois rejulga as 3 melhores com o texto
completo), [recuperacao-de-estrutura](../receitas/recuperacao-de-estrutura.md) (costura linhas, depois classifica os blocos que só existem
depois), [classificacao-hierarquica](../receitas/classificacao-hierarquica.md) (a resposta decide as opções do próximo nível).

## Princípios do "vibe coding" com agente (página do agent skill)
1. Conversar o desenho com o agente antes. 2. Revisar o plano antes de implementar.
3. **Perguntas e limiares num arquivo só**, fácil de revisar — "agentes não escrevem boas perguntas;
   espere editar junto". 4. Não aceitar afirmação sem validação.
O que um humano precisa revisar no código com Jev: **as perguntas e as constantes de limiar**.

## Relacionados
[o-que-e-o-jev](../modelo/o-que-e-o-jev.md) · [primitivas](../modelo/primitivas.md) · [confianca](../modelo/confianca.md) · [licoes-transversais](../licoes-transversais.md) · padrões: [fan-out-especulativo](padroes/fan-out-especulativo.md) · [roteamento-por-confianca](padroes/roteamento-por-confianca.md) · [pontuacao-composta](padroes/pontuacao-composta.md) · [roteamento-por-intencao](padroes/roteamento-por-intencao.md)
