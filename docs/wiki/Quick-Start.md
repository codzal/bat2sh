# Quick Start

| Task | Command |
|---|---|
| Preview bash output | `python3 -m bat2sh script.bat` |
| Convert next to input | `python3 -m bat2sh -i script.bat` |
| Choose output name | `python3 -m bat2sh script.bat out.sh` |
| Folder mode, file target | `python3 -m bat2sh script.bat -o out.sh` |
| Whole folder recursively | `python3 -m bat2sh examples/` |
| Syntax-check only | `python3 -m bat2sh -c script.bat` |
| Convert **and execute** | `python3 -m bat2sh -r script.bat` |
| Pipe (execute) | `cat x.bat \| python3 -m bat2sh` |
| Pipe (print bash) | `cat x.bat \| python3 -m bat2sh -` |
| Inline content argument | `python3 -m bat2sh "$(cat x.bat)"` |

Run results with plain `bash name.sh`. Flag details: [[CLI Reference]].
