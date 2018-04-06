from engine.graphics.charset import Charset
from engine.scene.map.events.event import Event
from engine.scene.map.mapscene import MapScene
from engine.tween.easing import Easing
from engine.tween.tween import Tween
from engine.tween.tweensubject import TweenSubject


class NPCEvent(Event):
    def __init__(self, scene, x, y, parameters):
        super().__init__(scene, x, y, parameters)

        self.__charset = Charset.ofTexture(parameters["charset"], parameters["orientation"])

        self.__charsetSurfaceOffset = None
        self.__tileSize = self.getScene().getTileSize()

        self.__moveTween = None
        self.__moving = False

        self.__movingOffsetX = TweenSubject(0)
        self.__movingOffsetY = TweenSubject(0)

    def update(self, dt, events):
        super().update(dt, events)
        if self.__moveTween is not None:
            self.__moveTween.update(dt)

    def load(self):
        super().load()
        self.__charset.load()

        self.__charsetSurfaceOffset = (self.__charset.getSurfaceWidth()/4, self.__charset.getSurfaceHeight()/2)

    def draw(self, offsetX, offsetY):
        super().draw(offsetX, offsetY)

        # No need to check if the charset will be offscreen since pygame does it for us
        self.getWindow().blit(self.__charset.getCurrentSurface(), (self.getPosX() * self.__tileSize - self.__charsetSurfaceOffset[0] + offsetX + self.__movingOffsetX.value * self.__tileSize, self.getPosY() * self.__tileSize - self.__charsetSurfaceOffset[1] + offsetY + self.__movingOffsetY.value * self.__tileSize))

    def isPassThrough(self):
        return False

    def moveTweenCallback(self, tag):
        self.__moving = False

    def setOrientation(self, orientation):
        self.__charset.setOrientation(orientation)

    def walk(self, orientation):
        if self.__moving:
            return

        self.__charset.setOrientation(orientation)

        # TODO Walk animation
        # TODO Collision checks
        if orientation == Charset.ORIENTATION_LEFT:
            self.setPosition(self.getPosX()-1, self.getPosY())
            self.__movingOffsetX.value = 1
            self.__moveTween = Tween.create(None, self.__movingOffsetX, 0, MapScene.CAMERA_MOVEMENT_DURATION, Easing.easingLinear, self.moveTweenCallback)
        elif orientation == Charset.ORIENTATION_RIGHT:
            self.setPosition(self.getPosX() + 1, self.getPosY())
            self.__movingOffsetX.value = -1
            self.__moveTween = Tween.create(None, self.__movingOffsetX, 0, MapScene.CAMERA_MOVEMENT_DURATION,
                                            Easing.easingLinear, self.moveTweenCallback)
        elif orientation == Charset.ORIENTATION_UP:
            self.setPosition(self.getPosX(), self.getPosY()-1)
            self.__movingOffsetY.value = 1
            self.__moveTween = Tween.create(None, self.__movingOffsetY, 0, MapScene.CAMERA_MOVEMENT_DURATION,
                                            Easing.easingLinear, self.moveTweenCallback)
        elif orientation == Charset.ORIENTATION_DOWN:
            self.setPosition(self.getPosX(), self.getPosY() + 1)
            self.__movingOffsetY.value = -1
            self.__moveTween = Tween.create(None, self.__movingOffsetY, 0, MapScene.CAMERA_MOVEMENT_DURATION,
                                            Easing.easingLinear, self.moveTweenCallback)
        # TODO Do other orientations

        self.__moving = True

        while self.__moving:
            pass




