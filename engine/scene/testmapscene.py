import json
import os

import pygame

from data.constants import Constants
from data.textures import Textures
from engine.scene.scene import Scene
from engine.tween.Easing import Easing
from engine.tween.TweenParameters import TweenParameters
from engine.tween.TweenSubject import TweenSubject
from lib.get_image_size import get_image_size


class TestMapScene(Scene):

    CAMERA_MOVEMENT_DELAY = 150

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
        self.__cameraOffsetX = TweenSubject(0)  # camera x offset in px
        self.__cameraOffsetY = TweenSubject(0)  # camera y offset in px
        self.__inputsBlocked = False  # self-explanatory

        self.__cameraTween = None

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

        self.updateTween(self.__cameraTween, dt)

        if not self.__inputsBlocked:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                if self.__offsetY > 0:
                    self.__cameraTween = self.createTween(TweenParameters("z", self.__cameraOffsetY, self.__cameraOffsetY.getValue() + self.__mapTilesSize, TestMapScene.CAMERA_MOVEMENT_DELAY,
                                            Easing.easingLinear))
                    self.__inputsBlocked = True
            elif keys[pygame.K_DOWN]:
                if self.__offsetY + self.__windowTilesHeight < self.__mapSize[0]:
                    self.__cameraTween = self.createTween(TweenParameters("s", self.__cameraOffsetY, self.__cameraOffsetY.getValue() - self.__mapTilesSize, TestMapScene.CAMERA_MOVEMENT_DELAY,
                                            Easing.easingLinear))
                    self.__inputsBlocked = True
            elif keys[pygame.K_LEFT]:
                if self.__offsetX > 0:
                    self.__cameraTween = self.createTween(TweenParameters("q", self.__cameraOffsetX, self.__cameraOffsetX.getValue() + self.__mapTilesSize, TestMapScene.CAMERA_MOVEMENT_DELAY,
                                            Easing.easingLinear))
                    self.__inputsBlocked = True
            elif keys[pygame.K_RIGHT]:
                if self.__offsetX + self.__windowTilesWidth < self.__mapSize[1]:
                    self.__cameraTween = self.createTween(TweenParameters("d", self.__cameraOffsetX, self.__cameraOffsetX.getValue() - self.__mapTilesSize, TestMapScene.CAMERA_MOVEMENT_DELAY,
                                            Easing.easingLinear))
                    self.__inputsBlocked = True

    def onTweenFinished(self, tag):
        super().onTweenFinished(tag)
        if tag == "s":
            self.__offsetY += 1
            self.__cameraOffsetY.setValue(0)
            self.__inputsBlocked = False
        elif tag == "z":
            self.__offsetY -= 1
            self.__cameraOffsetY.setValue(0)
            self.__inputsBlocked = False
        elif tag == "q":
            self.__offsetX -= 1
            self.__cameraOffsetX.setValue(0)
            self.__inputsBlocked = False
        elif tag == "d":
            self.__offsetX += 1
            self.__cameraOffsetX.setValue(0)
            self.__inputsBlocked = False

    def draw(self):
        for y in range(self.__windowTilesHeight + 2):
            for x in range(self.__windowTilesWidth + 2):
                for l in range(self.__layersCount):
                    yInMatrix = (y-1) + self.__offsetY
                    xInMatrix = (x-1) + self.__offsetX

                    if yInMatrix < 0 or xInMatrix < 0 or yInMatrix > len(self.__tilesMatrix[l])-1 or xInMatrix > len(self.__tilesMatrix[l][y-1])-1:
                        tileToDraw = 0
                    else:
                        tileToDraw = self.__tilesMatrix[l][yInMatrix][xInMatrix]

                    if tileToDraw == 0:
                        continue

                    tileToDraw -= 1

                    drawCoordinateX = (x-1) * self.__mapTilesSize + self.__cameraOffsetX.getValue()
                    drawCoordinateY = (y-1) * self.__mapTilesSize + self.__cameraOffsetY.getValue()

                    coordinatesOnTexture = self.__mapTiles[tileToDraw]

                    self.getEngine().getWindow().blit(Textures.getTextures()["maps." + self.__map], (drawCoordinateX, drawCoordinateY), coordinatesOnTexture)