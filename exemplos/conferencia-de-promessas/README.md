# Conferência de promessas (rascunho de resposta × ficha do imóvel, pt-BR)

## Problema
Antes de enviar a resposta ao cliente, conferir cada afirmação do rascunho do atendente contra a ficha
pública do imóvel: `supported` (a ficha sustenta), `contradicted` (diz o contrário) ou `not_stated`
(não diz). "Financiamento aprovado" quando a ficha diz "proprietário analisa" é promessa inventada — o
erro caro é **deixá-la passar**. Candidato a guarda de saída da Luci (0800): a resposta gerada só sai
depois que cada afirmação recebe `manter` / `revisar` / `retirar`. A ficha leva só campos públicos:
**andar e número da unidade nunca entram** (nem no state, nem nos dados).

## Quem faz o quê
| Parte | Onde | Por quê |
|---|---|---|
| número (quartos, vagas, área, preço, condomínio, distância ao metrô) | código (`conferir.py`): extrai o número e o comparador da afirmação, acha o valor na ficha, compara com a tolerância do LEIA-ME | exato; o Jev não compara números (limite #2). Afirmação só numérica nunca chama a API |
| afirmação composta ("2 vagas cobertas", "condomínio barato, R$ 520", "4 quartos e 1 vaga" sem campo de vagas) | código confere o que consegue; se bate, o resto vai ao Jev; contradição numérica provada decide sozinha, mesmo com outra parte sem valor na ficha | o número é do código, o adjetivo/condição é julgamento |
| negação que o código não interpreta ("Não tem 2 vagas"), multiplicador desconhecido ("2,1 mi") | Jev, sem comparação numérica | polaridade indefinida ou número truncado não podem decidir (rodada 2) |
| relação semântica (possibilidade × garantia, condição, paráfrase, negação, orientação solar) | Jev, 1 Choice por afirmação, todas as afirmações da ficha numa requisição | espaço fechado de 3 opções; state compartilhado divide o custo |
| tabela de orientação solar (leste = sol da manhã…) e enums (`proprietario_analisa`) | código expande na própria ficha, em inglês | conhecimento de mundo fixo é política, não julgamento |
| ação por afirmação (manter / revisar / retirar) | código, limiares em `perguntas.py` | risco: manter promessa inventada é o erro caro, então manter exige mais confiança que retirar |

## Desenho (`perguntas.py` = Choice, glosas, limiares, baseline, critério; `conferir.py` = número e composição)
- **State**: `{"listing": {"title", "description", "fields"}, "claims": [...]}` — só as afirmações que precisam
  do Jev; campos traduzidos (`bedrooms`, `parking_spots`, `facing: "east (morning sun; no afternoon sun)"`,
  `financing: "owner evaluates case by case"`).
- **Choice** (inglês, uma por `claims[i]`): "How does the listing relate to the statement?" com regras do
  LEIA-ME (exagero = `not_stated`; possibilidade/condição não sustenta garantia; paráfrase = `supported`;
  oposto ou o que a condição exclui = `contradicted`) e `what`/`not_for`/`examples` por opção.
- **Ação**: `supported` com conf ≥ 0,7 → manter; `contradicted`/`not_stated` com conf ≥ 0,5 → retirar; resto →
  revisar. Veredito do código não tem confiança: age direto. Resposta inválida do Jev (ID faltando, opção fora
  da lista, probabilidades que não cobrem as 3 opções ou não somam 1, bool/string como número) é exceção da
  integração — validação completa em `_comum/congelamento.py` — nunca `not_stated` nem `manter`.
- **Extrator numérico** (`conferir.py`): frase só é "numérica pura" se TODAS as proposições foram interpretadas
  (número com multiplicador e unidade, comparador, "sem/não tem vaga" = 0, "vaga" sem número = ≥ 1); negação
  fora desse padrão → sem decisão numérica, vai ao Jev; número seguido de palavra que a gramática não conhece
  ("2,1 mi", "2 suítes") não é interpretado. Bateria em código, sem API: `bateria_extrator.py` (49 casos).
- **Congelamento**: manifesto `congelamento.json` (hash de `perguntas.py`, `conferir.py`, `run.py`,
  `dados/teste.json` + o critério de continuar como dicionário; hash de `_comum/` só como registro). `run.py`
  recusa o teste sem manifesto ou com arquivo mudado; congelar de novo guarda o anterior em
  `congelamentos-anteriores/`. `run.py rascunho` escreve `resultados-rascunho.md` e não toca em nada disso.
- **Noul auxiliar** "a ficha trata do assunto?" medido no ajuste: nunca agiu (onde o tópico ficou baixo a
  Choice já dizia `not_stated`), +13% de tokens → fora.
- **Baseline de código**: mesmo comparador numérico + palavra de promessa ("garantido", "aprovado", "todos") →
  `not_stated` + booleano da ficha (pet, mobiliado, financiamento) com negação + palavras da afirmação na ficha.
- **Critério de continuar/descartar** (fixado antes do teste): numéricas puras 100% · acerto da relação ≥
  baseline + 15 p.p. · promessa inventada mantida ≤ 3% · cobertura ≥ 75%.

## Resultados (jev-1.13.0, 2026-10-01; tudo em `resultados.md`, gerado pelo script)
Ajuste = 30 fichas / 104 afirmações (afinado nele); teste = 60 fichas / 200 afirmações (112 supported, 50
contradicted, 38 not_stated; 52 fichas difíceis).

### Rodada 1 (cega, congelada em 2026-10-01 11:39 — hashes `perguntas.py` `42a8405b…`, `conferir.py` `ab3bf683…`, `dados/teste.json` `c3f34fe6…`)
Teste aberto e rodado UMA vez; relatório completo preservado em [`resultados-rodada1.md`](resultados-rodada1.md)
e manifesto retroativo (gravado com os arquivos originais) em `congelamentos-anteriores/2026-10-01T11-39-00-03-00.json`.
Os números abaixo são os dessa rodada, inalterados.

| Teste (n) | código + Jev | baseline de código |
|---|---|---|
| relação certa, todas as afirmações (200) | **0,930** (186/200) | 0,720 |
| numéricas puras pelo código (71) · compostas (16) · só Jev (113) | 0,972 (69/71) · 0,875 · 0,912 | 0,972 · 0,375 · 0,611 |
| ação: cobertura · erro entre decididos · revisões | 95,0% · 3,2% (6/190) · 10 | 100% · — · 0 |
| **promessa inventada mantida** (gabarito contradicted/not_stated → manter; 88) | **1/88** (sem faixa: 5/88) | 27/88 |
| requisições por ficha · tokens · p50 · p95 | 0,9 · 1.903 · 260 ms · 318 ms | 0 |
| US$ por ficha · por mil fichas · por mil afirmações | 0,00008 · **0,080** · 0,024 | 0 |

Ajuste: 0,962 (100/104), baseline 0,788, 0/48 promessa mantida, numéricas puras 32/32, 7 revisões (todas
com relação certa, conf 0,28–0,55).

**Critério (rodada 1):** (2) 0,930 ≥ 0,870 ✓ · (3) 1,1% ≤ 3% ✓ · (4) 95% ≥ 75% ✓ · **(1) numéricas puras 69/71 ✗** —
dois erros de código (abaixo). O resultado fica como rodou; as correções são pendência da próxima versão.

### Rodada 2 (pós-revisão; o teste já tinha sido visto, portanto NÃO é cega)
Correções da revisão adversarial (Codex, 2026-10-01), só de código e relatório — a pergunta ao Jev não mudou.
Manifesto novo `congelamento.json` (gravado em 2026-10-01 12:07; o de 12:06, estado intermediário da mesma
aplicação em que "custa" sobrava em "O condomínio custa R$ 520", foi para `congelamentos-anteriores/`).
Rodado com `JEV_MODO=auto`: **0 requisição nova no ajuste e no teste** (o único state que mudou, CP-T009, deixou
de precisar do Jev); 2 requisições novas no rascunho, vindas do estado intermediário (5.545 tokens, US$ 0,00023).
O que mudou, item a item:

| Número (teste) | Rodada 1 | Rodada 2 | Por quê |
|---|---|---|---|
| numéricas puras pelo código · acerto | 71 · 69/71 (0,972) | 72 · 70/72 (0,972) | CP-T009/a3 "Custa 1,9 milhão" sai da composta para o código e acerta pelo motivo certo: 1.900.000 × 2.100.000 (antes 1,9 × 2.100.000, acerto por acidente); os 2 erros são os mesmos (T015/a2, T038/a3 — fora da lista aplicada) |
| compostas · acerto | 16 · 0,875 | 15 · 0,867 | só a saída de T009/a3; nenhuma outra afirmação mudou de caminho, relação ou ação |
| relação certa (200) · só Jev (113) · cobertura · revisões | 0,930 · 0,912 · 95,0% · 10 | **iguais** | nenhuma resposta do Jev mudou |
| promessa inventada mantida (88) | 1/88 (sem faixa 5/88) | **igual** | idem (T044/a1 continua a única) |
| requisições · tokens por ficha · US$ por mil fichas | 54 · 1.903 · 0,0799 | 53 · 1.884 · 0,0791 | CP-T009 virou 100% código |

Ajuste: igual em tudo (0,962; 32/32 numéricas; 28 requisições por desenho). Critério (1) continua ✗ (70/72):
os dois erros restantes são os itens 1 e 2 de "O que falhou", que não estavam na lista aceita da revisão.

Correções sem efeito nos números deste conjunto (o conjunto não tinha as frases; a bateria `bateria_extrator.py`
tem, 49 casos em código): polaridade — "Tem 3 quartos e vaga" × `vagas: 0` virava `supported`/manter (a regra
"vaga sem número = ≥ 1" só disparava sem número na frase), "Não tem 2 vagas" × `vagas: 2` idem ("nao" era
descartado como palavra de ligação); agora o primeiro é `contradicted` pelo código e o segundo vai ao Jev; ponto
de milhar — "A 1.200 m do metrô" na descrição era partido no "." e virava 200 m quando o campo faltava (nos dados
as duas fichas com 1.200/1.800 m têm o campo, por isso não apareceu); multiplicador desconhecido ("2,1 mi", "2,1
bilhões") não compara truncado, vai ao Jev; campo ausente numa dimensão não apaga contradição provada em outra
("Tem 4 quartos e 1 vaga" × `quartos: 3`, vagas ausente → `contradicted`); distribuição da Choice validada
inteira antes de decidir (nenhuma resposta gravada era inválida). Na rodada 2 nada disso vale como aprovação
cega: a rodada que conta como teste é a 1.

## O que deu certo
- **Divisão número/semântica**: 71 afirmações numéricas resolvidas sem chamada; nenhuma delas virou promessa
  mantida. "Custa 890 mil" × "R$ 890.000", "abaixo de mil", "menos de 1,5 km", "3 quartos e 3 vagas" (vagas
  errado), "uns 5 minutos" × 400 m — tudo em regex + tolerância do LEIA-ME.
- **As famílias de promessa** que motivam o exemplo saíram limpas: possibilidade×garantia 10/10, vaga
  rotativa×privativa 6/6, negação 11/11, paráfrase negativa 2/2 — e o baseline faz 0,00 nas vagas e 0,70 na
  possibilidade.
- **A faixa segurou a família mais difícil**: "aceita pet" diante de permissão condicionada (3 casos, Jev
  disse `supported` a 0,47–0,66) foi para revisão; sem faixa seriam 3 promessas mantidas a mais (curva: 0,5/0,5
  → 3/73; 0,7/0,5 → 1/73; 0,9/0,5 → 0/73 com cobertura 0,905).
- **Uma requisição por ficha**: 260 ms, US$ 0,08 por mil rascunhos conferidos.

## O que falhou (visto no teste — NÃO corrigido, vira lição)
1. **T015 a2 "Menos de 3 minutos a pé" × 250 m** (código → `contradicted`; gabarito `supported`). Converti 3 min
   em 240 m e apliquei "<" ao pé da letra; a tolerância de ±50% dos minutos só valia para igualdade. Estimativa
   em minutos precisa da faixa também nos comparadores.
2. **T038 a3 "Área total de 78 m²" × `area_m2: 62` (útil), descrição "(78 m² total)"** (código → `contradicted`;
   `supported`). Tratei "terreno" como área à parte, não "total". O LEIA-ME avisava: construída ≠ terreno ≠ total.
3. **T041 a2 "Dá para alugar vaga perto" × `vagas: 0`** (código → `contradicted`; `supported`). A regra "vaga sem
   número = pelo menos 1", criada no ajuste para "Tem vaga" × `vagas: 0`, disparou numa frase que não afirma
   vaga do imóvel. Regra nascida de UM caso do ajuste não generalizou — a mesma lição da triagem.
4. **T057 a3 "Tem 1 vaga escriturada" × `vagas: 2` (1 escriturada + 1 rotativa)** (código → `contradicted`;
   `supported`, Jev dizia `supported` 1,00). Na composta, o número contradito vence sozinho — mas o qualificador
   restringe o conjunto contado. Número ≠ campo quando há adjetivo: a composta com número divergente deveria
   ir a revisão, não decidir.
5. **T044 a1 "Fica perto do metrô" × 1.800 m** (Jev `supported` 0,85 → **manter**: a única promessa mantida).
   O LEIA-ME fixa: palavra vaga contra número = `not_stated` (≥ 2 km, `contradicted`). É regra de número — era
   do código, e eu a deixei para o Jev, que julgou plausibilidade com confiança alta. Limiar não pega.
6. **T017 a3 "Aceita financiamento pela Caixa" × "financiamento bancário"** (`not_stated` 0,95 → retirar;
   `supported`). "Instância do genérico" não estava nas regras; a instrução "mais específico que a ficha =
   not_stated" levou o Jev ao pé da letra. Erro barato (retira fato verdadeiro).
7. **T024 a3 "Pega sol da tarde" × "sol da manhã na sala"** sem campo de orientação (`not_stated` 0,66;
   `contradicted`). A glosa de sol só entra quando há campo; "manhã e tarde excludentes" ficou fora. Ação certa.
8. **T029 a2 / T034 a1 e a3** (reforma parcial, móveis que podem sair): Jev `contradicted` onde o gabarito é
   `not_stated` — ação `retirar` certa; a relação discorda do rotulador na fronteira exagero × oposto.
9. **T020 a1 "É um lugar seguro" × "segurança 24h"** (`supported` 0,39 → revisão; opinião). A faixa segurou.

## Lições
1. **Toda regra numérica do LEIA-ME é do código, inclusive as que parecem semânticas** ("perto" contra 1,8 km):
   o Jev julga plausibilidade e vem confiante — foi a única promessa que passou.
2. **Composta com número divergente vai a revisão, não a `retirar`**: o qualificador ("escriturada", "total")
   muda o que o número conta. E comparador sobre estimativa (minutos) leva a tolerância junto.
3. **Regra de código nascida de um caso do ajuste** ("tem vaga" = ≥ 1) falhou no teste — igual ao piso 0,9 da
   triagem. O remédio é o mesmo: a regra tem de vir da especificação, não do caso.
4. **A faixa assimétrica (0,7 manter / 0,5 retirar) paga onde o modelo hesita certo**: os 3 "aceita pet"
   condicionados vieram `supported` a 0,47–0,66; manter exige 0,7. No ajuste a faixa só custava cobertura.
5. **Orientação solar como glosa no campo funcionou** (16 casos, 15 certos); o que falhou foi o caso SEM campo.
   Regra de mundo fixa cabe no state quando o código sabe o enum; na descrição livre, só o Jev lê.
6. **O baseline mostra onde o Jev vale**: 0,72 × 0,93 no total, mas 0,00 × 1,00 em vaga rotativa×privativa e
   0,27 × 0,55 em condição — o número o baseline resolve igual; a relação, não.

## Limites
- Dados sintéticos escritos por LLM (Fable), um rotulador só; fichas curtas e consistentes (campo e
  descrição nunca se contradizem) — mais limpas que fichas reais de portal. n = 30/60 fichas, 104/200
  afirmações: 1 afirmação = 0,5 p.p. no teste; 1 promessa mantida = 1,1 p.p. em 88.
- Uma versão (`jev-1.13.0`), uma rodada; chamadas repetidas variam ~0,01 (máx. 0,15): os três "aceita pet"
  (0,47–0,66) e "vem com geladeira" (0,51) podem trocar de lado da faixa.
- O extrator numérico cobre as 6 dimensões da ficha e o português das afirmações deste conjunto; fora disso
  a afirmação cai no Jev (medido: 1 numérica do gabarito caiu no Jev e acertou).
- O baseline é fraco de propósito (20 minutos de código); a Luci real teria o LLM gerador — não medido aqui.

## Como rodar
```
..\..\.venv\Scripts\python.exe run.py            # ajuste + teste (recusa sem congelamento.json ou com arquivo mudado)
..\..\.venv\Scripts\python.exe run.py rascunho   # 5 fichas, só encanamento → resultados-rascunho.md
..\..\.venv\Scripts\python.exe run.py ajuste     # afinação, nos dois desenhos
..\..\.venv\Scripts\python.exe run.py congelar   # roda o ajuste e grava o manifesto antes de abrir o teste
..\..\.venv\Scripts\python.exe bateria_extrator.py   # extrator numérico, 49 frases, sem API
set JEV_MODO=gravado                              # reproduz tudo do cache/, sem chave
```
