git --version *> $null
"LASTEXITCODE after git: $LASTEXITCODE"
if ($LASTEXITCODE -ne 0) { "git missing - that is fine on CI" }
