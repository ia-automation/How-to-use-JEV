"""Validador dos dados do sql-semantico (rotulador). Só biblioteca padrão.

Uso: python -X utf8 exemplos/sql-semantico/dados/valida.py
Confere esquema exato, IDs únicos, referências, tamanhos mínimos da spec, ≥ 4 linhas verdadeiras por
condição, parte numérica resolvível pelos `campos` e contagem de difíceis (≥ 30%). Sai com 1 se houver erro.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CAMPOS = {"data": str, "canal": str, "finalidade": str, "orcamento": (int, type(None)), "visitas": int, "etapa": str}
CANAIS = {"whatsapp", "telefone", "email", "presencial"}
FINALIDADES = {"compra", "locacao"}
ETAPAS = {"novo", "em_contato", "visita", "proposta", "perdido"}
NUMERICO = re.compile(r"`(data|canal|finalidade|orcamento|visitas|etapa)`\s*(<=|>=|=|em)\s*([\w-]+)")
MINIMOS = {"condicoes_ajuste.json": 8, "condicoes_teste.json": 16, "rascunho.json": 5}


def carrega(nome):
    bruto = (AQUI / nome).read_bytes()
    erros = []
    if bruto.startswith(b"\xef\xbb\xbf"):
        erros.append(f"{nome}: BOM")
    if b"\r" in bruto:
        erros.append(f"{nome}: CRLF")
    obj = json.loads(bruto.decode("utf-8"))
    if obj.get("versao") != "2026-10-01" or obj.get("autor") != "fable":
        erros.append(f"{nome}: envelope (versao/autor)")
    return obj, erros


def main() -> int:
    erros: list[str] = []
    linhas, e = carrega("linhas.json"); erros += e
    if set(linhas) != {"versao", "autor", "linhas"}:
        erros.append("linhas.json: envelope deve ter exatamente versao, autor, linhas")
    ls = linhas.get("linhas", [])
    if len(ls) < 150:
        erros.append(f"linhas.json: {len(ls)} linhas (< 150)")
    ids = [l.get("id") for l in ls]
    if len(set(ids)) != len(ids):
        erros.append("linhas.json: IDs repetidos")
    por_id = {}
    for l in ls:
        if set(l) != {"id", "texto", "campos"}:
            erros.append(f"{l.get('id')}: campos da linha devem ser id, texto, campos")
            continue
        c = l["campos"]
        if set(c) != set(CAMPOS):
            erros.append(f"{l['id']}: campos devem ser {sorted(CAMPOS)}")
        else:
            for k, t in CAMPOS.items():
                if not isinstance(c[k], t) or isinstance(c[k], bool):
                    erros.append(f"{l['id']}: campo {k} com tipo errado")
            if not re.fullmatch(r"2026-\d\d-\d\d", c["data"]): erros.append(f"{l['id']}: data")
            if c["canal"] not in CANAIS: erros.append(f"{l['id']}: canal")
            if c["finalidade"] not in FINALIDADES: erros.append(f"{l['id']}: finalidade")
            if c["etapa"] not in ETAPAS: erros.append(f"{l['id']}: etapa")
            if c["visitas"] < 0: erros.append(f"{l['id']}: visitas")
        if not (1 <= len(re.findall(r"[.!?](\s|$)", l["texto"])) <= 3):
            erros.append(f"{l['id']}: texto fora de 1–3 frases")
        por_id[l["id"]] = l

    def numerico_ok(cond: str) -> bool:
        """Toda parte numérica/categórica entre crases precisa referir campo existente e ser resolvível."""
        for campo, op, val in NUMERICO.findall(cond):
            if campo in ("orcamento", "visitas"):
                if not val.isdigit() or op not in ("<=", ">="):
                    return False
            elif campo == "data":
                if not re.fullmatch(r"2026-\d\d", val):
                    return False
            elif campo == "canal" and val not in CANAIS: return False
            elif campo == "finalidade" and val not in FINALIDADES: return False
            elif campo == "etapa" and val not in ETAPAS: return False
        return True

    resumo = {}
    for nome, minimo in MINIMOS.items():
        obj, e = carrega(nome); erros += e
        if set(obj) != {"versao", "autor", "casos"}:
            erros.append(f"{nome}: envelope deve ter exatamente versao, autor, casos")
        casos = obj.get("casos", [])
        if len(casos) < minimo:
            erros.append(f"{nome}: {len(casos)} condições (< {minimo})")
        cids = [c.get("id") for c in casos]
        if len(set(cids)) != len(cids):
            erros.append(f"{nome}: IDs repetidos")
        dificeis = 0
        for c in casos:
            if set(c) != {"id", "condicao", "linhas_verdadeiras", "linhas_indecidiveis", "nota"}:
                erros.append(f"{nome} {c.get('id')}: esquema do caso")
                continue
            v, i = c["linhas_verdadeiras"], c["linhas_indecidiveis"]
            for lid in v + i:
                if lid not in por_id:
                    erros.append(f"{nome} {c['id']}: linha inexistente {lid}")
            if len(set(v)) != len(v) or len(set(i)) != len(i) or set(v) & set(i):
                erros.append(f"{nome} {c['id']}: repetição ou sobreposição verdadeiras/indecidíveis")
            if len(v) < 4:
                erros.append(f"{nome} {c['id']}: só {len(v)} linhas verdadeiras (< 4)")
            if not numerico_ok(c["condicao"]):
                erros.append(f"{nome} {c['id']}: parte numérica não resolvível pelos campos")
            if "`" in c["condicao"] and not NUMERICO.search(c["condicao"]):
                erros.append(f"{nome} {c['id']}: crase sem campo reconhecido")
            if not re.match(r"^(difícil: (negação|composta|inferência fraca)|fácil)", c["nota"]):
                erros.append(f"{nome} {c['id']}: nota deve começar com 'difícil: <tipo>' ou 'fácil'")
            dificeis += c["nota"].startswith("difícil")
        if nome != "rascunho.json" and casos and dificeis / len(casos) < 0.3:
            erros.append(f"{nome}: {dificeis}/{len(casos)} difíceis (< 30%)")
        resumo[nome] = (len(casos), dificeis, [len(c["linhas_verdadeiras"]) for c in casos])

    teste = json.loads((AQUI / "condicoes_teste.json").read_text(encoding="utf-8"))["casos"]
    ajuste = json.loads((AQUI / "condicoes_ajuste.json").read_text(encoding="utf-8"))["casos"]
    if {c["condicao"] for c in teste} & {c["condicao"] for c in ajuste}:
        erros.append("condição repetida entre ajuste e teste")

    for nome, (n, d, vs) in resumo.items():
        print(f"{nome}: {n} condições, {d} difíceis, verdadeiras por condição {vs}")
    print(f"linhas.json: {len(ls)} linhas")
    for err in erros:
        print("ERRO:", err)
    print("OK" if not erros else f"{len(erros)} erro(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
