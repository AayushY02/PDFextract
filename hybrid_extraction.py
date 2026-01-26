"""
Hybrid Extractor
================
- Does everything like test_extraction.py (structure, merges, heading tagging, multi-format support).
- BUT table output formatting matches text_extractor.py exactly.
- Tables are inserted in correct PDF reading order based on their bbox position.

Notes:
- PDF extraction uses PyMuPDF find_tables().
- Tables are added as positioned items (bbox) and sorted with text lines to preserve location.
"""

import os
import csv
import re
import fitz  # PyMuPDF
import pandas as pd
import statistics
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


# ---------- CONFIGURATION ----------
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("results/test")
LOG_FILE = OUTPUT_DIR / "log.csv"
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls"}

# Page boundary marker settings (keep the same marker style used in your scripts)
PAGE_START_TEMPLATE = "[[PAGE_START {n}]]"
PAGE_END_TEMPLATE = "[[PAGE_END]]"

# Table formatting MUST match text_extractor style
TABLE_COL_SEPARATOR = " | "
# ----------------------------------


# ---------- TABLE HELPERS (MATCH text_extractor EXACTLY) ----------
def sanitize_cell_text(cell_value):
    """
    Normalizes table cell text for compact export.
    Collapses internal whitespace and removes surrounding blanks.
    (matches text_extractor)
    """
    if not cell_value:
        return ""
    return " ".join(str(cell_value).split())


def format_table_rows(rows, header_label: str, row_count: int, col_count: int) -> str:
    """
    Convert arbitrary row data into a structured text block with explicit markers.
    (matches text_extractor)
    """
    header = f"[[TABLE_START {header_label} rows={row_count} cols={col_count}]]"
    body_rows = []
    for row in rows:
        sanitized_cells = [sanitize_cell_text(cell) for cell in row]
        body_rows.append(TABLE_COL_SEPARATOR.join(sanitized_cells))
    body = "\n".join(body_rows)
    footer = "[[TABLE_END]]"
    content_lines = [header]
    if body:
        content_lines.append(body)
    content_lines.append(footer)
    return "\n".join(content_lines) + "\n\n"


def format_table(table, page_number: int, table_index: int) -> str:
    """
    Convert a PyMuPDF table object into a structured text block with explicit markers.
    (matches text_extractor)
    """
    header_label = f"page={page_number} index={table_index}"
    return format_table_rows(
        table.extract(),
        header_label=header_label,
        row_count=table.row_count,
        col_count=table.col_count,
    )


def line_belongs_to_table(
    line_bbox,
    table_entry,
    padding: float = 1.0,
    bottom_margin_rows: float = 0.25,
) -> bool:
    """
    Determine whether a line bbox should be considered part of a table bbox.

    Kept aligned with your test_extraction behavior (bbox-center based check + bottom shrink)
    so we avoid grabbing normal text right under the table.
    """
    bx0, by0, bx1, by1 = line_bbox
    cx = (bx0 + bx1) / 2
    cy = (by0 + by1) / 2

    tx0, ty0, tx1, ty1 = table_entry["bbox"]
    row_h = table_entry.get("row_height") or 0.0

    if row_h > 0:
        ty1_adj = ty1 - row_h * bottom_margin_rows
    else:
        ty1_adj = ty1

    return (
        (tx0 - padding) <= cx <= (tx1 + padding)
        and (ty0 - padding) <= cy <= (ty1_adj + padding)
    )


# ---------- DOCX BLOCK ITER ----------
def iter_docx_blocks(document):
    """Yield paragraphs and tables in the original document order."""
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


# ---------- PDF PAGE EXTRACTION ----------
def extract_page_body(page, page_number: int) -> str:
    """
    Page extraction with:
      - Stable reading-order sorting (top-to-bottom, left-to-right)
      - Tables inserted at their real page position (bbox-sorted)
      - Heading tagging via font size heuristic
      - Merge list-marker-only lines into the next line
      - Merge spaced single-CJK-glyph runs into one line
    Table *formatting* matches text_extractor exactly.
    """
    # Detect tables first
    table_finder = page.find_tables()
    tables = []
    if table_finder:
        for table_index, table in enumerate(table_finder.tables, start=1):
            tx0, ty0, tx1, ty1 = table.bbox
            height = ty1 - ty0
            row_h = height / max(table.row_count, 1)

            tables.append(
                {
                    "bbox": table.bbox,
                    "row_height": row_h,
                    "content": format_table(table, page_number, table_index),
                    "item_added": False,  # we add a table item once
                }
            )

    def _bbox(obj):
        return obj.get("bbox", (0, 0, 0, 0))

    def _sort_key_bbox(obj):
        x0, y0, x1, y1 = _bbox(obj)
        return (y0, x0, x1, y1)

    def _join_spans(line) -> str:
        """Join spans left-to-right; insert space only when it looks like Latin-word separation."""
        spans = sorted(line.get("spans", []), key=_sort_key_bbox)
        parts = []
        prev_x1 = None
        prev_txt = ""
        for sp in spans:
            txt = sp.get("text", "")
            if not txt:
                continue
            x0, y0, x1, y1 = sp.get("bbox", (0, 0, 0, 0))
            if prev_x1 is not None:
                gap = x0 - prev_x1
                if gap > 1.5 and prev_txt and txt:
                    if re.search(r"[A-Za-z0-9]$", prev_txt) and re.search(r"^[A-Za-z0-9]", txt):
                        parts.append(" ")
            parts.append(txt)
            prev_x1 = x1
            prev_txt = txt
        return "".join(parts)

    def _is_single_cjk_char(s: str) -> bool:
        s = s.strip()
        if len(s) != 1:
            return False
        ch = s[0]
        return bool(
            ("\u4e00" <= ch <= "\u9fff")  # CJK
            or ("\u3040" <= ch <= "\u309f")  # Hiragana
            or ("\u30a0" <= ch <= "\u30ff")  # Katakana
            or ("\u3000" <= ch <= "\u303f")  # CJK punctuation
        )

    def _merge_glyph_runs(items: list[dict]) -> list[dict]:
        """Merge consecutive single-CJK-char lines that obviously form a title run."""
        out = []
        i = 0
        while i < len(items):
            cur = items[i]
            txt = cur["text"].strip()
            if not _is_single_cjk_char(txt):
                out.append(cur)
                i += 1
                continue

            x0, y0, x1, y1 = cur["bbox"]
            base_x = (x0 + x1) / 2
            base_y = (y0 + y1) / 2

            def try_run(mode: str):
                run_chars = [txt]
                run_bbox = list(cur["bbox"])
                j = i + 1
                last_x = base_x
                last_y = base_y
                while j < len(items):
                    nxt = items[j]
                    nt = nxt["text"].strip()
                    if not _is_single_cjk_char(nt):
                        break
                    nx0, ny0, nx1, ny1 = nxt["bbox"]
                    nx = (nx0 + nx1) / 2
                    ny = (ny0 + ny1) / 2

                    if mode == "h":
                        if abs(ny - base_y) > 2:
                            break
                        if nx <= last_x:
                            break
                    else:
                        if abs(nx - base_x) > 6:
                            break
                        if ny <= last_y:
                            break

                    run_chars.append(nt)
                    run_bbox[0] = min(run_bbox[0], nx0)
                    run_bbox[1] = min(run_bbox[1], ny0)
                    run_bbox[2] = max(run_bbox[2], nx1)
                    run_bbox[3] = max(run_bbox[3], ny1)
                    last_x, last_y = nx, ny
                    j += 1
                return run_chars, tuple(run_bbox), j

            h_chars, h_bbox, h_end = try_run("h")
            v_chars, v_bbox, v_end = try_run("v")

            if len(h_chars) >= len(v_chars):
                run_chars, run_bbox, end = h_chars, h_bbox, h_end
            else:
                run_chars, run_bbox, end = v_chars, v_bbox, v_end

            if len(run_chars) >= 3:
                merged_txt = "".join(run_chars) + "\n"
                out.append({"kind": "text", "text": merged_txt, "bbox": run_bbox, "size": cur["size"]})
                i = end
            else:
                out.append(cur)
                i += 1
        return out

    def _merge_list_markers(items: list[dict]) -> list[dict]:
        """Merge lines that are just a list marker with the next line."""
        marker_re = re.compile(r"^\s*([ア-ン]|[A-Z]|[a-z]|[0-9]+|[①-⑳])\s*$")
        out = []
        i = 0
        while i < len(items):
            cur = items[i]
            cur_stripped = cur["text"].strip()
            if marker_re.match(cur_stripped) and i + 1 < len(items):
                nxt = items[i + 1]
                if nxt["text"].strip():
                    merged = f"{cur_stripped} {nxt['text'].lstrip()}"
                    if not merged.endswith("\n"):
                        merged += "\n"
                    bx0, by0, bx1, by1 = cur["bbox"]
                    nx0, ny0, nx1, ny1 = nxt["bbox"]
                    out.append(
                        {
                            "kind": "text",
                            "text": merged,
                            "bbox": (min(bx0, nx0), min(by0, ny0), max(bx1, nx1), max(by1, ny1)),
                            "size": max(cur["size"], nxt["size"]),
                        }
                    )
                    i += 2
                    continue
            out.append(cur)
            i += 1
        return out

    # Extract dict text
    try:
        info = page.get_text("dict", sort=True)
    except TypeError:
        info = page.get_text("dict")

    # Heading threshold
    span_sizes = []
    for block in info.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                sz = span.get("size")
                if isinstance(sz, (int, float)):
                    span_sizes.append(float(sz))
    median_size = statistics.median(span_sizes) if span_sizes else 0.0
    size_threshold = median_size + 1.5

    items: list[dict] = []

    blocks = sorted(info.get("blocks", []), key=_sort_key_bbox)
    for block in blocks:
        lines = sorted(block.get("lines", []), key=_sort_key_bbox)
        for line in lines:
            line_text = _join_spans(line)
            if not line_text:
                continue
            if not line_text.endswith("\n"):
                line_text += "\n"

            x0, y0, x1, y1 = line.get("bbox", (0, 0, 0, 0))
            line_bbox = (x0, y0, x1, y1)

            sizes = [float(span.get("size", 0)) for span in line.get("spans", [])]
            line_size = max(sizes) if sizes else 0.0

            # ---- TABLE: add positioned table item ONCE, do not emit immediately ----
            table_entry = None
            for entry in tables:
                if line_belongs_to_table(line_bbox, entry):
                    table_entry = entry
                    break

            if table_entry is not None:
                if not table_entry["item_added"]:
                    tx0, ty0, tx1, ty1 = table_entry["bbox"]
                    items.append(
                        {
                            "kind": "table",
                            "text": table_entry["content"],
                            "bbox": (tx0, ty0, tx1, ty1),
                            "size": 0.0,
                        }
                    )
                    table_entry["item_added"] = True
                continue

            # ---- NORMAL TEXT ----
            collapsed = "".join(line_text.strip().split())
            if collapsed and line_size >= size_threshold:
                items.append({"kind": "text", "text": f"[[HEADING]] {line_text}", "bbox": line_bbox, "size": line_size})
            else:
                items.append({"kind": "text", "text": line_text, "bbox": line_bbox, "size": line_size})

    # Sort all items once -> correct order including tables
    items = sorted(items, key=_sort_key_bbox)

    # Post-process merges on TEXT runs between tables (so we don't reorder tables)
    def flush_text_run(run: list[dict], out: list[str]):
        if not run:
            return
        run = _merge_glyph_runs(run)
        run = _merge_list_markers(run)
        out.extend(x["text"] for x in run)

    out_segments: list[str] = []
    text_run: list[dict] = []

    for it in items:
        if it["kind"] == "table":
            flush_text_run(text_run, out_segments)
            text_run = []
            out_segments.append(it["text"])
        else:
            text_run.append(it)

    flush_text_run(text_run, out_segments)

    page_body = "".join(out_segments)
    if page_body and not page_body.endswith("\n"):
        page_body += "\n"
    return page_body


# ---------- FILE TYPE EXTRACTORS ----------
def extract_text_from_pdf(pdf_path: Path):
    """Extract text from PDF with page boundary markers."""
    with fitz.open(pdf_path) as doc:
        page_count = len(doc)
        chunks = []

        for idx, page in enumerate(doc, start=1):
            page_text = extract_page_body(page, idx)
            if not page_text:
                fallback_text = page.get_text("text") or ""
                if fallback_text and not fallback_text.endswith("\n"):
                    fallback_text += "\n"
                page_text = fallback_text

            start_marker = f"{PAGE_START_TEMPLATE.format(n=idx)}\n\n"
            end_marker = f"\n{PAGE_END_TEMPLATE.format(n=idx)}\n"
            chunks.append(start_marker + page_text + end_marker)

        return "".join(chunks), page_count


def extract_text_from_docx(docx_path: Path):
    """
    Extract embedded text from a Word (.docx) file.
    Treat as single page for marker consistency.
    Table formatting matches text_extractor.
    """
    doc = Document(docx_path)
    segments = []
    table_index = 0

    for block in iter_docx_blocks(doc):
        if isinstance(block, Paragraph):
            text = (block.text or "").strip()
            if not text:
                continue
            if not text.endswith("\n"):
                text += "\n"
            style_name = block.style.name if block.style else ""
            if style_name and style_name.lower().startswith("heading"):
                segments.append(f"[[HEADING]] {text}")
            else:
                segments.append(text)

        elif isinstance(block, Table):
            table_index += 1
            rows = []
            for row in block.rows:
                rows.append([sanitize_cell_text(cell.text) for cell in row.cells])

            # Approx col count based on widest row (docx tables can be uneven)
            col_count = max((len(r) for r in rows), default=0)
            segments.append(
                format_table_rows(
                    rows=rows,
                    header_label=f"page=1 index={table_index}",
                    row_count=len(rows),
                    col_count=col_count,
                )
            )

    body = "".join(segments)
    start_marker = f"{PAGE_START_TEMPLATE.format(n=1)}\n\n"
    end_marker = f"\n{PAGE_END_TEMPLATE.format(n=1)}\n"
    return start_marker + body + end_marker, 1


def extract_text_from_excel(excel_path: Path):
    """
    Extract embedded text from Excel.
    Emit one table per sheet, formatted like text_extractor.
    """
    workbook = pd.ExcelFile(excel_path)
    chunks = []

    for idx, sheet_name in enumerate(workbook.sheet_names, start=1):
        df = workbook.parse(sheet_name, header=None, dtype=object)
        df = df.where(pd.notnull(df), "")
        rows = df.astype(str).values.tolist()
        col_count = df.shape[1] if not df.empty else 0

        table_text = format_table_rows(
            rows=rows,
            header_label=f"page={idx} index=1 sheet={sanitize_cell_text(sheet_name)}",
            row_count=len(rows),
            col_count=col_count,
        )
        start_marker = f"{PAGE_START_TEMPLATE.format(n=idx)}\n\n"
        end_marker = f"\n{PAGE_END_TEMPLATE.format(n=idx)}\n"
        chunks.append(start_marker + table_text + end_marker)

    return "".join(chunks), len(workbook.sheet_names)


# ---------- PIPELINE / IO ----------
def ensure_output_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def write_log_row(writer, file_path: Path, pages: int, status: str, error: str = ""):
    writer.writerow(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "file": str(file_path),
            "pages": pages,
            "status": status,
            "error": error,
        }
    )


def process_one_file(file_path: Path, input_dir: Path, output_dir: Path):
    relative_path = file_path.relative_to(input_dir)
    output_path = output_dir / relative_path.with_suffix(".txt")
    suffix = file_path.suffix.lower()

    try:
        if suffix == ".pdf":
            text, pages = extract_text_from_pdf(file_path)
        elif suffix == ".docx":
            text, pages = extract_text_from_docx(file_path)
        elif suffix in {".xlsx", ".xls"}:
            text, pages = extract_text_from_excel(file_path)
        else:
            raise ValueError(f"Unsupported extension: {suffix}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        return str(relative_path), pages, "OK", ""

    except Exception as e:
        return str(relative_path), 0, "FAIL", str(e)


def collect_supported_files(input_dir: Path):
    return sorted(
        (
            p for p in input_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda p: str(p).lower(),
    )


def process_documents(input_dir: Path, output_dir: Path):
    ensure_output_dir(output_dir)

    files = collect_supported_files(input_dir)
    if not files:
        print(f"No supported files found in: {input_dir}")
        return

    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "file", "pages", "status", "error"])
        writer.writeheader()

        with ProcessPoolExecutor() as ex:
            futures = [ex.submit(process_one_file, p, input_dir, output_dir) for p in files]
            for fut in as_completed(futures):
                rel, pages, status, error = fut.result()
                write_log_row(writer, rel, pages, status, error)
                if status == "OK":
                    print(f"✅ Extracted: {rel} ({pages} pages/sheets)")
                else:
                    print(f"❌ Failed: {rel} ({error})")

    print("\nAll done!")
    print(f"📂 Extracted texts: {output_dir}")
    print(f"📄 Log file: {LOG_FILE}")


# Backwards-compatible entry point name
def process_pdfs(input_dir: Path, output_dir: Path):
    process_documents(input_dir, output_dir)


if __name__ == "__main__":
    process_documents(INPUT_DIR, OUTPUT_DIR)
