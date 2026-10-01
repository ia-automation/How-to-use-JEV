"""Candidatos e normalizadores — a parte EXATA da extração (código; o Jev nunca gera valor).

Regra do projeto: a regex acha DEMAIS (recall alto); o Jev só escolhe entre os achados; o código copia
o trecho escolhido e normaliza. Candidato = dict:
  texto   trecho literal da mensagem (vira o NOME da opção na Choice; é o que o Jev vê)
  valor   forma normalizada (E.164, 000.000.000-00, "1234.56", e-mail minúsculo) ou None se não fecha
  origem  "literal" | "reconstruido" (e-mail montado pelo código a partir de uma correção escrita)
  inicio, fim  posição na mensagem (para mascarar e para o teste de rastreabilidade)

Tudo aqui é determinístico e testável sem a API.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

# ------------------------------------------------------------------ e-mail
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*")
_EMAIL_OK = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,}$")
# Correção solta, NÃO colada num e-mail: "ops, é .com.br" / "na vdd é @hotmail.com".
_FRAGMENTO = re.compile(r"(?<![\w.@-])(@[A-Za-z0-9-]+(?:\.[A-Za-z]{2,})+|(?:\.[A-Za-z]{2,})+)(?![\w@])")


def normalizar_email(s: str) -> str | None:
    e = s.strip().strip(".,;:)").lower()
    return e if _EMAIL_OK.match(e) else None


def _aplicar_correcao(email: str, frag: str) -> str:
    """'@hotmail.com' troca o domínio inteiro; '.com.br' troca o que vem depois do 1º rótulo do domínio.

    @example _aplicar_correcao("joao@uol.com", ".com.br") → "joao@uol.com.br"
    """
    local, _, dominio = email.partition("@")
    if frag.startswith("@"):
        return local + frag
    return f"{local}@{dominio.split('.')[0]}{frag}"


def emails(texto: str) -> list[dict]:
    """Literais (inclusive sem TLD — viram opção, mas `valor` None) + reconstruídos por correção escrita."""
    out, vistos = [], set()
    for m in _EMAIL.finditer(texto):
        lit = m.group().rstrip(".")
        chave = lit.lower()
        if chave not in vistos:
            vistos.add(chave)
            out.append({"texto": lit, "valor": normalizar_email(lit), "origem": "literal",
                        "inicio": m.start(), "fim": m.start() + len(lit)})
    # Reconstrução é CÓDIGO juntando dois trechos que estão no texto — não é o modelo inventando.
    # Só vira candidato; quem diz se a pessoa corrigiu o endereço é o Jev, e a política manda revisar.
    literais = [c for c in out]
    for f in _FRAGMENTO.finditer(texto):
        for c in literais:
            if f.start() <= c["fim"]:
                continue  # a correção vem DEPOIS do endereço que ela corrige
            novo = _aplicar_correcao(c["texto"].lower(), f.group().lower())
            if novo not in vistos and normalizar_email(novo):
                vistos.add(novo)
                out.append({"texto": novo, "valor": novo, "origem": "reconstruido", "base": c["texto"],
                            "correcao": f.group(), "inicio": f.start(), "fim": f.end()})
    return out


# ------------------------------------------------------------------ telefone
_TEL = re.compile(r"(?<!\d)(?:\+?\s?55[\s.-]?)?(?:\(\s?\d{2}\s?\)\s?|\d{2}[\s.-]?)?9?[\s.]?\d{4}[\s.-]?\d{4}(?!\d)")
_DDD_SOLTO = re.compile(r"\bDDD\s*\(?(\d{2})\)?", re.I)


def normalizar_telefone(s: str, texto: str = "") -> str | None:
    """E.164 brasileiro. Sem DDD no trecho: só usa um 'DDD xx' ESCRITO na mensagem; senão None (não chuta).

    @example normalizar_telefone("(11) 98765-4321") → "+5511987654321"
    """
    d = re.sub(r"\D", "", s)
    if len(d) in (12, 13) and d.startswith("55"):
        d = d[2:]
    if len(d) in (8, 9):
        m = _DDD_SOLTO.search(texto)
        if not m:
            return None
        d = m.group(1) + d
    if len(d) not in (10, 11) or "0" in d[:2]:
        return None
    if len(d) == 11 and d[2] != "9":  # celular tem 9 dígitos começando por 9
        return None
    if len(d) == 10 and d[2] not in "2345":  # fixo começa por 2–5
        return None
    return "+55" + d


def telefones(texto: str) -> list[dict]:
    out, vistos = [], set()
    for m in _TEL.finditer(texto):
        lit = m.group().strip()
        ini = m.start() + (len(m.group()) - len(m.group().lstrip()))
        val = normalizar_telefone(lit, texto)
        chave = val or lit
        if chave not in vistos:  # mesmo número escrito duas vezes = uma opção (senão a probabilidade se divide)
            vistos.add(chave)
            out.append({"texto": lit, "valor": val, "origem": "literal", "inicio": ini, "fim": ini + len(lit)})
    return out


# ------------------------------------------------------------------ CPF
_CPF = re.compile(r"(?<![\d.])\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}(?!\d)")


def cpf_valido(digitos: str) -> bool:
    """Dígitos verificadores do CPF (regra da Receita) — isto é código, nunca pergunta ao Jev."""
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False
    for n in (9, 10):
        soma = sum(int(digitos[i]) * (n + 1 - i) for i in range(n))
        if (soma * 10 % 11) % 10 != int(digitos[n]):
            return False
    return True


def cpfs(texto: str) -> tuple[list[dict], list[str]]:
    """(candidatos com DV válido, trechos descartados por DV inválido).

    O DV filtra ANTES do Jev: o que a regra resolve sai do modelo. Um CPF digitado errado não vira opção.
    """
    ok, ruins, vistos = [], [], set()
    for m in _CPF.finditer(texto):
        d = re.sub(r"\D", "", m.group())
        if d in vistos:
            continue
        vistos.add(d)
        if cpf_valido(d):
            ok.append({"texto": m.group(), "valor": f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}", "origem": "literal",
                       "inicio": m.start(), "fim": m.end()})
        else:
            ruins.append(m.group())
    return ok, ruins


# ------------------------------------------------------------------ valor em R$
_PALAVRAS = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6,
    "sete": 7, "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "quatorze": 14,
    "catorze": 14, "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19,
    "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50, "sessenta": 60, "setenta": 70,
    "oitenta": 80, "noventa": 90, "cem": 100, "cento": 100, "duzentos": 200, "duzentas": 200,
    "trezentos": 300, "trezentas": 300, "quatrocentos": 400, "quatrocentas": 400, "quinhentos": 500,
    "quinhentas": 500, "seiscentos": 600, "seiscentas": 600, "setecentos": 700, "setecentas": 700,
    "oitocentos": 800, "oitocentas": 800, "novecentos": 900, "novecentas": 900,
}
_MULT = {"mil": 1000, "k": 1000, "mi": 10**6, "milhão": 10**6, "milhao": 10**6, "milhões": 10**6,
         "milhoes": 10**6, "bi": 10**9, "bilhão": 10**9, "bilhao": 10**9, "bilhões": 10**9, "bilhoes": 10**9}
_MOEDA_DEPOIS = {"reais", "real", "conto", "contos", "pila", "pilas"}
_TOKEN = re.compile(r"R\$|\d+(?:[.,]\d+)*|[A-Za-zÀ-ÿ]+|\S")
# Número colado a uma unidade que não é dinheiro sai da lista (regra de código, não julgamento).
_UNIDADE = re.compile(r"\s*(?:m²|m2\b|m\b|metros|quartos?|su[ií]tes?|vagas?|%|h\b|hs\b|horas?|x\b|vezes|parcelas?"
                      r"|anos?\b|dias?\b|meses|km\b|andar(?:es)?\b|º|°)", re.I)
# Trechos que já têm dono (data, hora, CEP) mascaram números para a lista de valor.
_MASCARA = [re.compile(p) for p in (r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", r"\b\d{1,2}(?::\d{2}|h\d{0,2})\b",
                                    r"\b\d{5}-\d{3}\b", r"(?:#|\bn[º°]\.?\s*)\d+")]


def numero_ptbr(s: str) -> Decimal:
    """'1.234,56'→1234.56 · '450.000'→450000 · '1,5'→1.5 · '1.5'→1.5 (ponto seguido de 3 dígitos = milhar)."""
    if "," in s:
        return Decimal(s.replace(".", "").replace(",", "."))
    partes = s.split(".")
    if len(partes) > 1 and all(len(p) == 3 for p in partes[1:]):
        return Decimal("".join(partes))
    return Decimal(s)


def _tipo(tok: str) -> str:
    t = tok.lower()
    if tok == "R$":
        return "rs"
    if tok[0] in "0123456789":  # não isdigit(): "²" passaria
        return "num"
    if t in _PALAVRAS:
        return "palavra"
    if t == "meio":
        return "meio"
    if t in _MULT:
        return "mult"
    if t == "e":
        return "e"
    if t in _MOEDA_DEPOIS:
        return "moeda"
    return "outro"


def _ordem(v: Decimal) -> int:
    return 100 if v >= 100 else 10 if v >= 10 else 1


def _ler_quantia(toks: list, j: int, texto: str):
    """Lê uma quantia a partir de toks[j] → (valor, índice do último token usado, tem_mult, tem_num) ou None.

    Regras (pt-BR falado): 'e' liga partes decrescentes; multiplicador igual ou maior depois de outro separa
    ("500 mil e 600 mil" = dois candidatos); grupo solto depois de multiplicador vale na escala de baixo
    ("mil e quinhentos" = 1500; "um milhão e duzentos" = 1.200.000, uso coloquial), salvo se tem unidade
    colada ("500 mil e 3 quartos").
    """
    total, grupo, ultimo_mult, ult_palavra = Decimal(0), None, None, None
    fim = fim_antes_grupo = None
    tem_mult = tem_num = False
    k = j
    while k < len(toks):
        tok, tp, ini, _ = toks[k]
        if k > j and texto[toks[k - 1][3]:ini].strip():  # só espaço entre as partes
            break
        if tp == "e":
            k += 1
            continue
        if tp in ("num", "palavra"):
            v = numero_ptbr(tok) if tp == "num" else Decimal(_PALAVRAS[tok.lower()])
            if grupo is None:
                fim_antes_grupo, grupo = fim, v
            elif tp == "palavra" and ult_palavra is not None and v < _ordem(ult_palavra):
                grupo += v  # "quinhentos e cinquenta", "vinte e cinco"
            else:
                break  # "500 e 600 mil" → dois candidatos
            ult_palavra = v if tp == "palavra" else None
            tem_num = tem_num or tp == "num"
        elif tp == "meio":
            if grupo is None and ultimo_mult is not None:
                total += Decimal(ultimo_mult) / 2  # "um milhão e meio"
            elif grupo is None:
                fim_antes_grupo, grupo = fim, Decimal("0.5")  # "meio milhão"
            else:
                break
        elif tp == "mult":
            m = _MULT[tok.lower()]
            if ultimo_mult is not None and m >= ultimo_mult:
                if grupo is not None:
                    fim, grupo = fim_antes_grupo, None
                break
            total += (grupo if grupo is not None else Decimal(1)) * m
            grupo, ultimo_mult, ult_palavra, tem_mult = None, m, None, True
        else:
            break
        fim = k
        k += 1
    if fim is None:
        return None
    if grupo is not None and ultimo_mult is not None:
        if _UNIDADE.match(texto, toks[fim][3]):
            fim = fim_antes_grupo
        else:
            total += grupo * Decimal(ultimo_mult) / 1000
    elif grupo is not None:
        total += grupo
    return total, fim, tem_mult, tem_num


def valores(texto: str, mascarados: list[tuple[int, int]] = ()) -> list[dict]:
    """Quantias escritas em algarismo, por extenso ou misturadas ('1,2 mi', '450k', 'um milhão e meio').

    `nu` = número cru sem R$, sem 'mil' e sem 'reais' (ex.: 'ofereço 600'): a ESCALA dele (600 reais ou
    600 mil?) é lida pelo Jev numa pergunta própria; o código só multiplica.
    """
    mascarados = list(mascarados) + [m.span() for p in _MASCARA for m in p.finditer(texto)]
    toks = [(m.group(), _tipo(m.group()), m.start(), m.end()) for m in _TOKEN.finditer(texto)]
    out, vistos, i = [], set(), 0
    while i < len(toks):
        if toks[i][1] not in ("rs", "num", "palavra", "meio", "mult"):
            i += 1
            continue
        tem_rs = toks[i][1] == "rs"
        lido = _ler_quantia(toks, i + 1 if tem_rs else i, texto)
        if lido is None:
            i += 1
            continue
        total, fim, tem_mult, tem_num = lido
        ini_txt, fim_txt = toks[i][2], toks[fim][3]
        seg = fim + 1
        tem_moeda = seg < len(toks) and toks[seg][1] == "moeda" and not texto[fim_txt:toks[seg][2]].strip()
        if tem_moeda:
            fim_txt = toks[seg][3]
        i = fim + 1
        lit = texto[ini_txt:fim_txt]
        nu = not (tem_rs or tem_mult or tem_moeda)
        # Filtros de código (declarados): extenso só com 'mil/milhão' ou moeda ("dois quartos" não é valor);
        # algarismo nu só com >=3 dígitos ou vírgula; ano solto (19xx/20xx) não; unidade colada não; mascarado não.
        if nu and not tem_num:
            continue
        if nu and ((len(re.sub(r"\D", "", lit)) < 3 and "," not in lit) or re.fullmatch(r"(19|20)\d{2}", lit)
                   or _UNIDADE.match(texto, fim_txt)):
            continue
        if total <= 0 or lit in vistos or any(a < fim_txt and ini_txt < b for a, b in mascarados):
            continue
        vistos.add(lit)
        out.append({"texto": lit, "valor": f"{total.quantize(Decimal('0.01'))}", "origem": "literal",
                    "nu": nu, "base": total, "inicio": ini_txt, "fim": fim_txt})
    return out


def decimal_ou_none(s) -> Decimal | None:
    try:
        return Decimal(str(s)) if s is not None else None
    except InvalidOperation:
        return None


# ------------------------------------------------------------------ data (só pistas; o calendário é do extrator)
_MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
             "outubro", "novembro", "dezembro"]
_DIAS_SEMANA_PT = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
_PISTA_DATA = re.compile(
    r"\b(hoje|amanh[ãa]|depois de amanh|segunda|ter[çc]a|quarta|quinta|sexta|s[áa]bado|domingo|semana|feriado|"
    r"dia\s+\d{1,2}|\d{1,2}\s*/\s*\d{1,2}|" + "|".join(m[:3] for m in ["jan", "fev", "mar", "abr", "mai", "jun",
                                                                        "jul", "ago", "set", "out", "nov", "dez"]) +
    r"[a-zç]*)\b", re.I)
_ANO = re.compile(r"(?<!\d)(?:(19\d{2}|20\d{2})(?!\d)|\d{1,2}/\d{1,2}/(\d{2})(?!\d))")


def pistas_de_data(texto: str) -> bool:
    """Há algo com cara de dia na mensagem? Sem pista, as perguntas de data nem são feitas (null sem custo)."""
    return bool(_PISTA_DATA.search(texto))


def anos(texto: str) -> list[str]:
    """Anos escritos na mensagem — viram as opções da pergunta de ano (em vez de 151 anos fixos)."""
    vistos = []
    for m in _ANO.finditer(texto):
        a = m.group(1) or ("20" + m.group(2))
        if a not in vistos:
            vistos.append(a)
    return vistos
