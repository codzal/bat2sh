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


# subroutine: Report
sub_report() {
    echo Created ${ARGS[0]} files in the build directory.
    ERRORLEVEL=$?
    return
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
        # advanced/01_project_build.bat
        PC=3
        ;;
    3)
        # A small "build" script combining many features: arguments,
        PC=4
        ;;
    4)
        # variables, if/else, a for /l loop, a subroutine call and
        PC=5
        ;;
    5)
        # file operations. Runnable on Linux after conversion.
        PC=6
        ;;
    6)
        PC=7
        ;;
    7)
        # Usage: 01_project_build.sh [project name]
        PC=8
        ;;
    8)
        # ============================================================
        PC=9
        ;;
    9)
        PC=10
        ;;
    10)
        PROJECT="${ARGS[0]}"
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        if [[ "${PROJECT}" == "" ]]; then
            PROJECT="demo"
            ERRORLEVEL=$?
        fi
        PC=12
        ;;
    12)
        echo Building project: ${PROJECT}
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        mkdir -p build 2>/dev/null
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        (( FILES=0 ))
        ERRORLEVEL=$?
        PC=15
        ;;
    15)
        for ((n=1; n<=3; n+=1)); do
            echo // generated file $n >"build/${PROJECT}_$n.txt"
            ERRORLEVEL=$?
            (( FILES=FILES + 1 ))
            ERRORLEVEL=$?
        done
        ERRORLEVEL=$?
        PC=16
        ;;
    16)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(${FILES})
        sub_report
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=17
        ;;
    17)
        echo Build finished.
        ERRORLEVEL=$?
        PC=18
        ;;
    18)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ;;
    19)
        PC=20
        ;;
    20)
        echo Created ${ARGS[0]} files in the build directory.
        ERRORLEVEL=$?
        PC=21
        ;;
    21)
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
