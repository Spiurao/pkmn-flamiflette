import typing

from pypeg2 import *

from engine.graphics.charset import Charset


class BooleanLiteral(Keyword):
    grammar = Enum(K('true'), K('false'))

    def getValue(self):
        strSelf = str(self)
        if strSelf == "true":
            return True
        else:
            return False

class OrientationLiteral(Keyword):
    grammar = Enum(K('UP'), K('RIGHT'), K('DOWN'), K('LEFT'))

    def getValue(self):
        strSelf = str(self)
        if strSelf == "UP":
            return Charset.ORIENTATION_UP
        elif strSelf == "RIGHT":
            return Charset.ORIENTATION_RIGHT
        elif strSelf == "DOWN":
            return Charset.ORIENTATION_DOWN
        elif strSelf == "LEFT":
            return Charset.ORIENTATION_LEFT

class IntegerLiteral(int):
    def getValue(self):
        return self

class StringLiteral(str):
    quoted_string = re.compile(r'"[^"]*"')
    grammar = attr("value", [word, quoted_string])

    def getValue(self):
        return self.value[1:-1]

    def __repr__(self):
        return self.getValue()

class Literal(List):
    grammar = attr("literal", [OrientationLiteral, IntegerLiteral, BooleanLiteral, StringLiteral])

class FunctionParameters(List):
    grammar = attr("params", optional(csl(Literal)))

class FunctionCallStatement:
    grammar = name(), "(", attr("params", FunctionParameters), ")"

class BooleanExpression(str):
    grammar = attr("expression", [FunctionCallStatement, BooleanLiteral])

class Block(List):
    pass

class Register(str):
    grammar = attr("type", Symbol), "[", attr("name", [Symbol, StringLiteral]) ,"]"

class RegisterAffectationStatement(str):
    grammar = attr("register", Register), "=", attr("value", Literal)

class IfStatement(str):
    grammar = "if", "(", attr("expression", BooleanExpression), ")", attr("block", Block)

class Statement(List):
    grammar = attr("statement", [([FunctionCallStatement, RegisterAffectationStatement], ";"), IfStatement])

class Event(List):
    grammar = "event", name(), "()", attr("block", Block)

class Message(List):
    grammar = "message", name(), "()", attr("block", Block)

class Constant(List):
    grammar = "constant", name(), "=", attr("value", Literal), ";"

class CantalScript(str):
    grammar = attr("constants", maybe_some(Constant)), attr("messages", maybe_some(Message)), attr("events", maybe_some(Event))

    constantsTable = {}  # constants table

    def init(self):
        for constant in self.constants:
            self.constantsTable[constant.name] = constant.value.literal.getValue()

# Stupid Python
Block.grammar = "{", attr("statements", maybe_some(Statement)), "}"

class CantalParser:

    COMMENTS_GRAMMAR = [re.compile(r"//.*"),
                                re.compile("/\*.*?\*/", re.S)]

    @staticmethod
    def parse(scriptPath : str) -> CantalScript:
        result = None
        with open(scriptPath, "r") as f:
            result = parse(f.read(), CantalScript, None, whitespace, CantalParser.COMMENTS_GRAMMAR)

        result.init()

        return result

class BlockEntry:
    def __init__(self, code : typing.List[Statement]):
        self.code = code  # list of statements
        self.statementNumber = 0  # current statement


class CantalInterpreter:
    STATEMENTS_LIMIT_PER_FRAME = 100  # the interpreter cannot execute more statements per frame than this - fixes game freeze and maximum recursion depth errors

    def __init__(self, script : CantalScript, name : str, code : Block, functionsCallback : typing.Callable, conditionCallback : typing.Callable, loop : bool, registerAffectationCallback : typing.Callable):
        self.__name = name
        self.__code = code.statements
        self.__functionsCb = functionsCallback
        self.__conditionCb = conditionCallback
        self.__registerAffectationCb = registerAffectationCallback
        self.__loop = loop

        self.script = script

        self.__statementsForCurrentFrame = 0
        self.__waitingForNewFrame = False  # is the interpreter waiting for a new frame to continue ?

        self.__blockStack = []  # stack of BlockEntry instances
        self.__running = False

        self.__shouldLoop = False

    def newFrame(self):
        self.__statementsForCurrentFrame = 0

        if self.__shouldLoop:
            self.__shouldLoop = False
            self.run()

        if self.__waitingForNewFrame:
            self.__waitingForNewFrame = False
            self.nextStatement()

    def run(self):
        if self.__running:
            return

        self.__blockStack.append(BlockEntry(self.__code))
        self.__running = True
        self.processCurrentStatement()

    def evaluateBooleanExpression(self, expression) -> bool:
        expressionType = type(expression)

        if expressionType == BooleanLiteral:
            return expression.getValue()
        elif expressionType == FunctionCallStatement:
            return self.__conditionCb(self.__name, expression)



    def processCurrentStatement(self):
        if not self.__running:
            return

        currentBlock = self.__blockStack[-1]
        currentStatement = currentBlock.code[currentBlock.statementNumber].statement

        # If statement
        statementType = type(currentStatement)
        if statementType == IfStatement:
            # Evaluate condition
            if self.evaluateBooleanExpression(currentStatement.expression.expression):
                self.__blockStack.append(BlockEntry(currentStatement.block.statements))
                self.processCurrentStatement()
            else:
                self.nextStatement()
        # Actor function statement
        elif statementType == FunctionCallStatement:
            self.__functionsCb(self.__name, currentStatement)
        # Actor register affectation statement
        elif statementType == RegisterAffectationStatement:
            self.__registerAffectationCb(self.__name, currentStatement.register, currentStatement.value)
            self.nextStatement();
        else:
            raise Exception("Unknown statement type " + str(statementType))

    def nextStatement(self):
        if self.__statementsForCurrentFrame >= CantalInterpreter.STATEMENTS_LIMIT_PER_FRAME:
            self.__waitingForNewFrame = True
            return

        self.__statementsForCurrentFrame += 1

        currentBlock = self.__blockStack[-1]
        currentBlock.statementNumber += 1

        if currentBlock.statementNumber >= len(currentBlock.code):
            self.__blockStack.pop()

            if len(self.__blockStack) == 0:
                if self.__loop:
                    self.__shouldLoop = True
                self.reset()
            else:
                self.nextStatement();
        else:
            self.processCurrentStatement()

    def reset(self):
        self.__blockStack = []
        self.__running = False

    def isRunning(self):
        return self.__running