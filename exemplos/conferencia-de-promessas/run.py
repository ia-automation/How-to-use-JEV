"""Roda a conferência num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py                 ajuste + teste (o teste só roda com o manifesto `congelamento.json` batendo)
  python run.py rascunho        só o encanamento (dados/rascunho.json → resultados-rascunho.md; não é métrica)
  python run.py ajuste          afinação (nos dois desenhos)
  python run.py congelar        roda o ajuste e grava o manifesto (hash de perguntas.py, conferir.py, run.py,
                                dados/teste.json e o critério de continuar; hash de _comum/ só como registro);
                                o manifesto anterior vai para congelamentos-anteriores/
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Cada ficha vira 1 requisição com uma Choice por afirmação que precisa do Jev; as numéricas puras não chamam
nada. O cache em `cache/` faz a segunda rodada custar zero.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import conferir as C  # noqa: E402
import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
# Congelamento (achado 1 da revisão): manifesto `congelamento.json` com hash do código executado (inclusive este
# arquivo), dos dados de teste (por bytes: hash não é leitura) e do critério de aceite. A infra comum entra só
# como registro informativo: mudar `_comum/` não recusa o teste, mas fica anotado qual versão rodou.
CONGELADOS = ["perguntas.py", "conferir.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
# Grade (CONF_MANTER, CONF_RETIRAR) para a curva cobertura × erro — mesmas respostas, zero chamada nova.
GRADE = [(0.0, 0.0), (0.5, 0.5), (0.7, 0.5), (0.8, 0.5), (0.7, 0.7), (0.9, 0.5), (0.9, 0.7), (0.9, 0.9)]
RUIM = ("contradicted", "not_stated")  # gabarito que, mantido, é promessa inventada passando


# ---------------------------------------------------------------- gabarito: famílias e numéricas (da `nota`)
def _ids(trecho: str) -> list[str]:
    """'a1, a3' ou 'a1–a3' → ['a1', 'a3'] / ['a1', 'a2', 'a3']."""
    ids = []
    for m in re.finditer(r"a(\d+)\s*[–-]\s*a(\d+)|a(\d+)", trecho):
        if m.group(1):
            ids += [f"a{i}" for i in range(int(m.group(1)), int(m.group(2)) + 1)]
        else:
            ids.append(f"a{m.group(3)}")
    return ids


def ler_nota(caso: dict) -> tuple[dict[str, list[str]], set[str]]:
    """({id: [famílias]}, {ids numéricas}). Família sem ids entre parênteses vale para as afirmações não numéricas."""
    nota = caso.get("nota") or ""
    familias: dict[str, list[str]] = {a["id"]: [] for a in caso["afirmacoes"]}
    numericas: set[str] = set()
    pendentes = []
    for parte in re.split(r";\s+(?![^()]*\))", nota):  # "; " só fora de parênteses
        parte = parte.strip()
        if parte.startswith("numérica:"):
            numericas |= set(_ids(parte))
        elif parte:
            parte = parte.removeprefix("difícil:").strip()
            m = re.match(r"^(a\d+):", parte)
            nome = "outra" if m else re.split(r"\s*\(", parte)[0].strip()
            ids = [m.group(1)] if m else _ids(parte[len(nome):])
            pendentes.append((nome, ids))
    for nome, ids in pendentes:
        for i in ids or [a["id"] for a in caso["afirmacoes"] if a["id"] not in numericas]:
            if i in familias:
                familias[i].append(nome)
    return familias, numericas


# ---------------------------------------------------------------- execução
def _falha(caso: dict, motivo: str) -> dict:
    """Saída segura de UMA ficha quando a chamada ou a resposta falhou: numéricas puras continuam pelo código; o que
    precisava do Jev fica sem relação e vai a `revisar` (nunca `manter`). Família do comparador (Codex, 2026-10-01)."""
    afirmacoes = []
    for c in C.caminhos(caso):
        if c["caminho"] == "codigo":
            rel = c["numero"]["relacao"]
            afirmacoes.append({**c, "jev": None, "relacao": rel, "conf": None, "acao": C.acao(rel, None)})
        else:
            afirmacoes.append({**c, "jev": None, "relacao": None, "conf": None, "acao": "revisar"})
    return {"id": caso["id"], "afirmacoes": afirmacoes, "modelo": None, "falha": motivo}


def rodar(casos: list[dict], desenho: str) -> tuple[list[dict], dict]:
    """Falha isolada por ficha (revisão do Codex no comparador, 2026-10-01, família): erro de rede/cache fecha SÓ
    aquela ficha em `revisar`; resposta JSON válida que a validação rejeita idem, e sai do cache (`invalidar`) para não
    ser reproduzida em toda rodada. Antes, a exceção abortava o lote inteiro."""
    jev = Jev(AQUI / "cache")  # uma instância por desenho: latência, tokens e custo separados
    pedidos = [C.pedido(c, desenho) for c in casos]

    def perguntar(p):
        try:
            return jev.perguntar(p[0], p[1])
        except Exception as e:  # noqa: BLE001 — a falha vira dado da ficha, não aborto do lote
            return e

    with ThreadPoolExecutor(8) as ex:
        respostas = list(ex.map(perguntar, [p for p in pedidos if p]))
    saidas, i, falhas = [], 0, 0
    for c, p in zip(casos, pedidos):
        r = respostas[i] if p else None
        i += bool(p)
        if isinstance(r, Exception):
            saidas.append(_falha(c, f"falha operacional: chamada ({type(r).__name__})"))
            falhas += 1
            continue
        try:
            saidas.append(C.compor(c, r, desenho))
        except Exception as e:  # noqa: BLE001 — resposta fora do contrato: fecha a ficha e tira do cache
            if hasattr(jev, "invalidar"):
                jev.invalidar(p[0], p[1])
            saidas.append(_falha(c, f"falha operacional: resposta inválida ({type(e).__name__})"))
            falhas += 1
    custo = jev.resumo()
    custo["falhas_operacionais"] = falhas
    return saidas, custo


def itens_de(saidas: list[dict], casos: list[dict]) -> list[dict]:
    """Um item por afirmação: previsto, gabarito, caminho, família, numérica (gabarito), baseline."""
    itens = []
    for s, c in zip(saidas, casos):
        familias, numericas = ler_nota(c)
        gab = {a["id"]: a["relacao"] for a in c["afirmacoes"]}
        for a in s["afirmacoes"]:
            bl = C.baseline(a["texto"], c["ficha"])
            itens.append({"caso": c["id"], "id": a["id"], "texto": a["texto"], "gabarito": gab[a["id"]],
                          "relacao": a["relacao"], "conf": a["conf"], "acao": a["acao"], "caminho": a["caminho"],
                          "jev": a["jev"], "familias": familias[a["id"]] or ["(fácil)"],
                          "numerica": a["id"] in numericas, "baseline": bl,
                          "baseline_acao": "manter" if bl == "supported" else "retirar"})
    return itens


# ---------------------------------------------------------------- métricas
def resumo(itens: list[dict], limiares: tuple[float, float] | None = None) -> dict:
    """Acerto da relação (duro), ação com limiares (cobertura, erro entre decididos), erro caro, baseline."""
    ac = {i["id"] + i["caso"]: (C.acao(i["relacao"], i["conf"], *limiares) if limiares else i["acao"]) for i in itens}
    ruins = [i for i in itens if i["gabarito"] in RUIM]
    decididos = [i for i in itens if ac[i["id"] + i["caso"]] != "revisar"]
    certo = lambda i: (ac[i["id"] + i["caso"]] == "manter") == (i["gabarito"] == "supported")  # noqa: E731
    return {
        "n": len(itens),
        "acerto_relacao": M.acerto([(i["relacao"], i["gabarito"]) for i in itens]),
        "cobertura": len(decididos) / len(itens) if itens else float("nan"),
        "erro_decididos": (1 - sum(certo(i) for i in decididos) / len(decididos)) if decididos else float("nan"),
        "revisar": len(itens) - len(decididos),
        "erro_caro": f"{sum(ac[i['id'] + i['caso']] == 'manter' for i in ruins)}/{len(ruins)}",
        "erro_caro_duro": f"{sum(i['relacao'] == 'supported' for i in ruins)}/{len(ruins)}",
        "baseline_acerto": M.acerto([(i["baseline"], i["gabarito"]) for i in itens]),
        "baseline_erro_caro": f"{sum(i['baseline_acao'] == 'manter' for i in ruins)}/{len(ruins)}",
    }


def matriz(itens: list[dict]) -> list[dict]:
    conf = M.matriz_confusao([(i["relacao"], i["gabarito"]) for i in itens])
    return [{"gabarito \\ previsto": g, **{p: conf.get((g, p), 0) for p in P.RELACOES}} for g in P.RELACOES]


def por_grupo(itens: list[dict], chave) -> list[dict]:
    grupos: dict[str, list[dict]] = {}
    for i in itens:
        for g in (i[chave] if isinstance(i[chave], list) else [i[chave]]):
            grupos.setdefault(str(g), []).append(i)
    linhas = []
    for g, sub in sorted(grupos.items()):
        r = resumo(sub)
        linhas.append({chave: g, "n": r["n"], "acerto_relacao": r["acerto_relacao"], "erro_caro": r["erro_caro"],
                       "revisar": r["revisar"], "baseline": r["baseline_acerto"]})
    return linhas


def numericas(itens: list[dict]) -> list[dict]:
    """Afirmações que o GABARITO marca como numéricas: por onde passaram e como foram."""
    nums = [i for i in itens if i["numerica"]]
    linhas = []
    for cam in ("codigo", "composta", "jev"):
        sub = [i for i in nums if i["caminho"] == cam]
        linhas.append({"caminho": cam, "n": len(sub), "acerto_relacao": M.acerto([(i["relacao"], i["gabarito"]) for i in sub]),
                       "erros": ", ".join(f"{i['caso']}/{i['id']}" for i in sub if i["relacao"] != i["gabarito"]) or "—"})
    puras = [i for i in itens if i["caminho"] == "codigo" and not i["numerica"]]
    linhas.append({"caminho": "codigo (não marcada numérica)", "n": len(puras),
                   "acerto_relacao": M.acerto([(i["relacao"], i["gabarito"]) for i in puras]),
                   "erros": ", ".join(f"{i['caso']}/{i['id']}" for i in puras if i["relacao"] != i["gabarito"]) or "—"})
    return linhas


def curva(itens: list[dict]) -> list[dict]:
    jev = [i for i in itens if i["conf"] is not None]
    linhas = []
    for lim in GRADE:
        r = resumo(jev, lim)
        linhas.append({"CONF_MANTER": lim[0], "CONF_RETIRAR": lim[1], "cobertura": r["cobertura"],
                       "erro_decididos": r["erro_decididos"], "revisar": r["revisar"], "erro_caro": r["erro_caro"]})
    return linhas


def custo(c: dict, n_fichas: int, n_afirm: int, n_jev: int) -> dict:
    if not c:
        return {"requisicoes": 0}
    return {"requisicoes": c["requisicoes"], "perguntas": c["perguntas"], "p50_ms": c["latencia_p50_ms"],
            "p95_ms": c["latencia_p95_ms"], "tokens_por_ficha": round(c["input_tokens"] / n_fichas),
            "US$_por_ficha": f"{c['custo_us'] / n_fichas:.7f}",
            "US$_por_mil_fichas": f"{1000 * c['custo_us'] / n_fichas:.4f}",
            "US$_por_mil_afirmacoes": f"{1000 * c['custo_us'] / n_afirm:.4f}",
            "afirmacoes_no_jev": f"{n_jev}/{n_afirm}", "falhas_operacionais": c.get("falhas_operacionais", 0),
            "modelo": ", ".join(c["modelos"])}


# ---------------------------------------------------------------- seções
def secao_conjunto(nome: str, dados: dict, desenhos: list[str]) -> tuple[str, dict]:
    casos = dados["casos"]
    n_afirm = sum(len(c["afirmacoes"]) for c in casos)
    out = [f"## Conjunto `{nome}` — {len(casos)} fichas, {n_afirm} afirmações (arquivo versão {dados.get('versao')}, "
           f"autor {dados.get('autor')})\n"]
    if nome == "rascunho":
        out.append("> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**\n")
    res = {"n": len(casos), "n_afirm": n_afirm, "desenhos": {}}
    saidas, custos, itens = {}, {}, {}
    for d in desenhos:
        saidas[d], custos[d] = rodar(casos, d)
        itens[d] = itens_de(saidas[d], casos)

    out.append("### Relação e ação — Jev + código × baseline, por desenho\n")
    out.append("`acerto_relacao` = relação prevista (código ou Jev, resposta dura) × gabarito, todas as afirmações. "
               f"`cobertura`/`erro_decididos`/`revisar` = ação com CONF_MANTER={P.CONF_MANTER}, CONF_RETIRAR="
               f"{P.CONF_RETIRAR}; erro entre decididos = manteve o que não é supported ou retirou o que é. "
               "`erro_caro` = gabarito contradicted/not_stated → `manter` (promessa inventada passou); `_duro` = o "
               "mesmo sem faixa (relação prevista supported). `baseline` = número + palavra de promessa + "
               "booleano da ficha + palavras na ficha, sem faixa.\n")
    linhas = []
    for d in desenhos:
        r = resumo(itens[d])
        res["desenhos"][d] = {"res": r}
        linhas.append({"desenho": d, **r})
    out.append(M.tabela(linhas) + "\n")

    padrao = P.DESENHO_PADRAO if P.DESENHO_PADRAO in desenhos else desenhos[0]
    it = itens[padrao]
    out.append(f"### Matriz gabarito × previsto — `{padrao}`\n")
    out.append(M.tabela(matriz(it)) + "\n")

    out.append(f"### Por caminho (código puro / composta / Jev) — `{padrao}`\n")
    out.append("`codigo` = número comparado em código, sem chamada; `composta` = número bate e o resto foi ao Jev "
               "(número contradito decide sozinho); `jev` = só a Choice.\n")
    out.append(M.tabela(por_grupo(it, "caminho")) + "\n")

    out.append(f"### Numéricas do gabarito (nota `numérica`) — por onde passaram — `{padrao}`\n")
    lin = numericas(it)
    res["numericas"] = lin
    out.append(M.tabela(lin) + "\n")

    out.append(f"### Por família difícil (nota `difícil`) — `{padrao}`\n")
    out.append(M.tabela(por_grupo(it, "familias")) + "\n")

    for d in desenhos:
        out.append(f"### Cobertura × erro por limiares (só afirmações julgadas pelo Jev) — `{d}`\n")
        out.append(M.tabela(curva(itens[d])) + "\n")

    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    out.append("Latência por REQUISIÇÃO (= por ficha com alguma afirmação no Jev). Mil fichas = mil rascunhos "
               "conferidos. As numéricas puras custam zero.\n")
    linhas = []
    for d in desenhos:
        k = custo(custos[d], len(casos), n_afirm, sum(i["conf"] is not None for i in itens[d]))
        res["desenhos"][d]["custo"] = k
        linhas.append({"desenho": d, **k})
    out.append(M.tabela(linhas) + "\n")

    out.append(f"### Caso a caso — `{padrao}`" + (f" (`{[x for x in desenhos if x != padrao][0]}` entre parênteses)" if len(desenhos) > 1 else "") + "\n")
    out.append("`jev` = opção vencedora (confiança); `tópico` = Noul auxiliar quando ligado. `marca`: `caro` = promessa "
               "inventada mantida; `erro` = ação decidida errada; `rel` = relação errada mas ação certa ou em revisão.\n")
    linhas = []
    outro = next((d for d in desenhos if d != padrao), None)
    for idx, i in enumerate(it):
        i2 = itens[outro][idx] if outro else None
        if i["jev"]:
            jv = f"{i['jev']['relacao']} ({i['jev']['conf']:.2f})"
            if i2 and i2["jev"]:
                jv += f" ({i2['jev']['relacao']} {i2['jev']['conf']:.2f}" + (f", tópico {i2['jev']['topico']:.2f})" if "topico" in i2["jev"] else ")")
        else:
            jv = "—"
        num = i["jev"] is None or i["caminho"] == "composta"
        cod = "; ".join(f"{p['dim']} {p['comparador']} {p['valor']:g} × {p['ficha'] if p['ficha'] is None else format(p['ficha'], 'g')} → {p['relacao']}"
                        for p in (next((a for a in saidas[padrao][[c["id"] for c in casos].index(i["caso"])]["afirmacoes"]
                                        if a["id"] == i["id"]))["numero"] or {}).get("partes", [])) if num else "—"
        caro = i["gabarito"] in RUIM and i["acao"] == "manter"
        erro = i["acao"] != "revisar" and not caro and ((i["acao"] == "manter") != (i["gabarito"] == "supported"))
        rel = i["relacao"] != i["gabarito"] and not caro and not erro
        linhas.append({"id": i["caso"], "af": i["id"], "afirmação": i["texto"], "caminho": i["caminho"], "código": cod,
                       "jev": jv, "relação": i["relacao"], "gab": i["gabarito"], "ação": i["acao"],
                       "bl": i["baseline"][:4], "marca": "caro" if caro else ("erro" if erro else ("rel" if rel else "—"))})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), res


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Relação, ação e erro caro — Jev + código × baseline\n"]
    linhas = []
    for nome, r in resumos.items():
        for d, v in r["desenhos"].items():
            s = v["res"]
            linhas.append({"conjunto": nome, "desenho": d, "afirmações": s["n"], "acerto_relacao": s["acerto_relacao"],
                           "baseline": s["baseline_acerto"], "cobertura": s["cobertura"],
                           "erro_decididos": s["erro_decididos"], "revisar": s["revisar"], "erro_caro": s["erro_caro"],
                           "erro_caro_duro": s["erro_caro_duro"], "baseline_erro_caro": s["baseline_erro_caro"]})
    out.append(M.tabela(linhas) + "\n")
    out.append("### Numéricas pelo código, latência e custo\n")
    linhas = []
    for nome, r in resumos.items():
        cod = next(l for l in r["numericas"] if l["caminho"] == "codigo")
        for d, v in r["desenhos"].items():
            k = v["custo"]
            linhas.append({"conjunto": nome, "desenho": d, "fichas": r["n"], "numéricas_código": f"{cod['n']} ({cod['acerto_relacao']:.3f})",
                           "requisicoes": k.get("requisicoes"), "p50_ms": k.get("p50_ms"), "p95_ms": k.get("p95_ms"),
                           "tokens_por_ficha": k.get("tokens_por_ficha"), "US$_por_ficha": k.get("US$_por_ficha"),
                           "US$_por_mil_fichas": k.get("US$_por_mil_fichas"), "modelo": k.get("modelo")})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; cega ou não, conforme a rodada declarada no README): {h}"


def _congelar() -> dict:
    """Grava o manifesto pela infra comum e anota, só como registro, o hash da infra comum que rodou."""
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
        (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    return m


def _criterio_md() -> str:
    c = P.CRITERIO_CONTINUAR
    itens = [(k.split("_", 1), v) for k, v in c.items() if k != "onde"]
    return c["onde"] + ": " + "; ".join(f"({n}) {nome.replace('_', ' ')} {v}" for (n, nome), v in itens) + "."


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if "teste" in conjuntos:
        # O teste só roda com pergunta, código, dados E critério congelados: o manifesto gravado ANTES tem de bater.
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
        # Rascunho vai para um arquivo à parte (achado 1): não sobrescreve o resultado do teste nem o congelamento.
        texto, _ = secao_conjunto("rascunho", json.loads((AQUI / "dados" / "rascunho.json").read_text(encoding="utf-8")),
                                  list(P.DESENHOS))
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — conferencia-de-promessas (encanamento)\n\n{texto}",
                                                     encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        arquivo = AQUI / "dados" / f"{nome}.json"
        desenhos = [P.DESENHO_PADRAO] if nome == "teste" else list(P.DESENHOS)  # o teste roda só o desenho escolhido
        texto, resumos[nome] = secao_conjunto(nome, json.loads(arquivo.read_text(encoding="utf-8")), desenhos)
        partes.append(texto)
    cabecalho = (f"# Resultados — conferencia-de-promessas\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, limiares, "
                 f"glosas e baseline: `perguntas.py`; comparação numérica e composição: `conferir.py`. Preço: US$ 0,042 "
                 f"por milhão de tokens de entrada. Desenho padrão: `{P.DESENHO_PADRAO}`; CONF_MANTER {P.CONF_MANTER}, "
                 f"CONF_RETIRAR {P.CONF_RETIRAR}.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    RESULTADOS.write_text(cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes), encoding="utf-8",
                          newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")


if __name__ == "__main__":
    main()
