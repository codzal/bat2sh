import re

from .shell import expand_vars, fix_redir, split_args, split_redir, winpath


def cmd_taskkill(args):
    a = expand_vars(args.strip())
    a = re.sub(r'/pid\s+', '', a, flags=re.IGNORECASE)
    a = re.sub(r'/im\s+', '', a, flags=re.IGNORECASE)
    a = re.sub(r'/f\b', '', a, flags=re.IGNORECASE).strip()
    return 'kill %s' % a


def cmd_xcopy(args):
    a = re.sub(r'/[a-z]\b', '', args, flags=re.IGNORECASE).strip()
    parts = split_args(a)
    if len(parts) >= 2:
        return 'cp -r "%s" "%s"' % (winpath(parts[0]), winpath(parts[-1]))
    return 'cp -r ' + expand_vars(a)


def cmd_timeout(args):
    a = re.sub(r'/t\s*', '', args, flags=re.IGNORECASE).strip()
    a = re.sub(r'/nobreak', '', a, flags=re.IGNORECASE).strip()
    return 'sleep ' + expand_vars(a)


def cmd_setx(args):
    a = expand_vars(args.strip())
    m = re.split(r'\s+', a, 1)
    if len(m) == 2:
        return 'export %s=%s' % (m[0], m[1].strip('"'))
    return 'export ' + a


def cmd_mklink(args):
    hard = bool(re.search(r'(^|\s)/h(?=\s|$)', args, re.IGNORECASE))
    a = re.sub(r'/(d|h|j)\b', '', args, flags=re.IGNORECASE).strip()
    parts = split_args(a)
    if len(parts) >= 2:
        link = parts[0]
        target = ' '.join(parts[1:])
        opt = '' if hard else '-s '
        return 'ln %s%s "%s"' % (opt, winpath(target), winpath(link))
    return 'ln %s%s' % ('-s ' if not hard else '', expand_vars(a))


def cmd_net(args):
    """Best-effort mapping of the most common `net` subcommands."""
    a = args.strip()
    cmdpart, redir = split_redir(a)
    r = (' ' + fix_redir(redir)) if redir else ''
    toks = split_args(cmdpart)
    if not toks:
        return ':  # net'
    sub = toks[0].lower()
    rest = ' '.join(toks[1:])
    rest = expand_vars(rest)
    if sub == 'user':
        return ('id ' + rest if rest else 'getent passwd') + r
    if sub == 'localgroup':
        return ('getent group ' + rest if rest else 'getent group') + r
    if sub == 'share':
        return ('df -h ' + rest if rest else 'mount -l') + r
    if sub == 'use':
        return ('mount ' + rest) + r
    if sub == 'start':
        return 'systemctl start ' + rest + r
    if sub == 'stop':
        return 'systemctl stop ' + rest + r
    if sub == 'view':
        return ':  # net view (use: smbclient -L //host)' + r
    if sub == 'statistics':
        return ':  # net statistics (use: sar / vmstat)' + r
    if sub == 'time':
        return 'date' + r
    return ':  # net %s is not emulated' % sub




def cmd_attrib(args):
    """attrib +r/-r/+x/+h -> chmod / dot-file renames."""
    a = expand_vars(args.strip())
    plus = set(re.findall(r'\+([hrsx])', a, re.I))
    minus = set(re.findall(r'-([hrsx])', a, re.I))
    paths = split_args(re.sub(r'[+-][hrsxa]\b', '', a,
                              flags=re.IGNORECASE)) or ['*']
    out = []
    for raw in paths:
        p = winpath(raw)
        if 'r' in plus:
            out.append('chmod -w -- "%s"' % p)
        if 'x' in plus or 's' in plus:
            out.append('chmod +x -- "%s"' % p)
        if 'r' in minus:
            out.append('chmod +w -- "%s"' % p)
        if 'x' in minus or 's' in minus:
            out.append('chmod -x -- "%s"' % p)
        if 'h' in plus:
            out.append('f="%s"; case "$f" in */*) d="${f%%/*}"; b="${f##*/}";;'
                       ' *) d="." b="$f";; esac; '
                       'mv -n -- "$f" "$d/.${b#.}"' % p)
        if 'h' in minus:
            out.append('f="%s"; b="${f##*/}"; d="${f%%"$b"}"; '
                       '[ "${b#.}" != "$b" ] && mv -n -- "$f" "$d/${b#.}"'
                       % p)
    if not out:
        return 'ls -ld -- ' + ' '.join('"%s"' % winpath(x) for x in paths)
    return ' && '.join(out)


def cmd_icacls(args):
    """Basic ACL verbs -> chmod."""
    toks = split_args(expand_vars(args.strip()))
    if not toks:
        return ':  # icacls'
    path = winpath(toks[0])
    out = []
    for t in toks[1:]:
        tl = t.lower()
        if tl == '/reset':
            out.append('chmod -R u+rwX -- "%s"' % path)
        elif tl.startswith('/grant'):
            spec = t.split(':', 1)[1] if ':' in t else ''
            perms = (spec.split('(')[-1].rstrip(')').upper()
                     if '(' in spec else 'F')
            bits = {'R': 'r', 'W': 'w', 'X': 'x', 'F': 'rwx', 'M': 'rwx'}
            mode = ''.join(sorted({bits[c] for c in perms if c in bits}))
            if mode:
                out.append('chmod u+%s -- "%s"' % (mode, path))
        elif tl.startswith('/deny'):
            out.append('chmod u-w -- "%s"' % path)
    if not out:
        out = ['ls -ld -- "%s"' % path]
    return ' && '.join(out)


def cmd_assoc(args):
    """File associations via xdg-mime."""
    t = split_args(expand_vars(args.strip()))
    if not t:
        return ':  # assoc'
    cur = t[0]
    if '=' in cur:
        ext, val = cur.split('=', 1)
        ext = ext if ext.startswith('.') else '.' + ext
        target = val if '/' in val or val.endswith('.desktop') \
            else val + '.desktop'
        return 'xdg-mime default "%s" "%s"' % (target, ext)
    ext = cur if cur.startswith('.') else '.' + cur
    return ('xdg-mime query default '
            '"$(xdg-mime query filetype *%s 2>/dev/null | head -n1)"' % ext)


def cmd_ftype(args):
    e = expand_vars(args.strip())
    if not e:
        return ('grep -h "^MimeType=" ~/.local/share/applications/*.desktop '
                '2>/dev/null || true')
    return ':  # ftype %s (handlers live in *.desktop files)' % e


def cmd_subst(args):
    """subst X: [path] -> symlink under ~/.local/share/bat2sh/drives."""
    t = split_args(expand_vars(args.strip()))
    if not t:
        return ':  # subst'
    drv = t[0].rstrip(':').lower()
    link = '$HOME/.local/share/bat2sh/drives/%s' % drv
    if len(t) > 1 and t[1].lower() != '/d':
        tgt = winpath(t[1])
        return ('mkdir -p "$HOME/.local/share/bat2sh/drives" && '
                'ln -sfn "%s" "%s"' % (tgt, link))
    if any(x.lower() == '/d' for x in t[1:]):
        return 'rm -f "%s"' % link
    return 'readlink "%s" || true' % link


WIN_COMMAND_MAP = {
    'setlocal': lambda a: ':  # setlocal (no-op; delayed expansion always on)',
    'endlocal': lambda a: ':  # endlocal (no-op)',
    'shift': lambda a: 'ARGS=("${ARGS[@]:1}")',
    'title': lambda a: ':  # title %s' % expand_vars(a),
    'color': lambda a: ':  # color (no-op)',
    'ver': lambda a: 'uname -a',
    'vol': lambda a: 'df -h .',
    'hostname': lambda a: 'hostname',
    'whoami': lambda a: 'whoami',
    'sort': lambda a: 'sort ' + expand_vars(a),
    'more': lambda a: 'less ' + expand_vars(a),
    'tree': lambda a: 'tree ' + expand_vars(a),
    'ping': lambda a: 'ping ' + expand_vars(a),
    'netstat': lambda a: 'netstat ' + expand_vars(a),
    'nslookup': lambda a: 'nslookup ' + expand_vars(a),
    'tracert': lambda a: 'traceroute ' + expand_vars(a),
    'pathping': lambda a: 'ping ' + expand_vars(a),
    'systeminfo': lambda a: 'uname -a',
    'tasklist': lambda a: 'ps aux',
    'taskkill': cmd_taskkill,
    'attrib': cmd_attrib,
    'icacls': cmd_icacls,
    'cacls': cmd_icacls,
    'assoc': cmd_assoc,
    'ftype': cmd_ftype,
    'subst': cmd_subst,
    'fc': lambda a: 'diff ' + expand_vars(a),
    'comp': lambda a: 'cmp ' + expand_vars(a),
    'xcopy': cmd_xcopy,
    'robocopy': cmd_xcopy,
    'timeout': cmd_timeout,
    'setx': cmd_setx,
    'ipconfig': lambda a: 'ip -br addr' if '/all' in a.lower() else 'ip addr',
    'chcp': lambda a: ':  # chcp',
    'mode': lambda a: ':  # mode',
    'label': lambda a: ':  # label',
    'prompt': lambda a: ':  # prompt',
    'sc': lambda a: 'systemctl ' + expand_vars(a),
    'where': lambda a: 'which ' + expand_vars(a),
    'mklink': cmd_mklink,
    'runas': lambda a: 'sudo ' + expand_vars(re.sub(r'/user:\S+', '', a, flags=re.IGNORECASE).strip()),
    'shutdown': lambda a: 'shutdown ' + expand_vars(a),
    'logoff': lambda a: 'exit',
    'replace': lambda a: 'cp ' + expand_vars(a),
    'driverquery': lambda a: 'lsmod',
    'doskey': lambda a: ':  # doskey (define a shell alias instead)',
    'net': cmd_net,
    'net1': cmd_net,
    'schtasks': lambda a: ':  # schtasks (use cron) is not emulated',
    'gpupdate': lambda a: ':  # gpupdate is not emulated',
    'gpresult': lambda a: ':  # gpresult is not emulated',
    'format': lambda a: ':  # format is not emulated',
    'chkdsk': lambda a: ':  # chkdsk (use fsck) is not emulated',
    'verify': lambda a: ':  # verify is not emulated',
    'taskmgr': lambda a: ':  # taskmgr (use htop/top) is not emulated',
    'control': lambda a: ':  # control panel is not emulated',
    'diskpart': lambda a: ':  # diskpart is not emulated',
    'at': lambda a: ':  # at (use cron) is not emulated',
    'bitsadmin': lambda a: ':  # bitsadmin is not emulated',
    'powercfg': lambda a: ':  # powercfg is not emulated',
    'wmic': lambda a: ':  # wmic is not emulated',
    'netsh': lambda a: ':  # netsh (use ip / networkctl)',
    'nbtstat': lambda a: ':  # nbtstat (use nmblookup)',
    'getmac': lambda a: 'ip -o link',
    'arp': lambda a: 'arp ' + expand_vars(a),
    'route': lambda a: 'route ' + expand_vars(a),
    'telnet': lambda a: 'telnet ' + expand_vars(a),
    'ftp': lambda a: 'ftp ' + expand_vars(a),
    'tftp': lambda a: 'tftp ' + expand_vars(a),
    'ssh': lambda a: 'ssh ' + expand_vars(a),
    'scp': lambda a: 'scp ' + expand_vars(a),
    'sftp': lambda a: 'sftp ' + expand_vars(a),
    'curl': lambda a: 'curl ' + expand_vars(a),
    'wget': lambda a: 'wget ' + expand_vars(a),
    'ps': lambda a: 'ps ' + expand_vars(a),
    'kill': lambda a: 'kill ' + expand_vars(a),
    'mount': lambda a: 'mount ' + expand_vars(a),
    'umount': lambda a: 'umount ' + expand_vars(a),
    'df': lambda a: 'df ' + expand_vars(a),
    'du': lambda a: 'du ' + expand_vars(a),
    'free': lambda a: 'free ' + expand_vars(a),
    'uptime': lambda a: 'uptime',
    'uname': lambda a: 'uname ' + expand_vars(a),
    'who': lambda a: 'who ' + expand_vars(a),
    'w': lambda a: 'w',
    'last': lambda a: 'last ' + expand_vars(a),
    'crontab': lambda a: 'crontab ' + expand_vars(a),
    'service': lambda a: 'service ' + expand_vars(a),
    'useradd': lambda a: 'useradd ' + expand_vars(a),
    'userdel': lambda a: 'userdel ' + expand_vars(a),
    'passwd': lambda a: 'passwd ' + expand_vars(a),
    'groupadd': lambda a: 'groupadd ' + expand_vars(a),
    'chmod': lambda a: 'chmod ' + expand_vars(a),
    'chown': lambda a: 'chown ' + expand_vars(a),
    'tar': lambda a: 'tar ' + expand_vars(a),
    'gzip': lambda a: 'gzip ' + expand_vars(a),
    'tail': lambda a: 'tail ' + expand_vars(a),
    'head': lambda a: 'head ' + expand_vars(a),
    'wc': lambda a: 'wc ' + expand_vars(a),
    'tee': lambda a: 'tee ' + expand_vars(a),
    'sed': lambda a: 'sed ' + expand_vars(a),
    'awk': lambda a: 'awk ' + expand_vars(a),
    'cut': lambda a: 'cut ' + expand_vars(a),
    'tr': lambda a: 'tr ' + expand_vars(a),
    'env': lambda a: 'env ' + expand_vars(a),
    'umask': lambda a: 'umask ' + expand_vars(a),
    'touch': lambda a: 'touch ' + expand_vars(a),
}
