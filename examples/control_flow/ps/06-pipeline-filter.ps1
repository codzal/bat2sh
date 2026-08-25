1..10 | Where-Object { $_ % 2 -eq 0 } | ForEach-Object { "even: $_" }
