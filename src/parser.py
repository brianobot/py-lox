from .base_parser import (
    Binary,
    Expr,
    Grouping,
    Literal,
    Print,
    Statement,
    Unary,
    Var,
    Variable,
)
from .token import Token, TokenType


class Parser:
    # each grammar rule from our stratified rule becomes a method in this class
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements: list[Statement] = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def check(self, token_type: TokenType):
        if self.is_at_end():
            return False

        return self.peek().type == token_type

    def match(self, *token_types: TokenType):
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def variable_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable naem.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ; after declaration.")
        return Var(name, initializer)

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                pass

            return self.statement()
        except Exception:
            self.synchronize()
            return None

    def statement(self) -> Statement:
        if self.match(TokenType.PRINT):
            return self.print_statement()

        return self.expression_statement()

    def expression_statement(self):
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; after value")
        return Expr(expression)

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; after value")
        return Print(value)

    def expression(self):
        return self.equality()

    def equality(self):
        expression = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expression = Binary(expression, operator, right)

        return expression

    def comparison(self):
        expression = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expression = Binary(expression, operator, right)

        return expression

    def term(self):
        expression = self.factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expression = Binary(expression, operator, right)

        return expression

    def factor(self):
        expression = self.unary()

        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()
            expression = Binary(expression, operator, right)

        return expression

    def unary(self):
        if self.match(TokenType.MINUS, TokenType.BANG):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.STRING, TokenType.NUMBER):
            return Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expression = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ) after expression!")
            return Grouping(expression)

        return ParseError.error(self.peek(), "Expect Expression.")

    def consume(self, token_type: TokenType, message: str):
        if self.check(token_type):
            return self.advance()

        raise ParseError.error(self.peek(), message)

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            match self.peek().type:
                case (
                    TokenType.CLASS
                    | TokenType.FUN
                    | TokenType.VAR
                    | TokenType.IF
                    | TokenType.FOR
                    | TokenType.WHILE
                    | TokenType.PRINT
                    | TokenType.RETURN
                ):
                    return

            self.advance()


class ParseError(Exception):
    @classmethod
    def error(cls, token: Token, message: str):
        from .main import Lox

        Lox.error(token, message)
        raise ParseError()


class TestParser:
    def test_peek(self):
        parser = Parser(
            [
                Token(TokenType.NUMBER, lexeme="123", literal=123.0, line=0),
                Token(TokenType.EOF, lexeme="", literal=None, line=0),
            ]
        )
        token = parser.peek()
        assert token.type == TokenType.NUMBER

    def test_previous(self):
        parser = Parser(
            [
                Token(TokenType.NUMBER, lexeme="123", literal=123.0, line=0),
                Token(TokenType.EOF, lexeme="", literal=None, line=0),
            ]
        )
        parser.advance()
        token = parser.previous()
        assert token.type == TokenType.NUMBER

    def test_advance(self):
        parser = Parser(
            [
                Token(TokenType.NUMBER, lexeme="123", literal=123.0, line=0),
                Token(TokenType.EOF, lexeme="", literal=None, line=0),
            ]
        )

        token = parser.advance()
        assert token.type == TokenType.NUMBER
        assert token.literal == 123.0

    def test_is_at_end(self):
        parser = Parser(
            [
                Token(TokenType.EOF, lexeme="", literal=None, line=0),
            ]
        )

        assert parser.is_at_end() is True

    def test_check(self):
        parser = Parser(
            [
                Token(TokenType.NUMBER, lexeme="123", literal=123.0, line=0),
                Token(TokenType.EOF, lexeme="", literal=None, line=0),
            ]
        )

        assert parser.check(TokenType.NUMBER) is True

    def test_match(self):
        parser = Parser(
            [
                Token(TokenType.NUMBER, lexeme="123", literal=123.0, line=0),
                Token(TokenType.EOF, lexeme="", literal=None, line=0),
            ]
        )

        assert parser.match(TokenType.NUMBER) is True
