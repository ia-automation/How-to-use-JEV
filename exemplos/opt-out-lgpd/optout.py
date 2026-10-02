"""Opt-out e LGPD: UMA requisição ao Jev por mensagem (Nouls atômicos + Choice do tipo); a ação é do código.

O Jev só julga: a mensagem pede para parar o contato? pede pausa com retomada? exerce direito de titular? qual?
O código decide a ação e NADA executa daqui (bloquear envio, abrir pedido e pausar são efeitos do processo que
chama, com sua própria permissão):
  bloquear_envios          opt-out definitivo
  abrir_pedido_lgpd(tipo)  direito de titular; `bloqueia` diz se o envio também para (exclusão ⇒ opt-out);
                           `bloqueia=None` = bloqueio PENDENTE (quem atende confirma), não é "não bloqueia"
  pausar                   pausa temporária
  seguir                   nada disso — a conversa continua
  revisar                  dúvida, sinais em conflito, falha operacional ou mensagem fora da faixa validada →
                           humano; com `bloqueia=True` o envio fica SUSPENSO até a confirmação
Política assimétrica: perder um opt-out ou um pedido LGPD é infração; por isso DÚVIDA nunca vira `seguir`, e um
Noul de GUARDA nunca é a razão única para não cumprir uma obrigação (só move para `revisar`).
Ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO: `decidir`/`julgar` levantam exceção;
`guardar_seguro` (o que o consumidor chama) converte a falha em `revisar` para AQUELA mensagem. Nunca `seguir`.

Candidato a guarda de entrada da Luci/0010: roda em cada mensagem recebida, antes do agente responder.
Isto NÃO é parecer jurídico: as regras são as do dados/LEIA-ME.md, escritas para este exemplo.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

ACOES = ["bloquear_envios", "abrir_pedido_lgpd", "pausar", "seguir", "revisar"]
TIPOS = ["exclusao", "origem_dos_dados", "acesso", "correcao"]  # ordem = precedência do LEIA-ME


def state_de(mensagem: str) -> dict:
    """Mensagem (pt) → state enxuto com o nome que as perguntas citam entre crases. Texto vazio = erro antes da chamada.
    @example state_de("para de me mandar mensagem") → {"message": "para de me mandar mensagem"}
    """
    if not isinstance(mensagem, str) or not mensagem.strip():
        raise ValueError("mensagem vazia ou não textual")
    return {"message": mensagem}


def mensagem_longa(state: dict) -> str | None:
    """Motivo se a mensagem passa do teto; None dentro da faixa validada."""
    n = len(state["message"])
    return f"mensagem longa ({n} caracteres; teto {P.TETO_CARACTERES})" if n > P.TETO_CARACTERES else None


def _sem_numeros(motivo: str, marca: str) -> dict:
    """`revisar` sem números do Jev; `marca` (`longa` / `falha`) é o que o relatório conta à parte."""
    return {"acao": "revisar", "tipo_lgpd": None, "bloqueia": None, "motivo": motivo, marca: True,
            "nouls": {q: None for q in P.NOULS}, "sinais": {q: None for q in P.NOULS},
            "tipo_escolha": None, "tipo_conf": None, "tipo_probs": {}}


def decisao_longa(motivo: str) -> dict:
    """Decisão sem chamada ao Jev para mensagem acima do teto: humano lê (contada à parte, `longa`)."""
    return _sem_numeros(motivo, "longa")


def decisao_falha(tipo: str) -> dict:
    """Decisão para falha operacional (entrada, chamada ou contrato da resposta): humano lê (contada à parte,
    `falha`). O motivo leva só a etapa e a classe do erro — o texto da exceção pode citar o corpo da resposta."""
    return _sem_numeros(f"falha operacional: {tipo}", "falha")


def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    """Noul em três faixas: True / False / None (= dúvida)."""
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def validar(resposta: dict) -> dict:
    """Resposta da API → números validados pela infra comum: todo ID esperado presente, discriminador `type` batendo,
    Noul número real em [0,1] (não bool, não string), Choice com vencedor entre as opções, distribuição completa
    somando ~1 e confiança em [0,1]. Qualquer falha = erro operacional (exceção), nunca `seguir`."""
    answers = resposta.get("answers") or {}
    for q, p in P.PERGUNTAS.items():
        a = answers.get(q)
        if not isinstance(a, dict) or a.get("type", p["type"]) != p["type"]:
            raise ValueError(f"resposta sem `{q}` do tipo {p['type']}: {a!r}")
    tipo = CG.choice(resposta, "lgpd_type", set(P.TIPO_DA_OPCAO))
    return {"tipo_escolha": tipo["choice"], "tipo_conf": tipo["confidence"], "tipo_probs": tipo["probabilities"],
            **{q: CG.noul(resposta, q) for q in P.NOULS}}


def decidir(resposta: dict) -> dict:
    """Resposta JSON da API → decisão (guarda os números brutos para medir e re-limiar sem chamar de novo).

    Ordem (precedência por obrigação): pedido LGPD > opt-out > pausa > seguir; dúvida em qualquer degrau que
    poderia esconder uma obrigação → `revisar`.
    """
    v = validar(resposta)
    s = {q: _faixa(v[q], *P.FAIXA[q]) for q in P.NOULS}
    tipo = P.TIPO_DA_OPCAO[v["tipo_escolha"]]
    opt, pausa, lgpd = s["opt_out"], s["temporary_pause"], s["lgpd_request"]
    continua, sem_objeto, terceiro = s["wants_contact_to_continue"], s["stop_without_object"], s["about_another_contact"]

    acao, tipo_lgpd, bloqueia, motivo = "seguir", None, False, "nenhum pedido de parar, pausar ou de titular"
    if lgpd is True:
        if tipo is None or v["tipo_conf"] < P.TIPO_CONF_MIN:
            acao, bloqueia = "revisar", None
            motivo = f"pedido de titular sem tipo claro ({v['tipo_escolha']}, confiança {v['tipo_conf']:.2f})"
        else:
            acao, tipo_lgpd, motivo = "abrir_pedido_lgpd", tipo, f"direito de titular: {tipo}"
            if tipo == "exclusao":
                # Regra de CÓDIGO do LEIA-ME: exclusão implica opt-out (sem cadastro não há contato). A exceção
                # (exclusão parcial: a pessoa pede para continuar recebendo) só é lida por um Noul de GUARDA, e
                # guarda nunca é a razão única para não cumprir a obrigação (revisão do Codex, 2026-10-01: com
                # `opt_out` em dúvida e o guarda alto, o envio saía liberado). Sem opt-out explícito, o sinal de
                # continuar não libera nada: manda confirmar, com o envio SUSPENSO e o tipo reconhecido junto.
                bloqueia = True
                if continua is True and opt is not True:
                    acao, motivo = "revisar", "exclusão com sinal de continuar: confirmar"
            else:
                # Acesso/origem/correção não implicam opt-out. None = bloqueio PENDENTE: quem atende o pedido
                # confirma; o relatório conta como obrigação não cumprida inteira e fora da cobertura automática.
                bloqueia = opt
    elif lgpd is None:
        acao, bloqueia, motivo = "revisar", None, f"dúvida se há pedido de titular ({v['lgpd_request']:.2f})"
    elif opt is True:
        # Vetos do bloqueio: segunda leitura do lado caro "cliente interessado bloqueado". Só movem para
        # `revisar`, nunca para `seguir`.
        conflito = [n for n, x in (("diz que podem continuar", continua), ("pedido sobre outro número", terceiro),
                                   ("pausa com retomada", pausa), ("não diz o que parar", sem_objeto)) if x is True]
        if conflito:
            acao, bloqueia, motivo = "revisar", None, "opt-out em conflito: " + ", ".join(conflito)
        else:
            acao, bloqueia, motivo = "bloquear_envios", True, "opt-out definitivo"
    elif opt is None:
        acao, bloqueia, motivo = "revisar", None, f"dúvida de opt-out ({v['opt_out']:.2f})"
    elif sem_objeto is True:
        acao, bloqueia, motivo = "revisar", None, "'para' / 'não quero mais' sem dizer o quê"
    elif pausa is True:
        acao, motivo = "pausar", "pausa com retomada"
    elif pausa is None:
        acao, bloqueia, motivo = "revisar", None, f"dúvida de pausa ({v['temporary_pause']:.2f})"
    return {"acao": acao, "tipo_lgpd": tipo_lgpd, "bloqueia": bloqueia, "motivo": motivo,
            "nouls": {q: v[q] for q in P.NOULS}, "sinais": s,
            "tipo_escolha": v["tipo_escolha"], "tipo_conf": v["tipo_conf"], "tipo_probs": v["tipo_probs"]}


# ---------------------------------------------------------------------------------------- baseline de código
def _plano(texto: str) -> str:
    """Minúsculas, sem acento — a lista de expressões é escrita assim."""
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


def baseline(mensagem: str) -> dict:
    """Só lista de expressões, sem Jev. Precedência LGPD (exclusão > origem > acesso > correção) > opt-out > pausa >
    seguir. Nunca diz `revisar`: regex não sabe que não sabe.
    @example baseline("quem te passou meu número?")
             → {"acao": "abrir_pedido_lgpd", "tipo_lgpd": "origem_dos_dados", "bloqueia": False}
    """
    t = _plano(mensagem)
    bate = lambda lista: any(re.search(p, t) for p in lista)  # noqa: E731
    opt = bate(P.BASELINE_OPT_OUT)
    for tipo in TIPOS:
        if bate(P.BASELINE_LGPD[tipo]):
            return {"acao": "abrir_pedido_lgpd", "tipo_lgpd": tipo, "bloqueia": opt or tipo == "exclusao"}
    if opt:
        return {"acao": "bloquear_envios", "tipo_lgpd": None, "bloqueia": True}
    if bate(P.BASELINE_PAUSA):
        return {"acao": "pausar", "tipo_lgpd": None, "bloqueia": False}
    return {"acao": "seguir", "tipo_lgpd": None, "bloqueia": False}


def pedido(mensagem: str) -> tuple[dict, dict]:
    """(state, questions) de uma mensagem — todas as perguntas na mesma requisição (mesmo state, isoladas)."""
    return state_de(mensagem), P.PERGUNTAS


def julgar(jev, mensagem: str) -> dict:
    """Uma mensagem de ponta a ponta: texto validado, teto conferido, uma requisição, decisão em código.
    Baixo nível: mensagem vazia, falha da chamada e resposta fora do contrato LEVANTAM exceção."""
    state, questions = pedido(mensagem)
    motivo = mensagem_longa(state)
    if motivo:
        return decisao_longa(motivo)
    return decidir(jev.perguntar(state, questions))


def guardar_seguro(jev, mensagem: str) -> dict:
    """O que o consumidor (guarda de entrada, lote) chama: os mesmos passos de `julgar`, mas NENHUMA falha sobe
    nem aborta o lote — timeout, erro HTTP, cache faltando, resposta fora do contrato ou mensagem vazia viram
    `revisar` para AQUELA mensagem, com a etapa e a classe do erro no motivo (revisão do Codex, 2026-10-01).
    Pega `Exception` inteira de propósito: num guarda, erro não previsto também tem de fechar em `revisar`.
    @example guardar_seguro(jev_fora_do_ar, "para de me mandar mensagem")
             → {"acao": "revisar", "bloqueia": None, "motivo": "falha operacional: chamada (TimeoutError)", "falha": True, …}
    """
    etapa, pedido_feito = "entrada inválida", None
    try:
        state, questions = pedido(mensagem)
        motivo = mensagem_longa(state)
        if motivo:
            return decisao_longa(motivo)
        etapa, pedido_feito = "chamada", (state, questions)
        resposta = jev.perguntar(state, questions)
        etapa = "resposta inválida"
        return decidir(resposta)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        if etapa == "resposta inválida" and pedido_feito and hasattr(jev, "invalidar"):
            # Resposta JSON válida que a validação rejeita sai do cache (revisão do Codex no comparador, 2026-10-01,
            # família): senão `auto` a reproduziria em toda rodada e a mensagem ficaria presa em `revisar` para sempre.
            try:
                jev.invalidar(*pedido_feito)
            except Exception:  # noqa: BLE001 — melhor esforço; a decisão segura já está tomada
                pass
        return decisao_falha(f"{etapa} ({type(e).__name__})")
