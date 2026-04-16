from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .token import Token


class Visitor(ABC):
    @abstractmethod
    def visit_literal(self, literal: "Literal") -> Any:
        pass

    @abstractmethod
    def visit_grouping(self, grouping: "Grouping") -> Any:
        pass

    @abstractmethod
    def visit_logical(self, logical: "Logical") -> Any:
        pass

    @abstractmethod
    def visit_unary(self, unary: "Unary") -> Any:
        pass

    @abstractmethod
    def visit_assign(self, assign: "Assign") -> Any:
        pass

    @abstractmethod
    def visit_call(self, call: "Call") -> Any:
        pass

    @abstractmethod
    def visit_binary(self, binary: "Binary") -> Any:
        pass

    @abstractmethod
    def visit_variable(self, variable: "Variable") -> Any:
        pass

    @abstractmethod
    def visit_block_stmt(self, block_stmt: "Block_Stmt") -> Any:
        pass

    @abstractmethod
    def visit_expr_stmt(self, expr_stmt: "Expr_Stmt") -> Any:
        pass

    @abstractmethod
    def visit_if_stmt(self, if_stmt: "If_Stmt") -> Any:
        pass

    @abstractmethod
    def visit_function_stmt(self, function_stmt: "Function_Stmt") -> Any:
        pass

    @abstractmethod
    def visit_while_stmt(self, while_stmt: "While_Stmt") -> Any:
        pass

    @abstractmethod
    def visit_print_stmt(self, print_stmt: "Print_Stmt") -> Any:
        pass

    @abstractmethod
    def visit_return_stmt(self, return_stmt: "Return_Stmt") -> Any:
        pass

    @abstractmethod
    def visit_var_stmt(self, var_stmt: "Var_Stmt") -> Any:
        pass


class Expression(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor") -> Any:
        pass


@dataclass
class Literal(Expression):
    value: Any

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_literal(self)


@dataclass
class Grouping(Expression):
    expression: Expression

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_grouping(self)


@dataclass
class Logical(Expression):
    left: Expression
    operator: Token
    right: Expression

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_logical(self)


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_unary(self)


@dataclass
class Assign(Expression):
    name: Token
    value: Expression

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_assign(self)


@dataclass
class Call(Expression):
    callee: Expression
    paren: Token
    arguments: list["Expression"]

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_call(self)


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_binary(self)


@dataclass
class Variable(Expression):
    name: Token

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_variable(self)


class Statement(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor") -> Any:
        pass


@dataclass
class Block_Stmt(Statement):
    statements: list[Statement]

    def accept(self, visitor: Visitor):
        return visitor.visit_block_stmt(self)


@dataclass
class Expr_Stmt(Statement):
    expression: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_expr_stmt(self)


@dataclass
class If_Stmt(Statement):
    condition: Expression
    then_branch: Statement
    else_branch: Statement

    def accept(self, visitor: Visitor):
        return visitor.visit_if_stmt(self)


@dataclass
class Function_Stmt(Statement):
    name: Token
    params: list[Token]
    body: list["Statement"]

    def accept(self, visitor: Visitor):
        return visitor.visit_function_stmt(self)


@dataclass
class While_Stmt(Statement):
    condition: Expression
    body: Statement

    def accept(self, visitor: Visitor):
        return visitor.visit_while_stmt(self)


@dataclass
class Print_Stmt(Statement):
    expression: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_print_stmt(self)


@dataclass
class Return_Stmt(Statement):
    keyword: Token
    value: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_return_stmt(self)


@dataclass
class Var_Stmt(Statement):
    name: Token
    initializer: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_var_stmt(self)
