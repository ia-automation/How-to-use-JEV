# Jev × LLM — o mesmo teste congelado, respondido por um LLM barato

"Jev no lugar de LLM" era só argumento de custo: nenhum LLM tinha sido medido nos testes do estudo. Este exemplo
pega três testes já congelados — [opt-out-lgpd](../opt-out-lgpd/README.md) (60 mensagens),
[motivo-de-perda](../motivo-de-perda/README.md) (68 conversas, taxonomia de 30 folhas) e
[auditor-de-evidencia](../auditor-de-evidencia/README.md) (73 afirmações) — e manda a **cada caso o mesmo pedido que
foi ao Jev** (state + `instructions`/`criteria`/opções de `perguntas.py`, em JSON) a um LLM barato, com a mesma saída
(Noul → true/false, Choice → opção), a mesma validação estrita, a mesma regra de decisão e as mesmas métricas do
exemplo. Os números vêm de [`resultados.md`](resultados.md), gerado pelo `run.py` numa rodada única
([`resultados-rodada1.md`](resultados-rodada1.md) é a cópia preservada). **Não é um estudo sobre "o melhor LLM"**:
é um LLM barato, sem exemplos no prompt, sem raciocínio pedido, temperatura 0, uma rodada.

## O que mede
Por exemplo: a métrica principal do exemplo (ação / acerto folgado / relação), o erro caro do exemplo (infração +
pela metade + bloqueio indevido / grupo errado automatizado / falsa aprovação), falha operacional (resposta fora do
esquema, contada à parte), p50/p95, tokens de entrada e saída, custo real por mil casos ao preço publicado,
concordância Jev × LLM caso a caso (decisão final e por pergunta) e o baseline de código do exemplo ao lado.

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Prompt | código ([`comparar.montar_prompt`](comparar.py)) | o pedido do Jev serializado tal qual + um texto fixo de sistema (`comparar.SISTEMA`) que explica Noul/Choice e o formato JSON — único acréscimo, igual para os três |
| Chamada, cache, medição, retries | [`_comum/llmcache.py`](../_comum/llmcache.py) | `urllib` puro (sem SDK no .venv); chave só ali, nunca impressa; modos `auto`/`gravado`/`ao_vivo` como o `jevcache` |
| Validação estrita | `llmcache.validar_resposta` | todo ID, nenhum a mais, Noul = bool JSON, Choice ∈ opções; fora disso = **falha operacional**, gravada em `invalidos/` com o texto bruto e **nunca** como resposta |
| Injeção | `comparar.ViaLLM` | Noul → 1,0/0,0, Choice → one-hot; a validação e a decisão do exemplo (`guardar_seguro` / `julgar_seguro` / `auditar`) rodam sem mudar |
| Decisão, métricas, baseline | o módulo e o `run.py` de cada exemplo, importados sem mexer | nada replicado; o manifesto deles é conferido antes (dado intocado) |
| Jev | só o cache do exemplo (`modo="gravado"`) | 0 chamadas |

## Desenho
LLM: `claude-haiku-4-5-20251001`, temperatura 0, `max_tokens` 400, timeout 60 s, 2 retries (429/5xx/rede), uma chamada
por caso **em série**, teto de 250 chamadas HTTP, parada em 429 três vezes seguidas. Preço: US$ 1,00/M entrada e
US$ 5,00/M saída (tabela pública da Anthropic, 2026-10-01). Jev: `jev-1.13.0`, US$ 0,042/M entrada, latência da rodada
original (8 em paralelo). Prompt = `{"state": …, "questions": …}` exatamente como vai ao Jev (o LLM vê os IDs das
perguntas como chaves; o Jev não os recebe — diferença declarada). Consequência da injeção: **o LLM não tem faixa de
dúvida** — `revisar` só sai dele por guarda ou regra de código.

Critério fixado antes da primeira chamada ([`criterio.py`](criterio.py), no manifesto): na métrica principal o LLM
*ganha/perde* com diferença ≥ 3 casos, senão *empata*; no erro caro, por contagem; razão de custo e de latência (p50)
LLM ÷ Jev. Falha operacional conta como erro (como `revisar`) e é reportada à parte.

**Rodadas.** Rascunho (2 casos de cada exemplo, não é métrica) rodado 3 vezes (14 chamadas) porque o motivo-de-perda
falhava de esquema; o texto de sistema ganhou duas frases genéricas ("a chave tem de existir no `criteria` DAQUELA
pergunta"; "se nenhuma serve, escolha a que melhor cabe — nunca invente chave") e nada mudou. O manifesto foi
recongelado a cada mudança (os dois anteriores estão em `congelamentos-anteriores/`); o teste rodou **uma vez** depois
do último manifesto (23:19), 201 chamadas, zero retry, zero 429.

**Assimetria declarada (revisão do Codex, achado 6): a comparação é fluxo × fluxo, não julgamento × julgamento.**
O Jev julga cada pergunta isolada (uma não vê a outra). O LLM recebe as 7 / 12 / 2n+5 perguntas num só prompt e
gera as respostas numa só sequência: vê as perguntas e opções vizinhas e as próprias respostas anteriores. As 57
respostas `only_group` em `leaf.sem_informacao` são compatíveis com contaminação entre perguntas (a válvula das outras
7 Choices); a causa não foi investigada nesta rodada. Toda conclusão abaixo vale para "o fluxo do exemplo com o Jev"
× "o mesmo pedido num prompt único ao LLM", não para a capacidade de julgamento isolado de cada um.

**Leitura secundária do motivo-de-perda (declarada, não decide).** Em 57/68 conversas o LLM respondeu `only_group` em
`leaf.sem_informacao` — a única Choice de folhas SEM essa válvula (as outras 7 têm) — quando outro grupo vencia. Pela
regra estrita é falha operacional. Como a decisão (variante c) só lê a Choice de folhas do grupo VENCEDOR, o
relatório traz também a leitura "LLM tolerante": só quando toda violação está em Choice de folhas de grupo não
vencedor (campo que ninguém lê, como o Jev também descarta as suas especulativas), o valor inválido vira placeholder e
o caso é decidido; qualquer outra violação continua falha. Zero chamada nova (lê o mesmo `invalidos/`).

**Rodada 2 — pós-revisão do Codex (2026-10-01), NÃO cega.** Seis achados, todos aceitos e aplicados; `resultados.md`
regenerado do cache da rodada 1 com **zero chamada nova** (`orcamento.json` segue em 215/250); `resultados-rodada1.md`
intocado; manifesto anterior em `congelamentos-anteriores/`. **Nenhum número de métrica mudou** (as únicas colunas
diferentes são "novas (não cache)" e "tentativas HTTP", que na rodada 2 são 0): opt-out e auditor não tiveram falha
operacional, e no motivo a classe `falha` já ficava fora do acerto folgado.

| Achado | O que mudou |
|---|---|
| 1 (grav. 2) orçamento reiniciava por execução; `auto` refaria as 57 inválidas; retries escapavam do teto | consumo persistido em `orcamento.json`, conferido antes de CADA tentativa (retry conta), compartilhado entre instâncias e execuções; falha já registrada em `invalidos/` é reproduzida também em `auto` (refazer só com `LLM_REFAZER_INVALIDAS=1`) |
| 2 (grav. 2) registro de cache sem `ms` ia à quarentena e voltava sem validar → `KeyError` no `resumo()` | cache ilegível/sem contrato → `corrompidos/` (refeito em `auto`); registro de `invalidos/` sem medição é reproduzido com medição `None` (nunca zero) e `resumo()` conta `sem_medicao` |
| 3 (grav. 2) falha operacional (→ `revisar`) pontuava quando o gabarito era `revisar`; `saida_variante` descartava a marca | marca `falha` preservada até a métrica nos três exemplos; falha fora do numerador de acerto e da concordância; `✗F` na tabela caso a caso |
| 4 (grav. 3) chave extra na raiz do JSON passava | `set(obj) == {"answers"}` |
| 5 (grav. 3) `ms` media só a última tentativa | `ms` = operação inteira, retries e esperas incluídos (os 215 registros têm 1 tentativa: sem efeito) |
| 6 (grav. 4) LLM vê perguntas vizinhas e respostas anteriores; Jev julga isolado | assimetria declarada acima; conclusão limitada a fluxo × fluxo |

Bateria ampliada para cobrir 1–5 ([`testa_falhas.py`](testa_falhas.py), 29 conferências, sem chave nem rede).

## Resultados (`resultados.md`, 2026-10-01; n = 60 / 68 / 73; LLM `claude-haiku-4-5-20251001` × `jev-1.13.0`)
| | opt-out-lgpd (ação, 5 classes) | motivo-de-perda (acerto folgado, var. c) | auditor-de-evidencia (relação, revisa = erro) |
|---|---|---|---|
| **principal** Jev · LLM · baseline | 0,867 (52) · **0,850 (51)** · 0,717 | 0,853 (58) · **0,147 (10)** · 0,279 | 0,795 (58) · **0,685 (50)** · 0,425 |
| LLM − Jev → veredito | −1 caso → **empata** | −48 → **perde** (57 falhas operacionais) | −8 → **perde** |
| **erro caro** Jev · LLM · baseline | 0 · **1** (bloqueio indevido) · 10 → perde | 4 · **1** · 41 → "ganha" só porque 57 casos não decidiram | 1/48 · **15/48** falsas aprovações · 26/48 → perde |
| falha operacional LLM | 0 | **57/68** (todas `only_group` em `leaf.sem_informacao`) | 0 |
| secundário | revisou 3/59 (Jev 7/59); tipo LGPD 18/18 (Jev 15/18); infração 0/31; pela metade 0/31 | **tolerante: 0,809 (55), −3 casos; erro caro 7 × 4; revisar 1/68 × 5/68; só-grupo 3/7 × 5/7** | cobertura 1,000 (Jev 0,836); falso alarme 2/25 (Jev 1/25); apoio precisão 0,663 (Jev 0,824) |
| concordância decisão · por pergunta | 47/60 · 387/420 (0,921) | 9/68 (estrita) · 124/132 (0,939, só os 11 válidos) | 45/73 · 555/661 (0,840) |
| p50 / p95 ms Jev × LLM | 324/663 × 1.323/1.394 (**4,1×**) | 286/338 × 2.049/2.286 (**7,2×**) | 287/387 × 1.344/1.513 (**4,7×**) |
| tokens/caso Jev × LLM (entrada+saída) | 2.028 × 2.290+95 | 6.067 × 6.623+175 | 3.609 × 3.954+101 |
| US$ por mil casos Jev × LLM | 0,085 × 2,77 (**32×**) | 0,255 × 7,50 (**29×**) | 0,152 × 4,46 (**29×**) |

Custo da construção: 215 chamadas HTTP (201 do teste + 14 de rascunho), US$ 1,07; nenhuma ao Jev.

## O que deu certo
- **opt-out-lgpd: empate na ação (−1 caso) com o mesmo pedido.** O LLM acertou os 5 casos da fronteira "tirar o
  número × apagar dados" que o Jev mandou a `revisar` (OL-T011, T028, T046, T054, T055) e o tipo LGPD 18/18 — sem
  faixa de dúvida, decide tudo. O preço disso aparece no erro caro: 1 bloqueio indevido (OL-T020, "para de mandar
  apê sem vaga": filtro lido como opt-out; o Jev revisou) e 3 negações erradas (T008 → pausar, T015 → exclusão,
  T053 → acesso) que o Jev leu certo.
- **Por pergunta, os dois concordam muito** (0,92 / 0,94 / 0,84): a diferença de decisão vem de como o código consome
  — o Jev tem o meio (revisar), o LLM não.
- **A regra estrita pegou o que tinha de pegar**: 57 respostas fora do esquema ficaram em `invalidos/` com o texto
  bruto; nenhuma entrou no cache como válida; o replay em `LLM_MODO=gravado` reproduz as falhas sem chamar.

## O que deu errado
- **motivo-de-perda: o LLM barato não respeita o esquema por pergunta num fan-out de 12.** Viu 7 Choices com
  `only_group` e usou a válvula na 8ª, que não a tem — em 57 de 68 conversas, com temperatura 0, e duas frases
  genéricas no sistema não mudaram nada. Pela regra fixada é falha operacional sistemática: a comparação de julgamento
  do motivo **não foi medida pela regra estrita**. A leitura tolerante mostra o que a regra esconde: 0,809 × 0,853
  (−3 casos, no limite do empate) com **mais erro caro** (7 × 4 grupos errados automatizados) e menos revisão (1 × 5):
  o LLM decide onde o Jev se abstém, e paga.
- **auditor-de-evidencia: 15 falsas aprovações em 48 (Jev 1).** Em todas as 15 as 4 partes (`object/state/place/scope_shown`)
  vieram `true`: o LLM responde "provado" generosamente a Nouls de parte sobre registro de outra revisão, mock,
  localhost, run cancelada — exatamente a família que a decomposição foi feita para pegar. Cobertura 1,000 (nunca
  revisa) e acerto 0,685: menos que o Jev (0,795), muito mais que o baseline (0,425).
- **Custo e latência**: 29–32× mais caro por mil casos e 4–7× mais lento em série (o Jev foi medido com 8 em paralelo;
  o LLM em série por desenho — a razão de latência é entre essas duas medições, não entre pico e pico).

## Lições
1. **O LLM responde ao padrão, não ao esquema.** Chave válida em 7 perguntas vira "válida" na 8ª. Com Choice o Jev
   não tem como sair das opções; com LLM a validação estrita é obrigatória e a taxa de rejeição é um número a medir
   (aqui 84% num formato de 12 perguntas, 0% em 7 e em 2n+5 Nouls).
2. **Sem faixa de dúvida, o erro caro sobe.** Nos três exemplos o LLM revisa menos e decide mais; onde decidir custa
   (bloquear cliente, aprovar relatório sem prova, fechar motivo errado) ele perde, mesmo empatando na acurácia.
3. **A pergunta decomposta em partes não transfere.** O que deu zero falsa aprovação ao Jev (4 Nouls de parte +
   `supports_i`) deu 15 ao LLM com o mesmo texto: as perguntas foram afinadas no ajuste contra o Jev, não contra o LLM.
4. **Concordar por pergunta não é concordar na decisão** (motivo: 0,94 × 0,13): o consumidor de código amplifica
   diferenças pequenas, por desenho.

## Limites
**Fluxo × fluxo**: o LLM responde às perguntas juntas e em sequência, o Jev isoladas — nada aqui separa "julga pior" de
"contaminou-se pelas vizinhas" (achado 6; causa não investigada). Um fornecedor e um modelo barato (Haiku 4.5 é "LLM barato", não o topo); prompt sem few-shot, sem raciocínio, sem
afinação — as perguntas foram afinadas para o Jev; temperatura 0 e uma rodada (a variação do LLM entre rodadas não
foi medida); dados sintéticos escritos pelo mesmo fornecedor do LLM; o LLM vê os IDs das perguntas (o Jev não); a
cerca Markdown (```json) é tolerada na extração; a leitura tolerante do motivo é interpretação do construtor, declarada,
não o critério; latência Jev (8 em paralelo, rodada original) × LLM (série) não é pico × pico.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py             # teste dos três (recusa sem manifesto; recusa se o manifesto de cada exemplo não bate)
..\..\.venv\Scripts\python.exe run.py rascunho [exemplo]   # 2 casos do rascunho, encanamento; não é métrica
..\..\.venv\Scripts\python.exe run.py congelar    # manifesto (código daqui, llmcache, código + teste.json dos três, critério)
set LLM_MODO=gravado                               # só cache-llm/ (215 respostas, inválidas incluídas), sem chave
set LLM_REFAZER_INVALIDAS=1                        # só se quiser refazer as 57 inválidas (consome orcamento.json; padrão = reproduzir)
..\..\.venv\Scripts\python.exe testa_falhas.py    # bateria: fora do esquema, rede/HTTP, chave ausente, injeção (sem chave, sem rede)
```
`PYTHONIOENCODING=utf-8` no Windows. Chave: `ANTHROPIC_API_KEY` ou `.local/chaves/anthropic.txt` (fora do Git),
lida só por `llmcache.py`.
