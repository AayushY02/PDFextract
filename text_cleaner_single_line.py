"""
Single-line Text Cleaner

- Reuses the full cleaning pipeline from text_cleaner.py
- Then removes [[PAGE_START ...]] / [[PAGE_END]] lines
- Finally flattens everything to a single physical line
  (no line breaks, no extra spaces inserted at join points)

Input:  results/output1/*.txt   (same as original)
Output: results/output_singleline/*.txt
"""

from pathlib import Path
from datetime import datetime
import text_cleaner as base  # your existing cleaner module

# --- Override: collapse paragraph lines without adding extra spaces ---

# Keep a reference to the original function
_orig_collapse_paragraph_lines = base.clean_collapse_paragraph_lines

def _collapse_paragraph_lines_no_extra_spaces(text: str) -> str:
    """
    Call the original collapse function, but delete the spaces it inserts
    when it replaces line breaks. So:
        '入\\n札公告' → '入札公告'  (no '入 札')
        '案件)に\\nついては' → '案件)については'
    Other spacing edits (inside a line) are left alone.
    """
    original = text
    collapsed = _orig_collapse_paragraph_lines(text)

    i = j = 0
    len_orig = len(original)
    len_collapsed = len(collapsed)
    out_chars = []

    while i < len_orig and j < len_collapsed:
        if original[i] == collapsed[j]:
            # Same char → pass through
            out_chars.append(collapsed[j])
            i += 1
            j += 1
        elif original[i] == "\n":
            # We hit a newline in the original:
            #   - skip the newline itself
            #   - drop any immediate spaces that collapsed added in its place
            i += 1
            while j < len_collapsed and collapsed[j] == " ":
                j += 1
            # Don't append anything → newline + its synthetic spaces vanish
        else:
            # Some other edit (space compression, punctuation tweaks, etc.)
            # Keep whatever the original function produced.
            out_chars.append(collapsed[j])
            j += 1

    # Append any remaining tail from collapsed
    if j < len_collapsed:
        out_chars.append(collapsed[j:])

    return "".join(out_chars)

# Patch the function that the pipeline uses
base.clean_collapse_paragraph_lines = _collapse_paragraph_lines_no_extra_spaces



# ---------- CONFIGURATION ----------
BASE_DIR = base.BASE_DIR          # reuse same base "results" folder
INPUT_DIR = base.INPUT_DIR        # results/output1
OUTPUT_DIR = BASE_DIR / "output3"
LOG_FILE = BASE_DIR / "cleaning_log_singleline.txt"
# ----------------------------------


def log(message: str) -> None:
    """Small separate log just for the single-line cleaner."""
    OUTPUT_DIR.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")


# ---------- EXTRA RULES FOR THIS VARIANT ----------

def remove_page_markers(text: str) -> str:
    """
    Drop lines that are pure page markers:
        [[PAGE_START N]]
        [[PAGE_END]]
    (or similar variations starting with those tokens).
    """
    kept_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[[PAGE_START ") or stripped.startswith("[[PAGE_END"):
            # skip page markers entirely in this variant
            continue
        kept_lines.append(line)
    return "\n".join(kept_lines)


def collapse_to_single_line(text: str) -> str:
    """
    Remove all line breaks so everything becomes a single line.

    Important: we do NOT insert any extra spaces while joining.
    Whatever spaces are already in the cleaned text are preserved as-is.
    """
    # Normalize any CRLF / CR to LF, then strip all line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "".join(text.splitlines())
# ----------------------------------


def apply_cleaning_pipeline_single_line(text: str, file_name: str = "") -> str:
    """
    1. Run the original cleaning pipeline from text_cleaner.py
       (all your existing rules).
    2. Remove page markers ([[PAGE_START...]], [[PAGE_END]]).
    3. Flatten to one physical line (no line breaks, no added spaces).
    """
    # Step 1: your original rules (full-width → half-width, units, footers,
    #         入札説明書 start, end headings, table/footnote handling, etc.)
    cleaned = base.apply_cleaning_pipeline(text, file_name=file_name)

    # Step 2: drop page markers from the final content
    cleaned = remove_page_markers(cleaned)

    # Step 3: flatten everything to a single line
    cleaned = collapse_to_single_line(cleaned)

    return cleaned


def save_cleaned_text(output_path: Path, text: str) -> None:
    """Write the final single-line text."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)


def process_text_files(input_dir: Path = INPUT_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    """
    Read text files from input_dir, pass them through:
        original cleaning pipeline → remove page markers → flatten to 1 line,
    and save results into output_dir with the same relative paths.
    """
    text_files = list(input_dir.rglob("*.txt"))
    if not text_files:
        print(f"No text files found in: {input_dir}")
        return

    log(f"Started single-line cleaning for {len(text_files)} files.")

    for txt_path in text_files:
        relative_path = txt_path.relative_to(input_dir)
        output_path = output_dir / relative_path

        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            cleaned_single_line = apply_cleaning_pipeline_single_line(
                raw_text,
                file_name=str(relative_path),
            )
            save_cleaned_text(output_path, cleaned_single_line)

            print(f"✅ Single-line cleaned: {txt_path}")
            log(f"OK - {relative_path}")
        except Exception as e:
            print(f"❌ Failed: {txt_path} ({e})")
            log(f"FAIL - {relative_path} ({e})")

    log("Single-line cleaning complete.\n")
    print("\nAll single-line files saved in:", output_dir)


if __name__ == "__main__":
    process_text_files()
