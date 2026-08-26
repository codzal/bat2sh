@echo off
setlocal enabledelayedexpansion
set DATA=aa bbbbb ccccccccc dd
for %%l in (%DATA%) do call :bucket %%l
exit /b 0

:bucket
set L=%1
set /a SIZE=0
:len2
if defined L (set L=%L:~1%& set /a SIZE+=1& goto len2)
if %SIZE% geq 5 (echo long: %SIZE%) else echo short: %SIZE%
exit /b
