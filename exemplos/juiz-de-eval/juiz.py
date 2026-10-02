"""Juiz de eval: critérios FORMAIS por regra de código, SEMÂNTICOS por um Noul cada; composição em código.

Para cada resposta avaliada:
  formal    → `avaliar_formal` lê o texto do critério (regras do dados/LEIA-ME.md) e devolve True/False.
              O Jev nunca vê um critério formal.
  semantico → um Noul por critério (`perguntas.noul`), em um dos dois desenhos de state; a probabilidade
              vira atende / nao_atende / revisa pela FAIXA de `perguntas.py`.
Veredito da resposta: aprovada (todos atendem) · reprovada (algum nao_atende) · revisa (o resto).
Ausência de resposta do Jev (ID faltando, valor fora de [0,1], bool ou string) é ERRO, não "não atende"
(AGENTS §10). Critério formal cujo texto a gramática não reconhece INTEIRO também é erro (ValueError):
nunca vira `atende` — revisão do Codex 2026-10-01, achado 3.
"""
from __future__ import annotations

import re
import unicodedata

import congelamento as C  # _comum: validação de probabilidade (bool/string/não finito = erro)
import perguntas as P

# ---------------------------------------------------------------- critérios formais (código)
# Frase = trecho terminado por . ! ? ou pelo fim do texto. Antes de contar: URL vira palavra, ponto
# entre dígitos (milhar) some, abreviação perde o ponto, reticências viram um ponto só. "?!" ou "..."
# contam uma vez porque o split é por SEQUÊNCIA de terminadores.
_ABREV = re.compile(r"\b(Av|Dr|Dra|Sr|Sra|Srta|Prof|Obs|Tel|Apto|Ap|Cond|Ref|Ex|etc|km|cj)\.", re.I)
_HORARIO = re.compile(r"\d{1,2}h(\d{2})?\b|\d{1,2}:\d{2}")
# URL até antes da pontuação que a FECHA (". ", "!", ")" + espaço/fim): "Veja https://x.com. Ligue." tem
# 2 frases, não 1 — o `\S+` guloso engolia o ponto final (Codex 2026-10-01, achado 4).
_URL = re.compile(r"(?:https?://|www\.)\S+?(?=[.!?,;:)\]'\"]*(?:\s|$))")


def contar_frases(texto: str) -> int:
    t = _URL.sub(" url ", texto)
    t = re.sub(r"(?<=\d)\.(?=\d)", "", t)
    t = _ABREV.sub(r"\1", t)
    t = t.replace("…", ".")
    return sum(1 for parte in re.split(r"[.!?]+", t) if parte.strip())


def tem_emoji(texto: str) -> bool:
    """Fora do BMP (> U+FFFF) ou nos blocos de símbolos/dingbats (U+2600–27BF, U+2B00–2BFF)."""
    return any(ord(c) > 0xFFFF or 0x2600 <= ord(c) <= 0x27BF or 0x2B00 <= ord(c) <= 0x2BFF for c in texto)


# Gramática COMPLETA do texto de um critério formal (as 8 regras do dados/LEIA-ME.md), ancorada no texto
# inteiro: "Não contém um link" não casa com "contém um link" — a polaridade é lida à parte e inverte a
# regra. Número com dígitos ou por extenso (1–10); singular e plural ("1 frase", "2 frases"); parêntese
# explicativo opcional ("(10h ou 10:00)", "(http)"). Texto que sobra = critério NÃO reconhecido → erro.
_NUMERO = r"(\d+|uma?|dois|duas|tr[eê]s|quatro|cinco|seis|sete|oito|nove|dez)"
_POR_EXTENSO = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "três": 3, "quatro": 4, "cinco": 5,
                "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10}
_PARENTESE = r"(?:\s*\([^()]*\))?"
_REGRAS = [
    ("frases", rf"tem no m[aá]ximo {_NUMERO} frases?", lambda m, t: contar_frases(t) <= _n(m.group(1))),
    ("caracteres", rf"tem no m[aá]ximo {_NUMERO} caracteres?", lambda m, t: len(t) <= _n(m.group(1))),
    ("palavra", r"cont[eé]m a palavra\s+['\"“‘](.+?)['\"”’]", lambda m, t: m.group(1).casefold() in t.casefold()),
    ("horario", rf"cont[eé]m um hor[aá]rio{_PARENTESE}", lambda m, t: bool(_HORARIO.search(t))),
    ("link", rf"cont[eé]m um link{_PARENTESE}", lambda m, t: "http" in t),
    ("reais", r"cont[eé]m (?:um valor em reais no formato )?R\$", lambda m, t: "R$" in t),
    ("emoji", r"cont[eé]m emoji", lambda m, t: tem_emoji(t)),
    ("pergunta_final", r"termina com uma pergunta", lambda m, t: t.rstrip().endswith("?")),
]


def _n(token: str) -> int:
    return int(token) if token.isdigit() else _POR_EXTENSO[token.casefold()]


def avaliar_formal(criterio: str, resposta: str) -> tuple[str, bool]:
    """(nome da regra, veredito). Lê a polaridade ("Não …" inverte) e exige que a regra cubra o texto
    INTEIRO do critério (fora espaços e ponto final). Não reconhecido → ValueError: é bug a corrigir ou
    rubrica fora da gramática — nunca `atende` nem `nao_atende`."""
    texto = criterio.strip().rstrip(".").strip()
    negado = re.match(r"n[aã]o\s+", texto, re.I)
    corpo = texto[negado.end():] if negado else texto
    for nome, padrao, regra in _REGRAS:
        m = re.fullmatch(padrao, corpo, re.I)
        if m:
            ok = bool(regra(m, resposta))
            return nome, (not ok) if negado else ok
    raise ValueError(f"critério formal não reconhecido pela gramática: {criterio!r}")


# ---------------------------------------------------------------- semânticos: state e perguntas
# "Não inventa …" / "Não afirma … sem base no contexto" só é julgável com a ficha (`Contexto:` na
# pergunta). Sem ela, o gabarito é nulo por regra de rotulagem (LEIA-ME) e o Jev não tem com que
# comparar — não se pergunta o que o state não diz: o CÓDIGO manda para revisão e não gasta a chamada.
_PRECISA_CONTEXTO = re.compile(r"^n[aã]o (inventa|afirma)", re.I)


def sem_contexto(caso: dict, criterio: str) -> bool:
    return bool(_PRECISA_CONTEXTO.search(criterio)) and "Contexto:" not in caso["pergunta"]


def semanticos(caso: dict) -> list[dict]:
    """Critérios semânticos que VÃO ao Jev (os indecidíveis por falta de contexto ficam no código)."""
    return [r for r in caso["rubrica"] if r["tipo"] == "semantico" and not sem_contexto(caso, r["criterio"])]


def pedidos(caso: dict, desenho: str) -> list[tuple[dict, dict, list[str]]]:
    """[(state, questions, ids dos critérios na ordem das perguntas)] — 1 por critério ou 1 por resposta."""
    sem = semanticos(caso)
    if not sem:
        return []
    if desenho == "um_por_requisicao":
        return [({"question": caso["pergunta"], "answer": caso["resposta"], "criterion": r["criterio"]},
                 {"atende": P.noul("`criterion`")}, [r["id"]]) for r in sem]
    if desenho == "agrupado":
        state = {"question": caso["pergunta"], "answer": caso["resposta"], "criteria": [r["criterio"] for r in sem]}
        return [(state, {r["id"]: P.noul(f"`criteria[{i}]`") for i, r in enumerate(sem)}, [r["id"] for r in sem])]
    raise ValueError(f"desenho desconhecido: {desenho}")


def faixa(valor: float, limiares: tuple[float, float] = None) -> str:
    nao, sim = limiares or P.FAIXA
    if valor >= sim:
        return "atende"
    if valor <= nao:
        return "nao_atende"
    return "revisa"


# ---------------------------------------------------------------- composição
def compor(caso: dict, respostas_jev: list[dict], desenho: str) -> dict:
    """Respostas da API (na ordem de `pedidos`) → veredito por critério e da resposta."""
    nouls: dict[str, float] = {}
    for (_, questions, ids), resp in zip(pedidos(caso, desenho), respostas_jev):
        for q, cid in zip(questions, ids):
            nouls[cid] = C.noul(resp, q)  # bool, string, NaN, fora de [0,1] ou ID faltando = ValueError
    criterios = []
    for r in caso["rubrica"]:
        if r["tipo"] == "formal":
            try:
                regra, ok = avaliar_formal(r["criterio"], caso["resposta"])
                veredito = "atende" if ok else "nao_atende"
            except ValueError:
                # critério fora da gramática: erro OPERACIONAL, contado à parte no relatório
                regra, veredito = "nao_reconhecido", "erro"
            criterios.append({"id": r["id"], "tipo": "formal", "regra": regra, "noul": None, "veredito": veredito})
        elif sem_contexto(caso, r["criterio"]):
            criterios.append({"id": r["id"], "tipo": "semantico", "regra": "sem_contexto", "noul": None, "veredito": "revisa"})
        else:
            v = nouls[r["id"]]
            criterios.append({"id": r["id"], "tipo": "semantico", "regra": None, "noul": v, "veredito": faixa(v)})
    return {"id": caso["id"], "criterios": criterios, "resposta": veredito_resposta(criterios),
            "modelo": respostas_jev[0]["model"] if respostas_jev else None}


def veredito_resposta(criterios: list[dict]) -> str:
    vs = {c["veredito"] for c in criterios}
    if "erro" in vs:
        return "erro"
    if "nao_atende" in vs:
        return "reprovada"
    if "revisa" in vs:
        return "revisa"
    return "aprovada"


def julgar(jev, caso: dict, desenho: str = P.DESENHO_PADRAO) -> dict:
    """Uma resposta de ponta a ponta: formais em código, semânticos no Jev, composição em código."""
    return compor(caso, [jev.perguntar(s, q) for s, q, _ in pedidos(caso, desenho)], desenho)


# ---------------------------------------------------------------- baseline de código (semânticos)
def _tokens(texto: str) -> list[str]:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z0-9]+", sem_acento.casefold())


def baseline(criterio: str, resposta: str) -> bool:
    """Palavras-chave do critério presentes na resposta (prefixo de 5 letras); critério negado inverte."""
    negado = _tokens(criterio)[:1] == ["nao"]
    chaves = {w[:5] for w in _tokens(criterio) if len(w) >= 3 and w not in P.BASELINE_STOP and w != "nao"}
    if not chaves:
        return not negado
    presentes = {w[:5] for w in _tokens(resposta)}
    menciona = len(chaves & presentes) / len(chaves) >= P.BASELINE_FRACAO
    return (not menciona) if negado else menciona
