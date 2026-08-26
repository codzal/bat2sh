@echo off
setlocal enabledelayedexpansion
start "" cmd /c "timeout /t 2 >nul & echo ready>flag.tmp"
:waitloop
if exist flag.tmp goto got
ping -n 1 127.0.0.1 >nul
goto waitloop
:got
type flag.tmp
del flag.tmp
