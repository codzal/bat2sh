@echo off
setlocal
choice /c abc /m "pick a letter"
if errorlevel 3 echo you picked C
if errorlevel 2 echo you picked B
if errorlevel 1 echo you picked A
