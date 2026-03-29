# Py-Lox

Lox Implementation as presented in the book, Crafting an Interpreter Implemented in Python

Compilation Steps
- **Lexxing (Scanning)**:
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

- **Parsing**: This stage involves reading in the token stream from the lexxing stage and building an internal representation of the expressions, usually called a Syntax Tree, it's important to understand that in the lexxing stage, the unit of grammar was each character, but in the parsing stage, the unit of grammar is the token and expressions, and each node in our Syntax tree would map to a
token or an expression.

Like the scanner the parser consumes a flat sequence, but unlike the scanner, the consumed items are tokens and not characters.

*Technically*, A parser is an implementation for a language grammar that checks where a input expression is valid or not as par the grammar of the language.

Before any parsing is done, it is helpful to have a good mental representation of code first,
take the code for example
```
1 + 2 * 3 - 4
```

Looking at it, we know that following the precedence of operators, we should do 2 * 3 first and then addition and then subtraction
((1 + (2 * 3)) - 4), one way to visualize this is with a tree, with the leaf nodes being the number and the interior nodes being the connection operators

![Tree for the code above](images/tree_representation_sample.png)

Given any such tree, it's trivial to evaluate it, so intuitively, it's a workable solution to representation code as tree
to make evaluation easy. the tree must match the grammatical structure of the language.

### This is not the only way to represent code, there's another way that employs bytecodes, but this is much easier

A formal grammer thats a set of atomic units it calls alphabets and defines a set of (usually infinite) strings that are valid in that
grammar, each string is a sequence of alphabets in that grammar.

In the lexxing phase, the alphabets are the individual characters and the strings are the valid lexeme
while in the parsing phase, the alphabets are the indivudal tokens and the strings are the sequence of tokens; expression




- **Static Analysis**

- **Intermediate Representation**

- **Optimization**

- **Code Generation**

- **Virtual Machine**

- **Runtime**
