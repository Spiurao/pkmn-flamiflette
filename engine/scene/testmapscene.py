import json
import os

import pygame

from data.constants import Constants
from data.textures import Textures
from engine.scene.scene import Scene
from lib.get_image_size import get_image_size


class TestMapScene(Scene):
    def __init__(self, engine, map):
        super().__init__(engine)
        self.__map = map
        self.__mapSize = (0,0)
        self.__mapTilesSize = 0
        self.__mapTiles = []  # array of tileNumber -> coordinates in the texture : 0 : (0,0), 1 : (0,16), etc...
        self.__offsetX = 0
        self.__offsetY = 0

    def load(self):
        # We load the map
        with open(os.path.join(Constants.MAPS_PATH, self.__map + ".map"), "r") as f:
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

        print("Loaded map '" + self.__map + "' with size " + str(self.__mapSize) + ", tile size " + str(self.__mapTilesSize) + ", texture " + mapTexture + ", texture size " + str(width) + "x" + str(height))

    def update(self, dt, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_DOWN:
                    self.__offsetY -= self.__mapTilesSize
                elif e.key == pygame.K_UP:
                    self.__offsetY += self.__mapTilesSize
                elif e.key == pygame.K_LEFT:
                    self.__offsetX += self.__mapTilesSize
                elif e.key == pygame.K_RIGHT:
                    self.__offsetX -= self.__mapTilesSize
    def draw(self):
        # TODO Draw window x*y tiles based on camera position instead of iterating over the whole tiles
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

    def unload(self):
        # Unload the map
        self.__mapData = None