@echo off
rem arithmetic and string manipulation
set /a A=10
set /a B=3
set /a SUM=A+B
set /a PROD=A*B
echo A=%A% B=%B% SUM=%SUM% PROD=%PROD%
set STR=HelloWorldBatch
echo First5=%STR:~0,5%
echo From6=%STR:~5%
echo Last4=%STR:~-4%
set N=42
echo Padded=%N:~-5%
echo Arg1=%1
echo AllArgs=%*
