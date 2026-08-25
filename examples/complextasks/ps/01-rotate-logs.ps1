$dir = "logs_demo"
New-Item $dir -ItemType Directory -Force | Out-Null
"old entry" | Set-Content "$dir/app.log"
$n = 0
Get-ChildItem $dir -Filter *.log | Sort-Object Name -Descending |
    ForEach-Object { $n++; Rename-Item $_.FullName ("app.$n.log") }
Get-ChildItem $dir | Select-Object -ExpandProperty Name
Remove-Item $dir -Recurse -Force
