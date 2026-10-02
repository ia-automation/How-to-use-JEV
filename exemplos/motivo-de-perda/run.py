"""Roda o motivo de perda num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, motivo.py,
                             run.py, dados/teste.json, dados/taxonomia.json + critério + variante principal); o
                             manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste; o teste só roda com o manifesto batendo. A PRIMEIRA execução com teste
                             também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave

Requisições por conversa na medição: os quatro formatos (`grupo`, `folhas`, `unica`, `tudo`). Cada variante é custeada
só pelas requisições que ELA envia em produção (`motivo.ETAPAS`) — medido, nada estimado. Falha operacional ou
conversa inválida vira `sem_informacao` + revisar com `origem: "falha"`, contada à parte; a taxonomia é validada uma
vez antes do lote (inválida = parada com mensagem, não decisão).
"""
from __future__ import annotations

import datetime
import json
import os
import re
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import motivo as MO  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import PRECO_US_POR_MILHAO_ENTRADA, Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
# Manifesto: código executado (inclusive este arquivo), dados de teste, taxonomia e critério (que leva a variante
# principal). `_comum/` entra só como registro: mudar a infra comum não recusa o teste, mas fica anotado.
CONGELADOS = ["perguntas.py", "motivo.py", "run.py", "dados/teste.json", "dados/taxonomia.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
BASE = "base"
SG = f"{P.VARIANTE_PRINCIPAL}-sg"  # a principal com as guardas desligadas (informativa: mesmos sinais, sem chamada nova)
SEM_GUARDAS = {**P.LIMIAR, "guarda": -1.0, "sem_motivo": 0.0}  # a guarda dispara com `≤`: 0,0 ainda pegaria um Noul em 0,00
LINHAS = [BASE, *P.VARIANTES, SG]
ROTULO = {BASE: "código: palavra-chave por folha", "a": "a · duas etapas (grupo → folhas do grupo)",
          "b": "b · Choice única sobre as 30 folhas", "c": "c · uma requisição (grupo + folhas por grupo)",
          SG: f"{P.VARIANTE_PRINCIPAL} sem as guardas (informativa)"}
GRADE = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
# Classes de desfecho por conversa (ver `classe`); as duas primeiras marcas de erro são os ERROS CAROS.
MARCA = {"folha": "✓", "aceitavel": "≈", "so_grupo": "✓G", "absteve": "∅G", "folha_errada": "✗f", "grupo_errado": "✗G",
         "motivo_inventado": "✗I", "revisar": "?", "falha": "✗F"}
BOM = {"folha", "aceitavel", "so_grupo"}
COLUNAS = ["variante", "n", "acerto estrito", "acerto folgado", "grupo certo", "motivo INVENTADO", "grupo errado auto.",
           "só-grupo certo", "sem_info certo", "absteve", "folha errada", "revisar", "falha", "req/caso", "tokens/caso",
           "US$/1000", "p50_ms", "p95_ms"]


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador (LEIA-ME: "difícil: <família> — detalhe")."""
    nota = c.get("nota") or ""
    if nota.startswith("difícil:"):
        return re.split(r"\s+[—–-]\s+", nota[len("difícil:"):].strip(), maxsplit=1)[0].strip()
    return "fácil / outros"


def rodar(casos: list[dict], taxonomia: list[dict]) -> list[dict]:
    """Uma instância do cliente por conversa: latência e tokens ficam atribuídos à conversa e ao FORMATO de cada
    requisição. Roda pelo invólucro `julgar_seguro`: falha operacional ou conversa inválida (inclusive ausente) vira
    revisão daquela conversa; o lote segue."""
    def um(c: dict) -> dict:
        jev = Jev(AQUI / "cache")
        s = MO.julgar_seguro(jev, c.get("conversa"), taxonomia, etapas=MO.MEDICAO)
        return {**s, "chamadas": [{**ch, "etapa": e} for ch, e in zip(jev.chamadas, s["etapas"])]}
    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(um, casos))


def vivo(s: dict) -> bool:
    return s["origem"] == "jev" and not s.get("longa")


def _decidir(s: dict, limiares: dict) -> dict:
    """As decisões da conversa refeitas com outros limiares (os sinais são os mesmos: não chama nada)."""
    x = s["sinais"]
    return MO.decidir(x["grupo"], x["folhas"], x["unica"], x["tudo"], limiares)


def escolha(s: dict, c: dict, linha: str, taxonomia: list[dict], limiares: dict | None = None) -> dict:
    """Decisão `{grupo, folha, revisar, falha}` de uma linha do relatório no MESMO caso."""
    if linha == BASE and not s.get("invalida"):  # conversa inválida é falha para o baseline também
        return {**MO.baseline(c["conversa"], taxonomia), "falha": False}
    if not vivo(s):
        return {"grupo": s["grupo"], "folha": None, "revisar": True, "falha": True}
    if linha == SG:
        return {**_decidir(s, SEM_GUARDAS)[P.VARIANTE_PRINCIPAL], "falha": False}
    d = _decidir(s, limiares)[linha] if limiares else s["decisoes"][linha]
    return {**d, "falha": False}


def classe(d: dict, c: dict) -> str:
    """Desfecho de uma decisão contra o gabarito:
    folha (a principal) · aceitavel (∈ `aceitaveis`, de qualquer grupo) · so_grupo (gabarito `folha: null`, saiu só o
    grupo certo) · absteve (havia folha, saiu só o grupo certo: nem acerto nem erro) · folha_errada (grupo certo, folha
    fora de `aceitaveis`) · grupo_errado (ERRO CARO: grupo ≠ gabarito, automatizado) · motivo_inventado (ERRO CARO:
    gabarito `sem_informacao`, saiu outro grupo, automatizado) · revisar (mandado a humano: não conta como acerto) ·
    falha (operacional ou teto: idem)."""
    if d.get("falha"):
        return "falha"
    if d["revisar"]:
        return "revisar"
    G, F, A, g, f = c["grupo"], c["folha"], c["aceitaveis"], d["grupo"], d["folha"]
    if f is not None and f == F:
        return "folha"
    if f is not None and f in A:
        return "aceitavel"
    if G == P.SEM_INFORMACAO and g != G:
        return "motivo_inventado"
    if g != G:
        return "grupo_errado"
    if f is None:
        return "so_grupo" if F is None else "absteve"
    return "folha_errada"


def metricas(itens: list[tuple]) -> dict:
    """itens = [(decisão, caso)]."""
    cl = [classe(d, c) for d, c in itens]
    n = len(itens)
    nulos = sum(c["folha"] is None for _, c in itens)
    si = sum(c["grupo"] == P.SEM_INFORMACAO for _, c in itens)
    b = {"n": n, "nulos": nulos, "com": n - nulos, "sem_info": si, **{k: cl.count(k) for k in MARCA}}
    b["estrito"] = (b["folha"] + b["so_grupo"]) / n if n else 0.0
    b["folgado"] = (b["folha"] + b["aceitavel"] + b["so_grupo"]) / n if n else 0.0
    b["grupo_certo"] = sum(k in (*BOM, "absteve", "folha_errada") for k in cl) / n if n else 0.0
    b["grupo_errado_auto"] = b["grupo_errado"] + b["motivo_inventado"]
    b["si_certo"] = sum(k in BOM for k, (_, c) in zip(cl, itens) if c["grupo"] == P.SEM_INFORMACAO)
    b["automatizados"] = n - b["revisar"] - b["falha"]
    return {"n": n, "acerto estrito": b["estrito"], "acerto folgado": b["folgado"], "grupo certo": b["grupo_certo"],
            "motivo INVENTADO": f"{b['motivo_inventado']}/{si}", "grupo errado auto.": f"{b['grupo_errado_auto']}/{n}",
            "só-grupo certo": f"{b['so_grupo']}/{nulos}", "sem_info certo": f"{b['si_certo']}/{si}",
            "absteve": f"{b['absteve']}/{b['com']}", "folha errada": f"{b['folha_errada']}/{n}",
            "revisar": f"{b['revisar']}/{n}", "falha": f"{b['falha']}/{n}", "_bruto": b}


def custo(saidas: list[dict], etapas: tuple) -> dict:
    """Tokens, custo e latência MEDIDOS nas requisições que a variante envia em produção. Latência por conversa = soma
    das requisições da variante (são sequenciais), como medidas na chamada real (o cache guarda a da chamada original)."""
    n = max(len(saidas), 1)
    por_caso = [[ch for ch in s["chamadas"] if ch["etapa"] in etapas] for s in saidas]
    ch = [x for caso in por_caso for x in caso]
    tk = sum(x["input_tokens"] for x in ch)
    lat = sorted(sum(x["ms"] for x in caso) for caso in por_caso if caso)
    return {"req/caso": f"{len(ch) / n:.2f}", "tokens/caso": round(tk / n),
            "US$/1000": f"{1000 * tk / 1e6 * PRECO_US_POR_MILHAO_ENTRADA / n:.4f}",
            "p50_ms": round(statistics.median(lat)) if lat else 0, "p95_ms": lat[min(len(lat) - 1, int(0.95 * len(lat)))] if lat else 0,
            "_req": len(ch), "_novas": sum(not x["cache"] for x in ch), "_tokens": tk}


def veredito(v: dict) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    lim = P.CRITERIO_CONTINUAR.get("limites")
    if not lim:
        return "_(critério ainda não fixado — só depois do ajuste)_"
    p, base = v[P.VARIANTE_PRINCIPAL]["_bruto"], v[BASE]["_bruto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    n = max(p["n"], 1)
    rev = (p["revisar"] + p["falha"]) / n
    return M.tabela([
        {"critério": "1 motivo INVENTADO (gabarito `sem_informacao`, saiu outro grupo, automatizado)", "medido": f"{p['motivo_inventado']}/{p['sem_info']}",
         "limite": f"≤ {lim['inventado_max']}", "passa": ok(p["motivo_inventado"] <= lim["inventado_max"])},
        {"critério": "2 grupo errado automatizado (inclui os inventados)", "medido": f"{p['grupo_errado_auto']}/{n} ({p['grupo_errado_auto'] / n:.3f})",
         "limite": f"≤ {lim['grupo_errado_max_fracao']:.2f}", "passa": ok(p["grupo_errado_auto"] / n <= lim["grupo_errado_max_fracao"])},
        {"critério": "3 acerto folgado (revisão e falha = erro)", "medido": f"{p['folgado']:.3f}",
         "limite": f"≥ {lim['folgado_min']:.2f}", "passa": ok(p["folgado"] >= lim["folgado_min"])},
        {"critério": "4 grupo certo (revisão e falha = erro)", "medido": f"{p['grupo_certo']:.3f}",
         "limite": f"≥ {lim['grupo_min']:.2f}", "passa": ok(p["grupo_certo"] >= lim["grupo_min"])},
        {"critério": "5 revisão (inclui falha)", "medido": f"{p['revisar'] + p['falha']}/{n} ({rev:.3f})",
         "limite": f"≤ {lim['revisao_max_fracao']:.2f}", "passa": ok(rev <= lim["revisao_max_fracao"])},
        {"critério": "6 contra o baseline de palavras-chave", "medido": f"{p['folgado']:.3f} × {base['folgado']:.3f}",
         "limite": ">", "passa": ok(p["folgado"] > base["folgado"])},
    ])


def varredura(vivos: list[tuple], taxonomia: list[dict], linha: str, chave: str) -> str:
    """Cobertura × erro: a mesma variante com UM limiar percorrendo a grade (os outros ficam como estão)."""
    linhas = []
    for t in GRADE:
        itens = [(escolha(s, c, linha, taxonomia, {**P.LIMIAR, chave: t}), c) for s, c in vivos]
        b = metricas(itens)["_bruto"]
        linhas.append({"limiar": t, "automatizadas": f"{b['automatizados']}/{b['n']}", "folgado": b["folgado"], "grupo certo": b["grupo_certo"],
                       "inventado": f"{b['motivo_inventado']}/{b['sem_info']}", "grupo errado auto.": f"{b['grupo_errado_auto']}/{b['n']}",
                       "só-grupo certo": f"{b['so_grupo']}/{b['nulos']}", "absteve": b["absteve"], "folha errada": b["folha_errada"], "revisar": b["revisar"]})
    return M.tabela(linhas)


def _q(xs: list, f: float) -> str:
    return "—" if not xs else f"{sorted(xs)[min(len(xs) - 1, int(f * len(xs)))]:.2f}"


def guardas(vivos: list[tuple], taxonomia: list[dict]) -> str:
    """O que cada guarda fez na principal: quantas vezes disparou e o desfecho antes (sem guardas) → depois."""
    linhas = []
    for nome, lim in (("`blames_agency` (grupo atendimento)", {**SEM_GUARDAS, "guarda": P.LIMIAR["guarda"]}),
                      ("`closed_elsewhere` (grupo concorrencia)", {**SEM_GUARDAS, "guarda": P.LIMIAR["guarda"]}),
                      ("`reason_stated` (grupo ≠ sem_informacao)", {**SEM_GUARDAS, "sem_motivo": P.LIMIAR["sem_motivo"]})):
        antes = [(escolha(s, c, P.VARIANTE_PRINCIPAL, taxonomia, SEM_GUARDAS), c) for s, c in vivos]
        depois = [(escolha(s, c, P.VARIANTE_PRINCIPAL, taxonomia, lim), c) for s, c in vivos]
        if "blames" in nome:
            mudou = [(a, d, c) for (a, c), (d, _) in zip(antes, depois) if a != d and a["grupo"] == P.ATENDIMENTO]
        elif "closed" in nome:
            mudou = [(a, d, c) for (a, c), (d, _) in zip(antes, depois) if a != d and a["grupo"] == P.CONCORRENCIA]
        else:
            mudou = [(a, d, c) for (a, c), (d, _) in zip(antes, depois) if a != d]
        de_erro = sum(classe(a, c) in ("grupo_errado", "motivo_inventado", "folha_errada") for a, _, c in mudou)
        de_acerto = sum(classe(a, c) in BOM for a, _, c in mudou)
        linhas.append({"guarda": nome, "disparou": len(mudou), "tirou um erro": de_erro, "tirou um acerto": de_acerto,
                       "casos": " ".join(f"{c['id']}({MARCA[classe(a, c)]}→{MARCA[classe(d, c)]})" for a, d, c in mudou) or "—"})
    return M.tabela(linhas)


def secao_conjunto(nome: str, dados: dict, taxonomia: list[dict]) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas = rodar(casos, taxonomia)
    vivos = [(s, c) for s, c in zip(saidas, casos) if vivo(s)]
    falhas = [(c["id"], s["motivo"]) for s, c in zip(saidas, casos) if not vivo(s)]
    itens = {l: [(escolha(s, c, l, taxonomia), c) for s, c in zip(saidas, casos)] for l in LINHAS}
    zero = {"req/caso": "0", "tokens/caso": 0, "US$/1000": "0", "p50_ms": 0, "p95_ms": 0}
    custos = {l: zero if l == BASE else custo(saidas, MO.ETAPAS[P.VARIANTE_PRINCIPAL if l == SG else l]) for l in LINHAS}
    variantes = {l: {**metricas(itens[l]), **custos[l]} for l in LINHAS}
    dificeis = sum(familia(c) != "fácil / outros" for c in casos)
    nulos, si = sum(c["folha"] is None for c in casos), sum(c["grupo"] == P.SEM_INFORMACAO for c in casos)
    tudo = custo(saidas, MO.MEDICAO)
    resumo = {"n": len(casos), "dificeis": dificeis, "nulos": nulos, "sem_info": si, "variantes": variantes, "falhas": len(falhas), "tudo": tudo,
              "modelos": sorted({ch["modelo"] for s in saidas for ch in s["chamadas"]})}

    out = [f"## Conjunto `{nome}` — {len(casos)} conversas (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{dificeis} difíceis, {nulos} com `folha: null`, {si} `sem_informacao`, {len(falhas)} em revisão por falha operacional, entrada inválida ou teto; "
           f"taxonomia de {len(taxonomia)} grupos e {sum(len(g['folhas']) for g in taxonomia)} folhas\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if falhas:
        out.append(f"> **{len(falhas)} conversas em revisão por falha — este conjunto NÃO é medição limpa**: " + "; ".join(f"{i}: {m}" for i, m in falhas) + "\n")

    # --- escolha
    out.append("### Desfecho — baseline de código × variantes com Jev, nas mesmas conversas\n")
    out.append("`estrito` = a folha principal do gabarito (ou só o grupo certo quando `folha` é null). `folgado` = folha ∈ `aceitaveis` "
               "(ou só o grupo certo quando `folha` é null). `grupo certo` = grupo = gabarito ou folha aceitável. **Motivo INVENTADO** "
               "(erro caro) = gabarito `sem_informacao` e saiu outro grupo, automatizado (denominador = casos `sem_informacao`). "
               "**Grupo errado automatizado** (erro caro) = grupo ≠ gabarito sem revisão, inclui os inventados. `só-grupo certo` = nos "
               "casos `folha: null`, saiu só o grupo certo. `absteve` = havia folha, saiu só o grupo certo (nem acerto nem erro). "
               "Revisão e falha contam como erro em todas as taxas de acerto. Custo e latência: só as requisições que a variante envia "
               f"em produção, medidas. Variante principal (a que o critério julga): **{ROTULO[P.VARIANTE_PRINCIPAL]}**.\n")
    out.append(M.tabela([{"variante": ROTULO[l], **variantes[l]} for l in LINHAS], COLUNAS) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(variantes) + "\n")
    if not vivos:
        return "\n".join(out), resumo

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador) — acertos folgados; erros caros e revisões da principal\n")
    fams = list(dict.fromkeys(familia(c) for c in casos if familia(c) != "fácil / outros")) + ["fácil / outros"]
    linhas = []
    for fam in fams:
        idx = [k for k, c in enumerate(casos) if familia(c) == fam]
        if not idx:
            continue
        conta = lambda l, alvos: sum(classe(*itens[l][k]) in alvos for k in idx)  # noqa: E731
        linhas.append({"família": fam, "n": len(idx), "`null`": sum(casos[k]["folha"] is None for k in idx),
                       **{l: conta(l, BOM) for l in LINHAS},
                       "inventado (principal)": conta(P.VARIANTE_PRINCIPAL, {"motivo_inventado"}),
                       "grupo errado (principal)": conta(P.VARIANTE_PRINCIPAL, {"grupo_errado"}),
                       "revisar (principal)": conta(P.VARIANTE_PRINCIPAL, {"revisar"})})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- guardas
    out.append(f"### As guardas na principal (`{P.VARIANTE_PRINCIPAL}`) — o que cada Noul mudou\n")
    out.append(guardas(vivos, taxonomia) + "\n")

    # --- sinais
    out.append("### Os sinais — quem aponta o grupo e a folha certos, sem limiar nenhum\n")
    x = lambda s: s["sinais"]  # noqa: E731
    acerta_g = lambda s, c, g: g == c["grupo"]  # noqa: E731
    apontam_g = {"Choice `group` (requisição `grupo`)": lambda s: x(s)["grupo"]["grupo"],
                 "soma das folhas por grupo (Choice única)": lambda s: x(s)["unica"]["grupo"],
                 "Choice `group` (requisição `tudo`)": lambda s: x(s)["tudo"]["grupo"]}
    out.append(M.tabela([{"quem aponta o grupo": k, "grupo certo": f"{sum(acerta_g(s, c, f(s)) for s, c in vivos)}/{len(vivos)}"} for k, f in apontam_g.items()]) + "\n")
    com = [(s, c) for s, c in vivos if c["folha"] is not None]
    folha_a = lambda s: x(s)["folhas"]["folha"]  # noqa: E731
    folha_c = lambda s: x(s)["tudo"]["folhas"][x(s)["tudo"]["grupo"]]["folha"]  # noqa: E731
    apontam_f = {"Choice das folhas do grupo vencedor (`folhas`)": folha_a, "Choice única (vencedora)": lambda s: x(s)["unica"]["folha"],
                 "Choice `leaf.<grupo vencedor>` (`tudo`)": folha_c}
    out.append(M.tabela([{"quem aponta a folha": k, "a principal": f"{sum(f(s) == c['folha'] for s, c in com)}/{len(com)}",
                          "alguma aceitável": f"{sum(f(s) in c['aceitaveis'] for s, c in com)}/{len(com)}",
                          "`only_group`": f"{sum(f(s) is None for s, _ in com)}/{len(com)}"} for k, f in apontam_f.items()]) + "\n")
    nulos_v = [(s, c) for s, c in vivos if c["folha"] is None]
    if nulos_v:
        out.append(f"Nos {len(nulos_v)} casos `folha: null`: `only_group` saiu em `folhas` {sum(folha_a(s) is None for s, _ in nulos_v)}, em `tudo` "
                   f"{sum(folha_c(s) is None for s, _ in nulos_v)}; p da folha vencedora na Choice única: "
                   f"{', '.join(f'{x(s)['unica']['p'][x(s)['unica']['folha']]:.2f}' for s, _ in nulos_v)}.\n")
    certo_g = [x(s)["grupo"]["p"][x(s)["grupo"]["grupo"]] for s, c in vivos if x(s)["grupo"]["grupo"] == c["grupo"]]
    errado_g = [x(s)["grupo"]["p"][x(s)["grupo"]["grupo"]] for s, c in vivos if x(s)["grupo"]["grupo"] != c["grupo"]]
    out.append(f"p(grupo vencedor) na Choice `group` (`grupo`): quando certo (n = {len(certo_g)}) mínimo {_q(certo_g, 0)}, p10 {_q(certo_g, 0.1)}, "
               f"mediana {_q(certo_g, 0.5)}; quando errado (n = {len(errado_g)}) mínimo {_q(errado_g, 0)}, mediana {_q(errado_g, 0.5)}, máximo {_q(errado_g, 1.0)}. ")
    pf_c = [x(s)["folhas"]["p"][c["folha"]] for s, c in com if folha_a(s) == c["folha"]]
    pf_e = [x(s)["folhas"]["p"][folha_a(s)] for s, c in com if folha_a(s) not in (None, c["folha"]) and folha_a(s) not in c["aceitaveis"]]
    pu_c = [x(s)["unica"]["p"][c["folha"]] for s, c in com if x(s)["unica"]["folha"] == c["folha"]]
    pu_e = [x(s)["unica"]["p"][x(s)["unica"]["folha"]] for s, c in com if x(s)["unica"]["folha"] not in c["aceitaveis"]]
    out.append(f"p(folha vencedora) em `folhas`: certa mínimo {_q(pf_c, 0)}, p10 {_q(pf_c, 0.1)}, mediana {_q(pf_c, 0.5)}; errada (fora de aceitáveis) "
               f"{', '.join(f'{v:.2f}' for v in sorted(pf_e)) or '—'}. Na Choice única: certa mínimo {_q(pu_c, 0)}, p10 {_q(pu_c, 0.1)}, mediana "
               f"{_q(pu_c, 0.5)}; errada {', '.join(f'{v:.2f}' for v in sorted(pu_e)) or '—'}.\n")
    dif = [(c["id"], x(s)["grupo"]["grupo"], x(s)["tudo"]["grupo"]) for s, c in vivos if x(s)["grupo"]["grupo"] != x(s)["tudo"]["grupo"]]
    out.append(f"A MESMA Choice `group` em duas requisições (`grupo` × `tudo`, isolamento ≠ determinismo) trocou de vencedor em {len(dif)}/{len(vivos)}"
               + (": " + "; ".join(f"{i} {a}→{b}" for i, a, b in dif) if dif else "") + ".\n")
    for k, cond in (("reason_stated", lambda c: c["grupo"] != P.SEM_INFORMACAO), ("blames_agency", lambda c: c["grupo"] == P.ATENDIMENTO),
                    ("closed_elsewhere", lambda c: c["grupo"] == P.CONCORRENCIA)):
        sim = [x(s)["grupo"]["nouls"][k] for s, c in vivos if cond(c)]
        nao = [x(s)["grupo"]["nouls"][k] for s, c in vivos if not cond(c)]
        out.append(f"Noul `{k}` (requisição `grupo`): onde o gabarito pede sim (n = {len(sim)}) mínimo {_q(sim, 0)}, p10 {_q(sim, 0.1)}, mediana {_q(sim, 0.5)}; "
                   f"onde pede não (n = {len(nao)}) mediana {_q(nao, 0.5)}, p90 {_q(nao, 0.9)}, máximo {_q(nao, 1.0)}.\n")
    rep = [(x(s)["grupo"]["nouls"][k], x(s)["unica"]["nouls"][k], x(s)["tudo"]["nouls"][k]) for s, _ in vivos for k in P.NOULS]
    d1 = [abs(a - b) for a, b, _ in rep]
    d2 = [abs(a - c) for a, _, c in rep]
    out.append(f"O mesmo Noul em requisições diferentes: `grupo` × `unica` diferença absoluta média {statistics.mean(d1):.3f}, máxima {max(d1):.3f}; "
               f"`grupo` × `tudo` média {statistics.mean(d2):.3f}, máxima {max(d2):.3f} (n = {len(rep)}).\n")

    # --- curvas
    out.append("### Cobertura × erro por limiar (um limiar por vez; os outros como em `perguntas.py`)\n")
    for l in [P.VARIANTE_PRINCIPAL, *(v for v in P.VARIANTES if v != P.VARIANTE_PRINCIPAL)]:
        chaves = ["grupo", "folha_unica" if l == "b" else "folha"] + (["guarda", "sem_motivo"] if l == P.VARIANTE_PRINCIPAL else [])
        for ch in chaves:
            out.append(f"**{ROTULO[l]}** — limiar `{ch}` (em uso: {P.LIMIAR[ch]})\n")
            out.append(varredura(vivos, taxonomia, l, ch) + "\n")

    # --- custo
    out.append("### Custo e latência por formato de requisição (medidos)\n")
    linhas = []
    for e in MO.MEDICAO:
        k = custo(saidas, (e,))
        ms = sorted(ch["ms"] for s in saidas for ch in s["chamadas"] if ch["etapa"] == e)
        linhas.append({"requisição": e, "enviadas": k["_req"], "novas (não cache)": k["_novas"],
                       "tokens por requisição": round(k["_tokens"] / max(k["_req"], 1)),
                       "p50_ms": round(statistics.median(ms)) if ms else 0, "p95_ms": ms[min(len(ms) - 1, int(0.95 * len(ms)))] if ms else 0,
                       "quem usa": ", ".join(v for v in P.VARIANTES if e in MO.ETAPAS[v])})
    out.append(M.tabela(linhas) + "\n")
    out.append(f"Tudo o que esta execução usou: {tudo['_req']} requisições ({tudo['_novas']} novas), {tudo['_tokens']} tokens, "
               f"US$ {tudo['_tokens'] / 1e6 * PRECO_US_POR_MILHAO_ENTRADA:.4f} · modelo: {', '.join(resumo['modelos'])}. Latência = a da "
               "chamada original de cada requisição (o cache a guarda), medida com 8 conversas em paralelo.\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("Marca: ✓ a folha principal · ≈ aceitável · ✓G só grupo, certo · ∅G absteve da folha (grupo certo) · ✗f folha errada (grupo certo) · "
               "✗G grupo errado · ✗I motivo INVENTADO · ? revisar · ✗F falha. Célula = `grupo/folha marca`; `∅` = sem folha. "
               "`grupo` = Choice `group` com p(vencedor); `nouls` = reason_stated · blames_agency · closed_elsewhere (requisição `grupo`).\n")
    cel = lambda k, l: f"{itens[l][k][0]['grupo']}/{itens[l][k][0]['folha'] or '∅'} {MARCA[classe(*itens[l][k])]}"  # noqa: E731
    linhas = []
    for k, (s, c) in enumerate(zip(saidas, casos)):
        linha = {"id": c["id"], "fam": familia(c), "gabarito": f"{c['grupo']}/{c['folha'] or '∅'}",
                 "outras aceitáveis": " ".join(a for a in c["aceitaveis"] if a != c["folha"]) or "—", "base": cel(k, BASE)}
        if not vivo(s):
            linhas.append({**linha, "a": s["motivo"]})
            continue
        g, fo, u, t = x(s)["grupo"], x(s)["folhas"], x(s)["unica"], x(s)["tudo"]
        linhas.append({**linha, "grupo": f"{g['grupo']} ({g['p'][g['grupo']]:.2f})", "folhas": f"{fo['folha'] or P.SO_GRUPO} ({fo['p'][fo['folha'] or P.SO_GRUPO]:.2f})",
                       "a": cel(k, "a"), "única": f"{u['folha']} ({u['p'][u['folha']]:.2f}; grupo {u['p_grupo'][u['grupo']]:.2f})", "b": cel(k, "b"),
                       "tudo": f"{t['grupo']} ({t['p'][t['grupo']]:.2f}) › {t['folhas'][t['grupo']]['folha'] or P.SO_GRUPO} ({t['folhas'][t['grupo']]['p'][t['folhas'][t['grupo']]['folha'] or P.SO_GRUPO]:.2f})",
                       "c": cel(k, "c"), "nouls": " · ".join(f"{g['nouls'][n]:.2f}" for n in P.NOULS), SG: cel(k, SG)})
    out.append(M.tabela(linhas, ["id", "fam", "gabarito", "outras aceitáveis", "base", "grupo", "folhas", "a", "única", "b", "tudo", "c", "nouls", SG]) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n"]
    out.append(M.tabela([{"conjunto": n, "variante": ROTULO[l], **r["variantes"][l]} for n, r in resumos.items() for l in LINHAS],
                        ["conjunto", *COLUNAS]) + "\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"], "`folha: null`": r["nulos"], "`sem_informacao`": r["sem_info"],
                          "falhas": r["falhas"], "requisições (todas as variantes)": r["tudo"]["_req"],
                          "novas (não cache)": r["tudo"]["_novas"], "tokens": r["tudo"]["_tokens"],
                          "modelo": ", ".join(r["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}): {h}"


def _congelar() -> dict:
    """Grava o manifesto pela infra comum e anota, só como registro, o hash da infra comum que rodou."""
    if not P.CRITERIO_CONTINUAR.get("limites") or P.CRITERIO_CONTINUAR.get("variante_principal") != P.VARIANTE_PRINCIPAL:
        sys.exit("congelamento recusado: fixe `CRITERIO_CONTINUAR` (com `limites` e `variante_principal` = VARIANTE_PRINCIPAL)")
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    return "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_CONTINUAR.items() if k != "limites") or "ainda não fixado"


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    taxonomia = json.loads((AQUI / "dados" / "taxonomia.json").read_text(encoding="utf-8"))["casos"]
    try:
        MO.validar_taxonomia(taxonomia)  # compartilhada por todo o lote: inválida é parada aqui, não revisão por conversa
    except ValueError as e:
        sys.exit(f"taxonomia inválida: {e}")
    if "teste" in conjuntos:
        # O teste só roda com perguntas, política, dados, taxonomia E critério congelados: o manifesto gravado ANTES tem de bater.
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

    partes, resumos = [], {}
    for nome in conjuntos:
        dados = json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8"))
        texto, resumos[nome] = secao_conjunto(nome, dados, taxonomia)
        partes.append(texto)
        print(f"{nome}: {resumos[nome]['tudo']['_req']} requisições, {resumos[nome]['tudo']['_novas']} novas")
    cabecalho = (f"Gerado por `run.py` em {datetime.date.today().isoformat()} (modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e "
                 f"amostra em cada seção). Perguntas, limiares, variante principal e critério: `perguntas.py`; validação, decisão "
                 f"e baseline: `motivo.py`; bateria do código (sem API): `testa_falhas.py`. Preço: US$ 0,042 por milhão de tokens "
                 f"de entrada. Limiares: {P.LIMIAR}; teto da conversa {P.TETO_CARACTERES} caracteres.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    if args == ["rascunho"]:
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — motivo-de-perda (encanamento)\n\n{cabecalho}\n" + "\n".join(partes),
                                                     encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return
    texto = "# Resultados — motivo-de-perda\n\n" + cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    if "teste" in conjuntos and not RODADA1.exists():
        # A primeira execução COMPLETA com o teste É a rodada cega: fica preservada e nunca é reescrita por este script.
        # Falha operacional deixa a conversa pendente (não é resposta): rodar de novo envia só o que faltou — o cache
        # guarda o resto — e a rodada cega só é gravada quando todas as conversas tiverem resposta.
        if resumos["teste"]["falhas"]:
            print(f"rodada cega INCOMPLETA: {resumos['teste']['falhas']} conversas pendentes por falha operacional; rode de novo")
        else:
            RODADA1.write_text(texto, encoding="utf-8", newline="\n")
            print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
