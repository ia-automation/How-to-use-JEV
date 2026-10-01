"""Cliente do Jev com cache em disco e medição — infra comum dos exemplos em Python.

Por que cache: rodar de novo não pode gastar de novo, e os exemplos precisam rodar sem chave
(o cache é a "resposta gravada" da API real). Chave do cache = sha256(modelo + state + perguntas).

Modos (variável de ambiente JEV_MODO):
  auto     (padrão) usa o cache; se faltar, chama a API e grava.
  gravado  só o cache; resposta faltando = erro (é o modo de quem não tem chave).
  ao_vivo  sempre chama a API e regrava o cache.

A chave vem de TYPESAFE_API_KEY; se ausente, de `api_key.txt` na raiz do repositório.
Ela nunca é impressa nem gravada no cache.
"""
from __future__ import annotations

import hashlib
import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODELO = "jev-1.13.0"  # versão fixada: limiares afinados valem para esta versão, não para o alias
PRECO_US_POR_MILHAO_ENTRADA = 0.042  # saída não é cobrada (docs.typesafe.ai/models, 2026-09-30)
RAIZ = Path(__file__).resolve().parents[2]


def _chave_api() -> str:
    chave = os.environ.get("TYPESAFE_API_KEY", "").strip()
    arquivo = RAIZ / "api_key.txt"
    if not chave and arquivo.exists():
        chave = arquivo.read_text(encoding="utf-8").strip()
    return chave


def _para_json(resposta) -> dict:
    """Converte a resposta do SDK para o formato JSON da API (chaves de nível do Score como string)."""
    bruto = resposta.model_dump(mode="json")
    return {"model": bruto["model"], "answers": bruto["answers"], "usage": bruto.get("usage")}


class Jev:
    """Uma instância por projeto; `pasta_cache` fica dentro do projeto e vai para o Git."""

    def __init__(self, pasta_cache: str | Path, modelo: str = MODELO, modo: str | None = None):
        self.pasta = Path(pasta_cache)
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.modelo = modelo
        self.modo = modo or os.environ.get("JEV_MODO", "auto")
        self._cliente = None
        self.chamadas: list[dict] = []

    def _cli(self):
        if self._cliente is None:
            from typesafe_sdk import TypeSafeClient

            chave = _chave_api()
            if not chave:
                raise RuntimeError("sem chave: defina TYPESAFE_API_KEY ou rode com JEV_MODO=gravado")
            self._cliente = TypeSafeClient(api_key=chave, model=self.modelo)
        return self._cliente

    def perguntar(self, state, questions: dict) -> dict:
        """Uma requisição: um state, várias perguntas (formato JSON da API). Devolve o JSON da resposta."""
        corpo = json.dumps({"m": self.modelo, "s": state, "q": questions}, sort_keys=True, ensure_ascii=False)
        arquivo = self.pasta / f"{hashlib.sha256(corpo.encode()).hexdigest()[:24]}.json"
        if self.modo != "ao_vivo" and arquivo.exists():
            registro = json.loads(arquivo.read_text(encoding="utf-8"))
            self.chamadas.append({**registro["medicao"], "cache": True})
            return registro["resposta"]
        if self.modo == "gravado":
            raise RuntimeError(f"resposta não gravada no cache: {arquivo.name}")
        cliente = self._cli()  # fora do cronômetro: a 1ª chamada importaria o SDK dentro da medição
        inicio = time.perf_counter()
        resposta = _para_json(cliente.system_one(state=state, questions=questions))
        medicao = {
            "ms": round((time.perf_counter() - inicio) * 1000),
            "input_tokens": (resposta.get("usage") or {}).get("input_tokens", 0),
            "modelo": resposta["model"],
            "perguntas": len(questions),
        }
        arquivo.write_text(json.dumps({"medicao": medicao, "resposta": resposta}, ensure_ascii=False, indent=1),
                           encoding="utf-8")
        self.chamadas.append({**medicao, "cache": False})
        return resposta

    def perguntar_varios(self, pedidos: list[tuple], paralelo: int = 8) -> list[dict]:
        """Vários (state, questions) em paralelo — um item por requisição (rerank, linha a linha)."""
        with ThreadPoolExecutor(paralelo) as ex:
            return list(ex.map(lambda p: self.perguntar(*p), pedidos))

    def resumo(self) -> dict:
        """Latência medida na chamada real (mesmo quando veio do cache), tokens e custo."""
        if not self.chamadas:
            return {}
        ms = sorted(c["ms"] for c in self.chamadas)
        tokens = sum(c["input_tokens"] for c in self.chamadas)
        return {
            "requisicoes": len(self.chamadas),
            "do_cache": sum(c["cache"] for c in self.chamadas),
            "perguntas": sum(c.get("perguntas", 0) for c in self.chamadas),
            "latencia_p50_ms": round(statistics.median(ms)),
            "latencia_p95_ms": ms[min(len(ms) - 1, int(0.95 * len(ms)))],
            "input_tokens": tokens,
            "custo_us": round(tokens / 1e6 * PRECO_US_POR_MILHAO_ENTRADA, 6),
            "modelos": sorted({c["modelo"] for c in self.chamadas}),
        }
