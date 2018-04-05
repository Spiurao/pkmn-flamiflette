from engine.graphics.charset import Charset
from engine.scene.map.events.event import Event


class NPCEvent(Event):
    def __init__(self, scene, x, y, parameters):
        super().__init__(scene, x, y, parameters)

        self.__charset = Charset.ofTexture(parameters["charset"], parameters["orientation"])

        self.__charsetSurfaceOffset = None
        self.__tileSize = self.getScene().getTileSize()

    def load(self):
        super().load()
        self.__charset.load()

        self.__charsetSurfaceOffset = (self.__charset.getSurfaceWidth()/4, self.__charset.getSurfaceHeight()/2)

    def draw(self):
        super().draw()

        self.getWindow().blit(self.__charset.getCurrentSurface(), (self.getPosX() * self.__tileSize - self.__charsetSurfaceOffset[0], self.getPosY() * self.__tileSize - self.__charsetSurfaceOffset[1]))

    def isPassThrough(self):
        return False



