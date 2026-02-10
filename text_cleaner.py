"""
Text Cleaner (Non-regex, Modular)
=================================

This script reads all text files from `results/output1`,
applies cleaning functions, and saves cleaned text into
`results/output2`, preserving the folder structure.

RULE 1 IMPLEMENTED:
-------------------
Convert full-width (zenkaku) characters to half-width (hankaku).
Example: Ａ → A, ａ → a, １ → 1

Future rules can be added as new functions.

Requirements:
    Uses only built-in libraries (no regex).

Usage:
    python text_cleaner.py
"""

import os
import unicodedata
from pathlib import Path
import shutil
from datetime import datetime
import csv
import re

# ---------- CONFIGURATION ----------
BASE_DIR = Path("results")

# INPUT_DIR = BASE_DIR / "test"
# OUTPUT_DIR = BASE_DIR / "test2"

INPUT_DIR = BASE_DIR / "output1"
OUTPUT_DIR = BASE_DIR / "output2"

LOG_FILE = BASE_DIR / "cleaning_log.txt"
# ----------------------------------

# ---------- TABLE HELPERS ----------
TABLE_START_MARKER = "[[TABLE_START"
TABLE_END_MARKER = "[[TABLE_END]]"

# ---------- CHARACTER & LABEL HELPERS ----------

def _is_cjk(ch: str) -> bool:
    """Return True if ch is a Japanese CJK/Hiragana/Katakana-ish character."""
    if not ch:
        return False
    code = ord(ch)
    return (
        0x4E00 <= code <= 0x9FFF   # CJK Unified
        or 0x3400 <= code <= 0x4DBF  # CJK Ext A
        or 0x3040 <= code <= 0x309F  # Hiragana
        or 0x30A0 <= code <= 0x30FF  # Katakana
        or 0xFF66 <= code <= 0xFF9D  # Half-width Katakana
        or ch in "々〆ヶ"
    )


_LABEL_LIKE_SUFFIXES = (
    "日", "等", "名", "場所", "内容", "概要", "期", "期間", "方法", "方式", "金額",
)


def _strip_point_bullet_prefix(line: str) -> str:
    """
    Remove leading bullets / numbers like:
    '1. ', '２．', '(1)', '①', etc.
    """
    s = line.strip()
    # strip typical numeric / bullet style prefixes
    s = re.sub(r"^[0-9０-９IVXivx一二三四五六七八九十①-⑳\(\)（）\.\s　]+", "", s)
    return s


def _is_label_like_point(line: str) -> bool:
    """
    Heuristic:判定 if a bullet line is something like '公告日', '契約担当官等',
    '工事名', '工事場所' etc.
    """
    core = _strip_point_bullet_prefix(line)
    if not core:
        return False
    # Labels tend to be short
    if len(core) > 12:
        return False
    return core.endswith(_LABEL_LIKE_SUFFIXES)


def _apply_preserving_tables(text: str, transform) -> str:
    """
    Apply `transform` only to regions outside [[TABLE_START...[[TABLE_END]] blocks.
    Table blocks (including trailing newline characters) are passed through untouched.
    """
    if TABLE_START_MARKER not in text:
        return transform(text)

    result_parts = []
    cursor = 0
    text_len = len(text)

    while cursor < text_len:
        start_idx = text.find(TABLE_START_MARKER, cursor)
        if start_idx == -1:
            tail = text[cursor:]
            if tail:
                result_parts.append(transform(tail))
            else:
                result_parts.append(tail)
            break

        before = text[cursor:start_idx]
        if before:
            result_parts.append(transform(before))
        elif before == "":
            result_parts.append(before)

        end_idx = text.find(TABLE_END_MARKER, start_idx)
        if end_idx == -1:
            result_parts.append(text[start_idx:])
            cursor = text_len
            break

        end_idx += len(TABLE_END_MARKER)
        while end_idx < text_len and text[end_idx] in ("\n", "\r"):
            end_idx += 1

        result_parts.append(text[start_idx:end_idx])
        cursor = end_idx

    return "".join(result_parts)


def export_global_audit(
    file_name: str,
    status: str,
    start_keyword: str,
    start_page: str,
    end_keyword: str,
    end_page: str,
    page_range: str,
):
    """
    Append an entry to the global cleaning audit file.

    Columns:
        file, status, start_keyword, start_page,
        end_keyword, end_page, page_range
    """
    audit_path = BASE_DIR / "global_cleaning_audit.csv"
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    header_needed = not audit_path.exists()

    with open(audit_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow([
                "file",
                "status",
                "start_keyword",
                "start_page",
                "end_keyword",
                "end_page",
                "page_range",
            ])
        writer.writerow([
            file_name,
            status,
            start_keyword,
            start_page,
            end_keyword,
            end_page,
            page_range,
        ])


# ---------- RULE 1 ----------
def clean_fullwidth_to_halfwidth(text: str) -> str:
    """
    Convert all full-width (zenkaku) characters and common Japanese punctuation
    into half-width ASCII equivalents.

    - Uses Unicode NFKC normalization for general conversions.
    - Applies an extra mapping for symbols that NFKC does not change.
    """
    # Preserve circled digits (U+2460..U+2473) across NFKC normalization.
    circled_tokens = {chr(code): f"__CIRCLED_{i}__" for i, code in enumerate(range(0x2460, 0x2474), start=1)}
    for ch, token in circled_tokens.items():
        if ch in text:
            text = text.replace(ch, token)

    text = unicodedata.normalize("NFKC", text)

    # Manual mappings for characters not handled by NFKC
    replacements = {     # long vowel mark
        "〜": "~",     # wave dash
        "～": "~",     # fullwidth tilde variant
        "・": "･",     # middle dot → half-width dot
        "／": "/",
        "＼": "\\",
        "＋": "+",
        "－": "-",
        "＝": "=",
        "，": ",",
        "．": ".",
        "；": ";",
        "：": ":",
        "？": "?",
        "！": "!",
        "｜": "|",
        "＄": "$",
        "％": "%",
        "＠": "@",
        "＾": "^",
        "＆": "&",
        "＊": "*",
        "＃": "#",
    }

    for full, half in replacements.items():
        text = text.replace(full, half)

    for ch, token in circled_tokens.items():
        if token in text:
            text = text.replace(token, ch)

    return text
# ----------------------------

# ---------- RULE 2 ----------
def clean_fullwidth_space(text: str) -> str:
    """
    Replace full-width spaces (U+3000) with normal half-width spaces.
    Example: 'Ａ　Ｂ' → 'A B'
    """
    return text.replace("　", " ")
# -----------------------------

# ---------- RULE 3 ----------
# def clean_compress_spaces(text: str) -> str:
#     """
#     Compress consecutive spaces (mix of full/half width) into one space.
#     Uses simple Python split/join, no regex.
#     """
#     # Split collapses any sequence of whitespace and rejoins with single space
#     return " ".join(text.split())
def clean_compress_spaces(text: str) -> str:
    """
    Compress consecutive spaces within lines but preserve line breaks.
    """
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        # Only compress spaces *inside* the line
        cleaned_line = " ".join(line.split())
        cleaned_lines.append(cleaned_line)
    # Reconstruct text with original line breaks
    return "\n".join(cleaned_lines)
# -----------------------------

# ---------- RULE 4 ----------
def clean_space_around_units(text: str) -> str:
    """
    Remove unnecessary spaces before or after date/unit markers.
    Examples:
        "2024 年 5 月 1 日" → "2024年5月1日"
        "50 ％" → "50％"
        "100 円" → "100円"
        "5 m" → "5m"
    """
    # Define unit markers that should not have surrounding spaces
    unit_symbols = ["年", "月", "日", "式", "件", "円", "m", "㎜", "mm", "％", "%"]

    # Convert to list for mutable operations
    chars = list(text)
    result = []

    i = 0
    while i < len(chars):
        c = chars[i]

        # Remove space *before* unit markers
        if c == " " and i + 1 < len(chars) and chars[i + 1] in unit_symbols:
            i += 1
            continue

        # Remove space *after* unit markers
        if c in unit_symbols and i + 1 < len(chars) and chars[i + 1] == " ":
            result.append(c)
            i += 2
            continue

        result.append(c)
        i += 1

    return "".join(result)
# -----------------------------

# ---------- RULE 5 ----------
def clean_normalize_dashes(text: str) -> str:
    """
    Normalize all dash-like characters into a single ASCII hyphen '-'.

    Japanese definition:
        －／—／─ は '-' に統一。
    """
    dash_variants = ["－", "—", "─", "–", "―"]
    for d in dash_variants:
        text = text.replace(d, "-")
    return text
# -----------------------------

# ---------- RULE 6 ----------
def clean_normalize_numbered_symbols(text: str) -> str:
    """
    Normalize numbered symbols.

    - Circled numbers (①②③…) → ((1))((2))((3))…
    - Roman numerals (ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ) → I, II, III, IV, V, VI, VII, VIII, IX, X

    Japanese definition:
        ①②… は (1)(2)… に、
        ローマ数字 ⅡⅢ… は II, III… に統一（置換表で対応）。
    """

    # circled_map = {
        # "①": "((1))", "②": "((2))", "③": "((3))", "④": "((4))", "⑤": "((5))",
        # "⑥": "((6))", "⑦": "((7))", "⑧": "((8))", "⑨": "((9))", "⑩": "((10))",
        # "⑪": "((11))", "⑫": "((12))", "⑬": "((13))", "⑭": "((14))", "⑮": "((15))",
        # "⑯": "((16))", "⑰": "((17))", "⑱": "((18))", "⑲": "((19))", "⑳": "((20))",
    # }

    roman_map = {
        "Ⅰ": "I", "Ⅱ": "II", "Ⅲ": "III", "Ⅳ": "IV", "Ⅴ": "V",
        "Ⅵ": "VI", "Ⅶ": "VII", "Ⅷ": "VIII", "Ⅸ": "IX", "Ⅹ": "X",
        "Ⅺ": "XI", "Ⅻ": "XII", "Ⅼ": "L", "Ⅽ": "C", "Ⅾ": "D", "Ⅿ": "M",
    }

    # Apply both mappings
    # for k, v in circled_map.items():
        # text = text.replace(k, v)
    for k, v in roman_map.items():
        text = text.replace(k, v)

    return text
# -----------------------------

# ---------- RULE 7 ----------
def clean_remove_footers(text: str) -> str:
    """
    Remove footer lines such as:
    - "- 1 -"
    - "第1頁"
    - "Page 2", "page 3"
    Japanese definition:
        フッター（- 1 -、第1頁、Page 2 など）は破棄。
    """
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip empty line checks, process only short lines (footer-like)
        if len(stripped) <= 12:
            # Case 1: "- 1 -" or similar
            if stripped.startswith("-") and stripped.endswith("-"):
                middle = stripped.strip("- ").strip()
                if middle.isdigit():
                    continue

            # Case 2: "第1頁" or "第12頁"
            if stripped.startswith("第") and stripped.endswith("頁"):
                middle = stripped[1:-1]
                if middle.isdigit():
                    continue

            # Case 3: "Page 1" / "page 2"
            lower = stripped.lower()
            if lower.startswith("page "):
                num_part = lower.replace("page ", "").strip()
                if num_part.isdigit():
                    continue

        # Keep all non-footer lines
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
# -----------------------------

# ---------- RULE 8 ---------- ---------FIX -------------------
def clean_remove_fixed_headers(text: str) -> str:
    """
    Remove fixed page headers / titles that appear on each page.
    If uncertain, mark them with [疑いフラグ].

    Japanese definition:
        ページ先頭の局名・固定タイトルはテンプレ語一致で削除。
        自信がなければ「疑いフラグ」を付ける。
    """
    template_words = [
        "国土交通省",
        "北海道開発局",
        "東北地方整備局",
        "関東地方整備局",
        "中部地方整備局",
        "近畿地方整備局",
        "中国地方整備局",
        "四国地方整備局",
        "九州地方整備局",
        "入札説明書",
        "工事請負契約書",
        "契約書様式",
    ]

    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            cleaned_lines.append(line)
            continue

        # Exact or startswith match — confidently delete
        if any(stripped.startswith(word) for word in template_words):
            continue

        # Short uppercase or agency-like lines — uncertain
        if (
            len(stripped) <= 25
            and any(k in stripped for k in ["局", "省", "部", "課"])
            and not stripped.endswith("。")
        ):
            cleaned_lines.append("[疑いフラグ] " + line)
            continue

        # Otherwise keep line
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
# -----------------------------

# ---------- RULE 9 ---------- ----------FIX-------------------
def clean_remove_kokoku_section(text: str, file_name: str = "") -> str:
    """
    Rule 9: Remove the “Announcement” (公告) section appearing
    at the start of the file, up to just before "入札説明書",
    and log details to an audit CSV.

    English summary:
        Always exclude the announcement section (e.g., bid participation
        requirements, announcement number, etc.) before "入札説明書".
        If "入札説明書" appears later, delete everything from the first
        announcement keyword up to that heading.
        If no "入札説明書" follows, remove only a small heuristic block
        (two headings or two blank lines) after the announcement keyword.
        Logs the start/end lines and triggering keyword.
    """
    announcement_keywords = [
        "入札公告", "一般競争入札公告", "公告日", "公告番号",
        "入札参加資格", "参加申請", "指名停止",
        "公告期間", "調達ポータル", "入札情報サービス",
    ]
    target_keyword = "入札説明書"

    lines = text.splitlines()
    cleaned_lines = []
    announcement_start = None
    announcement_end = None
    found_target = False
    trigger_keyword = None
    target_index = None

    # Detect 入札説明書 position
    for i, line in enumerate(lines):
        if target_keyword in line:
            found_target = True
            target_index = i
            break

    # Detect 公告 zone before 入札説明書
    for i, line in enumerate(lines):
        if found_target and i >= target_index:
            break

        if any(k in line for k in announcement_keywords):
            announcement_start = i
            trigger_keyword = next(k for k in announcement_keywords if k in line)
            blank_count = 0
            heading_count = 0
            # Continue scanning forward for heuristic range
            for j in range(i + 1, len(lines)):
                stripped = lines[j].strip()
                if not stripped:
                    blank_count += 1
                elif stripped.endswith("：") or stripped.endswith(":") or stripped.endswith("）"):
                    heading_count += 1

                if blank_count >= 2 or heading_count >= 2:
                    announcement_end = j
                    break
            break

    # Compute removal boundaries
    if announcement_start is not None:
        if found_target and target_index is not None:
            announcement_end = target_index
        elif announcement_end is None:
            announcement_end = min(announcement_start + 10, len(lines))

        # Log to audit CSV
        export_global_audit(
            file_name=file_name,
            status="announcement_removed",
            start_keyword="入札説明書" if found_target else "",
            start_page="?",
            end_keyword=trigger_keyword,
            end_page="?",
            page_range="?–?",
        )

        # Remove section
        lines = lines[:announcement_start] + lines[announcement_end:]

    # If 公告 appears after 入札説明書 — remove small local block
    elif found_target:
        for i in range(target_index + 1, len(lines)):
            if any(k in lines[i] for k in announcement_keywords):
                trigger_keyword = next(k for k in announcement_keywords if k in lines[i])
                end_idx = min(i + 5, len(lines))
                export_announcement_audit(
                    file_name=file_name,
                    start=i,
                    end=end_idx,
                    keyword=trigger_keyword,
                    found_target=found_target,
                )
                del lines[i:end_idx]
                break

    return "\n".join(lines)

def export_announcement_audit(file_name: str, start: int, end: int, keyword: str, found_target: bool):
    """
    Log announcement-section removal details into results/announcement_audit.csv.
    """
    audit_path = BASE_DIR / "announcement_audit.csv"
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    header_needed = not audit_path.exists()
    with open(audit_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["timestamp", "file", "start_line", "end_line", "trigger_keyword", "入札説明書_found"])
        from datetime import datetime
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            file_name,
            start + 1,  # convert to 1-based line numbering
            end + 1,
            keyword or "",
            "Yes" if found_target else "No"
        ])
# -----------------------------

# ---------- RULE 10 ----------
def clean_start_from_nyusatsu_setsumeisho(text: str) -> str:
    """
    Rule 10: Start at the first “入札説明書”, preserving only the page-start marker
    line immediately before it (e.g., '[[PAGE_START N]]'), and removing all other
    content before the heading.

    Handles:
      - Normal lines: "入札説明書" or spaced variants like "入 札 説 明 書"
      - Vertical extraction: each character on its own line

    Output shape when a page-start marker is present:
        [[PAGE_START N]]
        入札説明書
        <rest of file...>

    If no page-start marker is found, behavior falls back to starting at the heading
    without adding any synthetic marker.
    """
    lines = text.splitlines()

    def is_page_start_marker(s: str) -> bool:
        s = s.strip()
        # Keep it simple and robust (no regex): matches strings like "[[PAGE_START 12]]"
        return s.startswith("[[PAGE_START ") and s.endswith("]]")

    def find_prev_page_start(idx: int) -> int:
        """Find the nearest page-start marker BEFORE index idx; return -1 if none."""
        for k in range(idx - 1, -1, -1):
            if is_page_start_marker(lines[k]):
                return k
        return -1

    # --- scan to find heading position(s) ---
    i = 0
    found = False
    heading_cut_after = -1   # index of the line AFTER the heading block to keep from
    keep_marker_idx = -1     # index of the page-start marker to preserve

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        # Case 1: Normal line or spaced variant "入 札 説 明 書"
        compressed = "".join(stripped.split())
        if compressed.startswith("入札説明書"):
            found = True
            keep_marker_idx = find_prev_page_start(i)
            heading_cut_after = i + 1  # keep normalized heading + content after it
            break

        # Case 2: Vertical layout detection (characters on separate lines)
        # Build up to 6 chars forward if each line contains exactly 1 char
        candidate = ""
        last_char_idx = -1
        if stripped and len(stripped) == 1 and stripped in "入札説明書":
            j = i
            while j < len(lines) and len(lines[j].strip()) == 1 and lines[j].strip() in "入札説明書":
                candidate += lines[j].strip()
                last_char_idx = j
                if len(candidate) >= 6:
                    break
                j += 1

            if candidate == "入札説明書":
                found = True
                keep_marker_idx = find_prev_page_start(i)
                heading_cut_after = last_char_idx + 1  # consume the full vertical block
                break

        i += 1

    if not found:
        # No heading found; return text unchanged
        return text

    # Build output:
    # - If we have a page-start marker, keep ONLY that marker before the heading.
    # - Normalize the heading line to a single "入札説明書".
    out_lines = []
    if keep_marker_idx != -1:
        out_lines.append(lines[keep_marker_idx].strip())

    out_lines.append("入札説明書")
    out_lines.extend(lines[heading_cut_after:])

    return "\n".join(out_lines)
# -----------------------------
    """
    Rule 10: Start of “入札説明書” (robust version)

    Handles both:
        - Normal line: "入札説明書" or "入 札 説 明 書"
        - Vertical extraction: each character on a separate line

    Steps:
        1. Compress spaces within lines.
        2. Detect consecutive short one-character lines forming "入札説明書".
        3. Merge them into a single "入札説明書" line.
        4. Remove all text before that line.
    """
    lines = text.splitlines()
    new_lines = []
    i = 0
    found_start = False

    while i < len(lines):
        line = lines[i].strip()
        # --- Case 1: Normal line or spaced variant ---
        compressed = "".join(line.split())
        if compressed.startswith("入札説明書"):
            found_start = True
            new_lines = ["入札説明書"] + lines[i + 1 :]
            break

        # --- Case 2: Vertical layout detection ---
        # Look ahead up to next 6 lines, each one short (1 char)
        if line in ["入", "入札", ""] or (len(line) == 1 and line in "入札説明書"):
            candidate = ""
            for j in range(i, min(i + 6, len(lines))):
                ch = lines[j].strip()
                if ch and len(ch) == 1:
                    candidate += ch
                else:
                    break

            if candidate == "入札説明書":
                found_start = True
                new_lines = ["入札説明書"] + lines[j + 1 :]
                break

        i += 1

    if found_start:
        return "\n".join(new_lines)
    else:
        return text
# -----------------------------

# ---------- RULE 11 ----------
def clean_cut_at_end_headings(text: str, file_name: str = "") -> str:
    """
    Rule 11 (exact as requested):
    After [[PAGE_START N]], skip the empty line(s), take the first 4 characters
    of the first non-empty line, and if those characters start with any of:
        "別表", "様式", "仕様書", "参考資料", "添付", "別紙"
    then remove that line and everything after it.
    """
    # Skip this rule for 86 Osaka files (to avoid trimming actual data)
    if "【86】大阪" in file_name or ("大阪" in file_name and "86" in file_name):
        return text

    end_keywords = ["別表", "様式", "仕様書", "参考資料", "添付", "別紙"]
    lines = text.splitlines()

    def is_page_start_marker(s: str) -> bool:
        t = s.strip()
        return t.startswith("[[PAGE_START ") and t.endswith("]]")

    end_index = None
    trigger_keyword = None

    i = 0
    while i < len(lines):
        if not is_page_start_marker(lines[i]):
            i += 1
            continue

        # first non-empty line after the marker (skip the blank line you insert)
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1

        if j < len(lines):
            # Heading-shape guard: do not cut if the line contains sentence punctuation
            full_line = lines[j]
            if ("。" in full_line) or ("、" in full_line):
                # treat as a continuation line; skip cutting on this page
                i = j  # advance past this checked position
                continue

            # take first 4 chars and test from the beginning
            first4 = full_line[:4]
            for kw in end_keywords:  # keep the list order as given
                if first4.startswith(kw):
                    end_index = j
                    trigger_keyword = kw
                    break
            if end_index is not None:
                break

        i = j if j > i else i + 1
        
    if end_index is not None:
        print("TRIGGER FOUND:", trigger_keyword, "at line", j)
        print("CUT PREVIEW:", lines[j-2:j+2])

    if end_index is not None:
        # keep everything up to—but not including—the trigger line
        return "\n".join(lines[:end_index])
    return text


# -----------------------------


# ---------- RULE 12 ----------
def clean_indent_headings(text: str) -> str:
    """
    Rule 12: Apply indentation and spacing based on heading levels.

    Heading token definitions:
        Level 1: 1. / (1) / I. / A.
        Level 2: (1) / ① / ② / a.
        Level 3: ア / (ア) / A) etc.

    Formatting rules:
        - Level 1: 0 full-width spaces
        - Level 2: 2 full-width spaces
        - Level 3: 4 full-width spaces
        - Insert 1–2 blank lines when switching between chapter levels.

    Japanese definition:
        第1層：1.／(1)／Ⅰ.／A.
        第2層：（1）／①②／a.
        第3層：ア／(ア)／A) など。
        各層に全角空白×Nでインデント（第1層0／第2層2／第3層4）、
        章切替時に1〜2行の空行を自動挿入。
    """

    full_space = "　"  # full-width space character (U+3000)

    def detect_level(line: str) -> int:
        stripped = line.strip()
        if not stripped:
            return 0
        # Level 1 patterns
        level1_prefixes = ("1.", "2.", "3.", "(1)", "(2)", "(3)", "I.", "II.", "III.", "A.", "B.", "C.")
        # Level 2 patterns
        level2_prefixes = ("①", "②", "③", "a.", "b.", "c.", "(1)", "(2)", "(3)")
        # Level 3 patterns
        level3_prefixes = ("ア", "イ", "ウ", "(ア)", "(イ)", "(ウ)", "A)", "B)", "C)")

        if any(stripped.startswith(p) for p in level1_prefixes):
            return 1
        if any(stripped.startswith(p) for p in level2_prefixes):
            return 2
        if any(stripped.startswith(p) for p in level3_prefixes):
            return 3
        return 0

    lines = text.splitlines()
    result = []
    last_level = 0

    for line in lines:
        current_level = detect_level(line)

        # Skip blank lines but preserve them
        if not line.strip():
            result.append(line)
            continue

        # Add blank lines when chapter level changes (e.g., from Level 1 → 2)
        if current_level != 0 and last_level != 0 and current_level <= last_level:
            # Add 1–2 blank lines before new major heading
            result.append("")
            result.append("")

        # Apply indentation
        if current_level == 1:
            indented_line = line.strip()
        elif current_level == 2:
            indented_line = f"{full_space * 2}{line.strip()}"
        elif current_level == 3:
            indented_line = f"{full_space * 4}{line.strip()}"
        else:
            indented_line = line

        result.append(indented_line)
        last_level = current_level if current_level != 0 else last_level

    return "\n".join(result)
# -----------------------------

# ---------- RULE 13 ----------
def clean_merge_point_wrapping(text: str) -> str:
    """
    Rule X: keep numbered/bulleted points on a single line.
    - Detects point headers like '1)', '(1)', 'a.', '*', '・', circled numbers, etc.
    - Joins the following wrapped lines into the same line until a blank line or a new point starts.
    """
    lines = text.splitlines()
    merged = []
    buffer = []

    no_space_before = set("、。，．,.!?;:)]）｝」』】〉》〕］>％％")
    no_space_after = set("([（｛「『【〈《〔［{<")
    bullet_prefixes = {"・", "＊", "*", "-", "―", "○", "●", "◎", "◇", "◆", "□", "■", "▲", "△"}
    circled_digits = tuple(chr(code) for code in range(9312, 9332))  # ①-⑳

    def is_point_line(raw: str) -> bool:
        stripped = raw.lstrip()
        if not stripped:
            return False
        first = stripped[0]
        if first in bullet_prefixes or first in circled_digits:
            return True
        if first.isdigit():
            if len(stripped) > 1 and stripped[1] in {")", ".", "．", "）"}:
                return True
            if len(stripped) > 2 and stripped[1] == " " and stripped[2] in {")", ".", "．", "）"}:
                return True
        if first.isalpha() and len(stripped) > 1 and stripped[1] in {")", ".", "）"}:
            return True
        if stripped.startswith("(") or stripped.startswith("（"):
            return len(stripped) > 1 and stripped[1].isdigit()
        return False

    def flush_buffer():
        if not buffer:
            return
        first_line = buffer[0]
        indent_len = len(first_line) - len(first_line.lstrip())
        indent = first_line[:indent_len]
        combined = first_line.strip()
        for part in buffer[1:]:
            piece = part.strip()
            if not piece:
                continue
            if combined.endswith(" ") or combined[-1] in no_space_after or piece[0] in no_space_before:
                combined += piece
            else:
                combined += " " + piece
        merged.append(indent + combined)
        buffer.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_buffer()
            merged.append("")
            continue
        if is_point_line(line):
            flush_buffer()
            buffer.append(line)
            continue
        if buffer:
            buffer.append(line)
        else:
            merged.append(line)

    flush_buffer()
    result = "\n".join(merged)
    if text.endswith("\n"):
        result += "\n"
    return result
# -----------------------------

# : no fixed the katakana points
def _clean_collapse_point_lines_core(text: str) -> str:
    """
    Rule X: keep every numbered / bulleted point on a single physical line.
    """
    whitespace_chars = (" ", "\t", "\u3000")
    bullet_chars = {
        "・", "･", "●", "○", "◎", "◯", "〇",
        "▲", "△", "◆", "◇", "■", "□",
        "＊", "*", "-", "―", "‐", "－", "–", "—", "※"
    }
    opening_wrappers = {"(", "（", "[", "［", "〔", "{", "｛", "〈", "《", "«"}
    closing_wrappers = {")", "）", "]", "］", "〕", "}", "｝", "〉", "》", "»"}
    sentence_terminators = {
        "。", "．", ".", "!", "！", "?", "？", "〟", "”", "’",
        "」", "』", "》", "〕", "］", "】", ")", "）", ">"
    }
    continuation_enders = {
        ",", "、", "，", ";", "；", "/", "／",
        "(", "（", "[", "［", "{", "｛", "「", "『", "“", "\"", "'"
    }
    no_space_before = {
        "、", "。", "，", "．", ",", ".", "!", "?", "！", "？",
        ";", "；", ":", "：", ")", "）", "]", "］", "}", "｝",
        "」", "』", "】", "〉", "》", "〔", "％", "%"
    }
    no_space_after = {
        "(", "（", "[", "［", "{", "｛", "「", "『", "【", "〈", "《", "〔", "<"
    }

    def reset_balance():
        return {
            "round": 0, "square": 0, "curly": 0, "angle": 0,
            "double_quote": 0, "single_quote": 0, "jp_quote": 0,
        }

    def has_open_balance(balance):
        return any(balance.values())

    def update_balance(line, balance):
        for ch in line:
            if ch in ("(", "（"):
                balance["round"] += 1
            elif ch in (")", "）"):
                balance["round"] = max(0, balance["round"] - 1)
            elif ch in ("[", "［", "〔"):
                balance["square"] += 1
            elif ch in ("]", "］", "〕"):
                balance["square"] = max(0, balance["square"] - 1)
            elif ch in ("{", "｛"):
                balance["curly"] += 1
            elif ch in ("}", "｝"):
                balance["curly"] = max(0, balance["curly"] - 1)
            elif ch in ("〈", "《"):
                balance["angle"] += 1
            elif ch in ("〉", "》"):
                balance["angle"] = max(0, balance["angle"] - 1)
            elif ch == "\"":
                balance["double_quote"] = 1 - balance["double_quote"]
            elif ch == "“":
                balance["double_quote"] = 1
            elif ch == "”":
                balance["double_quote"] = 0
            elif ch == "'":
                balance["single_quote"] = 1 - balance["single_quote"]
            elif ch == "「":
                balance["jp_quote"] += 1
            elif ch == "」":
                balance["jp_quote"] = max(0, balance["jp_quote"] - 1)

    def is_digit_char(ch): return "0" <= ch <= "9"
    def is_alpha_upper(ch): return "A" <= ch <= "Z"
    def is_alpha_lower(ch): return "a" <= ch <= "z"
    def is_katakana(ch): return "ァ" <= ch <= "ヶ" or "ｦ" <= ch <= "ﾟ"
    def is_roman_numeral(ch): return "\u2160" <= ch <= "\u217f"

    def roman_to_int(token):
        roman_map = {
            "I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000,
            "Ⅰ": 1, "Ⅴ": 5, "Ⅹ": 10, "Ⅼ": 50, "Ⅽ": 100, "Ⅾ": 500, "Ⅿ": 1000,
            "ⅰ": 1, "ⅴ": 5, "ⅹ": 10, "ⅼ": 50, "ⅽ": 100, "ⅾ": 500, "ⅿ": 1000,
        }
        total = prev = 0
        for ch in reversed(token):
            val = roman_map.get(ch)
            if val is None:
                return None
            if val < prev:
                total -= val
            else:
                total += val
                prev = val
        return total if total > 0 else None

    KATA_SEQUENCE = list("アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン")
    KATA_INDEX = {ch: i + 1 for i, ch in enumerate(KATA_SEQUENCE)}

    _DAKUTEN_BASE_MAP = {
        # dakuten
        "ガ": "カ", "ギ": "キ", "グ": "ク", "ゲ": "ケ", "ゴ": "コ",
        "ザ": "サ", "ジ": "シ", "ズ": "ス", "ゼ": "セ", "ゾ": "ソ",
        "ダ": "タ", "ヂ": "チ", "ヅ": "ツ", "デ": "テ", "ド": "ト",
        "バ": "ハ", "ビ": "ヒ", "ブ": "フ", "ベ": "ヘ", "ボ": "ホ",
        # handakuten
        "パ": "ハ", "ピ": "ヒ", "プ": "フ", "ペ": "ヘ", "ポ": "ホ",
        # ヴ
        "ヴ": "ウ",
    }

    def katakana_to_index(kana: str):
        if not kana:
            return None
        # normalize to NFKC just in case
        ch = unicodedata.normalize("NFKC", kana[0])
        # fold dakuten/handakuten to base row for ordering
        ch = _DAKUTEN_BASE_MAP.get(ch, ch)
        return KATA_INDEX.get(ch)

    def detect_point(line):
        n = len(line)
        idx = 0
        while idx < n and line[idx] in whitespace_chars:
            idx += 1
        indent = line[:idx]
        if idx >= n:
            return None

        ch = line[idx]
        # Treat U+FF65 halfwidth middle dot '･' as a bullet at line start
        if ch in bullet_chars or ch == "･":
            marker_end = idx + 1
            while marker_end < n and line[marker_end] in whitespace_chars:
                marker_end += 1
            rest = line[marker_end:].lstrip("".join(whitespace_chars))
            return {
                "indent": indent,
                "depth": 0,
                "kind": "symbol",
                "numeric": None,
                "marker": line[idx:marker_end],
                "rest": rest,
            }

        depth = 0
        opener_end = idx
        while opener_end < n and line[opener_end] in opening_wrappers:
            depth += 1
            opener_end += 1

        core_start = opener_end
        if core_start >= n:
            return None

        core = ""
        kind = None
        numeric = None
        pos = core_start

        circled_ord = ord(line[pos])
        if 0x2460 <= circled_ord <= 0x2473:
            core = line[pos]
            kind = "circled"
            numeric = circled_ord - 0x2460 + 1
            pos += 1
        else:
            token_chars = []
            while pos < n:
                ch = line[pos]
                if is_digit_char(ch):
                    if kind in (None, "digit"):
                        kind = "digit"
                        token_chars.append(ch)
                        pos += 1
                        continue
                    break
                if is_alpha_upper(ch):
                    if kind in (None, "alpha-upper"):
                        kind = "alpha-upper"
                        token_chars.append(ch)
                        pos += 1
                        continue
                    break
                if is_alpha_lower(ch):
                    if kind in (None, "alpha-lower"):
                        kind = "alpha-lower"
                        token_chars.append(ch)
                        pos += 1
                        continue
                    break
                if is_katakana(ch):
                    if kind in (None, "katakana"):
                        kind = "katakana"
                        token_chars.append(ch)
                        pos += 1
                        continue
                    break
                if is_roman_numeral(ch):
                    if kind in (None, "roman"):
                        kind = "roman"
                        token_chars.append(ch)
                        pos += 1
                        continue
                    break
                break

            if not token_chars:
                return None

            core = "".join(token_chars)
            if kind == "digit":
                numeric = int(core)
            elif kind == "alpha-upper" and len(core) == 1:
                numeric = ord(core) - ord("A") + 1
            elif kind == "alpha-lower" and len(core) == 1:
                numeric = ord(core) - ord("a") + 1
            elif kind == "roman":
                numeric = roman_to_int(core)
            elif kind == "katakana" and len(core) == 1:
                numeric = katakana_to_index(core)

        close_start = pos
        while pos < n and line[pos] in closing_wrappers:
            pos += 1

        if pos == close_start:
            if pos < n and line[pos] in (".", "．"):
                pos += 1
            elif depth == 0 and kind not in ("symbol", "circled"):
                return None

        marker = line[idx:pos]
        rest = line[pos:].lstrip("".join(whitespace_chars))
        return {
            "indent": indent,
            "depth": depth,
            "kind": kind,
            "numeric": numeric,
            "marker": marker,
            "rest": rest,
        }

    def rest_starts_clean(token):
        rest = token["rest"]
        if not rest:
            return True
        first = rest[0]
        if first in closing_wrappers:
            return False
        if first in (",", "、", "，", ".", "。", "．", ":", "：", ")", "）", "】", "」", "』"):
            return False
        return True

    def allows_new_point(prev_line):
        trimmed = prev_line.rstrip()
        if not trimmed:
            return True
        tail = trimmed[-1]
        if tail in continuation_enders:
            return False
        return True

    # def join_buffer(buffer_lines):
    #     """
    #     Join physical lines belonging to the same point.

    #     - If the point header looks like a 'label' (公告日, 契約担当官等, 工事名, ...),
    #       we ALWAYS put a space between the label line and the first value line.
    #     - For all other joins, we avoid inserting a space between CJK–CJK
    #       (to prevent '入 札', 'に ついて').
    #     """
    #     if not buffer_lines:
    #         return ""

    #     merged_line = buffer_lines[0].strip()
    #     is_label_point = _is_label_like_point(buffer_lines[0])

    #     for idx, piece in enumerate(buffer_lines[1:], start=1):
    #         chunk = piece.strip()
    #         if not chunk:
    #             continue

    #         need_space = False
    #         if merged_line and merged_line[-1] not in no_space_after and chunk[0] not in no_space_before:
    #             if is_label_point and idx == 1:
    #                 # First continuation after a label-like header: always separate
    #                 need_space = True
    #             else:
    #                 # Normal continuation: avoid CJK–CJK spaces
    #                 if not (_is_cjk(merged_line[-1]) and _is_cjk(chunk[0])):
    #                     need_space = True

    #         if need_space:
    #             merged_line += " "
    #         merged_line += chunk

    #     return merged_line

    def join_buffer(buffer_lines):
        """
        Join physical lines belonging to the same point.
        """
        if not buffer_lines:
            return ""

        # Find the first line that looks like a label (even if it's not the first physical line)
        label_idx = None
        for i, ln in enumerate(buffer_lines):
            if _is_label_like_point(ln):
                label_idx = i
                break
        is_label_point = label_idx is not None

        merged_line = buffer_lines[0].strip()

        for idx, piece in enumerate(buffer_lines[1:], start=1):
            chunk = piece.strip()
            if not chunk:
                continue

            need_space = False
            if merged_line and merged_line[-1] not in no_space_after and chunk[0] not in no_space_before:
                # Force a space before the label itself and the first value line after the label
                if is_label_point and (idx == label_idx or idx == label_idx + 1):
                    need_space = True
                else:
                    if not (_is_cjk(merged_line[-1]) and _is_cjk(chunk[0])):
                        need_space = True

            if need_space:
                merged_line += " "
            merged_line += chunk

        return merged_line


    lines = text.splitlines()
    ends_with_newline = text.endswith("\n")
    merged_output = []

    current_buffer = []
    current_token = None
    current_balance = reset_balance()

    def flush_current():
        nonlocal current_buffer, current_token, current_balance
        if current_buffer:
            merged_output.append(join_buffer(current_buffer))
        current_buffer = []
        current_token = None
        current_balance = reset_balance()

    for raw_line in lines:
        stripped_line = raw_line.strip()
        # Hard boundaries: never merge across page/table/heading markers or heading lines
        if (
            stripped_line.startswith("[[PAGE_START")
            or stripped_line.startswith("[[PAGE_END")
            or stripped_line.startswith("[[TABLE_START")
            or stripped_line == "[[TABLE_END]]"
            or stripped_line.startswith("[[HEADING]]")
            or stripped_line == "入札説明書"
            or stripped_line.startswith("入札説明書")
        ):
            flush_current()
            merged_output.append(raw_line)
            continue

        if not stripped_line:
            flush_current()
            merged_output.append("")
            continue

        token = detect_point(raw_line)

        if token and rest_starts_clean(token):
            if current_token is None:
                current_buffer = [raw_line]
                current_token = token
                current_balance = reset_balance()
                update_balance(raw_line, current_balance)
                continue

            if has_open_balance(current_balance):
                current_buffer.append(raw_line)
                update_balance(raw_line, current_balance)
                continue

            if token["depth"] != current_token["depth"]:
                flush_current()
                current_buffer = [raw_line]
                current_token = token
                current_balance = reset_balance()
                update_balance(raw_line, current_balance)
                continue

            if current_token["kind"] != token["kind"]:
                flush_current()
                current_buffer = [raw_line]
                current_token = token
                current_balance = reset_balance()
                update_balance(raw_line, current_balance)
                continue

            if allows_new_point(current_buffer[-1]):
                if current_token["numeric"] is not None and token["numeric"] is not None:
                    expected = current_token["numeric"] + 1
                    if token["numeric"] == expected or token["numeric"] == 1:
                        flush_current()
                        current_buffer = [raw_line]
                        current_token = token
                        current_balance = reset_balance()
                        update_balance(raw_line, current_balance)
                        continue
                    else:
                        current_buffer.append(raw_line)
                        update_balance(raw_line, current_balance)
                        continue
                else:
                    flush_current()
                    current_buffer = [raw_line]
                    current_token = token
                    current_balance = reset_balance()
                    update_balance(raw_line, current_balance)
                    continue

            current_buffer.append(raw_line)
            update_balance(raw_line, current_balance)

        else:
            if current_token is not None:
                current_buffer.append(raw_line)
                update_balance(raw_line, current_balance)
            else:
                merged_output.append(raw_line)

    flush_current()
    result = "\n".join(merged_output)
    if ends_with_newline:
        result += "\n"
    return result


def clean_collapse_point_lines(text: str) -> str:
    """Wrapper that preserves table blocks before collapsing bullet lines."""
    return _apply_preserving_tables(text, _clean_collapse_point_lines_core)

def clean_fix_common_split_words(text: str) -> str:
    """
    Fix some very common bad splits that still slip through.
    """
    replacements = {
        "入 札": "入札",
        "に ついて": "について",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def _clean_collapse_paragraph_lines_core(text: str) -> str:
    """
    Merge wrapped paragraph lines into a single physical line while keeping list points intact.
    """
    bullet_symbols = {
        "-", "*", "・", "•", "●", "○", "◎", "▲",
        "△", "◆", "◇", "■", "□", "▪", "▫",
        "◦", "◯", "※", "★", "☆", "▶", "▷",
    }
    sentence_enders = {
        ".", "!", "?", "。", "．", "！", "？", "」", "』",
        "）", "］", "｝", "〗", "〙", "〉", "》", "〛", "〟", ">", "»", "〉",
    }
    no_space_after = {
        "(", "[", "{", "<", "（", "［", "｛", "「", "『", "〈", "《", "«",
    }
    no_space_before = {
        ",", ".", "!", "?", ":", ";", "%", "、", "。", "，", "．",
        "！", "？", "：", "；", "％", "）", "］", "｝", "」", "』",
        "〗", "〙", "〉", "》", "〛", "〟", "»", "〉",
    }
    roman_chars = set("IVXLCDMivxlcdm")

    def reset_balance():
        return {
            "round": 0,
            "square": 0,
            "curly": 0,
            "angle": 0,
            "double_quote": 0,
            "single_quote": 0,
            "jp_quote": 0,
        }

    def has_open_balance(balance):
        return any(balance.values())

    def update_balance(line, balance):
        for ch in line:
            if ch in ("(", "（"):
                balance["round"] += 1
            elif ch in (")", "）"):
                balance["round"] = max(0, balance["round"] - 1)
            elif ch in ("[", "［"):
                balance["square"] += 1
            elif ch in ("]", "］"):
                balance["square"] = max(0, balance["square"] - 1)
            elif ch in ("{", "｛"):
                balance["curly"] += 1
            elif ch in ("}", "｝"):
                balance["curly"] = max(0, balance["curly"] - 1)
            elif ch in ("〈", "《", "«"):
                balance["angle"] += 1
            elif ch in ("〉", "》", "»"):
                balance["angle"] = max(0, balance["angle"] - 1)
            elif ch in ('"', "“", "”"):
                balance["double_quote"] = 1 - balance["double_quote"]
            elif ch in ("'", "‘", "’"):
                balance["single_quote"] = 1 - balance["single_quote"]
            elif ch in ("「", "『"):
                balance["jp_quote"] += 1
            elif ch in ("」", "』"):
                balance["jp_quote"] = max(0, balance["jp_quote"] - 1)

    def join_group(buffer_lines):
        """
        Join physical lines of a normal paragraph.

        - Same spacing rules as for points, but without label/value special-case.
        - Default: DO NOT insert a space between CJK–CJK joins.
        """
        if not buffer_lines:
            return ""

        merged = buffer_lines[0].strip()
        for piece in buffer_lines[1:]:
            chunk = piece.strip()
            if not chunk:
                continue

            need_space = False
            if (
                merged
                and merged[-1] not in no_space_after
                and chunk[0] not in no_space_before
            ):
                # Only add a space if it's NOT CJK–CJK.
                if not (_is_cjk(merged[-1]) and _is_cjk(chunk[0])):
                    need_space = True

            if need_space:
                merged += " "
            merged += chunk

        return merged

    

    def is_probable_point_line(line: str) -> bool:
        stripped = line.lstrip()
        if not stripped:
            return False
        # Treat halfwidth middle dot at line start as a bullet point
        if stripped[0] == "･":
            return True
        if stripped.startswith("[[PAGE_") or stripped.startswith("[[PAGE "):
            return True
        if stripped.startswith("[[PAGE_END"):
            return True
        s2 = stripped.strip()
        if s2.startswith("[[HEADING]]"):
            return True
        if "".join(s2.split()).startswith("入札説明書"):
            return True
        if stripped[0] in ("【", "□"):
            return True
        first = stripped[0]
        if first in bullet_symbols or "①" <= first <= "⑳":
            return True

        idx = 0
        while idx < len(stripped) and stripped[idx] in (
            "(", "[", "{", "<", "（", "［", "｛", "〈", "《", "「", "『", "«"
        ):
            idx += 1

        if idx >= len(stripped):
            return False

        if stripped.startswith("第") and ("章" in stripped[:6] or "節" in stripped[:6] or "項" in stripped[:6]):
            return True

        ch = stripped[idx]

        if "0" <= ch <= "9":
            digit_idx = idx + 1
            while digit_idx < len(stripped) and "0" <= stripped[digit_idx] <= "9":
                digit_idx += 1
            if digit_idx < len(stripped) and stripped[digit_idx] in (".", ")", "）", "．"):
                return True
            if digit_idx < len(stripped) and stripped[digit_idx] in (" ", "　"):
                return True

        if ch in roman_chars:
            roman_idx = idx + 1
            while roman_idx < len(stripped) and stripped[roman_idx] in roman_chars:
                roman_idx += 1
            if roman_idx < len(stripped) and stripped[roman_idx] in (".", ")", "）"):
                return True

        if "A" <= ch <= "Z" or "a" <= ch <= "z":
            alpha_idx = idx + 1
            while alpha_idx < len(stripped) and (
                "A" <= stripped[alpha_idx] <= "Z" or "a" <= stripped[alpha_idx] <= "z"
            ):
                alpha_idx += 1
            if alpha_idx < len(stripped) and stripped[alpha_idx] in (".", ")", "）"):
                return True
            if alpha_idx < len(stripped) and stripped[alpha_idx] in (" ", "　"):
                return True

        if "ァ" <= ch <= "ヶ":
            kana_idx = idx + 1
            if kana_idx < len(stripped) and stripped[kana_idx] in (")", "）", ".", "．"):
                return True
            if kana_idx < len(stripped) and stripped[kana_idx] in (" ", "　"):
                return True
            if kana_idx == len(stripped):
                return True

        return False

    lines = text.splitlines()
    ends_with_newline = text.endswith("\n")
    result = []

    paragraph_buffer = []
    paragraph_balance = reset_balance()

    def flush_paragraph():
        nonlocal paragraph_buffer, paragraph_balance
        if paragraph_buffer:
            result.append(join_group(paragraph_buffer))
        paragraph_buffer = []
        paragraph_balance = reset_balance()

    for raw_line in lines:
        stripped = raw_line.strip()

        if not stripped:
            flush_paragraph()
            result.append("")
            continue

        if is_probable_point_line(raw_line):
            flush_paragraph()
            result.append(raw_line)
            continue

        if not paragraph_buffer:
            paragraph_buffer = [raw_line]
            update_balance(raw_line, paragraph_balance)
            continue

        previous = paragraph_buffer[-1].rstrip()
        tail = previous[-1] if previous else ""

        if has_open_balance(paragraph_balance) or (tail and tail not in sentence_enders):
            paragraph_buffer.append(raw_line)
            update_balance(raw_line, paragraph_balance)
        else:
            flush_paragraph()
            paragraph_buffer = [raw_line]
            update_balance(raw_line, paragraph_balance)

    flush_paragraph()
    merged_text = "\n".join(result)
    if ends_with_newline:
        merged_text += "\n"
    return merged_text


def clean_collapse_paragraph_lines(text: str) -> str:
    """Wrapper that preserves table blocks before collapsing paragraph lines."""
    return _apply_preserving_tables(text, _clean_collapse_paragraph_lines_core)


def clean_start_from_heading2(text: str) -> str:
    """
    Start the document at the true '入札説明書' heading.

    Preference order:
      1) A line equal to 入札説明書 whose previous non-empty line is a generic heading marker '[[HEADING]]'.
      2) Exact line match 入札説明書 (no prefix like '入札説明書等').
      3) Vertical stacked characters forming 入札説明書.

    Always keep only the page-start marker immediately before the heading,
    then emit a normalized '入札説明書' line followed by the rest of the file.
    """
    lines = text.splitlines()

    def is_page_start_marker(s: str) -> bool:
        t = s.strip()
        return t.startswith("[[PAGE_START ") and t.endswith("]]")

    def find_prev_page_start(idx: int) -> int:
        for k in range(idx - 1, -1, -1):
            if is_page_start_marker(lines[k]):
                return k
        return -1

    def prev_non_empty(idx: int) -> int:
        k = idx - 1
        while k >= 0 and lines[k].strip() == "":
            k -= 1
        return k

    def try_vertical_from(start_idx: int) -> int:
        candidate = ""
        last = start_idx
        j = start_idx
        while j < len(lines) and len(lines[j].strip()) == 1 and lines[j].strip() in "入札説明書":
            candidate += lines[j].strip()
            last = j
            if len(candidate) >= 6:
                break
            j += 1
        if candidate == "入札説明書":
            return last + 1
        return -1

    # 1c) Stacked marker lines: multiple lines like
    #     "[[HEADING]] 入" / "[[HEADING]] 札" / "[[HEADING]] 説" / "[[HEADING]] 明" / "[[HEADING]] 書"
    #     Normalize to a single heading line "入札説明書".
    j = 0
    while j < len(lines):
        s = lines[j].strip()
        if s.startswith("[[HEADING]]"):
            after = s[len("[[HEADING]]"):].strip()
            # Start only if the first unit looks like a single target character
            if len(after) == 1 and after in "入札説明書":
                candidate = ""
                last = j
                k = j
                while k < len(lines):
                    t = lines[k].strip()
                    if t.startswith("[[HEADING]]"):
                        ch = t[len("[[HEADING]]"):].strip()
                        if len(ch) == 1 and ch in "入札説明書":
                            candidate += ch
                            last = k
                            if len(candidate) >= 6:
                                break
                            k += 1
                            continue
                    break
                if candidate == "入札説明書":
                    keep_idx = find_prev_page_start(j)
                    out = []
                    if keep_idx != -1:
                        out.append(lines[keep_idx].strip())
                    out.append("入札説明書")
                    out.extend(lines[last + 1 :])
                    return "\n".join(out)
        j += 1

    # 1) Marker-based exact heading (inline or previous-line marker)
    # 1a) Inline marker: accept "[[HEADING]] 入札説明書" and variants like "[[HEADING]] 入札説明書(個別事項)"
    for j in range(len(lines)):
        s = lines[j].strip()
        if not s:
            continue
        if s.startswith("[[HEADING]]"):
            after = s[len("[[HEADING]]"):].strip()
            compressed = "".join(after.split())
            # Only treat short, title-like patterns as the main heading
            if (
                compressed == "入札説明書"
                or compressed.startswith("入札説明書(")
                or compressed.startswith("入札説明書（")
            ):
                keep_idx = find_prev_page_start(j)
                out = []
                if keep_idx != -1:
                    out.append(lines[keep_idx].strip())
                # keep the full heading text (drop marker), e.g., 入札説明書(個別事項)
                out.append(after)
                out.extend(lines[j + 1 :])
                return "\n".join(out)

    # 1b) Previous-line marker: marker on its own line directly above heading
    for j in range(len(lines)):
        s = lines[j].strip()
        if not s:
            continue
        compressed = "".join(s.split())
        if (
            compressed == "入札説明書"
            or compressed.startswith("入札説明書(")
            or compressed.startswith("入札説明書（")
        ):
            k = prev_non_empty(j)
            if k >= 0 and lines[k].strip().startswith("[[HEADING]]"):
                keep_idx = find_prev_page_start(j)
                out = []
                if keep_idx != -1:
                    out.append(lines[keep_idx].strip())
                # keep the full heading line as-is (contains any suffix like (個別事項))
                out.append(s)
                out.extend(lines[j + 1 :])
                return "\n".join(out)

    

    # 2) Exact line match
    for j in range(len(lines)):
        s = lines[j].strip()
        if "".join(s.split()) == "入札説明書":
            keep_idx = find_prev_page_start(j)
            out = []
            if keep_idx != -1:
                out.append(lines[keep_idx].strip())
            out.append("入札説明書")
            out.extend(lines[j + 1 :])
            return "\n".join(out)

    # 3) Vertical stacked fallback
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s and len(s) == 1 and s in "入札説明書":
            cut_after = try_vertical_from(i)
            if cut_after != -1:
                keep_idx = find_prev_page_start(i)
                out = []
                if keep_idx != -1:
                    out.append(lines[keep_idx].strip())
                out.append("入札説明書")
                out.extend(lines[cut_after:])
                return "\n".join(out)
        i += 1

    return text


def clean_process_footnotes(text: str) -> str:
    """
    Process footnotes with the following rules:

    Detection:
    - Any line starting with "※", "注）", or "注)" is a footnote.
    - Inside tables (between [[TABLE_START ...]] and [[TABLE_END]]), rows that
      start with those markers, or contain the word "CORINS" (case-insensitive),
      are treated as table footnotes and moved to the bottom section.

    Formatting:
    - Prefix each footnote with "【注】" and a space.
    - Ensure one blank line before and after each footnote paragraph so it stands
      as an independent block.

    Behavior:
    - Footnotes found outside tables are formatted in place with the spacing.
    - Footnotes detected inside tables are removed from the table and appended as
      a separate section at the end of the document.
    - If table footnote rows are removed and the table header contains a rows=K
      field, K is reduced accordingly.
    """
    def line_is_footnote(raw: str) -> bool:
        s = raw.lstrip()
        return s.startswith("※") or s.startswith("注）") or s.startswith("注)")

    def format_footnote(raw: str) -> str:
        s = raw.lstrip()
        if s.startswith("※"):
            body = s[1:].strip()
        elif s.startswith("注）"):
            body = s[2:].strip()
        elif s.startswith("注)"):
            body = s[2:].strip()
        elif s.startswith("【注】"):
            body = s[len("【注】"):].strip()
        else:
            body = s
        return f"【注】 {body}" if body else "【注】"

    def parse_table_header(line: str) -> dict:
        meta = {}
        if not line.startswith("[[TABLE_START "):
            return meta
        inner = line[len("[[TABLE_START "):-2]
        for token in inner.split():
            if "=" in token:
                key, value = token.split("=", 1)
                meta[key.strip()] = value.strip()
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

    lines = text.splitlines()
    out_lines = []
    collected_footnotes = []

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # Table handling: remove footnote-like rows and collect them
        if line.startswith("[[TABLE_START "):
            header = line
            meta = parse_table_header(header)
            removed = 0
            out_lines.append(header)  # temporarily; may be replaced if rows updated
            i += 1
            body_start_idx = len(out_lines)

            while i < n and not lines[i].startswith("[[TABLE_END"):
                row = lines[i]
                row_stripped = row.lstrip()
                is_table_fn = (
                    row_stripped.startswith("※")
                    or row_stripped.startswith("注）")
                    or row_stripped.startswith("注)")
                    or ("corins" in row.lower())
                )
                if is_table_fn:
                    collected_footnotes.append(format_footnote(row))
                    removed += 1
                    i += 1
                    continue
                out_lines.append(row)
                i += 1

            # close table
            if i < n and lines[i].startswith("[[TABLE_END"):
                out_lines.append(lines[i])
                i += 1

            # If rows removed, try to update header rows count at its out_lines index
            if removed and "rows" in meta:
                try:
                    new_rows = max(0, int(meta["rows"]) - removed)
                    meta["rows"] = str(new_rows)
                    out_lines[body_start_idx - 1] = build_table_header(meta)
                except ValueError:
                    pass
            continue

        # Non-table lines
        if line_is_footnote(line):
            # Ensure blank line before
            if out_lines and out_lines[-1].strip() != "":
                out_lines.append("")
            out_lines.append(format_footnote(line))
            # Ensure blank line after
            out_lines.append("")
            i += 1
            continue

        out_lines.append(line)
        i += 1

    # Append collected table footnotes at the bottom as a separate section
    if collected_footnotes:
        if out_lines and out_lines[-1].strip() != "":
            out_lines.append("")
        for fn in collected_footnotes:
            out_lines.append(fn)
            out_lines.append("")

    result = "\n".join(out_lines)
    if text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result
def clean_merge_cross_page_tables(text: str) -> str:
    """
    Merge multi-page tables so each table appears entirely on the page where it
    starts.

    Detection and behavior:
    - If a page ends with a table ("[[TABLE_END]]") and the next page begins
      with a table ("[[TABLE_START …]]") with the same column count, and there
      is no non-table text between these blocks (blank lines allowed), append
      the next page's rows to the previous page's last table.
    - Update the "rows=" value in the original table header to reflect the
      appended rows.
    - Remove the moved table block from the later page while preserving any
      non-table text that may follow on that page.
    - Processes from the end backwards so chains over multiple pages (A→B→C…)
      roll up into the first page where the table started.
    """
    def parse_table_header(line: str):
        if not line.startswith("[[TABLE_START "):
            return {}
        inner = line[len("[[TABLE_START "):-2]
        info = {}
        for token in inner.split():
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in ("page", "index", "rows", "cols"):
                try:
                    info[key] = int(value)
                except ValueError:
                    info[key] = value
            else:
                info[key] = value
        return info

    def build_table_header(meta):
        return "[[TABLE_START page={page} index={index} rows={rows} cols={cols}]]".format(
            page=meta.get("page", ""),
            index=meta.get("index", ""),
            rows=meta.get("rows", ""),
            cols=meta.get("cols", "")
        )

    def build_segments(lines):
        segments = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("[[TABLE_START "):
                table_lines = [line]
                i += 1
                while i < len(lines):
                    table_lines.append(lines[i])
                    if lines[i].startswith("[[TABLE_END"):
                        i += 1
                        break
                    i += 1
                segments.append({"type": "table", "lines": table_lines})
            else:
                block = [line]
                i += 1
                while i < len(lines) and not lines[i].startswith("[[TABLE_START "):
                    block.append(lines[i])
                    i += 1
                segments.append({"type": "text", "lines": block})
        return segments

    def is_blank_segment(segment):
        if segment["type"] != "text":
            return False
        return all(line.strip() == "" for line in segment["lines"])

    def flatten_segments(segments):
        flattened = []
        for segment in segments:
            flattened.extend(segment["lines"])
        return flattened

    def find_last_table_segment(segments):
        idx = len(segments) - 1
        while idx >= 0 and is_blank_segment(segments[idx]):
            idx -= 1
        if idx >= 0 and segments[idx]["type"] == "table":
            return idx
        return None

    def find_first_table_segment(segments):
        idx = 0
        while idx < len(segments) and is_blank_segment(segments[idx]):
            idx += 1
        if idx < len(segments) and segments[idx]["type"] == "table":
            return idx
        return None

    def merge_pages(page_a, page_b):
        segments_a = build_segments(page_a["body"])
        segments_b = build_segments(page_b["body"])

        last_table_idx = find_last_table_segment(segments_a)
        if last_table_idx is None:
            return False

        first_table_idx = find_first_table_segment(segments_b)
        if first_table_idx is None:
            return False

        # Ensure trailing/leading segments are blank only
        for seg in segments_a[last_table_idx + 1:]:
            if not is_blank_segment(seg):
                return False
        for seg in segments_b[:first_table_idx]:
            if not is_blank_segment(seg):
                return False

        table_a = segments_a[last_table_idx]["lines"]
        table_b = segments_b[first_table_idx]["lines"]
        meta_a = parse_table_header(table_a[0])
        meta_b = parse_table_header(table_b[0])
        if not meta_a or not meta_b:
            return False
        if meta_a.get("cols") != meta_b.get("cols"):
            return False

        rows_a = meta_a.get("rows", max(len(table_a) - 2, 0))
        rows_b = meta_b.get("rows", max(len(table_b) - 2, 0))
        meta_a["rows"] = rows_a + rows_b

        merged_table = table_a[:-1] + table_b[1:-1] + [table_a[-1]]
        merged_table[0] = build_table_header(meta_a)
        segments_a[last_table_idx]["lines"] = merged_table

        segments_b.pop(first_table_idx)

        page_a["body"] = flatten_segments(segments_a)
        page_b["body"] = flatten_segments(segments_b)
        return True

    lines = text.splitlines()
    ends_with_newline = text.endswith("\n")

    pages = []
    prelude = []
    postlude = []
    current_page = None

    for line in lines:
        if line.startswith("[[PAGE_START "):
            number_part = line[len("[[PAGE_START "):-2]
            try:
                page_number = int(number_part)
            except ValueError:
                page_number = None
            current_page = {"number": page_number, "start": line, "body": [], "end": None}
            pages.append(current_page)
            continue

        if line.startswith("[[PAGE_END"):
            if current_page is not None:
                current_page["end"] = line
                current_page = None
            else:
                postlude.append(line)
            continue

        if current_page is None:
            if pages:
                postlude.append(line)
            else:
                prelude.append(line)
        else:
            current_page["body"].append(line)

    # Merge from the end backwards so multi-page chains (A->B->C...) fully
    # roll up into the page where the table started (A).
    for idx in range(len(pages) - 2, -1, -1):
        while merge_pages(pages[idx], pages[idx + 1]):
            continue

    output_lines = []
    output_lines.extend(prelude)
    for page in pages:
        if page["start"]:
            output_lines.append(page["start"])
        output_lines.extend(page["body"])
        if page["end"]:
            output_lines.append(page["end"])
    output_lines.extend(postlude)

    result = "\n".join(output_lines)
    if ends_with_newline:
        result += "\n"
    return result


# ---------- CLEANING PIPELINE ----------
def apply_cleaning_pipeline(text: str, file_name: str = "") -> str:
    """
    Apply all cleaning steps in sequence.
    Each step is a separate function for modularity.
    """
    cleaning_steps = [
        clean_normalize_numbered_symbols,   # Rule 6
        clean_fullwidth_to_halfwidth,   # Rule 1
        clean_fullwidth_space,   # Rule 2
        clean_compress_spaces,   # Rule 3
        clean_space_around_units,   # Rule 4
        clean_normalize_dashes,   # Rule 5
        clean_remove_footers,   # Rule 7
        # clean_remove_fixed_headers,   # Rule 8
        # clean_remove_kokoku_section,   # Rule 9
        clean_start_from_heading2,  #  Rule 10 (uses heading markers and exact match)
        clean_cut_at_end_headings,  #  Rule 11
        # clean_indent_headings,


        # extra rules - added by me:
        # clean_merge_point_wrapping
        # Merge multi-page tables before collapsing lines
        # clean_merge_cross_page_tables,
        # Collapse line-wrapped points and paragraphs (tables preserved)
        clean_collapse_point_lines,
        clean_collapse_paragraph_lines,
        # Footnotes formatting and relocation
        # clean_process_footnotes,
        clean_fix_common_split_words
    ]

    for func in cleaning_steps:
        try:
            if func.__name__ in ["clean_remove_kokoku_section", "clean_cut_at_end_headings"]:
                text = func(text, file_name)
            else:
                text = func(text)
        except Exception as e:
            log(f"❌ Error in {func.__name__}: {e}")
    return text
# --------------------------------------



# ---------- UTILITIES ----------
def log(message: str):
    """Append a message to the cleaning log file."""
    OUTPUT_DIR.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")


def save_cleaned_text(output_path: Path, text: str):
    """Save cleaned text file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
# ---------------------------------


# ---------- MAIN PROCESS ----------
def process_text_files(input_dir: Path, output_dir: Path):
    """Read text files from input_dir, clean them, and save to output_dir."""
    text_files = list(input_dir.rglob("*.txt"))
    if not text_files:
        print(f"No text files found in: {input_dir}")
        return

    log(f"Started cleaning {len(text_files)} files.")

    for txt_path in text_files:
        relative_path = txt_path.relative_to(input_dir)
        output_path = output_dir / relative_path

        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()

            cleaned_text = apply_cleaning_pipeline(text, file_name=str(relative_path))
            save_cleaned_text(output_path, cleaned_text)

            print(f"✅ Cleaned: {txt_path}")
            log(f"OK - {relative_path}")
        except Exception as e:
            print(f"❌ Failed: {txt_path} ({e})")
            log(f"FAIL - {relative_path} ({e})")

    log("Cleaning complete.\n")
    export_rules_status()
    print("\nAll cleaned files saved in:", output_dir)
# ----------------------------------

# ---------- RULE STATUS EXPORT ----------

def export_rules_status():
    """Generate or update CSV listing all cleaning rules and their implementation status."""
    rules_status = [
        ["Rule No.", "Rule Name / Description (English)", "Japanese Definition (Summary)", "Implemented"],
        [1, "Convert full-width characters to half-width (including punctuation and symbols)", "全角英数字・記号を半角に統一。", True],
        [2, "Replace full-width spaces (　) with half-width spaces ( )", "全角スペースを半角スペースに置換。", True],
        [3, "Compress consecutive spaces but preserve line breaks", "連続スペースを1つに圧縮（改行保持）。", True],
        [4, "Remove unnecessary spaces before/after dates and units (年, 月, 日, 円, ％, etc.)", "「年／月／日」や単位（円、％等）の前後の空白を削除。", True],
        [5, "Normalize dash characters (－／—／─／–／― → '-')", "－／—／─ は「-」に統一。", True],
        [6, "Normalize numbered symbols — circled numbers (①②…) → (1)(2)… and Roman numerals (ⅡⅢⅣ…) → II, III, IV…", "①②… は (1)(2)… に、ローマ数字ⅡⅢ… は II, III… に統一。", True],
        [7, "Remove footers such as '- 1 -', '第1頁', 'Page 2'", "フッター（- 1 -、第1頁、Page 2など）は破棄。", True],
        [8, "Remove fixed headers / page titles using template words; flag uncertain ones with [疑いフラグ]", "ページ先頭の局名・固定タイトルはテンプレ語一致で削除。自信がなければ「疑いフラグ」。", False],
        [9, "Remove announcement (公告) section up to 入札説明書", "公告部分（入札参加資格／公告番号 等）は本文対象外。", True],
    ]

    csv_path = BASE_DIR / "cleaning_rules_status.csv"
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rules_status)

    print(f"📋 Rule status CSV generated at: {csv_path}")
# ----------------------------------------

if __name__ == "__main__":
    process_text_files(INPUT_DIR, OUTPUT_DIR)
