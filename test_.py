from src.main import Lox


def tests_lox(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "exit")
    Lox()


a = "global"

if True:

    def func_a():
        print(a)

    func_a()
    a = "block"

    func_a()
