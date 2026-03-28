from .parser import Binary, Expression, Grouping, Literal, Unary, Visitor
from .token import Token, TokenType


class ASTPrinter(Visitor):
    def print(self, expression: Expression):
        return expression.accept(self)

    def visit_binary(self, binary: "Binary"):
        return self.parenthesize(binary.operator.lexeme, binary.left, binary.right)

    def visit_literal(self, literal: "Literal"):
        if literal.value is None:
            return "nil"
        return str(literal.value)

    def visit_grouping(self, grouping: "Grouping"):
        return self.parenthesize("group", grouping.expression)

    def visit_unary(self, unary: "Unary"):
        return self.parenthesize(unary.operator.lexeme, unary.right)

    def parenthesize(self, name: str, *expressions: Expression):
        builder = f"({name}"
        for expression in expressions:
            builder += " "
            builder += str(expression.accept(self))

        builder += ")"
        return builder


if __name__ == "__main__":
    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(23)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(23.45)),
    )

    ast_printer = ASTPrinter()
    value = ast_printer.print(expression)
    print("Value", value)
