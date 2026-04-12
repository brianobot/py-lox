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
    def visit_unary(self, unary: "Unary") -> Any:
        pass

    @abstractmethod
    def visit_assign(self, assign: "Assign") -> Any:
        pass

    @abstractmethod
    def visit_binary(self, binary: "Binary") -> Any:
        pass

    @abstractmethod
    def visit_variable(self, variable: "Variable") -> Any:
        pass

    @abstractmethod
    def visit_block(self, block: "Block") -> Any:
        pass

    @abstractmethod
    def visit_expr(self, expr: "Expr") -> Any:
        pass

    @abstractmethod
    def visit_print(self, print: "Print") -> Any:
        pass

    @abstractmethod
    def visit_var(self, var: "Var") -> Any:
        pass


class Expression(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor"):
        pass


@dataclass
class Literal(Expression):
    value: Any

    def accept(self, visitor: Visitor):
        return visitor.visit_literal(self)


@dataclass
class Grouping(Expression):
    expression: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_grouping(self)


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_unary(self)


@dataclass
class Assign(Expression):
    name: Token
    value: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_assign(self)


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_binary(self)


@dataclass
class Variable(Expression):
    name: Token

    def accept(self, visitor: Visitor):
        return visitor.visit_variable(self)


class Statement(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor"):
        pass


@dataclass
class Block(Statement):
    statements: list[Statement]

    def accept(self, visitor: Visitor):
        return visitor.visit_block(self)


@dataclass
class Expr(Statement):
    expression: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_expr(self)


@dataclass
class Print(Statement):
    expression: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_print(self)


@dataclass
class Var(Statement):
    name: Token
    initializer: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_var(self)
