"""Roda a "próxima pergunta" num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, proxima.py,
                             valores.py, run.py, dados/teste.json e o critério de continuar; hash de _comum/ só como
                             registro); o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA
                             execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Requisições por conversa (rodada 2): as da variante principal — a 1ª (Nouls) e, quando ela precisa, a 2ª (Choice
`next`) — são as que a produção faz e são medidas à parte; a medição acrescenta UMA de comparação (Choice única + a
`next` que a principal não chamou). O rascunho roda só as da principal. Conversa acima do teto não é enviada (sem
sugestão, contada à parte); falha operacional vira revisão da conversa, contada à parte. O cache em `cache/` faz
rodar de novo custar zero.
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
import proxima as X  # noqa: E402
from jevcache import PRECO_US_POR_MILHAO_ENTRADA, Jev  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
# Manifesto com hash do código executado (inclusive este arquivo), dos dados de teste e do critério de aceite.
# `_comum/` entra só como registro: mudar a infra comum não recusa o teste, mas fica anotado.
CONGELADOS = ["perguntas.py", "proxima.py", "valores.py", "run.py", "dados/teste.json"]
# O teste foi aberto na rodada 1 (cega, preservada em resultados-rodada1.md). Tudo o que este script gera agora é a
# rodada 2: código e perguntas mudados pelos achados da revisão do Codex, conhecendo o resultado do teste.
RODADA = ("**Rodada 2 — pós-revisão do Codex (2026-10-01), NÃO cega**: o teste já tinha sido aberto e rodado na rodada 1 "
          "(`resultados-rodada1.md`, intocado). Perguntas `answered.budget`/`neighbourhood`/`bedrooms` reescritas, valores "
          "em dinheiro lidos pelo código (`valores.py`) e postos no state, regra do orçamento em código, validação da 2ª "
          "etapa e custo da principal medido em requisições próprias → o state e as perguntas mudaram: chamadas novas.")
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
# Rótulo no relatório → como obter a escolha. As três primeiras são baselines de CÓDIGO (sem Jev).
B_LACUNA, B_PALAVRAS, B_NQN = "primeira lacuna (só CRM)", "lacuna + palavras-chave", "sempre no_question_needed"
BASELINES = [B_LACUNA, B_PALAVRAS, B_NQN]
ROTULO = {"unica": "Jev: Choice única (catálogo inteiro)", "mascarada": "Jev: Nouls + Choice única mascarada",
          "jev": "Jev: Nouls → candidatas → Choice `next`", "codigo": "Jev: Nouls + política de código",
          "hibrida": "Jev: Nouls + código nas essenciais, Choice `next` no resto"}
VARIANTES = [*BASELINES, *(ROTULO[v] for v in X.VARIANTES_JEV)]
PRINCIPAL = ROTULO[P.VARIANTE_PRINCIPAL]
CURTO = {"finalidade": "fin", "orcamento": "orc", "bairro": "bai", "quartos": "qua", "vagas": "vag", "prazo": "pra",
         "pet": "pet", "financiamento": "fnc", P.VISITA: "vis", P.NQN: "NQN", None: "—"}
LIMIARES_CONF = [0.0, 0.3, 0.5, 0.7, 0.9]
COLUNAS = ["variante", "n", "acerto (∈ aceitáveis)", "PROIBIDA escolhida", "NQN indevido", "fora do conjunto",
           "sem sugestão (revisão)", "acerto onde NQN não é aceitável", "perguntou algo"]
# Letra do motivo no caso a caso: de onde veio cada bloqueio (`detalhe` da saída de `proxima.sinais`).
LETRA = {"CRM": "C", "declarado pelo cliente": "N", "orçamento declarado, lido pelo código": "O", "anúncio específico": "A",
         "sem sentido (aluguel)": "S", "sem sentido (investidor)": "S"}


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador (LEIA-ME: "difícil: <família> — detalhe")."""
    nota = c.get("nota") or ""
    if nota.startswith("difícil:"):
        return re.split(r"\s+[—–-]\s+", nota[len("difícil:"):].strip(), maxsplit=1)[0].strip()
    return "fácil / outros"


def rodar(casos: list[dict], todas: bool) -> list[dict]:
    """Uma instância do cliente por conversa: latência e tokens ficam atribuídos à conversa e à ETAPA de cada
    requisição ("1" e "2" = as que a principal faz em produção; "comparacao" = só com `todas=True`). Roda pelo
    invólucro `julgar_seguro`: falha operacional vira revisão daquela conversa e é contada à parte."""
    def um(c: dict) -> dict:
        jev = Jev(AQUI / "cache")
        s = X.julgar_seguro(jev, c["conversa"], c["campos_conhecidos"], c["catalogo"], todas=todas)
        return {**s, "chamadas": [{**ch, "etapa": e} for ch, e in zip(jev.chamadas, s["etapas"])]}
    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(um, casos))


def vivo(s: dict) -> bool:
    """A conversa foi julgada: não passou do teto e não teve falha operacional."""
    return not s["longa"] and not s["falha"]


def bloqueados(s: dict) -> dict:
    """{item: evidência} dos bloqueios de uma saída."""
    return {b["id"]: b for b in s["bloqueadas"]}


def escolha(s: dict, c: dict, variante: str) -> str | None:
    """ID escolhido por cada variante no MESMO caso."""
    ids = [i["id"] for i in c["catalogo"]]
    if variante == B_LACUNA:
        return X.baseline_lacuna(c["campos_conhecidos"], ids)
    if variante == B_PALAVRAS:
        return X.baseline_palavras(c["conversa"], c["campos_conhecidos"], ids)
    if variante == B_NQN:
        return P.NQN
    return s["escolhas"][next(k for k, r in ROTULO.items() if r == variante)]


def classe(e: str | None, c: dict) -> str:
    """aceitavel · proibida (erro caro: perguntou o que já sabia ou o que não faz sentido) · nqn_indevido (deixou de
    perguntar o essencial) · fora (pergunta nem aceitável nem proibida: fora de hora) · sem_sugestao (teto, falha
    operacional ou item essencial em revisão: a etapa não sugere nada)."""
    if e in c["aceitaveis"]:
        return "aceitavel"
    if e in c["proibidas"]:
        return "proibida"
    if e == P.NQN:
        return "nqn_indevido"
    return "sem_sugestao" if e is None else "fora"


def metricas(itens: list[tuple]) -> dict:
    """itens = [(escolha, caso)]."""
    cl = [classe(e, c) for e, c in itens]
    sem_nqn = [k for k, (_, c) in zip(cl, itens) if P.NQN not in c["aceitaveis"]]
    b = {"n": len(itens), "acerto": cl.count("aceitavel") / len(itens), "proibida": cl.count("proibida"),
         "nqn_indevido": cl.count("nqn_indevido"), "fora": cl.count("fora"), "sem_sugestao": cl.count("sem_sugestao"),
         "sem_nqn": len(sem_nqn), "acerto_sem_nqn": sem_nqn.count("aceitavel"),
         "perguntou": sum(e not in (P.NQN, None) for e, _ in itens)}
    return {"n": b["n"], "acerto (∈ aceitáveis)": b["acerto"], "PROIBIDA escolhida": f"{b['proibida']}/{b['n']}",
            "NQN indevido": f"{b['nqn_indevido']}/{b['sem_nqn']}", "fora do conjunto": f"{b['fora']}/{b['n']}",
            "sem sugestão (revisão)": f"{b['sem_sugestao']}/{b['n']}",
            "acerto onde NQN não é aceitável": f"{b['acerto_sem_nqn']}/{b['sem_nqn']}",
            "perguntou algo": f"{b['perguntou']}/{b['n']}", "_bruto": b}


def bloqueio(saidas: list[dict], casos: list[dict]) -> tuple[list[dict], dict]:
    """Por item do catálogo: o que o código bloqueou (CRM, Noul, regra do orçamento, anúncio específico, sem sentido)
    e o que pôs em revisão × `proibidas`/`aceitaveis`, e o Noul `answered` cru. Item fora dos dois conjuntos não entra
    (o gabarito não diz nada sobre ele). Em revisão NÃO conta como bloqueada."""
    linhas, tot = [], {"proib": 0, "proib_bloq": 0, "aceit": 0, "aceit_bloq": 0, "proib_rev": 0, "aceit_rev": 0}
    for i in [*P.CAMPOS, P.VISITA]:
        pro = [s for s, c in zip(saidas, casos) if vivo(s) and i in c["proibidas"]]
        ace = [s for s, c in zip(saidas, casos) if vivo(s) and i in c["aceitaveis"]]
        cru = [(s["answered"][i], True) for s in pro] + [(s["answered"][i], False) for s in ace]
        rev = lambda xs: sum(any(r["id"] == i for r in s["em_revisao"]) for s in xs)  # noqa: E731
        tot["proib"] += len(pro); tot["proib_bloq"] += sum(i in bloqueados(s) for s in pro)  # noqa: E702
        tot["aceit"] += len(ace); tot["aceit_bloq"] += sum(i in bloqueados(s) for s in ace)  # noqa: E702
        tot["proib_rev"] += rev(pro); tot["aceit_rev"] += rev(ace)  # noqa: E702
        f = lambda xs, g: "—" if not xs else f"{g(xs):.2f}"  # noqa: E731
        linhas.append({"item": i, "proibidas bloqueadas": f"{sum(i in bloqueados(s) for s in pro)}/{len(pro)}",
                       "aceitáveis bloqueadas (indevido)": f"{sum(i in bloqueados(s) for s in ace)}/{len(ace)}",
                       "em revisão (proibidas · aceitáveis)": f"{rev(pro)} · {rev(ace)}",
                       "Noul cru ≥ limiar × proibida": M.acerto([(v >= P.LIMIAR["respondida"], g) for v, g in cru]),
                       "menor Noul entre proibidas": f([s["answered"][i] for s in pro], min),
                       "maior Noul entre aceitáveis": f([s["answered"][i] for s in ace], max),
                       "brier": M.brier(cru)})
    return linhas, tot


def veredito(variantes: dict, tot: dict) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    lim, j = P.CRITERIO_CONTINUAR["limites"], variantes[PRINCIPAL]["_bruto"]
    melhor = max(BASELINES, key=lambda v: variantes[v]["_bruto"]["acerto"])
    base, unica = variantes[melhor]["_bruto"]["acerto"], variantes.get(ROTULO["unica"], {}).get("_bruto")
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    div = lambda a, n: a / n if n else float("nan")  # noqa: E731
    cob, ind = div(tot["proib_bloq"], tot["proib"]), div(tot["aceit_bloq"], tot["aceit"])
    return M.tabela([
        {"critério": "1 pergunta proibida escolhida", "medido": f"{j['proibida']}/{j['n']}", "limite": f"≤ {lim['proibida_max']}",
         "passa": ok(j["proibida"] <= lim["proibida_max"])},
        {"critério": "2 acerto (∈ aceitáveis)", "medido": f"{j['acerto']:.3f} (melhor baseline de código: {melhor}, {base:.3f})",
         "limite": f"≥ {base + lim['margem_acerto']:.3f}", "passa": ok(j["acerto"] >= base + lim["margem_acerto"])},
        {"critério": "3 `no_question_needed` indevido", "medido": f"{j['nqn_indevido']}/{j['sem_nqn']}", "limite": f"≤ {lim['nqn_indevido_max']}",
         "passa": ok(j["nqn_indevido"] <= lim["nqn_indevido_max"])},
        {"critério": "4 contra a Choice única", "medido": f"acerto {j['acerto']:.3f} × {unica['acerto']:.3f}; proibidas {j['proibida']} × {unica['proibida']}",
         "limite": "acerto ≥ e proibidas ≤", "passa": ok(j["acerto"] >= unica["acerto"] and j["proibida"] <= unica["proibida"])}
        if unica else {"critério": "4 contra a Choice única", "medido": "não medida neste conjunto (sem requisição de comparação)",
                       "limite": "acerto ≥ e proibidas ≤", "passa": "—"},
        {"critério": "secundário: proibidas bloqueadas pelo código", "medido": f"{tot['proib_bloq']}/{tot['proib']} ({cob:.3f})",
         "limite": f"≥ {lim['proibidas_bloqueadas_min']}", "passa": ok(cob >= lim["proibidas_bloqueadas_min"])},
        {"critério": "secundário: aceitável bloqueada indevidamente", "medido": f"{tot['aceit_bloq']}/{tot['aceit']} ({ind:.3f})",
         "limite": f"≤ {lim['aceitavel_bloqueada_max']}", "passa": ok(ind <= lim["aceitavel_bloqueada_max"])},
    ])


def margem(s: dict) -> float:
    """"Julgamento mais fraco" (receita function-calling): menor distância ao limiar, ×2, entre os Nouls que decidiram
    o bloqueio (`withdrawn` para campo do CRM, `answered` para o resto). 0 = em cima do limiar; 1 = longe."""
    ds = [abs(s["withdrawn"][i] - P.LIMIAR["retirado"]) if i in s["withdrawn"] else abs(v - P.LIMIAR["respondida"])
          for i, v in s["answered"].items()]
    return min(1.0, 2 * min(ds))


def confianca(s: dict, v: str) -> float:
    """Confiança da decisão por variante: a da Choice que decidiu; sem Choice (só a válvula, ou política de código) = 1."""
    if v in ("unica", "mascarada"):
        return s["unica"]["conf"] if s["unica"] else 1.0
    usa_next = v == "jev" or (v == "hibrida" and not s["essenciais_faltando"])
    return s["next"]["conf"] if usa_next and s["next"] else 1.0


def curva(itens: list[tuple]) -> str:
    """itens = [(confiança, classe)] → cobertura automática × erro; abaixo do limiar = sem sugestão (o LLM/atendente decide)."""
    linhas = []
    for lim in LIMIARES_CONF:
        auto = [k for conf, k in itens if conf >= lim]
        linhas.append({"limiar": lim, "cobertura": len(auto) / len(itens),
                       "erro_automatico": (1 - auto.count("aceitavel") / len(auto)) if auto else float("nan"),
                       "proibidas": auto.count("proibida"), "nqn_indevido": auto.count("nqn_indevido"), "n_auto": len(auto)})
    return M.tabela(linhas)


def _fmt_nouls(s: dict) -> str:
    return " ".join(f"{CURTO[i]} {v:.2f}" for i, v in s["answered"].items())


def custo(saidas: list[dict], n: int) -> tuple[list[dict], dict]:
    """Tokens, custo e latência MEDIDOS por grupo de requisições (rodada 2, achado 4: nada estimado). As etapas "1" e
    "2" são exatamente o que `julgar(todas=False)` envia — o custo de produção da principal; "comparacao" só existe na
    medição. A latência por conversa soma as requisições do grupo, como medidas na chamada real (o cache guarda a
    latência da chamada original)."""
    p95 = lambda xs: xs[min(len(xs) - 1, int(0.95 * len(xs)))] if xs else 0  # noqa: E731

    def grupo(rotulo: str, etapas: set) -> dict:
        ch = [c for s in saidas for c in s["chamadas"] if c["etapa"] in etapas]
        lat = sorted(sum(c["ms"] for c in s["chamadas"] if c["etapa"] in etapas) for s in saidas
                     if any(c["etapa"] in etapas for c in s["chamadas"]))
        tk = sum(c["input_tokens"] for c in ch)
        return {"requisições medidas": rotulo, "requisições": len(ch), "novas (não cache)": sum(not c["cache"] for c in ch),
                "tokens por conversa": round(tk / max(n, 1)),
                "US$_por_1000_conversas": f"{1000 * tk / 1e6 * PRECO_US_POR_MILHAO_ENTRADA / max(n, 1):.4f}",
                "p50_ms por conversa": round(statistics.median(lat)) if lat else 0, "p95_ms por conversa": p95(lat)}

    principal = grupo(f"`{P.VARIANTE_PRINCIPAL}` em produção (`todas=False`): 1ª + 2ª quando precisa", {"1", "2"})
    linhas = [principal]
    if P.VARIANTE_PRINCIPAL == "hibrida":  # a 1ª requisição da `hibrida` é a requisição inteira da `codigo`
        linhas.append(grupo("`codigo` em produção: só a 1ª", {"1"}))
    linhas += [grupo("comparação (só na medição): Choice única + `next` onde a principal não chama", {"comparacao"}),
               grupo("tudo o que esta execução usou", {"1", "2", "comparacao"})]
    ch = [c for s in saidas for c in s["chamadas"]]
    por_etapa = lambda e: [c["input_tokens"] for c in ch if c["etapa"] == e]  # noqa: E731
    media = lambda xs: round(statistics.mean(xs)) if xs else 0  # noqa: E731
    ms = sorted(c["ms"] for c in ch)
    resumo = {"req": len(ch), "novas": sum(not c["cache"] for c in ch), "tokens": sum(c["input_tokens"] for c in ch),
              "us_mil": linhas[-1]["US$_por_1000_conversas"], "tokens_conversa": linhas[-1]["tokens por conversa"],
              "principal": principal, "com_2a": len(por_etapa("2")), "tok1": media(por_etapa("1")), "tok2": media(por_etapa("2")),
              "tokc": media(por_etapa("comparacao")), "p50_req": round(statistics.median(ms)) if ms else 0, "p95_req": p95(ms),
              "modelos": sorted({c["modelo"] for c in ch})}
    return linhas, resumo


def secao_conjunto(nome: str, dados: dict, todas: bool = True) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas = rodar(casos, todas)
    itens = {v: [(escolha(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    # Sem a requisição de comparação (`todas=False`, o rascunho) as variantes de comparação não existem neste conjunto.
    medidas = [v for v in VARIANTES if todas or v not in {ROTULO[k] for k in X.COMPARACAO}]
    chaves = [k for k in X.VARIANTES_JEV if ROTULO[k] in medidas]
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    sem_nqn = sum(P.NQN not in c["aceitaveis"] for c in casos)
    longas, falhas = sum(s["longa"] for s in saidas), [(c["id"], s["motivo"]) for s, c in zip(saidas, casos) if s["falha"]]
    resumo = {"n": len(casos), "dificeis": dificeis, "variantes": {v: metricas(itens[v]) for v in medidas}, "falhas": len(falhas)}
    vivos = [(s, c) for s, c in zip(saidas, casos) if vivo(s)]

    out = [f"## Conjunto `{nome}` — {len(casos)} conversas (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{dificeis} difíceis, {sem_nqn} em que `no_question_needed` NÃO é aceitável, {longas} acima do teto, "
           f"{len(falhas)} falhas operacionais\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if falhas:
        out.append(f"> **{len(falhas)} falhas operacionais — este conjunto NÃO é medição**: "
                   + "; ".join(f"{i}: {m}" for i, m in falhas) + "\n")
    if len(medidas) < len(VARIANTES):
        out.append("> Sem requisição de comparação neste conjunto (`todas=False`): só as baselines de código e as variantes "
                   "que a 1ª e a 2ª requisição da principal alimentam.\n")

    # --- escolha
    out.append("### Escolha — baselines de código × variantes com Jev, nos mesmos casos\n")
    out.append("`acerto` = escolha ∈ `aceitaveis`. **PROIBIDA escolhida** = erro caro: perguntou o que o cliente já disse, o que o "
               "CRM já tem ou o que não faz sentido (∈ `proibidas`). **NQN indevido** = respondeu `no_question_needed` onde ele não "
               "é aceitável (deixou de perguntar o essencial); denominador = casos em que NQN não é aceitável. `fora do conjunto` = "
               "pergunta nem aceitável nem proibida (fora de hora). `sem sugestão (revisão)` = a etapa não devolveu pergunta: item "
               "essencial em revisão, falha operacional ou teto — NÃO conta como acerto. `perguntou algo` = escolha ≠ NQN. "
               f"Variante principal (a que o critério julga): **{PRINCIPAL}**.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in medidas], COLUNAS) + "\n")
    linhas_bloq, tot = bloqueio(saidas, casos)
    resumo["bloqueio"] = tot
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(resumo["variantes"], tot) + "\n")

    # --- bloqueio
    out.append("### Portão — o que o código bloqueou × `proibidas` do gabarito, por item\n")
    out.append("Bloqueada = campo do CRM não retirado (regra exata) · `answered` ≥ limiar (preferência DECLARADA pelo cliente) · "
               "`orcamento` pela regra do LEIA-ME sobre o valor lido pelo código · bairro e quartos do anúncio específico (regra) · "
               "sem sentido (`financiamento` em aluguel, `pet` de investidor). Em revisão = o código não deixa perguntar nem dá "
               "por respondido (não conta como bloqueada). `Noul cru` compara só o `answered` com o gabarito (proibida ⇒ alto; "
               "aceitável ⇒ baixo): na rodada 2 ele deixou de ser o portão em `orcamento` (o Noul diz se o valor é do cliente; "
               "aluguel + \"até 600\" é declarado E aceitável), em `bairro`/`quartos` com anúncio citado, e em `financiamento`/`pet` "
               "sem sentido — ali quem bloqueia é a regra. Item fora dos dois conjuntos não entra.\n")
    out.append(M.tabela(linhas_bloq) + "\n")
    out.append(f"Total: proibidas bloqueadas {tot['proib_bloq']}/{tot['proib']} · aceitáveis bloqueadas indevidamente "
               f"{tot['aceit_bloq']}/{tot['aceit']} · em revisão: {tot['proib_rev']} proibidas, {tot['aceit_rev']} aceitáveis\n")
    out.append("Cada bloqueio sai com `motivo` (`noul` | `regra`), a evidência e a margem (menor distância ao limiar, ×2, "
               "entre os Nouls que o sustentam: 0 = em cima do limiar):\n")
    motivos = {}
    for s, c in vivos:
        for i, e in bloqueados(s).items():
            k = motivos.setdefault((e["motivo"], e["detalhe"]), {"motivo": e["motivo"], "detalhe": e["detalhe"], "n": 0,
                                                                 "em proibidas": 0, "em aceitáveis": 0, "fora dos dois": 0, "_m": []})
            k["n"] += 1
            k["em proibidas" if i in c["proibidas"] else "em aceitáveis" if i in c["aceitaveis"] else "fora dos dois"] += 1
            k["_m"].append(e["margem"])
    out.append(M.tabela([{**{a: b for a, b in k.items() if a != "_m"}, "menor margem": f"{min(k['_m']):.2f}",
                          "margem < 0,3": sum(m < 0.3 for m in k["_m"])} for k in motivos.values()]) + "\n")
    ret = [(v, i in c["aceitaveis"]) for s, c in vivos for i, v in s["withdrawn"].items() if i in c["aceitaveis"] or i in c["proibidas"]]
    if ret:
        out.append(f"`withdrawn.<campo>` (campo do CRM retirado sem valor novo; gabarito = o campo voltou a ser aceitável): "
                   f"acerto a {P.LIMIAR['retirado']} = {M.acerto([(v >= P.LIMIAR['retirado'], g) for v, g in ret]):.3f} "
                   f"(n = {len(ret)}; {sum(g for _, g in ret)} retirados; maior valor entre os não retirados "
                   f"{max((v for v, g in ret if not g), default=float('nan')):.2f}; menor entre os retirados "
                   f"{min((v for v, g in ret if g), default=float('nan')):.2f})\n")

    # --- regra do orçamento
    out.append("### Regra do orçamento em código (CRM sem o campo) × gabarito\n")
    out.append("`respondida` = valor declarado (Noul) e lido pela regra → bloqueia · `confirmar` = aluguel + centenas sem unidade → "
               "candidata · `aberta` = sem valor, prestação em compra ou valor que não é limite do cliente → candidata · `revisar` = "
               "a regra não decide → nem pergunta nem bloqueio.\n")
    estados = {}
    for s, c in vivos:
        if s["orcamento"]:
            k = estados.setdefault(s["orcamento"]["estado"], {"estado": s["orcamento"]["estado"], "n": 0, "orcamento proibida": 0,
                                                              "orcamento aceitável": 0, "fora dos dois": 0})
            k["n"] += 1
            k["orcamento proibida" if "orcamento" in c["proibidas"] else "orcamento aceitável" if "orcamento" in c["aceitaveis"]
              else "fora dos dois"] += 1
    resumo["orcamento"] = estados
    out.append(M.tabela(list(estados.values())) + "\n")
    revisoes = [f"{c['id']} (`{r['id']}`: {r['detalhe']}; margem {r['margem']:.2f})" for s, c in vivos for r in s["em_revisao"]]
    out.append("Itens em revisão: " + ("; ".join(revisoes) if revisoes else "nenhum") + "\n")

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador) — acertos\n")
    fams = list(dict.fromkeys(familia(c) for c in casos if familia(c) != "fácil / outros")) + ["fácil / outros"]
    linhas = []
    for fam in fams:
        idx = [k for k, c in enumerate(casos) if familia(c) == fam]
        if not idx:
            continue
        conta = lambda v, alvo="aceitavel": sum(classe(*itens[v][k]) == alvo for k in idx)  # noqa: E731
        linhas.append({"família": fam, "n": len(idx), **{v.replace("Jev: ", ""): conta(v) for v in medidas if v != B_NQN},
                       "proibidas (principal)": conta(PRINCIPAL, "proibida"), "NQN indevido (principal)": conta(PRINCIPAL, "nqn_indevido"),
                       "sem sugestão (principal)": conta(PRINCIPAL, "sem_sugestao")})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curvas
    out.append("### Cobertura × erro por confiança (abaixo do limiar = sem sugestão; o agente decide sozinho)\n")
    for v in dict.fromkeys(k for k in (P.VARIANTE_PRINCIPAL, "jev", "mascarada", "unica") if k in chaves):
        out.append(f"**{ROTULO[v]}** — confiança da Choice que decidiu (sem Choice = 1,0)\n")
        out.append(curva([(confianca(s, v), classe(s["escolhas"][v], c)) for s, c in vivos]) + "\n")
    out.append(f"**{PRINCIPAL}** — pelo Noul mais fraco (menor distância ao limiar ×2 entre os Nouls do portão)\n")
    out.append(curva([(margem(s), classe(s["escolhas"][P.VARIANTE_PRINCIPAL], c)) for s, c in vivos]) + "\n")

    # --- custo
    out.append("### Custo e latência — medidos por grupo de requisições (nada estimado)\n")
    linhas_custo, resumo["custo"] = custo(saidas, len(casos))
    out.append(M.tabela(linhas_custo) + "\n")
    cu = resumo["custo"]
    out.append(f"Conversas com 2ª requisição: {cu['com_2a']}/{len(casos)} · tokens médios: 1ª {cu['tok1']}, 2ª {cu['tok2']}, comparação "
               f"{cu['tokc']} · p50 / p95 por requisição: {cu['p50_req']} / {cu['p95_req']} ms · modelo: {', '.join(cu['modelos'])}. "
               "A linha da principal é o que `proxima.julgar(todas=False)` envia: a Choice única de comparação não está nela. "
               "Latência = a da chamada original de cada requisição (o cache a guarda).\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("`bloqueadas`: C = CRM · N = Noul `answered` (declarado pelo cliente) · O = regra do orçamento sobre o valor lido "
               "pelo código · A = anúncio específico (regra) · S = sem sentido; o número é a margem do bloqueio. `rev` = em "
               "revisão. `orçamento` = estado da regra e leitura do código (CRM sem o campo). `cand` = candidatas. Escolhas: "
               "`lac` primeira lacuna · `pal` palavras-chave · `única` (confiança) · `masc` · `next` (confiança) · `cód` · `híb`. "
               "Marca: ✓ aceitável · ✗P proibida · ✗N NQN indevido · ✗F fora do conjunto · ✗∅ sem sugestão. `answered` = Nouls "
               "crus; `ret` = `withdrawn`; `sinais` = rental / investor_not_living / specific_property / positive_reaction.\n")
    marca = {"aceitavel": "✓", "proibida": "✗P", "nqn_indevido": "✗N", "fora": "✗F", "sem_sugestao": "✗∅"}
    cel = lambda e, c: f"{CURTO[e]} {marca[classe(e, c)]}"  # noqa: E731
    med = lambda k, e, c: cel(e, c) if k in chaves else "—"  # noqa: E731
    linhas = []
    for k, (s, c) in enumerate(zip(saidas, casos)):
        linha = {"id": c["id"], "fam": familia(c), "aceitáveis": " ".join(CURTO[i] for i in c["aceitaveis"]),
                 "proibidas": " ".join(CURTO[i] for i in c["proibidas"]),
                 "lac": cel(itens[B_LACUNA][k][0], c), "pal": cel(itens[B_PALAVRAS][k][0], c)}
        if not vivo(s):
            linhas.append({**linha, "bloqueadas": "—", "rev": "—", "orçamento": "—", "cand": "—", "única": "—", "masc": "—",
                           "next": s["motivo"], "cód": "—", "híb": "✗∅"})
            continue
        e, o = s["escolhas"], s["orcamento"]
        leitura = o and o["leitura"]
        orc = "—" if not o else o["estado"] + (
            f" ({o['trecho']} → R$ {leitura['valor']:,} {leitura['tipo']})".replace(",", ".") if leitura and leitura["valor"] else
            f" ({o['trecho']})" if o["trecho"] else "")
        linhas.append({**linha,
                       "bloqueadas": " ".join(f"{CURTO[i]}:{LETRA[b['detalhe']]}{b['margem']:.2f}" for i, b in bloqueados(s).items()),
                       "rev": " ".join(CURTO[r["id"]] for r in s["em_revisao"]), "orçamento": orc,
                       "cand": " ".join(CURTO[i] for i in s["candidatas"]),
                       "única": f"{cel(e['unica'], c)} ({s['unica']['conf']:.2f})" if s["unica"] else "—",
                       "masc": med("mascarada", e["mascarada"], c),
                       "next": "—" if "jev" not in chaves else f"{cel(e['jev'], c)} ({s['next']['conf']:.2f})" if s["next"]
                       else f"{cel(e['jev'], c)} (sem Choice)",
                       "cód": cel(e["codigo"], c), "híb": cel(e["hibrida"], c),
                       "answered": _fmt_nouls(s), "ret": " ".join(f"{CURTO[i]} {v:.2f}" for i, v in s["withdrawn"].items()),
                       "sinais": " / ".join(f"{v:.2f}" for v in s["sinais"].values())})
    out.append(M.tabela(linhas, ["id", "fam", "aceitáveis", "proibidas", "bloqueadas", "rev", "orçamento", "cand", "lac", "pal", "única",
                                 "masc", "next", "cód", "híb", "answered", "ret", "sinais"]) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Escolha por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES
                         if v in r["variantes"]], ["conjunto", *COLUNAS]) + "\n")
    out.append("### Portão e custo (medido)\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"],
                          "proibidas bloqueadas": f"{r['bloqueio']['proib_bloq']}/{r['bloqueio']['proib']}",
                          "aceitáveis bloqueadas": f"{r['bloqueio']['aceit_bloq']}/{r['bloqueio']['aceit']}",
                          "em revisão (proibidas · aceitáveis)": f"{r['bloqueio']['proib_rev']} · {r['bloqueio']['aceit_rev']}",
                          "falhas operacionais": r["falhas"],
                          "principal: requisições": r["custo"]["principal"]["requisições"],
                          "principal: tokens por conversa": r["custo"]["principal"]["tokens por conversa"],
                          "principal: US$_por_1000": r["custo"]["principal"]["US$_por_1000_conversas"],
                          "principal: p50_ms": r["custo"]["principal"]["p50_ms por conversa"],
                          "principal: p95_ms": r["custo"]["principal"]["p95_ms por conversa"],
                          "tudo (com comparação): requisições": r["custo"]["req"], "novas (não cache)": r["custo"]["novas"],
                          "tudo: US$_por_1000": r["custo"]["us_mil"],
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; rodada 2, NÃO cega): {h}"


def _congelar() -> dict:
    """Grava o manifesto pela infra comum e anota, só como registro, o hash da infra comum que rodou."""
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    return "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_CONTINUAR.items() if k != "limites")


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
        # Só as requisições da principal (`todas=False`): o rascunho testa o encanamento de produção, sem comparação.
        texto, _ = secao_conjunto("rascunho", json.loads((AQUI / "dados" / "rascunho.json").read_text(encoding="utf-8")), todas=False)
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — proxima-pergunta (encanamento)\n\n{RODADA}\n\n{texto}",
                                                     encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — proxima-pergunta\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, limiares e variante "
                 f"principal: `perguntas.py`; valores em dinheiro: `valores.py`; validação, portão, regra do orçamento, candidatas "
                 f"e baselines: `proxima.py`; bateria do código (sem API): `testa_codigo.py`. Preço: US$ 0,042 por milhão "
                 f"de tokens de entrada. Teto da conversa: {P.TETO_TURNOS} turnos / {P.TETO_CARACTERES} caracteres (acima → sem "
                 f"sugestão, sem chamada). Limiares: {P.LIMIAR}; piso de preço de compra: {P.PISO_PRECO}.\n\n{RODADA}\n\n"
                 f"Critério de continuar/descartar (fixado antes da rodada 1 e mantido igual): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    if "teste" in conjuntos and not RODADA1.exists():
        # A primeira execução com o teste É a rodada cega: fica preservada e nunca é reescrita por este script.
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
