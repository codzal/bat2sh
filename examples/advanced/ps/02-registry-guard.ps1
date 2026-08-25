if ($IsWindows) {
    $k = "HKCU:\Software\bat2sh"
    New-Item -Path $k -Force | Out-Null
    Set-ItemProperty -Path $k -Name Version -Value "0.4"
    (Get-ItemProperty $k).Version
} else {
    "registry is Windows-only; use the JSON emulation from bat2sh"
}
