# pyright: basic
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import cast, get_type_hints

from src.token import Token

from .base_parser import (
    Assign,
    Binary,
    Block,
    Call,
    Expr,
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
    Var,
    Variable,
    Visitor,
    While_Stmt,
)
from .interpreter import Interpreter


def overload(fn):
    return NameSpace.get_instance().register(fn)


class Function:
    def __init__(self, fn) -> None:
        self.fn = fn

    def __call__(self, *args, **kwargs):
        fn = NameSpace.get_instance().get(self.fn)
        if not fn:
            raise Exception("No Matching Function found")

        return fn(*args, **kwargs)

    def key(self):
        type_hints = get_type_hints(self.fn)

        # Exclude return type, keep only parameter type hints, convert to a hashable tuple
        param_types = tuple(v for k, v in type_hints.items() if k != "return")

        return tuple(
            [
                self.fn.__module__,
                self.fn.__qualname__,
                self.fn.__name__,
                param_types,
            ]
        )


class NameSpace:
    __instance = None

    def __init__(self):
        self.function_map = dict()
        NameSpace.__instance = self

    @staticmethod
    def get_instance() -> NameSpace:
        if NameSpace.__instance is None:
            NameSpace()
        return cast(NameSpace, NameSpace.__instance)

    def register(self, fn):
        func = Function(fn)
        self.function_map[func.key()] = fn
        return func

    def get(self, fn):
        func = Function(fn)
        return self.function_map.get(func.key())


@dataclass
class Resolver(Visitor):
    interpreter: Interpreter
    scopes: deque[dict[str, bool]] = field(default_factory=deque)

    @overload  # type: ignore[no-redef]
    def resolve(  # noqa: F811 # pyright: ignore[reportRedeclaration] # type: ignore[no-redef]
        self, statement: Statement
    ):
        statement.accept(self)

    @overload  # type: ignore[no-redef]
    def resolve(  # noqa: F811 # pyright: ignore[reportRedeclaration] # type: ignore[no-redef]
        self, statements: list[Statement]
    ):
        for statement in statements:
            self.resolve(statement)

    @overload  # type: ignore[no-redef]
    def resolve(  # noqa: F811 # pyright: ignore[reportRedeclaration] # type: ignore[no-redef]
        self, expresssion: Expression
    ):
        expresssion.accept(self)

    def resolve_local(self, expression: Expression, name: Token):
        for i in range(len(self.scopes) - 1, 0, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expression, len(self.scopes) - 1 - i)
                return

    def resolve_function(self, function_stmt: Function_Stmt):
        self.begin_scope()
        for param in function_stmt.params:
            self.declare(param)
            self.define(param)

        self.resolve(function_stmt.body)
        self.end_scope

    def begin_scope(self):
        self.scopes.append(dict())

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        scope[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        scope[name.lexeme] = True

    def visit_block(self, block: "Block"):
        self.begin_scope()
        self.resolve(block.statements)
        self.end_scope()
        return None

    def visit_var(self, var: "Var"):
        self.declare(var.name)
        if var.initializer is not None:
            self.resolve(var.initializer)
        self.define(var.name)
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
        self.resolve(assign.value)
        self.resolve_local(assign, assign.name)
        return None

    def visit_function_stmt(self, function_stmt: "Function_Stmt"):
        self.declare(function_stmt.name)
        self.define(function_stmt.name)

        self.resolve_function(function_stmt)

    def visit_expr(self, expr: "Expr"):
        self.resolve(expr.expression)
        return None

    def visit_if_stmt(self, if_stmt: "If_Stmt"):
        self.resolve(if_stmt.condition)
        self.resolve(if_stmt.then_branch)
        if if_stmt.else_branch:
            self.resolve(if_stmt.else_branch)

        return None

    def visit_print_stmt(self, print_stmt: "Print_Stmt"):
        self.resolve(print_stmt.expression)
        return None

    def visit_return_stmt(self, return_stmt: "Return_Stmt"):
        if return_stmt.value:
            self.resolve(return_stmt.value)

        return None

    def visit_while_stmt(self, while_stmt: "While_Stmt"):
        self.resolve(while_stmt.condition)
        self.resolve(while_stmt.body)
        return None

    def visit_logical(self, logical: "Logical"):
        self.resolve(logical.left)
        self.resolve(logical.right)
        return None

    def visit_unary(self, unary: "Unary"):
        self.resolve(unary.right)
        return None

    def visit_literal(self, literal: "Literal"):
        return None

    def visit_binary(self, binary: "Binary"):
        return None

    def visit_grouping(self, grouping: "Grouping"):
        return None

    def visit_call(self, call: "Call"):
        return None
