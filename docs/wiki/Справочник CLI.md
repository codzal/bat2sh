# Справочник CLI

```
usage: bat2sh [-h] [-i] [-o DIR] [-c] [-r] [-n] [-C] [-q] [--encoding ENC]
              [--path-style {wsl,wine,root}] [--shebang STR] [-x] [--diff]
              [--strict-bash] [--analyze] [--report FILE]
              [--install-vscode-task [DIR]] [--runtime-layer]
              [--target {bash,ps1}] [-v]
              [input] [output]
```

## Основные
| Флаг | Действие |
|---|---|
| `-i`, `--inplace` | записать `<input>.sh` рядом с входным |
| `-o DIR\|FILE.sh` | папка вывода (сохраняет дерево) **или** полный путь к файлу, если заканчивается на `.sh` |
| `-c`, `--check` | только `bash -n` (+подсказки shellcheck), файлы не пишутся |
| `-r`, `--run` | конвертировать и сразу выполнить; код возврата = код скрипта |
| `-n`, `--no-debug` | убрать служебные комментарии конвертера |
| `-C`, `--no-clobber` | не перезаписывать существующие `.sh` |
| `-q`, `--quiet` | скрыть информационные сообщения |
| `--encoding ENC` | принудительная кодировка входа (`cp1251`, `cp866`, …) |

## Пути и стиль
| Флаг | Действие |
|---|---|
| `--path-style wsl\|wine\|root` | `C:\x` → `/mnt/c/x` \| `~/.wine/drive_c/x` \| `/x` |
| `--shebang STR` | шебанг результата (по умолчанию `#!/usr/bin/env bash`) |
| `-x`, `--executable` | выдать права 755 записанным `.sh` |

## Просмотр и надёжность
| Флаг | Действие |
|---|---|
| `--diff` | side-by-side «batch \| bash», без записи файлов |
| `--strict-bash` | вставить `set -euo pipefail` после шебанга |
| `--runtime-layer` | добавить `check_errorlevel()` и симлинки дисков в `/tmp/bat2sh_drives/<X>` |

## Аудит и отчёты
| Флаг | Действие |
|---|---|
| `--analyze` | только аудит: реестр, Windows-бинарники (+советы wine/аналог), службы, wmic |
| `--report FILE.md\|.html` | отчёт миграции: покрытие по каждому файлу + места ручного внимания |

## Прочее
| Флаг | Действие |
|---|---|
| `--target bash\|ps1` | язык результата (ps1 — beta) |
| `--install-vscode-task [DIR]` | создать `.vscode/tasks.json` для конвертации одной клавишей |
| `-v`, `--version` / `-h` | версия / справка |

## stdin-режимы
1. `python3 -m bat2sh < file.bat` или `cat file \| bat2sh` — **выполнить**.
2. Добавить `-` — напечатать bash. Добавить `-c` — проверить.
3. Без stdin-пайпа и без аргументов — печатается help.

## Свои правила команд
`~/.config/bat2sh/config.toml`
```toml
[commands]
my_tool = "mytool-linux {args}"      # {args} подставит аргументы
backup   = "rsync -a {args}"
```
Плоский формат `name = value` в `config.conf` тоже поддерживается.
