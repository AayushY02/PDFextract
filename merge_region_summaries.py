#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge region summary CSVs into two Excel workbooks:
1) Main summaries (all_texts_summary) – each region in its own sheet.
2) Level summaries (levels_summary) – each region in its own sheet.

Targets regions 82–90. Input CSVs are expected under results/csv/<region_folder>/.
Output workbook paths:
  - results/csv/merged_main_summary_82-90.xlsx
  - results/csv/merged_levels_summary_82-90.xlsx
"""

from pathlib import Path
import re
import pandas as pd


REGIONS = list(range(82, 91))
BASE_DIR = Path("results") / "csv"
OUT_MAIN = BASE_DIR / "merged_main_summary_82-90.xlsx"
OUT_LEVELS = BASE_DIR / "merged_levels_summary_82-90.xlsx"


def _find_first(pattern: str) -> Path | None:
    matches = list(BASE_DIR.glob(pattern))
    return matches[0] if matches else None


def _sheet_name(path: Path) -> str:
    """
    Build a safe sheet name (<=31 chars, avoid Excel banned chars).

    Requirement: sheet name should just be the region code + region name
    (e.g., `?82???`), not the full CSV stem that includes
    `_levels_summary` / `_all_texts_summary`.
    """
    # Prefer the parent directory name, which already matches the desired label.
    base = path.parent.name.strip()

    if not base:
        # Fallback: strip known suffixes from the file stem.
        stem = path.stem
        stem = re.sub(r"(_levels_summary|_all_texts_summary)$", "", stem)
        base = stem

    # Remove characters Excel forbids in sheet names: : \ / ? * [ ]
    base = re.sub(r"[:\\/\?\*\[\]]", "_", base)
    return base[:31]



def _collect_frames(kind: str):
    """
    kind: 'all' for main summaries, 'levels' for level summaries.
    Returns list of (sheet_name, DataFrame).
    """
    frames = []
    for region in REGIONS:
        if kind == "all":
            pattern = f"【{region}】*/【{region}】*_all_texts_summary.csv"
        else:
            pattern = f"【{region}】*/【{region}】*_levels_summary.csv"
        path = _find_first(pattern)
        if not path:
            print(f"SKIP region {region}: {kind} summary not found")
            continue
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
        except Exception as exc:
            print(f"SKIP region {region}: failed to read {path} ({exc})")
            continue
        sheet = _sheet_name(path)
        frames.append((sheet, df))
    return frames


def _write_workbook(output_path: Path, frames: list[tuple[str, pd.DataFrame]]):
    if not frames:
        print(f"No data to write for {output_path.name}")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet, df in frames:
            df.to_excel(writer, sheet_name=sheet, index=False)
    print(f"Wrote {output_path}")


def main():
    main_frames = _collect_frames("all")
    level_frames = _collect_frames("levels")
    _write_workbook(OUT_MAIN, main_frames)
    _write_workbook(OUT_LEVELS, level_frames)


if __name__ == "__main__":
    main()
