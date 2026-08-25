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


# subroutine: Parse_Kv
sub_parse_kv() {
    kv="${ARGS[0]}"
    ERRORLEVEL=$?
    while IFS= read -r _line; do
        IFS== read -ra _arr <<< "$_line" || true
        x="${_arr[0]}"
        _anchor="${_arr[0]:-}"
        _pre="${_line%%"${_anchor}"*}"
        _incl="${_line:${#_pre}}"
        y="${_incl#*"${_anchor}"}"
        y="${y#[=]*}"
        key="$x"
        ERRORLEVEL=$?
        val="$y"
        ERRORLEVEL=$?
        while IFS= read -r _line; do
            IFS=$' \t' read -r k <<< "$_line" || true
            key="$k"
            ERRORLEVEL=$?
        done < <(printf '%s\n' "${key}")
        ERRORLEVEL=$?
        while IFS= read -r _line; do
            IFS=$' \t' read -r v <<< "$_line" || true
            val="$v"
            ERRORLEVEL=$?
        done < <(printf '%s\n' "${val}")
        ERRORLEVEL=$?
        printf -v "config_${CURRENT_SECTION}_${key}" '%s' "${val}"
        ERRORLEVEL=$?
    done < <(printf '%s\n' "${kv}")
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
        INI_FILE="config.ini"
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        if [[ ! -e "${INI_FILE}" ]]; then
            echo Error: file ${INI_FILE} not found.
            ERRORLEVEL=$?
            ERRORLEVEL=1; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
            ERRORLEVEL=$?
        fi
        PC=4
        ;;
    4)
        echo Reading and parsing ${INI_FILE}...
        ERRORLEVEL=$?
        PC=5
        ;;
    5)
        echo ---------------------------------------------------
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        CURRENT_SECTION="default"
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        # Read the file line by line.
        PC=8
        ;;
    8)
        # usebackq lets us pass a quoted path, delims= keeps each whole line.
        PC=9
        ;;
    9)
        while IFS= read -r _line; do
            IFS='' read -ra _arr <<< "$_line" || true
            a="${_arr[0]}"
            line="$a"
            ERRORLEVEL=$?
            # Trim leading/trailing whitespace.
            while IFS= read -r _line; do
                IFS=$' \t' read -r b <<< "$_line" || true
                line="$b"
                ERRORLEVEL=$?
            done < <(printf '%s\n' "${line}")
            ERRORLEVEL=$?
            first_char="${line:0:1}"
            ERRORLEVEL=$?
            # Skip empty lines and comments (; or #).
            if [[ "${line}" != "" ]]; then
                if [[ "${first_char}" != ";" ]]; then
                    if [[ "${first_char}" != "#" ]]; then
                        # Section header like [server]: strip the brackets.
                        if [[ "${first_char}" == "[" ]]; then
                            line="${line//[[]/}"
                            ERRORLEVEL=$?
                            line="${line//]/}"
                            ERRORLEVEL=$?
                            CURRENT_SECTION="${line}"
                            ERRORLEVEL=$?
                        else
                            # Otherwise it is a key=value pair.
                            ARGS_STACK+=("$(IFS=$'\x1f'; echo "${ARGS[*]}")")
                            ARGS=("${line}")
                            sub_parse_kv
                            if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi
                        fi
                    fi
                fi
            fi
        done < "${INI_FILE}"
        ERRORLEVEL=$?
        PC=10
        ;;
    10)
        echo Parsing finished successfully.
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        echo ---------------------------------------------------
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        echo Extracted variables:
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        echo ---------------------------------------------------
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        echo Server:    ${config_server_host}:${config_server_port}
        ERRORLEVEL=$?
        PC=15
        ;;
    15)
        echo SSL:       ${config_server_enable_ssl}
        ERRORLEVEL=$?
        PC=16
        ;;
    16)
        echo DB User:   ${config_database_db_user}
        ERRORLEVEL=$?
        PC=17
        ;;
    17)
        echo DB Pass:   ${config_database_db_pass}
        ERRORLEVEL=$?
        PC=18
        ;;
    18)
        read -n1 -r -p "Press any key to continue . . . " || true; echo
        ERRORLEVEL=$?
        PC=19
        ;;
    19)
        ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=20
        ;;
    20)
        # Split a key=value line at the first "=" and store it as
        PC=21
        ;;
    21)
        # config.<section>.<key> (dots become underscores in bash).
        PC=22
        ;;
    22)
        PC=23
        ;;
    23)
        kv="${ARGS[0]}"
        ERRORLEVEL=$?
        PC=24
        ;;
    24)
        while IFS= read -r _line; do
            IFS== read -ra _arr <<< "$_line" || true
            x="${_arr[0]}"
            _anchor="${_arr[0]:-}"
            _pre="${_line%%"${_anchor}"*}"
            _incl="${_line:${#_pre}}"
            y="${_incl#*"${_anchor}"}"
            y="${y#[=]*}"
            key="$x"
            ERRORLEVEL=$?
            val="$y"
            ERRORLEVEL=$?
            while IFS= read -r _line; do
                IFS=$' \t' read -r k <<< "$_line" || true
                key="$k"
                ERRORLEVEL=$?
            done < <(printf '%s\n' "${key}")
            ERRORLEVEL=$?
            while IFS= read -r _line; do
                IFS=$' \t' read -r v <<< "$_line" || true
                val="$v"
                ERRORLEVEL=$?
            done < <(printf '%s\n' "${val}")
            ERRORLEVEL=$?
            printf -v "config_${CURRENT_SECTION}_${key}" '%s' "${val}"
            ERRORLEVEL=$?
        done < <(printf '%s\n' "${kv}")
        ERRORLEVEL=$?
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
