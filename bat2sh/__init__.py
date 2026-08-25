__version__ = '0.3'

from .cli import decode_text, main, syntax_check
from .commands import WIN_COMMAND_MAP
from .parser import Parser
from .shell import (dos_slashes, expand_vars, split_redir, split_top_ops,
                    unescape_caret, winpath)
from .translator import Translator

__all__ = ['Translator', 'Parser', 'main', 'decode_text',
           'syntax_check', 'expand_vars',
           'dos_slashes', 'unescape_caret', 'winpath', 'split_redir',
           'split_top_ops', 'WIN_COMMAND_MAP', '__version__']
