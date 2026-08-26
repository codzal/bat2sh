@echo off
setlocal enabledelayedexpansion
type nul > temps.csv
for /l %%d in (1,1,5) do (
    set /a T=20+%%d
    echo day%%d,!T!>>temps.csv
)
type temps.csv
del temps.csv
