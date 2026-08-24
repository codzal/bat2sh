# bat2sh — Windows Batch to Shell Converter

`bat2sh` translates Windows batch (`.bat` / `.cmd`) scripts into POSIX
`bash` scripts. It is a best-effort, block-oriented translator that handles
the constructs most real-world batch files use, so the generated `.sh`
files can be run on Linux / macOS / WSL with little or no manual tweaking.

```
batch (Windows)  ──►  bash (Linux / macOS / WSL)
```

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
  `lss`/`leq`), `else` branches, `for`, `for /l`, `for /f` (with `tokens=`,
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
* **Robust input** — UTF-8 (with or without BOM) and UTF-16 batch files
  are decoded automatically.

---

## Requirements

* Python 3.6+
* `bash` (for the generated scripts and the `-c` syntax check)
* `tkinter` (only for the optional GUI)

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
* Some constructs have no exact POSIX equivalent and are approximated
  (`start` is mapped to a background `nohup … &`; `color`/`mode` are no-ops).
* The body of `for /f "…"` and `cmd /c "…"` is executed as a shell command
  rather than recursively re-parsed as batch.
* `for /r` (recursive directory walk) and a few very rare commands are not
  yet modelled.

Patches and example batch files that expose missing behaviour are welcome.

---

## License

Released under the [MIT License](LICENSE).
