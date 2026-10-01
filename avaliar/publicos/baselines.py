"""Baselines de R4/R5 — mesmas entradas do Jev, mesmo split (PROTOCOLO.md, seção Baselines).

Todos treinam SÓ no ajuste (100), exceto `tfidf_lr_amplo`, declarado como OUTRO regime: treina em todo
o lado do ajuste (grupos fora do teste, sem duplicata do teste). Nenhum baseline vê o teste.
Configurações fixadas ANTES do teste e não afinadas (com 100 exemplos, afinar seria decorar o ajuste).

Cada baseline devolve, por item: `escore` (ordena para PR-AUC), `prob` (probabilidade de sim ou None se
o método não dá probabilidade → Brier n/a), `pred` (0/1) e, no B2W, `nota` (1..5).
LLM real: não entra (sem autorização para outro provedor; nada simulado como qualidade).
"""
from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

LO_MIN = 1.0  # |log-odds| mínimo para a palavra entrar no léxico
DF_MIN = 2  # a palavra precisa aparecer em ≥ 2 textos do ajuste
SEMENTE = 20260930


def tokens(texto: str) -> set[str]:
    return set(re.findall(r"\w+", texto.casefold()))


def texto_de(it: dict) -> str:
    """A mesma entrada do Jev: HateBR `comentario`; B2W título + texto."""
    return it["texto"]


def limiar_por_custo(escores: list[float], golds: list[int]) -> float:
    """Menor nº de erros (FP = FN = 1, o custo declarado em perguntas.py) entre os pontos médios observados."""
    cand = sorted(set(escores))
    cortes = [cand[0] - 1] + [(a + b) / 2 for a, b in zip(cand, cand[1:])] + [cand[-1] + 1]
    return min(cortes, key=lambda c: (sum((e >= c) != g for e, g in zip(escores, golds)), abs(c)))


class Maioria:
    nome = "maioria"

    def fit(self, treino):
        self.p = sum(it["gold"] for it in treino) / len(treino)
        self.moda = Counter(it.get("nota") for it in treino).most_common(1)[0][0]
        return self

    def prever(self, itens):
        return [{"escore": self.p, "prob": self.p, "pred": int(self.p >= 0.5), "nota": self.moda} for _ in itens]


class Lexico:
    """Léxico de ofensa (HateBR) / de polaridade (B2W) por log-odds suavizado no ajuste; soma por texto."""
    nome = "lexico"

    def fit(self, treino):
        pos = [tokens(texto_de(it)) for it in treino if it["gold"] == 1]
        neg = [tokens(texto_de(it)) for it in treino if it["gold"] == 0]
        dp, dn = Counter(t for d in pos for t in d), Counter(t for d in neg for t in d)
        self.lex = {}
        for t in set(dp) | set(dn):
            if dp[t] + dn[t] < DF_MIN:
                continue
            lo = math.log((dp[t] + 1) / (len(pos) + 2)) - math.log((dn[t] + 1) / (len(neg) + 2))
            if abs(lo) >= LO_MIN:
                self.lex[t] = lo
        esc = [self._escore(it) for it in treino]
        self.corte = limiar_por_custo(esc, [it["gold"] for it in treino])
        if "nota" in treino[0]:  # nota: reta nota ~ escore ajustada no ajuste, arredondada
            self.reta = np.polyfit(esc, [it["nota"] for it in treino], 1)
        return self

    def _escore(self, it):
        return sum(self.lex.get(t, 0.0) for t in tokens(texto_de(it)))

    def prever(self, itens):
        out = []
        for it in itens:
            e = self._escore(it)
            r = {"escore": e, "prob": None, "pred": int(e >= self.corte)}
            if hasattr(self, "reta"):
                r["nota"] = int(min(5, max(1, round(float(np.polyval(self.reta, e))))))
            out.append(r)
        return out


class TfidfLR:
    """TF-IDF de palavras (1–2-gramas, sem acento, tf sublinear) + regressão logística (C=1). Limiar 0,5."""

    def __init__(self, nome="tfidf_lr"):
        self.nome = nome

    def _vec(self):
        return TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode", lowercase=True, sublinear_tf=True)

    def fit(self, treino):
        textos = [texto_de(it) for it in treino]
        self.v = self._vec().fit(textos)
        X = self.v.transform(textos)
        self.lr = LogisticRegression(C=1.0, max_iter=2000, random_state=SEMENTE).fit(X, [it["gold"] for it in treino])
        if "nota" in treino[0]:
            self.lr_nota = LogisticRegression(C=1.0, max_iter=2000, random_state=SEMENTE).fit(
                X, [it["nota"] for it in treino])
        return self

    def prever(self, itens):
        X = self.v.transform([texto_de(it) for it in itens])
        p = self.lr.predict_proba(X)[:, list(self.lr.classes_).index(1)]
        notas = self.lr_nota.predict(X) if hasattr(self, "lr_nota") else [None] * len(itens)
        return [{"escore": float(pi), "prob": float(pi), "pred": int(pi >= 0.5), "nota": (int(n) if n is not None else None)}
                for pi, n in zip(p, notas)]


def rodar_todos(ajuste: list[dict], treino_amplo: list[dict], teste: list[dict]) -> dict:
    """{nome: (previsões no teste, regime)}. Regime 'ajuste-100' é o comparável ao Jev zero-shot."""
    saida = {}
    for b in (Maioria(), Lexico(), TfidfLR()):
        saida[b.nome] = (b.fit(ajuste).prever(teste), "ajuste-100")
    saida["tfidf_lr_amplo"] = (TfidfLR("tfidf_lr_amplo").fit(treino_amplo).prever(teste), f"amplo-{len(treino_amplo)}")
    return saida
