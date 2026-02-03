#!/usr/bin/env python3
"""
Merge 86 Osaka extracted texts into a single file per project.

Default behavior:
  - Input:  results/test/【86】大阪/<project>/*.txt
  - Output: results/test_merged/【86】大阪/<project>/<project>.txt

Order:
  1) 【個別_入札説明書】
  2) 【個別_入札説明書_別紙-4】
  3) 【個別_入札説明書_別紙-5】
"""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_INPUT_DIR = Path("results") / "test3" / "【86】大阪"
DEFAULT_OUTPUT_DIR = Path("results") / "test4" / "【86】大阪"
TOKEN_ORDER = [
    ("【個別_入札説明書】", "MAIN"),
    ("【個別_入札説明書_別紙-4】", "ANNEX-4"),
    ("【個別_入札説明書_別紙-5】", "ANNEX-5"),
]
END_OF_DOC_MARKER = "=== END OF DOCUMENT ==="


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge 86 Osaka extracted texts.")
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


def _start_marker(index: int, name: str) -> str:
    if index == 0:
        label = "FIRST"
    elif index == 1:
        label = "SECOND"
    elif index == 2:
        label = "THIRD"
    else:
        label = f"FILE {index + 1}"
    return f"=== {label} FILE START: {name} ==="


def order_files(paths: list[Path]) -> tuple[list[Path], list[str]]:
    ordered: list[Path] = []
    warnings: list[str] = []

    token_matches: dict[str, list[Path]] = {token: [] for token, _ in TOKEN_ORDER}
    unmatched: list[Path] = []

    for path in paths:
        matched = False
        for token, _ in TOKEN_ORDER:
            if token in path.name:
                token_matches[token].append(path)
                matched = True
        if not matched:
            unmatched.append(path)

    for token, label in TOKEN_ORDER:
        matches = sorted(token_matches[token], key=lambda p: p.name.lower())
        if not matches:
            warnings.append(f"Missing {label} file ({token}).")
            continue
        ordered.append(matches[0])
        if len(matches) > 1:
            extras = ", ".join(p.name for p in matches[1:])
            warnings.append(f"Multiple matches for {label} ({token}); ignored: {extras}")

    if unmatched:
        extras = ", ".join(p.name for p in sorted(unmatched, key=lambda p: p.name.lower()))
        warnings.append(f"Unmatched .txt files ignored: {extras}")

    return ordered, warnings


def combine_texts(paths: list[Path]) -> str:
    if not paths:
        return ""
    parts: list[str] = []
    for idx, path in enumerate(paths):
        parts.append(_start_marker(idx, path.name))
        parts.append(path.read_text(encoding="utf-8-sig").rstrip("\n"))
    parts.append(END_OF_DOC_MARKER)
    return "\n\n".join(parts) + "\n"


def process_project_folder(project_dir: Path, output_root: Path) -> bool:
    txt_files = [p for p in project_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"]
    if not txt_files:
        return False

    ordered, warnings = order_files(txt_files)
    if not ordered:
        print(f"Skipped (no matching files): {project_dir.name}")
        return False

    combined = combine_texts(ordered)

    out_dir = output_root / project_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{project_dir.name}.txt"
    out_path.write_text(combined, encoding="utf-8")

    print(f"Combined {len(ordered)} file(s): {project_dir.name} -> {out_path}")
    for warning in warnings:
        print(f"  Warning: {warning}")
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
