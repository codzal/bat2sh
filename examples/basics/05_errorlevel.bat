@echo off
cmd /c "exit /b 5"
if errorlevel 5 echo command-failed-with-5
if errorlevel 1 echo command-failed-at-least-1
echo after-checks
