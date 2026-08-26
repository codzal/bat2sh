$stamp = Get-Date -Format yyyyMMdd-HHmmss
"data" | Set-Content sample.txt
Copy-Item sample.txt "sample.$stamp.bak"
"backup created: sample.$stamp.bak"
