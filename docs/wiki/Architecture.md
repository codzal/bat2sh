# Architecture

```
bat2sh/
  shell.py       string->bash: expand_vars, winpath(+PATH_STYLE),
                 dos_slashes, split_top_ops/split_redir, unescape_caret
  parser.py      batch -> AST (Parser.parse_program)
  translator.py  AST -> bash: Translator.convert(), emit_node/emit_if/
                 emit_for, cmd_* handlers, WIN_COMMAND_MAP dispatch,
                 REG_FUNCS/ci_replace extras, stats
  commands.py    standalone command helpers (attrib, icacls, net, ...)
  ps1.py         beta PowerShell line translator (--target=ps1)
  audit.py       compatibility detectors + migration_report(md|html)
  config.py      user rules from ~/.config/bat2sh/config.toml
  cli.py         argparse, decode_text, _process_job/_check, analyze/report
frontend.py      Tkinter GUI
languages/ru.txt GUI language pack
```

## Output model (PC dispatch)
Statements are numbered; each becomes a `case $PC` arm:
```bash
PC=0
dispatch() { case $PC in
  0) ...; PC=1 ;;
esac }
while [ "$PC" -ge 0 ]; do dispatch; done
exit $ERRORLEVEL
```
`goto X` = `PC=N; return`. Labels that are only ever **called** become real
bash functions (`sub_*`) - a plain call does not abandon enclosing loops the
way a PC jump would. `ARGS` is saved/restored around calls.

## Line pipeline
`translate_segment`: strip/@ -> nul rewrite -> rem/:: -> goto -> reg/sc ->
`self._cmd` dict -> WIN_COMMAND_MAP -> user rules (config) -> passthrough
(`expand_vars`) incrementing fallback stats.

## Variable expansion (`shell.expand_vars`, lru_cache)
Order matters: `%VAR:f=r%` -> `%VAR:~s,l%` -> `%~dpN` -> args -> errorlevel
-> `%VAR%` (dot-sanitize + WIN_ENV table) -> `%%` -> `!...!` forms.
Replacement patterns are escaped using backslash-free glob classes so
`dos_slashes` cannot corrupt them; loop-variable replacements go through the
runtime helper `ci_replace`.

## for /f
`read -ra _arr` with `IFS=<delims>`; rest variables are cut from the original
line via `_anchor/_pre/_incl` preserving inner delimiters; empty `delims=`
disables splitting; `tokens=*` trims the whole line.

## Extension points
* new CLI flag -> `_argparser()` + handling in `main`/`_process_job`
* new command -> `cmd_*` method + entry in `Translator._cmd` or map
* runtime helper -> block appended via `extras` (see REG_FUNCS/ci_helper)
