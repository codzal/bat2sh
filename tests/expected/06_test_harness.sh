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
        TEST_TOTAL="0"
        ERRORLEVEL=$?
        PC=3
        ;;
    3)
        TEST_PASSED="0"
        ERRORLEVEL=$?
        PC=4
        ;;
    4)
        echo ===================================================
        ERRORLEVEL=$?
        PC=5
        ;;
    5)
        echo RUNNING COMPLEX TEST HARNESS
        ERRORLEVEL=$?
        PC=6
        ;;
    6)
        echo ===================================================
        ERRORLEVEL=$?
        PC=7
        ;;
    7)
        TESTRUN_1="test_math_overflow"
        ERRORLEVEL=$?
        PC=8
        ;;
    8)
        TESTRUN_2="test_string_parsing"
        ERRORLEVEL=$?
        PC=9
        ;;
    9)
        TEST_COUNT="2"
        ERRORLEVEL=$?
        PC=10
        ;;
    10)
        for ((i=1; i<=${TEST_COUNT}; i+=1)); do
            (( TEST_TOTAL+=1 ))
            ERRORLEVEL=$?
            CURRENT_TEST="!TESTRUN_$i!"
            ERRORLEVEL=$?
            echo [RUN] ${CURRENT_TEST}...
            ERRORLEVEL=$?
            { echo "The system cannot find the batch label specified - !CURRENT_TEST!" >&2; ERRORLEVEL=1; false; }
            if [[ "${ERRORLEVEL}" == "0" ]]; then
                echo [OK]  ${CURRENT_TEST} passed.
                ERRORLEVEL=$?
                (( TEST_PASSED+=1 ))
                ERRORLEVEL=$?
            else
                echo [FAIL] ${CURRENT_TEST} failed with error ${ERRORLEVEL}.
                ERRORLEVEL=$?
            fi
        done
        ERRORLEVEL=$?
        PC=11
        ;;
    11)
        echo ===================================================
        ERRORLEVEL=$?
        PC=12
        ;;
    12)
        echo RESULTS: ${TEST_PASSED} of ${TEST_TOTAL} tests passed.
        ERRORLEVEL=$?
        PC=13
        ;;
    13)
        echo ===================================================
        ERRORLEVEL=$?
        PC=14
        ;;
    14)
        if [[ "${TEST_PASSED}" != "${TEST_TOTAL}" ]]; then
            ERRORLEVEL=1; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
            ERRORLEVEL=$?
        fi
        PC=15
        ;;
    15)
        ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
        ERRORLEVEL=$?
        PC=16
        ;;
    16)
        PC=17
        ;;
    17)
        (( "max_int=2147483647" ))
        ERRORLEVEL=$?
        PC=18
        ;;
    18)
        (( "overflow_test=max_int + 1" )) 2>"/dev/null"
        ERRORLEVEL=$?
        PC=19
        ;;
    19)
        if [[ "${overflow_test}" == "-2147483648" ]]; then
            ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
            ERRORLEVEL=$?
        else
            ERRORLEVEL=1; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
            ERRORLEVEL=$?
        fi
        PC=20
        ;;
    20)
        PC=21
        ;;
    21)
        STR_INPUT="Core_Component_v1.4.2_Build99  "
        ERRORLEVEL=$?
        PC=22
        ;;
    22)
        while IFS= read -r _line; do
            IFS=_ read -ra _arr <<< "$_line" || true
            a="${_arr[1]}"
            RESULT="$a"
            ERRORLEVEL=$?
        done < <(printf '%s\n' "${STR_INPUT}")
        ERRORLEVEL=$?
        PC=23
        ;;
    23)
        if [[ "${RESULT}" == "Component" ]]; then
            ERRORLEVEL=0; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
            ERRORLEVEL=$?
        else
            ERRORLEVEL=2; if [ ${#CALL_STACK[@]} -gt 0 ]; then PC="${CALL_STACK[-1]}"; unset "CALL_STACK[-1]"; if [ ${#ARGS_STACK[@]} -gt 0 ]; then IFS=$'\x1f' read -ra ARGS <<<"${ARGS_STACK[-1]}"; unset "ARGS_STACK[-1]"; fi; else PC=-1; fi; return
            ERRORLEVEL=$?
        fi
        PC=24
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
