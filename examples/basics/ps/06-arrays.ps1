$items = @("alpha", "beta", "gamma")
foreach ($i in $items) { Write-Output "item: $i" }
"count = $($items.Count)"
