---
name: function-calling
description: Transforma frases de comando em chamadas de 10 funções tipadas (54 perguntas por comando em 1 requisição, args fechados viram Choice/Noul) com confiança por chamada = o julgamento mais fraco; 14 comandos de exemplo, confiança 0,53 a 1,00.
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/function_calling.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 7524–7897
estudado_em: 2026-09-30
---

# Function calling (Function calling)

## Problema
Um assistente de trading recebe frases ("plot rolling correlation between nvda and spy for the past month") e deve chamar funções Python comuns com argumentos que são `Literal`s (conjuntos fechados). Analogia do doc: o barista não anota a frase, marca opções num copo. Saída: nome da função + argumentos como enums avaliados, cada um com confiança. As funções não são alteradas; o que se acrescenta é um `spec` que explica em palavras o que cada argumento significa. No fim sai um `Dispatcher` que se aponta para as próprias funções.

As 10 funções (sobre 156.780 barras de 1 minuto): `list_symbols`, `market_summary`, `plot_price`, `intraday_pattern`, `compare_returns`, `rolling_correlation`, `summary_stats`, `volatility`, `top_movers`, `drawdown`. Exemplo de assinatura: `plot_price(symbol: Literal["SPY","NVDA","AMD","AAPL","MSFT","TSLA"], style: Literal["line","candles"]="line", resolution: Literal["1m","5m","15m","1h","1d"]="15m", window: Literal["1d","1w","1mo","3mo"]="1w", include_volume: bool=False, moving_average: Literal["9","20","50"]|None=None, log_scale: bool=False)`.

## Como o Jev entra
- **state:** o comando em texto livre (string).
- **perguntas:** montadas pelo `Dispatcher` a partir de assinatura + `spec.json`; todas na MESMA requisição por comando (54 perguntas no total para as 10 funções):
  - `__tool__` (Choice): "What is the user asking the trading assistant to do?" — uma opção por função, cada uma com a descrição do spec.
  - `<função>.<arg>` (Choice) para argumento de UM valor do conjunto fechado (`Literal`). Ex.: `plot_price.style`: "Does the user want a plain line or candles?" com opções `line` = "a simple line through the closing prices", `candles` = "a candlestick or OHLC chart, showing each bar's open, high, low and close". As chaves das opções SÃO as strings que a função aceita (nada mapeia rótulo→argumento depois). Ex. `moving_average`: "How many bars should the moving average cover - nine, twenty, or fifty?" opções `9` ("a nine-bar moving average, a fast one"), `20`, `50` ("a fifty-bar moving average, a slow one").
  - `<função>.<arg>?` (Noul) "stated": pergunta sim/não se o comando diz ALGO sobre aquele argumento. Ex.: `plot_price.style?`: "Does the user say how the chart should be drawn, such as a line, candles, or OHLC bars?". Se a resposta for não, o argumento é omitido e vale o default da função. Ex. `moving_average?`: "Does the user ask for a moving average or a smoothed line over the candles?".
  - `<função>.<arg>.<MEMBRO>` (Noul) para argumento `list[Literal]` (set): uma pergunta por membro, com `{}` no lugar do nome. Ex.: `compare_returns.symbols.NVDA`: "Does the user want NVDA in the comparison?".
  - Argumento `bool` = flag (ligado/desligado); como a pergunta de flag é escrita não é declarado no doc.
  - Argumentos não fechados (int, texto livre, número, data) NÃO recebem pergunta; vale o default (ex.: `limit` de `top_movers` fica 3).
- **formas detectadas por `closed_sets(fn)`:** choice (`Literal`), set (`list[Literal[...]]`), flag (`bool`). 28 argumentos preenchíveis no total: market_summary 1, plot_price 7, intraday_pattern 3, compare_returns 3, rolling_correlation 4, summary_stats 2, volatility 3, top_movers 2, drawdown 3, list_symbols 0.
- **chamadas:** 1 requisição por comando carrega a escolha da função e os argumentos de TODAS as funções; o dispatcher lê só as respostas da função escolhida. Modelo `jev-1.12`.
- **spec.json:** uma pergunta por argumento, uma linha por opção, uma descrição por função, mais a pergunta que escolhe a função; um LLM pode gerá-lo a partir das assinaturas. Regras de redação: escrever a pergunta sobre a IDEIA, não sobre as palavras do usuário (a correspondência é por significado: "is amd tracking nvidia lately" chega a `rolling_correlation` sem "tracking"/"lately" no spec); NÃO nomear a pergunta pelo parâmetro ("Which resolution?" não dá nada para casar); em argumentos irmãos do mesmo conjunto (`symbol` e `benchmark` com os mesmos 6 tickers) descrever o PAPEL: "the one being measured, named first" vs "the second one named, the yardstick".

## O que o código faz com a resposta
- Chamada = função escolhida + argumentos; cada argumento traz `value`, `probability`, `distribution`, `omitted`; o objeto tem `tool.probability`, `confidence`, `weakest()`, `.run()`.
- **`confidence` = o julgamento MENOS certo dentre os da chamada, não o produto** ("um argumento errado basta para estragar o resultado"; o produto responderia "tudo está certo?" e cai conforme a função tem mais argumentos, mesmo sem nenhum julgamento duvidoso).
- Argumento cuja pergunta "stated" deu não → omitido, default da função vale (p exibido na linha, ex. 0,96).
- `.run()` executa a função real (gráficos ou texto).

## Resultados medidos
14 comandos (confiança da chamada · p da função `tool`):
| Comando | Chamada | conf | tool |
|---|---|---|---|
| show nvda 1h | plot_price(symbol='NVDA', resolution='1h') | 0,78 | 1,00 |
| plot rolling correlation between nvda and spy for the past month | rolling_correlation(symbol='NVDA', benchmark='SPY', window='1mo') | 0,91 | 1,00 |
| when during the day does nvda trade the most | intraday_pattern(symbol='NVDA') | 0,53 | 1,00 |
| what moved today | top_movers(window='1d', direction='gainers') | 0,90 | 0,90 |
| what tickers do you have | list_symbols() | 1,00 | 1,00 |
| how did the market do this week | market_summary(window='1w') | 0,96 | 0,99 |
| candles for tesla with a 20 period moving average | plot_price(symbol='TSLA', style='candles', moving_average='20') | 0,69 | 0,97 |
| compare nvda amd and msft over the past three months | compare_returns(symbols=['NVDA','AMD','MSFT'], window='3mo') | 0,94 | 1,00 |
| how volatile is tsla | volatility(symbol='TSLA') | 0,96 | 1,00 |
| biggest losers today | top_movers(window='1d', direction='losers') | 0,98 | 0,98 |
| worst drawdown for nvda this quarter, and chart it please | drawdown(symbol='NVDA', window='3mo', plot=True) | 0,84 | 0,84 |
| spy stats for the last month | summary_stats(symbol='SPY', window='1mo') | 0,88 | 0,88 |
| show me apple daily with volume | plot_price(symbol='AAPL', resolution='1d', include_volume=True) | 0,75 | 0,85 |
| is amd tracking nvidia lately | rolling_correlation(symbol='AMD', benchmark='NVDA') | 0,82 | 0,82 |
Detalhe de "is amd tracking nvidia lately": symbol 'AMD' p 0,87 (AMD 0,87 / NVDA 0,13); benchmark 'NVDA' p 0,78 (NVDA 0,92 / AMD 0,08); window omitido p 0,96; resolution omitido p 0,99; weakest = benchmark. `window` e `resolution` omitidos porque "lately" não diz quanto nem com que barras; rodou nos defaults da função (um mês, barras horárias). Sem a pergunta `stated`, a escolha teria de nomear uma janela e o faria com confiança. Latência e custo: não declarados no doc.

## Técnicas reutilizáveis
- Assinatura de função tipada → perguntas (Literal→Choice, list[Literal]→um Noul por membro, bool→flag) → quando quiser tool-calling com valores garantidamente válidos (chaves das opções = valores aceitos).
- Segunda pergunta "stated" (Noul) por argumento opcional → o modelo não é obrigado a escolher valor quando o usuário não disse; o default da função vale.
- Escolha da função + argumentos de todas as funções numa única requisição; ler só o ramo escolhido → 1 round-trip, sem segunda chamada condicional.
- Confiança da chamada = mínimo dos julgamentos (não produto) → métrica que não despenca só por a função ter mais argumentos; `weakest()` aponta qual argumento duvidar.
- Descrever o papel de argumentos irmãos do mesmo domínio (medido vs referência) → evita trocar NVDA/SPY entre argumentos.
- Perguntas sobre a ideia, não sobre palavras, e nunca nomeadas pelo parâmetro → correspondência por significado.
- Deixar o que não é conjunto fechado (números, texto, datas) fora do modelo → default da função.
- Pedir a um LLM para gerar o spec a partir das assinaturas.

## Limites e pegadinhas
- O doc NÃO mostra o código de `Dispatcher`, `closed_sets`, `trader.py` nem o `spec.json` completo: só o comportamento. Reproduzir o dispatcher exige reescrevê-lo a partir da descrição acima.
- Só argumentos de conjunto fechado são preenchidos; `limit` (int) nunca é.
- Confiança baixa em comandos vagos: "when during the day does nvda trade the most" = 0,53.
- Saída exibida de "biggest losers today" lista AMD -0,57%, MSFT 0,67%, AAPL 1,40% como "top 3 losers" (valores positivos entre "losers"); é comportamento da função de exemplo, não do Jev, mas o doc não comenta.
- Inconsistência aparente: em "is amd tracking nvidia lately" a confiança é 0,82 e o argumento mais fraco mostra p 0,78 (benchmark), embora o texto diga que a confiança é o julgamento menos certo; o doc não explica a diferença (linhas 7837–7866).
- Como a probabilidade de argumento "omitido" é definida (p de "não declarado"?) não é declarado.

## Esqueleto de código
```python
assistant = Dispatcher(SPEC, TOOLS, client)        # dispatch.py (não mostrado no doc)
print(len(assistant.questions))                     # 54 perguntas por comando
# ids: "__tool__", "plot_price.style", "plot_price.style?", "compare_returns.symbols.NVDA"

call = assistant("is amd tracking nvidia lately")
print(call, call.confidence, call.tool.probability)
for name, argument in call.arguments.items():
    top = sorted(argument.distribution.items(), key=lambda kv: -kv[1])[:3]
    shown = "omitted, default stands" if argument.omitted else repr(argument.value)
    print(name, shown, argument.probability, top)
print(call.weakest().name)
call.run()                                          # executa a função real
```
Spec por argumento (forma): `{"question": "...", "stated": "...", "options": {"line": "...", "candles": "..."}}`.
