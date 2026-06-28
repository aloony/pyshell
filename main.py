from cursor import Cursor
from dataclasses import dataclass
from pathlib import Path
from tokenizer.tokenizer import Tokenizer, Token

text = Path("file.crap").read_text().strip() + "\n"


def bool_parser(bool_string) -> bool:
    return "true" in bool_string


input_tokens = [
    Token(name="eq", pattern=r"="),
    Token(name="newline", pattern=r"\n"),
    Token(name="true", pattern=r"\btrue\b", parser=bool_parser),
    Token(name="if", pattern=r"\bif\b"),
    Token(name="oparen", pattern=r"\("),
    Token(name="cparen", pattern=r"\)"),
    Token(name="false", pattern=r"\bfalse\b", parser=bool_parser),
    Token(name="lbracket", pattern=r"\{"),
    Token(name="rbracket", pattern=r"\}"),
    Token(name="colon", pattern=r":"),
    Token(name="dollar", pattern=r"\$"),
    Token(name="ident", pattern=r"\w+"),
]

tokenizer = Tokenizer(text, input_tokens)
tokens = tokenizer.tokenize()
print(tokens)


@dataclass
class Assignment:
    ident: str
    value: bool


class Parser(Cursor):
    ast: list

    def parse(self):
        self.ast = []

        while True:
            token: Token = self.peek()

            if token.name == "newline":
                ...
            elif token.name == "eof":
                break
            elif token.name == "ident":
                self.ast.append(self.assignment())
            elif token.name == "if":
                ...
            self.advance()

        return self.ast

    def block(self): ...

    def for_loop(self): ...

    def if_cond(self): ...

    def assignment(self):
        ident = self.advance()
        _eq = self.advance()
        value = self.advance()

        assert ident.name

        return Assignment(ident=ident.image, value=value.parsed)


parser = Parser(tokens)
ast = parser.parse()
print("--------------")
print(ast)
