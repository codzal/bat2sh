@echo off
setlocal
for /l %%i in (3,-1,1) do (
    echo T-minus %%i
    timeout /t 1 >nul
)
echo Liftoff!
