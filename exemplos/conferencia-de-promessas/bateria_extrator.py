"""Bateria do extrator numérico — roda em código, sem API, sem cache.

Nasceu da revisão adversarial (Codex, 2026-10-01): as frases que ele deduziu estaticamente ("Tem 3 quartos e
vaga" × `vagas: 0`, "Não tem 2 vagas", "A 1.200 m do metrô", "Custa 1,9 milhão", "Tem 4 quartos e 1 vaga" sem
campo de vagas) estão aqui, mais as vizinhas da mesma família. Cada caso fixa o CAMINHO (codigo / composta /
jev) e a relação que o código decide sozinho (None = o código não decide). Uso:
  ..\\..\\.venv\\Scripts\\python.exe bateria_extrator.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import conferir as C  # noqa: E402

DESC_1200 = "Apartamento em Santana, 3 quartos, a 1.200 m da estação Santana. Aceita pet."
DESC_21MI = "Cobertura em Moema, 4 vagas, 320 m². R$ 2.100.000. Condomínio R$ 2.400."
DESC_19MI = "Cobertura em Moema. R$ 1,9 milhão."


def ficha(campos: dict | None = None, descricao: str = "Apartamento à venda.") -> dict:
    return {"titulo": "Imóvel", "descricao": descricao, "campos": campos or {}}


# (afirmação, ficha, caminho esperado, relação que o CÓDIGO decide)
CASOS = [
    # --- achado 2: polaridade e proposição não interpretada
    ("Tem 3 quartos e vaga", ficha({"quartos": 3, "vagas": 0}), "codigo", "contradicted"),
    ("Não tem 2 vagas", ficha({"vagas": 2}), "jev", None),
    ("Não tem mais de 2 vagas", ficha({"vagas": 2}), "jev", None),
    ("Tem 2 vagas e não aceita pet", ficha({"vagas": 2, "aceita_pet": False}), "jev", None),
    ("Não tem vaga", ficha({"vagas": 0}), "codigo", "supported"),
    ("Não tem vaga", ficha({"vagas": 1}), "codigo", "contradicted"),
    ("Zero vagas", ficha({"vagas": 0}), "codigo", "supported"),
    ("Sem vaga própria", ficha({"vagas": 0}), "composta", "supported"),
    ("Tem vaga", ficha({"vagas": 0}), "codigo", "contradicted"),
    ("Tem 2 vagas cobertas", ficha({"vagas": 2}), "composta", "supported"),
    ("Tem 2 vagas cobertas", ficha({"vagas": 1}), "composta", "contradicted"),
    ("Tem 3 quartos, 2 suítes", ficha({"quartos": 3}), "composta", "supported"),
    ("Tem quartos amplos e 2 vagas", ficha({"quartos": 3, "vagas": 2}), "composta", "supported"),
    ("Tem garagem para dois carros", ficha({"vagas": 2}), "codigo", "supported"),
    ("Tem 2 vagas na garagem", ficha({"vagas": 2}), "codigo", "supported"),
    ("Tem 3 quartos e 3 vagas", ficha({"quartos": 3, "vagas": 2}), "codigo", "contradicted"),
    ("Tem 130 m² e 3 vagas", ficha({"area_m2": 130, "vagas": 2}), "codigo", "contradicted"),
    ("Condomínio de 450 reais já inclui luz", ficha({"condominio_reais": 450}), "composta", "supported"),
    ("Aceita pet de até 10 kg", ficha({"vagas": 1}), "jev", None),
    # --- achado 3: ponto de milhar na descrição (sem campo estruturado)
    ("Fica a 200 m do metrô", ficha(descricao=DESC_1200), "codigo", "contradicted"),
    ("Fica a 1,2 km do metrô", ficha(descricao=DESC_1200), "codigo", "supported"),
    ("Fica a 1 km do metrô", ficha(descricao=DESC_1200), "codigo", "contradicted"),
    ("Uns 15 minutos a pé do metrô", ficha(descricao=DESC_1200), "codigo", "supported"),
    # --- achado 4: gramática numérica inteira (milhão) e multiplicador desconhecido
    ("Custa 1,9 milhão", ficha(descricao=DESC_21MI), "codigo", "contradicted"),
    ("Custa 2,1 milhões", ficha(descricao=DESC_21MI), "codigo", "supported"),
    ("Custa 2,1 mi", ficha(descricao=DESC_21MI), "jev", None),
    ("Custa 2,1 bilhões", ficha(descricao=DESC_21MI), "jev", None),
    ("Custa 1,9 milhão", ficha(descricao=DESC_19MI), "codigo", "supported"),
    ("Custa 890 mil", ficha(descricao="Casa. R$ 890.000."), "codigo", "supported"),
    ("Custa menos de 800 mil", ficha(descricao="Casa. R$ 890.000."), "codigo", "contradicted"),
    ("Condomínio abaixo de mil", ficha({"condominio_reais": 1800}), "codigo", "contradicted"),
    ("O condomínio custa R$ 520", ficha({"condominio_reais": 520}), "codigo", "supported"),
    ("Condomínio barato, R$ 520", ficha({"condominio_reais": 520}), "composta", "supported"),
    # --- achado 5: campo ausente não apaga contradição provada em outra dimensão
    ("Tem 4 quartos e 1 vaga", ficha({"quartos": 3}), "composta", "contradicted"),
    ("Tem 3 quartos e 1 vaga", ficha({"quartos": 3}), "composta", "supported"),
    ("Tem vaga", ficha({"quartos": 1}), "jev", None),
    ("Tem 2 vagas e 90 m²", ficha({"vagas": 2}), "composta", "supported"),
    # --- distância estimada e comparadores (regressão do que já funcionava)
    ("Uns 5 minutos a pé do metrô", ficha({"distancia_metro_m": 400}), "codigo", "supported"),
    ("Fica a menos de 1,5 km do metrô", ficha({"distancia_metro_m": 1200}), "codigo", "supported"),
    ("Fica a 600 metros do metrô", ficha({"distancia_metro_m": 600}), "codigo", "supported"),
    ("Tem mais de 100 m²", ficha({"area_m2": 98}), "codigo", "contradicted"),
    ("Tem quase 100 m²", ficha({"area_m2": 98}), "codigo", "supported"),
]

# Respostas inválidas do Jev (achado 6): nenhuma pode virar decisão — todas têm de levantar erro.
_CASO_JEV = {"id": "X", "ficha": ficha({"vagas": 1}), "afirmacoes": [{"id": "a1", "texto": "Aceita pet"}]}
RESPOSTAS_INVALIDAS = {
    "sem probabilities": {"model": "x", "answers": {"rel_0": {"choice": "supported", "confidence": 0.9}}},
    "probabilities vazio": {"model": "x", "answers": {"rel_0": {"choice": "supported", "confidence": 0.9, "probabilities": {}}}},
    "opção faltando": {"model": "x", "answers": {"rel_0": {"choice": "supported", "confidence": 0.9,
                                                           "probabilities": {"supported": 0.9, "contradicted": 0.1}}}},
    "não soma 1": {"model": "x", "answers": {"rel_0": {"choice": "supported", "confidence": 0.9,
                                                       "probabilities": {"supported": 0.9, "contradicted": 0.5, "not_stated": 0.1}}}},
    "bool como probabilidade": {"model": "x", "answers": {"rel_0": {"choice": "supported", "confidence": True,
                                                                    "probabilities": {"supported": True, "contradicted": 0.0, "not_stated": 0.0}}}},
    "opção fora da lista": {"model": "x", "answers": {"rel_0": {"choice": "maybe", "confidence": 0.9,
                                                                "probabilities": {"supported": 0.5, "contradicted": 0.3, "not_stated": 0.2}}}},
    "ID faltando": {"model": "x", "answers": {}},
}


def main() -> int:
    falhas = 0
    for texto, f, caminho_esp, rel_esp in CASOS:
        c = C.caminhos({"id": "X", "ficha": f, "afirmacoes": [{"id": "a1", "texto": texto}]})[0]
        num = c["numero"] or {}
        rel = num.get("relacao") if c["caminho"] != "jev" else None
        ok = c["caminho"] == caminho_esp and rel == rel_esp
        falhas += not ok
        partes = "; ".join(f"{p['dim']} {p['comparador']} {p['valor']:g} × {p['ficha']} → {p['relacao']}" for p in num.get("partes", []))
        print(f"{'ok ' if ok else 'ERR'} {texto!r:42} {c['caminho']:8} {rel!s:12} | {partes} | sobra={num.get('sobra', [])}")
    for nome, resposta in RESPOSTAS_INVALIDAS.items():
        try:
            saida = C.compor(_CASO_JEV, resposta)
        except ValueError:
            print(f"ok  resposta inválida ({nome}) → erro")
        else:
            falhas += 1
            print(f"ERR resposta inválida ({nome}) virou {saida['afirmacoes'][0]['acao']}")
    print(f"\n{len(CASOS) + len(RESPOSTAS_INVALIDAS)} casos, {falhas} falhas")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
