from typing import List, Callable

import pygame

from engine.timer import Timer
from engine.tween.tween import Tween
from engine.tween.tweensubject import TweenSubject


class Scene:

    def __init__(self, engine):
        self.__engine = engine
        self.__tweenList = []
        self.__timersList = []

    def pushTimer(self, timer : Timer):
        self.__timersList.append(timer)

    def load(self):
        pass

    def unload(self):
        pass

    def draw(self):
        pass

    def update(self, dt : int, events : List[pygame.event.Event]):
        self.updateTweens(dt)
        self.updateTimers(dt)

    def getEngine(self):
        return self.__engine

    def transitionOut(self):
        return False

    def onPause(self):
        pass

    def onResume(self):
        pass

    def shouldDrawUnderlyingScenes(self) -> bool:
        return True

    def pushTween(self, tag : str, subject : TweenSubject, targetValue : float, duration : int, easing : Callable):
        tween = Tween(tag, subject, targetValue, duration, easing)

        # ignore born-dead tweens
        if tween.duration == 0 or tween.initialValue == tween.targetValue:
            return False

        self.__tweenList.append(tween)

        return True

    def updateTimers(self, dt : int):
        for timer in self.__timersList:
            timer.update(dt)

        self.__timersList = [t for t in self.__timersList if t.alive]

    def updateTweens(self, dt : int):
        for tween in self.__tweenList:
            tween.update(tween, dt)

        self.__tweenList = [t for t in self.__tweenList if t.alive]