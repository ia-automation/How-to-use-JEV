"""Bateria do código do motivo de perda — roda sem chave e sem rede (`python testa_falhas.py`).

Por que existe: os conjuntos rotulados não exercitam o que é do CÓDIGO e custa caro quando falha. Com um dublê no
lugar do Jev, a bateria prova:
  A. falha operacional — resposta fora do contrato (bool no lugar de número, ID faltando, opção desconhecida,
     distribuição incompleta, `only_group` onde não existe…) ou exceção de rede, em QUALQUER das quatro requisições:
     `julgar_seguro` devolve `sem_informacao` + `revisar` com `origem: "falha"` para aquela conversa, nunca um motivo;
     `julgar` (baixo nível) levanta erro; quebra numa requisição que a variante não envia não a afeta; resposta
     rejeitada pelo contrato é tirada do cache (SÓ ela; falha de chamada não tira nada) e a quarentena falhar não tira
     a escalada;
  B. política — grade de `decidir`: grupo fraco → revisar; `only_group` ou folha fraca → só grupo; folha vencedora da
     Choice única fora do grupo de maior soma → só grupo; e as GUARDAS da regra 8 do briefing: nenhuma leitura da Choice
     fecha o lead com `atendimento` sem `blames_agency` em sim, nem com `concorrencia` sem `closed_elsewhere` em sim
     (empate exato no limiar é revisão, não sim); Noul alto nunca promove um grupo; `reason_stated` baixo manda
     revisar e não troca o grupo;
  C. entrada e encanamento — conversa inválida (vazia, nula, turno sem `de`, texto numérico…) levanta erro em
     `julgar` e vira falha DAQUELA conversa em `julgar_seguro`, sem chamada e sem abortar o lote do `run.py`;
     taxonomia inválida levanta erro nos dois (é do lote); conversa acima do
     teto não chama (revisar, origem `jev`); cada variante envia exatamente as requisições de `ETAPAS`; `only_group`
     entra em toda Choice de folhas menos na de `sem_informacao`; o state traz a última fala do cliente e a contagem
     de mensagens do corretor sem resposta;
  D. baseline e métricas do `run.py` em casos montados à mão (inclusive: revisão e falha nunca contam como acerto; o
     `sem_informacao` da falha não vira "sem_informacao certo").
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import motivo as MO  # noqa: E402
import perguntas as P  # noqa: E402
import run as R  # noqa: E402

TAX = json.loads((AQUI / "dados" / "taxonomia.json").read_text(encoding="utf-8"))["casos"]
POR_ID = {g["id"]: g for g in TAX}
PAI = MO.validar_taxonomia(TAX)
CONVERSA = [{"de": "cliente", "texto": "oi, vi o anúncio da casa"}, {"de": "corretor", "texto": "Olá! Quer visitar?"},
            {"de": "cliente", "texto": "fui ver, mas o quarto é pequeno demais"}, {"de": "corretor", "texto": "Tenho outra maior."},
            {"de": "corretor", "texto": "Posso mandar fotos?"}]
NOULS_OK = {"reason_stated": 0.9, "blames_agency": 0.1, "closed_elsewhere": 0.1}


def formato(questions: dict) -> str:
    """De que requisição são estas perguntas (o dublê não recebe o nome da etapa, como a API)."""
    if "group" in questions:
        return "tudo" if any(q.startswith("leaf.") for q in questions) else "grupo"
    return "unica" if "reason_stated" in questions else "folhas"


class Duble:
    """Jev de mentira: monta uma resposta VÁLIDA para as perguntas recebidas, a partir de um roteiro.

    `grupo`   vencedor das Choices `group` (com `p_grupo`); `folha` vencedora das Choices de folhas (ou `only_group`)
              com `p_folha`; na Choice única a folha vence com `p_folha` e o resto se divide.
    `nouls`   {nome: valor}; `quebra` (etapa, função que estraga `answers`) ou (etapa, exceção).
    """

    def __init__(self, grupo="imovel", folha="tamanho_planta", p_grupo=0.9, p_folha=0.9, nouls=None, quebra=None):
        self.grupo, self.folha, self.p_grupo, self.p_folha = grupo, folha, p_grupo, p_folha
        self.nouls, self.quebra, self.etapas, self.invalidados = nouls or NOULS_OK, quebra, [], []

    def invalidar(self, state, questions) -> bool:
        """Como `jevcache.Jev.invalidar`: registra QUAL pedido foi tirado do cache."""
        self.invalidados.append((state, questions))
        return True

    @staticmethod
    def _choice(opcoes: list[str], vencedora: str, p: float) -> dict:
        p = max(p, 1.0 / len(opcoes))  # a vencedora tem de ser a mais provável, senão a validação comum recusa (e deve)
        resto = (1 - p) / max(len(opcoes) - 1, 1)
        probs = {o: (p if o == vencedora else resto) for o in opcoes}
        return {"type": "choice", "choice": vencedora, "confidence": 0.6, "probabilities": probs}

    def perguntar(self, state, questions):
        etapa = formato(questions)
        self.etapas.append(etapa)
        if self.quebra and self.quebra[0] == etapa and isinstance(self.quebra[1], Exception):
            raise self.quebra[1]
        answers = {}
        for q, p in questions.items():
            opcoes = list(p.get("criteria") or [])
            if q == "group":
                answers[q] = self._choice(opcoes, self.grupo, self.p_grupo)
            elif q == "leaf" and etapa == "unica":
                answers[q] = self._choice(opcoes, self.folha, self.p_folha)
            elif q.startswith("leaf"):
                venc = self.folha if self.folha in opcoes else (P.SO_GRUPO if P.SO_GRUPO in opcoes else opcoes[0])
                answers[q] = self._choice(opcoes, venc, self.p_folha)
            else:
                answers[q] = {"type": "noul", "noul": self.nouls[q]}
        if self.quebra and self.quebra[0] == etapa:
            self.quebra[1](answers)
        return {"model": "duble", "answers": answers}


class DubleQuarentenaQuebrada(Duble):
    def invalidar(self, state, questions) -> bool:
        raise OSError("cache somente leitura")


def testa_falha_operacional() -> int:
    duble = Duble()
    ok = MO.julgar_seguro(duble, CONVERSA, TAX, etapas=MO.MEDICAO)
    assert ok["origem"] == "jev" and all(ok["decisoes"][v]["folha"] == "tamanho_planta" and not ok["decisoes"][v]["revisar"] for v in P.VARIANTES), ok
    assert not duble.invalidados, "resposta válida não sai do cache"
    quebras = {
        "grupo": {
            "choice fora das opções": lambda a: a["group"].update(choice="grupo_inventado"),
            "choice é uma folha": lambda a: a["group"].update(choice="tamanho_planta"),
            "distribuição sem uma opção": lambda a: a["group"]["probabilities"].pop("preco"),
            "probabilidade bool": lambda a: a["group"]["probabilities"].update({"preco": True}),
            "soma ≠ 1": lambda a: a["group"]["probabilities"].update({"preco": 0.9}),
            "sem confiança": lambda a: a["group"].pop("confidence"),
            "tipo trocado": lambda a: a["group"].update(type="noul"),
            "noul bool": lambda a: a["blames_agency"].update(noul=True),
            "noul string": lambda a: a["reason_stated"].update(noul="0.9"),
            "noul NaN": lambda a: a["closed_elsewhere"].update(noul=float("nan")),
            "noul fora de [0,1]": lambda a: a["reason_stated"].update(noul=1.2),
            "noul faltando": lambda a: a.pop("closed_elsewhere"),
            "ID faltando": lambda a: a.pop("group"),
        },
        "folhas": {
            "folha de outro grupo": lambda a: a["leaf"].update(choice="preco_acima_orcamento"),
            "distribuição com opção a mais": lambda a: a["leaf"]["probabilities"].update({"extra": 0.0}),
            "confiança string": lambda a: a["leaf"].update(confidence="0.9"),
            "answers vazio": lambda a: a.clear(),
        },
        "unica": {
            "choice é `only_group`": lambda a: a["leaf"].update(choice=P.SO_GRUPO),
            "distribuição sem uma folha": lambda a: a["leaf"]["probabilities"].pop("adiou_sem_motivo"),
            "probabilidade negativa": lambda a: a["leaf"]["probabilities"].update({"adiou_sem_motivo": -0.01}),
            "noul faltando": lambda a: a.pop("reason_stated"),
        },
        "tudo": {
            "uma Choice de folhas faltando": lambda a: a.pop("leaf.preco"),
            "`only_group` em sem_informacao": lambda a: a["leaf.sem_informacao"].update(choice=P.SO_GRUPO, probabilities={**a["leaf.sem_informacao"]["probabilities"], P.SO_GRUPO: 0.0}),
            "grupo com tipo trocado": lambda a: a["group"].update(type="score"),
            "noul None": lambda a: a["blames_agency"].update(noul=None),
        },
    }
    n = 0
    for etapa, casos in quebras.items():
        for nome, mexe in [*casos.items(), ("timeout", TimeoutError("x")), ("cache faltando", RuntimeError("não gravada"))]:
            n += 1
            duble = Duble(quebra=(etapa, mexe))
            s = MO.julgar_seguro(duble, CONVERSA, TAX, etapas=MO.MEDICAO)
            assert s["origem"] == "falha" and s["grupo"] == P.SEM_INFORMACAO and s["folha"] is None and s["revisar"], (etapa, nome, s)
            assert not s["decisoes"] and etapa in s["motivo"] and not s["invalida"], (etapa, nome, s)
            # quarentena: SÓ o pedido rejeitado pelo contrato sai do cache; falha de chamada (exceção) não tira nada
            if isinstance(mexe, Exception):
                assert not duble.invalidados and "cache" not in s["motivo"], (etapa, nome, duble.invalidados)
            else:
                assert len(duble.invalidados) == 1 and "tirada do cache" in s["motivo"], (etapa, nome, duble.invalidados, s["motivo"])
                st, q = duble.invalidados[0]
                assert st == MO.state_de(CONVERSA) and formato(q) == etapa, (etapa, nome, formato(q))
                s2 = MO.julgar_seguro(DubleQuarentenaQuebrada(quebra=(etapa, mexe)), CONVERSA, TAX, etapas=MO.MEDICAO)
                assert s2["origem"] == "falha" and s2["revisar"] and "quarentena falhou" in s2["motivo"], (etapa, nome, s2)
            d = R.escolha(s, {"grupo": P.SEM_INFORMACAO, "folha": "sumiu_sem_resposta", "aceitaveis": []}, "a", TAX)
            assert R.classe(d, {"grupo": P.SEM_INFORMACAO, "folha": "sumiu_sem_resposta", "aceitaveis": []}) == "falha", "falha não é `sem_informacao` certo"
            try:
                MO.julgar(Duble(quebra=(etapa, mexe)), CONVERSA, TAX, etapas=MO.MEDICAO)
            except Exception:  # noqa: BLE001 — o baixo nível tem de levantar
                pass
            else:
                raise AssertionError(f"`julgar` não levantou em: {etapa} / {nome}")
            for v in P.VARIANTES:  # produção: só falha a variante que ENVIA a requisição quebrada
                s = MO.julgar_seguro(Duble(quebra=(etapa, mexe)), CONVERSA, TAX, variante=v)
                assert (s["origem"] == "falha") == (etapa in MO.ETAPAS[v]), (etapa, nome, v, s)
                assert s["origem"] == "falha" or s["folha"] == "tamanho_planta", (etapa, nome, v, s)
    return n


def _sinais(grupo="imovel", folha="tamanho_planta", p_grupo=0.9, p_folha=0.9, nouls=None, folha_unica=None, p_unica=None):
    """Sinais validados das quatro requisições, como `julgar` os monta, a partir do dublê."""
    d = Duble(grupo, folha, p_grupo, p_folha, nouls)
    g = MO.ler_grupo(d.perguntar({}, MO.pedido_grupo(TAX)), MO.pedido_grupo(TAX), TAX)
    f = MO.ler_folhas(d.perguntar({}, MO.pedido_folhas(POR_ID[grupo])), MO.pedido_folhas(POR_ID[grupo]), POR_ID[grupo])
    du = Duble(grupo, folha_unica or folha, p_grupo, p_unica if p_unica is not None else p_folha, nouls)
    u = {**MO.ler_unica(du.perguntar({}, MO.pedido_unica(TAX)), MO.pedido_unica(TAX), TAX, PAI), "pai": PAI}
    t = MO.ler_tudo(d.perguntar({}, MO.pedido_tudo(TAX)), MO.pedido_tudo(TAX), TAX)
    return g, f, u, t


def testa_politica() -> int:
    lim = P.LIMIAR
    n = 0
    # grupo fraco → revisar sem folha (a, c pela Choice `group`; b pela soma das folhas do grupo); forte → folha
    for pg, revisa in ((lim["grupo"] / 2, True), (lim["grupo"], False), (0.95, False)):
        out = MO.decidir(*_sinais(p_grupo=pg))
        for v in ("a", "c"):
            d = out[v]
            assert d["grupo"] == "imovel" and d["revisar"] == revisa and (d["folha"] is None) == revisa, (v, pg, d)
            n += 1
    for pu, revisa in ((lim["grupo"] / 4, True), (0.95, False)):  # soma do grupo da folha vencedora ≈ pu + resto diluído
        d = MO.decidir(*_sinais(p_unica=pu))["b"]
        assert d["grupo"] == "imovel" and d["revisar"] == revisa and (d["folha"] is None) == revisa, (pu, d)
        n += 1
    # `only_group` → só grupo, sem revisar (a, c); folha fraca → só grupo
    out = MO.decidir(*_sinais(folha=P.SO_GRUPO, folha_unica="tamanho_planta"))
    assert out["a"]["folha"] is None and out["c"]["folha"] is None and not out["a"]["revisar"] and not out["c"]["revisar"], out
    assert out["b"]["folha"] == "tamanho_planta", "a Choice única não tem `only_group`; o roteiro deu folha forte"
    for pf, folha in ((lim["folha"] / 2, None), (lim["folha"], "tamanho_planta")):
        out = MO.decidir(*_sinais(p_folha=pf))
        assert out["a"]["folha"] == folha and out["c"]["folha"] == folha and not out["a"]["revisar"], (pf, out)
        n += 1
    for pu, folha in ((lim["folha_unica"] / 2, None), (lim["folha_unica"], "tamanho_planta")):
        out = MO.decidir(*_sinais(p_unica=pu))
        assert out["b"]["folha"] == folha and out["b"]["grupo"] == "imovel", (pu, out)
        n += 1
    # Choice única: folha vencedora de um grupo, soma maior em outro → grupo manda, só grupo. Monta na mão: 0,35 numa
    # folha de `preco`, 0,2 em cada uma das 3 folhas de `localizacao` (0,6), resto 0.
    u = {**MO.ler_unica({"answers": {"leaf": {"type": "choice", "choice": "preco_acima_orcamento", "confidence": 0.3,
                                                "probabilities": {**dict.fromkeys(PAI, 0.0), "preco_acima_orcamento": 0.35, "distancia_deslocamento": 0.2,
                                                                  "entorno_seguranca": 0.2, "bairro_nao_desejado": 0.25}},
                                      **{k: {"type": "noul", "noul": v} for k, v in NOULS_OK.items()}}},
                        MO.pedido_unica(TAX), TAX, PAI), "pai": PAI}
    d = MO.decidir(unica=u)["b"]
    assert d["grupo"] == "localizacao" and d["folha"] is None and not d["revisar"], d
    n += 1
    # GUARDAS (regra 8): atendimento sem `blames_agency` → só grupo + revisar; concorrencia sem `closed_elsewhere` idem.
    # No limiar exato (0,50 = empate) a guarda DISPARA (revisão do Codex 2026-10-01: antes a bateria exigia liberar).
    for grupo, folha, noul in ((P.ATENDIMENTO, "demora_resposta", "blames_agency"), (P.CONCORRENCIA, "outra_imobiliaria", "closed_elsewhere")):
        for valor, fecha in ((lim["guarda"] / 2, False), (lim["guarda"], False), (lim["guarda"] + 0.01, True), (0.95, True)):
            out = MO.decidir(*_sinais(grupo, folha, nouls={**NOULS_OK, noul: valor}))
            for v in P.VARIANTES:
                d = out[v]
                assert d["grupo"] == grupo, (v, d)
                assert (d["folha"] == folha and not d["revisar"]) if fecha else (d["folha"] is None and d["revisar"]), (grupo, noul, valor, v, d)
                n += 1
        # a guarda de um grupo não mexe no outro, e Noul alto NUNCA promove: grupo `imovel` com os dois Nouls em 0,99 fica `imovel`
    out = MO.decidir(*_sinais(nouls={"reason_stated": 0.9, "blames_agency": 0.99, "closed_elsewhere": 0.99}))
    assert all(out[v]["grupo"] == "imovel" and out[v]["folha"] == "tamanho_planta" and not out[v]["revisar"] for v in P.VARIANTES), out
    out = MO.decidir(*_sinais(P.ATENDIMENTO, "demora_resposta", nouls={**NOULS_OK, "blames_agency": 0.9, "closed_elsewhere": 0.0}))
    assert all(out[v]["folha"] == "demora_resposta" and not out[v]["revisar"] for v in P.VARIANTES), "`closed_elsewhere` não guarda `atendimento`"
    # `reason_stated` baixo com motivo → revisar, grupo mantido (não vira sem_informacao); com `sem_informacao` não dispara
    out = MO.decidir(*_sinais(nouls={**NOULS_OK, "reason_stated": lim["sem_motivo"] / 2}))
    assert all(out[v]["grupo"] == "imovel" and out[v]["revisar"] for v in P.VARIANTES), out
    out = MO.decidir(*_sinais(P.SEM_INFORMACAO, "sumiu_sem_resposta", nouls={**NOULS_OK, "reason_stated": 0.0}))
    assert all(out[v]["grupo"] == P.SEM_INFORMACAO and out[v]["folha"] == "sumiu_sem_resposta" and not out[v]["revisar"] for v in P.VARIANTES), out
    # sinais parciais: só decide a variante cujos sinais chegaram (não vira None calado)
    g, f, u, t = _sinais()
    assert set(MO.decidir(grupo=g)) == set() and set(MO.decidir(grupo=g, folhas=f)) == {"a"} and set(MO.decidir(unica=u)) == {"b"} and set(MO.decidir(tudo=t)) == {"c"}
    # limiares alternativos passam por `limiares` (é o que a varredura do run.py usa)
    out = MO.decidir(*_sinais(p_grupo=0.6), limiares={**lim, "grupo": 0.7})
    assert out["a"]["revisar"] and out["c"]["revisar"] and not out["b"]["revisar"], "b lê a soma das folhas, não a Choice `group`"
    return n + 8


def testa_entrada_e_encanamento() -> int:
    # Conversa inválida: `julgar` levanta; `julgar_seguro` devolve falha DAQUELA conversa (revisão do Codex 2026-10-01:
    # relançar abortava o lote do run.py). Um turno só continua válido: o LEIA-ME descreve o dado (4–12 turnos), não
    # exige do consumidor.
    gab = {"grupo": "preco", "folha": "custos_extras", "aceitaveis": ["custos_extras"]}
    conversas = [[], None, "oi", {"de": "cliente", "texto": "oi"}, ["oi"], [None], [{"de": "cliente", "texto": " "}],
                 [{"de": "cliente", "texto": ""}], [{"de": "vendedor", "texto": "oi"}], [{"de": "cliente"}], [{"texto": "oi"}],
                 [{"de": None, "texto": "oi"}], [{"de": "cliente", "texto": 123}], [{"de": "cliente", "texto": None}],
                 [{"de": "cliente", "texto": ["oi"]}], [*CONVERSA, {"de": "corretor", "texto": "   "}], [*CONVERSA, "tchau"]]
    for conversa in conversas:
        duble = Duble()
        try:
            MO.julgar(duble, conversa, TAX)
        except MO.ConversaInvalida:
            pass
        else:
            raise AssertionError(f"conversa inválida aceita: {conversa!r}")
        s = MO.julgar_seguro(duble, conversa, TAX, etapas=MO.MEDICAO)
        assert s["origem"] == "falha" and s["invalida"] and s["grupo"] == P.SEM_INFORMACAO and s["folha"] is None and s["revisar"], (conversa, s)
        assert not s["decisoes"] and not s["etapas"] and "entrada inválida" in s["motivo"], (conversa, s)
        assert not duble.etapas and not duble.invalidados, "conversa inválida não chama o Jev nem mexe no cache"
        caso = {"id": "X", "conversa": conversa, **gab}
        for linha in R.LINHAS:  # contada à parte em todas as linhas, inclusive no baseline (que leria a conversa)
            assert R.classe(R.escolha(s, caso, linha, TAX), caso) == "falha", (linha, conversa)
    # o lote do run.py segue: uma falha por conversa inválida (inclusive caso sem `conversa`), nenhuma chamada
    lote = [{"id": f"X{k}", "conversa": c, **gab} for k, c in enumerate(conversas)] + [{"id": "X_sem", **gab}]
    saidas = R.rodar(lote, TAX)
    assert len(saidas) == len(lote) and all(s["origem"] == "falha" and s["invalida"] and not s["chamadas"] for s in saidas), saidas
    assert R.metricas([(R.escolha(s, c, "c", TAX), c) for s, c in zip(saidas, lote)])["_bruto"]["falha"] == len(lote)
    # Taxonomia inválida é do LOTE: levanta nos dois níveis (o run.py a valida uma vez antes de começar)
    taxonomias = [[], [TAX[0]], [*TAX, TAX[0]], [{**TAX[0], "folhas": []}, *TAX[1:]], [{**TAX[0], "id": P.SO_GRUPO}, *TAX[1:]],
                  [{**TAX[0], "folhas": [{"id": "Com Espaço", "nome": "x", "descricao": "y"}]}, *TAX[1:]],
                  [{**TAX[0], "folhas": [{"id": "financiamento_negado", "nome": "x", "descricao": "y"}]}, *TAX[1:]],
                  [g for g in TAX if g["id"] != P.SEM_INFORMACAO]]
    for tax in taxonomias:
        duble = Duble()
        for f in (MO.julgar, MO.julgar_seguro):
            try:
                f(duble, CONVERSA, tax)
            except MO.ConversaInvalida:
                raise AssertionError(f"taxonomia inválida tratada como conversa: {len(tax)} grupos")
            except ValueError:
                pass
            else:
                raise AssertionError(f"taxonomia inválida aceita: {len(tax)} grupos")
        assert not duble.etapas, "taxonomia inválida não chama o Jev"
    invalidos = conversas + taxonomias
    duble = Duble()
    s = MO.julgar_seguro(duble, [{"de": "cliente", "texto": "x" * (P.TETO_CARACTERES + 1)}], TAX, etapas=MO.MEDICAO)
    assert s["longa"] and s["grupo"] == P.SEM_INFORMACAO and s["folha"] is None and s["revisar"] and s["origem"] == "jev" and not duble.etapas, s
    # cada variante envia exatamente o que `ETAPAS` diz; `folhas` leva as folhas do grupo vencedor
    for v in P.VARIANTES:
        duble = Duble(grupo="preco", folha="custos_extras")
        s = MO.julgar(duble, CONVERSA, TAX, variante=v)
        assert tuple(duble.etapas) == MO.ETAPAS[v] and s["folha"] == "custos_extras" and s["grupo"] == "preco", (v, duble.etapas, s)
    for variante, etapas in (("a", ("unica",)), ("zz", None), ("a", ("grupo", "inventada")), ("b", ("unica", "folhas"))):
        duble = Duble()
        try:
            MO.julgar_seguro(duble, CONVERSA, TAX, variante=variante, etapas=etapas)
        except ValueError:
            assert not duble.etapas
        else:
            raise AssertionError(f"variante/etapas inválidas aceitas: {variante}, {etapas}")
    duble = Duble()
    MO.julgar(duble, CONVERSA, TAX, etapas=MO.MEDICAO)
    assert duble.etapas == list(MO.MEDICAO), duble.etapas
    # as perguntas têm a forma esperada
    q = MO.pedido_grupo(TAX)
    assert set(q) == {"group", *P.NOULS} and list(q["group"]["criteria"]) == [g["id"] for g in TAX]
    for g in TAX:
        c = MO.pedido_folhas(g)["leaf"]["criteria"]
        assert (P.SO_GRUPO in c) == (g["id"] != P.SEM_INFORMACAO) and all(f["id"] in c for f in g["folhas"]), g["id"]
        assert g["nome"] in MO.pedido_folhas(g)["leaf"]["instructions"]["question"], "a premissa leva o nome do grupo"
    u = MO.pedido_unica(TAX)["leaf"]["criteria"]
    assert list(u) == list(PAI) and P.SO_GRUPO not in u and all(TAX[0]["folhas"][0]["descricao"] in u[TAX[0]["folhas"][0]["id"]] for _ in [0])
    t = MO.pedido_tudo(TAX)
    assert set(t) == {"group", *P.NOULS, *(f"leaf.{g['id']}" for g in TAX)} and t["group"] == q["group"], "a Choice do grupo é a MESMA nos dois formatos"
    assert t["leaf.preco"] == MO.pedido_folhas(POR_ID["preco"])["leaf"], "a Choice de folhas é a MESMA em `folhas` e `tudo`"
    assert P.SEM_INFORMACAO in q["group"]["criteria"] and "guess" in q["group"]["criteria"][P.SEM_INFORMACAO]
    # state: papéis em inglês, última fala do cliente, contagem de mensagens do corretor sem resposta
    s = MO.state_de(CONVERSA)
    assert [t["from"] for t in s["conversation"]] == ["customer", "agent", "customer", "agent", "agent"]
    assert s["last_customer_message"] == "fui ver, mas o quarto é pequeno demais" and s["agent_messages_after_last_customer_message"] == 2
    s = MO.state_de([{"de": "corretor", "texto": "Oi!"}])
    assert s["last_customer_message"] is None and s["agent_messages_after_last_customer_message"] == 1
    return len(invalidos) + 18


def testa_baseline_e_metricas() -> int:
    b = MO.baseline([{"de": "cliente", "texto": "o banco negou meu financiamento, não aprovou o crédito"}], TAX)
    assert b["folha"] == "financiamento_negado" and b["grupo"] == "credito_documentacao", b
    b = MO.baseline([{"de": "cliente", "texto": "oi"}, {"de": "corretor", "texto": "Custa R$ 900 mil."}, {"de": "corretor", "texto": "Alô?"}], TAX)
    assert b["folha"] == "sumiu_apos_valor", b
    b = MO.baseline([{"de": "cliente", "texto": "oi"}, {"de": "corretor", "texto": "Olá!"}, {"de": "corretor", "texto": "Alô?"}], TAX)
    assert b["folha"] == "sumiu_sem_resposta", b
    b = MO.baseline([{"de": "cliente", "texto": "oi"}, {"de": "corretor", "texto": "Olá!"}], TAX)
    assert b["folha"] == "adiou_sem_motivo", b
    b = MO.baseline([{"de": "corretor", "texto": "o banco negou o financiamento"}, {"de": "cliente", "texto": "ok"}], TAX)
    assert b["grupo"] == P.SEM_INFORMACAO, "só a fala do cliente conta no baseline"
    assert MO._termos("O valor pedido está acima do orçamento") == {"valor", "pedid", "acima", "orcam"}
    # classes
    com = {"grupo": "preco", "folha": "negociacao_frustrada", "aceitaveis": ["negociacao_frustrada", "preco_acima_orcamento"]}
    cruz = {"grupo": "atendimento", "folha": "demora_resposta", "aceitaveis": ["demora_resposta", "outra_imobiliaria"]}
    nulo = {"grupo": "preco", "folha": None, "aceitaveis": ["preco_acima_orcamento", "custos_extras"]}
    nulo_vazio = {"grupo": "imovel", "folha": None, "aceitaveis": []}
    si = {"grupo": P.SEM_INFORMACAO, "folha": "sumiu_apos_valor", "aceitaveis": ["sumiu_apos_valor"]}
    dec = lambda g, f, r=False, falha=False: {"grupo": g, "folha": f, "revisar": r, "falha": falha}  # noqa: E731
    esperado = [(dec("preco", "negociacao_frustrada"), com, "folha"), (dec("preco", "preco_acima_orcamento"), com, "aceitavel"),
                (dec("preco", "custos_extras"), com, "folha_errada"), (dec("preco", None), com, "absteve"),
                (dec("imovel", "tamanho_planta"), com, "grupo_errado"), (dec("imovel", None), com, "grupo_errado"),
                (dec("concorrencia", "outra_imobiliaria"), cruz, "aceitavel"), (dec("concorrencia", "direto_proprietario"), cruz, "grupo_errado"),
                (dec("preco", None), nulo, "so_grupo"), (dec("preco", "custos_extras"), nulo, "aceitavel"), (dec("preco", "negociacao_frustrada"), nulo, "folha_errada"),
                (dec("imovel", None), nulo_vazio, "so_grupo"), (dec("imovel", "falta_item"), nulo_vazio, "folha_errada"),
                (dec(P.SEM_INFORMACAO, "sumiu_apos_valor"), si, "folha"), (dec(P.SEM_INFORMACAO, "sumiu_sem_resposta"), si, "folha_errada"),
                (dec("preco", "preco_acima_orcamento"), si, "motivo_inventado"), (dec("preco", None), si, "motivo_inventado"),
                (dec("preco", "preco_acima_orcamento", r=True), si, "revisar"), (dec("preco", "negociacao_frustrada", r=True), com, "revisar"),
                (dec(P.SEM_INFORMACAO, None, r=True, falha=True), si, "falha"), (dec(P.SEM_INFORMACAO, None, r=True, falha=True), com, "falha")]
    for d, c, k in esperado:
        assert R.classe(d, c) == k, (d, c, k, R.classe(d, c))
    b = R.metricas([(d, c) for d, c, _ in esperado])["_bruto"]
    assert b["n"] == 21 and b["nulos"] == 5 and b["sem_info"] == 6, b
    assert b["folha"] == 2 and b["aceitavel"] == 3 and b["so_grupo"] == 2 and b["absteve"] == 1 and b["folha_errada"] == 4, b
    assert b["grupo_errado"] == 3 and b["motivo_inventado"] == 2 and b["grupo_errado_auto"] == 5 and b["revisar"] == 2 and b["falha"] == 2, b
    assert abs(b["estrito"] - 4 / 21) < 1e-9 and abs(b["folgado"] - 7 / 21) < 1e-9, b
    assert b["si_certo"] == 1 and b["automatizados"] == 17, "falha com `sem_informacao` não é sem_info certo"
    assert R.familia({"nota": "difícil: dois motivos — o preço é contornável"}) == "dois motivos"
    assert R.familia({"nota": "fácil: crédito negado"}) == "fácil / outros"
    return len(esperado) + 13


def main() -> None:
    partes = [("A falha operacional", testa_falha_operacional), ("B política (grade de `decidir` e guardas)", testa_politica),
              ("C entrada e encanamento", testa_entrada_e_encanamento), ("D baseline e métricas", testa_baseline_e_metricas)]
    for nome, f in partes:
        print(f"{nome}: {f()} verificações ok")
    print("bateria ok")


if __name__ == "__main__":
    main()
