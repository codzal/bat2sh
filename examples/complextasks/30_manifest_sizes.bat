@echo off
setlocal enabledelayedexpansion
md man 2>nul
echo aaa>man\f1.dat
echo bb>man\f2.dat
type nul > manifest.lst
for %%F in (man\*) do echo %%~nxF %%~zF>>manifest.lst
type manifest.lst
rd /s /q man & del manifest.lst
