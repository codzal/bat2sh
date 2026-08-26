@echo off
setlocal enabledelayedexpansion
set W1=listened
set W2=silent
call :strlen W1 L1
call :strlen W2 L2
if !L1! equ !L2! (echo same length !L1! - possible anagram) else echo different lengths
exit /b 0

:strlen
set /a %2=0
for %%c in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do (
    if not "!%~1:%%c=!"=="!%~1!" set /a %2+=1
)
exit /b
