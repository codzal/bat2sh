# Installation

## Requirements
* Python 3.6+ (3.11+ recommended for `--target=ps1` and TOML config)
* `bash` - to run converted scripts and for the `-c` check
* `tkinter` - only for the GUI (`frontend.py`)
* optional: `shellcheck`, `kdialog`/`zenity`; `pwsh` to validate
  or run `--target=ps1` output

## From source
```bash
git clone https://github.com/codzal/bat2sh.git
cd bat2sh
python3 -m bat2sh -v          # bat2sh 0.4
```

No package installation needed - run the module from the repo folder.
Alias for anywhere-access:
```bash
alias bat2sh='PYTHONPATH=/path/to/bat2sh python3 -m bat2sh'
```

## Sanity checks
```bash
python3 -m bat2sh -c examples/
bash tests/snapshot.sh
```

Editor integration:
```bash
python3 -m bat2sh --install-vscode-task .   # detects VS Code / VSCodium
```
