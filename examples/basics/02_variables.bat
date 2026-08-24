@echo off
rem ============================================================
rem  basics/02_variables.bat
rem  Demonstrates variable handling:
rem   - plain set / assignment (delayed-expansion !VAR! also supported)
rem   - set /a arithmetic
rem   - substring expansion  %VAR:~start,len%
rem   - positional arguments %1 %2 ... %*  and  %~dp0 (script dir)
rem   - the special errorlevel variable
rem  This example is runnable on Linux after conversion.
rem ============================================================

set NAME=Alice
set /a AGE=30 + 5
echo Name is %NAME% and age is %AGE%

rem substring of a string variable
set GREETING=HelloWorld
echo Substring[0:5] = %GREETING:~0,5%

rem positional arguments (run: ./02_variables.sh Bob 42)
echo First argument : %1
echo All arguments  : %*

rem %~dp0 becomes the directory of the script
echo Script dir     : %~dp0

rem errorlevel reflects the last command
cmd /c "exit 0"
echo errorlevel after success = %errorlevel%
