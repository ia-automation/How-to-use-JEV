# Extração sem inventar — e-mail, telefone, CPF, valor em R$ e data de visita

**Problema.** De mensagens de clientes em português (WhatsApp, e-mail, formulário de imobiliária),
tirar os dados de contato e de negócio **sem nenhum valor inventado**: dígito trocado, e-mail
"consertado" pelo modelo ou data calculada errado custam caro no CRM.

## Por que cada parte é código ou Jev

| Parte | Quem | Por quê |
|---|---|---|
| Achar candidatos (regex; extenso "um milhão e meio", "450k", "1,2 mi") | código (`candidatos.py`) | formato regular; recall alto, o excesso o Jev descarta |
| Dígito verificador do CPF, DDD, E.164, `Decimal` | código | regra exata; o que a regra resolve sai do modelo |
| Qual candidato é o que o texto pede (ou `none`) | Jev — Choice cujas opções SÃO os trechos | papel só se lê no contexto (o telefone do marido, o preço do anúncio × a proposta) |
| Escala de número cru ("consigo pagar 600") | Jev — Choice `as_written/thousands/millions` | leitura de contexto; a multiplicação é do código |
| Data da visita | Jev lê PARTES (modo, dia, mês, ano, âncora, dia da semana, semana); código monta | limite #3: o modelo não faz calendário |
| Revisar ou aceitar | código (`perguntas.CONF_MIN` = 0,60) | limiar é constante num arquivo só |

## Desenho
- **State** `{"message": texto}`; a data de referência não vai ao modelo (é do calendário).
- **Uma requisição por mensagem**, todas as perguntas juntas (fan-out). Campo sem candidato não gera
  pergunta; sem pista de data, as perguntas de data nem vão; mensagem sem nada não chama a API.
- **E-mail corrigido** ("…@uol.com ops, é .com.br"): o CÓDIGO junta os dois trechos num candidato
  "reconstruído"; o Jev só diz se é esse. Reconstruído vai sempre para revisão.
- **Datas** (DADOS.md §Decisões 4 e 6): sem ano/sem mês → próxima ocorrência; "sexta"/"sexta que vem" →
  próxima sexta estritamente depois; "sexta da semana que vem" → semana civil seguinte (seg–dom);
  "essa segunda" já passada → null; data impossível → null + revisão (não se corrige em silêncio).
- **Confiança do composto** = mínimo das partes usadas (data; valor cru = escolha × escala).
- **"Inventou?"** tem prova independente (`run.rastreavel`): todo valor devolvido se reconstrói do texto.

## Resultados (jev-1.13.0, 2026-09-30; números completos em `resultados.md`, gerado pelo script)

Afinação: o ajuste deu 100% na primeira passada — **nenhuma pergunta nem limiar mudou**. Hash de
`perguntas.py`, `extrator.py` e `candidatos.py` registrado antes de abrir o teste; teste rodado uma vez.

| campo | ajuste (n=20) exatidão | teste (n=40) exatidão | teste: cobertura dos candidatos | teste: acerto da escolha entre cobertos | teste: automático | teste: erro entre automáticos |
|---|---|---|---|---|---|---|
| email | 1,000 | 0,975 | 8/8 | 0,875 | 39/40 | 0,026 |
| telefone | 1,000 | 1,000 | 5/5 | 1,000 | 40/40 | 0 |
| cpf | 1,000 | 1,000 | 4/4 | 1,000 | 40/40 | 0 |
| valor | 1,000 | 0,975 | 8/9 | 1,000 | 39/40 | 0,026 |
| data_visita | 1,000 | 0,925 | 13/13 | 0,923 | 37/40 | 0,027 |

**Inventou (= saída fora dos candidatos do texto): 0 nos dois conjuntos.** Isso NÃO é ausência de erro
semântico: "não posso visitar amanhã" virou data de visita — valor literal do texto, escolhido indevidamente. Custo: ~3,7–4,3 perguntas e ~940–1.030 tokens por requisição,
p50 280–330 ms, p95 450–550 ms, **US$ 0,04 por 1.000 mensagens**. Amostra pequena (teste: 4–13 casos
com valor por campo) — os números indicam, não provam.

## O que deu certo
- Seleção literal + normalização em código: telefone e CPF 100%, zero valor inventado, zero dígito trocado.
- Casos que o medo previa saíram certos: telefone designado entre dois, proposta × preço do anúncio,
  "600" com "mil" implícito (escala 0,99), extenso, "sexta da semana que vem", data sem ano, 31/11 e
  29/02/2027 barradas como impossíveis, identificador com cara de preço (`none` 0,40 → revisão).
- Fan-out + portões de código: 1 requisição por mensagem, mensagem vazia não custa nada.

## O que falhou no teste (erro de desenho — não corrigido, vira lição)
1. **Data negada virou agendamento** (EX-T030 "Não posso visitar amanhã" → amanhã, conf 0,66, automático).
   As partes leem a EXPRESSÃO de data, não se ela é afirmada. Faltou uma pergunta atômica "o autor
   propõe/confirma um dia de visita?" consumida antes das partes (lição 14: relevância antes de consumir).
   Mesma família: EX-T038 "possibilidade para sábado, mas não confirme" — salvo só pela confiança 0,36.
2. **`none` atraente demais no e-mail** (EX-T002 "Mande a confirmação para lia@…" → `none` 0,83, automático).
   A descrição de `none` dizia "no email address **of their own**": o Jev leu literal — a mensagem não
   diz que o endereço é dela. Condição extra no `none` puxa para ele (limite #1).
3. **Candidato incompleto escolhido com confiança** (EX-T034 "mil duzentos e trinta e quatro reais e
   cinquenta e seis centavos" → 1234.00, conf 0,97). O leitor de extenso não trata centavos; com um só
   candidato, a Choice escolhe ele e a confiança NÃO avisa que falta um pedaço. Falha de cobertura do
   código vira erro silencioso da escolha.
4. **Calendário**: "29/02 sem ano" deveria ir a 2028-02-29; o código só tenta este ano e o próximo
   (EX-T012). Foi para revisão, não para erro automático.

## Lições
- **O ajuste não amostrou nenhuma das famílias que falharam** (negação de data, centavos, "mande para",
  29/02). 100% no ajuste não é calibração: é ausência de caso difícil daquele tipo.
- **Cobertura dos candidatos antes do acerto da escolha.** Quando a regex não acha o valor certo, o
  Jev escolhe o mais parecido com confiança alta; só a coluna de cobertura mostra o defeito. Candidato
  que é PREFIXO de uma expressão maior ("… reais e cinquenta e seis centavos") tem de ser marcado incompleto.
- **Ler a data e decidir se ela vale são perguntas diferentes** — uma Choice de modo não carrega negação.
- **A opção `none` também é pergunta**: cada condição escrita nela é lida ao pé da letra.
- Nada disso inventou valor: o desenho segura a invenção; o que escapa é escolher a coisa errada.

## Limites (declarados)
- Não cobertos: e-mail ditado ("arroba … ponto com"), correção da parte local do e-mail, telefone sem
  DDD e sem "DDD xx" escrito (vai para revisão), número cru de 1–2 dígitos, centavos por extenso.
- Semana civil fixa em segunda–domingo; "sexta que vem" teve a parte de semana em 0,69–0,79 — perto do limiar.
- Dados sintéticos (escritos por LLM) são mais fáceis que reais; n pequeno por campo.

## Como rodar
```
python run.py              # ajuste + teste, do cache (sem gastar)
python run.py rascunho     # encanamento
JEV_MODO=gravado python run.py   # sem chave, só o cache
```
No Windows, `PYTHONIOENCODING=utf-8` para imprimir acentos.
