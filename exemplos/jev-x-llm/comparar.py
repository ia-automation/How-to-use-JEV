"""Jev × LLM no MESMO teste congelado de três exemplos: carrega cada exemplo, manda o mesmo pedido (state + perguntas de
`perguntas.py`, em JSON) a um LLM barato, injeta a resposta na regra de decisão do PRÓPRIO exemplo e mede com as
funções de métrica do PRÓPRIO `run.py` dele. Nada de regra replicada: `optout.guardar_seguro`, `motivo.julgar_seguro`
e `auditor.auditar` rodam com um adaptador no lugar do cliente do Jev.

Como a injeção funciona (`ViaLLM`): o LLM responde Noul = true/false e Choice = opção; o adaptador converte para o
formato JSON da API do Jev (Noul → 1,0/0,0; Choice → one-hot com confiança 1,0) e a validação estrita do exemplo
(`congelamento.noul/choice`) e a decisão rodam sem mudar. Consequência declarada: o LLM não tem faixa de dúvida —
`revisar` só sai dele por guarda ou regra de código, nunca por valor no meio.

Os três exemplos têm `perguntas.py` e `run.py` com o mesmo nome de módulo: `carregar` importa cada um isolado
(troca `sys.modules` e `sys.path` só durante o import) e devolve um namespace por exemplo.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

AQUI = Path(__file__).resolve().parent
EXEMPLOS = AQUI.parent
sys.path.insert(0, str(EXEMPLOS / "_comum"))

import congelamento as CG  # noqa: E402
import criterio as CR  # noqa: E402
import metricas as M  # noqa: E402
from jevcache import PRECO_US_POR_MILHAO_ENTRADA as PRECO_JEV  # noqa: E402
from jevcache import Jev  # noqa: E402
import llmcache as L  # noqa: E402
from llmcache import LLM, LoteInterrompido, RespostaInvalida, esquema_de  # noqa: E402

# Módulo de decisão de cada exemplo (o que recebe o cliente e devolve a decisão).
MODULO = {"opt-out-lgpd": "optout", "motivo-de-perda": "motivo", "auditor-de-evidencia": "auditor"}
NOMES = list(MODULO)

# O ÚNICO texto que o LLM recebe além do pedido do Jev: explica as duas primitivas (que o Jev tem embutidas) e o formato
# da resposta. Sem exemplos, sem pedido de raciocínio, igual para os três exemplos.
SISTEMA = (
    "You answer questions about a JSON `state`. The input is a JSON object with two keys: `state` (the data) and "
    "`questions` (a map from question id to a question about `state`). Each question has a `type`:\n"
    "- `noul`: a yes/no judgement. Answer `true` if the statement in `instructions` holds for `state`, `false` otherwise; "
    "`criteria.true` describes when the answer is true and `criteria.false` when it is false.\n"
    "- `choice`: pick exactly one of the keys of THAT question's own `criteria` (each key's value describes when it applies). "
    "Questions differ in their keys: a key that is not in the question's own `criteria` is not a valid answer. If none of "
    "the keys fits well, still answer with the one that fits best — never invent a key. Answer with that key as a string.\n"
    "Names between backticks in a question are paths inside `state`. Answer every question independently of the others, "
    "using only `state` and that question's own text. Reply with ONLY a JSON object of the form "
    "{\"answers\": {\"<question id>\": <answer>}} — one entry per question id, no prose, no Markdown, no extra keys."
)


# ---------------------------------------------------------------------------------------- carregar exemplo
def carregar(nome: str) -> SimpleNamespace:
    """Namespace `{nome, pasta, P (perguntas), D (decisão), R (run do exemplo)}`, importado isolado dos outros."""
    pasta = EXEMPLOS / nome
    nomes = ["perguntas", MODULO[nome], "run"]
    guardados = {m: sys.modules.pop(m) for m in nomes if m in sys.modules}
    sys.path.insert(0, str(pasta))
    try:
        P = importlib.import_module("perguntas")
        D = importlib.import_module(MODULO[nome])
        R = importlib.import_module("run")
    finally:
        sys.path.remove(str(pasta))
        for m in nomes:
            sys.modules.pop(m, None)
        sys.modules.update(guardados)
    return SimpleNamespace(nome=nome, pasta=pasta, P=P, D=D, R=R)


def conferir_dados(ex: SimpleNamespace) -> dict:
    """O teste do exemplo é intocado: TODO arquivo do manifesto do exemplo (código, teste.json, taxonomia) tem o hash gravado."""
    manifesto = json.loads((ex.pasta / CG.MANIFESTO).read_text(encoding="utf-8"))
    return CG.conferir(ex.pasta, list(manifesto["arquivos"]))


def dados(ex: SimpleNamespace, conjunto: str) -> dict:
    return json.loads((ex.pasta / "dados" / f"{conjunto}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------- adaptador
def montar_prompt(state, questions: dict) -> str:
    """O pedido do Jev, tal qual, serializado: o LLM vê exatamente o que o Jev viu."""
    return json.dumps({"state": state, "questions": questions}, ensure_ascii=False, indent=1)


def sintetizar(answers: dict, questions: dict, modelo: str) -> dict:
    """Respostas do LLM → formato JSON da API do Jev, para a validação e a decisão do exemplo rodarem sem mudar."""
    out = {}
    for q, p in questions.items():
        v = answers[q]
        if p["type"] == "noul":
            out[q] = {"type": "noul", "noul": 1.0 if v else 0.0}
        else:
            out[q] = {"type": "choice", "choice": v, "confidence": 1.0,
                      "probabilities": {o: (1.0 if o == v else 0.0) for o in p["criteria"]}}
    return {"model": modelo, "answers": out, "usage": None}


class ViaLLM:
    """Faz o papel do cliente do Jev (`perguntar(state, questions)`), respondido pelo LLM. `invalidar` é no-op: a
    resposta inválida nunca entra no cache do LLM (ver `llmcache`).

    `tolerar(answers, violacoes, questions)`: leitura SECUNDÁRIA, declarada, só para o relatório — devolve True quando as
    violações estão todas em perguntas que a decisão do exemplo nunca lê; aí o valor inválido vira a primeira opção da
    pergunta (um placeholder num campo descartado, como o Jev também descarta as suas respostas especulativas) e o caso é
    decidido. Sem `tolerar` (o padrão, e o que o critério julga) toda violação é falha operacional."""

    def __init__(self, llm: LLM, tolerar=None):
        self.llm, self.tolerar, self.toleradas = llm, tolerar, 0

    def perguntar(self, state, questions: dict) -> dict:
        try:
            answers = self.llm.perguntar(SISTEMA, montar_prompt(state, questions), esquema_de(questions))
        except RespostaInvalida as e:
            if not (self.tolerar and e.obj and self.tolerar(e.obj["answers"], e.violacoes, questions)):
                raise
            answers = {q: (next(iter(questions[q]["criteria"])) if q in e.violacoes else v) for q, v in e.obj["answers"].items()}
            self.toleradas += 1
        return sintetizar(answers, questions, self.llm.modelo)

    def invalidar(self, state, questions: dict) -> bool:
        return False

    def resumo(self) -> dict:
        return self.llm.resumo()


def _em_serie(via: ViaLLM, casos: list, um) -> list:
    """Uma chamada por vez (sem paralelo). Um 429 repetido ou orçamento esgotado interrompe o lote AQUI: os invólucros
    dos exemplos engolem toda exceção como falha operacional, por isso o sinal vem pelo cliente."""
    saidas = []
    for c in casos:
        saidas.append(um(c))
        if via.llm.interrompido:
            raise LoteInterrompido(via.llm.interrompido)
    return saidas


# ---------------------------------------------------------------------------------------- um bloco por exemplo
def _b(x: float) -> bool:
    return x >= 0.5


def rodar_optout(ex, casos: list, jev, via) -> dict:
    R, D = ex.R, ex.D
    s_jev = [D.guardar_seguro(jev, c["mensagem"]) for c in casos]
    s_llm = _em_serie(via, casos, lambda c: D.guardar_seguro(via, c["mensagem"]))
    # A marca `falha` vai até a métrica (revisão do Codex, achado 3): `saida_variante` do exemplo a descartava e uma falha
    # operacional (→ `revisar`) pontuava quando o gabarito era `revisar`. Critério congelado: falha = erro.
    saida = lambda s, c: {**R.saida_variante(s, c, "Jev"), "falha": bool(s.get("falha"))}  # noqa: E731
    lados = {"Jev": [(saida(s, c), c) for s, c in zip(s_jev, casos)],
             "LLM": [(saida(s, c), c) for s, c in zip(s_llm, casos)],
             "baseline": [({**R.saida_variante(None, c, "baseline (expressões)"), "falha": False}, c) for c in casos]}
    met = {k: R.metricas_acao(v) for k, v in lados.items()}
    gab = [R.acao_esperada(c) for c in casos]
    caro = lambda v, c: R.obrigacao_perdida(v, c) or ("bloqueio indevido" if v["bloqueia"] is True and c["opt_out"] is False and c["pedido_lgpd"] is False else "")  # noqa: E731
    acertos = {k: sum(v["acao"] == g and not v["falha"] for (v, _), g in zip(lados[k], gab)) for k in lados}
    for k in lados:  # a coluna de acerto do exemplo recebe o número com a falha fora do numerador
        met[k]["acerto_acao"] = met[k]["_bruto"]["acerto"] = acertos[k] / len(casos)
    caros = {k: sum(bool(caro(v, c)) for v, c in lados[k]) for k in lados}
    # concordância: decisão final (ação + tipo) e, por pergunta, o sinal binário (Jev ≥ 0,5 × LLM); falha não concorda
    dec = sum(not a["falha"] and not b["falha"] and (a["acao"], a["tipo_lgpd"]) == (b["acao"], b["tipo_lgpd"])
              for (a, _), (b, _) in zip(lados["Jev"], lados["LLM"]))
    perg = [0, 0]
    for a, b in zip(s_jev, s_llm):
        if R.sem_numeros(a) or R.sem_numeros(b):
            continue
        for q in ex.P.NOULS:
            perg[0] += _b(a["nouls"][q]) == _b(b["nouls"][q])
            perg[1] += 1
        perg[0] += a["tipo_escolha"] == b["tipo_escolha"]
        perg[1] += 1
    linhas = []
    for (vj, c), (vl, _), (vb, _), l, g in zip(lados["Jev"], lados["LLM"], lados["baseline"], s_llm, gab):
        f = lambda v: v["acao"] + (f"({v['tipo_lgpd']})" if v["tipo_lgpd"] else "")  # noqa: E731
        ok = lambda v: "✗F" if v["falha"] else "✓" if v["acao"] == g else "✗"  # noqa: E731
        linhas.append({"id": c["id"], "fam": R.familia(c), "gab": g + (f"({c['tipo_lgpd']})" if c["tipo_lgpd"] else ""),
                       "Jev": f(vj), "ok J": ok(vj), "caro J": caro(vj, c),
                       "LLM": f(vl), "ok L": ok(vl), "caro L": caro(vl, c),
                       "base": f(vb), "ok B": ok(vb),
                       "LLM: nouls opt·pausa·lgpd·cont·s/obj·terc / tipo": ("—" if R.sem_numeros(l) else
                                                                              "·".join("S" if _b(l["nouls"][q]) else "n" for q in ex.P.NOULS) + f" / {l['tipo_escolha']}"),
                       "motivo LLM": l["motivo"]})
    return {"n": len(casos), "metricas": met, "colunas": R.COLUNAS_ACAO, "acertos": acertos, "caros": caros,
            "falhas_llm": sum(bool(s.get("falha")) for s in s_llm), "falhas_jev": sum(bool(s.get("falha")) for s in s_jev),
            "concordancia": dec, "concordancia_perguntas": tuple(perg), "casos": linhas,
            "legenda": "erro caro = infração (opt-out/LGPD real → seguir) + obrigação pela metade + bloqueio indevido; "
                       "`caro` na tabela nomeia a perda. ✗F = falha operacional (não pontua, mesmo com gabarito `revisar`). "
                       "Sinais do LLM: S = true, n = false, na ordem dos 6 Nouls; tipo = Choice."}


def rodar_motivo(ex, casos: list, jev, via) -> dict:
    R, D, P = ex.R, ex.D, ex.P
    tax = json.loads((ex.pasta / "dados" / "taxonomia.json").read_text(encoding="utf-8"))["casos"]
    D.validar_taxonomia(tax)
    s_jev = [D.julgar_seguro(jev, c.get("conversa"), tax, variante=P.VARIANTE_PRINCIPAL) for c in casos]
    s_llm = _em_serie(via, casos, lambda c: D.julgar_seguro(via, c.get("conversa"), tax, variante=P.VARIANTE_PRINCIPAL))
    # Leitura secundária (declarada; não decide): o rascunho mostrou o LLM respondendo `only_group` na Choice de folhas de
    # `sem_informacao` — a única sem essa válvula — quando outro grupo vence; a decisão (variante c) só lê a Choice do grupo
    # VENCEDOR, então a violação está num campo que ninguém consome. Tolera SÓ esse caso: toda violação em `leaf.<g>` com
    # g ≠ grupo escolhido (e o grupo válido). Mesmo cache, modo `gravado`: zero chamada nova.
    def especulativa(answers: dict, violacoes: list[str], questions: dict) -> bool:
        g = answers.get("group")
        return isinstance(g, str) and g in questions["group"]["criteria"] and all(q.startswith("leaf.") and q != f"leaf.{g}" for q in violacoes)
    via_tol = ViaLLM(LLM(via.llm.pasta, modo="gravado"), tolerar=especulativa)
    s_tol = [D.julgar_seguro(via_tol, c.get("conversa"), tax, variante=P.VARIANTE_PRINCIPAL) for c in casos]
    v = P.VARIANTE_PRINCIPAL
    lados = {"Jev": [(R.escolha(s, c, v, tax), c) for s, c in zip(s_jev, casos)],
             "LLM": [(R.escolha(s, c, v, tax), c) for s, c in zip(s_llm, casos)],
             "LLM tolerante (secundária)": [(R.escolha(s, c, v, tax), c) for s, c in zip(s_tol, casos)],
             "baseline": [(R.escolha(s, c, R.BASE, tax), c) for s, c in zip(s_jev, casos)]}
    met = {k: R.metricas(x) for k, x in lados.items()}
    acertos = {k: met[k]["_bruto"]["folha"] + met[k]["_bruto"]["aceitavel"] + met[k]["_bruto"]["so_grupo"] for k in lados}
    caros = {k: met[k]["_bruto"]["grupo_errado_auto"] for k in lados}
    secundario = {"lado": "LLM tolerante (secundária)", "toleradas": via_tol.toleradas,
                  "o_que": "violação só em Choice de folhas de grupo não vencedor (campo que a decisão não lê) → caso decidido; "
                           "qualquer outra violação continua falha. Não é o critério: só mostra o julgamento que a regra estrita esconde"}
    dec = sum(not a["falha"] and not b["falha"] and (a["grupo"], a["folha"], a["revisar"]) == (b["grupo"], b["folha"], b["revisar"])
              for (a, _), (b, _) in zip(lados["Jev"], lados["LLM"]))
    perg = [0, 0]
    for a, b in zip(s_jev, s_llm):
        if not (R.vivo(a) and R.vivo(b)):
            continue
        xa, xb = a["sinais"]["tudo"], b["sinais"]["tudo"]
        perg[0] += xa["grupo"] == xb["grupo"]
        perg[1] += 1
        for g in tax:
            perg[0] += xa["folhas"][g["id"]]["folha"] == xb["folhas"][g["id"]]["folha"]
            perg[1] += 1
        for k in P.NOULS:
            perg[0] += _b(xa["nouls"][k]) == _b(xb["nouls"][k])
            perg[1] += 1
    cel = lambda d, c: f"{d['grupo']}/{d['folha'] or '∅'} {R.MARCA[R.classe(d, c)]}"  # noqa: E731
    linhas = []
    for (dj, c), (dl, _), (dt, _), (db, _), l, t in zip(lados["Jev"], lados["LLM"], lados["LLM tolerante (secundária)"], lados["baseline"], s_llm, s_tol):
        sinais = "—"
        if R.vivo(t):  # os sinais da leitura tolerante (iguais aos da estrita quando ela não falhou)
            x = t["sinais"]["tudo"]
            sinais = f"{x['grupo']} › {x['folhas'][x['grupo']]['folha'] or P.SO_GRUPO} · " + "·".join("S" if _b(x["nouls"][k]) else "n" for k in P.NOULS)
        linhas.append({"id": c["id"], "fam": R.familia(c), "gabarito": f"{c['grupo']}/{c['folha'] or '∅'}",
                       "outras aceitáveis": " ".join(a for a in c["aceitaveis"] if a != c["folha"]) or "—",
                       "Jev": cel(dj, c), "LLM": cel(dl, c), "LLM tol.": cel(dt, c), "base": cel(db, c),
                       "LLM: grupo › folha · reason·blames·closed": sinais, "motivo LLM (estrita)": l["motivo"]})
    return {"n": len(casos), "metricas": met, "colunas": [c for c in R.COLUNAS if c not in ("req/caso", "tokens/caso", "US$/1000", "p50_ms", "p95_ms")],
            "acertos": acertos, "caros": caros, "secundario": secundario,
            "falhas_llm": sum(not R.vivo(s) for s in s_llm), "falhas_jev": sum(not R.vivo(s) for s in s_jev),
            "concordancia": dec, "concordancia_perguntas": tuple(perg), "casos": linhas,
            "legenda": "erro caro = grupo errado automatizado (inclui motivo inventado). Marcas: " +
                       " · ".join(f"{m} {k}" for k, m in R.MARCA.items()) + ". Sinais do LLM: Choice do grupo › Choice de folhas desse grupo; "
                       "S/n = os 3 Nouls reason_stated·blames_agency·closed_elsewhere."}


def rodar_auditor(ex, casos: list, jev, via) -> dict:
    R, D, P = ex.R, ex.D, ex.P

    def auditar(cliente, c):
        try:
            return {**D.auditar(cliente, c), "falha": False}
        except Exception as e:  # noqa: BLE001 — falha fechada: nunca `supported`
            return {"relacao": P.REVISA, "apoio": [], "superados": {}, "falha": True, "passada": 0,
                    "motivo": f"falha operacional ({type(e).__name__})"}

    s_jev = [auditar(jev, c) for c in casos]
    s_llm = _em_serie(via, casos, lambda c: auditar(via, c))
    lados = {"Jev": [(s, c) for s, c in zip(s_jev, casos)], "LLM": [(s, c) for s, c in zip(s_llm, casos)],
             "baseline": [(D.baseline(D.state_bruto(c)), c) for c in casos]}
    met = {k: R.metricas_relacao(x) for k, x in lados.items()}
    # falha (→ `revisa`, marca preservada) fora do numerador de acerto e da concordância (critério: falha = erro)
    acertos = {k: sum(s["relacao"] == c["relacao"] and not s.get("falha") for s, c in lados[k]) for k in lados}
    for k in lados:
        met[k]["acerto (revisa=erro)"] = acertos[k] / len(casos)
    caros = {k: sum(s["relacao"] == "supported" and c["relacao"] != "supported" for s, c in lados[k]) for k in lados}
    dec = sum(not a.get("falha") and not b.get("falha") and a["relacao"] == b["relacao"] for (a, _), (b, _) in zip(lados["Jev"], lados["LLM"]))
    perg = [0, 0]
    for a, b in zip(s_jev, s_llm):
        if a["falha"] or b["falha"] or "supports" not in a or "supports" not in b or len(a["supports"]) != len(b["supports"]):
            continue
        for k in ("supports", "contradicts"):
            for x, y in zip(a[k], b[k]):
                perg[0] += _b(x) == _b(y)
                perg[1] += 1
        perg[0] += _b(a["established"]) == _b(b["established"])
        perg[1] += 1
        for q in P.PARTES_NOULS:
            perg[0] += _b(a["parts"][q]) == _b(b["parts"][q])
            perg[1] += 1
    linhas = []
    for (sj, c), (sl, _), (sb, _) in zip(lados["Jev"], lados["LLM"], lados["baseline"]):
        fa = lambda s: "FALSA APROVAÇÃO" if s["relacao"] == "supported" and c["relacao"] != "supported" else ""  # noqa: E731
        sinais = "—"
        if "supports" in sl:
            sinais = " ".join(f"{'S' if _b(x) else 'n'}/{'C' if _b(y) else 'n'}" for x, y in zip(sl["supports"], sl["contradicts"])) \
                + f" · est {'S' if _b(sl['established']) else 'n'} · partes " + "".join("S" if _b(x) else "n" for x in sl["parts"].values())
        ok = lambda s: "✗F" if s.get("falha") else "✓" if s["relacao"] == c["relacao"] else "✗"  # noqa: E731
        linhas.append({"id": c["id"], "fam": R.familia(c).split(" ")[0], "gab": c["relacao"],
                       "Jev": sj["relacao"], "ok J": ok(sj), "caro J": fa(sj),
                       "LLM": sl["relacao"], "ok L": ok(sl), "caro L": fa(sl),
                       "base": sb["relacao"], "ok B": "✓" if sb["relacao"] == c["relacao"] else "✗",
                       "LLM: sup/con por registro · established · partes": sinais, "motivo LLM": sl["motivo"]})
    return {"n": len(casos), "metricas": met, "colunas": None, "acertos": acertos, "caros": caros,
            "falhas_llm": sum(s["falha"] for s in s_llm), "falhas_jev": sum(s["falha"] for s in s_jev),
            "concordancia": dec, "concordancia_perguntas": tuple(perg), "casos": linhas,
            "legenda": "erro caro = FALSA APROVAÇÃO (gabarito insufficient_evidence ou contradicted → supported). Sinais do LLM por "
                       "registro: S = sustenta, C = contradiz, n = não; est = established; partes = object·state·place·scope."}


RODAR = {"opt-out-lgpd": rodar_optout, "motivo-de-perda": rodar_motivo, "auditor-de-evidencia": rodar_auditor}


# ---------------------------------------------------------------------------------------- veredito e custo
def veredito(b: dict) -> dict:
    """Aplica o critério congelado (gerado, não escrito à mão): ganha / empata / perde com diferença e n."""
    e = CR.CRITERIO["limites"]["empate_casos"]
    d = b["acertos"]["LLM"] - b["acertos"]["Jev"]
    dc = b["caros"]["LLM"] - b["caros"]["Jev"]
    return {"principal": "ganha" if d >= e else "perde" if d <= -e else "empata",
            "principal_diferenca": d, "erro_caro": "ganha" if dc < 0 else "perde" if dc > 0 else "empata", "erro_caro_diferenca": dc}


def custo(resumo: dict, n: int, preco_entrada: float, preco_saida: float) -> dict:
    """US$ por mil CASOS (não por requisição: um caso sem chamada custa zero) e tokens por caso."""
    r = resumo or {}
    entrada, saida = r.get("input_tokens", 0), r.get("output_tokens", 0)
    total = entrada / 1e6 * preco_entrada + saida / 1e6 * preco_saida
    return {"requisições": r.get("requisicoes", 0), "novas (não cache)": r.get("requisicoes", 0) - r.get("do_cache", 0),
            "respostas inválidas": r.get("invalidas", 0), "tentativas HTTP": r.get("tentativas_http", "—"),
            "p50_ms": r.get("latencia_p50_ms", 0), "p95_ms": r.get("latencia_p95_ms", 0),
            "tokens entrada/caso": round(entrada / max(n, 1)), "tokens saída/caso": round(saida / max(n, 1)),
            "US$ total": f"{total:.4f}", "US$/1000 casos": f"{1000 * total / max(n, 1):.4f}", "_us_1000": 1000 * total / max(n, 1),
            "modelo": ", ".join(r.get("modelos", []))}


def comparar(ex: SimpleNamespace, casos: list, pasta_cache_llm: Path, orcamento) -> dict:
    """Um exemplo: Jev só do cache (0 chamadas, `gravado` forçado), LLM pelo adaptador com o orçamento persistido
    (`llmcache.Orcamento`); devolve o bloco medido."""
    jev = Jev(ex.pasta / "cache", modo="gravado")
    llm = LLM(pasta_cache_llm, orcamento=orcamento)
    via = ViaLLM(llm)
    bloco = RODAR[ex.nome](ex, casos, jev, via)  # LoteInterrompido sobe daqui para quem roda
    bloco["custo"] = {"Jev": custo(jev.resumo(), len(casos), PRECO_JEV, 0.0),
                      "LLM": custo(llm.resumo(), len(casos), L.PRECO_US_POR_MILHAO_ENTRADA, L.PRECO_US_POR_MILHAO_SAIDA)}
    bloco["tentativas_http"] = llm.tentativas_http
    bloco["veredito"] = veredito(bloco)
    return bloco


# ---------------------------------------------------------------------------------------- relatório
def _sem_bruto(m: dict) -> dict:
    return {k: v for k, v in m.items() if not k.startswith("_")}


def secao(nome: str, b: dict) -> str:
    c = CR.CRITERIO["exemplos"][nome]
    v, n = b["veredito"], b["n"]
    j, l, base = b["acertos"]["Jev"], b["acertos"]["LLM"], b["acertos"]["baseline"]
    cj, cl, cb = b["caros"]["Jev"], b["caros"]["LLM"], b["caros"]["baseline"]
    razao_custo = b["custo"]["LLM"]["_us_1000"] / b["custo"]["Jev"]["_us_1000"] if b["custo"]["Jev"]["_us_1000"] else float("nan")
    razao_lat = b["custo"]["LLM"]["p50_ms"] / b["custo"]["Jev"]["p50_ms"] if b["custo"]["Jev"]["p50_ms"] else float("nan")
    out = [f"## `{nome}` — {n} casos do teste congelado\n",
           f"Métrica principal: **{c['metrica_principal']}**. Erro caro: **{c['erro_caro']}**. Baseline: {c['baseline']}.\n",
           "### Métricas do próprio exemplo (funções do `run.py` dele), Jev × LLM × baseline nos mesmos casos\n",
           M.tabela([{"lado": k, **_sem_bruto(m)} for k, m in b["metricas"].items()], (["lado", *b["colunas"][1:]] if b["colunas"] else None)) + "\n",
           "### Veredito pelo critério congelado (gerado pelo script)\n",
           M.tabela([
               {"o quê": "métrica principal (acertos)", "Jev": f"{j}/{n} ({j / n:.3f})", "LLM": f"{l}/{n} ({l / n:.3f})",
                "baseline": f"{base}/{n} ({base / n:.3f})", "LLM − Jev": f"{v['principal_diferenca']:+d} casos", "o LLM": f"**{v['principal']}**"},
               {"o quê": "erro caro (contagem)", "Jev": str(cj), "LLM": str(cl), "baseline": str(cb),
                "LLM − Jev": f"{v['erro_caro_diferenca']:+d}", "o LLM": f"**{v['erro_caro']}**"},
               {"o quê": "falha operacional", "Jev": str(b["falhas_jev"]), "LLM": str(b["falhas_llm"]), "baseline": "0", "LLM − Jev": "", "o LLM": ""},
           ], ["o quê", "Jev", "LLM", "baseline", "LLM − Jev", "o LLM"]) + "\n",
           f"Veredito: na métrica principal o LLM **{v['principal']}** ({v['principal_diferenca']:+d} casos em n = {n}; empate abaixo de "
           f"{CR.EMPATE_CASOS}); no erro caro o LLM **{v['erro_caro']}** ({cl} × {cj}). Razão de custo LLM ÷ Jev: **{razao_custo:.0f}×** "
           f"(US$ {b['custo']['LLM']['US$/1000 casos']} × {b['custo']['Jev']['US$/1000 casos']} por mil casos); razão de latência (p50): "
           f"**{razao_lat:.1f}×** ({b['custo']['LLM']['p50_ms']} × {b['custo']['Jev']['p50_ms']} ms).\n",
           *([f"Leitura secundária **{b['secundario']['lado']}** ({b['secundario']['toleradas']} casos tolerados; {b['secundario']['o_que']}): "
              f"acertos {b['acertos'][b['secundario']['lado']]}/{n} ({b['acertos'][b['secundario']['lado']] / n:.3f}) × Jev {j}/{n} "
              f"({b['acertos'][b['secundario']['lado']] - j:+d} casos); erro caro {b['caros'][b['secundario']['lado']]} × Jev {cj}.\n"]
             if "secundario" in b else []),
           f"Concordância Jev × LLM: decisão final igual em **{b['concordancia']}/{n}** ({b['concordancia'] / n:.3f}); por pergunta "
           f"(Jev ≥ 0,5 × LLM true, Choice = mesma opção) {b['concordancia_perguntas'][0]}/{b['concordancia_perguntas'][1]} "
           f"({(b['concordancia_perguntas'][0] / b['concordancia_perguntas'][1]) if b['concordancia_perguntas'][1] else float('nan'):.3f}).\n",
           "### Custo e latência (medidos na chamada real; do cache também)\n",
           M.tabela([{"lado": k, **{x: y for x, y in m.items() if not x.startswith('_')}} for k, m in b["custo"].items()]) + "\n",
           "### Caso a caso\n", b["legenda"] + "\n", M.tabela(b["casos"]) + "\n"]
    return "\n".join(out)


def resumo_geral(blocos: dict) -> str:
    linhas = []
    for nome, b in blocos.items():
        v, n = b["veredito"], b["n"]
        linhas.append({"exemplo": nome, "n": n, "principal Jev": f"{b['acertos']['Jev'] / n:.3f}", "principal LLM": f"{b['acertos']['LLM'] / n:.3f}",
                       "principal baseline": f"{b['acertos']['baseline'] / n:.3f}", "LLM − Jev (casos)": f"{v['principal_diferenca']:+d}",
                       "LLM na principal": v["principal"], "erro caro Jev": b["caros"]["Jev"], "erro caro LLM": b["caros"]["LLM"],
                       "erro caro baseline": b["caros"]["baseline"], "LLM no erro caro": v["erro_caro"], "falha op. LLM": b["falhas_llm"],
                       "p50 Jev/LLM ms": f"{b['custo']['Jev']['p50_ms']}/{b['custo']['LLM']['p50_ms']}",
                       "p95 Jev/LLM ms": f"{b['custo']['Jev']['p95_ms']}/{b['custo']['LLM']['p95_ms']}",
                       "US$/1000 Jev": b["custo"]["Jev"]["US$/1000 casos"], "US$/1000 LLM": b["custo"]["LLM"]["US$/1000 casos"],
                       "concordância": f"{b['concordancia']}/{n}"})
    return M.tabela(linhas)
