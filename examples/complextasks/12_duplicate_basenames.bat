@echo off
setlocal enabledelayedexpansion
md dup_demo\1 dup_demo\2 2>nul
echo a> dup_demo\1\same.txt
echo b> dup_demo\2\same.txt
for /r dup_demo %%F in (*) do call :check "%%~nxF"
rd /s /q dup_demo
exit /b 0

:check
set NAME=%~1
if defined seen_%NAME% (echo duplicate: %NAME%) else set seen_%NAME%=1
exit /b
