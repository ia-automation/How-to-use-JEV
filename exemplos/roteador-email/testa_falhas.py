"""Bateria do código do roteador de e-mail — roda sem chave, sem rede e SEM DADOS REAIS (`python testa_falhas.py`).

Por que existe: os e-mails reais não exercitam o que é do CÓDIGO e custa caro quando falha (zero falha de rede,
zero resposta fora do contrato, nenhum corpo acima do teto), e a pasta de dados nem existe fora da pasta de
estudo. A bateria prova, com um dublê no lugar do Jev e registros INVENTADOS:
  A. falha operacional — resposta falsa (bool no lugar de número, ID faltando, classe fora das opções…), exceção
     de rede simulada ou registro inválido: `rotear_seguro` devolve `escala` com motivo "falha operacional" para
     AQUELE e-mail, nunca uma classe decidida; `rotear` (baixo nível) continua levantando erro; resposta com JSON
     válido rejeitada pelo contrato sai do cache (`invalidar`), falha de chamada e registro inválido não;
  B. política — grade de classe × confiança × os três valores de cada Noul × tamanho do corpo × corpo truncado:
     `decide` só sai com confiança ≥ limiar da classe, nenhum Noul em conflito, nas classes de caixa de entrada
     corpo ≥ mínimo e, nas classes caras, corpo não truncado;
  C. código — state só com os campos permitidos, e-mail longo ou de corpo vazio sem chamada (mesmo com assunto),
     máscara de última milha, baseline, carga que filtra por `conjunto`, valida cada registro sem abortar e PARA
     sem metadado indispensável, mensagem de dados ausentes;
  D. relatório — a seção inteira gerada com registros inventados: nenhum texto de assunto, remetente, corpo ou
     nome de regra interna aparece no Markdown; o veredito é calculado; `redes_sociais` fica à parte; registro
     inválido não aborta; a regra do corpo truncado e a tabela por state único são medidas.
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import copy
import itertools
import json
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import perguntas as P  # noqa: E402
import roteador as R  # noqa: E402
import run  # noqa: E402

BAIXO, DUVIDA, ALTO = P.NOUL_NAO / 2, (P.NOUL_NAO + P.NOUL_SIM) / 2, (P.NOUL_SIM + 1) / 2
SEGREDOS = ("ASSUNTO-INVENTADO", "CORPO-INVENTADO", "REMETENTE-INVENTADO")  # marcas que não podem ir ao relatório


def registro(i: int = 1, classe: str = "promocoes", decidido_por: str = "ai_claude", corpo: str | None = None, **sinais) -> dict:
    """E-mail INVENTADO no formato do arquivo de dados (nada daqui veio de e-mail real)."""
    s = {"sender_kind": "other_domain", "dkim_pass": True, "dkim_aligned": True, "spf_pass": True, "dmarc_pass": True,
         "auth_header_present": True, "reply_to_differs": False, "list_unsubscribe": False, "list_id": False,
         "bulk_precedence": False, "auto_submitted": False, "attachment_types": [], "link_domains": 0,
         "links_outside_sender_domain": 0, "body_from": "text", "body_truncated": False, **sinais}
    return {"id": f"EM-T{i:03d}", "grupo": f"grupo-{i % 5}", "conjunto": "ajuste", "classe": classe, "decidido_por": decidido_por,
            "confianca": None, "regra": None, "pasta_chegada": "inbox", "retro": False, "crm_client": False, "sinais": s,
            "remetente_nome": f"{SEGREDOS[2]} {i}", "assunto": f"{SEGREDOS[0]} {i}",
            "texto": corpo if corpo is not None else f"{SEGREDOS[1]} {i} " + "texto de exemplo inventado para a bateria. " * 4}


def resposta(classe: str = "promocoes", conf: float = 0.95, **nouls: float) -> dict:
    """Resposta VÁLIDA no formato da API. Sem argumentos: `promocoes` confiante e todos os Nouls baixos → `decide`
    (o pior destino para uma falha tolerada: se a validação deixar passar, a bateria vê)."""
    resto = (1 - (conf * (len(P.CLASSES) - 1) + 1) / len(P.CLASSES)) / (len(P.CLASSES) - 1)
    probs = {c: resto for c in P.CLASSES}
    probs[classe] = 1 - resto * (len(P.CLASSES) - 1)
    return {"model": "duble", "answers": {
        P.CHOICE: {"type": "choice", "choice": classe, "confidence": conf, "probabilities": probs},
        **{q: {"type": "noul", "noul": nouls.get(q, BAIXO)} for q in P.NOULS}}}


class Duble:
    """Jev de mentira: devolve a resposta dada (ou a que a função dada calcular do state) ou levanta a exceção
    dada; conta as chamadas e guarda os states, como o `Jev` de verdade guarda as medições."""

    def __init__(self, saida=None, invalidar_quebra: bool = False):
        self.saida, self.chamadas, self.states = saida if saida is not None else resposta(), [], []
        self.invalidados, self.invalidar_quebra = [], invalidar_quebra

    def invalidar(self, state, questions):
        if self.invalidar_quebra:
            raise OSError("disco")
        self.invalidados.append(state)
        return True

    def perguntar(self, state, questions):
        self.states.append(state)
        if isinstance(self.saida, Exception):
            raise self.saida
        self.chamadas.append({"ms": 1, "input_tokens": 100, "modelo": "duble", "perguntas": len(questions), "cache": False})
        return self.saida(state) if callable(self.saida) else self.saida


def _quebrada(mexe) -> dict:
    r = copy.deepcopy(resposta())
    mexe(r["answers"])
    return r


def testa_falha_operacional() -> int:
    controle = R.rotear_seguro(Duble(), registro())
    assert controle["acao"] == "decide" and controle["classe"] == "promocoes", "o controle da bateria tem de decidir"
    quebras = {
        "noul bool": lambda a: a["property_admin_mail"].update(noul=False),
        "noul string": lambda a: a["impersonates_known_sender"].update(noul="0.01"),
        "noul fora de [0,1]": lambda a: a["asks_money_or_credentials"].update(noul=-0.1),
        "noul NaN": lambda a: a["transactional_notice"].update(noul=float("nan")),
        "noul faltando": lambda a: a.pop("pushes_to_act_on_pretext"),
        "noul com tipo trocado": lambda a: a["unsolicited_bulk_offer"].update(type="score"),
        "classe fora das opções": lambda a: a[P.CHOICE].update(choice="lixeira"),
        "choice com tipo trocado": lambda a: a[P.CHOICE].update(type="noul"),
        "choice sem distribuição": lambda a: a[P.CHOICE].pop("probabilities"),
        "distribuição com classe a mais": lambda a: a[P.CHOICE]["probabilities"].update(lixeira=0.0),
        "distribuição que não soma 1": lambda a: a[P.CHOICE]["probabilities"].update(promocoes=0.2),
        "probabilidade bool": lambda a: a[P.CHOICE]["probabilities"].update(spam=True),
        "choice sem confiança": lambda a: a[P.CHOICE].pop("confidence"),
        "confiança string": lambda a: a[P.CHOICE].update(confidence="0.95"),
        "answers vazio": lambda a: a.clear(),
    }
    # (nome, dublê, a resposta chegou como JSON e foi rejeitada pelo contrato → tem de sair do cache)
    saidas = [(nome, Duble(_quebrada(mexe)), True) for nome, mexe in quebras.items()]
    saidas += [("sem answers", Duble({"model": "duble"}), True), ("resposta não é objeto", Duble("ok"), True),
               ("timeout", Duble(TimeoutError("x")), False), ("cache faltando", Duble(RuntimeError("resposta não gravada")), False),
               ("contrato rejeitado e a quarentena falha", Duble(_quebrada(quebras["noul bool"]), invalidar_quebra=True), False)]
    for nome, duble, invalida in saidas:
        s = R.rotear_seguro(duble, registro())
        assert s["acao"] == "escala" and s["classe"] is None and s["origem"] == "falha", (nome, s)
        assert s["motivo"].startswith("falha operacional") and SEGREDOS[1] not in s["motivo"], (nome, s["motivo"])
        assert len(duble.invalidados) == (1 if invalida else 0), (nome, duble.invalidados)
        if invalida:
            assert duble.invalidados[0] == duble.states[0], nome   # invalida exatamente o pedido feito
        try:
            R.rotear(duble, registro())
        except Exception:  # noqa: BLE001 — o baixo nível tem de levantar
            pass
        else:
            raise AssertionError(f"`rotear` não levantou em: {nome}")
    base = registro()
    invalidos = {"não é objeto": None, "sem sinais": {**base, "sinais": None}, "corpo não é texto": {**base, "texto": 123},
                 "sinal booleano como string": {**base, "sinais": {**base["sinais"], "dkim_aligned": "true"}},
                 "sinal faltando": {**base, "sinais": {k: v for k, v in base["sinais"].items() if k != "list_unsubscribe"}},
                 "links como bool": {**base, "sinais": {**base["sinais"], "links_outside_sender_domain": True}},
                 "anexos não é lista": {**base, "sinais": {**base["sinais"], "attachment_types": "pdf"}}}
    invalidos["truncado não é booleano"] = {**base, "sinais": {**base["sinais"], "body_truncated": "sim"}}
    for nome, ruim in invalidos.items():
        duble = Duble()
        s = R.rotear_seguro(duble, ruim)
        assert s["acao"] == "escala" and s["origem"] == "falha" and not duble.states and not duble.invalidados, (nome, s)
        assert R.baseline_seguro(ruim)["acao"] == "escala", nome
    return len(saidas) + len(invalidos)


def _conflito_esperado(classe: str, nouls: dict) -> bool:
    """A regra de `P.CONFLITOS` reescrita de outro jeito (não chama `R.conflitos`)."""
    regra = P.CONFLITOS[classe]
    return any(nouls[q] >= P.NOUL_SIM for q in regra.get("alto", ())) or any(nouls[q] > P.NOUL_NAO for q in regra.get("nao_baixo", ()))


def testa_politica() -> int:
    """Grade inteira de `compor`: 6 classes × 3 confianças × 3^Nouls × 2 tamanhos de corpo × truncado ou não."""
    n = decididos = truncados_barrados = 0
    for classe in P.CLASSES:
        lim = P.LIMIAR_CONF[classe]
        for combo in itertools.product((BAIXO, DUVIDA, ALTO), repeat=len(P.NOULS)):
            nouls = dict(zip(P.NOULS, combo))
            for conf, corpo, trunc in itertools.product((lim - 0.01, lim, 0.999), (P.MIN_CORPO_CAIXA - 1, P.MIN_CORPO_CAIXA), (False, True)):
                d = R.compor({"classe": classe, "conf": conf, "probs": {}, "nouls": nouls}, corpo, trunc)
                n += 1
                espera = (conf >= lim and not _conflito_esperado(classe, nouls)
                          and not (classe in P.CLASSES_CAIXA and corpo < P.MIN_CORPO_CAIXA)
                          and not (trunc and classe in P.CLASSES_CARAS))
                assert (d["acao"] == "decide") == espera, (classe, conf, corpo, trunc, nouls, d["motivo"])
                assert d["classe"] == classe and d["acao"] in R.ACOES and d["truncado"] == trunc
                assert (d["trava"] is None) == (d["acao"] == "decide" or conf < lim), d
                decididos += espera
                truncados_barrados += d["trava"] == "truncado"
    assert decididos > 0 and truncados_barrados > 0
    # truncado nunca decide classe cara, mesmo com tudo a favor; classe barata decide
    for classe in P.CLASSES_CARAS:
        assert R.compor({"classe": classe, "conf": 0.999, "probs": {}, "nouls": {q: BAIXO for q in P.NOULS}}, 500, True)["trava"] == "truncado"
    assert R.compor({"classe": "promocoes", "conf": 0.999, "probs": {}, "nouls": {q: BAIXO for q in P.NOULS}}, 500, True)["acao"] == "decide"
    assert set(P.CLASSES_CARAS) | {"promocoes", "redes_sociais"} == set(P.CLASSES) and set(P.CLASSES_CAIXA) <= set(P.CLASSES_CARAS)
    # toda classe tem limiar e regra de conflito; todo Noul citado existe; todo Noul é usado por alguma trava
    assert set(P.LIMIAR_CONF) == set(P.CONFLITOS) == set(P.CLASSES)
    citados = {q for regra in P.CONFLITOS.values() for lista in regra.values() for q in lista}
    assert citados == set(P.NOULS), citados ^ set(P.NOULS)
    # os dois erros caros têm trava: fraude nas classes de caixa; e-mail de gente/condomínio em spam e golpe
    for c in P.CLASSES_CAIXA:
        assert {"impersonates_known_sender", "pushes_to_act_on_pretext"} <= set(P.CONFLITOS[c]["alto"])
    for c in ("spam", "golpe"):
        assert "human_wrote_to_this_recipient" in P.CONFLITOS[c]["alto"] and "property_admin_mail" in P.CONFLITOS[c]["nao_baixo"]
    # desligar os conflitos (variante medida) deixa só limiar + corpo curto
    with run._com(USAR_CONFLITOS=False):
        d = R.compor({"classe": "golpe", "conf": 0.99, "probs": {}, "nouls": {q: ALTO for q in P.NOULS}}, 500)
        assert d["acao"] == "decide"
    return n


def testa_codigo() -> int:
    n = 0
    # state: só os campos permitidos; nada de id, grupo, gabarito ou sinal fora da lista
    st = R.state_de(registro(corpo="corpo"))
    assert set(st) == {"sender_name", "subject", "body", "signals"} and list(st["signals"]) == P.SINAIS_NO_STATE
    assert "EM-T" not in json.dumps(st) and "ai_claude" not in json.dumps(st) and "promocoes" not in json.dumps(st)
    n += 1
    # campos de texto ausentes viram string vazia (não erro); corpo vazio não chama o Jev — mesmo com assunto
    duble = Duble()
    s = R.rotear_seguro(duble, {**registro(), "assunto": None, "texto": None})
    assert s["acao"] == "escala" and s["origem"] == "vazio" and not duble.states
    for corpo in (None, "", "  \n "):
        s = R.rotear_seguro(Duble(resposta("golpe", 0.99)), {**registro(), "texto": corpo})   # assunto presente
        assert s["acao"] == "escala" and s["origem"] == "vazio" and s["classe"] is None, (corpo, s)
    assert not duble.states
    s = R.rotear_seguro(duble, {**registro(), "texto": "x" * (P.TETO_CORPO + 1)})
    assert s["acao"] == "escala" and s["origem"] == "longo" and not duble.states
    s = R.rotear_seguro(duble, {**registro(), "texto": "x" * P.TETO_CORPO})
    assert s["origem"] == "jev" and len(duble.states) == 1
    n += 3
    # corpo curto: classe de caixa não decide sozinha; classe fora da caixa decide
    curto = registro(corpo="ok")
    assert R.rotear_seguro(Duble(resposta("notificacoes", 0.99)), curto)["acao"] == "escala"
    assert R.rotear_seguro(Duble(resposta("principal", 0.99)), curto)["acao"] == "escala"
    assert R.rotear_seguro(Duble(resposta("promocoes", 0.99)), curto)["acao"] == "decide"
    n += 3
    # máscara de última milha: nome em MAIÚSCULAS depois de saudação some; o resto fica
    t, k = run.mascarar("Olá, FULANA DE TAL SOBRENOME! Seu boleto vence amanhã. PROMOÇÃO IMPERDÍVEL hoje.")
    assert k == 1 and "FULANA" not in t and "SOBRENOME" not in t and "[NOME]" in t and "PROMOÇÃO IMPERDÍVEL" in t, t
    t, k = run.mascarar("Prezado(a) Sr(a). BELTRANO SILVA, segue.")
    assert k >= 1 and "BELTRANO" not in t, t
    assert run.mascarar("Olá, tudo bem?") == ("Olá, tudo bem?", 0) and run.mascarar(None) == (None, 0)
    n += 3
    # truncado: só o sinal muda a decisão (classe cara escala; barata decide), sem entrar no state
    trunc = registro(body_truncated=True)
    assert "body_truncated" not in json.dumps(R.state_de(trunc))
    assert R.rotear_seguro(Duble(resposta("golpe", 0.99)), trunc)["trava"] == "truncado"
    assert R.rotear_seguro(Duble(resposta("golpe", 0.99)), registro())["acao"] == "decide"
    assert R.rotear_seguro(Duble(resposta("promocoes", 0.99)), trunc)["acao"] == "decide"
    n += 4
    # baseline: uma regra por caso inventado
    casos = [
        (registro(dkim_aligned=False, links_outside_sender_domain=1, corpo="Atualize sua senha agora"), "golpe"),
        ({**registro(), "assunto": "RES: contrato"}, "principal"),
        (registro(corpo="Circular do condomínio sobre a assembleia"), "principal"),
        (registro(list_unsubscribe=True, corpo="Ofertas da semana"), "promocoes"),
        (registro(list_unsubscribe=True, corpo="Seu recibo chegou"), "notificacoes"),
        (registro(auto_submitted=True, corpo="mensagem automática"), "notificacoes"),
        (registro(corpo="nada que alguma regra pegue"), None),
    ]
    for r, classe in casos:
        b = R.baseline(r)
        assert b["classe"] == classe and b["acao"] == ("decide" if classe else "escala"), (classe, b)
    n += len(casos)
    # carga: filtra por conjunto, valida ANTES da máscara (registro ruim não aborta: vira falha), aplica a máscara,
    # calcula a chave do state, e sem o arquivo sai com a mensagem de dados ausentes
    with tempfile.TemporaryDirectory() as pasta:
        arq = Path(pasta) / "emails.jsonl"
        linhas = [registro(1), {**registro(2), "conjunto": "teste"}, {**registro(3), "texto": "Olá, NOME COMPLETO INVENTADO, bom dia"},
                  {**registro(4), "texto": 123}, {**registro(5), "sinais": None},
                  {**registro(6), "assunto": registro(1)["assunto"], "texto": registro(1)["texto"], "remetente_nome": registro(1)["remetente_nome"]}]
        arq.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in linhas) + "\n", encoding="utf-8")
        aj, te = run.carregar("ajuste", arq), run.carregar("teste", arq)
        assert [r["id"] for r in aj] == ["EM-T001", "EM-T003", "EM-T004", "EM-T005", "EM-T006"] and [r["id"] for r in te] == ["EM-T002"]
        assert aj[1]["_mascarado"] and aj[1]["_trocas"] == 1 and "INVENTADO" not in aj[1]["texto"] and not aj[0]["_mascarado"]
        assert aj[2]["_invalido"] and aj[3]["_invalido"] and aj[2]["texto"] == 123 and aj[2]["_state"] is None
        assert not aj[0]["_invalido"] and aj[0]["_state"] == aj[4]["_state"] != aj[1]["_state"]
        texto, resumo = run.secao_conjunto("ajuste", aj, fabrica=lambda: Duble())
        assert resumo["custo"]["falha"] == 2 and "Registros inválidos na carga (→ falha operacional): 2" in texto
        for ruim, marca in ((json.dumps({**registro(7), "classe": None}), "classe"), (json.dumps({**registro(7), "decidido_por": ""}), "decidido_por"),
                            (json.dumps({**registro(7), "conjunto": "outro"}), "conjunto"), (json.dumps({**registro(7), "classe": "lixeira"}), "classe"),
                            ("[1, 2]", "id"), ("{isto não é json", "não é JSON")):
            arq.write_text(json.dumps(registro(1), ensure_ascii=False) + "\n" + ruim + "\n", encoding="utf-8")
            try:
                run.carregar("teste", arq)   # o registro ruim nem é do conjunto pedido: o metadado é conferido antes do filtro
            except SystemExit as e:
                assert "registro 2" in str(e) and marca in str(e) and SEGREDOS[0] not in str(e), (marca, e)
            else:
                raise AssertionError(f"carregar não parou com metadado inválido: {marca}")
        try:
            run.carregar("ajuste", Path(pasta) / "nao-existe.jsonl")
        except SystemExit as e:
            assert "dados privados ausentes" in str(e)
        else:
            raise AssertionError("carregar não parou sem o arquivo de dados")
    n += 7
    # as linhas paralelas dividem a trava por pedido (state idêntico em duas linhas = uma chamada, uma resposta)
    from jevcache import Jev
    with tempfile.TemporaryDirectory() as pasta:
        inst = [Jev(pasta, modo="gravado") for _ in range(run.PARALELO)]
        # desde 2026-10-01 ~15h45 a infra comum já divide a tabela por PASTA de cache; `compartilhar_travas` é redundante
        run.compartilhar_travas(inst)
        assert len({id(j._travas) for j in inst}) == 1 and len({id(j._guarda) for j in inst}) == 1
        saidas, custo = run.rodar([registro(1), registro(2)], fabrica=lambda: Jev(pasta, modo="gravado"))
        assert custo["falha"] == 2 and all(s["origem"] == "falha" for s in saidas)   # sem cache: falha, não aborta
    n += 2
    # nada de pasta de cache nem de dados dentro do exemplo; o cache aponta para fora do repositório
    assert not (AQUI / "cache").exists() and not (AQUI / "dados").exists(), "o exemplo não pode ter cache/ nem dados/"
    assert ".local" in run.CACHE.parts and ".local" in run.DADOS.parts
    n += 1
    return n


def testa_relatorio() -> int:
    """A seção inteira com registros inventados e um dublê que responde conforme o e-mail."""
    plano = {  # id → (classe em produção, quem decidiu, o que o dublê responde)
        1: ("promocoes", "ai_claude", resposta("promocoes", 0.95)),                        # decide e concorda
        2: ("golpe", "ai_codex", resposta("notificacoes", 0.95)),                           # GOLPE NA CAIXA (erro caro 1)
        3: ("principal", "ai_api", resposta("golpe", 0.95)),                                # CLIENTE PERDIDO (erro caro 2)
        4: ("principal", "rule", resposta("spam", 0.95, property_admin_mail=ALTO)),         # trava barra o erro caro
        5: ("golpe", "rule", resposta("golpe", 0.5)),                                       # confiança baixa → escala
        6: ("redes_sociais", "ai_claude", resposta("redes_sociais", 0.9)),                  # à parte
        7: ("notificacoes", "crm", resposta("notificacoes", 0.9)),                          # estrato crm: só em `todos`
        8: ("spam", "ai_claude", resposta("promocoes", 0.9, impersonates_known_sender=ALTO)),  # trava barra erro barato
        10: ("golpe", "ai_claude", resposta("golpe", 0.95)),                                 # corpo truncado: classe cara escala
        11: ("promocoes", "ai_claude", resposta("promocoes", 0.95)),                         # mesmo state do 1 (campanha repetida)
    }
    casos = [registro(i, classe, quem) for i, (classe, quem, _) in plano.items()]
    casos[-2]["sinais"]["body_truncated"] = True
    casos[-1].update(assunto=casos[0]["assunto"], texto=casos[0]["texto"], remetente_nome=casos[0]["remetente_nome"])
    for r in casos:
        r["_state"] = run.chave_state(r)
    casos.append({**registro(9, "golpe", "ai_claude"), "sinais": None, "regra": "nome_de_regra_interna"})   # inválido: não aborta
    casos.append({**registro(12, "golpe", "ai_codex"), "texto": 123, "regra": "nome_de_regra_interna"})      # inválido: não aborta
    por_assunto = {f"{SEGREDOS[0]} {i}": r for i, (_, _, r) in plano.items()}
    with run._com(CRITERIO_CONTINUAR=P.CRITERIO_CONTINUAR or {"limites": {
            "golpe_na_caixa_max": 0.01, "cliente_perdido_max": 0.01, "concordancia_min": 0.95, "cobertura_min": 0.4,
            "cobertura_sugerida_no_briefing": 0.5}}):
        texto, resumo = run.secao_conjunto("ajuste", casos, fabrica=lambda: Duble(lambda st: por_assunto[st["subject"]]))
        cab = run.cabecalho("linha do manifesto") + run.comparacao({"ajuste": resumo})
    for marca in SEGREDOS + ("nome_de_regra_interna",):
        assert marca not in texto and marca not in cab, f"texto de e-mail ou regra interna vazou no relatório: {marca}"
    assert "texto de exemplo inventado" not in texto
    ia, todos = resumo["linhas"][("só IA", run.JEV)]["_c"], resumo["linhas"][("todos", run.JEV)]["_c"]
    assert ia["n"] == 8 and ia["caro1"] == 1 and ia["caro2"] == 1 and ia["certos"] == 2 and ia["dec"] == 4, dict(ia)
    assert todos["n"] == 11 and todos["dec"] == 5, dict(todos)                              # sem redes_sociais; crm entra
    assert resumo["linhas"][("só regra", run.JEV)]["_c"]["dec"] == 0
    assert resumo["custo"]["falha"] == 2 and resumo["passou"] is False
    assert "GOLPE NA CAIXA" in texto and "CLIENTE PERDIDO" in texto and "EM-T002" in texto and "EM-T003" in texto
    assert "`spam` × `property_admin_mail`" in texto and "`promocoes` × `impersonates_known_sender`" in texto
    assert "EM-T006" in texto and "NÃO PASSOU" in texto and "2 falha(s) operacional(is)" in texto
    assert "| truncado (código) | 0 | 0 | 1 |" in texto, "a trava do corpo truncado não foi medida"   # barrou 1 acerto (EM-T010)
    assert "1 barrado(s) por ela" in texto and "corpo truncado na extração (`golpe` é classe cara)" in texto
    assert "| só IA | por e-mail | 8 |" in texto and "| só IA | state único | 5 |" in texto and "| só IA | sem states do ajuste | 4 |" in texto, texto
    assert "| id | decidido_por | produção |" in texto and "| regra |" not in texto
    # bootstrap: determinístico e dentro de [0, 1]
    itens = [(r, "decide", r["classe"]) for r in casos[:8]]
    ic1, ic2 = run.bootstrap(itens), run.bootstrap(itens)
    assert ic1 == ic2 and all(0 <= a <= b <= 1 for a, b in ic1.values())
    # custo do LLM: cresce com o texto e com o preço
    curto, longo = registro(corpo="a"), registro(corpo="a" * 4000)
    assert run.custo_llm(curto, run.LLM_BARATO) < run.custo_llm(longo, run.LLM_BARATO) < run.custo_llm(longo, run.LLM_RACIOCINIO)
    return 18


def main() -> None:
    partes = {"A falha operacional": testa_falha_operacional, "B política": testa_politica,
              "C código": testa_codigo, "D relatório": testa_relatorio}
    for nome, f in partes.items():
        print(f"{nome}: {f()} verificações ok")
    print("testa_falhas: tudo ok (código nosso com dublê e registros inventados; nenhuma medição do Jev)")


if __name__ == "__main__":
    main()
