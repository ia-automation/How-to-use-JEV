"""Roda o lint num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py                 ajuste + teste (o teste só roda com o manifesto `congelamento.json` batendo)
  python run.py rascunho        só o encanamento (dados/rascunho.json → resultados-rascunho.md; não é métrica)
  python run.py ajuste          afinação (os dois desenhos de nulo, da MESMA requisição)
  python run.py congelar        roda o ajuste e grava o manifesto (hash de perguntas.py, lint.py, run.py,
                                dados/teste.json e o critério de continuar); o anterior vai para congelamentos-anteriores/
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Cada diff vira 1 requisição (todas as regras semânticas, 2 Nouls por regra); as mecânicas não chamam nada.
O diff vai ao Jev com o segredo já mascarado; diff acima do teto (`perguntas.TETO_*`) não chama nada, sai `revisa`
e é contado à parte (fora das métricas semânticas, que só existem onde houve Noul).
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import congelamento as C  # noqa: E402
import lint as L  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
CONGELADOS = ["perguntas.py", "lint.py", "run.py", "dados/teste.json"]  # teste.json por bytes: hash não é leitura
# Grades para a curva cobertura × erro (mesmas respostas, zero chamada nova).
GRADE_FAIXAS = [(0.5, 0.5), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9), (0.2, 0.7), (0.3, 0.8), (0.2, 0.9)]
GRADE_APLICA = [0.2, 0.3, 0.4, 0.5]
MAPA_GAB = {True: "T", False: "F", None: "null"}


# ---------------------------------------------------------------- execução
def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    """Uma requisição por diff; devolve as RESPOSTAS cruas (a composição por desenho vem depois, sem chamada)."""
    jev = Jev(AQUI / "cache")
    pedidos = [L.pedido(c) for c in casos]
    respostas = jev.perguntar_varios([p for p in pedidos if p])
    it = iter(respostas)
    return [next(it) if p else None for p in pedidos], jev.resumo()


def itens_semanticos(casos: list[dict], respostas: list[dict | None]) -> list[dict]:
    """Um item por regra semântica: nouls, gabarito, baseline, chave, dificuldade. Regra de diff acima do teto
    não tem Noul (saiu `revisa` sem chamada) e fica fora: é contada à parte em `secao_conjunto`."""
    itens = []
    for c, resp in zip(casos, respostas):
        saida = L.compor(c, resp)
        for r in saida["regras"]:
            if r["tipo"] != "semantica" or r["viola"] is None:
                continue
            itens.append({"caso": c["id"], "id": r["id"], "chave": r["chave"], "viola": r["viola"], "aplica": r["aplica"],
                          "gatilho": r["gatilho"], "gabarito": c["violacoes"][r["id"]], "baseline": L.baseline(r["chave"], c["diff"]),
                          "dificil": c.get("nota", "").startswith("difícil")})
    return itens


# ---------------------------------------------------------------- métricas
def _ver(i: dict, desenho: str, limiares=None, limiar_aplica=None) -> str:
    return L.faixa(i["viola"], i["aplica"], i["gatilho"], desenho, limiares, limiar_aplica)


def _duro(i: dict, desenho: str, limiar_aplica=None) -> bool:
    """Previsão sem faixa: viola ≥ 0,5 (quem diz "não se aplica" no desenho conta como não viola)."""
    if L.faixa(i["viola"], i["aplica"], i["gatilho"], desenho, (0.5, 0.5), limiar_aplica) == "nao_se_aplica":
        return False
    return i["viola"] >= 0.5


def resumo_semantico(itens: list[dict], desenho: str, limiares=None, limiar_aplica=None) -> dict:
    rot = [i for i in itens if i["gabarito"] is not None]
    nulos = [i for i in itens if i["gabarito"] is None]
    verd = [i for i in rot if i["gabarito"] is True]
    fals = [i for i in rot if i["gabarito"] is False]
    ver = {id(i): _ver(i, desenho, limiares, limiar_aplica) for i in itens}
    decididos = [i for i in rot if ver[id(i)] != "revisa"]
    caros = [i for i in verd if ver[id(i)] in ("ok", "nao_se_aplica")]
    alarmes = [i for i in fals if ver[id(i)] == "viola"]
    return {
        "n": len(rot),
        "acerto_duro": M.acerto([(_duro(i, desenho, limiar_aplica), i["gabarito"]) for i in rot]),
        "cobertura": len(decididos) / len(rot) if rot else float("nan"),
        "acerto_decididos": M.acerto([(ver[id(i)] == "viola", i["gabarito"]) for i in decididos]),
        "revisa": len(rot) - len(decididos),
        "erro_caro": f"{len(caros)}/{len(verd)}",
        "falso_alarme": f"{len(alarmes)}/{len(fals)}",
        "nulo_nao_se_aplica": f"{sum(ver[id(i)] == 'nao_se_aplica' for i in nulos)}/{len(nulos)}",
        "nulo_sem_alarme": f"{sum(ver[id(i)] != 'viola' for i in nulos)}/{len(nulos)}",
        "brier": M.brier([(i["viola"], i["gabarito"]) for i in rot]),
        "baseline_acerto": M.acerto([(i["baseline"] is True, i["gabarito"]) for i in rot]),
        "baseline_erro_caro": f"{sum(i['baseline'] is not True for i in verd)}/{len(verd)}",
        "baseline_falso_alarme": f"{sum(i['baseline'] is True for i in fals)}/{len(fals)}",
        "baseline_nulo_sinalizado": f"{sum(i['baseline'] is None for i in nulos)}/{len(nulos)}",
    }


def resumo_mecanico(casos: list[dict], respostas: list[dict | None]) -> tuple[dict, list[dict]]:
    """Acerto da regex × gabarito, por chave. Tem de ser 100%: menos é bug de código (ou gabarito fora da regex)."""
    por_chave: dict[str, list[bool]] = {}
    for c, resp in zip(casos, respostas):
        for r in L.compor(c, resp)["regras"]:
            if r["tipo"] == "mecanica":
                por_chave.setdefault(r["chave"], []).append((r["veredito"] == "viola") == c["violacoes"][r["id"]])
    todos = [ok for v in por_chave.values() for ok in v]
    linhas = [{"regra": k, "n": len(v), "acerto": sum(v) / len(v)} for k, v in sorted(por_chave.items())]
    return {"n": len(todos), "acerto": sum(todos) / len(todos) if todos else float("nan"), "erros": len(todos) - sum(todos)}, linhas


def aplicabilidade(itens: list[dict]) -> list[dict]:
    """Distribuição do Noul auxiliar por gabarito: é o que decide se ele separa `null` de `false`."""
    linhas = []
    for g in (None, False, True):
        sub = sorted(i["aplica"] for i in itens if i["gabarito"] is g)
        if sub:
            linhas.append({"gabarito": MAPA_GAB[g], "n": len(sub), "aplica_min": sub[0],
                           "aplica_p50": sub[len(sub) // 2], "aplica_max": sub[-1],
                           "abaixo_de_LIMIAR_APLICA": sum(v < P.LIMIAR_APLICA for v in sub),
                           "sem_gatilho_regex": sum(i["gatilho"] is False for i in itens if i["gabarito"] is g),
                           "viola_p50": sorted(i["viola"] for i in itens if i["gabarito"] is g)[len(sub) // 2]})
    return linhas


def curva(itens: list[dict], desenho: str) -> list[dict]:
    linhas = []
    for f in GRADE_FAIXAS:
        r = resumo_semantico(itens, desenho, f)
        linhas.append({"faixa": f"{f[0]}–{f[1]}", "cobertura": r["cobertura"], "erro_decididos": 1 - r["acerto_decididos"],
                       "revisa": r["revisa"], "erro_caro": r["erro_caro"], "falso_alarme": r["falso_alarme"],
                       "nulo_sem_alarme": r["nulo_sem_alarme"]})
    return linhas


def curva_aplica(itens: list[dict]) -> list[dict]:
    linhas = []
    for la in GRADE_APLICA:
        r = resumo_semantico(itens, "aplicabilidade", None, la)
        linhas.append({"LIMIAR_APLICA": la, "acerto_duro": r["acerto_duro"], "cobertura": r["cobertura"],
                       "erro_decididos": 1 - r["acerto_decididos"], "erro_caro": r["erro_caro"],
                       "falso_alarme": r["falso_alarme"], "nulo_nao_se_aplica": r["nulo_nao_se_aplica"]})
    return linhas


def por_grupo(itens: list[dict], chave: str, desenho: str) -> list[dict]:
    linhas = []
    for g in sorted({i[chave] for i in itens}, key=str):
        r = resumo_semantico([i for i in itens if i[chave] == g], desenho)
        n_null = sum(1 for i in itens if i[chave] == g and i["gabarito"] is None)
        linhas.append({chave: g, "n": r["n"], "nulos": n_null, "acerto_duro": r["acerto_duro"], "revisa": r["revisa"],
                       "erro_caro": r["erro_caro"], "falso_alarme": r["falso_alarme"],
                       "nulo_nao_se_aplica": r["nulo_nao_se_aplica"], "baseline": r["baseline_acerto"],
                       "baseline_erro_caro": r["baseline_erro_caro"]})
    return linhas


def custo(c: dict, n_diffs: int) -> dict:
    por_diff = c["custo_us"] / n_diffs
    return {"requisicoes": c["requisicoes"], "do_cache": c["do_cache"], "perguntas": c["perguntas"],
            "p50_ms": c["latencia_p50_ms"], "p95_ms": c["latencia_p95_ms"],
            "tokens_por_diff": round(c["input_tokens"] / n_diffs), "US$_por_diff": f"{por_diff:.7f}",
            "US$_por_mil_PRs": f"{por_diff * 1e3:.4f}", "modelo": ", ".join(c["modelos"])}


# ---------------------------------------------------------------- seções
def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    respostas, medicao = rodar(casos)
    itens = itens_semanticos(casos, respostas)
    out = [f"## Conjunto `{nome}` — {len(casos)} diffs (arquivo versão {dados.get('versao')}, autor {dados.get('autor')})\n"]
    if nome == "rascunho":
        out.append("> Rascunho do construtor, só para testar o encanamento. **Não é métrica.**\n")
    resumo = {"n": len(casos), "desenhos": {}}

    grandes = [c for c in casos if L.diff_grande(c["diff"])]
    n_sem_grandes = sum(len(L.semanticas(c)) for c in grandes)
    resumo["diff_grande"] = len(grandes)
    out.append(f"### Teto do diff — {len(grandes)} diff(s) acima de {P.TETO_LINHAS} linhas ou {P.TETO_CARACTERES} caracteres\n")
    out.append(f"Diff acima do teto não vai ao Jev nem é truncado: as {n_sem_grandes} regra(s) semântica(s) dele(s) saem `revisa` "
               f"(motivo \"{P.MOTIVO_DIFF_GRANDE}\"), sem chamada, e ficam FORA das métricas abaixo; as mecânicas rodam igual. "
               f"IDs: {', '.join(c['id'] for c in grandes) or 'nenhum'}. Maior diff deste conjunto: "
               f"{max(len(c['diff'].splitlines()) for c in casos)} linhas, {max(len(c['diff']) for c in casos)} caracteres.\n")

    n_rot = sum(i["gabarito"] is not None for i in itens)
    out.append(f"### Semânticas ({len(itens)} regras; {n_rot} com gabarito true/false, {len(itens) - n_rot} nulas) — Jev × baseline, por desenho\n")
    out.append("`acerto_duro` = viola ≥ 0,5 × gabarito (no desenho `aplicabilidade`, aplica < LIMIAR_APLICA conta como não "
               f"viola). `cobertura`/`acerto_decididos`/`revisa` = com a FAIXA {P.FAIXA} (e LIMIAR_APLICA {P.LIMIAR_APLICA}). "
               "`erro_caro` = gabarito true que saiu `ok` ou `nao_se_aplica` (violação real passou). `falso_alarme` = gabarito "
               "false que saiu `viola`. `nulo_nao_se_aplica` = gabarito nulo que o lint marcou como não aplicável (só o "
               "desenho `aplicabilidade` sabe dizer isso); `nulo_sem_alarme` = nulo que não virou `viola`. `baseline` = "
               "regex de gatilho + palavra-chave (`None` = sem gatilho = não se aplica).\n")
    linhas = []
    for d in P.DESENHOS:
        r = resumo_semantico(itens, d)
        resumo["desenhos"][d] = {"sem": r}
        linhas.append({"desenho": d, **r})
    out.append(M.tabela(linhas) + "\n")

    out.append("### O Noul de aplicabilidade separa `null` de `false`?\n")
    out.append("Distribuição de `aplica` (e mediana de `viola`) por gabarito. Se os nulos ficam abaixo do LIMIAR_APLICA "
               "e os true/false acima, o Noul auxiliar paga; se o `viola` dos nulos já é baixo, a válvula na instrução basta; "
               "`sem_gatilho_regex` é o que a regex de gatilho (desenho `gatilho`) diria — para nulo, quanto maior melhor; "
               "para true, cada um é uma violação que o código esconderia do Jev.\n")
    out.append(M.tabela(aplicabilidade(itens)) + "\n")
    out.append(M.tabela(curva_aplica(itens)) + "\n")

    mec, mec_linhas = resumo_mecanico(casos, respostas)
    resumo["mecanicas"] = mec
    out.append(f"### Mecânicas ({mec['n']} regras) — regex × gabarito (tem de ser 100%; menos é bug)\n")
    out.append(f"Acerto {mec['acerto']:.3f} ({mec['n'] - mec['erros']}/{mec['n']}); {mec['erros']} erro(s).\n\n" + M.tabela(mec_linhas) + "\n")

    for d in P.DESENHOS:
        out.append(f"### Cobertura × erro por faixa — `{d}`\n")
        out.append(M.tabela(curva(itens, d)) + "\n")
    out.append(f"### Por regra semântica e por dificuldade — `{P.DESENHO_PADRAO}`\n")
    out.append(M.tabela(por_grupo(itens, "chave", P.DESENHO_PADRAO)) + "\n")
    out.append(M.tabela(por_grupo(itens, "dificil", P.DESENHO_PADRAO)) + "\n")

    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    out.append("Uma requisição por diff com regras semânticas (2 Nouls por regra); diff só com mecânicas custa zero. "
               "Aqui 1 PR = 1 diff de 10–60 linhas; PR real tem vários arquivos e custa proporcionalmente mais.\n")
    k = custo(medicao, len(casos))
    resumo["custo"] = k
    out.append(M.tabela([k]) + "\n")

    out.append(f"### Caso a caso (desenho padrão `{P.DESENHO_PADRAO}`)\n")
    out.append("Por regra: `viola`/`aplica` do Jev, `g` = gatilho por regex (mecânica: regex), veredito com faixa, gabarito, baseline (T/F/null). "
               "`erro` = veredito decidido ≠ gabarito; `caro` = violação real que passou; `alarme` = false → viola; "
               "`nulo→viola` = nulo apontado como violação. Última coluna: comentário de CI do diff.\n")
    linhas = []
    for c, resp in zip(casos, respostas):
        s = L.compor(c, resp)
        for j, r in enumerate(s["regras"]):
            g = c["violacoes"][r["id"]]
            if r["tipo"] == "mecanica":
                marca = "ERRO MECANICA" if (r["veredito"] == "viola") != g else "—"
                valor = "regex"
            elif r["viola"] is None:
                marca, valor = "—", f"sem chamada ({r['motivo']})"
            else:
                pred = r["veredito"]
                if g is None:
                    marca = "nulo→viola" if pred == "viola" else "—"
                elif pred == "revisa":
                    marca = "—"
                elif g is True and pred in ("ok", "nao_se_aplica"):
                    marca = "caro"
                elif g is False and pred == "viola":
                    marca = "alarme"
                else:
                    marca = "—"
                bl = L.baseline(r["chave"], c["diff"])
                valor = f"v={r['viola']:.2f} a={r['aplica']:.2f} g={MAPA_GAB[r['gatilho']]} · bl={MAPA_GAB[bl]}"
            linhas.append({"id": c["id"], "regra": f"{r['id']} {r['chave']}", "tipo": r["tipo"][:3], "jev/regra": valor,
                           "veredito": r["veredito"], "gab": MAPA_GAB[g], "marca": marca,
                           "comentário de CI": s["comentario"].replace("\n", "<br>").replace("|", "\\|") if j == 0 else ""})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n"]
    linhas = []
    for nome, r in resumos.items():
        for d, v in r["desenhos"].items():
            s = v["sem"]
            linhas.append({"conjunto": nome, "desenho": d, "n_sem": s["n"], "acerto_duro": s["acerto_duro"],
                           "baseline": s["baseline_acerto"], "cobertura": s["cobertura"], "acerto_decididos": s["acerto_decididos"],
                           "erro_caro": s["erro_caro"], "falso_alarme": s["falso_alarme"], "nulo_nao_se_aplica": s["nulo_nao_se_aplica"],
                           "nulo_sem_alarme": s["nulo_sem_alarme"], "brier": s["brier"],
                           "mecânicas": f"{r['mecanicas']['n'] - r['mecanicas']['erros']}/{r['mecanicas']['n']}",
                           "p50_ms": r["custo"]["p50_ms"], "p95_ms": r["custo"]["p95_ms"],
                           "US$_por_mil_PRs": r["custo"]["US$_por_mil_PRs"], "modelo": r["custo"]["modelo"]})
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
        texto, _ = secao_conjunto("rascunho", json.loads((AQUI / "dados" / "rascunho.json").read_text(encoding="utf-8")))
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — lint-semantico-de-diff (encanamento, não é métrica)\n\n{texto}",
                                                     encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if "teste" in conjuntos:
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
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — lint-semantico-de-diff\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, regex, faixa e "
                 f"baseline: `perguntas.py`; composição: `lint.py`. Preço: US$ 0,042 por milhão de tokens de entrada. "
                 f"Desenho padrão: `{P.DESENHO_PADRAO}`; FAIXA {P.FAIXA}; LIMIAR_APLICA {P.LIMIAR_APLICA}; teto do diff "
                 f"{P.TETO_LINHAS} linhas / {P.TETO_CARACTERES} caracteres. Segredo casado pela regex de SEG sai `***` "
                 f"no state enviado ao Jev e em todo trecho do comentário de CI.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    RESULTADOS.write_text(cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes), encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")


if __name__ == "__main__":
    main()
