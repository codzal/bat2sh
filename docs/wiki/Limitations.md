# Limitations

bat2sh is a translator, not an emulator.

* `errorlevel` reflects the last executed command - same as real cmd.exe.
* `start` drops switches/title and backgrounds the process (`nohup ... &`);
  POSIX has no console/session concept.
* `color`/`mode`/`chcp` simplified (color sets ANSI text color only).
* The command source of `for /f '...'` executes as a shell command;
  batch syntax inside is not re-parsed.
* Computed variable names (`!prefix_%%i!`) and dynamic call labels
  (`call :!name!`) are not translatable.
* The PowerShell target covers a basic subset and is beta.
