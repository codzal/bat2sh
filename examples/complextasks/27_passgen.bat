@echo off
setlocal enabledelayedexpansion
set CHARS=abcdefghjkmnpqrstuvwxyzACDEFGHJKLMNPQRSTUVWXYZ23456789
set LEN=12
set PWD=
for /l %%i in (1,1,%LEN%) do (
    set /a IDX=%%RANDOM%% %% 56
    for %%j in (!IDX!) do set PWD=!PWD!!CHARS:~%%j,1!
)
echo generated: !PWD!
