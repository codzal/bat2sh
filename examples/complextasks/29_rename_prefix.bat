@echo off
setlocal enabledelayedexpansion
md rn 2>nul
echo a>rn\one.txt
echo b>rn\two.txt
for %%F in (rn\*.txt) do ren "%%F" "old_%%~nxF"
dir /b rn
rd /s /q rn
