from typing import Any

import pytest

from .token import Token, TokenType

KEYWORDS = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.CLASS,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.line = 0
        self.start = 0
        # start at a position behind zero since zero indexes the first time
        self.current = -1

    def scan_tokens(self):
        while not self.is_at_end():
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def add_token(self, token_type: TokenType, literal: Any = None):
        text = self.source[self.start : self.current]
        token = Token(token_type, text, literal, self.line)
        self.tokens.append(token)

    def scan_token(self):
        from .main import Lox

        c = self.advance()

        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "/":
                self.add_token(TokenType.SLASH)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.is_match("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.is_match("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.is_match("") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL if self.is_match("=") else TokenType.GREATER
                )
            case "#":
                while self.peek() != "\n":
                    self.advance()
            case "\\":
                if self.is_match("*"):
                    while self.peek() != "*" and self.is_match("\\"):
                        self.advance()
            case '"':
                self.string()
            # ignore whitespace
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case _:
                if c.isdigit():
                    self.number()
                elif c.isalpha() or c == "_":
                    self.identifier()
                else:
                    Lox.error(self.line, "Unexpected Character")

    def is_match(self, expected: str):
        """
        Checks if the next character matches the expected character
        consumes the next character and return True if it's a match else return False
        """
        if self.is_at_end():
            print("At the End of the Source Code")
            return False

        if self.source[self.current + 1] != expected:
            return False

        self.current += 1
        return True

    def is_at_end(self):
        # since the current alwys starts a negative one, you reach the end of the source when you're one less that the length of the source
        return self.current >= len(self.source) - 1

    def advance(self):
        self.current += 1
        return self.source[self.current]

    def peek(self):
        if self.current == -1:  # self.is_at_end()
            return "\0"
        return self.source[self.current]

    def peek_next(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current + 1]

    def string(self):
        from .main import Lox

        self.start = self.current
        self.advance()  # this ensures that we start the check on the next character after the first quote

        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1

            self.advance()

        if self.peek() == '"':
            pass
        else:
            Lox.error(self.line, "Unterminated string.")
            return

        value = self.source[self.start + 1 : self.current]
        self.add_token(TokenType.STRING, value)

    def number(self):
        self.start = self.current

        while (self.peek().isdigit()) and not self.is_at_end():
            self.advance()

        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()

            while (self.peek().isdigit()) and not self.is_at_end():
                self.advance()

        value = self.source[self.start : self.current + 1]
        self.add_token(TokenType.NUMBER, float(value))

    def identifier(self):
        self.advance()

        while self.peek().isalnum() and not self.is_at_end():
            self.advance()

        text = self.source[self.start : self.current + 1]
        type = KEYWORDS.get(text.strip())
        if type is None:
            self.add_token(TokenType.IDENTIFIER)
        else:
            self.add_token(type)


class TestScanner:
    def test_is_match_is_true(self):
        scanner = Scanner("ABC")
        assert scanner.is_match("A")
        assert scanner.is_match("B")
        assert scanner.is_match("C")

        scanner = Scanner("123")
        assert not scanner.is_match("2")
        assert scanner.is_match("1")

    def test_is_at_end_and_advance(self):
        scanner = Scanner("")
        assert scanner.is_at_end()

        scanner = Scanner("123")
        value = scanner.advance()
        assert not scanner.is_at_end()
        assert value == "1"

        value = scanner.advance()
        assert not scanner.is_at_end()
        assert value == "2"

        value = scanner.advance()
        assert scanner.is_at_end()
        assert value == "3"

    def test_peek(self):
        scanner = Scanner("123")
        assert scanner.peek() == "\0"

        value = scanner.advance()
        assert value == "1"
        assert scanner.peek() == "1"

        value = scanner.advance()
        assert value == "2"
        assert scanner.peek() == "2"

        value = scanner.advance()
        assert value == "3"
        assert scanner.peek() == "3"

    def test_peek_next(self):
        scanner = Scanner("123")

        assert scanner.peek_next() == "1"
        scanner.advance()

        assert scanner.peek_next() == "2"
        scanner.advance()

        assert scanner.peek_next() == "3"
        scanner.advance()

        assert scanner.peek_next() == "\0"

    def test_string(self):
        scanner = Scanner('"hello"')
        value = scanner.advance()
        assert value == '"'
        scanner.string()
        assert len(scanner.tokens) == 1
        assert scanner.tokens[0].literal == "hello"

        scanner = Scanner('"hello"b')
        value = scanner.advance()
        assert value == '"'
        scanner.string()
        assert len(scanner.tokens) == 1
        assert scanner.tokens[0].literal == "hello"

    def test_number(self):
        scanner = Scanner("12345")
        value = scanner.advance()

        assert value == "1"
        scanner.number()

        assert len(scanner.tokens) == 1
        assert scanner.tokens[0].literal == 12345

        scanner = Scanner("123.456")
        value = scanner.advance()

        assert value == "1"
        scanner.number()

        assert len(scanner.tokens) == 1
        assert scanner.tokens[0].literal == 123.456

    @pytest.mark.parametrize(
        "keyword,token_type",
        [
            ("result", TokenType.IDENTIFIER),
            ("print", TokenType.PRINT),
            ("class", TokenType.CLASS),
            ("var", TokenType.VAR),
            ("if", TokenType.IF),
        ],
    )
    def test_identifier(self, keyword: str, token_type: TokenType):
        scanner = Scanner(keyword)
        value = scanner.advance()

        assert value == keyword[0]
        scanner.identifier()
        assert len(scanner.tokens) == 1

        assert scanner.tokens[0].type == token_type


if __name__ == "__main__":
    scanner = Scanner('"brian""brian"')
    tokens = scanner.scan_tokens()
    print(*tokens, sep="\n")
