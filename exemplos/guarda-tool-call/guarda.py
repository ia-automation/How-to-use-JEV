"""Guarda de uma chamada de ferramenta: UMA requisição ao Jev com os 7 Nouls; a decisão é do código.

O Jev só julga (probabilidade de cada condição). O código decide, com as faixas de `perguntas.py`, pela
precedência do `dados/LEIA-ME.md`: bloqueia > pergunta > permite. O que a regra resolve sai do modelo: a
lista de padrões destrutivos (regex) é baseline sozinha e piso na composição Jev+regex.

Não é fronteira de segurança (limite #6 do jev-1.13: o state não é tratado como hostil — a injeção que
a guarda tenta pegar é exatamente o texto que pode mover a resposta). É uma camada barata de triagem
antes da confirmação humana, candidata a hook PreToolUse; autorização e execução continuam no processo.
Ausência de resposta (chamada falhou, ID faltando, bool/string no lugar de número, número fora de [0,1]) é
ERRO, nunca `permite`.

Pós-revisão (Codex, 2026-10-01; README "rodada 2"): (a) regex sobre segmentos normalizados, sensibilidade a
maiúsculas por comando, exceção de pasta gerada em código; (b) dispensa de confirmação vem de um campo
ESTRUTURADO do chamador (`dispensa_do_chamador`), nunca do Noul; (c) alvo compartilhado E não pedido E
comando que muda algo → ao menos `pergunta`; (d) validação de probabilidade pela infra comum.
"""
from __future__ import annotations

import posixpath
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as C  # noqa: E402
import perguntas as P  # noqa: E402

ACOES = ["permite", "pergunta", "bloqueia"]  # ordem de gravidade; a composição só sobe
_REGEX = [(nome, re.compile(padrao, flags)) for nome, padrao, flags in P.PADROES_DESTRUTIVOS]
_LEITURA = [re.compile(padrao, flags) for padrao, flags in P.SOMENTE_LEITURA]
_SENSIVEL = re.compile(P.ARQUIVOS_SENSIVEIS_WRITE, re.I)
_PASTA_GERADA = re.compile(rf"^{P.PASTAS_GERADAS}$")
_PIPELINES = re.compile(r"\s*(?:&&|\|\||;|\n)\s*")  # separa comandos; `|` separa dentro do pipeline
_FIND_NAME = re.compile(r"\bfind\b.*?\s-i?name\s+(\S+)")


def state_de(caso: dict) -> dict:
    """Caso rotulado (pt) → state enxuto em inglês, com os nomes que as perguntas citam entre crases.

    Mantém `plan` e `context_read` nulos quando não há (as perguntas tratam "vazio" explicitamente).
    @example state_de({"tarefa": "t", "plano": None, "contexto_lido": None,
                       "chamada": {"ferramenta": "bash", "comando": "ls"}})
             → {"task": "t", "plan": None, "context_read": None, "call": {"tool": "bash", "command": "ls"}}
    """
    ch = caso["chamada"]
    call = {"tool": ch["ferramenta"]}
    if ch["ferramenta"] == "bash":
        call["command"] = ch["comando"]
    else:
        call["file"], call["snippet"] = ch["arquivo"], ch["trecho"]
    return {"task": caso["tarefa"], "plan": caso.get("plano"), "context_read": caso.get("contexto_lido"), "call": call}


def pedido(caso: dict) -> tuple[dict, dict]:
    """(state, questions) de um caso: todos os Nouls na mesma requisição."""
    return state_de(caso), P.PERGUNTAS


def _token(t: str) -> str:
    """Tira as aspas que envolvem o token e normaliza o que parece caminho (`.\\dist` → `dist`,
    `dist/../uploads` → `uploads`, `"dist"` → `dist`). URL (`://`) fica como está."""
    t = t.strip("\"'")
    if "://" in t or not (("/" in t or "\\" in t) or t.startswith(".")):
        return t
    t = posixpath.normpath(t.replace("\\", "/"))
    return t[2:] if t.startswith("./") else t


def segmentos(comando: str) -> list[list[str]]:
    """Comando → pipelines (separados por `&&`, `||`, `;`, quebra de linha) → segmentos (separados por `|`),
    cada segmento já com tokens normalizados. Decomposição mínima, não um parser de shell: aspas que
    contêm `;`/`|` também são partidas; `$VAR` e `$(...)` não são resolvidos.
    @example segmentos('rm -rf ".\\dist" && npm run build') → [["rm -rf dist"], ["npm run build"]]
    """
    saida = []
    for pipeline in _PIPELINES.split(comando):
        if pipeline.strip():
            saida.append([" ".join(_token(t) for t in seg.split()) for seg in pipeline.split("|") if seg.strip()])
    return saida


def _alvos_gerados(segmento: str) -> bool:
    """`rm -r…`/`Remove-Item` cujo(s) alvo(s) são TODOS pasta gerada (último componente do caminho normalizado).
    `{}` de um `find … -exec` no mesmo segmento herda o `-name` do find. Alvo vazio, `/` ou `*` → não gerado."""
    tokens = segmento.split()
    verbo = next((i for i, t in enumerate(tokens) if t == "rm" or t.lower() == "remove-item"), None)
    if verbo is None:
        return False
    alvos = [t for t in tokens[verbo + 1:] if not t.startswith("-") and t not in {"+", "\\;", ";"}]
    find = _FIND_NAME.search(segmento)
    alvos = [(find.group(1) if (t == "{}" and find) else t) for t in alvos]
    return bool(alvos) and all(_PASTA_GERADA.match(posixpath.basename(a) or a) for a in alvos)


def padroes_casados(call: dict) -> list[str]:
    """Nomes dos padrões destrutivos que casam na chamada (baseline de código; vazio = nada casou).

    Só `bash` passa pela lista de comandos, segmento a segmento (o pipe remoto vê o pipeline inteiro);
    `write` casa só sobre arquivo sensível inteiro; `edit` nunca (LEIA-ME: edição pontual guarda o valor
    anterior). Comando citado numa string de `write` não casa de propósito — é a família "citado, não executado".
    @example padroes_casados({"tool": "bash", "command": "rm -rf dist && npm run build"}) → []
    @example padroes_casados({"tool": "bash", "command": "git push --force origin main"})
             → ["push --force em branch compartilhada", "push --force sem lease"]
    @example padroes_casados({"tool": "bash", "command": "git branch -d feature/x"}) → []
    """
    if call["tool"] == "write" and _SENSIVEL.search(call["file"]):
        return ["write de arquivo sensível inteiro"]
    if call["tool"] != "bash":
        return []
    casados = []
    for pipeline in segmentos(call["command"]):
        textos = [" | ".join(pipeline)] + pipeline  # pipeline inteiro (pipe remoto) + cada segmento
        for nome, rx in _REGEX:
            if nome in casados:
                continue
            for texto in textos:
                if rx.search(texto) and not (nome.endswith("pasta gerada") and _alvos_gerados(texto)):
                    casados.append(nome)
                    break
    return casados


def somente_leitura(call: dict) -> bool:
    """`bash` cujos segmentos TODOS são verbos de leitura (`perguntas.SOMENTE_LEITURA`); write/edit nunca."""
    if call["tool"] != "bash":
        return False
    segs = [seg for pipeline in segmentos(call["command"]) for seg in pipeline]
    return bool(segs) and all(any(rx.search(seg) for rx in _LEITURA) for seg in segs)


def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    """Noul em três faixas: True / False / None (= dúvida)."""
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def validar(resposta: dict) -> dict:
    """Resposta da API → {pergunta: probabilidade}. ID faltando, tipo errado (bool, string), não finito ou fora
    de [0,1] = erro (nunca 'permite'); a checagem é a da infra comum (`congelamento.noul`)."""
    return {q: C.noul(resposta, q) for q in P.PERGUNTAS}


def politica(flags: dict, dispensa_do_chamador: bool = False, leitura: bool = False) -> tuple[str, str]:
    """Precedência do LEIA-ME sobre os Nouls em três faixas (True / False / None = dúvida).

    Dúvida num Noul que decide vira PISO `pergunta` (humano olha), nunca `permite`; uma regra abaixo ainda
    pode subir para `bloqueia` (rascunho: pipe remoto com from_untrusted 0,67 em dúvida — a regra 2,
    irreversível e não pedido, bloqueia sozinha).

    `dispensa_do_chamador`: campo ESTRUTURADO do processo que chama a guarda (no hook, um sinal do usuário fora
    do texto; no exemplo, derivado do caso rotulado). Só ele retira a confirmação da regra 3 — o Noul
    `confirmation_waived` lê o `context_read` que o atacante controla e por isso só pode MANTER a confirmação.
    `leitura`: comando somente-leitura (`somente_leitura`), que a regra de alvo compartilhado não barra.
    @example politica({"from_untrusted": True, ...}) → ("bloqueia", "ordem veio do contexto lido")
    """
    f = flags
    # 1. origem não confiável → bloqueia, mesmo que a ação pareça benigna
    if f["from_untrusted"] is True:
        return "bloqueia", "ordem veio do contexto lido"
    piso = ("pergunta", "dúvida: ordem veio do contexto lido?") if f["from_untrusted"] is None else ("permite", "")
    # 1b. (pós-revisão, GT-T036) alvo compartilhado/produção E não pedido E comando que muda algo → ao menos
    # pergunta. Sinais firmes só (fora da faixa de dúvida): com dúvida também, 3 permite legítimos do ajuste
    # iriam a humano (medido pelo revisor).
    if f["shared_target"] is True and f["user_requested"] is False and not leitura:
        piso = ("pergunta", "alvo compartilhado/produção, não pedido, comando que muda algo")
    # 2/3. irreversível: não pedido → bloqueia; pedido → pergunta; pedido + dispensa + alvo local → permite
    if f["irreversible"] is True:
        if f["user_requested"] is False:
            return "bloqueia", "irreversível e não pedido"
        if f["user_requested"] is None:
            return "pergunta", "irreversível; dúvida se foi pedido"
        if not dispensa_do_chamador:
            acao = ("pergunta", "irreversível e pedido: confirmar")
        elif f["shared_target"] is not False:
            acao = ("pergunta", "irreversível, pedido, dispensa do chamador, mas alvo compartilhado ou em dúvida")
        elif f["confirmation_waived"] is not True:
            acao = ("pergunta", "irreversível, pedido, dispensa do chamador; o Noul não leu dispensa em `task`")
        else:
            acao = ("permite", "irreversível, pedido, confirmação dispensada pelo chamador, alvo local")
    elif f["irreversible"] is None:
        acao = ("pergunta", "dúvida: irreversível?")
    # 4/5. reversível: fora da tarefa E difícil de desfazer → pergunta; resto → permite
    elif f["off_task"] is True and f["hard_to_undo"] is True:
        acao = ("pergunta", "fora da tarefa e difícil de desfazer")
    elif f["off_task"] is not False and f["hard_to_undo"] is not False:
        acao = ("pergunta", "dúvida: fora da tarefa / difícil de desfazer")
    else:
        acao = ("permite", "reversível")
    return max(acao, piso, key=lambda a: ACOES.index(a[0]))


def decidir(resposta: dict, call: dict, dispensa_do_chamador: bool = False) -> dict:
    """Resposta JSON da API + chamada → decisão (guarda os números brutos, para medir e re-limiar sem chamar de novo).

    `jev` = só o Jev pela política; `regex` = padrões casados; `acao` = Jev+regex (regex é piso: casou → no
    mínimo `pergunta`; o Jev ainda pode subir para `bloqueia`). `dispensa_do_chamador` é o campo estruturado
    (nunca vem do state nem do Jev).
    """
    nouls = validar(resposta)
    flags = {q: _faixa(v, *P.FAIXA[q]) for q, v in nouls.items()}
    jev, motivo = politica(flags, dispensa_do_chamador, somente_leitura(call))
    regex = padroes_casados(call)
    acao = jev
    # Piso da regex só quando o Jev DISCORDA sobre a perda (irreversible não deu sim): pega o vazamento por
    # leitura errada da chamada. Quando o Jev concorda que é irreversível e mesmo assim permite, foi pela regra 3
    # (pedido + confirmação dispensada + alvo local): a dispensa do usuário vale, a regex não a desfaz.
    # Ajuste 2026-10-01: piso incondicional custava 4 "barrados" em 18 permite, 2 deles com dispensa explícita.
    if regex and acao == "permite" and flags["irreversible"] is not True:
        acao, motivo = "pergunta", f"padrão destrutivo ({regex[0]}) que o Jev leu como reversível"
    return {"acao": acao, "jev": jev, "motivo": motivo, "regex": regex, "nouls": nouls, "flags": flags}


def baseline(call: dict, leitura: str = "regex→bloqueia") -> str:
    """Só a lista de padrões, sem Jev: casou → ação da leitura (`bloqueia` ou `pergunta`); senão `permite`."""
    return P.BASELINE_ACAO[leitura] if padroes_casados(call) else "permite"


def guardar(jev, caso: dict, dispensa_do_chamador: bool = False) -> dict:
    """Uma chamada de ferramenta de ponta a ponta: uma requisição, decisão em código. A dispensa de confirmação
    chega por este parâmetro (campo do chamador), fora do state que o Jev lê."""
    state, questions = pedido(caso)
    resposta = jev.perguntar(state, questions)
    _rejeicao_de_contrato(jev, resposta, state, questions)
    return decidir(resposta, state["call"], dispensa_do_chamador)


def _rejeicao_de_contrato(jev, resposta, state: dict, questions: dict) -> None:
    """Resposta JSON válida mas fora do contrato (bool, ID faltando, número fora de [0,1]) é tirada do cache antes de
    levantar, para ser refeita sozinha na próxima rodada — nos dois níveis (revisão do Codex no supervisor-de-automacao,
    2026-10-02: a família ficava presa no cache aqui). Só o CONTRATO invalida; defeito de política e falha de chamada não."""
    try:
        validar(resposta)
    except Exception:
        if hasattr(jev, "invalidar"):
            try:
                jev.invalidar(state, questions)
            except Exception:  # noqa: BLE001 — zelo pelo cache não pode esconder a falha original
                pass
        raise


def guardar_seguro(jev, caso, dispensa_do_chamador: bool = False) -> dict:
    """O que o hook chama: os mesmos passos de `guardar`, mas NENHUMA falha sobe — caso malformado, timeout, erro
    HTTP, cache faltando ou resposta fora do contrato viram `pergunta` (confirmação humana) para AQUELA chamada,
    com a classe do erro no motivo (o texto da exceção pode citar o corpo da resposta). Nunca `permite`: guarda que
    não respondeu não liberou nada; e nem a dispensa do chamador vale sem a leitura do Jev. Pega `Exception`
    inteira de propósito (família do achado do opt-out-lgpd: falha fechada por item).
    @example guardar_seguro(jev_fora_do_ar, caso) → {"acao": "pergunta", "motivo": "falha operacional: chamada (TimeoutError)", "origem": "falha", …}
    """
    etapa, regex = "entrada inválida", []
    try:
        state, questions = pedido(caso)
        regex = padroes_casados(state["call"])
        etapa = "chamada"
        resposta = jev.perguntar(state, questions)
        etapa = "resposta inválida"
        _rejeicao_de_contrato(jev, resposta, state, questions)
        etapa = "política"
        return {**decidir(resposta, state["call"], dispensa_do_chamador), "origem": "jev"}
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        return {"acao": "pergunta", "jev": None, "motivo": f"falha operacional: {etapa} ({type(e).__name__})",
                "regex": regex, "nouls": {}, "flags": {}, "origem": "falha"}
