import typing

from pypeg2 import *

class BooleanLiteral(Keyword):
    grammar = Enum(K('true'), K('false'))

class OrientationLiteral(Keyword):
    grammar = Enum(K('UP'), K('RIGHT'), K('DOWN'), K('LEFT'))

class StringLiteral(str):
    quoted_string = re.compile(r'"[^"]*"')
    grammar = [word, quoted_string]

class Literal(List):
    grammar = [OrientationLiteral, int, StringLiteral, BooleanLiteral]

class FunctionParameters(List):
    grammar = optional(csl(Literal))

class FunctionCallStatement:
    grammar = name(), "(", attr("params", FunctionParameters), ")"

class BooleanExpression(str):
    grammar = [FunctionCallStatement, BooleanLiteral]

class Block(List):
    pass

class IfStatement(str):
    grammar = "if", "(", attr("expression", BooleanExpression), ")", Block

class Statement(List):
    grammar = [(FunctionCallStatement, ";"), IfStatement]

class Event(List):
    grammar = "event", name(), "()", Block

class CantalScript(str):
    grammar = maybe_some(Event)

# Stupid Python
Block.grammar = "{", maybe_some(Statement), "}"

class CantalParser:

    COMMENTS_GRAMMAR = [re.compile(r"//.*"),
                                re.compile("/\*.*?\*/", re.S)]

    def __init__(self):
        pass

    @staticmethod
    def parse(scriptPath : str) -> typing.List:
        with open(scriptPath, "r") as f:
            result = parse(f.read(), CantalScript, None, whitespace, CantalParser.COMMENTS_GRAMMAR)
            print(str(result))

class CantalInterpreter:
    def __init__(self, eventCode : Event):
        self.__eventCode = eventCode