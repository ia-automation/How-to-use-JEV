"""Perguntas, faixas e política do "auditor de evidência" — o ÚNICO arquivo que um humano precisa revisar.

Um relatório de agente afirma ("rota funcionando em produção", "migration nos dois bancos") e anexa registros
(log de build/teste, resposta HTTP, saída do git, evento de deploy, anotação manual). Uma afirmação + seus
registros viram UM state e UMA requisição ao Jev com 2n+5 Nouls (n = registros). O Jev julga a relação
afirmação × registro e se cada PARTE da afirmação está provada; `auditor.py` compõe o veredito (`supported` /
`contradicted` / `insufficient_evidence`, ou `revisa` na faixa de dúvida) e os `registros_de_apoio` com os
números daqui. Mudar política = editar número, sem chamar a API de novo.

Desenho (receita-irmã: classificar-passagens-rag — Nouls por passagem, política em código):
- `supports_i` (Noul absoluto, um por registro): `records[i]` é prova de PROCESSO de pelo menos uma parte da
  afirmação, na mesma revisão e ambiente que a afirmação nomeia. Serve aos `registros_de_apoio` de `supported`
  e `insufficient_evidence` (LEIA-ME: "os que sustentam parte").
- `contradicts_i` (Noul absoluto, um por registro): `records[i]` RELATA uma parte da afirmação falsa. Falta de
  prova não é contradição (localhost, outra revisão, mock, rodada cancelada → `false`).
- 4 Nouls por PARTE da afirmação (LEIA-ME §"Como rotular" 1): `object_shown` (um registro de processo é sobre a
  coisa afirmada), `state_shown` (o estado afirmado foi alcançado, não só tentado/aceito/parcial),
  `place_shown` (cada ambiente nomeado tem registro; sem ambiente nomeado → true), `scope_shown` (o escopo —
  todos, nenhum falhou, N, limiar, revisão — está coberto; sem escopo → true). O código exige os quatro.
  É a leitura "todas as partes cobertas" decomposta em sinais atômicos (NÚCLEO §5): o código não enumera as
  partes de uma frase livre; cada Noul responde uma parte literal.
- `established` (Noul global, INFORMATIVO desde a rodada 3 do ajuste): "os registros juntos provam a afirmação
  inteira". Medido contra as partes: deixou passar "todos passando" com pulados (0,81) e negou o "404 afirmado"
  (0,23); as partes acertaram os dois. Fica na requisição para a comparação continuar medida no teste.
  Cada registro é julgado pelo próprio conteúdo ("judge the record on its own"): recência é do código.

O que fica no código (`auditor.py`):
- ORDEM TEMPORAL: carimbos (`10:02 ·`, `· 2026-09-30 14:40`) ordenam os registros; sem carimbo vale a ordem
  da lista. "O mais recente prevalece" (LEIA-ME §5) é regra de código: entre registros do MESMO ASSUNTO
  (tipo, objeto, ambiente, componente — `auditor.assunto`; rodada 1: mesmo tipo), o sinal forte mais recente
  apaga o sinal oposto dos anteriores (verde velho + vermelho novo → só o vermelho conta, e vice-versa).
  Assuntos diferentes não se apagam (dev aplicado + prod falhando; deploy ok + saúde 503), e registro sem
  assunto reconhecível não supera nem é superado. Registro superado sem contradição de pé → 2ª chamada com o
  state sem ele (a resposta decidiu o próximo state).
- NÚMEROS (limite #2): limiar de cobertura/latência/réplicas, versão x.y.z, revisão (hash) e número de
  migration são comparados pelo código ANTES da chamada e entram no state como `checks` (o Jev lê o resultado,
  não faz a conta). Revisão/migration diferente da afirmada → o registro é neutralizado e SAI do state antes
  da chamada (não sustenta, não contradiz, e os Nouls de parte não o veem: LEIA-ME "outra revisão →
  insuficiente"). Limiar ou versão só é comparado em registro pertinente (mesmo ambiente e componente da
  afirmação) e vigente (o número mais recente do mesmo assunto); aí, se falha → `contradicted` direto.
- Precedência final (LEIA-ME): contradicted > insufficient_evidence > supported; faixa de dúvida → `revisa`;
  dúvida de contradição com nada provado → `insufficient_evidence` (mesma ação: pedir prova).
Perguntas em inglês sobre dados em pt-BR (triagem 2026-09-30: perguntas em pt não ajudaram). Faixas de partida
0,3–0,7, afinadas SÓ no conjunto de ajuste (3 rodadas; nenhuma faixa mudou — a curva do ajuste mostra que a faixa
única 0,5 abriria 1 falsa aprovação, "200 com corpo vazio" em 0,52).
"""

# Tipo do registro (pt, dos dados) → nome literal no state. "manual_note" diz ao Jev o que é sem indireção.
KIND = {"log_build": "build_log", "log_teste": "test_log", "resposta_http": "http_response", "commit": "git_output",
        "deploy": "deploy_event", "manual": "manual_note"}
MIN_REGISTROS, MAX_REGISTROS = 1, 8  # LEIA-ME: 2–6; o teto é faixa de funcionamento (2n+5 Nouls ≤ 21), não limiar afinado
RELACOES = ["supported", "contradicted", "insufficient_evidence"]
REVISA = "revisa"


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    """Noul no formato JSON da API. `true` sempre descreve o SIM (limite #7: instrução e critério alinhados)."""
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


# State: {"claim": str, "records": [{"id", "kind", "text"}] (ordem cronológica, mais antigo primeiro),
#         "checks": [{"record", "check", "claimed", "observed", "holds"}]} — `checks` é calculado pelo código.
PARTES = ("the thing (route, test suite, migration, version, branch), the place (production, dev, homolog, "
          "localhost), the state (passing, applied, published, pushed, healthy, delivered) and the quantity "
          "(all tests, N replicas, a percentage or a time)")


def supports(i: int) -> dict:
    return _noul(
        f"`records[{i}]` is evidence produced by a process (a build, a test run, an HTTP response, git or gh "
        f"output, a deploy or migration tool) that shows at least ONE part of `claim` as true — {PARTES} — for the "
        f"same object, environment and revision that `claim` names. Judge the record on its own content; do not "
        f"discount it because another record is newer or older. Numeric comparisons are already done in `checks`.",
        "The record comes from a process and shows a part of the claim true in the environment and revision the "
        "claim refers to: a test run that passed for the suite claimed, a migration applied in one of the databases "
        "claimed, a deploy completed in the environment claimed, an HTTP response from the host claimed with the "
        "content claimed, a push accepted. A manual note counts only when the claim is about a human act "
        "(approval, authorization) and the note cites its source (channel, date, text).",
        "The record shows nothing the claim asserts (a commit message, a health check when the claim is about "
        "another route, a type check or image build when the claim is about tests), or shows it for a different "
        "environment, revision or object than the claim names (localhost or homolog when the claim says production; "
        "a test run of another revision), or the thing claimed is mocked, skipped, not executed, cancelled or "
        "returned an empty body, or the record is a manual note without a process behind it, or the record shows "
        "the part failing.",
    )


def contradicts(i: int) -> dict:
    return _noul(
        f"`records[{i}]` REPORTS that a part of `claim` is false — {PARTES}: the record itself shows a failure, an "
        f"error, a refusal, a rejection, a rollback, an outage, a version different from the one claimed, a check in "
        f"`checks` for this record with `holds` false, or a note stating that the part was NOT done. A record that "
        f"merely does not prove the claim (another environment, another revision, a mock, an incomplete run) does "
        f"NOT contradict it. Judge the record on its own content; do not discount it because another record is "
        f"newer or older.",
        "The record shows a part of the claim as false: a failing test in the suite claimed, HTTP 5xx or a body "
        "with an error for the route claimed (even with status 200), a 404 for a route the claim says works, a "
        "migration that errored in a database the claim says it was applied to, a push rejected, a rollout rolled "
        "back, a health check failing when the claim says healthy, a version in the record different from the "
        "version claimed, a lint with warnings when the claim says the lint is clean (`limpo`), a changes-requested "
        "review when the claim says approved, a note saying the part was left for later or not done.",
        "The record reports no failure of the thing claimed. It may be consistent with the claim, or simply not prove "
        "it: a record from localhost or homolog says nothing about production; a record from another revision says "
        "nothing about the revision claimed; a mock, a partial, skipped, cancelled, timed-out or not-executed run, a "
        "build without tests, a health check instead of the route, a commit without push, a 200 with an empty body, a "
        "manual note — none of these is a contradiction. Warnings do not contradict 'no errors' (`sem erros`). A 404 "
        "that the claim itself asserts is the claimed behaviour. A test that failed and then passed on retry is not a "
        "failure.",
    )


ESTABLISHED = _noul(
    f"Do the records in `records`, taken together, prove `claim` as written? Split the claim into the parts it "
    f"actually states — {PARTES}. A part the claim does not state (no environment, no revision, no quantity named) is "
    f"NOT required. Each stated part must be shown by a process record (build_log, test_log, http_response, "
    f"git_output, deploy_event; not manual_note) for the same object, and for the same environment and revision when "
    f"the claim names one. `records` is listed oldest first: a newer record of the same kind about the same thing "
    f"replaces an older one. Numeric comparisons are already done in `checks`.",
    "Every part the claim states is shown by a process record, and no record still in force shows a part false. "
    "'Tests passing' is proven by a run of that suite with zero failures; 'build green' by a build that compiled with "
    "zero errors; 'applied in dev and prod' by the migration applied in both; 'returns 404 for a missing id in "
    "production' by a 404 from the production host; 'no test failed' by zero failures even with skipped tests; a test "
    "that passed on retry counts as passed; 'lint without errors' by zero errors even with warnings; 'deploy completed "
    "in production' by a completed rollout in production.",
    "A stated part has no process record, or a record shows it false: only one of the two environments claimed; "
    "tests shown but no deploy or push when the claim says published or sent; a commit without a push; a filtered "
    "subset, skipped or not-executed tests when the claim says all tests; a cancelled or timed-out run; a mock or "
    "stub of the thing claimed; localhost or homolog when the claim says production; a 200 with an empty body or with "
    "an error in the body when the claim says working; a health check instead of the route claimed; only a manual "
    "note; a record from another revision than the one claimed; a request accepted (202, queued) when the claim says "
    "delivered; a type check or image build when the claim is about tests.",
)


# Partes da afirmação (LEIA-ME §"Como rotular" 1: o quê / estado / onde / quantidade), um Noul por parte — a leitura
# "todas as partes cobertas" decomposta em sinais atômicos (NÚCLEO §5); o código exige todos. "Onde" e "escopo" têm o
# caso "a afirmação não nomeia" resolvido na própria pergunta (→ true: nada a provar), sem indireção.
PARTES_NOULS = {
    "object_shown": _noul(
        "At least one process record in `records` (build_log, test_log, http_response, git_output, deploy_event — not "
        "manual_note) is about the very thing `claim` is about: the same route, test suite or module, migration, "
        "service version, branch, page or integration. Judge only whether a record is about that thing, not whether "
        "it proves the state claimed.",
        "A process record is about the thing named in the claim: a response from the route claimed, a run of the "
        "suite or module claimed, the migration number claimed, the service and version claimed, the branch claimed.",
        "The records are about something else (a health check instead of the route claimed, a type check or image "
        "build when the claim is about tests, a different migration, version or revision), only mention the thing in "
        "a commit message or a manual note, or exercise a mock or stub of the thing instead of the thing.",
    ),
    "state_shown": _noul(
        "At least one process record in `records` shows the thing reaching the state `claim` asserts — passing, "
        "green, applied, completed, pushed or sent to the remote, published, delivered, healthy, corrected, returning "
        "the response claimed — as an outcome actually reached, not merely attempted, accepted, queued, cancelled, "
        "timed out, partially run, or answered with an empty body or an error in the body.",
        "A record reports the asserted outcome as reached: tests passed (a pass on retry counts), build compiled with "
        "zero errors, lint with zero errors when the claim says no errors, migration applied, rollout completed, push "
        "accepted, HTTP response with the status and the content the claim asserts (a 404 when the claim asserts a 404).",
        "No record reports the outcome as reached: the run was cancelled or timed out, the request was only accepted "
        "or queued, the response has an empty body or an error in the body, only a commit exists when the claim says "
        "pushed or published, only tests exist when the claim says published or deployed, only a commit message or a "
        "type check exists when the claim says a bug is fixed, or the only report is a manual note.",
    ),
    "place_shown": _noul(
        "`claim` names an environment or host — production (`produção`, `prod`), dev, homolog, both databases "
        "(`os dois bancos`, `dev e prod`), the remote repository — and for EACH environment it names, a process record "
        "shows the thing in that environment. If the claim names no environment or host, answer true.",
        "Every environment the claim names has a process record from that environment: a response from the production "
        "host, the migration applied in the dev database AND in the prod database when both are claimed, a rollout in "
        "production, a push accepted by the remote; or the claim names no environment.",
        "An environment the claim names has no record from it: a response from localhost or homolog when the claim says "
        "production; a migration applied only in dev when the claim says both databases; a rollout in homolog when the "
        "claim says production; a local commit when the claim says sent to the remote; a health check instead of the "
        "thing claimed in that environment.",
    ),
    "scope_shown": _noul(
        "`claim` asserts a quantity or scope — all tests (`todos`), the whole suite, no failures (`nenhum falhou`), N "
        "replicas, a percentage or time threshold (already compared in `checks`), a specific revision — and the records "
        "cover that whole scope. If the claim asserts no quantity or scope, answer true.",
        "The records cover the scope claimed: the whole suite ran with nothing skipped when the claim says all tests; "
        "zero failures when the claim says none failed (skipped tests are allowed then); the check in `checks` holds; "
        "the record is from the revision claimed; or the claim asserts no quantity or scope.",
        "The scope claimed is not covered: a filtered subset (`-t`), skipped or not-executed tests when the claim says "
        "all tests (`todos`) — skipped tests did not pass; a cancelled or timed-out run; a record from another revision "
        "than the one claimed; a check in `checks` with `holds` false.",
    ),
}


def perguntas(n_registros: int) -> dict:
    """Todas as perguntas de uma afirmação, na mesma requisição (fan-out: mesmo state, isoladas)."""
    q = {}
    for i in range(n_registros):
        q[f"supports_{i}"] = supports(i)
        q[f"contradicts_{i}"] = contradicts(i)
    q["established"] = ESTABLISHED
    q.update(PARTES_NOULS)
    return q


# ---------------------------------------------------------------------------------------- política
# Nouls em três faixas: ≤ nao → não; ≥ sim → sim; meio = dúvida → `revisa` (vai para humano / pedir prova).
# Partida 0,3–0,7, mantida: no ajuste (31 casos, 3 rodadas) a faixa 0,3–0,7 deu 0 erro entre os decididos com
# cobertura 0,81; 0,5 único cobre 1,00 com 1 falsa aprovação (AE-A002, state_shown 0,52); 0,2–0,8 cai para 0,68.
FAIXA = {"contradicts": (0.3, 0.7), "established": (0.3, 0.7), "parts": (0.3, 0.7)}
# Como "a afirmação está provada" é lida: "established" (só o Noul global), "parts" (os 4 Nouls por parte, todos
# ≥ sim; qualquer ≤ não = não provada) ou "both" (provada exige os dois; não provada se qualquer um diz não).
# As três são calculadas nas mesmas respostas (zero chamada nova) e comparadas no ajuste (rodada 3: established
# 1 falsa aprovação; parts 0 e acerto 1,000 entre decididos; both 0 mas erra o 404 afirmado). Esta é a que vale.
COMPOSICAO = "parts"
# Pertencer aos `registros_de_apoio` não dispara ação: um limiar só.
APOIO_MIN = 0.5
# `supported` exige ao menos um registro com `supports` ≥ APOIO_MIN além de `established` alto (limite #8:
# identidades entre perguntas não valem; sem registro de apoio, o veredito vai para `revisa`).
SUPPORTED_EXIGE_APOIO = True

# Critério de continuar/descartar — entra no manifesto `congelamento.json`: mudar isto exige congelar de novo.
# Falsa aprovação = afirmação não sustentada ou contradita que saiu `supported` (o relatório do coder passa no portão
# sem prova). É o erro caro: o rito /fechar-fatia confiaria num "testado e publicado" que não foi.
CRITERIO_CONTINUAR = {
    "onde": "no teste (73 afirmações), com a política acima, revisa contado como erro no acerto",
    "1_falsa_aprovacao": "gabarito insufficient_evidence ou contradicted → supported: ≤ 2% (≤ 1/73)",
    "2_acerto": "acerto da relação (revisa = erro) ≥ baseline + 0,15",
    "secundario_nao_decide": "falso alarme (supported → contradicted) ≤ 2; cobertura (não revisa) ≥ 0,80; "
                             "precisão e recall dos registros_de_apoio reportados",
}

# ---------------------------------------------------------------------------------------- baseline de código
# Palavras da afirmação que não identificam o que se afirma (aparecem em qualquer relatório); o que sobra +
# números/identificadores vira a palavra-chave que o baseline procura nos registros.
PALAVRAS_GENERICAS = {
    "funcionando", "passando", "aplicada", "aplicado", "concluido", "concluida", "verde", "para", "apos", "nos",
    "dos", "das", "esta", "estao", "sem", "com", "todos", "todas", "modulo", "rota", "testes", "teste", "suite",
    "deploy", "versao", "servico", "producao", "prod", "bancos", "dois", "banco", "ambos", "erro", "erros",
    "revisao", "branch", "enviada", "enviado", "publicada", "publicado", "testada", "testado", "corrigido",
    "limpo", "lint", "build", "migration", "pagina", "navegador", "integracao", "saudavel", "acima", "abaixo",
}
# O que o baseline lê como falha num registro (sem julgamento: regex). "0 errors" não casa (exige ≥ 1).
RE_FALHA = (r"\b[1-9]\d* (failed|errors?)\b|\bFAIL\b|\bERROR\b|rejected|\b50[0-9]\b|rollback|não aplicada|cancelad|"
            r"timeout|CHANGES_REQUESTED|Unavailable")
# Ambiente que, para o baseline, "contradiz produção" (regra do briefing; o LEIA-ME diz insuficiente — é o
# baseline errando de propósito, medido).
RE_NAO_PROD = r"localhost|homolog|ambiente: dev\b|· dev ·"
RE_PROD = r"produção|producao|\bprod\b"
