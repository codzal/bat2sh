"PATH","HOME","TEMP" | ForEach-Object {
    "{0,-8} = {1}" -f $_, ([Environment]::GetEnvironmentVariable($_))
}
