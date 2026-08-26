New-Item -ItemType Directory -Force -Path demo/d1/d2 | Out-Null
"one" | Set-Content demo/f1.txt
"two" | Set-Content demo/d1/f2.txt
