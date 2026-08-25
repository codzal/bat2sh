# bat2sh/ - converter core

| Module | Responsibility |
|---|---|
| `shell.py` | string->bash primitives: variable expansion (`expand_vars`), paths (`winpath` + styles), slashes, operator/redirect splitting |
| `parser.py` | batch -> AST (if/for/goto/call/label/blocks) |
| `translator.py` | AST -> bash: PC-dispatch output, command handlers, special helpers (`ci_replace`, `REG_FUNCS`) |
| `commands.py` | WIN_COMMAND_MAP + standalone emulations (attrib, icacls, net, ...) |
| `ps1.py` | beta PowerShell translation (`--target=ps1`) |
| `audit.py` | compatibility detectors + report generator (md/html) |
| `config.py` | user rules from `~/.config/bat2sh/config.toml` |
| `cli.py` | argparse, encodings, job processing, checks, run mode |

This is internal package code - the public interface is
`python3 -m bat2sh` (see the root README). Change translator behavior only
together with the snapshot baselines in `tests/expected/`.
