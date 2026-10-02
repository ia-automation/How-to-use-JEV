"""Rerank: o Jev julga "o trecho responde?" por trecho; o CÓDIGO ordena (probabilidade, desempate pelo BM25).

Política `*_seguro`: qualquer falha numa consulta (chamada, cache faltando, resposta fora do contrato, trecho ou
consulta acima do teto) devolve a ORDEM DO BM25 inteira para aquela consulta, marcada `falha` — nunca uma ordem
parcial inventada com os trechos que deram certo. Ausência de resposta é erro, não probabilidade 0.
Baixo nível (`julgar_trechos`, `julgar_lote`) levanta exceção; `reordenar_seguro` é o que o consumidor chama.
Resposta JSON válida mas REJEITADA pela validação (bool, string, ID faltando…) é tirada do cache só para aquele pedido
(`jev.invalidar`; revisão do Codex, 2026-10-01): sem isso, `auto` e `gravado` reliam a mesma falha para sempre e a
consulta ficava presa na ordem do BM25. As respostas válidas da mesma consulta ficam; o retorno seguro não muda.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_comum"))

import congelamento as CG  # noqa: E402
import perguntas as P  # noqa: E402


def state_de(consulta: str, trecho: str) -> dict:
    """Consulta + trecho → state enxuto com os nomes que a pergunta cita entre crases. Vazio ou longo = erro."""
    if not isinstance(consulta, str) or not consulta.strip() or not isinstance(trecho, str) or not trecho.strip():
        raise ValueError("consulta ou trecho vazio / não textual")
    if len(consulta) > P.TETO_CARACTERES_CONSULTA or len(trecho) > P.TETO_CARACTERES_TRECHO:
        raise ValueError(f"fora da faixa validada: consulta {len(consulta)}, trecho {len(trecho)} caracteres")
    return {"query": consulta, "passage": trecho}


def state_lote(consulta: str, trechos: list[str]) -> dict:
    if not trechos:
        raise ValueError("lote vazio")
    for t in trechos:
        state_de(consulta, t)  # mesma validação por trecho
    return {"query": consulta, "passages": [{"id": i, "text": t} for i, t in enumerate(trechos)]}


def _validar(jev, pedido: tuple, resposta: dict, ids: list[str]) -> list[float]:
    """Nouls validados de UMA resposta; rejeitada → sai do cache (só este pedido) e o erro sobe."""
    try:
        return [CG.noul(resposta, i) for i in ids]
    except ValueError:
        jev.invalidar(*pedido)
        raise


def julgar_trechos(jev, consulta: str, trechos: list[str], pergunta: dict = P.PERGUNTA_EN) -> list[float]:
    """Uma requisição por trecho (8 em paralelo). Devolve P(responde) por trecho, validada (CG.noul). Todas as
    respostas são validadas antes de levantar: cada rejeitada é invalidada no cache, as válidas ficam."""
    pedidos = [(state_de(consulta, t), pergunta) for t in trechos]
    respostas = jev.perguntar_varios(pedidos)
    probs, erro = [], None
    for pedido, r in zip(pedidos, respostas):
        try:
            probs.append(_validar(jev, pedido, r, ["answers"])[0])
        except ValueError as e:
            erro = erro or e
    if erro:
        raise erro
    return probs


def julgar_lote(jev, consulta: str, trechos: list[str]) -> list[float]:
    """Uma requisição por consulta: n Nouls sobre o mesmo state; todo ID tem de voltar válido (senão a requisição
    inteira é invalidada no cache)."""
    pedido = (state_lote(consulta, trechos), P.perguntas_lote(len(trechos)))
    return _validar(jev, pedido, jev.perguntar(*pedido), [f"p{i}" for i in range(len(trechos))])


def ordenar(probs: list[float], bm25: list[float]) -> list[int]:
    """Índices em ordem: maior probabilidade primeiro; empate → maior BM25; depois a posição original."""
    if len(probs) != len(bm25):
        raise ValueError("probabilidades e escores com tamanhos diferentes")
    return sorted(range(len(probs)), key=lambda i: (-probs[i], -bm25[i], i))


def reordenar_seguro(jev, consulta: str, trechos: list[str], bm25: list[float], modo: str = "trecho",
                     pergunta: dict = P.PERGUNTA_EN) -> dict:
    """O que o consumidor chama. `modo` = "trecho" (uma requisição por trecho) ou "lote" (uma por consulta).
    Falha em qualquer ponto → ordem do BM25 (índices 0..n−1), `probs` None e `falha` com etapa e classe do erro.
    Pega `Exception` inteira de propósito: num rerank, erro não previsto também tem de fechar na ordem de origem.
    @example reordenar_seguro(jev_fora_do_ar, "q", ["a", "b"], [2.0, 1.0])
             → {"ordem": [0, 1], "probs": None, "falha": "chamada (TimeoutError)"}
    """
    etapa = "entrada inválida"
    try:
        if len(trechos) != len(bm25):
            raise ValueError("trechos e escores com tamanhos diferentes")
        etapa = "chamada"
        probs = julgar_lote(jev, consulta, trechos) if modo == "lote" else julgar_trechos(jev, consulta, trechos, pergunta)
        etapa = "ordenação"
        return {"ordem": ordenar(probs, bm25), "probs": probs, "falha": None}
    except Exception as e:  # noqa: BLE001 — falha fechada: ver docstring
        return {"ordem": list(range(len(trechos))), "probs": None, "falha": f"{etapa} ({type(e).__name__})"}
