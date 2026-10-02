# Próxima pergunta necessária (qualificação de lead, pt-BR) — um ID do catálogo ou `no_question_needed`

O cliente já disse orçamento, bairro e finalidade, e o atendente (ou o agente) pergunta tudo de novo; ou falta
exatamente uma informação e ninguém pergunta. Este exemplo lê a conversa e o que o CRM já tem e devolve **uma**
pergunta-modelo do catálogo fixo (ou `no_question_needed`) para o próximo turno, mais o que o portão julgou **já
respondido**, item a item, com a evidência e a margem de cada julgamento. Os números vêm dos relatórios gerados pelo
`run.py`: a rodada cega está preservada em [`resultados-rodada1.md`](resultados-rodada1.md) e a rodada 2
(pós-revisão do Codex, **não cega**) é o [`resultados.md`](resultados.md) atual. Candidato a etapa de qualificação
da Luci SDR: roda antes de o agente redigir o próximo turno. **Nada é enviado daqui** e o texto da pergunta sai do
catálogo, pelo código.

## Problema
Catálogo de 10 itens ([`dados/LEIA-ME.md`](dados/LEIA-ME.md)): quatro essenciais (`finalidade`, `orcamento`,
`bairro`, `quartos`), quatro secundárias (`vagas`, `prazo`, `pet`, `financiamento`), `visita` e
`no_question_needed` (NQN). O gabarito de cada conversa é um **conjunto** de aceitáveis e um de proibidas. Dois erros:
- **erro caro — pergunta proibida**: perguntar o que o cliente já disse ("meu labrador precisa de quintal" responde
  `pet`), o que o CRM já tem, ou o que não faz sentido (financiamento em aluguel, pet de investidor);
- **calar**: responder NQN quando falta uma essencial e não há nada a responder antes.

O que confunde: resposta informal; correção tardia; campo do CRM contradito (com e sem valor novo); "até 600"
(preço? aluguel? 600 ou 6 mil?); prestação em vez de preço; visita já pedida; cliente que se recusa a repetir.

## Quem faz o quê
O que a rodada 2 mudou está marcado; o desenho da rodada 1 está em `congelamentos-anteriores/rodada1-codigo/`.

| Parte | Quem | Por quê |
|---|---|---|
| Que valores em dinheiro o cliente escreveu, com que escala e de que tipo ("até 6", "600 mil", "600k", "1,2 mi", "seiscentos mil", "2.500 por mês", "prestação de 3 mil") — **rodada 2** | **código** ([`valores.py`](valores.py)) | magnitude e unidade são comparação numérica (limite #2); o resultado entra no state como fato calculado |
| O cliente DECLAROU esta informação como preferência dele? (um por item) | Jev, Noul `answered.<item>` | julgamento semântico absoluto. Na rodada 2, orçamento, bairro e quartos perguntam só o declarado: preço e atributos do anúncio citado não contam |
| Regra do LEIA-ME sobre `orcamento`: respondida × aceitável como confirmação × em aberto × revisão — **rodada 2** | **código** (`proxima.regra_orcamento`) | combina o valor lido, o Noul "declarou" e o sinal de aluguel; o que a regra não cobre vai para revisão |
| Anúncio específico citado responde `bairro` e `quartos` — **rodada 2** | **código**, sobre o sinal `specific_property` | é regra do LEIA-ME sobre o imóvel, não preferência do cliente |
| O cliente retirou o valor do cadastro sem dar outro? | Jev, Noul `withdrawn.<campo>`, só para campo que o CRM tem | reabre um campo conhecido; pergunta montada por caso |
| É aluguel? É investidor que não vai morar? Há um imóvel específico na mesa? Reagiu bem a ele? | Jev, quatro Nouls de sinal | alimentam as regras de sentido |
| Campo do CRM = respondido; financiamento não se pergunta em aluguel; pet não se pergunta a investidor; visita só com imóvel específico; com essencial faltando, secundária não entra | **código** | são regras do LEIA-ME, não julgamento |
| Qual essencial perguntar | **código** (primeira que falta, na ordem fixa) | pela tabela do LEIA-ME qualquer essencial que falta é aceitável |
| Com as essenciais completas: secundária × visita × nada | Jev, Choice `next` só entre as candidatas (2ª requisição) | é o único ponto em que a tabela deixa escolha |
| Validar TODA resposta (IDs, tipos, discriminador `type`, números em [0,1]) — a da 2ª etapa inclusive (**rodada 2**); teto da conversa; ID → texto do catálogo; falha operacional → revisão da conversa | **código** | ausência de resposta é erro, nunca "nenhuma pergunta" e nunca uma pergunta |
| Redigir o turno | LLM do agente | o Jev não gera texto |

## Desenho
State `{"conversation": [{"from", "text"}], "known_fields": {...}, "customer_amounts": [{"quote", "value", "unit"}]}`.
`customer_amounts` é o fato calculado (rodada 2): os valores que o cliente escreveu, sem leitura de operação.
**O catálogo não vai no state** (desvio do briefing): ele é fixo, então cada item virou uma pergunta literal com as
regras do LEIA-ME no critério — apontar `catalog[i]` seria indireção (limite #4). Perguntas e limiares em
[`perguntas.py`](perguntas.py); decisão em [`proxima.py`](proxima.py); valores em [`valores.py`](valores.py).

1. **1ª requisição**: 9 Nouls `answered` + até 8 `withdrawn` + 4 sinais. Só isto — é o que a produção paga.
2. **Código — portão**. Bloqueada = campo do CRM não retirado · `answered` ≥ 0,5 (declarado pelo cliente) ·
   `orcamento` pela regra abaixo · bairro e quartos com `specific_property` ≥ 0,8 (anúncio citado) · sem sentido
   (`rental` ≥ 0,7; `investor_not_living` ≥ 0,5). O que sobra vira candidata: as essenciais que faltam; se não falta
   nenhuma, as secundárias; `visita` só com `specific_property` ≥ 0,8; NQN sempre.
3. **Regra do orçamento** (CRM sem o campo): o código lê o último valor que o cliente deu como limite e aplica o
   LEIA-ME — aluguel + número pequeno ("até 6") = R$ 6 mil, respondida; aluguel + centenas sem unidade ("até 600") =
   **confirmar** (candidata); compra ou operação desconhecida + "até 600" = R$ 600 mil, respondida; valor mensal em
   compra = prestação, em aberto. Só bloqueia se o Noul diz que o valor é do cliente (≥ 0,5). Noul ≤ 0,2 = o valor
   é de outra coisa (preço do anúncio): em aberto. **Revisão** — nem pergunta nem bloqueio — quando a regra não
   cobre a leitura ("até 6" fora de aluguel, R$ 4 mil sem aluguel conhecido, entrada, possível ano), quando o código
   leu um valor e o Noul ficou entre 0,2 e 0,5, ou quando o Noul vê valor declarado e o código não leu nenhum.
4. **Escolha** (variante principal, `hibrida`): essencial faltando → a primeira, pelo código, sem 2ª requisição;
   senão **2ª requisição** com a Choice `next` entre as candidatas (só NQN = sem chamada). Essencial em revisão e
   nenhuma outra faltando → sem sugestão (`revisar`): escolher entre secundárias seria dá-la por respondida.
5. Saída: `pergunta` (ID ou `None`), `texto` (copiado do catálogo), `bloqueadas`, `em_revisao`, `orcamento` (estado
   e leitura do código).

**`bloqueadas` não é proibição categórica** (rodada 2, achado 2). Cada item é `{id, motivo: "noul" | "regra",
detalhe, valor, nouls, margem}`: `noul` = o Jev julgou declarado (valor = o Noul); `regra` = regra de código sobre um
fato (CRM, valor lido com `{valor, escala, tipo}`, anúncio específico, sem sentido). `margem` é a menor distância ao
limiar, ×2, entre os Nouls que sustentam o bloqueio (0 = em cima do limiar). Quem consome decide o que fazer com
bloqueio de margem baixa. A margem ajuda, não garante: no teste da rodada 2, 1 dos 162 bloqueios era pergunta
aceitável e saiu com margem 0,16 (PP-T007); o falso bloqueio da rodada 1 tinha Noul 0,88.

Variantes medidas nos mesmos casos: `jev` (o desenho de partida: Choice `next` em todos os casos), `mascarada`
(Choice única lida só nas candidatas, sem 2ª requisição), `codigo` (sem Choice: essencial → `visita` se imóvel
específico com reação positiva → NQN) e `unica` (uma Choice sobre o catálogo inteiro, sem portão). `unica`,
`mascarada` e `jev` só existem com `todas=True`: uma requisição de comparação a mais, que a produção não envia.

**Por que a principal não é o desenho de partida.** No ajuste, nas duas passadas, a Choice `next` **re-julgou o
portão**: com orçamento "meio dito" (aluguel "até 600"; compra só com prestação) o Noul liberou `orcamento` e a Choice
respondeu NQN. Dizer na instrução que as opções "já foram conferidas e continuam em aberto" não moveu a escolha. Com
essencial faltando a tabela já decide, então a Choice ali só pode empatar ou errar. Ficou onde a tabela deixa escolha.

## Baselines (código, sem Jev)
- **Primeira lacuna (só CRM)**: primeiro campo do catálogo que o CRM não tem. Ignora a conversa — é a dor.
- **Lacuna + palavras-chave**: essencial preenchida = CRM ou expressão no texto do cliente (`perguntas.BASELINE`);
  primeira essencial vazia → pergunta; senão NQN. O que um dev escreve em meia hora.
- **Sempre NQN**: o trivial que o rotulador pediu para medir (nunca erra caro, nunca qualifica).

## Critério de continuar/descartar (fixado ANTES de abrir o teste, 2026-10-01)
No teste (40 conversas, 23 em que NQN não é aceitável), variante `hibrida`: (1) pergunta proibida ≤ 1/40;
(2) acerto ≥ melhor baseline de código + 0,15; (3) NQN indevido ≤ 2/23; (4) acerto ≥ e proibidas ≤ os da Choice
única. Secundário, não decide: portão bloqueia ≥ 90% das proibidas e ≤ 5% das aceitáveis. O critério está no
manifesto `congelamento.json` e o veredito é calculado pelo `run.py`. É o mesmo nas duas rodadas.

## Resultados (`jev-1.13.0`, 2026-10-01; curvas e caso a caso nos dois relatórios)
Ajuste = 20 conversas (13 difíceis), afinado em duas passadas; teste = 40 (29 difíceis). Duas rodadas, cada uma com o
relatório gerado pelo script: 1 (cega) em `resultados-rodada1.md`, 2 (pós-revisão do Codex, não cega) em
`resultados.md`.

### Rodada 1 (cega; [resultados-rodada1.md](resultados-rodada1.md))
Manifesto gravado em 2026-10-01 13:30 (`perguntas.py` `43b4435668feb2c5…`, `proxima.py` `a1a5d1199d270580…`, `run.py`
`fa3709876f26bfc4…`, `dados/teste.json` `7e7c79562367f542…`), teste aberto e rodado UMA vez depois disso. Os números
desta seção ficam como rodaram.

| Variante: acerto · **proibida** · NQN indevido · perguntou algo | ajuste (n = 20; 11 sem NQN) | teste (n = 40; 23 sem NQN) |
|---|---|---|
| primeira lacuna (só CRM) | 0,150 · 14 · 0 · 19 | 0,350 · **20** · 0 · 39 |
| lacuna + palavras-chave | 0,700 · 2 · 4 · 10 | 0,750 · **5** · 5 · 25 |
| sempre NQN | 0,450 · 0 · 11 · 0 | 0,425 · 0 · 23 · 0 |
| Jev: Choice única | 0,850 · 1 · 1 · 11 | 0,900 · **3** · 1 · 23 |
| Jev: Nouls + Choice única mascarada | 0,900 · 0 · 2 · 9 | 0,925 · 0 · 3 · 20 |
| Jev: Nouls → candidatas → Choice `next` (desenho de partida) | 0,900 · 0 · 2 · 10 | 0,925 · 1 · 2 · 23 |
| Jev: Nouls + política de código | 1,000 · 0 · 0 · 13 | 0,975 · 1 · 0 · 27 |
| **Jev: `hibrida` (principal)** | 1,000 · 0 · 0 · 14 | **0,975 (39/40) · 1 · 0 · 29** |

**Critério no teste: passou os quatro** — (1) 1/40 ✓, **no limite**; (2) 0,975 ≥ 0,900 ✓; (3) 0/23 ✓; (4) 0,975 ×
0,900 e 1 × 3 proibidas ✓. Secundários: portão 160/163 = 98,2% ✓; aceitável bloqueada 1/55 = 1,8% ✓.

| | ajuste | teste |
|---|---|---|
| Portão: proibidas bloqueadas · aceitáveis bloqueadas | 88/88 · 0/29 | 160/163 · 1/55 |
| Motivo do bloqueio: `answered` · CRM · sem sentido | 52 · 27 · 9 | 97 · 48 · 16 |
| `withdrawn` (campo do CRM): retirados achados · maior valor entre os mantidos | 1/1 · 0,28 (n = 28) | 2/2 · 0,20 (n = 50) |
| `hibrida` em produção: requisições · US$ por mil conversas (estimado) · p50 / p95 por conversa | 27 · 0,102 · 346 / 777 ms | 52 · 0,100 · 322 / 638 ms |
| `codigo` em produção (uma requisição) | 20 · 0,091 · 321 / 520 ms | 40 · 0,090 · 312 / 389 ms |
| Medido com tudo ligado (comparações inclusive): requisições · tokens por conversa · US$ por mil | 39 · 3.575 · 0,150 | 78 · 3.559 · 0,149 |

O custo "em produção" desconta a Choice única de comparação da 1ª requisição (~26% do texto das perguntas, estimado
por caracteres) — é estimativa; o medido é a última linha. Latência com 8 conversas em paralelo.

> Correção (revisão do Codex, achado 4): as duas linhas "em produção" acima **não eram custo de produção**. O desconto
> de 26% foi aplicado a todos os tokens da 1ª requisição — state e perguntas `withdrawn` inclusive, que a Choice única
> não ocupa — e o código entregue (`julgar` com `todas=False`) enviava e exigia a `single_choice` de qualquer jeito:
> quem o chamasse pagaria a linha "medido com tudo ligado" menos as 2ª requisições extras. Os números ficam como
> rodaram; o custo medido em requisições próprias está na rodada 2.

Por família no teste (`hibrida` × palavras-chave × Choice única): valor ambíguo 5/6 × 4/6 × 4/6 · já respondida de
modo informal 7/7 × 4/7 × 7/7 · correção tardia 3/3 × 3/3 × 3/3 · campo conhecido contradito 3/3 × 1/3 × 3/3 · nada
faltando 2/2 × 2/2 × 2/2 · recusa de repetição 1/1 × 0/1 × 1/1 · visita já pedida ou recusada 4/4 × 4/4 × 4/4 · sem
sentido 1/1 × 1/1 × 1/1 · anúncio específico 1/1 × 1/1 × 1/1 · reação negativa 1/1 × 1/1 × 1/1 · fáceis 11/11 ×
9/11 × 9/11.

Cobertura × erro no teste, pelo Noul mais fraco do portão (distância ao limiar × 2): sem piso, 100% e 1 erro; piso
0,3 → 85% automático, 0 erro (34 conversas); piso 0,5 → 67,5%, 0 erro. Pela confiança da Choice a curva da `hibrida`
não separa nada (o erro foi decidido pelo código, confiança 1,0).

Custo da construção: 176 requisições (orçamento 300) — 10 de rascunho, 39 + 39 nas duas passadas do ajuste, 10 de
rascunho com as perguntas finais, 78 de teste; 319.773 tokens de entrada, US$ 0,013.

### Rodada 2 (pós-revisão do Codex, não cega, 149 chamadas novas; manifesto de 2026-10-01 14:07; `resultados.md`)
Revisão adversarial do Codex sobre a rodada 1: quatro achados, todos aceitos e aplicados. O teste já estava aberto, e
quem aplicou leu o `teste.json` e o caso a caso da rodada 1: esta rodada **não é cega**. Os achados 1 e 2 mudam o
state e três perguntas, então **nada da rodada 1 serve de cache**: 149 requisições novas (orçamento 150) — 27 de uma
passada do ajuste só com as requisições da principal, 20 de comparação no ajuste, 92 no teste (rodado uma vez, depois
do manifesto), 8 no rascunho e 2 de uma sonda (abaixo); 246.604 tokens de entrada, US$ 0,010. Critério, limiares da
rodada 1 e variante principal (`hibrida`) são os mesmos. Não houve segunda passada: texto e limiares ficaram como
estavam antes da primeira chamada.

| Achado | O que mudou | Efeito medido no teste |
|---|---|---|
| 1 (grav. 2) magnitude e unidade do orçamento delegadas ao Noul | `valores.py` lê os valores do cliente (número, escala, mensal, prestação) e os põe no state; `answered.budget` pergunta só se o cliente declarou um valor; a regra do LEIA-ME é aplicada em `proxima.regra_orcamento`; o que ela não cobre vai para revisão | **PP-T022 deixa de ser pergunta proibida** (0/40); 15 orçamentos bloqueados pela regra, todos proibidos no gabarito; 1 em revisão (o próprio T022). Efeito colateral: **PP-T007 passa a errar** (abaixo) |
| 2 (grav. 2) preço do anúncio lido como orçamento do cliente; `bloqueadas` tratada como proibição | `answered.budget`, `neighbourhood` e `bedrooms` distinguem o declarado pelo cliente do atributo do imóvel citado; anúncio específico responde bairro e quartos por regra de código; `bloqueadas` sai com motivo, evidência e margem | **PP-T028**: `orcamento` 0,88 → 0,04, deixa de ser bloqueada e é a pergunta feita (aceitável). **PP-T019**: `bairro` passa a ser bloqueado (pela regra). 6 bloqueios por anúncio, todos proibidos no gabarito |
| 3 (grav. 3) resposta da 2ª etapa sem conferência de tipos | a Choice `next` (e a única) passam pela mesma conferência da 1ª e por `congelamento.choice`, que agora confere `type`; `julgar_seguro` transforma falha operacional em revisão da conversa | 0 falhas nos três conjuntos; nenhum número muda; provado pela bateria |
| 4 (grav. 3) custo "em produção" estimado | `julgar(todas=False)` não envia mais a `single_choice`; o `run.py` mede a principal nas requisições dela e a comparação numa requisição à parte | custo medido (abaixo); a frase da rodada 1 está corrigida acima |

**Números do teste, rodada 1 → rodada 2** (baselines de código não mudam; ajuste idêntico nas oito variantes:
`hibrida` 1,000 · 0 · 0 · 14, portão 88/88 e 0/29):

| acerto · **proibida** · NQN indevido · perguntou algo | rodada 1 (cega) | rodada 2 (não cega) |
|---|---|---|
| Jev: Choice única | 0,900 · 3 · 1 · 23 | **0,875 · 4** · 1 · 23 |
| Jev: Nouls + Choice única mascarada | 0,925 · 0 · 3 · 20 | **0,900** · 0 · **4 · 19** |
| Jev: Nouls → candidatas → Choice `next` | 0,925 · 1 · 2 · 23 | **0,950 · 0** · 2 · 23 |
| Jev: Nouls + política de código | 0,975 · 1 · 0 · 27 | 0,975 · **0 · 1** · 27 |
| **Jev: `hibrida` (principal)** | 0,975 (39/40) · 1 · 0 · 29 | 0,975 (39/40) · **0 · 1** · 29 |
| `hibrida`: sem sugestão (essencial em revisão) · falhas operacionais | não existia | 0/40 · 0 |
| Portão: proibidas bloqueadas · aceitáveis bloqueadas · em revisão | 160/163 · 1/55 · — | **161/163** · 1/55 · 1 proibida |
| `withdrawn`: retirados achados · maior valor entre os mantidos | 2/2 · 0,20 | **1/2** · 0,24 |
| Cobertura pelo Noul mais fraco: piso 0,3 · piso 0,5 (0 erro nos dois) | 85% · 67,5% | **95% · 82,5%** |

**Critério no teste (rodada 2): passou os quatro** — (1) 0/40 ✓ (era 1/40, no limite); (2) 0,975 ≥ 0,900 ✓;
(3) 1/23 ✓ (era 0/23; o limite é 2); (4) 0,975 × 0,875 e 0 × 4 proibidas ✓. Secundários: 161/163 = 98,8% ✓; 1/55 =
1,8% ✓. **O acerto é o mesmo (39/40): a rodada 2 trocou um erro caro por um silêncio, não ganhou um caso.**

Por família (`hibrida`): valor ambíguo 6/6 (era 5/6) · campo conhecido contradito 2/3 (era 3/3) · as outras nove
iguais à rodada 1.

**O que mudou, caso a caso** (variante `hibrida`; os outros 35 casos do teste têm a mesma escolha nas cinco
variantes, salvo PP-T033, em que só a `jev` mudou de NQN para `finalidade`):

| Caso | Rodada 1 | Rodada 2 | Por quê |
|---|---|---|---|
| PP-T022 "alugar, 3 quartos, até 6" | `orcamento` (**proibida**) | `bairro` ✓; `orcamento` em revisão | O código leu "até 6" → R$ 6 mil de aluguel (regra do LEIA-ME). Mas o Noul reescrito deu **0,29** a "o cliente declarou um valor" (era 0,43 com a pergunta antiga): o Jev continua sem ver "até 6" como valor declarado. Quem segurou foi a faixa de dúvida (0,2–0,5 com valor lido → revisão do item); como faltava `bairro`, o código perguntou `bairro`. Com o Noul ≤ 0,2 o item ficaria em aberto e a pergunta proibida voltaria: a folga é 0,09 sobre um piso **não afinado** |
| PP-T007 "…não dá mais pra ir até 500" (CRM com orçamento) | `orcamento` ✓ | NQN (**NQN indevido**; `orcamento` do CRM mantido bloqueado, margem 0,16) | **Efeito colateral do achado 1.** `withdrawn.budget` caiu de 0,59 para 0,42, abaixo do limiar. A pergunta não mudou; o state sim: o código recorta "até 500" da frase e o lista em `customer_amounts`, e o trecho recortado parece um valor novo. Sonda de 2 chamadas, só com esse Noul: **0,63 sem** `customer_amounts`, **0,44 com**. Regex não vê a negação ("não dá mais"), e o fato calculado levou a leitura errada para dentro de outra pergunta. **Não corrigido** |
| PP-T028 "…aceita cachorro? o aluguel tá 3800 né" | NQN ✓ (com `orcamento` 0,88 bloqueada indevidamente) | `orcamento` ✓ | `answered.budget` 0,04: o preço do anúncio deixou de contar como orçamento do cliente. O código leu "aluguel tá 3800" e a regra o deixou em aberto. `bairro` e `quartos` saem bloqueados pela regra do anúncio (`specific_property` 0,92; declarados 0,15 e 0,19). `pet` continua 0,24, sem bloqueio (regra fora do LEIA-ME, **não corrigida**) |
| PP-T019 "o apê do anúncio 4521 de vcs ainda tá disponível?" | `finalidade` ✓ (com `bairro` 0,31 sem bloqueio) | `finalidade` ✓ | `bairro` e `quartos` bloqueados pela regra do anúncio (`specific_property` 0,97); como preferência declarada os dois dão 0,04 e 0,03. A escolha não muda |
| PP-T024 "quero visitar o apê da rua harmonia…" | `finalidade` ✓ | `finalidade` ✓ | mesmos bloqueios, outro motivo: antes `answered` 0,75 e 0,52; agora regra do anúncio (0,94), com os Nouls declarados em 0,08 e 0,02 |

As 4 perguntas proibidas da Choice única na rodada 2 são PP-T003, T004, T034 (as três da rodada 1) e PP-T022, que ela
acertava: mesma pergunta, state novo. No ajuste, PP-A019 ganhou um bloqueio fora do gabarito: `prazo` com Noul 0,50 e
margem 0,00 ("hoje em dia") — é o tipo de bloqueio que a margem existe para denunciar.

**Portão com evidência (teste, 162 bloqueios):** `noul` (declarado pelo cliente) 75, menor margem 0,32 · regra do CRM
49 (48 proibidas, 1 aceitável: o T007), menor margem 0,16 · regra do orçamento 15, menor margem 0,44 · sem sentido 17
· **anúncio específico 6, com 4 abaixo de 0,3 de margem** (`specific_property` 0,92–0,94 contra limiar 0,8). As duas
proibidas que escaparam: `pet` do T028 e `orcamento` do T022 (em revisão, que não conta como bloqueio). Regra do
orçamento nos 30 casos sem o campo no CRM: 15 `respondida` (15 proibidas), 1 `confirmar` (aceitável: T003, aluguel
"até 600"), 13 `aberta` (11 aceitáveis, 2 fora do gabarito), 1 `revisar`.

**Custo medido** (requisições próprias; nada estimado):

| | ajuste | teste |
|---|---|---|
| `hibrida` em produção (`todas=False`): requisições · tokens por conversa · US$ por mil · p50 / p95 por conversa | 27 · 2.675 · 0,112 · 328 / 595 ms | 52 · 2.616 · **0,110** · 316 / 594 ms |
| `codigo` em produção (só a 1ª requisição) | 20 · 2.398 · 0,101 · 297 / 378 ms | 40 · 2.378 · **0,100** · 296 / 355 ms |
| comparação (só na medição): Choice única + `next` onde a principal não chama | 20 · 1.205 · 0,051 | 40 · 1.234 · 0,052 |
| tudo o que a medição usou | 47 · 3.880 · 0,163 | 92 · 3.850 · 0,162 |

A 1ª requisição tem ~2.380 tokens (antes, com a Choice única dentro, 2.880; as três perguntas reescritas e o
`customer_amounts` são mais longos que os da rodada 1, então os dois números não se subtraem). A estimativa da
rodada 1 (US$ 0,100 e 0,090) ficou ~10% abaixo do que a rodada 2 mede — para um desenho que não é mais o mesmo: o
custo de produção da rodada 1 nunca foi medido. Latência: teste com 8 conversas em paralelo; no ajuste, as 27
requisições da principal foram feitas em sequência (a passada de afinação) e as 20 de comparação em paralelo.

**Bateria do código** ([`testa_codigo.py`](testa_codigo.py), sem chave nem rede; dublê no lugar do Jev, porque o que
se testa é código): **A** 38 frases no normalizador — 29 com valor (PP-T022, "até 600", "600 mil", "600k", "1,2 mi",
"seiscentos mil", "um milhão e meio", "2.500 por mês", "prestação de 3 mil", correção, entrada, possível ano), cada
uma lida com aluguel e sem aluguel, e 9 números que não são dinheiro (quartos, anos, data, hora, número de anúncio,
condomínio) · **B** 456 combinações da regra do orçamento (frase × Noul × aluguel): só bloqueia com valor declarado E
lido; leitura ambígua nunca bloqueia nem vira candidata · **C** 18 conferências do portão de ponta a ponta: o PP-T022
com o Noul da rodada 1 (0,43) pergunta `bairro` e põe `orcamento` em revisão; em toda a grade do Noul acima de 0,2
ele nunca pergunta `orcamento`; preço de anúncio não bloqueia; todo bloqueio sai com motivo, evidência e margem ·
**D** 19 respostas inválidas ou exceções na 2ª etapa (discriminador `type` trocado, opção de fora, distribuição
ausente ou incompleta, probabilidade em string, confiança booleana ou NaN, ID faltando, timeout, rede, cache
faltando): `julgar` levanta erro e `julgar_seguro` devolve revisão, nunca pergunta; o mesmo para a `next` que vem na
requisição de comparação e para a 1ª etapa; o lote não aborta · **E** com `todas=False` nenhuma requisição leva
`single_choice`. 562 conferências, 0 falhas. Com a conferência da 2ª etapa desligada (como na rodada 1), a parte D
acusa 5 falhas: a resposta com `type` trocado é consumida e vira a pergunta `vagas`. Nada disso é medição do Jev.

O manifesto da rodada cega (13:30:04) foi para `congelamentos-anteriores/`, com o código que ele congelou em
`congelamentos-anteriores/rodada1-codigo/` (o repositório não tem histórico de commits; os hashes conferem com o
manifesto). O manifesto novo cobre `perguntas.py`, `proxima.py`, `valores.py`, `run.py`, `dados/teste.json` e o mesmo
critério. O `resultados.md` é a execução original da rodada 2 (modo `auto`, 92 requisições novas no teste).

## O que deu certo (rodada 1; o que a rodada 2 muda está dito em cada item)
- O portão: 160 de 163 proibidas bloqueadas no teste e 1 de 55 aceitáveis bloqueada. A lista "não pergunte isto" é
  o produto mais sólido do exemplo — serve ao agente mesmo quando ele escolhe a pergunta sozinho. Rodada 2: 161 de
  163, e a lista deixou de ser descrita assim — é julgamento com motivo, evidência e margem por item, não proibição
  (achado 2: o falso bloqueio da rodada 1 era um `answered` de 0,88, que nenhuma faixa perto de 0,5 pegaria).
- Resposta informal 7/7 (negação "não tenho carro e não vou ter" → `vagas` 0,98), correção tardia 3/3, visita já
  pedida ou recusada 4/4 (`answered.visit` ≥ 0,90). Igual na rodada 2.
- Campo do CRM por regra de código + Noul de retirada: os 2 retirados sem valor novo foram reabertos (≥ 0,59) e
  nenhum dos 48 mantidos foi (≤ 0,20). No ajuste, o `answered` cru deu 0,61 num bairro retirado — sozinho, teria
  bloqueado a única pergunta aceitável. Rodada 2: só 1 dos 2 foi reaberto (PP-T007, 0,42).
- Zero NQN indevido: com essencial faltando o código pergunta, sem pedir segunda opinião. Rodada 2: 1 (PP-T007).
- A Choice única sem portão perguntou 3 coisas já respondidas no teste (`quartos` a quem disse "kitnet" e "studio",
  `bairro` a quem disse a cidade); com o portão na frente, a mesma Choice (mascarada) não errou caro nenhuma vez.
  Rodada 2: 4 e 0.
- Rodada 2: a divisão "código lê o número, Jev diz de quem é" separou o que a rodada 1 misturava. Onde o cliente
  declarou valor, `answered.budget` deu ≥ 0,90 em 26 dos 27 casos sem o campo no CRM (ajuste e teste); nos 16 sem
  valor, ≤ 0,04; preço de anúncio, 0,04. O 27º é o "até 6" (0,29).

## O que falhou no teste (NÃO corrigido)
Tabela da rodada 1, como estava; o estado de cada caso na rodada 2 está na seção acima.

| Caso | Mensagem | Saída | Causa |
|---|---|---|---|
| PP-T022 | "alugar, 3 quartos, até 6" | `orcamento` (**proibida**; aceitável: `bairro`) | `answered.budget` 0,43. O critério dizia, com este exemplo, que "até 6" em aluguel é R$ 6 mil — e o Noul deu a "até 6" o mesmo valor que a "até 600" em aluguel (0,40 e 0,46), que é para ficar em aberto. Distinguir 6 de 600 é comparação de magnitude: trabalho do código (limite #2), entregue ao Jev. Único erro da principal |
| PP-T019 | "o apê do anúncio 4521 de vcs ainda tá disponível?" | `finalidade` (aceitável) | portão: `answered.neighbourhood` 0,31 — o anúncio responde bairro por regra do LEIA-ME, mas o texto não tem lugar nenhum. Não virou erro porque `finalidade` vem antes na ordem |
| PP-T028 | "…aceita cachorro? o aluguel tá 3800 né" | NQN (aceitável) | portão, dois lados: `pet` 0,29 (perguntar "aceita cachorro" responde `pet` no gabarito; a regra não estava no LEIA-ME e não foi escrita) e `orcamento` 0,88 bloqueada indevidamente (o preço do anúncio lido como orçamento do cliente) |

Nas variantes que não são a principal: a Choice `next` em todos os casos (`jev`) respondeu NQN em PP-T003 (aluguel
"até 600", confiança 0,54) e PP-T033 ("quero comprar, 3 quartos, até 800, zona leste": falta morar × investir;
confiança 0,17) — o mesmo re-julgamento visto no ajuste. A `mascarada` calou nesses dois e em PP-T004 (prestação).

Rodada 2, o que falha e continua sem correção: **PP-T007** (NQN indevido, erro novo, causado pelo fato calculado no
state); **PP-T022** sai certo pela faixa de revisão, com o Noul ainda em 0,29; `pet` do **PP-T028** segue sem
bloqueio. Na `jev`: PP-T003 (NQN, confiança 0,56) e PP-T007; na `mascarada`: PP-T003, T004, T007 e T033.

## Lições
1. **Magnitude não se pede ao Jev, nem dentro de um critério.** "Até 6" × "até 600" em aluguel ficaram em 0,40–0,46:
   o Noul não separa os dois. No ajuste a folga já era estreita (aceitáveis ≤ 0,44, proibidas ≥ 0,62, as duas pontas
   em `orcamento`) e a decisão foi não decompor com dois casos na mão. O desenho certo: o código extrai o número e
   a unidade, decide "centenas sem unidade em aluguel" e entrega o fato pronto no state (como os comparativos do
   `imovel-errado`). Não foi aplicado: o teste já foi visto. *(Aplicado na rodada 2, por achado da revisão.)*
2. **A Choice relativa re-julga o portão absoluto.** Candidata liberada pelo Noul e "meio dita" na conversa vira NQN
   na Choice, e a instrução não segura (ajuste: 2 casos, duas passadas; teste: 2 casos). "Passar o portão não prova
   que o vencedor passou" vale também ao contrário: o vencedor pode desfazer o portão.
3. **Onde a tabela de regras decide, a Choice só pode empatar ou errar.** Com essencial faltando, o código acertou
   tudo o que o portão entregou certo. A Choice ficou com o que sobra de escolha (secundária × visita × nada): 12 de
   40 conversas do teste, 12 acertos.
4. **Gabarito em conjunto esconde a diferença entre perguntar e calar.** `codigo` e `hibrida` empataram (39/40); a
   `hibrida` perguntou em 29 conversas e a `codigo` em 27. O acerto não diz qual qualifica melhor: nas regras 4 e 1
   do LEIA-ME, NQN e a pergunta são igualmente aceitáveis. A `codigo` custa uma requisição e é a escolha se o
   agente redige as secundárias sozinho com a lista `bloqueadas`.
5. **O que o código sabe exato não se pergunta de novo.** Campo do CRM = respondido por regra; ao Jev só a pergunta
   que o código não responde (retirou sem dar outro?). O `answered` cru errou esse caso no ajuste.
6. **A Choice única é barata e erra caro.** 0,900 com uma requisição de ~740 tokens, mas 3 perguntas repetidas em 40
   — o erro que o exemplo existe para evitar. A confiança ajuda pouco: as 3 saíram com 0,59–0,67.
7. **O Noul mais fraco localiza o erro; a confiança da Choice não.** Piso 0,3 na distância ao limiar tiraria 6
   conversas do automático e o único erro junto. Não é política congelada — é a primeira coisa a medir numa rodada 2.
   *(Rodada 2: piso 0,3 tira 2 conversas e o único erro junto — o `withdrawn` 0,42 do PP-T007.)*
8. **O critério 1 passou no limite** (1 de 1 permitido) e n = 40: um caso a mais reprovaria.

Da rodada 2 (não cega):

9. **Tirar a magnitude do Noul não o fez reconhecer o número.** A pergunta reescrita dizia que tamanho e unidade não
   importam e citava "até 6"; o Noul deu 0,29. O Jev hesita em chamar "6" de valor em dinheiro mesmo quando só lhe
   perguntam se o cliente declarou um. O que resolveu foi estrutural: código lê o número, e a discordância entre
   "o código leu um valor" e "o Jev não tem certeza de que é do cliente" vira revisão em vez de pergunta.
10. **Fato calculado no state é lido por TODAS as perguntas, não só pela que o pediu.** `customer_amounts` foi posto
    para `answered.budget`; `withdrawn.budget` também o viu, leu "até 500" como valor novo e caiu de 0,63 para 0,44
    (sonda). Um recorte de regex perde a negação que estava em volta. Antes de pôr um fato no state: que outra
    pergunta ele pode mover? Aqui a saída provável é não listar valores quando o CRM já tem o campo, ou mandar para
    revisão o campo do CRM com valor lido e `withdrawn` perto do limiar. Nenhuma foi aplicada nem medida.
11. **Corrigir um erro caro custou um erro barato, e o placar não mexeu.** 39/40 nas duas rodadas. Sem o caso a caso,
    a rodada 2 pareceria "igual com zero proibidas"; com ele, é uma troca — e a metade ruim da troca foi criada pela
    correção.
12. **Distinguir "declarado" de "do anúncio" funcionou nas perguntas e mudou onde mora o risco.** Os três Nouls
    reescritos separam bem (anúncio: 0,02–0,19; declarado: ≥ 0,66 em quartos, ≥ 0,88 em bairro). Mas o bloqueio de
    bairro e quartos do anúncio agora depende de um sinal só, `specific_property`, com margem 0,24–0,34 nos três
    casos. A margem na saída existe para isso.
13. **Custo estimado por desconto errou para baixo e descrevia um caminho que o código não tinha.** Medir exigiu
    mudar o código (requisição por variante), não a conta.

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só, mesmo fornecedor de quem construiu; n = 20/40; uma
  versão do modelo; uma rodada cega (a 2 não é). Conversa real é mais longa e mais suja (áudio transcrito, mensagens
  picadas).
- **A rodada 2 foi desenhada conhecendo o teste**: a regra do anúncio, a exclusão do preço citado e a faixa de
  revisão respondem a casos do teste (PP-T019, T022, T028), e o ajuste não tem nenhum caso de anúncio citado sem
  CRM nem de preço de anúncio. `declarado_nao` = 0,2 e `PISO_PRECO` = 50.000 não foram afinados em dado nenhum; o
  PP-T022 passou a 0,09 do primeiro. Os números da rodada 2 não medem generalização — medem que a correção faz o
  que diz nos casos que a motivaram, e o que ela quebrou.
- O normalizador é regex: lê "até", "prestação de", "R$", "o aluguel tá", escala e moeda, numeral por extenso com
  escala, correção ("quer dizer, 1600"). Não lê numeral pequeno por extenso sem escala ("até seis"), valor
  confirmado só com "isso", gíria; não vê negação nem quem é o dono do valor (isso é do Noul). Valor mensal sem
  aluguel conhecido é tratado como prestação. Provado por bateria de 38 frases, não por tráfego.
- Revisão do item: nos conjuntos só aconteceu uma vez (PP-T022) e com outra essencial faltando. O caminho "essencial
  em revisão e nada mais a perguntar → sem sugestão" só foi exercitado na bateria; a taxa de revisão em tráfego real
  não foi medida.
- `julgar_seguro` pega qualquer exceção depois da entrada: defeito de programação também vira "falha operacional" —
  a contagem à parte é o que o denuncia (0 nos três conjuntos).
- Catálogo fixo de 10 itens com pergunta escrita à mão para cada um; item novo = pergunta nova e revisão humana (o
  código recusa item desconhecido). As regras são as do LEIA-ME deste exemplo, não uma teoria de qualificação.
- A tabela do rotulador favorece calar nas regras 1, 4 e 6; por isso "sempre NQN" acerta 42,5% e a diferença entre
  variantes mora nos 23 casos em que NQN não é aceitável (`hibrida` 22/23 nas duas rodadas; palavras-chave 15/23).
- Guardas sem caso que os exercite bem: `investor_not_living` decidiu 1 caso por conjunto; `positive_reaction` só
  serve à variante `codigo`; o teto de 12 turnos / 3.000 caracteres não disparou (é faixa validada, não limiar).
- Latência medida do Brasil; ver a nota de paralelismo no custo da rodada 2. A sonda do PP-T007 são duas chamadas:
  indica a direção, não mede o tamanho do efeito.
- Valores perto do limiar trocam de lado entre chamadas idênticas (AGENTS.md, NÚCLEO §6): na rodada 1, PP-T022
  (0,43), PP-T003 (0,46) e PP-A003 (0,44); na rodada 2, `withdrawn.budget` do PP-T007 (0,42), `answered.budget` do
  PP-T022 (0,29 contra o piso 0,2), `prazo` do PP-A019 (0,50) e `quartos` do PP-T027 (0,56, decidido pelo `withdrawn`).
- Resposta do Jev não é autorização nem fronteira de segurança (limite #6): texto na conversa pode mover um Noul.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa se o manifesto congelamento.json não bate)
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação (marca "em afinação")
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 casos fáceis, só as requisições da principal → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # grava o manifesto (código, teste.json, critério); o anterior vai para congelamentos-anteriores/
set JEV_MODO=gravado                              # só o cache/ (as 147 respostas da rodada 2; as 176 da rodada 1 continuam lá), sem chave
..\..\.venv\Scripts\python.exe testa_codigo.py   # bateria do código: normalizador, regra do orçamento, portão, 2ª etapa, custo (sem chave, sem rede)
```
No Windows, use `PYTHONIOENCODING=utf-8`. A primeira execução com o teste gravou `resultados-rodada1.md`, que nunca é
reescrito. Como etapa: `proxima.julgar_seguro(jev, conversa, campos_conhecidos, catalogo)` devolve `pergunta` (ID, ou
`None` = sem sugestão: conversa acima do teto, essencial em revisão ou falha operacional — `revisar`, `falha` e
`motivo` dizem qual), `texto`, `bloqueadas` e `em_revisao` (cada item com motivo, evidência e margem), `orcamento`
(estado e leitura do código) e os números; **não levanta** por erro da chamada ou do contrato. Entrada inválida →
exceção. `proxima.julgar` é o baixo nível, que levanta a exceção; `todas=True` acrescenta a requisição de comparação.
As duas respostas da sonda do PP-T007 estão em `cache/sondas/` (o `run.py` não as usa). Receitas-irmãs:
[sugestão de skill](../../conhecimento/receitas/sugestao-de-skill.md) (Choice relativa + Noul absoluto) e
[function calling](../../conhecimento/receitas/function-calling.md) (Noul `stated`).
