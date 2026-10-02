# Dados do `juiz-de-eval` — decisões de rotulagem

Escrito ANTES dos casos (2026-10-01, rotulador: fable). Esquema e regras gerais em
[BRIEFING-2026-10-01-casos-novos.md](../../BRIEFING-2026-10-01-casos-novos.md) (item B) e [DADOS.md](../../DADOS.md).
Domínio: atendimento imobiliário e dúvidas de uso de um CRM, pt-BR. Nada de dado pessoal real; endereços e
domínios fictícios; nunca andar nem número de unidade.

## Formato da `pergunta`
Quando o critério depende do que o atendente sabia, a `pergunta` começa com `Contexto: …` (trecho da ficha ou do
sistema que o atendente tinha) e segue com `Cliente: …` ou `Usuário: …`. O juiz vê tudo isso como a pergunta;
não existe campo separado de ficha. Sem `Contexto:`, o juiz só tem o texto da resposta.

## `veredito` por critério
- `true` = a resposta atende; `false` = não atende; `null` = indecidível pelo texto disponível.
- **Atende de forma implícita conta como `true`**: "vou verificar com o proprietário e confirmo" atende "informa
  que a visita precisa de agendamento prévio"; "o regulamento não permite animais" atende "informa que não aceita
  pet". Implícito por conhecimento de mundo comum ("face leste" → sol da manhã) também conta.
- **Critério negado** ("não promete desconto", "não garante aceitação", "não culpa o usuário"): `true` quando a
  coisa proibida está ausente; `false` quando aparece, mesmo cercada de simpatia. "Costuma analisar", "não
  garanto" → não promete.
- **"Não inventa …"**: `false` quando a resposta afirma qualquer fato sobre o imóvel/produto que o `Contexto:` não
  sustenta — inclusive inferência plausível ("é de fundos, bem silencioso"; "650 m, uns 8 minutos a pé"; "rua
  tranquila para estacionar"). `null` quando a resposta afirma um valor/fato e **não há contexto** para comparar, ou
  quando o que aparece é regra geral de mercado com ressalva ("costuma ser 20%, varia pelo banco").
- **Repete a pergunta sem responder** → `false` em "responde à pergunta" / "responde se …"; o tom pode ser `true`.
- **Resposta longa que enterra a informação** → critério de conteúdo `true` (a informação está lá); o tamanho é
  pego pelo critério formal.
- **Responde outra pergunta** (valor do aluguel quando se perguntou se inclui condomínio) → `false` no "responde".
- **Resposta vaga** ("dá pra criar nas configurações" para "indica o caminho") → `false`: caminho pede trilha.
- **Tom cordial**: `false` para resposta seca ou que culpa ("confere aí", "você filtrou errado"); `true` não exige
  saudação, exige ausência de hostilidade e algum cuidado.

## Critérios `formal` — são do código, não do Jev
O veredito é o resultado da regra, nunca julgamento. Regras que o construtor deve implementar igual:
- **Contagem de frases**: frase = trecho terminado por `.`, `!` ou `?` (ou pelo fim do texto). Reticências `…`/`...`
  contam uma. Ponto dentro de número (`1.250.000`, `R$ 450.000,00`), de URL ou de abreviação (`Av.`, `R$`) **não**
  encerra frase. Pergunta retórica seguida de resposta são duas frases. Casos com 4 frases muito curtas existem de
  propósito: o Jev tende a julgar "curta" pelo tamanho, o código conta.
- **Contém R$**: a sequência literal `R$`.
- **Contém um link**: a sequência `http`.
- **Contém um horário**: regex `\d{1,2}h(\d{2})?\b` ou `\d{1,2}:\d{2}`.
- **Contém a palavra X**: busca sem diferenciar maiúsculas; acentos como escritos.
- **Não contém emoji**: nenhum caractere fora do BMP nem nos blocos de emoji/símbolos pictográficos.
- **Termina com uma pergunta**: último caractere não branco é `?`.
- **Tem no máximo N caracteres**: `len` do texto.
Pelo menos 1 em 5 critérios do conjunto é `formal`; quase toda resposta tem um.

## Famílias de caso difícil (em `ajuste.json` E `teste.json`; `nota` começa com "difícil:")
1. Atende de forma implícita (agendamento, negativa, alerta de lead parado).
2. Atende e acrescenta fato falso (critério "não inventa" → `false`; inferência plausível conta).
3. Critério negado ("não promete desconto", "não garante", "não culpa").
4. Resposta longa que enterra a informação (conteúdo `true`, formal de tamanho `false`).
5. Repete a pergunta sem responder (ou responde outra pergunta).
6. Critério formal que o Jev erraria: 4 frases curtíssimas (≤ 3 → `false`); ponto de milhar que não encerra
   frase (≤ 2 → `true`).
7. `null`: valor afirmado sem contexto; regra geral de mercado com ressalva.
8. Tom: cordial sem responder; seco e culpando o usuário.
9. Resposta vaga ou parcial (um de dois itens perguntados).

## Contagens (validação de 2026-10-01, zero erros; os critérios formais foram recomputados pelas regras acima e
batem com todos os vereditos rotulados)
| arquivo | respostas | critérios | formais | difíceis | vereditos `null` |
|---|---|---|---|---|---|
| `rascunho.json` | 5 | 13 | 4 (31%) | 0 | 0 |
| `ajuste.json` | 30 | 77 | 19 (25%) | 22 (73%) | 3 |
| `teste.json` | 57 | 139 | 35 (25%) | 40 (70%) | 5 |

Por família (ajuste / teste): implícito 2/5 · inventa 4/9 · negado 4/7 · longa 1/3 · repete/outra pergunta 3/2 ·
formal que o Jev erraria 2/3 · null 2/5 · tom 3/4 · vaga/parcial 2/4 · fáceis 7/15.

Ambiguidades decididas pelo rotulador: inferência plausível ("silencioso", "8 minutos a pé") conta como invenção;
valor sem contexto é `null`, não `false`; regra geral de mercado com ressalva é `null`; "face leste" atende "sol da
manhã" (implícito por conhecimento de mundo, limítrofe); resposta vaga ("nas configurações") não atende "indica o
caminho"; "não informa" sobre recuperação é `false`, não `null`.
