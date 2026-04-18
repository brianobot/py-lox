# pyright: basic
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum

from src.token import Token

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
from .interpreter import Interpreter


class FunctionType(Enum):
    NONE = ("NONE",)
    FUNCTION = "FUNCTION"


@dataclass
class Resolver(Visitor):
    interpreter: Interpreter
    scopes: deque[dict[str, bool]] = field(default_factory=deque)
    """
    The key refers to the variable being resolved and the value is a flag
    that indicate whether the variable initializer has been resolved too
    """
    current_function: FunctionType = FunctionType.NONE

    def resolve_expression(self, expression: Expression):
        expression.accept(self)

    def resolve_statement(self, statement: Statement):
        statement.accept(self)

    def resolve(self, statements: list[Statement]):
        for statement in statements:
            self.resolve_statement(statement)

    def resolve_local(self, expression: Expression, name: Token):
        for i in range(len(self.scopes) - 1, 0, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expression, len(self.scopes) - 1 - i)
                return

    def resolve_function(self, function_stmt: Function_Stmt, type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type
        self.begin_scope()
        for param in function_stmt.params:
            self.declare(param)
            self.define(param)

        self.resolve(function_stmt.body)
        self.end_scope
        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append(dict())

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if not self.scopes:
            return

        innermost_scope = self.scopes[-1]
        innermost_scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return

        innermost_scope = self.scopes[-1]
        innermost_scope[name.lexeme] = True

    def visit_block_stmt(self, block_stmt: "Block_Stmt"):
        self.begin_scope()
        self.resolve(block_stmt.statements)
        self.end_scope()
        return None

    def visit_var_stmt(self, var_stmt: "Var_Stmt"):
        self.declare(var_stmt.name)
        if var_stmt.initializer is not None:
            self.resolve_expression(var_stmt.initializer)
        self.define(var_stmt.name)
        return None

    def visit_variable(self, variable: "Variable"):
        from .main import Lox

        if self.scopes and self.scopes[-1].get(variable.name.lexeme) is False:
            Lox.error(
                variable.name, "Can't read local variable in its own initializer."
            )

        self.resolve_local(variable, variable.name)
        return None

    def visit_assign(self, assign: "Assign"):
        self.resolve_expression(assign.value)
        self.resolve_local(assign, assign.name)
        return None

    def visit_function_stmt(self, function_stmt: "Function_Stmt"):
        self.declare(function_stmt.name)
        self.define(function_stmt.name)

        self.resolve_function(function_stmt, FunctionType.FUNCTION)

    def visit_expr_stmt(self, expr_stmt: "Expr_Stmt"):
        self.resolve_expression(expr_stmt.expression)
        return None

    def visit_if_stmt(self, if_stmt: "If_Stmt"):
        self.resolve_expression(if_stmt.condition)
        self.resolve_statement(if_stmt.then_branch)
        if if_stmt.else_branch:
            self.resolve_statement(if_stmt.else_branch)

        return None

    def visit_print_stmt(self, print_stmt: "Print_Stmt"):
        self.resolve_expression(print_stmt.expression)
        return None

    def visit_return_stmt(self, return_stmt: "Return_Stmt"):
        from .main import Lox

        if self.current_function == FunctionType.NONE:
            Lox.error(return_stmt.keyword, "Can't return from top-level")

        if return_stmt.value:
            self.resolve_expression(return_stmt.value)

        return None

    def visit_while_stmt(self, while_stmt: "While_Stmt"):
        self.resolve_expression(while_stmt.condition)
        self.resolve_statement(while_stmt.body)
        return None

    def visit_logical(self, logical: "Logical"):
        self.resolve_expression(logical.left)
        self.resolve_expression(logical.right)
        return None

    def visit_unary(self, unary: "Unary"):
        self.resolve_expression(unary.right)
        return None

    def visit_literal(self, literal: "Literal"):
        return None

    def visit_binary(self, binary: "Binary"):
        self.resolve_expression(binary.left)
        self.resolve_expression(binary.right)
        return None

    def visit_grouping(self, grouping: "Grouping"):
        self.resolve_expression(grouping.expression)
        return None

    def visit_call(self, call: "Call"):
        self.resolve_expression(call.callee)

        for argument in call.arguments:
            self.resolve_expression(argument)

        return None


# if __name__ == "__main__":
#     resolver = Resolver(Interpreter())
#     resolver.resolve()
