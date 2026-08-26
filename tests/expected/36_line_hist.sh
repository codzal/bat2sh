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


# subroutine: Bucket
sub_bucket() {
    L="${ARGS[0]}"
    ERRORLEVEL=$?
    (( SIZE=0 ))
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
        DATA="aa bbbbb ccccccccc dd"
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        for l in ${DATA}; do
            ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
            ARGS=($l)
            sub_bucket
            if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        done
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=5
        ;;
    5)
        PC=6
        ;;
    6)
        L="${ARGS[0]}"
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        (( SIZE=0 ))
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        PC=9
        ;;
    9)
        if [[ -n "${L+x}" ]]; then
            L="${L:1}"
            ERRORLEVEL=$?
            (( SIZE+=1 ))
            ERRORLEVEL=$?
            PC=8; return
        fi
        PC=10
        ;;
    10)
        if [ "${SIZE}" -ge "5" ]; then
            echo long: ${SIZE}
            ERRORLEVEL=$?
        else
            echo short: ${SIZE}
            ERRORLEVEL=$?
        fi
        PC=11
        ;;
    11)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=12
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
