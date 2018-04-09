import importlib
import math
from typing import Tuple, List

import pygame

from data.constants import Constants
from engine.graphics.textures import Textures, Engine
from engine.graphics.charset import Charset
from engine.scene.map.actors.actor import Actor
from engine.scene.map.tile import Tile
from engine.scene.scene import Scene
import os
import json

from engine.tween.easing import Easing
from engine.tween.tween import Tween
from engine.tween.tweensubject import TweenSubject


class MapScene(Scene):

    CAMERA_MOVEMENT_DURATION = 200
    STEP_DURATION = 100

    def __init__(self, engine : Engine, map : str, spawnPosition : Tuple):
        super().__init__(engine)

        self.__mapName = map  # the map name

        self.__tilesetName = ""
        self.__tilesetTexture = None  # the tileset texture surface

        self.__tileSize = 0  # the size of one tile in px

        self.__mapWidth = 0  # the map width in tiles
        self.__mapHeight = 0  # the map height in tiles

        self.__windowWidth = 0  # width of the window in tiles (depends on tileSize)
        self.__windowHeight = 0  # height of the window in tiles (depends on tileSize)

        self.__tilesMatrix0 = []  # matrix of Tile objects to draw below the actors
        self.__tilesMatrix1 = []  # matrix of Tile objects surfaces to draw above the actors

        self.__inputsBlocked = False  # self-explanatory

        self.__window = self.getEngine().getWindow()  # the game window

        self.__characterCharset = Charset.ofTexture("charsets.character", Charset.ORIENTATION_DOWN)   # character charset
        self.__characterCharsetOffsetX = 0  # quarter the width of the step texture
        self.__characterCharsetOffsetY = 0  # half the height of the step texture

        self.__cameraTween = None  # the camera tween
        self.__characterTween = None  # the player tween

        self.__characterX = spawnPosition[0] # x position of the character in tiles
        self.__characterY = spawnPosition[1]  # y position of the character in tiles

        # TODO Initialize this properly / be able to (1) spawn player at any given position AND (2) place camera accordingly
        self.__characterXOnScreen = self.__characterX # x position on screen of the character in tiles
        self.__characterYOnScreen = self.__characterY  # y position on screen of the character in tiles

        self.__drawRectX = 0  # draw rect x position in the map
        self.__drawRectY = 0  # draw rect y position in the map
        self.__cameraOffsetX = TweenSubject(0)  # camera x offset in px in the map
        self.__cameraOffsetY = TweenSubject(0)  # camera y offset in px in the map

        self.__characterOffsetX = TweenSubject(0)  # offset x of the character in px
        self.__characterOffsetY = TweenSubject(0)  # offset y of the character in px

        # if the player is inside this rect (in tiles relative to the camera)
        # and the camera can move, the camera tween will be used instead of the player tween
        # X is for lateral movements, Y is for up / down movements
        # tuple (position, position + width) and (position, position + height)
        self.__cameraMovementRectX = (0, 0)
        self.__cameraMovementRectY = (0, 0)

        self.__characterMoving = False  # is the character moving ?

        # if the map is smaller than the window
        # offset all render by these values (in px)
        self.__mapOffsetX = 0
        self.__mapOffsetY = 0

        self.actorsMatrix = []  # actors matrix

        self.__touchEventProcessed = False  # used to prevent touch events spamming

        self.__dt = 0  # delta-time given by pygame clock
        self.__events = None  # pygame events

    def getTileSize(self) -> int:
        return self.__tileSize

    def getCharacterPosition(self) -> Tuple:
        return (self.__characterX, self.__characterY)

    def getMapName(self) -> str:
        return self.__mapName

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

        # Map offsets
        if self.__mapWidth < self.__windowWidth:
            self.__mapOffsetX = int((self.__windowWidth - self.__mapWidth) / 2) * self.__tileSize
            print("     Map offset X : " + str(self.__mapOffsetX))

        if self.__mapHeight < self.__windowHeight:
            self.__mapOffsetY = int((self.__windowHeight - self.__mapHeight) / 2) * self.__tileSize
            print("     Map offset Y : " + str(self.__mapOffsetX))

        # Camera scroll rect
        if self.__windowWidth % 2 == 0:
            self.__cameraMovementRectX = (self.__windowWidth/2-1, self.__windowWidth/2-1 + 2)
        else:
            self.__cameraMovementRectX = (math.floor(self.__windowWidth / 2), math.floor(self.__windowWidth / 2) + 1)

        if self.__windowHeight % 2 == 0:
            self.__cameraMovementRectY = (self.__windowHeight / 2 - 1, self.__windowHeight / 2 - 1 + 2)
        else:
            self.__cameraMovementRectY = (math.floor(self.__windowHeight / 2), math.floor(self.__windowHeight / 2) + 1)

        print("     Camera scroll boundaries : x : " + str(self.__cameraMovementRectX) + ", y :" + str(self.__cameraMovementRectY))

        # Load tileset texture
        self.__tilesetName = mapData["tilesets"][0]["source"][21:-4]

        print("     Tileset name : " + self.__tilesetName)

        self.__tilesetTexture = Textures.getTextures()["tilesets." + self.__tilesetName]

        # Load player charset
        self.__characterCharset.load()
        self.__characterCharsetOffsetX = int(self.__characterCharset.getSurfaceWidth() / 4)
        self.__characterCharsetOffsetY = int(self.__characterCharset.getSurfaceHeight() / 2)

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

                    # if there is at least one tile which is above the actors
                    # all the subsequent tiles will be above, regardless of the layer
                    if strTileId in tilesetData["tiles"] and tilesetData["tiles"][strTileId]["type"] == Tile.TYPE_ABOVE_ACTORS:
                        above = True

                    # Blit on the correct tile
                    if above:
                        tile = self.__tilesMatrix1[y][x]
                    else:
                        tile = self.__tilesMatrix0[y][x]

                    tile.surface.blit(self.__tilesetTexture, (0, 0), tileCoords)

                    # Collision flags
                    if strTileId in tilesetData["tileproperties"]:
                        tileProperties = tilesetData["tileproperties"][strTileId]
                        if "collision" in tileProperties:
                            collisionStr = tileProperties["collision"]

                            if len(collisionStr) > 0:
                                for flag in collisionStr.split(";"):
                                    if flag == "top":
                                        tile.collision = (True, tile.collision[1], tile.collision[2], tile.collision[3])
                                    elif flag == "right":
                                        tile.collision = (tile.collision[0], True, tile.collision[2], tile.collision[3])
                                    elif flag == "bottom":
                                        tile.collision = (tile.collision[0], tile.collision[1], True, tile.collision[3])
                                    elif flag == "left":
                                        tile.collision = (tile.collision[0], tile.collision[1], tile.collision[2], True)
                                    else:
                                        raise Exception("Unknown collision parameter : " + flag)

                # if there was no tile drawn on the above layer, discard the tile
                if not above:
                    self.__tilesMatrix1[y][x] = None

                tileCount += 1

        # Load and spawn actors
        for y in range(self.__mapHeight):
            self.actorsMatrix.append([])
            for x in range(self.__mapWidth):
                self.actorsMatrix[y].append([])
                self.actorsMatrix[y][x] = None

        try:

            with open(os.path.join(Constants.ACTORS_PATH, self.__mapName, "actors.json"), "r") as f:
                actorsData = json.loads(f.read())

            print("     Actors count : " + str(len(actorsData)))

            actorModules = {}

            for actor in actorsData:

                actorX = actor["positionX"]
                actorY = actor["positionY"]

                # Default values
                if "type" not in actor:
                    actor["type"] = "Actor"

                if "parameters" not in actor:
                    actor["parameters"] = {}

                if "script" not in actor:
                    actor["script"] = None

                if not actor["type"] in actorModules:
                    actorModules[actor["type"]] = importlib.import_module("engine.scene.map.actors." + actor["type"].lower())

                actorClass = getattr(actorModules[actor["type"]], actor["type"])

                actorInstance = actorClass(self, actorX, actorY, actor["parameters"], actor["script"])

                actorInstance.load()
                actorInstance.spawn()

        except FileNotFoundError as e:
            print("     No actors found for this map")

        print("Done loading map")

    def spawnActor(self, actor : Actor, posX : int, posY : int):
        self.actorsMatrix[posY][posX] = actor

    def despawnActor(self, posX : int, posY : int):
        self.actorsMatrix[posY][posX] = None


    def unload(self):
        super().unload()

        for y in range(self.__mapHeight):
            for x in range(self.__mapWidth):
                actor = self.actorsMatrix[y][x]
                if actor is not None:
                    actor.despawn()
                    actor.unload()

    def updateActorPosition(self, oldX : int, oldY : int, newX : int, newY : int):
        actor = self.actorsMatrix[oldY][oldX]

        if self.actorsMatrix[newY][newX] is not None:
            raise Exception("Cannot move an actor on top of another")

        if actor is not None:
            self.actorsMatrix[oldY][oldX] = None
            self.actorsMatrix[newY][newX] = actor

    def getCharacterOrientation(self) -> int:
        return self.__characterCharset.getOrientation()

    def draw(self):
        super().draw()

        # First layer
        self.drawMatrix(self.__tilesMatrix0)

        clockTime = self.getEngine().getClockTime()

        # Actors and character
        for y in range(self.__mapHeight):
            for x in range(self.__mapWidth):
                actor = self.actorsMatrix[y][x]

                if actor is not None and actor.lastUpdateDate != clockTime:
                    actor.update(self.__dt, self.__events)
                    actor.draw(self.__cameraOffsetX.value - self.__drawRectX * self.__tileSize + self.__mapOffsetX, self.__cameraOffsetY.value - self.__drawRectY * self.__tileSize + self.__mapOffsetY)
                    actor.lastUpdateTime = clockTime

                # Character
                if y == self.__characterY and x == self.__characterX:
                    self.__window.blit(self.__characterCharset.getCurrentSurface(),
                           (self.__characterXOnScreen * self.__tileSize + self.__characterOffsetX.value - self.__characterCharsetOffsetX + self.__mapOffsetX, self.__characterYOnScreen * self.__tileSize + self.__characterOffsetY.value - self.__characterCharsetOffsetY + self.__mapOffsetY))

        # Second layer
        self.drawMatrix(self.__tilesMatrix1)

    def canCameraMoveLeft(self) -> bool:
        return self.__drawRectX > 0

    def canCameraMoveRight(self) -> bool:
        return self.__drawRectX + self.__windowWidth < self.__mapWidth

    def canCameraMoveUp(self) -> bool:
        return self.__drawRectY > 0

    def canCameraMoveDown(self) -> bool:
        return self.__drawRectY + self.__windowHeight < self.__mapHeight

    def canCharacterMoveLeft(self) -> bool:
        # Actor collision
        facingActor = self.getActorWhichCharacterFaces()

        if facingActor is not None and not facingActor.isPassThrough():
            return False

        # Tile collision
        try:
            return self.__characterX > 0 and not (self.__tilesMatrix0[self.__characterY][self.__characterX-1].collision[1])
        except IndexError:
            return False

    def canCharacterMoveRight(self) -> bool:
        # Actor collision
        facingActor = self.getActorWhichCharacterFaces()

        if facingActor is not None and not facingActor.isPassThrough():
            return False

        # Tile collision
        try:
            return not self.__tilesMatrix0[self.__characterY][self.__characterX+1].collision[3]
        except IndexError:
            return False

    def canCharacterMoveUp(self) -> bool:
        # Actor collision
        facingActor = self.getActorWhichCharacterFaces()

        if facingActor is not None and not facingActor.isPassThrough():
            return False

        # Tile collision
        try:
            return self.__characterY > 0 and not (self.__tilesMatrix0[self.__characterY - 1][self.__characterX].collision[2])
        except IndexError:
            return False

    def canCharacterMoveDown(self) -> bool:
        # Actor collision
        facingActor = self.getActorWhichCharacterFaces()

        if facingActor is not None and not facingActor.isPassThrough():
            return False

        # Tile collision
        try:
            return not self.__tilesMatrix0[self.__characterY + 1][self.__characterX].collision[0]
        except IndexError:
            return False


    def getActorWhichCharacterFaces(self) -> Actor:
        actorPosX = self.__characterX
        actorPosY = self.__characterY

        orientation = self.__characterCharset.getOrientation()

        if orientation == Charset.ORIENTATION_DOWN:
            actorPosY += 1
        elif orientation == Charset.ORIENTATION_UP:
            actorPosY -= 1
        elif orientation == Charset.ORIENTATION_LEFT:
            actorPosX -= 1
        elif orientation == Charset.ORIENTATION_RIGHT:
            actorPosX += 1

        if actorPosX < 0 or actorPosY < 0:
            return None

        try:
            return self.actorsMatrix[actorPosY][actorPosX]
        except IndexError:
            return None

    def update(self, dt : int, events : List[pygame.event.Event]):
        super().update(dt, events)

        self.__dt = dt
        self.__events = events

        if self.__cameraTween is not None:
            self.__cameraTween.update(dt)

        if self.__characterTween is not None:
            self.__characterTween.update(dt)

        if not self.__inputsBlocked:

            orientation = self.__characterCharset.getOrientation()

            # Pygame events
            for event in events:
                # Return key (action)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:

                        gameActor = self.getActorWhichCharacterFaces()

                        if gameActor is not None:
                            gameActor.onActionPressed(orientation)

            # Arrow keys
            keys = pygame.key.get_pressed()

            playerPosXOnScreen = self.__characterXOnScreen - self.__cameraOffsetX.value
            playerPosYOnScreen = self.__characterYOnScreen - self.__cameraOffsetY.value

            isPlayerInCameraScrollRectX = (playerPosXOnScreen >= self.__cameraMovementRectX[0]) and (playerPosXOnScreen <= self.__cameraMovementRectX[1])
            isPlayerInCameraScrollRectY = (playerPosYOnScreen >= self.__cameraMovementRectY[0]) and (playerPosYOnScreen <= self.__cameraMovementRectY[1])

            if keys[pygame.K_LEFT]:
                self.__characterCharset.setOrientation(Charset.ORIENTATION_LEFT)
                self.processTouchEvent()
                if self.canCharacterMoveLeft():
                    self.__characterCharset.incrementStep()
                    if isPlayerInCameraScrollRectX and self.canCameraMoveLeft():
                        self.__cameraTween = Tween("cq", self.__cameraOffsetX, self.__cameraOffsetX.value + self.__tileSize, MapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear, self.tweensCallback)
                    else:
                        self.__characterTween = Tween("pq", self.__characterOffsetX, self.__characterOffsetX.value - self.__tileSize, MapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear, self.tweensCallback)
                    self.__characterMoving = True
                    self.__inputsBlocked = True
            elif keys[pygame.K_RIGHT]:
                self.__characterCharset.setOrientation(Charset.ORIENTATION_RIGHT)
                self.processTouchEvent()
                if self.canCharacterMoveRight():
                    self.__characterCharset.incrementStep()
                    if isPlayerInCameraScrollRectX and self.canCameraMoveRight():
                        self.__cameraTween = Tween("cd", self.__cameraOffsetX, self.__cameraOffsetX.value - self.__tileSize, MapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear, self.tweensCallback)
                    else:
                        self.__characterTween = Tween("pd", self.__characterOffsetX, self.__characterOffsetX.value + self.__tileSize, MapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear, self.tweensCallback)
                    self.__characterMoving = True
                    self.__inputsBlocked = True
            elif keys[pygame.K_UP]:
                self.__characterCharset.setOrientation(Charset.ORIENTATION_UP)
                self.processTouchEvent()
                if self.canCharacterMoveUp():
                    self.__characterCharset.incrementStep()
                    if isPlayerInCameraScrollRectY and self.canCameraMoveUp():
                        self.__cameraTween = Tween("cz", self.__cameraOffsetY, self.__cameraOffsetY.value + self.__tileSize, MapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear, self.tweensCallback)
                    else:
                        self.__characterTween = Tween("pz", self.__characterOffsetY, self.__characterOffsetY.value - self.__tileSize, MapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear, self.tweensCallback)
                    self.__characterMoving = True
                    self.__inputsBlocked = True
            elif keys[pygame.K_DOWN]:
                self.__characterCharset.setOrientation(Charset.ORIENTATION_DOWN)
                self.processTouchEvent()
                if self.canCharacterMoveDown():
                    self.__characterCharset.incrementStep()
                    if isPlayerInCameraScrollRectY and self.canCameraMoveDown():
                        self.__cameraTween = Tween("cs", self.__cameraOffsetY, self.__cameraOffsetY.value - self.__tileSize, MapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear, self.tweensCallback)
                    else:
                        self.__characterTween = Tween("ps", self.__characterOffsetY, self.__characterOffsetY.value + self.__tileSize, MapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear, self.tweensCallback)
                    self.__characterMoving =  True
                    self.__inputsBlocked = True
            elif self.__characterMoving:
                self.__characterMoving = False
                self.__characterCharset.resetStep()
            else:
                self.__touchEventProcessed = False


    def drawMatrix(self, matrix : List[List]):
        # Draw the map
        for y in range(self.__windowHeight + 2):
            for x in range(self.__windowWidth + 2):
                trueX = x-1
                trueY = y-1

                yInMatrix = trueY + self.__drawRectY
                xInMatrix = trueX + self.__drawRectX

                if xInMatrix < 0 or yInMatrix < 0:
                    continue

                try:
                    tileToDraw = matrix[yInMatrix][xInMatrix]
                except IndexError:
                    continue

                if tileToDraw is not None:
                    self.__window.blit(tileToDraw.surface, (trueX * self.__tileSize + self.__cameraOffsetX.value + self.__mapOffsetX, trueY * self.__tileSize + self.__cameraOffsetY.value + self.__mapOffsetY))


    def onCharacterEnteredTile(self):
        actor = self.actorsMatrix[self.__characterY][self.__characterX]

        if actor is not None:
            actor.onCharacterEnteredTile(self.__characterCharset.getOrientation())

    def processTouchEvent(self):
        if self.__touchEventProcessed:
            return

        actor = self.getActorWhichCharacterFaces()
        if actor is not None:
            actor.onCharacterTouchEvent(self.__characterCharset.getOrientation())
            self.__touchEventProcessed = True

    def tweensCallback(self, tag):
        if tag == "cs":
            self.__drawRectY += 1
            self.__cameraOffsetY.value = 0
            self.__characterY += 1

            self.onCharacterEnteredTile()
        elif tag == "cz":
            self.__drawRectY -= 1
            self.__cameraOffsetY.value = 0
            self.__characterY -= 1

            self.onCharacterEnteredTile()
        elif tag == "cq":
            self.__drawRectX -= 1
            self.__cameraOffsetX.value = 0
            self.__characterX -= 1

            self.onCharacterEnteredTile()
        elif tag == "cd":
            self.__drawRectX += 1
            self.__cameraOffsetX.value = 0
            self.__characterX += 1

            self.onCharacterEnteredTile()
        elif tag == "pq":
            self.__characterOffsetX.value = 0
            self.__characterXOnScreen -= 1
            self.__characterX -= 1

            self.onCharacterEnteredTile()
        elif tag == "pd":
            self.__characterOffsetX.value = 0
            self.__characterXOnScreen += 1
            self.__characterX += 1

            self.onCharacterEnteredTile()
        elif tag == "pz":
            self.__characterOffsetY.value = 0
            self.__characterYOnScreen -= 1
            self.__characterY -= 1

            self.onCharacterEnteredTile()
        elif tag == "ps":
            self.__characterOffsetY.value = 0
            self.__characterYOnScreen += 1
            self.__characterY += 1

            self.onCharacterEnteredTile()

        self.__inputsBlocked = False

