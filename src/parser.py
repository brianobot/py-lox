from typing import Any

import pytest

from .base_parser import (
    Assign,
    Binary,
    Block,
    Call,
    Expr,
    Expression,
    Grouping,
    If_Stmt,
    Literal,
    Logical,
    Print_Stmt,
    Statement,
    Unary,
    Var,
    Variable,
    While_Stmt,
)
from .token import Token, TokenType


class Parser:
    # each grammar rule from our stratified rule becomes a method in this class
    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._current = 0
        """index of next token waiting to be consumed"""

    def parse(self):
        statements: list[Statement] = []
        while not self.is_at_end():
            statements.append(self.declaration())  # type: ignore
        return statements

    def peek(self):
        return self._tokens[self._current]

    def previous(self):
        return self._tokens[self._current - 1]

    def advance(self):
        if not self.is_at_end():
            self._current += 1

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
                return self.variable_declaration()

            statement = self.statement()
        except ParseError:
            self.synchronize()
            return None

        return statement

    def statement(self) -> Statement:
        if self.match(TokenType.PRINT):
            return self.print_statement()

        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.match(TokenType.FOR):
            return self.for_loop_statement()

        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())

        return self.expression_statement()

    def block(self):
        statements: list[Statement] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())  # type: ignore

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression_statement(self):
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; after value")
        return Expr(expression)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after if.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")

        then_branch = self.statement()
        else_branch = None

        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If_Stmt(condition, then_branch, else_branch)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after 'condition'.")
        body = self.statement()

        return While_Stmt(condition, body)

    def for_loop_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")
        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition")
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clause")
        body = self.statement()

        if increment is not None:
            body = Block([body, Expr(increment)])

        if condition is None:
            condition = Literal(True)

        body = While_Stmt(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; after value")
        return Print_Stmt(value)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expression = self._or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expression, Variable):
                name = expression.name
                return Assign(name, value)

            ParseError.error(equals, "Invalid Assignment Target")

        return expression

    def _or(self):
        expression = self._and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self._and()
            expression = Logical(expression, operator, right)

        return expression

    def _and(self):
        expression = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expression = Logical(expression, operator, right)

        return expression

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

        return self.call()

    def call(self):
        expression = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expression = self.finish_call(expression)
            else:
                break

        return expression

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
            self.consume(
                TokenType.RIGHT_PAREN, "Runtime error: Expect ) after expression!"
            )
            return Grouping(expression)

        raise ParseError.error(self.peek(), "Runtime error: Expect Expression.")

    def finish_call(self, callee: "Expression"):
        arguments: list[Any] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    ParseError.error(self.peek(), "Can't have more than 255 arguments")

                arguments.append(self.expression)

        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments")
        return Call(callee, paren, arguments)

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
        return ParseError()


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

    def test_raise_exception(self):
        with pytest.raises(ParseError) as err:  # noqa
            raise ParseError.error(
                Token(TokenType.AND, "", None, 1),
                "Sample Error Message",
            )
