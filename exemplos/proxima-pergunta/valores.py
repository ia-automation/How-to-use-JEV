"""Normalizador de valores em dinheiro escritos pelo CLIENTE — magnitude e unidade são do código.

Por que existe (revisão do Codex, 2026-10-01, achado 1): na rodada 1 o Noul `answered.budget` julgava, dentro do
critério, se "até 6" é 6 mil e se "até 600" é 600 ou 600 mil. Deu 0,40–0,46 nos dois e o caso PP-T022 saiu com a
pergunta proibida. Distinguir 6 de 600 é comparação de magnitude: limite #2 do modelo, trabalho do código.

Duas etapas, as duas sem API:
  `mencoes(conversa)`  acha os valores nas mensagens do cliente (o agente citando preço de imóvel não entra) e
                       devolve o que NÃO depende da operação: número, escala dita (mil/milhão/reais ou nenhuma),
                       se é mensal, se é prestação. É isto que entra no state (`customer_amounts`).
  `ler(m, aluguel)`    aplica a parte numérica da regra do LEIA-ME ("Ambiguidade 'até 600'") já sabendo se é
                       aluguel: devolve `{valor, escala, tipo: preco|aluguel|prestacao}` com estado `respondida`,
                       `confirmar` (aluguel + centenas sem unidade), `prestacao` (valor total em aberto) ou
                       `ambiguo` (a regra não cobre: vai para revisão, nunca vira pergunta nem bloqueio).
Quem diz se o valor é um limite DECLARADO pelo cliente (e não o preço de um anúncio citado) é o Jev; quem diz se é
aluguel também. A combinação fica em `proxima.regra_orcamento`. Regex não sabe quem falou de quê: só lê números.

Fora da cobertura (ficam sem menção; se o Jev vir valor declarado, o item vai para revisão): numeral pequeno por
extenso sem escala ("até seis"), valor confirmado só com "isso" a uma pergunta do agente, gíria ("meio pau").
"""
from __future__ import annotations

import re

_PAL = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
        "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "quatorze": 14, "catorze": 14,
        "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19, "vinte": 20, "trinta": 30,
        "quarenta": 40, "cinquenta": 50, "sessenta": 60, "setenta": 70, "oitenta": 80, "noventa": 90, "cem": 100,
        "cento": 100, "duzentos": 200, "trezentos": 300, "quatrocentos": 400, "quinhentos": 500, "seiscentos": 600,
        "setecentos": 700, "oitocentos": 800, "novecentos": 900}
_ESCALA = {"k": 1e3, "mil": 1e3, "mi": 1e6, "milhao": 1e6, "milhão": 1e6, "milhoes": 1e6, "milhões": 1e6}

# O que vem logo depois do número e mostra que ele NÃO é dinheiro (quartos, vagas, área, idade, data, hora).
_NAO_DINHEIRO = (r"\s*(?:(?:quartos?|qts?|qtos?|dorm\w*|su[ií]tes?|vagas?|m2|metros?|anos?|vez(?:es)?|horas?|hrs?|h|dias?"
                 r"|m[eê]s|meses|semanas?|pessoas?|carros?|banheiros?|andar(?:es)?|min(?:utos?)?|km|x)\b|m²|%|[ºª°]|/\d"
                 r"|de\s+(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez))")
_DIG = r"\d{1,3}(?:\.\d{3})+|\d+(?:[.,]\d{1,2})?(?!\d)"                      # 3.800 · 450000 · 1,2 · 2500
_W = "|".join(sorted(_PAL, key=len, reverse=True))
_EXT = rf"(?:{_W})\b(?:\s+e\s+(?:{_W})\b)*"                                 # seiscentos e cinquenta
_ESC = r"(?:k|mil|mi|milh[aã]o|milh[oõ]es)\b"
_BASE = rf"(?:{_DIG}|{_EXT}|meio\b)"
# Valor = grupo com escala (+ continuação "e meio", "e quinhentos", "e 200 mil") | "mil e duzentos" | número sem
# escala. A continuação só existe depois de uma escala: "até 700 e 3 quartos" não vira 703.
_VALOR = re.compile(
    rf"(?<![\w.,/])(?:(?:{_BASE}\s?{_ESC}|mil\b)(?:\s+e\s+(?:meio\b|(?:{_DIG}|{_EXT})(?:\s?{_ESC})?)(?!{_NAO_DINHEIRO}))*"
    rf"|{_DIG}|{_EXT})", re.I)
_PECA = re.compile(rf"({_DIG})|\b({_W})\b|\b(meio)\b|({_ESC})", re.I)

# O que vem ANTES do número (colado, com palavras de enchimento no meio) e diz que ele é dinheiro.
_ENCHE_SEM_ATE = r"(?:\s*(?:uns|umas|os|as|r\$|d[eo]s?|em|a|no m[aá]ximo|mais ou menos|cerca de|s[oó])(?![\w$]))*\s*$"
_ENCHE = _ENCHE_SEM_ATE.replace("uns|", "uns|at[eé]|")
_LIMITE = re.compile(r"(?:\bat[eé]|\bno m[aá]ximo|\bm[aá]ximo|\bteto|\bor[cç]amento(?:\s+(?:[eé]|fica|seria))?|\bpagar|\bgastar"
                     r"|\binvestir|\besticar|\bem torno|\bna faixa|\bpor volta|\bna casa)" + _ENCHE, re.I)
_PREST = re.compile(r"\b(?:presta[cç][aã]o|presta[cç][oõ]es|parcelas?)(?:\s+mensa(?:l|is))?(?:\s+(?:[eé]|fica|seria))?" + _ENCHE,
                    re.I)
_NEUTRO = re.compile(r"(?:r\$|\b(?:aluguel|pre[cç]o|valor)\s+(?:t[aá]|est[aá]|[eé]|era|fica|sai|de)|\bcusta(?:ndo)?|\bsai por)"
                     + _ENCHE_SEM_ATE, re.I)
_CORRECAO = re.compile(r"\b(?:quer dizer|na verdade|na vdd|ou melhor|digo|ali[aá]s|corrigindo)[,:]?\s*$", re.I)
_OUTRA_COISA = re.compile(r"\b(?:condom[ií]nio|iptu|taxa)\b[^.;!?]{0,12}$", re.I)  # valor de condomínio não é orçamento
_ENTRADA_ANTES = re.compile(r"\bentrada\b[^.;!?]{0,12}$", re.I)
_DEPOIS_REAIS = re.compile(r"\s*(?:reais|real|contos?|pilas?)\b", re.I)
_DEPOIS_MES = re.compile(r"\s*(?:(?:por|ao|a|p/|/)\s?m[eê]s\b|mensa(?:l|is)\b|todo m[eê]s\b|de aluguel\b)", re.I)
_DEPOIS_PREST = re.compile(r"\s*(?:d[ea]|na|em)\s+(?:presta[cç][aã]o|presta[cç][oõ]es|parcelas?)\b", re.I)
_DEPOIS_ENTRADA = re.compile(r"\s*(?:d[ea]|pra|para)\s+entrada\b", re.I)


def _numero(texto: str) -> tuple[float, str | None]:
    """Trecho casado por `_VALOR` → (valor com a escala DITA aplicada, escala dita ou None).
    @example _numero("2 mil e quinhentos") → (2500.0, "mil") · _numero("1,2 mi") → (1200000.0, "milhão")
             _numero("600") → (600.0, None)
    """
    total, atual, ultima, maior = 0.0, None, None, None
    pecas = list(_PECA.finditer(texto))
    for k, p in enumerate(pecas):
        dig, pal, meio, esc = p.groups()
        if dig:
            atual = float(dig.replace(".", "")) if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", dig) else float(dig.replace(",", "."))
        elif pal:
            atual = (atual or 0.0) + _PAL[pal.lower()]
        elif meio:
            if k + 1 < len(pecas) and pecas[k + 1].group(4):  # "meio milhão"
                atual = 0.5
            elif ultima:                                       # "um milhão e meio", "2 mil e meio"
                total += ultima / 2
        else:
            ultima = _ESCALA[esc.lower()]
            maior = max(maior or 0, ultima)
            total += (1.0 if atual is None else atual) * ultima
            atual = None
    if atual is not None:  # resto sem escala: "2 mil e quinhentos" soma; "um milhão e duzentos" = +200 mil
        total += atual * (1e3 if ultima == 1e6 and atual < 1000 else 1)
    return total, {1e3: "mil", 1e6: "milhão"}.get(maior)


def mencoes(conversa: list[dict]) -> list[dict]:
    """Valores em dinheiro nas mensagens do CLIENTE, na ordem. Um número só conta se tem cara de dinheiro: marcador
    antes ("até", "prestação de", "R$", "o aluguel tá"), escala ou moeda depois ("mil", "k", "mi", "reais"), ou é
    correção de um valor anterior ("quer dizer, 1600"). Número seguido de quartos/vagas/anos/data não conta.
    @example mencoes([{"de": "cliente", "texto": "alugar, 3 quartos, até 6"}])
             → [{"msg": 0, "trecho": "até 6", "numero": 6.0, "escala": None, "mensal": False, "prestacao": False,
                 "limite": True, "entrada": False}]
    """
    achadas = []
    for k, msg in enumerate(conversa):
        if msg["de"] != "cliente":
            continue
        texto, anterior = msg["texto"], None
        for v in _VALOR.finditer(texto):
            antes, depois = texto[max(0, v.start() - 48):v.start()], texto[v.end():v.end() + 28]
            numero, escala = _numero(v.group())
            if re.match(_NAO_DINHEIRO, depois, re.I) or _OUTRA_COISA.search(antes):
                continue
            if escala is None and not re.search(r"\d", v.group()) and numero < 100:
                continue  # "um", "dois" sem escala: artigo ou contagem, não valor
            prest, limite, neutro = _PREST.search(antes), _LIMITE.search(antes), _NEUTRO.search(antes)
            reais = _DEPOIS_REAIS.match(depois)
            correcao = anterior is not None and _CORRECAO.search(antes)
            marca = prest or limite or neutro
            if not (marca or escala or reais or correcao):
                continue
            fim = v.end() + (reais.end() if reais else 0)
            resto = texto[fim:fim + 28]
            mes, prest_depois = _DEPOIS_MES.match(resto), _DEPOIS_PREST.match(resto)
            fim += (mes or prest_depois).end() if (mes or prest_depois) else 0
            inicio = v.start() - (len(antes) - marca.start()) if marca else v.start()
            m = {"msg": k, "trecho": texto[inicio:fim].strip(), "numero": numero,
                 "escala": escala or ("reais" if reais or (neutro and "$" in neutro.group()) else None),
                 "mensal": bool(mes), "prestacao": bool(prest or prest_depois), "limite": bool(prest or limite),
                 "entrada": bool(_ENTRADA_ANTES.search(antes) or _DEPOIS_ENTRADA.match(resto))}
            if correcao and not marca:  # a correção herda o que o valor corrigido era (limite, mensal, prestação)
                m.update({c: anterior[c] for c in ("mensal", "prestacao", "limite")})
            achadas.append(m)
            anterior = m
    return achadas


def principal(achadas: list[dict]) -> dict | None:
    """A menção que vale como orçamento: a ÚLTIMA dita como limite ou prestação (correção tardia: vale a última
    declaração); sem nenhuma assim, a última menção. None se o cliente não escreveu valor."""
    limites = [m for m in achadas if m["limite"]]
    return (limites or achadas or [None])[-1]


def para_state(achadas: list[dict]) -> list[dict]:
    """Fato calculado que entra no state (`customer_amounts`): só o que não depende da operação. O Jev não lê
    magnitude daqui — usa a lista para julgar se algum destes valores é o limite do próprio cliente."""
    return [{"quote": m["trecho"], "value": int(m["numero"]) if float(m["numero"]).is_integer() else m["numero"],
             "unit": "reais" if m["escala"] or m["numero"] >= 1000 else "none stated",
             **({"monthly": True} if m["mensal"] or m["prestacao"] else {})} for m in achadas]


def ler(m: dict, aluguel: bool, piso_preco: int) -> dict:
    """Parte numérica da regra do LEIA-ME, já sabendo se a operação é aluguel (`aluguel=False` = compra OU operação
    desconhecida: o LEIA-ME dá a mesma leitura às duas). `piso_preco` separa aluguel mensal de preço de compra.

    estado `respondida`  o número e a unidade estão dados → {valor em reais, escala, tipo}
           `confirmar`   aluguel + centenas sem unidade ("até 600": 600/mês ou 6 mil?) → perguntar é aceitável
           `prestacao`   valor mensal em compra → o valor total continua em aberto
           `ambiguo`     a regra não cobre esta combinação → revisão (nunca pergunta, nunca bloqueio)
    @example ler({"numero": 6.0, "escala": None, ...}, aluguel=True, piso_preco=50000)
             → {"estado": "respondida", "valor": 6000, "escala": "mil (inferida)", "tipo": "aluguel", "porque": "..."}
    """
    n, esc = m["numero"], m["escala"]
    sem_unidade = esc is None and n < 1000  # número escrito por inteiro (2500, 450000) já está em reais
    pode_ser_ano = esc is None and not m["mensal"] and float(n).is_integer() and 2020 <= n <= 2039

    def saida(estado, porque, valor=None, escala=None, tipo=None):
        return {"estado": estado, "valor": None if valor is None else int(round(valor)), "escala": escala, "tipo": tipo,
                "porque": porque}

    if m["entrada"]:
        return saida("ambiguo", "valor de entrada: o LEIA-ME não diz se responde o orçamento")
    if pode_ser_ano:
        return saida("ambiguo", "número sem unidade que pode ser um ano")
    if aluguel:
        if m["prestacao"]:
            return saida("ambiguo", "prestação com aluguel conhecido: combinação que o LEIA-ME não cobre")
        if sem_unidade and n < 100:
            return saida("respondida", "aluguel + número pequeno sem unidade = milhares (LEIA-ME: 'até 6' = R$ 6 mil)",
                         n * 1000, "mil (inferida)", "aluguel")
        if sem_unidade:
            return saida("confirmar", "aluguel + centenas sem unidade: 600 por mês ou 6 mil? (LEIA-ME: confirmar é aceitável)")
        if n < piso_preco:
            return saida("respondida", "aluguel com valor e unidade dados", n, esc or "reais", "aluguel")
        return saida("ambiguo", "valor com tamanho de preço de compra, mas a operação é aluguel")
    if m["prestacao"] or m["mensal"]:
        return saida("prestacao", "valor mensal em compra: o valor total continua em aberto (LEIA-ME: prestação)",
                     None if sem_unidade and n < 100 else n, esc or (None if sem_unidade else "reais"), "prestacao")
    if sem_unidade and n < 100:
        return saida("ambiguo", "número pequeno sem unidade fora de aluguel: o LEIA-ME não cobre")
    if sem_unidade:
        return saida("respondida", "centenas sem unidade em compra ou operação desconhecida = R$ mil (LEIA-ME: 'até 600')",
                     n * 1000, "mil (inferida)", "preco")
    if n >= piso_preco:
        return saida("respondida", "preço com valor e unidade dados", n, esc or "reais", "preco")
    return saida("ambiguo", "valor baixo demais para preço de compra e a operação não é aluguel conhecido")
