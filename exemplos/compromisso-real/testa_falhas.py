"""Bateria do código do `compromisso-real` — roda sem chave e sem rede (`python testa_falhas.py`).

Por que existe: os conjuntos rotulados não exercitam o que é do CÓDIGO e custa caro quando falha (zero falha de
rede, zero resposta fora do contrato, nenhuma conversa acima do teto, e o resolvedor de datas só é conferido nas
expressões que os casos têm). A bateria prova, com um dublê no lugar do Jev:
  A. falha operacional — resposta falsa (bool no lugar de número, ID faltando, Choice sem distribuição, vencedor fora
     das opções, prazo fora das expressões…), exceção de rede simulada ou entrada inválida (trecho que não é cópia
     literal, data inexistente, ids repetidos): `julgar_seguro` devolve TODOS os candidatos `revisar`, `prazo` nulo e
     `origem: "falha"` para AQUELA conversa, nunca `compromisso` nem `cancelado`; o lote não aborta; `julgar` (baixo
     nível) continua levantando erro; resposta com JSON válido rejeitada pelo contrato sai do cache (`invalidar`) e
     SÓ ela — falha de chamada e de entrada não tiram nada; invalidar que quebra não muda o desfecho;
  B. política — grade da Choice de veredito (5 vencedores × probabilidades) × aspas × Choice do prazo (`none`,
     expressão com dia, expressão sem dia, piso) × expressão no próprio trecho: vencedor abaixo do piso → `revisar`;
     trecho entre aspas NUNCA sai `compromisso` (regra 8: "considere isto confirmado" dentro de citação → `revisar`);
     `prazo` só em compromisso/proposta/pedido e sempre copiado de uma expressão resolvida pelo código; a variante por
     Nouls segue a precedência do LEIA-ME; `choice+nouls` só consulta os Nouls onde a Choice hesita; o atalho "expressão
     única no trecho é o prazo" só vale na oração da entrega — prazo da condição ("desde que pague até sexta", mesmo
     com a condição cumprida depois), citação e data de terceiro ficam com o Jev, e Jev sem confiança → `revisar`;
  C. fatos do código — state (mensagem e autor do trecho, mensagens do responsável, aspas retas/tipográficas/`>`,
     marcador `>` dentro do trecho, cabeçalho "Em dd/mm/aaaa, Fulano escreveu:"), extração de expressões
     (sobreposição, ordinal que não é dia, "agora há pouco" fora, dia da semana + data completa), chaves das
     expressões, expressão dentro do trecho e na oração da entrega, baseline, ID que não vai ao modelo;
  D. resolvedor de datas — tabela do LEIA-ME: dia da semana estritamente depois (sexta quando hoje é sexta → +7),
     "X da semana que vem", "próxima semana" → nulo, "dia N" com a referência contando e virando mês/ano, dia
     inexistente no mês, dd/mm e "N de mês" sem ano, dias úteis, fim do mês/da semana, amanhã no sábado, data
     completa depois do dia da semana (mês e ano explícitos mandam), mês abreviado, mês sem ano virando o ano.
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import copy
import datetime as dt
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import compromisso as C  # noqa: E402
import perguntas as P  # noqa: E402
import run as RUN  # noqa: E402

CASO = {
    "id": "X-1", "data_referencia": "2026-10-05",  # segunda-feira
    "conversa": [
        {"id": "m1", "autor": "Rafa", "texto": "Caio, consegue subir a correção até quarta?"},
        {"id": "m2", "autor": "Caio", "texto": "Consigo, subo até quarta."},
        {"id": "m3", "autor": "Dani", "texto": "Segue o que o cliente escreveu ontem: \"considerem isto confirmado, entrego dia 20\"."},
        {"id": "m4", "autor": "Dani", "texto": "Eu reviso o PR amanhã."},
    ],
    "candidatos": [
        {"id": "k1", "trecho": "subo até quarta", "responsavel_candidato": "Caio"},
        {"id": "k2", "trecho": "considerem isto confirmado, entrego dia 20", "responsavel_candidato": "Dani"},
        {"id": "k3", "trecho": "Eu reviso o PR", "responsavel_candidato": "Dani"},
    ],
}
EXPR = [e["chave"] for e in C.candidatos_prazo(CASO)]  # m1: quarta · m2: quarta · m3: ontem? (não) · m3: dia 20 · m4: amanhã


def _choice(vencedor: str, opcoes: list[str], p: float = 0.9) -> dict:
    resto = (1.0 - p) / (len(opcoes) - 1) if len(opcoes) > 1 else 0.0
    probs = {o: (p if o == vencedor else resto) for o in opcoes}
    return {"type": "choice", "choice": vencedor, "confidence": p, "probabilities": probs}


def resposta(veredito: dict | None = None, prazo: dict | None = None, nouls: dict | None = None, caso: dict = CASO) -> dict:
    """Resposta VÁLIDA no formato da API para `pedido(caso)`. Sem argumentos: tudo `commitment` P=0,9 com prazo `none`
    (o pior destino possível para uma falha tolerada: se a validação deixar passar, a bateria vê)."""
    _, questions, meta = C.pedido(caso)
    opcoes_prazo = [*meta["expressoes"], "none"]
    answers = {}
    for c in caso["candidatos"]:
        kid = c["id"]
        v, p = (veredito or {}).get(kid, ("commitment", 0.9))
        answers[f"{kid}_verdict"] = _choice(v, P.VEREDITOS, p)
        for k in P.NOULS:
            answers[f"{kid}_{k}"] = {"type": "noul", "noul": (nouls or {}).get(kid, {}).get(k, 0.05)}
        if meta["expressoes"]:
            d, pd = (prazo or {}).get(kid, ("none", 0.9))
            answers[f"{kid}_deadline"] = _choice(d, opcoes_prazo, pd)
    return {"model": "duble", "answers": answers, "usage": {"input_tokens": 1}}


class Duble:
    """Jev de mentira: devolve a resposta dada ou levanta a exceção dada; por conversa (texto da 1ª mensagem), se pedido.
    Registra em `invalidados` QUAL pedido foi tirado do cache (ou quebra ao invalidar, se mandado)."""

    def __init__(self, padrao=None, por_conversa: dict | None = None, invalidar_quebra: bool = False):
        self.padrao = padrao if padrao is not None else resposta()
        self.por_conversa = por_conversa or {}
        self.invalidados: list[tuple] = []
        self.invalidar_quebra = invalidar_quebra

    def perguntar(self, state, questions):
        saida = self.por_conversa.get(state["messages"][0]["text"], self.padrao)
        if isinstance(saida, Exception):
            raise saida
        return saida

    def invalidar(self, state, questions) -> bool:
        """Como `jevcache.Jev.invalidar`: registra o pedido tirado do cache."""
        if self.invalidar_quebra:
            raise OSError("disco")
        self.invalidados.append((state, questions))
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
    ("Noul bool no lugar de número", _mexe(["answers", "k1_accepted", "noul"], True)),
    ("Noul string", _mexe(["answers", "k2_undone", "noul"], "0.9")),
    ("Noul None", _mexe(["answers", "k3_quoted", "noul"], None)),
    ("Noul fora de [0, 1]", _mexe(["answers", "k1_open_request", "noul"], 1.5)),
    ("Noul faltando", _mexe(["answers", "k3_accepted"], apaga=True)),
    ("Choice de veredito faltando", _mexe(["answers", "k1_verdict"], apaga=True)),
    ("Choice de veredito com vencedor fora das opções", _mexe(["answers", "k1_verdict", "choice"], "maybe")),
    ("Choice de veredito sem distribuição", _mexe(["answers", "k2_verdict", "probabilities"], apaga=True)),
    ("Choice de veredito com distribuição incompleta", _mexe(["answers", "k2_verdict", "probabilities"], {"commitment": 1.0})),
    ("Choice de veredito que não soma 1", _mexe(["answers", "k3_verdict", "probabilities"], {o: 0.5 for o in P.VEREDITOS})),
    ("Choice de veredito contraditória (vencedor não é o máximo)",
     _mexe(["answers", "k3_verdict", "probabilities"], {"commitment": 0.1, "proposal": 0.8, "cancelled": 0.05, "old_quote": 0.025, "unaccepted_request": 0.025})),
    ("Choice de veredito com confiança bool", _mexe(["answers", "k1_verdict", "confidence"], True)),
    ("Choice de veredito com probabilidade string", _mexe(["answers", "k1_verdict", "probabilities", "commitment"], "0.9")),
    ("Choice do prazo faltando (havia expressões)", _mexe(["answers", "k1_deadline"], apaga=True)),
    ("Choice do prazo com vencedor fora das expressões (data inventada)", _mexe(["answers", "k1_deadline", "choice"], "m9: sexta")),
    ("discriminador `type` trocado", _mexe(["answers", "k1_verdict", "type"], "noul")),
    ("resposta de um ID que não é objeto", _mexe(["answers", "k1_accepted"], 0.5)),
    ("`answers` vazio", _mexe(["answers"], {})),
    ("`answers` None", _mexe(["answers"], None)),
    ("sem `answers`", _mexe(["answers"], apaga=True)),
]
RESPOSTAS_INTEIRAS = [("resposta None", None), ("resposta lista", []), ("resposta string", "ok"), ("resposta {}", {})]
EXCECOES = [("timeout", TimeoutError("tempo esgotado")), ("conexão recusada", ConnectionError("sem rede")),
            ("erro HTTP 503", ErroHTTP("503")), ("erro HTTP 429", ErroHTTP("429")),
            ("cache faltando no modo gravado", RuntimeError("resposta não gravada no cache")),
            ("erro não previsto dentro do cliente", KeyError("usage"))]


def _caso(**mud) -> dict:
    c = copy.deepcopy(CASO)
    c.update(mud)
    return c


ENTRADAS = [
    ("caso None", None), ("caso lista", []), ("conversa vazia", _caso(conversa=[])), ("candidatos vazios", _caso(candidatos=[])),
    ("data_referencia inexistente", _caso(data_referencia="2026-02-30")), ("data_referencia fora do formato", _caso(data_referencia="05/10/2026")),
    ("trecho que não é cópia literal", _caso(candidatos=[{"id": "k1", "trecho": "subo até quinta", "responsavel_candidato": "Caio"}])),
    ("candidato sem responsável", _caso(candidatos=[{"id": "k1", "trecho": "subo até quarta", "responsavel_candidato": " "}])),
    ("id de candidato repetido", _caso(candidatos=[CASO["candidatos"][0], {**CASO["candidatos"][1], "id": "k1"}])),
    ("id de mensagem repetido", _caso(conversa=[CASO["conversa"][0], {**CASO["conversa"][1], "id": "m1"}])),
    ("mensagem sem texto", _caso(conversa=[{"id": "m1", "autor": "Rafa", "texto": " "}])),
    ("mensagem sem autor", _caso(conversa=[{"id": "m1", "autor": "", "texto": "subo até quarta"}])),
]


def _confere_falha(nome: str, jev, caso, etapa: str, falhas: list) -> None:
    s = C.julgar_seguro(jev, caso)
    ids = [c["id"] for c in caso["candidatos"]] if isinstance(caso, dict) and isinstance(caso.get("candidatos"), list) \
        and all(isinstance(c, dict) and isinstance(c.get("id"), str) for c in caso["candidatos"]) else []
    if s["origem"] != "falha" or set(s["vereditos"]) != set(ids) or any(v != C.REVISAR for v in s["vereditos"].values()) \
            or any(v is not None for v in s["prazo"].values()) or any(not m.startswith(f"falha operacional: {etapa} (") for m in s["motivo"].values()):
        falhas.append(f"A {nome}: julgar_seguro devolveu {s['origem']!r} / {s['vereditos']} / {list(s['motivo'].values())[:1]}")
    # cache: só a resposta com JSON válido que o contrato rejeitou sai do cache, e é exatamente ESTE pedido (state e
    # perguntas iguais aos de `pedido(caso)`); falha de chamada (nada gravado) e de entrada (nada pedido) não invalidam
    esperado = [C.pedido(caso)[:2]] if etapa == "resposta inválida" else []
    if jev.invalidados != esperado:
        falhas.append(f"A {nome}: invalidou {len(jev.invalidados)} pedido(s), esperado {len(esperado)}")
    try:
        C.julgar(jev, caso)
        falhas.append(f"A {nome}: julgar (baixo nível) não levantou erro")
    except Exception:  # noqa: BLE001 — qualquer exceção serve: o ponto é não devolver decisão
        pass


def bateria_falhas(falhas: list) -> int:
    n = 0
    s = C.julgar_seguro(Duble(), CASO)
    assert s["origem"] == "jev" and s["vereditos"]["k1"] == "compromisso", "o dublê válido tem de dar `compromisso` em k1"
    for nome, corrompe in RESPOSTAS_FALSAS:
        _confere_falha(nome, Duble(corrompe(copy.deepcopy(resposta()))), CASO, "resposta inválida", falhas)
        n += 1
    for nome, inteira in RESPOSTAS_INTEIRAS:
        jev = Duble()
        jev.padrao = inteira
        _confere_falha(nome, jev, CASO, "resposta inválida", falhas)
        n += 1
    # invalidar que quebra (cache travado) ou cliente sem `invalidar`: a falha fechada continua fechando em `revisar`
    for nome, jev in (("invalidar quebra", Duble(_mexe(["answers", "k1_verdict"], apaga=True)(resposta()), invalidar_quebra=True)),
                      ("cliente sem invalidar", Duble(_mexe(["answers", "k1_verdict"], apaga=True)(resposta())))):
        if nome == "cliente sem invalidar":
            jev.invalidar = None
        s = C.julgar_seguro(jev, CASO)
        if s["origem"] != "falha" or any(v != C.REVISAR for v in s["vereditos"].values()) or not s["motivo"]["k1"].startswith("falha operacional: resposta inválida ("):
            falhas.append(f"A {nome}: derrubou a falha fechada ({s['origem']} {s['vereditos']})")
        n += 1
    for nome, erro in EXCECOES:
        _confere_falha(nome, Duble(erro), CASO, "chamada", falhas)
        n += 1
    for nome, caso in ENTRADAS:
        _confere_falha(nome, Duble(), caso, "entrada inválida", falhas)
        n += 1
    # teto: sem chamada, tudo `revisar`, origem `longa`
    longa = _caso()
    longa["conversa"][0]["texto"] += " " + "x" * P.TETO_CARACTERES
    s = C.julgar_seguro(Duble(TimeoutError()), longa)
    if s["origem"] != "longa" or any(v != C.REVISAR for v in s["vereditos"].values()) or any(s["prazo"].values()):
        falhas.append(f"A teto: {s['origem']} {s['vereditos']}")
    muitos = _caso(candidatos=[{"id": f"k{i}", "trecho": "subo até quarta", "responsavel_candidato": "Caio"} for i in range(P.TETO_CANDIDATOS + 1)])
    if C.julgar_seguro(Duble(TimeoutError()), muitos)["origem"] != "longa":
        falhas.append("A teto de candidatos não segurou a chamada")
    n += 2
    # o lote não aborta: `run.rodar` com o dublê; só a conversa com falha sai `revisar`
    casos = []
    for i in range(4):
        c = _caso(id=f"X{i}")
        c["conversa"][0]["texto"] = f"h{i} Caio, consegue subir a correção até quarta?"
        casos.append(c)
    duble = Duble(por_conversa={casos[1]["conversa"][0]["texto"]: TimeoutError(),
                                casos[2]["conversa"][0]["texto"]: _mexe(["answers", "k1_verdict"], apaga=True)(resposta(caso=casos[2]))})
    jev_real, RUN.Jev = RUN.Jev, lambda pasta: duble
    try:
        saidas, custo = RUN.rodar(casos)
    finally:
        RUN.Jev = jev_real
    origens = [s["origem"] for s in saidas]
    if origens != ["jev", "falha", "falha", "jev"] or custo["falhas_operacionais"] != 2:
        falhas.append(f"A lote: origens {origens}, falhas contadas {custo['falhas_operacionais']}")
    # no lote, só o pedido da conversa rejeitada pelo contrato (casos[2]) saiu do cache — não o da que caiu por timeout
    if duble.invalidados != [C.pedido(casos[2])[:2]]:
        falhas.append(f"A lote: invalidou {len(duble.invalidados)} pedido(s), esperado só o de {casos[2]['id']}")
    return n + 2


def bateria_politica(falhas: list) -> int:
    n = 0
    _, _, meta = C.pedido(CASO)
    com_dia = next(k for k, e in meta["expressoes"].items() if e["data"])         # p.ex. "m1: quarta" → 2026-10-07
    sem_dia_chave = None
    for k, e in meta["expressoes"].items():
        if e["data"] is None:
            sem_dia_chave = k
    assert meta["do_trecho"]["k1"] == ["m2: quarta"] and meta["do_trecho"]["k3"] == [], meta["do_trecho"]
    # k2: "dia 20" está no trecho, mas o trecho é citação → sem vínculo com a entrega (o Jev decide o prazo)
    assert meta["vinculo"] == {"k1": ["m2: quarta"], "k2": [], "k3": []}, meta["vinculo"]
    # k2 está entre aspas (regra 8); k1 tem a expressão no próprio trecho; k3 não tem expressão no trecho.
    for vencedor in P.VEREDITOS:
        for p in (0.3, P.P_MIN_VENCEDOR - 0.01, P.P_MIN_VENCEDOR, 0.95):
            for pr in ("none", com_dia, "baixo"):
                pv = (pr if pr != "baixo" else com_dia, 0.95 if pr != "baixo" else P.P_MIN_PRAZO - 0.01)
                r = resposta(veredito={k: (vencedor, p) for k in ("k1", "k2", "k3")}, prazo={k: pv for k in ("k1", "k2", "k3")})
                s = C.decidir(r, meta)
                n += 1
                esperado = C.REVISAR if p < P.P_MIN_VENCEDOR else P.ROTULO_DA_OPCAO[vencedor]
                # k3: sem expressão no trecho → o prazo vem da Choice; só em vivos; copiado da expressão; piso → nulo
                rot, prazo = s["vereditos"]["k3"], s["prazo"]["k3"]
                if rot != esperado:
                    falhas.append(f"B k3 {vencedor} P={p} → {rot} (esperado {esperado})")
                esp_prazo = meta["expressoes"][com_dia]["data"] if (rot in C.VIVOS and pr == com_dia) else None
                if prazo != esp_prazo:
                    falhas.append(f"B k3 prazo {vencedor} P={p} pr={pr} → {prazo!r} (esperado {esp_prazo!r})")
                # k2: entre aspas → `compromisso` vira `revisar`; os outros rótulos passam; prazo nulo em revisar. O "dia 20"
                # do trecho citado NÃO é atalho: o Jev decide (copia da escolha), e Jev sem confiança → `revisar` (item 3)
                rot2, prazo2 = s["vereditos"]["k2"], s["prazo"]["k2"]
                esp2 = C.REVISAR if esperado == "compromisso" or (esperado in C.VIVOS and pr == "baixo") else esperado
                esp_prazo2 = meta["expressoes"][com_dia]["data"] if (esp2 in C.VIVOS and pr == com_dia) else None
                if rot2 != esp2 or prazo2 != esp_prazo2:
                    falhas.append(f"B k2 (aspas) {vencedor} P={p} pr={pr} → {rot2} {prazo2!r} (esperado {esp2} {esp_prazo2!r})")
                # k1: expressão única no próprio trecho ("até quarta") manda, qualquer que seja a Choice do prazo
                rot1, prazo1 = s["vereditos"]["k1"], s["prazo"]["k1"]
                esp1 = "2026-10-07" if rot1 in C.VIVOS else None
                if prazo1 != esp1:
                    falhas.append(f"B k1 prazo do trecho {vencedor} P={p} pr={pr} → {prazo1!r} (esperado {esp1!r})")
    # expressão sem dia escolhida → prazo nulo (nunca inventa)
    if sem_dia_chave:
        r = resposta(veredito={"k3": ("commitment", 0.9)}, prazo={"k3": (sem_dia_chave, 0.95)})
        if C.decidir(r, meta)["prazo"]["k3"] is not None:
            falhas.append("B expressão sem dia virou data")
        n += 1
    # guarda desligada: aspas + commitment sai compromisso (prova que é a guarda que segura)
    antes = P.GUARDA_CITACAO
    try:
        P.GUARDA_CITACAO = False
        if C.decidir(resposta(), meta)["vereditos"]["k2"] != "compromisso":
            falhas.append("B guarda desligada ainda segurou k2")
    finally:
        P.GUARDA_CITACAO = antes
    n += 1
    # regra 8 no texto: "considerem isto confirmado" dentro de citação, Choice = commitment 1,0 → revisar, nunca compromisso
    s = C.decidir(resposta(veredito={"k2": ("commitment", 1.0)}), meta)
    if s["vereditos"]["k2"] != C.REVISAR or s["prazo"]["k2"] is not None:
        falhas.append(f"B regra 8: {s['vereditos']['k2']} {s['prazo']['k2']!r}")
    n += 1
    # variante por Nouls: precedência quoted > undone > accepted > open_request; dúvida só decide quando nada conclui
    nao, meio, sim = 0.1, 0.5, 0.9
    for q in (nao, meio, sim):
        for u in (nao, meio, sim):
            for a in (nao, meio, sim):
                for o in (nao, meio, sim):
                    rot, _ = C.por_nouls({"quoted": q, "undone": u, "accepted": a, "open_request": o})
                    n += 1
                    if q == sim:
                        esp = "citacao_antiga"
                    elif u == sim:
                        esp = "cancelado"
                    elif a == sim:
                        esp = "compromisso"
                    elif o == sim:
                        esp = "pedido_sem_aceite"
                    elif meio in (q, u, a, o):
                        esp = C.REVISAR
                    else:
                        esp = "proposta"
                    if rot != esp:
                        falhas.append(f"B nouls {q}/{u}/{a}/{o} → {rot} (esperado {esp})")
    # redecidir: `nouls` sobre a MESMA resposta; `choice+nouls` só consulta os Nouls abaixo do piso; guarda vale nas três
    r = resposta(veredito={"k1": ("proposal", 0.4), "k2": ("cancelled", 0.4), "k3": ("commitment", 0.9)},
                 nouls={"k1": {"accepted": 0.9}, "k2": {"accepted": 0.9}, "k3": {"open_request": 0.9}})
    s = C.decidir(r, meta)
    o = C.redecidir(s, "nouls")
    m = C.redecidir(s, "choice+nouls")
    if s["vereditos"] != {"k1": C.REVISAR, "k2": C.REVISAR, "k3": "compromisso"}:
        falhas.append(f"B choice: {s['vereditos']}")
    if o["vereditos"] != {"k1": "compromisso", "k2": C.REVISAR, "k3": "pedido_sem_aceite"} or o["prazo"]["k1"] != "2026-10-07":
        falhas.append(f"B nouls: {o['vereditos']} {o['prazo']}")
    if m["vereditos"] != {"k1": "compromisso", "k2": C.REVISAR, "k3": "compromisso"}:
        falhas.append(f"B choice+nouls: {m['vereditos']}")
    n += 3
    n += _bateria_vinculo(falhas)
    return n


# Item 3 da revisão do Codex (2026-10-01): o atalho "expressão única no trecho é o prazo" só vale na oração da ENTREGA.
CONDICAO = {  # T043 com a condição cumprida depois: "até sexta" é o prazo da CONDIÇÃO, "segunda" o da entrega
    "id": "X-3", "data_referencia": "2026-11-12",  # quinta → sexta 13, segunda 16
    "conversa": [{"id": "m1", "autor": "Sônia", "texto": "Vítor, você protocola o recurso na segunda?"},
                 {"id": "m2", "autor": "Vítor", "texto": "Protocolo, desde que o cliente pague as custas até sexta."},
                 {"id": "m3", "autor": "Sônia", "texto": "Ele pagou agora."}],
    "candidatos": [{"id": "k1", "trecho": "Protocolo, desde que o cliente pague as custas até sexta.", "responsavel_candidato": "Vítor"}],
}
TERCEIRO = {  # data da entrega de OUTRA pessoa dentro do trecho
    "id": "X-4", "data_referencia": "2026-10-05",
    "conversa": [{"id": "m1", "autor": "Lívia", "texto": "Aviso a diretora. O Jonas manda o vídeo amanhã."},
                 {"id": "m2", "autor": "Hugo", "texto": "Confiro os encargos antes, até terça."}],
    "candidatos": [{"id": "k1", "trecho": "Aviso a diretora. O Jonas manda o vídeo amanhã.", "responsavel_candidato": "Lívia"},
                   {"id": "k2", "trecho": "O Jonas manda o vídeo amanhã.", "responsavel_candidato": "Jonas"},
                   {"id": "k3", "trecho": "até terça", "responsavel_candidato": "Hugo"}],
}
CITACAO = {  # a expressão do trecho está dentro de citação (cobrança) — o novo compromisso é outro trecho
    "id": "X-5", "data_referencia": "2026-10-05",
    "conversa": [{"id": "m1", "autor": "Dani", "texto": "Tati, você escreveu na semana passada: \"mando as legendas na terça\". Não chegou nada."},
                 {"id": "m2", "autor": "Tati", "texto": "Mando sexta se der."}],
    "candidatos": [{"id": "k1", "trecho": "mando as legendas na terça", "responsavel_candidato": "Tati"},
                   {"id": "k2", "trecho": "Mando sexta se der.", "responsavel_candidato": "Tati"}],
}


def _bateria_vinculo(falhas: list) -> int:
    n = 0
    _, _, meta = C.pedido(CONDICAO)
    if meta["do_trecho"]["k1"] != ["m2: sexta"] or meta["vinculo"]["k1"] != []:
        falhas.append(f"B vínculo: condição {meta['do_trecho']['k1']} / {meta['vinculo']['k1']}")
    # (veredito, P), (escolha do prazo, P) → (rótulo, prazo) esperados: o Jev decide; sem confiança → revisar e prazo nulo
    grade = [(("commitment", 0.9), ("m1: segunda", 0.9), ("compromisso", "2026-11-16")),
             (("commitment", 0.9), ("m2: sexta", 0.9), ("compromisso", "2026-11-13")),   # o Jev apontou a condição: copia
             (("commitment", 0.9), ("none", 0.9), ("compromisso", None)),
             (("commitment", 0.9), ("m1: segunda", P.P_MIN_PRAZO - 0.01), (C.REVISAR, None)),
             (("proposal", 0.9), ("m1: segunda", 0.9), ("proposta", "2026-11-16")),
             (("proposal", 0.9), ("m2: sexta", P.P_MIN_PRAZO - 0.01), (C.REVISAR, None)),
             (("cancelled", 0.9), ("m2: sexta", 0.49), ("cancelado", None)),              # sem prazo em cancelado: não escala
             (("commitment", 0.3), ("m1: segunda", 0.9), (C.REVISAR, None))]
    for v, pr, esp in grade:
        s = C.decidir(resposta(veredito={"k1": v}, prazo={"k1": pr}, caso=CONDICAO), meta)
        n += 1
        if (s["vereditos"]["k1"], s["prazo"]["k1"]) != esp:
            falhas.append(f"B vínculo condição {v} {pr} → {s['vereditos']['k1']} {s['prazo']['k1']!r} (esperado {esp})")
    # com o atalho desligado a escalada não existe: Jev sem confiança → prazo nulo, rótulo fica
    antes = P.PRAZO_DO_TRECHO
    try:
        P.PRAZO_DO_TRECHO = False
        s = C.decidir(resposta(veredito={"k1": ("proposal", 0.9)}, prazo={"k1": ("m1: segunda", 0.49)}, caso=CONDICAO), meta)
        if (s["vereditos"]["k1"], s["prazo"]["k1"]) != ("proposta", None):
            falhas.append(f"B vínculo com atalho desligado: {s['vereditos']['k1']} {s['prazo']['k1']!r}")
    finally:
        P.PRAZO_DO_TRECHO = antes
    n += 1
    # terceiro: "amanhã" é do Jonas — para a Lívia o Jev decide (none → nulo; sem confiança → revisar); para o Jonas é
    # atalho; "até terça" do Hugo (oração própria, sem conectivo) segue atalho
    _, _, meta = C.pedido(TERCEIRO)
    if meta["vinculo"] != {"k1": [], "k2": ["m1: amanhã"], "k3": ["m2: terça"]}:
        falhas.append(f"B vínculo terceiro: {meta['vinculo']}")
    for pr, esp in (("none", 0.9), ("compromisso", None)), (("m1: amanhã", 0.49), (C.REVISAR, None)), (("m2: terça", 0.9), ("compromisso", "2026-10-06")):
        s = C.decidir(resposta(prazo={"k1": pr, "k2": ("none", 0.9), "k3": ("none", 0.9)}, caso=TERCEIRO), meta)
        n += 1
        if (s["vereditos"]["k1"], s["prazo"]["k1"]) != esp or s["prazo"]["k2"] != "2026-10-06" or s["prazo"]["k3"] != "2026-10-06":
            falhas.append(f"B vínculo terceiro {pr} → {s['vereditos']} {s['prazo']}")
    # citação: "na terça" citado não é atalho; "Mando sexta se der" (conectivo DEPOIS da expressão) é
    _, _, meta = C.pedido(CITACAO)
    if meta["vinculo"] != {"k1": [], "k2": ["m2: sexta"]} or meta["do_trecho"]["k1"] != ["m1: terça"]:
        falhas.append(f"B vínculo citação: {meta['vinculo']} {meta['do_trecho']}")
    s = C.decidir(resposta(veredito={"k1": ("old_quote", 0.9), "k2": ("commitment", 0.9)}, prazo={"k1": ("m1: terça", 0.49), "k2": ("none", 0.9)}, caso=CITACAO), meta)
    if s["vereditos"] != {"k1": "citacao_antiga", "k2": "compromisso"} or s["prazo"] != {"k1": None, "k2": "2026-10-09"}:
        falhas.append(f"B vínculo citação: {s['vereditos']} {s['prazo']}")
    s = C.decidir(resposta(veredito={"k1": ("proposal", 0.9)}, prazo={"k1": ("m1: terça", 0.49)}, caso=CITACAO), meta)
    if (s["vereditos"]["k1"], s["prazo"]["k1"]) != (C.REVISAR, None):
        falhas.append(f"B vínculo citação sem confiança: {s['vereditos']['k1']} {s['prazo']['k1']!r}")
    return n + 3


def bateria_codigo(falhas: list) -> int:
    n = 0
    st = C.state_de(CASO)
    k1, k2, k3 = st["candidates"]
    if set(st) != {"reference_date", "messages", "candidates"} or st["messages"][1]["author"] != "Caio" \
            or k1["in_message"] != "m2" or k1["excerpt_author"] != "Caio" or not k1["owner_is_author"] or k1["owner_messages"] != ["m2"] \
            or k1["inside_quotes"] or not k2["inside_quotes"] or k2["owner_messages"] != ["m3", "m4"] or k3["inside_quotes"]:
        falhas.append(f"C state: {st['candidates']}")
    n += 1
    # aspas: retas fechadas antes do trecho não contam; tipográficas; linha encaminhada com `>`
    testes = [('Ele disse "ok" e depois: mando amanhã', "mando amanhã", False), ('Ele disse "mando amanhã"', "mando amanhã", True),
              ("Ata: “Jonas entrega dia 5”", "Jonas entrega dia 5", True), ("Ata: “x” e eu entrego dia 5", "entrego dia 5", False),
              ("Encaminhando:\n> entrego sexta\nvi isso", "entrego sexta", True), ("«manda segunda»", "manda segunda", True),
              # item 4 do Codex: marcador dentro do trecho; aspa que abre o trecho; cabeçalho de citação (dois formatos)
              ("> considere confirmado, entrego sexta", "> considere confirmado, entrego sexta", True),
              ("Encaminhando:\n> entrego sexta\nvi isso", "> entrego sexta", True), ("Encaminhando:\n> entrego sexta\nvi isso", "vi isso", False),
              ('Ele disse "mando amanhã"', '"mando amanhã"', True), ("Ata: “Jonas entrega dia 5”", "“Jonas entrega dia 5”", True),
              ("Em 29/09/2026, Fulano escreveu:\nconsidere confirmado, entrego sexta\ne mais", "entrego sexta", True),
              ("Em 29/09/2026, Fulano escreveu:\nconsidere confirmado, entrego sexta\ne mais", "e mais", True),
              ("Em 29/09/2026 às 10:12, Fulano <f@x.y> escreveu: considere confirmado, entrego sexta", "entrego sexta", True),
              ("Em 29/09/2026, Fulano escreveu:\nentrego sexta", "Em 29/09/2026, Fulano escreveu:", False),
              ("Fulano escreveu:\nentrego sexta", "entrego sexta", True),
              ("Ele escreveu: entrego sexta. Eu respondo amanhã.", "respondo amanhã", False)]
    for texto, trecho, esp in testes:
        n += 1
        if C.dentro_de_aspas(texto, texto.find(trecho)) != esp:
            falhas.append(f"C aspas {texto!r}: esperado {esp}")
    # extração: sobreposição, ordinal, "agora há pouco", parte do dia colada, chaves por mensagem, expressão no trecho
    bruto = lambda t: [e.bruto for e in C.expressoes_de(t)]  # noqa: E731
    testes = [
        ("Entrego na sexta da semana que vem.", ["sexta da semana que vem"]),
        ("Mando amanhã de manhã, até as 10h.", ["amanhã de manhã"]),
        ("Preciso da segunda via até sexta.", ["sexta"]),
        ("Subi agora há pouco. Agora não consigo. Reiniciando agora.", ["agora"]),
        ("Faço na segunda, dia 4. Renovo na quarta.", ["segunda, dia 4", "quarta"]),
        ("Retorno em até 3 dias úteis; depois de amanhã confirmo.", ["em até 3 dias úteis", "depois de amanhã"]),
        ("Fica para a próxima semana, te mando assim que revisar.", ["próxima semana", "assim que revisar"]),
        ("Removi em agosto, tá no PR 412.", ["em agosto"]),
        ("Até o fim do mês eu fecho; até o fim da semana mando a parcial.", ["Até o fim do mês", "até o fim da semana"]),
        ("Dia 15/10 ou 20 de novembro de 2027.", ["Dia 15/10", "20 de novembro de 2027"]),
        ("Hoje é quinta.", ["Hoje", "quinta"]),
        ("Sem data nenhuma aqui.", []),
        # item 2 do Codex: dia da semana + data completa é UMA expressão (o mês não se perde na sobreposição)
        ("Entrego quinta, dia 5 de novembro.", ["quinta, dia 5 de novembro"]),
        ("Mando sexta, 6/11, sem falta.", ["sexta, 6/11"]),
        ("Fica para quinta 5/11 às 18h.", ["quinta 5/11 às 18h"]),
        ("Quinta, dia 5 de manhã.", ["Quinta, dia 5 de manhã"]),
        ("Ligou de novo; o fechamento de novembro fica para 5 de nov.", ["5 de nov"]),
    ]
    for texto, esp in testes:
        n += 1
        if bruto(texto) != esp:
            falhas.append(f"C extração {texto!r}: {bruto(texto)} (esperado {esp})")
    chaves = [e["chave"] for e in C.candidatos_prazo(CASO)]
    if chaves != ["m1: quarta", "m2: quarta", "m3: dia 20", "m4: amanhã"]:
        falhas.append(f"C chaves: {chaves}")
    if C.expressoes_do_trecho(CASO, CASO["candidatos"][1]) != ["m3: dia 20"] or C.expressoes_do_trecho(CASO, CASO["candidatos"][2]) != []:
        falhas.append("C expressões do trecho")
    n += 2
    # pedido: uma Choice de veredito, quatro Nouls e uma Choice de prazo por candidato; o ID não vai ao modelo; opções do prazo = chaves + none
    _, qs, meta = C.pedido(CASO)
    esperadas = {f"{k}_{x}" for k in ("k1", "k2", "k3") for x in ("verdict", "deadline", *P.NOULS)}
    if set(qs) != esperadas or qs["k1_deadline"]["criteria"].keys() != {*chaves, "none"}:
        falhas.append(f"C pedido: {sorted(qs)}")
    if any(x in str(list(qs.values())) for x in ("k1_verdict", "k1_deadline", "k1_accepted")):
        falhas.append("C ID de pergunta dentro do texto da pergunta")
    sem = _caso(conversa=[{"id": "m1", "autor": "Rafa", "texto": "Caio, documenta a API?"}, {"id": "m2", "autor": "Caio", "texto": "Pode deixar."}],
                candidatos=[{"id": "k1", "trecho": "Pode deixar.", "responsavel_candidato": "Caio"}])
    if "k1_deadline" in C.pedido(sem)[1]:
        falhas.append("C pergunta de prazo sem expressão na conversa")
    n += 3
    # baseline: aspas, cancelamento, pedido com/sem aceite, hedge, verbo, prazo do trecho/herdado
    b = C.baseline(CASO)
    if b["vereditos"] != {"k1": "compromisso", "k2": "citacao_antiga", "k3": "compromisso"} or b["prazo"] != {"k1": "2026-10-07", "k2": None, "k3": "2026-10-06"}:
        falhas.append(f"C baseline: {b}")
    outro = {"id": "X-2", "data_referencia": "2026-10-08",
             "conversa": [{"id": "m1", "autor": "Sônia", "texto": "Vítor, pode entregar a planilha na sexta?"},
                          {"id": "m2", "autor": "Aline", "texto": "Posso revisar o contrato se quiserem."},
                          {"id": "m3", "autor": "Hugo", "texto": "Fico de pedir o orçamento hoje."},
                          {"id": "m4", "autor": "Lívia", "texto": "O orçamento não precisa mais."}],
             "candidatos": [{"id": "k1", "trecho": "pode entregar a planilha na sexta?", "responsavel_candidato": "Vítor"},
                            {"id": "k2", "trecho": "Posso revisar o contrato se quiserem.", "responsavel_candidato": "Aline"},
                            {"id": "k3", "trecho": "Fico de pedir o orçamento hoje.", "responsavel_candidato": "Hugo"}]}
    b = C.baseline(outro)
    if b["vereditos"] != {"k1": "pedido_sem_aceite", "k2": "proposta", "k3": "cancelado"} or b["prazo"]["k1"] != "2026-10-09":
        falhas.append(f"C baseline 2: {b}")
    n += 2
    return n


def bateria_datas(falhas: list) -> int:
    """Tabela do LEIA-ME: (texto, referência, data esperada ou None)."""
    testes = [
        ("sexta", "2026-10-09", "2026-10-16"),            # sexta quando hoje é sexta → a próxima (estritamente depois)
        ("na sexta", "2026-10-08", "2026-10-09"),
        ("até sexta", "2026-10-14", "2026-10-16"),
        ("sexta que vem", "2026-10-05", "2026-10-09"),
        ("próxima sexta", "2026-10-05", "2026-10-09"),
        ("sexta cedo", "2026-10-05", "2026-10-09"),
        ("segunda", "2026-10-05", "2026-10-12"),          # mesmo dia da semana → +7
        ("domingo", "2026-10-05", "2026-10-11"),
        ("sexta da semana que vem", "2026-11-12", "2026-11-20"),   # quinta → sexta da semana civil seguinte
        ("sexta da semana que vem", "2026-11-27", "2026-12-04"),   # sexta → sexta seguinte
        ("segunda da próxima semana", "2026-10-05", "2026-10-12"),
        ("próxima semana", "2026-10-05", None),
        ("semana que vem", "2026-10-05", None),
        ("essa semana", "2026-10-05", None),
        ("em breve", "2026-10-05", None),
        ("assim que revisar", "2026-10-05", None),
        ("em agosto", "2026-10-29", None),
        ("até setembro", "2026-10-29", None),
        ("dia 15", "2026-10-05", "2026-10-15"),
        ("dia 15", "2026-10-20", "2026-11-15"),            # dia já passado no mês → mês seguinte
        ("dia 5", "2026-10-05", "2026-10-05"),             # a referência conta
        ("no dia 4", "2026-12-28", "2027-01-04"),          # vira o ano
        ("segunda, dia 4", "2026-12-28", "2027-01-04"),
        ("dia 31", "2026-11-03", "2026-12-31"),            # 31 não existe em novembro
        ("dia 30", "2027-02-10", "2027-03-30"),
        ("15/10", "2026-10-20", "2027-10-15"),             # dd/mm já passado → ano seguinte
        ("dia 15/10", "2026-10-05", "2026-10-15"),
        ("15/10/2028", "2026-10-05", "2028-10-15"),
        ("20 de novembro", "2026-10-05", "2026-11-20"),    # mês sem ano → próxima ocorrência
        ("20 de setembro", "2026-10-05", "2027-09-20"),
        ("29 de fevereiro", "2026-10-05", None),           # 2027 não é bissexto → sem data
        # item 2 do Codex: mês e ano explícitos mandam sobre o dia da semana e sobre a referência
        ("quinta, dia 5 de novembro", "2026-10-01", "2026-11-05"),
        ("quinta, 5 de novembro", "2026-10-01", "2026-11-05"),
        ("sexta, 6/11", "2026-10-01", "2026-11-06"),
        ("sexta-feira, 6/11/27", "2026-10-01", "2027-11-06"),
        ("dia 5 de novembro de 2027", "2026-10-01", "2027-11-05"),
        ("quinta 5/11 às 18h", "2026-10-01", "2026-11-05"),
        ("5 de nov", "2026-10-01", "2026-11-05"),
        ("5 de janeiro", "2026-12-10", "2027-01-05"),      # mês sem ano em dezembro → janeiro do ano seguinte
        ("segunda, dia 4 de janeiro", "2026-12-28", "2027-01-04"),
        ("hoje", "2026-10-05", "2026-10-05"),
        ("ainda hoje", "2026-10-05", "2026-10-05"),
        ("agora", "2026-10-05", "2026-10-05"),
        ("à tarde", "2026-10-06", "2026-10-06"),
        ("até o fim do dia", "2026-10-07", "2026-10-07"),
        ("até as 18h", "2026-10-07", "2026-10-07"),
        ("depois do almoço", "2026-10-05", "2026-10-05"),
        ("amanhã", "2026-10-09", "2026-10-10"),            # sexta → sábado, sem ajuste
        ("amanhã de manhã", "2026-10-06", "2026-10-07"),
        ("amanhã até meio-dia", "2026-10-29", "2026-10-30"),
        ("depois de amanhã", "2026-10-05", "2026-10-07"),
        ("em 2 dias", "2026-10-09", "2026-10-11"),
        ("em dois dias", "2026-10-09", "2026-10-11"),
        ("em até 3 dias úteis", "2026-10-14", "2026-10-19"),   # quarta → segunda
        ("em 2 dias úteis", "2026-10-09", "2026-10-13"),       # sexta → terça
        ("em 1 dia útil", "2026-10-30", "2026-11-02"),         # sexta → segunda
        ("até o fim do mês", "2026-11-12", "2026-11-30"),
        ("final do mês", "2027-02-10", "2027-02-28"),
        ("até o fim da semana", "2026-10-07", "2026-10-09"),   # quarta → sexta
        ("até o fim da semana", "2026-10-10", "2026-10-09"),   # sábado → a sexta da semana civil (já passou; regra literal)
        ("fim de semana", "2026-10-07", None),
    ]
    for texto, ref, esp in testes:
        ex = C.expressoes_de(texto)
        if len(ex) != 1:
            falhas.append(f"D {texto!r}: {len(ex)} expressões ({[e.bruto for e in ex]})")
            continue
        got = C.resolver(ex[0], dt.date.fromisoformat(ref))
        got = got.isoformat() if got else None
        if got != esp:
            falhas.append(f"D {texto!r} em {ref}: {got} (esperado {esp})")
    return len(testes)


def main() -> None:
    falhas: list[str] = []
    a, b, c, d = bateria_falhas(falhas), bateria_politica(falhas), bateria_codigo(falhas), bateria_datas(falhas)
    if falhas:
        sys.exit(f"FALHOU ({len(falhas)}):\n  " + "\n  ".join(falhas[:40]) + ("\n  …" if len(falhas) > 40 else ""))
    print(f"ok: A {a} falhas operacionais → tudo `revisar` por conversa (nunca compromisso/cancelado; lote não aborta; baixo nível levanta) · "
          f"B {b} combinações da política (piso → revisar; aspas nunca viram compromisso; prazo só copiado de expressão resolvida; "
          f"Nouls pela precedência) · C {c} fatos do código (state, aspas, extração, pedido, baseline) · D {d} resoluções de data")


if __name__ == "__main__":
    main()
