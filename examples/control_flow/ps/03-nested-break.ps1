foreach ($x in 1..5) {
    foreach ($y in 1..5) {
        if ($x * $y -gt 9) { break }
        "$x x $y = $($x*$y)"
    }
}
