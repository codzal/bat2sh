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


# subroutine: Greet
sub_greet() {
    echo Hello ${ARGS[0]} and ${ARGS[1]}
    ERRORLEVEL=$?
    ARGS=("${ARGS[@]:1}")
    ERRORLEVEL=$?
    echo After shift, first arg is now ${ARGS[0]}
    ERRORLEVEL=$?
    return
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
        # control_flow/03_goto_and_subroutines.bat
        PC=3
        ;;
    3)
        # Demonstrates GOTO (including jumping out of a loop) and
        PC=4
        ;;
    4)
        # CALL subroutines that receive and shift arguments.
        PC=5
        ;;
    5)
        # Runnable on Linux after conversion.
        PC=6
        ;;
    6)
        # ============================================================
        PC=7
        ;;
    7)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(Alice Bob)
        sub_greet
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=8
        ;;
    8)
        echo Back in main routine.
        ERRORLEVEL=$?
        PC=9
        ;;
    9)
        # GOTO can jump out of a FOR loop entirely:
        PC=10
        ;;
    10)
        for n in 1 2 3 4 5; do
            if [[ "$n" == "3" ]]; then
                PC=12; return
            fi
            echo processing $n
            ERRORLEVEL=$?
        done
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        echo THIS LINE SHOULD NOT PRINT
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        PC=13
        ;;
    13)
        echo Jumped out of the loop at 3.
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ;;
    15)
        PC=16
        ;;
    16)
        echo Hello ${ARGS[0]} and ${ARGS[1]}
        ERRORLEVEL=$?
        PC=17
        ;;
    17)
        ARGS=("${ARGS[@]:1}")
        ERRORLEVEL=$?
        PC=18
        ;;
    18)
        echo After shift, first arg is now ${ARGS[0]}
        ERRORLEVEL=$?
        PC=19
        ;;
    19)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
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
