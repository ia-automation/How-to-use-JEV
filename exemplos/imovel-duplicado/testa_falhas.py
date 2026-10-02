"""Bateria do código do imóvel duplicado — roda sem chave e sem rede (`python testa_falhas.py`).

Por que existe: os conjuntos rotulados não exercitam o que é do CÓDIGO e custa caro quando falha (zero falha de
rede, zero resposta fora do contrato, nenhum par acima do teto). A bateria prova, com um dublê no lugar do Jev:
  A. falha operacional — resposta falsa (bool no lugar de número, ID faltando, Score fora dos níveis…), exceção de
     rede simulada ou anúncio inválido: `julgar_seguro` devolve `revisar` com motivo "falha operacional" para
     AQUELE par, nunca `unir` nem `manter_separados`; `julgar` (baixo nível) continua levantando erro;
  B. política — grade com os três valores de cada Noul (não / dúvida / sim) × Score × área × bairro: `unir` só sai
     com os três vetos em `nao`, estado em `nao`, sinal forte em `sim`, área dentro ou conciliada, bairro igual e
     Score acima do mínimo; o Score nunca CRIA união; `manter_separados` só sai com um veto em `sim`;
  C. fatos do código — tolerâncias na borda, área total × privativa, par decidido pelo código sem chamada, par
     acima do teto sem chamada;
  D. os quatro achados da revisão do Codex (2026-10-01), caso a caso, sem abortar no primeiro erro: (1) metragem
     sem rótulo de área da unidade não concilia; (2) número brasileiro completo ("1.068,50 m²"); (3) bairro que
     difere só no texto não vira `manter_separados` sem chamada; (4) anúncio inválido não aborta o relatório.
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import copy
import itertools
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import duplicado as D  # noqa: E402
import perguntas as P  # noqa: E402
import run as R  # noqa: E402

BAIXO = {q: P.FAIXA[q][0] / 2 for q in P.NOULS}                      # dentro do "não"
DUVIDA = {q: (P.FAIXA[q][0] + P.FAIXA[q][1]) / 2 for q in P.NOULS}  # dentro da faixa do meio
ALTO = {q: (P.FAIXA[q][1] + 1) / 2 for q in P.NOULS}                # dentro do "sim"

A = {"titulo": "Apto 2 dorms - Mooca", "descricao": "Condomínio Bosque da Mooca: 2 quartos, 1 vaga, sacada.",
     "bairro": "Mooca", "cidade": "São Paulo", "quartos": 2, "vagas": 1, "area_m2": 55, "preco": 510000, "condominio_reais": 580}
B = {**A, "titulo": "Apartamento 2 quartos em Mooca", "descricao": "Mooca, Condomínio Bosque da Mooca: 2 dorms, 1 vaga, sacada na sala."}
CHAVES_STATE = {"same_neighborhood_and_city", "same_bedrooms", "same_parking_spaces", "area_within_3_percent",
                "area_gap_explained_by_second_figure", "price_within_5_percent"}


def resposta(score: float = 1.95, **nouls: float) -> dict:
    """Resposta VÁLIDA no formato da API. Sem argumentos: nenhum veto, estado calmo, sinal forte alto e Score no
    nível 2 → `unir` (o pior destino possível para uma falha tolerada: se a validação deixar passar, a bateria vê)."""
    padrao = {**BAIXO, "shared_distinctive_details": ALTO["shared_distinctive_details"],
              "same_building_or_street": ALTO["same_building_or_street"]}
    return {"model": "duble", "answers": {
        P.SCORE: {"type": "score", "score": score, "confidence": 0.9, "probabilities": {"0": 0.0, "1": 0.05, "2": 0.95}},
        **{q: {"type": "noul", "noul": nouls.get(q, padrao[q])} for q in P.NOULS}}}


class Duble:
    """Jev de mentira: devolve a resposta dada ou levanta a exceção dada, conta as chamadas e guarda os states."""

    def __init__(self, saida=None):
        self.saida, self.chamadas, self.states = saida if saida is not None else resposta(), 0, []

    def perguntar(self, state, questions):
        self.chamadas += 1
        self.states.append(state)
        if isinstance(self.saida, Exception):
            raise self.saida
        return self.saida

    def resumo(self) -> dict:
        return {}  # o `run.py` cai no custo zerado: aqui não há medição


def _quebrada(mexe) -> dict:
    r = copy.deepcopy(resposta())
    mexe(r["answers"])
    return r


def testa_falha_operacional() -> int:
    assert D.julgar_seguro(Duble(), A, B)["acao"] == "unir", "o controle da bateria tem de dar `unir`"
    quebras = {
        "noul bool": lambda a: a["fixed_contradiction"].update(noul=False),
        "noul string": lambda a: a["address_conflict"].update(noul="0.01"),
        "noul fora de [0,1]": lambda a: a["layout_contradiction"].update(noul=-0.1),
        "noul NaN": lambda a: a["state_contradiction"].update(noul=float("nan")),
        "ID faltando": lambda a: a.pop("fixed_contradiction"),
        "tipo trocado": lambda a: a["fixed_contradiction"].update(type="choice"),
        "score bool": lambda a: a[P.SCORE].update(score=True),
        "score fora dos níveis": lambda a: a[P.SCORE].update(score=2.4),
        "score sem distribuição": lambda a: a[P.SCORE].pop("probabilities"),
        "score com nível a mais": lambda a: a[P.SCORE]["probabilities"].update({"3": 0.0}),
        "score sem confiança": lambda a: a[P.SCORE].pop("confidence"),
        "answers vazio": lambda a: a.clear(),
    }
    saidas = [(nome, Duble(_quebrada(mexe))) for nome, mexe in quebras.items()]
    saidas += [("timeout", Duble(TimeoutError("x"))), ("cache faltando", Duble(RuntimeError("resposta não gravada")))]
    for nome, duble in saidas:
        s = D.julgar_seguro(duble, A, B)
        assert s["acao"] == "revisar" and s["origem"] == "falha" and s["motivo"].startswith("falha operacional"), (nome, s)
        try:
            D.julgar(duble, A, B)
        except Exception:  # noqa: BLE001 — o baixo nível tem de levantar
            pass
        else:
            raise AssertionError(f"`julgar` não levantou em: {nome}")
    invalidos = {"sem descrição": {**A, "descricao": " "}, "quartos bool": {**A, "quartos": True}, "área zero": {**A, "area_m2": 0},
                 "preço string": {**A, "preco": "510000"}, "não é objeto": None}
    for nome, ruim in invalidos.items():
        duble = Duble()
        s = D.julgar_seguro(duble, ruim, B)
        assert s["acao"] == "revisar" and s["origem"] == "falha" and duble.chamadas == 0, (nome, s)
    return len(saidas) + len(invalidos)


def testa_politica() -> int:
    """Grade inteira de `compor`: 3^6 Nouls × 4 Scores × 4 leituras de área × 2 de bairro."""
    fatos = [{"area": area, "local": lugar} for area in ("dentro", "conciliada", "indefinida", "diverge")
             for lugar in ("igual", "indefinido")]
    n = unioes = 0
    for combo in itertools.product((BAIXO, DUVIDA, ALTO), repeat=len(P.NOULS)):
        nouls = {q: nivel[q] for q, nivel in zip(P.NOULS, combo)}
        s = {q: D._faixa(nouls[q], *P.FAIXA[q]) for q in P.NOULS}
        for score, f in itertools.product((0.2, 1.0, P.SCORE_UNIR_MIN - 0.05, 1.95), fatos):
            v = {"nouls": nouls, "score": score, "score_conf": 0.9, "score_probs": {}}
            d, so_nouls = D.compor(v, f), D.acao_nouls(v, f)[0]
            n += 1
            limpo = (all(s[q] is False for q in P.VETOS) and s["state_contradiction"] is False
                     and s["shared_distinctive_details"] is True
                     and f["area"] in ("dentro", "conciliada") and f["local"] == "igual")
            assert (d["acao"] == "unir") == (limpo and score >= P.SCORE_UNIR_MIN), (nouls, score, f, d["motivo"])
            assert d["acao"] != "unir" or so_nouls == "unir", "o Score criou uma união"
            if d["acao"] == "manter_separados":
                assert any(s[q] is True for q in P.VETOS), (nouls, d["motivo"])
            if any(s[q] is None for q in P.VETOS) and not any(s[q] is True for q in P.VETOS):
                assert d["acao"] == "revisar", (nouls, d["motivo"])
            unioes += d["acao"] == "unir"
    assert unioes > 0
    return n


def testa_fatos_do_codigo() -> int:
    f = D.fatos({**A, "area_m2": 97, "preco": 95}, {**B, "area_m2": 100, "preco": 100})
    assert f["area_within_3_percent"] and f["price_within_5_percent"], "borda da tolerância entra (≤)"
    f = D.fatos({**A, "area_m2": 96, "preco": 94}, {**B, "area_m2": 100, "preco": 100})
    assert not f["area_within_3_percent"] and not f["price_within_5_percent"] and not f["area_gap_explained_by_second_figure"]
    total = {**B, "area_m2": 92, "descricao": "Área total de 92 m² (55 m² privativos). Condomínio Bosque da Mooca."}
    f = D.fatos(A, total)
    assert not f["area_within_3_percent"] and f["area_gap_explained_by_second_figure"], "área total × privativa"
    assert D.baseline(A, total)["acao"] == "manter_separados" and D.baseline(A, B)["acao"] == "unir"
    # o que o código decide não chama o Jev (bairro que difere dentro da mesma cidade saiu daqui: parte D)
    for outro in ({**B, "cidade": "Santos"}, {**B, "quartos": 3}, {**B, "vagas": 2}):
        duble = Duble()
        s = D.julgar_seguro(duble, A, outro)
        assert s["acao"] == "manter_separados" and s["origem"] == "codigo" and duble.chamadas == 0, s
    assert D.fatos(A, {**B, "bairro": "MOOCA ", "cidade": "Sao Paulo"})["same_neighborhood_and_city"], "acento e caixa não separam"
    # par acima do teto: `revisar` sem chamada
    duble = Duble()
    s = D.julgar_seguro(duble, A, {**B, "descricao": "x" * (P.TETO_CARACTERES + 1)})
    assert s["acao"] == "revisar" and s["origem"] == "longo" and duble.chamadas == 0, s
    return 8


# ---------------------------------------------------------------------------------------- D. achados do Codex
# (nome, área de x, descrição de x, área de y, descrição de y ou None = a de B, leitura esperada). O título de A/B
# não cita metragem. Em TODAS o dublê responde "unir": só a leitura `conciliada` pode deixar a união passar.
AREAS = [
    # achado 1 — coincidência de metragem não concilia
    ("salão comum (o caso do Codex)", 92, "Apartamento de 92 m² com salão comum de 68 m².", 68, None, "indefinida"),
    ("número solto, sem rótulo", 92, "Sala ampla. Depósito de 68 m² na garagem.", 68, None, "indefinida"),
    ("área comum total não é a unidade", 92, "Área comum total de 68 m² no térreo.", 68, None, "indefinida"),
    ("só a área do outro tem rótulo", 92, "São 68 m² privativos.", 68, None, "indefinida"),
    ("dois valores para o mesmo tipo", 92, "Área total de 92 m², área privativa de 68 m². Garden com área privativa de 75 m².", 68, None, "indefinida"),
    ("o mesmo número com dois rótulos", 92, "92 m² de área total 68 m² privativos.", 68, None, "indefinida"),
    ("o outro texto desmente", 92, "Área total de 92 m² (68 m² privativos).", 68, "Área total de 68 m².", "indefinida"),
    ("nenhuma metragem bate", 92, "Área total de 92 m² (70 m² privativos).", 60, None, "diverge"),
    # achado 2 — número brasileiro completo
    ("1.068,50 m² não é 68,5", 1068.5, "Cobertura com área total de 1.068,50 m².", 68, None, "diverge"),
    ("decimal à inglesa é ambíguo", 92, "Área total de 92 m² (68.5 m² privativos).", 68.5, None, "indefinida"),
    ("ponto de milhar dos dois lados", 1500, "Área total de 1.500 m² (1.068 m² privativos).", 1068, None, "conciliada"),
    ("vírgula decimal e m2", 92, "Área total de 92 m2, área útil de 68,5 m2.", 68.5, None, "conciliada"),
    # relação total × privativa com rótulo nos dois números: continua conciliando (as formas dos dados)
    ("total antes, privativos no parêntese", 92, "Área total de 92 m² (68 m² privativos).", 68, None, "conciliada"),
    ("total depois do número", 130, "130 m² de área total, 95 m² privativos.", 95, None, "conciliada"),
    ("área privativa antes", 120, "Área total 120 m², área privativa 88 m².", 88, None, "conciliada"),
    ("úteis", 160, "160 m² de área total (120 m² úteis).", 120, None, "conciliada"),
    ("útil antes", 135, "Área total 135 m², útil 100 m².", 100, None, "conciliada"),
    ("privativa antes, sem a palavra área", 150, "Área total 150 m², privativa 110 m².", 110, None, "conciliada"),
    ("apartamento de N m² + privativos", 92, "Apartamento de 92 m² (68 m² privativos).", 68, None, "conciliada"),
    ("o anúncio declara a privativa e cita a total", 68, "Área privativa de 68 m²; 92 m² de área total.", 92, None, "conciliada"),
]
BAIRROS_IGUAIS = [("Vila Mariana", "V. Mariana"), ("Vila Mariana", "Vl Mariana"), ("Jardim Paulista", "Jd. Paulista"),
                  ("Santa Cecília", "Sta. Cecilia"), ("Santo Amaro", "STO AMARO"), ("Alto da Boa Vista", "alto da boa-vista")]
BAIRROS_INDEFINIDOS = [("Vila Mariana", "Vila Clementino"), ("Quadra V", "Quadra Vila"), ("Santana", "Sant'Ana")]


def _confere_area(area_x, desc_x, area_y, desc_y, esperado) -> None:
    x = {**A, "area_m2": area_x, "descricao": desc_x}
    y = {**B, "area_m2": area_y, "descricao": desc_y or B["descricao"]}
    for a, b in ((x, y), (y, x)):  # a ordem do par não muda a leitura
        f = D.fatos(a, b)
        assert f["area_gap_explained_by_second_figure"] is (esperado == "conciliada"), f
        assert f["area"] == esperado, f["area"]
        duble = Duble()
        s = D.julgar_seguro(duble, a, b)
        assert s["acao"] == ("unir" if esperado == "conciliada" else "revisar") and duble.chamadas == 1, s


def _confere_bairro_igual(ba, bb) -> None:
    a, b = {**A, "bairro": ba}, {**B, "bairro": bb}
    assert D.fatos(a, b)["same_neighborhood_and_city"] is True and D.baseline(a, b)["acao"] == "unir"
    duble = Duble()
    s = D.julgar_seguro(duble, a, b)
    assert s["acao"] == "unir" and s["origem"] == "jev" and duble.chamadas == 1, s


def _confere_bairro_indefinido(ba, bb) -> None:
    a, b = {**A, "bairro": ba}, {**B, "bairro": bb}
    f = D.fatos(a, b)
    assert f["same_neighborhood_and_city"] is False and f["local"] == "indefinido", f
    assert D.baseline(a, b)["acao"] == "manter_separados", "o baseline é a regra: sem prova de igual, separa"
    duble = Duble()  # o dublê diz "unir": bairro indefinido não deixa
    s = D.julgar_seguro(duble, a, b)
    assert s["acao"] == "revisar" and s["origem"] == "jev" and duble.chamadas == 1, s
    s = D.julgar_seguro(Duble(resposta(address_conflict=ALTO["address_conflict"], same_building_or_street=BAIXO["same_building_or_street"])), a, b)
    assert s["acao"] == "manter_separados" and s["origem"] == "jev", "quem separa é o veto do Jev, não o texto do bairro"


def _confere_cidade(outro) -> None:
    duble = Duble()
    s = D.julgar_seguro(duble, A, outro)
    assert s["acao"] == "manter_separados" and s["origem"] == "codigo" and duble.chamadas == 0, s


def _confere_state() -> None:
    """O state que vai ao Jev leva só as seis chaves booleanas da rodada 1 (as leituras do código ficam de fora)."""
    for a, b in ((A, B), ({**A, "bairro": "Vila Mariana"}, {**B, "bairro": "Vila Clementino"}),
                 ({**A, "area_m2": 92, "descricao": "Apartamento de 92 m² com salão comum de 68 m²."}, {**B, "area_m2": 68})):
        duble = Duble()
        D.julgar_seguro(duble, a, b)
        checks = duble.states[0]["numeric_checks"]
        assert set(checks) == CHAVES_STATE and all(isinstance(v, bool) for v in checks.values()), checks


def _confere_baseline_seguro() -> None:
    for ruim in ({**A, "area_m2": None}, {**A, "preco": "510000"}, None):
        assert D.baseline_seguro(ruim, B) == {"acao": "revisar"} and D.baseline_seguro(B, ruim) == {"acao": "revisar"}
    assert D.baseline_seguro(A, B) == D.baseline(A, B) == {"acao": "unir"}


def _confere_fatos_da_falha() -> None:
    """Entrada inválida não tem fatos (ninguém recalcula); falha DEPOIS dos fatos os leva junto."""
    assert D.julgar_seguro(Duble(), {**A, "area_m2": None}, B)["fatos"] is None
    s = D.julgar_seguro(Duble(TimeoutError("x")), A, B)
    assert s["origem"] == "falha" and s["fatos"]["area_within_3_percent"] is True, s


def _confere_relatorio() -> None:
    """O caso do Codex: `area_m2: null` num par abortava o relatório inteiro (TypeError no baseline). Agora o
    relatório fecha, o par conta como `revisar` no Jev e no baseline, fora dos sinais do código, contado à parte."""
    sinais = {"mesmo_endereco": True, "mesma_area": True, "mesma_planta": True, "mesmo_preco": True}
    par = lambda i, a, b, mesmo, nota="dois corretores": {"id": f"BT-{i}", "a": a, "b": b, "mesmo_imovel": mesmo, "sinais": sinais, "nota": nota}  # noqa: E731
    casos = [par(1, A, B, True), par(2, {**A, "area_m2": None}, B, True), par(3, A, {**B, "preco": "510000"}, False),
             par(4, None, B, None), par(5, A, {**B, "cidade": "Santos"}, False, "bairros/cidades diferentes")]
    jev_real, R.Jev = R.Jev, lambda pasta: Duble()
    try:
        texto, resumo = R.secao_conjunto("bateria", {"versao": 0, "autor": "bateria", "casos": casos})
    finally:
        R.Jev = jev_real
    assert resumo["entrada_invalida"] == 3 and resumo["custo"]["falha"] == 3 and resumo["codigo_ok"], resumo
    assert "3 par(es) com entrada inválida" in texto and "BT-2, BT-3, BT-4" in texto
    for variante in (R.BASE, R.JEV):
        b = resumo["variantes"][variante]["_bruto"]
        assert b["revisou_sem"] == 2 and b["nulo_revisar"] == 1 and b["dup_unida"] == 1, (variante, b)


def testa_achados() -> tuple[int, list[str]]:
    """Parte D: cada caso roda isolado; devolve (casos, falhas) em vez de parar no primeiro erro."""
    casos = [(f"área — {nome}", lambda r=resto: _confere_area(*r)) for nome, *resto in AREAS]
    casos += [(f"bairro igual — {ba} × {bb}", lambda p=(ba, bb): _confere_bairro_igual(*p)) for ba, bb in BAIRROS_IGUAIS]
    casos += [(f"bairro indefinido — {ba} × {bb}", lambda p=(ba, bb): _confere_bairro_indefinido(*p)) for ba, bb in BAIRROS_INDEFINIDOS]
    casos += [
        ("cidade diferente separa sem chamada", lambda: _confere_cidade({**B, "cidade": "Santos"})),
        ("mesmo nome de bairro em cidades diferentes", lambda: _confere_cidade({**B, "bairro": "Mooca", "cidade": "Ribeirão Preto"})),
        ("bairro indefinido + quartos diferentes: o código separa (regra do LEIA-ME)",
         lambda: _confere_cidade({**B, "bairro": "Tatuapé", "quartos": 3})),
        ("state com as seis chaves booleanas", _confere_state),
        ("entrada inválida: baseline_seguro → revisar", _confere_baseline_seguro),
        ("entrada inválida: sem fatos; falha de chamada: com fatos", _confere_fatos_da_falha),
        ("entrada inválida não aborta o relatório", _confere_relatorio),
    ]
    falhas = []
    for nome, confere in casos:
        try:
            confere()
        except Exception as e:  # noqa: BLE001 — a bateria lista todas as falhas
            falhas.append(f"{nome}: {type(e).__name__}: {e}")
    return len(casos), falhas


if __name__ == "__main__":
    print(f"A. falha operacional → revisar: {testa_falha_operacional()} casos ok")
    print(f"B. política (grade): {testa_politica()} combinações ok")
    print(f"C. fatos do código, decisão sem chamada e teto: {testa_fatos_do_codigo()} checagens ok")
    total, falhas = testa_achados()
    print(f"D. achados da revisão (área rotulada, número brasileiro, bairro, entrada inválida): {total - len(falhas)}/{total} casos ok")
    for f in falhas:
        print(f"   FALHA {f}")
    sys.exit(1 if falhas else 0)
