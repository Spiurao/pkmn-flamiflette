from engine.tween.InternalTween import InternalTween


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


    def pushTween(self, tweenEntry):
        tween = InternalTween(True, tweenEntry.getDuration(), 0, tweenEntry.getSubject().getValue(), tweenEntry.getTargetValue(), tweenEntry.getSubject(), tweenEntry.getTag(), tweenEntry.getEasing())

        # ignore born-dead tweens
        if tween.duration == 0 or tween.initialValue == tween.targetValue:
            return False

        self.__tweenList.append(tween)

        return True

    def onTweenFinished(self, tag):
        pass

    def updateTweens(self, dt):
        toRemove = []
        for tween in self.__tweenList:
            if not tween.alive:
                continue

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
                toRemove.append(tween)

        for tween in toRemove:
            self.__tweenList.remove(tween)