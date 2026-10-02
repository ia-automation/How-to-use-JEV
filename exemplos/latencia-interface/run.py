"""Mede, AO VIVO, se uma Choice de 7 destinos cabe no gesto de uma barra de comando.

Uso (exige chave; o cache é regravado):
  JEV_MODO=ao_vivo python run.py            → resultados.md
  python run.py --n 10                      ensaio curto do encanamento (não é medição; não grava resultados.md)

Dois regimes sobre os MESMOS textos ciclados (`textos.py`): N chamadas em série e N com 4 em paralelo. A latência
é a medida pelo `jevcache` em volta da chamada HTTP (sem o I/O do cache), como nos outros exemplos. O critério de
aprovação está em CRITERIO, fixado antes de rodar; o veredito é calculado, não escrito à mão.
"""
from __future__ import annotations

import argparse
import datetime
import os
import socket
import statistics
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "_comum"))

import perguntas as P  # noqa: E402
import textos as T  # noqa: E402
from jevcache import PRECO_US_POR_MILHAO_ENTRADA, Jev  # noqa: E402

# ---------------------------------------------------------------- fixado ANTES de rodar
CRITERIO = {
    "pergunta": "cabe em 300 ms?",
    "p95_serie_ms_max": 300,      # a barra chama uma vez por pausa de digitação: p95 em série ≤ 300 ms
    "p95_paralelo4_ms_max": 400,  # 4 pessoas digitando ao mesmo tempo: p95 com 4 em paralelo ≤ 400 ms
    "chamadas_por_regime": 210,   # 66 textos ciclados ≈ 3,2 voltas; 420 no total (orçamento ≤ 450)
    "paralelo": 4,
}
ORCAMENTO_CHAMADAS = 450
REDE = "Brasil, rede doméstica/fibra — informar o que o ambiente permitir ver"
HOST_API = "api.typesafe.ai"
RESULTADOS = AQUI / "resultados.md"
PERCENTIS = (50, 90, 95, 99)


def percentil(valores: list[int], p: int) -> int:
    ordenados = sorted(valores)
    return ordenados[min(len(ordenados) - 1, int(p / 100 * len(ordenados)))]


def rtt_tcp(host: str, porta: int = 443, amostras: int = 5) -> dict:
    """Tempo de conexão TCP ao host da API (o RTT base da rede, sem TLS nem HTTP)."""
    ip = socket.gethostbyname(host)
    tempos = []
    for _ in range(amostras):
        inicio = time.perf_counter()
        with socket.create_connection((ip, porta), timeout=5):
            tempos.append(round((time.perf_counter() - inicio) * 1000, 1))
    return {"ip": ip, "min_ms": min(tempos), "mediana_ms": statistics.median(tempos), "amostras": tempos}


class Medidor:
    """Faz as chamadas de um regime e separa o que é latência (do jevcache) do que é falha (exceção)."""

    def __init__(self, jev: Jev):
        self.jev = jev
        self.falhas: list[str] = []
        self.rate_limit_seguidos = 0
        self.parar = False
        self._trava = threading.Lock()

    def uma(self, texto: str) -> str | None:
        if self.parar:
            return None
        from typesafe_sdk import TypeSafeRateLimitError  # import fora do cronômetro (o jevcache já separa)
        try:
            resposta = self.jev.perguntar({"text": texto}, P.PERGUNTAS)
        except TypeSafeRateLimitError as e:
            with self._trava:
                self.rate_limit_seguidos += 1
                self.falhas.append(f"429: {e}")
                if self.rate_limit_seguidos >= 3:
                    self.parar = True  # ordem do briefing: 3 × 429 seguidos → parar e reportar o que mediu
            return None
        except Exception as e:  # falha operacional: conta à parte, a medição continua
            with self._trava:
                self.rate_limit_seguidos = 0
                self.falhas.append(f"{type(e).__name__}: {e}")
            return None
        with self._trava:
            self.rate_limit_seguidos = 0
        return resposta["answers"][P.DESTINO]["choice"]

    def regime(self, itens: list[tuple[str, str]], paralelo: int) -> dict:
        antes = len(self.jev.chamadas)
        inicio = datetime.datetime.now().astimezone()
        relogio = time.perf_counter()
        if paralelo == 1:
            escolhas = [self.uma(t) for t, _ in itens]
        else:
            with ThreadPoolExecutor(paralelo) as ex:
                escolhas = list(ex.map(lambda par: self.uma(par[0]), itens))
        duracao_s = time.perf_counter() - relogio
        fim = datetime.datetime.now().astimezone()
        chamadas = self.jev.chamadas[antes:]
        ms = [c["ms"] for c in chamadas]
        pares = [(e, g) for e, (_, g) in zip(escolhas, itens) if e is not None]
        tokens = sum(c["input_tokens"] for c in chamadas)
        return {
            "paralelo": paralelo, "pedidas": len(itens), "feitas": len(chamadas), "inicio": inicio, "fim": fim,
            "duracao_s": round(duracao_s, 1),
            "percentis": {p: percentil(ms, p) for p in PERCENTIS} if ms else {},
            "max_ms": max(ms) if ms else None, "min_ms": min(ms) if ms else None,
            "tokens": tokens, "custo_us": tokens / 1e6 * PRECO_US_POR_MILHAO_ENTRADA,
            "acerto": sum(e == g for e, g in pares) / len(pares) if pares else float("nan"),
            "n_acerto": len(pares),
            "por_destino": {d: (sum(e == g for e, g in pares if g == d), sum(1 for _, g in pares if g == d)) for d in T.DESTINOS},
            "confusoes": Counter((g, e) for e, g in pares if e != g),
        }


def veredito(serie: dict, paralelo: dict, interrompido: bool) -> tuple[str, str]:
    completo = (not interrompido and serie["feitas"] >= 200 and paralelo["feitas"] >= 200)
    if not completo:
        return "medição incompleta", "menos de 200 chamadas num regime ou interrupção por 429 — sem veredito"
    cabe_s = serie["percentis"][95] <= CRITERIO["p95_serie_ms_max"]
    cabe_p = paralelo["percentis"][95] <= CRITERIO["p95_paralelo4_ms_max"]
    if cabe_s and cabe_p:
        return "cabe", "p95 em série e com 4 em paralelo dentro do critério"
    partes = []
    if not cabe_s:
        partes.append(f"p95 em série {serie['percentis'][95]} ms > {CRITERIO['p95_serie_ms_max']} ms")
    if not cabe_p:
        partes.append(f"p95 com 4 em paralelo {paralelo['percentis'][95]} ms > {CRITERIO['p95_paralelo4_ms_max']} ms")
    return "não cabe", "; ".join(partes)


def hora(d: datetime.datetime) -> str:
    return d.strftime("%Y-%m-%d %H:%M:%S %Z (UTC%z)")


def vazio(quando: datetime.datetime) -> dict:
    """Regime que não rodou (parada por 429 na série)."""
    return {"paralelo": CRITERIO["paralelo"], "pedidas": 0, "feitas": 0, "inicio": quando, "fim": quando, "duracao_s": 0,
            "percentis": {}, "max_ms": None, "min_ms": None, "tokens": 0, "custo_us": 0.0, "acerto": float("nan"),
            "n_acerto": 0, "por_destino": {d: (0, 0) for d in T.DESTINOS}, "confusoes": Counter()}


def relatorio(jev: Jev, rtt: dict, serie: dict, par: dict, falhas: list[str], interrompido: bool) -> str:
    resultado, motivo = veredito(serie, par, interrompido)
    linhas = [
        "# Latência da interface — resultados",
        "",
        f"Gerado por `run.py` em {hora(datetime.datetime.now().astimezone())}; modelo `{jev.modelo}`; modo `{jev.modo}`. "
        "Latência = tempo da chamada HTTP medido pelo `jevcache` (sem o I/O do cache); hora local da máquina.",
        "",
        "## Condições declaradas",
        f"- Rede: {REDE}.",
        f"- RTT base (conexão TCP a `{HOST_API}`:443, ip {rtt['ip']} — é o host resolvido, possivelmente uma borda de CDN, "
        f"não o servidor que responde; {len(rtt['amostras'])} amostras): "
        f"mínimo {rtt['min_ms']} ms, mediana {rtt['mediana_ms']} ms ({', '.join(str(a) for a in rtt['amostras'])}).",
        f"- Textos: {len(T.TEXTOS)} (`textos.py`, do construtor), ciclados; uma Choice de {len(T.DESTINOS)} opções por chamada.",
        f"- Critério fixado antes: {CRITERIO['pergunta']} = p95 em série ≤ {CRITERIO['p95_serie_ms_max']} ms E "
        f"p95 com {CRITERIO['paralelo']} em paralelo ≤ {CRITERIO['p95_paralelo4_ms_max']} ms.",
        "",
        "## Latência por regime (ms)",
        "| regime | chamadas | início | fim | duração | p50 | p90 | p95 | p99 | máx | mín |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for nome, r in (("série (1)", serie), (f"paralelo ({CRITERIO['paralelo']})", par)):
        pc = r["percentis"]
        linhas.append(f"| {nome} | {r['feitas']}/{r['pedidas']} | {r['inicio'].strftime('%H:%M:%S')} | {r['fim'].strftime('%H:%M:%S')} | "
                      f"{r['duracao_s']} s | {pc.get(50, '—')} | {pc.get(90, '—')} | {pc.get(95, '—')} | {pc.get(99, '—')} | "
                      f"{r['max_ms'] if r['max_ms'] is not None else '—'} | {r['min_ms'] if r['min_ms'] is not None else '—'} |")
    total = serie["feitas"] + par["feitas"]
    total_tokens = serie["tokens"] + par["tokens"]
    linhas += [
        "",
        f"**{CRITERIO['pergunta']} {resultado.upper()}** — {motivo}.",
        "",
        "## Custo",
        f"- Chamadas: {total} (orçamento {ORCAMENTO_CHAMADAS}); tokens de entrada {total_tokens} "
        f"({round(total_tokens / max(1, total))} por chamada); "
        f"custo US$ {(serie['custo_us'] + par['custo_us']):.5f} (US$ {PRECO_US_POR_MILHAO_ENTRADA}/M de entrada; saída não cobrada).",
        f"- Falhas operacionais: {len(falhas)}" + (" — " + "; ".join(sorted(set(falhas))[:5]) if falhas else "") + ".",
        "",
        "## Acerto bruto no rótulo do construtor (secundário)",
        f"- Série: {serie['acerto']:.3f} (n = {serie['n_acerto']}); paralelo: {par['acerto']:.3f} (n = {par['n_acerto']}). "
        "Rótulo do próprio construtor, sem afinação: diz que a resposta não é aleatória, não mede desempenho.",
        "",
        "| destino | acertos/n (série) | acertos/n (paralelo) |",
        "|---|---|---|",
    ]
    for d in T.DESTINOS:
        a, n = serie["por_destino"][d]
        b, m = par["por_destino"][d]
        linhas.append(f"| `{d}` | {a}/{n} | {b}/{m} |")
    confusoes = serie["confusoes"] + par["confusoes"]
    if confusoes:
        linhas += ["", "Confusões mais frequentes (rótulo → resposta, nas duas rodadas): " +
                   "; ".join(f"`{g}` → `{e}` ×{n}" for (g, e), n in confusoes.most_common(6)) + "."]
    linhas += [
        "",
        "## Limites",
        "- Uma máquina, uma hora do dia, uma rede, uma versão do modelo, textos do próprio construtor.",
        "- O SDK refaz chamada em 429/5xx/timeout por conta própria (até 2 vezes, com espera): um valor alto isolado "
        "pode ser retentativa, não latência de uma chamada.",
        "- Em `ao_vivo` a resposta anterior de cada texto vai para `cache/historico/`; o custo de mover arquivo não "
        "entra na latência.",
        "",
    ]
    return "\n".join(linhas)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=CRITERIO["chamadas_por_regime"], help="chamadas por regime")
    args = ap.parse_args()
    if 2 * args.n > ORCAMENTO_CHAMADAS:
        raise SystemExit(f"2 × {args.n} chamadas passa do orçamento de {ORCAMENTO_CHAMADAS}")
    if os.environ.get("JEV_MODO") != "ao_vivo":
        raise SystemExit("esta medição é ao vivo: rode com JEV_MODO=ao_vivo (do cache a latência não seria desta hora)")
    ensaio = args.n < 200
    itens = [T.TEXTOS[i % len(T.TEXTOS)] for i in range(args.n)]
    jev = Jev(AQUI / "cache")
    print(f"início {hora(datetime.datetime.now().astimezone())} — {len(T.TEXTOS)} textos, {args.n} chamadas por regime")
    rtt = rtt_tcp(HOST_API)
    print(f"RTT TCP {HOST_API}: mediana {rtt['mediana_ms']} ms, mínimo {rtt['min_ms']} ms")
    medidor = Medidor(jev)
    serie = medidor.regime(itens, 1)
    print(f"série: {serie['feitas']} chamadas, p50 {serie['percentis'].get(50)} ms, p95 {serie['percentis'].get(95)} ms, "
          f"acerto {serie['acerto']:.3f}")
    if medidor.parar:
        print("parado: 3 × 429 seguidos na série")
        par = vazio(serie["fim"])
    else:
        par = medidor.regime(itens, CRITERIO["paralelo"])
        print(f"paralelo {CRITERIO['paralelo']}: {par['feitas']} chamadas, p50 {par['percentis'].get(50)} ms, "
              f"p95 {par['percentis'].get(95)} ms, acerto {par['acerto']:.3f}")
    print(f"fim {hora(datetime.datetime.now().astimezone())}; falhas {len(medidor.falhas)}; custo US$ "
          f"{serie['custo_us'] + par['custo_us']:.5f}")
    texto = relatorio(jev, rtt, serie, par, medidor.falhas, medidor.parar)
    if ensaio:
        print("ensaio (< 200 por regime): resultados.md NÃO gravado")
        print(texto)
    else:
        RESULTADOS.write_text(texto, encoding="utf-8", newline="\n")
        print(f"gravado {RESULTADOS.name}: {veredito(serie, par, medidor.parar)[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
