# PowerShell-таргет (beta)

`--target=ps1` включает `bat2sh/ps1.py`. Поддерживается построчно:

| batch | ps1 |
|---|---|
| `echo x` | `Write-Output x` |
| `set V=x` / `set /a A=B+1` | `$env:V="x"` / арифметика |
| `if [not] exist p cmd` | `if (-not Test-Path "p") { … }` |
| `copy/move/ren/del/type/md/cd` | Copy-/Move-/Rename-/Remove-Item, Get-Content, New-Item, Set-Location |
| `cls`, `pause`, `rem` | Clear-Host, Read-Host, `#` |

Непокрытое помечается `# BAT2SH WARNING: no PowerShell mapping for: …`.
goto/for/call в beta-режиме не поддерживаются. Проверка синтаксиса `-c`
для ps1 выполняется через `pwsh -NoProfile` при его наличии.
