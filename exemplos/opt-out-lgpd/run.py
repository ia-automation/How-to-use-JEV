"""Roda o opt-out/LGPD num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py rascunho     só o encanamento (5 casos fáceis; não é métrica) → resultados-rascunho.md
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, optout.py,
                             run.py, dados/teste.json e o critério de continuar; hash de _comum/ só como registro);
                             o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA
                             execução com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por mensagem (todas as perguntas juntas); mensagem acima do teto não é enviada (revisar, contada à
parte). Falha operacional (chamada, cache faltando, resposta fora do contrato) NÃO aborta o lote: aquela mensagem
sai `revisar` por `optout.guardar_seguro` e é contada à parte — conjunto com falha não é medição do Jev.
O cache em `cache/` faz rodar de novo custar zero. Bateria do código (sem chave nem rede): `testa_falhas.py`.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import optout as O  # noqa: E402
import perguntas as P  # noqa: E402
from jevcache import Jev  # noqa: E402

ACOES = O.ACOES
RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
# Manifesto com hash do código executado (inclusive este arquivo), dos dados de teste e do critério de aceite.
# `_comum/` entra só como registro: mudar a infra comum não recusa o teste, mas fica anotado.
CONGELADOS = ["perguntas.py", "optout.py", "run.py", "dados/teste.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py"]
VARIANTES = ["baseline (expressões)", "sempre revisa", "Jev"]
PRINCIPAIS = {"opt_out": "opt_out", "temporary_pause": "pausa_temporaria", "lgpd_request": "pedido_lgpd"}  # Noul → campo do gabarito
# Grade da curva cobertura × erro (zero chamada nova): a MESMA faixa aplicada aos três Nouls principais.
GRADE_FAIXA = [(0.5, 0.5), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9)]
LIMIARES_CONF = [0.0, 0.3, 0.5, 0.7, 0.9]
COLUNAS_ACAO = ["variante", "n", "acerto_acao", "INFRAÇÃO (opt-out/LGPD real → seguir)", "obrigação pela metade",
                "BLOQUEIO INDEVIDO (sem opt-out nem LGPD → bloqueia)", "bloqueou c/ opt_out falso (todos)", "null → revisar",
                "revisou sem necessidade", "tipo LGPD certo (pedidos reais)"]


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador (LEIA-ME: "difícil: <família> — detalhe")."""
    nota = c.get("nota") or ""
    if nota.startswith("difícil:"):
        return re.split(r"\s+[—–-]\s+", nota[len("difícil:"):].strip(), maxsplit=1)[0].strip()
    return "fácil / outros"


def acao_esperada(c: dict) -> str:
    """Gabarito da ação pela mesma precedência do código: pedido LGPD > opt-out > pausa > seguir; `null` → revisar."""
    if c["pedido_lgpd"] is True:
        return "abrir_pedido_lgpd"
    if c["pedido_lgpd"] is None or c["opt_out"] is None:
        return "revisar"
    if c["opt_out"]:
        return "bloquear_envios"
    if c["pausa_temporaria"] is None:
        return "revisar"
    return "pausar" if c["pausa_temporaria"] else "seguir"


def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    """Uma requisição por mensagem dentro do teto, pelo mesmo invólucro que o consumidor usa (`guardar_seguro`):
    mensagem longa vira `revisar` sem chamada; falha operacional vira `revisar` SÓ naquela mensagem, sem abortar
    o lote. As duas são contadas à parte."""
    jev = Jev(AQUI / "cache")  # uma instância por conjunto: latência e tokens separados
    with ThreadPoolExecutor(8) as ex:  # mesmo paralelismo de `Jev.perguntar_varios`
        saidas = list(ex.map(lambda c: O.guardar_seguro(jev, c["mensagem"]), casos))
    custo = jev.resumo() or {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
                             "input_tokens": 0, "custo_us": 0.0, "modelos": []}
    custo["mensagens_longas"] = sum(bool(s.get("longa")) for s in saidas)
    custo["falhas_operacionais"] = sum(bool(s.get("falha")) for s in saidas)
    return saidas, custo


def sem_numeros(s: dict) -> bool:
    """Saída que não tem números do Jev (mensagem longa ou falha operacional): fora das métricas por pergunta."""
    return bool(s.get("longa") or s.get("falha"))


def automatico(s: dict) -> bool:
    """Decisão inteira sem humano: não foi a `revisar` e não deixou bloqueio pendente (`bloqueia=None`)."""
    return s["acao"] != "revisar" and s["bloqueia"] is not None


def saida_variante(s: dict, c: dict, variante: str) -> dict:
    """{acao, tipo_lgpd, bloqueia} de cada variante sobre o MESMO caso."""
    if variante.startswith("baseline"):
        return O.baseline(c["mensagem"])
    if variante == "sempre revisa":
        return {"acao": "revisar", "tipo_lgpd": None, "bloqueia": None}
    return {"acao": s["acao"], "tipo_lgpd": s["tipo_lgpd"], "bloqueia": s["bloqueia"]}


def obrigacao_perdida(v: dict, c: dict) -> str | None:
    """Erro caro do lado legal, sem `revisar` no meio: devolve o nome da perda ou None.
    `infração` = obrigação real (opt-out ou pedido LGPD) que saiu `seguir`. As outras são a obrigação atendida pela
    metade: opt-out real que virou `pausar` (o envio volta), pedido LGPD real que não abriu pedido, e pedido aberto
    sem bloquear o envio de quem também pediu para parar. O bloqueio só conta como cumprido com `bloqueia is True`:
    `None` (pendente, "quem atende confirma") é obrigação pela metade (revisão do Codex, 2026-10-01)."""
    if v["acao"] == "revisar":
        return None
    opt, lgpd = c["opt_out"] is True, c["pedido_lgpd"] is True
    if (opt or lgpd) and v["acao"] == "seguir":
        return "infração"
    if lgpd and v["acao"] != "abrir_pedido_lgpd":
        return "pedido LGPD não aberto"
    if opt and v["acao"] == "pausar":
        return "opt-out virou pausa"
    if opt and v["acao"] == "abrir_pedido_lgpd" and v["bloqueia"] is not True:
        return "pedido aberto sem bloqueio" if v["bloqueia"] is False else "pedido aberto com bloqueio pendente"
    return None


def metricas_acao(itens: list[tuple[dict, dict]]) -> dict:
    """itens = [(saída da variante, caso)]. Erros caros contados à parte, dos dois lados."""
    pares = [(v["acao"], acao_esperada(c)) for v, c in itens]
    obrig = [(v, c) for v, c in itens if c["opt_out"] is True or c["pedido_lgpd"] is True]
    livres = [(v, c) for v, c in itens if c["opt_out"] is False and c["pedido_lgpd"] is False]  # "sem opt-out nem LGPD"
    nulos = [(v, c) for v, c in itens if acao_esperada(c) == "revisar"]
    decidiveis = [(v, c) for v, c in itens if acao_esperada(c) != "revisar"]
    reais = [(v, c) for v, c in itens if c["pedido_lgpd"] is True]
    perdas = Counter(obrigacao_perdida(v, c) for v, c in obrig)
    opt_falso = [(v, c) for v, c in itens if c["opt_out"] is False]  # inclui pedido LGPD sem opt-out (acesso, exclusão parcial)
    b = {"acerto": M.acerto(pares), "infracao": perdas["infração"],
         "metade": sum(n for k, n in perdas.items() if k not in (None, "infração")), "obrig": len(obrig),
         "bloqueio_indevido": sum(v["bloqueia"] is True for v, _ in livres), "livres": len(livres),
         "nulo_revisar": sum(v["acao"] == "revisar" for v, _ in nulos), "nulos": len(nulos),
         "revisou_sem": sum(v["acao"] == "revisar" for v, _ in decidiveis), "decidiveis": len(decidiveis),
         "tipo_certo": sum(v["acao"] == "abrir_pedido_lgpd" and v["tipo_lgpd"] == c["tipo_lgpd"] for v, c in reais), "reais": len(reais)}
    return {
        "n": len(itens),
        "acerto_acao": b["acerto"],
        "INFRAÇÃO (opt-out/LGPD real → seguir)": f"{b['infracao']}/{b['obrig']}",
        "obrigação pela metade": f"{b['metade']}/{b['obrig']}",
        "BLOQUEIO INDEVIDO (sem opt-out nem LGPD → bloqueia)": f"{b['bloqueio_indevido']}/{b['livres']}",
        "bloqueou c/ opt_out falso (todos)": f"{sum(v['bloqueia'] is True for v, _ in opt_falso)}/{len(opt_falso)}",
        "null → revisar": f"{b['nulo_revisar']}/{b['nulos']}",
        "revisou sem necessidade": f"{b['revisou_sem']}/{b['decidiveis']}",
        "tipo LGPD certo (pedidos reais)": f"{b['tipo_certo']}/{b['reais']}",
        "_bruto": b,
    }


def veredito(variantes: dict) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    lim, j, base = P.CRITERIO_CONTINUAR["limites"], variantes["Jev"]["_bruto"], variantes[VARIANTES[0]]["_bruto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    div = lambda a, n: a / n if n else float("nan")  # noqa: E731
    linhas = [
        {"critério": "1 infração", "medido": f"{j['infracao']}/{j['obrig']}", "limite": f"≤ {lim['infracao_max']}", "passa": ok(j["infracao"] <= lim["infracao_max"])},
        {"critério": "2 obrigação pela metade", "medido": f"{j['metade']}/{j['obrig']}", "limite": f"≤ {lim['metade_max']}", "passa": ok(j["metade"] <= lim["metade_max"])},
        {"critério": "3 bloqueio indevido", "medido": f"{j['bloqueio_indevido']}/{j['livres']}", "limite": f"≤ {lim['bloqueio_indevido_max']}", "passa": ok(j["bloqueio_indevido"] <= lim["bloqueio_indevido_max"])},
        {"critério": "4 acerto da ação", "medido": f"{j['acerto']:.3f} (baseline {base['acerto']:.3f})", "limite": f"≥ {base['acerto'] + lim['margem_acao']:.3f}",
         "passa": ok(j["acerto"] >= base["acerto"] + lim["margem_acao"])},
        {"critério": "secundário: nulo → revisar", "medido": f"{j['nulo_revisar']}/{j['nulos']}", "limite": "todos", "passa": ok(j["nulo_revisar"] == j["nulos"])},
        {"critério": "secundário: revisou sem necessidade", "medido": f"{j['revisou_sem']}/{j['decidiveis']} ({div(j['revisou_sem'], j['decidiveis']):.3f})",
         "limite": f"≤ {lim['revisou_sem_necessidade_max']}", "passa": ok(div(j["revisou_sem"], j["decidiveis"]) <= lim["revisou_sem_necessidade_max"])},
        {"critério": "secundário: tipo LGPD certo", "medido": f"{j['tipo_certo']}/{j['reais']} ({div(j['tipo_certo'], j['reais']):.3f})",
         "limite": f"≥ {lim['tipo_certo_min']}", "passa": ok(div(j["tipo_certo"], j["reais"]) >= lim["tipo_certo_min"])},
    ]
    return M.tabela(linhas)


def matriz(pares: list[tuple[str, str]]) -> str:
    cont = Counter((g, p) for p, g in pares)
    return M.tabela([{"gabarito ↓ / previsto →": g, **{a: cont[(g, a)] for a in ACOES}} for g in ACOES])


def _redecidir(s: dict) -> dict:
    """Re-decide com as constantes atuais de `perguntas` a partir dos números guardados (sem cache nem API)."""
    return O.decidir({"answers": {
        "lgpd_type": {"type": "choice", "choice": s["tipo_escolha"], "confidence": s["tipo_conf"], "probabilities": s["tipo_probs"]},
        **{q: {"type": "noul", "noul": v} for q, v in s["nouls"].items()}}})


def curva(saidas: list[dict], casos: list[dict]) -> list[dict]:
    """Cobertura automática (não foi a `revisar` nem deixou bloqueio pendente) × erro entre automáticos, com a mesma
    faixa nos três Nouls principais. Troca as constantes no laço (o que um humano faria editando o arquivo) e
    restaura. A linha "atual" é a política do arquivo (faixas podem diferir por Noul)."""
    antes = P.FAIXA
    linhas = []
    try:
        for faixa in [None, *GRADE_FAIXA]:
            P.FAIXA = antes if faixa is None else {**antes, **{q: faixa for q in PRINCIPAIS}}
            ss = [s if sem_numeros(s) else _redecidir(s) for s in saidas]
            auto = [(s, c) for s, c in zip(ss, casos) if automatico(s)]
            linhas.append({"faixa (3 Nouls principais)": "atual (perguntas.py)" if faixa is None else f"{faixa[0]}–{faixa[1]}",
                           "cobertura_auto": len(auto) / len(casos),
                           "erro_automatico": (sum(s["acao"] != acao_esperada(c) for s, c in auto) / len(auto)) if auto else float("nan"),
                           "infrações": sum(obrigacao_perdida(s, c) == "infração" for s, c in auto),
                           "obrigação pela metade": sum(obrigacao_perdida(s, c) not in (None, "infração") for s, c in auto),
                           "bloqueios indevidos": sum(s["bloqueia"] is True and c["opt_out"] is False and c["pedido_lgpd"] is False for s, c in auto),
                           "bloqueio pendente (fora da cobertura)": sum(s["acao"] != "revisar" and s["bloqueia"] is None for s in ss),
                           "n_auto": len(auto)})
    finally:
        P.FAIXA = antes
    return linhas


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custo = rodar(casos)
    itens = {v: [(saida_variante(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    nulos = sum(c["opt_out"] is None for c in casos)
    resumo = {"n": len(casos), "dificeis": dificeis, "nulos": nulos, "custo": custo,
              "variantes": {v: metricas_acao(itens[v]) for v in VARIANTES}}

    out = [f"## Conjunto `{nome}` — {len(casos)} mensagens (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{dificeis} difíceis, {nulos} com `opt_out` nulo\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if custo["falhas_operacionais"]:
        out.append(f"> **{custo['falhas_operacionais']} falha(s) operacional(is)** neste conjunto: essas mensagens saíram `revisar` "
                   "sem resposta do Jev. **As métricas abaixo não são medição do Jev** — rode de novo.\n")

    # --- ação
    out.append("### Ação (5 classes) — métrica principal, baseline × sempre revisa × Jev nos mesmos casos\n")
    out.append("Gabarito da ação: `pedido_lgpd` → `abrir_pedido_lgpd`; `opt_out` nulo → `revisar`; `opt_out` → `bloquear_envios`; "
               "`pausa_temporaria` → `pausar`; senão `seguir`. **INFRAÇÃO** = opt-out ou pedido LGPD real que saiu `seguir`. "
               "`obrigação pela metade` = sem `seguir` e sem `revisar`, mas a obrigação não foi cumprida inteira: opt-out real → "
               "`pausar`; pedido LGPD real sem `abrir_pedido_lgpd`; pedido aberto sem bloquear quem também pediu para parar "
               "(bloqueio pendente, `bloq` = `?`, conta como não cumprido). "
               "**BLOQUEIO INDEVIDO** = mensagem sem opt-out nem pedido LGPD (cliente interessado, pausa, preferência, filtro) "
               "cujo envio foi bloqueado. `sempre revisa` = o custo de evitar todo erro: zero infração, 100% das mensagens a humano. "
               "`tipo LGPD certo` = pedido aberto com o tipo do gabarito, sobre os pedidos reais.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES], COLUNAS_ACAO) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(resumo["variantes"]) + "\n")
    out.append("**Matriz de confusão — Jev** (linhas = gabarito, colunas = previsto)\n")
    out.append(matriz([(v["acao"], acao_esperada(c)) for v, c in itens["Jev"]]) + "\n")
    out.append("**Matriz de confusão — baseline**\n")
    out.append(matriz([(v["acao"], acao_esperada(c)) for v, c in itens[VARIANTES[0]]]) + "\n")

    com_jev = [(s, c) for s, c in zip(saidas, casos) if not sem_numeros(s)]  # longa ou falha não tem números

    # --- Nouls principais
    out.append("### Nouls principais — acerto (≥ 0,5) contra o gabarito, faixa atual e Brier\n")
    out.append("`opt_out` é o pedido EXPLÍCITO de parar: nas exclusões o gabarito é `true` por regra de código (exclusão ⇒ "
               "opt-out), por isso há a linha sem os casos de exclusão. Gabarito nulo fica fora. `cobertura` = fração decidida "
               "fora da faixa de dúvida; `revisao` = casos dentro dela.\n")
    sub = {q: [(s["nouls"][q], c[campo]) for s, c in com_jev] for q, campo in PRINCIPAIS.items()}
    sub["opt_out (sem exclusões)"] = [(s["nouls"]["opt_out"], c["opt_out"]) for s, c in com_jev if c["tipo_lgpd"] != "exclusao"]
    linhas = []
    for q, it in sub.items():
        nao, sim = P.FAIXA[q.split(" ")[0]]
        linhas.append({"noul": q, "acerto": M.acerto([(v >= 0.5, g) for v, g in it]), "faixa": f"{nao}–{sim}",
                       **M.faixa_noul(it, nao, sim), "brier": M.brier(it)})
    resumo["nouls"] = {l["noul"]: l["acerto"] for l in linhas}
    out.append(M.tabela(linhas) + "\n")
    bloq = [(s["bloqueia"], c["opt_out"]) for s, c in zip(saidas, casos) if c["opt_out"] is not None]
    base_bloq = [(v["bloqueia"], c["opt_out"]) for v, c in itens[VARIANTES[0]] if c["opt_out"] is not None]
    resumo["bloqueia"] = {"jev": M.acerto(bloq), "baseline": M.acerto(base_bloq)}
    out.append(f"**`opt_out` composto** (bloqueio decidido pelo código: Noul + regra exclusão ⇒ opt-out; dúvida/`revisar` conta como "
               f"erro aqui): Jev {M.acerto(bloq):.3f} · baseline {M.acerto(base_bloq):.3f} (n = {len(bloq)})\n")

    # --- guardas
    out.append("### Nouls de guarda — valores por grupo (não têm campo próprio no gabarito)\n")
    grupos = {"stop_without_object": ("`opt_out` nulo", lambda c: c["opt_out"] is None),
              "wants_contact_to_continue": ("família negação", lambda c: familia(c) == "negação"),
              "about_another_contact": ("família terceiro", lambda c: familia(c) == "terceiro")}
    linhas = []
    for q, (rotulo, dentro) in grupos.items():
        a = sorted(s["nouls"][q] for s, c in com_jev if dentro(c))
        b = sorted(s["nouls"][q] for s, c in com_jev if not dentro(c))
        f = lambda xs: "—" if not xs else f"{xs[0]:.2f}–{xs[-1]:.2f}"  # noqa: E731
        linhas.append({"noul": q, "grupo": rotulo, "n_grupo": len(a), "mín–máx no grupo": f(a), "mín–máx fora": f(b),
                       "fora ≥ sim": sum(x >= P.FAIXA[q][1] for x in b), "faixa": f"{P.FAIXA[q][0]}–{P.FAIXA[q][1]}"})
    out.append(M.tabela(linhas) + "\n")

    # --- tipo LGPD
    reais = [(s, c) for s, c in com_jev if c["pedido_lgpd"] is True]
    out.append(f"### Tipo LGPD — Choice `lgpd_type` entre os {len(reais)} pedidos reais\n")
    cru = [(P.TIPO_DA_OPCAO[s["tipo_escolha"]], c["tipo_lgpd"]) for s, c in reais]
    na_acao = [(s["tipo_lgpd"] if s["acao"] == "abrir_pedido_lgpd" else None, c["tipo_lgpd"]) for s, c in reais]
    base_tipo = [(O.baseline(c["mensagem"])["tipo_lgpd"], c["tipo_lgpd"]) for _, c in reais]
    falsos_tipo = sum(P.TIPO_DA_OPCAO[s["tipo_escolha"]] is not None for s, c in com_jev if c["pedido_lgpd"] is False)
    resumo["tipo"] = {"cru": M.acerto(cru), "na_acao": M.acerto(na_acao), "baseline": M.acerto(base_tipo), "n": len(reais)}
    out.append(M.tabela([{"Choice crua (vencedor)": M.acerto(cru), "na ação (pedido aberto com o tipo certo)": M.acerto(na_acao),
                          "baseline": M.acerto(base_tipo), "n": len(reais),
                          "Choice ≠ none sem pedido real": f"{falsos_tipo}/{sum(c['pedido_lgpd'] is False for _, c in com_jev)}",
                          "piso de confiança": P.TIPO_CONF_MIN}]) + "\n")
    cont = Counter((g, p) for p, g in cru)
    out.append(M.tabela([{"gabarito ↓ / Choice →": g, **{str(t): cont[(g, t)] for t in [*O.TIPOS, None]}} for g in O.TIPOS]) + "\n")
    out.append("**Cobertura × erro por confiança da Choice** (pedidos reais)\n")
    out.append(M.tabela(M.cobertura_erro([(s["tipo_conf"], P.TIPO_DA_OPCAO[s["tipo_escolha"]] == c["tipo_lgpd"]) for s, c in reais], LIMIARES_CONF)) + "\n")

    # --- famílias
    out.append("### Por família difícil (pela `nota` do rotulador)\n")
    linhas = []
    fams = list(dict.fromkeys(familia(c) for c in casos if familia(c) != "fácil / outros")) + ["fácil / outros"]
    for fam in fams:
        grupo = [(s, c) for s, c in zip(saidas, casos) if familia(c) == fam]
        if not grupo:
            continue
        base = [(O.baseline(c["mensagem"]), c) for _, c in grupo]
        linhas.append({"família": fam, "n": len(grupo),
                       "ação Jev": M.acerto([(s["acao"], acao_esperada(c)) for s, c in grupo]),
                       "ação baseline": M.acerto([(b["acao"], acao_esperada(c)) for b, c in base]),
                       "Jev → revisar": sum(s["acao"] == "revisar" for s, _ in grupo),
                       "obrigação perdida Jev": sum(obrigacao_perdida(s, c) is not None for s, c in grupo),
                       "bloqueio indevido Jev": sum(s["bloqueia"] is True and c["opt_out"] is False and c["pedido_lgpd"] is False for s, c in grupo),
                       "obrigação perdida baseline": sum(obrigacao_perdida(b, c) is not None for b, c in base)})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- curvas
    out.append("### Cobertura × erro por faixa\n")
    out.append("**Política inteira** (mesmas respostas, outra faixa nos três Nouls principais; informativo no teste). "
               "`cobertura_auto` = não foi a `revisar` nem deixou bloqueio pendente (`bloqueia=None` num pedido aberto).\n")
    out.append(M.tabela(curva(saidas, casos)) + "\n")
    out.append("**Cada Noul principal sozinho** (cobertura = decidido fora da faixa; acerto entre os decididos)\n")
    linhas = []
    for q, campo in PRINCIPAIS.items():
        it = sub["opt_out (sem exclusões)"] if q == "opt_out" else sub[q]
        for nao, sim in GRADE_FAIXA:
            linhas.append({"noul": q + (" (sem exclusões)" if q == "opt_out" else ""), "faixa": f"{nao}–{sim}", **M.faixa_noul(it, nao, sim)})
    out.append(M.tabela(linhas) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "mensagens_longas (sem chamada)": custo["mensagens_longas"],
                          "falhas operacionais (→ revisar)": custo["falhas_operacionais"], "perguntas": custo["perguntas"],
                          "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_mensagem": round(custo["input_tokens"] / req),
                          "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_1000_mensagens": f"{1000 * custo['custo_us'] / req:.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("`opt`/`pausa`/`lgpd` = Nouls `opt_out`, `temporary_pause`, `lgpd_request`; `tipo` = vencedor da Choice (confiança); "
               "`cont`/`s/obj`/`terc` = guardas `wants_contact_to_continue`, `stop_without_object`, `about_another_contact`; "
               "`ok` compara a ação do Jev com o gabarito; `caro` marca obrigação perdida ou bloqueio indevido; `base` = baseline.\n")
    f2 = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731 — mensagem longa ou com falha não tem números
    linhas = []
    for s, c in zip(saidas, casos):
        gab, b, n = acao_esperada(c), O.baseline(c["mensagem"]), s["nouls"]
        caro = obrigacao_perdida(s, c) or ("bloqueio indevido" if s["bloqueia"] is True and c["opt_out"] is False and c["pedido_lgpd"] is False else "")
        tipo_ok = s["acao"] != "abrir_pedido_lgpd" or gab != "abrir_pedido_lgpd" or s["tipo_lgpd"] == c["tipo_lgpd"]
        linhas.append({"id": c["id"], "fam": familia(c), "gab": gab + (f"({c['tipo_lgpd']})" if c["tipo_lgpd"] else ""),
                       "opt": f2(n["opt_out"]), "pausa": f2(n["temporary_pause"]), "lgpd": f2(n["lgpd_request"]),
                       "tipo": f"{s['tipo_escolha']} ({f2(s['tipo_conf'])})", "cont": f2(n["wants_contact_to_continue"]),
                       "s/obj": f2(n["stop_without_object"]), "terc": f2(n["about_another_contact"]),
                       "ação Jev": s["acao"] + (f"({s['tipo_lgpd']})" if s["tipo_lgpd"] else ""),
                       "bloq": {True: "sim", False: "não", None: "?"}[s["bloqueia"]],
                       "ok": ("✓" if s["acao"] == gab else "✗") + ("" if tipo_ok else " tipo✗"), "caro": caro,
                       "base": b["acao"] + (f"({b['tipo_lgpd']})" if b["tipo_lgpd"] else ""), "motivo": s["motivo"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Ação por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES],
                        ["conjunto", *COLUNAS_ACAO]) + "\n")
    out.append("### Perguntas, tipo, custo\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"], "nulos": r["nulos"],
                          **{f"{q} ≥0,5": a for q, a in r["nouls"].items()},
                          "bloqueio composto Jev": r["bloqueia"]["jev"], "bloqueio composto baseline": r["bloqueia"]["baseline"],
                          "tipo LGPD (Choice crua)": r["tipo"]["cru"], "tipo baseline": r["tipo"]["baseline"],
                          "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_mensagem": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000": f"{1000 * r['custo']['custo_us'] / max(r['custo']['requisicoes'], 1):.4f}",
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
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — opt-out-lgpd (encanamento)\n\n{texto}", encoding="utf-8",
                                                     newline="\n")
        print("resultados-rascunho.md gerado")
        return

    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8")))
        partes.append(texto)
    cabecalho = (f"# Resultados — opt-out-lgpd\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas e política: "
                 f"`perguntas.py`; validação, ação e baseline: `optout.py`. Preço: US$ 0,042 por milhão de tokens de entrada. "
                 f"Teto da mensagem: {P.TETO_CARACTERES} caracteres (acima → revisar, sem chamada). Isto não é parecer jurídico.\n\n"
                 f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: r["custo"]["falhas_operacionais"] for n, r in resumos.items() if r["custo"]["falhas_operacionais"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — essas mensagens saíram `revisar` sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists():
        # A primeira execução com o teste É a rodada cega: fica preservada e nunca é reescrita por este script.
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
