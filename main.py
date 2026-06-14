#!/usr/bin/env python
import subprocess as sp
import os
from contextlib import suppress as suppress_exception
from utils import *
from pathlib import Path
from pyparsing import (
    Word,
    ParseResults,
    alphas,
    Keyword,
    StringStart,
    alphanums,
    OneOrMore,
    Optional,
    QuotedString,
    Combine,
    ZeroOrMore,
    Group,
    Suppress,
    LineEnd,
)

env = os.environ
shell_env = {}

# General
identifier = Word(alphas + "_", alphanums + "_")
endline = Suppress(Keyword(";"))

# Command
command_arg = QuotedString('"') | QuotedString("'")
command = Group(
    StringStart() + identifier("name") + ZeroOrMore(command_arg)("args") + endline
)("command")


text = Path("./file.crap").read_text().strip()

while True:
    try:
        parsed, start, end = next(command.scan_string(text, max_matches=1))
        text = text[end:]

        cmd = [parsed.command.name, *parsed.command.args]
        result = sp.run(cmd, capture_output=True)
        inspect(result)

    except StopIteration:
        exit()
