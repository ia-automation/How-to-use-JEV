# Requisito mudou (WhatsApp, pt-BR) — mantido / substituido / negado / incerto + shortlist a reavaliar

O cliente tinha requisitos registrados no cadastro (teto, vagas, quartos, bairro, elevador, pet…); chegam turnos novos
de conversa; para CADA requisito anterior o sistema diz se ele continua valendo (`mantido`), ganhou outro valor
(`substituido` + `novo_valor`), caiu (`negado`) ou ficou em aberto (`incerto`), e lista os itens da shortlist que
deixam de servir (`reavaliar`). Uma requisição ao Jev por história, com as perguntas de todos os requisitos. Os
números vêm dos relatórios gerados pelo `run.py`: rodada cega em [`resultados-rodada1.md`](resultados-rodada1.md)
(nunca regenerada); [`resultados.md`](resultados.md) é a **rodada 2, pós-revisão do Codex e NÃO cega** (seção
própria abaixo). Candidato a guarda da Luci/0800: roda sobre a conversa antes de o agente reenviar imóveis.

**Nada é executado daqui**: `substituido` é uma proposta de atualização do cadastro e `reavaliar` uma proposta ao
corretor; `incerto` é sinal para perguntar, nunca para descartar imóvel (lição 26: resposta do Jev não é autorização).

## Problema
A dor (briefing, seção P): o cliente aceitou imóvel sem elevador e depois diz que a mãe vai morar junto; a shortlist
antiga não serve mais e ninguém percebe porque o assunto da conversa continua o mesmo. Erros caros, dos dois lados:
- **mudança perdida**: requisito substituído ou negado que sai `mantido` — a shortlist velha continua valendo;
- **troca indevida**: hipótese, fala de terceiro ou requisito mantido que sai `substituido`/`negado` — o cadastro é
  trocado por fala que não decide ("se eu for promovida subo pra 800"; "minha esposa prefere Vila Mariana").

O que confunde (famílias do [LEIA-ME](dados/LEIA-ME.md)): mudança indireta (mãe que não sobe escada → `elevador`),
correção explícita (asterisco, "falei 2 mas é 1"), duas mudanças na mesma história, mudança sem valor ("dá pra
esticar"), "não faço questão" → "agora preciso", hipótese sobre o futuro, preferência de terceiro, orçamento de
outra pessoa (o irmão pagou 1,1 milhão), sugestão do corretor, negado × substituído ("com ou sem mobília"), ironia.

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Depois destes turnos o cliente continua com a mesma restrição em `q_n`? | Jev, Choice `kept / replaced / denied / uncertain` por requisito (variante principal) | julgamento semântico num catálogo fechado de 4 classes (lição 37) |
| Qual é o valor novo? | Jev, Choice entre **candidatos lidos pelo código** + `none` (só quando há candidatos) | o Jev escolhe, o código copia literal; `none` é a válvula |
| Mesmo julgamento em três sinais (`changed`, `dropped`, `open`) | Jev, 3 Nouls por requisito, mesma requisição — **variante informativa** | comparação Choice × Nouls (lição 32); não decide |
| Estado inicial dos requisitos | **cadastro** (`previous_requirements`), nunca o texto | o que está registrado é fato do sistema |
| Candidatos: números pt-BR (`_comum/numeros_br.py`), escala (compra "850" = R$ 850.000; locação "3,5" = R$ 3.500), bairros (dicionário escrito à mão + registrados + shortlist), meses, `mobiliado`/`sem mobília`, faixa de quartos/vagas | **código** | número e lista são do código (limite #2) |
| Atributo sim/indiferente (`elevador`, `pet`, `andar_baixo`, `financiamento`): `replaced` → `sim` | **código** | único valor novo possível pelo esquema |
| `replaced` sem valor utilizável (sem candidato, `none`, piso) → `incerto` | **código** | "sem valor não há substituição" (LEIA-ME) |
| Piso do vencedor (0,5) → `incerto`; validação da resposta (IDs, tipos, vencedor entre as opções, distribuição) | **código** | ausência de resposta é erro, nunca `mantido` |
| `reavaliar`: vigentes = mantido/incerto com o valor antigo, substituido com o novo, negado fora; comparação de preço, quartos, vagas, bairro, elevador/térreo, andar, pet, mobília, financiamento, mês de entrega sobre o `resumo` canônico | **código** | comparação numérica e de calendário (limites #2/#3) |
| Falha operacional → tudo `incerto` naquela história, `reavaliar` vazio, `origem: "falha"` | **código** (`requisitos.julgar_seguro`) | contada à parte, fora da métrica |
| Atualizar o cadastro, descartar imóvel, responder ao cliente | processo que chama (e LLM/humano) | efeito e texto não são do Jev |

## Desenho
State `{"previous_requirements": [{"id", "attribute", "value"}], "new_turns": [{"from": "client" | "broker",
"text"}]}` — enxuto: só o cadastro e os turnos novos; a shortlist não vai ao Jev (é do código). Por requisito, a
pergunta de status cita id, atributo, significado em inglês e valor registrado, com as regras comuns do LEIA-ME
(só o cliente decide; última fala vale; asterisco corrige; número do corretor confirmado pelo cliente conta;
mudança indireta com consequência inescapável conta; fato sobre OUTRO atributo não toca este). Tudo em
[`perguntas.py`](perguntas.py): vocabulário dos atributos, moldes das perguntas, piso, faixas, critério, dicionário
de bairros e listas do baseline. Lógica em [`requisitos.py`](requisitos.py).

Uma história com 3–6 requisitos vira 12–30 perguntas numa requisição (status + valor + 3 Nouls por requisito),
≈ 12 mil tokens, porque a descrição completa das 4 classes se repete por requisito. O teto de 12 requisitos
(`TETO_REQUISITOS`) daria ≈ 25 mil tokens — dentro dos 64k do contrato, mas é o custo dominante; acima do teto a
história não é enviada (tudo `incerto`, origem `longa`). Um molde compacto por requisito não foi medido.

## Baseline (código, sem Jev)
Palavras-chave por atributo só nos turnos do cliente (`perguntas.BASELINE_*`): negação ("não preciso mais", "tanto
faz", "com ou sem", "pode tirar"; "à vista" só para `financiamento`) → `negado`; número novo diferente na frase que
cita o atributo → `substituido`; "agora", "preciso de", "tem que ser", "inclui" → `substituido`; "talvez", "se…",
"vamos ver", "depende" → `incerto`; senão `mantido`. `reavaliar` pela mesma conta de código. Segunda referência:
**sempre `mantido`** (o baseline trivial do LEIA-ME: acerta 141/181 = 0,779 dos requisitos do teste).

## Critério de continuar/descartar (fixado ANTES de abrir o teste)
Manifesto `congelamento.json` gravado em **2026-10-01 15:41:37 (−03:00)**, depois da 2ª passada do ajuste; o
teste foi aberto e rodado UMA vez depois disso (`perguntas.py` `18d651ccebb2743c…`, `requisitos.py`
`6ff62506b8f9c7de…`, `run.py` `8ae5b6e032b90ce8…`, `dados/teste.json` `20234bc9baf6b7c1…`). Variante principal
declarada no manifesto: `choice`. No teste (44 histórias, 181 requisitos): (1) mudança perdida ≤ 2 de 28; (2)
troca indevida ≤ 4 de 153; (3) rótulo exato nos 40 mudados ≥ 0,75; (4) `reavaliar` exato ≥ 0,85 das 44; (5) rótulo
exato nos 181 ≥ 0,90. Secundário (não decide): `novo_valor` certo ≥ 0,85; detectou mudança ≥ 0,85 das 34.
Limites absolutos no erro caro + piso de acerto; o baseline é informativo (margem sobre baseline é critério frágil).
O veredito é calculado pelo `run.py`.

> Errata: o comentário sobre o critério em `perguntas.py` diz "~19h"; a hora certa é a do manifesto (15:41:37). O
> arquivo está congelado e não foi tocado — vale o manifesto.

> Cronologia do limiar (3): o piso de acerto nos mudados foi 0,70 numa versão anterior do critério e passou a 0,75
> antes do congelamento. Que essa mudança antecedeu a abertura de `dados/teste.json` é **declaração do construtor**:
> a revisão adversarial (Codex, 2026-10-01) conferiu que os hashes batem e que os 44 caches do teste são posteriores
> ao manifesto, mas não há prova independente além dos carimbos de hora locais (manifesto e arquivos de cache), que
> quem construiu controla.

A rodada 2 (abaixo) alterou `requisitos.py` e recongelou: manifesto de **2026-10-01 16:05:15** (`requisitos.py`
`653de0b0d88d772b…`; `perguntas.py`, `run.py` e `dados/teste.json` com os mesmos hashes); o manifesto cego foi para
`congelamentos-anteriores/2026-10-01T15-41-37-03-00.json`. O critério e a política não mudaram.

## Resultados — rodada 1, cega (`jev-1.13.0`, 2026-10-01; detalhes, curvas e caso a caso em `resultados-rodada1.md`)
Rascunho = 5 histórias fáceis (19 requisitos): 19/19 nas duas variantes, só encanamento. Ajuste = 22 histórias (95
requisitos; 19 difíceis), afinado em duas passadas; teste = 44 (181 requisitos; 41 difíceis), uma rodada, cega.
A linha do baseline nesta tabela é a do código da rodada 1, com os defeitos que a revisão apontou (itens 1 e 2
abaixo): a comparação era **desfavorável ao baseline por defeito nosso**; o baseline corrigido está na rodada 2.

| | ajuste (22 hist., 95 req.) | **teste (44 hist., 181 req.)** |
|---|---|---|
| baseline: total · mudados · **perdida** · **indevida** · hipótese→subst · `novo_valor` · `reavaliar` · detectou | 0,874 · 0,556 · 4/13 · 2/82 · 0/5 · 5/5 · 18/22 · 10/17 | 0,823 · 0,350 · **15/28** · **7/153** · 1/12 · 6/10 · 30/44 · 14/34 |
| sempre `mantido`: total · `reavaliar` | 0,811 · 16/22 | 0,779 · 29/44 |
| **Jev `choice`** (principal): total · mudados · **perdida** · **indevida** · hipótese→subst · `novo_valor` · `reavaliar` · detectou · alarme falso | 1,000 · 1,000 · 0/13 · 0/82 · 0/5 · 10/10 · 22/22 · 17/17 · 0/5 | **0,961 (174/181) · 0,900 (36/40) · 0/28 · 1/153 · 0/12 · 21/21 · 42/44 · 33/34 · 0/10** |
| Jev `nouls` (informativa): total · mudados · perdida · indevida · `reavaliar` · detectou · alarme falso | 0,905 · 0,944 · 0/13 · 1/82 · 22/22 · 17/17 · 3/5 | 0,923 · 0,925 · 0/28 · 1/153 · 42/44 · 34/34 · 5/10 |
| Jev `choice` por classe (acertos/gabarito): mantido · substituido · negado · incerto | 77/77 · 10/10 · 3/3 · 5/5 | 138/141 · 21/22 · 5/6 · 10/12 |
| p50 / p95 · tokens por história · US$ por mil histórias | 404 / 485 ms · 12.729 · 0,53 | 342 / 439 ms · 12.156 · 0,51 |

**Critério no teste: passou os cinco** — (1) 0/28 ✓ · (2) 1/153 ✓ · (3) 0,900 ≥ 0,75 ✓ · (4) 42/44 = 0,955 ✓ ·
(5) 0,961 ≥ 0,90 ✓. Secundários: `novo_valor` 21/21 ✓ · detectou 33/34 = 0,971 ✓. Nenhum no limite: (1) tinha
2 de folga, (2) 3, (3) 6 requisitos, (4) 4 histórias, (5) 11 requisitos.

Ajuste, 1ª passada (perguntas escritas do LEIA-ME, sem olhar resposta): Choice 92/95 — os 3 erros eram `mantido`
→ `uncertain` (0,62–0,70) por hipótese sobre OUTRO atributo (promoção/ajuda do pai → o `financiamento` ficou em
aberto; "mais uma vaga mudaria o valor?" → `orcamento`). 2ª passada: a regra do LEIA-ME "o fato não contamina os
outros atributos" entrou nas regras comuns e no `not_for` de `uncertain` → 95/95. Nada foi escrito para um caso só.
**O ajuste ficou fácil demais para calibrar** (metodo.md): o piso do vencedor ficou no 0,5 de partida; os vencedores
mais fracos do ajuste (0,61–0,78) estavam todos do lado certo.

Por família (teste, acerto nos mudados, Jev × baseline): mudança indireta 6/6 × 1/6 · duas mudanças 10/12 × 5/12 ·
mudança sem valor 3/4 × 0/4 · negado × substituído 1/2 × 1/2 · correção explícita 3/3 × 2/3 · "não faço questão" →
"agora preciso" 3/3 × 2/3 · hipótese 2/2 × 1/2 · terceiro 2/2 × 1/2 · sugestão do corretor 1/1 × 0/1 · ambíguo 2/2
× 0/2 · orçamento de outra pessoa 1/1 × 1/1 · ironia e "nada mudou" sem mudança (Jev 0 troca indevida; baseline 1).

Curva do teste (mesmas respostas, outro piso do vencedor; informativa): piso 0,6 → total 0,967, cobertura 91,7%
(um `mantido` a 0,54 viraria `incerto`, que é o gabarito); 0,7 → 0,950. A política congelada (0,5) fica.

Custo da rodada 1: **98 requisições** (orçamento 500): 5 + 22 (1ª passada), 22 + 5 (2ª passada), 44 de teste;
**1.173.754 tokens de entrada, US$ 0,049**. Nenhuma resposta sobrescrita (`cache/historico` vazio). Com a rodada 2:
115 requisições, 1.391.999 tokens, US$ 0,058 (detalhe na seção da rodada 2).

## O que deu certo
- **Zero mudança perdida no teste (0/28)** — a dor do exemplo — contra 15/28 do baseline, que não vê mudança
  indireta (5 das 6 perdidas na família) nem "não faço questão" → "agora preciso".
- `novo_valor` **21/21** copiado literal de candidato do código: números com escala ("teto caiu pra 850" → `até R$
  850.000`), correção por asterisco ("3 vagas" → "*2 vagas" → `2`), bairro somado ("pode incluir a Lapa" → `Pompeia
  ou Lapa`), `mobiliado` onde era `indiferente`. O gabarito estava entre os candidatos em 21 dos 22 `substituido`.
- Hipótese e terceiro: **0/12 virou `substituido`**; "orçamento de outra pessoa" 8/8 requisitos certos (o número
  do irmão/amigo ficou `mantido`; em RM-T015 o teto PRÓPRIO subiu junto e saiu `substituido → até R$ 850.000`),
  contra 2 trocas indevidas do baseline; ironia 4/4 `mantido` (baseline: `até R$ 2.000.000`); os dois casos
  "ambíguo" (família sem caso no ajuste) saíram `incerto` como no gabarito.
- `reavaliar` 42/44 — e os 2 erros são consequência de um erro de rótulo cada, não da conta (a conta bateu 100% com
  o gabarito nos 71 casos quando alimentada com os rótulos do rotulador).
- A válvula do valor funcionou no único caso em que o candidato certo faltava (T035): o Jev disse `none` (0,75) e o
  código rebaixou para `incerto` em vez de copiar um valor errado.

## O que falhou no teste (rodada 1; o que a rodada 2 mudou está na coluna da direita)
Sete requisitos em 181, seis histórias, em **três causas distintas** (revisão do Codex, item 6): erro semântico do
modelo (5, com `P` do vencedor de 0,51 a 0,88) · candidato ausente, defeito do gerador do código (1, status certo a
1,00) · gabarito disputável (1, `kept` 0,99). Só a primeira causa mora perto do piso.

| Caso | O que o cliente disse | Saída (gabarito) | Causa | Rodada 2 |
|---|---|---|---|---|
| RM-T001 `q3` `andar_baixo` | pai operou o joelho, "escada proibida"; corretor pergunta andar baixo; "tanto faz o andar, desde que ele não precise subir degrau" | `substituido → sim` (`mantido`) | **erro semântico do modelo — a única troca indevida, a 0,88**: `replaced` leu "não subir degrau" como andar baixo (o LEIA-ME liga escada a `elevador`, que saiu certo). Para sim/indiferente o código põe `sim` sem pergunta de valor — não há válvula `none` nesse ramo. IM-02 entrou a mais no `reavaliar` | igual (cache; 0,88) |
| RM-T001 `q5` `quartos` | o pai "fica no quarto de hóspedes" | `incerto` (`mantido`) | **erro semântico**: `replaced` 0,51 (vencedor no limite do piso), valor `none` 0,81 → `incerto` pela regra. A regra "fato sobre outro atributo não contamina" segurou a Choice de valor, não a de status | igual (cache; 0,51) |
| RM-T004 `q1` `quartos` | "tô grávida"; "não sei ainda, tô digerindo" | `mantido` (`incerto`) | **erro semântico**: `kept` 0,54 × `uncertain` 0,33: mudança sem valor com fato indireto; está a 0,04 do piso — o único caso que o piso 0,6 corrigiria. Única mudança não detectada (33/34) | saiu `incerto` (`uncertain` 0,53) — **não é mérito das correções**: a história foi reenviada porque os candidatos de bairro mudaram e a resposta de fronteira trocou de lado (NÚCLEO §6) |
| RM-T007 `q3` `orcamento` | separou-se, ficou sem móveis; "não sei se compensa pagar mais caro no aluguel ou comprar tudo de novo" | `incerto` (`mantido`) | **erro semântico**: contaminação que a 2ª passada não cobriu: a dúvida é sobre `mobilia` (saiu `incerto`, certo), mas cita o aluguel e o teto foi junto (0,68) | igual (reenviada; 0,67) |
| RM-T033 `q1` `andar_baixo` | "agora quero andar alto, do 8º pra cima" | `incerto` (`negado`) | **erro semântico**: `replaced` 0,72, `denied` baixo: o modelo leu "andar alto" como OUTRA restrição de andar, apesar de o `what` de `denied` citar esse exemplo. Como o valor já era `sim`, o código não tem valor novo e rebaixa para `incerto` — não é caro, mas o rótulo errado é do modelo | igual (cache; 0,72) |
| RM-T035 `q3` `bairro` | "quero tirar o Tatuapé e ficar com Vila Mariana ou Saúde" | `incerto` (`substituido → Vila Mariana ou Saúde`) | **candidato ausente (defeito do código)**, status certo a 1,00: o gerador fazia "novo", "atual + novo" e "novos juntos", não "tira um e põe outro"; o gabarito não estava entre os candidatos, o Jev disse `none` (certo) e o código rebaixou. Efeito na shortlist igual ao de `mantido`: os dois itens do Tatuapé ficaram (`reavaliar` `[]` em vez de `IM-01, IM-03`). O critério conta rótulos e não viu isso como mudança perdida | **corrigido pelo item 3**: 6 candidatos, `Vila Mariana ou Saúde` a 1,00; `reavaliar` `IM-01, IM-03` |
| RM-T038 `q3` `orcamento` | tia "ajuda no aluguel, mas não disse com quanto"; corretor: "mantenho 2.600 até ela confirmar?"; "isso" | `mantido` (`incerto`) | **gabarito disputável**: o cliente reafirma o teto (LEIA-ME: reafirmar → `mantido`) e o ajuste tem o mesmo padrão rotulado `mantido` (RM-A018, "Mantemos o teto de 520?" "mantém"). O rotulador seguiu "ajuda de parente sem valor → incerto". `kept` 0,99 | igual (cache; 0,99) |

Variante informativa (Nouls) no teste: `open` dispara em 10 requisitos `mantido` (e 5 histórias sem mudança ganham
alarme), mas detecta 34/34 e acerta 37/40 dos mudados (contra 36/40 da Choice): compra recall de "algo mudou" com
10 `incerto` a mais. Única troca indevida é a mesma (T001 `q3`).

## Pós-revisão do Codex (2026-10-01) — rodada 2, não cega
A revisão adversarial leu código, relatório e teste; a triagem aceitou os 7 achados (mais um 9º da família de outro
exemplo). **O teste já tinha sido visto**: nada de pergunta, limiar ou política foi afinado olhando o teste — só a
lista triada foi aplicada, toda em `requisitos.py` (itens 1–5, 9), na bateria (`testa_falhas.py`) e neste README
(6–8). O critério não mudou. Os itens 1, 3, 4 e 5 mudam os candidatos que vão na requisição, logo o cache não servia
para as histórias afetadas: `run.py congelar` (manifesto novo; o cego foi para `congelamentos-anteriores/`) e
`run.py` em `JEV_MODO=auto` reenviaram **17 histórias** (8 do ajuste, 9 do teste: T002, T004, T006, T007, T008,
T011, T019, T027, T035); as outras 49 vieram do cache. Rodada 2 = `resultados.md`; rodada 1 fica em
`resultados-rodada1.md`.

| # | O que era | O que mudou |
|---|---|---|
| 1 | Escala de dinheiro ignorava a escala já lida por `numeros_br`: "15 mil" em compra virava R$ 15 milhões; "80 mil" (compra) e "70 mil" (locação) eram descartados pela plausibilidade | `dinheiro_na_escala`: quantia explícita ("mil", "milhão", "k", "R$"/"reais") vale como veio; milhares implícitos e plausibilidade só para número SEM escala declarada ("850" → 850.000; "3,5" → 3.500). O baseline usa a mesma função (família) |
| 2 | O baseline partia a frase no ponto de milhar: "2.800 é o teto" (T024) virava `substituido → até R$ 800/mês` e os 4 itens iam para `reavaliar` | Segmentação não parte "." entre dígitos (`_FRASE`), nos dois lugares em que o baseline divide frases. `requisitos.py` está no manifesto, então a correção entra na rodada 2; a rodada 1 fica como foi (desfavorável ao baseline por defeito nosso) |
| 3 | Reduzir a lista sem acrescentar ("Tatuapé ou Vila Mariana" → "só Vila Mariana") dava zero candidatos; "tira um e põe outro" (T035) não era gerado; nome curto cadastrado ("Ahú") era descartado por ter 3 letras | Candidatos novos: subconjuntos próprios dos bairros atuais, sozinhos e com cada novo (e com todos os novos); o atual com todos os novos. O corte por tamanho saiu: tudo que entra no laço vem do dicionário ou do cadastro |
| 4 | Ano só com "de": "novembro 2027" virava `11/2026` | Separador opcional ("novembro de 2027", "novembro 2027", "nov/2027"; "11/2027" já valia); o ano declarado prevalece sobre a referência |
| 5 | O filtro temporal só tirava `MM/AAAA`, horas `18h30`, ordinais e enumerações: "3 de novembro" (T005) deixava o 3 virar R$ 3.000 (só a igualdade com o teto antigo salvou) | Saem antes da leitura de dinheiro, nesta ordem: `15/11/2026`, `11/2026`, `15/11`, "3 de novembro", "dia 15", horas |
| 6 | README: "todos os vencedores errados abaixo de 0,75" contradizia T001 `q3` (troca indevida a 0,88) e T035 (status 1,00) | Lição 4 reescrita; a tabela de erros separa erro semântico do modelo (5) × candidato ausente (1) × gabarito disputável (1) |
| 7 | — | Hipótese registrada na lição 4, **não aplicada**: guarda `changed ≥ 0,85` bloquearia T001 `q3` (0,82); os 28 substituídos/negados reais têm ≥ 0,89 |
| 8 | A mudança 0,70 → 0,75 do critério não tinha prova independente de ter antecedido o teste | Dito na seção do critério: declaração do construtor, só com carimbos de hora locais |
| 9 | Resposta em JSON válido rejeitada pela validação do contrato ficava no cache: a próxima rodada reproduzia a falha em vez de refazer o pedido | `julgar_seguro` chama `jev.invalidar(state, questions)` SÓ nessa etapa (não em falha de chamada nem de entrada); a falha continua `incerto` em todos os requisitos, contada à parte; invalidar que falha não derruba a falha fechada. Bateria com dublê prova que exatamente o pedido rejeitado é invalidado |

Bateria: 42 falhas operacionais · 93 combinações da política · 105 fatos do código (era 29 · 93 · 77): famílias dos
itens 1 ("15 mil", "80 mil", "70 mil", "1,2 milhão", "900k", "850", "3,5", "R$ 3.800"), 2 (baseline com "2.800 é o
teto", "2.500", "15 mil"), 3 (redução, troca, "Ahú"), 4 (quatro grafias do ano e mês sem ano), 5 (cada formato de
data e hora) e 9 (invalidação exata; dublê sem `invalidar`).

**Rodada 1 × rodada 2 no teste** (44 histórias, 181 requisitos; Jev `choice`, principal):

| | rodada 1 (cega) | rodada 2 (não cega) |
|---|---|---|
| total · mudados | 0,961 (174/181) · 0,900 (36/40) | **0,972 (176/181) · 0,950 (38/40)** |
| mudança perdida · troca indevida | 0/28 · 1/153 | 0/28 · 1/153 (a mesma, T001 `q3`) |
| hipótese/terceiro → substituido | 0/12 | 0/12 |
| `novo_valor` certo · gabarito entre os candidatos | 21/21 · 21/22 | 22/22 · 22/22 |
| `reavaliar` exato · detectou mudança · alarme falso | 42/44 · 33/34 · 0/10 | 43/44 · 34/34 · 0/10 |
| por classe (mantido · substituido · negado · incerto) | 138/141 · 21/22 · 5/6 · 10/12 | 138/141 · 22/22 · 5/6 · 11/12 |
| Jev `nouls` (informativa): total · mudados · perdida · indevida · `reavaliar` | 0,923 · 0,925 · 0/28 · 1/153 · 42/44 | 0,928 · 0,950 · 0/28 · 1/153 · 43/44 |
| **baseline**: total · mudados · perdida · indevida · `novo_valor` · `reavaliar` · alarme falso | 0,823 · 0,350 · 15/28 · 7/153 · 6/10 · 30/44 · 4/10 | 0,834 · 0,350 · 15/28 · 5/153 · 7/10 · 32/44 · 3/10 |
| p50 / p95 · tokens por história · US$ por mil | 342 / 439 ms · 12.156 · 0,51 | 347 / 487 ms · 12.237 · 0,51 |

Ajuste: 95/95 nas duas rodadas (8 histórias reenviadas, nenhum rótulo mudou; 12.729 → 12.861 tokens por história).

**Critério** — rodada 1: passou os cinco ((1) 0/28 · (2) 1/153 · (3) 0,900 · (4) 0,955 · (5) 0,961). Rodada 2:
**passou os cinco** ((1) 0/28 · (2) 1/153 · (3) 0,950 · (4) 43/44 = 0,977 · (5) 0,972; secundários 22/22 e 34/34).
A rodada 2 não substitui a cega como evidência: o teste já tinha sido lido quando o código mudou.

Dos 2 requisitos que passaram a acertar, **só T035 é mérito das correções** (item 3: o gabarito virou candidato e
o Jev o escolheu a 1,00; `reavaliar` fechou). **T004 `q1` virou `incerto` por variação do modelo**: a pergunta de
status é idêntica e o state também, mas a história foi reenviada (os candidatos de bairro mudaram) e o vencedor de
fronteira trocou de lado (`kept` 0,54 → `uncertain` 0,53). Com o piso em 0,5, um caso desses pode voltar na próxima
chamada. Baseline: T024 e T042 (item 2: "2.800", "4.200" inteiros), T014 (a plausibilidade compartilhada descartou
"2 quartos" lido como R$ 2.000).

Chamadas novas: **17** (orçamento 200), **218.245 tokens de entrada, US$ 0,0092** (p50 426 ms, máximo 520 ms).
Acumulado do exemplo: 115 requisições, 1.391.999 tokens, US$ 0,058. Nenhuma resposta sobrescrita nem invalidada
(`cache/historico` e `cache/invalidos` não existem).

**O que piorou**
- Tokens por história: +81 no teste (12.156 → 12.237) e +132 no ajuste, pelas combinações de bairro a mais; a Choice
  de bairro de T008 e T035 passou de 2 para 6 candidatos (sem efeito no acerto: 1,00 nos dois). Com 3 bairros
  registrados e 3 citados são 38 candidatos — ainda longe do teto de 255, mas é custo que cresce rápido.
- p95 do teste 439 → 487 ms (latência das 9 chamadas novas, medida ao vivo).
- Probabilidades que se aproximaram do piso sem cruzar, nas histórias reenviadas: T004 `q2` `kept` 0,80 → 0,73;
  T027 `q1` 0,89 → 0,88; T002 `q2` 0,98 → 0,97. Nenhum rótulo piorou; nenhuma história longa nem falha.
- O baseline continua perdendo 15/28 mudanças (os defeitos corrigidos eram todos de troca indevida e `novo_valor`).

## Lições
1. **"Código gera candidatos, Jev escolhe" só vale se o gerador cobre o valor.** T035 é o caso: a válvula `none`
   funcionou, mas o efeito na shortlist foi o de uma mudança perdida. A tabela "gabarito entre os candidatos" do
   relatório é a métrica a vigiar (21/22) — e o critério deveria contar `reavaliar` errado como erro caro, não só o
   rótulo. (Não aplicado: o teste já foi visto.)
2. **Regra de código que preenche valor sem pergunta tira a segunda leitura.** Para sim/indiferente, `replaced` vira
   `sim` direto; nos outros tipos a Choice de valor com `none` segurou 2 vezes (T001 `q5`, T035). A troca indevida do
   teste (T001 `q3`) é exatamente o ramo sem válvula. Desenho a testar: pedir `{sim, none}` também nesses atributos.
3. **Contaminação entre atributos irmãos é a família dominante de erro** (dinheiro ↔ financiamento, mobília ↔
   aluguel, escada ↔ andar): 3/3 do ajuste e 2/7 do teste. Escrever a regra geral ("judge only what is said about
   this attribute") resolveu o ajuste e deixou escapar o caso em que a fala cita literalmente o atributo vizinho.
4. **Os erros semânticos de fronteira moram perto do piso, mas não todos os erros**: 0,51, 0,54, 0,68, 0,72 são os
   vencedores errados do modelo abaixo de 0,75; a única troca indevida (T001 `q3`) saiu a **0,88**, o gabarito
   disputável (T038) a 0,99 e o candidato ausente (T035) com status certo a 1,00 — o piso não vê nenhum dos três
   (texto corrigido na revisão do Codex; a versão da rodada 1 dizia "todos abaixo de 0,75"). Os certos têm mediana
   1,00. O ajuste não tinha nenhum errado nessa faixa para calibrar (ajuste fácil não calibra). Piso 0,6 corrigiria um
   caso e custaria 1 ponto de cobertura; fica como hipótese.
   **Observação pós-teste, não validada** (Codex, item 7): uma guarda por requisito com o Noul `changed ≥ 0,85` para
   confirmar `replaced`/`denied` bloquearia a troca indevida de T001 `q3` (`changed` 0,82), e os 28 requisitos
   realmente substituídos ou negados do teste têm `changed` ≥ 0,89. Foi lida no relatório depois do teste: não é
   calibração, não foi aplicada e só valeria medida em dados novos.
5. **Choice única com descrição completa venceu os Nouls atômicos** (0,961 × 0,923), repetindo a lição 32/37: onde
   a Choice vê as 4 classes, decompor só comprou `incerto` a mais. Os Nouls detectam melhor "algo mudou" (34/34);
   podem servir de segunda leitura só para a história, não por requisito.
6. **O rótulo também erra**: T038 × A018 têm o mesmo padrão e rótulos opostos. Registrado; o placar não muda.
7. **Regex perde o indireto e dispara no dinheiro dos outros**: baseline 15/28 perdidas e 7/153 trocas — e acerta
   os `substituido` explícitos com número (6/10 `novo_valor`).
8. **O custo é das perguntas, não do state**: ≈ 12 mil tokens por história porque as 4 classes são descritas por
   requisito; US$ 0,51 por mil histórias ainda é barato, mas 12 requisitos dobrariam.

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só, mesmo fornecedor de quem construiu; n = 22/44
  histórias; uma versão do modelo; uma rodada cega. Conversa real é mais suja (áudio transcrito, erro de digitação).
- O `resumo` da shortlist segue um molde canônico (LEIA-ME): o leitor de `reavaliar` quebra fora dele e marca o item
  como "a reavaliar" (não provou que atende). Anúncio real exige campos estruturados, não texto.
- Dicionário de bairros escrito à mão (238 entradas, 228 nomes únicos, 12 cidades); bairro fora dele não vira
  candidato → `incerto`. Na rodada 1 as combinações "tira um, põe outro" não eram geradas (T035; corrigido na
  rodada 2). Mês sem ano usa a data de referência dos dados (10/2026).
- `incerto` junta duas coisas: hipótese do cliente (gabarito) e dúvida do modelo (piso). Para o corretor é a mesma
  ação (perguntar); para medir, não.
- Para sim/indiferente, `replaced` vira `sim` sem segunda leitura (lição 2). Atributo que já é `sim` e sai
  `replaced` cai em `incerto`, nunca em `negado` (T033).
- Falha operacional provada só por bateria com dublê (`testa_falhas.py`): nenhum conjunto teve falha, história longa
  ou resposta fora do contrato.
- Valores perto do piso trocam de lado entre chamadas idênticas (NÚCLEO §6: p95 ~0,05, máximo 0,15): T001 `q5`
  (0,51) e T004 (0,54) estão nessa zona.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa se o manifesto congelamento.json não bate)
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação (marca "em afinação")
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 casos fáceis → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # grava o manifesto (código, teste.json, critério); o anterior vai para congelamentos-anteriores/
set JEV_MODO=gravado                              # só o cache/ (115 respostas reais: 98 da rodada 1 + 17 da rodada 2), sem chave
..\..\.venv\Scripts\python.exe testa_falhas.py   # bateria do código: falha operacional, política, reavaliar, candidatos (sem chave, sem rede)
```
No Windows, use `PYTHONIOENCODING=utf-8`. A primeira execução com o teste grava `resultados-rodada1.md` e nunca o
reescreve. Como guarda: `requisitos.julgar_seguro(jev, requisitos, conversa, shortlist)` devolve `atualizacoes`,
`novo_valor`, `reavaliar`, `origem` (`jev` / `falha` / `longa`) e `motivo`, e **não levanta**: entrada inválida, erro
da chamada ou resposta fora do contrato → tudo `incerto`, `reavaliar` vazio, `origem: "falha"` (nunca `mantido`).
`requisitos.julgar` é o baixo nível, que levanta a exceção.
