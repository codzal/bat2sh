# Audit and Reports

```bash
python3 -m bat2sh --analyze path[.bat|folder]
python3 -m bat2sh --analyze examples/ --report report.html
```

## Detectors
| id | trigger | advice |
|---|---|---|
| registry | `reg add/query/...` | verify logic; through bat2sh it runs on a JSON store |
| regfile | `.reg` mentioned | manual review |
| binary | running `*.exe/*.msi/*.com` | wrap with `wine prog` or use native equivalent; concrete tips for notepad/calc/mspaint/taskmgr/explorer/msiexec |
| service | `net start/stop`, `sc config/start/stop/query`, `vssadmin` | map to systemctl/service |
| wmi | `wmic` | no POSIX analog |

## Report
`--report out.md` (or `.html`) aggregates per processed file:
statement count, fallback count, coverage percent and the manual-attention
list (`file:line`). Coverage = `(stmts-fallback)/stmts`; fallback counts
lines passed through untranslated.
