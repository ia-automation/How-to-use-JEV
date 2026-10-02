# Dados do `auditor-de-evidencia` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item G) e [DADOS.md](../../DADOS.md).
Registros sintéticos e normalizados de um CRM imobiliário fictício: serviços `api-leads`, `portal-web`,
`fila-cobranca`, `agenda-svc`, `mail-svc`; hosts `api.exemplo.com.br` (produção), `homolog.exemplo.com.br`,
`localhost:3000`; revisões curtas inventadas (`a1b2c3d`). Sem IP, sem caminho de máquina, sem credencial.

## O que cada `tipo` de registro é
`log_build` (tsc, docker build, next build, eslint, varredura) · `log_teste` (vitest/jest, cobertura) ·
`resposta_http` (verbo, URL, status, corpo, tempo) · `commit` (**saída do git ou do `gh`**: commit, push,
`pr view`) · `deploy` (rollout do Swarm, migration aplicada, evento de entrega, cofre) · `manual` (anotação
humana ou do agente, sem processo por trás).

## Como rotular `relacao` (precedência: contradicted > insufficient_evidence > supported)
1. Decompor a afirmação em partes: **o quê** (rota, suíte, migration, versão), **onde** (prod, dev, homolog,
   local), **estado** (passando, aplicada, publicada, saudável) e **quantidade** (todos, 3 réplicas, > 80%).
2. `contradicted`: algum registro diz o contrário de uma parte — teste falhou, HTTP 500/503, 404 em rota que
   deveria responder, corpo com erro mesmo com status 200, deploy com rollback, migration com erro em prod,
   push recusado, versão respondida diferente da afirmada, `CHANGES_REQUESTED`, número abaixo do limiar.
   Um registro **manual** que declara que a parte NÃO foi feita ("prod aplico depois") também contradiz.
3. `supported`: cada parte tem registro de **processo** (não manual) compatível em revisão, ambiente e conteúdo.
4. `insufficient_evidence`: o resto — nada sustenta, ou sustenta só parte (dev sem prod; teste sem deploy;
   commit sem push; subconjunto da suíte; rodada cancelada/incompleta; mock/dublê da coisa afirmada; `localhost`
   ou homolog quando se afirma produção; 200 sem o conteúdo afirmado; registro manual sem processo; evidência
   de **outra revisão**, anterior ou posterior).
5. **O registro mais recente sobre o mesmo assunto prevalece**: verde antigo + vermelho na revisão atual →
   `contradicted`; vermelho antigo + verde na revisão atual → `supported`.
6. `null` **não é usado**: `insufficient_evidence` já é a válvula do indecidível (ex.: "No migrations to apply"
   em prod, `AE-T014`). O construtor deve tratar `insufficient_evidence` como "mandar para humano/pedir prova".

## Decisões específicas
- **200 ≠ funcionando.** Precisa de corpo compatível com o que se afirma (`AE-A002`, `AE-T006`); corpo com
  `erro` contradiz (`AE-A027`); 404 quando a afirmação É o 404 sustenta (`AE-A026`).
- **Build ≠ teste; teste ≠ deploy; commit ≠ push; push ≠ publicado; aceito (202 queued) ≠ entregue.**
  Exceção: log de build que **contém a etapa de teste** com resultado sustenta "testes passando" (`AE-T009`).
- **Dublê**: `vi.mock`/`nock` da coisa afirmada → insuficiente (`AE-A004`, `AE-T011`, `AE-T012`); mock de algo que
  a afirmação não toca não pesa (`AE-T010`).
- **Pulados**: "todos passando" com `skipped` → insuficiente; "nenhum falhou" com `skipped` → sustentado.
  Repetição (`retry`) que passou → sustentado (a afirmação não promete estabilidade). Rodada cancelada, por
  timeout ou worker morto → insuficiente, mesmo com "0 failed".
- **Lint**: "sem erros" com warnings → sustentado; "limpo" com warnings → contradito ("limpo" exclui warnings).
- **Numéricas** (cobertura, latência, réplicas, versão): rotuladas normalmente com nota "numérica"; comparar é
  trabalho do **código**. "Acima de 80%" com 80,0% → contradito. Cobertura sem métrica nomeada → `statements`.
- **Manual**: nunca sustenta sozinho afirmação que tem prova mecânica possível (tela, teste, rota, cache). Sustenta
  afirmação sobre **ato humano** (autorização do dono, aprovação) quando cita a fonte — canal, data, texto
  (`AE-T018`); sem fonte ("acho que") → insuficiente (`AE-T019`).
- **Ambiente**: `localhost` e `homolog` não são produção (insuficiente, não contradição — nada diz que prod
  está quebrada). Afirmação "em homolog e prod" com só prod → insuficiente.
- **Revisão**: log de teste de revisão anterior ou posterior à afirmada → insuficiente (`AE-A001`, `AE-T004`).
- **Nome do teste**: suíte verde cujos testes listados não cobrem o comportamento afirmado → insuficiente
  (`AE-T072`); teste nomeado para o comportamento → sustentado (`AE-T073`).

## `registros_de_apoio`
- `supported`: os registros que sustentam (todos os necessários; o manual redundante fica fora, `AE-A024`).
- `contradicted`: os registros que contradizem (só eles; `AE-A028` lista os dois porque os dois mostram 1.9.1).
- `insufficient_evidence`: os registros que sustentam **parte** da afirmação (pode ser vazio quando nada
  sustenta nada, ex.: manual puro, saúde no lugar da rota, commit como prova).

## Famílias de caso difícil (todas em `ajuste.json` E `teste.json`; `nota` começa com "difícil:")
Contagem ajuste / teste:
1. Teste real de OUTRA revisão (anterior / posterior) — 1 / 1; mesma revisão (sustenta) — 0 / 1.
2. HTTP 200 sem conteúdo provado (vazio, lista vazia) × com conteúdo × 200 com erro no corpo — 2 / 3.
3. Build sem teste × build com etapa de teste — 1 / 2.
4. Teste com mock/nock dizendo "integração ok" × mock irrelevante — 1 / 3.
5. "Aplicada em dev" generalizada; prod com erro; prod "nothing to apply"; manual dizendo que prod ficou para depois — 2 / 4 (+ cofre dev/prod 0 / 2).
6. Registro manual sem processo × manual com fonte sobre ato humano × manual contradito por HTTP — 2 / 4.
7. Testado estendido a publicado (sem deploy; com push; com deploy ok; com rollback) — 1 / 3.
8. Verde velho × vermelho novo (e o inverso) — 2 / 2.
9. Homolog/localhost como produção — 2 / 4.
10. Subconjunto da suíte, pulados, "nenhum falhou", repetição, cancelada, worker morto — 4 / 7.
11. Commit ≠ push; push recusado; `gh pr view` — 2 / 5.
12. Lint "sem erros" × "limpo" com warnings — 2 / 2. Numéricas (cobertura, latência, réplicas, versão, limiar exato) — 4 / 8.
13. 404 esperado × inesperado; saúde no lugar da rota; saúde 503 após deploy — 3 / 5.
14. Aceito ≠ entregue (e-mail), backup não registrado, `down` não testada, sem sonda de disponibilidade — 0 / 5.

## Contagens (validação de 2026-10-01, zero erros: JSON, UTF-8 sem BOM, LF, campos, enums de `tipo` e `relacao`,
IDs `e1…en` e apoio existentes, 2–6 registros de 1–4 linhas, sem IP/caminho/segredo, mínimos, ≥ 30% difíceis)
| arquivo | casos | difíceis | supported | contradicted | insufficient_evidence |
|---|---|---|---|---|---|
| `rascunho.json` | 5 | 0 (por desenho: só encanamento) | 4 | 1 | 0 |
| `ajuste.json` | 31 | 26 (83%) | 8 | 8 | 15 |
| `teste.json` | 73 | 45 (61%) | 25 | 21 | 27 |

Ambiguidades decididas pelo rotulador (não estavam no briefing): `null` não é usado; manual pode contradizer e
pode sustentar ato humano com fonte; registro mais recente prevalece; "limpo" ≠ "sem erros"; "No migrations to
apply" é indecidível → insuficiente; `localhost`/homolog é insuficiente, não contradição; apoio de insuficiente
= o que sustenta parte; `commit` abrange saída de push e de `gh`.
