"""Lint semântico de diff: regras MECÂNICAS por regex, SEMÂNTICAS por um Noul cada; composição e comentário de CI
em código.

Para cada diff com suas regras:
  mecanica  → `mecanica(chave, diff)` aplica a regex do LEIA-ME às linhas adicionadas; devolve (viola, trechos).
              O Jev nunca vê uma regra mecânica. Regra mecânica sem regex conhecida é ValueError (nunca `ok`).
  semantica → state {"diff", "rules": [textos]} com SÓ as semânticas; um Noul de violação por regra (+ um de
              aplicabilidade, mesma requisição); a probabilidade vira viola / revisa / ok / nao_se_aplica pela
              FAIXA e pelo LIMIAR_APLICA de `perguntas.py`.
Comentário de CI: só IDs, vereditos, probabilidades e trechos do próprio diff — nada gerado.
Ausência de resposta do Jev (ID faltando, bool, string, NaN, fora de [0,1]) é ERRO, não "ok" (AGENTS §10).

Segredo (revisão do Codex, 2026-10-01, dois achados de gravidade 1):
  1. A regex de SEG roda ANTES de qualquer chamada, sobre TODAS as linhas do diff (adicionada, removida, contexto):
     o state que vai ao Jev é o diff com cada trecho casado trocado por `***` (`mascarar`). O detector não pode
     transmitir ao modelo justamente o segredo que ele existe para barrar. Isso muda o state (e a chave do cache)
     só dos diffs com segredo — contado na rodada 3 do README.
  2. A máscara vale para TODO trecho que sai na composição (`compor`), não só para o da regra SEG: uma linha
     `console.log(token)` com segredo literal saía inteira pelo trecho de LOG. Bateria em `testa_mascara.py`.
Teto (gravidade 2): diff acima de TETO_LINHAS/TETO_CARACTERES não vai ao Jev nem é truncado em silêncio — as
regras semânticas saem `revisa` com motivo "diff grande" e o relatório conta esses diffs à parte.
"""
from __future__ import annotations

import congelamento as C  # _comum: validação estrita de probabilidade
import perguntas as P


# ---------------------------------------------------------------- leitura do diff
def linhas_adicionadas(diff: str) -> list[dict]:
    """[{arquivo, texto, idx, apos_adicionada}] — uma por linha `+` (sem `+++`); `idx` é a posição no diff e
    `apos_adicionada` diz se a linha do diff imediatamente anterior também era `+` (regra do DROP)."""
    saida, arquivo, anterior_add = [], "", False
    for idx, linha in enumerate(diff.splitlines()):
        if linha.startswith("+++ "):
            arquivo = linha[4:].strip()
            arquivo = arquivo[2:] if arquivo.startswith("b/") else arquivo
            anterior_add = False
        elif linha.startswith("+"):
            saida.append({"arquivo": arquivo, "texto": linha[1:], "idx": idx, "apos_adicionada": anterior_add})
            anterior_add = True
        else:
            anterior_add = False
    return saida


def mascarar(texto: str) -> str:
    """Troca por `***` todo trecho que a regex de SEG casa, linha a linha (a alternativa `nome = "…"` da regex
    aceita quebra de linha dentro das aspas; por linha ela não atravessa o diff). Idempotente: `***` não casa."""
    return "\n".join(P.SEG_RE.sub("***", linha) for linha in texto.split("\n"))


def diff_grande(diff: str) -> bool:
    """Acima do teto declarado em perguntas.py: não vai ao Jev (e não é truncado em silêncio)."""
    return len(diff.splitlines()) > P.TETO_LINHAS or len(diff) > P.TETO_CARACTERES


# ---------------------------------------------------------------- regras mecânicas (código)
def mecanica(chave: str, diff: str) -> tuple[bool, list[str]]:
    """(viola, trechos das linhas que violam, ainda brutos — `compor` mascara todo trecho na saída).
    A regex é a do dados/LEIA-ME.md, literal."""
    adds = linhas_adicionadas(diff)
    ruins: list[str] = []
    if chave == "SEG":
        ruins = [a["texto"] for a in adds if P.SEG_RE.search(a["texto"])]
    elif chave == "LOG":
        ruins = [a["texto"] for a in adds
                 if P.LOG_RE.search(a["texto"]) and not P.LOG_ARQUIVO_DE_TESTE_RE.search(a["arquivo"])]
    elif chave == "DROP":
        for i, a in enumerate(adds):
            if not P.DROP_RE.search(a["texto"]):
                continue
            na_linha = P.DROP_MARCADOR_RE.search(a["texto"])
            # a linha adicionada imediatamente anterior: adjacente no diff (linha em branco `+` quebra a sequência,
            # porque ela é a anterior e não tem o marcador)
            na_anterior = a["apos_adicionada"] and i > 0 and P.DROP_MARCADOR_RE.search(adds[i - 1]["texto"])
            if not (na_linha or na_anterior):
                ruins.append(a["texto"])
    elif chave == "TODO":
        for a in adds:
            for m in P.TODO_RE.finditer(a["texto"]):
                if not P.TODO_OK_RE.match(a["texto"], m.start()):
                    ruins.append(a["texto"])
                    break
    else:
        raise ValueError(f"regra mecânica sem regex conhecida: {chave!r}")
    return bool(ruins), [r.strip() for r in ruins]


# ---------------------------------------------------------------- semânticas: state e perguntas
def semanticas(caso: dict) -> list[dict]:
    return [r for r in caso["regras"] if r["tipo"] == "semantica"]


def pedido(caso: dict) -> tuple[dict, dict] | None:
    """(state, questions) — uma requisição por diff com todas as regras semânticas; None se não há nenhuma ou se
    o diff passa do teto (`compor` devolve `revisa`, motivo "diff grande").
    Os dois Nouls (violação e aplicabilidade) vão juntos: mesmo state, zero requisição extra.
    O diff entra no state JÁ MASCARADO: a regra mecânica de segredo roda antes de qualquer chamada externa."""
    sem = semanticas(caso)
    if not sem or diff_grande(caso["diff"]):
        return None
    state = {"diff": mascarar(caso["diff"]), "rules": [r["texto"] for r in sem]}
    questions = {}
    for i, r in enumerate(sem):
        questions[f"{r['id']}_viola"] = P.noul_viola(i)
        questions[f"{r['id']}_aplica"] = P.noul_aplica(i)
    return state, questions


def faixa(viola: float, aplica: float | None, gatilho: bool | None, desenho: str, limiares=None, limiar_aplica=None) -> str:
    """viola / revisa / ok / nao_se_aplica. Quem decide "não se aplica" depende do desenho: ninguém (`valvula`),
    o Noul auxiliar (`aplicabilidade`) ou a regex de gatilho (`gatilho`; regra sem regex conhecida = aplicável)."""
    nao, sim = limiares or P.FAIXA
    if desenho == "aplicabilidade" and aplica is not None and aplica < (limiar_aplica if limiar_aplica is not None else P.LIMIAR_APLICA):
        return "nao_se_aplica"
    if desenho == "gatilho" and gatilho is False:
        return "nao_se_aplica"
    if viola >= sim:
        return "viola"
    if viola <= nao:
        return "ok"
    return "revisa"


# ---------------------------------------------------------------- composição
def compor(caso: dict, resposta: dict | None, desenho: str = P.DESENHO_PADRAO) -> dict:
    """Resposta da API → veredito por regra + comentário de CI. Mecânicas vêm do código, sempre.
    Sem resposta: diff acima do teto → semânticas `revisa` (motivo "diff grande"); qualquer outro caso é erro."""
    regras = []
    grande = diff_grande(caso["diff"])
    for r in caso["regras"]:
        chave = P.chave_da_regra(r["texto"])
        if r["tipo"] == "mecanica":
            if chave is None:
                raise ValueError(f"regra mecânica desconhecida em {caso['id']}: {r['texto'][:40]!r}")
            viola, trechos = mecanica(chave, caso["diff"])
            regras.append({"id": r["id"], "chave": chave, "tipo": "mecanica", "viola": None, "aplica": None,
                           "veredito": "viola" if viola else "ok", "trechos": trechos})
        else:
            if grande:
                # fora da faixa medida (10–60 linhas): humano olha; nada foi enviado nem cortado
                regras.append({"id": r["id"], "chave": chave or "?", "tipo": "semantica", "viola": None, "aplica": None,
                               "gatilho": aplica_por_regex(chave, caso["diff"]), "veredito": "revisa",
                               "motivo": P.MOTIVO_DIFF_GRANDE, "trechos": []})
                continue
            if resposta is None:
                raise ValueError(f"regra semântica sem resposta do Jev em {caso['id']}")
            v = C.noul(resposta, f"{r['id']}_viola")   # bool, string, NaN, fora de [0,1] ou ID faltando = erro
            a = C.noul(resposta, f"{r['id']}_aplica")
            g = aplica_por_regex(chave, caso["diff"])
            regras.append({"id": r["id"], "chave": chave or "?", "tipo": "semantica", "viola": v, "aplica": a, "gatilho": g,
                           "veredito": faixa(v, a, g, desenho), "trechos": gatilhos(chave, caso["diff"])})
    # Saída comum: TODO trecho (SEG, LOG, TODO, DROP, gatilhos semânticos) passa pela máscara de segredo antes de
    # virar comentário — bot que repete o segredo no PR espalha o vazamento, venha ele pela regra que vier.
    for r in regras:
        r["trechos"] = [mascarar(t) for t in r["trechos"]]
    return {"id": caso["id"], "regras": regras, "comentario": comentario_ci(regras), "diff_grande": grande,
            "modelo": resposta["model"] if resposta else None}


def comentario_ci(regras: list[dict]) -> str:
    """Texto do comentário de CI: só IDs, vereditos, probabilidades e trechos do diff (já mascarados por
    `compor`). Sem geração."""
    linhas = []
    for r in regras:
        if r["veredito"] in ("ok", "nao_se_aplica"):
            continue
        prob = "" if r["viola"] is None else f" (p={r['viola']:.2f})"
        prob += f" ({r['motivo']})" if r.get("motivo") else ""
        linhas.append(f"- {r['id']} {r['chave']}: {r['veredito']}{prob}")
        linhas.extend(f"    `{t}`" for t in r["trechos"][:3])
    return "\n".join(linhas) if linhas else "nenhuma regra violada ou em revisão"


def julgar(jev, caso: dict, desenho: str = P.DESENHO_PADRAO) -> dict:
    """Um diff de ponta a ponta: mecânicas em código, semânticas no Jev (1 requisição), composição em código.
    `pedido` mascara o segredo e aplica o teto ANTES da chamada; diff grande não chama nada."""
    p = pedido(caso)
    return compor(caso, jev.perguntar(*p) if p else None, desenho)


# ---------------------------------------------------------------- baseline de código (semânticas)
def gatilhos(chave: str | None, diff: str) -> list[str]:
    """Linhas adicionadas que disparam o gatilho da regra (para o comentário de CI e para o baseline)."""
    adds, disparadas = _disparadas(chave, diff)
    return [adds[i]["texto"].strip() for i in disparadas]


def _disparadas(chave: str | None, diff: str) -> tuple[list[dict], list[int]]:
    """(linhas adicionadas consideradas, índices das que disparam o gatilho da regra) — a parte MECÂNICA de uma
    regra semântica: "há função nova exportada / supressão / rota nova lendo entrada / SQL cru em código?"."""
    b = P.BASELINE.get(chave or "")
    adds = linhas_adicionadas(diff)
    if not b:
        return adds, []
    if chave == "SQL":
        adds = [a for a in adds if not P.MIGRATION_RE.search(a["arquivo"])]
    disparadas = [i for i, a in enumerate(adds) if b["gatilho"].search(a["texto"])]
    if chave == "JSDOC":
        # `export default nome` de uma const arrow definida no diff conta como função nova exportada (LEIA-ME)
        for i, a in enumerate(adds):
            m = P.JSDOC_DEFAULT_RE.match(a["texto"])
            if m and any(P.JSDOC_ARROW_RE(m.group(1)).match(x["texto"]) for x in adds):
                disparadas.append(i)
    if chave == "VALID" and not any(P.VALID_LE_ENTRADA_RE.search(a["texto"]) for a in adds):
        disparadas = []  # rota nova que não lê entrada: a regra não toca
    return adds, sorted(set(disparadas))


def aplica_por_regex(chave: str | None, diff: str) -> bool | None:
    """True/False = a regex de gatilho achou/não achou o assunto da regra; None = regra sem regex (desconhecida)."""
    if chave not in P.BASELINE:
        return None
    return bool(_disparadas(chave, diff)[1])


def baseline(chave: str | None, diff: str) -> bool | None:
    """True = viola, False = ok, None = não se aplica (sem gatilho). Regex + palavra-chave, 20 minutos de código."""
    b = P.BASELINE.get(chave or "")
    if not b:
        return None
    adds, disparadas = _disparadas(chave, diff)
    if not disparadas:
        return None
    texto_add = "\n".join(a["texto"] for a in adds)
    if chave == "JSDOC":
        return not b["satisfaz"].search(texto_add)
    if chave == "VALID":
        return not (b["satisfaz"].search(texto_add) and P.VALID_RESULT_RE.search(texto_add))
    if chave == "DESVIO":
        # comentário na própria linha (após `--` ou um segundo `#`) ou linha `+` anterior é comentário
        for i in disparadas:
            t = adds[i]["texto"]
            propria = " -- " in t or t.count("#") >= 2 or ("//" in t and "eslint" not in t.split("//", 1)[1][:16])
            anterior = i > 0 and adds[i]["apos_adicionada"] and P.COMENTARIO_RE.match(adds[i - 1]["texto"])
            if not (propria or anterior):
                return True
        return False
    if chave == "SQL":
        for i in disparadas:
            anterior = i > 0 and adds[i]["apos_adicionada"] and P.COMENTARIO_RE.match(adds[i - 1]["texto"])
            if not anterior:
                return True
        return False
    return None
