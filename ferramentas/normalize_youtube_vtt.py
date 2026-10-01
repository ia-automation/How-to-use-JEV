"""Converte legendas VTT progressivas do YouTube em texto com timestamps.

Remove somente a sobreposicao entre cues consecutivos. Nao corrige a transcricao.
Para legendas convencionais sem rolagem, use --keep-repeats.
"""

import argparse
import html
import re
from pathlib import Path


def normalize(content, keep_repeats=False):
    previous = []
    rows = []
    # YouTube usa uma linha com espaco como placeholder DENTRO de um cue.
    # Apenas linhas realmente vazias separam cues neste formato.
    for block in re.split(r"\n\n+", content.replace("\r\n", "\n")):
        lines = block.splitlines()
        timing = next((i for i, line in enumerate(lines) if " --> " in line), None)
        if timing is None:
            continue
        start = lines[timing].split(" --> ", 1)[0].strip()
        current = html.unescape(re.sub(r"<[^>]+>", "", " ".join(lines[timing + 1:]))).split()
        overlap = 0
        if not keep_repeats:
            for length in range(min(len(previous), len(current)), 0, -1):
                if previous[-length:] == current[:length]:
                    overlap = length
                    break
        if current[overlap:]:
            rows.append(f"[{start}] {' '.join(current[overlap:])}")
        previous = current
    return "\n".join(rows) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--keep-repeats", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("A saida ja existe; escolha outro nome")
    result = normalize(args.source.read_text(encoding="utf-8-sig"), args.keep_repeats)
    if not result.strip():
        parser.error("Nenhum cue de legenda encontrado")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(result)


if __name__ == "__main__":
    main()
