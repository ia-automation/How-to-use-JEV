"""Repetição ou revisão: o código resolve o que é exato, UMA requisição ao Jev julga a relação, o código compõe.

Sinal por grupo de mensagens do mesmo remetente — e NADA é executado nem descartado daqui (é um sinal de
reconciliação para o processo que consome a fila, com a permissão e a idempotência dele):
  colapsar    same_intent: a última é cópia, cobrança ou confirmação → executar UMA vez (vale a primeira)
  substituir  revision: a última corrige, troca ou cancela → a ação vigente é a última; o que a anterior pediu
              e a última não tocou continua de pé (revisão parcial) — por isso a saída NUNCA autoriza descarte
  somar       additional_request: pedido novo ou complemento → valem todas
  revisar     unclear, dúvida entre duas leituras, falha operacional ou grupo fora da faixa validada → humano
Divisão: idempotência por ID, validação da ordem e deduplicação EXATA (texto igual após normalização) são do
código e não gastam requisição; o Jev lê o texto das mensagens já ordenadas; `acao_vigente` é derivada da relação
em código. Política assimétrica (números em `perguntas.py`): colapsar uma revisão apaga a correção e somar uma
repetição duplica o efeito — por isso dúvida entre repetição e revisão, ou entre repetição e soma, vira `revisar`.
Ausência de resposta, ID faltando, tipo errado ou número inválido é ERRO: `decidir`/`julgar` levantam exceção;
`julgar_seguro` (o que o consumidor chama) converte a falha em `revisar` para AQUELE grupo. Nunca `colapsar`,
`substituir` nem `somar`.

Candidato à fila de mensagens da Luci (0010): roda sobre o lote de mensagens pendentes do mesmo contato antes de o
agente agir.
"""
from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

SINAIS = ["colapsar", "substituir", "somar", "revisar"]
BASELINES = ["igualdade", "jaccard", "ultima"]


# ---------------------------------------------------------------------------------------- o que é do código
def normalizar(texto: str) -> str:
    """Forma de comparação da deduplicação EXATA: NFKC, minúsculas, espaços colapsados, pontuação final fora.
    Conservadora de propósito: acento e pontuação INTERNA ficam ("10,30" ≠ "10.30"; "é" ≠ "e") — atalho de código
    só decide com prova; reenvio com erro de digitação vai ao Jev.
    @example normalizar("Vocês têm horário  pra visita no sábado??") → "vocês têm horário pra visita no sábado"
    """
    return " ".join(unicodedata.normalize("NFKC", texto).casefold().split()).rstrip(" ?!.…,;")


def palavras(texto: str) -> set[str]:
    """Conjunto de palavras para o Jaccard: sem acento, minúsculas, o que não é letra nem dígito separa.
    @example palavras("Quarta 15h, pode ser?") → {"quarta", "15h", "pode", "ser"}
    """
    sem = unicodedata.normalize("NFKD", texto.casefold()).encode("ascii", "ignore").decode()
    return set("".join(c if c.isalnum() else " " for c in sem).split())


def jaccard(a: str, b: str) -> float:
    pa, pb = palavras(a), palavras(b)
    return len(pa & pb) / len(pa | pb) if pa | pb else 1.0


def preparar(mensagens: list[dict]) -> tuple[list[dict], list[str]]:
    """Valida o grupo e tira o que é repetição EXATA: (mensagens distintas na ordem, IDs colapsados pelo código).
    - campos e tipos; mesmo remetente; minutos inteiros não decrescentes. Fora de ordem é ERRO de entrada, não
      motivo para reordenar aqui: quem ordena é a fila, dona dos carimbos — ordem trocada inverte uma revisão;
    - mesmo ID duas vezes com o mesmo texto = a mesma mensagem entregue de novo (idempotência por ID): sai;
      mesmo ID com textos diferentes = entrada inválida;
    - texto igual ao da mensagem IMEDIATAMENTE anterior (após `normalizar`) = cópia: sai. Só adjacente: repetir
      a primeira DEPOIS de uma mudança ("terça" → "melhor quarta" → "terça") desfaz a mudança, não é cópia.
    @example preparar([m1 "quero visita quarta 14h", m2 idem, m3 "na verdade quinta"]) → ([m1, m3], ["m2"])
    """
    if not isinstance(mensagens, list) or len(mensagens) < 2:
        raise ValueError("grupo precisa de pelo menos 2 mensagens")
    vistos: dict[str, str] = {}
    distintas, colapsadas, minuto = [], [], 0
    for m in mensagens:
        if not isinstance(m, dict):
            raise ValueError("mensagem não é objeto")
        for campo in ("id", "de", "texto"):
            if not isinstance(m.get(campo), str) or not m[campo].strip():
                raise ValueError(f"mensagem sem `{campo}` textual")
        t = m.get("minutos_desde_a_primeira")
        if isinstance(t, bool) or not isinstance(t, int) or t < minuto:
            raise ValueError("`minutos_desde_a_primeira` inválido ou fora de ordem")
        minuto = t
        if m["de"] not in P.REMETENTES or m["de"] != mensagens[0]["de"]:
            raise ValueError("remetente desconhecido ou diferente dentro do grupo")
        if m["id"] in vistos:
            if vistos[m["id"]] != m["texto"]:
                raise ValueError("mesmo ID com textos diferentes")
            colapsadas.append(m["id"])
            continue
        vistos[m["id"]] = m["texto"]
        if distintas and normalizar(m["texto"]) == normalizar(distintas[-1]["texto"]):
            colapsadas.append(m["id"])
            continue
        distintas.append(m)
    return distintas, colapsadas


def sem_reentregas(mensagens) -> list[dict]:
    """O grupo sem as reentregas por ID: fica a PRIMEIRA ocorrência de cada ID. A mesma mensagem entregue de novo
    não é mensagem nova — em [m1 "quinta", m2 "sexta", m1 "quinta"] a reentrega de `m1` no fim não pode
    ressuscitar o pedido que `m2` corrigiu (revisão do Codex, 2026-10-01). Tolerante a entrada inválida, porque
    serve também à saída de falha: ignora o que não é mensagem com `id` textual.
    @example sem_reentregas([m1, m2, m1]) → [m1, m2]
    """
    vistos, unicas = set(), []
    for m in mensagens if isinstance(mensagens, list) else []:
        if isinstance(m, dict) and isinstance(m.get("id"), str) and m["id"] not in vistos:
            vistos.add(m["id"])
            unicas.append(m)
    return unicas


def vigente(relacao: str, mensagens: list[dict]) -> str | None:
    """`acao_vigente` derivada da relação (regra do LEIA-ME), sobre o grupo SEM reentregas por ID: a primeira em
    `same_intent`; a ÚLTIMA em `revision`; `None` em `additional_request` (valem todas) e em `unclear`."""
    unicas = sem_reentregas(mensagens)
    if not unicas or relacao not in ("same_intent", "revision"):
        return None
    return unicas[0]["id"] if relacao == "same_intent" else unicas[-1]["id"]


def baselines(mensagens: list[dict]) -> dict[str, str]:
    """As três regras de código, sobre o grupo cru. Nenhuma diz `unclear`: regra não sabe que não sabe.
      igualdade  textos todos iguais após `normalizar` → same_intent; senão executa tudo (additional_request);
      jaccard    palavras em comum entre a última e a anterior mais parecida: ≥ MESMO → same_intent; ≥ REVISAO →
                 revision; abaixo → additional_request;
      ultima     "a última sempre vale" → revision.
    """
    textos = [m["texto"] for m in mensagens]
    j = max(jaccard(textos[-1], t) for t in textos[:-1])
    return {"igualdade": "same_intent" if len({normalizar(t) for t in textos}) == 1 else "additional_request",
            "jaccard": "same_intent" if j >= P.JACCARD_MESMO else "revision" if j >= P.JACCARD_REVISAO else "additional_request",
            "ultima": "revision"}


def baselines_seguro(mensagens) -> dict[str, str]:
    """Os baselines como o relatório os chama: grupo inválido não vira conta — sai `unclear` (revisar) nos três."""
    try:
        preparar(mensagens)
    except ValueError:
        return {b: "unclear" for b in BASELINES}
    return baselines(mensagens)


# ---------------------------------------------------------------------------------------- state e saídas
def state_de(distintas: list[dict]) -> dict:
    """State enxuto: remetente + textos, com a última mensagem apontada por nome. IDs ficam no código (a resposta
    não cita mensagem). Minutos só entram na variante medida (`P.MINUTOS_NO_STATE`)."""
    def msg(m):
        return {"text": m["texto"], "minutes_since_first": m["minutos_desde_a_primeira"]} if P.MINUTOS_NO_STATE else m["texto"]
    return {"from": P.REMETENTES[distintas[0]["de"]], "earlier_messages": [msg(m) for m in distintas[:-1]],
            "last_message": msg(distintas[-1])}


def _saida(relacao: str, motivo: str, origem: str, mensagens, colapsadas=(), v: dict | None = None, distintas=None) -> dict:
    """Decisão no formato único. `origem`: `codigo` (igualdade exata), `jev`, `longo` (fora da faixa) ou `falha`.
    Sem números do Jev (`v` None) os campos de medição ficam vazios.
    Contrato com o consumidor (revisão do Codex, 2026-10-01): `ids_de_contexto_obrigatorio` = toda mensagem cujo
    pedido ainda pode valer — as distintas (sem reentrega nem cópia exata) em QUALQUER sinal, porque o esquema tem
    uma relação por grupo e não diz O QUE foi substituído (revisão parcial: o resto da anterior continua de pé).
    `descartar_anterior` é sempre False: `substituir` diz qual ação vale, nunca autoriza apagar mensagem. Sem as
    distintas (falha antes da validação), vai o grupo inteiro sem reentregas."""
    v = v or {"choice": None, "conf": None, "probs": {}, "nouls": {q: None for q in P.NOULS}}
    contexto = distintas if distintas is not None else sem_reentregas(mensagens)
    return {"relacao": relacao, "sinal": P.SINAL[relacao], "acao_vigente": vigente(relacao, mensagens),
            "ids_de_contexto_obrigatorio": [m["id"] for m in contexto], "descartar_anterior": False,
            "motivo": motivo, "origem": origem, "colapsadas_pelo_codigo": list(colapsadas), **v}


def fora_da_faixa(distintas: list[dict]) -> str | None:
    """Motivo se o grupo passa da faixa validada (mensagens distintas ou caracteres); None dentro dela."""
    n = sum(len(m["texto"]) for m in distintas)
    if len(distintas) > P.MAX_MENSAGENS:
        return f"grupo com {len(distintas)} mensagens distintas (validado até {P.MAX_MENSAGENS})"
    return f"grupo longo ({n} caracteres; teto {P.TETO_CARACTERES})" if n > P.TETO_CARACTERES else None


def decisao_falha(tipo: str, mensagens=None) -> dict:
    """Falha operacional (entrada, chamada ou contrato da resposta): humano lê. O motivo leva só a etapa e a
    classe do erro — o texto da exceção pode citar o corpo da resposta."""
    return _saida("unclear", f"falha operacional: {tipo}", "falha", mensagens)


# ---------------------------------------------------------------------------------------- resposta → decisão
def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    """Noul em três faixas: True / False / None (= dúvida)."""
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def validar(resposta: dict) -> dict:
    """Resposta da API → números validados (infra comum): Choice entre as 4 opções com probabilidades somando ~1
    e confiança em [0,1]; cada Noul número real em [0,1]. Falha = erro operacional (exceção), nunca decisão."""
    c = CG.choice(resposta, P.CHOICE, set(P.OPCOES))
    return {"choice": c["choice"], "conf": c["confidence"], "probs": c["probabilities"],
            "nouls": {q: CG.noul(resposta, q) for q in P.NOULS}}


def politica(v: dict) -> tuple[str, str]:
    """(relação, motivo) pela política assimétrica de `perguntas.py`. A Choice propõe; os Nouls absolutos têm de
    confirmar a proposta E negar a leitura que tornaria o erro caro; senão `unclear` (→ revisar)."""
    n, op = v["nouls"], v["choice"]
    s = {q: _faixa(n[q], *P.FAIXA[q]) for q in P.NOULS}
    troca, mesma = s["replaces_previous"], s["same_request_again"]
    soma_sim = any(s[q] is True for q in P.NOULS_SOMA)
    soma_nao = all(s[q] is False for q in P.NOULS_SOMA)
    soma_txt = "/".join(f"{n[q]:.2f}" for q in P.NOULS_SOMA)
    if op == "unclear":
        return "unclear", "o texto não decide entre corrigir e somar (Choice)"
    duvida = [f"{q} {n[q]:.2f}" for q in P.NOULS_DUVIDA if s[q] is True]
    if duvida:
        return "unclear", "Noul de dúvida: " + "; ".join(duvida)
    if v["conf"] < P.CONF_MIN:
        return "unclear", f"confiança da Choice baixa ({v['conf']:.2f}, {op})"
    if op == "same_intent":
        if troca is not False:
            return "unclear", f"repetição ou revisão? ({n['replaces_previous']:.2f}) — colapsar apagaria a correção"
        if not soma_nao:
            return "unclear", f"repetição ou pedido novo/complemento? ({soma_txt})"
        if mesma is not True:
            return "unclear", f"Choice diz repetição, Noul não confirma ({n['same_request_again']:.2f})"
        return "same_intent", "mesmo pedido, nada muda nem se soma"
    if op == "revision":
        if troca is not True:
            return "unclear", f"Choice diz revisão, Noul não confirma ({n['replaces_previous']:.2f})"
        if mesma is True:
            return "unclear", "lido como repetição E revisão"
        return "revision", "a última corrige, troca ou cancela"
    if not soma_sim:
        return "unclear", f"Choice diz pedido adicional, Nouls não confirmam ({soma_txt})"
    if mesma is not False:
        return "unclear", f"pedido novo ou repetição? ({n['same_request_again']:.2f}) — somar duplicaria o efeito"
    if troca is not False:
        return "unclear", f"pedido novo ou revisão? ({n['replaces_previous']:.2f})"
    return "additional_request", "pedido novo ou complemento; o anterior continua de pé"


def compor(v: dict, mensagens: list[dict], colapsadas=(), distintas=None) -> dict:
    """Números validados → decisão da POLÍTICA (guarda os números para medir e re-limiar sem chamar de novo)."""
    relacao, motivo = politica(v)
    return _saida(relacao, motivo, "jev", mensagens, colapsadas, v, distintas)


def decidir(resposta: dict, mensagens: list[dict], colapsadas=(), distintas=None) -> dict:
    """Resposta JSON da API → decisão. Resposta fora do contrato LEVANTA exceção."""
    return compor(validar(resposta), mensagens, colapsadas, distintas)


def _em_pares(jev, mensagens, distintas, colapsadas, etapa) -> dict:
    """Variante medida para grupos de 3: duas requisições (m1→m2, m2→m3), cada uma pela mesma política, e o código
    compõe. Repetição no 1º par: vale o 2º. Revisão depois de soma (ou soma depois de revisão) não cabe em UMA
    relação por grupo — "desmarca" depois de dois pedidos não diz qual: `unclear`. Guarda os números do 2º par."""
    etapa[0] = "chamada"
    r1, r2 = (jev.perguntar(state_de(par), P.PERGUNTAS) for par in (distintas[:2], distintas[1:]))
    etapa[0] = "resposta inválida"
    v1, v2 = validar(r1), validar(r2)
    (a, _), (b, motivo) = politica(v1), politica(v2)
    if "unclear" in (a, b):
        relacao = "unclear"
    elif a == "same_intent" or a == b:
        relacao = b
    elif b == "same_intent":
        relacao = a  # m3 só repete m2: vale a relação do 1º par
    else:
        relacao = "unclear"  # revisão + soma em mensagens separadas
    return _saida(relacao, f"pares: {a} depois {b} — {motivo}", "jev", mensagens, colapsadas, v2, distintas)


def julgar(jev, mensagens: list[dict], _etapa: list | None = None) -> dict:
    """Um grupo de ponta a ponta: validação, deduplicação exata (se sobra uma mensagem só → `same_intent` sem
    chamada), faixa conferida, uma requisição, composição. Baixo nível: grupo inválido, falha da chamada e
    resposta fora do contrato LEVANTAM exceção. `_etapa` é onde `julgar_seguro` lê em que passo a falha ocorreu."""
    etapa = _etapa if _etapa is not None else [""]
    etapa[0] = "entrada inválida"
    distintas, colapsadas = preparar(mensagens)
    if len(distintas) == 1:
        return _saida("same_intent", "texto idêntico após normalização (código)", "codigo", mensagens, colapsadas, distintas=distintas)
    motivo = fora_da_faixa(distintas)
    if motivo:
        return _saida("unclear", motivo, "longo", mensagens, colapsadas, distintas=distintas)
    if len(distintas) == 3 and P.GRUPO_DE_3 == "pares":
        return _em_pares(jev, mensagens, distintas, colapsadas, etapa)
    etapa[0] = "chamada"
    resposta = jev.perguntar(state_de(distintas), P.PERGUNTAS)
    etapa[0] = "resposta inválida"
    return decidir(resposta, mensagens, colapsadas, distintas)


def julgar_seguro(jev, mensagens) -> dict:
    """O que o consumidor (fila de mensagens, lote) chama: os mesmos passos de `julgar`, mas NENHUMA falha sobe nem
    aborta o lote — timeout, erro HTTP, cache faltando, resposta fora do contrato ou grupo inválido viram
    `revisar` para AQUELE grupo, com a etapa e a classe do erro no motivo. Pega `Exception` inteira de propósito:
    numa fila, erro não previsto também tem de fechar em `revisar` (nunca colapsar, substituir nem somar).
    @example julgar_seguro(jev_fora_do_ar, grupo) → {"sinal": "revisar", "motivo": "falha operacional: chamada (TimeoutError)", "origem": "falha", …}
    """
    etapa = [""]
    try:
        return julgar(jev, mensagens, etapa)
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        return decisao_falha(f"{etapa[0]} ({type(e).__name__})", mensagens)
