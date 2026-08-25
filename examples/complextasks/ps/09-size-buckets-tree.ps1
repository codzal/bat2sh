$tree = "bucket_demo"
New-Item "$tree/d1/d2" -ItemType Directory -Force | Out-Null
"x"     | Set-Content "$tree/tiny.txt"
("x" * 20) | Set-Content "$tree/d1/big.txt"
$small = 0; $big = 0
Get-ChildItem $tree -Recurse -File | ForEach-Object {
    if ($_.Length -gt 5) { $big++ } else { $small++ }
}
"small=$small big=$big"
Remove-Item $tree -Recurse -Force
