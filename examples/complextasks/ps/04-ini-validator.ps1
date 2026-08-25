$required = "host", "port", "user"
$present = @("host")
$missing = $required | Where-Object { $_ -notin $present }
if ($missing) { "ini INVALID: $($missing -join ",")" }
else { "ini OK" }
