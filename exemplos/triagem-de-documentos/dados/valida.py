"""Validador dos dados do triagem-de-documentos (rotulador). Só biblioteca padrão.

Uso: python -X utf8 exemplos/triagem-de-documentos/dados/valida.py
Confere envelope, esquema exato, IDs únicos, referências, tamanhos mínimos da spec, 4–8 seções de 60–200
palavras, `campos` fixos por tipo, ≥ 4 documentos verdadeiros por condição, `secao_que_prova` para cada
verdadeiro (seção do próprio documento), condições numéricas recalculadas pelos `campos`, ≥ 30% de condições
difíceis em ajuste e teste e presença dos seis tipos difíceis da spec. Sai com 1 se houver erro.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
AUTOR = "fable"
VERSAO = {"documentos.json": "2026-10-02", "rascunho.json": "2026-10-02", "condicoes_ajuste.json": "2026-10-02b",
          "condicoes_teste.json": "2026-10-02b"}  # v2: condições compostas (TD-A03, TD-T03)
TIPOS = {"locacao", "prestacao_servico", "ata_condominio", "proposta_comercial"}
CAMPOS = {
    "locacao": {"valor_aluguel": int, "prazo_meses": int, "multa_alugueis": (int, type(None)),
                "indice_reajuste": (str, type(None)), "garantia": str, "renovacao_automatica": bool},
    "prestacao_servico": {"valor_mensal": int, "prazo_meses": int, "multa_percentual": (int, type(None)),
                          "indice_reajuste": (str, type(None)), "exclusividade": bool, "renovacao_automatica": bool},
    "ata_condominio": {"data": str, "quorum_percentual": int, "taxa_valor": int, "reajuste_percentual": int,
                       "obra_aprovada": bool},
    "proposta_comercial": {"valor_total": int, "validade_dias": int, "prazo_entrega_dias": (int, type(None)),
                           "desconto_percentual": int, "garantia_meses": int},
}
NUMERICA = re.compile(r"`(\w+)`\s*(<=|>=|<|>)\s*(\d+)")
MINIMOS = {"rascunho.json": 5, "condicoes_ajuste.json": 6, "condicoes_teste.json": 12}
TIPOS_DIFICEIS = ["negada", "revogada", "duas seções", "termo só no título", "seção parecida", "sem a cláusula"]


def carrega(nome, chave):
    bruto = (AQUI / nome).read_bytes()
    erros = []
    if bruto.startswith(b"\xef\xbb\xbf"):
        erros.append(f"{nome}: BOM")
    if b"\r" in bruto:
        erros.append(f"{nome}: CRLF")
    obj = json.loads(bruto.decode("utf-8"))
    if set(obj) != {"versao", "autor", chave} or obj["versao"] != VERSAO[nome] or obj["autor"] != AUTOR:
        erros.append(f"{nome}: envelope deve ser versao={VERSAO[nome]}, autor={AUTOR}, {chave}")
    return obj.get(chave, []), erros


def tipo_ok(v, t) -> bool:
    if isinstance(v, bool):
        return t is bool
    return isinstance(v, t)


def main() -> int:
    erros: list[str] = []
    docs, e = carrega("documentos.json", "documentos"); erros += e
    if len(docs) < 40:
        erros.append(f"documentos.json: {len(docs)} documentos (< 40)")
    ids = [d.get("id") for d in docs]
    if len(set(ids)) != len(ids):
        erros.append("documentos.json: IDs repetidos")
    por_id, secoes_de = {}, {}
    for d in docs:
        did = d.get("id")
        if set(d) != {"id", "tipo", "secoes", "campos"}:
            erros.append(f"{did}: chaves do documento devem ser id, tipo, secoes, campos"); continue
        if d["tipo"] not in TIPOS:
            erros.append(f"{did}: tipo"); continue
        if not 4 <= len(d["secoes"]) <= 8:
            erros.append(f"{did}: {len(d['secoes'])} seções (fora de 4–8)")
        sids = set()
        for i, s in enumerate(d["secoes"], 1):
            if set(s) != {"id", "titulo", "texto"}:
                erros.append(f"{did}: seção {i} com chaves erradas"); continue
            if s["id"] != f"{did}-s{i}":
                erros.append(f"{did}: id da seção {i} deveria ser {did}-s{i}")
            n = len(s["texto"].split())
            if not 60 <= n <= 200:
                erros.append(f"{s['id']}: {n} palavras (fora de 60–200)")
            if not s["titulo"].strip():
                erros.append(f"{s['id']}: título vazio")
            sids.add(s["id"])
        esperados = CAMPOS[d["tipo"]]
        if set(d["campos"]) != set(esperados):
            erros.append(f"{did}: campos devem ser {sorted(esperados)}")
        else:
            for k, t in esperados.items():
                if not tipo_ok(d["campos"][k], t):
                    erros.append(f"{did}: campo {k} com tipo errado")
        por_id[did] = d; secoes_de[did] = sids
    tipos_doc = {}
    for d in docs:
        tipos_doc[d["tipo"]] = tipos_doc.get(d["tipo"], 0) + 1
    if set(tipos_doc) != TIPOS:
        erros.append(f"documentos.json: faltam tipos {TIPOS - set(tipos_doc)}")

    textos = {}
    resumo = {}
    for nome in MINIMOS:
        casos, e = carrega(nome, "casos"); erros += e
        if len(casos) < MINIMOS[nome]:
            erros.append(f"{nome}: {len(casos)} condições (< {MINIMOS[nome]})")
        cids = [c.get("id") for c in casos]
        if len(set(cids)) != len(cids):
            erros.append(f"{nome}: IDs repetidos")
        dificeis = 0
        for c in casos:
            cid = c.get("id")
            if set(c) != {"id", "condicao", "tipo", "documentos_verdadeiros", "documentos_indecidiveis",
                          "secao_que_prova", "nota"}:
                erros.append(f"{cid}: chaves da condição erradas"); continue
            if c["tipo"] not in ("semantica", "numerica"):
                erros.append(f"{cid}: tipo")
            verd, ind, prova = c["documentos_verdadeiros"], c["documentos_indecidiveis"], c["secao_que_prova"]
            if len(verd) < 4:
                erros.append(f"{cid}: {len(verd)} verdadeiros (< 4)")
            if len(set(verd)) != len(verd) or len(set(ind)) != len(ind):
                erros.append(f"{cid}: documento repetido na lista")
            if set(verd) & set(ind):
                erros.append(f"{cid}: documento verdadeiro e indecidível ao mesmo tempo")
            for did in verd + ind:
                if did not in por_id:
                    erros.append(f"{cid}: documento {did} não existe")
            if set(prova) != set(verd):
                erros.append(f"{cid}: secao_que_prova deve ter exatamente os verdadeiros")
            for did, sid in prova.items():
                if did in secoes_de and sid not in secoes_de[did]:
                    erros.append(f"{cid}: seção {sid} não pertence a {did}")
            if c["tipo"] == "numerica":
                m = NUMERICA.findall(c["condicao"])
                if len(m) != 1:
                    erros.append(f"{cid}: condição numérica precisa de exatamente uma expressão `campo` op valor")
                else:
                    campo, op, val = m[0]; val = int(val)
                    calc = []
                    for d in docs:
                        v = d["campos"].get(campo)
                        if v is None or isinstance(v, bool):
                            continue
                        if {"<": v < val, ">": v > val, "<=": v <= val, ">=": v >= val}[op]:
                            calc.append(d["id"])
                    if sorted(calc) != sorted(verd):
                        erros.append(f"{cid}: verdadeiros não batem com `{campo}` {op} {val} em campos: {sorted(calc)}")
                    if ind:
                        erros.append(f"{cid}: condição numérica não tem indecidíveis")
            if c["nota"].startswith("difícil:"):
                dificeis += 1
            elif not c["nota"].startswith("fácil"):
                erros.append(f"{cid}: nota deve começar com 'difícil: <tipo>' ou 'fácil'")
            textos.setdefault(c["condicao"], []).append((nome, cid))
        if nome != "rascunho.json" and casos and dificeis / len(casos) < 0.3:
            erros.append(f"{nome}: {dificeis}/{len(casos)} difíceis (< 30%)")
        resumo[nome] = (len(casos), dificeis)
    for texto, onde in textos.items():
        arqs = {a for a, _ in onde if a != "rascunho.json"}
        if len(arqs) > 1:
            erros.append(f"condição repetida entre ajuste e teste: {onde}")
    notas = " ".join(c["nota"] for nome in ("condicoes_ajuste.json", "condicoes_teste.json")
                     for c in carrega(nome, "casos")[0])
    for t in TIPOS_DIFICEIS:
        if t not in notas:
            erros.append(f"tipo difícil ausente nas notas: {t}")

    for err in erros:
        print("ERRO", err)
    print(json.dumps({"resultado": "passou" if not erros else "falhou", "erros": len(erros),
                      "documentos": len(docs), "por_tipo": tipos_doc,
                      "condicoes (total, difíceis)": resumo}, ensure_ascii=False))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
