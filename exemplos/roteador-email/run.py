"""Roda o roteador de e-mail nos e-mails REAIS anonimizados e gera `resultados.md` sozinho — só com agregados.

Uso:
  python run.py ajuste       afinação (resultados.md marcado "em afinação"; lê só os registros `conjunto == "ajuste"`)
  python run.py congelar     roda o ajuste e grava o manifesto `congelamento.json` (hash de perguntas.py, roteador.py,
                             run.py, do arquivo de dados e o critério de continuar; hash de _comum/ só como registro)
  python run.py              ajuste + teste numa execução; o teste só roda com o manifesto batendo. A PRIMEIRA execução
                             completa com teste também grava `resultados-rodada1.md` (a rodada cega) e nunca o reescreve
  JEV_MODO=gravado python run.py   reproduz do cache, sem chave (o cache só existe na pasta de estudo)

PRIVACIDADE — o que este script garante:
  - a única fonte é `.local/dados-reais/email/emails-anon-v2.jsonl` (fora do Git; a v1 só serviu à rodada cega e
    não vai mais à API); sem ela o script para com uma mensagem clara: o exemplo só reproduz na pasta de estudo,
    e o `resultados.md` versionado é a prova pública;
  - o cache do Jev (contém o state = texto) fica em `.local/dados-reais/email/cache-jev/`, nunca nesta pasta;
  - NENHUM texto de e-mail vai para o relatório: só agregados, IDs `EM-xxxx`, classes, `decidido_por`, números
    do Jev, sinais calculados em código e motivos montados pelo código (nomes de pergunta e números). Assunto,
    remetente, corpo e o nome da regra interna de produção (`regra`; revisão do Codex, 2026-10-01) nunca são escritos.

GABARITO = a decisão do classificador em produção (F11). Tudo aqui é CONCORDÂNCIA com produção, não acerto contra
verdade independente. "Escalar" = mandar ao LLM que já classifica hoje; como o gabarito É a decisão de produção,
o escalado concorda por definição (1,0) — o que se mede é quanto o Jev decide sozinho e quanto disso concorda.

Uma requisição por e-mail. Falha operacional (chamada, cache faltando, resposta fora do contrato, registro
inválido) NÃO aborta o lote: aquele e-mail sai `escala` por `roteador.rotear_seguro`, é contado à parte, e conjunto
com falha não vira rodada cega. A carga valida cada registro ANTES da máscara (revisão do Codex, 2026-10-01): texto
com tipo errado ou sinal inválido vira falha daquele registro; metadado indispensável para medir (`id`, `grupo`,
`conjunto`, `classe`, `decidido_por`) ausente ou inválido PARA o script — sem gabarito não há veredito.
Bateria do código, sem dados reais: `testa_falhas.py`.
"""
from __future__ import annotations

import contextlib
import datetime
import hashlib
import json
import os
import queue
import random
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
import perguntas as P  # noqa: E402
import roteador as R  # noqa: E402
from jevcache import PRECO_US_POR_MILHAO_ENTRADA, Jev  # noqa: E402

# Dados e cache FORA do repositório (`.local/` está no .gitignore e não vai para a versão pública).
DADOS_REL = "../../.local/dados-reais/email/emails-anon-v2.jsonl"   # rodada 1 (cega) usou a v1; ver README
DADOS = (AQUI / DADOS_REL).resolve()
CACHE = DADOS.parent / "cache-jev"
RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
# Manifesto: código executado (inclusive este arquivo), o arquivo de dados inteiro (ajuste + teste) e o critério.
CONGELADOS = ["perguntas.py", "roteador.py", "run.py", DADOS_REL]
INFORMATIVOS = ["../_comum/jevcache.py", "../_comum/congelamento.py", "../_comum/metricas.py"]
SEM_DADOS = ("dados privados ausentes: este exemplo só reproduz na pasta de estudo (falta "
             ".local/dados-reais/email/emails-anon-v2.jsonl, que nunca entra no Git). A prova pública é o "
             "`resultados.md` versionado; a bateria `testa_falhas.py` roda sem dados.")
METADADOS = ("id", "grupo", "conjunto", "classe", "decidido_por")   # sem eles não há gabarito nem recorte

PARALELO = 4   # ~3.000 tokens por requisição: 4 em paralelo fica longe do teto de 100 mil tokens/s
SEMENTE = 20261001
N_BOOT = 2000
BASE, TUDO_LLM, FORCADO, SO_CONF, JEV = ("baseline (regras de código)", "tudo no LLM (hoje)", "Jev forçado (sem limiar)",
                                         "Jev só confiança", "Jev roteador (política)")
VARIANTES = [BASE, TUDO_LLM, FORCADO, SO_CONF, JEV]
CAIXA = ("principal", "notificacoes")   # decidir uma destas põe o e-mail na caixa de entrada
FORA = ("spam", "golpe")                # decidir uma destas tira o e-mail da caixa
A_PARTE = "redes_sociais"               # sem caso no ajuste: fora do critério e das tabelas principais
RECORTES = {
    "todos": lambda r: True,
    "só regra": lambda r: r["decidido_por"] == "rule",
    "só IA": lambda r: str(r["decidido_por"]).startswith("ai_"),
}
REC_CRITERIO = "só IA"
LIMIARES_CURVA = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]

# ---------------------------------------------------------------- custo do LLM (ESTIMADO; nada é chamado)
# Mesmas premissas de preço de `../roteador-jev-llm/run.py` (tabela recebida do dono em 2026-09-30). Em produção
# o resíduo vai a Claude → Codex → API; aqui o custo de "escalar" é estimado nos dois extremos de preço.
LLM_BARATO = {"nome": "gpt-6-luna", "entrada": 0.10, "saida": 0.50}
LLM_RACIOCINIO = {"nome": "gpt-6-astra", "entrada": 10.00, "saida": 50.00}
TOKENS_POR_CARACTERE = 1 / 4   # aproximação grosseira para pt-BR
LLM_PROMPT = 1500              # instruções do classificador + regras da caixa (premissa)
LLM_SAIDA = 150                # classe + justificativa curta em JSON (premissa)

# Máscara de última milha (defesa em profundidade, NÚCLEO §10): a anonimização deixa passar nome próprio em
# MAIÚSCULAS logo depois de uma saudação (limite declarado no LEIA-ME dos dados). O que casar vira [NOME] ANTES
# de qualquer envio. Não substitui o anonimizador; só fecha o padrão que a leitura do ajuste encontrou.
_CAIXA_ALTA = r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}"
_NOME_APOS_SAUDACAO = re.compile(
    r"((?:Ol[áa]|Oi|Prezad[oa]s?(?:\(a\))?|Car[oa](?:\(a\))?|Sr\.?(?:\(a\))?\.?|Sra\.?|Senhor(?:a|\(a\))?)[,:!]?\s+)"
    rf"({_CAIXA_ALTA}(?:\s+{_CAIXA_ALTA}){{1,5}})")


# ---------------------------------------------------------------------------------------- dados
def mascarar(texto: str | None) -> tuple[str | None, int]:
    """(texto com nome em maiúsculas após saudação trocado por [NOME], quantas trocas)."""
    if not texto:
        return texto, 0
    return _NOME_APOS_SAUDACAO.subn(lambda m: m.group(1) + "[NOME]", texto)


def _metadados_ok(r, n_linha: int) -> None:
    """Para o script se faltar o que mede: sem `classe`/`decidido_por`/`conjunto`/`id`/`grupo` válidos não há
    gabarito nem recorte, e um veredito calculado em cima disso seria inventado."""
    faltam = [k for k in METADADOS if not isinstance(r.get(k), str) or not r[k]] if isinstance(r, dict) else list(METADADOS)
    if not faltam and r["classe"] not in P.CLASSES:
        faltam.append("classe (fora das 6)")
    if not faltam and r["conjunto"] not in ("ajuste", "teste"):
        faltam.append("conjunto (não é ajuste/teste)")
    if faltam:
        sys.exit(f"registro {n_linha} do arquivo de dados sem metadado indispensável: {', '.join(faltam)} — "
                 "sem gabarito não há veredito (o arquivo de dados precisa de conserto; nenhum texto é mostrado)")


def chave_state(r: dict) -> str:
    """Hash do state que o Jev leria (depois da máscara): mede repetição de campanha entre e dentro dos conjuntos."""
    return hashlib.sha256(json.dumps(R.state_de(r), sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def carregar(conjunto: str, caminho: Path = DADOS) -> list[dict]:
    """Registros de UM conjunto (`ajuste` ou `teste`), validados e já com a máscara de última milha. Os registros do
    outro conjunto são descartados na leitura, sem serem guardados nem inspecionados: afinar nunca vê o teste.
    Registro com texto ou sinal inválido (`roteador.validar_registro`) fica marcado `_invalido` e sem máscara: vai
    virar `escala` por falha operacional em `rotear_seguro`, contado à parte, sem abortar o lote."""
    if not caminho.exists():
        sys.exit(SEM_DADOS)
    casos = []
    with caminho.open(encoding="utf-8") as f:
        for n_linha, linha in enumerate(f, 1):
            if not linha.strip():
                continue
            try:
                r = json.loads(linha)
            except ValueError:
                sys.exit(f"registro {n_linha} do arquivo de dados não é JSON válido — conserte o arquivo")
            _metadados_ok(r, n_linha)
            if r["conjunto"] != conjunto:
                continue
            try:
                R.validar_registro(r)
            except ValueError as e:
                r["_invalido"] = type(e).__name__
                r["_mascarado"], r["_trocas"], r["_state"] = False, 0, None
                casos.append(r)
                continue
            trocas = 0
            for campo in ("assunto", "texto"):
                r[campo], n = mascarar(r.get(campo))
                trocas += n
            r["_invalido"], r["_mascarado"], r["_trocas"] = None, trocas > 0, trocas
            r["_state"] = chave_state(r)
            casos.append(r)
    return casos


# ---------------------------------------------------------------------------------------- execução
def compartilhar_travas(instancias: list) -> None:
    """As instâncias dividem a MESMA tabela de travas por pedido. A trava do `jevcache` é por instância e aqui cada
    linha de execução tem a sua: sem isto, dois e-mails de state idêntico em linhas diferentes chamavam a API duas
    vezes (15 vezes na rodada 2) e um deles consumia uma resposta que não é a que ficou gravada — o replay
    `gravado` divergia do `auto` em 3 e-mails do recorte `só regra`. Mexe em atributo interno do `Jev` de propósito:
    a infra comum não é editada por este exemplo. (Desde 2026-10-01 ~15h45 o `jevcache` divide a tabela por pasta
    de cache entre instâncias: esta função ficou redundante e inofensiva; fica porque o manifesto cobre `run.py`.)"""
    for j in instancias[1:]:
        if hasattr(j, "_travas"):
            j._travas, j._guarda = instancias[0]._travas, instancias[0]._guarda


def rodar(casos: list[dict], fabrica=lambda: Jev(CACHE)) -> tuple[list[dict], dict]:
    """Um e-mail por vez pelo mesmo invólucro que o consumidor usa (`rotear_seguro`). Cada linha de execução tem a
    SUA instância do Jev (fila de instâncias): assim a medição da última chamada daquela instância é a daquele
    e-mail, e o custo por recorte sai dos tokens reais de cada um."""
    instancias = [fabrica() for _ in range(PARALELO)]
    compartilhar_travas(instancias)
    fila: queue.SimpleQueue = queue.SimpleQueue()
    for j in instancias:
        fila.put(j)

    def um(r: dict) -> dict:
        jev = fila.get()
        try:
            antes = len(jev.chamadas)
            s = R.rotear_seguro(jev, r)
            feita = len(jev.chamadas) > antes
            s["tokens"] = jev.chamadas[-1]["input_tokens"] if feita else 0
            return s
        finally:
            fila.put(jev)

    with ThreadPoolExecutor(PARALELO) as ex:
        saidas = list(ex.map(um, casos))
    chamadas = [c for j in instancias for c in j.chamadas]
    custo = {"requisicoes": len(chamadas), "do_cache": sum(c["cache"] for c in chamadas),
             "perguntas": sum(c.get("perguntas", 0) for c in chamadas), "latencia_p50_ms": 0, "latencia_p95_ms": 0,
             "input_tokens": sum(c["input_tokens"] for c in chamadas), "modelos": sorted({c["modelo"] for c in chamadas})}
    if chamadas:
        ms = sorted(c["ms"] for c in chamadas)
        custo["latencia_p50_ms"], custo["latencia_p95_ms"] = ms[len(ms) // 2], ms[min(len(ms) - 1, int(0.95 * len(ms)))]
    custo["custo_us"] = custo["input_tokens"] / 1e6 * PRECO_US_POR_MILHAO_ENTRADA
    for origem in ("longo", "vazio", "falha"):
        custo[origem] = sum(s["origem"] == origem for s in saidas)
    return saidas, custo


@contextlib.contextmanager
def _com(**troca):
    """Troca constantes de `perguntas` dentro do bloco (o que um humano faria editando o arquivo) e restaura."""
    antes = {k: getattr(P, k) for k in troca}
    try:
        for k, v in troca.items():
            setattr(P, k, v)
        yield
    finally:
        for k, v in antes.items():
            setattr(P, k, v)


def _recompor(s: dict) -> tuple[str, str | None]:
    """(ação, classe) com as constantes ATUAIS de `perguntas`, a partir dos números guardados (sem cache nem API)."""
    if s["origem"] != "jev":
        return "escala", None
    d = R.compor({"classe": s["classe"], "conf": s["conf"], "probs": s["probs"], "nouls": s["nouls"]}, s["corpo"], s["truncado"])
    return d["acao"], d["classe"]


def acao_variante(s: dict, r: dict, variante: str) -> tuple[str, str | None]:
    """(ação, classe) de cada variante sobre o MESMO e-mail; as três do Jev leem a MESMA resposta."""
    if variante == BASE:
        b = R.baseline_seguro(r)
        return b["acao"], b["classe"]
    if variante == TUDO_LLM or s["origem"] != "jev":
        return "escala", None
    if variante == FORCADO:
        return "decide", s["classe"]
    if variante == SO_CONF:
        return ("decide" if s["conf"] >= P.LIMIAR_CONF[s["classe"]] else "escala"), s["classe"]
    return s["acao"], s["classe"]


# ---------------------------------------------------------------------------------------- métricas
def contas(itens: list[tuple[dict, str, str | None]]) -> dict:
    """itens = [(registro, ação, classe)] → contagens brutas (somáveis: o bootstrap soma por grupo)."""
    c = Counter()
    for r, acao, classe in itens:
        c["n"] += 1
        c["golpes"] += r["classe"] == "golpe"
        c["principais"] += r["classe"] == "principal"
        if acao == "decide":
            c["dec"] += 1
            c["certos"] += classe == r["classe"]
            c["caro1"] += r["classe"] == "golpe" and classe in CAIXA       # golpe na caixa de entrada
            c["caro2"] += r["classe"] == "principal" and classe in FORA    # e-mail de cliente perdido
    return c


def taxas(c: Counter) -> dict:
    """Contagens → as taxas do relatório. Escalado concorda por definição (gabarito = produção)."""
    div = lambda a, b: a / b if b else float("nan")  # noqa: E731
    return {"cobertura": div(c["dec"], c["n"]), "concordancia_decididos": div(c["certos"], c["dec"]),
            "util": div(c["certos"], c["n"]), "ponta_a_ponta": div(c["certos"] + c["n"] - c["dec"], c["n"]),
            "caro1": div(c["caro1"], c["golpes"]), "caro2": div(c["caro2"], c["principais"])}


def bootstrap(itens: list[tuple[dict, str, str | None]]) -> dict:
    """IC 95% por bootstrap AGRUPADO por `grupo` (remetente): e-mails do mesmo remetente não são independentes.
    Reamostra grupos com reposição e soma as contagens. Devolve {taxa: (inferior, superior)}."""
    por_grupo: dict[str, Counter] = defaultdict(Counter)
    for item in itens:
        por_grupo[item[0]["grupo"]].update(contas([item]))
    grupos = list(por_grupo.values())
    if not grupos:
        return {}
    rng = random.Random(SEMENTE)
    amostras = defaultdict(list)
    for _ in range(N_BOOT):
        soma = Counter()
        for g in rng.choices(grupos, k=len(grupos)):
            soma.update(g)
        for k, v in taxas(soma).items():
            if v == v:  # descarta NaN (reamostra sem denominador)
                amostras[k].append(v)
    ic = {}
    for k, vals in amostras.items():
        vals.sort()
        ic[k] = (vals[int(0.025 * len(vals))], vals[min(len(vals) - 1, int(0.975 * len(vals)))])
    return ic


def _f(v: float) -> str:
    return "—" if v != v else f"{v:.3f}"


def _ic(ic: dict, k: str) -> str:
    return f"[{ic[k][0]:.3f}; {ic[k][1]:.3f}]" if k in ic else "—"


def linha_variante(itens: list[tuple[dict, str, str | None]]) -> dict:
    c = contas(itens)
    t = taxas(c)
    return {"n": c["n"], "cobertura (decide sozinho)": t["cobertura"], "concordância entre decididos": _f(t["concordancia_decididos"]),
            "decidido E concorda / n": t["util"], "escalados": c["n"] - c["dec"],
            "GOLPE NA CAIXA (golpe → principal/notificações, sozinho)": f"{c['caro1']}/{c['golpes']}",
            "CLIENTE PERDIDO (principal → spam/golpe, sozinho)": f"{c['caro2']}/{c['principais']}",
            "concordância ponta a ponta (escalado = 1)": t["ponta_a_ponta"], "_c": c, "_t": t}


COLUNAS = ["recorte", "variante", "n", "cobertura (decide sozinho)", "concordância entre decididos", "decidido E concorda / n",
           "escalados", "GOLPE NA CAIXA (golpe → principal/notificações, sozinho)",
           "CLIENTE PERDIDO (principal → spam/golpe, sozinho)", "concordância ponta a ponta (escalado = 1)"]


def veredito(linhas: dict) -> tuple[str, bool | None]:
    """Confere o critério congelado contra os números do recorte IA (gerado, não escrito à mão)."""
    if not P.CRITERIO_CONTINUAR:
        return "_(critério ainda não fixado em `perguntas.py`)_", None
    lim = P.CRITERIO_CONTINUAR["limites"]
    j, b = linhas[(REC_CRITERIO, JEV)], linhas[(REC_CRITERIO, BASE)]
    c, t = j["_c"], j["_t"]
    ok = lambda x: "✓" if x else "✗"  # noqa: E731
    conc = t["concordancia_decididos"]
    bc, bt = b["_c"], b["_t"]
    # O baseline "chega lá" se passa nos itens 1–3 com os MESMOS limites; aí só perde para o Jev se cobrir menos.
    base_seguro = ((not bc["golpes"] or bt["caro1"] <= lim["golpe_na_caixa_max"])
                   and (not bc["principais"] or bt["caro2"] <= lim["cliente_perdido_max"])
                   and bt["concordancia_decididos"] == bt["concordancia_decididos"]
                   and bt["concordancia_decididos"] >= lim["concordancia_min"])
    testes = [
        ("1 golpe na caixa (sozinho)", f"{c['caro1']}/{c['golpes']} ({_f(t['caro1'])})", f"≤ {lim['golpe_na_caixa_max']}",
         not c["golpes"] or t["caro1"] <= lim["golpe_na_caixa_max"]),
        ("2 cliente perdido (sozinho)", f"{c['caro2']}/{c['principais']} ({_f(t['caro2'])})", f"≤ {lim['cliente_perdido_max']}",
         not c["principais"] or t["caro2"] <= lim["cliente_perdido_max"]),
        ("3 concordância entre decididos", f"{c['certos']}/{c['dec']} ({_f(conc)})", f"≥ {lim['concordancia_min']}",
         conc == conc and conc >= lim["concordancia_min"]),
        ("4 cobertura", f"{c['dec']}/{c['n']} ({_f(t['cobertura'])})", f"≥ {lim['cobertura_min']}", t["cobertura"] >= lim["cobertura_min"]),
        ("5 o baseline de código não chega lá",
         f"baseline: golpe na caixa {bc['caro1']}/{bc['golpes']}, cliente perdido {bc['caro2']}/{bc['principais']}, "
         f"concordância {_f(bt['concordancia_decididos'])}, cobertura {_f(bt['cobertura'])}",
         "baseline falha em 1, 2 ou 3, ou cobre menos que o Jev", not (base_seguro and bt["cobertura"] >= t["cobertura"])),
    ]
    tab = [{"critério": n, "medido": m, "limite": l, "passa": ok(p)} for n, m, l, p in testes]
    tab.append({"critério": f"informativo: cobertura ≥ {lim['cobertura_sugerida_no_briefing']} (sugestão do briefing)",
                "medido": _f(t["cobertura"]), "limite": f"≥ {lim['cobertura_sugerida_no_briefing']}",
                "passa": ok(t["cobertura"] >= lim["cobertura_sugerida_no_briefing"]) + " (não decide)"})
    passou = all(p for *_, p in testes)
    return M.tabela(tab) + f"\n\n**Veredito calculado: {'PASSOU' if passou else 'NÃO PASSOU'}** (os 5 itens numerados).", passou


def curva(pares: list[tuple[dict, dict]], so_confianca: bool) -> list[dict]:
    """Cobertura × concordância × erro caro com o MESMO limiar em todas as classes (zero chamada nova)."""
    linhas = []
    for lim in LIMIARES_CURVA:
        troca = {"LIMIAR_CONF": {k: lim for k in P.CLASSES}}
        if so_confianca:
            troca.update(USAR_CONFLITOS=False, MIN_CORPO_CAIXA=0)
        with _com(**troca):
            c = contas([(r, *_recompor(s)) for s, r in pares])
        t = taxas(c)
        linhas.append({"limiar (todas as classes)": lim, "cobertura": t["cobertura"], "concordância entre decididos": _f(t["concordancia_decididos"]),
                       "golpe na caixa": f"{c['caro1']}/{c['golpes']}", "cliente perdido": f"{c['caro2']}/{c['principais']}",
                       "n decididos": c["dec"]})
    return linhas


def custo_llm(r: dict, modelo: dict) -> float:
    """Custo ESTIMADO (US$) de classificar UM e-mail no LLM: prompt fixo + texto do e-mail, saída curta."""
    caracteres = sum(len(r[k]) for k in ("remetente_nome", "assunto", "texto") if isinstance(r.get(k), str))
    return ((LLM_PROMPT + caracteres * TOKENS_POR_CARACTERE) * modelo["entrada"] + LLM_SAIDA * modelo["saida"]) / 1e6


def us(v: float) -> str:
    return f"{v:.4f}" if v >= 0.01 else f"{v:.6f}"


def matriz(pares: list[tuple[str, str]], colunas: list[str]) -> str:
    """pares = [(gabarito, previsto)] → tabela (linhas = produção, colunas = Jev)."""
    cont = Counter(pares)
    return M.tabela([{"produção ↓ / Jev →": g, **{p: cont[(g, p)] for p in colunas}} for g in P.CLASSES if any(a == g for a, _ in pares)])


# ---------------------------------------------------------------------------------------- relatório
def secao_conjunto(nome: str, casos: list[dict], fabrica=lambda: Jev(CACHE), excluir_states: set | None = None) -> tuple[str, dict]:
    """`excluir_states` = states do ajuste (no teste) ou os repetidos dentro do próprio conjunto (no ajuste)."""
    saidas, custo = rodar(casos, fabrica)
    if excluir_states is None:
        vistos: set = set()
        excluir_states = {r["_state"] for r in casos if r.get("_state") and (r["_state"] in vistos or vistos.add(r["_state"]))}
    todos = list(zip(saidas, casos))
    pares = [(s, r) for s, r in todos if r["classe"] != A_PARTE]          # tabelas principais e critério
    a_parte = [(s, r) for s, r in todos if r["classe"] == A_PARTE]
    por_rec = {nome_r: [(s, r) for s, r in pares if f(r)] for nome_r, f in RECORTES.items()}
    itens = {(rec, v): [(r, *acao_variante(s, r, v)) for s, r in sub] for rec, sub in por_rec.items() for v in VARIANTES}
    linhas = {k: linha_variante(v) for k, v in itens.items()}
    resumo = {"n": len(casos), "custo": custo, "linhas": linhas}

    classes = Counter(r["classe"] for r in casos)
    estratos = Counter(r["decidido_por"] for r in casos)
    truncados = sum(bool(r["sinais"].get("body_truncated")) for r in casos if isinstance(r.get("sinais"), dict))
    invalidos = sum(bool(r.get("_invalido")) for r in casos)
    out = [f"## Conjunto `{nome}` — {len(casos)} e-mails reais anonimizados, {len({r['grupo'] for r in casos})} remetentes (grupos)\n"]
    out.append("Classe em produção: " + ", ".join(f"`{k}` {classes[k]}" for k in P.CLASSES if classes[k]) + ". Quem decidiu em produção: "
               + ", ".join(f"`{k}` {v}" for k, v in sorted(estratos.items())) + f". Corpo truncado na extração: {truncados}/{len(casos)}. "
               f"Máscara de última milha na carga (nome em maiúsculas após saudação → `[NOME]`): "
               f"{sum(r.get('_mascarado', False) for r in casos)} registro(s), {sum(r.get('_trocas', 0) for r in casos)} troca(s). "
               f"Registros inválidos na carga (→ falha operacional): {invalidos}. "
               f"`{A_PARTE}`: {len(a_parte)} caso(s), fora das tabelas principais e do critério (seção própria).\n")
    if custo["falha"]:
        out.append(f"> **{custo['falha']} falha(s) operacional(is)** neste conjunto: esses e-mails saíram `escala` sem resposta do "
                   "Jev. **As métricas abaixo não são medição do Jev** — rode de novo.\n")

    # --- tabela principal
    out.append("### Roteamento por recorte — baseline × tudo no LLM × Jev, nos mesmos e-mails\n")
    out.append("**Gabarito = decisão de produção: tudo é concordância com produção, não acerto.** `cobertura` = fração que a variante "
               "decide sozinha (o resto escala ao LLM). `concordância entre decididos` = dos decididos sozinho, quantos batem com "
               "produção. `decidido E concorda / n` = automação útil. **GOLPE NA CAIXA** = golpe de produção decidido sozinho como "
               "`principal`/`notificacoes` (denominador: golpes do recorte). **CLIENTE PERDIDO** = `principal` de produção decidido "
               "sozinho como `spam`/`golpe` (denominador: principais do recorte). `ponta a ponta` conta o escalado como concordante "
               "(o LLM É o gabarito). Recortes: `só regra` = produção decidiu por regra; `só IA` = produção mandou a um LLM (o resíduo "
               "ambíguo: o caso de uso real do roteador); `todos` inclui também os decididos por `crm`. Variantes do Jev leem a MESMA "
               "resposta: `forçado` = sempre a classe mais provável; `só confiança` = limiar por classe, sem Nouls nem regra do corpo "
               "curto; `roteador` = a política de `perguntas.py`.\n")
    out.append(M.tabela([{"recorte": rec, "variante": v, **linhas[(rec, v)]} for rec in RECORTES for v in VARIANTES], COLUNAS) + "\n")

    # --- IC
    out.append(f"### IC 95% da política — bootstrap agrupado por remetente (`grupo`), {N_BOOT} reamostragens\n")
    tab = []
    for rec in RECORTES:
        ic, t = bootstrap(itens[(rec, JEV)]), linhas[(rec, JEV)]["_t"]
        tab.append({"recorte": rec, "grupos": len({r["grupo"] for r, *_ in itens[(rec, JEV)]}),
                    "cobertura": f"{_f(t['cobertura'])} {_ic(ic, 'cobertura')}",
                    "concordância entre decididos": f"{_f(t['concordancia_decididos'])} {_ic(ic, 'concordancia_decididos')}",
                    "golpe na caixa / golpes": f"{_f(t['caro1'])} {_ic(ic, 'caro1')}",
                    "cliente perdido / principais": f"{_f(t['caro2'])} {_ic(ic, 'caro2')}",
                    "ponta a ponta": f"{_f(t['ponta_a_ponta'])} {_ic(ic, 'ponta_a_ponta')}"})
    out.append(M.tabela(tab) + "\n")

    # --- por state único (campanhas repetidas): mesmas respostas, outro denominador
    out.append("### Política por state único — campanhas repetidas contadas uma vez\n")
    out.append("O mesmo texto (state idêntico depois da máscara) aparece em vários e-mails, inclusive entre ajuste e teste. "
               "`por e-mail` = as tabelas acima (cada registro conta 1). `state único` = cada state distinto conta 1 (fica o "
               "primeiro registro). `sem states do ajuste` = state único, tirando os states que também aparecem no ajuste "
               "(no `ajuste`, tira os repetidos dentro dele mesmo). Mesmas respostas do Jev, nenhuma chamada nova.\n")
    tab = []
    for rec in RECORTES:
        base = itens[(rec, JEV)]
        vistos: set = set()
        unicos = [x for x in base if x[0].get("_state") and not (x[0]["_state"] in vistos or vistos.add(x[0]["_state"]))]
        sem_aj = [x for x in unicos if x[0]["_state"] not in excluir_states]
        for rotulo, sub_itens in (("por e-mail", base), ("state único", unicos), ("sem states do ajuste", sem_aj)):
            c, t = contas(sub_itens), taxas(contas(sub_itens))
            tab.append({"recorte": rec, "denominador": rotulo, "n": c["n"], "cobertura": _f(t["cobertura"]),
                        "concordância entre decididos": f"{c['certos']}/{c['dec']} ({_f(t['concordancia_decididos'])})",
                        "golpe na caixa": f"{c['caro1']}/{c['golpes']}", "cliente perdido": f"{c['caro2']}/{c['principais']}"})
    out.append(M.tabela(tab) + "\n")

    # --- critério
    out.append(f"**Critério congelado conferido no teste, recorte `{REC_CRITERIO}`** (é este que decide)\n" if nome == "teste"
               else f"**Critério conferido no `{nome}`, recorte `{REC_CRITERIO}`** (informativo: só o `teste` decide)\n")
    texto_veredito, resumo["passou"] = veredito(linhas)
    out.append(texto_veredito + "\n")

    # --- curvas
    out.append("### Curva cobertura × concordância × erro caro por limiar (mesmas respostas, zero chamada nova)\n")
    out.append("O MESMO limiar de confiança em todas as classes. `com a política` mantém os conflitos de Noul e a regra do corpo "
               "curto; `só confiança` desliga os dois. A linha de `perguntas.py` (limiar por classe) está na tabela principal.\n")
    for rec in (REC_CRITERIO, "todos"):
        for rotulo, so_conf in (("com a política", False), ("só confiança", True)):
            out.append(f"**Recorte `{rec}` — {rotulo}**\n")
            out.append(M.tabela(curva(por_rec[rec], so_conf)) + "\n")

    # --- por classe
    out.append("### Por classe (política) — o que o Jev decide sozinho em cada classe\n")
    for rec in (REC_CRITERIO, "todos"):
        tab = []
        for cl in P.CLASSES:
            prod = [(r, a, c) for r, a, c in itens[(rec, JEV)] if r["classe"] == cl]
            prev = [(r, a, c) for r, a, c in itens[(rec, JEV)] if a == "decide" and c == cl]
            forc = [(r, a, c) for r, a, c in itens[(rec, FORCADO)] if r["classe"] == cl]
            if not prod and not prev:
                continue
            dec = [x for x in prod if x[1] == "decide"]
            tab.append({"classe": cl, "n em produção": len(prod), "decididos sozinho": len(dec),
                        "… que concordam": sum(c == cl for _, _, c in dec),
                        "concordância forçada (sem limiar)": _f(sum(c == cl for _, _, c in forc) / len(forc)) if forc else "—",
                        "Jev decidiu esta classe": len(prev),
                        "… e produção concorda (precisão)": _f(sum(r["classe"] == cl for r, _, _ in prev) / len(prev)) if prev else "—"})
        out.append(f"**Recorte `{rec}`**\n")
        out.append(M.tabela(tab) + "\n")

    # --- matrizes
    out.append("### Matrizes de confusão (linhas = produção, colunas = Jev)\n")
    for rec in (REC_CRITERIO, "todos"):
        dec = [(r["classe"], c) for r, a, c in itens[(rec, JEV)] if a == "decide"]
        forc = [(r["classe"], c or "sem resposta") for r, a, c in itens[(rec, FORCADO)]]
        out.append(f"**Recorte `{rec}` — decididos sozinho pela política** ({len(dec)})\n")
        out.append((matriz(dec, P.CLASSES) if dec else "_(nenhum)_") + "\n")
        out.append(f"**Recorte `{rec}` — leitura forçada, todos os e-mails** ({len(forc)})\n")
        out.append(matriz(forc, P.CLASSES + (["sem resposta"] if any(p == "sem resposta" for _, p in forc) else [])) + "\n")

    # --- Nouls
    com_jev = [(s, r) for s, r in pares if s["origem"] == "jev"]
    out.append(f"### Nouls por classe de produção — média (≥ {P.NOUL_SIM} / ≤ {P.NOUL_NAO}), {len(com_jev)} e-mails com resposta\n")
    tab = []
    for q in P.NOULS:
        linha = {"noul": q}
        for cl in P.CLASSES:
            v = [s["nouls"][q] for s, r in com_jev if r["classe"] == cl]
            if v:
                linha[f"{cl} (n={len(v)})"] = f"{sum(v) / len(v):.2f} ({sum(x >= P.NOUL_SIM for x in v)}/{sum(x <= P.NOUL_NAO for x in v)})"
        tab.append(linha)
    out.append(M.tabela(tab) + "\n")
    out.append("**O que cada trava fez** (e-mails com confiança ≥ limiar da classe que a política mandou escalar mesmo assim): "
               "`erros barrados` = a classe do Jev discordava de produção; `acertos barrados` = concordava (cobertura perdida). "
               "`corpo truncado (código)` é a regra posta depois da rodada 1 (`P.CLASSES_CARAS`).\n")
    travas: dict[str, Counter] = defaultdict(Counter)
    for s, r in com_jev:
        if s["acao"] == "escala" and s["conf"] >= P.LIMIAR_CONF[s["classe"]]:
            nomes = ([f"{s['trava']} (código)"] if s["trava"] in ("corpo curto", "truncado")
                     else [f"`{s['classe']}` × `{c.split(' ')[0]}`" for c in s["conflitos"]])
            for n in nomes:
                travas[n]["erros" if s["classe"] != r["classe"] else "acertos"] += 1
                travas[n]["caro"] += (r["classe"] == "golpe" and s["classe"] in CAIXA) or (r["classe"] == "principal" and s["classe"] in FORA)
    out.append((M.tabela([{"trava": k, "erros barrados": v["erros"], "… dos quais erro caro": v["caro"], "acertos barrados": v["acertos"]}
                          for k, v in sorted(travas.items())]) if travas else "_(nenhuma trava disparou acima do limiar)_") + "\n")

    # --- motivos de escalada
    def motivo(s: dict) -> str:
        if s["origem"] != "jev":
            return {"longo": "corpo acima do teto (sem chamada)", "vazio": "corpo vazio (sem chamada)"}.get(s["origem"], "falha operacional")
        if s["conf"] < P.LIMIAR_CONF[s["classe"]]:
            return f"confiança abaixo do limiar (`{s['classe']}` < {P.LIMIAR_CONF[s['classe']]})"
        return {"corpo curto": "corpo curto para decidir classe de caixa de entrada",
                "truncado": f"corpo truncado na extração (`{s['classe']}` é classe cara)"}.get(s["trava"], f"conflito de Noul com `{s['classe']}`")
    out.append("### Por que escalou (política, todos os recortes)\n")
    esc = Counter(motivo(s) for s, r in pares if s["acao"] == "escala")
    out.append(M.tabela([{"motivo": k, "e-mails": v} for k, v in esc.most_common()]) + "\n")
    # --- regra do corpo truncado (posta depois da rodada 1): quantos casos ela toca, e com que efeito
    trunc = [(s, r) for s, r in pares if s["origem"] == "jev" and s["truncado"]]
    barrados = [(s, r) for s, r in trunc if s["trava"] == "truncado"]
    out.append(f"**Regra do corpo truncado** (código, posta depois da rodada 1): {len(trunc)} e-mail(s) com resposta do Jev e corpo "
               f"truncado; {len(barrados)} barrado(s) por ela (confiança ≥ limiar, classe cara, sem corpo curto antes): "
               f"{sum(s['classe'] == r['classe'] for s, r in barrados)} concordavam com produção, "
               f"{sum(s['classe'] != r['classe'] for s, r in barrados)} discordavam, dos quais "
               f"{sum((r['classe'] == 'golpe' and s['classe'] in CAIXA) or (r['classe'] == 'principal' and s['classe'] in FORA) for s, r in barrados)} erro(s) caro(s).\n")

    # --- redes_sociais
    out.append(f"### `{A_PARTE}` à parte ({len(a_parte)} caso(s); nenhum no ajuste: fora do critério)\n")
    if a_parte:
        out.append(M.tabela([{"id": r["id"], "decidido_por": r["decidido_por"], "Jev leu": s["classe"] or "—",
                              "confiança": _f(s["conf"]) if s["conf"] is not None else "—", "ação": s["acao"],
                              "concorda": "✓" if s["classe"] == A_PARTE else "✗"} for s, r in a_parte]) + "\n")
    else:
        out.append("_(nenhum neste conjunto)_\n")

    # --- custo
    out.append("### Custo e latência — Jev MEDIDO; LLM ESTIMADO (premissas no cabeçalho)\n")
    req = max(custo["requisicoes"], 1)
    out.append(M.tabela([{"e-mails": len(casos), "requisições": custo["requisicoes"], "novas (não cache)": custo["requisicoes"] - custo["do_cache"],
                          "sem chamada (longo/vazio)": custo["longo"] + custo["vazio"], "falhas operacionais (→ escala)": custo["falha"],
                          "perguntas": custo["perguntas"], "p50_ms": custo["latencia_p50_ms"], "p95_ms": custo["latencia_p95_ms"],
                          "tokens_por_e-mail": round(custo["input_tokens"] / req), "US$_total": f"{custo['custo_us']:.6f}",
                          "US$_por_1000_e-mails": f"{1000 * custo['custo_us'] / max(len(casos), 1):.4f}",
                          "modelo": ", ".join(custo["modelos"])}]) + "\n")
    tab = []
    for rec in (REC_CRITERIO, "todos"):
        sub = por_rec[rec]
        if not sub:
            continue
        jev_us = sum(s["tokens"] for s, _ in sub) / 1e6 * PRECO_US_POR_MILHAO_ENTRADA
        k = 1000 / len(sub)
        for modelo in (LLM_BARATO, LLM_RACIOCINIO):
            tudo = sum(custo_llm(r, modelo) for _, r in sub)
            escalado = sum(custo_llm(r, modelo) for s, r in sub if s["acao"] == "escala")
            tab.append({"recorte": rec, "LLM (premissa)": modelo["nome"], "n": len(sub), "escalados": sum(s["acao"] == "escala" for s, _ in sub),
                        "US$/1000: tudo no LLM": us(tudo * k), "US$/1000: roteado (Jev + LLM nos escalados)": us((jev_us + escalado) * k),
                        "… só a parte Jev (medida)": us(jev_us * k), "economia": f"{1 - (jev_us + escalado) / tudo:.1%}" if tudo else "—"})
    out.append(M.tabela(tab) + "\n")
    out.append("No recorte `só regra` a produção não gasta LLM (a regra decide): o custo de `todos` é hipotético — vale o recorte "
               f"`{REC_CRITERIO}`, que é o que hoje vai ao LLM.\n")

    # --- erros
    erros = [(s, r) for s, r in pares if s["acao"] == "decide" and s["classe"] != r["classe"]]
    out.append(f"### Decididos sozinho que discordam de produção — um a um ({len(erros)}; só IDs e números)\n")
    cat = Counter(f"{r['classe']} → {s['classe']}" for s, r in erros)
    out.append("Por categoria: " + ("; ".join(f"`{k}` {v}" for k, v in cat.most_common()) if cat else "nenhum") + ".\n")
    if erros:
        out.append(M.tabela([{"id": r["id"], "decidido_por": r["decidido_por"], "produção": r["classe"],
                              "Jev": s["classe"], "confiança": f"{s['conf']:.2f}",
                              "caro": "GOLPE NA CAIXA" if r["classe"] == "golpe" and s["classe"] in CAIXA
                              else "CLIENTE PERDIDO" if r["classe"] == "principal" and s["classe"] in FORA else "",
                              **{q: f"{s['nouls'][q]:.2f}" for q in P.NOULS},
                              "dkim_aligned": r["sinais"]["dkim_aligned"], "list_unsubscribe": r["sinais"]["list_unsubscribe"],
                              "corpo (caracteres)": s["corpo"]} for s, r in erros]) + "\n")
    return "\n".join(out), resumo


def comparacao(resumos: dict) -> str:
    out = ["## Lado a lado\n", "Gabarito = decisão de produção (concordância, não acerto); escalado conta como concordante.\n"]
    out.append(M.tabela([{"conjunto": n, "recorte": rec, "variante": v, **r["linhas"][(rec, v)]}
                         for n, r in resumos.items() for rec in RECORTES for v in (BASE, FORCADO, JEV)], ["conjunto", *COLUNAS]) + "\n")
    out.append(M.tabela([{"conjunto": n, "e-mails": r["n"], "requisições": r["custo"]["requisicoes"],
                          "falhas": r["custo"]["falha"], "p50_ms": r["custo"]["latencia_p50_ms"], "p95_ms": r["custo"]["latencia_p95_ms"],
                          "tokens_por_e-mail": round(r["custo"]["input_tokens"] / max(r["custo"]["requisicoes"], 1)),
                          "US$_por_1000_e-mails (Jev)": f"{1000 * r['custo']['custo_us'] / max(r['n'], 1):.4f}",
                          "modelo": ", ".join(r["custo"]["modelos"]),
                          "critério": {True: "PASSOU", False: "NÃO PASSOU", None: "—"}[r["passou"]] + ("" if n == "teste" else " (informativo)")}
                         for n, r in resumos.items()]) + "\n")
    return "\n".join(out)


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{Path(a).name}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}): {h}"


def _congelar() -> dict:
    """Grava o manifesto pela infra comum e anota, só como registro, o hash da infra comum que rodou."""
    if not P.CRITERIO_CONTINUAR:
        sys.exit("congelar recusado: `perguntas.CRITERIO_CONTINUAR` está vazio (o critério vem ANTES do teste)")
    m = CG.congelar(AQUI, CONGELADOS, P.CRITERIO_CONTINUAR)
    if "informativo_comum" not in m:
        m["informativo_comum"] = CG.hashes(AQUI, INFORMATIVOS)
    (AQUI / CG.MANIFESTO).write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return m


def _criterio_md() -> str:
    return "; ".join(f"**{k}**: {v}" for k, v in P.CRITERIO_CONTINUAR.items() if k != "limites") or "(ainda não fixado)"


def cabecalho(linha: str) -> str:
    return (f"# Resultados — roteador-email\n\nGerado por `run.py` em {datetime.date.today().isoformat()} (modo "
            f"`{os.environ.get('JEV_MODO', 'auto')}`; modelo e amostra em cada seção). Perguntas, limiares e política: `perguntas.py`; "
            f"validação, composição e baseline: `roteador.py`.\n\n"
            "> **Dado real, relatório sem texto.** E-mails de produção já classificados pelo F11, anonimizados; o texto e o cache do "
            "Jev ficam fora do Git. Aqui só há agregados, IDs `EM-xxxx`, classes e números.\n>\n"
            "> **Gabarito = a decisão do sistema em produção** (regra, Claude, Codex, API ou CRM). Toda taxa é CONCORDÂNCIA com "
            "produção, não acerto contra verdade independente. Escalar = mandar ao LLM de produção, que concorda por definição.\n\n"
            f"Limiares em vigor: confiança por classe {P.LIMIAR_CONF}; Noul sim ≥ {P.NOUL_SIM}, não ≤ {P.NOUL_NAO}; corpo < "
            f"{P.MIN_CORPO_CAIXA} caracteres não decide classe de caixa de entrada; teto do corpo {P.TETO_CORPO}.\n\n"
            f"Custo: Jev MEDIDO (tokens reais × US$ {PRECO_US_POR_MILHAO_ENTRADA}/M de entrada). LLM ESTIMADO, nada é chamado — "
            f"`{LLM_BARATO['nome']}` US$ {LLM_BARATO['entrada']}/{LLM_BARATO['saida']} e `{LLM_RACIOCINIO['nome']}` US$ "
            f"{LLM_RACIOCINIO['entrada']}/{LLM_RACIOCINIO['saida']} por 1M entrada/saída (premissas de `../roteador-jev-llm/run.py`); "
            f"por e-mail: {LLM_PROMPT} tokens de instruções + caracteres × {TOKENS_POR_CARACTERE} → {LLM_SAIDA} de saída.\n\n"
            f"Critério de continuar/descartar (fixado antes do teste): {_criterio_md()}\n\n{linha}\n")


def main() -> None:
    args = sys.argv[1:] or ["ajuste", "teste"]
    congelar = args == ["congelar"]
    conjuntos = ["ajuste"] if congelar else args
    if any(c not in ("ajuste", "teste") for c in conjuntos):
        sys.exit("uso: python run.py [ajuste | congelar | ajuste teste]")
    if not DADOS.exists():
        sys.exit(SEM_DADOS)
    if "teste" in conjuntos:
        # O teste só roda com perguntas, política, dados E critério congelados: o manifesto gravado ANTES tem de bater.
        try:
            manifesto = CG.conferir(AQUI, CONGELADOS)
        except RuntimeError as e:
            sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
        if manifesto["criterio_de_aceite"] != P.CRITERIO_CONTINUAR:
            sys.exit("teste recusado: o critério de continuar mudou desde o congelamento (rode `run.py congelar`)")
        linha = _linha_manifesto(manifesto)
    elif congelar:
        linha = _linha_manifesto(_congelar())
    else:
        h = CG.hashes(AQUI, CONGELADOS)
        linha = "Versão em afinação (NÃO congelada): " + " · ".join(f"`{Path(a).name}` sha256 {v[:16]}…" for a, v in h.items())

    partes, resumos = [], {}
    states_ajuste = {r["_state"] for r in carregar("ajuste") if r.get("_state")} if "teste" in conjuntos else set()
    for nome in conjuntos:
        texto, resumos[nome] = secao_conjunto(nome, carregar(nome), excluir_states=states_ajuste if nome == "teste" else None)
        partes.append(texto)
    texto = cabecalho(linha) + "\n" + comparacao(resumos) + "\n" + "\n".join(partes)
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({', '.join(conjuntos)})")
    falhas = {n: r["custo"]["falha"] for n, r in resumos.items() if r["custo"]["falha"]}
    if falhas:
        print(f"ATENÇÃO: falhas operacionais {falhas} — esses e-mails saíram `escala` sem resposta do Jev; "
              "o relatório marca o conjunto e não vale como medição", file=sys.stderr)
    if "teste" in conjuntos and not RODADA1.exists() and not falhas:
        # A primeira execução COMPLETA com o teste É a rodada cega: fica preservada e nunca é reescrita por este
        # script. Execução com falha operacional não é medição: não vira rodada 1; rodar de novo só refaz as
        # chamadas que faltaram (o resto vem do cache).
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada cega preservada)")


if __name__ == "__main__":
    main()
