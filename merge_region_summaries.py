#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge region summary CSVs into Excel workbooks.

Creates two workbook sets:
1) Regions 82-90
   - results/csv/merged_main_summary_82-90.xlsx
   - results/csv/merged_levels_summary_82-90.xlsx
2) Regions 810-819
   - results/csv/merged_main_summary_810-819.xlsx
   - results/csv/merged_levels_summary_810-819.xlsx

Each workbook contains one sheet per region folder.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable

import pandas as pd


BASE_DIR = Path("results") / "csv"
REGION_SETS: list[tuple[str, list[int]]] = [
    ("82-90", list(range(82, 91))),
    ("810-819", list(range(810, 820))),
]

LEFT_BRACKET = chr(0x3010)   # 【
RIGHT_BRACKET = chr(0x3011)  # 】


def _region_prefix(region_code: int) -> str:
    return f"{LEFT_BRACKET}{region_code}{RIGHT_BRACKET}"


def _find_region_dir(region_code: int) -> Path | None:
    if not BASE_DIR.exists():
        return None
    prefix = _region_prefix(region_code)
    matches = sorted(
        (
            path
            for path in BASE_DIR.iterdir()
            if path.is_dir() and path.name.startswith(prefix)
        ),
        key=lambda p: p.name,
    )
    return matches[0] if matches else None


def _find_first(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern), key=lambda p: p.name)
    return matches[0] if matches else None


def _sheet_name(folder_name: str) -> str:
    # Remove characters Excel forbids in sheet names: : \ / ? * [ ]
    cleaned = re.sub(r"[:\\/\?\*\[\]]", "_", folder_name.strip())
    return (cleaned or "Sheet1")[:31]


def _collect_frames(region_codes: Iterable[int], kind: str) -> list[tuple[str, pd.DataFrame]]:
    """
    kind: 'all' for *_all_texts_summary.csv, 'levels' for *_levels_summary.csv.
    """
    suffix = "_all_texts_summary.csv" if kind == "all" else "_levels_summary.csv"
    pattern = f"*{suffix}"
    frames: list[tuple[str, pd.DataFrame]] = []

    for region_code in region_codes:
        region_dir = _find_region_dir(region_code)
        if not region_dir:
            print(f"SKIP region {region_code}: folder not found")
            continue

        csv_path = _find_first(region_dir, pattern)
        if not csv_path:
            print(f"SKIP region {region_code}: {kind} summary not found in {region_dir.name}")
            continue

        try:
            frame = pd.read_csv(csv_path, encoding="utf-8-sig")
        except Exception as exc:
            print(f"SKIP region {region_code}: failed to read {csv_path} ({exc})")
            continue

        frames.append((_sheet_name(region_dir.name), frame))

    return frames


def _write_workbook(output_path: Path, frames: list[tuple[str, pd.DataFrame]]) -> None:
    if not frames:
        print(f"No data to write for {output_path.name}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet, frame in frames:
            frame.to_excel(writer, sheet_name=sheet, index=False)
    print(f"Wrote {output_path}")


def main() -> None:
    for label, region_codes in REGION_SETS:
        main_frames = _collect_frames(region_codes, "all")
        levels_frames = _collect_frames(region_codes, "levels")

        out_main = BASE_DIR / f"merged_main_summary_{label}.xlsx"
        out_levels = BASE_DIR / f"merged_levels_summary_{label}.xlsx"

        _write_workbook(out_main, main_frames)
        _write_workbook(out_levels, levels_frames)


if __name__ == "__main__":
    main()
