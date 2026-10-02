# Resultados — juiz-de-eval

Gerado por `run.py` em 2026-10-01 (modo `gravado`; modelo e amostra em cada seção). Pergunta, faixa e baseline: `perguntas.py`; regras formais: `juiz.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Desenho padrão: `agrupado`; FAIXA (0.3, 0.8).

Critério de continuar/descartar (fixado antes do teste): no teste, com o desenho padrão e a FAIXA acima: (1) formais: 100% (menos é bug de código); (2) semantico duro: acerto duro (noul ≥ 0,5, gabarito não nulo) ≥ baseline + 15 p.p.; (3) erro caro: ≤ 5% dos critérios semânticos com gabarito false (gabarito false → `atende`); (4) resposta ruim aprovada: nenhuma resposta com algum critério false aprovada inteira (`aprovada` com gabarito reprovada).

Versão congelada (manifesto `congelamento.json`, gravado em 2026-10-01T11:47:21-03:00; cega ou não, conforme a rodada declarada no README): `perguntas.py` sha256 2d6512fb6a1477fb… · `juiz.py` sha256 c9fffbb643f30103… · `dados/teste.json` sha256 4bd70634a250741c…

## Lado a lado

### Semânticos — Jev × baseline

| conjunto | desenho | n_sem | acerto_duro | baseline | cobertura | acerto_decididos | erro_caro | baseline_erro_caro | brier | formais |
|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | um_por_requisicao | 55 | 0.982 | 0.582 | 0.945 | 1.000 | 0/17 | 5/17 | 0.014 | 19/19 |
| ajuste | agrupado | 55 | 0.982 | 0.582 | 0.945 | 1.000 | 0/17 | 5/17 | 0.014 | 19/19 |
| teste | um_por_requisicao | 99 | 0.970 | 0.596 | 0.939 | 0.989 | 0/34 | 14/34 | 0.025 | 35/35 |
| teste | agrupado | 99 | 0.970 | 0.596 | 0.939 | 1.000 | 0/34 | 14/34 | 0.020 | 35/35 |

### Resposta inteira, latência e custo

| conjunto | desenho | n | acerto_resposta | ruim_aprovada | ruim_em_revisa | boa_em_revisa | p50_ms | p95_ms | US$_por_resposta | US$_por_milhao_respostas | US$_por_milhao_vereditos | modelo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ajuste | um_por_requisicao | 30 | 0.966 | 0/17 | 1/17 | 0/12 | 261 | 354 | 0.0000491 | 49.13 | 25.41 | jev-1.13.0 |
| ajuste | agrupado | 30 | 0.966 | 0/17 | 1/17 | 0/12 | 271 | 340 | 0.0000381 | 38.10 | 19.71 | jev-1.13.0 |
| teste | um_por_requisicao | 57 | 0.982 | 0/33 | 0/33 | 1/22 | 250 | 314 | 0.0000469 | 46.95 | 25.73 | jev-1.13.0 |
| teste | agrupado | 57 | 0.964 | 0/33 | 1/33 | 1/22 | 258 | 320 | 0.0000369 | 36.93 | 20.24 | jev-1.13.0 |

## Conjunto `ajuste` — 30 respostas (arquivo versão 2026-10-01, autor fable)

### Semânticos (58 critérios) — Jev × baseline, por desenho

`acerto_duro` = noul ≥ 0,5 × gabarito (sem faixa; gabarito nulo fora). `cobertura`/`acerto_decididos`/`revisa` = com a FAIXA (0.3, 0.8). `erro_caro` = gabarito false → `atende` (aprovou critério que a resposta não atende); `_duro` = o mesmo sem faixa. `nulo_em_revisa` = gabarito nulo que caiu na faixa do meio. `baseline` = palavras-chave do critério na resposta (negado inverte).

| desenho | n | acerto_duro | cobertura | acerto_decididos | revisa | erro_caro | erro_caro_duro | nulo_em_revisa | brier | baseline_acerto | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| um_por_requisicao | 55 | 0.982 | 0.945 | 1.000 | 3 | 0/17 | 1/17 | 3/3 | 0.014 | 0.582 | 5/17 |
| agrupado | 55 | 0.982 | 0.945 | 1.000 | 3 | 0/17 | 1/17 | 3/3 | 0.014 | 0.582 | 5/17 |

### Formais (19 critérios) — código × gabarito (tem de ser 100%; menos é bug)

Acerto 1.000 (19/19); 0 veredito(s) errado(s), 0 critério(s) não reconhecido(s) pela gramática (erro operacional, à parte).

| regra | n | acerto |
|---|---|---|
| emoji | 1 | 1.000 |
| frases | 10 | 1.000 |
| horario | 2 | 1.000 |
| link | 1 | 1.000 |
| palavra | 2 | 1.000 |
| pergunta_final | 1 | 1.000 |
| reais | 2 | 1.000 |

### Veredito da resposta inteira (formais + semânticos) por desenho

Gabarito: `reprovada` = algum critério false; `aprovada` = todos true; `indecidivel` = há nulo e nenhum false. `ruim_aprovada` = o erro caro no nível da resposta.

| desenho | n | acerto | ruim_aprovada | ruim_em_revisa | boa_reprovada | boa_em_revisa | indecidivel_em_revisa |
|---|---|---|---|---|---|---|---|
| um_por_requisicao | 30 | 0.966 | 0/17 | 1/17 | 0/12 | 0/12 | 1/1 |
| agrupado | 30 | 0.966 | 0/17 | 1/17 | 0/12 | 0/12 | 1/1 |

### Cobertura × erro por faixa — `um_por_requisicao` (critério; e a composição da resposta à parte)

| faixa | cobertura | erro_decididos | revisa | erro_caro | nulo_em_revisa | ruim_aprovada (resposta) | acerto_resposta |
|---|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.018 | 0 | 1/17 | 3/3 | 1/17 | 0.966 |
| 0.3–0.7 | 0.964 | 0.000 | 2 | 0/17 | 3/3 | 0/17 | 0.966 |
| 0.2–0.8 | 0.927 | 0.000 | 4 | 0/17 | 3/3 | 0/17 | 0.966 |
| 0.1–0.9 | 0.818 | 0.000 | 10 | 0/17 | 3/3 | 0/17 | 0.828 |
| 0.3–0.8 | 0.945 | 0.000 | 3 | 0/17 | 3/3 | 0/17 | 0.966 |
| 0.2–0.9 | 0.836 | 0.000 | 9 | 0/17 | 3/3 | 0/17 | 0.862 |
| 0.3–0.9 | 0.855 | 0.000 | 8 | 0/17 | 3/3 | 0/17 | 0.862 |

### Por família do critério e por dificuldade — `um_por_requisicao`

| familia | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| informa | 22 | 1.000 | 0/2 | 1 | 0.682 |
| nao_inventa | 5 | 1.000 | 0/4 | 0 | 0.400 |
| negado | 6 | 1.000 | 0/3 | 0 | 0.667 |
| oferece | 10 | 1.000 | 0/3 | 0 | 0.600 |
| responde | 6 | 0.833 | 0/4 | 1 | 0.667 |
| tom | 6 | 1.000 | 0/1 | 1 | 0.167 |

| dificil | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| False | 14 | 1.000 | 0/0 | 0 | 0.571 |
| True | 41 | 0.976 | 0/17 | 3 | 0.585 |

### Cobertura × erro por faixa — `agrupado` (critério; e a composição da resposta à parte)

| faixa | cobertura | erro_decididos | revisa | erro_caro | nulo_em_revisa | ruim_aprovada (resposta) | acerto_resposta |
|---|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.018 | 0 | 1/17 | 3/3 | 1/17 | 0.966 |
| 0.3–0.7 | 0.964 | 0.000 | 2 | 0/17 | 3/3 | 0/17 | 0.966 |
| 0.2–0.8 | 0.909 | 0.000 | 5 | 0/17 | 3/3 | 0/17 | 0.966 |
| 0.1–0.9 | 0.855 | 0.000 | 8 | 0/17 | 3/3 | 0/17 | 0.862 |
| 0.3–0.8 | 0.945 | 0.000 | 3 | 0/17 | 3/3 | 0/17 | 0.966 |
| 0.2–0.9 | 0.891 | 0.000 | 6 | 0/17 | 3/3 | 0/17 | 0.931 |
| 0.3–0.9 | 0.927 | 0.000 | 4 | 0/17 | 3/3 | 0/17 | 0.931 |

### Por família do critério e por dificuldade — `agrupado`

| familia | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| informa | 22 | 1.000 | 0/2 | 0 | 0.682 |
| nao_inventa | 5 | 1.000 | 0/4 | 0 | 0.400 |
| negado | 6 | 1.000 | 0/3 | 1 | 0.667 |
| oferece | 10 | 1.000 | 0/3 | 0 | 0.600 |
| responde | 6 | 0.833 | 0/4 | 1 | 0.667 |
| tom | 6 | 1.000 | 0/1 | 1 | 0.167 |

| dificil | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| False | 14 | 1.000 | 0/0 | 0 | 0.571 |
| True | 41 | 0.976 | 0/17 | 3 | 0.585 |

### Custo e latência (medidos na chamada real; do cache também)

Latência por REQUISIÇÃO; custo por resposta avaliada e por milhão de respostas / de vereditos semânticos. Os formais custam zero.

| desenho | requisicoes | req_por_resposta | p50_ms | p95_ms | tokens_por_resposta | US$_por_resposta | US$_por_milhao_respostas | US$_por_milhao_vereditos | modelo |
|---|---|---|---|---|---|---|---|---|---|
| um_por_requisicao | 55 | 1.830 | 261 | 354 | 1170 | 0.0000491 | 49.13 | 25.41 | jev-1.13.0 |
| agrupado | 30 | 1.000 | 271 | 340 | 907 | 0.0000381 | 38.10 | 19.71 | jev-1.13.0 |

### Caso a caso (desenho padrão `agrupado`; o outro entre parênteses)

Por critério: `noul` do Jev, veredito com faixa, gabarito, baseline. `erro` = veredito decidido ≠ gabarito, ou formal errado; `caro` = gabarito false aprovado.

| id | crit | tipo | critério | jev/regra | veredito | gab | marca | resposta |
|---|---|---|---|---|---|---|---|---|
| JE-A001 | c1 | sem | Informa que o imóvel tem vaga | 0.99 (0.97) · bl=T | atende | T | — | aprovada |
| JE-A001 | c2 | sem | Especifica se a vaga é coberta | 0.98 (0.98) · bl=T | atende | T | — |  |
| JE-A001 | c3 | for | Tem no máximo 2 frases | frases | atende | T | — |  |
| JE-A002 | c1 | sem | Informa que a visita precisa de agendamento prévio | 0.83 (0.85) · bl=F | atende | T | — | aprovada |
| JE-A002 | c2 | sem | Oferece horários concretos | 0.96 (0.95) · bl=F | atende | T | — |  |
| JE-A002 | c3 | for | Termina com uma pergunta | pergunta_final | atende | T | — |  |
| JE-A003 | c1 | sem | Informa o número de quartos | 0.98 (0.96) · bl=T | atende | T | — | reprovada |
| JE-A003 | c2 | sem | Informa que não há vaga | 0.95 (0.94) · bl=T | atende | T | — |  |
| JE-A003 | c3 | sem | Não inventa característica que não esteja no contexto | 0.05 (0.04) · bl=T | nao_atende | F | — |  |
| JE-A003 | c4 | for | Tem no máximo 3 frases | frases | atende | T | — |  |
| JE-A004 | c1 | sem | Não promete desconto | 0.03 (0.03) · bl=T | nao_atende | F | — | reprovada |
| JE-A004 | c2 | sem | Oferece encaminhar proposta ao proprietário | 0.10 (0.05) · bl=F | nao_atende | F | — |  |
| JE-A004 | c3 | sem | Responde em tom cordial | 0.79 (0.88) · bl=F | revisa | T | — |  |
| JE-A005 | c1 | sem | Não promete desconto | 0.97 (0.97) · bl=F | atende | T | — | aprovada |
| JE-A005 | c2 | sem | Oferece encaminhar proposta ao proprietário | 0.98 (0.98) · bl=T | atende | T | — |  |
| JE-A005 | c3 | sem | Responde em tom cordial | 0.90 (0.92) · bl=F | atende | T | — |  |
| JE-A006 | c1 | sem | Informa que o imóvel aceita financiamento | 0.97 (0.92) · bl=T | atende | T | — | reprovada |
| JE-A006 | c2 | for | Tem no máximo 3 frases | frases | nao_atende | F | — |  |
| JE-A006 | c3 | sem | Responde à pergunta feita | 0.95 (0.88) · bl=T | atende | T | — |  |
| JE-A007 | c1 | sem | Responde se o condomínio tem piscina | 0.03 (0.03) · bl=T | nao_atende | F | — | reprovada |
| JE-A007 | c2 | sem | Responde em tom cordial | 0.95 (0.92) · bl=F | atende | T | — |  |
| JE-A008 | c1 | sem | Responde se há elevador | 0.98 (0.97) · bl=F | atende | T | — | reprovada |
| JE-A008 | c2 | for | Tem no máximo 3 frases | frases | nao_atende | F | — |  |
| JE-A009 | c1 | sem | Informa o valor do IPTU | 0.97 (0.96) · bl=T | atende | T | — | revisa |
| JE-A009 | c2 | sem | Não inventa valor que não esteja no contexto | sem contexto (código, sem chamada) · bl=T | revisa | null | — |  |
| JE-A009 | c3 | for | Contém um valor em reais no formato R$ | reais | atende | T | — |  |
| JE-A010 | c1 | sem | Explica como mover o lead de etapa | 0.98 (0.97) · bl=T | atende | T | — | aprovada |
| JE-A010 | c2 | sem | Menciona arrastar o card ou trocar pelo campo de etapa | 0.98 (0.98) · bl=T | atende | T | — |  |
| JE-A010 | c3 | for | Tem no máximo 4 frases | frases | atende | T | — |  |
| JE-A011 | c1 | sem | Responde em tom cordial | 0.96 (0.95) · bl=F | atende | T | — | aprovada |
| JE-A011 | c2 | sem | Pede um detalhe para diagnosticar (tela, mensagem, navegador) | 0.96 (0.95) · bl=F | atende | T | — |  |
| JE-A011 | c3 | sem | Não culpa o usuário | 0.97 (0.96) · bl=T | atende | T | — |  |
| JE-A012 | c1 | sem | Responde em tom cordial | 0.29 (0.42) · bl=F | nao_atende | F | — | reprovada |
| JE-A012 | c2 | sem | Pede um detalhe para diagnosticar (tela, mensagem, navegador) | 0.08 (0.06) · bl=F | nao_atende | F | — |  |
| JE-A012 | c3 | sem | Não culpa o usuário | 0.35 (0.09) · bl=F | revisa | F | — |  |
| JE-A013 | c1 | sem | Informa que o imóvel não aceita pet | 0.95 (0.88) · bl=F | atende | T | — | aprovada |
| JE-A013 | c2 | sem | Oferece alternativa (outro imóvel) | 0.93 (0.93) · bl=F | atende | T | — |  |
| JE-A014 | c1 | sem | Informa que aceita pet | 0.96 (0.74) · bl=T | atende | T | — | reprovada |
| JE-A014 | c2 | sem | Não inventa restrição que não esteja no contexto | 0.03 (0.03) · bl=T | nao_atende | F | — |  |
| JE-A015 | c1 | for | Contém a palavra 'Palmeiras' | palavra | atende | T | — | aprovada |
| JE-A015 | c2 | for | Contém um horário (10h ou 10:00) | horario | atende | T | — |  |
| JE-A015 | c3 | sem | Confirma a visita de sábado | 0.98 (0.97) · bl=T | atende | T | — |  |
| JE-A016 | c1 | for | Contém a palavra 'Palmeiras' | palavra | nao_atende | F | — | reprovada |
| JE-A016 | c2 | for | Contém um horário (10h ou 10:00) | horario | nao_atende | F | — |  |
| JE-A016 | c3 | sem | Confirma a visita de sábado | 0.95 (0.93) · bl=T | atende | T | — |  |
| JE-A017 | c1 | sem | Responde se o condomínio está incluído no aluguel | 0.03 (0.03) · bl=F | nao_atende | F | — | reprovada |
| JE-A017 | c2 | sem | Não inventa valor que não esteja no contexto | sem contexto (código, sem chamada) · bl=T | revisa | null | — |  |
| JE-A018 | c1 | sem | Responde se pode levar o animal na visita | 0.54 (0.52) · bl=F | revisa | F | — | revisa |
| JE-A018 | c2 | for | Tem no máximo 2 frases | frases | atende | T | — |  |
| JE-A019 | c1 | sem | Não garante aceitação do proprietário | 0.93 (0.93) · bl=T | atende | T | — | aprovada |
| JE-A019 | c2 | sem | Convida a enviar proposta | 0.97 (0.96) · bl=T | atende | T | — |  |
| JE-A020 | c1 | sem | Não garante aceitação do proprietário | 0.16 (0.08) · bl=F | nao_atende | F | — | reprovada |
| JE-A020 | c2 | sem | Convida a enviar proposta | 0.93 (0.94) · bl=F | atende | T | — |  |
| JE-A021 | c1 | for | Contém um link (http) | link | atende | T | — | aprovada |
| JE-A021 | c2 | sem | Indica onde encontrar o tutorial | 0.97 (0.97) · bl=F | atende | T | — |  |
| JE-A022 | c1 | sem | Informa que tem churrasqueira | 0.99 (0.98) · bl=F | atende | T | — | reprovada |
| JE-A022 | c2 | for | Não contém emoji | emoji | nao_atende | F | — |  |
| JE-A023 | c1 | sem | Informa que a visita precisa de agendamento | 0.98 (0.98) · bl=T | atende | T | — | reprovada |
| JE-A023 | c2 | for | Tem no máximo 3 frases | frases | nao_atende | F | — |  |
| JE-A023 | c3 | sem | Não inventa horário de funcionamento | sem contexto (código, sem chamada) · bl=T | revisa | null | — |  |
| JE-A024 | c1 | sem | Responde se está disponível | 0.03 (0.03) · bl=F | nao_atende | F | — | reprovada |
| JE-A024 | c2 | sem | Responde em tom cordial | 0.96 (0.94) · bl=F | atende | T | — |  |
| JE-A025 | c1 | sem | Informa que o imóvel é de fundos (não é de frente) | 0.95 (0.90) · bl=F | atende | T | — | reprovada |
| JE-A025 | c2 | sem | Não inventa característica que não esteja no contexto | 0.12 (0.14) · bl=T | nao_atende | F | — |  |
| JE-A026 | c1 | for | Contém um valor em reais no formato R$ | reais | atende | T | — | aprovada |
| JE-A026 | c2 | for | Tem no máximo 2 frases | frases | atende | T | — |  |
| JE-A026 | c3 | sem | Informa o valor | 0.96 (0.85) · bl=T | atende | T | — |  |
| JE-A027 | c1 | sem | Informa que a recuperação é possível | 0.99 (0.98) · bl=F | atende | T | — | aprovada |
| JE-A027 | c2 | sem | Explica onde ou como recuperar | 0.96 (0.97) · bl=F | atende | T | — |  |
| JE-A027 | c3 | for | Tem no máximo 3 frases | frases | atende | T | — |  |
| JE-A028 | c1 | sem | Informa que a recuperação é possível | 0.24 (0.24) · bl=F | nao_atende | F | — | reprovada |
| JE-A028 | c2 | sem | Explica onde ou como recuperar | 0.04 (0.04) · bl=F | nao_atende | F | — |  |
| JE-A028 | c3 | for | Tem no máximo 3 frases | frases | atende | T | — |  |
| JE-A029 | c1 | sem | Não afirma que a vaga é coberta sem base no contexto | 0.07 (0.04) · bl=F | nao_atende | F | — | reprovada |
| JE-A029 | c2 | sem | Oferece confirmar com o proprietário | 0.08 (0.05) · bl=F | nao_atende | F | — |  |
| JE-A030 | c1 | sem | Não afirma que a vaga é coberta sem base no contexto | 0.98 (0.98) · bl=T | atende | T | — | aprovada |
| JE-A030 | c2 | sem | Oferece confirmar com o proprietário | 0.97 (0.98) · bl=T | atende | T | — |  |

## Conjunto `teste` — 57 respostas (arquivo versão 2026-10-01, autor fable)

### Semânticos (104 critérios) — Jev × baseline, por desenho

`acerto_duro` = noul ≥ 0,5 × gabarito (sem faixa; gabarito nulo fora). `cobertura`/`acerto_decididos`/`revisa` = com a FAIXA (0.3, 0.8). `erro_caro` = gabarito false → `atende` (aprovou critério que a resposta não atende); `_duro` = o mesmo sem faixa. `nulo_em_revisa` = gabarito nulo que caiu na faixa do meio. `baseline` = palavras-chave do critério na resposta (negado inverte).

| desenho | n | acerto_duro | cobertura | acerto_decididos | revisa | erro_caro | erro_caro_duro | nulo_em_revisa | brier | baseline_acerto | baseline_erro_caro |
|---|---|---|---|---|---|---|---|---|---|---|---|
| um_por_requisicao | 99 | 0.970 | 0.939 | 0.989 | 6 | 0/34 | 0/34 | 4/5 | 0.025 | 0.596 | 14/34 |
| agrupado | 99 | 0.970 | 0.939 | 1.000 | 6 | 0/34 | 1/34 | 4/5 | 0.020 | 0.596 | 14/34 |

### Formais (35 critérios) — código × gabarito (tem de ser 100%; menos é bug)

Acerto 1.000 (35/35); 0 veredito(s) errado(s), 0 critério(s) não reconhecido(s) pela gramática (erro operacional, à parte).

| regra | n | acerto |
|---|---|---|
| emoji | 1 | 1.000 |
| frases | 19 | 1.000 |
| horario | 3 | 1.000 |
| link | 3 | 1.000 |
| palavra | 2 | 1.000 |
| pergunta_final | 3 | 1.000 |
| reais | 4 | 1.000 |

### Veredito da resposta inteira (formais + semânticos) por desenho

Gabarito: `reprovada` = algum critério false; `aprovada` = todos true; `indecidivel` = há nulo e nenhum false. `ruim_aprovada` = o erro caro no nível da resposta.

| desenho | n | acerto | ruim_aprovada | ruim_em_revisa | boa_reprovada | boa_em_revisa | indecidivel_em_revisa |
|---|---|---|---|---|---|---|---|
| um_por_requisicao | 57 | 0.982 | 0/33 | 0/33 | 0/22 | 1/22 | 1/2 |
| agrupado | 57 | 0.964 | 0/33 | 1/33 | 0/22 | 1/22 | 1/2 |

### Cobertura × erro por faixa — `um_por_requisicao` (critério; e a composição da resposta à parte)

| faixa | cobertura | erro_decididos | revisa | erro_caro | nulo_em_revisa | ruim_aprovada (resposta) | acerto_resposta |
|---|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.030 | 0 | 0/34 | 4/5 | 0/33 | 1.000 |
| 0.3–0.7 | 0.939 | 0.011 | 6 | 0/34 | 4/5 | 0/33 | 0.982 |
| 0.2–0.8 | 0.899 | 0.000 | 10 | 0/34 | 4/5 | 0/33 | 0.964 |
| 0.1–0.9 | 0.848 | 0.000 | 15 | 0/34 | 4/5 | 0/33 | 0.927 |
| 0.3–0.8 | 0.939 | 0.011 | 6 | 0/34 | 4/5 | 0/33 | 0.982 |
| 0.2–0.9 | 0.848 | 0.000 | 15 | 0/34 | 4/5 | 0/33 | 0.927 |
| 0.3–0.9 | 0.889 | 0.011 | 11 | 0/34 | 4/5 | 0/33 | 0.945 |

### Por família do critério e por dificuldade — `um_por_requisicao`

| familia | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| informa | 44 | 0.977 | 0/8 | 3 | 0.705 |
| nao_inventa | 14 | 0.929 | 0/9 | 1 | 0.429 |
| negado | 10 | 1.000 | 0/6 | 1 | 0.300 |
| oferece | 10 | 1.000 | 0/5 | 1 | 1.000 |
| outra | 4 | 1.000 | 0/1 | 0 | 0.250 |
| responde | 8 | 1.000 | 0/4 | 0 | 0.875 |
| tom | 9 | 0.889 | 0/1 | 0 | 0.111 |

| dificil | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| False | 28 | 1.000 | 0/3 | 0 | 0.679 |
| True | 71 | 0.958 | 0/31 | 6 | 0.563 |

### Cobertura × erro por faixa — `agrupado` (critério; e a composição da resposta à parte)

| faixa | cobertura | erro_decididos | revisa | erro_caro | nulo_em_revisa | ruim_aprovada (resposta) | acerto_resposta |
|---|---|---|---|---|---|---|---|
| 0.5–0.5 | 1.000 | 0.030 | 0 | 1/34 | 4/5 | 0/33 | 1.000 |
| 0.3–0.7 | 0.939 | 0.000 | 6 | 0/34 | 4/5 | 0/33 | 0.964 |
| 0.2–0.8 | 0.919 | 0.000 | 8 | 0/34 | 4/5 | 0/33 | 0.964 |
| 0.1–0.9 | 0.869 | 0.000 | 13 | 0/34 | 4/5 | 0/33 | 0.945 |
| 0.3–0.8 | 0.939 | 0.000 | 6 | 0/34 | 4/5 | 0/33 | 0.964 |
| 0.2–0.9 | 0.909 | 0.000 | 9 | 0/34 | 4/5 | 0/33 | 0.964 |
| 0.3–0.9 | 0.929 | 0.000 | 7 | 0/34 | 4/5 | 0/33 | 0.964 |

### Por família do critério e por dificuldade — `agrupado`

| familia | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| informa | 44 | 1.000 | 0/8 | 2 | 0.705 |
| nao_inventa | 14 | 0.929 | 0/9 | 1 | 0.429 |
| negado | 10 | 0.900 | 0/6 | 2 | 0.300 |
| oferece | 10 | 1.000 | 0/5 | 0 | 1.000 |
| outra | 4 | 1.000 | 0/1 | 0 | 0.250 |
| responde | 8 | 1.000 | 0/4 | 0 | 0.875 |
| tom | 9 | 0.889 | 0/1 | 1 | 0.111 |

| dificil | n | acerto_duro | erro_caro | revisa | baseline |
|---|---|---|---|---|---|
| False | 28 | 1.000 | 0/3 | 0 | 0.679 |
| True | 71 | 0.958 | 0/31 | 6 | 0.563 |

### Custo e latência (medidos na chamada real; do cache também)

Latência por REQUISIÇÃO; custo por resposta avaliada e por milhão de respostas / de vereditos semânticos. Os formais custam zero.

| desenho | requisicoes | req_por_resposta | p50_ms | p95_ms | tokens_por_resposta | US$_por_resposta | US$_por_milhao_respostas | US$_por_milhao_vereditos | modelo |
|---|---|---|---|---|---|---|---|---|---|
| um_por_requisicao | 100 | 1.750 | 250 | 314 | 1118 | 0.0000469 | 46.95 | 25.73 | jev-1.13.0 |
| agrupado | 57 | 1.000 | 258 | 320 | 879 | 0.0000369 | 36.93 | 20.24 | jev-1.13.0 |

### Caso a caso (desenho padrão `agrupado`; o outro entre parênteses)

Por critério: `noul` do Jev, veredito com faixa, gabarito, baseline. `erro` = veredito decidido ≠ gabarito, ou formal errado; `caro` = gabarito false aprovado.

| id | crit | tipo | critério | jev/regra | veredito | gab | marca | resposta |
|---|---|---|---|---|---|---|---|---|
| JE-T001 | c1 | sem | Informa o número de banheiros | 0.98 (0.98) · bl=T | atende | T | — | aprovada |
| JE-T001 | c2 | for | Tem no máximo 2 frases | frases | atende | T | — |  |
| JE-T002 | c1 | sem | Informa que a visita precisa de agendamento prévio | 0.95 (0.94) · bl=F | atende | T | — | aprovada |
| JE-T002 | c2 | for | Termina com uma pergunta | pergunta_final | atende | T | — |  |
| JE-T003 | c1 | sem | Informa que a visita precisa de agendamento prévio | 0.02 (0.02) · bl=F | nao_atende | F | — | reprovada |
| JE-T003 | c2 | for | Termina com uma pergunta | pergunta_final | nao_atende | F | — |  |
| JE-T004 | c1 | sem | Informa quartos, vagas e área | 0.96 (0.88) · bl=F | atende | T | — | reprovada |
| JE-T004 | c2 | sem | Não inventa característica que não esteja no contexto | 0.04 (0.03) · bl=T | nao_atende | F | — |  |
| JE-T004 | c3 | for | Tem no máximo 3 frases | frases | atende | T | — |  |
| JE-T005 | c1 | sem | Não promete parcelamento da entrada | 0.05 (0.03) · bl=T | nao_atende | F | — | reprovada |
| JE-T005 | c2 | sem | Encaminha a dúvida ao proprietário ou ao banco | 0.05 (0.04) · bl=F | nao_atende | F | — |  |
| JE-T006 | c1 | sem | Não promete parcelamento da entrada | 0.95 (0.95) · bl=T | atende | T | — | aprovada |
| JE-T006 | c2 | sem | Encaminha a dúvida ao proprietário ou ao banco | 0.95 (0.92) · bl=F | atende | T | — |  |
| JE-T007 | c1 | sem | Não afirma que há vaga de moto | 0.97 (0.98) · bl=F | atende | T | — | reprovada |
| JE-T007 | c2 | for | Tem no máximo 3 frases | frases | nao_atende | F | — |  |
| JE-T007 | c3 | sem | Oferece confirmar | 0.98 (0.97) · bl=T | atende | T | — |  |
| JE-T008 | c1 | sem | Responde se o proprietário aceita permuta | 0.12 (0.10) · bl=F | nao_atende | F | — | reprovada |
| JE-T008 | c2 | sem | Responde em tom cordial | 0.94 (0.95) · bl=F | atende | T | — |  |
| JE-T009 | c1 | sem | Responde se há portaria 24h | 0.97 (0.97) · bl=T | atende | T | — | reprovada |
| JE-T009 | c2 | for | Tem no máximo 3 frases | frases | nao_atende | F | — |  |
| JE-T010 | c1 | sem | Informa o valor do condomínio | 0.98 (0.98) · bl=F | atende | T | — | revisa |
| JE-T010 | c2 | sem | Não inventa valor que não esteja no contexto | sem contexto (código, sem chamada) · bl=T | revisa | null | — |  |
| JE-T010 | c3 | for | Contém um valor em reais no formato R$ | reais | atende | T | — |  |
| JE-T011 | c1 | sem | Indica o caminho nas configurações | 0.97 (0.96) · bl=F | atende | T | — | aprovada |
| JE-T011 | c2 | sem | Menciona os tipos de campo disponíveis | 0.98 (0.98) · bl=F | atende | T | — |  |
| JE-T011 | c3 | for | Tem no máximo 4 frases | frases | atende | T | — |  |
| JE-T012 | c1 | sem | Indica o caminho nas configurações | 0.16 (0.10) · bl=T | nao_atende | F | — | reprovada |
| JE-T012 | c2 | sem | Menciona os tipos de campo disponíveis | 0.03 (0.03) · bl=F | nao_atende | F | — |  |
| JE-T012 | c3 | for | Tem no máximo 4 frases | frases | atende | T | — |  |
| JE-T013 | c1 | sem | Responde em tom cordial | 0.96 (0.96) · bl=F | atende | T | — | reprovada |
| JE-T013 | c2 | sem | Reconhece o problema recorrente | 0.95 (0.97) · bl=F | atende | T | — |  |
| JE-T013 | c3 | sem | Não promete prazo de correção | 0.03 (0.02) · bl=T | nao_atende | F | — |  |
| JE-T014 | c1 | sem | Responde em tom cordial | 0.97 (0.97) · bl=F | atende | T | — | aprovada |
| JE-T014 | c2 | sem | Reconhece o problema recorrente | 0.97 (0.97) · bl=F | atende | T | — |  |
| JE-T014 | c3 | sem | Não promete prazo de correção | 0.92 (0.93) · bl=T | atende | T | — |  |
| JE-T015 | c1 | sem | Informa que não aceita pet | 0.97 (0.95) · bl=T | atende | T | — | aprovada |
| JE-T015 | c2 | sem | Responde em tom cordial | 0.91 (0.89) · bl=F | atende | T | — |  |
| JE-T016 | c1 | sem | Informa que aceita pet | 0.94 (0.61) · bl=T | atende | T | — | reprovada |
| JE-T016 | c2 | sem | Não inventa restrição que não esteja no contexto | 0.03 (0.03) · bl=T | nao_atende | F | — |  |
| JE-T017 | c1 | for | Contém a palavra 'Brasil' | palavra | atende | T | — | aprovada |
| JE-T017 | c2 | for | Contém um horário (14h ou 14:00) | horario | atende | T | — |  |
| JE-T017 | c3 | sem | Confirma a visita de quinta | 0.95 (0.92) · bl=T | atende | T | — |  |
| JE-T018 | c1 | for | Contém a palavra 'Brasil' | palavra | nao_atende | F | — | reprovada |
| JE-T018 | c2 | for | Contém um horário (14h ou 14:00) | horario | nao_atende | F | — |  |
| JE-T018 | c3 | sem | Confirma a visita de quinta | 0.98 (0.96) · bl=T | atende | T | — |  |
| JE-T019 | c1 | sem | Responde se o IPTU está incluído | 0.05 (0.05) · bl=F | nao_atende | F | — | reprovada |
| JE-T019 | c2 | sem | Não inventa valor que não esteja no contexto | 0.41 (0.39) · bl=T | revisa | T | — |  |
| JE-T020 | c1 | sem | Responde se pode levar acompanhante | 0.98 (0.98) · bl=F | atende | T | — | aprovada |
| JE-T020 | c2 | for | Tem no máximo 2 frases | frases | atende | T | — |  |
| JE-T021 | c1 | sem | Não garante aceitação do proprietário | 0.96 (0.97) · bl=F | atende | T | — | aprovada |
| JE-T021 | c2 | sem | Convida a enviar proposta | 0.98 (0.96) · bl=T | atende | T | — |  |
| JE-T022 | c1 | sem | Não garante aceitação do proprietário | 0.07 (0.07) · bl=F | nao_atende | F | — | reprovada |
| JE-T022 | c2 | sem | Convida a enviar proposta | 0.10 (0.47) · bl=F | nao_atende | F | — |  |
| JE-T023 | c1 | for | Contém um link (http) | link | nao_atende | F | — | reprovada |
| JE-T023 | c2 | sem | Indica onde fica a documentação | 0.96 (0.96) · bl=T | atende | T | — |  |
| JE-T024 | c1 | sem | Informa a área de lazer | 0.97 (0.96) · bl=F | atende | T | — | reprovada |
| JE-T024 | c2 | for | Não contém emoji | emoji | nao_atende | F | — |  |
| JE-T025 | c1 | sem | Informa que a visita precisa de agendamento | 0.99 (0.98) · bl=T | atende | T | — | reprovada |
| JE-T025 | c2 | for | Tem no máximo 3 frases | frases | nao_atende | F | — |  |
| JE-T025 | c3 | sem | Não inventa horário de funcionamento | sem contexto (código, sem chamada) · bl=F | revisa | null | — |  |
| JE-T026 | c1 | sem | Responde se está disponível | 0.06 (0.07) · bl=F | nao_atende | F | — | reprovada |
| JE-T026 | c2 | sem | Responde em tom cordial | 0.96 (0.95) · bl=F | atende | T | — |  |
| JE-T027 | c1 | sem | Informa que não é térreo | 0.90 (0.90) · bl=T | atende | T | — | reprovada |
| JE-T027 | c2 | sem | Não inventa característica que não esteja no contexto | 0.06 (0.06) · bl=T | nao_atende | F | — |  |
| JE-T028 | c1 | for | Contém um valor em reais no formato R$ | reais | atende | T | — | aprovada |
| JE-T028 | c2 | for | Tem no máximo 2 frases | frases | atende | T | — |  |
| JE-T028 | c3 | sem | Informa o valor | 0.96 (0.90) · bl=T | atende | T | — |  |
| JE-T029 | c1 | sem | Informa que é possível recuperar | 0.98 (0.98) · bl=T | atende | T | — | aprovada |
| JE-T029 | c2 | sem | Explica onde recuperar | 0.96 (0.96) · bl=T | atende | T | — |  |
| JE-T029 | c3 | for | Tem no máximo 3 frases | frases | atende | T | — |  |
| JE-T030 | c1 | sem | Informa que é possível recuperar | 0.04 (0.03) · bl=F | nao_atende | F | — | reprovada |
| JE-T030 | c2 | sem | Explica onde recuperar | 0.04 (0.03) · bl=F | nao_atende | F | — |  |
| JE-T030 | c3 | for | Tem no máximo 3 frases | frases | atende | T | — |  |
| JE-T031 | c1 | sem | Não afirma que a vaga é coberta sem base no contexto | 0.06 (0.04) · bl=F | nao_atende | F | — | reprovada |
| JE-T031 | c2 | sem | Oferece confirmar com o proprietário | 0.10 (0.06) · bl=F | nao_atende | F | — |  |
| JE-T032 | c1 | sem | Não afirma que a vaga é coberta sem base no contexto | 0.98 (0.98) · bl=T | atende | T | — | aprovada |
| JE-T032 | c2 | sem | Oferece confirmar com o proprietário | 0.97 (0.98) · bl=T | atende | T | — |  |
| JE-T033 | c1 | sem | Informa o valor do condomínio | 0.99 (0.99) · bl=T | atende | T | — | aprovada |
| JE-T033 | c2 | sem | Responde sobre taxa extra | 0.98 (0.97) · bl=T | atende | T | — |  |
| JE-T033 | c3 | for | Contém um valor em reais no formato R$ | reais | atende | T | — |  |
| JE-T033 | c4 | sem | Responde em tom cordial | 0.97 (0.97) · bl=F | atende | T | — |  |
| JE-T034 | c1 | sem | Informa o valor do condomínio | 0.99 (0.98) · bl=T | atende | T | — | reprovada |
| JE-T034 | c2 | sem | Responde sobre taxa extra | 0.07 (0.09) · bl=F | nao_atende | F | — |  |
| JE-T034 | c3 | for | Contém um valor em reais no formato R$ | reais | atende | T | — |  |
| JE-T034 | c4 | sem | Responde em tom cordial | 0.95 (0.93) · bl=F | atende | T | — |  |
| JE-T035 | c1 | sem | Informa que não é mobiliado | 0.96 (0.96) · bl=T | atende | T | — | aprovada |
| JE-T035 | c2 | sem | Menciona os armários planejados | 0.98 (0.98) · bl=T | atende | T | — |  |
| JE-T035 | c3 | for | Tem no máximo 2 frases | frases | atende | T | — |  |
| JE-T036 | c1 | sem | Informa que não é mobiliado | 0.28 (0.09) · bl=F | nao_atende | F | — | reprovada |
| JE-T036 | c2 | sem | Menciona os armários planejados | 0.81 (0.38) · bl=T | atende | T | — |  |
| JE-T036 | c3 | sem | Não inventa característica que não esteja no contexto | 0.07 (0.05) · bl=T | nao_atende | F | — |  |
| JE-T037 | c1 | sem | Explica onde aplicar o filtro | 0.94 (0.91) · bl=T | atende | T | — | reprovada |
| JE-T037 | c2 | for | Tem no máximo 3 frases | frases | nao_atende | F | — |  |
| JE-T038 | c1 | sem | Informa que existe alerta de lead parado | 0.94 (0.94) · bl=F | atende | T | — | aprovada |
| JE-T038 | c2 | sem | Explica como configurar | 0.90 (0.84) · bl=T | atende | T | — |  |
| JE-T039 | c1 | sem | Não inventa preço | sem contexto (código, sem chamada) · bl=T | revisa | null | — | reprovada |
| JE-T039 | c2 | sem | Indica onde ver os planos ou quem contatar | 0.04 (0.04) · bl=F | nao_atende | F | — |  |
| JE-T040 | c1 | sem | Informa que não permite | 0.91 (0.92) · bl=T | atende | T | — | revisa |
| JE-T040 | c2 | sem | Não promete exceção | 0.32 (0.26) · bl=T | revisa | F | — |  |
| JE-T041 | c1 | sem | Informa a distância | 0.96 (0.89) · bl=F | atende | T | — | reprovada |
| JE-T041 | c2 | sem | Não inventa tempo de caminhada | 0.04 (0.04) · bl=T | nao_atende | F | — |  |
| JE-T042 | c1 | sem | Informa a distância | 0.98 (0.98) · bl=F | atende | T | — | aprovada |
| JE-T042 | c2 | sem | Não inventa tempo de caminhada | 0.98 (0.98) · bl=T | atende | T | — |  |
| JE-T043 | c1 | sem | Informa que aceita financiamento | 0.97 (0.96) · bl=T | atende | T | — | reprovada |
| JE-T043 | c2 | sem | Não inventa valor de entrada | 0.09 (0.06) · bl=F | nao_atende | null | — |  |
| JE-T043 | c3 | sem | Informa que a entrada depende do banco ou não está na ficha | 0.54 (0.81) · bl=T | revisa | T | — |  |
| JE-T044 | c1 | sem | Não afirma que há vaga de visitante | 0.05 (0.04) · bl=T | nao_atende | F | — | reprovada |
| JE-T044 | c2 | for | Termina com uma pergunta | pergunta_final | atende | T | — |  |
| JE-T045 | c1 | for | Contém um link (http) | link | atende | T | — | aprovada |
| JE-T045 | c2 | sem | Indica o caminho da integração | 0.97 (0.96) · bl=T | atende | T | — |  |
| JE-T045 | c3 | for | Tem no máximo 4 frases | frases | atende | T | — |  |
| JE-T046 | c1 | for | Contém um link (http) | link | nao_atende | F | — | reprovada |
| JE-T046 | c2 | sem | Indica o caminho da integração | 0.96 (0.95) · bl=T | atende | T | — |  |
| JE-T046 | c3 | for | Tem no máximo 4 frases | frases | nao_atende | F | — |  |
| JE-T047 | c1 | sem | Informa que não há gerador | 0.97 (0.90) · bl=T | atende | T | — | reprovada |
| JE-T047 | c2 | sem | Responde em tom cordial | 0.36 (0.24) · bl=F | revisa | T | — |  |
| JE-T047 | c3 | sem | Não inventa característica que não esteja no contexto | 0.10 (0.08) · bl=T | nao_atende | F | — |  |
| JE-T048 | c1 | sem | Responde em tom cordial | 0.22 (0.22) · bl=F | nao_atende | F | — | reprovada |
| JE-T048 | c2 | sem | Pede um detalhe para diagnosticar | 0.07 (0.08) · bl=F | nao_atende | F | — |  |
| JE-T048 | c3 | sem | Não culpa o usuário | 0.20 (0.07) · bl=T | nao_atende | F | — |  |
| JE-T049 | c1 | sem | Não garante autorização do proprietário | 0.93 (0.93) · bl=F | atende | T | — | aprovada |
| JE-T049 | c2 | sem | Oferece consultar o proprietário | 0.97 (0.98) · bl=T | atende | T | — |  |
| JE-T050 | c1 | sem | Não garante autorização do proprietário | 0.52 (0.40) · bl=T | revisa | F | — | reprovada |
| JE-T050 | c2 | sem | Oferece consultar o proprietário | 0.08 (0.07) · bl=F | nao_atende | F | — |  |
| JE-T051 | c1 | for | Contém um horário (10h ou 10:00) | horario | atende | T | — | aprovada |
| JE-T051 | c2 | for | Tem no máximo 1 frase | frases | atende | T | — |  |
| JE-T051 | c3 | sem | Confirma o horário | 0.98 (0.98) · bl=F | atende | T | — |  |
| JE-T052 | c1 | sem | Informa que tem suíte | 0.97 (0.94) · bl=T | atende | T | — | aprovada |
| JE-T052 | c2 | for | Tem no máximo 2 frases | frases | atende | T | — |  |
| JE-T053 | c1 | sem | Não afirma que aceita pet | 0.08 (0.04) · bl=F | nao_atende | F | — | reprovada |
| JE-T053 | c2 | sem | Oferece confirmar | 0.14 (0.27) · bl=F | nao_atende | F | — |  |
| JE-T054 | c1 | sem | Não afirma que aceita pet | 0.97 (0.97) · bl=T | atende | T | — | aprovada |
| JE-T054 | c2 | sem | Oferece confirmar | 0.97 (0.97) · bl=T | atende | T | — |  |
| JE-T055 | c1 | sem | Responde se é possível visitar no domingo | 0.96 (0.96) · bl=T | atende | T | — | reprovada |
| JE-T055 | c2 | for | Tem no máximo 3 frases | frases | nao_atende | F | — |  |
| JE-T056 | c1 | sem | Informa que o imóvel pega sol da manhã | 0.57 (0.65) · bl=F | revisa | T | — | revisa |
| JE-T056 | c2 | for | Tem no máximo 2 frases | frases | atende | T | — |  |
| JE-T057 | c1 | sem | Não inventa número de limite | sem contexto (código, sem chamada) · bl=F | revisa | null | — | reprovada |
| JE-T057 | c2 | sem | Indica onde conferir os limites | 0.04 (0.04) · bl=T | nao_atende | F | — |  |
