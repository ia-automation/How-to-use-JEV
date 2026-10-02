"""Bateria do código do auditor — roda sem chave e sem rede (`python testa_auditor.py`).

Por que existe (revisão adversarial do Codex, 2026-10-01, 5 achados): o que mudou na rodada 2 é CÓDIGO (comparador,
recência, triagem do state, métrica), e quase nada disso é exercitado pelos 104 casos rotulados — nenhum tem `≥`,
dois números do mesmo assunto ou um número em ambiente errado. Aqui cada verificação monta o caso mínimo e confere
a saída do código; onde a regra depende de Nouls, eles são um dublê (o que se testa é código nosso, não o modelo).
  A. comparadores: `≥`, `≤`, `>=`, `<=`, "pelo menos", "no mínimo", "no máximo", "abaixo de", "acima de", "menos de",
     vírgula decimal, `%`, ms, réplicas, limiar exato — o check nasce e `holds` é a conta certa (achado 4);
  B. recência só dentro do mesmo assunto (objeto, ambiente, componente); sem assunto reconhecível, ninguém é
     superado (achado 1);
  C. triagem antes da chamada: registro de outra revisão/migration fora do state; número refeito por outro mais
     recente do mesmo assunto fora do state; número de outro ambiente/componente não vira check (achados 2 e 3);
  D. `compor` não devolve `supported` com registro superado no state; state sem registro não chama o Jev (achado 2);
  E. métrica de apoio por par (registro, papel) e rótulo de `supports_i` só onde é inequívoco (achado 5).
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import auditor as A  # noqa: E402
import perguntas as P  # noqa: E402
import run as R  # noqa: E402

FALHAS: list[str] = []
FEITAS = 0


def confere(nome: str, obtido, esperado) -> None:
    global FEITAS
    FEITAS += 1
    if obtido != esperado:
        FALHAS.append(f"{nome}: esperado {esperado!r}, obtido {obtido!r}")


def caso(afirmacao: str, *registros: tuple[str, str]) -> dict:
    """Caso no formato dos dados: registros (tipo, texto) viram e1, e2, … na ordem dada."""
    return {"afirmacao": afirmacao, "registros": [{"id": f"e{i}", "tipo": t, "texto": x} for i, (t, x) in enumerate(registros, 1)]}


def nouls(sup: list[float], con: list[float], partes: float = 0.9) -> dict:
    """Dublê da resposta já validada: Nouls por registro dados, partes e global num valor só."""
    return {"supports": sup, "contradicts": con, "established": partes, "parts": {q: partes for q in P.PARTES_NOULS}}


class JevProibido:
    """Dublê que acusa qualquer chamada: prova que o caminho testado decide sem o Jev."""

    def perguntar(self, state, questions):
        raise AssertionError("o Jev foi chamado")


# ------------------------------------------------------------------------------------------ A. comparadores
COBERTURA = "coverage · statements 78.4% · branches 71.0% · functions 80.2% · lines 78.9%"
LATENCIA = "GET https://api.exemplo.com.br/imoveis/busca → 200 OK · tempo: 245 ms"
P95 = "k6 · GET /imoveis/busca · p50 120 ms · p95 310,5 ms"
REPLICAS = "swarm · prod · api-leads:1.9.3 — rollout completed · 2/3 réplicas"
# (afirmação, registro, nome do check, comparação afirmada, vale?)
COMPARADORES = [
    ("Cobertura ≥ 80%.", COBERTURA, "coverage", "statements >= 80%", False),
    ("Cobertura ≥ 78,4%.", COBERTURA, "coverage", "statements >= 78,4%", True),
    ("Cobertura ≤ 80%.", COBERTURA, "coverage", "statements <= 80%", True),
    ("Cobertura >= 80%.", COBERTURA, "coverage", "statements >= 80%", False),
    ("Cobertura <= 78.3%.", COBERTURA, "coverage", "statements <= 78.3%", False),
    ("Cobertura de pelo menos 80%.", COBERTURA, "coverage", "statements >= 80%", False),
    ("Cobertura de no mínimo 78,4%.", COBERTURA, "coverage", "statements >= 78,4%", True),
    ("Cobertura de no máximo 78,4%.", COBERTURA, "coverage", "statements <= 78,4%", True),
    ("Cobertura abaixo de 78,4%.", COBERTURA, "coverage", "statements < 78,4%", False),
    ("Cobertura acima de 78,4%.", COBERTURA, "coverage", "statements > 78,4%", False),
    ("Cobertura de branches ≥ 70,5%.", COBERTURA, "coverage", "branches >= 70,5%", True),
    ("Cobertura de linhas acima de 78,95%.", COBERTURA, "coverage", "lines > 78,95%", False),
    ("Rota responde em menos de 300 ms.", LATENCIA, "latency", "ms < 300 ms", True),
    ("Rota responde em no máximo 245 ms.", LATENCIA, "latency", "ms <= 245 ms", True),
    ("Latência abaixo de 245 ms.", LATENCIA, "latency", "ms < 245 ms", False),
    ("p95 ≤ 310 ms.", P95, "latency", "p95 <= 310 ms", False),
    ("p95 de no máximo 310,5 ms.", P95, "latency", "p95 <= 310,5 ms", True),
    ("Serviço com ≥ 3 réplicas.", REPLICAS, "replicas", "replicas >= 3 replicas", False),
    ("Serviço com pelo menos 2 réplicas.", REPLICAS, "replicas", "replicas >= 2 replicas", True),
]
for afirmacao, texto, nome, afirmado, vale in COMPARADORES:
    saida = A.checks(afirmacao, [{"id": "e1", "texto": texto}])
    confere(f"A comparador «{afirmacao}»", [(c["check"], c["claimed"], c["holds"]) for c in saida], [(nome, afirmado, vale)])

# ------------------------------------------------------------------------------------------ B. recência por assunto
DEV_OK = ("deploy", "drizzle migrate · dev · 0015_lembrete_visita aplicada")
PROD_NADA = ("deploy", "drizzle migrate · prod · No migrations to apply")
PROD_ERRO = ("deploy", "drizzle migrate · prod · ERROR: permission denied · 0015 não aplicada")

# AE-T014: prod "nada a aplicar" (sinal contra) depois de dev aplicado (sinal a favor) — ninguém supera ninguém.
st = A.state_de(caso("Migration 0015 aplicada nos dois bancos.", DEV_OK, PROD_NADA))
confere("B dev aplicado × prod nada a aplicar", A.superados(st, nouls([0.9, 0.1], [0.1, 0.6]), [0, 1]), {})
# O inverso que a revisão apontou: falha vigente em prod NÃO é apagada por sucesso posterior em dev.
st = A.state_de(caso("Migration 0015 aplicada nos dois bancos.", PROD_ERRO, DEV_OK))
v = nouls([0.05, 0.95], [0.97, 0.05])
confere("B falha em prod × sucesso posterior em dev: superados", A.superados(st, v, [0, 1]), {})
confere("B falha em prod × sucesso posterior em dev: veredito", A.compor(v, st)["relacao"], "contradicted")
# Mesmo assunto (migration 0015 em prod): o mais recente prevalece nas duas direções.
st = A.state_de(caso("Migration 0015 aplicada em prod.", PROD_ERRO, ("deploy", "drizzle migrate · prod · 0015_lembrete_visita aplicada")))
confere("B mesmo assunto, vermelho velho × verde novo", list(A.superados(st, nouls([0.05, 0.95], [0.97, 0.05]), [0, 1])), [0])
confere("B mesmo assunto, verde velho × vermelho novo", list(A.superados(st, nouls([0.95, 0.05], [0.05, 0.97]), [0, 1])), [0])
# Mesmo comando de teste, revisões diferentes (família 8 do LEIA-ME): mesmo assunto.
st = A.state_de(caso("Suíte verde.", ("log_teste", "09:50 · revisão 1c1c1c1 · vitest run — 60 passed, 1 failed"),
                     ("log_teste", "10:12 · revisão 2d2d2d2 · vitest run — 61 passed (61)")))
confere("B mesmo comando de teste", list(A.superados(st, nouls([0.1, 0.9], [0.9, 0.05]), [0, 1])), [0])
# Alvos diferentes do mesmo comando: assuntos diferentes.
st = A.state_de(caso("Testes passando.", ("log_teste", "vitest tests/agenda — 3 passed, 1 failed"), ("log_teste", "vitest tests/cobranca — 19 passed (19)")))
confere("B alvos diferentes", A.superados(st, nouls([0.1, 0.9], [0.9, 0.05]), [0, 1]), {})
# Rodada sem comando escrito: o código não sabe se é a mesma suíte — os dois ficam (a contradição antiga fica de pé).
st = A.state_de(caso("Testes passando.", ("log_teste", "08:41 · revisão 5g5g5g5 · 29 passed, 1 failed"), ("log_teste", "09:02 · revisão 6h6h6h6 · 30 passed (30)")))
v = nouls([0.1, 0.9], [0.9, 0.05])
confere("B sem assunto reconhecível: superados", A.superados(st, v, [0, 1]), {})
confere("B sem assunto reconhecível: veredito", A.compor(v, st)["relacao"], "contradicted")
# Mesma rota em hosts diferentes; mesmo serviço em ambientes diferentes.
confere("B assunto http por host", A.assunto("http_response", "GET https://homolog.exemplo.com.br/propostas → 200 OK")
        == A.assunto("http_response", "GET https://api.exemplo.com.br/propostas → 500"), False)
confere("B assunto deploy por ambiente", A.assunto("deploy_event", "swarm · homolog · api-leads:1.9.3 — rollout completed")
        == A.assunto("deploy_event", "swarm · prod · api-leads:1.9.3 — rollout completed"), False)
confere("B deploy sem ambiente não tem assunto", A.assunto("deploy_event", "mail-svc · evento m-5521 · status: delivered"), None)
confere("B manual não tem assunto", A.assunto("manual_note", "Rodei a invalidação em prod."), None)

# ------------------------------------------------------------------------------------------ C. triagem antes da chamada
# Outra revisão: fora do state, sem check dele; o registro da revisão afirmada fica.
c = caso("Testes passando na revisão b7e2f90.", ("commit", "b7e2f90 feat(propostas): parcelas com juros"),
         ("log_teste", "CI api-leads · revisão 4c1d8aa · vitest run — 52 passed (52)"))
st = A.state_de(c)
confere("C outra revisão: registros no state", [r["id"] for r in st["records"]], ["e1"])
confere("C outra revisão: checks no state", [(k["record"], k["holds"]) for k in st["checks"]], [("e1", True)])
confere("C outra revisão: motivo", A.fora_do_state(c)["neutros"], {"e2": "revision 4c1d8aa ≠ b7e2f90"})
# Outra migration, idem.
c = caso("Migration 0011 aplicada em dev.", ("deploy", "drizzle migrate · dev · 0010_origem_lead aplicada"), ("deploy", "drizzle migrate · dev · 0011_score_lead aplicada"))
confere("C outra migration: registros no state", [r["id"] for r in A.state_de(c)["records"]], ["e2"])
# Número antigo × número atual do MESMO assunto: só o atual entra; 78% de antes não contradiz 85% de agora.
c = caso("Cobertura acima de 80%.", ("log_teste", "10:00 · coverage · statements 78.4%"), ("log_teste", "10:30 · coverage · statements 85.0%"))
st = A.state_de(c)
confere("C número refeito: registros no state", [r["id"] for r in st["records"]], ["e2"])
confere("C número refeito: checks", [(k["record"], k["holds"]) for k in st["checks"]], [("e2", True)])
confere("C número refeito: não contradiz", A.compor(nouls([0.9], [0.05]), st)["relacao"], "supported")
# O inverso: o número atual é o ruim → contradito pelo atual.
c = caso("Cobertura acima de 80%.", ("log_teste", "10:00 · coverage · statements 85.0%"), ("log_teste", "10:30 · coverage · statements 78.4%"))
saida = A.compor(nouls([0.1], [0.9]), A.state_de(c))
confere("C número refeito para pior", (saida["relacao"], saida["apoio"]), ("contradicted", ["e2"]))
# Dois números sem assunto reconhecível: os dois ficam e o ruim decide (lado seguro).
c = caso("Cobertura acima de 80%.", ("log_teste", "10:00 · statements 78.4%"), ("log_teste", "10:30 · statements 85.0%"))
st = A.state_de(c)
confere("C número sem assunto: os dois ficam", [r["id"] for r in st["records"]], ["e1", "e2"])
confere("C número sem assunto: veredito", A.compor(nouls([0.1, 0.9], [0.9, 0.05]), st)["relacao"], "contradicted")
# Número em outro ambiente: o registro fica no state, mas não nasce check (nem negativo, nem positivo).
c = caso("Rota GET /imoveis/busca responde em menos de 300 ms em produção.", ("resposta_http", "GET http://localhost:3000/imoveis/busca → 200 OK · tempo: 412 ms"))
st = A.state_de(c)
confere("C localhost × produção: registro fica", [r["id"] for r in st["records"]], ["e1"])
confere("C localhost × produção: sem check", st["checks"], [])
confere("C localhost × produção: motivo", A.fora_do_state(c)["nao_pertinentes"], {"e1": "ambiente local ≠ prod"})
c = caso("api-leads 1.9.3 em produção.", ("deploy", "swarm · homolog · api-leads:1.9.2 — rollout completed"))
confere("C versão em homolog × produção: sem check", A.state_de(c)["checks"], [])
c = caso("api-leads 1.9.3 em produção.", ("deploy", "swarm · prod · api-leads:1.9.2 — rollout completed"))
confere("C versão em prod × produção: check decide", [(k["check"], k["holds"]) for k in A.state_de(c)["checks"]], [("version", False)])
c = caso("Cobertura do api-leads acima de 80%.", ("log_teste", "portal-web · coverage · statements 70.0%"))
confere("C cobertura de outro componente: sem check", A.state_de(c)["checks"], [])
# Sem ambiente afirmado, tudo é pertinente (comportamento da rodada 1).
c = caso("Rota responde em menos de 300 ms.", ("resposta_http", "GET http://localhost:3000/imoveis/busca → 200 OK · tempo: 412 ms"))
confere("C sem ambiente afirmado: check nasce", [(k["check"], k["holds"]) for k in A.state_de(c)["checks"]], [("latency", False)])

# ------------------------------------------------------------------------------------------ D. compor e chamada
# Partes altas com registro superado ainda no state: nunca `supported`; a 2ª passada é pedida.
st = A.state_de(caso("Suíte verde.", ("log_teste", "09:50 · vitest run — 60 passed, 1 failed"), ("log_teste", "10:12 · vitest run — 61 passed (61)")))
saida = A.compor(nouls([0.1, 0.9], [0.9, 0.05], partes=0.95), st)
confere("D superado no state: não aprova", saida["relacao"], P.REVISA)
confere("D superado no state: pede 2ª passada", A.precisa_segunda_passada(saida), True)
# Todos os registros de outra revisão: nenhum pertinente → insuficiente, sem chamar o Jev.
c = caso("Testes passando na revisão b7e2f90.", ("log_teste", "CI · revisão 4c1d8aa · vitest run — 52 passed (52)"))
saida = A.auditar(JevProibido(), c)
confere("D state vazio: veredito sem chamada", (saida["relacao"], saida["apoio"], saida["passada"]), ("insufficient_evidence", [], 0))
confere("D state vazio: motivo do registro", saida["neutros"], {"e1": "revision 4c1d8aa ≠ b7e2f90"})

# ------------------------------------------------------------------------------------------ E. métrica de apoio
# AE-T044: o baseline diz `supported` citando e1; o gabarito diz `contradicted` por e1 — não pontua.
gab = {"relacao": "contradicted", "registros_de_apoio": ["e1"]}
m = R.metricas_relacao([({"relacao": "supported", "apoio": ["e1"]}, gab)])
confere("E citar como sustentação quem contradiz", (m["apoio precisão"], m["apoio recall"], m["apoio exato"]), (0.0, 0.0, "0/1"))
m = R.metricas_relacao([({"relacao": "contradicted", "apoio": ["e1"]}, gab)])
confere("E mesmo registro, mesmo papel", (m["apoio precisão"], m["apoio recall"], m["apoio exato"]), (1.0, 1.0, "1/1"))
# AE-T042: em `contradicted`, o registro fora do apoio não tem rótulo de sustentação; o do apoio não sustenta.
gab = {"relacao": "contradicted", "registros_de_apoio": ["e2"]}
confere("E rótulo de sustentação em contradicted", (R.gabarito_sustenta(gab, "e1"), R.gabarito_sustenta(gab, "e2")), (None, False))
gab = {"relacao": "insufficient_evidence", "registros_de_apoio": ["e1"]}
confere("E rótulo de sustentação em insufficient", (R.gabarito_sustenta(gab, "e1"), R.gabarito_sustenta(gab, "e2")), (True, False))

if FALHAS:
    print(f"{len(FALHAS)} de {FEITAS} verificações falharam:")
    for f in FALHAS:
        print("  -", f)
    sys.exit(1)
print(f"ok: {FEITAS} verificações ({len(COMPARADORES)} frases com comparador)")
