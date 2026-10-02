"""Próxima pergunta: o Jev julga o que já foi respondido; o código monta as candidatas e devolve UM ID do catálogo.

Fluxo por conversa:
  1ª requisição  Nouls `answered.<item>` (um por item do catálogo), `withdrawn.<campo>` (só campos que o CRM tem),
                 sinais das regras de sentido e a Choice única do catálogo inteiro (comparação).
  código         respondidas (CRM por regra exata; conversa pelo Noul), sem sentido (aluguel → financiamento;
                 investidor → pet), candidatas (com essencial faltando, secundária não entra).
  2ª requisição  Choice `next` só entre as candidatas + `no_question_needed` — a resposta da 1ª decide as OPÇÕES
                 da 2ª (único motivo legítimo para uma 2ª chamada). Só candidata única (a válvula) = sem chamada.
                 Na variante principal (`hibrida`) ela só acontece com as essenciais completas: com essencial
                 faltando o código pergunta a primeira da ordem fixa (a tabela do LEIA-ME já decide).
`julgar` devolve também `bloqueadas` — a lista "não pergunte isto" (respondida, CRM, sem sentido) — que serve ao
agente mesmo quando ele redige a pergunta sozinho.
A saída é o ID da pergunta-modelo; o TEXTO vem do catálogo, pelo código — o Jev não gera nada. Nada é enviado
daqui. Ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO (exceção), nunca "nenhuma pergunta".
Entrada inválida (conversa vazia, última mensagem que não é do cliente, item de catálogo sem pergunta escrita em
`perguntas.py`) = erro ANTES da chamada. Conversa acima do teto não vai ao Jev: sem sugestão, contada à parte.

Candidato a etapa de qualificação da Luci SDR: roda antes de o agente redigir o próximo turno.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

_DE = {"cliente": "customer", "agente": "agent"}
VARIANTES_JEV = ["unica", "mascarada", "jev", "codigo", "hibrida"]


# ---------------------------------------------------------------------------------------- entrada
def validar_entrada(conversa: list[dict], campos: dict, catalogo: list[dict]) -> list[str]:
    """Confere a entrada antes de qualquer chamada e devolve os IDs do catálogo, na ordem.
    Item de catálogo desconhecido é erro: não há pergunta `answered` escrita para ele (pergunta nova = revisão humana)."""
    if not isinstance(conversa, list) or not conversa:
        raise ValueError("conversa vazia")
    for m in conversa:
        if m.get("de") not in _DE or not isinstance(m.get("texto"), str) or not m["texto"].strip():
            raise ValueError(f"mensagem inválida: {m!r}")
    if conversa[-1]["de"] != "cliente":
        raise ValueError("a última mensagem tem de ser do cliente")
    if not isinstance(campos, dict) or set(campos) - set(P.CAMPOS):
        raise ValueError(f"campos conhecidos fora do catálogo: {sorted(set(campos) - set(P.CAMPOS))}")
    ids = [i.get("id") for i in catalogo]
    if len(set(ids)) != len(ids) or P.NQN not in ids or set(ids) - set(P.EN):
        raise ValueError(f"catálogo inválido (repetido, sem `{P.NQN}` ou com item sem pergunta escrita): {ids!r}")
    if any(not isinstance(i.get("pergunta"), str) or not i["pergunta"].strip() for i in catalogo):
        raise ValueError("item de catálogo sem texto")
    return ids


def state_de(conversa: list[dict], campos: dict) -> dict:
    """Conversa e campos do CRM (pt) → state enxuto com os nomes que as perguntas citam entre crases.
    @example state_de([{"de": "cliente", "texto": "oi"}], {"quartos": 2})
             → {"conversation": [{"from": "customer", "text": "oi"}], "known_fields": {"bedrooms": 2}}
    """
    return {"conversation": [{"from": _DE[m["de"]], "text": m["texto"]} for m in conversa],
            "known_fields": {P.EN[k]: v for k, v in campos.items()}}


def conversa_longa(state: dict) -> str | None:
    """Motivo se a conversa passa do teto (turnos ou caracteres); None dentro da faixa validada."""
    turnos, chars = len(state["conversation"]), sum(len(m["text"]) for m in state["conversation"])
    if turnos > P.TETO_TURNOS or chars > P.TETO_CARACTERES:
        return f"conversa longa ({turnos} turnos, {chars} caracteres; teto {P.TETO_TURNOS}/{P.TETO_CARACTERES})"
    return None


def perguntas_etapa1(ids: list[str], campos: dict) -> dict:
    """1ª requisição: um `answered` por item do catálogo (menos a válvula), um `withdrawn` por campo que o CRM tem,
    os sinais das regras de sentido e a Choice única (comparação). Mesmo state, perguntas isoladas."""
    itens = [i for i in ids if i != P.NQN]
    return {**{f"answered.{P.EN[i]}": P.RESPONDIDA[i] for i in itens},
            **{f"withdrawn.{P.EN[c]}": P.retirado(c) for c in P.CAMPOS if c in campos and c in ids},
            **P.SINAIS,
            "single_choice": P.choice_unica(ids)}


# ---------------------------------------------------------------------------------------- leitura da 1ª resposta
def _conferir_tipos(resposta: dict, questions: dict) -> None:
    """Todo ID esperado presente e com o discriminador `type` batendo (quando vem)."""
    answers = resposta.get("answers") or {}
    for q, p in questions.items():
        a = answers.get(q)
        if not isinstance(a, dict) or a.get("type", p["type"]) != p["type"]:
            raise ValueError(f"resposta sem `{q}` do tipo {p['type']}: {a!r}")


def sinais(resposta: dict, ids: list[str], campos: dict) -> dict:
    """1ª resposta validada → números + o que o CÓDIGO deriva deles: respondidas, sem sentido, candidatas.

    `bloqueadas` = {item: motivo} — o que NÃO pode ser perguntado (é a previsão que se compara com `proibidas`):
      campo do CRM não retirado (regra exata); `answered` ≥ limiar; financiamento em aluguel; pet de investidor.
    `candidatas` = o que sobra, pela tabela do LEIA-ME: com essencial faltando só as essenciais (regras 1–3);
      senão as secundárias; `visita` só com imóvel específico na conversa; a válvula sempre por último.
    """
    questions = perguntas_etapa1(ids, campos)
    _conferir_tipos(resposta, questions)
    itens = [i for i in ids if i != P.NQN]
    L = P.LIMIAR
    resp = {i: CG.noul(resposta, f"answered.{P.EN[i]}") for i in itens}
    ret = {c: CG.noul(resposta, f"withdrawn.{P.EN[c]}") for c in P.CAMPOS if c in campos and c in ids}
    sin = {q: CG.noul(resposta, q) for q in P.SINAIS}
    unica = CG.choice(resposta, "single_choice", {P.EN[i] for i in ids})

    bloqueadas = {}
    for i in itens:
        if i in ret:  # o CRM tem o campo: respondido por regra de código; só a retirada sem valor novo reabre
            if ret[i] < L["retirado"]:
                bloqueadas[i] = "CRM"
        elif resp[i] >= L["respondida"]:
            bloqueadas[i] = "respondida"
    if "financiamento" in itens and sin["rental"] >= L["aluguel"]:
        bloqueadas.setdefault("financiamento", "sem sentido (aluguel)")
    if "pet" in itens and sin["investor_not_living"] >= L["investidor"]:
        bloqueadas.setdefault("pet", "sem sentido (investidor)")

    livres = [i for i in itens if i not in bloqueadas]
    essenciais = [i for i in P.ESSENCIAIS if i in livres]
    candidatas = essenciais or [i for i in P.SECUNDARIAS if i in livres]
    especifico = sin["specific_property"] >= L["imovel_especifico"]
    if P.VISITA in livres and especifico:
        candidatas = candidatas + [P.VISITA]
    return {"answered": resp, "withdrawn": ret, "sinais": sin, "bloqueadas": bloqueadas, "essenciais_faltando": essenciais,
            "candidatas": candidatas + [P.NQN], "especifico": especifico,
            "unica": {"escolha": P.PT[unica["choice"]], "conf": unica["confidence"],
                      "probs": {P.PT[k]: v for k, v in unica["probabilities"].items()}}}


def pedido_etapa2(s: dict) -> dict | None:
    """Perguntas da 2ª requisição, ou None quando só sobrou a válvula (nada a escolher → sem chamada)."""
    return {"next": P.choice_proxima(s["candidatas"])} if len(s["candidatas"]) > 1 else None


# ---------------------------------------------------------------------------------------- decisão
def decidir(s: dict, resposta2: dict | None) -> dict:
    """Sinais da 1ª resposta (+ 2ª resposta, se houve) → escolha de cada variante. Guarda os números brutos.

    `unica`      vencedor da Choice única, sem portão (comparação: pode cair em pergunta já respondida).
    `mascarada`  maior probabilidade da Choice única ENTRE as candidatas (sem 2ª requisição).
    `codigo`     tabela do LEIA-ME em código: 1ª essencial faltando → `visita` se imóvel específico + reação
                 positiva e visita não respondida → `no_question_needed`.
    `jev`        vencedor da Choice `next` entre as candidatas (só a válvula → válvula, sem chamada).
    `hibrida`    essencial faltando → o código (como `codigo`); essenciais completas → a Choice `next` (como `jev`).
    """
    cands = s["candidatas"]
    mascarada = max(cands, key=lambda c: s["unica"]["probs"][c])
    if s["essenciais_faltando"]:
        codigo = s["essenciais_faltando"][0]
    elif P.VISITA in cands and s["sinais"]["positive_reaction"] >= P.LIMIAR["reacao_positiva"]:
        codigo = P.VISITA
    else:
        codigo = P.NQN
    prox = None
    if len(cands) == 1:
        jev = P.NQN
    elif resposta2 is not None:
        c = CG.choice(resposta2, "next", {P.EN[i] for i in cands})
        prox = {"escolha": P.PT[c["choice"]], "conf": c["confidence"], "probs": {P.PT[k]: v for k, v in c["probabilities"].items()}}
        jev = prox["escolha"]
    else:
        jev = None  # 2ª requisição não feita (variante principal não precisa dela)
    return {**s, "next": prox, "escolhas": {"unica": s["unica"]["escolha"], "mascarada": mascarada, "jev": jev, "codigo": codigo,
                         "hibrida": codigo if s["essenciais_faltando"] else jev}}


def julgar(jev, conversa: list[dict], campos: dict, catalogo: list[dict], todas: bool = False) -> dict:
    """Uma conversa de ponta a ponta. Devolve `pergunta` (ID do catálogo ou None = sem sugestão), `texto` (a
    pergunta-modelo, copiada do catálogo) e os números. `todas=True` faz a 2ª requisição mesmo que a variante
    principal não precise (medição)."""
    ids = validar_entrada(conversa, campos, catalogo)
    campos = {k: v for k, v in campos.items() if v is not None and v != ""}  # chave sem valor não é campo conhecido (False é valor)
    state = state_de(conversa, campos)
    motivo = conversa_longa(state)
    if motivo:
        return {"pergunta": None, "texto": None, "motivo": motivo, "longa": True, "escolhas": dict.fromkeys(VARIANTES_JEV)}
    s = sinais(jev.perguntar(state, perguntas_etapa1(ids, campos)), ids, campos)
    precisa2 = P.VARIANTE_PRINCIPAL == "jev" or (P.VARIANTE_PRINCIPAL == "hibrida" and not s["essenciais_faltando"])
    q2 = pedido_etapa2(s) if (todas or precisa2) else None
    d = decidir(s, jev.perguntar(state, q2) if q2 else None)
    escolha = d["escolhas"][P.VARIANTE_PRINCIPAL]
    textos = {i["id"]: i["pergunta"] for i in catalogo}
    return {**d, "pergunta": escolha, "texto": textos[escolha], "motivo": f"variante `{P.VARIANTE_PRINCIPAL}`", "longa": False}


# ---------------------------------------------------------------------------------------- baselines de código
def baseline_lacuna(campos: dict, ids: list[str]) -> str:
    """"Primeira lacuna do formulário": o bot que só olha o CRM, na ordem do catálogo. Ignora a conversa — é a dor.
    @example baseline_lacuna({"finalidade": "compra"}, ["finalidade", "orcamento", "no_question_needed"]) → "orcamento"
    """
    return next((c for c in P.CAMPOS if c in ids and c not in campos), P.NQN)


def _plano(texto: str) -> str:
    """Minúsculas, sem acento — as expressões do baseline são escritas assim."""
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


def baseline_palavras(conversa: list[dict], campos: dict, ids: list[str]) -> str:
    """Lacuna + palavras-chave: essencial preenchida = está no CRM ou a expressão bate no texto do cliente;
    primeira essencial vazia → pergunta; todas preenchidas → `no_question_needed`. Regex não sabe que não sabe.
    @example baseline_palavras([{"de": "cliente", "texto": "quero alugar em moema"}], {}, [...]) → "orcamento"
    """
    texto = _plano(" ".join(m["texto"] for m in conversa if m["de"] == "cliente"))
    for c in P.ESSENCIAIS:
        if c in ids and c not in campos and not any(re.search(p, texto) for p in P.BASELINE[c]):
            return c
    return P.NQN
