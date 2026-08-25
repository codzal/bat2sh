@echo off
call :greet Alice
call :add 3 4
echo back in main
goto :eof

:greet
echo Hello, %1!
goto :eof

:add
set /a R=%1+%2
echo %1 + %2 = %R%
goto :eof
