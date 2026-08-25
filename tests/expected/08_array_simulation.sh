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


# subroutine: Arraypush
sub_arraypush() {
    array_name="${ARGS[0]}"
    ERRORLEVEL=$?
    value="${ARGS[1]}"
    ERRORLEVEL=$?
    # unhandled: arithmetic uses delayed/indirect expansion of a computed variable name: set /a "current_index=!%array_name%_count!"
    printf -v "${array_name}_${current_index}" '%s' "${value}"
    ERRORLEVEL=$?
    (( "${array_name}_count+=1" ))
    ERRORLEVEL=$?
    return
    ERRORLEVEL=$?
}

# subroutine: Printarray
sub_printarray() {
    array_name="${ARGS[0]}"
    ERRORLEVEL=$?
    (( "max_index=${ARGS[1]} - 1" ))
    ERRORLEVEL=$?
    for ((i=0; i<=${max_index}; i+=1)); do
        echo Index $i: %${array_name}_%${i}%
        ERRORLEVEL=$?
    done
    ERRORLEVEL=$?
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
        users_count="0"
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(users "Administrator")
        sub_arraypush
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=4
        ;;
    4)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(users "Moderator")
        sub_arraypush
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=5
        ;;
    5)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(users "Guest")
        sub_arraypush
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=6
        ;;
    6)
        echo Total elements: ${users_count}
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        echo ----------------------------------------
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=(users ${users_count})
        sub_printarray
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=9
        ;;
    9)
        read -n1 -r -p "Press any key to continue . . . " || true; echo
        ERRORLEVEL=$?
        PC=10
        ;;
    10)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        PC=12
        ;;
    12)
        PC=13
        ;;
    13)
        array_name="${ARGS[0]}"
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        value="${ARGS[1]}"
        ERRORLEVEL=$?
        PC=15
        ;;
    15)
        # unhandled: arithmetic uses delayed/indirect expansion of a computed variable name: set /a "current_index=!%array_name%_count!"
        PC=16
        ;;
    16)
        PC=17
        ;;
    17)
        printf -v "${array_name}_${current_index}" '%s' "${value}"
        ERRORLEVEL=$?
        (( "${array_name}_count+=1" ))
        ERRORLEVEL=$?
        PC=18
        ;;
    18)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=19
        ;;
    19)
        PC=20
        ;;
    20)
        PC=21
        ;;
    21)
        array_name="${ARGS[0]}"
        ERRORLEVEL=$?
        PC=22
        ;;
    22)
        (( "max_index=${ARGS[1]} - 1" ))
        ERRORLEVEL=$?
        PC=23
        ;;
    23)
        for ((i=0; i<=${max_index}; i+=1)); do
            echo Index $i: %${array_name}_%${i}%
            ERRORLEVEL=$?
        done
        ERRORLEVEL=$?
        PC=24
        ;;
    24)
        PC=25
        ;;
    25)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=26
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
