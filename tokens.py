from pyparsing import (
    Word,
    alphas,
    alphanums,
    OneOrMore,
    Optional,
    QuotedString,
)

command_name = Word(alphas + "_")
command_arg = QuotedString('"') | Word(alphanums + "_-./")
command = command_name("name") + Optional(OneOrMore(command_arg), default=[])("args")
