"""Cliente mínimo da API Messages (Anthropic) com cache em disco e medição — irmão do `jevcache.py`, para o
exemplo `jev-x-llm/` (o MESMO teste congelado respondido por um LLM barato).

Por que existe: comparar Jev × LLM exige (1) o mesmo prompt para todo caso, (2) rodar de novo sem gastar de novo e
sem chave, (3) resposta fora do esquema contada como FALHA OPERACIONAL e nunca gravada como resposta válida
(lição do estudo: "resposta inválida presa no cache"). Só biblioteca padrão (`urllib`): o .venv não tem `anthropic`,
`requests` nem `httpx`, e nada é instalado.

Modos (variável de ambiente LLM_MODO):
  auto     (padrão) usa o cache; se faltar, chama a API e grava. Falha já registrada em `invalidos/` é REPRODUZIDA
           (revisão do Codex, achado 1: refazer as inválidas estourava o orçamento em silêncio); refazer só com
           `refazer_invalidas=True` (ou LLM_REFAZER_INVALIDAS=1).
  gravado  só o cache; resposta faltando = erro; inválida gravada = RespostaInvalida de novo, sem chamar.
  ao_vivo  sempre chama a API e regrava (a anterior vai para `historico/`).

Orçamento (`Orcamento`): consumo PERSISTIDO em arquivo na pasta do exemplo e conferido antes de CADA tentativa HTTP
(retry conta) — o contador não reinicia por execução (revisão do Codex, achado 1).

Chave: `ANTHROPIC_API_KEY` ou, se ausente, `.local/chaves/anthropic.txt` na raiz do repositório (fora do Git). Lida SÓ
aqui; nunca impressa, logada nem gravada no cache (o cache guarda medição + resposta, não o pedido nem cabeçalhos).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import socket
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path

MODELO = "claude-haiku-4-5-20251001"  # "LLM barato" de um fornecedor, versão datada; não é o topo da linha
# Preço publicado (tabela pública da Anthropic, consultada em 2026-10-01): US$ por milhão de tokens.
PRECO_US_POR_MILHAO_ENTRADA = 1.00
PRECO_US_POR_MILHAO_SAIDA = 5.00
PRECO_CONSULTADO_EM = "2026-10-01"
PRECO_FONTE = "tabela pública da Anthropic"
URL = "https://api.anthropic.com/v1/messages"
VERSAO_API = "2023-06-01"
RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_CHAVE = RAIZ / ".local" / "chaves" / "anthropic.txt"
RETRIES = 2                 # tentativas EXTRAS em 429/5xx/timeout/rede (3 tentativas no total)
ESPERA_S = (2.0, 6.0)       # espera antes de cada retentativa; 429 com `retry-after` usa o cabeçalho (teto 30 s)
TIMEOUT_S = 60
MAX_429_SEGUIDOS = 3        # 429 em três tentativas seguidas = parar o lote e reportar (ordem do briefing)
CAMPOS_MEDICAO = ("ms", "input_tokens", "output_tokens")


class FalhaChamada(RuntimeError):
    """Rede, timeout, HTTP de erro depois dos retries, ou chave ausente. A mensagem nunca leva corpo nem cabeçalho."""


class RespostaInvalida(ValueError):
    """JSON ilegível ou fora do esquema pedido: falha operacional, gravada em `invalidos/`, nunca como resposta.
    Leva o objeto bruto (`obj`, None se ilegível) e os IDs violados (`violacoes`) para quem quiser uma leitura
    secundária declarada — a resposta em si continua inválida."""

    def __init__(self, mensagem: str, obj=None, violacoes: list[str] | None = None):
        super().__init__(mensagem)
        self.obj, self.violacoes = obj, violacoes or []


class LoteInterrompido(RuntimeError):
    """429 em `MAX_429_SEGUIDOS` tentativas seguidas ou orçamento esgotado: quem roda para e reporta."""


def _chave_api() -> str:
    chave = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not chave and ARQUIVO_CHAVE.exists():
        chave = ARQUIVO_CHAVE.read_text(encoding="utf-8").strip()
    if not chave:
        raise FalhaChamada("sem chave: defina ANTHROPIC_API_KEY ou grave .local/chaves/anthropic.txt (ou rode com LLM_MODO=gravado)")
    return chave


def _gravar_json(arquivo: Path, registro: dict) -> None:
    """Gravação atômica (escreve ao lado e troca); LF."""
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    temporario = arquivo.with_suffix(".tmp")
    temporario.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    temporario.replace(arquivo)


# ---------------------------------------------------------------------------------------- orçamento
class Orcamento:
    """Teto de tentativas HTTP persistido em `arquivo` ({"teto", "chamadas_http"}); `consumir()` lê, confere e grava
    ANTES da tentativa. Vale entre execuções e entre instâncias (teste, rascunho, retries)."""

    def __init__(self, arquivo: str | Path, teto: int):
        self.arquivo, self.teto = Path(arquivo), teto

    def consumo(self) -> int:
        if not self.arquivo.exists():
            return 0
        return int(json.loads(self.arquivo.read_text(encoding="utf-8")).get("chamadas_http", 0))

    def consumir(self) -> int:
        gasto = self.consumo()
        if gasto >= self.teto:
            raise LoteInterrompido(f"orçamento esgotado: {gasto}/{self.teto} tentativas HTTP ({self.arquivo.name})")
        _gravar_json(self.arquivo, {"teto": self.teto, "chamadas_http": gasto + 1,
                                    "atualizado_em": datetime.datetime.now().astimezone().isoformat(timespec="seconds")})
        return gasto + 1


# ---------------------------------------------------------------------------------------- esquema de saída
def esquema_de(questions: dict) -> dict:
    """{id: ("noul", None) | ("choice", {opções})} a partir das perguntas no formato JSON da API do Jev.
    Score é tratado como escolha de UM nível (chave de `criteria`); nenhum dos três exemplos usa Score."""
    esquema = {}
    for q, p in questions.items():
        if p["type"] == "noul":
            esquema[q] = ("noul", None)
        elif p["type"] in ("choice", "score"):
            esquema[q] = ("choice", set(p["criteria"]))
        else:
            raise ValueError(f"tipo de pergunta desconhecido: {p['type']!r}")
    return esquema


def validar_resposta(obj, esquema: dict) -> dict:
    """Validação ESTRITA do JSON devolvido: objeto com SÓ a chave `answers` (revisão do Codex, achado 4: chave extra na
    raiz passava), dict; todo ID esperado presente e nenhum a mais; Noul = bool JSON (não string, não 0/1); Choice =
    string exatamente igual a uma opção. Qualquer desvio = RespostaInvalida."""
    if not isinstance(obj, dict) or set(obj) != {"answers"} or not isinstance(obj.get("answers"), dict):
        raise RespostaInvalida("resposta não é um objeto só com `answers`", obj)
    answers = obj["answers"]
    if set(answers) != set(esquema):
        faltam, sobram = sorted(set(esquema) - set(answers)), sorted(set(answers) - set(esquema))
        raise RespostaInvalida(f"IDs não batem: faltam {faltam}, sobram {sobram}", obj, faltam + sobram)
    erros = []
    for q, (tipo, opcoes) in esquema.items():
        v = answers[q]
        if tipo == "noul" and not isinstance(v, bool):
            erros.append((q, f"`{q}` não é booleano JSON: {type(v).__name__}"))
        if tipo == "choice" and (not isinstance(v, str) or v not in opcoes):
            erros.append((q, f"`{q}` fora das opções: {v!r}"))
    if erros:
        raise RespostaInvalida("; ".join(m for _, m in erros), obj, [q for q, _ in erros])
    return answers


def _extrair_json(texto: str):
    """JSON estrito; a única tolerância é a cerca Markdown (```json … ```), que é formatação, não esquema."""
    t = texto.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        t = t.rsplit("```", 1)[0]
    try:
        return json.loads(t)
    except json.JSONDecodeError as e:
        raise RespostaInvalida(f"JSON ilegível ({e.msg} na posição {e.pos})") from None


def medicao_ou_nula(m) -> dict:
    """Medição do registro validada (revisão do Codex, achado 2): campo ausente ou com tipo errado vira None — nunca
    zero inventado — e `resumo()` segue sem quebrar, contando `sem_medicao`."""
    m = m if isinstance(m, dict) else {}
    ok = all(isinstance(m.get(k), int) and not isinstance(m.get(k), bool) for k in CAMPOS_MEDICAO) and isinstance(m.get("modelo"), str)
    if ok:
        return dict(m)
    return {**{k: None for k in CAMPOS_MEDICAO}, "modelo": m.get("modelo") if isinstance(m.get("modelo"), str) else None, "sem_medicao": True}


# ---------------------------------------------------------------------------------------- HTTP
def _http(corpo: dict, chave: str, timeout: float) -> dict:
    """Uma tentativa. Levanta urllib.error.HTTPError / URLError / TimeoutError como vierem (o laço de retries decide).
    Separada em função para a bateria trocar por um dublê sem rede."""
    req = urllib.request.Request(URL, data=json.dumps(corpo).encode("utf-8"), method="POST",
                                 headers={"x-api-key": chave, "anthropic-version": VERSAO_API, "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


class LLM:
    """Uma instância por conjunto; `pasta_cache` fica dentro do exemplo e vai para o Git (medição + resposta)."""

    def __init__(self, pasta_cache: str | Path, modelo: str = MODELO, modo: str | None = None, temperature: float = 0.0,
                 max_tokens: int = 400, timeout: float = TIMEOUT_S, orcamento: Orcamento | None = None,
                 refazer_invalidas: bool | None = None):
        self.pasta = Path(pasta_cache)
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.modelo, self.temperature, self.max_tokens, self.timeout = modelo, temperature, max_tokens, timeout
        self.modo = modo or os.environ.get("LLM_MODO", "auto")
        self.orcamento = orcamento
        self.refazer_invalidas = (os.environ.get("LLM_REFAZER_INVALIDAS") == "1") if refazer_invalidas is None else refazer_invalidas
        self.chamadas: list[dict] = []        # medições (do cache ou novas), uma por pedido respondido
        self.invalidas: list[dict] = []       # respostas fora do esquema (do cache `invalidos/` ou novas)
        self.tentativas_http = 0              # toda requisição HTTP disparada nesta instância, inclusive retries
        self.interrompido = ""                # motivo do LoteInterrompido (quem roda confere, porque os invólucros engolem exceções)
        self._429_seguidos = 0

    def _interromper(self, motivo: str) -> LoteInterrompido:
        self.interrompido = motivo
        return LoteInterrompido(motivo)

    # --- cache
    def _arquivo(self, system: str, user: str) -> Path:
        corpo = json.dumps({"m": self.modelo, "s": system, "u": user}, sort_keys=True, ensure_ascii=False)
        return self.pasta / f"{hashlib.sha256(corpo.encode()).hexdigest()[:24]}.json"

    def _invalidos_de(self, arquivo: Path) -> list[Path]:
        return sorted((self.pasta / "invalidos").glob(f"{arquivo.stem}.*.json"))

    def _por_de_lado(self, arquivo: Path, pasta: str) -> None:
        destino = self.pasta / pasta
        destino.mkdir(exist_ok=True)
        arquivo.replace(destino / f"{arquivo.stem}.{time.strftime('%Y%m%dT%H%M%S')}.json")

    def _do_cache(self, arquivo: Path, esquema: dict) -> dict | None:
        """Resposta válida do cache, ou None quando não há. Registro ilegível/sem contrato → `corrompidos/` (é refeito em
        `auto`); registro legível que a validação de HOJE rejeita → vira registro de `invalidos/` (falha reproduzível)."""
        try:
            registro = json.loads(arquivo.read_text(encoding="utf-8"))
            medicao, resposta, texto = registro["medicao"], registro["resposta"], registro.get("texto", "")
            if "sem_medicao" in medicao_ou_nula(medicao):
                raise ValueError("medição fora do contrato")
        except (ValueError, KeyError, TypeError, AttributeError):
            self._por_de_lado(arquivo, "corrompidos")
            return None
        try:
            answers = validar_resposta(resposta, esquema)
        except RespostaInvalida as e:
            _gravar_json(self.pasta / "invalidos" / f"{arquivo.stem}.{time.strftime('%Y%m%dT%H%M%S')}.json",
                         {"medicao": medicao, "erro": f"rejeitada pela validação atual: {e}", "texto": texto})
            arquivo.unlink()
            return None
        self.chamadas.append({**medicao, "cache": True})
        return answers

    def _reproduzir_invalida(self, arquivo: Path, esquema: dict) -> None:
        """Falha já registrada em `invalidos/`: conta na medição e levanta RespostaInvalida de novo, sem chamar."""
        anteriores = self._invalidos_de(arquivo)
        if not anteriores:
            return
        reg = json.loads(anteriores[-1].read_text(encoding="utf-8"))
        self.invalidas.append({**medicao_ou_nula(reg.get("medicao")), "cache": True, "erro": reg.get("erro", "")})
        try:  # a mesma validação de hoje sobre o texto gravado: a exceção leva `obj` e `violacoes`
            validar_resposta(_extrair_json(reg.get("texto", "")), esquema)
        except RespostaInvalida as e:
            raise RespostaInvalida(f"resposta inválida gravada ({e}): {anteriores[-1].name}", e.obj, e.violacoes) from None
        raise RespostaInvalida(f"resposta inválida gravada ({reg.get('erro', '?')}): {anteriores[-1].name}")

    # --- chamada
    def perguntar(self, system: str, user: str, esquema: dict) -> dict:
        """Um prompt → `answers` validado pelo `esquema` (ver `validar_resposta`). Falha operacional levanta:
        RespostaInvalida (fora do esquema; gravada em `invalidos/`), FalhaChamada (rede/HTTP/chave), LoteInterrompido."""
        arquivo = self._arquivo(system, user)
        if self.modo != "ao_vivo" and arquivo.exists():
            answers = self._do_cache(arquivo, esquema)
            if answers is not None:
                return answers
        if self.modo == "gravado" or (self.modo == "auto" and not self.refazer_invalidas):
            self._reproduzir_invalida(arquivo, esquema)
        if self.modo == "gravado":
            raise FalhaChamada(f"resposta não gravada no cache: {arquivo.name}")
        if arquivo.exists():
            self._por_de_lado(arquivo, "historico")
        texto, medicao = self._chamar(system, user)
        try:
            answers = validar_resposta(_extrair_json(texto), esquema)
        except RespostaInvalida as e:
            _gravar_json(self.pasta / "invalidos" / f"{arquivo.stem}.{time.strftime('%Y%m%dT%H%M%S')}.json",
                         {"medicao": medicao, "erro": str(e), "texto": texto})
            self.invalidas.append({**medicao, "cache": False, "erro": str(e)})
            raise
        _gravar_json(arquivo, {"medicao": medicao, "resposta": {"answers": answers}, "texto": texto})
        self.chamadas.append({**medicao, "cache": False})
        return answers

    def _chamar(self, system: str, user: str) -> tuple[str, dict]:
        """HTTP com até RETRIES retentativas em 429/5xx/timeout/rede. Devolve (texto da resposta, medição). `ms` é o
        tempo da OPERAÇÃO inteira — tentativas e esperas incluídas, como o cronômetro do Jev envolve a chamada do SDK
        (revisão do Codex, achado 5). O orçamento é consumido antes de CADA tentativa."""
        chave = _chave_api()  # fora do cronômetro
        corpo = {"model": self.modelo, "max_tokens": self.max_tokens, "temperature": self.temperature,
                 "system": system, "messages": [{"role": "user", "content": user}]}
        ultimo: Exception | None = None
        inicio = time.perf_counter()
        for tentativa in range(RETRIES + 1):
            if tentativa:
                time.sleep(self._espera(tentativa, ultimo))
            if self.orcamento is not None:
                try:
                    self.orcamento.consumir()
                except LoteInterrompido as e:
                    raise self._interromper(str(e)) from None
            self.tentativas_http += 1
            try:
                dados = _http(corpo, chave, self.timeout)
            except urllib.error.HTTPError as e:
                ultimo = e
                if e.code == 429:
                    self._429_seguidos += 1
                    if self._429_seguidos >= MAX_429_SEGUIDOS:
                        raise self._interromper(f"HTTP 429 em {self._429_seguidos} tentativas seguidas") from None
                if e.code == 429 or e.code >= 500:
                    continue
                raise FalhaChamada(f"HTTP {e.code}") from None  # 400/401/404…: não se retenta (integracao-segura)
            except (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError) as e:
                ultimo = e
                continue
            ms = round((time.perf_counter() - inicio) * 1000)
            self._429_seguidos = 0
            uso = dados.get("usage") or {}
            texto = "".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text")
            medicao = {"ms": ms, "input_tokens": int(uso.get("input_tokens", 0)), "output_tokens": int(uso.get("output_tokens", 0)),
                       "modelo": str(dados.get("model", self.modelo)), "data": datetime.date.today().isoformat(),
                       "tentativas": tentativa + 1, "stop_reason": dados.get("stop_reason")}
            return texto, medicao
        raise FalhaChamada(f"sem resposta após {RETRIES + 1} tentativas ({type(ultimo).__name__})")

    @staticmethod
    def _espera(tentativa: int, erro: Exception | None) -> float:
        base = ESPERA_S[min(tentativa - 1, len(ESPERA_S) - 1)]
        if isinstance(erro, urllib.error.HTTPError) and erro.code == 429:
            try:
                return min(float(erro.headers.get("retry-after", base)), 30.0)
            except (TypeError, ValueError):
                return base
        return base

    # --- medição
    def resumo(self) -> dict:
        """Latência da chamada real (também quando veio do cache), tokens de entrada e saída, custo, falhas inválidas.
        Registro sem medição (None) fica fora das somas e é contado em `sem_medicao`."""
        if not self.chamadas and not self.invalidas:
            return {}
        todas = self.chamadas + self.invalidas  # a resposta inválida também custou tempo e tokens
        ms = sorted(c["ms"] for c in todas if isinstance(c.get("ms"), int))
        entrada = sum(c["input_tokens"] for c in todas if isinstance(c.get("input_tokens"), int))
        saida = sum(c["output_tokens"] for c in todas if isinstance(c.get("output_tokens"), int))
        return {
            "requisicoes": len(todas),
            "do_cache": sum(bool(c.get("cache")) for c in todas),
            "invalidas": len(self.invalidas),
            "sem_medicao": sum(not isinstance(c.get("ms"), int) for c in todas),
            "tentativas_http": self.tentativas_http,
            "latencia_p50_ms": round(statistics.median(ms)) if ms else 0,
            "latencia_p95_ms": ms[min(len(ms) - 1, int(0.95 * len(ms)))] if ms else 0,
            "input_tokens": entrada,
            "output_tokens": saida,
            "custo_us": round(entrada / 1e6 * PRECO_US_POR_MILHAO_ENTRADA + saida / 1e6 * PRECO_US_POR_MILHAO_SAIDA, 6),
            "modelos": sorted({c["modelo"] for c in todas if isinstance(c.get("modelo"), str)}),
        }
