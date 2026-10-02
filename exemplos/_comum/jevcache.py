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
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODELO = "jev-1.13.0"  # versão fixada: limiares afinados valem para esta versão, não para o alias
PRECO_US_POR_MILHAO_ENTRADA = 0.042  # saída não é cobrada (docs.typesafe.ai/models, 2026-09-30)
RAIZ = Path(__file__).resolve().parents[2]
_TRAVAS_POR_PASTA: dict[str, dict[str, threading.Lock]] = {}
_GUARDA_GLOBAL = threading.Lock()


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

    def __init__(self, pasta_cache: str | Path, modelo: str | None = None, modo: str | None = None):
        # Reavaliação por versão (`ferramentas/reavaliar_versao.py`, 2026-10-01): os run.py estão congelados por hash e
        # passam `cache/` fixo, então o redirecionamento vem do ambiente. `JEV_PASTA_CACHE` troca o NOME da pasta
        # (irmã da passada: `cache/` → `cache-jev-1.14.0/`) e `JEV_MODELO` o modelo; argumento explícito de modelo
        # vence a variável. Sem as duas variáveis, nada muda.
        pasta = Path(pasta_cache)
        redirecionada = os.environ.get("JEV_PASTA_CACHE", "").strip()
        # Caminho absoluto = usado como está (o arnês lê uma CÓPIA do cache na referência); nome = pasta irmã.
        self.pasta = (Path(redirecionada) if Path(redirecionada).is_absolute() else pasta.with_name(redirecionada)) if redirecionada else pasta
        modelo_do_ambiente = not modelo and bool(os.environ.get("JEV_MODELO", "").strip())
        if modelo_do_ambiente and (not redirecionada or self.pasta.resolve() == pasta.resolve() or self.pasta.name == "cache"):
            # Revisão do Codex (achado 3): `JEV_MODELO` sozinho gravaria respostas da versão nova em `cache/` com outra
            # chave — poluição silenciosa do cache congelado. Recusa ANTES de criar pasta ou chamar.
            raise RuntimeError("JEV_MODELO vindo do ambiente exige JEV_PASTA_CACHE apontando para uma pasta distinta de `cache` "
                               f"(recebido: {redirecionada!r})")
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.modelo = modelo or os.environ.get("JEV_MODELO", "").strip() or MODELO
        self.modo = modo or os.environ.get("JEV_MODO", "auto")
        self._cliente = None
        self.chamadas: list[dict] = []
        # Tabela de travas por PASTA de cache, compartilhada entre instâncias (o aplicador do roteador-email viu 15
        # chamadas duplicadas com uma instância por linha paralela, 2026-10-01): a trava protege o arquivo, não o objeto.
        with _GUARDA_GLOBAL:
            self._travas = _TRAVAS_POR_PASTA.setdefault(str(self.pasta.resolve()), {})
        self._guarda = _GUARDA_GLOBAL

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
        arquivo = self._arquivo(state, questions)
        # Uma trava por pedido (revisão do Codex em roteador-email, 2026-10-01): dois pedidos IDÊNTICOS em paralelo
        # disputavam o mesmo `.tmp` e podiam consumir respostas diferentes da que ficou gravada para o replay. Com a
        # trava, o segundo espera e lê do cache o que o primeiro gravou (em `ao_vivo`, chama de novo, por desenho).
        with self._guarda:
            trava = self._travas.setdefault(arquivo.name, threading.Lock())
        with trava:
            return self._perguntar(arquivo, state, questions)

    def _perguntar(self, arquivo: Path, state, questions: dict) -> dict:
        if self.modo != "ao_vivo" and arquivo.exists():
            try:
                registro = json.loads(arquivo.read_text(encoding="utf-8"))
                medicao = registro["medicao"]
                # Medição sem os campos do contrato (revisão do Codex em triagem-de-alerta, 2026-10-01): antes entrava
                # em `chamadas` e `resumo()` quebrava fora de qualquer tratamento por item, abortando o lote inteiro.
                if not all(isinstance(medicao.get(k), int) for k in ("ms", "input_tokens")) or not isinstance(medicao.get("modelo"), str):
                    raise ValueError("medição fora do contrato")
                self.chamadas.append({**medicao, "cache": True})
                return registro["resposta"]
            except (ValueError, KeyError, TypeError, AttributeError):
                # Arquivo de cache ilegível (gravação interrompida): não pode deixar o pedido pendente para
                # sempre (revisão do Codex em selecao-de-skill, 2026-10-01). Vai para `invalidos/` e a chamada
                # é refeita — menos no modo `gravado`, que nunca chama a API.
                self._por_de_lado(arquivo, "invalidos")
        if self.modo == "gravado":
            raise RuntimeError(f"resposta não gravada no cache: {arquivo.name}")
        if arquivo.exists():
            # `ao_vivo` sobre resposta já gravada: a anterior vai para `historico/` com a hora, não some
            # (revisão do Codex 2026-10-01: sobrescrever apagava a prova de que houve outra rodada).
            self._por_de_lado(arquivo, "historico")
        cliente = self._cli()  # fora do cronômetro: a 1ª chamada importaria o SDK dentro da medição
        inicio = time.perf_counter()
        resposta = _para_json(cliente.system_one(state=state, questions=questions))
        medicao = {
            "ms": round((time.perf_counter() - inicio) * 1000),
            "input_tokens": (resposta.get("usage") or {}).get("input_tokens", 0),
            "modelo": resposta["model"],
            "perguntas": len(questions),
        }
        # Gravação atômica: escreve ao lado e troca; um corte no meio não deixa JSON pela metade no cache.
        temporario = arquivo.with_suffix(".tmp")
        temporario.write_text(json.dumps({"medicao": medicao, "resposta": resposta}, ensure_ascii=False, indent=1),
                              encoding="utf-8")
        temporario.replace(arquivo)
        self.chamadas.append({**medicao, "cache": False})
        return resposta

    def _arquivo(self, state, questions: dict) -> Path:
        corpo = json.dumps({"m": self.modelo, "s": state, "q": questions}, sort_keys=True, ensure_ascii=False)
        return self.pasta / f"{hashlib.sha256(corpo.encode()).hexdigest()[:24]}.json"

    def _por_de_lado(self, arquivo: Path, pasta: str) -> None:
        """Move um registro do cache para `historico/` ou `invalidos/` com a hora — nada se apaga."""
        destino = self.pasta / pasta
        destino.mkdir(exist_ok=True)
        arquivo.replace(destino / f"{arquivo.stem}.{time.strftime('%Y%m%dT%H%M%S')}.json")

    def invalidar(self, state, questions: dict) -> bool:
        """Tira do cache a resposta deste pedido (JSON válido, mas rejeitada pela validação do exemplo), para
        que SÓ ele seja refeito na próxima rodada; as respostas válidas ficam. Devolve se havia o que invalidar."""
        arquivo = self._arquivo(state, questions)
        if not arquivo.exists():
            return False
        self._por_de_lado(arquivo, "invalidos")
        return True

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
