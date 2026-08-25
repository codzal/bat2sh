import atexit
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from functools import lru_cache

from . import __version__
from .audit import analyze, migration_report, summarize
from .config import load_rules
from . import shell
from .ps1 import convert as ps1_convert
from .translator import Translator


def decode_text(raw, encoding=None):
    """Decode raw batch bytes (BOM/codepage autodetect or forced)."""
    if encoding:
        return raw.decode(encoding, errors='replace')
    if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
        return raw.decode('utf-16', errors='replace')
    for enc in ('utf-8-sig', 'utf-8', 'cp1251', 'cp1252', 'latin-1'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='replace')


def _collect_jobs(args):
    """Return a list of (input_path, output_path_or_None) jobs."""
    jobs = []
    inp = args.input
    if inp == '-':
        jobs.append(('-', None))
        return jobs
    if os.path.isdir(inp):
        out_dir = args.output_dir
        for root, _dirs, files in os.walk(inp):
            for fn in sorted(files):
                if fn.lower().endswith(('.bat', '.cmd')):
                    src = os.path.join(root, fn)
                    if out_dir:
                        rel = os.path.relpath(src, inp)
                        dst = os.path.join(out_dir,
                                           os.path.splitext(rel)[0] + '.sh')
                    else:
                        dst = os.path.splitext(src)[0] + '.sh'
                    jobs.append((src, dst))
        return jobs
    out = args.output
    if out is None and args.inplace:
        out = os.path.splitext(inp)[0] + '.sh'
    elif args.output_dir:
        # -o accepts either a directory or a full .sh file path
        if args.output_dir.lower().endswith('.sh'):
            out = args.output_dir
        elif out is None:
            out = os.path.join(args.output_dir,
                               os.path.splitext(os.path.basename(inp))[0]
                               + '.sh')
    jobs.append((inp, out))
    return jobs


_TMP_FILES = []


def _cleanup_tmp():
    for p in _TMP_FILES:
        try:
            os.unlink(p)
        except OSError:
            pass


atexit.register(_cleanup_tmp)


def _mktemp_sh(tag):
    """Private 0600 temp file immune to symlink pre-creation."""
    fd, path = tempfile.mkstemp(prefix='bat2sh_%s_' % tag, suffix='.sh')
    _TMP_FILES.append(path)
    return fd, path

_REPORT = []
_LOCK = threading.Lock()


def _write_tmp(text):
    with _LOCK:
        fd, path = _mktemp_sh('check')
    with os.fdopen(fd, 'w') as f:
        f.write(text)
    return path





def _run_script(text):
    """Run converted text via bash, inheriting stdio."""
    fd, run_path = _mktemp_sh('run')
    with os.fdopen(fd, 'w') as f:
        f.write(text)
    try:
        rc = subprocess.call(['bash', run_path])
    except OSError as e:
        _notify_error('bat2sh', 'cannot run converted script: %s' % e)
        return 127
    finally:
        try:
            os.unlink(run_path)
            _TMP_FILES.remove(run_path)
        except (OSError, ValueError):
            pass
    if rc != 0 and not sys.stderr.isatty():
        _notify_error('bat2sh',
                      'converted script exited with code %d' % rc)
    elif rc != 0:
        sys.stderr.write('converted script exited with code %d\n' % rc)
    return rc


def _notify_error(title, text):
    """Error dialog when detached from a terminal; else stderr."""
    if sys.stderr.isatty():
        sys.stderr.write(text + '\n')
        return
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, text)
        root.destroy()
        return
    except Exception:
        pass
    for argv_ in (('kdialog', '--error', text, '--title', title),
                  ('zenity', '--error', '--width=400', '--text', text,
                   '--title', title)):
        try:
            bin_path = shutil.which(argv_[0])
            if bin_path and subprocess.run(
                    [bin_path] + list(argv_[1:])).returncode == 0:
                return
        except OSError:
            pass
    sys.stderr.write(text + '\n')


def shell_hints(text, limit=8):
    """Run shellcheck when available; return list of hint lines."""
    import subprocess as sp
    SC_BIN = shutil.which('shellcheck')
    if not SC_BIN:
        return []
    r = sp.run([SC_BIN, '-f', 'gcc', '-x', '-s', 'bash', '-S', 'warning',
                _write_tmp(text)], stdout=sp.PIPE, stderr=sp.PIPE,
                   universal_newlines=True)
    keep = [ln for ln in r.stdout.splitlines()
            if not any(c in ln for c in ('SC2317', 'SC2152', 'SC2320', 'SC1097', 'SC2154'))]
    if not keep:
        return []
    out = ['shellcheck hints:']
    out += ['  ' + ln for ln in keep[:limit]]
    if len(keep) > limit:
        out.append('  ...')
    return out


def install_vscode_task(directory='.'):
    """Create .vscode/tasks.json with a bat2sh convert+run task."""
    import json
    vdir = os.path.join(directory, '.vscode')
    os.makedirs(vdir, exist_ok=True)
    cfg = {
        'version': '2.0.0',
        'tasks': [{
            'label': 'bat2sh convert',
            'type': 'shell',
            'command': ('python3 -m bat2sh "${file}" '
                        '"${fileDirname}/${fileBasenameNoExtension}.sh"'),
            'problemMatcher': [],
            'group': {'kind': 'build', 'isDefault': True},
        }],
    }
    dst = os.path.join(vdir, 'tasks.json')
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)
    print('Wrote %s' % dst)


def syntax_check(text):
    """`bash -n` the converted text; return (ok, error_output)."""
    # executes repo-trusted converted output; input audited separately
    r = subprocess.run(['bash', '-n', _write_tmp(text)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True)
    return r.returncode == 0, r.stderr


@lru_cache(maxsize=1)
def _argparser():
    import argparse

    ap = argparse.ArgumentParser(
        prog='bat2sh',
        description='Convert Windows batch files to bash scripts.')
    ap.add_argument('input', nargs='?', default=None,
                    help='Input .bat/.cmd file, directory, or - for stdin; '
                         'with no argument a piped batch script is converted '
                         'and executed immediately')
    ap.add_argument('output', nargs='?', help='Output .sh file (default: stdout)')
    ap.add_argument('-i', '--inplace', action='store_true',
                    help='Write <input>.sh next to the input file')
    ap.add_argument('-o', '--output-dir', metavar='DIR',
                    help='Write outputs into DIR (mirrors folder structure for '
                         'directories; for a single file places <name>.sh there)')
    ap.add_argument('-c', '--check', action='store_true',
                    help='Only syntax-check the converted output (no files written)')
    ap.add_argument('-r', '--run', action='store_true',
                    help='Convert and execute immediately via bash '
                         '(nothing is written to disk)')
    ap.add_argument('-d', '--debug', action='store_true',
                    help='Keep converter debug comments in the output '
                         '(output is clean by default)')
    ap.add_argument('-C', '--no-clobber', action='store_true',
                    help="Don't overwrite existing output files")
    ap.add_argument('-q', '--quiet', action='store_true',
                    help='Suppress informational messages (errors are still shown)')
    ap.add_argument('--encoding', metavar='ENC',
                    help='Force input decoding with this codec '
                         '(e.g. cp1251, latin-1); default: auto-detect')
    ap.add_argument('--target', choices=('bash', 'ps1'), default='bash',
                    help='Output language (PowerShell target is beta)')
    ap.add_argument('--path-style', choices=('wsl', 'wine', 'root'),
                    default='wsl',
                    help='Drive-letter mapping: /mnt/x | ~/.wine/drive_x '
                         '| /')
    ap.add_argument('--shebang', metavar='STR',
                    help='Interpreter line for generated scripts '
                         '(default: #!/usr/bin/env bash)')
    ap.add_argument('-x', '--executable', action='store_true',
                    help='chmod +x the written .sh files')
    ap.add_argument('--diff', action='store_true',
                    help='Print original batch and converted bash side by '
                         'side instead of writing files')
    ap.add_argument('--strict-bash', action='store_true',
                    help="Insert 'set -euo pipefail' into generated scripts")
    ap.add_argument('--analyze', action='store_true',
                    help='Compatibility audit only: report registry, '
                         'Windows binaries and service usage')
    ap.add_argument('--report', metavar='FILE',
                    help='Write a migration report (.md or .html) covering '
                         'all processed files')
    ap.add_argument('--install-vscode-task', nargs='?', const='.',
                    metavar='DIR',
                    help="Create .vscode/tasks.json for one-key conversion "
                         "in the editor")
    ap.add_argument('--runtime-layer', action='store_true',
                    help='Emit helper layer: check_errorlevel() and '
                         '/tmp drive-letter symlinks')
    ap.add_argument('-v', '--version', action='version',
                    version='bat2sh ' + __version__)
    return ap


def _process_job(args, src, out):
    """Convert one job; return (rc, stdout_text_or_None, stderr_lines)."""
    if src == '-':
        text = sys.stdin.read()
        name = '<stdin>'
    else:
        with open(src, 'rb') as f:
            text = decode_text(f.read(), encoding=args.encoding)
        name = src
        syn = ('# bat2sh: untranslatable input\n'
               "echo 'The syntax of the command is incorrect.' >&2\n"
               'exit 1\n')
    if args.target == 'ps1':
        try:
            result, _w = ps1_convert(text)
            result = result.replace('\r\n', '\n')
        except Exception as e:  # noqa: BLE001
            return 1, None, ['FAIL  %s' % name, str(e)]
        if args.run:
            return _run_script(result), None, []
        if out is None:
            return 0, result, []
        with open(out, 'w', encoding='utf-8') as f:
            f.write(result)
        return 0, None, ([] if args.quiet else ['Wrote %s' % out])

    try:
        tr = Translator()
        tr._rules = load_rules()
        result = tr.convert(text, clean=not args.debug,
                            shebang=args.shebang,
                            strict=args.strict_bash)
        stats = dict(tr.stats)
        findings = summarize(analyze(text))
        _REPORT.append((name, stats, findings))
    except Exception:
        if args.check:
            return 1, None, ['FAIL  %s' % name,
                             'conversion error: bad batch syntax']
        result = syn

    result = result.replace('\r\n', '\n')

    if args.diff:
        return 0, _side_by_side(text, result) + '\n', []

    if args.runtime_layer:
        drives = sorted({m.group(1).lower()
                         for m in re.finditer(r'\b([A-Za-z]):[\\/]',
                                              text)})
        helpers = ['check_errorlevel() { echo "$ERRORLEVEL"; }']
        for d in drives:
            tgt = {'wsl': '/mnt/%s' % d,
                   'root': '/',
                   'wine': '$HOME/.wine/drive_%s' % d}[args.path_style]
            helpers.append('mkdir -p "/tmp/bat2sh_drives/%s" && '
                           'ln -sfn "%s" "/tmp/bat2sh_drives/%s/." '
                           '2>/dev/null || true' % (d, tgt, d))
        lines = result.split('\n')
        insert = 2 if lines[0].startswith('#!') else 0
        lines[insert:insert] = helpers
        result = '\n'.join(lines)

    if args.run:
        # convert -> execute; the script's exit code becomes ours
        return _run_script(result), None, []

    if args.check:
        ok, errout = syntax_check(result)
        if not ok:
            return 1, None, ['FAIL  %s' % name, errout.rstrip('\n')]
        return 0, None, ['OK    %s' % name] + shell_hints(result)
    if out is None:
        return 0, result, []

    err = []
    if args.no_clobber and os.path.exists(out):
        if not args.quiet:
            err.append('Skip  %s (exists)' % out)
        return 0, None, err
    os.makedirs(os.path.dirname(os.path.abspath(out)) or '.', exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(result)
    if args.executable:
        try:
            os.chmod(out, 0o755)
        except OSError:
            pass
    if not args.quiet:
        err.append('Wrote %s' % out)
    return 0, None, err


def _read_source(args, src):
    if src == '-':
        return sys.stdin.read()
    with open(src, 'rb') as f:
        return decode_text(f.read(), encoding=args.encoding)


def _side_by_side(a, b, width=56):
    import textwrap
    la = textwrap.wrap(a, width) or ['']
    lb = textwrap.wrap(b, width) or ['']
    h = max(len(la), len(lb))
    la += [''] * (h - len(la))
    lb += [''] * (h - len(lb))
    out = ['batch'.ljust(width) + '| bash',
           '-' * width + '+' + '-' * width]
    out += ['%-*s| %s' % (width, x, y) for x, y in zip(la, lb)]
    return '\n'.join(out)


def main(argv=None):
    args = _argparser().parse_args(argv)
    if getattr(args, 'install_vscode_task', None):
        install_vscode_task(args.install_vscode_task)
        return 0
    shell.set_path_style(args.path_style)

    if args.input is None:
        if sys.stdin.isatty():
            _argparser().print_help(sys.stderr)
            return 1
        text = sys.stdin.read()
        try:
            result = Translator().convert(text, clean=not args.debug)
        except Exception:
            result = ('# bat2sh: untranslatable input\n'
                      "echo 'The syntax of the command is incorrect.' >&2\n"
                      'exit 1\n')
        return _run_script(result)

    if args.input is not None and args.input != '-' and \
            not os.path.exists(args.input):
        text = args.input
        try:
            result = Translator().convert(text, clean=not args.debug)
        except Exception:
            result = ('# bat2sh: untranslatable input\n'
                      "echo 'The syntax of the command is incorrect.' >&2\n"
                      'exit 1\n')
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            return 0
        if args.check:
            ok, errout = syntax_check(result)
            print(('OK    <inline>' if ok else 'FAIL  <inline>') +
                  ('\n' + errout if errout else ''))
            return 0 if ok else 1
        return _run_script(result)

    if args.analyze:
        rc_a = 0
        items = []
        for src, _out in _collect_jobs(args):
            text = _read_source(args, src)
            finds = summarize(analyze(text))
            tr = Translator()
            tr.convert(text)
            items.append((src, dict(tr.stats), finds))
            if finds:
                rc_a = 1
            print(src)
            for f in finds:
                print('  %s:%d [%s] %s\n      %s'
                      % (f['severity'], f['line'], f['id'],
                         f['message'], f['snippet']))
            if not finds:
                print('  clean')
        if args.report:
            fmt = 'html' if args.report.endswith(('.html', '.htm')) \
                else 'md'
            open(args.report, 'w', encoding='utf-8').write(
                migration_report(items, fmt))
            print('report written: %s' % args.report, file=sys.stderr)
        return rc_a

    jobs = _collect_jobs(args)
    if not jobs:
        print('No .bat/.cmd files found.', file=sys.stderr)
        return 1

    parallel = len(jobs) > 1 and not args.run and not args.diff \
        and (args.check or all(out for _s, out in jobs))

    def run_all(worker):
        rc = 0
        fails = []
        for r in worker():
            jrc, out_text, err_lines = r
            rc |= jrc
            if out_text is not None:
                sys.stdout.write(out_text)
            for ln in err_lines:
                print(ln, file=sys.stderr)
                if ln.startswith('FAIL'):
                    fails.append(ln)
        if args.report and _REPORT:
            fmt = 'html' if args.report.endswith(('.html', '.htm')) \
                else 'md'
            open(args.report, 'w', encoding='utf-8').write(
                migration_report(_REPORT, fmt))
            print('report written: %s' % args.report, file=sys.stderr)
        if fails:
            extra = len(fails) - 5
            shown = '\n'.join(fails[:5])
            if extra > 0:
                shown += '\n... and %d more' % extra
            _notify_error('bat2sh', shown)
        return rc

    if parallel:
        from concurrent.futures import ThreadPoolExecutor
        workers = min(8, (os.cpu_count() or 2), len(jobs))
        with ThreadPoolExecutor(max_workers=workers) as ex:
            return run_all(lambda: ex.map(lambda j: _process_job(args, *j),
                                          jobs))
    return run_all(lambda: (_process_job(args, src, out) for src, out in jobs))

