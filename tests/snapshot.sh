#!/usr/bin/env bash
# Snapshot test: convert every example and compare with stored expectations.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
EXP="$HERE/expected"
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT

fail=0
for bat in "$ROOT"/examples/*/*.bat; do
    name=$(basename "${bat%.bat}")
    exp="$EXP/$name.sh"
    got="$OUT/$name.sh"
    PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" \
        python3 -m bat2sh --path-style wsl "$bat" > "$got" 2>/dev/null || {
        echo "CONVERT FAIL $name"; fail=1; continue; }
    if [ ! -f "$exp" ]; then
        echo "NEW snapshot: $name (expected file missing)"; fail=1; continue
    fi
    if ! diff -u "$exp" "$got" > /dev/null; then
        echo "DIFF $name (update: cp $got $exp)"; fail=1
    fi
done
[ $fail -eq 0 ] && echo "snapshots OK"
exit $fail
