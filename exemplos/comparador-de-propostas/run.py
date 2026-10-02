"""Roda o comparador num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py                 ajuste + teste (o teste só roda com o manifesto `congelamento.json` batendo)
  python run.py rascunho        só o encanamento (dados/rascunho.json → resultados-rascunho.md; não é métrica)
  python run.py ajuste          afinação (nos dois desenhos)
  python run.py congelar        roda o ajuste e grava o manifesto (hash de perguntas.py, comparador.py, run.py,
                                dados/teste.json e o critério de continuar; hash de _comum/ só como registro)
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Cada PROPOSTA vira 1 requisição com uma pergunta por requisito semântico (Choice) ou duas (Nouls); as células
numéricas são do código e não chamam nada. Orçamento declarado: ≤ 400 requisições no teste (60 propostas × 1
desenho = 60). O cache em `cache/` faz a segunda rodada custar zero.
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import comparador as C  # noqa: E402
import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
CONGELADOS = ["perguntas.py", "comparador.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
ORCAMENTO_TESTE = 400  # requisições; o teste aborta antes de chamar se o pedido passar disso
# Grade para a curva cobertura × erro (mesmas respostas, zero chamada nova).
GRADE_CHOICE = [(0.0, 0.0), (0.5, 0.5), (0.7, 0.5), (0.8, 0.5), (0.7, 0.7), (0.9, 0.5), (0.9, 0.7), (0.9, 0.9)]
GRADE_NOULS = [(0.5, 0.5), (0.7, 0.5), (0.7, 0.7), (0.8, 0.5), (0.9, 0.5), (0.9, 0.7)]  # (sim entrega, sim exclui); nao = 0,3

# ---------------------------------------------------------------- critério de continuar / descartar
# Fixado ANTES de abrir o teste (2026-10-01), a partir do ajuste; entra no manifesto `congelamento.json`. Falhar
# um item = o desenho não serve como está; o teste não se repete para consertar. Os erros caros contam à parte:
# (3) exclusão escondida aprovada = gabarito `contradiz` semântico lido como `atende` (compra a proposta errada);
# (4) inelegível marcada elegível = proposta com `contradiz` obrigatório no gabarito que entra na lista.
CRITERIO_CONTINUAR = {
    "onde": "no teste (20 disputas, 60 propostas), com o desenho padrão e os limiares de perguntas.py",
    "1_numericas": "células numéricas pelo código 100% (menos é bug)",
    "2_acerto_semantico": "células semânticas (Jev, com válvula) ≥ baseline + 15 p.p.",
    "3_exclusao_aprovada": "gabarito contradiz semântico → atende ≤ 5% dessas células",
    "4_inelegivel_elegivel": "proposta inelegível no gabarito dentro de `elegiveis` ≤ 10% das inelegíveis",
    "5_elegiveis_exatos": "lista `elegiveis` igual ao gabarito em ≥ 70% das disputas",
}


def veredito(res: dict) -> list[dict]:
    """Calcula cada item do critério sobre o resumo de um conjunto; `passa` por item e no total."""
    r, b = res["res"], res["res"]
    linhas = [
        {"item": "1_numericas", "valor": f"{r['acerto_numerico']:.3f} ({r['n_num']})", "passa": r["acerto_numerico"] >= 1.0},
        {"item": "2_acerto_semantico", "valor": f"{r['acerto_semantico']:.3f} × baseline {b['baseline_semantico']:.3f}",
         "passa": r["acerto_semantico"] >= b["baseline_semantico"] + 0.15},
        {"item": "3_exclusao_aprovada", "valor": r["exclusao_aprovada"], "passa": _fracao(r["exclusao_aprovada"]) <= 0.05},
        {"item": "4_inelegivel_elegivel", "valor": r["inelegivel_elegivel"], "passa": _fracao(r["inelegivel_elegivel"]) <= 0.10},
        {"item": "5_elegiveis_exatos", "valor": f"{r['elegiveis_exatos']:.3f}", "passa": r["elegiveis_exatos"] >= 0.70},
    ]
    return linhas


def _fracao(texto: str) -> float:
    a, b = texto.split("/")
    return int(a) / int(b) if int(b) else 0.0


# ---------------------------------------------------------------- execução
def rodar(casos: list[dict], desenho: str) -> tuple[list[dict], dict]:
    """Uma requisição por proposta, em paralelo (a trava do cache é por pedido); falha fecha em nao_informado."""
    # Estrutura conferida ANTES de qualquer chamada (revisão do Codex, achado 2): dado rotulado quebrado aborta aqui,
    # com a lista do que está errado, e não no meio do lote.
    problemas = [f"{c.get('id') if isinstance(c, dict) else k}: {'; '.join(e)}" for k, c in enumerate(casos) if (e := C.validar_disputa(c))]
    if problemas:
        raise ValueError("estrutura dos dados: " + " | ".join(problemas))
    jev = Jev(AQUI / "cache")  # uma instância por desenho: latência, tokens e custo separados
    pares = [(c, p) for c in casos for p in c["propostas"]]
    with ThreadPoolExecutor(8) as ex:
        saidas = list(ex.map(lambda cp: C.comparar_proposta_seguro(jev, cp[0], cp[1], desenho), pares))
    por_caso, i = [], 0
    for c in casos:
        props = saidas[i:i + len(c["propostas"])]
        i += len(c["propostas"])
        matriz = {s["id"]: s["celulas"] for s in props}
        por_caso.append({"id": c["id"], "matriz": matriz, "elegiveis": C.elegiveis(c, matriz),
                         "perguntas": C.perguntas_ao_fornecedor(c, matriz), "propostas": props,
                         "falhas": [s["falha"] for s in props if s.get("falha")]})
    custo = jev.resumo()
    custo["falhas_operacionais"] = sum(len(s["falhas"]) for s in por_caso)
    return por_caso, custo


def familia(caso: dict) -> str:
    nota = caso.get("nota") or ""
    return nota.split("—")[0].removeprefix("difícil:").strip() if nota.startswith("difícil") else "fácil"


def itens_de(saidas: list[dict], casos: list[dict], desenho: str) -> list[dict]:
    """Um item por célula: previsto, bruto (antes da válvula), confiança/Nouls, gabarito, baseline, família."""
    itens = []
    for s, c in zip(saidas, casos):
        reqs = {r["id"]: r for r in c["requisitos"]}
        for p, sp in zip(c["propostas"], s["propostas"]):
            for rid, cel in sp["celulas"].items():
                d = sp["detalhes"][rid]
                itens.append({"caso": c["id"], "pid": p["id"], "rid": rid, "tipo": reqs[rid]["tipo"],
                              "obrigatorio": reqs[rid]["obrigatorio"], "requisito": reqs[rid]["texto"],
                              "gabarito": c["matriz"][p["id"]][rid], "celula": cel, "detalhe": d, "desenho": desenho,
                              "familia": familia(c), "baseline": C.baseline_celula(reqs[rid], p),
                              "falha": bool(sp.get("falha"))})
    return itens


def celula_com(item: dict, lim: tuple | None) -> str:
    """Recalcula a célula com outros limiares (curva), sem chamada nova."""
    d = item["detalhe"]
    if lim is None or d["origem"] != "jev":
        return item["celula"]
    if item["desenho"] == "choice":
        return C.valvula_choice({v: k for k, v in P.CELULA_DA_OPCAO.items()}[d["bruto"]], d["conf"], *lim)
    return C.combinar_nouls(d["entrega"], d["exclui"], (P.FAIXA_ENTREGA[0], lim[0]), (P.FAIXA_EXCLUI[0], lim[1]))


def abstencao(item: dict, lim: tuple | None) -> bool:
    """A válvula (Choice) ou a faixa (Nouls) mandou para nao_informado o que a leitura dura decidia (achado 5: os
    Nouls não registravam `bruto` e a cobertura saía 1,000 por construção)."""
    d = item["detalhe"]
    return d["origem"] == "jev" and celula_com(item, lim) == "nao_informado" and d["bruto"] != "nao_informado"


# ---------------------------------------------------------------- métricas
def _elegiveis_por_proposta(itens: list[dict], casos: list[dict], lim: tuple | None) -> list[dict]:
    """Por proposta: elegível no gabarito × previsto (recalculado da matriz prevista com os limiares dados)."""
    por = {}
    for i in itens:
        por.setdefault((i["caso"], i["pid"]), {})[i["rid"]] = celula_com(i, lim)
    out = []
    for c in casos:
        obrig = [r["id"] for r in c["requisitos"] if r["obrigatorio"]]
        for p in c["propostas"]:
            m = por[(c["id"], p["id"])]
            prev = not any(m[r] == "contradiz" for r in obrig)
            gab = p["id"] in c["elegiveis"]
            out.append({"caso": c["id"], "pid": p["id"], "gab": gab, "prev": prev})
    return out


def resumo(itens: list[dict], casos: list[dict], lim: tuple | None = None) -> dict:
    sem = [i for i in itens if i["tipo"] == "semantico"]
    num = [i for i in itens if i["tipo"] == "numerico"]
    cel = {id(i): celula_com(i, lim) for i in itens}
    contradiz = [i for i in sem if i["gabarito"] == "contradiz"]
    ni = [i for i in sem if i["gabarito"] == "nao_informado"]
    atende = [i for i in sem if i["gabarito"] == "atende"]
    valvula = [i for i in sem if abstencao(i, lim)]
    decididos = [i for i in sem if i not in valvula]
    props = _elegiveis_por_proposta(itens, casos, lim)
    inel = [p for p in props if not p["gab"]]
    eleg = [p for p in props if p["gab"]]
    exatos = [all(p["gab"] == p["prev"] for p in props if p["caso"] == c["id"]) for c in casos]
    # perguntas: célula nao_informado em obrigatório, SÓ de proposta elegível — no gabarito para `perg_gab`, na
    # previsão para `perg_prev` (achado 3: a saída não pergunta a fornecedor inelegível; a métrica contava).
    eleg_gab = {(p["caso"], p["pid"]) for p in props if p["gab"]}
    eleg_prev = {(p["caso"], p["pid"]) for p in props if p["prev"]}
    perg_gab = {(i["caso"], i["pid"], i["rid"]) for i in itens
                if i["obrigatorio"] and i["gabarito"] == "nao_informado" and (i["caso"], i["pid"]) in eleg_gab}
    perg_prev = {(i["caso"], i["pid"], i["rid"]) for i in itens
                 if i["obrigatorio"] and cel[id(i)] == "nao_informado" and (i["caso"], i["pid"]) in eleg_prev}
    return {
        "n_sem": len(sem), "n_num": len(num),
        "acerto_semantico": M.acerto([(cel[id(i)], i["gabarito"]) for i in sem]),
        "acerto_numerico": M.acerto([(cel[id(i)], i["gabarito"]) for i in num]),
        "acerto_total": M.acerto([(cel[id(i)], i["gabarito"]) for i in itens]),
        "classe_atende": M.acerto([(cel[id(i)], i["gabarito"]) for i in atende]),
        "classe_contradiz": M.acerto([(cel[id(i)], i["gabarito"]) for i in contradiz]),
        "classe_nao_informado": M.acerto([(cel[id(i)], i["gabarito"]) for i in ni]),
        "exclusao_aprovada": f"{sum(cel[id(i)] == 'atende' for i in contradiz)}/{len(contradiz)}",
        "exclusao_aprovada_bruto": f"{sum(i['detalhe'].get('bruto') == 'atende' for i in contradiz)}/{len(contradiz)}",
        "descartou_sem_perguntar": f"{sum(cel[id(i)] == 'contradiz' for i in ni)}/{len(ni)}",
        "falso_alarme": f"{sum(cel[id(i)] == 'contradiz' for i in atende)}/{len(atende)}",
        "valvula": len(valvula),
        "cobertura": len(decididos) / len(sem) if sem else float("nan"),
        "erro_decididos": (1 - M.acerto([(cel[id(i)], i["gabarito"]) for i in decididos])) if decididos else float("nan"),
        "inelegivel_elegivel": f"{sum(p['prev'] for p in inel)}/{len(inel)}",
        "elegivel_fora": f"{sum(not p['prev'] for p in eleg)}/{len(eleg)}",
        "elegiveis_exatos": sum(exatos) / len(exatos) if exatos else float("nan"),
        "perguntas_precisao": len(perg_gab & perg_prev) / len(perg_prev) if perg_prev else float("nan"),
        "perguntas_recall": len(perg_gab & perg_prev) / len(perg_gab) if perg_gab else float("nan"),
        "baseline_semantico": M.acerto([(i["baseline"], i["gabarito"]) for i in sem]),
        "baseline_exclusao_aprovada": f"{sum(i['baseline'] == 'atende' for i in contradiz)}/{len(contradiz)}",
        "falhas": len({(i["caso"], i["pid"]) for i in itens if i["falha"]}),
    }


def matriz_confusao(itens: list[dict]) -> list[dict]:
    sem = [i for i in itens if i["tipo"] == "semantico"]
    conf = M.matriz_confusao([(i["celula"], i["gabarito"]) for i in sem])
    return [{"gabarito \\ previsto": g, **{p: conf.get((g, p), 0) for p in P.CELULAS}} for g in P.CELULAS]


def por_familia(itens: list[dict], casos: list[dict]) -> list[dict]:
    linhas = []
    for f in sorted({i["familia"] for i in itens}):
        sub = [i for i in itens if i["familia"] == f]
        r = resumo(sub, [c for c in casos if familia(c) == f])
        linhas.append({"família": f, "disputas": sum(familia(c) == f for c in casos), "células_sem": r["n_sem"],
                       "acerto_semantico": r["acerto_semantico"], "exclusao_aprovada": r["exclusao_aprovada"],
                       "descartou_sem_perguntar": r["descartou_sem_perguntar"], "elegiveis_exatos": r["elegiveis_exatos"],
                       "baseline": r["baseline_semantico"]})
    return linhas


def curva(itens: list[dict], casos: list[dict], desenho: str) -> list[dict]:
    linhas = []
    for lim in (GRADE_CHOICE if desenho == "choice" else GRADE_NOULS):
        r = resumo(itens, casos, lim)
        nome = ("CONF_ATENDE", "CONF_CONTRADIZ") if desenho == "choice" else ("SIM_ENTREGA", "SIM_EXCLUI")
        linhas.append({nome[0]: lim[0], nome[1]: lim[1], "acerto_semantico": r["acerto_semantico"], "cobertura": r["cobertura"],
                       "erro_decididos": r["erro_decididos"], "valvula": r["valvula"], "exclusao_aprovada": r["exclusao_aprovada"],
                       "descartou_sem_perguntar": r["descartou_sem_perguntar"], "inelegivel_elegivel": r["inelegivel_elegivel"],
                       "elegiveis_exatos": r["elegiveis_exatos"]})
    return linhas


def custo(c: dict, n_disputas: int, n_propostas: int) -> dict:
    if not c.get("requisicoes"):
        return {"requisicoes": 0, "falhas_operacionais": c.get("falhas_operacionais", 0)}
    return {"requisicoes": c["requisicoes"], "perguntas": c["perguntas"], "p50_ms": c["latencia_p50_ms"],
            "p95_ms": c["latencia_p95_ms"], "tokens_por_proposta": round(c["input_tokens"] / n_propostas),
            "US$_por_disputa": f"{c['custo_us'] / n_disputas:.6f}",
            "US$_por_mil_disputas": f"{1000 * c['custo_us'] / n_disputas:.4f}",
            "falhas_operacionais": c["falhas_operacionais"], "modelo": ", ".join(c["modelos"])}


# ---------------------------------------------------------------- seções
def _jev_txt(d: dict) -> str:
    if d["origem"] == "codigo":
        return "—"
    if d["origem"] == "falha":
        return "falha"
    if "conf" in d:
        return f"{d['bruto'][:4]} ({d['conf']:.2f})"
    return f"e {d['entrega']:.2f} / x {d['exclui']:.2f} → {d['bruto'][:4]}"


def secao_conjunto(nome: str, dados: dict, desenhos: list[str]) -> tuple[str, dict]:
    casos = dados["casos"]
    n_prop = sum(len(c["propostas"]) for c in casos)
    n_cel = sum(len(c["propostas"]) * len(c["requisitos"]) for c in casos)
    out = [f"## Conjunto `{nome}` — {len(casos)} disputas, {n_prop} propostas, {n_cel} células (arquivo versão "
           f"{dados.get('versao')}, autor {dados.get('autor')})\n"]
    if nome == "rascunho":
        out.append("> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**\n")
    res = {"n": len(casos), "n_prop": n_prop, "desenhos": {}}
    saidas, custos, itens = {}, {}, {}
    for d in desenhos:
        saidas[d], custos[d] = rodar(casos, d)
        itens[d] = itens_de(saidas[d], casos, d)

    out.append("### Matriz, elegíveis e perguntas — Jev + código × baseline, por desenho\n")
    out.append("`acerto_semantico` = células semânticas (Jev, depois da válvula) × gabarito; `acerto_numerico` = células "
               "numéricas pelo código; `classe_*` = acerto dentro de cada classe do gabarito. Erros caros: "
               "`exclusao_aprovada` = gabarito contradiz → atende (`_bruto` = antes da válvula); `inelegivel_elegivel` = "
               "proposta com contradiz obrigatório no gabarito que entrou em `elegiveis`. Secundários: "
               "`descartou_sem_perguntar` = gabarito nao_informado → contradiz; `falso_alarme` = atende → contradiz; "
               "`elegivel_fora` = elegível do gabarito que ficou fora. `valvula` = abstenções: células cuja leitura dura "
               "(`bruto`: opção da Choice; Nouls com corte em 0,5) decidia e a válvula/faixa mandou para nao_informado; "
               "`cobertura` = o resto; `erro_decididos` = erro entre as não movidas. `perguntas_*` = nao_informado em "
               "obrigatório de proposta ELEGÍVEL (o que a saída pergunta ao fornecedor) × gabarito, cada lado filtrado "
               "pela própria elegibilidade. `baseline` = palavra-chave + marca de exclusão na mesma frase.\n")
    linhas = []
    for d in desenhos:
        r = resumo(itens[d], casos)
        res["desenhos"][d] = {"res": r}
        linhas.append({"desenho": d, **r})
    out.append(M.tabela(linhas) + "\n")

    padrao = P.DESENHO_PADRAO if P.DESENHO_PADRAO in desenhos else desenhos[0]
    it = itens[padrao]
    out.append(f"### Matriz de confusão (células semânticas) gabarito × previsto — `{padrao}`\n")
    out.append(M.tabela(matriz_confusao(it)) + "\n")
    out.append(f"### Por família (prefixo da `nota`) — `{padrao}`\n")
    out.append(M.tabela(por_familia(it, casos)) + "\n")
    for d in desenhos:
        out.append(f"### Cobertura × erro por limiares (células semânticas; elegíveis recalculados) — `{d}`\n")
        out.append(M.tabela(curva(itens[d], casos, d)) + "\n")

    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    out.append("Latência por REQUISIÇÃO (= por proposta). Mil disputas = 3 mil propostas comparadas.\n")
    linhas = []
    for d in desenhos:
        k = custo(custos[d], len(casos), n_prop)
        res["desenhos"][d]["custo"] = k
        linhas.append({"desenho": d, **k})
    out.append(M.tabela(linhas) + "\n")

    out.append(f"### Por proposta — elegível e perguntas — `{padrao}`\n")
    linhas = []
    for c, s in zip(casos, saidas[padrao]):
        for p in c["propostas"]:
            perg = s["perguntas"].get(p["id"])
            linhas.append({"id": c["id"], "p": p["id"], "elegível gab": p["id"] in c["elegiveis"],
                           "elegível prev": p["id"] in s["elegiveis"],
                           "perguntas ao fornecedor": "; ".join(q["pergunta"] for q in perg) if perg else ("—" if perg is not None else "(inelegível)")})
    out.append(M.tabela(linhas) + "\n")

    out.append(f"### Célula a célula — `{padrao}`" + (f" (`{[x for x in desenhos if x != padrao][0]}` entre parênteses)" if len(desenhos) > 1 else "") + "\n")
    out.append("`jev` = opção bruta (confiança) ou Nouls entrega/exclui → leitura dura; `marca`: `caro` = exclusão aprovada (contradiz → "
               "atende); `desc` = descartou sem perguntar (nao_informado → contradiz); `erro` = outra célula errada.\n")
    linhas = []
    outro = next((d for d in desenhos if d != padrao), None)
    for idx, i in enumerate(it):
        jv = _jev_txt(i["detalhe"])
        if outro:
            jv += f" ({_jev_txt(itens[outro][idx]['detalhe'])} → {itens[outro][idx]['celula'][:4]})"
        caro = i["gabarito"] == "contradiz" and i["celula"] == "atende"
        desc = i["gabarito"] == "nao_informado" and i["celula"] == "contradiz"
        erro = i["celula"] != i["gabarito"] and not caro and not desc
        linhas.append({"id": i["caso"], "p": i["pid"], "r": i["rid"], "requisito": i["requisito"][:60], "tipo": i["tipo"][:3],
                       "jev": jv, "célula": i["celula"][:4], "gab": i["gabarito"][:4], "bl": i["baseline"][:4],
                       "marca": "caro" if caro else ("desc" if desc else ("erro" if erro else "—"))})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), res


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Células, erros caros, elegíveis — Jev + código × baseline\n"]
    linhas = []
    for nome, r in resumos.items():
        for d, v in r["desenhos"].items():
            s = v["res"]
            linhas.append({"conjunto": nome, "desenho": d, "células_sem": s["n_sem"], "acerto_semantico": s["acerto_semantico"],
                           "baseline": s["baseline_semantico"], "numericas": f"{s['acerto_numerico']:.3f} ({s['n_num']})",
                           "exclusao_aprovada": s["exclusao_aprovada"], "baseline_excl": s["baseline_exclusao_aprovada"],
                           "descartou_sem_perguntar": s["descartou_sem_perguntar"], "inelegivel_elegivel": s["inelegivel_elegivel"],
                           "elegivel_fora": s["elegivel_fora"], "elegiveis_exatos": s["elegiveis_exatos"],
                           "perguntas_P/R": f"{s['perguntas_precisao']:.2f}/{s['perguntas_recall']:.2f}", "valvula": s["valvula"]})
    out.append(M.tabela(linhas) + "\n")
    out.append("### Latência e custo\n")
    linhas = []
    for nome, r in resumos.items():
        for d, v in r["desenhos"].items():
            k = v["custo"]
            linhas.append({"conjunto": nome, "desenho": d, "disputas": r["n"], "propostas": r["n_prop"],
                           "requisicoes": k.get("requisicoes"), "p50_ms": k.get("p50_ms"), "p95_ms": k.get("p95_ms"),
                           "tokens_por_proposta": k.get("tokens_por_proposta"), "US$_por_mil_disputas": k.get("US$_por_mil_disputas"),
                           "falhas": k.get("falhas_operacionais"), "modelo": k.get("modelo")})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out)


def secao_veredito(resumos: dict) -> str:
    if "teste" not in resumos:
        return ""
    r = resumos["teste"]["desenhos"][P.DESENHO_PADRAO]
    linhas = veredito(r)
    todos = all(l["passa"] for l in linhas)
    out = ["## Veredito do critério (teste, desenho padrão)\n",
           M.tabela([{"item": l["item"], "regra": CRITERIO_CONTINUAR[l["item"]], "valor": l["valor"], "passa": "✓" if l["passa"] else "✗"} for l in linhas]),
           f"\n**{'CONTINUAR' if todos else 'NÃO PASSOU'}**: {sum(l['passa'] for l in linhas)}/{len(linhas)} itens.\n"]
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}): {h}"


def _congelar() -> dict:
    m = CG.congelar(AQUI, CONGELADOS, CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
        (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    return m


def _criterio_md() -> str:
    c = CRITERIO_CONTINUAR
    return c["onde"] + ": " + "; ".join(f"({k.split('_', 1)[0]}) {v}" for k, v in c.items() if k != "onde") + "."


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if "teste" in conjuntos:
        try:
            manifesto = CG.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != CRITERIO_CONTINUAR:
            sys.exit("teste recusado: o critério de continuar mudou desde o congelamento (rode `run.py congelar`)")
        n_teste = sum(len(c["propostas"]) for c in json.loads((AQUI / "dados" / "teste.json").read_text(encoding="utf-8"))["casos"])
        if n_teste > ORCAMENTO_TESTE:
            sys.exit(f"teste recusado: {n_teste} requisições > orçamento {ORCAMENTO_TESTE}")
        linha = _linha_manifesto(manifesto)
    elif congelar:
        linha = _linha_manifesto(_congelar())
    else:
        h = CG.hashes(AQUI, CONGELADOS)
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())
    if args == ["rascunho"]:
        texto, _ = secao_conjunto("rascunho", json.loads((AQUI / "dados" / "rascunho.json").read_text(encoding="utf-8")),
                                  list(P.DESENHOS))
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — comparador-de-propostas (encanamento)\n\n{texto}",
                                                     encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        arquivo = AQUI / "dados" / f"{nome}.json"
        desenhos = [P.DESENHO_PADRAO] if nome == "teste" else list(P.DESENHOS)  # o teste roda só o desenho escolhido
        texto, resumos[nome] = secao_conjunto(nome, json.loads(arquivo.read_text(encoding="utf-8")), desenhos)
        partes.append(texto)
    cabecalho = (f"# Resultados — comparador-de-propostas\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, limiares, "
                 f"contexto do comprador e baseline: `perguntas.py`; comparação numérica, válvula, elegíveis e perguntas: "
                 f"`comparador.py`. Preço: US$ 0,042 por milhão de tokens de entrada. Desenho padrão: `{P.DESENHO_PADRAO}`; "
                 f"CONF_ATENDE {P.CONF_ATENDE}, CONF_CONTRADIZ {P.CONF_CONTRADIZ}; Nouls FAIXA_ENTREGA {P.FAIXA_ENTREGA}, "
                 f"FAIXA_EXCLUI {P.FAIXA_EXCLUI}.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    RESULTADOS.write_text(cabecalho + "\n" + comparacao(resumos) + "\n" + secao_veredito(resumos) + "\n" + "\n".join(partes),
                          encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")


if __name__ == "__main__":
    main()
