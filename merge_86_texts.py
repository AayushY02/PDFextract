#!/usr/bin/env python3
"""
Merge 86 Osaka extracted texts into a single file per project.

Default behavior:
  - Input:  results/test3/【86】大阪/**/<project>/*.txt
  - Output: results/test4/【86】大阪/**/<project>/<project>.txt

Order:
  - If regular tokens are found in file names, use this order:
      1) 【個別_入札説明書】
      2) 【個別_入札説明書_別紙-4】
      3) 【個別_入札説明書_別紙-5】
  - Otherwise (honkan-style files), use this order:
      1) files containing "kobetsusetsumeisho/setsumeisyo"
      2) everything else (sorted by file name)
      3) file containing "別紙_besshi-5" (last)
"""

from __future__ import annotations

import argparse
from pathlib import Path
import os
import re


DEFAULT_INPUT_DIR = Path("results") / "test3" / "【86】大阪"
DEFAULT_OUTPUT_DIR = Path("results") / "test4" / "【86】大阪"
TOKEN_ORDER = [
    ("【個別_入札説明書】", "MAIN"),
    ("【個別_入札説明書_別紙-4】", "ANNEX-4"),
    ("【個別_入札説明書_別紙-5】", "ANNEX-5"),
]
END_OF_DOC_MARKER = "=== END OF DOCUMENT ==="
KOBETSU_RE = re.compile(r"kobetsusetsumei(?:sho|syo)", re.IGNORECASE)
KYOUTSUU_RE = re.compile(r"kyoutsu(?:u)?(?:setsumei(?:sho|syo))?", re.IGNORECASE)
KYOUTSUU_JA_RE = re.compile(r"共通\s*説明書|共通_?入札説明書|共通説明")
BESSHI5_RE = re.compile(r"besshi[-_‐ー－–−]?\s*[5５]", re.IGNORECASE)
BESSHI5_JA_RE = re.compile(r"別紙\s*[-_‐ー－–−]?\s*[5５]")


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


def _has_regular_tokens(paths: list[Path]) -> bool:
    for path in paths:
        for token, _ in TOKEN_ORDER:
            if token in path.name:
                return True
    return False


def _order_files_regular(paths: list[Path]) -> tuple[list[Path], list[str]]:
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


def _order_files_honkan(paths: list[Path]) -> tuple[list[Path], list[str]]:
    ordered: list[Path] = []
    warnings: list[str] = []

    kyoutsuu_matches = [
        p for p in paths
        if KYOUTSUU_RE.search(p.name) or KYOUTSUU_JA_RE.search(p.name)
    ]
    kobetsu_matches = [p for p in paths if KOBETSU_RE.search(p.name)]
    besshi5_matches = [
        p for p in paths
        if BESSHI5_RE.search(p.name) or BESSHI5_JA_RE.search(p.name)
    ]

    kyoutsuu_matches = sorted(kyoutsuu_matches, key=lambda p: p.name.lower())
    kobetsu_matches = sorted(kobetsu_matches, key=lambda p: p.name.lower())
    besshi5_matches = sorted(besshi5_matches, key=lambda p: p.name.lower())

    used = set(kyoutsuu_matches + kobetsu_matches + besshi5_matches)
    middle_all = sorted([p for p in paths if p not in used], key=lambda p: p.name.lower())

    if kyoutsuu_matches:
        ordered.append(kyoutsuu_matches[0])
        if len(kyoutsuu_matches) > 1:
            extras = ", ".join(p.name for p in kyoutsuu_matches[1:])
            warnings.append(f"Multiple kyoutsuu files; ignored: {extras}")

        if kobetsu_matches:
            ordered.append(kobetsu_matches[0])
            if len(kobetsu_matches) > 1:
                extras = ", ".join(p.name for p in kobetsu_matches[1:])
                warnings.append(f"Multiple kobetsusetsumeisho files; ignored: {extras}")
        else:
            warnings.append("Missing kobetsusetsumeisho file.")

        # besshi-5 should always be after kobetsu
        if besshi5_matches:
            ordered.append(besshi5_matches[0])
            if len(besshi5_matches) > 1:
                extras = ", ".join(p.name for p in besshi5_matches[1:])
                warnings.append(f"Multiple 別紙_besshi-5 files; ignored: {extras}")
        else:
            warnings.append("Missing 別紙_besshi-5 file.")

        # other files go after besshi-5
        ordered.extend(middle_all)
    else:
        warnings.append("Missing kyoutsuu file.")

        # No kyoutsuu: kobetsu first, besshi-5 second, rest after
        if kobetsu_matches:
            ordered.append(kobetsu_matches[0])
            if len(kobetsu_matches) > 1:
                extras = ", ".join(p.name for p in kobetsu_matches[1:])
                warnings.append(f"Multiple kobetsusetsumeisho files; ignored: {extras}")
        else:
            warnings.append("Missing kobetsusetsumeisho file.")

        if besshi5_matches:
            ordered.append(besshi5_matches[0])
            if len(besshi5_matches) > 1:
                extras = ", ".join(p.name for p in besshi5_matches[1:])
                warnings.append(f"Multiple 別紙_besshi-5 files; ignored: {extras}")
        else:
            warnings.append("Missing 別紙_besshi-5 file.")

        # other files go after besshi-5
        ordered.extend(middle_all)

    return ordered, warnings


def order_files(paths: list[Path]) -> tuple[list[Path], list[str]]:
    if _has_regular_tokens(paths):
        return _order_files_regular(paths)
    return _order_files_honkan(paths)


def combine_texts(paths: list[Path]) -> str:
    if not paths:
        return ""
    parts: list[str] = []
    for idx, path in enumerate(paths):
        parts.append(_start_marker(idx, path.name))
        parts.append(path.read_text(encoding="utf-8-sig").rstrip("\n"))
    parts.append(END_OF_DOC_MARKER)
    return "\n\n".join(parts) + "\n"


def process_project_folder(project_dir: Path, output_root: Path, input_root: Path) -> bool:
    txt_files = [p for p in project_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"]
    if not txt_files:
        return False

    ordered, warnings = order_files(txt_files)
    if not ordered:
        print(f"Skipped (no matching files): {project_dir.name}")
        return False

    combined = combine_texts(ordered)

    rel_dir = project_dir.relative_to(input_root)
    out_dir = output_root / rel_dir
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
    for dirpath, dirnames, filenames in os.walk(input_root):
        dirnames.sort(key=str.lower)
        has_txt = any(f.lower().endswith(".txt") for f in filenames)
        if not has_txt:
            continue
        project_dir = Path(dirpath)
        if process_project_folder(project_dir, output_root, input_root):
            combined_count += 1
            # Do not descend further once a project folder is processed
            dirnames[:] = []

    print(f"Done. Combined {combined_count} project folder(s).")


if __name__ == "__main__":
    main()
