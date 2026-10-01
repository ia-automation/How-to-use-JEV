"""Roteador: para cada pedido de cliente, decide quem responde — código, LLM barato, LLM de raciocínio
ou humano.

Divisão (lição 1 — o Jev julga, o código decide):
  código  número de pedido (regex) e cartão no texto (regex + Luhn): regra exata, não julgamento;
          a ordem das etapas e toda a política.
  Jev     julgamentos sobre o texto: risco, irritação, pede status?, qual FAQ e se ela basta,
          a resposta exige raciocínio? Uma requisição por pedido com TODAS as perguntas.
  LLM     só escreve texto (simulado neste exemplo): o barato para o simples, o de raciocínio
          para política + cálculo + exceção.
Composição (política, não probabilidade): alertas por max (não dilui o mais forte); confiança da rota
= o julgamento consumido MENOS certo, orientado para o lado escolhido (receita de function calling).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import perguntas as P

# Número de pedido: "#482913", "pedido 482913", "a compra é 81005", "número 81006". 5+ dígitos para
# não pegar ano. Pegar um telefone por engano não roteia sozinho: o Noul de status ainda decide.
RE_PEDIDO = re.compile(r"(?:#|\bpedido\b|\bcompra\b|\bencomenda\b|\bn[úu]mero\b|\bn[º°o]\.?)\D{0,20}?"
                       r"\b([A-Z]{0,4}-?\d{5,12})\b", re.I)
RE_CARTAO = re.compile(r"\b(?:\d[ .-]?){13,19}\b")
BARATAS = {"faq", "status_pedido", "llm_barato"}  # rotas a que o piso se aplica


@dataclass
class Rota:
    destino: str          # destino final (depois do piso)
    destino_bruto: str    # destino antes do piso — é o que a curva cobertura × erro mede
    motivo: str
    confianca: float      # julgamento consumido menos certo, orientado para o lado escolhido
    mais_fraco: str       # qual julgamento é esse (onde duvidar primeiro)
    faq_id: str | None = None
    numero_pedido: str | None = None


def numero_pedido(texto: str) -> str | None:
    m = RE_PEDIDO.search(texto)
    return m.group(1) if m else None


def _luhn(digitos: str) -> bool:
    soma = 0
    for i, c in enumerate(reversed(digitos)):
        d = int(c) * (2 if i % 2 else 1)
        soma += d - 9 if d > 9 else d
    return soma % 10 == 0


def tem_cartao(texto: str) -> bool:
    """Cartão é forma exata (13–19 dígitos que passam no Luhn) — código, antes de qualquer modelo."""
    for m in RE_CARTAO.finditer(texto):
        d = re.sub(r"\D", "", m.group())
        if 13 <= len(d) <= 19 and _luhn(d):
            return True
    return False


def _rota(destino: str, motivo: str, usados: list[tuple[str, float]], **extra) -> Rota:
    nome, conf = min(usados, key=lambda u: u[1])
    final = destino
    if destino in BARATAS and conf < P.PISO_ROTA:
        final, motivo = "llm_raciocinio", f"piso: {destino} com confiança {conf:.2f} ({motivo})"
    return Rota(final, destino, motivo, round(conf, 4), nome, **extra)


def decidir(texto: str, resposta: dict) -> Rota:
    """Aplica a política às respostas do Jev. Ordem = precedência congelada no DADOS.md:
    humano > llm_raciocinio > status_pedido > faq > llm_barato.

    @param texto: o pedido do cliente (para as regras de código)
    @param resposta: JSON da API para as perguntas de `perguntas.montar`
    """
    a = resposta["answers"]
    numero = numero_pedido(texto)
    if tem_cartao(texto):
        return Rota("humano", "humano", "cartão no texto (regex + Luhn)", 1.0, "regex_cartao", numero_pedido=numero)

    # 1. Risco → humano. Irritação vira probabilidade de "muito irritado ou hostil" (massa do Score).
    alertas = {k: a[k]["noul"] for k in P.RISCO}
    alertas["irritacao"] = sum(p for nivel, p in a["irritacao"]["probabilities"].items()
                               if int(nivel) >= P.NIVEL_IRRITADO)
    limiar = {**{k: P.LIM_RISCO for k in P.RISCO}, "irritacao": P.LIM_IRRITACAO}
    disparados = {k: v for k, v in alertas.items() if v >= limiar[k]}
    if disparados:
        k = max(disparados, key=disparados.get)
        return Rota("humano", "humano", k, round(disparados[k], 4), k, numero_pedido=numero)
    usados = [(k, 1 - v) for k, v in alertas.items()]

    # 2. Raciocínio → LLM caro. Vem antes das rotas de código pela precedência congelada: pedido que
    # exige plano/conflito/exceção não se resolve com FAQ nem consulta, mesmo com número de pedido.
    rac = {k: a[k]["noul"] for k in P.RACIOCINIO}
    kr = max(rac, key=rac.get)
    if rac[kr] >= P.LIM_RACIOCINIO:
        return _rota("llm_raciocinio", kr, usados + [(kr, rac[kr])], numero_pedido=numero)
    usados.append((kr, 1 - rac[kr]))

    # 3. Status do pedido → código (consulta ao sistema). O número é regra de código: sem ele não há
    # consulta (vai ao barato, que pede o número), e o Noul nem é lido — no rascunho, "vcs entregam no
    # sábado?" deu status 0,83.
    if numero:
        s = a["status_pedido"]["noul"]
        if s >= P.LIM_STATUS:
            return _rota("status_pedido", f"status do pedido {numero}", usados + [("status_pedido", s)],
                         numero_pedido=numero)
        usados.append(("status_pedido", 1 - s))

    # 4. FAQ → código devolve a resposta oficial. Exige QUAL (Choice) e SE basta (Noul da escolhida).
    f = a["faq"]
    fid = f["choice"]
    if fid != P.NENHUMA:
        cobre = a[f"faq_cobre::{fid}"]["noul"]
        if f["confidence"] >= P.LIM_FAQ_CONF and cobre >= P.LIM_FAQ_COBRE:
            return _rota("faq", f"faq {fid}", usados + [("faq", f["confidence"]), (f"faq_cobre::{fid}", cobre)],
                         faq_id=fid, numero_pedido=numero)
        usados.append((f"faq_cobre::{fid}", 1 - cobre))
    else:
        usados.append(("faq", f["probabilities"][P.NENHUMA]))

    # 5. Resto → LLM barato (texto simples; status sem número: pede o número).
    sem_numero = not numero and a["status_pedido"]["noul"] >= P.LIM_STATUS
    return _rota("llm_barato", "status sem número: pedir o número" if sem_numero else "texto simples",
                 usados, numero_pedido=numero)


def rotear(jev, textos: list[str], faq: list[dict], paralelo: int = 8) -> tuple[list[Rota], list[dict]]:
    """Uma requisição por pedido, em paralelo; devolve as rotas e as respostas brutas (para métricas)."""
    q = P.montar(faq)
    respostas = jev.perguntar_varios([({"message": t}, q) for t in textos], paralelo)
    return [decidir(t, r) for t, r in zip(textos, respostas)], respostas
