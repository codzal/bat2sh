$t = New-TemporaryFile
"payload" | Set-Content $t
Get-Content $t
Remove-Item $t
