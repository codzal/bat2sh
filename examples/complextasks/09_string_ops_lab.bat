@echo off
setlocal enabledelayedexpansion
set S=Hello Batch World
echo len-ish first5: !S:~0,5!
echo from6: !S:~6!
echo lower->upper sample: !S:w=W!
set T=!S:World=Everyone!
echo replaced: !T!
