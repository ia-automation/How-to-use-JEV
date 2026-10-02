---
name: metodo
description: Protocolo de avaliação de uma integração com o Jev (registro mínimo, métricas por primitiva, casos que mudam decisões, limiares, critério de conclusão) + as lições de método que os 5 exemplos medidos e a avaliação em dados públicos ensinaram em 2026-09-30.
tipo: principio
fonte: plano de avaliação do Codex (skills/jev-evaluate, 2026-09-30) + https://docs.typesafe.ai/confidence · /primitives/score · /primitives/noul · /model-jaggedness/jev-1.13 + exemplos/ e avaliar/ deste repositório
estudado_em: 2026-09-30
---

# Método de avaliação

O protocolo abaixo é **proposta local** [local] do Codex (antes em `skills/jev-evaluate/references/evaluation.md`);
não é benchmark executado. As lições da última seção vêm de execuções reais nossas [testado].
Procedimento passo a passo: skill [jev-avaliar](../../skills/jev-avaliar/SKILL.md).

## Registro mínimo de experimento

Identificar: objetivo, versão do dataset, separação ajuste/teste, provedor e modelo
solicitado/retornado, revisão de perguntas, política de limiares, concorrência,
região de execução, data, número de repetições e orçamento. Usar referências ou
hashes para dados sensíveis; não inserir o dataset privado na memória geral.

Para cada caso: ID, rótulo de referência, resposta, decisão do consumidor, tempo
total, número de tentativas, uso e estado da chamada. Guardar erros separadamente.

## Métricas conforme a tarefa

| Tarefa | Evidência útil |
|---|---|
| Choice | Matriz de confusão, desempenho por categoria, efeito da opção `other` e desempenho em casos ambíguos. |
| Noul | Precisão/recall por limiar, curva de confiabilidade por faixas de probabilidade e Brier score quando há rótulo binário confiável. |
| Score | Concordância com a rubrica, erro ordinal/absoluto conforme o uso e qualidade da ordenação; preservar distribuições. |
| Política de ação | Cobertura automática, erro entre ações automáticas, taxa de revisão e custo de cada tipo de erro. |
| Sistema | p50/p95/p99 ponta a ponta, falhas, sobrecarga, retentativas, custo por registro e custo de fallback. |

Com amostra pequena, os percentis extremos são frágeis: informar tamanho e
condições. Não comparar somente médias nem tempos exibidos por interfaces distintas.

## Armadilhas
- `confidence` de Choice/Score não é P(acerto); não usá-lo como probabilidade binária para Brier score.
- Não transportar um limiar ajustado em Noul para Choice sim/não.
- Não exigir identidades aritméticas entre perguntas diferentes. Se a aplicação
  precisa de uma negação exata, derive-a no código a partir do mesmo resultado.
- Não tratar timeout, resposta incompleta ou erro HTTP como rótulo negativo: fica fora da métrica de
  qualidade e é contado à parte (cobertura/erro operacional).
- Não aprovar um limiar só porque a confiança média aumentou; ajustar perguntas pode melhorar a tarefa,
  mas aumento isolado de confiança não prova melhoria.

## Casos que mudam decisões

- Solicitação explícita, negação explícita e fala de outra pessoa citada no texto.
- Falta de informação, categorias não previstas e duas intenções simultâneas.
- Siglas/nomes ambíguos, como o problema mostrado no vídeo 02.
- Português informal, erros de escrita e, se relevante, mistura de idiomas.
- Conteúdo tentando instruir a classificação dentro do `state`.
- Muitos campos irrelevantes versus contexto filtrado; perguntas independentes
  agrupadas versus separadas, sem assumir que a divisão seja sempre melhor.
- Ausência de uma resposta esperada, tipo errado, não finitos, timeout e erros HTTP:
  verificar o consumidor com testes locais, sem precisar provocar falhas na API real.

## Limiares

Noul pode ter limite inferior para “não”, superior para “sim” e intervalo de
indecisão. Choice/Score podem ter políticas baseadas em significado e confiança.
Os valores são escolhidos de acordo com erros observados e consequências, não
copiados de um exemplo. Ranking sem efeito automático pode usar diretamente os
scores/probabilidades, sem impor um bloqueio por confiança a toda saída.
Ao alterar uma rubrica, repetir a avaliação relevante.
Referências: [Score](https://docs.typesafe.ai/primitives/score),
[Noul](https://docs.typesafe.ai/primitives/noul),
[Confidence](https://docs.typesafe.ai/confidence).

## Limitações documentadas para 1.13

Leitura literal, contagem/cálculos, comparação de datas, várias indireções,
estado grande com informação irrelevante, instruções/critério em conflito,
conteúdo adversarial, invariantes entre perguntas separadas e geração livre
([limites-jev-1-13](../modelo/limites-jev-1-13.md)). Não significa que todo caso nessas categorias
falhe; significa que a integração não deve presumir que funcionem sem avaliação.

## Critério de conclusão

Entregar resultado com amostra, condições, métricas, falhas observadas e decisão
recomendável para aquele contexto. Se só existe mock ou leitura documental, a
conclusão é “contrato preparado/conferido”, nunca “Jev aprovado em produção”.

## Lições de método das nossas execuções [testado 2026-09-30]
| Lição | De onde |
|---|---|
| Ajuste e teste separados; perguntas, código e limiares **congelados com hash** antes de abrir o teste; teste rodado uma vez. Mudar pergunta depois de ver o teste transforma o teste em ajuste. | todos os [exemplos](../../exemplos/README.md); [protocolo público](../../avaliar/publicos/PROTOCOLO.md) |
| **Ajuste fácil não calibra**: se todas as probabilidades do ajuste estão perto de 0 ou 1, a curva cobertura × erro fica plana e o limiar vira palpite; os erros do teste moraram perto dos limiares. | triagem, guardrail, extração, busca |
| Consertar um caso do ajuste **alargando a pergunta** é overfit (roteador: 30/30 no ajuste, 4 dos 10 erros do teste vieram das perguntas alargadas); regra afinada num caso só não generalizou (triagem). Estreitar a pergunta até o alvo da política generalizou. | [roteador](../../exemplos/roteador-jev-llm/README.md), [triagem](../../exemplos/triagem-atendimento/README.md) |
| Separar **erro do componente**, **erro do fluxo** e **rótulo disputável**: na triagem uma regra falhou como detector isolado mas outra proteção segurou a ação; 1 dos 2 erros dependia de regra de rotulagem ausente (T018). Registrar a lacuna e fixar a regra antes do próximo corpus; o placar congelado não muda. | triagem |
| Num guardrail, reportar a **faixa do meio** e o falso "passa", não só o acerto: limiar único 0,50 daria acerto 0,967 com 1 vazamento contra 0,950 sem vazamento. | [guardrail](../../exemplos/guardrail-chatbot/README.md) |
| Em extração, medir **cobertura dos candidatos** antes do acerto da escolha; "zero saída fora dos candidatos" não prova ausência de erro semântico (data negada virou agendamento). | [extração](../../exemplos/extracao-sem-inventar/README.md) |
| Catálogo controlado mede o **mecanismo**, não desempenho real; medir a perda da recuperação à parte. | [busca](../../exemplos/busca-imoveis/README.md) |
| Informar **casos únicos** separados de repetições (40 pares pt×en: 14/11/11 casos únicos, não 28/22/22); p95 de variação de uma amostra não define banda segura. | [medicoes](../evidencias/medicoes-2026-09-30.md) |
| Dados públicos: protocolo congelado antes da primeira chamada; deduplicação (exata e aproximada) e divisão por grupo (post, produto) antes de sortear ajuste/teste, para o mesmo conteúdo não aparecer dos dois lados; baselines com os mesmos rótulos e em outro regime; bootstrap por grupo; estratos unânime × disputado (concordância entre anotadores é referência de ambiguidade, não teto). | [avaliar/publicos](../../avaliar/publicos/README.md) ([preparação](../../avaliar/publicos/preparacao.md)) |
| Custo de "tudo no LLM" com LLM **simulado** é cenário, não economia observada. | roteador |
| Com poucos rótulos (100), pesos fixos declarados antes ≥ logística treinada; ajuste pequeno esconde sinal raro (coluna chata no ajuste que separa no teste). Desfecho de negócio mede **sinal preditivo**, não acerto por pergunta; Brier perto da constante = usar para ordenar, não como probabilidade. | dados internos ([medicoes](../evidencias/medicoes-2026-09-30.md#dados-internos-conversas-reais-de-venda)) |

## Lições de método das execuções de 2026-10-01 [testado]
Doze exemplos com teste congelado e revisão adversarial; números em [medicoes-2026-10-01](../evidencias/medicoes-2026-10-01.md).
| Lição | De onde |
|---|---|
| **Rodada única só é auditável com manifesto**: hash de perguntas, código, dados de teste E critério de aceite gravados antes do teste; o `run.py` recusa rodar se algo mudou; cache com histórico (a resposta anterior não some). Sem isso "rodei uma vez" é palavra. | revisão do Codex na onda 1; `exemplos/_comum/congelamento.py` |
| **Critério de aceite num dicionário, com o veredito calculado pelo script.** Reprovou 4 de 12 e a reprovação ficou escrita — é o valor do protocolo. Critério só em prosa vira interpretação depois do teste. | guarda, juiz, lint, seleção |
| **Correção depois do teste é "rodada N, pós-revisão, não cega"**, relatada ao lado da cega e nunca no lugar dela. Passar o critério na rodada 2 não reabilita o desenho. | todos os que tiveram rodada 2 |
| **A rodada pós-revisão também regride**: a correção de um erro criou outro em 3 exemplos. Reportar o que piorou com o mesmo destaque do que melhorou. | auditor, opt-out, próxima-pergunta |
| **Medir o baseline e as peças de código com o mesmo rigor do Jev.** O código errou mais que o modelo: número brasileiro, regex "exata", parser sem polaridade. Um critério "numéricas 100%" existia para denunciar isso e denunciou. | promessas, próxima-pergunta, duplicado, guarda, juiz |
| **Margem sobre o baseline é critério frágil com teto perto**: fixado com o baseline em 0,722 no ajuste, virou alvo de 0,959 quando o baseline fez 0,759 no teste. Preferir limite absoluto no erro caro + piso de acerto. | [seleção](../../exemplos/selecao-de-skill/README.md) |
| **Com n de 40–60, um caso decide o veredito** ("+15 p.p." separa 52 de 51 acertos). Declarar quando o critério passou no limite. | opt-out, próxima-pergunta |
| **Família com poucos casos no ajuste não calibra nem faixa nem expectativa**: alerta sem necessidade 17% no ajuste, 25% no teste; taxa de revisão 8% → 15,7%. | injeção, repetição |
| **Ablação feita depois de ver o teste é hipótese**, mesmo quando sai do cache sem chamada nova: respostas de uma requisição com 8 perguntas não provam o que uma com 3 responderia. | repetição, seleção (variante `a2`) |
| **Variante informativa não vira principal depois do teste.** A principal é a declarada no manifesto; a melhor entre as demais é candidata para dados novos. | seleção |
| **Falha operacional é desfecho medido, não exceção**: bateria sem rede (`testa_falhas.py`) prova que timeout, cache faltando e resposta fora do contrato caem na classe de revisão, por caso, sem abortar o lote. | opt-out, duplicado, injeção, seleção, repetição |
| **Dado real anonimizado: a varredura automática não substitui ler a amostra.** A conferência exata contra o bruto pegou o que os padrões frouxos não viam (nome em maiúsculas após rótulo, usuário do endereço no corpo, entidade HTML escondendo o andar). | preparação do `roteador-email` |

## Reavaliar quando sair versão nova do modelo [local]
Os limiares dos exemplos valem para `jev-1.13.0`; `jev-latest` muda sozinho. Antes de trocar a versão:
`python -X utf8 ferramentas/reavaliar_versao.py --modelo jev-1.14.0 --so-estimar` (imprime requisições e custo, zero chamada) e depois
sem `--so-estimar`: roda o teste congelado de cada exemplo ao vivo, grava em `exemplos/<ex>/cache-<modelo>/` (o `cache/`,
o manifesto e os limiares ficam intocados, conferido por hash) e escreve `conhecimento/evidencias/reavaliacao-<modelo>-<data>.md`
com veredito do critério, métricas, casos e perguntas que trocaram de lado e a distância ao limiar. A rodada da MESMA
versão ([reavaliacao-jev-1.13.0-2026-10-01](../evidencias/reavaliacao-jev-1.13.0-2026-10-01.md)) é referência
empírica do quanto a API varia sozinha (uma amostra, um dia) — não é banda segura: a distância ao limiar não diz a
causa, e uma troca do mesmo tamanho numa versão nova pode ser efeito da versão. Recalibrar continua decisão humana,
registrada em `decisoes.md`.

## Avaliar o próprio repositório
`ferramentas/copia_fria.py` copia o repositório para `C:\tmp\jev-frio-<hora>` sem `prova/`, `fontes/`,
`chat.txt`, `.local/`, `.git/` e `api_key.txt`, por lista permitida, e confere a cópia
([README](../../README.md#ferramentas)). Protocolo da prova, decisão de 2026-09-30 e limites (não é
isolamento): [prova-fria](prova-fria.md).
