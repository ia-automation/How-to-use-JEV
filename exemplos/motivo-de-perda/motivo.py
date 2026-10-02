"""Motivo de perda: o Jev julga em que grupo e em que folha da taxonomia está o motivo; o código valida, compõe e decide.

Fluxo por conversa (cada variante paga só as requisições de `ETAPAS[variante]`):
  código     valida conversa e taxonomia; monta o state com os fatos calculados (última fala do cliente, silêncio).
  `grupo`    (a) Choice `group` + 3 Nouls de guarda → grupo vencedor e sua probabilidade.
  `folhas`   (a) Choice `leaf` das folhas do grupo vencedor + `only_group`. A 1ª resposta decide as OPÇÕES da 2ª.
  `unica`    (b) Choice `leaf` sobre as 30 folhas + 3 Nouls; grupo = soma das probabilidades das folhas do grupo.
  `tudo`     (c) Choice `group` + uma Choice `leaf.<grupo>` por grupo + 3 Nouls, numa requisição; o código lê a
             Choice de folhas do grupo vencedor (as outras 7 foram perguntas especulativas com premissa explícita).
  código     `decidir`: aplica os limiares e as guardas de `perguntas.py` → `{grupo, folha, revisar}` por variante.

`julgar(etapas=MEDICAO)` (medição) envia os formatos pedidos e decide todas as variantes que eles alimentam;
`julgar()` (produção) envia só os da variante pedida. Toda resposta é validada logo depois da sua chamada (IDs
esperados, tipo, opções, números reais em [0, 1]); erro levanta exceção. O consumidor chama `julgar_seguro`: falha
operacional ou conversa inválida vira `sem_informacao` + `revisar` com `origem: "falha"` — nunca um motivo, e nunca
confundida com o `sem_informacao` julgado (`origem: "jev"`); resposta rejeitada pelo contrato sai do cache para ser
refeita sozinha na próxima rodada. Taxonomia inválida é defeito de quem chama: levanta erro (o `run.py` a valida uma
vez antes do lote). A saída é sugestão para o relatório de perda; fechar o lead continua sendo decisão do processo.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

ETAPAS = {"a": ("grupo", "folhas"), "b": ("unica",), "c": ("tudo",)}
MEDICAO = ("grupo", "folhas", "unica", "tudo")
_ID = re.compile(r"^[a-z][a-z0-9_]*$")
PAPEIS = set(P.PAPEL)


# ---------------------------------------------------------------------------------------- entrada
def validar_taxonomia(taxonomia: list[dict]) -> dict:
    """Confere a árvore e devolve `{folha: grupo}` na ordem da taxonomia. Erro aqui é defeito de quem chama."""
    if not isinstance(taxonomia, list) or len(taxonomia) < 2:
        raise ValueError("taxonomia precisa de ao menos 2 grupos")
    pai: dict[str, str] = {}
    for g in taxonomia:
        if not isinstance(g, dict) or not isinstance(g.get("id"), str) or not _ID.match(g["id"]) or g["id"] == P.SO_GRUPO:
            raise ValueError(f"grupo com id inválido: {g!r}")
        if any(not isinstance(g.get(k), str) or not g[k].strip() for k in ("nome", "descricao")):
            raise ValueError(f"grupo sem nome ou descrição: {g['id']}")
        if not isinstance(g.get("folhas"), list) or not g["folhas"]:
            raise ValueError(f"grupo sem folhas: {g['id']}")
        for f in g["folhas"]:
            if not isinstance(f, dict) or not isinstance(f.get("id"), str) or not _ID.match(f["id"]) or f["id"] == P.SO_GRUPO:
                raise ValueError(f"folha com id inválido em {g['id']}: {f!r}")
            if any(not isinstance(f.get(k), str) or not f[k].strip() for k in ("nome", "descricao")):
                raise ValueError(f"folha sem nome ou descrição: {f['id']}")
            if f["id"] in pai or f["id"] in {x["id"] for x in taxonomia}:
                raise ValueError(f"id repetido na árvore: {f['id']}")
            pai[f["id"]] = g["id"]
    if len({g["id"] for g in taxonomia}) != len(taxonomia):
        raise ValueError("grupo com id repetido")
    if P.SEM_INFORMACAO not in {g["id"] for g in taxonomia}:
        raise ValueError(f"taxonomia sem o grupo `{P.SEM_INFORMACAO}`")
    if len(pai) > P.MAX_FOLHAS:
        raise ValueError(f"mais de {P.MAX_FOLHAS} folhas não cabem numa Choice")
    return pai


class ConversaInvalida(ValueError):
    """Conversa fora da forma: é da CONVERSA (vira falha dela em `julgar_seguro`), não do lote como a taxonomia."""


def validar_conversa(conversa: list[dict]) -> None:
    """Lista de turnos `{de: cliente|corretor, texto}` não vazia, texto não vazio."""
    if not isinstance(conversa, list) or not conversa:
        raise ConversaInvalida("conversa vazia ou não é lista")
    for t in conversa:
        if not isinstance(t, dict) or t.get("de") not in PAPEIS or not isinstance(t.get("texto"), str) or not t["texto"].strip():
            raise ConversaInvalida(f"turno inválido: {t!r}")


def state_de(conversa: list[dict]) -> dict:
    """State enxuto: a conversa com papéis em inglês + dois fatos calculados em código (recência e contagem são do
    código — lição 30): a última fala do cliente e quantas mensagens do corretor ficaram sem resposta no fim.
    @example state_de([{"de": "cliente", "texto": "oi"}, {"de": "corretor", "texto": "Olá!"}, {"de": "corretor", "texto": "Ainda aí?"}])
             → {"conversation": [{"from": "customer", "text": "oi"}, {"from": "agent", "text": "Olá!"}, {"from": "agent", "text": "Ainda aí?"}],
                "last_customer_message": "oi", "agent_messages_after_last_customer_message": 2}
    """
    turnos = [{"from": P.PAPEL[t["de"]], "text": t["texto"].strip()} for t in conversa]
    do_cliente = [k for k, t in enumerate(turnos) if t["from"] == "customer"]
    ultimo = do_cliente[-1] if do_cliente else -1
    return {"conversation": turnos,
            "last_customer_message": turnos[ultimo]["text"] if do_cliente else None,
            "agent_messages_after_last_customer_message": len(turnos) - 1 - ultimo}


# ---------------------------------------------------------------------------------------- requisições
def pedido_grupo(taxonomia: list[dict]) -> dict:
    return {"group": P.choice_grupo(taxonomia), **P.nouls()}


def pedido_folhas(grupo: dict) -> dict:
    return {"leaf": P.choice_folhas(grupo)}


def pedido_unica(taxonomia: list[dict]) -> dict:
    return {"leaf": P.choice_unica(taxonomia), **P.nouls()}


def pedido_tudo(taxonomia: list[dict]) -> dict:
    return {"group": P.choice_grupo(taxonomia), **{f"leaf.{g['id']}": P.choice_folhas(g) for g in taxonomia}, **P.nouls()}


# ---------------------------------------------------------------------------------------- leitura das respostas
def _conferir_tipos(resposta: dict, questions: dict) -> None:
    """Todo ID pedido voltou, com o discriminador `type` batendo (quando vem). Ausência é erro, nunca 0."""
    answers = resposta.get("answers") if isinstance(resposta, dict) else None
    if not isinstance(answers, dict):
        raise ValueError(f"resposta sem `answers`: {type(resposta).__name__}")
    for q, p in questions.items():
        a = answers.get(q)
        if not isinstance(a, dict) or a.get("type", p["type"]) != p["type"]:
            raise ValueError(f"resposta sem `{q}` do tipo {p['type']}")


def _ler_nouls(resposta: dict) -> dict:
    return {k: CG.noul(resposta, k) for k in P.NOULS}


def _ler_choice_grupo(resposta: dict, taxonomia: list[dict]) -> dict:
    c = CG.choice(resposta, "group", {g["id"] for g in taxonomia})
    return {"grupo": c["choice"], "p": c["probabilities"], "conf": c["confidence"]}


def _ler_choice_folhas(resposta: dict, id_pergunta: str, grupo: dict) -> dict:
    """Choice de folhas de um grupo validada: `folha` None quando a escolha é `only_group`."""
    opcoes = {f["id"] for f in grupo["folhas"]} | ({P.SO_GRUPO} if grupo["id"] != P.SEM_INFORMACAO else set())
    c = CG.choice(resposta, id_pergunta, opcoes)
    return {"folha": None if c["choice"] == P.SO_GRUPO else c["choice"], "p": c["probabilities"], "conf": c["confidence"]}


def ler_grupo(resposta: dict, questions: dict, taxonomia: list[dict]) -> dict:
    _conferir_tipos(resposta, questions)
    return {**_ler_choice_grupo(resposta, taxonomia), "nouls": _ler_nouls(resposta)}


def ler_folhas(resposta: dict, questions: dict, grupo: dict) -> dict:
    _conferir_tipos(resposta, questions)
    return _ler_choice_folhas(resposta, "leaf", grupo)


def ler_unica(resposta: dict, questions: dict, taxonomia: list[dict], pai: dict) -> dict:
    """Choice única validada: folha vencedora, probabilidades e a probabilidade de cada GRUPO = soma das folhas dele
    (composição em código: a Choice é relativa, a soma por grupo também)."""
    _conferir_tipos(resposta, questions)
    c = CG.choice(resposta, "leaf", set(pai))
    p_grupo = {g["id"]: sum(c["probabilities"][f["id"]] for f in g["folhas"]) for g in taxonomia}
    grupo = max(p_grupo, key=p_grupo.get)  # empate: ordem da taxonomia (dict estável)
    return {"folha": c["choice"], "p": c["probabilities"], "conf": c["confidence"], "grupo": grupo, "p_grupo": p_grupo,
            "nouls": _ler_nouls(resposta)}


def ler_tudo(resposta: dict, questions: dict, taxonomia: list[dict]) -> dict:
    _conferir_tipos(resposta, questions)
    return {**_ler_choice_grupo(resposta, taxonomia),
            "folhas": {g["id"]: _ler_choice_folhas(resposta, f"leaf.{g['id']}", g) for g in taxonomia},
            "nouls": _ler_nouls(resposta)}


# ---------------------------------------------------------------------------------------- decisão
def _guardas(d: dict, nouls: dict, lim: dict) -> dict:
    """Guardas em código, nunca promoção: um Noul baixo tira a folha e manda revisar; um Noul alto não muda nada.
    `atendimento` sem `blames_agency` e `concorrencia` sem `closed_elsewhere` → só grupo + revisar (regra 8 do briefing).
    Qualquer grupo com motivo e `reason_stated` baixo → revisar (motivo possivelmente inventado)."""
    g = d["grupo"]
    # `≤`, não `<`: Noul exatamente no limiar (0,50 = sim e não igualmente prováveis) é empate, não sim — vai a revisão
    # (revisão do Codex, 2026-10-01).
    if g == P.ATENDIMENTO and nouls["blames_agency"] <= lim["guarda"]:
        d.update(folha=None, revisar=True, motivo=d["motivo"] + f"; guarda: `blames_agency` {nouls['blames_agency']:.2f} ≤ {lim['guarda']}")
    if g == P.CONCORRENCIA and nouls["closed_elsewhere"] <= lim["guarda"]:
        d.update(folha=None, revisar=True, motivo=d["motivo"] + f"; guarda: `closed_elsewhere` {nouls['closed_elsewhere']:.2f} ≤ {lim['guarda']}")
    if g != P.SEM_INFORMACAO and nouls["reason_stated"] < lim["sem_motivo"]:
        d.update(revisar=True, motivo=d["motivo"] + f"; guarda: `reason_stated` {nouls['reason_stated']:.2f} < {lim['sem_motivo']}")
    return d


def _duas_etapas(grupo: str, p_grupo: float, folhas: dict, lim: dict, limiar_folha: str = "folha") -> dict:
    """Política comum a a e c: grupo abaixo do limiar → revisar sem folha; `only_group` ou folha fraca → só grupo."""
    if p_grupo < lim["grupo"]:
        return {"grupo": grupo, "folha": None, "revisar": True, "p_grupo": p_grupo, "p_folha": None,
                "motivo": f"p(grupo) {p_grupo:.2f} < {lim['grupo']}: revisar"}
    f = folhas["folha"]
    if f is None:
        return {"grupo": grupo, "folha": None, "revisar": False, "p_grupo": p_grupo, "p_folha": folhas["p"].get(P.SO_GRUPO),
                "motivo": f"Choice de folhas disse `{P.SO_GRUPO}`"}
    pf = folhas["p"][f]
    if pf < lim[limiar_folha]:
        return {"grupo": grupo, "folha": None, "revisar": False, "p_grupo": p_grupo, "p_folha": pf,
                "motivo": f"p(folha) {pf:.2f} < {lim[limiar_folha]}: só grupo"}
    return {"grupo": grupo, "folha": f, "revisar": False, "p_grupo": p_grupo, "p_folha": pf, "motivo": f"p(grupo) {p_grupo:.2f}, p(folha) {pf:.2f}"}


def decidir(grupo: dict | None = None, folhas: dict | None = None, unica: dict | None = None, tudo: dict | None = None,
            limiares: dict | None = None) -> dict:
    """Sinais JÁ VALIDADOS → decisão de cada variante cujos sinais chegaram: `{variante: {grupo, folha, revisar, motivo, …}}`.
    `folha` None = só o grupo. `revisar` True = o código não fecha sozinho (grupo e folha ficam como sugestão).
    a   Choice do grupo (+ guardas) → Choice das folhas do grupo vencedor.
    b   Choice única: grupo = soma das probabilidades das folhas do grupo; folha = vencedora se p ≥ `folha_unica`.
    c   igual a a, lendo a Choice `leaf.<grupo vencedor>` da mesma requisição.
    """
    lim = limiares or P.LIMIAR
    out: dict = {}
    if grupo is not None and folhas is not None:
        d = _duas_etapas(grupo["grupo"], grupo["p"][grupo["grupo"]], folhas, lim)
        out["a"] = _guardas(d, grupo["nouls"], lim)
    if unica is not None:
        g = unica["grupo"]
        pf = unica["p"][unica["folha"]]
        d = _duas_etapas(g, unica["p_grupo"][g], {"folha": unica["folha"], "p": unica["p"]}, lim, "folha_unica")
        # A folha vencedora pode estar FORA do grupo de maior soma (grupo A com 3 folhas de 0,2; folha de B com 0,35):
        # nesse caso o grupo manda e a folha não entra (só grupo). Decidido em código, não pela Choice.
        if d["folha"] is not None and unica["pai"][unica["folha"]] != g:
            d.update(folha=None, p_folha=pf, motivo=f"folha vencedora fora do grupo de maior soma ({g} {unica['p_grupo'][g]:.2f}): só grupo")
        out["b"] = _guardas(d, unica["nouls"], lim)
    if tudo is not None:
        g = tudo["grupo"]
        d = _duas_etapas(g, tudo["p"][g], tudo["folhas"][g], lim)
        out["c"] = _guardas(d, tudo["nouls"], lim)
    return out


def _vazio(grupo: str, motivo: str, origem: str) -> dict:
    return {"grupo": grupo, "folha": None, "revisar": True, "origem": origem, "motivo": motivo, "decisoes": {}, "sinais": {}, "etapas": []}


def julgar(jev, conversa: list[dict], taxonomia: list[dict], variante: str | None = None, etapas: tuple | None = None,
           _rastro: dict | None = None) -> dict:
    """Uma conversa de ponta a ponta. Devolve `grupo`, `folha` (ID ou None), `revisar`, `origem` ("jev"), `motivo`,
    `decisoes` (uma por variante decidida), `sinais` e `etapas` (formato de cada chamada, na ordem).
    `etapas` None (produção) = só as requisições da variante; a medição passa `MEDICAO`.
    Erro de chamada ou de contrato levanta exceção — o consumidor usa `julgar_seguro`."""
    variante = variante or P.VARIANTE_PRINCIPAL
    rastro = _rastro if _rastro is not None else {}
    rastro.update(etapas=[], em="entrada")
    pai = validar_taxonomia(taxonomia)
    validar_conversa(conversa)
    if variante not in ETAPAS or not set(ETAPAS[variante]) <= set(etapas or ETAPAS[variante]) <= set(MEDICAO):
        raise ValueError(f"variante ou etapas inválidas: {variante!r}, {etapas!r}")
    if "folhas" in (etapas or ETAPAS[variante]) and "grupo" not in (etapas or ETAPAS[variante]):
        raise ValueError("`folhas` depende de `grupo`")
    tamanho = sum(len(t["texto"]) for t in conversa)
    if tamanho > P.TETO_CARACTERES:
        return {**_vazio(P.SEM_INFORMACAO, f"conversa longa ({tamanho} caracteres; teto {P.TETO_CARACTERES}): revisar, sem chamada", "jev"),
                "longa": True, "invalida": False}
    por_id = {g["id"]: g for g in taxonomia}
    state = state_de(conversa)

    def chamar(etapa: str, questions: dict, ler) -> dict:
        rastro["em"] = etapa
        resposta = jev.perguntar(state, questions)
        rastro["etapas"].append(etapa)
        try:
            return ler(resposta, questions)
        except ValueError:
            # Chamada feita e gravada pelo cliente, mas resposta fora do contrato: `julgar_seguro` tira SÓ este pedido do cache.
            rastro["rejeitado"] = (state, questions)
            raise

    precisa = set(etapas or ETAPAS[variante])
    grupo = folhas = unica = tudo = None
    if "grupo" in precisa:
        grupo = chamar("grupo", pedido_grupo(taxonomia), lambda r, q: ler_grupo(r, q, taxonomia))
        if "folhas" in precisa:
            g = por_id[grupo["grupo"]]
            folhas = chamar("folhas", pedido_folhas(g), lambda r, q: ler_folhas(r, q, g))
    if "unica" in precisa:
        unica = {**chamar("unica", pedido_unica(taxonomia), lambda r, q: ler_unica(r, q, taxonomia, pai)), "pai": pai}
    if "tudo" in precisa:
        tudo = chamar("tudo", pedido_tudo(taxonomia), lambda r, q: ler_tudo(r, q, taxonomia))
    decisoes = decidir(grupo, folhas, unica, tudo)
    d = decisoes[variante]
    return {"grupo": d["grupo"], "folha": d["folha"], "revisar": d["revisar"], "origem": "jev", "longa": False, "invalida": False,
            "motivo": f"variante `{variante}`: {d['motivo']}", "decisoes": decisoes,
            "sinais": {"grupo": grupo, "folhas": folhas, "unica": unica, "tudo": tudo}, "etapas": rastro["etapas"]}


def julgar_seguro(jev, conversa: list[dict], taxonomia: list[dict], variante: str | None = None, etapas: tuple | None = None) -> dict:
    """O que o consumidor chama. Falha operacional — timeout, erro da API, resposta ausente ou fora do contrato, em
    qualquer requisição — e conversa inválida (vazia, nula, turno sem `de` ou sem texto) viram `sem_informacao` +
    `revisar` com `origem: "falha"` DAQUELA conversa: o relatório não ganha motivo e a conversa vai para a fila humana;
    o lote não aborta (`invalida: True` marca a entrada inválida, que não chamou nada). Resposta com JSON válido mas
    rejeitada pelo contrato é tirada do cache (`jev.invalidar`) para que SÓ ela seja refeita na próxima rodada; falha
    de chamada não invalida nada. Taxonomia, variante ou etapas inválidas continuam levantando erro: é defeito de quem
    chama, antes de qualquer requisição."""
    rastro: dict = {}
    try:
        return julgar(jev, conversa, taxonomia, variante, etapas, rastro)
    except ConversaInvalida as e:
        # Revisão do Codex (2026-10-01): relançar aqui fazia o `ex.map` do run.py abortar o lote inteiro por uma conversa.
        return {**_vazio(P.SEM_INFORMACAO, f"entrada inválida: {e}", "falha"), "longa": False, "invalida": True}
    except Exception as e:  # noqa: BLE001 — qualquer falha depois da entrada é da conversa, não do lote
        if rastro.get("em", "entrada") == "entrada":
            raise
        motivo = f"falha operacional: requisição `{rastro['em']}` ({type(e).__name__})"
        if "rejeitado" in rastro:
            # Revisão do Codex (2026-10-01): o cliente grava a resposta antes da validação; sem isto a próxima rodada
            # consumiria a mesma resposta inválida para sempre. A quarentena falhar não tira a escalada.
            try:
                jev.invalidar(*rastro["rejeitado"])
                motivo += "; resposta rejeitada tirada do cache"
            except Exception as e2:  # noqa: BLE001
                motivo += f"; quarentena falhou ({type(e2).__name__})"
        return {**_vazio(P.SEM_INFORMACAO, motivo, "falha"), "longa": False, "invalida": False, "etapas": rastro["etapas"]}


# ---------------------------------------------------------------------------------------- baseline de código
def _plano(texto: str) -> str:
    """Minúsculas, sem acento."""
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


_VAZIAS = {_plano(w) for w in P.VAZIAS}


def _termos(texto: str) -> set[str]:
    """@example _termos("O valor pedido está acima do orçamento") → {"valor", "pedid", "acima", "orcam"}"""
    return {w[:P.RADICAL] for w in re.findall(r"[a-z0-9]+", _plano(texto)) if len(w) > 2 and w not in _VAZIAS}


def chaves_do_baseline(taxonomia: list[dict]) -> dict:
    """{folha: radicais de nome + descrição}, na ordem da taxonomia — derivado, não escrito à mão."""
    return {f["id"]: _termos(f"{f['nome']} {f['descricao']}") for g in taxonomia for f in g["folhas"]}


def baseline(conversa: list[dict], taxonomia: list[dict], pai: dict | None = None) -> dict:
    """Palavra-chave por folha nas mensagens do CLIENTE: a folha com mais radicais em comum vence (empate: ordem da
    taxonomia). Sem nenhum radical em comum → `sem_informacao` por contagem de silêncio: ≥ `SILENCIO_MINIMO` mensagens
    do corretor sem resposta no fim → `sumiu_apos_valor` se houve "R$" nelas, senão `sumiu_sem_resposta`; menos que
    isso → `adiou_sem_motivo`. Palavra não sabe o que é ordem, confissão nem quem falou o quê — é a régua de baixo."""
    pai = pai or validar_taxonomia(taxonomia)
    chaves = chaves_do_baseline(taxonomia)
    df = {t: sum(t in ch for ch in chaves.values()) for ch in chaves.values() for t in ch}  # radical comum a muitas folhas pesa menos
    do_cliente = _termos(" ".join(t["texto"] for t in conversa if t["de"] == "cliente"))
    pontos = {f: round(sum(1 / df[t] for t in ch & do_cliente), 3) for f, ch in chaves.items()}
    melhor = max(pontos, key=pontos.get)
    if pontos[melhor] > 0:
        return {"grupo": pai[melhor], "folha": melhor, "revisar": False, "pontos": pontos[melhor]}
    s = state_de(conversa)
    cauda = s["agent_messages_after_last_customer_message"]
    if cauda >= P.SILENCIO_MINIMO:
        com_valor = any("r$" in t["texto"].lower() for t in conversa[len(conversa) - cauda:])
        return {"grupo": P.SEM_INFORMACAO, "folha": "sumiu_apos_valor" if com_valor else "sumiu_sem_resposta", "revisar": False, "pontos": 0}
    return {"grupo": P.SEM_INFORMACAO, "folha": "adiou_sem_motivo", "revisar": False, "pontos": 0}
