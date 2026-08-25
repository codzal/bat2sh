@echo off
rem ============================================================
rem  control_flow/02_loops.bat
rem  Demonstrates the three FOR loop forms:
rem   - for %%v in (list)         iterate over a list
rem   - for /l %%v (start,step,end)  numeric range
rem   - for /f "delims=" %%v in (file/or command)  parse lines
rem  Runnable on Linux after conversion.
rem ============================================================

echo --- iterating over a list ---
for %%f in (apple banana cherry) do (
    echo fruit: %%f
)

echo --- numeric range with for /l ---
set /a TOTAL=0
for /l %%n in (1,1,5) do (
    set /a TOTAL=%%n + TOTAL
)
echo sum 1..5 = %TOTAL%

echo --- for /f over command output ---
for /f "delims=" %%l in ('echo line one ^& echo line two') do (
    echo got: %%l
)

echo --- for /f reading a file ---
echo first > example.tmp
echo second >> example.tmp
for /f "delims=" %%l in (example.tmp) do (
    echo file line: %%l
)
del example.tmp
