# Latência da interface — resultados

Gerado por `run.py` em 2026-10-02 00:13:11 Hora padrão América do Sul Or. (UTC-0300); modelo `jev-1.13.0`; modo `ao_vivo`. Latência = tempo da chamada HTTP medido pelo `jevcache` (sem o I/O do cache); hora local da máquina.

## Condições declaradas
- Rede: Brasil, rede doméstica/fibra — informar o que o ambiente permitir ver.
- RTT base (conexão TCP a `api.typesafe.ai`:443, ip 104.18.24.46 — é o host resolvido, possivelmente uma borda de CDN, não o servidor que responde; 5 amostras): mínimo 15.8 ms, mediana 16.0 ms (21.7, 16.1, 16.0, 15.8, 15.9).
- Textos: 66 (`textos.py`, do construtor), ciclados; uma Choice de 7 opções por chamada.
- Critério fixado antes: cabe em 300 ms? = p95 em série ≤ 300 ms E p95 com 4 em paralelo ≤ 400 ms.

## Latência por regime (ms)
| regime | chamadas | início | fim | duração | p50 | p90 | p95 | p99 | máx | mín |
|---|---|---|---|---|---|---|---|---|---|---|
| série (1) | 210/210 | 00:11:55 | 00:12:49 | 54.9 s | 248 | 291 | 303 | 338 | 801 | 229 |
| paralelo (4) | 210/210 | 00:12:49 | 00:13:11 | 22.0 s | 251 | 299 | 320 | 763 | 12344 | 224 |

**cabe em 300 ms? NÃO CABE** — p95 em série 303 ms > 300 ms.

## Custo
- Chamadas: 420 (orçamento 450); tokens de entrada 268578 (639 por chamada); custo US$ 0.01128 (US$ 0.042/M de entrada; saída não cobrada).
- Falhas operacionais: 0.

## Acerto bruto no rótulo do construtor (secundário)
- Série: 0.933 (n = 210); paralelo: 0.929 (n = 210). Rótulo do próprio construtor, sem afinação: diz que a resposta não é aleatória, não mede desempenho.

| destino | acertos/n (série) | acertos/n (paralelo) |
|---|---|---|
| `buscar_cliente` | 36/40 | 36/40 |
| `buscar_imovel` | 29/32 | 29/32 |
| `criar_tarefa` | 24/27 | 24/27 |
| `abrir_relatorio` | 27/27 | 27/27 |
| `agendar_visita` | 27/27 | 27/27 |
| `enviar_mensagem` | 26/27 | 25/27 |
| `nenhum` | 27/30 | 27/30 |

Confusões mais frequentes (rótulo → resposta, nas duas rodadas): `buscar_cliente` → `abrir_relatorio` ×8; `buscar_imovel` → `abrir_relatorio` ×6; `nenhum` → `buscar_imovel` ×6; `criar_tarefa` → `buscar_imovel` ×5; `enviar_mensagem` → `nenhum` ×3; `criar_tarefa` → `nenhum` ×1.

## Limites
- Uma máquina, uma hora do dia, uma rede, uma versão do modelo, textos do próprio construtor.
- O SDK refaz chamada em 429/5xx/timeout por conta própria (até 2 vezes, com espera): um valor alto isolado pode ser retentativa, não latência de uma chamada.
- Em `ao_vivo` a resposta anterior de cada texto vai para `cache/historico/`; o custo de mover arquivo não entra na latência.
