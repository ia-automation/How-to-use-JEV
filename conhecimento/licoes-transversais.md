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

## Anti-padrões (o que as receitas e o doc condenam)
- Fragmentar sem motivo perguntas agrupáveis. · Noul usado como escala. · Limiar de Noul reaproveitado em Choice.
- Pedir ao Jev para contar, somar, comparar datas ou gerar texto. · State com o documento inteiro
  quando a pergunta usa um parágrafo. · Tratar guardrail com Jev como fronteira de segurança.
- Confiar em confiança alta como prova. · Limiar espalhado pelo código.
