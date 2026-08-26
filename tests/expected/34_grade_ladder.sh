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


# subroutine: Grade
sub_grade() {
    SCORE="${ARGS[0]}"
    ERRORLEVEL=$?
    if [ "${SCORE}" -ge "90" ]; then
        echo "${SCORE} -> A"
        ERRORLEVEL=$?
    else
        if [ "${SCORE}" -ge "80" ]; then
            echo "${SCORE} -> B"
            ERRORLEVEL=$?
        else
            if [ "${SCORE}" -ge "70" ]; then
                echo "${SCORE} -> C"
                ERRORLEVEL=$?
            else
                if [ "${SCORE}" -ge "60" ]; then
                    echo "${SCORE} -> D"
                    ERRORLEVEL=$?
                else
                    echo "${SCORE} -> F"
                    ERRORLEVEL=$?
                fi
            fi
        fi
    fi
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
        for s in 95 82 74 61 40; do
            ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
            ARGS=($s)
            sub_grade
            if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        done
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        PC=5
        ;;
    5)
        SCORE="${ARGS[0]}"
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        if [ "${SCORE}" -ge "90" ]; then
            echo "${SCORE} -> A"
            ERRORLEVEL=$?
        else
            if [ "${SCORE}" -ge "80" ]; then
                echo "${SCORE} -> B"
                ERRORLEVEL=$?
            else
                if [ "${SCORE}" -ge "70" ]; then
                    echo "${SCORE} -> C"
                    ERRORLEVEL=$?
                else
                    if [ "${SCORE}" -ge "60" ]; then
                        echo "${SCORE} -> D"
                        ERRORLEVEL=$?
                    else
                        echo "${SCORE} -> F"
                        ERRORLEVEL=$?
                    fi
                fi
            fi
        fi
        PC=7
        ;;
    7)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=8
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
