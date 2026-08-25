#!/usr/bin/env bash
# Demonstrates that bat2sh can convert an entire folder of batch files
# with a single argument (it recurses through .bat/.cmd files).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"

if [ ! -f "$ROOT/bat2sh/cli.py" ]; then
    echo "Cannot find the bat2sh package under $ROOT" >&2
    exit 1
fi

echo "Converting every .bat/.cmd file under: $HERE"
PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -m bat2sh "$HERE"

echo
echo "Generated shell scripts:"
find "$HERE" -type f -name '*.sh' | sort
