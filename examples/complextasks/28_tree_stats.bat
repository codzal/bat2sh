@echo off
setlocal enabledelayedexpansion
md tree\d1\d2 2>nul
echo 1>tree\f1.txt
echo 22>tree\d1\f2.txt
echo 333>tree\d1\d2\f3.txt
set FILES=0
for /r tree %%F in (*) do set /a FILES+=1
echo files under tree/: !FILES!
rd /s /q tree
