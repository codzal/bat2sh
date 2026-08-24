@echo off
rem ============================================================
rem  control_flow/01_if_statements.bat
rem  Demonstrates the many forms of the batch IF command:
rem   - if /i  (case-insensitive compare)
rem   - if not
rem   - if exist  (file exists)
rem   - if defined
rem   - if errorlevel N
rem   - numeric and string comparisons (equ/neq/gtr/lss/geq/leq)
rem   - else branches
rem  Runnable on Linux after conversion.
rem ============================================================

set COLOR=blue
if /i "%COLOR%"=="blue" (
    echo Color is blue (case-insensitive match)
) else (
    echo Color is something else
)

set FLAG=1
if not "%FLAG%"=="0" echo FLAG is not zero

if defined COLOR echo COLOR variable is defined

if exist "01_if_statements.bat" echo This script file exists

rem errorlevel comparison (0 means success)
cmd /c "exit 3"
if errorlevel 3 (
    echo Last command returned errorlevel >= 3
) else (
    echo Unexpected errorlevel
)

set /a NUM=10
if %NUM% gtr 5 if %NUM% leq 20 echo NUM is between 5 and 20

if %NUM% equ 10 echo NUM equals ten
