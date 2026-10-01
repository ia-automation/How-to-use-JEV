# Busca de imóveis em linguagem natural (TypeScript, SDK JS)

A pessoa escreve "apartamento em Cidade Aurora até 600 mil, 2 quartos, aceita pet e rua tranquila" e recebe os
150 anúncios fictícios ordenados. **Demonstração de mecanismo**, não desempenho em portal real. O catálogo é
controlado: cada anúncio tem 8 fatos ternários (afirma, nega ou omite), e cada estado é escrito com um de três
enunciados fixos. O gabarito foi **derivado desses fatos de autoria** pela escala congelada, sem anotação
humana sobre anúncios reais. Os números vêm de [`resultados.md`](resultados.md), que `src/run.ts` gera sozinho.

## Problema
- As restrições duras (preço, quartos, vagas, tipo, cidade, bairro) precisam de comparação exata.
- Os critérios subjetivos (pet, rua tranquila, home office, metrô a pé, sol da manhã, reformado, vista, jardim
  privativo) precisam de leitura.
- Pela escala congelada, "não informa pet" não é "aceita pet". Um critério negado zera a relevância, e um
  omitido rebaixa.
- O erro caro é o **anúncio relevante que o filtro descarta antes de qualquer leitura**. O ranking não
  devolve o que a recuperação perdeu.

## Quem faz o quê
| Parte | Quem | Por quê |
|---|---|---|
| O que a consulta pede: tipo, cidade, bairro, mínimo de quartos e vagas, teto e piso de preço | Jev, com uma **Choice sobre valores fechados** por campo | O texto é livre ("meio milhão", "590 mil", "dois quartos no mínimo"). Ler qual valor foi escrito é leitura; comparar é aritmética (limite #2) |
| Quais critérios subjetivos foram pedidos | Jev, com um Noul por critério | Negação e paráfrase ("não quero rua barulhenta", "tem de aceitar meu gato") |
| Filtro das restrições duras | código | Comparação exata e inclusiva sobre os campos estruturados |
| O que o anúncio diz de cada critério pedido | Jev, com uma **Choice ternária** (afirma, nega, omite) por critério, uma requisição por anúncio | O fato é ternário. Um Score misturaria "não informado" com "incerto" |
| Escala de relevância e ordenação | código (`busca.ts`) | É política: muda editando um número, sem chamar a API |

## Desenho
- **Leitura da consulta** (1 requisição, 15 perguntas, state `{buyer_request}`): 7 Choices duras e 8 Nouls
  "pede X?".
  - O preço é lido numa grade de 10 em 10 mil, de 200 mil a 1,5 milhão (131 opções).
  - Faixa de dúvida orientada para a recuperação (`P_ACEITA` = 0,15): todo valor com probabilidade ≥ 0,15
    entra no filtro. O teto vira o maior deles, o mínimo o menor, e "qualquer" desliga a restrição. Na
    dúvida, o filtro fica largo.
- **Recuperação:** o código filtra os 150 anúncios e **todos** os que passam vão ao Jev. Não há corte de top-K,
  logo não há segunda perda.
- **Leitura do anúncio** (1 requisição por anúncio, state `{listing_description}`, só os critérios pedidos,
  8 em paralelo): Choice ternária.
- **Escala em probabilidade** (critérios tratados como independentes):
  - P(0) = algum critério negado;
  - P(3) = todos afirmados;
  - P(1) = todos omitidos;
  - P(2) = o resto sem negação.
- **Ordenação** pelo ganho esperado Σ (2^rel − 1)·P(rel), o mesmo ganho do NDCG. É a ordem que maximiza o DCG
  esperado.
- **Linhas de base**, todas nas mesmas consultas:
  - `palavras`: BM25 no catálogo inteiro, sem Jev nem filtro;
  - `filtro_palavras`: o mesmo filtro com ranking BM25, o que isola o valor do Jev no anúncio;
  - `filtro_so`: o filtro na ordem do catálogo;
  - `teto`: os recuperados na ordem do gabarito.
- **Métricas:** NDCG@10 com o ideal tirado do **gabarito inteiro**, não da lista devolvida. Assim, o anúncio
  perdido na recuperação pesa.

## Resultados (`jev-1.13.0`, 2026-09-30)
Só o ajuste foi usado para afinar. O hash de `perguntas.ts` (`1705f8f2…`) e de `busca.ts` (`b25edfc7…`) foi
gravado antes de abrir o teste, que rodou uma vez.

| | ajuste (8 consultas) | teste (16 consultas) |
|---|---|---|
| NDCG@10: jev · filtro_palavras · filtro_so · palavras | **1,000** · 0,731 · 0,682 · 0,194 | **1,000** · 0,694 · 0,581 · 0,233 |
| P@5 (rel ≥ 1): jev · palavras (teto 0,95) | 0,950 · 0,200 | 0,950 · 0,175 |
| relevantes após a recuperação: rel ≥ 1 · rel = 3 | 92/92 · 38/38 | 206/206 · 75/75 |
| **perda da recuperação** (rel ≥ 1 · rel = 3) | **0 · 0** | **0 · 0** |
| rel = 3 no top-10: jev · filtro_palavras · palavras (teto) | 33 · 23 · 10 (33) | 71 · 58 · 26 (71) |
| relevância prevista (argmax) = gabarito, entre os recuperados | 124/124 | 311/311 |
| requisições · tokens · US$ por consulta | 16,5 · 18.959 · 0,00080 | 20,4 · 21.826 · 0,00092 |
| latência por requisição p50/p95 · por consulta p50/p95 | 261/344 ms · 873/1.994 ms | 271/346 ms · 1.008/2.787 ms |

A latência por consulta soma a leitura da consulta à fila de 8 vagas, montada com os ms medidos de cada
requisição. A pior consulta do teste (T016, 67 recuperados, 4 critérios) fez 68 requisições e levou 2,8 s. Nas
455 chamadas reais do ajuste e do teste o SDK não fez nenhuma retentativa.

## O que deu certo
- **O Jev no anúncio vale a chamada.** Sobre o mesmo filtro, o BM25 ganha +0,05 a +0,11 de NDCG em relação à
  ordem do catálogo, e o Jev ganha +0,32 a +0,42. As palavras-chave falham no ponto que a escala pune: a frase
  negada contém a palavra ("não existe ambiente apropriado para **escritório**"). Em T016, o
  `filtro_palavras` fez 0,096.
- **A omissão como resposta.** A opção `omite` separa o 1 e o 2 do 3 e do 0. A matriz saiu diagonal nos 435
  recuperados.
- **A leitura da consulta aguentou paráfrase e negação:** "Não serve se precisar de reforma; quero pronto"
  (reformado 0,90), "Não quero rua barulhenta" (0,98), "meu cachorro precisa poder morar comigo" (0,98),
  "entre 350 e 650 mil" (piso e teto).
- **Custo:** US$ 0,92 por mil consultas.

## O que falhou ou ficou frágil (visto no teste, NÃO corrigido)
1. **O ajuste não calibrou nada.** Tudo caiu longe dos limiares. No anúncio, a menor probabilidade máxima
   foi 0,97 (0 de 873 leituras abaixo de 0,9). Na consulta, as confianças duras ficaram ≥ 0,98. A faixa de
   dúvida `P_ACEITA` nunca disparou em dado rotulado. O 1,000 mede a **composição** (filtro e escala em
   probabilidade) num texto de três frases fixas por fato. Ele não mede a leitura do Jev sob a variedade de um
   anúncio real.
2. **Os dois consertos que importaram vieram de consultas de rascunho do construtor, não do ajuste.** No
   ajuste, todos os preços caíam na grade de 50 mil e os critérios usavam as palavras do catálogo.
   - Com grade de 50 mil, "até 620 mil" virou **600 mil**, com confiança 0,91. É uma perda silenciosa.
   - O teste trouxe dois preços fora dessa grade: T011 "590 mil" e T010 "740 mil". Arredondando para baixo
     como no rascunho, eles teriam descartado **6 relevantes, 4 deles rel = 3**. Isso é exposição calculada
     depois do teste, não uma medição com a grade antiga.
   - A grade de 10 mil custa ~7 mil tokens a mais por consulta. A leitura da consulta inteira já é metade dos
     tokens.
3. **Colisão de nome com critério:** "No **Jardim** Norte…" deu 0,29 para "pede jardim" no teste e 0,15 no
   ajuste. A pista "(jardim, área verde)" que pus na pergunta aproximou o nome do bairro do critério. A
   margem até o limiar 0,5 foi de 0,21.
4. **Situação no lugar de pedido:** "Trabalho de casa" deu home office 0,68. Foi o pedido mais fraco, a 0,18
   do limiar.
5. **Custo escondido confirmado:** uma requisição por anúncio faz a consulta larga custar 68 chamadas e
   levar 2,8 s. A leitura da consulta, com 262 opções de preço, é metade dos tokens.

## Lições
1. **O risco de recuperação mora na leitura da CONSULTA, não na do anúncio.**
   - Uma grade que arredonda some com o anúncio antes de o Jev vê-lo, e nenhuma métrica de ranking denuncia
     isso.
   - Meça a perda da recuperação à parte e prove a grade com valores fora dela de propósito. Um ajuste com
     valores redondos não prova a grade.
   - Na dúvida, o filtro fica largo: errar para fora custa ordenação, e errar para dentro custa o anúncio.
2. **Modele a estrutura do fato, não a nota.**
   - Ternária por critério e escala em código como probabilidade dão uma ordem pelo ganho esperado. Não há
     peso inventado.
   - Um Score "quão bom é o anúncio?" poria o critério não informado e o incerto no mesmo meio da escala.
3. **Dois lados, duas frases.**
   - O lado da pessoa precisa das palavras dela. No rascunho, "perto do metrô" foi de 0,53 para 0,98 e
     "precisa ter jardim" de 0,30 para 0,99.
   - O lado do anúncio precisa do fato.
   - A pista em português na pergunta também pesca nome próprio (Jardim Norte), como na lição 3.
4. **Vocabulário fechado deixa indexar na ingestão (estimativa, não medido).**
   - Os 8 critérios são fixos, então uma requisição por anúncio com as 8 ternárias dá ~1,2 mil tokens × 150,
     ~US$ 0,008 uma vez só.
   - Depois disso, cada consulta custaria 1 requisição (~300 ms) em vez de 1 + n (p95 2,8 s).
   - A leitura por consulta só se paga quando o critério é aberto ("perto de escola"). Neste gabarito isso não
     ocorre.
5. **Um ajuste perfeito na 1ª passada é sinal de ajuste fácil**, a mesma lição da triagem, do guardrail e da
   extração. A tabela "Margem das leituras" em `resultados.md` diz onde nenhum limiar foi testado.

Varredura da família:
- `_comum/metricas.py:ndcg` tira o ideal da **lista devolvida**. Numa busca, isso esconde exatamente a perda
  da recuperação: um sistema que devolve só 2 relevantes de 20 teria NDCG alto. Nenhum outro exemplo o usa
  hoje. Este projeto calcula o ideal pelo gabarito inteiro.
- Choice sobre grade numérica que arredonda: não achei em `exemplos/*/perguntas.py`. A extração usa o dia de
  1 a 31, um conjunto completo.

## Limites
- **Demonstração de mecanismo.** O catálogo é sintético e controlado (Codex, seed 20260930), com 3 enunciados
  por estado de fato. O gabarito vem dos fatos de autoria. O teste usa consultas novas sobre o **mesmo**
  catálogo, não anúncios inéditos.
- Premissas:
  - "2 quartos" = mínimo de 2 (LEIA-ME: quantidades são mínimas e inclusivas).
  - "casa" ≠ sobrado (conferido no ajuste).
  - Tipo, cidade e bairro são as opções do catálogo (`run.ts` recusa o catálogo se aparecer valor novo).
- Não cobertos:
  - preço fora da grade de 10 mil (ex.: 625 mil) e acima de 1,5 milhão;
  - critério fora dos 8 (ele some calado);
  - "casa ou sobrado", que no rascunho virou "qualquer tipo" (confiança 0,65): cobre a recuperação, mas não
    tem prova rotulada.
- Amostra pequena: 24 consultas. Um modelo só (`jev-1.13.0`) e uma rodada. Repetir a mesma chamada varia
  ~0,01, com máximo de 0,15.

## Como rodar
```bash
npm install                      # Node ≥ 20 (SDK @typesafe-ai/sdk 0.6.0, tsx)
npm start                        # ajuste + teste do cache/ (recusa se perguntas.ts/busca.ts mudaram desde o congelamento)
JEV_MODO=gravado npm start       # só o cache (455 respostas reais do ajuste e do teste + 18 do rascunho), sem chave
JEV_MODO=ao_vivo npm start       # refaz as chamadas
npm run ajuste | congelar | rascunho | typecheck
```

## O SDK JS na prática (0.6.0)
- **Tipos:**
  - `answers.tipo.probabilities` e `answers[c].probabilities` saem tipados pelas chaves dos critérios.
  - Perguntas montadas com `Object.fromEntries` (um Noul por critério) perdem a inferência e pedem `as
    Record<\`pede_${Nome}\`, NoulQuestion>`.
  - Iterar as respostas por nome genérico pede cast.
  - A tipagem é **só de compilação**: o SDK faz `JSON.parse` da resposta sem validar a forma.
- **Corpo:** `systemOne` espalha `...request` no corpo. Campo extra vai para a API, que responde 400 (medido
  em 2026-09-30). O cache passa só `state`, `questions` e `model`.
- **Retentativa:** o padrão é 2 retentativas, 500 ms dobrando até 5 s. Ela **só é observável pelo logger no
  nível `info`**, pela mensagem "retrying in …": a resposta não traz contagem. Aqui um logger próprio conta
  as retentativas e descarta o resto. Nunca use `debug`, que imprime os corpos.
- **Validação local:** além de perguntas vazias e Score com menos de 2 níveis, `choice()` recusa critérios
  em lista e `score()` recusa mapa. A nota `memoria/sdk/javascript.md` diz "só perguntas vazias e score".
