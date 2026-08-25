@echo off
setlocal enabledelayedexpansion

echo Starting deep search for log files...
echo ----------------------------------------
call :searchDir "%USERPROFILE%\Documents" "log"
echo ----------------------------------------
echo Search finished.
pause
exit /b

:searchDir
setlocal
set "target_dir=%~1"
set "extension=%~2"

if not exist "%target_dir%" exit /b

for /f "delims=" %%f in ('dir /b /a:-d "%target_dir%" 2^>nul') do (
    set "filename=%%f"
    if /i "!filename:~-3!"=="%extension%" (
        echo Found: %target_dir%\%%f
    )
)

for /f "delims=" %%d in ('dir /b /a:d "%target_dir%" 2^>nul') do (
    call :searchDir "%target_dir%\%%d" "%extension%"
)

endlocal
exit /b
