"""Próxima pergunta: o Jev julga o que já foi respondido; o código monta as candidatas e devolve UM ID do catálogo.

Fluxo por conversa:
  código         valores em dinheiro escritos pelo cliente (`valores.mencoes`) → fato calculado no state.
  1ª requisição  Nouls `answered.<item>` (um por item do catálogo), `withdrawn.<campo>` (só campos que o CRM tem) e
                 os sinais das regras de sentido. Só isto: é a requisição que a produção paga.
  código         respondidas (CRM por regra exata; conversa pelo Noul; orçamento pela regra do LEIA-ME sobre o valor
                 lido pelo código; bairro/quartos do anúncio citado por regra), sem sentido (aluguel →
                 financiamento; investidor → pet), em revisão, candidatas (com essencial faltando, secundária não entra).
  2ª requisição  Choice `next` só entre as candidatas + `no_question_needed` — a resposta da 1ª decide as OPÇÕES
                 da 2ª (único motivo legítimo para uma 2ª chamada). Só candidata única (a válvula) = sem chamada.
                 Na variante principal (`hibrida`) ela só acontece com as essenciais completas: com essencial
                 faltando o código pergunta a primeira da ordem fixa (a tabela do LEIA-ME já decide).
  comparação     só com `todas=True` (medição): UMA requisição a mais com a Choice única do catálogo inteiro e, onde
                 a principal não chamou a `next`, a `next` também. Produção (`todas=False`) não envia nada disto.
`julgar` devolve também `bloqueadas` — o que o portão julgou respondido ou sem sentido, cada item com o motivo
(`noul` | `regra`), a evidência (`valor`), os Nouls usados e a margem até o limiar. NÃO é proibição categórica: é
julgamento com incerteza declarada; quem consome decide o que fazer com bloqueio de margem baixa. `em_revisao` são os
itens que o código não deixa perguntar NEM dar por respondidos (valor ambíguo que a regra do LEIA-ME não cobre).
A saída é o ID da pergunta-modelo; o TEXTO vem do catálogo, pelo código — o Jev não gera nada. Nada é enviado
daqui. Ausência de resposta, ID faltando, tipo errado ou número inválido — na 1ª, na 2ª ou na de comparação — é ERRO
(exceção em `julgar`; `revisar` em `julgar_seguro`), nunca "nenhuma pergunta" e nunca uma pergunta.
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
import valores as V  # noqa: E402

_DE = {"cliente": "customer", "agente": "agent"}
VARIANTES_JEV = ["unica", "mascarada", "jev", "codigo", "hibrida"]
COMPARACAO = ["unica", "mascarada", "jev"]  # só existem com `todas=True`


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


def state_de(conversa: list[dict], campos: dict, mencoes: list[dict]) -> dict:
    """Conversa, campos do CRM (pt) e valores lidos pelo código → state enxuto com os nomes que as perguntas citam.
    @example state_de([{"de": "cliente", "texto": "até 6"}], {"quartos": 2}, valores.mencoes(...))
             → {"conversation": [{"from": "customer", "text": "até 6"}], "known_fields": {"bedrooms": 2},
                "customer_amounts": [{"quote": "até 6", "value": 6, "unit": "none stated"}]}
    """
    return {"conversation": [{"from": _DE[m["de"]], "text": m["texto"]} for m in conversa],
            "known_fields": {P.EN[k]: v for k, v in campos.items()},
            "customer_amounts": V.para_state(mencoes)}


def conversa_longa(state: dict) -> str | None:
    """Motivo se a conversa passa do teto (turnos ou caracteres); None dentro da faixa validada."""
    turnos, chars = len(state["conversation"]), sum(len(m["text"]) for m in state["conversation"])
    if turnos > P.TETO_TURNOS or chars > P.TETO_CARACTERES:
        return f"conversa longa ({turnos} turnos, {chars} caracteres; teto {P.TETO_TURNOS}/{P.TETO_CARACTERES})"
    return None


def perguntas_etapa1(ids: list[str], campos: dict) -> dict:
    """1ª requisição: um `answered` por item do catálogo (menos a válvula), um `withdrawn` por campo que o CRM tem e
    os sinais das regras de sentido. Mesmo state, perguntas isoladas. A Choice única NÃO vai aqui (rodada 2): é
    comparação, e o custo medido desta requisição é o custo de produção."""
    itens = [i for i in ids if i != P.NQN]
    return {**{f"answered.{P.EN[i]}": P.RESPONDIDA[i] for i in itens},
            **{f"withdrawn.{P.EN[c]}": P.retirado(c) for c in P.CAMPOS if c in campos and c in ids},
            **P.SINAIS}


# ---------------------------------------------------------------------------------------- leitura das respostas
def _conferir_tipos(resposta: dict, questions: dict) -> None:
    """Todo ID esperado presente e com o discriminador `type` batendo (quando vem). Vale para as TRÊS requisições."""
    answers = resposta.get("answers") if isinstance(resposta, dict) else None
    if not isinstance(answers, dict):
        raise ValueError(f"resposta sem `answers`: {type(resposta).__name__}")
    for q, p in questions.items():
        a = answers.get(q)
        if not isinstance(a, dict) or a.get("type", p["type"]) != p["type"]:
            raise ValueError(f"resposta sem `{q}` do tipo {p['type']}: {a!r}")


def _choice(resposta: dict, questions: dict, id_pergunta: str, opcoes: list[str]) -> dict:
    """Choice validada em duas camadas — conferência de tipos e `congelamento.choice` (opções, distribuição,
    confiança, discriminador `type`) — e traduzida para os IDs do catálogo. Inválida = ValueError."""
    _conferir_tipos(resposta, {id_pergunta: questions[id_pergunta]})
    c = CG.choice(resposta, id_pergunta, {P.EN[i] for i in opcoes})
    return {"escolha": P.PT[c["choice"]], "conf": c["confidence"], "probs": {P.PT[k]: v for k, v in c["probabilities"].items()}}


_LIMIAR_DO_NOUL = {"answered": "respondida", "withdrawn": "retirado", "rental": "aluguel",
                   "investor_not_living": "investidor", "specific_property": "imovel_especifico"}


def _evidencia(item: str, motivo: str, detalhe: str, valor, nouls: dict) -> dict:
    """Um bloqueio (ou revisão) com o que o sustenta. `motivo` = `noul` (o Jev julgou respondido) | `regra` (regra de
    código sobre um fato: CRM, valor lido, anúncio citado, sem sentido). `margem` = menor distância ao limiar, ×2,
    entre os Nouls usados (0 = em cima do limiar; 1 = longe) — é a incerteza do bloqueio."""
    dist = [abs(v - P.LIMIAR[_LIMIAR_DO_NOUL[q.split(".")[0]]]) for q, v in nouls.items()]
    return {"id": item, "motivo": motivo, "detalhe": detalhe, "valor": valor, "nouls": nouls,
            "margem": round(min(1.0, 2 * min(dist)), 3) if dist else 1.0}


def regra_orcamento(mencoes: list[dict], declarado: float, aluguel: bool) -> dict:
    """Regra do LEIA-ME sobre `orcamento` quando o CRM não tem o campo — em CÓDIGO (rodada 2, achados 1 e 2).

    Entram três coisas: o valor que o código leu nas mensagens do cliente (`valores`), o Noul `answered.budget`
    (o cliente DECLAROU um valor como limite dele? — o preço do anúncio citado não conta) e se é aluguel (sinal).
    estado `respondida`  declarado + valor e unidade lidos pela regra → bloqueia (evidência: valor, escala, tipo)
           `confirmar`   declarado + aluguel com centenas sem unidade → candidata (o LEIA-ME aceita confirmar)
           `aberta`      sem valor · prestação em compra · valor que não é limite do cliente (Noul ≤ `declarado_nao`)
           `revisar`     o que a regra não decide: leitura ambígua; valor lido com o Noul em dúvida; Noul vê valor
                         declarado e o código não leu nenhum. Nunca vira pergunta nem bloqueio.
    """
    L, m = P.LIMIAR, V.principal(mencoes)

    def saida(estado, porque, leitura=None):
        return {"estado": estado, "porque": porque, "trecho": m["trecho"] if m else None, "leitura": leitura}

    if m is None:
        if declarado >= L["respondida"]:
            return saida("revisar", "o Jev vê um valor declarado, mas o código não leu nenhum valor do cliente")
        return saida("aberta", "o cliente não escreveu valor")
    leitura = V.ler(m, aluguel, P.PISO_PRECO)
    if leitura["estado"] in ("confirmar", "prestacao"):
        # Candidata dos dois lados do Noul (declarado → a regra deixa perguntar; não declarado → em aberto).
        return saida("confirmar" if leitura["estado"] == "confirmar" and declarado >= L["respondida"] else "aberta",
                     leitura["porque"], leitura)
    if declarado <= L["declarado_nao"]:
        return saida("aberta", "o valor que o cliente escreveu não é limite declarado por ele (preço citado ou retirado)", leitura)
    if declarado < L["respondida"]:
        return saida("revisar", "o código leu um valor do cliente e o Jev ficou em dúvida se é limite declarado", leitura)
    if leitura["estado"] == "ambiguo":
        return saida("revisar", leitura["porque"], leitura)
    return saida("respondida", leitura["porque"], leitura)


def sinais(resposta: dict, ids: list[str], campos: dict, mencoes: list[dict]) -> dict:
    """1ª resposta validada → números + o que o CÓDIGO deriva deles: bloqueadas, em revisão, candidatas.

    `bloqueadas` = lista de {id, motivo: noul|regra, detalhe, valor, nouls, margem} — o que o portão não deixa
      perguntar: campo do CRM não retirado (regra exata); orçamento pela regra do LEIA-ME sobre o valor lido pelo
      código; `answered` ≥ limiar (preferência DECLARADA); bairro e quartos do anúncio específico (regra do LEIA-ME
      sobre o sinal `specific_property`); financiamento em aluguel; pet de investidor.
    `em_revisao` = mesmos campos, para o item que não pode ser perguntado NEM dado por respondido.
    `candidatas` = o que sobra, pela tabela do LEIA-ME: com essencial faltando só as essenciais (regras 1–3);
      senão as secundárias; `visita` só com imóvel específico na conversa; a válvula sempre por último.
    `revisar` = motivo quando falta decidir uma essencial em revisão e não há outra essencial a perguntar: aí
      nenhuma variante com portão sugere pergunta (a decisão dependeria do item duvidoso).
    """
    questions = perguntas_etapa1(ids, campos)
    _conferir_tipos(resposta, questions)
    itens = [i for i in ids if i != P.NQN]
    L = P.LIMIAR
    resp = {i: CG.noul(resposta, f"answered.{P.EN[i]}") for i in itens}
    ret = {c: CG.noul(resposta, f"withdrawn.{P.EN[c]}") for c in P.CAMPOS if c in campos and c in ids}
    sin = {q: CG.noul(resposta, q) for q in P.SINAIS}
    aluguel, especifico = sin["rental"] >= L["aluguel"], sin["specific_property"] >= L["imovel_especifico"]

    bloq, revisao, orc = {}, {}, None
    for i in itens:
        if i in ret:  # o CRM tem o campo: respondido por regra de código; só a retirada sem valor novo reabre
            if ret[i] < L["retirado"]:
                bloq[i] = _evidencia(i, "regra", "CRM", campos[i], {f"withdrawn.{P.EN[i]}": ret[i]})
        elif i == "orcamento":  # magnitude e unidade são do código; o Noul só diz se o valor é do cliente
            orc = regra_orcamento(mencoes, resp[i], aluguel)
            nouls = {"answered.budget": resp[i], **({"rental": sin["rental"]} if orc["leitura"] else {})}
            if orc["estado"] == "respondida":
                bloq[i] = _evidencia(i, "regra", "orçamento declarado, lido pelo código", orc["leitura"], nouls)
            elif orc["estado"] == "revisar":
                revisao[i] = _evidencia(i, "regra", orc["porque"], orc["leitura"], nouls)
        elif resp[i] >= L["respondida"]:
            bloq[i] = _evidencia(i, "noul", "declarado pelo cliente", resp[i], {f"answered.{P.EN[i]}": resp[i]})
    if especifico:  # LEIA-ME: anúncio específico citado responde bairro e quartos — atributo do imóvel, não preferência
        for i in ("bairro", "quartos"):
            if i in itens and i not in bloq:
                bloq[i] = _evidencia(i, "regra", "anúncio específico", None, {"specific_property": sin["specific_property"]})
    if "financiamento" in itens and aluguel and "financiamento" not in bloq:
        bloq["financiamento"] = _evidencia("financiamento", "regra", "sem sentido (aluguel)", None, {"rental": sin["rental"]})
    if "pet" in itens and sin["investor_not_living"] >= L["investidor"] and "pet" not in bloq:
        bloq["pet"] = _evidencia("pet", "regra", "sem sentido (investidor)", None,
                                 {"investor_not_living": sin["investor_not_living"]})

    livres = [i for i in itens if i not in bloq and i not in revisao]
    essenciais = [i for i in P.ESSENCIAIS if i in livres]
    pendentes = [i for i in P.ESSENCIAIS if i in revisao]
    # Essencial em revisão e nenhuma outra a perguntar: escolher entre secundárias exigiria dá-la por respondida.
    revisar = None if essenciais or not pendentes else f"`{pendentes[0]}` em revisão: {revisao[pendentes[0]]['detalhe']}"
    candidatas = [] if revisar else essenciais or [i for i in P.SECUNDARIAS if i in livres]
    if P.VISITA in livres and especifico and not revisar:
        candidatas = candidatas + [P.VISITA]
    return {"answered": resp, "withdrawn": ret, "sinais": sin, "orcamento": orc,
            "bloqueadas": [bloq[i] for i in itens if i in bloq], "em_revisao": [revisao[i] for i in itens if i in revisao],
            "essenciais_faltando": essenciais, "candidatas": candidatas + [P.NQN], "especifico": especifico, "revisar": revisar}


def pedido_etapa2(s: dict) -> dict | None:
    """Perguntas da 2ª requisição, ou None quando só sobrou a válvula (nada a escolher → sem chamada) ou há revisão."""
    return {"next": P.choice_proxima(s["candidatas"])} if len(s["candidatas"]) > 1 and not s["revisar"] else None


# ---------------------------------------------------------------------------------------- decisão
def ler_next(s: dict, resposta: dict) -> dict:
    """Choice `next` validada (a resposta pode ser a da 2ª requisição ou a de comparação)."""
    return _choice(resposta, pedido_etapa2(s), "next", s["candidatas"])


def ler_unica(ids: list[str], resposta: dict) -> dict:
    """Choice única validada (só existe na requisição de comparação)."""
    return _choice(resposta, {"single_choice": P.choice_unica(ids)}, "single_choice", ids)


def decidir(s: dict, prox: dict | None, unica: dict | None) -> dict:
    """Sinais da 1ª resposta + as Choices JÁ VALIDADAS (`ler_next`, `ler_unica`; None = não pedida) → escolha de
    cada variante.

    `unica`      vencedor da Choice única, sem portão (comparação: pode cair em pergunta já respondida).
    `mascarada`  maior probabilidade da Choice única ENTRE as candidatas (sem 2ª requisição).
    `codigo`     tabela do LEIA-ME em código: 1ª essencial faltando → `visita` se imóvel específico + reação
                 positiva e visita não respondida → `no_question_needed`.
    `jev`        vencedor da Choice `next` entre as candidatas (só a válvula → válvula, sem chamada).
    `hibrida`    essencial faltando → o código (como `codigo`); essenciais completas → a Choice `next` (como `jev`).
    None = a variante não tem sugestão: comparação não pedida, `next` não chamada, ou item essencial em revisão.
    """
    cands = s["candidatas"]
    if s["revisar"]:
        gate = dict.fromkeys(["mascarada", "jev", "codigo", "hibrida"])
    else:
        if s["essenciais_faltando"]:
            codigo = s["essenciais_faltando"][0]
        elif P.VISITA in cands and s["sinais"]["positive_reaction"] >= P.LIMIAR["reacao_positiva"]:
            codigo = P.VISITA
        else:
            codigo = P.NQN
        jev = P.NQN if len(cands) == 1 else (prox["escolha"] if prox else None)
        gate = {"mascarada": max(cands, key=lambda c: unica["probs"][c]) if unica else None, "jev": jev, "codigo": codigo,
                "hibrida": codigo if s["essenciais_faltando"] else jev}
    return {**s, "unica": unica, "next": prox, "escolhas": {"unica": unica["escolha"] if unica else None, **gate}}


def julgar(jev, conversa: list[dict], campos: dict, catalogo: list[dict], todas: bool = False, _rastro: dict | None = None) -> dict:
    """Uma conversa de ponta a ponta. Devolve `pergunta` (ID do catálogo ou None = sem sugestão: teto ou revisão),
    `texto` (a pergunta-modelo, copiada do catálogo), `bloqueadas`/`em_revisao` com evidência e os números.

    `todas=False` (produção): só as requisições da variante principal — a 1ª e, quando ela precisa, a 2ª.
    `todas=True` (medição): mais UMA requisição de comparação (Choice única + a `next` que a principal não chamou).
    `etapas` diz, na ordem, que requisição foi cada chamada: "1", "2", "comparacao". Cada resposta é validada logo
    depois da sua chamada — a da 2ª etapa com a mesma conferência de tipos da 1ª e `congelamento.choice` (rodada 2,
    achado 3). Erro da chamada ou do contrato, em qualquer etapa, levanta exceção (o consumidor usa `julgar_seguro`).
    """
    rastro = _rastro if _rastro is not None else {}
    rastro.update(etapas=[], em="entrada")

    def chamar(etapa: str, questions: dict) -> dict:
        rastro["em"] = etapa
        resposta = jev.perguntar(state, questions)
        rastro["etapas"].append(etapa)
        return resposta

    ids = validar_entrada(conversa, campos, catalogo)
    campos = {k: v for k, v in campos.items() if v is not None and v != ""}  # chave sem valor não é campo conhecido (False é valor)
    mencoes = V.mencoes(conversa)
    state = state_de(conversa, campos, mencoes)
    motivo = conversa_longa(state)
    if motivo:
        return {"pergunta": None, "texto": None, "motivo": motivo, "longa": True, "revisar": False, "falha": False,
                "escolhas": dict.fromkeys(VARIANTES_JEV), "etapas": []}
    s = sinais(chamar("1", perguntas_etapa1(ids, campos)), ids, campos, mencoes)
    q2 = pedido_etapa2(s)
    precisa2 = P.VARIANTE_PRINCIPAL == "jev" or (P.VARIANTE_PRINCIPAL == "hibrida" and not s["essenciais_faltando"])
    prox = ler_next(s, chamar("2", q2)) if q2 and precisa2 else None
    unica = None
    if todas:  # comparação: nunca na produção. A `next` entra aqui só onde a principal não a chamou.
        r = chamar("comparacao", {"single_choice": P.choice_unica(ids), **(q2 if q2 and prox is None else {})})
        unica = ler_unica(ids, r)
        if q2 and prox is None:
            prox = ler_next(s, r)
    d = decidir(s, prox, unica)
    escolha = d["escolhas"][P.VARIANTE_PRINCIPAL]
    textos = {i["id"]: i["pergunta"] for i in catalogo}
    return {**d, "pergunta": escolha, "texto": textos.get(escolha), "longa": False, "falha": False, "etapas": rastro["etapas"],
            "revisar": bool(s["revisar"]), "motivo": s["revisar"] or f"variante `{P.VARIANTE_PRINCIPAL}`"}


def julgar_seguro(jev, conversa: list[dict], campos: dict, catalogo: list[dict], todas: bool = False) -> dict:
    """O que o consumidor chama. Falha operacional — timeout, erro da API, resposta ausente ou fora do contrato, na
    1ª requisição, na 2ª ou na de comparação — vira REVISÃO daquela conversa (`pergunta` = None, `revisar` e `falha`
    = True, motivo com a etapa e a classe do erro), nunca uma pergunta e nunca `no_question_needed`; o lote não
    aborta. Entrada inválida continua levantando erro: é defeito de quem chama, antes de qualquer requisição."""
    rastro: dict = {}
    try:
        return julgar(jev, conversa, campos, catalogo, todas, rastro)
    except Exception as e:  # noqa: BLE001 — qualquer falha depois da entrada é do item, não do lote
        if rastro.get("em") == "entrada":
            raise
        etapa = {"1": "1ª requisição", "2": "2ª requisição", "comparacao": "requisição de comparação"}[rastro["em"]]
        return {"pergunta": None, "texto": None, "longa": False, "revisar": True, "falha": True,
                "motivo": f"falha operacional: {etapa} ({type(e).__name__})", "escolhas": dict.fromkeys(VARIANTES_JEV),
                "etapas": rastro["etapas"]}


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
