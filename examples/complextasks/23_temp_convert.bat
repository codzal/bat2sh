@echo off
setlocal enabledelayedexpansion
set C=25
set /a F=C*9/5+32
echo !C%!degC = %F% degF
set F2=212
set /a C2=(F2-32)*5/9
echo !F2! degF = !C2! degC
