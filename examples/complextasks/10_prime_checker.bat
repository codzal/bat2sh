@echo off
setlocal enabledelayedexpansion
call :isprime 13
if !ERRORLEVEL! equ 0 (echo 13 is prime) else echo 13 not prime
call :isprime 15
if !ERRORLEVEL! equ 0 (echo 15 is prime) else echo 15 not prime
exit /b 0

:isprime
set /a N=%1, I=2
:loop
set /a R=N%%I
if %R% equ 0 exit /b 1
set /a I+=1
set /a SQ=I*I
if %SQ% leq %N% goto loop
exit /b 0
