---
name: padroes-das-receitas
description: Síntese do Codex sobre as receitas oficiais — que desenho reutilizar para cada necessidade (extração, datas, busca, skill, taxonomia, RAG, citação, verificação, function calling, reranking, features, estrutura) e o cuidado de cada um; decisões práticas sobre ausência, composição, custo e cache.
tipo: padrao
fonte: notas de receitas deste diretório + conferência dirigida dos snapshots oficiais (https://docs.typesafe.ai/cookbooks), Codex, 2026-09-30
estudado_em: 2026-09-30
---

# Padrões aproveitados das receitas

Consolidação do Codex em 2026-09-30 (antes em `skills/jev-design/references/cookbook-patterns.md`), a partir
das notas do Claude e de conferência dirigida dos snapshots oficiais locais. Receitas são exemplos de
desenho, não integrações testadas por nós. Limiares, custos e acurácias publicados não são garantias locais.

## Escolher o padrão

| Necessidade | Desenho reutilizável | Cuidado na aplicação | Receita |
|---|---|---|---|
| Extrair e-mail, telefone ou valor | Parser/regex produz candidatos; Choice escolhe um ID; código copia o trecho e normaliza. | Incluir `none`; ausência do candidato correto limita a qualidade; moeda e separadores dependem do locale. | [extracao-de-valor-pre-parseado](extracao-de-valor-pre-parseado.md) |
| Resolver datas | Choices leem modo e componentes; código monta e valida o calendário. | Fixar data de referência e convenção para ano ausente/dia relativo; data impossível vira revisão. | [extracao-de-datas](extracao-de-datas.md) |
| Localizar resposta em documento | Choice aponta IDs de trechos; Noul pergunta se há resposta. | O primeiro lugar do ranking pode ser só o trecho menos inadequado. | [busca-linha-a-linha](busca-linha-a-linha.md) |
| Selecionar ferramenta/skill | Ranking amplo com descrições curtas, depois reavaliação da shortlist com conteúdo detalhado. | Verificar adequação absoluta além do vencedor relativo; segunda chamada tem dependência real. | [sugestao-de-skill](sugestao-de-skill.md) |
| Classificar com especificidade variável | Quando a folha é incerta, devolver categoria pai e nível de especificidade. | Categoria ampla correta não equivale a folha correta; medir separadamente. | [classificacao-com-confianca](classificacao-com-confianca.md) |
| Navegar taxonomia | Choice entre filhos; manter alguns caminhos plausíveis em vez de descartar todos menos um. | Versionar taxonomia; score do caminho é heurística de busca, não P(acerto). | [classificacao-hierarquica](classificacao-hierarquica.md) |
| Filtrar contexto de RAG | Nouls separados para relevância, evidência, contradição da premissa e tentativa de instrução. | Preservar conflito em bloco próprio; filtro semântico não torna a passagem confiável. | [classificar-passagens-rag](classificar-passagens-rag.md) |
| Conferir citação | Primeiro localizar a frase por código; depois Choice entre apoio, contradição e ausência de apoio. | Falha de correspondência literal não prova fabricação se o produto aceita paráfrases. | [checagem-de-citacoes](checagem-de-citacoes.md) |
| Verificar extração de outro modelo | Validar estrutura, perguntar por campo se está errado/sem apoio/omitido; escalar conforme política. | Falha de parse ou campo obrigatório ausente precisa de caminho explícito (falha confirmada no exemplo oficial). | [cascata-sde](cascata-sde.md) |
| Preencher chamada de função | Nome/argumentos fechados viram Choice; Noul `stated` distingue argumento informado de default. | Validar combinação, autorização e efeito em código; valor permitido isoladamente pode formar chamada inválida. | [function-calling](function-calling.md) |
| Reordenar resultados | Recuperação barata produz shortlist; julgamento por par consulta–candidato dá ranking. | Reranking não recupera item que a primeira etapa perdeu. | [reranking](reranking.md) |
| Transformar texto em features | Noul vira coluna; Score pode virar média e dispersão; modelo tabular aprende a composição. | Geração/revisão das perguntas só usa desenvolvimento; teste fica fora do ciclo. | [autoresearch-de-features](autoresearch-de-features.md) |
| Recuperar estrutura de texto | Julgar junções, construir blocos, depois classificar/renderizar os blocos em código. | Não anunciar preservação byte a byte: junções e formatação alteram espaços/marcadores. | [recuperacao-de-estrutura](recuperacao-de-estrutura.md) |

## Decisões práticas

**Seleção e ausência.** Choice com `none` é válido e aparece na receita de extração.
Um Choice que só contém candidatos reais sempre escolhe um deles. Noul de
existência/adequação acrescenta outro sinal quando isso importa; não é obrigatório
em toda Choice. No exemplo de sugestão de skills, o portão usa o maior `fits` da
shortlist, mas o vencedor vem de outra pergunta. Assim, passar o portão não prova
que o candidato vencedor foi o que passou. Conferir o vencedor consumido é uma
proposta local a avaliar, não uma correção já medida.

**Composição.** O menor `confidence` dos componentes usados, adotado na receita
de datas, é uma política para destacar a parte fraca. Não é confiança estatística
conjunta. Da mesma forma, `max` entre alertas evita diluir um sinal forte, mas não
calcula a probabilidade da união dos erros. Normalizar sentido antes de ponderar:
um Noul de contradição entra como `1 - p` se alto no composto deve significar bom.

**Custo e chamadas.** Agrupar perguntas compartilha os tokens do estado. O número
de requests pode ficar fixo enquanto o custo aumenta com instruções/critérios.
Agrupar é preferência dentro dos limites de contexto e do orçamento, não proibição
de chamadas unitárias. Perguntas irrelevantes descartadas também consumiram tokens.
Limites, isolamento ou execução seletiva podem justificar dividir um lote.

**Cache.** Identificar estado, perguntas/critérios, provedor e versão efetiva do
modelo. Guardar tokens separadamente da tarifa. Um replay do cache não é nova
inferência. A retenção da resposta bruta deve respeitar os dados do projeto
(regras em [integracao-segura](../construir/integracao-segura.md)).

## Fontes oficiais por padrão

- [Extração por candidatos](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook), [datas](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook).
- [Busca por linha](https://docs.typesafe.ai/cookbooks/semantic_find), [sugestão de skill](https://docs.typesafe.ai/cookbooks/skill_suggestion).
- [Classificação com confiança](https://docs.typesafe.ai/cookbooks/classification_using_confidence), [hierárquica](https://docs.typesafe.ai/cookbooks/hierarchical_classification).
- [Passagens RAG](https://docs.typesafe.ai/cookbooks/classifying_rag_passages), [citações](https://docs.typesafe.ai/cookbooks/citation_check), [cascata SDE](https://docs.typesafe.ai/cookbooks/sde_cascade).
- [Function calling](https://docs.typesafe.ai/cookbooks/function_calling), [reranking](https://docs.typesafe.ai/cookbooks/rerank_typesafe).
- [Features](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery), [estrutura](https://docs.typesafe.ai/cookbooks/autoformat), [perguntas em paralelo](https://docs.typesafe.ai/cookbooks/parallel_questions).
