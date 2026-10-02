"""Bateria do arnês de reavaliação — roda sem chave e sem rede (`python -X utf8 ferramentas/testa_reavaliar_versao.py`).

Prova, com dublês no lugar do subprocesso que roda o run.py de cada exemplo, os 9 achados aplicados da revisão do
Codex (2026-10-01) e o básico:
  1. referência (gravado) lê uma CÓPIA do cache: o cliente redirecionado grava/move na cópia, o original fica igual;
  2. referência incompleta (pedido sem resposta absorvido pelo exemplo, n ≠ teste.json, invalidação) barra estimativa
     e rodada paga daquele exemplo; os outros seguem;
  3. `JEV_MODELO` do ambiente sem `JEV_PASTA_CACHE` (ou com `cache`, ou com a mesma pasta) é recusado antes de criar
     pasta; argumento explícito de modelo não é afetado; caminho absoluto é aceito;
  4. resposta inválida (bool, string, Choice sem distribuição, contraditória) é contada à parte e não vira troca;
  5. limiar vem do mapa do consumidor por ID (auditor `contradicts_0` → FAIXA["contradicts"], `scope_shown` → parts,
     `supports_0` → corte APOIO_MIN); ID sem regra = "limiar desconhecido", não 0,5;
  6. corte único: valor exatamente no corte é `sim`, como em `metricas.faixa_noul`;
  7. métricas de `resumo["variantes"]` E `resumo["desenhos"]`; outra estrutura = aviso explícito;
  8. identidade composta por tabela (id + k): linhas repetidas, só de um lado, registradas;
  9. troca de lado no caso só pelas colunas de resultado do consumidor (`?` no motivo não conta; marca na célula da
     variante principal conta);
  A. troca de lado pergunta a pergunta com a distância ao limiar; falha isolada; 3×429 param; teto; índice.
Nada aqui é medição do Jev: é código nosso.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import types
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "exemplos" / "_comum"))

import reavaliar_versao as R  # noqa: E402
import jevcache  # noqa: E402

FAIXAS = {"opt_out": [0.2, 0.7], "pausa": [0.3, 0.7], "nivel": None}


def pedido(**answers) -> dict:
    return {"tipos": {q: a.get("type") for q, a in answers.items()}, "answers": answers, "modelo": "duble", "tokens": 100000, "ms": 1,
            "opcoes": {q: list(a["probabilities"]) for q, a in answers.items() if a.get("type") == "choice" and "probabilities" in a}}


def noul(v):
    return {"type": "noul", "noul": v}


def choice(c, **p):
    return {"type": "choice", "choice": c, "probabilities": p, "confidence": 0.9}


def score(s):
    return {"type": "score", "score": s}


MD = """# Resultados — duble

**Critério congelado conferido no teste** (é este que decide)

| critério | medido | limite | passa |
|---|---|---|---|
| 1 erro caro | 0/10 | ≤ 0 | ✓ |
| 2 acerto | 0.900 | ≥ 0.85 | {p2} |

### Caso a caso

| id | gab | ação Jev | ok | motivo |
|---|---|---|---|---|
| T001 | seguir | seguir | ✓ | nada |
| T002 | bloquear | {t2} | {ok2} | {m2} |
| T003 | seguir | seguir | ✓ | nada |

| id | variante | erro |
|---|---|---|
| T002 | Jev | {erro2} |
"""


def md(p2="✓", t2="bloquear", ok2="✓", m2="opt-out", erro2=""):
    return MD.format(p2=p2, t2=t2, ok2=ok2, m2=m2, erro2=erro2)


# ---------------------------------------------------------------- A, 4, 5, 6: pergunta a pergunta
def testa_pedidos():
    antes = {"k1": pedido(opt_out=noul(0.72), pausa=noul(0.10), tipo=choice("none", none=0.55, deletion=0.45), nivel=score(1.4)),
             "k2": pedido(opt_out=noul(0.05), pausa=noul(0.95)),
             "so_antes": pedido(opt_out=noul(0.5))}
    depois = {"k1": pedido(opt_out=noul(0.68), pausa=noul(0.31), tipo=choice("deletion", none=0.40, deletion=0.60), nivel=score(1.6)),
              "k2": pedido(opt_out=noul(0.06), pausa=noul(0.94)),
              "so_depois": pedido(opt_out=noul(0.5))}
    r = R.comparar_pedidos(antes, depois, FAIXAS)
    assert r["pareados"] == 2 and r["pedidos_antes"] == 3 and r["pedidos_depois"] == 3, r
    assert r["perguntas"] == 6, r["perguntas"]
    por = {(t["pergunta"], t["tipo"]): t for t in r["trocas"]}
    t = por[("opt_out", "noul")]  # 0,72 → 0,68 com faixa 0,2–0,7: sim → dúvida; distância do original ao limiar = 0,02
    assert t["lado"] == "sim → dúvida" and t["distancia"] == 0.02 and t["limiar"] == "0.2–0.7", t
    t = por[("pausa", "noul")]  # 0,10 → 0,31 com 0,3–0,7: não → dúvida; distância 0,2
    assert t["lado"] == "não → dúvida" and t["distancia"] == 0.2, t
    t = por[("tipo", "choice")]  # vencedor trocou; margem original 0,10
    assert t["lado"] == "none → deletion" and t["distancia"] == 0.1, t
    t = por[("nivel", "score")]  # 1,4 → 1,6 cruza 1,5
    assert t["lado"] == "1 → 2" and t["distancia"] == 0.1, t
    assert len(r["trocas"]) == 4 and r["trocas_por_tipo"] == {"noul": 2, "choice": 1, "score": 1}, r["trocas_por_tipo"]
    assert r["delta_max"] == 0.21 and r["delta_medio"] is not None and r["invalidas"] == [], r
    # 4. inválidas (bool, string, Choice sem distribuição, Choice contraditória): contadas à parte, nunca troca
    r2 = R.comparar_pedidos({"k": pedido(a=noul(True), b=noul("0.9"), c=choice("x", x=0.5, y=0.5), d=choice("x", x=0.2, y=0.8))},
                            {"k": pedido(a=noul(0.9), b=noul(0.1), c={"type": "choice", "choice": "y"}, d=choice("y", x=0.1, y=0.9))},
                            {"a": [0.5, 0.5], "b": [0.5, 0.5]})
    assert r2["trocas"] == [] and r2["perguntas"] == 0 and len(r2["invalidas"]) == 4, r2
    assert any("contraditória" in i["erro"] for i in r2["invalidas"]), r2["invalidas"]
    # 5. ID sem limiar mapeado: Δ medido, "limiar desconhecido", NUNCA 0,5 por padrão
    r3 = R.comparar_pedidos({"k": pedido(a=noul(0.49))}, {"k": pedido(a=noul(0.51))}, {})
    assert r3["trocas"] == [] and r3["sem_limiar"] == ["a"] and r3["delta_max"] == 0.02, r3
    # 6. corte único: o valor EXATO no corte é `sim` (metricas.faixa_noul); 0,5 → 0,49 é sim → não
    r4 = R.comparar_pedidos({"k": pedido(a=noul(0.5), b=noul(0.49))}, {"k": pedido(a=noul(0.49), b=noul(0.5))}, {"a": [0.5, 0.5], "b": [0.5, 0.5]})
    lados = {t["pergunta"]: t["lado"] for t in r4["trocas"]}
    assert lados == {"a": "sim → não", "b": "não → sim"} and r4["trocas"][0]["limiar"] == "corte 0.5", r4["trocas"]
    assert R.lado_noul(0.7, 0.3, 0.7) == "sim" and R.lado_noul(0.3, 0.3, 0.7) == "não" and R.lado_noul(0.5, 0.3, 0.7) == "dúvida"
    print("A/4/5/6. pergunta a pergunta, inválidas, limiar desconhecido, corte único: ok")


# ---------------------------------------------------------------- 5. mapa explícito id → faixa do consumidor
def testa_mapa_faixas():
    P = types.SimpleNamespace(FAIXA={"contradicts": (0.3, 0.7), "established": (0.3, 0.8), "parts": (0.2, 0.9)}, APOIO_MIN=0.5)
    f = R._faixas_resolvidas("auditor-de-evidencia", P, ["contradicts_0", "supports_2", "scope_shown", "established", "inventado"])
    assert f == {"contradicts_0": [0.3, 0.7], "supports_2": [0.5, 0.5], "scope_shown": [0.2, 0.9], "established": [0.3, 0.8], "inventado": None}, f
    P2 = types.SimpleNamespace(FAIXA={"accepted": (0.3, 0.7)})
    assert R._faixas_resolvidas("compromisso-real", P2, ["k3_accepted", "k3_verdict"]) == {"k3_accepted": [0.3, 0.7], "k3_verdict": None}
    P3 = types.SimpleNamespace(LIMIAR={"fits": 0.5})
    assert R._faixas_resolvidas("selecao-de-skill", P3, ["fits.x", "gate.y"]) == {"fits.x": [0.5, 0.5], "gate.y": None}
    assert R._faixas_resolvidas("exemplo-desconhecido", P3, ["q"]) == {"q": None}
    print("5. mapa explícito id → faixa por consumidor: ok")


# ---------------------------------------------------------------- 7, 8, 9: métricas, identidade, colunas de resultado
def testa_casos():
    fmt = {"faixa": [], "identidade": ["k"], "resultado": ["ok"], "marca": "celula"}
    r = R.comparar_casos(md(), md(t2="revisar", ok2="✗", m2="dúvida", erro2="DUPLICATA"), fmt)
    assert r["linhas"] == 4 and r["pareadas"] == 4, r
    assert [x["id"] for x in r["mudaram"]] == ["T002", "T002"], r["mudaram"]  # as duas tabelas
    assert len(r["trocaram_lado"]) == 1 and r["trocaram_lado"][0]["colunas"]["ok"] == "✓ → ✗", r["trocaram_lado"]
    # 9. só o motivo (com `?`) mudou: a linha mudou, mas NÃO trocou de lado
    r = R.comparar_casos(md(), md(m2="dúvida: irreversível?"), fmt)
    assert len(r["mudaram"]) == 1 and r["trocaram_lado"] == [], r
    # 9. marca na célula da variante principal (motivo `c`): "grupo/folha ✓" → "grupo/folha ✗f" conta; texto sem marca mudando, não
    fmt_m = {"faixa": [], "identidade": [], "resultado": ["c"], "marca": "sufixo"}
    md_a = "| id | a | c |\n|---|---|---|\n| X1 | g/f ✓ | g/f ✓ |\n| X2 | g/f ✓ | g/f2 ✓ |\n"
    md_d = "| id | a | c |\n|---|---|---|\n| X1 | g/f ✗f | g/f ✗f |\n| X2 | g/f ✗f | g/f3 ✓ |\n"
    r = R.comparar_casos(md_a, md_d, fmt_m)
    assert [x["id"] for x in r["trocaram_lado"]] == ["X1"] and len(r["mudaram"]) == 2, r
    assert R._marca("fin ✓ (0.92)") == "✓" and R._marca("NQN ✗N") == "✗N" and R._marca("∅ ✓∅") == "✓∅" and R._marca("texto") == ""
    # 9. sem coluna de resultado na tabela → aviso, nada contado
    r = R.comparar_casos(md_a, md_d, {"faixa": [], "identidade": [], "resultado": ["ok"], "marca": "celula"})
    assert r["trocaram_lado"] == [] and "ok" in r["aviso"], r
    # 8. identidade composta: id + k; repetida sem a coluna → fora do pareamento e registrada; só de um lado registrada
    md_k = "| id | k | ok |\n|---|---|---|\n| C1 | 1 | ✓ |\n| C1 | 2 | ✓ |\n| C2 | 1 | ✓ |\n"
    md_k2 = "| id | k | ok |\n|---|---|---|\n| C1 | 1 | ✓ |\n| C1 | 2 | ✗ |\n| C3 | 1 | ✓ |\n"
    r = R.comparar_casos(md_k, md_k2, fmt)
    assert [x["id"] for x in r["trocaram_lado"]] == ["C1/2"] and r["so_antes"] == ["1:C2/1"] and r["so_depois"] == ["1:C3/1"], r
    r = R.comparar_casos(md_k, md_k2, {"faixa": [], "identidade": [], "resultado": ["ok"], "marca": "celula"})
    assert r["repetidas"] == ["1:C1"] and r["trocaram_lado"] == [] and r["pareadas"] == 0, r
    # veredito
    v = R.veredito_md(md())
    assert v["passa_tudo"] and v["resumo"] == "✓✓" and v["linhas"][1]["critério"] == "2 acerto", v
    assert R.veredito_md("# nada aqui") is None
    # 7. variantes E desenhos; estrutura desconhecida = aviso
    m, av = R.comparar_metricas({"variantes": {"Jev": {"acerto": 0.9, "p50_ms": 300}}}, {"variantes": {"Jev": {"acerto": 0.8, "p50_ms": 900}}})
    assert m == [{"metrica": "Jev/acerto", "antes": 0.9, "depois": 0.8}] and av == [], (m, av)
    m, av = R.comparar_metricas({"desenhos": {"sem": {"res": {"acerto_duro": 0.97, "brier": 0.02}}}}, {"desenhos": {"sem": {"res": {"acerto_duro": 0.95, "brier": 0.02}}}})
    assert m == [{"metrica": "sem/res/acerto_duro", "antes": 0.97, "depois": 0.95}], m
    m, av = R.comparar_metricas({"n": 3, "outra": {}}, {"n": 3})
    assert m == [] and len(av) == 2 and "desconhecida" in av[0] and "n, outra" in av[0], av
    cmp = R.comparar({"markdown": md(), "pedidos": {}, "resumo": {"variantes": {"Jev": {"acerto": 0.9}}}, "faixas": {}},
                     {"markdown": md(p2="✗"), "pedidos": {}, "resumo": {"variantes": {"Jev": {"acerto": 0.8}}}}, "compromisso-real")
    assert cmp["veredito"]["mudou"] == [{"criterio": "2 acerto", "antes": "✓", "depois": "✗", "medido": "0.900 → 0.900"}], cmp["veredito"]
    assert cmp["metricas"] == [{"metrica": "Jev/acerto", "antes": 0.9, "depois": 0.8}] and cmp["avisos"] == [], cmp
    print("7/8/9. métricas (variantes e desenhos), identidade composta, colunas de resultado: ok")


# ---------------------------------------------------------------- 3. jevcache: modelo do ambiente exige pasta própria
def testa_jevcache_ambiente():
    t = Path(tempfile.mkdtemp(prefix="jevcache-"))
    guardado = {k: os.environ.pop(k, None) for k in ("JEV_MODELO", "JEV_PASTA_CACHE")}
    try:
        j = jevcache.Jev(t / "cache")
        assert j.pasta.name == "cache" and j.modelo == jevcache.MODELO
        os.environ["JEV_MODELO"] = "jev-9.9.9"
        for ruim in (None, "cache", str((t / "cache").resolve())):
            if ruim is None:
                os.environ.pop("JEV_PASTA_CACHE", None)
            else:
                os.environ["JEV_PASTA_CACHE"] = ruim
            try:
                jevcache.Jev(t / "cache")
                raise AssertionError(f"aceitou JEV_MODELO com JEV_PASTA_CACHE={ruim!r}")
            except RuntimeError as e:
                assert "JEV_PASTA_CACHE" in str(e)
        assert not (t / "cache-x").exists()
        assert jevcache.Jev(t / "cache", modelo="explicito").modelo == "explicito"  # argumento explícito não é afetado
        os.environ["JEV_PASTA_CACHE"] = "cache-jev-9.9.9"
        j = jevcache.Jev(t / "cache")
        assert j.pasta == t / "cache-jev-9.9.9" and j.modelo == "jev-9.9.9" and j.pasta.is_dir()
        copia = t / "copia" / "cache-referencia"
        os.environ.pop("JEV_MODELO")
        os.environ["JEV_PASTA_CACHE"] = str(copia)  # caminho absoluto (referência sobre cópia)
        j = jevcache.Jev(t / "cache")
        assert j.pasta == copia and j.pasta.is_dir() and j.modelo == jevcache.MODELO
    finally:
        for k, v in guardado.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(t, ignore_errors=True)
    print("3. JEV_MODELO do ambiente exige pasta própria; absoluto aceito; explícito intocado: ok")


# ---------------------------------------------------------------- 1, 2, A: orquestração com dublê do subprocesso
def _exemplo(raiz: Path, nome: str, manifesto: bool = True, n_casos: int = 1) -> Path:
    p = raiz / nome
    (p / "cache").mkdir(parents=True)
    (p / "dados").mkdir()
    (p / "run.py").write_text("# dublê\n", encoding="utf-8")
    (p / "cache" / "a.json").write_text('{"medicao": {}, "resposta": {}}', encoding="utf-8")
    (p / "dados" / "teste.json").write_text(json.dumps({"casos": [{"id": f"T{i}"} for i in range(n_casos)]}), encoding="utf-8")
    if manifesto:
        (p / "congelamento.json").write_text("{}", encoding="utf-8")
    return p


def _registro(modo: str, **extra) -> dict:
    valor = 0.72 if modo == "gravado" else 0.68
    return {"modo": modo, "pedidos": {"k1": pedido(opt_out=noul(valor))}, "erros": [], "invalidacoes": 0, "max_429_seguidos": 0, "tokens": 100000,
            "resumo": {"n": 1, "variantes": {"Jev": {"acerto": 1.0 if modo == "gravado" else 0.0}}},
            "markdown": md() if modo == "gravado" else md(t2="revisar", ok2="✗"), "faixas": FAIXAS, **extra}


def testa_orquestracao():
    raiz = Path(tempfile.mkdtemp(prefix="reaval-"))
    local = raiz / "_local"
    try:
        for nome in ("quebra", "bom", "recusa", "suja-cache", "ref-absorvida", "ref-n-errado", "ref-invalidou", "zz-429", "zz-depois"):
            _exemplo(raiz, nome)
        _exemplo(raiz, "sem-manifesto", manifesto=False)
        (raiz / "roteador-email").mkdir()

        def executar(pasta: Path, modo: str, modelo, pasta_cache, saida_dir: Path) -> dict:
            saida_dir.mkdir(parents=True, exist_ok=True)
            if modo == "gravado":
                assert modelo is None and pasta_cache is None
                if pasta.name == "ref-absorvida":  # falha que `*_seguro` engoliu: o interceptor viu a exceção
                    return _registro(modo, erros=[{"pedido": "k1", "erro": "RuntimeError: resposta não gravada no cache"}])
                if pasta.name == "ref-n-errado":
                    return _registro(modo, resumo={"n": 7, "variantes": {}})
                if pasta.name == "ref-invalidou":
                    return _registro(modo, invalidacoes=1)
                return _registro(modo)
            if pasta.name == "quebra":
                raise RuntimeError("driver morreu")
            if pasta.name == "recusa":
                return _registro(modo, recusado="teste recusado: arquivos congelados mudaram")
            assert modelo == "jev-9.9.9" and pasta_cache == "cache-jev-9.9.9", (modelo, pasta_cache)
            (pasta / pasta_cache).mkdir(exist_ok=True)
            (pasta / pasta_cache / "b.json").write_text("{}", encoding="utf-8")  # permitido: cache novo ao lado
            if pasta.name == "suja-cache":
                (pasta / "cache" / "a.json").write_text("{}", encoding="utf-8")  # proibido: cache original
            if pasta.name == "zz-429":
                return _registro(modo, max_429_seguidos=3)
            return _registro(modo)

        elegiveis, pulados = R.listar_exemplos(raiz)
        assert elegiveis == ["bom", "quebra", "recusa", "ref-absorvida", "ref-invalidou", "ref-n-errado", "suja-cache", "zz-429", "zz-depois"], elegiveis
        assert set(pulados) == {"roteador-email", "sem-manifesto"}, pulados
        hashes = {ex: R.hash_pasta(raiz / ex, ("cache-jev-9.9.9",)) for ex in elegiveis}
        mensagens = []
        res = R.reavaliar("jev-9.9.9", elegiveis, raiz=raiz, executar=executar, local=local, log=mensagens.append)
        ex = res["exemplos"]
        # 2. referência incompleta barra o exemplo (fora da estimativa, sem rodada paga); os outros seguem
        for nome, trecho in (("ref-absorvida", "sem resposta no cache"), ("ref-n-errado", "n=7"), ("ref-invalidou", "invalidação")):
            assert ex[nome]["erro"].startswith("referência incompleta") and trecho in ex[nome]["erro"], ex[nome]["erro"]
            assert ex[nome]["depois"] is None and not ex[nome].get("estimativa")
        assert mensagens[0].startswith("estimativa (6 exemplos com referência completa") and "US$" in mensagens[0], mensagens[0]
        assert res["estimativa"]["requisicoes"] == 6
        # A. um quebra, um é recusado, os outros seguem
        assert ex["quebra"]["erro"].startswith("ao vivo falhou: RuntimeError: driver morreu"), ex["quebra"]["erro"]
        assert "recusado" in ex["recusa"]["erro"], ex["recusa"]["erro"]
        assert ex["bom"]["comparacao"]["pedidos"]["trocas"][0]["lado"] == "sim → dúvida"
        assert len(ex["bom"]["comparacao"]["casos"]["trocaram_lado"]) == 1
        assert ex["bom"]["comparacao"]["metricas"] == [{"metrica": "Jev/acerto", "antes": 1.0, "depois": 0.0}]
        # 3 erros 429 seguidos param a execução: `zz-depois` vem depois na ordem e não roda ao vivo
        assert res["parado"] and "429" in res["parado"], res["parado"]
        assert ex["zz-depois"]["depois"] is None and ex["zz-429"]["depois"] is not None
        # pasta intocada: o cache novo ao lado não muda o hash; quem sujou o cache original é denunciado
        assert ex["bom"]["intocado"] is True and ex["suja-cache"]["intocado"] is False
        assert R.hash_pasta(raiz / "bom", ("cache-jev-9.9.9",)) == hashes["bom"]
        assert (raiz / "bom" / "cache-jev-9.9.9" / "b.json").exists()
        texto = R.relatorio_md(res, pulados, "2026-10-01")
        assert "driver morreu" in texto and "sim → dúvida" in texto and "T002" in texto and "429" in texto and "ALTERAD" in texto, texto[:400]
        assert "name: reavaliacao-jev-9.9.9-2026-10-01" in texto and "referência incompleta" in texto
        # --so-estimar não chama o ao vivo; teto de custo barra antes de chamar
        chamadas = []
        res3 = R.reavaliar("jev-9.9.9", ["bom"], raiz=raiz, so_estimar=True, local=local, log=lambda *_: None,
                           executar=lambda p, modo, *a: chamadas.append(modo) or executar(p, modo, *a))
        assert chamadas == ["gravado"] and res3["exemplos"]["bom"]["depois"] is None
        chamadas.clear()
        res4 = R.reavaliar("jev-9.9.9", ["bom"], raiz=raiz, max_custo=0.001, local=local, log=lambda *_: None,
                           executar=lambda p, modo, *a: chamadas.append(modo) or executar(p, modo, *a))
        assert chamadas == ["gravado"] and "teto" in res4["parado"]
        # índice: insere uma linha e, rodando de novo, substitui em vez de duplicar
        indice = raiz / "INDICE.md"
        indice.write_text("## Evidências\n- [Medições](evidencias/medicoes-2026-10-01.md) — x\n\n## Fora\n", encoding="utf-8")
        R.atualizar_indice(indice, "evidencias/reavaliacao-x.md", "[Reavaliação x](evidencias/reavaliacao-x.md) — 1")
        R.atualizar_indice(indice, "evidencias/reavaliacao-x.md", "[Reavaliação x](evidencias/reavaliacao-x.md) — 2")
        linhas = indice.read_text(encoding="utf-8").split("\n")
        assert linhas[2] == "- [Reavaliação x](evidencias/reavaliacao-x.md) — 2" and sum("reavaliacao-x" in l for l in linhas) == 1, linhas
        print("2/A. referência incompleta barra; falha isolada; 3×429; teto; índice: ok")
    finally:
        shutil.rmtree(raiz, ignore_errors=True)


def testa_referencia_sobre_copia():
    """1. O driver real em `gravado` (subprocesso, sem chave) lê uma CÓPIA do cache: o cliente redirecionado grava e
    move na cópia; o `cache/` do exemplo-dublê fica byte a byte igual."""
    raiz = Path(tempfile.mkdtemp(prefix="reaval-copia-"))
    try:
        p = _exemplo(raiz, "duble", n_casos=1)
        comum = (AQUI.parent / "exemplos" / "_comum").resolve()
        # run.py mínimo com o contrato que o driver usa: Jev(AQUI / "cache"), secao_conjunto, main. Força uma
        # invalidação e um pedido ausente: na cópia isso move arquivos; o original não pode mudar.
        (p / "run.py").write_text(f'''
import json, sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, r"{comum}")
from jevcache import Jev
RESULTADOS = AQUI / "resultados.md"
def secao_conjunto(nome, dados):
    jev = Jev(AQUI / "cache")
    try:
        jev.perguntar({{"m": "x"}}, {{"q": {{"type": "noul"}}}})
    except RuntimeError:
        pass
    jev.invalidar({{"m": "y"}}, {{"q": {{"type": "noul"}}}})
    (jev.pasta / "escrita.json").write_text("{{}}", encoding="utf-8")  # o consumidor grava onde o cliente aponta
    return "# md\\n", {{"n": 1, "variantes": {{}}}}
def main():
    texto, _ = secao_conjunto("teste", {{}})
    RESULTADOS.write_text(texto, encoding="utf-8")
''', encoding="utf-8")
        jev = jevcache.Jev(p / "cache")
        arq = jev._arquivo({"m": "y"}, {"q": {"type": "noul"}})
        arq.write_text(json.dumps({"medicao": {"ms": 1, "input_tokens": 1, "modelo": "x", "perguntas": 1}, "resposta": {"answers": {}}}), encoding="utf-8")
        h0 = R.hash_pasta(p)
        reg = R.executar_driver(p, "gravado", None, None, raiz / "_local" / "duble" / "antes")
        assert R.hash_pasta(p) == h0, "o cache original mudou durante a referência"
        assert reg.get("excecao") is None, reg.get("excecao")
        assert reg["invalidacoes"] == 1 and len(reg["erros"]) == 1 and "não gravada" in reg["erros"][0]["erro"], (reg["invalidacoes"], reg["erros"])
        copia = raiz / "_local" / "duble" / "antes" / "cache-referencia"
        assert (copia / "invalidos").is_dir() and (copia / "escrita.json").exists() and not (p / "cache" / "escrita.json").exists()
        assert not (p / "resultados.md").exists() and (raiz / "_local" / "duble" / "antes" / "resultados.md").exists()
        assert R.referencia_completa(reg, 1) and "sem resposta" in R.referencia_completa(reg, 1)[0]
        print("1. referência lê cópia do cache (driver real): original intocado, inválidos/escritas na cópia: ok")
    finally:
        shutil.rmtree(raiz, ignore_errors=True)


if __name__ == "__main__":
    testa_pedidos()
    testa_mapa_faixas()
    testa_casos()
    testa_jevcache_ambiente()
    testa_orquestracao()
    testa_referencia_sobre_copia()
    print("bateria do arnês: tudo passou")
