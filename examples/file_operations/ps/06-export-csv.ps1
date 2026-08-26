1..5 | ForEach-Object { [pscustomobject]@{ day = "d$_"; temp = 20 + $_ } } |
    Export-Csv temps.csv -NoTypeInformation
Import-Csv temps.csv | Format-Table | Out-String
