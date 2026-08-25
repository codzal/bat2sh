@echo off
setlocal enabledelayedexpansion
set TRY=0
:again
set /a TRY+=1
echo attempt !TRY! ...
if %TRY% lss 3 (
    timeout /t 1 >nul
    goto again
)
echo done after !TRY! tries
