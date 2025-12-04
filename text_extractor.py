"""
PDF Text Extractor with Page Start/End Markers (results/output1 version)
=======================================================================

This script recursively scans the 'input' folder for PDF files,
extracts their embedded text (no OCR), and saves the result in:
    results/output1/

Enhancements:
    - Adds explicit page boundary identifiers ONLY:
        * [[PAGE_START N]] at the very beginning of each page (then a blank line)
        * [[PAGE_END   N]] after each page's text
    - No "Page N" footer lines
    - No form-feed (\f) separators
    - Detects tabular regions and replaces their text with structured markers:
        * [[TABLE_START page=P index=I rows=R cols=C]]
        * Pipe-delimited rows (`col1 | col2 | col3`)
        * [[TABLE_END]]

Layout per page N in the TXT:
    [[PAGE_START N]]

    <page N text>

    [[PAGE_END   N]]

It also writes a CSV log file (results/extraction_log.csv)
summarizing:
    - File path (relative to input)
    - Page count
    - Status (OK/FAIL)
    - Error message (if any)

Requirements:
    pip install PyMuPDF

Usage:
    python pdf_text_extractor.py
"""

import csv
import fitz  # PyMuPDF
import statistics
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
# ---------- CONFIGURATION ----------
INPUT_DIR = Path("input")
RESULTS_DIR = Path("results")
OUTPUT_DIR = RESULTS_DIR / "output1"
LOG_FILE = RESULTS_DIR / "extraction_log.csv"
EXTENSION = ".pdf"

# Page boundary marker settings
PAGE_START_TEMPLATE = "[[PAGE_START {n}]]"
PAGE_END_TEMPLATE = "[[PAGE_END]]"
TABLE_COL_SEPARATOR = " | "
# ----------------------------------

def process_one_pdf(pdf_path: Path, input_dir: Path, output_dir: Path):
    relative_path = pdf_path.relative_to(input_dir)
    output_path = output_dir / relative_path.with_suffix(".txt")

    try:
        text, pages = extract_text_from_pdf(pdf_path)
        save_text(output_path, text)
        return relative_path, pages, "OK", ""
    except Exception as e:
        return relative_path, 0, "FAIL", str(e)


def sanitize_cell_text(cell_value):
    """
    Normalizes table cell text for compact export.
    Collapses internal whitespace and removes surrounding blanks.
    """
    if not cell_value:
        return ""
    return " ".join(str(cell_value).split())


def format_table(table, page_number: int, table_index: int) -> str:
    """
    Convert a PyMuPDF table object into a structured text block with explicit markers.
    Cells are joined with the configured column separator to keep columns clear.
    """
    header = (
        f"[[TABLE_START page={page_number} index={table_index} "
        f"rows={table.row_count} cols={table.col_count}]]"
    )
    rows = []
    for row in table.extract():
        sanitized_cells = [sanitize_cell_text(cell) for cell in row]
        rows.append(TABLE_COL_SEPARATOR.join(sanitized_cells))
    body = "\n".join(rows)
    footer = "[[TABLE_END]]"
    content_lines = [header]
    if body:
        content_lines.append(body)
    content_lines.append(footer)
    return "\n".join(content_lines) + "\n\n"


def block_center_in_bbox(block_bbox, table_bbox, padding: float = 0.5) -> bool:
    """
    Check if the center of a text block falls within the table bounding box.
    Padding slightly enlarges the table bounds to cover rounding differences.
    """
    bx0, by0, bx1, by1 = block_bbox
    tx0, ty0, tx1, ty1 = table_bbox
    cx = (bx0 + bx1) / 2
    cy = (by0 + by1) / 2
    return (
        (tx0 - padding) <= cx <= (tx1 + padding)
        and (ty0 - padding) <= cy <= (ty1 + padding)
    )

def line_belongs_to_table(
    line_bbox,
    table_entry,
    padding: float = 0.5,
    bottom_margin_rows: float = 0.4,
) -> bool:
    """
    Decide if a text line should be treated as part of a table.

    We slightly shrink the bottom of the table bbox so that normal text just
    under the table is not accidentally considered "inside" the table region.
    """
    bx0, by0, bx1, by1 = line_bbox
    cx = (bx0 + bx1) / 2
    cy = (by0 + by1) / 2

    tx0, ty0, tx1, ty1 = table_entry["bbox"]
    row_h = table_entry.get("row_height") or 0.0

    # shrink table bottom by a fraction of one row height
    if row_h > 0:
        ty1_adj = ty1 - row_h * bottom_margin_rows
    else:
        ty1_adj = ty1

    return (
        (tx0 - padding) <= cx <= (tx1 + padding)
        and (ty0 - padding) <= cy <= (ty1_adj + padding)
    )



def extract_page_body(page, page_number: int) -> str:
    """
    Build the body text for a single page, replacing detected tables with structured markers.
    """
    table_finder = page.find_tables()
    tables = []
    # if table_finder:
    #     for table_index, table in enumerate(table_finder.tables, start=1):
    #         tables.append(
    #             {
    #                 "bbox": table.bbox,
    #                 "content": format_table(table, page_number, table_index),
    #                 "emitted": False,
    #             }
    #         )
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
                    "emitted": False,
                }
            )


    segments = []
    info = page.get_text("dict")
    span_sizes = []
    for block in info.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                sz = span.get("size")
                if isinstance(sz, (int, float)):
                    span_sizes.append(float(sz))
    median_size = statistics.median(span_sizes) if span_sizes else 0.0
    size_threshold = median_size + 1.5

    for block in info.get("blocks", []):
        for line in block.get("lines", []):
            # compose line text
            line_text = "".join(span.get("text", "") for span in line.get("spans", []))
            if not line_text:
                continue
            if not line_text.endswith("\n"):
                line_text += "\n"

            # line bbox and max size
            x0, y0, x1, y1 = line.get("bbox", [0, 0, 0, 0])
            line_bbox = (x0, y0, x1, y1)
            sizes = [float(span.get("size", 0)) for span in line.get("spans", [])]
            line_size = max(sizes) if sizes else 0.0

            # table handling: emit once when first encountered
            # table_entry = None
            # for entry in tables:
            #     if block_center_in_bbox(line_bbox, entry["bbox"]):
            #         table_entry = entry
            #         break
            # if table_entry is not None:
            #     if not table_entry["emitted"]:
            #         segments.append(table_entry["content"])
            #         table_entry["emitted"] = True
            #     continue
            table_entry = None
            for entry in tables:
                if line_belongs_to_table(line_bbox, entry):
                    table_entry = entry
                    break

            if table_entry is not None:
                # emit table once, skip individual table lines
                if not table_entry["emitted"]:
                    segments.append(table_entry["content"])
                    table_entry["emitted"] = True
                continue


            # heading marker for large font lines (inline before the text)
            collapsed = "".join(line_text.strip().split())
            if collapsed and line_size >= size_threshold:
                segments.append(f"[[HEADING]] {line_text}")
            else:
                segments.append(line_text)

    for entry in tables:
        if not entry["emitted"]:
            segments.append(entry["content"])

    page_body = "".join(segments)
    if page_body and not page_body.endswith("\n"):
        page_body += "\n"
    return page_body


def extract_text_from_pdf(pdf_path: Path):
    """
    Extracts text and counts pages from a PDF using PyMuPDF.

    For each page N:
        - Insert a page-start marker line: [[PAGE_START N]], followed by a blank line.
        - Append the page's extracted text (ensuring trailing newline).
        - Insert a page-end marker line: [[PAGE_END N]].

    Returns:
        combined_text (str), page_count (int)
    """
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

            # Build the page chunk with ONLY our markers
            start_marker = f"{PAGE_START_TEMPLATE.format(n=idx)}\n\n"
            end_marker = f"\n{PAGE_END_TEMPLATE.format(n=idx)}\n"

            chunk = start_marker + page_text + end_marker
            chunks.append(chunk)

        combined_text = "".join(chunks)
        return combined_text, page_count


def save_text(output_path: Path, text: str):
    """Writes text to a UTF-8 encoded file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def init_log():
    """Initialize CSV log file in the results folder."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "file", "pages", "status", "error"])


def append_log(file_path: Path, pages: int, status: str, error: str = ""):
    """Append a single record to the log file."""
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            str(file_path),
            pages,
            status,
            error
        ])


# def process_pdfs(input_dir: Path, output_dir: Path):
#     """Recursively processes all PDFs in input_dir and saves text to output_dir."""
#     pdf_files = list(input_dir.rglob(f"*{EXTENSION}"))
#     if not pdf_files:
#         print(f"No PDF files found in: {input_dir}")
#         return

#     init_log()
#     print(f"Found {len(pdf_files)} PDF files. Starting extraction...\n")

#     for pdf_path in pdf_files:
#         relative_path = pdf_path.relative_to(input_dir)
#         output_path = output_dir / relative_path.with_suffix(".txt")

#         try:
#             text, pages = extract_text_from_pdf(pdf_path)
#             save_text(output_path, text)
#             append_log(relative_path, pages, "OK")
#             print(f"✅ Extracted: {pdf_path}  ({pages} pages)")
#         except Exception as e:
#             append_log(relative_path, 0, "FAIL", str(e))
#             print(f"❌ Failed: {pdf_path} ({e})")

#     print("\nAll done!")
#     print(f"📂 Extracted texts: {output_dir}")
#     print(f"📄 Log file: {LOG_FILE}")

def process_pdfs(input_dir: Path, output_dir: Path):
    pdf_files = list(input_dir.rglob(f"*{EXTENSION}"))
    if not pdf_files:
        print(f"No PDF files found in: {input_dir}")
        return

    init_log()
    print(f"Found {len(pdf_files)} PDF files. Starting extraction...\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(process_one_pdf, pdf_path, input_dir, output_dir): pdf_path
            for pdf_path in pdf_files
        }

        for fut in as_completed(futures):
            rel, pages, status, error = fut.result()
            append_log(rel, pages, status, error)
            if status == "OK":
                print(f"✅ Extracted: {rel}  ({pages} pages)")
            else:
                print(f"❌ Failed: {rel} ({error})")

    print("\nAll done!")
    print(f"📂 Extracted texts: {output_dir}")
    print(f"📄 Log file: {LOG_FILE}")


if __name__ == "__main__":
    process_pdfs(INPUT_DIR, OUTPUT_DIR)
