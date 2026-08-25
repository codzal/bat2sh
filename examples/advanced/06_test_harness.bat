@echo off
setlocal enabledelayedexpansion

set "TEST_TOTAL=0"
set "TEST_PASSED=0"

echo ===================================================
echo  RUNNING COMPLEX TEST HARNESS
echo ===================================================

set "TESTRUN_1=test_math_overflow"
set "TESTRUN_2=test_string_parsing"
set "TEST_COUNT=2"

for /L %%i in (1,1,%TEST_COUNT%) do (
    set /a TEST_TOTAL+=1
    set "CURRENT_TEST=!TESTRUN_%%i!"
    echo [RUN] !CURRENT_TEST!...
    call :!CURRENT_TEST!
    if !ERRORLEVEL! equ 0 (
        echo [OK]  !CURRENT_TEST! passed.
        set /a TEST_PASSED+=1
    ) else (
        echo [FAIL] !CURRENT_TEST! failed with error !ERRORLEVEL!.
    )
)

echo ===================================================
echo  RESULTS: %TEST_PASSED% of %TEST_TOTAL% tests passed.
echo ===================================================
if %TEST_PASSED% neq %TEST_TOTAL% exit /b 1
exit /b 0

:test_math_overflow
set /a "max_int=2147483647"
set /a "overflow_test=max_int + 1" 2>nul
if %overflow_test% equ -2147483648 (
    exit /b 0
) else (
    exit /b 1
)

:test_string_parsing
set "STR_INPUT=  Core_Component_v1.4.2_Build99  "
for /f "tokens=2 delims=_" %%a in ("%STR_INPUT%") do set "RESULT=%%a"
if "!RESULT!"=="Component" (
    exit /b 0
) else (
    exit /b 2
)
