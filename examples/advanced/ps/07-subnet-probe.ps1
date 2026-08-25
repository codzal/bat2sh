foreach ($h in 1..3) {
    if (Test-Connection 127.0.0.$h -Count 1 -Quiet) { "host $h up" }
    else { "host $h down" }
}
