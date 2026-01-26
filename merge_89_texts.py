#!/usr/bin/env python3
"""
Combine paired cleaned texts for region 89 (九州) into one file per project.

Default behavior:
  - Input:  results/test3/【89】九州/<project>/*.txt
  - Output: results/test3_merged/【89】九州/<project>/<project>.txt

Ordering:
  - Prefer files whose name includes "入札説明書" or "説明書"
  - Then fall back to alphabetical order
  - Finally, reverse the order (so the former second file becomes first)

You can override input/output roots with CLI flags.
"""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_INPUT_DIR = Path("results") / "test3" / "【89】九州"
DEFAULT_OUTPUT_DIR = Path("results") / "test4" / "【89】九州"
PREFERRED_TOKENS = ("入札説明書", "説明書")
END_OF_DOC_MARKER = "=== END OF DOCUMENT ==="


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge paired 89-region cleaned texts.")
    parser.add_argument(
        "--input_dir",
        default=str(DEFAULT_INPUT_DIR),
        help="Directory with per-project folders of cleaned .txt files.",
    )
    parser.add_argument(
        "--output_dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to write combined .txt files.",
    )
    return parser.parse_args()


def order_files(paths: list[Path]) -> list[Path]:
    def sort_key(p: Path) -> tuple[int, str]:
        name = p.name
        preferred = any(token in name for token in PREFERRED_TOKENS)
        return (0 if preferred else 1, name.lower())

    return sorted(paths, key=sort_key)


def _start_marker(index: int, name: str) -> str:
    if index == 0:
        label = "FIRST"
    elif index == 1:
        label = "SECOND"
    else:
        label = f"FILE {index + 1}"
    return f"=== {label} FILE START: {name} ==="


def combine_texts(texts: list[str], names: list[str]) -> str:
    if not texts:
        return ""
    parts: list[str] = []
    for idx, (text, name) in enumerate(zip(texts, names)):
        parts.append(_start_marker(idx, name))
        parts.append(text.rstrip("\n"))
        if idx == 1:
            parts.append(END_OF_DOC_MARKER)
    return "\n\n".join(parts) + "\n"


def process_project_folder(project_dir: Path, output_root: Path) -> bool:
    txt_files = [p for p in project_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"]
    if not txt_files:
        return False

    ordered = list(reversed(order_files(txt_files)))
    combined = combine_texts(
        [p.read_text(encoding="utf-8-sig") for p in ordered],
        [p.name for p in ordered],
    )

    out_dir = output_root / project_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{project_dir.name}.txt"
    out_path.write_text(combined, encoding="utf-8")

    print(f"Combined {len(ordered)} file(s): {project_dir.name} -> {out_path}")
    return True


def main() -> None:
    args = parse_args()
    input_root = Path(args.input_dir)
    output_root = Path(args.output_dir)

    if not input_root.exists():
        raise SystemExit(f"Input directory not found: {input_root}")

    output_root.mkdir(parents=True, exist_ok=True)

    combined_count = 0
    for entry in sorted(input_root.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_dir():
            continue
        if process_project_folder(entry, output_root):
            combined_count += 1

    print(f"Done. Combined {combined_count} project folder(s).")


if __name__ == "__main__":
    main()
