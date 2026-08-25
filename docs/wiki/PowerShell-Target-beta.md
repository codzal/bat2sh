# PowerShell Target beta

`--target=ps1` enables `bat2sh/ps1.py`. Line-based subset:

| batch | ps1 |
|---|---|
| `echo x` | `Write-Output x` |
| `set V=x` / `set /a A=B+1` | `$env:V="x"` / arithmetic |
| `if [not] exist p cmd` | `if (-not Test-Path "p") { ... }` |
| `copy/move/ren/del/type/md/cd` | Copy-/Move-/Rename-/Remove-Item, Get-Content, New-Item, Set-Location |
| `cls`, `pause`, `rem` | Clear-Host, Read-Host, `#` |

Anything else emits `# BAT2SH WARNING: no PowerShell mapping for: ...`.
goto/for/call are not supported in the beta. With `-c`, validation uses
`pwsh -NoProfile` when available.
