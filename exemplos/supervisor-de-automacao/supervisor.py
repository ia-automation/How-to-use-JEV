"""Supervisor de automação: UMA requisição ao Jev por estado (14 Nouls + 1 Choice informativa); a ação é do código.

O Jev só julga sinais sobre a tela. O código decide a ação e a rotina pela precedência P1–P7 de dados/LEIA-ME.md e
NADA executa daqui:
  pedir_ajuda             credencial/2FA/captcha, confirmação de efeito, erro fora do catálogo, efeito duplicado, efeito
                          pendente sem como conferir, inconsistência que persiste depois de reler, dúvida em sinal que
                          decide, ou falha
  recuperacao_conhecida   + `rotina` do catálogo (pré-condição = Noul + fato do código); `apos_rotina` diz o passo obrigatório
  aguardar / reler_estado carregando dentro do prazo / captura contraditória ou duas esperas sem mudança
  continuar               o que sobra quando nenhuma guarda casou; com efeito pendente, só depois de a pendência estar
                          RESOLVIDA (ver abaixo) — e mesmo assim as guardas P3–P6 continuam valendo
Toda saída leva `autoriza: False` (lição 36): a máquina de estados do robô executa com a própria permissão.

Pendência de efeito (pós-revisão do Codex, 2026-10-02): o consumidor mantém a pendência ESTRUTURADA (`pendencia`),
fora da janela de 3 passos do histórico, e a encerra só por resolução explícita — a saída `pendencia_resolvida`
(`confirmado` / `nao_ocorreu`) ou um humano agindo (`nenhuma`). Sem o campo, o código deriva a pendência da janela
(uso avulso). A prova que dispensa a conferência é ESTRUTURADA: ou `evidencia` do chamador (resposta do sistema,
protocolo consultado por API), ou a tela de consulta que o próprio robô alcançou por `conferir_resultado`; uma mensagem
de sucesso lida na tela logo depois de submeter NÃO dispensa a conferência (texto é conteúdo; um banner pode imitá-la).
Resultado negativo conclusivo (na consulta, nada do efeito, nada processando, tela de consulta firme) também resolve a
pendência: refazer passa a ser seguro, mas P3–P6 ainda decidem antes de `continuar`.

Fatos do código (o Jev não conta nem lê o histórico com aritmética): esperas no histórico, releitura no ciclo, prazo
(tempo DECORRIDO na tela; "até 10 min" é duração prometida), formulário preenchido sem salvar, menu ou link de retorno,
"na tela de consulta", humano acabou de agir.

Ausência de resposta, ID faltando, tipo errado, número inválido, rotina fora do catálogo ou estado malformado é ERRO:
`decidir`/`supervisionar` levantam exceção; `supervisionar_seguro` (o que o consumidor chama) converte a falha em
`pedir_ajuda` com `origem: "falha"` para AQUELE estado — nunca `continuar`. Resposta JSON válida mas fora do CONTRATO
(bool, ID faltando, número fora de [0,1]) é tirada do cache (`jev.invalidar`) nos dois níveis, para ser refeita
sozinha na próxima rodada; defeito de política (rotina fora do catálogo) não invalida nada.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

ACOES = P.ACOES
OPCOES_ACAO = set(P.PERGUNTAS["action"]["criteria"])
# Catálogo de rotinas (dados/rotinas.json): a única fonte dos IDs válidos. Rotina fora daqui é erro, nunca sai.
ROTINAS = {r["id"]: r for r in json.loads((AQUI / "dados" / "rotinas.json").read_text(encoding="utf-8"))["rotinas"]}
_RE_MIN = re.compile(P.MINUTOS_NA_TELA)
_RE_PROMETIDA = re.compile(P.DURACAO_PROMETIDA)
_RE_EXPORT = re.compile(P.PASSO_DE_EXPORTACAO)
_RE_RETORNO = re.compile(P.LINK_DE_RETORNO)
_PASSO = {"tipo", "alvo"}
NAO_INFORMADA = object()  # sentinela: o chamador não mantém pendência estruturada → deriva da janela
EVIDENCIAS = {None, "confirmado", "nao_ocorreu"}
_ESPERA = ("aguardar", "reler_estado")


# ---------------------------------------------------------------------------------------- entrada
def validar_caso(caso) -> None:
    """Estado malformado = erro ANTES da chamada (vira falha operacional em `supervisionar_seguro`). As mensagens citam
    só o nome do campo, nunca o conteúdo. Passo com alvo vazio é malformado (um `submeter` sem alvo escaparia da pendência)."""
    if not isinstance(caso, dict):
        raise ValueError("caso não é objeto")
    if not isinstance(caso.get("objetivo"), str) or not caso["objetivo"].strip():
        raise ValueError("`objetivo` vazio ou não textual")
    if not isinstance(caso.get("historico"), list) or len(caso["historico"]) > 3:
        raise ValueError("`historico` não é lista de 0–3 passos")
    for p in [caso.get("acao_anterior"), *caso["historico"]]:
        if not isinstance(p, dict) or set(p) != _PASSO or p["tipo"] not in P.PASSOS or not isinstance(p["alvo"], str) or not p["alvo"].strip():
            raise ValueError("passo fora do formato {tipo, alvo}, tipo fora da enumeração ou alvo vazio")
    eo = caso.get("estado_observado")
    if not isinstance(eo, dict) or set(eo) != {"titulo", "texto_visivel", "elementos"} or not isinstance(eo["titulo"], str):
        raise ValueError("`estado_observado` sem {titulo, texto_visivel, elementos}")
    for campo in ("texto_visivel", "elementos"):
        if not isinstance(eo[campo], list) or any(not isinstance(l, str) for l in eo[campo]):
            raise ValueError(f"`estado_observado.{campo}` não é lista de texto")
    linhas = [eo["titulo"], *eo["texto_visivel"], *eo["elementos"]]
    if sum(len(l) for l in linhas) + len(caso["objetivo"]) > P.TETO_CARACTERES or len(linhas) > P.TETO_LINHAS:
        raise ValueError("estado fora da faixa validada (tamanho)")


# ---------------------------------------------------------------------------------------- fatos do código
def pendencia_da_janela(passos: list[dict]) -> str | None:
    """Uso avulso (sem pendência estruturada): alvo do último `submeter` depois do último passo humano (`nenhuma`); um
    `recuperacao: conferir_resultado` sem `submeter` à vista também marca pendência (a rotina só roda com efeito pendente).
    A janela de 3 passos pode esconder o `submeter`: por isso o consumidor deve passar `pendencia` (ver `fatos_de`)."""
    ult_humano = max((i for i, p in enumerate(passos) if p["tipo"] == "nenhuma"), default=-1)
    pendente = None
    for p in passos[ult_humano + 1:]:
        if p["tipo"] == "submeter":
            pendente = p["alvo"]
        elif p["tipo"] == "recuperacao" and p["alvo"] == "conferir_resultado" and pendente is None:
            pendente = "(ação submetida antes da conferência)"
    return pendente


def fatos_de(caso: dict, pendencia=NAO_INFORMADA) -> dict:
    """Tudo o que o código resolve antes da chamada, a partir do histórico (passos estruturados) e dos rótulos.
    - `pendente`: alvo do efeito submetido ainda sem prova. Vem do campo ESTRUTURADO `pendencia` ({"alvo"} ou None) que o
      consumidor mantém fora da janela; sem ele (`NAO_INFORMADA`), deriva da janela (`pendencia_da_janela`).
    - `esperas`: `aguardar` registrados no HISTÓRICO (a ação anterior não conta: LEIA-ME "0–1 esperas no histórico").
    - `releu`: houve `reler_estado` no ciclo de espera atual (os passos desde a última ação que não é espera/releitura).
    - `prazo_estourado`: 2 esperas + releitura, 3 esperas, ou a tela dizendo tempo DECORRIDO ≥ PRAZO_MINUTOS ("há 3 min",
      "processando… 2 min 10 s"); "até 10 min" / "pode levar 30 minutos" é duração prometida e não conta.
    - `na_consulta`: a última ação do ciclo foi `recuperacao: conferir_resultado` — o robô está na tela de consulta que
      ele mesmo alcançou (evidência estruturada para dispensar a conferência).
    - `retorno`: há menu (`menu:`) ou link de retorno (`link: Voltar…`, `link: Início`) — pré-condição de `voltar_ao_inicio`.
    @example fatos_de({... historico: [submeter, aguardar, aguardar], acao_anterior: aguardar ...})["esperas"] → 2
    """
    passos = [*caso["historico"], caso["acao_anterior"]]  # ordem cronológica
    anterior = caso["acao_anterior"]
    if pendencia is NAO_INFORMADA:
        pendente = pendencia_da_janela(passos)
    else:
        pendente = pendencia["alvo"] if isinstance(pendencia, dict) and pendencia.get("alvo") else None
    inicio = len(passos) - 1
    while inicio > 0 and passos[inicio]["tipo"] in _ESPERA:
        inicio -= 1
    ciclo = passos[inicio:]  # começa na última ação que não é espera/releitura (ou no 1º passo) e termina na ação anterior
    esperas = sum(p["tipo"] == "aguardar" for p in passos[inicio:len(caso["historico"])])  # só o histórico conta
    releu = any(p["tipo"] == "reler_estado" for p in ciclo)
    eo = caso["estado_observado"]
    decorridos = [int(m.group(1)) for l in [eo["titulo"], *eo["texto_visivel"]] if not _RE_PROMETIDA.search(l)
                  for m in _RE_MIN.finditer(l)]
    ult_humano = max((i for i, p in enumerate(passos) if p["tipo"] == "nenhuma"), default=-1)
    preenchido = False
    for p in passos[ult_humano + 1:]:
        if p["tipo"] == "preencher":
            preenchido = True
        elif p["tipo"] == "submeter":
            preenchido = False
    acao = ciclo[0] if ciclo[0]["tipo"] not in _ESPERA else None  # a ação que abriu o ciclo
    exportando = acao is not None and ((acao["tipo"] == "clicar" and bool(_RE_EXPORT.search(acao["alvo"])))
                                       or (acao["tipo"] == "recuperacao" and acao["alvo"] == "reabrir_exportacao"))
    rotulos = [(e.split(":", 1)[0].strip().lower(), e.split(":", 1)[1].strip() if ":" in e else "") for e in eo["elementos"]]
    return {"pendente": pendente, "esperas": esperas, "releu": releu,
            "prazo_estourado": esperas >= 3 or (esperas >= 2 and releu) or any(m >= P.PRAZO_MINUTOS for m in decorridos),
            "preenchido": preenchido, "exportando": exportando,
            "retorno": any(t == "menu" or (t == "link" and _RE_RETORNO.search(n)) for t, n in rotulos),
            "na_consulta": acao is not None and acao["tipo"] == "recuperacao" and acao["alvo"] == "conferir_resultado",
            "humano_agiu": anterior["tipo"] == "nenhuma"}


def _passo_en(p: dict) -> dict:
    return {"type": P.PASSOS[p["tipo"]], "target": p["alvo"]}


def state_de(caso: dict, fatos: dict) -> dict:
    """Caso (pt) → state enxuto com os nomes que as perguntas citam entre crases. Os tipos de passo vão traduzidos e
    explicados (o Jev não sabe que `submeter` tem efeito e `clicar` não); o conteúdo da tela vai como está (pt-BR).
    @example state_de(caso, fatos)["computed_by_code"]["waits_so_far"] → 0
    """
    eo = caso["estado_observado"]
    return {"goal": caso["objetivo"], "previous_action": _passo_en(caso["acao_anterior"]),
            "history": [_passo_en(p) for p in caso["historico"]],
            "screen": {"title": eo["titulo"], "visible_text": list(eo["texto_visivel"]), "elements": list(eo["elementos"])},
            "computed_by_code": {"submitted_action_awaiting_proof": fatos["pendente"], "waits_so_far": fatos["esperas"],
                                 "deadline_exceeded": fatos["prazo_estourado"], "form_filled_not_saved": fatos["preenchido"],
                                 "a_human_acted_just_before": fatos["humano_agiu"]}}


# ---------------------------------------------------------------------------------------- política
def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    """Noul em três faixas: True / False / None (= dúvida)."""
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def _esperar(f: dict, motivo: str) -> tuple[str, str | None, str]:
    """P5 dentro do prazo: 0–1 esperas → aguardar; 2 esperas sem releitura → reler_estado."""
    if f["esperas"] >= 2 and not f["releu"]:
        return "reler_estado", None, f"{motivo}: duas esperas sem mudança, capturar de novo"
    return "aguardar", None, f"{motivo} (espera {f['esperas'] + 1})"


def politica(s: dict, f: dict, evidencia: str | None = None) -> dict:
    """Sinais em três estados (True/False/None) + fatos do código + evidência estruturada do chamador → (ação, rotina,
    motivo, pendência resolvida). É a precedência P1–P7 do LEIA-ME, com a dúvida resolvida para o lado barato de cada
    sinal (ver `perguntas.FAIXA`). `continuar` só sai por uma via: nenhuma guarda casada e nenhuma pré-condição em dúvida —
    com efeito pendente, só depois de a pendência estar resolvida por evidência estruturada.
    @example politica({"asks_credentials": True, ...}, fatos)["acao"] → "pedir_ajuda"
    """
    if evidencia not in EVIDENCIAS:
        raise ValueError("`evidencia` fora de {None, 'confirmado', 'nao_ocorreu'}")
    d = lambda q: " (dúvida)" if s[q] is None else ""  # noqa: E731
    resolvida = None
    # P1 — credencial / confirmação: dúvida também pede ajuda (o erro caro é qualquer outra ação).
    if s["asks_credentials"] is not False:
        return _saida("pedir_ajuda", None, "tela de credencial, 2FA, captcha ou troca de senha" + d("asks_credentials"))
    if s["asks_confirmation"] is not False:
        return _saida("pedir_ajuda", None, "a tela pede confirmação de um efeito" + d("asks_confirmation"))
    # P2 — efeito submetido: resolve por evidência estruturada ou cai em "resultado desconhecido" (nunca continuar, nunca repetir).
    if f["pendente"]:
        if s["effect_duplicated"] is not False:
            return _saida("pedir_ajuda", None, "o efeito aparece mais de uma vez" + d("effect_duplicated"))
        if evidencia == "confirmado" or (f["na_consulta"] and s["effect_confirmed"] is True):
            resolvida = "confirmado"
        elif evidencia == "nao_ocorreu" or (f["na_consulta"] and s["effect_confirmed"] is False and s["still_processing"] is False
                                             and s["can_verify_here"] is True):
            resolvida = "nao_ocorreu"
        else:
            if s["needs_human_action"] is True:
                return _saida("pedir_ajuda", None, "erro que pede ação fora do catálogo, com efeito pendente")
            if s["session_expired_reentry"] is True:
                return _saida("recuperacao_conhecida", "refazer_login", "sessão expirou depois de submeter; reentrar e CONFERIR antes de seguir",
                              apos="conferir_resultado")
            if s["still_processing"] is not False and not f["prazo_estourado"]:
                return _saida(*_esperar(f, "efeito pendente ainda processando" + d("still_processing")))
            if f["na_consulta"]:
                if s["effect_confirmed"] is None and not f["releu"]:
                    return _saida("reler_estado", None, "dúvida: o efeito está provado na consulta? capturar de novo")
                return _saida("pedir_ajuda", None, "conferência não conclusiva; não repetir a submissão")
            if s["can_verify_here"] is True:
                return _saida("recuperacao_conhecida", "conferir_resultado",
                              "resultado desconhecido com tela de consulta alcançável" + ("; a mensagem de sucesso na tela não dispensa a conferência" if s["effect_confirmed"] is True else ""))
            return _saida("pedir_ajuda", None, "resultado desconhecido sem como conferir no prazo" + d("can_verify_here"))
    # P3 — erro que pede ação fora do catálogo.
    if s["needs_human_action"] is not False:
        return _saida("pedir_ajuda", None, "erro que pede ação fora do catálogo" + d("needs_human_action"), resolvida)
    # P6 antes de P5 — captura contraditória não é "carregando" (nunca age); se persiste depois de reler, humano.
    if s["inconsistent_observation"] is True:
        if not f["releu"]:
            return _saida("reler_estado", None, "observação inconsistente ou parcial", resolvida)
        return _saida("pedir_ajuda", None, "inconsistência persiste depois de reler", resolvida)
    # P4 — rotinas do catálogo com pré-condição firme (Noul) + parte do código.
    if s["session_expired_reentry"] is True:
        return _saida("recuperacao_conhecida", "refazer_login", "sessão expirada com reentrada sem digitar", resolvida)
    if s["informative_modal"] is True:
        return _saida("recuperacao_conhecida", "fechar_modal", "modal informativo bloqueante", resolvida)
    if s["export_failed"] is True:
        return _saida("recuperacao_conhecida", "reabrir_exportacao", "exportação expirada ou com erro (leitura)", resolvida)
    if s["blank_or_broken"] is True:
        if f["preenchido"]:
            return _saida("pedir_ajuda", None, "tela em branco com formulário preenchido: recarregar perderia o que foi digitado", resolvida)
        return _saida("recuperacao_conhecida", "recarregar_pagina", "tela em branco ou quebrada após navegação, nada pendente", resolvida)
    if s["unexpected_page"] is True:
        if f["retorno"]:
            return _saida("recuperacao_conhecida", "voltar_ao_inicio", "página inesperada com menu ou link de retorno acessível", resolvida)
        return _saida("pedir_ajuda", None, "página inesperada sem menu nem link de retorno", resolvida)
    # P5 — carregando (dúvida também espera: barato).
    if s["still_processing"] is not False:
        if not f["prazo_estourado"]:
            return _saida(*_esperar(f, "carregando" + d("still_processing")), resolvida)
        if f["exportando"]:
            return _saida("recuperacao_conhecida", "reabrir_exportacao", "exportação presa além do prazo: gerar de novo (leitura)", resolvida)
        return _saida("pedir_ajuda", None, "carregamento preso além do prazo, sem rotina para isso", resolvida)
    # P6 em dúvida NÃO relê: no ajuste (1ª passada) a faixa do meio deste Noul foi ruído (0,50–0,60 em modal, tela em
    # branco, página inesperada e numa planilha salva); só o sinal firme relê.
    # Pré-condição de rotina em dúvida, sem nenhum sinal firme: humano, nunca rotina nem `continuar` por dúvida.
    duvidas = [q for q in P.ROTINA_DO_NOUL if q != "can_verify_here" and s[q] is None]
    if duvidas:
        return _saida("pedir_ajuda", None, "dúvida em pré-condição de rotina: " + ", ".join(duvidas), resolvida)
    # P7 — tudo o mais: tela esperada, aviso não bloqueante, relatório vazio, texto que "manda" clicar.
    if resolvida == "nao_ocorreu":
        return _saida("continuar", None, "a consulta prova que o efeito NÃO ocorreu: refazer a submissão é seguro", resolvida)
    if resolvida == "confirmado":
        return _saida("continuar", None, "efeito provado uma vez (evidência estruturada); seguir sem repetir", resolvida)
    return _saida("continuar", None, "nenhuma guarda casou: tela esperada")


def _saida(acao: str, rotina: str | None, motivo: str, resolvida: str | None = None, apos: str | None = None) -> dict:
    return {"acao": acao, "rotina": rotina, "motivo": motivo, "apos_rotina": apos, "pendencia_resolvida": resolvida}


def validar(resposta: dict) -> dict:
    """Resposta da API → números validados pela infra comum: todo ID presente, discriminador `type` batendo, Noul número
    real em [0,1] (não bool, não string), Choice com vencedor entre as opções e distribuição completa. Falha = exceção.
    É a REJEIÇÃO DE CONTRATO: só ela invalida o cache (ver `supervisionar`)."""
    answers = resposta.get("answers") or {}
    for q, p in P.PERGUNTAS.items():
        a = answers.get(q)
        if not isinstance(a, dict) or a.get("type", p["type"]) != p["type"]:
            raise ValueError(f"resposta sem `{q}` do tipo {p['type']}")
    return {"choice": CG.choice(resposta, "action", OPCOES_ACAO), **{q: CG.noul(resposta, q) for q in P.NOULS}}


def decidir(validado: dict, fatos: dict, evidencia: str | None = None) -> dict:
    """Resposta já validada (`validar`) + fatos do código → decisão (guarda os números brutos para medir e re-limiar sem
    chamar de novo). A Choice `action` é guardada e NÃO entra na ação. Rotina fora do catálogo é erro de POLÍTICA (nunca
    sai; não invalida o cache)."""
    v = validado
    s = {q: _faixa(v[q], *P.FAIXA[q]) for q in P.NOULS}
    p = politica(s, fatos, evidencia)
    if p["rotina"] is not None and p["rotina"] not in ROTINAS:
        raise RuntimeError("política apontou rotina fora do catálogo")
    return {**p, "origem": "jev", "autoriza": False, "nouls": {q: v[q] for q in P.NOULS}, "sinais": s,
            "choice": v["choice"], "fatos": fatos}


def decisao_falha(tipo: str) -> dict:
    """Decisão para falha operacional: humano lê. O motivo leva só a etapa e a classe do erro — o texto da exceção pode
    citar o corpo da resposta ou da tela."""
    return {"acao": "pedir_ajuda", "rotina": None, "motivo": f"falha operacional: {tipo}", "apos_rotina": None,
            "pendencia_resolvida": None, "origem": "falha", "autoriza": False, "nouls": {q: None for q in P.NOULS},
            "sinais": {q: None for q in P.NOULS}, "choice": None, "fatos": None}


# ---------------------------------------------------------------------------------------- baseline de código
def _plano(texto: str) -> str:
    """Minúsculas, sem acento — as listas de expressões são escritas assim."""
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


def baseline(caso: dict, pendencia=NAO_INFORMADA) -> dict:
    """Só regras de código, sem Jev: palavra-chave no texto da tela + tipo da ação anterior + os MESMOS fatos do código.
    Mesma precedência. Nunca tem dúvida.
    @example baseline(caso_com_campo_senha)["acao"] → "pedir_ajuda"
    """
    f = fatos_de(caso, pendencia)
    eo = caso["estado_observado"]
    linhas = [_plano(l) for l in [eo["titulo"], *eo["texto_visivel"], *eo["elementos"]]]
    bate = lambda lista: any(re.search(p, l) for p in lista for l in linhas)  # noqa: E731
    sessao = bate(P.BASELINE_SESSAO) and bate(P.BASELINE_REENTRADA)
    carregando = bate(P.BASELINE_CARREGANDO)
    rec = lambda r, m: {"acao": "recuperacao_conhecida", "rotina": r, "motivo": m}  # noqa: E731
    if bate(P.BASELINE_CREDENCIAL) or (bate(P.BASELINE_SESSAO) and not sessao):
        return {"acao": "pedir_ajuda", "rotina": None, "motivo": "credencial"}
    if bate(P.BASELINE_CONFIRMACAO):
        return {"acao": "pedir_ajuda", "rotina": None, "motivo": "confirmação"}
    if f["pendente"]:
        if bate(P.BASELINE_PROVADO) and not bate(P.BASELINE_DESCONHECIDO):
            return {"acao": "continuar", "rotina": None, "motivo": "efeito provado (palavra)"}
        if sessao:
            return rec("refazer_login", "sessão expirada após submeter")
        if carregando and not f["prazo_estourado"]:
            return {"acao": "aguardar" if f["esperas"] < 2 or f["releu"] else "reler_estado", "rotina": None, "motivo": "processando"}
        if f["na_consulta"]:
            return {"acao": "pedir_ajuda", "rotina": None, "motivo": "conferência sem o efeito"}
        return rec("conferir_resultado", "efeito pendente")
    if bate(P.BASELINE_SEM_ROTINA):
        return {"acao": "pedir_ajuda", "rotina": None, "motivo": "erro sem rotina"}
    if sessao:
        return rec("refazer_login", "sessão expirada")
    if bate(P.BASELINE_MODAL):
        return rec("fechar_modal", "modal")
    if bate(P.BASELINE_EXPORTACAO):
        return rec("reabrir_exportacao", "exportação")
    if not eo["texto_visivel"] and not eo["elementos"]:
        return rec("recarregar_pagina", "tela em branco") if not f["preenchido"] else {"acao": "pedir_ajuda", "rotina": None, "motivo": "branco com formulário"}
    if bate(P.BASELINE_INESPERADA):
        return rec("voltar_ao_inicio", "página inesperada") if f["retorno"] else {"acao": "pedir_ajuda", "rotina": None, "motivo": "inesperada sem retorno"}
    if carregando:
        if f["prazo_estourado"]:
            return rec("reabrir_exportacao", "exportação presa") if f["exportando"] else {"acao": "pedir_ajuda", "rotina": None, "motivo": "preso"}
        return {"acao": "aguardar" if f["esperas"] < 2 or f["releu"] else "reler_estado", "rotina": None, "motivo": "carregando"}
    return {"acao": "continuar", "rotina": None, "motivo": "nada casou"}


def baseline_seguro(caso, pendencia=NAO_INFORMADA) -> dict:
    """O baseline pelo mesmo contrato de falha: estado malformado → pedir_ajuda."""
    try:
        validar_caso(caso)
        return baseline(caso, pendencia)
    except Exception:  # noqa: BLE001 — falha fechada
        return {"acao": "pedir_ajuda", "rotina": None, "motivo": "falha operacional: entrada inválida"}


# ---------------------------------------------------------------------------------------- chamada
def pedido(caso: dict, pendencia=NAO_INFORMADA) -> tuple[dict, dict, dict]:
    """(state, questions, fatos) de um estado — todas as perguntas na mesma requisição (mesmo state, isoladas)."""
    validar_caso(caso)
    fatos = fatos_de(caso, pendencia)
    return state_de(caso, fatos), P.PERGUNTAS, fatos


def _validar_ou_invalidar(jev, resposta: dict, state: dict, questions: dict) -> dict:
    """Rejeição de CONTRATO tira a resposta do cache (só ela é refeita na próxima rodada) e levanta. Nos dois níveis."""
    try:
        return validar(resposta)
    except Exception:
        if hasattr(jev, "invalidar"):
            try:
                jev.invalidar(state, questions)
            except Exception:  # noqa: BLE001 — zelo pelo cache não pode esconder a falha original
                pass
        raise


def supervisionar(jev, caso: dict, pendencia=NAO_INFORMADA, evidencia: str | None = None) -> dict:
    """Um estado de ponta a ponta: entrada validada, fatos calculados, uma requisição, decisão em código.
    Baixo nível: estado malformado, falha da chamada e resposta fora do contrato LEVANTAM exceção (a resposta fora do
    contrato é invalidada no cache antes)."""
    state, questions, fatos = pedido(caso, pendencia)
    resposta = jev.perguntar(state, questions)
    return decidir(_validar_ou_invalidar(jev, resposta, state, questions), fatos, evidencia)


def supervisionar_seguro(jev, caso, pendencia=NAO_INFORMADA, evidencia: str | None = None) -> dict:
    """O que o consumidor (a máquina de estados do robô) chama: os mesmos passos, mas NENHUMA falha sobe nem aborta o
    lote — timeout, erro HTTP, cache faltando, resposta fora do contrato, rotina fora do catálogo ou estado malformado
    viram `pedir_ajuda` com `origem: "falha"` para AQUELE estado. Só a rejeição de contrato invalida o cache; defeito
    de política não. Pega `Exception` inteira de propósito: erro não previsto também tem de parar o robô, nunca `continuar`.
    @example supervisionar_seguro(jev_fora_do_ar, caso)
             → {"acao": "pedir_ajuda", "origem": "falha", "motivo": "falha operacional: chamada (TimeoutError)", …}
    """
    etapa = "entrada inválida"
    try:
        state, questions, fatos = pedido(caso, pendencia)
        etapa = "chamada"
        resposta = jev.perguntar(state, questions)
        etapa = "resposta inválida"
        validado = _validar_ou_invalidar(jev, resposta, state, questions)
        etapa = "política"
        return decidir(validado, fatos, evidencia)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        return decisao_falha(f"{etapa} ({type(e).__name__})")
