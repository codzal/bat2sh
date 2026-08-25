#!/usr/bin/env bash
# Converted from a Windows batch file by bat2sh.
set -o pipefail
shopt -s nocasematch   # emulate "if /i" case-insensitive compares

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

# choice: emulate the batch CHOICE command
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
        :  # echo off
        PC=1
        ;;
    1)
        # ============================================================
        PC=2
        ;;
    2)
        # advanced/03_windows_paths.bat
        PC=3
        ;;
    3)
        # Demonstrates how Windows drive letters and backslashes are
        PC=4
        ;;
    4)
        # translated to POSIX paths (C:\...  ->  /mnt/c/...).
        PC=5
        ;;
    5)
        # NOTE: this example is meant to show translation only; the
        PC=6
        ;;
    6)
        # generated script references /mnt/c which does not exist on
        PC=7
        ;;
    7)
        # a typical Linux box, so run it only to inspect the output.
        PC=8
        ;;
    8)
        # ============================================================
        PC=9
        ;;
    9)
        SRC="C:/Projects/app/input.txt"
        ERRORLEVEL=$?
        PC=10
        ;;
    10)
        DST="C:/Projects/app/output.txt"
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        if [[ -e "${SRC}" ]]; then
            cp "${SRC}" "${DST}"
            ERRORLEVEL=$?
        else
            echo Source ${SRC} not found
            ERRORLEVEL=$?
        fi
        PC=12
        ;;
    12)
        # %~dp0 is the directory the script lives in
        PC=13
        ;;
    13)
        echo "Script location: "$(dirname "$0")/""
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        # backslash separators are converted automatically
        PC=15
        ;;
    15)
        mkdir -p C:/Temp/work 2>/dev/null
        ERRORLEVEL=$?
        PC=16
        ;;
    16)
        echo test >"/mnt/c/Temp/work/data.txt"
        ERRORLEVEL=$?
        PC=17
        ;;
    17)
        cat C:/Temp/work/data.txt
        ERRORLEVEL=$?
        PC=18
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
