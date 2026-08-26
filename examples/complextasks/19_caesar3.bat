@echo off
setlocal enabledelayedexpansion
set ALPHA=abcdefghijklmnopqrstuvwxyz
set IN=abc xyz
set OUT=
for /l %%i in (0,1,25) do set MAP!i!=
echo input : !IN!
echo rotated: see full alphabet demo below
echo alpha shifted by 3: !ALPHA:~3!!ALPHA:~0,3!
