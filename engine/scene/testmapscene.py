import json
import os

import pygame

from data.constants import Constants
from data.textures import Textures
from engine.scene.scene import Scene
from engine.tween.easing import Easing
from engine.tween.tweensubject import TweenSubject
from lib.get_image_size import get_image_size


class TestMapScene(Scene):

    CAMERA_MOVEMENT_DURATION = 150

    # TODO Add tile caching to reduce the number of blits per frame
    # TODO Add player spawn position to __init__

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

        self.__characterX = 10  # x position of the character in tiles
        self.__characterY = 10  # y position of the character in tiles

        self.__characterOffsetX = TweenSubject(0)  # offset x of the character in px
        self.__characterOffsetY = TweenSubject(0)  # offset y of the character in px

        self.__cameraTween = None
        self.__playerTween = None

        self.__mapTexture = Textures.getTextures()["tilesets." + self.__map]
        self.__characterTexture = Textures.getTextures()["ash"]

        self.__window = self.getEngine().getWindow()

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
        mapTexture = "tilesets." + self.__mapData["tilesets"][0]["source"][17:-4]

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
        self.updateTween(self.__playerTween, dt)

        # TODO Make a working character : move the character OR the camera, but never both at the same time ?

        if not self.__inputsBlocked:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                #self.__playerTween = self.createTween("pl", self.__characterX, self.__characterX.getValue() - 1, TestMapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear)
                if self.__offsetX > 0:
                    self.__cameraTween = self.createTween("cq", self.__cameraOffsetX,
                                                                          self.__cameraOffsetX.value + self.__mapTilesSize,
                                                                          TestMapScene.CAMERA_MOVEMENT_DURATION,
                                                                          Easing.easingLinear)
                    self.__inputsBlocked = True
            elif keys[pygame.K_RIGHT]:
                #self.__playerTween = self.createTween("pr", self.__characterX, self.__characterX.getValue() + 1, TestMapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear)
                if self.__offsetX + self.__windowTilesWidth < self.__mapSize[1]:
                    self.__cameraTween = self.createTween("cd", self.__cameraOffsetX,
                                                                          self.__cameraOffsetX.value - self.__mapTilesSize,
                                                                          TestMapScene.CAMERA_MOVEMENT_DURATION,
                                                                          Easing.easingLinear)
                    self.__inputsBlocked = True
            elif keys[pygame.K_UP]:
                #self.__playerTween = self.createTween("pu", self.__characterY, self.__characterY.getValue() - 1, TestMapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear)
                if self.__offsetY > 0:
                    self.__cameraTween = self.createTween("cz", self.__cameraOffsetY,
                                                                          self.__cameraOffsetY.value + self.__mapTilesSize,
                                                                          TestMapScene.CAMERA_MOVEMENT_DURATION,
                                                                          Easing.easingLinear)
                    self.__inputsBlocked = True
            elif keys[pygame.K_DOWN]:
                #self.__playerTween = self.createTween("pd", self.__characterY, self.__characterY.getValue() + 1, TestMapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear)
                if self.__offsetY + self.__windowTilesHeight < self.__mapSize[0]:
                    self.__cameraTween = self.createTween("cs", self.__cameraOffsetY,
                                                                          self.__cameraOffsetY.value - self.__mapTilesSize,
                                                                          TestMapScene.CAMERA_MOVEMENT_DURATION,
                                                                          Easing.easingLinear)
                    self.__inputsBlocked = True
    def onTweenFinished(self, tag):
        super().onTweenFinished(tag)
        if tag == "cs":
            self.__offsetY += 1
            self.__cameraOffsetY.value = 0
        elif tag == "cz":
            self.__offsetY -= 1
            self.__cameraOffsetY.value = 0
        elif tag == "cq":
            self.__offsetX -= 1
            self.__cameraOffsetX.value = 0
        elif tag == "cd":
            self.__offsetX += 1
            self.__cameraOffsetX.value = 0

        self.__inputsBlocked = False

    def draw(self):
        # Draw the map
        for y in range(self.__windowTilesHeight + 2):
            for x in range(self.__windowTilesWidth + 2):
                for l in range(self.__layersCount):
                    trueX = x-1
                    trueY = y-1

                    yInMatrix = (trueY) + self.__offsetY
                    xInMatrix = (trueX) + self.__offsetX

                    try:
                        tileToDraw = self.__tilesMatrix[l][yInMatrix][xInMatrix] - 1
                    except IndexError:
                        tileToDraw = 0

                    if tileToDraw == 0:  # can be 0 because of IndexError or just because there isn't a tile there
                        continue

                    drawCoordinateX = (trueX) * self.__mapTilesSize + self.__cameraOffsetX.value
                    drawCoordinateY = (trueY) * self.__mapTilesSize + self.__cameraOffsetY.value

                    coordinatesOnTexture = self.__mapTiles[tileToDraw]

                    self.__window.blit(self.__mapTexture, (drawCoordinateX, drawCoordinateY), coordinatesOnTexture)

        # Draw the character
        self.__window.blit(self.__characterTexture, (self.__characterX.value * self.__mapTilesSize, self.__characterY.value * self.__mapTilesSize))