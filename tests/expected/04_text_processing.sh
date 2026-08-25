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
        # process lines with tokens and delims
        PC=2
        ;;
    2)
        while IFS= read -r _line; do
            IFS=, read -ra _arr <<< "$_line" || true
            a="${_arr[0]}"
            b="${_arr[1]}"
            c="${_arr[2]}"
            echo first=$a second=$b third=$c
            ERRORLEVEL=$?
        done < <(printf '%s\n' "alpha,beta,gamma")
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        _skip=1
        while IFS= read -r _line; do
            if [ $_skip -gt 0 ]; then ((_skip--)); continue; fi
            IFS=$' \t' read -ra _arr <<< "$_line" || true
            a="${_arr[1]}"
            echo skipped_tok2=$a
            ERRORLEVEL=$?
        done < <(printf '%s\n' "header" "data1 data2")
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        while IFS= read -r _line; do
            IFS=$' \t' read -r a <<< "$_line" || true
            echo got=$a
            ERRORLEVEL=$?
        done < <(echo piped line)
        ERRORLEVEL=$?
        PC=5
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
