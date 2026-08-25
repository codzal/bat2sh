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


# subroutine: Strlen
sub_strlen() {
    (( ${ARGS[1]}=0 ))
    ERRORLEVEL=$?
    for c in a b c d e f g h i j k l m n o p q r s t u v w x y z; do
        if [[ "!${ARGS[0]}:$c=!" != "!${ARGS[0]}!" ]]; then
            (( ${ARGS[1]}+=1 ))
            ERRORLEVEL=$?
        fi
    done
    ERRORLEVEL=$?
    return
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
        W1="listened"
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        W2="silent"
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(W1 L1)
        sub_strlen
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=5
        ;;
    5)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(W2 L2)
        sub_strlen
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=6
        ;;
    6)
        if [[ "${L1}" == "${L2}" ]]; then
            echo same length ${L1} - possible anagram
            ERRORLEVEL=$?
        else
            echo different lengths
            ERRORLEVEL=$?
        fi
        PC=7
        ;;
    7)
        ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        PC=9
        ;;
    9)
        (( ${ARGS[1]}=0 ))
        ERRORLEVEL=$?
        PC=10
        ;;
    10)
        for c in a b c d e f g h i j k l m n o p q r s t u v w x y z; do
            if [[ "!${ARGS[0]}:$c=!" != "!${ARGS[0]}!" ]]; then
                (( ${ARGS[1]}+=1 ))
                ERRORLEVEL=$?
            fi
        done
        ERRORLEVEL=$?
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
