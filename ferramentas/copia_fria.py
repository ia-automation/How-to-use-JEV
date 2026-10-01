"""Cópia fria do repositório JEV — o pacote que um agente "frio" recebe para ser testado.

Exporta por LISTA PERMITIDA, arquivo a arquivo, para C:\\tmp\\jev-frio-<AAAAMMDD-HHMMSS>:
  - da raiz, só as entradas de PERMITIDO_NA_RAIZ; as de EXCLUIDO_NA_RAIZ ficam de fora (prova/ e gabarito,
    fontes/ integrais, chat.txt, .local/, .git/, api_key.txt, .venv/); QUALQUER outra entrada na raiz
    interrompe a exportação até ser classificada aqui (arquivo novo não entra por omissão);
  - dentro das pastas permitidas, só arquivos com extensão de EXTENSOES_PERMITIDAS; extensão inesperada,
    nome de credencial (.env*, *.pem, *.key, credentials*.json) ou link/ponto de reparse interrompe;
  - node_modules/ e __pycache__/ são pulados (ambiente, não conhecimento).
Depois confere na cópia, sem imprimir segredo:
  - o VALOR da chave local (api_key.txt ou TYPESAFE_API_KEY) não aparece em nenhum arquivo de texto;
  - ferramentas/validar.py passa na cópia (links resolvem, índice, frontmatter, JSON, skills, segredo).
Grava um manifesto ao lado da cópia (<destino>.manifesto.json) com as regras, a lista materializada de
arquivos (caminho + sha256) e o hash da árvore.

Limite: é uma cópia por lista permitida, não um ambiente isolado — quem roda a prova na mesma máquina ainda
alcança o resto do disco. Protocolo e limites: conhecimento/avaliar/prova-fria.md.

Uso (Python 3.12 testado; só biblioteca padrão):
    python -X utf8 ferramentas/copia_fria.py [--base C:\\tmp]
    python -X utf8 ferramentas/copia_fria.py --publicar <pasta do repositório público>
      (versão pública: inclui fontes/catalogo e fontes/skill-oficial; nunca privado/, prova/, .local/)
Sai com código 1 se a exportação ou a conferência falhar (a cópia parcial fica no disco para inspeção).
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PERMITIDO_NA_RAIZ = {"AGENTS.md", "CLAUDE.md", "README.md", "CHANGELOG.md", "LICENSE", "LICENSE-CONTEUDO.md",
                     ".gitignore", ".claude-plugin", "avaliar", "conhecimento", "exemplos", "ferramentas", "skills"}
EXCLUIDO_NA_RAIZ = {"prova", "privado", "fontes", "chat.txt", ".local", ".git", "api_key.txt", ".venv"}
# --publicar: a versão pública leva também fontes/ (catálogo e skill oficial MIT), nunca o material integral.
PERMITIDO_NA_RAIZ_PUBLICO = PERMITIDO_NA_RAIZ | {"fontes"}
PULAR_NO_PUBLICO = {"fontes/docs", "fontes/videos"}
NOMES_SEM_EXTENSAO = {".gitignore", "LICENSE"}
PULAR_EM_QUALQUER_NIVEL = {"node_modules", "__pycache__"}
EXTENSOES_PERMITIDAS = {".md", ".py", ".ts", ".json"}
NOMES_DE_CREDENCIAL = [".env", ".env.*", "*.pem", "*.key", "credentials*.json"]


def e_link(p: Path) -> bool:
    """Link simbólico, junção ou qualquer ponto de reparse do Windows (pode apontar para fora da árvore)."""
    st = os.lstat(p)
    return stat.S_ISLNK(st.st_mode) or bool(getattr(st, "st_file_attributes", 0) & 0x400)


def selecionar(problemas: list[str], permitido: set[str] = PERMITIDO_NA_RAIZ,
               pular: set[str] | frozenset[str] = frozenset()) -> list[Path]:
    """Percorre a raiz e devolve os arquivos permitidos (relativos); registra tudo o que for inesperado."""
    escolhidos: list[Path] = []
    for entrada in sorted(RAIZ.iterdir()):
        if entrada.name in EXCLUIDO_NA_RAIZ - permitido:
            continue
        if entrada.name not in permitido:
            problemas.append(f"entrada da raiz fora da lista: {entrada.name} (classificar em copia_fria.py)")
            continue
        pilha = [entrada]
        while pilha:
            p = pilha.pop()
            rel = p.relative_to(RAIZ).as_posix()
            if rel in pular:
                continue
            if e_link(p):
                problemas.append(f"link/ponto de reparse: {rel}")
            elif p.is_dir():
                pilha += [f for f in p.iterdir() if f.name not in PULAR_EM_QUALQUER_NIVEL]
            elif any(fnmatch.fnmatch(p.name.lower(), m) for m in NOMES_DE_CREDENCIAL):
                problemas.append(f"nome de credencial: {rel}")
            elif p.suffix.lower() not in EXTENSOES_PERMITIDAS and p.name not in NOMES_SEM_EXTENSAO:
                problemas.append(f"extensão fora da lista: {rel}")
            else:
                escolhidos.append(p.relative_to(RAIZ))
    return sorted(escolhidos)


def carregar_validar():
    spec = importlib.util.spec_from_file_location("validar", RAIZ / "ferramentas" / "validar.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", type=Path, default=Path(r"C:\tmp"))
    ap.add_argument("--publicar", type=Path, metavar="PASTA",
                    help="gera/atualiza a versão pública nesta pasta (pode já ter .git); manifesto em .local/publicacoes/")
    args = ap.parse_args()
    hora = f"{datetime.now():%Y%m%d-%H%M%S}"
    destino = args.publicar or args.base / f"jev-frio-{hora}"

    problemas: list[str] = []
    if args.publicar:
        arquivos = selecionar(problemas, PERMITIDO_NA_RAIZ_PUBLICO, PULAR_NO_PUBLICO)
    else:
        arquivos = selecionar(problemas)
    if problemas:  # nada é copiado enquanto houver entrada não classificada
        for p in problemas:
            print("ERRO ", p)
        sys.exit(1)

    lista, total, bytes_ = [], hashlib.sha256(), 0
    for rel in arquivos:
        alvo = destino / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / rel, alvo)
        dados = alvo.read_bytes()
        h = hashlib.sha256(dados).hexdigest()
        lista.append({"caminho": rel.as_posix(), "sha256": h})
        total.update(rel.as_posix().encode() + b"\0" + bytes.fromhex(h))
        bytes_ += len(dados)

    if args.publicar:  # sincronização: o que sobrou no destino é relatado, nunca apagado sozinho
        selecionados = {r.as_posix() for r in arquivos}
        for p in destino.rglob("*"):
            r = p.relative_to(destino).as_posix()
            if p.is_file() and not r.startswith(".git/") and r not in selecionados:
                problemas.append(f"sobra no destino (fora da seleção; apagar à mão se for o caso): {r}")

    validar = carregar_validar()
    # A chave de referência é a da raiz original: a cópia não tem api_key.txt.
    erros, avisos, stats = validar.validar(destino, arquivo_chave=RAIZ / "api_key.txt")
    problemas += erros

    manifesto = {
        "origem": str(RAIZ),
        "destino": str(destino),
        "criado_em": datetime.now().isoformat(timespec="seconds"),
        "metodo": "lista permitida (entradas da raiz + extensões), arquivo a arquivo; inesperado interrompe",
        "permitido_na_raiz": sorted(PERMITIDO_NA_RAIZ),
        "excluido_na_raiz": sorted(EXCLUIDO_NA_RAIZ),
        "pulado_em_qualquer_nivel": sorted(PULAR_EM_QUALQUER_NIVEL),
        "extensoes_permitidas": sorted(EXTENSOES_PERMITIDAS),
        "arquivos": len(lista),
        "bytes": bytes_,
        "sha256_da_arvore": total.hexdigest(),
        "chave_local_conferida": stats.get("chave_local_conhecida", False),
        "validar": {"erros": len(erros), "avisos": len(avisos), **stats},
        "resultado": "ok" if not problemas else "falhou",
        "lista": lista,
    }
    saida = (RAIZ / ".local" / "publicacoes" / f"{hora}.manifesto.json") if args.publicar \
        else Path(str(destino) + ".manifesto.json")
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for p in problemas:
        print("ERRO ", p)
    print(json.dumps({k: manifesto[k] for k in ("destino", "arquivos", "sha256_da_arvore", "resultado")},
                     ensure_ascii=False))
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
