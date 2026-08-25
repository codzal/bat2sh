@echo off
rem ============================================================
rem  advanced/02_user_interaction.bat
rem  Demonstrates interactive batch features: set /p (prompt),
rem  the CHOICE command and conditional branching on the result.
rem  Runnable on Linux after conversion (CHOICE is emulated).
rem ============================================================

set /p USERNAME=Please enter your name: 
echo Welcome, %USERNAME%!

choice /m "Continue with installation?"
if errorlevel 2 (
    echo Aborted by user.
    goto :eof
)
if errorlevel 1 (
    echo Proceeding with installation...
)

set /p CONFIRM=Type YES to confirm: 
if /i "%CONFIRM%"=="YES" (
    echo Confirmed. Starting...
) else (
    echo Not confirmed.
)
echo done
