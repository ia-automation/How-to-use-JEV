---
name: video-01-max-carrau
description: Vídeo "Jev explicado em 4 minutos" (Max Carrau, 23/09/2026) — a tese em analogia — LLM foi treinado para conversar e programar; automação ficou de fora; Jev é a "gaveta" que faltava. Opinião/divulgação, sem teste próprio.
tipo: visao-externa
fonte: https://www.youtube.com/watch?v=vzYKuvD05rE (4:13, pt-BR)
transcricao: fontes/videos/01-jev-explicado-em-4-minutos.md (fora do Git)
estudado_em: 2026-09-30
---

# Vídeo 1 — "Jev explicado em 4 minutos" (Max Carrau | IA)

[terceiro] Publicado em 2026-09-23; 4min13s. Estudado pelos dois agentes em 2026-09-30 (primeiro da ordem
pedida). Método do Claude: transcrição por legenda automática. Método do Codex: legenda automática original
completa (`pt-orig`) e imagens a cada 20 s — não equivale a conferir cada frame. A legenda varia a grafia de
Jev e Typesafe ("JV", "Jeff"): nomes, código e números não se copiam dela como especificação.

## O que acrescenta ao doc
- **Enquadramento:** desde 2022 todo modelo foi treinado para conversar; desde 2025 (Claude Code,
  Codex) para conversar e programar. "Quem manda no modelo é o uso." Automação — "fluxo que decide
  1.000 vezes por dia: aprova, classifica, manda para cá ou para lá" — ficou de fora; usar um modelo
  de fronteira nisso funciona, mas é lento e caro.
- Analogia: goleiro no pênalti não escreve três parágrafos antes de pular. Adaptar modelo de chat para
  automação = "pino quadrado em buraco redondo".
- Não é "Jev contra Claude": é o contrário do rumo atual, não substituto.
- Números citados (da TypeSafe): 40 a 200× mais rápido; 70 a 500 ms do pedido à resposta (não
  confirmados no doc nem por nós).
- Por que é rápido: LLM escreve token a token, sem atalho; o Jev "amostra em paralelo e devolve a
  decisão já com tipo e probabilidade". A diferença não é o que ele sabe, é o **alvo de treino**.
- "Você não conversa com o Jev": manda uma ficha (pergunta, opções, formato), volta outra ficha com a
  chance de cada opção. Três peças — "escolha, nota e nulo" — "quase voltar para porta lógica"
  (o "nulo" é o **Noul**, não `null`; ver [primitivas](../../modelo/primitivas.md)).
- Lugar na caixa de ferramentas: gaveta dos rápidos e baratos (junto de GPT 5.6 Luna, DeepSeek V4
  Flash, Sonnet 5), mas **só em tarefa de fluxo**. Faltava a gaveta de automação.
- Método RLCD não aberto; no Reddit alguém montou algo parecido com BERT bidirecional aberto de
  421 M parâmetros que roda em notebook (afirmação do vídeo, não verificada).
- Conclusão do autor: a notícia é a volta do **modelo pequeno especialista** — "bateu no limite da
  arquitetura ou do treino? Treina um modelo pro limite certo".

## Trechos com timestamp (Codex)
| Trecho | Síntese |
|---|---|
| [00:38](https://www.youtube.com/watch?v=vzYKuvD05rE&t=38s) | O foco é a decisão recorrente em automações: classificar, aprovar e encaminhar. |
| [01:23](https://www.youtube.com/watch?v=vzYKuvD05rE&t=83s) | Jev como ferramenta especializada, complementar a modelos conversacionais e de programação. |
| [01:30](https://www.youtube.com/watch?v=vzYKuvD05rE&t=90s) | Alega ganhos de velocidade; sem medição reproduzida. |
| [02:19](https://www.youtube.com/watch?v=vzYKuvD05rE&t=139s) | A interação é uma solicitação estruturada com opções e saída restrita. |
| [02:37](https://www.youtube.com/watch?v=vzYKuvD05rE&t=157s) | Escolha, pontuação e "nulo" como peças combináveis; a semântica de API vem da documentação. |

## Confiabilidade
Opinião/divulgação; sem teste próprio. Números vêm da TypeSafe. Útil como explicação curta. O vídeo
explica o posicionamento; não demonstra autenticação nem tratamento de falhas.

## Relacionados
[o-que-e-o-jev](../../modelo/o-que-e-o-jev.md) · [video-02-quantbrasil](video-02-quantbrasil.md) · [video-03-maestros-da-ia](video-03-maestros-da-ia.md)
