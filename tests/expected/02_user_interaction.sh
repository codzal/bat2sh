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
        # advanced/02_user_interaction.bat
        PC=3
        ;;
    3)
        # Demonstrates interactive batch features: set /p (prompt),
        PC=4
        ;;
    4)
        # the CHOICE command and conditional branching on the result.
        PC=5
        ;;
    5)
        # Runnable on Linux after conversion (CHOICE is emulated).
        PC=6
        ;;
    6)
        # ============================================================
        PC=7
        ;;
    7)
        IFS= read -r -p "Please enter your name:" USERNAME
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        echo Welcome, ${USERNAME}!
        ERRORLEVEL=$?
        PC=9
        ;;
    9)
        choice /m "Continue with installation?"
        ERRORLEVEL=$?
        PC=10
        ;;
    10)
        if [ "$ERRORLEVEL" -ge 2 ]; then
            echo Aborted by user.
            ERRORLEVEL=$?
            if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        fi
        PC=11
        ;;
    11)
        if [ "$ERRORLEVEL" -ge 1 ]; then
            echo Proceeding with installation...
            ERRORLEVEL=$?
        fi
        PC=12
        ;;
    12)
        IFS= read -r -p "Type YES to confirm:" CONFIRM
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        if [[ "${CONFIRM}" == "YES" ]]; then
            echo Confirmed. Starting...
            ERRORLEVEL=$?
        else
            echo Not confirmed.
            ERRORLEVEL=$?
        fi
        PC=14
        ;;
    14)
        echo done
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
