---
name: jev-llm-codigo
description: Como decidir, ao projetar e ao codar, entre código, Jev e LLM (ou um híbrido) — perguntas de triagem, matriz, custos e latências medidos, os 6 híbridos e os erros comuns nas duas direções.
tipo: principio
fonte: síntese da documentação TypeSafe (snapshot 2026-09-30), testes na API real em 2026-09-30 (exemplos/ e avaliar/), vídeos 2 e 3, tabela de preços OpenAI de 2026-09-30, padrões de aplicação do Codex
estudado_em: 2026-09-30
---

# Código × Jev × LLM — como decidir

Rótulos: **[doc]** documentação TypeSafe · **[testado]** medido por nós na API em 2026-09-30 (jev-1.13.0,
chamadas do Brasil) · **[terceiro]** vídeo · **[local]** conclusão nossa.

## As 5 perguntas de triagem (nesta ordem)
1. **O código resolve exato?** (regra, cálculo, busca exata, data, contagem, regex, permissão) → **código**.
   Nunca pague modelo por algo determinístico. [doc: jaggedness #2, #3]
2. **A saída é texto novo para alguém ler?** (resposta ao cliente, resumo, e-mail, código) → **LLM**.
   O Jev não gera texto. [doc]
3. **A resposta cabe num espaço fechado que você consegue listar?** (uma de N opções · um nível de
   uma rubrica · sim/não) → **Jev** é o candidato natural.
4. **O julgamento exige raciocínio em várias etapas, conhecimento de mundo para desambiguar, ou
   extrair um valor que você não consegue gerar como candidato?** → **LLM** (ou decompor até caber
   no Jev; se não couber, LLM). [doc: jaggedness #4, #9; terceiro: caso "MS"]
5. **Volume, latência ou custo importam?** (milhares/milhões de decisões, caminho de requisição em
   tempo real, rodar em segundo plano sem supervisão) → pesa fortemente para **Jev**, mesmo que um LLM
   também acerte.

Se passou por 3 e por 4 ao mesmo tempo: **híbrido** (abaixo).

## Matriz rápida
| Situação | Escolha | Por quê |
|---|---|---|
| classificar ticket/e-mail/lead em categorias conhecidas | Jev (Choice) | fechado, volume, confiança para mandar o incerto a humano |
| "isso contém / pede / ameaça X?" | Jev (Noul) | sim/não com probabilidade; faixa de dúvida vira revisão |
| grau (urgência, frustração, aderência a um perfil) | Jev (Score) | níveis descritos; ordena itens |
| ranquear N candidatos contra uma consulta | Jev (1 Noul/Score por item) | paralelo e barato; LLM listwise custa N× mais tokens de saída |
| checar resposta/extração/citação de outro LLM | Jev | verificação por campo a uma fração do custo da chamada verificada |
| escolher ferramenta/skill/modelo para um agente | Jev (Choice + Nouls) | rota rápida antes do LLM caro |
| extrair valor citado no texto (e-mail, telefone, valor, data) | código acha candidatos + Jev escolhe | o Jev não inventa; o código copia literal |
| extrair valor que não dá para listar (nome livre, endereço solto) | LLM (+ Jev verifica) | o Jev não gera |
| responder, resumir, reescrever, traduzir, conversar | LLM | geração |
| raciocínio de várias etapas, política + cálculo + exceção | LLM de raciocínio (+ código para as contas) | Sistema 2 |
| desambiguar sigla/nome pelo conhecimento de mundo | LLM, ou pré-filtro + Jev | o Jev é literal (caso "MS") |
| contar, somar, comparar números/datas | código | o Jev não conta nem compara |

## Custos e latências (números com fonte)
**Preço por milhão de tokens (US$):** Jev 0,042 entrada / **0 saída** [doc] · gpt-6-luna 0,10 / 0,50 ·
gpt-6-sol 2 / 10 · gpt-6-astra 10 / 50 [premissa: tabela de preços da OpenAI informada pelo dono em
2026-09-30; não conferida na página oficial — conferir antes de decidir por custo].

**Exemplo: classificar um ticket** (~400 tokens de entrada; o LLM devolve ~60 tokens de JSON):
| Modelo | Custo por ticket | Por milhão de tickets | × Jev |
|---|---|---|---|
| Jev | US$ 0,0000168 | US$ 16,80 | 1× |
| gpt-6-luna | US$ 0,000070 | US$ 70 | ~4× |
| gpt-6-sol | US$ 0,0014 | US$ 1.400 | ~83× |
| gpt-6-astra | US$ 0,0070 | US$ 7.000 | ~420× |
[local: conta sobre os preços acima; modelos de raciocínio somam tokens de raciocínio na saída → a
diferença cresce]

**Mais perguntas no mesmo texto:** no Jev, cada pergunta curta extra ≈ 20 tokens de entrada e a
latência quase não muda (1 → 100 perguntas: 283 → 322 ms) [testado]. No LLM, cada campo a mais na
resposta é saída cobrada e gerada token a token.

**Latência:** Jev ~100 ms [doc] · 280–350 ms ponta a ponta daqui, 20 chamadas paralelas em 368 ms
[testado] · 0,4 s contra 2,6 s do DeepSeek V4 Flash, mesma tarefa [terceiro, vídeo 2] · 1,5–2,7 s por
chamada via gateway com Choices de 26–80 opções [terceiro, vídeo 3]. Medições completas:
[medicoes](../evidencias/medicoes-2026-09-30.md).

**Qualidade em texto real pt-BR com gabarito humano** [testado 2026-09-30, jev-1.13.0, teste n = 300 por
corpus, dois corpora públicos, uma versão, uma rodada]: sem exemplos no contexto nem ajuste de pesos (perguntas e
limiar afinados em 100 rotulados), o Jev superou o TF-IDF + logística com ~3,3 mil rótulos no HateBR; no B2W,
contra o de ~67 mil, a diferença ficou não resolvida (IC inclui zero); US$ 0,024 no total; a incerteza acompanhou a
discordância humana. Números e ressalvas: [medicoes](../evidencias/medicoes-2026-09-30.md#texto-real-pt-br-com-gabarito-humano-r4r5).
Dois corpora não fazem regra: medir no próprio domínio.

**Onde o LLM ganha:** o caso "MS" (vídeo 2) — o LLM entendeu que "MS NOW" não era Morgan Stanley; o
Jev disse `negative` com probabilidade 0,50 × 0,49 (confiança 0,25) ([video-02](../evidencias/videos/video-02-quantbrasil.md)). O conserto foi de DESENHO
(Noul "o artigo menciona Morgan Stanley?" antes do sentimento: 0,09), não de modelo. Regra: se o
desenho não consegue isolar a ambiguidade numa pergunta literal, é trabalho de LLM.

## Os 6 híbridos (os mais valiosos)
| Híbrido | Como | Exemplo / receita |
|---|---|---|
| **Jev roteia → LLM executa** | Choice de intenção + Score de complexidade + Nouls de risco; só o que precisa vai ao LLM (o barato ou o de raciocínio) | [roteador-jev-llm](../../exemplos/roteador-jev-llm/README.md); [roteamento-por-intencao](../construir/padroes/roteamento-por-intencao.md) |
| **LLM extrai → Jev verifica** | bateria de Nouls por campo; escala ao modelo grande só se algum campo falhar; falha de parse/campo ausente tem caminho próprio | [cascata-sde](../receitas/cascata-sde.md) |
| **Código/LLM gera candidatos → Jev escolhe** | regex, BM25 ou LLM propõe; Choice com `none` escolhe; código copia | [extracao-sem-inventar](../../exemplos/extracao-sem-inventar/README.md); [extracao-de-valor-pre-parseado](../receitas/extracao-de-valor-pre-parseado.md), [reranking](../receitas/reranking.md) |
| **Jev filtra contexto → LLM responde** | Noul de relevância por passagem antes do prompt | [classificar-passagens-rag](../receitas/classificar-passagens-rag.md) |
| **Jev guarda o LLM** | Nouls de perigo em toda entrada e saída; política por limiar (não é fronteira de segurança) | [guardrail-chatbot](../../exemplos/guardrail-chatbot/README.md); [guardrails-llm](../receitas/guardrails-llm.md) |
| **Jev incerto → escala** | confiança baixa ou Noul no meio → LLM de raciocínio ou humano | [roteamento-por-confianca](../construir/padroes/roteamento-por-confianca.md) |

E o inverso: **LLM propõe perguntas → Jev responde em escala → modelo clássico aprende**
([autoresearch-de-features](../receitas/autoresearch-de-features.md)).

**Jev como extrator de features** [testado 2026-09-30, dados internos]: em conversas reais de venda
(anonimizadas), perguntas atômicas sobre a janela inicial, combinadas em código (pesos fixos ou logística),
predisseram o desfecho melhor que a contagem de mensagens e que TF-IDF com 100 rótulos — sinal modesto:
ordena melhor que o acaso, não decide sozinho nem é probabilidade calibrada; priorizar a fila com ele é
hipótese a ensaiar ([medicoes](../evidencias/medicoes-2026-09-30.md#dados-internos-conversas-reais-de-venda)).

**Entrada que não é texto** (áudio, imagem, vídeo, binário): o Jev só aceita texto [doc]. Outro
componente transcreve/descreve → o Jev julga o texto → o código executa; texto novo fica com um modelo
gerativo. Assim o estúdio por voz do vídeo 3 (transcrição → Choices sobre componentes existentes → código
renderiza; LLM local escreve) [terceiro, [video-03](../evidencias/videos/video-03-maestros-da-ia.md)].
**Identificação antes do julgamento**: sigla ou nome que pode ser outra entidade → Noul de referência
antes de consumir o sentimento (vídeo 2); as perguntas podem ir na mesma chamada.

## Erros comuns
**Usar LLM onde o Jev resolve:** prompt "responda só com JSON {categoria, confiança}" para
classificar; LLM como juiz de sim/não em lote; ranquear 100 itens pedindo lista ordenada ao LLM;
pedir "confiança" a um LLM (é texto gerado, não probabilidade calibrada).
**Usar Jev onde não cabe:** pedir texto; pedir conta, contagem ou comparação de datas; uma pergunta
ampla ("isto é spam?") em vez de sinais atômicos; varrer milhares de opções sem pré-filtro (vídeo 2:
errou muito no universo inteiro); confiar numa resposta com confiança baixa.
**Nos dois:** limiar espalhado pelo código; não versionar o modelo; não medir no próprio domínio
(português: [medicoes](../evidencias/medicoes-2026-09-30.md#idioma); protocolo: [metodo](../avaliar/metodo.md)).

## Checklist de desenho (antes de codar)
- [ ] Separei o que é regra (código) do que é julgamento (Jev) do que é geração (LLM)?
- [ ] Cada julgamento do Jev é uma pergunta literal, atômica, com espaço de resposta fechado e saída
      "nenhum/não declarado"?
- [ ] Todas as perguntas do mesmo texto vão numa chamada?
- [ ] O que acontece com confiança baixa em cada ramo?
- [ ] Onde o LLM entra, ele recebe só o que o Jev não resolve?
- [ ] Custo e latência estimados com os números acima, para o volume real?
- [ ] Conjunto rotulado do próprio domínio para medir antes de ligar?
