# Simple Compiler using python to compile HelloWorld language
#### Author: Aaron
#### Update Date: Dec 24 2024
#### Course: Compiler Design
#### Language: python
#### Reference: https://austinhenley.com/blog/teenytinycompiler1.html

This tutorial is very helpful for beginner who are learning Compiler Design. Strong recommendation.

### How to use this document
Step 1: Clone this repository and import the lex.py in your code

Step 2: Open your terminal and type this command:
    
    bash build.sh <ExecutedFile>

Example:
![image](img/img1.png)


### The Language would look like
```HellowWorld
    PRINT"Here is example 3: add(10, 20)"
    LET a = 10
    LET b = 20
    FUNC add(a, b)
        LET c = a + b
        RETURN c
    ENDFUNC
    PRINT add(a, b)
```