"""Bateria do código da seleção de skill — roda sem chave e sem rede (`python testa_falhas.py`).

Por que existe: os conjuntos rotulados não exercitam o que é do CÓDIGO e custa caro quando falha. Com um dublê no
lugar do Jev, a bateria prova:
  A. falha operacional — resposta fora do contrato (bool no lugar de número, ID faltando, opção desconhecida,
     distribuição incompleta…) ou exceção de rede, em QUALQUER das cinco requisições: `selecionar_seguro` devolve
     "sem sugestão" com `falha` = True para aquele pedido, nunca uma skill; `selecionar` (baixo nível) levanta erro;
     quebra numa requisição que a variante não envia não a afeta;
  B. política — grade de `decidir`: cada variante só devolve skill com o SEU portão aberto; a grade também exibe o
     furo da receita (c devolve um vencedor cujo `fits` está abaixo do limiar) e mostra que c2 e d não o têm;
  C. entrada e encanamento — pedido/catálogo inválido levanta erro antes de qualquer chamada; pedido acima do teto
     não chama; cada variante envia exatamente as requisições de `ETAPAS`; a válvula não entra na shortlist;
  D. baseline e métricas do `run.py` em casos montados à mão.
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import perguntas as P  # noqa: E402
import run as R  # noqa: E402
import selecao as S  # noqa: E402

CATALOGO = json.loads((AQUI / "dados" / "skills.json").read_text(encoding="utf-8"))["casos"]
IDS = [s["id"] for s in CATALOGO]
PEDIDO = "Revisa o diff que eu acabei de fazer."
TOP = ["code-review", "simplify", "security-review"]


def formato(questions: dict) -> str:
    """De que requisição são estas perguntas (o dublê não recebe o nome da etapa, como a API)."""
    if "which" in questions:
        return "ampla_completa" if questions["which"]["criteria"][IDS[0]] == P.completa(CATALOGO[0]) else "ampla"
    if "rerank" in questions:
        return "rerank"
    return "fits_vencedor" if len(questions) == 1 else "todos"


class Duble:
    """Jev de mentira: monta uma resposta VÁLIDA para as perguntas recebidas, a partir de um roteiro.

    `ranking`  ordem das opções da Choice ampla (a 1ª vence; pode ser `none`); o resto do catálogo vem depois.
    `rerank`   vencedor da Choice `rerank` (padrão: a 1ª candidata).
    `fits`     {id: valor} dos Nouls `fits` (padrão 0,9); `portas` {nome: valor} (padrão: porta aberta).
    `quebra`   (etapa, função que estraga `answers`) ou (etapa, exceção).
    """

    def __init__(self, ranking=None, rerank=None, fits=None, portas=None, quebra=None):
        self.ranking, self.rerank, self.fits = ranking or TOP, rerank, fits or {}
        self.portas = portas or {"acts_on_user_system": 0.9, "would_follow_documented_procedure": 0.9, "prose_suffices": 0.1}
        self.quebra, self.etapas = quebra, []

    def _choice(self, opcoes: list[str], ordem: list[str]) -> dict:
        ordem = [o for o in ordem if o in opcoes] + [o for o in opcoes if o not in ordem]
        pesos = [2.0 ** -(k + 1) for k in range(len(ordem))]  # estritamente decrescente: a ordem É o ranking
        return {"type": "choice", "choice": ordem[0], "confidence": 0.6,
                "probabilities": {o: p / sum(pesos) for o, p in zip(ordem, pesos)}}

    def perguntar(self, state, questions):
        etapa = formato(questions)
        self.etapas.append(etapa)
        if self.quebra and self.quebra[0] == etapa and isinstance(self.quebra[1], Exception):
            raise self.quebra[1]
        answers = {}
        for q, p in questions.items():
            if q == "which":
                answers[q] = self._choice(list(p["criteria"]), self.ranking)
            elif q == "rerank":
                answers[q] = self._choice(list(p["criteria"]), [self.rerank] if self.rerank else [])
            elif q.startswith("fits."):
                answers[q] = {"type": "noul", "noul": self.fits.get(q[5:], 0.9)}
            else:
                answers[q] = {"type": "noul", "noul": self.portas[q[5:]]}
        if self.quebra and self.quebra[0] == etapa:
            self.quebra[1](answers)
        return {"model": "duble", "answers": answers}


def testa_falha_operacional() -> int:
    ok = S.selecionar_seguro(Duble(), PEDIDO, CATALOGO, etapas=S.MEDICAO_COM_A2)
    assert not ok["falha"] and all(ok["decisoes"][v]["skill"] == "code-review" for v in ("a", "b", "c", "c2", "d", "a2")), ok
    quebras = {
        "ampla": {
            "choice fora das opções": lambda a: a["which"].update(choice="skill-inventada"),
            "distribuição sem uma opção": lambda a: a["which"]["probabilities"].pop("rollback"),
            "distribuição com opção a mais": lambda a: a["which"]["probabilities"].update({"extra": 0.0}),
            "probabilidade bool": lambda a: a["which"]["probabilities"].update({"rollback": True}),
            "soma ≠ 1": lambda a: a["which"]["probabilities"].update({"rollback": 0.9}),
            "sem confiança": lambda a: a["which"].pop("confidence"),
            "tipo trocado": lambda a: a["which"].update(type="noul"),
            "ID faltando": lambda a: a.pop("which"),
        },
        "fits_vencedor": {
            "noul bool": lambda a: a["fits.code-review"].update(noul=True),
            "noul string": lambda a: a["fits.code-review"].update(noul="0.9"),
            "noul NaN": lambda a: a["fits.code-review"].update(noul=float("nan")),
            "noul fora de [0,1]": lambda a: a["fits.code-review"].update(noul=1.2),
            "ID faltando": lambda a: a.clear(),
        },
        "rerank": {
            "vencedor fora da shortlist": lambda a: a["rerank"].update(choice="rollback"),
            "fits de candidata faltando": lambda a: a.pop("fits.simplify"),
            "porta faltando": lambda a: a.pop("gate.prose_suffices"),
            "porta None": lambda a: a["gate.acts_on_user_system"].update(noul=None),
            "tipo trocado na porta": lambda a: a["gate.prose_suffices"].update(type="score"),
        },
        "todos": {
            "um dos 42 faltando": lambda a: a.pop("fits.rollback"),
            "um dos 42 negativo": lambda a: a["fits.rollback"].update(noul=-0.01),
            "answers vazio": lambda a: a.clear(),
        },
        "ampla_completa": {
            "choice fora das opções": lambda a: a["which"].update(choice="skill-inventada"),
            "confiança string": lambda a: a["which"].update(confidence="0.9"),
        },
    }
    n = 0
    for etapa, casos in quebras.items():
        for nome, mexe in [*casos.items(), ("timeout", TimeoutError("x")), ("cache faltando", RuntimeError("não gravada"))]:
            n += 1
            s = S.selecionar_seguro(Duble(quebra=(etapa, mexe)), PEDIDO, CATALOGO, etapas=S.MEDICAO_COM_A2)
            assert s["falha"] and s["skill"] is None and not s["decisoes"] and etapa in s["motivo"], (etapa, nome, s)
            assert R.classe(None, not R.vivo(s), {"skill": None, "aceitaveis": []}) == "sem_sugestao", "falha não é `null` certo"
            try:
                S.selecionar(Duble(quebra=(etapa, mexe)), PEDIDO, CATALOGO, etapas=S.MEDICAO_COM_A2)
            except Exception:  # noqa: BLE001 — o baixo nível tem de levantar
                pass
            else:
                raise AssertionError(f"`selecionar` não levantou em: {etapa} / {nome}")
            for v in [*P.VARIANTES, *P.INFORMATIVAS]:  # produção: só falha a variante que ENVIA a requisição quebrada
                s = S.selecionar_seguro(Duble(quebra=(etapa, mexe)), PEDIDO, CATALOGO, variante=v)
                assert s["falha"] == (etapa in S.ETAPAS[v]), (etapa, nome, v, s)
                assert s["falha"] or s["skill"] == "code-review", (etapa, nome, v, s)
    return n


def testa_politica() -> int:
    lim = P.LIMIAR
    baixo, alto = lim["fits"] / 2, (lim["fits"] + 1) / 2
    n = furos = 0
    for valores, venc, porta in itertools.product(itertools.product((baixo, lim["fits"], alto), repeat=3), TOP, (lim["porta"] / 2, lim["porta"], 0.9)):
        fits = dict(zip(TOP, valores))
        rerank = {"vencedor": venc, "conf": 0.5, "probs": {}, "fits": fits, "portas": {}, "porta": porta}
        d = S.decidir(rerank=rerank)
        n += 1
        maior = max(fits, key=fits.get)
        aberta, passa = porta >= lim["porta"], max(valores) >= lim["fits"]
        assert d["c"]["skill"] == (venc if aberta and passa else None), (fits, venc, porta, d)
        assert d["c2"]["skill"] == (venc if aberta and fits[venc] >= lim["fits"] else None), (fits, venc, porta, d)
        assert d["d"]["skill"] == (maior if aberta and passa else None), (fits, venc, porta, d)
        for v in ("c2", "d"):  # o que c2 e d devolvem SEMPRE passou no próprio portão
            assert d[v]["skill"] is None or fits[d[v]["skill"]] >= lim["fits"], (v, fits, d)
        if d["c"]["skill"] and fits[d["c"]["skill"]] < lim["fits"]:
            furos += 1  # o furo da receita: o portão passou por outro candidato
            assert d["c2"]["skill"] is None and d["d"]["skill"] == maior != venc
    assert furos > 0, "a grade tem de exibir o furo da receita"
    ampla = {"escolha": "code-review", "conf": 0.4, "p_nenhuma": 0.1, "shortlist": TOP, "probs": {}}
    for f, esperado in ((baixo, None), (lim["fits"], "code-review"), (alto, "code-review")):
        d = S.decidir(ampla=ampla, fits_vencedor=f)
        assert d["a"]["skill"] == "code-review" and d["b"]["skill"] == esperado, d
    d = S.decidir(ampla={**ampla, "escolha": None})
    assert d["a"]["skill"] is None and d["b"]["skill"] is None, d
    assert "b" not in S.decidir(ampla=ampla), "sem o `fits` do vencedor a variante b não decide (não vira None calado)"
    for f, esperado in ((lim["fits_todos"] / 2, None), (lim["fits_todos"], "rollback"), (0.99, "rollback")):
        assert S.decidir(todos={**dict.fromkeys(IDS, 0.0), "rollback": f})["e"]["skill"] == esperado
    assert S.decidir(todos=dict.fromkeys(IDS, 0.9))["e"]["skill"] == IDS[0], "empate fica com a ordem do catálogo"
    assert S.decidir(rerank={"vencedor": TOP[2], "fits": dict.fromkeys(TOP, 0.9), "porta": 0.9})["d"]["skill"] == TOP[0], "empate: ordem da shortlist"
    return n + 9


def testa_entrada_e_encanamento() -> int:
    invalidos = [("", CATALOGO), ("   ", CATALOGO), (None, CATALOGO), (PEDIDO, []), (PEDIDO, CATALOGO[:2]),
                 (PEDIDO, [*CATALOGO, CATALOGO[0]]), (PEDIDO, [*CATALOGO, {"id": P.NENHUMA, "nome": "x", "descricao": "y"}]),
                 (PEDIDO, [*CATALOGO, {"id": "Com Espaço", "nome": "x", "descricao": "y"}]),
                 (PEDIDO, [*CATALOGO, {"id": "sem-descricao", "nome": "x", "descricao": " "}]),
                 (PEDIDO, CATALOGO * 7)]
    for pedido, catalogo in invalidos:
        duble = Duble()
        for f in (S.selecionar, S.selecionar_seguro):
            try:
                f(duble, pedido, catalogo)
            except ValueError:
                pass
            else:
                raise AssertionError(f"entrada inválida aceita: {pedido!r} / {len(catalogo)} skills")
        assert not duble.etapas, "entrada inválida não chama o Jev"
    duble = Duble()
    s = S.selecionar_seguro(duble, "x" * (P.TETO_CARACTERES + 1), CATALOGO, etapas=S.MEDICAO)
    assert s["longo"] and s["skill"] is None and not s["falha"] and not duble.etapas, s
    # cada variante envia exatamente o que `ETAPAS` diz; `fits_vencedor` só quando a ampla escolhe skill
    for v in [*P.VARIANTES, *P.INFORMATIVAS]:
        duble = Duble()
        S.selecionar(duble, PEDIDO, CATALOGO, variante=v)
        assert tuple(duble.etapas) == S.ETAPAS[v], (v, duble.etapas)
    for variante, etapas in (("b", ("todos",)), ("zz", None), ("a", ("ampla", "inventada"))):
        duble = Duble()
        try:
            S.selecionar_seguro(duble, PEDIDO, CATALOGO, variante=variante, etapas=etapas)
        except ValueError:
            assert not duble.etapas
        else:
            raise AssertionError(f"variante/etapas inválidas aceitas: {variante}, {etapas}")
    duble = Duble(ranking=[P.NENHUMA, *TOP])
    s = S.selecionar(duble, PEDIDO, CATALOGO, variante="b")
    assert duble.etapas == ["ampla"] and s["skill"] is None, (duble.etapas, s)
    duble = Duble(ranking=[P.NENHUMA, *TOP])
    s = S.selecionar(duble, PEDIDO, CATALOGO, etapas=S.MEDICAO)
    assert duble.etapas == ["ampla", "rerank", "todos"], duble.etapas
    assert s["sinais"]["ampla"]["shortlist"] == TOP, "a válvula não entra na shortlist"
    assert s["decisoes"]["a"]["skill"] is None and s["decisoes"]["c"]["skill"] == "code-review", s["decisoes"]
    duble = Duble()
    S.selecionar(duble, PEDIDO, CATALOGO, etapas=S.MEDICAO_COM_A2)
    assert duble.etapas == list(S.MEDICAO_COM_A2), duble.etapas
    # as perguntas têm a forma esperada
    q = S.pedido_ampla(CATALOGO)["which"]
    assert len(q["criteria"]) == len(CATALOGO) + 1 and P.NENHUMA in q["criteria"]
    assert all(len(P.curta(s)) <= len(s["nome"]) + 2 + P.CURTA + 1 for s in CATALOGO)
    inteira = S.pedido_ampla(CATALOGO, inteira=True)["which"]
    assert inteira["instructions"] == q["instructions"] and inteira["criteria"][P.NENHUMA] == q["criteria"][P.NENHUMA]
    assert all(s["descricao"] in inteira["criteria"][s["id"]] for s in CATALOGO), "a2 leva a descrição inteira" 
    assert sorted(S.pedido_rerank(CATALOGO[:3])) == sorted(["rerank", *(f"fits.{i}" for i in IDS[:3]), *(f"gate.{k}" for k in P.PORTAS)])
    assert len(S.pedido_fits(CATALOGO)) == len(CATALOGO)
    assert S.pedido_fits(CATALOGO[:1]) == {k: v for k, v in S.pedido_fits(CATALOGO).items() if k == f"fits.{IDS[0]}"}, \
        "o Noul do vencedor é a MESMA pergunta nos três formatos"
    # porta: `prose_suffices` entra invertida
    q = S.pedido_rerank(CATALOGO[:3])
    r = Duble(portas={"acts_on_user_system": 0.0, "would_follow_documented_procedure": 0.0, "prose_suffices": 1.0}).perguntar({}, q)
    assert S.ler_rerank(r, q, IDS[:3])["porta"] == 0.0
    r = Duble(portas={"acts_on_user_system": 1.0, "would_follow_documented_procedure": 1.0, "prose_suffices": 0.0}).perguntar({}, q)
    assert S.ler_rerank(r, q, IDS[:3])["porta"] == 1.0
    return len(invalidos) + 18


def testa_baseline_e_metricas() -> int:
    assert S.baseline("abrir o pull request pelo terminal", CATALOGO, 0.0)["skill"] == "pr-open"
    assert S.baseline("xyzzy plugh", CATALOGO, 0.0)["skill"] is None, "sem palavra em comum não há skill"
    assert S.baseline("abrir o pull request pelo terminal", CATALOGO, 1e9)["skill"] is None, "abaixo do limiar = nenhuma"
    assert S._termos("Revisa o diff da revisão") == ["revis", "diff", "revis"]
    com = {"skill": "simplify", "aceitaveis": ["simplify", "refactor-safe"]}
    nulo = {"skill": None, "aceitaveis": []}
    esperado = [("simplify", False, com, "melhor"), ("refactor-safe", False, com, "aceitavel"), (None, False, com, "null_indevido"),
                ("rollback", False, com, "skill_errada"), (None, False, nulo, "nula_certa"), ("rollback", False, nulo, "skill_indevida"),
                (None, True, nulo, "sem_sugestao"), (None, True, com, "sem_sugestao")]
    for e, sem, c, k in esperado:
        assert R.classe(e, sem, c) == k, (e, sem, c, k)
    b = R.metricas([(e, sem, c) for e, sem, c, _ in esperado])["_bruto"]
    assert (b["n"], b["nulos"], b["com"]) == (8, 3, 5) and b["estrito"] == 2 / 8 and b["folgado"] == 3 / 8, b
    assert b["skill_indevida"] == 1 and b["null_indevido"] == 1 and b["skill_errada"] == 1 and b["sem_sugestao"] == 2, b
    assert R.familia({"nota": "difícil: duas próximas — diff recém-escrito"}) == "duas próximas"
    assert R.familia({"nota": "Pedido direto."}) == "fácil / outros"
    return len(esperado) + 7


def main() -> None:
    partes = [("A falha operacional", testa_falha_operacional), ("B política (grade de `decidir`)", testa_politica),
              ("C entrada e encanamento", testa_entrada_e_encanamento), ("D baseline e métricas", testa_baseline_e_metricas)]
    for nome, f in partes:
        print(f"{nome}: {f()} verificações ok")
    print("bateria ok")


if __name__ == "__main__":
    main()
