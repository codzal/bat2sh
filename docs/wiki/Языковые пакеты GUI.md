# Языковые пакеты GUI

Формат `languages/<code>.txt`: `key=value`, `#`-комментарии допустимы,
первая опциональная строка `name=Native Name` идёт в меню.

Ключи (30): file, open_file, open_dir, save_as, quit, edit, copy, run,
convert, help, about, input, browse_file, browse_dir, options, output,
out_inplace, out_file, out_outdir, out_stdout, encoding, chk, clean,
noclobber, quiet, copy_btn, save_btn, ready, preview (+name).

Отсутствующий ключ откатывается к английскому; пакет с пустым файлом
игнорируется. Заголовок меню всегда `Language`.
Подсказки флагов `(-c)` и т.п. живут внутри переводов.
