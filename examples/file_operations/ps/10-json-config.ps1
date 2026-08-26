$cfg = @{ host = "web01"; port = 8080; ssl = $true }
$cfg | ConvertTo-Json | Set-Content cfg.json
(Get-Content cfg.json -Raw | ConvertFrom-Json).host
