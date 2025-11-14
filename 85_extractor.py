
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight, end-user-editable rule runner for text extraction.
Usage:
  python extractor.py --rules /path/to/rules.yaml --input /path/to/input.txt

The YAML defines a list of steps (ops). Each op is a dict with at least an "op" field.
Supported ops are intentionally small and composable. End users can tweak YAML without touching Python.

Core ideas:
- There's a single mutable "text" (the current working text).
- You can create named "buffers" (copies of text) and "vars" (named strings/bools).
- You can branch with "if_var".
- You can emit outputs with "emit" (these are collected and printed at the end).

If a pattern isn't found, most ops safely no-op (they won't crash).
"""

import argparse
import sys
import yaml
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class Ctx:
    file_name: str = ""
    text: str = ""
    original_text: str = ""
    buffers: Dict[str, str] = field(default_factory=dict)
    vars: Dict[str, Any] = field(default_factory=dict)
    outputs: List[Dict[str, str]] = field(default_factory=list)


def safe_find(source: str, needle: str) -> int:
    """Return index of needle in source or -1 if not found."""
    if needle is None or needle == "":
        return -1
    return source.find(needle)


def op_print_file_info(ctx: Ctx, args: Dict[str, Any]):
    print(f"file_name: {ctx.file_name}")
    print(f"file_length: {len(ctx.original_text)}")


def op_contains(ctx: Ctx, args: Dict[str, Any]):
    """
    Check whether a given phrase exists in a scope.
    args:
      phrase: str (required)
      in: "all" (default) | "first_n"
      n: int (used when in == "first_n")
      set: str (var name to store True/False)
      echo_true: str (print this text iff True)
      echo_false: str (print this text iff False)
    """
    phrase = args.get("phrase", "")
    scope = args.get("in", "all")
    n = int(args.get("n", 0))
    target = ctx.text
    if scope == "first_n" and n > 0:
        target = target[:n]
    ok = phrase in target
    varname = args.get("set")
    if varname:
        ctx.vars[varname] = ok
    if ok and args.get("echo_true") is not None:
        print(args.get("echo_true"))
    if (not ok) and args.get("echo_false") is not None:
        print(args.get("echo_false"))


def op_len_print(ctx: Ctx, args: Dict[str, Any]):
    """Print the length of current working text."""
    print(f"current_text_length: {len(ctx.text)}")


def op_find_after(ctx: Ctx, args: Dict[str, Any]):
    """
    Slice ctx.text to everything after first occurrence of 'pattern'.
    args:
      pattern: str (required)
      into: str (optional var name to store result instead of mutating ctx.text)
    """
    pat = args.get("pattern", "")
    idx = safe_find(ctx.text, pat)
    if idx >= 0:
        result = ctx.text[idx + len(pat):]
        if "into" in args and args["into"]:
            ctx.vars[args["into"]] = result
        else:
            ctx.text = result


def op_take_before(ctx: Ctx, args: Dict[str, Any]):
    """
    Slice ctx.text to everything before first occurrence of 'pattern'.
    args:
      pattern: str (required)
      into: str (optional var name to store result instead of mutating ctx.text)
    """
    pat = args.get("pattern", "")
    idx = safe_find(ctx.text, pat)
    if idx >= 0:
        result = ctx.text[:idx]
        if "into" in args and args["into"]:
            ctx.vars[args["into"]] = result
        else:
            ctx.text = result


def op_copy(ctx: Ctx, args: Dict[str, Any]):
    """Save a named copy of the current text into buffers[name]."""
    name = args.get("as", "")
    if name:
        ctx.buffers[name] = ctx.text


def op_restore(ctx: Ctx, args: Dict[str, Any]):
    """Restore current text from buffers[name] if present."""
    name = args.get("from", "")
    if name and name in ctx.buffers:
        ctx.text = ctx.buffers[name]


def op_set_text(ctx: Ctx, args: Dict[str, Any]):
    """
    Set ctx.text from a var or a literal.
    args:
      from_var: str (preferred)
      literal: str
    """
    if "from_var" in args and args["from_var"] in ctx.vars:
        ctx.text = str(ctx.vars[args["from_var"]])
    elif "literal" in args:
        ctx.text = str(args["literal"])


def op_set_var(ctx: Ctx, args: Dict[str, Any]):
    """
    Set a variable.
    args:
      name: str
      from_text: bool (if true, copies current ctx.text)
      literal: any (else set to this literal)
    """
    name = args.get("name", "")
    if not name:
        return
    if args.get("from_text"):
        ctx.vars[name] = ctx.text
    else:
        ctx.vars[name] = args.get("literal")


def op_strip(ctx: Ctx, args: Dict[str, Any]):
    """Strip whitespace around ctx.text or a var."""
    var = args.get("var")
    if var:
        if var in ctx.vars and isinstance(ctx.vars[var], str):
            ctx.vars[var] = ctx.vars[var].strip()
    else:
        ctx.text = ctx.text.strip()


def op_compact_whitespace(ctx: Ctx, args: Dict[str, Any]):
    """
    Remove all whitespace characters from ctx.text or a var.
    If keep_spaces=True, collapses multiple spaces to one and trims ends.
    """
    keep_spaces = args.get("keep_spaces", False)
    var = args.get("var")
    import re
    def compact(s: str) -> str:
        if keep_spaces:
            # collapse runs of whitespace to single space and strip
            return re.sub(r'\s+', ' ', s).strip()
        else:
            # remove all whitespace
            return re.sub(r'\s+', '', s)

    if var:
        if var in ctx.vars and isinstance(ctx.vars[var], str):
            ctx.vars[var] = compact(ctx.vars[var])
    else:
        ctx.text = compact(ctx.text)


def op_concat(ctx: Ctx, args: Dict[str, Any]):
    """
    Concatenate prefix + (var or text) + suffix into a target var.
    args:
      target: str (required)
      prefix: str (default "")
      from_var: str (optional)
      from_text: bool (if true, uses current ctx.text)
      suffix: str (default "")
    """
    target = args.get("target")
    if not target:
        return
    prefix = args.get("prefix", "")
    suffix = args.get("suffix", "")
    payload = ""
    if args.get("from_text"):
        payload = ctx.text
    elif "from_var" in args and args["from_var"] in ctx.vars:
        payload = str(ctx.vars[args["from_var"]])
    ctx.vars[target] = f"{prefix}{payload}{suffix}"


def op_emit(ctx: Ctx, args: Dict[str, Any]):
    """
    Emit a key/value output row.
    args:
      key: str
      from_var: str (preferred)
      literal: str (fallback)
    """
    key = args.get("key", "output")
    if "from_var" in args and args["from_var"] in ctx.vars:
        val = str(ctx.vars[args["from_var"]])
    else:
        val = str(args.get("literal", ""))
    ctx.outputs.append({"key": key, "value": val})
    print(f"{key}: {val}")


def op_if_var(ctx: Ctx, args: Dict[str, Any], dispatch):
    """
    Conditional branch on a var.
    args:
      var: str (required)
      equals: any (optional)
      not_equals: any (optional)
      truthy: bool (optional)
      falsy: bool (optional)
      then: [ops]
      else: [ops]
    """
    var = args.get("var", "")
    cond_met = False
    val = ctx.vars.get(var, None)
    if "equals" in args:
        cond_met = (val == args["equals"])
    elif "not_equals" in args:
        cond_met = (val != args["not_equals"])
    elif "truthy" in args and args["truthy"]:
        cond_met = bool(val)
    elif "falsy" in args and args["falsy"]:
        cond_met = not bool(val)

    if cond_met:
        for step in args.get("then", []):
            dispatch(ctx, step)
    else:
        for step in args.get("else", []):
            dispatch(ctx, step)


# Simple dispatcher
def dispatch(ctx: Ctx, step: Dict[str, Any]):
    op = step.get("op")
    if not op:
        return
    if op == "print_file_info":
        op_print_file_info(ctx, step)
    elif op == "contains":
        op_contains(ctx, step)
    elif op == "len_print":
        op_len_print(ctx, step)
    elif op == "find_after":
        op_find_after(ctx, step)
    elif op == "take_before":
        op_take_before(ctx, step)
    elif op == "copy":
        op_copy(ctx, step)
    elif op == "restore":
        op_restore(ctx, step)
    elif op == "set_text":
        op_set_text(ctx, step)
    elif op == "set_var":
        op_set_var(ctx, step)
    elif op == "strip":
        op_strip(ctx, step)
    elif op == "compact_ws":
        op_compact_whitespace(ctx, step)
    elif op == "concat":
        op_concat(ctx, step)
    elif op == "emit":
        op_emit(ctx, step)
    elif op == "if_var":
        op_if_var(ctx, step, dispatch)
    else:
        print(f"[WARN] Unknown op: {op}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", required=True, help="YAML rules file")
    ap.add_argument("--input", required=True, help="Text file to parse (UTF-8)")
    args = ap.parse_args()

    # load input text
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # load rules
    with open(args.rules, "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f)

    ctx = Ctx(file_name=args.input, text=text, original_text=text)

    # basic intro ops (optional) from YAML
    steps = rules.get("steps", [])
    for step in steps:
        dispatch(ctx, step)

    # final pretty print (already emitted progressively)
    # Optionally dump JSON of outputs or similar.
    # For now, just end.
    return 0


if __name__ == "__main__":
    sys.exit(main())
