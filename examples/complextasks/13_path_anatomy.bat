@echo off
setlocal
set FULL=C:\Windows\System32\notepad.exe
echo drive-less parts:
for %%F in ("%FULL%") do (
    echo name=%%~nF ext=%%~xF dir=%%~dpF size_attr=%%~aF
)
