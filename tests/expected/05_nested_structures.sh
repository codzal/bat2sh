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


# subroutine: Addupto
sub_addupto() {
    (( TOTAL=${ARGS[0]}*2 ))
    ERRORLEVEL=$?
    echo ${ARGS[0]} doubled is ${TOTAL}
    ERRORLEVEL=$?
    return
}

dispatch() {
    case $PC in    0)
        PC=1
        ;;
    1)
        for ((i=1; i<=3; i+=1)); do
            echo outer $i
            ERRORLEVEL=$?
            for ((j=1; j<=2; j+=1)); do
                if [[ "$j" == "2" ]]; then
                    echo inner %${i_}%j is two
                    ERRORLEVEL=$?
                else
                    echo inner %${i_}%j
                    ERRORLEVEL=$?
                fi
            done
            ERRORLEVEL=$?
        done
        ERRORLEVEL=$?
        PC=2
        ;;
    2)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(5)
        sub_addupto
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=3
        ;;
    3)
        echo after-call
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ;;
    5)
        PC=6
        ;;
    6)
        (( TOTAL=${ARGS[0]}*2 ))
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        echo ${ARGS[0]} doubled is ${TOTAL}
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
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
