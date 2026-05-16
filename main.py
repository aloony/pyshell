#!/usr/bin/env python
from pathlib import Path
from enum import Enum
import tokens
import pudb
import rich


def inspect(obj):
    rich.inspect(obj, all=True)


class EOF(Exception): ...


class EOL(Exception): ...


class SubstringNotFound(Exception): ...


class Command:
    def __init__(self, name: str, args: list[str]):
        self.name = name
        self.args = args

    def __repr__(self):
        arg_string = (" " + " ".join(self.args)) if self.args else ""
        return f"{self.name}{arg_string}"


class Reader:
    def __init__(self, text: str):
        self.text = text
        self.i = 0

    def step(self, n: int = 1):
        self.i += n

        if self.i == len(self.text):
            raise EOF()

    def read(self, start: int = 0, end: int = 0, advance=True) -> str:
        start = start or self.i
        end = end or self.i + 1
        if advance:
            self.i = end
        try:
            return self.text[start:end]
        except IndexError:
            raise EOF()

    def read_untill(self, sub: str, start: int = 0, end: int = 0) -> str:
        start = start or self.i
        end = self.text.find(sub, start)
        if end == -1:
            raise SubstringNotFound()

        return self.read(start, end)

    def repr(self):
        print(self.text[self.i :])


class State(Enum):
    ANY = 1
    PARSING_COMMAND = 2


class CommandParser:
    @classmethod
    def parse_name(cls, reader: Reader) -> str:
        try:
            return reader.read_untill(" ")
        except SubstringNotFound:
            return reader.read_untill("\n")

    @classmethod
    def parse_args(cls, reader: Reader) -> list[str]:
        args = []
        arg_reader = Reader(reader.read_untill("\n").strip() + " ")
        try:
            while True:
                arg = arg_reader.read_untill(" ")
                args.append(arg)
                arg_reader.step()
        except SubstringNotFound:
            ...
        except EOF:
            ...

        return args

    @classmethod
    def parse_command(cls, reader: Reader) -> Command:
        name = cls.parse_name(reader)
        args = cls.parse_args(reader)
        return Command(name, args)


def make_stack(filepath: Path = Path("file.crap")):
    stack = []
    lines = filepath.read_text().strip().splitlines()

    for line in lines:
        parsed = tokens.command.parse_string(line)
        stack.append(Command(parsed.name, parsed.args))

    print(f'"{stack}"')


make_stack()
