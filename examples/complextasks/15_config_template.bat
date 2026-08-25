@echo off
setlocal enabledelayedexpansion
set HOST=db.local
set PORT=5432
(
echo host=!HOST!
echo port=!PORT!
echo pool=4
) > app.conf
type app.conf
del app.conf
