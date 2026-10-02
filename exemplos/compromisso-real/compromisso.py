"""Compromisso real: UMA requisição ao Jev por conversa (perguntas de todos os candidatos); a decisão é do código.

O Jev só julga, por candidato (trecho, responsável): quando a conversa termina, o responsável deve esta entrega
(`commitment | proposal | cancelled | old_quote | unaccepted_request`)? E, entre as expressões de tempo que o
código leu na conversa, qual dá o dia da entrega? O código: valida a entrada; localiza o trecho na mensagem e lê
os fatos que são dele (autor da mensagem, se o responsável falou, se o trecho está entre aspas); extrai e RESOLVE
as expressões de tempo contra `data_referencia` (tabela do LEIA-ME; números por `_comum/numeros_br.py`); valida a
resposta; aplica a política de `perguntas.py`; copia a data da expressão escolhida (nunca calcula a partir do
modelo); e aplica a guarda de citação (trecho entre aspas nunca vira `compromisso` sozinho).

Saída por conversa: `{"vereditos": {k: compromisso|proposta|cancelado|citacao_antiga|pedido_sem_aceite|revisar},
"prazo": {k: "AAAA-MM-DD"|None}, "origem": "jev" | "falha" | "longa", "motivo": {k: str}, "detalhe": {k: {...}}}`.
`revisar` é sinal para um humano olhar: o consumidor NÃO cria nem cancela tarefa a partir dele (lição 26: a resposta
do Jev nunca é autorização); `compromisso` é proposta de tarefa, não tarefa criada.
Ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO: `decidir`/`julgar` levantam exceção;
`julgar_seguro` (o que o consumidor chama) converte a falha em `revisar` para TODOS os candidatos daquela
conversa, `prazo` nulo e `origem: "falha"` — contada à parte, fora da métrica. Nunca `compromisso` nem `cancelado`
por falha.
"""
from __future__ import annotations

import calendar
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import numeros_br as NB  # noqa: E402
import perguntas as P  # noqa: E402

ROTULOS = ["compromisso", "proposta", "cancelado", "citacao_antiga", "pedido_sem_aceite"]
REVISAR = P.REVISAR
VIVOS = ("compromisso", "proposta", "pedido_sem_aceite")  # só estes carregam `prazo`
_ACENTOS = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüçÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇ", "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC")


def _plano(texto: str) -> str:
    """Minúsculas, sem acento, MESMO comprimento (mapa por caractere): os índices continuam valendo no texto original."""
    return texto.translate(_ACENTOS).lower()


# ---------------------------------------------------------------------------------------- entrada e state
def validar_entrada(caso: dict) -> None:
    """Conversa e candidatos têm de ter a forma do esquema; trecho que não é cópia literal de uma mensagem é erro
    ANTES da chamada (o exemplo mede o decisor, não a extração)."""
    if not isinstance(caso, dict):
        raise ValueError("caso não é objeto")
    ref = caso.get("data_referencia")
    if not isinstance(ref, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", ref):
        raise ValueError(f"data_referencia inválida: {ref!r}")
    dt.date.fromisoformat(ref)  # ValueError se não existe
    conversa, cands = caso.get("conversa"), caso.get("candidatos")
    if not isinstance(conversa, list) or not conversa or not isinstance(cands, list) or not cands:
        raise ValueError("conversa ou candidatos vazios / não são listas")
    ids = set()
    for m in conversa:
        if not isinstance(m, dict) or not isinstance(m.get("id"), str) or not isinstance(m.get("autor"), str) \
                or not isinstance(m.get("texto"), str) or not m["texto"].strip() or not m["autor"].strip():
            raise ValueError(f"mensagem inválida: {m!r}")
        if m["id"] in ids:
            raise ValueError(f"id de mensagem repetido: {m['id']}")
        ids.add(m["id"])
    kids = set()
    for c in cands:
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not isinstance(c.get("trecho"), str) \
                or not c["trecho"].strip() or not isinstance(c.get("responsavel_candidato"), str) or not c["responsavel_candidato"].strip():
            raise ValueError(f"candidato inválido: {c!r}")
        if c["id"] in kids:
            raise ValueError(f"id de candidato repetido: {c['id']}")
        kids.add(c["id"])
        if localizar(conversa, c["trecho"]) is None:
            raise ValueError(f"trecho não é cópia literal de nenhuma mensagem: {c['trecho'][:40]!r}")


def localizar(conversa: list, trecho: str) -> tuple[int, int] | None:
    """(índice da mensagem, posição) da PRIMEIRA mensagem que contém o trecho literalmente; None se nenhuma."""
    for i, m in enumerate(conversa):
        pos = m["texto"].find(trecho)
        if pos >= 0:
            return i, pos
    return None


_ABRE_FECHA = [("“", "”"), ("«", "»"), ("‘", "’")]
# Cabeçalho de citação de e-mail ("Em 29/09/2026, Fulano escreveu:", "Em 29/09 às 10:12, Fulano <…> escreveu:") ou linha
# que termina em "escreveu:" / "wrote:": tudo o que vem DEPOIS dele na mesma mensagem é citado (revisão do Codex
# 2026-10-01, item 4). Avaliado sobre o texto plano (sem acento, minúsculas).
_CABECALHO_CITACAO = re.compile(r"\bem\s+\d{1,2}/\d{1,2}(?:/\d{2,4})?[^\n]*?\b(?:escreveu|wrote)\s*:|^[^\n]*\b(?:escreveu|wrote)\s*:[ \t]*$", re.MULTILINE)


def dentro_de_aspas(texto: str, inicio: int) -> bool:
    """O trecho que começa em `inicio` está dentro de aspas (retas em número ímpar antes dele, ou tipográficas abertas
    e não fechadas — contando a aspa que ABRE o próprio trecho), numa linha encaminhada (a linha inteira começa com
    `>`, mesmo quando o marcador faz parte do trecho) ou depois de um cabeçalho de citação ("Em dd/mm/aaaa, Fulano
    escreveu:"). Fato do código: alimenta o state e a guarda."""
    antes = texto[:inicio + 1] if inicio < len(texto) and texto[inicio] in '"“«‘' else texto[:inicio]
    if antes.count('"') % 2 == 1:
        return True
    for abre, fecha in _ABRE_FECHA:
        if antes.count(abre) > antes.count(fecha):
            return True
    fim_linha = texto.find("\n", inicio)
    linha = texto[texto.rfind("\n", 0, inicio) + 1:(fim_linha if fim_linha >= 0 else len(texto))]
    if linha.lstrip().startswith(">"):
        return True
    return any(m.end() <= inicio for m in _CABECALHO_CITACAO.finditer(_plano(texto)))


def candidato_enriquecido(caso: dict, c: dict) -> dict:
    """Candidato + fatos lidos pelo código: mensagem e autor do trecho, mensagens do responsável, aspas."""
    i, pos = localizar(caso["conversa"], c["trecho"])
    msg = caso["conversa"][i]
    owner = c["responsavel_candidato"]
    return {"id": c["id"], "excerpt": c["trecho"], "owner": owner, "in_message": msg["id"], "excerpt_author": msg["autor"],
            "owner_is_author": msg["autor"].strip().lower() == owner.strip().lower(),
            "owner_messages": [m["id"] for m in caso["conversa"] if m["autor"].strip().lower() == owner.strip().lower()],
            "inside_quotes": dentro_de_aspas(msg["texto"], pos)}


def state_de(caso: dict) -> dict:
    """Conversa + candidatos enriquecidos → state enxuto com os nomes que as perguntas citam entre crases.
    @example state_de({"data_referencia": "2026-10-05", "conversa": [{"id": "m1", "autor": "Rafa", "texto": "Caio, sobe até quarta?"},
                       {"id": "m2", "autor": "Caio", "texto": "Subo."}], "candidatos": [{"id": "k1", "trecho": "Subo.", "responsavel_candidato": "Caio"}]})
             → {"reference_date": "2026-10-05", "messages": [{"id": "m1", "author": "Rafa", "text": "Caio, sobe até quarta?"}, ...],
                "candidates": [{"id": "k1", "excerpt": "Subo.", "owner": "Caio", "in_message": "m2", "excerpt_author": "Caio",
                                "owner_is_author": True, "owner_messages": ["m2"], "inside_quotes": False}]}
    """
    validar_entrada(caso)
    return {"reference_date": caso["data_referencia"],
            "messages": [{"id": m["id"], "author": m["autor"], "text": m["texto"]} for m in caso["conversa"]],
            "candidates": [candidato_enriquecido(caso, c) for c in caso["candidatos"]]}


def fora_da_faixa(caso: dict) -> str | None:
    """Motivo se a conversa passa do teto (caracteres ou candidatos); None dentro da faixa validada."""
    n = sum(len(m["texto"]) for m in caso["conversa"])
    if n > P.TETO_CARACTERES:
        return f"conversa longa ({n} caracteres; teto {P.TETO_CARACTERES})"
    if len(caso["candidatos"]) > P.TETO_CANDIDATOS:
        return f"candidatos demais ({len(caso['candidatos'])}; teto {P.TETO_CANDIDATOS})"
    return None


# ---------------------------------------------------------------------------------------- expressões de tempo (código)
DIAS = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sabado": 5, "domingo": 6}
MESES = {"janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
         "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
_WD = r"(?P<wd>segunda|terca|quarta|quinta|sexta|sabado|domingo)(?:-feira)?"
# Mês por extenso ou abreviado ("5 de nov"); o nome inteiro vem antes na alternância. Número pelo prefixo de 3 letras.
_MES = r"(?P<mes>" + "|".join([*MESES, *(m[:3] for m in MESES)]) + r")"
_MES_NUM = {m[:3]: n for m, n in MESES.items()}
# Data completa (dia + mês [+ ano]): "6/11", "6/11/27", "5 de novembro", "5 de nov de 2027". Grupos d, m, a, mes, a2.
_DATA_COMPLETA = (r"(?P<d>\d{1,2})(?:\s*/\s*(?P<m>\d{1,2})(?:\s*/\s*(?P<a>\d{4}|\d{2}))?\b(?!\s*/)"
                  rf"|\s+de\s+{_MES}(?:\s+de\s+(?P<a2>\d{{4}}))?\b)")
# Ordinal que não é dia da semana ("segunda via", "quarta versão"): não extrair.
_NAO_DIA = r"(?!\s+(?:via|vez|versao|opcao|parte|fase|etapa|rodada|coisa|metade|tentativa|chamada|leva|pagina|linha|camada|turma|sprint|semana)\b)"
_PARTE_DO_DIA = r"(?:\s+(?:cedo|cedinho|de\s+manha|a\s+tarde|a\s+noite|ate\s+(?:o\s+)?meio-dia|ate\s+as\s+\d{1,2}\s*h\d{0,2}|as\s+\d{1,2}\s*h\d{0,2}|sem\s+falta))?"

# (tipo, regex sobre o texto plano). Sobreposição: começa antes vence; mesmo início, o mais longo vence.
# Dia da semana seguido de DATA COMPLETA ("quinta, dia 5 de novembro", "sexta, 6/11", "quinta 5/11 às 18h") é UMA
# expressão com o mês (e o ano) explícitos mandando — antes, a sobreposição ficava com "quinta, dia 5" e perdia o
# mês (revisão do Codex 2026-10-01, item 2).
_PADROES = [
    ("dia_semana_prox_semana", re.compile(rf"\b{_WD}\s+da\s+(?:semana\s+que\s+vem|proxima\s+semana|semana\s+seguinte)\b")),
    ("dia_semana", re.compile(rf"\b{_WD}{_NAO_DIA}(?:\s+que\s+vem)?(?:\s*,?\s*(?:dia\s+)?{_DATA_COMPLETA}|\s*,?\s*dia\s+(?P<n>\d{{1,2}})\b)?{_PARTE_DO_DIA}\b")),
    ("dia_mes_ano", re.compile(r"\b(?:dia\s+)?(?P<d>\d{1,2})\s*/\s*(?P<m>\d{1,2})(?:\s*/\s*(?P<a>\d{4}|\d{2}))?\b(?!\s*/)")),
    ("dia_de_mes", re.compile(rf"\b(?:dia\s+)?(?P<d>\d{{1,2}})\s+de\s+{_MES}(?:\s+de\s+(?P<a>\d{{4}}))?\b")),
    ("dia_n", re.compile(r"\b(?:no\s+|ate\s+o\s+|ate\s+|pro\s+|para\s+o\s+)?dia\s+(?P<n>\d{1,2})\b(?!\s*/|\s+de\s+[a-z])")),
    ("em_n_dias", re.compile(r"\b(?:em|daqui\s+a|dentro\s+de|no\s+prazo\s+de|prazo\s+de)\s+(?:ate\s+)?(?P<n>\d{1,2}|um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez)\s+dias?(?P<uteis>\s+ut(?:eis|il))?\b")),
    ("amanha", re.compile(rf"\b(?P<q>depois\s+de\s+amanha|amanha){_PARTE_DO_DIA}\b")),
    ("hoje", re.compile(rf"\b(?:ainda\s+)?hoje(?:\s+mesmo)?{_PARTE_DO_DIA}\b")),
    ("agora", re.compile(r"\bagora(?:\s+mesmo)?\b(?!\s+(?:ha\s+pouco|nao|que|a\s+pouco|pouco))")),
    ("fim_do_dia", re.compile(r"\b(?:ate\s+)?(?:o\s+)?(?:fim|final)\s+do\s+dia\b|\bate\s+(?:as\s+)?\d{1,2}\s*h\d{0,2}\b|\bate\s+(?:o\s+)?meio-dia\b|\ba\s+tarde\b(?!\s+toda)|\ba\s+noite\b|\bdepois\s+do\s+almoco\b|\bainda\s+nesta\s+tarde\b")),
    ("fim_do_mes", re.compile(r"\b(?:ate\s+)?(?:o\s+)?(?:fim|final)\s+(?:do|de|deste|desse)\s+mes\b")),
    ("fim_da_semana", re.compile(r"\b(?:ate\s+)?(?:o\s+)?(?:fim|final)\s+(?:da|desta|dessa)\s+semana\b")),
    ("sem_dia", re.compile(r"\b(?:semana\s+que\s+vem|proxima\s+semana|semana\s+seguinte|ess[ae]\s+semana|est[ae]\s+semana|ess[ae]\s+mes|est[ae]\s+mes|mes\s+que\s+vem|proximo\s+mes|sprint\s+que\s+vem|proxima\s+sprint|nesta\s+sprint|nessa\s+sprint|em\s+breve|assim\s+que\s+\w+|um\s+dia(?:\s+desses)?|qualquer\s+(?:hora|dia)|fim\s+de\s+semana|(?:ate|em|para|durante)\s+(?:" + "|".join(MESES) + r")\b|depois\s+da\s+planning|no\s+proximo\s+ciclo|quando\s+der|mais\s+tarde|mais\s+pra\s+frente|depois)\b")),
]


@dataclass(frozen=True)
class Expressao:
    bruto: str          # trecho literal do texto original
    tipo: str
    inicio: int
    fim: int
    args: tuple         # o que o resolvedor precisa (dia da semana, número, mês, ano, úteis…)


def expressoes_de(texto: str) -> list[Expressao]:
    """Todas as expressões de tempo do texto, na ordem, sem sobreposição. Números de "em N dias" lidos por
    `numeros_br` (inclusive por extenso). O que não está na tabela do LEIA-ME não é extraído."""
    plano = _plano(texto)
    achados: list[tuple[int, int, str, tuple]] = []
    for tipo, rx in _PADROES:
        for m in rx.finditer(plano):
            g = m.groupdict()
            if tipo == "dia_semana" and g.get("d"):
                # "quinta, dia 5 de novembro" / "sexta, 6/11": a data completa manda; o dia da semana não é conferido.
                tipo = "dia_semana_data"
                mes = int(g["m"]) if g.get("m") else _MES_NUM[g["mes"][:3]]
                ano = g.get("a") or g.get("a2")
                d, ano = int(g["d"]), (int(ano) if ano else None)
                if not (1 <= d <= 31 and 1 <= mes <= 12):
                    continue
                if ano is not None and ano < 100:
                    ano += 2000
                args = (d, mes, ano)
            elif tipo in ("dia_semana_prox_semana", "dia_semana"):
                args = (DIAS[g["wd"]], int(g["n"]) if g.get("n") else None)
            elif tipo == "dia_mes_ano":
                d, mes = int(g["d"]), int(g["m"])
                if not (1 <= d <= 31 and 1 <= mes <= 12):
                    continue
                ano = int(g["a"]) if g.get("a") else None
                if ano is not None and ano < 100:
                    ano += 2000
                args = (d, mes, ano)
            elif tipo == "dia_de_mes":
                d = int(g["d"])
                if not 1 <= d <= 31:
                    continue
                args = (d, _MES_NUM[g["mes"][:3]], int(g["a"]) if g.get("a") else None)
            elif tipo == "dia_n":
                n = int(g["n"])
                if not 1 <= n <= 31:
                    continue
                args = (n,)
            elif tipo == "em_n_dias":
                nums = NB.ler_numeros(m.group(0), extenso=True)
                if not nums:
                    continue
                args = (int(nums[0].valor), bool(g.get("uteis")))
            elif tipo == "amanha":
                args = (2 if g["q"].startswith("depois") else 1,)
            else:
                args = ()
            achados.append((m.start(), m.end(), tipo, args))
    achados.sort(key=lambda a: (a[0], -(a[1] - a[0])))
    saida, ocupado = [], -1
    for ini, fim, tipo, args in achados:
        if ini < ocupado:
            continue
        # Parte do dia ("até as 10h", "à tarde", "de manhã") só significa HOJE quando está sozinha na frase: depois de
        # outra expressão na mesma frase ("amanhã de manhã, até as 10h") é só o horário, que o LEIA-ME ignora.
        if tipo == "fim_do_dia" and saida and not re.search(r"[.!?;\n]", plano[saida[-1].fim:ini]):
            continue
        saida.append(Expressao(texto[ini:fim], tipo, ini, fim, args))
        ocupado = fim
    return saida


def _dias_uteis(ref: dt.date, n: int) -> dt.date:
    d = ref
    while n > 0:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def _dia_do_mes(ref: dt.date, n: int) -> dt.date:
    """Próxima ocorrência do dia `n` do mês, a referência CONTA; dia inexistente no mês (31 em novembro) pula para o
    mês seguinte em que existe."""
    ano, mes = ref.year, ref.month
    for _ in range(14):
        ultimo = calendar.monthrange(ano, mes)[1]
        if n <= ultimo and ((ano, mes) != (ref.year, ref.month) or n >= ref.day):
            return dt.date(ano, mes, n)
        mes += 1
        if mes > 12:
            mes, ano = 1, ano + 1
    raise ValueError(f"dia {n} não existe")


def resolver(e: Expressao, ref: dt.date) -> dt.date | None:
    """Expressão → data pela tabela do LEIA-ME; None = sem dia resolvível. Só aritmética de calendário.
    @example resolver(expressoes_de("sexta da semana que vem")[0], dt.date(2026, 11, 12)) → dt.date(2026, 11, 20)
    """
    t, a = e.tipo, e.args
    if t == "dia_semana_prox_semana":
        proxima_segunda = ref + dt.timedelta(days=7 - ref.weekday())
        return proxima_segunda + dt.timedelta(days=a[0])
    if t == "dia_semana":
        if a[1] is not None:  # "segunda, dia 4": o número manda
            return _dia_do_mes(ref, a[1])
        delta = (a[0] - ref.weekday()) % 7 or 7  # estritamente depois da referência
        return ref + dt.timedelta(days=delta)
    if t in ("dia_mes_ano", "dia_de_mes", "dia_semana_data"):
        d, mes, ano = a
        if ano is None:
            ano = ref.year if (mes, d) >= (ref.month, ref.day) else ref.year + 1
        try:
            return dt.date(ano, mes, d)
        except ValueError:
            return None
    if t == "dia_n":
        return _dia_do_mes(ref, a[0])
    if t == "em_n_dias":
        n, uteis = a
        return _dias_uteis(ref, n) if uteis else ref + dt.timedelta(days=n)
    if t == "amanha":
        return ref + dt.timedelta(days=a[0])
    if t in ("hoje", "agora", "fim_do_dia"):
        return ref
    if t == "fim_do_mes":
        return dt.date(ref.year, ref.month, calendar.monthrange(ref.year, ref.month)[1])
    if t == "fim_da_semana":
        return ref - dt.timedelta(days=ref.weekday()) + dt.timedelta(days=4)
    return None  # sem_dia


def candidatos_prazo(caso: dict) -> list[dict]:
    """Expressões de tempo de TODAS as mensagens, já resolvidas: `{"chave": "m2: até sexta", "msg", "bruto", "tipo",
    "data": "AAAA-MM-DD" | None}`. A chave é a opção da Choice (volta literal); uma por (mensagem, texto)."""
    ref = dt.date.fromisoformat(caso["data_referencia"])
    saida, vistas = [], set()
    for m in caso["conversa"]:
        for e in expressoes_de(m["texto"]):
            chave = f"{m['id']}: {e.bruto}"
            if chave in vistas:
                continue
            vistas.add(chave)
            data = resolver(e, ref)
            saida.append({"chave": chave, "msg": m["id"], "bruto": e.bruto, "tipo": e.tipo, "data": data.isoformat() if data else None})
    return saida


# ---------------------------------------------------------------------------------------- perguntas e pedido
def pedido(caso: dict) -> tuple[dict, dict, dict]:
    """(state, questions, meta): TODAS as perguntas de todos os candidatos numa requisição — veredito (principal),
    quatro Nouls (informativos) e, quando o código achou expressões de tempo, a Choice do prazo."""
    state = state_de(caso)
    exprs = candidatos_prazo(caso)
    questions = {}
    for c in state["candidates"]:
        questions[f"{c['id']}_verdict"] = P.pergunta_veredito(c)
        questions.update(P.perguntas_nouls(c))
        if exprs:
            questions[f"{c['id']}_deadline"] = P.pergunta_prazo(c, exprs)
    meta = {"expressoes": {e["chave"]: e for e in exprs}, "candidatos": state["candidates"],
            "do_trecho": {c["id"]: expressoes_do_trecho(caso, c) for c in caso["candidatos"]},
            "vinculo": {c["id"]: expressoes_do_trecho(caso, c, so_da_entrega=True) for c in caso["candidatos"]}}
    return state, questions, meta


# Conectivo que abre oração condicional/temporal: a expressão depois dele na mesma oração é prazo da CONDIÇÃO, não da
# entrega ("Protocolo, desde que o cliente pague as custas até sexta" — T043). "se" só como palavra solta (não "-se").
_CONDICAO = re.compile(r"(?:(?<![-\w])se|caso|desde\s+que|contanto\s+que|quando|assim\s+que|logo\s+que|depois\s+que|so\s+depois|ate\s+que|enquanto)\b")
_ORACAO = re.compile(r"[,;.!?:\n]")
_NOME_PROPRIO = re.compile(r"\b[OoAa]\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)\b")


def na_oracao_da_entrega(caso: dict, msg: dict, e: Expressao, owner: str) -> bool:
    """A expressão está na oração da ENTREGA do responsável: não depois de conectivo condicional na mesma oração
    ("se…", "desde que…", "assim que…"), não dentro de citação, e a oração não nomeia OUTRA pessoa (autor da conversa
    ou "o/a Nome" ≠ responsável). Só isto autoriza o atalho "expressão única no trecho é o prazo" (revisão do Codex
    2026-10-01, item 3). Pronome ("ele paga até sexta") não é lido: fica com o Jev quando houver conectivo."""
    texto, plano = msg["texto"], _plano(msg["texto"])
    ini = max((m.end() for m in _ORACAO.finditer(plano, 0, e.inicio)), default=0)
    fim_m = _ORACAO.search(plano, e.fim)
    fim = fim_m.start() if fim_m else len(plano)
    if _CONDICAO.search(plano, ini, e.inicio):
        return False
    if dentro_de_aspas(texto, e.inicio):
        return False
    oracao = texto[ini:fim]
    dono = owner.strip().lower()
    outros = {m["autor"].strip().lower() for m in caso["conversa"]} - {dono}
    if any(re.search(rf"\b{re.escape(n)}\b", oracao.lower()) for n in outros):
        return False
    return all(nome.lower() == dono for nome in _NOME_PROPRIO.findall(oracao))


def expressoes_do_trecho(caso: dict, c: dict, so_da_entrega: bool = False) -> list[str]:
    """Chaves (`"m2: até terça"`) das expressões da conversa que ficam DENTRO do trecho do candidato — fato do código.
    Com `so_da_entrega`, só as que estão na oração da entrega (`na_oracao_da_entrega`)."""
    i, pos = localizar(caso["conversa"], c["trecho"])
    msg = caso["conversa"][i]
    fim = pos + len(c["trecho"])
    return [f"{msg['id']}: {e.bruto}" for e in expressoes_de(msg["texto"]) if e.inicio >= pos and e.fim <= fim
            and (not so_da_entrega or na_oracao_da_entrega(caso, msg, e, c["responsavel_candidato"]))]


def validar(resposta: dict, meta: dict) -> dict:
    """Resposta da API → números validados pela infra comum, por candidato: Choice de veredito com vencedor entre as 5
    opções e distribuição completa; quatro Nouls reais em [0,1]; Choice do prazo (se pedida) com vencedor entre as
    expressões + `none`. Qualquer falha = erro operacional (exceção), nunca `compromisso`."""
    if not isinstance(resposta, dict):
        raise ValueError("resposta não é objeto")
    opcoes_prazo = set(meta["expressoes"]) | {"none"}
    v = {}
    for c in meta["candidatos"]:
        kid = c["id"]
        v[kid] = {"verdict": CG.choice(resposta, f"{kid}_verdict", set(P.VEREDITOS)),
                  "nouls": {k: CG.noul(resposta, f"{kid}_{k}") for k in P.NOULS},
                  "deadline": CG.choice(resposta, f"{kid}_deadline", opcoes_prazo) if meta["expressoes"] else None,
                  "inside_quotes": c["inside_quotes"], "in_message": c["in_message"], "do_trecho": meta["do_trecho"][kid],
                  "vinculo": meta["vinculo"][kid]}
    return v


# ---------------------------------------------------------------------------------------- política
def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def por_choice(ch: dict) -> tuple[str, str]:
    """(rótulo, motivo) pela variante principal: vencedor da Choice; abaixo do piso → `revisar`."""
    p = ch["probabilities"][ch["choice"]]
    if p < P.P_MIN_VENCEDOR:
        return REVISAR, f"vencedor {ch['choice']} com P={p:.2f} < {P.P_MIN_VENCEDOR}"
    return P.ROTULO_DA_OPCAO[ch["choice"]], f"{ch['choice']} P={p:.2f}"


def por_nouls(n: dict) -> tuple[str, str]:
    """(rótulo, motivo) pela variante informativa, na precedência do LEIA-ME: `quoted` sim → citacao_antiga;
    `undone` sim → cancelado; `accepted` sim → compromisso; `open_request` sim → pedido_sem_aceite; os quatro não →
    proposta; qualquer dúvida no caminho → revisar."""
    s = {k: _faixa(n[k], *P.FAIXA[k]) for k in P.NOULS}
    txt = " ".join(f"{k}={n[k]:.2f}" for k in P.NOULS)
    for k, rot in (("quoted", "citacao_antiga"), ("undone", "cancelado"), ("accepted", "compromisso"), ("open_request", "pedido_sem_aceite")):
        if s[k] is True:
            return rot, txt
    # Dúvida no meio da faixa não bloqueia um sinal conclusivo que venha depois na precedência (2ª passada: o `undone`
    # fica no meio em metade dos compromissos e o `accepted` alto decide); sem sinal conclusivo, dúvida → revisar.
    if None in s.values():
        return REVISAR, txt
    return "proposta", txt


def prazo_de(dl: dict | None, expressoes: dict, do_trecho: list[str] = (), vinculo: list[str] | None = None) -> tuple[str | None, str, bool]:
    """(data, motivo, pedir revisão). Data copiada da expressão escolhida (já resolvida pelo código); `none`, expressão
    sem dia ou vencedor abaixo do piso → None. Nunca inventa data. `do_trecho` = chaves das expressões que estão DENTRO
    do próprio trecho; `vinculo` = as que estão na oração da entrega (`na_oracao_da_entrega`; None = todas). Com
    exatamente uma no trecho E vinculada, ela é o prazo (regra do LEIA-ME em código, `P.PRAZO_DO_TRECHO`) e a Choice só
    fica registrada. Uma no trecho SEM vínculo (prazo da condição, citação, data de terceiro): o Jev decide entre as
    opções; se não aponta com confiança, prazo nulo e o candidato pede revisão (3º valor)."""
    vinculo = list(do_trecho) if vinculo is None else vinculo
    if P.PRAZO_DO_TRECHO and len(do_trecho) == 1 and do_trecho[0] in vinculo:
        e = expressoes[do_trecho[0]]
        jev = "" if dl is None else f" (Jev apontou {dl['choice']!r} P={dl['probabilities'][dl['choice']]:.2f})"
        return e["data"], f"prazo do próprio trecho {do_trecho[0]!r} → {e['data'] or 'sem dia'}{jev}", False
    sem_vinculo = P.PRAZO_DO_TRECHO and len(do_trecho) == 1
    nota = f"; {do_trecho[0]!r} está no trecho mas fora da oração da entrega, o Jev decide" if sem_vinculo else ""
    if dl is None:
        return None, "sem expressão de tempo na conversa", False
    p = dl["probabilities"][dl["choice"]]
    if dl["choice"] == "none":
        return None, f"prazo `none` P={p:.2f}{nota}", False
    if p < P.P_MIN_PRAZO:
        return None, f"prazo {dl['choice']!r} com P={p:.2f} < {P.P_MIN_PRAZO}{nota}", sem_vinculo
    e = expressoes[dl["choice"]]
    return e["data"], f"prazo {dl['choice']!r} P={p:.2f} → {e['data'] or 'sem dia'}{nota}", False


def decidir(resposta: dict, meta: dict, variante: str | None = None) -> dict:
    """Resposta JSON da API → saída da conversa (guarda os números brutos para medir e re-limiar sem chamar de novo)."""
    v = validar(resposta, meta)
    return redecidir({"origem": "jev", "detalhe": v, "expressoes": meta["expressoes"]}, variante or P.VARIANTE_PRINCIPAL)


def redecidir(saida: dict, variante: str) -> dict:
    """Re-decide a MESMA resposta (números guardados em `detalhe`) com outra variante ou com as constantes atuais de
    `perguntas` — sem cache nem API. Saída sem Jev (falha/longa) volta igual."""
    if saida["origem"] != "jev":
        return saida
    vereditos, prazos, motivos = {}, {}, {}
    for kid, d in saida["detalhe"].items():
        if variante == "choice":
            rot, motivo = por_choice(d["verdict"])
        elif variante == "nouls":
            rot, motivo = por_nouls(d["nouls"])
        elif variante == "choice+nouls":
            rot, motivo = por_choice(d["verdict"])
            if rot == REVISAR:
                rot2, m2 = por_nouls(d["nouls"])
                motivo += f"; nouls → {rot2} ({m2})"
                rot = rot2
        else:
            raise ValueError(f"variante desconhecida: {variante}")
        if P.GUARDA_CITACAO and d["inside_quotes"] and rot == "compromisso":
            # Regra 8 do briefing: texto citado não cria tarefa sozinho — um humano confere.
            rot, motivo = REVISAR, motivo + "; guarda: trecho entre aspas não vira compromisso sozinho"
        prazo, mp, revisao = (prazo_de(d["deadline"], saida["expressoes"], d["do_trecho"], d.get("vinculo")) if rot in VIVOS
                              else (None, f"sem prazo em {rot}", False))
        if revisao:
            # Expressão no trecho que NÃO é da entrega e Jev sem confiança no prazo: um humano olha (item 3 do Codex).
            rot, mp = REVISAR, mp + "; revisar: prazo do trecho sem vínculo com a entrega e Jev sem confiança"
        vereditos[kid], prazos[kid], motivos[kid] = rot, prazo, motivo + "; " + mp
    return {**saida, "vereditos": vereditos, "prazo": prazos, "variante": variante, "motivo": motivos}


def saida_sem_jev(caso: dict, origem: str, motivo: str) -> dict:
    """Tudo `revisar`, `prazo` nulo: falha operacional ou conversa fora da faixa (contadas à parte). O motivo leva só a
    etapa e a classe do erro — o texto da exceção pode citar o corpo da resposta."""
    kids = [c["id"] for c in caso.get("candidatos", []) if isinstance(c, dict) and isinstance(c.get("id"), str)] \
        if isinstance(caso, dict) and isinstance(caso.get("candidatos"), list) else []
    return {"vereditos": {k: REVISAR for k in kids}, "prazo": {k: None for k in kids}, "origem": origem, "variante": None,
            "motivo": {k: motivo for k in kids}, "detalhe": {}, "expressoes": {}}


# ---------------------------------------------------------------------------------------- baseline de código
def _algum(padroes: list[str], texto: str) -> bool:
    return any(re.search(p, texto) for p in padroes)


def baseline(caso: dict) -> dict:
    """Só regex, sem Jev: aspas → citacao_antiga; cancelamento em mensagem posterior de OUTRA pessoa (ou "ops"/troca
    do próprio) → cancelado; trecho é pedido ao responsável → aceite dele depois? compromisso : pedido_sem_aceite;
    hedge → proposta; verbo de compromisso → compromisso; senão: autor = responsável → compromisso, senão
    pedido_sem_aceite. Prazo: primeira expressão do trecho; senão da mensagem do trecho; senão da mensagem anterior.
    @example baseline({"data_referencia": "2026-10-05", "conversa": [{"id": "m1", "autor": "Rafa", "texto": "Caio, sobe até quarta?"},
                       {"id": "m2", "autor": "Caio", "texto": "Subo."}], "candidatos": [{"id": "k1", "trecho": "Subo.", "responsavel_candidato": "Caio"}]})
             → {"vereditos": {"k1": "compromisso"}, "prazo": {"k1": "2026-10-07"}}
    """
    ref = dt.date.fromisoformat(caso["data_referencia"])
    conversa = caso["conversa"]
    vereditos, prazos = {}, {}
    for c in caso["candidatos"]:
        i, pos = localizar(conversa, c["trecho"])
        msg, owner = conversa[i], c["responsavel_candidato"].strip().lower()
        trecho = _plano(c["trecho"]).strip()
        depois = [m for m in conversa[i + 1:]]
        depois_outros = " ".join(_plano(m["texto"]) for m in depois if m["autor"].strip().lower() != owner)
        depois_proprio = " ".join(_plano(m["texto"]) for m in depois if m["autor"].strip().lower() == owner)
        autor_e_owner = msg["autor"].strip().lower() == owner
        # Cancelamento por outra pessoa só conta quando a mensagem fala da MESMA coisa (palavra de ≥ 5 letras em comum com
        # a mensagem do trecho) ou quando alguém assume no lugar ("eu pego", "deixa que eu"); senão todo candidato da
        # conversa cairia com um "não precisa mais" qualquer.
        palavras = {w for w in re.findall(r"[a-z]{5,}", _plano(msg["texto"]))}
        cancelou = any(_algum(P.BASELINE_CANCELAMENTO, _plano(m["texto"])) and
                       (palavras & set(re.findall(r"[a-z]{5,}", _plano(m["texto"]))) or
                        re.search(r"\beu pego\b|deixa que eu|deixa comigo|\beu assumo\b", _plano(m["texto"])))
                       for m in depois if m["autor"].strip().lower() != owner)
        if dentro_de_aspas(msg["texto"], pos):
            rot = "citacao_antiga"
        elif cancelou or re.search(r"\bops\b|no lugar|em vez", depois_proprio):
            rot = "cancelado"
        elif _algum(P.BASELINE_PEDIDO, trecho) and not autor_e_owner:
            if _algum(P.BASELINE_RECUSA, depois_proprio):
                rot = "pedido_sem_aceite"
            elif depois_proprio and _algum(P.BASELINE_ACEITE, depois_proprio):
                rot = "compromisso"
            else:
                rot = "pedido_sem_aceite"
        elif _algum(P.BASELINE_HEDGE, trecho):
            rot = "compromisso" if re.search(r"\bmanda sim\b|\bpode ser\b|\bfechado\b|\bcombinado\b", depois_outros) else "proposta"
        elif _algum(P.BASELINE_COMPROMISSO, trecho):
            rot = "compromisso"
        else:
            rot = "compromisso" if autor_e_owner else "pedido_sem_aceite"
        prazo = None
        if rot in VIVOS:
            fonte = expressoes_de(c["trecho"]) or expressoes_de(msg["texto"])
            if not fonte and i > 0:
                fonte = expressoes_de(conversa[i - 1]["texto"])  # herança burra: a mensagem anterior
            if fonte:
                d = resolver(fonte[0], ref)
                prazo = d.isoformat() if d else None
        vereditos[c["id"]], prazos[c["id"]] = rot, prazo
    return {"vereditos": vereditos, "prazo": prazos}


# ---------------------------------------------------------------------------------------- ponta a ponta
def julgar(jev, caso: dict, variante: str | None = None) -> dict:
    """Uma conversa de ponta a ponta: entrada validada, teto conferido, uma requisição, decisão em código.
    Baixo nível: entrada inválida, falha da chamada e resposta fora do contrato LEVANTAM exceção."""
    validar_entrada(caso)
    motivo = fora_da_faixa(caso)
    if motivo:
        return saida_sem_jev(caso, "longa", motivo)
    state, questions, meta = pedido(caso)
    return decidir(jev.perguntar(state, questions), meta, variante)


def julgar_seguro(jev, caso: dict, variante: str | None = None) -> dict:
    """O que o consumidor chama: os mesmos passos de `julgar`, mas NENHUMA falha sobe nem aborta o lote — entrada
    inválida, timeout, erro HTTP, cache faltando ou resposta fora do contrato viram `revisar` em TODOS os candidatos
    daquela conversa, `prazo` nulo e `origem: "falha"`. Pega `Exception` inteira de propósito: erro não previsto
    também tem de fechar em `revisar`, nunca em `compromisso` nem `cancelado`.
    @example julgar_seguro(jev_fora_do_ar, caso)
             → {"vereditos": {"k1": "revisar", …}, "prazo": {"k1": None, …}, "origem": "falha", "motivo": {"k1": "falha operacional: chamada (TimeoutError)", …}}
    """
    etapa = "entrada inválida"
    state = questions = None
    try:
        validar_entrada(caso)
        motivo = fora_da_faixa(caso)
        if motivo:
            return saida_sem_jev(caso, "longa", motivo)
        state, questions, meta = pedido(caso)
        etapa = "chamada"
        resposta = jev.perguntar(state, questions)
        etapa = "resposta inválida"
        return decidir(resposta, meta, variante)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        if etapa == "resposta inválida":
            # JSON válido que o contrato rejeitou: sai do cache para SÓ este pedido ser refeito na próxima rodada
            # (revisão do Codex 2026-10-01, item 1). Falha de chamada ou de entrada não invalida nada; e invalidar
            # não pode derrubar a falha fechada.
            try:
                jev.invalidar(state, questions)
            except Exception:  # noqa: BLE001
                pass
        return saida_sem_jev(caso, "falha", f"falha operacional: {etapa} ({type(e).__name__})")
