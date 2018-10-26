import sys
import re
import builtins
import argparse
import io
import functools
import operator

stack = []
variables = {}
lineno = 0
line = ''
defining = None

def _error(exc):
    print(type(exc).__name__, str(exc) + ' (line {} {})'.format(lineno, line), sep=': ', file=sys.stderr)
    sys.exit(1)

def _empty():
    _error(RuntimeError('stack is empty'))

def _pop():
    try:
        return stack.pop()
    except IndexError:
        _empty()

def printstack():
    """Pop and print every item on the stack."""
    _tmpstack = []
    while len(stack) > 0:
        _tmpstack.append(_pop())
    for i in _tmpstack:
        print(i)

builtins.printstack = printstack

parser = argparse.ArgumentParser(description='Run a Boa file.')
parser.add_argument('file', nargs='?', help='the Boa file to read from. If not specified, defaults to stdin.')
parser.add_argument('-C', action='store_true', help='if specified, do not parse comments in strings (i.e. treat the # and everything after as part of the string)')
cmdargs = parser.parse_args()

def run_boa(fileobj, call=lineno, ret=None):
    global lineno, line, stack, variables, defining
    lineno = call
    while 1:
        try:
            line = f.readline().rstrip('\n')
        except EOFError:
            break
        if not line:
            break
        if defining and not line.startswith('>'):
            defining[2].write(line + '\n')
            continue
        elif defining: #i.e. the line starts with >
            newfunc = functools.partial(
                run_boa, defining[2], defining[1], lineno
            )
            variables[defining[0]] = newfunc
            defining = None
            continue
        if not (cmdargs.C and line.startswith(('"', "'"))):
            line = line.partition('#')[0] #get rid of comments
        if line.startswith('<'): #start function definition
            name = line[1:]
            defining = (name, lineno + 1, io.StringIO())
        elif re.search('^[0-9]', line): #number
            try:
                num = int(line, 0)
            except ValueError:
                try:
                    num = float(line)
                except ValueError:
                    _error(SyntaxError('invalid number'))
            stack.append(num)
        elif line.startswith(('"', "'")): #string
            stack.append(line[1:])
        elif line.startswith('.'): #attribute
            o = _pop()
            a = getattr(o, line[1:])
            stack.append(a)
        elif line == '!': #call
            o = _pop()
            n = _pop()
            if not isinstance(n, int):
                _error(TypeError('number of arguments must be an integer'))
            args = []
            for i in range(n):
                args.append(_pop())
            stack.append(o(*args))
        elif hasattr(builtins, line): #builtin
            stack.append(getattr(builtins, line))
        elif hasattr(operator, line): #operator
            stack.append(getattr(operator, line))
        else: #variable
            if line not in variables: #pop from stack and set variable if name not known
                variables[line] = _pop()
            else: #append variable to stack if name known
                stack.append(variables[line])
        lineno += 1

with open(cmdargs.file) if cmdargs.file else sys.stdin as f:
    run_boa(f)
