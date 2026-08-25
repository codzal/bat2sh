function Test-Prime($n) {
    if ($n -lt 2) { return $false }
    for ($i = 2; $i * $i -le $n; $i++) {
        if ($n % $i -eq 0) { return $false }
    }
    return $true
}
(2..30 | Where-Object { Test-Prime $_ }) -join ", "
