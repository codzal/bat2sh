@echo off
setlocal
for %%s in (95 82 74 61 40) do call :grade %%s
exit /b 0

:grade
set SCORE=%1
if %SCORE% geq 90 (echo %SCORE% -> A) else if %SCORE% geq 80 (echo %SCORE% -> B) else if %SCORE% geq 70 (echo %SCORE% -> C) else if %SCORE% geq 60 (echo %SCORE% -> D) else echo %SCORE% -> F
exit /b
