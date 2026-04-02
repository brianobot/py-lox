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
        self.line = 1
        self.start = 0
        # start at a position behind zero since zero indexes the first time
        self.current = -1

    def scan_tokens(self):
        while not self.is_at_end():
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def add_token(self, token_type: TokenType, text: str = "", literal: Any = None):
        token = Token(token_type, text, literal, self.line)
        self.tokens.append(token)

    def scan_token(self):
        c = self.advance()

        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN, c)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN, c)
            case "{":
                self.add_token(TokenType.LEFT_BRACE, c)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE, c)
            case ",":
                self.add_token(TokenType.COMMA, c)
            case ".":
                self.add_token(TokenType.DOT, c)
            case "-":
                self.add_token(TokenType.MINUS, c)
            case "+":
                self.add_token(TokenType.PLUS, c)
            case ";":
                self.add_token(TokenType.SEMICOLON, c)
            case "*":
                self.add_token(TokenType.STAR, c)
            case "/":
                self.add_token(TokenType.SLASH, c)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self.is_match("=") else TokenType.BANG,
                    f"{c}=" if self.peek() == "=" else c,
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self.is_match("=") else TokenType.EQUAL,
                    f"{c}=" if self.peek() == "=" else c,
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self.is_match("") else TokenType.LESS,
                    f"{c}=" if self.peek() == "=" else c,
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL
                    if self.is_match("=")
                    else TokenType.GREATER,
                    f"{c}=" if self.peek() == "=" else c,
                )
            case "#":
                while self.peek() != "\n" and not self.is_at_end():
                    c = self.advance()
                    print("⚠️ Skipping ", c)
            # TODO: implement the correct version for the c-style comment
            case "\\" if self.is_match("*"):
                while (
                    self.peek() != "*" and self.peek_next() != "\\"
                ) and not self.is_at_end():
                    if self.peek() == "\n":
                        self.line += 1
                    self.advance()
            case '"':
                self.string()
            # ignore whitespace
            case "\n":
                self.line += 1
            case " " | "\r" | "\t":
                pass
            case _:
                if c.isdigit():
                    self.number()
                elif c.isalpha() or c == "_":
                    self.identifier()
                else:
                    # Lox.error(self.line, "Unexpected Character")
                    # TODO
                    pass

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

        # this keeps track of where the string started in
        # order to slice the source code correctly to get the string literal
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
        # This eliminates newlines characters found within a string
        # this support multiline strings effortlessly
        value = "".join(value.split("\n"))
        self.add_token(TokenType.STRING, value, value)

    # 2"Hello"
    # 12345
    # TODO: Correct the implementation for Number to catch numbers sitting directly beside strings
    def number(self):
        # this keeps track of where the string started in
        # order to slice the source code correctly to get the string literal
        self.start = self.current

        while self.peek().isdigit() and not self.is_at_end():
            if self.peek_next().isdigit() or self.peek_next() == ".":
                self.advance()
            else:
                break

        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()

            while self.peek_next().isdigit() and not self.is_at_end():
                self.advance()

        value = self.source[self.start : self.current + 1]
        self.add_token(TokenType.NUMBER, value, float(value))

    def identifier(self):
        self.advance()

        while self.peek().isalnum() and not self.is_at_end():
            self.advance()

        text = self.source[self.start : self.current + 1]
        type = KEYWORDS.get(text.strip())
        if type is None:
            self.add_token(TokenType.IDENTIFIER, text)
        else:
            self.add_token(type, text)


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

    @pytest.mark.parametrize(
        "string_value,literal_string",
        [
            ('"hello"', "hello"),
            ('"hello"bb', "hello"),
            ('"123245"bb', "123245"),
            ('"hello world"', "hello world"),
            ('"hello  world"', "hello  world"),
            ('"hello\n\n world"bb', "hello world"),
            ('"hello\n\n  world"bb', "hello  world"),
        ],
    )
    def test_string(self, string_value: str, literal_string: str):
        scanner = Scanner(string_value)
        value = scanner.advance()

        assert value == '"'

        scanner.string()
        assert len(scanner.tokens) == 1
        assert scanner.tokens[0].literal == literal_string

    @pytest.mark.parametrize(
        "number_value,literal_number",
        [
            ("25;", 25),
            ("123", 123),
            ("123.", 123),
            ("12.34", 12.34),
            ("12.34.", 12.34),
            ("12.34b", 12.34),
            ("12.34+", 12.34),
            ('12.34"Brian"', 12.34),
        ],
    )
    def test_number(self, number_value: str, literal_number: float):
        scanner = Scanner(number_value)
        value = scanner.advance()

        assert value == str(literal_number)[0]
        scanner.number()

        assert len(scanner.tokens) == 1
        assert scanner.tokens[0].literal == literal_number

    @pytest.mark.parametrize(
        "keyword,token_type",
        [
            ("result", TokenType.IDENTIFIER),
            ("print", TokenType.PRINT),
            ("class", TokenType.CLASS),
            ("var", TokenType.VAR),
            ("if", TokenType.IF),
            ("\nprint", TokenType.PRINT),
        ],
    )
    def test_identifier(self, keyword: str, token_type: TokenType):
        scanner = Scanner(keyword)
        value = scanner.advance()

        assert value == keyword[0]
        scanner.identifier()
        assert len(scanner.tokens) == 1

        assert scanner.tokens[0].type == token_type

    @pytest.mark.parametrize(
        "comment,expected_count",
        [
            ("#this is a comment", ""),
            ("#this is a comment\n", ""),
            ("\\* This is an inline comment *\\", ""),
        ],
    )
    def test_comments(self, comment: str, expected_count: int):
        scanner = Scanner(comment)
        scanner.scan_token()

        assert scanner.current == len(scanner.source) - 1


if __name__ == "__main__":
    scanner = Scanner('"brian"\n"brian"')
    tokens = scanner.scan_tokens()
    print(*tokens, sep="\n")
