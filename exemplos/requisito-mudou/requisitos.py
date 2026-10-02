"""Requisito mudou: UMA requisição ao Jev por história (todas as perguntas de todos os requisitos); a decisão é do código.

O Jev só julga, por requisito registrado: depois destes turnos o cliente continua com a mesma restrição
(`kept | replaced | denied | uncertain`)? E, entre candidatos que o código leu do texto, qual é o valor novo?
O código: monta o state a partir do CADASTRO (os requisitos) e dos turnos novos; lê candidatos de valor
(`_comum/numeros_br.py`, dicionário de bairros, meses, faixa de quartos/vagas); valida a resposta; aplica a
política de `perguntas.py`; copia o valor escolhido literalmente (nunca gera); e recalcula a shortlist —
`reavaliar` é comparação numérica/textual do CÓDIGO sobre o `resumo` canônico de cada item (regra do LEIA-ME).

Saída por história: `{"atualizacoes": {q: mantido|substituido|negado|incerto}, "novo_valor": {q: texto|None},
"reavaliar": [ids], "origem": "jev" | "falha" | "longa", "motivo", "detalhe": {...números brutos...}}`.
`reavaliar` é uma PROPOSTA ao corretor: o consumidor não descarta imóvel nem reescreve o cadastro daqui — `incerto`
é sinal para perguntar, e `substituido` pede confirmação antes de virar cadastro (lição 26: resposta do Jev nunca
é autorização).
Ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO: `decidir`/`julgar` levantam exceção;
`julgar_seguro` (o que o consumidor chama) converte a falha em `incerto` para TODOS os requisitos daquela história,
`reavaliar` vazio e `origem: "falha"` — contada à parte, fora da métrica. Nunca `mantido` por falha.
"""
from __future__ import annotations

import itertools
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import numeros_br as NB  # noqa: E402
import perguntas as P  # noqa: E402

ROTULOS = ["mantido", "substituido", "negado", "incerto"]
PAPEL = {"cliente": "client", "corretor": "broker"}
# Data de referência dos dados (LEIA-ME, 2026-10-01): mês citado sem ano vira MM/2026 se ainda não passou, senão
# MM/2027. Premissa declarada, não regra do rotulador.
ANO_REF, MES_REF = 2026, 10
MESES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
         "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12, "jan": 1, "fev": 2, "mar": 3, "abr": 4,
         "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}


def _plano(texto: str) -> str:
    """Minúsculas, sem acento — dicionário de bairros e listas do baseline são casados assim."""
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


# ---------------------------------------------------------------------------------------- entrada e state
def validar_entrada(requisitos: list, conversa: list) -> None:
    """Cadastro e turnos têm de ter a forma do esquema; atributo fora do vocabulário é erro ANTES da chamada."""
    if not isinstance(requisitos, list) or not requisitos or not isinstance(conversa, list) or not conversa:
        raise ValueError("requisitos ou conversa vazios / não são listas")
    ids = set()
    for r in requisitos:
        if not isinstance(r, dict) or not isinstance(r.get("id"), str) or not isinstance(r.get("valor"), str) \
                or r.get("atributo") not in P.ATRIBUTOS or not r["valor"].strip():
            raise ValueError(f"requisito inválido: {r!r}")
        if r["id"] in ids:
            raise ValueError(f"id de requisito repetido: {r['id']}")
        ids.add(r["id"])
    for t in conversa:
        if not isinstance(t, dict) or t.get("de") not in PAPEL or not isinstance(t.get("texto"), str) or not t["texto"].strip():
            raise ValueError(f"turno inválido: {t!r}")


def state_de(requisitos: list, conversa: list) -> dict:
    """Cadastro + turnos novos → state enxuto com os nomes que as perguntas citam entre crases.
    @example state_de([{"id": "q1", "atributo": "vagas", "valor": "1"}], [{"de": "cliente", "texto": "agora 2 vagas"}])
             → {"previous_requirements": [{"id": "q1", "attribute": "vagas", "value": "1"}],
                "new_turns": [{"from": "client", "text": "agora 2 vagas"}]}
    """
    validar_entrada(requisitos, conversa)
    return {"previous_requirements": [{"id": r["id"], "attribute": r["atributo"], "value": r["valor"]} for r in requisitos],
            "new_turns": [{"from": PAPEL[t["de"]], "text": t["texto"]} for t in conversa]}


def fora_da_faixa(requisitos: list, conversa: list) -> str | None:
    """Motivo se a história passa do teto (caracteres ou requisitos); None dentro da faixa validada."""
    n = sum(len(t["texto"]) for t in conversa)
    if n > P.TETO_CARACTERES:
        return f"conversa longa ({n} caracteres; teto {P.TETO_CARACTERES})"
    if len(requisitos) > P.TETO_REQUISITOS:
        return f"requisitos demais ({len(requisitos)}; teto {P.TETO_REQUISITOS})"
    return None


# ---------------------------------------------------------------------------------------- candidatos de valor
def _e_locacao(valor: str) -> bool:
    return "/mês" in valor or "/mes" in _plano(valor)


def formatar_dinheiro(v: float, locacao: bool) -> str:
    """Formato canônico do LEIA-ME: `até R$ 650.000` (compra) · `até R$ 3.200/mês` (locação)."""
    inteiro = f"{int(round(v)):,}".replace(",", ".")
    return f"até R$ {inteiro}" + ("/mês" if locacao else "")


_NAO_DINHEIRO = re.compile(r"^\s*(?:anos?|meses|m[eê]s|semanas?|dias?|horas?|hrs?|h\b|carros?|pessoas?|filh[oa]s?|"
                           r"vez(?:es)?|andar|[ºª°]|quartos?|vagas?|x\b)", re.I)
# Datas e horas saem ANTES da leitura de dinheiro (revisão do Codex, 2026-10-01: "3 de novembro" deixava o 3 virar
# R$ 3.000). Ordem importa: a data completa antes das partes ("15/11/2026" antes de "11/2026" e de "15/11").
_MES_RX = r"(?:" + "|".join(sorted(MESES, key=len, reverse=True)) + r"|mar[cç]o)"
_LIMPA = [re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"), re.compile(r"\b\d{1,2}/\d{4}\b"), re.compile(r"\b\d{1,2}/\d{1,2}\b"),
          re.compile(r"\b\d{1,2}\s+de\s+" + _MES_RX + r"\b", re.I), re.compile(r"\bdia\s+\d{1,2}\b", re.I),
          re.compile(r"\b\d{1,2}h\d{0,2}\b", re.I), re.compile(r"\d+[ºª°]"), re.compile(r"(?m)^\s*\d\)")]
_ESCALA = re.compile(r"\d\s*(?:mil\b|milh|bilh|mi\b|mm\b|bi\b|k\b)", re.I)


def _escala_declarada(n: NB.Numero) -> bool:
    """"R$"/"reais", "mil", "milhão", "k"… no próprio trecho: a quantia veio explícita (`numeros_br` já a multiplicou)."""
    return n.unidade == "R$" or bool(_ESCALA.search(n.bruto))


def dinheiro_na_escala(n: NB.Numero, locacao: bool) -> float | None:
    """Reais a partir de um número lido: quantia explícita vale como veio ("15 mil" = 15.000, "80 mil", "70 mil",
    "1,2 milhão"); só número SEM escala declarada é lido em milhares ("850" compra → 850.000; "3,5" locação → 3.500) e
    passa pela plausibilidade (None = absurdo). Revisão do Codex, 2026-10-01: antes "15 mil" virava 15 milhões."""
    v = n.valor
    if _escala_declarada(n):
        return v
    if locacao:
        if v < 100:
            v *= 1000
        return v if 500 <= v <= 60_000 else None
    if v < 20_000:
        v *= 1000
    return v if 100_000 <= v <= 30_000_000 else None


def candidatos_dinheiro(conversa: list, valor_atual: str) -> list[str]:
    """Números de todos os turnos (o corretor pode dizer e o cliente confirmar) na escala do atributo
    (`dinheiro_na_escala`). Datas, horas, ordinais, enumerações e números com unidade de outra coisa saem antes."""
    locacao = _e_locacao(valor_atual)
    achados: list[str] = []
    for t in conversa:
        texto = t["texto"]
        for rx in _LIMPA:
            texto = rx.sub(" ", texto)
        for n in NB.ler_numeros(texto):
            if n.unidade not in (None, "R$") or _NAO_DINHEIRO.match(texto[n.fim:]):
                continue
            v = dinheiro_na_escala(n, locacao)
            if v is None:
                continue
            c = formatar_dinheiro(v, locacao)
            if c != valor_atual and c not in achados:
                achados.append(c)
    return achados


def _bairros_do_valor(valor: str) -> list[str]:
    return [b.strip() for b in re.split(r"\s+ou\s+|,\s*", valor) if b.strip()]


def _subconjuntos_proprios(itens: list[str]) -> list[list[str]]:
    """Subconjuntos não vazios e diferentes do todo, do menor para o maior, na ordem do valor."""
    return [list(c) for r in range(1, len(itens)) for c in itertools.combinations(itens, r)]


def candidatos_bairro(conversa: list, valor_atual: str, conhecidos: list[str]) -> list[str]:
    """Bairros do dicionário (+ os já registrados e os da shortlist) citados em qualquer turno e que não estão no
    valor atual. Cada novo entra sozinho (troca) e somado ao atual (ampliação); os novos juntos quando há mais de
    um. Depois, os subconjuntos próprios dos bairros atuais — sozinhos (redução: "só Vila Mariana") e com cada novo
    ("tira um, põe outro": T035) — e o atual com todos os novos. Nome curto cadastrado ("Ahú") conta: tudo que
    entra no laço vem do dicionário ou do cadastro (revisão do Codex, 2026-10-01). O Jev escolhe a combinação; o
    código não decide se é troca, ampliação ou redução."""
    atuais = _bairros_do_valor(valor_atual)
    plano_atuais = {_plano(b) for b in atuais}
    texto = _plano(" ".join(t["texto"] for t in conversa))
    achados: dict[str, int] = {}  # bairro → posição da primeira citação (ordem do texto, não do dicionário)
    for b in list(dict.fromkeys([*P.BAIRROS, *conhecidos])):
        pb = _plano(b)
        if pb in plano_atuais or b in achados:
            continue
        m = re.search(rf"(?<![a-z]){re.escape(pb)}(?![a-z])", texto)
        if m:
            achados[b] = m.start()
    novos = sorted(achados, key=achados.get)
    cands: list[str] = []
    for b in novos:
        cands += [b, " ou ".join([*atuais, b])]
    if len(novos) > 1:
        cands.append(" ou ".join(novos))
    for sub in _subconjuntos_proprios(atuais):
        cands.append(" ou ".join(sub))
        cands += [" ou ".join([*sub, b]) for b in novos]
        if len(novos) > 1:
            cands.append(" ou ".join([*sub, *novos]))
    if len(novos) > 1:
        cands.append(" ou ".join([*atuais, *novos]))
    return [c for c in dict.fromkeys(cands) if c != valor_atual]


def candidatos_prazo(conversa: list, valor_atual: str) -> list[str]:
    """`MM/AAAA` explícito ou nome de mês → `mudança até MM/AAAA`. O ano declarado prevalece, com ou sem separador
    ("novembro de 2027", "novembro 2027", "nov/2027"); sem ano, a data de referência (revisão do Codex, 2026-10-01:
    "novembro 2027" virava 11/2026)."""
    cands: list[str] = []
    for t in conversa:
        texto = t["texto"]
        for m in re.finditer(r"\b(\d{1,2})/(\d{4})\b", texto):
            mes, ano = int(m.group(1)), int(m.group(2))
            if 1 <= mes <= 12:
                cands.append(f"mudança até {mes:02d}/{ano}")
        for m in re.finditer(r"\b(" + "|".join(MESES) + r")\b(?:\s*(?:/|de\s+)?\s*(20\d{2})\b)?", _plano(texto)):
            mes = MESES[m.group(1)]
            ano = int(m.group(2)) if m.group(2) else (ANO_REF if mes >= MES_REF else ANO_REF + 1)
            cands.append(f"mudança até {mes:02d}/{ano}")
    return [c for c in dict.fromkeys(cands) if c != valor_atual]


def candidatos(req: dict, conversa: list, conhecidos: list[str] = ()) -> list[str]:
    """Candidatos de valor novo para um requisito, por tipo do atributo. Lista vazia = sem pergunta de valor."""
    tipo, atual = P.ATRIBUTOS[req["atributo"]]["tipo"], req["valor"]
    if tipo == "dinheiro":
        return candidatos_dinheiro(conversa, atual)
    if tipo == "contagem":
        a, b = P.ATRIBUTOS[req["atributo"]]["faixa"]
        return [str(n) for n in range(a, b + 1) if str(n) != atual]
    if tipo == "bairro":
        return candidatos_bairro(conversa, atual, list(conhecidos))
    if tipo == "mobilia":
        return [v for v in ("mobiliado", "sem mobília") if v != atual]
    if tipo == "prazo":
        return candidatos_prazo(conversa, atual)
    return []  # sim_ou_nada: o único valor novo possível é "sim" (regra de código em `decidir`)


# ---------------------------------------------------------------------------------------- perguntas e pedido
def pedido(requisitos: list, conversa: list, conhecidos: list[str] = ()) -> tuple[dict, dict, dict]:
    """(state, questions, candidatos por requisito): TODAS as perguntas de todos os requisitos numa requisição —
    status (principal), valor (quando há candidatos) e os três Nouls informativos."""
    state = state_de(requisitos, conversa)
    questions, cands = {}, {}
    for r in requisitos:
        questions[f"{r['id']}_status"] = P.pergunta_status(r)
        cands[r["id"]] = candidatos(r, conversa, conhecidos)
        if cands[r["id"]]:
            questions[f"{r['id']}_new_value"] = P.pergunta_valor(r, cands[r["id"]])
        questions.update(P.perguntas_nouls(r))
    return state, questions, cands


def validar(resposta: dict, requisitos: list, cands: dict) -> dict:
    """Resposta da API → números validados pela infra comum, por requisito: Choice de status com vencedor entre as
    4 opções e distribuição completa; Choice de valor (se pedida) com vencedor entre candidatos + `none`; três
    Nouls reais em [0,1]. Qualquer falha = erro operacional (exceção), nunca `mantido`."""
    if not isinstance(resposta, dict):
        raise ValueError("resposta não é objeto")
    v = {}
    for r in requisitos:
        rid = r["id"]
        st = CG.choice(resposta, f"{rid}_status", set(P.STATUS))
        valor = CG.choice(resposta, f"{rid}_new_value", set(cands[rid]) | {"none"}) if cands[rid] else None
        v[rid] = {"status": st, "valor": valor,
                  "nouls": {k: CG.noul(resposta, f"{rid}_{k}") for k in ("changed", "dropped", "open")}}
    return v


# ---------------------------------------------------------------------------------------- política
def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def status_por_choice(st: dict) -> tuple[str, str]:
    """(rótulo, motivo) pela variante principal: vencedor da Choice; abaixo do piso → `incerto`."""
    p = st["probabilities"][st["choice"]]
    if p < P.P_MIN_VENCEDOR:
        return "incerto", f"vencedor {st['choice']} com P={p:.2f} < {P.P_MIN_VENCEDOR}"
    return P.ROTULO_DA_OPCAO[st["choice"]], f"{st['choice']} P={p:.2f}"


def status_por_nouls(n: dict) -> tuple[str, str]:
    """(rótulo, motivo) pela variante informativa: `dropped` sim → negado; `changed` sim → substituido; `open` sim
    ou qualquer dúvida → incerto; senão mantido."""
    s = {k: _faixa(n[k], *P.FAIXA[k]) for k in P.FAIXA}
    txt = " ".join(f"{k}={n[k]:.2f}" for k in P.FAIXA)
    if s["changed"] is True and s["dropped"] is True:
        return "negado", txt
    if s["changed"] is True:
        return "substituido", txt
    if s["open"] is True or None in s.values():
        return "incerto", txt
    return "mantido", txt


def valor_novo(req: dict, val: dict | None) -> tuple[str | None, str]:
    """Valor copiado literalmente da opção escolhida (ou `sim` para sim/indiferente quando o atual não é `sim`).
    None = `replaced` sem valor utilizável → o chamador rebaixa para `incerto`."""
    tipo = P.ATRIBUTOS[req["atributo"]]["tipo"]
    if tipo == "sim_ou_nada":
        return ("sim", "regra: único valor novo possível") if req["valor"] != "sim" else (None, "já era `sim`: não há valor novo")
    if val is None:
        return None, "sem candidato no texto"
    p = val["probabilities"][val["choice"]]
    if val["choice"] == "none":
        return None, f"valor `none` P={p:.2f}"
    if p < P.P_MIN_VALOR:
        return None, f"valor {val['choice']!r} com P={p:.2f} < {P.P_MIN_VALOR}"
    return val["choice"], f"valor {val['choice']!r} P={p:.2f}"


def decidir(resposta: dict, requisitos: list, shortlist: list, cands: dict, variante: str | None = None) -> dict:
    """Resposta JSON da API → saída da história (guarda os números brutos para medir e re-limiar sem chamar de novo)."""
    v = validar(resposta, requisitos, cands)
    detalhe = {r["id"]: {**v[r["id"]], "candidatos": cands[r["id"]]} for r in requisitos}
    return redecidir({"origem": "jev", "detalhe": detalhe}, requisitos, shortlist, variante or P.VARIANTE_PRINCIPAL)


def redecidir(saida: dict, requisitos: list, shortlist: list, variante: str) -> dict:
    """Re-decide a MESMA resposta (números guardados em `detalhe`) com outra variante ou com as constantes atuais de
    `perguntas` — sem cache nem API. Saída sem Jev (falha/longa) volta igual."""
    if saida["origem"] != "jev":
        return saida
    atualizacoes, novo, motivos = {}, {}, {}
    for r in requisitos:
        d = saida["detalhe"][r["id"]]
        rot, motivo = (status_por_choice(d["status"]) if variante == "choice" else status_por_nouls(d["nouls"]))
        nv = None
        if rot == "substituido":
            nv, m2 = valor_novo(r, d["valor"])
            motivo += "; " + m2
            if nv is None:
                rot = "incerto"  # LEIA-ME: sem valor não há substituição
        atualizacoes[r["id"]], novo[r["id"]], motivos[r["id"]] = rot, nv, motivo
    return {**saida, "atualizacoes": atualizacoes, "novo_valor": novo, "variante": variante, "motivo": motivos,
            "reavaliar": reavaliar(requisitos, atualizacoes, novo, shortlist)}


def saida_sem_jev(requisitos: list, origem: str, motivo: str) -> dict:
    """Tudo `incerto`, `reavaliar` vazio: falha operacional ou história fora da faixa (contadas à parte). O motivo
    leva só a etapa e a classe do erro — o texto da exceção pode citar o corpo da resposta."""
    return {"atualizacoes": {r["id"]: "incerto" for r in requisitos}, "novo_valor": {r["id"]: None for r in requisitos},
            "reavaliar": [], "origem": origem, "variante": None, "motivo": {r["id"]: motivo for r in requisitos}, "detalhe": {}}


# ---------------------------------------------------------------------------------------- shortlist (código)
_RESUMO = re.compile(
    r"^(?P<tipo>Apartamento|Casa térrea) em (?P<bairro>[^,]+), (?P<quartos>\d+) quartos?, (?:(?P<vagas>\d+) vagas?|sem vaga), "
    r"R\$ (?P<preco>[\d.]+)(?P<mes>/mês)?\.\s*(?:(?P<andar>térreo|\d+º andar), (?P<elev>com|sem) elevador;\s*)?"
    r"(?P<pet>aceita pet|não aceita pet);\s*(?P<mob>mobiliado|sem mobília);\s*(?:(?P<fin>aceita financiamento|não aceita financiamento);\s*)?"
    r"(?P<disp>pronto para morar|disponível imediato|entrega em (?P<m1>\d{2})/(?P<a1>\d{4})|disponível a partir de (?P<m2>\d{2})/(?P<a2>\d{4}))\.?$",
    re.I)


def ler_resumo(resumo: str) -> dict:
    """`resumo` canônico do LEIA-ME → atributos do item. Fora do molde = erro (o item não é comparável)."""
    m = _RESUMO.match(resumo.strip())
    if not m:
        raise ValueError(f"resumo fora do molde: {resumo[:60]!r}")
    g = m.groupdict()
    casa = g["tipo"].lower().startswith("casa")
    andar = 0 if casa or (g["andar"] or "").lower() == "térreo" else (int(g["andar"].split("º")[0]) if g["andar"] else None)
    entrega = None
    if g["m1"]:
        entrega = (int(g["a1"]), int(g["m1"]))
    elif g["m2"]:
        entrega = (int(g["a2"]), int(g["m2"]))
    return {"casa": casa, "bairro": g["bairro"].strip(), "quartos": int(g["quartos"]), "vagas": int(g["vagas"] or 0),
            "preco": float(g["preco"].replace(".", "")), "locacao": bool(g["mes"]), "andar": andar,
            "elevador": (g["elev"] or "").lower() == "com", "pet": g["pet"].lower() == "aceita pet",
            "mobiliado": g["mob"].lower() == "mobiliado",
            "financiamento": None if g["fin"] is None else g["fin"].lower() == "aceita financiamento", "entrega": entrega}


def atende(atributo: str, valor: str, item: dict) -> bool:
    """Tabela "o item atende quando" do LEIA-ME. Valor que não restringe (`indiferente`, `não`, `0`) atende sempre."""
    v = valor.strip()
    if atributo == "orcamento":
        nums = NB.ler_numeros(v)
        if not nums:
            raise ValueError(f"orçamento sem número: {valor!r}")
        return item["preco"] <= nums[0].valor
    if atributo in ("quartos", "vagas"):
        return item[atributo] >= int(v)
    if atributo == "bairro":
        return _plano(item["bairro"]) in {_plano(b) for b in _bairros_do_valor(v)}
    if atributo == "elevador":
        return v != "sim" or item["elevador"] or item["andar"] == 0
    if atributo == "pet":
        return v != "sim" or item["pet"]
    if atributo == "mobilia":
        return v == "indiferente" or (item["mobiliado"] if v == "mobiliado" else not item["mobiliado"])
    if atributo == "andar_baixo":
        return v != "sim" or (item["andar"] is not None and item["andar"] <= 3)
    if atributo == "financiamento":
        return v != "sim" or bool(item["financiamento"])
    if atributo == "prazo":
        m = re.search(r"(\d{2})/(\d{4})", v)
        if not m:
            raise ValueError(f"prazo sem MM/AAAA: {valor!r}")
        return item["entrega"] is None or item["entrega"] <= (int(m.group(2)), int(m.group(1)))
    raise ValueError(f"atributo desconhecido: {atributo}")


def reavaliar(requisitos: list, atualizacoes: dict, novo_valor: dict, shortlist: list) -> list[str]:
    """Regra do LEIA-ME: vigentes = mantido/incerto com o valor antigo, substituido com o novo, negado fora; devolve
    os IDs (na ordem da shortlist) que falham em pelo menos um vigente. Item fora do molde conta como a reavaliar
    (não dá para provar que atende) — e fica no motivo do chamador."""
    vigentes = []
    for r in requisitos:
        rot = atualizacoes[r["id"]]
        if rot == "negado":
            continue
        vigentes.append((r["atributo"], novo_valor[r["id"]] if rot == "substituido" else r["valor"]))
    fora = []
    for item in shortlist:
        try:
            lido = ler_resumo(item["resumo"])
            ok = all(atende(a, v, lido) for a, v in vigentes)
        except ValueError:
            ok = False
        if not ok:
            fora.append(item["id"])
    return fora


# ---------------------------------------------------------------------------------------- baseline de código
# Frase do baseline: pontuação, mas NÃO o ponto de milhar ("2.800 é o teto" virava "800": revisão do Codex, 2026-10-01).
_FRASE = re.compile(r"[!?;\n]|(?<!\d)\.|\.(?!\d)")


def _numero_perto(texto: str, rx_atributo: str) -> NB.Numero | None:
    """Último número da frase (separada por pontuação) que cita o atributo — regex "sabe" tanto quanto isso."""
    achado = None
    for frase in re.split(_FRASE.pattern + r"|\s-\s", texto):
        if re.search(rx_atributo, _plano(frase)):
            for n in NB.ler_numeros(frase, extenso=True):
                if not n.ambiguo or n.unidade:
                    achado = n
    return achado


def baseline(requisitos: list, conversa: list, shortlist: list) -> dict:
    """Só palavras-chave, sem Jev: por requisito, negação → negado; número novo → substituido; "agora/preciso" →
    substituido; hipótese → incerto; senão mantido. Olha só os turnos do cliente. `reavaliar` pela mesma regra de código.
    @example baseline([{"id": "q1", "atributo": "vagas", "valor": "1"}], [{"de": "cliente", "texto": "agora preciso de 2 vagas"}], [])
             → {"atualizacoes": {"q1": "substituido"}, "novo_valor": {"q1": "2"}, "reavaliar": []}
    """
    texto = "\n".join(t["texto"] for t in conversa if t["de"] == "cliente")
    plano = _plano(texto)
    atual, novo = {}, {}
    for r in requisitos:
        atr, rx = r["atributo"], P.BASELINE_ATRIBUTO[r["atributo"]]
        tipo = P.ATRIBUTOS[atr]["tipo"]
        frases = [f for f in _FRASE.split(plano) if re.search(rx, f)]
        rot, nv = "mantido", None
        if frases:
            junto = " ".join(frases)
            if any(re.search(p, junto) for p in [*P.BASELINE_NEGACAO, *P.BASELINE_NEGACAO_POR_ATRIBUTO.get(atr, [])]):
                rot = "negado"
            else:
                n = _numero_perto(texto, rx)
                num = n.valor if n else None
                if tipo == "dinheiro" and n is not None:
                    loc = _e_locacao(r["valor"])
                    v = dinheiro_na_escala(n, loc)
                    nv = formatar_dinheiro(v, loc) if v is not None else None
                elif tipo == "contagem" and num is not None and 0 <= num <= 6:
                    nv = str(int(num))
                elif tipo == "mobilia" and re.search(r"mobili", junto):
                    nv = "sem mobília" if re.search(r"sem mobili", junto) else "mobiliado"
                elif tipo == "sim_ou_nada":
                    nv = "sim"
                elif tipo == "bairro":
                    cand = candidatos_bairro(conversa, r["valor"], [i["bairro"] for i in map(_bairro_do_item, shortlist) if i])
                    nv = cand[1] if len(cand) > 1 else (cand[0] if cand else None)
                elif tipo == "prazo":
                    cand = candidatos_prazo(conversa, r["valor"])
                    nv = cand[-1] if cand else None
                if nv is not None and nv != r["valor"] and any(re.search(p, junto) for p in P.BASELINE_MUDANCA):
                    rot = "substituido"
                elif any(re.search(p, junto) for p in P.BASELINE_HIPOTESE):
                    rot, nv = "incerto", None
                elif nv is not None and nv != r["valor"] and tipo in ("dinheiro", "contagem"):
                    rot = "substituido"
                else:
                    nv = None
        atual[r["id"]], novo[r["id"]] = rot, nv
    return {"atualizacoes": atual, "novo_valor": novo, "reavaliar": reavaliar(requisitos, atual, novo, shortlist)}


def _bairro_do_item(item: dict) -> dict | None:
    try:
        return ler_resumo(item["resumo"])
    except ValueError:
        return None


def bairros_da_shortlist(shortlist: list) -> list[str]:
    return list(dict.fromkeys(i["bairro"] for i in map(_bairro_do_item, shortlist) if i))


# ---------------------------------------------------------------------------------------- ponta a ponta
def julgar(jev, requisitos: list, conversa: list, shortlist: list, variante: str | None = None) -> dict:
    """Uma história de ponta a ponta: entrada validada, teto conferido, uma requisição, decisão em código.
    Baixo nível: entrada inválida, falha da chamada e resposta fora do contrato LEVANTAM exceção."""
    validar_entrada(requisitos, conversa)
    motivo = fora_da_faixa(requisitos, conversa)
    if motivo:
        return saida_sem_jev(requisitos, "longa", motivo)
    state, questions, cands = pedido(requisitos, conversa, bairros_da_shortlist(shortlist))
    return decidir(jev.perguntar(state, questions), requisitos, shortlist, cands, variante)


def julgar_seguro(jev, requisitos: list, conversa: list, shortlist: list, variante: str | None = None) -> dict:
    """O que o consumidor chama: os mesmos passos de `julgar`, mas NENHUMA falha sobe nem aborta o lote — entrada
    inválida, timeout, erro HTTP, cache faltando ou resposta fora do contrato viram `incerto` em TODOS os
    requisitos daquela história, `reavaliar` vazio e `origem: "falha"`. Pega `Exception` inteira de propósito:
    erro não previsto também tem de fechar em `incerto`, nunca em `mantido`.
    @example julgar_seguro(jev_fora_do_ar, reqs, conversa, shortlist)
             → {"atualizacoes": {"q1": "incerto", …}, "reavaliar": [], "origem": "falha", "motivo": {"q1": "falha operacional: chamada (TimeoutError)", …}}
    """
    etapa = "entrada inválida"
    reqs = requisitos if isinstance(requisitos, list) else []
    state = questions = None
    try:
        validar_entrada(requisitos, conversa)
        motivo = fora_da_faixa(requisitos, conversa)
        if motivo:
            return saida_sem_jev(requisitos, "longa", motivo)
        state, questions, cands = pedido(requisitos, conversa, bairros_da_shortlist(shortlist))
        etapa = "chamada"
        resposta = jev.perguntar(state, questions)
        etapa = "resposta inválida"
        return decidir(resposta, requisitos, shortlist, cands, variante)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        if etapa == "resposta inválida":
            # JSON válido que o contrato rejeitou: sai do cache para SÓ este pedido ser refeito na próxima rodada
            # (família do achado do Codex em motivo-de-perda, 2026-10-01). Falha de chamada ou de entrada não
            # invalida nada; e invalidar não pode derrubar a falha fechada.
            try:
                jev.invalidar(state, questions)
            except Exception:  # noqa: BLE001
                pass
        reqs = [r for r in reqs if isinstance(r, dict) and isinstance(r.get("id"), str)]
        return saida_sem_jev(reqs, "falha", f"falha operacional: {etapa} ({type(e).__name__})")
