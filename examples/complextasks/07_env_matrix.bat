@echo off
setlocal enabledelayedexpansion
for %%p in ("EDITOR=vim" "SHELL=/bin/bash" "TERM=xterm") do set %%~p
echo EDITOR=!EDITOR! SHELL=!SHELL! TERM=!TERM!
