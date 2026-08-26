# PowerShell Target (beta)

`--target=ps1` switches the backend to `bat2sh/ps1.py` and produces
PowerShell 7 scripts instead of bash. It has grown past the "line-by-line
toy" stage: today **every example in this repo converts to a script that
pwsh parses without errors**, and CI enforces that on every push.

## What works

* variables - plain, environment (`%PATH%` → `$env:PATH`), delayed
  expansion (`!V!`), substring replace (`!v:a=b!` → `.Replace()`)
* computed names. `set seen_%%w=1`, `set /a cnt_%%~xF+=1` or even
  `set %%~p` become `Set-Variable` calls that build the name at runtime
* loop-variable modifiers: `%%~zF` turns into `$f.Length`,
  `%%~nF` into `$f.BaseName`, and so on for f/n/x/t/a/p/d
* full control flow: if/else with exist, defined, errorlevel, numeric and
  string compares; plain, `/l`, `/r` and `/f` for-loops; subroutines as
  real `function`s with `$args`
* top-level `goto` is translated through a small program-counter switch,
  so state-machine batch files keep working; `goto :eof` inside a function
  becomes `return`
* arithmetic keeps its numeric meaning - env vars and call arguments are
  wrapped with `[int]`, because `"2" + 1` would otherwise give `"21"`
* common commands map to native cmdlets (Copy-Item, Get-Content,
  Test-Path...); registry access falls back to a JSON store off Windows

## What to expect

Anything the translator cannot express becomes a warning comment rather
than broken code, and CI fails loudly if one ever leaks into the output.
Coverage is still smaller than the bash target, and semantics follow
batch only where a direct PowerShell analogue exists.

With `-c` the generated script is validated by pwsh when it is installed;
otherwise the usual `bash -n` check runs against the bash target.
