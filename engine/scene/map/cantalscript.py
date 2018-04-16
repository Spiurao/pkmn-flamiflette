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
    grammar = attr("value", quoted_string)

    def getValue(self):
        return self.value[1:-1]

    def __repr__(self):
        return self.getValue()

class Literal(List):
    grammar = attr("literal", [OrientationLiteral, IntegerLiteral, BooleanLiteral, StringLiteral])

class Block(List):
    pass

class Register(str):
    grammar = attr("type", Symbol), "[", attr("name", [StringLiteral, Symbol]) ,"]"

class FunctionParameters(List):
    pass

class FunctionCallStatement:
    grammar = name(), "(", attr("params", FunctionParameters), ")"

class ValueSymbol(Symbol):
    def getValue(self, valueCb):
        return valueCb(self)

class ValueOperator:

    def getValue(self, valueCb):
        return self.operator.getValue(valueCb)

class TernaryValue:
    grammar = "(", attr("condition", ValueOperator), "?", attr("v1", ValueOperator), ":", attr("v2", ValueOperator), ")"

    def getValue(self, valueCb):
        return self.v1.getValue(valueCb) if self.condition.getValue(valueCb) else self.v2.getValue(valueCb)

class Value(str):

    def getValue(self, valueCb):
        valueType = type(self.value)
        if valueType == Register or valueType == Symbol or valueType == FunctionCallStatement:
            return valueCb(self.value)
        elif valueType == Literal:
            return self.value.literal.getValue()
        else:
            raise Exception("Unknown value type " + str(valueType))

class AddOperator:
    grammar = "(", attr("v1", ValueOperator), "+", attr("v2", ValueOperator), ")"

    def getValue(self, valueCb):
        firstValue = self.v1.getValue(valueCb)
        secondValue = self.v2.getValue(valueCb)

        if type(firstValue) == str:
            secondValue = str(secondValue)
        elif type(secondValue) == str:
            firstValue = str(firstValue)

        return firstValue + secondValue

class SubOperator:
    grammar = "(", attr("v1", ValueOperator), "-", attr("v2", ValueOperator), ")"

    def getValue(self, valueCb):
        firstValue = self.v1.getValue(valueCb)
        secondValue = self.v2.getValue(valueCb)

        return firstValue - secondValue

class MulOperator:
    grammar = "(", attr("v1", ValueOperator), "*", attr("v2", ValueOperator), ")"

    def getValue(self, valueCb):
        firstValue = self.v1.getValue(valueCb)
        secondValue = self.v2.getValue(valueCb)

        return int(firstValue * secondValue)

class DivOperator:
    grammar = "(", attr("v1", ValueOperator), "/", attr("v2", ValueOperator), ")"

    def getValue(self, valueCb):
        firstValue = self.v1.getValue(valueCb)
        secondValue = self.v2.getValue(valueCb)

        return int(firstValue / secondValue)

class EqualsOperator(str):
    grammar = attr("var1", ValueOperator), "==", attr("var2", ValueOperator)

    def getValue(self, valueCb):
        return self.var1.getValue(valueCb) == self.var2.getValue(valueCb)

class AndOperator(str):
    grammar = attr("op1", ValueOperator), "&&", attr("op2", ValueOperator)

    def getValue(self, valueCb):
        return self.var1.getValue(valueCb) and self.var2.getValue(valueCb)

class NotOperator(str):
    grammar = "!", attr("op", ValueOperator)

    def getValue(self, valueCb):
        return not self.op.getValue(valueCb)

class OrOperator(str):
    grammar = attr("op1", ValueOperator), "||", attr("op2", ValueOperator)

    def getValue(self, valueCb):
        return self.var1.getValue(valueCb) or self.var2.getValue(valueCb)

class BooleanOperator:
    grammar = "(", attr("operator", [EqualsOperator, NotOperator, AndOperator, OrOperator]), ")"

    def getValue(self, valueCb):
        return self.operator.getValue(valueCb)

class AffectationStatement(str):
    grammar = attr("register", [Register, Symbol]), "=", attr("value", ValueOperator)

class IfStatement(str):
    grammar = "if", "(", attr("expression", ValueOperator), ")", attr("block", Block)

class Statement(List):
    grammar = attr("statement", [([FunctionCallStatement, AffectationStatement], ";"), IfStatement])

class Event(List):
    grammar = "event", name(), "()", attr("block", Block)

class Message(List):
    grammar = "message", name(), "()", attr("block", Block)

class CantalScript(str):
    constantsTable = {}  # constants table

    def init(self):
        for constant in self.constants:
            self.constantsTable[constant.name] = constant.value.literal.getValue()

class ConstantDeclaration(List):
    grammar = "const", name(), "=", attr("value", Literal), ";"

class VariableDeclaration(List):
    grammar = flag("saved"), "var", name(), [("=", attr("value", Literal)),""], ";"

class State(List):
    grammar = "state", name(), "(", attr("condition", ValueOperator), ")", "{", attr("messages", maybe_some(Message)), attr("events", maybe_some(Event)), "}"

# Stupid Python
Block.grammar = "{", attr("statements", maybe_some(Statement)), "}"
CantalScript.grammar = attr("constants", maybe_some(ConstantDeclaration)), attr("vars", maybe_some(VariableDeclaration)), attr("states", maybe_some(State))
FunctionParameters.grammar = attr("params", optional(csl(ValueOperator)))
Value.grammar = attr("value", [FunctionCallStatement, Register, Literal, ValueSymbol])
ValueOperator.grammar = attr("operator", [AddOperator, SubOperator, DivOperator, MulOperator, BooleanOperator, TernaryValue, Value])


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

    def __init__(self, script : CantalScript, name : str, code : Block, functionsCallback : typing.Callable, loop : bool, affectationCallback : typing.Callable, valueCallback : typing.Callable):
        self.__name = name
        self.__code = code.statements
        self.__functionsCb = functionsCallback
        self.__affectationCb = affectationCallback
        self.__valueCb = valueCallback
        self.__loop = loop

        self.script = script

        self.__statementsForCurrentFrame = 0
        self.__waitingForNewFrame = False  # is the interpreter waiting for a new frame to continue ?

        self.__blockStack = []  # stack of BlockEntry instances
        self.__running = False

        self.__shouldLoop = False

    def onNewFrame(self):
        self.__statementsForCurrentFrame = 0

        if self.__shouldLoop:
            self.__shouldLoop = False
            self.run()

        if self.__waitingForNewFrame:
            self.__waitingForNewFrame = False
            self.nextStatement()

    def run(self):
        if self.__running or len(self.__code) <= 0:
            return

        self.__blockStack.append(BlockEntry(self.__code))
        self.__running = True
        self.processCurrentStatement()

    def processCurrentStatement(self):
        if not self.__running:
            return

        currentBlock = self.__blockStack[-1]
        currentStatement = currentBlock.code[currentBlock.statementNumber].statement

        # If statement
        statementType = type(currentStatement)
        if statementType == IfStatement:
            # Evaluate condition
            if currentStatement.expression.getValue(self.__valueCb):
                self.__blockStack.append(BlockEntry(currentStatement.block.statements))
                self.processCurrentStatement()
            else:
                self.nextStatement()
        # Actor function statement
        elif statementType == FunctionCallStatement:
            self.__functionsCb(self.__name, currentStatement)
        # Actor register affectation statement
        elif statementType == AffectationStatement:
            self.__affectationCb(currentStatement.register, currentStatement.value.getValue(self.__valueCb))
            self.nextStatement();
        else:
            raise Exception("Unknown statement type " + str(statementType))

    def nextStatement(self):
        if not self.__running:
            return

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