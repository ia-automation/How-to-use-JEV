---
name: sugestao-de-skill
description: Escolhe no máximo 1 skill entre 182 (catálogo Hermes) com 2 requisições Jev (rank amplo + reranque de 3); reduz carga de skill errada de 16,8% para 7,3% e carga desnecessária de 9,8% para 4,0% (agente claude-haiku-4-5-20251001, 488 pedidos).
tipo: receita
fonte: https://docs.typesafe.ai/cookbooks/skill_suggestion.md
snapshot: fontes/docs/llms-full-2026-09-30.txt, linhas 11409–12330
estudado_em: 2026-09-30
---

# Sugestão de skill (Skill suggestion)

## Problema
Um agente com roster grande de skills decide com pouca informação: o índice tem uma linha por skill, com a descrição truncada (Hermes: 60 caracteres por padrão; média 54). Nesse tamanho a skill que EDITA `.pptx` parece a que CRIA. Quando nenhuma skill serve, o agente ainda carrega uma, porque "a list of names invites a guess" e o preâmbulo do Hermes manda "err on the side of loading". Carregar tudo no system prompt aumenta custo, piora a seleção e causa "context rot". Solução: progressive disclosure — ler as 182 de forma barata, depois ler 3 em detalhe — e injetar UMA linha no system prompt do turno.

## Como o Jev entra
Duas requisições `client.system_one(..., model="jev-1.12")` por turno, em sequência (a 2 depende do top-3 da 1).

- **state** (ambas): `{"request": <texto do pedido>, "recent_context": ""}` (`build_state`).
- **Requisição 1 — rank_wide** (todo o roster):
  - `which` — **Choice**. `instructions`: `Which of these skills, if any, is the right one to load to help with the user's latest request?`. `criteria`: `{name: description_do_índice}` para as 182 skills (a mesma descrição truncada que o agente vê). As probabilidades = ranking.
  - 3 perguntas **Noul** de "porta" (chaves `gate::<nome>`), sem `criteria`, só `instructions`:
    - `acts_on_user_system`: `Is the assistant being asked to act on the user's files, accounts, devices, or online services, rather than only to explain or advise?`
    - `would_follow_documented_procedure`: `Would a careful expert answering this consult a specific documented procedure or set of commands, rather than answering from general understanding?`
    - `prose_suffices` (INVERTIDA): `Could a knowledgeable generalist fully satisfy this request in prose, with no tools, no documentation, and no access to the user's files or accounts?`
  - Redação: as três perguntam se uma AÇÃO é desejada, não o assunto — pergunta sobre assunto não separa "explain what a monad is" de um pedido que precisa de skill, pois ambos são software.
- **Requisição 2 — rerank** (top 3 da 1):
  - `which` — **Choice** sobre as 3 candidatas. `instructions`: `Exactly one of these skills is the right one to load for the user's latest request. Which one? Read what each actually does, not just its name.` `criteria[name] = f"{description_full} — {body[:700]}"` (descrição completa + os primeiros 700 caracteres do `SKILL.md`; o arquivo do roster guarda 1600, e há `assert EXCERPT_CHARS <= 1600`).
  - `fits::{name}` — uma **Noul** por candidata (3): `Does the skill '{name}' do the specific thing the user's request asks for? It is described as: {description_full}`. Cada uma é respondida sozinha (absoluta), então todas podem voltar baixas.
- **chamadas:** 2 por turno (1 ampla + 1 de reranque). Em cada uma, Choice + Nouls vão na MESMA requisição ("one round trip"). Em lote, usa-se `ThreadPoolExecutor(max_workers=WORKERS=8)` entre pedidos diferentes (até 488 x 2 requisições).

## O que o código faz com a resposta
Constantes: `SHORTLIST = 3`, `EXCERPT_CHARS = 700`, `GATE_THRESHOLD = 0.30`, `FITS_THRESHOLD = 0.30`.

1. Porta: `values[k] = answer.noul`; orienta as invertidas (`1 - v` para `prose_suffices`); `gate = média das 3 orientadas`. Se `gate < 0.30` -> sugere nada (`()`).
2. `ranked` = probabilidades do `which` ordenadas desc; guarda as 12 primeiras (cache pequeno); shortlist = 3 primeiras.
3. Reranque: `winner = answers["which"].choice`; `fits[name] = noul`. Se `max(fits) < 0.30` -> sugere nada (shortlist inteira descartada). Senão devolve `(winner,)`.
4. `suggest()` devolve no máximo 1 nome, ou `()`.
5. Bloco no system prompt, DEPOIS do roster (o roster fica idêntico em todos os turnos, preservando prefix caching; o `cache_control` ephemeral fica no roster, a sugestão vem após o breakpoint):
```
<skill_relevance>
Relevant to the current request: pptx-author. Ignore this if it does not fit what the user
actually asked for.
</skill_relevance>
```
   Sem sugestão, ainda envia: `No skill in the roster appears relevant to this request.` Motivo: enviar nada deixaria sem oposição a instrução "err on the side of loading" do roster. O texto "Ignore this if it does not fit" existe porque empurrar mais forte ganha conformidade também em sugestões erradas, e uma errada é pior que nenhuma. Esse texto é entrada medida: mudar uma palavra invalida o cache dos resultados.
6. O agente mantém o índice completo e seu julgamento; a linha só diz qual entrada olhar primeiro.

### Como o catálogo vira opções
- `hermes_roster.json`: 182 skills em 33 categorias (NousResearch/hermes-agent, MIT, commit fixo). Cada registro: `name`, `category`, `description` (como o índice mostra), `description_full`, `body` (início do `SKILL.md`). Só esses campos são lidos; trocar o arquivo aplica a receita a outro roster.
- Índice do agente (copiado do Hermes): categorias ordenadas, skills ordenadas por nome, linha `    - {name}: {description}` dentro de `<available_skills>`; prompt de 16.089 caracteres; descrição média 54, máx. 60.
- Escolha 1ª rodada: nome -> descrição truncada (barato, cobre tudo). 2ª rodada: só 3 candidatas com texto completo + 700 caracteres do corpo.

## Resultados medidos
Agente: `claude-haiku-4-5-20251001`; Jev: `jev-1.12`; 488 pedidos de turno único (315 cobertos por exatamente 1 skill, 171 skills distintas; 173 sem cobertura: 85 cotidianos, 42 técnicos sem skill, 46 pedindo algo específico que o roster não tem, ex.: "post this to Mastodon"). Pedidos cobertos foram escritos pelo Claude Sonnet 5 a partir do `SKILL.md` (mais fáceis que os de usuário real). Pontua só a primeira resposta do agente.

| braço | carga de skill errada (315 cobertos) | carga desnecessária (173 sem skill) |
|---|---|---|
| agente sozinho (só o roster) | 16,8% | 9,8% |
| **agente + sugestão Jev** | **7,3%** | **4,0%** |
| agente com a resposta certa (oráculo) | 2,5% | 1,2% |

- Razão: 2,3x menos cargas erradas, 2,4x menos desnecessárias.
- Dos 315 cobertos: a sugestão corrigiu 37 e quebrou 7.
- Base: dos 36 primeiros palpites errados do agente sozinho, 10 vieram da própria categoria da skill certa (erro de "vizinho parecido").
- Métricas: `wrong_load` = 1 - (primeira `skill_view` == skill coberta; turno sem carga conta como erro); `needless_load` = fração dos sem cobertura com qualquer `skill_view`.
- Latência por requisição (demos): rank amplo 0,31 s / 0,16 s / 0,16 s; reranque 0,12 s / 0,09 s / 0,09 s. Tokens coletados (`input_tokens`, `output_tokens`) mas valores não declarados no doc. Custo em dinheiro: não declarado.
- Demos: Notes.app -> gate 0,75; apple-notes 0,990 -> vence apple-notes (fits 0,60; computer-use 0,54). Pitch deck -> gate 0,76; `powerpoint` 0,700 vs `pptx-author` 0,300 no rank amplo; no reranque vence `pptx-author` (fits powerpoint 0,73, pptx-author 0,38). Mastodon -> gate 0,78; `xurl` 0,550; vence `xurl` com fits 0,56 (sugestão errada que passa nos dois filtros).

## Técnicas reutilizáveis
- Funil "barato e largo, depois caro e estreito": rank de tudo com descrição curta, releitura de 2–3 com evidência longa -> quando o roster é grande demais para detalhe completo.
- Dois tipos de pergunta por estágio: Choice decide QUAL (relativo), Noul decide SE (absoluto); Choice sempre soma 1, Nouls podem todos vir baixos -> permitem "nenhuma".
- Porta de "preciso de skill?" com perguntas sobre AÇÃO desejada (não assunto), várias formulações e média; inverter as que apontam ao contrário (`1 - v`).
- Noul por candidato ("esta candidata faz exatamente o pedido?") + limiar sobre o MÁXIMO -> descartar a shortlist inteira.
- Cada estágio pode voltar vazio (porta baixa ou fits baixo) -> sugerir nada.
- Sugestão branda e opcional no prompt ("ignore se não servir") + frase explícita de "nenhuma skill relevante" para neutralizar instrução viesada do roster.
- Sugestão injetada fora do prefixo cacheado -> roster idêntico a cada turno, cache preservado.
- Jev decide, o agente continua com julgamento próprio e índice completo (soft hint, não imposição).
- Avaliação com três braços (sozinho / com sugestão / oráculo) -> o oráculo é o teto do método; mede-se o ganho como fração da distância baseline->teto.
- Duas métricas de erro na mesma direção (errado-carregado e carregado-sem-precisar); negativos escritos para punir chute.
- Roster muito maior: dividir em blocos, ranquear cada, rodar a mesma etapa de shortlist sobre os vencedores (doc afirma que 182 cabe confortavelmente em 1 Choice).
- `JsonCache` por chave de entrada: reexecutar sem custo e com cada braço amostrado independentemente (`arm` na chave).

## Limites e pegadinhas
- Sugestão errada e confiante é mais persuasiva que nenhuma: quebrou 7 pedidos que o agente acertaria sozinho.
- O piso de erro não é zero: mesmo o oráculo erra 2,5% / 1,2% (agente nem sempre carrega a skill certa).
- Nenhum ranking salva o caso Mastodon: o gate diz "ação desejada", e a skill mais próxima (xurl, X/Twitter) vence e passa os dois filtros (fits 0,56 > 0,30). Doc: "Most requests like it are caught", sem número; o 2º passe só rejeita o que o 1º lhe entrega (aqui, 3 quase-acertos).
- No rank amplo de 60 caracteres, a skill de edição ficou à frente da de criação para um pedido de criação; só se resolve com o texto longo de cada uma. Os `fits` Nouls pontuaram a de edição mais alto enquanto o Choice escolheu a de criação — decidem coisas diferentes.
- Pedidos cobertos são mais fáceis que os de usuários reais.
- Os limiares 0,30/0,30 são dados sem justificativa própria; o doc remete a /confidence para escolhê-los. Sem análise de sensibilidade no trecho.
- Números de contagem: a taxa 16,8% de 315 corresponde a ~53 erros, mas a análise de vizinhança lista 36 "primeiros palpites errados" — os demais são turnos que não carregaram nada (contam como erro na métrica mas não entram na lista). O doc não explicita isso.
- Latências citadas são de poucas demonstrações; custo total da bateria (488 x 2) não declarado.
- Requisito de implantação: `skill_view` exige nome exato; o agente testado tinha só 4 ferramentas (`skill_view`, `terminal`, `read_file`, `web_search`).

## Esqueleto de código
```python
GATE_THRESHOLD = 0.30; FITS_THRESHOLD = 0.30; SHORTLIST = 3; EXCERPT_CHARS = 700
INVERTED = {"prose_suffices"}

def build_state(request): return {"request": request, "recent_context": ""}

def rank_wide(request):
    questions = {"which": Choice(instructions=CHOICE_INSTRUCTIONS,
        criteria={s["name"]: s["description"] for s in ROSTER})}
    for key, text in GATE_QUESTIONS.items():
        questions[f"gate::{key}"] = Noul(instructions=text)
    r = client.system_one(state=build_state(request), questions=questions, model="jev-1.12")
    ranked = sorted(r.answers["which"].probabilities.items(), key=lambda kv: -kv[1])
    values = {k.removeprefix("gate::"): a.noul for k, a in r.answers.items() if k.startswith("gate::")}
    oriented = [(1.0 - v) if k in INVERTED else v for k, v in values.items()]
    return {"ranked": ranked[:12], "gate": sum(oriented) / len(oriented)}

def rerank_questions(names, excerpt):
    q = {"which": Choice(instructions=RERANK_INSTRUCTIONS, criteria={
        n: f"{BY_NAME[n]['description_full']} — {BY_NAME[n]['body'][:excerpt]}" for n in names})}
    for n in names:
        q[f"fits::{n}"] = Noul(instructions=(f"Does the skill '{n}' do the specific thing the "
            f"user's request asks for? It is described as: {BY_NAME[n]['description_full']}"))
    return q

def suggest(request):
    wide = rank_wide(request)
    if wide["gate"] < GATE_THRESHOLD: return ()
    shortlist = tuple(n for n, _ in wide["ranked"][:SHORTLIST])
    result = rerank(request, shortlist, EXCERPT_CHARS)  # winner = answers["which"].choice
    if max(result["fits"].values()) < FITS_THRESHOLD: return ()
    return (result["winner"],)
```
