@echo off
setlocal
set SRC=src_demo
set DST=backup_demo
md %SRC%\data 2>nul
echo v1 > %SRC%\data\a.txt
xcopy /e /y %SRC% %DST% >nul
echo v2 > %SRC%\data\a.txt
xcopy /e /y /d %SRC% %DST% >nul
dir /b /s %DST%
rd /s /q %SRC% %DST%
