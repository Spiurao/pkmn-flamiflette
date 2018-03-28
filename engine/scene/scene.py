from engine.tween.Tween import Tween


class Scene:

    def __init__(self, engine):
        self.__engine = engine
        self.__tweenList = []

    def load(self):
        pass

    def unload(self):
        pass

    def draw(self):
        pass

    def update(self, dt, events):
        self.updateTweens(dt)

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


    def pushTween(self, parameters):
        tween = self.createTween(parameters)

        # ignore born-dead tweens
        if tween.duration == 0 or tween.initialValue == tween.targetValue:
            return False

        self.__tweenList.append(tween)

        return True

    def onTweenFinished(self, tag):
        pass

    def updateTween(self, tween, dt):
        if not tween or not tween.alive:
            return

        tween.runningSince += dt

        tween.subject.setValue(
            tween.easing(
                tween.runningSince,
                tween.initialValue,
                tween.targetValue - tween.initialValue,
                tween.duration
            )
        )

        if tween.runningSince >= tween.duration:
            tween.subject.setValue(
                tween.targetValue
            )
            tween.alive = False
            self.onTweenFinished(tween.tag)

    def createTween(self, parameters):
        return Tween(True, parameters.getDuration(), 0, parameters.getSubject().getValue(), parameters.getTargetValue(), parameters.getSubject(), parameters.getTag(), parameters.getEasing())

    def updateTweens(self, dt):
        toRemove = []
        for tween in self.__tweenList:
            self.updateTween(tween, dt)
            if not tween.alive:
                toRemove.append(tween)

        for tween in toRemove:
            self.__tweenList.remove(tween)