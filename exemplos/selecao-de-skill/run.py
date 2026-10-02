"""Roda a seleção de skill num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, selecao.py,
                             run.py, dados/teste.json, dados/skills.json + critério + variante principal); o
                             manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste; o teste só roda com o manifesto batendo. A PRIMEIRA execução com teste
                             também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave

Requisições por pedido na medição: os quatro formatos (`ampla`, `fits_vencedor` quando a ampla escolhe skill,
`rerank`, `todos`) e, no rascunho e no teste, a `ampla_completa` da variante informativa a2 (no ajuste ela não foi
medida: orçamento de requisições, e não há nada nela para afinar). Cada variante é custeada só pelas requisições
que ELA envia em produção (`selecao.ETAPAS`) — medido, nada estimado. Falha operacional vira "sem sugestão" do
pedido, contada à parte.
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
import perguntas as P  # noqa: E402
import selecao as S  # noqa: E402
from jevcache import PRECO_US_POR_MILHAO_ENTRADA, Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
# Manifesto: código executado (inclusive este arquivo), dados de teste, catálogo e critério (que leva a variante
# principal). `_comum/` entra só como registro: mudar a infra comum não recusa o teste, mas fica anotado.
CONGELADOS = ["perguntas.py", "selecao.py", "run.py", "dados/teste.json", "dados/skills.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
BASE, RECEITA_030 = "base", "c@0,30"
# Conjuntos em que a informativa a2 é medida (uma requisição a mais por pedido).
ETAPAS_DO_CONJUNTO = {"rascunho": S.MEDICAO_COM_A2, "ajuste": S.MEDICAO, "teste": S.MEDICAO_COM_A2}
LIMIARES_RECEITA = {**P.LIMIAR, "fits": P.LIMIAR_RECEITA, "porta": P.LIMIAR_RECEITA}
ROTULO = {BASE: "código: BM25 + limiar", "a": "a · Choice única", "b": "b · Choice + `fits` do vencedor",
          "c": "c · receita oficial (portão = maior `fits`; vencedor = Choice `rerank`)",
          "c2": "c2 · receita + portão no vencedor consumido", "d": "d · receita corrigida (vencedor = maior `fits`)",
          "e": "e · um `fits` por skill (42 Nouls)",
          "a2": "a2 · Choice única com a descrição completa — informativa",
          RECEITA_030: "c com os limiares publicados (porta 0,30; `fits` 0,30) — informativa"}


def linhas_de(etapas: tuple) -> list[str]:
    """Linhas do relatório num conjunto: baseline, as seis variantes, a2 se foi medida, e a receita com os limiares
    publicados quando os nossos são outros."""
    return ([BASE, *P.VARIANTES] + (["a2"] if "ampla_completa" in etapas else [])
            + ([RECEITA_030] if LIMIARES_RECEITA != P.LIMIAR else []))


GRADE = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
GRADE_BASE = [0.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0]
MARCA = {"melhor": "✓", "aceitavel": "≈", "nula_certa": "✓∅", "skill_indevida": "✗I", "null_indevido": "✗N",
         "skill_errada": "✗E", "sem_sugestao": "✗F"}
COLUNAS = ["variante", "n", "acerto estrito", "acerto folgado", "skill INDEVIDA", "null indevido", "skill errada",
           "aceitável (não a melhor)", "sem sugestão (falha)", "req/pedido", "tokens/pedido", "US$/1000", "p50_ms", "p95_ms"]


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador (LEIA-ME: "difícil: <família> — detalhe")."""
    nota = c.get("nota") or ""
    if nota.startswith("difícil:"):
        return re.split(r"\s+[—–-]\s+", nota[len("difícil:"):].strip(), maxsplit=1)[0].strip()
    return "fácil / outros"


def rodar(casos: list[dict], catalogo: list[dict], etapas: tuple) -> list[dict]:
    """Uma instância do cliente por pedido: latência e tokens ficam atribuídos ao pedido e ao FORMATO de cada
    requisição. Roda pelo invólucro `selecionar_seguro`: falha operacional vira "sem sugestão" daquele pedido."""
    def um(c: dict) -> dict:
        jev = Jev(AQUI / "cache")
        s = S.selecionar_seguro(jev, c["pedido"], catalogo, etapas=etapas)
        return {**s, "chamadas": [{**ch, "etapa": e} for ch, e in zip(jev.chamadas, s["etapas"])]}
    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(um, casos))


def vivo(s: dict) -> bool:
    return not s["longo"] and not s["falha"]


def _decidir(s: dict, limiares: dict) -> dict:
    """As decisões do pedido refeitas com outros limiares (os sinais são os mesmos: não chama nada)."""
    x = s["sinais"]
    return S.decidir(x["ampla"], x["fits_vencedor"], x["rerank"], x["todos"], limiares, x["ampla_completa"])


def escolha(s: dict, c: dict, linha: str, catalogo: list[dict], limiares: dict | None = None) -> tuple:
    """(skill escolhida ou None, sem_sugestao) de uma linha do relatório no MESMO caso."""
    if linha == BASE:
        return S.baseline(c["pedido"], catalogo, (limiares or P.LIMIAR)["baseline"])["skill"], False
    if not vivo(s):
        return None, True
    if linha == RECEITA_030:
        return _decidir(s, LIMIARES_RECEITA)["c"]["skill"], False
    return (_decidir(s, limiares)[linha] if limiares else s["decisoes"][linha])["skill"], False


def classe(e: str | None, sem: bool, c: dict) -> str:
    """melhor · aceitavel (∈ `aceitaveis`, não a melhor) · nula_certa · skill_indevida (ERRO CARO: carregou skill com
    gabarito `null`) · null_indevido (não carregou quando havia) · skill_errada (carregou outra, fora de `aceitaveis`)
    · sem_sugestao (falha operacional ou teto: não conta como acerto nem quando o gabarito é `null`)."""
    if sem:
        return "sem_sugestao"
    if c["skill"] is None:
        return "nula_certa" if e is None else "skill_indevida"
    if e is None:
        return "null_indevido"
    return "melhor" if e == c["skill"] else "aceitavel" if e in c["aceitaveis"] else "skill_errada"


def metricas(itens: list[tuple]) -> dict:
    """itens = [(escolha, sem_sugestao, caso)]."""
    cl = [classe(e, sem, c) for e, sem, c in itens]
    n, nulos = len(itens), sum(c["skill"] is None for _, _, c in itens)
    b = {"n": n, "nulos": nulos, "com": n - nulos, **{k: cl.count(k) for k in MARCA}}
    b["estrito"] = (b["melhor"] + b["nula_certa"]) / n
    b["folgado"] = (b["melhor"] + b["aceitavel"] + b["nula_certa"]) / n
    b["sugeriu"] = sum(e is not None for e, _, _ in itens)
    return {"n": n, "acerto estrito": b["estrito"], "acerto folgado": b["folgado"],
            "skill INDEVIDA": f"{b['skill_indevida']}/{nulos}", "null indevido": f"{b['null_indevido']}/{b['com']}",
            "skill errada": f"{b['skill_errada']}/{b['com']}", "aceitável (não a melhor)": f"{b['aceitavel']}/{b['com']}",
            "sem sugestão (falha)": f"{b['sem_sugestao']}/{n}", "_bruto": b}


def custo(saidas: list[dict], etapas: tuple) -> dict:
    """Tokens, custo e latência MEDIDOS nas requisições que a variante envia em produção. Latência por pedido = soma
    das requisições da variante (são sequenciais), como medidas na chamada real (o cache guarda a da chamada original)."""
    n = max(len(saidas), 1)
    por_caso = [[ch for ch in s["chamadas"] if ch["etapa"] in etapas] for s in saidas]
    ch = [x for caso in por_caso for x in caso]
    tk = sum(x["input_tokens"] for x in ch)
    lat = sorted(sum(x["ms"] for x in caso) for caso in por_caso if caso)
    return {"req/pedido": f"{len(ch) / n:.2f}", "tokens/pedido": round(tk / n),
            "US$/1000": f"{1000 * tk / 1e6 * PRECO_US_POR_MILHAO_ENTRADA / n:.4f}",
            "p50_ms": round(statistics.median(lat)) if lat else 0, "p95_ms": lat[min(len(lat) - 1, int(0.95 * len(lat)))] if lat else 0,
            "_req": len(ch), "_novas": sum(not x["cache"] for x in ch), "_tokens": tk}


def veredito(v: dict) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    lim = P.CRITERIO_CONTINUAR.get("limites")
    if not lim:
        return "_(critério ainda não fixado — só depois do ajuste)_"
    p, a, base = v[P.VARIANTE_PRINCIPAL]["_bruto"], v["a"]["_bruto"], v[BASE]["_bruto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    fr = lambda k, n: k / n if n else 0.0  # noqa: E731
    return M.tabela([
        {"critério": "1 skill indevida (gabarito `null`, carregou skill)", "medido": f"{p['skill_indevida']}/{p['nulos']} ({fr(p['skill_indevida'], p['nulos']):.3f})",
         "limite": f"≤ {lim['indevida_max_fracao']:.3f}", "passa": ok(fr(p["skill_indevida"], p["nulos"]) <= lim["indevida_max_fracao"])},
        {"critério": "2 acerto folgado", "medido": f"{p['folgado']:.3f} (baseline de código {base['folgado']:.3f})",
         "limite": f"≥ {base['folgado'] + lim['margem_folgado']:.3f}", "passa": ok(p["folgado"] >= base["folgado"] + lim["margem_folgado"])},
        {"critério": "3 contra a Choice única (a)", "medido": f"folgado {p['folgado']:.3f} × {a['folgado']:.3f}; indevidas {p['skill_indevida']} × {a['skill_indevida']}",
         "limite": "folgado ≥ e indevidas ≤", "passa": ok(p["folgado"] >= a["folgado"] and p["skill_indevida"] <= a["skill_indevida"])},
        {"critério": "4 null indevido (havia skill, não carregou)", "medido": f"{p['null_indevido']}/{p['com']} ({fr(p['null_indevido'], p['com']):.3f})",
         "limite": f"≤ {lim['null_indevido_max_fracao']:.3f}", "passa": ok(fr(p["null_indevido"], p["com"]) <= lim["null_indevido_max_fracao"])},
        {"critério": "5 skill errada (carregou outra, fora de `aceitaveis`)", "medido": f"{p['skill_errada']}/{p['com']} ({fr(p['skill_errada'], p['com']):.3f})",
         "limite": f"≤ {lim['errada_max_fracao']:.3f}", "passa": ok(fr(p["skill_errada"], p["com"]) <= lim["errada_max_fracao"])},
    ])


def varredura(vivos: list[tuple], catalogo: list[dict], linha: str, chave: str | None = None) -> str:
    """Cobertura × erro: a mesma variante com o portão em cada limiar da grade (o resto dos limiares fica como está).
    `a` e `a2` não têm portão: a grade vira piso de confiança da Choice (abaixo → nenhuma)."""
    chave = chave or {"e": "fits_todos", BASE: "baseline"}.get(linha, "fits")
    linhas = []
    for t in (GRADE_BASE if linha == BASE else GRADE):
        if linha in ("a", "a2"):
            itens = [(s["decisoes"][linha]["skill"] if s["decisoes"][linha]["sinal"] >= t else None, False, c) for s, c in vivos]
        else:
            itens = [(*escolha(s, c, linha, catalogo, {**P.LIMIAR, chave: t}), c) for s, c in vivos]
        b = metricas(itens)["_bruto"]
        linhas.append({"limiar": t, "sugeriu skill": f"{b['sugeriu']}/{b['n']}", "skill indevida": f"{b['skill_indevida']}/{b['nulos']}",
                       "skill errada": f"{b['skill_errada']}/{b['com']}", "null indevido": f"{b['null_indevido']}/{b['com']}",
                       "folgado": b["folgado"], "estrito": b["estrito"]})
    return M.tabela(linhas)


def ressalva(vivos: list[tuple]) -> tuple[str, dict]:
    """A ressalva de `padroes-das-receitas`: na receita o portão olha o MAIOR `fits` da shortlist, mas o vencedor vem
    da Choice `rerank`. Conta onde os dois apontam para candidatos diferentes e o que cada desenho entregou ali."""
    lim, abertos = P.LIMIAR["fits"], [(s, c) for s, c in vivos if s["sinais"]["rerank"]["porta"] >= P.LIMIAR["porta"]]
    div = [(s, c) for s, c in abertos if max(s["sinais"]["rerank"]["fits"], key=s["sinais"]["rerank"]["fits"].get) != s["sinais"]["rerank"]["vencedor"]]
    furo = [(s, c) for s, c in div if max(s["sinais"]["rerank"]["fits"].values()) >= lim
            and s["sinais"]["rerank"]["fits"][s["sinais"]["rerank"]["vencedor"]] < lim]
    cl = lambda s, c, v: classe(s["decisoes"][v]["skill"], False, c)  # noqa: E731
    bom = {"melhor", "aceitavel", "nula_certa"}
    r = {"n": len(vivos), "porta_aberta": len(abertos), "divergem": len(div), "furo": len(furo),
         "div_c_certo": sum(cl(s, c, "c") in bom for s, c in div), "div_d_certo": sum(cl(s, c, "d") in bom for s, c in div),
         "furo_c_certo": sum(cl(s, c, "c") in bom for s, c in furo), "furo_c2_certo": sum(cl(s, c, "c2") in bom for s, c in furo),
         "furo_d_certo": sum(cl(s, c, "d") in bom for s, c in furo),
         "c_x_c2": sum(s["decisoes"]["c"]["skill"] != s["decisoes"]["c2"]["skill"] for s, _ in vivos),
         "c_x_d": sum(s["decisoes"]["c"]["skill"] != s["decisoes"]["d"]["skill"] for s, _ in vivos)}
    out = [f"Porta aberta (≥ {P.LIMIAR['porta']}) em {r['porta_aberta']}/{r['n']} pedidos. Neles, o vencedor da Choice `rerank` e o "
           f"candidato de maior `fits` são skills DIFERENTES em **{r['divergem']}**; nesses, acerto folgado de `c` "
           f"(fica com a Choice) {r['div_c_certo']}/{r['divergem']} × `d` (fica com o maior `fits`) {r['div_d_certo']}/{r['divergem']}. "
           f"O furo que a ressalva descreve — o maior `fits` passa o portão (≥ {lim}) mas o `fits` do vencedor consumido "
           f"está abaixo — aconteceu em **{r['furo']}** pedidos; neles, acerto folgado: `c` {r['furo_c_certo']}, `c2` (devolve "
           f"nenhuma) {r['furo_c2_certo']}, `d` {r['furo_d_certo']} de {r['furo']}. Decisão final diferente: `c` × `c2` em "
           f"{r['c_x_c2']} pedidos, `c` × `d` em {r['c_x_d']}.\n"]
    if div:
        out.append(M.tabela([{"id": c["id"], "gabarito": c["skill"] or "∅", "aceitáveis": " ".join(c["aceitaveis"]) or "—",
                              "vencedor rerank (fits)": f"{s['sinais']['rerank']['vencedor']} ({s['sinais']['rerank']['fits'][s['sinais']['rerank']['vencedor']]:.2f})",
                              "maior fits": "{} ({:.2f})".format(*max(s["sinais"]["rerank"]["fits"].items(), key=lambda kv: kv[1])),
                              **{v: f"{s['decisoes'][v]['skill'] or '∅'} {MARCA[cl(s, c, v)]}" for v in ("c", "c2", "d")},
                              "furo": "sim" if (s, c) in furo else ""} for s, c in div]) + "\n")
    return "\n".join(out), r


def secao_conjunto(nome: str, dados: dict, catalogo: list[dict]) -> tuple[str, dict]:
    casos, etapas = dados["casos"], ETAPAS_DO_CONJUNTO[nome]
    LINHAS = linhas_de(etapas)
    saidas = rodar(casos, catalogo, etapas)
    vivos = [(s, c) for s, c in zip(saidas, casos) if vivo(s)]
    falhas = [(c["id"], s["motivo"]) for s, c in zip(saidas, casos) if not vivo(s)]
    itens = {l: [(*escolha(s, c, l, catalogo), c) for s, c in zip(saidas, casos)] for l in LINHAS}
    custos = {l: custo(saidas, S.ETAPAS["c" if l == RECEITA_030 else l]) if l != BASE else
              {"req/pedido": "0", "tokens/pedido": 0, "US$/1000": "0", "p50_ms": 0, "p95_ms": 0} for l in LINHAS}
    variantes = {l: {**metricas(itens[l]), **custos[l]} for l in LINHAS}
    dificeis, nulos = sum(familia(c) != "fácil / outros" for c in casos), sum(c["skill"] is None for c in casos)
    tudo = custo(saidas, etapas)
    resumo = {"linhas": LINHAS, "n": len(casos), "dificeis": dificeis, "nulos": nulos, "variantes": variantes, "falhas": len(falhas), "tudo": tudo,
              "modelos": sorted({ch["modelo"] for s in saidas for ch in s["chamadas"]})}

    out = [f"## Conjunto `{nome}` — {len(casos)} pedidos (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{dificeis} difíceis, {nulos} com gabarito `null`, {len(falhas)} sem sugestão por falha operacional ou teto; "
           f"catálogo de {len(catalogo)} skills\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if "a2" not in LINHAS:
        out.append("> A variante informativa a2 (Choice única com a descrição completa) não foi medida neste conjunto.\n")
    if falhas:
        out.append(f"> **{len(falhas)} pedidos sem sugestão — este conjunto NÃO é medição limpa**: " + "; ".join(f"{i}: {m}" for i, m in falhas) + "\n")

    # --- escolha
    out.append("### Escolha — baseline de código × variantes com Jev, nos mesmos pedidos\n")
    out.append("`estrito` = a skill exata do gabarito (ou nenhuma quando o gabarito é `null`). `folgado` = escolha ∈ `aceitaveis` "
               "(ou nenhuma quando `aceitaveis` é vazio). **Skill INDEVIDA** = erro caro: carregou skill com gabarito `null` "
               "(denominador = pedidos `null`). **Null indevido** = não carregou quando havia skill; **skill errada** = carregou "
               "outra, fora de `aceitaveis` (denominador dos dois = pedidos com skill). Custo e latência: só as requisições que a "
               f"variante envia em produção, medidas. Variante principal (a que o critério julga): **{ROTULO[P.VARIANTE_PRINCIPAL]}**.\n")
    out.append(M.tabela([{"variante": ROTULO[l], **variantes[l]} for l in LINHAS], COLUNAS) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(variantes) + "\n")
    if not vivos:
        return "\n".join(out), resumo

    # --- ressalva
    out.append("### A ressalva da receita oficial — o portão olha um candidato, o vencedor é outro?\n")
    texto, resumo["ressalva"] = ressalva(vivos)
    out.append(texto)

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador) — acertos folgados; erros caros da principal\n")
    fams = list(dict.fromkeys(familia(c) for c in casos if familia(c) != "fácil / outros")) + ["fácil / outros"]
    linhas = []
    for fam in fams:
        idx = [k for k, c in enumerate(casos) if familia(c) == fam]
        if not idx:
            continue
        conta = lambda l, alvos: sum(classe(*itens[l][k]) in alvos for k in idx)  # noqa: E731
        linhas.append({"família": fam, "n": len(idx), "`null`": sum(casos[k]["skill"] is None for k in idx),
                       **{l: conta(l, {"melhor", "aceitavel", "nula_certa"}) for l in LINHAS if l != RECEITA_030},
                       "indevida (principal)": conta(P.VARIANTE_PRINCIPAL, {"skill_indevida"}),
                       "null indevido (principal)": conta(P.VARIANTE_PRINCIPAL, {"null_indevido"}),
                       "errada (principal)": conta(P.VARIANTE_PRINCIPAL, {"skill_errada"})})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- sinais
    out.append("### Os sinais — o `fits` separa \"serve\" de \"não serve\"? E as portas da receita?\n")
    com = [(s, c) for s, c in vivos if c["skill"]]
    sem = [(s, c) for s, c in vivos if not c["skill"]]
    q = lambda xs, f: "—" if not xs else f"{sorted(xs)[min(len(xs) - 1, int(f * len(xs)))]:.2f}"  # noqa: E731
    do_gab = [s["sinais"]["todos"][c["skill"]] for s, c in com]
    max_sem = [max(s["sinais"]["todos"].values()) for s, c in sem]
    out.append(f"`fits` (requisição `todos`) da skill do gabarito, nos {len(com)} pedidos com skill: mínimo {q(do_gab, 0)}, "
               f"p10 {q(do_gab, 0.1)}, mediana {q(do_gab, 0.5)}. Maior `fits` do catálogo nos {len(sem)} pedidos `null` (aqui "
               f"alto = skill indevida em `e`): mediana {q(max_sem, 0.5)}, p90 {q(max_sem, 0.9)}, máximo {q(max_sem, 1.0)}. "
               f"A skill do gabarito é a de maior `fits` do catálogo em {sum(max(s['sinais']['todos'], key=s['sinais']['todos'].get) == c['skill'] for s, c in com)}/{len(com)}; "
               f"está na shortlist da ampla em {sum(c['skill'] in s['sinais']['ampla']['shortlist'] for s, c in com)}/{len(com)} "
               f"(alguma aceitável: {sum(bool(set(c['aceitaveis']) & set(s['sinais']['ampla']['shortlist'])) for s, c in com)}/{len(com)}) — "
               "o que a 2ª requisição não recebe, ela não recupera.\n")
    # Quem aponta a skill certa quando HÁ skill, sem portão nenhum: separa "escolher" de "decidir se carrega".
    maior = lambda d: max(d, key=d.get)  # noqa: E731
    apontam = {"ampla, descrição curta (1ª skill do ranking)": lambda s: s["sinais"]["ampla"]["shortlist"][0],
               "Choice `rerank`, texto completo, entre as 3": lambda s: s["sinais"]["rerank"]["vencedor"],
               "maior `fits` entre as 3 da shortlist": lambda s: maior(s["sinais"]["rerank"]["fits"]),
               "maior `fits` entre as 42": lambda s: maior(s["sinais"]["todos"])}
    if "a2" in LINHAS:
        apontam["ampla, descrição completa (1ª skill do ranking)"] = lambda s: s["sinais"]["ampla_completa"]["shortlist"][0]
    out.append(f"Quem aponta a skill certa nos {len(com)} pedidos com skill, sem portão (a 1ª skill do ranking, mesmo quando a "
               "Choice preferiu `none`):\n")
    out.append(M.tabela([{"quem aponta": k, "a melhor": f"{sum(f(s) == c['skill'] for s, c in com)}/{len(com)}",
                          "alguma aceitável": f"{sum(f(s) in c['aceitaveis'] for s, c in com)}/{len(com)}"} for k, f in apontam.items()]) + "\n")
    mudou = [(s, c) for s, c in com if s["sinais"]["rerank"]["vencedor"] != s["sinais"]["ampla"]["shortlist"][0]]
    out.append(f"A releitura com o texto completo (`rerank`) trocou a 1ª skill da ampla em {len(mudou)}/{len(com)} pedidos com skill: "
               f"passou a apontar a melhor em {sum(s['sinais']['rerank']['vencedor'] == c['skill'] for s, c in mudou)}, deixou de apontá-la em "
               f"{sum(s['sinais']['ampla']['shortlist'][0] == c['skill'] for s, c in mudou)}"
               + (" (" + "; ".join(f"{c['id']}: {s['sinais']['ampla']['shortlist'][0]} → {s['sinais']['rerank']['vencedor']}" for s, c in mudou) + ")" if mudou else "") + ".\n")
    portas_sem, portas_com = [s["sinais"]["rerank"]["porta"] for s, _ in sem], [s["sinais"]["rerank"]["porta"] for s, _ in com]
    out.append(f"Porta da receita (média das 3 orientadas; < {P.LIMIAR['porta']} = nenhuma): fechou em "
               f"{sum(p < P.LIMIAR['porta'] for p in portas_sem)}/{len(sem)} pedidos `null` e em "
               f"{sum(p < P.LIMIAR['porta'] for p in portas_com)}/{len(com)} pedidos com skill. Valores nos `null`: mínimo "
               f"{q(portas_sem, 0)}, mediana {q(portas_sem, 0.5)}, máximo {q(portas_sem, 1.0)}; nos com skill: mínimo {q(portas_com, 0)}, "
               f"mediana {q(portas_com, 0.5)}. A Choice ampla disse `none` em {sum(s['sinais']['ampla']['escolha'] is None for s, _ in sem)}/{len(sem)} "
               f"pedidos `null` e em {sum(s['sinais']['ampla']['escolha'] is None for s, _ in com)}/{len(com)} com skill.\n")
    rep = [(s["sinais"]["fits_vencedor"], s["sinais"]["rerank"]["fits"].get(s["sinais"]["ampla"]["escolha"]),
            s["sinais"]["todos"][s["sinais"]["ampla"]["escolha"]]) for s, _ in vivos if s["sinais"]["fits_vencedor"] is not None]
    if rep:
        d1 = [abs(a - b) for a, b, _ in rep if b is not None]
        d2 = [abs(a - c) for a, _, c in rep]
        out.append(f"O mesmo Noul em requisições diferentes (isolamento ≠ determinismo): o `fits` do vencedor da ampla foi pedido "
                   f"sozinho (`fits_vencedor`), junto de 2 candidatas (`rerank`) e junto das 42 (`todos`). Diferença absoluta "
                   f"sozinho × `rerank`: média {statistics.mean(d1):.3f}, máxima {max(d1):.3f} (n = {len(d1)}); sozinho × `todos`: "
                   f"média {statistics.mean(d2):.3f}, máxima {max(d2):.3f} (n = {len(d2)}).\n")

    # --- curvas
    out.append("### Cobertura × erro por limiar (o portão de cada variante em cada ponto da grade)\n")
    for l in [P.VARIANTE_PRINCIPAL, *(x for x in LINHAS if x not in (P.VARIANTE_PRINCIPAL, RECEITA_030))]:
        sinal = {"a": "piso na confiança da Choice (a variante medida não tem piso)", "a2": "piso na confiança da Choice (idem)",
                 "e": "limiar no maior `fits` do catálogo", BASE: "limiar na pontuação BM25"}.get(l, "limiar no `fits`")
        atual = "" if l in ("a", "a2") else f"; em uso: {P.LIMIAR[{'e': 'fits_todos', BASE: 'baseline'}.get(l, 'fits')]}"
        out.append(f"**{ROTULO[l]}** — {sinal}{atual}\n")
        out.append(varredura(vivos if l != BASE else list(zip(saidas, casos)), catalogo, l) + "\n")
    out.append(f"**{ROTULO['c']}** — limiar na PORTA da receita (média das 3 portas orientadas); em uso: {P.LIMIAR['porta']}\n")
    out.append(varredura(vivos, catalogo, "c", "porta") + "\n")

    # --- custo
    out.append("### Custo e latência por formato de requisição (medidos)\n")
    linhas = []
    for e in etapas:
        k = custo(saidas, (e,))
        ms = sorted(ch["ms"] for s in saidas for ch in s["chamadas"] if ch["etapa"] == e)
        linhas.append({"requisição": e, "enviadas": k["_req"], "novas (não cache)": k["_novas"],
                       "tokens por requisição": round(k["_tokens"] / max(k["_req"], 1)),
                       "p50_ms": round(statistics.median(ms)) if ms else 0, "p95_ms": ms[min(len(ms) - 1, int(0.95 * len(ms)))] if ms else 0,
                       "quem usa": ", ".join(v for v in [*P.VARIANTES, *P.INFORMATIVAS] if e in S.ETAPAS[v])})
    out.append(M.tabela(linhas) + "\n")
    out.append(f"Tudo o que esta execução usou: {tudo['_req']} requisições ({tudo['_novas']} novas), {tudo['_tokens']} tokens, "
               f"US$ {tudo['_tokens'] / 1e6 * PRECO_US_POR_MILHAO_ENTRADA:.4f} · modelo: {', '.join(resumo['modelos'])}. Latência = a da "
               "chamada original de cada requisição (o cache a guarda), medida com 8 pedidos em paralelo.\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("Marca: ✓ a melhor · ≈ aceitável · ✓∅ nenhuma (certo) · ✗I skill INDEVIDA · ✗N null indevido · ✗E skill errada · "
               "✗F sem sugestão por falha. `ampla` = vencedor (confiança; p(`none`)); `fits venc.` = Noul pedido sozinho; "
               "`shortlist` = as 3 da ampla com o `fits` de cada uma na `rerank`; `rerank` = vencedor (confiança); `porta` = média "
               "das 3 portas; `e` = skill de maior `fits` do catálogo (valor); `a2` = Choice com descrição completa (confiança).\n")
    cel = lambda k, l: f"{itens[l][k][0] or '∅'} {MARCA[classe(*itens[l][k])]}"  # noqa: E731
    linhas = []
    for k, (s, c) in enumerate(zip(saidas, casos)):
        linha = {"id": c["id"], "fam": familia(c), "gabarito": c["skill"] or "∅",
                 "outras aceitáveis": " ".join(a for a in c["aceitaveis"] if a != c["skill"]) or "—", "base": cel(k, BASE)}
        if not vivo(s):
            linhas.append({**linha, "a": s["motivo"]})
            continue
        x = s["sinais"]
        todos_max = max(x["todos"], key=x["todos"].get)
        linhas.append({**linha, "a": cel(k, "a"), "ampla": f"{x['ampla']['escolha'] or '∅'} ({x['ampla']['conf']:.2f}; {x['ampla']['p_nenhuma']:.2f})",
                       "fits venc.": "—" if x["fits_vencedor"] is None else f"{x['fits_vencedor']:.2f}", "b": cel(k, "b"),
                       "shortlist": " · ".join(f"{i} {x['rerank']['fits'][i]:.2f}" for i in x["ampla"]["shortlist"]),
                       "rerank": f"{x['rerank']['vencedor']} ({x['rerank']['conf']:.2f})", "porta": f"{x['rerank']['porta']:.2f}",
                       "c": cel(k, "c"), "c2": cel(k, "c2"), "d": cel(k, "d"), "e": f"{cel(k, 'e')} [{todos_max} {x['todos'][todos_max]:.2f}]",
                       "a2": f"{cel(k, 'a2')} ({x['ampla_completa']['conf']:.2f})" if "a2" in LINHAS else ""})
    out.append(M.tabela(linhas, ["id", "fam", "gabarito", "outras aceitáveis", "base", "a", "ampla", "fits venc.", "b", "shortlist",
                                 "rerank", "porta", "c", "c2", "d", "e", *(["a2"] if "a2" in LINHAS else [])]) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n"]
    out.append(M.tabela([{"conjunto": n, "variante": ROTULO[l], **r["variantes"][l]} for n, r in resumos.items() for l in r["linhas"]],
                        ["conjunto", *COLUNAS]) + "\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"], "gabarito `null`": r["nulos"],
                          "sem sugestão (falha)": r["falhas"], "requisições (todas as variantes)": r["tudo"]["_req"],
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
    catalogo = json.loads((AQUI / "dados" / "skills.json").read_text(encoding="utf-8"))["casos"]
    if "teste" in conjuntos:
        # O teste só roda com perguntas, política, dados, catálogo E critério congelados: o manifesto gravado ANTES tem de bater.
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
        texto, resumos[nome] = secao_conjunto(nome, dados, catalogo)
        partes.append(texto)
        print(f"{nome}: {resumos[nome]['tudo']['_req']} requisições, {resumos[nome]['tudo']['_novas']} novas")
    cabecalho = (f"Gerado por `run.py` em {datetime.date.today().isoformat()} (modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e "
                 f"amostra em cada seção). Perguntas, limiares, variante principal e critério: `perguntas.py`; validação, decisão "
                 f"e baseline: `selecao.py`; bateria do código (sem API): `testa_falhas.py`. Preço: US$ 0,042 por milhão de tokens "
                 f"de entrada. Limiares: {P.LIMIAR}; shortlist {P.SHORTLIST}; descrição curta {P.CURTA} caracteres; teto do pedido "
                 f"{P.TETO_CARACTERES} caracteres.\n\nCritério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    if args == ["rascunho"]:
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — selecao-de-skill (encanamento)\n\n{cabecalho}\n" + "\n".join(partes),
                                                     encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return
    texto = "# Resultados — selecao-de-skill\n\n" + cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    if "teste" in conjuntos and not RODADA1.exists():
        # A primeira execução COMPLETA com o teste É a rodada cega: fica preservada e nunca é reescrita por este script.
        # Falha operacional deixa o pedido pendente (não é resposta): rodar de novo envia só o que faltou — o cache
        # guarda o resto — e a rodada cega só é gravada quando todos os pedidos tiverem resposta.
        if resumos["teste"]["falhas"]:
            print(f"rodada cega INCOMPLETA: {resumos['teste']['falhas']} pedidos pendentes por falha operacional; rode de novo")
        else:
            RODADA1.write_text(texto, encoding="utf-8", newline="\n")
            print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
