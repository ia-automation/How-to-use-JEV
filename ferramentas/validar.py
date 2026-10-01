"""Validador do repositório JEV — roda antes de encerrar qualquer mudança.

Confere, no pacote versionável (tudo exceto .git, .venv, .local, node_modules, __pycache__ e o material de
terceiros em fontes/docs e fontes/videos):
  1. links Markdown relativos resolvem e não apontam para o que fica fora da cópia fria
     (prova/, fontes/, .local/, chat.txt, api_key.txt); nenhum [[wikilink]];
  2. frontmatter das notas de conhecimento/ (name = arquivo, description, tipo, fonte, estudado_em);
  3. toda nota de conhecimento/ aparece em conhecimento/INDICE.md;
  4. todo .json é válido; o par requisição/resposta mock e a semente de avaliação são coerentes;
  5. frontmatter das skills (name = pasta, description) e tamanho do SKILL.md;
  6. nenhum padrão de chave/segredo e nenhuma ocorrência do valor da chave local;
  7. hashes do catálogo de fontes, quando o arquivo local existe;
  8. .gitignore exclui material de terceiros e segredo; CLAUDE.md importa AGENTS.md.

Uso:
    python -X utf8 ferramentas/validar.py [--raiz CAMINHO] [--chave ARQUIVO]   (Python 3.12 testado)
Sai com código 1 se houver erro. Nunca imprime o valor de um segredo: só arquivo e linha.
Só usa a biblioteca padrão.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

IGNORAR_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".local"}
# Material de terceiros integral (fora do Git) e o que não é conteúdo do pacote.
IGNORAR_PREFIXOS = ("fontes/docs/", "fontes/videos/")
# O que copia_fria.py não leva: um link para cá quebraria na sessão fria.
FORA_DA_COPIA_FRIA = ("prova/", "privado/", "fontes/", ".local/", ".git/")
FORA_DA_COPIA_FRIA_ARQUIVOS = {"chat.txt", "api_key.txt"}
# Arquivos que não se validam como conteúdo (segredo e coordenação), mas entram na varredura de chave como aviso.
ARQUIVOS_SENSIVEIS = {"api_key.txt", "chat.txt"}

TIPOS_NOTA = {"conceito", "padrao", "receita", "sdk", "limite", "referencia", "principio",
              "pendencia", "visao-externa", "medicao"}
CAMPOS_NOTA = ("name", "description", "tipo", "fonte", "estudado_em")
MAX_LINHAS_SKILL = 120
EXT_TEXTO = {".md", ".py", ".ts", ".js", ".json", ".txt", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".csv", ".html"}

PADROES_SEGREDO = [
    ("chave estilo sk-", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("chave AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("chave privada PEM", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("token GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("token Slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("chave Google", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Bearer literal", re.compile(r"Bearer\s+[A-Za-z0-9._\-]{24,}")),
    ("atribuição de segredo", re.compile(
        r"(?i)\b(api[_-]?key|secret|token|senha|password)\b\s*[:=]\s*[\"']"
        r"(?-i:(?![A-Z][A-Z0-9_]*[\"']))[A-Za-z0-9_\-\.]{16,}[\"']")),
]
# O (?!...) aceita o NOME de uma variável de ambiente (ex.: "TYPESAFE_API_KEY"), que não é segredo.

LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
WIKI = re.compile(r"\[\[[^\]\n]+\]\]")
CERCA = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)
INLINE = re.compile(r"`[^`\n]*`")


def rel(p: Path, raiz: Path) -> str:
    return p.relative_to(raiz).as_posix()


def arquivos(raiz: Path):
    """Arquivos do pacote (sem .git, .venv, .local, node_modules, caches de bytecode, terceiros)."""
    for dirpath, dirnames, filenames in os.walk(raiz):
        dirnames[:] = [d for d in dirnames if d not in IGNORAR_DIRS]
        base = Path(dirpath)
        for nome in filenames:
            p = base / nome
            r = rel(p, raiz)
            if r.startswith(IGNORAR_PREFIXOS):
                continue
            yield p, r


def sem_codigo(texto: str) -> str:
    """Remove blocos e trechos de código, onde colchetes não são links."""
    return INLINE.sub("", CERCA.sub("", texto))


def frontmatter(texto: str):
    """Frontmatter simples `chave: valor` (com suporte a `>` dobrado). Devolve dict ou None."""
    if not texto.startswith("---\n"):
        return None
    fim = texto.find("\n---", 4)
    if fim < 0:
        return None
    campos, chave = {}, None
    for linha in texto[4:fim].splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s?(.*)$", linha)
        if m and not linha.startswith(" "):
            chave = m.group(1)
            campos[chave] = m.group(2).strip()
        elif chave and linha.startswith(" "):
            campos[chave] = (campos[chave] + " " + linha.strip()).strip()
    for k, v in campos.items():
        if v in (">", "|", ">-", "|-"):
            campos[k] = ""
    # valor dobrado ('>') foi concatenado acima; limpar marcador
    return {k: (v[1:].strip() if v.startswith(">") else v) for k, v in campos.items()}


def yaml_inseguro(valor: str) -> bool:
    """Heurística sem PyYAML: escalar simples que um parser YAML recusaria ou leria diferente."""
    if not valor:
        return False
    if valor[0] in "\"'" :
        return not (len(valor) >= 2 and valor[-1] == valor[0])
    if valor[0] in "&*!%@`[{|>":
        return True
    return ": " in valor or " #" in valor


def ancoras(md: Path) -> set[str]:
    """Âncoras dos títulos como o GitHub gera: minúsculas, sem pontuação (letras acentuadas ficam),
    espaço vira hífen; título repetido ganha -1, -2..."""
    vistas, saida = {}, set()
    for linha in CERCA.sub("", md.read_text(encoding="utf-8")).splitlines():
        m = re.match(r"#{1,6}\s+(.*?)\s*#*\s*$", linha)
        if not m:
            continue
        slug = re.sub(r"[^\w\- ]", "", m.group(1).lower()).replace(" ", "-")
        n = vistas.get(slug, 0)
        vistas[slug] = n + 1
        saida.add(slug if n == 0 else f"{slug}-{n}")
    return saida


def checar_links(raiz: Path, erros: list, stats: dict):
    for p, r in arquivos(raiz):
        # prova/, privado/ e fontes/ ficam fora da cópia fria e da versão pública (fontes/skill-oficial é de terceiro).
        if p.suffix != ".md" or r.startswith(("prova/", "privado/", "fontes/")):
            continue
        texto = sem_codigo(p.read_text(encoding="utf-8"))
        for w in WIKI.findall(texto):
            erros.append(f"wikilink proibido: {r} -> {w}")
        for alvo in LINK.findall(texto):
            alvo = alvo.strip().split()[0].strip("<>")
            if "://" in alvo or alvo.startswith(("#", "mailto:")):
                continue
            caminho = unquote(alvo.split("#", 1)[0])
            if not caminho:
                continue
            stats["links"] += 1
            destino = (p.parent / caminho).resolve()
            if not destino.exists():
                erros.append(f"link quebrado: {r} -> {alvo}")
                continue
            try:
                d = destino.relative_to(raiz.resolve()).as_posix()
            except ValueError:
                erros.append(f"link para fora do repositório: {r} -> {alvo}")
                continue
            if d.startswith(FORA_DA_COPIA_FRIA) or d in FORA_DA_COPIA_FRIA_ARQUIVOS:
                erros.append(f"link para o que fica fora da cópia fria: {r} -> {alvo}")
            elif "#" in alvo and destino.suffix == ".md":
                ancora = unquote(alvo.split("#", 1)[1]).lower()
                if ancora not in ancoras(destino):
                    erros.append(f"âncora inexistente: {r} -> {alvo}")


def checar_notas(raiz: Path, erros: list, avisos: list, stats: dict):
    base = raiz / "conhecimento"
    indice = base / "INDICE.md"
    if not indice.exists():
        erros.append("falta conhecimento/INDICE.md")
        return
    no_indice = set()
    for alvo in LINK.findall(sem_codigo(indice.read_text(encoding="utf-8"))):
        caminho = unquote(alvo.strip().split()[0].split("#", 1)[0])
        if caminho and "://" not in caminho:
            no_indice.add((indice.parent / caminho).resolve())
    for p in sorted(base.rglob("*.md")):
        if p == indice:
            continue
        r = rel(p, raiz)
        stats["notas"] += 1
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if fm is None:
            erros.append(f"nota sem frontmatter: {r}")
        else:
            for campo in CAMPOS_NOTA:
                if not fm.get(campo):
                    erros.append(f"frontmatter sem '{campo}': {r}")
            if fm.get("name") and fm["name"] != p.stem:
                erros.append(f"name '{fm['name']}' ≠ arquivo '{p.stem}': {r}")
            if fm.get("tipo") and fm["tipo"] not in TIPOS_NOTA:
                erros.append(f"tipo inválido '{fm['tipo']}': {r}")
            if fm.get("estudado_em") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fm["estudado_em"]):
                erros.append(f"estudado_em fora de AAAA-MM-DD: {r}")
            for k, v in fm.items():
                if yaml_inseguro(v):
                    erros.append(f"frontmatter com valor que YAML estrito leria diferente ({k}): {r}")
        if p.resolve() not in no_indice:
            erros.append(f"nota fora do INDICE: {r}")


def checar_skills(raiz: Path, erros: list, stats: dict):
    base = raiz / "skills"
    for pasta in sorted(d for d in base.iterdir() if d.is_dir()):
        skill = pasta / "SKILL.md"
        r = rel(skill, raiz)
        if not skill.exists():
            erros.append(f"skill sem SKILL.md: {rel(pasta, raiz)}")
            continue
        stats["skills"] += 1
        texto = skill.read_text(encoding="utf-8")
        fm = frontmatter(texto)
        if fm is None:
            erros.append(f"SKILL.md sem frontmatter: {r}")
            continue
        nome, desc = fm.get("name", ""), fm.get("description", "")
        if nome != pasta.name:
            erros.append(f"skill name '{nome}' ≠ pasta '{pasta.name}'")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nome) or len(nome) > 64:
            erros.append(f"skill name fora do padrão hífen-minúsculo: {r}")
        if not desc or len(desc) > 1024 or "<" in desc or ">" in desc:
            erros.append(f"skill description vazia, > 1024 caracteres ou com < >: {r}")
        for k, v in fm.items():
            if yaml_inseguro(v):
                erros.append(f"frontmatter de skill que YAML estrito recusaria ({k}): {r}")
        n = len(texto.splitlines())
        if n > MAX_LINHAS_SKILL:
            erros.append(f"SKILL.md com {n} linhas (> {MAX_LINHAS_SKILL}): {r}")


def checar_json(raiz: Path, erros: list, stats: dict):
    for p, r in arquivos(raiz):
        if p.suffix != ".json":
            continue
        stats["json"] += 1
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError) as e:
            erros.append(f"JSON inválido: {r} ({e.__class__.__name__})")


def checar_assets(raiz: Path, erros: list):
    """Coerência do par requisição/resposta mock e da semente (portado do validador do Codex)."""
    a = raiz / "skills/jev-integrar/assets"
    try:
        req = json.loads((a / "support-triage.request.json").read_text(encoding="utf-8"))
        resp = json.loads((a / "support-triage.response.mock.json").read_text(encoding="utf-8"))
        assert set(req) == {"model", "state", "questions"}
        assert set(req["questions"]) == set(resp["answers"])
        for chave, q in req["questions"].items():
            ans, tipo = resp["answers"][chave], q["type"]
            assert ans["type"] == tipo and q.get("instructions")
            if tipo == "noul":
                v = ans["noul"]
                assert isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and 0 <= v <= 1
                assert "confidence" not in ans
                continue
            probs = ans["probabilities"]
            assert all(math.isfinite(v) and 0 <= v <= 1 for v in probs.values())
            assert math.isclose(sum(probs.values()), 1) and 0 <= ans["confidence"] <= 1
            if tipo == "choice":
                assert 1 < len(q["criteria"]) <= 255 and set(probs) == set(q["criteria"])
                assert ans["choice"] in probs and probs[ans["choice"]] == max(probs.values())
            else:
                assert 2 <= len(q["criteria"]) <= 10
                esperado = {str(i): nivel for i, nivel in enumerate(q["criteria"])}
                assert ans["legend"] == esperado and set(probs) == set(esperado)
                assert math.isclose(ans["score"], sum(int(i) * p for i, p in probs.items()))
    except (AssertionError, KeyError, OSError, ValueError) as e:
        erros.append(f"par requisição/resposta mock incoerente ({e.__class__.__name__})")
    try:
        seed = json.loads((raiz / "skills/jev-avaliar/assets/seed-cases.json").read_text(encoding="utf-8"))
        assert seed["status"] == "synthetic_not_executed"
        assert len({c["id"] for c in seed["cases"]}) == len(seed["cases"])
        assert all(c["gold"] is None or isinstance(c["gold"], bool) for c in seed["cases"])
    except (AssertionError, KeyError, OSError, ValueError) as e:
        erros.append(f"semente de avaliação incoerente ({e.__class__.__name__})")


def valores_de_chave(raiz: Path, arquivo_chave: Path | None):
    valores = []
    for origem in filter(None, [arquivo_chave, raiz / "api_key.txt"]):
        if origem.exists():
            v = origem.read_text(encoding="utf-8", errors="ignore").strip()
            if len(v) >= 12:
                valores.append(v)
    v = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if len(v) >= 12:
        valores.append(v)
    return list(dict.fromkeys(valores))


def checar_segredos(raiz: Path, erros: list, avisos: list, stats: dict, arquivo_chave: Path | None):
    chaves = valores_de_chave(raiz, arquivo_chave)
    stats["chave_local_conhecida"] = bool(chaves)
    for p, r in arquivos(raiz):
        # .env e .env.* não têm extensão de texto, mas são o lugar mais provável de um segredo.
        if (p.suffix.lower() not in EXT_TEXTO and not p.name.lower().startswith(".env")) or r == "api_key.txt":
            continue
        try:
            texto = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        stats["varridos"] += 1
        destino = avisos if r in ARQUIVOS_SENSIVEIS else erros
        for n, linha in enumerate(texto.splitlines(), 1):
            for c in chaves:
                if c in linha:
                    destino.append(f"VALOR DA CHAVE encontrado: {r}:{n}")
            for nome, rx in PADROES_SEGREDO:
                if rx.search(linha):
                    destino.append(f"possível segredo ({nome}): {r}:{n}")


def checar_catalogo(raiz: Path, erros: list, stats: dict):
    cat = raiz / "fontes/catalogo/catalogo.json"
    if not (raiz / "fontes").exists():
        stats["catalogo"] = "ausente: cópia fria sem fontes/"
        return
    if not cat.exists():
        erros.append("falta fontes/catalogo/catalogo.json")
        return
    d = json.loads(cat.read_text(encoding="utf-8"))
    pares = []
    for doc in d["estudo_codex"]["documentation"]:
        pares.append((doc["cache"], doc["sha256"]))
    for v in d["estudo_codex"]["videos"]:
        pares.append((v["caption_cache"], v["caption_sha256"]))
        if not (raiz / v["note"]).exists():
            erros.append(f"catálogo aponta nota inexistente: {v['note']}")
    for doc in d["revisao_dirigida_codex"]["documentation"]:
        pares.append((doc["snapshot"], doc["sha256"]))
    for m in d["handoff_claude"]:
        pares.append((m["copia_atual"], m["sha256"]))
    for caminho, esperado in pares:
        p = raiz / caminho
        if not p.exists():
            stats["hash_sem_arquivo_local"] += 1
            continue
        stats["hash_conferido"] += 1
        if hashlib.sha256(p.read_bytes()).hexdigest().lower() != esperado.lower():
            erros.append(f"hash diferente do catálogo: {caminho}")


def checar_raiz(raiz: Path, erros: list):
    gi = raiz / ".gitignore"
    linhas = set(gi.read_text(encoding="utf-8").split()) if gi.exists() else set()
    for regra in ("fontes/docs/", "fontes/videos/", ".local/", "api_key.txt"):
        if regra not in linhas:
            erros.append(f".gitignore não contém {regra}")
    claude = raiz / "CLAUDE.md"
    if not claude.exists() or not claude.read_text(encoding="utf-8").startswith("@AGENTS.md"):
        erros.append("CLAUDE.md não começa com @AGENTS.md")


def validar(raiz: Path, arquivo_chave: Path | None = None):
    erros, avisos = [], []
    stats = {"links": 0, "notas": 0, "skills": 0, "json": 0, "varridos": 0,
             "hash_conferido": 0, "hash_sem_arquivo_local": 0}
    checar_links(raiz, erros, stats)
    checar_notas(raiz, erros, avisos, stats)
    checar_skills(raiz, erros, stats)
    checar_json(raiz, erros, stats)
    checar_assets(raiz, erros)
    checar_segredos(raiz, erros, avisos, stats, arquivo_chave)
    checar_catalogo(raiz, erros, stats)
    checar_raiz(raiz, erros)
    return erros, avisos, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--chave", type=Path, default=None,
                    help="arquivo com a chave cujo VALOR não pode aparecer (padrão: api_key.txt da raiz)")
    args = ap.parse_args()
    erros, avisos, stats = validar(args.raiz.resolve(), args.chave)
    for a in avisos:
        print("AVISO", a)
    for e in erros:
        print("ERRO ", e)
    print(json.dumps({"resultado": "passou" if not erros else "falhou", "erros": len(erros),
                      "avisos": len(avisos), **stats}, ensure_ascii=False))
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
