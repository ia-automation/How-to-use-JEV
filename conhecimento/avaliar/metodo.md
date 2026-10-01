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

## Avaliar o próprio repositório
`ferramentas/copia_fria.py` copia o repositório para `C:\tmp\jev-frio-<hora>` sem `prova/`, `fontes/`,
`chat.txt`, `.local/`, `.git/` e `api_key.txt`, por lista permitida, e confere a cópia
([README](../../README.md#ferramentas)). Protocolo da prova, decisão de 2026-09-30 e limites (não é
isolamento): [prova-fria](prova-fria.md).
