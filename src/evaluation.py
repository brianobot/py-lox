from .base_parser import Binary, Expression, Grouping, Literal, Unary, Visitor


class EvaluationVisitor(Visitor):
    def eval(self, expression: Expression):
        return expression.accept(self)

    def visit_binary(self, binary: "Binary"):
        return bin

    def visit_literal(self, literal: "Literal"):
        pass

    def visit_grouping(self, grouping: "Grouping"):
        pass

    def visit_unary(self, unary: "Unary"):
        pass
