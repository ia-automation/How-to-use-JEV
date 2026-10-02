"""Imóvel errado: UMA requisição ao Jev por conversa (Choice do referente + 3 Nouls); a ação é do código.

O Jev só julga: de qual candidato a última mensagem do cliente trata, se a referência é inequívoca, se o
rascunho usa fato de outro candidato, se o rascunho se compromete com um candidato. O código decide:
`manter` (rascunho segue), `trocar_referente` (sugere o candidato certo; NUNCA reescreve o rascunho — isso é
do LLM que o gerou), `pedir_esclarecimento` (perguntar ao cliente de qual imóvel fala). Nenhuma mensagem é
enviada daqui. Ausência de resposta, ID fora da lista, distribuição da Choice incompleta ou número inválido
é ERRO, nunca `manter`. Candidatos fora de 2–4, ID repetido ou igual à válvula, resumo vazio = erro ANTES da
chamada. Conversa acima do teto (`perguntas.TETO_*`) não vai ao Jev: `pedir_esclarecimento`, motivo
"conversa longa". Comparativos numéricos (mais barato, maior, mais quartos, mais vagas) são do CÓDIGO e
entram no state como `comparatives` — o Jev lê o resultado, não faz a conta.

Candidato a guarda da Luci (0800): roda entre o rascunho e o envio.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

ACOES = ["manter", "trocar_referente", "pedir_esclarecimento"]
_DE = {"cliente": "customer", "agente": "agent"}
# Campos estruturados lidos do resumo (pt-BR dos anúncios). Preço só com sufixo mil/mi: "condomínio R$ 800" não é
# preço do imóvel. "quintal 200 m²" não é área do imóvel. "sem vaga" = 0; "vaga rotativa" (sem número) = desconhecido.
_RE_PRECO = re.compile(r"R\$\s*(\d+(?:[.,]\d+)?)\s*(mil|mi)\b", re.I)
_RE_AREA = re.compile(r"(?<!quintal )(\d+)\s*m²")
_RE_QUARTOS = re.compile(r"(\d+)\s*(?:quartos?|suítes?)", re.I)
_RE_VAGAS = re.compile(r"(\d+)\s*vagas?", re.I)
# {campo: [(chave em `comparatives`, função de extremo)]}
_COMPARATIVOS = {"price": [("cheapest", min), ("most_expensive", max)], "area": [("largest", max), ("smallest", min)],
                 "bedrooms": [("most_bedrooms", max)], "parking": [("most_parking", max)]}


def extrair_campos(resumo: str) -> dict:
    """Preço (R$), área (m²), quartos e vagas do resumo; campo ausente = None (nunca chuta).
    @example extrair_campos("Apto 2 quartos em Perdizes, 72 m², 1 vaga, R$ 790 mil")
             → {"price": 790000.0, "area": 72, "bedrooms": 2, "parking": 1}
    @example extrair_campos("Apto 1 quarto na Barra, 45 m², sem vaga, R$ 1,2 mi")
             → {"price": 1200000.0, "area": 45, "bedrooms": 1, "parking": 0}
    """
    preco = _RE_PRECO.search(resumo)
    valor = None
    if preco:
        valor = float(preco.group(1).replace(".", "").replace(",", ".")) * (1e6 if preco.group(2).lower() == "mi" else 1e3)
    area, quartos, vagas = _RE_AREA.search(resumo), _RE_QUARTOS.search(resumo), _RE_VAGAS.search(resumo)
    return {
        "price": valor,
        "area": int(area.group(1)) if area else None,
        "bedrooms": int(quartos.group(1)) if quartos else None,
        "parking": int(vagas.group(1)) if vagas else (0 if re.search(r"\bsem vaga", resumo, re.I) else None),
    }


def comparativos(candidatos: list[dict]) -> dict[str, str]:
    """{comparativo: id} calculado pelo código, SÓ quando todos os candidatos têm o campo e o extremo é único
    (empate ou campo faltando = o comparativo não existe; o Jev então não tem "o mais barato" para apontar).
    @example comparativos([{"id": "a", "summary": "2 quartos, R$ 720 mil"}, {"id": "b", "summary": "3 quartos, R$ 740 mil"}])
             → {"cheapest": "a", "most_expensive": "b", "most_bedrooms": "b"}
    """
    campos = {c["id"]: extrair_campos(c["summary"]) for c in candidatos}
    saida = {}
    for campo, extremos in _COMPARATIVOS.items():
        valores = {i: f[campo] for i, f in campos.items()}
        if any(v is None for v in valores.values()):
            continue
        for chave, extremo in extremos:
            alvo = extremo(valores.values())
            vencedores = [i for i, v in valores.items() if v == alvo]
            if len(vencedores) == 1:
                saida[chave] = vencedores[0]
    return saida


def validar_candidatos(candidatos: list[dict]) -> None:
    """Antes da chamada (achado 2): 2–4 candidatos, IDs textuais únicos e diferentes da válvula, resumo não vazio.
    Dois imóveis com o mesmo ID virariam UMA opção da Choice em silêncio; um resumo vazio é uma opção sem descrição."""
    if not P.MIN_CANDIDATOS <= len(candidatos) <= P.MAX_CANDIDATOS:
        raise ValueError(f"{len(candidatos)} candidatos; esperado {P.MIN_CANDIDATOS}–{P.MAX_CANDIDATOS}")
    ids = [c.get("id") for c in candidatos]
    if any(not isinstance(i, str) or not i.strip() or i == P.NEI for i in ids) or len(set(ids)) != len(ids):
        raise ValueError(f"IDs de candidato inválidos ou repetidos: {ids!r}")
    if any(not isinstance(c.get("summary"), str) or not c["summary"].strip() for c in candidatos):
        raise ValueError("candidato com resumo vazio")


def state_de(caso: dict) -> dict:
    """Caso rotulado (pt) → state enxuto com os nomes que as perguntas citam entre crases.

    Preserva a ORDEM dos candidatos (LEIA-ME: IDs na ordem de apresentação; "o primeiro" = candidates[0]) e
    acrescenta `comparatives`, calculado pelo código sobre os resumos (achado 5).
    @example state_de({"conversa": [{"de": "cliente", "texto": "oi"}], "candidatos": [{"id": "IM-01", "resumo": "r"}],
                       "rascunho": "x"})
             → {"conversation": [{"from": "customer", "text": "oi"}], "candidates": [{"id": "IM-01", "summary": "r"}],
                "draft": "x", "comparatives": {}}
    """
    candidatos = [{"id": c["id"], "summary": c["resumo"]} for c in caso["candidatos"]]
    return {
        "conversation": [{"from": _DE[m["de"]], "text": m["texto"]} for m in caso["conversa"]],
        "candidates": candidatos,
        "draft": caso["rascunho"],
        "comparatives": comparativos(candidatos),
    }


def conversa_longa(state: dict) -> str | None:
    """Motivo se a conversa passa do teto (turnos ou caracteres); None dentro da faixa validada."""
    turnos, chars = len(state["conversation"]), sum(len(m["text"]) for m in state["conversation"])
    if turnos > P.TETO_TURNOS or chars > P.TETO_CARACTERES:
        return f"conversa longa ({turnos} turnos, {chars} caracteres; teto {P.TETO_TURNOS}/{P.TETO_CARACTERES})"
    return None


def decisao_longa(motivo: str) -> dict:
    """Decisão sem chamada ao Jev para conversa acima do teto (achado 6): pedir, contada à parte (`longa`)."""
    return {"acao": "pedir_esclarecimento", "sugestao": None, "motivo": motivo, "referente": None,
            "referente_decidido": None, "conf": None, "probs": {}, "usa_outro": None,
            "nouls": {q: None for q in P.NOULS}, "longa": True}


def pedido(caso: dict) -> tuple[dict, dict]:
    """(state, questions) de uma conversa: a Choice é montada com os candidatos desta conversa.
    Candidatos inválidos = erro aqui, antes de qualquer chamada."""
    state = state_de(caso)
    validar_candidatos(state["candidates"])
    return state, P.perguntas(state["candidates"])


def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    """Noul em três faixas: True / False / None (= dúvida)."""
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def validar(resposta: dict, ids: list[str]) -> dict:
    """Resposta da API → números validados pela infra comum (achado 3): Choice com `choice` entre as opções,
    distribuição completa somando ~1 e confiança real em [0,1]; cada Noul número real em [0,1] (não bool, não
    string); discriminador `type`, quando vem, tem de bater. Qualquer falha = erro operacional, nunca `manter`."""
    answers = resposta.get("answers") or {}
    for q, tipo in (("referent", "choice"), *((n, "noul") for n in P.NOULS)):
        a = answers.get(q)
        if not isinstance(a, dict) or a.get("type", tipo) != tipo:
            raise ValueError(f"resposta sem `{q}` do tipo {tipo}: {a!r}")
    ref = CG.choice(resposta, "referent", {*ids, P.NEI})
    nouls = {q: CG.noul(resposta, q) for q in P.NOULS}
    return {"escolha": ref["choice"], "conf": ref["confidence"], "probs": ref["probabilities"], **nouls}


def decidir(resposta: dict, candidatos: list[dict]) -> dict:
    """Resposta JSON da API + candidatos → decisão (guarda os números brutos para medir e re-limiar sem chamar de novo).

    `referente` = vencedor da Choice (válvula → None), sem portão: é o que se compara ao gabarito.
    `referente_decidido` = o que a política aceita (piso de confiança + Noul de ambiguidade); None → pedir.
    `usa_outro` = sim/não/dúvida sobre o rascunho: Noul relacional quando o referente é conhecido; Noul
    absoluto "se compromete com um" quando não é (LEIA-ME: com referente nulo, comprometer-se É o erro).
    """
    ids = [c["id"] for c in candidatos]
    v = validar(resposta, ids)
    referente = None if v["escolha"] == P.NEI else v["escolha"]
    unamb = _faixa(v["unambiguous_reference"], P.UNAMBIGUOUS_MIN, 1.0) if P.UNAMBIGUOUS_MIN is not None else None

    decidido, motivo = referente, ""
    if referente is None:
        motivo = "o Jev não identificou um candidato"
    elif v["conf"] < P.REFERENTE_CONF_MIN:
        decidido, motivo = None, f"referente incerto (confiança {v['conf']:.2f})"
    elif unamb is False:
        decidido, motivo = None, f"referência ambígua (noul {v['unambiguous_reference']:.2f})"

    if decidido is None:
        usa_outro = _faixa(v["draft_commits_to_one"], *P.FAIXA["draft_commits_to_one"])
        acao, sugestao = "pedir_esclarecimento", None
    else:
        usa_outro = _faixa(v["draft_uses_other"], *P.FAIXA["draft_uses_other"])
        if usa_outro is False:
            acao, sugestao, motivo = "manter", None, "rascunho sobre o referente"
        else:
            # dúvida também troca: regenerar com o candidato certo custa pouco; fato errado enviado custa caro
            acao, sugestao = "trocar_referente", decidido
            motivo = "rascunho usa fato de outro candidato" if usa_outro else f"dúvida sobre o rascunho ({v['draft_uses_other']:.2f})"
    return {
        "acao": acao, "sugestao": sugestao, "motivo": motivo,
        "referente": referente, "referente_decidido": decidido, "conf": v["conf"], "probs": v["probs"],
        "usa_outro": usa_outro,
        "nouls": {q: v[q] for q in P.NOULS},
    }


# ---------------------------------------------------------------------------------------- baseline de código
def _tokens(texto: str) -> set[str]:
    """Palavras ≥ 4 letras (sem acento, minúsculas) fora da lista genérica + números com ≥ 2 dígitos."""
    plano = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    palavras = {w for w in re.findall(r"[a-z]{4,}", plano) if w not in P.PALAVRAS_GENERICAS}
    numeros = {n.rstrip(".,") for n in re.findall(r"\d[\d.,]*", plano) if len(re.sub(r"\D", "", n)) >= P.MIN_DIGITOS_NUMERO}
    return palavras | numeros


def assinaturas(candidatos: list[dict]) -> dict[str, set[str]]:
    """Tokens do resumo que só um candidato tem (bairro, preço, metragem). O que dois têm não identifica.
    @example assinaturas([{"id": "a", "summary": "Apto 2 quartos em Moema, R$ 900 mil"},
                          {"id": "b", "summary": "Apto 2 quartos em Pinheiros, R$ 870 mil"}])
             → {"a": {"moema", "900"}, "b": {"pinheiros", "870"}}
    """
    toks = {c["id"]: _tokens(c["summary"]) for c in candidatos}
    return {i: {t for t in ts if all(t not in o for j, o in toks.items() if j != i)} for i, ts in toks.items()}


def ultimo_citado(state: dict) -> str | None:
    """Baseline: o candidato cuja assinatura aparece na mensagem mais recente que cita exatamente um deles.
    Varre a conversa do fim para o início (cliente e agente); mensagem que cita dois não decide; nenhuma → None."""
    assin = assinaturas(state["candidates"])
    for m in reversed(state["conversation"]):
        toks = _tokens(m["text"])
        citados = [i for i, a in assin.items() if toks & a]
        if len(citados) == 1:
            return citados[0]
    return None


def baseline(state: dict) -> dict:
    """Só regra de código, sem Jev: referente = último citado; rascunho usa outro = assinatura de outro candidato
    no rascunho. Ausência de referente → pedir."""
    ref = ultimo_citado(state)
    assin = assinaturas(state["candidates"])
    no_rascunho = {i for i, a in assin.items() if _tokens(state["draft"]) & a}
    if ref is None:
        return {"acao": "pedir_esclarecimento", "referente": None, "usa_outro": bool(no_rascunho), "sugestao": None}
    usa = bool(no_rascunho - {ref})
    return {"acao": "trocar_referente" if usa else "manter", "referente": ref, "usa_outro": usa, "sugestao": ref if usa else None}


def conferir(jev, caso: dict) -> dict:
    """Uma conversa de ponta a ponta: candidatos validados, teto conferido, uma requisição, decisão em código."""
    state, questions = pedido(caso)
    motivo = conversa_longa(state)
    if motivo:
        return decisao_longa(motivo)
    return decidir(jev.perguntar(state, questions), state["candidates"])
