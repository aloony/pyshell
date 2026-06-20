#!/usr/bin/env python

import subprocess as sp
import readline
import click
import socket
import getpass
import os
import sys
from contextlib import suppress as suppress_exception
from utils import inspect
from pathlib import Path
from pyparsing import (
    Word,
    ParseResults,
    alphas,
    nums,
    Literal,
    Keyword,
    StringStart,
    LineStart,
    alphanums,
    OneOrMore,
    Optional,
    QuotedString,
    printables,
    Combine,
    ZeroOrMore,
    Group,
    Suppress,
    LineEnd,
)


RESET = "\033[0m"
CYAN = "\033[36m"
RED = "\033[31m"
GREEN = "\033[32m"
DIM = "\033[2m"
CLEAR_SCREEN = "\033[2J\033[H"
CTRL_L = "\x0c"


env = os.environ
shell_env = {}

# General
identifier = Word(alphas + "_", alphanums + "_")
endline = Suppress(Keyword(";"))

# Command
command_arg = (
    QuotedString('"') | QuotedString("'") | Word(printables, exclude_chars=" ")
)
command = Group(StringStart() + identifier("name") + ZeroOrMore(command_arg)("args"))(
    "command"
)

text = Path("./file.crap").read_text().strip()


def print_stdout(s: str):
    sys.stdout.write(s)
    sys.stdout.flush()


def prompt(last_return_code):
    if not last_return_code:
        msg = f"{GREEN}{getpass.getuser()}@{socket.gethostname()}{RESET} {CYAN}{os.getcwd()}{RESET}{DIM}:{RESET} "
    else:
        msg = f"{GREEN}{getpass.getuser()}@{socket.gethostname()}{RESET} {CYAN}{os.getcwd()}{RESET} {RED}[{last_return_code}]{RESET}{DIM}:{RESET} "
    return msg


def clear_screen():
    print_stdout(CLEAR_SCREEN)


def print_error(msg):
    print(f"{RED}{msg}{RESET}")


def complete(text, state):
    matches = [m for m in os.listdir(".") if m.startswith(text)]
    if state < len(matches):
        return matches[state]
    return None


readline.set_completer(complete)
readline.parse_and_bind("tab: complete")


def shell():
    last_return_code: int = 0
    clear_screen()
    while True:
        parsed = None
        try:
            line = input(prompt(last_return_code))
            if not line:
                exit()
            parsed, start, end = next(command.scan_string(line, max_matches=1))
            if parsed.command.name == "exit":
                exit()

            cmd = [parsed.command.name, *parsed.command.args]
            result = sp.run(
                cmd,
                capture_output=True,
            )
            last_return_code = result.returncode
            output = (result.stdout or result.stderr).decode()
            print_stdout(f"{output}")

        except (FileNotFoundError, StopIteration):
            last_return_code = 1
            msg = None
            if parsed:
                msg = parsed.command.name
            else:
                msg = line
            print_error(f"No such file or directory: {msg}")
        except KeyboardInterrupt:
            last_return_code = 0
            print_stdout("\n")
            continue


def exec(filepath):
    file = Path(filepath)

    quoted_string = QuotedString(
        '"', esc_char="\\", unquote_results=False
    ) | QuotedString("'", esc_char="\\", unquote_results=False)
    literal = Word(alphas + "_", alphanums + "_")
    number = Word(nums)
    opening_bracket = Literal("{")
    closing_bracket = Literal("}")
    true = Literal("true")
    false = Literal("false")
    semicolon = Suppress(Literal(";"))
    if_literal = Literal("if")
    for_literal = Literal("for")
    is_equal = Literal("==")
    is_literal = Literal("is")
    in_literal = Literal("in")
    else_literal = Literal("else")
    colon = Literal(":")("colon")
    line_start = Suppress(LineStart())
    line_end = Suppress(LineEnd())
    ellipsis = Literal("...")

    command = Group(literal("name") + ZeroOrMore(quoted_string)("args") + line_end)
    condition = Group(
        if_literal
        + literal
        + opening_bracket
        + ZeroOrMore(command)("commands")
        + closing_bracket
    )
    for_loop = Group(
        for_literal
        + literal
        + in_literal
        + literal
        + opening_bracket
        + ZeroOrMore(command)("commands")
        + closing_bracket
    )

    lexer = ZeroOrMore(command | condition | for_loop)

    tokens = lexer.parseString(file.read_text().strip(), parse_all=True)
    print(tokens)
    # for t in tokens:
    #     inspect(t)


@click.command()
@click.argument(
    "filepath",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    required=False,
)
def main(filepath):
    if filepath:
        exec(filepath)
    else:
        shell()


if __name__ == "__main__":
    main()
