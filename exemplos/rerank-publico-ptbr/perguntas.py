"""Perguntas e critério do rerank — o ÚNICO arquivo que um humano precisa revisar.

Uma consulta (pt-BR) e um trecho (pt-BR) viram UM state `{"query", "passage"}` e UM Noul: "o trecho responde à
consulta?". O código (`rerank.py`) reordena os 20 primeiros do BM25 pela probabilidade do Noul, com desempate pelo
escore do BM25. Não há limiar: a ordem é o produto. A escala do gabarito (Quati, 0–3) chama de "answers the
question" as notas 2 e 3; o `true` do Noul descreve exatamente isso, e o `false` cobre a nota 1 ("pertence ao
tema, mas não responde") — a fronteira que o BM25 não vê.

Variantes medidas à parte:
- `PERGUNTA_PT`: a mesma pergunta em português (só no ajuste; NÚCLEO §9: inglês é o idioma principal).
- `perguntas_lote(n)`: os 20 trechos num state `{"query", "passages": [{"id", "text"}…]}` e um Noul por trecho
  apontando `passages[i].text` — uma requisição por consulta em vez de 20 (custo escondido do busca-imoveis).

Afinação (ajuste, 10 consultas × 20 trechos): registrada em resultados.md e no README; nenhuma mudança depois
do congelamento.
"""

TETO_CARACTERES_TRECHO = 4000   # os trechos do Quati têm ~1.000 caracteres; acima disso não vai ao Jev (falha → ordem do BM25)
TETO_CARACTERES_CONSULTA = 500


def _noul(instrucao: str, sim: str, nao: str) -> dict:
    return {"type": "noul", "instructions": instrucao, "criteria": {"true": sim, "false": nao}}


# State por trecho: {"query": "<consulta>", "passage": "<trecho>"}
PERGUNTA_EN = {"answers": _noul(
    "The text in `passage` answers the question asked in `query`. Both are in Brazilian Portuguese.",
    "The passage states the information that answers the question — the fact, list, reason, date, place or "
    "procedure asked for — even if it also contains unrelated content or lacks clarity.",
    "The passage does not answer the question: it is about the same topic but gives no answer (only mentions "
    "the subject, discusses something adjacent, or asks the question without answering it), or it is about "
    "something else entirely.",
)}

# A mesma pergunta em português (variante medida só no ajuste).
PERGUNTA_PT = {"answers": _noul(
    "O texto em `passage` responde à pergunta feita em `query`.",
    "O trecho traz a informação que responde à pergunta — o fato, a lista, o motivo, a data, o lugar ou o "
    "procedimento pedido —, mesmo que também contenha conteúdo não relacionado ou falte clareza.",
    "O trecho não responde à pergunta: é sobre o mesmo tema mas não dá a resposta (só menciona o assunto, "
    "fala de algo próximo, ou repete a pergunta sem responder), ou é sobre outra coisa.",
)}


def perguntas_lote(n: int) -> dict:
    """n Nouls no mesmo state `{"query", "passages": [{"id", "text"}…]}`, um por posição (isoladas entre si)."""
    return {f"p{i}": _noul(
        f"The text in `passages[{i}].text` answers the question asked in `query`. Both are in Brazilian Portuguese.",
        PERGUNTA_EN["answers"]["criteria"]["true"],
        PERGUNTA_EN["answers"]["criteria"]["false"],
    ) for i in range(n)}


# Critério de continuar/descartar — fixado em 2026-10-01 ANTES de abrir dados/teste.json; entra no manifesto.
# "Ganho" = Δ NDCG@10 pareado por consulta (BM25 → Jev menos BM25 puro), média sobre as consultas de teste,
# intervalo de 95% por bootstrap (1.000 reamostras, semente fixa) sobre as consultas.
CRITERIO_CONTINUAR = {
    "onde": "no teste (as consultas sorteadas de teste), rerank por trecho em inglês sobre o top-20 do BM25",
    "1_ganho_ndcg": "Δ NDCG@10 (Jev − BM25) médio ≥ 0,05 E limite inferior do intervalo de 95% > 0",
    "2_custo": "custo do Jev ≤ US$ 2,00 por mil consultas (20 requisições por consulta, preço de entrada)",
    "3_latencia": "p95 por requisição ≤ 1.200 ms, medido na chamada real (8 em paralelo)",
    "secundario_nao_decide": "Δ MRR@10 (nota ≥ 2) com intervalo que não cruza zero; Jev ≥ baseline de sobreposição em NDCG@10; "
                             "variante 'lote' (20 trechos num state) relatada ao lado, sem decidir",
    "se_falhar": "1 falhando = o Noul por trecho não paga a chamada neste corpus; 2 ou 3 falhando = reler em lote ou indexar na ingestão",
    "limites": {"ganho_ndcg_min": 0.05, "custo_por_mil_max_us": 2.0, "p95_ms_max": 1200},
}
