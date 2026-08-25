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
        # ============================================================
        PC=2
        ;;
    2)
        # basics/02_variables.bat
        PC=3
        ;;
    3)
        # Demonstrates variable handling:
        PC=4
        ;;
    4)
        # - plain set / assignment (delayed-expansion !VAR! also supported)
        PC=5
        ;;
    5)
        # - set /a arithmetic
        PC=6
        ;;
    6)
        # - substring expansion  %VAR:~start,len%
        PC=7
        ;;
    7)
        # - positional arguments %1 %2 ... %*  and  %~dp0 (script dir)
        PC=8
        ;;
    8)
        # - the special errorlevel variable
        PC=9
        ;;
    9)
        # This example is runnable on Linux after conversion.
        PC=10
        ;;
    10)
        # ============================================================
        PC=11
        ;;
    11)
        NAME="Alice"
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        (( AGE=30 + 5 ))
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        echo Name is ${NAME} and age is ${AGE}
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        # substring of a string variable
        PC=15
        ;;
    15)
        GREETING="HelloWorld"
        ERRORLEVEL=$?
        PC=16
        ;;
    16)
        echo Substring[0:5] = ${GREETING:0:5}
        ERRORLEVEL=$?
        PC=17
        ;;
    17)
        # positional arguments (run: ./02_variables.sh Bob 42)
        PC=18
        ;;
    18)
        echo First argument : ${ARGS[0]}
        ERRORLEVEL=$?
        PC=19
        ;;
    19)
        echo All arguments  : "${ARGS[@]}"
        ERRORLEVEL=$?
        PC=20
        ;;
    20)
        # %~dp0 becomes the directory of the script
        PC=21
        ;;
    21)
        echo "Script dir     : "$(dirname "$0")/""
        ERRORLEVEL=$?
        PC=22
        ;;
    22)
        # errorlevel reflects the last command
        PC=23
        ;;
    23)
        bash -c "exit 0"
        ERRORLEVEL=$?
        PC=24
        ;;
    24)
        echo errorlevel after success = ${ERRORLEVEL}
        ERRORLEVEL=$?
        PC=25
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
