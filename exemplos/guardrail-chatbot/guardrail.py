"""Guardrail de uma mensagem: UMA chamada ao Jev com a bateria da direção; a decisão é do código.

O Jev só julga (probabilidade de cada perigo, grau de severidade). O código decide, com os números de
`perguntas.py`: qual perigo disparou, em que faixa, e a ação final pela precedência bloqueia > revisa >
passa. O que a regra resolve sai do modelo: CPF e cartão válidos por inteiro na SAÍDA são achados por
regex + dígito verificador, sem depender do julgamento.

Não é fronteira de segurança (limite #6 do jev-1.13: o state não é tratado como hostil). É uma camada
de triagem barata ao lado de controles que não dependem de texto (autorização no backend, mascaramento).
"""
from __future__ import annotations

import re

import perguntas as P

_CPF = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
_CARTAO = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


def pedido(texto: str, direcao: str) -> tuple[dict, dict]:
    """(state, questions) de uma mensagem. State mínimo: só o texto, no campo que as perguntas nomeiam."""
    return {P.CAMPO_STATE[direcao]: texto}, P.PERGUNTAS[direcao]


def _cpf_valido(digitos: str) -> bool:
    """Dígitos verificadores do CPF. Rejeita sequência repetida (000.000.000-00 passa no cálculo)."""
    if len(digitos) != 11 or len(set(digitos)) == 1:
        return False
    for tam in (9, 10):
        soma = sum(int(d) * (tam + 1 - i) for i, d in enumerate(digitos[:tam]))
        if (soma * 10 % 11) % 10 != int(digitos[tam]):
            return False
    return True


def _luhn(digitos: str) -> bool:
    """Checagem de Luhn (número de cartão)."""
    total = 0
    for i, d in enumerate(reversed(digitos)):
        n = int(d) * (2 if i % 2 else 1)
        total += n - 9 if n > 9 else n
    return total % 10 == 0


def achar_documento(texto: str) -> list[str]:
    """CPF (11 dígitos com verificador válido) e cartão (13–19 dígitos, Luhn) escritos por INTEIRO.

    Mascarado ("***.***.247-25", "final 1111") não casa — é o que deve passar.
    @example achar_documento("CPF 529.982.247-25") → ["cpf"]
    """
    achados = []
    if any(_cpf_valido(re.sub(r"\D", "", m)) for m in _CPF.findall(texto)):
        achados.append("cpf")
    if any(_luhn(re.sub(r"\D", "", m)) for m in _CARTAO.findall(texto)):
        achados.append("cartao")
    return achados


def decidir(resposta: dict, texto: str, direcao: str) -> dict:
    """Resposta JSON da API → decisão (guarda os números brutos, para medir e re-limiar sem chamar de novo).

    @returns {"acao", "disparos": [(perigo, ação)], "nouls", "severidade", "regex", "flags"}
    """
    a = resposta["answers"]
    nouls = {q: v["noul"] for q, v in a.items() if v["type"] == "noul"}
    sev = a["severidade"]["score"]

    # Regex só na saída: na entrada, CPF/cartão costumam ser do próprio usuário (→ passa; mascarar no log
    # é outra camada). Na saída, documento inteiro bloqueia mesmo sendo do destinatário (GR-A024).
    regex = achar_documento(texto) if direcao == "saida" else []
    disparos = [("regex_documento", "bloqueia")] if regex else []

    for perigo, acao in P.ACAO_DO_PERIGO[direcao].items():
        lim, p = P.LIMIARES[direcao][perigo], nouls[perigo]
        if p >= lim["acao"]:
            disparos.append((perigo, acao))
        elif p >= lim["revisa"]:
            disparos.append((perigo, "revisa"))  # faixa do meio: humano olha, não o automático

    if sev >= P.SEV_BLOQUEIA:
        disparos = [(q, "bloqueia" if x == "revisa" else x) for q, x in disparos]
    if not disparos and P.SEV_REVISA is not None and sev >= P.SEV_REVISA:
        disparos.append(("severidade", "revisa"))  # rede: grave sem perigo nomeado não passa calado

    acao = next((x for x in P.PRECEDENCIA if any(d == x for _, d in disparos)), "passa")
    sinais = {**nouls, "regex_documento": 1.0 if regex else 0.0}
    flags = {f: max(sinais[q] for q in qs) >= P.FLAG_SIM for f, qs in P.FLAGS[direcao].items()}
    return {"acao": acao, "disparos": disparos, "nouls": nouls, "severidade": sev, "regex": regex, "flags": flags}
