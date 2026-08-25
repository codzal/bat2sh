# bat2sh developer guide

## Run everything

```bash
# lint
python3 -m compileall -q bat2sh frontend.py
python3 -m pyflakes bat2sh/*.py frontend.py

# snapshot tests (bash output vs expected baselines)
bash tests/snapshot.sh
```

## Convert files

```bash
python3 -m bat2sh input.bat output.sh            # bash output
python3 -m bat2sh --target=ps1 input.bat out.ps1 # PowerShell (beta)
python3 -m bat2sh -r input.bat                   # convert + run via bash
```

## Snapshot baselines

Intentional translator changes require regenerating affected baselines in
the same commit; CI rejects any diff:

```bash
cd tests
for f in ../examples/*/*.bat; do
  python3 -m bat2sh "$f" > "expected/$(basename "${f%.bat}").sh"
done
```

## CI

`.github/workflows/ci.yml`: lint → test (bash -n all examples, runtime smoke,
snapshots), plus parallel jobs: powershell (converts every example with
--target=ps1 and parse-checks via pwsh `[scriptblock]::Create`, including
hand-written `examples/*/ps/*.ps1`), legacy-36 (python:3.6 container),
shellcheck.

Local pwsh parse check for one file:

```bash
pwsh -NoProfile -Command "\$null=[scriptblock]::Create((Get-Content -Raw -LiteralPath 'out/x.ps1'))"
```

## Architecture

| Module | Role |
|---|---|
| `bat2sh/parser.py` | batch → AST (if/for/goto/call/label/blocks) |
| `bat2sh/translator.py` | AST → bash, PC-dispatch output |
| `bat2sh/shell.py` | string→bash primitives: expand_vars, winpath, redirects |
| `bat2sh/commands.py` | WIN_COMMAND_MAP + emulations (attrib, net, sc, reg…) |
| `bat2sh/ps1.py` | PowerShell backend (`--target=ps1`) |
| `bat2sh/cli.py` | argparse, encodings, jobs, `-r` runner |
| `frontend.py` | tkinter GUI |

## ps1 backend notes

- Output must parse: any line with unescaped `%` becomes a warning comment;
  emit_if drops a whole if/else block when its condition keeps `%`.
- Top-level goto/goto_eof → `$__pc` switch loop (`:__loop while ($true)`),
  mirroring translator.py's PC dispatch; `goto :eof` inside subs → `return`.
- Computed set targets go through `Set-Variable` + `_name_expr`.
- `_WIN_ENV` values are full PS expressions (`$env:TMPDIR`) — never brace them.
- `_q()` braces bare `$names`; otherwise `$i:` parses as a scoped variable.
- Op splitting is quote-aware; `>&1` tokens are never split on `&`.

## Conventions

- Branches: `master` (protected, PRs only), `dev`, feature branches.
- Do not push to master directly; wait for explicit user instruction.
- UI texts default to English; `languages/ru.txt` is the only translation pack.
- Python compatibility: oldest supported is 3.6 (CI legacy job).
