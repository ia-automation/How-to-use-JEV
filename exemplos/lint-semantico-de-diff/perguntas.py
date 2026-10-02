"""Perguntas, regex mecânicas, faixas, baseline e critério de aceite do lint semântico — o ÚNICO arquivo que um
humano precisa revisar.

Divisão de trabalho (a mesma do dados/LEIA-ME.md, escrita antes dos casos):
  regras MECÂNICAS  (segredo literal, `console.log(`, `DROP` sem confirmação, `TODO` sem ticket) → regex em código.
                    O gabarito É a regex; o Jev nunca vê essas regras. Literal demais? É o ponto: o custo fica visível.
  regras SEMÂNTICAS (JSDoc com `@description`, desvio com porquê, validação com express-validator, SQL cru
                    justificado) → um Noul por regra sobre o diff, todas as regras do mesmo diff numa requisição,
                    cada Noul apontando `rules[i]` entre crases (state compartilhado: 1 requisição por diff).
O código decide `viola` / `revisa` / `ok` pela FAIXA e monta o comentário de CI só com IDs e trechos: o Jev julga,
não gera texto.

Três desenhos para o `null` (regra que não toca o assunto do diff), medidos no ajuste com a MESMA requisição:
  "valvula"        — só o Noul de violação; a instrução diz que "não toca o assunto" é `false`. O lint não sabe
                     dizer "não se aplica": o nulo vira `ok` (mede-se só se ele NÃO virou alarme).
  "aplicabilidade" — Noul auxiliar "o diff adiciona algo que a regra governa?" na mesma requisição; abaixo de
                     LIMIAR_APLICA o código responde `nao_se_aplica` sem consumir o Noul de violação.
  "gatilho"        — o CÓDIGO decide a aplicabilidade pela regex de gatilho do BASELINE (há `+export function`?
                     `+router.post(` lendo `req.*`? supressão em `+`? SQL cru em `+` fora de migration?); só regra
                     disparada consome o Noul de violação. Zero chamada extra (num job de CI, regra sem gatilho
                     nem iria à requisição). Acrescentado no ajuste v1: os 2 nulos que viraram `viola` eram função
                     MODIFICADA lida como nova — o Noul auxiliar errou junto (0,71 / 0,58), a regex não.
Perguntas em inglês sobre diff e regras em pt-BR (medido em 2026-09-30: a língua não muda o acerto).
Afinação medida (overfit): v1 → v2 da instrução acrescentou só a NOTAÇÃO ("nova" = linha de declaração com `+`;
"E" exige os dois; elemento em outra função não conta) — a metade literal que faltava (limite #1), não um caso.
"""
import re

# ---------------------------------------------------------------- identificação das regras pelo texto
# A numeração `r1…rn` muda de caso para caso; o TEXTO identifica a regra. Prefixo literal do LEIA-ME.
# Regra mecânica com texto fora desta tabela é ERRO (não há regex para ela); semântica desconhecida vai ao Jev
# normalmente (o Noul é genérico) e só fica sem baseline.
CHAVES = {
    "SEG": "Nenhuma linha adicionada contém valor de segredo",
    "LOG": "Nenhum `console.log(`",
    "DROP": "Nenhuma linha adicionada contém `DROP TABLE`",
    "TODO": "Todo `TODO` ou `FIXME`",
    "JSDOC": "Toda função nova exportada em TypeScript",
    "DESVIO": "Supressão de lint ou de tipo",
    "VALID": "Rota nova de Express",
    "SQL": "Query SQL crua em código adicionado",
}


def chave_da_regra(texto: str) -> str | None:
    return next((k for k, prefixo in CHAVES.items() if texto.startswith(prefixo)), None)


# ---------------------------------------------------------------- regras mecânicas (regex literais do LEIA-ME)
# Todas sobre LINHAS ADICIONADAS (`+`, sem `+++`); o caminho vem de `+++ b/<caminho>`.
SEG_RE = re.compile(
    r"sk_(?:live|test)_[A-Za-z0-9]{8,}"
    r"|ghp_[A-Za-z0-9]{10,}"
    r"|AKIA[A-Z0-9]{12,}"
    r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
    r"|(?:password|senha|secret|api_key|apikey|token)\b\s*[:=]+\s*[\"'`][^\"'`]{6,}[\"'`]",
    re.I,
)
LOG_RE = re.compile(r"console\.log\s*\(")
LOG_ARQUIVO_DE_TESTE_RE = re.compile(r"(\.test\.|\.spec\.|(^|/)tests?/|(^|/)__tests__/)")
DROP_RE = re.compile(r"\bDROP\s+(?:TABLE|COLUMN)\b", re.I)
DROP_MARCADOR_RE = re.compile(r"confirmado por", re.I)
TODO_RE = re.compile(r"\b(TODO|FIXME)\b")  # sensível a maiúsculas: `todo:` não entra
TODO_OK_RE = re.compile(r"\b(TODO|FIXME)\(([A-Z]{2,}-\d+)\)")

# ---------------------------------------------------------------- teto do diff (revisão do Codex, 2026-10-01)
# O desenho foi medido em diffs de 10–24 linhas e 241–847 caracteres (ajuste + teste; a especificação dos dados
# admite até 60 linhas). Acima do teto o diff NÃO vai ao Jev e NÃO é truncado em silêncio: as regras semânticas
# saem `revisa` com MOTIVO_DIFF_GRANDE e o relatório conta esses diffs à parte (as mecânicas rodam igual, são
# código). O teto é 2× a faixa especificada, não um limite medido: dentro dele e acima de 24 linhas o lint
# ainda roda FORA da faixa medida. Num job de CI: um state por arquivo; arquivo acima do teto pede olhar humano.
TETO_LINHAS = 120
TETO_CARACTERES = 8000
MOTIVO_DIFF_GRANDE = "diff grande"

# ---------------------------------------------------------------- perguntas (um Noul por regra semântica)
# `{ref}` = `rules[i]` entre crases. Alto = sim. O diff vai inteiro (10–60 linhas): o Jev precisa ver `+`/`-`/
# contexto para ler "nova" × "modificada" — a instrução explica a notação porque o modelo é literal (limite #1).
_NOTACAO = (
    "`diff` is a unified diff of a pull request: file paths follow '+++ b/'; a line starting with '+' was ADDED, "
    "a line starting with '-' was REMOVED, any other line is unchanged context. Only ADDED lines are under review. "
    "Something is NEW only if its declaring line (the `export function`, `router.post(`, etc.) itself starts with "
    "'+'; a declaration in a context line already existed and was merely modified, even when lines were added "
    "inside it. "
)
_INSTRUCAO_VIOLA = (
    _NOTACAO + "{ref} is one of the team's code conventions, written in Portuguese. "
    "Does the code ADDED in `diff` violate the rule in {ref}, read exactly as written?"
)
_VIOLA_TRUE = (
    "An added line contains the kind of thing the rule governs, and that addition fails what the rule demands or "
    "does what it forbids: the required comment, tag, marker, justification or validation is missing, is not in "
    "the exact place the rule names (same line, line immediately above), does not say what the rule asks it to say "
    "(a comment that only describes or says 'ok' is not a reason), or uses something the rule says does not count. "
    "When the rule requires two things joined by 'E' (and), one without the other violates; a required element "
    "attached to a different function, route or line than the one the rule covers does not count."
)
_VIOLA_FALSE = (
    "The rule is satisfied for every added line it covers (the required element is present where the rule says, "
    "or the case falls under an exception the rule itself states); OR the rule does not apply to this diff at all: "
    "nothing added is the kind of thing it governs, the thing it mentions appears only in removed ('-') or context "
    "lines, it is a modified function/route rather than a new one, or it is another language or framework than "
    "the rule names."
)
_INSTRUCAO_APLICA = (
    _NOTACAO + "{ref} is one of the team's code conventions, written in Portuguese. "
    "Does `diff` ADD (in '+' lines) something of the kind that the rule in {ref} governs, within the scope the rule "
    "states, so that this diff could satisfy or violate the rule?"
)
_APLICA_TRUE = (
    "At least one '+' line contains the kind of element the rule is about (the new exported function, the "
    "suppression comment, the new route reading request input, the raw SQL call, etc.), in the language, framework "
    "and file kind the rule names."
)
_APLICA_FALSE = (
    "No '+' line contains that kind of element; it appears only in '-' or context lines (the thing already existed "
    "and was only modified); the rule's own text excludes it (another language or framework, migration file, "
    "fragment inside a builder call, route that reads no request input); or the diff is unrelated to the rule."
)


def noul_viola(i: int) -> dict:
    ref = f"`rules[{i}]`"
    return {"type": "noul", "instructions": _INSTRUCAO_VIOLA.format(ref=ref),
            "criteria": {"true": _VIOLA_TRUE, "false": _VIOLA_FALSE}}


def noul_aplica(i: int) -> dict:
    ref = f"`rules[{i}]`"
    return {"type": "noul", "instructions": _INSTRUCAO_APLICA.format(ref=ref),
            "criteria": {"true": _APLICA_TRUE, "false": _APLICA_FALSE}}


# ---------------------------------------------------------------- faixas (três faixas por regra)
# viola ≥ SIM · ok ≤ NAO · meio → revisa (humano). Erro caro = violação real que passou como `ok`; falso alarme
# (false → viola) custa a confiança do dev no bot. Ajuste v2 2026-10-01 (19 regras semânticas rotuladas, 22 nulas):
# os `false` ficaram em 0,06–0,28 (os quatro mais altos são os "justificados": desvio com porquê, SQL com razão) e
# os `true` em 0,60–0,97; a faixa fica DENTRO dessa lacuna com margem para a variação entre chamadas (máx. 0,15
# medido): 0,3/0,7 dá 1 revisão e 0 erro no ajuste; 0,2/0,8 daria 5 revisões pelo mesmo 0 erro. Só o teste calibra.
FAIXA = (0.3, 0.7)
DESENHOS = ("valvula", "aplicabilidade", "gatilho")
# Noul de aplicabilidade abaixo disto → `nao_se_aplica` (o Noul de violação não é consumido). No ajuste v2, 0,3
# sinaliza 12/22 nulos (0,5: 15/22) e 1/9 `false` (inofensivo), 0/10 `true`; a regex sinaliza 22/22 nulos e 0 `true`.
LIMIAR_APLICA = 0.3
# `gatilho`: a aplicabilidade é a metade MECÂNICA de cada regra semântica (há função nova exportada? supressão em
# `+`? rota nova lendo `req.*`? SQL cru fora de migration?) e o código a resolve exato; o Jev julga só o resto
# (o comentário justifica? a tag está na função certa? a cadeia vem com `validationResult`?). Risco assumido: forma
# de "função nova" que a regex não conheça esconde a violação do Jev — medido como `sem_gatilho_regex` nos `true`.
DESENHO_PADRAO = "gatilho"

# ---------------------------------------------------------------- baseline de código (só semânticas)
# O que um dev faria em 20 minutos com regex: gatilho (a regra se aplica?) + palavra-chave (está satisfeita?).
# Sem gatilho → `null` (não se aplica). É o piso que o Jev precisa superar — e também o "aplicabilidade por regex".
BASELINE = {
    # função nova exportada em linha `+` → precisa de `@description` em alguma linha `+`
    "JSDOC": {"gatilho": re.compile(r"^\s*export\s+(?:async\s+)?(?:function\b|const\s+\w+\s*=.*=>)"),
              "satisfaz": re.compile(r"@description\b")},
    # supressão em linha `+` → precisa de comentário na mesma linha (após `--` ou ` # `) ou na anterior
    "DESVIO": {"gatilho": re.compile(r"eslint-disable|@ts-ignore|@ts-expect-error|#\s*noqa|#\s*type:\s*ignore"),
               "satisfaz": None},  # tratado em lint.baseline: olha a própria linha e a anterior
    # rota nova em linha `+` que lê req.* → precisa de `express-validator` no import adicionado e `validationResult`
    "VALID": {"gatilho": re.compile(r"\b(?:router|app)\.(?:get|post|put|patch|delete|all)\s*\("),
              "satisfaz": re.compile(r"from 'express-validator'|from \"express-validator\"")},
    # SQL cru em linha `+` (fora de migration) → precisa de linha de comentário imediatamente acima.
    # Rodada 1 do teste (cega): o gatilho era `db\.execute\(\s*sql`` e NÃO disparou em `db.execute(sql.raw(...))`
    # (LS-T066) — a violação ficou escondida do Jev. Rodada 2 (não cega): qualquer `db.execute(` é SQL cru.
    "SQL": {"gatilho": re.compile(r"\bdb\.execute\(|\b(?:pool|client)\.query\(|\b(?:cursor|cur)\.execute\("),
            "satisfaz": None},  # tratado em lint.baseline: comentário na linha `+` anterior
}
JSDOC_DEFAULT_RE = re.compile(r"^\s*export\s+default\s+(\w+)\s*;?\s*$")


def JSDOC_ARROW_RE(nome: str) -> re.Pattern:
    """`const <nome> = (...) =>` (com ou sem tipo) em linha adicionada: a arrow que o `export default` exporta."""
    return re.compile(rf"^\s*(?:export\s+)?const\s+{re.escape(nome)}\s*(?::[^=]+)?=.*=>")



VALID_LE_ENTRADA_RE = re.compile(r"req\.(?:body|params|query)\b")
VALID_RESULT_RE = re.compile(r"\bvalidationResult\b")
COMENTARIO_RE = re.compile(r"^\s*(?://|#|/\*|\*|--)")
MIGRATION_RE = re.compile(r"(^|/)(drizzle|migrations?)/|\.sql$")

# ---------------------------------------------------------------- critério de continuar / descartar
# Fixado ANTES de abrir o teste (2026-10-01), a partir do ajuste. Falhar um item = o desenho não serve como está;
# o teste não se repete para consertar. Dicionário porque entra no manifesto `congelamento.json`.
CRITERIO_CONTINUAR = {
    "onde": "no teste, com o desenho padrão, a FAIXA e o LIMIAR_APLICA acima",
    "1_mecanicas": "100% (menos é bug de código)",
    # +10 p.p. e não +15: o baseline já embute a metade mecânica de cada regra (gatilho) e deu 0,789 no ajuste;
    # +15 exigiria ~0,94 e, com baseline ≥ 0,85 no teste, seria impossível por construção. Fixado antes do teste.
    "2_semantico_duro": "acerto duro (noul ≥ 0,5, gabarito true/false) ≥ 0,90 E ≥ baseline + 10 p.p.",
    "3_erro_caro": "≤ 5% das violações reais (gabarito true) passam como `ok` ou `nao_se_aplica`",
    "4_falso_alarme": "≤ 10% dos gabaritos false viram `viola`",
    "5_nulo": "≥ 80% dos gabaritos null NÃO viram `viola`",
}
