@echo off
setlocal enabledelayedexpansion
set A=left
set B=right
set TMP=%A%
set A=%B%
set B=%TMP%
echo swapped: A=%A% B=%B%
set /a X=3 Y=9
set /a X=X+Y, Y=X-Y, X=X-Y
echo numeric swap: X=%X% Y=%Y%
