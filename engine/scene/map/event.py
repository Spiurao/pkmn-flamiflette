class Event:

    def __init__(self, scene, x, y):
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
        # TODO Spawn this event by adding it to the event matrix
        pass

    def despawn(self):
        self.__spawned = False
        # TODO Despawn this event by removing it from the event matrix
        pass

    def passThrough(self):
        return True

    def setPosition(self, x, y):
        self.__posX = x
        self.__posY = x
        # TODO Replicate this change in the scene's events matrix (important !)

    '''
    Fired when the character faces the event
    and presses the action button
    '''
    def onActionPressed(self):
        pass

    '''
    Fired when the character walks on the tile
    where this event is (only works for
    pass-throughs events)
    
    Always fired after onCharacterTouchEvent()
    '''
    def onCharacterEntersTile(self):
        pass

    '''
    Fired when the character is on a tile near the event and
    presses an arrow key towards the event, even if it 
    is not pass-through / tile collision prevents the movement
    
    Always fired before onCharacterEntersTile()
    '''
    def onCharacterTouchEvent(self):
        pass