# Dados do `triagem-de-alerta` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item N) e [DADOS.md](../../DADOS.md).
Alertas sintéticos de um parque fictício de microsserviços (Swarm, Postgres, fila, gateway, e-mail, login). Nenhum
host, IP, usuário ou chamado é real: rede interna sempre `10.0.0.x`; origem externa sempre nas faixas reservadas
para documentação (`203.0.113.x`, `198.51.100.x`); contas no formato `inicial.sobrenome` ou `svc-*`, inventadas.
Gabarito = o que um engenheiro de plantão experiente decidiria às 3h lendo só `alerta` + `contexto`.

Arquivos: `rascunho.json` (5 fáceis), `ajuste.json`, `teste.json` (abrir uma vez, no fim). Envelope
`{"versao", "autor": "fable", "casos"}`. A ordem dos casos foi embaralhada (as ações não vêm agrupadas).

## Esquema (o do briefing, sem campo extra)
`{"id", "alerta": {"fonte", "titulo", "detalhe", "ativo", "ambiente"}, "contexto": [linhas], "acao", "sinais":
{"atividade_esperada", "ativo_critico", "indicio_de_comprometimento", "em_andamento"}, "nota"}`
- `fonte` ∈ `monitoramento | waf | auth | banco | fila | edr | backup` (quem emitiu o alerta).
- `ambiente` ∈ `prod | homolog | dev`. `ativo`: nome inventado do serviço, nó ou banco.
- `detalhe`: 1–6 frases com hora, contagens e estado ("sessão ativa", "bloqueado às 01:18"). O "agora" do caso é a
  hora do alerta; quando o caso não diz a data, é a madrugada de quinta-feira, 2026-10-01.
- `contexto`: 0–5 linhas que o plantão teria à mão (janela de manutenção, chamado, deploy, histórico do usuário,
  inventário). Contexto vazio é informação: nada explica o alerta.
- `acao` ∈ `auto_close | notify_owner | queue_tier2 | contain_now` — sempre decidida (o plantão tem de fazer algo).
- `sinais`: quatro valores `true | false | null`; `null` só com explicação na `nota`.
- `nota`: começa com `"difícil: <família>"` nos casos difíceis.

## O que cada ação significa
- `auto_close` — fecha sem avisar ninguém: o contexto explica o alerta inteiro.
- `notify_owner` — manda para o dono do serviço: anomalia sem sinal de ataque que ele precisa saber (falha,
  degradação, capacidade, tentativa barrada). A URGÊNCIA do aviso é do código, não do rótulo: `ativo_critico` e
  `em_andamento` verdadeiros → acorda o dono; senão → mensagem para a manhã. Banco de produção fora do ar é
  `notify_owner`.
- `queue_tier2` — fila do analista de segundo nível: há indício (ou dúvida real) de ação hostil, mas não há o que
  conter agora — a atividade parou e a porta foi fechada, ou o ativo não é crítico.
- `contain_now` — age na hora (derruba sessão, isola nó, bloqueia origem, revoga credencial) e acorda quem for:
  indício de comprometimento, em ativo crítico, acontecendo agora.

## Os quatro sinais (cada um é uma pergunta sim/não independente)
1. **`atividade_esperada`** — o `contexto` explica o alerta INTEIRO como atividade planejada ou conhecida:
   mudança dentro da janela anunciada e no ativo anunciado; deploy recente cujo efeito é o que se vê e dentro do
   prazo normal; usuário, conta de serviço ou tarefa agendada fazendo o de sempre; teste de intrusão autorizado
   dentro de escopo, janela e origem; condição repetida já com chamado aberto, dono ciente e sem mudança.
   **Não é esperada** quando: a hora está fora da janela; o ativo é outro; o deploy foi em outro serviço ou há
   horas; o efeito passou do combinado; o alerta repetido piorou; a causa é conhecida mas o efeito não foi
   planejado (atualização de regras que passa a barrar cliente legítimo). Sem `contexto` → `false`.
2. **`ativo_critico`** — o ativo guarda dado de cliente, guarda ou valida credencial, ou sua queda para o negócio:
   Postgres de produção (primário e réplica), gateway de borda, login/SSO, cofre, gerente e nós do Swarm de
   produção, APIs de pedidos/pagamentos/clientes, fila, servidor de e-mail, backup de produção, painel
   administrativo. **Não é o mesmo que `ambiente = prod`**: ferramenta interna em produção sem dado de cliente e
   sem credencial de produção (`wiki-interna`, `painel-status`) é `false`; ativo de dev/homolog que guarda CÓPIA
   de dado de produção é `true`. Dev/homolog com base sintética é `false`. `null` = o alerta não identifica o ativo.
3. **`indicio_de_comprometimento`** — há sinal de que alguém obteve ou está obtendo acesso ou efeito não
   autorizado, e o contexto não o explica: login bem-sucedido de origem/dispositivo estranho, credencial usada
   fora do lugar, comando ou processo plantado, dado saindo para destino desconhecido, privilégio/conta/regra
   criados sem chamado, payload de ataque respondido com sucesso, teste de intrusão fora do escopo, da janela ou
   da origem autorizada. **Tentativa 100% barrada não é indício** (varredura com 403/404, força bruta sem nenhum
   sucesso, arquivo posto em quarentena antes de executar): é ruído ou aviso ao dono. Falha operacional (queda,
   disco, lentidão, backup quebrado) não é indício. `null` = o texto sustenta igualmente a leitura hostil e a
   benigna (usuário legítimo fazendo algo incomum, tráfego sem identificação de processo).
4. **`em_andamento`** — na hora do alerta a coisa continua: sessão ou conexão aberta, processo rodando, tráfego
   fluindo, tentativas chegando, condição operacional persistindo, ou artefato hostil ainda instalado (conta
   criada, chave adicionada, arquivo plantado, regra ativa). `false` = acabou e a porta foi fechada (origem
   bloqueada, conta travada, token revogado, processo morto, sessão encerrada) ou foi evento pontual que já
   passou. Vale para qualquer alerta, não só de segurança (CPU ainda alta = `true`; reinício que já voltou =
   `false`).

## Precedência — função mecânica de `sinais` para `acao` (o validador confere todos os casos)
```
se indicio = true E ativo_critico = true E em_andamento = true  -> contain_now
senão se indicio != false (true ou null)                         -> queue_tier2
senão se atividade_esperada = true                               -> auto_close
senão                                                            -> notify_owner
```
- Ordem do briefing: `contain_now` > `queue_tier2` > `auto_close` > `notify_owner`.
- **`null` nunca fecha e nunca contém**: dúvida sobre o indício → fila; dúvida sobre esperado → avisa o dono;
  indício com `ativo_critico` ou `em_andamento` nulos → fila.
- `atividade_esperada = true` e `indicio = true` não coexistem nos dados: "esperada" exige que o contexto cubra o
  alerta inteiro; se sobra um pedaço hostil sem explicação, `atividade_esperada = false`.
- "Indício sem confirmação" do briefing vira: indício que não fecha as três condições (parou, ou ativo não
  crítico) ou indício `null`. Indício em ativo crítico E ainda em andamento contém mesmo sem confirmação: conter é
  reversível (derrubar sessão, isolar nó), esperar não é.
- Indício em andamento em ativo NÃO crítico → `queue_tier2` (ninguém é acordado por causa da wiki ou de uma
  máquina de dev com base sintética; o analista contém no horário dele).

## Decisões específicas
- **Credencial possivelmente exposta, sem sessão aberta**: os casos sempre dizem o estado ("conta travada pela
  regra de anomalia", "token revogado às 22:15", "sessão ativa"). Não há caso de "sessão encerrada e credencial
  ainda válida sem ninguém ter mexido" — fronteira evitada de propósito.
- **Operacional grave não é `contain_now`**: não há o que conter. Vai ao dono; a urgência sai dos sinais.
- **Título não decide**: há título assustador com detalhe benigno (EDR gritando para ferramenta do próprio time)
  e título banal com detalhe grave (disco enchendo por arquivo compactado saindo para fora).
- **Alerta repetido**: mesmo valor + chamado aberto + dono ciente → esperado; mesmo alerta sem chamado → dono;
  "mesmo" alerta com valor ou detalhe diferente (escalada, origem nova) → julgado como alerta novo.
- **Teste de intrusão**: esperado só com as três coisas batendo — alvo no escopo, hora na janela, origem
  registrada. Qualquer uma fora → indício.
- **Deploy**: explica reinício, pico curto e erro durante a troca; não explica o que persiste além do prazo
  normal informado, nem processo estranho na imagem.
- **Manutenção**: explica o ativo e a janela anunciados; depois do fim registrado, ou em outro ativo, não explica.
- **Exposição não é comprometimento**: porta aberta ou regra frouxa sem acesso registrado → dono, não fila.

## Famílias de caso difícil (`nota` começa com "difícil: <família>"; todas nos dois conjuntos)
1. `manutenção fora da janela` — anunciada, mas a hora ou o ativo não batem.
2. `alerta repetido` — com chamado e igual × sem chamado × piorou ou mudou.
3. `login impossível` — VPN ou viagem conhecida × sem explicação × indecidível.
4. `teste de intrusão` — no escopo × fora do escopo, da janela ou da origem.
5. `pico após deploy` — explicado × persiste × processo estranho junto.
6. `exfiltração lenta` — em curso × encerrada × rotina conhecida que parece exfiltração.
7. `dado de produção fora de produção` — dev/homolog com cópia de produção (e produção que não é crítica).
8. `tentativa barrada` — 100% barrada não é indício × a mesma tentativa com um sucesso no meio.
9. `indício encerrado` (em ativo crítico) e `indício em ativo não crítico` (em andamento).
10. `título engana` — assustador com detalhe benigno; banal com detalhe grave.
11. `contexto não cobre` — deploy de outro serviço, deploy antigo, causa conhecida sem efeito planejado.
12. `operacional grave` — sem indício (tentação de conter).
13. `usuário legítimo, ação incomum` e `sinal indecidível` (`null`).
14. `backup` — sucesso que é falha silenciosa; "falha" que é política; exclusão em massa.

## Contagens (validador do rotulador, 2026-10-01, zero erros)
| arquivo | casos | difíceis | `auto_close` | `notify_owner` | `queue_tier2` | `contain_now` |
|---|---|---|---|---|---|---|
| `rascunho.json` | 5 | 0 (por desenho) | 2 | 1 | 1 | 1 |
| `ajuste.json` | 40 | 28 (70%) | 12 (30%) | 12 (30%) | 10 (25%) | 6 (15%) |
| `teste.json` | 80 | 51 (63%) | 23 (28%) | 23 (28%) | 21 (26%) | 13 (16%) |

Sinais, `true` / `false` / `null` (ajuste · teste): `atividade_esperada` 12/28/0 · 23/57/0; `ativo_critico` 31/9/0 ·
61/18/1; `indicio_de_comprometimento` 14/24/2 · 30/46/4; `em_andamento` 30/10/0 · 51/29/0.
Casos com sinal `null`: `TA-A023`, `TA-A038`, `TA-T045`, `TA-T059`, `TA-T065`, `TA-T070` (todos `queue_tier2`).
`ativo_critico` contra `ambiente` (ajuste · teste): produção não crítica 2 · 6; fora de produção e crítico 2 · 4.

Por fonte (ajuste / teste): `monitoramento` 10/17 · `auth` 8/14 · `banco` 8/13 · `edr` 5/16 · `waf` 4/8 · `backup`
3/7 · `fila` 2/5. Por ambiente: `prod` 31/64 · `homolog` 4/8 · `dev` 5/8.

Por família difícil (ajuste / teste; a família é o primeiro rótulo da nota): título engana 3/5 · pico após deploy
3/4 · alerta repetido 3/4 · teste de intrusão 2/4 · dado de produção fora de produção 2/4 · exfiltração lenta 2/3 ·
tentativa barrada 2/3 · indício em ativo não crítico 2/2 · backup 2/2 · indício encerrado 1/5 · manutenção fora da
janela 1/4 · login impossível 1/3 · contexto não cobre 1/3 · operacional grave 1/2 · sinal indecidível 1/2 ·
usuário legítimo, ação incomum 1/1.

O validador conferiu: envelope, campos e ordem, enums (`fonte`, `ambiente`, `acao`), `sinais` com as quatro chaves
e valores `true | false | null`, **`acao` igual à função de precedência aplicada aos `sinais`** em todos os casos,
`atividade_esperada` e indício nunca juntos, `null` só com explicação na nota, `contexto` de 0–5 linhas, IDs em
sequência, mínimos, ≥ 30% difíceis, nenhum alerta repetido (nem entre arquivos), todo IPv4 dentro de `10.0.0.x`
ou das faixas de documentação, UTF-8 sem BOM, LF.

## Ambiguidades decididas pelo rotulador (não estavam no briefing)
- `acao` é função mecânica dos quatro sinais (a tabela acima); `acao` nunca é `null`.
- Indício não confirmado em ativo crítico e em andamento → `contain_now` (conter é reversível). "Indício sem
  confirmação → `queue_tier2`" do briefing ficou como: indício que parou, indício em ativo não crítico, ou indício `null`.
- Tentativa 100% barrada não é indício: vai ao dono (ou fecha, se o contexto a explica).
- Operacional grave sem indício é `notify_owner`; a urgência do aviso é do código (`ativo_critico` + `em_andamento`).
- `ativo_critico` não é `ambiente = prod`: wiki e página de situação em produção são `false`; dev/homolog com
  cópia de produção é `true`.
- `em_andamento` vale para qualquer alerta e inclui artefato hostil ainda instalado.
- Causa conhecida sem efeito planejado não é `atividade_esperada`; alerta repetido só é esperado com chamado
  aberto, dono ciente e mesmo valor; exposição sem acesso não é indício.
- A fronteira "sessão encerrada, credencial ainda válida, ninguém mexeu" foi evitada: os casos dizem o estado.
