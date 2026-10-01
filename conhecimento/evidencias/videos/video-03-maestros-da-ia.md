---
name: video-03-maestros-da-ia
description: Maestros da IA (28/09/2026) — tese "janela de oportunidade" e 17 apps de demonstração (estúdio por voz, venda cruzada no caixa, página que se adapta, planilha preditiva); quadros com chamadas, perguntas, latência (0,34–2,7 s por chamada via OpenRouter) e custo; mistura propaganda de VPS e prática de risco.
tipo: visao-externa
fonte: https://www.youtube.com/watch?v=WLSqQprxai4 (47:07, pt-BR)
transcricao: fontes/videos/03-maestros-da-ia-janela-para-lucrar.md (fora do Git)
estudado_em: 2026-09-30
---

# Vídeo 3 — "JEV: a melhor janela para lucrar com IA em anos" (Maestros da IA)

[terceiro] Publicado em 2026-09-28; 47min07s. Claude: transcrição por legenda automática. Codex: legenda
original completa e **quadros conferidos** em 12:50, 19:55 e 43:57 (números marcados "quadro"). Sem acesso
ao código dos apps nem reprodução dos testes.

## A tese
- Tudo que as demos virais mostram "dá para fazer de outro jeito" (RL, automação simples, LLM barato
  ou local). O diferencial é ser **muito mais barato e rápido** — o autor admite ter subestimado isso.
- Três corridas: qualidade (OpenAI × Anthropic), preço (dominada pela China), velocidade (negligenciada).
  O Jev abandonou a primeira para "humilhar" nas outras duas.
- Três funções nas palavras do vídeo: classificar (Choice), decidir (Noul — ex.: "esse lead é
  qualificado o bastante para marcar reunião, pelo histórico da conversa?"), nota em escala (Score —
  ex.: animosidade de tickets para priorizar).

## As demonstrações (17 apps; 4 mostrados)
| App | Como usa o Jev | Número citado (narração) | Quadro (Codex) |
|---|---|---|---|
| Estúdio por voz ([12:22](https://www.youtube.com/watch?v=WLSqQprxai4&t=742s)) — site, identidade visual, e-mail, anúncios, carrosséis | fala → transcrição em tempo real → muitas Choices (paleta, fonte, ícones, forma, template por seção) + Scores (tempo de mercado, faixa de preço percebida); **texto escrito por um LLM local** ([15:43](https://www.youtube.com/watch?v=WLSqQprxai4&t=943s)), não pelo Jev | "microdecisões por segundo" | 12:50: 6 chamadas / 89 perguntas (59 escolha, 4 nota, 26 sim/não). Grupo Entender 10 perguntas 1.465 ms US$ 0,000137; Site 28 perguntas 2.124 ms US$ 0,000144; Marca 8 perguntas 2.703 ms US$ 0,000265. Choices grandes: paleta 26 opções, fonte 17, ícone 80, forma 7, disposição 5, caixa 3. **Instruções em português** ("…Se ela mudou de ideia no meio da fala, vale o que disse por último."). 1,5–2,7 s por chamada via OpenRouter, com opções grandes |
| Venda cruzada / busca que entende ([19:50](https://www.youtube.com/watch?v=WLSqQprxai4&t=1190s)) | contexto do cliente ("vou acampar com meus filhos", "sou chef") → **1 Score por produto** "quão bem o produto X atende ao pedido?" sobre 120 produtos → ordena | ~200 ms | 19:55: 6 chamadas / 125 perguntas (5 escolha, 120 nota); entendimento 5 perguntas 392 ms US$ 0,000062; **lote 1/5 = 24 Scores numa chamada**, 343 ms, US$ 0,000173; Score 0–3 ("Irrelevante", "Talvez"…); pergunta "Quão bem o produto p001 atende ao pedido do cliente?" |
| Página de vendas que se adapta ([20:43](https://www.youtube.com/watch?v=WLSqQprxai4&t=1243s)) | classifica cliques/leitura para montar perfil e reordenar seções/ofertas existentes | — | — |
| Planilha preditiva ([27:02](https://www.youtube.com/watch?v=WLSqQprxai4&t=1622s)) | pergunta livre sobre cada linha ("quem pode comprar hoje?", "quais leads estão bravos?", "quem teria interesse em produto caro?") → **1 Noul por linha**, ordena por probabilidade | 124 linhas em 1–2 s; 120 linhas < US$ 0,01; 10.000 linhas projetadas < US$ 0,05 | 43:57: 6 chamadas / 124 Nouls; "Chamada 5 de 6 · lote 5/6 · Quer comprar? 21 perguntas · 347 ms · US$ 0,0000934 · **typesafe/jev-1.13-20260917**" (ID versionado no gateway); pergunta "Linha r85: Quer comprar?" em português; lotes de ~21 linhas por chamada |

Na planilha: "segue há muito tempo?" deu 63% para quem citou vídeo antigo; "quer contratar
consultoria" 91–92%.

**Divergência registrada:** a narração fala em ~200 ms na venda cruzada; os quadros mostram 343–392 ms por
chamada nessa demo e 1,5–2,7 s no estúdio (via OpenRouter, Choices de 26–80 opções). Nenhum desses números
é medição nossa; os nossos estão em [medicoes](../medicoes-2026-09-30.md).

## Acesso
Pelo **OpenRouter** (chave com limite de gasto e validade configuráveis) — não pela API própria.

## Cuidado
- Metade do vídeo é tutorial para montar os apps numa VPS com cupom de afiliado. O tutorial de
  hospedagem é escolha do autor, não dependência do Jev.
- O tutorial entrega ao agente de código uma **chave de API da hospedagem com poder de reinstalar o
  servidor** e uma chave do OpenRouter coladas no prompt. Não seguir esse modelo: segredo em prompt e
  agente com poder destrutivo sobre infraestrutura ([integracao-segura](../../construir/integracao-segura.md)).
- Nenhum número medido com rigor; "17 apps" não mostrados por inteiro; promessas de receita, conversão e
  custo não validadas.

## O que aproveitar
- Padrão **"1 pergunta por item, ordenar pela probabilidade"** (produto × pedido, lead × pergunta)
  é o do [reranking](../../receitas/reranking.md), aplicado a catálogo e lista de leads. Os quadros
  mostram **lotes de perguntas** e rubrica compartilhada — não um endpoint especial de catálogo.
- Jev decide, **LLM (até local) escreve** — divisão de trabalho recorrente. A demo de voz usa uma etapa
  anterior de transcrição: não é evidência de entrada de áudio nativa no Jev (a entrada documentada é só
  texto; ver [state](../../modelo/state.md)).
- Tabela com decisões por registro: incluir o registro na instrução ou apontar seu caminho no state,
  ligar a resposta ao ID original; lote que falhou é pendente, não "não" (recomendação local,
  [integracao-segura](../../construir/integracao-segura.md)).
- Qualificação de lead pelo histórico da conversa é caso direto de Noul ([casos-de-uso](../../modelo/casos-de-uso.md) — geração de leads).

## Relacionados
[video-02-quantbrasil](video-02-quantbrasil.md) · [reranking](../../receitas/reranking.md) · [fan-out-especulativo](../../construir/padroes/fan-out-especulativo.md) · [jev-llm-codigo](../../decidir/jev-llm-codigo.md)
