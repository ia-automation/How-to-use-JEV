---
name: confianca
description: confidence (só Choice/Score) resume o formato da distribuição; não é acerto nem permissão; três faixas (agir/cautela/não agir) e limiar por risco da ação; Noul não tem confidence.
tipo: conceito
fonte: https://docs.typesafe.ai/confidence · /patterns/confidence-routing · /agent-skill
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 1186–1269, 13182–13241 e 97–100
estudado_em: 2026-09-30
---

# Confiança

## O que é
- Choice e Score trazem `probabilities`. O **formato** diz a certeza: concentrada = confiante;
  espalhada = incerta. `confidence` ∈ [0,1] colapsa esse formato num número para você limitar.
- É **estatística derivada** das probabilidades. O componente `ConfidenceExplorer`
  publica uma aproximação para 3 opções: `(3 × p_max − 1) / 2`, limitada a [0,1].
  O código generaliza para `(n × p_max − 1) / (n − 1)`, mas isso não é uma
  definição contratual da API. Exemplos de Score com 4/5 níveis não seguem essa
  fórmula: formality [0;0,14;0,86;0;0] mostra confidence 0,89, enquanto ela daria
  0,825. Não recalcular a confiança oficial por essa aproximação.
  Fonte adicional: `fontes/docs/paginas/confidence.md`, linhas 28–32 e texto do
  componente; `fontes/docs/paginas/primitives/score.md`, dados do ScoreExplorer
  (https://docs.typesafe.ai/confidence e https://docs.typesafe.ai/primitives/score).
- **Medido [testado 2026-09-30, 40 respostas, jev-1.13.0]:** em Choice (n = 2…8) e Score de 3 níveis a
  fórmula `(n·máx − 1)/(n − 1)` bateu em todas (erro ≤ arredondamento); em Score de 4–5 níveis não
  (p = [0; 0,18; 0,42; 0,40; 0] → 0,52; a fórmula daria 0,28). Coincidir numa amostra não a torna
  contrato: **usar o campo devolvido**. Detalhe: [medicoes](../evidencias/medicoes-2026-09-30.md#confiança-40-respostas).
- `confidence` não é a probabilidade da opção vencedora: no vídeo 2 (36:05) o vencedor tinha 0,50 e
  `confidence` 0,25 ([video-02-quantbrasil](../evidencias/videos/video-02-quantbrasil.md)).
- **Noul não tem `confidence`**: só dois desfechos, o próprio `noul` descreve tudo.
- Exemplos reais: probabilidades 0,88/0,12/0,0 → conf 0,81; 0,85/0,15/0,0 → 0,78; 0,61/0,35/0,04 →
  0,42; 0,40/0,34/0,24/0,02 → 0,20; Score [0;0,57;0,43] → 0,35.

## Como ler confiança baixa
- Choice: nenhuma opção ganha com clareza (ou o caso é de duas opções ao mesmo tempo).
- Score: níveis ambíguos/sobrepostos, pergunta multidimensional, ou state não informa o bastante.
- Várias alternativas aceitáveis também espalham probabilidade: **confiança baixa numa escolha
  inofensiva de preferência não invalida a resposta**. Ignore incerteza de ramos que o código não usa.
- `confidence` resume concentração — **não é a correção do workflow nem permissão para agir**.
- **Duas intenções não aparecem na confiança** [testado 2026-09-30]: ticket com cobrança dupla + atraso
  deu setor com 0,99–1,00. Duas intenções pedem um Noul por destino ("o cliente pede algo a esta
  equipe?"), não um limiar ([triagem](../../exemplos/triagem-atendimento/README.md)).

## Calibração
Calibração é propriedade de **conjuntos** de previsões (das respostas com 0,8, ~80% acertam), não
certificado de acerto individual ([o-que-e-o-jev](o-que-e-o-jev.md#treino-rlcd)). Não confundir
`confidence` com P(opção escolhida) nem com intervalo estatístico. Ao mudar domínio, idioma ou versão,
a calibração precisa ser conferida de novo nos seus dados (ver [metodo](../avaliar/metodo.md)).
Chamadas idênticas não devolvem números idênticos: variação média 0,002–0,011, p95 ~0,05, máximo 0,15
[testado, [medicoes](../evidencias/medicoes-2026-09-30.md#estabilidade-mesma-requisição-repetida)].

## "Não sei" é sinal útil
Sistema que não expressa incerteza honesta não é confiável. A confiança é o mecanismo do modelo
dizer "não tenho certeza deste" — base para o código ter comportamento diferente por faixa.

## Três faixas (ponto de partida)
| Faixa | Comportamento |
|---|---|
| alta | agir automaticamente |
| média | prosseguir com cautela: pedir confirmação, marcar para revisão, coletar mais informação |
| baixa | não agir: humano, pedir esclarecimento, outro sistema (LLM de raciocínio) |

## Limiar escala com o risco
Um sistema tem **vários** limiares, um por consequência:
```python
if confidence < 0.5:            route_to_human(msg)          # piso: incerto de verdade
elif choice == "check_balance": show_balance(acct)            # risco baixo: errado é recuperável
elif choice == "approve_transfer":
    if confidence > 0.9:        confirm_then_execute(acct)    # risco alto + confiança alta
    else:                       ask_user_to_confirm(acct)
```
No padrão do doc (voz bancária): piso 0,6; saldo ≥ 0,6; transferência > 0,85 aprova, 0,6–0,85 pede
confirmação; intenção `other` → atendente.

Outros limiares vistos nas páginas/receitas: 0,3 (department → triagem manual); 0,5 (resolução →
perguntar ao cliente); 0,75/0,8 (tópico → humano); 0,8 (citação auto-aceita); 0,9 (classe SIC
aceita, senão sobe para a divisão pai); 0,60 (datas → revisão). Nenhum é universal.

## Regras práticas
- **Começar conservador, medir nos seus dados e ajustar.** Plotar confiança × acurácia nos seus casos.
- Se só importa a melhor opção, **pegue a de maior probabilidade** — não precisa limiar de confiança
  em todo lugar (erro comum do agente de código).
- Algoritmo estatístico específico → use `probabilities`, não `confidence`.
- Limiar afinado num Noul **não serve** para Choice (e vice-versa) — [limites-jev-1-13](limites-jev-1-13.md) #8.
- Limiar afinado numa **versão** do modelo: fixar o ID versionado (`jev-1.13.0`) em vez do alias
  `jev-latest`, que muda sozinho ([modelos-precos-limites](modelos-precos-limites.md)).
- As receitas de datas/function calling usam o **mínimo** das partes consumidas
  como sinal operacional da parte fraca. Não é probabilidade conjunta nem fórmula
  geral de confiança. O beam usa média geométrica de probabilidades para ordenar caminhos.
- Faixa de incerteza de dois lados para Noul (ex.: 0,30–0,70 ou `NO=0.2`/`YES=0.8`) → meio vai a humano;
  se o revisor recebe demais, estreitar; se passa rota errada, alargar.

## Relacionados
[primitivas](primitivas.md) · [roteamento-por-confianca](../construir/padroes/roteamento-por-confianca.md) · [classificacao-com-confianca](../receitas/classificacao-com-confianca.md) · [autoconsistencia-nouls](../receitas/autoconsistencia-nouls.md)
