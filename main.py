#!/usr/bin/env python
from pathlib import Path
from enum import Enum
import pudb


class Command:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name


class File:
    def __init__(self, text: str):
        self.text = text
        self.i = 0

    def step(self, n: int = 1):
        self.i += n

        if self.i == len(self.text):
            raise EOF()

    def read(self, start: int = 0, end: int = 0) -> str:
        start = start or self.i
        end = end or self.i + 1
        try:
            return self.text[start:end]
        except IndexError:
            raise EOF()

    def read_untill(self, sub: str, start: int) -> str:
        start = start or self.i
        end = self.text.find(sub, start)

        return self.read(start, end)


class State(Enum):
    ANY = 1
    PARSING_COMMAND = 2


class Parser:
    @staticmethod
    def parse_command(file: File):
        def 

        command_name = ""

        while True:
            char = file.read()
            if char.isidentifier():
                command_name += char
                file.step()
            else:
                break

        return Command(command_name)



class EOF(Exception): ...


def make_stack(filepath: Path = Path("file.crap")):
    stack = []
    file = File(filepath.read_text(encoding="utf-8"))

    try:
        while True:
            char = file.read()
            if char.isidentifier():
                stack.append(Parser.parse_command(file))
            file.step()
    except EOF:
        ...

    print(stack)


make_stack()
