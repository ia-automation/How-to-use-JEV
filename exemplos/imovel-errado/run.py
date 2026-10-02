"""Roda o "imóvel errado" num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, referente.py,
                             run.py, dados/teste.json e o critério de continuar; hash de _comum/ só como registro);
                             o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por conversa (Choice + 3 Nouls juntos); conversa acima do teto não é enviada (pedir, contada à
parte). O cache em `cache/` faz rodar de novo custar zero.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
import referente as R  # noqa: E402
from jevcache import Jev  # noqa: E402

ACOES = R.ACOES
RESULTADOS = AQUI / "resultados.md"
# Congelamento (achado 1): manifesto com hash do código executado (inclusive este arquivo), dos dados de teste e do
# critério de aceite. `_comum/` entra só como registro: mudar a infra comum não recusa o teste, mas fica anotado.
CONGELADOS = ["perguntas.py", "referente.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
LIMIARES_CONF = [0.0, 0.3, 0.5, 0.7, 0.9]
# Grade para a curva cobertura × erro (zero chamada nova): piso da Choice × faixa dos Nouls do rascunho.
GRADE_CONF = [0.0, 0.5, 0.7, 0.9]
GRADE_FAIXA = [(0.5, 0.5), (0.3, 0.7), (0.2, 0.8)]
VARIANTES = ["baseline (último citado)", "sempre pergunta", "Jev"]
# Família difícil pela `nota` do rotulador (LEIA-ME: começa com "difícil: <família>"); ordem = tabela do LEIA-ME.
FAMILIAS = [("troca de foco", "troca de foco no meio"), ("citação", "citação de fala antiga"),
            ("parecidos", "dois imóveis parecidos"), ("vaga", "referência vaga"), ("correção", "correção do cliente"),
            ("só um", "atributo que só um tem"), ("dois têm", "atributo que dois têm (null)"),
            ("elíptica", "pergunta elíptica")]


def familia(caso: dict) -> str:
    nota = caso.get("nota") or ""
    if nota.startswith("difícil"):
        return next((nome for chave, nome in FAMILIAS if chave in nota), "difícil: outra")
    return "outro nulo (fora da lista / geral)" if caso["referente"] is None else "fácil / outros"


def acao_esperada(c: dict) -> str:
    """Gabarito da ação: referente nulo → pedir; rascunho usa outro → trocar; senão manter."""
    if c["referente"] is None:
        return "pedir_esclarecimento"
    return "trocar_referente" if c["rascunho_usa_outro"] else "manter"


def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    """Uma requisição por conversa dentro do teto; conversa longa (achado 6) vira `pedir` sem chamada, contada à parte."""
    jev = Jev(AQUI / "cache")  # uma instância por conjunto: latência e tokens separados
    pedidos = [R.pedido(c) for c in casos]  # candidatos inválidos = erro aqui, antes de qualquer chamada (achado 2)
    longas = [R.conversa_longa(st) for st, _ in pedidos]
    respostas = jev.perguntar_varios([p for p, m in zip(pedidos, longas) if m is None])
    saidas, it = [], iter(respostas)
    for (st, _), motivo in zip(pedidos, longas):
        saidas.append(R.decisao_longa(motivo) if motivo else R.decidir(next(it), st["candidates"]))
    custo = jev.resumo() or {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
                             "input_tokens": 0, "custo_us": 0.0, "modelos": []}
    custo["conversas_longas"] = sum(m is not None for m in longas)
    return saidas, custo


def saida_variante(s: dict, c: dict, variante: str) -> dict:
    """{acao, referente, sugestao, usa_outro} de cada variante sobre o MESMO caso."""
    if variante.startswith("baseline"):
        return R.baseline(R.state_de(c))
    if variante == "sempre pergunta":
        return {"acao": "pedir_esclarecimento", "referente": None, "sugestao": None, "usa_outro": None}
    return {"acao": s["acao"], "referente": s["referente_decidido"], "sugestao": s["sugestao"], "usa_outro": s["usa_outro"]}


def usa_outro_previsto(s: dict) -> bool | None:
    """Resposta dura de `rascunho_usa_outro`, sem olhar o gabarito: Noul relacional se o referente foi decidido,
    Noul "se compromete com um" se não foi. Conversa longa (sem chamada) não prevê: None."""
    if s.get("longa"):
        return None
    q = "draft_uses_other" if s["referente_decidido"] is not None else "draft_commits_to_one"
    return s["nouls"][q] >= 0.5


def metricas_acao(itens: list[tuple[dict, dict]]) -> dict:
    """itens = [(saída da variante, caso)]. Respostas erradas que iriam ao cliente, somadas no critério 1:
    erro caro (rascunho que usa outro imóvel → `manter`), troca sugerindo candidato errado e — achado 4 da
    revisão — candidato sugerido/mantido quando o gabarito é nulo (o cliente não identificou de qual fala)."""
    pares = [(v["acao"], acao_esperada(c)) for v, c in itens]
    usam = [v for v, c in itens if c["rascunho_usa_outro"]]
    nao_nulos = [(v, c) for v, c in itens if c["referente"] is not None]
    nulos = [v for v, c in itens if c["referente"] is None]
    certos = [(v, c) for v, c in nao_nulos if not c["rascunho_usa_outro"]]
    erro_caro = sum(v["acao"] == "manter" for v in usam)
    troca_errada = sum(v["acao"] == "trocar_referente" and v["sugestao"] != c["referente"] for v, c in nao_nulos)
    nulo_candidato = sum(v["acao"] != "pedir_esclarecimento" for v in nulos)  # manter ou trocar = assumiu um candidato
    return {
        "n": len(itens),
        "acerto_acao": M.acerto(pares),
        "ERRO CARO (usa outro → manter)": f"{erro_caro}/{len(usam)}",
        "troca p/ candidato errado": f"{troca_errada}/{len(nao_nulos)}",
        "sugeriu candidato c/ gabarito nulo": f"{nulo_candidato}/{len(nulos)}",
        "RESPOSTA ERRADA (soma)": f"{erro_caro + troca_errada + nulo_candidato}/{len(itens)}",
        "pediu sem necessidade": f"{sum(v['acao'] == 'pedir_esclarecimento' for v, _ in nao_nulos)}/{len(nao_nulos)}",
        "trocou sem necessidade": f"{sum(v['acao'] == 'trocar_referente' for v, _ in certos)}/{len(certos)}",
        "nulo → pedir": f"{sum(v['acao'] == 'pedir_esclarecimento' for v in nulos)}/{len(nulos)}",
        "acerto_referente (c/ nulo)": M.acerto([(v["referente"], c["referente"]) for v, c in itens]) if not all(v["referente"] is None for v, _ in itens) else 0.0,
    }


def matriz(pares: list[tuple[str, str]]) -> str:
    cont = Counter((g, p) for p, g in pares)
    return M.tabela([{"gabarito ↓ / previsto →": g, **{a: cont[(g, a)] for a in ACOES}} for g in ACOES])


def _redecidir(s: dict, c: dict) -> dict:
    """Re-decide com as constantes atuais de `perguntas` a partir dos números guardados (sem cache nem API)."""
    resposta = {"answers": {"referent": {"choice": s["referente"] or P.NEI, "confidence": s["conf"], "probabilities": s["probs"]},
                            **{q: {"noul": v} for q, v in s["nouls"].items()}}}
    return R.decidir(resposta, R.state_de(c)["candidates"])


def curva(saidas: list[dict], casos: list[dict]) -> list[dict]:
    """Cobertura automática (não pediu esclarecimento) × erro entre automáticos, por piso da Choice × faixa dos
    Nouls do rascunho. Troca as constantes no laço (o que um humano faria editando o arquivo) e restaura."""
    antes = P.REFERENTE_CONF_MIN, P.FAIXA
    linhas = []
    try:
        for piso in GRADE_CONF:
            for faixa in GRADE_FAIXA:
                P.REFERENTE_CONF_MIN, P.FAIXA = piso, {q: faixa for q in P.FAIXA}
                ss = [s if s.get("longa") else _redecidir(s, c) for s, c in zip(saidas, casos)]
                auto = [(s, c) for s, c in zip(ss, casos) if s["acao"] != "pedir_esclarecimento"]
                linhas.append({"piso_choice": piso, "faixa_nouls": f"{faixa[0]}–{faixa[1]}",
                               "atual": "←" if (piso, faixa) == (antes[0], antes[1]["draft_uses_other"]) else "",
                               "cobertura_auto": len(auto) / len(casos),
                               "erro_automatico": (sum(s["acao"] != acao_esperada(c) for s, c in auto) / len(auto)) if auto else float("nan"),
                               "erros_caros": sum(s["acao"] == "manter" and c["rascunho_usa_outro"] for s, c in auto),
                               "n_auto": len(auto)})
    finally:
        P.REFERENTE_CONF_MIN, P.FAIXA = antes
    return linhas


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custo = rodar(casos)
    itens = {v: [(saida_variante(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    nulos = sum(c["referente"] is None for c in casos)
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    resumo = {"n": len(casos), "nulos": nulos, "dificeis": dificeis, "variantes": {v: metricas_acao(itens[v]) for v in VARIANTES},
              "custo": custo}

    out = [f"## Conjunto `{nome}` — {len(casos)} conversas (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{nulos} com referente nulo, {dificeis} difíceis\n"]
    if nome == "rascunho":
        out.append("> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**\n")

    out.append("### Ação — métrica principal, baseline × sempre pergunta × Jev nos mesmos casos\n")
    out.append("Gabarito da ação: referente nulo → `pedir_esclarecimento`; `rascunho_usa_outro` → `trocar_referente`; senão "
               "`manter`. **Erro caro** = rascunho que usa fato de outro imóvel e recebeu `manter` (a resposta errada iria ao "
               "cliente). `troca p/ candidato errado` = trocou sugerindo outro que não o referente do gabarito. `sugeriu candidato "
               "c/ gabarito nulo` = o gabarito exige esclarecimento e a saída foi `manter`/`trocar_referente` (assumiu um imóvel que "
               "o cliente não identificou; achado 4 da revisão). **RESPOSTA ERRADA (soma)** = os três somados, sobre n: é o "
               "critério 1. `sempre pergunta` = o custo de evitar todo erro: zero resposta errada, 100% das conversas "
               "interrompidas. `acerto_referente` compara o referente decidido (nulo = pediu) com o gabarito, nulo incluído.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES]) + "\n")
    out.append("**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto)\n")
    out.append(matriz([(v["acao"], acao_esperada(c)) for v, c in itens["Jev"]]) + "\n")
    out.append("**Matriz de confusão — baseline**\n")
    out.append(matriz([(v["acao"], acao_esperada(c)) for v, c in itens["baseline (último citado)"]]) + "\n")

    # --- referente: Choice crua, com nulo e sem
    out.append("### Referente — Choice crua (vencedor; válvula = nulo), antes dos portões\n")
    pares_todos = [(s["referente"], c["referente"]) for s, c in zip(saidas, casos)]
    pares_nn = [(s["referente"], c["referente"]) for s, c in zip(saidas, casos) if c["referente"] is not None]
    nulos_valvula = sum(s["referente"] is None for s, c in zip(saidas, casos) if c["referente"] is None)
    nn_valvula = sum(s["referente"] is None for s, c in zip(saidas, casos) if c["referente"] is not None)
    base_pares = [(v["referente"], c["referente"]) for v, c in itens["baseline (último citado)"]]
    resumo["referente"] = {"jev_todos": M.acerto(pares_todos), "jev_nao_nulos": M.acerto(pares_nn), "baseline_todos": M.acerto(base_pares),
                           "nulo→válvula": f"{nulos_valvula}/{nulos}", "não nulo→válvula": f"{nn_valvula}/{len(pares_nn)}"}
    out.append(M.tabela([{"acerto Jev (c/ nulo)": M.acerto(pares_todos), "acerto Jev (só não nulos)": M.acerto(pares_nn),
                          "acerto baseline (c/ nulo)": M.acerto(base_pares),
                          "nulo → válvula": f"{nulos_valvula}/{nulos}", "não nulo → válvula (perda)": f"{nn_valvula}/{len(pares_nn)}",
                          "piso atual": P.REFERENTE_CONF_MIN}]) + "\n")
    out.append("**Cobertura × erro por confiança da Choice** (todos os casos; `erro` = vencedor ≠ gabarito, nulo incluído)\n")
    out.append(M.tabela(M.cobertura_erro([(s["conf"], s["referente"] == c["referente"]) for s, c in zip(saidas, casos)], LIMIARES_CONF)) + "\n")

    # --- Nouls
    out.append("### Nouls — acerto (≥ 0,5) no subconjunto que cada um decide, faixa atual e Brier\n")
    linhas = []
    com_jev = [(s, c) for s, c in zip(saidas, casos) if not s.get("longa")]  # conversa longa não tem Noul (não foi enviada)
    sub = {"unambiguous_reference": [(s["nouls"]["unambiguous_reference"], c["referente"] is not None) for s, c in com_jev],
           "draft_uses_other": [(s["nouls"]["draft_uses_other"], c["rascunho_usa_outro"]) for s, c in com_jev if c["referente"] is not None],
           "draft_commits_to_one": [(s["nouls"]["draft_commits_to_one"], c["rascunho_usa_outro"]) for s, c in com_jev if c["referente"] is None]}
    faixas = {"unambiguous_reference": (P.UNAMBIGUOUS_MIN or 0.0, P.UNAMBIGUOUS_MIN or 0.0), **P.FAIXA}
    for q, it in sub.items():
        nao, sim = faixas[q]
        linhas.append({"noul": q, "subconjunto": {"unambiguous_reference": "todos (gabarito = referente não nulo)",
                                                   "draft_uses_other": "referente não nulo", "draft_commits_to_one": "referente nulo"}[q],
                       "acerto": M.acerto([(v >= 0.5, g) for v, g in it]), "faixa": f"{nao}–{sim}", **M.faixa_noul(it, nao, sim), "brier": M.brier(it)})
    out.append(M.tabela(linhas) + "\n")
    usa_pares = [(usa_outro_previsto(s), c["rascunho_usa_outro"]) for s, c in zip(saidas, casos)]
    base_usa = [(v["usa_outro"], c["rascunho_usa_outro"]) for v, c in itens["baseline (último citado)"]]
    resumo["usa_outro"] = {"jev": M.acerto(usa_pares), "baseline": M.acerto(base_usa)}
    out.append(f"**`rascunho_usa_outro` composto** (relacional se o referente foi decidido, senão \"se compromete com um\"; ≥ 0,5): "
               f"Jev {M.acerto(usa_pares):.3f} · baseline por palavra-chave {M.acerto(base_usa):.3f} (n = {len(casos)})\n")

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador)\n")
    linhas = []
    for fam in dict.fromkeys([nome_f for _, nome_f in FAMILIAS] + ["difícil: outra", "outro nulo (fora da lista / geral)", "fácil / outros"]):
        grupo = [(s, c) for s, c in zip(saidas, casos) if familia(c) == fam]
        if not grupo:
            continue
        linhas.append({"família": fam, "n": len(grupo),
                       "referente Jev": M.acerto([(s["referente"], c["referente"]) for s, c in grupo]),
                       "referente baseline": M.acerto([(R.baseline(R.state_de(c))["referente"], c["referente"]) for _, c in grupo]),
                       "ação Jev": M.acerto([(s["acao"], acao_esperada(c)) for s, c in grupo]),
                       "ação baseline": M.acerto([(R.baseline(R.state_de(c))["acao"], acao_esperada(c)) for _, c in grupo]),
                       "erros caros Jev": sum(s["acao"] == "manter" and c["rascunho_usa_outro"] for s, c in grupo)})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curva
    out.append("### Cobertura automática × erro por piso da Choice e faixa dos Nouls (mesmas respostas; informativo no teste)\n")
    out.append(M.tabela(curva(saidas, casos)) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    out.append(M.tabela([{"requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "conversas_longas (sem chamada)": custo["conversas_longas"], "perguntas": custo["perguntas"],
                          "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_conversa": round(custo["input_tokens"] / max(custo["requisicoes"], 1)),
                          "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_1000_conversas": f"{1000 * custo['custo_us'] / max(custo['requisicoes'], 1):.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("`ref` = vencedor da Choice (confiança); `unamb`/`usa`/`comp` = Nouls `unambiguous_reference`, `draft_uses_other`, "
               "`draft_commits_to_one`; `ok` compara a ação do Jev com o gabarito; `base` = ação do baseline.\n")
    linhas = []
    f2 = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731 — conversa longa não tem números (não foi enviada)
    for s, c in zip(saidas, casos):
        b = R.baseline(R.state_de(c))
        gab = acao_esperada(c)
        linhas.append({"id": c["id"], "fam": familia(c).split(" (")[0], "gab ref": c["referente"] or "null", "usa_outro": c["rascunho_usa_outro"],
                       "ref": f"{s['referente'] or 'null'} ({f2(s['conf'])})", "unamb": f2(s["nouls"]["unambiguous_reference"]),
                       "usa": f2(s["nouls"]["draft_uses_other"]), "comp": f2(s["nouls"]["draft_commits_to_one"]),
                       "ação Jev": s["acao"], "gab ação": gab, "ok": "✓" if s["acao"] == gab else "✗",
                       "base": f"{b['acao']} ({b['referente'] or 'null'})", "motivo": s["motivo"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Ação por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES]) + "\n")
    out.append("### Referente, rascunho, custo\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "nulos": r["nulos"], "difíceis": r["dificeis"],
                          "referente Jev (c/ nulo)": r["referente"]["jev_todos"], "referente Jev (não nulos)": r["referente"]["jev_nao_nulos"],
                          "referente baseline": r["referente"]["baseline_todos"], "nulo→válvula": r["referente"]["nulo→válvula"],
                          "usa_outro Jev": r["usa_outro"]["jev"], "usa_outro baseline": r["usa_outro"]["baseline"],
                          "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_conversa": round(r["custo"]["input_tokens"] / r["custo"]["requisicoes"]),
                          "US$_por_1000": f"{1000 * r['custo']['custo_us'] / r['custo']['requisicoes']:.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; cega ou não, conforme a rodada declarada no README): {h}"


def _congelar() -> dict:
    """Grava o manifesto pela infra comum e anota, só como registro, o hash da infra comum que rodou."""
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
        (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    c = P.CRITERIO_CONTINUAR
    return f"{c['onde']}: (1) {c['1_resposta_errada_ao_cliente']}; (2) acerto do referente {c['2_acerto_referente']}. Secundário: {c['secundario_nao_decide']}."


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if "teste" in conjuntos:
        # O teste só roda com perguntas, política, dados E critério congelados: o manifesto gravado ANTES tem de bater.
        try:
            manifesto = CG.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != P.CRITERIO_CONTINUAR:
            sys.exit("teste recusado: o critério de continuar mudou desde o congelamento (rode `run.py congelar`)")
        linha = _linha_manifesto(manifesto)
    elif congelar:
        linha = _linha_manifesto(_congelar())
    else:
        h = CG.hashes(AQUI, CONGELADOS)
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())
    if args == ["rascunho"]:
        texto, _ = secao_conjunto("rascunho", json.loads((AQUI / "dados" / "rascunho.json").read_text(encoding="utf-8")))
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — imovel-errado (encanamento)\n\n{texto}", encoding="utf-8",
                                                     newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — imovel-errado\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas e política: "
                 f"`perguntas.py`; comparativos, validação e ação: `referente.py`. Preço: US$ 0,042 por milhão de tokens de "
                 f"entrada. Teto da conversa: {P.TETO_TURNOS} turnos / {P.TETO_CARACTERES} caracteres (acima → pedir, sem chamada).\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    RESULTADOS.write_text(cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes), encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")


if __name__ == "__main__":
    main()
