@echo off
setlocal enabledelayedexpansion
set ATTEMPTS=0
:check
set /a ATTEMPTS+=1
ping -n 1 127.0.0.1 >nul
if %ATTEMPTS% lss 3 goto check
echo watchdog finished after %ATTEMPTS% probes
