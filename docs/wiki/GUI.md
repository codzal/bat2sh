# GUI

Run: `python3 frontend.py`

* File/folder pickers; output modes (beside input / choose file /
  output directory / preview-only).
* Live dual-pane viewer: **batch \| bash**, synchronized scrolling,
  keyword/comment highlighting.
* Target presets: **Pure Bash** (default, root-style paths) / **WSL**
  (/mnt/c) / **Wine-friendly** (~/.wine/drive_c).
* Convert/Copy/Save As buttons, folder progress bar, `[beta]` status note.
* Menu **Language**: built-in English; other packs load from
  `languages/*.txt` ([[Language Packs]]). Non-English packs may be
  incomplete.

Background errors surface as dialog windows: tkinter -> kdialog ->
zenity -> stderr.
