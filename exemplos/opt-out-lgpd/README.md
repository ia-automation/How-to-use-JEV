# Opt-out e LGPD (WhatsApp, pt-BR) — bloquear_envios / abrir_pedido_lgpd / pausar / seguir / revisar

"Não me mande mais mensagem", "apaga meus dados", "quem te passou meu número?": cada uma exige uma ação
imediata e diferente. Este exemplo julga UMA mensagem de cliente por requisição e devolve a ação. Os números
vêm dos relatórios gerados pelo `run.py`: a rodada cega está preservada em
[`resultados-rodada1.md`](resultados-rodada1.md) e a rodada 2 (pós-revisão do Codex, **não cega**) é o
[`resultados.md`](resultados.md) atual. Candidato a guarda de entrada da Luci/0010: roda em cada mensagem
recebida, antes de o agente responder.

**Isto não é parecer jurídico.** As regras são as de [`dados/LEIA-ME.md`](dados/LEIA-ME.md), escritas para este
exemplo (quatro tipos de direito, uma leitura de "opt-out"); o que a lei exige de cada operação é assunto do
encarregado. **Nada é executado daqui**: bloquear envio, abrir pedido e pausar são efeitos do processo que
chama, com a permissão dele — `abrir_pedido_lgpd` abre um pedido para o encarregado, não apaga nada.

## Problema
Conversa de SDR/atendimento de imobiliária por WhatsApp. O erro caro tem dois lados:
- **infração**: opt-out ou pedido de titular real que sai `seguir` (a empresa continua mandando, ou ignora o
  pedido). Logo atrás, a obrigação cumprida pela metade: opt-out que vira `pausar`, pedido LGPD sem pedido
  aberto, pedido aberto sem parar o envio de quem também pediu para parar;
- **perda comercial**: cliente interessado cujo envio é bloqueado ("não precisa parar, pode mandar"; "para de
  mandar apê sem vaga"; "não quero mais ESSE apê").

O que confunde: pausa × definitivo ("me chama mês que vem" × "não quero mais, se precisar eu procuro");
preferência de canal; filtro; negação; ironia; terceiro (o recado sobre o número da mãe × o número deste
canal que é da mãe); "para" / "não quero mais" sem objeto (indecidível → humano); "tirar da lista" (opt-out)
× "encerrar cadastro" (exclusão).

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| A mensagem pede para parar o contato neste número? | Jev, Noul `opt_out` | julgamento semântico, espaço fechado (sim/não) |
| Pede pausa com prazo ou condição de retomada? | Jev, Noul `temporary_pause` | idem; coexiste com as outras, então é pergunta separada |
| Exerce direito de titular? | Jev, Noul `lgpd_request` (absoluto) | é o portão: a Choice sempre tem vencedor |
| Qual direito? | Jev, Choice `lgpd_type` + `none` | uma de N; consumida só se o Noul passar |
| Diz que podem continuar mandando? · "Para" sem objeto? · Pedido sobre o número de outra pessoa? | Jev, três Nouls de guarda | segunda leitura do lado caro; mesma requisição |
| Exclusão ⇒ opt-out; "continuem mandando" → `revisar` com o envio suspenso (rodada 2) | **código** | é regra do LEIA-ME, não julgamento; guarda não dispensa obrigação sozinho |
| Precedência (LGPD > opt-out > pausa > seguir), faixas, dúvida → `revisar` | **código** | política por risco; mudar = editar número |
| Validar a resposta (IDs, tipos, números em [0,1]), teto da mensagem; falha operacional → `revisar` por mensagem (rodada 2) | **código** | ausência de resposta é erro, nunca `seguir` |
| Bloquear, abrir o pedido, pausar, responder ao cliente | processo que chama (e LLM/modelo de resposta) | efeito e texto não são do Jev |

## Desenho
State `{"message": "<texto>"}`; uma requisição com 7 perguntas (6 Nouls + 1 Choice), em inglês, todas em
[`perguntas.py`](perguntas.py) com as faixas e o critério. O `false` de cada Noul lista os casos do medo
(negação, pausa, canal, filtro, terceiro, fim de interesse). Decisão em [`optout.py`](optout.py):

1. `lgpd_request` ≥ 0,7 → `abrir_pedido_lgpd(tipo)` com o tipo da Choice (vencedor `none` ou confiança < 0,5 →
   `revisar`). `bloqueia` = sim se o tipo é exclusão (regra de código) ou se `opt_out` também passou; nos outros
   tipos, `opt_out` em dúvida deixa o bloqueio **pendente** (`None`: quem atende confirma). Exclusão com
   `wants_contact_to_continue` ≥ 0,7 e sem `opt_out` ≥ 0,7 (exclusão parcial) → `revisar` com o envio
   **suspenso** (`bloqueia` = sim), motivo "exclusão com sinal de continuar: confirmar". Na rodada 1 esse ramo
   abria o pedido **sem** bloquear; mudou na rodada 2 (abaixo).
2. `lgpd_request` entre 0,3 e 0,7 → `revisar`.
3. `opt_out` ≥ 0,7 → `bloquear_envios`; vetos (qualquer guarda ≥ `sim`, ou pausa junto) → `revisar`.
4. `opt_out` entre 0,2 e 0,7 → `revisar`; `stop_without_object` ≥ 0,5 → `revisar`.
5. `temporary_pause` ≥ 0,6 → `pausar`; entre 0,4 e 0,6 → `revisar`; senão `seguir`.

Política assimétrica: o `nao` de `opt_out` e de `lgpd_request` fica colado no grupo dos falsos, e **dúvida
nunca vira `seguir`**. Mensagem acima de 2.000 caracteres não vai ao Jev (`revisar`; não disparou: a maior do
teste tem 253).

Duas regras da rodada 2 (revisão do Codex), as duas de código:
- **Um Noul de guarda nunca é a razão única para não cumprir uma obrigação.** Guarda só move para `revisar`:
  não libera envio, não leva a `seguir`. Conferido na grade inteira de `decidir` pela bateria.
- **Falha operacional é saída, não exceção do lote.** `optout.guardar_seguro` é o que o consumidor chama:
  timeout, erro HTTP, cache faltando, resposta fora do contrato ou mensagem vazia viram `revisar` para AQUELA
  mensagem, motivo `falha operacional: <etapa> (<classe do erro>)`. `optout.julgar`/`decidir` (baixo nível)
  continuam levantando erro. O `run.py` roda pelo invólucro e conta as falhas à parte; conjunto com falha é
  marcado no relatório como "não é medição".

## Baseline (código, sem Jev)
Lista de expressões sem acento (`perguntas.BASELINE_*`): "para de", "pode parar", "não quero mais", "lista",
"descadastr", "spam", "apag", "exclu", "LGPD", "quem passou", "de onde", "meus dados", "corrig", "atualiz",
"mês que vem", "por enquanto", "agora não"… Precedência LGPD > opt-out > pausa > seguir. Não tem `revisar`:
regex não sabe que não sabe. Segunda referência: "sempre revisa" (zero infração, 100% das mensagens a humano).

## Critério de continuar/descartar (fixado ANTES de abrir o teste, 2026-10-01)
No teste (60 mensagens): (1) infração = 0; (2) obrigação pela metade ≤ 1; (3) bloqueio indevido ≤ 1/28 —
"≤ 2%" não é mensurável com n = 28 (só admitiria zero); (4) acerto da ação (5 classes) ≥ baseline + 0,15.
Secundário, não decide: nulo → `revisar`; revisou sem necessidade ≤ 15%; tipo LGPD certo ≥ 85%. 1–3 falhando =
o desenho não serve como guarda sem mudança; 4 falhando = a lista de expressões basta. O critério está no
manifesto `congelamento.json` e o veredito é calculado pelo `run.py`.

## Resultados (`jev-1.13.0`, 2026-10-01; detalhes, curvas e caso a caso nos dois relatórios)
Ajuste = 30 mensagens (15 difíceis, 2 nulas), afinado nele em duas passadas; teste = 60 (30 difíceis, 1 nula).
Duas rodadas, cada uma com o relatório gerado pelo script: 1 (cega) em `resultados-rodada1.md`, 2 (pós-revisão
do Codex, não cega) em `resultados.md`.

### Rodada 1 (cega; [resultados-rodada1.md](resultados-rodada1.md))
Manifesto gravado em 2026-10-01 13:07 (`perguntas.py` `bd839986d8b3eab0…`, `optout.py`
`99515b087057bdad…`, `run.py` `2695bda4d2ae0edf…`, `dados/teste.json` `1207d0b7d4d14d6a…`), teste aberto e
rodado UMA vez depois disso. Os números desta seção ficam como rodaram.

| | ajuste (n = 30) | teste (n = 60) |
|---|---|---|
| baseline: ação · **infração** · pela metade · **bloqueio indevido** · tipo LGPD | 0,733 · 2/14 · 0/14 · 3/14 · 8/9 | 0,717 · **4/31** · 1/31 · **5/28** · 14/18 |
| "sempre revisa": infração · a humano | 0/14 · 30/30 | 0/31 · 60/60 |
| **Jev**: ação · **infração** · pela metade · **bloqueio indevido** · tipo LGPD | 0,967 · 0/14 · 0/14 · 0/14 · 9/9 | **0,883 (53/60) · 0/31 · 0/31 · 0/28 · 16/18** |
| Jev: nulo → `revisar` · revisou sem necessidade | 2/2 · 1/28 | 1/1 · 6/59 (10,2%) |
| Nouls ≥ 0,5: `opt_out` (sem exclusões) · `temporary_pause` · `lgpd_request` | 0,960 · 1,000 · 1,000 | 1,000 (53/53) · 1,000 (60/60) · 0,950 (57/60) |
| Choice `lgpd_type` crua nos pedidos reais · Choice ≠ `none` sem pedido real | 9/9 · 2/21 | 17/18 · 5/42 |
| p50 / p95 · tokens por mensagem · US$ por mil mensagens | 299 / 393 ms · 2.026 · 0,085 | 324 / 663 ms · 2.028 · 0,085 |

**Critério no teste: passou os quatro** — (1) 0/31 ✓ · (2) 0/31 ✓ · (3) 0/28 ✓ · (4) 0,883 ≥ 0,867 ✓, **com um
caso de folga** (53 acertos; o limite é 52/60 = 43/60 do baseline + 0,15, e o critério usa `≥`: 52 passam, 51
reprovam). Secundários: 1/1 ✓ · 10,2% ✓ · 16/18 = 0,889 ✓.

> Correção de texto (revisão do Codex, achado 4): a versão cega deste README dizia "por um caso (53 acertos; 52
> reprovaria)". A conta estava errada; o critério congelado e os números não mudaram.

Matriz do teste, Jev (gabarito → previsto): `bloquear_envios` 10 certos, 1 → abrir pedido, 2 → revisar ·
`abrir_pedido_lgpd` 17, 1 → revisar · `pausar` 5, 2 → revisar · `seguir` 20, 1 → revisar · `revisar` 1/1.
Os 7 erros de ação são 6 `revisar` desnecessários e 1 pedido de exclusão aberto para quem só pediu para sair.

Por família (teste, ação Jev × baseline): negação 5/5 × 2/5 · ironia 3/3 × 3/3 · terceiro 3/5 × 4/5 · pausa ×
opt-out 3/4 × 2/4 · "para" ambíguo 2/3 × 1/3 · reclamação longa 2/2 × 2/2 · tipo de direito duvidoso 3/3 × 3/3
· origem sem exclusão 2/2 × 2/2 · dois pedidos 1/1 (tipo errado) × 0/1 · exclusão parcial 1/1 × 1/1 · fim de
interesse 1/1 × 1/1 · fáceis 27/30 × 22/30.

Curva do teste (mesmas respostas, outra faixa nos três Nouls principais; informativa): limiar único 0,5 →
98% automático, mas 1 obrigação pela metade; 0,4–0,6 → 92% automático, 1 erro, nenhum caro; política
congelada → 88% automático, 1 erro (T046), nenhum caro; 0,2–0,8 → 73% automático, 0 erro.

Custo total da construção: 130 requisições (orçamento 300) — 35 na 1ª passada (rascunho + ajuste), 30 na 2ª,
5 de rascunho, 60 de teste; 261.266 tokens de entrada, US$ 0,011.

### Rodada 2 (pós-revisão do Codex, não cega; manifesto gravado em 2026-10-01 13:23:06; `resultados.md`)
Revisão adversarial do Codex sobre a rodada 1: quatro achados, todos aceitos e aplicados. O teste já estava
aberto: esta rodada **não é cega**. Não mexe no texto das perguntas, nas faixas nem no critério; **zero chamada
nova** — as 90 requisições de ajuste e teste (e as 5 do rascunho) vieram do cache, em `JEV_MODO=gravado`.

| Achado | O que mudou | Efeito medido |
|---|---|---|
| 1 (grav. 1) exclusão reconhecida + `opt_out` em dúvida + guarda "pode continuar" alto saía com o envio liberado: o guarda sozinho dispensava o bloqueio | `optout.decidir`: exclusão bloqueia sempre; com sinal de continuar e sem opt-out explícito → `revisar` com o envio suspenso | **1 caso do teste muda: OL-T054** (abaixo); ajuste e rascunho: nenhum |
| 2 (grav. 2) timeout, erro da API ou resposta inválida subiam como exceção e abortavam o lote | `optout.guardar_seguro` devolve `revisar` por mensagem; `run.py` roda por ele e conta "falhas operacionais" à parte | **0 falhas** nos três conjuntos; nenhum número muda; provado só pela bateria |
| 3 (grav. 2) "obrigação pela metade" ignorava `bloqueia=None` | `run.obrigacao_perdida` exige `bloqueia is True`; pendência sai da cobertura automática da curva (coluna nova) | nenhum caso na política congelada (0 pendentes no ajuste e no teste); na curva do teste, faixa 0,1–0,9, aparece 1 pendente (OL-T049, origem com `opt_out` 0,17; o gabarito não tem opt-out, não é perda) |
| 4 (grav. 3) "52 reprovaria" contradiz o `≥` do critério | texto corrigido nas duas ocorrências (critério da rodada 1 e lição 9) | só texto |

**Números do teste, Jev, rodada 1 → rodada 2** (baseline e "sempre revisa" não mudam; ajuste idêntico: 0,967,
0/14, 0/14, 0/14, 9/9):

| | rodada 1 (cega) | rodada 2 (não cega) |
|---|---|---|
| ação (5 classes) | 0,883 (53/60) | **0,867 (52/60)** |
| infração · pela metade · bloqueio indevido | 0/31 · 0/31 · 0/28 | 0/31 · 0/31 · 0/28 |
| tipo LGPD certo (pedido aberto com o tipo do gabarito) | 16/18 | **15/18** |
| nulo → `revisar` · revisou sem necessidade | 1/1 · 6/59 (10,2%) | 1/1 · **7/59 (11,9%)** |
| bloqueou com `opt_out` falso (todas as 40) | 0/40 | **1/40** (suspensão provisória do T054) |
| bloqueio composto (Jev × baseline, n = 59) | 0,898 × 0,881 | **0,881** × 0,881 |
| cobertura automática · erro entre automáticos (política congelada) | 88% (53) · 1 (T046) | **87% (52)** · 1 (T046) |
| falhas operacionais | não contadas | 0 |

**Critério no teste (rodada 2)**: (1) 0/31 ✓ · (2) 0/31 ✓ · (3) 0/28 ✓ · (4) 0,867 ≥ 0,867 ✓ — **no limite exato,
sem folga** (52/60 = 43/60 + 9/60; um acerto a menos reprovaria). Secundários: nulo 1/1 ✓ · 11,9% ✓ · **tipo
LGPD certo 15/18 = 0,833 < 0,85 ✗** (secundário, não decide; passava na rodada 1).

**O caso que mudou — OL-T054** ("prefiro que apaguem meu histórico de buscas, mas podem continuar me mandando
os lançamentos"; gabarito `abrir_pedido_lgpd(exclusao)`, `opt_out` falso): `lgpd_request` 0,93, Choice `deletion`
1,00, `opt_out` 0,03, `wants_contact_to_continue` 0,91. Rodada 1: pedido aberto **sem** bloquear (acerto).
Rodada 2: `revisar` com o envio suspenso e o tipo reconhecido junto (erro de ação, uma revisão desnecessária a
mais, um pedido a menos no "tipo certo"). É o preço da regra, medido num caso só: o único exemplo de exclusão
parcial dos conjuntos é justamente aquele em que o guarda estava certo. O ramo que o Codex demonstrou no código
(`opt_out` em dúvida) não tem caso em nenhum conjunto; a regra foi aplicada ao ramo inteiro porque, sem opt-out
explícito, quem dispensaria o bloqueio continua sendo só o guarda (decisão de desenho, não medição). A suspensão
não entra em "bloqueio indevido" (essa métrica é sobre as 28 mensagens sem opt-out nem LGPD); aparece em
"bloqueou com `opt_out` falso".

**Varredura da família do achado 1** (todos os ramos de `decidir`): opt-out ≥ 0,7 com veto de guarda já ia a
`revisar` (não a `seguir`), com o bloqueio pendente — não mudou; pedido de acesso/origem/correção não consulta
guarda; `stop_without_object` só acrescenta `revisar`. O único ramo em que um guarda liberava envio era o da
exclusão. A bateria confere isso em toda a grade.

**Bateria** ([`testa_falhas.py`](testa_falhas.py), sem chave nem rede; dublê no lugar do Jev porque o que se
testa é código): **A** 40 falhas operacionais — 25 respostas falsas (bool no lugar de número, string, NaN, fora
de [0,1], ID faltando, `type` trocado, Choice sem distribuição ou com distribuição incompleta, vencedor fora das
opções, confiança bool…), 4 respostas que não são objeto, 6 exceções simuladas (timeout, conexão, HTTP 503 e 429,
cache faltando, erro não previsto), 4 entradas inválidas e 1 lote de 6 mensagens com 2 falhas: toda falha sai
`revisar` com motivo "falha operacional", **nenhuma vira `seguir`**, o lote não aborta e o baixo nível continua
levantando erro · **B** 7.294 combinações de `decidir` (três níveis por Noul × 5 opções da Choice × 2 confianças):
guarda só move para `revisar`, nenhum bloqueio dispensado, obrigação ou dúvida nunca sai `seguir` · **C** 5
conferências do bloqueio pendente. Contra o código da rodada 1, a parte B acusa 56 falhas (54 "guarda dispensou
o bloqueio") e `bloqueia=None` não contava como perda.

O manifesto da rodada cega (13:07:34) foi para `congelamentos-anteriores/`. `perguntas.py` mudou só em dois
comentários que descreviam a exceção antiga (por isso o hash novo); o dicionário das perguntas, as faixas e o
critério são os mesmos — é o que o cache reproduzir 100% e o critério do manifesto mostram.

## O que deu certo (rodada 1; o que a rodada 2 muda está dito em cada item)
- Nenhum erro caro no teste, dos dois lados (igual na rodada 2); o baseline teve 4 infrações (3 pedidos de acesso/origem em
  paráfrase que a lista não cobre, 1 chip herdado), 1 pedido não aberto e 5 bloqueios indevidos (negação,
  filtro, preferência de horário, pausa "até lá").
- Negação 5/5 ("não quero mais ESSE apê", "não quero que tirem meu número", "não precisa apagar meus dados, só
  não quero mais mensagem de lançamento" → bloqueia sem abrir exclusão).
- `temporary_pause` 60/60 e `opt_out` 53/53 a 0,5 fora das exclusões; a regra de código cobriu as exclusões.
- A exceção do LEIA-ME funcionou no único caso (T054, "apaguem meu histórico, mas podem continuar mandando"):
  `wants_contact_to_continue` 0,91 → pedido de exclusão aberto **sem** bloquear. Na rodada 2 este mesmo caso vai
  a `revisar` com o envio suspenso: o guarda leu certo, mas deixou de poder liberar o envio sozinho.
- O nulo ("não quero mais, obrigado") foi a `revisar` por duas leituras independentes (`opt_out` 0,38 e
  `stop_without_object` 0,91).

## O que falhou no teste (NÃO corrigido)
Cinco dos oito casos marcados são a mesma fronteira — **"tirar o número" × "apagar dados"**:

| Caso | Mensagem | Saída | Causa |
|---|---|---|---|
| OL-T046 | "Me descadastra desse whatsapp. Obrigada." | `abrir_pedido_lgpd(exclusao)` (gabarito `bloquear_envios`) | `lgpd_request` 0,79, Choice `deletion` 0,95: "descadastrar" lido como encerrar cadastro. O envio foi bloqueado (certo), mas abriu um pedido de exclusão que ninguém fez. Único erro automático |
| OL-T055 | "Tira meu número daí!!! Já falei!!!" | `revisar` (gabarito `bloquear_envios`) | `lgpd_request` 0,32 (faixa de dúvida), `opt_out` 0,56 |
| OL-T059 | "…não sou a Carla. tirem daqui por favor" (chip herdado) | `revisar` (gabarito `bloquear_envios`) | `lgpd_request` 0,59, apesar de o `false` dizer "não é a pessoa procurada" |
| OL-T011 | "esse celular é da minha filha… não mandem mais nada aqui e apaguem o número" | `revisar` (gabarito exclusão) | a mesma fronteira pelo outro lado: `lgpd_request` 0,43 — "apaguem o número" é exclusão no gabarito, "tira meu número" não |
| OL-T040 | "Me tira da lista. E me diz quem foi que vendeu meu contato…" | pedido aberto e envio bloqueado, mas tipo `exclusao` (gabarito `origem_dos_dados`) | a Choice leu "tira da lista" como exclusão (0,79) e a precedência escrita na instrução pôs exclusão na frente |
| OL-T028 | "…por favor não mandem nada esse mês." | `revisar` (gabarito `pausar`) | `temporary_pause` 0,93, mas `opt_out` 0,27 caiu na faixa de dúvida, que vem antes na política |
| OL-T048 | "…Não me mandem mais nada até lá." | `revisar` (gabarito `pausar`) | idem: pausa 0,91, `opt_out` 0,40 |
| OL-T020 | "para de mandar coisa que eu já disse que não quero, apê sem vaga não serve" | `revisar` (gabarito `seguir`) | filtro com cara de opt-out: `opt_out` 0,47. O baseline bloqueou |

No ajuste, o único erro foi OL-A006 ("esse número aqui é da minha mãe… pode tirar": `opt_out` 0,40 → `revisar`).

Rodada 2: os oito continuam iguais (nenhum foi corrigido) e soma-se OL-T054, descrito acima.

## Lições
1. **Sintoma visto no ajuste e tratado com limiar volta no teste.** "Tirem meu número da lista" já dava
   `lgpd_request` 0,24–0,26 no ajuste; uma frase a mais no `false` baixou para 0,19–0,21 e o `nao` foi posto em
   0,3, logo acima. No teste a mesma família veio em 0,32–0,79. O que faltava era desenho: um Noul atômico só
   para "pede para apagar DADOS ou encerrar o cadastro, além de sair da lista", ou a regra de código "Choice
   `deletion` + `opt_out` sim + `lgpd_request` em dúvida → bloquear e mandar só a exclusão para revisão". Nenhum
   dos dois foi aplicado (o teste já foi visto).
2. **A Choice relativa dá tipo a quem não pediu nada; o Noul absoluto é o portão** (limite #8). No teste a
   Choice escolheu um tipo em 5 das 42 mensagens sem pedido; o Noul segurou 2, pôs 2 em dúvida e deixou passar 1
   (T046). Sem o portão seriam 5 pedidos abertos à toa.
3. **A faixa do meio é o que compra o zero de erro caro, e tem preço**: 6 revisões desnecessárias em 59 (10%).
   Com limiar único 0,5 o teste teria 98% automático e um pedido de exclusão não aberto (T011).
4. **A ordem da política também é política.** Dúvida de opt-out vem antes da pausa, então duas pausas claras
   (0,91 e 0,93) foram a humano. Inverter resolveria as duas e transformaria opt-out duvidoso em pausa — a
   obrigação pela metade. Ficou como está.
5. **Qualificador que o cliente nunca escreve não vai na instrução.** `opt_out` pedia parar "for good" e
   hesitou em "para de me mandar mensagem" (0,76); tirar o "for good" da instrução e deixar "sem data de
   retomada" no critério levou a 0,80–0,96 (limite #1).
6. **Palavra ambígua na língua do dado precisa ser dita na pergunta.** "para" sozinho deu 0,60 no guarda (em
   português também é preposição); dizer que a mensagem é em português e citar as palavras levou a 0,96.
7. **Guarda sem caso que o exercite é peso não medido.** `wants_contact_to_continue` decidiu um caso no teste
   (exclusão parcial) e `stop_without_object` um no ajuste ("para" sozinho; no teste coincidiu com a dúvida de
   `opt_out`). Os vetos do bloqueio — inclusive `about_another_contact`, que só serve a isso — não dispararam
   em nenhuma das 95 mensagens (rascunho, ajuste, teste). Os três guardas são ~27% do texto das perguntas
   (≈ 550 dos 2.028 tokens, estimado por caracteres); ficaram por desenho, sem prova.
8. **A lista de expressões erra dos dois lados e não avisa**: 4 infrações e 5 bloqueios no teste, zero
   `revisar`. Ela acerta o que é literal (ironia 3/3, "descadastra") e perde paráfrase e negação.
9. **O critério 4 passou com um caso de folga, e depois com nenhum.** Com n = 60, "+15 p.p." separa 52 de 51
   acertos: a rodada 1 teve 53, a rodada 2 tem 52. Não é margem. (A versão cega dizia "separa 53 de 52";
   corrigido na revisão.)
10. **Guarda que veta é barato; guarda que libera é política.** Os três guardas foram pensados como segunda
    leitura que só manda a humano, mas um deles também dispensava o bloqueio da exclusão — e passou no teste
    cego porque o único caso era o favorável. A regra "guarda nunca é a razão única para não cumprir obrigação"
    custou um acerto e não evitou nenhum erro medido: o que ela cobre (guarda alto por engano, ou movido por
    texto que argumenta) não está nos dados.
11. **Métrica que só olha `False` não vê o pendente.** "Pedido aberto sem bloqueio" contava `bloqueia is False`;
    `None` passava como cumprido e como automático. Nenhum caso na política congelada — o defeito só existia
    para quem mudasse a faixa.

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só, mesmo fornecedor de quem construiu; n = 30/60;
  uma versão do modelo; uma rodada cega (a 2 não é). Mensagem real é mais suja (áudio transcrito, erro de
  digitação, emoji).
- As três correções de código da rodada 2 estão provadas por bateria com dublê, não por tráfego: nenhum conjunto
  tem falha de rede, bloqueio pendente ou exclusão com `opt_out` em dúvida. O custo da regra do guarda foi medido
  em um caso (T054).
- `guardar_seguro` pega qualquer exceção: defeito de programação também vira `revisar` "falha operacional" — a
  contagem à parte é o que o denuncia. `revisar` com `bloqueia` = sim é combinação nova: o consumidor tem de
  suspender o envio até a confirmação, e desfazer a suspensão é dele.
- Uma mensagem isolada: sem a conversa, "para" e "não quero mais" continuam indecidíveis (por isso `revisar`);
  com o turno anterior do agente no state o desenho seria outro, não medido.
- Só os quatro tipos do LEIA-ME; portabilidade, revogação de consentimento, oposição e anonimização não existem
  aqui. A fronteira opt-out × exclusão é do rotulador, não da lei.
- Guarda com Jev não é fronteira de segurança (limite #6): texto que "argumenta pela própria classificação"
  move a resposta. A permissão para bloquear ou apagar continua no processo.
- Valores perto do limiar trocam de lado entre chamadas idênticas (AGENTS.md, NÚCLEO §6: p95 ~0,05, máximo
  0,15): T055 (`lgpd_request` 0,32, limiar 0,30) está nessa zona.
- Os nomes de família no relatório saem do prefixo da `nota`; "tipo" é "tipo de direito duvidoso", e "dois
  pedidos" / "exclusão parcial" aparecem separados (o LEIA-ME os conta juntos).

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa se o manifesto congelamento.json não bate)
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação (marca "em afinação")
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 casos fáceis → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # grava o manifesto (código, teste.json, critério); o anterior vai para congelamentos-anteriores/
set JEV_MODO=gravado                              # só o cache/ (130 respostas reais), sem chave
..\..\.venv\Scripts\python.exe testa_falhas.py   # bateria do código: falha operacional, guarda, bloqueio pendente (sem chave, sem rede)
```
No Windows, use `PYTHONIOENCODING=utf-8`. A primeira execução com o teste grava `resultados-rodada1.md` e nunca
o reescreve. Como guarda: `optout.guardar_seguro(jev, mensagem)` devolve `acao`, `tipo_lgpd`, `bloqueia`
(sim / não / `None` = pendente, quem atende confirma) e `motivo`, e **não levanta**: mensagem vazia, erro da
chamada ou resposta fora do contrato → `revisar` com motivo `falha operacional: …` (ausência de resposta nunca
vira `seguir`). `revisar` com `bloqueia` = sim → suspender o envio até a confirmação. `optout.julgar` é o baixo
nível, que levanta a exceção.
