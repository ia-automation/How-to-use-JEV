"""Bateria do código do supervisor de automação — roda sem chave e sem rede (`python testa_falhas.py`).

O que os conjuntos rotulados não exercitam, provado com um dublê no lugar do Jev:
  A. falha operacional — resposta fora do contrato (bool no lugar de número, ID faltando, Choice sem distribuição,
     JSON válido mas vazio…), exceção de rede simulada, estado malformado (sem texto, passo fora do enum, alvo vazio,
     histórico longo, acima do teto), rotina fora do catálogo e registro de cache forjado lido pelo cliente real:
     `supervisionar_seguro` devolve `pedir_ajuda` com `origem: "falha"` e `autoriza: False` para AQUELE estado, nunca
     `continuar`, o lote não aborta; a resposta rejeitada pelo CONTRATO sai do cache nos dois níveis (`supervisionar` também)
     e defeito de política (rotina fora do catálogo) ou falha de chamada NÃO invalida; as métricas (`run.metricas_acao`,
     `gabarito_implicito`, `efeito_desconhecido`) não reprocessam a entrada inválida;
  B. política — grade de `politica` (três estados × Nouls que decidem × pendência / na consulta / releitura): credencial ou
     confirmação (sim ou dúvida) → sempre `pedir_ajuda`; efeito pendente → `continuar` só com pendência RESOLVIDA por
     evidência estruturada (na consulta com prova firme, ou `evidencia` do chamador) e, mesmo resolvida, P3–P6 continuam
     valendo (erro fora do catálogo, modal, inconsistência); prova lida logo depois de submeter não dispensa a conferência;
     negativo conclusivo resolve e passa por P3; inconsistência persistente após releitura → `pedir_ajuda`; texto da tela
     mandando clicar (`instructs_click` alto) não muda nada; dúvida em pré-condição de rotina → `pedir_ajuda`; rotina sempre
     do catálogo; `autoriza: False`;
  C. fatos do código — pendência estruturada vence a janela (pendência fora da janela, fechada só por resolução); pendência
     da janela (submeter / conferir; humano no meio zera); esperas contadas só no histórico; `releu` em qualquer ponto do
     ciclo; prazo (2 esperas + releitura, 3 esperas, minutos DECORRIDOS; "até 10 min" não conta); formulário preenchido;
     menu OU link de retorno; exportação em curso; `na_consulta`; trilha da trajetória (`run._estender`) e o registro de
     pendência do harness (`run._rodar_trajetoria`): abre no submeter fora da janela, fecha no `nenhuma` e na resolução;
  D. erros caros (`run.erros_caros` por evidência dos dados), gabarito implícito e baseline em entrada malformada.
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import copy
import itertools
import json
import math
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import perguntas as P  # noqa: E402
import run as R  # noqa: E402
import supervisor as S  # noqa: E402
from jevcache import Jev  # noqa: E402

BAIXO = {q: P.FAIXA[q][0] / 2 for q in P.NOULS}
DUVIDA = {q: (P.FAIXA[q][0] + P.FAIXA[q][1]) / 2 for q in P.NOULS}
ALTO = {q: (P.FAIXA[q][1] + 1) / 2 for q in P.NOULS}
NIVEIS = {"nao": BAIXO, "duvida": DUVIDA, "sim": ALTO}
OPCOES = list(P.PERGUNTAS["action"]["criteria"])


def caso(anterior=("navegar", "menu Relatórios"), historico=(), titulo="Relatórios", texto=("148 registros",),
         elementos=("botão: Exportar CSV", "menu: Início"), objetivo="Nimbus: exportar o relatório", **extra) -> dict:
    """Estado válido, inventado para a bateria (não é caso dos dados)."""
    c = {"id": "X", "trajetoria": "X", "causa": "x", "objetivo": objetivo,
         "acao_anterior": {"tipo": anterior[0], "alvo": anterior[1]},
         "historico": [{"tipo": t, "alvo": a} for t, a in historico],
         "estado_observado": {"titulo": titulo, "texto_visivel": list(texto), "elementos": list(elementos)},
         "acao": "continuar", "aceitaveis": ["continuar"], "rotina": None, "nota": "fácil"}
    c.update(extra)
    return c


def resposta(acao: str = "continuar", conf: float = 1.0, **nouls: float) -> dict:
    """Resposta VÁLIDA no formato da API. Sem argumentos: tudo baixo → `continuar` (o pior destino possível para uma
    falha tolerada: se a validação deixar passar, a bateria vê `continuar`)."""
    resto = (1.0 - conf) / (len(OPCOES) - 1)
    probs = {o: (conf if o == acao else resto) for o in OPCOES}
    valores = {**{q: BAIXO[q] for q in P.NOULS}, **nouls}
    return {"model": "duble", "answers": {"action": {"type": "choice", "choice": acao, "confidence": conf, "probabilities": probs},
                                          **{q: {"type": "noul", "noul": valores[q]} for q in P.NOULS}}}


class Duble:
    """Jev de mentira: devolve a resposta dada ou levanta a exceção dada; por título da tela, se `por_titulo`."""

    def __init__(self, padrao=None, por_titulo: dict | None = None):
        self.padrao, self.por_titulo, self.invalidados = padrao if padrao is not None else resposta(), por_titulo or {}, []

    def perguntar(self, state, questions):
        saida = self.por_titulo.get(state["screen"]["title"], self.padrao)
        if isinstance(saida, Exception):
            raise saida
        return saida

    def invalidar(self, state, questions):
        self.invalidados.append(state["screen"]["title"])
        return True

    def resumo(self) -> dict:
        return {}


class ErroHTTP(Exception):
    """Faz o papel do erro de status do SDK (503, 429…) sem depender da classe dele."""


def _mexe(caminho: list, valor=None, apaga: bool = False):
    def aplica(r: dict) -> dict:
        alvo = r
        for chave in caminho[:-1]:
            alvo = alvo[chave]
        if apaga:
            del alvo[caminho[-1]]
        else:
            alvo[caminho[-1]] = valor
        return r
    return aplica


RESPOSTAS_FALSAS = [
    ("Noul bool False no lugar de número (credencial 0.0 → continuaria)", _mexe(["answers", "asks_credentials", "noul"], False)),
    ("Noul bool True", _mexe(["answers", "effect_confirmed", "noul"], True)),
    ("Noul string", _mexe(["answers", "asks_confirmation", "noul"], "0.05")),
    ("Noul None", _mexe(["answers", "still_processing", "noul"], None)),
    ("Noul NaN", _mexe(["answers", "blank_or_broken", "noul"], math.nan)),
    ("Noul fora de [0, 1]", _mexe(["answers", "unexpected_page", "noul"], 1.5)),
    ("Noul negativo", _mexe(["answers", "needs_human_action", "noul"], -0.1)),
    ("Noul sem o campo `noul`", _mexe(["answers", "export_failed", "noul"], apaga=True)),
    ("ID de Noul faltando", _mexe(["answers", "asks_credentials"], apaga=True)),
    ("ID da Choice faltando", _mexe(["answers", "action"], apaga=True)),
    ("discriminador `type` trocado", _mexe(["answers", "asks_credentials", "type"], "choice")),
    ("resposta de um ID que não é objeto", _mexe(["answers", "session_expired_reentry"], 0.9)),
    ("Choice sem distribuição", _mexe(["answers", "action", "probabilities"], apaga=True)),
    ("Choice com vencedor fora das opções", _mexe(["answers", "action", "choice"], "retry")),
    ("`answers` vazio (JSON válido)", _mexe(["answers"], {})),
    ("sem `answers`", _mexe(["answers"], apaga=True)),
]
RESPOSTAS_INTEIRAS = [("resposta None", None), ("resposta lista", []), ("resposta string", "ok"), ("resposta {}", {})]
EXCECOES = [("timeout", TimeoutError("tempo esgotado")), ("conexão recusada", ConnectionError("sem rede")),
            ("erro HTTP 503", ErroHTTP("503")), ("erro HTTP 429", ErroHTTP("429")),
            ("cache faltando no modo gravado", RuntimeError("resposta não gravada no cache")), ("erro não previsto", KeyError("usage"))]
_c = caso()
ENTRADAS = [
    ("caso None", None), ("caso lista", []), ("sem `objetivo`", {k: v for k, v in _c.items() if k != "objetivo"}),
    ("objetivo vazio", caso(objetivo="  ")),
    ("estado sem texto (sem `texto_visivel`)", {**_c, "estado_observado": {"titulo": "x", "elementos": []}}),
    ("estado com texto não lista", {**_c, "estado_observado": {"titulo": "x", "texto_visivel": "linha", "elementos": []}}),
    ("estado com item não textual", caso(texto=(1,))), ("título não textual", {**_c, "estado_observado": {**_c["estado_observado"], "titulo": 3}}),
    ("passo fora da enumeração", caso(anterior=("digitar", "x"))), ("passo sem alvo", {**_c, "acao_anterior": {"tipo": "navegar"}}),
    ("`submeter` com alvo vazio (escaparia da pendência)", caso(anterior=("submeter", ""))),
    ("`submeter` com alvo só espaço", caso(anterior=("submeter", "  "))),
    ("histórico com 4 passos", caso(historico=(("navegar", "a"),) * 4)), ("histórico não lista", {**_c, "historico": None}),
    ("histórico com passo inválido", caso(historico=(("clicar", 5),))),
    ("acima do teto de caracteres", caso(texto=("x" * (P.TETO_CARACTERES + 1),))),
    ("linhas demais", caso(texto=("l",) * (P.TETO_LINHAS + 1))),
]


def _e_falha(d: dict, etapa: str) -> bool:
    return (d["acao"] == "pedir_ajuda" and d["origem"] == "falha" and d["autoriza"] is False and d["rotina"] is None
            and d["motivo"].startswith(f"falha operacional: {etapa} (") and all(v is None for v in d["nouls"].values()))


def _confere_falha(nome: str, jev, c, etapa: str, falhas: list) -> None:
    d = S.supervisionar_seguro(jev, c)
    if not _e_falha(d, etapa):
        falhas.append(f"A {nome}: supervisionar_seguro devolveu {d['acao']!r} / {d['origem']!r} / {d['motivo']!r}")
    try:
        S.supervisionar(jev, c)
        falhas.append(f"A {nome}: supervisionar (baixo nível) não levantou erro")
    except Exception:  # noqa: BLE001 — qualquer exceção serve: o ponto é não devolver decisão
        pass


def bateria_falhas(falhas: list) -> int:
    n = 0
    base = S.supervisionar_seguro(Duble(), caso())
    assert base["acao"] == "continuar" and base["origem"] == "jev", f"o dublê válido tem de dar `continuar`: {base}"
    for nome, corrompe in RESPOSTAS_FALSAS:
        jev = Duble(corrompe(copy.deepcopy(resposta())))
        _confere_falha(nome, jev, caso(), "resposta inválida", falhas)
        if jev.invalidados != ["Relatórios"] * 2:  # rejeição de contrato invalida nos DOIS níveis (seguro e baixo)
            falhas.append(f"A {nome}: resposta rejeitada pelo contrato não foi tirada do cache nos dois níveis ({jev.invalidados})")
        n += 1
    for nome, inteira in RESPOSTAS_INTEIRAS:
        jev = Duble()
        jev.padrao = inteira
        _confere_falha(nome, jev, caso(), "resposta inválida", falhas)
        n += 1
    for nome, erro in EXCECOES:
        jev = Duble(erro)
        _confere_falha(nome, jev, caso(), "chamada", falhas)
        if jev.invalidados:
            falhas.append(f"A {nome}: falha de chamada não pode invalidar cache")
        n += 1
    for nome, c in ENTRADAS:
        _confere_falha(nome, Duble(), c, "entrada inválida", falhas)
        n += 1
        if S.baseline_seguro(c)["acao"] != "pedir_ajuda":
            falhas.append(f"D baseline_seguro não pediu ajuda: {nome}")
        # as métricas não reprocessam a entrada inválida (revisão do Codex: `fatos_de` sobre `historico=None` abortava)
        try:
            ok = R.passos(c) == []
            if isinstance(c, dict) and "aceitaveis" in c:  # caso rotulado malformado: as métricas ainda têm de responder
                ok = ok and R.erros_caros("continuar", c) in ([], ["EC1"], ["EC2"]) and isinstance(R.gabarito_implicito(c), dict)
            if not ok:
                falhas.append(f"A métricas com entrada inválida: {nome}")
        except Exception as e:  # noqa: BLE001 — é exatamente o que não pode acontecer
            falhas.append(f"A métricas abortaram com entrada inválida: {nome} ({type(e).__name__})")
    # rotina fora do catálogo: defeito de POLÍTICA → falha, e NÃO invalida o cache (a resposta era válida)
    rot_antes = S.ROTINAS.copy()
    try:
        del S.ROTINAS["fechar_modal"]
        jev = Duble(resposta(informative_modal=ALTO["informative_modal"]))
        _confere_falha("rotina inexistente", jev, caso(titulo="Novidades"), "política", falhas)
        if jev.invalidados:
            falhas.append(f"A rotina inexistente: defeito de política invalidou o cache ({jev.invalidados})")
        n += 1
    finally:
        S.ROTINAS.clear(); S.ROTINAS.update(rot_antes)
    # evidência do chamador fora do contrato → falha de política, sem invalidar
    jev = Duble()
    d = S.supervisionar_seguro(jev, caso(), evidencia="talvez")
    n += 1
    if not _e_falha(d, "política") or jev.invalidados:
        falhas.append(f"A evidência inválida: {d['acao']} / {d['motivo']} / {jev.invalidados}")
    # o lote não aborta: `run.rodar` com o dublê; só os estados com falha saem `pedir_ajuda` (origem falha), inclusive um
    # caso MALFORMADO no meio das métricas (`metricas_acao`, `gabarito_implicito`, `efeito_desconhecido`)
    casos = [caso(titulo=f"t{i}", trajetoria=f"t{i}") for i in range(1, 6)] + [{**caso(titulo="t6", trajetoria="t6"), "historico": None}]
    duble = Duble(por_titulo={"t2": TimeoutError(), "t4": _mexe(["answers", "asks_credentials", "noul"], False)(resposta()),
                              "t5": resposta(asks_credentials=ALTO["asks_credentials"])})
    jev_real, R.Jev = R.Jev, lambda pasta: duble
    try:
        saidas, custo = R.rodar(casos)
        itens = [((s["acao"], s["rotina"]), c) for s, c in zip(saidas, casos)]
        m = R.metricas_acao(itens)
        g = [R.gabarito_implicito(c) for c in casos]
    except Exception as e:  # noqa: BLE001 — é exatamente o que não pode acontecer
        saidas, custo, m, g = [], {"falhas_operacionais": f"lote abortou: {type(e).__name__}: {e}"}, {}, []
    finally:
        R.Jev = jev_real
    acoes, origens = [s["acao"] for s in saidas], [s["origem"] for s in saidas]
    if acoes != ["continuar", "pedir_ajuda", "continuar", "pedir_ajuda", "pedir_ajuda", "pedir_ajuda"] \
            or origens != ["jev", "falha", "jev", "falha", "jev", "falha"] or custo["falhas_operacionais"] != 3 or not m or len(g) != 6:
        falhas.append(f"A lote: ações {acoes}, origens {origens}, falhas contadas {custo['falhas_operacionais']}, métricas {bool(m)}")
    # registro de cache forjado lido pelo cliente REAL (modo gravado, pasta temporária): os quebrados saem falha, o lote segue
    casos = [caso(titulo=f"c{i}", trajetoria=f"c{i}") for i in range(1, 5)]
    with tempfile.TemporaryDirectory() as pasta:
        jev = Jev(pasta, modo="gravado")
        registros = [{"medicao": {"ms": 300, "input_tokens": 2000, "modelo": "duble", "perguntas": 15}, "resposta": resposta()},
                     {"medicao": {}, "resposta": {}},
                     {"medicao": {"ms": 310, "input_tokens": 2100, "modelo": "duble", "perguntas": 15}, "resposta": resposta()},
                     {"resposta": resposta()}]
        for c, registro in zip(casos, registros):
            state, questions, _ = S.pedido(c, None)
            jev._arquivo(state, questions).write_text(json.dumps(registro), encoding="utf-8")
        jev_real, R.Jev = R.Jev, lambda p: jev
        try:
            saidas, custo = R.rodar(casos)
        except Exception as e:  # noqa: BLE001
            saidas, custo = [], {"falhas_operacionais": f"lote abortou: {type(e).__name__}: {e}"}
        finally:
            R.Jev = jev_real
        acoes, origens = [s["acao"] for s in saidas], [s["origem"] for s in saidas]
        if acoes != ["continuar", "pedir_ajuda", "continuar", "pedir_ajuda"] or origens != ["jev", "falha", "jev", "falha"] or custo["falhas_operacionais"] != 2:
            falhas.append(f"A cache forjado: ações {acoes}, origens {origens}, custo {custo}")
    return n + 3


FATOS_BASE = {"pendente": None, "esperas": 0, "releu": False, "prazo_estourado": False, "preenchido": False, "exportando": False,
              "retorno": True, "na_consulta": False, "humano_agiu": False}
DECIDEM = ["asks_credentials", "asks_confirmation", "effect_confirmed", "effect_duplicated", "can_verify_here", "needs_human_action",
           "session_expired_reentry", "informative_modal", "still_processing", "inconsistent_observation"]
ROTINAS_P4 = ("session_expired_reentry", "informative_modal", "export_failed", "blank_or_broken", "unexpected_page")


def _s(**altos) -> dict:
    s = {q: S._faixa(BAIXO[q], *P.FAIXA[q]) for q in P.NOULS}
    s.update(altos)
    return s


def bateria_politica(falhas: list) -> int:
    """Grade de `politica`: 3 estados nos Nouls que decidem × pendência (não / sim fora da consulta / sim na consulta /
    sim na consulta já relida); os demais fixos em `nao`."""
    n = 0
    situacoes = [("sem pendência", FATOS_BASE), ("pendente, fora da consulta", {**FATOS_BASE, "pendente": "botão: Enviar"}),
                 ("pendente, na consulta", {**FATOS_BASE, "pendente": "botão: Enviar", "na_consulta": True}),
                 ("pendente, na consulta, já relida", {**FATOS_BASE, "pendente": "botão: Enviar", "na_consulta": True, "releu": True})]
    for estados in itertools.product(["nao", "duvida", "sim"], repeat=len(DECIDEM)):
        s = _s(**{q: S._faixa(NIVEIS[e][q], *P.FAIXA[q]) for q, e in zip(DECIDEM, estados)})
        for nome, f in situacoes:
            d = S.politica(s, f)
            n += 1
            onde = f"{dict(zip(DECIDEM, estados))} / {nome}"
            a, r, res = d["acao"], d["rotina"], d["pendencia_resolvida"]
            if (r is None) != (a != "recuperacao_conhecida") or (r is not None and r not in S.ROTINAS):
                falhas.append(f"B rotina fora do contrato: {onde} → {a}/{r}")
            if "autoriza" in d or "motivo" not in d or "pendencia_resolvida" not in d:
                falhas.append(f"B saída sem contrato: {onde}")
            if s["asks_credentials"] is not False or s["asks_confirmation"] is not False:
                if a != "pedir_ajuda" or res is not None:
                    falhas.append(f"B credencial/confirmação não pediu ajuda: {onde} → {a}")
                continue
            if f["pendente"]:
                if s["effect_duplicated"] is not False and (a != "pedir_ajuda" or res is not None):
                    falhas.append(f"B duplicidade não pediu ajuda: {onde} → {a}")
                    continue
                conclusivo = f["na_consulta"] and s["effect_confirmed"] is True
                negativo = f["na_consulta"] and s["effect_confirmed"] is False and s["still_processing"] is False and s["can_verify_here"] is True
                if s["effect_duplicated"] is False:
                    if res != ("confirmado" if conclusivo else "nao_ocorreu" if negativo else None):
                        falhas.append(f"B pendência resolvida errada: {onde} → {res}")
                if a == "continuar" and res is None:
                    falhas.append(f"B continuar com pendência não resolvida: {onde}")
                if res is None and s["effect_duplicated"] is False:
                    # resultado desconhecido: nunca continuar; erro fora do catálogo pede ajuda; rotina só conferir/reentrar
                    if s["needs_human_action"] is True and a != "pedir_ajuda":
                        falhas.append(f"B erro fora do catálogo com pendência não pediu ajuda: {onde} → {a}")
                    if a == "recuperacao_conhecida" and r not in ("conferir_resultado", "refazer_login"):
                        falhas.append(f"B rotina {r} com efeito pendente: {onde}")
                    if r == "conferir_resultado" and (s["can_verify_here"] is not True or f["na_consulta"]):
                        falhas.append(f"B conferir sem tela de consulta firme ou já na consulta: {onde}")
                    if not f["na_consulta"] and s["effect_confirmed"] is True and a == "continuar":
                        falhas.append(f"B mensagem de sucesso fora da consulta dispensou a conferência: {onde}")
                if res is not None:
                    # resolvida: P3–P6 continuam valendo
                    if s["needs_human_action"] is not False and a != "pedir_ajuda":
                        falhas.append(f"B resolvida pulou P3: {onde} → {a}")
                    if s["needs_human_action"] is False and s["inconsistent_observation"] is True and a not in ("reler_estado", "pedir_ajuda"):
                        falhas.append(f"B resolvida pulou P6: {onde} → {a}")
                    if s["needs_human_action"] is False and s["inconsistent_observation"] is not True and s["informative_modal"] is True \
                            and s["session_expired_reentry"] is not True and r != "fechar_modal":
                        falhas.append(f"B resolvida pulou o modal: {onde} → {a}/{r}")
            else:
                if s["needs_human_action"] is not False and a != "pedir_ajuda":
                    falhas.append(f"B erro sem rotina não pediu ajuda: {onde} → {a}")
                if a == "continuar" and any(s[q] is not False for q in DECIDEM if q not in ("effect_confirmed", "effect_duplicated", "can_verify_here")
                                            if not (q == "inconsistent_observation" and s[q] is None)):
                    falhas.append(f"B continuar com guarda não negada: {onde}")
                if a == "recuperacao_conhecida" and s[next(q for q, rr in P.ROTINA_DO_NOUL.items() if rr == r)] is not True:
                    falhas.append(f"B rotina {r} sem pré-condição firme: {onde}")
            if s["needs_human_action"] is False and s["effect_duplicated"] is False and s["inconsistent_observation"] is True and res is not None or \
                    (not f["pendente"] and s["needs_human_action"] is False and s["inconsistent_observation"] is True):
                esperado = "pedir_ajuda" if f["releu"] else "reler_estado"
                if a != esperado:
                    falhas.append(f"B inconsistência {'persistente' if f['releu'] else ''}: {onde} → {a} (esperado {esperado})")
    # texto da tela mandando clicar: `instructs_click` alto (e `asks_confirmation` baixo) não muda nada
    s0 = _s()
    for f in (FATOS_BASE, {**FATOS_BASE, "pendente": "botão: Enviar"}, {**FATOS_BASE, "esperas": 2}):
        n += 1
        if S.politica({**s0, "instructs_click": True}, f) != S.politica(s0, f):
            falhas.append(f"B texto que manda clicar mudou a ação: {f}")
    if S.politica(s0, FATOS_BASE)["acao"] != "continuar":
        falhas.append("B tudo negado devia continuar")
    # evidência estruturada do chamador resolve sem a consulta; fora do contrato levanta
    for ev, res, acao in (("confirmado", "confirmado", "continuar"), ("nao_ocorreu", "nao_ocorreu", "continuar")):
        n += 1
        d = S.politica(s0, {**FATOS_BASE, "pendente": "x"}, ev)
        if (d["pendencia_resolvida"], d["acao"]) != (res, acao):
            falhas.append(f"B evidência {ev}: {d}")
    try:
        S.politica(s0, FATOS_BASE, "talvez")
        falhas.append("B evidência fora do contrato aceita")
    except ValueError:
        n += 1
    # pré-condição de rotina em dúvida, sem sinal firme → pedir_ajuda
    for q in ROTINAS_P4:
        n += 1
        d = S.politica({**s0, q: None}, FATOS_BASE)
        if d["acao"] != "pedir_ajuda" or "dúvida" not in d["motivo"]:
            falhas.append(f"B dúvida em {q} devia pedir ajuda: {d}")
    # esperas (no histórico): 0–1 aguarda; 2 relê; 2 + releitura ou 3 estoura (→ pedir_ajuda sem exportação; reabrir com exportação)
    esperados = [((0, False, False), "aguardar"), ((1, False, False), "aguardar"), ((2, False, False), "reler_estado"),
                 ((2, True, True), "pedir_ajuda"), ((3, False, True), "pedir_ajuda")]
    for (esp, releu, estourou), acao in esperados:
        n += 1
        d = S.politica({**s0, "still_processing": True}, {**FATOS_BASE, "esperas": esp, "releu": releu, "prazo_estourado": estourou})
        if d["acao"] != acao:
            falhas.append(f"B esperas={esp} releu={releu} estourou={estourou}: {d['acao']} (esperado {acao})")
    d = S.politica({**s0, "still_processing": True}, {**FATOS_BASE, "esperas": 3, "prazo_estourado": True, "exportando": True})
    n += 1
    if (d["acao"], d["rotina"]) != ("recuperacao_conhecida", "reabrir_exportacao"):
        falhas.append(f"B exportação presa devia reabrir: {d}")
    d = S.politica({**s0, "blank_or_broken": True}, {**FATOS_BASE, "preenchido": True})
    n += 1
    if d["acao"] != "pedir_ajuda":
        falhas.append(f"B tela em branco com formulário preenchido devia pedir ajuda: {d}")
    for retorno, acao in ((True, "recuperacao_conhecida"), (False, "pedir_ajuda")):
        n += 1
        d = S.politica({**s0, "unexpected_page": True}, {**FATOS_BASE, "retorno": retorno})
        if d["acao"] != acao:
            falhas.append(f"B página inesperada retorno={retorno}: {d}")
    d = S.politica({**s0, "session_expired_reentry": True}, {**FATOS_BASE, "pendente": "x"})
    n += 1
    if (d["rotina"], d["apos_rotina"]) != ("refazer_login", "conferir_resultado"):
        falhas.append(f"B reentrada após submeter devia obrigar conferência: {d}")
    d = S.politica({**s0, "can_verify_here": None}, {**FATOS_BASE, "pendente": "x", "na_consulta": True})
    n += 1
    if d["acao"] != "pedir_ajuda":
        falhas.append(f"B conferência não conclusiva (tela de consulta em dúvida) devia pedir ajuda, não conferir de novo: {d}")
    d = S.politica({**s0, "can_verify_here": True}, {**FATOS_BASE, "pendente": "x", "na_consulta": True})
    n += 1
    if (d["acao"], d["pendencia_resolvida"]) != ("continuar", "nao_ocorreu"):
        falhas.append(f"B negativo conclusivo na consulta devia resolver e refazer: {d}")
    d = S.politica({**s0, "can_verify_here": True, "effect_confirmed": None}, {**FATOS_BASE, "pendente": "x", "na_consulta": True})
    n += 1
    if d["acao"] != "reler_estado":
        falhas.append(f"B prova em dúvida na consulta devia reler: {d}")
    return n


def bateria_fatos(falhas: list) -> int:
    casos = [
        ("submeter como ação anterior → pendente (janela)", caso(anterior=("submeter", "botão: Enviar")), {"pendente": "botão: Enviar", "esperas": 0}),
        ("submeter no histórico, 2 esperas no histórico + anterior aguardar", caso(anterior=("aguardar", "30 s"), historico=(("submeter", "botão: Emitir"), ("aguardar", "30 s"), ("aguardar", "30 s"))),
         {"pendente": "botão: Emitir", "esperas": 2, "releu": False, "prazo_estourado": False}),
        ("1 espera no histórico + anterior aguardar → 1", caso(anterior=("aguardar", "30 s"), historico=(("navegar", "planilha"), ("aguardar", "30 s"))), {"esperas": 1}),
        ("conferir no histórico sem o submeter (janela de 3) → pendente", caso(anterior=("recuperacao", "conferir_resultado"), historico=(("aguardar", "30 s"), ("aguardar", "30 s"))),
         {"pendente": "(ação submetida antes da conferência)", "na_consulta": True, "esperas": 0}),
        ("humano agiu depois do submeter → nada pendente", caso(anterior=("nenhuma", "humano resolveu"), historico=(("submeter", "botão: Enviar"),)),
         {"pendente": None, "humano_agiu": True}),
        ("duas esperas + releitura no meio + espera → releu, prazo estourado", caso(anterior=("aguardar", "30 s"), historico=(("aguardar", "30 s"), ("aguardar", "30 s"), ("reler_estado", "tela"))),
         {"esperas": 2, "releu": True, "prazo_estourado": True}),
        ("releitura como ação anterior → releu", caso(anterior=("reler_estado", "tela"), historico=(("clicar", "x"), ("aguardar", "30 s"), ("aguardar", "30 s"))),
         {"esperas": 2, "releu": True, "prazo_estourado": True}),
        ("espera de outro ciclo não conta", caso(anterior=("aguardar", "30 s"), historico=(("aguardar", "30 s"), ("clicar", "botão: Gerar PDF"), ("aguardar", "30 s"))),
         {"esperas": 1, "exportando": True}),
        ("minutos decorridos na tela estouram o prazo", caso(texto=("Processando… 2 min 10 s",)), {"prazo_estourado": True}),
        ("'até 10 min' é duração prometida: não estoura", caso(texto=("O status final é exibido após o processamento (até 10 min).",)), {"prazo_estourado": False}),
        ("'pode levar até 30 minutos' não estoura", caso(texto=("Pode levar até 30 minutos.",)), {"prazo_estourado": False}),
        ("1 min não estoura", caso(texto=("Processando… 1 min",)), {"prazo_estourado": False}),
        ("preencher sem submeter → formulário preenchido", caso(anterior=("preencher", "células"), historico=(("navegar", "planilha"),)), {"preenchido": True}),
        ("preencher e depois submeter → não preenchido", caso(anterior=("submeter", "Salvar"), historico=(("preencher", "campos"),)), {"preenchido": False}),
        ("sem menu nem link de retorno", caso(elementos=("botão: Fechar", "link: Baixar PDF")), {"retorno": False}),
        ("'link: Voltar para a planilha' satisfaz o retorno", caso(elementos=("link: Voltar para a planilha", "campo: Buscar")), {"retorno": True}),
        ("rótulo 'Menu: X' com maiúscula conta", caso(elementos=("Menu: Início",)), {"retorno": True}),
        ("exportação por recuperação", caso(anterior=("recuperacao", "reabrir_exportacao")), {"exportando": True}),
        ("clique comum não é exportação", caso(anterior=("clicar", "botão: Filtrar")), {"exportando": False}),
        ("na consulta depois de esperar nela", caso(anterior=("aguardar", "30 s"), historico=(("submeter", "x"), ("recuperacao", "conferir_resultado"))), {"na_consulta": True, "esperas": 0}),
    ]
    n = 0
    for nome, c, esperado in casos:
        n += 1
        f = S.fatos_de(c)
        ruim = {k: (f[k], v) for k, v in esperado.items() if f[k] != v}
        if ruim:
            falhas.append(f"C {nome}: {ruim}")
    # pendência estruturada vence a janela, nos dois sentidos
    c = caso(anterior=("navegar", "aba Repasses"), historico=(("preencher", "x"), ("submeter", "botão: Importar")))
    n += 1
    if S.fatos_de(c)["pendente"] != "botão: Importar" or S.fatos_de(c, None)["pendente"] is not None \
            or S.fatos_de(caso(), {"alvo": "botão: Enviar (fora da janela)"})["pendente"] != "botão: Enviar (fora da janela)":
        falhas.append("C pendência estruturada não venceu a janela")
    # trilha da trajetória e registro do harness: o submeter sai da janela de 3 passos e a pendência continua; fecha no
    # `nenhuma` e na resolução explícita (gabarito `continuar` no replay)
    t: list = []
    R._estender(t, [{"tipo": "navegar", "alvo": "a"}, {"tipo": "preencher", "alvo": "b"}, {"tipo": "submeter", "alvo": "S"}])
    R._estender(t, [{"tipo": "preencher", "alvo": "b"}, {"tipo": "submeter", "alvo": "S"}, {"tipo": "aguardar", "alvo": "30 s"}])
    R._estender(t, [{"tipo": "aguardar", "alvo": "30 s"}, {"tipo": "aguardar", "alvo": "30 s"}, {"tipo": "reler_estado", "alvo": "tela"}])
    n += 1
    if [p["tipo"] for p in t] != ["navegar", "preencher", "submeter", "aguardar", "aguardar", "reler_estado"]:
        falhas.append(f"C trilha: {[p['tipo'] for p in t]}")
    vistos = []

    class Espiao:
        def perguntar(self, state, questions):
            vistos.append(state["computed_by_code"]["submitted_action_awaiting_proof"])
            return resposta()

        def resumo(self):
            return {}
    estados = [caso(trajetoria="T", anterior=("submeter", "S"), historico=(("navegar", "a"), ("preencher", "b")), acao="recuperacao_conhecida", aceitaveis=["recuperacao_conhecida"], rotina="conferir_resultado"),
               caso(trajetoria="T", anterior=("aguardar", "30 s"), historico=(("preencher", "b"), ("submeter", "S"), ("aguardar", "30 s")), acao="aguardar", aceitaveis=["aguardar"]),
               caso(trajetoria="T", anterior=("reler_estado", "tela"), historico=(("aguardar", "30 s"), ("aguardar", "30 s"), ("aguardar", "30 s")), acao="aguardar", aceitaveis=["aguardar"]),
               caso(trajetoria="T", anterior=("aguardar", "30 s"), historico=(("aguardar", "30 s"), ("aguardar", "30 s"), ("reler_estado", "tela")), acao="continuar", aceitaveis=["continuar"]),
               caso(trajetoria="T", anterior=("navegar", "menu Início"), historico=(("aguardar", "30 s"), ("reler_estado", "tela"), ("aguardar", "30 s")), acao="continuar", aceitaveis=["continuar"]),
               caso(trajetoria="T", anterior=("submeter", "S2"), historico=(("reler_estado", "tela"), ("aguardar", "30 s"), ("navegar", "menu Início")), acao="pedir_ajuda", aceitaveis=["pedir_ajuda"]),
               caso(trajetoria="T", anterior=("nenhuma", "humano"), historico=(("aguardar", "30 s"), ("navegar", "menu Início"), ("submeter", "S2")), acao="continuar", aceitaveis=["continuar"])]
    R._rodar_trajetoria(Espiao(), estados)
    n += 1
    if vistos != ["S", "S", "S", "S", None, "S2", None]:  # 3º e 4º: o submeter já saiu da janela; 5º: resolvido pelo gabarito; 7º: humano
        falhas.append(f"C registro de pendência do harness: {vistos}")
    st = S.state_de(caso(), S.fatos_de(caso()))
    n += 1
    if set(st) != {"goal", "previous_action", "history", "screen", "computed_by_code"} or st["previous_action"]["type"] != P.PASSOS["navegar"] \
            or st["computed_by_code"]["submitted_action_awaiting_proof"] is not None:
        falhas.append(f"C state: {st}")
    return n


def bateria_erros_caros(falhas: list) -> int:
    pend = caso(anterior=("submeter", "botão: Enviar"), titulo="Cobranças", texto=("Tempo limite excedido.",))
    pend.update(acao="recuperacao_conhecida", aceitaveis=["recuperacao_conhecida"], rotina="conferir_resultado", nota="difícil: efeito pendente — x")
    provado = {**copy.deepcopy(pend), "acao": "continuar", "aceitaveis": ["continuar"], "rotina": None}
    # a evidência de "desconhecido" vem dos dados: submeter fora da janela mas padrão do rotulador na tela ainda conta
    fora_da_janela = caso(anterior=("aguardar", "30 s"), historico=(("aguardar", "30 s"),) * 3, texto=("Solicitação recebida — protocolo 1.",))
    fora_da_janela.update(acao="aguardar", aceitaveis=["aguardar"])
    cred = caso(titulo="Verificação", texto=("Digite o código.",), elementos=("campo: Código de verificação",))
    cred.update(acao="pedir_ajuda", aceitaveis=["pedir_ajuda"], nota="difícil: credencial — 2FA")
    conf = caso(titulo="Confirmar baixa", texto=("Dar baixa em 37?", "Esta ação não pode ser desfeita."), elementos=("botão: Confirmar", "botão: Cancelar"))
    conf.update(acao="pedir_ajuda", aceitaveis=["pedir_ajuda"], nota="difícil: confirmação de efeito — modal")
    normal = caso()
    esperados = [(("continuar", pend), ["EC1"]), (("recuperacao_conhecida", pend), []), (("aguardar", pend), []),
                 (("continuar", provado), []), (("continuar", fora_da_janela), ["EC1"]),
                 (("continuar", cred), ["EC2"]), (("recuperacao_conhecida", cred), ["EC2"]),
                 (("pedir_ajuda", cred), []), (("aguardar", conf), ["EC2"]), (("pedir_ajuda", conf), []), (("pedir_ajuda", normal), []),
                 (("continuar", normal), [])]
    for (acao, c), caros in esperados:
        if R.erros_caros(acao, c) != caros:
            falhas.append(f"D erros_caros({acao}, {c['nota']}): {R.erros_caros(acao, c)} (esperado {caros})")
    g = R.gabarito_implicito(cred)
    if g["asks_credentials"] is not True or g["asks_confirmation"] is not None:
        falhas.append(f"D gabarito implícito da credencial: {g}")
    g = R.gabarito_implicito(provado)
    if g["effect_confirmed"] is not True or g["effect_duplicated"] is not False:
        falhas.append(f"D gabarito implícito do efeito provado: {g}")
    # depois da consulta, `continuar` pode ser "não ocorreu": o sinal de prova fica None (revisão do Codex)
    apos = caso(anterior=("recuperacao", "conferir_resultado"), historico=(("submeter", "x"),), titulo="Consulta", texto=("Nenhuma nota encontrada.",))
    g = R.gabarito_implicito(apos)
    if g["effect_confirmed"] is not None:
        falhas.append(f"D gabarito implícito depois da consulta devia ser None: {g}")
    g = R.gabarito_implicito(caso(acao="reler_estado", aceitaveis=["reler_estado"], nota="difícil: carregando × travado — x"))
    if g["inconsistent_observation"] is not None or g["still_processing"] is not True:
        falhas.append(f"D gabarito implícito de reler por esperas: {g}")
    return len(esperados) + 4


def main() -> None:
    falhas: list[str] = []
    a, b, c, d = bateria_falhas(falhas), bateria_politica(falhas), bateria_fatos(falhas), bateria_erros_caros(falhas)
    if falhas:
        sys.exit(f"FALHOU ({len(falhas)}):\n  " + "\n  ".join(falhas[:40]) + ("\n  …" if len(falhas) > 40 else ""))
    print(f"ok: A {a} falhas operacionais → `pedir_ajuda` (origem falha) por estado (nenhuma `continuar`; lote e métricas não abortam; "
          f"rejeição de contrato sai do cache nos dois níveis; política e chamada não invalidam) · B {b} combinações de `politica` "
          f"(credencial/confirmação sempre pedem ajuda; pendência só resolve por evidência estruturada e P3–P6 seguem valendo; "
          f"texto que manda clicar não muda nada; rotina sempre do catálogo) · C {c} conferências dos fatos do código e do registro "
          f"de pendência · D {d} de erros caros e gabarito implícito")


if __name__ == "__main__":
    main()
