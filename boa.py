# --------- /-------\ +-------\ /-------\
#     |     |       | |       | |       |
#     |     |       | |       | |       |
#     |     |       | |       | |       |
#     |     |       | |       | |       |
#     |     \-------/ +-------/ \-------/
# LAMBDA AND FUNCTOOLS.PARTIAL HAVE DIFFERENT SEMANTICS
# COMBINE THEM
import sys
import re
import builtins
import argparse
from functools import partial
from contextlib import nullcontext
import operator

def _error(exc, lineno):
    print(type(exc).__name__, str(exc) + ' (line {})'.format(lineno), sep=': ', file=sys.stderr)
    raise SystemExit(1)

parser = argparse.ArgumentParser(description='Run a Boa file.')
parser.add_argument('file', nargs='?',
    help='the Boa file to read from. If not specified, defaults to stdin.')
parser.add_argument('-C', action='store_true',
    help='if specified, do not parse comments in strings (i.e. treat the \
# and everything after as part of the string)')
cmdargs = parser.parse_args()

def compile_boa(fileobj):
    funcs = []
    ops = []
    stack = []
    variables = {}

    def _pop(ln):
        try:
            return stack.pop()
        except IndexError:
            _error(RuntimeError('stack is empty'), ln)
    def app(val, ln):
        #print('appending', val, '; line', ln)
        stack.append(val)
    def gtr(l, ln):
        #print('getattr', l, '; line', ln)
        stack.append(getattr(_pop(ln), l))
    def lecall(ln):
        o = _pop(ln)
        n = _pop(ln)
        if not isinstance(n, int):
            _error(TypeError('number of arguments must be an integer'), ln)
        args = []
        for i in range(n):
            args.append(_pop(ln))
        #print(o, '(', *args, '); line ', ln, sep='')
        stack.append(o(*args))
    def gbr(a, l, ln):
        #print('get builtin/op', l, '; line', ln)
        stack.append(getattr(a, l))
    class BoaBuiltins:
        @staticmethod
        def p(ln):
            try:
                print(stack[-1])
            except IndexError:
                _error(RuntimeError('stack is empty'), ln)
        @staticmethod
        def ps(ln):
            _tmpstack = []
            while len(stack) > 0:
                _tmpstack.append(_pop(ln))
            for i in _tmpstack:
                print(i)
        @staticmethod
        def s(ln):
            #print('swap on line', ln)
            stack.insert(-1, _pop(ln))
        @staticmethod
        def o(ln):
            #print('silent pop on line', ln)
            _pop(ln)
    def levar(l, ln):
        #print('var', l, '; line', ln)
        if l not in variables:
            variables[l] = _pop(ln)
        else:
            stack.append(variables[l])
    for lineno, line in enumerate(fileobj):
        line = line.rstrip('\n')
        if not (cmdargs.C and line.startswith(('"', "'"))) and '#' in line:
            line = line.rpartition('#')[0]
            if not line.rstrip():
                break
        if line.startswith('<'): #start func
            funcs.append((line[1:], [lineno + 1]))
            ops.append('<')
        elif line.startswith('>'): #return
            if len(funcs[-1][-1]) > 1:
                _error(SyntaxError('return outside function'))
            funcs[-1][-1].append(lineno)
            ops.append('>')
        elif re.search('^[0-9]', line): #number
            try:
                num = int(line, 0)
            except ValueError:
                try:
                    num = float(line)
                except ValueError:
                    _error(SyntaxError('invalid number'), lineno)
            ops.append(partial(app, num, lineno))
        elif line.startswith(("'", '"')): #string
            ops.append(partial(app, line[1:], lineno))
        elif line.startswith('.'): #attrib
            ops.append(partial(gtr, line[1:], lineno))
        elif line == '!': #call function object
            ops.append(partial(lecall, lineno))
        elif line == '!!': #shorthand boa func
            ops.append(partial(app, 0, lineno))
            ops.append(partial(BoaBuiltins.s, lineno))
            ops.append(partial(lecall, lineno))
            ops.append(partial(BoaBuiltins.o, lineno))
        elif hasattr(builtins, line):
            ops.append(partial(gbr, builtins, line, lineno))
        elif line.startswith(':'):
            try:
                ops.append(partial(getattr(BoaBuiltins, line[1:]), lineno))
            except AttributeError:
                _error(SyntaxError('invalid syntax'), lineno)
        elif hasattr(operator, line):
            ops.append(partial(gbr, operator, line, lineno))
        else:
            ops.append(partial(levar, line, lineno))
    if funcs and len(funcs[-1][-1]) != 2:
        _error(SyntaxError('gosub without return'), funcs[-1][-1][-1])
    funcs = {k: partial(run_boa, ops[l1:l2]) for k, (l1, l2) in funcs}
    variables.update(funcs)
    return ops

def run_boa(opi):
    dont_run = 0
    for i in opi:
        if i == '<':
            dont_run += 1
        elif i == '>':
            dont_run -= 1
        elif dont_run < 1:
            i()

with open(cmdargs.file) if cmdargs.file else nullcontext(sys.stdin) as f:
    run_boa(compile_boa(f))
