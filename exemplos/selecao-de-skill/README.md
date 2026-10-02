# Seleção de skill (catálogo de 42, pt-BR) — no máximo uma skill, ou nenhuma

Agente com dezenas de skills carrega a errada ou nenhuma, e decidir com LLM custa uma chamada cara por turno. Este
exemplo lê o pedido e devolve **no máximo um ID do catálogo** (ou nenhum) como dica para o agente. Compara, nos
mesmos pedidos, cinco desenhos com o Jev, uma ADAPTAÇÃO LOCAL da receita oficial (não a receita ao pé da letra: ver a nota em "Receita oficial") e um baseline de código. Os números vêm
de [`resultados.md`](resultados.md), gerado pelo `run.py`; a rodada cega do teste está preservada em
[`resultados-rodada1.md`](resultados-rodada1.md) (mesmos números: não houve rodada 2; o atual foi regerado do
cache e só muda o contador de requisições novas). Candidato a
**roteador de skill/agente do parque**: roda antes do turno do agente e injeta uma linha de sugestão.

**A sugestão é dica, não autorização**: `selecao.py` não carrega nem executa nada; o agente mantém o índice e o
próprio julgamento. Receita-irmã: [sugestao-de-skill](../../conhecimento/receitas/sugestao-de-skill.md).

## Problema
Catálogo fictício de 42 skills de um parque de desenvolvimento + marketing ([`dados/LEIA-ME.md`](dados/LEIA-ME.md)),
com 17 grupos de skills próximas. Gabarito por pedido: `skill` (a melhor, ou `null`) e `aceitaveis` (conjunto).
Erros, do mais caro ao mais barato:
- **skill indevida** — carregou skill quando o gabarito é `null` (trivial, fora do catálogo, vago, conversa): gasta
  contexto e empurra o agente para um rito que não cabe;
- **skill errada** — carregou outra, fora de `aceitaveis` (sugestão errada e confiante é pior que nenhuma);
- **null indevido** — não sugeriu quando havia skill (o agente fica como estava: sozinho com o índice).

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| Validar pedido e catálogo; teto do pedido (600 caracteres) | código | forma exata; entrada inválida é erro de quem chama |
| QUAL skill, entre todas (ou `none`) | Jev, Choice `which` | espaço fechado listável; a política de `null` do LEIA-ME vai escrita no critério `none` |
| SE uma skill serve, em absoluto | Jev, Noul `fits.<id>` (texto da receita) | a Choice sempre tem vencedor; o Noul pode vir baixo para todas |
| Releitura das 3 melhores com o texto completo | Jev, Choice `rerank` + 3 Nouls `fits` + 3 portas (2ª requisição) | a resposta da 1ª decide as OPÇÕES da 2ª — único motivo legítimo para outra chamada |
| Limiares, portão, empate, no máximo UMA skill | código (`selecao.decidir`) | política: muda editando número, sem chamar a API |
| Validar toda resposta (IDs, tipo, opções, números reais em [0, 1]); falha → "sem sugestão" marcada | código | ausência de resposta é erro, nunca "nenhuma skill" julgada e nunca uma skill |
| Carregar a skill, executar, redigir | agente / LLM | o Jev não gera nem age |

## Desenho
State `{"request": <pedido>}`. O catálogo vira as opções da Choice e o texto de cada Noul (como na receita).
Perguntas em inglês; nome e descrição das skills em português, como estão no catálogo. Tudo em
[`perguntas.py`](perguntas.py); decisão em [`selecao.py`](selecao.py). Cinco formatos de requisição:

| Requisição | Perguntas | Tokens (teste) |
|---|---|---|
| `ampla` | Choice sobre as 42 + `none`, descrição **curta** (nome + 60 caracteres, o índice da receita) | 1.965 |
| `fits_vencedor` | 1 Noul `fits` do vencedor da ampla (só quando ela escolhe skill) | 354 |
| `rerank` | Choice entre as 3 melhores com a descrição **completa** + 3 Nouls `fits` + 3 portas da receita | 889 |
| `todos` | 42 Nouls `fits`, um por skill | 3.276 |
| `ampla_completa` | a Choice ampla com a descrição completa das 42 (variante informativa) | 2.573 |

Variantes (cada uma paga só as suas requisições; custo medido nelas):

| | Variante | Requisições | Como decide |
|---|---|---|---|
| a | Choice única | `ampla` | vencedor da Choice; `none` → nenhuma |
| b | Choice + `fits` do vencedor (**principal**) | `ampla` + `fits_vencedor` | vencedor, se o `fits` DELE ≥ 0,5 |
| c | receita oficial | `ampla` + `rerank` | porta ≥ 0,2 e MAIOR `fits` da shortlist ≥ 0,5 → vencedor da Choice `rerank` |
| c2 | receita + portão no vencedor consumido | idem | como c, mas o `fits` conferido é o do vencedor da `rerank` |
| d | receita corrigida | idem | vencedor = o de maior `fits` entre os 3, com o portão nele |
| e | um `fits` por skill | `todos` | o maior entre os 42, se ≥ 0,5 |
| a2 | Choice única, descrição completa (informativa, fora do critério) | `ampla_completa` | vencedor da Choice |

Desvios da receita, declarados: a Choice ampla tem a válvula `none` (a receita não tem); as 3 portas vão na 2ª
requisição e não na 1ª (para a `ampla` ser exatamente o que a Choice única paga — nossa receita faz sempre 2
requisições); não há corpo de `SKILL.md` nos dados (o "texto longo" é a descrição de 1–2 linhas); `c2` não estava
no pedido — é a "conferência do vencedor consumido" da ressalva, tomada ao pé da letra.

## Baseline (código, sem Jev)
BM25 do pedido contra id + nome + descrição de cada skill (minúsculas, sem acento, radical de 5 letras); a melhor
vence se a pontuação ≥ 4,0 (afinado no ajuste), senão nenhuma.

## Afinação (só no ajuste) e critério (fixado ANTES de abrir o teste, 2026-10-01)
Textos das perguntas: escritos uma vez a partir do LEIA-ME e **não mexidos** depois de medir. Só limiares foram
afinados, nos 36 pedidos do ajuste (partida = 0,30 da receita em tudo): `fits` 0,5; porta 0,2; BM25 4,0.
Principal escolhida pela regra "menos skill indevida; empate → maior folgado; empate → mais barata": **b**
(ajuste: 1/10 e 0,944; a 2/10 e 0,917; c, c2, d, e 3/10 e 0,917).

Critério no manifesto [`congelamento.json`](congelamento.json), com o veredito calculado pelo `run.py`:

| Critério (principal, teste) | Limite | Medido | Passa |
|---|---|---|---|
| 1 skill indevida | ≤ 2/24 | **0/24** | ✓ |
| 2 acerto folgado | ≥ baseline + 0,20 (= 0,959) | 0,931 (baseline 0,759) | **✗** |
| 3 contra a Choice única | folgado ≥ e indevidas ≤ | 0,931 × 0,920; 0 × 3 | ✓ |
| 4 null indevido | ≤ 10% (6/63) | 5/63 | ✓ |
| 5 skill errada | ≤ 5% (3/63) | 1/63 | ✓ |

**O critério NÃO passou** (4 de 5): a margem sobre o baseline foi +0,172, não +0,20. Não foi reescrito.

## Resultados [testado, 2026-10-01, `jev-1.13.0`, rodada cega única]
Teste: 87 pedidos (24 `null`, 63 com skill; 43 difíceis). Ajuste: 36 (10 `null`). Zero falha operacional.

| Variante (teste) | estrito | folgado | skill indevida | null indevido | skill errada | req | tokens | US$ por mil | p50 / p95 ms |
|---|---|---|---|---|---|---|---|---|---|
| código: BM25 + limiar | 0,678 | 0,759 | 5/24 | 8/63 | 8/63 | 0 | — | — | — |
| a · Choice única | 0,885 | 0,920 | 3/24 | 2/63 | 2/63 | 1,00 | 1.965 | 0,083 | 287 / 438 |
| **b · Choice + `fits` do vencedor** | 0,908 | 0,931 | **0/24** | 5/63 | 1/63 | 1,74 | 2.225 | 0,094 | 534 / 714 |
| c · receita oficial | 0,885 | 0,897 | 3/24 | 4/63 | 2/63 | 2,00 | 2.854 | 0,120 | 555 / 727 |
| c2 · receita + portão no vencedor | 0,862 | 0,874 | 3/24 | 7/63 | 1/63 | 2,00 | 2.854 | 0,120 | 555 / 727 |
| d · receita corrigida | 0,851 | 0,897 | 3/24 | 4/63 | 2/63 | 2,00 | 2.854 | 0,120 | 555 / 727 |
| e · um `fits` por skill | 0,828 | 0,897 | 6/24 | 1/63 | 2/63 | 1,00 | 3.276 | 0,138 | 275 / 364 |
| a2 · Choice única, descrição completa (informativa) | **0,954** | **0,977** | 1/24 | 1/63 | 0/63 | 1,00 | 2.573 | 0,108 | 263 / 350 |
| c com os limiares publicados (0,30 / 0,30) | 0,770 | 0,782 | 6/24 | 11/63 | 2/63 | 2,00 | 2.854 | 0,120 | 555 / 727 |

No ajuste (n = 36): baseline 0,722; a 0,917; b 0,944; c, c2, d, e 0,917 (folgado). `a2` não foi medida no ajuste
(orçamento de requisições; não tem limiar nem texto afinado) — só no rascunho e no teste.

Quem aponta a skill certa nos 63 pedidos com skill, sem portão: ampla curta 57 (a melhor) / 60 (alguma aceitável);
`rerank` com texto completo 60 / 61; maior `fits` da shortlist 56 / 61; maior `fits` entre as 42: 55 / 61; ampla
completa 60 / 62. A skill do gabarito estava na shortlist em 62/63.

## O que a receita oficial prometia × o que medimos
**Prometia** [doc, `jev-1.12`, 182 skills, 488 pedidos]: com 2 requisições (ranking amplo de descrições truncadas →
releitura de 3 com texto longo), o agente `claude-haiku-4-5` passa de 16,8% para 7,3% de carga de skill errada e de
9,8% para 4,0% de carga desnecessária. Limiares 0,30 / 0,30 publicados sem análise de sensibilidade.

**Medimos** [testado] outra coisa, mais estreita: o acerto da PRÓPRIA sugestão (não o comportamento de um agente
que a recebe), em 42 skills, sem corpo de `SKILL.md`. Não é réplica do número oficial. Nisso:
- **O que a variante `c` é e não é (correção da revisão do Codex, 2026-10-01):** é uma adaptação local da receita —
  acrescenta a válvula `none` na Choice ampla, usa descrição truncada em 60 caracteres no lugar do corpo das skills
  e desloca as portas para a 2ª requisição, o que obriga duas chamadas. Isso muda ranking, informação e custo.
  Portanto os números abaixo medem ESTA adaptação, em 42 skills e nesta versão do modelo; não refutam a receita
  publicada (182 skills, `jev-1.12`, comportamento de um agente). A vantagem de `a2` é **hipótese exploratória**:
  ela não foi afinada nem comparada no ajuste, só medida no rascunho e no teste.
- Com os limiares publicados (0,30 / 0,30): folgado 0,782, skill indevida 6/24 (25%), null indevido 11/63. Com os limiares
  afinados no ajuste: 0,897, 3/24, 4/63. Nos dois casos a adaptação ficou **abaixo de uma Choice só** com a válvula `none` e a
  descrição completa (a2: 0,977, 1/24, 1/63) e, em skill indevida, para a principal (0/24).
- **As portas da receita não serviram a este catálogo.** Elas perguntam "é ação ou prosa?"; aqui há skills que
  PRODUZEM texto. A porta fechou pedidos legítimos de marketing (5 variações de título de anúncio: 0,10; sequência
  de 4 e-mails: 0,13 — `prose_suffices` ≈ 0,9) e ficou aberta em triviais ("Roda o lint": 0,75). Na varredura,
  subir a porta de 0,1 a 0,4 não removeu nenhuma skill indevida (3/24 em todos os pontos) e levou o null indevido
  de 2 para 15 de 63; para zerar as indevidas seria preciso 0,6, calando 33/63.
- **O `fits` não conhece a política de "trivial → nenhuma".** "Troca a cor do botão" → `frontend-design` 0,75;
  "Roda o lint" → `fix-ci` 0,58; "Qual skill eu uso pra fazer deploy?" → `deploy-prod` 0,83. Maior `fits` nos 24
  `null`: mediana 0,23, máximo 0,83. Já a Choice com a política escrita disse `none` em 21/24 `null` e em 2/63
  com skill. Decidir SE carrega foi melhor na Choice relativa com válvula do que no Noul absoluto.
- **O texto completo ajuda, e cabe na 1ª requisição.** A releitura trocou a 1ª skill da ampla em 4 pedidos e
  acertou a melhor em 3; a mesma informação numa Choice única (a2) custou 2.573 tokens e uma requisição. Com 42
  skills de 1–2 linhas o funil curto → longo não paga; ele existe para 182 skills com corpo de 700 caracteres.

## Veredito sobre a ressalva de `padroes-das-receitas` [testado, n = 87]
A ressalva de [padroes-das-receitas](../../conhecimento/receitas/padroes-das-receitas.md) ("o portão usa o maior
`fits`, mas o vencedor vem de outra pergunta") descreve um mecanismo **real e raro**, e a correção proposta **não
se sustentou** aqui:
- Vencedor da `rerank` ≠ candidato de maior `fits` em 12 pedidos (7 com skill). O furo propriamente dito — o maior
  `fits` passa e o `fits` do vencedor consumido está abaixo do limiar — aconteceu em **3/87**.
- Num deles (T077) a receita entregou skill errada (`ads-audit`, `fits` próprio 0,36): é o defeito previsto. Nos
  outros dois (T070, T079) o vencedor da Choice ERA a skill do gabarito, com `fits` 0,25 e 0,03 — quem errou foi o
  Noul.
- **Conferir o vencedor consumido (c2)** trocou 1 skill errada por 3 nulls indevidos: folgado 0,897 → 0,874.
- **Vencedor = maior `fits` (d)** empatou no folgado (0,897) e perdeu no estrito (0,885 → 0,851): nas 7
  divergências com skill a Choice apontou a melhor em 5 e o maior `fits` em 2.
- Onde o portão no vencedor consumido pagou foi fora da receita, em **b**: ao lado de uma Choice com `none`, tirou
  as 3 skills indevidas de `a` (`fits` 0,15 / 0,21 / 0,25) ao custo de 3 nulls indevidos a mais (2 escolhas boas
  perdidas e 1 skill errada virada em nenhuma).

Leitura: o `fits` é pior seletor que a Choice e falha baixo na skill certa (composto, vago). Fica como portão, não
como seletor; e conferir o vencedor consumido é troca de erro, não ganho. Três furos são indicação, não prova.

## Erros da principal no teste (6), com causa
| Pedido | Saiu | Causa |
|---|---|---|
| T012 "confere se mais alguém consome esse campo" | `code-review` (errada; era `api-contract`) | descrição truncada: "confere quem consome cada campo" fica depois dos 60 caracteres; a2 acertou com 0,94 |
| T080 "Roda um EXPLAIN nessa query" | nenhuma (era `perf-profile`) | a ampla curta escolheu `db-query` (aceitável); o `fits` dela veio 0,39 e o portão a tirou |
| T047 "régua… primeiro WhatsApp e depois e-mail" | nenhuma (era `whatsapp-template`) | a Choice acertou; o `fits` (0,28) lê o pedido inteiro e não sabe da regra "composto → 1ª etapa" |
| T077 "diagnóstico do bug da campanha… leads não chegam" | nenhuma (era `logs-prod`) | a ampla foi atrás de "campanha" (`ads-audit`); o portão barrou (0,33): erro caro virou barato |
| T070 "Sobe isso aí." | nenhuma (era `deploy-dev`) | a regra "vago com padrão do parque → skill" não foi escrita na pergunta; `none` 0,90 |
| T072 "Planeja a integração com o portal novo." | nenhuma (era `grilling`) | `none` 0,44 × skill; com a descrição completa (a2) saiu `grilling` |

## Lições
1. **Com catálogo que cabe numa Choice, comece pela Choice única com a descrição completa e a política de `null`
   escrita na válvula.** Foi o melhor desenho medido e o mais barato em latência (1 requisição, p50 263 ms).
   Erro de desenho nosso: seguimos a receita e truncamos a descrição na variante principal; os erros T012 e T080
   vêm daí. a2 era informativa — não foi a principal declarada, então é hipótese para a próxima rodada.
2. **Noul absoluto julga adequação, não política.** O que é "pequeno demais para merecer skill" é regra do parque:
   vai escrito (na válvula da Choice), não se espera que `fits` adivinhe.
3. **Porta copiada de outra receita mede outra coisa.** As 3 portas eram para um assistente pessoal que age em
   arquivos e contas; num catálogo com skills de texto elas fecham o que devia passar.
4. **Limiar publicado não é parâmetro local.** 0,30 / 0,30 deu 6/24 de skill indevida e 11/63 de null indevido.
5. **Margem sobre o baseline é critério frágil com teto perto.** O +0,20 foi fixado com o BM25 em 0,722 no
   ajuste; no teste ele fez 0,759 e o alvo virou 0,959. O baseline, sozinho, reprova nos critérios 1 e 5 (5/24 e
   8/63) — mas o critério escrito é o que vale, e ele não passou.
6. **O mesmo Noul em requisições diferentes varia pouco**: sozinho × junto de outras, diferença média 0,011 e
   máxima 0,07 (n = 64). Perto do limiar isso troca de lado.

## Limites
- Dados sintéticos, um rotulador (Fable), um modelo, uma rodada; ajuste de 36 não calibra limiar (platôs largos).
- Mede a sugestão, não o agente: o efeito sobre carga errada/desnecessária de um agente real não foi medido.
- a2 só tem teste (n = 87) e rascunho; "piso de confiança 0,5 na Choice única" (1/24 e 0,931 no teste) é leitura
  pós-teste da varredura, não variante declarada.
- A política de `null` no critério repete exemplos do LEIA-ME (renomear variável, typo): o teste mede a política
  escrita, não a descoberta dela.
- Catálogo maior: a Choice inteira é uma pergunta só e tem de caber em 32k tokens; acima disso volta o funil.
- Latência medida com 8 pedidos em paralelo; a de 2 requisições é a soma (são sequenciais).

## Custo desta medição
571 requisições (24 rascunho, 135 ajuste, 412 teste), 1.055.669 tokens de entrada, US$ 0,044. Retentativas
internas do SDK, se houve, não são contadas.

## Como rodar
```
python run.py rascunho      # encanamento → resultados-rascunho.md
python run.py ajuste        # afinação
python run.py congelar      # manifesto (código, dados de teste, catálogo, critério, principal)
python run.py               # ajuste + teste (só com o manifesto batendo)
python testa_falhas.py      # bateria do código, sem API
JEV_MODO=gravado python run.py   # reproduz do cache/, sem chave
```
Consumidor: `selecao.selecionar_seguro(jev, pedido, catalogo)` → `{"skill", "nome", "motivo", "falha", …}`.
`falha` = True é "sem sugestão por erro operacional", diferente de `skill` = None julgado.

## Pós-revisão do Codex (2026-10-01) — sem rodada 2
Três achados, todos aceitos; nenhum mudou pergunta, política ou número, então a rodada cega continua sendo a única.
1. Texto: "a receita perdeu" e "ao pé da letra" excediam a comparação — corrigido acima (a variante `c` é adaptação
   local; `a2` é hipótese).
2. Cache: registro ilegível (gravação interrompida) ou resposta rejeitada pela validação deixava o pedido pendente
   para sempre. Corrigido na infra comum (`_comum/jevcache.py`): gravação atômica, registro ilegível vai para
   `cache/invalidos/` e a chamada é refeita, e `Jev.invalidar(state, questions)` tira do cache só o pedido rejeitado.
3. Hipótese registrada, NÃO medida: o Noul `fits` mede adequação sem conhecer a política "trivial → nenhuma"; os 6/24
   carregamentos indevidos da variante `e` não provam que um Noul não aplica essa política. Próxima rodada: um Noul
   `needs_skill` com a política escrita, na mesma requisição dos 42, como portão antes da seleção — afinar no ajuste
   e confirmar em teste novo.
