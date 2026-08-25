# bat2sh/ — ядро конвертера

| Модуль | Ответственность |
|---|---|
| `shell.py` | строковые→bash примитивы: раскрытие переменных (`expand_vars`), пути (`winpath` + стили), слэши, разрезание по операторам и редиректам |
| `parser.py` | батч → AST (if/for/goto/call/label/blocks) |
| `translator.py` | AST → bash: PC-dispatch вывод, хендлеры команд, спец-хелперы (`ci_replace`, `REG_FUNCS`) |
| `commands.py` | карта WIN_COMMAND_MAP + отдельные эмуляции (attrib, icacls, net, …) |
| `ps1.py` | бета-перевод в PowerShell (`--target=ps1`) |
| `audit.py` | детекторы совместимости + генератор отчётов (md/html) |
| `config.py` | пользовательские правила из `~/.config/bat2sh/config.toml` |
| `cli.py` | argparse, кодировки, обработка заданий, проверки, запуск |

⚠️ Это внутренний код пакета — публичный интерфейс: `python3 -m bat2sh`
(см. README в корне). Менять поведение транслятора — только вместе с
обновлением snapshot-бейлайнов `tests/expected/`.
