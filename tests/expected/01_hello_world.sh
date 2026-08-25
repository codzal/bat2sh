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
        # basics/01_hello_world.bat
        PC=3
        ;;
    3)
        # The simplest possible batch file. Demonstrates:
        PC=4
        ;;
    4)
        # - @echo off (suppress command echoing)
        PC=5
        ;;
    5)
        # - echo of a literal string
        PC=6
        ;;
    6)
        # - a comment with rem
        PC=7
        ;;
    7)
        # - exiting with a code
        PC=8
        ;;
    8)
        # Converts to a trivial bash script.
        PC=9
        ;;
    9)
        # ============================================================
        PC=10
        ;;
    10)
        echo Hello, World!
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        echo This batch file was converted by bat2sh.
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=13
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
