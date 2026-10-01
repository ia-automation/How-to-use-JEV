"""Prepara R5 (HateBR) e R4 (B2W-Reviews01) segundo PROTOCOLO.md: elegíveis, deduplicação, divisão por grupo.

Roda ANTES de qualquer chamada à API e publica as contagens e o custo máximo estimado
(`preparacao.md` + `preparacao.json`, só agregados, IDs e hashes). As listas COM TEXTO vão só para
`.local/publicos/divisoes/` — o texto é licenciado (CC BY-NC / BY-NC-SA) e não entra no repositório.

Regras (congeladas no protocolo; as escolhas que o protocolo deixou abertas estão declaradas aqui):
- Entrada ao Jev: HateBR `comentario`; B2W `review_title` + `review_text`. Nada mais.
- Chave de duplicata EXATA = texto NFC com espaços colapsados; APROXIMADA = a exata sem pontuação
  (categoria Unicode P*) e sem caixa. Uma chave aproximada aparece em no máximo UMA amostra
  (ajuste OU teste) e uma vez só. Declarado: não se une grupo por duplicata na população inteira —
  no B2W, avaliação curta genérica ("ótimo produto") liga milhares de produtos num componente só;
  o vazamento que importa é entre as duas AMOSTRAS (o ajuste afina perguntas e treina baselines).
- Grupos: HateBR por `links_post`; B2W por `product_id`. Os grupos são embaralhados com semente e
  metade vai para o lado do ajuste, metade para o do teste; cada amostra sai só do seu lado.
- Prevalência natural: amostra aleatória simples dentro do lado (sem estratificar por classe).
- Duplicata com gabarito divergente NÃO é excluída: cada item fica com o próprio rótulo (declarado;
  contado no relatório).

Rodar: .venv/Scripts/python.exe avaliar/publicos/preparar.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
CRU = RAIZ / ".local" / "publicos"
DIVISOES = CRU / "divisoes"

SEMENTE = 20260930
N_AJUSTE, N_TESTE = 100, 300
# Teto de custo declarado ANTES da API: até 8 versões de perguntas no ajuste + 1 rodada de teste,
# +20% de margem para repetição por erro operacional. Tokens por requisição estimados por excesso.
VERSOES_MAX_AJUSTE = 8
MARGEM_REPETICAO = 1.20
TOKENS_FIXOS_POR_REQUISICAO = 700  # perguntas longas com critério (~300 medidos p/ 1 Noul curto) — excesso
CARACTERES_POR_TOKEN = 3.0  # português ~3,5–4; 3 superestima de propósito
PRECO_US_POR_MILHAO = 0.042

csv.field_size_limit(10**9)


def chave_exata(texto: str) -> str:
    """NFC + espaços colapsados: duas cópias do mesmo texto com espaçamento diferente viram uma."""
    return " ".join(unicodedata.normalize("NFC", texto).split())


def chave_aprox(texto: str) -> str:
    """Sem pontuação (Unicode P*) e sem caixa. Texto só de pontuação cai na chave exata."""
    exata = chave_exata(texto)
    sem = "".join(c for c in exata.casefold() if not unicodedata.category(c).startswith("P"))
    sem = " ".join(sem.split())
    return sem or exata


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def sha_arquivo(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------ leitura
def ler_hatebr() -> tuple[list[dict], Counter]:
    excl = Counter()
    itens = []
    with (CRU / "HateBR.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            texto = r["comentario"]
            votos = [r["anotator1"], r["anotator2"], r["anotator3"]]
            if not texto.strip():
                excl["comentário vazio"] += 1
                continue
            if r["label_final"] not in ("0", "1") or any(v not in ("0", "1") for v in votos):
                excl["rótulo ou voto inválido"] += 1
                continue
            votos = [int(v) for v in votos]
            itens.append({
                "id": int(r["id"]), "grupo": r["links_post"], "texto": texto,
                "gold": int(r["label_final"]), "votos": votos,
                "estrato": "unanime" if len(set(votos)) == 1 else "disputado",
            })
    return itens, excl


def ler_b2w() -> tuple[list[dict], Counter]:
    """ID = índice da linha de dados (0 = primeira depois do cabeçalho): o B2W não traz ID de avaliação."""
    excl = Counter()
    itens = []
    with (CRU / "B2W-Reviews01.csv").open(encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f)):
            titulo, corpo = r["review_title"] or "", r["review_text"] or ""
            if r["recommend_to_a_friend"] not in ("Yes", "No"):
                excl["recommend_to_a_friend vazio/ inválido"] += 1
                continue
            if r["overall_rating"] not in ("1", "2", "3", "4", "5"):
                excl["overall_rating inválido"] += 1
                continue
            if not (titulo.strip() or corpo.strip()):
                excl["título e texto vazios"] += 1
                continue
            itens.append({
                "id": i, "grupo": r["product_id"], "titulo": titulo, "corpo": corpo,
                "texto": f"{titulo}\n{corpo}",  # só para a chave de duplicata; o Jev recebe os dois campos
                "gold": 1 if r["recommend_to_a_friend"] == "Yes" else 0,
                "nota": int(r["overall_rating"]),
            })
    return itens, excl


# ------------------------------------------------------------------------------------------ divisão
def dividir(itens: list[dict]) -> dict:
    for it in itens:
        it["chave"] = hashlib.sha256(chave_aprox(it["texto"]).encode()).hexdigest()[:16]
    grupos = sorted({it["grupo"] for it in itens})
    rng = random.Random(SEMENTE)
    rng.shuffle(grupos)
    lado_ajuste = set(grupos[: len(grupos) // 2])

    def amostrar(pool: list[dict], n: int, proibidas: set) -> list[dict]:
        pool = sorted(pool, key=lambda x: x["id"])
        rng.shuffle(pool)
        tomadas, saida = set(proibidas), []
        for it in pool:
            if it["chave"] in tomadas:
                continue
            tomadas.add(it["chave"])
            saida.append(it)
            if len(saida) == n:
                break
        return saida

    pool_aj = [it for it in itens if it["grupo"] in lado_ajuste]
    pool_te = [it for it in itens if it["grupo"] not in lado_ajuste]
    ajuste = amostrar(pool_aj, N_AJUSTE, set())
    teste = amostrar(pool_te, N_TESTE, {it["chave"] for it in ajuste})
    chaves_teste = {it["chave"] for it in teste}
    # Regime "mais dados" do baseline supervisionado: todo o lado do ajuste, sem chave que esteja no teste.
    treino_amplo = [it for it in pool_aj if it["chave"] not in chaves_teste]
    return {"ajuste": ajuste, "teste": teste, "treino_amplo": treino_amplo,
            "grupos": {"total": len(grupos), "lado_ajuste": len(lado_ajuste), "lado_teste": len(grupos) - len(lado_ajuste)},
            "pool": {"ajuste": len(pool_aj), "teste": len(pool_te)}}


def duplicatas(itens: list[dict]) -> dict:
    exatas = Counter(chave_exata(it["texto"]) for it in itens)
    aprox = defaultdict(list)
    for it in itens:
        aprox[chave_aprox(it["texto"])].append(it["gold"])
    return {
        "itens_em_duplicata_exata": sum(c for c in exatas.values() if c > 1),
        "grupos_de_duplicata_exata": sum(1 for c in exatas.values() if c > 1),
        "itens_em_duplicata_aproximada": sum(len(v) for v in aprox.values() if len(v) > 1),
        "grupos_de_duplicata_aproximada": sum(1 for v in aprox.values() if len(v) > 1),
        "grupos_aprox_com_gabarito_divergente": sum(1 for v in aprox.values() if len(v) > 1 and len(set(v)) > 1),
        "textos_unicos_aprox": len(aprox),
    }


def custo_max(amostras: list[list[dict]]) -> dict:
    todos = [it for a in amostras for it in a]
    chars = statistics.mean(len(it["texto"]) for it in todos)
    tok = TOKENS_FIXOS_POR_REQUISICAO + chars / CARACTERES_POR_TOKEN
    req = (VERSOES_MAX_AJUSTE * N_AJUSTE + N_TESTE) * MARGEM_REPETICAO
    return {"requisicoes_max": round(req), "tokens_por_requisicao_est": round(tok),
            "tokens_max": round(req * tok), "custo_max_us": round(req * tok / 1e6 * PRECO_US_POR_MILHAO, 4)}


def resumo_amostra(a: list[dict], corpus: str) -> dict:
    r = {"n": len(a), "grupos": len({it["grupo"] for it in a}),
         "positivos": sum(it["gold"] for it in a), "prevalencia_positiva": round(sum(it["gold"] for it in a) / len(a), 3),
         "ids_sha256": sha(sorted(it["id"] for it in a))}
    if corpus == "hatebr":
        r["estratos"] = dict(Counter(it["estrato"] for it in a))
    else:
        r["notas"] = {str(k): v for k, v in sorted(Counter(it["nota"] for it in a).items())}
    return r


def gravar_local(nome: str, itens: list[dict]) -> None:
    DIVISOES.mkdir(parents=True, exist_ok=True)
    with (DIVISOES / f"{nome}.jsonl").open("w", encoding="utf-8") as f:
        for it in itens:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def main() -> None:
    saida = {"semente": SEMENTE, "protocolo_sha256": sha_arquivo(AQUI / "PROTOCOLO.md"), "corpora": {}}
    for corpus, leitor, arquivo, alvo in (("hatebr", ler_hatebr, "HateBR.csv", "ofensivo (label_final=1)"),
                                          ("b2w", ler_b2w, "B2W-Reviews01.csv", "recomendaria (Yes)")):
        itens, excl = leitor()
        d = dividir(itens)
        for parte in ("ajuste", "teste", "treino_amplo"):
            gravar_local(f"{corpus}-{parte}", d[parte])
        pop = {"elegiveis": len(itens), "excluidos": dict(excl),
               "positivos": sum(it["gold"] for it in itens),
               "prevalencia_positiva": round(sum(it["gold"] for it in itens) / len(itens), 4)}
        if corpus == "hatebr":
            pop["estratos"] = dict(Counter(it["estrato"] for it in itens))
            pop["gold_diverge_da_maioria_dos_votos"] = sum(
                1 for it in itens if (sum(it["votos"]) >= 2) != bool(it["gold"]))
        else:
            pop["notas"] = {str(k): v for k, v in sorted(Counter(it["nota"] for it in itens).items())}
        saida["corpora"][corpus] = {
            "arquivo": arquivo, "arquivo_sha256": sha_arquivo(CRU / arquivo), "classe_positiva": alvo,
            "populacao": pop, "duplicatas": duplicatas(itens), "grupos": d["grupos"], "pool": d["pool"],
            "ajuste": resumo_amostra(d["ajuste"], corpus), "teste": resumo_amostra(d["teste"], corpus),
            "treino_amplo": {"n": len(d["treino_amplo"]), "ids_sha256": sha(sorted(it["id"] for it in d["treino_amplo"]))},
            "ids": {"ajuste": sorted(it["id"] for it in d["ajuste"]), "teste": sorted(it["id"] for it in d["teste"])},
            "custo_estimado": custo_max([d["ajuste"], d["teste"]]),
        }
    total = sum(c["custo_estimado"]["custo_max_us"] for c in saida["corpora"].values())
    saida["custo_max_total_us"] = round(total, 4)
    (AQUI / "preparacao.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    (AQUI / "preparacao.md").write_text(markdown(saida), encoding="utf-8")
    print(markdown(saida))


def markdown(s: dict) -> str:
    L = ["# Preparação R4/R5 — contagens e custo máximo (gerado por `preparar.py`, ANTES da API)", "",
         f"Semente `{s['semente']}` · protocolo sha256 `{s['protocolo_sha256'][:16]}…` · "
         f"custo máximo estimado total **US$ {s['custo_max_total_us']}**. Só agregados, IDs e hashes; "
         "o texto licenciado fica em `.local/publicos/divisoes/`.", ""]
    for nome, c in s["corpora"].items():
        p, d = c["populacao"], c["duplicatas"]
        L += [f"## {nome} — `{c['arquivo']}` (sha256 `{c['arquivo_sha256'][:16]}…`)", "",
              f"- Elegíveis **{p['elegiveis']}**; excluídos {p['excluidos'] or 'nenhum'}; classe positiva = {c['classe_positiva']}, "
              f"prevalência {p['prevalencia_positiva']} ({p['positivos']})."]
        if "estratos" in p:
            L.append(f"- Estratos na população: {p['estratos']}; gold diferente da maioria dos votos: {p['gold_diverge_da_maioria_dos_votos']}.")
        if "notas" in p:
            L.append(f"- Notas na população: {p['notas']}.")
        L += [f"- Duplicatas: exatas {d['itens_em_duplicata_exata']} itens em {d['grupos_de_duplicata_exata']} grupos; "
              f"aproximadas {d['itens_em_duplicata_aproximada']} itens em {d['grupos_de_duplicata_aproximada']} grupos "
              f"({d['grupos_aprox_com_gabarito_divergente']} grupos com gabarito divergente); textos únicos {d['textos_unicos_aprox']}.",
              f"- Grupos: {c['grupos']['total']} ({c['grupos']['lado_ajuste']} no lado do ajuste, {c['grupos']['lado_teste']} no do teste); "
              f"itens por lado {c['pool']}.", ""]
        L += ["| amostra | n | grupos | positivos | prevalência | extra | sha256 dos IDs |", "|---|---|---|---|---|---|---|"]
        for parte in ("ajuste", "teste"):
            a = c[parte]
            extra = a.get("estratos") or a.get("notas")
            L.append(f"| {parte} | {a['n']} | {a['grupos']} | {a['positivos']} | {a['prevalencia_positiva']} | {extra} | `{a['ids_sha256'][:16]}…` |")
        L.append(f"| treino_amplo (outro regime do baseline) | {c['treino_amplo']['n']} | | | | | `{c['treino_amplo']['ids_sha256'][:16]}…` |")
        e = c["custo_estimado"]
        L += ["", f"Custo máximo: {e['requisicoes_max']} requisições × ~{e['tokens_por_requisicao_est']} tokens = "
              f"{e['tokens_max']} tokens → **US$ {e['custo_max_us']}** (até {VERSOES_MAX_AJUSTE} versões no ajuste + teste 1×, "
              f"+{round((MARGEM_REPETICAO - 1) * 100)}% de repetição).", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
