"""Roda o juiz num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py                 ajuste + teste (o teste só roda com o manifesto `congelamento.json` batendo)
  python run.py rascunho        só o encanamento (dados/rascunho.json → resultados-rascunho.md; não é métrica)
  python run.py ajuste          afinação (nos dois desenhos)
  python run.py congelar        roda o ajuste e grava o manifesto (hash de perguntas.py, juiz.py, dados/teste.json
                                e o critério de continuar); o manifesto anterior vai para congelamentos-anteriores/
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Cada resposta vira 1 requisição (desenho `agrupado`) ou 1 por critério semântico (`um_por_requisicao`);
os formais não chamam nada. O cache em `cache/` faz a segunda rodada custar zero.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import congelamento as C  # noqa: E402
import juiz as J  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
CONGELADOS = ["perguntas.py", "juiz.py", "dados/teste.json"]  # teste.json por bytes: hash não é leitura
# Grade de faixas para a curva cobertura × erro (mesmas respostas, zero chamada nova). Inclui assimétricas:
# aprovar pede mais certeza que reprovar quando o erro caro é aprovar resposta ruim.
GRADE_FAIXAS = [(0.5, 0.5), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9), (0.3, 0.8), (0.2, 0.9), (0.3, 0.9)]
# Família do critério semântico, pelo texto (para ver ONDE o Jev erra). Primeira que casa vence.
FAMILIAS = [("nao_inventa", r"^n[aã]o (inventa|afirma)"), ("negado", r"^n[aã]o "), ("tom", r"tom cordial"),
            ("responde", r"^responde"), ("informa", r"^(informa|confirma|especifica|explica|indica|menciona)"),
            ("oferece", r"^(oferece|convida|pede)")]


def familia(criterio: str) -> str:
    return next((f for f, pat in FAMILIAS if re.search(pat, criterio, re.I)), "outra")


def gabarito_resposta(caso: dict) -> str:
    vs = list(caso["veredito"].values())
    return "reprovada" if False in vs else ("indecidivel" if None in vs else "aprovada")


# ---------------------------------------------------------------- execução
def rodar(casos: list[dict], desenho: str) -> tuple[list[dict], dict]:
    jev = Jev(AQUI / "cache")  # uma instância por desenho: latência, tokens e custo separados
    pedidos = [(c, J.pedidos(c, desenho)) for c in casos]
    respostas = jev.perguntar_varios([(s, q) for _, ps in pedidos for s, q, _ in ps])
    saidas, i = [], 0
    for c, ps in pedidos:
        saidas.append(J.compor(c, respostas[i:i + len(ps)], desenho))
        i += len(ps)
    return saidas, jev.resumo()


def itens_semanticos(saidas: list[dict], casos: list[dict]) -> list[dict]:
    """Um item por critério semântico: noul, gabarito, baseline, família, dificuldade."""
    itens = []
    for s, c in zip(saidas, casos):
        rub = {r["id"]: r for r in c["rubrica"]}
        for k in s["criterios"]:
            if k["tipo"] != "semantico":
                continue
            crit = rub[k["id"]]["criterio"]
            itens.append({"caso": c["id"], "id": k["id"], "criterio": crit, "noul": k["noul"], "veredito": k["veredito"],
                          "gabarito": c["veredito"][k["id"]], "baseline": J.baseline(crit, c["resposta"]),
                          "familia": familia(crit), "dificil": c.get("nota", "").startswith("difícil")})
    return itens


# ---------------------------------------------------------------- métricas
def resumo_semantico(itens: list[dict], limiares=None) -> dict:
    """Acerto duro (noul ≥ 0,5), com faixa (cobertura, acerto dos decididos), Brier, erro caro, baseline.

    Critério sem noul (o código mandou para revisão por falta de contexto) conta na cobertura e nos
    nulos, fica fora do acerto duro e do Brier (não houve julgamento do Jev).
    """
    rot = [i for i in itens if i["gabarito"] is not None]
    nulos = [i for i in itens if i["gabarito"] is None]
    falsos = [i for i in rot if i["gabarito"] is False]
    jev = [i for i in rot if i["noul"] is not None]
    ver = {i["id"] + i["caso"]: ("revisa" if i["noul"] is None else J.faixa(i["noul"], limiares)) for i in itens}
    decididos = [i for i in rot if ver[i["id"] + i["caso"]] != "revisa"]
    caros = [i for i in falsos if ver[i["id"] + i["caso"]] == "atende"]
    return {
        "n": len(rot),
        "acerto_duro": M.acerto([(i["noul"] >= 0.5, i["gabarito"]) for i in jev]),
        "cobertura": len(decididos) / len(rot) if rot else float("nan"),
        "acerto_decididos": M.acerto([(ver[i["id"] + i["caso"]] == "atende", i["gabarito"]) for i in decididos]),
        "revisa": len(rot) - len(decididos),
        "erro_caro": f"{len(caros)}/{len(falsos)}",
        "erro_caro_duro": f"{sum(i['noul'] is not None and i['noul'] >= 0.5 for i in falsos)}/{len(falsos)}",
        "nulo_em_revisa": f"{sum(ver[i['id'] + i['caso']] == 'revisa' for i in nulos)}/{len(nulos)}",
        "brier": M.brier([(i["noul"], i["gabarito"]) for i in jev]),
        "baseline_acerto": M.acerto([(i["baseline"], i["gabarito"]) for i in rot]),
        "baseline_erro_caro": f"{sum(i['baseline'] for i in falsos)}/{len(falsos)}",
    }


def resumo_formal(saidas: list[dict], casos: list[dict]) -> tuple[dict, list[dict]]:
    """Acerto da regra × gabarito. Critério que a gramática não reconheceu (`erro`) é falha OPERACIONAL:
    conta à parte em `nao_reconhecidos`, nunca como acerto — e derruba o 100% do mesmo jeito."""
    por_regra: dict[str, list[bool]] = {}
    for s, c in zip(saidas, casos):
        for k in s["criterios"]:
            if k["tipo"] == "formal":
                ok = k["veredito"] == ("atende" if c["veredito"][k["id"]] else "nao_atende")
                por_regra.setdefault(k["regra"], []).append(ok)
    todos = [ok for v in por_regra.values() for ok in v]
    nao_rec = len(por_regra.get("nao_reconhecido", []))
    linhas = [{"regra": r, "n": len(v), "acerto": sum(v) / len(v)} for r, v in sorted(por_regra.items())]
    return {"n": len(todos), "acerto": sum(todos) / len(todos) if todos else float("nan"),
            "erros": len(todos) - sum(todos) - nao_rec, "nao_reconhecidos": nao_rec}, linhas


def resumo_resposta(saidas: list[dict], casos: list[dict]) -> dict:
    """Veredito da resposta inteira × gabarito composto (reprovada = algum false; aprovada = todos true)."""
    pares = [(s["resposta"], gabarito_resposta(c)) for s, c in zip(saidas, casos)]
    reprovadas = [p for p, g in pares if g == "reprovada"]
    aprovadas = [p for p, g in pares if g == "aprovada"]
    return {
        "n": len(pares),
        "acerto": M.acerto([(p, g) for p, g in pares if g != "indecidivel"]),
        "ruim_aprovada": f"{sum(p == 'aprovada' for p in reprovadas)}/{len(reprovadas)}",
        "ruim_em_revisa": f"{sum(p == 'revisa' for p in reprovadas)}/{len(reprovadas)}",
        "boa_reprovada": f"{sum(p == 'reprovada' for p in aprovadas)}/{len(aprovadas)}",
        "boa_em_revisa": f"{sum(p == 'revisa' for p in aprovadas)}/{len(aprovadas)}",
        "indecidivel_em_revisa": f"{sum(p == 'revisa' for p, g in pares if g == 'indecidivel')}/{sum(g == 'indecidivel' for _, g in pares)}",
    }


def _recompor(saida: dict, limiares) -> str:
    """Veredito da resposta inteira com OUTRA faixa, a partir dos nouls já medidos (zero chamada nova)."""
    crits = [{**k, "veredito": J.faixa(k["noul"], limiares)} if k["noul"] is not None else k for k in saida["criterios"]]
    return J.veredito_resposta(crits)


def curva(itens: list[dict], saidas: list[dict], casos: list[dict]) -> list[dict]:
    """Por faixa: métricas por CRITÉRIO e, à parte, a composição da RESPOSTA (`ruim_aprovada`): aprovar um
    critério false não aprova a resposta se outro critério dela já reprova (Codex 2026-10-01, achado 6)."""
    linhas = []
    for f in GRADE_FAIXAS:
        r = resumo_semantico(itens, f)
        pares = [(_recompor(s, f), gabarito_resposta(c)) for s, c in zip(saidas, casos)]
        ruins = [p for p, g in pares if g == "reprovada"]
        linhas.append({"faixa": f"{f[0]}–{f[1]}", "cobertura": r["cobertura"], "erro_decididos": 1 - r["acerto_decididos"],
                       "revisa": r["revisa"], "erro_caro": r["erro_caro"], "nulo_em_revisa": r["nulo_em_revisa"],
                       "ruim_aprovada (resposta)": f"{sum(p == 'aprovada' for p in ruins)}/{len(ruins)}",
                       "acerto_resposta": M.acerto([(p, g) for p, g in pares if g != "indecidivel"])})
    return linhas


def por_grupo(itens: list[dict], chave: str) -> list[dict]:
    grupos = sorted({i[chave] for i in itens}, key=str)
    linhas = []
    for g in grupos:
        sub = [i for i in itens if i[chave] == g]
        r = resumo_semantico(sub)
        linhas.append({chave: g, "n": r["n"], "acerto_duro": r["acerto_duro"], "erro_caro": r["erro_caro"],
                       "revisa": r["revisa"], "baseline": r["baseline_acerto"]})
    return linhas


def custo(c: dict, n_respostas: int, n_verdictos: int) -> dict:
    por_resposta = c["custo_us"] / n_respostas
    return {"requisicoes": c["requisicoes"], "req_por_resposta": round(c["requisicoes"] / n_respostas, 2),
            "p50_ms": c["latencia_p50_ms"], "p95_ms": c["latencia_p95_ms"],
            "tokens_por_resposta": round(c["input_tokens"] / n_respostas),
            "US$_por_resposta": f"{por_resposta:.7f}", "US$_por_milhao_respostas": f"{por_resposta * 1e6:.2f}",
            "US$_por_milhao_vereditos": f"{c['custo_us'] / n_verdictos * 1e6:.2f}", "modelo": ", ".join(c["modelos"])}


# ---------------------------------------------------------------- seções
def secao_conjunto(nome: str, dados: dict, desenhos: list[str]) -> tuple[str, dict]:
    casos = dados["casos"]
    out = [f"## Conjunto `{nome}` — {len(casos)} respostas (arquivo versão {dados.get('versao')}, autor {dados.get('autor')})\n"]
    if nome == "rascunho":
        out.append("> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**\n")
    resumo = {"n": len(casos), "desenhos": {}}
    saidas, custos, itens = {}, {}, {}
    for d in desenhos:
        saidas[d], custos[d] = rodar(casos, d)
        itens[d] = itens_semanticos(saidas[d], casos)
    n_sem = len(itens[desenhos[0]])
    n_form = sum(r["tipo"] == "formal" for c in casos for r in c["rubrica"])

    out.append(f"### Semânticos ({n_sem} critérios) — Jev × baseline, por desenho\n")
    out.append("`acerto_duro` = noul ≥ 0,5 × gabarito (sem faixa; gabarito nulo fora). `cobertura`/`acerto_decididos`/"
               f"`revisa` = com a FAIXA {P.FAIXA}. `erro_caro` = gabarito false → `atende` (aprovou critério que a "
               "resposta não atende); `_duro` = o mesmo sem faixa. `nulo_em_revisa` = gabarito nulo que caiu na faixa "
               "do meio. `baseline` = palavras-chave do critério na resposta (negado inverte).\n")
    linhas = []
    for d in desenhos:
        r = resumo_semantico(itens[d])
        resumo["desenhos"][d] = {"sem": r}
        linhas.append({"desenho": d, **r})
    out.append(M.tabela(linhas) + "\n")

    fm, fm_linhas = resumo_formal(saidas[desenhos[0]], casos)
    resumo["formal"] = fm
    out.append(f"### Formais ({n_form} critérios) — código × gabarito (tem de ser 100%; menos é bug)\n")
    out.append(f"Acerto {fm['acerto']:.3f} ({fm['n'] - fm['erros'] - fm['nao_reconhecidos']}/{fm['n']}); "
               f"{fm['erros']} veredito(s) errado(s), {fm['nao_reconhecidos']} critério(s) não reconhecido(s) pela "
               f"gramática (erro operacional, à parte).\n\n" + M.tabela(fm_linhas) + "\n")

    out.append("### Veredito da resposta inteira (formais + semânticos) por desenho\n")
    out.append("Gabarito: `reprovada` = algum critério false; `aprovada` = todos true; `indecidivel` = há nulo e nenhum "
               "false. `ruim_aprovada` = o erro caro no nível da resposta.\n")
    linhas = []
    for d in desenhos:
        r = resumo_resposta(saidas[d], casos)
        resumo["desenhos"][d]["resp"] = r
        linhas.append({"desenho": d, **r})
    out.append(M.tabela(linhas) + "\n")

    for d in desenhos:
        out.append(f"### Cobertura × erro por faixa — `{d}` (critério; e a composição da resposta à parte)\n")
        out.append(M.tabela(curva(itens[d], saidas[d], casos)) + "\n")
        out.append(f"### Por família do critério e por dificuldade — `{d}`\n")
        out.append(M.tabela(por_grupo(itens[d], "familia")) + "\n")
        out.append(M.tabela(por_grupo(itens[d], "dificil")) + "\n")

    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    out.append("Latência por REQUISIÇÃO; custo por resposta avaliada e por milhão de respostas / de vereditos "
               "semânticos. Os formais custam zero.\n")
    linhas = []
    for d in desenhos:
        k = custo(custos[d], len(casos), n_sem)
        resumo["desenhos"][d]["custo"] = k
        linhas.append({"desenho": d, **k})
    out.append(M.tabela(linhas) + "\n")

    out.append("### Caso a caso (desenho padrão `" + P.DESENHO_PADRAO + "`; o outro entre parênteses)\n")
    out.append("Por critério: `noul` do Jev, veredito com faixa, gabarito, baseline. `erro` = veredito decidido ≠ "
               "gabarito, ou formal errado; `caro` = gabarito false aprovado.\n")
    linhas = []
    outro = next((d for d in desenhos if d != P.DESENHO_PADRAO), None)
    for i, c in enumerate(casos):
        s = saidas[P.DESENHO_PADRAO][i] if P.DESENHO_PADRAO in saidas else saidas[desenhos[0]][i]
        s2 = saidas[outro][i] if outro else None
        for j, k in enumerate(s["criterios"]):
            g = c["veredito"][k["id"]]
            crit = next(r["criterio"] for r in c["rubrica"] if r["id"] == k["id"])
            if k["tipo"] == "formal":
                erro = k["veredito"] != ("atende" if g else "nao_atende")
                marca = "ERRO FORMAL" if erro else "—"
                valor = k["regra"]
            else:
                erro = k["veredito"] != "revisa" and g is not None and (k["veredito"] == "atende") != g
                caro = g is False and k["veredito"] == "atende"
                marca = "caro" if caro else ("erro" if erro else "—")
                if k["noul"] is None:
                    valor = "sem contexto (código, sem chamada)"
                else:
                    valor = f"{k['noul']:.2f}" + (f" ({s2['criterios'][j]['noul']:.2f})" if s2 else "")
                valor += f" · bl={'T' if J.baseline(crit, c['resposta']) else 'F'}"
            linhas.append({"id": c["id"], "crit": k["id"], "tipo": k["tipo"][:3], "critério": crit, "jev/regra": valor,
                           "veredito": k["veredito"], "gab": {True: "T", False: "F", None: "null"}[g], "marca": marca,
                           "resposta": s["resposta"] if j == 0 else ""})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Semânticos — Jev × baseline\n"]
    linhas = []
    for nome, r in resumos.items():
        for d, v in r["desenhos"].items():
            s = v["sem"]
            linhas.append({"conjunto": nome, "desenho": d, "n_sem": s["n"], "acerto_duro": s["acerto_duro"],
                           "baseline": s["baseline_acerto"], "cobertura": s["cobertura"],
                           "acerto_decididos": s["acerto_decididos"], "erro_caro": s["erro_caro"],
                           "baseline_erro_caro": s["baseline_erro_caro"], "brier": s["brier"],
                           "formais": f"{r['formal']['n'] - r['formal']['erros'] - r['formal']['nao_reconhecidos']}/{r['formal']['n']}"
                                      + (f" (+{r['formal']['nao_reconhecidos']} não reconhecidos)" if r["formal"]["nao_reconhecidos"] else "")})
    out.append(M.tabela(linhas) + "\n")
    out.append("### Resposta inteira, latência e custo\n")
    linhas = []
    for nome, r in resumos.items():
        for d, v in r["desenhos"].items():
            linhas.append({"conjunto": nome, "desenho": d, "n": r["n"], "acerto_resposta": v["resp"]["acerto"],
                           "ruim_aprovada": v["resp"]["ruim_aprovada"], "ruim_em_revisa": v["resp"]["ruim_em_revisa"],
                           "boa_em_revisa": v["resp"]["boa_em_revisa"], "p50_ms": v["custo"]["p50_ms"],
                           "p95_ms": v["custo"]["p95_ms"], "US$_por_resposta": v["custo"]["US$_por_resposta"],
                           "US$_por_milhao_respostas": v["custo"]["US$_por_milhao_respostas"],
                           "US$_por_milhao_vereditos": v["custo"]["US$_por_milhao_vereditos"], "modelo": v["custo"]["modelo"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{C.MANIFESTO}`, gravado em {m['congelado_em']}; cega ou não, conforme a rodada declarada no README): {h}"


def _criterio_md() -> str:
    c = P.CRITERIO_CONTINUAR
    itens = [(k.split("_", 1), v) for k, v in c.items() if k != "onde"]
    return c["onde"] + ": " + "; ".join(f"({n}) {nome.replace('_', ' ')}: {v}" for (n, nome), v in itens) + "."


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    if args == ["rascunho"]:
        # Encanamento só: arquivo próprio, sem tocar em resultados.md nem no manifesto (Codex 2026-10-01, achado 2).
        texto, _ = secao_conjunto("rascunho", json.loads((AQUI / "dados" / "rascunho.json").read_text(encoding="utf-8")),
                                  list(P.DESENHOS))
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — juiz-de-eval (encanamento, não é métrica)\n\n{texto}",
                                                     encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if "teste" in conjuntos:
        # O teste só roda com pergunta, juiz, dados E critério congelados: o manifesto gravado ANTES tem de bater.
        try:
            manifesto = C.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != P.CRITERIO_CONTINUAR:
            sys.exit("teste recusado: o critério de continuar mudou desde o congelamento (rode `run.py congelar`)")
        linha = _linha_manifesto(manifesto)
    elif congelar:
        linha = _linha_manifesto(C.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR))
    else:
        h = C.hashes(AQUI, CONGELADOS)
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())

    partes, resumos = [], {}
    for nome in conjuntos:
        arquivo = AQUI / "dados" / f"{nome}.json"
        texto, resumos[nome] = secao_conjunto(nome, json.loads(arquivo.read_text(encoding="utf-8")), list(P.DESENHOS))
        partes.append(texto)
    cabecalho = (f"# Resultados — juiz-de-eval\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Pergunta, faixa e "
                 f"baseline: `perguntas.py`; regras formais: `juiz.py`. Preço: US$ 0,042 por milhão de tokens de "
                 f"entrada. Desenho padrão: `{P.DESENHO_PADRAO}`; FAIXA {P.FAIXA}.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    RESULTADOS.write_text(cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes), encoding="utf-8",
                          newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")


if __name__ == "__main__":
    main()
