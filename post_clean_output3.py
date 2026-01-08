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
import re


INPUT_DIR = Path("results/output2")
OUTPUT_DIR = Path("results/output3")

TABLE_START = "[[TABLE_START "
TABLE_END = "[[TABLE_END]]"

# def _title_from_nonempty(nonempty: list[str]) -> str:
#     """
#     Merge non-empty cells into one line.
#     Special handling: "3" + ")xxx" -> "3)xxx".
#     """
#     if not nonempty:
#         return ""

#     # special "3" + ")タイトル" pattern
#     if (
#         len(nonempty) >= 2
#         and re.fullmatch(r"[0-9�E�E�E�]+", nonempty[0])
#         and (nonempty[1].startswith(")") or nonempty[1].startswith("�E�E))
#     ):
#         first = nonempty[0] + nonempty[1]  # "3" + ")総合評価" -> "3)総合評価"
#         rest = nonempty[2:]
#         parts = [first] + rest
#         return " ".join(parts)

#     return " ".join(nonempty)

def _title_from_nonempty(nonempty: list[str]) -> str:
    """
    Merge non-empty cells into one line.
    Special handling:
      - "3" + ")xxx"    -> "3)xxx"
      - "II" + ")xxx"   -> "II)xxx"
      - "Ⅲ" + ")xxx"    -> "Ⅲ)xxx"
    """
    if not nonempty:
        return ""

    first = nonempty[0]

    def _is_num_or_roman(token: str) -> bool:
        # ASCII / full-width digits
        if re.fullmatch(r"[0-9０-９]+", token):
            return True
        # ASCII Roman numerals
        if re.fullmatch(r"[ivxlcdmIVXLCDM]+", token):
            return True
        # Full-width Roman numerals (ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ etc.)
        if re.fullmatch(r"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+", token):
            return True
        return False

    # special pattern: "3 | )タイトル" / "II | )タイトル"
    if (
        len(nonempty) >= 2
        and _is_num_or_roman(first)
        and (nonempty[1].startswith(")") or nonempty[1].startswith("）"))
    ):
        merged_first = first + nonempty[1]  # e.g. "3" + ")" -> "3)"
        rest = nonempty[2:]
        parts = [merged_first] + rest
        return " ".join(parts)

    # otherwise just join normally
    return " ".join(nonempty)


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

def merge_boundary_rows(body_a: list[str], body_b: list[str]) -> tuple[list[str], list[str]]:
    """
    Merge a row that was split across a page break.

    We look at:
      - last non-empty row in body_a
      - first non-empty row in body_b

    If the set of non-empty columns in the first row of body_b is a
    subset of the non-empty columns in the last row of body_a, we treat
    it as a continuation of the same cell(s) and concatenate text.
    """
    def last_nonempty_idx(lines: list[str]) -> int | None:
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip():
                return i
        return None

    def first_nonempty_idx(lines: list[str]) -> int | None:
        for i in range(len(lines)):
            if lines[i].strip():
                return i
        return None

    i_a = last_nonempty_idx(body_a)
    i_b = first_nonempty_idx(body_b)
    if i_a is None or i_b is None:
        return body_a, body_b

    # split into cells
    cells_a = _split_cells(body_a[i_a])
    cells_b = _split_cells(body_b[i_b])

    # pad to same length
    max_len = max(len(cells_a), len(cells_b))
    while len(cells_a) < max_len:
        cells_a.append("")
    while len(cells_b) < max_len:
        cells_b.append("")

    idxs_a = {idx for idx, val in enumerate(cells_a) if val.strip()}
    idxs_b = {idx for idx, val in enumerate(cells_b) if val.strip()}

    # only merge if body_b's non-empty cols are a subset of body_a's
    if not idxs_b or not idxs_b.issubset(idxs_a):
        return body_a, body_b

    # concatenate text in those columns
    for idx in idxs_b:
        if cells_b[idx].strip():
            if cells_a[idx].strip():
                cells_a[idx] = cells_a[idx].rstrip() + " " + cells_b[idx].lstrip()
            else:
                cells_a[idx] = cells_b[idx]

    # write back merged row and drop the continuation row from body_b
    body_a[i_a] = " | ".join(cells_a)
    del body_b[i_b]

    return body_a, body_b



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

def contains_section_pointer(lines: list[str]) -> bool:
    return any(re.search(r"\(\(\d+\)\)", line) for line in lines)

def page_has_real_text(page: dict) -> bool:
    segs = build_segments(page["body"])
    for seg in segs:
        if seg["type"] == "text" and not is_ignorable_text(seg):
            # any real (non-ignorable) text blocks further chaining
            return True
    return False


def is_ignorable_text(seg: dict) -> bool:
    """
    Decide if a text segment can be ignored when searching for the
    last/first table on a page (for cross-page merging).

    We treat a segment as ignorable if:
      - it's all blank / digit-only lines, OR
      - it consists of short-ish lines that look like table leaks.
    """
    if seg["type"] != "text":
        return False

    lines = [ln.strip() for ln in seg["lines"] if ln.strip()]

    if not lines:
        return True
    
    if contains_section_pointer(lines):
        return False

    if all(is_digit_line(ln) for ln in lines):
        return True

    if len(lines) < 3 and all(len(s) <= 100 for s in lines):
        return True

    return False
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
    Previously pulled short trailing lines into the preceding table. Disabled to
    avoid dragging normal paragraphs or notes inside tables; merging is handled
    purely by table markers now.
    """
    return lines


def merge_pages(page_a: dict, page_b: dict) -> bool:
    segments_a = build_segments(page_a["body"])
    segments_b = build_segments(page_b["body"])

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

    # split header/body/footer
    header_a = table_a[0]
    footer_a = table_a[-1]
    body_a = table_a[1:-1]

    header_b = table_b[0]
    footer_b = table_b[-1]
    body_b = table_b[1:-1]

    # merge the boundary row(s) caused by page break
    body_a, body_b = merge_boundary_rows(body_a, body_b)

    # build merged table: header from A, footer from A, body = body_a + body_b
    merged_body = body_a + body_b
    merged_table = [header_a] + merged_body + [footer_a]

    # update TABLE_START metadata (rows / cols) on header
    meta_a = parse_table_header(header_a)
    if meta_a:
        meta_a["rows"] = len(merged_body)
        est_cols = estimate_cols(merged_table)
        if est_cols is not None:
            meta_a["cols"] = est_cols
        merged_table[0] = build_table_header(meta_a)

    # replace table in segments_a and remove from segments_b
    segments_a[last_a]["lines"] = merged_table
    segments_b.pop(first_b)

    page_a["body"] = flatten_segments(segments_a)
    page_b["body"] = flatten_segments(segments_b)
    return True


def merge_table_chain(pages: list[dict], start_idx: int) -> bool:
    """
    Greedily merge a table on page start_idx with subsequent pages while
    the boundary tables remain compatible.
    """
    changed = False
    j = start_idx + 1
    while j < len(pages):
        if merge_pages(pages[start_idx], pages[j]):
            changed = True
            # ✅ NEW: stop if the merged-into page still contains real text
            if page_has_real_text(pages[j]):
                break

            # Existing behavior: stop if page j still has another table to handle
            if find_first_table_idx(build_segments(pages[j]["body"])) is not None:
                break
            
            j += 1
            continue
        break
    return changed


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

    # Merge forward so multi-page chains roll up to the starting page
    idx = 0
    while idx < len(pages) - 1:
        merge_table_chain(pages, idx)
        idx += 1

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



def _split_cells(line: str) -> list[str]:
    # Simple split that works even if the line doesn't start/end with "|"
    return [c.strip() for c in line.split("|")]


def _join_nonempty_cells(cells: list[str]) -> str:
    return " ".join(c for c in cells if c.strip())

# def process_single_table_outer_rows(table_lines: list[str]) -> tuple[str | None, str | None, list[str]]:
#     """
#     For each [[TABLE_START ...]] block:

#       - If the first non-empty body row starts with a numeric item
#         like '3', '3)', '�E�！E, treat it as a section heading and move it
#         ABOVE the table.

#       - If the last non-empty body row looks like a footnote
#         (first cell starts with '※' or '*'), move it BELOW the table.

#       - Otherwise, leave the table body as-is.

#     Returns: (top_line_or_None, bottom_line_or_None, new_table_lines)
#     """
#     if len(table_lines) <= 2:
#         # no body
#         return None, None, table_lines

#     first_idx: int | None = None
#     first_title: str | None = None
#     last_idx: int | None = None
#     last_title: str | None = None

#     # ----- look for a numeric heading at the top -----
#     for idx in range(1, len(table_lines) - 1):
#         raw = table_lines[idx]
#         if not raw.strip():
#             continue
#         cells = _split_cells(raw)
#         nonempty = [c for c in cells if c.strip()]
#         if not nonempty:
#             continue
#         first_cell = nonempty[0]

#         # heading like "3", "3.", "3)", "�E�E, "�E�！E, etc.
#         if re.fullmatch(r"[0-9�E�E�E�]+[.)�E�]?", first_cell):
#             first_idx = idx
#             first_title = _title_from_nonempty(nonempty)
#         break  # only ever consider the first non-empty row

#     # ----- look for a footnote at the bottom -----
#     for idx in range(len(table_lines) - 2, 0, -1):
#         raw = table_lines[idx]
#         if not raw.strip():
#             continue
#         cells = _split_cells(raw)
#         nonempty = [c for c in cells if c.strip()]
#         if not nonempty:
#             continue
#         first_cell = nonempty[0]

#         if first_cell.startswith("※") or first_cell.startswith("*"):
#             last_idx = idx
#             last_title = _join_nonempty_cells(nonempty)
#             break

#     # ----- remove only the rows we actually classified -----
#     indices_to_pop: list[int] = []
#     if first_idx is not None:
#         indices_to_pop.append(first_idx)
#     if last_idx is not None and last_idx != first_idx:
#         indices_to_pop.append(last_idx)

#     for idx in sorted(indices_to_pop, reverse=True):
#         table_lines.pop(idx)

#     # ----- update TABLE_START metadata -----
#     meta = parse_table_header(table_lines[0])
#     if meta:
#         meta["rows"] = body_row_count(table_lines)
#         est_cols = estimate_cols(table_lines)
#         if est_cols is not None:
#             meta["cols"] = est_cols
#         table_lines[0] = build_table_header(meta)

#     return first_title, last_title, table_lines

def process_single_table_outer_rows(table_lines: list[str]) -> tuple[str | None, str | None, list[str]]:
    """
    For each [[TABLE_START ...]] block:

      - If the first non-empty body row starts with a section heading
        like '3', '3)', 'Ⅱ)', '(1)', '①', treat it as a section heading
        and move it ABOVE the table.

      - If the last non-empty body row looks like a footnote
        (first cell starts with '※' or '*'), move it BELOW the table.

      - Otherwise, leave the table body as-is.
    """
    if len(table_lines) <= 2:
        return None, None, table_lines

    first_idx: int | None = None
    first_title: str | None = None
    last_idx: int | None = None
    last_title: str | None = None

    # ----- look for a numeric / roman / bracketed heading at the top -----
    for idx in range(1, len(table_lines) - 1):
        raw = table_lines[idx]
        if not raw.strip():
            continue
        cells = _split_cells(raw)
        nonempty = [c for c in cells if c.strip()]
        if not nonempty:
            continue
        first_cell = nonempty[0]

        # patterns:
        #  - 3, 3), 3.
        #  - II, II), Ⅳ)
        #  - (1), �E�E�E�E
        #  - ①, ②, ... ⑳
        if (
            re.fullmatch(r"[0-9�E�E�E�]+[.)�E�]?", first_cell)           # digits
            or re.fullmatch(r"[ivxlcdmIVXLCDM]+[.)�E�]?", first_cell) # roman (ASCII)
            or re.fullmatch(r"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+[.)�E�]?", first_cell)  # roman (full-width)
            or re.fullmatch(r"[\(�E�E[0-9�E�E�E�]+[)�E�]", first_cell)    # (1), �E�E�E�E
            or re.fullmatch(r"[\u2460-\u2473]", first_cell)          # ①–⑳
        ):
            first_idx = idx
            first_title = _title_from_nonempty(nonempty)
        break  # only consider the first non-empty body row

    # ----- look for a footnote at the bottom -----
    for idx in range(len(table_lines) - 2, 0, -1):
        raw = table_lines[idx]
        if not raw.strip():
            continue
        cells = _split_cells(raw)
        nonempty = [c for c in cells if c.strip()]
        if not nonempty:
            continue
        first_cell = nonempty[0]

        if first_cell.startswith("※") or first_cell.startswith("*"):
            last_idx = idx
            last_title = _join_nonempty_cells(nonempty)
            break

    # ----- remove only the rows we actually classified -----
    indices_to_pop: list[int] = []
    if first_idx is not None:
        indices_to_pop.append(first_idx)
    if last_idx is not None and last_idx != first_idx:
        indices_to_pop.append(last_idx)

    for idx in sorted(indices_to_pop, reverse=True):
        table_lines.pop(idx)

    # ----- update TABLE_START metadata -----
    meta = parse_table_header(table_lines[0])
    if meta:
        meta["rows"] = body_row_count(table_lines)
        est_cols = estimate_cols(table_lines)
        if est_cols is not None:
            meta["cols"] = est_cols
        table_lines[0] = build_table_header(meta)

    return first_title, last_title, table_lines


def extract_outer_table_rows(text: str) -> str:
    """
    For every table:
      - Move a leading '3 | ...' style title row above the table.
      - Move a trailing '※1: ...' style footnote row below the table.
    """
    lines = text.splitlines()
    ends_with_nl = text.endswith("\n")

    out: list[str] = []
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

            title_text, footnote_text, new_table_lines = process_single_table_outer_rows(table_lines)

            if title_text:
                out.append(title_text)
            out.extend(new_table_lines)
            if footnote_text:
                out.append(footnote_text)
        else:
            out.append(line)
            i += 1

    result = "\n".join(out)
    if ends_with_nl:
        result += "\n"
    return result


# ---------- pipeline ----------
def process_text(text: str) -> str:
    text = normalize_markers(text)
    text = remove_stray_page_numbers(text)
    text = merge_cross_page_tables(text)
    text = extract_outer_table_rows(text) 
    # text = merge_continuation_rows_in_tables(text)  # ↁENEW
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


