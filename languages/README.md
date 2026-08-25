# languages/ - GUI language packs

Format: `key=value`, `#` comments allowed, optional first line
`name=Native Name`.

To add a language copy `ru.txt` to `<code>.txt`, translate the values,
keep the keys. A missing key falls back to English.

Warning: translations other than the built-in English may be incomplete -
the reference values live in `frontend.py` (`STRINGS['en']`).
