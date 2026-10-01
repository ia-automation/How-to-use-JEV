---
name: pontuacao-composta
description: Padrão — quebrar um julgamento complexo em Scores atômicos (um por dimensão), normalizar para 0–1 e combinar com pesos no código; mudar prioridade = mudar coeficiente, sem nova chamada.
tipo: padrao
fonte: https://docs.typesafe.ai/patterns/composite-scoring · /primitives/score#splitting-a-complex-judgment-into-several-scores
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 13124–13179 e 14500–14635; exemplo em fontes/docs/paginas/patterns/composite-scoring.md
estudado_em: 2026-09-30
---

# Pontuação composta (Composite scoring)

**Ideia:** dimensões independentes, cada uma um Score; o peso fica no código. Benefício: custo,
confiabilidade, velocidade — e **visibilidade** de como o número final nasce.

## Exemplo do doc (triagem de currículos)
4 Scores de 5 níveis, uma chamada:
- `python_depth` — "How much depth of python experience does this candidate have, based on the
  supplied resume?" — No Python mentioned · Mentioned but no detail · Used in projects, some
  specifics · Primary language, multiple projects · Deep expertise: architecture, performance, libraries
- `team_leadership` — No management · Informal mentorship or tech lead · Led a small team or project ·
  Managed a team with direct reports · Managed multiple teams or an engineering org
- `system_design` — No architecture work · Contributed to design discussions · Designed components
  of a larger system · Owned architecture of a significant system · Designed systems at scale across
  multiple domains
- `generalist` — Only one domain · Some variety, narrow field · A few areas or stacks · Regularly moved
  between domains · Track record of ramping up in unfamiliar areas and delivering

```python
py, lead, arch, gen = (response.answers[k].score / 4 for k in ("python_depth","team_leadership","system_design","generalist"))
ic_score = 0.40*py + 0.10*lead + 0.40*arch + 0.10*gen      # IC sênior
em_score = 0.15*py + 0.40*lead + 0.20*arch + 0.25*gen      # gerente de engenharia
```
Mesmas respostas, dois rankings — trocar a vaga não custa chamada.

## Exemplo da página Score (prioridade de ticket)
`severity` (3 níveis), `frustration` (3), `report_quality` (4: sem detalhe → passos E ambiente).
Normalizar por `len(criteria) - 1` (escalas de tamanhos diferentes!), depois
`0.6*severity + 0.3*frustration + 0.1*report_quality`. No exemplo: 0,62 / 0,64 / 1,0 → 0,664.

## Regras
- Uma dimensão por Score; níveis descrevem situações ([primitivas](../../modelo/primitivas.md)).
- **Sempre normalizar** antes de pesar, senão um Score de 5 níveis pesa mais que um de 3.
- Peso compensatório (soma ponderada) serve para **preferências**; regra "qualquer violação grave"
  precisa de condições separadas (um vermelho basta — `max`, não média). Ver [guardrails-llm](../../receitas/guardrails-llm.md) e
  [cascata-sde](../../receitas/cascata-sde.md).
- Mudar peso ou filtro de exibição **não exige nova inferência** se evidência e perguntas não mudaram
  → guardar as respostas brutas.
- Com rótulos, trocar a fórmula por modelo clássico sobre as probabilidades ([autoresearch-de-features](../../receitas/autoresearch-de-features.md)).
- Ordenar candidatos: Scores por item comparáveis (mesma pergunta para todos).

## Relacionados
[primitivas](../../modelo/primitivas.md) · [fan-out-especulativo](fan-out-especulativo.md) · [autoresearch-de-features](../../receitas/autoresearch-de-features.md)
