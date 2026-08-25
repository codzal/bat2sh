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
        VAL="7"
        ERRORLEVEL=$?
        PC=2
        ;;
    2)
        if [ "${VAL}" -gt "5" ]; then
            echo VAL is greater than 5
            ERRORLEVEL=$?
        fi
        PC=3
        ;;
    3)
        if [ "${VAL}" -lt "10" ]; then
            echo VAL is less than 10
            ERRORLEVEL=$?
        fi
        PC=4
        ;;
    4)
        if [[ -n "${VAL+x}" ]]; then
            echo VAL is defined
            ERRORLEVEL=$?
        fi
        PC=5
        ;;
    5)
        EMPTY=""
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        if [[ -z "${EMPTY+x}" ]]; then
            echo EMPTY is not defined
            ERRORLEVEL=$?
        fi
        PC=7
        ;;
    7)
        if [[ -e "does_not_exist.txt" ]]; then
            echo exists
            ERRORLEVEL=$?
        else
            echo not exists
            ERRORLEVEL=$?
        fi
        PC=8
        ;;
    8)
        bash -c "exit 2"
        ERRORLEVEL=$?
        PC=9
        ;;
    9)
        if [ "$ERRORLEVEL" -ge 2 ]; then
            echo previous errorlevel was 2
            ERRORLEVEL=$?
        fi
        PC=10
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
