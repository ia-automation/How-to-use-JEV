# Imóvel duplicado — decisões de rotulagem

Autor: fable (rotulador). Data: 2026-10-01. Regras escritas ANTES dos pares. Pares de anúncios
sintéticos de apartamentos à venda, no estilo de portal. Bairros, cidades e ruas reais; nomes de
condomínio inventados. Nenhum andar, número de unidade, número de rua, nome de pessoa ou contato.

Arquivos: `rascunho.json` (5 pares fáceis), `ajuste.json` (40 pares), `teste.json` (80 pares, abrir
uma vez no fim). Envelope `{"versao", "autor": "fable", "casos"}`.

## Esquema (o do briefing, sem campo extra)
`{"id", "a": {anúncio}, "b": {anúncio}, "mesmo_imovel", "sinais": {"mesmo_endereco", "mesma_area",
"mesma_planta", "mesmo_preco"}, "nota"}` — anúncio = `{"titulo", "descricao", "bairro", "cidade",
"quartos", "vagas", "area_m2", "preco", "condominio_reais"}` (inteiros; preço e condomínio em reais).
A ordem `a`/`b` foi sorteada. `nota` começa com `"difícil: <família>"` nos casos difíceis.

## Como os pares foram feitos (e o que isso limita)
45 imóveis-base escritos à mão (15 para rascunho/ajuste, 30 para o teste — **nenhuma base aparece nos
dois conjuntos**), cada um com 3 a 5 descrições escritas à mão: dois corretores, o **vizinho** (outra
unidade do mesmo prédio/rua) e, em parte das bases, a versão que informa área total e a versão sem
endereço. Um gerador com semente fixa (`20261001`) monta os pares por família, perturba preço e área
dentro da faixa da família e escolhe o estilo de título. Os JSONs gravados são o artefato congelado.
Limite: a mesma base entra em mais de um par do mesmo conjunto (o construtor verá a mesma descrição em
pares diferentes) e os textos "genéricos" (sem detalhe distintivo) vêm de 3 moldes. Um bom placar aqui
valida o mecanismo; não prova desempenho em portal real.

## Sinais
- **`mesma_area` e `mesmo_preco` — preenchidos POR CÓDIGO a partir dos campos**, não à mão:
  `mesma_area = |a − b| / max(a, b) ≤ 0,03` sobre `area_m2`; `mesmo_preco = |a − b| / max(a, b) ≤ 0,05`
  sobre `preco`. Sempre `true`/`false` (os campos nunca faltam). São trabalho do CÓDIGO no exemplo: o
  validador recalcula e exige igualdade. O condomínio não entra em sinal nenhum.
- **`mesmo_endereco` — regra do rotulador** (aplicada pelo gerador sobre o que cada anúncio CITA em
  título + descrição, e conferida por amostragem): os dois nomeiam o prédio/condomínio → `true` se é o
  mesmo nome, `false` se são nomes diferentes (mesmo na mesma rua); senão, os dois citam rua → `true`
  se é a mesma rua, `false` se não; um dos dois não cita nada comparável → `null`.
  `true` quer dizer "mesmo prédio ou mesma rua", nunca "mesma unidade".
- **`mesma_planta` — regra do rotulador**: mesmos quartos, mesmas vagas e mesmos cômodos ESTRUTURAIS
  (sacada/varanda, dependência). `false` quando quartos ou vagas diferem ou um tem sacada/varanda e o
  outro "sem sacada". Cozinha americana × fechada, piso, armários, churrasqueira = estado/acabamento,
  não planta. Área não entra (é o outro sinal). Nunca `null` nestes dados.

## Regra de `mesmo_imovel`
`true` — é a mesma unidade anunciada duas vezes quando: mesmo bairro e cidade; endereço compatível
(`true` ou `null`); mesma planta; e o **conjunto de detalhes distintivos** coincide (vista, face/sol,
frente × fundos, lareira, pé-direito, taco, churrasqueira…). Diferença de preço NÃO derruba (preço
reajustado, corretores diferentes). Diferença de área NÃO derruba quando um anúncio declara área total
e o outro a útil. Mobiliado só num (omissão) não contradiz.

`false` — outro imóvel quando: bairro/cidade diferentes; ruas ou prédios diferentes; **mesmo prédio,
unidade diferente** (outra planta, ou mesma planta com detalhe FIXO que contradiz: vista para o parque
× fundos sem vista, face norte × face sul, com × sem lareira, pé-direito duplo × padrão); texto de
corretor reaproveitado em anúncio de outro endereço com outra área e outro preço.
**Mesmo prédio ≠ mesmo imóvel**: os quatro sinais podem ser `true` e o par ser `false`.

`null` (10%, sempre com nota) — indecidível: mesmo prédio e mesma planta SEM detalhe distintivo em
nenhum dos dois (mesma unidade ou a vizinha idêntica?); um anúncio sem endereço e ambos genéricos;
"mobiliado e decorado" × "entregue vazio" com o resto igual (mobília sai — pode ser a mesma unidade
em outro momento, ou a vizinha).
Só contradição de ESTADO (reformado × original, com × sem armários) não prova unidade diferente: nos
pares `false` por detalhe há sempre uma contradição fixa.

## Famílias e distribuição (contagem do validador do rotulador, 2026-10-01)
| Conjunto | pares | `mesmo_imovel` T/F/null | difíceis | `true` com área fora | `true` com preço fora | `false` com os 4 sinais `true` |
|---|---|---|---|---|---|---|
| rascunho | 5 | 3/2/0 | 0 | 0 | 0 | 0 |
| ajuste | 40 | 20/16/4 | 33 | 3 | 4 | 4 |
| teste | 80 | 40/32/8 | 66 | 6 | 8 | 8 |

| Família (prefixo da `nota`) | rótulo | ajuste | teste |
|---|---|---|---|
| dois corretores, descrições diferentes (não marcada difícil) | true | 5 | 10 |
| anúncio sem endereço, detalhes coincidem | true | 2 | 4 |
| preço reajustado | true | 4 | 8 |
| área útil × total | true | 3 | 6 |
| descrição copiada com pequenas mudanças | true | 3 | 6 |
| mobiliado só num (omissão) | true | 3 | 6 |
| sem detalhe distintivo (mesmo prédio/planta; ou um sem endereço) | null | 3 | 6 |
| mobiliado × vazio | null | 1 | 2 |
| unidade diferente no mesmo prédio/rua (outra planta) | false | 4 | 8 |
| detalhe fixo contradiz (mesma planta, números na tolerância) | false | 4 | 8 |
| mesma rua, prédios diferentes | false | 2 | 4 |
| mesmo bairro e números parecidos, ruas diferentes | false | 3 | 5 |
| texto reaproveitado em outro anúncio | false | 1 | 3 |
| bairros/cidades diferentes (não marcada difícil) | false | 2 | 4 |

Baseline que o construtor deve medir: "os 4 sinais `true` ⇒ duplicata" erra todos os pares de
"detalhe fixo contradiz" e não tem resposta para os `null`; "área e preço na tolerância" erra área
útil × total e preço reajustado.

O validador conferiu: envelope, campos e tipos, inteiros plausíveis, `mesma_area` e `mesmo_preco`
recalculados dos campos, planta `false` quando quartos/vagas diferem, `true` nunca com endereço
`false`/planta `false`/bairro diferente, ~metade `true` e ~10% `null`, ≥ 30% difíceis, nenhum padrão
de número de rua/andar/unidade, nenhuma descrição repetida entre ajuste e teste, UTF-8 sem BOM, LF.
