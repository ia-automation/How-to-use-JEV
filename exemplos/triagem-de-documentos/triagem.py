"""Triagem de documentos: condição numérica em código; semântica por dois desenhos (mapa por seção × documento inteiro).

Saída por documento, para UMA condição — nada é executado daqui (o consumidor decide o que fazer com a lista):
  verdadeiro    o documento dispõe o que a condição pede (e nenhuma seção posterior revogou)
  falso         não dispõe / nega / revogou — ou o número em `campos` não satisfaz a parte numérica
  indecidivel   Noul na faixa do meio, decisão deixada em aberto (`deferred`), texto fora da faixa validada ou
                falha operacional → humano lê o documento
Desenho A (`avaliar_mapa`): uma requisição por seção (`establishes`, `revokes`, `deferred`), redução em código na
ordem do texto (`reduzir`). Desenho B (`avaliar_inteiro`): uma requisição por documento (`holds`, `deferred`,
Choice `proving_section`). Os `campos` não vão ao Jev; a condição numérica (`tipo: numerica`, expressão
"(`campo` op inteiro)" validada inteira) é resolvida em Python. Condição composta "A E B" (regra 6, duas seções):
um Noul por cláusula, combinados em código (`combinar`); uma cláusula só nunca é `verdadeiro`.
Política assimétrica onde dói: resposta ausente, ID faltando, tipo errado ou número inválido é ERRO — as funções
baixas levantam; as `*_seguro` (o que o consumidor chama) convertem a falha em `indecidivel` para AQUELE documento e
tiram do cache a resposta inválida (`jev.invalidar`), para que a repetição em `auto` a refaça. Nunca `verdadeiro`.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

SAIDAS = ["verdadeiro", "falso", "indecidivel"]
# Campos numéricos por tipo (LEIA-ME): a cláusula numérica só pode citar um deles. Documento sem o campo vale falso.
CAMPOS_NUMERICOS = {"valor_aluguel", "prazo_meses", "multa_alugueis", "valor_mensal", "multa_percentual", "quorum_percentual",
                    "taxa_valor", "reajuste_percentual", "valor_total", "validade_dias", "prazo_entrega_dias",
                    "desconto_percentual", "garantia_meses"}
# A gramática do rotulador (dados/valida.py): "(`campo` op inteiro)" entre parênteses, UMA vez. A expressão é validada
# INTEIRA (revisão do Codex, 2026-10-02, achado 2: a regex antiga aceitava o prefixo de "`prazo_meses` < 12.5" como
# "< 12"); sufixo decimal/científico, operador extra ou crase fora do parêntese = condição recusada, não adivinhada.
_CLAUSULA = re.compile(r"\(\s*`(\w+)`\s*(<=|>=|<|>)\s*(\d+)\s*\)")
_OPS = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}
TIPOS_CONDICAO = ("semantica", "numerica")
# Condição composta (regra 6 do LEIA-ME, "duas seções"): cláusulas ligadas por " E " em MAIÚSCULAS, como o rotulador do
# sql-semantico escreve; cada cláusula ganha um Noul próprio por seção/documento e o código combina (achado 3 do Codex).
# "e" minúsculo é conjunção da frase, não conector.
_CONECTOR = re.compile(r"\s+E\s+")


# ---------------------------------------------------------------------------------------- parte do código
def separar(condicao: str, tipo: str = "semantica") -> dict:
    """Condição + `tipo` do rotulador → {"numerica": (campo, op, valor) | None, "texto": condição, "partes": [cláusulas]}.
    `tipo` é validado e tem de bater com a forma (achado 1 do Codex: `tipo` era descartado e uma numérica sem crase
    iria ao Jev): `numerica` exige a expressão estruturada válida; `semantica` não pode ter crase. Semântica com " E "
    maiúsculo é composta (`partes` com ≥ 2 cláusulas); senão `partes` = [texto].
    @example separar("Multa superior a dois aluguéis (`multa_alugueis` > 2).", "numerica") → {"numerica": ("multa_alugueis", ">", 2), …}"""
    if not isinstance(condicao, str) or not condicao.strip():
        raise ValueError("condição vazia ou não textual")
    if tipo not in TIPOS_CONDICAO:
        raise ValueError(f"tipo de condição inválido: {tipo!r}")
    texto = condicao.strip()
    if tipo == "semantica":
        if "`" in texto:
            raise ValueError("condição semântica com crase (expressão estruturada)")
        partes = [p.strip(" ,;:") for p in _CONECTOR.split(texto)]
        partes = [p for p in partes if p]
        if not partes:
            raise ValueError("condição sem cláusula")
        return {"numerica": None, "texto": texto, "partes": partes if len(partes) > 1 else [texto]}
    clausulas = _CLAUSULA.findall(texto)
    if len(clausulas) != 1 or texto.count("`") != 2:
        raise ValueError("condição numérica exige UMA expressão `(`campo` op inteiro)` válida")
    campo, op, valor = clausulas[0]
    if campo not in CAMPOS_NUMERICOS:
        raise ValueError(f"campo numérico desconhecido: {campo!r}")
    return {"numerica": (campo, op, int(valor)), "texto": texto, "partes": [texto]}


def separar_seguro(condicao, tipo=None) -> dict:
    """Condição inválida vira {"erro": …}: todo documento dela sai `indecidivel` pelas `*_seguro`, zero chamada."""
    try:
        return separar(condicao, tipo)
    except Exception as e:  # noqa: BLE001 — entrada inválida fecha em "humano lê", nunca em `verdadeiro`
        return {"erro": f"condição inválida: {e}", "numerica": None, "texto": "", "partes": []}


def avaliar_numerica(sep: dict, doc: dict) -> dict:
    """Parte numérica, em Python, sobre `campos` (regra 8 do LEIA-ME): campo ausente ou nulo = falso (o documento não
    dispõe o número); tipo errado é ERRO. `prova` = nenhuma (o código não sabe a seção)."""
    campo, op, valor = sep["numerica"]
    v = (doc.get("campos") or {}).get(campo)
    if v is None:
        return _saida("falso", "codigo", f"`{campo}` ausente ou nulo")
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"campo {campo} com tipo inválido: {v!r}")
    ok = _OPS[op](v, valor)
    return _saida("verdadeiro" if ok else "falso", "codigo", f"`{campo}` = {v} {op} {valor}: {ok}")


# ---------------------------------------------------------------------------------------- states e validação
def _secoes(doc: dict) -> list[dict]:
    secoes = doc.get("secoes")
    if not isinstance(secoes, list) or not secoes:
        raise ValueError("documento sem seções")
    for s in secoes:
        if not isinstance(s, dict) or not isinstance(s.get("id"), str) or not isinstance(s.get("texto"), str) or not s["texto"].strip():
            raise ValueError(f"seção vazia ou fora do esquema: {s.get('id') if isinstance(s, dict) else s!r}")
    if len({s["id"] for s in secoes}) != len(secoes):
        raise ValueError("ids de seção repetidos")
    return secoes


def _tipo(doc: dict) -> str:
    tipo = doc.get("tipo")
    if tipo not in P.TIPOS_DOCUMENTO:
        raise ValueError(f"tipo de documento desconhecido: {tipo!r}")
    return P.TIPOS_DOCUMENTO[tipo]


def _composta(sep: dict) -> bool:
    return len(sep.get("partes") or []) > 1


def state_secao(sep: dict, doc: dict, secao: dict) -> dict:
    """Condição simples: state idêntico ao da rodada 1 (as respostas em cache continuam valendo); composta: ganha
    `condition_parts`, que as perguntas por cláusula citam."""
    state = {"condition": sep["texto"], "document_type": _tipo(doc),
             "section": {"title": str(secao.get("titulo") or ""), "text": secao["texto"]}}
    if _composta(sep):
        state["condition_parts"] = list(sep["partes"])
    return state


def state_documento(sep: dict, doc: dict) -> dict:
    state = {"condition": sep["texto"], "document_type": _tipo(doc),
             "sections": [{"id": s["id"], "title": str(s.get("titulo") or ""), "text": s["texto"]} for s in _secoes(doc)]}
    if _composta(sep):
        state["condition_parts"] = list(sep["partes"])
    return state


def texto_longo(n: int, teto: int, o_que: str) -> str | None:
    return f"texto longo ({o_que}: {n} caracteres; teto {teto})" if n > teto else None


def validar_nouls(resposta: dict, ids: list[str]) -> dict:
    """{id: valor} validados pela infra comum (ID presente, tipo `noul`, número real em [0,1]); falha = exceção."""
    if not isinstance(resposta, dict):
        raise ValueError(f"resposta não é objeto: {type(resposta).__name__}")
    return {q: CG.noul(resposta, q) for q in ids}


# ---------------------------------------------------------------------------------------- política
def _faixa(valor: float, nao: float, sim: float) -> str:
    if valor >= sim:
        return "verdadeiro"
    if valor <= nao:
        return "falso"
    return "indecidivel"


def _reduzir_clausula(secoes: list[dict], chave: str, fx: dict) -> tuple[str, list[str]]:
    """Máquina de estados de UMA cláusula na ordem do texto: uma seção que institui (≥ sim) põe `verdadeiro`; uma
    posterior que revoga (≥ sim) devolve a `falso`; valor no meio (institui ou revoga) → `indecidivel`, salvo se outra
    seção depois institui de novo."""
    estado, passos = "falso", []
    for s in secoes:
        e = _faixa(s[chave], *fx["establishes"])
        r = _faixa(s["revokes"], *fx["revokes"])
        if e == "verdadeiro":
            estado = "verdadeiro"
            passos.append(f"{s['id']} institui {s[chave]:.2f}")
        elif e == "indecidivel" and estado != "verdadeiro":
            estado = "indecidivel"
            passos.append(f"{s['id']} institui? {s[chave]:.2f}")
        if estado != "falso" and r == "verdadeiro":
            estado = "falso"
            passos.append(f"{s['id']} revoga {s['revokes']:.2f}")
        elif estado == "verdadeiro" and r == "indecidivel":
            estado = "indecidivel"
            passos.append(f"{s['id']} revoga? {s['revokes']:.2f}")
    return estado, passos


def combinar(estados: list[str]) -> str:
    """Regra 6 do LEIA-ME sobre os estados das cláusulas (E): todas → verdadeiro; alguma falsa → falso; senão indecidível."""
    if all(e == "verdadeiro" for e in estados):
        return "verdadeiro"
    return "falso" if "falso" in estados else "indecidivel"


def chaves_clausulas(secao_ou_valores: dict) -> list[str]:
    """IDs dos Nouls por cláusula presentes (`establishes_part_<i>` / `holds_part_<i>`), na ordem das cláusulas."""
    ks = [k for k in secao_ou_valores if k.startswith(("establishes_part_", "holds_part_"))]
    return sorted(ks, key=lambda k: int(k.rsplit("_", 1)[1]))


def reduzir(secoes: list[dict], faixa: dict | None = None, adiado: float | None = None) -> tuple[str, str | None, str]:
    """Desenho A, em código, na ORDEM do texto. `secoes` = [{"id", "establishes", "revokes", "deferred"
    (+ "establishes_part_<i>" nas compostas)}, …]. Condição simples: a máquina de estados sobre `establishes`.
    Composta (regra 6, achado 3 do Codex): uma máquina por cláusula sobre `establishes_part_<i>` (cada uma pode ser
    provada em seção diferente; o `revokes` é o mesmo) e `combinar` (E) em código — uma cláusula só NÃO basta.
    Ao final, `falso` com alguma seção `deferred` ≥ ADIADO_SIM → `indecidivel` (deixou em aberto, regra 7).
    `prova` = seção de maior `establishes`; na composta, a que COMPLETA a prova: a mais tardia entre as de maior
    valor de cada cláusula (LEIA-ME, regra 6).
    @example reduzir([{"id": "s5", "establishes": 0.95, "revokes": 0.01, "deferred": 0.0}, {"id": "s8", "establishes": 0.05, "revokes": 0.97, "deferred": 0.0}])
             → ("falso", "s5", "s5 institui 0.95; s8 revoga 0.97")"""
    if not secoes:
        raise ValueError("nada a reduzir: documento sem seções avaliadas")
    fx = faixa or P.FAIXA
    lim_adiado = P.ADIADO_SIM if adiado is None else adiado
    partes = chaves_clausulas(secoes[0])
    if partes:
        estados, passos = [], []
        for k in partes:
            e, p = _reduzir_clausula(secoes, k, fx)
            estados.append(e)
            passos.append(f"cláusula {k.rsplit('_', 1)[1]} {e}: " + ("; ".join(p) or "nada institui"))
        estado = combinar(estados)
        idx = [max(range(len(secoes)), key=lambda i: secoes[i][k]) for k in partes]
        melhor = secoes[max(idx)]
    else:
        estado, passos = _reduzir_clausula(secoes, "establishes", fx)
        melhor = max(secoes, key=lambda s: s["establishes"])
        if not passos:
            passos.append(f"nenhuma seção institui (máx {melhor['establishes']:.2f} em {melhor['id']})")
    if estado == "falso":
        aberto = [s for s in secoes if s["deferred"] >= lim_adiado]
        if aberto:
            estado = "indecidivel"
            passos.append(f"{aberto[0]['id']} deixa em aberto {aberto[0]['deferred']:.2f}")
    return estado, melhor["id"], "; ".join(passos)


def decidir_inteiro(valores: dict, faixa: dict | None = None, adiado: float | None = None) -> tuple[str, str]:
    """Desenho B: `holds` em três faixas (composta: um `holds_part_<i>` por cláusula, combinados pela regra 6);
    `falso` com `deferred` ≥ ADIADO_SIM → `indecidivel`."""
    fx = faixa or P.FAIXA
    lim_adiado = P.ADIADO_SIM if adiado is None else adiado
    partes = chaves_clausulas(valores)
    if partes:
        saida = combinar([_faixa(valores[k], *fx["holds"]) for k in partes])
        motivo = "cláusulas " + ", ".join(f"{valores[k]:.2f}" for k in partes)
    else:
        saida = _faixa(valores["holds"], *fx["holds"])
        motivo = f"holds {valores['holds']:.2f}"
    if saida == "falso" and valores.get("deferred", 0.0) >= lim_adiado:
        return "indecidivel", motivo + f", deferred {valores['deferred']:.2f}: deixa em aberto"
    return saida, motivo


# ---------------------------------------------------------------------------------------- baseline de código
def _plano(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


def radicais(condicao: str) -> list[str]:
    """Radicais da condição (sem a cláusula numérica): palavras sem acento, fora da lista genérica, cortadas na 5ª letra.
    @example radicais("Ata que registra a aprovação de reajuste da taxa condominial.") → ["aprov", "reaju", "taxa"]"""
    texto = re.sub(r"\(?`[^`]*`[^()]*\)?", " ", condicao)
    saida = []
    for w in re.findall(r"[a-z]+", _plano(texto)):
        if w in P.BASELINE_IGNORAR or len(w) < 3:
            continue
        r = w[:P.BASELINE_CORTE]
        if r not in saida:
            saida.append(r)
    return saida


def baseline(sep: dict, doc: dict) -> dict:
    """Numérica → código (igual aos desenhos). Semântica → por seção, conta radicais presentes; seção com ≥ metade
    bate; documento `verdadeiro` se alguma bate; `prova` = seção com mais radicais. Nunca `indecidivel`. Baixo nível:
    condição inválida e campo com tipo errado LEVANTAM."""
    if sep.get("erro"):
        raise ValueError(sep["erro"])
    if sep["numerica"]:
        return avaliar_numerica(sep, doc)
    secoes = _secoes(doc)
    provas, motivos = [], []
    for parte in sep["partes"]:  # composta: cada cláusula tem de bater em alguma seção (pode ser outra); prova = a mais tardia
        rads = radicais(parte)
        if not rads:
            provas.append(0)
            motivos.append("cláusula sem radical")
            continue
        minimo = max(1, -(-len(rads) // 2))
        contagens = [(sum(r in _plano(f"{s.get('titulo') or ''} {s['texto']}") for r in rads), i) for i, s in enumerate(secoes)]
        n, i = max(contagens)
        motivos.append(f"{n}/{len(rads)} radicais em {secoes[i]['id']} (mínimo {minimo})")
        provas.append(i if n >= minimo else None)
    ok = all(p is not None for p in provas)
    return _saida("verdadeiro" if ok else "falso", "baseline", "; ".join(motivos), prova=secoes[max(provas)]["id"] if ok else None)


def baseline_seguro(sep: dict, doc: dict) -> dict:
    try:
        return baseline(sep, doc)
    except Exception as e:  # noqa: BLE001 — falha fechada por documento, como nas `*_seguro` do Jev
        return _saida("indecidivel", "falha", f"falha operacional: baseline ({type(e).__name__})", falha=True)


# ---------------------------------------------------------------------------------------- um documento
def _saida(saida: str, por: str, motivo: str, **marcas) -> dict:
    return {"saida": saida, "por": por, "motivo": motivo, **marcas}


def _invalidar(jev, state, perguntas: dict) -> None:
    """Resposta com JSON válido que a validação rejeitou: tira SÓ este pedido do cache (família "resposta inválida presa
    no cache"); não em falha de chamada (nada foi gravado). Falhar ao invalidar não muda o desfecho."""
    try:
        jev.invalidar(state, perguntas)
    except Exception:  # noqa: BLE001 — a limpeza do cache nunca derruba a falha fechada
        pass


def _perguntar_validado(jev, state, perguntas: dict, validar):
    resposta = jev.perguntar(state, perguntas)
    try:
        return validar(resposta)
    except Exception:
        _invalidar(jev, state, perguntas)
        raise


def avaliar_mapa(jev, sep: dict, doc: dict) -> dict:
    """Desenho A, baixo nível (levanta): numérica em código; senão uma requisição por seção e redução em código.
    Guarda os três Nouls de cada seção para o relatório re-decidir com outra faixa sem chamada."""
    if sep.get("erro"):
        raise ValueError(sep["erro"])
    if sep["numerica"]:
        return avaliar_numerica(sep, doc)
    valores = []
    for s in _secoes(doc):
        motivo = texto_longo(len(s["texto"]), P.TETO_CARACTERES["secao"], s["id"])
        if motivo:
            return _saida("indecidivel", "longo", motivo, longo=True, secoes=None, prova=None)
        state, perguntas = state_secao(sep, doc, s), P.perguntas_secao(sep["partes"])
        v = _perguntar_validado(jev, state, perguntas, lambda r: validar_nouls(r, list(perguntas)))
        valores.append({"id": s["id"], **v})
    saida, prova, motivo = reduzir(valores)
    return _saida(saida, "jev", motivo, secoes=valores, prova=prova)


def avaliar_inteiro(jev, sep: dict, doc: dict) -> dict:
    """Desenho B, baixo nível (levanta): numérica em código; senão UMA requisição com o documento inteiro."""
    if sep.get("erro"):
        raise ValueError(sep["erro"])
    if sep["numerica"]:
        return avaliar_numerica(sep, doc)
    state = state_documento(sep, doc)
    n = sum(len(s["text"]) for s in state["sections"])
    motivo = texto_longo(n, P.TETO_CARACTERES["documento"], doc.get("id", "?"))
    if motivo:
        return _saida("indecidivel", "longo", motivo, longo=True, valores=None, prova=None)
    ids = [s["id"] for s in state["sections"]]
    perguntas = P.perguntas_documento(ids, sep["partes"])

    def validar(resposta):
        v = validar_nouls(resposta, [q for q in perguntas if q != "proving_section"])
        escolha = CG.choice(resposta, "proving_section", {*ids, P.PROVA_NENHUMA})
        return v, escolha

    valores, escolha = _perguntar_validado(jev, state, perguntas, validar)
    saida, motivo = decidir_inteiro(valores)
    prova = None if escolha["choice"] == P.PROVA_NENHUMA else escolha["choice"]
    return _saida(saida, "jev", motivo + f"; prova {escolha['choice']} {escolha['probabilities'][escolha['choice']]:.2f}",
                  valores=valores, prova=prova, prova_probs=escolha["probabilities"])


def _seguro(f, jev, sep: dict, doc: dict) -> dict:
    """NENHUMA falha sobe nem aborta o lote: condição inválida, documento fora do esquema, timeout, cache faltando,
    resposta fora do contrato, campo com tipo errado → `indecidivel` para AQUELE documento, com o motivo. Pega
    `Exception` inteira de propósito: num filtro, erro não previsto também fecha em "humano lê", nunca em `verdadeiro`."""
    try:
        if sep.get("erro"):
            return _saida("indecidivel", "falha", sep["erro"], falha=True)
        return f(jev, sep, doc)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        return _saida("indecidivel", "falha", f"falha operacional: {type(e).__name__}: {e}"[:160], falha=True)


def avaliar_mapa_seguro(jev, sep: dict, doc: dict) -> dict:
    """O que o consumidor chama (desenho A). @example → {"saida": "indecidivel", "por": "falha", "motivo": "falha operacional: TimeoutError: …", "falha": True}"""
    return _seguro(avaliar_mapa, jev, sep, doc)


def avaliar_inteiro_seguro(jev, sep: dict, doc: dict) -> dict:
    """O que o consumidor chama (desenho B)."""
    return _seguro(avaliar_inteiro, jev, sep, doc)


AVALIAR = {"mapa": avaliar_mapa_seguro, "inteiro": avaliar_inteiro_seguro}
