"""Triagem de alerta: UMA requisição ao Jev por alerta (4 Nouls + 1 Choice informativa); a ação é do código.

O Jev só julga: o contexto explica o alerta inteiro? o ativo é crítico? há indício de comprometimento? continua
acontecendo? O código decide a ação pela precedência de dados/LEIA-ME.md e NADA executa daqui:
  contain_now    PROPOSTA de contenção para o plantão/automação (que têm a própria permissão) — nunca autorização
  queue_tier2    fila do analista: indício sem as três condições, dúvida de indício, sinais em conflito, ou falha
  auto_close     fecha sem avisar: só com DUAS leituras de acordo (esperado sim E indício não) e sem veto do código
  notify_owner   avisa o dono; `urgencia` (acordar / manha) sai de ativo crítico + em andamento
Toda saída leva `autoriza: False`: quem executa confere a própria permissão (lição 36: a saída diz ao consumidor o
que ele NÃO pode fazer).

Fatos do código (o Jev não compara datas nem faz conta): dia do alerta, hora do alerta × faixas de horário escritas
no contexto, contexto vazio. Entram no state como fato calculado E na política como veto de `auto_close`.

Ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO: `decidir`/`julgar` levantam exceção;
`julgar_seguro` (o que o consumidor chama) converte a falha em `queue_tier2` com `origem: "falha"` para AQUELE
alerta — humano lê; nunca `auto_close`.
"""
from __future__ import annotations

import datetime
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

ACOES = P.ACOES
CAMPOS_ALERTA = ("fonte", "titulo", "detalhe", "ativo", "ambiente")
OPCOES_ACAO = set(P.PERGUNTAS["action"]["criteria"])


# ---------------------------------------------------------------------------------------- entrada
def validar_alerta(caso) -> None:
    """Alerta malformado = erro ANTES da chamada (vira falha operacional em `julgar_seguro`). As mensagens citam só
    o nome do campo, nunca o conteúdo."""
    if not isinstance(caso, dict) or not isinstance(caso.get("alerta"), dict):
        raise ValueError("caso sem `alerta`")
    alerta, contexto = caso["alerta"], caso.get("contexto")
    for campo in CAMPOS_ALERTA:
        if not isinstance(alerta.get(campo), str) or not alerta[campo].strip():
            raise ValueError(f"`alerta.{campo}` vazio ou não textual")
    if alerta["fonte"] not in P.FONTES:
        raise ValueError("`alerta.fonte` fora da enumeração")
    if alerta["ambiente"] not in P.AMBIENTES:
        raise ValueError("`alerta.ambiente` fora da enumeração")
    if not isinstance(contexto, list) or any(not isinstance(l, str) or not l.strip() for l in contexto):
        raise ValueError("`contexto` não é lista de linhas de texto")
    tamanho = sum(len(alerta[c]) for c in CAMPOS_ALERTA) + sum(len(l) for l in contexto)
    if tamanho > P.TETO_CARACTERES or len(contexto) > P.TETO_LINHAS_CONTEXTO:
        raise ValueError("alerta fora da faixa validada (tamanho)")


# ---------------------------------------------------------------------------------------- fatos de tempo (código)
# Hora = HH:MM (com segundos opcionais). Só o formato dos dados: "3 h de duração" e "90 min" não são hora, e
# endereço IP, porta e contagem não casam (os lookarounds barram dígito, ponto, barra e dois-pontos vizinhos; hora
# seguida de dois-pontos de pontuação — "01:02 a 01:17: 212 requisições" — vale).
_HM = r"(?<![\d:/.,])([01]?\d|2[0-3]):([0-5]\d)(?::[0-5]\d)?(?!\d|:\d)"
_DATA = r"(?<![\d/.])(\d{1,2})/(\d{1,2})(?![\d/])"  # dia/mês
_RE_HM = re.compile(_HM)
_RE_EVENTO = re.compile(rf"(?:{_DATA}\s+(?:(?:às|as|à|a)\s+)?)?{_HM}")
# Entre duas horas de uma faixa: "às", "a", "até", traço — ou "e" quando a faixa começa com "entre".
_RE_MEIO = re.compile(rf"^\s*(às|as|a|até|ate|e|-|–|—)\s*(?:{_DATA}\s+)?(?:(?:às|as)\s+)?$", re.IGNORECASE)
# A data da 1ª ponta pode vir colada à hora com "às" ("28/09 às 22:00"): sem isto a data inicial se perdia e a janela
# vencida virava janela diária (revisão do Codex, 2026-10-01).
_RE_ANTES = re.compile(rf"(?:{_DATA}\s+(?:(?:às|as|à|a)\s+)?)?(?:(das|de|desde|entre)\s+)?(?:{_DATA}\s+(?:(?:às|as|à|a)\s+)?)?$",
                       re.IGNORECASE)
_DIAS = ["Monday (segunda-feira)", "Tuesday (terça-feira)", "Wednesday (quarta-feira)", "Thursday (quinta-feira)",
         "Friday (sexta-feira)", "Saturday (sábado)", "Sunday (domingo)"]


def _quando(mes: int, dia: int, hora: int, minuto: int) -> datetime.datetime | None:
    """Data-hora no ano dos dados; None se a data não existe (31/02)."""
    try:
        return datetime.datetime(P.ANO_DOS_DADOS, mes, dia, hora, minuto)
    except ValueError:
        return None


def horas_do_alerta(detalhe: str) -> list[datetime.datetime]:
    """Toda hora escrita em `alerta.detalhe`, com data: a data escrita antes dela ("30/09 19:12"); senão a da hora
    anterior, se o detalhe já deu uma data (vira o dia se a hora andou para trás); senão a convenção dos dados
    (≥ 12:00 = véspera, < 12:00 = dia do alerta).
    @example horas_do_alerta("CPU alta desde 21:40; às 03:10 continua") → [30/09 21:40, 01/10 03:10]
    """
    eventos, anterior, com_data = [], None, False
    for m in _RE_EVENTO.finditer(detalhe):
        dia, mes, hora, minuto = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        quando = _quando(int(mes), int(dia), hora, minuto) if dia else None
        if quando is not None:
            com_data = True
        elif com_data and anterior is not None:
            quando = anterior.replace(hour=hora, minute=minuto)
            if quando < anterior:
                quando += datetime.timedelta(days=1)
        else:
            quando = _quando(*P.NOITE_PADRAO[0 if hora >= 12 else 1], hora, minuto)
        eventos.append(quando)
        anterior = quando
    return eventos


def faixas_do_contexto(linha: str) -> list[dict]:
    """Faixas de horário escritas numa linha do contexto: duas horas seguidas ligadas por "às/a/até/–" (ou por "e"
    depois de "entre"), com data opcional em cada ponta. Hora solta ("deploy às 02:09") não é faixa.
    @example faixas_do_contexto("Janela: 30/09 22:00 a 01/10 06:00.") → [{"texto": "30/09 22:00 a 01/10 06:00", …}]
    """
    faixas, horas = [], list(_RE_HM.finditer(linha))
    for a, b in zip(horas, horas[1:]):
        meio = _RE_MEIO.match(linha[a.end():b.start()])
        antes = _RE_ANTES.search(linha[:a.start()])
        if not meio:
            continue
        palavra = (antes.group(3) or "").lower()
        if meio.group(1).lower() == "e" and palavra != "entre":
            continue  # "às 02:09 e 02:40" são duas horas soltas, não uma faixa
        # data da 1ª ponta: colada na hora ("30/09 22:00") ou antes da palavra ("01/10 das 01:00")
        d1 = (antes.group(4), antes.group(5)) if antes.group(4) else (antes.group(1), antes.group(2))
        d2 = (meio.group(2), meio.group(3))
        inicio_texto = antes.start() if (antes.group(1) or antes.group(3) or antes.group(4)) else a.start()
        faixas.append({"texto": linha[inicio_texto:b.end()].strip(),
                       "t1": (int(a.group(1)), int(a.group(2))), "t2": (int(b.group(1)), int(b.group(2))),
                       "d1": (int(d1[1]), int(d1[0])) if d1[0] else None,   # (mês, dia)
                       "d2": (int(d2[1]), int(d2[0])) if d2[0] else None})
    return faixas


def _dentro(quando: datetime.datetime, faixa: dict) -> bool | None:
    """A hora do alerta cai na faixa? Com data na 1ª ponta: intervalo absoluto (a 2ª ponta herda a data se não tem a
    sua). Sem data nenhuma: hora do dia (a faixa pode atravessar a meia-noite). `None` = NÃO dá para comparar: data
    só na 2ª ponta ou data inválida (31/02) — uma faixa com data pela metade nunca vira janela diária, senão uma
    janela vencida "cobre" o alerta de hoje (revisão do Codex, 2026-10-01)."""
    if faixa["d1"] is None and faixa["d2"] is None:
        minuto, a, b = quando.hour * 60 + quando.minute, faixa["t1"][0] * 60 + faixa["t1"][1], faixa["t2"][0] * 60 + faixa["t2"][1]
        return a <= minuto <= b if a <= b else (minuto >= a or minuto <= b)
    if faixa["d1"] is None:
        return None
    inicio = _quando(*faixa["d1"], *faixa["t1"])
    fim = _quando(*(faixa["d2"] or faixa["d1"]), *faixa["t2"])
    if inicio is None or fim is None:
        return None
    if fim <= inicio:
        fim += datetime.timedelta(days=1)
    return inicio <= quando <= fim


def _dia_em_ingles(d: datetime.date) -> str:
    return f"{_DIAS[d.weekday()]} {d.isoformat()} ({d.day:02d}/{d.month:02d})"


def fatos_de_tempo(detalhe: str, contexto: list[str]) -> dict:
    """Tudo o que o código calcula antes da chamada. `veto` = há faixa de horário no contexto, há hora no alerta e
    NENHUMA faixa comprovadamente contém todas as horas do alerta: o contexto não cobre a hora, então o alerta não
    fecha sozinho. Faixa que não dá para comparar (data pela metade ou inválida) não gera fato dentro/fora e não
    derruba o veto: o Jev lê o texto como antes.
    @example fatos_de_tempo("04:42 reiniciou. Voltou às 04:44.", ["Janela MUD-1: 01/10 das 01:00 às 03:00."])["veto"] → True
    """
    eventos = horas_do_alerta(detalhe)
    faixas = [f for linha in contexto for f in faixas_do_contexto(linha)]
    hm = lambda e: e.strftime("%H:%M")  # noqa: E731
    frases, veto = [], bool(eventos and faixas)
    for f in faixas:
        if not eventos:
            break
        if any(_dentro(e, f) is None for e in eventos):
            frases.append(f"The time range '{f['texto']}' written in `context` could not be compared with the alert times "
                          "(its date is incomplete or invalid).")
            continue
        dentro = [hm(e) for e in eventos if _dentro(e, f)]
        fora = [hm(e) for e in eventos if not _dentro(e, f)]
        if not fora:
            veto = False
            frases.append(f"All alert times ({', '.join(dentro)}) are INSIDE the time range '{f['texto']}' written in `context`.")
        elif not dentro:
            frases.append(f"All alert times ({', '.join(fora)}) are OUTSIDE the time range '{f['texto']}' written in `context`.")
        else:
            frases.append(f"Alert times {', '.join(dentro)} are INSIDE and {', '.join(fora)} are OUTSIDE the time range "
                          f"'{f['texto']}' written in `context`.")
    if not faixas:
        frases = ["No time range is written in `context`, so there is nothing to compare."]
    elif not eventos:
        frases = ["`alert.detail` has no clock time to compare with the time ranges written in `context`."]
    padrao = datetime.date(P.ANO_DOS_DADOS, *P.NOITE_PADRAO[1])
    dias = sorted({e.date() for e in eventos}) or [padrao]
    dia = _dia_em_ingles(dias[0]) if len(dias) == 1 else f"from {_dia_em_ingles(dias[0])} to {_dia_em_ingles(dias[-1])}"
    return {"dia": dia, "frases": frases, "veto": veto, "faixas": len(faixas), "horas": [hm(e) for e in eventos],
            "contexto_vazio": not contexto}


def state_de(caso: dict, fatos: dict, com_fatos: bool = True) -> dict:
    """Caso (pt) → state enxuto com os nomes que as perguntas citam entre crases. `fonte` e `ambiente` são campos
    estruturados do emissor do alerta (fato, não julgamento). `com_fatos=False` é a variante medida no ajuste.
    @example state_de(caso, fatos)["computed_by_code"]["alert_day"] → "Thursday (quinta-feira) 2026-10-01 (01/10)"
    """
    a = caso["alerta"]
    state = {"alert": {"source": P.FONTES[a["fonte"]], "title": a["titulo"], "detail": a["detalhe"], "asset": a["ativo"],
                       "environment": P.AMBIENTES[a["ambiente"]]},
             "context": list(caso["contexto"])}
    if com_fatos:
        state["computed_by_code"] = {"alert_day": fatos["dia"], "time_ranges": fatos["frases"]}
    return state


# ---------------------------------------------------------------------------------------- política
def precedencia(esperada, critico, indicio, andamento) -> str:
    """A função mecânica do LEIA-ME, de sinais (True / False / None) para ação. `None` nunca fecha e nunca contém."""
    if indicio is True and critico is True and andamento is True:
        return "contain_now"
    if indicio is not False:
        return "queue_tier2"
    return "auto_close" if esperada is True else "notify_owner"


def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    """Noul em três faixas: True / False / None (= dúvida)."""
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def politica(s: dict, fatos: dict) -> dict:
    """Sinais em três estados + fatos do código → ação. É aqui que mora a assimetria:
    - `auto_close` precisa de esperado SIM e indício NÃO (duas leituras) e de nenhum veto do código;
    - nenhum valor de `expected_activity` tira da fila ou da contenção um alerta cujo indício não é NÃO;
    - indício + crítico + andamento com esperado SIM é conflito → fila (não se contém o que parece planejado);
      mas o veto do código (contexto vazio, hora fora da faixa) derruba o "esperado" ANTES: aí não há conflito e a
      contenção segue a precedência — o Jev disse "planejado" sobre um contexto que não sustenta isso.
    """
    esperada, critico = s["expected_activity"], s["critical_asset"]
    indicio, andamento = s["compromise_indication"], s["ongoing"]
    veto = None
    if esperada is True and fatos["contexto_vazio"]:
        esperada, veto = False, "contexto vazio: nada explica o alerta"
    elif esperada is True and fatos["veto"]:
        esperada, veto = False, "hora do alerta fora de toda faixa de horário escrita no contexto"
    acao, urgencia = precedencia(esperada, critico, indicio, andamento), None
    if acao == "contain_now" and esperada is True and P.CONFLITO_VAI_PARA_FILA:
        acao, motivo = "queue_tier2", "sinais em conflito: indício em andamento em ativo crítico E atividade esperada"
    elif acao == "contain_now":
        motivo = "indício de comprometimento em andamento em ativo crítico (proposta de contenção)"
    elif acao == "queue_tier2":
        motivo = "dúvida de indício" if indicio is None else "indício sem as três condições de contenção"
    elif acao == "auto_close":
        motivo = "o contexto explica o alerta inteiro e não há indício"
    else:
        # A urgência do aviso é do código (LEIA-ME): ativo crítico e em andamento → acorda o dono. Dúvida acorda.
        urgencia = "acordar" if critico is not False and andamento is not False else "manha"
        motivo = ("sem indício e " + (f"esperado vetado pelo código ({veto})" if veto else "o contexto não explica o alerta inteiro"))
    return {"acao": acao, "urgencia": urgencia, "motivo": motivo, "esperado_efetivo": esperada, "veto": veto}


def validar(resposta: dict) -> dict:
    """Resposta da API → números validados pela infra comum: todo ID esperado presente, discriminador `type` batendo,
    Noul número real em [0,1] (não bool, não string), Choice com vencedor entre as opções e distribuição completa.
    Qualquer falha = erro operacional (exceção), nunca `auto_close`."""
    answers = resposta.get("answers") or {}
    for q, p in P.PERGUNTAS.items():
        a = answers.get(q)
        if not isinstance(a, dict) or a.get("type", p["type"]) != p["type"]:
            raise ValueError(f"resposta sem `{q}` do tipo {p['type']}")
    return {"choice": CG.choice(resposta, "action", OPCOES_ACAO), **{q: CG.noul(resposta, q) for q in P.NOULS}}


def decidir(resposta: dict, fatos: dict) -> dict:
    """Resposta JSON da API + fatos do código → decisão (guarda os números brutos para medir e re-limiar sem chamar
    de novo). A Choice `action` é guardada e NÃO entra na ação (variante informativa)."""
    v = validar(resposta)
    s = {q: _faixa(v[q], *P.FAIXA[q]) for q in P.NOULS}
    return {**politica(s, fatos), "origem": "jev", "autoriza": False, "nouls": {q: v[q] for q in P.NOULS},
            "sinais": s, "choice": v["choice"], "fatos": fatos}


def decisao_falha(tipo: str) -> dict:
    """Decisão para falha operacional (entrada, chamada ou contrato da resposta): fila do analista, humano lê. O
    motivo leva só a etapa e a classe do erro — o texto da exceção pode citar o corpo da resposta."""
    return {"acao": "queue_tier2", "urgencia": None, "motivo": f"falha operacional: {tipo}", "esperado_efetivo": None,
            "veto": None, "origem": "falha", "autoriza": False, "nouls": {q: None for q in P.NOULS},
            "sinais": {q: None for q in P.NOULS}, "choice": None, "fatos": None}


# ---------------------------------------------------------------------------------------- baseline de código
def _plano(texto: str) -> str:
    """Minúsculas, sem acento — as listas de expressões são escritas assim."""
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


def baseline(caso: dict) -> dict:
    """Só regras de código, sem Jev: palavra-chave no alerta e no contexto, ambiente, e os MESMOS fatos de tempo do
    código (contexto vazio e hora fora da faixa não fecham). Mesma precedência. Nunca tem dúvida.
    @example baseline(caso_shell_reverso_em_prod)["acao"] → "contain_now"
    """
    a, contexto = caso["alerta"], caso["contexto"]
    alerta, ctx = _plano(a["titulo"] + " " + a["detalhe"]), _plano(" ".join(contexto))
    bate = lambda lista, t: any(re.search(p, t) for p in lista)  # noqa: E731
    fatos = fatos_de_tempo(a["detalhe"], contexto)
    sinais = {
        "atividade_esperada": bool(contexto) and bate(P.BASELINE_ESPERADA, ctx) and not fatos["veto"],
        "ativo_critico": (a["ambiente"] == "prod" and not bate(P.BASELINE_NAO_CRITICO, _plano(a["ativo"]) + " " + ctx))
                         or bate(P.BASELINE_COPIA_DE_PROD, ctx),
        "indicio_de_comprometimento": bate(P.BASELINE_INDICIO, alerta) and not bate(P.BASELINE_BARRADA, alerta),
        # "continua" manda; senão palavra de encerramento; sem nenhuma das duas, a condição persiste.
        "em_andamento": bate(P.BASELINE_EM_ANDAMENTO, alerta) or not bate(P.BASELINE_ENCERRADO, alerta),
    }
    acao = precedencia(sinais["atividade_esperada"], sinais["ativo_critico"], sinais["indicio_de_comprometimento"],
                       sinais["em_andamento"])
    urgencia = None
    if acao == "notify_owner":
        urgencia = "acordar" if sinais["ativo_critico"] and sinais["em_andamento"] else "manha"
    return {"acao": acao, "urgencia": urgencia, "sinais": sinais}


def baseline_seguro(caso: dict) -> dict:
    """O baseline pelo mesmo contrato de falha: alerta malformado → fila."""
    try:
        validar_alerta(caso)
        return baseline(caso)
    except Exception:  # noqa: BLE001 — falha fechada
        return {"acao": "queue_tier2", "urgencia": None, "sinais": {}}


# ---------------------------------------------------------------------------------------- chamada
def pedido(caso: dict, com_fatos: bool = True) -> tuple[dict, dict, dict]:
    """(state, questions, fatos) de um alerta — todas as perguntas na mesma requisição (mesmo state, isoladas)."""
    validar_alerta(caso)
    fatos = fatos_de_tempo(caso["alerta"]["detalhe"], caso["contexto"])
    return state_de(caso, fatos, com_fatos), P.PERGUNTAS, fatos


def _rejeicao_de_contrato(jev, resposta, state: dict, questions: dict) -> None:
    """Resposta JSON válida mas fora do contrato (bool, ID faltando, número fora de [0,1]) é tirada do cache antes de
    levantar, para ser refeita sozinha na próxima rodada — nos dois níveis (revisão do Codex no supervisor-de-automacao,
    2026-10-02: a família ficava presa no cache aqui). Só o CONTRATO invalida; defeito de política e falha de chamada não."""
    try:
        validar(resposta)
    except Exception:
        if hasattr(jev, "invalidar"):
            try:
                jev.invalidar(state, questions)
            except Exception:  # noqa: BLE001 — zelo pelo cache não pode esconder a falha original
                pass
        raise


def julgar(jev, caso: dict, com_fatos: bool = True) -> dict:
    """Um alerta de ponta a ponta: entrada validada, fatos calculados, uma requisição, decisão em código.
    Baixo nível: alerta malformado, falha da chamada e resposta fora do contrato LEVANTAM exceção (a resposta fora do
    contrato é invalidada no cache antes)."""
    state, questions, fatos = pedido(caso, com_fatos)
    resposta = jev.perguntar(state, questions)
    _rejeicao_de_contrato(jev, resposta, state, questions)
    return decidir(resposta, fatos)


def julgar_seguro(jev, caso: dict, com_fatos: bool = True) -> dict:
    """O que o consumidor (fila do plantão, lote) chama: os mesmos passos de `julgar`, mas NENHUMA falha sobe nem
    aborta o lote — timeout, erro HTTP, cache faltando, resposta fora do contrato ou alerta malformado viram
    `queue_tier2` com `origem: "falha"` para AQUELE alerta. Pega `Exception` inteira de propósito: na triagem das
    3h, erro não previsto também tem de cair em fila com humano, nunca em `auto_close`.
    @example julgar_seguro(jev_fora_do_ar, caso)
             → {"acao": "queue_tier2", "origem": "falha", "motivo": "falha operacional: chamada (TimeoutError)", …}
    """
    etapa = "entrada inválida"
    try:
        state, questions, fatos = pedido(caso, com_fatos)
        etapa = "chamada"
        resposta = jev.perguntar(state, questions)
        etapa = "resposta inválida"
        _rejeicao_de_contrato(jev, resposta, state, questions)
        etapa = "política"
        return decidir(resposta, fatos)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        return decisao_falha(f"{etapa} ({type(e).__name__})")
