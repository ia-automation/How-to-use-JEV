# R4/R5 — o Jev em texto real em português, com gabarito humano

Avaliação do `jev-1.13.0` zero-shot (sem exemplos no contexto nem ajuste de pesos; perguntas e limiar afinados
em 100 exemplos rotulados) em dois conjuntos públicos rotulados por pessoas, feita pelo protocolo
congelado [`PROTOCOLO.md`](PROTOCOLO.md). Os números estão em [`resultados.md`](resultados.md), gerado pelo script.

- **R5 · HateBR** (Vargas et al., LREC 2022, CC BY-NC 4.0): o comentário do Instagram é ofensivo?
- **R4 · B2W-Reviews01** (B2W Digital, CC BY-NC-SA 4.0): recomendaria a um amigo? (R4a) e nota 1–5 (R4b).

## O que mostra (teste, n = 300 por corpus, uma rodada)
| tarefa | Jev | melhor baseline com os mesmos 100 rótulos | TF-IDF + LR com milhares de rótulos (outro regime) |
|---|---|---|---|
| R5 macro-F1 | **0,937** [0,906; 0,962] | léxico 0,579 | 0,798 (3.314 rótulos); Δ +0,139 [0,097; 0,186] |
| R4a macro-F1 | **0,899** [0,859; 0,932] | léxico 0,683 | 0,886 (67.339 rótulos); Δ +0,012 [−0,029; 0,055] |
| R4b MAE (nota) | **0,430** [0,359; 0,502]; ±1 0,953 | léxico 1,143 | 0,497; ΔMAE [−0,148; 0,020] |

- Sem exemplos no contexto e sem ajuste de pesos — com perguntas e limiar afinados nos 100 rotulados do
  ajuste —, o Jev fica à frente do TF-IDF + LR treinado com 3,3 mil rótulos no HateBR; no B2W, contra o de
  67 mil, esta amostra **não resolveu a diferença** (IC do Δ inclui zero; não é prova de equivalência).
- **A incerteza do Jev acompanha a divergência humana.** No HateBR, o acerto foi 0,957 nos itens unânimes e
  0,830 nos disputados, com Brier 0,037 × 0,152. A faixa de dúvida 0,2–0,8 recebeu 15% dos unânimes e 40%
  dos disputados. Com ela, o Jev decide 81% (R5) e 85% (R4a) dos casos, com acerto de 0,97 e 0,96 nos decididos.
- Auditoria das divergências. No R5, 13 dos 19 erros são gabarito discutível ou leitura defensável. No R4a,
  10 dos 20 da amostra são gabarito contrário ao texto ou texto sem opinião sobre o produto. O erro próprio do
  Jev aparece em três lugares: ofensa sem palavra pejorativa (apologia, incitação), gíria pejorativa nova e
  ressalva leve lida como "não recomendaria" (24 falsos não × 2 falsos sim no R4a).
- Custo total de US$ 0,024 (ajuste e teste somados), com p50 de 269 ms e p95 de 333 ms.

## O que NÃO mostra
- Taxa de erro rara, porque n = 300 é exploratório. O HateBR do teste tem só 34 posts, então o intervalo é largo.
- Desempenho em tráfego real. O HateBR é 50/50 por construção e, com ofensa rara, a precisão cairia.
- Comparação com um LLM, porque sem autorização para outro provedor ele não entrou. O TF-IDF treinado com 100
  exemplos virou maioria no limiar 0,5, então a comparação justa com ele é a PR-AUC (R5 0,981 × 0,748).
- Estabilidade entre versões ou rodadas: há uma versão e uma rodada. Itens perto do limiar podem trocar de lado.
- Que as perguntas generalizem para outra definição de ofensa. Elas foram afinadas no ajuste (2 passadas) para a
  definição do HateBR.

## Arquivos e como rodar
`preparar.py` faz elegíveis, deduplicação, divisão por grupo com semente e hashes → `preparacao.md`/`.json`,
publicados antes da API. `perguntas.py` guarda as perguntas, os limiares e a conversão; é o único arquivo afinado.
`baselines.py` guarda os baselines. `avaliar.py ajuste|congelar|teste` gera `congelamento.json` com os hashes
anteriores ao teste. `auditoria.json` tem as categorias das divergências, só com IDs.
O texto licenciado, o cache das respostas e as listas com texto ficam SÓ em `.local/publicos/`, fora do Git.
**Para reproduzir:** baixe `HateBR.csv` (https://github.com/franciellevargas/HateBR) e `B2W-Reviews01.csv`
(https://github.com/americanas-tech/b2w-reviews01) para `.local/publicos/`; sem o cache, `avaliar.py` chama a
API de novo (chave em `TYPESAFE_API_KEY`) — é uma rodada nova, não a mesma.

```
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe avaliar/publicos/preparar.py
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe avaliar/publicos/avaliar.py teste   # do cache, sem chamada nova
```
