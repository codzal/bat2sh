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
        # control_flow/02_loops.bat
        PC=3
        ;;
    3)
        # Demonstrates the three FOR loop forms:
        PC=4
        ;;
    4)
        # - for %%v in (list)         iterate over a list
        PC=5
        ;;
    5)
        # - for /l %%v (start,step,end)  numeric range
        PC=6
        ;;
    6)
        # - for /f "delims=" %%v in (file/or command)  parse lines
        PC=7
        ;;
    7)
        # Runnable on Linux after conversion.
        PC=8
        ;;
    8)
        # ============================================================
        PC=9
        ;;
    9)
        echo --- iterating over a list ---
        ERRORLEVEL=$?
        PC=10
        ;;
    10)
        for f in apple banana cherry; do
            echo fruit: $f
            ERRORLEVEL=$?
        done
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        echo --- numeric range with for /l ---
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        (( TOTAL=0 ))
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        for ((n=1; n<=5; n+=1)); do
            (( TOTAL=$n + TOTAL ))
            ERRORLEVEL=$?
        done
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        echo sum 1..5 = ${TOTAL}
        ERRORLEVEL=$?
        PC=15
        ;;
    15)
        echo --- for /f over command output ---
        ERRORLEVEL=$?
        PC=16
        ;;
    16)
        while IFS= read -r _line; do
            IFS='' read -ra _arr <<< "$_line" || true
            l="${_arr[0]}"
            echo got: $l
            ERRORLEVEL=$?
        done < <(echo line one & echo line two)
        ERRORLEVEL=$?
        PC=17
        ;;
    17)
        echo --- for /f reading a file ---
        ERRORLEVEL=$?
        PC=18
        ;;
    18)
        echo first >"example.tmp"
        ERRORLEVEL=$?
        PC=19
        ;;
    19)
        echo second >>"example.tmp"
        ERRORLEVEL=$?
        PC=20
        ;;
    20)
        while IFS= read -r _line; do
            IFS='' read -ra _arr <<< "$_line" || true
            l="${_arr[0]}"
            echo file line: $l
            ERRORLEVEL=$?
        done < "example.tmp"
        ERRORLEVEL=$?
        PC=21
        ;;
    21)
        rm -f "example.tmp"
        ERRORLEVEL=$?
        PC=22
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
