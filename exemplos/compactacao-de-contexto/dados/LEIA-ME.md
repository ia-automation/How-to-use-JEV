# Dados do `compactacao-de-contexto` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item O) e [DADOS.md](../../DADOS.md).
Sessões sintéticas de um agente de programação num parque fictício (serviços `api-pedidos`, `api-agenda`,
`worker-relatorios`…): conversa em pt-BR, comandos e saídas em inglês como seriam de verdade. Caminhos sempre
relativos ao repositório, domínios `exemplo.com`, nenhum segredo, nenhuma pessoa real.
Gabarito = o que um engenheiro sênior, que vai CONTINUAR a tarefa a partir do contexto compactado, manteria.

Arquivos: `rascunho.json` (5 sessões fáceis), `ajuste.json`, `teste.json` (abrir uma vez, no fim). Envelope
`{"versao", "autor": "fable", "casos"}`.

## Esquema (o do briefing, sem campo extra)
`{"id", "tarefa_atual", "mensagens": [{"id", "papel", "texto"}], "manter": [ids], "descartar": [ids], "nota"}`
- `tarefa_atual`: uma frase com o que está sendo feito AGORA (é o que o compactador recebe como alvo).
- `mensagens`: 12–25 por sessão, IDs `m01`, `m02`… na ordem da conversa. `papel` ∈ `usuario | assistente |
  ferramenta`. Texto de 1–6 linhas; saída de ferramenta até 12 linhas.
- `manter` e `descartar` são disjuntos. Mensagem que não está em nenhuma das duas é **discutível**: fica fora da
  métrica e a `nota` do caso diz qual é e por quê (`discutível: m07 (…)`). No máximo 15% das mensagens.
- `nota`: começa com `"difícil: <família>"` nas sessões difíceis.

## A pergunta que decide cada mensagem
> Se esta mensagem sumisse, quem continua a `tarefa_atual` perderia um fato de que precisa e que não está em
> outra mensagem mantida nem se recupera relendo o repositório?

Sim → `manter`. Não → `descartar`. A unidade é a mensagem inteira: uma linha necessária basta para manter.

## O que fica (`manter`)
1. **O pedido que define a tarefa atual** e todo **requisito dela** dito pelo usuário — mesmo já implementado:
   enquanto a tarefa está aberta, o requisito é o critério de aceite.
2. **Restrição ou preferência do usuário ainda válida**, por mais antiga que seja ("commit só nesta branch",
   "sem dependência nova", "prod é comigo").
3. **Decisão em vigor** (a última palavra sobre cada assunto).
4. **Valor literal ainda em uso que nasceu na sessão**: caminho de arquivo criado, nome escolhido, URL, ID
   devolvido por uma API, número medido, comando que reproduz o problema.
5. **Erro ainda não resolvido** — a ocorrência mais recente e completa.
6. **Estado do trabalho**: o que já foi feito e o que falta (o placar mais recente).
7. **Conclusão de tarefa anterior que é premissa da atual** ("a migration já está em dev; em prod não").
8. **Hipótese já eliminada de um erro AINDA aberto** — só a conclusão ("não é o cache"), para não repetir o teste.
9. **Pergunta do assistente ainda sem resposta** e proposta aguardando decisão.
10. **Contorno em vigor** de um problema não resolvido ("use `DOCKER_BUILDKIT=0` até a infra atualizar").

## O que sai (`descartar`)
- Saudação, agradecimento, "ok", "segue", aviso de pausa.
- Anúncio ou plano do assistente já executado ("vou rodar o lint").
- Saída de ferramenta já consumida: conteúdo de arquivo do repositório (relê-se), listagem, teste que passou,
  busca cujo achado outra mensagem mantida repete.
- Exploração abandonada e tentativa que não deu certo, quando o problema já foi resolvido ou contornado.
- Tarefa anterior concluída que a atual não usa — pedido, passos e resultado.
- Decisão ou valor substituído depois (a versão antiga).
- Erro já resolvido (e o diagnóstico dele).
- Restrição que só valia para uma tarefa anterior ("não mude a assinatura dessa função", com a função já entregue).
- Hipótese eliminada quando a causa JÁ foi encontrada.
- Pergunta do assistente cuja resposta é completa sozinha.
- Repetição: fato que outra mensagem mantida traz por inteiro.

## Desempates
- **Redundância** — fato necessário em duas mensagens: fica UMA. Resumo do assistente que traz o valor literal
  vence a saída bruta; saída bruta vence resumo vago (sem o literal). Entre duas equivalentes, a mais recente.
- **Resposta curta que depende da pergunta** ("a 1", "pode", "nessa ordem", "o resto ok"): ficam as duas — a
  resposta e a mensagem que lhe dá sentido.
- **Mensagem com parte velha e parte válida** (restrição + pedido já cumprido; URL corrigida depois + nome do
  header que continua valendo): fica, pela parte válida.
- **Decisão revertida**: a antiga sai; a nova fica. Se a nova diz "volta ao que era antes" sem repetir o
  conteúdo, a mensagem original volta a ser necessária e fica também.
- **Requisito cumprido**: da tarefa atual → fica (item 1); de tarefa anterior encerrada → sai.
- **Instrução de passo único já executada** ("roda em dev antes") → sai; o resultado fica no placar.
- **Saída longa**: se o assistente não repetiu a linha necessária com o valor literal, a saída inteira fica.

## O que é discutível (fora das duas listas, com nota)
- Justificativa técnica de uma decisão mantida, quando a decisão sozinha já basta.
- Nota de desenho do assistente que ajuda a continuar, mas está no código.
- Erro aberto cujo próximo passo já está dito em outra mensagem mantida.
- Resposta que apenas adia uma pergunta aberta.
- Estado de tarefa interrompida que o usuário disse que "depois retoma".

## Famílias de caso difícil (`nota` começa com "difícil: <família>"; todas nos dois conjuntos)
1. `restrição antiga ainda válida` — dita no começo, vale até o fim.
2. `decisão revertida` — a antiga é descartável, a nova não.
3. `saída longa com uma linha necessária` — e a variante em que o assistente já repetiu a linha.
4. `conclusão anterior é premissa` — a tarefa passada acabou, o resultado dela sustenta a atual.
5. `restrição que caducou` — valia para a tarefa anterior.
6. `resposta curta que depende da pergunta`.
7. `hipótese descartada` — de erro ainda aberto (fica a conclusão) × de erro já explicado (sai).
8. `contorno em vigor` — o erro some, o contorno não (e o contorno que deixou de ser necessário).
9. `valor corrigido` — o primeiro valor sai, a correção fica.
10. `progresso parcial` — placar do que falta; pergunta sem resposta.
11. `decisão embutida` — em elogio, em mensagem longa, em resposta a outra coisa.
12. `redundância` — resumo × saída bruta.
13. `tarefa interrompida` — o usuário troca de assunto no meio.

## Contagens (validador do rotulador, 2026-10-01, zero erros)
| arquivo | sessões | difíceis | mensagens (mín–máx por sessão) | `manter` | `descartar` | discutíveis |
|---|---|---|---|---|---|---|
| `rascunho.json` | 5 | 0 (por desenho) | 61 (12–13) | 22 (36%) | 39 (64%) | 0 |
| `ajuste.json` | 18 | 16 (88%) | 235 (12–20) | 84 (36%) | 145 (62%) | 6 (2,6%) |
| `teste.json` | 36 | 31 (86%) | 477 (12–22) | 169 (35%) | 299 (63%) | 9 (1,9%) |

Por sessão, `manter` fica entre 25% e 47% das mensagens.

Por papel — mensagens / em `manter` (ajuste · teste): `usuario` 73/54 (74%) · 163/106 (65%); `assistente` 102/25
(25%) · 203/54 (27%); `ferramenta` 60/5 (8%) · 111/9 (8%). Sessões com alguma saída de ferramenta em `manter`:
5 de 18 · 9 de 36.
**Aviso ao construtor (baseline óbvio):** a regra "`papel = usuario` → manter" acerta 79% das mensagens no ajuste e
75% no teste (precisão 76% · 67%; cobertura 64% · 63%). O exemplo só se justifica acima disso — o ganho mora nas
mensagens de usuário descartáveis (conversa, decisão revertida, tarefa encerrada) e nas de assistente/ferramenta
necessárias (placar, erro aberto, valor literal).

Discutíveis (fora das duas listas, citadas na nota): ajuste `CC-A004` m06, `CC-A009` m09, `CC-A010` m10, `CC-A011`
m01 e m04, `CC-A014` m10; teste `CC-T006` m05 e m12, `CC-T008` m12, `CC-T011` m06, `CC-T015` m04, `CC-T022` m11,
`CC-T027` m10, `CC-T031` m01 e m04.

Por família difícil (ajuste / teste; a família é o primeiro rótulo da nota, e uma sessão costuma tocar duas ou
três): decisão revertida 2/5 · saída longa com uma linha necessária 1/5 · hipótese descartada 2/3 · conclusão
anterior é premissa 1/3 · restrição antiga ainda válida 2/2 · contorno em vigor 1/2 · progresso parcial 1/2 ·
resposta curta que depende da pergunta 1/2 · restrição que caducou 1/2 · valor corrigido 1/2 · decisão embutida
1/1 · redundância 1/1 · tarefa interrompida 1/1.

O validador conferiu: envelope, campos e ordem, `papel` no enum, IDs `m01…` em sequência, 12–25 mensagens por
sessão, texto de até 6 linhas (até 12 em `ferramenta`), `manter` e `descartar` sem repetição, sem ID inexistente,
em ordem e disjuntos, toda mensagem fora das duas listas citada na nota depois de `discutível:`, todo `mNN` citado
numa nota existe na sessão, discutíveis ≤ 15%, mínimos, ≥ 30% difíceis, nenhuma `tarefa_atual` repetida, nenhum
caminho de máquina, nenhum domínio fora de `exemplo.com`, UTF-8 sem BOM, LF.

## Ambiguidades decididas pelo rotulador (não estavam no briefing)
- **Requisito já cumprido da tarefa ATUAL fica** (critério de aceite); o de tarefa encerrada sai.
- **Redundância**: fica uma só — o resumo com o literal vence a saída bruta; a saída vence o resumo vago.
- **Resposta curta** leva junto a mensagem que lhe dá sentido.
- **Hipótese eliminada** fica só enquanto o erro está aberto, e só a conclusão.
- **Lista de trabalho** achada por busca (arquivos a alterar) fica enquanto houver item pendente; depois sai.
- **Conteúdo de arquivo do repositório** sai sempre (relê-se); saída com valor que só existe ali (ID devolvido por
  API, caminho gerado, progresso de carga, cron do servidor) fica se ninguém a repetiu.
- **Instrução de passo único já executada** sai; restrição permanente fica.
- **Tarefa interrompida** ("depois a gente retoma"): pedido e ponto de parada ficam como discutíveis.
- `tarefa_atual` diz, entre parênteses, o que já terminou quando isso muda o gabarito.
