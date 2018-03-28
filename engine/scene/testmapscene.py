import json
import os

import pygame

from data.constants import Constants
from data.textures import Textures
from engine.scene.scene import Scene
from engine.tween.Easing import Easing
from engine.tween.TweenEntry import TweenEntry
from engine.tween.TweenSubject import TweenSubject
from lib.get_image_size import get_image_size


class TestMapScene(Scene):
    def __init__(self, engine, map):
        super().__init__(engine)
        self.__map = map  # map name
        self.__mapSize = (0,0)  # map size in tiles
        self.__mapTilesSize = 0  # size in px of one tile
        self.__mapTiles = []  # array of tileId -> coordinates in the texture : 0 : (0,0), 1 : (0,16), etc...
        self.__tilesMatrix = []  # tilesMatri[layer][y][x] = tileId
        self.__windowTilesWidth = 0  # width of the window in tiles
        self.__windowTilesHeight = 0  # height of the window in tiles
        self.__layersCount = 0  # layers count
        self.__offsetX = 0  # camera x offset in tiles
        self.__offsetY = 0  # camera y offset in tiles
        self.__cameraOffsetX = TweenSubject(0)
        self.__cameraOffsetY = TweenSubject(0)

    def load(self):
        # We load the map
        with open(os.path.join(Constants.MAPS_PATH, self.__map + ".json"), "r") as f:
            self.__mapData = json.loads(f.read())

        # Load the data
        if self.__mapData["tileheight"] != self.__mapData["tilewidth"]:
            raise Exception("The map " + self.__map + " has different tile width and height")

        self.__mapTilesSize = self.__mapData["tilewidth"]
        self.__mapSize = (self.__mapData["width"], self.__mapData["height"])

        # Get map texture
        mapTexture = "maps." + self.__mapData["tilesets"][0]["source"][17:-4]

        # Load image metadata
        width, height = get_image_size(os.path.join(Constants.IMG_PATH, mapTexture.replace(".", os.path.sep) + ".png"))
        tilesWidth = int(width / self.__mapTilesSize)
        tilesHeight = int(height / self.__mapTilesSize)
        for y in range(tilesHeight):
            for x in range(tilesWidth):
                data = (x * self.__mapTilesSize, y * self.__mapTilesSize, self.__mapTilesSize, self.__mapTilesSize)
                self.__mapTiles.append(data)

        # Prepare tiles matrix
        tileCount = 0
        self.__layersCount = 0
        for l in self.__mapData["layers"]:
            self.__tilesMatrix.append([])

            for y in range(self.__mapSize[1]):
                self.__tilesMatrix[self.__layersCount].append([])

                for x in range(self.__mapSize[0]):
                    self.__tilesMatrix[self.__layersCount][y].append(l["data"][tileCount])
                    tileCount += 1

            self.__layersCount += 1
            tileCount = 0

        # Tiles count in the window
        self.__windowTilesWidth = int(self.getEngine().getResolution()[0] / self.__mapTilesSize)
        self.__windowTilesHeight = int(self.getEngine().getResolution()[1] / self.__mapTilesSize)

        print("Loaded map '" + self.__map + "' with size " + str(self.__mapSize) + ", tile size " + str(self.__mapTilesSize) + ", texture " + mapTexture + ", texture size " + str(width) + "x" + str(height))

    def update(self, dt, events):
        super().update(dt, events)
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.__offsetY += 1
                elif e.key == pygame.K_UP:
                    self.__offsetY -= 1
                elif e.key == pygame.K_LEFT:
                    self.__offsetX -= 1
                elif e.key == pygame.K_RIGHT:
                    self.__offsetX += 1
                elif e.key == pygame.K_z:
                    tween = TweenEntry("z", self.__cameraOffsetY, self.__cameraOffsetY.getValue() + 32, 100, Easing.easingLinear)
                    self.pushTween(tween)
                elif e.key == pygame.K_s:
                    tween = TweenEntry("s", self.__cameraOffsetY, self.__cameraOffsetY.getValue() - 32, 100, Easing.easingLinear)
                    self.pushTween(tween)
                elif e.key == pygame.K_q:
                    tween = TweenEntry("q", self.__cameraOffsetX, self.__cameraOffsetX.getValue() + 32, 100, Easing.easingLinear)
                    self.pushTween(tween)
                elif e.key == pygame.K_d:
                    tween = TweenEntry("d", self.__cameraOffsetX, self.__cameraOffsetX.getValue() - 32, 100, Easing.easingLinear)
                    self.pushTween(tween)

    def onTweenFinished(self, tag):
        super().onTweenFinished(tag)
        if tag == "s":
            self.__offsetY += 1
            self.__cameraOffsetY.setValue(0)
        elif tag == "z":
            self.__offsetY -= 1
            self.__cameraOffsetY.setValue(0)
        elif tag == "q":
            self.__offsetX -= 1
            self.__cameraOffsetX.setValue(0)
        elif tag == "d":
            self.__offsetX += 1
            self.__cameraOffsetX.setValue(0)

    def draw(self):
        # TODO Offset camera
        for y in range(self.__windowTilesHeight):
            for x in range(self.__windowTilesWidth):
                for l in range(self.__layersCount):

                    yInMatrix = y + self.__offsetY
                    xInMatrix = x + self.__offsetX

                    if yInMatrix < 0 or xInMatrix < 0 or yInMatrix > len(self.__tilesMatrix[l])-1 or xInMatrix > len(self.__tilesMatrix[l][y])-1:
                        tileToDraw = 0
                    else:
                        tileToDraw = self.__tilesMatrix[l][yInMatrix][xInMatrix]

                    if tileToDraw == 0:
                        continue

                    tileToDraw -= 1

                    drawCoordinateX = x * self.__mapTilesSize + self.__cameraOffsetX.getValue()
                    drawCoordinateY = y * self.__mapTilesSize + self.__cameraOffsetY.getValue()

                    coordinatesOnTexture = self.__mapTiles[tileToDraw]

                    self.getEngine().getWindow().blit(Textures.getTextures()["maps." + self.__map], (drawCoordinateX, drawCoordinateY), coordinatesOnTexture)

        '''
        for l in self.__mapData["layers"]:
            tileCount = 0
            for y in range(self.__mapSize[1]):
                for x in range(self.__mapSize[0]):
                    tileToDraw = l["data"][tileCount]

                    # because 0 is transparent tile
                    if tileToDraw == 0:
                        tileCount += 1
                        continue

                    tileToDraw -= 1

                    drawCoordinateX = x * self.__mapTilesSize + self.__offsetX
                    drawCoordinateY = y * self.__mapTilesSize + self.__offsetY

                    coordinatesOnTexture = self.__mapTiles[tileToDraw]

                    self.getEngine().getWindow().blit(Textures.getTextures()["maps." + self.__map], (drawCoordinateX, drawCoordinateY), coordinatesOnTexture)

                    tileCount += 1
        '''
    def unload(self):
        # Unload the map
        self.__mapData = None