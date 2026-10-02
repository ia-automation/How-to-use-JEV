"""Bateria do leitor de números brasileiro. Rodar: python testa_numeros_br.py (sem API, sem dependência)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from numeros_br import dentro_da_tolerancia, ler_numeros  # noqa: E402

# (texto, [(valor, unidade)]) — os três primeiros blocos são os defeitos reais achados pelo Codex em 2026-10-01.
CASOS = [
    # conferencia-de-promessas: ponto de milhar não é fim de frase; "milhão" multiplica
    ("A 1.200 m do metrô", [(1200.0, "m")]),
    ("Custa 2,1 milhões", [(2_100_000.0, None)]),
    ("R$ 1,9 milhão", [(1_900_000.0, "R$")]),
    ("900 mil", [(900_000.0, None)]),
    # imovel-duplicado: número completo, nunca o sufixo
    ("1.068 m²", [(1068.0, "m2")]),
    ("1.068,50 m²", [(1068.5, "m2")]),
    ("68,5 m2 de área privativa", [(68.5, "m2")]),
    ("apartamento de 92 m² com salão comum de 68 m²", [(92.0, "m2"), (68.0, "m2")]),
    # proxima-pergunta: magnitude
    ("até 6", [(6.0, None)]),
    ("até 600", [(600.0, None)]),
    ("até 600 mil", [(600_000.0, None)]),
    ("600k", [(600_000.0, None)]),
    ("1,2 mi", [(1_200_000.0, None)]),
    ("prestação de 3 mil", [(3000.0, None)]),
    ("2.500 por mês", [(2500.0, None)]),
    # unidades e moeda
    ("R$ 520 de condomínio", [(520.0, "R$")]),
    ("a 5 minutos do metrô", [(5.0, "min")]),
    ("fica a 1,8 km", [(1.8, "km")]),
    ("3 quartos e 2 vagas", [(3.0, "quartos"), (2.0, "vagas")]),
    ("cobertura de 85%", [(85.0, "%")]),
    ("2.100.000", [(2_100_000.0, None)]),
    ("62 metros quadrados", [(62.0, "m2")]),
    # não inventa: sem dígito, nada
    ("perto do metrô", []),
]


def main() -> int:
    falhas = 0
    for texto, esperado in CASOS:
        lido = [(n.valor, n.unidade) for n in ler_numeros(texto)]
        if lido != esperado:
            falhas += 1
            print(f"FALHA {texto!r}: lido {lido}, esperado {esperado}")
    # decimal à inglesa é marcado ambíguo, não adivinhado
    n = ler_numeros("versão 1.5 do app")
    if not (len(n) == 1 and n[0].ambiguo and n[0].valor == 1.5):
        falhas += 1
        print(f"FALHA ambíguo: {n}")
    # extenso só quando pedido, e sempre ambíguo ("um" pode ser artigo)
    if ler_numeros("tem um quarto") or [(x.valor, x.unidade, x.ambiguo) for x in ler_numeros("tem um quarto", True)] != [(1.0, "quartos", True)]:
        falhas += 1
        print("FALHA extenso")
    # tolerância simétrica
    if not dentro_da_tolerancia(100, 103, 0.03) or dentro_da_tolerancia(100, 104, 0.03) or \
            dentro_da_tolerancia(100, 103, 0.03) != dentro_da_tolerancia(103, 100, 0.03):
        falhas += 1
        print("FALHA tolerância")
    print(f"{len(CASOS) + 3 - falhas}/{len(CASOS) + 3} ok")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
