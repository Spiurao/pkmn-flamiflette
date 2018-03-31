import pygame

from data.constants import Constants
from data.textures import Textures
from engine.scene.scene import Scene
import os
import json

from engine.tween.Easing import Easing
from engine.tween.TweenSubject import TweenSubject


class Tile:

    TYPE_ABOVE_EVENTS = "aboveEvents"

    def __init__(self):
        self.surface = None  # the surface of this tile
        # TODO Add animation, collision...

class TestNotSlowMapScene(Scene):

    CAMERA_MOVEMENT_DURATION = 150

    def __init__(self, engine, map):
        super().__init__(engine)

        self.__mapName = map  # the map name

        self.__tilesetName = ""
        self.__tilesetTexture = None  # the tileset texture surface

        self.__tileSize = 0  # the size of one tile in px

        self.__mapWidth = 0  # the map width in tiles
        self.__mapHeight = 0  # the map height in tiles

        self.__windowWidth = 0  # width of the window in tiles (depends on tileSize)
        self.__windowHeight = 0  # height of the window in tiles (depends on tileSize)

        self.__tilesMatrix0 = []  # matrix of Tile objects to draw below the events
        self.__tilesMatrix1 = []  # matrix of Tile objects surfaces to draw above the events

        self.__inputsBlocked = False  # self-explanatory

        self.__window = self.getEngine().getWindow()  # the game window

        self.__playerTexture = Textures.getTextures()["ash"]  # player texture

        self.__cameraTween = None  # the camera tween

        self.__drawRectX = 0  # draw rect x position in the map
        self.__drawRectY = 0  # draw rect y position in the map
        self.__cameraOffsetX = TweenSubject(0)  # camera x offset in px in the map
        self.__cameraOffsetY = TweenSubject(0)  # camera y offset in px in the map

    def load(self):
        super().load()

        print("Loading map " + self.__mapName + "...")

        # Load the map data
        mapData = None

        with open(os.path.join(Constants.MAPS_PATH, self.__mapName + ".json"), "r") as f:
            mapData = json.loads(f.read())

        if mapData["tilewidth"] != mapData["tileheight"]:
            raise Exception("The tile width and height must not be different")

        self.__mapWidth = mapData["width"]
        self.__mapHeight = mapData["height"]
        self.__tileSize = mapData["tilewidth"]

        print("     Map size in tiles : " + str(self.__mapWidth) + "*" + str(self.__mapHeight))
        print("     Tile size in px : " + str(self.__tileSize))

        # Tiles count in the window
        if self.getEngine().getResolution()[0] % self.__tileSize != 0 or self.getEngine().getResolution()[1] % self.__tileSize != 0:
            raise Exception("The window resolution must be a multiple of the map's tile size")

        self.__windowWidth = int(self.getEngine().getResolution()[0] / self.__tileSize)
        self.__windowHeight = int(self.getEngine().getResolution()[1] / self.__tileSize)

        print("     Window size in tiles : " + str(self.__windowWidth) + "*" + str(self.__windowHeight))

        # Load tileset texture
        self.__tilesetName = mapData["tilesets"][0]["source"][21:-4]

        print("     Tileset name : " + self.__tilesetName)

        self.__tilesetTexture = Textures.getTextures()["tilesets." + self.__tilesetName]

        # Load tileset data
        tilesetData = None

        with open(os.path.join(Constants.TILESETS_PATH, self.__tilesetName + ".json"), "r") as f:
            tilesetData = json.loads(f.read())

        layersCount = len(mapData["layers"])

        print("     Layers count : " + str(layersCount))

        # Get list of texture coords
        tileIdToTextureCoords = {}
        tileCount = 0
        for y in range(int(tilesetData["imageheight"] / self.__tileSize)):
            for x in range(int(tilesetData["imagewidth"] / self.__tileSize)):
                tileIdToTextureCoords[tileCount] = (x * self.__tileSize,
                                                    y * self.__tileSize,
                                                    self.__tileSize,
                                                    self.__tileSize)
                tileCount += 1

        # Create tiles cache
        tileCount = 0

        # For each tile
        for y in range(self.__mapHeight):
            self.__tilesMatrix0.append([])
            self.__tilesMatrix1.append([])
            for x in range(self.__mapWidth):
                self.__tilesMatrix0[y].append([])
                self.__tilesMatrix1[y].append([])

                # Tile data allocation
                tile0 = Tile()
                tile0.surface = pygame.Surface([self.__tileSize, self.__tileSize])
                self.__tilesMatrix0[y][x] = tile0

                tile1 = Tile()
                tile1.surface = pygame.Surface([self.__tileSize, self.__tileSize], pygame.SRCALPHA, 32)
                self.__tilesMatrix1[y][x] = tile1

                above = False

                # For each layer
                for lId in range(layersCount):
                    layer = mapData["layers"][lId]

                    tileId = layer["data"][tileCount]

                    if tileId == 0:
                        continue

                    tileId -= 1
                    tileCoords = tileIdToTextureCoords[tileId]

                    strTileId = str(tileId)

                    # if there is at least one tile which is above the events
                    # all the subsequent tiles will be above, regardless of the layer
                    if strTileId in tilesetData["tiles"] and tilesetData["tiles"][strTileId]["type"] == Tile.TYPE_ABOVE_EVENTS:
                        above = True

                    # Blit on the correct tile
                    if above:
                        toBlit = self.__tilesMatrix1[y][x].surface
                    else:
                        toBlit = self.__tilesMatrix0[y][x].surface

                    toBlit.blit(self.__tilesetTexture, (0, 0), tileCoords)

                tileCount += 1

        print("Done loading map")

    def unload(self):
        super().unload()

    def draw(self):
        super().draw()

        # First layer
        self.drawMatrix(self.__tilesMatrix0)

        # Events
        self.__window.blit(self.__playerTexture, (10 * self.__tileSize, 10 * self.__tileSize))

        # Second layer
        self.drawMatrix(self.__tilesMatrix1)


    def update(self, dt, events):
        super().update(dt, events)

        self.updateTween(self.__cameraTween, dt)

        # TODO Make a working character : move the character OR the camera, but never both at the same time ?

        if not self.__inputsBlocked:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                if self.__drawRectX > 0:
                    self.__cameraTween = self.createTween("cq", self.__cameraOffsetX,
                                                                          self.__cameraOffsetX.value + self.__tileSize,
                                                                          TestNotSlowMapScene.CAMERA_MOVEMENT_DURATION,
                                                                          Easing.easingLinear)
                    self.__inputsBlocked = True
            elif keys[pygame.K_RIGHT]:
                if self.__drawRectX + self.__windowWidth < self.__mapWidth:
                    self.__cameraTween = self.createTween("cd", self.__cameraOffsetX,
                                                                          self.__cameraOffsetX.value - self.__tileSize,
                                                                          TestNotSlowMapScene.CAMERA_MOVEMENT_DURATION,
                                                                          Easing.easingLinear)
                    self.__inputsBlocked = True
            elif keys[pygame.K_UP]:
                if self.__drawRectY > 0:
                    self.__cameraTween = self.createTween("cz", self.__cameraOffsetY,
                                                                          self.__cameraOffsetY.value + self.__tileSize,
                                                                          TestNotSlowMapScene.CAMERA_MOVEMENT_DURATION,
                                                                          Easing.easingLinear)
                    self.__inputsBlocked = True
            elif keys[pygame.K_DOWN]:
                if self.__drawRectY + self.__windowHeight < self.__mapHeight:
                    self.__cameraTween = self.createTween("cs", self.__cameraOffsetY,
                                                                          self.__cameraOffsetY.value - self.__tileSize,
                                                                          TestNotSlowMapScene.CAMERA_MOVEMENT_DURATION,
                                                                          Easing.easingLinear)
                    self.__inputsBlocked = True

    def drawMatrix(self, matrix):
        # Draw the map
        for y in range(self.__windowHeight + 2):
            for x in range(self.__windowWidth + 2):
                trueX = x-1
                trueY = y-1

                yInMatrix = trueY + self.__drawRectY
                xInMatrix = trueX + self.__drawRectX

                try:
                    tileToDraw = matrix[yInMatrix][xInMatrix]
                except IndexError:
                    continue

                self.__window.blit(tileToDraw.surface, (trueX * self.__tileSize + self.__cameraOffsetX.value, trueY * self.__tileSize + self.__cameraOffsetY.value))

    def onTweenFinished(self, tag):
        super().onTweenFinished(tag)
        if tag == "cs":
            self.__drawRectY += 1
            self.__cameraOffsetY.value = 0
        elif tag == "cz":
            self.__drawRectY -= 1
            self.__cameraOffsetY.value = 0
        elif tag == "cq":
            self.__drawRectX -= 1
            self.__cameraOffsetX.value = 0
        elif tag == "cd":
            self.__drawRectX += 1
            self.__cameraOffsetX.value = 0

        self.__inputsBlocked = False

