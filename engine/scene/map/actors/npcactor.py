import math
import pygame
from typing import Dict, List, Any

from engine.graphics.charset import Charset
from engine.scene.map.actors.actor import Actor
from engine.scene.map.mapscene import MapScene
from engine.tween.easing import Easing
from engine.tween.tween import Tween
from engine.tween.tweensubject import TweenSubject


class NPCActor(Actor):
    def __init__(self, scene: MapScene, x: int, y: int, parameters: Dict, script : str, name : str):
        super().__init__(scene, x, y, parameters, script, name)

        self.__charset = Charset.ofTexture(parameters["charset"], parameters["orientation"])

        self.__charsetSurfaceOffset = None
        self.__tileSize = self.getScene().getTileSize()

        self.__moveTween = None
        self.__moving = False

        self.__movingOffsetX = TweenSubject(0)
        self.__movingOffsetY = TweenSubject(0)

        # Cantal functions
        self.registerCantalFunction("turnToFaceCharacter", self.cantalTurnToFaceCharacter)
        self.registerCantalFunction("walk", self.cantalWalk)

    def update(self, dt : int, events : List[pygame.event.Event]):
        super().update(dt, events)
        if self.__moveTween is not None:
            self.__moveTween.update(dt)

    def load(self):
        super().load()
        self.__charset.load()

        self.__charsetSurfaceOffset = (self.__charset.getSurfaceWidth()/4, self.__charset.getSurfaceHeight()/2)

    def draw(self, offsetX : int, offsetY : int):
        super().draw(offsetX, offsetY)

        # No need to check if the charset will be offscreen since pygame does it for us
        self.getWindow().blit(self.__charset.getCurrentSurface(), (self.getPosX() * self.__tileSize - self.__charsetSurfaceOffset[0] + offsetX + self.__movingOffsetX.value * self.__tileSize, self.getPosY() * self.__tileSize - self.__charsetSurfaceOffset[1] + offsetY + self.__movingOffsetY.value * self.__tileSize))

    def isPassThrough(self) -> bool:
        return False

    def unload(self):
        super().unload()
        self.__charset.unload()

    def moveTweenCallback(self, tag : Any):
        self.__moving = False
        self.interpreters[self.currentState][tag].nextStatement()

    def setOrientation(self, orientation : int):
        self.__charset.setOrientation(orientation)

    '''
    CantalScript methods
    '''
    def cantalTurnToFaceCharacter(self, interpreter, functionParameters):
        characterPosition = self.getScene().getCharacterPosition()

        degree = math.degrees(math.atan2(characterPosition[1] - self.getPosY(), characterPosition[0] - self.getPosX()))

        # right : -45 to 45
        # down : 45 to 135
        # left : 135 to -135
        # top : -135 to -45

        if degree >= -45 and degree < 45:
            self.setOrientation(Charset.ORIENTATION_RIGHT)
        elif degree >= 45 and degree < 135:
            self.setOrientation(Charset.ORIENTATION_DOWN)
        elif degree >= -135 and degree < -45:
            self.setOrientation(Charset.ORIENTATION_UP)
        elif degree >= -135 or degree < 135:
            self.setOrientation(Charset.ORIENTATION_LEFT)

        self.interpreters[self.currentState][interpreter].nextStatement()

    def cantalWalk(self, interpreter, functionParams):

        orientation = functionParams[0].literal.getValue()
        stepsCount = functionParams[1].literal.getValue()

        self.__charset.setOrientation(orientation)

        # TODO Walk animation
        # TODO Collision checks
        # TODO Optionnal speed parameter

        if orientation == Charset.ORIENTATION_LEFT:
            self.setPosition(self.getPosX()-stepsCount, self.getPosY())
            self.__movingOffsetX.value = stepsCount
            self.__moveTween = Tween(interpreter, self.__movingOffsetX, 0, MapScene.CAMERA_MOVEMENT_DURATION*stepsCount, Easing.easingLinear, self.moveTweenCallback)
        elif orientation == Charset.ORIENTATION_RIGHT:
            self.setPosition(self.getPosX() + stepsCount, self.getPosY())
            self.__movingOffsetX.value = -stepsCount
            self.__moveTween = Tween(interpreter, self.__movingOffsetX, 0, MapScene.CAMERA_MOVEMENT_DURATION*stepsCount,
                                            Easing.easingLinear, self.moveTweenCallback)
        elif orientation == Charset.ORIENTATION_UP:
            self.setPosition(self.getPosX(), self.getPosY()-stepsCount)
            self.__movingOffsetY.value = stepsCount
            self.__moveTween = Tween(interpreter, self.__movingOffsetY, 0, MapScene.CAMERA_MOVEMENT_DURATION*stepsCount,
                                            Easing.easingLinear, self.moveTweenCallback)
        elif orientation == Charset.ORIENTATION_DOWN:
            self.setPosition(self.getPosX(), self.getPosY() + stepsCount)
            self.__movingOffsetY.value = -stepsCount
            self.__moveTween = Tween(interpreter, self.__movingOffsetY, 0, MapScene.CAMERA_MOVEMENT_DURATION*stepsCount,
                                            Easing.easingLinear, self.moveTweenCallback)

        self.__moving = True




