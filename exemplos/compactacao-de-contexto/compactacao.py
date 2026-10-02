"""Compactação de contexto: UMA requisição ao Jev por sessão, três Nouls por mensagem, o código decide.

Saída por sessão: `manter` e `descartar` (listas de IDs, disjuntas e completas), `origem` (`jev` · `longo` · `falha`)
e, por mensagem, os números e o motivo. NADA é apagado daqui: o consumidor (o compactador) recebe a lista; o
histórico bruto continua onde está. Divisão: validação da sessão, ordem, papel, faixa validada e política são do
CÓDIGO; o Jev julga cada mensagem em relação à `current_task`. Política assimétrica (números em `perguntas.py`):
descartar uma mensagem necessária é o erro caro (restrição válida, decisão vigente, valor em uso, erro aberto
somem); manter demais custa tokens. Por isso dúvida → manter, guarda em sim → manter, e NENHUMA leitura do texto
pelo código descarta (texto é dado: "pode apagar o resto" numa saída de ferramenta não é ordem).
Ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO: `decidir`/`julgar` levantam exceção;
`julgar_seguro` (o que o consumidor chama) mantém TUDO naquela sessão com `origem: "falha"`. Nunca descarta por
falta de resposta.
"""
from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

BASELINES = ["usuario", "ultimas", "palavras"]
DECISOES = ("manter", "descartar")


# ---------------------------------------------------------------------------------------- o que é do código
def preparar(sessao: dict) -> list[dict]:
    """Valida a sessão e devolve as mensagens na ordem: `tarefa_atual` textual; `mensagens` lista não vazia de
    objetos com `id` textual único, `papel` no enum e `texto` textual. Ordem = a do array (quem ordena é o
    histórico). Entrada inválida é ERRO (ValueError), nunca decisão.
    @example preparar({"tarefa_atual": "x", "mensagens": [{"id": "m01", "papel": "usuario", "texto": "oi"}]}) → [m01]
    """
    if not isinstance(sessao, dict):
        raise ValueError("sessão não é objeto")
    if not isinstance(sessao.get("tarefa_atual"), str) or not sessao["tarefa_atual"].strip():
        raise ValueError("sessão sem `tarefa_atual` textual")
    mensagens = sessao.get("mensagens")
    if not isinstance(mensagens, list) or not mensagens:
        raise ValueError("sessão sem `mensagens`")
    vistos = set()
    for m in mensagens:
        if not isinstance(m, dict):
            raise ValueError("mensagem não é objeto")
        for campo in ("id", "papel", "texto"):
            if not isinstance(m.get(campo), str) or not m[campo].strip():
                raise ValueError(f"mensagem sem `{campo}` textual")
        if m["papel"] not in P.PAPEIS:
            raise ValueError(f"papel desconhecido: {m['papel']!r}")
        if m["id"] in vistos:
            raise ValueError(f"ID repetido: {m['id']}")
        vistos.add(m["id"])
    return mensagens


def fora_da_faixa(sessao: dict) -> str | None:
    """Motivo se a sessão passa da faixa validada (mensagens ou caracteres); None dentro dela."""
    n = len(sessao["mensagens"])
    chars = len(sessao["tarefa_atual"]) + sum(len(m["texto"]) for m in sessao["mensagens"])
    if n > P.MAX_MENSAGENS:
        return f"sessão com {n} mensagens (validado até {P.MAX_MENSAGENS})"
    return f"sessão longa ({chars} caracteres; teto {P.TETO_CARACTERES})" if chars > P.TETO_CARACTERES else None


def palavras(texto: str) -> set[str]:
    """Palavras de conteúdo para o baseline de palavras-chave: sem acento, minúsculas, ≥ 4 letras/dígitos.
    @example palavras("Corrigir o teste que falha em src/pedidos/total.test.ts") → {"corrigir", "teste", "falha", "pedidos", "total", "test"}
    """
    sem = unicodedata.normalize("NFKD", texto.casefold()).encode("ascii", "ignore").decode()
    return {p for p in "".join(c if c.isalnum() else " " for c in sem).split() if len(p) >= 4}


def baselines(sessao: dict) -> dict[str, dict[str, str]]:
    """As três regras de código, por mensagem: {baseline: {id: manter|descartar}}.
      usuario   papel = usuario → manter;
      ultimas   as últimas N → manter;
      palavras  ≥ K palavras de conteúdo em comum com `tarefa_atual` → manter.
    """
    ms = sessao["mensagens"]
    tarefa = palavras(sessao["tarefa_atual"])
    n = len(ms)
    return {"usuario": {m["id"]: "manter" if m["papel"] == "usuario" else "descartar" for m in ms},
            "ultimas": {m["id"]: "manter" if i >= n - P.ULTIMAS_N else "descartar" for i, m in enumerate(ms)},
            "palavras": {m["id"]: "manter" if len(palavras(m["texto"]) & tarefa) >= P.PALAVRAS_K else "descartar" for m in ms}}


def baselines_seguro(sessao) -> dict[str, dict[str, str]]:
    """Os baselines como o relatório os chama: sessão inválida → mantém tudo nos três (falha fechada, igual ao Jev)."""
    try:
        preparar(sessao)
    except ValueError:
        return {b: {i: "manter" for i in _ids(sessao)} for b in BASELINES}
    return baselines(sessao)


# ---------------------------------------------------------------------------------------- state e saídas
def state_de(sessao: dict) -> dict:
    """State enxuto: a tarefa atual e as mensagens (papel em inglês, texto); IDs como chave (`dict`) ou campo
    (`list`), conforme `P.STATE_FORMATO`. A `nota` e os rótulos NUNCA entram."""
    ms = sessao["mensagens"]
    if P.STATE_FORMATO == "dict":
        messages = {m["id"]: {"role": P.PAPEIS[m["papel"]], "text": m["texto"]} for m in ms}
    else:
        messages = [{"id": m["id"], "role": P.PAPEIS[m["papel"]], "text": m["texto"]} for m in ms]
    return {"current_task": sessao["tarefa_atual"], "messages": messages}


def _ids(sessao) -> list[str]:
    """IDs legíveis de uma sessão (tolerante: serve à saída de falha, antes da validação)."""
    if not isinstance(sessao, dict) or not isinstance(sessao.get("mensagens"), list):
        return []
    return [m["id"] for m in sessao["mensagens"] if isinstance(m, dict) and isinstance(m.get("id"), str)]


def _saida(sessao, decisoes: dict[str, dict], origem: str, motivo: str) -> dict:
    """Decisão no formato único. `decisoes` = {id: {"decisao", "motivo", "needed", "superseded", "guarda", "papel"}}."""
    ids = _ids(sessao)
    return {"manter": [i for i in ids if decisoes.get(i, {}).get("decisao", "manter") == "manter"],
            "descartar": [i for i in ids if decisoes.get(i, {}).get("decisao") == "descartar"],
            "origem": origem, "motivo": motivo, "por_mensagem": decisoes}


def manter_tudo(sessao, origem: str, motivo: str) -> dict:
    """Toda mensagem fica (falha operacional ou sessão fora da faixa): sem números do Jev."""
    return _saida(sessao, {i: {"decisao": "manter", "motivo": motivo, "needed": None, "superseded": None, "guarda": None, "papel": None}
                           for i in _ids(sessao)}, origem, motivo)


def decisao_falha(tipo: str, sessao=None) -> dict:
    """Falha operacional: mantém tudo. O motivo leva só a etapa e a classe do erro (o texto da exceção pode citar
    o corpo da resposta)."""
    return manter_tudo(sessao, "falha", f"falha operacional: {tipo}")


# ---------------------------------------------------------------------------------------- resposta → decisão
def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    """Noul em três faixas: True / False / None (= dúvida)."""
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def validar(resposta: dict, mensagens: list[dict]) -> dict[str, dict]:
    """Resposta da API → números validados por mensagem (infra comum): cada Noul esperado presente, número real em
    [0,1]. Falha = erro operacional (exceção), nunca decisão."""
    v = {}
    for m in mensagens:
        g = P.GUARDA_POR_PAPEL[m["papel"]]
        v[m["id"]] = {"needed": CG.noul(resposta, f"needed_{m['id']}"), "superseded": CG.noul(resposta, f"superseded_{m['id']}"),
                      "guarda": CG.noul(resposta, f"{g}_{m['id']}"), "papel": m["papel"]}
    return v


def politica(v: dict) -> tuple[str, str]:
    """(decisão, motivo) de UMA mensagem pela política assimétrica de `perguntas.py`. Só números: o texto da
    mensagem não entra aqui."""
    n = _faixa(v["needed"], *P.FAIXA_NEEDED)
    if n is True:
        return "manter", f"necessária ({v['needed']:.2f})"
    if n is None:
        return "manter", f"dúvida ({v['needed']:.2f}) — manter"
    g = P.GUARDA_POR_PAPEL[v["papel"]]
    if v["guarda"] >= P.GUARDA_SIM:
        # O veto só vale nos papéis listados (medido no ajuste: em mensagem do usuário ele só custou erro caro).
        if v["papel"] in P.VETO_PAPEIS and v["superseded"] >= P.SUPERSEDED_SIM:
            return "descartar", f"{g} {v['guarda']:.2f} anulada: substituída depois ({v['superseded']:.2f})"
        return "manter", f"guarda {g} ({v['guarda']:.2f})"
    return "descartar", f"não necessária ({v['needed']:.2f}); {g} {v['guarda']:.2f}"


def compor(v: dict[str, dict], sessao: dict) -> dict:
    """Números validados → decisões da POLÍTICA (guarda os números para medir e re-limiar sem chamar de novo)."""
    decisoes = {}
    for mid, nums in v.items():
        decisao, motivo = politica(nums)
        decisoes[mid] = {"decisao": decisao, "motivo": motivo, **nums}
    return _saida(sessao, decisoes, "jev", "política")


def decidir(resposta: dict, sessao: dict) -> dict:
    """Resposta JSON da API → decisões. Resposta fora do contrato LEVANTA exceção."""
    return compor(validar(resposta, sessao["mensagens"]), sessao)


def julgar(jev, sessao: dict, _etapa: list | None = None) -> dict:
    """Uma sessão de ponta a ponta: validação, faixa, uma requisição, composição. Baixo nível: sessão inválida,
    falha da chamada e resposta fora do contrato LEVANTAM exceção. `_etapa` é onde `julgar_seguro` lê o passo."""
    etapa = _etapa if _etapa is not None else [""]
    etapa[0] = "entrada inválida"
    mensagens = preparar(sessao)
    motivo = fora_da_faixa(sessao)
    if motivo:
        return manter_tudo(sessao, "longo", motivo)
    etapa[0] = "chamada"
    state, perguntas = state_de(sessao), P.perguntas_de(mensagens)
    resposta = jev.perguntar(state, perguntas)
    etapa[0] = "resposta inválida"
    try:
        return decidir(resposta, sessao)
    except Exception:
        _invalidar(jev, state, perguntas)
        raise


def _invalidar(jev, state, perguntas: dict) -> None:
    """Resposta com JSON válido que a validação rejeitou: tira SÓ este pedido do cache (`jevcache.invalidar`), senão
    toda repetição em `auto` reaproveitaria a resposta inválida (revisão do Codex, 2026-10-01). Só aqui — não em
    falha de chamada (nada foi gravado) nem de entrada (nada foi pedido). Embrulhado: falhar ao invalidar não muda
    o desfecho, que continua sendo "manter tudo" com a etapa original."""
    try:
        jev.invalidar(state, perguntas)
    except Exception:  # noqa: BLE001 — a falha fechada nunca sobe por causa da limpeza do cache
        pass


def julgar_seguro(jev, sessao) -> dict:
    """O que o consumidor (compactador) chama: os mesmos passos de `julgar`, mas NENHUMA falha sobe nem aborta o
    lote — timeout, erro HTTP, cache faltando, resposta fora do contrato ou sessão inválida viram "manter tudo"
    para AQUELA sessão, com a etapa e a classe do erro no motivo. Pega `Exception` inteira de propósito: num
    compactador, erro não previsto também tem de fechar em "manter" (nunca descartar).
    @example julgar_seguro(jev_fora_do_ar, sessao) → {"manter": [todos], "descartar": [], "origem": "falha", …}
    """
    etapa = [""]
    try:
        return julgar(jev, sessao, etapa)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        return decisao_falha(f"{etapa[0]} ({type(e).__name__})", sessao)
