from src.main import Lox


def tests_lox(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "exit")
    Lox()
