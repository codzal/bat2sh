@echo off
rem ============================================================
rem  advanced/03_windows_paths.bat
rem  Demonstrates how Windows drive letters and backslashes are
rem  translated to POSIX paths (C:\...  ->  /mnt/c/...).
rem  NOTE: this example is meant to show translation only; the
rem  generated script references /mnt/c which does not exist on
rem  a typical Linux box, so run it only to inspect the output.
rem ============================================================

set SRC=C:\Projects\app\input.txt
set DST=C:/Projects/app/output.txt

if exist "%SRC%" (
    copy "%SRC%" "%DST%"
) else (
    echo Source %SRC% not found
)

rem %~dp0 is the directory the script lives in
echo Script location: %~dp0

rem backslash separators are converted automatically
md C:\Temp\work 2> nul
echo test > C:\Temp\work\data.txt
type C:\Temp\work\data.txt
