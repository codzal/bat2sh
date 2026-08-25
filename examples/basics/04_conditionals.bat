@echo off
set VAL=7
if %VAL% gtr 5 echo VAL is greater than 5
if %VAL% lss 10 echo VAL is less than 10
if defined VAL echo VAL is defined
set EMPTY=
if not defined EMPTY echo EMPTY is not defined
if exist does_not_exist.txt (echo exists) else (echo not exists)
cmd /c "exit /b 2"
if errorlevel 2 echo previous errorlevel was 2
