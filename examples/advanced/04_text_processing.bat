@echo off
rem process lines with tokens and delims
for /f "tokens=1,2,3 delims=," %%a in ("alpha,beta,gamma") do echo first=%%a second=%%b third=%%c
for /f "skip=1 tokens=2" %%a in ("header" "data1 data2") do echo skipped_tok2=%%a
for /f "tokens=*" %%a in ('echo piped line') do echo got=%%a
