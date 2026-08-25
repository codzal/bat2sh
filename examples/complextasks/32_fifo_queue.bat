@echo off
setlocal enabledelayedexpansion
set Q=task1 task2 task3
:serve
for /f "tokens=1*" %%a in ("!Q!") do (
    echo serving %%a
    set Q=%%b
    if defined Q goto serve
)
echo queue empty
