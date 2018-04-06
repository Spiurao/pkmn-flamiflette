from engine.graphics.charset import Charset
from engine.scene.map.events.npcevent import NPCEvent

class Wobbuffet(NPCEvent):
    def __init__(self, scene, x, y, parameters):
        super().__init__(scene, x, y, parameters)

    def onActionPressed(self, orientation):
        super().onActionPressed(orientation)

        self.walk(Charset.ORIENTATION_UP)
        self.walk(Charset.ORIENTATION_UP)
        self.walk(Charset.ORIENTATION_UP)
        self.walk(Charset.ORIENTATION_UP)
        self.walk(Charset.ORIENTATION_LEFT)
        self.walk(Charset.ORIENTATION_LEFT)
        self.walk(Charset.ORIENTATION_LEFT)
        self.setOrientation(Charset.ORIENTATION_DOWN)


