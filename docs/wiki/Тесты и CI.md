# Тесты и CI

## Локально
```bash
python3 -m compileall -q bat2sh frontend.py
python3.13 -m pyflakes bat2sh/*.py frontend.py   # pip install pyflakes
bash tests/snapshot.sh                            # golden-файлы
python3 -m bat2sh -c examples/
```

## Snapshot-тесты
`tests/expected/<name>.sh` — эталонные выводы для каждого примера.
Смена поведения транслятора = осознанное обновление baseline в том же PR:

```bash
for f in examples/*/*.bat; do
  python3 -m bat2sh "$f" > "tests/expected/$(basename "${f%.bat}").sh"
done
```

## GitHub Actions (.github/workflows/ci.yml)
* job **test**: compileall → pyflakes → конвертация всех примеров + `bash -n`
  → runtime-smoke (hello_world и ini из своей папки) → snapshots
* job **shellcheck**: линт shell-хелперов репозитория
* job **release** (release.yml): тег `v*` → прогон тестов → zip-архив →
  GitHub Release с секцией CHANGELOG

Защита ветки master (ruleset `protect-master`): изменения только через PR,
обязательные проверки `test` и `shellcheck`, запрещены удаление ветки и
non-fast-forward пуши.
