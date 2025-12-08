"""
Post-clean pass for results/output2 -> results/output4.

Goals:
 - Strip stray page-number lines that survived earlier cleaning.
 - Merge cross-page tables more robustly (ignoring page numbers/blank lead-ins and tolerating slight column mismatches).
 - Keep folder structure identical to output2.

This script does not modify the original output2 files.
"""

from pathlib import Path
import shutil

INPUT_DIR = Path("results/output2")
OUTPUT_DIR = Path("results/output4")

TABLE_START = "[[TABLE_START "
TABLE_END = "[[TABLE_END]]"


# ---------- small helpers ----------
def is_digit_line(line: str) -> bool:
    s = line.strip()
    return s.isdigit() and 0 < len(s) <= 3


def _apply_preserving_tables(text: str, transform) -> str:
    """
    Apply a transform only outside table blocks.
    """
    if TABLE_START not in text:
        return transform(text)

    out = []
    i = 0
    n = len(text)
    start = text.find(TABLE_START, i)
    while start != -1:
        before = text[i:start]
        out.append(transform(before))

        end = text.find(TABLE_END, start)
        if end == -1:
            out.append(text[start:])
            return "".join(out)

        end += len(TABLE_END)
        # include trailing newlines after table marker
        while end < n and text[end] in "\r\n":
            end += 1
        out.append(text[start:end])
        i = end
        start = text.find(TABLE_START, i)

    out.append(transform(text[i:]))
    return "".join(out)


# ---------- page-number stripping ----------
def remove_stray_page_numbers(text: str) -> str:
    """
    Drop digit-only lines (e.g., '15') that sit between page markers and content.
    """

    def transform(chunk: str) -> str:
        ends_with_nl = chunk.endswith("\n")
        lines = chunk.splitlines()
        out = []
        for idx, line in enumerate(lines):
            if is_digit_line(line):
                # Look at nearby context to decide if this is a stray page number.
                prev = ""
                for k in range(idx - 1, -1, -1):
                    if lines[k].strip():
                        prev = lines[k].strip()
                        break
                nxt = ""
                for k in range(idx + 1, len(lines)):
                    if lines[k].strip():
                        nxt = lines[k].strip()
                        break
                if (
                    prev.startswith("[[PAGE_START ")
                    or nxt.startswith("[[PAGE_END")
                    or nxt.startswith(TABLE_START)
                ):
                    continue
            out.append(line)
        result = "\n".join(out)
        if ends_with_nl:
            result += "\n"
        return result

    return _apply_preserving_tables(text, transform)


# ---------- marker normalization ----------
def normalize_markers(text: str) -> str:
    """
    Ensure PAGE/TABLE markers live on their own lines, even if the extractor
    emitted them inline with preceding text.
    """
    markers = ("[[PAGE_START ", "[[PAGE_END", "[[TABLE_START ", "[[TABLE_END]]")
    ends_with_nl = text.endswith("\n")
    lines = text.split("\n")  # preserves empty lines
    out: list[str] = []
    for line in lines:
        remainder = line
        placed_any = False
        while True:
            idxs = [remainder.find(m) for m in markers if m in remainder]
            idxs = [i for i in idxs if i != -1]
            if not idxs:
                if remainder != "" or not placed_any:
                    out.append(remainder)
                break
            idx = min(idxs)
            if idx > 0:
                prefix = remainder[:idx]
                out.append(prefix)
                placed_any = True
            # find which marker and its length
            m = None
            for cand in markers:
                if remainder.startswith(cand, idx):
                    m = cand
                    break
            if m is None:
                out.append(remainder[idx:])
                placed_any = True
                break
            if m == "[[TABLE_END]]":
                marker_len = len("[[TABLE_END]]")
            elif m.startswith("[[PAGE_END"):
                marker_len = len("[[PAGE_END]]")
            elif m.startswith("[[PAGE_START "):
                marker_len = remainder[idx:].find("]]") + 2  # up to closing ]]
            else:  # TABLE_START
                marker_len = remainder[idx:].find("]]") + 2
            out.append(remainder[idx : idx + marker_len])
            placed_any = True
            remainder = remainder[idx + marker_len :]
            if remainder == "":
                # preserve trailing empties on the same original line
                out.append("")
                break
    result = "\n".join(out)
    if ends_with_nl:
        result += "\n"
    return result


# ---------- table parsing/merging ----------
def parse_table_header(line: str) -> dict:
    meta = {}
    if not line.startswith(TABLE_START):
        return meta
    inner = line[len(TABLE_START) :].rstrip("]]").strip()
    for token in inner.split():
        if "=" in token:
            k, v = token.split("=", 1)
            try:
                meta[k] = int(v)
            except ValueError:
                meta[k] = v
    return meta


def build_table_header(meta: dict) -> str:
    keys = ["page", "index", "rows", "cols"]
    parts = []
    for k in keys:
        if k in meta:
            parts.append(f"{k}={meta[k]}")
    # include any extra keys in stable order
    for k in sorted(meta.keys()):
        if k not in keys:
            parts.append(f"{k}={meta[k]}")
    return f"[[TABLE_START {' '.join(parts)}]]"


def estimate_cols(table_lines: list[str]) -> int | None:
    for row in table_lines[1:-1]:
        s = row.strip()
        if not s:
            continue
        parts = [p.strip() for p in s.strip("|").split("|")]
        if len(parts) > 1:
            return len(parts)
    return None


def body_row_count(table_lines: list[str]) -> int:
    # exclude header and footer
    return max(len(table_lines) - 2, 0)


def cols_compatible(a: int | None, b: int | None) -> bool:
    if a is None or b is None:
        return True
    if a == b:
        return True
    if abs(a - b) <= 2:
        return True
    # allow small relative drift
    small = min(a, b)
    return small > 0 and abs(a - b) / small <= 0.25


def build_segments(lines: list[str]) -> list[dict]:
    segments = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.startswith(TABLE_START):
            table_lines = [line]
            i += 1
            while i < n:
                table_lines.append(lines[i])
                if lines[i].startswith(TABLE_END):
                    i += 1
                    break
                i += 1
            segments.append({"type": "table", "lines": table_lines})
        else:
            block = [line]
            i += 1
            while i < n and not lines[i].startswith(TABLE_START):
                block.append(lines[i])
                i += 1
            segments.append({"type": "text", "lines": block})
    return segments


def is_ignorable_text(seg: dict) -> bool:
    if seg["type"] != "text":
        return False
    lines = seg["lines"]
    if not lines:
        return True
    # all lines are blank or digit-only and short
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if is_digit_line(ln):
            continue
        # treat very short fragments (likely table leak) as ignorable
        if len(s) <= 30 and (" " not in s or "　" not in s):
            continue
        return False
    return True


def flatten_segments(segments: list[dict]) -> list[str]:
    out: list[str] = []
    for seg in segments:
        out.extend(seg["lines"])
    return out


def find_last_table_idx(segments: list[dict]) -> int | None:
    idx = len(segments) - 1
    while idx >= 0 and is_ignorable_text(segments[idx]):
        idx -= 1
    if idx >= 0 and segments[idx]["type"] == "table":
        return idx
    return None


def find_first_table_idx(segments: list[dict]) -> int | None:
    idx = 0
    while idx < len(segments) and is_ignorable_text(segments[idx]):
        idx += 1
    if idx < len(segments) and segments[idx]["type"] == "table":
        return idx
    return None


def absorb_trailing_text_into_table(lines: list[str]) -> list[str]:
    """
    If short text immediately follows a table, treat it as extra rows of that table
    and bump the rows count accordingly. This helps when the extractor dropped
    a row outside the table bbox. Collects a block of consecutive short lines
    (plus blanks) until a marker or a long line is hit.
    """
    i = 0
    n = len(lines)
    out: list[str] = []
    while i < n:
        line = lines[i]
        if line.startswith(TABLE_START):
            table_lines = [line]
            i += 1
            while i < n:
                table_lines.append(lines[i])
                if lines[i].startswith(TABLE_END):
                    i += 1
                    break
                i += 1

            # collect a block of short trailing lines (and blanks)
            trailing: list[str] = []
            j = i
            while j < n:
                s = lines[j].strip()
                if not s:
                    trailing.append(lines[j])
                    j += 1
                    continue
                if lines[j].startswith("[["):
                    break
                # tweak threshold if needed; 80 chars to allow multi-word cells
                if len(s) <= 80:
                    trailing.append(lines[j])
                    j += 1
                    continue
                break

            if trailing:
                meta = parse_table_header(table_lines[0])
                cols = meta.get("cols") or estimate_cols(table_lines) or 1
                rows_added = 0
                for tline in trailing:
                    if not tline.strip():
                        continue
                    cells = [tline.strip()] + [""] * max(cols - 1, 0)
                    row = "| " + " | ".join(cells) + " |"
                    table_lines.insert(-1, row)
                    rows_added += 1
                if rows_added and "rows" in meta and isinstance(meta["rows"], int):
                    meta["rows"] = meta["rows"] + rows_added
                    table_lines[0] = build_table_header(meta)
                # skip consumed trailing lines
                i = j

            out.extend(table_lines)
        else:
            out.append(line)
            i += 1
    return out


def merge_pages(page_a: dict, page_b: dict) -> bool:
    # Pre-absorb leaked short lines into preceding tables
    body_a = absorb_trailing_text_into_table(page_a["body"])
    body_b = absorb_trailing_text_into_table(page_b["body"])

    segments_a = build_segments(body_a)
    segments_b = build_segments(body_b)

    last_a = find_last_table_idx(segments_a)
    first_b = find_first_table_idx(segments_b)
    if last_a is None or first_b is None:
        return False

    table_a = segments_a[last_a]["lines"]
    table_b = segments_b[first_b]["lines"]
    meta_a = parse_table_header(table_a[0])
    meta_b = parse_table_header(table_b[0])

    cols_a = meta_a.get("cols")
    cols_b = meta_b.get("cols")
    if cols_a is None:
        cols_a = estimate_cols(table_a)
    if cols_b is None:
        cols_b = estimate_cols(table_b)
    if not cols_compatible(cols_a, cols_b):
        return False

    rows_a = meta_a.get("rows")
    rows_b = meta_b.get("rows")
    if not isinstance(rows_a, int):
        rows_a = body_row_count(table_a)
    if not isinstance(rows_b, int):
        rows_b = body_row_count(table_b)

    new_rows = rows_a + rows_b
    meta_a["rows"] = new_rows
    if cols_a is not None:
        meta_a["cols"] = cols_a

    merged_table = table_a[:-1] + table_b[1:-1] + [table_a[-1]]
    merged_table[0] = build_table_header(meta_a)
    segments_a[last_a]["lines"] = merged_table

    segments_b.pop(first_b)

    page_a["body"] = flatten_segments(segments_a)
    page_b["body"] = flatten_segments(segments_b)
    return True


def merge_cross_page_tables(text: str) -> str:
    lines = text.splitlines()
    ends_with_nl = text.endswith("\n")

    pages = []
    prelude = []
    postlude = []
    current = None

    for line in lines:
        if line.startswith("[[PAGE_START "):
            current = {"start": line, "body": [], "end": None}
            pages.append(current)
            continue
        if line.startswith("[[PAGE_END"):
            if current is not None:
                current["end"] = line
                current = None
            else:
                postlude.append(line)
            continue
        if current is None:
            if pages:
                postlude.append(line)
            else:
                prelude.append(line)
        else:
            current["body"].append(line)

    # First pass: absorb leaked trailing lines within each page body
    for page in pages:
        page["body"] = absorb_trailing_text_into_table(page["body"])

    # Merge backwards so chains roll up to the starting page
    for idx in range(len(pages) - 2, -1, -1):
        while merge_pages(pages[idx], pages[idx + 1]):
            continue

    out_lines: list[str] = []
    out_lines.extend(prelude)
    for page in pages:
        if page["start"]:
            out_lines.append(page["start"])
        out_lines.extend(page["body"])
        if page["end"]:
            out_lines.append(page["end"])
    out_lines.extend(postlude)

    result = "\n".join(out_lines)
    if ends_with_nl:
        result += "\n"
    return result


# ---------- pipeline ----------
def process_text(text: str) -> str:
    text = normalize_markers(text)
    text = remove_stray_page_numbers(text)
    text = merge_cross_page_tables(text)
    return text


def process_all():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for txt_path in INPUT_DIR.rglob("*.txt"):
        rel = txt_path.relative_to(INPUT_DIR)
        out_path = OUTPUT_DIR / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        content = txt_path.read_text(encoding="utf-8")
        cleaned = process_text(content)
        out_path.write_text(cleaned, encoding="utf-8")
        print(f"Processed {rel}")


if __name__ == "__main__":
    process_all()
