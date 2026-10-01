---
name: leitura-critica-das-receitas
description: O que os benchmarks das receitas oficiais permitem e não permitem concluir (13 perguntas 12,2×/10× só contra sequencial; 99,2% é concordância, não acurácia; desvio 0,0102 não estima acerto) e os acréscimos ao nosso protocolo de avaliação.
tipo: principio
fonte: https://docs.typesafe.ai/cookbooks (parallel_questions, consistency_choice_cookbook, consistency_noul_cookbook, classification_using_confidence, autoresearch_feature_discovery), revisão documental do Codex em 2026-09-30
estudado_em: 2026-09-30
---

# Leitura crítica das receitas

Revisão documental do Codex em 2026-09-30 (antes em `skills/jev-evaluate/references/cookbook-evidence.md`).
Os resultados abaixo pertencem ao fornecedor; não reexecutamos experimentos. As notas do Claude ajudaram a
identificar os limites. Os números completos estão em cada receita.

| Exemplo publicado | O que permite aprender | O que não conclui |
|---|---|---|
| 13 perguntas em lote: 12,2× menos custo e 10× menos tempo ([perguntas-em-paralelo](../receitas/perguntas-em-paralelo.md)) | Compartilhar estado longo economiza repetição de tokens. | O tempo compara com 13 chamadas sequenciais; não prova 10× contra cliente concorrente. |
| Choice: 99,2% de concordância com política de abstenção, 74,2% automático ([autoconsistencia-choices](../receitas/autoconsistencia-choices.md)) | Medir estabilidade da ação junto da cobertura. | Concordância não é acurácia; um caso foi repetido 15 vezes. O corte usa probabilidade máxima, não `confidence`. |
| Noul: desvio médio 0,0102 em uma rubrica repetida ([autoconsistencia-nouls](../receitas/autoconsistencia-nouls.md)) | Medir dispersão por pergunta e mudanças de ação perto do limiar. | Não estima acerto em outros casos ou em português. |
| Classificação SIC: retornar pai em casos incertos ([classificacao-com-confianca](../receitas/classificacao-com-confianca.md)) | Reduzir especificidade pode ser útil sem nova chamada. | Acerto em níveis diferentes não deve ser confundido com melhoria de acurácia na folha. |
| Reranking e sugestão de skills ([reranking](../receitas/reranking.md), [sugestao-de-skill](../receitas/sugestao-de-skill.md)) | Comparar pipeline completo com a recuperação/seleção original. | Domínio único, shortlist favorável ou pedidos sintéticos não demonstram generalização. |
| Perguntas como features ([autoresearch-de-features](../receitas/autoresearch-de-features.md)) | Separar a busca de perguntas em desenvolvimento da avaliação final. | Importância de feature em uma execução não demonstra estabilidade entre amostras. |

## Acréscimos ao nosso protocolo

1. **Estabilidade separada da qualidade.** Para cada pergunta, medir dispersão,
   concordância do rótulo bruto, concordância após política, abstenção e conflitos.
   Avaliar qualidade em exemplos distintos e rotulados, além das repetições.
2. **Entrada idêntica versus perturbação.** Os cookbooks de consistência mudam um
   `uid` no estado a cada chamada. Isso mistura variação entre chamadas com
   sensibilidade a um campo irrelevante. Separar esses dois experimentos; um
   identificador só no registro externo não altera a entrada semântica.
3. **Cache explícito.** Registrar origem `live` ou `replay`. Os notebooks incluem
   respostas cacheadas; executar o notebook pode apenas redesenhar gráficos.
4. **Comparação de tempo justa.** Mesma região, concorrência, limites, política de
   retry e medição ponta a ponta. Nos exemplos de consistência, Jev sequencial e
   LLMs em pool não bastam para uma razão universal de velocidade.
5. **Métricas do consumidor.** Classificação hierárquica mede folha e ancestral
   separadamente; extração mede valor e omissão; RAG mede recuperação e resposta
   final; guardrails medem falsos bloqueios e riscos que passaram.
6. **Mutações de perguntas são treinamento da política.** Revisar exemplos, rubricas
   ou selecionar features só no conjunto de desenvolvimento. O teste reservado
   não escolhe o próximo limiar nem a próxima pergunta.

`min(confidences)`, média geométrica de caminho e `max(alertas)` são escolhas de
composição; avaliar a ação resultante sem chamá-las de probabilidades conjuntas.
Poucos casos ilustrativos ajudam a depurar, mas não aprovam a integração.
Protocolo completo: [metodo](metodo.md).

Fontes: [paralelismo](https://docs.typesafe.ai/cookbooks/parallel_questions),
[consistência Choice](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook),
[consistência Noul](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook),
[classificação](https://docs.typesafe.ai/cookbooks/classification_using_confidence),
[features](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery).
