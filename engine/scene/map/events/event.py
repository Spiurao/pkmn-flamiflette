import sys
import time

class Event:

    def __init__(self, scene, x, y, parameters):
        self.__scene = scene  # the MapScene containing this event
        self.__posX = x  # x position of this event
        self.__posY = y  # y position of this event

        self.__spawned = False  # if the event is not spawned, update(), draw() and events methods will not be called

        self.__parameters = parameters

        self.lastUpdateTime = 0  # the last time this event was updated and drawn

        self.__waitFor = 0
        self.__waiting = False

        # used to keep references to threads
        self.threadList = {
            "onSpawn": None,
            "onActionPressed": None,
            "onCharacterEnteredTile": None,
            "onCharacterTouchEvent": None
        }

    def getParameters(self):
        return self.__parameters

    def update(self, dt, events):
        if self.__waiting:
            self.__waitFor -= dt

            if self.__waitFor <= 0:
                self.__waiting = False

    def isSpawned(self):
        return self.__spawned

    def load(self):
        pass

    def unload(self):
        self.despawn()  # just to be sure

    def draw(self, offsetX, offsetY):
        pass

    def getPosX(self):
        return self.__posX

    def getPosY(self):
        return self.__posY

    def spawn(self):
        if not self.__spawned:
            self.__spawned = True
            self.__scene.spawnEvent(self, self.__posX, self.__posY)


    def despawn(self):
        if self.__spawned:
            self.__spawned = False
            self.__scene.despawnEvent(self.__posX, self.__posY)


    def getScene(self):
        return self.__scene

    def getWindow(self):
        return self.__scene.getEngine().getWindow()

    def runOnMainThread(self, func):
        self.getScene().toRunOnMainThread = func

    '''
    Collision flag for this event
    returns True if the character should collide with this event's tile
    False otherwise
    '''
    def isPassThrough(self):
        return True

    def setPosition(self, x, y):
        self.__scene.updateEventPosition(self.__posX, self.__posY, x, y)
        self.__posX = x
        self.__posY = y

    # THREADED METHODS
    # CAN USE BLOCKING CALLS

    '''
    Fired when the event spawns
    '''
    def onSpawn(self):
        pass

    '''
    Fired when the character faces the event
    and presses the action button
    '''
    def onActionPressed(self, orientation):
        pass

    '''
    Fired when the character walks on the tile
    where this event is (only works for
    pass-throughs events)
    
    Always fired after onCharacterTouchEvent()
    '''
    def onCharacterEnteredTile(self, orientation):
        pass

    '''
    Fired when the character is on a tile near the event and
    presses an arrow key towards the event, even if it 
    is not pass-through / tile collision prevents the movement
    
    Always fired before onCharacterEnteredTile()
    '''
    def onCharacterTouchEvent(self, orientation):
        pass

    def blockingCallsSafeGuard(self):
        if not self.isSpawned():
            sys.exit()

    # BLOCKNG CALLS
    # TO USE IN THREADED METHODS

    def wait(self, duration):
        self.blockingCallsSafeGuard()

        if (not self.__waiting) or (self.__waiting and self.__waitFor < duration):
            self.__waitFor = duration

        self.__waiting = True

        while self.isSpawned() and self.__waiting:
            pass