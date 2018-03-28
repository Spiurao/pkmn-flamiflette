import pygame

from engine.scene.scene import Scene
from engine.tween.Easing import Easing
from engine.tween.TweenEntry import TweenEntry
from engine.tween.TweenSubject import TweenSubject


class TweenScene(Scene):

    def update(self, dt, events):
        super().update(dt, events)
        for e in events:
            if e.type == pygame.KEYDOWN:
                tweenEntry = TweenEntry("test", self.__posX, 500, 1000, Easing.easingOutSine)
                self.pushTween(tweenEntry)

    def load(self):
        self.__posX = TweenSubject(0)
        pass

    def draw(self):
        pygame.draw.rect(self.getEngine().getWindow(), (255, 255, 255), (self.__posX.getValue(), 0, 100, 100))