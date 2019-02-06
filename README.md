# Boa
Boa is a stack-based programming language alternative to Python.

# Usage
Pushing items onto the stack:
```boa
10
"string
```
Setting variables:
```boa
10# push 10 onto the stack
number# pop an item from the stack and set the number variable to the item
```
Getting variables:
```boa
number# since number is now defined, push the value of number onto the stack
```
Calling functions:
```boa
#push an argument
"Hello World!
1# push the number of arguments
print# push the function object. Note that builtins are predefined variables and cannot be overwritten.
!# call the function object. Pops the function object, number of arguments, and *number of arguments* more items off the stack, and pushes return value onto stack
:o# silently drop the last item of the stack (return value from print, which is None). Not necessary at the end of a program, but is good practice.
```
Calling functions can also be used to push instances of other Python classes onto the stack:
```boa
4#push 2nd argument
3#push 1st argument
2# push number of arguments
complex# push class object
!# pop complex and 2 off the stack and call ClassName() with 2 arguments (i.e. create an instance of complex(3, 4)) and push the result onto the stack
num# store (3+4j) in "num"
num# push back onto stack
1# push number of arguments
print# push function
!# call and push ret to stack
:o# drop None
num# push onto stack again
1# push number of arguments
abs# push function
!# call and push ret (5) to stack
1# push number of arguments
print# push function
!# call and push ret (None) to stack
:o# drop None
```
