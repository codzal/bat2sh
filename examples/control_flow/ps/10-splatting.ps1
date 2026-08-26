$splat = @{ Path = "."; Recurse = $true; Depth = 1 }
Get-ChildItem @splat | Select-Object -First 3 -ExpandProperty Name
