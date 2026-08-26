@echo off
setlocal enabledelayedexpansion
set CSV=spend.csv
(
echo name;amount
echo alice;120
echo bob;75
echo carol;200
) > %CSV%
sort /r %CSV% | more +1
del %CSV%
