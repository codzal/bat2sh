import atexit
import os
import subprocess
import sys
import tempfile
import threading
from functools import lru_cache

from . import __version__
from .translator import Translator


def decode_text(raw, encoding=None):
    """Decode batch file bytes, tolerating BOMs and common code pages.

    If *encoding* is supplied it is used directly; otherwise the first
    matching codec out of a sensible default list is chosen.
    """
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
    elif out is None and args.output_dir:
        out = os.path.join(args.output_dir,
                           os.path.splitext(os.path.basename(inp))[0] + '.sh')
    jobs.append((inp, out))
    return jobs


_CHECK_PATH = os.path.join(tempfile.gettempdir(), 'bat2sh_check_%d.sh' % os.getpid())
atexit.register(lambda: os.path.exists(_CHECK_PATH) and os.unlink(_CHECK_PATH))

_LOCK = threading.Lock()


def _write_tmp(text):
    with _LOCK, open(_CHECK_PATH, 'w') as f:
        f.write(text)
    return _CHECK_PATH


def syntax_check(text):
    """`bash -n` the converted text; return (ok, error_output)."""
    r = subprocess.run(['bash', '-n', _write_tmp(text)],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stderr


@lru_cache(maxsize=1)
def _argparser():
    import argparse

    ap = argparse.ArgumentParser(
        prog='bat2sh',
        description='Convert Windows batch files to bash scripts.')
    ap.add_argument('input', help='Input .bat/.cmd file, directory, or - for stdin')
    ap.add_argument('output', nargs='?', help='Output .sh file (default: stdout)')
    ap.add_argument('-i', '--inplace', action='store_true',
                    help='Write <input>.sh next to the input file')
    ap.add_argument('-o', '--output-dir', metavar='DIR',
                    help='Write outputs into DIR (mirrors folder structure for '
                         'directories; for a single file places <name>.sh there)')
    ap.add_argument('-c', '--check', action='store_true',
                    help='Only syntax-check the converted output (no files written)')
    ap.add_argument('-n', '--no-debug', action='store_true',
                    help='Strip converter-injected comments/placeholders; keep only '
                         'comments present in the original batch file')
    ap.add_argument('-C', '--no-clobber', action='store_true',
                    help="Don't overwrite existing output files")
    ap.add_argument('-q', '--quiet', action='store_true',
                    help='Suppress informational messages (errors are still shown)')
    ap.add_argument('--encoding', metavar='ENC',
                    help='Force input decoding with this codec '
                         '(e.g. cp1251, latin-1); default: auto-detect')
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
    try:
        result = Translator().convert(text, clean=args.no_debug)
    except Exception as e:  # noqa: BLE001
        return 1, None, ['FAIL  %s' % name,
                         'conversion error: %s' % e]

    if args.check:
        ok, errout = syntax_check(result)
        if ok:
            return 0, None, []
        return 1, None, ['FAIL  %s' % name, errout.rstrip('\n')]
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
    try:
        os.chmod(out, 0o755)
    except OSError:
        pass
    if not args.quiet:
        err.append('Wrote %s' % out)
    return 0, None, err


def main(argv=None):
    args = _argparser().parse_args(argv)

    jobs = _collect_jobs(args)
    if not jobs:
        print('No .bat/.cmd files found.', file=sys.stderr)
        return 1

    # streaming modes stay sequential; batch file jobs run in parallel
    parallel = len(jobs) > 1 and (args.check or all(out for _s, out in jobs))

    def run_all(worker):
        rc = 0
        for r in worker():
            jrc, out_text, err_lines = r
            rc |= jrc
            if out_text is not None:
                sys.stdout.write(out_text)
            for ln in err_lines:
                print(ln, file=sys.stderr)
        return rc

    if parallel:
        from concurrent.futures import ThreadPoolExecutor
        workers = min(8, (os.cpu_count() or 2), len(jobs))
        with ThreadPoolExecutor(max_workers=workers) as ex:
            return run_all(lambda: ex.map(lambda j: _process_job(args, *j),
                                          jobs))
    return run_all(lambda: (_process_job(args, src, out) for src, out in jobs))

