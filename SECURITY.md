# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
| 0.3.x   | :white_check_mark: |
| < 0.3   | :x:                |

## Reporting a vulnerability

Please use **GitHub → Security → Report a vulnerability**
(private vulnerability reporting) for anything that could be exploited by a
crafted `.bat` file (path traversal in redirections, command injection via
generated bash, unsafe temp files, …).

For non-sensitive bugs, open a regular issue with the template.

Generated scripts run **arbitrary commands from the source batch file** —
treat every converted script the way you would treat the original `.bat`,
and audit it first:

```bash
python3 -m bat2sh --analyze suspect.bat --report report.md
python3 -m bat2sh -c suspect.bat      # + shellcheck hints if installed
```
