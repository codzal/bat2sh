#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox, scrolledtext

try:                                   # stable drag & drop when available
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND = True
except Exception:
    DND_FILES = '<<Drop>>'
    TkinterDnD = None
    _DND = False


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
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True,
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
syntax_check = bat2sh.syntax_check
Translator = bat2sh.Translator
from bat2sh.audit import analyze, summarize   # noqa: E402
VERSION = bat2sh.__version__
ENCODINGS = ['auto', 'utf-8', 'utf-8-sig', 'cp1251', 'cp1252',
             'cp866', 'latin-1', 'utf-16']

STRINGS = {
    'en': {
        'name': 'English',
        'file': 'File', 'open_file': 'Open File…',
        'open_dir': 'Open Folder…', 'save_as': 'Save Script As…',
        'quit': 'Quit', 'edit': 'Edit', 'copy': 'Copy Script',
        'run': 'Run', 'convert': 'Convert', 'run_now': 'Run', 'help': 'Help',
        'about': 'About',
        'input': 'Input .bat / .cmd file or folder:',
        'browse_file': 'Browse File…', 'browse_dir': 'Browse Folder…',
        'options': 'Options', 'output': 'Output:',
        'out_inplace': 'Next to input (name.sh)',
        'out_file': 'Choose file:', 'out_outdir': 'Output directory:',
        'out_stdout': 'Preview only (do not write)',
        'encoding': 'Encoding:', 'chk': 'Syntax-check only (-c)',
        'noclobber': "Don't overwrite existing (-C)",
        'debug': 'Keep debug comments (--debug)', 'copy_btn': 'Copy', 'save_btn': 'Save As…',
        'ready': 'Ready.', 'preview': 'Generated shell script',
        'target': 'Target:',
        'preset_bash': 'Pure Bash', 'preset_wsl': 'WSL',
        'preset_wine': 'Wine-friendly',
        'strict': 'set -euo pipefail',
        'out_lang': 'Script language:',
        'audit': 'Audit (--analyze)',
        'rlayer': 'Runtime layer',
        'shebang': 'Shebang:',
        'ran_ok': 'Exited with code %d.',
        'ran_fail': 'Exit %d (see console).',
        'tip_preset_bash': 'Convert paths as-is; drives like C:\\ stay '
                           'literal. Best for reading, not for running.',
        'tip_preset_wsl': 'Map drive letters to /mnt/c style WSL paths '
                          'so the script runs inside WSL.',
        'tip_preset_wine': 'Keep Windows paths but point commands at a '
                           'Wine prefix (Z:\\C\\...).',
        'tip_strict': 'Prepend "set -euo pipefail": stop on errors, unset '
                      'variables and failed pipes. Stricter than batch.',
        'tip_check': 'Run bash -n on the result and write nothing. Use it '
                     'to test conversion safety first.',
        'tip_noclobber': 'Refuse to overwrite an existing output file '
                         'instead of silently replacing it.',
        'tip_debug': 'Keep BAT2SH debug comments in the output. Off by '
                     'default - generated scripts are clean.',
        'audit_clean': 'clean - no compatibility findings',
        'tip_audit': 'Scan the batch source for Windows-only calls '
                     '(registry, services, .exe binaries) before '
                     'conversion. Report goes to the preview pane.',
        'tip_run_now': 'Convert in memory and execute right away; the '
                          'script itself is never written to disk.',
        'tip_target_ps1': 'Emit PowerShell 7 instead of bash. Beta: every '
                          'example converts parse-clean, coverage is still '
                          'smaller.',
        'beta': '[beta] translations other than English may be incomplete',
        'choose_input': 'Please choose an input file or folder.',
        'input_missing': 'Input not found: %s',
        'no_bat': 'No .bat/.cmd files found in folder.',
        'processed': 'Processed %d file(s).',
        'wrote': 'Wrote %s', 'skipped': 'Skipped %s (exists).',
        'syntax_ok': 'Syntax OK', 'syntax_fail': 'Syntax FAIL',
        'preview_ready': 'Preview ready (not written to disk).',
        'copied': 'Script copied to clipboard.',
        'nothing_to_save': 'Nothing to save yet.',
        'saved': 'Saved %s',
        'write_err': 'Write error: %s', 'save_err': 'Save error: %s',
        'conv_err': 'Conversion error: %s',
        'dlg_open_file': 'Open Batch File',
        'dlg_open_dir': 'Open Batch Folder',
        'dlg_save_as': 'Save Shell Script As',
        'dlg_outdir': 'Select Output Directory',
        'ft_batch': 'Batch files', 'ft_shell': 'Shell script',
        'ft_all': 'All files',
    }
}

LANG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'languages')


def _load_langs():
    """Built-in English plus every languages/<code>.txt pack found."""
    packs = {'en': STRINGS['en']}
    try:
        files = sorted(os.listdir(LANG_DIR))
    except OSError:
        return packs
    for fn in files:
        if not fn.endswith('.txt'):
            continue
        code = fn[:-4]
        d = {}
        for line in open(os.path.join(LANG_DIR, fn), encoding='utf-8'):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            d[k.strip()] = v
        if d:
            packs[code] = d
    return packs


LANGS = _load_langs()


_BASE = TkinterDnD.Tk if _DND else tk.Tk


class ToolTip:
    """Hover hint shown after a short delay.

    One persistent (withdrawn, not destroyed) borderless window per tip so
    repeated hovers do not flicker. Never stays above other applications:
    no -topmost, and every focus loss hides it.
    """

    @classmethod
    def hide_all(cls):
        for inst in cls._registry:
            inst._hide()

    _registry = []

    def __init__(self, widget, get_text, delay=700):
        self.widget = widget
        self.get_text = get_text
        self.delay = delay
        self._id = None
        self._win = None
        self._lbl = None
        ToolTip._registry.append(self)
        widget.bind('<Enter>', self._schedule)
        widget.bind('<Leave>', self._hide)
        widget.bind('<ButtonPress>', self._hide)

    def _pointer_inside(self):
        px, py = self.widget.winfo_pointerx(), self.widget.winfo_pointery()
        under = self.widget.winfo_containing(px, py)
        return under is not None and str(under).startswith(str(self.widget))

    def _schedule(self, _e=None):
        self._cancel()
        self._id = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self._id:
            try:
                self.widget.after_cancel(self._id)
            except tk.TclError:
                pass
            self._id = None

    def _show(self):
        self._id = None
        text = self.get_text()
        if not text or not self._pointer_inside():
            return
        if self._win is None:
            self._win = tk.Toplevel(self.widget)
            self._win.wm_overrideredirect(True)
            self._lbl = tk.Label(
                self._win, justify='left', wraplength=340,
                background='#ffffe0', relief='solid', borderwidth=1,
                font=('TkDefaultFont', 9), padx=6, pady=4)
            self._lbl.pack()
        self._lbl.configure(text=text)
        # below-right of the cursor, flipped away from screen edges,
        # so the window never covers the pointer (that causes flicker)
        x = self.widget.winfo_rootx() + min(12, self.widget.winfo_width())
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        sw, sh = self.widget.winfo_screenwidth(), \
            self.widget.winfo_screenheight()
        self._win.update_idletasks()
        if x + self._win.winfo_reqwidth() > sw - 8:
            x = max(8, self.widget.winfo_rootx()
                    - self._win.winfo_reqwidth() - 12)
        if y + self._win.winfo_reqheight() > sh - 8:
            y = self.widget.winfo_rooty() - self._win.winfo_reqheight() - 6
        self._win.wm_geometry('+%d+%d' % (x, y))
        self._win.deiconify()
        self._win.lift(self.widget)

    def _hide(self, _e=None):
        self._cancel()
        if self._win is not None:
            self._win.withdraw()


class Bat2ShGUI(_BASE):
    def __init__(self):
        super().__init__()
        if _DND:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_drop)
        self.lang = 'en'
        self.title('bat2sh %s' % VERSION)
        self.geometry('900x680')
        self.minsize(680, 500)

        self.inp_var = tk.StringVar()
        self.out_mode = tk.StringVar(value='inplace')
        self.out_var = tk.StringVar()
        self.outdir_var = tk.StringVar()
        self.check_var = tk.BooleanVar(value=False)
        self.noclobber_var = tk.BooleanVar(value=False)
        self.debug_var = tk.BooleanVar(value=False)
        self.encoding_var = tk.StringVar(value='auto')
        self.preset_var = tk.StringVar(value='bash')
        self.target_var = tk.StringVar(value='bash')
        self.strict_var = tk.BooleanVar(value=False)
        self.analyze_var = tk.BooleanVar(value=False)
        self.rlayer_var = tk.BooleanVar(value=False)
        self.shebang_var = tk.StringVar()
        self._cascades = []          # filled by _build_menubar

        fixed = tkfont.nametofont('TkFixedFont')
        fixed.configure(size=10)
        self.fixed_font = fixed

        self._build_widgets()
        self._layout()
        self._bind_shortcuts()
        self._sync_output_state()
        self._apply_lang()

    def _t(self, key):
        return LANGS.get(self.lang, STRINGS['en']).get(
            key, STRINGS['en'].get(key, key))

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
        self.lang_lbl.configure(text=t('out_lang'))
        self.shebang_lbl.configure(text=t('shebang'))
        self.runnow_btn.configure(text=t('run_now'))
        self.analyze_btn.configure(text=t('audit'))
        self.rlayer_btn.configure(text=t('rlayer'))
        self.check_btn.configure(text=t('chk'))
        self.noclobber_btn.configure(text=t('noclobber'))
        self.debug_btn.configure(text=t('debug'))
        self.convert_btn.configure(text=t('convert'))
        self.copy_btn.configure(text=t('copy_btn'))
        self.save_btn.configure(text=t('save_btn'))
        self.preview_frame.configure(text=t('preview'))
        self.status_lbl.configure(text=t('ready'))
        self.config(menu=self._build_menubar())
        # never leave a hint floating over other applications
        self.bind('<Deactivate>', lambda _e: ToolTip.hide_all())
        for cascade in self._cascades:
            old_post = cascade.cget('postcommand')

            def guarded(_old=old_post):
                ToolTip.hide_all()
                if _old:
                    self.tk.call(_old)

            cascade.configure(postcommand=guarded)

    def _set_lang(self, lang):
        self.lang = lang
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
        runmenu.add_command(label=t('run_now'), accelerator='Ctrl+R',
                            command=self._run_now)
        menubar.add_cascade(label=t('run'), menu=runmenu)
        langmenu = tk.Menu(menubar, tearoff=0)
        for code, pack in sorted(LANGS.items()):
            label = pack.get('name', code.capitalize())
            langmenu.add_command(
                label=('• %s' % label if code == self.lang else label),
                command=lambda c=code: self._set_lang(c))
        menubar.add_cascade(label='Language', menu=langmenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=t('about'), command=self._about)
        menubar.add_cascade(label=t('help'), menu=helpmenu)
        self._cascades = [c for c in (filemenu, editmenu, runmenu,
                                      langmenu, helpmenu)]
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

        self.preset_lbl = ttk.Label(self.opt_frame,
                                    text=self._t('target'))
        for val in ('bash', 'wsl', 'wine'):
            rb = ttk.Radiobutton(self.opt_frame, value=val,
                                 variable=self.preset_var,
                                 text=self._t('preset_' + val),
                                 command=self._apply_preset)
            setattr(self, 'preset_' + val, rb)

        self.strict_btn = ttk.Checkbutton(
            self.opt_frame, text=self._t('strict'),
            variable=self.strict_var)

        self.check_btn = ttk.Checkbutton(
            self.opt_frame, text=self._t('chk'),
            variable=self.check_var)
        self.noclobber_btn = ttk.Checkbutton(
            self.opt_frame, text=self._t('noclobber'),
            variable=self.noclobber_var)
        self.debug_btn = ttk.Checkbutton(
            self.opt_frame, text=self._t('debug'),
            variable=self.debug_var)

        self.lang_lbl = ttk.Label(self.opt_frame, text=self._t('out_lang'))
        self.target_combo = ttk.Combobox(self.opt_frame,
                                         textvariable=self.target_var,
                                         values=('bash', 'ps1'), width=6,
                                         state='readonly')
        self.analyze_btn = ttk.Checkbutton(self.opt_frame,
                                           text=self._t('audit'),
                                           variable=self.analyze_var)
        self.rlayer_btn = ttk.Checkbutton(self.opt_frame,
                                          text=self._t('rlayer'),
                                          variable=self.rlayer_var)
        self.shebang_lbl = ttk.Label(self.opt_frame,
                                     text=self._t('shebang'))
        self.shebang_entry = ttk.Entry(self.opt_frame,
                                       textvariable=self.shebang_var,
                                       width=22)

        self.convert_btn = ttk.Button(self, text=self._t('convert'),
                                      command=self._convert)
        self.runnow_btn = ttk.Button(self, text=self._t('run_now'),
                                     command=self._run_now)
        self.copy_btn = ttk.Button(self, text=self._t('copy_btn'),
                                   command=self._copy)
        self.save_btn = ttk.Button(self, text=self._t('save_btn'),
                                   command=self._save_as)
        self.progress = ttk.Progressbar(self, orient='horizontal',
                                        mode='determinate', maximum=100)

        self.status_lbl = ttk.Label(
            self, text=self._t('ready') + '  ' + self._t('beta'),
                                    anchor='w')

        self.preview_frame = ttk.LabelFrame(
            self, text=self._t('preview'))
        self.pane = tk.PanedWindow(self.preview_frame, orient=tk.HORIZONTAL,
                              sashrelief=tk.RAISED)
        self.orig = scrolledtext.ScrolledText(
            self.pane, wrap=tk.NONE, font=self.fixed_font,
                       width=40)
        self.preview = scrolledtext.ScrolledText(
            self.pane, wrap=tk.NONE, font=self.fixed_font)
        self.pane.add(self.orig, width=280)
        self.pane.add(self.preview)
        self.orig.configure(state=tk.DISABLED)
        self._sync_lock = False
        self.orig['yscrollcommand'] = (
            lambda f, l: self._mirror(self.preview, f))
        self.preview['yscrollcommand'] = (
            lambda f, l: self._mirror(self.orig, f))
        for wdg in (self.orig, self.preview):
            wdg.tag_configure('kw', foreground='#2a6fdb')
            wdg.tag_configure('str', foreground='#b0560f')
            wdg.tag_configure('com', foreground='#3d8f3d')

        # hints only where the label alone does not explain the option
        for wdg, key in (
            (self.preset_bash, 'tip_preset_bash'),
            (self.preset_wsl, 'tip_preset_wsl'),
            (self.preset_wine, 'tip_preset_wine'),
            (self.strict_btn, 'tip_strict'),
            (self.check_btn, 'tip_check'),
            (self.noclobber_btn, 'tip_noclobber'),
            (self.debug_btn, 'tip_debug'),
            (self.analyze_btn, 'tip_audit'),
        ):
            ToolTip(wdg, lambda k=key: self._t(k))

    def _mirror(self, other, first):
        """Mirror scroll position without feedback loops."""
        if self._sync_lock:
            return
        self._sync_lock = True
        try:
            other.yview_moveto(first)
        finally:
            self._sync_lock = False

    @staticmethod
    def _highlight(widget, kind):
        data = widget.get('1.0', tk.END)
        widget.tag_remove('kw', '1.0', tk.END)
        widget.tag_remove('com', '1.0', tk.END)
        widget.tag_remove('str', '1.0', tk.END)
        import re as _re
        kws = (r'\b(if|not|exist|defined|errorlevel|else|for|do|done|goto|'
               r'call|set|setlocal|endlocal|echo|exit|shift|pause|then|fi|'
               r'while|case|esac|local|function|return|in)\b') \
            if kind == 'bat' else \
            (r'\b(if|then|fi|for|do|done|while|case|esac|local|function|'
             r'return|in|set|echo)\b')
        for m in _re.finditer(kws, data):
            widget.tag_add('kw', '1.0+%dc' % m.start(),
                           '1.0+%dc' % m.end())
        for m in _re.finditer(r'(?:^|\s)(rem [^\n]*|#[^\n]*)', data):
            widget.tag_add('com', '1.0+%dc' % (m.start(1)),
                           '1.0+%dc' % m.end(1))

    def _layout(self):
        pad = dict(padx=8, pady=4)
        self.input_lbl.grid(row=0, column=0, sticky='w', **pad)
        self.input_entry.grid(row=0, column=1, sticky='ew', **pad)
        self.browse_file_btn.grid(row=0, column=2, sticky='e', **pad)
        self.browse_dir_btn.grid(row=0, column=3, sticky='e', **pad)

        self.opt_frame.grid(row=1, column=0, columnspan=5, sticky='ew', **pad)
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
        self.radio_stdout.grid(row=3, column=0, columnspan=5, sticky='w',
                               padx=6, pady=2)
        self.enc_lbl.grid(row=0, column=4, sticky='e', padx=6, pady=2)
        self.enc_combo.grid(row=0, column=5, sticky='w', padx=4, pady=2)
        self.check_btn.grid(row=4, column=0, columnspan=2, sticky='w', **pad)
        self.noclobber_btn.grid(row=5, column=0, columnspan=2, sticky='w', **pad)
        self.debug_btn.grid(row=5, column=2, columnspan=2, sticky='w', **pad)
        self.preset_lbl.grid(row=6, column=0, sticky='w', padx=6, pady=2)
        self.preset_bash.grid(row=6, column=1, sticky='w', padx=4, pady=2)
        self.preset_wsl.grid(row=6, column=2, sticky='w', padx=4, pady=2)
        self.preset_wine.grid(row=6, column=3, sticky='w', padx=4, pady=2)

        self.lang_lbl.grid(row=7, column=0, sticky='w', padx=6, pady=2)
        self.target_combo.grid(row=7, column=1, sticky='w', padx=4, pady=2)
        self.shebang_lbl.grid(row=7, column=2, sticky='e', padx=6, pady=2)
        self.shebang_entry.grid(row=7, column=3, sticky='ew', padx=4, pady=2)
        self.analyze_btn.grid(row=8, column=0, sticky='w', **pad)
        self.rlayer_btn.grid(row=8, column=1, columnspan=3, sticky='w', **pad)
        for c in (1, 2):
            self.opt_frame.columnconfigure(c, weight=1)
        self.opt_frame.columnconfigure(5, weight=0)

        self.convert_btn.grid(row=2, column=0, sticky='w', **pad)
        self.runnow_btn.grid(row=2, column=1, sticky='w', **pad)
        self.copy_btn.grid(row=2, column=2, sticky='w', **pad)
        self.save_btn.grid(row=2, column=3, sticky='w', **pad)
        self.progress.grid(row=2, column=4, sticky='ew', **pad)

        self.status_lbl.grid(row=3, column=0, columnspan=5, sticky='ew', **pad)

        self.preview_frame.grid(row=4, column=0, columnspan=5,
                                sticky='nsew', **pad)
        # the two text panes are managed by the PanedWindow itself
        self.pane.pack(fill=tk.BOTH, expand=True)
        try:
            self.pane.sashpos(0, 280)
        except Exception:
            pass

        self.columnconfigure(1, weight=1)
        self.rowconfigure(4, weight=1)

    def _apply_preset(self):
        style = {'bash': 'root', 'wsl': 'wsl', 'wine': 'wine'}[
            self.preset_var.get()]
        try:
            bat2sh.shell.set_path_style(style)
        except Exception:
            pass

    def _bind_shortcuts(self):
        self.bind('<Control-o>', lambda e: self._browse_file())
        self.bind('<Control-s>', lambda e: self._save_as())
        self.bind('<Control-c>', lambda e: self._copy())
        self.bind('<Control-q>', lambda e: self.destroy())
        self.bind('<Control-r>', lambda e: self._run_now())
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
            os.chmod(dst, 0o700)
        except OSError:
            pass

    def _set_preview(self, text, source=None):
        self.preview.configure(state=tk.NORMAL)
        self.preview.delete('1.0', tk.END)
        self.preview.insert('1.0', text)
        self.preview.configure(state=tk.DISABLED)
        self._highlight(self.preview, 'sh')
        if source is not None:
            self.orig.configure(state=tk.NORMAL)
            self.orig.delete('1.0', tk.END)
            self.orig.insert('1.0', source)
            self.orig.configure(state=tk.DISABLED)
        self._highlight(self.orig, 'bat')

    def _status(self, msg, error=False):
        self.status_lbl.configure(
            text=msg, foreground=('#c0392b' if error else '#2c3e50'))

    def _about(self):
        if self.lang == 'ru':
            body = ('bat2sh %s\n\nПереводит сценарии Windows batch '
                    '(.bat/.cmd) в сценарии POSIX bash.\n\n'
                    'Бэкенд: bat2sh.\n'
                    'Фронтенд: Tkinter.') % VERSION
            title = 'О программе bat2sh'
        else:
            body = ('bat2sh %s\n\nConverts Windows batch (.bat/.cmd) scripts'
                    ' into POSIX bash scripts.\n\n'
                    'Backend: bat2sh.\n'
                    'GUI: Tkinter front-end.') % VERSION
            title = 'About bat2sh'
        messagebox.showinfo(title, body)

    @staticmethod
    def _bash_check(sh):
        return syntax_check(sh)

    @staticmethod
    def _pwsh_check(ps):
        """Parse-validate PowerShell output the same way CI does."""
        exe = shutil.which('pwsh')
        if not exe:
            return False, 'pwsh not found on PATH'
        fd, tmp = tempfile.mkstemp(suffix='.ps1')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(ps)
            r = subprocess.run(
                [exe, '-NoProfile', '-Command',
                 '$null=[scriptblock]::Create((Get-Content -Raw '
                 "-LiteralPath '%s'))" % tmp],
                capture_output=True, text=True, timeout=30)
            return r.returncode == 0, (r.stderr or '').strip()
        finally:
            os.unlink(tmp)

    # browse actions
    def _on_drop(self, event):
        """Accept dropped .bat/.cmd files (tkinterdnd2)."""
        raw = event.data
        paths = re.findall(r'\{([^}]+)\}|([^{}\s]+)', raw)
        paths = [a or b for a, b in paths]
        batches = [p for p in paths
                   if p.lower().endswith(('.bat', '.cmd'))]
        if not batches:
            self._status('Drop a .bat/.cmd file', error=True)
            return
        self.inp_var.set(batches[0])
        self.out_mode.set('inplace')
        self._sync_output_state()
        self._convert()

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title=self._t('dlg_open_file'),
            filetypes=[(self._t('ft_batch'), '*.bat *.cmd'),
                       (self._t('ft_all'), '*.*')])
        if path:
            self.inp_var.set(path)
            self.out_mode.set('inplace')
            self._sync_output_state()

    def _browse_dir(self):
        path = filedialog.askdirectory(title=self._t('dlg_open_dir'))
        if path:
            self.inp_var.set(path)
            self.out_mode.set('inplace')
            self._sync_output_state()

    def _browse_out(self):
        path = filedialog.asksaveasfilename(
            title=self._t('dlg_save_as'), defaultextension='.sh',
            filetypes=[(self._t('ft_shell'), '*.sh'),
                       (self._t('ft_all'), '*.*')])
        if path:
            self.out_var.set(path)

    def _browse_outdir(self):
        path = filedialog.askdirectory(title=self._t('dlg_outdir'))
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
            self._status(self._t('choose_input'), error=True)
            return
        if not (inp == '-' or os.path.isfile(inp) or os.path.isdir(inp)):
            self._status(self._t('input_missing') % inp, error=True)
            return
        if os.path.isdir(inp):
            self._convert_folder(inp)
        else:
            self._convert_file(inp)

    def _convert_file(self, inp):
        try:
            data = self._read(inp)
            if self.target_var.get() == 'ps1':
                from bat2sh.ps1 import convert as ps1_convert
                sh, _fb = ps1_convert(data)
            else:
                sh = Translator().convert(
                    data, clean=not self.debug_var.get(),
                    shebang=self.shebang_var.get().strip() or None,
                    strict=self.strict_var.get())
        except Exception as e:  # noqa: BLE001
            self._status(self._t('conv_err') % e, error=True)
            self._set_preview('')
            return

        # audit report for the preview pane; never mixed into saved output
        audit_block = ''
        if self.analyze_var.get():
            findings = summarize(analyze(data))
            if findings:
                rows = '\n'.join(
                    '  %s:%d [%s] %s\n      %s'
                    % (f['severity'], f['line'], f['id'],
                       f['message'], f['snippet'])
                    for f in findings)
                audit_block = ('\n\n--- %s (%d) ---\n%s'
                               % (self._t('audit'), len(findings), rows))
            else:
                audit_block = ('\n\n--- %s ---\n  %s'
                               % (self._t('audit'), self._t('audit_clean')))

        if self.check_var.get():
            if self.target_var.get() == 'ps1':
                ok, err = self._pwsh_check(sh)
            else:
                ok, err = self._bash_check(sh)
            text = sh + audit_block
            if not ok:
                text += '\n\n--- errors ---\n' + err
            self._set_preview(text)
            ok_txt = self._t('syntax_ok') if ok else self._t('syntax_fail')
            self._status(ok_txt, error=not ok)
            return

        mode = self.out_mode.get()
        if mode == 'stdout':
            self._set_preview(sh + audit_block, data)
            self._status(self._t('preview_ready'))
            return

        dst = self._build_dst(inp)
        if not dst:
            self._status('Please choose an output file or directory.',
                         error=True)
            return
        if self.noclobber_var.get() and os.path.exists(dst):
            self._set_preview(sh + audit_block)
            self._status(self._t('skipped') % dst)
            return
        try:
            self._write(dst, sh)
        except OSError as e:
            self._status(self._t('write_err') % e, error=True)
            return
        self._set_preview(sh + audit_block, data)
        self._status(self._t('wrote') % dst)

    def _run_now(self):
        """Run the current input converted in-memory; nothing is saved."""
        inp = self.inp_var.get().strip()
        if not inp or not (inp == '-' or os.path.isfile(inp)):
            self._status(self._t('choose_input'), error=True)
            return
        if os.path.isdir(inp):
            self._status(self._t('input_missing') % inp, error=True)
            return
        try:
            data = self._read(inp)
            if self.target_var.get() == 'ps1':
                from bat2sh.ps1 import convert as ps1_convert
                script, _fb = ps1_convert(data)
                suffix, interpreter = '.ps1', ['pwsh', '-NoProfile', '-File']
            else:
                script = Translator().convert(
                    data, clean=not self.debug_var.get(),
                    shebang=self.shebang_var.get().strip() or None,
                    strict=self.strict_var.get())
                suffix, interpreter = '.sh', ['bash']
        except Exception as e:  # noqa: BLE001
            self._status(self._t('conv_err') % e, error=True)
            return
        fd, tmp = tempfile.mkstemp(suffix=suffix, prefix='bat2sh_run_')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(script)
            workdir = os.path.dirname(os.path.abspath(inp))
            cmd = interpreter + [tmp]
            try:
                proc = subprocess.run(cmd, cwd=workdir, timeout=120,
                                      capture_output=True, text=True)
            except FileNotFoundError:
                self._status('%s not found on PATH' % cmd[0], error=True)
                return
            except subprocess.TimeoutExpired:
                self._status('timed out after 120s', error=True)
                return
            out = (proc.stdout + proc.stderr).strip()
            if out:
                self._set_preview(script, data + '\n\n--- output ---\n'
                                  + out[-4000:])
            ok = proc.returncode == 0
            self._status(self._t('ran_ok' if ok else 'ran_fail')
                         % proc.returncode, error=not ok)
        finally:
            os.unlink(tmp)

    def _convert_folder(self, folder):
        files = []
        for root, _d, fs in os.walk(folder):
            for fn in sorted(fs):
                if fn.lower().endswith(('.bat', '.cmd')):
                    files.append(os.path.join(root, fn))
        if not files:
            self._status(self._t('no_bat'), error=True)
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
                                          clean=not self.debug_var.get())
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
        self._status(self._t('processed') % len(files))

    # clipboard and save
    def _copy(self):
        text = self.preview.get('1.0', tk.END)
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text)
            self._status(self._t('copied'))

    def _save_as(self):
        text = self.preview.get('1.0', tk.END)
        if not text.strip():
            self._status(self._t('nothing_to_save'), error=True)
            return
        path = filedialog.asksaveasfilename(
            title=self._t('dlg_save_as'), defaultextension='.sh',
            filetypes=[(self._t('ft_shell'), '*.sh'),
                       (self._t('ft_all'), '*.*')])
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                try:
                    os.chmod(path, 0o700)
                except OSError:
                    pass
                self._status(self._t('saved') % path)
            except OSError as e:
                self._status(self._t('save_err') % e, error=True)


def main():
    if not os.environ.get('DISPLAY') and sys.platform.startswith('linux'):
        print('No DISPLAY available; the GUI requires a graphical session.',
              file=sys.stderr)
        sys.exit(1)
    app = Bat2ShGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
