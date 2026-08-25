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
        # ============================================================
        PC=2
        ;;
    2)
        # control_flow/01_if_statements.bat
        PC=3
        ;;
    3)
        # Demonstrates the many forms of the batch IF command:
        PC=4
        ;;
    4)
        # - if /i  (case-insensitive compare)
        PC=5
        ;;
    5)
        # - if not
        PC=6
        ;;
    6)
        # - if exist  (file exists)
        PC=7
        ;;
    7)
        # - if defined
        PC=8
        ;;
    8)
        # - if errorlevel N
        PC=9
        ;;
    9)
        # - numeric and string comparisons (equ/neq/gtr/lss/geq/leq)
        PC=10
        ;;
    10)
        # - else branches
        PC=11
        ;;
    11)
        # Runnable on Linux after conversion.
        PC=12
        ;;
    12)
        # ============================================================
        PC=13
        ;;
    13)
        COLOR="blue"
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        if [[ "${COLOR}" == "blue" ]]; then
            echo "Color is blue (case-insensitive match)"
            ERRORLEVEL=$?
        else
            echo Color is something else
            ERRORLEVEL=$?
        fi
        PC=15
        ;;
    15)
        FLAG="1"
        ERRORLEVEL=$?
        PC=16
        ;;
    16)
        if [[ "${FLAG}" != "0" ]]; then
            echo FLAG is not zero
            ERRORLEVEL=$?
        fi
        PC=17
        ;;
    17)
        if [[ -n "${COLOR+x}" ]]; then
            echo COLOR variable is defined
            ERRORLEVEL=$?
        fi
        PC=18
        ;;
    18)
        if [[ -e "01_if_statements.bat" ]]; then
            echo This script file exists
            ERRORLEVEL=$?
        fi
        PC=19
        ;;
    19)
        # errorlevel comparison (0 means success)
        PC=20
        ;;
    20)
        bash -c "exit 3"
        ERRORLEVEL=$?
        PC=21
        ;;
    21)
        if [ "$ERRORLEVEL" -ge 3 ]; then
            echo "Last command returned errorlevel >= 3"
            ERRORLEVEL=$?
        else
            echo Unexpected errorlevel
            ERRORLEVEL=$?
        fi
        PC=22
        ;;
    22)
        (( NUM=10 ))
        ERRORLEVEL=$?
        PC=23
        ;;
    23)
        if [ "${NUM}" -gt "5" ]; then
            if [ "${NUM}" -le "20" ]; then
                echo NUM is between 5 and 20
                ERRORLEVEL=$?
            fi
        fi
        PC=24
        ;;
    24)
        if [[ "${NUM}" == "10" ]]; then
            echo NUM equals ten
            ERRORLEVEL=$?
        fi
        PC=25
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
