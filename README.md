# bat2sh — Windows Batch to Shell Converter

**English** | [Русский](README_RU.md)

[![CI](https://github.com/codzal/bat2sh/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/codzal/bat2sh/actions/workflows/ci.yml) [![CodeQL](https://github.com/codzal/bat2sh/actions/workflows/codeql.yml/badge.svg)](https://github.com/codzal/bat2sh/security/code-scanning) ![python](https://img.shields.io/badge/python-3.6%2B-blue) [![license](https://img.shields.io/badge/license-MIT-green)](LICENSE) ![status](https://img.shields.io/badge/status-beta-orange)

## Contents

[Quick start](#quick-start) · [Features](#features) ·
[CLI reference](#command-line-usage) · [GUI](#graphical-interface) ·
[Examples](#examples) · [How it works](#how-it-works) ·
[Limitations](#limitations) · [Security](SECURITY.md) ·
[Wiki](https://github.com/codzal/bat2sh/wiki)

`bat2sh` translates Windows batch (`.bat` / `.cmd`) scripts into POSIX
`bash` scripts. It is a best-effort, block-oriented translator that handles
the constructs most real-world batch files use, so the generated `.sh`
files can be run on Linux / macOS / WSL with little or no manual tweaking.

```
batch (Windows)  ──►  bash (Linux / macOS / WSL)
```

---

> **Status: beta (v0.3).** Many commands and edge cases are still being
> implemented — audit your scripts with `--analyze` / `-c` before relying
> on the output.

## Quick start

```bash
git clone https://github.com/codzal/bat2sh.git
cd bat2sh

# convert one file, print the bash script to stdout
python3 -m bat2sh examples/basics/01_hello_world.bat

# convert in place: myscript.bat -> myscript.sh
python3 -m bat2sh -i myscript.bat

# convert a whole folder (recursively) and syntax-check every result
python3 -m bat2sh -c path/to/batch/files/

# optional graphical interface
python3 frontend.py
```

Generated scripts need nothing but `bash`: run them with `bash name.sh`.

---

## Features

* **Layout** — `bat2sh/` package (`shell` expansions, `parser`, `translator`,
  `commands` map, `cli`) with a thin Tkinter `frontend.py`.

* **Variables** — `set`, `set /a`, `set /p`, `%VAR%`, delayed `!VAR!`,
  substrings `%VAR:~0,5%` (including negative `%~-5` offsets, clamped to the
  whole string when shorter) and string replacement `%VAR:find=rep%`,
  arguments `%1`…`%9`, `%*`, `%~dp0` and other `%~` modifiers, the special
  `errorlevel` variable.
* **Control flow** — `if`, `if not`, `if /i`, `if exist`, `if defined`,
  `if errorlevel`, string and numeric comparisons (`equ`/`neq`/`gtr`/`geq`/
  `lss`/`leq`), `else` branches, `for`, `for /l`, `for /r`, `for /f` (with `tokens=`,
  `delims=`, `skip=`, and quoted-string/literal sources), **nested** `for` and
  `if` blocks, `goto` (including jumping out of loops) and `call` subroutines
  with their own argument stack.
* **Redirection & operators** — `>`, `>>`, `<`, pipes `|`, and the `&`,
  `&&`, `||` separators. The Windows `nul` device becomes `/dev/null`.
  Literal comparisons such as `>=` / `<=` inside text are preserved.
* **Common commands** — `echo`, `rem`/`::`, `@`, `cd`, `md`/`mkdir`,
  `rd`/`rmdir` (incl. `/s`), `del`/`erase` (incl. `/s`), `copy`, `move`,
  `ren`, `type`, `cls`, `pause`, `exit`, `title`, `color`, `setlocal`/
  `endlocal`, `pushd`/`popd`, `shift`, `start`, `dir`, `find`, `findstr`,
  `path`, `choice`, `cmd /c` and many standard Windows commands mapped to
  their POSIX equivalents (`tasklist`→`ps`, `xcopy`→`cp -r`, `ping`→`ping`,
  `ipconfig`→`ip`, `setx`→`export`, `timeout`→`sleep`, …).
* **Path translation** — `C:\dir\file` becomes `/mnt/c/dir/file` and
  backslashes are converted to forward slashes.
* **Audit & reports** — `--analyze` flags registry access, Windows binaries
  (`wine` or native-equivalent suggestions) and service management;
  `--report out.md|.html` writes a migration report with per-file coverage.
* **PowerShell target (beta)** — `--target=ps1` emits PowerShell instead of
  bash for common constructs.
* **shellcheck** hints run automatically with `-c` when installed.
* **Editor integration** — `--install-vscode-task [DIR]` creates a one-key
  convert task for VS Code / VSCodium.
* **Runtime layer** — `--runtime-layer` injects `check_errorlevel()` and
  `/tmp/bat2sh_drives/<X>` symlinks; `--strict-bash` inserts
  `set -euo pipefail`; `-x` marks outputs executable.
* **Custom command rules** — map your own tools in
  `~/.config/bat2sh/config.toml`:
  `[commands] my_tool = "mytool-linux {args}"`.
* **Robust input** — UTF-8 (with or without BOM) and UTF-16 batch files
  are decoded automatically.
* **cmd.exe-style diagnostics** - unknown commands print
  `'x' is not recognized as an internal or external command…`, missing
  labels report `The system cannot find the batch label specified - X`
  (`goto` stops, `call` continues), and when launched without a terminal
  (e.g. from Dolphin) errors appear in dialog windows instead of stderr.

---

## Requirements

* Python 3.6+
* `bash` (for the generated scripts and the `-c` syntax check)
* `tkinter` (only for the frontend GUI)

---

## Command-line usage

```bash
# Convert a file (output to stdout)
python3 -m bat2sh script.bat

# Write next to the input as script.sh
python3 -m bat2sh -i script.bat
python3 -m bat2sh script.bat script.sh

# Read from stdin
cat script.bat | python3 -m bat2sh -

# Convert from stdin and run immediately (nothing is saved)
cat script.bat | python3 -m bat2sh

# Convert an entire folder of .bat/.cmd files at once
python3 -m bat2sh examples/

# Only syntax-check the converted output (writes nothing)
python3 -m bat2sh -c script.bat
python3 -m bat2sh -c examples/
```

| Option | Description |
| --- | --- |
| `-i`, `--inplace` | Write `<input>.sh` beside the input file |
| `-o`, `--output-dir DIR` | Write outputs into `DIR` (mirrors the folder tree for directories; places `<name>.sh` there for a single file) |
| `-c`, `--check` | Only run `bash -n` on the result; no files written |
| `-n`, `--no-debug` | Strip converter-injected comments/placeholders; keep only comments from the original batch file |
| `-C`, `--no-clobber` | Don't overwrite existing output files |
| `-r`, `--run` | Convert and execute immediately (nothing written) |
| `--path-style {wsl,wine,root}` | Drive-letter mapping style |
| `--shebang STR` | Interpreter line for generated scripts |
| `-x`, `--executable` | chmod +x written .sh files |
| `--diff` | Show batch vs bash side by side |
| `--strict-bash` | Insert `set -euo pipefail` |
| `--analyze` / `--report FILE` | Compatibility audit / migration report |
| `--runtime-layer` | Inject errorlevel + drive-symlink helpers |
| `--target {bash,ps1}` | Output language (ps1 is beta) |
| `-q`, `--quiet` | Suppress informational messages (errors are still shown) |
| `--encoding ENC` | Force input decoding with this codec (e.g. `cp1251`, `latin-1`); default is auto-detect |
| `--version` | Print the version and exit |
| `-h`, `--help` | Show help |

When the input is a **directory**, every `.bat`/`.cmd` file found inside it
(recursively) is converted to a `.sh` file placed next to it.

---

## Graphical interface

A Tkinter GUI is provided for users who prefer point-and-click operation:

```bash
python3 frontend.py
```

It offers file/folder selection, output options (next-to-input, choose file,
output directory, or preview-only), a *syntax-check only* mode, a live preview
of the generated script, copy-to-clipboard, *Save As…*, an encoding selector,
and *no-clobber* / *quiet* toggles. A menu bar (File / Edit / Run / Help) and
keyboard shortcuts (`Ctrl+O`, `Ctrl+S`, `Ctrl+C`, `F5`) are provided.
The UI language can be switched in the **Language** menu - English is
built in, further languages ship as editable `languages/<code>.txt`
packs (e.g. `languages/ru.txt`).

> ⚠️ Non-English UI packs are community translations and may be incomplete.
> English is the reference language. The **wiki** is maintained in English only.

---

## Examples

The [`examples/`](examples/) directory contains categorized, self-contained
batch files that demonstrate (and verify) the converter's coverage:

```
examples/
  basics/         variables, echo, arguments, substrings
  control_flow/   if/else, loops, goto & subroutines
  file_operations/  md/copy/move/ren/del/rd with spaces & redirects
  advanced/       build scripts, user interaction, Windows path translation
```

Run `examples/generate_examples.sh` to convert the whole tree in one command:

```bash
bash examples/generate_examples.sh
```

---

## How it works

The converter parses the batch file into a list of statements and emits a
single `bash` script driven by a **program-counter dispatch loop**:

```bash
PC=0
dispatch() {
    case $PC in
        0)  ... ; PC=1 ;;
        1)  ... ; PC=2 ;;
        ...
    esac
}
while [ "$PC" -ge 0 ]; do dispatch; done
```

This faithfully models `goto`, including jumps that leave `for`/`if` blocks
(the `goto` simply sets `PC` and `return`s), and `call :label` subroutines
(with their own argument/`return` stack).

---

## Limitations

`bat2sh` is a translator, not an emulator. Known caveats:

* `errorlevel` reflects the status of the **last executed command**, exactly
  as in batch; if a command such as `echo` runs between the command and an
  `if errorlevel` test, the value is reset (this matches real `cmd.exe`).
* `start` strips its switches/title and runs the program in the background
  (`nohup … &`) - there is no console/session concept in POSIX.
* `color`, `mode`, `chcp` and a few other console-only commands are no-ops.
* The command source of `for /f '…'` is executed as a shell command with
  variables pre-expanded; batch-only syntax inside it is not re-parsed.
  `cmd /c other.bat` invokes the converted `other.sh` sibling.
* Computed variable names (`!prefix_%%i!`) and dynamic call labels
  (`call :!name!`) have no direct bash equivalent and stay untranslatable.

Patches and example batch files that expose missing behaviour are welcome.

---

## License

Released under the [MIT License](LICENSE).
