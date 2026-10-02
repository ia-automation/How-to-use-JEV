# Juiz de eval (rubrica sobre respostas de atendimento, pt-BR)

## Problema
Avaliar respostas de LLM por rubrica ("informa que a visita precisa de agendamento?", "não promete
desconto?", "tem no máximo 3 frases?") custa um LLM de fronteira por resposta. Caso externo de
referência (não reproduzido aqui): 6.003 checagens de rubrica, Jev concordou com Fable 5.1 em 91,5% a
US$ 160 por milhão de vereditos contra US$ 33.000 ([casos-externos](../../conhecimento/evidencias/casos-externos.md), seção 1).
Aqui o ponto é a **divisão de trabalho**: o Jev julga só o que é julgamento; o resto é regra de código.

## Quem faz o quê
| Parte | Onde | Por quê |
|---|---|---|
| critérios **formais** (contar frases, `R$`, horário, link, palavra, emoji, tamanho, termina com `?`) | código (`juiz.py`: gramática das 8 regras do [LEIA-ME](dados/LEIA-ME.md), com polaridade "Não …", singular/plural e número por extenso; texto fora da gramática é erro, nunca veredito) | exato; o Jev não conta nem compara (limite #2) — e erraria "4 frases curtíssimas" |
| critérios **semânticos** ("informa que…", "não promete…", "tom cordial") | Jev, 1 Noul por critério | julgamento sobre texto livre, espaço fechado (atende / não) |
| "não inventa…" **sem** `Contexto:` na pergunta | código → `revisa`, sem chamada | o state não tem com que comparar; não se pergunta o que ele não diz |
| veredito por critério (3 faixas) e da resposta (todos atendem?) | código (`FAIXA` em `perguntas.py`) | política por risco: aprovar resposta ruim é o erro caro |
| LLM juiz de comparação | **não roda aqui** | aceito por desenho (BRIEFING): a referência de custo é o caso externo |

## Desenho (`perguntas.py` = pergunta, faixa, baseline, critério de continuar; `juiz.py` = regras e composição)
- **State** (desenho `agrupado`, o padrão): `{"question", "answer", "criteria": [c1, c2, …]}` — só os
  critérios semânticos julgáveis; 1 requisição por resposta, um Noul por critério apontando `` `criteria[i]` ``.
  Alternativa medida: `um_por_requisicao` (`{"question", "answer", "criterion"}`, 1 requisição por critério).
- **Pergunta** (uma só, inglês): "Does `answer` satisfy the criterion written in `criteria[i]`, taken as
  written?" · `true` = atende explícito, em outras palavras ou implicação plana ("regulamento não permite
  animais"); critério "Não …" = a coisa proibida está ausente · `false` = não menciona, contradiz, vago,
  repete/responde outra pergunta, só por inferência do leitor; "Não …" com a coisa presente mesmo
  suavizada; "Não inventa" com fato que o `Contexto:` não sustenta. As regras são as do LEIA-ME (escritas
  antes dos casos), não casos do ajuste.
- **Faixa** `(0,3, 0,8)`: noul ≤ 0,3 → `nao_atende`; ≥ 0,8 → `atende`; meio → `revisa`. Assimétrica
  porque aprovar exige mais certeza que reprovar. Resposta: `aprovada` (todos atendem) · `reprovada`
  (algum não atende) · `revisa` · `erro` (critério formal fora da gramática ou resposta do Jev inválida —
  ID faltando, bool, string, NaN ou valor fora de [0,1] é exceção, nunca "não atende"; validação em
  `_comum/congelamento.py`).
- **Baseline** (só semânticos): palavras-chave do critério presentes na resposta (sem stopwords e verbos
  de rubrica, prefixo de 5 letras, ≥ metade); critério negado inverte.
- **Critério de continuar/descartar**, fixado antes do teste: formais 100% · acerto semântico duro ≥
  baseline + 15 p.p. · erro caro (gabarito `false` → `atende`) ≤ 5% dos `false` · nenhuma resposta ruim
  aprovada inteira. É um dicionário em `perguntas.py` e congela junto com o código no manifesto
  `congelamento.json` (hash de `perguntas.py`, `juiz.py`, `dados/teste.json` + o critério); `run.py teste`
  recusa sem manifesto ou com arquivo mudado; congelar de novo guarda o anterior em `congelamentos-anteriores/`.

## Resultados (jev-1.13.0, 2026-10-01; tudo em `resultados.md`, gerado pelo script)
Ajuste = 30 respostas / 77 critérios (afinado nele); teste = 57 respostas / 139 critérios (104 semânticos,
99 com gabarito, 35 formais; 70% difíceis). Desenho padrão `agrupado`.

### Rodada 1 (cega, congelada em 2026-10-01 11:24 — hashes `perguntas.py` `4d8e9d37…`, `juiz.py` `0084a770…`, `dados/teste.json` `4bd70634…`)
Teste aberto e rodado UMA vez; os números abaixo são os dessa rodada, inalterados.

| Teste (n) | Jev `agrupado` | Jev `um_por_requisicao` | baseline de código |
|---|---|---|---|
| semântico, acerto duro (noul ≥ 0,5; 99) | **0,970** (96/99) | 0,970 | 0,596 |
| com faixa: cobertura · erro entre decididos · revisões | 93,9% · **0** (0/93) · 6 | 93,9% · 1,1% (1/93) · 6 | — |
| erro caro: gabarito `false` → `atende` (34) | **0/34** (sem faixa: 1/34) | 0/34 (0/34) | 14/34 |
| gabarito nulo em revisão (5) | 4/5 | 4/5 | — |
| Brier | 0,020 | 0,025 | — |
| formais (35) | **34/35** — 1 bug de regex (abaixo) | idem | idem (é o mesmo código) |
| resposta inteira: ruim aprovada (33) · boa reprovada (22) · acerto | 0/33 · 0/22 · 0,945 | 0/33 · 0/22 · 0,964 | — |
| requisições por resposta · tokens · p50 · p95 | 1 · 879 · 258 ms · 320 ms | 1,75 · 1.118 · 250 ms · 314 ms | 0 |
| US$ por resposta · por milhão de respostas · por milhão de vereditos semânticos | 0,000037 · **36,93** · **20,24** | 0,000047 · 46,95 · 25,73 | 0 |

Ajuste: 54/55 duro nos dois desenhos, 0 erro com faixa, 3 revisões, formais 19/19, baseline 0,582.

**Critério de continuar (rodada 1):** (2) 0,970 ≥ 0,746 ✓ · (3) 0/34 ✓ · (4) 0/33 ✓ · **(1) formais 34/35 ✗** —
falhou por um bug de código (regra "Tem no máximo 1 **frase**", singular; a regex só casava "frases"). O
resultado da rodada cega fica como rodou.

### Rodada 2 (pós-revisão; o teste já tinha sido visto, portanto NÃO é cego)
Correções da revisão adversarial (Codex, 2026-10-01), todas de código e relatório — a pergunta ao Jev não
mudou, então o cache reproduz as mesmas respostas gravadas sem chamada nova (`JEV_MODO=gravado`). Manifesto novo
`congelamento.json` (gravado em 2026-10-01 11:47; o congelamento da rodada 1 era a linha de hashes acima,
não um manifesto — por isso `congelamentos-anteriores/` está vazia). O que mudou, item a item:

| Número | Rodada 1 | Rodada 2 | Por quê |
|---|---|---|---|
| formais (35) | 34/35 | **35/35** | gramática completa reconhece "1 frase" (singular); T051/c2 deixa de ser `erro` |
| resposta inteira, acerto (`agrupado` / `um_por_requisicao`) | 0,945 / 0,964 | 0,964 / 0,982 | T051 sai de `erro` para `aprovada` (gabarito aprovada) |
| semântico: acerto duro, cobertura, erro caro, Brier, revisões | 0,970 · 93,9% · 0/34 · 0,020 · 6 | **iguais** | nenhuma resposta do Jev mudou |
| ruim aprovada · boa reprovada | 0/33 · 0/22 | iguais | idem |
| custo, latência | iguais | iguais | mesmas medições do cache |

Outras correções sem efeito nos números deste conjunto: URL no fim de frase não engole mais o ponto
("Veja https://x.com. Ligue." = 2 frases; nenhum caso do teste tinha URL seguida de pontuação);
polaridade ("Não contém um link" já não casa com "contém um link"; nenhum caso usava); bool/string como
probabilidade agora é erro (nenhuma resposta gravada tinha); `run.py rascunho` escreve
`resultados-rascunho.md` e não toca em `resultados.md` nem no manifesto. Na rodada 2 o critério (1) passa,
mas isso não vale como aprovação cega: a rodada que conta como teste é a 1.

**Custo × caso externo:** US$ 20 por milhão de vereditos semânticos aqui × US$ 160 lá — states diferentes
(respostas de 1–8 frases com rubrica curta × respostas financeiras), então não é a mesma conta; a ordem de
grandeza contra o LLM de fronteira (US$ 33.000 por milhão no relato) é a mesma. O LLM juiz não foi
medido aqui.

## O que deu certo
- **A divisão**: os 34 formais que a regex cobria saíram 100% (18 contagens de frase, incluindo "4 frases
  curtíssimas" e ponto de milhar), a custo zero — nada disso passou pelo Jev.
- **Critério negado** ("não promete desconto", "não garante", "não culpa") 9/10 duro no teste (o 10º é
  T050, 0,52, que foi para revisão); o baseline de palavra-chave acerta 0,30 nessa família (a palavra
  "desconto" aparece justamente quando se nega).
- **Erro caro zero com faixa**: o único `false` com noul ≥ 0,5 (T050, 0,52) caiu na revisão; o baseline aprova
  14 de 34 critérios não atendidos.
- **Nulo por código**: os 4 "não inventa" sem `Contexto:` (4 dos 5 gabaritos nulos) foram para revisão
  sem gastar chamada; o 5º nulo tinha contexto e é o caso 6 abaixo.
- **Agrupar não custou acerto agregado nesta rodada**: mesmo 96/99 do desenho de 1 requisição por
  critério, 24% mais barato, Brier menor (0,020 × 0,025). Critério a critério os desenhos divergem mais do
  que a variação entre chamadas repetidas (máx. 0,15 medido): T036/c2 0,81 × 0,38 (Δ 0,43, `atende` ×
  `revisa`), T022/c2 0,10 × 0,47, T016/c1 0,94 × 0,61, T043/c3 0,54 × 0,81. Uma rodada não separa efeito
  da indireção de `criteria[i]` (limite #4) de ruído — a conclusão é só sobre o agregado.
- **O difícil ficou difícil, não errado**: nos 71 critérios difíceis, 0,958 duro e as 6 revisões; nos 28
  fáceis, 1,000.

## O que falhou (visto no teste — NÃO corrigido, vira lição)
1. **T051 c2 "Tem no máximo 1 frase"** → regra desconhecida → resposta `erro`. Regex no plural. Bug de
   código puro, pego pelo teste porque a regra formal não tinha teste unitário próprio. Corrigido na
   rodada 2 (gramática completa), que por isso não é cega.
2. **T019 c2 "Não inventa valor que não esteja no contexto"** (0,41 → revisa; gabarito `true`). A resposta
   diz "está disponível" (fato fora da ficha) mas o VALOR é da ficha. Minha `false` alarga "valor" para
   "qualquer fato sobre o imóvel" — a instrução ficou mais larga que o critério (limite #1/#7, erro meu).
3. **T047 c2 "tom cordial"** (0,36 → revisa; `true`; no outro desenho 0,24 → `nao_atende`, o único erro
   decidido). "Gerador não tem, mas quedas são raras": seco e correto. O rotulador aceita "ausência de
   hostilidade"; o Jev lê seco como não cordial. Família `tom` é a pior (0,889) e a de baseline mais inútil (0,111).
4. **T050 c1 "Não garante autorização do proprietário"** (0,52 → revisa; `false`). "Pode, claro, é sua
   casa" garante sem citar proprietário nem autorização; leitura literal do critério hesitou. É o caso que
   a faixa existe para pegar — sem faixa seria o único erro caro.
5. **T056 c1 "pega sol da manhã"** (0,57 → revisa; `true`, "face leste"). Implícito por conhecimento de
   mundo, que o próprio rotulador marcou como limítrofe. Incerteza certa.
6. **T043 c2 "Não inventa valor de entrada"** (0,09 → `nao_atende`; gabarito **nulo**: "costuma ser 20%,
   varia pelo banco" é regra geral com ressalva). A instrução manda tratar palpite plausível como invenção e
   não distingue regra de mercado; reprovou o indecidível — lado seguro, mas reprova resposta que o humano
   talvez aprovasse. T043 c3 no `agrupado` deu 0,54 × 0,81 no outro desenho (Δ 0,27) — não é a maior
   divergência: T036/c2 chega a 0,81 × 0,38 (Δ 0,43, com mudança de decisão; ver "O que deu certo").
7. **T040 c2 "Não promete exceção"** (0,32 → revisa; `false`). "Dá um jeito, muita gente faz" insinua; o Jev
   pendeu para o lado certo mas dentro da faixa.

## Lições
1. **Regra formal precisa de teste unitário próprio** sobre as variações do texto do critério
   (singular/plural, com e sem parêntese). O conjunto de teste do Jev não é o lugar de descobrir isso.
2. **A instrução não pode ser mais larga que o critério**: "não inventa valor" ≠ "não inventa nada". O
   critério é o texto da rubrica; a `false` só deve dar exemplos, não redefinir o escopo.
3. **Faixa assimétrica paga no CRITÉRIO, não (aqui) na resposta**: os 3 erros duros do teste (0,41 ·
   0,36 · 0,52) ficaram todos entre 0,3 e 0,8; 0,5/0,5 daria 3 erros de critério, 1 deles caro (T050/c1
   aprovado), mas **0 resposta ruim aprovada**: T050/c2 (0,08) reprova a resposta de qualquer jeito — a
   composição por faixa está em `resultados.md` ("ruim_aprovada (resposta)"). No nível da resposta,
   0,5/0,5 acertaria 55/55 contra 53/55 de 0,3/0,8 (duas respostas em revisão: uma boa, uma ruim). A faixa vale pelo
   risco (um critério errado a mais e a resposta ruim passava), não por um ganho medido neste n. Como na
   triagem, o ajuste (tudo ~0 ou ~1) não calibrava a faixa; o teste calibrou.
4. **Agrupar critérios da mesma resposta** é o desenho mais barato com o mesmo acerto agregado nesta
   rodada: estado compartilhado, 1 requisição. As divergências por critério (até Δ 0,43) pedem rodadas
   repetidas antes de afirmar que a indireção não custa; uma requisição por critério continua a
   alternativa se o número de critérios crescer (limite #5).
5. **Nulo é do código quando a estrutura denuncia** (critério de invenção sem ficha). Nulo por
   nuance (regra de mercado com ressalva) o Jev não vê — e nem deveria: é decisão de rotulagem, não de modelo.
6. **"Tom"** é a família a decompor antes de confiar: "não hostil" e "demonstra cuidado" são duas
   condições; o rotulador aceita a primeira sozinha.

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só, mesmo fornecedor do rotulador e do LLM do
  caso externo comparado; mais limpos que respostas reais. n = 30/57 respostas, 55/99 critérios
  semânticos rotulados: 1 critério = 1 p.p. no teste.
- Uma versão (`jev-1.13.0`), uma rodada; chamadas repetidas variam ~0,01 (máx. 0,15): T050 (0,52) e
  T056 (0,57) podem trocar de lado na faixa.
- O LLM juiz não roda; a comparação de custo é com o relato externo, não medida.
- O baseline é fraco de propósito (20 minutos de código); um baseline com embeddings mudaria o degrau.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa sem congelamento.json ou com arquivo mudado)
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 respostas, só encanamento → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py congelar   # roda o ajuste e grava o manifesto antes de abrir o teste
set JEV_MODO=gravado                              # reproduz tudo do cache/, sem chave
```
