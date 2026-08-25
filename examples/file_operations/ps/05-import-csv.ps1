"name,amount" | Set-Content s.csv
"alice,120"  | Add-Content s.csv
"bob,75"     | Add-Content s.csv
Import-Csv s.csv | Sort-Object {[int]$_.amount} -Descending | Select-Object -First 1
