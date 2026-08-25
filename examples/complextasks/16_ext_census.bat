@echo off
setlocal enabledelayedexpansion
md census 2>nul
echo x>census\a.txt
echo y>census\b.txt
echo z>census\c.ini
for %%F in (census\*) do set /a cnt_%%~xF+=1
echo .txt=!cnt_.txt! .ini=!cnt_.ini!
rd /s /q census
