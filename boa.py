import sys
import re
import builtins

stack = []
variables = {}
lineno = 0
line = ''

def _error(exc):
    raise exc

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

with open(sys.argv[1]) as f:
    while 1:
        lineno += 1
        try:
            line = f.readline().rstrip('\n')
        except EOFError:
            break
        if re.search('^[0-9]', line): #number
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
        else: #variable
            if line not in variables: #pop from stack and set variable if name not known
                variables[line] = _pop()
            else: #append variable to stack if name known
                stack.append(variables[line])
