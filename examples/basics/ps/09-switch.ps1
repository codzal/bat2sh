foreach ($c in "a","b","z") {
    switch ($c) {
        "a" { "alpha" }
        "b" { "beta" }
        default { "unknown: $c" }
    }
}
