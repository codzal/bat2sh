Get-ChildItem demo -File | ForEach-Object {
    if ($_.Length -gt 5) { "big: $($_.Name)" } else { "small: $($_.Name)" }
}
