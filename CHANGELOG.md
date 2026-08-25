# Changelog

All notable changes to **bat2sh** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning: [SemVer](https://semver.org/) (pre-1.0 — minor = breaking).

## [0.4] — 2026-08-25

### Added
- Stable drag & drop of `.bat/.cmd` files into the GUI
  (optional `tkinterdnd2`; graceful fallback without it).
- Cross-platform polish: native monospace font in the viewer, bash binary
  resolved through PATH with a clear message on Windows.
- `-d/--debug` keeps converter comments; output is clean by default.

### Changed
- **Breaking:** `-n/--no-debug` removed (clean output is the default).
- GUI: quiet checkbox removed; debug checkbox added instead.
- Logo aligned to the left; documentation refreshed.

### Fixed
- Generated script was not displayed in the dual-pane preview
  (geometry manager conflict inside the PanedWindow).

## [0.3] — 2026-08-25

### Added
- Compatibility audit: `--analyze` detects registry access, Windows
  binaries (with wine / native-equivalent suggestions), service management
  (`net start`, `sc`, `vssadmin`) and `wmic`; `--report out.md|out.html`
  writes a migration report with per-file translation coverage.
- PowerShell target (beta): `--target=ps1` translates common constructs
  (`%VAR%`→`$env:VAR`, `echo`→`Write-Output`, `if exist`→`Test-Path`,
  `set /a`→arithmetic, `copy/move/ren/del/type/md/cd/type/cls/pause`).
- shellcheck hints run automatically with `-c` when shellcheck is installed
  (converter-specific false positives filtered).
- Editor integration: `--install-vscode-task [DIR]` writes a VS Code task
  that converts the active `.bat` with one keypress.
- Runtime layer: `--runtime-layer` injects `check_errorlevel()` and creates
  `/tmp/bat2sh_drives/<X>` symlinks for referenced drive letters;
  `--strict-bash` inserts `set -euo pipefail`.
- Path styles: `--path-style=wsl|wine|root` (`C:\x` → `/mnt/c/x` |
  `~/.wine/drive_c/x` | `/x`).
- Windows environment variables mapped to POSIX: `%TEMP%/%TMP%`, `%USERPROFILE%`,
  `%APPDATA%`, `%LOCALAPPDATA%`, `%PROGRAMFILES%`, `%PROGRAMDATA%`,
  `%SYSTEMROOT%/%WINDIR%`, `%COMPUTERNAME%`.
- Commands emulated: `attrib ±h/r/x/s`, `icacls/cacls /grant /deny /reset`,
  `assoc`, `ftype`, `subst X: path|/d`,
  `reg add/query/delete` backed by a JSON store with virtual values from
  `/etc/os-release` (`HKLM\...\CurrentVersion\ProductName`, `ComSpec`, …).
- Network/service mappings: `netstat -ano`→`ss -tulpn`,
  `route print`→`ip route`, `nslookup h`→`dig +short h`,
  `netsh wlan show profiles`→`nmcli connection show`,
  `sc config X start= auto|demand`→`systemctl enable/disable X`,
  `sc query/start/stop`→`systemctl status/start/stop`.
- Flow fidelity: `choice /t N /d Y` (timeout + default, rc=255 on timeout),
  `start /wait` synchronous, `start "" http://…`→`xdg-open`,
  `exit /b N` propagates exit code, octal guard in `set /a`
  (`val=08+2` works), `del /s/f/q` multi-pattern,
  `rd` without `/s` → `rmdir`.
- CLI: `-r/--run` execute immediately; `-o DIR/file.sh` accepts both forms;
  `--diff` side-by-side preview; `-x/--executable`;
  `--shebang STR`; custom command rules via
  `~/.config/bat2sh/config.toml` `[commands]`.
- GUI: target presets (Pure Bash / WSL / Wine-friendly), dual-pane viewer
  (batch | bash) with synchronized scrolling and syntax highlighting,
  RU/EN interface packs loaded from `languages/*.txt`.
- Tests & CI: snapshot suite over all examples (`tests/snapshot.sh`),
  GitHub Actions (static checks, convert+`bash -n`, runtime smoke,
  snapshots, shellcheck job), Dependabot for actions.

### Fixed
- Exit codes were always 0 — now `main()` result is propagated; `exit /b N`
  sets the process exit code.
- Undefined `call :label` inside loops caused an endless dispatch loop.
- Empty `delims=` was ignored (lines were split by whitespace).
- `tokens=*` branch was unreachable; `N*` created an extra variable.
- Chained `if A if B ( … )` lost the real block body of `B`.

## [0.2] — 2026-08

### Added
- Program-counter runtime with real bash subroutines: called labels become
  functions, so `call` works inside loops and if-blocks.
- `for /r` recursive walk, `usebackq`, `delims=` empty semantics,
  `tokens=N*` / `a,N*`.
- Case-insensitive string replacement (`ci_replace` helper) matching cmd.exe.
- cmd.exe-style diagnostics: unknown commands print
  `'x' is not recognized as an internal or external command…`; missing labels
  report `The system cannot find the batch label specified - X`.
- stdin pipe without arguments converts and executes immediately.
- Error dialog windows when launched without a terminal
  (tkinter / kdialog / zenity fallback chain).
- Package layout: `bat2sh/` split into shell/parser/translator/commands/cli;
  Tkinter frontend moved to `frontend.py`.

## [0.1] — initial public version
- Core batch→bash translation: variables (incl. delayed expansion,
  substrings, replacement), control flow, redirection, common command
  mappings, program-counter dispatch output.
