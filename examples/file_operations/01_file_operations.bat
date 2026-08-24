@echo off
rem ============================================================
rem  file_operations/01_file_operations.bat
rem  Demonstrates file and directory commands:
rem   - md / mkdir, rd / rmdir (incl. recursive /s)
rem   - copy, move, ren, del / erase (incl. recursive /s)
rem   - type (cat), redirection > and >>, nul device
rem  Runnable on Linux after conversion. Paths with spaces
rem  and Windows backslashes are handled.
rem ============================================================

md "work dir" 2> nul
echo hello > "work dir\a.txt"
echo world >> "work dir\a.txt"

copy "work dir\a.txt" "work dir\b.txt"
move "work dir\b.txt" "work dir\c.txt"
ren "work dir\c.txt" d.txt

type "work dir\d.txt"

del "work dir\a.txt"
rd /s /q "work dir"

echo All file operations completed. > nul
echo done
