@echo off
setlocal enabledelayedexpansion
set TEXT=the cat and the dog and the bird
for %%w in (%TEXT%) do set /a count_%%w+=1
for %%w in (the cat dog and bird) do echo %%w = !count_%%w!
