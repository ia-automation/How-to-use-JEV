"""Conferência de promessas: número pelo CÓDIGO, relação semântica pelo Jev, ação por afirmação em código.

Para cada afirmação do rascunho:
  caminho `codigo`   → tem número e dimensão conhecida (quartos, vagas, área, preço, condomínio, distância ao
                       metrô), a ficha tem o valor, e o extrator interpretou TODAS as proposições da frase
                       (número, negação, "vaga" sem número): o código compara e decide sozinho.
  caminho `composta` → número + algo que o extrator não interpretou ("2 vagas cobertas", "condomínio de 450 já
                       inclui luz", parte cujo campo a ficha não tem): o código compara o que resolveu; se bate,
                       o resto vai ao Jev. Contradição numérica provada vence sempre.
  caminho `jev`      → sem número comparável, ou negação que o código não interpreta ("Não tem 2 vagas"):
                       uma Choice supported/contradicted/not_stated.
Ação: manter / retirar / revisar pelos limiares de `perguntas.py`. Resposta do Jev inválida (ID faltando, opção
fora da lista, probabilidades não somando 1, confiança fora de [0,1]) é ERRO operacional, nunca "not_stated"
nem "manter" (AGENTS §10; validação em `_comum/congelamento.py`).

Revisão adversarial (Codex, 2026-10-01) — o que mudou aqui e por quê:
  2. polaridade: "Tem 3 quartos e vaga" × `vagas: 0` e "Não tem 2 vagas" × `vagas: 2` viravam supported pelo
     código, porque "vaga" sem número só contava quando a frase não tinha número nenhum e "nao"/"sem" eram
     descartados como palavra de ligação. Agora a frase só é numérica pura se tudo foi interpretado.
  3. ponto de milhar: "A 1.200 m do metrô" na descrição era partido no "." e virava 200 m.
  4. "milhão/milhões" não existia na gramática: "1,9 milhão" comparava 1,9 com 2.100.000 (acerto pelo motivo
     errado). Multiplicador desconhecido agora bloqueia a decisão numérica em vez de comparar truncado.
  5. parte sem valor na ficha apagava uma contradição já provada em outra dimensão.
  6. a Choice passa pela validação completa (`congelamento.choice`) antes de qualquer decisão.
"""
from __future__ import annotations

import re
import unicodedata

import congelamento as CG
import perguntas as P

# ---------------------------------------------------------------- normalização
_NUM_PALAVRA = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6,
                "sete": 7, "oito": 8, "nove": 9, "dez": 10}


def normalizar(texto: str) -> str:
    """Sem acento, minúsculas; NFKD também transforma 'm²' em 'm2'."""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().casefold()


def _valor(txt: str) -> float:
    """'1.200' → 1200; '890.000' → 890000; '1,5' → 1.5."""
    return float(txt.replace(".", "").replace(",", "."))


# Gramática numérica INTEIRA: número (dígitos ou palavra) + multiplicador opcional + unidade opcional.
# Após `normalizar`, "milhão" é "milhao" e "milhões" é "milhoes". 'km' vira metros; 'min' marca minutos.
_MULT = {"mil": 1_000, "milhao": 1_000_000, "milhoes": 1_000_000}
_UNIDADES = ("km", "m2", "metros quadrados", "metros", "m", "minutos", "min", "reais", "%", "kg", "horas", "h")
_NUMERO = re.compile(
    r"(?<![\w$])(?P<n>\d{1,3}(?:\.\d{3})+|\d+(?:,\d+)?|" + "|".join(_NUM_PALAVRA) + r"|mil)"
    r"(?:\s*(?P<mult>" + "|".join(_MULT) + r"))?"
    r"(?:\s*(?P<u>" + "|".join(_UNIDADES) + r"))?(?![\w])"
)
_UNIDADE_IGNORADA = {"%", "kg", "horas", "h"}  # número com essas unidades não é dimensão da ficha
# Negação: só o padrão "sem / não tem / nenhuma / zero vaga(s)" é interpretado (= 0 vagas). Qualquer outra
# negação deixa a polaridade do número indefinida ("Não tem 2 vagas", "não tem mais de 2 vagas"): o código
# NÃO decide — nem supported nem contradicted — e a frase inteira vai ao Jev.
_NEGACAO = re.compile(r"\b(nao|sem|nenhum|nenhuma|nunca|zero)\b")
# Fim de frase na descrição: "." ou ";" que NÃO está entre dígitos ("1.200 m" é um número, não duas frases).
_FIM_DE_FRASE = re.compile(r"(?<!\d)[.;]|[.;](?!\d)")

# dimensão → (regex no texto normalizado da afirmação, nome do campo da ficha, é contagem exata?)
DIMENSOES = {
    "quartos": (re.compile(r"\b(quartos?|dormitorios?)\b"), "quartos", True),
    "vagas": (re.compile(r"\b(vagas?|garagem|carros?)\b"), "vagas", True),
    "area": (re.compile(r"\b(m2|metros quadrados)\b"), "area_m2", False),
    "terreno": (re.compile(r"\bterreno\b"), None, False),  # só na descrição ("terreno de N m²")
    "condominio": (re.compile(r"\bcondominio\b"), "condominio_reais", False),
    "preco": (re.compile(r"\b(custa|preco|valor|r\$|mil|reais)\b"), None, False),  # só na descrição (R$ …)
    "distancia": (re.compile(r"\b(metro|estacao)\b"), "distancia_metro_m", False),
}
TOLERANCIA = 0.05  # medidas (área, dinheiro, metros × metros): ≤ 5% = igual (LEIA-ME "aproximação numérica")
TOLERANCIA_MINUTOS = 0.5  # metros ↔ minutos a pé (~80 m/min): ±50% (LEIA-ME "distância estimada")
METROS_POR_MINUTO = 80

_COMPARADOR = [(re.compile(r"\b(mais de|acima de|superior a)\s*$"), ">"),
               (re.compile(r"\b(menos de|abaixo de|inferior a)\s*$"), "<"),
               (re.compile(r"\b(ate|no maximo)\s*$"), "<="),
               (re.compile(r"\b(pelo menos|no minimo)\s*$"), ">=")]
_SEM_VAGA = re.compile(r"\b(sem|nao tem|nenhuma|zero)\s+vagas?\b")

# Palavras de LIGAÇÃO: não carregam proposição, então não contam como sobra. Negação ("nao", "sem") e
# palavras de dimensão ("vaga", "quartos", "metro") NÃO estão aqui: ou o extrator as interpreta e as consome,
# ou elas sobram e a frase vira composta (achado 2 da revisão: descartá-las escondia polaridade e proposição).
_LIGACAO = {
    "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "e", "tem", "fica",
    "vem", "sao", "com", "ha", "possui", "conta", "imovel", "apartamento", "casa", "so", "apenas", "exatos",
    "mais", "menos", "cerca", "quase", "aproximadamente", "uns", "umas", "ate", "acima", "abaixo", "pelo",
    "pela", "minimo", "maximo", "superior", "inferior", "torno", "volta", "por", "r$", "r", "reais", "mil",
    "km", "m2", "m", "metros", "quadrados", "minutos", "min", "pe", "ao", "para", "area", "util", "construida",
    "construidos", "total", "taxa", "mensal", "mes", "dista", "distancia", "caminhando", "andando", "andar",
    "ir", "chegar",
}


# ---------------------------------------------------------------- ficha: valor por dimensão
def _dinheiro_descricao(descricao: str) -> list[tuple[bool, float]]:
    """[(é condomínio?, valor)] para cada 'R$ N' da descrição (condomínio = palavra nos 25 chars antes)."""
    t = normalizar(descricao)
    out = []
    for m in re.finditer(r"r\$\s*(\d{1,3}(?:\.\d{3})+|\d+(?:,\d+)?)(?:\s*(" + "|".join(_MULT) + r"))?\b", t):
        v = _valor(m.group(1)) * _MULT.get(m.group(2), 1)
        out.append(("condominio" in t[max(0, m.start() - 25):m.start()], v))
    return out


def valor_ficha(dim: str, ficha: dict) -> tuple[float, bool] | None:
    """(valor em unidade da ficha, veio em minutos?) ou None quando a ficha não declara."""
    campos = ficha.get("campos") or {}
    campo = DIMENSOES[dim][1]
    if campo and campos.get(campo) is not None:
        return float(campos[campo]), False
    t = normalizar(ficha.get("descricao", ""))
    if dim == "terreno":
        m = re.search(r"terreno de (\d{1,3}(?:\.\d{3})+|\d+)\s*m2", t)
        return (_valor(m.group(1)), False) if m else None
    if dim in ("preco", "condominio"):
        for eh_cond, v in _dinheiro_descricao(ficha.get("descricao", "")):
            if eh_cond == (dim == "condominio"):
                return v, False
        return None
    if dim == "distancia":  # frase da descrição que fala do metrô e traz número + unidade
        for frase in _FIM_DE_FRASE.split(t):  # achado 3: "1.200 m" não é fim de frase
            if re.search(r"\b(metro|estacao)\b", frase):
                m = re.search(r"(\d{1,3}(?:\.\d{3})+|\d+(?:,\d+)?)\s*(km|m|metros|minutos|min)\b", frase)
                if m:
                    v, u = _valor(m.group(1)), m.group(2)
                    if u in ("minutos", "min"):
                        return v * METROS_POR_MINUTO, True
                    return (v * 1000 if u == "km" else v), False
        return None
    return None


# ---------------------------------------------------------------- afirmação: partes numéricas
def _dentro(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(a <= pos < b for a, b in spans)


def _palavra_conhecida(w: str) -> bool:
    """Palavra que a gramática entende logo depois de um número nu: ligação, dimensão, número por extenso."""
    return w in _LIGACAO or w in _NUM_PALAVRA or w in _MULT or any(rx.fullmatch(w) for rx, _, _ in DIMENSOES.values())


def interpretar(texto: str) -> tuple[list[dict], list[str]]:
    """([{dim, valor, comparador, minutos}], sobra) — o extrator marca o que CONSUMIU; `sobra` são as palavras
    que ele não interpretou. Frase numérica pura = partes e sobra vazia. Regras (LEIA-ME + revisão):
      - "sem / não tem / nenhuma / zero vaga(s)" = 0 vagas; qualquer OUTRA negação não é interpretada e, como
        inverte o sentido do número, nenhuma parte numérica é devolvida (a frase inteira vai ao Jev);
      - número nu (sem unidade nem multiplicador) seguido de palavra desconhecida ("1,9 bilhão", "2 suítes") não
        é interpretado: pode ser um multiplicador que o código não conhece, e comparar truncado seria mentir;
      - "vaga/garagem" sem número = pelo menos 1 (regra do LEIA-ME); outra palavra de dimensão sem número sobra.
    """
    t = normalizar(texto)
    consumido: list[tuple[int, int]] = []
    partes: list[dict] = []
    for m in _SEM_VAGA.finditer(t):  # "não tem vaga" = 0 vagas: a negação É interpretada aqui
        partes.append({"dim": "vagas", "valor": 0.0, "comparador": "=", "minutos": False})
        consumido.append(m.span())
    if any(not _dentro(m.start(), consumido) for m in _NEGACAO.finditer(t)):
        return [], ["(negação não interpretada)"]
    numeros = list(_NUMERO.finditer(t))
    spans_num = [m.span() for m in numeros]
    dims = sorted((m.start(), m.end(), dim) for dim, (rx, _, _) in DIMENSOES.items() for m in rx.finditer(t)
                  if not _dentro(m.start(), spans_num + consumido))
    if any(d == "condominio" for _, _, d in dims):  # "condomínio custa R$ 520": o dinheiro é o condomínio
        consumido += [x[:2] for x in dims if x[2] == "preco"]  # "custa"/"r$" interpretados, não sobram
        dims = [x for x in dims if x[2] != "preco"]
    ligadas: set[int] = set()  # índices de `dims` já ligados a um número (cada palavra liga a um número só)

    def ligar(j: int) -> None:
        ligadas.add(j)
        consumido.append(dims[j][:2])

    for k, m in enumerate(numeros):
        bruto, mult, u = m.group("n"), m.group("mult"), m.group("u")
        if u in _UNIDADE_IGNORADA:  # "10 kg", "24 horas": número que não é dimensão da ficha
            consumido.append(m.span())
            continue
        seguinte = re.match(r"\s*([a-z$]+)", t[m.end():])
        if not u and not mult and seguinte and not _palavra_conhecida(seguinte.group(1)):
            continue  # número + palavra desconhecida: não interpretado (número e palavra ficam na sobra)
        v = 1000.0 if bruto == "mil" else (float(_NUM_PALAVRA[bruto]) if bruto in _NUM_PALAVRA else _valor(bruto))
        v *= _MULT.get(mult, 1)
        minutos = u in ("minutos", "min")
        if u == "km":
            v *= 1000
        elif minutos:
            v *= METROS_POR_MINUTO
        # dimensão: unidade inequívoca decide; senão a 1ª palavra de dimensão depois do número (antes do número
        # seguinte), senão a última antes dele.
        if u in ("m2", "metros quadrados"):
            dim = "terreno" if any(d == "terreno" for _, _, d in dims) else "area"
        elif minutos or u == "km" or (u in ("m", "metros") and any(d == "distancia" for _, _, d in dims)):
            dim = "distancia"
        else:
            prox = numeros[k + 1].start() if k + 1 < len(numeros) else len(t) + 1
            depois = [j for j, (p, _, d) in enumerate(dims) if m.end() <= p < prox and d != "preco" and j not in ligadas]
            antes = [j for j, (p, _, _) in enumerate(dims) if p < m.start() and j not in ligadas]
            j = (depois or antes[::-1] or [None])[0]
            if j is None:
                continue  # número sem dimensão: fica na sobra
            dim = dims[j][2]
            ligar(j)
        for j, (_, _, d) in enumerate(dims):  # a palavra da dimensão decidida pela unidade ("do metrô") é consumida
            if d == dim and j not in ligadas:
                ligar(j)
                break
        comp = "="
        for rx, c in _COMPARADOR:
            mc = rx.search(t[:m.start()])
            if mc:
                comp = c
                consumido.append(mc.span())
                break
        consumido.append(m.span())
        partes.append({"dim": dim, "valor": v, "comparador": comp, "minutos": minutos})
    for j, (p, f, d) in enumerate(dims):  # "vaga" sem número: ≥ 1 (uma vez); "2 vagas na garagem" só consome
        if d == "vagas" and j not in ligadas:
            if not any(x["dim"] == "vagas" for x in partes):
                partes.append({"dim": "vagas", "valor": 1.0, "comparador": ">=", "minutos": False})
            ligar(j)
    sobra = [m.group(0) for m in re.finditer(r"[a-z$]+|\d[\d.,]*", t)
             if not _dentro(m.start(), consumido) and m.group(0) not in _LIGACAO]
    return partes, sobra


def comparar(parte: dict, ficha_valor: float, ficha_minutos: bool, contagem: bool) -> str:
    """'supported' | 'contradicted' pela regra do LEIA-ME: contagem exata; medida ±5%; minutos ±50%."""
    c, v, f = parte["comparador"], parte["valor"], ficha_valor
    if c == ">":
        return "supported" if f > v else "contradicted"
    if c == "<":
        return "supported" if f < v else "contradicted"
    if c == ">=":
        return "supported" if f >= v else "contradicted"
    if c == "<=":
        return "supported" if f <= v else "contradicted"
    if contagem:
        return "supported" if f == v else "contradicted"
    tol = TOLERANCIA_MINUTOS if (parte["minutos"] or ficha_minutos) else TOLERANCIA
    return "supported" if abs(f - v) <= tol * max(f, 1e-9) else "contradicted"


def conferir_numero(texto: str, ficha: dict) -> dict | None:
    """None = sem parte numérica interpretável. Senão {relacao, partes, composta, sobra}:
    relacao None = nenhuma parte tem valor na ficha; `composta` = sobrou palavra OU parte sem valor na ficha.
    Achado 5: uma parte sem valor na ficha NÃO apaga a contradição provada em outra ("Tem 4 quartos e 1 vaga"
    com `quartos: 3` e vagas ausente → contradicted pelos quartos; só o que não se resolveu vai ao Jev)."""
    partes, sobra = interpretar(texto)
    if not partes:
        return None
    detalhes = []
    for p in partes:
        fv = valor_ficha(p["dim"], ficha)
        rel = None if fv is None else comparar(p, fv[0], fv[1], DIMENSOES[p["dim"]][2])
        detalhes.append({**p, "ficha": fv[0] if fv else None, "relacao": rel})
    resolvidas = [d["relacao"] for d in detalhes if d["relacao"]]
    if not resolvidas:
        relacao = None
    else:
        relacao = "contradicted" if "contradicted" in resolvidas else "supported"
    return {"relacao": relacao, "partes": detalhes, "sobra": sobra,
            "composta": bool(sobra) or len(resolvidas) < len(detalhes)}


# ---------------------------------------------------------------- state e perguntas
def state_ficha(ficha: dict, claims: list[str]) -> dict:
    campos = {}
    for k, v in (ficha.get("campos") or {}).items():
        if v is None:
            continue
        if k == "financiamento":
            v = P.FINANCIAMENTO_EN.get(v, v)
        elif k == "orientacao_solar":
            v = P.ORIENTACAO_EN.get(v, v)
        campos[P.CAMPO_EN.get(k, k)] = v
    return {"listing": {"title": ficha["titulo"], "description": ficha["descricao"], "fields": campos},
            "claims": claims}


def caminhos(caso: dict) -> list[dict]:
    """Por afirmação: caminho (codigo / composta / jev) e o resultado numérico, antes de qualquer chamada."""
    out = []
    for a in caso["afirmacoes"]:
        num = conferir_numero(a["texto"], caso["ficha"])
        if num is None or num["relacao"] is None:
            caminho = "jev"
        else:
            caminho = "composta" if num["composta"] else "codigo"
        out.append({"id": a["id"], "texto": a["texto"], "caminho": caminho, "numero": num})
    return out


def pedido(caso: dict, desenho: str = P.DESENHO_PADRAO) -> tuple[dict, dict, list[str]] | None:
    """(state, questions, ids na ordem de `claims`) — só as afirmações que precisam do Jev; None se nenhuma."""
    precisa = [c for c in caminhos(caso) if c["caminho"] != "codigo"]
    if not precisa:
        return None
    questions = {}
    for i, c in enumerate(precisa):
        questions[f"rel_{i}"] = P.choice(i)
        if desenho == "choice+topico":
            questions[f"top_{i}"] = P.noul_topico(i)
        elif desenho != "choice":
            raise ValueError(f"desenho desconhecido: {desenho}")
    return state_ficha(caso["ficha"], [c["texto"] for c in precisa]), questions, [c["id"] for c in precisa]


# ---------------------------------------------------------------- resposta → relação → ação
# Validação ANTES de usar (achado 6): `congelamento.choice` exige ID presente, opção da lista, probabilidades
# numéricas reais (nem bool nem string) cobrindo as 3 opções e somando ~1, confiança em [0,1]. Falha = ValueError
# da integração; nunca vira "not_stated" nem "manter".
def _choice_valida(resposta: dict, chave: str) -> dict:
    v = CG.choice(resposta, chave, set(P.RELACOES))
    return {"relacao": v["choice"], "conf": v["confidence"], "probs": v["probabilities"]}


def acao(relacao: str, conf: float | None, manter: float = None, retirar: float = None) -> str:
    """Veredito do código (conf None) age direto; o do Jev passa pelos limiares."""
    manter = P.CONF_MANTER if manter is None else manter
    retirar = P.CONF_RETIRAR if retirar is None else retirar
    if conf is None:
        return "manter" if relacao == "supported" else "retirar"
    if relacao == "supported":
        return "manter" if conf >= manter else "revisar"
    return "retirar" if conf >= retirar else "revisar"


def compor(caso: dict, resposta: dict | None, desenho: str = P.DESENHO_PADRAO) -> dict:
    """Caminhos + resposta da API (ou None quando nada foi ao Jev) → relação, confiança e ação por afirmação."""
    ped = pedido(caso, desenho)
    if ped is not None and resposta is None:
        raise RuntimeError(f"{caso['id']}: afirmações precisam do Jev e não há resposta")
    ids = ped[2] if ped else []
    saidas = []
    for c in caminhos(caso):
        jev = None
        if c["id"] in ids:
            i = ids.index(c["id"])
            jev = _choice_valida(resposta, f"rel_{i}")
            if desenho == "choice+topico":
                jev["topico"] = CG.noul(resposta, f"top_{i}")
                if jev["relacao"] == "supported" and jev["topico"] <= P.TOPICO_MAX:
                    jev["relacao"] = "not_stated"  # a ficha nem trata do assunto: não pode sustentar
        if c["caminho"] == "codigo":
            rel, conf = c["numero"]["relacao"], None
        elif c["caminho"] == "composta" and c["numero"]["relacao"] == "contradicted":
            rel, conf = "contradicted", None  # o número já derruba; o resto não importa
        else:
            rel, conf = jev["relacao"], jev["conf"]
        saidas.append({**c, "jev": jev, "relacao": rel, "conf": conf, "acao": acao(rel, conf)})
    return {"id": caso["id"], "afirmacoes": saidas, "modelo": resposta["model"] if resposta else None}


def conferir(jev, caso: dict, desenho: str = P.DESENHO_PADRAO) -> dict:
    """Uma ficha de ponta a ponta: número em código, uma requisição para o resto, ação em código."""
    ped = pedido(caso, desenho)
    return compor(caso, jev.perguntar(ped[0], ped[1]) if ped else None, desenho)


# ---------------------------------------------------------------- baseline de código
_BOOL = [("aceita_pet", re.compile(r"\b(pet|pets|animal|animais|cachorro|cao|gato)\b")),
         ("mobiliado", re.compile(r"\b(mobiliad[oa]|mobilia|moveis)\b")),
         ("financiamento", re.compile(r"\bfinanc"))]


def _tokens(texto: str) -> set[str]:
    return {w[:5] for w in re.findall(r"[a-z0-9]+", normalizar(texto)) if len(w) >= 3 and w not in P.BASELINE_STOP}


def baseline(texto: str, ficha: dict) -> str:
    """Número → mesma comparação; promessa → not_stated; booleano da ficha → igualdade; senão palavras."""
    num = conferir_numero(texto, ficha)
    if num and num["relacao"]:
        return num["relacao"]
    t = normalizar(texto)
    if any(p in t for p in P.BASELINE_PROMESSA):
        return "not_stated"
    negado = bool(re.search(r"\b(nao|sem)\b", t))
    campos = ficha.get("campos") or {}
    for campo, rx in _BOOL:
        if rx.search(t) and campos.get(campo) is not None:
            v = campos[campo]
            positivo = v is True or v == "aceita"
            if v == "proprietario_analisa":
                return "not_stated"
            return "supported" if positivo != negado else "contradicted"
    chaves = _tokens(texto)
    if not chaves:
        return "not_stated"
    presentes = _tokens(ficha["titulo"] + " " + ficha["descricao"] + " " + " ".join(map(str, campos)))
    return "supported" if len(chaves & presentes) / len(chaves) >= P.BASELINE_FRACAO else "not_stated"
