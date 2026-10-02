# Latência da interface — uma Choice cabe em 300 ms?

Item Z (reduzido) do briefing de 2026-10-01: mede, **ao vivo**, se uma Choice de 7 destinos sobre o texto de uma
barra de comando de CRM imobiliário cabe no gesto da interface. A alegação é **latência**; o acerto é
secundário (rótulo do próprio construtor, sem afinação). Números completos em [`resultados.md`](resultados.md),
gerado por `run.py`.

## O que mede
- `textos.py`: 66 textos curtos (10–80 caracteres) escritos à mão, 7 destinos (`buscar_cliente`, `buscar_imovel`,
  `criar_tarefa`, `abrir_relatorio`, `agendar_visita`, `enviar_mensagem`, `nenhum`), com os casos difíceis da
  spec (nome que é bairro, "visita" busca × agendamento, código × telefone, abreviação, texto colado).
- `perguntas.py`: UMA Choice de 7 opções, em inglês, com descrição por opção. State `{"text": <texto>}`.
- `run.py`: 210 chamadas em série e 210 com 4 em paralelo (os mesmos textos ciclados), hora local de início e
  fim, RTT TCP ao host da API, p50/p90/p95/p99/máximo por regime, tokens, custo e acerto bruto.
- **Critério fixado antes de rodar** (dicionário `CRITERIO` no `run.py`): cabe = p95 em série ≤ 300 ms **e** p95
  com 4 em paralelo ≤ 400 ms. O veredito é calculado pelo script.

Rodar: `JEV_MODO=ao_vivo python run.py` (exige chave; regrava `cache/`, a rodada anterior vai para
`cache/historico/`). `python run.py --n 10` só ensaia o encanamento.

## Condições (2026-10-02, 00:11–00:13 hora local, UTC−3)
Brasil, rede doméstica/fibra, uma máquina Windows; `jev-1.13.0`, SDK Python. RTT TCP a `api.typesafe.ai:443`
(ip 104.18.24.46, provavelmente borda de CDN): 16 ms de mediana — a latência da chamada é quase toda do
servidor, não da rede local.

## Resultado [testado, 420 chamadas, 0 falhas, US$ 0,011]
| regime | n | p50 | p90 | p95 | p99 | máx |
|---|---|---|---|---|---|---|
| série (1) | 210 | 248 ms | 291 ms | **303 ms** | 338 ms | 801 ms |
| 4 em paralelo | 210 | 251 ms | 299 ms | 320 ms | 763 ms | 12 344 ms |

**Cabe em 300 ms? Não cabe** — p95 em série deu 303 ms (critério ≤ 300). Por 3 ms, e o critério não se move
depois do teste. O p50 (~250 ms) cabe; os 4 em paralelo não mudaram o p50 nem o p95 de forma visível; o máximo
de 12,3 s no paralelo é um valor único, compatível com a retentativa interna do SDK (timeout de 10 s + nova
chamada), não com latência de uma chamada. Acerto bruto no rótulo do construtor: 0,933 (série) e 0,929
(paralelo); as confusões caem em `abrir_relatorio` ("leads que entraram hoje", "imóveis que já receberam
visita") — não foi afinado e não é o objeto da medição.

## Limites
- Uma máquina, uma hora do dia (madrugada), uma rede, uma versão do modelo, textos do próprio construtor.
- 639 tokens de entrada por chamada (a Choice com descrições é a maior parte); outra pergunta, outro tempo.
- O SDK retenta 408/429/5xx e timeout por conta própria: p99 e máximo podem conter retentativas.
- Latência medida em volta da chamada HTTP pelo `jevcache`, sem o I/O do cache nem o tempo da interface.
