$matrix = @{ EDITOR = "vim"; SHELL = "/bin/bash"; TERM = "xterm" }
$matrix.GetEnumerator() | ForEach-Object {
    "{0}={1}" -f $_.Key, $_.Value }
