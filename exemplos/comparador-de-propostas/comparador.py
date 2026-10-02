"""Comparador de propostas: número pelo CÓDIGO, célula semântica pelo Jev, elegíveis e perguntas em código.

Por (proposta, requisito):
  `numerico`  → o texto do requisito termina com "(`campo` <= N)" ou "(`campo` >= N)"; o código lê o limite e
                compara com `campos` (já normalizados pelo rotulador). `null` ou valor não numérico → nao_informado.
  `semantico` → o Jev julga, uma pergunta por requisito, todos os requisitos da proposta na MESMA requisição
                (state = proposta inteira + contexto do comprador + lista de requisitos). Desenho `choice` (Choice
                de 3 + válvula por confiança) ou `nouls` (dois Nouls combinados aqui, exclusão vence).
Elegíveis = propostas sem `contradiz` em requisito obrigatório; perguntas ao fornecedor = `nao_informado` em
obrigatório (LEIA-ME "Elegibilidade"). Os dois são código.

Falha (rede, cache faltando, resposta fora do contrato, entrada inválida): `comparar_proposta_seguro` devolve
TODAS as células semânticas daquela proposta como `nao_informado` marcadas `falha` — a proposta vira pergunta, nunca
`atende` (uma exclusão escondida não pode ser aprovada por um timeout) nem `contradiz` (não se descarta um
fornecedor por falha nossa); a disputa continua. Resposta JSON válida mas rejeitada pela validação sai do cache
(`jev.invalidar`) para não ficar presa e ser reproduzida para sempre. O baixo nível (`comparar_proposta`) levanta.

Revisão adversarial (Codex, 2026-10-01) — o que mudou aqui:
  2. estrutura validada ANTES do lote (`validar_disputa`); a saída de falha não reacessa campo ausente (requisito
     sem `tipo` abortava o lote pela própria rotina de falha);
  5. os Nouls registram `bruto` (leitura dura) e `abstencao` (dúvida → nao_informado), como a Choice;
  6. baseline: negação por fronteira de palavra ("Instalação: não." era `atende`);
  7. pergunta ao fornecedor em linguagem de comprador (campo técnico e parêntese operacional fora).
"""
from __future__ import annotations

import re
import unicodedata

import congelamento as CG
import perguntas as P

NUM = re.compile(r"\(`(\w+)` (<=|>=) (\d+)\)")  # mesmo formato que o validador do rotulador lê
FALHA = "falha operacional"
TIPOS = ("semantico", "numerico")


# ---------------------------------------------------------------- estrutura (antes de qualquer chamada)
def validar_disputa(disputa) -> list[str]:
    """Problemas de estrutura, em texto; lista vazia = disputa utilizável. Nada aqui acessa campo sem conferir."""
    erros: list[str] = []
    if not isinstance(disputa, dict):
        return ["disputa não é objeto"]
    reqs, props = disputa.get("requisitos"), disputa.get("propostas")
    if not isinstance(reqs, list) or not reqs:
        erros.append("sem requisitos")
    else:
        for k, r in enumerate(reqs):
            if not isinstance(r, dict) or not isinstance(r.get("id"), str) or not isinstance(r.get("texto"), str):
                erros.append(f"requisito #{k} sem id/texto")
                continue
            if r.get("tipo") not in TIPOS:
                erros.append(f"requisito {r['id']} com tipo {r.get('tipo')!r}")
            elif r["tipo"] == "numerico" and limite(r) is None:
                erros.append(f"requisito {r['id']} numérico sem limite legível")
            if not isinstance(r.get("obrigatorio"), bool):
                erros.append(f"requisito {r['id']} sem obrigatorio booleano")
    if not isinstance(props, list) or not props:
        erros.append("sem propostas")
    else:
        for k, p in enumerate(props):
            if not isinstance(p, dict) or not isinstance(p.get("id"), str):
                erros.append(f"proposta #{k} sem id")
                continue
            if not isinstance(p.get("texto"), str) or not p["texto"].strip():
                erros.append(f"proposta {p['id']} sem texto")
            if not isinstance(p.get("campos"), dict):
                erros.append(f"proposta {p['id']} sem campos")
    return erros


# ---------------------------------------------------------------- requisito numérico (código)
def limite(requisito: dict) -> tuple[str, str, int] | None:
    """('preco_total', '<=', 30000) lido do texto do requisito; None se não houver."""
    texto = requisito.get("texto") if isinstance(requisito, dict) else None
    m = NUM.search(texto) if isinstance(texto, str) else None
    return (m.group(1), m.group(2), int(m.group(3))) if m else None


def celula_numerica(requisito: dict, proposta: dict) -> str:
    """Compara `campos[campo]` com o limite. Ausente, `null`, bool ou não numérico → nao_informado (pergunta)."""
    lim = limite(requisito)
    if lim is None:
        raise ValueError(f"requisito numérico sem limite legível: {requisito.get('id')}")
    campo, op, n = lim
    campos = proposta.get("campos") if isinstance(proposta, dict) else None
    v = campos.get(campo) if isinstance(campos, dict) else None
    if v is None or isinstance(v, bool) or not isinstance(v, (int, float)):
        return "nao_informado"
    return "atende" if ((v <= n) if op == "<=" else (v >= n)) else "contradiz"


# ---------------------------------------------------------------- state e perguntas (semânticos)
def semanticos(disputa: dict) -> list[dict]:
    return [r for r in disputa["requisitos"] if r["tipo"] == "semantico"]


def pedido(disputa: dict, proposta: dict, desenho: str = P.DESENHO_PADRAO) -> tuple[dict, dict, list[str]] | None:
    """(state, questions, ids dos requisitos na ordem de `requirements`); None se a proposta não tem semântico.
    Estrutura inválida → ValueError (nunca KeyError solto)."""
    erros = validar_disputa(disputa)
    if erros:
        raise ValueError("estrutura: " + "; ".join(erros))
    if not isinstance(proposta, dict) or not isinstance(proposta.get("texto"), str) or not proposta["texto"].strip():
        raise ValueError(f"proposta {proposta.get('id') if isinstance(proposta, dict) else proposta!r} sem texto")
    reqs = semanticos(disputa)
    if not reqs:
        return None
    questions = {}
    for i, _ in enumerate(reqs):
        if desenho == "choice":
            questions[f"req_{i}"] = P.choice(i)
        elif desenho == "nouls":
            questions[f"entrega_{i}"] = P.noul_entrega(i)
            questions[f"exclui_{i}"] = P.noul_exclui(i)
        else:
            raise ValueError(f"desenho desconhecido: {desenho}")
    state = {"proposal": proposta["texto"], "buyer": P.BUYER, "requirements": [r["texto"] for r in reqs]}
    return state, questions, [r["id"] for r in reqs]


# ---------------------------------------------------------------- resposta → célula
def valvula_choice(opcao: str, conf: float, conf_atende: float | None = None, conf_contradiz: float | None = None) -> str:
    """`meets`/`contradicts` abaixo do limiar viram nao_informado (pergunta); `not_stated` fica."""
    conf_atende = P.CONF_ATENDE if conf_atende is None else conf_atende
    conf_contradiz = P.CONF_CONTRADIZ if conf_contradiz is None else conf_contradiz
    celula = P.CELULA_DA_OPCAO[opcao]
    if celula == "atende" and conf < conf_atende:
        return "nao_informado"
    if celula == "contradiz" and conf < conf_contradiz:
        return "nao_informado"
    return celula


def bruto_nouls(entrega: float, exclui: float) -> str:
    """Leitura DURA dos dois Nouls (sem faixa, corte em 0,5): o que o par diz antes de qualquer abstenção."""
    if exclui >= 0.5:
        return "contradiz"
    return "atende" if entrega >= 0.5 else "nao_informado"


def combinar_nouls(entrega: float, exclui: float, faixa_entrega=None, faixa_exclui=None) -> str:
    """Exclusão vence inclusão; dúvida em qualquer um → nao_informado (abstenção)."""
    e_nao, e_sim = faixa_entrega or P.FAIXA_ENTREGA
    x_nao, x_sim = faixa_exclui or P.FAIXA_EXCLUI
    if exclui >= x_sim:
        return "contradiz"
    if entrega >= e_sim and exclui <= x_nao:
        return "atende"
    return "nao_informado"


def ler_resposta(resposta: dict, ids: list[str], desenho: str) -> dict[str, dict]:
    """{rid: {"celula", "bruto", "conf"} | {"celula", "bruto", "abstencao", "entrega", "exclui"}} — validação completa
    ANTES de usar (`congelamento.choice`/`noul`): ID faltando, opção fora da lista, probabilidade bool/string, soma ≠ 1
    → ValueError da integração, nunca uma célula. `bruto` = leitura dura; `abstencao` = a faixa/válvula mandou para
    nao_informado o que a leitura dura decidia."""
    out = {}
    for i, rid in enumerate(ids):
        if desenho == "choice":
            v = CG.choice(resposta, f"req_{i}", set(P.CELULA_DA_OPCAO))
            bruto = P.CELULA_DA_OPCAO[v["choice"]]
            celula = valvula_choice(v["choice"], v["confidence"])
            out[rid] = {"celula": celula, "bruto": bruto, "conf": v["confidence"], "abstencao": celula != bruto}
        else:
            e, x = CG.noul(resposta, f"entrega_{i}"), CG.noul(resposta, f"exclui_{i}")
            bruto, celula = bruto_nouls(e, x), combinar_nouls(e, x)
            out[rid] = {"celula": celula, "bruto": bruto, "entrega": e, "exclui": x, "abstencao": celula != bruto}
    return out


def compor(disputa: dict, proposta: dict, lidas: dict[str, dict] | None) -> dict:
    """Matriz de uma proposta: numéricas pelo código + semânticas lidas (None = nenhuma semântica)."""
    celulas, detalhes = {}, {}
    for r in disputa["requisitos"]:
        if r["tipo"] == "numerico":
            celulas[r["id"]] = celula_numerica(r, proposta)
            detalhes[r["id"]] = {"origem": "codigo"}
        else:
            d = (lidas or {})[r["id"]]
            celulas[r["id"]] = d["celula"]
            detalhes[r["id"]] = {"origem": "jev", **d}
    return {"id": proposta["id"], "celulas": celulas, "detalhes": detalhes}


def comparar_proposta(jev, disputa: dict, proposta: dict, desenho: str = P.DESENHO_PADRAO) -> dict:
    """Baixo nível: uma requisição por proposta; qualquer falha LEVANTA."""
    ped = pedido(disputa, proposta, desenho)
    lidas = ler_resposta(jev.perguntar(ped[0], ped[1]), ped[2], desenho) if ped else None
    return compor(disputa, proposta, lidas)


def _saida_falha(disputa, proposta, motivo: str) -> dict:
    """Saída segura construída SEM reacessar campo obrigatório ausente (achado 2): o que for requisito numérico
    legível continua pelo código; todo o resto é nao_informado."""
    celulas, detalhes = {}, {}
    reqs = disputa.get("requisitos") if isinstance(disputa, dict) else None
    for r in (reqs if isinstance(reqs, list) else []):
        if not isinstance(r, dict) or not isinstance(r.get("id"), str):
            continue
        c, origem = "nao_informado", "falha"
        if r.get("tipo") == "numerico" and limite(r) is not None:
            c, origem = celula_numerica(r, proposta), "codigo"
        celulas[r["id"]] = c
        detalhes[r["id"]] = {"origem": origem}
    pid = proposta.get("id") if isinstance(proposta, dict) else None
    return {"id": pid, "celulas": celulas, "detalhes": detalhes, "falha": motivo}


def comparar_proposta_seguro(jev, disputa: dict, proposta: dict, desenho: str = P.DESENHO_PADRAO) -> dict:
    """O que o consumidor chama: nenhuma falha sobe. Semânticas da proposta → nao_informado com `falha`; as
    numéricas continuam pelo código quando a entrada permite. Resposta inválida sai do cache (`invalidar`).
    @example comparar_proposta_seguro(jev_fora_do_ar, disputa, p1)
             → {"id": "p1", "celulas": {"r1": "nao_informado", "r2": "atende"}, "falha": "falha operacional: chamada (TimeoutError)", …}
    """
    etapa, ped = "entrada inválida", None
    try:
        ped = pedido(disputa, proposta, desenho)
        etapa = "chamada"
        resposta = jev.perguntar(ped[0], ped[1]) if ped else None
        etapa = "resposta inválida"
        return compor(disputa, proposta, ler_resposta(resposta, ped[2], desenho) if ped else None)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring do módulo
        if etapa == "resposta inválida" and ped and hasattr(jev, "invalidar"):
            try:
                jev.invalidar(ped[0], ped[1])
            except Exception:  # noqa: BLE001 — invalidar é melhor esforço; a decisão segura já está tomada
                pass
        return _saida_falha(disputa, proposta, f"{FALHA}: {etapa} ({type(e).__name__})")


# ---------------------------------------------------------------- disputa: elegíveis e perguntas (código)
def elegiveis(disputa: dict, matriz: dict[str, dict[str, str]]) -> list[str]:
    """Sem `contradiz` em obrigatório, na ordem das propostas. `nao_informado` mantém elegível (com pergunta)."""
    obrig = [r["id"] for r in disputa["requisitos"] if r["obrigatorio"]]
    return [p["id"] for p in disputa["propostas"]
            if not any(matriz[p["id"]].get(rid) == "contradiz" for rid in obrig)]


def texto_pergunta(requisito: dict) -> str:
    """Pergunta em linguagem de comprador (achado 7): sem o nome do campo nem o parêntese operacional."""
    lim = limite(requisito)
    enunciado = re.sub(r"\s+([.;,])", r"\1", NUM.sub("", requisito["texto"])).replace("  ", " ").strip()
    if lim:
        return f"Informar {P.CAMPO_LEGIVEL.get(lim[0], lim[0].replace('_', ' '))} — requisito: {enunciado}"
    return f"Confirmar, por escrito e dentro do preço cotado: {enunciado}"


def perguntas_ao_fornecedor(disputa: dict, matriz: dict[str, dict[str, str]]) -> dict[str, list[dict]]:
    """Por proposta elegível: um item por `nao_informado` em obrigatório — o que perguntar antes de decidir."""
    reqs = {r["id"]: r for r in disputa["requisitos"]}
    out = {}
    for pid in elegiveis(disputa, matriz):
        out[pid] = [{"requisito": rid, "pergunta": texto_pergunta(reqs[rid])}
                    for rid, c in matriz[pid].items() if c == "nao_informado" and reqs[rid]["obrigatorio"]]
    return out


def comparar_disputa_seguro(jev, disputa: dict, desenho: str = P.DESENHO_PADRAO) -> dict:
    """Uma disputa de ponta a ponta: estrutura conferida antes de qualquer chamada; 3 propostas (uma requisição
    cada), matriz, elegíveis e perguntas. Estrutura inválida → saída de falha sem chamada e sem elegível."""
    erros = validar_disputa(disputa)
    if erros:
        return {"id": disputa.get("id") if isinstance(disputa, dict) else None, "matriz": {}, "elegiveis": [],
                "perguntas": {}, "propostas": [], "falhas": [f"{FALHA}: estrutura ({'; '.join(erros)})"]}
    saidas = [comparar_proposta_seguro(jev, disputa, p, desenho) for p in disputa["propostas"]]
    matriz = {s["id"]: s["celulas"] for s in saidas}
    return {"id": disputa.get("id"), "matriz": matriz, "elegiveis": elegiveis(disputa, matriz),
            "perguntas": perguntas_ao_fornecedor(disputa, matriz), "propostas": saidas,
            "falhas": [s["falha"] for s in saidas if s.get("falha")]}


# ---------------------------------------------------------------- baseline de código
def normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().casefold()


def _chaves(texto: str) -> set[str]:
    return {w[:5] for w in re.findall(r"[a-z0-9]+", normalizar(NUM.sub("", texto)))
            if len(w) >= 4 and w not in P.BASELINE_STOP}


def baseline_celula(requisito: dict, proposta: dict) -> str:
    """Numérico → mesma comparação; semântico → frase com palavra-chave: marca de exclusão (fronteira de palavra,
    inclusive antes de pontuação ou no fim do texto — achado 6) → contradiz, senão atende; sem frase → nao_informado."""
    if requisito["tipo"] == "numerico":
        return celula_numerica(requisito, proposta)
    chaves = _chaves(requisito["texto"])
    frases = [f for f in re.split(r"(?<!\d)[.;](?!\d)", normalizar(proposta["texto"])) if f.strip()]
    achadas = [f for f in frases if chaves & {w[:5] for w in re.findall(r"[a-z0-9]+", f) if len(w) >= 4}]
    if not achadas:
        return "nao_informado"
    if any(re.search(marca, f) for f in achadas for marca in P.BASELINE_EXCLUSAO):
        return "contradiz"
    return "atende"
