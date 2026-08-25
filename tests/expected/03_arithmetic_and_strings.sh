#!/usr/bin/env bash
# Converted from a Windows batch file by bat2sh.
set -o pipefail
shopt -s nocasematch   # emulate "if /i" case-insensitive compares

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

# choice: emulate the batch CHOICE command
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
        :  # echo off
        PC=1
        ;;
    1)
        # arithmetic and string manipulation
        PC=2
        ;;
    2)
        (( A=10 ))
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        (( B=3 ))
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        (( SUM=A+B ))
        ERRORLEVEL=$?
        PC=5
        ;;
    5)
        (( PROD=A*B ))
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        echo A=${A} B=${B} SUM=${SUM} PROD=${PROD}
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        STR="HelloWorldBatch"
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        echo First5=${STR:0:5}
        ERRORLEVEL=$?
        PC=9
        ;;
    9)
        echo From6=${STR:5}
        ERRORLEVEL=$?
        PC=10
        ;;
    10)
        echo "Last4=${STR:$(( ( ${#STR} -4 ) < 0 ? 0 : ( ${#STR} -4 ) ))}"
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        N="42"
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        echo "Padded=${N:$(( ( ${#N} -5 ) < 0 ? 0 : ( ${#N} -5 ) ))}"
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        echo Arg1=${ARGS[0]}
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        echo AllArgs="${ARGS[@]}"
        ERRORLEVEL=$?
        PC=15
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
