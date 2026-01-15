
# DSL Engine — How to use

## 1) Files
- `dsl_engine.py` — interpreter for the indentation-based DSL
- `85_script.dsl` — your example rules (editable)

## 2) Run
```bash
python dsl_engine.py --script 85_script.dsl --input your_text.txt
# Print JSON instead:
python dsl_engine.py --script 85_script.dsl --input your_text.txt --json
```

## 3) DSL recap (what the engine supports)
- **Top-level**: each unindented `X:` defines a variable to compute/print.
- **Search**
  - `search in : all | taken`
  - `search in first : N`  (search in first N chars of the whole text)
  - `search text : 文字列`  (first match is used as the anchor)
  - `search text : [A, B, C]`  (boolean check: all must appear; no anchor)
- **Branches (after a search or check)**
  - `if found : ...`
  - `if not found : ...`
  - With `check` + `has value`:
    - `if true : ...`
    - `if false : ...`
- **Slicing**
  - `take right : ...` — sets the working text to the substring **after** the last match; body runs inside that context; then the previous context is restored.
  - `take left : ...` — substring **before** the last match; same scoping behavior.
- **Mutations on working text**
  - `remove whitespaces` — trims leading/trailing whitespace
  - `add in right(XX)` / `add in left(XX)` — append/prepend text
- **Temp variables**
  - `store(varX)` — saves current working text to a temp `varX`
  - `set(varX)` — sets the top-level variable to the temp’s value
  - `set(本官)`, `set(true)`, etc. — sets literal values (true/false supported)

## 4) Cross-variable checks
- Use `check : name_of` then `has value : 本官` and next `if true:` / `if false:` blocks will branch based on previously-computed variables.

## 5) Notes
- All text matching is **literal** (no regex).
- `search in : taken` always uses the current slice from the nearest `take left/right` scope.
- Comments: any line starting with `##` (optionally indented) is ignored; inline `# ...` comments also work (outside quotes).
- The engine tolerates the typo `seach` → treats as `search`.
- If a search list `[A, B]` is used, it sets only a boolean (no anchor). To anchor for slicing, do a regular `search text : "A"` first.

If you want features like regex, earliest-of-multiple-end-markers, or N-th occurrence picking,
we can extend the DSL with `search nth : 2`, `take before any : [A, B, C]`, etc.
