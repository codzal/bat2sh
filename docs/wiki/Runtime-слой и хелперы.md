# Runtime-слой и хелперы

`--runtime-layer` вставляет после шебанга:

```bash
check_errorlevel() { echo "$ERRORLEVEL"; }
mkdir -p "/tmp/bat2sh_drives/<x>" && ln -sfn "<root>" "/tmp/bat2sh_drives/<x>/."
```

* буквы дисков извлекаются из исходника (`X:\`);
* цель симлинка зависит от `--path-style`;
* `--strict-bash` добавляет `set -euo pipefail` — учтите, что «падающие»
  команды (например, намеренный `false`) остановят скрипт;
* `ERRORLEVEL=$?` после каждой инструкции — сознательная модель cmd.exe.
