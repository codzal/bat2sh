@echo off
setlocal enabledelayedexpansion
set /a a11=1 a12=2 a21=3 a22=4 b11=5 b12=6 b21=7 b22=8
set /a c11=a11*b11+a12*b21 c12=a11*b12+a12*b22
set /a c21=a21*b11+a22*b21 c22=a21*b12+a22*b22
echo result: %c11% %c12% / %c21% %c22%
