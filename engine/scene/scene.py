from engine.tween.tween import Tween


class Scene:

    def __init__(self, engine):
        self.__engine = engine
        self.__tweenList = []
        self.__timersList = []

    def pushTimer(self, timer):
        self.__timersList.append(timer)

    def load(self):
        pass

    def unload(self):
        pass

    def draw(self):
        pass

    def update(self, dt, events):
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

    def shouldDrawUnderlyingScenes(self):
        return True


    def pushTween(self, tag, subject, targetValue, duration, easing):
        tween = Tween.create(tag, subject, targetValue, duration, easing)

        # ignore born-dead tweens
        if tween.duration == 0 or tween.initialValue == tween.targetValue:
            return False

        self.__tweenList.append(tween)

        return True

    def updateTimers(self, dt):
        for timer in self.__timersList:
            timer.update(dt)

        self.__timersList = [t for t in self.__timersList if t.alive]

    def updateTweens(self, dt):
        for tween in self.__tweenList:
            tween.update(tween, dt)

        self.__tweenList = [t for t in self.__tweenList if t.alive]