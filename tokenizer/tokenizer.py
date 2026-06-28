import re
from dataclasses import dataclass
from collections.abc import Callable
from typing import Any


@dataclass
class Token:
    name: str
    pattern: str | None = None
    image: str | None = None
    parser: Callable[[str], Any] | None = None
    parsed: Any | None = None

    def __repr__(self):
        return (
            self.name + " " + (self.image if self.image and self.image != "\n" else "_")
        )


class Tokenizer:
    def __init__(self, text, input_tokens: list[Token]):
        self.text = text
        self.input_tokens = {t.name: t for t in input_tokens}

    def tokenize(self) -> list[Token]:
        output_tokens = []
        master_pattern = "|".join(
            f"(?P<{t.name}>{t.pattern})" for t in self.input_tokens.values()
        )

        for match in re.finditer(master_pattern, self.text):
            rule = self.input_tokens[match.lastgroup]  # type: ignore
            token: Token

            if rule.parser:
                token = Token(
                    name=rule.name,
                    pattern=rule.pattern,
                    image=match.group(),
                    parsed=rule.parser(match.group()),
                    parser=rule.parser,
                )
            else:
                token = Token(name=rule.name, pattern=rule.pattern, image=match.group())
            output_tokens.append(token)
        output_tokens.append(Token(name="eof"))

        return output_tokens
