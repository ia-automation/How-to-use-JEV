---
name: jev-avaliar
description: Planejar ou executar a avaliação de uma integração com o Jev (TypeSafe) no domínio real — dados rotulados, ajuste × teste congelado, métricas por primitiva, limiares e faixa de dúvida, custo, latência, regressões e comparação com baselines. Use para validar qualidade, calibrar limiares ou comparar versões/idiomas; não tratar demos, receitas ou respostas mockadas como benchmark.
---

# Avaliar o Jev no domínio

Procedimento. Protocolo e lições: [metodo](../../conhecimento/avaliar/metodo.md) · o que as receitas oficiais
provam e não provam: [leitura-critica-das-receitas](../../conhecimento/avaliar/leitura-critica-das-receitas.md) ·
o que já medimos: [medicoes](../../conhecimento/evidencias/medicoes-2026-09-30.md). Raiz = dois níveis acima.

## Procedimento
1. **Defina a decisão e o custo dos erros**: falso positivo, falso negativo, encaminhamento a revisão e
   falha operacional. Se a tarefa é só preparar a avaliação, entregue os artefatos sem chamar a API.
2. **Monte os dados**: casos representativos + difíceis (negação, citação de terceiro, duas intenções,
   falta de informação com gabarito `null`, instrução adversarial no texto, sigla ambígua, português
   informal). Ajuste e teste separados, com a mesma distribuição; o teste só é aberto no fim.
3. **Fixe provedor, versão (`jev-1.13.0`, não o alias), perguntas e rubricas**; afine perguntas e limiares
   **só no ajuste**; grave o hash de perguntas/código/limiares antes de abrir o teste. Mudança depois do
   teste = nova versão; o teste antigo vira ajuste.
4. **Execute com autorização e orçamento** confirmados; chave por variável, nunca impressa; cache com
   chave = hash(modelo + state + perguntas) para não pagar duas vezes; registre `model` efetivo, latência,
   tentativas, `usage`, status e `live`/`replay`.
5. **Meça conforme o tipo**: Noul → P(sim), Brier, precisão/recall por limiar; Choice → matriz de confusão;
   Score → erro ordinal e ordenação. Falhas operacionais ficam fora da métrica de qualidade e são contadas à
   parte (cobertura). `confidence` não é P(acerto).
6. **Escolha a política** (três faixas, limiar por risco) no ajuste; no teste, reporte cobertura automática,
   erro entre os automáticos, taxa de revisão e o erro caro (ex.: falso "passa") — não só o acerto global.
7. **Compare com baselines** nas mesmas condições (regra, contagem, TF-IDF, fluxo atual/LLM), com o mesmo
   conjunto; distinga resultado do modelo, do pipeline e do rótulo disputável.
8. **Relate** n de casos únicos (não repetições), intervalo de confiança quando couber, condições, falhas
   observadas e o que o número **não** mostra. Só marque [testado] com execução e evidência; nova versão,
   idioma ou rubrica exigem nova verificação.
9. **Registre** o resultado com [jev-manter](../jev-manter/SKILL.md) (nota de medição + índice + CHANGELOG).

## Semente
[seed-cases.json](assets/seed-cases.json): 8 casos sintéticos em pt-BR para "pede reembolso?", com
gabaritos definidos por nós (um com `gold: null`, fora da métrica binária). **Não contém resultados do Jev**
e não é amostra representativa.

## Armadilhas
Limiar de Noul reaproveitado em Choice sim/não · exigir que pergunta e negação somem 1 · tratar timeout ou
erro HTTP como "não" · aprovar limiar porque a confiança média subiu · ajuste "fácil" (tudo perto de 0 ou 1)
não calibra faixa · alargar pergunta para consertar um caso do ajuste (overfit) · anunciar replay de cache
como rodada nova · comparar latências medidas em concorrências diferentes.
