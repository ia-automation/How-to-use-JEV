"""Validador dos dados do supervisor-de-automacao (rotulador). Só biblioteca padrão.

Uso: python -X utf8 exemplos/supervisor-de-automacao/dados/valida.py
Confere envelope, esquema exato, IDs únicos e em sequência por trajetória, `acao` no enum, `rotina` só com
`recuperacao_conhecida` e existente no catálogo, `aceitaveis` contendo `acao`, histórico de 0–3 passos, mínimos da
spec (rotinas 5–7, ajuste ≥ 15 e teste ≥ 30 trajetórias com 2–4 estados cada), precedência (efeito submetido sem
resposta → nunca `continuar`; credencial/2FA/captcha/confirmação → `pedir_ajuda`), ≥ 30% de estados difíceis,
split por (causa, interface) sem repetição entre ajuste e teste e ausência de credencial no estado. Sai com 1 se erro.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VERSAO, AUTOR = "2026-10-02", "fable"
ACOES = {"continuar", "aguardar", "reler_estado", "recuperacao_conhecida", "pedir_ajuda"}
TIPOS_PASSO = {"navegar", "clicar", "preencher", "submeter", "aguardar", "reler_estado", "recuperacao", "nenhuma"}
INTERFACES = ("Nimbus: ", "Tabular: ", "Portal NFS-e: ")
CHAVES_CASO = ["id", "trajetoria", "causa", "objetivo", "acao_anterior", "historico", "estado_observado", "acao",
               "aceitaveis", "rotina", "nota"]
MIN_TRAJ = {"ajuste.json": 15, "teste.json": 30}
CREDENCIAL = re.compile(r"(?i)(senha\s*[:=]\s*\S|token\s*[:=]|bearer\s|cookie|cpf|\b\d{3}\.\d{3}\.\d{3}-\d{2}\b)")
CONFIRMACAO = re.compile(r"(?i)(campo: (senha|código|e-mail|usuário)|captcha|não é um robô|não pode ser desfeita|deseja (enviar|emitir)|confirmar (emissão|baixa))")


def carrega(nome, chave):
    bruto = (AQUI / nome).read_bytes()
    erros = []
    if bruto.startswith(b"\xef\xbb\xbf"):
        erros.append(f"{nome}: BOM")
    if b"\r" in bruto:
        erros.append(f"{nome}: CRLF")
    obj = json.loads(bruto.decode("utf-8"))
    if set(obj) != {"versao", "autor", chave} or obj["versao"] != VERSAO or obj["autor"] != AUTOR:
        erros.append(f"{nome}: envelope deve ser versao={VERSAO}, autor={AUTOR}, {chave}")
    return obj.get(chave, []), erros


def passo_ok(p) -> bool:
    return isinstance(p, dict) and set(p) == {"tipo", "alvo"} and p["tipo"] in TIPOS_PASSO and isinstance(p["alvo"], str)


def main() -> int:
    erros: list[str] = []
    rotinas, e = carrega("rotinas.json", "rotinas"); erros += e
    if not 5 <= len(rotinas) <= 7:
        erros.append(f"rotinas.json: {len(rotinas)} rotinas (fora de 5–7)")
    rot_ids = set()
    for r in rotinas:
        if set(r) != {"id", "nome", "pre_condicao"}:
            erros.append(f"rotinas.json: rotina com chaves erradas: {r.get('id')}")
        rot_ids.add(r.get("id"))
    if len(rot_ids) != len(rotinas):
        erros.append("rotinas.json: IDs repetidos")

    pares = {}
    resumo = {}
    for nome in ("rascunho.json", "ajuste.json", "teste.json"):
        casos, e = carrega(nome, "casos"); erros += e
        ids = [c.get("id") for c in casos]
        if len(set(ids)) != len(ids):
            erros.append(f"{nome}: IDs repetidos")
        traj: dict[str, list] = {}
        dificeis = 0
        por_acao = {a: 0 for a in ACOES}
        for c in casos:
            cid = c.get("id")
            if list(c) != CHAVES_CASO:
                erros.append(f"{cid}: chaves do caso devem ser {CHAVES_CASO}"); continue
            traj.setdefault(c["trajetoria"], []).append(c)
            if not cid.startswith(c["trajetoria"] + "-"):
                erros.append(f"{cid}: id não começa pela trajetória")
            if not c["objetivo"].startswith(INTERFACES):
                erros.append(f"{cid}: objetivo deve começar com a interface {INTERFACES}")
            if not passo_ok(c["acao_anterior"]):
                erros.append(f"{cid}: acao_anterior")
            if not isinstance(c["historico"], list) or not 0 <= len(c["historico"]) <= 3 or not all(map(passo_ok, c["historico"])):
                erros.append(f"{cid}: historico deve ter 0–3 passos {{tipo, alvo}}")
            eo = c["estado_observado"]
            if set(eo) != {"titulo", "texto_visivel", "elementos"} or not isinstance(eo["titulo"], str) \
                    or not isinstance(eo["texto_visivel"], list) or not isinstance(eo["elementos"], list):
                erros.append(f"{cid}: estado_observado")
            if c["acao"] not in ACOES:
                erros.append(f"{cid}: acao {c['acao']}")
            por_acao[c["acao"]] = por_acao.get(c["acao"], 0) + 1
            if not isinstance(c["aceitaveis"], list) or c["acao"] not in c["aceitaveis"] or not set(c["aceitaveis"]) <= ACOES:
                erros.append(f"{cid}: aceitaveis deve conter acao e só ações válidas")
            if c["acao"] == "recuperacao_conhecida":
                if c["rotina"] not in rot_ids:
                    erros.append(f"{cid}: rotina {c['rotina']} não está no catálogo")
            elif c["rotina"] is not None:
                erros.append(f"{cid}: rotina só com recuperacao_conhecida")
            if c["nota"].startswith("difícil:"):
                dificeis += 1
            elif not c["nota"].startswith("fácil"):
                erros.append(f"{cid}: nota deve começar com 'difícil: <família>' ou 'fácil'")
            tela = " ".join([eo["titulo"], *eo["texto_visivel"], *eo["elementos"]])
            if CREDENCIAL.search(tela):
                erros.append(f"{cid}: credencial, cookie ou CPF no estado")
            # precedência: credencial / 2FA / captcha / confirmação de efeito → pedir_ajuda
            if CONFIRMACAO.search(tela) and c["acao"] != "pedir_ajuda":
                erros.append(f"{cid}: tela de credencial ou confirmação de efeito exige pedir_ajuda")
            # precedência: efeito submetido sem resposta → nunca continuar
            if c["acao_anterior"]["tipo"] == "submeter" and c["acao"] == "continuar":
                # prova do efeito: aviso explícito OU o dado gravado visível (registro com data, linha da grade)
                confirmado = re.search(r"(?i)(autorizada|emitida|enviados|concluíd|cadastrado em|salvas|substituídas|agendado|alterado em|status: pago|em atendimento|\bA2: )", tela)
                if not confirmado:
                    erros.append(f"{cid}: continuar após submeter sem confirmação do efeito na tela")
            if c["acao"] == "continuar" and re.search(r"(?i)(tempo limite|timeout|esgotado|err_network|falha de rede)", tela):
                erros.append(f"{cid}: continuar com resultado desconhecido na tela")
        for tid, lst in traj.items():
            n = len(lst)
            if nome != "rascunho.json" and not 2 <= n <= 4:
                erros.append(f"{tid}: {n} estados (fora de 2–4)")
            if [c["id"] for c in lst] != [f"{tid}-{i}" for i in range(1, n + 1)]:
                erros.append(f"{tid}: estados fora de sequência")
            if len({c["causa"] for c in lst}) != 1 or len({c["objetivo"] for c in lst}) != 1:
                erros.append(f"{tid}: causa e objetivo devem ser os mesmos em toda a trajetória")
            interface = lst[0]["objetivo"].split(":")[0]
            pares.setdefault((lst[0]["causa"], interface), set()).add(nome)
        if nome in MIN_TRAJ and len(traj) < MIN_TRAJ[nome]:
            erros.append(f"{nome}: {len(traj)} trajetórias (< {MIN_TRAJ[nome]})")
        if nome != "rascunho.json" and casos and dificeis / len(casos) < 0.3:
            erros.append(f"{nome}: {dificeis}/{len(casos)} difíceis (< 30%)")
        resumo[nome] = {"trajetorias": len(traj), "estados": len(casos), "dificeis": dificeis, "acoes": por_acao}
    for (causa, interface), arqs in pares.items():
        if {"ajuste.json", "teste.json"} <= arqs:
            erros.append(f"split: causa '{causa}' em {interface} aparece em ajuste E teste")
    for err in erros:
        print("ERRO", err)
    print(json.dumps({"resultado": "passou" if not erros else "falhou", "erros": len(erros), "rotinas": len(rotinas),
                      "arquivos": resumo}, ensure_ascii=False))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
