$text = "the cat and the dog and the bird"
$text -split "\s+" | Group-Object | Sort-Object Count -Descending |
    ForEach-Object { "{0} = {1}" -f $_.Name, $_.Count }
