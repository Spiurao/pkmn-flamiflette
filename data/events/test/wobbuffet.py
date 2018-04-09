import time
from typing import Dict

from engine.graphics.charset import Charset
from engine.scene.map.events.npcevent import NPCEvent
from engine.scene.map.mapscene import MapScene


class Wobbuffet(NPCEvent):
    def __init__(self, scene: MapScene, x: int, y: int, parameters: Dict):
        super().__init__(scene, x, y, parameters)

    def onSpawn(self):
        super().onSpawn()

        while self.isSpawned():
            if "look" in self.getParameters():
                self.turnToFaceCharacter()
                self.wait(500)

    def onActionPressed(self, orientation):
        super().onActionPressed(orientation)

        if "walk" in self.getParameters():
            self.walk(Charset.ORIENTATION_UP)
            self.walk(Charset.ORIENTATION_UP)
            self.walk(Charset.ORIENTATION_UP)
            self.walk(Charset.ORIENTATION_UP)
            self.walk(Charset.ORIENTATION_LEFT)
            self.walk(Charset.ORIENTATION_LEFT)
            self.walk(Charset.ORIENTATION_LEFT)
            self.getParameters()["look"] = True


