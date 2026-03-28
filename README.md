# Py-Lox

Lox Implementation as presented in the book, Crafting an Interpreter Implemented in Python

Compilation Steps
- *Lexxing (Scanning)*:
  In this step of the compilation process, We implement a functionality that takes in the source code string as input
  and breaks it into a sequence of tokens present in the source code string, characters like whitespace and comment strings are completely ignore this step, and to be useful, the actual values for tokens like numeric values are stored on the token object
  some tokens that represent punctuation are unit types, in the sense that a . is always a dot, but a number can be 1, 2 or 23245
  this value store is also applied to tokens that represent strings, along side storing the literal values for some tokens, the line
  where the token appear in the source code is stored on the token object, this helps with things like error reporting later in the compilation/interpretation phases.

  Example:
  ```
  # Source Code
  var name = "Brian Obot";
  print name;

  var age = 25;
  print age
  ```

  give this sample source code, which by the way is a valid syntax for the py-lox being built in the course of this course,
  when this code is passed to the lexxer, it reads the characters and produces a stream of token that matches the ones shown below

  ```
Token(type=<TokenType.VAR: 37>, lexeme='var', literal=None, line=1)
Token(type=<TokenType.IDENTIFIER: 20>, lexeme='var name', literal=None, line=1)
Token(type=<TokenType.EQUAL: 14>, lexeme='var name ', literal=None, line=1)
Token(type=<TokenType.STRING: 21>, lexeme='"Brian Obot is the developing', literal='Brian Obot is the developing', line=1)
Token(type=<TokenType.SEMICOLON: 9>, lexeme='"Brian Obot is the developing"', literal=None, line=1)
Token(type=<TokenType.IDENTIFIER: 20>, lexeme='"Brian Obot is the developing";\nprint', literal=None, line=2)
Token(type=<TokenType.IDENTIFIER: 20>, lexeme='"Brian Obot is the developing";\nprint name', literal=None, line=2)
Token(type=<TokenType.IDENTIFIER: 20>, lexeme='"Brian Obot is the developing";\nprint name;\n\nvar', literal=None, line=4)
Token(type=<TokenType.IDENTIFIER: 20>, lexeme='"Brian Obot is the developing";\nprint name;\n\nvar age', literal=None, line=4)
Token(type=<TokenType.EQUAL: 14>, lexeme='"Brian Obot is the developing";\nprint name;\n\nvar age ', literal=None, line=4)
Token(type=<TokenType.NUMBER: 22>, lexeme='2', literal=25.0, line=4)
Token(type=<TokenType.SEMICOLON: 9>, lexeme='25', literal=None, line=4)
Token(type=<TokenType.IDENTIFIER: 20>, lexeme='25;\nprint', literal=None, line=5)
Token(type=<TokenType.IDENTIFIER: 20>, lexeme='25;\nprint age', literal=None, line=5)
Token(type=<TokenType.EOF: 39>, lexeme='', literal=None, line=5)
  ```

  for the acute reader, you might notice an error with parsing print function, I have just temporarily given up and fixing that to maintain learning progress at all cost, i would definitely resolve that soon, also the lexeme for the tokens are not correct

- *Parsing*

- *Static Analysis*

- *Intermediate Representation*

- *Optimization*

- *Code Generation*

- *Virtual Machine*

- *Runtime*
