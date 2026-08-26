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
        mkdir -p tree/d1/d2 2>/dev/null
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        echo  1>"tree/f1.txt"
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        echo 2 2>"tree/d1/f2.txt"
        ERRORLEVEL=$?
        PC=5
        ;;
    5)
        echo 33 3>"tree/d1/d2/f3.txt"
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        FILES="0"
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        while IFS= read -r -d '' _fr; do
            F="$_fr"
            (( FILES+=1 ))
            ERRORLEVEL=$?
        done < <(LC_ALL=C find "tree" \( -name '*' \) -type f -print0 | sort -z)
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        echo files under tree/: ${FILES}
        ERRORLEVEL=$?
        PC=9
        ;;
    9)
        rm -rf "tree"
        ERRORLEVEL=$?
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
