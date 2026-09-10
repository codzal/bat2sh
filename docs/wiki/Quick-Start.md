# Quick Start

Grab the repo and convert something real in under a minute:

```bash
git clone https://github.com/codzal/bat2sh.git
cd bat2sh

python3 -m bat2sh examples/basics/01_hello_world.bat
```

You should see a complete bash script on stdout - shebang, helper
functions, and the translated `echo` lines. Nothing was written to disk;
pipe it to a file when you are happy with it:

```bash
python3 -m bat2sh examples/basics/01_hello_world.bat hello.sh
bash hello.sh        # Hello, World!
```

## Everyday tasks

| Task | Command |
|---|---|
| Preview bash output | `python3 -m bat2sh script.bat` |
| Convert next to input | `python3 -m bat2sh -i script.bat` |
| Choose output name | `python3 -m bat2sh script.bat out.sh` |
| Whole folder, recursively | `python3 -m bat2sh examples/` |
| Syntax-check only | `python3 -m bat2sh -c script.bat` |
| Convert **and execute** | `python3 -m bat2sh -r script.bat` |
| PowerShell instead of bash | `python3 -m bat2sh --target=ps1 script.bat out.ps1` |
| Pipe (execute) | `cat x.bat \| python3 -m bat2sh` |
| Pipe (print bash) | `cat x.bat \| python3 -m bat2sh -` |

## Suggested workflow for an unfamiliar script

1. `--analyze script.bat` - see whether it touches the registry, services
   or Windows binaries before trusting anything.
2. `-c script.bat` - confirm the translation parses (`bash -n`).
3. Convert for real, skim the diff (`--diff` shows both side by side).
4. Run it with `-r`, or hand the `.sh` to the target machine.

Generated scripts need nothing but `bash`. Full flag list: [[CLI Reference]].
Prefer clicking? [[GUI]] does all of the above.
