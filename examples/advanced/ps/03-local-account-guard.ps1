if (Get-Command Get-LocalUser -ErrorAction SilentlyContinue) {
    Get-LocalUser | Select-Object -First 5 Name, Enabled
} elseif (Test-Path /etc/passwd) {
    Get-Content /etc/passwd | Select-Object -First 5 |
        ForEach-Object { ($_ -split ":")[0] }
}
