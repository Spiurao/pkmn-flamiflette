import pygame
import sys
from typing import Dict, List, Callable

class Actor:
    def __init__(self, scene, x: int, y: int, parameters: Dict):
        self.__scene = scene  # the MapScene containing this actor
        self.__posX = x  # x position of this actor
        self.__posY = y  # y position of this actor

        self.__spawned = False  # if the actor is not spawned, update(), draw() and events methods will not be called

        self.__parameters = parameters

        self.lastUpdateDate = 0  # the last time this actor was updated and drawn

        self.__waitFor = 0
        self.__waiting = False

        # used to keep references to parsed scripts
        self.eventScripts = {
            "spawn": None,
            "actionPressed": None,
            "characterEnteredTile": None,
            "characterTouchEvent": None
        }

    def getParameters(self) -> Dict:
        return self.__parameters

    def update(self, dt : int, events : List[pygame.event.Event]):
        if self.__waiting:
            self.__waitFor -= dt

            if self.__waitFor <= 0:
                self.__waiting = False

    def isSpawned(self) -> bool:
        return self.__spawned

    def load(self):
        # TODO load CantalScript interpreters
        pass

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

            self.onSpawn()

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
    Fired when the actor spawns
    '''
    def onSpawn(self):
        pass

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