@echo off
setlocal enabledelayedexpansion

set "INI_FILE=config.ini"

if not exist "%INI_FILE%" (
    echo Error: file %INI_FILE% not found.
    exit /b 1
)

echo Reading and parsing %INI_FILE%...
echo ---------------------------------------------------

set "CURRENT_SECTION=default"

rem Read the file line by line.
rem usebackq lets us pass a quoted path, delims= keeps each whole line.
for /f "usebackq delims=" %%a in ("%INI_FILE%") do (
    set "line=%%a"

    rem Trim leading/trailing whitespace.
    for /f "tokens=*" %%b in ("!line!") do set "line=%%b"

    set "first_char=!line:~0,1!"

    rem Skip empty lines and comments (; or #).
    if "!line!" neq "" if "!first_char!" neq ";" if "!first_char!" neq "#" (

        rem Section header like [server]: strip the brackets.
        if "!first_char!"=="[" (
            set "line=!line:[=!"
            set "line=!line:]=!"
            set "CURRENT_SECTION=!line!"
        ) else (
            rem Otherwise it is a key=value pair.
            call :parse_kv "!line!"
        )
    )
)

echo Parsing finished successfully.
echo ---------------------------------------------------
echo Extracted variables:
echo ---------------------------------------------------
echo Server:    !config.server.host!:!config.server.port!
echo SSL:       !config.server.enable_ssl!
echo DB User:   !config.database.db_user!
echo DB Pass:   !config.database.db_pass!

pause
exit /b 0

rem Split a key=value line at the first "=" and store it as
rem config.<section>.<key> (dots become underscores in bash).
:parse_kv
set "kv=%~1"
for /f "tokens=1* delims==" %%x in ("!kv!") do (
    set "key=%%x"
    set "val=%%y"
    for /f "tokens=*" %%k in ("!key!") do set "key=%%k"
    for /f "tokens=*" %%v in ("!val!") do set "val=%%v"
    set "config.!CURRENT_SECTION!.!key!=!val!"
)
exit /b
