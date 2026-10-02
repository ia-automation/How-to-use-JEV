# Rascunho — juiz-de-eval (encanamento, não é métrica)

## Conjunto `rascunho` — 5 respostas (arquivo versão 2026-10-01, autor fable)

> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**

### Semânticos (9 critérios) — Jev × baseline, por desenho

`acerto_duro` = noul ≥ 0,5 × gabarito (sem faixa; gabarito nulo fora). `cobertura`/`acerto_decididos`/`revisa` = com a FAIXA (0.3, 0.8). `erro_caro` = gabarito false → `atende` (aprovou critério que a resposta não atende); `_duro` = o mesmo sem faixa. `nulo_em_revisa` = gabarito nulo que caiu na faixa do meio. `baseline` = palavras-chave do critério na resposta (negado inverte).

| desenho | n | acerto_duro | cobertura | acerto_decididos | revisa | erro_caro | erro_caro_duro | nulo_em_revisa | brier | baseline_acerto | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| um_por_requisicao | 9 | 1.000 | 0.889 | 1.000 | 1 | 0/0 | 0/0 | 0/0 | 0.010 | 0.667 | 0/0 |
| agrupado | 9 | 1.000 | 1.000 | 1.000 | 0 | 0/0 | 0/0 | 0/0 | 0.003 | 0.667 | 0/0 |

### Formais (4 critérios) — código × gabarito (tem de ser 100%; menos é bug)

Acerto 1.000 (4/4); 0 veredito(s) errado(s), 0 critério(s) não reconhecido(s) pela gramática (erro operacional, à parte).

| regra | n | acerto |
|---|---|---|
| emoji | 1 | 1.000 |
| frases | 1 | 1.000 |
| pergunta_final | 1 | 1.000 |
| reais | 1 | 1.000 |

### Veredito da resposta inteira (formais + semânticos) por desenho

Gabarito: `reprovada` = algum critério false; `aprovada` = todos true; `indecidivel` = há nulo e nenhum false. `ruim_aprovada` = o erro caro no nível da resposta.

| desenho | n | acerto | ruim_aprovada | ruim_em_revisa | boa_reprovada | boa_em_revisa | indecidivel_em_revisa |
|---|---|---|---|---|---|---|---|
| um_por_requisicao | 5 | 0.800 | 0/0 | 0/0 | 0/5 | 1/5 | 0/0 |
| agrupado | 5 | 1.000 | 0/0 | 0/0 | 0/5 | 0/5 | 0/0 |

### Cobertura × erro por faixa — `um_por_requisicao` (critério; e a composição da resposta à parte)

| faixa | cobertura | erro_decididos | revisa | erro_caro | nulo_em_revisa | ruim_aprovada (resposta) | acerto_resposta |
|---|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0/0 | 0/0 | 0/0 | 1.000 |
| 0.3–0.7 | 1.000 | 0.000 | 0 | 0/0 | 0/0 | 0/0 | 1.000 |
| 0.2–0.8 | 0.889 | 0.000 | 1 | 0/0 | 0/0 | 0/0 | 0.800 |
| 0.1–0.9 | 0.889 | 0.000 | 1 | 0/0 | 0/0 | 0/0 | 0.800 |
| 0.3–0.8 | 0.889 | 0.000 | 1 | 0/0 | 0/0 | 0/0 | 0.800 |
| 0.2–0.9 | 0.889 | 0.000 | 1 | 0/0 | 0/0 | 0/0 | 0.800 |
| 0.3–0.9 | 0.889 | 0.000 | 1 | 0/0 | 0/0 | 0/0 | 0.800 |

### Por família do critério e por dificuldade — `um_por_requisicao`

| familia | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| informa | 7 | 1.000 | 0/0 | 0 | 0.714 |
| nao_inventa | 1 | 1.000 | 0/0 | 1 | 1.000 |
| tom | 1 | 1.000 | 0/0 | 0 | 0.000 |

| dificil | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| False | 9 | 1.000 | 0/0 | 1 | 0.667 |

### Cobertura × erro por faixa — `agrupado` (critério; e a composição da resposta à parte)

| faixa | cobertura | erro_decididos | revisa | erro_caro | nulo_em_revisa | ruim_aprovada (resposta) | acerto_resposta |
|---|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.000 | 0 | 0/0 | 0/0 | 0/0 | 1.000 |
| 0.3–0.7 | 1.000 | 0.000 | 0 | 0/0 | 0/0 | 0/0 | 1.000 |
| 0.2–0.8 | 1.000 | 0.000 | 0 | 0/0 | 0/0 | 0/0 | 1.000 |
| 0.1–0.9 | 0.889 | 0.000 | 1 | 0/0 | 0/0 | 0/0 | 0.800 |
| 0.3–0.8 | 1.000 | 0.000 | 0 | 0/0 | 0/0 | 0/0 | 1.000 |
| 0.2–0.9 | 0.889 | 0.000 | 1 | 0/0 | 0/0 | 0/0 | 0.800 |
| 0.3–0.9 | 0.889 | 0.000 | 1 | 0/0 | 0/0 | 0/0 | 0.800 |

### Por família do critério e por dificuldade — `agrupado`

| familia | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| informa | 7 | 1.000 | 0/0 | 0 | 0.714 |
| nao_inventa | 1 | 1.000 | 0/0 | 0 | 1.000 |
| tom | 1 | 1.000 | 0/0 | 0 | 0.000 |

| dificil | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| False | 9 | 1.000 | 0/0 | 0 | 0.667 |

### Custo e latência (medidos na chamada real; do cache também)

Latência por REQUISIÇÃO; custo por resposta avaliada e por milhão de respostas / de vereditos semânticos. Os formais custam zero.

| desenho | requisicoes | req_por_resposta | p50_ms | p95_ms | tokens_por_resposta | US$_por_resposta | US$_por_milhao_respostas | US$_por_milhao_vereditos | modelo |
|---|---|---|---|---|---|---|---|---|---|
| um_por_requisicao | 9 | 1.800 | 354 | 436 | 1156 | 0.0000486 | 48.60 | 27.00 | jev-1.13.0 |
| agrupado | 5 | 1.000 | 324 | 408 | 902 | 0.0000380 | 38.00 | 21.11 | jev-1.13.0 |

### Caso a caso (desenho padrão `agrupado`; o outro entre parênteses)

Por critério: `noul` do Jev, veredito com faixa, gabarito, baseline. `erro` = veredito decidido ≠ gabarito, ou formal errado; `caro` = gabarito false aprovado.

| id | crit | tipo | critério | jev/regra | veredito | gab | marca | resposta |
|---|---|---|---|---|---|---|---|---|
| JE-R001 | c1 | sem | Informa que o imóvel aceita pet | 0.98 (0.96) · bl=F | atende | T | — | aprovada |
| JE-R001 | c2 | sem | Menciona a restrição de porte | 0.98 (0.98) · bl=T | atende | T | — |  |
| JE-R001 | c3 | for | Tem no máximo 3 frases | frases | atende | T | — |  |
| JE-R002 | c1 | sem | Informa que a visita precisa de agendamento prévio | 0.98 (0.98) · bl=T | atende | T | — | aprovada |
| JE-R002 | c2 | for | Termina com uma pergunta | pergunta_final | atende | T | — |  |
| JE-R003 | c1 | sem | Indica onde fica a opção de exportar | 0.97 (0.96) · bl=F | atende | T | — | aprovada |
| JE-R003 | c2 | sem | Menciona o formato do arquivo exportado | 0.97 (0.98) · bl=T | atende | T | — |  |
| JE-R003 | c3 | for | Não contém emoji | emoji | atende | T | — |  |
| JE-R004 | c1 | sem | Informa o valor do condomínio | 0.97 (0.96) · bl=T | atende | T | — | aprovada |
| JE-R004 | c2 | sem | Não inventa valor que não esteja no contexto | 0.86 (0.71) · bl=T | atende | T | — |  |
| JE-R004 | c3 | for | Contém um valor em reais no formato R$ | reais | atende | T | — |  |
| JE-R005 | c1 | sem | Responde em tom cordial | 0.98 (0.97) · bl=F | atende | T | — | aprovada |
| JE-R005 | c2 | sem | Explica que o financiamento é feito pelo banco, não pela imobiliária | 0.97 (0.97) · bl=T | atende | T | — |  |
