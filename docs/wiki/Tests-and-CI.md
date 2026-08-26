# Tests and CI

## Locally
```bash
python3 -m compileall -q bat2sh frontend.py
python3.13 -m pyflakes bat2sh/*.py frontend.py   # pip install pyflakes
bash tests/snapshot.sh                            # golden files
python3 -m bat2sh -c examples/
```

## Snapshots
`tests/expected/<name>.sh` are golden outputs. Intentional translator changes
must regenerate baselines in the same PR:

```bash
for f in examples/*/*.bat; do
  python3 -m bat2sh "$f" > "tests/expected/$(basename "${f%.bat}").sh"
done
```

## GitHub Actions (.github/workflows/ci.yml)
* job **test**: compileall -> pyflakes -> convert all examples + `bash -n`
  -> runtime smoke (hello_world and ini from their own folder) -> snapshots
* job **powershell**: converts every example with `--target=ps1`, parse-checks
  all 62 outputs plus the hand-written `examples/*/ps/*.ps1` under pwsh,
  fails on any `BAT2SH WARNING` leaking into output, and runs two converted
  scripts end-to-end as a runtime smoke
* job **legacy-36**: python:3.6-slim container proves oldest support
* job **shellcheck**: lints repository shell helpers
* workflow **codeql.yml**: weekly security scanning
* workflow **release.yml**: tag `v*` -> tests -> zip -> GitHub Release with
  CHANGELOG section

Branch protection: ruleset `protect-master` on master - PR-only changes,
required checks `test` and `shellcheck`, deletions and non-fast-forward
denied.
