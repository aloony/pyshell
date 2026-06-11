#!/usr/bin/env python
import subprocess as sp
import pudb
import os
from rich import inspect
from pathlib import Path
from pyparsing import (
    Word,
    alphas,
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

# Command
command_arg = QuotedString('"') | Combine(Optional("$") + Word(alphanums + "_-./"))
command = Group(
    identifier("name")
    + ZeroOrMore(command_arg, default=[])("args")
    + Suppress(LineEnd())
)("command")

# Variable
variable_setting = Group(
    Suppress("$") + identifier("name") + Suppress("=") + QuotedString('"')("value")
)("variable_setting")

# Expression
expression = variable_setting | command


text = Path("./file.crap").read_text().strip()

i = 1
pudb.set_trace()
while True:
    _, start, end = next(expression.scan_string(text, max_matches=1))
    parsed = expression.parse_string(text[start:end], parse_all=True)
    text = text[end:]

    if "command" in parsed:
        command = parsed.command
        cmd = command.name + " " + " ".join(command.args)
        print(cmd)
        result = sp.run(
            cmd, text=True, capture_output=True, shell=True, env={**env, **shell_env}
        )
        output = result.stdout or result.stderr
        print(f"{i}: {output.strip()}")
    elif "variable_setting" in parsed:
        name, value = parsed.variable_setting.name, parsed.variable_setting.value
        shell_env[name] = value
    i += 1
    print("-------")
