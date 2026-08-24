@echo off
setlocal enabledelayedexpansion

set "my_string=Hello, world!"
echo Before: !my_string!

call :toUpperCase my_string "hello, batch world"

echo After: !my_string!
pause
exit /b

:toUpperCase
setlocal enabledelayedexpansion
set "string=%~2"

for %%a in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set "string=!string:%%a=%%a!"
)

endlocal & call set "%~1=%string%"
exit /b
