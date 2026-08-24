@echo off
rem ============================================================
rem  control_flow/03_goto_and_subroutines.bat
rem  Demonstrates GOTO (including jumping out of a loop) and
rem  CALL subroutines that receive and shift arguments.
rem  Runnable on Linux after conversion.
rem ============================================================

call :greet Alice Bob
echo Back in main routine.

rem GOTO can jump out of a FOR loop entirely:
for %%n in (1 2 3 4 5) do (
    if %%n equ 3 goto :escaped
    echo processing %%n
)
echo THIS LINE SHOULD NOT PRINT
:escaped
echo Jumped out of the loop at 3.

goto :eof

:greet
echo Hello %1 and %2
shift
echo After shift, first arg is now %1
goto :eof
