"""Validador dos dados do comparador-de-propostas (rotulador). Só biblioteca padrão.

Uso: python -X utf8 exemplos/comparador-de-propostas/dados/valida.py
Confere esquema exato, IDs únicos, referências, 3 propostas por disputa, tamanhos mínimos, trechos literais,
requisito numérico resolvível pelos `campos` (recalcula a célula), coerência matriz × elegíveis e contagem de
difíceis (≥ 30%). Sai com 1 se houver erro.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NUM = re.compile(r"\(`(\w+)` (<=|>=) (\d+)\)")
STATUS = {"atende", "contradiz", "nao_informado"}
FAMILIAS = ("exclusão escondida", "promessa condicionada", "termo vago", "anexo citado mas ausente",
            "atende tudo menos o prazo")
MINIMOS = {"ajuste.json": 10, "teste.json": 20, "rascunho.json": 5}


def carrega(nome):
    bruto = (AQUI / nome).read_bytes()
    erros = []
    if bruto.startswith(b"\xef\xbb\xbf"):
        erros.append(f"{nome}: BOM")
    if b"\r" in bruto:
        erros.append(f"{nome}: CRLF")
    obj = json.loads(bruto.decode("utf-8"))
    if set(obj) != {"versao", "autor", "casos"} or obj["versao"] not in ("2026-10-01", "2026-10-02") or obj["autor"] != "fable":
        erros.append(f"{nome}: envelope")
    return obj, erros


def checa_caso(nome, c, erros):
    cid = c.get("id")
    if set(c) != {"id", "requisitos", "propostas", "matriz", "trechos", "elegiveis", "nota"}:
        erros.append(f"{nome} {cid}: esquema do caso"); return False
    reqs, props = c["requisitos"], c["propostas"]
    rids = [r.get("id") for r in reqs]; pids = [p.get("id") for p in props]
    if len(props) != 3:
        erros.append(f"{nome} {cid}: {len(props)} propostas (≠ 3)")
    if len(set(rids)) != len(rids) or len(set(pids)) != len(pids):
        erros.append(f"{nome} {cid}: IDs repetidos")
    for r in reqs:
        if set(r) != {"id", "texto", "obrigatorio", "tipo"} or not isinstance(r["obrigatorio"], bool) \
                or r["tipo"] not in ("semantico", "numerico"):
            erros.append(f"{nome} {cid} {r.get('id')}: esquema do requisito")
        if r.get("tipo") == "numerico" and not NUM.search(r.get("texto", "")):
            erros.append(f"{nome} {cid} {r.get('id')}: numérico sem (`campo` op valor)")
        if r.get("tipo") == "semantico" and "`" in r.get("texto", ""):
            erros.append(f"{nome} {cid} {r.get('id')}: semântico não leva campo")
    for p in props:
        if set(p) != {"id", "texto", "campos"} or not isinstance(p["campos"], dict):
            erros.append(f"{nome} {cid} {p.get('id')}: esquema da proposta")
    if set(c["matriz"]) != set(pids) or set(c["trechos"]) != set(pids):
        erros.append(f"{nome} {cid}: matriz/trechos devem ter exatamente as 3 propostas")
    dif = False
    for p in props:
        pid = p["id"]
        m, t = c["matriz"].get(pid, {}), c["trechos"].get(pid, {})
        if set(m) != set(rids) or set(t) != set(rids):
            erros.append(f"{nome} {cid} {pid}: matriz/trechos devem ter exatamente os requisitos"); continue
        for r in reqs:
            rid, st, tr = r["id"], m[r["id"]], t[r["id"]]
            if st not in STATUS:
                erros.append(f"{nome} {cid} {pid} {rid}: status {st}")
            if st == "nao_informado":
                if tr is not None:
                    erros.append(f"{nome} {cid} {pid} {rid}: nao_informado com trecho")
                dif = True
            else:
                if not isinstance(tr, str) or tr not in p["texto"]:
                    erros.append(f"{nome} {cid} {pid} {rid}: trecho não é substring literal")
            if r["tipo"] == "numerico":
                campo, op, lim = NUM.search(r["texto"]).groups()
                if campo not in p["campos"]:
                    erros.append(f"{nome} {cid} {pid}: campo {campo} ausente"); continue
                v = p["campos"][campo]
                if v is None:
                    esperado = "nao_informado"
                elif not isinstance(v, (int, float)) or isinstance(v, bool):
                    erros.append(f"{nome} {cid} {pid}: campo {campo} não numérico"); continue
                else:
                    esperado = "atende" if ((v <= int(lim)) if op == "<=" else (v >= int(lim))) else "contradiz"
                if st != esperado:
                    erros.append(f"{nome} {cid} {pid} {rid}: matriz {st} ≠ campos {esperado}")
    esperado = [p["id"] for p in props
                if not any(c["matriz"][p["id"]][r["id"]] == "contradiz" for r in reqs if r["obrigatorio"])]
    if c["elegiveis"] != esperado:
        erros.append(f"{nome} {cid}: elegiveis {c['elegiveis']} ≠ {esperado}")
    nota = c["nota"]
    if nota.startswith("difícil:"):
        if not any(nota.startswith(f"difícil: {f}") for f in FAMILIAS):
            erros.append(f"{nome} {cid}: família de difícil desconhecida")
        return True
    if not nota.startswith("fácil"):
        erros.append(f"{nome} {cid}: nota deve começar com 'difícil: <família>' ou 'fácil'")
    return False


def main() -> int:
    erros: list[str] = []
    todos = set()
    for nome, minimo in MINIMOS.items():
        obj, e = carrega(nome); erros += e
        casos = obj["casos"]
        if len(casos) < minimo:
            erros.append(f"{nome}: {len(casos)} disputas (< {minimo})")
        ids = [c.get("id") for c in casos]
        if len(set(ids)) != len(ids) or set(ids) & todos:
            erros.append(f"{nome}: IDs repetidos (no arquivo ou entre arquivos)")
        todos |= set(ids)
        dificeis = sum(checa_caso(nome, c, erros) for c in casos)
        if nome != "rascunho.json" and casos and dificeis / len(casos) < 0.3:
            erros.append(f"{nome}: {dificeis}/{len(casos)} difíceis (< 30%)")
        fam = {f: sum(c["nota"].startswith(f"difícil: {f}") for c in casos) for f in FAMILIAS}
        print(f"{nome}: {len(casos)} disputas, {dificeis} difíceis {fam}, elegíveis por disputa "
              f"{[len(c.get('elegiveis', [])) for c in casos]}")
    for err in erros:
        print("ERRO:", err)
    print("OK" if not erros else f"{len(erros)} erro(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
