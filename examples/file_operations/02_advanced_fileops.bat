@echo off
set DIR=workdir
md %DIR%
echo line one > %DIR%\a.txt
echo line two > %DIR%\b.txt
copy %DIR%\a.txt %DIR%\c.txt
move %DIR%\b.txt %DIR%\b_moved.txt
ren %DIR%\c.txt c_renamed.txt
dir %DIR%
del /q %DIR%\a.txt
rd /s /q %DIR%
