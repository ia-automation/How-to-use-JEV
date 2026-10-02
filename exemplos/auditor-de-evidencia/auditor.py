"""Auditor de evidência: UMA requisição ao Jev por afirmação (2 Nouls por registro + 1 global); o veredito é do código.

O Jev só julga a relação afirmação × registro (sustenta parte / contradiz) e se o conjunto prova a afirmação
inteira. O código faz o que é exato: ordem temporal e "mais recente prevalece" (só entre registros do mesmo
assunto: objeto, ambiente, componente), comparações numéricas (cobertura, latência, réplicas, versão),
casamento de revisão e de migration, QUEM entra no state (registro de outra revisão/migration e registro com
número refeito por outro mais recente saem ANTES da chamada) e a composição final pela precedência do LEIA-ME
(contradicted > insufficient_evidence > supported; dúvida → `revisa`). Nada é aprovado daqui: `supported` é "o relatório prova o que afirma"; `revisa` e `insufficient_evidence` vão para
humano/pedir prova. Ausência de resposta, ID faltando ou número inválido é ERRO, nunca `supported`.

Candidato a portão do rito /fechar-fatia do parque: "o relatório do coder prova o que afirma?".
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402

# ---------------------------------------------------------------------------------------- state
# Carimbo de hora reconhecido só como campo delimitado por "·" (início ou fim de campo): "10:02 · …",
# "… · 2026-09-30 14:40". Uma data dentro de um corpo JSON ("2026-10-03T10:00:00-03:00") NÃO é carimbo.
_RE_CARIMBO = re.compile(r"(?:^|· )(\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2})?|\d{2}:\d{2})(?= ·|$)", re.M)


def carimbo(texto: str) -> tuple[str, str] | None:
    """(data, hora) do primeiro carimbo delimitado; data vazia quando só há hora; None sem carimbo.
    @example carimbo("10:02 · revisão 5a5a5a5 · vitest run — 61 passed") → ("", "10:02")
    @example carimbo("b7e2f90 feat(x) · 2026-09-30 14:40") → ("2026-09-30", "14:40")
    @example carimbo("POST http://localhost:3000/visitas → 201 · {\\"quando\\":\\"2026-10-03T10:00:00-03:00\\"}") → None
    """
    m = _RE_CARIMBO.search(texto)
    if not m:
        return None
    partes = m.group(1).split(" ")
    return (partes[0], partes[1]) if len(partes) == 2 else (("", partes[0]) if ":" in partes[0] else (partes[0], ""))


def ordenar(registros: list[dict]) -> list[dict]:
    """Ordem cronológica quando TODOS os registros têm carimbo do mesmo formato (todos com data, ou todos só
    hora); senão a ordem da lista (LEIA-ME §5: o código usa carimbo se houver; se não, a ordem dada).
    Ordenação estável: empate mantém a ordem original."""
    cs = [carimbo(r["texto"]) for r in registros]
    if any(c is None for c in cs) or len({bool(c[0]) for c in cs}) != 1:
        return list(registros)
    return [r for _, r in sorted(zip(cs, registros), key=lambda par: par[0])]


# ---------------------------------------------------------------------------------------- assunto (código)
# Revisão do Codex 2026-10-01, achado 1: "o mais recente prevalece" vale entre registros do MESMO ASSUNTO — objeto,
# ambiente e componente —, não do mesmo tipo. Agrupando por tipo, "prod: nada a aplicar" apagava a prova válida de
# dev (AE-T014) e um sucesso posterior em dev apagaria uma falha vigente em prod. O assunto é derivado por código e
# SÓ quando o registro o traz de forma reconhecível; sem isso não há recência: os dois registros ficam.
_AMBIENTES = {"prod": "prod", "producao": "prod", "dev": "dev", "homolog": "homolog", "homologacao": "homolog", "local": "local"}
_RE_URL = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+https?://([^/\s]+)(/[^\s?]*)?", re.I)
_RE_IMAGEM = re.compile(r"\b([a-z][a-z0-9]*(?:-[a-z0-9]+)+):\d")
_RE_CAMPO_SERVICO = re.compile(r"(?:ci )?([a-z][a-z0-9]*(?:-[a-z0-9]+)+)")
# Comando de teste/build como o registro o escreve; o que vem depois de "—" ou "→" é resultado, não objeto.
_RE_COMANDO = re.compile(r"(?:ci )?(?:vitest|jest|eslint|tsc|next build|docker build|npm test|coverage|varredura)\b[^—→]*")
_RE_MIGRATION_ASSUNTO = re.compile(r"\b(\d{4})(?:_[a-z]\w*)? (?:nao )?aplicada|\b(\d{4})_[a-z]")
_RE_GIT_ASSUNTO = re.compile(r"git push \S+ (\S+)|gh pr view (\d+)")
# Tipos em que o ambiente FAZ parte do assunto: sem ambiente reconhecível não há assunto (nem recência).
_TIPOS_COM_AMBIENTE = {"deploy_event", "http_response"}


def _sem_acento(texto: str) -> str:
    """Minúsculas sem acento, preservando "·", "—" e "→" (que `_ascii` apagaria)."""
    return "".join(c for c in unicodedata.normalize("NFKD", texto.lower()) if not unicodedata.combining(c))


def _campos(texto: str) -> list[str]:
    """Campos do registro: separados por "·" ou quebra de linha, já sem acento."""
    return [c.strip() for c in re.split(r"·|\n", _sem_acento(texto))]


def ambiente(texto: str) -> str | None:
    """Ambiente que o registro traz de forma reconhecível: um campo `prod` / `dev` / `homolog` / `local` (ou
    `ambiente: X`), ou o host da URL — `localhost` → local, host com `homolog` → homolog; outro host fica LITERAL
    (o código não sabe qual host é produção: isso é do Jev). None quando o registro não diz.
    @example ambiente("drizzle migrate · ambiente: dev · 0011_score_lead aplicada") → "dev"
    @example ambiente("POST http://localhost:3000/visitas → 201 Created") → "local"
    @example ambiente("GET https://api.exemplo.com.br/saude → 200 OK") → "api.exemplo.com.br"
    @example ambiente("vitest run — 61 passed (61)") → None
    """
    for campo in _campos(texto):
        nome = campo.removeprefix("ambiente: ")
        if nome in _AMBIENTES:
            return _AMBIENTES[nome]
    m = _RE_URL.search(texto)
    if not m:
        return None
    host = m.group(2).lower()
    return "local" if host.startswith(("localhost", "127.0.0.1")) else "homolog" if "homolog" in host else host


def componente(texto: str) -> str:
    """Serviço que o registro nomeia de forma reconhecível: imagem `api-leads:1.9.3` ou um campo que é só o nome
    (`fila-cobranca · tsc …`, `CI api-leads · …`). "" quando não nomeia.
    @example componente("swarm · prod · api-leads:1.9.1 — rollout completed · 3/3") → "api-leads"
    @example componente("eslint . — 0 errors, 3 warnings (no-unused-vars ×2)") → ""
    """
    m = _RE_IMAGEM.search(texto.lower())
    if m:
        return m.group(1)
    return next((m.group(1) for m in map(_RE_CAMPO_SERVICO.fullmatch, _campos(texto)) if m), "")


def _objeto(kind: str, texto: str) -> str | None:
    """A coisa de que o registro fala, por tipo: migration NNNN ou o deploy do componente (deploy_event); verbo +
    caminho (http_response); o comando como escrito (test_log / build_log); push do branch ou PR N (git_output).
    None quando não está escrito (rodada sem comando, "No migrations to apply", commit, anotação manual)."""
    plano = _sem_acento(texto)
    if kind == "deploy_event":
        m = _RE_MIGRATION_ASSUNTO.search(plano)
        if m:
            return f"migration {m.group(1) or m.group(2)}"
        return "deploy" if componente(texto) else None
    if kind == "http_response":
        m = _RE_URL.search(texto)
        return f"{m.group(1).upper()} {m.group(3) or '/'}" if m else None
    if kind in ("test_log", "build_log"):
        m = next((m for m in map(_RE_COMANDO.match, _campos(texto)) if m), None)
        return " ".join(m.group(0).split()) if m else None
    if kind == "git_output":
        m = _RE_GIT_ASSUNTO.search(plano)
        return (f"push {m.group(1)}" if m.group(1) else f"pr {m.group(2)}") if m else None
    return None


def assunto(kind: str, texto: str) -> tuple[str, str, str, str] | None:
    """(tipo, objeto, ambiente, componente) do registro, ou None quando o código não consegue dizer do que ele fala.
    Dois registros só disputam recência com o assunto IGUAL; None nunca supera nem é superado.
    @example assunto("deploy_event", "drizzle migrate · dev · 0015_lembrete_visita aplicada") → ("deploy_event", "migration 0015", "dev", "")
    @example assunto("deploy_event", "drizzle migrate · prod · No migrations to apply") → None
    @example assunto("test_log", "10:02 · revisão 5a5a5a5 · vitest run — 61 passed (61)") → ("test_log", "vitest run", "", "")
    @example assunto("test_log", "08:41 · revisão 5g5g5g5 · 29 passed, 1 failed") → None
    """
    objeto, amb = _objeto(kind, texto), ambiente(texto)
    if objeto is None or (amb is None and kind in _TIPOS_COM_AMBIENTE):
        return None
    return kind, objeto, amb or "", componente(texto)


# ---------------------------------------------------------------------------------------- checks (código)
_COMPARADORES = {
    "acima de": ">", "mais de": ">", "maior que": ">", "superior a": ">", ">": ">",
    "pelo menos": ">=", "no mínimo": ">=", "no minimo": ">=", "≥": ">=", ">=": ">=",
    "abaixo de": "<", "menos de": "<", "inferior a": "<", "<": "<",
    "no máximo": "<=", "no maximo": "<=", "até": "<=", "ate": "<=", "≤": "<=", "<=": "<=",
}
_RE_LIMIAR = re.compile(r"(" + "|".join(re.escape(k) for k in sorted(_COMPARADORES, key=len, reverse=True)) +
                        r")\s*(\d+(?:[.,]\d+)?)\s*(%|ms|réplicas?|replicas?)", re.I)
_METRICAS_PCT = {"statements": "statements", "instruções": "statements", "instrucoes": "statements", "branches": "branches",
                 "ramos": "branches", "functions": "functions", "funções": "functions", "funcoes": "functions",
                 "lines": "lines", "linhas": "lines"}
_RE_PCT_REG = re.compile(r"(statements|branches|functions|lines)\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*%", re.I)
_RE_PCT_SOLTO = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")
_ESTATS_MS = ("p50", "p95", "p99", "média", "media", "mean")
_RE_MS_REG = re.compile(r"(p50|p95|p99|média|media|mean)\s*[:=]?\s*(\d+(?:[.,]\d+)?)\s*ms", re.I)
_RE_MS_SOLTO = re.compile(r"(\d+(?:[.,]\d+)?)\s*ms\b", re.I)
_RE_REPLICAS_CLAIM = re.compile(r"(\d+)\s*r[ée]plicas?", re.I)
_RE_REPLICAS_REG = re.compile(r"\b(\d+)/(\d+)\b")
_RE_VERSAO = re.compile(r"\b(\d+\.\d+\.\d+)\b")
_RE_SERVICO = re.compile(r"\b([a-z]+-[a-z]+)\b")
_RE_REVISAO_CLAIM = re.compile(r"revis[ãa]o\s+([0-9a-f]{7,40})\b", re.I)
_RE_REVISAO_REG = re.compile(r"(?:revis[ãa]o\s+|\[[A-Za-z]+ |^)([0-9a-f]{7,40})\b", re.I | re.M)
_RE_MIGRATION_CLAIM = re.compile(r"migration\s+(\d{4})\b", re.I)
_RE_MIGRATION_REG = re.compile(r"\b(\d{4})_[a-z]", re.I)
# Checks que, falhando, NEUTRALIZAM o registro (é de outra revisão/outro objeto: não sustenta nem contradiz —
# LEIA-ME "outra revisão → insuficiente"); os demais, falhando, CONTRADIZEM (LEIA-ME: "número abaixo do limiar",
# "versão respondida diferente da afirmada").
CHECKS_NEUTRALIZAM = {"revision", "migration"}


def _num(s: str) -> float:
    return float(s.replace(",", "."))


def _compara(observado: float, op: str, limiar: float) -> bool:
    return {">": observado > limiar, ">=": observado >= limiar, "<": observado < limiar, "<=": observado <= limiar}[op]


def _check(reg_id: str, nome: str, afirmado: str, observado: str, vale: bool) -> dict:
    return {"record": reg_id, "check": nome, "claimed": afirmado, "observed": observado, "holds": vale}


_RE_AMB_AFIRMADO = (("prod", r"producao|\bprod\b"), ("homolog", r"homolog"), ("dev", r"\bdev\b"), ("local", r"localhost|\blocal\b"))


def _servico_afirmado(afirmacao: str) -> str | None:
    return next((s for s in _RE_SERVICO.findall(afirmacao.lower()) if "-" in s), None)


def nao_pertinente(afirmacao: str, texto: str) -> str | None:
    """Motivo pelo qual um número deste registro NÃO se compara com a afirmação, ou None quando é pertinente (revisão
    do Codex 2026-10-01, achado 3: 412 ms em localhost não contradiz "menos de 300 ms em produção"; versão em homolog
    nada diz de produção). Só o que o código deriva: ambiente reconhecível fora dos que a afirmação nomeia; componente
    nomeado no registro diferente do serviço nomeado na afirmação. Host literal (nem local nem homolog) é pertinente:
    se ele é produção, quem julga é o Jev. O registro continua no state; só não nasce `check` dele.
    @example nao_pertinente("Rota responde em menos de 300 ms em produção.", "GET http://localhost:3000/x → 200 · tempo: 412 ms") → "ambiente local ≠ prod"
    @example nao_pertinente("Cobertura acima de 80%.", "coverage · statements 78.4%") → None
    """
    plano = _ascii(afirmacao)
    afirmados = sorted(nome for nome, padrao in _RE_AMB_AFIRMADO if re.search(padrao, plano))
    amb = ambiente(texto)
    if afirmados and amb in _AMBIENTES.values() and amb not in afirmados:
        return f"ambiente {amb} ≠ {'/'.join(afirmados)}"
    servico, comp = _servico_afirmado(afirmacao), componente(texto)
    if servico and comp and comp != servico:
        return f"componente {comp} ≠ {servico}"
    return None


def checks(afirmacao: str, registros: list[dict]) -> list[dict]:
    """Os checks que podem entrar no state: revisão/migration de todo registro e os numéricos só de registro
    PERTINENTE (`nao_pertinente`) — um número só é comparado com a afirmação quando o registro fala do mesmo
    ambiente e componente, valendo ou falhando.
    @example checks("Rota responde em menos de 300 ms em produção.", [{"id": "e1", "texto": "GET http://localhost:3000/x → 200 · tempo: 412 ms"}]) → []
    """
    textos = {r["id"]: r["texto"] for r in registros}
    return [c for c in _checks_brutos(afirmacao, registros)
            if c["check"] in CHECKS_NEUTRALIZAM or nao_pertinente(afirmacao, textos[c["record"]]) is None]


def _checks_brutos(afirmacao: str, registros: list[dict]) -> list[dict]:
    """Comparações exatas entre afirmação e registros, feitas ANTES da chamada (limite #2: o Jev não compara
    números). Só produz check quando há número DOS DOIS LADOS; sem par, nada (o Jev julga o resto).
    @example checks("Cobertura acima de 80%.", [{"id": "e1", "texto": "coverage · statements 78.4% · lines 78.9%"}])
             → [{"record": "e1", "check": "coverage", "claimed": "statements > 80%", "observed": "78.4%", "holds": False}]
    @example checks("Versão 1.9.2 da api-leads em produção.", [{"id": "e2", "texto": "GET …/versao → 200 · {\\"versao\\":\\"1.9.1\\"}"}])
             → [{"record": "e2", "check": "version", "claimed": "1.9.2", "observed": "1.9.1", "holds": False}]
    @example checks("Testes passando na revisão b7e2f90.", [{"id": "e2", "texto": "CI · revisão 4c1d8aa · 52 passed"}])
             → [{"record": "e2", "check": "revision", "claimed": "b7e2f90", "observed": "4c1d8aa", "holds": False}]
    """
    saida = []
    plano = _ascii(afirmacao)
    # --- limiares (cobertura %, latência ms, réplicas com comparador)
    for comp, valor, unidade in _RE_LIMIAR.findall(plano):
        op, limiar, unidade = _COMPARADORES[comp.lower()], _num(valor), unidade.lower()
        for r in registros:
            obs = _observado(unidade, plano, r["texto"])
            if obs is not None:
                saida.append(_check(r["id"], {"%": "coverage", "ms": "latency"}.get(unidade, "replicas"),
                                    f"{obs[0]} {op} {valor}{'%' if unidade == '%' else ' ' + unidade}", obs[2],
                                    _compara(obs[1], op, limiar)))
    # --- réplicas sem comparador ("3 réplicas no ar") = igualdade com as que rodam
    if not any(c["check"] == "replicas" for c in saida):
        m = _RE_REPLICAS_CLAIM.search(plano)
        if m:
            for r in registros:
                rep = _RE_REPLICAS_REG.search(r["texto"])
                if rep:
                    saida.append(_check(r["id"], "replicas", f"{m.group(1)} replicas running", f"{rep.group(1)}/{rep.group(2)}",
                                        int(rep.group(1)) == int(m.group(1)) == int(rep.group(2))))
    # --- versão x.y.z: registro do mesmo serviço (ou sem serviço nomeado) que só mostra outra versão → falha
    mv = _RE_VERSAO.search(afirmacao)
    if mv:
        servico = _servico_afirmado(afirmacao)
        for r in registros:
            versoes = _RE_VERSAO.findall(r["texto"])
            outros = [s for s in _RE_SERVICO.findall(r["texto"].lower())]
            if versoes and (servico is None or servico in r["texto"].lower() or not outros):
                saida.append(_check(r["id"], "version", mv.group(1), ", ".join(versoes), mv.group(1) in versoes))
    # --- revisão (hash) e migration (número): outro objeto → o registro não fala da coisa afirmada
    for nome, re_claim, re_reg in (("revision", _RE_REVISAO_CLAIM, _RE_REVISAO_REG), ("migration", _RE_MIGRATION_CLAIM, _RE_MIGRATION_REG)):
        mc = re_claim.search(afirmacao)
        if mc:
            for r in registros:
                achados = {a.lower() for a in re_reg.findall(r["texto"])}
                if achados:
                    saida.append(_check(r["id"], nome, mc.group(1).lower(), ", ".join(sorted(achados)), mc.group(1).lower() in achados))
    return saida


def _observado(unidade: str, afirmacao_plana: str, texto: str) -> tuple[str, float, str] | None:
    """(métrica, valor, texto observado) no registro para a unidade do limiar; None quando o registro não traz
    o número comparável. Cobertura sem métrica nomeada → `statements` (LEIA-ME). Latência sem estatística
    nomeada → p95 se houver, senão o único valor em ms."""
    if unidade == "%":
        metrica = next((v for k, v in _METRICAS_PCT.items() if k in afirmacao_plana), "statements")
        nomeados = {k.lower(): _num(v) for k, v in _RE_PCT_REG.findall(texto)}
        if metrica in nomeados:
            return metrica, nomeados[metrica], f"{metrica} {nomeados[metrica]}%"
        soltos = _RE_PCT_SOLTO.findall(texto)
        if not nomeados and len(soltos) == 1 and re.search(r"cobertura|coverage", texto, re.I):
            return "coverage", _num(soltos[0]), f"{soltos[0]}%"
        return None
    if unidade == "ms":
        estat = next((e for e in _ESTATS_MS if e in afirmacao_plana), None)
        nomeados = {k.lower(): _num(v) for k, v in _RE_MS_REG.findall(texto)}
        alvo = estat or ("p95" if "p95" in nomeados else None)
        if alvo and alvo in nomeados:
            return alvo, nomeados[alvo], f"{alvo} {nomeados[alvo]} ms"
        soltos = _RE_MS_SOLTO.findall(texto)
        if not estat and not nomeados and len(soltos) == 1:
            return "ms", _num(soltos[0]), f"{soltos[0]} ms"
        return None
    rep = _RE_REPLICAS_REG.search(texto)
    return ("replicas", float(rep.group(1)), f"{rep.group(1)}/{rep.group(2)}") if rep else None


# ---------------------------------------------------------------------------------------- pedido
def validar_registros(registros: list[dict]) -> None:
    """Antes da chamada: 1–8 registros, IDs únicos, tipo conhecido, texto não vazio. ID repetido religaria
    duas respostas ao mesmo registro em silêncio; tipo desconhecido não tem nome literal no state."""
    if not P.MIN_REGISTROS <= len(registros) <= P.MAX_REGISTROS:
        raise ValueError(f"{len(registros)} registros; esperado {P.MIN_REGISTROS}–{P.MAX_REGISTROS}")
    ids = [r.get("id") for r in registros]
    if any(not isinstance(i, str) or not i.strip() for i in ids) or len(set(ids)) != len(ids):
        raise ValueError(f"IDs de registro inválidos ou repetidos: {ids!r}")
    for r in registros:
        if r.get("tipo") not in P.KIND:
            raise ValueError(f"tipo de registro desconhecido: {r.get('tipo')!r}")
        if not isinstance(r.get("texto"), str) or not r["texto"].strip():
            raise ValueError(f"registro {r['id']} sem texto")


def triagem(caso: dict) -> dict:
    """Trabalho do código ANTES da chamada: quem entra no state e com quais checks (revisão do Codex 2026-10-01,
    achados 2 e 3 — na rodada 1 o registro neutralizado ficava no state e os 4 Nouls de parte ainda o viam; e um
    check numérico negativo decidia `contradicted` antes de se saber se o registro era pertinente e vigente).
    - `neutros` {id: motivo}: registro de OUTRA revisão/migration — não fala da coisa afirmada, sai do state;
    - `vencidos` {id: motivo}: registro cujo número foi refeito por outro mais recente do MESMO assunto (cobertura
      78% de antes × 85% de agora) — sai do state; sem assunto reconhecível os dois ficam e o número ruim decide;
    - `nao_pertinentes` {id: motivo}: registro de outro ambiente/componente — FICA no state, mas não gera check numérico;
    - `registros` (ordem cronológica) e `checks`: o que sobra, que é o que o Jev vê e o que `compor` usa.
    """
    validar_registros(caso["registros"])
    ordenados = ordenar(caso["registros"])
    brutos = _checks_brutos(caso["afirmacao"], ordenados)
    neutros, fora = {}, {}
    for c in brutos:
        if c["check"] in CHECKS_NEUTRALIZAM:
            if not c["holds"]:
                neutros.setdefault(c["record"], f"{c['check']} {c['observed']} ≠ {c['claimed']}")
        elif c["record"] not in fora:
            motivo = nao_pertinente(caso["afirmacao"], next(r["texto"] for r in ordenados if r["id"] == c["record"]))
            if motivo:
                fora[c["record"]] = motivo
    validos = [c for c in brutos if c["record"] not in neutros and (c["check"] in CHECKS_NEUTRALIZAM or c["record"] not in fora)]
    por_assunto: dict[tuple, list[str]] = {}
    for r in ordenados:  # ordem cronológica: o último de cada (check, assunto) é o vigente
        chave = assunto(P.KIND[r["tipo"]], r["texto"])
        for nome in dict.fromkeys(c["check"] for c in validos if c["record"] == r["id"] and c["check"] not in CHECKS_NEUTRALIZAM):
            if chave is not None:
                por_assunto.setdefault((nome, chave), []).append(r["id"])
    vencidos = {i: f"{nome} refeito por {ids[-1]} (mesmo assunto, mais recente)" for (nome, _), ids in por_assunto.items() for i in ids[:-1]}
    registros = [r for r in ordenados if r["id"] not in neutros and r["id"] not in vencidos]
    return {"registros": registros, "checks": [c for c in validos if c["record"] not in vencidos],
            "neutros": neutros, "vencidos": vencidos, "nao_pertinentes": fora}


def fora_do_state(caso: dict) -> dict:
    """O que a triagem tirou do jogo, para o relatório e para a saída de `auditar`."""
    t = triagem(caso)
    return {k: t[k] for k in ("neutros", "vencidos", "nao_pertinentes")}


def state_de(caso: dict, excluir: set[str] | None = None) -> dict:
    """Caso rotulado (pt) → state enxuto: afirmação, registros pertinentes e vigentes (`triagem`) em ordem
    cronológica com tipo literal em inglês, e `checks` calculados pelo código. A posição em `records` é o índice que
    as perguntas citam (`records[i]`). `excluir` = IDs fora da 2ª passada (superados por outro mais recente do mesmo assunto).
    @example state_de({"afirmacao": "Build verde.", "registros": [{"id": "e1", "tipo": "log_build", "texto": "next build — ok"}]})
             → {"claim": "Build verde.", "records": [{"id": "e1", "kind": "build_log", "text": "next build — ok"}], "checks": []}
    """
    t = triagem(caso)
    registros = [r for r in t["registros"] if r["id"] not in (excluir or set())]
    ids = {r["id"] for r in registros}
    return {
        "claim": caso["afirmacao"],
        "records": [{"id": r["id"], "kind": P.KIND[r["tipo"]], "text": r["texto"]} for r in registros],
        "checks": [c for c in t["checks"] if c["record"] in ids],
    }


def state_bruto(caso: dict) -> dict:
    """Todos os registros, sem triagem nem checks: o que o BASELINE lê (ele não herda trabalho do auditor)."""
    validar_registros(caso["registros"])
    return {"claim": caso["afirmacao"],
            "records": [{"id": r["id"], "kind": P.KIND[r["tipo"]], "text": r["texto"]} for r in ordenar(caso["registros"])]}


def pedido(caso: dict, excluir: set[str] | None = None) -> tuple[dict, dict]:
    """(state, questions) de uma afirmação: 2 Nouls por registro + `established` + 4 Nouls por parte. State sem
    registro (todos de outra revisão/migration) NÃO vai ao Jev: `compor` devolve `insufficient_evidence` sozinho."""
    state = state_de(caso, excluir)
    return state, P.perguntas(len(state["records"]))


def precisa_segunda_passada(saida: dict) -> bool:
    """2ª chamada SÓ quando a 1ª resposta decide o próximo state (NÚCLEO §5): algum registro foi superado por outro
    mais recente do mesmo assunto e nenhuma contradição ficou de pé. Os Nouls de parte da 1ª passada ainda viram o
    registro superado (verde novo com vermelho velho na lista → partes em 0,65–0,69 no ajuste); a 2ª passada manda o
    state sem ele. Contradição decidida não precisa: a precedência já fechou o veredito."""
    return bool(saida["superados"]) and saida["relacao"] != "contradicted"


# ---------------------------------------------------------------------------------------- resposta → veredito
def validar(resposta: dict, n: int) -> dict:
    """Resposta da API → números validados pela infra comum: todo ID esperado presente, tipo noul, número real em
    [0,1] (não bool, não string); ID inesperado também é erro (integracao-segura). Falha = erro, nunca `supported`."""
    esperados = set(P.perguntas(n))
    recebidos = set(resposta.get("answers") or {})
    if recebidos != esperados:
        raise ValueError(f"IDs da resposta não batem: faltam {sorted(esperados - recebidos)}, sobram {sorted(recebidos - esperados)}")
    return {"supports": [CG.noul(resposta, f"supports_{i}") for i in range(n)],
            "contradicts": [CG.noul(resposta, f"contradicts_{i}") for i in range(n)],
            "established": CG.noul(resposta, "established"),
            "parts": {q: CG.noul(resposta, q) for q in P.PARTES_NOULS}}


def valor_falha(n: int, motivo: str) -> dict:
    """Valor no formato de `validar` para uma afirmação cuja chamada/resposta falhou: zeros só para as tabelas não
    quebrarem; `falha` faz `compor` fechar em `revisa` antes de ler qualquer número."""
    return {"supports": [0.0] * n, "contradicts": [0.0] * n, "established": 0.0,
            "parts": {q: 0.0 for q in P.PARTES_NOULS}, "falha": motivo}


def _faixa(valor: float, nao: float, sim: float) -> bool | None:
    if valor >= sim:
        return True
    if valor <= nao:
        return False
    return None


def _polaridade(sup: float, con: float) -> str | None:
    """Sinal forte do registro para a regra de recência: `contra`, `sup` ou nenhum (abaixo de APOIO_MIN)."""
    if con >= P.APOIO_MIN and con > sup:
        return "contra"
    if sup >= P.APOIO_MIN:
        return "sup"
    return None


def provada(v: dict, composicao: str | None = None) -> tuple[bool | None, str]:
    """(True / False / None=dúvida, descrição) da leitura "a afirmação está provada", conforme `perguntas.COMPOSICAO`:
    `established` = só o Noul global; `parts` = os 4 Nouls por parte (todos ≥ sim → provada; qualquer ≤ não → não);
    `both` = provada exige as duas leituras; não provada se qualquer uma diz não; o resto é dúvida."""
    composicao = composicao or P.COMPOSICAO
    e = _faixa(v["established"], *P.FAIXA["established"])
    partes = {q: _faixa(x, *P.FAIXA["parts"]) for q, x in v["parts"].items()}
    if any(x is False for x in partes.values()):
        pt = False
    elif all(x is True for x in partes.values()):
        pt = True
    else:
        pt = None
    desc_e = f"established {v['established']:.2f}"
    desc_p = "partes " + " ".join(f"{q.split('_')[0]} {x:.2f}" for q, x in v["parts"].items())
    if composicao == "established":
        return e, desc_e
    if composicao == "parts":
        return pt, desc_p
    if e is False or pt is False:
        return False, f"{desc_e}; {desc_p}"
    if e is True and pt is True:
        return True, f"{desc_e}; {desc_p}"
    return None, f"{desc_e}; {desc_p}"


def superados(state: dict, v: dict, vivos: list[int]) -> dict[int, str]:
    """"O mais recente prevalece" (LEIA-ME §5: "sobre o mesmo assunto"), em código: para cada ASSUNTO (`assunto`:
    tipo, objeto, ambiente, componente), o registro vivo mais recente com sinal forte manda; os anteriores do mesmo
    assunto com o sinal OPOSTO são superados (verde velho diante de vermelho novo, e o inverso). Assuntos diferentes
    não se superam: dev aplicado + prod falhando → os dois valem; deploy ok + saúde 503 → os dois valem. Registro
    sem assunto reconhecível (rodada sem comando, "No migrations to apply", manual) não supera nem é superado — sem
    saber que dois registros falam da mesma coisa, apagar um deles é chute (rodada 1 agrupava por tipo: AE-T014).
    Devolve {índice: motivo}."""
    saida = {}
    por_assunto: dict[tuple, list[int]] = {}
    for i in vivos:  # `records` já está em ordem cronológica
        chave = assunto(state["records"][i]["kind"], state["records"][i]["text"])
        if chave is not None:
            por_assunto.setdefault(chave, []).append(i)
    for chave, idx in por_assunto.items():
        fortes = [(i, _polaridade(v["supports"][i], v["contradicts"][i])) for i in idx]
        fortes = [(i, p) for i, p in fortes if p]
        if not fortes:
            continue
        ultimo, sinal = fortes[-1]
        for i, p in fortes[:-1]:
            if p != sinal:
                saida[i] = f"superado por {state['records'][ultimo]['id']} (mesmo assunto: {' · '.join(x for x in chave[1:] if x)}; mais recente, {sinal})"
    return saida


def compor(v: dict, state: dict, composicao: str | None = None) -> dict:
    """Números validados + state → veredito pela precedência do LEIA-ME, com os limiares de `perguntas`.

    O state já chega sem os registros de outra revisão/migration e sem os de número refeito (`triagem`), e só com
    checks de registro pertinente e vigente — por isso um check que falha aqui pode decidir.
    0. state sem registro → `insufficient_evidence` (nada pertinente foi anexado), sem resposta do Jev (`v` None);
    1. check de número/versão que falha (código) → `contradicted`, sem olhar o Jev;
    2. registro superado por outro mais recente do mesmo assunto (`superados`) sai do jogo;
    3. maior `contradicts` vivo ≥ sim → `contradicted`; na faixa de dúvida → `revisa`;
    4. senão a leitura "provada" (`provada()`: Noul global, Nouls por parte ou ambos, conforme `COMPOSICAO`) →
       `supported` (exige ≥ 1 registro de apoio) / `insufficient_evidence` / meio → `revisa`. `supported` NUNCA sai
       de um state que ainda contém registro superado: os Nouls de parte o viram (→ `revisa`; a 2ª passada decide).
    `registros_de_apoio`: os que contradizem (em `contradicted`) ou os que sustentam parte (nos demais), ≥ APOIO_MIN.
    """
    recs = state["records"]
    ids = [r["id"] for r in recs]
    if not recs:
        return {"relacao": "insufficient_evidence", "apoio": [], "superados": {},
                "motivo": "código: nenhum registro pertinente (todos de outra revisão/migration)"}
    if v.get("falha"):
        # Falha operacional (chamada ou resposta fora do contrato, `run._validar_seguro`): classe segura `revisa`,
        # nunca `supported` nem `insufficient_evidence` (revisão do Codex no comparador, 2026-10-01, família).
        return {"established": v["established"], "parts": v["parts"], "supports": v["supports"],
                "contradicts": v["contradicts"], "superados": {}, "relacao": P.REVISA, "apoio": [], "motivo": v["falha"]}
    duros = [c for c in state["checks"] if not c["holds"] and c["check"] not in CHECKS_NEUTRALIZAM]
    base = {"established": v["established"], "parts": v["parts"], "supports": v["supports"], "contradicts": v["contradicts"],
            "superados": {}}
    if duros:
        apoio = sorted({c["record"] for c in duros}, key=ids.index)
        return {**base, "relacao": "contradicted", "apoio": apoio,
                "motivo": "código: " + "; ".join(f"{c['record']} {c['check']} {c['observed']} não satisfaz {c['claimed']}" for c in duros)}
    vivos = list(range(len(recs)))
    sup = superados(state, v, vivos)
    base["superados"] = {ids[i]: m for i, m in sup.items()}
    vivos = [i for i in vivos if i not in sup]
    c_nao, c_sim = P.FAIXA["contradicts"]
    contra = [i for i in vivos if v["contradicts"][i] >= P.APOIO_MIN]
    maior_contra = max((v["contradicts"][i] for i in vivos), default=0.0)
    if _faixa(maior_contra, c_nao, c_sim) is True:
        return {**base, "relacao": "contradicted", "apoio": [ids[i] for i in contra], "motivo": f"contradição {maior_contra:.2f}"}
    sustentam = [ids[i] for i in vivos if v["supports"][i] >= P.APOIO_MIN]
    est, desc = provada(v, composicao)
    if _faixa(maior_contra, c_nao, c_sim) is None:
        # Dúvida de contradição (ajuste 2026-10-01: homolog, localhost e rodada cancelada deram 0,47–0,64): se nada está
        # estabelecido, o veredito já é "não provado" — mesma ação (pedir prova); só vira `revisa` quando a afirmação
        # parece estabelecida E possivelmente contradita (conflito que um humano precisa olhar).
        if est is False:
            return {**base, "relacao": "insufficient_evidence", "apoio": sustentam,
                    "motivo": f"não provada ({desc}); contradição possível ({maior_contra:.2f})"}
        return {**base, "relacao": P.REVISA, "apoio": sustentam, "motivo": f"contradição possível ({maior_contra:.2f})"}
    if est is True:
        if sup:
            # Revisão do Codex 2026-10-01, achado 2: as partes foram julgadas com o registro superado ainda no state;
            # cobertura que pode vir de registro excluído não aprova. A 2ª passada (state sem ele) é quem decide.
            return {**base, "relacao": P.REVISA, "apoio": sustentam, "motivo": f"provada ({desc}) com registro superado no state"}
        if sustentam or not P.SUPPORTED_EXIGE_APOIO:
            return {**base, "relacao": "supported", "apoio": sustentam, "motivo": f"provada ({desc})"}
        return {**base, "relacao": P.REVISA, "apoio": [], "motivo": f"provada ({desc}) sem registro de apoio"}
    if est is False:
        return {**base, "relacao": "insufficient_evidence", "apoio": sustentam, "motivo": f"não provada ({desc})"}
    return {**base, "relacao": P.REVISA, "apoio": sustentam, "motivo": f"dúvida ({desc})"}


def compor_sem_global(v: dict, state: dict) -> dict:
    """Variante medida no ajuste: SEM o Noul global — `supported` quando nenhum registro vivo contradiz e algum
    sustenta parte. Mostra o que `established` acrescenta (a leitura "todas as partes cobertas")."""
    saida = compor(v, state)
    if saida["relacao"] == "contradicted" or "contradição possível" in saida["motivo"]:
        return saida
    rel = "supported" if saida["apoio"] else "insufficient_evidence"
    return {**saida, "relacao": rel, "motivo": "sem Noul global: " + ("algum registro sustenta" if saida["apoio"] else "nenhum sustenta")}


def decidir(resposta: dict, state: dict) -> dict:
    return compor(validar(resposta, len(state["records"])), state)


def auditar(jev, caso: dict) -> dict:
    """Uma afirmação de ponta a ponta: registros validados, triagem e checks em código, uma requisição (duas quando um
    registro foi superado e nada contradiz; nenhuma quando a triagem não deixa registro), veredito em código."""
    fora = fora_do_state(caso)
    state, questions = pedido(caso)
    if not state["records"]:
        return {**compor(None, state), **fora, "passada": 0}
    saida = decidir(jev.perguntar(state, questions), state)
    if precisa_segunda_passada(saida):
        state2, questions2 = pedido(caso, set(saida["superados"]))
        saida2 = decidir(jev.perguntar(state2, questions2), state2)
        return {**saida2, **fora, "passada": 2, "superados": saida["superados"]}
    return {**saida, **fora, "passada": 1}


# ---------------------------------------------------------------------------------------- baseline de código
def _ascii(texto: str) -> str:
    """Minúsculas ASCII. `≥` e `≤` viram `>=` e `<=` ANTES de normalizar: o `encode("ascii", "ignore")` os apagava e
    "Cobertura ≥ 80%" ficava sem check — a comparação voltava para o Jev (revisão do Codex 2026-10-01, achado 4)."""
    texto = texto.replace("≥", ">=").replace("≤", "<=")
    return unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()


def _tokens(texto: str) -> set[str]:
    """Palavras ≥ 4 letras fora da lista genérica + números com ≥ 2 dígitos (0011, 1.9.2, 80) + hashes de 7+ hex."""
    plano = _ascii(texto)
    palavras = {w for w in re.findall(r"[a-z]{4,}", plano) if w not in P.PALAVRAS_GENERICAS}
    numeros = {n.rstrip(".,") for n in re.findall(r"\d[\d.,]*", plano) if len(re.sub(r"\D", "", n)) >= 2}
    hashes = set(re.findall(r"\b[0-9a-f]{7,}\b", plano)) - numeros
    return palavras | numeros | hashes


def baseline(state: dict) -> dict:
    """Só regra de código, sem Jev (regra do briefing): registro com palavra de falha → `contradicted`; afirmação
    de produção com registro de localhost/homolog/dev e nenhum de prod → `contradicted`; palavra-chave da
    afirmação presente em algum registro de processo → `supported`; senão `insufficient_evidence`.
    @example baseline({"claim": "Build do portal-web verde.", "records": [{"id": "e1", "kind": "build_log", "text": "portal-web · next build — compiled"}]})
             → {"relacao": "supported", "apoio": ["e1"]}
    """
    recs = state["records"]
    falhas = [r["id"] for r in recs if re.search(P.RE_FALHA, r["text"])]
    if falhas:
        return {"relacao": "contradicted", "apoio": falhas}
    if re.search(P.RE_PROD, state["claim"], re.I):
        fora = [r["id"] for r in recs if re.search(P.RE_NAO_PROD, r["text"], re.I)]
        if fora and not any(re.search(P.RE_PROD, r["text"], re.I) for r in recs):
            return {"relacao": "contradicted", "apoio": fora}
    chaves = _tokens(state["claim"])
    acham = [r["id"] for r in recs if r["kind"] != "manual_note" and _tokens(r["text"]) & chaves]
    return {"relacao": "supported" if acham else "insufficient_evidence", "apoio": acham}
