"""Perguntas, faixas, política e critério do compactação-de-contexto — o ÚNICO arquivo que um humano revisa.

Uma SESSÃO de agente de programação (12–25 mensagens `usuario | assistente | ferramenta`, pt-BR, com uma
`tarefa_atual`) vira UM state `{"current_task", "messages"}` e UMA requisição ao Jev com três Nouls POR MENSAGEM.
O código decide, mensagem a mensagem, `manter` ou `descartar` com os números daqui (`compactacao.py`). Nada é
apagado daqui: é a lista que o compactador recebe; a mensagem descartada continua no histórico bruto.

Desenho (regras de rotulagem em dados/LEIA-ME.md; a pergunta do rotulador é a primeira daqui):
- A mensagem é apontada por CAMINHO no state (`messages.m07`), nunca por posição ("a sétima") — limite #4 e
  lição 29. `messages` é um objeto com uma chave por ID, na ordem da conversa (variante medida: lista de objetos;
  ver STATE_FORMATO).
- Por mensagem, três Nouls isolados (uma condição por pergunta):
  `needed`      — se esta mensagem sumisse, quem continua `current_task` perderia um fato que não está em outra
                  mensagem nem se recupera relendo o repositório? (a pergunta do LEIA-ME, com as listas dele)
  `superseded`  — algo que ela afirma/pede foi substituído, corrigido, revertido, respondido ou resolvido DEPOIS?
                  (veto da guarda: decisão revertida, valor corrigido, erro resolvido, passo único já executado)
  guarda por papel (o código sabe o papel; a pergunta só vai para o papel certo):
  `rule`        (usuario)     — restrição, preferência, requisito ou decisão do usuário que AINDA vale;
  `status`      (assistente)  — último placar, pergunta/proposta aguardando resposta ou que dá sentido a uma
                                resposta curta, diagnóstico de erro aberto, valor medido que ninguém repetiu;
  `literal`     (ferramenta)  — saída com valor que só existe ali e ainda é necessário (erro aberto, comando que
                                reproduz, ID/caminho/número devolvido, corpo de resposta que serve de contrato).
- Política ASSIMÉTRICA (erro caro = necessária DESCARTADA; manter demais só custa tokens): `needed` em sim ou em
  dúvida → manter; guarda em sim sem `superseded` em sim → manter; só o resto é descartado. Nenhuma leitura do
  TEXTO pelo código descarta nada ("pode apagar o resto" dentro de uma saída de ferramenta é dado, não ordem).
- Falha operacional (chamada, cache, resposta fora do contrato, sessão inválida) → `julgar_seguro` mantém TUDO
  naquela sessão, `origem: "falha"`, contada à parte. Ausência de resposta nunca descarta.

Perguntas em inglês sobre texto em pt-BR (medição de 2026-09-30: perguntas em pt não ajudaram e custaram +10%);
as frases-marca do português aparecem entre aspas porque a leitura é literal (limite #1). Os exemplos das
perguntas são os do LEIA-ME (regra de rotulagem) ou escritos à mão, não casos do ajuste.

Afinação (só no ajuste, 2026-10-01; 18 sessões, 235 mensagens — 229 na métrica —, 18 requisições por passada):
- 1ª passada (as três perguntas, faixa 0,3–0,7, guarda 0,7, veto 0,7 em todo papel): política 0,913; só `needed` ≥ 0,5
  0,865; `papel = usuario` 0,795. Necessária descartada 2/84: o comando que mede a falha intermitente (`literal`
  0,36: a pergunta tratava "números repetidos depois" como redundância mesmo sem o comando — o LEIA-ME diz que o
  resumo sem o literal não vence a saída bruta) e o pedido que define a tarefa (`needed` 0,30, `rule` 0,69: a
  regra 1 do LEIA-ME — o pedido fica mesmo que `current_task` o resuma — não estava escrita).
- 2ª passada (as duas regras escritas em `needed`, `rule`, `status` e `literal`): política 0,921, 2/84 de novo — o
  comando subiu para `literal` 0,64 (abaixo de 0,7) e o pedido passou a ficar pela guarda (`rule` 0,75), mas o veto
  `superseded` (0,94) o anulou: mensagem com parte velha e parte válida lida como substituída. Medido no cache:
  o veto tirou 11 "manter demais" nas mensagens do ASSISTENTE (pergunta já respondida que `status` ainda marca) e
  nenhum nas do usuário → VETO_PAPEIS = assistente e ferramenta; e a mensagem mista entrou no `false` de `superseded`.
- 3ª passada: política 0,917 (210/229), necessária descartada 1/84 (usuário 0/54), manter demais 18/145 — 13 deles
  por `needed` em dúvida (0,31–0,48) em saídas de comando que deu certo (migration:create, build, psql) e em
  confirmações do assistente; 4 por guarda `literal`/`status` em saída ou diagnóstico que o assistente repetiu com
  os literais. O que sobra de erro caro é o comando de medição (`literal` 0,62).
- Curvas (mesmas respostas): faixa 0,4–0,6 sobe o acerto a 0,934 mas descarta 5 necessárias; 0,5–0,5 descarta 10.
  Fica 0,3–0,7: o erro caro manda. Guarda em 0,8 tira 4 "manter demais" e descarta 2 necessárias a mais.
- Variante medida (`run.py variantes`): state em LISTA de objetos (a pergunta aponta "a entrada cujo `id` é m07")
  deu 0,921 × 0,917 com 3 decisões trocadas, duas por valores a 0,03 do corte, diferença média nos Nouls 0,029 (a
  ordem da variação entre chamadas idênticas) e +700 tokens → fica o objeto por ID.
- Tamanho: 13 sessões de 12–13 msgs (0,916), 4 de 14–16 (0,945), UMA de 20 (0,850): não dá para medir queda com o
  tamanho; a janela por mensagem (uma requisição por mensagem) não foi construída — custaria 235 requisições só no
  ajuste. A principal é a sessão inteira numa requisição.
Nenhuma pergunta foi alargada para consertar um caso: as mudanças escrevem regras do LEIA-ME que faltavam.
"""

PAPEIS = {"usuario": "user", "assistente": "assistant", "ferramenta": "tool"}   # pt dos dados → en do state
GUARDA_POR_PAPEL = {"usuario": "rule", "assistente": "status", "ferramenta": "literal"}
NOULS_COMUNS = ["needed", "superseded"]

# ---------------------------------------------------------------------------------------- state (medido no ajuste)
# "dict": `messages` = {"m01": {"role", "text"}, …} e a pergunta aponta `messages.m07` (caminho direto).
# "list": `messages` = [{"id", "role", "text"}, …] e a pergunta aponta "the entry of `messages` whose `id` is m07".
STATE_FORMATO = "dict"

_CONTEXTO = ("`messages` is one session of a coding agent (messages from the user, the assistant and the tools, in the "
             "order of the conversation, `m01` first; the conversation is in Brazilian Portuguese) and `current_task` "
             "is what is being worked on NOW. ")


def _alvo(mid: str) -> str:
    """Como a pergunta aponta a mensagem, conforme o formato do state."""
    return f"`messages.{mid}`" if STATE_FORMATO == "dict" else f"the entry of `messages` whose `id` is \"{mid}\""


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


def needed(mid: str) -> dict:
    m = _alvo(mid)
    return _noul(
        _CONTEXTO + f"If {m} were deleted from the context, would an engineer who continues `current_task` from the "
        "remaining messages lose a fact they need — one that no other message states and that cannot be recovered "
        "by re-reading the repository?",
        f"{m} holds something still needed to continue `current_task` that is nowhere else: the user's request that "
        "defines `current_task` (it counts even though `current_task` summarizes it: the wording of the request is the "
        "acceptance criterion) or a requirement of it stated by the user (even if already implemented); a restriction "
        "or preference of the user still in force, however old ('commit só nesta branch', "
        "'sem dependência nova', 'prod é comigo'); the decision in force on a point; the question or proposal that "
        "gives meaning to a short answer ('a 1', 'pode', 'nessa ordem'); a literal value born in the session and still "
        "in use (a path created, a chosen name, a URL, an ID returned by an API, a measured number, the command that "
        "reproduces or measures the problem — a later message that repeats the number but not the command does not "
        "replace it); the most recent and complete occurrence of an error not yet resolved; the latest "
        "statement of what is done and what is still missing; a conclusion of a previous task that `current_task` "
        "relies on ('já está em dev; em prod não'); a hypothesis already ruled out for an error still open; a "
        "question or proposal still waiting for the user's answer; a workaround in force. A message with an old part "
        "and a part still valid counts.",
        "Nothing would be lost: a greeting, thanks, 'ok', 'blz', 'valeu', a pause notice; an announcement or plan of "
        "an action that was then carried out ('vou rodar o lint'); a tool output already consumed — the content of a "
        "repository file (it can be re-read), a listing, a test run that passed, a search or command whose result a "
        "later message restates with the same literal values; an exploration abandoned or an attempt that failed, once "
        "the problem was solved or worked around; a previous task already finished that `current_task` does not use "
        "(its request, its steps, its results); the old version of a decision or value replaced later; an error "
        "already resolved, and its diagnosis; a restriction that applied only to a previous task; a hypothesis ruled "
        "out after the cause was found; an assistant question whose answer is complete by itself; a status that a "
        "later message updates; a fact that another message states in full with the same literals (a summary that "
        "carries the literal values makes the raw output unnecessary; a summary without them does not).",
    )


def superseded(mid: str) -> dict:
    m = _alvo(mid)
    return _noul(
        _CONTEXTO + f"Was something that {m} states or asks for — a decision, a value, a plan, a hypothesis, an "
        "error, a single-step instruction — replaced, corrected, reverted, answered or resolved by a LATER message, so "
        f"that the content of {m} no longer holds as written?",
        "A later message changes the decision ('pensando melhor…', 'então volta atrás', 'em vez disso'), corrects the "
        "value (another URL, another lot size, another name), resolves or works around the error, finds the cause that "
        "this hypothesis was about, answers this question completely, or reports that this single-step instruction "
        "('roda em dev antes', 'pode commitar') was carried out. It also counts when a later message restates in full "
        "the part that still holds, with the same literal values.",
        "Nothing later contradicts, corrects or closes it: the decision, restriction, requirement, value, error, "
        "proposal or question still stands as written; a later message only confirms, repeats partially or builds on "
        "it; the instruction was attempted and failed; a later message says 'go back to what it was' without "
        "restating the content, which makes this message current again; or the message has an old part AND a part "
        "that still holds (a restriction next to a finished task, a corrected address next to a header name still in "
        "use, the request that defines `current_task` when a later message changes only a detail of it).",
    )


def rule(mid: str) -> dict:
    m = _alvo(mid)
    return _noul(
        _CONTEXTO + f"{m} is a message from the user. Does it state a restriction, preference, requirement or decision "
        "of the user that still binds the work on `current_task`?",
        "A rule of the house or of this session that applies to the current work no matter when it was said ('nada de "
        "mexer em src/legado', 'sem dependência nova', 'commit só nesta branch', 'prod é comigo', 'sempre roda o lint "
        "antes'); the request that defines `current_task` (it counts even though `current_task` summarizes it) or a "
        "requirement of `current_task` — what it must do or look like — even if already implemented; the "
        "user's decision on a point of `current_task` that was not reverted later; a short answer that decides "
        "('a 1', 'pode', 'nessa ordem', 'o resto ok'); a value, name or address given by the user that the work still "
        "uses. A message that mixes an old part with a part still valid counts.",
        "A greeting, thanks, 'ok', 'blz', 'valeu', 'segue', a pause notice; a question or hypothesis of the user that "
        "was answered; an instruction of a single step already carried out ('roda em dev antes', 'pode commitar'); a "
        "request or restriction that applied only to a previous task already finished and that `current_task` does "
        "not depend on ('não muda a assinatura' once that function was delivered); a decision that the user later "
        "reverted or replaced (the old version); a value later corrected, when nothing else in the message is still "
        "valid; praise with no rule in it.",
    )


def status(mid: str) -> dict:
    m = _alvo(mid)
    return _noul(
        _CONTEXTO + f"{m} is a message from the assistant. Is it one of these: the LATEST statement of what has been "
        "done and what is still missing for `current_task`; a question or proposal to the user still waiting for an "
        "answer, or whose answer in a later user message only makes sense together with it ('a 1', 'pode', 'nessa "
        "ordem'); the diagnosis, location or current suspicion of an error still open, when no later message restates "
        "it with the same literals; a conclusion of a previous task that `current_task` relies on; a hypothesis ruled "
        "out for an error whose cause is still unknown; or a measured value or literal (path, name, number, ID, "
        "command) that the work still uses and that no later message repeats?",
        "The message carries the current state of the work, an open point, or a literal that is only there: the most "
        "recent 'done / still missing' list; the options the user then chose from; a proposal awaiting 'pode'; "
        "'achei: na linha 88…' for a bug not yet fixed; 'em prod ainda não foi aplicada'; 'não é o cache' while the "
        "cause is unknown; 'a imagem saiu: registro…/api-notas:8c1d2e4'.",
        "An announcement or plan of an action then carried out ('vou rodar o lint', 'seguindo com X', 'vou olhar'); a "
        "status that a later message updates; a question whose answer is complete by itself; a diagnosis of an error "
        "already resolved; a diagnosis or measurement that a later message repeats in full with the same numbers, "
        "paths or line numbers; a hypothesis ruled out after the cause was found (also when `current_task` says the "
        "cause is already known); a summary without the literal values when the raw output is what is needed; a "
        "confirmation that only repeats what the user decided ('combinado', 'fechado'); a plan or option later "
        "abandoned.",
    )


def literal(mid: str) -> dict:
    m = _alvo(mid)
    return _noul(
        _CONTEXTO + f"{m} is a tool output. Does it carry something that `current_task` still needs and that no other "
        "message states with the same literal content: the most recent and complete occurrence of an error still "
        "open; a command and its result that reproduce or measure the problem; or a value that exists only there (an "
        "ID returned by an API, a generated path, a measured number, a server-side setting, a response body that "
        "serves as the contract to code against)?",
        "The output is the only place with: the failing test or the error text that still has to be fixed; the exact "
        "command that measures or reproduces the failure and will check the fix (a later message that repeats the "
        "number but not the command does not replace it); a response body whose fields the code will use; an ID, tag, "
        "path or number that was generated or measured and that no later message repeats in full.",
        "The content of a repository file (it can be re-read); a listing or search whose finding a later message "
        "restates; a test run that passed; a build, commit or migration that succeeded and whose result a later "
        "message states; an error since fixed or worked around; an output whose necessary line a later message repeats "
        "with the same literal values; a measurement whose numbers AND command a later message repeats.",
    )


GUARDAS = {"rule": rule, "status": status, "literal": literal}


def perguntas_de(mensagens: list[dict]) -> dict:
    """As perguntas de UMA requisição: três por mensagem, ID `<noul>_<id da mensagem>`."""
    qs = {}
    for m in mensagens:
        qs[f"needed_{m['id']}"] = needed(m["id"])
        qs[f"superseded_{m['id']}"] = superseded(m["id"])
        g = GUARDA_POR_PAPEL[m["papel"]]
        qs[f"{g}_{m['id']}"] = GUARDAS[g](m["id"])
    return qs


# ---------------------------------------------------------------------------------------- política
# `needed` em três faixas: ≤ nao → não; ≥ sim → sim; meio = dúvida → MANTER (assimétrica). Partida 0,3–0,7.
FAIXA_NEEDED = (0.3, 0.7)
GUARDA_SIM = 0.7        # guarda por papel ≥ isto → manter (salvo `superseded` ≥ SUPERSEDED_SIM nos papéis com veto)
SUPERSEDED_SIM = 0.7    # substituída depois ≥ isto anula a guarda (nunca anula `needed` em sim/dúvida)
# O veto vale só para assistente e ferramenta. Medido na 2ª passada do ajuste: nas mensagens do assistente ele tirou
# 11 "manter demais" (perguntas já respondidas que `status` ainda marca); nas do usuário não tirou nenhum e descartou o
# pedido que define a tarefa (mensagem com parte velha e parte válida: `superseded` 0,94). O usuário é onde mora o erro
# caro (restrição, decisão): lá a guarda `rule` não tem veto.
VETO_PAPEIS = ("assistente", "ferramenta")
# Faixa validada: os dados têm 12–25 mensagens e até ~3.000 caracteres por sessão. Fora disso a sessão NÃO vai ao
# Jev: mantém tudo (`origem: "longo"`). Teto de caracteres ≈ 20k (~7k tokens de state + 25×3 perguntas ≈ 25k).
MAX_MENSAGENS = 25
TETO_CARACTERES = 20000

# ---------------------------------------------------------------------------------------- baselines de código
# `usuario`: papel = usuario → manter (o baseline do LEIA-ME: 79% no ajuste, 75% no teste).
# `ultimas`: as últimas N mensagens → manter. `palavras`: ≥ K palavras de conteúdo em comum com `tarefa_atual` →
# manter. N e K = os melhores da grade do ajuste (o baseline tem a mesma chance de afinação que o Jev).
ULTIMAS_N = 4     # grade do ajuste: N = 2 e 4 empatam em 0,633; 4 descarta menos necessárias (49 × 66 de 84)
PALAVRAS_K = 2    # grade do ajuste: K = 2 dá 0,677 (K = 1: 0,555; K = 3: 0,672)

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Fixado ANTES de abrir `dados/teste.json` (data/hora no manifesto). Denominadores pela tabela do LEIA-ME (teste:
# 36 sessões, 477 mensagens, 169 `manter`, 299 `descartar`, 9 discutíveis fora da métrica).
CRITERIO_CONTINUAR = {
    "onde": "no teste (36 sessões, 477 mensagens: 169 manter, 299 descartar, 9 discutíveis fora da métrica), com a política acima",
    "1_necessaria_descartada": "gabarito `manter` que saiu `descartar` ≤ 6% das necessárias (≤ 10 de 169) — limite ABSOLUTO, "
                               "não margem (no ajuste: 1 de 84)",
    "2_acerto_piso": "acerto por mensagem ≥ 0,85 (absoluto; no ajuste 0,917)",
    "3_acerto_sobre_baseline": "acerto ≥ melhor baseline de código no próprio teste + 0,08 (o LEIA-ME avisa 0,75 para `papel = usuario`)",
    "secundario_nao_decide": "manter demais ≤ 20% das descartáveis; precisão de `manter` ≥ 0,75",
    "se_falhar": "1 falhando = não serve para descartar sem revisão (só a faixa de dúvida vira `manter`, o resto vai a humano); "
                 "2 ou 3 falhando = a regra `papel = usuario` basta e o exemplo é descartado",
    # Os mesmos limites em número, para o `run.py` conferir sozinho (o veredito não é escrito à mão).
    "limites": {"necessaria_descartada_max_fracao": 0.06, "acerto_min": 0.85, "margem_sobre_baseline": 0.08,
                "manter_demais_max_fracao": 0.20, "precisao_min": 0.75},
}
