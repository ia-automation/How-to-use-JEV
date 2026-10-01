"""Mede o efeito do idioma da MENSAGEM (pt-BR × inglês) no Jev, com a pergunta idêntica em inglês.

Conjunto: casos-pt-en.json (40 pares, escritos pelo Codex; protocolo dentro do arquivo).
Uma mensagem + uma pergunta por requisição; ordem pt/en alternada por par; REPETICOES rodadas.
Gera resultados-pt-en.md. Rodar: ../.venv/Scripts/python rodar_pt_en.py  (JEV_MODO=gravado sem chave)
"""
import json
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "exemplos" / "_comum"))
from jevcache import Jev  # noqa: E402  (infra comum fica fora deste pacote)
from metricas import brier  # noqa: E402

REPETICOES = 2
IDIOMAS = ("pt-BR", "en")
CORTE_NOUL = 0.5  # corte ILUSTRATIVO para acurácia (declarado antes da rodada, não aprovado para produção)

dados = json.loads((AQUI / "casos-pt-en.json").read_text(encoding="utf-8"))
casos = dados["cases"]
jev = Jev(AQUI / "cache")

# pedidos: (caso, idioma, repetição). Repetição entra no state? NÃO — o cache é por (state, pergunta);
# para medir variação entre chamadas idênticas usamos a pasta de cache por repetição.
respostas = {}
for rep in range(REPETICOES):
    j = Jev(AQUI / "cache" / f"rep{rep}")
    pedidos, chaves = [], []
    for i, c in enumerate(casos):
        ordem = IDIOMAS if (i + rep) % 2 == 0 else IDIOMAS[::-1]  # contrabalança o idioma que roda primeiro
        for idioma in ordem:
            pedidos.append(({"message": c["message"][idioma]}, {"judge": c["question"]}))
            chaves.append((c["id"], idioma, rep))
    for chave, r in zip(chaves, j.perguntar_varios(pedidos, paralelo=8)):
        respostas[chave] = r["answers"]["judge"]
    jev.chamadas += j.chamadas


def valor(a):
    return {"noul": a.get("noul"), "choice": a.get("choice"), "score": a.get("score")}[a["type"]]


linhas_md, por_tipo = [], {"noul": [], "choice": [], "score": []}
for c in casos:
    for rep in range(REPETICOES):
        pt, en = respostas[(c["id"], "pt-BR", rep)], respostas[(c["id"], "en", rep)]
        por_tipo[c["primitive"]].append((c, rep, pt, en))


def media(xs):
    xs = [x for x in xs if x is not None]
    return statistics.mean(xs) if xs else float("nan")


saida = ["# Português × inglês no Jev — resultados", "",
         f"Conjunto `{dados['dataset_id']}` (Codex, sintético): 40 pares, pergunta idêntica em inglês; "
         f"só a mensagem muda de idioma. {REPETICOES} repetições. Modelo: {jev.resumo().get('modelos')}.", ""]

# Noul
itens = por_tipo["noul"]
sup = [(c, r, pt, en) for c, r, pt, en in itens if c["gold"] is not None]
b_pt = brier([(pt["noul"], c["gold"]) for c, _, pt, _ in sup])
b_en = brier([(en["noul"], c["gold"]) for c, _, _, en in sup])
a_pt = media([(pt["noul"] >= CORTE_NOUL) == c["gold"] for c, _, pt, _ in sup])
a_en = media([(en["noul"] >= CORTE_NOUL) == c["gold"] for c, _, _, en in sup])
dif = media([abs(pt["noul"] - en["noul"]) for _, _, pt, en in itens])
saida += ["## Noul", f"- Brier pt {b_pt:.3f} · en {b_en:.3f} (menor é melhor) — n={len(sup)} (casos×repetições com gabarito)",
          f"- Acerto no corte ilustrativo {CORTE_NOUL}: pt {a_pt:.1%} · en {a_en:.1%}",
          f"- Diferença média |p_pt − p_en| no mesmo caso: {dif:.3f}", ""]

# Choice
itens = por_tipo["choice"]
sup = [(c, r, pt, en) for c, r, pt, en in itens if c["gold"] is not None]
saida += ["## Choice",
          f"- Acerto pt {media([pt['choice'] == c['gold'] for c, _, pt, _ in sup]):.1%} · "
          f"en {media([en['choice'] == c['gold'] for c, _, _, en in sup]):.1%} — n={len(sup)}",
          f"- Vencedor diferente entre idiomas: {media([pt['choice'] != en['choice'] for _, _, pt, en in itens]):.1%}",
          f"- Confiança média pt {media([pt['confidence'] for _, _, pt, _ in itens]):.2f} · "
          f"en {media([en['confidence'] for _, _, _, en in itens]):.2f}", ""]

# Score
itens = por_tipo["score"]
sup = [(c, r, pt, en) for c, r, pt, en in itens if c["gold"] is not None]
saida += ["## Score",
          f"- Erro absoluto médio ao nível de referência: pt {media([abs(pt['score'] - c['gold']) for c, _, pt, _ in sup]):.2f} · "
          f"en {media([abs(en['score'] - c['gold']) for c, _, _, en in sup]):.2f} — n={len(sup)}",
          f"- Nível arredondado = referência: pt {media([round(pt['score']) == c['gold'] for c, _, pt, _ in sup]):.1%} · "
          f"en {media([round(en['score']) == c['gold'] for c, _, _, en in sup]):.1%}",
          f"- Diferença média |score_pt − score_en|: {media([abs(pt['score'] - en['score']) for _, _, pt, en in itens]):.2f}", ""]

# Variação entre repetições idênticas
var = []
for c in casos:
    for idioma in IDIOMAS:
        a0, a1 = respostas[(c["id"], idioma, 0)], respostas[(c["id"], idioma, 1)]
        if c["primitive"] == "choice":
            var.append(float(a0["choice"] != a1["choice"]))
        else:
            var.append(abs(valor(a0) - valor(a1)))
saida += ["## Estabilidade (mesma requisição, 2 chamadas)",
          f"- Variação média entre repetições (|Δ| em Noul/Score; troca de vencedor em Choice): {media(var):.3f}", ""]

# Casos com erro ou divergência forte
saida += ["## Casos para olhar (erro em algum idioma ou divergência pt × en)", "",
          "| caso | tipo | gabarito | pt | en | tags |", "|---|---|---|---|---|---|"]
for c in casos:
    pt, en = respostas[(c["id"], "pt-BR", 0)], respostas[(c["id"], "en", 0)]
    g = c["gold"]
    if c["primitive"] == "noul":
        errou = g is not None and ((pt["noul"] >= CORTE_NOUL) != g or (en["noul"] >= CORTE_NOUL) != g)
        forte = abs(pt["noul"] - en["noul"]) >= 0.3
    elif c["primitive"] == "choice":
        errou = g is not None and (pt["choice"] != g or en["choice"] != g)
        forte = pt["choice"] != en["choice"]
    else:
        errou = g is not None and (round(pt["score"]) != g or round(en["score"]) != g)
        forte = abs(pt["score"] - en["score"]) >= 0.75
    if errou or forte or g is None:
        saida.append(f"| {c['id']} | {c['primitive']} | {g} | {valor(pt)} | {valor(en)} | {', '.join(c.get('tags', []))} |")

r = jev.resumo()
saida += ["", "## Custo e latência",
          f"- {r['requisicoes']} requisições ({r['do_cache']} do cache) · p50 {r['latencia_p50_ms']} ms · "
          f"p95 {r['latencia_p95_ms']} ms · {r['input_tokens']} tokens · US$ {r['custo_us']}",
          "", "Limites: dados sintéticos escritos por um LLM; tradução sem revisão independente; mede só o "
          "idioma da mensagem (perguntas em português são outro experimento)."]
(AQUI / "resultados-pt-en.md").write_text("\n".join(saida) + "\n", encoding="utf-8")
print("\n".join(saida))
