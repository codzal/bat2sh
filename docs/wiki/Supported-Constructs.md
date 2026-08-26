# Supported Constructs

## Variables
`set`, `set /a` (octal guard: `val=08+2` works), `set /p`,
`%VAR%`, delayed `!VAR!`, `%VAR:~N,M%` incl. negative offsets,
case-insensitive replacement `%VAR:f=r%` (cmd semantics),
args `%1..%9 %* %~1 %~dp0 %~nx...`, `%ERRORLEVEL%`.
Windows env -> POSIX: `%TEMP%/%TMP%`, `%USERPROFILE%`, `%APPDATA%`,
`%LOCALAPPDATA%`, `%PROGRAMFILES%`, `%PROGRAMDATA%`, `%SYSTEMROOT%/%WINDIR%`,
`%COMPUTERNAME%`. Dotted names (`config.server.host`) become
`config_server_host`; dynamic `set "a.!sec!.!k!=!v!"` uses `printf -v`. Dynamic call labels (`call :!name!`) resolve through the same
mechanism. In the PowerShell target computed names go through
`Set-Variable` with a runtime name expression instead.

The table above describes the **bash** target; `--target=ps1` covers a
growing subset of it - see [[PowerShell Target beta]] for what translates
there today.

## Flow
`if/not/i/exist/defined/errorlevel`, comparisons (`equ neq lss leq gtr geq`;
string equ/neq via `[[ ]]`), `else`,
`for`, `for /l`, `for /r [path]`, `for /f` (`usebackq`, empty `delims=` =
no split, `skip=`, `tokens=N,N-M,a,N*,*`),
nested blocks, chained `if A if B (...) else (...)`,
`goto` (incl. leaving loops), `call :label args` - called labels become real
bash functions so they work inside loops; `exit /b N` propagates the code.

## Redirection
`> >> <`, pipes, `& && ||`; `nul` -> `/dev/null`; literal `>= <=` inside text
is preserved.

## Commands (selection)
echo/rem/::/@, cd, md/mkdir, rd/rmdir (`/s /q`; without `/s` -> `rmdir`),
del (`/s /f /q`, multiple patterns), copy/move/ren, type, cls,
pause (exact cmd text), title, color (ANSI), setlocal/endlocal (no-op),
pushd/popd (path translated), shift, start (switches, quoted title,
URL -> xdg-open, `/wait` synchronous), dir, find/findstr, path,
choice (`/t /d /c`, timeout rc=255), `cmd /c other.bat` -> runs converted
sibling.

### Network & services
`ipconfig[/all]`->`ip[-br] addr`, `netstat -ano`->`ss -tulpn`,
`route print`->`ip route`, `nslookup h`->`dig +short h`,
`netsh wlan show profiles`->`nmcli connection show`,
`sc query/start/stop X`->`systemctl ... X`,
`sc config X start= auto|demand`->`systemctl enable/disable X`,
`net start/stop`->`systemctl`.

### System emulations
`attrib +-hrs x`->dot-rename/chmod; `icacls/cacls /grant /deny /reset`->chmod;
`assoc`/`ftype`->xdg-mime; `subst X: path|/d`->
`~/.local/share/bat2sh/drives/x`; `where`->`which`;
`reg add/query/delete`->JSON store `${BAT2SH_REG:-$HOME/.config/bat2sh/registry.json}`
with virtual values from `/etc/os-release`
(`HKLM\...\CurrentVersion\ProductName`, `ComSpec=/bin/bash`, `SystemRoot=/`).

## cmd.exe-style diagnostics
Unknown command -> `'x' is not recognized as an internal or external command,`
`operable program or batch file.` (errorlevel 9009, keeps running).
Missing label on `goto` -> message + stop; on `call` -> message + continue
(errorlevel 1). Untranslatable input -> `The syntax of the command is
incorrect.` and rc=1 instead of a translator crash.
