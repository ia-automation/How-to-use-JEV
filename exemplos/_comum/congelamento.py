"""Congelamento auditável e validação de resposta — infra comum dos exemplos.

Por que existe (revisão adversarial do Codex, 2026-10-01, exemplos juiz-de-eval e guarda-tool-call):
  1. "Rodada única não é auditável": o hash no cabeçalho de resultados.md cobria só o código, podia ser
     recalculado a cada rodada e o cache em `ao_vivo` sobrescrevia a resposta anterior sem rastro. Aqui o
     congelamento vira um MANIFESTO gravado uma vez (`congelamento.json`): hashes de código, dados e critério
     de aceite, com data/hora. Rodar o teste exige que o manifesto exista e bata; mudar qualquer arquivo
     congelado exige congelar de novo, e o manifesto anterior fica guardado em `congelamentos-anteriores/`.
  2. "Booleano passa como probabilidade": `isinstance(True, int)` é verdadeiro em Python e `float("1")`
     converte string. `probabilidade()` exige número JSON real, finito, em [0, 1] — nunca bool nem string.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import shutil
from pathlib import Path

MANIFESTO = "congelamento.json"


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def hashes(pasta: Path, arquivos: list[str]) -> dict[str, str]:
    """{arquivo relativo: sha256} dos arquivos congelados (código, dados de teste, critério)."""
    return {a: _sha(pasta / a) for a in arquivos}


def congelar(pasta: Path, arquivos: list[str], criterio: dict | str) -> dict:
    """Grava o manifesto. Se já existia um diferente, guarda o antigo em `congelamentos-anteriores/<hora>.json`
    em vez de apagar (nada se apaga). Devolve o manifesto novo."""
    pasta = Path(pasta)
    novo = {
        "congelado_em": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "arquivos": hashes(pasta, arquivos),
        "criterio_de_aceite": criterio,
    }
    alvo = pasta / MANIFESTO
    if alvo.exists():
        antigo = json.loads(alvo.read_text(encoding="utf-8"))
        if antigo.get("arquivos") == novo["arquivos"] and antigo.get("criterio_de_aceite") == criterio:
            return antigo  # nada mudou: o manifesto original (e sua hora) permanece
        guarda = pasta / "congelamentos-anteriores"
        guarda.mkdir(exist_ok=True)
        shutil.move(str(alvo), str(guarda / f"{antigo['congelado_em'].replace(':', '-')}.json"))
    alvo.write_text(json.dumps(novo, ensure_ascii=False, indent=1), encoding="utf-8")
    return novo


def conferir(pasta: Path, arquivos: list[str]) -> dict:
    """Lê o manifesto e recusa a rodada se algum arquivo congelado mudou ou se não há manifesto."""
    pasta = Path(pasta)
    alvo = pasta / MANIFESTO
    if not alvo.exists():
        raise RuntimeError(f"sem {MANIFESTO}: rode `congelar` antes do teste")
    manifesto = json.loads(alvo.read_text(encoding="utf-8"))
    atual = hashes(pasta, arquivos)
    mudados = sorted(a for a in set(atual) | set(manifesto["arquivos"]) if atual.get(a) != manifesto["arquivos"].get(a))
    if mudados:
        raise RuntimeError(f"arquivos congelados mudaram desde {manifesto['congelado_em']}: {', '.join(mudados)}")
    return manifesto


def probabilidade(valor) -> float:
    """Aceita só número JSON (int/float, não bool, não string), finito, em [0, 1]; senão ValueError.
    Ausência ou tipo errado é ERRO da integração, nunca probabilidade 0 (integracao-segura)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"probabilidade com tipo inválido: {type(valor).__name__} ({valor!r})")
    v = float(valor)
    if not math.isfinite(v) or not 0.0 <= v <= 1.0:
        raise ValueError(f"probabilidade fora de [0, 1]: {v!r}")
    return v


def noul(resposta: dict, id_pergunta: str) -> float:
    """Valor de um Noul já validado (tipo, finitude, intervalo); erro se o ID não voltou ou o tipo não é noul."""
    a = (resposta.get("answers") or {}).get(id_pergunta)
    if not isinstance(a, dict) or a.get("type", "noul") != "noul" or "noul" not in a:
        raise ValueError(f"resposta sem Noul válido para {id_pergunta!r}")
    return probabilidade(a["noul"])


def choice(resposta: dict, id_pergunta: str, opcoes: set[str]) -> dict:
    """Choice validada: `choice` entre as opções esperadas, probabilidades reais somando ~1, confiança em [0, 1]."""
    a = (resposta.get("answers") or {}).get(id_pergunta)
    # O discriminador `type` também é conferido (revisão do Codex em proxima-pergunta, 2026-10-01): uma resposta
    # de outro tipo com campos parecidos não pode ser consumida como Choice. Ausente = aceito (cache antigo).
    if not isinstance(a, dict) or a.get("type", "choice") != "choice" or a.get("choice") not in opcoes:
        raise ValueError(f"resposta sem Choice válida para {id_pergunta!r}")
    probs = {k: probabilidade(v) for k, v in (a.get("probabilities") or {}).items()}
    if set(probs) != set(opcoes) or abs(sum(probs.values()) - 1.0) > 0.02:
        raise ValueError(f"probabilidades inválidas em {id_pergunta!r}: {probs}")
    # A opção escolhida tem de ser (uma das) de maior probabilidade (revisão do Codex em roteador-email,
    # 2026-10-01): `choice=principal` com P(golpe)=1 é resposta contraditória, não decisão. Folga de 0,025 porque a
    # API arredonda as probabilidades: em 4.272 Choices reais do cache, 4 tinham a escolhida 0,01 abaixo do máximo
    # e nenhuma mais que isso [testado, jev-1.13.0].
    if max(probs.values()) - probs[a["choice"]] > 0.025:
        raise ValueError(f"Choice contraditória em {id_pergunta!r}: escolhida {a['choice']!r} não é a de maior probabilidade")
    return {"choice": a["choice"], "probabilities": probs, "confidence": probabilidade(a.get("confidence"))}
