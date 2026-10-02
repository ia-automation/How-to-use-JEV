"""Critério da comparação Jev × LLM — fixado em 2026-10-01 ANTES de qualquer chamada ao LLM; entra no manifesto
`congelamento.json` (mudar isto exige congelar de novo).

O relatório tem de dizer, por exemplo, onde o LLM GANHA, EMPATA ou PERDE na métrica principal e no erro caro, com a
diferença e o n — e a razão custo/latência Jev × LLM. "O Jev é melhor" sem diferença e n não é veredito.
"""

# Diferença mínima, em CASOS, para sair de "empate" na métrica principal. Com n = 60–73, 3 casos ≈ 4–5 p.p.; abaixo disso
# a diferença cabe na variação entre rodadas (NÚCLEO §6) e numa única rodada do LLM a temperatura 0.
EMPATE_CASOS = 3

CRITERIO = {
    "fixado_em": "2026-10-01, antes da primeira chamada ao LLM",
    "lado_a_lado": "mesmo teste congelado (hash do manifesto de cada exemplo conferido), mesmas instructions/criteria/opções "
                   "de perguntas.py serializadas em JSON, mesma validação estrita, mesma regra de decisão do módulo do exemplo "
                   "(respostas do LLM injetadas no lugar das do Jev: Noul true/false → 1,0/0,0; Choice → one-hot), mesmo baseline",
    "metrica_principal": (f"LLM ganha se acerta ≥ {EMPATE_CASOS} casos a mais que o Jev; perde se ≥ {EMPATE_CASOS} a menos; "
                          "senão empata. Falha operacional do LLM conta como erro (como `revisar`) e é reportada à parte"),
    "erro_caro": "contagem absoluta: LLM ganha se tem MENOS erros caros que o Jev, perde se tem MAIS, empata se igual "
                 "(erro caro é raro: cada caso conta)",
    "custo_latencia": "razão = US$ por mil casos do LLM ÷ do Jev (tokens de entrada + saída ao preço publicado, "
                      "input US$ 1,00/M e output US$ 5,00/M em 2026-10-01; Jev US$ 0,042/M só entrada); latência = p50 do "
                      "LLM ÷ p50 do Jev, as duas medidas na chamada real (Jev com 8 em paralelo na rodada original; LLM em série)",
    "concordancia": "fração dos casos em que a decisão final do Jev e a do LLM são iguais (ação+tipo / grupo+folha+revisar / "
                    "relação); informativa, não decide",
    "exemplos": {
        "opt-out-lgpd": {"n": 60, "metrica_principal": "acerto da ação (5 classes)",
                         "erro_caro": "infração + obrigação pela metade + bloqueio indevido (os três somados; cada um reportado)",
                         "baseline": "lista de expressões (optout.baseline)"},
        "motivo-de-perda": {"n": 68, "metrica_principal": "acerto folgado (folha ∈ aceitáveis ou só-grupo certo; revisão e falha = erro), variante c",
                            "erro_caro": "motivo inventado + grupo errado automatizado (contados juntos, como no exemplo)",
                            "baseline": "palavra-chave por folha (motivo.baseline)"},
        "auditor-de-evidencia": {"n": 73, "metrica_principal": "acerto da relação (revisa = erro)",
                                 "erro_caro": "falsa aprovação (gabarito não sustentado → supported)",
                                 "baseline": "palavra-chave + regex de falha (auditor.baseline)"},
    },
    "o_que_nao_conclui": "um fornecedor, um modelo barato (Haiku 4.5), uma rodada, temperatura 0, prompt sem exemplos e sem "
                         "raciocínio pedido; dados sintéticos do mesmo fornecedor do LLM. Nada aqui mede o topo da linha nem "
                         "o que um prompt afinado faria.",
    "limites": {"empate_casos": EMPATE_CASOS},
}
