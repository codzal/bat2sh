"ERROR disk", "INFO ok", "ERROR panic" | Set-Content app.log
Select-String -Path app.log -Pattern "^ERROR" | ForEach-Object Line
