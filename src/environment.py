from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, cast

from .token import Token


@dataclass
class Environment:
    enclosing: Optional[Environment] = None
    values: dict[str, Any] = field(default_factory=dict)

    def define(self, name: str, value: Any):
        self.values[name] = value

    def get(self, name: Token):
        from .interpreter import RunTimeError

        if self.values.get(name.lexeme) is not None:
            return self.values[name.lexeme]

        if self.enclosing:
            return self.enclosing.get(name)

        raise RunTimeError(name, f"Undefined variable {name.lexeme}.")

    def get_at(self, distance: int, name: str):
        return cast(Environment, self.ancestor(distance)).values.get(name)

    def ancestor(self, distance: int):
        environment = self
        i = 0
        while i < distance:
            environment = cast(Environment, environment.enclosing)
            i += 1
        return environment

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing:
            self.enclosing.assign(name, value)
            return

        raise RuntimeError(name, f"Undefined variable {name.lexeme}.")

    def assign_at(self, distance: int, name: Token, value: Any):
        cast(Environment, self.ancestor(distance)).values[name.lexeme] = value


if __name__ == "__main__":
    env = Environment()
