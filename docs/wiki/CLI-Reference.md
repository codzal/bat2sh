# CLI Reference

```
usage: bat2sh [-h] [-i] [-o DIR|FILE.sh] [-c] [-r] [-d] [-C] [-q]
              [--encoding ENC] [--path-style {wsl,wine,root}]
              [--shebang STR] [-x] [--diff] [--strict-bash] [--analyze]
              [--report FILE] [--install-vscode-task [DIR]]
              [--runtime-layer] [--target {bash,ps1}] [-v]
              [input] [output]
```

## Core
| Flag | Action |
|---|---|
| `-i`, `--inplace` | write `<input>.sh` beside input |
| `-o DIR\|FILE.sh` | output dir (keeps tree) **or** full file path when it ends with `.sh` |
| `-c`, `--check` | `bash -n` (+shellcheck hints if installed); writes nothing |
| `-r`, `--run` | convert then execute; exit code = script exit code |
| `-d`, `--debug` | keep converter debug comments (output is clean by default) |
| `-C`, `--no-clobber` | do not overwrite existing `.sh` |
| `-q`, `--quiet` | suppress info messages |
| `--encoding ENC` | force input codec (`cp1251`, `cp866`, ...) |

## Paths & style
| Flag | Action |
|---|---|
| `--path-style wsl\|wine\|root` | `C:\x` -> `/mnt/c/x` \| `~/.wine/drive_c/x` \| `/x` |
| `--shebang STR` | interpreter line (default `#!/usr/bin/env bash`) |
| `-x`, `--executable` | chmod 0700 written files (owner only) |

## Review & hardening
| Flag | Action |
|---|---|
| `--diff` | side-by-side batch vs bash, no files written |
| `--strict-bash` | insert `set -euo pipefail` |
| `--runtime-layer` | inject `check_errorlevel()` + `/tmp/bat2sh_drives/<X>` symlinks |

## Audit
| Flag | Action |
|---|---|
| `--analyze` | report registry usage, Windows binaries (wine/native hints), services, wmic |
| `--report FILE.md\|.html` | migration report: per-file coverage + manual-attention list |

## Misc
| Flag | Action |
|---|---|
| `--target bash\|ps1` | output language; ps1 emits PowerShell 7 and names outputs `.ps1` ([[PowerShell Target beta]]) |
| `--install-vscode-task [DIR]` | write `.vscode/tasks.json`; reports detected VS Code / VSCodium installs (both read the same file) |
| `-v` / `-h` | version / help |

## stdin modes
1. no flag + pipe -> **execute**; add `-` -> print bash; add `-c` -> check.
2. No pipe and no args -> help.

## Custom command rules
`~/.config/bat2sh/config.toml`
```toml
[commands]
my_tool = "mytool-linux {args}"
backup   = "rsync -a {args}"
```
Flat `name = value` in `config.conf` also works.
