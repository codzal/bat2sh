@echo off
setlocal enabledelayedexpansion
for /l %%h in (1,1,3) do (
    ping -n 1 -w 100 127.0.0.%%h >nul 2>&1 && echo host %%h reachable || echo host %%h down
)
