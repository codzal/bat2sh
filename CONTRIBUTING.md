# Contributing

## Flow

1. Branch from **dev** (`git switch -c feat/xyz dev`).
2. Make changes; keep the public behavior of examples stable.
3. Run local checks:

```bash
python3 -m compileall -q bat2sh frontend.py
python3.13 -m pyflakes bat2sh/*.py frontend.py   # or: pip install pyflakes
bash tests/snapshot.sh                            # update baselines only on purpose
python3 -m bat2sh -c examples/
```

4. Open a PR into **dev**. CI must be green.
5. After review, dev is merged into **master** through a PR as well —
   direct pushes to master are blocked by a repository ruleset.

## Snapshot baselines

`tests/expected/*.sh` are golden outputs. If you *intentionally* change
translator behavior, regenerate and commit them in the same PR:

```bash
for f in examples/*/*.bat; do
  python3 -m bat2sh "$f" > "tests/expected/$(basename "${f%.bat}").sh"
done
```

## Language packs (GUI)

Copy `languages/ru.txt` to `languages/<code>.txt`, translate values,
keep keys intact; optional first line `name=Native Name`.
