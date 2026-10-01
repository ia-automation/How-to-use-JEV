# Exemplos medidos na API real — índice

Cinco projetos pequenos, cada um com dados rotulados (escritos pelo Codex, sintéticos, pt-BR), perguntas e
limiares num arquivo só, **ajuste separado do teste** (teste congelado por hash e rodado uma vez) e o cache das
respostas reais do `jev-1.13.0` (2026-09-30), para reproduzir os números sem chave. Especificação:
[BRIEFING.md](BRIEFING.md) e [DADOS.md](DADOS.md). Números detalhados em cada `resultados.md`, gerado pelo script.
Síntese e leitura crítica: [medicoes](../conhecimento/evidencias/medicoes-2026-09-30.md#exemplos-dados-sintéticos-do-codex-rodada-única-no-teste)
e [metodo](../conhecimento/avaliar/metodo.md).

| Projeto | Problema | Resultado no teste [testado] | Lição principal |
|---|---|---|---|
| [roteador-jev-llm](roteador-jev-llm/README.md) (Python) | cada pedido de cliente vai para código (FAQ/status), LLM barato, LLM de raciocínio ou humano; 27 perguntas numa requisição | destino certo 50/60 (0,833); 1 risco vazou ao LLM barato; economia estimada 76,5% contra "tudo no raciocínio" (LLM **simulado**, cenário); Jev US$ 0,10 por mil pedidos | pergunta larga no topo da precedência engole rotas; alargar pergunta para consertar o ajuste é overfit; a regex "exata" foi a maior fonte isolada de erro |
| [triagem-atendimento](triagem-atendimento/README.md) (Python) | ticket → setor, reembolso, quer humano, ameaça cancelar, frustração, prioridade; pt × en | acerto por pergunta 0,93–1,0; roteamento en 0 erro em 65% automático, pt 2 erros em 72%; perguntas em pt não ajudaram (+10% tokens) | a confiança da Choice não mostra duas intenções (use Noul por setor); regra afinada num caso não generalizou; 1 dos 2 erros depende de rótulo disputável (T018) |
| [extracao-sem-inventar](extracao-sem-inventar/README.md) (Python) | e-mail, telefone, CPF, valor em R$ e data de visita de mensagens | por campo 0,925–1,000; saída fora dos candidatos = 0; US$ 0,04 por mil mensagens | "zero inventado" ≠ zero erro semântico (data negada virou visita); `none` lido ao pé da letra; só a cobertura dos candidatos denunciou centavos perdidos |
| [guardrail-chatbot](guardrail-chatbot/README.md) (Python) | toda mensagem que entra e sai de um chatbot → passa / revisa / bloqueia | 57/60 (0,950); falso "passa" em bloqueio 0/30; os 3 erros foram a humano; US$ 0,05 por mil mensagens | a faixa do meio vale mais que o acerto (limiar único daria 0,967 com 1 vazamento); não perguntar ao Jev o que o texto não diz ("de quem é este dado?") |
| [busca-imoveis](busca-imoveis/README.md) (TypeScript, SDK JS) | busca em linguagem natural sobre 150 anúncios fictícios de catálogo controlado | NDCG@10 1,000 (palavras-chave 0,233; filtro + palavras 0,694); perda da recuperação 0/206; US$ 0,92 por mil consultas | **demonstração de mecanismo**, não desempenho real; o risco mora na leitura da consulta (grade de preço que arredonda descarta anúncio); uma requisição por anúncio multiplica chamadas |

Infra comum: [_comum/](_comum/) (cliente com cache `jevcache.py` e métricas `metricas.py`). Rodar sem chave:
`python run.py` (ou `npm start` na busca) reproduz do cache; `JEV_MODO=ao_vivo` refaz as chamadas.
Limites comuns: dados sintéticos são mais fáceis que reais; n pequeno (30 de ajuste, 40–60 de teste); uma
versão do modelo; uma rodada.
