"""Bateria do código do opt-out/LGPD — roda sem chave e sem rede (`python testa_falhas.py`).

Por que existe (revisão do Codex, 2026-10-01): três defeitos estavam no CÓDIGO, não no modelo, e os conjuntos
rotulados não exercitam nenhum deles (zero falha de rede, zero bloqueio pendente, um só caso de exclusão parcial).
A bateria prova, com um dublê no lugar do Jev:
  A. falha operacional — resposta falsa (bool no lugar de número, ID faltando, Choice sem distribuição…), exceção
     de rede simulada ou entrada inválida: `guardar_seguro` devolve `revisar` com motivo "falha operacional" para
     AQUELA mensagem, nunca `seguir`, e o lote não aborta; `julgar` (baixo nível) continua levantando erro;
  B. guarda não dispensa obrigação — grade com os três valores de cada Noul (não / dúvida / sim) × as cinco opções
     da Choice × dois níveis de confiança: nenhum Noul de guarda tira uma decisão de bloqueio para `bloqueia=False`
     nem para `seguir`; guarda só move para `revisar`; pedido de titular ou opt-out em dúvida ou acima do limiar
     nunca sai `seguir`;
  C. bloqueio pendente — `bloqueia=None` num pedido aberto conta como obrigação pela metade e fica fora da
     cobertura automática da curva.
O que se testa aqui é código nosso, não o modelo: nenhum número desta bateria é medição do Jev.
"""
from __future__ import annotations

import copy
import itertools
import math
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import optout as O  # noqa: E402
import perguntas as P  # noqa: E402
import run as R  # noqa: E402

GUARDAS = ["wants_contact_to_continue", "stop_without_object", "about_another_contact"]
PRINCIPAIS = [q for q in P.NOULS if q not in GUARDAS]
BAIXO = {q: P.FAIXA[q][0] / 2 for q in P.NOULS}                      # dentro do "não"
DUVIDA = {q: (P.FAIXA[q][0] + P.FAIXA[q][1]) / 2 for q in P.NOULS}  # dentro da faixa do meio
ALTO = {q: (P.FAIXA[q][1] + 1) / 2 for q in P.NOULS}                # dentro do "sim"


def resposta(tipo: str = "none", conf: float = 1.0, **nouls: float) -> dict:
    """Resposta VÁLIDA no formato da API. Sem argumentos: tudo baixo e Choice `none` → `seguir` (o pior destino
    possível para uma falha tolerada: se a validação deixar passar, a bateria vê `seguir`)."""
    resto = (1.0 - conf) / (len(P.TIPO_DA_OPCAO) - 1)
    probs = {o: (conf if o == tipo else resto) for o in P.TIPO_DA_OPCAO}
    return {"model": "duble", "answers": {
        "lgpd_type": {"type": "choice", "choice": tipo, "confidence": conf, "probabilities": probs},
        **{q: {"type": "noul", "noul": nouls.get(q, BAIXO[q])} for q in P.NOULS}}}


class Duble:
    """Jev de mentira: devolve a resposta dada ou levanta a exceção dada; por mensagem, se `por_mensagem`."""

    def __init__(self, padrao=None, por_mensagem: dict | None = None):
        self.padrao, self.por_mensagem = padrao if padrao is not None else resposta(), por_mensagem or {}

    def perguntar(self, state, questions):
        saida = self.por_mensagem.get(state["message"], self.padrao)
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


# (nome, corrupção sobre uma resposta válida que daria `seguir`)
RESPOSTAS_FALSAS = [
    ("Noul bool False no lugar de número (viraria 0.0 → seguir)", _mexe(["answers", "opt_out", "noul"], False)),
    ("Noul bool True no lugar de número", _mexe(["answers", "lgpd_request", "noul"], True)),
    ("Noul string", _mexe(["answers", "opt_out", "noul"], "0.05")),
    ("Noul None", _mexe(["answers", "temporary_pause", "noul"], None)),
    ("Noul NaN", _mexe(["answers", "opt_out", "noul"], math.nan)),
    ("Noul infinito", _mexe(["answers", "lgpd_request", "noul"], math.inf)),
    ("Noul fora de [0, 1] (1.5)", _mexe(["answers", "opt_out", "noul"], 1.5)),
    ("Noul negativo", _mexe(["answers", "stop_without_object", "noul"], -0.1)),
    ("Noul sem o campo `noul`", _mexe(["answers", "opt_out", "noul"], apaga=True)),
    ("ID de Noul principal faltando", _mexe(["answers", "opt_out"], apaga=True)),
    ("ID de guarda faltando", _mexe(["answers", "wants_contact_to_continue"], apaga=True)),
    ("ID da Choice faltando", _mexe(["answers", "lgpd_type"], apaga=True)),
    ("discriminador `type` trocado (Noul que volta como choice)", _mexe(["answers", "opt_out", "type"], "choice")),
    ("resposta de um ID que não é objeto", _mexe(["answers", "lgpd_request"], 0.01)),
    ("Choice sem distribuição", _mexe(["answers", "lgpd_type", "probabilities"], apaga=True)),
    ("Choice com distribuição vazia", _mexe(["answers", "lgpd_type", "probabilities"], {})),
    ("Choice com distribuição incompleta", _mexe(["answers", "lgpd_type", "probabilities"], {"none": 1.0})),
    ("Choice com distribuição que não soma 1",
     _mexe(["answers", "lgpd_type", "probabilities"], {o: 0.5 for o in P.TIPO_DA_OPCAO})),
    ("Choice com probabilidade bool", _mexe(["answers", "lgpd_type", "probabilities", "none"], True)),
    ("Choice com vencedor fora das opções", _mexe(["answers", "lgpd_type", "choice"], "portability")),
    ("Choice sem confiança", _mexe(["answers", "lgpd_type", "confidence"], apaga=True)),
    ("Choice com confiança bool", _mexe(["answers", "lgpd_type", "confidence"], True)),
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
ENTRADAS = [("mensagem vazia", ""), ("mensagem só com espaço", "   "), ("mensagem None", None), ("mensagem não textual", 123)]


def _confere_falha(nome: str, jev, mensagem, etapa: str, falhas: list) -> None:
    """Uma falha: o invólucro devolve `revisar` marcado; o baixo nível levanta."""
    d = O.guardar_seguro(jev, mensagem)
    if d["acao"] != "revisar" or not d.get("falha") or d["bloqueia"] is not None \
            or not d["motivo"].startswith(f"falha operacional: {etapa} ("):
        falhas.append(f"A {nome}: guardar_seguro devolveu {d['acao']!r} / {d['motivo']!r}")
    try:
        O.julgar(jev, mensagem)
        falhas.append(f"A {nome}: julgar (baixo nível) não levantou erro")
    except Exception:  # noqa: BLE001 — qualquer exceção serve: o ponto é não devolver decisão
        pass


def bateria_falhas(falhas: list) -> int:
    n = 0
    assert O.guardar_seguro(Duble(), "oi, tudo bem?")["acao"] == "seguir", "o dublê válido tem de dar `seguir`"
    for nome, corrompe in RESPOSTAS_FALSAS:
        _confere_falha(nome, Duble(corrompe(copy.deepcopy(resposta()))), "oi", "resposta inválida", falhas)
        n += 1
    for nome, inteira in RESPOSTAS_INTEIRAS:
        jev = Duble()
        jev.padrao = inteira  # direto: o construtor trocaria None pela resposta válida
        _confere_falha(nome, jev, "oi", "resposta inválida", falhas)
        n += 1
    for nome, erro in EXCECOES:
        _confere_falha(nome, Duble(erro), "para de me mandar mensagem", "chamada", falhas)
        n += 1
    for nome, mensagem in ENTRADAS:
        _confere_falha(nome, Duble(), mensagem, "entrada inválida", falhas)
        n += 1

    # o lote não aborta: `run.rodar` com o dublê no lugar do cliente; só as mensagens com falha saem `revisar`
    casos = [{"mensagem": m} for m in ("m1", "m2", "m3", "m4", "m5", "m6")]
    duble = Duble(por_mensagem={"m2": TimeoutError(), "m4": _mexe(["answers", "opt_out", "noul"], False)(resposta()),
                                "m5": resposta(opt_out=ALTO["opt_out"])})
    jev_real, R.Jev = R.Jev, lambda pasta: duble
    try:
        saidas, custo = R.rodar(casos)
    finally:
        R.Jev = jev_real
    acoes = [s["acao"] for s in saidas]
    if acoes != ["seguir", "revisar", "seguir", "revisar", "bloquear_envios", "seguir"] or custo["falhas_operacionais"] != 2:
        falhas.append(f"A lote: ações {acoes}, falhas contadas {custo['falhas_operacionais']}")
    return n + 1


def bateria_guarda(falhas: list) -> int:
    """Grade inteira de `decidir`: 3 valores por Noul × 5 opções × 2 confianças."""
    niveis = lambda q: (BAIXO[q], DUVIDA[q], ALTO[q])  # noqa: E731
    n = 0
    for vals in itertools.product(*(niveis(q) for q in PRINCIPAIS)):
        principais = dict(zip(PRINCIPAIS, vals))
        for tipo, conf in itertools.product(P.TIPO_DA_OPCAO, (0.3, 0.9)):
            base = O.decidir(resposta(tipo, conf, **principais))  # os três guardas baixos
            if (base["sinais"]["opt_out"] is not False or base["sinais"]["lgpd_request"] is not False) and base["acao"] == "seguir":
                falhas.append(f"B obrigação/dúvida → seguir sem guarda: {principais} {tipo} {conf}")
            for gvals in itertools.product(*(niveis(q) for q in GUARDAS)):
                d = O.decidir(resposta(tipo, conf, **principais, **dict(zip(GUARDAS, gvals))))
                n += 1
                onde = f"{principais} {tipo} {conf} guardas {dict(zip(GUARDAS, gvals))}"
                if d["acao"] not in (base["acao"], "revisar"):
                    falhas.append(f"B guarda mudou a ação para fora de `revisar` ({base['acao']} → {d['acao']}): {onde}")
                if base["acao"] != "seguir" and d["acao"] == "seguir":
                    falhas.append(f"B guarda levou a `seguir`: {onde}")
                if base["bloqueia"] is not False and d["bloqueia"] is False:
                    falhas.append(f"B guarda dispensou o bloqueio ({base['bloqueia']} → False): {onde}")

    # os quatro cantos do achado: exclusão reconhecida × opt-out (baixo, dúvida, alto) × sinal de continuar
    excl = {"lgpd_request": ALTO["lgpd_request"], "wants_contact_to_continue": ALTO["wants_contact_to_continue"]}
    esperado = {BAIXO["opt_out"]: "revisar", DUVIDA["opt_out"]: "revisar", ALTO["opt_out"]: "abrir_pedido_lgpd"}
    for opt, acao in esperado.items():
        d = O.decidir(resposta("deletion", 0.9, opt_out=opt, **excl))
        n += 1
        if d["acao"] != acao or d["bloqueia"] is not True or d["tipo_lgpd"] != "exclusao" \
                or (acao == "revisar" and d["motivo"] != "exclusão com sinal de continuar: confirmar"):
            falhas.append(f"B exclusão + continuar, opt_out {opt:.2f}: {d['acao']} / bloqueia {d['bloqueia']} / {d['motivo']}")
    d = O.decidir(resposta("deletion", 0.9, lgpd_request=ALTO["lgpd_request"]))
    n += 1
    if d["acao"] != "abrir_pedido_lgpd" or d["bloqueia"] is not True:
        falhas.append(f"B exclusão sem sinal de continuar deixou de abrir pedido com bloqueio: {d['acao']} / {d['bloqueia']}")
    return n


def bateria_pendente(falhas: list) -> int:
    """`bloqueia=None` num pedido aberto: obrigação pela metade e fora da cobertura automática."""
    caso = {"id": "X1", "mensagem": "quais dados vocês têm? e parem de me mandar mensagem", "opt_out": True,
            "pedido_lgpd": True, "tipo_lgpd": "acesso", "pausa_temporaria": False, "nota": ""}
    s = O.decidir(resposta("access", 0.9, lgpd_request=ALTO["lgpd_request"], opt_out=DUVIDA["opt_out"]))
    if s["acao"] != "abrir_pedido_lgpd" or s["bloqueia"] is not None:
        falhas.append(f"C caso mal montado: {s['acao']} / {s['bloqueia']}")
    perdas = {b: R.obrigacao_perdida({"acao": "abrir_pedido_lgpd", "tipo_lgpd": "acesso", "bloqueia": b}, caso)
              for b in (True, False, None)}
    if perdas != {True: None, False: "pedido aberto sem bloqueio", None: "pedido aberto com bloqueio pendente"}:
        falhas.append(f"C obrigacao_perdida: {perdas}")
    m = R.metricas_acao([(R.saida_variante(s, caso, "Jev"), caso)])["_bruto"]
    if (m["metade"], m["infracao"]) != (1, 0):
        falhas.append(f"C métrica: metade {m['metade']}, infração {m['infracao']} (esperado 1 e 0)")
    if R.automatico(s) or not R.automatico({"acao": "seguir", "bloqueia": False}) or R.automatico({"acao": "revisar", "bloqueia": True}):
        falhas.append("C `automatico` não separa pendente/revisar de decisão inteira")
    atual = R.curva([s], [caso])[0]
    if atual["n_auto"] != 0 or atual["bloqueio pendente (fora da cobertura)"] != 1:
        falhas.append(f"C curva: {atual}")
    return 5


def main() -> None:
    falhas: list[str] = []
    a, b, c = bateria_falhas(falhas), bateria_guarda(falhas), bateria_pendente(falhas)
    if falhas:
        sys.exit(f"FALHOU ({len(falhas)}):\n  " + "\n  ".join(falhas[:40]) + ("\n  …" if len(falhas) > 40 else ""))
    print(f"ok: A {a} falhas operacionais → `revisar` por item (nenhuma `seguir`; lote não aborta; baixo nível levanta) · "
          f"B {b} combinações de `decidir` (guarda só move para `revisar`; nenhum bloqueio dispensado) · "
          f"C {c} conferências de bloqueio pendente")


if __name__ == "__main__":
    main()
