@echo off
setlocal enabledelayedexpansion

set "users_count=0"

call :arrayPush users "Administrator"
call :arrayPush users "Moderator"
call :arrayPush users "Guest"

echo Total elements: %users_count%
echo ----------------------------------------

call :printArray users %users_count%
pause
exit /b

:arrayPush
setlocal enabledelayedexpansion
set "array_name=%~1"
set "value=%~2"
set /a "current_index=!%array_name%_count!"

endlocal & (
    set "%array_name%_%current_index%=%value%"
    set /a "%array_name%_count+=1"
)
exit /b

:printArray
setlocal enabledelayedexpansion
set "array_name=%~1"
set /a "max_index=%~2 - 1"

for /L %%i in (0,1,%max_index%) do (
    call echo Index %%i: %%!array_name!_%%i%%
)
endlocal
exit /b
