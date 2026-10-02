"""Imóvel duplicado: o código compara os números, UMA requisição ao Jev julga o texto do par, o código compõe.

Ação por par de anúncios — e NADA é executado daqui (`unir` é proposta de união para o processo que chama, com a
permissão dele; nenhum anúncio é apagado):
  unir               mesma unidade anunciada duas vezes: sinal forte E zero contradição
  manter_separados   outro imóvel: cidade, quartos ou vagas diferentes (CÓDIGO, sem chamada), prédio/rua
                     diferentes, planta ou detalhe fixo que contradiz (Jev)
  revisar            não fecha para nenhum lado, dúvida num veto, estado/mobília opostos, área sem explicação,
                     bairro que difere só no texto, falha operacional ou anúncio fora da faixa validada → humano
Divisão: números são do código (limite #2) — bairro/cidade, quartos, vagas, área ±3%, preço ±5% e "o texto de um
anúncio declara a relação área total × privativa que explica a diferença" entram no state já calculados em
`numeric_checks`. O Jev lê título e descrição.
Rodada 2 (revisão do Codex, 2026-10-01): metragem do texto é lida por `_comum/numeros_br` (número brasileiro
completo) e só concilia a área com RÓTULO de área da unidade nos dois números (`leitura_area`); bairro que difere
no texto dentro da mesma cidade não é prova de outro imóvel — o par vai ao Jev e não pode sair `unir` (`local`).
Política assimétrica: unir errado apaga um imóvel; por isso dúvida nunca vira `unir`, e o Score só pode TIRAR
uma união, nunca criar. Ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO:
`decidir`/`julgar` levantam exceção; `julgar_seguro` (o que o consumidor chama) converte a falha em `revisar`
para AQUELE par. Nunca `unir`, nunca `manter_separados`.

Candidato a dedup de captação/portais no CRM: roda sobre pares candidatos (mesma cidade/bairro) antes de o
imóvel entrar no catálogo.
"""
from __future__ import annotations

import math
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402
from numeros_br import ler_numeros  # noqa: E402

ACOES = ["unir", "revisar", "manter_separados"]
_TEXTO = ("titulo", "descricao", "bairro", "cidade")
_INTEIROS = ("quartos", "vagas")
_POSITIVOS = ("area_m2", "preco")
# O que vai ao Jev em `numeric_checks` (as mesmas seis chaves da rodada 1: o state dos pares não muda). `fatos`
# devolve também `local` e `area`, leituras de três/quatro valores que só o código consome.
CHAVES_STATE = ("same_neighborhood_and_city", "same_bedrooms", "same_parking_spaces", "area_within_3_percent",
                "area_gap_explained_by_second_figure", "price_within_5_percent")
# Abreviações comuns de bairro/cidade; só valem ANTES de um nome ("V. Mariana"), nunca como última palavra.
_ABREVIACOES = {"v": "vila", "vl": "vila", "jd": "jardim", "sta": "santa", "sto": "santo"}
# Rótulo de área DA UNIDADE colado ao número (sem vírgula nem parêntese no meio). Depois: "92 m² de área total",
# "68 m² privativos", "120 m² úteis". Antes: "Área total de 92 m²", "área privativa 88 m²", "útil 100 m²",
# "apartamento de 92 m²". "total" solto antes do número não vale ("área comum total de 68 m²" não é a unidade).
_PRIV = r"privativ[ao]s?|[uú]til|[uú]teis"
_ROTULO_DEPOIS = re.compile(rf"\s*(?:de\s+)?(?:[aá]rea\s+)?(?P<tipo>tota(?:l|is)|{_PRIV})\b", re.IGNORECASE)
_ROTULO_ANTES = re.compile(rf"\b(?P<tipo>[aá]rea\s+total|(?:[aá]rea\s+)?(?:{_PRIV}))\s*(?:de\b|:|=)?\s*$", re.IGNORECASE)
_UNIDADE_ANTES = re.compile(r"\b(?:apartamento|apto\.?|unidade|im[oó]vel)\s+(?:de|com)\s*$", re.IGNORECASE)


# ---------------------------------------------------------------------------------------- fatos do código
def _plano(texto: str) -> str:
    """Minúsculas, sem acento, pontuação vira espaço, abreviação comum por extenso — bairro e cidade são
    comparados assim. @example _plano("V. Mariana") → "vila mariana"; _plano("Jd. São Luís") → "jardim sao luis"
    """
    sem = unicodedata.normalize("NFKD", texto.casefold()).encode("ascii", "ignore").decode()
    palavras = re.sub(r"[^a-z0-9]+", " ", sem).split()
    return " ".join(_ABREVIACOES.get(p, p) if i < len(palavras) - 1 else p for i, p in enumerate(palavras))


def local(a: dict, b: dict) -> str:
    """Bairro e cidade do par em três valores. `distinto` exige PROVA: cidades diferentes. Bairro que difere no
    texto dentro da mesma cidade ("Vila Mariana" × "Vila Clementino", ou uma grafia que a normalização não
    alcança) é `indefinido`: o mesmo prédio aparece com dois nomes de bairro, e o código não tem como saber.
    @example local({…"bairro": "Vila Mariana", "cidade": "São Paulo"}, {…"bairro": "V. Mariana", "cidade": "Sao Paulo"}) → "igual"
    """
    ca, cb = _plano(a["cidade"]), _plano(b["cidade"])
    if ca != cb:
        return "distinto"
    ba, bb = _plano(a["bairro"]), _plano(b["bairro"])
    return "igual" if ca and ba and ba == bb else "indefinido"


def _perto(x: float, y: float, tolerancia: float) -> bool:
    """A fórmula do LEIA-ME, literal: |a − b| / max(a, b) ≤ tolerância."""
    return abs(x - y) / max(x, y) <= tolerancia


def validar_anuncio(anuncio: dict) -> None:
    """Campos e tipos do anúncio ANTES de qualquer conta ou chamada; erro = falha de entrada (→ `revisar`)."""
    if not isinstance(anuncio, dict):
        raise ValueError("anúncio não é objeto")
    for campo in _TEXTO:
        if not isinstance(anuncio.get(campo), str) or not anuncio[campo].strip():
            raise ValueError(f"anúncio sem `{campo}` textual")
    for campo in _INTEIROS:
        v = anuncio.get(campo)
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise ValueError(f"`{campo}` inválido: {v!r}")
    for campo in _POSITIVOS:
        v = anuncio.get(campo)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
            raise ValueError(f"`{campo}` inválido: {v!r}")


def _metragens(anuncio: dict) -> tuple[list[tuple[float, str]], list[float], bool]:
    """Metragens (unidade m²) de título + descrição, lidas pelo leitor comum de números brasileiros:
    (rotuladas [(valor, tipo)], soltas [valor], conflito). tipo = `total`, `privativa` (privativa ou útil) ou
    `unidade` ("apartamento de 92 m²"). `conflito`: o mesmo número com dois rótulos diferentes, dois valores
    para o mesmo tipo, ou número em formato ambíguo ("68.5 m²") — o texto não serve de prova.
    @example _metragens({…"descricao": "Apartamento de 92 m² com salão comum de 68 m²"}) → ([(92.0, "unidade")], [68.0], False)
    """
    texto = anuncio["titulo"] + " " + anuncio["descricao"]
    rotuladas, soltas, conflito = [], [], False
    for n in ler_numeros(texto):
        if n.unidade != "m2":
            continue
        if n.ambiguo:
            soltas.append(n.valor)
            conflito = True
            continue
        antes, depois = _ROTULO_ANTES.search(texto[:n.inicio]), _ROTULO_DEPOIS.match(texto, n.fim)
        tipos = {"total" if "tota" in m.group("tipo").lower() else "privativa" for m in (antes, depois) if m}
        if not tipos and _UNIDADE_ANTES.search(texto[:n.inicio]):
            tipos = {"unidade"}
        if len(tipos) == 1:
            rotuladas.append((n.valor, tipos.pop()))
        else:
            soltas.append(n.valor)
            conflito = conflito or bool(tipos)
    for tipo in {t for _, t in rotuladas}:
        valores = [v for v, t in rotuladas if t == tipo]
        conflito = conflito or not all(_perto(v, valores[0], P.TOLERANCIA_AREA) for v in valores)
    return rotuladas, soltas, conflito


def leitura_area(a: dict, b: dict) -> str:
    """A área do par em quatro valores:
      dentro      áreas declaradas dentro de ±3%;
      conciliada  divergem, mas o texto de UM anúncio declara a relação com rótulo nos dois números: a própria
                  área e a do outro, com tipos diferentes ("Área total de 92 m² (68 m² privativos)" × 68 m²), sem
                  conflito em nenhum dos dois textos e sem o outro texto desmentir (o mesmo tipo com outro valor);
      indefinida  divergem e alguma metragem de um texto bate com a área do outro, mas sem essa prova ("salão
                  comum de 68 m²", número sem rótulo, texto em conflito): coincidência não concilia → `revisar`;
      diverge     divergem e nenhuma metragem do texto bate.
    @example leitura_area({…"area_m2": 68…}, {…"area_m2": 92, "descricao": "Apartamento de 92 m² com salão comum de 68 m²"}) → "indefinida"
    """
    perto = lambda x, y: _perto(x, y, P.TOLERANCIA_AREA)  # noqa: E731
    if perto(a["area_m2"], b["area_m2"]):
        return "dentro"
    ma, mb = _metragens(a), _metragens(b)
    conflito = ma[2] or mb[2]
    desmente = any(ta == tb and ta != "unidade" and not perto(va, vb) for va, ta in ma[0] for vb, tb in mb[0])
    coincide = prova = False
    for (rotuladas, soltas, _), x, y in ((ma, a, b), (mb, b, a)):
        do_outro = {t for v, t in rotuladas if perto(v, y["area_m2"])}
        proprio = {t for v, t in rotuladas if perto(v, x["area_m2"])}
        prova = prova or bool(do_outro and proprio and do_outro != proprio)
        coincide = coincide or bool(do_outro) or any(perto(v, y["area_m2"]) for v in soltas)
    if prova and not conflito and not desmente:
        return "conciliada"
    return "indefinida" if coincide else "diverge"


def fatos(a: dict, b: dict) -> dict:
    """Os sinais do par, calculados pelo código. As seis chaves de `CHAVES_STATE` vão ao state como
    `numeric_checks` (fatos prontos, sempre booleanos: `True` só com prova); `local` e `area` são as mesmas
    leituras com o valor "indefinido" à vista, para a política e o motivo.
    @example fatos({…"area_m2": 68, "preco": 790000…}, {…"area_m2": 92, "preco": 775000, "descricao": "…Área total de 92 m² (68 m² privativos)…"})
             → {…, "area_within_3_percent": False, "area_gap_explained_by_second_figure": True, "price_within_5_percent": True,
                "local": "igual", "area": "conciliada"}
    """
    lugar, area = local(a, b), leitura_area(a, b)
    return {
        "same_neighborhood_and_city": lugar == "igual",
        "same_bedrooms": a["quartos"] == b["quartos"],
        "same_parking_spaces": a["vagas"] == b["vagas"],
        "area_within_3_percent": area == "dentro",
        "area_gap_explained_by_second_figure": area == "conciliada",
        "price_within_5_percent": _perto(a["preco"], b["preco"], P.TOLERANCIA_PRECO),
        "local": lugar,
        "area": area,
    }


def baseline(a: dict, b: dict) -> dict:
    """O dedup por regra: mesmos bairro/cidade + quartos + vagas + área ±3% + preço ±5% ⇒ unir; senão separados.
    Nunca diz `revisar`: regra não sabe que não sabe."""
    f = fatos(a, b)
    igual = all(f[k] for k in ("same_neighborhood_and_city", "same_bedrooms", "same_parking_spaces",
                               "area_within_3_percent", "price_within_5_percent"))
    return {"acao": "unir" if igual else "manter_separados"}


def baseline_seguro(a: dict, b: dict) -> dict:
    """O baseline como o relatório o chama: anúncio inválido não vira conta (`area_m2: null` abortava o lote
    inteiro) — sai `revisar` para aquele par, contado à parte. É a única vez que o baseline diz `revisar`."""
    try:
        validar_anuncio(a)
        validar_anuncio(b)
    except ValueError:
        return {"acao": "revisar"}
    return baseline(a, b)


# ---------------------------------------------------------------------------------------- state e saídas
def state_de(a: dict, b: dict, f: dict) -> dict:
    """State enxuto: só título e descrição de cada anúncio (o que as perguntas leem) + os fatos do código.
    Área, preço, quartos e vagas NÃO vão como valor: comparação numérica não é pedida ao Jev."""
    return {"a": {"title": a["titulo"], "description": a["descricao"]},
            "b": {"title": b["titulo"], "description": b["descricao"]},
            "numeric_checks": {k: f[k] for k in CHAVES_STATE}}


def _sem_jev(acao: str, motivo: str, origem: str, f: dict | None) -> dict:
    """Decisão sem números do Jev. `origem`: `codigo` (decidido pelos fatos), `longo` (fora da faixa) ou `falha`."""
    return {"acao": acao, "motivo": motivo, "origem": origem, "fatos": f,
            "nouls": {q: None for q in P.NOULS}, "sinais": {q: None for q in P.NOULS},
            "score": None, "score_conf": None, "score_probs": {}}


def decisao_do_codigo(f: dict) -> dict | None:
    """O que o código resolve exato não vai ao Jev: cidade, quartos ou vagas diferentes = outro imóvel (regra do
    LEIA-ME). Bairro que difere só no texto (`local` indefinido) NÃO é decidido aqui. None = o par precisa da
    leitura do texto."""
    if f["local"] == "distinto":
        return _sem_jev("manter_separados", "cidades diferentes (código)", "codigo", f)
    if not (f["same_bedrooms"] and f["same_parking_spaces"]):
        return _sem_jev("manter_separados", "quartos ou vagas diferentes: outra planta (código)", "codigo", f)
    return None


def par_longo(state: dict) -> str | None:
    """Motivo se o texto do par passa do teto; None dentro da faixa validada."""
    n = sum(len(state[k]["title"]) + len(state[k]["description"]) for k in ("a", "b"))
    return f"anúncio longo ({n} caracteres no par; teto {P.TETO_CARACTERES})" if n > P.TETO_CARACTERES else None


def decisao_falha(tipo: str, f: dict | None = None) -> dict:
    """Falha operacional (entrada, chamada ou contrato da resposta): humano lê. O motivo leva só a etapa e a
    classe do erro — o texto da exceção pode citar o corpo da resposta. `f` = fatos do código quando a falha
    veio DEPOIS deles (chamada, resposta); entrada inválida não tem fatos (None) e ninguém os recalcula."""
    return _sem_jev("revisar", f"falha operacional: {tipo}", "falha", f)


# ---------------------------------------------------------------------------------------- resposta → decisão
def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    """Noul em três faixas: True / False / None (= dúvida)."""
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def _score(resposta: dict, q: str, niveis: int) -> dict:
    """Score validado (a infra comum só valida Noul e Choice): número real finito em [0, níveis−1], distribuição
    com exatamente os níveis esperados somando ~1, confiança em [0, 1]. Qualquer desvio = ValueError."""
    a = (resposta.get("answers") or {}).get(q)
    if not isinstance(a, dict) or a.get("type", "score") != "score":
        raise ValueError(f"resposta sem Score válido para {q!r}")
    s = a.get("score")
    if isinstance(s, bool) or not isinstance(s, (int, float)) or not math.isfinite(s) or not 0 <= s <= niveis - 1:
        raise ValueError(f"score inválido em {q!r}: {s!r}")
    probs = {k: CG.probabilidade(v) for k, v in (a.get("probabilities") or {}).items()}
    if set(probs) != {str(i) for i in range(niveis)} or abs(sum(probs.values()) - 1.0) > 0.02:
        raise ValueError(f"probabilidades inválidas em {q!r}: {probs}")
    return {"score": float(s), "score_conf": CG.probabilidade(a.get("confidence")), "score_probs": probs}


def validar(resposta: dict) -> dict:
    """Resposta da API → números validados: todo ID esperado presente, `type` batendo, Noul real em [0,1] (não
    bool, não string), Score dentro dos níveis. Falha = erro operacional (exceção), nunca decisão."""
    answers = resposta.get("answers") or {}
    for q, p in P.PERGUNTAS.items():
        a = answers.get(q)
        if not isinstance(a, dict) or a.get("type", p["type"]) != p["type"]:
            raise ValueError(f"resposta sem `{q}` do tipo {p['type']}")
    return {"nouls": {q: CG.noul(resposta, q) for q in P.NOULS}, **_score(resposta, P.SCORE, len(P.NIVEIS))}


def acao_nouls(v: dict, f: dict) -> tuple[str, str]:
    """(ação, motivo) só com os Nouls e os fatos do código. Ordem: vetos com `sim` separam; veto em dúvida,
    bairro indefinido, estado oposto, área sem prova de conciliação ou falta do sinal forte → `revisar`; só o
    que sobra é `unir`."""
    n = v["nouls"]
    s = {q: _faixa(n[q], *P.FAIXA[q]) for q in P.NOULS}
    nomes = {"address_conflict": "prédios ou ruas diferentes", "layout_contradiction": "planta contradiz (cômodo estrutural)",
             "fixed_contradiction": "detalhe fixo contradiz"}
    if s["address_conflict"] is True and s["same_building_or_street"] is True:
        # As duas leituras do endereço se contradizem (identidades entre perguntas não valem, limite #8):
        # nenhuma decide sozinha um `manter_separados`.
        return "revisar", "endereço lido como igual E diferente"
    separa = [nomes[q] for q in P.VETOS if s[q] is True]
    if separa:
        return "manter_separados", "; ".join(separa)
    duvida = [f"{nomes[q]}? ({n[q]:.2f})" for q in P.VETOS if s[q] is None]
    if duvida:
        return "revisar", "dúvida: " + "; ".join(duvida)
    if f["local"] != "igual":
        return "revisar", "bairro difere no texto, sem prova de que é outro lugar (código)"
    if s["state_contradiction"] is not False:
        return "revisar", f"estado ou mobília opostos ({n['state_contradiction']:.2f}): mesma unidade em outro momento ou a vizinha"
    if f["area"] == "indefinida":
        return "revisar", "área diverge; a metragem que bate no texto não está rotulada como área da unidade (código)"
    if f["area"] not in ("dentro", "conciliada"):
        return "revisar", "área diverge sem explicação no texto (código)"
    if s["shared_distinctive_details"] is not True:
        return "revisar", f"sem detalhe distintivo em comum ({n['shared_distinctive_details']:.2f})"
    return "unir", "mesmos detalhes da unidade, nenhuma contradição"


def acao_score(v: dict) -> tuple[str, str]:
    """(ação, motivo) só com o Score, pelo arredondamento da receita (cortes em `perguntas`). Só para MEDIR."""
    separa, une = P.SCORE_ARREDONDA
    if v["score"] >= une:
        return "unir", f"Score {v['score']:.2f}"
    if v["score"] <= separa:
        return "manter_separados", f"Score {v['score']:.2f}"
    return "revisar", f"Score {v['score']:.2f}"


def compor(v: dict, f: dict) -> dict:
    """Números validados + fatos do código → decisão da POLÍTICA (guarda os números para medir e re-limiar sem
    chamar de novo). O Score só entra como segunda leitura do lado caro: tira uma união, não cria."""
    acao, motivo = acao_nouls(v, f)
    if acao == "unir" and P.USAR_SCORE and v["score"] < P.SCORE_UNIR_MIN:
        acao, motivo = "revisar", f"Nouls dizem unir, Score não confirma ({v['score']:.2f})"
    return {"acao": acao, "motivo": motivo, "origem": "jev", "fatos": f, "nouls": v["nouls"],
            "sinais": {q: _faixa(v["nouls"][q], *P.FAIXA[q]) for q in P.NOULS},
            "score": v["score"], "score_conf": v["score_conf"], "score_probs": v["score_probs"]}


def decidir(resposta: dict, f: dict) -> dict:
    """Resposta JSON da API + fatos do código → decisão. Resposta fora do contrato LEVANTA exceção."""
    return compor(validar(resposta), f)


def julgar(jev, a: dict, b: dict) -> dict:
    """Um par de ponta a ponta: anúncios validados, fatos do código, decisão do código quando basta (sem
    chamada), teto conferido, uma requisição, composição. Baixo nível: anúncio inválido, falha da chamada e
    resposta fora do contrato LEVANTAM exceção."""
    validar_anuncio(a)
    validar_anuncio(b)
    f = fatos(a, b)
    pronto = decisao_do_codigo(f)
    if pronto:
        return pronto
    state = state_de(a, b, f)
    motivo = par_longo(state)
    if motivo:
        return _sem_jev("revisar", motivo, "longo", f)
    return decidir(jev.perguntar(state, P.PERGUNTAS), f)


def julgar_seguro(jev, a: dict, b: dict) -> dict:
    """O que o consumidor (dedup de captação, lote) chama: os mesmos passos de `julgar`, mas NENHUMA falha sobe
    nem aborta o lote — timeout, erro HTTP, cache faltando, resposta fora do contrato ou anúncio inválido viram
    `revisar` para AQUELE par, com a etapa e a classe do erro no motivo. Pega `Exception` inteira de propósito:
    num dedup, erro não previsto também tem de fechar em `revisar` (nunca `unir`, nunca `manter_separados`).
    @example julgar_seguro(jev_fora_do_ar, a, b) → {"acao": "revisar", "motivo": "falha operacional: chamada (TimeoutError)", "origem": "falha", …}
    """
    etapa, f = "entrada inválida", None
    try:
        validar_anuncio(a)
        validar_anuncio(b)
        f = fatos(a, b)
        pronto = decisao_do_codigo(f)
        if pronto:
            return pronto
        state = state_de(a, b, f)
        motivo = par_longo(state)
        if motivo:
            return _sem_jev("revisar", motivo, "longo", f)
        etapa = "chamada"
        resposta = jev.perguntar(state, P.PERGUNTAS)
        etapa = "resposta inválida"
        return decidir(resposta, f)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        return decisao_falha(f"{etapa} ({type(e).__name__})", f)
