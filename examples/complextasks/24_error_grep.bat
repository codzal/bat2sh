@echo off
setlocal
(
echo INFO start
echo ERROR disk full
echo WARN slow io
echo ERROR panic
) > app.log
findstr /b "ERROR" app.log
del app.log
