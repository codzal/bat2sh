"""Optional user command-replacement rules."""
import os

_PATH = os.path.expanduser("~/.config/bat2sh/config.toml")

def load_rules(_path=_PATH):
    """[commands] table from TOML, or flat key=value .conf fallback."""
    rules = {}
    try:
        if os.path.exists(_path):
            with open(_path, 'rb') as f:
                import tomllib
                rules.update(tomllib.load(f).get("commands", {}))
    except Exception:
        try:
            conf = _path.replace('.toml', '.conf')
            for line in open(conf, encoding='utf-8'):
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    rules[k.strip().lower()] = v.strip()
        except OSError:
            pass
    return rules
