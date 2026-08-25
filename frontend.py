#!/usr/bin/env python3
"""bat2sh GUI - a Tkinter front-end for the batch-to-shell converter.

Provides a friendly interface to convert Windows .bat/.cmd files (or whole
folders) into bash scripts, with a live preview, syntax checking and the
same options as the command-line tool.
"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


def _load_backend():
    """Import the bat2sh package, falling back to a copy next to this file."""
    try:
        return __import__('bat2sh')
    except ImportError:
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (here, os.path.dirname(here)):
        if os.path.isfile(os.path.join(cand, 'bat2sh', '__init__.py')):
            sys.path.insert(0, cand)
            try:
                return __import__('bat2sh')
            except ImportError:
                sys.path.remove(cand)
    return None


def _backend_works(mod):
    """The backend must answer `-v` / `--version` as a subprocess CLI."""
    root = os.path.dirname(os.path.abspath(mod.__file__))
    env = dict(os.environ, PYTHONPATH=root)
    for flag in ('-v', '--version'):
        try:
            r = subprocess.run([sys.executable, '-m', 'bat2sh', flag],
                               capture_output=True, text=True,
                               env=env, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            return False
        if r.returncode == 0 and 'bat2sh' in r.stdout:
            return True
    return False


bat2sh = _load_backend()
if bat2sh is None or not _backend_works(bat2sh):
    sys.stderr.write(
        'frontend: the bat2sh backend was not found or is not working.\n'
        'Place this script next to the bat2sh package and make sure\n'
        '`python3 -m bat2sh -v` prints a version string.\n')
    sys.exit(1)

decode_text = bat2sh.decode_text
Translator = bat2sh.Translator
VERSION = bat2sh.__version__
ENCODINGS = ['auto', 'utf-8', 'utf-8-sig', 'cp1251', 'cp1252',
             'cp866', 'latin-1', 'utf-16']

STRINGS = {
    'en': {
        'file': 'File', 'open_file': 'Open File…',
        'open_dir': 'Open Folder…', 'save_as': 'Save Script As…',
        'quit': 'Quit', 'edit': 'Edit', 'copy': 'Copy Script',
        'run': 'Run', 'convert': 'Convert', 'help': 'Help',
        'about': 'About',
        'lang_menu': 'Language', 'lang_other': 'Русский',
        'input': 'Input .bat / .cmd file or folder:',
        'browse_file': 'Browse File…', 'browse_dir': 'Browse Folder…',
        'options': 'Options', 'output': 'Output:',
        'out_inplace': 'Next to input (name.sh)',
        'out_file': 'Choose file:', 'out_outdir': 'Output directory:',
        'out_stdout': 'Preview only (do not write)',
        'encoding': 'Encoding:', 'chk': 'Syntax-check only (-c)',
        'clean': 'Clean output (-n)',
        'noclobber': "Don't overwrite existing (-C)",
        'quiet': 'Quiet (-q)', 'copy_btn': 'Copy', 'save_btn': 'Save As…',
        'ready': 'Ready.', 'preview': 'Generated shell script',
    },
    'ru': {
        'file': 'Файл', 'open_file': 'Открыть файл…',
        'open_dir': 'Открыть папку…', 'save_as': 'Сохранить скрипт как…',
        'quit': 'Выход', 'edit': 'Правка', 'copy': 'Копировать скрипт',
        'run': 'Запуск', 'convert': 'Конвертировать', 'help': 'Справка',
        'about': 'О программе',
        'lang_menu': 'Язык / Language', 'lang_other': 'English',
        'input': 'Входной .bat/.cmd файл или папка:',
        'browse_file': 'Выбрать файл…', 'browse_dir': 'Выбрать папку…',
        'options': 'Параметры', 'output': 'Вывод:',
        'out_inplace': 'Рядом с входным (имя.sh)',
        'out_file': 'Указать файл:', 'out_outdir': 'Папка вывода:',
        'out_stdout': 'Только просмотр (не сохранять)',
        'encoding': 'Кодировка:', 'chk': 'Только проверка синтаксиса (-c)',
        'clean': 'Чистый вывод (-n)',
        'noclobber': 'Не перезаписывать существующие (-C)',
        'quiet': 'Тихий режим (-q)', 'copy_btn': 'Копировать',
        'save_btn': 'Сохранить как…', 'ready': 'Готово.',
        'preview': 'Готовый shell-скрипт',
    },
}


class Bat2ShGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = 'en'
        self.title('bat2sh %s' % VERSION)
        self.geometry('900x680')
        self.minsize(680, 500)

        self.inp_var = tk.StringVar()
        self.out_mode = tk.StringVar(value='inplace')
        self.out_var = tk.StringVar()
        self.outdir_var = tk.StringVar()
        self.check_var = tk.BooleanVar(value=False)
        self.clean_var = tk.BooleanVar(value=False)
        self.noclobber_var = tk.BooleanVar(value=False)
        self.quiet_var = tk.BooleanVar(value=False)
        self.encoding_var = tk.StringVar(value='auto')

        self._build_widgets()
        self._layout()
        self._bind_shortcuts()
        self._sync_output_state()
        self._apply_lang()

    def _t(self, key):
        return STRINGS[self.lang][key]

    def _apply_lang(self):
        t = self._t
        self.input_lbl.configure(text=t('input'))
        self.browse_file_btn.configure(text=t('browse_file'))
        self.browse_dir_btn.configure(text=t('browse_dir'))
        self.opt_frame.configure(text=t('options'))
        self.out_lbl.configure(text=t('output'))
        self.radio_inplace.configure(text=t('out_inplace'))
        self.radio_file.configure(text=t('out_file'))
        self.radio_outdir.configure(text=t('out_outdir'))
        self.radio_stdout.configure(text=t('out_stdout'))
        self.enc_lbl.configure(text=t('encoding'))
        self.check_btn.configure(text=t('chk'))
        self.clean_btn.configure(text=t('clean'))
        self.noclobber_btn.configure(text=t('noclobber'))
        self.quiet_btn.configure(text=t('quiet'))
        self.convert_btn.configure(text=t('convert'))
        self.copy_btn.configure(text=t('copy_btn'))
        self.save_btn.configure(text=t('save_btn'))
        self.preview_frame.configure(text=t('preview'))
        self.status_lbl.configure(text=t('ready'))
        self.config(menu=self._build_menubar())

    def _set_lang(self, lang):
        self.lang = 'ru' if lang == 'en' else 'en'
        self._apply_lang()

    # ui construction
    def _build_menubar(self):
        t = self._t
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label=t('open_file'), accelerator='Ctrl+O',
                             command=self._browse_file)
        filemenu.add_command(label=t('open_dir'), command=self._browse_dir)
        filemenu.add_separator()
        filemenu.add_command(label=t('save_as'), accelerator='Ctrl+S',
                             command=self._save_as)
        filemenu.add_separator()
        filemenu.add_command(label=t('quit'), accelerator='Ctrl+Q',
                             command=self.destroy)
        menubar.add_cascade(label=t('file'), menu=filemenu)
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label=t('copy'), accelerator='Ctrl+C',
                             command=self._copy)
        menubar.add_cascade(label=t('edit'), menu=editmenu)
        runmenu = tk.Menu(menubar, tearoff=0)
        runmenu.add_command(label=t('convert'), accelerator='F5',
                            command=self._convert)
        menubar.add_cascade(label=t('run'), menu=runmenu)
        langmenu = tk.Menu(menubar, tearoff=0)
        langmenu.add_command(label=t('lang_other'),
                             command=lambda: self._set_lang(self.lang))
        menubar.add_cascade(label=t('lang_menu'), menu=langmenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=t('about'), command=self._about)
        menubar.add_cascade(label=t('help'), menu=helpmenu)
        return menubar

    def _build_widgets(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            pass

        self.input_lbl = ttk.Label(self, text=self._t('input'))
        self.input_entry = ttk.Entry(self, textvariable=self.inp_var)
        self.browse_file_btn = ttk.Button(self, text=self._t('browse_file'),
                                          command=self._browse_file)
        self.browse_dir_btn = ttk.Button(self, text=self._t('browse_dir'),
                                         command=self._browse_dir)

        self.opt_frame = ttk.LabelFrame(self, text=self._t('options'))

        self.out_lbl = ttk.Label(self.opt_frame, text=self._t('output'))
        self.radio_inplace = ttk.Radiobutton(
            self.opt_frame, text=self._t('out_inplace'),
            variable=self.out_mode, value='inplace',
            command=self._sync_output_state)
        self.radio_file = ttk.Radiobutton(
            self.opt_frame, text=self._t('out_file'),
            variable=self.out_mode, value='file',
            command=self._sync_output_state)
        self.out_entry = ttk.Entry(self.opt_frame, textvariable=self.out_var)
        self.out_browse_btn = ttk.Button(self.opt_frame, text='Browse…',
                                         command=self._browse_out)
        self.radio_outdir = ttk.Radiobutton(
            self.opt_frame, text=self._t('out_outdir'),
            variable=self.out_mode, value='outdir',
            command=self._sync_output_state)
        self.outdir_entry = ttk.Entry(self.opt_frame,
                                      textvariable=self.outdir_var)
        self.outdir_browse_btn = ttk.Button(self.opt_frame, text='Browse…',
                                            command=self._browse_outdir)
        self.radio_stdout = ttk.Radiobutton(
            self.opt_frame, text=self._t('out_stdout'),
            variable=self.out_mode, value='stdout',
            command=self._sync_output_state)

        self.enc_lbl = ttk.Label(self.opt_frame, text=self._t('encoding'))
        self.enc_combo = ttk.Combobox(self.opt_frame,
                                      textvariable=self.encoding_var,
                                      values=ENCODINGS, width=12,
                                      state='readonly')

        self.check_btn = ttk.Checkbutton(
            self.opt_frame, text=self._t('chk'),
            variable=self.check_var)
        self.clean_btn = ttk.Checkbutton(
            self.opt_frame, text=self._t('clean'),
            variable=self.clean_var)
        self.noclobber_btn = ttk.Checkbutton(
            self.opt_frame, text=self._t('noclobber'),
            variable=self.noclobber_var)
        self.quiet_btn = ttk.Checkbutton(
            self.opt_frame, text=self._t('quiet'),
            variable=self.quiet_var)

        self.convert_btn = ttk.Button(self, text=self._t('convert'),
                                      command=self._convert)
        self.copy_btn = ttk.Button(self, text=self._t('copy_btn'),
                                   command=self._copy)
        self.save_btn = ttk.Button(self, text=self._t('save_btn'),
                                   command=self._save_as)
        self.progress = ttk.Progressbar(self, orient='horizontal',
                                        mode='determinate', maximum=100)

        self.status_lbl = ttk.Label(self, text=self._t('ready'),
                                    anchor='w')

        self.preview_frame = ttk.LabelFrame(
            self, text=self._t('preview'))
        self.preview = scrolledtext.ScrolledText(
            self.preview_frame, wrap=tk.NONE, font=('Courier New', 10))

    def _layout(self):
        pad = dict(padx=8, pady=4)
        self.input_lbl.grid(row=0, column=0, sticky='w', **pad)
        self.input_entry.grid(row=0, column=1, sticky='ew', **pad)
        self.browse_file_btn.grid(row=0, column=2, sticky='e', **pad)
        self.browse_dir_btn.grid(row=0, column=3, sticky='e', **pad)

        self.opt_frame.grid(row=1, column=0, columnspan=4, sticky='ew', **pad)
        self.out_lbl.grid(row=0, column=0, sticky='w', padx=6, pady=2)
        self.radio_inplace.grid(row=0, column=1, sticky='w', padx=6, pady=2)
        self.radio_file.grid(row=1, column=0, sticky='w', padx=6, pady=2)
        self.out_entry.grid(row=1, column=1, columnspan=2, sticky='ew',
                            padx=4, pady=2)
        self.out_browse_btn.grid(row=1, column=3, padx=4, pady=2)
        self.radio_outdir.grid(row=2, column=0, sticky='w', padx=6, pady=2)
        self.outdir_entry.grid(row=2, column=1, columnspan=2, sticky='ew',
                               padx=4, pady=2)
        self.outdir_browse_btn.grid(row=2, column=3, padx=4, pady=2)
        self.radio_stdout.grid(row=3, column=0, columnspan=4, sticky='w',
                               padx=6, pady=2)
        self.enc_lbl.grid(row=0, column=4, sticky='e', padx=6, pady=2)
        self.enc_combo.grid(row=0, column=5, sticky='w', padx=4, pady=2)
        self.check_btn.grid(row=4, column=0, columnspan=2, sticky='w', **pad)
        self.clean_btn.grid(row=4, column=2, columnspan=2, sticky='w', **pad)
        self.noclobber_btn.grid(row=5, column=0, columnspan=2, sticky='w', **pad)
        self.quiet_btn.grid(row=5, column=2, columnspan=2, sticky='w', **pad)
        for c in (1, 2):
            self.opt_frame.columnconfigure(c, weight=1)
        self.opt_frame.columnconfigure(5, weight=0)

        self.convert_btn.grid(row=2, column=0, sticky='w', **pad)
        self.copy_btn.grid(row=2, column=1, sticky='w', **pad)
        self.save_btn.grid(row=2, column=2, sticky='w', **pad)
        self.progress.grid(row=2, column=3, sticky='ew', **pad)

        self.status_lbl.grid(row=3, column=0, columnspan=4, sticky='ew', **pad)

        self.preview_frame.grid(row=4, column=0, columnspan=4,
                                sticky='nsew', **pad)
        self.preview.pack(fill=tk.BOTH, expand=True)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)

    def _bind_shortcuts(self):
        self.bind('<Control-o>', lambda e: self._browse_file())
        self.bind('<Control-s>', lambda e: self._save_as())
        self.bind('<Control-c>', lambda e: self._copy())
        self.bind('<Control-q>', lambda e: self.destroy())
        self.bind('<F5>', lambda e: self._convert())

    # helpers
    def _enc(self):
        enc = self.encoding_var.get()
        return None if enc == 'auto' else enc

    def _build_dst(self, src):
        mode = self.out_mode.get()
        if mode == 'inplace':
            return os.path.splitext(src)[0] + '.sh'
        if mode == 'file':
            return self.out_var.get().strip()
        if mode == 'outdir':
            od = self.outdir_var.get().strip()
            return os.path.join(od, os.path.splitext(os.path.basename(src))[0] + '.sh')
        return None

    def _write(self, dst, sh):
        os.makedirs(os.path.dirname(os.path.abspath(dst)) or '.', exist_ok=True)
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(sh)
        try:
            os.chmod(dst, 0o755)
        except OSError:
            pass

    def _set_preview(self, text):
        self.preview.configure(state=tk.NORMAL)
        self.preview.delete('1.0', tk.END)
        self.preview.insert('1.0', text)
        self.preview.configure(state=tk.DISABLED)

    def _status(self, msg, error=False):
        if self.quiet_var.get() and not error:
            return
        self.status_lbl.configure(
            text=msg, foreground=('#c0392b' if error else '#2c3e50'))

    def _about(self):
        if self.lang == 'ru':
            body = ('bat2sh %s\n\nПереводит сценарии Windows batch '
                    '(.bat/.cmd) в сценарии POSIX bash.\n\n'
                    'Бэкенд: bat2sh (диспетчер по счётчику команд).\n'
                    'Фронтенд: Tkinter.') % VERSION
            title = 'О программе bat2sh'
        else:
            body = ('bat2sh %s\n\nConverts Windows batch (.bat/.cmd) scripts'
                    ' into POSIX bash scripts.\n\n'
                    'Backend: bat2sh (program-counter dispatch translator).\n'
                    'GUI: Tkinter front-end.') % VERSION
            title = 'About bat2sh'
        messagebox.showinfo(title, body)

    @staticmethod
    def _bash_check(sh):
        import subprocess
        import tempfile
        fd, path = tempfile.mkstemp(suffix='.sh')
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(sh)
            r = subprocess.run(['bash', '-n', path],
                               capture_output=True, text=True)
            return r.returncode == 0, r.stderr
        finally:
            os.unlink(path)

    # browse actions
    def _browse_file(self):
        path = filedialog.askopenfilename(
            title='Open Batch File',
            filetypes=[('Batch files', '*.bat *.cmd'), ('All files', '*.*')])
        if path:
            self.inp_var.set(path)
            self.out_mode.set('inplace')
            self._sync_output_state()

    def _browse_dir(self):
        path = filedialog.askdirectory(title='Open Batch Folder')
        if path:
            self.inp_var.set(path)
            self.out_mode.set('inplace')
            self._sync_output_state()

    def _browse_out(self):
        path = filedialog.asksaveasfilename(
            title='Save Shell Script As', defaultextension='.sh',
            filetypes=[('Shell script', '*.sh'), ('All files', '*.*')])
        if path:
            self.out_var.set(path)

    def _browse_outdir(self):
        path = filedialog.askdirectory(title='Select Output Directory')
        if path:
            self.outdir_var.set(path)

    def _sync_output_state(self):
        mode = self.out_mode.get()
        fstate = 'normal' if mode == 'file' else 'disabled'
        dstate = 'normal' if mode == 'outdir' else 'disabled'
        self.out_entry.configure(state=fstate)
        self.out_browse_btn.configure(state=fstate)
        self.outdir_entry.configure(state=dstate)
        self.outdir_browse_btn.configure(state=dstate)

    # conversion
    def _read(self, path):
        with open(path, 'rb') as f:
            return decode_text(f.read(), encoding=self._enc())

    def _convert(self):
        inp = self.inp_var.get().strip()
        if not inp:
            self._status('Please choose an input file or folder.', error=True)
            return
        if not (inp == '-' or os.path.isfile(inp) or os.path.isdir(inp)):
            self._status('Input not found: %s' % inp, error=True)
            return
        if os.path.isdir(inp):
            self._convert_folder(inp)
        else:
            self._convert_file(inp)

    def _convert_file(self, inp):
        try:
            data = self._read(inp)
            sh = Translator().convert(data, clean=self.clean_var.get())
        except Exception as e:  # noqa: BLE001
            self._status('Conversion error: %s' % e, error=True)
            self._set_preview('')
            return

        if self.check_var.get():
            ok, err = self._bash_check(sh)
            text = sh + ('\n\n--- bash -n errors ---\n' + err if not ok else '')
            self._set_preview(text)
            self._status('Syntax %s' % ('OK' if ok else 'FAIL'), error=not ok)
            return

        mode = self.out_mode.get()
        if mode == 'stdout':
            self._set_preview(sh)
            self._status('Preview ready (not written to disk).')
            return

        dst = self._build_dst(inp)
        if not dst:
            self._status('Please choose an output file or directory.',
                         error=True)
            return
        if self.noclobber_var.get() and os.path.exists(dst):
            self._set_preview(sh)
            self._status('Skipped %s (already exists).' % dst)
            return
        try:
            self._write(dst, sh)
        except OSError as e:
            self._status('Write error: %s' % e, error=True)
            return
        self._set_preview(sh)
        self._status('Wrote %s' % dst)

    def _convert_folder(self, folder):
        files = []
        for root, _d, fs in os.walk(folder):
            for fn in sorted(fs):
                if fn.lower().endswith(('.bat', '.cmd')):
                    files.append(os.path.join(root, fn))
        if not files:
            self._status('No .bat/.cmd files found in folder.', error=True)
            return

        mode = self.out_mode.get()
        if mode == 'file':
            mode = 'outdir' if self.outdir_var.get().strip() else 'inplace'
            self.out_mode.set(mode)

        self.progress['maximum'] = len(files)
        self.progress['value'] = 0
        lines = []
        for i, src in enumerate(files, 1):
            try:
                sh = Translator().convert(self._read(src),
                                          clean=self.clean_var.get())
            except Exception as e:  # noqa: BLE001
                lines.append('%s : ERROR %s' % (src, e))
                continue
            if self.check_var.get():
                ok, err = self._bash_check(sh)
                lines.append('%s : %s' % (src, 'OK' if ok else 'FAIL'))
                if not ok:
                    lines.append(err.rstrip())
            elif mode == 'stdout':
                lines.append('%s : processed' % src)
            else:
                if mode == 'outdir':
                    rel = os.path.relpath(src, folder)
                    dst = os.path.join(self.outdir_var.get().strip(),
                                       os.path.splitext(rel)[0] + '.sh')
                else:
                    dst = os.path.splitext(src)[0] + '.sh'
                if self.noclobber_var.get() and os.path.exists(dst):
                    lines.append('%s : skipped (exists)' % src)
                    self.progress['value'] = i
                    self.update_idletasks()
                    continue
                try:
                    self._write(dst, sh)
                    lines.append('%s -> %s' % (src, dst))
                except OSError as e:
                    lines.append('%s : WRITE ERROR %s' % (src, e))
            self.progress['value'] = i
            self.update_idletasks()
        self._set_preview('\n'.join(lines))
        self._status('Processed %d file(s).' % len(files))

    # clipboard and save
    def _copy(self):
        text = self.preview.get('1.0', tk.END)
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text)
            self._status('Script copied to clipboard.')

    def _save_as(self):
        text = self.preview.get('1.0', tk.END)
        if not text.strip():
            self._status('Nothing to save yet.', error=True)
            return
        path = filedialog.asksaveasfilename(
            title='Save Shell Script As', defaultextension='.sh',
            filetypes=[('Shell script', '*.sh'), ('All files', '*.*')])
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                try:
                    os.chmod(path, 0o755)
                except OSError:
                    pass
                self._status('Saved %s' % path)
            except OSError as e:
                self._status('Save error: %s' % e, error=True)


def main():
    if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
        print('No DISPLAY available; the GUI requires a graphical session.',
              file=sys.stderr)
        sys.exit(1)
    app = Bat2ShGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
