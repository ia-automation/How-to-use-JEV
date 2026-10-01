---
name: primitivas
description: As 3 perguntas do Jev — Choice (qual opção, ≤255), Score (posição em 2–10 níveis ordenados), Noul (probabilidade de sim, sem confidence); formato de cada resposta, como escolher e como escrever bem.
tipo: conceito
fonte: https://docs.typesafe.ai/primitives · /primitives/choice · /primitives/score · /primitives/noul · /api
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 13397–14703 e 160–430
estudado_em: 2026-09-30
---

# Primitivas (perguntas)

Contrato mental: `dados relevantes → state + questions → answers → lógica e efeitos do aplicativo`.

Toda pergunta tem um **ID** no mapa (NÃO vai para o modelo) e `type`.
Choice/Score exigem `criteria`. `instructions` é opcional/nulo no OpenAPI v0.2.0,
apesar do campo obrigatório na página HTTP; omitida ou `null` a API respondeu 200
[testado 2026-09-30, [medicoes](../evidencias/medicoes-2026-09-30.md)]. Escreva a pergunta completa nele
como prática de desenho, mesmo que o ID pareça autoexplicativo. IDs e relações de registros
precisam aparecer no state ou na instrução: embutidos só no nome da pergunta (`q_registro_123`),
não informam o modelo.

| Tipo | Responde | `criteria` | Resposta |
|---|---|---|---|
| **Choice** | qual destas opções? (sem ordem) | mapa `opção → descrição` (ou `null`), **até 255 opções** | `choice`, `probabilities` (somam 1), `confidence` |
| **Score** | em que nível? (ordenado) | array de níveis do baixo ao alto, **2 a 10** | `score` (média ponderada, pode cair entre níveis), `legend`, `probabilities`, `confidence` |
| **Noul** | isto é verdade? | opcional: `{"true": ..., "false": ...}` | `noul` ∈ [0,1] = P(sim). **Sem `confidence`** |

## Como escolher
- **Choice**: resposta é uma de um conjunto conhecido sem ordem (departamento, tipo de documento,
  linguagem). Dê a lista **inteira** (opção extra custa poucos tokens) e inclua `other` / `none of
  the above` quando a lista pode não cobrir tudo.
- **Score**: resposta é posição num espectro que você consegue descrever em degraus (gravidade,
  frustração, nível de experiência).
- **Noul**: sim/não limpo, em que a probabilidade é o sinal útil (tem PII? pediu reembolso?).
- Na dúvida, o tipo cuja resposta o código usa direto: Choice → N caminhos; Score → limiar; Noul → `if`.
- **Noul ≠ escala.** Noul 0,5 = "sim e não igualmente prováveis", NÃO "médio". "Forte em Python?"
  como Noul deu 0,03 / 0,14 / 0,81 / 0,92 em 4 candidatos; como Score de 4 níveis deu 0,0 / 1,0 /
  2,05 / 2,89 — só o Score cai perto de um nível que você escreveu. Grau → Score.
- **Choice ≠ N Nouls.** Choice é relativo (sempre há vencedor, soma 1); Noul é absoluto (todos podem
  ser baixos). Se várias condições podem coexistir (duas intenções), use perguntas separadas; a
  distribuição da Choice não é um conjunto de rótulos independentes. Uma opção explícita `none` pode representar "nenhuma serve"
  ([extracao-de-valor-pre-parseado](../receitas/extracao-de-valor-pre-parseado.md)). Noul de existência/adequação é outro sinal
  útil; Choice com apenas candidatos reais não representa ausência.

## Choice — detalhes
- Nomes das opções E descrições vão ao modelo: escreva descrições que **separem** as opções.
- `null` quando o nome basta (`{"calm": null, "frustrated": null, "angry": null}`).
- `confidence` cai quando a probabilidade se divide. Exemplo do doc (ticket ambíguo): `department`
  returns 0,61 / billing 0,35 → confidence 0,42; `requested_resolution` refund 0,40 / replacement 0,34 /
  exchange 0,24 → confidence 0,20.
- Uso da distribuição, não só do vencedor: "segundo time com probabilidade > 0,25 recebe cópia".
- Opções parecidas que o modelo confunde → descrição em objeto `what` / `not_for` / `examples`
  ([estrutura-nas-perguntas](estrutura-nas-perguntas.md)).
- Taxonomia profunda → uma Choice por nível, andando a árvore em código ([classificacao-hierarquica](../receitas/classificacao-hierarquica.md)).
- Lista pequena e completa não precisa de busca preliminar. Catálogo grande: recuperar candidatos ou
  classificar em etapas; a recuperação também precisa ser avaliada, porque a Choice não recupera a opção
  que ficou de fora.
- Teto: 255 opções [doc]; 256 → **400** "Too many choices…", 255 → 200; Choice de 1 opção → 200 com
  confiança 1,0 (inútil) [testado 2026-09-30, [medicoes](../evidencias/medicoes-2026-09-30.md)].

## Score — detalhes
- Nível = posição no array (0, 1, 2…). `score = Σ nível × probabilidade` (ex.: 0×0 + 1×0,57 + 2×0,43 = 1,43).
- **Cada nível é avaliado sozinho**: o modelo não vê o número nem os vizinhos. "Pior que o anterior"
  não significa nada; números na descrição não ajudam. Níveis só com números (`["0","1","2"]`) no bug
  cosmético deram 0,55 / conf 0,33; com descrições, 0,0 / conf 1,0.
- **Descreva situações, não graus**: "Broken or degraded feature, but workaround exists" ✓ /
  "Moderately severe" ✗.
- Quantos níveis? Tantos quantos você descreve distintamente, até 10. Três está bom.
- Uma dimensão por Score ("pontual e esperto e experiente" = 3 Scores).
- Extremo raro que exige ação diferente ganha nível próprio ("abusivo ou ameaçador" além de "muito bravo").
- Mesmo `score` pode vir de distribuições diferentes (1,0 = tudo no nível 1 OU metade em 0 e 2): leia
  `probabilities` e `confidence` junto. Fracionário serve para **ordenar** ou arredondar ao nível.
- **Não usar o score para reconstruir magnitude numérica** entre níveis ([limites-jev-1-13](limites-jev-1-13.md)).
- Para combinar Scores de tamanhos diferentes: normalizar `score / (len(criteria) - 1)` → 0..1.
- Confiança baixa em Score = níveis se sobrepõem para esse state, a pergunta mede >1 coisa, ou o state
  não diz o bastante.
- SDK Python: `probabilities` e `legend` do `ScoreAnswer` são chaveados por **inteiro**; no JSON da
  API, por **string**.
- Faixa 2–10 [doc]. O OpenAPI só exige lista não vazia, sem teto declarado; JS exige ao menos 2.
  Medido em 2026-09-30: 11 níveis → **400** "Too many score levels. Must have at most 10"; 1 nível → 200
  com confiança 1,0 (inútil); nível `null` → 422 [testado, [medicoes](../evidencias/medicoes-2026-09-30.md)].
  Contrato completo: [api-http](../construir/api-http.md).
- `legend` de níveis estruturados devolve os objetos completos (exemplo oficial).
  Score 1,43 em [0;0,57;0,43] é posição esperada, não fração de clientes sem contorno.
  Confiança 1,0 descreve concentração da resposta, não garante acerto.
- Outra conta do mesmo tipo: probabilidades 0,2 / 0,5 / 0,3 em três níveis dão média 1,1 — não é
  porcentagem de qualidade nem medição física.

### Exemplos publicados de Score (página `/primitives/score`)
Componente ScoreExplorer (dados só na página individual; score / confiança / probabilidades):
| Pergunta (níveis) | Resultado |
|---|---|
| gravidade de bug, "Export button crashes … Safari" (3) | 1,43 / 0,35 / [0; 0,57; 0,43] |
| formalidade da roupa, blazer + camiseta + jeans + mocassim (5: gym clothes → black tie) | 1,86 / 0,89 / [0; 0,14; 0,86; 0; 0] |
| aderência do candidato (4: completely unrelated → deep direct experience) | 2,52 / 0,52 / [0; 0; 0,48; 0,52] |
| frustração do cliente, ticket do spinner "third time … I'm done" (3) | 1,26 / 0,61 / [0; 0,74; 0,26] |
| detalhe do relato, mesmo ticket (4) | 3,0 / 1,0 / [0; 0; 0; 1,0] |

Tabela "Reading a Score" (gravidade, 3 níveis): botão desalinhado por alguns pixels 0,0 / 1,0 ·
exportar PDF não faz nada, CSV funciona 1,0 / 1,0 · PDF em spinner, parte da equipe diz que CSV funciona
1,11 / 0,84 [0; 0,89; 0,11] · exportar trava configurações no Safari 1,43 / 0,35 · ninguém loga, erro 500
2,0 / 1,0. Com 4–5 níveis a `confidence` não segue a aproximação `(n·máx−1)/(n−1)` ([confianca](confianca.md)).

## Noul — detalhes
- **Noul não é `null`**: é o nome do tipo (grafia confirmada na interface do vídeo 2, 23:18, e no doc).
- O número é resposta e certeza ao mesmo tempo. Exemplos reais (`is_human_escalation`): "Thanks, that
  fixed it!" 0,02 · "How do I reset my password?" 0,07 · "I need this sorted today" 0,26 · "Are you a
  bot?" 0,40 · "any way to speak to someone about my invoice?" 0,84 · "Can I please just talk to a
  real person?" 0,99.
- Limiar pelo custo do erro: 0,5 quando sim/não são igualmente fáceis; **subir** quando falso-sim é
  caro (acionar alguém, reembolsar); **baixar** quando perder um sim é caro (segurança). Faixa do meio
  → humano (padrão `YES = 0.8`, `NO = 0.2`).
- Uma condição por Noul ("bravo E pede reembolso" = 2 Nouls).
- Frase em que alto = sim: "contém dado pessoal?" ✓ / "está livre de dado pessoal?" ✗ (inverte).
- Afirmação funciona como pergunta ("The customer is requesting a refund") — testar as duas.
- Fronteira inequívoca ("any Python experience?"); se sutil, `criteria` true/false. Testar com e sem
  criteria e ficar com o melhor. **Nunca** `true` descrevendo "não" (contradição piora — [limites-jev-1-13](limites-jev-1-13.md) #7).
- Padrão de código: um Noul por registro candidato, gerado em código, IDs com o id do registro
  (`same_as_record_18`), tudo numa requisição.

## Uma chamada, muitas perguntas
- Perguntas sobre o mesmo state vão **juntas**: paralelas, isoladas, tempo quase igual, custo = tokens
  das perguntas extras (baratos). "Perguntar algo que talvez não use é quase de graça." A ordem das
  perguntas no JSON não cria sequência de raciocínio; "use a resposta da pergunta X" dentro de outra
  pergunta do mesmo request não funciona.
- Segunda requisição só quando o código **não consegue montar** a segunda sem a primeira resposta
  (buscar mais dado, montar outro state, escolher as próximas opções). Ver [como-construir](../construir/como-construir.md).
- Agentes de código caem no hábito "uma pergunta por chamada" — evitar.

## Relacionados
[state](state.md) · [confianca](confianca.md) · [estrutura-nas-perguntas](estrutura-nas-perguntas.md) · [fan-out-especulativo](../construir/padroes/fan-out-especulativo.md) ·
[pontuacao-composta](../construir/padroes/pontuacao-composta.md) · [api-http](../construir/api-http.md)
