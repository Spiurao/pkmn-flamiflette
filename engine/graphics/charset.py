import pygame

from engine.graphics.textures import Textures


class Charset:
    ORIENTATION_DOWN = 0
    ORIENTATION_LEFT = 1
    ORIENTATION_RIGHT = 2
    ORIENTATION_UP = 3

    COLUMNS = 4  # the number of columns / steps in a charset
    LINES = 4  # the number of lines / orientations in a charset

    @staticmethod
    def ofTexture(texture: pygame.Surface, orientation: int):
        return Charset(Textures.getTexture(texture), orientation)

    def __init__(self, texture: pygame.Surface, orientation: int):
        self.__texture = texture  # the texture surface
        self.__orientation = orientation  # the current character orientation
        self.__step = 0  # the current step

        self.__stepWidth = 0  # width of a step surface in px
        self.__stepHeight = 0  # height of a step surface in px

        self.__surfaceMatrix = []

    def load(self):
        width = self.__texture.get_width()
        height = self.__texture.get_height()

        self.__stepWidth = width / Charset.COLUMNS
        self.__stepHeight = height / Charset.LINES

        for y in range(Charset.LINES):
            self.__surfaceMatrix.append([])
            for x in range(Charset.COLUMNS):
                self.__surfaceMatrix[y].append([])
                surface = pygame.Surface((self.__stepWidth, self.__stepHeight), pygame.SRCALPHA, 32)

                surface.blit(self.__texture, (0,0), (x * self.__stepWidth, y * self.__stepHeight, self.__stepWidth, self.__stepWidth))

                self.__surfaceMatrix[y][x] = surface

    def unload(self):
        self.__surfaceMatrix = None

    def getSurfaceWidth(self) -> int:
        return self.__stepWidth

    def getSurfaceHeight(self) -> int:
        return self.__stepHeight

    def getCurrentSurface(self) -> pygame.Surface:
        return self.__surfaceMatrix[self.__orientation][self.__step]

    def resetStep(self):
        if self.__step == 1:
            self.__step = 2
        elif self.__step == 3:
            self.__step = 0

    def incrementStep(self):
        self.__step = (self.__step + 1) % Charset.COLUMNS

    def setOrientation(self, orientation):
        self.__orientation = orientation

    def getOrientation(self) -> int:
        return self.__orientation