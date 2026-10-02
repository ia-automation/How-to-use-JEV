"""Bateria sem rede do invólucro `guarda.guardar_seguro`: falha operacional → `pergunta`, nunca `permite`.

Roda com um Jev de mentira (sem chave, sem cache): `python testa_falhas.py`. O controle é uma resposta LIMPA que
daria `permite` — se a validação deixasse uma falha passar, a bateria veria `permite`.
"""
from __future__ import annotations

import math

import guarda as G
import perguntas as P

CASO = {"tarefa": "listar os arquivos do projeto", "plano": None, "contexto_lido": None,
        "chamada": {"ferramenta": "bash", "comando": "ls -la"}}
DESTRUTIVO = {**CASO, "chamada": {"ferramenta": "bash", "comando": "rm -rf /srv/dados"}}


def resposta(valor: float = 0.02) -> dict:
    """Resposta válida no formato da API com todos os Nouls no mesmo valor."""
    return {"model": "duble", "answers": {q: {"type": "noul", "noul": valor} for q in P.PERGUNTAS}}


class Duble:
    def __init__(self, saida):
        self.saida, self.chamadas = saida, 0

    def perguntar(self, state, questions):
        self.chamadas += 1
        if isinstance(self.saida, Exception):
            raise self.saida
        return self.saida


def _sem(resp: dict, q: str) -> dict:
    return {**resp, "answers": {k: v for k, v in resp["answers"].items() if k != q}}


def _com(resp: dict, q: str, valor) -> dict:
    return {**resp, "answers": {**resp["answers"], q: {"type": "noul", "noul": valor}}}


def main() -> None:
    q0 = next(iter(P.PERGUNTAS))
    controle = G.guardar_seguro(Duble(resposta()), CASO)
    assert controle["origem"] == "jev" and controle["acao"] in G.ACOES, controle

    falhas = {
        "timeout": TimeoutError("sem resposta"),
        "erro de rede": ConnectionError("queda"),
        "cache faltando": RuntimeError("resposta não gravada no cache"),
        "resposta vazia": {},
        "sem answers": {"model": "duble"},
        "resposta None": None,
        "ID faltando": _sem(resposta(), q0),
        "bool no lugar de número": _com(resposta(), q0, True),
        "texto no lugar de número": _com(resposta(), q0, "0.1"),
        "número fora de [0,1]": _com(resposta(), q0, 1.4),
        "NaN": _com(resposta(), q0, math.nan),
        "noul None": _com(resposta(), q0, None),
    }
    for nome, saida in falhas.items():
        for dispensa in (False, True):
            s = G.guardar_seguro(Duble(saida), CASO, dispensa)
            assert s["acao"] == "pergunta" and s["origem"] == "falha" and s["motivo"].startswith("falha operacional"), (nome, s)
            try:
                G.guardar(Duble(saida), CASO, dispensa)
            except Exception:  # noqa: BLE001 — o baixo nível TEM de levantar
                pass
            else:
                raise AssertionError(f"`guardar` aceitou: {nome}")

    # o motivo não ecoa o texto da exceção (pode citar o corpo da resposta)
    s = G.guardar_seguro(Duble(RuntimeError("segredo-no-corpo")), CASO)
    assert "segredo-no-corpo" not in s["motivo"], s

    # caso malformado: nem chega a chamar
    for nome, ruim in {"None": None, "lista": [], "sem chamada": {"tarefa": "t"}, "chamada sem ferramenta": {"tarefa": "t", "chamada": {}},
                       "bash sem comando": {"tarefa": "t", "chamada": {"ferramenta": "bash"}}}.items():
        d = Duble(resposta())
        s = G.guardar_seguro(d, ruim)
        assert s["acao"] == "pergunta" and s["origem"] == "falha" and "entrada inválida" in s["motivo"] and d.chamadas == 0, (nome, s)

    # com a API fora, o padrão destrutivo casado segue junto para o humano ver
    s = G.guardar_seguro(Duble(TimeoutError()), DESTRUTIVO)
    assert s["acao"] == "pergunta" and s["regex"], s

    print(f"falha operacional → pergunta: {len(falhas) * 2} casos ok; entrada inválida: 5 ok; motivo sem eco: ok; "
          f"padrão destrutivo acompanha a falha: {s['regex']}")


if __name__ == "__main__":
    main()
