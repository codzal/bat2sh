@echo off
setlocal enabledelayedexpansion
set DIR=logs_demo
md %DIR% 2>nul
for %%i in (a b c) do echo old > %DIR%\app.log
set N=0
for /f "delims=" %%f in ('dir /b /o-n %DIR%\*.log') do (
    set /a N+=1
    ren "%DIR%\%%f" "app.!N!.log"
)
dir /b %DIR%
rd /s /q %DIR%
