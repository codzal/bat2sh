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


# case-insensitive replace (batch semantics):
ci_replace() {
    local __d="$1" __s="$2" __f="$3" __r="$4" __t __u __l
    [ -z "$__f" ] && return 0
    __u="${__f^^}" __l="${__f,,}"
    __t="${!__s//"$__u"/$__r}"
    printf -v "$__d" '%s' "${__t//"$__l"/$__r}"
}

# subroutine: Touppercase
sub_touppercase() {
    :  # setlocal
    string="${ARGS[1]}"
    ERRORLEVEL=$?
    for a in A B C D E F G H I J K L M N O P Q R S T U V W X Y Z; do
        ci_replace string string "$a" "$a"
        ERRORLEVEL=$?
    done
    ERRORLEVEL=$?
    :  # endlocal
    printf -v "${ARGS[0]}" '%s' "${string}"
    ERRORLEVEL=$?
    return
    ERRORLEVEL=$?
}

dispatch() {
    case $PC in    0)
        :  # echo off
        PC=1
        ;;
    1)
        :  # setlocal
        PC=2
        ;;
    2)
        my_string="Hello, world!"
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        echo Before: ${my_string}
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(my_string "hello, batch world")
        sub_touppercase
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=5
        ;;
    5)
        echo After: ${my_string}
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        read -n1 -r -p "Press any key to continue . . . " || true; echo
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        PC=9
        ;;
    9)
        :  # setlocal
        PC=10
        ;;
    10)
        string="${ARGS[1]}"
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        for a in A B C D E F G H I J K L M N O P Q R S T U V W X Y Z; do
            ci_replace string string "$a" "$a"
            ERRORLEVEL=$?
        done
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        :  # endlocal
        PC=13
        ;;
    13)
        printf -v "${ARGS[0]}" '%s' "${string}"
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=15
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
