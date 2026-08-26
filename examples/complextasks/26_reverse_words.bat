@echo off
setlocal enabledelayedexpansion
set SENT=one two three four
set REV=
for %%w in (%SENT%) do set REV=%%w !REV!
echo original: %SENT%
echo reversed: !REV!
