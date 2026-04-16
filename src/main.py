import sys
from typing import Any

from .interpreter import Interpreter, RunTimeError
from .parser import Parser
from .scanner import Scanner
from .token import Token, TokenType


def green_print(value: Any):
    print("\033[92m{}\033[00m".format(value))


def yellow_print(value: Any):
    print("\033[33m{}\033[00m".format(value))


def crimson_print(value: Any):
    print("\033[31m{}\033[00m".format(value))


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
        print(
            """\033[92mInteractive Shell for Pylox: Implemented In Python Programming language by Brian Obot\033[00m"""
        )
        print("\033[92mVersion: 2026.0.1a\033[00m")
        while True:
            line = input("\033[31m>>> \033[00m")
            # if not line:
            #     break

            if line == "exit" or line == "exit()":
                break

            self.run(line)
            self.has_error = False

    def run(self, source: str):
        # the compilation pipeline
        # 1. Scanning and Tokenization
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()  # noqa

        for token in tokens:
            green_print(token)

        # 2. Parsing tokens into AST
        parser = Parser(tokens)
        statements = parser.parse()

        for statement in statements:
            yellow_print(statement)

        if self.has_error:
            return

        # 2b Run the Resolver
        # resolver = Resolver(self.interpreter)
        # resolver.resolve(statements)

        # 3. Executing the AST
        self.interpreter.interpret(statements)

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
        error_detail = f"\n[line {error.operator.line if error.operator else ''}]"
        print(error.get_message() + error_detail)
        cls.has_runtime_error = True


if __name__ == "__main__":
    Lox()
