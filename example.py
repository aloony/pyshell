#!/usr/bin/env python3
"""Interpreter for the language described in lang.specification.

Pipeline:  source text  ->  Lexer (tokens)  ->  Parser (AST)  ->  Interpreter
"""

import subprocess
import sys
from dataclasses import dataclass


class LangError(Exception):
    pass


def display(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


# --------------------------------------------------------------------------- #
# Lexer
# --------------------------------------------------------------------------- #


@dataclass
class Token:
    kind: str  # INT STRING IDENT TRUE FALSE ASSIGN LPAREN RPAREN NEWLINE EOF
    value: object
    line: int


KEYWORDS = {"true": "TRUE", "false": "FALSE"}


class Lexer:
    def __init__(self, source):
        self.src = source
        self.pos = 0
        self.line = 1

    def error(self, msg):
        raise LangError(f"line {self.line}: {msg}")

    def peek(self):
        return self.src[self.pos] if self.pos < len(self.src) else ""

    def advance(self):
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def tokens(self):
        toks = []
        while self.pos < len(self.src):
            ch = self.peek()
            if ch == "\n":
                self.advance()
                toks.append(Token("NEWLINE", "\n", self.line - 1))
            elif ch in " \t\r":
                self.advance()
            elif ch == "#":  # comment to end of line
                while self.peek() not in ("", "\n"):
                    self.advance()
            elif ch == '"':
                toks.append(self.read_string())
            elif ch == "=":
                self.advance()
                toks.append(Token("ASSIGN", "=", self.line))
            elif ch == "(":
                self.advance()
                toks.append(Token("LPAREN", "(", self.line))
            elif ch == ")":
                self.advance()
                toks.append(Token("RPAREN", ")", self.line))
            elif ch.isdigit():
                toks.append(self.read_number())
            elif ch.isalpha() or ch == "_":
                tok = self.read_word()
                toks.append(tok)
                # sh(...) takes a raw shell command, not a normal expression,
                # so capture its body here as a single string token.
                if tok.kind == "IDENT" and tok.value == "sh":
                    self.read_sh_body(toks)
            else:
                self.error(f"unexpected character {ch!r}")
        toks.append(Token("NEWLINE", "\n", self.line))
        toks.append(Token("EOF", None, self.line))
        return toks

    def read_string(self):
        line = self.line
        self.advance()  # opening quote
        start = self.pos
        while self.peek() not in ('"', "", "\n"):
            self.advance()
        if self.peek() != '"':
            self.error("unterminated string")
        value = self.src[start : self.pos]
        self.advance()  # closing quote
        return Token("STRING", value, line)

    def read_number(self):
        line = self.line
        start = self.pos
        while self.peek().isdigit():
            self.advance()
        return Token("INT", int(self.src[start : self.pos]), line)

    def read_word(self):
        line = self.line
        start = self.pos
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        text = self.src[start : self.pos]
        return Token(KEYWORDS.get(text, "IDENT"), text, line)

    def read_sh_body(self, toks):
        save = self.pos
        while self.peek() in " \t":
            self.advance()
        if self.peek() != "(":  # bare `sh`, not a call
            self.pos = save
            return
        line = self.line
        self.advance()  # consume (
        toks.append(Token("LPAREN", "(", line))
        start = self.pos
        while self.peek() not in (")", "", "\n"):
            self.advance()
        if self.peek() != ")":
            self.error("unterminated sh(...) command")
        toks.append(Token("STRING", self.src[start : self.pos].strip(), line))
        self.advance()  # consume )
        toks.append(Token("RPAREN", ")", line))


# --------------------------------------------------------------------------- #
# AST
# --------------------------------------------------------------------------- #


@dataclass
class Program:
    statements: list


@dataclass
class Assign:
    name: str
    value: object


@dataclass
class ExprStmt:
    expr: object


@dataclass
class StringLit:
    value: str


@dataclass
class IntLit:
    value: int


@dataclass
class BoolLit:
    value: bool


@dataclass
class Var:
    name: str


@dataclass
class Call:
    name: str
    args: list


# --------------------------------------------------------------------------- #
# Parser
# --------------------------------------------------------------------------- #


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, kind):
        tok = self.peek()
        if tok.kind != kind:
            raise LangError(f"line {tok.line}: expected {kind}, got {tok.kind}")
        return self.advance()

    def parse(self):
        statements = []
        while self.peek().kind != "EOF":
            if self.peek().kind == "NEWLINE":
                self.advance()
                continue
            statements.append(self.statement())
        return Program(statements)

    def statement(self):
        # assignment:  IDENT '=' expression
        if self.peek().kind == "IDENT" and self.tokens[self.pos + 1].kind == "ASSIGN":
            name = self.advance().value
            self.expect("ASSIGN")
            value = self.expression()
            self.end_of_statement()
            return Assign(name, value)
        expr = self.expression()
        self.end_of_statement()
        return ExprStmt(expr)

    def end_of_statement(self):
        tok = self.peek()
        if tok.kind not in ("NEWLINE", "EOF"):
            raise LangError(f"line {tok.line}: unexpected {tok.kind} after statement")

    def expression(self):
        tok = self.peek()
        if tok.kind == "STRING":
            self.advance()
            return StringLit(tok.value)
        if tok.kind == "INT":
            self.advance()
            return IntLit(tok.value)
        if tok.kind == "TRUE":
            self.advance()
            return BoolLit(True)
        if tok.kind == "FALSE":
            self.advance()
            return BoolLit(False)
        if tok.kind == "IDENT":
            self.advance()
            if self.peek().kind == "LPAREN":
                return self.finish_call(tok.value)
            return Var(tok.value)
        raise LangError(f"line {tok.line}: unexpected {tok.kind} in expression")

    def finish_call(self, name):
        self.expect("LPAREN")
        args = []
        if self.peek().kind != "RPAREN":
            args.append(self.expression())
        self.expect("RPAREN")
        return Call(name, args)


# --------------------------------------------------------------------------- #
# Interpreter (AST walker)
# --------------------------------------------------------------------------- #


class Interpreter:
    def __init__(self):
        self.env = {}

    def run(self, program):
        for stmt in program.statements:
            self.execute(stmt)
        return self.env

    def execute(self, stmt):
        if isinstance(stmt, Assign):
            self.env[stmt.name] = self.evaluate(stmt.value)
        elif isinstance(stmt, ExprStmt):
            self.evaluate(stmt.expr)
        else:
            raise LangError(f"unknown statement: {stmt!r}")

    def evaluate(self, expr):
        if isinstance(expr, (StringLit, IntLit, BoolLit)):
            return expr.value
        if isinstance(expr, Var):
            if expr.name not in self.env:
                raise LangError(f"undefined variable: {expr.name}")
            return self.env[expr.name]  # values are copied (immutable)
        if isinstance(expr, Call):
            return self.call(expr)
        raise LangError(f"unknown expression: {expr!r}")

    def call(self, node):
        if node.name not in ("sh", "print"):
            raise LangError(f"unknown function: {node.name}")
        if len(node.args) != 1:
            raise LangError(f"{node.name}() takes exactly one argument")
        if node.name == "sh":
            command = self.evaluate(node.args[0])
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.stdout != "":
                return result.stdout
            if result.stderr != "":
                return result.stderr
            return ""
        # print
        sys.stdout.write(display(self.evaluate(node.args[0])) + "\n")
        return None


# --------------------------------------------------------------------------- #
# Entry points
# --------------------------------------------------------------------------- #


def run(source):
    program = Parser(Lexer(source).tokens()).parse()
    interp = Interpreter()
    interp.run(program)
    return interp.env


def main():
    if len(sys.argv) != 2:
        print("usage: interpreter.py <program>", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        source = f.read()
    try:
        run(source)
    except LangError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
