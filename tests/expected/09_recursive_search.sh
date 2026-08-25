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


# subroutine: Searchdir
sub_searchdir() {
    target_dir="${ARGS[0]}"
    ERRORLEVEL=$?
    extension="${ARGS[1]}"
    ERRORLEVEL=$?
    if [[ ! -e "${target_dir}" ]]; then
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
    fi
    while IFS= read -r _line; do
        IFS='' read -ra _arr <<< "$_line" || true
        f="${_arr[0]}"
        filename="$f"
        ERRORLEVEL=$?
        if [[ "${filename:$(( ( ${#filename} -3 ) < 0 ? 0 : ( ${#filename} -3 ) ))}" == "${extension}" ]]; then
            echo Found: ${target_dir}/$f
            ERRORLEVEL=$?
        fi
    done < <(dir /b /a:-d "${target_dir}" 2>nul)
    ERRORLEVEL=$?
    while IFS= read -r _line; do
        IFS='' read -ra _arr <<< "$_line" || true
        d="${_arr[0]}"
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=("${target_dir}\$d" "${extension}")
        sub_searchdir
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
    done < <(dir /b /a:d "${target_dir}" 2>nul)
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
        echo Starting deep search for log files...
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        echo ----------------------------------------
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
        ARGS=("$HOME\Documents" "log")
        sub_searchdir
        if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        PC=5
        ;;
    5)
        echo ----------------------------------------
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        echo Search finished.
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        read -n1 -r -p "Press any key to continue . . . " || true; echo
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=9
        ;;
    9)
        PC=10
        ;;
    10)
        PC=11
        ;;
    11)
        target_dir="${ARGS[0]}"
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        extension="${ARGS[1]}"
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        if [[ ! -e "${target_dir}" ]]; then
            if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
            ERRORLEVEL=$?
        fi
        PC=14
        ;;
    14)
        while IFS= read -r _line; do
            IFS='' read -ra _arr <<< "$_line" || true
            f="${_arr[0]}"
            filename="$f"
            ERRORLEVEL=$?
            if [[ "${filename:$(( ( ${#filename} -3 ) < 0 ? 0 : ( ${#filename} -3 ) ))}" == "${extension}" ]]; then
                echo Found: ${target_dir}/$f
                ERRORLEVEL=$?
            fi
        done < <(dir /b /a:-d "${target_dir}" 2>nul)
        ERRORLEVEL=$?
        PC=15
        ;;
    15)
        while IFS= read -r _line; do
            IFS='' read -ra _arr <<< "$_line" || true
            d="${_arr[0]}"
            ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
            ARGS=("${target_dir}\$d" "${extension}")
            sub_searchdir
            if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
        done < <(dir /b /a:d "${target_dir}" 2>nul)
        ERRORLEVEL=$?
        PC=16
        ;;
    16)
        PC=17
        ;;
    17)
        if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
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
