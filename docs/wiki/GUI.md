# GUI

```bash
python3 frontend.py
```

The window is built around a live dual-pane preview: batch on the left,
translated script on the right, synchronized scrolling, keyword and
comment highlighting. Everything else orbits it.

## Input and output

* **Input** - type a path, use *Browse File… / Browse Folder…*, or simply
  drag `.bat`/`.cmd` files onto the window (needs `tkinterdnd2`; the app
  works without it).
* **Output modes** - write beside the input (`name.sh`), pick an exact
  file, choose an output directory, or stay in *preview only*.
  With `--target ps1` selected, generated names and the Save dialog
  switch to `.ps1`.
* *Don't overwrite existing (-C)* refuses to replace files that are
  already there.

## Conversion options

| Control | What it does |
|---|---|
| Script language | bash or PowerShell 7 (`--target=ps1`, beta) |
| Paths: Pure Bash / WSL / Wine | how `C:\…` is rewritten |
| Syntax-check only (-c) | validate, write nothing |
| set -euo pipefail | strict mode for the generated script |
| Shebang | override the default `#!/usr/bin/env bash` |
| Audit (--analyze) | Windows-only calls report, shown under the preview |
| Runtime layer | errorlevel + drive-symlink helpers injected |
| Encoding | auto-detect or force (`cp1251`, …) |

## Run button

**Run** (Ctrl+R, also in the Run menu) converts the current input in
memory and executes it immediately - via `bash`, or `pwsh` when the
target language is ps1. The script itself is never written to disk;
output appears under the source, and the status bar shows the exit code.

## Little comforts

* Hover any non-obvious checkbox for a plain-language hint (English and
  Russian packs both carry them). Hints hide when you open a menu or
  switch away from the window - they never float above other apps.
* Menu **Help → Wiki (online)** opens this wiki.
* Menu **Language** switches EN/RU; other packs load from
  `languages/*.txt` ([[Language Packs]]) and may be incomplete.
* Folder conversions show per-file progress; background errors surface
  as dialogs (tkinter → kdialog → zenity → stderr).
