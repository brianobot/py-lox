from typing import Any

from .base_parser import Binary, Expression, Grouping, Literal, Unary, Visitor
from .token import Token, TokenType


class Interpreter(Visitor):
    def interpret(self, expression: Expression):
        from .main import Lox

        try:
            value = self.evaluate(expression)
            print(str(value))
            return value
        except RunTimeError as err:
            return Lox.runtime_error(err)
        except Exception as err:
            runtime_error = RunTimeError(None, str(err))
            return Lox.runtime_error(runtime_error)

    def is_truthy(self, object: Any):
        if object is None:
            return False
        if isinstance(object, bool):
            return object

        return True

    def is_equal(self, left: Any, right: Any):
        return left == right

    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, float):
            return

        raise RunTimeError(operator, "Operand must be a Number")

    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if isinstance(left, float) and isinstance(right, float):
            return

        raise RunTimeError(operator, "Operands must be Numbers")

    def evaluate(self, expression: Expression):
        return expression.accept(self)

    def visit_literal(self, literal: "Literal"):
        return literal.value

    def visit_grouping(self, grouping: "Grouping"):
        return self.evaluate(grouping.expression)

    def visit_unary(self, unary: "Unary"):
        right = self.evaluate(unary.right)

        match unary.operator.type:
            case TokenType.MINUS:
                self.check_number_operand(unary.operator, right)
                return -right
            case TokenType.BANG:
                return not self.is_truthy(right)

    def visit_binary(self, binary: "Binary"):
        left = self.evaluate(binary.left)
        right = self.evaluate(binary.right)

        match binary.operator.type:
            case TokenType.MINUS:
                self.check_number_operands(binary.operator, left, right)
                return left - right
            case TokenType.SLASH:
                self.check_number_operands(binary.operator, left, right)
                return left / right
            case TokenType.STAR:
                self.check_number_operands(binary.operator, left, right)
                return left * right
            case TokenType.PLUS:
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, float) and isinstance(right, float):
                    return left + right

                raise RunTimeError(
                    binary.operator, "Operands must be two numbers or two strings."
                )

            case TokenType.GREATER:
                return left > right
            case TokenType.GREATER_EQUAL:
                return left >= right
            case TokenType.LESS:
                return left < right
            case TokenType.LESS_EQUAL:
                return left <= right
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)


class RunTimeError(Exception):
    def __init__(self, operator: Token | None, message: str):
        super().__init__()
        self.operator = operator
        self.message = message

    def get_message(self):
        return f"{self.operator.lexeme if self.operator else ''}: {self.message}"
