if (Get-Command Get-CimInstance -ErrorAction SilentlyContinue) {
    Get-CimInstance Win32_OperatingSystem | Select-Object Caption
} elseif (Test-Path /etc/os-release) {
    Get-Content /etc/os-release | Where-Object { $_ -like "PRETTY_NAME*" }
} else { Write-Warning "CIM/WMI unavailable and no os-release" }
