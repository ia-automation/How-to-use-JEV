# Compactação de contexto (sessão de agente, pt-BR) — manter / descartar por mensagem

Sessão longa de agente de programação (12–25 mensagens de `usuario | assistente | ferramenta`) com uma
`tarefa_atual`: ao compactar, qual mensagem fica e qual sai? Resumir tudo com LLM custa caro e perde o detalhe
decisivo (a restrição dita no começo, o hash do commit, o erro ainda aberto). Este exemplo julga UMA sessão por
requisição e devolve, por mensagem, `manter` ou `descartar`. Os números vêm dos relatórios gerados pelo `run.py`:
a rodada cega está em [`resultados-rodada1.md`](resultados-rodada1.md); [`resultados.md`](resultados.md) é a
rodada 2 (pós-revisão, não cega, regenerada do cache em modo `gravado`: mesmos números; ver
[Pós-revisão](#pós-revisão-do-codex-2026-10-01--rodada-2-não-cega)) e a variante de desenho está em
[`resultados-variantes.md`](resultados-variantes.md).

**Veredito: REPROVADO para descarte automático** (rodada cega, `jev-1.13.0`, 2026-10-01): necessária descartada
12/169 = 7,1% no teste, acima do limite absoluto de 6% fixado antes. Pela regra escrita antes, a faixa de dúvida vira
`manter` e todo descarte vai a revisão humana; não é um compactador automático.

**Nada é apagado daqui.** A saída é a lista que o compactador recebe; o histórico bruto continua onde está, e
quem apaga (ou resume) é o processo que consome a lista.

## Problema
O erro caro é **necessária descartada**: uma restrição ainda válida, uma decisão vigente, um valor em uso ou um
erro aberto somem do contexto e o agente continua sem eles. **Manter demais** só custa tokens. O baseline óbvio,
"`papel = usuario` → manter", acerta 79% no ajuste e 75% no teste (aviso do rotulador em
[`dados/LEIA-ME.md`](dados/LEIA-ME.md)): o ganho possível mora nas mensagens do usuário descartáveis (conversa,
decisão revertida, tarefa encerrada) e nas do assistente/ferramenta necessárias (placar, erro aberto, valor literal).

O que confunde (famílias do LEIA-ME): restrição antiga ainda válida; decisão revertida (a antiga sai, a nova
fica); saída longa com UMA linha necessária; conclusão de tarefa anterior que é premissa da atual; restrição que
caducou; resposta curta que depende da pergunta ("a 1", "pode"); hipótese descartada de erro aberto × de erro já
explicado; contorno em vigor; valor corrigido; progresso parcial; decisão embutida em elogio; redundância (resumo
com o literal vence a saída bruta); tarefa interrompida.

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Validar a sessão (campos, papel no enum, IDs únicos), ordem, papel de cada mensagem, faixa validada (≤ 25 msgs, ≤ 20 k caracteres: acima → manter tudo, sem chamada) | **código** (`compactacao.preparar`, `fora_da_faixa`) | é exato; o Jev não conta nem ordena |
| Se esta mensagem sumisse, quem continua `current_task` perderia um fato que não está em outra mensagem nem se recupera relendo o repositório? | Jev, Noul `needed` (um por mensagem) | a pergunta do rotulador, com as listas dele; espaço fechado |
| Algo que ela afirma/pede foi substituído, corrigido, revertido, respondido ou resolvido DEPOIS? | Jev, Noul `superseded` (um por mensagem) | veto da guarda: decisão revertida, valor corrigido, pergunta já respondida |
| Restrição/decisão do usuário que ainda vale? · Último placar, pergunta aguardando resposta, diagnóstico de erro aberto? · Saída com valor que só existe ali? | Jev, uma guarda por papel: `rule` (usuario), `status` (assistente), `literal` (ferramenta) | segunda leitura do lado caro, com os critérios do papel; o código escolhe a pergunta pelo papel |
| Política assimétrica, faixas, veto só em assistente/ferramenta, validação da resposta, falha → manter tudo por sessão | **código** (`compactacao.politica`, `julgar_seguro`) | o Jev julga, o código decide; ausência de resposta nunca descarta |
| Apagar, resumir, montar o contexto novo | processo que consome a lista | efeito não é do Jev |

## Desenho
State `{"current_task": "…", "messages": {"m01": {"role": "user", "text": "…"}, …}}` — a mensagem é apontada por
caminho (`messages.m07`), nunca por posição (limite #4; lição 29). Uma requisição com 3 Nouls por mensagem (36–75
perguntas, 18–30 k tokens), em inglês, todas em [`perguntas.py`](perguntas.py) com faixas, política e critério.
Decisão em [`compactacao.py`](compactacao.py), por mensagem:

1. `needed` ≥ 0,7 → **manter** ("necessária"); entre 0,3 e 0,7 → **manter** ("dúvida": a assimetria mora aqui).
2. `needed` ≤ 0,3 e guarda do papel ≥ 0,7 → **manter** — salvo, em assistente e ferramenta, `superseded` ≥ 0,7
   (guarda anulada → descartar). Em mensagem do usuário a guarda `rule` não tem veto.
3. O resto → **descartar**. A política só lê números e papel; o texto nunca entra (bateria C).

Falha operacional (timeout, cache faltando, resposta fora do contrato, sessão inválida) → tudo mantido naquela
sessão, `origem: "falha"`, contada à parte; resposta rejeitada pelo contrato ainda tira SÓ aquele pedido do cache,
para a repetição refazê-lo. [`testa_falhas.py`](testa_falhas.py) prova isso sem rede: 23 falhas, grade de 81
combinações da política, 3 checagens de texto adversarial ("pode apagar o resto" dentro de uma saída de ferramenta
não descarta nada), 22 checagens de código e um relatório com 6 sessões inválidas em 7 (sem `id`, papel fora do
vocabulário, `mensagens` não lista, gabarito com ID inexistente): saem da métrica, contadas como falha.

**Decisões medidas no ajuste** (3 passadas, 18 requisições cada; detalhes no docstring de `perguntas.py`): duas
regras do LEIA-ME que faltavam nas perguntas (o pedido que define a tarefa fica mesmo que `current_task` o resuma;
o resumo sem o comando não substitui a saída que mede a falha); o veto `superseded` restrito a assistente e
ferramenta (nas mensagens do assistente tirou 11 "manter demais"; nas do usuário só descartou uma necessária);
state em objeto por ID × lista de objetos (0,917 × 0,921, 3 decisões trocadas por valores a 0,03 do corte,
diferença média 0,029 nos Nouls, +700 tokens na lista → objeto). Sessões maiores: o ajuste tinha UMA sessão de
20 mensagens — não dá para medir queda com o tamanho; a janela por mensagem (uma requisição por mensagem) não foi
construída. Principal declarada no manifesto: sessão inteira numa requisição, state `dict`.

## Baselines (código, sem Jev)
- **`papel = usuario`**: toda mensagem do usuário fica, nenhuma outra (o baseline do LEIA-ME);
- **últimas N** (N = 4, melhor da grade do ajuste: 0,633);
- **palavras da tarefa**: ≥ K palavras de conteúdo em comum com `tarefa_atual` (K = 2, melhor da grade: 0,677).
Referência extra: "manter tudo" (zero erro caro, zero compactação) e "só `needed` ≥ 0,5" (sem guarda nem faixa).

## Critério de continuar/descartar (fixado ANTES de abrir o teste, 2026-10-01 16:03)
No teste (468 mensagens na métrica: 169 `manter`, 299 `descartar`): (1) **necessária descartada ≤ 6% das
necessárias (≤ 10 de 169)** — limite absoluto; (2) acerto por mensagem ≥ 0,85; (3) acerto ≥ melhor baseline no
próprio teste + 0,08. Secundário, não decide: manter demais ≤ 20%; precisão de `manter` ≥ 0,75. Está no manifesto
[`congelamento.json`](congelamento.json) e o veredito é calculado pelo `run.py`.

## Resultados (`jev-1.13.0`, 2026-10-01; rodada cega, uma execução)
Ajuste = 18 sessões, 235 mensagens (229 na métrica; 84 `manter`, 145 `descartar`; 16 difíceis). Teste = 36
sessões, 477 mensagens (468 na métrica; 169 / 299; 31 difíceis). Manifesto gravado antes; teste rodado uma vez.

| | ajuste (229 msgs) | teste (468 msgs) |
|---|---|---|
| `papel = usuario`: acerto · precisão/cobertura · **nec. descartada** · manter demais | 0,795 · 0,76/0,64 · 30/84 · 17/145 | 0,752 · 0,67/0,63 · **63/169** · 53/299 |
| últimas 4: acerto · nec. descartada | 0,633 · 49/84 | 0,628 · 101/169 |
| palavras K=2: acerto · nec. descartada | 0,677 · 53/84 | 0,682 · 105/169 |
| só `needed` ≥ 0,5: acerto · nec. descartada · manter demais | 0,852 · 34/84 · 0/145 | 0,823 · 77/169 · 6/299 |
| **Jev (política)**: acerto · precisão/cobertura · **nec. descartada** · manter demais | 0,917 · 0,82/0,99 · 1/84 · 18/145 | **0,861 · 0,75/0,93 · 12/169 (7,1%) · 53/299 (17,7%)** |
| Jev: nec. descartada do usuário | 0/54 | 2/106 |
| Jev por papel (acerto): usuario · assistente · ferramenta | 0,986 · 0,929 · 0,814 | 0,868 · 0,864 · 0,847 |
| `needed` ≥ 0,5 contra o gabarito · Brier | 0,852 · 0,11 | 0,823 · 0,12 |
| guarda ≥ 0,5 contra o gabarito do papel: `rule` · `status` · `literal` | 0,986 · 0,818 · 0,797 | 0,887 · 0,742 · 0,730 |
| requisições · p50 / p95 · tokens por sessão · US$ por mil sessões | 18 · 438 / 536 ms · 19.905 · 0,84 | 36 · 415 / 672 ms · 20.226 · 0,85 |

A coluna do ajuste é a 3ª passada, a mesma do manifesto, como está em `resultados-rodada1.md` (a versão anterior
desta tabela trazia números de uma passada anterior do ajuste em quatro linhas: por papel, Brier, guardas e
latência/custo — corrigido na rodada 2; ver Pós-revisão, item 4).

**Critério no teste: REPROVADO no (1)** — 12/169 = 7,1% > 6% (o limite era 10). (2) 0,861 ≥ 0,85 ✓ (passou por
0,011). (3) 0,861 ≥ 0,752 + 0,08 = 0,832 ✓. Secundários: manter demais 17,7% ✓; precisão 0,748 ✗ (por 0,002).
Pela regra escrita antes: **não serve para descartar sem revisão** — a faixa de dúvida vira `manter` e o resto
vai a humano; não é um compactador automático.

Por família no teste (acerto · nec. descartada): contorno em vigor 1,000 · 0/8; restrição que caducou 0,962 ·
0/9; decisão embutida 0,929 · 0/4; hipótese descartada 0,896 · 2/17; resposta curta que depende da pergunta
0,889 · 2/13; restrição antiga ainda válida 0,880 · 0/9; decisão revertida 0,853 · 1/23; conclusão anterior é
premissa 0,838 · 2/14; valor corrigido 0,792 · 1/10; saída longa com uma linha necessária 0,773 · 1/23 (14/43 de
manter demais); progresso parcial 0,769 · 1/9; redundância 0,727 · 1/5; tarefa interrompida 0,700 · 0/3; fáceis
0,934 · 1/22. Por tamanho: 12–13 msgs 0,851 (26 sessões) · 14–16 0,893 (8) · 17–22 0,854 (2): sem queda visível,
mas 2 sessões grandes não medem nada.

Custo total da construção: 113 requisições (orçamento 400) — 5 de rascunho, 54 em três passadas de ajuste, 18 da
variante, 36 de teste; 2.219.023 tokens de entrada, US$ 0,093.

## O que deu certo
- **O Jev bateu o baseline nos três conjuntos sem olhar o papel**: 0,861 × 0,752 no teste, com cobertura de
  `manter` 0,93 contra 0,63 — a regra "usuário fica" perde 63 das 169 necessárias (todos os placares, erros abertos
  e valores literais do assistente e da ferramenta); a política perdeu 12.
- **A assimetria funcionou onde foi desenhada**: necessária descartada do USUÁRIO 2/106 (o baseline, por
  construção, 0/106; mas com 53 "manter demais"). Restrição antiga ainda válida 0/9, restrição que caducou 0/9,
  contorno em vigor 0/8, decisão embutida 0/4.
- **A faixa de dúvida é o que segura o erro caro**: com corte único em 0,5 o acerto sobe a 0,889 e as necessárias
  descartadas vão a 28/169; com 0,4–0,6, 0,895 e 22/169. A curva é a mesma do ajuste (3ª passada: 0,4–0,6 dá 0,939
  e 4/84; corte único, 0,952 e 5/84): a troca acerto × erro caro foi prevista, e o critério escolheu o erro caro.
- **O código sem rede provou o que os dados não exercitam**: 22 falhas operacionais caem em "manter tudo"; texto
  que manda apagar dentro de uma saída de ferramenta não move uma decisão.

## O que falhou (12 necessárias descartadas no teste, cada uma com a causa)
| Sessão | Msg | Família | Causa |
|---|---|---|---|
| CC-T011 | m07 (assistente) | redundância; resposta curta | pergunta "R$ 0,00 ou traço?" cuja resposta é "Traço.": `status` 0,93, **veto `superseded` 0,87** ("respondida depois") anulou a guarda. `needed` 0,29 |
| CC-T014 | m08 | resposta curta | "Sigo essa convenção?" → "Na última, nesse caso": `status` 0,95, veto 0,91. `needed` 0,29 |
| CC-T015 | m02 | resposta curta que depende da pergunta | as três opções de "A segunda.": `status` 0,89, veto 0,90. `needed` 0,29 |
| CC-T029 | m05 | resposta curta que depende da pergunta | "Posso apagar 2026-07 e 2026-08?" → "Pode.": `status` 0,90, veto 0,90. `needed` 0,27 |
| CC-T012 | m07 | saída longa com uma linha necessária | diagnóstico com o hash do commit que renomeou os IDs, e pergunta respondida: `status` 0,88, veto 0,83. `needed` 0,23 |
| CC-T008 | m17 | decisão revertida | placar "rotina pronta… ainda não rodei em dev": `status` 0,80, veto 0,84 (a rodada veio depois). `needed` 0,27 |
| CC-T018 | m11 | progresso parcial | placar "(3) parado… aguardando o usuário": `status` 0,82, veto 0,84 (o usuário respondeu). `needed` 0,21 |
| CC-T003 | m09 | valor corrigido | resumo do assistente que traz o erro com os literais (vence a saída bruta): `needed` 0,28, `status` 0,59 — lido como repetição da saída que ele mesmo resume |
| CC-T004 | m05 | hipótese descartada | medição resumida com os números (18.422 envios, 1.307 repetidos): `needed` 0,19, `status` 0,56 — o mesmo: o resumo que vence a saída bruta é lido como redundante |
| CC-T020 | m04 (usuario) | conclusão anterior é premissa | fato do usuário ("obrigatório desde a 0158; o app antigo não manda") que vale igual para a tarefa atual: `needed` 0,29, `rule` 0,42 — lido como parte da tarefa encerrada |
| CC-T033 | m01 (usuario) | hipótese descartada | o pedido que define a tarefa ("descobre e corrige"), com `tarefa_atual` dizendo "correção feita": `needed` 0,29, `rule` 0,50 — a regra escrita na 2ª passada não bastou quando a tarefa já está quase fechada |
| CC-T036 | m05 | conclusão anterior é premissa | resumo com o hash do revert (chão da tarefa atual): `needed` 0,28, `status` 0,52 |

- **7 dos 12 são o veto `superseded` anulando `status` numa pergunta já respondida que dá sentido a uma resposta
  curta, ou num placar que o usuário respondeu.** No ajuste o veto foi medido em 11 perguntas do assistente cuja
  resposta era completa sozinha ("banco ou front?" → "no banco, pela rota…") e acertou todas; a família "resposta
  curta que depende da pergunta" tinha UMA sessão no ajuste (CC-A006, segurada por `needed`). O `false` de
  `superseded` não separa "respondida por completo" de "respondida por 'pode'". Sem o veto, no teste: 5/169 (3%,
  passaria o critério 1) mas acerto 0,827 e 76/299 de manter demais (reprovaria o 2). Com o veto em 0,9: 8/169 e
  0,840. **Na grade que o `run.py` examinou** (faixas 0,5–0,5 · 0,4–0,6 · 0,3–0,7 · 0,2–0,8 · 0,1–0,9; guarda e
  veto em 0,5 a 0,9 e desligados; um parâmetro por vez) **nenhum ponto passa os três critérios**. Fora da grade
  existe ponto que passaria: a revisão do Codex (2026-10-01) recalculou das mesmas respostas a faixa 0,27–0,7 com
  guarda e veto em 0,7 — 5/169 e acerto 0,8504 (precisão 0,716, abaixo do secundário). É análise POSTERIOR ao
  teste, feita com o teste aberto: não vale como calibração (seria afinar no teste) e a reprovação fica. O que
  sobra é o mesmo: o veto está mal desenhado para a família "resposta curta", e ajustar corte não é conserto.
- **Resumo que vence a saída bruta** (T003, T004, T036): `needed` lê "o mesmo fato está em outra mensagem" e
  descarta o resumo E mantém a saída bruta — ou nenhum dos dois. A regra do LEIA-ME ("fica UMA: o resumo com o
  literal") exige comparar duas mensagens e escolher, coisa que um Noul por mensagem, isolado, não faz.
- **O ajuste previu 1,2% de erro caro e o teste deu 7,1%**; manter demais 12% → 18%. Dezoito sessões com uma ou
  duas por família não calibram expectativa (lição de 2026-10-01).

## Lições
1. **Veto do lado barato é guarda do lado caro ao contrário.** `superseded` só existe para descartar; cada vez que
   dispara numa mensagem necessária, é erro caro. No ajuste ele comprou 11 acertos baratos em perguntas respondidas;
   no teste custou 7 necessárias da família que o ajuste não tinha. Veto que anula uma guarda precisa de `false`
   escrito com a família do erro caro (resposta curta; placar respondido) E de casos dela no ajuste — ou não entra.
2. **"Fica UMA das duas" não cabe num Noul por mensagem.** Redundância (resumo × saída bruta) é relação entre
   duas mensagens; em perguntas isoladas o Jev ou mantém as duas ou descarta as duas. Desenho a medir: Choice por
   par ("qual das duas fica?") composta em código, ou regra de código (saída bruta cujo valor literal aparece em
   mensagem posterior do assistente sai) — o literal é comparável por igualdade.
3. **A faixa de dúvida vira `manter` e é o que segura o erro caro**: 163 de 468 mensagens do teste caíram nela
   (35%); 114 delas eram `manter` no gabarito. O veredito diz o que fazer com ela: a dúvida FICA (manter, sem
   revisão) e o que vai a humano é o DESCARTE — as 269 de 468 (57%) que `needed` nega com folga, onde moram as 12
   necessárias perdidas. Revisar a dúvida seria revisar o lado que já está certo; o erro caro está no descarte.
4. **Uma requisição com 75 Nouls funciona e custa pouco** (p95 672 ms, US$ 0,85 por mil sessões): o estado da
   arte do custo é o das perguntas (1.400–1.500 tokens por mensagem, 93% da requisição), não do state. Encurtar
   os critérios é a primeira economia — a medir, porque os critérios são as regras do LEIA-ME.
5. **Margem sobre o baseline passou; o limite absoluto reprovou.** Com n = 169 necessárias, 2 mensagens
   separam 6% de 7,1%: o critério absoluto fez o que o método pede (reprovar e ficar escrito), e a lição de
   2026-10-01 sobre "um caso decide o veredito" vale aqui também.

## Pós-revisão do Codex (2026-10-01) — rodada 2, não cega
A rodada 1 (cega) foi vista antes desta rodada; por isso **nada de faixa, limiar, pergunta ou política mudou** e
o critério é o mesmo. Seis achados, todos aplicados ou registrados:
1. **Resposta inválida presa no cache** (grav. 2): quando a validação do contrato rejeita uma resposta com JSON
   válido, `compactacao.julgar` tira SÓ aquele pedido do cache (`jevcache.invalidar`), para que a repetição em
   `auto` o refaça em vez de reaproveitar a resposta inválida; a sessão continua saindo com tudo mantido,
   `origem: "falha"`. Falha de chamada ou de entrada não invalida nada; falhar ao invalidar não muda o desfecho.
   Bateria com dublê: 23 casos (11 rejeições invalidam exatamente o pedido feito; timeout e cache faltando, nada).
2. **Sessão sem `id` derrubava o relatório** (grav. 2): `run.sessao_invalida` separa, ANTES das métricas e de
   qualquer chamada, a sessão que `preparar` recusa ou cujo gabarito cita ID inexistente / não é lista; ela é listada
   no relatório e contada como falha. Bateria: 6 inválidas em 7, relatório fechado, métrica só com a válida.
3. **Frase falsa** ("nenhum ajuste de limiar passa os três critérios"): restrita à grade examinada; o ponto fora da
   grade (0,27–0,7) está registrado como análise posterior ao teste — não aplicado.
4. **Números do ajuste no README**: quatro linhas da tabela traziam uma passada anterior do ajuste; agora a coluna é a
   3ª passada, a do manifesto (por papel 0,986 · 0,929 · 0,814; guardas 0,986 · 0,818 · 0,797; Brier 0,11; p50/p95
   438/536 ms; US$ 0,84 por mil sessões), e a curva do ajuste citada em "O que deu certo" também.
5. **Orientação**: o topo declara "reprovado para descarte automático" e a lição 3 diz o que o veredito diz —
   manter a dúvida, revisar o descarte.
6. **Hipótese registrada, não medida** (grav. 4, desenho): decisões por mensagem isoladas não preservam dependência
   — em CC-T015 a política descarta `m02`, que define as opções de "A segunda.". Proposta: tratar pergunta→resposta
   como UMA unidade e, na redundância, escolher um representante e só descartar a contraparte depois de confirmar que
   o valor literal está preservado no representante. Não aplicada: exige outro desenho (par ou código) e outra rodada.

Rodada 2 em `JEV_MODO=gravado`, manifesto novo (`congelamento.json`, 16:18; o cego de 16:03 está em
`congelamentos-anteriores/`), **zero chamadas novas** (36 requisições do teste, todas do cache). Rodada 1 × rodada 2:

| | rodada 1 (cega, `auto`) | rodada 2 (não cega, `gravado`) |
|---|---|---|
| teste: acerto · precisão/cobertura · nec. descartada · manter demais | 0,861 · 0,748/0,929 · 12/169 · 53/299 | idêntico |
| ajuste: acerto · nec. descartada · manter demais | 0,917 · 1/84 · 18/145 | idêntico |
| critério (1) · (2) · (3) · secundários | ✗ 7,1% · ✓ 0,861 · ✓ 0,861 ≥ 0,832 · manter demais ✓, precisão ✗ | idêntico |
| requisições novas (não cache) | 36 (teste) | 0 |
| veredito | REPROVADO no (1) | REPROVADO no (1) |

`resultados-rodada1.md` não foi regenerado; o `diff` com `resultados.md` muda só o modo, a hora/hashes do manifesto e
a coluna "novas (não cache)".

## Limites
- Dados sintéticos de um rotulador só (Fable), por famílias; teste com as mesmas famílias. **Um placar assim
  valida o mecanismo, não o desempenho em sessões reais** (mensagens reais são mais longas, com mais ferramenta
  e menos texto do usuário). Uma rodada, um modelo.
- Sessões de 12–22 mensagens e até 3 k caracteres: fora disso o código mantém tudo sem chamada. Sessões reais de
  100+ mensagens passam de 64 k tokens com 3 Nouls por mensagem — exigem janela (várias requisições) que **não
  foi construída nem medida**; o acerto por tamanho (26/8/2 sessões) não mede queda.
- Discutíveis do rotulador (9 no teste) ficam fora da métrica; a política decidiu 4 delas como `descartar`.
- A saída não diz O QUE de uma mensagem mista continua valendo: manter a mensagem inteira é o contrato (unidade
  = mensagem).
- Não medido: texto adversarial real no state (a bateria prova só que o CÓDIGO não lê o texto; o Jev lê, e
  conteúdo que argumenta pela própria necessidade move o Noul — limite #6); sessões com várias tarefas abertas;
  idiomas além de pt-BR com comandos em inglês.

## Rodar
```
python run.py rascunho      # encanamento (5 sessões)
python run.py ajuste        # afinação
python run.py variantes     # state dict × list, no ajuste
python run.py congelar      # grava congelamento.json
python run.py               # ajuste + teste (exige o manifesto batendo)
python testa_falhas.py      # bateria do código, sem chave nem rede
```
`JEV_MODO=gravado` reproduz tudo do `cache/` sem chave (113 registros: as três passadas de ajuste, o rascunho, a
variante em lista e o teste). No Windows, use `PYTHONIOENCODING=utf-8`. A primeira execução com o teste gravou
`resultados-rodada1.md`; o `run.py` nunca o reescreve. `resultados.md` é a rodada 2 (gravado, pós-revisão).
