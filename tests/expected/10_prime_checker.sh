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


# subroutine: Isprime
sub_isprime() {
    (( N=${ARGS[0]}, I=2 ))
    ERRORLEVEL=$?
}

dispatch() {
    case $PC in    0)
        PC=1
        ;;
    1)
        PC=2
        ;;
    2)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(13)
        sub_isprime
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=3
        ;;
    3)
        if [[ "${ERRORLEVEL}" == "0" ]]; then
            echo 13 is prime
            ERRORLEVEL=$?
        else
            echo 13 not prime
            ERRORLEVEL=$?
        fi
        PC=4
        ;;
    4)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(15)
        sub_isprime
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=5
        ;;
    5)
        if [[ "${ERRORLEVEL}" == "0" ]]; then
            echo 15 is prime
            ERRORLEVEL=$?
        else
            echo 15 not prime
            ERRORLEVEL=$?
        fi
        PC=6
        ;;
    6)
        ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        PC=8
        ;;
    8)
        (( N=${ARGS[0]}, I=2 ))
        ERRORLEVEL=$?
        PC=9
        ;;
    9)
        PC=10
        ;;
    10)
        (( R=N%%I ))
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        if [[ "${R}" == "0" ]]; then
            ERRORLEVEL=1; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
            ERRORLEVEL=$?
        fi
        PC=12
        ;;
    12)
        (( I+=1 ))
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        (( SQ=I*I ))
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        if [ "${SQ}" -le "${N}" ]; then
            PC=9; return
        fi
        PC=15
        ;;
    15)
        ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=16
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
