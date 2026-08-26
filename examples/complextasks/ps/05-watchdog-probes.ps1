$attempts = 0
while ($attempts -lt 3) {
    $attempts++
    Test-Connection 127.0.0.1 -Count 1 -Quiet | Out-Null
}
"watchdog finished after $attempts probes"
