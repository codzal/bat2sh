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
        PC=2
        ;;
    2)
        DIR="logs_demo"
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        mkdir -p ${DIR} 2>/dev/null
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        for i in a b c; do
            echo old >"${DIR}/app.log"
            ERRORLEVEL=$?
        done
        ERRORLEVEL=$?
        PC=5
        ;;
    5)
        N="0"
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        while IFS= read -r _line; do
            IFS='' read -ra _arr <<< "$_line" || true
            f="${_arr[0]}"
            (( N+=1 ))
            ERRORLEVEL=$?
            mv "${DIR}/$f" "${DIR}/app.${N}.log"
            ERRORLEVEL=$?
        done < <(dir /b /o-n ${DIR}/*.log)
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        ls -1 "${DIR}"
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        rm -rf "${DIR}"
        ERRORLEVEL=$?
        PC=9
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
