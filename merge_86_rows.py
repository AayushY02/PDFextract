#!/usr/bin/env python3
"""
Merge 【86】近畿 summary rows that represent the same project but come from
both the main 入札説明書 and its annex 別紙-5.

Rules:
- Normalize file names to strip numbering, 入札説明書 markers, and 別紙-5
  variants so main/annex rows collapse into one group.
- When both main and annex have a value, annex wins except for these columns
  which keep the main (non-別紙) value: has_eval_phrase, has_eval_phrase pageNo,
  name_bu, name_bu pageNo, name_of, name_of pageNo, 「工事名・作業名」,
  「工事名・作業名」 pageNo, file name.
- Blank cells are filled from any row in the same group.
- Output is UTF-8 with BOM and all fields quoted so embedded newlines stay in
  their cells.

Input : results/csv/【86】近畿/【86】近畿_summary.csv
Output: results/csv/【86】近畿/【86】近畿_summary_merged.csv
"""

from pathlib import Path
import csv
import re
import pandas as pd

INPUT_CSV = Path("results/csv/【86】近畿/【86】近畿_summary.csv")
OUTPUT_CSV = Path("results/csv/【86】近畿/【86】近畿_summary_merged.csv")
NAME_COL = "file name"
PREFER_MAIN_COLS = {
    NAME_COL,
    "has_eval_phrase",
    "has_eval_phrase pageNo",
    "name_bu",
    "name_bu pageNo",
    "name_of",
    "name_of pageNo",
    "「工事名・作業名」",
    "「工事名・作業名」 pageNo",
}

ANNEX_RE = re.compile(r"(別紙\s*[-‐ー－–−]?\s*5|別紙\s*５)", re.IGNORECASE)
LEADING_ENUM_RE = re.compile(r"^[\u2460-\u2473\d０-９]+[._-]?\s*")
BRACKET_MARKER_RE = re.compile(
    r"【[^】]*(入札説明書|別紙|個別)[^】]*】"
    r"|\[[^\]]*(入札説明書|別紙|個別)[^\]]*\]"
    r"|（[^）]*(入札説明書|別紙|個別)[^）]*）"
    r"|\([^)]*(入札説明書|別紙|個別)[^)]*\)"
)
TOKEN_REPLACEMENTS = [
    re.compile(r"入札説明書"),
    re.compile(r"個別事項"),
    re.compile(r"個別"),
]


def is_annex(name: str) -> bool:
    return bool(ANNEX_RE.search(str(name)))


def normalize_file_name(value: str) -> str:
    text = str(value)
    base = Path(text).stem
    base = LEADING_ENUM_RE.sub("", base)
    base = BRACKET_MARKER_RE.sub(" ", base)
    base = ANNEX_RE.sub(" ", base)
    for token_re in TOKEN_REPLACEMENTS:
        base = token_re.sub(" ", base)
    base = re.sub(r"[【】\[\]()（）]", " ", base)
    base = base.replace("_", " ")
    base = re.sub(r"\s+", " ", base)
    return base.strip()


def has_value(val) -> bool:
    if val is None:
        return False
    if pd.isna(val):
        return False
    if isinstance(val, str):
        return val.strip() != ""
    return True


def merge_group(group: pd.DataFrame) -> pd.Series:
    group = group.copy()
    group["_is_annex"] = group[NAME_COL].apply(is_annex)
    data_cols = [c for c in group.columns if c not in {"_is_annex", "norm_key"}]

    non_annex = group[~group["_is_annex"]]
    base_idx = non_annex.index[0] if not non_annex.empty else group.index[0]
    base = group.loc[base_idx].copy()

    for idx, row in group.iterrows():
        if idx == base_idx:
            continue
        for col in data_cols:
            bval = base[col]
            rval = row[col]
            if not has_value(bval) and has_value(rval):
                base[col] = rval
            elif has_value(rval) and has_value(bval) and str(bval) != str(rval):
                prefer_annex = col not in PREFER_MAIN_COLS
                base_is_annex = base["_is_annex"]
                row_is_annex = row["_is_annex"]

                if prefer_annex:
                    if row_is_annex and not base_is_annex:
                        base[col] = rval
                else:
                    if not row_is_annex and base_is_annex:
                        base[col] = rval
    return base[data_cols]


def main():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV, dtype=str, encoding="utf-8").fillna("")
    if NAME_COL not in df.columns:
        raise KeyError(f"Column '{NAME_COL}' not found in {INPUT_CSV}")

    df["norm_key"] = df[NAME_COL].apply(normalize_file_name)
    merged_rows = [merge_group(group) for _, group in df.groupby("norm_key", sort=False)]

    out_df = pd.DataFrame(merged_rows)
    out_df = out_df[df.columns.drop("norm_key")].fillna("")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig",  # BOM for Excel-friendly UTF-8
        quoting=csv.QUOTE_ALL,  # keep embedded newlines inside one cell
    )
    print(f"Merged {len(df)} rows into {len(out_df)} rows -> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
