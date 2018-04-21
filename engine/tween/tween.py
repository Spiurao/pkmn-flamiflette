from typing import Any, Callable

from engine.tween.tweensubject import TweenSubject


class Tween:
    def __init__(self, tag : Any, subject : TweenSubject, targetValue : float, duration : int, easing : Callable, cb : Callable):
        self.alive = True
        self.duration = duration
        self.runningSince = 0
        self.initialValue = None if subject is None else subject.value
        self.targetValue = targetValue
        self.subject = subject
        self.tag = tag
        self.easing = easing
        self.cb = cb

    def reverse(self):
        self.alive = True
        self.runningSince = 0
        oldInitialValue = self.initialValue
        self.initialValue = self.targetValue
        self.targetValue = oldInitialValue

    def update(self, dt : int):
        if not self.alive:
            return

        self.runningSince += dt

        if self.subject is not None:
            self.subject.value = (
                self.easing(
                    self.runningSince,
                    self.initialValue,
                    self.targetValue - self.initialValue,
                    self.duration
                )
            )

        if self.runningSince >= self.duration:
            if self.subject is not None:
                self.subject.value = (
                    self.targetValue
                )
            self.alive = False

            if self.cb is not None:
                self.cb(self.tag)
