"""Roda a comparação Jev × LLM nos três testes congelados e gera `resultados.md` sozinho.

Uso:
  python run.py congelar     grava o manifesto `congelamento.json` (hash deste código, de llmcache.py, do código e do
                             teste.json de cada exemplo comparado, mais o critério) — ANTES de qualquer chamada ao LLM
  python run.py rascunho     encanamento: 2 casos do rascunho de cada exemplo (6 chamadas) → resultados-rascunho.md; não é métrica
  python run.py              o teste dos três exemplos; só roda com o manifesto batendo e com o manifesto de CADA exemplo
                             batendo (dado intocado). A PRIMEIRA execução grava `resultados-rodada1.md` e nunca o reescreve
  LLM_MODO=gravado python run.py   reproduz tudo do cache (`cache-llm/`), sem chave
O Jev é SEMPRE lido do cache do exemplo (0 chamadas). Chamadas ao LLM em série, com teto total de ORCAMENTO tentativas
HTTP persistido em `orcamento.json` (não reinicia por execução; retry conta); falha já registrada é reproduzida também em
`auto` (refazer: LLM_REFAZER_INVALIDAS=1); 429 em três tentativas seguidas interrompe o lote (e o relatório não é gerado).
"""
from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import comparar as C  # noqa: E402
import congelamento as CG  # noqa: E402
import criterio as CR  # noqa: E402
import llmcache as L  # noqa: E402
from llmcache import LoteInterrompido  # noqa: E402

RESULTADOS = AQUI / "resultados.md"
RODADA1 = AQUI / "resultados-rodada1.md"
ORCAMENTO = 250        # tentativas HTTP ao LLM, no total, retries incluídos — consumo persistido em `orcamento.json`
ARQUIVO_ORCAMENTO = AQUI / "orcamento.json"
# Qual rodada este código gera (o cache é sempre o da rodada 1; a 1 está preservada em resultados-rodada1.md).
RODADA = "rodada 2 — pós-revisão do Codex (2026-10-01), NÃO cega, reproduzida do cache da rodada 1 sem chamada nova"
CASOS_RASCUNHO = 2     # por exemplo
# Manifesto: este código, o cliente do LLM, e — por exemplo comparado — perguntas, módulo de decisão, run e dados de teste
# (o prompt e a regra de decisão dependem deles). Caminhos relativos a esta pasta.
CONGELADOS = ["comparar.py", "criterio.py", "run.py", "../_comum/llmcache.py"] + [
    f"../{n}/{a}" for n in C.NOMES for a in ("perguntas.py", f"{C.MODULO[n]}.py", "run.py", "dados/teste.json")
] + ["../motivo-de-perda/dados/taxonomia.json"]


def _linha_manifesto(m: dict) -> str:
    h = " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in m["arquivos"].items())
    return f"Versão congelada (manifesto `{CG.MANIFESTO}`, gravado em {m['congelado_em']}): {h}"


def cabecalho(titulo: str, linha: str) -> str:
    return (f"# {titulo}\n\n{RODADA}.\n\nGerado por `run.py` em {datetime.date.today().isoformat()} (modo LLM `{os.environ.get('LLM_MODO', 'auto')}`; "
            f"Jev sempre `gravado`, 0 chamadas). LLM: `{L.MODELO}`, temperatura {0.0}, max_tokens 400, uma chamada por caso em série, "
            f"2 retries; preço US$ {L.PRECO_US_POR_MILHAO_ENTRADA:.2f}/M entrada e US$ {L.PRECO_US_POR_MILHAO_SAIDA:.2f}/M saída "
            f"({L.PRECO_FONTE}, consultada em {L.PRECO_CONSULTADO_EM}). Jev: `jev-1.13.0`, US$ 0,042/M entrada, latência da rodada "
            f"original (8 em paralelo). Prompt = state + perguntas de `perguntas.py` do exemplo, serializados em JSON, mais o texto "
            f"fixo `comparar.SISTEMA`; resposta validada por `llmcache.validar_resposta` (fora do esquema = falha operacional, "
            f"contada à parte, nunca gravada como resposta); decisão pela regra do próprio exemplo (`comparar.py`).\n\n"
            f"Critério (fixado antes da primeira chamada): " + "; ".join(f"**{k}**: {v}" for k, v in CR.CRITERIO.items() if k not in ("exemplos", "limites"))
            + f"\n\n{linha}\n")


def rodar(conjunto: str, n_casos: int | None, nomes: list[str] | None = None) -> tuple[dict, int]:
    blocos, gasto = {}, 0
    orcamento = L.Orcamento(ARQUIVO_ORCAMENTO, ORCAMENTO)
    for nome in nomes or C.NOMES:
        ex = C.carregar(nome)
        casos = C.dados(ex, conjunto)["casos"][:n_casos]
        pasta = AQUI / "cache-llm" / (nome if conjunto == "teste" else f"{nome}-{conjunto}")
        blocos[nome] = C.comparar(ex, casos, pasta, orcamento)
        gasto += blocos[nome]["tentativas_http"]
        print(f"{nome}: {len(casos)} casos, {blocos[nome]['tentativas_http']} chamadas HTTP novas, "
              f"{blocos[nome]['falhas_llm']} falhas operacionais do LLM", file=sys.stderr)
    return blocos, gasto


def main() -> None:
    args = sys.argv[1:] or ["teste"]
    if args == ["congelar"]:
        m = CG.congelar(AQUI, CONGELADOS, CR.CRITERIO)
        print(_linha_manifesto(m))
        return
    if args[0] == "rascunho":  # `rascunho [exemplo…]`: só os exemplos nomeados (afinar o encanamento de um sem gastar nos outros)
        h = CG.hashes(AQUI, CONGELADOS)
        linha = "Versão NÃO congelada (rascunho): " + " · ".join(f"`{a}` sha256 {v[:16]}…" for a, v in h.items())
        blocos, gasto = rodar("rascunho", CASOS_RASCUNHO, args[1:] or None)
        texto = cabecalho("Rascunho — jev-x-llm (encanamento; não é métrica)", linha) + "\n> 2 casos do rascunho de cada exemplo, só para provar " \
                "o encanamento (prompt, validação, injeção, métricas). **Não é métrica.**\n\n" + "\n".join(C.secao(n, b) for n, b in blocos.items())
        (AQUI / "resultados-rascunho.md").write_text(texto, encoding="utf-8", newline="\n")
        print(f"resultados-rascunho.md gerado ({gasto} chamadas HTTP)")
        return
    if args != ["teste"]:
        sys.exit(f"argumento desconhecido: {args}")
    try:
        manifesto = CG.conferir(AQUI, CONGELADOS)
    except RuntimeError as e:
        sys.exit(f"teste recusado: {e} (rode `run.py congelar`)")
    if manifesto["criterio_de_aceite"] != CR.CRITERIO:
        sys.exit("teste recusado: o critério mudou desde o congelamento (rode `run.py congelar`)")
    for nome in C.NOMES:  # o dado de cada exemplo é intocado: o manifesto DELE tem de bater
        try:
            C.conferir_dados(C.carregar(nome))
        except RuntimeError as e:
            sys.exit(f"teste recusado: manifesto de {nome} não bate: {e}")
    try:
        blocos, gasto = rodar("teste", None)
    except LoteInterrompido as e:
        sys.exit(f"LOTE INTERROMPIDO: {e}. Nada gerado; o que foi respondido ficou em cache-llm/ e a próxima execução continua de lá.")
    texto = (cabecalho("Resultados — jev-x-llm (o mesmo teste congelado, respondido por um LLM barato)", _linha_manifesto(manifesto))
             + f"\nTentativas HTTP ao LLM nesta execução: {gasto}; acumulado em `orcamento.json`: "
               f"{L.Orcamento(ARQUIVO_ORCAMENTO, ORCAMENTO).consumo()} de {ORCAMENTO}.\n\n## Resumo\n\n" + C.resumo_geral(blocos) + "\n\n"
             + "\n".join(C.secao(n, b) for n, b in blocos.items()))
    RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
    print(f"resultados.md gerado ({gasto} chamadas HTTP)")
    if not RODADA1.exists():
        RODADA1.write_text(texto, encoding="utf-8", newline="\n")
        print("resultados-rodada1.md gravado (rodada única preservada)")


if __name__ == "__main__":
    main()
