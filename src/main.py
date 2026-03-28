import sys

from .scanner import Scanner


class Lox:
    has_error = False

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

    @classmethod
    def error(cls, line: int, message: str):
        cls.report(line, "", message)

    @classmethod
    def report(cls, line: int, where: str, message: str):
        msg = f"[line {line}] Error {where}: {message}"
        print(msg, file=sys.stderr)


if __name__ == "__main__":
    Lox()
