"""Métricas comuns dos exemplos: acerto, cobertura × erro por limiar, Brier, NDCG e tabelas em Markdown."""
from __future__ import annotations

import math
from collections import Counter


def acerto(pares: list[tuple]) -> float:
    """pares = [(previsto, gabarito)]; ignora gabarito None (caso sem rótulo)."""
    validos = [(p, g) for p, g in pares if g is not None]
    return sum(p == g for p, g in validos) / len(validos) if validos else float("nan")


def matriz_confusao(pares: list[tuple]) -> dict:
    return dict(Counter((g, p) for p, g in pares if g is not None))


def cobertura_erro(itens: list[tuple], limiares: list[float]) -> list[dict]:
    """itens = [(confianca, acertou)]. Para cada limiar: fração automatizada e erro entre os automatizados."""
    linhas = []
    for lim in limiares:
        auto = [ok for conf, ok in itens if conf >= lim]
        linhas.append({
            "limiar": lim,
            "cobertura": len(auto) / len(itens) if itens else float("nan"),
            "erro_automatico": (1 - sum(auto) / len(auto)) if auto else float("nan"),
            "n_auto": len(auto),
        })
    return linhas


def faixa_noul(itens: list[tuple], nao: float, sim: float) -> dict:
    """itens = [(noul, gabarito_bool)]. Abaixo de `nao` = não; acima de `sim` = sim; meio = revisão."""
    decididos = [(v >= sim, g) for v, g in itens if g is not None and (v <= nao or v >= sim)]
    revisao = sum(1 for v, g in itens if g is not None and nao < v < sim)
    total = sum(1 for _, g in itens if g is not None)
    return {
        "cobertura": len(decididos) / total if total else float("nan"),
        "acerto_decididos": sum(p == g for p, g in decididos) / len(decididos) if decididos else float("nan"),
        "revisao": revisao,
        "n": total,
    }


def brier(itens: list[tuple]) -> float:
    """itens = [(probabilidade_sim, gabarito_bool)]; menor é melhor (0 = perfeito)."""
    validos = [(p, g) for p, g in itens if g is not None]
    return sum((p - (1.0 if g else 0.0)) ** 2 for p, g in validos) / len(validos) if validos else float("nan")


def ndcg(relevancias_na_ordem: list[float], k: int, relevancias_do_gabarito: list[float] | None = None) -> float:
    """Relevâncias graduadas na ordem devolvida pelo sistema.

    O ideal vem do GABARITO INTEIRO (todos os itens relevantes, inclusive os que a recuperação
    descartou). Calcular o ideal só pela lista devolvida esconderia a perda da recuperação —
    por isso `relevancias_do_gabarito` deve ser passado sempre que houver etapa de recuperação.
    """
    def dcg(rs):
        return sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(rs[:k]))
    base = relevancias_do_gabarito if relevancias_do_gabarito is not None else relevancias_na_ordem
    ideal = dcg(sorted(base, reverse=True))
    return dcg(relevancias_na_ordem) / ideal if ideal else 0.0


def tabela(linhas: list[dict], colunas: list[str] | None = None) -> str:
    """Lista de dicts → tabela Markdown (números com 3 casas)."""
    if not linhas:
        return "_(vazio)_"
    colunas = colunas or list(linhas[0])

    def fmt(v):
        return f"{v:.3f}" if isinstance(v, float) else str(v)

    cab = "| " + " | ".join(colunas) + " |\n|" + "---|" * len(colunas) + "\n"
    return cab + "\n".join("| " + " | ".join(fmt(l.get(c, "")) for c in colunas) + " |" for l in linhas)
