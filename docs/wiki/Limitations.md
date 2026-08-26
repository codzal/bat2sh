# Limitations

bat2sh is a translator, not an emulator. It reproduces the constructs real
batch files use; the rest degrades gracefully. The honest list:

* `errorlevel` reflects the last executed command - exactly like cmd.exe.
* `start` drops switches and titles, backgrounds the process with
  `nohup ... &`. POSIX has no console or session concept.
* `color`, `mode`, `chcp` are simplified: color sets an ANSI palette,
  the others are no-ops.
* The command source of `for /f '...'` runs as a shell command; batch
  syntax inside that string is not re-parsed.
* Computed variable names (`!prefix_%%i!`) and dynamic call labels
  (`call :!name!`) do translate - through bash indirect expansion /
  `Set-Variable` - but deeply nested combinations may still fall back to
  a warning comment instead of guessing.
* `--target=ps1` emits parse-clean PowerShell for every bundled example,
  yet stays beta: fewer commands are covered than in the bash target.
