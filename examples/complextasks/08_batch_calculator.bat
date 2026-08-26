@echo off
setlocal enabledelayedexpansion
set /a A=12 B=5
echo %A%+%B%=!A!+!B! ... running
set /a SUM=A+B DIF=A-B MUL=A*B DIV=A/B MOD=A%%B
echo sum=%SUM% dif=%DIF% mul=%MUL% div=%DIV% mod=%MOD%
