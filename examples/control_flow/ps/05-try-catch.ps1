try { [int]"abc" | Out-Null }
catch { Write-Output "caught: $($_.Exception.Message)" }
