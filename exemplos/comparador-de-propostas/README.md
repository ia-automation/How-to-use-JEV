# Comparador de propostas (3 cotações × lista de requisitos, pt-BR)

## Problema
Uma imobiliária pede cotação a três fornecedores (ar-condicionado, CRM, fachada, CFTV, buffet…) e compara
as propostas contra 3–4 requisitos. Por (proposta, requisito) a célula vale `atende` / `contradiz` /
`nao_informado`; `elegiveis` = propostas sem `contradiz` em requisito obrigatório; `nao_informado` em
obrigatório **não derruba**: vira pergunta ao fornecedor. O erro caro é **aprovar uma exclusão escondida**
("instalação inclusa… Observação: os valores não contemplam infraestrutura") e, com ela, deixar uma proposta
inelegível na lista — comprar a proposta errada. Logo atrás, descartar um fornecedor sem perguntar
(`contradiz` onde era `nao_informado`). Saída por disputa: matriz + lista de perguntas a fazer a cada
fornecedor elegível. Regras de rotulagem em [`dados/LEIA-ME.md`](dados/LEIA-ME.md).

## Quem faz o quê
| Parte | Onde | Por quê |
|---|---|---|
| requisito numérico (preço ≤ X, prazo ≤ N, garantia ≥ M…): limite lido de "(`campo` <= N)" no texto, comparado com `campos` | código (`comparador.py`) | exato; o Jev não compara números (limite #2). `null`/bool/texto → `nao_informado`. 93/93 no teste, zero chamada |
| célula semântica (incluso × à parte, exclusão escondida, termo vago, anexo ausente, plano/opção, condição que o pedido já satisfaz) | Jev, 1 Choice por requisito, todos os requisitos da proposta numa requisição | espaço fechado de 3 opções; state compartilhado divide o custo |
| contexto do pedido (sede na capital, plano mensal, serviço único, preço base) | código, no state (`buyer`) | são fatos do pedido, não regra escondida na pergunta |
| válvula: `meets` com conf < 0,7 ou `contradicts` com conf < 0,5 → `nao_informado` | código, limiares em `perguntas.py` | `nao_informado` é a ação segura: vira pergunta, não aprova nem descarta |
| elegíveis, perguntas ao fornecedor, precedência (contradiz obrigatório derruba; opcional nunca) | código | é regra do LEIA-ME, não julgamento |
| validar a resposta (IDs, opção, probabilidades reais somando 1, confiança em [0,1]); falha → `nao_informado` com `falha` por proposta; resposta inválida sai do cache | código (`comparar_proposta_seguro`) | ausência de resposta é erro, nunca `atende` (AGENTS §10); bateria em `testa_falhas.py` (100 conferências, sem API) |

## Desenho (`perguntas.py` = Choice, Nouls, contexto, limiares, baseline; `comparador.py` = número, válvula, elegíveis, perguntas; critério em `run.py`)
- **State por proposta**: `{"proposal": "<texto>", "buyer": "<contexto do pedido>", "requirements": [só os semânticos]}`;
  pergunta `req_i` aponta `requirements[i]`. 1 requisição por proposta, 3 por disputa.
- **Choice** (inglês): "Does `proposal` meet the requirement in `requirements[i]` at the price it quotes?" com as
  regras do LEIA-ME em `rules` (exclusão em qualquer frase vence "incluso"; opcional/adicional/plano com preço
  = não entregue no preço cotado; termo vago e anexo ausente não atendem nem contradizem; requisito com várias
  partes exige todas; plano/opção SEM preço = pergunta) e `what`/`not_for`/`examples` por opção.
- **Desenho alternativo medido**: dois Nouls por requisito ("afirma que entrega" / "exclui ou contradiz")
  combinados em código (exclusão vence; dúvida → pergunta). No ajuste: 0,847 × 0,917 da Choice, mesma
  exclusão aprovada (0/19), metade dos tokens (1.790 × 3.439 por proposta). A Choice ficou pelo acerto.
- **Baseline de código**: número → mesma comparação; semântico → frase da proposta com palavra-chave do
  requisito: marca de exclusão na frase → `contradiz`, sem marca → `atende`, sem frase → `nao_informado`.
- **Congelamento**: `congelamento.json` (hash de `perguntas.py`, `comparador.py`, `run.py`, `dados/teste.json` +
  critério); `run.py` recusa o teste sem manifesto, com arquivo mudado ou acima do orçamento (400 requisições).
- **Critério de continuar** (fixado antes do teste): numéricas 100% · semânticas ≥ baseline + 15 p.p. · exclusão
  aprovada ≤ 5% das `contradiz` · inelegível na lista ≤ 10% das inelegíveis · `elegiveis` exatos ≥ 70%.

## Resultados (jev-1.13.0; a rodada cega está preservada em `resultados-rodada1.md`; `resultados.md` é a rodada 2)
Ajuste = 10 disputas / 30 propostas (8 difíceis; afinado nele em duas passadas). Teste = 20 disputas / 60
propostas (18 difíceis). Rodada 1 (dados v1): 72 + 48 células no ajuste, 141 semânticas (84 atende, 40 contradiz,
17 nao_informado) + 93 numéricas no teste. Rodada 2 (dados v2, abaixo): 69 + 51 e 132 + 102.

### Rodada 1 (cega, congelada em 2026-10-01 23:35 — `perguntas.py` `6107efad…`, `comparador.py` `d8f6d961…`, `dados/teste.json` `8f02e3ef…`)
Teste aberto e rodado UMA vez; relatório preservado em [`resultados-rodada1.md`](resultados-rodada1.md).

| Teste (n) | código + Jev | baseline de código |
|---|---|---|
| células semânticas certas (141) | **0,894** (126/141) | 0,660 |
| por classe: atende (84) · contradiz (40) · nao_informado (17) | 0,857 · 0,975 · 0,882 | — |
| numéricas pelo código (93) | **1,000** | 1,000 |
| **exclusão escondida aprovada** (contradiz → atende; 40) | **0/40** (sem válvula: 0/40) | 21/40 |
| **inelegível na lista** (32) · elegível fora (28) · `elegiveis` exatos (20 disputas) | **0/32** · 0/28 · **20/20** | — |
| descartou sem perguntar (nao_informado → contradiz; 17) · falso alarme (atende → contradiz; 84) | 1/17 · 0/84 | — |
| perguntas ao fornecedor (nao_informado obrigatório): precisão · recall | 0,52 · 0,88 | — |
| válvula: células movidas para pergunta | 10 (7 `meets` CERTOS a 0,39–0,65; 2 `contradicts` errados a 0,19/0,27; 1 `meets` errado a 0,13) | — |
| requisições · tokens por proposta · p50 · p95 | 60 · 3.368 · 268 ms · 543 ms | 0 |
| US$ por disputa · por mil disputas | 0,00042 · **0,42** | 0 |

Por família (acerto semântico): exclusão escondida 0,917 (36 células, 0/10 aprovadas) · termo vago 0,907 (54)
· anexo ausente 0,933 · promessa condicionada 0,867 · atende tudo menos o prazo 0,833 · fácil 0,800.
Ajuste: 0,917 (66/72), baseline 0,653, 0/19 exclusão aprovada (baseline 12/19), 48/48 numéricas, `elegiveis`
exatos 8/10, Nouls 0,847.

**Critério (rodada 1): 5/5 ✓** — (1) 93/93 · (2) 0,894 ≥ 0,810 · (3) 0% ≤ 5% · (4) 0/32 · (5) 100% ≥ 70%.

### Rodada 2 (pós-revisão do Codex, 2026-10-02 — o teste já tinha sido visto, portanto NÃO é cega)
Manifesto novo `congelamento.json` (gravado em 2026-10-02 00:04; o de 23:35 foi para `congelamentos-anteriores/`).
Causa, item a item da revisão (`.local` do coordenador; todos os 7 achados aplicados):
- **Dados v2 — 12 células saíram do Jev para o código** (achado 1, defeito de rotulagem): quatro requisitos eram
  comparação numérica rotulada `semantico` (CP-A10 "até 50 mil contatos", CP-T01 "franquia mínima de 5 mil páginas",
  CP-T18 "SLA de reparo ≤ 4 h", CP-T20 "substituição em até 24 h"). `versao` 2026-10-02, campos novos e a nota em
  `dados/LEIA-ME.md` ("ilimitados" → sentinela 999999999). A matriz do gabarito não mudou. **15 requisições novas**
  (as 12 propostas dessas disputas, choice no teste e choice + nouls no ajuste): o state perde o requisito, logo a
  chave de cache muda; as outras 48 propostas vieram do cache.
- P/R das perguntas filtrados pela elegibilidade (achado 3); Nouls com leitura dura e abstenção (achado 5);
  estrutura validada antes do lote e saída de falha sem reacessar campo ausente (achado 2); negação terminal no
  baseline (achado 6); pergunta ao fornecedor legível (achado 7). Nenhuma pergunta ao Jev mudou.

| Teste | Rodada 1 (v1) | Rodada 2 (v2) | Por quê |
|---|---|---|---|
| células semânticas certas | 0,894 (126/141) | **0,894** (118/132) | saíram 9 células, todas certas na rodada 1 (T01 r3 estava na válvula: `meets` 0,56) |
| por classe atende · contradiz · nao_informado | 0,857 · 0,975 · 0,882 | 0,863 · 0,973 · 0,867 | mesmas 14 células erradas (T01 p2 r3 foi para o código) |
| numéricas pelo código | 93/93 | **102/102** | +9 células |
| exclusão aprovada · baseline | 0/40 · 21/40 | **0/37** · 19/37 | 3 `contradiz` viraram numéricas |
| inelegível na lista · elegível fora · `elegiveis` exatos | 0/32 · 0/28 · 20/20 | **0/32 · 0/28 · 20/20** | — |
| descartou sem perguntar · falso alarme | 1/17 · 0/84 | 1/15 · 0/80 | — |
| perguntas ao fornecedor P · R | 0,52 · 0,88 | **0,71 · 0,91** | achado 3: só propostas elegíveis contam (a saída nunca perguntava a inelegível) |
| válvula · cobertura | 10 · 0,929 | 9 · 0,932 | T01 p2 r3 saiu da válvula |
| requisições · tokens/proposta · p50 · p95 · US$/mil disputas | 60 · 3.368 · 268 · 543 · 0,42 | 60 · 3.178 · 273 · 459 · 0,40 | 15 chamadas novas (cache 210 → 225 respostas) |
| **critério** | 5/5 ✓ | **5/5 ✓** | (2) 0,894 ≥ 0,817 · (3) 0/37 · (4) 0/32 · (5) 20/20 |

Ajuste: Choice 0,913 (63/69) × Nouls 0,855, baseline 0,652, numéricas 51/51, exclusão aprovada 0/18 (baseline
11/18), `elegiveis` exatos 8/10; Nouls agora com **abstenção medida**: 4 células (cobertura 0,942, antes 1,000 por
construção — achado 5). O desenho e os limiares não mudaram; a rodada que conta como cega é a 1.

## O que deu certo
- **Exclusão escondida é o que o Jev lê melhor**: 39/40 `contradiz` certos (o único erro foi `nao_informado`,
  não `atende`), "incluso" no começo + exclusão na última frase 10/10; o baseline aprova 21/40 porque procura a
  palavra-chave na mesma frase — a família existe exatamente por isso.
- **Elegíveis exatos em 20/20 disputas** (inclusive CP-T06, sem elegível) — a matriz erra em células que não
  mudam a lista: `atende` que virou pergunta mantém a proposta elegível.
- **Número no código, zero chamada**: 141 das 234 células vão ao Jev; 93 são comparação com o limite do texto.
- **Válvula do lado `contradiz` pagou**: dois `contradicts` errados (0,19 e 0,27) viraram pergunta em vez de
  descarte; sem válvula, `elegiveis` exatos cai de 20/20 para 19/20 (curva 0,0/0,0).
- **Uma requisição por proposta**: 268 ms, US$ 0,42 por mil disputas (3 mil propostas).

## O que falhou (visto no teste — NÃO corrigido, vira lição)
1. **Exclusão vizinha contamina a célula** (7 `meets` certos a 0,39–0,65 → pergunta): "tinta lavável" ao lado de
   "fim de semana com acréscimo de 20%" (T02 p3, 0,49); "vídeo aéreo editado" ao lado de "documentação conforme
   anexo" (T03 p3, 0,53); "entregas expressas (até 3 horas)" ao lado de "fora do perímetro têm acréscimo" (T16 p3,
   0,65); "80 kVA com QTA" ao lado de "instalação por eletricista do cliente" (T09 p3, 0,39). A instrução "exclusão
   em qualquer frase vence" faz a exclusão de OUTRO item baixar a confiança do item certo.
2. **CONF_ATENDE 0,7 não pagou**: exclusão aprovada é 0/40 em toda a grade (de 0/0 a 0,9/0,9); o lado `atende` só
   agiu certo uma vez, a 0,13 (T05 p3, termo vago) — de 0,39 a 0,65 moveu apenas células certas, 7 perguntas a mais
   (precisão das perguntas 0,52). A 0,5/0,5 o acerto seria 0,929 com os mesmos 20/20 elegíveis.
3. **Qualificador literal** (3 `not_stated` com gabarito `atende`): "manutenção preventiva mensal" sem "dos 2
   elevadores" (T06 p2, 0,48); "quadro de transferência automática" para "QTA" (T09 p1, 0,44 — sigla); "40 camisas
   com bordado" sem "do logotipo" (T14 p3, 0,61). O modelo lê ao pé da letra (limite #1); o rotulador aceita.
4. **"Mesmo dia" × "até 3 horas"** (T16 p2): gabarito `contradiz` (entrega outro prazo), Jev `not_stated` 0,24.
5. **Termo vago aprovado com confiança** (T20 p3, `meets` 0,86 — gabarito `nao_informado`): "com Windows e
   Office" para "licenciados". A única célula em que faltou a pergunta e a válvula não alcança.
6. **Descartou sem perguntar 1/17** (T02 p2): "tinta acrílica fosca" para "tinta lavável", `contradicts` 0,53 —
   "outra tinta" lido como "outra coisa"; a 0,7 no lado `contradiz` seria pergunta (curva 0,7/0,7: 0/17, 0,901).

## Lições
1. **A exclusão de outro item vaza para a célula** quando o state é a proposta inteira. Candidato à próxima
   versão: o código recorta as frases candidatas por requisito e manda as exclusões como lista à parte — hipótese,
   não medida.
2. **Limiar por risco precisa de curva que o sustente**: aqui o lado `atende` nunca errou acima de 0,13 e o lado
   `contradiz` errou abaixo de 0,3. A faixa útil é assimétrica ao contrário do que o risco sugeria.
3. **O que "cobre" o requisito é política de rotulagem**, não do modelo: "instalação inclusa" genérico, sigla,
   qualificador omitido. Escrever no LEIA-ME antes dos casos — foi o que fez as regras de "várias partes" e "plano
   com/sem preço" entrarem na pergunta sem overfit (afinação em `perguntas.py`).
4. **Choice × Nouls com as mesmas regras**: a Choice acerta +7 p.p. e custa 2× tokens (as glosas repetem por
   requisito); para volume, os Nouls são a alternativa barata que ainda não aprova exclusão.
5. **O baseline mostra onde o Jev vale**: 0,66 × 0,89 no total, 21/40 × 0/40 na exclusão escondida.

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só; propostas de 2–5 frases, mais curtas e limpas que
  PDFs reais. n = 141 células semânticas no teste (132 na v2): 1 célula = 0,7 p.p.; 1 exclusão aprovada = 2,5 p.p.
  em 40. Rotulagem corrigida uma vez pelo construtor (v2) — o rotulador original não revisou a mudança.
- Uma versão (`jev-1.13.0`), uma rodada; 7 células entre 0,39 e 0,69 podem trocar de lado da válvula.
- `trechos` do gabarito (evidência literal) não são medidos: a Choice não devolve trecho.
- Requisito numérico só com o limite já no texto ("(`campo` <= N)") e `campos` já normalizados pelo rotulador;
  a extração do número da proposta não é o que este exemplo mede.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa sem congelamento.json ou com arquivo mudado)
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 disputas, só encanamento → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação, nos dois desenhos
..\..\.venv\Scripts\python.exe run.py congelar   # roda o ajuste e grava o manifesto antes de abrir o teste
..\..\.venv\Scripts\python.exe testa_falhas.py   # bateria do código com dublê, sem API
set JEV_MODO=gravado                              # reproduz tudo do cache/, sem chave
```
