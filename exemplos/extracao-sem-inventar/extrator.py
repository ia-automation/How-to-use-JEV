"""Extração de uma mensagem: candidatos (código) → UMA chamada ao Jev com todas as perguntas → valor (código).

O Jev só escolhe entre trechos que a regex achou (ou `none`) e lê partes de data e escala de número.
O valor devolvido é sempre cópia normalizada de um trecho, ou data montada pelo código a partir de partes.
Campo sem candidato não gera pergunta (null sem custo); mensagem sem nada não gera chamada.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import candidatos as C
import perguntas as P

CAMPOS = ["email", "telefone", "cpf", "valor", "data_visita"]


def montar(mensagem: str) -> tuple[dict, dict, dict]:
    """(state, questions, contexto). `contexto` guarda os candidatos para o código decidir depois."""
    emails = C.emails(mensagem)
    tels = C.telefones(mensagem)
    cpfs, cpfs_dv_invalido = C.cpfs(mensagem)
    # Número que já é e-mail, telefone ou CPF (válido ou não) não concorre a valor em R$.
    donos = [(c["inicio"], c["fim"]) for c in emails + tels if c["origem"] == "literal"]
    donos += [m.span() for m in C._CPF.finditer(mensagem)]
    vals = C.valores(mensagem, donos)
    ctx = {"email": emails, "telefone": tels, "cpf": cpfs, "valor": vals, "cpf_dv_invalido": cpfs_dv_invalido,
           "escalas": {}, "data_perguntada": False}

    q = {}
    for campo in ("email", "telefone", "cpf", "valor"):
        if ctx[campo]:
            q[campo] = P.escolha(campo, ctx[campo])
    for n, c in enumerate([c for c in vals if c["nu"]][:P.MAX_ESCALAS]):
        q[f"valor_escala_{n}"] = P.escala(c["texto"])
        ctx["escalas"][c["texto"]] = f"valor_escala_{n}"
    if C.pistas_de_data(mensagem):
        q.update(P.perguntas_data(C.anos(mensagem)))
        ctx["data_perguntada"] = True
    return {"message": mensagem}, q, ctx


def _saida(valor=None, revisar=False, motivo="", conf=None, escolha=None, origem=None) -> dict:
    return {"valor": valor, "revisar": revisar, "motivo": motivo, "conf": conf, "escolha": escolha, "origem": origem}


def _decidir_escolha(campo: str, a: dict, ctx: dict) -> dict:
    cands = ctx[campo]
    if not cands:
        if campo == "cpf" and ctx["cpf_dv_invalido"]:
            return _saida(revisar=True, motivo="só CPF com dígito verificador inválido")
        return _saida(motivo="sem candidato")
    r = a[campo]
    conf, escolhido = r["confidence"], r["choice"]
    baixa = conf < P.CONF_MIN[campo]
    if escolhido == P.NONE:
        return _saida(revisar=baixa, motivo="jev: nenhum" + (" (conf. baixa)" if baixa else ""), conf=conf)
    c = next(c for c in cands if c["texto"] == escolhido)
    valor, motivos = c["valor"], []
    if campo == "valor" and c["nu"]:
        qid = ctx["escalas"].get(c["texto"])
        if qid is None:
            motivos.append("número cru sem pergunta de escala")
            valor = None
        else:
            e = a[qid]
            valor = f"{(c['base'] * P.ESCALA_FATOR[e['choice']]).quantize(Decimal('0.01'))}"
            conf = min(conf, e["confidence"])
            baixa = baixa or e["confidence"] < P.ESCALA_CONF_MIN
    if valor is None and not motivos:
        motivos.append("trecho escolhido não normaliza (incompleto/inválido)")
    if c["origem"] == "reconstruido" and P.RECONSTRUIDO_REVISA:
        motivos.append("e-mail reconstruído de correção")
    if baixa:
        motivos.append("conf. baixa")
    return _saida(valor, bool(motivos), "; ".join(motivos), conf, escolhido, c["origem"])


# ---------------------------------------------------------------- calendário (código, nunca o Jev)
def proxima_ocorrencia_dia(ref: date, dia: int) -> date | None:
    """Dia do mês sem mês escrito: a próxima vez que ele cai, a partir da referência (inclusive)."""
    for k in range(13):
        ano, mes = ref.year + (ref.month - 1 + k) // 12, (ref.month - 1 + k) % 12 + 1
        try:
            d = date(ano, mes, dia)
        except ValueError:
            continue
        if d >= ref:
            return d
    return None


def resolver_dia_semana(ref: date, w: int, semana: str) -> date | None:
    """Convenções de DADOS.md §Decisões 4 (semana civil = segunda a domingo, ISO):
    plain ('sexta', 'sexta que vem', 'próxima sexta') → próxima sexta ESTRITAMENTE depois da referência;
    next_week ('sexta da semana que vem') → sexta da semana civil seguinte;
    this_week ('essa sexta') → sexta desta semana; se já passou, None (vai para revisão, não se adivinha).
    """
    segunda = ref - timedelta(days=ref.weekday())
    if semana == "next_week":
        return segunda + timedelta(days=7 + w)
    if semana == "this_week":
        d = segunda + timedelta(days=w)
        return d if d >= ref else None
    return ref + timedelta(days=(w - ref.weekday() - 1) % 7 + 1)


def _decidir_data(a: dict, ctx: dict, ref: date) -> dict:
    if not ctx["data_perguntada"]:
        return _saida(motivo="sem pista de data")
    modo = a["visita_modo"]
    usadas = [modo["confidence"]]

    def parte(nome):
        r = a.get(nome)
        if r is None:
            return P.NONE
        usadas.append(r["confidence"])
        return r["choice"]

    d, motivo = None, ""
    if modo["choice"] in (P.NONE, "unclear"):
        motivo = f"modo {modo['choice']}"
    elif modo["choice"] == "absolute":
        dia, mes, ano = parte("visita_dia"), parte("visita_mes"), parte("visita_ano")
        if dia == P.NONE:
            motivo = "dia não lido"
        elif mes == P.NONE:
            d = proxima_ocorrencia_dia(ref, int(dia))
        else:
            m = P.MESES.index(mes) + 1
            try:
                if ano != P.NONE:
                    d = date(int(ano), m, int(dia))
                else:  # data sem ano → próxima ocorrência a partir da referência (inclusive)
                    d = date(ref.year, m, int(dia))
                    if d < ref:
                        d = date(ref.year + 1, m, int(dia))
            except ValueError:
                motivo = f"data impossível: {dia} {mes} {ano}"
    else:
        anc = parte("visita_relativo")
        if anc in ("today", "tomorrow", "day_after"):
            d = ref + timedelta(days={"today": 0, "tomorrow": 1, "day_after": 2}[anc])
        else:
            ds, sem = parte("visita_dia_semana"), parte("visita_semana")
            if ds == P.NONE:
                motivo = "dia relativo não lido"
            else:
                d = resolver_dia_semana(ref, P.DIAS_SEMANA.index(ds), sem)
                motivo = "" if d else "dia 'desta semana' já passou"
    conf = min(usadas)
    if d is None:
        # modo none/unclear com confiança alta = null automático; falha estrutural = revisão
        revisar = conf < P.CONF_MIN["data_visita"] or modo["choice"] not in (P.NONE, "unclear")
        return _saida(revisar=revisar, motivo=motivo, conf=conf, escolha=modo["choice"])
    baixa = conf < P.CONF_MIN["data_visita"]
    return _saida(d.isoformat(), baixa, "conf. baixa" if baixa else "", conf, modo["choice"])


def extrair(resposta: dict, ctx: dict, data_referencia: str) -> dict:
    """Resposta JSON da API → {campo: saída}. Guarda confiança e escolha para medir e re-limiar sem nova chamada."""
    a = resposta.get("answers", {})
    out = {campo: _decidir_escolha(campo, a, ctx) for campo in ("email", "telefone", "cpf", "valor")}
    out["data_visita"] = _decidir_data(a, ctx, date.fromisoformat(data_referencia))
    return out


def partes_data(resposta: dict) -> dict:
    """Escolhas brutas das partes de data (para o relatório caso a caso)."""
    return {k.removeprefix("visita_"): v["choice"] for k, v in resposta.get("answers", {}).items()
            if k.startswith("visita_") and v["choice"] != P.NONE}

