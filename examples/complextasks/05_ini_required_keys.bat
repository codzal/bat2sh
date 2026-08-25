@echo off
setlocal enabledelayedexpansion
set MISSING=0
for %%k in (host port user) do (
    if not defined cfg_%%k (
        echo missing key: %%k
        set /a MISSING+=1
    )
)
if %MISSING% equ 0 (echo ini OK) else (echo ini INVALID: %MISSING% problems)
exit /b %MISSING%
