"""Roteador de e-mail: UMA requisição ao Jev por e-mail; o código decide se o Jev fica com a decisão ou escala.

Saída por e-mail — e NADA é executado daqui (mover de pasta, marcar, responder é do serviço que chama):
  decide   o Jev classificou com confiança ≥ limiar da classe e nenhum Noul atômico contradiz → vale a `classe`
  escala   confiança abaixo do limiar, Noul em conflito, corpo acima do teto, corpo vazio, corpo truncado na
           extração com classe cara, falha operacional → o e-mail segue para o LLM que já classifica hoje
           (Claude → Codex → API)
Divisão: os `sinais` (DKIM, SPF, lista, anexos, links) são do CÓDIGO — vêm calculados dos cabeçalhos e entram no
state como fato pronto; o Jev lê nome exibido, assunto e corpo; a política (limiar por classe, conflitos) é
código, com os números em `perguntas.py`.
Ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO: `decidir`/`rotear` levantam exceção;
`rotear_seguro` (o que o consumidor chama) converte a falha em `escala` para AQUELE e-mail. Falha nunca decide.

Candidato a degrau entre a regra e o LLM no serviço 0802 (classificador de e-mail).
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

ACOES = ["decide", "escala"]
_TEXTO = ("remetente_nome", "assunto", "texto")
_BOOLEANOS = ("dkim_aligned", "spf_pass", "dmarc_pass", "reply_to_differs", "list_unsubscribe", "bulk_precedence",
              "auto_submitted", "body_truncated")


# ---------------------------------------------------------------------------------------- entrada e state
def validar_registro(r: dict) -> None:
    """Campos e tipos do e-mail ANTES de qualquer chamada; erro = falha de entrada (→ `escala`)."""
    if not isinstance(r, dict):
        raise ValueError("registro não é objeto")
    for campo in _TEXTO:
        if r.get(campo) is not None and not isinstance(r[campo], str):
            raise ValueError(f"`{campo}` não é texto")
    s = r.get("sinais")
    if not isinstance(s, dict):
        raise ValueError("registro sem `sinais`")
    for k in _BOOLEANOS:
        if not isinstance(s.get(k), bool):
            raise ValueError(f"sinal `{k}` não é booleano")
    if not isinstance(s.get("sender_kind"), str):
        raise ValueError("sinal `sender_kind` não é texto")
    n = s.get("links_outside_sender_domain")
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("sinal `links_outside_sender_domain` inválido")
    if not isinstance(s.get("attachment_types"), list) or not all(isinstance(x, str) for x in s["attachment_types"]):
        raise ValueError("sinal `attachment_types` inválido")


def state_de(r: dict) -> dict:
    """State enxuto: nome exibido, assunto, corpo e só os sinais que as perguntas usam (`P.SINAIS_NO_STATE`).
    Endereço e domínio do remetente não existem no registro (anonimização) — o que sobra deles são os sinais."""
    return {"sender_name": r.get("remetente_nome") or "", "subject": r.get("assunto") or "", "body": r.get("texto") or "",
            "signals": {k: r["sinais"][k] for k in P.SINAIS_NO_STATE}}


def fora_da_faixa(state: dict) -> tuple[str, str] | None:
    """(origem, motivo) se o e-mail não deve ir ao Jev; None dentro da faixa validada."""
    if len(state["body"]) > P.TETO_CORPO:
        return "longo", f"corpo longo ({len(state['body'])} caracteres; teto {P.TETO_CORPO})"
    if not state["body"].strip():
        # Revisão do Codex (2026-10-01): antes só parava sem assunto E sem corpo; com assunto presente a política
        # ainda podia decidir `golpe` só pelo assunto. Corpo vazio escala ANTES da chamada, sempre.
        return "vazio", "corpo vazio: o Jev julgaria só pelo assunto"
    return None


def _sem_jev(motivo: str, origem: str) -> dict:
    """Escalada sem números do Jev. `origem`: `longo`, `vazio` ou `falha`."""
    return {"acao": "escala", "classe": None, "motivo": motivo, "origem": origem, "conf": None, "probs": {},
            "nouls": {q: None for q in P.NOULS}, "conflitos": [], "corpo": None, "truncado": False, "trava": None}


def decisao_falha(tipo: str) -> dict:
    """Falha operacional (entrada, chamada ou contrato da resposta): escala. O motivo leva só a etapa e a classe
    do erro — o texto da exceção pode citar o corpo da resposta ou do e-mail."""
    return _sem_jev(f"falha operacional: {tipo}", "falha")


# ---------------------------------------------------------------------------------------- resposta → decisão
def validar(resposta: dict) -> dict:
    """Resposta da API → números validados: todo ID esperado presente, `type` batendo, Choice entre as 6 classes
    com distribuição real somando ~1, Nouls reais em [0, 1] (não bool, não string). Falha = exceção."""
    answers = resposta.get("answers") if isinstance(resposta, dict) else None
    if not isinstance(answers, dict):
        raise ValueError("resposta sem `answers`")
    for q, p in P.PERGUNTAS.items():
        a = answers.get(q)
        if not isinstance(a, dict) or a.get("type", p["type"]) != p["type"]:
            raise ValueError(f"resposta sem `{q}` do tipo {p['type']}")
    c = CG.choice(resposta, P.CHOICE, set(P.CLASSES))
    return {"classe": c["choice"], "conf": c["confidence"], "probs": c["probabilities"],
            "nouls": {q: CG.noul(resposta, q) for q in P.NOULS}}


def conflitos(classe: str, nouls: dict) -> list[str]:
    """Nouls que contradizem a classe escolhida (regras em `P.CONFLITOS`). Lista vazia = sem conflito."""
    regra = P.CONFLITOS.get(classe, {})
    fora = [f"{q} alto ({nouls[q]:.2f})" for q in regra.get("alto", []) if nouls[q] >= P.NOUL_SIM]
    fora += [f"{q} não está baixo ({nouls[q]:.2f})" for q in regra.get("nao_baixo", []) if nouls[q] > P.NOUL_NAO]
    return fora


def compor(v: dict, corpo: int, truncado: bool = False) -> dict:
    """Números validados + tamanho do corpo (contado pelo código) + se a extração cortou o corpo → decisão da
    POLÍTICA. Guarda os números para medir e re-limiar sem chamar de novo. `trava` = a regra de código que
    barrou uma leitura acima do limiar (`corpo curto`, `truncado`, `conflito`) ou None."""
    classe, conf = v["classe"], v["conf"]
    fora = conflitos(classe, v["nouls"]) if P.USAR_CONFLITOS else []
    trava = None
    if conf < P.LIMIAR_CONF[classe]:
        acao, motivo = "escala", f"confiança {conf:.2f} < {P.LIMIAR_CONF[classe]} ({classe})"
    elif classe in P.CLASSES_CAIXA and corpo < P.MIN_CORPO_CAIXA:
        acao, motivo, trava = "escala", f"corpo curto ({corpo} caracteres) para decidir `{classe}` sozinho", "corpo curto"
    elif truncado and classe in P.CLASSES_CARAS:
        acao, motivo, trava = "escala", f"corpo truncado na extração: `{classe}` não se decide sozinho", "truncado"
    elif fora:
        acao, motivo, trava = "escala", f"conflito com `{classe}`: " + "; ".join(fora), "conflito"
    else:
        acao, motivo = "decide", f"`{classe}` com confiança {conf:.2f}, sem conflito"
    return {"acao": acao, "classe": classe, "motivo": motivo, "origem": "jev", "conf": conf, "probs": v["probs"],
            "nouls": v["nouls"], "conflitos": fora, "corpo": corpo, "truncado": truncado, "trava": trava}


def decidir(resposta: dict, corpo: int, truncado: bool = False) -> dict:
    """Resposta JSON da API + tamanho do corpo → decisão. Resposta fora do contrato LEVANTA exceção."""
    return compor(validar(resposta), corpo, truncado)


def rotear(jev, r: dict) -> dict:
    """Um e-mail de ponta a ponta: registro validado, faixa conferida, uma requisição, composição. Baixo nível:
    registro inválido, falha da chamada e resposta fora do contrato LEVANTAM exceção."""
    validar_registro(r)
    state = state_de(r)
    fora = fora_da_faixa(state)
    if fora:
        return _sem_jev(fora[1], fora[0])
    return decidir(jev.perguntar(state, P.PERGUNTAS), len(state["body"].strip()), r["sinais"]["body_truncated"])


def rotear_seguro(jev, r: dict) -> dict:
    """O que o consumidor (classificador de e-mail, lote) chama: os mesmos passos de `rotear`, mas NENHUMA falha
    sobe nem aborta o lote — timeout, erro HTTP, cache faltando, resposta fora do contrato ou registro inválido
    viram `escala` para AQUELE e-mail, com a etapa e a classe do erro no motivo. Pega `Exception` inteira de
    propósito: erro não previsto também tem de fechar em `escala` (falha nunca decide classe).
    Resposta com JSON válido mas fora do contrato (revisão do Codex, 2026-10-01): além de escalar, o pedido sai
    do cache (`jev.invalidar`) para que SÓ ele seja refeito na próxima rodada — sem isso a resposta ruim ficava
    presa no cache e "rode de novo" não refazia nada.
    @example rotear_seguro(jev_fora_do_ar, r) → {"acao": "escala", "motivo": "falha operacional: chamada (TimeoutError)", "origem": "falha", …}
    """
    etapa = "entrada inválida"
    try:
        validar_registro(r)
        state = state_de(r)
        fora = fora_da_faixa(state)
        if fora:
            return _sem_jev(fora[1], fora[0])
        etapa = "chamada"
        resposta = jev.perguntar(state, P.PERGUNTAS)
        etapa = "resposta inválida"
        return decidir(resposta, len(state["body"].strip()), r["sinais"]["body_truncated"])
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        if etapa == "resposta inválida":
            try:
                jev.invalidar(state, P.PERGUNTAS)
            except Exception:  # noqa: BLE001 — a quarentena falhar não pode tirar o e-mail da escalada
                pass
        return decisao_falha(f"{etapa} ({type(e).__name__})")


# ---------------------------------------------------------------------------------------- baseline de código
# Regras simples sobre os sinais + palavras-chave, na ordem. Sem regra que dispare → escala (como o Jev incerto).
# Palavras escolhidas por conhecimento geral de e-mail e conferidas só no ajuste; comparação sem acento e em
# minúsculas. É o "o que um script de uma tarde faria", não o motor de regras de produção.
_PEDE = ("pix", "boleto", "pagamento", "fatura", "transferencia", "senha", "atualizacao cadastral", "atualize",
         "bloquead", "comprovante", "nota fiscal", "nf-e", "processo", "intimacao", "protocolo", "orcar", "orcamento")
_TRANSACIONAL = ("recibo", "receipt", "confirmacao", "confirmation", "pedido", "ordered", "order", "assinatura",
                 "relatorio", "report", "aprovado", "codigo de verificacao", "fatura disponivel")
_CONDOMINIO = ("condominio", "condominial", "circular", "assembleia", "administradora", "locacao", "escritura")
_RESPOSTA = re.compile(r"^\s*(re|res|fw|fwd|enc)\s*:", re.IGNORECASE)


def _plano(texto: str) -> str:
    """Minúsculas e sem acento, para casar palavra-chave."""
    return unicodedata.normalize("NFKD", texto.casefold()).encode("ascii", "ignore").decode()


def baseline(r: dict) -> dict:
    """Regra de código, sem Jev: devolve `decide` + classe quando uma regra dispara, senão `escala`."""
    s = r["sinais"]
    assunto = r.get("assunto") or ""
    t = _plano(" ".join([r.get("remetente_nome") or "", assunto, r.get("texto") or ""]))
    tem = lambda palavras: any(p in t for p in palavras)  # noqa: E731
    if not s["dkim_aligned"] and not s["list_unsubscribe"] and tem(_PEDE) and s["links_outside_sender_domain"] > 0:
        return {"acao": "decide", "classe": "golpe", "motivo": "sem DKIM alinhado + pedido de dinheiro/dado + link externo"}
    if _RESPOSTA.match(assunto):
        return {"acao": "decide", "classe": "principal", "motivo": "resposta ou encaminhamento (RE/RES/FW/ENC)"}
    if s["dkim_aligned"] and tem(_CONDOMINIO):
        return {"acao": "decide", "classe": "principal", "motivo": "DKIM alinhado + palavra de condomínio/negócio"}
    if s["list_unsubscribe"] or s["bulk_precedence"]:
        if tem(_TRANSACIONAL):
            return {"acao": "decide", "classe": "notificacoes", "motivo": "lista + palavra transacional"}
        return {"acao": "decide", "classe": "promocoes", "motivo": "cabeçalho de descadastro ou envio em massa"}
    if s["auto_submitted"] or (s["dkim_aligned"] and tem(_TRANSACIONAL)):
        return {"acao": "decide", "classe": "notificacoes", "motivo": "automático ou DKIM alinhado + palavra transacional"}
    return {"acao": "escala", "classe": None, "motivo": "nenhuma regra disparou"}


def baseline_seguro(r: dict) -> dict:
    """O baseline como o relatório o chama: registro inválido não vira regra — escala, contado à parte."""
    try:
        validar_registro(r)
    except ValueError:
        return {"acao": "escala", "classe": None, "motivo": "falha operacional: entrada inválida"}
    return baseline(r)
