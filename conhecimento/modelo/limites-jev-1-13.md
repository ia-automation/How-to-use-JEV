---
name: limites-jev-1-13
description: As 9 falhas conhecidas do jev-1.13 (leitura literal, conta/números, datas, indireção, state grande, conteúdo adversarial, instrução×critério contraditórios, invariantes estruturais, geração) e o que fazer em cada uma.
tipo: limite
fonte: https://docs.typesafe.ai/model-jaggedness/jev-1.13 (revisado pela TypeSafe em 2026-09-17)
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 12840–12992
estudado_em: 2026-09-30
---

# Limites do jev-1.13 ("jaggedness")

Resumo do doc: rápido, calibrado, bom em bom senso; sofre com **indireção**, é **literal** e ruim em
**precisão numérica**.

| # | Falha | Faça isto |
|---|---|---|
| 1 | Leitura literal | Escrever a condição exata; casos de fronteira nos `criteria` |
| 2 | Matemática e números | Aritmética no código |
| 3 | Comparar data/hora | Extrair componentes; comparar no código |
| 4 | Indireção | Menos saltos; apontar a parte do state |
| 5 | State grande com detalhe irrelevante | Filtrar antes; mandar só o que a pergunta usa |
| 6 | Conteúdo adversarial | Critérios precisos; testar casos de borda antes de publicar |
| 7 | Instrução e critério contraditórios | Alinhar os dois |
| 8 | Invariantes estruturais "de bom senso" | Perguntar cada decisão de um jeito só; garantir identidades no código |
| 9 | Geração | Usar modelo generativo |

## 1. Leitura literal
Responde a pergunta **escrita**, não a pretendida — escopo, negação e condição implícita valem ao pé
da letra. **Quando você se pega explicando "o que eu quis dizer" diante de uma resposta errada, essa
explicação é a metade que falta da instrução.** Interpretação inevitável → dividir em duas perguntas
literais e combinar em código.

## 2. Números
- **Não conta** (caracteres, ocorrências, itens de lista longa): reconhece a "forma" da resposta; erro
  cresce com o tamanho. Se regex/parser acha a unidade, a contagem é do código. Contar itens que
  atendem um critério = **um Noul por item, soma no código**:
  ```python
  result = client.system_one({"items": items},
      {f"item_{i}": Noul(instructions=f"Is `items[{i}]` the name of a fruit?") for i in range(len(items))})
  count = sum(result.nouls[f"item_{i}"].noul > YES for i in range(len(items)))
  ```
- Representação numérica pior que semântica: cor em hex/RGB pior que nome da cor; assembly/binário
  pior que linguagem de alto nível. Converter no código e passar número calculado ou faixa nomeada.
- **Score não é régua**: pode usar a média para passar/não passar um limiar, mas não para reconstruir
  a magnitude interpolando entre níveis.

## 3. Datas
Lê data como texto, não como quantidade ordenada — "qual vem antes", "quanto tempo entre", "cai na
janela" são pouco confiáveis (pior com formatos mistos, datas relativas, trimestres, janelas de
liquidação). Cada parte da data é conjunto fechado (12 meses, 31 dias, faixa de anos) → **Choice por
parte com opção "não declarado"**; o código monta e faz toda a aritmética ([extracao-de-datas](../receitas/extracao-de-datas.md)).

## 4. Indireção
Dupla negação, "propriedade de uma propriedade", vários saltos → menos confiável. Escrever o mais
direto possível e nomear a parte do state.

## 5. State grande
Acurácia cai com conteúdo não relacionado (distrator). Recuperar e filtrar em código; se não der,
Noul de relevância filtra ([classificar-passagens-rag](../receitas/classificar-passagens-rag.md)). Contexto é limitado (64k/32k).

## 6. Adversarial
O state é dado e o modelo **não o trata como hostil por padrão**: instrução injetada, enquadramento
enganoso ou texto que "argumenta pela própria classificação" movem a resposta. TypeSafe espera
melhorar. Critérios explícitos + teste amplo antes de liberar para muitos usuários. (Guardrails com
Jev "não são fronteira de segurança" — [guardrails-llm](../receitas/guardrails-llm.md).)

## 7. Contradição instrução × critério
Ex.: Noul em que `true` descreve "não" e `false` descreve "sim" piora. Critério é extensão da
instrução; linguagem clara que uma pessoa comum entenda.

## 8. Invariantes estruturais
O modelo é muito **consistente** (entradas semanticamente parecidas → saídas parecidas), mas
identidades que parecem óbvias não valem:
- Mesma pergunta ("o cliente pede reembolso?") no ticket "I'm not happy with the fit. What are my
  options here?": Noul 0,22 × Choice sim/não com yes 0,01 / no 0,99 / conf 0,97.
- Pergunta e sua negação como dois Nouls ("…something other than a refund?") no ticket de cobrança
  dupla: 0,72 + 0,47 = 1,19 (não soma 1).
→ Não reaproveitar limiar de Noul em Choice; não exigir aritmética entre perguntas separadas; Choice
(relativa: *qual*) e Noul por opção (absoluto: *se*) respondem perguntas diferentes — usar os dois
quando precisa dos dois ([sugestao-de-skill](../receitas/sugestao-de-skill.md)).

## 9. Geração
Não treinado para gerar texto. Extração = gerar candidatos com regex ou LLM e o Jev **escolher**
([extracao-de-valor-pre-parseado](../receitas/extracao-de-valor-pre-parseado.md)); espaço limitado → Choice sobre as opções.

## Lembrete final do doc
Evitar: perguntar o que o código calcula exatamente; esconder vários julgamentos numa pergunta;
tarefa de Sistema 2 (muitas camadas de indireção); state maior que o necessário (*context rot*).
Falha nova → Discord da TypeSafe.

## Visto na prática (vídeo 2, fora do doc)
Sentimento de notícia para o ticker "MS" (Morgan Stanley) numa matéria sobre o canal "MS NOW": Jev
disse `negative` com confiança **0,25** (a incerteza avisou); o LLM acertou `neutral`. Consertado por
desenho: primeiro Noul "o artigo menciona a empresa X?" (0,09 → não), só depois sentimento. Ver
[video-02-quantbrasil](../evidencias/videos/video-02-quantbrasil.md).

## Relacionados
[primitivas](primitivas.md) · [state](state.md) · [confianca](confianca.md) · [licoes-transversais](../licoes-transversais.md)
