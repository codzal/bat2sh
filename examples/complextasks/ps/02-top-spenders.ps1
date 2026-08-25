$rows = @(
    [pscustomobject]@{ name = "alice"; amount = 120 }
    [pscustomobject]@{ name = "bob";   amount = 75 }
    [pscustomobject]@{ name = "carol"; amount = 200 })
$rows | Sort-Object amount -Descending | Select-Object -First 2
