"""Bateria do código de `jev-x-llm` — roda sem chave e sem rede (`python testa_falhas.py`), com um dublê no lugar do HTTP.

O que se prova (código nosso, não o modelo):
  A. resposta do LLM fora do esquema — JSON ilegível, opção fora da lista, ID faltando ou sobrando, Noul como string ou
     0/1, resposta cortada — é FALHA OPERACIONAL: não entra no cache (vai para `invalidos/`), e nos três exemplos a
     decisão fecha no lado seguro (`revisar` / `sem_informacao`+revisar / `revisa`), nunca numa classe arriscada;
     em `LLM_MODO=gravado` a falha gravada é reproduzida sem chamar;
     falha já registrada é reproduzida também em `auto` (refazer só com flag); cache corrompido vai a `corrompidos/` e
     registro de quarentena sem medição não quebra o `resumo()` (revisão do Codex, achados 1, 2 e 4);
  B. timeout/rede e 5xx: retentados e, esgotados, falha operacional; 400 não se retenta; 429 em três tentativas
     seguidas interrompe o lote (`LoteInterrompido` sinalizado para quem roda); orçamento persistido em arquivo,
     conferido a cada tentativa e compartilhado entre instâncias; `ms` inclui retries (achados 1 e 5);
  C. chave ausente: erro claro, sem valor de chave na mensagem e sem nada impresso; falha operacional nunca pontua,
     nem com gabarito `revisar` (achado 3);
  D. resposta válida atravessa a injeção: Noul true/false e Choice viram a decisão certa pelo código do exemplo.
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import comparar as C  # noqa: E402
import llmcache as L  # noqa: E402


class Duble:
    """Troca `llmcache._http`: devolve o texto dado (ou levanta a exceção dada), uma resposta por chamada."""

    def __init__(self, *respostas):
        self.fila, self.chamadas = list(respostas), 0

    def __call__(self, corpo, chave, timeout):
        self.chamadas += 1
        r = self.fila.pop(0) if len(self.fila) > 1 else self.fila[0]
        if isinstance(r, Exception):
            raise r
        return {"model": "duble", "stop_reason": "end_turn", "content": [{"type": "text", "text": r}],
                "usage": {"input_tokens": 10, "output_tokens": 5}}


def http(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("u", code, "x", {}, None)


def resposta_optout(opt=False, lgpd=False, tipo="none", **extra) -> str:
    base = {"opt_out": opt, "temporary_pause": False, "lgpd_request": lgpd, "lgpd_type": tipo,
            "wants_contact_to_continue": False, "stop_without_object": False, "about_another_contact": False}
    return json.dumps({"answers": {**base, **extra}})


def novo_llm(pasta: Path, duble: Duble, **kw) -> C.ViaLLM:
    L._http = duble
    llm = L.LLM(pasta, **kw)
    return C.ViaLLM(llm)


def main() -> None:
    falhas: list[str] = []
    L.ESPERA_S = (0.0, 0.0)  # sem dormir na bateria
    os.environ["ANTHROPIC_API_KEY"] = "chave-de-mentira-da-bateria"
    tmp = Path(tempfile.mkdtemp(prefix="jev-x-llm-"))
    ex_o, ex_m, ex_a = (C.carregar(n) for n in C.NOMES)
    tax = json.loads((ex_m.pasta / "dados" / "taxonomia.json").read_text(encoding="utf-8"))["casos"]
    caso_a = {"afirmacao": "Testes do módulo de imóveis passando.", "registros": [{"id": "e1", "tipo": "log_teste", "texto": "vitest tests/imoveis — 23 passed (23)"}]}
    conversa = [{"de": "cliente", "texto": "achei caro, R$ 7.200 não cabe"}, {"de": "corretor", "texto": "Entendo!"}]
    n = 0

    # --- A. fora do esquema → falha operacional, lado seguro, nunca no cache
    foras = [("JSON ilegível", "não é json {"), ("opção fora da lista", resposta_optout(tipo="portability")),
             ("chave extra na raiz", json.dumps({**json.loads(resposta_optout()), "extra": 1})),  # revisão do Codex, achado 4
             ("ID faltando", json.dumps({"answers": {"opt_out": True}})), ("ID sobrando", resposta_optout(extra_id=True)),
             ("Noul string", resposta_optout(opt="true")), ("Noul 0/1", resposta_optout(opt=1)),
             ("sem `answers`", json.dumps({"opt_out": True})), ("resposta cortada", resposta_optout()[:40])]
    for nome, texto in foras:
        pasta = tmp / f"A-{nome}"
        via = novo_llm(pasta, Duble(texto))
        d = ex_o.D.guardar_seguro(via, "para de me mandar mensagem")
        n += 1
        if d["acao"] != "revisar" or not d.get("falha") or d["bloqueia"] is not None:
            falhas.append(f"A opt-out {nome}: {d['acao']} / {d['motivo']}")
        if list(pasta.glob("*.json")) or not list((pasta / "invalidos").glob("*.json")):
            falhas.append(f"A {nome}: resposta inválida gravada como válida (ou não gravada em invalidos/)")
        if via.llm.resumo().get("invalidas") != 1:
            falhas.append(f"A {nome}: resumo não conta a inválida: {via.llm.resumo()}")
        # replay em `gravado`: a falha é reproduzida sem chamar
        via2 = novo_llm(pasta, Duble(resposta_optout()), modo="gravado")
        d2 = ex_o.D.guardar_seguro(via2, "para de me mandar mensagem")
        if d2["acao"] != "revisar" or not d2.get("falha") or via2.llm.tentativas_http:
            falhas.append(f"A {nome} replay gravado: {d2['acao']} / chamadas {via2.llm.tentativas_http}")
    # falha já registrada é reproduzida também em `auto` (padrão); refazer só com flag explícita (achado 1)
    pasta = tmp / "A-JSON ilegível"
    via = novo_llm(pasta, Duble(resposta_optout()))
    d = ex_o.D.guardar_seguro(via, "para de me mandar mensagem")
    via_r = novo_llm(pasta, Duble(resposta_optout()), refazer_invalidas=True)
    d_r = ex_o.D.guardar_seguro(via_r, "para de me mandar mensagem")
    n += 1
    if d["acao"] != "revisar" or via.llm.tentativas_http or d_r["acao"] != "seguir" or via_r.llm.tentativas_http != 1:
        falhas.append(f"A auto reproduz inválida: {d['acao']}/{via.llm.tentativas_http}; refazer: {d_r['acao']}/{via_r.llm.tentativas_http}")
    # quarentena com medição validada (achado 2): registro de cache sem `ms` → corrompidos/ e refeito; registro de
    # invalidos/ sem medição → reproduzido com medição None e `resumo()` não quebra
    pasta = tmp / "A-corrompido"
    via = novo_llm(pasta, Duble(resposta_optout()))
    state, questions = ex_o.D.pedido("oi")
    arq = via.llm._arquivo(C.SISTEMA, C.montar_prompt(state, questions))
    L._gravar_json(arq, {"medicao": {"input_tokens": 1}, "resposta": {"answers": json.loads(resposta_optout())["answers"]}})
    d = ex_o.D.guardar_seguro(via, "oi")
    n += 1
    if d["acao"] != "seguir" or via.llm.tentativas_http != 1 or not list((pasta / "corrompidos").glob("*.json")) or via.llm.resumo()["sem_medicao"]:
        falhas.append(f"A cache corrompido: {d['acao']} / tentativas {via.llm.tentativas_http} / {via.llm.resumo()}")
    pasta = tmp / "A-invalida-sem-medicao"
    via = novo_llm(pasta, Duble(resposta_optout()), modo="gravado")
    L._gravar_json(pasta / "invalidos" / f"{arq.stem}.x.json", {"erro": "x", "texto": "não é json"})
    d = ex_o.D.guardar_seguro(via, "oi")
    n += 1
    try:
        r = via.llm.resumo()
        if d["acao"] != "revisar" or not d.get("falha") or r["sem_medicao"] != 1 or r["invalidas"] != 1 or r["input_tokens"] != 0:
            falhas.append(f"A inválida sem medição: {d['acao']} / {r}")
    except Exception as e:  # noqa: BLE001
        falhas.append(f"A inválida sem medição: resumo() quebrou ({type(e).__name__})")
    # os outros dois exemplos, com uma resposta fora do esquema deles
    d = ex_m.D.julgar_seguro(novo_llm(tmp / "A-motivo", Duble(json.dumps({"answers": {"group": "preco"}}))), conversa, tax, variante="c")
    n += 1
    if d["grupo"] != "sem_informacao" or not d["revisar"] or d["origem"] != "falha":
        falhas.append(f"A motivo: {d['grupo']} / {d['revisar']} / {d['origem']}")
    try:
        ex_a.D.auditar(novo_llm(tmp / "A-auditor", Duble(json.dumps({"answers": {"supports_0": "yes"}}))), caso_a)
        falhas.append("A auditor: resposta fora do esquema não levantou erro")
    except L.RespostaInvalida:
        pass
    n += 1

    # --- B. rede e HTTP
    via = novo_llm(tmp / "B-timeout", Duble(TimeoutError("t")))
    d = ex_o.D.guardar_seguro(via, "oi")
    n += 1
    if d["acao"] != "revisar" or not d.get("falha") or via.llm.tentativas_http != L.RETRIES + 1:
        falhas.append(f"B timeout: {d['acao']} / tentativas {via.llm.tentativas_http}")
    via = novo_llm(tmp / "B-503", Duble(http(503), http(503), resposta_optout(opt=True)))
    d = ex_o.D.guardar_seguro(via, "para de me mandar mensagem")
    n += 1
    if d["acao"] != "bloquear_envios" or via.llm.tentativas_http != 3:
        falhas.append(f"B 503 depois sucesso: {d['acao']} / tentativas {via.llm.tentativas_http}")
    via = novo_llm(tmp / "B-400", Duble(http(400)))
    d = ex_o.D.guardar_seguro(via, "oi")
    n += 1
    if d["acao"] != "revisar" or via.llm.tentativas_http != 1:
        falhas.append(f"B 400 retentado: tentativas {via.llm.tentativas_http}")
    via = novo_llm(tmp / "B-429", Duble(http(429)))
    d = ex_o.D.guardar_seguro(via, "oi")
    n += 1
    if d["acao"] != "revisar" or not via.llm.interrompido or via.llm.tentativas_http != L.MAX_429_SEGUIDOS:
        falhas.append(f"B 429×3: {d['acao']} / interrompido {via.llm.interrompido!r} / tentativas {via.llm.tentativas_http}")
    try:
        C._em_serie(via, [{"mensagem": "oi"}], lambda c: ex_o.D.guardar_seguro(via, c["mensagem"]))
        falhas.append("B 429×3: `_em_serie` não interrompeu o lote")
    except L.LoteInterrompido:
        pass
    # orçamento persistido (achado 1): conferido antes de CADA tentativa (retry conta) e compartilhado entre instâncias
    orc = L.Orcamento(tmp / "orcamento.json", 2)
    via = novo_llm(tmp / "B-orc", Duble(http(503), http(503), resposta_optout()), orcamento=orc)
    d = ex_o.D.guardar_seguro(via, "oi")
    via2 = novo_llm(tmp / "B-orc2", Duble(resposta_optout()), orcamento=orc)
    d2 = ex_o.D.guardar_seguro(via2, "oi")
    n += 1
    if d["acao"] != "revisar" or not via.llm.interrompido or via.llm.tentativas_http != 2 or orc.consumo() != 2 \
            or d2["acao"] != "revisar" or not via2.llm.interrompido or via2.llm.tentativas_http:
        falhas.append(f"B orçamento: {d['acao']}/{via.llm.tentativas_http}/{via.llm.interrompido!r}; consumo {orc.consumo()}; "
                      f"2ª instância {d2['acao']}/{via2.llm.tentativas_http}")
    # `ms` = operação inteira, retries e esperas incluídos (achado 5)
    espera, L.ESPERA_S = L.ESPERA_S, (0.05, 0.05)
    try:
        via = novo_llm(tmp / "B-ms", Duble(http(503), resposta_optout()))
        ex_o.D.guardar_seguro(via, "oi")
    finally:
        L.ESPERA_S = espera
    n += 1
    if via.llm.tentativas_http != 2 or via.llm.chamadas[0]["ms"] < 50 or via.llm.chamadas[0]["tentativas"] != 2:
        falhas.append(f"B ms com retries: {via.llm.chamadas}")

    # --- C. chave ausente: erro claro, nada impresso
    os.environ["ANTHROPIC_API_KEY"] = ""
    arquivo_chave, L.ARQUIVO_CHAVE = L.ARQUIVO_CHAVE, tmp / "nao-existe.txt"
    saida = io.StringIO()
    try:
        with redirect_stdout(saida), redirect_stderr(saida):
            try:
                L._chave_api()
                falhas.append("C chave ausente não levantou")
            except L.FalhaChamada as e:
                if "ANTHROPIC_API_KEY" not in str(e) or "mentira" in str(e):
                    falhas.append(f"C mensagem: {e}")
            via = novo_llm(tmp / "C", Duble(resposta_optout()))
            d = ex_o.D.guardar_seguro(via, "oi")
            if d["acao"] != "revisar" or via.llm.tentativas_http:
                falhas.append(f"C sem chave chamou ou decidiu: {d['acao']} / {via.llm.tentativas_http}")
    finally:
        L.ARQUIVO_CHAVE = arquivo_chave
        os.environ["ANTHROPIC_API_KEY"] = "chave-de-mentira-da-bateria"
    if saida.getvalue():
        falhas.append(f"C imprimiu algo: {saida.getvalue()[:80]!r}")
    n += 2

    # --- C2. falha operacional não pontua nem com gabarito `revisar` (achado 3), e não concorda
    caso = {"id": "X1", "mensagem": "não quero mais", "opt_out": None, "pedido_lgpd": False, "tipo_lgpd": None, "pausa_temporaria": False, "nota": ""}
    jev_duble = novo_llm(tmp / "C2-jev", Duble(resposta_optout()))  # faz o papel do Jev: resposta válida → seguir
    via = novo_llm(tmp / "C2-llm", Duble(TimeoutError("t")))
    b = C.rodar_optout(ex_o, [caso], jev_duble, via)
    n += 1
    if b["acertos"]["LLM"] != 0 or b["falhas_llm"] != 1 or b["metricas"]["LLM"]["acerto_acao"] != 0.0 or b["concordancia"] != 0 \
            or b["casos"][0]["ok L"] != "✗F" or b["casos"][0]["LLM"] != "revisar":
        falhas.append(f"C2 falha pontuou: acertos {b['acertos']} / {b['metricas']['LLM']['acerto_acao']} / conc {b['concordancia']} / {b['casos'][0]['ok L']}")

    # --- D. resposta válida atravessa a injeção
    d = ex_o.D.guardar_seguro(novo_llm(tmp / "D-opt", Duble(resposta_optout(lgpd=True, tipo="deletion"))), "apaga meus dados")
    n += 1
    if (d["acao"], d["tipo_lgpd"], d["bloqueia"]) != ("abrir_pedido_lgpd", "exclusao", True):
        falhas.append(f"D opt-out exclusão: {d['acao']} / {d['tipo_lgpd']} / {d['bloqueia']}")
    pedido = ex_m.D.pedido_tudo(tax)
    answers = {q: ("preco" if q == "group" else "preco_acima_orcamento" if q == "leaf.preco" else list(p["criteria"])[0] if p["type"] == "choice" else True)
               for q, p in pedido.items()}
    answers_m = dict(answers)
    d = ex_m.D.julgar_seguro(novo_llm(tmp / "D-motivo", Duble(json.dumps({"answers": answers}))), conversa, tax, variante="c")
    n += 1
    if (d["grupo"], d["folha"], d["revisar"]) != ("preco", "preco_acima_orcamento", False):
        falhas.append(f"D motivo: {d['grupo']} / {d['folha']} / {d['revisar']} / {d['motivo']}")
    answers = {q: True for q in ex_a.P.perguntas(1)}
    answers["contradicts_0"] = False
    d = ex_a.D.auditar(novo_llm(tmp / "D-auditor", Duble(json.dumps({"answers": answers}))), caso_a)
    n += 1
    if d["relacao"] != "supported" or d["apoio"] != ["e1"]:
        falhas.append(f"D auditor: {d['relacao']} / {d['apoio']}")
    # leitura tolerante (secundária): violação só em Choice de folhas de grupo NÃO vencedor → decidido, sem chamar de novo;
    # violação na Choice do grupo vencedor → continua falha
    tolerar = lambda a, v, q: all(x.startswith("leaf.") and x != f"leaf.{a.get('group')}" for x in v)  # noqa: E731
    for nome, viol, esperado in (("especulativa", "leaf.imovel", ("preco", "preco_acima_orcamento", False)),
                                 ("no vencedor", "leaf.preco", ("sem_informacao", None, True))):
        ruim = {**answers_m, viol: "chave_inventada"}
        pasta = tmp / f"D-tol-{nome}"
        estrita = ex_m.D.julgar_seguro(novo_llm(pasta, Duble(json.dumps({"answers": ruim}))), conversa, tax, variante="c")
        via = novo_llm(pasta, Duble(TimeoutError("não devia chamar")), modo="gravado")
        via.tolerar = tolerar
        tol = ex_m.D.julgar_seguro(via, conversa, tax, variante="c")
        n += 1
        if estrita["origem"] != "falha" or (tol["grupo"], tol["folha"], tol["revisar"]) != esperado or via.llm.tentativas_http \
                or via.toleradas != (1 if nome == "especulativa" else 0):
            falhas.append(f"D tolerante {nome}: estrita {estrita['origem']} / tol {tol['grupo']},{tol['folha']},{tol['revisar']} / toleradas {via.toleradas}")
    # cache: a segunda leitura vem do disco sem chamar
    via = novo_llm(tmp / "D-opt", Duble(TimeoutError("não devia chamar")))
    d = ex_o.D.guardar_seguro(via, "apaga meus dados")
    n += 1
    if d["acao"] != "abrir_pedido_lgpd" or via.llm.tentativas_http or not via.llm.resumo()["do_cache"]:
        falhas.append(f"D cache: {d['acao']} / tentativas {via.llm.tentativas_http}")

    if falhas:
        sys.exit(f"FALHOU ({len(falhas)}):\n  " + "\n  ".join(falhas))
    print(f"ok: {n} conferências — A fora do esquema = falha operacional (lado seguro, nunca no cache, replay reproduz); "
          f"B rede/HTTP (retries, 400 sem retry, 429×3 e orçamento interrompem); C chave ausente sem imprimir; D injeção e cache")


if __name__ == "__main__":
    main()
