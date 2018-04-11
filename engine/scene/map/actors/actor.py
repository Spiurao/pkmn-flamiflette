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
        "loop"
    ]

    def __init__(self, scene, x: int, y: int, parameters: Dict, script : str, name : str):
        self.__scene = scene  # the MapScene containing this actor
        self.__posX = x  # x position of this actor
        self.__posY = y  # y position of this actor
        self.__script = script
        self.__name = name

        self.__spawned = False  # if the actor is not spawned, update(), draw() and events methods will not be called

        self.__parameters = parameters

        self.lastUpdateDate = 0  # the last time this actor was updated and drawn

        # used to keep references to interpreters
        self.interpreters = {}

        # used to keep references to interpreters timers
        self.interpreterTimers = {}

        # List of the condition functions
        # name associated to boolean function
        self.__cantalConditionFunctions = {}

        # List of regular conditions
        # name associated to the function
        self.__cantalFunctions = {}

        # Cantal variables
        self.__cantalVariables = {}

        # Default Cantal functions
        self.registerCantalConditionFunction("inParameters", self.cantalIsInParameters)
        self.registerCantalConditionFunction("isParameterTrue", self.cantalIsParameterTrue)

        self.registerCantalFunction("wait", self.cantalWait)
        self.registerCantalFunction("setParameter", self.cantalSetParameter)
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
        for i in self.interpreters:
            interpreter = self.interpreters[i]
            if interpreter is not None:
                interpreter.newFrame()

        # Interpreters timers
        for t in self.interpreterTimers:
            timer = self.interpreterTimers[t]
            if timer is not None:
                timer.update(dt)  # will self-delete in callback

    def isSpawned(self) -> bool:
        return self.__spawned

    def load(self):
        # Load CantalScript file
        if self.__script is not None:
            try:
                scriptKey = self.getScene().getMapName() + "." + self.__script + ".cantalscript"

                if scriptKey not in Actor.CANTAL_CACHE:
                    scriptPath = os.path.join(Constants.ACTORS_PATH, self.getScene().getMapName(), self.__script + ".cantalscript")
                    Actor.CANTAL_CACHE[scriptKey] = CantalParser.parse(scriptPath)

                scriptData = Actor.CANTAL_CACHE[scriptKey]

                for event in scriptData.events:
                    eventName = event.name

                    if eventName not in Actor.CANTAL_EVENTS_LIST:
                        raise Exception("Unknown event " + eventName)

                    eventName = "event." + eventName

                    if eventName in self.interpreters:
                        raise Exception("Duplicate event " + eventName)

                    self.interpreters[eventName] = CantalInterpreter(scriptData, eventName, event.block, self.cantalFunctionCallback, self.cantalConditionCallback, eventName == "event.loop", self.cantalRegisterAffectationCallback, self.cantalRegisterCallback)

            except FileNotFoundError:
                raise Exception("Could not find a script named " + self.__script)

    def cantalConditionCallback(self, interpreter, expression):
        # Function calls
        if expression.name not in self.__cantalConditionFunctions:
            raise Exception("Unknown Cantal condition function " + expression.name)

        return self.__cantalConditionFunctions[expression.name](interpreter, expression.params.params)

    def cantalFunctionCallback(self, interpreter, function : FunctionCallStatement):
        if function.name not in self.__cantalFunctions:
            raise Exception("Unknown Cantal function " + function.name)

        self.__cantalFunctions[function.name](interpreter, function.params.params)

    def getConstantForInterpreter(self, interpreter, constant):
        constantsTable = self.interpreters[interpreter].script.constantsTable
        if not constant in constantsTable:
            raise Exception("Unknown constant " + constant)

        return constantsTable[constant]

    def cantalRegisterCallback(self, interpreter : str, register : Register):
        regType = register.type
        regName = self.getRegName(interpreter, register.name)

        try:
            if regType == "parameters":
                return self.__parameters[regName]
            elif regType == "variables":
                return self.__cantalVariables[regName]
            elif regType == "savedVariables":
                return SaveManager.getCurrentSaveValue(regName)
            elif regType == "messageParameters":
                pass # TODO Implement this - get message parameters for message name
        except KeyError:
            return None


    def getRegName(self, interpreter : str, regName : str):
        if type(regName) == Symbol:
            # Assume it's a constant
            regName = str(regName)
            return self.getConstantForInterpreter(interpreter, regName)
        else:
            # String literal
            return regName.getValue()

    def cantalRegisterAffectationCallback(self, interpreter:str, register : Register, value : Literal):
            regType = register.type
            regName = self.getRegName(interpreter, register.name)

            if regType == "parameters":
                self.__parameters[regName] = value.literal.getValue()
            elif regType == "variables":
                self.__cantalVariables[regName] = value.literal.getValue()
            elif regType == "savedVariables":
                if self.__name == None:
                    raise Exception("The event must have a name to be able to use savedVariables register")
                SaveManager.setCurrentSaveValue(self.getScene().getMapName() + "." + self.__name + "." + regName, value.literal.getValue())
            elif regType == "messageParameters":
                pass # TODO Implement this - store the parameters for a later message call
            else:
                raise Exception("Unknown register type " + regType)


    def unload(self):
        self.despawn()  # just to be sure

        for interpreter in self.interpreters:
            if self.interpreters[interpreter] is not None:
                self.interpreters[interpreter].reset()
                self.interpreters[interpreter] = None

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

            self.runInterpreter("event.loop")

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
        if interpreter in self.interpreters and self.interpreters[interpreter] is not None:
            self.interpreters[interpreter].run()

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
        self.interpreters[tag].nextStatement()

    '''
    CantalScript conditional functions
    '''
    def cantalIsInParameters(self, interpreter, functionParams):
        name = functionParams[0].literal

        return name.getValue() in self.__parameters

    def cantalIsParameterTrue(self, interpreter, functionParams):
        name = functionParams[0].literal

        value = name.getValue()

        returnValue = value in self.__parameters and self.__parameters[value] == True

        return returnValue

    '''
    CantalScript methods
    '''

    def cantalWait(self, interpreter, functionParams):
        duration = functionParams[0].literal

        self.interpreterTimers[interpreter] = Timer(interpreter, duration.getValue(), self.interpreterTimerCallback)


    def cantalSetParameter(self, interpreter, functionParams):
        name = functionParams[0].literal
        value = functionParams[1].literal

        self.__parameters[name.getValue()] = value.getValue()
        self.interpreters[interpreter].nextStatement()

    def cantalPrint(self, interpreter, functionParams):
        text = functionParams[0].literal

        print(text.getValue())

        self.interpreters[interpreter].nextStatement()