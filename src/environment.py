from dataclasses import dataclass, field
from typing import Any

from .token import Token


@dataclass
class Environment:
    values: dict[str, Any] = field(default_factory=dict)

    def define(self, name: str, value: Any):
        self.values[name] = value

    def get(self, name: Token):
        from .interpreter import RunTimeError

        if self.values.get(name.lexeme):
            return self.values[name.lexeme]

        raise RunTimeError(name, f"Undefined variable {name.lexeme}.")

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        raise RuntimeError(name, f"Undefined variable {name.lexeme}.")
