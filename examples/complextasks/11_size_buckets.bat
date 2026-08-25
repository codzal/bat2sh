@echo off
setlocal enabledelayedexpansion
md bucket_demo 2>nul
echo x> bucket_demo\tiny.txt
echo xxxxxxxxxxxx> bucket_demo\big.txt
set SMALL=0 BIG=0
for %%F in (bucket_demo\*) do (
    if %%~zF gtr 5 (set /a BIG+=1) else set /a SMALL+=1
)
echo small=%SMALL% big=%BIG%
rd /s /q bucket_demo
