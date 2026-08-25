@echo off
setlocal enabledelayedexpansion
set HOST=web01
set PORT=8080
set SSL=true
(
echo {
echo   "host": "%HOST%",
echo   "port": %PORT%,
echo   "ssl": "%SSL%"
echo }
) > cfg.json
type cfg.json
del cfg.json
