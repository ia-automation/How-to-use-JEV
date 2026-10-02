"""SQL semântico: o código filtra pelos `campos`, UMA requisição ao Jev por linha julga a parte semântica, o código decide.

Saída por linha, para UMA condição — e nada é executado daqui (o consumidor decide o que fazer com a lista):
  verdadeiro    a linha passou no filtro de campos E a observação afirma o fato pedido
  falso         falhou o filtro de campos (sem chamada), ou a observação não diz / nega o fato
  indecidivel   Noul na faixa do meio, pista sem afirmação (variante com `hinted`), texto fora da faixa validada,
                ou falha operacional → humano lê a linha
Divisão: a parte entre crases da condição é do código (`separar` + `passa_filtro`; limite #2: número, data e
igualdade não vão ao Jev); o Jev vê só a frase semântica e o `texto` da linha. Os `campos` não vão no state.
Política assimétrica onde dói: ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO —
`avaliar`/`decidir` levantam exceção; `avaliar_seguro` (o que o consumidor chama) converte a falha em
`indecidivel` para AQUELA linha e tira do cache a resposta inválida (`jev.invalidar`), para que a repetição em
`auto` a refaça em vez de reaproveitá-la. Nunca `verdadeiro`.

Candidato a filtro "em linguagem natural" sobre tabelas do CRM (observações, notas de visita, histórico de chat):
o gestor escreve a condição, o código resolve a parte estruturada, o Jev lê linha a linha o que o SQL não expressa.
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
CAMPOS = ("data", "canal", "finalidade", "orcamento", "visitas", "etapa")
# A mesma gramática do validador do rotulador (dados/valida.py): campo entre crases, operador, valor.
NUMERICO = re.compile(r"`(data|canal|finalidade|orcamento|visitas|etapa)`\s*(<=|>=|=|em)\s*([\w-]+)")
# Toda crase da condição tem de ser uma cláusula válida ANTES de qualquer remoção (revisão do Codex, 2026-10-02, achado
# 1: "(`orcamento` < 500000)" era apagado sem validar e a condição virava "só de campos" sem filtro → `verdadeiro` para
# toda linha). Gramática: campo conhecido, operador do campo, valor do domínio.
_QUALQUER_CRASE = re.compile(r"`([^`]*)`\s*([<>=]+|em|)\s*([\w-]*)")
VALORES = {"canal": {"whatsapp", "telefone", "email", "presencial"}, "finalidade": {"compra", "locacao"},
           "etapa": {"novo", "em_contato", "visita", "proposta", "perdido"}}
# A parte de campo vem entre parênteses ("(`canal` = whatsapp)", "(`orcamento` <= 500000, não nulo)"): o grupo inteiro
# sai da frase semântica. Crase fora de parênteses: sai só a cláusula e o conector que a precede.
_PARENTESE_COM_CRASE = re.compile(r"\s*\([^()]*`[^()]*\)")
_CLAUSULA_SOLTA = re.compile(r"\s*(?:,|\be\b|\bE\b|\bcom\b)?\s*`(?:data|canal|finalidade|orcamento|visitas|etapa)`\s*(?:<=|>=|=|em)\s*[\w-]+(?:,\s*não nulo)?")
# Conector lógico de condição composta: só em MAIÚSCULAS (como o rotulador escreve); "e" minúsculo liga a parte
# numérica em linguagem natural ("e têm orçamento de até…"), que o filtro já resolveu.
_CONECTOR = re.compile(r"\s+(E|OU)\s+")


# ---------------------------------------------------------------------------------------- parte do código
def separar(condicao: str) -> dict:
    """Condição → {"filtros": [(campo, op, valor)], "semantica": str, "partes": [str], "conector": "E"|"OU"|None}.
    `semantica` vazia = condição só de campos (resolvida sem chamada).
    @example separar("Clientes com pet (`canal` = whatsapp).")
             → {"filtros": [("canal", "=", "whatsapp")], "semantica": "Clientes com pet.", "partes": ["Clientes com pet."], "conector": None}
    """
    if not isinstance(condicao, str) or not condicao.strip():
        raise ValueError("condição vazia ou não textual")
    filtros = validar_clausulas(condicao)
    texto = _PARENTESE_COM_CRASE.sub("", condicao)
    texto = _CLAUSULA_SOLTA.sub("", texto)
    if "`" in texto:
        raise ValueError(f"crase que não é cláusula de campo: {texto!r}")
    texto = re.sub(r"\s+", " ", texto).strip()
    texto = re.sub(r"\s*,\s*([.?!]|$)", r"\1", texto).strip(" ,;:")
    if not re.search(r"[^\W\d_]", texto):
        # Resíduo sem letra ("." que sobra de "(`canal` = whatsapp).") não é frase: condição só de campos, zero chamada
        # (revisão do Codex, 2026-10-02, achado 2).
        texto = ""
    partes = [p for p in _CONECTOR.split(texto) if p not in ("E", "OU")] if texto else []
    conectores = set(_CONECTOR.findall(texto))
    if len(conectores) > 1:
        raise ValueError(f"condição mistura E e OU: {condicao!r}")
    partes = [p.strip(" ,;:") for p in partes if p.strip(" ,;:")]
    # Cláusula sem sujeito ("que estão avaliando…") herda o sujeito da frase ("Clientes"): cada Noul vê uma frase inteira.
    sujeito = texto.split(" ", 1)[0] if texto[:1].isupper() else ""
    partes = [p if p[:1].isupper() or not sujeito else f"{sujeito} {p}" for p in partes]
    return {"filtros": filtros, "semantica": texto, "partes": partes if len(partes) > 1 else ([texto] if texto else []),
            "conector": conectores.pop() if conectores and len(partes) > 1 else None}


def validar_clausulas(condicao: str) -> list[tuple]:
    """Toda crase da condição → cláusula válida (campo, op, valor), ou ValueError. Nada é removido antes disto.
    @example validar_clausulas("Clientes com pet (`orcamento` < 500000).") → ValueError (operador `<` não existe)"""
    if condicao.count("`") % 2:
        raise ValueError("crase sem par na condição")
    clausulas = _QUALQUER_CRASE.findall(condicao)
    if len(clausulas) != condicao.count("`") // 2:
        raise ValueError("crase que não é cláusula de campo")
    for campo, op, valor in clausulas:
        if campo not in CAMPOS:
            raise ValueError(f"campo desconhecido: {campo!r}")
        if campo in ("orcamento", "visitas"):
            ok = op in ("<=", ">=", "=") and valor.isdigit()
        elif campo == "data":
            ok = (op == "em" and re.fullmatch(r"\d{4}-\d\d", valor)) or (op == "=" and re.fullmatch(r"\d{4}-\d\d-\d\d", valor))
        else:
            ok = op == "=" and valor in VALORES[campo]
        if not ok:
            raise ValueError(f"cláusula inválida: `{campo}` {op} {valor}")
    return [(c, op, v) for c, op, v in clausulas]


def separar_seguro(condicao) -> dict:
    """O que o lote chama: `separar`, mas condição inválida vira {"erro": …} em vez de exceção — toda linha dela sai
    `indecidivel` por `avaliar_seguro`/`baseline_seguro`, com o erro registrado, e o lote não aborta (achados 1 e 4)."""
    try:
        return separar(condicao)
    except Exception as e:  # noqa: BLE001 — a condição inválida fecha em "humano lê", nunca em `verdadeiro`
        return {"erro": f"condição inválida: {e}", "filtros": [], "semantica": "", "partes": [], "conector": None}


def passa_filtro(campos: dict, filtros: list[tuple]) -> bool:
    """Parte de campo da condição, em Python. Campo nulo ou ausente falha a comparação (LEIA-ME, regra 4: `orcamento`
    nulo é falso, não indecidível). Tipo errado (texto onde se espera número) é ERRO — levanta.
    @example passa_filtro({"orcamento": None}, [("orcamento", "<=", 500000)]) → False
    """
    for campo, op, valor in filtros:
        v = (campos or {}).get(campo)
        if v is None:
            return False
        if campo in ("orcamento", "visitas"):
            if isinstance(v, bool) or not isinstance(v, int):
                raise ValueError(f"campo {campo} com tipo inválido: {v!r}")
            n = int(valor)
            ok = {"<=": v <= n, ">=": v >= n, "=": v == n}.get(op)
        elif campo == "data":
            if not isinstance(v, str):
                raise ValueError(f"campo data com tipo inválido: {v!r}")
            ok = v.startswith(valor) if op == "em" else (v == valor if op == "=" else None)
        else:
            if not isinstance(v, str):
                raise ValueError(f"campo {campo} com tipo inválido: {v!r}")
            ok = (v == valor) if op == "=" else None
        if ok is None:
            raise ValueError(f"operador {op!r} não vale para o campo {campo}")
        if not ok:
            return False
    return True


# ---------------------------------------------------------------------------------------- state e política
def state_de(sep: dict, texto: str) -> dict:
    """Parte semântica + texto da linha → state enxuto com os nomes que as perguntas citam entre crases."""
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("texto da linha vazio ou não textual")
    state = {"condition": sep["semantica"], "note": texto}
    if sep["filtros"]:
        # A parte de campo entra como fato JÁ conferido (2ª passada do ajuste): a frase semântica costuma repeti-la em
        # palavras ("têm orçamento de até R$ 500.000") e, sem isto, o Jev hesitava (falsas a 0,21–0,41 em vez de ≤ 0,05).
        state["checked_by_code"] = [f"{c} {op} {v}" for c, op, v in sep["filtros"]]
    if len(sep["partes"]) > 1:
        state["condition_parts"] = list(sep["partes"])
    return state


def texto_longo(texto: str) -> str | None:
    n = len(texto)
    return f"texto longo ({n} caracteres; teto {P.TETO_CARACTERES})" if n > P.TETO_CARACTERES else None


def validar(resposta: dict, perguntas: dict) -> dict:
    """Resposta da API → {id: valor} validados pela infra comum (todo ID presente, tipo `noul`, número real em [0,1]).
    Qualquer falha = erro operacional (exceção), nunca `verdadeiro` nem `falso`."""
    if not isinstance(resposta, dict):
        raise ValueError(f"resposta não é objeto: {type(resposta).__name__}")
    return {q: CG.noul(resposta, q) for q in perguntas}


def _faixa(valor: float, nao: float, sim: float) -> str:
    if valor >= sim:
        return "verdadeiro"
    if valor <= nao:
        return "falso"
    return "indecidivel"


def combinar(estados: list[str], conector: str) -> str:
    """Regra 5 do LEIA-ME sobre os três estados de cada cláusula (afirmado / fraco / negado-ausente).
    E: todos verdadeiros → verdadeiro; algum falso → falso; senão indecidível.
    OU: algum verdadeiro → verdadeiro; todos falsos → falso; senão indecidível."""
    if conector == "E":
        if all(e == "verdadeiro" for e in estados):
            return "verdadeiro"
        return "falso" if "falso" in estados else "indecidivel"
    if conector == "OU":
        if "verdadeiro" in estados:
            return "verdadeiro"
        return "falso" if all(e == "falso" for e in estados) else "indecidivel"
    raise ValueError(f"conector desconhecido: {conector!r}")


def decidir(valores: dict, conector: str | None, variante: dict | None = None) -> tuple[str, str]:
    """Valores validados → (saída, motivo), pela variante (padrão: `perguntas.VARIANTE`). Guarda os números para o
    relatório recalcular as outras variantes sem chamada."""
    var = variante or P.VARIANTE
    nao, sim = P.FAIXA["stated"]
    partes = [k for k in valores if k.startswith("stated_part_")]
    if var["composta"] == "clausulas" and conector and partes:
        estados = [_faixa(valores[k], nao, sim) for k in sorted(partes, key=lambda k: int(k.rsplit("_", 1)[1]))]
        motivo = f"cláusulas {conector}: " + ", ".join(f"{valores[k]:.2f}" for k in sorted(partes))
        # Válvula da pista ANTES de combinar (revisão do Codex, 2026-10-02, achado 3: o retorno antecipado ignorava a
        # pista; SQ-T14/OB-062 saía `falso` com `hinted` 0,78). `hinted` é da condição INTEIRA (não há um por cláusula —
        # pedir isso seria chamada nova): quando alguma cláusula já está afirmada, a pista vem dela e não diz nada sobre
        # as outras — então a válvula só vale com nenhuma cláusula afirmada, e uma cláusula negada/ausente sem pista
        # continua `falso` (precedência de negação no E preservada: `combinar` não muda).
        if var["pista"] and valores.get("hinted", 0.0) >= P.PISTA_SIM and "verdadeiro" not in estados:
            estados = ["indecidivel" if e == "falso" else e for e in estados]
            motivo += f", hinted {valores['hinted']:.2f}: sugere sem afirmar"
        return combinar(estados, conector), motivo
    saida = _faixa(valores["stated"], nao, sim)
    motivo = f"stated {valores['stated']:.2f}"
    if saida == "falso" and var["pista"] and valores.get("hinted", 0.0) >= P.PISTA_SIM:
        return "indecidivel", motivo + f", hinted {valores['hinted']:.2f}: sugere sem afirmar"
    return saida, motivo


# ---------------------------------------------------------------------------------------- baseline de código
def _plano(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


def palavras_like(semantica: str) -> list[str]:
    """Radicais do LIKE tirados da parte semântica: palavras sem acento, fora da lista genérica, cortadas na 5ª letra.
    @example palavras_like("Clientes que dependem de financiamento bancário.") → ["depen", "finan", "banca"]"""
    saida = []
    for w in re.findall(r"[a-z]+", _plano(semantica)):
        if w in P.BASELINE_IGNORAR or len(w) < 3:
            continue
        r = w[:P.BASELINE_CORTE]
        if r not in saida:
            saida.append(r)
    return saida


def baseline(sep: dict, linha: dict) -> str:
    """Filtro de campos + LIKE de qualquer radical: `verdadeiro` / `falso`. Nunca `indecidivel`. Baixo nível: condição
    inválida ou campo com tipo errado LEVANTAM."""
    if sep.get("erro"):
        raise ValueError(sep["erro"])
    if not passa_filtro(linha["campos"], sep["filtros"]):
        return "falso"
    radicais = palavras_like(sep["semantica"])
    if not radicais:
        return "verdadeiro"
    t = _plano(linha["texto"])
    return "verdadeiro" if any(r in t for r in radicais) else "falso"


def baseline_seguro(sep: dict, linha: dict) -> dict:
    """O que o relatório chama: {"saida", "falha"}; condição inválida ou campo com tipo errado → `indecidivel` marcado
    `falha` (o LIKE não sabe que não sabe, mas o lote não pode abortar nem dar `verdadeiro` — achado 4)."""
    try:
        return {"saida": baseline(sep, linha), "falha": False}
    except Exception as e:  # noqa: BLE001 — falha fechada por linha, como em `avaliar_seguro`
        return {"saida": "indecidivel", "falha": True, "motivo": f"falha operacional: baseline ({type(e).__name__})"}


# ---------------------------------------------------------------------------------------- uma linha
def _saida(saida: str, por: str, motivo: str, valores: dict | None = None, **marcas) -> dict:
    return {"saida": saida, "por": por, "motivo": motivo, "valores": valores, **marcas}


def avaliar(jev, sep: dict, linha: dict) -> dict:
    """Uma linha de ponta a ponta para uma condição já separada: filtro em código (sem chamada quando falha ou
    quando a condição não tem parte semântica), teto, uma requisição, decisão em código. Baixo nível: entrada
    inválida, falha da chamada e resposta fora do contrato LEVANTAM exceção."""
    if sep.get("erro"):
        raise ValueError(sep["erro"])
    if not passa_filtro(linha["campos"], sep["filtros"]):
        return _saida("falso", "filtro", "falhou a parte de campo")
    if not sep["semantica"]:
        return _saida("verdadeiro", "filtro", "condição só de campos")
    motivo = texto_longo(linha["texto"])
    if motivo:
        return _saida("indecidivel", "longo", motivo, longo=True)
    state, perguntas = state_de(sep, linha["texto"]), P.perguntas_de(sep["partes"])
    resposta = jev.perguntar(state, perguntas)
    try:
        valores = validar(resposta, perguntas)
    except Exception:
        _invalidar(jev, state, perguntas)
        raise
    saida, motivo = decidir(valores, sep["conector"])
    return _saida(saida, "jev", motivo, valores)


def _invalidar(jev, state, perguntas: dict) -> None:
    """Resposta com JSON válido que a validação rejeitou: tira SÓ este pedido do cache, senão toda repetição em `auto`
    reaproveitaria a resposta inválida (família "resposta inválida presa no cache"). Só aqui — não em falha de
    chamada (nada foi gravado). Falhar ao invalidar não muda o desfecho."""
    try:
        jev.invalidar(state, perguntas)
    except Exception:  # noqa: BLE001 — a limpeza do cache nunca derruba a falha fechada
        pass


def avaliar_seguro(jev, sep: dict, linha: dict) -> dict:
    """O que o consumidor (filtro em lote) chama: os mesmos passos de `avaliar`, mas NENHUMA falha sobe nem aborta
    o lote — timeout, erro HTTP, cache faltando, resposta fora do contrato, campo com tipo errado ou texto vazio
    viram `indecidivel` para AQUELA linha, com a etapa e a classe do erro no motivo. Pega `Exception` inteira de
    propósito: num filtro, erro não previsto também tem de fechar em "humano lê", nunca em `verdadeiro`.
    @example avaliar_seguro(jev_fora_do_ar, sep, linha) → {"saida": "indecidivel", "por": "falha", "motivo": "falha operacional: chamada (TimeoutError)", "falha": True, …}
    """
    etapa = "filtro"
    try:
        if sep.get("erro"):
            # Condição que `separar` recusou (achado 1): humano lê TODAS as linhas dela, com o motivo; nunca `verdadeiro`.
            return _saida("indecidivel", "falha", sep["erro"], falha=True)
        if not passa_filtro(linha["campos"], sep["filtros"]):
            return _saida("falso", "filtro", "falhou a parte de campo")
        if not sep["semantica"]:
            return _saida("verdadeiro", "filtro", "condição só de campos")
        etapa = "entrada inválida"
        motivo = texto_longo(linha["texto"]) if isinstance(linha["texto"], str) else None
        if motivo:
            return _saida("indecidivel", "longo", motivo, longo=True)
        state, perguntas = state_de(sep, linha["texto"]), P.perguntas_de(sep["partes"])
        etapa = "chamada"
        resposta = jev.perguntar(state, perguntas)
        etapa = "resposta inválida"
        try:
            valores = validar(resposta, perguntas)
        except Exception:
            _invalidar(jev, state, perguntas)
            raise
        saida, motivo = decidir(valores, sep["conector"])
        return _saida(saida, "jev", motivo, valores)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        return _saida("indecidivel", "falha", f"falha operacional: {etapa} ({type(e).__name__})", falha=True)
