# Compromisso real (chat de trabalho, pt-BR) — compromisso / proposta / cancelado / citação antiga / pedido sem aceite + prazo

Uma conversa curta de equipe (chat ou e-mail, 2–6 mensagens) com `data_referencia` e candidatos já marcados (trecho
literal + responsável candidato); para CADA par o sistema diz se, no fim da conversa, a pessoa deve a entrega
(`compromisso`), só ofereceu ou condicionou (`proposta`), foi desfeito depois (`cancelado`), é texto citado de antes
(`citacao_antiga`) ou é pedido que ninguém aceitou (`pedido_sem_aceite`) — e, quando há dia resolvível, o `prazo`
(`AAAA-MM-DD`). Uma requisição ao Jev por conversa, com as perguntas de todos os candidatos. Os números vêm dos
relatórios gerados pelo `run.py`: rodada cega em [`resultados-rodada1.md`](resultados-rodada1.md); rodada 2 (depois
da revisão do Codex, NÃO cega — seção no fim) em [`resultados.md`](resultados.md).

**Nada é executado daqui**: `compromisso` é PROPOSTA de tarefa com dono e dia; `cancelado` é proposta de fechamento;
`revisar` (6ª saída, do sistema, nunca do gabarito) é sinal para um humano olhar. O consumidor não cria nem cancela
tarefa a partir de `revisar` nem de falha (lição 26: a resposta do Jev não é autorização).

## Problema
A dor (briefing, seção S): "posso mandar sexta", "ficou para a próxima semana", "não precisa mais" — tarefa fantasma
ou compromisso? Erros caros, dos dois lados:
- **tarefa fantasma**: `proposta`, `cancelado`, `citacao_antiga` ou `pedido_sem_aceite` que sai `compromisso` (uma
  tarefa com dono e dia é criada do nada — inclusive a partir de e-mail antigo colado na conversa);
- **compromisso perdido**: `compromisso` real que sai `cancelado` ou `citacao_antiga` (a tarefa é fechada);
- **prazo errado** num `compromisso` acertado (a tarefa existe, com o dia errado).

O que confunde (famílias do [LEIA-ME](dados/LEIA-ME.md)): citação antiga (e-mail, ata, changelog, resposta
automática), responsável ambíguo ("alguém", "a gente", ausente), cancelamento implícito ("já resolvi", projeto
cancelado, troca de dono), prazo herdado do pedido ou de resposta posterior, pedido sem aceite ("vou ver minha
agenda"), aceite condicional ("se o cliente mandar os extratos"), correção tardia (asterisco, "ops, quarta não"),
proposta × compromisso, aceite curto ("👍"), oferta aceita ("manda sim").

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| No fim da conversa, {responsável} deve esta entrega — e, se não, por quê? | Jev, Choice `commitment / proposal / cancelled / old_quote / unaccepted_request` por candidato (**variante principal**) | catálogo fechado de 5 classes com precedência do LEIA-ME escrita nas regras (lição 37) |
| Mesmo julgamento em quatro sinais (`accepted`, `undone`, `quoted`, `open_request`) | Jev, 4 Nouls por candidato, mesma requisição — **variante informativa** `nouls`; `choice+nouls` consulta-os só onde a Choice hesita | comparação Choice × Nouls (lição 32); não decidem |
| QUAL expressão de tempo dá o dia da entrega (ou nenhuma) | Jev, Choice entre **expressões lidas pelo código** (`"m1: até sexta"`) + `none` | o Jev aponta, nunca compara datas nem faz conta (limite #3) |
| Extrair as expressões ("sexta", "sexta da semana que vem", "dia 15", "15/10", "amanhã de manhã", "em 3 dias úteis", "até o fim do mês", "semana que vem") e RESOLVER contra `data_referencia` pela tabela do LEIA-ME; números por `_comum/numeros_br.py` | **código** (`compromisso.expressoes_de` / `resolver`, bateria própria de 52 casos) | calendário é do código (limites #2/#3) |
| Expressão ÚNICA dentro do próprio trecho = o prazo (`PRAZO_DO_TRECHO`), desde que esteja na ORAÇÃO DA ENTREGA (rodada 2: não depois de "se/desde que/assim que…", não em citação, não em oração que nomeia outra pessoa); fora disso o Jev decide e, sem confiança, `revisar` | **código** (regra do LEIA-ME: "a data é a da entrega, esteja ela no trecho…") | fato literal; a Choice fica registrada para comparação |
| Mensagem e autor do trecho, mensagens do responsável, trecho entre aspas / linha `>` / depois de "Em dd/mm/aaaa, Fulano escreveu:" | **código** → entram no state como fatos | o modelo não lê posição com segurança (lição 29) |
| Trecho entre aspas que a Choice chama de `commitment` → `revisar` (`GUARDA_CITACAO`) | **código** | regra 8 do briefing: texto citado não cria tarefa sozinho |
| Vencedor abaixo do piso (0,5) → `revisar`; prazo abaixo do piso ou `none` → nulo; `prazo` sempre nulo em `cancelado`/`citacao_antiga`/`revisar`; validação da resposta (IDs, tipos, vencedor entre as opções, distribuição) | **código** | ausência de resposta é erro, nunca `compromisso` |
| Falha operacional → tudo `revisar` naquela conversa, `prazo` nulo, `origem: "falha"`; resposta com JSON válido que o contrato rejeitou sai do cache (só ela) | **código** (`compromisso.julgar_seguro`) | contada à parte, fora da métrica |
| Criar/fechar tarefa, responder no chat | processo que chama (e humano) | efeito não é do Jev |

## Desenho
State `{"reference_date", "messages": [{"id", "author", "text"}], "candidates": [{"id", "excerpt", "owner",
"in_message", "excerpt_author", "owner_is_author", "owner_messages", "inside_quotes"}]}` — a conversa inteira (2–6
mensagens curtas) mais os fatos de código por candidato. Por candidato: a Choice de veredito (pergunta cita o par, a
mensagem, o autor e as regras do LEIA-ME em inglês — precedência citado > desfeito > estado do que sobrou, oferta
aceita, condição de terceiro, "vou tentar", troca × confirmação, troca de dono, pedido a "alguém", recusa,
responsável ausente, "a gente", citação reafirmada, cancelamento implícito), os quatro Nouls (regras curtas) e, se o
código achou expressões de tempo na conversa, a Choice do prazo. Tudo em [`perguntas.py`](perguntas.py); lógica em
[`compromisso.py`](compromisso.py).

Uma conversa com 2–4 candidatos vira 12–24 perguntas numa requisição, ≈ 10 mil tokens (a descrição das 5 classes e
as regras se repetem por candidato). Teto de 8 candidatos / 4.000 caracteres (acima → tudo `revisar`, origem `longa`).

## Baseline (código, sem Jev)
`compromisso.baseline`: aspas → `citacao_antiga`; mensagem posterior de outra pessoa com palavra de cancelamento E
palavra em comum com a mensagem do trecho (ou "eu pego"/"deixa que eu") → `cancelado`; trecho é pedido ao
responsável ("pode…?", "consegue…?", "preciso…") → ele aceitou depois ("sim", "consigo", "👍", verbo em 1ª pessoa)?
`compromisso` : `pedido_sem_aceite`; hedge ("posso", "que tal eu", "vou tentar", "se o cliente") → `proposta` (ou
`compromisso` se alguém disse "manda sim"); verbo de compromisso em 1ª pessoa → `compromisso`. Prazo: primeira
expressão do trecho, senão da mensagem, senão da anterior — pelo mesmo resolvedor. Segunda referência: **sempre
`compromisso`** (acerta 57/102 = 0,559 dos candidatos do teste).

## Critério de continuar/descartar (fixado ANTES de abrir o teste)
Manifesto `congelamento.json` gravado em **2026-10-01 16:10:27 (−03:00)**, depois da 2ª passada do ajuste; o teste
foi aberto e rodado UMA vez depois disso (`perguntas.py` `6ee7f8a8524eeac8…`, `compromisso.py` `393133a6e07bb0d1…`,
`run.py` `ede2eb604d43f82c…`, `dados/teste.json` `2d603138083f3ea4…`). Variante principal declarada: `choice`. No
teste (46 conversas, 102 candidatos; 57 `compromisso`, 45 não): (1) tarefa fantasma ≤ 3 de 45; (2) compromisso
perdido ≤ 3 de 57; (3) prazo igual ao gabarito nos `compromisso` acertados ≥ 0,85; (4) veredito exato ≥ 0,80
(`revisar` conta como erro; sempre-compromisso = 0,559); (5) veredito exato nos 45 não-compromisso ≥ 0,70.
Secundário (não decide): `revisar` ≤ 15%; prazo exato nos vivos acertados ≥ 0,85. Limites absolutos no erro caro +
piso de acerto; o baseline é informativo. O veredito é calculado pelo `run.py`.

## Resultados (`jev-1.13.0`, 2026-10-01; detalhes, curvas e caso a caso nos relatórios) [testado]
Rascunho = 5 conversas fáceis (10 candidatos): 10/10 vereditos e 8/8 prazos nas duas passadas, só encanamento.
Ajuste = 23 conversas (47 candidatos; 21 difíceis), afinado em duas passadas; teste = 46 (102 candidatos; 43
difíceis), uma rodada, cega.

| | ajuste (23 conv., 47 cand.) | **teste (46 conv., 102 cand.)** |
|---|---|---|
| baseline: total · não-compromisso · **fantasma** · **perdido** · enfraquecido · prazo compromissos · prazo vivos | 0,872 · 0,783 · 5/23 · 0/24 · 1/24 · 21/23 · 32/34 | 0,716 · 0,600 · **11/45** · 0/57 · 11/57 · 40/46 · 57/65 |
| sempre `compromisso`: total · fantasma | 0,511 · 23/23 | 0,559 · 45/45 |
| **Jev `choice`** (principal): total · não-compromisso · **fantasma** · **perdido** · enfraquecido · `revisar` · prazo compromissos · prazo vivos | 1,000 · 1,000 · 0/23 · 0/24 · 0/24 · 0/47 · 24/24 · 36/36 | **0,961 (98/102) · 0,933 (42/45) · 0/45 · 0/57 · 0/57 · 2/102 · 54/56 · 73/76** |
| Jev `nouls` (informativa): total · fantasma · perdido · enfraquecido · `revisar` | 0,851 · 0/23 · 0/24 · 0/24 · 7/47 | 0,843 · 0/45 · 0/57 · 1/57 · 14/102 |
| Jev `choice+nouls` (informativa): total · fantasma · perdido · enfraquecido · `revisar` | 1,000 · 0 · 0 · 0 · 0 | 0,971 (99/102) · 0/45 · 0/57 · 1/57 · 0/102 |
| Jev `choice` por classe (acertos/gabarito): compromisso · proposta · cancelado · citacao_antiga · pedido_sem_aceite | 24/24 · 5/5 · 7/7 · 4/4 · 7/7 | 56/57 · 10/10 · 15/17 · 7/7 · 10/11 |
| cobertura do extrator de datas (gabarito entre as expressões ou nulo) | 36/36 | 78/78 |
| p50 / p95 · tokens por conversa · US$ por mil conversas | 343 / 389 ms · 9.517 · 0,40 | 339 / 414 ms · 10.379 · 0,44 |

**Critério no teste: passou os cinco** — (1) 0/45 ✓ · (2) 0/57 ✓ · (3) 54/56 = 0,964 ≥ 0,85 ✓ · (4) 0,961 ≥ 0,80
✓ · (5) 0,933 ≥ 0,70 ✓. Secundários: `revisar` 2/102 = 2% ✓ · prazo nos vivos 73/76 = 0,961 ✓. Nenhum no limite
(folga: 3 fantasmas, 3 perdidos, 6 prazos, 16 candidatos no total, 10 nos não-compromisso).

Ajuste, 1ª passada (perguntas escritas do LEIA-ME, sem olhar resposta): veredito 47/47 com P do vencedor ≥ 0,86 —
**fácil demais para calibrar o piso** (curva plana de 0,0 a 0,8; `P_MIN_VENCEDOR` ficou no 0,5 de partida); prazo
31/36 nos vivos. Em 3 dos 5 erros de prazo (CR-A010 "até terça", CR-A015 "à tarde", CR-A016 "agora") a expressão
estava DENTRO do próprio trecho e o Jev apontou outra mensagem; CR-A012 herança "terça" certa mas a 0,49; CR-A008
pegou o "amanhã" da entrega de OUTRA pessoa. Nouls: 30/47 `revisar`, porque o `undone` quase não separava
(cancelado 0,50–0,70 × compromisso 0,14–0,68) e a dúvida bloqueava a precedência. 2ª passada: (a) regra do LEIA-ME
em código — expressão única dentro do trecho é o prazo — e dita na pergunta, que ganhou "entrega de OUTRA pessoa →
none" e "'só depois que…' → none"; (b) `por_nouls`: dúvida não bloqueia sinal conclusivo posterior; (c) Nouls com
regras curtas (15,8 mil → 9,5 mil tokens por conversa). Resultado: 47/47 e 36/36; Nouls 0,851 com `undone`
separando (0,65–0,96 × ≤ 0,11). O texto da Choice de veredito não mudou entre as passadas; nada foi escrito para
um caso só.

Regra "prazo do próprio trecho" × escolha do Jev, nos vivos acertados do teste: a regra foi aplicada em 61
candidatos e acertou 60; a Choice do prazo sozinha acertaria 57 desses 61 (discordaram em 5; a regra ganhou 4,
perdeu 1 — CR-T043). Nos 15 sem regra (zero ou duas+ expressões no trecho: herança do pedido, resposta posterior),
o Jev acertou 13.

Por família (teste, acerto do Jev × baseline): cancelamento implícito 10/10 × 4/10 · prazo 10/10 × 10/10 · citação
antiga 18/18 × 16/18 · correção tardia 11/12 × 7/12 · **pedido sem aceite 9/12 × 10/12** · responsável ambíguo
14/14 × 9/14 · aceite condicional 8/8 × 6/8 · proposta × compromisso 7/7 × 5/7 · aceite curto 2/2 · oferta aceita
2/2 × 0/2 · fáceis 7/7 × 4/7.

Curva do teste (mesmas respostas, outro piso; informativa): piso 0,4 → cobertura 100%, **1 tarefa fantasma**
(CR-T023 k3, `commitment` 0,47); piso 0,5 (congelado) → 98%, 0; piso 0,6 → 95,1%, acerto 0,931. Os dois `revisar`
do teste são exatamente os dois vencedores abaixo de 0,5, e um deles seria fantasma.

Custo total da construção: **102 requisições** (orçamento 400): 5 + 23 (1ª passada), 5 + 23 (2ª), 46 de teste;
**1.181.570 tokens de entrada, US$ 0,0496**. Nenhuma resposta sobrescrita (`cache/historico` não existe); o manifesto
da rodada cega está em `congelamentos-anteriores/2026-10-01T16-10-27-03-00.json` (o atual é o da rodada 2).

## O que deu certo
- **Zero tarefa fantasma e zero compromisso perdido no teste** (0/45 e 0/57) — as duas dores — contra 11/45
  fantasmas do baseline (9 `cancelado` lidos como compromisso: regex não vê cancelamento implícito, troca de dono
  nem "a gente" desdobrado).
- Citação antiga 7/7 vereditos e 18/18 candidatos da família; a guarda de código (aspas → nunca `compromisso`) não
  precisou agir no teste (a Choice já disse `old_quote` em todos), mas está provada na bateria para o caso
  "considerem isto confirmado" dentro de citação.
- Prazo: o extrator cobriu 78/78 (toda data do gabarito estava entre as expressões resolvidas pelo código); 73/76
  nos vivos acertados, com herança do pedido ("Eu pego." → "até sexta" do pedido; "Deixa que eu respondo" → "hoje")
  e troca tardia ("*sexta, quinta eu tô no outro cliente" → sexta) certas.
- Oferta aceita 2/2, aceite curto 2/2, aceite condicional 8/8 ("desde que o cliente pague" → `proposta`).
- O piso 0,5 segurou o único vencedor errado acima de `cancelled` (CR-T023 k3, `commitment` 0,47) — virou `revisar`
  em vez de tarefa fantasma.

## O que falhou no teste (NÃO corrigido)
Quatro vereditos em 102 e três prazos (dois em `compromisso`), em sete conversas:

| Caso | O que a conversa diz | Saída (gabarito) | Causa |
|---|---|---|---|
| CR-T007 k3 (Hugo) | "o relatório de dezembro até dia 18" → Hugo: "dia 18 tá em cima das minhas férias" → Lívia: "Então antecipa para o dia 16 também?" (sem resposta) | `pedido_sem_aceite → 2026-12-18` (`cancelado`) | `unaccepted_request` 0,81 × `cancelled` 0,17: o modelo leu o pedido original como contestado-sem-aceite; o rotulador diz que a proposta de nova data o substituiu. **Rótulo disputável**: a nova data também não foi aceita (k2 é `pedido_sem_aceite`), e o LEIA-ME manda "recusa → pedido_sem_aceite" |
| CR-T017 k2 (Aline) | "consegue organizar o arquivo morto este mês?" → Aline: "Que tal eu começar pelas caixas de 2020…" → "Deixa eu pensar" | `proposta` (`pedido_sem_aceite`) | `proposal` 0,78: a contraproposta da própria responsável (k3, `proposta`) contaminou o pedido original. A regra "contraproposta é OUTRA entrega; o pedido segue sem aceite" não está nas perguntas (nem no LEIA-ME em palavras) |
| CR-T022 k2 (Paula) | Paula pede laudo a Fábio; Duda: "o cliente da farmácia ligou de novo"; Paula: "Eu retorno para ele agora." | `revisar` (`compromisso → 2026-10-07`) | `unaccepted_request` 0,47 × `commitment` 0,43 → piso. O modelo leu a frase de Duda como pedido a Paula sem aceite, apesar da 1ª pessoa; os Nouls também erraram (`accepted` 0,09; variante `nouls` deu `proposta`). Único `compromisso` não acertado; não é caro |
| CR-T023 k3 (Jonas) | "A cliente pediu três opções de logo até segunda. Jonas, consegue?" → "é apertado" → "mando duas na segunda e a terceira na quarta" | `revisar` (`cancelado`) | `commitment` 0,47 × `cancelled` 0,26: o pedido original desdobrado em duas entregas. O piso segurou a tarefa fantasma; os Nouls (`undone` 0,73) acertariam — a variante `choice+nouls` deu `cancelado` |
| CR-T013 k2 (Sônia) — prazo | "Vítor precisa assinar até amanhã" → "ele está de férias" → Sônia: "Então assino eu como substituta. Aline, você leva ao cartório na quinta?" | `compromisso → 2026-10-08` (`→ 2026-10-07`) | veredito certo (0,60); sem expressão no trecho, a Choice do prazo apontou "quinta" (0,78) — o dia da OUTRA entrega na mesma mensagem — em vez de herdar o "até amanhã" do pedido que ela assume. **Prazo errado em compromisso** (caro) |
| CR-T014 k3 (Paula) — prazo | "*sexta, quinta eu tô no outro cliente" → Paula: "Ok, sexta. Aviso a diretora." | `compromisso → 2026-10-23` (`→ null`) | a Choice do prazo apontou "sexta" (0,57) da mesma mensagem; o rotulador deixou o aviso sem dia. **Rótulo disputável** (o aviso é sobre a sexta, não para a sexta); conta como prazo errado em compromisso (caro) |
| CR-T043 k1 (Vítor) — prazo | "você protocola o recurso na segunda?" → "Protocolo, desde que o cliente pague as custas até sexta." | `proposta → 2026-11-13` (`→ 2026-11-16`) | **defeito da regra de código**: "até sexta" está dentro do trecho, mas é o prazo da CONDIÇÃO, não da entrega; a regra `PRAZO_DO_TRECHO` a usou enquanto a Choice do prazo apontava "m1: segunda" (0,65), que é o gabarito. Não é caro (é `proposta`) |

Variante informativa `choice+nouls` no teste: 0,971 (99/102), 0 `revisar`, 1 enfraquecido — os Nouls decidiram os
dois casos em que a Choice hesitou, acertando um (T023) e errando o outro (T022 → `proposta`). Não é a principal
(declarada antes do teste) e fica como candidata para dados novos (metodo.md: variante informativa não vira
principal depois do teste).

## Lições
1. **Regra de código sobre fato literal rende, mas tem a borda dela.** "Expressão única dentro do trecho é o prazo"
   acertou 60/61 no teste (o Jev sozinho 57/61) e perdeu o único caso em que a expressão do trecho é de uma
   CONDIÇÃO ("desde que pague até sexta"). A regra devia ceder quando o trecho contém condição de terceiro —
   aplicado só na rodada 2, não cega (seção no fim): ganhou T043 e perdeu T018 ("enquanto isso eu reservo…").
2. **Bloco longo de regras embaralha Nouls atômicos.** Com as regras completas repetidas em cada Noul, `undone`
   não separava (cancelado 0,50–0,70 × compromisso até 0,68) e 30/47 caíam em `revisar`; com três linhas de regra,
   separou (0,65–0,96 × ≤ 0,11) e custou 40% menos. Na Choice, que precisa das 5 classes, o bloco longo ficou.
3. **Os erros moram perto do piso e o piso vale o que custa**: os dois `revisar` do teste são os dois vencedores a
   0,47; um seria tarefa fantasma a piso 0,4. Piso 0,6 custaria 3 pontos de cobertura sem corrigir nada. O ajuste
   no teto (P ≥ 0,86) não calibrou o piso — o teste calibrou, tarde.
4. **"Nouls onde a Choice hesita" rendeu 1 de 2**: a precedência do LEIA-ME em quatro sinais atômicos pegou a
   troca por desdobramento (T023) que a Choice não viu, e repetiu o erro da Choice onde o state confunde quem pede
   a quem (T022). Decomposição ajuda quando a Choice não vê a classe (lição 32), não quando o state é ambíguo.
5. **A família mais fraca é "pedido sem aceite" (9/12)**: contestação, contraproposta e mudança de assunto são
   três jeitos de "não aceitar" que as regras não nomeiam; as três falhas do teste nessa família são rótulos
   defensáveis dos dois lados (T007, T017) ou state ambíguo (T022).
6. **O gabarito de prazo também é interpretação**: "Ok, sexta. Aviso a diretora." (T014) tem leitura "aviso sobre a
   sexta" (rotulador) e "aviso até sexta" (modelo). Registrado; o placar não muda.
7. **Regex perde cancelamento implícito e troca de dono** (9 de 11 fantasmas do baseline são `cancelado`) e acerta
   o prazo quando a expressão está no trecho (40/46).
8. **Um candidato por par, não por trecho**: o mesmo trecho com responsáveis diferentes recebe vereditos diferentes
   ("alguém precisa mandar" → `cancelado` para Hugo, `compromisso` para Tati); a pergunta cita o par e os fatos de
   código do par (quem escreveu, se o responsável falou), e isso funcionou (responsável ambíguo 14/14).

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só, mesmo fornecedor de quem construiu; n = 23/46
  conversas; uma versão do modelo; uma rodada cega. Conversa real é mais suja (threads, respostas fora de ordem,
  áudio transcrito) e tem mais de uma data de referência.
- Candidatos já marcados: o exemplo mede o decisor, não a extração de trechos. Trecho que não é cópia literal de uma
  mensagem é entrada inválida (→ `revisar`).
- Resolvedor de datas segue a tabela do LEIA-ME (dia da semana estritamente depois; "dia N" com a referência
  contando; sem ajuste de feriado/dia útil; "fim da semana" = sexta da semana civil mesmo no sábado). Não lê "ontem",
  "daqui a duas semanas", "próximo mês dia 5", hora sozinha ("às 10h") nem mês solto como data; expressão fora da
  tabela não vira candidato → prazo nulo. Dia inexistente ("29 de fevereiro" em ano não bissexto) → nulo.
- `inside_quotes` conta aspas retas em número ímpar (inclusive a que abre o próprio trecho), tipográficas abertas,
  linha com `>` (mesmo quando o marcador está no trecho) e o que vem depois de "Em dd/mm/aaaa, Fulano escreveu:" na
  mesma mensagem; citação sem aspas (ata colada em texto corrido) depende só do modelo.
- `revisar` junta duas coisas: hesitação do modelo (piso) e trecho citado que a Choice chamou de `commitment`
  (guarda). Para o consumidor é a mesma ação (olhar); para medir, não — o relatório traz o motivo por candidato.
- Mesmo trecho em duas mensagens: a primeira ocorrência é a usada (não aconteceu nos dados).
- Falha operacional provada só por bateria com dublê (`testa_falhas.py`): nenhum conjunto teve falha, conversa longa
  ou resposta fora do contrato.
- Valores perto do piso trocam de lado entre chamadas idênticas (NÚCLEO §6: p95 ~0,05, máximo 0,15): T014 k1
  (`commitment` 0,51 × `cancelled` 0,47) e T023 k2 (0,55) estão nessa zona.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa se o manifesto congelamento.json não bate)
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação (marca "em afinação")
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 casos fáceis → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # grava o manifesto (código, teste.json, critério); o anterior vai para congelamentos-anteriores/
set JEV_MODO=gravado                              # só o cache/ (102 respostas reais), sem chave
..\..\.venv\Scripts\python.exe testa_falhas.py   # bateria do código: falha operacional, política, aspas, extração, datas (sem chave, sem rede)
```
No Windows, use `PYTHONIOENCODING=utf-8`. A primeira execução com o teste grava `resultados-rodada1.md` e nunca o
reescreve. Como serviço: `compromisso.julgar_seguro(jev, caso)` devolve `vereditos`, `prazo`, `origem` (`jev` /
`falha` / `longa`) e `motivo`, e **não levanta**: entrada inválida, erro da chamada ou resposta fora do contrato →
tudo `revisar`, `prazo` nulo, `origem: "falha"` (nunca `compromisso` nem `cancelado`); resposta com JSON válido que o
contrato rejeitou sai do cache (`cache/invalidos/`) para só ela ser refeita na próxima rodada. `compromisso.julgar` é
o baixo nível, que levanta a exceção.

## Pós-revisão do Codex (2026-10-01) — rodada 2, não cega
Revisão adversarial depois da rodada cega; quatro achados (gravidade 2), todos em `compromisso.py`, aplicados sem
mudar pergunta, limiar, política nem critério — e sem olhar o teste para afinar: o que entrou é a lista triada, nem
mais, nem menos. Manifesto refeito (`congelamento.json`, 16:30:34; `compromisso.py` `908e2b385fc624ec…`; o da rodada
cega está em `congelamentos-anteriores/`). State e perguntas ficaram idênticos nas 69 conversas: **0 chamadas novas,
0 tokens, US$ 0** (orçamento era 150); a rodada 2 é a mesma resposta do Jev com o código novo por cima.

| # | O que era | O que mudou |
|---|---|---|
| 1 | Resposta com JSON válido rejeitada pela validação ficava no cache: em `auto`, toda rodada repetia o `revisar` daquela conversa | `julgar_seguro` chama `jev.invalidar(state, questions)` só na etapa "resposta inválida" (não em falha de chamada nem de entrada), embrulhado para nunca derrubar a falha fechada; a conversa continua saindo toda `revisar`, origem `falha`. Bateria: dublê registra que invalidou exatamente o pedido rejeitado (e só ele num lote de 4), e que invalidar que quebra ou cliente sem `invalidar` não mudam o desfecho |
| 2 | "quinta, dia 5 de novembro" (referência 2026-10-01) virava 2026-10-05: a regex pegava "quinta, dia 5" e a sobreposição eliminava a expressão com o mês | Dia da semana seguido de data completa (dia + mês [+ ano], "sexta, 6/11", "quinta 5/11 às 18h", "5 de nov") é UMA expressão (`dia_semana_data`); mês e ano explícitos mandam sobre o dia da semana e sobre a referência; mês abreviado aceito. Bateria: 9 resoluções e 5 extrações novas, inclusive mês sem ano em dezembro → janeiro |
| 3 | Atalho "expressão única no trecho é o prazo" pegava o prazo da CONDIÇÃO (T043) e valia também em `compromisso` | O atalho só vale quando a expressão está na ORAÇÃO DA ENTREGA: não depois de conectivo condicional/temporal na mesma oração ("se", "desde que", "assim que", "quando", "enquanto"…), não dentro de citação, não em oração que nomeia outra pessoa (autor da conversa ou "o/a Nome" ≠ responsável). Fora disso o Jev decide entre as opções; se não aponta com confiança (abaixo do piso), prazo nulo e o candidato sai `revisar`. Bateria: condição cumprida depois (T043 + "ele pagou agora" → o Jev aponta "segunda"), citação e data de terceiro |
| 4 | Trecho que começa por `> ` deixava `antes` vazio → `inside_quotes=False`; a guarda não agia | A linha inteira do trecho é lida (marcador dentro do trecho conta), a aspa que abre o próprio trecho conta, e tudo depois de um cabeçalho "Em dd/mm/aaaa, Fulano escreveu:" (ou linha terminada em "escreveu:") na mesma mensagem é citado. Bateria com os dois formatos |

**Rodada 1 (cega) × rodada 2 (não cega)**, teste, variante principal `choice`:

| | rodada 1 | rodada 2 |
|---|---|---|
| veredito exato | 0,961 (98/102) | 0,961 (98/102) |
| não-compromisso | 0,933 (42/45) | 0,933 (42/45) |
| tarefa fantasma | 0/45 | 0/45 |
| compromisso perdido | 0/57 | 0/57 |
| `revisar` | 2/102 | 2/102 |
| prazo nos compromissos acertados (critério 3) | 54/56 = 0,964 | **53/56 = 0,946** |
| prazo nos vivos acertados | 73/76 | 73/76 |
| cobertura do extrator | 78/78 | 78/78 |
| baseline (regex): total · fantasma | 0,716 · 11/45 | 0,716 · 11/45 |
| critério | passou os cinco | passou os cinco |
| chamadas novas · tokens · US$ | 46 (teste) | 0 · 0 · 0 |

Ajuste: idêntico (47/47, 36/36). Variantes informativas no teste: iguais, exceto o prazo de T018 (`choice+nouls` 54/56 → 53/56).

**O que mudou caso a caso (3 candidatos):**
- **Melhorou — CR-T043 k1** (Vítor, "Protocolo, desde que o cliente pague as custas até sexta."): "sexta" está depois de
  "desde que" → sem atalho; o Jev já apontava "m1: segunda" (0,65) → `proposta → 2026-11-16`, igual ao gabarito.
- **Piorou — CR-T018 k1** (Hugo, "Enquanto isso eu reservo a sala de edição para quarta."): "quarta" vem depois de
  "enquanto" na mesma oração e a regra leu como condição; sem o atalho, o Jev apontou "m1: amanhã" (0,59, o dia do pedido
  ao Jonas) → `compromisso → 2026-10-27` (gabarito 2026-10-28). **Prazo errado em compromisso acertado (caro)**; é o que
  levou o critério 3 de 0,964 a 0,946. Causa: "enquanto isso" é advérbio ("nesse meio-tempo"), não conectivo
  condicional — a lista de conectivos não distingue. NÃO corrigido: o caso veio do teste e mexer na lista agora seria
  afinar olhando o teste; fica para dados novos.
- **Igual — CR-T038 k1** (Nanda, "Posso ficar no plantão de sábado no lugar do Fábio…"): a oração nomeia o Fábio (outro
  autor) → sem atalho; o Jev apontou o mesmo "sábado" (0,81). Saída inalterada.

Saldo do item 3 no teste: 1 ganho, 1 perda, 1 empate — a regra em código continua com a borda dela (lição 1), agora do
outro lado: um advérbio temporal parece conectivo. Os itens 1, 2 e 4 não tocaram nenhum caso dos conjuntos (nenhuma
conversa tem data completa depois de dia da semana, `>` no trecho ou cabeçalho de e-mail); estão provados só na bateria.
