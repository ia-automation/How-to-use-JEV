"""BM25 próprio (sem dependência) e a linha de base de sobreposição de termos — a parte de CÓDIGO da busca.

Por que próprio: a coleção tem ~22 mil passagens; um BM25 de 60 linhas é auditável e evita dependência nova.
Parâmetros k1 = 0,9 e b = 0,4 (os do Anserini para passagens do MS MARCO; não afinados aqui). Tokens: NFKD sem
acento, minúsculas, `[a-z0-9]{2,}`, menos uma lista curta de palavras vazias do português. Sem radicalização
("biomas" ≠ "bioma") — é parte do que o rerank pode consertar e fica declarado como limite do baseline.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter

K1, B = 0.9, 0.4
_VAZIAS_BRUTAS = """a o as os um uma uns umas de do da dos das em no na nos nas por para com sem sob sobre e ou
que se ao aos à às pelo pela pelos pelas qual quais quando onde como porque por que quem ser é são foi foram ter tem
seu sua seus suas este esta esse essa isso isto aquele aquela mais menos muito já não sim também até entre"""
_TOKEN = re.compile(r"[a-z0-9]{2,}")


def _plano(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


# A lista passa pela MESMA normalização dos tokens (bateria: "não" só era removido se escrito sem acento).
PALAVRAS_VAZIAS = set(_plano(_VAZIAS_BRUTAS).split())


def tokens(texto: str) -> list[str]:
    return [t for t in _TOKEN.findall(_plano(texto)) if t not in PALAVRAS_VAZIAS]


class BM25:
    def __init__(self, documentos: list[str]):
        self.tf = [Counter(tokens(d)) for d in documentos]
        self.tam = [sum(c.values()) for c in self.tf]
        self.media = sum(self.tam) / len(self.tam) if self.tam else 0.0
        df = Counter(t for c in self.tf for t in c)
        n = len(documentos)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.postings: dict[str, list[int]] = {}
        for i, c in enumerate(self.tf):
            for t in c:
                self.postings.setdefault(t, []).append(i)

    def escore(self, termos: list[str], i: int) -> float:
        tf, tam = self.tf[i], self.tam[i]
        s = 0.0
        for t in termos:
            f = tf.get(t)
            if f:
                s += self.idf[t] * f * (K1 + 1) / (f + K1 * (1 - B + B * tam / self.media))
        return s

    def buscar(self, consulta: str, k: int) -> list[tuple[int, float]]:
        """[(índice do documento, escore)] dos k melhores; empate pelo índice (determinístico)."""
        termos = tokens(consulta)
        candidatos = {i for t in set(termos) for i in self.postings.get(t, ())}
        pontuados = sorted(((i, self.escore(termos, i)) for i in candidatos), key=lambda x: (-x[1], x[0]))
        return pontuados[:k]


def sobreposicao(consulta: str, passagem: str) -> float:
    """Baseline de rerank sem Jev: fração dos termos distintos da consulta presentes na passagem."""
    q = set(tokens(consulta))
    if not q:
        return 0.0
    return len(q & set(tokens(passagem))) / len(q)
