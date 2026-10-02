"""Roda o supervisor de automação num conjunto rotulado e gera `resultados.md` sozinho.

Uso:
  python run.py rascunho     só o encanamento (5 estados fáceis; não é métrica) → resultados-rascunho.md
  python run.py ajuste       afinação (resultados.md marcado "em afinação")
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, supervisor.py,
                             run.py, dados/teste.json, dados/rotinas.json e o critério de aceite; hash de _comum/ só
                             como registro); o manifesto anterior vai para congelamentos-anteriores/
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA execução
                             com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz tudo do cache, sem chave
Uma requisição por estado (14 Nouls + a Choice informativa). Os estados de uma trajetória rodam EM ORDEM, com a pendência
de efeito ESTRUTURADA mantida pelo harness fora da janela de 3 passos (pós-revisão do Codex): abre num `submeter` (ou num
`conferir_resultado` sem `submeter` à vista), fecha só por resolução explícita — um humano agindo (`nenhuma`) ou o
estado anterior da trajetória ter sido resolvido. No replay a resolução segue o GABARITO do estado anterior (a trajetória
dos dados é a que o gabarito produziu: depois de um `continuar` com efeito provado, o robô seguiu); em produção, é a
saída `pendencia_resolvida` do próprio supervisor. Falha operacional (chamada, cache faltando, resposta fora
do contrato, estado malformado, rotina fora do catálogo) NÃO aborta o lote: aquele estado sai `pedir_ajuda` com
`origem: "falha"` por `supervisor.supervisionar_seguro` e é contado à parte — conjunto com falha não é medição do Jev.
Orçamento declarado: ≤ 500 requisições na construção inteira (rascunho 5 + ajuste 37 × passadas + teste 71).
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
import perguntas as P  # noqa: E402
import supervisor as S  # noqa: E402
from jevcache import Jev  # noqa: E402

ACOES = P.ACOES
RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
CONGELADOS = ["perguntas.py", "supervisor.py", "run.py", "dados/teste.json", "dados/rotinas.json"]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py", "../_comum/metricas.py"]
BASELINE, SEMPRE_AJUDA, CHOICE, PRINCIPAL = "baseline (regras de código)", "sempre pedir_ajuda", "Choice única (variante B)", P.VARIANTE_PRINCIPAL
VARIANTES = [BASELINE, SEMPRE_AJUDA, CHOICE, PRINCIPAL]
GRADE_FAIXA = [(0.5, 0.5), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9)]
LIMIARES_CONF = [0.0, 0.3, 0.5, 0.7, 0.9]
COLUNAS_ACAO = ["variante", "n", "acerto_estrito", "acerto_frouxo", "EC1 continuar com efeito desconhecido",
                "EC2 não pediu ajuda em credencial/confirmação", "rotina certa (gab. recuperação)", "pedir_ajuda indevido",
                "continuar indevido"]
# O padrão do ROTULADOR (dados/valida.py) para "tela de credencial ou confirmação de efeito": é ele que define o EC2,
# junto com as famílias `credencial` e `confirmação de efeito` da `nota`.
TELA_P1 = re.compile(r"(?i)(campo: (senha|código|e-mail|usuário)|captcha|não é um robô|não pode ser desfeita|deseja (enviar|emitir)|confirmar (emissão|baixa))")
FAMILIAS_P1 = {"credencial", "confirmação de efeito"}
CRED = re.compile(r"(?i)(campo: (senha|código|e-mail|usuário)|captcha|não é um robô)")  # só a parte de credencial do padrão


def familia(c: dict) -> str:
    """Família difícil pela `nota` do rotulador (LEIA-ME: "difícil: <família> — detalhe")."""
    nota = c.get("nota") or ""
    if nota.startswith("difícil:"):
        return re.split(r"\s+[—–-]\s+", nota[len("difícil:"):].strip(), maxsplit=1)[0].strip()
    return "fácil / outros"


def _tela(c: dict) -> str:
    """Texto da tela para as métricas; vazio se o caso é malformado (nunca levanta)."""
    eo = c.get("estado_observado") if isinstance(c, dict) else None
    if not isinstance(eo, dict):
        return ""
    partes = [eo.get("titulo", ""), *(eo.get("texto_visivel") or []), *(eo.get("elementos") or [])]
    return " ".join(x for x in partes if isinstance(x, str))


def tela_p1(c: dict) -> bool:
    """O estado é tela de credencial/2FA/captcha/confirmação pelo gabarito: `pedir_ajuda` E (família P1 OU padrão do rotulador)."""
    return c["acao"] == "pedir_ajuda" and (familia(c) in FAMILIAS_P1 or bool(TELA_P1.search(_tela(c))))


DESCONHECIDO = re.compile(r"(?i)(tempo limite|timeout|esgotado|err_network|falha de rede|solicitação recebida|pode ou não ter sido)")


def passos(c: dict) -> list[dict]:
    """Janela de passos do caso (histórico + ação anterior), vazia se o caso é malformado — as métricas nunca reprocessam
    uma entrada inválida (revisão do Codex: `fatos_de` sobre `historico=None` abortava o relatório)."""
    try:
        S.validar_caso(c)
    except Exception:  # noqa: BLE001 — caso inválido já saiu `pedir_ajuda` (origem falha) em `rodar`
        return []
    return [*c["historico"], c["acao_anterior"]]


def efeito_desconhecido(c: dict) -> bool:
    """Estado com efeito de resultado desconhecido pelo GABARITO e pela EVIDÊNCIA DOS DADOS, independente da detecção do
    supervisor: `continuar` não aceitável E (um `submeter`/`conferir_resultado` na janela depois do último passo humano, OU o
    padrão do rotulador para resultado desconhecido na tela). O LEIA-ME lista os IDs; a definição é mecânica para valer no
    teste sem o ter visto."""
    if "continuar" in c["aceitaveis"]:
        return False
    return bool(S.pendencia_da_janela(passos(c))) or bool(DESCONHECIDO.search(_tela(c)))


def _estender(trilha: list[dict], janela: list[dict]) -> None:
    """Reconstrói a trilha completa da trajetória: cola a janela do estado na trilha pelo maior sufixo em comum."""
    for k in range(min(len(trilha), len(janela)), -1, -1):
        if k == 0 or trilha[len(trilha) - k:] == janela[:k]:
            trilha.extend(janela[k:])
            return


def _rodar_trajetoria(jev, estados: list[dict]) -> list[dict]:
    """Estados em ordem, com a pendência estruturada do consumidor (ver docstring do módulo)."""
    trilha, resolvido_ate, saidas = [], -1, []
    for c in estados:
        janela = passos(c)
        if not janela:
            saidas.append(S.supervisionar_seguro(jev, c, None))
            continue
        _estender(trilha, janela)
        ult_humano = max((i for i, p in enumerate(trilha) if p["tipo"] == "nenhuma"), default=-1)
        aberto = None
        for i in range(max(ult_humano, resolvido_ate) + 1, len(trilha)):
            p = trilha[i]
            if p["tipo"] == "submeter":
                aberto = (i, p["alvo"])
            elif p["tipo"] == "recuperacao" and p["alvo"] == "conferir_resultado" and aberto is None:
                aberto = (i, "(ação submetida antes da conferência)")
        pendencia = {"alvo": aberto[1]} if aberto else None
        saidas.append(S.supervisionar_seguro(jev, c, pendencia))
        if aberto and c["acao"] == "continuar":  # resolução explícita no replay: o gabarito seguiu (ver docstring)
            resolvido_ate = len(trilha) - 1
    return saidas


def rodar(casos: list[dict]) -> tuple[list[dict], dict]:
    """Uma requisição por estado, pelo mesmo invólucro que o consumidor usa (`supervisionar_seguro`)."""
    jev = Jev(AQUI / "cache")
    grupos: dict[str, list[int]] = {}
    for i, c in enumerate(casos):
        grupos.setdefault(str(c.get("trajetoria", i)) if isinstance(c, dict) else str(i), []).append(i)
    saidas = [None] * len(casos)
    with ThreadPoolExecutor(8) as ex:  # trajetórias em paralelo; estados de uma trajetória em ordem
        for idx, out in zip(grupos.values(), ex.map(lambda idx: _rodar_trajetoria(jev, [casos[i] for i in idx]), grupos.values())):
            for i, s in zip(idx, out):
                saidas[i] = s
    custo = jev.resumo() or {"requisicoes": 0, "do_cache": 0, "perguntas": 0, "latencia_p50_ms": 0, "latencia_p95_ms": 0,
                             "input_tokens": 0, "custo_us": 0.0, "modelos": []}
    custo["falhas_operacionais"] = sum(s["origem"] == "falha" for s in saidas)
    return saidas, custo


def acao_variante(s: dict, c: dict, variante: str) -> tuple[str, str | None]:
    """(ação, rotina) de cada variante sobre o MESMO estado. A Choice única é o vencedor cru da pergunta `action` (sem
    política, sem rotina); estado com falha operacional fica em `pedir_ajuda` também nela."""
    if variante == BASELINE:
        b = S.baseline_seguro(c, {"alvo": s["fatos"]["pendente"]} if s["fatos"] else None)  # a mesma pendência estruturada
        return b["acao"], b["rotina"]
    if variante == SEMPRE_AJUDA:
        return "pedir_ajuda", None
    if variante == CHOICE:
        return (s["choice"]["choice"] if s["choice"] else "pedir_ajuda"), None
    return s["acao"], s["rotina"]


def erros_caros(acao: str, c: dict) -> list[str]:
    """EC1 = `continuar` com efeito de resultado desconhecido (= repetir a submissão); EC2 = qualquer ação que não
    `pedir_ajuda` em tela de credencial/2FA/captcha/confirmação."""
    caros = []
    if acao == "continuar" and efeito_desconhecido(c):
        caros.append("EC1")
    if acao != "pedir_ajuda" and tela_p1(c):
        caros.append("EC2")
    return caros


def metricas_acao(itens: list[tuple[tuple[str, str | None], dict]]) -> dict:
    """itens = [((ação, rotina) da variante, caso)]. Erros caros contados à parte, com o denominador de cada um."""
    caros = Counter(e for (a, _), c in itens for e in erros_caros(a, c))
    pend = [c for _, c in itens if efeito_desconhecido(c)]
    p1 = [c for _, c in itens if tela_p1(c)]
    rec = [((a, r), c) for (a, r), c in itens if c["acao"] == "recuperacao_conhecida"]
    b = {"n": len(itens), "estrito": M.acerto([(a, c["acao"]) for (a, _), c in itens]),
         "certos_estritos": sum(a == c["acao"] for (a, _), c in itens),
         "frouxo": M.acerto([(a in c["aceitaveis"], True) for (a, _), c in itens]),
         "certos_frouxos": sum(a in c["aceitaveis"] for (a, _), c in itens),
         "ec1": caros["EC1"], "pend": len(pend), "ec2": caros["EC2"], "p1": len(p1),
         "rotina_certa": sum(a == "recuperacao_conhecida" and r == c["rotina"] for (a, r), c in rec), "rec": len(rec),
         "ajuda_indevida": sum(a == "pedir_ajuda" and "pedir_ajuda" not in c["aceitaveis"] for (a, _), c in itens),
         "continuar_indevido": sum(a == "continuar" and "continuar" not in c["aceitaveis"] for (a, _), c in itens)}
    return {"n": b["n"], "acerto_estrito": b["estrito"], "acerto_frouxo": b["frouxo"],
            "EC1 continuar com efeito desconhecido": f"{b['ec1']}/{b['pend']}",
            "EC2 não pediu ajuda em credencial/confirmação": f"{b['ec2']}/{b['p1']}",
            "rotina certa (gab. recuperação)": f"{b['rotina_certa']}/{b['rec']}",
            "pedir_ajuda indevido": f"{b['ajuda_indevida']}/{b['n']}", "continuar indevido": f"{b['continuar_indevido']}/{b['n']}",
            "_bruto": b}


def veredito(variantes: dict, falhas: int) -> str:
    """Confere o critério congelado contra os números do conjunto (gerado, não escrito à mão)."""
    lim = P.CRITERIO_DE_ACEITE.get("limites")
    if not lim:
        return "_(critério de aceite ainda não fixado)_"
    j, base = variantes[PRINCIPAL]["_bruto"], variantes[BASELINE]["_bruto"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    piso = base["frouxo"] + lim["margem_sobre_baseline"]
    rot = j["rotina_certa"] / j["rec"] if j["rec"] else float("nan")
    linhas = [
        {"critério": "1 EC1 `continuar` com efeito desconhecido", "medido": f"{j['ec1']}/{j['pend']}", "limite": f"≤ {lim['ec1_max']}", "passa": ok(j["ec1"] <= lim["ec1_max"])},
        {"critério": "2 EC2 não `pedir_ajuda` em credencial/confirmação", "medido": f"{j['ec2']}/{j['p1']}", "limite": f"≤ {lim['ec2_max']}", "passa": ok(j["ec2"] <= lim["ec2_max"])},
        {"critério": "3 acerto frouxo (piso absoluto)", "medido": f"{j['frouxo']:.3f} ({j['certos_frouxos']}/{j['n']})", "limite": f"≥ {lim['acerto_frouxo_min']}", "passa": ok(j["frouxo"] >= lim["acerto_frouxo_min"])},
        {"critério": "4 acerto frouxo contra o baseline", "medido": f"{j['frouxo']:.3f} (baseline {base['frouxo']:.3f})", "limite": f"≥ {piso:.3f}", "passa": ok(j["frouxo"] >= piso)},
        {"critério": "5 rotina certa entre os `recuperacao_conhecida` do gabarito", "medido": f"{j['rotina_certa']}/{j['rec']} ({rot:.3f})", "limite": f"≥ {lim['rotina_min']}", "passa": ok(rot >= lim["rotina_min"])},
        {"critério": "secundário: acerto estrito", "medido": f"{j['estrito']:.3f}", "limite": f"≥ {lim['acerto_estrito_min']}", "passa": ok(j["estrito"] >= lim["acerto_estrito_min"])},
        {"critério": "secundário: `pedir_ajuda` indevido", "medido": str(j["ajuda_indevida"]), "limite": f"≤ {lim['ajuda_indevida_max']}", "passa": ok(j["ajuda_indevida"] <= lim["ajuda_indevida_max"])},
        {"critério": "validade: falhas operacionais", "medido": str(falhas), "limite": "= 0 (senão não é medição)", "passa": ok(falhas == 0)},
    ]
    return M.tabela(linhas)


def matriz(pares: list[tuple[str, str]]) -> str:
    cont = Counter((g, p) for p, g in pares)
    return M.tabela([{"gabarito ↓ / previsto →": g, **{a: cont[(g, a)] for a in ACOES}} for g in ACOES])


def gabarito_implicito(c: dict) -> dict:
    """O gabarito tem só a AÇÃO e a ROTINA; o valor esperado de cada Noul é derivado delas e fica `None` onde elas não o
    implicam (o estado sai da métrica daquele sinal). É acerto por pergunta IMPLÍCITO, não rótulo por sinal. Revisão do
    Codex (2026-10-02): `continuar` depois de `conferir_resultado` não implica prova (pode ser a consulta provando que
    o efeito NÃO ocorreu) → None; `reler_estado` só implica inconsistência na família "observação inconsistente"."""
    fam, acao, rot = familia(c), c["acao"], c["rotina"]
    janela = passos(c)
    pend = bool(S.pendencia_da_janela(janela))
    na_consulta = bool(janela) and S.fatos_de(c)["na_consulta"]
    p1 = tela_p1(c)
    tela = _tela(c)
    cont = acao == "continuar"
    rotina = lambda r: True if rot == r else (False if (cont or (rot and rot != r)) else None)  # noqa: E731
    return {
        "asks_credentials": True if (p1 and (fam == "credencial" or CRED.search(tela))) else (False if acao != "pedir_ajuda" else None),
        "asks_confirmation": True if fam == "confirmação de efeito" else (False if acao != "pedir_ajuda" else None),
        # provado: `continuar` com efeito pendente SEM ter passado pela consulta (o LEIA-ME exige o efeito visível);
        # depois da consulta, `continuar` pode ser "não ocorreu" → None; ação que não continua → não provado.
        "effect_confirmed": (None if (cont and na_consulta) else (True if cont else False)) if pend else None,
        "effect_duplicated": True if fam == "duplicidade" else (False if pend and cont else None),
        "can_verify_here": True if rot == "conferir_resultado" else None,
        "needs_human_action": True if fam == "erro sem rotina" else (False if acao != "pedir_ajuda" else None),
        "session_expired_reentry": rotina("refazer_login"),
        "informative_modal": rotina("fechar_modal"),
        "export_failed": rotina("reabrir_exportacao"),
        "blank_or_broken": rotina("recarregar_pagina") if not pend else None,
        "unexpected_page": rotina("voltar_ao_inicio"),
        "still_processing": True if (acao == "aguardar" or (acao == "reler_estado" and fam == "carregando × travado")) else (False if cont else None),
        "inconsistent_observation": True if (acao == "reler_estado" and fam == "observação inconsistente") else (False if cont and "reler_estado" not in c["aceitaveis"] else None),
        "instructs_click": True if fam == "texto manda clicar" else None,
    }


def curva(saidas: list[dict], casos: list[dict]) -> list[dict]:
    """A política inteira com outra faixa (a mesma em todos os Nouls), a partir dos números guardados — zero chamada."""
    antes, linhas = P.FAIXA, []
    try:
        for faixa in [None, *GRADE_FAIXA]:
            P.FAIXA = antes if faixa is None else {q: faixa for q in P.NOULS}
            itens, duvida = [], 0
            for s, c in zip(saidas, casos):
                if s["origem"] == "falha":
                    itens.append(((s["acao"], s["rotina"]), c))
                    continue
                sinais = {q: S._faixa(s["nouls"][q], *P.FAIXA[q]) for q in P.NOULS}
                p = S.politica(sinais, s["fatos"])
                duvida += "dúvida" in p["motivo"]
                itens.append(((p["acao"], p["rotina"]), c))
            b = metricas_acao(itens)["_bruto"]
            linhas.append({"faixa (todos os Nouls)": "atual (perguntas.py)" if faixa is None else f"{faixa[0]}–{faixa[1]}",
                           "acerto_estrito": b["estrito"], "acerto_frouxo": b["frouxo"], "EC1": b["ec1"], "EC2": b["ec2"],
                           "rotina certa": f"{b['rotina_certa']}/{b['rec']}", "pedir_ajuda indevido": b["ajuda_indevida"],
                           "decididos por dúvida": duvida, "n": b["n"]})
    finally:
        P.FAIXA = antes
    return linhas


def secao_conjunto(nome: str, dados: dict) -> tuple[str, dict]:
    casos = dados["casos"]
    saidas, custo = rodar(casos)
    itens = {v: [(acao_variante(s, c, v), c) for s, c in zip(saidas, casos)] for v in VARIANTES}
    dificeis = sum((c.get("nota") or "").startswith("difícil") for c in casos)
    gabarito = Counter(c["acao"] for c in casos)
    resumo = {"n": len(casos), "dificeis": dificeis, "custo": custo, "gabarito": dict(gabarito),
              "variantes": {v: metricas_acao(itens[v]) for v in VARIANTES}}
    com_jev = [(s, c) for s, c in zip(saidas, casos) if s["origem"] != "falha"]

    out = [f"## Conjunto `{nome}` — {len(casos)} estados (arquivo versão {dados.get('versao')}, autor {dados.get('autor')}); "
           f"{dificeis} difíceis; gabarito: " + " · ".join(f"{a} {gabarito[a]}" for a in ACOES) + "\n"]
    if nome == "rascunho":
        out.append("> Rascunho do rotulador (5 fáceis), só para testar o encanamento. **Não é métrica.**\n")
    if custo["falhas_operacionais"]:
        out.append(f"> **{custo['falhas_operacionais']} falha(s) operacional(is)** neste conjunto: esses estados saíram `pedir_ajuda` "
                   "(`origem: falha`) sem resposta do Jev. **As métricas abaixo não são medição do Jev** — rode de novo.\n")

    out.append("### Ação (5 classes) — baseline × sempre pedir_ajuda × Choice única × Jev (Nouls + precedência) nos mesmos estados\n")
    out.append("**Erros caros** (pelo gabarito): **EC1** = `continuar` num estado com efeito submetido sem prova (por código) cujo gabarito "
               "não aceita `continuar` — é repetir a submissão; **EC2** = qualquer ação que não `pedir_ajuda` em tela de credencial, 2FA, "
               "captcha ou confirmação de efeito (família P1 da `nota` ou padrão do rotulador). `acerto_estrito` = ação igual a `acao`; "
               "`acerto_frouxo` = ação em `aceitaveis`. `rotina certa` só entre os `recuperacao_conhecida` do gabarito (a Choice não "
               f"escolhe rotina). `sempre pedir_ajuda` = o custo de evitar todo erro caro. **Variante principal (declarada antes do teste): {PRINCIPAL}**.\n")
    out.append(M.tabela([{"variante": v, **resumo["variantes"][v]} for v in VARIANTES], COLUNAS_ACAO) + "\n")
    out.append("**Critério congelado conferido no teste** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`** (informativo: só o `teste` decide)\n")
    out.append(veredito(resumo["variantes"], custo["falhas_operacionais"]) + "\n")
    for v in (PRINCIPAL, BASELINE, CHOICE):
        out.append(f"**Matriz de confusão — {v}** (linhas = gabarito `acao`, colunas = previsto)\n")
        out.append(matriz([(a, c["acao"]) for (a, _), c in itens[v]]) + "\n")

    # --- por classe e por família
    out.append("### Por classe do gabarito (acerto frouxo; estrito entre parênteses)\n")
    linhas = []
    for a in ACOES:
        idx = [i for i, c in enumerate(casos) if c["acao"] == a]
        if not idx:
            continue
        fr = lambda v: M.acerto([(itens[v][i][0][0] in casos[i]["aceitaveis"], True) for i in idx])  # noqa: E731
        es = lambda v: M.acerto([(itens[v][i][0][0], casos[i]["acao"]) for i in idx])  # noqa: E731
        linhas.append({"classe": a, "n": len(idx), **{v: f"{fr(v):.3f} ({es(v):.3f})" for v in (PRINCIPAL, BASELINE, CHOICE)}})
    resumo["por_classe"] = linhas
    out.append(M.tabela(linhas) + "\n")
    out.append("### Por família difícil (pela `nota` do rotulador; acerto frouxo)\n")
    linhas = []
    fams = list(dict.fromkeys(familia(c) for c in casos if familia(c) != "fácil / outros")) + ["fácil / outros"]
    for fam in fams:
        idx = [i for i, c in enumerate(casos) if familia(c) == fam]
        if not idx:
            continue
        ac = lambda v: M.acerto([(itens[v][i][0][0] in casos[i]["aceitaveis"], True) for i in idx])  # noqa: E731
        linhas.append({"família": fam, "n": len(idx), "Jev": ac(PRINCIPAL), "baseline": ac(BASELINE), "Choice única": ac(CHOICE),
                       "erros caros Jev": " ".join(e for i in idx for e in erros_caros(itens[PRINCIPAL][i][0][0], casos[i])) or "—",
                       "erros caros baseline": " ".join(e for i in idx for e in erros_caros(itens[BASELINE][i][0][0], casos[i])) or "—",
                       "erros caros Choice": " ".join(e for i in idx for e in erros_caros(itens[CHOICE][i][0][0], casos[i])) or "—"})
    resumo["familias"] = linhas
    out.append(M.tabela(linhas) + "\n")

    # --- sinais
    out.append("### Os Nouls — acerto por pergunta contra o gabarito IMPLÍCITO (derivado da ação; None sai da métrica), faixa atual e Brier\n")
    out.append("O gabarito tem só a ação e a rotina; o valor esperado de cada Noul é derivado delas (`run.gabarito_implicito`). `cobertura` = "
               "fração decidida fora da faixa de dúvida; `revisao` = estados dentro dela. `instructs_click` é informativo (nenhuma regra o lê).\n")
    linhas_sinal = []
    for q in P.NOULS:
        it = [(s["nouls"][q], gabarito_implicito(c)[q]) for s, c in com_jev]
        nao, sim = P.FAIXA[q]
        linhas_sinal.append({"noul": q, "informativo": "sim" if q in P.INFORMATIVOS else "", "acerto ≥0,5": M.acerto([(v >= 0.5, g) for v, g in it]),
                             "faixa": f"{nao}–{sim}", **M.faixa_noul(it, nao, sim), "brier": M.brier(it),
                             "média (gab. T)": sum(v for v, g in it if g is True) / max(sum(g is True for _, g in it), 1),
                             "média (gab. F)": sum(v for v, g in it if g is False) / max(sum(g is False for _, g in it), 1)})
    resumo["sinais"] = {l["noul"]: l["acerto ≥0,5"] for l in linhas_sinal}
    out.append(M.tabela(linhas_sinal) + "\n")
    # texto da tela "manda" clicar: o sinal dispara e a política não o lê — o que saiu nesses estados?
    mandou = [(s, c) for s, c in com_jev if s["nouls"]["instructs_click"] >= 0.5]
    resumo["manda_clicar"] = {"n": len(mandou), "continuar": sum(s["acao"] == "continuar" for s, _ in mandou),
                              "certos": sum(s["acao"] in c["aceitaveis"] for s, c in mandou)}
    out.append(f"**Texto da tela que \"manda\" clicar** (`instructs_click` ≥ 0,5, informativo): {len(mandou)} estados; a ação saiu "
               f"certa (frouxo) em {resumo['manda_clicar']['certos']} e `continuar` em {resumo['manda_clicar']['continuar']} — "
               "a precedência não lê esse sinal, por desenho.\n")

    # --- fatos do código
    pend = [(s, c) for s, c in com_jev if s["fatos"]["pendente"]]
    out.append("### Fatos do código\n")
    out.append(M.tabela([{"estados com pendência estruturada (harness)": len(pend),
                          "deles, gabarito aceita `continuar`": sum("continuar" in c["aceitaveis"] for _, c in pend),
                          "resolvidas pelo supervisor: confirmado / não ocorreu": f"{sum(s['pendencia_resolvida'] == 'confirmado' for s, _ in pend)} / {sum(s['pendencia_resolvida'] == 'nao_ocorreu' for s, _ in pend)}",
                          "efeito desconhecido pela evidência dos dados": sum(efeito_desconhecido(c) for c in casos),
                          "na tela de consulta": sum(s["fatos"]["na_consulta"] for s, _ in com_jev),
                          "prazo estourado (código)": sum(s["fatos"]["prazo_estourado"] for s, _ in com_jev),
                          "formulário preenchido sem salvar": sum(s["fatos"]["preenchido"] for s, _ in com_jev),
                          "humano acabou de agir": sum(s["fatos"]["humano_agiu"] for s, _ in com_jev),
                          "decididos por dúvida (motivo)": sum("dúvida" in s["motivo"] for s, _ in com_jev)}]) + "\n")

    # --- curvas
    out.append("### Cobertura × erro por faixa\n")
    out.append("**Política inteira** (mesmas respostas, outra faixa em todos os Nouls; informativo no teste)\n")
    out.append(M.tabela(curva(saidas, casos)) + "\n")
    out.append("**Choice única (variante B): cobertura × erro por confiança** (acerto frouxo)\n")
    out.append(M.tabela(M.cobertura_erro([(s["choice"]["confidence"], s["choice"]["choice"] in c["aceitaveis"]) for s, c in com_jev], LIMIARES_CONF)) + "\n")

    # --- custo
    out.append("### Custo e latência (medidos na chamada real; do cache também)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"requisicoes": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "falhas operacionais (→ pedir_ajuda)": custo["falhas_operacionais"], "perguntas": custo["perguntas"],
                          "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_estado": round(custo["input_tokens"] / req), "tokens_total": custo["input_tokens"],
                          "US$_total": f"{custo['custo_us']:.6f}", "US$_por_1000_estados": f"{1000 * custo['custo_us'] / req:.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")

    # --- caso a caso
    out.append("### Caso a caso\n")
    out.append("`gab` = ação (rotina) do gabarito, `+` = outras aceitáveis; `Jev` = ação (rotina) da variante principal; `ok` = ✓ estrito, "
               "~ frouxo, ✗ erro; `caro` = EC1/EC2; `base` = baseline; `Choice` = variante B (confiança); `sinais` = Nouls ≥ 0,5 "
               "(abreviados; `?` = na faixa de dúvida); `pend` = pendência estruturada (e como o supervisor a resolveu).\n")
    abrev = {"asks_credentials": "cred", "asks_confirmation": "conf", "effect_confirmed": "prov", "effect_duplicated": "dup",
             "can_verify_here": "verif", "needs_human_action": "hum", "session_expired_reentry": "sess", "informative_modal": "modal",
             "export_failed": "exp", "blank_or_broken": "branco", "unexpected_page": "inesp", "still_processing": "proc",
             "inconsistent_observation": "incons", "instructs_click": "manda"}
    linhas = []
    for s, c in zip(saidas, casos):
        a, r = s["acao"], s["rotina"]
        ok = "✓" if (a, r) == (c["acao"], c["rotina"]) else ("~" if a in c["aceitaveis"] else "✗")
        sin = " ".join(f"{abrev[q]}{'?' if s['sinais'][q] is None else ''}" for q in P.NOULS if s["nouls"][q] is not None and s["nouls"][q] >= 0.3) if s["origem"] == "jev" else "—"
        base = S.baseline_seguro(c, {"alvo": s["fatos"]["pendente"]} if s["fatos"] else None)
        linhas.append({"id": c["id"], "fam": familia(c), "gab": c["acao"] + (f" ({c['rotina']})" if c["rotina"] else "") + (" +" if len(c["aceitaveis"]) > 1 else ""),
                       "Jev": a + (f" ({r})" if r else ""), "ok": ok, "caro": " ".join(erros_caros(a, c)),
                       "base": base["acao"] + (f" ({base['rotina']})" if base["rotina"] else ""),
                       "Choice": f"{s['choice']['choice']} ({s['choice']['confidence']:.2f})" if s["choice"] else "—",
                       "pend": ("sim" + (f" → {s['pendencia_resolvida']}" if s["pendencia_resolvida"] else "")) if s["fatos"] and s["fatos"]["pendente"] else "",
                       "sinais": sin, "motivo": s["motivo"]})
    out.append(M.tabela(linhas) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "### Ação por variante e conjunto\n"]
    out.append(M.tabela([{"conjunto": n, "variante": v, **r["variantes"][v]} for n, r in resumos.items() for v in VARIANTES],
                        ["conjunto", *COLUNAS_ACAO]) + "\n")
    out.append("### Custo\n")
    out.append(M.tabela([{"conjunto": n, "n": r["n"], "difíceis": r["dificeis"], "p50_ms": r["custo"]["latencia_p50_ms"],
                          "p95_ms": r["custo"]["latencia_p95_ms"], "tokens_por_estado": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000": f"{1000 * r['custo']['custo_us'] / max(r['custo']['requisicoes'], 1):.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"])} for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}; cega ou não, conforme a rodada declarada no README): {h}"


def _congelar() -> dict:
    if "limites" not in P.CRITERIO_DE_ACEITE:
        sys.exit("congelamento recusado: fixe `perguntas.CRITERIO_DE_ACEITE` (com `limites`) antes de congelar")
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_DE_ACEITE)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    return "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_DE_ACEITE.items() if k != "limites")


def _ler(nome: str) -> dict:
    return json.loads((AQUI / "dados" / f"{nome}.json").read_text(encoding="utf-8"))


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if "teste" in conjuntos:
        try:
            manifesto = CG.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != P.CRITERIO_DE_ACEITE:
            sys.exit("teste recusado: o critério de aceite mudou desde o congelamento (rode `run.py congelar`)")
        linha = _linha_manifesto(manifesto)
    elif congelar:
        linha = _linha_manifesto(_congelar())
    else:
        h = CG.hashes(AQUI, [a for a in CONGELADOS if not a.startswith("dados/teste")])
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())
    if args == ["rascunho"]:
        texto, _ = secao_conjunto("rascunho", _ler("rascunho"))
        (AQUI / "resultados-rascunho.md").write_text(f"# Rascunho — supervisor-de-automacao (encanamento)\n\n{texto}", encoding="utf-8", newline="\n")
        print("resultados-rascunho.md gerado")
        return
    partes, resumos = [], {}
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, _ler(nome))
        partes.append(texto)
    cabecalho = (f"# Resultados — supervisor-de-automacao\n\nGerado por `run.py` em {datetime.date.today().isoformat()} "
                 f"(modo `{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, faixas, política e critério: "
                 f"`perguntas.py`; validação, fatos do código, precedência e baseline: `supervisor.py`. Preço: US$ 0,042 por milhão de "
                 f"tokens de entrada. Toda saída leva `autoriza: False`: a máquina de estados do robô executa com a própria permissão; "
                 f"nada é executado daqui.\n\nCritério de aceite (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")
    texto = cabecalho + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    for n, r in resumos.items():
        b = r["variantes"][PRINCIPAL]["_bruto"]
        print(f"  {n}: estrito {b['estrito']:.3f} · frouxo {b['frouxo']:.3f} ({b['certos_frouxos']}/{b['n']}) · EC1 {b['ec1']}/{b['pend']} · "
              f"EC2 {b['ec2']}/{b['p1']} · rotina {b['rotina_certa']}/{b['rec']} · ajuda indevida {b['ajuda_indevida']} · "
              f"baseline {r['variantes'][BASELINE]['_bruto']['frouxo']:.3f} · Choice {r['variantes'][CHOICE]['_bruto']['frouxo']:.3f} · "
              f"novas {r['custo']['requisicoes'] - r['custo']['do_cache']}")
    falhas = {n: r["custo"]["falhas_operacionais"] for n, r in resumos.items() if r["custo"]["falhas_operacionais"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — esses estados saíram `pedir_ajuda` sem resposta do Jev; o relatório marca o "
              "conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists():
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
