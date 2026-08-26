function Get-Fact($n) { if ($n -le 1) { 1 } else { $n * (Get-Fact ($n-1)) } }
"5! = $(Get-Fact 5)"
