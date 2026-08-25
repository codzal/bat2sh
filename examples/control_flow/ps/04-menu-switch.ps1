foreach ($pick in "start","stop","status") {
    switch -Regex ($pick) {
        "^start" { "starting service" }
        "^stop"  { "stopping service" }
        default  { "querying status" }
    }
}
