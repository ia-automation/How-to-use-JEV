---
name: licoes-transversais
description: Síntese do estudo — princípios do doc, das receitas e dos vídeos, com limites e políticas de aplicação explícitos.
tipo: principio
fonte: síntese de conhecimento/modelo, conhecimento/construir, conhecimento/receitas e conhecimento/evidencias/videos (antes em memoria/)
estudado_em: 2026-09-30
---

# Lições transversais — o que vale em toda integração

## Divisão de trabalho
1. **O Jev julga, o código decide.** Fluxo, regras determinísticas, aritmética, datas, contagem,
   efeitos colaterais e política ficam no código. O modelo só dá julgamentos atômicos sobre texto.
2. **O Jev escolhe, não gera.** Candidatos saem de regex/parser/BM25/LLM; o Jev escolhe; o código
   copia literal e normaliza. O valor nunca é inventado ([extracao-de-valor-pre-parseado](receitas/extracao-de-valor-pre-parseado.md)).
3. **Precisa de texto? LLM escreve, Jev decide** (vídeo 3: LLM local escreve; [demo-casa-inteligente](receitas/demo-casa-inteligente.md):
   LLM só para dividir pedido composto e conversa livre; [cascata-sde](receitas/cascata-sde.md): LLM extrai, Jev verifica).
4. **O que a regra resolve sai do modelo** (string match antes da citação; prefixo SIC para subir na
   hierarquia; regex de ticker antes de "empresa mencionada?").

## Desenho das perguntas
5. **Atômico é o conceito nº 1.** Uma condição por Noul, uma dimensão por Score, uma decisão por
   Choice. Pergunta ampla esconde julgamentos; atômica expõe para inspecionar, afinar, combinar.
6. **Pergunte o fato mais estreito que decide o limiar** ("a linha retoma no meio da frase?" deu
   17 blocos; "mesmo parágrafo?" deu 12 — [recuperacao-de-estrutura](receitas/recuperacao-de-estrutura.md)).
7. **Literal:** o modelo responde o que está escrito. A explicação que você daria diante do erro é a
   metade que falta da instrução.
8. **Alto = sim.** Frases positivas; em verificação, o caso de alerta é o `true`; nunca `true`
   descrevendo "não".
9. **Sempre uma válvula de "nada disso":** `other`/`none`/`not_stated`/`out_of_range` numa Choice, ou
   uma pergunta `stated`/`exists` separada. O código sinaliza em vez de chutar.
10. **Choice = qual (relativo); Noul = se (absoluto).** Choice só de candidatos reais
    sempre escolhe um. Pode-se incluir `none` ou acrescentar Noul de adequação/existência,
    conforme a tarefa; o vencedor relativo sozinho não prova utilidade.
11. **Score descreve situações, não graus**; cada nível é julgado sozinho; normalizar por
    `len(criteria)-1` antes de pesar.
12. **Opções carregam os valores válidos**: as chaves da Choice são os valores aceitos pelo código
    (argumentos de função, trechos candidatos, rótulos `c0..cn` da hierarquia).
13. **Estrutura quando separa orientação**: `question` + dado em campo próprio; `what`/`not_for`/
    `examples` com os mesmos nomes em todas as opções; subárvore como valor para andar taxonomia.
14. **Relevância antes de consumir o julgamento**: se o state pode não tratar do alvo,
    usar um Noul "menciona/trata de X?". As perguntas podem compartilhar a chamada;
    a ordem de consumo em código não exige sequência de inferências.

## Chamadas
15. **Agrupar perguntas do mesmo state** compartilha seus tokens. A receita de 13
    perguntas mediu 12,2× menos custo e 10× menos tempo contra execução sequencial,
    naquele documento longo. Não é ganho universal ([perguntas-em-paralelo](receitas/perguntas-em-paralelo.md)).
16. **Outra chamada quando há dependência real** ou quando limites de contexto,
    isolamento/orçamento justificam dividir. Fan-out é preferência de desenho.
17. **Requests e custo são coisas diferentes.** Num lote, mais perguntas não exigem
    mais requests, mas acrescentam tokens. Estados repetidos podem dominar o custo;
    limite concorrência conforme as cotas efetivas.
18. **Funil barato e largo → caro e estreito:** Choice sobre 182 descrições curtas, depois Nouls nos 3
    melhores com o texto completo. Não varrer milhares de opções irrelevantes sem pré-filtro
    (vídeo 2: universo inteiro errou; lista curta igualou o GPT-6).

## Usar a resposta
19. **Limiar é constante nomeada, num arquivo só** (`POLICIES`, `AUTO_ACCEPT`, `FIRE_T`, `YES`/`NO`).
    Mudar política = editar número, sem nova chamada; é o que o humano revisa.
20. **Três faixas, não uma:** age / revisa / não age. Meio de Noul (ex.: 0,30–0,70) vai a humano.
21. **Limiar por risco da ação**, com piso global (0,5–0,6) e limiar alto para ação destrutiva.
22. **Incerteza vira desfecho útil**, não descarte: `uncertain` → humano; classe incerta → divisão pai;
    passagem que contradiz → bloco de conflito; resolução incerta → perguntar ao cliente.
23. **Composição é política.** `min` das confianças usadas destaca a parte fraca;
    `max` entre alertas evita diluí-la. Não são probabilidades conjuntas nem
    fórmulas obrigatórias para todo fluxo.
24. **Guardar a resposta bruta** (probabilidades + versão do modelo): repesar, re-limiar e reexibir
    sem reinferir; cache pela identidade completa definida em
    [integracao-segura](construir/integracao-segura.md) (state + perguntas/critérios + modelo + provedor),
    preço aplicado depois.

## Validação
25. **Medir nos seus dados, na versão fixada.** Limiares de receita são exemplos. Confiança alta não
    prova acerto. Alias `jev-latest` muda sozinho → logar `model`, fixar versão quando afinar.
    Português: acurácia não publicada pelo doc; o que medimos em 2026-09-30 (sintético e texto real)
    está em [medicoes-2026-09-30](evidencias/medicoes-2026-09-30.md#idioma) — medir de novo no próprio domínio.

## O que os 12 exemplos de 2026-10-01 acrescentaram [testado]
Sintético, n de 40–87 por exemplo; números em [medicoes-2026-10-01](evidencias/medicoes-2026-10-01.md).
26. **Resposta do Jev nunca é autorização — nem dispensa.** Um Noul "o usuário dispensou a confirmação" retirava a
    confirmação; um Noul "pode continuar mandando" dispensava o bloqueio legal. Dispensa vem de campo estruturado
    do chamador; um Noul de guarda nunca é a razão única para NÃO cumprir uma obrigação
    ([guarda-tool-call](../exemplos/guarda-tool-call/README.md), [opt-out-lgpd](../exemplos/opt-out-lgpd/README.md)).
27. **Sinal medido sem regra que o leia é sinal perdido.** `shared_target` deu 0,96 e nenhuma regra o consumia: o
    comando vazou. Para cada pergunta, apontar a linha da política que usa a resposta.
28. **O que o modelo não pode ver é filtrado ANTES da chamada.** O lint mandava o diff com o segredo que devia
    detectar; a máscara entra em código, antes do state.
29. **O Jev não lê notação posicional com segurança** (`+`/`-` de diff, índice de lista): o código diz o que é novo
    e aponta a parte por nome (`last_message`, não "a terceira").
30. **Recência, magnitude, contagem e comparativo são do código** e entram no state como fato calculado ("o mais
    barato é B"). Cuidado: um fato calculado no state pode mover um Noul vizinho — conferir no ajuste as perguntas
    que não deviam mudar ([proxima-pergunta](../exemplos/proxima-pergunta/README.md)).
31. **Guarda só no lado caro.** Cada Noul de guarda tem de apontar para um erro com custo declarado; guarda extra
    só comprou revisão a mais ([repeticao-ou-revisao](../exemplos/repeticao-ou-revisao/README.md): 7 Nouls
    perderam para a Choice sozinha, 0,862 × 0,931, com o mesmo erro caro zero).
32. **Decompor rende quando a Choice não vê a classe** (indecidível, afirmação com várias partes, injeção escondida);
    onde a Choice já acerta, mais perguntas custam acerto. Choice + válvula acertou onde o Noul relacional hesitou
    ([imovel-errado](../exemplos/imovel-errado/README.md)); o Score não acrescentou nada aos Nouls
    ([imovel-duplicado](../exemplos/imovel-duplicado/README.md)).
33. **Dividir um Noul em dois abre um vão entre eles**: o caso do meio fica com 0,37 e 0,39 e sem dono. Somar as
    duas leituras em código antes da faixa, ou conferir o caso do meio no ajuste.
34. **Enumerar opostos na pergunta falha fora da lista**; escrever a condição geral.
35. **O state carrega o payload.** Conteúdo que argumenta pela própria classificação move a resposta: trocou
    `descartar` por alerta, e não trocou alerta por `usar` só porque nenhum Noul lido do conteúdo libera sozinho
    ([injecao-em-ferramenta](../exemplos/injecao-em-ferramenta/README.md)). Filtro, não fronteira.
36. **A saída diz ao consumidor o que ele NÃO pode fazer.** Aviso só no README não protege: `substituir` passou a
    sair com o contexto obrigatório e `descartar_anterior: false`; sinal de reconciliação nunca autoriza apagar.
37. **Com catálogo que cabe numa Choice, comece pela Choice única com descrição completa e a política de "nenhuma"
    escrita na válvula**; limiar publicado em receita não é parâmetro local (0,30 deu 6/24 de skill indevida)
    ([selecao-de-skill](../exemplos/selecao-de-skill/README.md)) — hipótese exploratória, não era a variante principal.

## Anti-padrões (o que as receitas e o doc condenam)
- Fragmentar sem motivo perguntas agrupáveis. · Noul usado como escala. · Limiar de Noul reaproveitado em Choice.
- Pedir ao Jev para contar, somar, comparar datas ou gerar texto. · State com o documento inteiro
  quando a pergunta usa um parágrafo. · Tratar guardrail com Jev como fronteira de segurança.
- Confiar em confiança alta como prova. · Limiar espalhado pelo código.
