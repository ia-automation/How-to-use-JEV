"""Triagem de um ticket: UMA chamada ao Jev com todas as perguntas (fan-out especulativo);
composição da prioridade e roteamento ficam no código.

O Jev só julga (setor, três sim/não, grau de frustração). O código decide: qual fila, se vai cópia
para um 2º setor, se o ticket é incerto demais para seguir sozinho, e a prioridade.
"""
from __future__ import annotations

import perguntas as P


def pedido(mensagem: str, variante: str = "en") -> tuple[dict, dict]:
    """(state, questions) de um ticket. State mínimo: só a mensagem — as perguntas não usam mais nada."""
    return {P.CAMPO_STATE[variante]: mensagem}, P.PERGUNTAS[variante]


def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    """Noul em três faixas: True / False / None (= dúvida, vai para revisão)."""
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def compor_prioridade(valores: dict) -> tuple[float, str]:
    """valores: frustracao em 0..1 e os três Nouls em 0..1 (probabilidade ou gabarito 0/1).

    @example compor_prioridade({"frustracao": 1.0, "ameaca_cancelar": 1, "pede_reembolso": 0, "quer_humano": 1})
             → (0.85, "alta")
    """
    p = sum(peso * float(valores[k]) for k, peso in P.PESOS_PRIORIDADE.items())
    faixa = next(nome for piso, nome in P.FAIXAS_PRIORIDADE if p >= piso)
    return round(p, 4), faixa


def decidir(resposta: dict, variante: str = "en") -> dict:
    """Resposta JSON da API → decisão da triagem (guarda também os números brutos, para medir e re-limiar)."""
    a = resposta["answers"]
    mapa = P.SETOR_DA_OPCAO[variante]

    setor = a["setor"]
    principal = mapa[setor["choice"]]
    tambem = {k.removeprefix("tambem_"): v["noul"] for k, v in a.items() if k.startswith("tambem_")}
    copias = [s for s, v in sorted(tambem.items(), key=lambda kv: -kv[1]) if s != principal and v >= P.SETOR_COPIA_SIM]

    nouls = {f: a[f]["noul"] for f in P.NOULS}
    flags = {f: _faixa(v, *P.FAIXA_NOUL[f]) for f, v in nouls.items()}

    fr = a["frustracao"]
    n_niveis = len(fr["probabilities"])
    nivel = int(fr["score"] + 0.5)  # arredonda ao nível mais próximo (round() do Python arredonda 0,5 para o par)

    prioridade, faixa = compor_prioridade({"frustracao": fr["score"] / (n_niveis - 1), **nouls})

    # Só o que muda a AÇÃO vai para humano: setor (fila) e os três sim/não (reembolso, atendente,
    # retenção). Frustração incerta NÃO: ela só alimenta a prioridade, que usa o score contínuo mesmo
    # assim (medido no rascunho: reclamação educada de defeito cai entre calmo e frustrado, conf 0,2–0,5).
    motivos = []
    if principal is None:
        motivos.append("sem informação")  # a válvula da Choice venceu: não há setor a decidir
    elif setor["confidence"] < P.SETOR_CONF_MIN:
        motivos.append("setor incerto")
    elif copias and setor["confidence"] < P.SETOR_CONF_MIN_COM_COPIA:
        motivos.append("duas intenções sem principal claro")
    setor_duvida = bool(motivos)  # até aqui, só motivos de setor
    motivos += [f"{f} em dúvida" for f, v in flags.items() if v is None]
    if flags["quer_humano"]:
        motivos.append("pediu humano")  # não é incerteza: é o pedido do cliente

    return {
        "setor": principal,
        "setor_conf": setor["confidence"],
        "setor_copias": copias,
        "setor_duvida": setor_duvida,
        "tambem": tambem,
        "nouls": nouls,
        "flags": flags,
        "frustracao_score": fr["score"],
        "frustracao_conf": fr["confidence"],
        "frustracao_nivel": nivel,
        "prioridade": prioridade,
        "prioridade_faixa": faixa,
        "motivos": motivos,
        "destino": "humano" if motivos else f"fila:{principal}",
        "modelo": resposta["model"],
    }


def triar(jev, mensagem: str, variante: str = "en") -> dict:
    """Um ticket de ponta a ponta: uma requisição, decisão em código."""
    return decidir(jev.perguntar(*pedido(mensagem, variante)), variante)
