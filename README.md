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
print# push the function object, note that builtins are predefined variables and cannot be overwritten
!# call the function object. Pops the function object, number of arguments, and *number of arguments* more items off the stack
```
Calling functions can also be used to push instances of other Python classes onto the stack:
```boa
0# push number of arguments
ClassName# push class object
!# pop ClassName and 0 off the stack and call ClassName() with 0 arguments (i.e. create an instance of ClassName) and push the result onto the stack
```
