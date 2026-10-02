# Roteador de e-mail (dado REAL anonimizado) — o Jev entre a regra e o LLM

O classificador de e-mail em produção (F11) decide cerca de 2/3 das mensagens por regra e manda o resto a um LLM
(Claude → Codex → API). Este exemplo mede o Jev como **degrau entre a regra e o LLM**: uma requisição por e-mail,
o Jev decide sozinho o que tem confiança e **escala só o incerto**. Classes: `principal`, `notificacoes`,
`promocoes`, `redes_sociais`, `spam`, `golpe`. Os números vêm do relatório gerado pelo `run.py`: a rodada cega
(rodada 1) está em [`resultados-rodada1.md`](resultados-rodada1.md); a rodada 2, pós-revisão e NÃO cega, é o
[`resultados.md`](resultados.md) atual (seção "Pós-revisão do Codex" abaixo).
Candidato a degrau no serviço 0802 — **não aprovado pelo critério nas duas rodadas** (4 de 5 nas duas).

**Nada é executado daqui**: `roteador.py` devolve `decide` + classe ou `escala`; mover de pasta é do serviço.

## Dado e privacidade
- 738 e-mails de produção já classificados pelo F11, **anonimizados** (152 de ajuste, 586 de teste, separados por
  domínio do remetente), enviados à API da TypeSafe com aval do dono em 2026-10-01. Endereço e domínio do
  remetente não existem no dado: viraram um pseudônimo de grupo e sinais calculados em código.
- **Nenhum texto de e-mail está neste repositório.** Aqui há código, o relatório com agregados, IDs `EM-xxxx`,
  classes, `decidido_por`, números do Jev e sinais calculados em código, e este README. O arquivo de dados e o
  cache do Jev (que contém o state) ficam fora do Git; sem eles o `run.py` para com "dados privados ausentes". O
  relatório versionado é a prova pública. O nome da regra interna de produção (`regra`) não é exportado.
- **Duas versões do dado anonimizado.** A rodada 1 (cega) usou a versão 1; depois do envio achou-se resíduo de
  anonimização nela (marca própria em forma curta, nome em maiúsculas depois de saudação, nome de pessoa no
  nome exibido — 63 registros). A versão 2 corrige isso com os MESMOS IDs, conjuntos, classes e sinais. **Toda
  chamada nova usa só a v2**; a v1 continua fora do Git e só serve para reproduzir a rodada 1 a partir do cache
  antigo. O `run.py` ainda aplica uma máscara de última milha (nome em maiúsculas após saudação → `[NOME]`) e o
  relatório diz quantas trocas ela fez: na v2, zero.
- **Gabarito = a decisão do sistema em produção** (`decidido_por`: `rule`, `ai_claude`, `ai_codex`, `ai_api`,
  `crm`). Toda taxa aqui é **concordância com produção**, não acerto contra verdade independente. "Escalar" é
  mandar ao LLM que já classifica hoje; como o gabarito é a decisão dele, o escalado concorda por definição —
  o que se mede é quanto o Jev decide sozinho e quanto disso concorda.
- Três recortes em toda tabela: `todos`, `só regra` (produção decidiu por regra) e **`só IA`** (produção mandou a
  um LLM: o resíduo ambíguo, que é o caso de uso real do roteador e o recorte do critério).

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| DKIM/SPF/DMARC, alinhamento, cabeçalho de lista, anexos, links fora do domínio | **código** (extração) | são cabeçalhos; entram no state como fato pronto em `signals` |
| Qual das 6 classes? | Jev, Choice `class` (opções com `what`/`not_for`/`examples`) | espaço fechado; a confiança diz se ele decide |
| Pede dinheiro ou credencial? Usa nome conhecido com sinal de que não é ele? Empurra a agir com pretexto? É e-mail de administração de imóvel? Uma pessoa escreveu para este destinatário? É aviso transacional? É oferta em massa? | Jev, 7 Nouls atômicos na mesma requisição | segunda leitura das fronteiras caras: um Noul que contradiz a classe faz escalar |
| Corpo com menos de 80 caracteres não decide classe de caixa de entrada; corpo acima do teto ou e-mail vazio não vai ao Jev | **código** | contagem; com corpo vazio o Jev julgaria só pelo assunto |
| Limiar por classe, conflitos, validar a resposta, falha operacional → `escala` | **código** (`roteador.py`, números em `perguntas.py`) | política por risco; falha nunca decide classe |
| O que o Jev não decide | **LLM** de produção | raciocínio, conhecimento de remetente, casos ambíguos |

## Desenho
State `{"sender_name", "subject", "body", "signals"}`. Uma requisição com 8 perguntas em inglês
([`perguntas.py`](perguntas.py)); decisão em [`roteador.py`](roteador.py):

1. Corpo vazio (mesmo com assunto), ou corpo acima de 4.500 caracteres → `escala`, sem chamada.
2. Confiança da Choice abaixo do limiar da classe → `escala`. Limiares: `principal`, `notificacoes`, `promocoes`,
   `redes_sociais` 0,7; `golpe` 0,8; `spam` 0,9.
3. Classe de caixa de entrada (`principal`, `notificacoes`) com corpo menor que 80 caracteres → `escala`.
4. Corpo truncado na extração (`body_truncated`, 4.000 caracteres) com classe cara (`principal`, `notificacoes`,
   `spam`, `golpe`) → `escala` — regra de código posta DEPOIS da rodada 1 (ver Pós-revisão); só `promocoes` e
   `redes_sociais` se decidem com corpo truncado.
5. Noul em conflito com a classe → `escala` (ex.: `promocoes` com `impersonates_known_sender` ≥ 0,8; `golpe` ou
   `spam` com `property_admin_mail` > 0,2 ou `human_wrote_to_this_recipient` ≥ 0,8).
6. Sobrou: `decide`.

Erros caros, contados à parte: **golpe na caixa** (golpe de produção decidido sozinho como `principal` ou
`notificacoes`) e **cliente perdido** (`principal` de produção decidido sozinho como `spam` ou `golpe`).
Falha operacional (timeout, cache faltando, resposta fora do contrato, registro inválido) sai `escala` para
aquele e-mail por `roteador.rotear_seguro`; resposta com JSON válido mas fora do contrato também sai do cache
(`invalidar`), para ser refeita na próxima rodada. [`testa_falhas.py`](testa_falhas.py) prova isso sem rede e sem
dado real (28 falhas, grade de 157.464 combinações da política, carga, código e relatório com registros inventados).

Afinação, só nos 152 do ajuste, duas passadas. A primeira (Choice + os 5 Nouls do briefing) mostrou três
defeitos de desenho: a descrição tratava DKIM alinhado como prova do remetente (fraude assinada pelo próprio
domínio saía `notificacoes`; boleto de administradora sem DKIM alinhado saía `golpe`), o Noul de falsificação
disparava só com DKIM não alinhado, e nada dizia que e-mail de administradora de condomínio é trabalho desta
caixa. A segunda corrigiu os três e somou dois Nouls. Leitura forçada no ajuste: 0,750 → 0,822.

## Baseline (código, sem Jev)
Regras simples sobre os sinais + palavras-chave, na ordem: sem DKIM alinhado + pedido de dinheiro ou dado + link
externo → `golpe`; RE/RES/FW/ENC → `principal`; DKIM alinhado + palavra de condomínio → `principal`; cabeçalho de
descadastro ou envio em massa → `promocoes` (ou `notificacoes`, com palavra transacional); automático, ou DKIM
alinhado + palavra transacional → `notificacoes`; nenhuma regra → escala. É o roteiro de uma tarde, não o motor de regras de produção.

## Critério de continuar/descartar (fixado ANTES de ler o teste; está no manifesto)
No teste, recorte `só IA`: (1) golpe na caixa ≤ 1% dos golpes; (2) cliente perdido ≤ 1% dos principais;
(3) concordância entre os decididos ≥ 0,95; (4) cobertura ≥ 40% (o briefing sugeria 50% como exemplo; o ajuste
dava 48%); (5) o baseline não chega lá (falha em 1–3 ou cobre menos). O veredito é calculado pelo `run.py`.

## Resultados — rodada 1 (`jev-1.13.0`, 2026-10-01, cega, dado v1; concordância com produção)
Manifesto gravado em 2026-10-01 14:56:49 (hoje em `congelamentos-anteriores/`); teste rodado uma vez depois.
`redes_sociais` (6 casos) fica à parte. Esta seção é a rodada cega e não foi reescrita; a rodada 2 vem depois.

| teste | n | decide sozinho | concordância entre decididos | golpe na caixa | cliente perdido | ponta a ponta (escalado = 1) |
|---|---|---|---|---|---|---|
| **só IA — Jev roteador** | 242 | **46,3%** [35,4; 57,9] | **0,973** (109/112) [0,937; 1,000] | **0/72** | **1/68** (1,5%) [0; 5,6%] | 0,988 |
| só IA — Jev forçado (sem limiar) | 242 | 100% | 0,690 | 13/72 | 6/68 | 0,690 |
| só IA — baseline | 242 | 66,5% | 0,435 | 12/72 | 10/68 | 0,624 |
| só regra — Jev roteador | 329 | 24,0% [14,1; 34,8] | 0,975 [0,919; 1,000] | 0/75 | 1/147 | 0,994 |
| só regra — baseline | 329 | 66,9% | 0,682 | 1/75 | 2/147 | 0,787 |
| todos — Jev roteador | 580 | 34,0% [26,0; 42,6] | 0,975 [0,948; 0,995] | 0/147 | 2/223 (0,9%) | 0,991 |
| todos — baseline | 580 | 67,2% | 0,579 | 13/147 | 15/223 | 0,717 |

IC 95% por bootstrap agrupado por remetente. No ajuste (limiares escolhidos nele, número otimista): só IA 47,8%
de cobertura, 44/44 concordando.

**Critério no teste: NÃO PASSOU — 4 de 5.** (1) 0/72 ✓ · (2) **1/68 = 1,5% ✗** (limite 1%) · (3) 0,973 ✓ ·
(4) 46,3% ✓ (a linha informativa dos 50% não foi atingida) · (5) o baseline falha em 1, 2 e 3 ✓.

**Curva do teste, recorte `só IA`** (o mesmo limiar em todas as classes, com a política; informativa):

| limiar | cobertura | concordância entre decididos | golpe na caixa | cliente perdido |
|---|---|---|---|---|
| 0,5 | 70,2% | 0,794 | 4/72 | 2/68 |
| 0,6 | 62,0% | 0,860 | 2/72 | 1/68 |
| 0,7 | 50,0% | 0,975 | 0/72 | 1/68 |
| 0,8 | 39,3% | 0,989 | 0/72 | 1/68 |
| 0,9 | 31,0% | 1,000 | 0/72 | 0/68 |
| 0,95 | 22,7% | 1,000 | 0/72 | 0/68 |

Por classe, no recorte `só IA` (Jev decidiu sozinho → produção concorda): `principal` 34 → 34 · `notificacoes`
8 → 6 · `promocoes` 28 → 28 · `spam` 3 → 3 · `golpe` 39 → 38. `redes_sociais` (à parte, todos por regra): 5 de 6
decididos sozinho e concordando; 1 escalado.

### Erros por categoria (5 decididos sozinho que discordam, nos 580; IDs no relatório)
- **Cliente perdido, 2** (`principal` → `golpe`): um aviso de cobrança por pix de um fornecedor contratado, com
  corpo quase só de folha de estilo, lido como golpe a 0,81 (recorte IA); um código de recuperação de conta de
  rede social, que a produção manda à caixa principal por regra, lido como golpe a 0,92 (recorte regra).
- **`principal` → `notificacoes`, 2** (IA): aviso automático de serviço contratado (confirmação de pedido,
  lembrete de fatura) que a produção trata como trabalho. Os dois destinos ficam na caixa de entrada: barato.
- **`spam` → `promocoes`, 1** (regra): divulgação de curso em massa. Barato.

### Custo
Jev medido: 3.025 tokens e US$ 0,127 por mil e-mails; p50 269 ms, p95 320 ms (4 em paralelo). LLM **estimado**
(premissas de preço de `../roteador-jev-llm/run.py`; 1.500 tokens de instruções + texto → 150 de saída), recorte
`só IA`, por mil e-mails:

| LLM que recebe o resíduo | tudo no LLM | roteado (Jev em todos + LLM nos 53,7% escalados) | economia |
|---|---|---|---|
| barato (`gpt-6-luna`) | US$ 0,257 | US$ 0,267 | **−3,9%** (fica mais caro) |
| raciocínio (`gpt-6-astra`) | US$ 25,68 | US$ 13,98 | 45,5% |

Construção inteira: 812 respostas gravadas (143 + 143 nas duas passadas de ajuste, 2 remascaradas, 524 de teste
com state distinto; cerca de 830 requisições contando duplicatas simultâneas e 2 de medição com state vazio),
2,38 milhões de tokens, US$ 0,10 (orçamento: 2.500 requisições).

## Lições
1. **Falhou por um caso, no lado caro, e a confiança não o separa.** Com 68 principais no recorte, 1% é
   tolerância zero. O limiar de `golpe` (0,8) saiu do vão do ajuste (0,59–0,79); o teste trouxe leituras `golpe`
   discordantes a 0,81 e 0,92. Só em 0,9 o recorte IA zera (cobertura 31%), e em `todos` só em 0,95 (14%).
   Cobrança e aviso de segurança legítimos se parecem com fraude quando o domínio do remetente não está no dado.
2. **Golpe na caixa: zero em 147.** A leitura forçada poria 13 dos 72 golpes do recorte IA na caixa de entrada;
   o limiar 0,7 das classes de caixa segurou todos (a 0,6 passariam 2).
3. **Quem trabalhou foi a confiança da Choice; os 7 Nouls não se pagaram.** No teste as travas de Noul barraram
   1 erro barato e custaram 1 concordante; a regra do corpo curto barrou 1 e custou 2; nenhuma barrou erro caro.
   Só confiança: 47,5% e 0,957; com as travas: 46,3% e 0,973. Os 7 Nouls custam 997 tokens por requisição
   (medido com state vazio), um terço dela. Nenhuma trava cobria "aviso transacional legítimo lido como golpe":
   é a que faltou.
4. **`spam` de produção não é classe de conteúdo.** Leitura forçada concorda em 5 de 72; 65 saem `promocoes`.
   A produção separa spam de promoção por histórico do remetente (famílias de regra), sinal que o texto não tem.
   O Jev decidiu `spam` sozinho 3 vezes.
5. **O Jev não substitui a camada de regra.** No recorte `só regra` ele decide 24% (leitura forçada 0,644): as
   regras de produção carregam conhecimento de remetente. O lugar dele é depois da regra.
6. **Economia depende de qual LLM recebe o resíduo, e a pergunta longa custa em toda requisição.** Dos 3.025
   tokens por e-mail, 2.639 são as perguntas (medido com state vazio; só a Choice com `what`/`not_for`/`examples`:
   1.642) — o e-mail em si pesa menos de 400. Contra um LLM barato o degrau não paga em dólar, só em latência;
   contra um LLM de raciocínio corta 45%.
7. **A regra de código escrita em uma tarde é pior que não rotear**: decide 2/3 e concorda em 43,5% no recorte
   IA, com 12 golpes na caixa e 10 clientes perdidos.
8. **O ajuste achou os defeitos de desenho antes do teste** (DKIM lido como prova), e o encolhimento foi pequeno:
   47,8% → 46,3% de cobertura, 1,000 → 0,973 de concordância.

Hipótese para a próxima rodada (conta feita depois, no mesmo teste — **não é medição cega**): se `golpe` e `spam`
sempre escalassem, o recorte IA teria 70 decididos (28,9%), 68 concordando (0,971) e nenhum erro caro. Precisa de
dado novo, de preferência com o domínio real do remetente no state. (Não foi aplicada na rodada 2: a rodada 2
só aplica a lista da revisão, não afina política.)

## Pós-revisão do Codex (2026-10-01) — rodada 2, não cega
A revisão adversarial (6 achados, todos aceitos) e três achados do construtor foram aplicados DEPOIS de o teste
ter sido lido. A rodada 2 é portanto **não cega**: nada de pergunta, limiar ou política foi afinado olhando o
teste — só a lista abaixo —, mas o teste já era conhecido, e o critério de aceite não mudou. Manifesto novo
gravado em 2026-10-01 15:36:21 (o das 15:31:05, gravado antes do conserto da trava por pedido, também está em
`congelamentos-anteriores/`). O que era → o que mudou:

1. **Privacidade (gravidade 1).** A tabela de erros exportava a coluna `regra` (nome interno da regra de produção)
   por mensagem. Saiu da saída do `run.py`; `resultados-rodada1.md` recebeu **essa única edição posterior**
   (remoção da coluna nas 7 linhas da tabela; o original ficou fora do Git, em
   `.local/dados-reais/email/relatorios-originais/`). Varredura da família: por mensagem só saem `id`, `classe`,
   `decidido_por`, números do Jev (confiança, Nouls), sinais calculados em código (`dkim_aligned`,
   `list_unsubscribe`) e o tamanho do corpo em caracteres — `confianca`, `pasta_chegada`, `retro`, `crm_client`,
   `grupo` e qualquer texto nunca entram. A bateria confere que um nome de regra inventado não aparece no relatório.
2. **Entrada inválida abortava o lote (gravidade 2).** A máscara rodava antes da validação (`texto` não-texto dava
   erro fora de `rotear_seguro`) e metadado ausente quebrava as métricas. Agora a carga valida cada registro
   ANTES da máscara: texto ou sinal inválido vira `escala` por falha operacional daquele registro, contado à parte;
   `id`, `grupo`, `conjunto`, `classe` ou `decidido_por` ausente ou inválido PARA o script com mensagem clara (sem
   gabarito não há veredito). Na v2: 0 registros inválidos.
3. **Corpo vazio decidia classe cara (gravidade 2).** `fora_da_faixa` só parava sem assunto E sem corpo. Agora
   corpo vazio escala antes da chamada, sempre: 3 e-mails do teste (`notificacoes`; 2 por regra, 1 por IA) deixaram
   de ir ao Jev. `body_truncated` ganhou tratamento explícito, conservador e **posto depois do teste**: leitura
   com corpo truncado não decide sozinha classe cara (`principal`, `notificacoes`, `spam`, `golpe`); o sinal não
   entra no state. Medido no teste: 63 e-mails com resposta e corpo truncado, **22 barrados pela regra, os 22
   concordavam com produção, 0 discordavam** (10 dos 22 no recorte `só IA`). No ajuste: 6 barrados, 6 concordantes.
4. **Resposta inválida presa no cache (gravidade 2).** `rotear_seguro` agora chama `jev.invalidar` quando a
   validação do contrato rejeita uma resposta que veio como JSON válido; a falha continua saindo como `escala` e
   contada. Bateria com dublê: contrato rejeitado invalida exatamente o pedido feito; falha de chamada e registro
   inválido não invalidam; quarentena falhando não tira o e-mail da escalada. Na rodada 2 nenhuma resposta foi
   rejeitada (a validação da infra comum passou a recusar Choice cuja opção escolhida não é a de maior
   probabilidade, folga 0,025; o exemplo continua rodando com isso).
5. **Dado v2.** `DADOS_REL` aponta para `emails-anon-v2.jsonl`; a máscara de última milha fica como defesa em
   profundidade e o relatório conta as trocas: **0 na v2** (na v1: 2 registros no ajuste, 16 no teste).
6. **Exemplo de pergunta igual a assunto real.** Um exemplo de `notificacoes` coincidia com o assunto-padrão de uma
   plataforma presente nos dados (EM-0439); na conferência, dois outros exemplos (`principal`, `spam`) dividiam uma
   sequência de quatro palavras com algum e-mail. Os três foram trocados por frases inventadas; conferido contra
   assunto e corpo da v2: nenhum exemplo coincide, nem por sequência de 4 palavras. Como as perguntas mudaram, o
   cache da rodada 1 não serviu: a rodada 2 refez todas as chamadas, sobre a v2.
7. **States repetidos.** A divisão congelada não muda. O teste tem 526 states distintos em 586 e-mails (580 → 520
   sem `redes_sociais`); 3 states também aparecem no ajuste (todos no recorte `só regra`; no `só IA`, nenhum). O
   relatório traz as métricas da política por três denominadores: `por e-mail` (cada registro conta 1; é o das
   tabelas principais e do critério), `state único` (cada state distinto conta 1, fica o primeiro registro) e `sem
   states do ajuste` (state único, tirando os que também estão no ajuste). Mesmas respostas, nenhuma chamada nova.

Fora da lista, achado ao conferir a infra comum: a trava por pedido do `jevcache` é por instância, e o `run.py`
dá uma instância a cada linha paralela. Dois e-mails de state idêntico em linhas diferentes ainda chamavam a API
duas vezes (15 vezes na rodada 2) e um deles consumia uma resposta diferente da gravada: a primeira passada ao
vivo da rodada 2 diferia do replay `gravado` em 3 e-mails do recorte `só regra`. O `run.py` passou a fazer as
instâncias dividirem a mesma tabela de travas (sem editar a infra comum), o manifesto foi gravado de novo e o
`resultados.md` publicado é o replay do cache, idêntico em `auto` e em `gravado`. A rodada 1 tinha o mesmo
defeito (relatório = o que a passada ao vivo consumiu); seus números não foram refeitos.

### Rodada 1 × rodada 2 no teste (política do Jev; concordância com produção; IC 95% bootstrap por remetente)
| recorte | rodada | n | decide sozinho | concordância entre decididos | golpe na caixa | cliente perdido | ponta a ponta |
|---|---|---|---|---|---|---|---|
| **só IA** | 1 (cega, v1) | 242 | 46,3% [35,4; 57,9] | 0,973 (109/112) [0,937; 1,000] | 0/72 | 1/68 (1,5%) | 0,988 |
| **só IA** | 2 (v2) | 242 | **43,0%** [32,6; 54,9] | **0,971** (101/104) [0,932; 1,000] | 0/72 | **1/68 (1,5%)** [0; 5,6%] | 0,988 |
| só regra | 1 | 329 | 24,0% [14,1; 34,8] | 0,975 [0,919; 1,000] | 0/75 | 1/147 | 0,994 |
| só regra | 2 | 329 | 21,0% [11,7; 31,5] | 0,986 (68/69) [0,942; 1,000] | 0/75 | 1/147 | 0,997 |
| todos | 1 | 580 | 34,0% [26,0; 42,6] | 0,975 [0,948; 0,995] | 0/147 | 2/223 (0,9%) | 0,991 |
| todos | 2 | 580 | 30,3% [23,4; 38,4] | 0,977 (172/176) [0,952; 0,995] | 0/147 | 2/223 (0,9%) | 0,993 |

Leitura forçada no `só IA`: 0,690 → 0,693 (golpe na caixa 13/72 → 12/72; cliente perdido 6/68 → 9/68). Baseline:
idêntico (mesmo código, mesmos sinais). Ajuste (número otimista nas duas): `só IA` 47,8% e 44/44 → 40,2% e 37/37;
forçada 0,772 → 0,793. Por state único no teste, `só IA`: 228 states, 43,4% (99/228), 97/99 = 0,980, 0/65, 1/67;
`todos`: 520 states, 29,0%, 0,980, 0/137, 2/216; sem os states do ajuste: 517, 29,2%, 0,980, 0/134, 2/216.

**Critério, teste, recorte `só IA`:** rodada 1 **NÃO PASSOU (4 de 5)** — (2) 1/68 = 1,5% ✗. Rodada 2 **NÃO PASSOU
(4 de 5)** — (1) 0/72 ✓ · (2) **1/68 = 1,5% ✗** (o mesmo EM-0207, `principal` lido como `golpe` a 0,82; na rodada
1, 0,81) · (3) 0,971 ✓ · (4) 43,0% ✓ (a linha informativa dos 50% continua não atingida) · (5) baseline falha em 1,
2 e 3 ✓. O desenho não foi reabilitado pela revisão: o caso que derruba o critério é o mesmo.

**O que piorou:** cobertura no `só IA` 46,3% → 43,0% (−3,3 pontos), no `só regra` 24,0% → 21,0%, em `todos`
34,0% → 30,3%. A causa principal é a regra do corpo truncado (item 3): barrou 22 decisões no teste (10 no `só IA`),
todas concordantes — sem ela a rodada 2 daria 114/242 = 47,1% e 111/114 = 0,974 no `só IA`. A regra é conservadora
por desenho e não evitou erro nenhum neste teste; fica declarada como custo, não como ganho. Concordância entre
decididos 0,973 → 0,971 (um erro a menos, `spam → promocoes`, e oito decisões a menos). Economia estimada contra o
LLM de raciocínio 45,5% → 41,4%; contra o barato −3,9% → −8,2% (mais escalados). Os dois erros caros de `todos` são
os mesmos IDs (EM-0207, EM-0728); `principal → notificacoes` também os mesmos (EM-0624, EM-0701).
**O que melhorou:** `só regra` 0,975 → 0,986 e ponta a ponta 0,994 → 0,997; `todos` 0,975 → 0,977; o erro
`spam → promocoes` da rodada 1 (EM-0675) sumiu; as travas de Noul barraram 3 erros (1 na rodada 1), nenhum caro.

**Chamadas da rodada 2:** 679 requisições novas medidas (143 no ajuste ao congelar + 536 no teste; 664 respostas
distintas gravadas — as 15 a mais são a corrida entre instâncias descrita acima), todas sobre a v2, 4 em paralelo,
p50 274 ms, p95 323 ms; 2,23 milhões de tokens (0,45 M ajuste + 1,78 M teste; 2.978 e 3.045 tokens por e-mail);
**US$ 0,094** (orçamento desta rodada: 900 requisições). Acumulado do exemplo: cerca de 1.510 requisições e US$ 0,19.
Zero falhas operacionais, zero respostas rejeitadas, zero registros inválidos.

## Limites
- **Gabarito = produção**: mede concordância. Um par de e-mails com state idêntico tem classes de produção
  diferentes (ruído do gabarito).
- Uma versão do modelo, uma rodada. Valores perto do limiar trocam de lado entre chamadas idênticas (p95 ~0,05).
- **A anonimização remove endereço, domínio e nomes**: o sinal mais forte contra fraude (o domínio bate com a
  marca?) não está no state. Em produção o state teria o domínio; os números mudariam, não se sabe quanto.
- Corpo cortado em 4.000 caracteres na extração: `body_truncated` em 87 dos 738 (12%; o briefing estimava 26%).
- **Campanhas repetidas**: o teste tem 526 states distintos em 586 (v2), e 3 states aparecem no ajuste e no teste
  (a mesma campanha saindo de domínios diferentes). A divisão por domínio não separa campanhas, e o bootstrap por
  remetente não modela essa dependência. O relatório da rodada 2 dá as métricas por `state único` e `sem states do
  ajuste` ao lado de `por e-mail`; o critério usa `por e-mail`.
- Mistura de classes diferente entre ajuste e teste no recorte IA (12 principais de 92 × 68 de 242).
- `redes_sociais`: 6 casos, todos decididos por regra em produção, nenhum no ajuste.
- Custo do LLM é estimativa; em produção o resíduo passa antes por assinaturas (Claude, Codex), não por tarifa.
- Na rodada 1, um dos 18 exemplos escritos à mão em `perguntas.py` coincidia com o assunto-padrão de uma
  plataforma presente nos dados (frase genérica, sem dado pessoal); trocado na rodada 2, com rodada nova.
- Máscara de última milha no `run.py`: nome em maiúsculas depois de saudação vira `[NOME]` antes do envio (v1: 2
  registros no ajuste, 16 no teste; v2: 0). Não substitui o anonimizador.
- A rodada 2 não é cega; o critério continua o mesmo e o resultado é o mesmo (4 de 5), mas a leitura "o desenho
  falha pelo mesmo caso" veio depois de ver o teste.

## Como rodar
Só na pasta de estudo (os dados e o cache não vão para o Git). Python do `.venv`, `PYTHONIOENCODING=utf-8`:
```
..\..\.venv\Scripts\python.exe testa_falhas.py   # bateria do código, sem dados reais nem rede
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação (lê só os registros de ajuste)
..\..\.venv\Scripts\python.exe run.py congelar   # manifesto: perguntas.py, roteador.py, run.py, dados (v2), critério
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste; recusa se algo congelado mudou
```
`JEV_MODO=gravado` reproduz a rodada 2 do cache, sem chave (a rodada 1 só se reproduz do cache antigo com a v1 e o
código da época). Sem a pasta de dados o script sai com "dados privados ausentes". Registro sem metadado
indispensável para o script com mensagem clara.

## Arquivos
`perguntas.py` (perguntas, limiares, conflitos, critério) · `roteador.py` (state, validação, política, baseline,
`rotear_seguro`) · `run.py` (carga por conjunto, métricas, bootstrap, relatório sem texto) · `testa_falhas.py` ·
`congelamento.json` (rodada 2; os anteriores em `congelamentos-anteriores/`) · `resultados.md` (rodada 2) e
`resultados-rodada1.md` (rodada cega, com a única edição posterior descrita acima). Sem `cache/` e sem `dados/`.
Receitas-irmãs: [classificação com confiança](../../conhecimento/receitas/classificacao-com-confianca.md) ·
[roteamento por confiança](../../conhecimento/construir/padroes/roteamento-por-confianca.md) ·
caso externo de roteador de e-mail com escalada em [casos externos](../../conhecimento/evidencias/casos-externos.md).
