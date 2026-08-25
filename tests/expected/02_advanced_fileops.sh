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
        DIR="workdir"
        ERRORLEVEL=$?
        PC=2
        ;;
    2)
        mkdir -p ${DIR}
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        echo line one >"${DIR}/a.txt"
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        echo line two >"${DIR}/b.txt"
        ERRORLEVEL=$?
        PC=5
        ;;
    5)
        cp "${DIR}/a.txt" "${DIR}/c.txt"
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        mv "${DIR}/b.txt" "${DIR}/b_moved.txt"
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        mv "${DIR}/c.txt" "${DIR}/c_renamed.txt"
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        ls "${DIR}"
        ERRORLEVEL=$?
        PC=9
        ;;
    9)
        rm -f "${DIR}/a.txt"
        ERRORLEVEL=$?
        PC=10
        ;;
    10)
        rm -rf "${DIR}"
        ERRORLEVEL=$?
        PC=11
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
