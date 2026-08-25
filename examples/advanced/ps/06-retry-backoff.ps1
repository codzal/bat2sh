$delay = 1
foreach ($try in 1..3) {
    "attempt $try"
    Start-Sleep -Seconds $delay
    $delay *= 2
}
