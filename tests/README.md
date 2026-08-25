# tests/

`snapshot.sh` + `expected/*.sh` - golden tests: every example is converted
and compared byte-for-byte with its baseline.

If you *intentionally* change translator behavior, regenerate the affected
baselines and include them in the same PR:

```bash
for f in ../examples/*/*.bat; do
  python3 -m bat2sh "$f" > "expected/$(basename "${f%.bat}").sh"
done
```

An unexpected diff means a regression - CI will reject it.
