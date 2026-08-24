@echo off
for /l %%i in (1,1,3) do (
    echo outer %%i
    for /l %%j in (1,1,2) do (
        if %%j==2 ( echo inner %%i.%%j is two ) else ( echo inner %%i.%%j )
    )
)
call :addupto 5
echo after-call
goto :eof

:addupto
set /a TOTAL=%1*2
echo %1 doubled is %TOTAL%
goto :eof
