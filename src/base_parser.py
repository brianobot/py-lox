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
    def visit_binary(self, binary: "Binary") -> Any:
        pass

    @abstractmethod
    def visit_expr(self, expr: "Expr") -> Any:
        pass

    @abstractmethod
    def visit_print(self, expr: "Print") -> Any:
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
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_binary(self)


class Statement(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor"):
        pass


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
