
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dsl_engine.py
A tiny interpreter for an indentation-based DSL like the sample provided.
Usage:
  python dsl_engine.py --script 85_script.dsl --input input.txt

Concepts:
- Top-level keys (no indent, ending with ':') define output variables to compute and print.
- Nested blocks describe how to compute them using:
  - search in : all | taken | varName  (where varName was previously store(varName))
  - search in first : N
  - search text : <str> | [a, b, c]  (list means: all must be present; order ignored)
  - if found: ... / if not found: ...
  - take right: ... / take left: ...  (switch the working text to right/left side of the last match)
  - remove whitespaces
  - add in right(XX) / add in left(XX)
  - replace(old, new)  (global replace in current working text)
  - replace(start, old, new) / replace(end, old, new) (only at start/end)
  - store(varName)  (stores current working text to a temp)
  - set(XX)         (sets the outer variable to temp var or literal; supports true/false)
  - check : varName + has value : XXX + if true/if false blocks

Notes:
- "search in : taken" operates on the current working text inside the current nested block.
- "search in : all" or "search in first : N" operate on the full original input.
- After a "take right/left" block finishes, the working text reverts to previous (nested-scope style).
- Minor typos tolerated: "seach" is treated as "search".
- "remove tables" removes any [[TABLE_START...]] ... [[TABLE_END]] blocks from the working text.
"""

import argparse
import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import csv
import unicodedata
import pandas as pd

# --------------------------- Parsing ---------------------------

BLOCK_KEYS = {
    "if found", "if not found", "if true", "if false",
    "take right", "take left"
}

COMMAND_PATTERN_PARENS = re.compile(r'^(?P<cmd>add in right|add in left|store|set|replace)\s*\((?P<arg>.*)\)\s*$')
PAGE_MARKER_RE = re.compile(
    r"\[\[PAGE_START(?:\s*\d+)?\s*\]\]|\[\[PAGE_END\s*\]\]|\[\[HEADING\]\]\s*\d*"
)
TABLE_MARKER_RE = re.compile(
    r"\[\[TABLE_START(?:\s*\d+)?\s*\]\]|\[\[TABLE_END\s*\]\]|\[\[HEADING\]\]\s*\d*"
)
TRAILING_MARKER_RE = re.compile(
    r"(?:\s*(?:\[\[PAGE_START(?:\s*\d+)?\s*\]\]|\[\[PAGE_END\s*\]\]|\[\[HEADING\]\]\s*\d*|\[\[TABLE_START(?:\s*\d+)?\s*\]\]|\[\[TABLE_END\s*\]\]))\s*$"
)
LEADING_MARKER_RE = re.compile(
    r"^\s*(?:\[\[PAGE_START(?:\s*\d+)?\s*\]\]|\[\[PAGE_END\s*\]\]|\[\[HEADING\]\]\s*\d*|\[\[TABLE_START(?:\s*\d+)?\s*\]\]|\[\[TABLE_END\s*\]\])\s*"
)
EDGE_INVISIBLE_RE = re.compile(r"[\s\u200b\u200c\u200d\u2060\ufeff\u00ad\u200e\u200f\u202a-\u202e]+$")
EDGE_INVISIBLE_LEAD_RE = re.compile(r"^[\s\u200b\u200c\u200d\u2060\ufeff\u00ad\u200e\u200f\u202a-\u202e]+")
INVISIBLE_CHARS_CLASS = r"[\u200b\u200c\u200d\u2060\ufeff\u00ad\u200e\u200f\u202a-\u202e]*"

def _strip_page_markers(s: str) -> str:
    """Remove [[PAGE_START...]] and [[PAGE_END...]] markers from a string."""
    return PAGE_MARKER_RE.sub("", s)

def _strip_table_markers(s: str) -> str:
    """Remove [[PAGE_START...]] and [[PAGE_END...]] markers from a string."""
    return TABLE_MARKER_RE.sub("", s)

def _remove_tables(s: str) -> str:
    """
    Remove any table blocks from text. A table block is defined as:
      [[TABLE_START...]] ... [[TABLE_END]]
    If a start marker is found without a matching end marker, the rest of the
    text is dropped (defensive).
    """
    start_token = "[[TABLE_START"
    end_token = "[[TABLE_END]]"
    if start_token not in s and end_token not in s:
        return s

    out = []
    i = 0
    n = len(s)
    while i < n:
        start = s.find(start_token, i)
        if start == -1:
            out.append(s[i:])
            break
        out.append(s[i:start])
        end = s.find(end_token, start)
        if end == -1:
            # Drop rest if table end is missing
            break
        i = end + len(end_token)

    result = "".join(out)
    # Remove any stray markers left behind (e.g., unmatched end markers).
    if start_token in result or end_token in result:
        result = re.sub(r"\[\[TABLE_START[^\]]*\]\]", "", result)
        result = result.replace(end_token, "")
    return result


def _remove_empty_lines(s: str) -> str:
    return "\n".join(line for line in s.splitlines() if line.strip())

def _cell_value(v: Any) -> Any:
    if v is None:
        return ""
    if isinstance(v, str):
        return _remove_empty_lines(v)
    return v


def strip_comment(line: str) -> str:
    # remove '#' comments outside quotes
    # - full-line comments: lines that start with '##' (optionally indented) are treated as empty
    # - inline comments: everything after the first '#' (outside quotes) is stripped
    if line.lstrip().startswith("##"):
        return ""
    s = []
    in_q = False
    q = ''
    for ch in line:
        if ch in ('"', "'"):
            if not in_q:
                in_q = True; q = ch
            elif q == ch:
                in_q = False
        if ch == '#' and not in_q:
            break
        s.append(ch)
    return ''.join(s).rstrip('\n')

def _unquote(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

def _decode_escapes_for_search(s: str) -> str:
    # support "\n" and "\t" at least
    return s.replace("\\n", "\n").replace("\\t", "\t")

def _decode_escapes_for_add(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch != "\\" or i == len(s) - 1:
            out.append(ch)
            i += 1
            continue

        nxt = s[i + 1]
        if nxt == "n":
            out.append("\n")
        elif nxt == "t":
            out.append("\t")
        elif nxt == "r":
            out.append("\r")
        elif nxt == "\\":
            out.append("\\")
        else:
            out.append("\\")
            out.append(nxt)
        i += 2
    return "".join(out)

def _resolve_add_arg(arg: Any, env: "ExecEnv") -> str:
    """
    Resolve the argument of add in left/right into a string:
    - "..." or '...': treat as a literal
    - name in env.stored: use stored local value
    - name in env.outputs: use previously computed global variable
    - otherwise: use the raw text as-is

    Also decodes escape sequences for literal inputs: \n, \t, \r, \\.
    """
    if arg is None:
        return ""

    s = str(arg).strip()

    # quoted literal
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return _decode_escapes_for_add(s[1:-1])

    # local temp storage has priority
    if s in env.stored and env.stored[s] is not None:
        return str(env.stored[s])

    # then global outputs (other DSL top-level vars)
    if s in env.outputs and env.outputs[s] is not None:
        return str(env.outputs[s])

    # fallback: treat as literal text
    return _decode_escapes_for_add(s)

def _split_trailing_markers_and_ws(s: str):
    """Split text into (base, suffix) by stripping trailing whitespace/markers from the end."""
    base = s
    while True:
        new = EDGE_INVISIBLE_RE.sub("", base)
        m = TRAILING_MARKER_RE.search(new)
        if m:
            base = new[:m.start()]
            continue
        if new == base:
            base = new
            break
        base = new
    suffix = s[len(base):]
    return base, suffix

def _split_leading_markers_and_ws(s: str):
    """Split text into (prefix, rest) by stripping leading whitespace/markers from the start."""
    rest = s
    prefix = ""
    while True:
        m_ws = EDGE_INVISIBLE_LEAD_RE.match(rest)
        if m_ws:
            prefix += m_ws.group(0)
            rest = rest[m_ws.end():]
            continue
        m = LEADING_MARKER_RE.match(rest)
        if m:
            prefix += m.group(0)
            rest = rest[m.end():]
            continue
        break
    return prefix, rest

def _fuzzy_invisible_pattern(text: str) -> str:
    """Build a regex that matches text allowing invisible chars between characters."""
    if not text:
        return ""
    return INVISIBLE_CHARS_CLASS.join(re.escape(ch) for ch in text)


@dataclass
class Node:
    kind: str              # 'var' | 'block' | 'kv' | 'command'
    name: str              # variable name, block key, kv key, or command name
    value: Any = None      # for kv or command arg
    indent: int = 0
    children: List['Node'] = field(default_factory=list)

def parse_list_value(text: str) -> list:
    s = text.strip()
    if not (s.startswith('[') and s.endswith(']')):
        # Fallback: treat as single (quoted or unquoted) token
        return [_unquote(s)]

    inner = s[1:-1]
    items, buf = [], []
    in_q = None
    escape = False

    for ch in inner:
        if escape:
            buf.append(ch)
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if in_q:
            if ch == in_q:
                in_q = None
            else:
                buf.append(ch)
            continue
        # not in quotes
        if ch in ('"', "'"):
            in_q = ch
        elif ch == ',':
            item = ''.join(buf).strip()
            items.append(_unquote(item))
            buf = []
        else:
            buf.append(ch)

    # last item
    if buf:
        items.append(_unquote(''.join(buf).strip()))
    return items


def parse_script(text: str) -> List[Node]:
    lines = text.splitlines()
    root: List[Node] = []
    stack: List[Node] = []
    indent_stack: List[int] = []

    def add_node(node: Node):
        if not stack:
            root.append(node)
        else:
            stack[-1].children.append(node)

    for raw in lines:
        # Tolerate UTF-8 BOM if present at start-of-file / start-of-line
        raw = raw.lstrip("\ufeff")
        line = strip_comment(raw).rstrip()
        if not line.strip():
            continue
        # normalize tabs to 4 spaces & count indent
        expanded = line.expandtabs(4)
        indent = len(expanded) - len(expanded.lstrip(' '))
        content = expanded.strip()

        # commands like store(x), set(y), add in right(z)
        m = COMMAND_PATTERN_PARENS.match(content)
        if m:
            cmd = m.group('cmd').strip()
            arg = m.group('arg').strip()
            node = Node(kind='command', name=cmd, value=arg, indent=indent)
        else:
            # normalize 'seach' to 'search'
            content = re.sub(r'^\s*seach\b', 'search', content)
            # block vs kv
            if content.endswith(':'):
                key = content[:-1].strip()
                if indent == 0:
                    node = Node(kind='var', name=key, indent=indent)
                elif key in BLOCK_KEYS:
                    node = Node(kind='block', name=key, indent=indent)
                else:
                    # treat unknown trailing-colon as block too (defensive)
                    node = Node(kind='block', name=key, indent=indent)
            else:
                # kv: key : value
                if ':' in content:
                    key, val = content.split(':', 1)
                    node = Node(kind='kv', name=key.strip(), value=val.strip(), indent=indent)
                else:
                    # bare word -> treat as command with no arg
                    node = Node(kind='command', name=content.strip(), indent=indent)

        # fix stack
        while indent_stack and indent_stack[-1] >= indent:
            stack.pop(); indent_stack.pop()
        add_node(node)
        if node.kind in ('var', 'block'):
            stack.append(node); indent_stack.append(indent)

    return root

def _parse_two_args_quoted(argstr: str):
    s = argstr.strip()
    items, buf = [], []
    quoted_flags = []
    in_q = None
    escape = False
    quoted = False
    after_quote = False
    for ch in s:
        if escape:
            buf.append(ch); escape = False; continue
        if ch == '\\':
            escape = True; continue
        if in_q:
            if ch == in_q:
                in_q = None
                after_quote = True
            else:
                buf.append(ch)
            continue
        if ch in ('"', "'"):
            in_q = ch
            quoted = True
            continue
        if ch == ',' and len(items) == 0:
            item = ''.join(buf)
            if not quoted:
                item = item.strip()
            items.append(item); quoted_flags.append(quoted); buf = []
            quoted = False
            after_quote = False
            continue
        if after_quote:
            if ch.isspace():
                continue
            after_quote = False
        if not quoted and not buf and ch.isspace():
            continue
        buf.append(ch)
    item = ''.join(buf)
    if not quoted:
        item = item.strip()
    items.append(item); quoted_flags.append(quoted)

    def clean(x: str, was_quoted: bool) -> str:
        if was_quoted:
            return x
        x = x.strip()
        if (x.startswith('"') and x.endswith('"')) or (x.startswith("'") and x.endswith("'")):
            return x[1:-1]
        return x
    a = clean(items[0], quoted_flags[0]) if items else ''
    b = clean(items[1], quoted_flags[1]) if len(items) > 1 else ''
    return a, b

def _parse_three_args_quoted(argstr: str):
    s = argstr.strip()
    items, buf = [], []
    quoted_flags = []
    in_q = None
    escape = False
    quoted = False
    after_quote = False
    for ch in s:
        if escape:
            buf.append(ch); escape = False; continue
        if ch == '\\':
            escape = True; continue
        if in_q:
            if ch == in_q:
                in_q = None
                after_quote = True
            else:
                buf.append(ch)
            continue
        if ch in ('"', "'"):
            in_q = ch
            quoted = True
            continue
        if ch == ',' and len(items) < 2:
            item = ''.join(buf)
            if not quoted:
                item = item.strip()
            items.append(item); quoted_flags.append(quoted); buf = []
            quoted = False
            after_quote = False
            continue
        if after_quote:
            if ch.isspace():
                continue
            after_quote = False
        if not quoted and not buf and ch.isspace():
            continue
        buf.append(ch)
    item = ''.join(buf)
    if not quoted:
        item = item.strip()
    items.append(item); quoted_flags.append(quoted)
    def clean(x: str, was_quoted: bool) -> str:
        if was_quoted:
            return x
        x = x.strip()
        if (x.startswith('"') and x.endswith('"')) or (x.startswith("'") and x.endswith("'")):
            return x[1:-1]
        return x
    return [clean(x, q) for x, q in zip(items, quoted_flags)]


# --------------------------- Execution ---------------------------

@dataclass
class ExecEnv:
    original_text: str
    current_text: str
    stored: Dict[str, str] = field(default_factory=dict)   # temp store for this variable
    outputs: Dict[str, Any] = field(default_factory=dict)  # global outputs across variables
    last_search_found: bool = False
    last_match_start: int = -1
    last_match_end: int = -1
    last_scope_kind: str = ''   # 'all' | 'taken' | 'first'
    last_scope_text: str = ''
    pending_scope: str = ''     # 'all' | 'taken' | 'first'
    pending_scope_var: Optional[str] = None  # for 'search in : varName'
    pending_first_n: Optional[int] = None
    pending_search_value: Any = None
    check_var: Optional[str] = None
    check_expected: Optional[str] = None
    set_value: Any = None       # final value for the variable being computed

# def resolve_scope_text(env: ExecEnv) -> str:
#     if env.pending_scope == 'taken':
#         return env.current_text
#     if env.pending_scope == 'first':
#         n = env.pending_first_n or 0
#         return env.original_text[:max(n, 0)]
#     # default/all
#     return env.original_text

def resolve_scope_text(env: ExecEnv) -> str:
    # Decide which base text to search in, based on the last 'search in :' directive.
    # - 'taken' : the current working text in this block
    # - 'first' : first N chars of the full text
    # - 'stored': a previously store(varName) buffer or an already-set output
    # - default : full original text
    if env.pending_scope == 'taken':
        return env.current_text
    if env.pending_scope == 'first':
        n = env.pending_first_n or 0
        return env.original_text[:max(n, 0)]
    if env.pending_scope == 'stored' and env.pending_scope_var:
        # Prefer locally stored buffers
        buf = env.stored.get(env.pending_scope_var)
        if buf is not None:
            return buf
        # Fallback: allow searching in another variable's output if it's a string
        out_val = env.outputs.get(env.pending_scope_var)
        if isinstance(out_val, str):
            return out_val
        # As a last resort, fall back to full text (backwards-compatible behaviour)
        return env.original_text
    # default/all
    return env.original_text


def do_search(env: ExecEnv, search_value: Any):
    # search_value can be string or list of strings
    scope_text = resolve_scope_text(env)
    env.last_scope_text = scope_text
    env.last_match_start = -1
    env.last_match_end = -1

    if isinstance(search_value, list):
        ok = all(scope_text.find(item) >= 0 for item in search_value)
        env.last_search_found = ok
        # keep no specific match indices for list search
    else:
        pat = str(search_value)
        idx = scope_text.find(pat)
        env.last_search_found = (idx >= 0)
        if idx >= 0:
            env.last_match_start = idx
            env.last_match_end = idx + len(pat)
    # reset pending
    env.pending_scope = ''
    env.pending_scope_var = None
    env.pending_first_n = None
    env.pending_search_value = None
    
def do_search_any(env, items):
    """OR search over items; anchor to the earliest occurrence among matches."""
    scope_text = resolve_scope_text(env)
    env.last_scope_text = scope_text
    best_idx = -1
    best_len = 0
    for it in items:
        idx = scope_text.find(it)
        if idx >= 0 and (best_idx == -1 or idx < best_idx):
            best_idx = idx
            best_len = len(it)
    env.last_search_found = (best_idx >= 0)
    env.last_match_start = best_idx
    env.last_match_end = (best_idx + best_len) if best_idx >= 0 else -1
    # clear pending
    env.pending_scope = ''
    env.pending_scope_var = None
    env.pending_first_n = None
    env.pending_search_value = None


def do_search_ordered(env, items):
    """Sequential search by order; anchor to the first item in order that is found."""
    scope_text = resolve_scope_text(env)
    env.last_scope_text = scope_text
    found_idx = -1
    found_len = 0
    for it in items:
        idx = scope_text.find(it)
        if idx >= 0:
            found_idx = idx
            found_len = len(it)
            break
    env.last_search_found = (found_idx >= 0)
    env.last_match_start = found_idx
    env.last_match_end = (found_idx + found_len) if found_idx >= 0 else -1
    # clear pending
    env.pending_scope = ''
    env.pending_scope_var = None
    env.pending_first_n = None
    env.pending_search_value = None


def with_taken(env: ExecEnv, take: str) -> ExecEnv:
    new_env = ExecEnv(
        original_text=env.original_text,
        current_text=take,
        stored=dict(env.stored),
        outputs=env.outputs,  # share global outputs
        last_search_found=False
    )
    return new_env

def eval_nodes(nodes: List[Node], env: ExecEnv, var_name: Optional[str]=None):
    i = 0
    while i < len(nodes):
        node = nodes[i]

        if node.kind == 'kv':
            key = node.name.strip().lower()
            val_raw = node.value

            # normalize keys
            key = key.replace('seach', 'search')
            if key == 'search in first':
                # e.g., '20'
                try:
                    env.pending_scope = 'first'
                    env.pending_first_n = int(str(val_raw).strip())
                except:
                    env.pending_scope = 'first'
                    env.pending_first_n = 0
            elif key == 'search in':
                raw = str(val_raw).strip()
                v = raw.lower()
                if v == 'taken':
                    env.pending_scope = 'taken'
                    env.pending_scope_var = None
                elif v == 'all' or raw == '':
                    env.pending_scope = 'all'
                    env.pending_scope_var = None
                else:
                    # Treat as "search only inside this stored/output buffer"
                    env.pending_scope = 'stored'
                    env.pending_scope_var = raw
            elif key == 'search text':
                txt = str(val_raw).strip()
                # AND list: [a, b, c] — boolean only (no anchor)
                if txt.startswith('[') and txt.endswith(']'):
                    search_list = parse_list_value(txt)
                    search_list = [_decode_escapes_for_search(s) for s in search_list]
                    env.pending_search_value = search_list
                    do_search(env, search_list)

                # OR list: (a, b, c) — true if any found; anchor to earliest occurrence
                elif txt.startswith('(') and txt.endswith(')'):
                    inner = txt[1:-1]
                    items = parse_list_value(f'[{inner}]')  # reuse list parser (quote-aware)
                    items = [_decode_escapes_for_search(s) for s in items]
                    env.pending_search_value = items
                    do_search_any(env, items)

                # ORDERED list: {a, b, c} — try a, else b, else c; anchor to first found in order
                elif txt.startswith('{') and txt.endswith('}'):
                    inner = txt[1:-1]
                    items = parse_list_value(f'[{inner}]')  # reuse list parser (quote-aware)
                    items = [_decode_escapes_for_search(s) for s in items]
                    env.pending_search_value = items
                    do_search_ordered(env, items)

                # scalar
                else:
                    scalar = _unquote(txt)  # supports "quoted" or bare
                    scalar = _decode_escapes_for_search(scalar)
                    env.pending_search_value = scalar
                    do_search(env, scalar)
            elif key == 'remove whitespaces':
                env.current_text = env.current_text.strip()
            elif key == 'remove tables':
                env.current_text = _remove_tables(env.current_text)
            elif key == 'add in right':
                # value might be "(所)" if parsed as kv; but in sample it's a command form add in right(所)
                to_add = _resolve_add_arg(val_raw, env)
                env.current_text = f"{env.current_text}{to_add}"
            elif key == 'add in left':
                to_add = _resolve_add_arg(val_raw, env)
                env.current_text = f"{to_add}{env.current_text}"
            elif key == 'store':
                name = str(val_raw).strip()
                env.stored[name] = env.current_text
            elif key == 'set':
                arg = str(val_raw).strip()
                if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                    env.set_value = arg[1:-1]
                else:
                    lc = arg.lower()
                    if arg in env.stored:
                        env.set_value = env.stored[arg]
                    elif arg in env.outputs:
                        env.set_value = env.outputs[arg]
                    elif lc == 'true':
                        env.set_value = True
                    elif lc == 'false':
                        env.set_value = False
                    else:
                        env.set_value = arg
            elif key == 'check':
                env.check_var = str(val_raw).strip()
            elif key == 'has value':
                env.check_expected = _unquote(str(val_raw).strip())
            else:
                # ignore unknown kv
                pass

        elif node.kind == 'command':
            cmd = node.name.strip().lower()
            # allow paren form: handled earlier; still support bare variants
            m = COMMAND_PATTERN_PARENS.match(node.name)
            arg_text = node.value if node.value is not None else (m.group('arg') if m else None)
            if cmd.startswith('add in right'):
                raw = node.value if node.value is not None else (m.group('arg') if m else '')
                to_add = _resolve_add_arg(raw, env)
                env.current_text = f"{env.current_text}{to_add}"
            elif cmd.startswith('add in left'):
                raw = node.value if node.value is not None else (m.group('arg') if m else '')
                to_add = _resolve_add_arg(raw, env)
                env.current_text = f"{to_add}{env.current_text}"
            elif cmd.startswith('store'):
                name = node.value if node.value is not None else (m.group('arg') if m else 'var')
                env.stored[name] = env.current_text
            elif cmd.startswith('set'):
                arg = node.value if node.value is not None else (m.group('arg') if m else '')
                arg = str(arg).strip()
                if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                    env.set_value = arg[1:-1]
                else:
                    lc = arg.lower()
                    # Special case: set(all) should stash the full original text
                    if lc == 'all':
                        env.set_value = env.original_text
                    elif arg in env.stored:
                        env.set_value = env.stored[arg]
                    elif arg in env.outputs:
                        env.set_value = env.outputs[arg]
                    elif lc == 'true':
                        env.set_value = True
                    elif lc == 'false':
                        env.set_value = False
                    else:
                        env.set_value = arg
            elif cmd == 'remove whitespaces':
                env.current_text = env.current_text.strip()
            elif cmd == 'remove tables':
                env.current_text = _remove_tables(env.current_text)
            elif cmd.startswith('replace'):
                raw = node.value if node.value is not None else (m.group('arg') if m else '')
                args3 = _parse_three_args_quoted(raw)
                if len(args3) >= 3 and args3[0].strip().lower() in ("start", "end"):
                    mode = args3[0].strip().lower()
                    old = args3[1]
                    new = args3[2]
                    if old:
                        if mode == "start":
                            if env.current_text.startswith(old):
                                env.current_text = f"{new}{env.current_text[len(old):]}"
                            else:
                                prefix, rest = _split_leading_markers_and_ws(env.current_text)
                                if rest.startswith(old):
                                    env.current_text = f"{prefix}{new}{rest[len(old):]}"
                                else:
                                    pat = _fuzzy_invisible_pattern(old)
                                    if pat:
                                        m = re.search(rf"^{pat}", rest)
                                        if m:
                                            env.current_text = f"{prefix}{new}{rest[m.end():]}"
                        else:
                            if env.current_text.endswith(old):
                                env.current_text = f"{env.current_text[:-len(old)]}{new}"
                            else:
                                base, suffix = _split_trailing_markers_and_ws(env.current_text)
                                if base.endswith(old):
                                    env.current_text = f"{base[:-len(old)]}{new}{suffix}"
                                else:
                                    pat = _fuzzy_invisible_pattern(old)
                                    if pat:
                                        m = re.search(rf"{pat}$", base)
                                        if m:
                                            env.current_text = f"{base[:m.start()]}{new}{base[m.end():]}{suffix}"
                else:
                    old, new = _parse_two_args_quoted(raw)
                    env.current_text = env.current_text.replace(old, new)
            else:
                # unknown bare command -> ignore
                pass

        elif node.kind == 'block':
            bname = node.name.strip().lower()
            if bname == 'if found':
                if env.last_search_found:
                    eval_nodes(node.children, env, var_name)
            elif bname == 'if not found':
                if not env.last_search_found:
                    eval_nodes(node.children, env, var_name)
            elif bname == 'if true':
                val = env.outputs.get(env.check_var)
                if val is None:
                    val = env.stored.get(env.check_var)  # ← look at stored vars too
                ok = (val == env.check_expected) if env.check_expected is not None else bool(val)
                if ok:
                    eval_nodes(node.children, env, var_name)
            elif bname == 'if false':
                val = env.outputs.get(env.check_var)
                if val is None:
                    val = env.stored.get(env.check_var)  # ← same here
                ok = (val == env.check_expected) if env.check_expected is not None else bool(val)
                if not ok:
                    eval_nodes(node.children, env, var_name)
            elif bname == 'take right':
                # use last match window; if no match recorded, nothing happens but descend with same env
                if env.last_search_found and env.last_match_end >= 0:
                    sub_text = env.last_scope_text[env.last_match_end:]
                else:
                    sub_text = env.current_text
                sub_env = with_taken(env, sub_text)
                eval_nodes(node.children, sub_env, var_name)
                # sync changes that are global-ish
                env.outputs = sub_env.outputs
                env.stored.update(sub_env.stored)
                if sub_env.set_value is not None:
                    env.set_value = sub_env.set_value
            elif bname == 'take left':
                if env.last_search_found and env.last_match_start >= 0:
                    sub_text = env.last_scope_text[:env.last_match_start]
                else:
                    sub_text = env.current_text
                sub_env = with_taken(env, sub_text)
                eval_nodes(node.children, sub_env, var_name)
                env.outputs = sub_env.outputs
                env.stored.update(sub_env.stored)
                if sub_env.set_value is not None:
                    env.set_value = sub_env.set_value
            else:
                # unknown block, just eval its children in same env
                eval_nodes(node.children, env, var_name)

        elif node.kind == 'var':
            # shouldn't be nested, but if it is, evaluate normally
            eval_variable(node, env)

        i += 1

def eval_variable(var_node: Node, global_env: ExecEnv):
    # compute a single variable in isolation (fresh local store/current), but can read previously computed outputs.
    var_name = var_node.name
    env = ExecEnv(
        original_text=global_env.original_text,
        current_text=global_env.original_text,
        stored={},
        outputs=global_env.outputs
    )
    eval_nodes(var_node.children, env, var_name)
    # if not set, default to empty string
    value = env.set_value
    if isinstance(value, str):
        value = _strip_page_markers(value)
        value = _strip_table_markers(value)
        value = _remove_empty_lines(value)
        value = value.strip()
        
    global_env.outputs[var_name] = value

def _build_page_spans(text: str):
    """
    Scan [[PAGE_START N]] markers and build a list of (page_no:int, start_index:int).
    """
    spans = []
    for m in re.finditer(r"\[\[PAGE_START\s*(\d+)\s*\]\]", text):
        page_no = int(m.group(1))
        spans.append((page_no, m.start()))
    spans.sort(key=lambda x: x[1])
    return spans


def _page_for_index(idx: int, spans) -> Optional[int]:
    """
    Given a character index and page spans, return the page number whose start <= idx.
    If no page_start exists before idx, returns None.
    """
    current = None
    for page_no, start_idx in spans:
        if start_idx <= idx:
            current = page_no
        else:
            break
    return current


# def run(script_text: str, input_text: str) -> Dict[str, Any]:
#     tree = parse_script(script_text)
#     g = ExecEnv(original_text=input_text, current_text=input_text, outputs={})
#     # Execute variables in order
#     for node in tree:
#         if node.kind == 'var':
#             eval_variable(node, g)
#     return g.outputs

def run(script_text: str, input_text: str) -> Dict[str, Any]:
    tree = parse_script(script_text)
    g = ExecEnv(original_text=input_text, current_text=input_text, outputs={})
    # Execute variables in order
    for node in tree:
        if node.kind == 'var':
            eval_variable(node, g)

    # After values are computed, add "<var> pageNo" entries for string values
    page_spans = _build_page_spans(input_text)
    if page_spans:
        for name, val in list(g.outputs.items()):
            # avoid creating pageNo for pageNo fields themselves
            if name.endswith(" pageNo"):
                continue
            if isinstance(val, str) and val:
                idx = input_text.find(val)
                if idx >= 0:
                    page_no = _page_for_index(idx, page_spans)
                    if page_no is not None:
                        g.outputs[f"{name} pageNo"] = page_no

    return g.outputs


def _write_csv(out_path, headers, outputs, source_name):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    full_headers = ['file name'] + headers

    outputs = _normalize_outputs_for_csv(outputs)

    row = [source_name] + [
        outputs.get(h, "")
        for h in headers
    ]
    table = _transpose_table([
        full_headers,
        row,
    ])
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        # 🔽 force quoting so line breaks stay inside the cell
        w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        for r in table:
            w.writerow([_cell_value(v) for v in r])


def _write_excel(out_path, headers, outputs, source_name):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    full_headers = ['file name'] + headers

    outputs = _normalize_outputs_for_csv(outputs)

    row = [source_name] + [
        outputs.get(h, "")
        for h in headers
    ]
    table = _transpose_table([
        full_headers,
        row,
    ])
    df = pd.DataFrame([[_cell_value(v) for v in r] for r in table])
    df.to_excel(out_path, index=False, header=False, engine="openpyxl")


def _write_excel_table(out_path, headers, rows):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    table = _transpose_table([headers] + rows)
    df = pd.DataFrame([[_cell_value(v) for v in r] for r in table])
    df.to_excel(out_path, index=False, header=False, engine="openpyxl")


HALFWIDTH_KANA_RE = re.compile(r"[\uFF61-\uFF9F]+")
DOUBLE_PAREN_POINTER_RE = re.compile(r"[(（]{2}\s*([0-9０-９]{1,3})\s*[)）]{2}")

def _circled_number(n: int) -> Optional[str]:
    if n == 0:
        return "⓪"
    # ①..⑳ (1..20)
    if 1 <= n <= 20:
        return chr(0x2460 + (n - 1))
    # ㉑..㉟ (21..35)
    if 21 <= n <= 35:
        return chr(0x3251 + (n - 21))
    # ㊱..㊿ (36..50)
    if 36 <= n <= 50:
        return chr(0x32B1 + (n - 36))
    return None

def _replace_double_paren_pointers(s: str) -> str:
    if not s:
        return s

    def repl(m: re.Match) -> str:
        raw = m.group(1)
        try:
            n = int(unicodedata.normalize("NFKC", raw))
        except ValueError:
            return m.group(0)
        enclosed = _circled_number(n)
        return enclosed if enclosed is not None else m.group(0)

    return DOUBLE_PAREN_POINTER_RE.sub(repl, s)

def _to_fullwidth(s: str) -> str:
    if not s:
        return s

    # Convert halfwidth Katakana (and related marks) to fullwidth without touching other chars.
    s = HALFWIDTH_KANA_RE.sub(lambda m: unicodedata.normalize("NFKC", m.group(0)), s)

    # Convert ASCII to fullwidth (e.g., 0-9/A-Z/a-z/- etc.) and space to ideographic space.
    trans = {0x20: 0x3000}
    trans.update({code: code + 0xFEE0 for code in range(0x21, 0x7F)})
    return s.translate(trans)

def _remove_halfwidth_spaces(s: str) -> str:
    if not s:
        return s
    return s.replace(" ", "")

def _transpose_table(rows: List[List[Any]]) -> List[List[Any]]:
    if not rows:
        return rows
    max_len = max(len(r) for r in rows)
    padded = [list(r) + [""] * (max_len - len(r)) for r in rows]
    return [list(col) for col in zip(*padded)]

def _is_kouji_name_key(name: Any) -> bool:
    if not isinstance(name, str):
        return False
    # DSL variable names often use Japanese corner quotes: 「工事名」
    return name.strip().strip("「」") == "工事名"

def _normalize_outputs_for_csv(outputs: Dict[str, Any]) -> Dict[str, Any]:
    if not outputs:
        return outputs
    normalized = dict(outputs)
    for k, v in list(normalized.items()):
        if not isinstance(v, str):
            continue
        if _is_kouji_name_key(k):
            v = _replace_double_paren_pointers(v)
            normalized[k] = _to_fullwidth(v)
        else:
            normalized[k] = _remove_halfwidth_spaces(v)
    return normalized


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="DSL script file")
    ap.add_argument("--input", help="UTF-8 text file to parse")
    ap.add_argument("--input_dir", help="Directory of .txt files to batch process")
    ap.add_argument("--outdir", help="Directory to write per-file CSVs")
    ap.add_argument("--json", action="store_true", help="Print JSON output")
    args = ap.parse_args()

    with open(args.script, "r", encoding="utf-8") as f:
        script_text = f.read()
    # with open(args.input, "r", encoding="utf-8") as f:
    #     input_text = f.read()

    tree_for_header = parse_script(script_text)
    base_vars  = [n.name for n in tree_for_header if n.kind == 'var']

    excluded_csv_vars = {"reg_A", "reg_B"}
    var_order = []
    for name in base_vars:
        if name in excluded_csv_vars:
            continue
        var_order.append(name)
        var_order.append(f"{name} pageNo")

    # outputs = run(script_text, input_text)

    # if args.json:
    #     print(json.dumps(outputs, ensu    re_ascii=False, indent=2))
    # else:
    #     for k, v in outputs.items():
    #         print(f"{k}: {v}")

    if args.input_dir:
        if not args.outdir:
            raise SystemExit("--outdir is required when using --input_dir")
        in_dir = args.input_dir
        out_dir = args.outdir

        overall_rows = []      # summary for all text files (with relative path)

        # recursive walk to pick up nested folders
        for dirpath, _, filenames in os.walk(in_dir):
            txt_files = [f for f in sorted(filenames) if f.lower().endswith(".txt")]
            if not txt_files:
                continue

            rel_dir = os.path.relpath(dirpath, in_dir)
            rel_dir = "" if rel_dir == "." else rel_dir

            for fname in txt_files:
                fpath = os.path.join(dirpath, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                outputs = run(script_text, text)
                outputs_csv = _normalize_outputs_for_csv(outputs)

                dest_dir = out_dir if not rel_dir else os.path.join(out_dir, rel_dir)
                os.makedirs(dest_dir, exist_ok=True)
                base = os.path.splitext(fname)[0]
                out_path = os.path.join(dest_dir, base + ".csv")
                _write_csv(out_path, var_order, outputs_csv, source_name=fname)
                row_vals = [
                    (outputs_csv.get(h, "") if outputs_csv.get(h, "") is not None else "")
                    for h in var_order
                ]
                rel_name = fname if not rel_dir else os.path.join(rel_dir, fname)
                overall_rows.append([rel_name] + row_vals)

        # write overall summary for every text file processed
        if overall_rows:
            root_label = os.path.basename(os.path.normpath(in_dir))
            overall_path = os.path.join(out_dir, f"{root_label}_all_texts_summary.csv")
            os.makedirs(os.path.dirname(overall_path), exist_ok=True)
            with open(overall_path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
                table = _transpose_table([['file name'] + var_order] + overall_rows)
                for r in table:
                    w.writerow([_cell_value(v) for v in r])
            overall_xlsx_path = os.path.join(out_dir, f"{root_label}_all_texts_summary.xlsx")
            _write_excel_table(overall_xlsx_path, ['file name'] + var_order, overall_rows)
        return

 # --- Single-file mode ---
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            input_text = f.read()
        outputs = run(script_text, input_text)
        # If outdir is provided, write one CSV for this file; else keep old behavior
        if args.outdir:
            outputs_csv = _normalize_outputs_for_csv(outputs)
            base = os.path.splitext(os.path.basename(args.input))[0]
            out_path = os.path.join(args.outdir, base + ".csv")
            src_name = os.path.basename(args.input)
            _write_csv(out_path, var_order, outputs_csv, source_name=src_name)
        else:
            if args.json:
                cleaned = {
                    k: (_remove_empty_lines(v) if isinstance(v, str) else v)
                    for k, v in outputs.items()
                }
                print(json.dumps(cleaned, ensure_ascii=False, indent=2))
            else:
                for k, v in outputs.items():
                    if isinstance(v, str):
                        v = _remove_empty_lines(v)
                    print(f"{k}: {v}")
        return

    raise SystemExit("Provide either --input or --input_dir")

if __name__ == "__main__":
    main()
