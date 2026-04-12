from typing import Any

from .base_parser import (
    Assign,
    Binary,
    Expr,
    Expression,
    Grouping,
    Literal,
    Print,
    Statement,
    Unary,
    Var,
    Variable,
    Visitor,
)
from .environment import Environment
from .token import Token, TokenType


class Interpreter(Visitor):
    _environment = Environment()

    def interpret(self, statements: list[Statement]):
        from .main import Lox

        try:
            for statement in statements:
                self.execute(statement)
        except RunTimeError as err:
            return Lox.runtime_error(err)
        except Exception as err:
            runtime_error = RunTimeError(None, str(err))
            return Lox.runtime_error(runtime_error)

    def stringify(self, string: Any):
        str_form = str(string)
        if str_form.endswith(".0"):
            return str_form[:-2]
        return str_form

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
            return True

        raise RunTimeError(operator, "Operand must be a Number")

    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if isinstance(left, float) and isinstance(right, float):
            return True

        raise RunTimeError(operator, "Operands must be Numbers")

    def execute(self, statement: Statement):
        return statement.accept(self)

    def evaluate(self, expression: Expression):
        return expression.accept(self)

    def visit_expr(self, expr: Expr):
        self.evaluate(expr.expression)
        return None

    def visit_variable(self, variable: Variable):
        return self._environment.get(variable.name)

    def visit_print(self, expression: Print):
        value = self.evaluate(expression.expression)
        print(self.stringify(value))
        return None

    def visit_var(self, var: Var):
        value = None
        if var.initializer is not None:
            value = self.evaluate(var.initializer)

        self._environment.define(var.name.lexeme, value)
        return None

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
            case _:
                raise ValueError("Unexpected Unary Operator type")

    def visit_assign(self, assign: "Assign"):
        value = self.evaluate(assign.value)
        self._environment.assign(assign.name, value)
        return value

    def visit_binary(self, binary: "Binary"):
        left = self.evaluate(binary.left)
        right = self.evaluate(binary.right)

        match binary.operator.type:
            case TokenType.MINUS:
                self.check_number_operands(binary.operator, left, right)
                return left - right
            case TokenType.PLUS:
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, float) and isinstance(right, float):
                    return left + right

                raise RunTimeError(
                    binary.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.SLASH:
                self.check_number_operands(binary.operator, left, right)
                if right == 0:
                    raise RunTimeError(
                        binary.operator, "Division by Zero is not allowed"
                    )

                return left / right
            case TokenType.STAR:
                self.check_number_operands(binary.operator, left, right)
                return left * right
            case TokenType.GREATER:
                self.check_number_operands(binary.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(binary.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self.check_number_operands(binary.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(binary.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case _:
                raise ValueError("Unexpected Form")


class RunTimeError(Exception):
    def __init__(self, operator: Token | None, message: str):
        super().__init__()
        self.operator = operator
        self.message = message

    def get_message(self):
        return f"{self.operator.lexeme if self.operator else ''}: {self.message}"


class TestInterpreter:
    import pytest

    @pytest.mark.parametrize(
        "object,value", [(None, False), (False, False), (1, True), ("Hello", True)]
    )
    def test_is_truthy(self, object: Any, value: bool):
        interpreter = Interpreter()
        assert interpreter.is_truthy(object) is value

    @pytest.mark.parametrize(
        "left,right,case",
        [
            (1, 1, True),
            ("", "", True),
            ("1", 1, False),
            (None, None, True),
        ],
    )
    def test_is_equal(self, left: Any, right: Any, case: bool):
        interpreter = Interpreter()
        assert interpreter.is_equal(left, right) is case
