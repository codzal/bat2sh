$svc = "spooler"
if (Get-Command Start-Service -ErrorAction SilentlyContinue) {
    if (Get-Service -Name $svc -ErrorAction SilentlyContinue) {
        Start-Service $svc; "started $svc"
    } else { "service $svc not installed" }
} elseif (Get-Command systemctl -ErrorAction SilentlyContinue) {
    systemctl start $svc
} else { Write-Warning "no service management for $svc" }
