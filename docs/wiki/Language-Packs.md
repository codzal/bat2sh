# Language Packs

Format `languages/<code>.txt`: `key=value` lines, `#` comments allowed,
optional first line `name=Native Name` shown in the menu.

Keys (57): file, open_file, open_dir, save_as, quit, edit, copy, run,
convert, help, about, input, browse_file, browse_dir, options, output,
out_inplace, out_file, out_outdir, out_stdout, encoding, chk, clean,
noclobber, quiet, target, preset_bash, preset_wsl, preset_wine, strict,
copy_btn, save_btn, ready, preview, choose_input, input_missing, no_bat,
processed, wrote, skipped, syntax_ok, syntax_fail, preview_ready, copied,
nothing_to_save, saved, write_err, save_err, conv_err, dlg_open_file,
dlg_open_dir, dlg_save_as, dlg_outdir, ft_batch, ft_shell, ft_all, beta.

Missing keys fall back to English; an empty pack is ignored. The menu title
is always `Language`. Flag hints like `(-c)` live inside translations.

> Non-English packs may be incomplete - English is the reference.
