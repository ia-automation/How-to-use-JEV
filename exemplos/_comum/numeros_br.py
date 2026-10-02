"""Leitura de números em formato brasileiro — infra comum dos exemplos.

Por que existe (revisões do Codex, 2026-10-01): o MESMO defeito apareceu em três exemplos escritos por agentes
diferentes — `conferencia-de-promessas` ("A 1.200 m do metrô" virou 200; "2,1 milhões" virou 2,1),
`imovel-duplicado` ("1.068,50 m²" virou 68,5) e `proxima-pergunta` ("até 6" × "até 600"). Número é do código
(limite #2 do jev-1.13), e código que lê número errado erra mais que o modelo. Um leitor só, com bateria.

O que lê: inteiros e decimais com ponto de milhar e vírgula decimal ("1.200", "1.068,50", "68,5", "2.100.000"),
multiplicadores ("900 mil", "2,1 milhões", "1,2 mi", "600k", "3 bi"), prefixo "R$" e a unidade que vem logo
depois ("m²", "m2", "m", "km", "min", "minutos", "%", "quartos", "vagas"...). O que NÃO lê (devolve nada, para o
chamador mandar a frase ao Jev ou à revisão em vez de comparar número truncado): número por extenso além de
"um/uma/dois/duas…dez", data, telefone, faixa ("de 3 a 5"), e ponto usado como decimal à inglesa ("1.5") — este
último é AMBÍGUO em pt-BR e vem marcado `ambiguo=True`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_MULT = {
    "mil": 1e3, "k": 1e3,
    "milhao": 1e6, "milhoes": 1e6, "mi": 1e6, "mm": 1e6,
    "bilhao": 1e9, "bilhoes": 1e9, "bi": 1e9,
}
_EXTENSO = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
            "oito": 8, "nove": 9, "dez": 10}
_UNIDADES = {
    "m²": "m2", "m2": "m2", "metros quadrados": "m2", "metro quadrado": "m2",
    "km": "km", "quilometros": "km", "quilometro": "km",
    "m": "m", "metros": "m", "metro": "m",
    "min": "min", "minutos": "min", "minuto": "min",
    "%": "%", "por cento": "%",
    "quartos": "quartos", "quarto": "quartos", "dormitorios": "quartos", "dormitorio": "quartos",
    "suites": "suites", "suite": "suites",
    "vagas": "vagas", "vaga": "vagas",
    "reais": "R$",
}

# Dígitos: milhar com ponto (1.200.000) OU sequência simples (1200), com decimal por vírgula opcional (,50).
# O lookbehind/lookahead impedem capturar o sufixo de um número maior ("1.068" não pode render "068").
_NUM = r"(?<![\d.,])(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?(?![\d])"
_RE = re.compile(
    rf"(?P<moeda>R\$\s*)?(?P<num>{_NUM})(?P<ingles>\.\d{{1,2}}(?!\d))?\s*"
    r"(?P<mult>milh[õo]es|milh[ãa]o|bilh[õo]es|bilh[ãa]o|mil\b|mi\b|mm\b|bi\b|k\b)?",
    re.IGNORECASE,
)
_RE_EXTENSO = re.compile(r"\b(" + "|".join(_EXTENSO) + r")\b", re.IGNORECASE)


def _sem_acento(s: str) -> str:
    return s.lower().translate(str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc"))


@dataclass(frozen=True)
class Numero:
    valor: float
    bruto: str          # trecho literal do texto
    inicio: int
    fim: int
    unidade: str | None  # "m2", "m", "km", "min", "%", "R$", "quartos", "vagas", "suites" ou None
    ambiguo: bool = False  # ponto decimal à inglesa ("1.5") ou extenso ("um" pode ser artigo)


def _unidade_apos(texto: str, fim: int) -> tuple[str | None, int]:
    resto = _sem_acento(texto[fim:fim + 24]).lstrip()
    salto = len(texto[fim:fim + 24]) - len(texto[fim:fim + 24].lstrip())
    for nome in sorted(_UNIDADES, key=len, reverse=True):  # "metros quadrados" antes de "metros", "m²" antes de "m"
        n = _sem_acento(nome)
        if resto.startswith(n) and not resto[len(n):len(n) + 1].isalnum():
            return _UNIDADES[nome], fim + salto + len(nome)
    return None, fim


def ler_numeros(texto: str, extenso: bool = False) -> list[Numero]:
    """Todos os números do texto, na ordem. `extenso=True` inclui um…dez por extenso (marcados ambíguos)."""
    achados: list[Numero] = []
    consumido = 0  # fim do último número + unidade: o "2" de "m2" é parte da unidade, não um número novo
    for m in _RE.finditer(texto):
        if m.start() < consumido:
            continue
        bruto_num = m.group("num")
        valor = float(bruto_num.replace(".", "").replace(",", "."))
        ambiguo = False
        if m.group("ingles"):
            # "1.5" ou "12.75": não é milhar (grupo de 3) nem decimal brasileiro — não adivinhar.
            valor = float(bruto_num.replace(".", "").replace(",", ".") + m.group("ingles"))
            ambiguo = True
        mult = m.group("mult")
        if mult:
            valor *= _MULT[_sem_acento(mult)]
        unidade, fim = _unidade_apos(texto, m.end())
        if m.group("moeda") and unidade is None:
            unidade = "R$"
        achados.append(Numero(valor, texto[m.start():fim].strip(), m.start(), fim, unidade, ambiguo))
        consumido = fim
    if extenso:
        for m in _RE_EXTENSO.finditer(_sem_acento(texto)):
            unidade, fim = _unidade_apos(texto, m.end())
            achados.append(Numero(float(_EXTENSO[m.group(1).lower()]), texto[m.start():fim].strip(), m.start(), fim,
                                  unidade, True))
        achados.sort(key=lambda n: n.inicio)
    return achados


def dentro_da_tolerancia(a: float, b: float, tolerancia: float) -> bool:
    """|a − b| ≤ tolerância × max(|a|, |b|) — simétrico, para "±3%" não depender de quem é o primeiro."""
    return abs(a - b) <= tolerancia * max(abs(a), abs(b))
