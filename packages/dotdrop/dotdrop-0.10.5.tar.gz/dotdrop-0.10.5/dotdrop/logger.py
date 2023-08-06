"""
author: deadc0de6 (https://github.com/deadc0de6)
Copyright (c) 2017, deadc0de6
handle logging to stdout/stderr
"""

import sys


class Logger:

    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    EMPH = '\033[33m'

    def __init__(self):
        pass

    def log(self, string, end='\n', pre=''):
        cs = self._color(self.BLUE)
        ce = self._color(self.RESET)
        sys.stdout.write('%s%s%s%s%s' % (pre, cs, string, end, ce))

    def sub(self, string):
        cs = self._color(self.BLUE)
        ce = self._color(self.RESET)
        sys.stdout.write('\t%s->%s %s\n' % (cs, ce, string))

    def emph(self, string):
        cs = self._color(self.EMPH)
        ce = self._color(self.RESET)
        sys.stderr.write('%s%s%s' % (cs, string, ce))

    def err(self, string, end='\n'):
        cs = self._color(self.RED)
        ce = self._color(self.RESET)
        sys.stderr.write('%s[ERR] %s %s%s' % (cs, string, end, ce))

    def warn(self, string, end='\n'):
        cs = self._color(self.YELLOW)
        ce = self._color(self.RESET)
        sys.stderr.write('%s[WARN] %s %s%s' % (cs, string, end, ce))

    def dry(self, string, end='\n'):
        cs = self._color(self.GREEN)
        ce = self._color(self.RESET)
        sys.stdout.write('%s[DRY] %s %s%s' % (cs, string, end, ce))

    def raw(self, string, end='\n'):
        sys.stdout.write('%s%s' % (string, end))

    def ask(self, query):
        cs = self._color(self.BLUE)
        ce = self._color(self.RESET)
        q = '%s%s%s' % (cs, query + ' [y/N] ? ', ce)
        r = input(q)
        return r == 'y'

    def _color(self, col):
        if not sys.stdout.isatty():
            return ''
        return col
