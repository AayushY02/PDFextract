
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
  - search in : all | taken
  - search in first : N
  - search text : <str> | [a, b, c]  (list means: all must be present; order ignored)
  - if found: ... / if not found: ...
  - take right: ... / take left: ...  (switch the working text to right/left side of the last match)
  - remove whitespaces
  - add in right(XX) / add in left(XX)
  - store(varName)  (stores current working text to a temp)
  - set(XX)         (sets the outer variable to temp var or literal; supports true/false)
  - check : varName + has value : XXX + if true/if false blocks

Notes:
- "search in : taken" operates on the current working text inside the current nested block.
- "search in : all" or "search in first : N" operate on the full original input.
- After a "take right/left" block finishes, the working text reverts to previous (nested-scope style).
- Minor typos tolerated: "seach" is treated as "search".
"""

import argparse
import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import csv

# --------------------------- Parsing ---------------------------

BLOCK_KEYS = {
    "if found", "if not found", "if true", "if false",
    "take right", "take left"
}

COMMAND_PATTERN_PARENS = re.compile(r'^(?P<cmd>add in right|add in left|store|set|replace)\((?P<arg>.*)\)\s*$')
PAGE_MARKER_RE = re.compile(r"\[\[PAGE_START\s+\d+\]\]|\[\[PAGE_END\]\]")

def _strip_page_markers(s: str) -> str:
    """Remove [[PAGE_START N]] and [[PAGE_END]] markers from a string."""
    return PAGE_MARKER_RE.sub("", s)


def strip_comment(line: str) -> str:
    # remove '#' comments outside quotes
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
    in_q = None
    escape = False
    for ch in s:
        if escape:
            buf.append(ch); escape = False; continue
        if ch == '\\':
            escape = True; continue
        if in_q:
            if ch == in_q:
                in_q = None
            else:
                buf.append(ch)
            continue
        if ch in ('"', "'"):
            in_q = ch
            continue
        if ch == ',' and len(items) == 0:
            items.append(''.join(buf).strip()); buf = []
            continue
        buf.append(ch)
    items.append(''.join(buf).strip())

    def unq(x: str) -> str:
        x = x.strip()
        if (x.startswith('"') and x.endswith('"')) or (x.startswith("'") and x.endswith("'")):
            return x[1:-1]
        return x
    a = unq(items[0]) if items else ''
    b = unq(items[1]) if len(items) > 1 else ''
    return a, b


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
    pending_first_n: Optional[int] = None
    pending_search_value: Any = None
    check_var: Optional[str] = None
    check_expected: Optional[str] = None
    set_value: Any = None       # final value for the variable being computed

def resolve_scope_text(env: ExecEnv) -> str:
    if env.pending_scope == 'taken':
        return env.current_text
    if env.pending_scope == 'first':
        n = env.pending_first_n or 0
        return env.original_text[:max(n, 0)]
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
                v = str(val_raw).strip().lower()
                env.pending_scope = 'taken' if v == 'taken' else 'all'
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
            elif key == 'add in right':
                # value might be "(所)" if parsed as kv; but in sample it's a command form add in right(所)
                env.current_text = f"{env.current_text}{val_raw}"
            elif key == 'add in left':
                env.current_text = f"{val_raw}{env.current_text}"
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
                    elif lc == 'true':
                        env.set_value = True
                    elif lc == 'false':
                        env.set_value = False
                    else:
                        env.set_value = arg
            elif key == 'check':
                env.check_var = str(val_raw).strip()
            elif key == 'has value':
                env.check_expected = str(val_raw).strip()
            else:
                # ignore unknown kv
                pass

        elif node.kind == 'command':
            cmd = node.name.strip().lower()
            # allow paren form: handled earlier; still support bare variants
            m = COMMAND_PATTERN_PARENS.match(node.name)
            arg_text = node.value if node.value is not None else (m.group('arg') if m else None)
            if cmd.startswith('add in right'):
                to_add = node.value if node.value is not None else (m.group('arg') if m else '')
                env.current_text = f"{env.current_text}{to_add}"
            elif cmd.startswith('add in left'):
                to_add = node.value if node.value is not None else (m.group('arg') if m else '')
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
                    if arg in env.stored:
                        env.set_value = env.stored[arg]
                    elif lc == 'true':
                        env.set_value = True
                    elif lc == 'false':
                        env.set_value = False
                    else:
                        env.set_value = arg
            elif cmd == 'remove whitespaces':
                env.current_text = env.current_text.strip()
            elif cmd.startswith('replace'):
                raw = node.value if node.value is not None else (m.group('arg') if m else '')
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
                ok = (val == env.check_expected) if env.check_expected is not None else bool(val)
                if ok:
                    eval_nodes(node.children, env, var_name)
            elif bname == 'if false':
                val = env.outputs.get(env.check_var)
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
        value = _strip_page_markers(value).strip()
        
    global_env.outputs[var_name] = value

def _build_page_spans(text: str):
    """
    Scan [[PAGE_START N]] markers and build a list of (page_no:int, start_index:int).
    """
    spans = []
    for m in re.finditer(r"\[\[PAGE_START\s+(\d+)\]\]", text):
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
    row = [source_name] + [(outputs.get(h, "") if outputs.get(h, "") is not None else "") for h in headers]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(full_headers)
        w.writerow(row)


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

    var_order = []
    for name in base_vars:
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

        summary_rows = []  # NEW: keep all rows for this folder

        # process all .txt files (non-recursive)
        for fname in sorted(os.listdir(in_dir)):
            if not fname.lower().endswith(".txt"):
                continue
            fpath = os.path.join(in_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                text = f.read()
            outputs = run(script_text, text)
            base = os.path.splitext(fname)[0]
            out_path = os.path.join(out_dir, base + ".csv")
            _write_csv(out_path, var_order, outputs, source_name=fname)

            # build row for summary (same shape as per-file CSV)
            row = [fname] + [
                (outputs.get(h, "") if outputs.get(h, "") is not None else "")
                for h in var_order
            ]
            summary_rows.append(row)
            
            # NEW: write folder/bureau-wise summary CSV
        if summary_rows:
            bureau_name = os.path.basename(os.path.normpath(in_dir))
            summary_path = os.path.join(out_dir, f"{bureau_name}_summary.csv")
            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
            with open(summary_path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(['file name'] + var_order)
                w.writerows(summary_rows)
        return

 # --- Single-file mode ---
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            input_text = f.read()
        outputs = run(script_text, input_text)
        # If outdir is provided, write one CSV for this file; else keep old behavior
        if args.outdir:
            base = os.path.splitext(os.path.basename(args.input))[0]
            out_path = os.path.join(args.outdir, base + ".csv")
            src_name = os.path.basename(args.input)
            _write_csv(out_path, var_order, outputs, source_name=src_name)
        else:
            if args.json:
                print(json.dumps(outputs, ensure_ascii=False, indent=2))
            else:
                for k, v in outputs.items():
                    print(f"{k}: {v}")
        return

    raise SystemExit("Provide either --input or --input_dir")

if __name__ == "__main__":
    main()
