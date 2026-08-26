@echo off
setlocal enabledelayedexpansion
call :walk 1
exit /b 0

:walk
if %1 gtr 4 exit /b
set SP=
for /l %%i in (1,1,%1) do set SP=!SP!.
echo %SP%depth %1
set /a NEXT=%1+1
call :walk !NEXT!
echo %SP%unwind %1
exit /b
