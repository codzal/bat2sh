@echo off
setlocal enabledelayedexpansion
for /l %%i in (1,1,15) do (
    set /a M3=%%i %% 3, M5=%%i %% 5
    set OUT=%%i
    if !M3! equ 0 set OUT=Fizz
    if !M5! equ 0 set OUT=!OUT!Buzz
    echo !OUT!
)
