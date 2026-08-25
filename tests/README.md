# tests/

`snapshot.sh` + `expected/*.sh` — golden-тесты: конвертируем все примеры
и сравниваем побайтно с эталонами.

⚠️ Если вы **намеренно** изменили поведение транслятора — перегенерируйте
baseline и приложите к тому же PR:
```bash
for f in ../examples/*/*.bat; do
  python3 -m bat2sh "$f" > "expected/$(basename "${f%.bat}").sh"
done
```
Случайное расхождение = регрессия, CI не пустит.
