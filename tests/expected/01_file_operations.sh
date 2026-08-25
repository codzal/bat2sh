#!/usr/bin/env bash
set -o pipefail
shopt -s nocasematch

CALL_STACK=()
ARGS_STACK=()
ARGS=("$@")
ERRORLEVEL=0
PC=0

# cmd.exe-style diagnostics for unknown commands
command_not_found_handle() {
    printf "'%s' is not recognized as an internal or external command,\n" "$1" >&2
    echo "operable program or batch file." >&2
    ERRORLEVEL=9009
    return 1
}

choice() {
    local opts="" prompt="" default="" t=""
    while [ $# -gt 0 ]; do
        case "$1" in
            /c:*) opts="${1#/c:}";;
            /m:*) prompt="${1#/m:} ";;
            /t:*) t="${1#/t:}";;
            /d:*) default="${1#/d:}";;
        esac
        shift
    done
    if [ -n "$t" ]; then
        read -n1 -r -t "$t" -p "$prompt" _ch || _ch=""
    else
        read -n1 -r -p "$prompt" _ch || _ch=""
    fi
    echo
    [ -z "$_ch" ] && [ -n "$default" ] && _ch="$default"
    if [ -t 0 ]; then
        IFS= read -r _rest || true
    fi
    local i
    for ((i=1; i<=${#opts}; i++)); do
        c="${opts:i-1:1}"
        if [ "$_ch" = "$c" ]; then ERRORLEVEL=$i; return; fi
    done
    ERRORLEVEL=255
}

dispatch() {
    case $PC in    0)
        PC=1
        ;;
    1)
        # ============================================================
        PC=2
        ;;
    2)
        # file_operations/01_file_operations.bat
        PC=3
        ;;
    3)
        # Demonstrates file and directory commands:
        PC=4
        ;;
    4)
        # - md / mkdir, rd / rmdir (incl. recursive /s)
        PC=5
        ;;
    5)
        # - copy, move, ren, del / erase (incl. recursive /s)
        PC=6
        ;;
    6)
        # - type (cat), redirection > and >>, nul device
        PC=7
        ;;
    7)
        # Runnable on Linux after conversion. Paths with spaces
        PC=8
        ;;
    8)
        # and Windows backslashes are handled.
        PC=9
        ;;
    9)
        # ============================================================
        PC=10
        ;;
    10)
        mkdir -p "work dir" 2>/dev/null
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        echo hello >"work dir/a.txt"
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        echo world >>"work dir/a.txt"
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        cp "work dir/a.txt" "work dir/b.txt"
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        mv "work dir/b.txt" "work dir/c.txt"
        ERRORLEVEL=$?
        PC=15
        ;;
    15)
        mv "work dir/c.txt" "work dir/d.txt"
        ERRORLEVEL=$?
        PC=16
        ;;
    16)
        cat "work dir/d.txt"
        ERRORLEVEL=$?
        PC=17
        ;;
    17)
        rm -f "work dir/a.txt"
        ERRORLEVEL=$?
        PC=18
        ;;
    18)
        rm -rf "work dir"
        ERRORLEVEL=$?
        PC=19
        ;;
    19)
        echo All file operations completed. >"/dev/null"
        ERRORLEVEL=$?
        PC=20
        ;;
    20)
        echo done
        ERRORLEVEL=$?
        PC=21
        ;;
        *) PC=-1;;
    esac
}

run() {
    while [ "$PC" -ge 0 ]; do
        dispatch
    done
}

run
exit $ERRORLEVEL
