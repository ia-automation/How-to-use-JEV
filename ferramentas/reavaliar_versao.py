"""Arnês de reavaliação por versão do modelo — roda o teste congelado de cada exemplo AO VIVO contra um modelo
dado e compara com o cache da versão congelada. Não altera nada do exemplo.

Uso (com o `.venv` da raiz):
  python -X utf8 ferramentas/reavaliar_versao.py --modelo jev-1.14.0 [--exemplos a,b,c] [--so-estimar] [--max-custo 0.30]
                                                 [--acumular] [--so-relatorio]

Por que existe (briefing AC, 2026-10-01): os limiares dos exemplos valem para `jev-1.13.0`; o alias `jev-latest` muda
sozinho e nada avisa. O arnês mede o que uma versão nova faz com os MESMOS testes congelados, sem recalibrar nada
(recalibrar é decisão humana, registrada). Rodado contra o próprio `jev-1.13.0`, mede a variação entre rodadas.

Como funciona:
  1. Para cada exemplo com `run.py` + `congelamento.json` (menos `roteador-email`: dado real, só com o dono), roda
     `run.py teste` duas vezes em subprocesso: REFERÊNCIA em `JEV_MODO=gravado` sobre uma CÓPIA do `cache/` (o
     original nunca é lido pelo cliente, que em replay move registros inválidos; revisão do Codex 2026-10-01, achado
     1) — zero chamada, é também a estimativa de custo — e RODADA NOVA em `JEV_MODO=ao_vivo` com `JEV_MODELO=<modelo>`
     e `JEV_PASTA_CACHE=cache-<modelo>` (o cache novo fica AO LADO do original; `_comum/jevcache.py` lê as variáveis
     e recusa modelo do ambiente sem pasta própria).
  2. A referência só vale se estiver COMPLETA (achado 2): `n` do resumo = casos de `dados/teste.json`, nenhum pedido
     sem resposta no cache (falha absorvida por `*_seguro` é vista aqui, antes do exemplo engolir), nenhuma
     invalidação. Referência incompleta barra a estimativa e a rodada paga daquele exemplo.
  3. O subprocesso (`--_driver`) importa o `run.py` do exemplo SEM alterá-lo (está congelado por hash no manifesto:
     editar o run.py faria o próprio exemplo recusar o teste): redireciona os `.md` que ele grava para
     `.local/reavaliacao/`, intercepta `Jev.perguntar` e `Jev.invalidar` para registrar cada pedido (chave = hash de
     state+perguntas, SEM o modelo, para parear rodadas de modelos diferentes) e captura o `resumo` que
     `secao_conjunto` devolve.
  4. Compara, com o formato de cada consumidor declarado em `CONSUMIDORES` (achados 5, 8 e 9): métricas
     (`resumo["variantes"]` ou `resumo["desenhos"]`; outra estrutura = aviso), veredito do critério (tabela "Critério
     congelado conferido no teste"), linhas da tabela "Caso a caso" por identidade composta (id + k/q/variante…) que
     mudaram e as cujas colunas de RESULTADO trocaram, e, pedido a pedido, Nouls/Choices/Scores validados por
     `congelamento.noul/choice` (inválidos contados à parte) que trocaram de lado com a distância ao limiar — o limiar é
     o que o consumidor usa para aquele ID (mapa explícito; sem mapa = "limiar desconhecido", nunca 0,5 por padrão).
  5. Confere, por hash, que a pasta do exemplo (fora de `cache-<modelo>/` e `__pycache__/`) ficou idêntica.
Saída: `conhecimento/evidencias/reavaliacao-<modelo>-<data>.md` + linha em `conhecimento/INDICE.md`; registros brutos
em `.local/reavaliacao/<modelo>/`. `--so-relatorio` recompara e regera a nota a partir desses registros (zero chamada).
Exemplo que falha (sem manifesto, `run.py` recusa, exceção, 429) é registrado e os outros seguem; 3 erros 429 seguidos
param a execução. Chave da API só pelo `jevcache.py`; nunca é lida nem impressa aqui.
Bateria sem chave: `ferramentas/testa_reavaliar_versao.py`.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
EXEMPLOS = RAIZ / "exemplos"
LOCAL = RAIZ / ".local" / "reavaliacao"
EVIDENCIAS = RAIZ / "conhecimento" / "evidencias"
INDICE = RAIZ / "conhecimento" / "INDICE.md"
sys.path.insert(0, str(EXEMPLOS / "_comum"))
import congelamento as CG  # noqa: E402
import metricas as M  # noqa: E402
from jevcache import MODELO as MODELO_CONGELADO, PRECO_US_POR_MILHAO_ENTRADA as PRECO  # noqa: E402

PULAR_SEMPRE = {"roteador-email": "dado real do F11, cache fora do repositório: só com ordem do dono",
                "jev-x-llm": "compara um LLM com o cache do Jev; não é teste do Jev"}
# Métricas que variam sem dizer nada do modelo (latência, custo, contagem de cache): fora do diff.
IGNORAR_METRICA = re.compile(r"ms|custo|US\$|token|req|cache|modelo|novas", re.I)
MARCA = re.compile(r"[✓✗≈?][A-Za-z∅]*")  # a marca de desfecho dentro de uma célula ("fin ✓", "grupo/folha ✗f", "∅ ✓∅" → "✓∅")
MAX_LINHAS_TROCAS = 60


# ----------------------------------------------------------------------------------------------------------------
# Formato de cada consumidor (achados 5, 8 e 9 da revisão do Codex, 2026-10-01): o arnês não adivinha.
#   faixa:      [(regex do ID da pergunta, função(perguntas, match) → (nao, sim))] — o limiar que o CÓDIGO do exemplo
#               aplica àquele ID. Corte único = (c, c). ID sem regra → "limiar desconhecido" (não vira troca).
#   identidade: colunas que, junto com `id`, identificam a linha nas tabelas por `id` (quando existem no cabeçalho).
#   resultado:  colunas cuja mudança é "trocou de lado" no caso; `marca` = "celula" (compara a célula inteira: `ok`,
#               `marca`, `acerto`) ou "sufixo" (compara só o símbolo de desfecho dentro da célula da variante).
# ----------------------------------------------------------------------------------------------------------------
def _f(chave):
    return lambda P, m: P.FAIXA[chave]


def _fg(P, m):  # FAIXA pela parte capturada do ID (compromisso `k1_accepted` → FAIXA["accepted"])
    return P.FAIXA[m.group(1)]


def _corte(nome):  # corte único por constante do `perguntas.py`
    return lambda P, m: (getattr(P, nome), getattr(P, nome))


def _corte_limiar(chave):
    return lambda P, m: (P.LIMIAR[chave], P.LIMIAR[chave])


CONSUMIDORES: dict[str, dict] = {
    "auditor-de-evidencia": {"faixa": [(r"^contradicts_\d+$", _f("contradicts")), (r"^supports_\d+$", _corte("APOIO_MIN")),
                                       (r"^established$", _f("established")), (r"^(object|state|place|scope)_shown$", _f("parts"))],
                             "identidade": [], "resultado": ["ok"], "marca": "celula"},
    "compactacao-de-contexto": {"faixa": [(r"^needed_m\d+$", lambda P, m: P.FAIXA_NEEDED), (r"^superseded_m\d+$", _corte("SUPERSEDED_SIM")),
                                          (r"^(rule|status|literal)_m\d+$", _corte("GUARDA_SIM"))],
                                "identidade": [], "resultado": ["acerto"], "marca": "celula"},
    "compromisso-real": {"faixa": [(r"^k\d+_(accepted|undone|quoted|open_request)$", _fg)], "identidade": ["k"], "resultado": ["ok"], "marca": "celula"},
    "conferencia-de-promessas": {"faixa": [(r"^top_\d+$", _corte("TOPICO_MAX"))], "identidade": ["af"], "resultado": ["marca"], "marca": "celula"},
    "guarda-tool-call": {"faixa": [(r"^(.+)$", _fg)], "identidade": [], "resultado": ["ok"], "marca": "celula"},
    "imovel-duplicado": {"faixa": [(r"^(.+)$", _fg)], "identidade": ["variante"], "resultado": ["ok"], "marca": "celula"},
    "imovel-errado": {"faixa": [(r"^(draft_uses_other|draft_commits_to_one)$", _fg), (r"^unambiguous_reference$", lambda P, m: (P.UNAMBIGUOUS_MIN, 1.0))],
                      "identidade": [], "resultado": ["ok"], "marca": "celula"},
    "injecao-em-ferramenta": {"faixa": [(r"^(directed_at_agent|asks_action_outside_task|quotes_or_discusses|user_endorsed_source)$", _fg),
                                        (r"^relevant_to_task$", _corte("RELEVANTE_MIN"))],
                              "identidade": [], "resultado": ["ok"], "marca": "celula"},
    "juiz-de-eval": {"faixa": [(r"^(.+)$", lambda P, m: P.FAIXA)], "identidade": ["crit"], "resultado": ["marca"], "marca": "celula"},
    "lint-semantico-de-diff": {"faixa": [(r"^r\d+_viola$", lambda P, m: P.FAIXA), (r"^r\d+_aplica$", _corte("LIMIAR_APLICA"))],
                               "identidade": ["regra"], "resultado": ["marca"], "marca": "celula"},
    # Guardas com `≤`/`<` no consumidor: no valor EXATO do corte o código decide o outro lado do que `faixa_noul` diz.
    "motivo-de-perda": {"faixa": [(r"^reason_stated$", _corte_limiar("sem_motivo")), (r"^(blames_agency|closed_elsewhere)$", _corte_limiar("guarda"))],
                        "identidade": [], "resultado": ["c"], "marca": "sufixo"},
    "opt-out-lgpd": {"faixa": [(r"^(.+)$", _fg)], "identidade": [], "resultado": ["ok"], "marca": "celula"},
    "proxima-pergunta": {"faixa": [(r"^answered\.", _corte_limiar("respondida")), (r"^withdrawn\.", _corte_limiar("retirado")),
                                   (r"^rental$", _corte_limiar("aluguel")), (r"^investor_not_living$", _corte_limiar("investidor")),
                                   (r"^specific_property$", _corte_limiar("imovel_especifico")), (r"^positive_reaction$", _corte_limiar("reacao_positiva"))],
                         "identidade": [], "resultado": ["híb"], "marca": "sufixo"},
    "repeticao-ou-revisao": {"faixa": [(r"^(.+)$", _fg)], "identidade": ["variante"], "resultado": ["ok"], "marca": "celula"},
    "requisito-mudou": {"faixa": [(r"^q\d+_(changed|dropped|open)$", _fg)], "identidade": ["q"], "resultado": ["ok"], "marca": "celula"},
    # `gate.*` entram só pela média das três portas: não têm limiar por ID → ficam "desconhecido" de propósito.
    "selecao-de-skill": {"faixa": [(r"^fits\.", _corte_limiar("fits"))], "identidade": [], "resultado": ["b"], "marca": "sufixo"},
    "triagem-de-alerta": {"faixa": [(r"^(.+)$", _fg)], "identidade": [], "resultado": ["ok"], "marca": "celula"},
}
PADRAO_CONSUMIDOR = {"faixa": [], "identidade": [], "resultado": ["ok", "marca", "acerto", "concorda"], "marca": "celula"}


def consumidor(exemplo: str) -> dict:
    return CONSUMIDORES.get(exemplo, PADRAO_CONSUMIDOR)


# ----------------------------------------------------------------------------------------------------------------
# Inventário e integridade
# ----------------------------------------------------------------------------------------------------------------
def listar_exemplos(raiz: Path, pedidos: list[str] | None = None) -> tuple[list[str], dict[str, str]]:
    """Exemplos elegíveis (run.py + manifesto) e os pulados com o motivo. `roteador-email` nunca entra."""
    elegiveis, pulados = [], {}
    nomes = pedidos or sorted(p.name for p in raiz.iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))
    for nome in nomes:
        pasta = raiz / nome
        if nome in PULAR_SEMPRE:
            pulados[nome] = PULAR_SEMPRE[nome]
        elif not pasta.is_dir():
            pulados[nome] = "pasta não existe"
        elif not (pasta / "run.py").exists():
            pulados[nome] = "sem run.py (exemplo em TypeScript ou sem arnês em Python)"
        elif not (pasta / "congelamento.json").exists():
            pulados[nome] = "sem congelamento.json (teste não congelado)"
        else:
            elegiveis.append(nome)
    return elegiveis, pulados


def hash_pasta(pasta: Path, ignorar: tuple[str, ...] = ()) -> str:
    """sha256 de (caminho relativo + conteúdo) de todos os arquivos, fora dos prefixos ignorados e de __pycache__."""
    h = hashlib.sha256()
    for p in sorted(pasta.rglob("*")):
        rel = p.relative_to(pasta).as_posix()
        if p.is_dir() or "__pycache__" in rel or any(rel == i or rel.startswith(i + "/") for i in ignorar):
            continue
        h.update(rel.encode("utf-8"))
        h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def casos_esperados(pasta: Path) -> int | None:
    """Quantos casos o teste congelado tem (`dados/teste.json`); None se o arquivo não segue o formato comum."""
    try:
        return len(json.loads((pasta / "dados" / "teste.json").read_text(encoding="utf-8"))["casos"])
    except Exception:
        return None


def referencia_completa(registro: dict, n_esperado: int | None) -> list[str]:
    """Motivos pelos quais a referência (gravado) NÃO vale como base: lista vazia = completa. Falha absorvida pelo
    exemplo (`*_seguro` devolve `revisar`) aparece aqui porque o interceptor vê a exceção antes do exemplo."""
    motivos = []
    if registro.get("excecao"):
        motivos.append(f"exceção: {registro['excecao']}")
    if registro.get("recusado"):
        motivos.append(f"recusado: {registro['recusado']}")
    if registro.get("erros"):
        motivos.append(f"{len(registro['erros'])} pedido(s) sem resposta no cache (falha absorvida pelo exemplo)")
    if registro.get("invalidacoes"):
        motivos.append(f"{registro['invalidacoes']} invalidação(ões) de resposta durante o replay")
    if not registro.get("pedidos"):
        motivos.append("nenhum pedido registrado")
    n = (registro.get("resumo") or {}).get("n")
    if n_esperado is None:
        motivos.append("dados/teste.json sem a lista `casos`: n esperado desconhecido")
    elif n != n_esperado:
        motivos.append(f"resumo com n={n!r}, teste.json com {n_esperado} casos")
    return motivos


# ----------------------------------------------------------------------------------------------------------------
# Driver: roda dentro do subprocesso, um por (exemplo, modo)
# ----------------------------------------------------------------------------------------------------------------
def _json_seguro(obj):
    """Torna serializável o que o `resumo` dos exemplos carrega (chaves não-string, tuplas, NaN, objetos)."""
    if isinstance(obj, dict):
        return {str(k): _json_seguro(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_json_seguro(v) for v in obj]
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def _opcoes(questao) -> list[str] | None:
    """Opções de uma Choice como o exemplo as declara (`criteria` dict → chaves; lista → itens)."""
    c = questao.get("criteria") if isinstance(questao, dict) else None
    if isinstance(c, dict):
        return [str(k) for k in c]
    if isinstance(c, list) and all(isinstance(x, str) for x in c):
        return list(c)
    return None


def _faixas_resolvidas(exemplo: str, P, ids: list[str]) -> dict[str, list[float] | None]:
    """Para cada ID de pergunta visto, (nao, sim) pelo mapa do consumidor; None = limiar desconhecido."""
    regras = [(re.compile(rx), fn) for rx, fn in consumidor(exemplo)["faixa"]]
    saida = {}
    for q in ids:
        saida[q] = None
        for rx, fn in regras:
            m = rx.match(q)
            if m:
                try:
                    nao, sim = fn(P, m)
                    saida[q] = [float(nao), float(sim)]
                except Exception:
                    saida[q] = None
                break
    return saida


def _driver(pasta: Path, saida_json: Path) -> None:
    """Importa o run.py do exemplo sem alterá-lo, roda `teste` e grava o registro em `saida_json`."""
    pasta = pasta.resolve()
    saida_dir = saida_json.parent
    registro: dict = {"exemplo": pasta.name, "modo": os.environ.get("JEV_MODO"), "modelo_pedido": os.environ.get("JEV_MODELO"),
                      "pasta_cache": os.environ.get("JEV_PASTA_CACHE"), "pedidos": {}, "erros": [], "invalidacoes": 0, "max_429_seguidos": 0}
    os.chdir(pasta)
    sys.path.insert(0, str(pasta))
    try:
        import run  # noqa: F401 — o run.py do exemplo (insere `_comum` no sys.path ao importar)
        import jevcache

        # 1. Os `.md` que o run.py grava (resultados.md, resultados-rodada1.md…) vão para a pasta de saída.
        for nome, val in list(vars(run).items()):
            if isinstance(val, Path) and val.suffix == ".md" and val.parent == pasta:
                setattr(run, nome, saida_dir / val.name)

        # 2. Intercepta cada pedido ao Jev (a classe é a mesma que o run.py usa) e cada invalidação.
        trava = threading.Lock()
        original, invalidar_original = jevcache.Jev.perguntar, jevcache.Jev.invalidar
        seguidos = {"n": 0}

        def perguntar(self, state, questions):
            chave = hashlib.sha256(json.dumps({"s": state, "q": questions}, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:24]
            inicio = time.perf_counter()
            try:
                resposta = original(self, state, questions)
            except Exception as e:  # o exemplo trata a falha (revisar/falha operacional); aqui só se registra
                with trava:
                    texto = f"{type(e).__name__}: {str(e)[:200]}"
                    registro["erros"].append({"pedido": chave[:10], "erro": texto})
                    seguidos["n"] = seguidos["n"] + 1 if "429" in texto else 0
                    registro["max_429_seguidos"] = max(registro["max_429_seguidos"], seguidos["n"])
                raise
            with trava:
                seguidos["n"] = 0
                registro["pedidos"][chave] = {
                    "tipos": {q: (v.get("type") if isinstance(v, dict) else None) for q, v in questions.items()},
                    "opcoes": {q: _opcoes(v) for q, v in questions.items() if isinstance(v, dict) and v.get("type") == "choice"},
                    "answers": resposta.get("answers"), "modelo": resposta.get("model"),
                    "tokens": (resposta.get("usage") or {}).get("input_tokens", 0),
                    "ms": round((time.perf_counter() - inicio) * 1000), "repetido": chave in registro["pedidos"]}
            return resposta

        def invalidar(self, state, questions):
            with trava:
                registro["invalidacoes"] += 1
            return invalidar_original(self, state, questions)

        jevcache.Jev.perguntar, jevcache.Jev.invalidar = perguntar, invalidar

        # 3. Captura o resumo estruturado que `secao_conjunto` devolve (o run.py só o usa para o markdown).
        capturas = {}
        secao_original = run.secao_conjunto

        def secao_conjunto(nome, *a, **k):
            r = secao_original(nome, *a, **k)
            capturas[nome] = r[1]
            return r

        run.secao_conjunto = secao_conjunto

        sys.argv = ["run.py", "teste"]
        try:
            run.main()
        except SystemExit as e:  # `teste recusado: …` (manifesto não bate) sai por aqui
            registro["recusado"] = str(e)
        registro["resumo"] = _json_seguro(capturas.get("teste"))
        ids = sorted({q for p in registro["pedidos"].values() for q in (p.get("answers") or {})})
        try:
            import perguntas
            registro["faixas"] = _faixas_resolvidas(pasta.name, perguntas, ids)
        except Exception as e:  # exemplo sem perguntas.py importável: todo limiar fica desconhecido
            registro["faixas"] = {q: None for q in ids}
            registro["aviso_faixa"] = f"{type(e).__name__}: {str(e)[:200]}"
        md = saida_dir / "resultados.md"
        registro["markdown"] = md.read_text(encoding="utf-8") if md.exists() else ""
    except Exception as e:
        registro["excecao"] = f"{type(e).__name__}: {str(e)[:500]}"
    registro["tokens"] = sum(p["tokens"] for p in registro["pedidos"].values())
    saida_json.write_text(json.dumps(registro, ensure_ascii=False), encoding="utf-8", newline="\n")


def executar_driver(pasta: Path, modo: str, modelo: str | None, pasta_cache: str | None, saida_dir: Path,
                    python: str = sys.executable, timeout: int = 3600) -> dict:
    """Roda `_driver` num subprocesso com o ambiente do modo pedido e devolve o registro gravado. Em `gravado`, o
    cliente lê uma CÓPIA do `cache/` (achado 1): o original não é aberto para escrita em nenhuma hipótese."""
    saida_dir.mkdir(parents=True, exist_ok=True)
    for velho in saida_dir.glob("*"):
        if velho.is_file():
            velho.unlink()
    saida_json = saida_dir / "driver.json"
    env = {k: v for k, v in os.environ.items() if k not in ("JEV_MODELO", "JEV_PASTA_CACHE")}
    env.update({"JEV_MODO": modo, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    if modo == "gravado" and not pasta_cache:
        copia = saida_dir / "cache-referencia"
        shutil.rmtree(copia, ignore_errors=True)
        if (pasta / "cache").is_dir():
            shutil.copytree(pasta / "cache", copia)
        else:
            copia.mkdir()
        pasta_cache = str(copia)
    if modelo:
        env["JEV_MODELO"] = modelo
    if pasta_cache:
        env["JEV_PASTA_CACHE"] = pasta_cache
    proc = subprocess.run([python, "-X", "utf8", str(Path(__file__).resolve()), "--_driver", str(pasta), "--_saida", str(saida_json)],
                          env=env, cwd=str(pasta), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if not saida_json.exists():
        raise RuntimeError(f"driver não produziu saída (código {proc.returncode}): {(proc.stderr or '')[-600:]}")
    registro = json.loads(saida_json.read_text(encoding="utf-8"))
    registro["stdout"] = (proc.stdout or "")[-600:]
    registro["stderr"] = (proc.stderr or "")[-600:]
    return registro


# ----------------------------------------------------------------------------------------------------------------
# Comparação (funções puras; a bateria as testa com dublês)
# ----------------------------------------------------------------------------------------------------------------
def lado_noul(v: float, nao: float, sim: float) -> str:
    """O lado que `metricas.faixa_noul` dá ao valor (achado 6: no corte único, o valor exato no corte é `sim`)."""
    r = M.faixa_noul([(v, True)], nao, sim)
    if r["revisao"]:
        return "dúvida"
    return "sim" if r["acerto_decididos"] == 1.0 else "não"


def _num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _validar(tipo: str, q: str, a: dict, opcoes: list[str] | None) -> dict:
    """Resposta validada pelo mesmo crivo dos exemplos (`congelamento.noul/choice`); Score conferido aqui.
    Levanta ValueError no inválido (achado 4)."""
    resposta = {"answers": {q: a}}
    if tipo == "noul":
        return {"noul": CG.noul(resposta, q)}
    if tipo == "choice":
        ops = set(opcoes) if opcoes else set((a.get("probabilities") or {}).keys())
        if not ops:
            raise ValueError(f"Choice {q!r} sem opções declaradas nem probabilidades")
        return CG.choice(resposta, q, ops)
    if tipo == "score":
        if not isinstance(a, dict) or a.get("type", "score") != "score" or not _num(a.get("score")):
            raise ValueError(f"resposta sem Score válido para {q!r}")
        probs = {k: CG.probabilidade(v) for k, v in (a.get("probabilities") or {}).items()}
        if probs and abs(sum(probs.values()) - 1.0) > 0.02:
            raise ValueError(f"probabilidades inválidas em {q!r}")
        return {"score": float(a["score"]), "probabilities": probs}
    raise ValueError(f"tipo desconhecido em {q!r}: {tipo!r}")


def comparar_pedidos(antes: dict, depois: dict, faixas: dict | None = None) -> dict:
    """Pedido a pedido (pareados pela chave state+perguntas), pergunta a pergunta: quem trocou de lado e a distância
    que o valor ORIGINAL tinha do limiar (pequena = já morava na fronteira). Noul: faixa do consumidor para aquele ID
    (`faixas`; sem regra = limiar desconhecido, conta à parte e não vira troca); Choice: vencedor, distância = margem
    entre as duas maiores probabilidades; Score: arredondamento, distância ao meio-inteiro mais próximo. Resposta
    que não passa na validação dos exemplos é contada em `invalidas` e não é comparada."""
    faixas = faixas or {}
    comuns = sorted(set(antes) & set(depois))
    trocas, deltas, invalidas, sem_limiar = [], [], [], set()
    n_perguntas = 0
    por_tipo = {"noul": 0, "choice": 0, "score": 0}
    for ch in comuns:
        a, d = antes[ch], depois[ch]
        for q, ra in (a.get("answers") or {}).items():
            rd = (d.get("answers") or {}).get(q)
            if rd is None:
                continue
            tipo = (a.get("tipos") or {}).get(q) or (ra.get("type") if isinstance(ra, dict) else None) \
                or next((t for t in ("noul", "choice", "score") if isinstance(ra, dict) and t in ra), None)
            opcoes = (a.get("opcoes") or {}).get(q)
            try:
                va, vd = _validar(tipo, q, ra, opcoes), _validar(tipo, q, rd, opcoes)
            except ValueError as e:
                invalidas.append({"pedido": ch[:10], "pergunta": q, "erro": str(e)[:120]})
                continue
            n_perguntas += 1
            base = {"pedido": ch[:10], "pergunta": q, "tipo": tipo}
            if tipo == "noul":
                x, y = va["noul"], vd["noul"]
                deltas.append(abs(y - x))
                faixa = faixas.get(q)
                if not faixa:
                    sem_limiar.add(q)
                    continue
                nao, sim = faixa
                la, ld = lado_noul(x, nao, sim), lado_noul(y, nao, sim)
                if la != ld:
                    por_tipo["noul"] += 1
                    trocas.append({**base, "antes": round(x, 3), "depois": round(y, 3), "lado": f"{la} → {ld}",
                                   "limiar": f"{nao}–{sim}" if nao != sim else f"corte {sim}", "distancia": round(min(abs(x - nao), abs(x - sim)), 3)})
            elif tipo == "choice":
                pa, pd = va["probabilities"], vd["probabilities"]
                deltas.append(max(abs(pd.get(k, 0.0) - pa.get(k, 0.0)) for k in set(pa) | set(pd)))
                if va["choice"] != vd["choice"]:
                    por_tipo["choice"] += 1
                    ordem = sorted(pa.values(), reverse=True)
                    margem = (ordem[0] - ordem[1]) if len(ordem) > 1 else 0.0
                    trocas.append({**base, "antes": va["choice"], "depois": vd["choice"], "lado": f"{va['choice']} → {vd['choice']}",
                                   "limiar": "vencedor", "distancia": round(margem, 3)})
            elif tipo == "score":
                sa, sd = va["score"], vd["score"]
                deltas.append(abs(sd - sa))
                na, nd = math.floor(sa + 0.5), math.floor(sd + 0.5)
                if na != nd:
                    por_tipo["score"] += 1
                    trocas.append({**base, "antes": round(sa, 3), "depois": round(sd, 3), "lado": f"{na} → {nd}", "limiar": "meio-inteiro",
                                   "distancia": round(abs(sa - (min(na, nd) + 0.5)), 3)})
    deltas.sort()
    return {"pedidos_antes": len(antes), "pedidos_depois": len(depois), "pareados": len(comuns), "perguntas": n_perguntas,
            "trocas": trocas, "trocas_por_tipo": por_tipo, "invalidas": invalidas, "sem_limiar": sorted(sem_limiar),
            "delta_medio": round(statistics.mean(deltas), 4) if deltas else None,
            "delta_p95": round(deltas[min(len(deltas) - 1, int(0.95 * len(deltas)))], 3) if deltas else None,
            "delta_max": round(deltas[-1], 3) if deltas else None}


def tabelas_por_id(md: str, identidade: list[str] | None = None) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Linhas de toda tabela Markdown cuja primeira coluna é `id`, por identidade composta
    ("<nº da tabela>:<id>[/<coluna extra>…]" com as colunas de `identidade` presentes no cabeçalho — achado 8).
    Devolve também as chaves REPETIDAS (ambíguas: ficam fora do pareamento e são relatadas)."""
    identidade = identidade or []
    linhas = md.splitlines()
    saida, repetidas, i, n = {}, [], 0, 0
    while i < len(linhas):
        l = linhas[i].strip()
        if l.startswith("|") and i + 1 < len(linhas) and re.match(r"^\|(?:-{3,}\|)+\s*$", linhas[i + 1].strip()):
            cab = [c.strip() for c in l[1:-1].split("|")]
            if cab and cab[0].lower() == "id":
                n += 1
                extras = [c for c in identidade if c in cab]
                j = i + 2
                while j < len(linhas) and linhas[j].strip().startswith("|"):
                    cels = [c.strip() for c in linhas[j].strip()[1:-1].split("|")]
                    if cels and cels[0]:
                        linha = dict(zip(cab, cels))
                        chave = f"{n}:" + "/".join([cels[0], *[linha.get(c, "") for c in extras]])
                        if chave in saida:
                            repetidas.append(chave)
                        saida[chave] = linha
                    j += 1
                i = j
                continue
        i += 1
    for chave in set(repetidas):
        saida.pop(chave, None)
    return saida, sorted(set(repetidas))


def _marca(celula: str) -> str:
    m = MARCA.search(celula or "")
    return m.group(0) if m else ""


def comparar_casos(md_antes: str, md_depois: str, formato: dict | None = None) -> dict:
    """Diferença linha a linha das tabelas por identidade: quais colunas mudaram; "trocou de lado" = uma coluna de
    RESULTADO do consumidor mudou (célula inteira em `ok`/`marca`/`acerto`; só o símbolo de desfecho na célula da
    variante quando `marca` = "sufixo" — achado 9). Linhas só de um lado e repetidas são registradas."""
    formato = formato or PADRAO_CONSUMIDOR
    ta, rep_a = tabelas_por_id(md_antes, formato["identidade"])
    td, rep_d = tabelas_por_id(md_depois, formato["identidade"])
    resultado = [c.lower() for c in formato["resultado"]]
    sufixo = formato.get("marca") == "sufixo"
    mudaram, trocaram, sem_coluna = [], [], True
    for k, la in ta.items():
        ld = td.get(k)
        if ld is None:
            continue
        if any(c.lower() in resultado for c in la):
            sem_coluna = False
        cols = [c for c in la if la[c] != ld.get(c)]
        if not cols:
            continue
        item = {"id": k.split(":", 1)[1], "tabela": int(k.split(":", 1)[0]), "colunas": {c: f"{la[c]} → {ld.get(c)}" for c in cols}}
        mudaram.append(item)
        troca = [c for c in cols if c.lower() in resultado and (not sufixo or _marca(la[c]) != _marca(ld.get(c, "")))]
        if troca:
            trocaram.append(item)
    return {"linhas": len(ta), "pareadas": sum(k in td for k in ta), "mudaram": mudaram, "trocaram_lado": trocaram,
            "so_antes": sorted(k for k in ta if k not in td), "so_depois": sorted(k for k in td if k not in ta),
            "repetidas": sorted(set(rep_a) | set(rep_d)),
            "aviso": None if not ta or not sem_coluna else f"nenhuma linha tem coluna de resultado {formato['resultado']}: troca de lado no caso não é medida"}


def veredito_md(md: str) -> dict | None:
    """Tabela "Critério congelado conferido no teste" → {"linhas": [{critério, medido, limite, passa}], "passa_tudo"}.
    None quando o run.py não gera essa tabela (o README decide)."""
    pos = md.find("Critério congelado conferido no teste")
    if pos < 0:
        return None
    linhas = md[pos:].splitlines()
    for i, l in enumerate(linhas):
        if l.strip().startswith("|") and i + 1 < len(linhas) and re.match(r"^\|(?:-{3,}\|)+\s*$", linhas[i + 1].strip()):
            cab = [c.strip() for c in l.strip()[1:-1].split("|")]
            saida = []
            for r in linhas[i + 2:]:
                if not r.strip().startswith("|"):
                    break
                saida.append(dict(zip(cab, [c.strip() for c in r.strip()[1:-1].split("|")])))
            passa = [x.get("passa", "") for x in saida]
            return {"linhas": saida, "passa_tudo": bool(passa) and all(p == "✓" for p in passa),
                    "resumo": "".join(p if p in "✓✗" else "?" for p in passa)}
    return None


def _achatar(obj, prefixo: str = "") -> dict:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out.update(_achatar(v, f"{prefixo}{k}/"))
        return out
    return {prefixo.rstrip("/"): obj}


def _metricas_de(resumo: dict | None) -> tuple[dict, str | None]:
    """`resumo["variantes"]` (a maioria) ou `resumo["desenhos"]` (juiz, conferência, lint) achatados; outra
    estrutura = aviso explícito (achado 7)."""
    r = resumo or {}
    for chave in ("variantes", "desenhos"):
        if isinstance(r.get(chave), dict):
            return _achatar(r[chave]), None
    return {}, f"estrutura do resumo desconhecida (chaves: {', '.join(map(str, r)) or 'nenhuma'}): métricas não comparadas"


def comparar_metricas(resumo_antes: dict | None, resumo_depois: dict | None) -> tuple[list[dict], list[str]]:
    """Toda folha das métricas que mudou (fora latência/custo/contagem de cache) e os avisos de estrutura."""
    a, av_a = _metricas_de(resumo_antes)
    d, av_d = _metricas_de(resumo_depois)
    saida = []
    for k in sorted(set(a) | set(d)):
        if IGNORAR_METRICA.search(k):
            continue
        va, vd = a.get(k), d.get(k)
        if va != vd and not (_num(va) and _num(vd) and abs(va - vd) < 1e-9):
            saida.append({"metrica": k, "antes": va, "depois": vd})
    return saida, [x for x in (av_a and f"referência: {av_a}", av_d and f"rodada nova: {av_d}") if x]


def comparar(antes: dict, depois: dict, exemplo: str | None = None) -> dict:
    formato = consumidor(exemplo or antes.get("exemplo") or "")
    v_a, v_d = veredito_md(antes.get("markdown", "")), veredito_md(depois.get("markdown", ""))
    metricas, avisos = comparar_metricas(antes.get("resumo"), depois.get("resumo"))
    casos = comparar_casos(antes.get("markdown", ""), depois.get("markdown", ""), formato)
    pedidos = comparar_pedidos(antes.get("pedidos", {}), depois.get("pedidos", {}), antes.get("faixas") or depois.get("faixas"))
    if casos.get("aviso"):
        avisos.append(casos["aviso"])
    if casos["repetidas"]:
        avisos.append(f"{len(casos['repetidas'])} linha(s) com identidade repetida ficaram fora do pareamento: {', '.join(casos['repetidas'][:6])}")
    if casos["so_antes"] or casos["so_depois"]:
        avisos.append(f"linhas só na referência: {len(casos['so_antes'])}; só na rodada nova: {len(casos['so_depois'])}")
    if pedidos["sem_limiar"]:
        avisos.append(f"{len(pedidos['sem_limiar'])} ID(s) de Noul sem limiar mapeado (Δ medido, troca não): {', '.join(pedidos['sem_limiar'][:8])}"
                      + (" …" if len(pedidos["sem_limiar"]) > 8 else ""))
    if pedidos["invalidas"]:
        avisos.append(f"{len(pedidos['invalidas'])} resposta(s) inválida(s) pelo crivo dos exemplos, fora da comparação")
    if antes.get("aviso_faixa"):
        avisos.append(f"perguntas.py da referência não importou: {antes['aviso_faixa']}")
    return {"metricas": metricas,
            "veredito": {"antes": v_a, "depois": v_d,
                         "mudou": [{"criterio": x.get("critério"), "antes": x.get("passa"), "depois": y.get("passa"), "medido": f"{x.get('medido')} → {y.get('medido')}"}
                                   for x, y in zip((v_a or {}).get("linhas", []), (v_d or {}).get("linhas", [])) if x.get("passa") != y.get("passa")]},
            "casos": casos, "pedidos": pedidos, "avisos": avisos}


# ----------------------------------------------------------------------------------------------------------------
# Orquestração
# ----------------------------------------------------------------------------------------------------------------
def _custo_de(registro: dict) -> dict:
    return {"requisicoes": len(registro.get("pedidos", {})), "tokens": registro.get("tokens", 0),
            "custo_us": round(registro.get("tokens", 0) / 1e6 * PRECO, 4), "erros": len(registro.get("erros", [])),
            "modelos": sorted({p.get("modelo") for p in registro.get("pedidos", {}).values() if p.get("modelo")})}


def reavaliar(modelo: str, exemplos: list[str], raiz: Path = EXEMPLOS, so_estimar: bool = False, executar=executar_driver,
              local: Path = LOCAL, max_custo: float | None = None, ao_vivo: bool = True, parar_em_429: int = 3, log=print) -> dict:
    """Referência (gravado, sobre cópia do cache) em todos; estimativa; depois ao vivo em cada um. Referência
    incompleta barra o exemplo (achado 2); nunca aborta por um exemplo."""
    pasta_cache = f"cache-{modelo}"
    inicio = datetime.datetime.now().astimezone()
    resultado = {"modelo": modelo, "modelo_congelado": MODELO_CONGELADO, "inicio": inicio.isoformat(timespec="seconds"), "exemplos": {},
                 "so_estimar": so_estimar, "estimativa": {}, "parado": None}
    # 1. Referência + estimativa, do cache (zero chamada).
    for ex in exemplos:
        pasta = raiz / ex
        item: dict = {"antes": None, "depois": None, "erro": None, "intocado": None, "referencia": None}
        resultado["exemplos"][ex] = item
        h0 = hash_pasta(pasta, (pasta_cache,))
        try:
            item["antes"] = executar(pasta, "gravado", None, None, local / modelo / ex / "antes")
            item["referencia"] = referencia_completa(item["antes"], casos_esperados(pasta))
            if item["referencia"]:
                item["erro"] = "referência incompleta: " + "; ".join(item["referencia"])
        except Exception as e:
            item["erro"] = f"referência (gravado) falhou: {type(e).__name__}: {str(e)[:300]}"
        item["intocado"] = hash_pasta(pasta, (pasta_cache,)) == h0
        if item["antes"] and not item["erro"]:
            item["estimativa"] = {**_custo_de(item["antes"]), "n": (item["antes"].get("resumo") or {}).get("n")}
    est = [i["estimativa"] for i in resultado["exemplos"].values() if i.get("estimativa")]
    resultado["estimativa"] = {"exemplos": len(est), "requisicoes": sum(e["requisicoes"] for e in est), "tokens": sum(e["tokens"] for e in est),
                               "custo_us": round(sum(e["custo_us"] for e in est), 4)}
    log(f"estimativa ({len(est)} exemplos com referência completa, do cache): {resultado['estimativa']['requisicoes']} requisições, "
        f"{resultado['estimativa']['tokens']} tokens, US$ {resultado['estimativa']['custo_us']:.4f}")
    for ex, i in resultado["exemplos"].items():
        e = i.get("estimativa") or {}
        log(f"  {ex}: {e.get('requisicoes', '—')} req · {e.get('tokens', '—')} tokens · US$ {e.get('custo_us', 0):.4f}" + (f" · BARRADO: {i['erro']}" if i["erro"] else ""))
    if so_estimar or not ao_vivo:
        return resultado
    if max_custo is not None and resultado["estimativa"]["custo_us"] > max_custo:
        resultado["parado"] = f"estimativa US$ {resultado['estimativa']['custo_us']:.4f} acima do teto US$ {max_custo:.2f}; nada foi chamado"
        log(resultado["parado"])
        return resultado
    # 2. Ao vivo, um exemplo por vez.
    for ex, item in resultado["exemplos"].items():
        if item["erro"]:
            continue
        pasta = raiz / ex
        h0 = hash_pasta(pasta, (pasta_cache,))
        t0 = time.perf_counter()
        try:
            item["depois"] = executar(pasta, "ao_vivo", modelo, pasta_cache, local / modelo / ex / "depois")
            item["segundos"] = round(time.perf_counter() - t0)
            if item["depois"].get("excecao") or item["depois"].get("recusado"):
                item["erro"] = f"ao vivo falhou: {item['depois'].get('excecao') or item['depois'].get('recusado')}"
            else:
                item["comparacao"] = comparar(item["antes"], item["depois"], ex)
            item["custo"] = _custo_de(item["depois"])
        except Exception as e:
            item["erro"] = f"ao vivo falhou: {type(e).__name__}: {str(e)[:300]}"
        item["intocado"] = item["intocado"] and hash_pasta(pasta, (pasta_cache,)) == h0
        c = item.get("custo") or {}
        log(f"{ex}: {c.get('requisicoes', 0)} req, US$ {c.get('custo_us', 0):.4f}, {c.get('erros', 0)} erro(s)"
            + (f" · ERRO {item['erro']}" if item["erro"] else "") + ("" if item["intocado"] else " · PASTA DO EXEMPLO ALTERADA"))
        if (item.get("depois") or {}).get("max_429_seguidos", 0) >= parar_em_429:
            resultado["parado"] = f"{parar_em_429} erros 429 seguidos em {ex}; os exemplos seguintes não foram rodados"
            log(resultado["parado"])
            break
    resultado["fim"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    return resultado


def _faixas_subprocesso(pasta: Path, ids: list[str], python: str = sys.executable) -> dict:
    """Resolve o mapa id→faixa importando o `perguntas.py` do exemplo num subprocesso (sem o `run.py`, zero chamada)."""
    proc = subprocess.run([python, "-X", "utf8", str(Path(__file__).resolve()), "--_faixas", str(pasta)], input=json.dumps(ids),
                          cwd=str(pasta), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or "")[-400:])
    return json.loads(proc.stdout)


def recomparar(resultado: dict, local: Path, raiz: Path = EXEMPLOS, faixas=_faixas_subprocesso) -> dict:
    """Refaz comparação e conferência da referência a partir dos registros gravados (`--so-relatorio`): zero chamada.
    Registro gravado antes do mapa de faixas existir ganha o mapa agora, pelo `perguntas.py` do exemplo."""
    for ex, item in resultado["exemplos"].items():
        for lado in ("antes", "depois"):
            arq = local / resultado["modelo"] / ex / lado / "driver.json"
            if arq.exists():
                item[lado] = json.loads(arq.read_text(encoding="utf-8"))
        if item.get("antes") and "faixas" not in item["antes"]:
            ids = sorted({q for p in item["antes"].get("pedidos", {}).values() for q in (p.get("answers") or {})})
            try:
                item["antes"]["faixas"] = faixas(raiz / ex, ids)
            except Exception as e:
                item["antes"]["faixas"], item["antes"]["aviso_faixa"] = {q: None for q in ids}, f"{type(e).__name__}: {str(e)[:200]}"
        if item.get("antes"):
            item["referencia"] = referencia_completa(item["antes"], casos_esperados(raiz / ex))
            if item["referencia"] and not (item.get("erro") or "").startswith("referência incompleta"):
                item["erro"] = "referência incompleta: " + "; ".join(item["referencia"])
        if item.get("antes") and item.get("depois") and not item.get("erro"):
            item["comparacao"] = comparar(item["antes"], item["depois"], ex)
            item["custo"] = _custo_de(item["depois"])
    return resultado


# ----------------------------------------------------------------------------------------------------------------
# Relatório
# ----------------------------------------------------------------------------------------------------------------
def _tabela(linhas: list[dict], colunas: list[str] | None = None) -> str:
    if not linhas:
        return "_(nenhuma)_"
    colunas = colunas or list(linhas[0])
    f = lambda v: "—" if v is None else f"{v:.3f}" if isinstance(v, float) else str(v).replace("|", "¦").replace("\n", " ")  # noqa: E731
    return "| " + " | ".join(colunas) + " |\n|" + "---|" * len(colunas) + "\n" + "\n".join("| " + " | ".join(f(l.get(c)) for c in colunas) + " |" for l in linhas)


def relatorio_md(resultado: dict, pulados: dict[str, str], data: str) -> str:
    modelo, exs = resultado["modelo"], resultado["exemplos"]
    feitos = {k: v for k, v in exs.items() if v.get("comparacao")}
    tot_req = sum((v.get("custo") or {}).get("requisicoes", 0) for v in exs.values())
    tot_tok = sum((v.get("custo") or {}).get("tokens", 0) for v in exs.values())
    tot_us = round(tot_tok / 1e6 * PRECO, 4)
    tot_trocas = sum(len(v["comparacao"]["pedidos"]["trocas"]) for v in feitos.values())
    tot_perg = sum(v["comparacao"]["pedidos"]["perguntas"] for v in feitos.values())
    tot_casos_lado = sum(len(v["comparacao"]["casos"]["trocaram_lado"]) for v in feitos.values())
    ver_mudou = [k for k, v in feitos.items() if v["comparacao"]["veredito"]["mudou"]]
    est = resultado["estimativa"]
    mesma_versao = modelo == resultado["modelo_congelado"]
    out = ["---", f"name: reavaliacao-{modelo}-{data}",
           f"description: Reavaliação dos testes congelados contra `{modelo}` ao vivo em {data}"
           + (" (a MESMA versão congelada — referência empírica da variação entre rodadas)" if mesma_versao else f" (versão congelada `{resultado['modelo_congelado']}`)")
           + f" — {len(feitos)} exemplos, {tot_req} requisições, US$ {tot_us:.4f}; {tot_trocas} trocas de lado em {tot_perg} perguntas, "
           f"{tot_casos_lado} casos trocaram o resultado, veredito do critério mudou em {len(ver_mudou)} exemplo(s)",
           "tipo: medicao",
           f"fonte: gerado por `ferramentas/reavaliar_versao.py --modelo {modelo}` em {data}; caches novos em `exemplos/*/cache-{modelo}/`; referência = cópia de `exemplos/*/cache/` (versão congelada)",
           f"estudado_em: {data}", "---", "",
           f"# Reavaliação por versão — `{modelo}` ({data})", "",
           f"Gerado por `ferramentas/reavaliar_versao.py` [testado]. Início {resultado['inicio']}, fim {resultado.get('fim', '—')}. "
           f"Versão congelada dos exemplos: `{resultado['modelo_congelado']}`; modelo reavaliado: `{modelo}`"
           + (" — **a mesma versão**: as diferenças abaixo são a variação entre rodadas da API nesta amostra, uma rodada, um dia. São referência "
              "empírica, não banda segura: uma versão nova com trocas do mesmo tamanho pode ser efeito de versão; só a distância não diz a causa." if mesma_versao else ".")
           + " Nada do exemplo foi alterado: a referência leu uma cópia do `cache/`, o cache novo está em `cache-<modelo>/` ao lado do original, "
           "limiares e manifestos intocados (conferido por hash da pasta antes/depois, coluna `intocado`). Recalibrar é decisão humana: este relatório só mede.", "",
           f"**Estimativa impressa antes de qualquer chamada** (da referência, só exemplos com referência completa): {est.get('exemplos')} exemplos, "
           f"{est.get('requisicoes')} requisições, {est.get('tokens')} tokens, US$ {est.get('custo_us', 0):.4f}. **Custo real**: {tot_req} requisições, {tot_tok} tokens, "
           f"US$ {tot_us:.4f} (US$ {PRECO} por milhão de tokens de entrada).", ""]
    if resultado.get("parado"):
        out += [f"> **Parado:** {resultado['parado']}", ""]
    out += ["## Como ler", "",
            "- **referência completa**: `n` do resumo = casos de `dados/teste.json`, nenhum pedido sem resposta no cache, nenhuma invalidação; sem isso o exemplo é barrado antes de estimar ou chamar.",
            "- **métricas**: folhas de `resumo[\"variantes\"]` (ou `resumo[\"desenhos\"]`) que o `run.py` calcula (sem latência/custo) que mudaram entre a referência e a rodada nova.",
            "- **veredito**: a tabela \"Critério congelado conferido no teste\" gerada pelo `run.py` (✓/✗ por critério, na ordem); exemplos sem essa tabela aparecem como `—` (o README decide).",
            "- **casos**: linhas das tabelas por `id` (identidade composta com k/q/variante/af/crit/regra quando a tabela tem) que mudaram; *trocou o resultado* = a coluna de resultado "
            "declarada para o exemplo (`ok`, `marca`, `acerto`, ou a marca de desfecho na célula da variante principal) mudou.",
            "- **perguntas**: pedido a pedido (pareado por hash de state+perguntas), cada Noul/Choice/Score válido pelo crivo dos exemplos que trocou de lado; `distância` = quanto o valor ORIGINAL "
            "distava do limiar que o CÓDIGO do exemplo aplica àquele ID (mapa explícito por consumidor; ID sem mapa = limiar desconhecido, só Δ); Choice = margem entre as duas maiores "
            "probabilidades; Score = distância ao meio-inteiro. `Δ` = diferença absoluta por pergunta (Choice: maior diferença entre probabilidades).", "",
            "## Resumo", ""]
    linhas = []
    for ex, v in exs.items():
        c, cmp = v.get("custo") or {}, v.get("comparacao")
        ver = cmp["veredito"] if cmp else None
        f_ver = lambda x: (x or {}).get("resumo", "—") if x else "—"  # noqa: E731
        linhas.append({"exemplo": ex, "n": (v.get("estimativa") or {}).get("n"), "ref. completa": "—" if v.get("referencia") is None else ("✓" if not v["referencia"] else "✗"),
                       "req": c.get("requisicoes"), "US$": c.get("custo_us"), "erros API": c.get("erros"),
                       "veredito antes → depois": f"{f_ver(ver['antes'])} → {f_ver(ver['depois'])}" if ver else "—",
                       "métricas ≠": len(cmp["metricas"]) if cmp else None,
                       "casos ≠ / trocaram": f"{len(cmp['casos']['mudaram'])} / {len(cmp['casos']['trocaram_lado'])} de {cmp['casos']['pareadas']}" if cmp else "—",
                       "perguntas trocaram": f"{len(cmp['pedidos']['trocas'])} de {cmp['pedidos']['perguntas']}" if cmp else "—",
                       "Δ médio / p95 / máx": f"{cmp['pedidos']['delta_medio']} / {cmp['pedidos']['delta_p95']} / {cmp['pedidos']['delta_max']}" if cmp else "—",
                       "avisos": len(cmp["avisos"]) if cmp else None,
                       "intocado": "✓" if v.get("intocado") else "**✗ ALTERADO**",
                       "erro": v.get("erro") or ""})
    out += [_tabela(linhas), ""]
    if pulados:
        out += ["**Pulados**: " + "; ".join(f"`{k}` — {v}" for k, v in pulados.items()), ""]
    for ex, v in exs.items():
        cmp = v.get("comparacao")
        c = v.get("custo") or {}
        out += [f"## `{ex}`", ""]
        if v.get("erro"):
            out += [f"**Não medido**: {v['erro']}", ""]
            if not v.get("intocado"):
                out += ["**A pasta do exemplo foi alterada durante a execução** — conferir `git status` antes de qualquer uso.", ""]
            continue
        if not cmp:
            out += ["**Não rodado ao vivo** (execução parada antes de chegar aqui).", ""]
            continue
        a_m = (v["antes"].get("pedidos") and sorted({p.get("modelo") for p in v["antes"]["pedidos"].values() if p.get("modelo")})) or []
        out += [f"n = {(v.get('estimativa') or {}).get('n', '—')} · referência completa ✓ · {c.get('requisicoes')} requisições ao vivo ({c.get('erros')} erro(s) de API), "
                f"{c.get('tokens')} tokens, US$ {c.get('custo_us', 0):.4f}, {v.get('segundos', '—')} s · modelo devolvido pela API: {', '.join(c.get('modelos') or ['—'])} "
                f"(referência: {', '.join(a_m) or '—'}) · pasta intocada: {'✓' if v.get('intocado') else '**✗ ALTERADA**'}", ""]
        if c.get("erros"):
            out += [f"> {c['erros']} pedido(s) falharam na API (o exemplo os trata como falha operacional/revisar — **a rodada nova não é medição limpa**): "
                    + "; ".join(e["erro"] for e in v["depois"].get("erros", [])[:5]), ""]
        if cmp["avisos"]:
            out += ["**Avisos**: " + " · ".join(cmp["avisos"]), ""]
        ver = cmp["veredito"]
        if ver["antes"] is None and ver["depois"] is None:
            out += ["**Veredito**: o `run.py` deste exemplo não gera a tabela do critério (o README decide).", ""]
        else:
            out += [f"**Veredito do critério**: {(ver['antes'] or {}).get('resumo', '—')} → {(ver['depois'] or {}).get('resumo', '—')}"
                    + (" — **mudou**:" if ver["mudou"] else " — igual."), ""]
            if ver["mudou"]:
                out += [_tabela(ver["mudou"], ["criterio", "antes", "depois", "medido"]), ""]
        out += [f"**Métricas que mudaram** ({len(cmp['metricas'])}):", "", _tabela(cmp["metricas"][:MAX_LINHAS_TROCAS], ["metrica", "antes", "depois"]), ""]
        cs = cmp["casos"]
        fmt = consumidor(ex)
        out += [f"**Casos**: {cs['pareadas']} linhas pareadas (identidade `id`{''.join(' + `' + c + '`' for c in fmt['identidade'])}; "
                f"só na referência {len(cs['so_antes'])}, só na nova {len(cs['so_depois'])}, repetidas {len(cs['repetidas'])}); "
                f"{len(cs['mudaram'])} mudaram alguma coluna; **{len(cs['trocaram_lado'])} trocaram o resultado** (coluna {', '.join('`' + c + '`' for c in fmt['resultado'])}):", "",
                _tabela([{"id": x["id"], "tabela": x["tabela"], "colunas que mudaram": "; ".join(f"{k}: {val}" for k, val in x["colunas"].items())}
                         for x in cs["trocaram_lado"][:MAX_LINHAS_TROCAS]], ["id", "tabela", "colunas que mudaram"]), ""]
        if len(cs["trocaram_lado"]) > MAX_LINHAS_TROCAS:
            out += [f"_(… e mais {len(cs['trocaram_lado']) - MAX_LINHAS_TROCAS}; tudo em `.local/reavaliacao/`)_", ""]
        pd = cmp["pedidos"]
        out += [f"**Perguntas**: {pd['pareados']} pedidos pareados de {pd['pedidos_antes']} (referência) × {pd['pedidos_depois']} (nova); {pd['perguntas']} perguntas válidas comparadas "
                f"({len(pd['invalidas'])} inválidas fora; {len(pd['sem_limiar'])} IDs sem limiar mapeado); "
                f"Δ médio {pd['delta_medio']}, p95 {pd['delta_p95']}, máximo {pd['delta_max']}; **{len(pd['trocas'])} trocaram de lado** "
                f"(noul {pd['trocas_por_tipo']['noul']}, choice {pd['trocas_por_tipo']['choice']}, score {pd['trocas_por_tipo']['score']}):", "",
                _tabela(sorted(pd["trocas"], key=lambda t: t["distancia"])[:MAX_LINHAS_TROCAS], ["pedido", "pergunta", "tipo", "antes", "depois", "lado", "limiar", "distancia"]), ""]
        if len(pd["trocas"]) > MAX_LINHAS_TROCAS:
            out += [f"_(… e mais {len(pd['trocas']) - MAX_LINHAS_TROCAS}, ordenadas pela distância; tudo em `.local/reavaliacao/`)_", ""]
    return "\n".join(out)


def atualizar_indice(indice: Path, arquivo_rel: str, linha: str) -> None:
    """Uma linha por relatório na seção Evidências; se já existe uma para o mesmo arquivo, substitui."""
    texto = indice.read_text(encoding="utf-8")
    linhas = texto.split("\n")
    nova = f"- {linha}"
    idx = [i for i, l in enumerate(linhas) if f"({arquivo_rel})" in l]
    if idx:
        linhas[idx[0]] = nova
    else:
        ancora = [i for i, l in enumerate(linhas) if "evidencias/medicoes-2026-10-01.md" in l or "evidencias/medicoes-" in l]
        pos = (ancora[-1] + 1) if ancora else len(linhas)
        linhas.insert(pos, nova)
    indice.write_text("\n".join(linhas), encoding="utf-8", newline="\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--modelo", help="id do modelo a reavaliar (ex.: jev-1.14.0)")
    ap.add_argument("--exemplos", help="lista separada por vírgula; padrão = todos com manifesto")
    ap.add_argument("--so-estimar", action="store_true", help="só conta requisições e custo (da referência), sem chamar")
    ap.add_argument("--max-custo", type=float, help="teto em US$ para a soma estimada; acima disso nada é chamado")
    ap.add_argument("--so-relatorio", action="store_true", help="recompara e regera o relatório a partir de .local/reavaliacao/<modelo>/ (zero chamada)")
    ap.add_argument("--acumular", action="store_true", help="junta com o resultado anterior do mesmo modelo no mesmo dia (retomar depois de uma parada ou rodar por partes)")
    ap.add_argument("--_driver", help=argparse.SUPPRESS)
    ap.add_argument("--_saida", help=argparse.SUPPRESS)
    ap.add_argument("--_faixas", help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args._driver:
        _driver(Path(args._driver), Path(args._saida))
        return
    if args._faixas:
        pasta = Path(args._faixas).resolve()
        sys.path.insert(0, str(pasta))
        import perguntas
        print(json.dumps(_faixas_resolvidas(pasta.name, perguntas, json.loads(sys.stdin.read()))))
        return
    if not args.modelo:
        ap.error("--modelo é obrigatório")
    if "/" in args.modelo or "\\" in args.modelo or args.modelo.strip() in ("", ".", ".."):
        ap.error("--modelo tem de ser um id simples (vira o nome da pasta cache-<modelo>)")
    pedidos = [x.strip() for x in args.exemplos.split(",") if x.strip()] if args.exemplos else None
    elegiveis, pulados = listar_exemplos(EXEMPLOS, pedidos)
    print(f"exemplos elegíveis ({len(elegiveis)}): {', '.join(elegiveis)}")
    for k, v in pulados.items():
        print(f"  pulado {k}: {v}")
    data = datetime.date.today().isoformat()
    anterior = LOCAL / args.modelo / "resultado.json"
    if args.so_relatorio:
        resultado = recomparar(json.loads(anterior.read_text(encoding="utf-8")), LOCAL)
        data = resultado.get("inicio", data)[:10]
    else:
        resultado = reavaliar(args.modelo, elegiveis, so_estimar=args.so_estimar, max_custo=args.max_custo)
    if args.so_estimar:
        return
    if args.acumular and anterior.exists() and not args.so_relatorio:
        velho = json.loads(anterior.read_text(encoding="utf-8"))
        if velho.get("inicio", "")[:10] == data:
            # Exemplos já medidos hoje e não pedidos agora continuam no relatório; os pedidos agora substituem.
            resultado["exemplos"] = dict(sorted({**velho.get("exemplos", {}), **resultado["exemplos"]}.items()))
            resultado["inicio"] = velho.get("inicio", resultado["inicio"])
            est = [i["estimativa"] for i in resultado["exemplos"].values() if i.get("estimativa")]
            resultado["estimativa"] = {"exemplos": len(est), "requisicoes": sum(e["requisicoes"] for e in est),
                                       "tokens": sum(e["tokens"] for e in est), "custo_us": round(sum(e["custo_us"] for e in est), 4)}
            resultado["acumulado_de"] = str(anterior)
    saida = EVIDENCIAS / f"reavaliacao-{args.modelo}-{data}.md"
    saida.write_text(relatorio_md(resultado, pulados, data), encoding="utf-8", newline="\n")
    feitos = sum(1 for v in resultado["exemplos"].values() if v.get("comparacao"))
    trocas = sum(len(v["comparacao"]["pedidos"]["trocas"]) for v in resultado["exemplos"].values() if v.get("comparacao"))
    mudou = sum(1 for v in resultado["exemplos"].values() if v.get("comparacao") and v["comparacao"]["veredito"]["mudou"])
    tot_us = round(sum((v.get("custo") or {}).get("tokens", 0) for v in resultado["exemplos"].values()) / 1e6 * PRECO, 4)
    atualizar_indice(INDICE, f"evidencias/{saida.name}",
                     f"[Reavaliação {args.modelo} ({data})](evidencias/{saida.name}) — testes congelados rodados ao vivo contra `{args.modelo}`: "
                     f"{feitos} exemplos, US$ {tot_us:.4f}; {trocas} perguntas trocaram de lado; veredito mudou em {mudou} exemplo(s)")
    print(f"relatório: {saida}")
    anterior.parent.mkdir(parents=True, exist_ok=True)
    anterior.write_text(json.dumps(_json_seguro(resultado), ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
