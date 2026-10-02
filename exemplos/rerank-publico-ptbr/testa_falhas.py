"""Bateria do código do rerank — roda sem chave, sem rede e sem o corpus (`python testa_falhas.py`).

O que se prova, com um dublê no lugar do Jev (código nosso, não o modelo — nenhum número daqui é medição do Jev):
  A. falha operacional — resposta falsa (bool, string, NaN, fora de [0,1], ID faltando, `type` trocado…), exceção
     de rede, cache faltando, trecho acima do teto, lote com um ID a menos: `reordenar_seguro` devolve a ORDEM DO
     BM25 inteira com `falha` marcada (nunca uma ordem parcial com os trechos que deram certo); o baixo nível levanta;
  B. ordenação — probabilidade manda, empate pelo BM25, depois a posição; o lote valida todos os IDs;
  C. métricas — NDCG@10 com ideal pelo gabarito INTEIRO (relevante fora do top-20 pesa), MRR@10 com nota ≥ 2,
     bootstrap determinístico pela semente;
  D. BM25 e sobreposição — ordem esperada em casos construídos (consulta SINTÉTICA, nenhuma do Quati); tokenização
     sem acento;
  E. cache — resposta rejeitada pela validação é invalidada SÓ para aquele pedido (`jev.invalidar`); exceção de rede
     não invalida nada; o hash dos textos consumidos muda quando um trecho muda e não quando só a ordem dos campos muda.
"""
from __future__ import annotations

import copy
import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))
sys.path.insert(0, str(AQUI))

import bm25 as B  # noqa: E402
import perguntas as P  # noqa: E402
import rerank as R  # noqa: E402
import run as RUN  # noqa: E402

TRECHOS = ["a", "b", "c", "d"]
BM25 = [4.0, 3.0, 2.0, 1.0]


def resposta(p: float) -> dict:
    return {"model": "duble", "answers": {"answers": {"type": "noul", "noul": p}}}


def resposta_lote(probs: list[float]) -> dict:
    return {"model": "duble", "answers": {f"p{i}": {"type": "noul", "noul": p} for i, p in enumerate(probs)}}


class Duble:
    """Jev de mentira: por trecho devolve `por_trecho[texto]` (resposta ou exceção) ou `padrao`; `lote` para o modo lote."""

    def __init__(self, padrao=None, por_trecho: dict | None = None, lote=None):
        self.padrao, self.por_trecho, self.lote = padrao if padrao is not None else resposta(0.1), por_trecho or {}, lote
        self.chamadas: list[dict] = []
        self.invalidados: list = []

    def perguntar(self, state, questions):
        saida = self.lote if "passages" in state else self.por_trecho.get(state["passage"], self.padrao)
        if isinstance(saida, Exception):
            raise saida
        return saida

    def perguntar_varios(self, pedidos, paralelo=8):
        return [self.perguntar(*p) for p in pedidos]

    def invalidar(self, state, questions):
        self.invalidados.append(state)
        return True

    def resumo(self):
        return {}


def _mexe(caminho: list, valor=None, apaga: bool = False):
    def aplica(r: dict) -> dict:
        alvo = r
        for chave in caminho[:-1]:
            alvo = alvo[chave]
        if apaga:
            del alvo[caminho[-1]]
        else:
            alvo[caminho[-1]] = valor
        return r
    return aplica


FALSAS = [
    ("Noul bool", _mexe(["answers", "answers", "noul"], True)),
    ("Noul string", _mexe(["answers", "answers", "noul"], "0.9")),
    ("Noul None", _mexe(["answers", "answers", "noul"], None)),
    ("Noul NaN", _mexe(["answers", "answers", "noul"], math.nan)),
    ("Noul > 1", _mexe(["answers", "answers", "noul"], 1.5)),
    ("Noul negativo", _mexe(["answers", "answers", "noul"], -0.1)),
    ("sem campo noul", _mexe(["answers", "answers", "noul"], apaga=True)),
    ("ID faltando", _mexe(["answers", "answers"], apaga=True)),
    ("type trocado", _mexe(["answers", "answers", "type"], "choice")),
    ("answers vazio", _mexe(["answers"], {})),
    ("sem answers", _mexe(["answers"], apaga=True)),
]
EXCECOES = [TimeoutError("tempo"), ConnectionError("rede"), RuntimeError("resposta não gravada no cache"), KeyError("usage")]


def _confere(nome: str, saida: dict, etapa: str, falhas: list) -> None:
    if saida["ordem"] != [0, 1, 2, 3] or saida["probs"] is not None or not (saida["falha"] or "").startswith(etapa):
        falhas.append(f"A {nome}: {saida}")


def bateria_falhas(falhas: list) -> int:
    n = 0
    # falha num só trecho (o 3º) → a consulta INTEIRA volta à ordem do BM25
    for nome, corrompe in FALSAS:
        jev = Duble(resposta(0.9), {"c": corrompe(copy.deepcopy(resposta(0.9)))})
        _confere(nome, R.reordenar_seguro(jev, "q", TRECHOS, BM25), "chamada", falhas)
        try:
            R.julgar_trechos(jev, "q", TRECHOS)
            falhas.append(f"A {nome}: julgar_trechos não levantou")
        except Exception:  # noqa: BLE001
            pass
        n += 1
    for e in EXCECOES:
        _confere(type(e).__name__, R.reordenar_seguro(Duble(resposta(0.9), {"b": e}), "q", TRECHOS, BM25), "chamada", falhas)
        n += 1
    for nome, inteira in (("None", None), ("lista", []), ("string", "ok"), ({}, {})):
        jev = Duble(resposta(0.9))
        jev.padrao = inteira
        _confere(f"resposta {nome}", R.reordenar_seguro(jev, "q", TRECHOS, BM25), "chamada", falhas)
        n += 1
    # entrada fora da faixa: trecho acima do teto, consulta vazia, tamanhos diferentes → sem chamada
    longo = ["a", "x" * (P.TETO_CARACTERES_TRECHO + 1), "c", "d"]
    _confere("trecho longo", R.reordenar_seguro(Duble(resposta(0.9)), "q", longo, BM25), "chamada", falhas)
    _confere("consulta vazia", R.reordenar_seguro(Duble(resposta(0.9)), "  ", TRECHOS, BM25), "chamada", falhas)
    s = R.reordenar_seguro(Duble(resposta(0.9)), "q", TRECHOS, BM25[:3])
    if s["ordem"] != [0, 1, 2, 3] or not s["falha"].startswith("entrada inválida"):
        falhas.append(f"A tamanhos diferentes: {s}")
    n += 3
    # lote: um ID a menos, ou um inválido → ordem do BM25
    for nome, lote in (("ID a menos", resposta_lote([0.9, 0.8, 0.7])), ("bool no p2", _mexe(["answers", "p2", "noul"], False)(resposta_lote([0.9, 0.8, 0.7, 0.6]))),
                       ("exceção", TimeoutError())):
        _confere(f"lote {nome}", R.reordenar_seguro(Duble(lote=lote), "q", TRECHOS, BM25, modo="lote"), "chamada", falhas)
        n += 1
    return n


def bateria_ordenacao(falhas: list) -> int:
    if R.ordenar([0.1, 0.9, 0.9, 0.5], BM25) != [1, 2, 3, 0]:
        falhas.append(f"B ordem: {R.ordenar([0.1, 0.9, 0.9, 0.5], BM25)}")
    if R.ordenar([0.5, 0.5, 0.5, 0.5], [1.0, 3.0, 2.0, 3.0]) != [1, 3, 2, 0]:
        falhas.append("B empate pelo BM25 e depois posição")
    jev = Duble(resposta(0.1), {"c": resposta(0.95), "d": resposta(0.6)})
    s = R.reordenar_seguro(jev, "q", TRECHOS, BM25)
    if s["falha"] or s["ordem"] != [2, 3, 0, 1] or s["probs"] != [0.1, 0.1, 0.95, 0.6]:
        falhas.append(f"B por trecho: {s}")
    s = R.reordenar_seguro(Duble(lote=resposta_lote([0.2, 0.2, 0.7, 0.2])), "q", TRECHOS, BM25, modo="lote")
    if s["falha"] or s["ordem"] != [2, 0, 1, 3]:
        falhas.append(f"B lote: {s}")
    st = R.state_lote("q", TRECHOS)
    if [p["id"] for p in st["passages"]] != [0, 1, 2, 3] or set(P.perguntas_lote(4)) != {"p0", "p1", "p2", "p3"} \
            or "`passages[3].text`" not in P.perguntas_lote(4)["p3"]["instructions"]:
        falhas.append("B state/perguntas do lote não apontam a posição")
    try:
        R.ordenar([0.5], BM25)
        falhas.append("B ordenar aceitou tamanhos diferentes")
    except ValueError:
        pass
    return 6


def bateria_metricas(falhas: list) -> int:
    c = {"notas": [0, 2, None, 3], "gabarito": {"x": 2, "y": 3, "z": 3}}  # um 3 do gabarito fora do top-20
    if abs(RUN.ndcg([3, 1, 0, 2], c) - 1.0) > 1e-9 + (1 - RUN.ndcg([3, 1, 0, 2], c)) or RUN.ndcg([3, 1, 0, 2], c) >= 1.0:
        falhas.append("C ideal não vem do gabarito inteiro (relevante perdido não pesou)")
    melhor = RUN.ndcg([3, 1, 0, 2], c)
    ideal_parcial = (7 / math.log2(2) + 3 / math.log2(3)) / (7 / math.log2(2) + 7 / math.log2(3) + 3 / math.log2(4))
    if abs(melhor - ideal_parcial) > 1e-9:
        falhas.append(f"C NDCG esperado {ideal_parcial:.4f}, veio {melhor:.4f}")
    if RUN.ndcg([0, 2, 1, 3], c) >= melhor:
        falhas.append("C ordem pior não deu NDCG menor")
    if RUN.mrr([0, 2, 1, 3], c) != 1 / 3 or RUN.mrr([3, 0, 1, 2], c) != 1.0 or RUN.mrr([0, 2, 0, 0], {"notas": [1, None, 1, 1], "gabarito": {}}) != 0.0:
        falhas.append("C MRR com nota ≥ 2")
    if RUN.primeiro_relevante([2, 1, 3, 0], c) != 2 or RUN.primeiro_relevante([0, 2], c) is not None:
        falhas.append("C primeiro_relevante")
    a = RUN.bootstrap({"bm25": [0.2, 0.4, 0.6], "jev": [0.3, 0.5, 0.9]})
    b = RUN.bootstrap({"bm25": [0.2, 0.4, 0.6], "jev": [0.3, 0.5, 0.9]})
    if a != b or a["jev"]["delta"] <= 0 or a["jev"]["delta_ic"][0] <= 0 or a["bm25"]["delta"] != 0:
        falhas.append(f"C bootstrap: {a}")
    if RUN.latencia_consulta([100] * 16, 8) != 200 or RUN.latencia_consulta([300, 100, 100], 2) != 300:
        falhas.append("C latência por consulta (fila de vagas)")
    return 7


def bateria_bm25(falhas: list) -> int:
    # Frases inventadas aqui; nenhuma consulta nem passagem do Quati (revisão do Codex, 2026-10-01).
    docs = ["o planeta marte tem duas luas pequenas", "lua é um satélite natural", "receita de bolo de cenoura", "luas luas luas de júpiter"]
    idx = B.BM25(docs)
    topo = [i for i, _ in idx.buscar("Quantas luas tem o planeta Marte?", 3)]
    if topo[0] != 0 or 2 in topo or 1 in topo:
        falhas.append(f"D BM25: {topo}")
    if B.tokens("Água ÁRVORE, não!") != ["agua", "arvore"]:
        falhas.append(f"D tokens: {B.tokens('Água ÁRVORE, não!')}")
    if B.sobreposicao("luas marte", docs[0]) != 1.0 or B.sobreposicao("luas marte", docs[2]) != 0.0 or B.sobreposicao("", docs[0]) != 0.0:
        falhas.append("D sobreposição")
    return 3


def bateria_cache(falhas: list) -> int:
    # só o pedido rejeitado é invalidado; os válidos da mesma consulta ficam
    jev = Duble(resposta(0.9), {"c": _mexe(["answers", "answers", "noul"], True)(resposta(0.9))})
    R.reordenar_seguro(jev, "q", TRECHOS, BM25)
    if jev.invalidados != [{"query": "q", "passage": "c"}]:
        falhas.append(f"E invalidou {jev.invalidados}")
    # dois rejeitados → os dois invalidados, uma vez cada
    jev = Duble(resposta(0.9), {"a": {}, "d": _mexe(["answers", "answers", "noul"], "x")(resposta(0.9))})
    R.reordenar_seguro(jev, "q", TRECHOS, BM25)
    if sorted(s["passage"] for s in jev.invalidados) != ["a", "d"]:
        falhas.append(f"E dois rejeitados: {jev.invalidados}")
    # exceção de rede / entrada inválida: nada a invalidar (não havia resposta gravada)
    jev = Duble(resposta(0.9), {"b": TimeoutError()})
    R.reordenar_seguro(jev, "q", TRECHOS, BM25)
    jev2 = Duble(resposta(0.9))
    R.reordenar_seguro(jev2, "q", ["a", "x" * (P.TETO_CARACTERES_TRECHO + 1)], BM25[:2])
    if jev.invalidados or jev2.invalidados:
        falhas.append("E invalidou sem resposta rejeitada")
    # lote: um ID a menos → a requisição do lote é invalidada (uma vez)
    jev = Duble(lote=resposta_lote([0.9, 0.8, 0.7]))
    R.reordenar_seguro(jev, "q", TRECHOS, BM25, modo="lote")
    if len(jev.invalidados) != 1 or "passages" not in jev.invalidados[0]:
        falhas.append(f"E lote: {jev.invalidados}")
    # hash dos textos consumidos
    base = [{"query_id": 1, "texto": "q", "top": [{"id": "p1"}, {"id": "p2"}], "trechos": ["t1", "t2"]}]
    h1 = RUN.hash_textos(base)
    outro = [{"query_id": 1, "texto": "q", "top": [{"id": "p1"}, {"id": "p2"}], "trechos": ["t1", "t2 mudou"]}]
    mesma = [{"top": [{"id": "p1"}, {"id": "p2"}], "trechos": ["t1", "t2"], "texto": "q", "query_id": 1}]
    if h1 == RUN.hash_textos(outro) or h1 != RUN.hash_textos(mesma) or h1 != RUN.hash_textos(base):
        falhas.append("E hash dos textos não distingue trecho trocado / não é determinístico")
    return 5


def main() -> None:
    falhas: list[str] = []
    a, b, c, d, e = bateria_falhas(falhas), bateria_ordenacao(falhas), bateria_metricas(falhas), bateria_bm25(falhas), bateria_cache(falhas)
    if falhas:
        sys.exit(f"FALHOU ({len(falhas)}):\n  " + "\n  ".join(falhas[:40]))
    print(f"ok: A {a} falhas → ordem do BM25 inteira com `falha` (baixo nível levanta) · B {b} conferências de ordenação e lote · "
          f"C {c} de métricas e bootstrap · D {d} de BM25/sobreposição · E {e} de cache (invalidar só o rejeitado) e hash dos textos")


if __name__ == "__main__":
    main()
