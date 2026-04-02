import sys

from .interpreter import Interpreter, RunTimeError
from .parser import Parser
from .printer import ASTPrinterVisitor
from .scanner import Scanner
from .token import Token, TokenType


class Lox:
    has_error = False
    has_runtime_error = False

    interpreter = Interpreter()

    def __init__(self):
        if len(sys.argv) > 2:
            print("Usage: py_lox [script]")
            exit(64)

        elif len(sys.argv) == 2:
            self.run_file(sys.argv[1])

        else:
            self.run_prompt()

    def run_file(self, filename: str):
        print("Running File: ", filename)
        if self.has_error:
            exit(65)
        if self.has_runtime_error:
            exit(70)
        with open(filename) as file:
            self.run(file.read())

    def run_prompt(self):
        print("Running Prompt")
        while True:
            line = input("> ")
            if not line:
                break
            self.run(line)
            self.has_error = False

    def run(self, source: str):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)

        parser = Parser(tokens)
        expression = parser.parse()

        if not expression:
            print("Invalid Expression: ", expression)
            return None

        ast_printer = ASTPrinterVisitor()
        tree = ast_printer.print(expression)
        print("AST\n", tree)

        value = self.interpreter.interpret(expression)
        print("----------------")
        print(f"Value = {value}")
        print("----------------")

    @classmethod
    def error(cls, token: Token, message: str):
        if token.type == TokenType.EOF:
            return cls.report(token.line, "at end", message)
        else:
            return cls.report(token.line, f"at '{token.lexeme}'", message)

    @classmethod
    def report(cls, line: int, where: str, message: str):
        msg = f"[line {line}] Error {where}: {message}"
        print(msg, file=sys.stderr)

    @classmethod
    def runtime_error(cls, error: RunTimeError):
        print(
            error.get_message()
            + f"\n[line {error.operator.line if error.operator else ''}]"
        )
        cls.has_runtime_error = True


if __name__ == "__main__":
    Lox()
