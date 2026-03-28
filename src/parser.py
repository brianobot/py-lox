from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .token import Token


class Visitor(ABC):
    @abstractmethod
    def visit_binary(self, binary: "Binary") -> Any:
        pass

    @abstractmethod
    def visit_grouping(self, grouping: "Grouping") -> Any:
        pass

    @abstractmethod
    def visit_literal(self, literal: "Literal") -> Any:
        pass

    @abstractmethod
    def visit_unary(self, unary: "Unary") -> Any:
        pass


class Expression(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor"):
        pass


@dataclass
class Binary(Expression):
    left: Expression
    operator: Token
    right: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_binary(self)


@dataclass
class Grouping(Expression):
    expression: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_grouping(self)


@dataclass
class Literal(Expression):
    value: Any

    def accept(self, visitor: Visitor):
        return visitor.visit_literal(self)


@dataclass
class Unary(Expression):
    operator: Token
    right: Expression

    def accept(self, visitor: Visitor):
        return visitor.visit_unary(self)
