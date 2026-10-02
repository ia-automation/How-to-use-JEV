"""Prepara o subconjunto do Quati (1M) para o rerank: download filtrado, BM25, sorteio com semente, top-20.

Roda ANTES de qualquer chamada ao Jev. Primeiro baixa (se faltarem) e confere pelo sha256 os arquivos pequenos da fonte
(qrels 1M, tópicos de teste, README e LICENSE do dataset — revisão do Codex, 2026-10-01: a reprodução do zero parava
antes do download); depois grava:
  .local/publicos/quati/quati_1M.subconjunto.jsonl   passagens julgadas + distratores (TEXTO: fora do Git)
  .local/publicos/rerank/consultas.json               consultas sorteadas COM texto (fora do Git)
  dados/ajuste.json, dados/teste.json                 só IDs, notas do gabarito e escore BM25 (vão para o Git)
  preparacao.json + bloco de contagens em preparacao.md

Decisões (declaradas em preparacao.md antes de olhar resultado): versão 1M; coleção = passagens julgadas +
amostra Bernoulli p=0,02 de não julgadas (semente fixa); BM25 próprio (bm25.py); elegível = ≥ 1 passagem com
nota ≥ 1 na coleção; 10 de ajuste e o resto de teste, sorteio com semente. O gabarito guardado por consulta é o
conjunto INTEIRO dos qrels dela (o ideal do NDCG usa todos); julgamento cuja passagem não esteja na coleção é
contado à parte (`ausentes_da_colecao`), nunca descartado do ideal (revisão do Codex, 2026-10-01).
Rodar: PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe exemplos/rerank-publico-ptbr/preparar.py
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
CRU = RAIZ / ".local" / "publicos" / "quati"
LOCAL_RERANK = RAIZ / ".local" / "publicos" / "rerank"
sys.path.insert(0, str(AQUI))
import bm25 as B  # noqa: E402

SEMENTE = 20261001
N_AJUSTE = 10          # o corpus tem 50 consultas julgadas: 10 de ajuste, o resto de teste (desvio declarado)
TOP_K = 20
P_DISTRATOR = 0.02     # ≈ 20 mil passagens não julgadas, sorteadas no fluxo
BASE = "https://huggingface.co/datasets/unicamp-dl/quati/resolve/main/"
URL_PASSAGENS = BASE + "quati_1M.tsv"
# Arquivos pequenos da fonte: baixados se faltarem e conferidos pelo sha256 lido em 2026-10-01 (mudou na fonte = parar).
ARQUIVOS_FONTE = {
    "qrels/quati_1M_qrels.txt": "aafab4294572a043974bcb5fccfe76e55267e37d5d76d648ab1d3697d13f6f76",
    "topics/quati_test_topics.tsv": "61936c7b582b3d9b4d47ec7ff94033841578aa2c843c31b9a54f01e3549db466",
    "README.md": "8dec16ddf7ff6722ea96cbc3d921e691782e101c46141367a7c89ea599a8103c",
    "LICENSE": "9e5f1b3c610b9c2da5c313bf81d577a7d1acec686bdb0384edefa6df0f90cd94",
}
ARQ_QRELS = CRU / "qrels__quati_1M_qrels.txt"
ARQ_TOPICOS = CRU / "topics__quati_test_topics.tsv"
ARQ_SUB = CRU / "quati_1M.subconjunto.jsonl"
MARCA_INI, MARCA_FIM = "<!-- contagens: início (gerado por preparar.py) -->", "<!-- contagens: fim -->"


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def baixar_fonte() -> None:
    """Qrels, tópicos, README e LICENSE: baixa o que falta e confere o sha256 de todos (fonte mudou = parar)."""
    CRU.mkdir(parents=True, exist_ok=True)
    for nome, esperado in ARQUIVOS_FONTE.items():
        alvo = CRU / nome.replace("/", "__")
        if not alvo.exists():
            req = urllib.request.Request(BASE + nome, headers={"User-Agent": "jev-estudo"})
            alvo.write_bytes(urllib.request.urlopen(req, timeout=120).read())
        atual = hashlib.sha256(alvo.read_bytes()).hexdigest()
        if atual != esperado:
            sys.exit(f"{alvo.name}: sha256 {atual[:16]}… ≠ o registrado em preparacao.md ({esperado[:16]}…) — a fonte mudou; "
                     "conferir e registrar antes de seguir")


def ler_qrels() -> dict[int, dict[str, int]]:
    """{query_id: {passage_id: nota}} — formato TREC `q 0 p nota`."""
    q = defaultdict(dict)
    for linha in ARQ_QRELS.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            qid, _, pid, nota = linha.split()
            q[int(qid)][pid] = int(nota)
    return dict(q)


def ler_topicos() -> dict[int, str]:
    linhas = ARQ_TOPICOS.read_text(encoding="utf-8").splitlines()[1:]  # cabeçalho `query_id\tquery`
    return {int(l.split("\t")[0]): l.split("\t", 1)[1] for l in linhas if l.strip()}


def baixar_subconjunto(julgadas: set[str]) -> dict:
    """Lê o TSV de 1M em fluxo e guarda só as passagens julgadas + distratores sorteados. Idempotente: se o
    subconjunto já existe, não baixa de novo (o relatório de transferência fica no JSON ao lado)."""
    meta_arq = ARQ_SUB.with_suffix(".meta.json")
    if ARQ_SUB.exists() and meta_arq.exists():
        return json.loads(meta_arq.read_text(encoding="utf-8"))
    rng = random.Random(SEMENTE)
    cont = Counter()
    bytes_lidos = 0
    req = urllib.request.Request(URL_PASSAGENS, headers={"User-Agent": "jev-estudo"})
    with urllib.request.urlopen(req, timeout=120) as r, ARQ_SUB.open("w", encoding="utf-8", newline="\n") as saida:
        resto = b""
        while True:
            bloco = r.read(1 << 22)
            if not bloco:
                break
            bytes_lidos += len(bloco)
            resto += bloco
            linhas = resto.split(b"\n")
            resto = linhas.pop()
            for bruta in linhas:
                cont["linhas"] += 1
                pid, _, texto = bruta.decode("utf-8").partition("\t")
                if pid in julgadas:
                    tipo = "julgada"
                elif rng.random() < P_DISTRATOR:
                    tipo = "distrator"
                else:
                    continue
                cont[tipo] += 1
                saida.write(json.dumps({"id": pid, "tipo": tipo, "texto": texto.rstrip("\r")}, ensure_ascii=False) + "\n")
    meta = {"url": URL_PASSAGENS, "bytes_transferidos": bytes_lidos, "linhas_lidas": cont["linhas"],
            "julgadas_encontradas": cont["julgada"], "distratores": cont["distrator"], "p_distrator": P_DISTRATOR,
            "bytes_gravados": ARQ_SUB.stat().st_size, "semente": SEMENTE}
    meta_arq.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


def main() -> None:
    baixar_fonte()
    qrels, topicos = ler_qrels(), ler_topicos()
    julgadas = {pid for notas in qrels.values() for pid in notas}
    meta = baixar_subconjunto(julgadas)
    passagens = [json.loads(l) for l in ARQ_SUB.open(encoding="utf-8")]
    ids = [p["id"] for p in passagens]
    indice = B.BM25([p["texto"] for p in passagens])
    presentes = set(ids)

    elegiveis, excluidas = [], {}
    for qid in sorted(topicos):
        notas = {pid: n for pid, n in qrels.get(qid, {}).items() if pid in presentes}
        if not notas:
            excluidas[qid] = "sem julgamento na coleção"
        elif max(notas.values()) < 1:
            excluidas[qid] = "nenhuma passagem com nota ≥ 1"
        else:
            elegiveis.append(qid)
    rng = random.Random(SEMENTE)
    sorteio = elegiveis[:]
    rng.shuffle(sorteio)
    partes = {"ajuste": sorted(sorteio[:N_AJUSTE]), "teste": sorted(sorteio[N_AJUSTE:])}

    def consulta(qid: int) -> dict:
        topo = indice.buscar(topicos[qid], TOP_K)
        notas = qrels[qid]
        # gabarito INTEIRO da consulta (o ideal do NDCG precisa de todos); ausentes da coleção listados à parte
        return {"query_id": qid, "gabarito": dict(notas), "ausentes_da_colecao": sorted(p for p in notas if p not in presentes),
                "top": [{"id": ids[i], "bm25": round(s, 4), "nota": notas.get(ids[i])} for i, s in topo]}

    LOCAL_RERANK.mkdir(parents=True, exist_ok=True)
    com_texto, resumo = {}, {}
    for parte, qids in partes.items():
        consultas = [consulta(q) for q in qids]
        (AQUI / "dados" / f"{parte}.json").write_text(
            json.dumps({"versao": "2026-10-01", "fonte": "Quati 1M (unicamp-dl/quati, CC BY 4.0)", "semente": SEMENTE,
                        "top_k": TOP_K, "consultas": consultas}, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        com_texto[parte] = {q: topicos[q] for q in qids}
        rel2 = [sum(1 for n in c["gabarito"].values() if n >= 2) for c in consultas]
        rel2_top = [sum(1 for t in c["top"] if (t["nota"] or 0) >= 2) for c in consultas]
        resumo[parte] = {"n": len(qids), "ids_sha256": sha(qids),
                         "relevantes_nota>=2_no_gabarito": sum(rel2), "relevantes_nota>=2_no_top20": sum(rel2_top),
                         "consultas_sem_relevante_no_top20": sum(1 for r in rel2_top if r == 0),
                         "julgamentos_ausentes_da_colecao": sum(len(c["ausentes_da_colecao"]) for c in consultas),
                         "nao_julgadas_no_top20": sum(1 for c in consultas for t in c["top"] if t["nota"] is None),
                         "trechos_no_top20": sum(len(c["top"]) for c in consultas)}
    (LOCAL_RERANK / "consultas.json").write_text(json.dumps(com_texto, ensure_ascii=False, indent=1), encoding="utf-8")
    saida = {"semente": SEMENTE, "download": meta, "colecao": {"passagens": len(ids), "julgadas": sum(p["tipo"] == "julgada" for p in passagens),
             "distratores": sum(p["tipo"] == "distrator" for p in passagens), "sha256_ids": sha(sorted(ids))},
             "qrels_sha256": hashlib.sha256(ARQ_QRELS.read_bytes()).hexdigest(),
             "topicos_sha256": hashlib.sha256(ARQ_TOPICOS.read_bytes()).hexdigest(),
             "elegiveis": len(elegiveis), "excluidas": excluidas, "ids": partes, "partes": resumo,
             "bm25": {"k1": B.K1, "b": B.B, "top_k": TOP_K}}
    (AQUI / "preparacao.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    bloco = markdown(saida)
    md = (AQUI / "preparacao.md").read_text(encoding="utf-8")
    ini, fim = md.index(MARCA_INI) + len(MARCA_INI), md.index(MARCA_FIM)
    (AQUI / "preparacao.md").write_text(md[:ini] + "\n" + bloco + "\n" + md[fim:], encoding="utf-8", newline="\n")
    print(bloco)


def markdown(s: dict) -> str:
    d, c = s["download"], s["colecao"]
    L = ["## Contagens (geradas por `preparar.py`, antes da API)", "",
         f"- Download em fluxo: {d['bytes_transferidos'] / 1e6:.0f} MB transferidos ({d['linhas_lidas']} linhas); gravados "
         f"{d['bytes_gravados'] / 1e6:.1f} MB em `.local/publicos/quati/quati_1M.subconjunto.jsonl` "
         f"({d['julgadas_encontradas']} julgadas + {d['distratores']} distratores, p = {d['p_distrator']}).",
         f"- Coleção da busca: **{c['passagens']}** passagens ({c['julgadas']} julgadas, {c['distratores']} distratores); "
         f"sha256 dos IDs `{c['sha256_ids'][:16]}…`; qrels sha256 `{s['qrels_sha256'][:16]}…`; tópicos `{s['topicos_sha256'][:16]}…`.",
         f"- BM25 k1 = {s['bm25']['k1']}, b = {s['bm25']['b']}, top-{s['bm25']['top_k']}. Elegíveis **{s['elegiveis']}** de 50; "
         f"excluídas {s['excluidas'] or 'nenhuma'}.", "",
         "| parte | n | relevantes (nota ≥ 2) no gabarito | no top-20 do BM25 | consultas sem relevante no top-20 (teto) | não julgadas no top-20 | sha256 dos IDs |",
         "|---|---|---|---|---|---|---|"]
    for parte, r in s["partes"].items():
        L.append(f"| {parte} | {r['n']} | {r['relevantes_nota>=2_no_gabarito']} | {r['relevantes_nota>=2_no_top20']} | "
                 f"{r['consultas_sem_relevante_no_top20']} | {r['nao_julgadas_no_top20']}/{r['trechos_no_top20']} | `{r['ids_sha256'][:16]}…` |")
    aus = {p: r["julgamentos_ausentes_da_colecao"] for p, r in s["partes"].items()}
    L.append(f"\nJulgamentos cuja passagem NÃO está na coleção (ficam no ideal do NDCG, contados à parte): {aus}.")
    L.append(f"\nIDs: ajuste {s['ids']['ajuste']} · teste {s['ids']['teste']}")
    return "\n".join(L)


if __name__ == "__main__":
    main()
