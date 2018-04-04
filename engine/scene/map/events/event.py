class Event:

    def __init__(self, scene, x, y, parameters):
        self.__scene = scene  # the MapScene containing this event
        self.__posX = x  # x position of this event
        self.__posY = y  # y position of this event

        self.__spawned = False  # if the event is not spawned, update(), draw() and events methods will not be called

    def update(self, dt, events):
        pass

    def isSpawned(self):
        return self.__spawned

    def load(self):
        pass

    def unload(self):
        pass

    def draw(self):
        pass

    def spawn(self):
        self.__spawned = True
        self.__scene.spawnEvent(self, self.__posX, self.__posY)
        pass

    def despawn(self):
        self.__spawned = False
        self.__scene.despawnEvent(self.__posX, self.__posY)
        pass

    '''
    Collision flag for this event
    returns True if the character should collide with this event's tile
    False otherwise
    '''
    def isPassThrough(self):
        return True

    def setPosition(self, x, y):
        self.__scene.updateEventPosition(self.__posX, self.__poxY, x, y)
        self.__posX = x
        self.__posY = x

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