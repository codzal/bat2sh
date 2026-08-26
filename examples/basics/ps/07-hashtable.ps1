$cfg = @{ host = "db.local"; port = 5432 }
$cfg.Keys | ForEach-Object { "$_ = $($cfg[$_])" }
