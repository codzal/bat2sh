@echo off
rem ============================================================
rem  advanced/01_project_build.bat
rem  A small "build" script combining many features: arguments,
rem  variables, if/else, a for /l loop, a subroutine call and
rem  file operations. Runnable on Linux after conversion.
rem
rem  Usage: 01_project_build.sh [project name]
rem ============================================================

setlocal
set PROJECT=%1
if "%PROJECT%"=="" set PROJECT=demo

echo Building project: %PROJECT%
md build 2> nul

set /a FILES=0
for /l %%n in (1,1,3) do (
    echo // generated file %%n > build\%PROJECT%_%%n.txt
    set /a FILES=FILES + 1
)

call :report %FILES%
echo Build finished.
goto :eof

:report
echo Created %1 files in the build directory.
goto :eof
