# Origem e rótulos do catálogo de busca

Autor: Codex. Data: 2026-09-30. Dados integralmente sintéticos, preparados sem ler
a implementação da busca. Cidades, anúncios e condições são fictícios. Nenhum
endereço pessoal, andar, número de unidade ou contato integra as entradas.

- `anuncios.json`: 150 anúncios, duas cidades fictícias e três tipos de imóvel.
- `consultas_ajuste.json`: oito consultas para desenvolvimento.
- `consultas_teste.json`: 16 consultas reservadas à avaliação final.

Os três JSONs seguem o envelope `versao`, `autor`, `casos` de `exemplos/DADOS.md`.
O catálogo é compartilhado; a separação é entre consultas. Portanto, o teste mede
consultas novas **sobre este catálogo**, não generalização para anúncios inéditos.

## Como o gabarito foi construído

Cada anúncio recebeu fatos controlados para oito critérios: permite pet, rua
tranquila, espaço adequado para home office, metrô a pé, sol da manhã, reforma
concluída, vista aberta e jardim privativo. Para cada critério há três estados:
afirmado, negado ou não informado. Um dos três enunciados equivalentes expressa
o fato presente; fatos não informados são omitidos. A ordem das frases varia.
O sorteio usou seed `20260930`; os JSONs entregues são os artefatos congelados.

Os rótulos foram calculados sobre esses fatos de autoria, antes de qualquer
resposta do Jev. Não se trata de anotação humana independente de anúncios reais.
As descrições controladas facilitam conferir contradição e ausência, mas têm
menos variedade que textos espontâneos. Um bom placar aqui valida o mecanismo;
não comprova qualidade em portais ou dados reais.

## Aplicação da escala congelada

1. Cidade, bairro e tipo, quando pedidos, devem coincidir. Quantidades mínimas e
   limites de preço são inclusivos. Falhar qualquer restrição dura dá **0**.
2. Se um critério subjetivo pedido estiver explicitamente negado, dá **0**, mesmo
   que os outros sejam favoráveis.
3. Restrições duras satisfeitas e todos os critérios subjetivos afirmados: **3**.
4. Restrições duras satisfeitas, alguns subjetivos afirmados e os demais ausentes:
   **2**. Nenhum pode estar explicitamente negado.
5. Restrições duras satisfeitas e todos os subjetivos ausentes: **1**.

Não informar pet não significa aceitar ou proibir pet. Não informar um escritório
também não prova que o imóvel seja apropriado para trabalho remoto. Uma propriedade
com relevância 1 é candidata incompleta para investigação, não atendimento
comprovado de todos os requisitos do comprador.

Foram julgados os **3.600 pares** entre 24 consultas e 150 anúncios. Os mapas
`relevancia` armazenam todos os 298 pares com nota maior que zero; os omitidos
valem zero. Há ao menos um candidato não nulo por consulta. Os números são
características deste corpus, não metas a perseguir no resultado da busca.

## Uso no experimento

O implementador consulta somente o ajuste até congelar perguntas, rubrica de
ranking e limiares. Não enviar `relevancia` ao modelo. Comparar a saída com todos
os candidatos, incluindo anúncio omitido pelo recuperador; medir também a perda
na recuperação inicial, antes de reordenar os poucos selecionados.

Não afinar o código depois de abrir o teste e apresentar o novo placar como se
fosse a mesma avaliação cega. O conjunto é pequeno e deliberadamente controlado;
as médias precisam vir acompanhadas de exemplos de erro e limites da evidência.
