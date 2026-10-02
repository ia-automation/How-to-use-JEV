# Imóvel errado (atendimento imobiliário, pt-BR) — manter / trocar_referente / pedir_esclarecimento

O cliente discutiu os imóveis A e B; a última mensagem diz "o outro, o da varanda maior"; o agente preparou
uma resposta com os fatos de A. Antes de enviar, decidir: (a) de qual candidato a última mensagem do cliente
trata — ou `null`, não dá para saber; (b) se o rascunho usa fatos de outro candidato. Os números vêm de
[`resultados.md`](resultados.md), gerado pelo `run.py`. Candidato a guarda da Luci (0800), entre o rascunho e
o envio. **Nenhuma mensagem é enviada daqui; o rascunho nunca é reescrito** — `trocar_referente` só sugere
o candidato certo para quem gera a resposta.

## Problema
A dor: o cliente fala de dois (ou quatro) imóveis parecidos, troca de foco, cita uma fala antiga do agente,
corrige-se ("não, o primeiro"), ou usa um atributo que dois candidatos têm — e o agente responde com o preço,
a vaga, o pet ou o condomínio do imóvel errado. O **erro caro** é o rascunho sobre outro imóvel que recebe
`manter` (a resposta errada iria ao cliente); logo atrás vem a troca que sugere o candidato errado. O custo do
outro lado é interromper o cliente com "de qual imóvel você fala?" quando a conversa já diz qual. Regras de
rotulagem em [`dados/LEIA-ME.md`](dados/LEIA-ME.md).

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Filtrar e ordenar candidatos, montar o state, mapear a resposta ao ID | código | o Jev escolhe entre o que recebe; a ordem de apresentação ("o primeiro") é dado, não julgamento |
| De qual candidato a última mensagem trata (ou nenhum)? | Jev, **Choice** com uma opção por candidato + `not_enough_information` | seleção entre candidatos existentes (receita da extração pré-parseada): o ID devolvido sempre existe |
| A referência aponta para exatamente um? | Jev, Noul absoluto `unambiguous_reference` | segunda leitura do "não dá para saber": a confiança da Choice não denuncia empate (NÚCLEO §6) |
| O rascunho usa fato de outro candidato que não o referente? | Jev, Noul relacional `draft_uses_other` | o gabarito é relacional (nomear cada candidato com o fato certo NÃO conta) — decompor em "fato de cada um" perderia a distinção |
| O rascunho se compromete com um candidato (quando não dá para saber qual)? | Jev, Noul absoluto `draft_commits_to_one` | com referente nulo, comprometer-se É o erro (LEIA-ME); pedir, responder genérico ou comparar não é |
| Piso de confiança, faixas, ação, sugestão | código (`referente.py`, números em `perguntas.py`) | política: muda editando número, sem chamada nova |
| Comparativos numéricos ("o mais barato", "o maior", "o de mais vagas") | código (`referente.comparativos`): extrai preço, área, quartos e vagas do resumo e põe `comparatives` no state; só quando todos têm o valor e não há empate | comparar 720 × 740 é conta, não julgamento; o Jev lê o resultado (rodada 2; na rodada 1 a instrução dizia "the cheaper one" e a conta ficava com o Jev) |
| Candidatos válidos antes da chamada (2–4, IDs únicos ≠ válvula, resumo não vazio) · conversa dentro do teto (12 turnos / 3.000 caracteres) | código → **erro** / `pedir_esclarecimento` "conversa longa", sem chamada | ID repetido viraria UMA opção da Choice em silêncio; a faixa validada é 3–10 turnos |
| Resposta ausente, ID fora da lista, distribuição da Choice incompleta, número fora de [0,1] (ou bool/string) | código (`congelamento.choice/noul`) → **erro**, nunca `manter` | NÚCLEO §10 |

Fora do Jev de propósito: gerar a resposta certa (LLM).

## Desenho
- **State** `{"conversation": [{"from", "text"}], "candidates": [{"id", "summary"}], "draft", "comparatives"}` —
  a conversa inteira (o referente depende do histórico), os resumos na ordem de apresentação, o rascunho e,
  desde a rodada 2, `comparatives` (`cheapest`, `most_expensive`, `largest`, `smallest`, `most_bedrooms`,
  `most_parking` → ID), calculado pelo código. ~1.500 tokens na rodada 1; ~1.630 com `comparatives`.
- **4 perguntas na mesma requisição.** A Choice `referent` é montada por conversa: chave = ID, descrição =
  "Presented first/second…: resumo" (o cliente diz "o primeiro" e "o de 720", nunca o ID). A instrução traz
  as regras de precedência do LEIA-ME em linguagem literal (correção > nome/atributo único > citação de fala
  do agente > "o outro"/pronome > continuidade; descartado sai do jogo), manda resolver comparações pelo
  `comparatives` (rodada 2) e diz quando escolher a válvula.
- **Teto da conversa** (`perguntas.TETO_TURNOS` 12 / `TETO_CARACTERES` 3.000): acima dele a conversa não é
  enviada; `pedir_esclarecimento` com motivo "conversa longa", contada à parte em `resultados.md`. Nos dados
  (3–10 turnos, ≤ ~300 caracteres) o teto não disparou em nenhum dos 77 casos — é a faixa validada, não um
  limiar afinado.
- **Política** (`referente.decidir`): válvula, confiança < 0,5 ou `unambiguous_reference` ≤ 0,3 →
  `pedir_esclarecimento`; senão `draft_uses_other` ≥ 0,7 → `trocar_referente` (sugere o vencedor), ≤ 0,3 →
  `manter`, meio → **`trocar_referente`** (regenerar com o candidato certo é barato; fato errado enviado é
  caro). No caso nulo, `rascunho_usa_outro` sai do Noul "se compromete com um" (só informa; a ação é pedir).
- **Afinação no ajuste** (24 conversas, 18 difíceis, 4 nulas): a 1ª versão acertou os 24; uma 2ª versão que
  explicitava "resposta sim/não com o fato do outro" no `draft_uses_other` não moveu nenhum valor (±0,04,
  ruído de repetição) e foi revertida. Nenhum limiar foi movido: a curva do ajuste é plana (0 erro em
  qualquer piso × faixa). O portão `unambiguous_reference` nunca mudou uma decisão; fica por desenho.

## Baseline (código, sem Jev)
`referente.baseline`: assinatura de cada candidato = tokens do resumo que só ele tem (bairro, preço,
metragem; sem palavras genéricas de anúncio e sem números de 1 dígito); o referente é o candidato citado na
mensagem mais recente que cita exatamente um (varrendo cliente e agente do fim para o início); nenhum → pedir.
`rascunho_usa_outro` = assinatura de outro candidato no rascunho. Mede o que "último imóvel citado por nome"
resolve e o que não vê: "o outro", "o primeiro", "o que tem piscina", a correção, o fato copiado sem nome.
Segundo baseline, **`sempre pergunta`**: pedir esclarecimento em toda conversa — zero erro caro ao custo de
interromper 100% dos clientes; é o preço de evitar todo erro sem julgamento.

## Critério de continuar/descartar (fixado ANTES de abrir o teste, 2026-10-01)
Continua se, no teste (48 conversas), o Jev tiver:
1. **resposta errada que iria ao cliente ≤ 1/48 (2,1%)** — soma de erro caro (rascunho de outro imóvel →
   `manter`) e troca sugerindo candidato errado;
2. **acerto do referente (nulo incluído) ≥ baseline + 0,15**.
Secundário (não decide): nulos → `pedir` ≥ 6/8; `pediu sem necessidade` ≤ 10% dos não nulos.

**Resultado (rodada 1): PASSOU** — 0/48 respostas erradas (erro caro 0/19, troca para o errado 0/40); referente
1,000 contra baseline 0,700 (+0,30). Secundário: nulos → `pedir` 8/8; pediu sem necessidade 0/40. Os 3 erros do
teste são `trocou sem necessidade` (3/25), o lado barato — estão em "O que falhou", não corrigidos.

Desde a rodada 2 (revisão adversarial, achado 4) o item 1 soma uma terceira parcela: **sugeriu candidato
quando o gabarito exige esclarecimento** (gabarito `referente: null` → `manter`/`trocar_referente`). Na rodada 1
essa parcela não era contada para ninguém — o baseline tinha 3/8 (IE-T042 troca para IM-02 com gabarito nulo;
IE-T017 e IE-T039 mantêm) fora do erro publicado; o Jev, 0/8. O critério vive em `perguntas.CRITERIO_CONTINUAR`
e entra no manifesto `congelamento.json`: mudar o critério recusa o teste até congelar de novo.

## Resultados (`jev-1.13.0`, 2026-10-01; detalhes, curvas e caso a caso em `resultados.md`)
Ajuste = 24 conversas (18 difíceis, 4 nulas), afinado nele; teste = 48 conversas (33 difíceis, 8 nulas).

### Rodada 1 (cega, congelada em 2026-10-01 11:38 — `perguntas.py` `25e7b7cdbe7a5d6d…`, `referente.py` `61480de1c0a47c29…`, `dados/teste.json` `2c07ffb6e6e37c45…`)
Teste aberto e rodado UMA vez (o hash do teste é o mesmo de antes de o construtor começar). Relatório completo
preservado em [`resultados-rodada1.md`](resultados-rodada1.md); manifesto retroativo, gravado com os arquivos
originais intactos, em `congelamentos-anteriores/2026-10-01T11-38-00-03-00.json`. Os números abaixo são os
dessa rodada, inalterados.

| Ação | ajuste (n = 24) | teste (n = 48) |
|---|---|---|
| baseline "último citado": acerto · **erro caro** · troca p/ errado · pediu sem nec. · referente | 0,500 · 3/10 · 2/20 · 6/20 · 0,500 | 0,542 · **8/19** · 2/40 · 9/40 · 0,700 |
| "sempre pergunta": erro caro · interrompidos | 0/10 · 24/24 | 0/19 · 48/48 |
| **Jev** (congelado): acerto · **erro caro** · troca p/ errado · pediu sem nec. · trocou sem nec. · referente | 1,000 · 0/10 · 0/20 · 0/20 · 0/13 · 1,000 | **0,938 · 0/19 · 0/40 · 0/40 · 3/25 · 1,000** |
| Choice crua: referente certo (nulo incluído) · nulo → válvula · não nulo → válvula | 24/24 · 4/4 · 0/20 | 48/48 · 8/8 · 0/40 |
| `rascunho_usa_outro` composto (≥ 0,5): Jev · baseline por palavra-chave | 1,000 · 0,458 | 0,958 · 0,562 |
| Nouls (≥ 0,5) no subconjunto que decidem: `unambiguous_reference` · `draft_uses_other` · `draft_commits_to_one` | 1,000 · 1,000 · 1,000 | 1,000 · 0,950 (38/40) · 1,000 (8/8) |
| p50 / p95 · tokens por conversa · US$ por mil conversas | 266 / 313 ms · 1.533 · 0,064 | 269 / 356 ms · 1.514 · 0,064 |

Matriz do teste, Jev (linhas = gabarito): manter 22/3/0 · trocar 0/15/0 · pedir 0/0/8. Por família (teste,
ação): troca de foco 3/4, citação de fala antiga 6/6, parecidos 5/5, referência vaga 6/8, correção 2/2,
atributo que só um tem 2/2, atributo que dois têm (nulo) 5/5, outros nulos 2/2, fáceis 13/13. Baseline nas
mesmas famílias: 0,00–0,69, salvo "só um tem" (2/2) e fáceis (0,69).

Curva do teste (mesmas respostas, outros limiares; informativa): limiar único 0,5 nos Nouls → **1 erro caro**
(IE-T028, 0,40); faixa 0,3–0,7 (atual) → 0 erro caro, 3 trocas a mais; piso 0,7 na Choice → 2 dos 3 erros
viram `pedir` (cobertura 0,79, erro 0,026) — ver lição 2.

### Rodada 2 (pós-revisão, NÃO cega, 77 chamadas novas por causa do item 5)
Correções da revisão adversarial (Codex, 2026-10-01; triagem da sessão principal, 6 achados, 6 aceitos).
O item 5 — comparativos calculados pelo código e postos no state — muda o state de TODAS as conversas, logo
o cache não serve: **24 chamadas novas no ajuste, 48 no teste e 5 no rascunho (77; 126.452 tokens de entrada,
US$ 0,0053, medidos nos 77 registros novos de `cache/`)**. O teste já tinha sido visto na rodada 1, portanto a rodada 2 não aprova nada às cegas: a
rodada que conta como teste é a 1. Manifesto novo `congelamento.json` (gravado em 2026-10-01 12:16, cobre
`perguntas.py`, `referente.py`, `run.py`, `dados/teste.json` e o critério).

| Número (teste, n = 48) | Rodada 1 | Rodada 2 | Por quê |
|---|---|---|---|
| acerto da ação · trocou sem necessidade | 0,938 · 3/25 | **0,958 · 2/25** | IE-T031 ("quintal não, é apartamento") deu `draft_uses_other` **0,22** (era 0,41) e saiu da faixa de dúvida → `manter` ✓. O critério do Noul NÃO mudou; mudou o state (`comparatives`) e a chamada foi outra — repetição varia ~0,01–0,15 (Limites), então é movimento de borda, não correção |
| erro caro · troca p/ errado | 0/19 · 0/40 | **iguais** | nenhum rascunho errado passou; nenhuma troca para o candidato errado |
| sugeriu candidato c/ gabarito nulo (novo, achado 4) | não contado (Jev 0/8; baseline 3/8) | **Jev 0/8 · baseline 3/8** | os 8 nulos foram à válvula nas duas rodadas (0,61–1,00); o baseline troca IE-T042 para IM-02 e mantém IE-T017/IE-T039 com gabarito nulo — agora dentro da soma |
| **RESPOSTA ERRADA (soma; critério 1)** | 0/48 (sem a 3ª parcela) | **Jev 0/48 · baseline 13/48** | baseline: 8 erros caros + 2 trocas erradas + 3 com nulo |
| referente (Choice crua, nulo incluído) · nulo → válvula | 48/48 · 8/8 | **iguais** | os 4 casos com comparação ("o mais barato" IE-A012/IE-T026, "o maior" IE-T037) já acertavam na rodada 1 com a conta no Jev; com `comparatives` acertam com 1,00. "O mais perto do metrô" (IE-A013) não está na lista de comparativos aceita e segue com o Jev (1,00) |
| IE-T044 · IE-T034 (os outros 2 erros originais) | trocar ✗ (0,51 / 0,80) · trocar ✗ (0,62 / 0,41) | **trocar ✗ (0,51 / 0,81) · trocar ✗ (0,54 / 0,46)** | mesma causa (lição 2): a Choice hesita e o Noul relacional herda; nada da lista aceita toca isso |
| IE-T028 (o caso que a faixa segura) | usa 0,40 → trocar ✓ | usa **0,45** → trocar ✓ | continua na faixa de dúvida; limiar único 0,5 continuaria com 1 erro caro (curva) |
| `rascunho_usa_outro` composto · `draft_uses_other` ≥ 0,5 | 0,958 · 38/40 | **iguais** | |
| tokens por conversa · p50 / p95 · US$ por mil | 1.514 · 269 / 356 ms · 0,064 | 1.634 · 264 / 346 ms · 0,069 | +120 tokens de `comparatives` por conversa |
| conversas acima do teto (achado 6) | — | **0/48** (0/24 ajuste, 0/5 rascunho) | dados têm 3–10 turnos; o teto é faixa validada, não disparou |

Ajuste: 1,000 em tudo nas duas rodadas (24/24 referente, 0/24 resposta errada; baseline sugeriu candidato c/
nulo 1/4 → soma 6/24); 1.656 tokens por conversa. Curva do ajuste continua plana (0 erro em qualquer piso ×
faixa). Critério (rodada 2, com a 3ª parcela): (1) 0/48 ✓ · (2) 1,000 ≥ 0,850 ✓ — mas não vale como aprovação
cega.

Correções sem efeito nos números (o conjunto não tinha o caso; valem como contrato): candidatos inválidos
(fora de 2–4, ID repetido, ID igual à válvula, resumo vazio) viram erro antes da chamada — na rodada 1 um ID
repetido virava uma opção só, em silêncio; contrato da resposta validado pela infra comum (`type`, distribuição
completa da Choice somando ~1, confiança e Nouls como número real em [0,1]) — as 101 respostas gravadas da
rodada 1 passam na validação nova, nenhuma era inválida; manifesto `congelamento.json` com `run.py` e o critério,
o anterior preservado em `congelamentos-anteriores/`.

## O que deu certo
- **Choice com uma opção por candidato + válvula acertou os 72 referentes** (ajuste + teste), nulos
  incluídos: os 12 nulos foram para `not_enough_information` (0,64–1,00) e nenhum não nulo caiu nela. As
  famílias que o baseline não vê — "o outro" com três candidatos (só um não discutido), "não, o primeiro",
  "você disse que o da varanda…", "o que tem piscina", "o mais barato", "o de 2 quartos" com dois de 2
  quartos (→ nulo), "o que a gente viu ontem" (→ nulo), descarte que deixa dois com pet (→ nulo) — passaram
  inteiras no referente. As regras de precedência do LEIA-ME escritas em linguagem literal na instrução
  bastaram; nenhuma foi reescrita no ajuste.
- **Zero resposta errada ao cliente nos 72 casos**: os 29 rascunhos que usavam outro imóvel receberam
  `trocar_referente` com o candidato certo; o baseline de palavra-chave deixou passar 11 deles (8/19 no
  teste) — é a família "copia o fato sem nomear" ("Aceita sim", "É sim, mobiliado", "não tem vaga também"),
  invisível para regra de nome.
- **A faixa de dúvida com dúvida→trocar fez o que devia**: no teste, a zona 0,40–0,60 do `draft_uses_other`
  tinha 3 `true` (0,40 / 0,50 / 0,60) e 2 `false` (0,41 / 0,41). Limiar único 0,5 teria enviado IE-T028
  ("O do Ingá não tem vaga também" — fato de Botafogo repetido). O desenho pagou com 2 regenerações a mais.
- **Nulo tratado como nulo**: com referente nulo, `draft_commits_to_one` separou "se compromete com um"
  (0,63–0,96) de "pede/compara" (0,06–0,12), 12/12 nos dois conjuntos. Um Noul absoluto bastou; não foi
  preciso um por candidato.
- **Uma requisição por conversa**, 4 perguntas, ~1.500 tokens, ~270 ms, US$ 0,064 por mil conversas.
  Guarda viável entre o rascunho e o envio da Luci sem latência perceptível.

## O que falhou no teste (NÃO corrigido; a lista é a da rodada 1 — na rodada 2, IE-T031 passou por movimento de borda, não por conserto; IE-T044 e IE-T034 continuam)
1. **IE-T044** (`trocar` com gabarito `manter`): "o sobrado de santa felicidade tem churrasqueira?" → agente
   responde e emenda "o apê do Batel tem churrasqueira na sacada" → "esse tem piscina?". Gabarito: Batel (último
   em foco). Choice deu Batel com **0,51** (quase empate com Santa Felicidade, que tem piscina) e
   `draft_uses_other` **0,80** sobre "Piscina não tem, mas a sacada com churrasqueira compensa" — o Noul
   leu o rascunho como resposta sobre Santa Felicidade (que TEM piscina) e viu contradição. O erro é do
   referente, não do rascunho: o Noul relacional resolve o referente de novo, por conta própria, e com a
   Choice em 0,51 ele resolveu diferente. Rotulagem discutível também: a mensagem do cliente antes era sobre
   Santa Felicidade e "esse" após a emenda do agente é fronteira fina — a confiança 0,51 avisou.
2. **IE-T034** (`trocar` com gabarito `manter`): "o de 2 vagas tem elevador?" → agente descreve os dois →
   "e o outro tem quantos m²?". Choice Vila Romana **0,62**; rascunho "O da Vila Romana tem 70 m²" (certo)
   deu `draft_uses_other` **0,41**. Mesma causa: o Noul herda a incerteza do referente.
3. **IE-T031** (`trocar` com gabarito `manter`): "ele tem quintal?" sobre Osasco (apto); rascunho "Quintal
   não, é apartamento. Mas o condomínio tem lazer completo com playground." → **0,41**. O rascunho NEGA
   para o referente um atributo que o outro candidato tem (quintal de Cotia) e acrescenta um detalhe que
   nenhum resumo tem (playground). O `false` do Noul não lista "nega para o referente um atributo do outro"
   (leitura literal, limite #1).
4. **Sem erro na Choice, mas as três confianças mais baixas do teste** (0,51, 0,62 e 0,64) são exatamente os
   dois erros acima e um nulo: a confiança da Choice avisou onde o resto do desenho ia tropeçar.

## Lições
1. **Choice entre candidatos com válvula é o desenho certo para "de qual fala"**: 72/72 com as regras de
   precedência escritas literalmente na instrução. Não precisou de pergunta por regra nem de LLM.
2. **Um Noul relacional resolve o referente por conta própria** — e pode resolver diferente da Choice.
   `draft_uses_other` ("fato de outro candidato que não o que o cliente quer") embute a mesma pergunta da
   Choice; quando a Choice hesita (≤ 0,62), o Noul hesita ou erra junto (2 dos 3 erros). Dois caminhos, não
   medidos: (a) portão de confiança da Choice mais alto só para `manter` (piso 0,7 no teste: 2 erros a menos,
   2 `pedir` a mais); (b) tirar a resolução do referente do Noul — um Noul absoluto por candidato "o
   rascunho dá como resposta os fatos de `candidates[i]`" e o código compara com o vencedor da Choice, que
   passa a ser o ÚNICO lugar que decide o referente. (b) perde a distinção "nomeia cada um com o fato certo",
   que precisaria de outro Noul. É política e desenho; fica para a próxima versão.
3. **Explicitar o caso no critério não é garantia de mover o número**: a cláusula "resposta sim/não com o
   fato do outro conta" não tirou os três 0,6 do ajuste do lugar (±0,04). Esses casos exigem conferir o resumo
   do referente (contradição) — é uma pergunta diferente ("o rascunho contradiz o resumo do referente?"),
   não uma frase a mais na mesma.
4. **A faixa de dúvida se paga quando o lado da dúvida é o barato**: regenerar com o candidato certo custa
   uma chamada de LLM; enviar o fato do outro imóvel custa a confiança do cliente. Com o limiar único a
   cobertura não mudava e havia 1 erro caro; com a faixa, 0 — e 3 regenerações desnecessárias em 48.
5. **Ajuste fácil não calibra a faixa** (mesma lição da triagem e da guarda): no ajuste todo `false` ficou
   ≤ 0,11 e todo `true` ≥ 0,60; a borda inferior (0,40–0,41) só apareceu no teste.
6. **Negação do atributo do outro** ("quintal não, é apartamento") lê como "usa fato do outro" para o Jev;
   é uma família de rascunho correto que o `false` precisa nomear.
7. **Baseline de nome resolve 70% do referente e nenhuma cópia de fato sem nome**: o que o Jev acrescenta
   não é o bairro citado — é "o outro", "o primeiro", a citação de fala antiga e o fato copiado.

## Limites
- **Dados sintéticos** escritos por LLM (Fable), um rotulador só, sem ver o código; mais limpos que conversas
  reais de WhatsApp (áudio transcrito, várias mensagens seguidas, imóveis fora da lista). n = 24 e 48: um caso
  vale 2,1 pontos no teste; "0/19 erro caro" é um teste de 19 rascunhos errados.
- Um modelo (`jev-1.13.0`), uma rodada; repetir a mesma chamada varia ~0,01 (máx. 0,15): IE-T044 (Choice
  0,51 contra piso 0,5) e os Nouls em 0,40–0,41 podem trocar de lado numa repetição.
- Os candidatos vêm prontos (2–4 resumos, na ordem de apresentação); na Luci, montar essa lista a partir do
  histórico é trabalho do código, e o resumo precisa ter os campos que o cliente cita (preço, bairro,
  metragem). Resumo sem o atributo citado → o Jev não tem como escolher.
- `trocar_referente` sugere o candidato; não verifica a resposta regenerada — isso é outra passagem desta
  mesma guarda.
- Não é fronteira de segurança (limite #6): texto do cliente ou do rascunho que "argumenta" move a resposta.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa se o manifesto congelamento.json não bate)
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação (marca "em afinação")
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 casos do construtor → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # grava o manifesto (código, teste.json, critério); o anterior vai para congelamentos-anteriores/
set JEV_MODO=gravado                              # só o cache/ (178 respostas reais: 101 da rodada 1 + 77 da rodada 2), sem chave
```
No Windows, use `PYTHONIOENCODING=utf-8`. Como guarda da Luci: `referente.conferir(jev, caso)` recebe
`{"conversa", "candidatos", "rascunho"}` e devolve `acao`, `sugestao` e `motivo`; `manter` → envia;
`trocar_referente` → regenera com `sugestao`; `pedir_esclarecimento` → pergunta ao cliente (inclusive
"conversa longa", acima do teto, sem chamada); candidatos inválidos ou erro da chamada/contrato → exceção,
não envia (ausência de resposta nunca vira `manter`).
