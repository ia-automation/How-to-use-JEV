"""Seleção de skill: o Jev julga qual skill do catálogo serve ao pedido (ou nenhuma); o código valida, compõe e decide.

Fluxo por pedido (cada variante paga só as requisições de `ETAPAS[variante]`):
  código           valida pedido e catálogo; pedido acima do teto não é enviado (sem sugestão).
  `ampla`          Choice `which` sobre o catálogo inteiro + `none`, descrição curta → vencedor e as 3 melhores skills.
  `fits_vencedor`  (b) um Noul `fits` do vencedor da ampla — só quando a ampla não disse `none`.
  `rerank`         (c, c2, d) Choice entre as 3 melhores com o texto completo + um Noul `fits` por candidata + as 3
                   portas da receita. A resposta da ampla decide as OPÇÕES desta requisição: é o motivo da 2ª chamada.
  `todos`          (e) um Noul `fits` por skill, todas numa requisição.
  `ampla_completa` (a2, informativa) a Choice ampla com a descrição inteira de cada skill.
  código           `decidir`: aplica os limiares de `perguntas.py` e devolve no máximo UMA skill por variante.

`selecionar(etapas=MEDICAO)` (medição) envia os formatos pedidos e decide todas as variantes que eles alimentam;
`selecionar()` (produção) envia só os da variante pedida. Toda resposta é validada logo depois da sua
chamada (IDs esperados, tipo, opções, números reais em [0, 1]); erro levanta exceção. O consumidor chama
`selecionar_seguro`: falha operacional vira "sem sugestão" marcada como FALHA — nunca uma skill, e nunca confundida
com o "nenhuma skill" julgado. A sugestão é dica para o agente, não autorização para executar nada.
"""
from __future__ import annotations

import math
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

# Formatos de requisição que cada variante envia em produção, na ordem. `fits_vencedor` só sai quando a ampla
# escolheu uma skill. O custo de cada variante no relatório é a soma exata destas requisições.
ETAPAS = {"a": ("ampla",), "b": ("ampla", "fits_vencedor"), "c": ("ampla", "rerank"), "c2": ("ampla", "rerank"),
          "d": ("ampla", "rerank"), "e": ("todos",), "a2": ("ampla_completa",)}
MEDICAO = ("ampla", "fits_vencedor", "rerank", "todos")  # as requisições das seis variantes do critério
MEDICAO_COM_A2 = (*MEDICAO, "ampla_completa")            # + a informativa
_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


# ---------------------------------------------------------------------------------------- entrada
def validar_entrada(pedido: str, catalogo: list[dict]) -> list[str]:
    """Confere pedido e catálogo antes de qualquer chamada e devolve os IDs, na ordem do catálogo.
    Erro aqui é defeito de quem chama (levanta ValueError), não falha operacional."""
    if not isinstance(pedido, str) or not pedido.strip():
        raise ValueError("pedido vazio ou não textual")
    if not isinstance(catalogo, list) or not P.SHORTLIST <= len(catalogo) <= P.MAX_SKILLS:
        raise ValueError(f"catálogo precisa de {P.SHORTLIST} a {P.MAX_SKILLS} skills")
    ids = []
    for s in catalogo:
        if not isinstance(s, dict) or not isinstance(s.get("id"), str) or not _ID.match(s["id"]) or s["id"] == P.NENHUMA:
            raise ValueError(f"skill com id inválido (hífen-minúsculo, diferente de `{P.NENHUMA}`): {s!r}")
        if any(not isinstance(s.get(k), str) or not s[k].strip() for k in ("nome", "descricao")):
            raise ValueError(f"skill sem nome ou descrição: {s['id']}")
        ids.append(s["id"])
    if len(set(ids)) != len(ids):
        raise ValueError("catálogo com id repetido")
    return ids


def state_de(pedido: str) -> dict:
    """@example state_de("Sobe pra homolog.") → {"request": "Sobe pra homolog."}"""
    return {"request": pedido.strip()}


# ---------------------------------------------------------------------------------------- requisições
def pedido_ampla(catalogo: list[dict], inteira: bool = False) -> dict:
    return {"which": P.choice_ampla(catalogo, inteira)}


def pedido_fits(skills: list[dict]) -> dict:
    return {f"fits.{s['id']}": P.noul_fits(s) for s in skills}


def pedido_rerank(candidatas: list[dict]) -> dict:
    return {"rerank": P.choice_rerank(candidatas), **pedido_fits(candidatas), **P.nouls_porta()}


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


def ler_ampla(resposta: dict, questions: dict, ids: list[str]) -> dict:
    """Choice ampla validada → vencedor (None = `none`), confiança e as `SHORTLIST` melhores SKILLS (a válvula não
    entra na shortlist: a receita relê as 3 skills mais prováveis mesmo quando nenhuma convence). Empate: ordem do catálogo."""
    _conferir_tipos(resposta, questions)
    c = CG.choice(resposta, "which", {*ids, P.NENHUMA})
    probs = c["probabilities"]
    ranking = sorted(ids, key=lambda i: -probs[i])  # ordenação estável
    escolha = None if c["choice"] == P.NENHUMA else c["choice"]
    return {"escolha": escolha, "conf": c["confidence"], "p_nenhuma": probs[P.NENHUMA],
            "shortlist": ranking[:P.SHORTLIST], "probs": {i: probs[i] for i in ranking[:P.SHORTLIST]}}


def ler_fits(resposta: dict, questions: dict, ids: list[str]) -> dict:
    """{id: `fits`} validado para os IDs pedidos."""
    _conferir_tipos(resposta, {f"fits.{i}": questions[f"fits.{i}"] for i in ids})
    return {i: CG.noul(resposta, f"fits.{i}") for i in ids}


def ler_rerank(resposta: dict, questions: dict, shortlist: list[str]) -> dict:
    """2ª requisição da receita validada: vencedor da Choice, `fits` por candidata e a porta (média das 3 orientadas)."""
    _conferir_tipos(resposta, questions)
    c = CG.choice(resposta, "rerank", set(shortlist))
    portas = {k: CG.noul(resposta, f"gate.{k}") for k in P.PORTAS}
    orientadas = [1.0 - v if k in P.INVERTIDAS else v for k, v in portas.items()]
    return {"vencedor": c["choice"], "conf": c["confidence"], "probs": c["probabilities"],
            "fits": ler_fits(resposta, questions, shortlist), "portas": portas, "porta": sum(orientadas) / len(orientadas)}


# ---------------------------------------------------------------------------------------- decisão
def _d(skill: str | None, sinal: float | None, motivo: str) -> dict:
    return {"skill": skill, "sinal": sinal, "motivo": motivo}


def decidir(ampla: dict | None = None, fits_vencedor: float | None = None, rerank: dict | None = None,
            todos: dict | None = None, limiares: dict | None = None, ampla_completa: dict | None = None) -> dict:
    """Sinais JÁ VALIDADOS → decisão de cada variante cujos sinais chegaram: `{variante: {skill, sinal, motivo}}`.
    `skill` None = nenhuma skill. `sinal` = o número que o portão da variante olhou (confiança da Choice em `a`).

    a   vencedor da ampla.
    b   vencedor da ampla, se o `fits` DELE ≥ limiar (portão no vencedor consumido).
    c   receita ao pé da letra: porta ≥ limiar e MAIOR `fits` da shortlist ≥ limiar → vencedor da Choice `rerank`
        (que pode não ser o candidato que passou no portão — a ressalva de `padroes-das-receitas`).
    c2  igual a c, mas o portão olha o `fits` do vencedor da `rerank`.
    d   igual a c, mas o vencedor É o candidato de maior `fits` (empate: ordem da shortlist).
    e   maior `fits` entre todas as skills, se ≥ limiar (empate: ordem do catálogo).
    a2  (informativa) vencedor da Choice ampla com a descrição completa.
    """
    lim = limiares or P.LIMIAR
    out: dict = {}
    if ampla is not None:
        v = ampla["escolha"]
        out["a"] = _d(v, ampla["conf"], "vencedor da Choice ampla" if v else "a Choice ampla disse `none`")
        if v is None:
            out["b"] = _d(None, None, "a Choice ampla disse `none`")
        elif fits_vencedor is not None:
            passa = fits_vencedor >= lim["fits"]
            out["b"] = _d(v if passa else None, fits_vencedor, f"`fits` do vencedor {'≥' if passa else '<'} {lim['fits']}")
    if rerank is not None:
        fits = rerank["fits"]
        maior = max(fits, key=fits.get)  # dict na ordem da shortlist: empate fica com o mais provável na ampla
        venc = rerank["vencedor"]
        if rerank["porta"] < lim["porta"]:
            fechada = _d(None, rerank["porta"], f"porta < {lim['porta']}")
            out.update(c=fechada, c2=fechada, d=fechada)
        else:
            ok = fits[maior] >= lim["fits"]
            out["c"] = _d(venc if ok else None, fits[maior], f"maior `fits` da shortlist {'≥' if ok else '<'} {lim['fits']}")
            ok2 = fits[venc] >= lim["fits"]
            out["c2"] = _d(venc if ok2 else None, fits[venc], f"`fits` do vencedor da rerank {'≥' if ok2 else '<'} {lim['fits']}")
            out["d"] = _d(maior if ok else None, fits[maior], f"maior `fits` {'≥' if ok else '<'} {lim['fits']}")
    if todos is not None:
        maior = max(todos, key=todos.get)
        ok = todos[maior] >= lim["fits_todos"]
        out["e"] = _d(maior if ok else None, todos[maior], f"maior `fits` do catálogo {'≥' if ok else '<'} {lim['fits_todos']}")
    if ampla_completa is not None:
        v = ampla_completa["escolha"]
        out["a2"] = _d(v, ampla_completa["conf"], "vencedor da Choice com descrição completa" if v else "a Choice disse `none`")
    return out


def selecionar(jev, pedido: str, catalogo: list[dict], variante: str | None = None, etapas: tuple | None = None,
               _rastro: dict | None = None) -> dict:
    """Um pedido de ponta a ponta. Devolve `skill` (ID do catálogo ou None), `nome`, `motivo`, `decisoes` (uma por
    variante decidida), `sinais` (o que cada requisição respondeu) e `etapas` (formato de cada chamada, na ordem).
    `etapas` None (produção) = só as requisições da variante; a medição passa `MEDICAO` ou `MEDICAO_COM_A2`.
    Erro de chamada ou de contrato levanta exceção — o consumidor usa `selecionar_seguro`."""
    variante = variante or P.VARIANTE_PRINCIPAL
    rastro = _rastro if _rastro is not None else {}
    rastro.update(etapas=[], em="entrada")
    ids = validar_entrada(pedido, catalogo)
    if variante not in ETAPAS or not set(ETAPAS[variante]) <= set(etapas or ETAPAS[variante]) <= set(MEDICAO_COM_A2):
        raise ValueError(f"variante ou etapas inválidas: {variante!r}, {etapas!r}")
    por_id = {s["id"]: s for s in catalogo}
    if len(pedido) > P.TETO_CARACTERES:
        return {"skill": None, "nome": None, "longo": True, "falha": False, "decisoes": {}, "sinais": {}, "etapas": [],
                "motivo": f"pedido longo ({len(pedido)} caracteres; teto {P.TETO_CARACTERES}): sem sugestão, sem chamada"}
    state = state_de(pedido)

    def chamar(etapa: str, questions: dict) -> dict:
        rastro["em"] = etapa
        resposta = jev.perguntar(state, questions)
        rastro["etapas"].append(etapa)
        return resposta

    precisa = set(etapas or ETAPAS[variante])
    ampla = fits_v = rerank = todos = inteira = None
    if "ampla" in precisa:
        q = pedido_ampla(catalogo)
        ampla = ler_ampla(chamar("ampla", q), q, ids)
        if "fits_vencedor" in precisa and ampla["escolha"]:
            v = ampla["escolha"]
            q = pedido_fits([por_id[v]])
            fits_v = ler_fits(chamar("fits_vencedor", q), q, [v])[v]
        if "rerank" in precisa:
            q = pedido_rerank([por_id[i] for i in ampla["shortlist"]])
            rerank = ler_rerank(chamar("rerank", q), q, ampla["shortlist"])
    if "todos" in precisa:
        q = pedido_fits(catalogo)
        todos = ler_fits(chamar("todos", q), q, ids)
    if "ampla_completa" in precisa:
        q = pedido_ampla(catalogo, inteira=True)
        inteira = ler_ampla(chamar("ampla_completa", q), q, ids)
    decisoes = decidir(ampla, fits_v, rerank, todos, ampla_completa=inteira)
    escolha = decisoes[variante]
    return {"skill": escolha["skill"], "nome": por_id[escolha["skill"]]["nome"] if escolha["skill"] else None,
            "motivo": f"variante `{variante}`: {escolha['motivo']}", "longo": False, "falha": False, "decisoes": decisoes,
            "sinais": {"ampla": ampla, "fits_vencedor": fits_v, "rerank": rerank, "todos": todos, "ampla_completa": inteira},
            "etapas": rastro["etapas"]}


def selecionar_seguro(jev, pedido: str, catalogo: list[dict], variante: str | None = None, etapas: tuple | None = None) -> dict:
    """O que o consumidor chama. Falha operacional — timeout, erro da API, resposta ausente ou fora do contrato, em
    qualquer requisição — vira "sem sugestão" DAQUELE pedido com `falha` = True e o motivo (etapa + classe do erro):
    o agente segue com o índice e o próprio julgamento, e o lote não aborta. Entrada inválida continua levantando
    erro: é defeito de quem chama, antes de qualquer requisição."""
    rastro: dict = {}
    try:
        return selecionar(jev, pedido, catalogo, variante, etapas, rastro)
    except Exception as e:  # noqa: BLE001 — qualquer falha depois da entrada é do item, não do lote
        if rastro.get("em", "entrada") == "entrada":
            raise
        return {"skill": None, "nome": None, "longo": False, "falha": True, "decisoes": {}, "sinais": {},
                "etapas": rastro["etapas"], "motivo": f"falha operacional: requisição `{rastro['em']}` ({type(e).__name__})"}


# ---------------------------------------------------------------------------------------- baseline de código
def _plano(texto: str) -> str:
    """Minúsculas, sem acento."""
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


_VAZIAS = {_plano(w) for w in P.VAZIAS}


def _termos(texto: str) -> list[str]:
    """@example _termos("Revisa o diff da revisão") → ["revis", "diff", "revis"]"""
    return [w[:P.RADICAL] for w in re.findall(r"[a-z0-9]+", _plano(texto)) if len(w) > 1 and w not in _VAZIAS]


def baseline(pedido: str, catalogo: list[dict], limiar: float | None = None) -> dict:
    """BM25 do pedido contra id + nome + descrição de cada skill; a melhor vence se a pontuação ≥ limiar, senão
    nenhuma. Sobreposição de palavras não sabe o que é intenção, negação nem "trivial" — é a régua de baixo."""
    limiar = P.LIMIAR["baseline"] if limiar is None else limiar
    docs = {s["id"]: _termos(f"{s['id'].replace('-', ' ')} {s['nome']} {s['descricao']}") for s in catalogo}
    media = sum(len(d) for d in docs.values()) / len(docs)
    consulta = set(_termos(pedido))
    df = {t: sum(t in d for d in docs.values()) for t in consulta}
    pontos = {}
    for i, d in docs.items():
        total = 0.0
        for t in consulta:
            tf = d.count(t)
            if tf:
                idf = math.log(1 + (len(docs) - df[t] + 0.5) / (df[t] + 0.5))
                total += idf * tf * (P.BM25_K1 + 1) / (tf + P.BM25_K1 * (1 - P.BM25_B + P.BM25_B * len(d) / media))
        pontos[i] = total
    melhor = max(pontos, key=pontos.get)
    return {"skill": melhor if pontos[melhor] > 0 and pontos[melhor] >= limiar else None, "melhor": melhor, "pontos": pontos[melhor]}
