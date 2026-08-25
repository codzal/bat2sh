$a = 12; $b = 5
[pscustomobject]@{ sum = $a + $b; dif = $a - $b;
                   mul = $a * $b; div = [math]::Floor($a / $b);
                   mod = $a % $b }
