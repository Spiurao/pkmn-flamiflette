import os

import pygame
import sys
from typing import Dict, List, Callable

from data.constants import Constants
from engine.scene.map.cantalscript import CantalParser, CantalInterpreter, BooleanLiteral, FunctionCallStatement, \
    StringLiteral


class Actor:

    CANTAL_CACHE = {}  # this is the cache for already parsed scripts (key : map name dot script name)

    def __init__(self, scene, x: int, y: int, parameters: Dict, script : str):
        self.__scene = scene  # the MapScene containing this actor
        self.__posX = x  # x position of this actor
        self.__posY = y  # y position of this actor
        self.__script = script

        self.__spawned = False  # if the actor is not spawned, update(), draw() and events methods will not be called

        self.__parameters = parameters

        self.lastUpdateDate = 0  # the last time this actor was updated and drawn

        # used to keep references to interpreters
        self.__eventScripts = {
            "spawn": None,
            "actionPressed": None,
            "characterEnteredTile": None,
            "characterTouchEvent": None,
            "loop" : None
        }

        # List of the condition functions
        # name associated to boolean function
        self.conditionFunctions = {
            "inParameters": self.isInParameters
        }


    def getParameters(self) -> Dict:
        return self.__parameters

    def update(self, dt : int, events : List[pygame.event.Event]):
        # Notify interpreters that a new frame has been displayed
        # so that they can continue running the scripts
        for i in self.__eventScripts:
            interpreter = self.__eventScripts[i]
            if interpreter is not None:
                interpreter.newFrame()

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

                    if eventName not in self.__eventScripts:
                        raise Exception("Unknown event " + eventName)

                    if self.__eventScripts[eventName] is not None:
                        raise Exception("Duplicate event " + eventName)

                    self.__eventScripts[eventName] = CantalInterpreter(event.block, self.cantalStatementCallback, self.cantalConditionCallback, eventName == "loop")

            except FileNotFoundError:
                raise Exception("Could not find a script named " + self.__script)

    def cantalConditionCallback(self, expression):
        # Boolean litterals
        if type(expression) == BooleanLiteral:
            return str(expression) == "true"
        # Function calls
        elif type(expression) == FunctionCallStatement:
            if expression.name not in self.conditionFunctions:
                raise Exception("Unknown function " + expression.name)

            return self.conditionFunctions[expression.name](expression.params.params)

        #Default
        raise Exception("Unknown boolean expression in condition (type : " + str(type(expression))) + ")"

    def cantalStatementCallback(self, statement):
        print("Received statement " + str(statement))

    def unload(self):
        self.despawn()  # just to be sure

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

            if self.__eventScripts["loop"] is not None:
                self.__eventScripts["loop"].run()

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

    # TODO Events should run the interpreter

    '''
    Fired when the character faces the actor
    and presses the action button
    '''
    def onActionPressed(self, orientation : int):
        pass

    '''
    Fired when the character walks on the tile
    where this actor is (only works for
    pass-throughs actors)
    
    Always fired after onCharacterTouchEvent()
    '''
    def onCharacterEnteredTile(self, orientation : int):
        pass

    '''
    Fired when the character is on a tile near the actor and
    presses an arrow key towards the actor, even if it 
    is not pass-through / tile collision prevents the movement
    
    Always fired before onCharacterEnteredTile()
    '''
    def onCharacterTouchEvent(self, orientation : int):
        pass

    def blockingCallsSafeGuard(self):
        if not self.isSpawned():
            sys.exit()

    '''
    CantalScript conditional functions
    '''
    def isInParameters(self, functionParams):
        param = functionParams[0].literal
        if type(param) != StringLiteral:
            raise Exception("Illegal parameter - expected StringLiteral, got " + str(type(param)))

        return param.getValue() in self.__parameters

    '''
    CantalScript methods
    '''

    # TODO Move things here
