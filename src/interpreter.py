import time
from abc import ABC
from dataclasses import dataclass
from typing import Any

from .base_parser import (
    Assign,
    Binary,
    Block_Stmt,
    Call,
    Expr_Stmt,
    Expression,
    Function_Stmt,
    Grouping,
    If_Stmt,
    Literal,
    Logical,
    Print_Stmt,
    Return_Stmt,
    Statement,
    Unary,
    Var_Stmt,
    Variable,
    Visitor,
    While_Stmt,
)
from .environment import Environment
from .token import Token, TokenType


class LoxCallable(ABC):
    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        pass

    def arity(self) -> int:
        return 0


class BuiltIns:
    class Clock(LoxCallable):
        def call(self, interpreter: "Interpreter", arguments: list[Any]):
            return time.time()

        def arity(self) -> int:
            return 0

        def to_string(self):
            return "<native fn>"

    class ReadFile(LoxCallable):
        def call(self, interpreter: "Interpreter", arguments: list[Any]):
            return open(file=arguments[0], mode=arguments[1]).read()

        def arity(self) -> int:
            return 2

        def to_string(self):
            return "<native fn>"

    class PWD(LoxCallable):
        def call(self, interpreter: "Interpreter", arguments: list[Any]):
            import os

            return print(os.getcwd())

        def arity(self) -> int:
            return 0

        def to_string(self):
            return "<native fn>"


@dataclass
class LoxFunction(LoxCallable):
    closure: Environment
    declaration: Function_Stmt

    def call(self, interpreter: "Interpreter", arguments: list[Any]):
        environment = Environment(self.closure)
        for index in range(len(arguments)):
            environment.define(self.declaration.params[index].lexeme, arguments[index])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_except:
            return return_except.value
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def to_string(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"


class Interpreter(Visitor):
    _locals: dict[Expression, int] = dict()
    _globals = Environment()
    _environment = _globals

    def __init__(self):
        self._globals.define("pwd", BuiltIns.PWD())
        self._globals.define("clock", BuiltIns.Clock())
        self._globals.define("read_file", BuiltIns.ReadFile())

    def interpret(self, statements: list[Statement]):
        from .main import Lox

        try:
            for statement in statements:
                print(f"✅✅✅ Statement: {statement}")
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

    def look_up_variable(self, name: Token, variable: Expression):
        return self._environment.get(name)

        distance = self._locals.get(variable)
        if distance:
            return self._environment.get_at(distance, name.lexeme)
        return self._globals.get(name)

    def execute(self, statement: Statement):
        return statement.accept(self)

    def resolve(self, expression: Expression, depth: int):
        self._locals[expression] = depth

    def evaluate(self, expression: Expression):
        return expression.accept(self)

    def visit_expr_stmt(self, expr_stmt: Expr_Stmt):
        self.evaluate(expr_stmt.expression)
        return None

    def visit_variable(self, variable: Variable):
        return self.look_up_variable(variable.name, variable)

    def visit_print_stmt(self, print_stmt: Print_Stmt):
        value = self.evaluate(print_stmt.expression)
        print(self.stringify(value))
        return None

    def visit_var_stmt(self, var_stmt: Var_Stmt):
        value = None
        if var_stmt.initializer is not None:
            value = self.evaluate(var_stmt.initializer)

        self._environment.define(var_stmt.name.lexeme, value)
        return None

    def visit_literal(self, literal: "Literal"):
        return literal.value

    def visit_grouping(self, grouping: "Grouping"):
        return self.evaluate(grouping.expression)

    def visit_logical(self, logical: "Logical"):
        left = self.evaluate(logical.left)

        if logical.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(logical.right)

    def visit_while_stmt(self, while_stmt: "While_Stmt"):
        while self.is_truthy(while_stmt.condition):
            self.execute(while_stmt.body)

        return None

    def visit_return_stmt(self, return_stmt: "Return_Stmt") -> Any:
        value = None
        if return_stmt.value is not None:
            value = self.evaluate(return_stmt.value)

        raise Return(value)

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

    def visit_call(self, call: "Call"):
        callee = self.evaluate(call.callee)
        arguments = []
        for argument in call.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RunTimeError(call.paren, "Can only call function and classes")

        function: LoxCallable = callee

        if len(arguments) != function.arity():
            raise RunTimeError(
                call.paren,
                f"Expected {function.arity()} argument(s) but got {len(arguments)}",
            )

        return function.call(self, arguments)

    def visit_assign(self, assign: "Assign"):
        value = self.evaluate(assign.value)

        distance = self._locals.get(assign)
        if distance:
            self._environment.assign_at(distance, assign.name, value)
        else:
            self._globals.assign(assign.name, value)
        return value

    def visit_if_stmt(self, if_stmt: "If_Stmt") -> Any:
        if self.is_truthy(self.evaluate(if_stmt.condition)):
            self.execute(if_stmt.then_branch)
        elif if_stmt.else_branch is not None:
            self.execute(if_stmt.else_branch)

        return None

    def visit_function_stmt(self, function_stmt: "Function_Stmt"):
        function = LoxFunction(self._environment, function_stmt)
        self._environment.define(function_stmt.name.lexeme, function)
        return None

    def visit_block_stmt(self, block_stmt: "Block_Stmt"):
        from .environment import Environment

        self.execute_block(block_stmt.statements, Environment(self._environment))
        return None

    def execute_block(self, statements: list[Statement], environment: "Environment"):
        previous = self._environment
        try:
            self._environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self._environment = previous

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


@dataclass
class Return(Exception):
    value: Any


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
