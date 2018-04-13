import os

import pygame
import sys
from typing import Dict, List, Callable, Tuple

from data.constants import Constants
from engine.savemanager import SaveManager
from engine.scene.map.cantalscript import CantalParser, CantalInterpreter, BooleanLiteral, FunctionCallStatement, \
    StringLiteral, IntegerLiteral, Register, Literal, Symbol
from engine.timer import Timer


class Actor:

    CANTAL_CACHE = {}  # this is the cache for already parsed scripts (key : map name dot script name)

    CANTAL_EVENTS_LIST = [
        "spawn",
        "actionPressed",
        "characterEnteredTile",
        "characterTouchEvent",
        "loop",
        "enterState"
    ]

    VARIABLE_TYPE_NORMAL = 0
    VARIABLE_TYPE_SAVED = 1

    def __init__(self, scene, x: int, y: int, parameters: Dict, script : str, name : str):
        self.__scene = scene  # the MapScene containing this actor
        self.__posX = x  # x position of this actor
        self.__posY = y  # y position of this actor
        self.__script = script
        self.__name = name

        self.__spawned = False  # if the actor is not spawned, update(), draw() and events methods will not be called

        self.__parameters = parameters

        self.lastUpdateDate = 0  # the last time this actor was updated and drawn

        self.currentState = None # name of the current state

        # used to keep references to interpreters
        # state name -> interpreter name
        self.interpreters = {}

        # used to keep references to interpreters timers for current state
        self.interpreterTimers = {}

        self.__cantalScript = None  # the CantalScript instance of this actor
        self.__scriptKey = None  # the key of the script in the cantal cache

        # List of the condition functions
        # name associated to boolean function
        self.__cantalConditionFunctions = {}

        # List of regular conditions
        # name associated to the function
        self.__cantalFunctions = {}

        # Cantal variables
        self.__cantalVariables = {}
        self.__cantalVariablesTypes = {}  # name -> type (saved or normal)

        # Default Cantal functions

        # No conditional

        self.registerCantalFunction("wait", self.cantalWait)
        self.registerCantalFunction("print", self.cantalPrint)

    def registerCantalConditionFunction(self, name, cb):
        self.__cantalConditionFunctions[name] = cb

    def registerCantalFunction(self, name, cb):
        self.__cantalFunctions[name] = cb

    def getParameters(self) -> Dict:
        return self.__parameters

    def getName(self) -> str:
        return self.__name

    def update(self, dt : int, events : List[pygame.event.Event]):
        # Notify interpreters that a new frame has been displayed
        # so that they can continue running the scripts
        if self.__script is not None:
            for i in self.interpreters[self.currentState]:
                interpreter = self.interpreters[self.currentState][i]
                if interpreter is not None:
                    interpreter.newFrame()

            # Interpreters timers
            for t in self.interpreterTimers:
                timer = self.interpreterTimers[t]
                if timer is not None:
                    timer.update(dt)  # will self-delete in callback

    def isSpawned(self) -> bool:
        return self.__spawned

    def activateRightState(self):
        if self.__script is None:
            return

        try:
            # Get the first state we find
            found = False
            for state in self.__cantalScript.states:
                stateName = str(state.name)
                stateExpression = state.condition

                if self.__cantalScript.evaluateBooleanExpression(stateExpression, self.cantalValueCallback, self.cantalConditionCallback):
                    # Activate the newly found state
                    if stateName != self.currentState:
                        if self.currentState is not None:
                            for i in self.interpreters[self.currentState]:
                                self.interpreters[self.currentState][i].reset()
                        self.interpreterTimers = {}
                        self.currentState = stateName
                        self.runInterpreter("event.loop")
                        self.runInterpreter("event.enterState")
                    found = True
                    break

            if not found:
                raise Exception("Could not activate any state for event " + str(self.__name))
        except StopIteration:
            raise Exception("Could not activate any state for event " + str(self.__name))

    def load(self):
        # Load CantalScript file
        if self.__script is not None:
            try:
                # Load the script
                self.__scriptKey = self.getScene().getMapName() + "." + self.__script + ".cantalscript"

                if self.__scriptKey not in Actor.CANTAL_CACHE:
                    scriptPath = os.path.join(Constants.ACTORS_PATH, self.getScene().getMapName(), self.__script + ".cantalscript")
                    Actor.CANTAL_CACHE[self.__scriptKey] = CantalParser.parse(scriptPath)

                scriptData = Actor.CANTAL_CACHE[self.__scriptKey]

                self.__cantalScript = scriptData

                # Variables
                for variable in scriptData.vars:
                    if variable.name in self.__cantalVariablesTypes:
                        raise Exception("Duplicate variable " + variable.name)
                    if variable.saved and self.__name == None:
                        raise Exception("The actor must have a name to be able to use saved variables")
                    self.__cantalVariablesTypes[variable.name] = Actor.VARIABLE_TYPE_SAVED if variable.saved else Actor.VARIABLE_TYPE_NORMAL

                    if hasattr(variable, "value") and variable.value is not None:
                        self.__cantalVariables[variable.name] = variable.value.literal.getValue()

                # Interpreters
                for state in scriptData.states:
                    stateName = str(state.name)
                    if not stateName in self.interpreters:
                        self.interpreters[stateName] = {}

                    for event in state.events:
                        eventName = event.name

                        if eventName not in Actor.CANTAL_EVENTS_LIST:
                            raise Exception("Unknown event " + eventName)

                        eventName = "event." + eventName

                        if eventName in self.interpreters:
                            raise Exception("Duplicate event " + eventName)

                        self.interpreters[stateName][eventName] = CantalInterpreter(scriptData, eventName, event.block, self.cantalFunctionCallback, self.cantalConditionCallback, eventName == "event.loop", self.cantalAffectationCallback, self.cantalValueCallback)

                # The right state will be activated on spawn

            except FileNotFoundError:
                raise Exception("Could not find a script named " + self.__script)

    def cantalConditionCallback(self, expression):
        # Function calls
        if expression.name not in self.__cantalConditionFunctions:
            raise Exception("Unknown Cantal condition function " + expression.name)

        return self.__cantalConditionFunctions[expression.name](expression.params.params)

    def cantalFunctionCallback(self, interpreter, function : FunctionCallStatement):
        if function.name not in self.__cantalFunctions:
            raise Exception("Unknown Cantal function " + function.name)

        self.__cantalFunctions[function.name](interpreter, function.params.params)

    def getConstant(self, constant):
        constantsTable = self.__cantalScript.constantsTable
        if not constant in constantsTable:
            raise Exception("Unknown constant " + constant)

        return constantsTable[constant]

    def cantalValueCallback(self, value):
        valueType = type(value)
        if valueType == Register:
            regType = value.type
            regName = self.getRegName(value.name)

            try:
                if regType == "parameters":
                    return self.__parameters[regName]
                elif regType == "messageParameters":
                    pass # TODO Implement this - get message parameters for message name
                else:
                    raise Exception("Unknown register " + str(regType))
            except KeyError:
                return None
        elif valueType == Symbol:
            symbol = str(value)
            #Is it a constant ?
            if symbol in self.__cantalScript.constantsTable:
                return self.__cantalScript.constantsTable[symbol]
            # Is it a variable ?
            elif symbol in self.__cantalVariablesTypes:
                vtype = self.__cantalVariablesTypes[symbol]
                if vtype == Actor.VARIABLE_TYPE_NORMAL:
                    return symbol in self.__cantalVariables and self.__cantalVariables[symbol]
                elif vtype == Actor.VARIABLE_TYPE_SAVED:
                    return SaveManager.getCurrentSaveValue(self.getScene().getMapName() + "." + self.__name + "." + symbol)
            else:
                raise Exception("Unknown symbol " + symbol)
        else:
            raise Exception("Unknown value type " + str(valueType))

    def getRegName(self, regName : str):
        if type(regName) == Symbol:
            # Assume it's a constant
            regName = str(regName)
            return self.getConstant(regName)
        else:
            # String literal
            return regName.getValue()

    def cantalAffectationCallback(self, variable, value):
        variableType = type(variable)
        if variableType == Register:
            regType = variable.type
            regName = self.getRegName(variable.name)

            if regType == "parameters":
                self.__parameters[regName] = value
            elif regType == "messageParameters":
                pass # TODO Implement this - store the parameters for a later message call
            else:
                raise Exception("Unknown register type " + regType)
        elif variableType == Symbol:
            symbol = str(variable)
            # Is it a constant ?
            if symbol in self.__cantalScript.constantsTable:
                raise Exception("Cannot make an affectation to a constant")
            elif symbol in self.__cantalVariablesTypes:
                vtype = self.__cantalVariablesTypes[symbol]
                if vtype == Actor.VARIABLE_TYPE_NORMAL:
                    self.__cantalVariables[symbol] = value
                elif vtype == Actor.VARIABLE_TYPE_SAVED:
                    SaveManager.setCurrentSaveValue(self.getScene().getMapName() + "." + self.__name + "." + symbol,
                                                    value)
            else:
                raise Exception("Unknown symbol " + symbol)

        self.activateRightState()

    def unload(self):
        self.despawn()  # just to be sure

        for state in self.interpreters:
            for interpreter in self.interpreters[state]:
                if self.interpreters[state][interpreter] is not None:
                    self.interpreters[state][interpreter].reset()
                    self.interpreters[state][interpreter] = None

    def draw(self, offsetX, offsetY):
        pass

    def getPosX(self) -> int:
        return self.__posX

    def getPosY(self) -> int:
        return self.__posY

    def spawn(self):
        if not self.__spawned:
            self.__spawned = True
            self.__scene.spawnActor(self, self.__posX, self.__posY)

            self.activateRightState()

    def despawn(self):
        if self.__spawned:
            self.__spawned = False
            self.__scene.despawnActor(self.__posX, self.__posY)


    def getScene(self):
        return self.__scene

    def getWindow(self) -> pygame.Surface:
        return self.__scene.getEngine().getWindow()

    '''
    Collision flag for this actor
    returns True if the character should collide with this actor's tile
    False otherwise
    '''
    def isPassThrough(self) -> bool:
        return True

    def setPosition(self, x : int, y : int):
        self.__scene.updateActorPosition(self.__posX, self.__posY, x, y)
        self.__posX = x
        self.__posY = y

    def runInterpreter(self, interpreter):
        if self.currentState in self.interpreters and interpreter in self.interpreters[self.currentState] and self.interpreters[self.currentState][interpreter] is not None:
            self.interpreters[self.currentState][interpreter].run()

    '''
    Fired when the character faces the actor
    and presses the action button
    '''
    def onActionPressed(self):
        self.runInterpreter("event.actionPressed")

    '''
    Fired when the character walks on the tile
    where this actor is (only works for
    pass-throughs actors)
    
    Always fired after onCharacterTouchEvent()
    '''
    def onCharacterEnteredTile(self):
        self.runInterpreter("event.characterEnteredTile")

    '''
    Fired when the character is on a tile near the actor and
    presses an arrow key towards the actor, even if it 
    is not pass-through / tile collision prevents the movement
    
    Always fired before onCharacterEnteredTile()
    '''
    def onCharacterTouchEvent(self):
        self.runInterpreter("event.characterTouchEvent")

    def interpreterTimerCallback(self, tag):
        self.interpreterTimers[tag] = None
        self.interpreters[self.currentState][tag].nextStatement()

    '''
    CantalScript conditional functions
    '''

    # None

    '''
    CantalScript methods
    '''

    def cantalWait(self, interpreter, functionParams):
        duration = functionParams[0].getValue(self.cantalValueCallback)

        self.interpreterTimers[interpreter] = Timer(interpreter, duration.getValue(), self.interpreterTimerCallback)

    def cantalPrint(self, interpreter, functionParams):
        text = functionParams[0].getValue(self.cantalValueCallback)

        print(text)

        self.interpreters[self.currentState][interpreter].nextStatement()