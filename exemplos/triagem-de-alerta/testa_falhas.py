"""Bateria do código da triagem de alerta — roda sem chave e sem rede (`python testa_falhas.py`).

O que os conjuntos rotulados não exercitam, provado com um dublê no lugar do Jev:
  A. falha operacional — resposta falsa (bool no lugar de número, ID faltando, Choice sem distribuição…), exceção de
     rede simulada, alerta malformado ou registro de cache forjado (medição vazia, lido pelo cliente real numa pasta
     temporária): `julgar_seguro` devolve `queue_tier2` com `origem: "falha"` e `autoriza: False` para AQUELE alerta,
     nunca `auto_close`, o lote não aborta e `resumo()` não derruba o relatório; `julgar` (baixo nível) continua levantando;
  B. política — grade inteira de `politica` (três estados por Noul × contexto vazio / veto de horário / normal):
     `auto_close` só com esperado SIM e indício NÃO, contexto não vazio e sem veto; indício que não é NÃO nunca sai
     `auto_close` nem `notify_owner`, seja qual for `expected_activity` (texto que "explica" não rebaixa um alerta
     com indício — limite #6); `contain_now` só com indício, ativo crítico e andamento SIM e esperado não-SIM;
     toda saída com `autoriza: False`; sem veto nem conflito, a ação é a precedência do LEIA-ME;
  C. fatos de tempo (código) — faixa com e sem data, data nas duas pontas (com "às" colado), faixa que atravessa a
     meia-noite, "entre X e Y", hora solta e "às X e Y" não são faixa, IP/porta/contagem não viram hora, hora ≥ 12:00
     é da véspera, veto só quando toda hora do alerta cai fora de toda faixa; janela vencida, data só na ponta final
     ou data inválida NUNCA vira janela diária (fato ausente, veto mantido);
  D. erros caros (`run.erros_caros`) e baseline em entrada malformada.
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import copy
import datetime
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
import triagem as T  # noqa: E402
from jevcache import Jev  # noqa: E402

BAIXO = {q: P.FAIXA[q][0] / 2 for q in P.NOULS}                      # dentro do "não"
DUVIDA = {q: (P.FAIXA[q][0] + P.FAIXA[q][1]) / 2 for q in P.NOULS}  # dentro da faixa do meio
ALTO = {q: (P.FAIXA[q][1] + 1) / 2 for q in P.NOULS}                # dentro do "sim"
NIVEIS = {"nao": BAIXO, "duvida": DUVIDA, "sim": ALTO}
OPCOES = list(P.PERGUNTAS["action"]["criteria"])


def caso(detalhe: str = "02:10 reiniciou. Saudável às 02:15.", contexto: list | None = None, **alerta) -> dict:
    """Alerta válido, inventado para a bateria (não é caso dos dados)."""
    a = {"fonte": "monitoramento", "titulo": "Serviço reiniciou", "detalhe": detalhe, "ativo": "api-exemplo", "ambiente": "prod"}
    a.update(alerta)
    return {"id": "X", "alerta": a, "contexto": ["Deploy do api-exemplo às 02:09 pelo pipeline."] if contexto is None else contexto}


def resposta(acao: str = "notify_owner", conf: float = 1.0, **nouls: float) -> dict:
    """Resposta VÁLIDA no formato da API. Sem argumentos: esperado alto, resto baixo → `auto_close` (o pior destino
    possível para uma falha tolerada: se a validação deixar passar, a bateria vê `auto_close`)."""
    resto = (1.0 - conf) / (len(OPCOES) - 1)
    probs = {o: (conf if o == acao else resto) for o in OPCOES}
    valores = {"expected_activity": ALTO["expected_activity"], **{q: BAIXO[q] for q in P.NOULS if q != "expected_activity"}, **nouls}
    return {"model": "duble", "answers": {"action": {"type": "choice", "choice": acao, "confidence": conf, "probabilities": probs},
                                          **{q: {"type": "noul", "noul": valores[q]} for q in P.NOULS}}}


class Duble:
    """Jev de mentira: devolve a resposta dada ou levanta a exceção dada; por título do alerta, se `por_titulo`."""

    def __init__(self, padrao=None, por_titulo: dict | None = None):
        self.padrao, self.por_titulo = padrao if padrao is not None else resposta(), por_titulo or {}

    def perguntar(self, state, questions):
        saida = self.por_titulo.get(state["alert"]["title"], self.padrao)
        if isinstance(saida, Exception):
            raise saida
        return saida

    def resumo(self) -> dict:
        return {}


class ErroHTTP(Exception):
    """Faz o papel do erro de status do SDK (503, 429…) sem depender da classe dele."""


def _mexe(caminho: list, valor=None, apaga: bool = False):
    """Fábrica de corrupção: troca (ou apaga) um campo de uma resposta válida."""
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
    ("Noul bool True no lugar de número (viraria 1.0)", _mexe(["answers", "expected_activity", "noul"], True)),
    ("Noul bool False no lugar de número (indício 0.0 → fecharia)", _mexe(["answers", "compromise_indication", "noul"], False)),
    ("Noul string", _mexe(["answers", "compromise_indication", "noul"], "0.05")),
    ("Noul None", _mexe(["answers", "ongoing", "noul"], None)),
    ("Noul NaN", _mexe(["answers", "critical_asset", "noul"], math.nan)),
    ("Noul infinito", _mexe(["answers", "expected_activity", "noul"], math.inf)),
    ("Noul fora de [0, 1] (1.5)", _mexe(["answers", "expected_activity", "noul"], 1.5)),
    ("Noul negativo", _mexe(["answers", "compromise_indication", "noul"], -0.1)),
    ("Noul sem o campo `noul`", _mexe(["answers", "ongoing", "noul"], apaga=True)),
    ("ID de Noul faltando", _mexe(["answers", "compromise_indication"], apaga=True)),
    ("ID da Choice faltando", _mexe(["answers", "action"], apaga=True)),
    ("discriminador `type` trocado (Noul que volta como choice)", _mexe(["answers", "expected_activity", "type"], "choice")),
    ("resposta de um ID que não é objeto", _mexe(["answers", "critical_asset"], 0.9)),
    ("Choice sem distribuição", _mexe(["answers", "action", "probabilities"], apaga=True)),
    ("Choice com distribuição incompleta", _mexe(["answers", "action", "probabilities"], {"notify_owner": 1.0})),
    ("Choice com distribuição que não soma 1", _mexe(["answers", "action", "probabilities"], {o: 0.5 for o in OPCOES})),
    ("Choice com probabilidade bool", _mexe(["answers", "action", "probabilities", "notify_owner"], True)),
    ("Choice com vencedor fora das opções", _mexe(["answers", "action", "choice"], "escalate")),
    ("Choice sem confiança", _mexe(["answers", "action", "confidence"], apaga=True)),
    ("`answers` vazio", _mexe(["answers"], {})),
    ("`answers` None", _mexe(["answers"], None)),
    ("sem `answers`", _mexe(["answers"], apaga=True)),
]
RESPOSTAS_INTEIRAS = [("resposta None", None), ("resposta lista", []), ("resposta string", "ok"), ("resposta {}", {})]
EXCECOES = [
    ("timeout", TimeoutError("tempo esgotado")),
    ("conexão recusada", ConnectionError("sem rede")),
    ("erro HTTP 503", ErroHTTP("503 Service Unavailable")),
    ("erro HTTP 429", ErroHTTP("429 Too Many Requests")),
    ("cache faltando no modo gravado", RuntimeError("resposta não gravada no cache")),
    ("erro não previsto dentro do cliente", KeyError("usage")),
]
ENTRADAS = [
    ("caso None", None), ("caso sem `alerta`", {"id": "X", "contexto": []}), ("`alerta` string", {"alerta": "x", "contexto": []}),
    ("detalhe vazio", caso(detalhe="")), ("detalhe só espaço", caso(detalhe="   ")), ("detalhe não textual", caso(detalhe=42)),
    ("título faltando", {**caso(), "alerta": {k: v for k, v in caso()["alerta"].items() if k != "titulo"}}),
    ("fonte fora da enumeração", caso(fonte="siem")), ("ambiente fora da enumeração", caso(ambiente="producao")),
    ("contexto faltando", {**caso(), "contexto": None}), ("contexto string", {**caso(), "contexto": "janela 01:00"}),
    ("contexto com linha vazia", caso(contexto=["ok", ""])), ("contexto com item não textual", caso(contexto=[1])),
    ("detalhe acima do teto", caso(detalhe="x" * (P.TETO_CARACTERES + 1))),
    ("contexto com linhas demais", caso(contexto=["linha"] * (P.TETO_LINHAS_CONTEXTO + 1))),
]


def _e_falha(d: dict, etapa: str) -> bool:
    return (d["acao"] == "queue_tier2" and d["origem"] == "falha" and d["autoriza"] is False and d["urgencia"] is None
            and d["motivo"].startswith(f"falha operacional: {etapa} (") and all(v is None for v in d["nouls"].values()))


def _confere_falha(nome: str, jev, c, etapa: str, falhas: list) -> None:
    """Uma falha: o invólucro devolve `queue_tier2` marcado; o baixo nível levanta."""
    d = T.julgar_seguro(jev, c)
    if not _e_falha(d, etapa):
        falhas.append(f"A {nome}: julgar_seguro devolveu {d['acao']!r} / {d['origem']!r} / {d['motivo']!r}")
    try:
        T.julgar(jev, c)
        falhas.append(f"A {nome}: julgar (baixo nível) não levantou erro")
    except Exception:  # noqa: BLE001 — qualquer exceção serve: o ponto é não devolver decisão
        pass


def bateria_falhas(falhas: list) -> int:
    n = 0
    base = T.julgar_seguro(Duble(), caso())
    assert base["acao"] == "auto_close" and base["origem"] == "jev", f"o dublê válido tem de dar `auto_close`: {base}"
    for nome, corrompe in RESPOSTAS_FALSAS:
        _confere_falha(nome, Duble(corrompe(copy.deepcopy(resposta()))), caso(), "resposta inválida", falhas)
        n += 1
    for nome, inteira in RESPOSTAS_INTEIRAS:
        jev = Duble()
        jev.padrao = inteira  # direto: o construtor trocaria None pela resposta válida
        _confere_falha(nome, jev, caso(), "resposta inválida", falhas)
        n += 1
    for nome, erro in EXCECOES:
        _confere_falha(nome, Duble(erro), caso(), "chamada", falhas)
        n += 1
    for nome, c in ENTRADAS:
        _confere_falha(nome, Duble(), c, "entrada inválida", falhas)
        n += 1
        if T.baseline_seguro(c)["acao"] != "queue_tier2":
            falhas.append(f"D baseline_seguro não mandou à fila: {nome}")

    # o lote não aborta: `run.rodar` com o dublê no lugar do cliente; só os alertas com falha saem `queue_tier2`
    casos = [caso(titulo=f"t{i}") for i in range(1, 7)]
    duble = Duble(por_titulo={"t2": TimeoutError(), "t4": _mexe(["answers", "compromise_indication", "noul"], False)(resposta()),
                              "t5": resposta(compromise_indication=ALTO["compromise_indication"], critical_asset=ALTO["critical_asset"],
                                             ongoing=ALTO["ongoing"], expected_activity=BAIXO["expected_activity"])})
    jev_real, R.Jev = R.Jev, lambda pasta: duble
    try:
        saidas, custo = R.rodar(casos)
    finally:
        R.Jev = jev_real
    acoes = [s["acao"] for s in saidas]
    if acoes != ["auto_close", "queue_tier2", "auto_close", "queue_tier2", "contain_now", "auto_close"] or custo["falhas_operacionais"] != 2:
        falhas.append(f"A lote: ações {acoes}, falhas contadas {custo['falhas_operacionais']}")

    # Registro de cache forjado (revisão do Codex, 2026-10-01): `{"medicao": {}, "resposta": {}}` entrava em `chamadas` e
    # `resumo()` levantava KeyError fora do tratamento por alerta, abortando o lote. Aqui o cliente REAL (`jevcache.Jev`,
    # modo gravado, sem chave) lê uma pasta temporária com dois registros válidos e dois quebrados: só os quebrados
    # saem `queue_tier2` (origem falha), o lote continua, `resumo()` não derruba o relatório e os quebrados vão para
    # `invalidos/` da pasta temporária (nada toca `cache/`).
    casos = [caso(titulo=f"c{i}") for i in range(1, 5)]
    with tempfile.TemporaryDirectory() as pasta:
        jev = Jev(pasta, modo="gravado")
        registros = [{"medicao": {"ms": 300, "input_tokens": 2000, "modelo": "duble", "perguntas": 5}, "resposta": resposta()},
                     {"medicao": {}, "resposta": {}},
                     {"medicao": {"ms": 310, "input_tokens": 2100, "modelo": "duble", "perguntas": 5}, "resposta": resposta()},
                     {"resposta": resposta()}]
        for c, registro in zip(casos, registros):
            state, questions, _ = T.pedido(c)
            jev._arquivo(state, questions).write_text(json.dumps(registro), encoding="utf-8")
        jev_real, R.Jev = R.Jev, lambda p: jev
        try:
            saidas, custo = R.rodar(casos)
        except Exception as e:  # noqa: BLE001 — é exatamente o que não pode acontecer
            saidas, custo = [], {"falhas_operacionais": f"lote abortou: {type(e).__name__}: {e}"}
        finally:
            R.Jev = jev_real
        acoes = [s["acao"] for s in saidas]
        origens = [s["origem"] for s in saidas]
        invalidos = sorted(Path(pasta, "invalidos").glob("*.json")) if Path(pasta, "invalidos").exists() else []
        if (acoes != ["auto_close", "queue_tier2", "auto_close", "queue_tier2"] or origens != ["jev", "falha", "jev", "falha"]
                or custo["falhas_operacionais"] != 2 or custo.get("requisicoes") != 2 or custo.get("do_cache") != 2 or len(invalidos) != 2):
            falhas.append(f"A cache forjado: ações {acoes}, origens {origens}, custo {custo}, inválidos {len(invalidos)}")
    return n + 2


FATOS = {"normal": {"veto": False, "contexto_vazio": False}, "contexto vazio": {"veto": False, "contexto_vazio": True},
         "veto de horário": {"veto": True, "contexto_vazio": False}}


def bateria_politica(falhas: list) -> int:
    """Grade inteira de `politica`: 3 estados × 4 Nouls × 3 situações de fato."""
    n = 0
    for estados in itertools.product(["nao", "duvida", "sim"], repeat=4):
        valores = {q: NIVEIS[e][q] for q, e in zip(P.NOULS, estados)}
        s = {q: T._faixa(valores[q], *P.FAIXA[q]) for q in P.NOULS}
        esperado, critico, indicio, andamento = (s[q] for q in P.NOULS)
        for nome, fatos in FATOS.items():
            d = T.decidir(resposta(**valores), {**fatos, "frases": [], "dia": "", "faixas": 0, "horas": []})
            n += 1
            onde = f"{dict(zip(P.NOULS, estados))} / {nome}"
            # o veto do código derruba "esperado" ANTES da política: o conflito esperado×indício só existe sem veto
            esperado = d["esperado_efetivo"]
            if nome != "normal" and s["expected_activity"] is True and esperado is not False:
                falhas.append(f"B veto do código não derrubou o esperado: {onde}")
            if d["autoriza"] is not False or d["origem"] != "jev":
                falhas.append(f"B saída sem `autoriza: False` / origem: {onde}")
            if d["acao"] == "auto_close" and not (esperado is True and indicio is False and nome == "normal"):
                falhas.append(f"B fechou sem as condições: {onde} → {d}")
            if indicio is not False and d["acao"] in ("auto_close", "notify_owner"):
                falhas.append(f"B indício {indicio} rebaixado para {d['acao']} (esperado={esperado}): {onde}")
            if d["acao"] == "contain_now" and not (indicio is True and critico is True and andamento is True and esperado is not True):
                falhas.append(f"B conteve sem as condições: {onde}")
            if indicio is True and critico is True and andamento is True and esperado is True and d["acao"] != "queue_tier2":
                falhas.append(f"B conflito esperado×indício não foi à fila: {onde} → {d['acao']}")
            if (d["urgencia"] is None) != (d["acao"] != "notify_owner"):
                falhas.append(f"B urgência só em notify_owner: {onde} → {d['acao']} / {d['urgencia']}")
            if esperado is not True and d["acao"] != T.precedencia(esperado, critico, indicio, andamento):
                falhas.append(f"B sem veto nem conflito a ação devia ser a precedência: {onde}")
            if nome != "normal" and s["expected_activity"] is True and indicio is False and (d["acao"] != "notify_owner" or not d["veto"]):
                falhas.append(f"B veto do código não segurou o fechamento: {onde} → {d['acao']}")
            if d["acao"] == "notify_owner" and d["urgencia"] != ("acordar" if critico is not False and andamento is not False else "manha"):
                falhas.append(f"B urgência errada: {onde} → {d['urgencia']}")
    # a precedência do LEIA-ME, nos 81 estados possíveis
    for estados in itertools.product([True, False, None], repeat=4):
        a = T.precedencia(*estados)
        esperado, critico, indicio, andamento = estados
        certo = ("contain_now" if (indicio, critico, andamento) == (True, True, True) else "queue_tier2" if indicio is not False
                 else "auto_close" if esperado is True else "notify_owner")
        n += 1
        if a != certo:
            falhas.append(f"B precedência {estados}: {a} (esperado {certo})")
    return n


def bateria_tempo(falhas: list) -> int:
    dt = lambda m, d, h, mi: datetime.datetime(P.ANO_DOS_DADOS, m, d, h, mi)  # noqa: E731
    casos_horas = [
        ("hora após o meio-dia é da véspera; antes, do dia", "CPU alta desde 21:40; às 03:10 continua", [dt(9, 30, 21, 40), dt(10, 1, 3, 10)]),
        ("data explícita manda", "30/09 19:12 exportou. Encerrada às 19:15.", [dt(9, 30, 19, 12), dt(9, 30, 19, 15)]),
        ("data explícita e hora que vira o dia", "30/09 23:50 começou; 00:10 terminou.", [dt(9, 30, 23, 50), dt(10, 1, 0, 10)]),
        ("IP, porta, contagem e duração não são hora", "10.0.0.0/24 porta 5432; 1.900 req; 3 h 50 min; 2,4 vezes", []),
        ("hora com segundos e dois-pontos de pontuação", "01:02:30 a 01:17: 212 requisições", [dt(10, 1, 1, 2), dt(10, 1, 1, 17)]),
        ("hora inválida não casa", "às 25:70 nada; 24:00 nada", []),
    ]
    n = 0
    for nome, detalhe, esperado in casos_horas:
        n += 1
        if T.horas_do_alerta(detalhe) != esperado:
            falhas.append(f"C horas: {nome}: {T.horas_do_alerta(detalhe)}")
    casos_faixas = [
        ("faixa com data nas duas pontas", "Janela: 30/09 22:00 a 01/10 06:00.", 1),
        ("faixa com data e 'às' nas duas pontas (Codex)", "Janela: 28/09 às 22:00 a 29/09 às 06:00.", 1),
        ("faixa com data antes de 'das'", "MUD-1: 01/10 das 01:00 às 03:00.", 1),
        ("faixa sem data", "Varredura semanal das 02:00 às 04:00.", 1),
        ("'entre X e Y'", "svc-x lê entre 01:00 e 05:00, todo dia.", 1),
        ("traço", "Plantão 22:00-06:00.", 1),
        ("hora solta não é faixa", "Deploy às 02:09 pelo pipeline.", 0),
        ("'às X e Y' sem 'entre' não é faixa", "Reiniciou às 02:09 e 02:40.", 0),
        ("duas faixas na mesma linha", "Lotes das 01:00 às 02:00 e das 04:00 às 05:00.", 2),
    ]
    for nome, linha, quantas in casos_faixas:
        n += 1
        if len(T.faixas_do_contexto(linha)) != quantas:
            falhas.append(f"C faixas: {nome}: {T.faixas_do_contexto(linha)}")
    # As datas das duas pontas têm de ficar guardadas (revisão do Codex: "28/09 às 22:00" perdia a 28/09).
    casos_datas = [
        ("data colada com 'às' nas duas pontas", "Janela: 28/09 às 22:00 a 29/09 às 06:00.", (9, 28), (9, 29)),
        ("data colada com 'às' e 'até'", "Janela: 30/09 às 22:00 até 01/10 às 06:00.", (9, 30), (10, 1)),
        ("data só na 2ª ponta fica registrada como tal", "Janela 22:00 a 29/09 06:00.", None, (9, 29)),
        ("data antes de 'das' vale para a 1ª ponta", "MUD-1: 01/10 das 01:00 às 03:00.", (10, 1), None),
    ]
    for nome, linha, d1, d2 in casos_datas:
        n += 1
        fx = T.faixas_do_contexto(linha)
        if len(fx) != 1 or fx[0]["d1"] != d1 or fx[0]["d2"] != d2:
            falhas.append(f"C datas: {nome}: {fx}")
    casos_veto = [
        ("dentro da faixa com data", "01:40 atraso de replicação.", ["Janela: 01/10 das 01:00 às 03:00."], False),
        ("fora da faixa com data (depois do fim)", "04:42 reiniciou. Voltou às 04:44.", ["Janela: 01/10 das 01:00 às 03:00."], True),
        ("fora por causa da DATA (mesma hora, outro dia)", "02:30 rajada.", ["Janela: 28/09 22:00 a 29/09 06:00."], True),
        # Família do Codex: janela vencida de dois dias, data só na ponta final, data inválida — nenhuma vira janela
        # diária; o veto segue valendo e o fato dentro/fora fica ausente.
        ("janela vencida de dois dias com 'às' nas duas pontas (Codex)", "02:30 rajada.", ["Janela: 28/09 às 22:00 a 29/09 às 06:00."], True),
        ("janela vencida com 'às', hora de ontem à noite também fora", "23:10 rajada; 02:30 continua.", ["Janela: 28/09 às 22:00 a 29/09 às 06:00."], True),
        ("só data final: não compara, veto mantido", "02:30 rajada.", ["Janela 22:00 a 29/09 06:00."], True),
        ("só data final, mesmo com a hora na faixa diária", "02:30 rajada.", ["Janela 22:00 a 01/10 06:00."], True),
        ("data inválida (31/02) na 1ª ponta: não compara, veto mantido", "02:30 rajada.", ["Janela: 31/02 22:00 a 01/03 06:00."], True),
        ("data inválida na 2ª ponta: não compara, veto mantido", "02:30 rajada.", ["Janela: 30/09 22:00 a 31/02 06:00."], True),
        ("faixa com data que cruza a meia-noite, hora dentro", "02:30 rajada.", ["Janela: 30/09 às 22:00 a 01/10 às 06:00."], False),
        ("faixa com data que cruza a meia-noite, hora da véspera dentro", "23:10 rajada; 02:30 continua.", ["Janela: 30/09 às 22:00 a 01/10 às 06:00."], False),
        ("data só na 1ª ponta cruzando a meia-noite (fim herda e vira o dia)", "02:30 rajada.", ["Janela: 30/09 das 22:00 às 06:00."], False),
        ("faixa não comparável ao lado de uma que cobre: a boa decide", "02:30 rajada.", ["Janela 22:00 a 29/09 06:00.", "Varredura das 02:00 às 04:00."], False),
        ("faixa sem data que atravessa a meia-noite", "23:40 login; 00:03 token.", ["Acesso permitido entre 22:00 e 07:00."], False),
        ("faixa sem data, hora fora", "07:40 payloads.", ["Teste das 22:00 às 06:00."], True),
        ("parte dentro, parte fora = veto", "22:10 começou; 03:00 continua.", ["Janela das 23:00 às 01:00."], True),
        ("duas faixas, uma cobre tudo", "02:30 pico.", ["Lote das 01:00 às 02:00.", "Varredura das 02:00 às 04:00."], False),
        ("sem faixa no contexto não veta", "02:30 pico.", ["Deploy às 02:09."], False),
        ("sem hora no alerta não veta", "Disco em 95%.", ["Janela das 01:00 às 03:00."], False),
        ("contexto vazio", "02:30 pico.", [], False),
    ]
    for nome, detalhe, contexto, veto in casos_veto:
        n += 1
        f = T.fatos_de_tempo(detalhe, contexto)
        if f["veto"] is not veto or f["contexto_vazio"] is not (not contexto):
            falhas.append(f"C veto: {nome}: {f}")
    f = T.fatos_de_tempo("02:30 pico.", ["Janela das 01:00 às 03:00."])
    n += 1
    if "INSIDE" not in f["frases"][0] or "Thursday" not in f["dia"] or "2026-10-01" not in f["dia"]:
        falhas.append(f"C frase/dia: {f}")
    # Faixa não comparável: sem fato INSIDE/OUTSIDE no state (o Jev lê o texto como antes), mas contada como faixa.
    f = T.fatos_de_tempo("02:30 pico.", ["Janela: 31/02 22:00 a 01/03 06:00."])
    n += 1
    if f["faixas"] != 1 or any(p in f["frases"][0] for p in ("INSIDE", "OUTSIDE")) or "could not be compared" not in f["frases"][0]:
        falhas.append(f"C faixa não comparável: {f}")
    st = T.state_de(caso(), f)
    n += 1
    if set(st) != {"alert", "context", "computed_by_code"} or st["alert"]["source"] != "monitoring" or st["alert"]["environment"] != "prod" \
            or "computed_by_code" in T.state_de(caso(), f, com_fatos=False):
        falhas.append(f"C state: {st}")
    return n


def bateria_erros_caros(falhas: list) -> int:
    g = lambda acao, esp, crit, ind, and_: {"acao": acao, "sinais": {"atividade_esperada": esp, "ativo_critico": crit,  # noqa: E731
                                                                     "indicio_de_comprometimento": ind, "em_andamento": and_}}
    ataque, esperado, nulo = g("contain_now", False, True, True, True), g("auto_close", True, True, False, True), g("queue_tier2", False, True, None, True)
    esperados = [
        (("auto_close", ataque), ["E1", "E2"]), (("notify_owner", ataque), ["E1"]), (("queue_tier2", ataque), []), (("contain_now", ataque), []),
        (("contain_now", esperado), ["E3"]), (("auto_close", esperado), []), (("notify_owner", esperado), []),
        (("auto_close", nulo), ["E2"]), (("contain_now", nulo), []), (("queue_tier2", nulo), []),
    ]
    for (acao, c), caros in esperados:
        if R.erros_caros(acao, c) != caros:
            falhas.append(f"D erros_caros({acao}, {c['acao']}): {R.erros_caros(acao, c)} (esperado {caros})")
    return len(esperados)


def main() -> None:
    falhas: list[str] = []
    a, b, c, d = bateria_falhas(falhas), bateria_politica(falhas), bateria_tempo(falhas), bateria_erros_caros(falhas)
    if falhas:
        sys.exit(f"FALHOU ({len(falhas)}):\n  " + "\n  ".join(falhas[:40]) + ("\n  …" if len(falhas) > 40 else ""))
    print(f"ok: A {a} falhas operacionais → `queue_tier2` (origem falha) por alerta (nenhuma `auto_close`; lote não aborta; "
          f"baixo nível levanta) · B {b} combinações de `politica`/`precedencia` (indício nunca rebaixado por texto; fechamento só com "
          f"duas leituras e sem veto; `autoriza: False`) · C {c} conferências dos fatos de tempo · D {d} de erros caros")


if __name__ == "__main__":
    main()
