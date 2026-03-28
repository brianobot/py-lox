# Py-Lox

Lox Implementation as presented in the book, Crafting an Interpreter Implemented in Python

Compilation Steps
- *Lexxing (Scanning)*:
  In this step of the compilation process, We implement a functionality that takes in the source code string as input
  and breaks it into a sequence of tokens present in the source code string, characters like whitespace and comment strings are completely ignore this step, and to be useful, the actual values for tokens like numeric values are stored on the token object
  some tokens that represent punctuation are unit types, in the sense that a . is always a dot, but a number can be 1, 2 or 23245
  this value store is also applied to tokens that represent strings, along side storing the literal values for some tokens, the line
  where the token appear in the source code is stored on the token object, this helps with things like error reporting later in the compilation/interpretation phases.

- *Parsing*

- *Static Analysis*

- *Intermediate Representation*

- *Optimization*

- *Code Generation*

- *Virtual Machine*

- *Runtime*
