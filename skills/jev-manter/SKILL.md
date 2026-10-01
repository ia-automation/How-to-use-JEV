---
name: jev-manter
description: Manter o repositório de conhecimento do Jev em dia quando a documentação da TypeSafe mudar, sair versão nova do modelo ou do SDK, ou quando o uso real trouxer um aprendizado ou medição nova. Use ao ouvir "atualiza o estudo do Jev", "saiu jev-1.14", "o doc da TypeSafe mudou", ou ao fim de um trabalho com o Jev que mediu algo novo.
---

# Manter o conhecimento do Jev

Procedimento. Regras de escrita (fidelidade, rótulos, um fato num lugar, frontmatter, links) estão em
[AGENTS.md](../../AGENTS.md); raiz = dois níveis acima desta pasta.

## A. A documentação mudou (ou suspeita)
1. Com acesso autorizado às fontes, baixe índice (`llms.txt`), texto completo (`llms-full.txt`) e OpenAPI
   para um diretório com data **e hora** em `fontes/docs/` (fora do Git). Nunca sobrescreva uma coleta
   anterior. Análise offline: use os snapshots existentes e registre a limitação.
2. Compare com o snapshot mais recente: páginas novas/removidas (`diff` das listas de URL) e alteradas
   (`diff -rq` das pastas de páginas). Não basta o `llms-full`: leia também dados e assinaturas de
   `TypesafeExample`, `ConfidenceExplorer`, `ScoreExplorer` e `SdkSignature` quando pertinentes. Separe
   prosa, OpenAPI, tipos do SDK e comportamento medido.
3. Para cada página alterada, ache a nota que a cita (`grep -rl "<slug>" conhecimento/`) e atualize **só**
   o que mudou, citando a nova captura (URL + arquivo + linhas). Receita nova → nota nova no molde de
   `conhecimento/receitas/`. Divergência → [contradicoes-da-documentacao](../../conhecimento/evidencias/contradicoes-da-documentacao.md).
4. Versão nova do modelo: atualizar [modelos-precos-limites](../../conhecimento/modelo/modelos-precos-limites.md)
   e criar `conhecimento/modelo/limites-<versão>.md`, mantendo a antiga (números antigos valem para a versão antiga).
   Limiares e medições precisam ser refeitos antes de transportar resultados.
5. Página baixada não é página estudada; 404 não conta como documentação. Registre em
   [proveniencia](../../conhecimento/evidencias/proveniencia.md) o que foi lido e o hash no
   `fontes/catalogo/catalogo.json`.

## B. Aprendizado do uso real
- Medição nossa (acurácia, latência, limiar que funcionou, falha nova) → nota em `conhecimento/evidencias/`
  (`medicoes-AAAA-MM-DD.md` ou seção nova), com data, versão do modelo, n, como foi medido e o que não mostra.
- Fecha ou abre uma pendência → [pendencias](../../conhecimento/evidencias/pendencias.md) (status + link).
- Decisão do dono → [decisoes](../../conhecimento/evidencias/decisoes.md) (não apague a anterior; marque e date).
- Regra que vale para toda integração → [licoes-transversais](../../conhecimento/licoes-transversais.md); se
  muda o jeito de escrever pergunta, também o checklist de [jev-desenhar](../jev-desenhar/SKILL.md).
- Se o fato novo muda o que todo agente precisa saber, atualize a linha correspondente do NÚCLEO no
  `AGENTS.md` (resumo + link; o fato mora na nota).

## Fechamento (sempre)
- Nota nova → uma linha em [INDICE](../../conhecimento/INDICE.md); mudança relevante → `CHANGELOG.md`.
- Afirmação sem fonte não entra; número entra com de onde veio e rótulo [doc]/[testado]/[terceiro]/[local].
- Nada se apaga: arquivo superado vai para `.local/antigos/<data>/` com o caminho relativo.
- Rode `python -X utf8 ferramentas/validar.py` (PowerShell ou Bash) até passar: links e âncoras, frontmatter,
  índice, JSON, skills e ausência de segredo. Registre se foi leitura, mock ou execução real.
