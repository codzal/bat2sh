Get-ChildItem demo -File |
    Select-Object Name, Length | Export-Csv manifest.csv -NoTypeInformation
Import-Csv manifest.csv | Format-Table | Out-String
