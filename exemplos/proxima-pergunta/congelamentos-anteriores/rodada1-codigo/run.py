"""Roda a "próxima pergunta" num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, proxima.py,
                             run.py, dados/teste.json e o critério de continuar; hash de _comum/ só como registro);
                             o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA
                             execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Até duas requisições por conversa (a 2ª só quando sobra mais de uma candidata); conversa acima do teto não é
enviada (sem sugestão, contada à parte). O cache em `cache/` faz rodar de novo custar zero.
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
CONGELADOS = ["perguntas.py", "proxima.py", "run.py", "dados/teste.json"]
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
           "acerto onde NQN não é aceitável", "perguntou algo"]


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador (LEIA-ME: "difícil: <família> — detalhe")."""
    nota = c.get("nota") or ""
    if nota.startswith("difícil:"):
        return re.split(r"\s+[—–-]\s+", nota[len("difícil:"):].strip(), maxsplit=1)[0].strip()
    return "fácil / outros"


def rodar(casos: list[dict]) -> list[dict]:
    """Uma instância do cliente por conversa: latência e tokens ficam atribuídos à conversa (1ª + 2ª requisição)."""
    def um(c: dict) -> dict:
        jev = Jev(AQUI / "cache")
        s = X.julgar(jev, c["conversa"], c["campos_conhecidos"], c["catalogo"], todas=True)
        return {**s, "chamadas": jev.chamadas}
    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(um, casos))


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
    perguntar o essencial) · fora (pergunta nem aceitável nem proibida: fora de hora) · sem_sugestao (teto)."""
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
         "nqn_indevido": cl.count("nqn_indevido"), "fora": cl.count("fora") + cl.count("sem_sugestao"),
         "sem_nqn": len(sem_nqn), "acerto_sem_nqn": sem_nqn.count("aceitavel"),
         "perguntou": sum(e not in (P.NQN, None) for e, _ in itens)}
    return {"n": b["n"], "acerto (∈ aceitáveis)": b["acerto"], "PROIBIDA escolhida": f"{b['proibida']}/{b['n']}",
            "NQN indevido": f"{b['nqn_indevido']}/{b['sem_nqn']}", "fora do conjunto": f"{b['fora']}/{b['n']}",
            "acerto onde NQN não é aceitável": f"{b['acerto_sem_nqn']}/{b['sem_nqn']}",
            "perguntou algo": f"{b['perguntou']}/{b['n']}", "_bruto": b}


def bloqueio(saidas: list[dict], casos: list[dict]) -> tuple[list[dict], dict]:
    """Por item do catálogo: o que o código bloqueou (respondida, CRM ou sem sentido) × `proibidas`/`aceitaveis`, e o
    Noul `answered` cru. Item fora dos dois conjuntos não entra (o gabarito não diz nada sobre ele)."""
    linhas, tot = [], {"proib": 0, "proib_bloq": 0, "aceit": 0, "aceit_bloq": 0}
    for i in [*P.CAMPOS, P.VISITA]:
        pro = [s for s, c in zip(saidas, casos) if not s["longa"] and i in c["proibidas"]]
        ace = [s for s, c in zip(saidas, casos) if not s["longa"] and i in c["aceitaveis"]]
        cru = [(s["answered"][i], True) for s in pro] + [(s["answered"][i], False) for s in ace]
        tot["proib"] += len(pro); tot["proib_bloq"] += sum(i in s["bloqueadas"] for s in pro)  # noqa: E702
        tot["aceit"] += len(ace); tot["aceit_bloq"] += sum(i in s["bloqueadas"] for s in ace)  # noqa: E702
        f = lambda xs, g: "—" if not xs else f"{g(xs):.2f}"  # noqa: E731
        linhas.append({"item": i, "proibidas bloqueadas": f"{sum(i in s['bloqueadas'] for s in pro)}/{len(pro)}",
                       "aceitáveis bloqueadas (indevido)": f"{sum(i in s['bloqueadas'] for s in ace)}/{len(ace)}",
                       "Noul cru ≥ limiar × proibida": M.acerto([(v >= P.LIMIAR["respondida"], g) for v, g in cru]),
                       "menor Noul entre proibidas": f([s["answered"][i] for s in pro], min),
                       "maior Noul entre aceitáveis": f([s["answered"][i] for s in ace], max),
                       "brier": M.brier(cru)})
    return linhas, tot


def veredito(variantes: dict, tot: dict) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    lim, j = P.CRITERIO_CONTINUAR["limites"], variantes[PRINCIPAL]["_bruto"]
    melhor = max(BASELINES, key=lambda v: variantes[v]["_bruto"]["acerto"])
    base, unica = variantes[melhor]["_bruto"]["acerto"], variantes[ROTULO["unica"]]["_bruto"]
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
         "limite": "acerto ≥ e proibidas ≤", "passa": ok(j["acerto"] >= unica["acerto"] and j["proibida"] <= unica["proibida"])},
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
        return s["unica"]["conf"]
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


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas = rodar(casos)
    itens = {v: [(escolha(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    sem_nqn = sum(P.NQN not in c["aceitaveis"] for c in casos)
    longas = sum(s["longa"] for s in saidas)
    resumo = {"n": len(casos), "dificeis": dificeis, "variantes": {v: metricas(itens[v]) for v in VARIANTES}}
    vivos = [(s, c) for s, c in zip(saidas, casos) if not s["longa"]]

    out = [f"## Conjunto `{nome}` — {len(casos)} conversas (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{dificeis} difíceis, {sem_nqn} em que `no_question_needed` NÃO é aceitável, {longas} acima do teto\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")

    # --- escolha
    out.append("### Escolha — baselines de código × variantes com Jev, nos mesmos casos\n")
    out.append("`acerto` = escolha ∈ `aceitaveis`. **PROIBIDA escolhida** = erro caro: perguntou o que o cliente já disse, o que o "
               "CRM já tem ou o que não faz sentido (∈ `proibidas`). **NQN indevido** = respondeu `no_question_needed` onde ele não "
               "é aceitável (deixou de perguntar o essencial); denominador = casos em que NQN não é aceitável. `fora do conjunto` = "
               "pergunta nem aceitável nem proibida (fora de hora). `perguntou algo` = escolha ≠ NQN. "
               f"Variante principal (a que o critério julga): **{PRINCIPAL}**.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES], COLUNAS) + "\n")
    linhas_bloq, tot = bloqueio(saidas, casos)
    resumo["bloqueio"] = tot
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(resumo["variantes"], tot) + "\n")

    # --- bloqueio
    out.append("### Portão — o que o código bloqueou × `proibidas` do gabarito, por item\n")
    out.append("Bloqueada = campo do CRM não retirado (regra exata) · `answered` ≥ limiar · sem sentido (`financiamento` em "
               "aluguel, `pet` de investidor). `Noul cru` compara só o `answered` com o gabarito (proibida ⇒ alto; aceitável ⇒ "
               "baixo): em `financiamento` e `pet` parte das proibidas é \"sem sentido\", onde o Noul cru é baixo de propósito — "
               "quem bloqueia ali é a regra de sentido. Item fora dos dois conjuntos não entra.\n")
    out.append(M.tabela(linhas_bloq) + "\n")
    out.append(f"Total: proibidas bloqueadas {tot['proib_bloq']}/{tot['proib']} · aceitáveis bloqueadas indevidamente "
               f"{tot['aceit_bloq']}/{tot['aceit']}\n")
    motivos = {}
    for s, c in vivos:
        for i, m in s["bloqueadas"].items():
            k = motivos.setdefault(m, {"motivo do bloqueio": m, "n": 0, "em proibidas": 0, "em aceitáveis": 0, "fora dos dois": 0})
            k["n"] += 1
            k["em proibidas" if i in c["proibidas"] else "em aceitáveis" if i in c["aceitaveis"] else "fora dos dois"] += 1
    out.append(M.tabela(list(motivos.values())) + "\n")
    ret = [(v, i in c["aceitaveis"]) for s, c in vivos for i, v in s["withdrawn"].items() if i in c["aceitaveis"] or i in c["proibidas"]]
    if ret:
        out.append(f"`withdrawn.<campo>` (campo do CRM retirado sem valor novo; gabarito = o campo voltou a ser aceitável): "
                   f"acerto a {P.LIMIAR['retirado']} = {M.acerto([(v >= P.LIMIAR['retirado'], g) for v, g in ret]):.3f} "
                   f"(n = {len(ret)}; {sum(g for _, g in ret)} retirados; maior valor entre os não retirados "
                   f"{max((v for v, g in ret if not g), default=float('nan')):.2f}; menor entre os retirados "
                   f"{min((v for v, g in ret if g), default=float('nan')):.2f})\n")

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador) — acertos\n")
    fams = list(dict.fromkeys(familia(c) for c in casos if familia(c) != "fácil / outros")) + ["fácil / outros"]
    linhas = []
    for fam in fams:
        idx = [k for k, c in enumerate(casos) if familia(c) == fam]
        if not idx:
            continue
        conta = lambda v, alvo="aceitavel": sum(classe(*itens[v][k]) == alvo for k in idx)  # noqa: E731
        linhas.append({"família": fam, "n": len(idx), **{v.replace("Jev: ", ""): conta(v) for v in VARIANTES if v != B_NQN},
                       "proibidas (principal)": conta(PRINCIPAL, "proibida"), "NQN indevido (principal)": conta(PRINCIPAL, "nqn_indevido")})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curvas
    out.append("### Cobertura × erro por confiança (abaixo do limiar = sem sugestão; o agente decide sozinho)\n")
    for v in dict.fromkeys((P.VARIANTE_PRINCIPAL, "jev", "mascarada", "unica")):
        out.append(f"**{ROTULO[v]}** — confiança da Choice que decidiu (sem Choice = 1,0)\n")
        out.append(curva([(confianca(s, v), classe(s["escolhas"][v], c)) for s, c in vivos]) + "\n")
    out.append(f"**{PRINCIPAL}** — pelo Noul mais fraco (menor distância ao limiar ×2 entre os Nouls do portão)\n")
    out.append(curva([(margem(s), classe(s["escolhas"][P.VARIANTE_PRINCIPAL], c)) for s, c in vivos]) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    ch = [c for s in saidas for c in s.get("chamadas", [])]
    por_conversa = sorted(sum(c["ms"] for c in s["chamadas"]) for s in saidas if s.get("chamadas"))
    ms = sorted(c["ms"] for c in ch)
    p95 = lambda xs: xs[min(len(xs) - 1, int(0.95 * len(xs)))] if xs else 0  # noqa: E731
    tok1 = [s["chamadas"][0]["input_tokens"] for s in saidas if s.get("chamadas")]
    tok2 = [s["chamadas"][1]["input_tokens"] for s in saidas if len(s.get("chamadas", [])) > 1]
    tokens = sum(c["input_tokens"] for c in ch)
    q1 = X.perguntas_etapa1([i["id"] for i in casos[0]["catalogo"]], {})
    fatia = len(json.dumps(q1["single_choice"])) / len(json.dumps(q1))
    resumo["custo"] = {"req": len(ch), "novas": sum(not c["cache"] for c in ch), "p50": round(statistics.median(por_conversa)) if por_conversa else 0,
                       "p95": p95(por_conversa), "tokens_conversa": round(tokens / max(len(casos), 1)),
                       "us_mil": 1000 * tokens / 1e6 * PRECO_US_POR_MILHAO_ENTRADA / max(len(casos), 1),
                       "modelos": sorted({c["modelo"] for c in ch})}
    out.append(M.tabela([{"conversas": len(casos), "requisições": len(ch), "novas (não cache)": resumo["custo"]["novas"],
                          "com 2ª requisição": len(tok2), "p50_ms por conversa (1ª+2ª)": resumo["custo"]["p50"],
                          "p95_ms por conversa": resumo["custo"]["p95"], "p50_ms por requisição": round(statistics.median(ms)) if ms else 0,
                          "p95_ms por requisição": p95(ms), "tokens 1ª (média)": round(statistics.mean(tok1)) if tok1 else 0,
                          "tokens 2ª (média)": round(statistics.mean(tok2)) if tok2 else 0,
                          "tokens por conversa": resumo["custo"]["tokens_conversa"],
                          "US$_por_1000_conversas": f"{resumo['custo']['us_mil']:.4f}", "modelo": ", ".join(resumo["custo"]["modelos"])}]) + "\n")

    def producao(v: str) -> dict:
        """Custo de UMA variante em produção: a medição acima faz tudo (comparação inclusive). Quem não usa a Choice
        única desconta a fatia dela na 1ª requisição (estimada por caracteres); a 2ª só conta onde a variante a faz."""
        usa2 = lambda s: len(s["chamadas"]) > 1 and (v == "jev" or (v == "hibrida" and not s["essenciais_faltando"]))  # noqa: E731
        sv = [s for s in saidas if s.get("chamadas")]
        desconto = {"unica": 1 - fatia, "mascarada": 0.0}.get(v, fatia)  # `unica` sozinha paga só a própria fatia
        tk = [s["chamadas"][0]["input_tokens"] * (1 - desconto) + (s["chamadas"][1]["input_tokens"] if usa2(s) else 0) for s in sv]
        lat = sorted(s["chamadas"][0]["ms"] + (s["chamadas"][1]["ms"] if usa2(s) else 0) for s in sv)
        media = statistics.mean(tk) if tk else 0.0
        return {"variante": ROTULO[v], "requisições": len(sv) + sum(usa2(s) for s in sv), "tokens por conversa (estimado)": round(media),
                "US$_por_1000_conversas (estimado)": f"{1000 * media / 1e6 * PRECO_US_POR_MILHAO_ENTRADA:.4f}",
                "p50_ms por conversa": round(statistics.median(lat)) if lat else 0, "p95_ms por conversa": p95(lat)}

    out.append(f"**Em produção, por variante** — a 1ª requisição medida carrega a Choice única de comparação (~{fatia:.0%} do texto "
               "das perguntas, por caracteres, com CRM vazio); quem não a usa tem essa fatia descontada (estimativa). A 2ª "
               "requisição só entra onde a variante a faz. Latência = soma das requisições que a variante faz, medidas com 8 "
               "conversas em paralelo.\n")
    resumo["producao"] = producao(P.VARIANTE_PRINCIPAL)
    out.append(M.tabela([producao(v) for v in X.VARIANTES_JEV]) + "\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("`bloqueadas`: C = CRM, R = `answered` ≥ limiar, S = sem sentido. `cand` = candidatas enviadas à Choice `next`. "
               "Escolhas: `lac` primeira lacuna · `pal` palavras-chave · `única` (confiança) · `masc` · `next` (confiança) · `cód` · `híb`. "
               "Marca: ✓ aceitável · ✗P proibida · ✗N NQN indevido · ✗F fora do conjunto. `answered` = Nouls crus; `ret` = "
               "`withdrawn`; `sinais` = rental / investor_not_living / specific_property / positive_reaction.\n")
    marca = {"aceitavel": "✓", "proibida": "✗P", "nqn_indevido": "✗N", "fora": "✗F", "sem_sugestao": "✗∅"}
    cel = lambda e, c: f"{CURTO[e]} {marca[classe(e, c)]}"  # noqa: E731
    linhas = []
    for k, (s, c) in enumerate(zip(saidas, casos)):
        linha = {"id": c["id"], "fam": familia(c), "aceitáveis": " ".join(CURTO[i] for i in c["aceitaveis"]),
                 "proibidas": " ".join(CURTO[i] for i in c["proibidas"]),
                 "lac": cel(itens[B_LACUNA][k][0], c), "pal": cel(itens[B_PALAVRAS][k][0], c)}
        if s["longa"]:
            linhas.append({**linha, "bloqueadas": "—", "cand": "—", "única": "—", "masc": "—", "next": s["motivo"], "cód": "—", "híb": "—"})
            continue
        e = s["escolhas"]
        linhas.append({**linha,
                       "bloqueadas": " ".join(f"{CURTO[i]}:{m[0].upper()}" for i, m in s["bloqueadas"].items()),
                       "cand": " ".join(CURTO[i] for i in s["candidatas"]),
                       "única": f"{cel(e['unica'], c)} ({s['unica']['conf']:.2f})", "masc": cel(e["mascarada"], c),
                       "next": f"{cel(e['jev'], c)} ({s['next']['conf']:.2f})" if s["next"] else f"{cel(e['jev'], c)} (sem Choice)",
                       "cód": cel(e["codigo"], c), "híb": cel(e["hibrida"], c),
                       "answered": _fmt_nouls(s), "ret": " ".join(f"{CURTO[i]} {v:.2f}" for i, v in s["withdrawn"].items()),
                       "sinais": " / ".join(f"{v:.2f}" for v in s["sinais"].values())})
    out.append(M.tabela(linhas, ["id", "fam", "aceitáveis", "proibidas", "bloqueadas", "cand", "lac", "pal", "única", "masc", "next", "cód",
                                 "híb", "answered", "ret", "sinais"]) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Escolha por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES],
                        ["conjunto", *COLUNAS]) + "\n")
    out.append("### Portão e custo\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"],
                          "proibidas bloqueadas": f"{r['bloqueio']['proib_bloq']}/{r['bloqueio']['proib']}",
                          "aceitáveis bloqueadas": f"{r['bloqueio']['aceit_bloq']}/{r['bloqueio']['aceit']}",
                          "requisições (tudo)": r["custo"]["req"], "tokens por conversa (tudo)": r["custo"]["tokens_conversa"],
                          "US$_por_1000 (tudo)": f"{r['custo']['us_mil']:.4f}",
                          "principal: requisições": r["producao"]["requisições"],
                          "principal: US$_por_1000 (estimado)": r["producao"]["US$_por_1000_conversas (estimado)"],
                          "principal: p50_ms": r["producao"]["p50_ms por conversa"], "principal: p95_ms": r["producao"]["p95_ms por conversa"],
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
        texto, _ = secao_conjunto("rascunho", json.loads((AQUI / "dados" / "rascunho.json").read_text(encoding="utf-8")))
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — proxima-pergunta (encanamento)\n\n{texto}", encoding="utf-8",
                                                     newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — proxima-pergunta\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, limiares e variante "
                 f"principal: `perguntas.py`; validação, portão, candidatas e baselines: `proxima.py`. Preço: US$ 0,042 por milhão "
                 f"de tokens de entrada. Teto da conversa: {P.TETO_TURNOS} turnos / {P.TETO_CARACTERES} caracteres (acima → sem "
                 f"sugestão, sem chamada). Limiares: {P.LIMIAR}.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    if "teste" in conjuntos and not RODADA1.exists():
        # A primeira execução com o teste É a rodada cega: fica preservada e nunca é reescrita por este script.
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
